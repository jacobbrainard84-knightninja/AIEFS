#!/usr/bin/env python3
"""Trace phase-source stabilization and alignment-law emergence in AIEF-1.4.

For each directed comparison between edges 25=(2,7) and 59=(7,11), define

    DeltaC_n = C_a,n - C_b,n,
    DeltaZ_n = z_a,n - z_b,n,
    E_n      = DeltaZ_n - DeltaC_n.

The exact EMA tracking-error recurrence is

    E_{n+1} = alpha E_n + (DeltaZ_{n+1}-DeltaZ_n).

The squared-magnitude alignment residual also has the exact decomposition

    2 DeltaA - DeltaM
      = 2 Re(conj(Cbar) (DeltaZ-DeltaC))
        + 2 Re(conj(DeltaC) Zbar).

This script verifies both identities, measures temporal stabilization of the
phase-source difference, separates tracking and tangential/mean-alignment
contributions to the radial law, and reports which term controls the emergence
of 2 DeltaA ~= DeltaM.
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
DEFAULT_OUTPUT_DIR = "aief_1_4_phase_source_locking"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_INTERVALS = "0,100,150,200,250,320"
DEFAULT_SIGNAL_FLOOR = 1e-15
DEFAULT_MIDPOINT_FLOOR = 1e-8
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


def complex_pair_geometry(
    C_a: complex,
    C_b: complex,
    Z_a: complex,
    Z_b: complex,
    midpoint_floor: float,
) -> dict[str, Any]:
    Cbar = 0.5 * (C_a + C_b)
    Zbar = 0.5 * (Z_a + Z_b)
    DeltaC = C_a - C_b
    DeltaZ = Z_a - Z_b
    tracking = DeltaZ - DeltaC
    DeltaM = float(abs(C_a) ** 2 - abs(C_b) ** 2)
    DeltaA = float(
        np.real(np.conj(C_a) * Z_a)
        - np.real(np.conj(C_b) * Z_b)
    )
    alignment_residual = 2.0 * DeltaA - DeltaM
    term_tracking = float(
        2.0 * np.real(np.conj(Cbar) * tracking)
    )
    term_tangential = float(
        2.0 * np.real(np.conj(DeltaC) * Zbar)
    )
    identity_error = abs(
        alignment_residual - term_tracking - term_tangential
    )

    Cbar_abs = abs(Cbar)
    Zbar_abs = abs(Zbar)
    reliable = Cbar_abs > midpoint_floor and Zbar_abs > midpoint_floor
    if Cbar_abs > midpoint_floor:
        rotated_C = np.conj(Cbar) * DeltaC / Cbar_abs
        radial = float(np.real(rotated_C))
        tangential = float(np.imag(rotated_C))
        radial_fraction = abs(radial) / max(abs(DeltaC), ZERO_TOL)
    else:
        radial = tangential = radial_fraction = np.nan
    if reliable:
        mean_alignment = float(
            np.real(np.conj(Cbar) * Zbar) / (Cbar_abs * Zbar_abs)
        )
        mean_alignment = float(np.clip(mean_alignment, -1.0, 1.0))
        mean_angle = float(
            np.angle(Zbar * np.conj(Cbar))
        )
    else:
        mean_alignment = mean_angle = np.nan

    return {
        "Cbar": Cbar,
        "Zbar": Zbar,
        "DeltaC": DeltaC,
        "DeltaZ": DeltaZ,
        "tracking": tracking,
        "DeltaM": DeltaM,
        "DeltaA": DeltaA,
        "alignment_residual": alignment_residual,
        "term_tracking": term_tracking,
        "term_tangential": term_tangential,
        "identity_error": identity_error,
        "Cbar_abs": Cbar_abs,
        "Zbar_abs": Zbar_abs,
        "midpoint_reliable": reliable,
        "radial": radial,
        "tangential": tangential,
        "radial_fraction": radial_fraction,
        "mean_alignment": mean_alignment,
        "mean_angle": mean_angle,
        "tracking_relative": abs(tracking) / max(abs(DeltaC), ZERO_TOL),
        "source_memory_norm_ratio": abs(DeltaZ) / max(abs(DeltaC), ZERO_TOL),
        "alignment_relative": abs(alignment_residual)
        / max(abs(DeltaM), ZERO_TOL),
        "tracking_term_fraction": abs(term_tracking)
        / max(abs(term_tracking) + abs(term_tangential), ZERO_TOL),
        "component_cancellation": abs(alignment_residual)
        / max(abs(term_tracking) + abs(term_tangential), ZERO_TOL),
    }


def make_report(
    identity_frame: pd.DataFrame,
    interval_frame: pd.DataFrame,
    *,
    alpha: float,
    ema_rate: float,
    final_replay_exact: bool,
) -> str:
    lines = [
        "AIEF K3 phase-source locking and alignment analysis",
        "===================================================",
        "",
        f"alpha_EMA: {alpha:.12g}",
        f"EMA rate: {ema_rate:.9g}",
        f"Final replay exact: {final_replay_exact}",
        "",
        "Exact identities",
        "----------------",
    ]
    for _, row in identity_frame.iterrows():
        lines.append(
            f"  {row['identity']}: max={row['maximum_absolute_error']:.6g}, "
            f"median={row['median_absolute_error']:.6g}"
        )

    lines.extend(["", "Interval source-locking diagnostics", "-----------------------------------"])
    for _, row in interval_frame.iterrows():
        lines.append(
            f"  channel={row['channel']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"tracking_rate={row['tracking_error_rate']:.6g}, "
            f"source_increment_rate={row['source_increment_rate']:.6g}, "
            f"tracking_relative={row['median_tracking_relative']:.3g}, "
            f"source_increment/tracking={row['median_source_increment_to_tracking']:.3g}, "
            f"mean_angle={row['median_abs_mean_angle']:.3g}, "
            f"radial_fraction={row['median_radial_fraction']:.3g}, "
            f"alignment_error={row['median_alignment_relative']:.3g}, "
            f"tracking_term_fraction={row['median_tracking_term_fraction']:.3g}, "
            f"component_cancellation={row['median_component_cancellation']:.3g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Tracking-error and alignment-residual decompositions are exact complex identities.",
            "* A small tracking error can result from temporal source stabilization; the source increment is measured directly.",
            "* Tangentialization and mean source-memory alignment are separate empirical conditions.",
            "* Cancellation between alignment-residual terms is reported explicitly.",
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
    per_channel: dict[str, list[dict[str, Any]]] = {
        channel: [] for channel in directed
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
            geometry = complex_pair_geometry(
                state.coherence_acc[index_a],
                state.coherence_acc[index_b],
                intermediate["phase_factor"][index_a],
                intermediate["phase_factor"][index_b],
                args.midpoint_floor,
            )
            per_channel[channel].append(
                {
                    "step": step,
                    "time": step * dt,
                    **geometry,
                }
            )
        if step < future_steps:
            augmented.advance_base_state(state, intermediate)

    final_replay_exact = bool(np.array_equal(state.B, expected_final))

    trajectory_rows: list[dict[str, Any]] = []
    identity_rows: list[dict[str, Any]] = []
    for channel, values in per_channel.items():
        count = len(values)
        tracking_identity_errors: list[float] = []
        alignment_identity_errors = [
            float(value["identity_error"]) for value in values
        ]
        for step, value in enumerate(values):
            row: dict[str, Any] = {
                "channel": channel,
                "step": step,
                "time": value["time"],
                "DeltaC_real": float(np.real(value["DeltaC"])),
                "DeltaC_imag": float(np.imag(value["DeltaC"])),
                "DeltaZ_real": float(np.real(value["DeltaZ"])),
                "DeltaZ_imag": float(np.imag(value["DeltaZ"])),
                "tracking_real": float(np.real(value["tracking"])),
                "tracking_imag": float(np.imag(value["tracking"])),
                "tracking_norm": abs(value["tracking"]),
                "DeltaC_norm": abs(value["DeltaC"]),
                "DeltaZ_norm": abs(value["DeltaZ"]),
                "tracking_relative": value["tracking_relative"],
                "source_memory_norm_ratio": value[
                    "source_memory_norm_ratio"
                ],
                "DeltaM": value["DeltaM"],
                "DeltaA": value["DeltaA"],
                "alignment_residual": value["alignment_residual"],
                "alignment_relative": value["alignment_relative"],
                "term_tracking": value["term_tracking"],
                "term_tangential": value["term_tangential"],
                "tracking_term_fraction": value[
                    "tracking_term_fraction"
                ],
                "component_cancellation": value[
                    "component_cancellation"
                ],
                "Cbar_abs": value["Cbar_abs"],
                "Zbar_abs": value["Zbar_abs"],
                "mean_alignment": value["mean_alignment"],
                "mean_angle": value["mean_angle"],
                "radial": value["radial"],
                "tangential": value["tangential"],
                "radial_fraction": value["radial_fraction"],
                "midpoint_reliable": value["midpoint_reliable"],
            }
            if step < count - 1:
                next_value = values[step + 1]
                source_increment = (
                    next_value["DeltaZ"] - value["DeltaZ"]
                )
                tracking_predicted = (
                    alpha * value["tracking"] + source_increment
                )
                tracking_error = (
                    next_value["tracking"] - tracking_predicted
                )
                tracking_identity_errors.append(abs(tracking_error))
                row.update(
                    {
                        "source_increment_real": float(
                            np.real(source_increment)
                        ),
                        "source_increment_imag": float(
                            np.imag(source_increment)
                        ),
                        "source_increment_norm": abs(source_increment),
                        "source_increment_to_tracking": abs(source_increment)
                        / max(abs(value["tracking"]), ZERO_TOL),
                        "tracking_recurrence_error": abs(tracking_error),
                        "DeltaZ_temporal_angle": float(
                            np.angle(
                                next_value["DeltaZ"]
                                * np.conj(value["DeltaZ"])
                            )
                        )
                        if abs(value["DeltaZ"]) > ZERO_TOL
                        and abs(next_value["DeltaZ"]) > ZERO_TOL
                        else np.nan,
                    }
                )
            else:
                row.update(
                    {
                        "source_increment_real": np.nan,
                        "source_increment_imag": np.nan,
                        "source_increment_norm": np.nan,
                        "source_increment_to_tracking": np.nan,
                        "tracking_recurrence_error": np.nan,
                        "DeltaZ_temporal_angle": np.nan,
                    }
                )
            trajectory_rows.append(row)

        identity_rows.extend(
            [
                {
                    "identity": f"tracking_recurrence_{channel}",
                    "maximum_absolute_error": float(
                        np.max(tracking_identity_errors)
                    ),
                    "median_absolute_error": float(
                        np.median(tracking_identity_errors)
                    ),
                },
                {
                    "identity": f"alignment_decomposition_{channel}",
                    "maximum_absolute_error": float(
                        np.max(alignment_identity_errors)
                    ),
                    "median_absolute_error": float(
                        np.median(alignment_identity_errors)
                    ),
                },
            ]
        )

    trajectory = pd.DataFrame(trajectory_rows)
    identity_frame = pd.DataFrame(identity_rows)

    boundaries = np.asarray(args.intervals, dtype=float)
    if boundaries[0] > 0.0:
        boundaries = np.concatenate(([0.0], boundaries))
    if boundaries[-1] < future_steps * dt:
        boundaries = np.concatenate((boundaries, [future_steps * dt]))
    boundaries = np.unique(boundaries)

    interval_rows: list[dict[str, Any]] = []
    for channel in directed:
        group = trajectory.loc[trajectory["channel"] == channel].reset_index(
            drop=True
        )
        for interval in range(len(boundaries) - 1):
            start = max(0, int(round(boundaries[interval] / dt)))
            end = min(
                len(group), int(round(boundaries[interval + 1] / dt))
            )
            if end <= start + 2:
                continue
            times = group["time"].to_numpy(float)[start:end]
            tracking_fit = fit_log_rate(
                times,
                group["tracking_norm"].to_numpy(float)[start:end],
                args.signal_floor,
            )
            source_increment_fit = fit_log_rate(
                times,
                group["source_increment_norm"].to_numpy(float)[start:end],
                args.signal_floor,
            )
            alignment_fit = fit_log_rate(
                times,
                group["alignment_residual"].to_numpy(float)[start:end],
                args.signal_floor,
            )
            radial_fit = fit_log_rate(
                times,
                group["radial"].to_numpy(float)[start:end],
                args.signal_floor,
            )
            reliable = group["midpoint_reliable"].iloc[start:end].to_numpy(
                bool
            )
            interval_rows.append(
                {
                    "channel": channel,
                    "start_time": start * dt,
                    "end_time": end * dt,
                    "tracking_error_rate": tracking_fit["rate"],
                    "tracking_error_R_squared": tracking_fit["R_squared"],
                    "source_increment_rate": source_increment_fit["rate"],
                    "source_increment_R_squared": source_increment_fit[
                        "R_squared"
                    ],
                    "alignment_residual_rate": alignment_fit["rate"],
                    "alignment_residual_R_squared": alignment_fit[
                        "R_squared"
                    ],
                    "radial_rate": radial_fit["rate"],
                    "radial_R_squared": radial_fit["R_squared"],
                    "median_tracking_relative": float(
                        group["tracking_relative"].iloc[start:end].median()
                    ),
                    "median_source_memory_norm_ratio": float(
                        group["source_memory_norm_ratio"].iloc[
                            start:end
                        ].median()
                    ),
                    "median_source_increment_to_tracking": float(
                        group["source_increment_to_tracking"].iloc[
                            start:end
                        ].median()
                    ),
                    "median_abs_source_temporal_angle": float(
                        group["DeltaZ_temporal_angle"].iloc[start:end].abs().median()
                    ),
                    "median_abs_mean_angle": float(
                        group["mean_angle"].iloc[start:end].abs().median()
                    ),
                    "median_mean_alignment_defect": float(
                        (1.0 - group["mean_alignment"].iloc[start:end]).median()
                    ),
                    "median_radial_fraction": float(
                        group["radial_fraction"].iloc[start:end].median()
                    ),
                    "median_alignment_relative": float(
                        group["alignment_relative"].iloc[start:end].median()
                    ),
                    "median_tracking_term_fraction": float(
                        group["tracking_term_fraction"].iloc[
                            start:end
                        ].median()
                    ),
                    "median_component_cancellation": float(
                        group["component_cancellation"].iloc[
                            start:end
                        ].median()
                    ),
                    "minimum_Cbar_abs": float(
                        group["Cbar_abs"].iloc[start:end].min()
                    ),
                    "minimum_Zbar_abs": float(
                        group["Zbar_abs"].iloc[start:end].min()
                    ),
                    "midpoint_unreliable_count": int(np.sum(~reliable)),
                }
            )
    interval_frame = pd.DataFrame(interval_rows)

    component_audit.atomic_write_csv(
        output_dir / "phase_source_locking_trajectory.csv", trajectory
    )
    component_audit.atomic_write_csv(
        output_dir / "phase_source_locking_intervals.csv", interval_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "phase_source_locking_identity_checks.csv", identity_frame
    )

    report = make_report(
        identity_frame,
        interval_frame,
        alpha=alpha,
        ema_rate=ema_rate,
        final_replay_exact=final_replay_exact,
    )
    component_audit.atomic_write_text(
        output_dir / "phase_source_locking_report.txt", report
    )

    manifest_output = {
        "analysis": "AIEF-1.4 phase-source stabilization and alignment-law decomposition",
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
            "phase_source_locking_trajectory.csv",
            "phase_source_locking_intervals.csv",
            "phase_source_locking_identity_checks.csv",
            "phase_source_locking_report.txt",
        ],
        "interpretation_constraints": [
            "Tracking and alignment decompositions are exact identities; stabilization and tangentialization are replay observations.",
            "Mean alignment and radial fractions are conditioned on nonzero complex midpoints.",
            "A shared asymptotic relation does not prove universal phase-locking causality.",
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
