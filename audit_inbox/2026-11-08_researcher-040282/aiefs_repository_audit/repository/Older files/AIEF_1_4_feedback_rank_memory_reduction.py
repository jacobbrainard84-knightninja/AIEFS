#!/usr/bin/env python3
"""Quantify rank-one reduction and target-time feedback memory in AIEF-1.4.

This no-replay analysis consumes the exact augmented Duhamel vectors and asks
whether two strongly suggested interpretations are directly supported:

1. Do total/feedback/forcing vectors occupy a nearly rank-one late channel?
2. Is recent-forcing reconstruction approximately exponential at multiple
   target times, rather than only at the final horizon?

For each target time and initial direction it reconstructs the feedback from
all past forcing contributions, computes recent-memory error curves, fits

    E_T(L) ~= C exp(-kappa_T L),

reports fit quality and threshold horizons, and performs an SVD of all forcing
contributions propagated to that target.  It also computes weighted and
unit-direction POD ranks on user-selected time intervals, instantaneous rank
of the two-direction feedback matrix, rotation of leading POD directions, and
a scalar projection onto the final late slow channel.

The script does not alter T_window.  A genuine EMA-parameter sensitivity study
requires a separately versioned, consistently regenerated base trajectory;
that should follow only after the existing-trajectory memory law is quantified.
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
DEFAULT_OUTPUT_DIR = "aief_1_4_feedback_rank_memory_reduction"
DEFAULT_DT = 0.01
DEFAULT_TARGET_TIMES = "10,50,72.86,100,150,200,250,320"
DEFAULT_INTERVALS = "0,10,50,100,150,200,250,320"
DEFAULT_THRESHOLDS = "0.5,0.1,0.01"
DEFAULT_CURVE_STRIDE = 10
DEFAULT_FIT_ERROR_MIN = 0.01
DEFAULT_FIT_ERROR_MAX = 0.8
DEFAULT_VECTOR_NORM_TOL = 1e-20


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


def parse_positive_float_list(value: str) -> list[float]:
    values = parse_nonnegative_float_list(value)
    if any(item <= 0.0 for item in values):
        raise argparse.ArgumentTypeError("values must be positive")
    return values


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def robust_cosine(left: np.ndarray, right: np.ndarray) -> float:
    left_norm = float(np.linalg.norm(left))
    right_norm = float(np.linalg.norm(right))
    if left_norm <= np.finfo(float).tiny or right_norm <= np.finfo(float).tiny:
        return np.nan
    return float(
        np.clip(
            float(left @ right / (left_norm * right_norm)),
            -1.0,
            1.0,
        )
    )


def pod_diagnostics(vectors: np.ndarray, norm_tolerance: float) -> dict[str, Any]:
    """Weighted and direction-normalized POD for vectors shaped (samples,3)."""
    vectors = np.asarray(vectors, dtype=float)
    norms = np.linalg.norm(vectors, axis=1)
    valid = np.isfinite(norms) & (norms > norm_tolerance)
    selected = vectors[valid]
    if not len(selected):
        return {
            "sample_count": 0,
            "weighted_singular_values": np.full(3, np.nan),
            "weighted_energy_fraction_1": np.nan,
            "weighted_energy_fraction_2": np.nan,
            "unit_singular_values": np.full(3, np.nan),
            "unit_energy_fraction_1": np.nan,
            "unit_energy_fraction_2": np.nan,
            "leading_weighted_direction": np.full(3, np.nan),
            "leading_unit_direction": np.full(3, np.nan),
        }
    matrix = selected.T
    left, singular, _ = np.linalg.svd(matrix, full_matrices=False)
    energy = singular**2
    total_energy = float(np.sum(energy))
    unit_matrix = (selected / np.linalg.norm(selected, axis=1)[:, None]).T
    unit_left, unit_singular, _ = np.linalg.svd(unit_matrix, full_matrices=False)
    unit_energy = unit_singular**2
    unit_total = float(np.sum(unit_energy))
    padded = np.zeros(3)
    padded[: len(singular)] = singular
    unit_padded = np.zeros(3)
    unit_padded[: len(unit_singular)] = unit_singular
    return {
        "sample_count": int(len(selected)),
        "weighted_singular_values": padded,
        "weighted_energy_fraction_1": float(energy[0] / total_energy),
        "weighted_energy_fraction_2": float(np.sum(energy[:2]) / total_energy),
        "unit_singular_values": unit_padded,
        "unit_energy_fraction_1": float(unit_energy[0] / unit_total),
        "unit_energy_fraction_2": float(np.sum(unit_energy[:2]) / unit_total),
        "leading_weighted_direction": left[:, 0],
        "leading_unit_direction": unit_left[:, 0],
    }


def fit_exponential_memory(
    horizons: np.ndarray,
    errors: np.ndarray,
    error_min: float,
    error_max: float,
) -> dict[str, float]:
    valid = (
        np.isfinite(horizons)
        & np.isfinite(errors)
        & (errors >= error_min)
        & (errors <= error_max)
        & (errors > 0.0)
    )
    if np.sum(valid) < 3:
        return {
            "fit_count": int(np.sum(valid)),
            "kappa": np.nan,
            "intercept": np.nan,
            "R_squared": np.nan,
            "rmse_log_error": np.nan,
        }
    x = horizons[valid]
    y = np.log(errors[valid])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "fit_count": int(np.sum(valid)),
        "kappa": float(-slope),
        "intercept": float(intercept),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
        "rmse_log_error": float(np.sqrt(np.mean((y - prediction) ** 2))),
    }


def target_contributions(
    matrices: np.ndarray,
    forcing: np.ndarray,
    target_step: int,
) -> np.ndarray:
    """Return U(target,m+1) f_m for m=0,...,target-1."""
    contributions = np.zeros((target_step, 3), dtype=float)
    suffix = np.eye(3)
    for step in range(target_step - 1, -1, -1):
        contributions[step] = suffix @ forcing[step]
        suffix = suffix @ matrices[step]
    return contributions


def make_report(
    memory_fits: pd.DataFrame,
    pod_frame: pd.DataFrame,
    contribution_rank: pd.DataFrame,
    *,
    ema_rate: float,
) -> str:
    lines = [
        "AIEF feedback rank and target-time memory reduction",
        "===================================================",
        "",
        f"Base EMA decay rate 1/T_window: {ema_rate:.6g}",
        "",
        "Target-time memory fits",
        "-----------------------",
    ]
    for _, row in memory_fits.iterrows():
        horizon_parts = []
        for column in memory_fits.columns:
            if column.startswith("horizon_error_"):
                threshold = column.removeprefix("horizon_error_")
                horizon_parts.append(
                    f"h(error<={threshold})={row[column]:.6g}"
                )
        lines.append(
            f"  direction={int(row['direction_id'])}, target={row['target_time']:.6g}: "
            f"kappa={row['kappa']:.6g}, tau={row['memory_time_constant']:.6g}, "
            f"R2={row['R_squared']:.6g}, monotonic_violations={int(row['monotonic_violation_count'])}, "
            + ", ".join(horizon_parts)
        )

    lines.extend(["", "POD rank by interval", "--------------------"])
    for _, row in pod_frame.iterrows():
        lines.append(
            f"  object={row['object']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}), "
            f"samples={int(row['sample_count'])}, weighted_E1={row['weighted_energy_fraction_1']:.6g}, "
            f"unit_E1={row['unit_energy_fraction_1']:.6g}, "
            f"angle_to_final={row['angle_to_final_leading_degrees']:.6g} deg"
        )

    lines.extend(["", "Propagated forcing rank", "-----------------------"])
    for _, row in contribution_rank.iterrows():
        lines.append(
            f"  direction={int(row['direction_id'])}, target={row['target_time']:.6g}: "
            f"weighted_E1={row['weighted_energy_fraction_1']:.6g}, "
            f"unit_E1={row['unit_energy_fraction_1']:.6g}, "
            f"leading_alignment_with_feedback={row['leading_alignment_with_target_feedback']:.6g}"
        )

    valid_kappa = memory_fits.loc[
        memory_fits["kappa"].notna() & (memory_fits["R_squared"] >= 0.95)
    ]
    if len(valid_kappa):
        lines.extend(
            [
                "",
                f"High-quality fit median kappa: {valid_kappa['kappa'].median():.6g}",
                f"High-quality fit kappa range: [{valid_kappa['kappa'].min():.6g}, {valid_kappa['kappa'].max():.6g}]",
                f"Median kappa minus EMA rate: {(valid_kappa['kappa'] - ema_rate).median():.6g}",
            ]
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Exponential fits describe operational recent-forcing reconstruction curves, not automatically an intrinsic memory kernel.",
            "* Weighted POD can be dominated by large early vectors; unit-vector POD measures directional collapse separately.",
            "* A high first POD fraction directly supports low rank but does not prove a universal invariant one-dimensional manifold.",
            "* Target-time robustness is required before identifying kappa with any model parameter.",
            "* This analysis uses one seed and two initial directions.",
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
    parser.add_argument(
        "--target-times",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_TARGET_TIMES),
    )
    parser.add_argument(
        "--intervals",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_INTERVALS),
    )
    parser.add_argument(
        "--thresholds",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_THRESHOLDS),
    )
    parser.add_argument("--curve-stride", type=int, default=DEFAULT_CURVE_STRIDE)
    parser.add_argument("--fit-error-min", type=float, default=DEFAULT_FIT_ERROR_MIN)
    parser.add_argument("--fit-error-max", type=float, default=DEFAULT_FIT_ERROR_MAX)
    parser.add_argument("--vector-norm-tol", type=float, default=DEFAULT_VECTOR_NORM_TOL)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.duhamel_npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if args.dt <= 0.0 or args.curve_stride <= 0 or args.vector_norm_tol <= 0.0:
        raise ValueError("dt, curve-stride, and vector-norm-tol must be positive")
    if not (0.0 < args.fit_error_min < args.fit_error_max < 1.0):
        raise ValueError("fit error bounds must satisfy 0 < min < max < 1")
    if len(args.intervals) < 2:
        raise ValueError("intervals requires at least two boundaries")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = manifest["model"]
    t_window = float(model["T_window"])
    ema_rate = 1.0 / t_window

    with np.load(args.duhamel_npz, allow_pickle=False) as data:
        total = np.asarray(data["total_weight_tangent"], dtype=float).copy()
        homogeneous = np.asarray(data["homogeneous_weight_tangent"], dtype=float).copy()
        feedback = np.asarray(data["feedback_weight_tangent"], dtype=float).copy()
        forcing = np.asarray(data["instant_forcing"], dtype=float).copy()
        matrices = np.asarray(data["K3_matrix_sequence"], dtype=float).copy()
    count, state_steps, dimension = total.shape
    future_steps = state_steps - 1
    if dimension != 3 or forcing.shape != (count, future_steps, 3):
        raise ValueError("unexpected Duhamel array shapes")

    target_steps = sorted(
        set(
            max(1, min(future_steps, int(round(time_value / args.dt))))
            for time_value in args.target_times
        )
    )
    memory_fit_rows: list[dict[str, Any]] = []
    memory_curve_rows: list[dict[str, Any]] = []
    contribution_rank_rows: list[dict[str, Any]] = []

    for direction_id in range(count):
        for target_step in target_steps:
            contributions = target_contributions(
                matrices,
                forcing[direction_id],
                target_step,
            )
            target_feedback = feedback[direction_id, target_step]
            target_norm = float(np.linalg.norm(target_feedback))
            recent = np.zeros(3)
            horizons: list[float] = []
            errors: list[float] = []
            threshold_horizons: dict[float, float] = {
                threshold: np.nan for threshold in args.thresholds
            }
            for step in range(target_step - 1, -1, -1):
                recent += contributions[step]
                horizon = (target_step - step) * args.dt
                error = float(
                    np.linalg.norm(recent - target_feedback)
                    / max(target_norm, 1e-300)
                )
                horizons.append(horizon)
                errors.append(error)
                for threshold in args.thresholds:
                    if np.isnan(threshold_horizons[threshold]) and error <= threshold:
                        threshold_horizons[threshold] = horizon
                if (
                    step % args.curve_stride == 0
                    or step == target_step - 1
                    or step == 0
                ):
                    memory_curve_rows.append(
                        {
                            "direction_id": direction_id,
                            "target_step": target_step,
                            "target_time": target_step * args.dt,
                            "start_step": step,
                            "start_time": step * args.dt,
                            "recent_horizon": horizon,
                            "relative_reconstruction_error": error,
                            "recent_norm": float(np.linalg.norm(recent)),
                            "alignment_with_target_feedback": robust_cosine(
                                recent, target_feedback
                            ),
                        }
                    )
            horizons_array = np.asarray(horizons)
            errors_array = np.asarray(errors)
            fit = fit_exponential_memory(
                horizons_array,
                errors_array,
                args.fit_error_min,
                args.fit_error_max,
            )
            monotonic_violations = int(
                np.sum(np.diff(errors_array) > 1e-12)
            )
            row = {
                "direction_id": direction_id,
                "target_step": target_step,
                "target_time": target_step * args.dt,
                "target_feedback_norm": target_norm,
                "monotonic_violation_count": monotonic_violations,
                **fit,
                "memory_time_constant": 1.0 / fit["kappa"]
                if np.isfinite(fit["kappa"]) and fit["kappa"] > 0.0
                else np.nan,
                "kappa_minus_ema_rate": fit["kappa"] - ema_rate
                if np.isfinite(fit["kappa"])
                else np.nan,
            }
            for threshold in args.thresholds:
                row[f"horizon_error_{threshold:g}"] = threshold_horizons[threshold]
            memory_fit_rows.append(row)

            pod = pod_diagnostics(contributions, args.vector_norm_tol)
            leading = pod["leading_weighted_direction"]
            contribution_rank_rows.append(
                {
                    "direction_id": direction_id,
                    "target_step": target_step,
                    "target_time": target_step * args.dt,
                    "contribution_count": pod["sample_count"],
                    "weighted_energy_fraction_1": pod[
                        "weighted_energy_fraction_1"
                    ],
                    "weighted_energy_fraction_2": pod[
                        "weighted_energy_fraction_2"
                    ],
                    "unit_energy_fraction_1": pod["unit_energy_fraction_1"],
                    "unit_energy_fraction_2": pod["unit_energy_fraction_2"],
                    "leading_alignment_with_target_feedback": abs(
                        robust_cosine(leading, target_feedback)
                    ),
                    "weighted_singular_values_json": json_compact(
                        pod["weighted_singular_values"].tolist()
                    ),
                    "unit_singular_values_json": json_compact(
                        pod["unit_singular_values"].tolist()
                    ),
                    "leading_direction_json": json_compact(leading.tolist()),
                }
            )

    memory_fits = pd.DataFrame(memory_fit_rows)
    memory_curves = pd.DataFrame(memory_curve_rows)
    contribution_rank = pd.DataFrame(contribution_rank_rows)

    # POD on trajectory objects over requested intervals, pooling directions.
    boundaries = np.asarray(args.intervals, dtype=float)
    if boundaries[0] > 0.0:
        boundaries = np.concatenate(([0.0], boundaries))
    final_time = future_steps * args.dt
    if boundaries[-1] < final_time:
        boundaries = np.concatenate((boundaries, [final_time]))

    objects = {
        "total_weight_tangent": total,
        "feedback_weight_tangent": feedback,
        "instant_forcing": forcing,
    }
    pod_rows: list[dict[str, Any]] = []
    pod_directions: dict[tuple[str, int], np.ndarray] = {}
    for object_name, values in objects.items():
        object_steps = values.shape[1]
        for interval_id in range(len(boundaries) - 1):
            start_step = max(0, int(round(boundaries[interval_id] / args.dt)))
            end_step = min(
                object_steps,
                int(round(boundaries[interval_id + 1] / args.dt)),
            )
            if end_step <= start_step:
                continue
            vectors = values[:, start_step:end_step, :].reshape(-1, 3)
            pod = pod_diagnostics(vectors, args.vector_norm_tol)
            pod_directions[(object_name, interval_id)] = pod[
                "leading_weighted_direction"
            ]
            pod_rows.append(
                {
                    "object": object_name,
                    "interval_id": interval_id,
                    "start_time": start_step * args.dt,
                    "end_time": end_step * args.dt,
                    "sample_count": pod["sample_count"],
                    "weighted_energy_fraction_1": pod[
                        "weighted_energy_fraction_1"
                    ],
                    "weighted_energy_fraction_2": pod[
                        "weighted_energy_fraction_2"
                    ],
                    "unit_energy_fraction_1": pod["unit_energy_fraction_1"],
                    "unit_energy_fraction_2": pod["unit_energy_fraction_2"],
                    "weighted_singular_values_json": json_compact(
                        pod["weighted_singular_values"].tolist()
                    ),
                    "unit_singular_values_json": json_compact(
                        pod["unit_singular_values"].tolist()
                    ),
                    "leading_weighted_direction_json": json_compact(
                        pod["leading_weighted_direction"].tolist()
                    ),
                    "leading_unit_direction_json": json_compact(
                        pod["leading_unit_direction"].tolist()
                    ),
                }
            )
    pod_frame = pd.DataFrame(pod_rows)

    # Compare each interval leading direction with the final interval for the
    # same object.  Sign is immaterial for a one-dimensional subspace.
    for object_name in objects:
        object_rows = pod_frame.loc[pod_frame["object"] == object_name]
        if not len(object_rows):
            continue
        final_interval = int(object_rows["interval_id"].max())
        final_direction = pod_directions[(object_name, final_interval)]
        for index in object_rows.index:
            interval_id = int(pod_frame.loc[index, "interval_id"])
            direction = pod_directions[(object_name, interval_id)]
            alignment = abs(robust_cosine(direction, final_direction))
            pod_frame.loc[index, "alignment_to_final_leading"] = alignment
            pod_frame.loc[index, "angle_to_final_leading_degrees"] = (
                math.degrees(math.acos(np.clip(alignment, -1.0, 1.0)))
                if np.isfinite(alignment)
                else np.nan
            )

    # Instantaneous rank of the two-direction matrices and projection onto the
    # final late feedback POD direction.
    final_feedback_rows = pod_frame.loc[
        pod_frame["object"] == "feedback_weight_tangent"
    ]
    final_feedback_interval = int(final_feedback_rows["interval_id"].max())
    late_direction = pod_directions[
        ("feedback_weight_tangent", final_feedback_interval)
    ].copy()
    if np.dot(late_direction, feedback[min(1, count - 1), -1]) < 0.0:
        late_direction *= -1.0

    instantaneous_rows: list[dict[str, Any]] = []
    scalar_rows: list[dict[str, Any]] = []
    for step in range(state_steps):
        matrix = feedback[:, step, :].T
        singular = np.linalg.svd(matrix, compute_uv=False)
        energy = singular**2
        energy_fraction = (
            float(energy[0] / np.sum(energy))
            if np.sum(energy) > args.vector_norm_tol**2
            else np.nan
        )
        instantaneous_rows.append(
            {
                "step": step,
                "time": step * args.dt,
                "feedback_rank1_energy_fraction": energy_fraction,
                "singular_value_1": float(singular[0]),
                "singular_value_2": float(singular[1]),
                "direction_alignment": abs(
                    robust_cosine(feedback[0, step], feedback[min(1, count - 1), step])
                ),
            }
        )
        for direction_id in range(count):
            for object_name, values in (
                ("total", total),
                ("homogeneous", homogeneous),
                ("feedback", feedback),
            ):
                vector = values[direction_id, step]
                amplitude = float(vector @ late_direction)
                transverse = vector - amplitude * late_direction
                scalar_rows.append(
                    {
                        "step": step,
                        "time": step * args.dt,
                        "direction_id": direction_id,
                        "object": object_name,
                        "scalar_amplitude": amplitude,
                        "vector_norm": float(np.linalg.norm(vector)),
                        "transverse_norm": float(np.linalg.norm(transverse)),
                        "transverse_fraction": float(
                            np.linalg.norm(transverse)
                            / max(np.linalg.norm(vector), 1e-300)
                        ),
                    }
                )

    instantaneous_rank = pd.DataFrame(instantaneous_rows)
    scalar_projection = pd.DataFrame(scalar_rows)

    component_audit.atomic_write_csv(
        output_dir / "target_time_memory_fits.csv", memory_fits
    )
    component_audit.atomic_write_csv(
        output_dir / "target_time_memory_curves.csv", memory_curves
    )
    component_audit.atomic_write_csv(
        output_dir / "pod_rank_by_interval.csv", pod_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "propagated_forcing_rank_by_target.csv", contribution_rank
    )
    component_audit.atomic_write_csv(
        output_dir / "instantaneous_feedback_rank.csv", instantaneous_rank
    )
    component_audit.atomic_write_csv(
        output_dir / "late_channel_scalar_projection.csv", scalar_projection
    )

    report = make_report(
        memory_fits,
        pod_frame,
        contribution_rank,
        ema_rate=ema_rate,
    )
    component_audit.atomic_write_text(
        output_dir / "feedback_rank_memory_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 feedback rank and target-time memory reduction",
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
        "target_times": args.target_times,
        "intervals": boundaries.tolist(),
        "thresholds": args.thresholds,
        "curve_stride": args.curve_stride,
        "fit_error_min": args.fit_error_min,
        "fit_error_max": args.fit_error_max,
        "vector_norm_tolerance": args.vector_norm_tol,
        "ema_rate": ema_rate,
        "late_feedback_direction": late_direction.tolist(),
        "outputs": [
            "target_time_memory_fits.csv",
            "target_time_memory_curves.csv",
            "pod_rank_by_interval.csv",
            "propagated_forcing_rank_by_target.csv",
            "instantaneous_feedback_rank.csv",
            "late_channel_scalar_projection.csv",
            "feedback_rank_memory_report.txt",
        ],
        "interpretation_constraints": [
            "Exponential fits characterize operational reconstruction error, not automatically an intrinsic kernel.",
            "Weighted and unit-vector POD answer different rank questions.",
            "A one-seed two-direction POD does not establish a universal invariant manifold.",
            "EMA parameter sensitivity requires consistently regenerated base trajectories.",
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
