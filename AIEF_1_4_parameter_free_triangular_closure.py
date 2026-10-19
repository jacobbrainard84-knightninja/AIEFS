#!/usr/bin/env python3
"""Parameter-free triangular closure test for the late AIEF K3 reduction.

The proposed asymptotic reduction is

    a[n+1] = lambda[n] a[n] + g[n],
    g[n+1] = alpha_EMA g[n],

where

    a[n]      = v^T b[n],
    g[n]      = v^T f[n],
    lambda[n] = v^T K[n] v,
    v         = (1,-1,-1)/sqrt(3),
    alpha_EMA = exp(-dt/T_window).

No coefficients are fitted.  The script checks one-step residuals and free
rollouts from several late start times.  It also compares the geometric axis
with a data-derived late POD axis, quantifies the measured transverse
correction, and reports the implied time-varying spectral gap

    kappa[n] = -log(|lambda[n]/alpha_EMA|)/dt.

This analysis remains conditional on the saved base replay.  The measured
lambda[n] sequence is an input from the validated frozen-weight cocycle, not a
new fitted model parameter.
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
DEFAULT_OUTPUT_DIR = "aief_1_4_parameter_free_triangular_closure"
DEFAULT_DT = 0.01
DEFAULT_POD_START = 250.0
DEFAULT_LATE_START = 200.0
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
    if not values or any(item < 0.0 for item in values):
        raise argparse.ArgumentTypeError("values must be nonnegative")
    return sorted(set(values))


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def geometric_direction() -> np.ndarray:
    return np.array([1.0, -1.0, -1.0]) / math.sqrt(3.0)


def relative_sequence_error(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(
        np.linalg.norm(actual - predicted)
        / max(np.linalg.norm(actual), ZERO_TOL)
    )


def fit_log_rate(
    times: np.ndarray,
    values: np.ndarray,
    tolerance: float,
) -> dict[str, float]:
    magnitudes = np.abs(np.asarray(values, dtype=float))
    valid = np.isfinite(magnitudes) & (magnitudes > tolerance)
    if np.sum(valid) < 3:
        return {"rate": np.nan, "R_squared": np.nan, "count": int(np.sum(valid))}
    x = np.asarray(times, dtype=float)[valid]
    y = np.log(magnitudes[valid])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "rate": float(-slope),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
        "count": int(len(x)),
    }


def make_report(
    one_step_summary: pd.DataFrame,
    rollout_summary: pd.DataFrame,
    gap_summary: pd.DataFrame,
    *,
    alpha_ema: float,
    ema_rate: float,
    pod_direction: np.ndarray,
    geom_direction: np.ndarray,
) -> str:
    angle = math.degrees(
        math.acos(
            np.clip(abs(float(pod_direction @ geom_direction)), -1.0, 1.0)
        )
    )
    lines = [
        "AIEF parameter-free triangular closure analysis",
        "===============================================",
        "",
        f"alpha_EMA: {alpha_ema:.12g}",
        f"EMA rate: {ema_rate:.9g}",
        f"POD/geometric unsigned angle: {angle:.9g} degrees",
        "",
        "One-step closure",
        "----------------",
    ]
    for _, row in one_step_summary.iterrows():
        lines.append(
            f"  axis={row['axis']}, direction={int(row['direction_id'])}: "
            f"median_a_residual={row['median_a_relative_residual']:.6g}, "
            f"max_a_residual={row['maximum_a_relative_residual']:.6g}, "
            f"median_g_residual={row['median_g_relative_residual']:.6g}, "
            f"max_g_residual={row['maximum_g_relative_residual']:.6g}, "
            f"median_transverse={row['median_transverse_fraction']:.6g}"
        )

    lines.extend(["", "Free rollouts", "-------------"])
    for _, row in rollout_summary.iterrows():
        lines.append(
            f"  axis={row['axis']}, direction={int(row['direction_id'])}, "
            f"start={row['start_time']:.6g}: "
            f"a_RMSE={row['a_trajectory_relative_RMSE']:.6g}, "
            f"g_RMSE={row['g_trajectory_relative_RMSE']:.6g}, "
            f"final_a_error={row['final_a_relative_error']:.6g}, "
            f"final_g_error={row['final_g_relative_error']:.6g}, "
            f"predicted_a_rate={row['predicted_a_rate']:.6g}, "
            f"actual_a_rate={row['actual_a_rate']:.6g}"
        )

    lines.extend(["", "Implied spectral gap", "--------------------"])
    for _, row in gap_summary.iterrows():
        lines.append(
            f"  axis={row['axis']}, target={row['target_time']:.6g}: "
            f"median_kappa_model={row['median_model_kappa']:.6g}, "
            f"observed_kappa={row['observed_kappa']:.6g}, "
            f"closure_error={row['closure_error']:.6g}, "
            f"kappa_variation={row['model_kappa_std']:.6g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* The model has no fitted coefficients but uses the measured base lambda[n] sequence.",
            "* The g equation tests whether projected forcing is asymptotically pure EMA decay.",
            "* Geometric and POD axes are tested separately; only the geometric axis is analytic a priori.",
            "* Rollout failure can arise from transverse correction even when one-step scalar closure is accurate.",
            "* Results remain conditional on this replay and tested tangent directions.",
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
    parser.add_argument("--pod-start", type=float, default=DEFAULT_POD_START)
    parser.add_argument("--late-start", type=float, default=DEFAULT_LATE_START)
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
    for path in (args.duhamel_npz, args.memory_fits, args.manifest):
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
    memory_fits = pd.read_csv(args.memory_fits)
    count, state_steps, dimension = total.shape
    future_steps = state_steps - 1
    if dimension != 3 or matrices.shape != (future_steps, 3, 3):
        raise ValueError("unexpected Duhamel shapes")

    pod_start_step = min(
        future_steps, int(round(args.pod_start / args.dt))
    )
    late_vectors = feedback[:, pod_start_step:, :].reshape(-1, 3)
    norms = np.linalg.norm(late_vectors, axis=1)
    late_vectors = late_vectors[norms > args.scalar_tol]
    left, _, _ = np.linalg.svd(late_vectors.T, full_matrices=False)
    pod_direction = left[:, 0]
    geom_direction = geometric_direction()
    if np.dot(pod_direction, geom_direction) < 0.0:
        pod_direction *= -1.0
    axes = {"POD": pod_direction, "geometric": geom_direction}

    late_step = int(round(args.late_start / args.dt))
    one_step_rows: list[dict[str, Any]] = []
    one_step_trajectory_rows: list[dict[str, Any]] = []
    rollout_rows: list[dict[str, Any]] = []
    rollout_summary_rows: list[dict[str, Any]] = []
    gap_rows: list[dict[str, Any]] = []
    array_payload: dict[str, np.ndarray] = {}

    for axis_name, axis in axes.items():
        a = total @ axis
        g = forcing @ axis
        lambdas = np.einsum("i,nij,j->n", axis, matrices, axis)
        Kaxis = np.einsum("nij,j->ni", matrices, axis)
        invariance_defect = np.linalg.norm(
            Kaxis - lambdas[:, None] * axis[None, :], axis=1
        ) / np.maximum(np.linalg.norm(Kaxis, axis=1), ZERO_TOL)
        model_kappa = -np.log(
            np.maximum(np.abs(lambdas / alpha_ema), ZERO_TOL)
        ) / args.dt

        array_payload[f"{axis_name}_a_total"] = a
        array_payload[f"{axis_name}_g_forcing"] = g
        array_payload[f"{axis_name}_lambda"] = lambdas
        array_payload[f"{axis_name}_model_kappa"] = model_kappa
        array_payload[f"{axis_name}_invariance_defect"] = invariance_defect

        for direction_id in range(count):
            a_residual = np.empty(future_steps)
            g_residual = np.empty(future_steps - 1)
            a_relative = np.empty(future_steps)
            g_relative = np.empty(future_steps - 1)
            transverse_fraction = np.empty(future_steps)
            for step in range(future_steps):
                transverse = (
                    total[direction_id, step]
                    - a[direction_id, step] * axis
                )
                predicted_a = (
                    lambdas[step] * a[direction_id, step]
                    + g[direction_id, step]
                )
                a_residual[step] = a[direction_id, step + 1] - predicted_a
                a_relative[step] = abs(a_residual[step]) / max(
                    abs(a[direction_id, step + 1]),
                    abs(predicted_a),
                    args.scalar_tol,
                )
                transverse_fraction[step] = np.linalg.norm(transverse) / max(
                    np.linalg.norm(total[direction_id, step]),
                    args.scalar_tol,
                )
                if step < future_steps - 1:
                    predicted_g = alpha_ema * g[direction_id, step]
                    g_residual[step] = (
                        g[direction_id, step + 1] - predicted_g
                    )
                    g_relative[step] = abs(g_residual[step]) / max(
                        abs(g[direction_id, step + 1]),
                        abs(predicted_g),
                        args.scalar_tol,
                    )
                if step % args.sample_stride == 0 or step == future_steps - 1:
                    one_step_trajectory_rows.append(
                        {
                            "axis": axis_name,
                            "direction_id": direction_id,
                            "step": step,
                            "time": step * args.dt,
                            "a_actual_next": a[direction_id, step + 1],
                            "a_predicted_next": predicted_a,
                            "a_relative_residual": a_relative[step],
                            "g_actual": g[direction_id, step],
                            "g_predicted_next": alpha_ema
                            * g[direction_id, step],
                            "g_relative_residual": g_relative[step]
                            if step < future_steps - 1
                            else np.nan,
                            "lambda": lambdas[step],
                            "model_kappa": model_kappa[step],
                            "invariance_defect": invariance_defect[step],
                            "transverse_fraction": transverse_fraction[step],
                        }
                    )

            late_a = a_relative[late_step:]
            late_g = g_relative[late_step : future_steps - 1]
            late_transverse = transverse_fraction[late_step:]
            one_step_rows.append(
                {
                    "axis": axis_name,
                    "direction_id": direction_id,
                    "late_start": args.late_start,
                    "median_a_relative_residual": float(np.median(late_a)),
                    "maximum_a_relative_residual": float(np.max(late_a)),
                    "median_g_relative_residual": float(np.median(late_g)),
                    "maximum_g_relative_residual": float(np.max(late_g)),
                    "median_transverse_fraction": float(
                        np.median(late_transverse)
                    ),
                    "maximum_transverse_fraction": float(
                        np.max(late_transverse)
                    ),
                    "median_invariance_defect": float(
                        np.median(invariance_defect[late_step:])
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
                        actual_g = float(g[direction_id, step + 1])
                        actual_g_values.append(actual_g)
                        predicted_g_values.append(g_hat)
                    if (
                        (step + 1 - start) % args.sample_stride == 0
                        or step + 1 == future_steps
                    ):
                        rollout_rows.append(
                            {
                                "axis": axis_name,
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
                times = (
                    np.arange(start + 1, future_steps + 1) * args.dt
                )
                actual_fit = fit_log_rate(
                    times, actual_a_array, args.scalar_tol
                )
                predicted_fit = fit_log_rate(
                    times, predicted_a_array, args.scalar_tol
                )
                rollout_summary_rows.append(
                    {
                        "axis": axis_name,
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

        for target_time in sorted(memory_fits["target_time"].unique()):
            target_step = min(
                future_steps, int(round(float(target_time) / args.dt))
            )
            start = max(late_step, target_step - int(round(66.6 / args.dt)))
            if target_step <= start:
                continue
            candidates = memory_fits.loc[
                memory_fits["target_time"] == target_time
            ]
            observed = float(candidates["kappa"].median())
            gap_rows.append(
                {
                    "axis": axis_name,
                    "target_time": float(target_time),
                    "fit_start_time": start * args.dt,
                    "median_model_kappa": float(
                        np.median(model_kappa[start:target_step])
                    ),
                    "model_kappa_std": float(
                        np.std(model_kappa[start:target_step], ddof=1)
                    ),
                    "observed_kappa": observed,
                    "closure_error": observed
                    - float(np.median(model_kappa[start:target_step])),
                }
            )

    one_step_summary = pd.DataFrame(one_step_rows)
    one_step_trajectory = pd.DataFrame(one_step_trajectory_rows)
    rollout_trajectory = pd.DataFrame(rollout_rows)
    rollout_summary = pd.DataFrame(rollout_summary_rows)
    gap_summary = pd.DataFrame(gap_rows)

    component_audit.atomic_write_csv(
        output_dir / "triangular_one_step_trajectory.csv", one_step_trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "triangular_one_step_summary.csv", one_step_summary
    )
    component_audit.atomic_write_csv(
        output_dir / "triangular_rollout_trajectory.csv", rollout_trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "triangular_rollout_summary.csv", rollout_summary
    )
    component_audit.atomic_write_csv(
        output_dir / "triangular_gap_summary.csv", gap_summary
    )
    component_audit.atomic_savez(
        output_dir / "triangular_closure_arrays.npz",
        {
            "POD_direction": pod_direction,
            "geometric_direction": geom_direction,
            "alpha_EMA": np.asarray([alpha_ema]),
            **array_payload,
        },
    )

    report = make_report(
        one_step_summary,
        rollout_summary,
        gap_summary,
        alpha_ema=alpha_ema,
        ema_rate=ema_rate,
        pod_direction=pod_direction,
        geom_direction=geom_direction,
    )
    component_audit.atomic_write_text(
        output_dir / "parameter_free_triangular_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 parameter-free triangular closure",
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
        "pod_start": args.pod_start,
        "late_start": args.late_start,
        "rollout_starts": args.rollout_starts,
        "sample_stride": args.sample_stride,
        "scalar_tolerance": args.scalar_tol,
        "alpha_EMA": alpha_ema,
        "ema_rate": ema_rate,
        "outputs": [
            "triangular_one_step_trajectory.csv",
            "triangular_one_step_summary.csv",
            "triangular_rollout_trajectory.csv",
            "triangular_rollout_summary.csv",
            "triangular_gap_summary.csv",
            "triangular_closure_arrays.npz",
            "parameter_free_triangular_report.txt",
        ],
        "interpretation_constraints": [
            "No coefficients are fitted; lambda[n] is measured from the validated base cocycle and alpha_EMA is fixed by the model.",
            "POD and geometric axes are tested separately.",
            "The triangular model is intended only for the late regime.",
            "A successful rollout on this replay does not establish universality across seeds or branches.",
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
