#!/usr/bin/env python3
"""Test resonant EMA tracking, alignment cancellation, and angular freezing.

For each directed K3 edge comparison, define

    E_n = DeltaZ_n - DeltaC_n,
    S_n = DeltaZ_{n+1} - DeltaZ_n.

The exact recurrence is E_{n+1}=alpha E_n+S_n.  If S_n=B alpha^(n+1), then

    E_n=(A+B n) alpha^n.

This script fits that complex affine law, compares its slope B with
S_n/alpha^(n+1), estimates the limiting phase-source difference, tests whether
T1/T2 -> -1 in the alignment decomposition, and unwraps memory/source angular
separations while tracking radius-difference contraction.
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
DEFAULT_OUTPUT_DIR = "aief_1_4_resonant_tracking_angular"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_INTERVALS = "100,150,200,250,320"
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


def fit_complex_affine(
    indices: np.ndarray,
    values: np.ndarray,
) -> dict[str, Any]:
    """Fit complex Y=A+B*n using centered real design and complex targets."""
    indices = np.asarray(indices, dtype=float)
    values = np.asarray(values, dtype=complex)
    center = float(np.mean(indices))
    design = np.column_stack([np.ones(len(indices)), indices - center])
    coefficients, *_ = np.linalg.lstsq(design, values, rcond=None)
    A_center, B = coefficients
    A = A_center - B * center
    prediction = A + B * indices
    residual_norm = float(np.linalg.norm(values - prediction))
    total_norm = float(np.linalg.norm(values - np.mean(values)))
    return {
        "A": complex(A),
        "B": complex(B),
        "prediction": prediction,
        "relative_RMSE": residual_norm / max(float(np.linalg.norm(values)), ZERO_TOL),
        "R_squared": 1.0 - residual_norm**2 / max(total_norm**2, ZERO_TOL),
    }


def fit_real_affine(
    indices: np.ndarray,
    values: np.ndarray,
) -> dict[str, Any]:
    result = fit_complex_affine(indices, np.asarray(values, dtype=float).astype(complex))
    return {
        "A": float(np.real(result["A"])),
        "B": float(np.real(result["B"])),
        "prediction": np.real(result["prediction"]),
        "relative_RMSE": result["relative_RMSE"],
        "R_squared": result["R_squared"],
    }


def fit_log_rate(times: np.ndarray, values: np.ndarray, floor: float) -> dict[str, float]:
    magnitudes = np.abs(np.asarray(values, dtype=float))
    valid = np.isfinite(magnitudes) & (magnitudes > floor)
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


def channel_quantities(
    C_a: complex,
    C_b: complex,
    Z_a: complex,
    Z_b: complex,
) -> dict[str, Any]:
    Cbar = 0.5 * (C_a + C_b)
    Zbar = 0.5 * (Z_a + Z_b)
    DeltaC = C_a - C_b
    DeltaZ = Z_a - Z_b
    E = DeltaZ - DeltaC
    DeltaM = float(abs(C_a) ** 2 - abs(C_b) ** 2)
    DeltaA = float(
        np.real(np.conj(C_a) * Z_a)
        - np.real(np.conj(C_b) * Z_b)
    )
    T1 = float(2.0 * np.real(np.conj(Cbar) * E))
    T2 = float(2.0 * np.real(np.conj(DeltaC) * Zbar))
    return {
        "Cbar": Cbar,
        "Zbar": Zbar,
        "DeltaC": DeltaC,
        "DeltaZ": DeltaZ,
        "E": E,
        "DeltaM": DeltaM,
        "DeltaA": DeltaA,
        "T1": T1,
        "T2": T2,
        "alignment_residual": 2.0 * DeltaA - DeltaM,
        "radius_difference": float(abs(C_a) - abs(C_b)),
        "memory_phase_raw": float(np.angle(C_a * np.conj(C_b))),
        "source_phase_raw": float(np.angle(Z_a * np.conj(Z_b))),
    }


def make_report(
    resonant_frame: pd.DataFrame,
    alignment_frame: pd.DataFrame,
    angular_frame: pd.DataFrame,
    *,
    alpha: float,
    ema_rate: float,
    final_replay_exact: bool,
) -> str:
    lines = [
        "AIEF resonant tracking and angular-freezing analysis",
        "====================================================",
        "",
        f"alpha_EMA: {alpha:.12g}",
        f"EMA rate: {ema_rate:.9g}",
        f"Final replay exact: {final_replay_exact}",
        "",
        "Resonant tracking fits",
        "----------------------",
    ]
    for _, row in resonant_frame.iterrows():
        lines.append(
            f"  channel={row['channel']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"Y_affine_R2={row['Y_affine_R_squared']:.6g}, "
            f"Y_RMSE={row['Y_affine_relative_RMSE']:.3g}, "
            f"B={row['B_real']:.6g}+{row['B_imag']:.6g}i, "
            f"Q_match={row['Q_minus_B_relative']:.3g}, "
            f"limit_spread={row['source_limit_relative_spread']:.3g}, "
            f"median_n_forcing_ratio={row['median_n_forcing_ratio']:.6g}"
        )

    lines.extend(["", "Alignment-component asymptotics", "-------------------------------"])
    for _, row in alignment_frame.iterrows():
        lines.append(
            f"  channel={row['channel']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"median_T1/T2={row['median_T1_over_T2']:.9g}, "
            f"p95_|ratio+1|={row['p95_ratio_plus_one_abs']:.3g}, "
            f"T1_rate={row['T1_rate']:.6g}, T2_rate={row['T2_rate']:.6g}, "
            f"scaled_affine_R2_T1={row['T1_scaled_affine_R_squared']:.6g}, "
            f"scaled_affine_R2_T2={row['T2_scaled_affine_R_squared']:.6g}"
        )

    lines.extend(["", "Angular and radial freezing", "---------------------------"])
    for _, row in angular_frame.iterrows():
        lines.append(
            f"  channel={row['channel']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"memory_phase_increment={row['median_abs_memory_phase_increment']:.3g}, "
            f"source_phase_increment={row['median_abs_source_phase_increment']:.3g}, "
            f"source-memory_phase_gap={row['median_abs_phase_gap']:.3g}, "
            f"radius_rate={row['radius_difference_rate']:.6g}, "
            f"radius_R2={row['radius_difference_R_squared']:.6g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* The resonant form is tested in complex coordinates; norm-only fits are insufficient.",
            "* A good affine Y=E/alpha^n fit and Q=S/alpha^(n+1) match support resonant forcing but remain finite-horizon evidence.",
            "* T1/T2 -> -1 establishes cancellation; it does not imply either term is independently negligible.",
            "* Phase separations are unwrapped replay observables, not invariant-manifold proofs.",
            "* Results remain conditional on one replay and fixed branch.",
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
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.dt, args.scale_epsilon, args.signal_floor) <= 0.0:
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
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(int(model["N"]), capacity)
    A, edges = base.incidence_matrix(int(model["N"]))
    future_steps = int(manifest["protocol"]["future_steps"])

    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
        expected_final = np.asarray(
            data[base.branch_key("continue", args.seed, "B_final")], dtype=float
        ).copy()

    directed = {
        "forward": ((2, 7), (7, 11)),
        "reverse": ((7, 2), (11, 7)),
    }
    channel_data: dict[str, dict[str, np.ndarray]] = {}
    raw_lists: dict[str, dict[str, list[Any]]] = {
        channel: {
            "DeltaC": [],
            "DeltaZ": [],
            "E": [],
            "T1": [],
            "T2": [],
            "alignment_residual": [],
            "radius_difference": [],
            "memory_phase_raw": [],
            "source_phase_raw": [],
        }
        for channel in directed
    }

    for step in range(future_steps + 1):
        intermediate = augmented.base_intermediates(
            state,
            model,
            capacities,
            A,
            edges,
            args.scale_epsilon,
        )
        for channel, (index_a, index_b) in directed.items():
            values = channel_quantities(
                state.coherence_acc[index_a],
                state.coherence_acc[index_b],
                intermediate["phase_factor"][index_a],
                intermediate["phase_factor"][index_b],
            )
            for key in raw_lists[channel]:
                raw_lists[channel][key].append(values[key])
        if step < future_steps:
            augmented.advance_base_state(state, intermediate)

    final_replay_exact = bool(np.array_equal(state.B, expected_final))
    alpha_powers = alpha ** np.arange(future_steps + 1)

    for channel, values in raw_lists.items():
        data_dict: dict[str, np.ndarray] = {}
        for key, sequence in values.items():
            dtype = complex if key in {"DeltaC", "DeltaZ", "E"} else float
            data_dict[key] = np.asarray(sequence, dtype=dtype)
        data_dict["S"] = np.diff(data_dict["DeltaZ"])
        data_dict["memory_phase"] = np.unwrap(data_dict["memory_phase_raw"])
        data_dict["source_phase"] = np.unwrap(data_dict["source_phase_raw"])
        data_dict["phase_gap"] = np.unwrap(
            data_dict["source_phase_raw"] - data_dict["memory_phase_raw"]
        )
        data_dict["memory_phase_increment"] = np.diff(
            data_dict["memory_phase"]
        )
        data_dict["source_phase_increment"] = np.diff(
            data_dict["source_phase"]
        )
        data_dict["Y"] = data_dict["E"] / alpha_powers
        data_dict["Q"] = data_dict["S"] / alpha_powers[1:]
        data_dict["T1_scaled"] = data_dict["T1"] / alpha_powers
        data_dict["T2_scaled"] = data_dict["T2"] / alpha_powers
        channel_data[channel] = data_dict

    boundaries = np.asarray(args.intervals, dtype=float)
    if boundaries[0] > 0.0:
        boundaries = np.concatenate(([0.0], boundaries))
    if boundaries[-1] < future_steps * dt:
        boundaries = np.concatenate((boundaries, [future_steps * dt]))
    boundaries = np.unique(boundaries)

    resonant_rows: list[dict[str, Any]] = []
    alignment_rows: list[dict[str, Any]] = []
    angular_rows: list[dict[str, Any]] = []
    trajectory_rows: list[dict[str, Any]] = []

    for channel, values in channel_data.items():
        for step in range(future_steps + 1):
            row = {
                "channel": channel,
                "step": step,
                "time": step * dt,
                "DeltaC_real": float(np.real(values["DeltaC"][step])),
                "DeltaC_imag": float(np.imag(values["DeltaC"][step])),
                "DeltaZ_real": float(np.real(values["DeltaZ"][step])),
                "DeltaZ_imag": float(np.imag(values["DeltaZ"][step])),
                "E_real": float(np.real(values["E"][step])),
                "E_imag": float(np.imag(values["E"][step])),
                "E_norm": float(abs(values["E"][step])),
                "Y_real": float(np.real(values["Y"][step])),
                "Y_imag": float(np.imag(values["Y"][step])),
                "T1": float(values["T1"][step]),
                "T2": float(values["T2"][step]),
                "T1_over_T2": float(values["T1"][step] / values["T2"][step])
                if abs(values["T2"][step]) > args.signal_floor
                else np.nan,
                "alignment_residual": float(values["alignment_residual"][step]),
                "radius_difference": float(values["radius_difference"][step]),
                "memory_phase": float(values["memory_phase"][step]),
                "source_phase": float(values["source_phase"][step]),
                "phase_gap": float(values["phase_gap"][step]),
            }
            if step < future_steps:
                row.update(
                    {
                        "S_real": float(np.real(values["S"][step])),
                        "S_imag": float(np.imag(values["S"][step])),
                        "S_norm": float(abs(values["S"][step])),
                        "Q_real": float(np.real(values["Q"][step])),
                        "Q_imag": float(np.imag(values["Q"][step])),
                        "memory_phase_increment": float(
                            values["memory_phase_increment"][step]
                        ),
                        "source_phase_increment": float(
                            values["source_phase_increment"][step]
                        ),
                        "n_forcing_ratio": float(
                            step
                            * abs(values["S"][step])
                            / max(
                                (1.0 - alpha) * abs(values["E"][step]),
                                ZERO_TOL,
                            )
                        ),
                    }
                )
            else:
                row.update(
                    {
                        "S_real": np.nan,
                        "S_imag": np.nan,
                        "S_norm": np.nan,
                        "Q_real": np.nan,
                        "Q_imag": np.nan,
                        "memory_phase_increment": np.nan,
                        "source_phase_increment": np.nan,
                        "n_forcing_ratio": np.nan,
                    }
                )
            trajectory_rows.append(row)

        for interval in range(len(boundaries) - 1):
            start = max(0, int(round(boundaries[interval] / dt)))
            end = min(
                future_steps + 1,
                int(round(boundaries[interval + 1] / dt)),
            )
            if end <= start + 2:
                continue
            indices = np.arange(start, end, dtype=float)
            Y_fit = fit_complex_affine(indices, values["Y"][start:end])
            B = Y_fit["B"]
            q_start = start
            q_end = min(end - 1, future_steps)
            Q_values = values["Q"][q_start:q_end]
            if len(Q_values):
                Q_minus_B_relative = float(
                    np.linalg.norm(Q_values - B)
                    / max(np.linalg.norm(Q_values), ZERO_TOL)
                )
            else:
                Q_minus_B_relative = np.nan
            # Each late sample gives an estimate of the limiting source.
            source_limit_estimates = (
                values["DeltaZ"][start:end]
                + B
                * alpha_powers[start:end]
                * alpha
                / (1.0 - alpha)
            )
            source_limit_mean = np.mean(source_limit_estimates)
            source_limit_spread = float(
                np.linalg.norm(
                    source_limit_estimates - source_limit_mean
                )
                / max(
                    math.sqrt(len(source_limit_estimates))
                    * abs(source_limit_mean),
                    ZERO_TOL,
                )
            )
            n_forcing = (
                indices[:-1]
                * np.abs(values["S"][start : end - 1])
                / np.maximum(
                    (1.0 - alpha)
                    * np.abs(values["E"][start : end - 1]),
                    ZERO_TOL,
                )
            )
            resonant_rows.append(
                {
                    "channel": channel,
                    "start_time": start * dt,
                    "end_time": (end - 1) * dt,
                    "sample_count": int(end - start),
                    "A_real": float(np.real(Y_fit["A"])),
                    "A_imag": float(np.imag(Y_fit["A"])),
                    "B_real": float(np.real(B)),
                    "B_imag": float(np.imag(B)),
                    "Y_affine_relative_RMSE": Y_fit["relative_RMSE"],
                    "Y_affine_R_squared": Y_fit["R_squared"],
                    "Q_minus_B_relative": Q_minus_B_relative,
                    "source_limit_real": float(np.real(source_limit_mean)),
                    "source_limit_imag": float(np.imag(source_limit_mean)),
                    "source_limit_relative_spread": source_limit_spread,
                    "median_n_forcing_ratio": float(np.median(n_forcing))
                    if len(n_forcing)
                    else np.nan,
                }
            )

            T1 = values["T1"][start:end]
            T2 = values["T2"][start:end]
            valid_ratio = np.abs(T2) > args.signal_floor
            ratios = T1[valid_ratio] / T2[valid_ratio]
            T1_fit = fit_log_rate(
                np.arange(start, end) * dt,
                T1,
                args.signal_floor,
            )
            T2_fit = fit_log_rate(
                np.arange(start, end) * dt,
                T2,
                args.signal_floor,
            )
            T1_scaled_fit = fit_real_affine(
                indices, values["T1_scaled"][start:end]
            )
            T2_scaled_fit = fit_real_affine(
                indices, values["T2_scaled"][start:end]
            )
            alignment_rows.append(
                {
                    "channel": channel,
                    "start_time": start * dt,
                    "end_time": (end - 1) * dt,
                    "median_T1_over_T2": float(np.median(ratios))
                    if len(ratios)
                    else np.nan,
                    "p95_ratio_plus_one_abs": float(
                        np.quantile(np.abs(ratios + 1.0), 0.95)
                    )
                    if len(ratios)
                    else np.nan,
                    "T1_rate": T1_fit["rate"],
                    "T1_R_squared": T1_fit["R_squared"],
                    "T2_rate": T2_fit["rate"],
                    "T2_R_squared": T2_fit["R_squared"],
                    "T1_scaled_affine_R_squared": T1_scaled_fit[
                        "R_squared"
                    ],
                    "T1_scaled_affine_RMSE": T1_scaled_fit[
                        "relative_RMSE"
                    ],
                    "T2_scaled_affine_R_squared": T2_scaled_fit[
                        "R_squared"
                    ],
                    "T2_scaled_affine_RMSE": T2_scaled_fit[
                        "relative_RMSE"
                    ],
                }
            )

            memory_increment = values["memory_phase_increment"][
                start : min(end, future_steps)
            ]
            source_increment = values["source_phase_increment"][
                start : min(end, future_steps)
            ]
            radius_fit = fit_log_rate(
                np.arange(start, end) * dt,
                values["radius_difference"][start:end],
                args.signal_floor,
            )
            angular_rows.append(
                {
                    "channel": channel,
                    "start_time": start * dt,
                    "end_time": (end - 1) * dt,
                    "median_abs_memory_phase_increment": float(
                        np.median(np.abs(memory_increment))
                    ),
                    "median_abs_source_phase_increment": float(
                        np.median(np.abs(source_increment))
                    ),
                    "median_abs_phase_gap": float(
                        np.median(np.abs(values["phase_gap"][start:end]))
                    ),
                    "memory_phase_start": float(
                        values["memory_phase"][start]
                    ),
                    "memory_phase_end": float(
                        values["memory_phase"][end - 1]
                    ),
                    "source_phase_start": float(
                        values["source_phase"][start]
                    ),
                    "source_phase_end": float(
                        values["source_phase"][end - 1]
                    ),
                    "radius_difference_rate": radius_fit["rate"],
                    "radius_difference_R_squared": radius_fit[
                        "R_squared"
                    ],
                }
            )

    trajectory = pd.DataFrame(trajectory_rows)
    resonant_frame = pd.DataFrame(resonant_rows)
    alignment_frame = pd.DataFrame(alignment_rows)
    angular_frame = pd.DataFrame(angular_rows)

    identity_frame = pd.DataFrame(
        [
            {
                "identity": "tracking_recurrence",
                "maximum_absolute_error": float(
                    trajectory["tracking_recurrence_error"].max()
                ),
                "median_absolute_error": float(
                    trajectory["tracking_recurrence_error"].median()
                ),
            },
            {
                "identity": "alignment_decomposition",
                "maximum_absolute_error": float(
                    max(
                        abs(
                            trajectory["alignment_residual"]
                            - trajectory["T1"]
                            - trajectory["T2"]
                        )
                    )
                ),
                "median_absolute_error": float(
                    np.median(
                        abs(
                            trajectory["alignment_residual"]
                            - trajectory["T1"]
                            - trajectory["T2"]
                        )
                    )
                ),
            },
        ]
    )

    component_audit.atomic_write_csv(
        output_dir / "resonant_tracking_trajectory.csv", trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "resonant_tracking_fit_summary.csv", resonant_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "alignment_component_asymptotics.csv", alignment_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "angular_radius_summary.csv", angular_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "resonant_tracking_identity_checks.csv", identity_frame
    )

    report = make_report(
        resonant_frame,
        alignment_frame,
        angular_frame,
        alpha=alpha,
        ema_rate=ema_rate,
        final_replay_exact=final_replay_exact,
    )
    component_audit.atomic_write_text(
        output_dir / "resonant_tracking_angular_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 resonant EMA tracking and angular freezing",
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
        "final_replay_exact": final_replay_exact,
        "outputs": [
            "resonant_tracking_trajectory.csv",
            "resonant_tracking_fit_summary.csv",
            "alignment_component_asymptotics.csv",
            "angular_radius_summary.csv",
            "resonant_tracking_identity_checks.csv",
            "resonant_tracking_angular_report.txt",
        ],
        "interpretation_constraints": [
            "Resonant tracking is tested in complex coordinates, not inferred from norm rates alone.",
            "T1/T2 cancellation and independent term decay are reported separately.",
            "Unwrapped angular convergence is a replay observation, not an invariant-manifold theorem.",
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
