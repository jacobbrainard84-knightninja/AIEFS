#!/usr/bin/env python3
"""Direct scalar and two-state tests of the AIEF spectral-gap hypothesis.

This no-replay analysis uses the exact saved Duhamel arrays.  It measures a
fixed late POD direction v and projects

    a_n      = v^T b_n,
    g_n      = v^T f_n,
    lambda_n = v^T K_n v.

It then audits the exact projected recurrence

    a_{n+1} = lambda_n a_n + g_n + epsilon_n,
    epsilon_n = v^T K_n (b_n - a_n v),

and the line-invariance defect

    ||(I-vv^T) K_n v||.

For multiple target times it estimates the projected weight contraction and
projected forcing-envelope decay over a common lookback window, then compares

    kappa_observed  versus  r_B - r_g.

Finally it fits a closed constant two-state late recurrence

    [a_{n+1}, g_{n+1}]^T = M [a_n, g_n]^T

on a training interval and evaluates one-step and free-rollout predictions on
a disjoint validation interval.  This directly tests the proposed mechanism
without changing T_window or replaying the model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import AIEF_1_4_component_controller_audit as component_audit


DEFAULT_DUHAMEL_NPZ = "aief_1_4_augmented_duhamel_feedback/duhamel_vectors.npz"
DEFAULT_MEMORY_FITS = "aief_1_4_feedback_rank_memory_reduction/target_time_memory_fits.csv"
DEFAULT_MANIFEST = "runs/5a9f093a2fe0/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_scalar_spectral_gap_reduction"
DEFAULT_DT = 0.01
DEFAULT_LATE_DIRECTION_START = 250.0
DEFAULT_TARGET_TIMES = "150,200,250,320"
DEFAULT_RATE_FIT_WINDOW = 66.6
DEFAULT_TRAIN_WINDOW = "200,260"
DEFAULT_VALIDATION_WINDOW = "260,320"
DEFAULT_SCALAR_TOL = 1e-30
ZERO_TOL = 1e-300


def file_sha256(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_float_pair(value: str) -> tuple[float, float]:
    try:
        parts = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected start,end") from exc
    if len(parts) != 2 or parts[0] < 0.0 or parts[1] <= parts[0]:
        raise argparse.ArgumentTypeError("expected 0 <= start < end")
    return float(parts[0]), float(parts[1])


def parse_positive_float_list(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated floats") from exc
    if not values or any(item <= 0.0 for item in values):
        raise argparse.ArgumentTypeError("values must be positive")
    return sorted(set(values))


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def fit_log_envelope(
    times: np.ndarray,
    values: np.ndarray,
    scalar_tolerance: float,
) -> dict[str, float]:
    magnitudes = np.abs(np.asarray(values, dtype=float))
    valid = (
        np.isfinite(times)
        & np.isfinite(magnitudes)
        & (magnitudes > scalar_tolerance)
    )
    if np.sum(valid) < 3:
        return {
            "count": int(np.sum(valid)),
            "rate": np.nan,
            "intercept": np.nan,
            "R_squared": np.nan,
            "rmse_log": np.nan,
            "sign_change_count": np.nan,
        }
    x = np.asarray(times, dtype=float)[valid]
    raw = np.asarray(values, dtype=float)[valid]
    y = np.log(np.abs(raw))
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    signs = np.sign(raw)
    sign_changes = int(np.sum(signs[1:] != signs[:-1]))
    return {
        "count": int(len(x)),
        "rate": float(-slope),
        "intercept": float(intercept),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
        "rmse_log": float(np.sqrt(np.mean((y - prediction) ** 2))),
        "sign_change_count": sign_changes,
    }


def r_squared(actual: np.ndarray, predicted: np.ndarray) -> float:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    residual = float(np.sum((actual - predicted) ** 2))
    total = float(np.sum((actual - np.mean(actual)) ** 2))
    return float(1.0 - residual / total) if total > 0.0 else np.nan


def fit_linear_map(
    state: np.ndarray,
    start_step: int,
    end_step: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Fit x[n+1] = M x[n] with column scaling and no intercept."""
    X = state[start_step:end_step].T
    Y = state[start_step + 1 : end_step + 1].T
    x_scale = np.maximum(np.max(np.abs(X), axis=1), np.finfo(float).tiny)
    y_scale = np.maximum(np.max(np.abs(Y), axis=1), np.finfo(float).tiny)
    Xs = X / x_scale[:, None]
    Ys = Y / y_scale[:, None]
    scaled_map = Ys @ np.linalg.pinv(Xs, rcond=1e-12)
    matrix = y_scale[:, None] * scaled_map / x_scale[None, :]
    prediction = matrix @ X
    diagnostics = {
        "training_R2_a": r_squared(Y[0], prediction[0]),
        "training_R2_g": r_squared(Y[1], prediction[1]),
        "training_relative_RMSE": float(
            np.linalg.norm(Y - prediction) / max(np.linalg.norm(Y), ZERO_TOL)
        ),
        "design_condition_number": float(np.linalg.cond(Xs)),
    }
    return matrix, diagnostics


def validate_linear_map(
    matrix: np.ndarray,
    state: np.ndarray,
    start_step: int,
    end_step: int,
) -> tuple[dict[str, Any], pd.DataFrame]:
    X = state[start_step:end_step]
    Y = state[start_step + 1 : end_step + 1]
    one_step = (matrix @ X.T).T
    one_step_diagnostics = {
        "validation_R2_a": r_squared(Y[:, 0], one_step[:, 0]),
        "validation_R2_g": r_squared(Y[:, 1], one_step[:, 1]),
        "validation_relative_RMSE": float(
            np.linalg.norm(Y - one_step) / max(np.linalg.norm(Y), ZERO_TOL)
        ),
    }
    rollout = np.empty_like(Y)
    current = state[start_step].copy()
    rows: list[dict[str, Any]] = []
    for local_index, step in enumerate(range(start_step, end_step)):
        current = matrix @ current
        rollout[local_index] = current
        actual = state[step + 1]
        rows.append(
            {
                "step": step + 1,
                "actual_a": actual[0],
                "predicted_a": current[0],
                "actual_g": actual[1],
                "predicted_g": current[1],
                "absolute_error": float(np.linalg.norm(actual - current)),
                "relative_error": float(
                    np.linalg.norm(actual - current)
                    / max(np.linalg.norm(actual), ZERO_TOL)
                ),
            }
        )
    one_step_diagnostics.update(
        {
            "rollout_relative_RMSE": float(
                np.linalg.norm(Y - rollout) / max(np.linalg.norm(Y), ZERO_TOL)
            ),
            "rollout_final_relative_error": float(
                np.linalg.norm(Y[-1] - rollout[-1])
                / max(np.linalg.norm(Y[-1]), ZERO_TOL)
            ),
        }
    )
    return one_step_diagnostics, pd.DataFrame(rows)


def make_report(
    scalar_summary: pd.DataFrame,
    gap_frame: pd.DataFrame,
    model_frame: pd.DataFrame,
    *,
    ema_rate: float,
    late_direction: np.ndarray,
) -> str:
    lines = [
        "AIEF scalar spectral-gap reduction analysis",
        "===========================================",
        "",
        f"Late POD direction: {late_direction.tolist()}",
        f"EMA rate 1/T_window: {ema_rate:.9g}",
        "",
        "Late scalar recurrence diagnostics",
        "----------------------------------",
    ]
    for _, row in scalar_summary.iterrows():
        lines.append(
            f"  direction={int(row['direction_id'])}: "
            f"median_invariance_defect={row['median_invariance_defect']:.6g}, "
            f"max_invariance_defect={row['maximum_invariance_defect']:.6g}, "
            f"median_scalar_residual={row['median_scalar_recurrence_relative_residual']:.6g}, "
            f"max_scalar_residual={row['maximum_scalar_recurrence_relative_residual']:.6g}, "
            f"median_weight_rate={row['median_projected_weight_rate']:.6g}, "
            f"total_rate={row['total_amplitude_rate']:.6g}, "
            f"forcing_rate={row['forcing_amplitude_rate']:.6g}"
        )

    lines.extend(["", "Target-wise spectral-gap tests", "-------------------------------"])
    for _, row in gap_frame.iterrows():
        lines.append(
            f"  direction={int(row['direction_id'])}, target={row['target_time']:.6g}: "
            f"observed_kappa={row['observed_kappa']:.6g}, "
            f"rB={row['projected_weight_rate']:.6g}, rg={row['forcing_envelope_rate']:.6g}, "
            f"predicted_gap={row['predicted_gap']:.6g}, "
            f"closure_error={row['gap_closure_error']:.6g}, "
            f"forcing_R2={row['forcing_fit_R_squared']:.6g}"
        )

    lines.extend(["", "Closed two-state recurrence", "---------------------------"])
    for _, row in model_frame.iterrows():
        lines.append(
            f"  model={row['model']}: matrix={row['matrix_json']}, "
            f"train_RMSE={row['training_relative_RMSE']:.6g}, "
            f"validation_RMSE={row['validation_relative_RMSE']:.6g}, "
            f"rollout_RMSE={row['rollout_relative_RMSE']:.6g}, "
            f"final_rollout_error={row['rollout_final_relative_error']:.6g}, "
            f"eigen_rates={row['eigenvalue_rates_json']}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* The scalar recurrence is an exact projection plus a measured transverse residual; small residual is required for closure.",
            "* Spectral-gap estimates use related quantities from one trajectory and are deterministic mechanism checks, not independent statistical replications.",
            "* Exponential forcing fits use absolute scalar amplitudes and report sign changes separately.",
            "* The two-state model is fitted without an intercept and evaluated on a disjoint late validation interval.",
            "* A good two-state fit on two directions does not establish universality beyond this replay and tangent subspace.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duhamel-npz", default=DEFAULT_DUHAMEL_NPZ)
    parser.add_argument("--memory-fits", default=DEFAULT_MEMORY_FITS)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dt", type=float, default=DEFAULT_DT)
    parser.add_argument("--late-direction-start", type=float, default=DEFAULT_LATE_DIRECTION_START)
    parser.add_argument(
        "--target-times",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_TARGET_TIMES),
    )
    parser.add_argument("--rate-fit-window", type=float, default=DEFAULT_RATE_FIT_WINDOW)
    parser.add_argument(
        "--train-window", type=parse_float_pair, default=parse_float_pair(DEFAULT_TRAIN_WINDOW)
    )
    parser.add_argument(
        "--validation-window",
        type=parse_float_pair,
        default=parse_float_pair(DEFAULT_VALIDATION_WINDOW),
    )
    parser.add_argument("--scalar-tol", type=float, default=DEFAULT_SCALAR_TOL)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.duhamel_npz, args.memory_fits, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.dt, args.rate_fit_window, args.scalar_tol) <= 0.0:
        raise ValueError("dt, rate-fit-window, and scalar-tol must be positive")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    ema_rate = 1.0 / float(manifest["model"]["T_window"])

    with np.load(args.duhamel_npz, allow_pickle=False) as data:
        total = np.asarray(data["total_weight_tangent"], dtype=float).copy()
        homogeneous = np.asarray(data["homogeneous_weight_tangent"], dtype=float).copy()
        feedback = np.asarray(data["feedback_weight_tangent"], dtype=float).copy()
        forcing = np.asarray(data["instant_forcing"], dtype=float).copy()
        matrices = np.asarray(data["K3_matrix_sequence"], dtype=float).copy()
    count, state_steps, dimension = total.shape
    future_steps = state_steps - 1
    if dimension != 3 or matrices.shape != (future_steps, 3, 3):
        raise ValueError("unexpected Duhamel shapes")

    start_direction_step = max(
        0, min(future_steps, int(round(args.late_direction_start / args.dt)))
    )
    late_vectors = feedback[:, start_direction_step:, :].reshape(-1, 3)
    norms = np.linalg.norm(late_vectors, axis=1)
    late_vectors = late_vectors[norms > args.scalar_tol]
    if not len(late_vectors):
        raise RuntimeError("no late feedback vectors above scalar tolerance")
    left, _, _ = np.linalg.svd(late_vectors.T, full_matrices=False)
    v = left[:, 0]
    if np.dot(v, feedback[min(1, count - 1), -1]) < 0.0:
        v *= -1.0
    projector = np.outer(v, v)
    transverse_projector = np.eye(3) - projector

    a = total @ v
    a_h = homogeneous @ v
    a_r = feedback @ v
    g = forcing @ v
    lambdas = np.einsum("i,nij,j->n", v, matrices, v)
    Kv = np.einsum("nij,j->ni", matrices, v)
    invariance_defect = np.linalg.norm(
        Kv - lambdas[:, None] * v[None, :], axis=1
    )
    invariance_relative = invariance_defect / np.maximum(
        np.linalg.norm(Kv, axis=1), ZERO_TOL
    )
    projected_weight_rates = -np.log(np.maximum(np.abs(lambdas), ZERO_TOL)) / args.dt

    scalar_rows: list[dict[str, Any]] = []
    for direction_id in range(count):
        for step in range(future_steps):
            e = total[direction_id, step] - a[direction_id, step] * v
            epsilon = float(v @ matrices[step] @ e)
            recurrence_residual = float(
                a[direction_id, step + 1]
                - lambdas[step] * a[direction_id, step]
                - g[direction_id, step]
            )
            scalar_rows.append(
                {
                    "direction_id": direction_id,
                    "step": step,
                    "time": step * args.dt,
                    "a_total": a[direction_id, step],
                    "a_homogeneous": a_h[direction_id, step],
                    "a_feedback": a_r[direction_id, step],
                    "g_forcing": g[direction_id, step],
                    "lambda_projected": lambdas[step],
                    "projected_weight_rate": projected_weight_rates[step],
                    "invariance_defect": invariance_defect[step],
                    "invariance_relative": invariance_relative[step],
                    "transverse_norm": float(np.linalg.norm(e)),
                    "transverse_fraction": float(
                        np.linalg.norm(e)
                        / max(np.linalg.norm(total[direction_id, step]), ZERO_TOL)
                    ),
                    "epsilon_transverse_correction": epsilon,
                    "scalar_recurrence_residual": recurrence_residual,
                    "residual_minus_epsilon": recurrence_residual - epsilon,
                    "scalar_recurrence_relative_residual": abs(
                        recurrence_residual
                    )
                    / max(
                        abs(a[direction_id, step + 1]),
                        abs(lambdas[step] * a[direction_id, step])
                        + abs(g[direction_id, step]),
                        args.scalar_tol,
                    ),
                }
            )
    scalar_trajectory = pd.DataFrame(scalar_rows)

    late_step = start_direction_step
    late_time = np.arange(state_steps) * args.dt
    scalar_summary_rows: list[dict[str, Any]] = []
    for direction_id in range(count):
        late_scalar = scalar_trajectory.loc[
            (scalar_trajectory["direction_id"] == direction_id)
            & (scalar_trajectory["step"] >= late_step)
        ]
        total_fit = fit_log_envelope(
            late_time[late_step:], a[direction_id, late_step:], args.scalar_tol
        )
        feedback_fit = fit_log_envelope(
            late_time[late_step:], a_r[direction_id, late_step:], args.scalar_tol
        )
        forcing_fit = fit_log_envelope(
            np.arange(future_steps)[late_step:] * args.dt,
            g[direction_id, late_step:],
            args.scalar_tol,
        )
        scalar_summary_rows.append(
            {
                "direction_id": direction_id,
                "late_start_time": args.late_direction_start,
                "median_invariance_defect": float(
                    np.median(invariance_relative[late_step:])
                ),
                "maximum_invariance_defect": float(
                    np.max(invariance_relative[late_step:])
                ),
                "median_scalar_recurrence_relative_residual": float(
                    late_scalar["scalar_recurrence_relative_residual"].median()
                ),
                "maximum_scalar_recurrence_relative_residual": float(
                    late_scalar["scalar_recurrence_relative_residual"].max()
                ),
                "maximum_residual_minus_epsilon": float(
                    late_scalar["residual_minus_epsilon"].abs().max()
                ),
                "median_projected_weight_rate": float(
                    np.median(projected_weight_rates[late_step:])
                ),
                "total_amplitude_rate": total_fit["rate"],
                "total_fit_R_squared": total_fit["R_squared"],
                "feedback_amplitude_rate": feedback_fit["rate"],
                "feedback_fit_R_squared": feedback_fit["R_squared"],
                "forcing_amplitude_rate": forcing_fit["rate"],
                "forcing_fit_R_squared": forcing_fit["R_squared"],
                "forcing_sign_change_count": forcing_fit["sign_change_count"],
                "weight_minus_forcing_rate": float(
                    np.median(projected_weight_rates[late_step:])
                    - forcing_fit["rate"]
                ),
                "forcing_rate_minus_ema": forcing_fit["rate"] - ema_rate,
            }
        )
    scalar_summary = pd.DataFrame(scalar_summary_rows)

    memory_fits = pd.read_csv(args.memory_fits)
    gap_rows: list[dict[str, Any]] = []
    for direction_id in range(count):
        for target_time in args.target_times:
            target_step = min(
                future_steps, int(round(target_time / args.dt))
            )
            start_step = max(
                0,
                int(round((target_time - args.rate_fit_window) / args.dt)),
            )
            time_forcing = np.arange(start_step, target_step) * args.dt
            forcing_fit = fit_log_envelope(
                time_forcing,
                g[direction_id, start_step:target_step],
                args.scalar_tol,
            )
            if target_step > start_step:
                weight_rate = float(
                    -np.sum(
                        np.log(
                            np.maximum(
                                np.abs(lambdas[start_step:target_step]),
                                ZERO_TOL,
                            )
                        )
                    )
                    / ((target_step - start_step) * args.dt)
                )
            else:
                weight_rate = np.nan
            candidates = memory_fits.loc[
                memory_fits["direction_id"] == direction_id
            ]
            if len(candidates):
                nearest = candidates.iloc[
                    int(
                        np.argmin(
                            np.abs(
                                candidates["target_time"].to_numpy(float)
                                - target_time
                            )
                        )
                    )
                ]
                observed_kappa = float(nearest["kappa"])
                observed_target = float(nearest["target_time"])
            else:
                observed_kappa = observed_target = np.nan
            predicted_gap = weight_rate - forcing_fit["rate"]
            gap_rows.append(
                {
                    "direction_id": direction_id,
                    "target_time": target_time,
                    "observed_target_time": observed_target,
                    "fit_start_time": start_step * args.dt,
                    "fit_end_time": target_step * args.dt,
                    "observed_kappa": observed_kappa,
                    "projected_weight_rate": weight_rate,
                    "forcing_envelope_rate": forcing_fit["rate"],
                    "forcing_fit_R_squared": forcing_fit["R_squared"],
                    "forcing_sign_change_count": forcing_fit[
                        "sign_change_count"
                    ],
                    "predicted_gap": predicted_gap,
                    "gap_closure_error": observed_kappa - predicted_gap,
                    "gap_relative_error": (observed_kappa - predicted_gap)
                    / max(abs(observed_kappa), args.scalar_tol),
                    "forcing_rate_minus_ema": forcing_fit["rate"] - ema_rate,
                }
            )
    gap_frame = pd.DataFrame(gap_rows)

    train_start = int(round(args.train_window[0] / args.dt))
    train_end = int(round(args.train_window[1] / args.dt))
    validation_start = int(round(args.validation_window[0] / args.dt))
    validation_end = min(
        future_steps - 1,
        int(round(args.validation_window[1] / args.dt)),
    )
    if not (
        0 <= train_start < train_end <= validation_start < validation_end < future_steps
    ):
        raise ValueError("training/validation windows are invalid or overlapping")

    model_rows: list[dict[str, Any]] = []
    rollout_frames: list[pd.DataFrame] = []
    states: dict[str, np.ndarray] = {}
    for direction_id in range(count):
        states[f"direction_{direction_id}"] = np.column_stack(
            [a[direction_id, :future_steps], g[direction_id]]
        )
    states["pooled"] = np.concatenate(
        [states[f"direction_{direction_id}"] for direction_id in range(count)],
        axis=0,
    )

    for label, state_values in states.items():
        if label == "pooled":
            # Fit pooled one-step pairs from both directions over the same
            # physical training interval.
            X_parts = []
            Y_parts = []
            for direction_id in range(count):
                values = states[f"direction_{direction_id}"]
                X_parts.append(values[train_start:train_end])
                Y_parts.append(values[train_start + 1 : train_end + 1])
            X = np.concatenate(X_parts).T
            Y = np.concatenate(Y_parts).T
            x_scale = np.maximum(np.max(np.abs(X), axis=1), np.finfo(float).tiny)
            y_scale = np.maximum(np.max(np.abs(Y), axis=1), np.finfo(float).tiny)
            scaled_map = (Y / y_scale[:, None]) @ np.linalg.pinv(
                X / x_scale[:, None], rcond=1e-12
            )
            matrix = y_scale[:, None] * scaled_map / x_scale[None, :]
            prediction = matrix @ X
            training_diag = {
                "training_R2_a": r_squared(Y[0], prediction[0]),
                "training_R2_g": r_squared(Y[1], prediction[1]),
                "training_relative_RMSE": float(
                    np.linalg.norm(Y - prediction) / max(np.linalg.norm(Y), ZERO_TOL)
                ),
                "design_condition_number": float(
                    np.linalg.cond(X / x_scale[:, None])
                ),
            }
            validation_metrics = []
            for direction_id in range(count):
                metrics, rollout = validate_linear_map(
                    matrix,
                    states[f"direction_{direction_id}"],
                    validation_start,
                    validation_end,
                )
                rollout["model"] = label
                rollout["direction_id"] = direction_id
                rollout_frames.append(rollout)
                validation_metrics.append(metrics)
            validation_diag = {
                key: float(np.mean([metrics[key] for metrics in validation_metrics]))
                for key in validation_metrics[0]
            }
        else:
            matrix, training_diag = fit_linear_map(
                state_values, train_start, train_end
            )
            validation_diag, rollout = validate_linear_map(
                matrix, state_values, validation_start, validation_end
            )
            rollout["model"] = label
            rollout["direction_id"] = int(label.split("_")[-1])
            rollout_frames.append(rollout)

        eigenvalues = np.linalg.eigvals(matrix)
        eigen_rates = [
            float(-math.log(max(abs(value), ZERO_TOL)) / args.dt)
            for value in eigenvalues
        ]
        model_rows.append(
            {
                "model": label,
                "matrix_json": json_compact(matrix.tolist()),
                "M_aa": matrix[0, 0],
                "M_ag": matrix[0, 1],
                "M_ga": matrix[1, 0],
                "M_gg": matrix[1, 1],
                **training_diag,
                **validation_diag,
                "eigenvalues_json": json_compact(
                    [[float(np.real(value)), float(np.imag(value))] for value in eigenvalues]
                ),
                "eigenvalue_rates_json": json_compact(eigen_rates),
            }
        )
    model_frame = pd.DataFrame(model_rows)
    rollout_frame = pd.concat(rollout_frames, ignore_index=True)

    component_audit.atomic_write_csv(
        output_dir / "scalar_projection_trajectory.csv", scalar_trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "scalar_projection_summary.csv", scalar_summary
    )
    component_audit.atomic_write_csv(
        output_dir / "target_spectral_gap_tests.csv", gap_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "two_state_model_summary.csv", model_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "two_state_rollout_validation.csv", rollout_frame
    )
    component_audit.atomic_savez(
        output_dir / "scalar_reduction_arrays.npz",
        {
            "late_direction": v,
            "a_total": a,
            "a_homogeneous": a_h,
            "a_feedback": a_r,
            "g_forcing": g,
            "lambda_projected": lambdas,
            "invariance_defect": invariance_defect,
            "projected_weight_rates": projected_weight_rates,
        },
    )

    report = make_report(
        scalar_summary,
        gap_frame,
        model_frame,
        ema_rate=ema_rate,
        late_direction=v,
    )
    component_audit.atomic_write_text(
        output_dir / "scalar_spectral_gap_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 scalar spectral-gap and two-state reduction",
        "source": {
            "path": str(Path(__file__).resolve()),
            "sha256": file_sha256(Path(__file__).resolve()),
        },
        "command": sys.argv,
        "inputs": {
            "duhamel_npz": {
                "path": str(Path(args.duhamel_npz).resolve()),
                "sha256": file_sha256(args.duhamel_npz),
            },
            "memory_fits": {
                "path": str(Path(args.memory_fits).resolve()),
                "sha256": file_sha256(args.memory_fits),
            },
            "manifest": {
                "path": str(Path(args.manifest).resolve()),
                "sha256": file_sha256(args.manifest),
            },
        },
        "dt": args.dt,
        "late_direction_start": args.late_direction_start,
        "late_direction": v.tolist(),
        "target_times": args.target_times,
        "rate_fit_window": args.rate_fit_window,
        "train_window": args.train_window,
        "validation_window": args.validation_window,
        "scalar_tolerance": args.scalar_tol,
        "ema_rate": ema_rate,
        "outputs": [
            "scalar_projection_trajectory.csv",
            "scalar_projection_summary.csv",
            "target_spectral_gap_tests.csv",
            "two_state_model_summary.csv",
            "two_state_rollout_validation.csv",
            "scalar_reduction_arrays.npz",
            "scalar_spectral_gap_report.txt",
        ],
        "interpretation_constraints": [
            "The fixed late POD direction is measured from this replay and tested subspace.",
            "Spectral-gap closure is a deterministic same-trajectory mechanism test, not independent statistical replication.",
            "Forcing envelopes are fit in absolute value and sign changes are reported.",
            "The two-state recurrence is trained and validated on disjoint late intervals.",
            "No T_window parameter is changed in this analysis.",
        ],
    }
    component_audit.atomic_write_text(
        output_dir / "analysis_manifest.json",
        json.dumps(manifest_output, indent=2, sort_keys=True) + "\n",
    )

    print(report)
    print(f"Saved analysis to {output_dir.resolve()}")


if __name__ == "__main__":
    main()
