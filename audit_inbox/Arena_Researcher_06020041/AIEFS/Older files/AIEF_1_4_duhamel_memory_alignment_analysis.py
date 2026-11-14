#!/usr/bin/env python3
"""Post-process AIEF Duhamel vectors for memory and alignment diagnostics.

This script uses the saved exact Duhamel arrays, so it does not replay the
simulation.  It provides:
* exact-step homogeneous/feedback crossover times;
* robust signed cancellation angles and log feedback ratios;
* immediate alignment of forcing with the principal output singular vector;
* final-horizon alignment with a nondegenerate principal future input vector;
* propagated influence of every forcing step on the final feedback;
* recent-forcing reconstruction curves and effective memory horizons;
* corrected target-time summaries of tangent ablations after the updated
  Duhamel script has been rerun.

The term propagated influence is used instead of gain unless the ratio exceeds
one.  Time-resolved contribution vectors can cancel and are not interpreted as
additive percentages.
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
DEFAULT_ABLATION_CSV = "aief_1_4_augmented_duhamel_feedback/tangent_ablation_trajectory.csv"
DEFAULT_OUTPUT_DIR = "aief_1_4_duhamel_memory_alignment"
DEFAULT_DT = 0.01
DEFAULT_SAMPLE_STRIDE = 10
DEFAULT_MEMORY_THRESHOLDS = "0.5,0.1,0.01"
DEFAULT_TARGET_TIMES = "0.4,1,10,50,72.9,100,150,200,250,320"
ZERO_TOL = 1e-300


def file_sha256(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_positive_float_list(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated floats") from exc
    if not values or any(item <= 0.0 for item in values):
        raise argparse.ArgumentTypeError("values must be positive")
    return sorted(set(values))


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


def safe_log10_ratio(numerator: float, denominator: float) -> float:
    if numerator == 0.0 and denominator == 0.0:
        return np.nan
    if denominator == 0.0:
        return np.inf
    if numerator == 0.0:
        return -np.inf
    return float(math.log10(numerator) - math.log10(denominator))


def nearest_time_rows(
    frame: pd.DataFrame,
    target_times: list[float],
) -> pd.DataFrame:
    rows: list[pd.Series] = []
    if not len(frame):
        return frame.copy()
    times = frame["time"].to_numpy(float)
    for target in target_times:
        index = int(np.argmin(np.abs(times - target)))
        row = frame.iloc[index].copy()
        row["requested_target_time"] = target
        rows.append(row)
    return pd.DataFrame(rows)


def make_report(
    summary: pd.DataFrame,
    ablation_targets: pd.DataFrame,
    *,
    dt: float,
) -> str:
    lines = [
        "AIEF Duhamel memory and alignment analysis",
        "============================================",
        "",
        "Direction-wise mechanism summary",
        "--------------------------------",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"  direction={int(row['direction_id'])}: "
            f"exact_crossover_step={int(row['crossover_step']) if row['crossover_step'] >= 0 else -1}, "
            f"crossover_time={row['crossover_time']:.6g}, "
            f"median_immediate_alignment={row['median_immediate_output_alignment']:.6g}, "
            f"median_future_alignment={row['median_future_input_alignment']:.6g}, "
            f"strongest_final_forcing_time={row['strongest_final_forcing_time']:.6g}, "
            f"contribution_sum_error={row['final_contribution_sum_relative_error']:.3g}"
        )
        memory = json.loads(row["memory_horizons_json"])
        for threshold, horizon in memory.items():
            lines.append(
                f"    recent forcing horizon for relative error <= {threshold}: {horizon}"
            )

    lines.extend(["", "Selected ablation states", "------------------------"])
    if len(ablation_targets):
        for _, row in ablation_targets.iterrows():
            lines.append(
                f"  direction={int(row['direction_id'])}, ablation={row['ablation']}, "
                f"target={row['requested_target_time']:.6g}, actual_time={row['time']:.6g}, "
                f"full_norm={row['full_norm']:.6g}, ablation_norm={row['ablation_norm']:.6g}, "
                f"difference={row['absolute_difference']:.6g}, "
                f"ratio={row['norm_ratio']:.6g}, alignment={row['alignment']:.6g}"
            )
    else:
        lines.append("  no ablation CSV supplied")

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Exact crossover is computed at the original dt rather than the report sampling stride.",
            "* A principal future-input alignment is omitted when the largest future singular value is degenerate.",
            "* Propagated influence below one can still dominate after the homogeneous response decays.",
            "* Recent-memory horizons use vector reconstruction error and therefore include cancellation.",
            "* Ablation ratios near a zero of the full tangent are ill-conditioned; absolute norms and alignment must also be inspected.",
            f"* Time resolution: dt={dt}.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duhamel-npz", default=DEFAULT_DUHAMEL_NPZ)
    parser.add_argument("--ablation-csv", default=DEFAULT_ABLATION_CSV)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dt", type=float, default=DEFAULT_DT)
    parser.add_argument("--sample-stride", type=int, default=DEFAULT_SAMPLE_STRIDE)
    parser.add_argument(
        "--memory-thresholds",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_MEMORY_THRESHOLDS),
    )
    parser.add_argument(
        "--target-times",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_TARGET_TIMES),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if not os.path.isfile(args.duhamel_npz):
        raise FileNotFoundError(args.duhamel_npz)
    if args.dt <= 0.0 or args.sample_stride <= 0:
        raise ValueError("dt and sample-stride must be positive")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with np.load(args.duhamel_npz, allow_pickle=False) as data:
        total = np.asarray(data["total_weight_tangent"], dtype=float).copy()
        homogeneous = np.asarray(
            data["homogeneous_weight_tangent"], dtype=float
        ).copy()
        feedback = np.asarray(data["feedback_weight_tangent"], dtype=float).copy()
        forcing = np.asarray(data["instant_forcing"], dtype=float).copy()
        matrices = np.asarray(data["K3_matrix_sequence"], dtype=float).copy()
        directions = np.asarray(data["directions"], dtype=float).copy()
    count, state_steps, dimension = total.shape
    future_steps = state_steps - 1
    if dimension != 3 or matrices.shape != (future_steps, 3, 3):
        raise ValueError("unexpected Duhamel array shapes")
    if forcing.shape != (count, future_steps, 3):
        raise ValueError("unexpected forcing shape")

    trajectory_rows: list[dict[str, Any]] = []
    forcing_rows: list[dict[str, Any]] = []
    recent_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for direction_id in range(count):
        hnorms = np.linalg.norm(homogeneous[direction_id], axis=1)
        rnorms = np.linalg.norm(feedback[direction_id], axis=1)
        ratios = np.divide(
            rnorms,
            hnorms,
            out=np.full_like(rnorms, np.inf),
            where=hnorms > 0.0,
        )
        crossing = np.flatnonzero(ratios >= 1.0)
        crossing_step = int(crossing[0]) if len(crossing) else -1

        for step in range(state_steps):
            if step % args.sample_stride != 0 and step != future_steps:
                continue
            hvec = homogeneous[direction_id, step]
            rvec = feedback[direction_id, step]
            bvec = total[direction_id, step]
            trajectory_rows.append(
                {
                    "direction_id": direction_id,
                    "step": step,
                    "time": step * args.dt,
                    "homogeneous_norm": float(hnorms[step]),
                    "feedback_norm": float(rnorms[step]),
                    "total_norm": float(np.linalg.norm(bvec)),
                    "feedback_to_homogeneous_ratio": float(ratios[step]),
                    "log10_feedback_to_homogeneous": safe_log10_ratio(
                        float(rnorms[step]), float(hnorms[step])
                    ),
                    "homogeneous_feedback_cosine": robust_cosine(hvec, rvec),
                    "reconstruction_relative_error": float(
                        np.linalg.norm(bvec - hvec - rvec)
                        / max(np.linalg.norm(bvec), 1e-300)
                    ),
                }
            )

        # Build all suffix propagators and per-step final contributions.
        contributions = np.zeros((future_steps, 3), dtype=float)
        immediate_alignment = np.full(future_steps, np.nan)
        future_alignment = np.full(future_steps, np.nan)
        future_gap = np.full(future_steps, np.nan)
        suffix = np.eye(3)
        for step in range(future_steps - 1, -1, -1):
            fvec = forcing[direction_id, step]
            contributions[step] = suffix @ fvec
            fnorm = float(np.linalg.norm(fvec))
            if fnorm > np.finfo(float).tiny:
                left, _, _ = np.linalg.svd(matrices[step])
                immediate_alignment[step] = float(
                    abs(fvec @ left[:, 0]) / fnorm
                )
                suffix_norm = float(np.linalg.norm(suffix))
                if suffix_norm > np.finfo(float).tiny:
                    _, singular, right_t = np.linalg.svd(suffix)
                    gap = float(
                        singular[0]
                        / max(singular[1], np.finfo(float).tiny)
                    )
                    future_gap[step] = gap
                    if gap > 1.0 + 1e-8:
                        future_alignment[step] = float(
                            abs(fvec @ right_t[0]) / fnorm
                        )
            suffix = suffix @ matrices[step]

        final_feedback = feedback[direction_id, -1]
        summed_contributions = np.sum(contributions, axis=0)
        contribution_sum_error = float(
            np.linalg.norm(summed_contributions - final_feedback)
            / max(np.linalg.norm(final_feedback), 1e-300)
        )
        for step in range(future_steps):
            fvec = forcing[direction_id, step]
            cvec = contributions[step]
            fnorm = float(np.linalg.norm(fvec))
            forcing_rows.append(
                {
                    "direction_id": direction_id,
                    "forcing_step": step,
                    "forcing_time": step * args.dt,
                    "instant_forcing_norm": fnorm,
                    "immediate_principal_output_alignment": immediate_alignment[step],
                    "future_principal_singular_gap": future_gap[step],
                    "future_principal_input_alignment": future_alignment[step],
                    "propagated_contribution_norm": float(np.linalg.norm(cvec)),
                    "propagated_influence_ratio": float(
                        np.linalg.norm(cvec) / max(fnorm, 1e-300)
                    ),
                    "alignment_with_final_feedback": robust_cosine(
                        cvec, final_feedback
                    ),
                }
            )

        # Reconstruct final feedback from increasingly long recent windows.
        recent = np.zeros(3)
        memory_horizons: dict[str, float | None] = {
            f"{threshold:g}": None for threshold in args.memory_thresholds
        }
        final_norm = float(np.linalg.norm(final_feedback))
        for step in range(future_steps - 1, -1, -1):
            recent += contributions[step]
            horizon = (future_steps - step) * args.dt
            relative_error = float(
                np.linalg.norm(recent - final_feedback)
                / max(final_norm, 1e-300)
            )
            for threshold in args.memory_thresholds:
                key = f"{threshold:g}"
                if memory_horizons[key] is None and relative_error <= threshold:
                    memory_horizons[key] = horizon
            if step % args.sample_stride == 0 or step == future_steps - 1:
                recent_rows.append(
                    {
                        "direction_id": direction_id,
                        "start_step": step,
                        "start_time": step * args.dt,
                        "recent_horizon": horizon,
                        "recent_reconstruction_norm": float(np.linalg.norm(recent)),
                        "relative_error_to_final_feedback": relative_error,
                        "alignment_with_final_feedback": robust_cosine(
                            recent, final_feedback
                        ),
                    }
                )

        strongest_step = int(
            np.argmax(np.linalg.norm(contributions, axis=1))
        )
        finite_immediate = immediate_alignment[np.isfinite(immediate_alignment)]
        finite_future = future_alignment[np.isfinite(future_alignment)]
        summary_rows.append(
            {
                "direction_id": direction_id,
                "crossover_step": crossing_step,
                "crossover_time": crossing_step * args.dt
                if crossing_step >= 0
                else np.nan,
                "median_immediate_output_alignment": float(
                    np.median(finite_immediate)
                )
                if len(finite_immediate)
                else np.nan,
                "median_future_input_alignment": float(
                    np.median(finite_future)
                )
                if len(finite_future)
                else np.nan,
                "strongest_final_forcing_step": strongest_step,
                "strongest_final_forcing_time": strongest_step * args.dt,
                "strongest_propagated_contribution_norm": float(
                    np.linalg.norm(contributions[strongest_step])
                ),
                "final_contribution_sum_relative_error": contribution_sum_error,
                "memory_horizons_json": json.dumps(memory_horizons, sort_keys=True),
            }
        )

    trajectory = pd.DataFrame(trajectory_rows)
    forcing_frame = pd.DataFrame(forcing_rows)
    recent_frame = pd.DataFrame(recent_rows)
    summary = pd.DataFrame(summary_rows)

    ablation_targets = pd.DataFrame()
    if args.ablation_csv and os.path.isfile(args.ablation_csv):
        ablation = pd.read_csv(args.ablation_csv)
        target_frames = []
        for (direction_id, label), group in ablation.groupby(
            ["direction_id", "ablation"]
        ):
            selected = nearest_time_rows(
                group.sort_values("time"), args.target_times
            )
            if not len(selected):
                continue
            selected["absolute_difference"] = (
                selected["relative_difference"] * selected["full_norm"]
            )
            target_frames.append(selected)
        if target_frames:
            ablation_targets = pd.concat(target_frames, ignore_index=True)

    component_audit.atomic_write_csv(
        output_dir / "exact_crossover_and_angles.csv", trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "forcing_alignment_and_final_influence.csv", forcing_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "recent_forcing_memory_curve.csv", recent_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "duhamel_mechanism_summary.csv", summary
    )
    component_audit.atomic_write_csv(
        output_dir / "selected_ablation_states.csv", ablation_targets
    )

    report = make_report(summary, ablation_targets, dt=args.dt)
    component_audit.atomic_write_text(
        output_dir / "duhamel_memory_alignment_report.txt", report
    )
    manifest = {
        "analysis": "AIEF-1.4 Duhamel memory and alignment post-processing",
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
            "ablation_csv": {
                "path": str(Path(args.ablation_csv).resolve()),
                "sha256": file_sha256(args.ablation_csv),
            }
            if args.ablation_csv and os.path.isfile(args.ablation_csv)
            else None,
        },
        "dt": args.dt,
        "sample_stride": args.sample_stride,
        "memory_thresholds": args.memory_thresholds,
        "target_times": args.target_times,
        "outputs": [
            "exact_crossover_and_angles.csv",
            "forcing_alignment_and_final_influence.csv",
            "recent_forcing_memory_curve.csv",
            "duhamel_mechanism_summary.csv",
            "selected_ablation_states.csv",
            "duhamel_memory_alignment_report.txt",
        ],
        "interpretation_constraints": [
            "Propagated influence is not called gain unless it exceeds one.",
            "Principal future alignment is omitted when the leading singular value is degenerate.",
            "Recent-memory curves include vector cancellation.",
            "Ablation ratios near zeros of the full tangent require absolute-norm inspection.",
        ],
    }
    component_audit.atomic_write_text(
        output_dir / "analysis_manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )

    print(report)
    print(f"Saved analysis to {output_dir.resolve()}")


if __name__ == "__main__":
    main()
