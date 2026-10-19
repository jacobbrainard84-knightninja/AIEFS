#!/usr/bin/env python3
"""Exact squared-magnitude and radial-observable analysis for AIEF-1.4.

The full directed complex EMA differences do not decay at the EMA rate, while
the symmetrized resonance difference and downstream K3 operator defect do.
This script analyzes the nonlinear observation C -> |C| directly.

For each directed orientation of edges 25=(2,7) and 59=(7,11), define

    M = |C|^2,
    A = Re(conj(C) z),
    z = exp(i dphi).

The exact update is

    M_next = alpha^2 M + (1-alpha)^2 + 2 alpha (1-alpha) A,

so edge differences satisfy

    Delta M_next = alpha^2 Delta M + 2 alpha (1-alpha) Delta A.

An effective alpha-mode requires Delta A ~= Delta M/2.  The script checks this
pointwise, reconstructs magnitude differences exactly from squared magnitudes,
separates forward/reverse channels before symmetrization, audits radial and
tangential components with midpoint conditioning, and tests whether a late
(Delta B, Delta R) subsystem is identifiable beyond the autonomous
Delta R_next ~= alpha Delta R relation.
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

import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_component_controller_audit as component_audit
import AIEF_1_4_augmented_tangent_cocycle_analysis as augmented


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_radial_observable_subsystem"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_INTERVALS = "0,100,150,200,250,320"
DEFAULT_SIGNAL_FLOOR = 1e-15
DEFAULT_MIDPOINT_FLOOR = 1e-8

EDGE_25 = 25
EDGE_59 = 59
NODE_7 = 7
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


def project_on_reference(
    difference: complex,
    reference: complex,
    midpoint_floor: float,
) -> tuple[float, float, float, bool]:
    reference_magnitude = abs(reference)
    reliable = reference_magnitude > midpoint_floor
    if not reliable:
        return np.nan, np.nan, reference_magnitude, False
    rotated = np.conj(reference) * difference / reference_magnitude
    return (
        float(np.real(rotated)),
        float(np.imag(rotated)),
        float(reference_magnitude),
        True,
    )


def radial_tangential(
    left: complex,
    right: complex,
    midpoint_floor: float,
) -> tuple[float, float, float, bool]:
    midpoint = 0.5 * (left + right)
    difference = left - right
    return project_on_reference(difference, midpoint, midpoint_floor)


def fit_log_rate(
    times: np.ndarray,
    values: np.ndarray,
    floor: float,
) -> dict[str, float]:
    magnitudes = np.abs(np.asarray(values, dtype=float))
    valid = np.isfinite(magnitudes) & (magnitudes > floor)
    if np.sum(valid) < 3:
        return {
            "count": int(np.sum(valid)),
            "rate": np.nan,
            "R_squared": np.nan,
            "rmse_log": np.nan,
        }
    x = np.asarray(times, dtype=float)[valid]
    y = np.log(magnitudes[valid])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "count": int(len(x)),
        "rate": float(-slope),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
        "rmse_log": float(np.sqrt(np.mean((y - prediction) ** 2))),
    }


def scalar_recurrence(
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
    multiplier = np.full(len(current), np.nan)
    relative_error = np.full(len(current), np.nan)
    local_rate = np.full(len(current), np.nan)
    multiplier[valid] = following[valid] / current[valid]
    relative_error[valid] = np.abs(
        following[valid] - alpha * current[valid]
    ) / np.abs(current[valid])
    local_rate[valid] = -np.log(np.abs(multiplier[valid])) / dt
    return {
        "valid": valid,
        "multiplier": multiplier,
        "relative_error": relative_error,
        "local_rate": local_rate,
        "sign_change": valid & (np.sign(current) != np.sign(following)),
    }


def fit_observable_subsystem(
    delta_B: np.ndarray,
    delta_R: np.ndarray,
    start: int,
    end: int,
) -> dict[str, Any]:
    """Fit DeltaR[n+1] = a DeltaR[n] + b DeltaB[n], no intercept."""
    X = np.column_stack(
        [delta_R[start:end], delta_B[start:end]]
    )
    y = delta_R[start + 1 : end + 1]
    scales = np.maximum(np.max(np.abs(X), axis=0), np.finfo(float).tiny)
    y_scale = max(float(np.max(np.abs(y))), np.finfo(float).tiny)
    Xs = X / scales[None, :]
    ys = y / y_scale
    coefficients_scaled, *_ = np.linalg.lstsq(Xs, ys, rcond=1e-12)
    coefficients = y_scale * coefficients_scaled / scales
    prediction = X @ coefficients
    singular = np.linalg.svd(Xs, compute_uv=False)
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    correlation = float(np.corrcoef(X[:, 0], X[:, 1])[0, 1])
    return {
        "a_R": float(coefficients[0]),
        "b_B": float(coefficients[1]),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
        "relative_RMSE": float(
            np.linalg.norm(y - prediction) / max(np.linalg.norm(y), ZERO_TOL)
        ),
        "condition_number": float(singular[0] / singular[-1])
        if singular[-1] > 0.0
        else np.inf,
        "singular_value_1": float(singular[0]),
        "singular_value_2": float(singular[-1]),
        "correlation_R_B": correlation,
        "count": int(len(y)),
    }


def make_report(
    identity_frame: pd.DataFrame,
    interval_frame: pd.DataFrame,
    subsystem_frame: pd.DataFrame,
    *,
    alpha: float,
    ema_rate: float,
    final_replay_exact: bool,
) -> str:
    lines = [
        "AIEF K3 radial observable and subsystem analysis",
        "================================================",
        "",
        f"alpha_EMA: {alpha:.12g}",
        f"EMA rate: {ema_rate:.9g}",
        f"Final replay exact: {final_replay_exact}",
        "",
        "Exact identity errors",
        "---------------------",
    ]
    for _, row in identity_frame.iterrows():
        lines.append(
            f"  {row['identity']}: max={row['maximum_absolute_error']:.6g}, "
            f"median={row['median_absolute_error']:.6g}"
        )

    lines.extend(["", "Interval observable diagnostics", "-------------------------------"])
    for _, row in interval_frame.iterrows():
        lines.append(
            f"  channel={row['channel']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"DeltaM_rate={row['DeltaM_rate']:.6g}, R2={row['DeltaM_R_squared']:.6g}, "
            f"alpha_error={row['median_DeltaM_alpha_error']:.3g}, "
            f"alignment_ratio={row['median_2DeltaA_over_DeltaM']:.6g}, "
            f"alignment_error={row['median_alignment_law_error']:.3g}, "
            f"radial_fraction={row['median_radial_fraction']:.6g}, "
            f"source_memory={row['median_source_to_memory_norm']:.6g}, "
            f"source_difference={row['median_source_minus_memory_ratio']:.6g}, "
            f"min_midpoint={row['minimum_midpoint_magnitude']:.6g}"
        )

    lines.extend(["", "Symmetrized resonance", "---------------------"])
    sym = interval_frame.loc[interval_frame["channel"] == "symmetrized"]
    for _, row in sym.iterrows():
        lines.append(
            f"  [{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"DeltaR_rate={row['DeltaM_rate']:.6g}, alpha_error={row['median_DeltaM_alpha_error']:.3g}, "
            f"cancellation={row['median_forward_reverse_cancellation']:.6g}"
        )

    lines.extend(["", "Observable subsystem fits", "-------------------------"])
    for _, row in subsystem_frame.iterrows():
        lines.append(
            f"  interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"a_R={row['a_R']:.12g}, b_B={row['b_B']:.6g}, "
            f"R2={row['R_squared']:.6g}, RMSE={row['relative_RMSE']:.3g}, "
            f"condition={row['condition_number']:.6g}, corr={row['correlation_R_B']:.6g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Squared-magnitude recurrences are exact; radial/tangential decompositions are geometric diagnostics.",
            "* DeltaA ~= DeltaM/2 is the precise condition for an effective alpha multiplier of DeltaM.",
            "* Forward and reverse directed channels are analyzed before symmetrization.",
            "* A well-fit but ill-conditioned (DeltaB,DeltaR) regression does not identify unique subsystem coefficients.",
            "* Results remain conditional on one replay and fixed K3 branch.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", default=DEFAULT_SEED)
    parser.add_argument("--dt", type=float, default=DEFAULT_DT)
    parser.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    parser.add_argument(
        "--intervals",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_INTERVALS),
    )
    parser.add_argument("--signal-floor", type=float, default=DEFAULT_SIGNAL_FLOOR)
    parser.add_argument("--midpoint-floor", type=float, default=DEFAULT_MIDPOINT_FLOOR)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(
        args.dt,
        args.scale_epsilon,
        args.signal_floor,
        args.midpoint_floor,
    ) <= 0.0:
        raise ValueError("dt and tolerances must be positive")
    if args.scale_epsilon != 1e-12:
        raise ValueError("implemented actual_step uses fixed scale epsilon=1e-12")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = manifest["model"]
    dt = float(model["dt"])
    if abs(dt - args.dt) > 1e-15:
        raise ValueError("command dt does not match manifest dt")
    alpha = math.exp(-dt / float(model["T_window"]))
    ema_rate = 1.0 / float(model["T_window"])
    gamma = float(model["gamma"])
    eta = float(model["eta"])
    mu = float(model["mu"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(int(model["N"]), capacity)
    A, edges = base.incidence_matrix(int(model["N"]))
    future_steps = int(manifest["protocol"]["future_steps"])

    edge_i, edge_j = edges
    if (int(edge_i[EDGE_25]), int(edge_j[EDGE_25])) != (2, 7):
        raise RuntimeError("edge 25 mapping mismatch")
    if (int(edge_i[EDGE_59]), int(edge_j[EDGE_59])) != (7, 11):
        raise RuntimeError("edge 59 mapping mismatch")

    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
        expected_final = np.asarray(
            data[base.branch_key("continue", args.seed, "B_final")], dtype=float
        ).copy()

    rows: list[dict[str, Any]] = []
    identity_errors: dict[str, list[float]] = {
        "squared_magnitude_forward": [],
        "squared_magnitude_reverse": [],
        "directed_magnitude_forward": [],
        "directed_magnitude_reverse": [],
        "symmetrized_R": [],
        "weight_difference_update": [],
    }

    for step in range(future_steps):
        intermediate = augmented.base_intermediates(
            state,
            model,
            capacities,
            A,
            edges,
            args.scale_epsilon,
        )

        directed = {
            "forward": ((2, 7), (7, 11)),
            "reverse": ((7, 2), (11, 7)),
        }
        channel_values: dict[str, dict[str, Any]] = {}
        for channel, (index_a, index_b) in directed.items():
            C_a = state.coherence_acc[index_a]
            C_b = state.coherence_acc[index_b]
            z_a = intermediate["phase_factor"][index_a]
            z_b = intermediate["phase_factor"][index_b]
            C_a_next = intermediate["updated_coherence"][index_a]
            C_b_next = intermediate["updated_coherence"][index_b]

            M_a = abs(C_a) ** 2
            M_b = abs(C_b) ** 2
            M_a_next = abs(C_a_next) ** 2
            M_b_next = abs(C_b_next) ** 2
            A_a = float(np.real(np.conj(C_a) * z_a))
            A_b = float(np.real(np.conj(C_b) * z_b))
            DeltaM = float(M_a - M_b)
            DeltaM_next = float(M_a_next - M_b_next)
            DeltaA = float(A_a - A_b)
            predicted_DeltaM_next = float(
                alpha**2 * DeltaM
                + 2.0 * alpha * (1.0 - alpha) * DeltaA
            )
            identity_errors[f"squared_magnitude_{channel}"].append(
                abs(DeltaM_next - predicted_DeltaM_next)
            )

            magnitude_difference = float(abs(C_a_next) - abs(C_b_next))
            magnitude_from_squares = float(
                DeltaM_next / max(abs(C_a_next) + abs(C_b_next), ZERO_TOL)
            )
            identity_errors[f"directed_magnitude_{channel}"].append(
                abs(magnitude_difference - magnitude_from_squares)
            )

            radial_old, tangential_old, midpoint_old, reliable_old = radial_tangential(
                C_a, C_b, args.midpoint_floor
            )
            radial_new, tangential_new, midpoint_new, reliable_new = radial_tangential(
                C_a_next, C_b_next, args.midpoint_floor
            )
            DeltaC = C_a - C_b
            DeltaZ = z_a - z_b
            old_midpoint = 0.5 * (C_a + C_b)
            # Project the phase-source difference onto the *memory* radial
            # frame.  Projecting onto the source's own midpoint would not test
            # how the source changes the magnitude observable.
            source_radial, source_tangential, source_reference_magnitude, source_reliable = project_on_reference(
                DeltaZ, old_midpoint, args.midpoint_floor
            )
            source_to_memory = abs(DeltaZ) / max(abs(DeltaC), ZERO_TOL)
            source_minus_memory = abs(DeltaZ - DeltaC) / max(
                abs(DeltaC), ZERO_TOL
            )
            radial_fraction = abs(radial_new) / max(
                math.sqrt(radial_new**2 + tangential_new**2), ZERO_TOL
            ) if reliable_new else np.nan
            alignment_ratio = 2.0 * DeltaA / DeltaM if abs(DeltaM) > args.signal_floor else np.nan
            alignment_error = abs(2.0 * DeltaA - DeltaM) / max(
                abs(DeltaM), args.signal_floor
            )
            alpha_error = abs(DeltaM_next - alpha * DeltaM) / max(
                abs(DeltaM), args.signal_floor
            )

            channel_values[channel] = {
                "DeltaM": DeltaM,
                "DeltaM_next": DeltaM_next,
                "DeltaA": DeltaA,
                "magnitude_difference": magnitude_difference,
                "radial_old": radial_old,
                "tangential_old": tangential_old,
                "radial_new": radial_new,
                "tangential_new": tangential_new,
                "source_radial": source_radial,
                "source_tangential": source_tangential,
                "midpoint_old": midpoint_old,
                "midpoint_new": midpoint_new,
                "source_reference_magnitude": source_reference_magnitude,
                "midpoint_reliable": reliable_old and reliable_new and source_reliable,
                "radial_fraction": radial_fraction,
                "source_to_memory": source_to_memory,
                "source_minus_memory": source_minus_memory,
                "alignment_ratio": alignment_ratio,
                "alignment_error": alignment_error,
                "alpha_error": alpha_error,
            }

        delta_R = float(
            intermediate["R"][edges][EDGE_25]
            - intermediate["R"][edges][EDGE_59]
        )
        delta_R_from_directed = 0.5 * (
            channel_values["forward"]["magnitude_difference"]
            + channel_values["reverse"]["magnitude_difference"]
        )
        identity_errors["symmetrized_R"].append(
            abs(delta_R - delta_R_from_directed)
        )
        denominator = (
            abs(channel_values["forward"]["magnitude_difference"])
            + abs(channel_values["reverse"]["magnitude_difference"])
        )
        cancellation = abs(
            channel_values["forward"]["magnitude_difference"]
            + channel_values["reverse"]["magnitude_difference"]
        ) / max(denominator, ZERO_TOL)

        B_edges = state.B[edges]
        B_next_edges = intermediate["projected"][edges]
        delta_B = float(B_edges[EDGE_25] - B_edges[EDGE_59])
        delta_B_next = float(
            B_next_edges[EDGE_25] - B_next_edges[EDGE_59]
        )
        s7 = float(intermediate["scales"][NODE_7])
        predicted_delta_B_next = float(
            s7
            * (
                (1.0 - gamma * dt) * delta_B
                + dt * (eta + mu) * delta_R
            )
        )
        identity_errors["weight_difference_update"].append(
            abs(delta_B_next - predicted_delta_B_next)
        )

        row: dict[str, Any] = {
            "step": step,
            "time": step * dt,
            "DeltaB": delta_B,
            "DeltaB_next": delta_B_next,
            "DeltaR": delta_R,
            "DeltaR_from_directed": delta_R_from_directed,
            "forward_reverse_cancellation": cancellation,
            "s7": s7,
            "DeltaB_weight_term": s7 * (1.0 - gamma * dt) * delta_B,
            "DeltaB_resonance_term": s7 * dt * (eta + mu) * delta_R,
        }
        for channel, values in channel_values.items():
            for key, value in values.items():
                row[f"{channel}_{key}"] = value
        rows.append(row)
        augmented.advance_base_state(state, intermediate)

    final_replay_exact = bool(np.array_equal(state.B, expected_final))
    trajectory = pd.DataFrame(rows)

    # Add pointwise recurrence diagnostics after full trajectories exist.
    for channel in ("forward", "reverse"):
        DeltaM = trajectory[f"{channel}_DeltaM"].to_numpy(float)
        recurrence = scalar_recurrence(
            DeltaM, alpha, dt, args.signal_floor
        )
        trajectory.loc[: len(recurrence["multiplier"]) - 1, f"{channel}_DeltaM_multiplier"] = recurrence[
            "multiplier"
        ]
        trajectory.loc[: len(recurrence["relative_error"]) - 1, f"{channel}_DeltaM_alpha_error_pointwise"] = recurrence[
            "relative_error"
        ]
        trajectory.loc[: len(recurrence["local_rate"]) - 1, f"{channel}_DeltaM_local_rate"] = recurrence[
            "local_rate"
        ]
    recurrence_R = scalar_recurrence(
        trajectory["DeltaR"].to_numpy(float),
        alpha,
        dt,
        args.signal_floor,
    )
    trajectory.loc[: len(recurrence_R["multiplier"]) - 1, "DeltaR_multiplier"] = recurrence_R[
        "multiplier"
    ]
    trajectory.loc[: len(recurrence_R["relative_error"]) - 1, "DeltaR_alpha_error_pointwise"] = recurrence_R[
        "relative_error"
    ]
    trajectory.loc[: len(recurrence_R["local_rate"]) - 1, "DeltaR_local_rate"] = recurrence_R[
        "local_rate"
    ]

    boundaries = np.asarray(args.intervals, dtype=float)
    if boundaries[0] > 0.0:
        boundaries = np.concatenate(([0.0], boundaries))
    if boundaries[-1] < (future_steps - 1) * dt:
        boundaries = np.concatenate(
            (boundaries, [(future_steps - 1) * dt])
        )
    boundaries = np.unique(boundaries)

    interval_rows: list[dict[str, Any]] = []
    subsystem_rows: list[dict[str, Any]] = []
    for interval in range(len(boundaries) - 1):
        start = max(0, int(round(boundaries[interval] / dt)))
        end = min(
            future_steps - 1,
            int(round(boundaries[interval + 1] / dt)),
        )
        if end <= start + 2:
            continue
        for channel in ("forward", "reverse"):
            fit = fit_log_rate(
                trajectory["time"].to_numpy(float)[start:end],
                trajectory[f"{channel}_DeltaM"].to_numpy(float)[start:end],
                args.signal_floor,
            )
            interval_rows.append(
                {
                    "channel": channel,
                    "start_time": start * dt,
                    "end_time": end * dt,
                    "DeltaM_rate": fit["rate"],
                    "DeltaM_R_squared": fit["R_squared"],
                    "rate_minus_EMA": fit["rate"] - ema_rate
                    if np.isfinite(fit["rate"])
                    else np.nan,
                    "median_DeltaM_alpha_error": float(
                        trajectory[f"{channel}_alpha_error"].iloc[start:end].median()
                    ),
                    "median_2DeltaA_over_DeltaM": float(
                        trajectory[f"{channel}_alignment_ratio"].iloc[start:end].median()
                    ),
                    "median_alignment_law_error": float(
                        trajectory[f"{channel}_alignment_error"].iloc[start:end].median()
                    ),
                    "median_radial_fraction": float(
                        trajectory[f"{channel}_radial_fraction"].iloc[start:end].median()
                    ),
                    "median_source_to_memory_norm": float(
                        trajectory[f"{channel}_source_to_memory"].iloc[start:end].median()
                    ),
                    "median_source_minus_memory_ratio": float(
                        trajectory[f"{channel}_source_minus_memory"].iloc[start:end].median()
                    ),
                    "minimum_midpoint_magnitude": float(
                        min(
                            trajectory[f"{channel}_midpoint_old"].iloc[start:end].min(),
                            trajectory[f"{channel}_midpoint_new"].iloc[start:end].min(),
                            trajectory[f"{channel}_source_reference_magnitude"].iloc[start:end].min(),
                        )
                    ),
                    "midpoint_unreliable_count": int(
                        np.sum(
                            ~trajectory[f"{channel}_midpoint_reliable"].iloc[start:end].to_numpy(bool)
                        )
                    ),
                    "median_forward_reverse_cancellation": np.nan,
                }
            )

        fit_R = fit_log_rate(
            trajectory["time"].to_numpy(float)[start:end],
            trajectory["DeltaR"].to_numpy(float)[start:end],
            args.signal_floor,
        )
        interval_rows.append(
            {
                "channel": "symmetrized",
                "start_time": start * dt,
                "end_time": end * dt,
                "DeltaM_rate": fit_R["rate"],
                "DeltaM_R_squared": fit_R["R_squared"],
                "rate_minus_EMA": fit_R["rate"] - ema_rate
                if np.isfinite(fit_R["rate"])
                else np.nan,
                "median_DeltaM_alpha_error": float(
                    trajectory["DeltaR_alpha_error_pointwise"].iloc[start:end].median()
                ),
                "median_2DeltaA_over_DeltaM": np.nan,
                "median_alignment_law_error": np.nan,
                "median_radial_fraction": np.nan,
                "median_source_to_memory_norm": np.nan,
                "median_source_minus_memory_ratio": np.nan,
                "minimum_midpoint_magnitude": np.nan,
                "midpoint_unreliable_count": 0,
                "median_forward_reverse_cancellation": float(
                    trajectory["forward_reverse_cancellation"].iloc[start:end].median()
                ),
            }
        )

        fit = fit_observable_subsystem(
            trajectory["DeltaB"].to_numpy(float),
            trajectory["DeltaR"].to_numpy(float),
            start,
            end,
        )
        autonomous_error = trajectory["DeltaR_alpha_error_pointwise"].iloc[
            start:end
        ].to_numpy(float)
        subsystem_rows.append(
            {
                "start_time": start * dt,
                "end_time": end * dt,
                **fit,
                "alpha_EMA": alpha,
                "a_R_minus_alpha": fit["a_R"] - alpha,
                "median_autonomous_alpha_error": float(
                    np.nanmedian(autonomous_error)
                ),
            }
        )

    interval_frame = pd.DataFrame(interval_rows)
    subsystem_frame = pd.DataFrame(subsystem_rows)

    identity_rows = []
    for name, values in identity_errors.items():
        identity_rows.append(
            {
                "identity": name,
                "maximum_absolute_error": float(np.max(values)),
                "median_absolute_error": float(np.median(values)),
            }
        )
    identity_frame = pd.DataFrame(identity_rows)

    component_audit.atomic_write_csv(
        output_dir / "radial_observable_trajectory.csv", trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "radial_observable_interval_summary.csv", interval_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "observable_subsystem_fits.csv", subsystem_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "radial_observable_identity_checks.csv", identity_frame
    )

    report = make_report(
        identity_frame,
        interval_frame,
        subsystem_frame,
        alpha=alpha,
        ema_rate=ema_rate,
        final_replay_exact=final_replay_exact,
    )
    component_audit.atomic_write_text(
        output_dir / "radial_observable_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 exact squared-magnitude and radial-observable subsystem",
        "source": {
            "path": str(Path(__file__).resolve()),
            "sha256": file_sha256(Path(__file__).resolve()),
        },
        "command": sys.argv,
        "inputs": {
            "npz": {
                "path": str(Path(args.npz).resolve()),
                "sha256": file_sha256(args.npz),
            },
            "manifest": {
                "path": str(Path(args.manifest).resolve()),
                "sha256": file_sha256(args.manifest),
            },
        },
        "seed": args.seed,
        "dt": dt,
        "alpha_EMA": alpha,
        "ema_rate": ema_rate,
        "scale_epsilon": args.scale_epsilon,
        "intervals": boundaries.tolist(),
        "signal_floor": args.signal_floor,
        "midpoint_floor": args.midpoint_floor,
        "final_replay_exact": final_replay_exact,
        "outputs": [
            "radial_observable_trajectory.csv",
            "radial_observable_interval_summary.csv",
            "observable_subsystem_fits.csv",
            "radial_observable_identity_checks.csv",
            "radial_observable_report.txt",
        ],
        "interpretation_constraints": [
            "Squared-magnitude identities are exact; radial/tangential decomposition is a conditioned geometric interpretation.",
            "DeltaA=DeltaM/2 is tested rather than assumed.",
            "Forward and reverse channels are kept separate before symmetrization.",
            "Observable-subsystem coefficient fits may be unidentifiable when DeltaB and DeltaR are collinear.",
            "Results remain conditional on one seed and fixed branch.",
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
