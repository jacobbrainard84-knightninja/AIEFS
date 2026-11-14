#!/usr/bin/env python3
"""Direct propagation-gap and geometric-direction controls for AIEF-1.4.

This no-replay script addresses the two questions left by the scalar reduction:

1. Does the operational memory rate equal the decay rate of the *actual
   propagated forcing ensemble* minus the projected forcing-envelope rate?
2. Do the scalar recurrence and rate conclusions survive replacement of the
   data-derived POD axis by the analytic K3 lineality vector

       v_geom = (1,-1,-1)/sqrt(3)?

For each target and forcing time it constructs

    c_{T,m} = U_K(T,m+1) f_m.

It fits both norm and scalar-channel propagation ratios, and directly fits the
age envelope of the propagated contributions.  It also diagnoses why the
late two-state coordinates (a,g) may be unidentifiable by reporting design
singular values, correlations, and coefficient stability for

    g_{n+1} = rho g_n + chi a_n

across directions, pooled data, and rolling late windows.
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
DEFAULT_OUTPUT_DIR = "aief_1_4_propagation_gap_geometric_control"
DEFAULT_DT = 0.01
DEFAULT_TARGET_TIMES = "150,200,250,320"
DEFAULT_LOOKBACK = 66.6
DEFAULT_AGE_MINS = "0,10"
DEFAULT_POD_START = 250.0
DEFAULT_LATE_START = 200.0
DEFAULT_IDENT_WINDOW_LENGTH = 60.0
DEFAULT_IDENT_WINDOW_STARTS = "150,175,200,225"
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


def parse_positive_float_list(value: str) -> list[float]:
    values = parse_nonnegative_float_list(value)
    if any(value <= 0.0 for value in values):
        raise argparse.ArgumentTypeError("values must be positive")
    return values


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def fit_log_rate(
    independent: np.ndarray,
    positive_values: np.ndarray,
    tolerance: float,
) -> dict[str, float]:
    independent = np.asarray(independent, dtype=float)
    values = np.asarray(positive_values, dtype=float)
    valid = (
        np.isfinite(independent)
        & np.isfinite(values)
        & (values > tolerance)
    )
    if np.sum(valid) < 3:
        return {
            "count": int(np.sum(valid)),
            "rate": np.nan,
            "intercept": np.nan,
            "R_squared": np.nan,
            "rmse_log": np.nan,
        }
    x = independent[valid]
    y = np.log(values[valid])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "count": int(len(x)),
        "rate": float(-slope),
        "intercept": float(intercept),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
        "rmse_log": float(np.sqrt(np.mean((y - prediction) ** 2))),
    }


def r_squared(actual: np.ndarray, prediction: np.ndarray) -> float:
    residual = float(np.sum((actual - prediction) ** 2))
    total = float(np.sum((actual - np.mean(actual)) ** 2))
    return float(1.0 - residual / total) if total > 0.0 else np.nan


def propagated_contributions(
    matrices: np.ndarray,
    forcing: np.ndarray,
    target_step: int,
) -> np.ndarray:
    contributions = np.zeros((target_step, 3), dtype=float)
    suffix = np.eye(3)
    for step in range(target_step - 1, -1, -1):
        contributions[step] = suffix @ forcing[step]
        suffix = suffix @ matrices[step]
    return contributions


def fit_g_equation(
    a: np.ndarray,
    g: np.ndarray,
    start: int,
    end: int,
) -> dict[str, Any]:
    """Fit g[n+1]=rho*g[n]+chi*a[n], no intercept, with scaling."""
    X = np.column_stack([g[start:end], a[start:end]])
    y = g[start + 1 : end + 1]
    scales = np.maximum(np.max(np.abs(X), axis=0), np.finfo(float).tiny)
    y_scale = max(float(np.max(np.abs(y))), np.finfo(float).tiny)
    Xs = X / scales[None, :]
    ys = y / y_scale
    coefficients_scaled, *_ = np.linalg.lstsq(Xs, ys, rcond=1e-12)
    coefficients = y_scale * coefficients_scaled / scales
    prediction = X @ coefficients
    singular = np.linalg.svd(Xs, compute_uv=False)
    correlation = float(np.corrcoef(X[:, 0], X[:, 1])[0, 1])
    return {
        "rho": float(coefficients[0]),
        "chi": float(coefficients[1]),
        "R_squared": r_squared(y, prediction),
        "relative_RMSE": float(
            np.linalg.norm(y - prediction) / max(np.linalg.norm(y), ZERO_TOL)
        ),
        "condition_number": float(
            singular[0] / singular[-1]
        ) if singular[-1] > 0.0 else np.inf,
        "singular_value_1": float(singular[0]),
        "singular_value_2": float(singular[-1]),
        "g_a_correlation": correlation,
        "count": int(len(y)),
    }


def geometric_direction() -> np.ndarray:
    return np.array([1.0, -1.0, -1.0]) / math.sqrt(3.0)


def make_report(
    direction_control: pd.DataFrame,
    propagation: pd.DataFrame,
    identifiability: pd.DataFrame,
    *,
    pod_direction: np.ndarray,
    geom_direction: np.ndarray,
    ema_rate: float,
) -> str:
    alignment = abs(float(pod_direction @ geom_direction))
    angle = math.degrees(math.acos(np.clip(alignment, -1.0, 1.0)))
    lines = [
        "AIEF propagation-gap and geometric-direction control",
        "====================================================",
        "",
        f"POD direction: {pod_direction.tolist()}",
        f"Geometric direction: {geom_direction.tolist()}",
        f"Unsigned angle: {angle:.9g} degrees",
        f"EMA rate: {ema_rate:.9g}",
        "",
        "Direction-control scalar diagnostics",
        "------------------------------------",
    ]
    for _, row in direction_control.iterrows():
        lines.append(
            f"  axis={row['axis']}, direction={int(row['direction_id'])}: "
            f"median_invariance={row['median_invariance_relative']:.6g}, "
            f"median_scalar_residual={row['median_scalar_residual']:.6g}, "
            f"median_weight_rate={row['median_projected_weight_rate']:.6g}, "
            f"forcing_rate={row['forcing_rate']:.6g}, forcing_R2={row['forcing_R2']:.6g}"
        )

    lines.extend(["", "Direct propagation-gap tests", "----------------------------"])
    for _, row in propagation.iterrows():
        lines.append(
            f"  axis={row['axis']}, direction={int(row['direction_id'])}, "
            f"target={row['target_time']:.6g}, age_min={row['age_min']:.6g}: "
            f"kappa_obs={row['observed_kappa']:.6g}, "
            f"rprop_scalar={row['scalar_propagation_rate']:.6g}, "
            f"rg_scalar={row['scalar_forcing_rate']:.6g}, "
            f"gap_scalar={row['scalar_predicted_gap']:.6g}, "
            f"error_scalar={row['scalar_gap_error']:.6g}, "
            f"direct_contribution_rate={row['direct_contribution_rate']:.6g}, "
            f"R2={row['direct_contribution_R2']:.6g}"
        )

    lines.extend(["", "Forcing-state identifiability", "-----------------------------"])
    for _, row in identifiability.iterrows():
        lines.append(
            f"  axis={row['axis']}, dataset={row['dataset']}, "
            f"window=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"rho={row['rho']:.6g}, chi={row['chi']:.6g}, R2={row['R_squared']:.6g}, "
            f"condition={row['condition_number']:.6g}, corr={row['g_a_correlation']:.6g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* POD and analytic geometric axes are tested separately to avoid circularity.",
            "* Propagation fits use the actual forcing ensemble and are distinct from Rayleigh, eigenvalue, and singular-value rates.",
            "* Direct contribution-envelope fits include both forcing evolution and propagation; they should be compared directly with observed kappa.",
            "* Large design condition and |corr(a,g)| near one indicate non-identifiability of rho and chi even when R2 is excellent.",
            "* Results remain conditional on this replay and two initial directions.",
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
    parser.add_argument(
        "--target-times",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_TARGET_TIMES),
    )
    parser.add_argument("--lookback", type=float, default=DEFAULT_LOOKBACK)
    parser.add_argument(
        "--age-mins",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_AGE_MINS),
    )
    parser.add_argument("--pod-start", type=float, default=DEFAULT_POD_START)
    parser.add_argument("--late-start", type=float, default=DEFAULT_LATE_START)
    parser.add_argument(
        "--ident-window-length", type=float, default=DEFAULT_IDENT_WINDOW_LENGTH
    )
    parser.add_argument(
        "--ident-window-starts",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_IDENT_WINDOW_STARTS),
    )
    parser.add_argument("--scalar-tol", type=float, default=DEFAULT_SCALAR_TOL)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.duhamel_npz, args.memory_fits, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(
        args.dt,
        args.lookback,
        args.ident_window_length,
        args.scalar_tol,
    ) <= 0.0:
        raise ValueError("dt, windows, and scalar-tol must be positive")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    ema_rate = 1.0 / float(manifest["model"]["T_window"])

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

    pod_step = min(future_steps, int(round(args.pod_start / args.dt)))
    late_vectors = feedback[:, pod_step:, :].reshape(-1, 3)
    norms = np.linalg.norm(late_vectors, axis=1)
    late_vectors = late_vectors[norms > args.scalar_tol]
    left, _, _ = np.linalg.svd(late_vectors.T, full_matrices=False)
    pod_direction = left[:, 0]
    geom_direction = geometric_direction()
    if np.dot(pod_direction, geom_direction) < 0.0:
        pod_direction *= -1.0

    axes = {
        "POD": pod_direction,
        "geometric": geom_direction,
    }
    direction_control_rows: list[dict[str, Any]] = []
    propagation_rows: list[dict[str, Any]] = []
    identifiability_rows: list[dict[str, Any]] = []
    contribution_rows: list[dict[str, Any]] = []

    late_step = int(round(args.late_start / args.dt))
    for axis_name, axis in axes.items():
        a = total @ axis
        g = forcing @ axis
        lambdas = np.einsum("i,nij,j->n", axis, matrices, axis)
        Kaxis = np.einsum("nij,j->ni", matrices, axis)
        defects = np.linalg.norm(
            Kaxis - lambdas[:, None] * axis[None, :], axis=1
        ) / np.maximum(np.linalg.norm(Kaxis, axis=1), ZERO_TOL)
        projected_rates = -np.log(np.maximum(np.abs(lambdas), ZERO_TOL)) / args.dt

        for direction_id in range(count):
            residuals = []
            relative_residuals = []
            for step in range(future_steps):
                transverse = (
                    total[direction_id, step]
                    - a[direction_id, step] * axis
                )
                epsilon = float(axis @ matrices[step] @ transverse)
                residual = float(
                    a[direction_id, step + 1]
                    - lambdas[step] * a[direction_id, step]
                    - g[direction_id, step]
                )
                residuals.append(residual - epsilon)
                relative_residuals.append(
                    abs(residual)
                    / max(
                        abs(a[direction_id, step + 1]),
                        abs(lambdas[step] * a[direction_id, step])
                        + abs(g[direction_id, step]),
                        args.scalar_tol,
                    )
                )
            forcing_fit = fit_log_rate(
                np.arange(late_step, future_steps) * args.dt,
                np.abs(g[direction_id, late_step:]),
                args.scalar_tol,
            )
            direction_control_rows.append(
                {
                    "axis": axis_name,
                    "direction_id": direction_id,
                    "late_start": args.late_start,
                    "median_invariance_relative": float(
                        np.median(defects[late_step:])
                    ),
                    "maximum_invariance_relative": float(
                        np.max(defects[late_step:])
                    ),
                    "median_scalar_residual": float(
                        np.median(relative_residuals[late_step:])
                    ),
                    "maximum_scalar_residual": float(
                        np.max(relative_residuals[late_step:])
                    ),
                    "maximum_residual_minus_epsilon": float(
                        np.max(np.abs(residuals[late_step:]))
                    ),
                    "median_projected_weight_rate": float(
                        np.median(projected_rates[late_step:])
                    ),
                    "forcing_rate": forcing_fit["rate"],
                    "forcing_R2": forcing_fit["R_squared"],
                }
            )

        for direction_id in range(count):
            for target_time in args.target_times:
                target_step = min(
                    future_steps, int(round(target_time / args.dt))
                )
                start_step = max(
                    0,
                    target_step - int(round(args.lookback / args.dt)),
                )
                contributions = propagated_contributions(
                    matrices,
                    forcing[direction_id],
                    target_step,
                )
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

                all_steps = np.arange(start_step, target_step)
                ages_all = (target_step - all_steps) * args.dt
                f_norm = np.linalg.norm(
                    forcing[direction_id, start_step:target_step], axis=1
                )
                c_norm = np.linalg.norm(
                    contributions[start_step:target_step], axis=1
                )
                scalar_input = np.abs(g[direction_id, start_step:target_step])
                scalar_output = np.abs(
                    contributions[start_step:target_step] @ axis
                )
                forcing_fit = fit_log_rate(
                    all_steps * args.dt,
                    scalar_input,
                    args.scalar_tol,
                )

                for age_min in args.age_mins:
                    age_mask = ages_all >= age_min
                    norm_ratio = c_norm[age_mask] / np.maximum(
                        f_norm[age_mask], args.scalar_tol
                    )
                    scalar_ratio = scalar_output[age_mask] / np.maximum(
                        scalar_input[age_mask], args.scalar_tol
                    )
                    norm_prop_fit = fit_log_rate(
                        ages_all[age_mask], norm_ratio, args.scalar_tol
                    )
                    scalar_prop_fit = fit_log_rate(
                        ages_all[age_mask], scalar_ratio, args.scalar_tol
                    )
                    direct_fit = fit_log_rate(
                        ages_all[age_mask],
                        scalar_output[age_mask],
                        args.scalar_tol,
                    )
                    scalar_gap = scalar_prop_fit["rate"] - forcing_fit["rate"]
                    norm_gap = norm_prop_fit["rate"] - forcing_fit["rate"]
                    propagation_rows.append(
                        {
                            "axis": axis_name,
                            "direction_id": direction_id,
                            "target_time": target_time,
                            "observed_target_time": observed_target,
                            "fit_start_time": start_step * args.dt,
                            "fit_end_time": target_step * args.dt,
                            "age_min": age_min,
                            "observed_kappa": observed_kappa,
                            "scalar_forcing_rate": forcing_fit["rate"],
                            "scalar_forcing_R2": forcing_fit["R_squared"],
                            "norm_propagation_rate": norm_prop_fit["rate"],
                            "norm_propagation_R2": norm_prop_fit["R_squared"],
                            "scalar_propagation_rate": scalar_prop_fit["rate"],
                            "scalar_propagation_R2": scalar_prop_fit["R_squared"],
                            "norm_predicted_gap": norm_gap,
                            "scalar_predicted_gap": scalar_gap,
                            "norm_gap_error": observed_kappa - norm_gap,
                            "scalar_gap_error": observed_kappa - scalar_gap,
                            "direct_contribution_rate": direct_fit["rate"],
                            "direct_contribution_R2": direct_fit["R_squared"],
                            "direct_contribution_error": observed_kappa
                            - direct_fit["rate"],
                        }
                    )

                # Save sampled contribution envelopes for plotting/audit.
                for local_index, step in enumerate(all_steps):
                    if local_index % 10 != 0 and step != target_step - 1:
                        continue
                    contribution_rows.append(
                        {
                            "axis": axis_name,
                            "direction_id": direction_id,
                            "target_time": target_time,
                            "forcing_step": int(step),
                            "forcing_time": step * args.dt,
                            "age": ages_all[local_index],
                            "forcing_norm": f_norm[local_index],
                            "contribution_norm": c_norm[local_index],
                            "scalar_forcing_abs": scalar_input[local_index],
                            "scalar_contribution_abs": scalar_output[local_index],
                        }
                    )

        # Identifiability of g[n+1]=rho*g[n]+chi*a[n].
        datasets = {
            f"direction_{direction_id}": (
                a[direction_id], g[direction_id]
            )
            for direction_id in range(count)
        }
        for window_start in args.ident_window_starts:
            start = int(round(window_start / args.dt))
            end = min(
                future_steps - 1,
                int(round((window_start + args.ident_window_length) / args.dt)),
            )
            if end <= start + 2:
                continue
            for dataset, (a_values, g_values) in datasets.items():
                fit = fit_g_equation(a_values, g_values, start, end)
                identifiability_rows.append(
                    {
                        "axis": axis_name,
                        "dataset": dataset,
                        "start_time": start * args.dt,
                        "end_time": end * args.dt,
                        **fit,
                    }
                )
            # Pooled fit: concatenate pairs from both directions.
            X_parts = []
            y_parts = []
            for direction_id in range(count):
                X_parts.append(
                    np.column_stack(
                        [
                            g[direction_id, start:end],
                            a[direction_id, start:end],
                        ]
                    )
                )
                y_parts.append(g[direction_id, start + 1 : end + 1])
            X = np.concatenate(X_parts)
            y = np.concatenate(y_parts)
            scales = np.maximum(
                np.max(np.abs(X), axis=0), np.finfo(float).tiny
            )
            y_scale = max(float(np.max(np.abs(y))), np.finfo(float).tiny)
            Xs = X / scales[None, :]
            ys = y / y_scale
            coefficients_scaled, *_ = np.linalg.lstsq(Xs, ys, rcond=1e-12)
            coefficients = y_scale * coefficients_scaled / scales
            prediction = X @ coefficients
            singular = np.linalg.svd(Xs, compute_uv=False)
            identifiability_rows.append(
                {
                    "axis": axis_name,
                    "dataset": "pooled",
                    "start_time": start * args.dt,
                    "end_time": end * args.dt,
                    "rho": float(coefficients[0]),
                    "chi": float(coefficients[1]),
                    "R_squared": r_squared(y, prediction),
                    "relative_RMSE": float(
                        np.linalg.norm(y - prediction)
                        / max(np.linalg.norm(y), ZERO_TOL)
                    ),
                    "condition_number": float(
                        singular[0] / singular[-1]
                    )
                    if singular[-1] > 0.0
                    else np.inf,
                    "singular_value_1": float(singular[0]),
                    "singular_value_2": float(singular[-1]),
                    "g_a_correlation": float(np.corrcoef(X[:, 0], X[:, 1])[0, 1]),
                    "count": int(len(y)),
                }
            )

    direction_control = pd.DataFrame(direction_control_rows)
    propagation = pd.DataFrame(propagation_rows)
    identifiability = pd.DataFrame(identifiability_rows)
    contribution_frame = pd.DataFrame(contribution_rows)

    component_audit.atomic_write_csv(
        output_dir / "geometric_vs_POD_direction_control.csv", direction_control
    )
    component_audit.atomic_write_csv(
        output_dir / "direct_propagation_gap_tests.csv", propagation
    )
    component_audit.atomic_write_csv(
        output_dir / "propagated_contribution_envelopes.csv", contribution_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "forcing_state_identifiability.csv", identifiability
    )

    report = make_report(
        direction_control,
        propagation,
        identifiability,
        pod_direction=pod_direction,
        geom_direction=geom_direction,
        ema_rate=ema_rate,
    )
    component_audit.atomic_write_text(
        output_dir / "propagation_gap_geometric_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 propagation-gap and geometric-direction controls",
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
        "target_times": args.target_times,
        "lookback": args.lookback,
        "age_mins": args.age_mins,
        "pod_start": args.pod_start,
        "late_start": args.late_start,
        "ident_window_length": args.ident_window_length,
        "ident_window_starts": args.ident_window_starts,
        "scalar_tolerance": args.scalar_tol,
        "pod_direction": pod_direction.tolist(),
        "geometric_direction": geom_direction.tolist(),
        "ema_rate": ema_rate,
        "outputs": [
            "geometric_vs_POD_direction_control.csv",
            "direct_propagation_gap_tests.csv",
            "propagated_contribution_envelopes.csv",
            "forcing_state_identifiability.csv",
            "propagation_gap_geometric_report.txt",
        ],
        "interpretation_constraints": [
            "POD and geometric directions are tested separately.",
            "Propagation rates are fitted from the actual forcing ensemble and need not equal Rayleigh/eigen/singular rates.",
            "Excellent forcing-state R2 with a large condition number does not identify unique rho and chi coefficients.",
            "All conclusions remain conditional on one replay and two initial directions.",
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
