#!/usr/bin/env python3
"""Test the analytic K3 defect mode and its one-step EMA recurrence.

For the fixed K3 winner branch, extract directly from each saved 3x3 matrix:

    beta25 = -K[0,2]/c0
    beta29 = -K[1,0]/c0
    beta59 = -K[2,0]/c0
    s7     = (K[0,0]-K[0,2])/c0
    s2     = (K[1,1]-K[1,0])/c0

and define

    delta   = beta25-beta59       # dominant left-breaking mismatch
    delta_R = s7-s2               # right-breaking scale mismatch
    delta_S = beta29-beta59       # secondary symmetry mismatch.

The proposed raw defect is

    E* = [[-1,0,-1],[0,0,0],[0,0,0]],

which satisfies E*v=0 for v=(1,-1,-1)/sqrt(3).  The script compares the
analytic projected defects with numerical family-defect POD directions,
checks whether family residuals equal c0*delta times the analytic projected
shape, and tests pointwise recurrences

    delta[n+1] ~= alpha_EMA delta[n],
    D[n+1]     ~= alpha_EMA D[n].

It also separates the best scalar defect multiplier from defect-shape change.
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
import AIEF_1_4_nested_operator_family_audit as nested


DEFAULT_COCYCLE_NPZ = "aief_1_4_frozen_driver_cocycle/frozen_cocycle_matrices.npz"
DEFAULT_MANIFEST = "runs/5a9f093a2fe0/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_defect_recurrence_analytic_mode"
DEFAULT_DT = 0.01
DEFAULT_INTERVALS = "100,150,200,250,320"
DEFAULT_LATE_START = 100.0
DEFAULT_SIGNAL_FLOOR = 1e-15
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


def raw_defect() -> np.ndarray:
    return np.array(
        [
            [-1.0, 0.0, -1.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
        ]
    )


def normalized_cosine(left: np.ndarray, right: np.ndarray) -> float:
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    if denominator <= np.finfo(float).tiny:
        return np.nan
    return float(
        np.clip(
            abs(float(np.vdot(left.reshape(-1), right.reshape(-1))))
            / denominator,
            0.0,
            1.0,
        )
    )


def scalar_recurrence_diagnostics(
    values: np.ndarray,
    alpha: float,
    dt: float,
    floor: float,
) -> dict[str, np.ndarray]:
    current = values[:-1]
    following = values[1:]
    valid = (
        np.isfinite(current)
        & np.isfinite(following)
        & (np.abs(current) > floor)
        & (np.abs(following) > floor)
    )
    ratio = np.full(len(current), np.nan)
    ema_relative_error = np.full(len(current), np.nan)
    local_rate = np.full(len(current), np.nan)
    ratio[valid] = following[valid] / current[valid]
    ema_relative_error[valid] = np.abs(
        following[valid] - alpha * current[valid]
    ) / np.abs(current[valid])
    local_rate[valid] = -np.log(np.abs(ratio[valid])) / dt
    return {
        "valid": valid,
        "ratio": ratio,
        "ema_relative_error": ema_relative_error,
        "local_rate": local_rate,
        "sign_change": valid & (np.sign(current) != np.sign(following)),
    }


def matrix_recurrence_diagnostics(
    defects: np.ndarray,
    alpha: float,
    floor: float,
) -> dict[str, np.ndarray]:
    count = len(defects) - 1
    best_multiplier = np.full(count, np.nan)
    ema_relative_error = np.full(count, np.nan)
    shape_relative_error = np.full(count, np.nan)
    norms = np.linalg.norm(defects.reshape(len(defects), -1), axis=1)
    for step in range(count):
        current = defects[step]
        following = defects[step + 1]
        if norms[step] <= floor or norms[step + 1] <= floor:
            continue
        multiplier = float(
            np.vdot(following.reshape(-1), current.reshape(-1))
            / np.vdot(current.reshape(-1), current.reshape(-1))
        )
        best_multiplier[step] = multiplier
        ema_relative_error[step] = float(
            np.linalg.norm(following - alpha * current) / norms[step]
        )
        shape_relative_error[step] = float(
            np.linalg.norm(following - multiplier * current)
            / norms[step + 1]
        )
    return {
        "norm": norms,
        "best_multiplier": best_multiplier,
        "ema_relative_error": ema_relative_error,
        "shape_relative_error": shape_relative_error,
    }


def interval_summary(
    frame: pd.DataFrame,
    start: int,
    end: int,
    interval_start: float,
    interval_end: float,
    alpha: float,
    ema_rate: float,
    dt: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in ("delta", "delta_R", "delta_S"):
        ratio = frame[f"{name}_ratio"].iloc[start:end].dropna().to_numpy(float)
        error = frame[f"{name}_ema_relative_error"].iloc[start:end].dropna().to_numpy(float)
        rate = frame[f"{name}_local_rate"].iloc[start:end].dropna().to_numpy(float)
        sign = frame[f"{name}_sign_change"].iloc[start:end].fillna(False).to_numpy(bool)
        rows.append(
            {
                "object": name,
                "start_time": interval_start,
                "end_time": interval_end,
                "valid_count": int(len(ratio)),
                "median_multiplier": float(np.median(ratio)) if len(ratio) else np.nan,
                "median_multiplier_minus_alpha": float(np.median(ratio) - alpha)
                if len(ratio)
                else np.nan,
                "median_ema_relative_error": float(np.median(error)) if len(error) else np.nan,
                "p95_ema_relative_error": float(np.quantile(error, 0.95)) if len(error) else np.nan,
                "median_local_rate": float(np.median(rate)) if len(rate) else np.nan,
                "median_rate_minus_EMA": float(np.median(rate) - ema_rate)
                if len(rate)
                else np.nan,
                "sign_change_count": int(np.sum(sign)),
            }
        )
    for name in ("biorthogonal", "symmetric"):
        multiplier = frame[f"{name}_best_multiplier"].iloc[start:end].dropna().to_numpy(float)
        ema_error = frame[f"{name}_matrix_ema_error"].iloc[start:end].dropna().to_numpy(float)
        shape_error = frame[f"{name}_shape_error"].iloc[start:end].dropna().to_numpy(float)
        rows.append(
            {
                "object": f"matrix_{name}",
                "start_time": interval_start,
                "end_time": interval_end,
                "valid_count": int(len(multiplier)),
                "median_multiplier": float(np.median(multiplier)) if len(multiplier) else np.nan,
                "median_multiplier_minus_alpha": float(np.median(multiplier) - alpha)
                if len(multiplier)
                else np.nan,
                "median_ema_relative_error": float(np.median(ema_error)) if len(ema_error) else np.nan,
                "p95_ema_relative_error": float(np.quantile(ema_error, 0.95)) if len(ema_error) else np.nan,
                "median_local_rate": float(
                    np.median(-np.log(np.abs(multiplier)) / dt)
                )
                if len(multiplier)
                else np.nan,
                "median_rate_minus_EMA": float(
                    np.median(-np.log(np.abs(multiplier)) / dt) - ema_rate
                )
                if len(multiplier)
                else np.nan,
                "median_shape_relative_error": float(np.median(shape_error)) if len(shape_error) else np.nan,
                "p95_shape_relative_error": float(np.quantile(shape_error, 0.95)) if len(shape_error) else np.nan,
                "sign_change_count": np.nan,
            }
        )
    return rows


def make_report(
    analytic_frame: pd.DataFrame,
    summary_frame: pd.DataFrame,
    *,
    alpha: float,
    ema_rate: float,
) -> str:
    lines = [
        "AIEF analytic defect-mode and EMA-recurrence audit",
        "=================================================",
        "",
        f"alpha_EMA: {alpha:.12g}",
        f"EMA rate: {ema_rate:.9g}",
        "",
        "Analytic/POD defect alignment",
        "-----------------------------",
    ]
    for _, row in analytic_frame.iterrows():
        lines.append(
            f"  family={row['family']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"POD_cosine={row['POD_analytic_cosine']:.12g}, "
            f"median_direct_reconstruction_error={row['median_direct_reconstruction_error']:.6g}, "
            f"p95={row['p95_direct_reconstruction_error']:.6g}"
        )

    lines.extend(["", "Pointwise recurrence summaries", "------------------------------"])
    for _, row in summary_frame.iterrows():
        lines.append(
            f"  object={row['object']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"valid={int(row['valid_count'])}, multiplier={row['median_multiplier']:.12g}, "
            f"minus_alpha={row['median_multiplier_minus_alpha']:.3g}, "
            f"EMA_error={row['median_ema_relative_error']:.3g}, "
            f"p95_EMA_error={row['p95_ema_relative_error']:.3g}, "
            f"local_rate={row['median_local_rate']:.6g}, "
            f"rate-EMA={row['median_rate_minus_EMA']:.3g}, "
            f"shape_error={row.get('median_shape_relative_error', np.nan):.3g}, "
            f"sign_changes={row['sign_change_count']}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* POD directions are compared with projected analytic defects, not with raw E* in the wrong quotient space.",
            "* Direct reconstruction error includes the smaller right and secondary symmetry mismatches.",
            "* Pointwise EMA agreement establishes a shared multiplier, not causal control by EMA memory.",
            "* Ratios are censored below the configured signal floor.",
            "* Results remain conditional on one replay and fixed winner branch.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cocycle-npz", default=DEFAULT_COCYCLE_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dt", type=float, default=DEFAULT_DT)
    parser.add_argument(
        "--intervals",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_INTERVALS),
    )
    parser.add_argument("--late-start", type=float, default=DEFAULT_LATE_START)
    parser.add_argument("--signal-floor", type=float, default=DEFAULT_SIGNAL_FLOOR)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.cocycle_npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.dt, args.signal_floor) <= 0.0:
        raise ValueError("dt and signal-floor must be positive")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = manifest["model"]
    gamma = float(model["gamma"])
    c0 = 1.0 - gamma * args.dt
    t_window = float(model["T_window"])
    alpha = math.exp(-args.dt / t_window)
    ema_rate = 1.0 / t_window

    with np.load(args.cocycle_npz, allow_pickle=False) as data:
        matrices = np.asarray(data["K3_matrix_sequence"], dtype=float).copy()
    steps = len(matrices)
    times = np.arange(steps) * args.dt

    bases = nested.family_bases()
    raw = raw_defect()
    projected_analytic: dict[str, np.ndarray] = {}
    for family in ("biorthogonal", "symmetric"):
        names, family_basis = bases[family]
        projection, _ = nested.project_family(raw, names, family_basis)
        projected_analytic[family] = raw - projection

    defects: dict[str, np.ndarray] = {
        "biorthogonal": np.empty_like(matrices),
        "symmetric": np.empty_like(matrices),
    }
    pod_leading: dict[tuple[str, int], np.ndarray] = {}

    beta25 = -matrices[:, 0, 2] / c0
    beta29 = -matrices[:, 1, 0] / c0
    beta59 = -matrices[:, 2, 0] / c0
    s7_from_row0 = (matrices[:, 0, 0] - matrices[:, 0, 2]) / c0
    s7_from_row2 = (matrices[:, 2, 2] - matrices[:, 2, 0]) / c0
    s7 = 0.5 * (s7_from_row0 + s7_from_row2)
    s2 = (matrices[:, 1, 1] - matrices[:, 1, 0]) / c0

    delta = beta25 - beta59
    delta_R = s7 - s2
    delta_S = beta29 - beta59
    controller_consistency = s7_from_row0 - s7_from_row2

    for family in defects:
        names, family_basis = bases[family]
        for step, matrix in enumerate(matrices):
            projection, _ = nested.project_family(matrix, names, family_basis)
            defects[family][step] = matrix - projection

    scalar_diag = {
        "delta": scalar_recurrence_diagnostics(
            delta, alpha, args.dt, args.signal_floor
        ),
        "delta_R": scalar_recurrence_diagnostics(
            delta_R, alpha, args.dt, args.signal_floor
        ),
        "delta_S": scalar_recurrence_diagnostics(
            delta_S, alpha, args.dt, args.signal_floor
        ),
    }
    matrix_diag = {
        family: matrix_recurrence_diagnostics(
            family_defect, alpha, args.signal_floor
        )
        for family, family_defect in defects.items()
    }

    trajectory_rows: list[dict[str, Any]] = []
    for step in range(steps - 1):
        row: dict[str, Any] = {
            "step": step,
            "time": times[step],
            "beta25": beta25[step],
            "beta29": beta29[step],
            "beta59": beta59[step],
            "s7": s7[step],
            "s2": s2[step],
            "s7_internal_consistency": controller_consistency[step],
            "delta": delta[step],
            "delta_R": delta_R[step],
            "delta_S": delta_S[step],
            "delta_to_right_ratio": abs(delta_R[step])
            / max(abs(delta[step]), ZERO_TOL),
            "delta_to_secondary_ratio": abs(delta_S[step])
            / max(abs(delta[step]), ZERO_TOL),
        }
        for name, diagnostics in scalar_diag.items():
            row[f"{name}_ratio"] = diagnostics["ratio"][step]
            row[f"{name}_ema_relative_error"] = diagnostics[
                "ema_relative_error"
            ][step]
            row[f"{name}_local_rate"] = diagnostics["local_rate"][step]
            row[f"{name}_sign_change"] = diagnostics["sign_change"][step]
        for family, diagnostics in matrix_diag.items():
            row[f"{family}_defect_norm"] = diagnostics["norm"][step]
            row[f"{family}_best_multiplier"] = diagnostics[
                "best_multiplier"
            ][step]
            row[f"{family}_matrix_ema_error"] = diagnostics[
                "ema_relative_error"
            ][step]
            row[f"{family}_shape_error"] = diagnostics[
                "shape_relative_error"
            ][step]
            predicted = c0 * delta[step] * projected_analytic[family]
            row[f"{family}_direct_reconstruction_error"] = float(
                np.linalg.norm(defects[family][step] - predicted)
                / max(np.linalg.norm(defects[family][step]), ZERO_TOL)
            )
        trajectory_rows.append(row)
    trajectory = pd.DataFrame(trajectory_rows)

    boundaries = np.asarray(args.intervals, dtype=float)
    if boundaries[0] > args.late_start:
        boundaries = np.concatenate(([args.late_start], boundaries))
    if boundaries[-1] < times[-1]:
        boundaries = np.concatenate((boundaries, [times[-1]]))
    boundaries = np.unique(boundaries)

    summary_rows: list[dict[str, Any]] = []
    analytic_rows: list[dict[str, Any]] = []
    for interval in range(len(boundaries) - 1):
        start = max(0, int(round(boundaries[interval] / args.dt)))
        end = min(steps - 1, int(round(boundaries[interval + 1] / args.dt)))
        if end <= start + 2:
            continue
        summary_rows.extend(
            interval_summary(
                trajectory,
                start,
                end,
                start * args.dt,
                end * args.dt,
                alpha,
                ema_rate,
                args.dt,
            )
        )
        for family in ("biorthogonal", "symmetric"):
            pod = nested.defect_pod(defects[family][start:end], args.signal_floor)
            leading = pod["leading_unit"].reshape(3, 3)
            pod_leading[(family, interval)] = leading
            cosine = normalized_cosine(
                leading, projected_analytic[family]
            )
            reconstruction = trajectory[
                f"{family}_direct_reconstruction_error"
            ].iloc[start:end].to_numpy(float)
            analytic_rows.append(
                {
                    "family": family,
                    "interval_id": interval,
                    "start_time": start * args.dt,
                    "end_time": end * args.dt,
                    "sample_count": pod["count"],
                    "POD_weighted_E1": pod["weighted_E1"],
                    "POD_unit_E1": pod["unit_E1"],
                    "POD_analytic_cosine": cosine,
                    "median_direct_reconstruction_error": float(
                        np.median(reconstruction)
                    ),
                    "p95_direct_reconstruction_error": float(
                        np.quantile(reconstruction, 0.95)
                    ),
                    "analytic_projected_defect_json": json_compact(
                        projected_analytic[family].tolist()
                    ),
                    "POD_leading_defect_json": json_compact(
                        leading.tolist()
                    ),
                }
            )

    summary_frame = pd.DataFrame(summary_rows)
    analytic_frame = pd.DataFrame(analytic_rows)

    component_audit.atomic_write_csv(
        output_dir / "defect_coefficient_trajectory.csv", trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "defect_recurrence_summary.csv", summary_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "analytic_defect_POD_comparison.csv", analytic_frame
    )
    component_audit.atomic_savez(
        output_dir / "analytic_defect_recurrence_arrays.npz",
        {
            "K3_matrix_sequence": matrices,
            "raw_analytic_defect": raw,
            "biorthogonal_analytic_defect": projected_analytic[
                "biorthogonal"
            ],
            "symmetric_analytic_defect": projected_analytic["symmetric"],
            "beta25": beta25,
            "beta29": beta29,
            "beta59": beta59,
            "s7": s7,
            "s2": s2,
            "delta": delta,
            "delta_R": delta_R,
            "delta_S": delta_S,
            "biorthogonal_defect": defects["biorthogonal"],
            "symmetric_defect": defects["symmetric"],
        },
    )

    report = make_report(
        analytic_frame,
        summary_frame,
        alpha=alpha,
        ema_rate=ema_rate,
    )
    component_audit.atomic_write_text(
        output_dir / "analytic_defect_recurrence_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 analytic defect mode and pointwise EMA recurrence",
        "source": {
            "path": str(Path(__file__).resolve()),
            "sha256": file_sha256(Path(__file__).resolve()),
        },
        "command": sys.argv,
        "inputs": {
            "cocycle_npz": {
                "path": str(Path(args.cocycle_npz).resolve()),
                "sha256": file_sha256(args.cocycle_npz),
            },
            "manifest": {
                "path": str(Path(args.manifest).resolve()),
                "sha256": file_sha256(args.manifest),
            },
        },
        "dt": args.dt,
        "intervals": boundaries.tolist(),
        "late_start": args.late_start,
        "signal_floor": args.signal_floor,
        "c0": c0,
        "alpha_EMA": alpha,
        "ema_rate": ema_rate,
        "outputs": [
            "defect_coefficient_trajectory.csv",
            "defect_recurrence_summary.csv",
            "analytic_defect_POD_comparison.csv",
            "analytic_defect_recurrence_arrays.npz",
            "analytic_defect_recurrence_report.txt",
        ],
        "interpretation_constraints": [
            "The raw analytic defect assumes scale and secondary symmetry mismatches are negligible; their measured remainders are reported separately.",
            "POD comparisons use the projected analytic defect in the matching quotient space.",
            "Pointwise EMA recurrence establishes a common multiplier, not causal derivation from EMA state equations.",
            "Ratios are censored below the configured signal floor.",
            "Results remain conditional on one replay and winner branch.",
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
