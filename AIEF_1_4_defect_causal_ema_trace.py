#!/usr/bin/env python3
"""Trace the analytic K3 operator defect back through EMA, R, and proposals.

This deterministic replay analysis follows the dominant defect

    delta_K = beta25-beta59 = (K[2,0]-K[0,2])/(1-gamma*dt)

through the exact implemented chain

    complex EMA -> symmetrized magnitude R -> adaptive proposal x
    -> common node-7 scale -> K3 Jacobian defect.

For edges 25=(2,7) and 59=(7,11), it records both directed complex EMA
orientations, phase-factor source differences, magnitude differences, B/R/F
proposal terms, and projected B updates.  It checks exact algebraic identities
and tests whether late source differences become negligible so that the complex
EMA difference follows its homogeneous multiplier alpha_EMA.

This can establish an implementation-level causal chain on the replay, but a
shared multiplier alone is not interpreted as universal causal control beyond
this branch and trajectory.
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
DEFAULT_COCYCLE_NPZ = "aief_1_4_frozen_driver_cocycle/frozen_cocycle_matrices.npz"
DEFAULT_OUTPUT_DIR = "aief_1_4_defect_causal_ema_trace"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_INTERVALS = "100,150,200,250,320"
DEFAULT_SIGNAL_FLOOR = 1e-15
ZERO_TOL = 1e-300

EDGE_25 = 25
EDGE_59 = 59
NODE_7 = 7


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
    rate = np.full(len(current), np.nan)
    multiplier[valid] = following[valid] / current[valid]
    relative_error[valid] = np.abs(
        following[valid] - alpha * current[valid]
    ) / np.abs(current[valid])
    rate[valid] = -np.log(np.abs(multiplier[valid])) / dt
    return {
        "valid": valid,
        "multiplier": multiplier,
        "relative_error": relative_error,
        "rate": rate,
        "sign_change": valid & (np.sign(current) != np.sign(following)),
    }


def linearized_magnitude_difference(
    left: complex,
    right: complex,
) -> float:
    midpoint = 0.5 * (left + right)
    difference = left - right
    magnitude = abs(midpoint)
    if magnitude <= np.finfo(float).tiny:
        return np.nan
    return float(np.real(np.conj(midpoint) * difference) / magnitude)


def make_report(
    interval_frame: pd.DataFrame,
    identity_frame: pd.DataFrame,
    *,
    alpha: float,
    ema_rate: float,
    final_replay_exact: bool,
) -> str:
    lines = [
        "AIEF K3 defect causal EMA trace",
        "================================",
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
            f"  {row['identity']}: max_abs={row['maximum_absolute_error']:.6g}, "
            f"median_abs={row['median_absolute_error']:.6g}"
        )

    lines.extend(["", "Interval dynamics", "-----------------"])
    for _, row in interval_frame.iterrows():
        lines.append(
            f"  object={row['object']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"rate={row['rate']:.6g}, R2={row['R_squared']:.6g}, "
            f"rate-EMA={row['rate_minus_EMA']:.3g}, "
            f"median_multiplier={row['median_multiplier']:.12g}, "
            f"EMA_error={row['median_ema_relative_error']:.3g}, "
            f"source_ratio={row['median_source_to_memory_ratio']:.3g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Complex EMA identities are checked in both directed orientations before R symmetrization.",
            "* A small phase-source ratio supports homogeneous EMA relaxation but does not prove why the source vanishes.",
            "* Magnitude linearization is a late small-difference approximation; its error is reported.",
            "* Shared decay rates on one replay are not universal causal evidence.",
            "* Results remain conditional on the fixed K3 branch and support.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--cocycle-npz", default=DEFAULT_COCYCLE_NPZ)
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
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.npz, args.manifest, args.cocycle_npz):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.dt, args.scale_epsilon, args.signal_floor) <= 0.0:
        raise ValueError("dt, scale-epsilon, and signal-floor must be positive")
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
    gamma = float(model["gamma"])
    eta = float(model["eta"])
    mu = float(model["mu"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(int(model["N"]), capacity)
    A, edges = base.incidence_matrix(int(model["N"]))
    c0 = 1.0 - gamma * dt
    alpha = math.exp(-dt / float(model["T_window"]))
    ema_rate = 1.0 / float(model["T_window"])
    future_steps = int(manifest["protocol"]["future_steps"])

    with np.load(args.cocycle_npz, allow_pickle=False) as data:
        matrices = np.asarray(data["K3_matrix_sequence"], dtype=float).copy()
    if len(matrices) != future_steps:
        raise ValueError("cocycle matrix sequence length mismatch")

    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
        expected_final = np.asarray(
            data[base.branch_key("continue", args.seed, "B_final")], dtype=float
        ).copy()

    edge_i, edge_j = edges
    if (int(edge_i[EDGE_25]), int(edge_j[EDGE_25])) != (2, 7):
        raise RuntimeError("edge 25 mapping mismatch")
    if (int(edge_i[EDGE_59]), int(edge_j[EDGE_59])) != (7, 11):
        raise RuntimeError("edge 59 mapping mismatch")

    rows: list[dict[str, Any]] = []
    ema_forward_error: list[float] = []
    ema_reverse_error: list[float] = []
    proposal_error: list[float] = []
    delta_operator_error: list[float] = []
    projected_B_error: list[float] = []

    for step in range(future_steps):
        intermediate = augmented.base_intermediates(
            state,
            model,
            capacities,
            A,
            edges,
            args.scale_epsilon,
        )
        K = matrices[step]

        # Directed orientations: 25=(2,7), 59=(7,11).
        C25_old_f = state.coherence_acc[2, 7]
        C59_old_f = state.coherence_acc[7, 11]
        C25_old_r = state.coherence_acc[7, 2]
        C59_old_r = state.coherence_acc[11, 7]
        C25_new_f = intermediate["updated_coherence"][2, 7]
        C59_new_f = intermediate["updated_coherence"][7, 11]
        C25_new_r = intermediate["updated_coherence"][7, 2]
        C59_new_r = intermediate["updated_coherence"][11, 7]
        z25_f = intermediate["phase_factor"][2, 7]
        z59_f = intermediate["phase_factor"][7, 11]
        z25_r = intermediate["phase_factor"][7, 2]
        z59_r = intermediate["phase_factor"][11, 7]

        dC_old_f = C25_old_f - C59_old_f
        dC_old_r = C25_old_r - C59_old_r
        dz_f = z25_f - z59_f
        dz_r = z25_r - z59_r
        dC_new_f = C25_new_f - C59_new_f
        dC_new_r = C25_new_r - C59_new_r
        predicted_dC_new_f = alpha * dC_old_f + (1.0 - alpha) * dz_f
        predicted_dC_new_r = alpha * dC_old_r + (1.0 - alpha) * dz_r
        error_f = abs(dC_new_f - predicted_dC_new_f)
        error_r = abs(dC_new_r - predicted_dC_new_r)
        ema_forward_error.append(error_f)
        ema_reverse_error.append(error_r)

        B_edges = state.B[edges]
        R_edges = intermediate["R"][edges]
        F_edges = intermediate["F_matrix"][edges]
        x = intermediate["x"]
        dB = float(B_edges[EDGE_25] - B_edges[EDGE_59])
        dR = float(R_edges[EDGE_25] - R_edges[EDGE_59])
        dF = float(F_edges[EDGE_25] - F_edges[EDGE_59])
        dx = float(x[EDGE_25] - x[EDGE_59])
        weight_term = (1.0 - gamma * dt) * dB
        resonance_term = dt * (eta + mu) * dR
        proposal_predicted = weight_term + resonance_term
        proposal_error.append(abs(dx - proposal_predicted))

        q7 = float(intermediate["q_scale"][NODE_7])
        s7 = float(intermediate["scales"][NODE_7])
        delta_from_K = float((K[2, 0] - K[0, 2]) / c0)
        delta_from_proposal = float(s7 / (q7 + args.scale_epsilon) * dx)
        delta_operator_error.append(abs(delta_from_K - delta_from_proposal))

        B_next_edges = intermediate["projected"][edges]
        dB_next = float(
            B_next_edges[EDGE_25] - B_next_edges[EDGE_59]
        )
        projected_predicted = s7 * dx
        projected_B_error.append(abs(dB_next - projected_predicted))

        # Exact magnitude difference and small-difference linearization.
        magnitude_forward = abs(C25_new_f) - abs(C59_new_f)
        magnitude_reverse = abs(C25_new_r) - abs(C59_new_r)
        dR_from_directed = 0.5 * (
            magnitude_forward + magnitude_reverse
        )
        linear_forward = linearized_magnitude_difference(
            C25_new_f, C59_new_f
        )
        linear_reverse = linearized_magnitude_difference(
            C25_new_r, C59_new_r
        )
        dR_linearized = 0.5 * (linear_forward + linear_reverse)

        source_norm = math.sqrt(abs(dz_f) ** 2 + abs(dz_r) ** 2)
        memory_norm = math.sqrt(abs(dC_old_f) ** 2 + abs(dC_old_r) ** 2)
        source_to_memory = (
            (1.0 - alpha) * source_norm
            / max(alpha * memory_norm, ZERO_TOL)
        )

        rows.append(
            {
                "step": step,
                "time": step * dt,
                "delta_operator": delta_from_K,
                "delta_from_proposal": delta_from_proposal,
                "delta_B": dB,
                "delta_R": dR,
                "delta_F": dF,
                "delta_x": dx,
                "weight_term": weight_term,
                "resonance_term": resonance_term,
                "resonance_to_weight_ratio": abs(resonance_term)
                / max(abs(weight_term), ZERO_TOL),
                "delta_B_next": dB_next,
                "q7": q7,
                "s7": s7,
                "dC_old_forward_real": float(np.real(dC_old_f)),
                "dC_old_forward_imag": float(np.imag(dC_old_f)),
                "dC_old_reverse_real": float(np.real(dC_old_r)),
                "dC_old_reverse_imag": float(np.imag(dC_old_r)),
                "dC_new_forward_abs": abs(dC_new_f),
                "dC_new_reverse_abs": abs(dC_new_r),
                "phase_source_forward_abs": abs(dz_f),
                "phase_source_reverse_abs": abs(dz_r),
                "source_to_memory_ratio": source_to_memory,
                "EMA_forward_identity_error": error_f,
                "EMA_reverse_identity_error": error_r,
                "proposal_identity_error": proposal_error[-1],
                "operator_delta_identity_error": delta_operator_error[-1],
                "projected_B_identity_error": projected_B_error[-1],
                "R_directed_reconstruction_error": abs(
                    dR - dR_from_directed
                ),
                "R_linearization_absolute_error": abs(
                    dR - dR_linearized
                ),
                "R_linearization_relative_error": abs(
                    dR - dR_linearized
                )
                / max(abs(dR), args.signal_floor),
                "complex_memory_norm": memory_norm,
                "phase_source_norm": source_norm,
            }
        )
        augmented.advance_base_state(state, intermediate)

    final_replay_exact = bool(np.array_equal(state.B, expected_final))
    trajectory = pd.DataFrame(rows)

    scalar_objects = {
        "delta_operator": trajectory["delta_operator"].to_numpy(float),
        "delta_x": trajectory["delta_x"].to_numpy(float),
        "delta_B": trajectory["delta_B"].to_numpy(float),
        "delta_R": trajectory["delta_R"].to_numpy(float),
        "complex_memory_norm": trajectory["complex_memory_norm"].to_numpy(float),
        "phase_source_norm": trajectory["phase_source_norm"].to_numpy(float),
    }
    recurrence = {
        name: scalar_recurrence(values, alpha, dt, args.signal_floor)
        for name, values in scalar_objects.items()
    }

    boundaries = np.asarray(args.intervals, dtype=float)
    if boundaries[0] > 0.0:
        boundaries = np.concatenate(([0.0], boundaries))
    if boundaries[-1] < (future_steps - 1) * dt:
        boundaries = np.concatenate(
            (boundaries, [(future_steps - 1) * dt])
        )
    boundaries = np.unique(boundaries)

    interval_rows: list[dict[str, Any]] = []
    for interval in range(len(boundaries) - 1):
        start = max(0, int(round(boundaries[interval] / dt)))
        end = min(
            future_steps - 1,
            int(round(boundaries[interval + 1] / dt)),
        )
        if end <= start + 2:
            continue
        for name, values in scalar_objects.items():
            fit = fit_log_rate(
                trajectory["time"].to_numpy(float)[start:end],
                values[start:end],
                args.signal_floor,
            )
            diagnostics = recurrence[name]
            multipliers = diagnostics["multiplier"][start:end]
            errors = diagnostics["relative_error"][start:end]
            rates = diagnostics["rate"][start:end]
            valid = np.isfinite(multipliers)
            source_ratio = trajectory["source_to_memory_ratio"].iloc[
                start:end
            ].to_numpy(float)
            interval_rows.append(
                {
                    "object": name,
                    "start_time": start * dt,
                    "end_time": end * dt,
                    **fit,
                    "rate_minus_EMA": fit["rate"] - ema_rate
                    if np.isfinite(fit["rate"])
                    else np.nan,
                    "median_multiplier": float(
                        np.median(multipliers[valid])
                    )
                    if np.any(valid)
                    else np.nan,
                    "median_multiplier_minus_alpha": float(
                        np.median(multipliers[valid]) - alpha
                    )
                    if np.any(valid)
                    else np.nan,
                    "median_ema_relative_error": float(
                        np.nanmedian(errors)
                    ),
                    "median_local_rate": float(np.nanmedian(rates)),
                    "sign_change_count": int(
                        np.sum(diagnostics["sign_change"][start:end])
                    ),
                    "median_source_to_memory_ratio": float(
                        np.nanmedian(source_ratio)
                    )
                    if name in {"complex_memory_norm", "phase_source_norm"}
                    else np.nan,
                }
            )
    interval_frame = pd.DataFrame(interval_rows)

    identity_frame = pd.DataFrame(
        [
            {
                "identity": "directed_complex_EMA_forward",
                "maximum_absolute_error": max(ema_forward_error),
                "median_absolute_error": float(np.median(ema_forward_error)),
            },
            {
                "identity": "directed_complex_EMA_reverse",
                "maximum_absolute_error": max(ema_reverse_error),
                "median_absolute_error": float(np.median(ema_reverse_error)),
            },
            {
                "identity": "proposal_difference",
                "maximum_absolute_error": max(proposal_error),
                "median_absolute_error": float(np.median(proposal_error)),
            },
            {
                "identity": "operator_delta_from_proposal",
                "maximum_absolute_error": max(delta_operator_error),
                "median_absolute_error": float(
                    np.median(delta_operator_error)
                ),
            },
            {
                "identity": "projected_B_difference",
                "maximum_absolute_error": max(projected_B_error),
                "median_absolute_error": float(np.median(projected_B_error)),
            },
            {
                "identity": "R_from_directed_magnitudes",
                "maximum_absolute_error": float(
                    trajectory["R_directed_reconstruction_error"].max()
                ),
                "median_absolute_error": float(
                    trajectory["R_directed_reconstruction_error"].median()
                ),
            },
        ]
    )

    component_audit.atomic_write_csv(
        output_dir / "defect_causal_trace_trajectory.csv", trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "defect_causal_trace_intervals.csv", interval_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "defect_causal_identity_checks.csv", identity_frame
    )

    report = make_report(
        interval_frame,
        identity_frame,
        alpha=alpha,
        ema_rate=ema_rate,
        final_replay_exact=final_replay_exact,
    )
    component_audit.atomic_write_text(
        output_dir / "defect_causal_ema_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 causal trace of K3 defect through EMA and proposals",
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
            "cocycle_npz": {
                "path": str(Path(args.cocycle_npz).resolve()),
                "sha256": file_sha256(args.cocycle_npz),
            },
        },
        "seed": args.seed,
        "dt": dt,
        "scale_epsilon": args.scale_epsilon,
        "intervals": boundaries.tolist(),
        "signal_floor": args.signal_floor,
        "alpha_EMA": alpha,
        "ema_rate": ema_rate,
        "final_replay_exact": final_replay_exact,
        "outputs": [
            "defect_causal_trace_trajectory.csv",
            "defect_causal_trace_intervals.csv",
            "defect_causal_identity_checks.csv",
            "defect_causal_ema_report.txt",
        ],
        "interpretation_constraints": [
            "Complex EMA differences are directed quantities; R is reconstructed only after magnitude and symmetrization.",
            "Magnitude linearization is approximate and separately audited.",
            "Shared pointwise multipliers do not alone establish causal direction.",
            "Results remain conditional on one seed and fixed winner branch.",
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
