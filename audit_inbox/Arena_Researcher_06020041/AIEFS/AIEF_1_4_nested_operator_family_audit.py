#!/usr/bin/env python3
"""Nested operator-family and defect-mode audit for the exceptional AIEF K3.

The fixed K3 winner branch has selected matrix sparsity

    [p  0  q]
    [r  s  0]
    [t  0  u].

This script projects every saved K3 cocycle matrix onto four nested linear
families:

1. fixed sparsity;
2. right-invariant family for v=(1,-1,-1)/sqrt(3),
       p-q = s-r = u-t;
3. biorthogonal family for
       v=(1,-1,-1)/sqrt(3),
       u=sqrt(3)/2*(1,0,-1),
       K = [[p,0,q],[r,r+p-q,0],[q,0,p]];
4. symmetric two-parameter family
       K = [[d,0,q],[q,d,0],[q,0,d]].

It reports distances to each family, analytic left/right residuals, numerical
left-mode convergence, projected parameters, exponential decay fits, and POD
of normalized defect matrices over the complete late trajectory.
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


DEFAULT_COCYCLE_NPZ = "aief_1_4_frozen_driver_cocycle/frozen_cocycle_matrices.npz"
DEFAULT_MANIFEST = "runs/5a9f093a2fe0/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_nested_operator_family"
DEFAULT_DT = 0.01
DEFAULT_LATE_START = 100.0
DEFAULT_INTERVALS = "100,150,200,250,320"
DEFAULT_KEY_TIMES = "100,150,200,250,319.99"
DEFAULT_NORM_TOL = 1e-16
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


def geometric_right() -> np.ndarray:
    return np.array([1.0, -1.0, -1.0]) / math.sqrt(3.0)


def analytic_left() -> np.ndarray:
    return math.sqrt(3.0) / 2.0 * np.array([1.0, 0.0, -1.0])


def matrix_basis(entries: list[tuple[int, int, float]]) -> np.ndarray:
    matrix = np.zeros((3, 3), dtype=float)
    for row, column, value in entries:
        matrix[row, column] = value
    return matrix


def family_bases() -> dict[str, tuple[list[str], np.ndarray]]:
    sparse_names = ["p", "q", "r", "s", "t", "u"]
    sparse = np.stack(
        [
            matrix_basis([(0, 0, 1.0)]),
            matrix_basis([(0, 2, 1.0)]),
            matrix_basis([(1, 0, 1.0)]),
            matrix_basis([(1, 1, 1.0)]),
            matrix_basis([(2, 0, 1.0)]),
            matrix_basis([(2, 2, 1.0)]),
        ]
    )

    # Parameters q,r,t,lambda:
    # [[q+lambda,0,q],[r,r+lambda,0],[t,0,t+lambda]].
    right_names = ["q", "r", "t", "lambda"]
    right = np.stack(
        [
            matrix_basis([(0, 0, 1.0), (0, 2, 1.0)]),
            matrix_basis([(1, 0, 1.0), (1, 1, 1.0)]),
            matrix_basis([(2, 0, 1.0), (2, 2, 1.0)]),
            matrix_basis([(0, 0, 1.0), (1, 1, 1.0), (2, 2, 1.0)]),
        ]
    )

    # Parameters p,q,r:
    # [[p,0,q],[r,r+p-q,0],[q,0,p]].
    bi_names = ["p", "q", "r"]
    bi = np.stack(
        [
            matrix_basis([(0, 0, 1.0), (1, 1, 1.0), (2, 2, 1.0)]),
            matrix_basis([(0, 2, 1.0), (1, 1, -1.0), (2, 0, 1.0)]),
            matrix_basis([(1, 0, 1.0), (1, 1, 1.0)]),
        ]
    )

    # Parameters d,q, with q=-a in the earlier notation.
    symmetric_names = ["d", "q"]
    symmetric = np.stack(
        [
            matrix_basis([(0, 0, 1.0), (1, 1, 1.0), (2, 2, 1.0)]),
            matrix_basis([(0, 2, 1.0), (1, 0, 1.0), (2, 0, 1.0)]),
        ]
    )
    return {
        "sparse": (sparse_names, sparse),
        "right": (right_names, right),
        "biorthogonal": (bi_names, bi),
        "symmetric": (symmetric_names, symmetric),
    }


def project_family(
    matrix: np.ndarray,
    names: list[str],
    bases: np.ndarray,
) -> tuple[np.ndarray, dict[str, float]]:
    design = bases.reshape(len(bases), -1).T
    coefficients, *_ = np.linalg.lstsq(design, matrix.reshape(-1), rcond=None)
    projected = np.tensordot(coefficients, bases, axes=(0, 0))
    return projected, {
        name: float(value) for name, value in zip(names, coefficients)
    }


def fit_exponential(
    times: np.ndarray,
    values: np.ndarray,
    norm_tolerance: float,
) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    valid = np.isfinite(values) & (values > norm_tolerance)
    if np.sum(valid) < 3:
        return {
            "count": int(np.sum(valid)),
            "rate": np.nan,
            "R_squared": np.nan,
            "rmse_log": np.nan,
            "monotonic_violation_count": np.nan,
            "maximum_upward_jump": np.nan,
            "upward_variation_fraction": np.nan,
        }
    x = np.asarray(times, dtype=float)[valid]
    y_raw = values[valid]
    y = np.log(y_raw)
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    differences = np.diff(y_raw)
    upward = np.maximum(differences, 0.0)
    total_decay = max(float(y_raw[0] - y_raw[-1]), ZERO_TOL)
    return {
        "count": int(len(x)),
        "rate": float(-slope),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
        "rmse_log": float(np.sqrt(np.mean((y - prediction) ** 2))),
        "monotonic_violation_count": int(np.sum(differences > 0.0)),
        "maximum_upward_jump": float(np.max(upward)) if len(upward) else 0.0,
        "upward_variation_fraction": float(np.sum(upward) / total_decay),
    }


def defect_pod(defects: np.ndarray, tolerance: float) -> dict[str, Any]:
    flattened = defects.reshape(len(defects), -1)
    norms = np.linalg.norm(flattened, axis=1)
    valid = norms > tolerance
    selected = flattened[valid]
    if not len(selected):
        return {
            "count": 0,
            "weighted_E1": np.nan,
            "unit_E1": np.nan,
            "leading_weighted": np.full(9, np.nan),
            "leading_unit": np.full(9, np.nan),
        }
    matrix = selected.T
    left, singular, _ = np.linalg.svd(matrix, full_matrices=False)
    energy = singular**2
    normalized = (selected / np.linalg.norm(selected, axis=1)[:, None]).T
    unit_left, unit_singular, _ = np.linalg.svd(normalized, full_matrices=False)
    unit_energy = unit_singular**2
    return {
        "count": int(len(selected)),
        "weighted_E1": float(energy[0] / np.sum(energy)),
        "unit_E1": float(unit_energy[0] / np.sum(unit_energy)),
        "leading_weighted": left[:, 0],
        "leading_unit": unit_left[:, 0],
    }


def numerical_left_mode(matrix: np.ndarray, right: np.ndarray) -> dict[str, Any]:
    target = float(right @ matrix @ right)
    eigenvalues, eigenvectors = np.linalg.eig(matrix.T)
    index = int(np.argmin(np.abs(eigenvalues - target)))
    vector = eigenvectors[:, index]
    if np.max(np.abs(np.imag(vector))) > 1e-8:
        return {
            "vector": np.full(3, np.nan),
            "difference": np.nan,
            "angle": np.nan,
        }
    vector = np.real(vector)
    pairing = float(vector @ right)
    if abs(pairing) <= 1e-14:
        return {
            "vector": np.full(3, np.nan),
            "difference": np.nan,
            "angle": np.nan,
        }
    vector /= pairing
    candidate = analytic_left()
    alignment = abs(
        float(vector @ candidate)
        / (np.linalg.norm(vector) * np.linalg.norm(candidate))
    )
    return {
        "vector": vector,
        "difference": float(np.linalg.norm(vector - candidate)),
        "angle": float(
            math.degrees(math.acos(np.clip(alignment, -1.0, 1.0)))
        ),
    }


def make_report(
    key_frame: pd.DataFrame,
    fit_frame: pd.DataFrame,
    pod_frame: pd.DataFrame,
    *,
    ema_rate: float,
) -> str:
    lines = [
        "AIEF nested K3 operator-family audit",
        "====================================",
        "",
        f"EMA rate: {ema_rate:.9g}",
        "",
        "Key-time residuals",
        "------------------",
    ]
    for _, row in key_frame.iterrows():
        lines.append(
            f"  t={row['time']:.6g}: sparse={row['distance_sparse']:.3g}, "
            f"right={row['distance_right']:.3g}, biorth={row['distance_biorthogonal']:.3g}, "
            f"symmetric={row['distance_symmetric']:.3g}, "
            f"rR={row['analytic_right_residual']:.3g}, rL={row['analytic_left_residual']:.3g}, "
            f"left/sym={row['left_to_symmetric_ratio']:.6g}, "
            f"left/bi={row['left_to_biorthogonal_ratio']:.6g}"
        )

    lines.extend(["", "Decay fits", "----------"])
    for _, row in fit_frame.iterrows():
        lines.append(
            f"  metric={row['metric']}, window=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"rate={row['rate']:.6g}, R2={row['R_squared']:.6g}, "
            f"rate-EMA={row['rate_minus_EMA']:.3g}, "
            f"upward_fraction={row['upward_variation_fraction']:.3g}"
        )

    lines.extend(["", "Defect POD", "----------"])
    for _, row in pod_frame.iterrows():
        lines.append(
            f"  family={row['family']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"samples={int(row['sample_count'])}, weighted_E1={row['weighted_E1']:.6g}, "
            f"unit_E1={row['unit_E1']:.6g}, angle_to_final={row['angle_to_final_unit_degrees']:.6g} deg"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* The families are nested linear least-squares projections in the selected 3x3 edge coordinates.",
            "* Distance to the symmetric family is stronger than the distance required for the analytic biorthogonal pair.",
            "* Exponential fits establish replay regularities, not causal control by EMA memory.",
            "* A rank-one normalized defect POD supports a fixed defect shape but does not prove asymptotic continuation beyond the horizon.",
            "* Results remain conditional on one replay and one fixed winner branch.",
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
    parser.add_argument("--late-start", type=float, default=DEFAULT_LATE_START)
    parser.add_argument(
        "--intervals",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_INTERVALS),
    )
    parser.add_argument(
        "--key-times",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_KEY_TIMES),
    )
    parser.add_argument("--norm-tol", type=float, default=DEFAULT_NORM_TOL)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.cocycle_npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if args.dt <= 0.0 or args.norm_tol <= 0.0:
        raise ValueError("dt and norm-tol must be positive")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    ema_rate = 1.0 / float(manifest["model"]["T_window"])

    with np.load(args.cocycle_npz, allow_pickle=False) as data:
        matrices = np.asarray(data["K3_matrix_sequence"], dtype=float).copy()
    if matrices.ndim != 3 or matrices.shape[1:] != (3, 3):
        raise ValueError("expected K3 matrix sequence with shape (steps,3,3)")
    steps = len(matrices)
    times = np.arange(steps) * args.dt
    bases = family_bases()
    right = geometric_right()
    left = analytic_left()

    projections: dict[str, np.ndarray] = {
        family: np.empty_like(matrices) for family in bases
    }
    defects: dict[str, np.ndarray] = {
        family: np.empty_like(matrices) for family in bases
    }
    parameters: dict[str, list[dict[str, float]]] = {
        family: [] for family in bases
    }
    distances: dict[str, np.ndarray] = {
        family: np.empty(steps, dtype=float) for family in bases
    }
    right_residual = np.empty(steps)
    left_residual = np.empty(steps)
    numeric_left_difference = np.empty(steps)
    numeric_left_angle = np.empty(steps)
    lambda_analytic = np.empty(steps)

    for step, matrix in enumerate(matrices):
        matrix_norm = max(float(np.linalg.norm(matrix)), ZERO_TOL)
        for family, (names, family_basis) in bases.items():
            projected, coefficients = project_family(
                matrix, names, family_basis
            )
            projections[family][step] = projected
            defects[family][step] = matrix - projected
            distances[family][step] = float(
                np.linalg.norm(defects[family][step]) / matrix_norm
            )
            parameters[family].append(coefficients)

        lam = float(left @ matrix @ right)
        lambda_analytic[step] = lam
        right_residual[step] = float(
            np.linalg.norm(matrix @ right - lam * right)
            / max(np.linalg.norm(matrix @ right), ZERO_TOL)
        )
        left_residual[step] = float(
            np.linalg.norm(matrix.T @ left - lam * left)
            / max(np.linalg.norm(matrix.T @ left), ZERO_TOL)
        )
        numeric = numerical_left_mode(matrix, right)
        numeric_left_difference[step] = numeric["difference"]
        numeric_left_angle[step] = numeric["angle"]

    trajectory_rows: list[dict[str, Any]] = []
    for step in range(steps):
        row: dict[str, Any] = {
            "step": step,
            "time": times[step],
            "lambda_analytic": lambda_analytic[step],
            "analytic_right_residual": right_residual[step],
            "analytic_left_residual": left_residual[step],
            "numeric_left_difference": numeric_left_difference[step],
            "numeric_left_angle_degrees": numeric_left_angle[step],
        }
        for family in bases:
            row[f"distance_{family}"] = distances[family][step]
            for name, value in parameters[family][step].items():
                row[f"{family}_{name}"] = value
        row["left_to_symmetric_ratio"] = left_residual[step] / max(
            distances["symmetric"][step], ZERO_TOL
        )
        row["left_to_biorthogonal_ratio"] = left_residual[step] / max(
            distances["biorthogonal"][step], ZERO_TOL
        )
        trajectory_rows.append(row)
    trajectory = pd.DataFrame(trajectory_rows)

    key_rows = []
    for time_value in args.key_times:
        step = min(steps - 1, int(round(time_value / args.dt)))
        key_rows.append(trajectory.iloc[step].copy())
    key_frame = pd.DataFrame(key_rows)

    boundaries = np.asarray(args.intervals, dtype=float)
    if boundaries[0] > args.late_start:
        boundaries = np.concatenate(([args.late_start], boundaries))
    if boundaries[-1] < times[-1]:
        boundaries = np.concatenate((boundaries, [times[-1]]))
    boundaries = np.unique(boundaries)

    metric_arrays = {
        "distance_sparse": distances["sparse"],
        "distance_right": distances["right"],
        "distance_biorthogonal": distances["biorthogonal"],
        "distance_symmetric": distances["symmetric"],
        "analytic_right_residual": right_residual,
        "analytic_left_residual": left_residual,
        "numeric_left_difference": numeric_left_difference,
    }
    fit_rows: list[dict[str, Any]] = []
    for interval in range(len(boundaries) - 1):
        start = max(0, int(round(boundaries[interval] / args.dt)))
        end = min(steps, int(round(boundaries[interval + 1] / args.dt)))
        if end <= start + 2:
            continue
        for metric, values in metric_arrays.items():
            fit = fit_exponential(
                times[start:end], values[start:end], args.norm_tol
            )
            fit_rows.append(
                {
                    "metric": metric,
                    "start_time": start * args.dt,
                    "end_time": end * args.dt,
                    **fit,
                    "rate_minus_EMA": fit["rate"] - ema_rate
                    if np.isfinite(fit["rate"])
                    else np.nan,
                }
            )
    # Add one full late fit from late_start to the final state.
    late_start_step = int(round(args.late_start / args.dt))
    for metric, values in metric_arrays.items():
        fit = fit_exponential(
            times[late_start_step:], values[late_start_step:], args.norm_tol
        )
        fit_rows.append(
            {
                "metric": metric,
                "start_time": args.late_start,
                "end_time": times[-1],
                **fit,
                "rate_minus_EMA": fit["rate"] - ema_rate
                if np.isfinite(fit["rate"])
                else np.nan,
            }
        )
    fit_frame = pd.DataFrame(fit_rows)

    pod_rows: list[dict[str, Any]] = []
    pod_directions: dict[tuple[str, int], np.ndarray] = {}
    for family in ("right", "biorthogonal", "symmetric"):
        for interval in range(len(boundaries) - 1):
            start = max(0, int(round(boundaries[interval] / args.dt)))
            end = min(steps, int(round(boundaries[interval + 1] / args.dt)))
            if end <= start:
                continue
            pod = defect_pod(defects[family][start:end], args.norm_tol)
            pod_directions[(family, interval)] = pod["leading_unit"]
            pod_rows.append(
                {
                    "family": family,
                    "interval_id": interval,
                    "start_time": start * args.dt,
                    "end_time": end * args.dt,
                    "sample_count": pod["count"],
                    "weighted_E1": pod["weighted_E1"],
                    "unit_E1": pod["unit_E1"],
                    "leading_weighted_json": json_compact(
                        pod["leading_weighted"].tolist()
                    ),
                    "leading_unit_json": json_compact(
                        pod["leading_unit"].tolist()
                    ),
                }
            )
    pod_frame = pd.DataFrame(pod_rows)
    for family in ("right", "biorthogonal", "symmetric"):
        family_rows = pod_frame.loc[pod_frame["family"] == family]
        if not len(family_rows):
            continue
        final_interval = int(family_rows["interval_id"].max())
        final_direction = pod_directions[(family, final_interval)]
        for index in family_rows.index:
            interval = int(pod_frame.loc[index, "interval_id"])
            direction = pod_directions[(family, interval)]
            if np.any(~np.isfinite(direction)) or np.any(
                ~np.isfinite(final_direction)
            ):
                alignment = np.nan
            else:
                alignment = abs(
                    float(direction @ final_direction)
                    / (
                        np.linalg.norm(direction)
                        * np.linalg.norm(final_direction)
                    )
                )
            pod_frame.loc[index, "alignment_to_final_unit"] = alignment
            pod_frame.loc[index, "angle_to_final_unit_degrees"] = (
                math.degrees(math.acos(np.clip(alignment, -1.0, 1.0)))
                if np.isfinite(alignment)
                else np.nan
            )

    parameter_rows: list[dict[str, Any]] = []
    for family, values in parameters.items():
        for step, coefficients in enumerate(values):
            for parameter, value in coefficients.items():
                parameter_rows.append(
                    {
                        "family": family,
                        "step": step,
                        "time": times[step],
                        "parameter": parameter,
                        "value": value,
                    }
                )
    parameter_frame = pd.DataFrame(parameter_rows)

    component_audit.atomic_write_csv(
        output_dir / "nested_family_trajectory.csv", trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "nested_family_key_times.csv", key_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "nested_family_decay_fits.csv", fit_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "nested_family_defect_pod.csv", pod_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "nested_family_parameters.csv", parameter_frame
    )
    component_audit.atomic_savez(
        output_dir / "nested_family_arrays.npz",
        {
            "K3_matrix_sequence": matrices,
            "right_direction": right,
            "left_covector": left,
            "analytic_lambda": lambda_analytic,
            "analytic_right_residual": right_residual,
            "analytic_left_residual": left_residual,
            "numeric_left_difference": numeric_left_difference,
            **{
                f"projection_{family}": value
                for family, value in projections.items()
            },
            **{
                f"defect_{family}": value
                for family, value in defects.items()
            },
        },
    )

    report = make_report(
        key_frame,
        fit_frame,
        pod_frame,
        ema_rate=ema_rate,
    )
    component_audit.atomic_write_text(
        output_dir / "nested_operator_family_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 nested K3 operator-family and defect-mode audit",
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
        "late_start": args.late_start,
        "intervals": boundaries.tolist(),
        "key_times": args.key_times,
        "norm_tolerance": args.norm_tol,
        "families": {
            family: names for family, (names, _) in bases.items()
        },
        "right_direction": right.tolist(),
        "left_covector": left.tolist(),
        "ema_rate": ema_rate,
        "outputs": [
            "nested_family_trajectory.csv",
            "nested_family_key_times.csv",
            "nested_family_decay_fits.csv",
            "nested_family_defect_pod.csv",
            "nested_family_parameters.csv",
            "nested_family_arrays.npz",
            "nested_operator_family_report.txt",
        ],
        "interpretation_constraints": [
            "Right, biorthogonal, and symmetric operator families are nested but impose different algebraic requirements.",
            "The symmetric family is sufficient but not necessary for the analytic left/right pair.",
            "Exponential replay fits do not establish causal control by EMA memory.",
            "Defect POD rank is finite-horizon numerical evidence, not an asymptotic proof.",
            "Results remain conditional on one fixed winner branch and replay.",
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
