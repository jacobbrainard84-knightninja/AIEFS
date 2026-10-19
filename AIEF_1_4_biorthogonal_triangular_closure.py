#!/usr/bin/env python3
"""Biorthogonal triangular closure for the non-normal exceptional AIEF K3.

The geometric late right direction is fixed analytically as

    v = (1,-1,-1)/sqrt(3).

For a non-normal weight cocycle, the modal amplitude need not be v^T b.  This
script tests fixed late left covectors u, normalized by u^T v=1, and a
backward-transported adjoint covector bundle satisfying

    K_n^T u_{n+1} = lambda_n u_n,
    u_n^T v = 1.

For fixed covectors it uses

    a_n = u^T b_n,
    g_n = u^T f_n,
    lambda_n = u^T K_n v.

For the adjoint bundle it uses

    a_n = u_n^T b_n,
    g_n = u_{n+1}^T f_n.

It then evaluates the parameter-free triangular closure

    a[n+1] = lambda[n] a[n] + g[n],
    g[n+1] = alpha_EMA g[n],

with no fitted coefficients.  POD and Euclidean geometric coordinates are
retained as controls.  The purpose is to decide whether direction-0 rollout
failure is a Euclidean-coordinate artifact or requires an additional mode.
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
DEFAULT_MANIFEST = "runs/5a9f093a2fe0/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_biorthogonal_triangular_closure"
DEFAULT_DT = 0.01
DEFAULT_POD_START = 250.0
DEFAULT_LATE_START = 200.0
DEFAULT_LEFT_REFERENCE_TIMES = "200,250,319.99"
DEFAULT_AVERAGE_START = 250.0
DEFAULT_ROLLOUT_STARTS = "150,200,250"
DEFAULT_SAMPLE_STRIDE = 10
DEFAULT_SCALAR_TOL = 1e-30
ZERO_TOL = 1e-300


def file_sha256(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_nonnegative_float_list(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated floats") from exc
    if not values or any(value < 0.0 for value in values):
        raise argparse.ArgumentTypeError("values must be nonnegative")
    return sorted(set(values))


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def geometric_direction() -> np.ndarray:
    return np.array([1.0, -1.0, -1.0]) / math.sqrt(3.0)


def left_mode(matrix: np.ndarray, right: np.ndarray) -> dict[str, Any]:
    rayleigh = float(right @ matrix @ right)
    eigenvalues, eigenvectors = np.linalg.eig(matrix.T)
    index = int(np.argmin(np.abs(eigenvalues - rayleigh)))
    eigenvalue = eigenvalues[index]
    vector = eigenvectors[:, index]
    if np.max(np.abs(np.imag(vector))) > 1e-9:
        raise RuntimeError("selected left mode is materially complex")
    vector = np.real(vector)
    pairing = float(vector @ right)
    if abs(pairing) <= 1e-14:
        raise RuntimeError("left/right pairing is numerically zero")
    vector /= pairing
    residual = float(
        np.linalg.norm(matrix.T @ vector - np.real(eigenvalue) * vector)
        / max(np.linalg.norm(matrix.T @ vector), ZERO_TOL)
    )
    return {
        "u": vector,
        "eigenvalue": float(np.real(eigenvalue)),
        "rayleigh": rayleigh,
        "left_residual": residual,
        "condition": float(np.linalg.norm(vector) * np.linalg.norm(right)),
    }


def backward_adjoint_bundle(
    matrices: np.ndarray,
    right: np.ndarray,
    terminal_covector: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    steps = len(matrices)
    covectors = np.empty((steps + 1, len(right)), dtype=float)
    lambdas = np.empty(steps, dtype=float)
    residuals = np.empty(steps, dtype=float)
    terminal = terminal_covector / float(terminal_covector @ right)
    covectors[-1] = terminal
    for step in range(steps - 1, -1, -1):
        transported = matrices[step].T @ covectors[step + 1]
        lam = float(right @ transported)
        if abs(lam) <= np.finfo(float).tiny:
            raise RuntimeError(f"adjoint transport pairing vanished at step {step}")
        covectors[step] = transported / lam
        lambdas[step] = lam
        residuals[step] = float(
            np.linalg.norm(
                matrices[step].T @ covectors[step + 1]
                - lam * covectors[step]
            )
            / max(
                np.linalg.norm(matrices[step].T @ covectors[step + 1]),
                ZERO_TOL,
            )
        )
    return covectors, lambdas, residuals


def relative_sequence_error(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(
        np.linalg.norm(actual - predicted)
        / max(np.linalg.norm(actual), ZERO_TOL)
    )


def fit_log_rate(times: np.ndarray, values: np.ndarray, tolerance: float) -> dict[str, float]:
    magnitudes = np.abs(np.asarray(values, dtype=float))
    valid = np.isfinite(magnitudes) & (magnitudes > tolerance)
    if np.sum(valid) < 3:
        return {"rate": np.nan, "R_squared": np.nan}
    x = np.asarray(times, dtype=float)[valid]
    y = np.log(magnitudes[valid])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "rate": float(-slope),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
    }


def make_report(
    coordinate_frame: pd.DataFrame,
    one_step_summary: pd.DataFrame,
    rollout_summary: pd.DataFrame,
    *,
    alpha_ema: float,
    ema_rate: float,
) -> str:
    lines = [
        "AIEF biorthogonal triangular closure analysis",
        "==============================================",
        "",
        f"alpha_EMA: {alpha_ema:.12g}",
        f"EMA rate: {ema_rate:.9g}",
        "",
        "Coordinate conditioning",
        "-----------------------",
    ]
    for _, row in coordinate_frame.iterrows():
        lines.append(
            f"  coordinate={row['coordinate']}: condition={row['condition']:.6g}, "
            f"left_residual={row['left_residual']:.6g}, "
            f"u_norm={row['u_norm']:.6g}, "
            f"pairing={row['u_dot_v']:.12g}"
        )

    lines.extend(["", "One-step closure", "----------------"])
    for _, row in one_step_summary.iterrows():
        lines.append(
            f"  coordinate={row['coordinate']}, direction={int(row['direction_id'])}: "
            f"median_a_residual={row['median_a_relative_residual']:.6g}, "
            f"max_a_residual={row['maximum_a_relative_residual']:.6g}, "
            f"median_g_residual={row['median_g_relative_residual']:.6g}, "
            f"max_g_residual={row['maximum_g_relative_residual']:.6g}"
        )

    lines.extend(["", "Free rollouts", "-------------"])
    for _, row in rollout_summary.iterrows():
        lines.append(
            f"  coordinate={row['coordinate']}, direction={int(row['direction_id'])}, "
            f"start={row['start_time']:.6g}: a_RMSE={row['a_trajectory_relative_RMSE']:.6g}, "
            f"g_RMSE={row['g_trajectory_relative_RMSE']:.6g}, "
            f"final_a_error={row['final_a_relative_error']:.6g}, "
            f"final_g_error={row['final_g_relative_error']:.6g}, "
            f"actual_rate={row['actual_a_rate']:.6g}, predicted_rate={row['predicted_a_rate']:.6g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Fixed left covectors are late reference modes, not exact covariant bundles over the full transient.",
            "* The backward adjoint coordinate makes the a-recurrence exact by construction; its nontrivial test is the EMA law for projected forcing and free rollout.",
            "* Large left/right condition indicates sensitivity even if scalar closure improves.",
            "* A successful result remains conditional on this replay and tested directions.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duhamel-npz", default=DEFAULT_DUHAMEL_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dt", type=float, default=DEFAULT_DT)
    parser.add_argument("--pod-start", type=float, default=DEFAULT_POD_START)
    parser.add_argument("--late-start", type=float, default=DEFAULT_LATE_START)
    parser.add_argument(
        "--left-reference-times",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_LEFT_REFERENCE_TIMES),
    )
    parser.add_argument("--average-start", type=float, default=DEFAULT_AVERAGE_START)
    parser.add_argument(
        "--rollout-starts",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_ROLLOUT_STARTS),
    )
    parser.add_argument("--sample-stride", type=int, default=DEFAULT_SAMPLE_STRIDE)
    parser.add_argument("--scalar-tol", type=float, default=DEFAULT_SCALAR_TOL)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.duhamel_npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.dt, args.scalar_tol) <= 0.0 or args.sample_stride <= 0:
        raise ValueError("dt/scalar-tol and sample-stride must be positive")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    t_window = float(manifest["model"]["T_window"])
    alpha_ema = math.exp(-args.dt / t_window)
    ema_rate = 1.0 / t_window

    with np.load(args.duhamel_npz, allow_pickle=False) as data:
        total = np.asarray(data["total_weight_tangent"], dtype=float).copy()
        feedback = np.asarray(data["feedback_weight_tangent"], dtype=float).copy()
        forcing = np.asarray(data["instant_forcing"], dtype=float).copy()
        matrices = np.asarray(data["K3_matrix_sequence"], dtype=float).copy()
    count, state_steps, dimension = total.shape
    future_steps = state_steps - 1
    if dimension != 3 or matrices.shape != (future_steps, 3, 3):
        raise ValueError("unexpected Duhamel array shapes")

    v = geometric_direction()
    pod_start = min(future_steps, int(round(args.pod_start / args.dt)))
    late_vectors = feedback[:, pod_start:, :].reshape(-1, 3)
    late_norms = np.linalg.norm(late_vectors, axis=1)
    late_vectors = late_vectors[late_norms > args.scalar_tol]
    left_pod, _, _ = np.linalg.svd(late_vectors.T, full_matrices=False)
    v_pod = left_pod[:, 0]
    if np.dot(v_pod, v) < 0.0:
        v_pod *= -1.0

    coordinate_specs: dict[str, dict[str, Any]] = {
        "POD_Euclidean": {
            "right": v_pod,
            "covectors": np.broadcast_to(v_pod, (state_steps, 3)).copy(),
            "type": "fixed",
            "left_residual": np.nan,
            "condition": 1.0,
        },
        "geometric_Euclidean": {
            "right": v,
            "covectors": np.broadcast_to(v, (state_steps, 3)).copy(),
            "type": "fixed",
            "left_residual": np.nan,
            "condition": 1.0,
        },
    }

    for reference_time in args.left_reference_times:
        step = min(future_steps - 1, int(round(reference_time / args.dt)))
        mode = left_mode(matrices[step], v)
        label = f"left_t{reference_time:g}".replace(".", "p")
        coordinate_specs[label] = {
            "right": v,
            "covectors": np.broadcast_to(mode["u"], (state_steps, 3)).copy(),
            "type": "fixed",
            "left_residual": mode["left_residual"],
            "condition": mode["condition"],
            "eigenvalue": mode["eigenvalue"],
        }

    average_start = min(
        future_steps - 1, int(round(args.average_start / args.dt))
    )
    average_matrix = np.mean(matrices[average_start:], axis=0)
    average_mode = left_mode(average_matrix, v)
    coordinate_specs["left_late_average"] = {
        "right": v,
        "covectors": np.broadcast_to(
            average_mode["u"], (state_steps, 3)
        ).copy(),
        "type": "fixed",
        "left_residual": average_mode["left_residual"],
        "condition": average_mode["condition"],
        "eigenvalue": average_mode["eigenvalue"],
    }

    terminal_mode = left_mode(matrices[-1], v)
    adjoint_covectors, adjoint_lambdas, adjoint_residuals = (
        backward_adjoint_bundle(matrices, v, terminal_mode["u"])
    )
    coordinate_specs["adjoint_bundle"] = {
        "right": v,
        "covectors": adjoint_covectors,
        "type": "adjoint",
        "left_residual": float(np.max(adjoint_residuals)),
        "condition": float(
            np.max(np.linalg.norm(adjoint_covectors, axis=1))
        ),
        "adjoint_lambdas": adjoint_lambdas,
    }

    coordinate_rows: list[dict[str, Any]] = []
    one_step_rows: list[dict[str, Any]] = []
    one_step_trajectory_rows: list[dict[str, Any]] = []
    rollout_rows: list[dict[str, Any]] = []
    rollout_summary_rows: list[dict[str, Any]] = []
    covector_rows: list[dict[str, Any]] = []
    payload: dict[str, np.ndarray] = {
        "geometric_right_direction": v,
        "POD_direction": v_pod,
        "alpha_EMA": np.asarray([alpha_ema]),
    }
    late_step = int(round(args.late_start / args.dt))

    for label, spec in coordinate_specs.items():
        right = np.asarray(spec["right"], dtype=float)
        covectors = np.asarray(spec["covectors"], dtype=float)
        coordinate_type = str(spec["type"])
        pairings = covectors @ right
        if np.max(np.abs(pairings - 1.0)) > 1e-8:
            raise RuntimeError(f"coordinate {label} lost biorthogonal normalization")

        a = np.einsum("ni,dni->dn", covectors, total)
        if coordinate_type == "adjoint":
            lambdas = np.asarray(spec["adjoint_lambdas"], dtype=float)
            g = np.einsum("ni,dni->dn", covectors[1:], forcing)
        else:
            lambdas = np.einsum(
                "ni,nij,j->n", covectors[:-1], matrices, right
            )
            g = np.einsum("ni,dni->dn", covectors[:-1], forcing)

        payload[f"{label}_covectors"] = covectors
        payload[f"{label}_a"] = a
        payload[f"{label}_g"] = g
        payload[f"{label}_lambda"] = lambdas

        # Fixed-coordinate left residual is evaluated over the late sequence;
        # the adjoint bundle has its exact transport residual by construction.
        if coordinate_type == "adjoint":
            left_residual_late = float(spec["left_residual"])
        else:
            residual_values = []
            for step in range(late_step, future_steps):
                u = covectors[step]
                lam = lambdas[step]
                residual_values.append(
                    np.linalg.norm(matrices[step].T @ u - lam * u)
                    / max(np.linalg.norm(matrices[step].T @ u), ZERO_TOL)
                )
            left_residual_late = float(np.median(residual_values))

        coordinate_rows.append(
            {
                "coordinate": label,
                "type": coordinate_type,
                "right_json": json_compact(right.tolist()),
                "u_start_json": json_compact(covectors[late_step].tolist()),
                "u_end_json": json_compact(covectors[-1].tolist()),
                "u_norm": float(np.median(np.linalg.norm(covectors[late_step:], axis=1))),
                "u_norm_max": float(np.max(np.linalg.norm(covectors[late_step:], axis=1))),
                "u_dot_v": float(np.median(pairings[late_step:])),
                "condition": float(spec["condition"]),
                "left_residual": left_residual_late,
                "covector_total_variation": float(
                    np.sum(
                        np.linalg.norm(
                            np.diff(covectors[late_step:], axis=0), axis=1
                        )
                    )
                ),
            }
        )

        for step in range(0, state_steps, args.sample_stride):
            covector_rows.append(
                {
                    "coordinate": label,
                    "step": step,
                    "time": step * args.dt,
                    "u_0": covectors[step, 0],
                    "u_1": covectors[step, 1],
                    "u_2": covectors[step, 2],
                    "u_norm": float(np.linalg.norm(covectors[step])),
                    "u_dot_v": float(covectors[step] @ right),
                    "lambda": lambdas[step]
                    if step < future_steps
                    else np.nan,
                }
            )

        for direction_id in range(count):
            a_residual = np.empty(future_steps)
            g_residual = np.empty(future_steps - 1)
            a_relative = np.empty(future_steps)
            g_relative = np.empty(future_steps - 1)
            for step in range(future_steps):
                prediction_a = lambdas[step] * a[direction_id, step] + g[
                    direction_id, step
                ]
                a_residual[step] = a[direction_id, step + 1] - prediction_a
                a_relative[step] = abs(a_residual[step]) / max(
                    abs(a[direction_id, step + 1]),
                    abs(prediction_a),
                    args.scalar_tol,
                )
                if step < future_steps - 1:
                    prediction_g = alpha_ema * g[direction_id, step]
                    g_residual[step] = g[direction_id, step + 1] - prediction_g
                    g_relative[step] = abs(g_residual[step]) / max(
                        abs(g[direction_id, step + 1]),
                        abs(prediction_g),
                        args.scalar_tol,
                    )
                if step % args.sample_stride == 0 or step == future_steps - 1:
                    one_step_trajectory_rows.append(
                        {
                            "coordinate": label,
                            "direction_id": direction_id,
                            "step": step,
                            "time": step * args.dt,
                            "a_actual_next": a[direction_id, step + 1],
                            "a_predicted_next": prediction_a,
                            "a_relative_residual": a_relative[step],
                            "g_actual": g[direction_id, step],
                            "g_predicted_next": alpha_ema
                            * g[direction_id, step],
                            "g_relative_residual": g_relative[step]
                            if step < future_steps - 1
                            else np.nan,
                            "lambda": lambdas[step],
                        }
                    )

            one_step_rows.append(
                {
                    "coordinate": label,
                    "direction_id": direction_id,
                    "late_start": args.late_start,
                    "median_a_relative_residual": float(
                        np.median(a_relative[late_step:])
                    ),
                    "maximum_a_relative_residual": float(
                        np.max(a_relative[late_step:])
                    ),
                    "median_g_relative_residual": float(
                        np.median(g_relative[late_step:])
                    ),
                    "maximum_g_relative_residual": float(
                        np.max(g_relative[late_step:])
                    ),
                }
            )

            for start_time in args.rollout_starts:
                start = int(round(start_time / args.dt))
                if start >= future_steps:
                    continue
                a_hat = float(a[direction_id, start])
                g_hat = float(g[direction_id, start])
                actual_a_values = []
                predicted_a_values = []
                actual_g_values = []
                predicted_g_values = []
                for step in range(start, future_steps):
                    a_hat = lambdas[step] * a_hat + g_hat
                    g_hat = alpha_ema * g_hat
                    actual_a = float(a[direction_id, step + 1])
                    actual_a_values.append(actual_a)
                    predicted_a_values.append(a_hat)
                    if step + 1 < future_steps:
                        actual_g_values.append(float(g[direction_id, step + 1]))
                        predicted_g_values.append(g_hat)
                    if (
                        (step + 1 - start) % args.sample_stride == 0
                        or step + 1 == future_steps
                    ):
                        rollout_rows.append(
                            {
                                "coordinate": label,
                                "direction_id": direction_id,
                                "start_time": start_time,
                                "step": step + 1,
                                "time": (step + 1) * args.dt,
                                "actual_a": actual_a,
                                "predicted_a": a_hat,
                                "a_relative_error": abs(actual_a - a_hat)
                                / max(abs(actual_a), args.scalar_tol),
                                "actual_g": actual_g_values[-1]
                                if actual_g_values
                                else np.nan,
                                "predicted_g": predicted_g_values[-1]
                                if predicted_g_values
                                else np.nan,
                                "g_relative_error": abs(
                                    actual_g_values[-1] - predicted_g_values[-1]
                                )
                                / max(
                                    abs(actual_g_values[-1]), args.scalar_tol
                                )
                                if actual_g_values
                                else np.nan,
                            }
                        )
                actual_a_array = np.asarray(actual_a_values)
                predicted_a_array = np.asarray(predicted_a_values)
                actual_g_array = np.asarray(actual_g_values)
                predicted_g_array = np.asarray(predicted_g_values)
                times = np.arange(start + 1, future_steps + 1) * args.dt
                actual_fit = fit_log_rate(
                    times, actual_a_array, args.scalar_tol
                )
                predicted_fit = fit_log_rate(
                    times, predicted_a_array, args.scalar_tol
                )
                rollout_summary_rows.append(
                    {
                        "coordinate": label,
                        "direction_id": direction_id,
                        "start_time": start_time,
                        "end_time": future_steps * args.dt,
                        "a_trajectory_relative_RMSE": relative_sequence_error(
                            actual_a_array, predicted_a_array
                        ),
                        "g_trajectory_relative_RMSE": relative_sequence_error(
                            actual_g_array, predicted_g_array
                        )
                        if len(actual_g_array)
                        else np.nan,
                        "final_a_relative_error": abs(
                            actual_a_array[-1] - predicted_a_array[-1]
                        )
                        / max(abs(actual_a_array[-1]), args.scalar_tol),
                        "final_g_relative_error": abs(
                            actual_g_array[-1] - predicted_g_array[-1]
                        )
                        / max(abs(actual_g_array[-1]), args.scalar_tol)
                        if len(actual_g_array)
                        else np.nan,
                        "actual_a_rate": actual_fit["rate"],
                        "actual_a_R_squared": actual_fit["R_squared"],
                        "predicted_a_rate": predicted_fit["rate"],
                        "predicted_a_R_squared": predicted_fit["R_squared"],
                    }
                )

    coordinate_frame = pd.DataFrame(coordinate_rows)
    one_step_summary = pd.DataFrame(one_step_rows)
    one_step_trajectory = pd.DataFrame(one_step_trajectory_rows)
    rollout_trajectory = pd.DataFrame(rollout_rows)
    rollout_summary = pd.DataFrame(rollout_summary_rows)
    covector_trajectory = pd.DataFrame(covector_rows)

    component_audit.atomic_write_csv(
        output_dir / "biorthogonal_coordinate_summary.csv", coordinate_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "biorthogonal_one_step_summary.csv", one_step_summary
    )
    component_audit.atomic_write_csv(
        output_dir / "biorthogonal_one_step_trajectory.csv", one_step_trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "biorthogonal_rollout_summary.csv", rollout_summary
    )
    component_audit.atomic_write_csv(
        output_dir / "biorthogonal_rollout_trajectory.csv", rollout_trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "biorthogonal_covector_trajectory.csv", covector_trajectory
    )
    component_audit.atomic_savez(
        output_dir / "biorthogonal_closure_arrays.npz", payload
    )

    report = make_report(
        coordinate_frame,
        one_step_summary,
        rollout_summary,
        alpha_ema=alpha_ema,
        ema_rate=ema_rate,
    )
    component_audit.atomic_write_text(
        output_dir / "biorthogonal_triangular_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 biorthogonal triangular closure",
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
            "manifest": {
                "path": str(Path(args.manifest).resolve()),
                "sha256": file_sha256(args.manifest),
            },
        },
        "dt": args.dt,
        "pod_start": args.pod_start,
        "late_start": args.late_start,
        "left_reference_times": args.left_reference_times,
        "average_start": args.average_start,
        "rollout_starts": args.rollout_starts,
        "sample_stride": args.sample_stride,
        "scalar_tolerance": args.scalar_tol,
        "alpha_EMA": alpha_ema,
        "ema_rate": ema_rate,
        "outputs": [
            "biorthogonal_coordinate_summary.csv",
            "biorthogonal_one_step_summary.csv",
            "biorthogonal_one_step_trajectory.csv",
            "biorthogonal_rollout_summary.csv",
            "biorthogonal_rollout_trajectory.csv",
            "biorthogonal_covector_trajectory.csv",
            "biorthogonal_closure_arrays.npz",
            "biorthogonal_triangular_report.txt",
        ],
        "interpretation_constraints": [
            "Fixed left covectors are reference modes of selected late matrices.",
            "The adjoint-bundle a recurrence is exact by construction; g EMA closure and rollout are the nontrivial tests.",
            "Large biorthogonal condition indicates sensitivity to perturbation/noise.",
            "No coefficients are fitted; alpha_EMA is fixed and lambda sequences are measured from the base cocycle.",
            "Results remain conditional on this replay and tested directions.",
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
