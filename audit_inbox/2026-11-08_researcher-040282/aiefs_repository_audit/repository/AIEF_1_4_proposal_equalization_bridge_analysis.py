#!/usr/bin/env python3
"""Audit the conditional K3 proposal-equalization bridge on the frozen replay.

This analysis checks two distinct exceptional-K3 channels:

    fixed_left:  x25 - x59  -> beta25-beta59 -> fixed-left defect
    right_mode:  x59 - x29  -> s2-s7         -> right-invariance defect

On the isolated fixed branch it validates the exact recurrences

    dx_next = lambda_step * dx + dt*(eta+mu)*dR_next,

with separate projection coefficients for the two channels.  It also extends
the directed squared-magnitude/alignment audit to both edge pairs (25,59) and
(59,29), including the previously less-developed right-mode pair.

No trajectory is regenerated with changed dynamics.  The script replays the
existing frozen split state under the unchanged production step.  Use
--self-test for synthetic algebra checks that require no run artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_augmented_tangent_cocycle_analysis as augmented


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_proposal_equalization_bridge"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_INTERVALS = "0,100,150,200,250,320"
DEFAULT_SIGNAL_FLOOR = 1e-15

EDGE_25 = 25
EDGE_29 = 29
EDGE_59 = 59
NODE_2 = 2
NODE_7 = 7
ZERO_TOL = 1e-300

PAIR_DEFINITIONS = {
    "fixed_left": (EDGE_25, EDGE_59),
    "right_mode": (EDGE_59, EDGE_29),
}
EXPECTED_WINNERS = {
    EDGE_25: NODE_7,
    EDGE_29: NODE_2,
    EDGE_59: NODE_7,
}


def sha256(path: str | os.PathLike[str]) -> str:
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
    if len(values) < 2 or any(value < 0.0 for value in values):
        raise argparse.ArgumentTypeError("need at least two nonnegative values")
    values = sorted(set(values))
    if len(values) < 2:
        raise argparse.ArgumentTypeError("need at least two distinct values")
    return values


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def atomic_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            frame.to_csv(handle, index=False, quoting=csv.QUOTE_MINIMAL)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def fit_log_rate(times: np.ndarray, values: np.ndarray, floor: float) -> dict[str, float]:
    magnitudes = np.abs(np.asarray(values, dtype=float))
    times = np.asarray(times, dtype=float)
    valid = np.isfinite(magnitudes) & np.isfinite(times) & (magnitudes > floor)
    if int(np.sum(valid)) < 3:
        return {"count": int(np.sum(valid)), "rate": np.nan, "R_squared": np.nan}
    x = times[valid]
    y = np.log(magnitudes[valid])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "count": int(len(x)),
        "rate": float(-slope),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
    }


def directed_radial_metrics(
    C_a: complex,
    C_b: complex,
    z_a: complex,
    z_b: complex,
    C_a_next: complex,
    C_b_next: complex,
    alpha: float,
) -> dict[str, float]:
    M_a = abs(C_a) ** 2
    M_b = abs(C_b) ** 2
    M_a_next = abs(C_a_next) ** 2
    M_b_next = abs(C_b_next) ** 2
    A_a = float(np.real(np.conj(C_a) * z_a))
    A_b = float(np.real(np.conj(C_b) * z_b))
    delta_M = float(M_a - M_b)
    delta_M_next = float(M_a_next - M_b_next)
    delta_A = float(A_a - A_b)
    alignment_residual = float(2.0 * delta_A - delta_M)
    predicted_next = float(
        alpha * delta_M + alpha * (1.0 - alpha) * alignment_residual
    )
    denominator_next = float(abs(C_a_next) + abs(C_b_next))
    magnitude_difference_next = float(abs(C_a_next) - abs(C_b_next))
    quotient = float(delta_M_next / max(denominator_next, ZERO_TOL))
    return {
        "delta_M": delta_M,
        "delta_M_next": delta_M_next,
        "delta_A": delta_A,
        "alignment_residual": alignment_residual,
        "radial_recurrence_error": abs(delta_M_next - predicted_next),
        "magnitude_denominator_next": denominator_next,
        "magnitude_difference_next": magnitude_difference_next,
        "magnitude_quotient_error": abs(magnitude_difference_next - quotient),
    }


def right_projection_coefficient(
    x25: float,
    x29: float,
    x59: float,
    capacity: float,
    epsilon: float,
) -> float:
    q2 = x25 + x29
    q7 = x25 + x59
    return float(
        capacity
        * (x25 + epsilon)
        / ((q7 + epsilon) * (q2 + epsilon))
    )


def synthetic_self_test() -> None:
    rng = np.random.default_rng(20260727)
    capacity = 0.6333333333333333
    epsilon = 1e-12
    dt = 0.01
    gamma = 0.015
    eta = 0.04
    mu = 0.03
    c0 = 1.0 - gamma * dt
    a_R = dt * (eta + mu)

    # Positive isolated K3 proposal with both controller rows clipped.
    x25, x29, x59 = 0.41, 0.31, 0.27
    q2 = x25 + x29
    q7 = x25 + x59
    s2 = capacity / (q2 + epsilon)
    s7 = capacity / (q7 + epsilon)
    projected = {
        EDGE_25: s7 * x25,
        EDGE_29: s2 * x29,
        EDGE_59: s7 * x59,
    }
    d_left = x25 - x59
    d_right = x59 - x29
    sigma_right = right_projection_coefficient(
        x25, x29, x59, capacity, epsilon
    )
    assert abs(
        (projected[EDGE_25] - projected[EDGE_59]) - s7 * d_left
    ) < 1e-14
    assert abs(
        (projected[EDGE_59] - projected[EDGE_29]) - sigma_right * d_right
    ) < 1e-14
    assert 0.0 < s7 < 1.0
    assert 0.0 < sigma_right < 1.0

    # Exact proposal difference identity.
    B = rng.uniform(0.1, 0.4, size=3)
    R = rng.uniform(0.2, 0.9, size=3)
    x = c0 * B + a_R * R - dt * mu
    for ia, ib in ((0, 2), (2, 1)):
        assert abs(
            (x[ia] - x[ib])
            - (c0 * (B[ia] - B[ib]) + a_R * (R[ia] - R[ib]))
        ) < 1e-15

    # Directed radial recurrence and quotient identity.
    alpha = 0.999428829846
    for _ in range(100):
        C_a = rng.normal() + 1j * rng.normal()
        C_b = rng.normal() + 1j * rng.normal()
        z_a = np.exp(1j * rng.uniform(-math.pi, math.pi))
        z_b = np.exp(1j * rng.uniform(-math.pi, math.pi))
        C_a_next = alpha * C_a + (1.0 - alpha) * z_a
        C_b_next = alpha * C_b + (1.0 - alpha) * z_b
        metrics = directed_radial_metrics(
            C_a, C_b, z_a, z_b, C_a_next, C_b_next, alpha
        )
        assert metrics["radial_recurrence_error"] < 5e-15
        assert metrics["magnitude_quotient_error"] < 5e-15

    # Stable forced recurrence with vanishing input.
    value = 1.0
    for n in range(20000):
        forcing = 0.05 * (0.999 ** (n + 1))
        value = 0.9987 * value + forcing
    assert abs(value) < 1e-6
    print("Synthetic proposal-equalization bridge checks: PASS")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", default=DEFAULT_SEED)
    parser.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    parser.add_argument(
        "--intervals",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_INTERVALS),
    )
    parser.add_argument("--signal-floor", type=float, default=DEFAULT_SIGNAL_FLOOR)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run deterministic synthetic algebra checks without loading replay artifacts",
    )
    return parser.parse_args()


def make_report(
    trajectory: pd.DataFrame,
    intervals: pd.DataFrame,
    identities: pd.DataFrame,
    *,
    final_replay_exact: bool,
    alpha: float,
    c0: float,
) -> str:
    lines = [
        "AIEF K3 proposal-equalization bridge analysis",
        "=============================================",
        "",
        f"final replay exact: {final_replay_exact}",
        f"alpha_EMA: {alpha:.12g}",
        f"c0=1-gamma*dt: {c0:.12g}",
        f"trajectory rows: {len(trajectory)}",
        "",
        "Exact identity errors",
        "---------------------",
    ]
    for _, row in identities.iterrows():
        lines.append(
            f"  pair={row['pair']}, identity={row['identity']}: "
            f"max={row['maximum_absolute_error']:.6g}, "
            f"median={row['median_absolute_error']:.6g}"
        )

    lines.extend(["", "Branch checks", "-------------"])
    for pair, group in trajectory.groupby("pair", sort=False):
        lines.append(
            f"  {pair}: gate_all={bool(group['gate_on'].all())}, "
            f"positive_all={bool(group['selected_positive'].all())}, "
            f"controllers_clipped_all={bool(group['controllers_clipped'].all())}, "
            f"winner_map_all={bool(group['winner_map_expected'].all())}, "
            f"isolation_max={group['isolation_error'].max():.3g}, "
            f"min_winner_margin={group['minimum_winner_margin'].min():.3g}, "
            f"max_lambda={group['lambda_step'].max():.12g}"
        )

    lines.extend(["", "Interval dynamics", "-----------------"])
    for _, row in intervals.iterrows():
        lines.append(
            f"  pair={row['pair']}, interval=[{row['start_time']:.6g},{row['end_time']:.6g}): "
            f"dx_rate={row['dx_rate']:.6g}, dR_rate={row['dR_rate']:.6g}, "
            f"align_f_rate={row['alignment_forward_rate']:.6g}, "
            f"align_r_rate={row['alignment_reverse_rate']:.6g}, "
            f"dx_R2={row['dx_R_squared']:.6g}, "
            f"dR_R2={row['dR_R_squared']:.6g}, "
            f"median_lambda={row['median_lambda_step']:.12g}, "
            f"min_denominator={row['minimum_magnitude_denominator']:.6g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Proposal, projection, recurrence, radial, magnitude-quotient, and symmetrization identities are exact implementation checks.",
            "* The two edge pairs carry different operator defects and are not interchangeable.",
            "* Stable downstream recurrences prove proposal equalization only if the corresponding resonance differences converge to zero.",
            "* Alignment-residual and rate fits are finite-horizon replay evidence, not infinite-time limits.",
            "* Branch checks over the saved replay do not prove future branch persistence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_arguments()
    if args.self_test:
        synthetic_self_test()
        return
    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.scale_epsilon, args.signal_floor) <= 0.0:
        raise ValueError("scale epsilon and signal floor must be positive")
    if args.scale_epsilon != DEFAULT_SCALE_EPSILON:
        raise ValueError("implemented actual step uses fixed scale epsilon=1e-12")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = manifest["model"]
    node_count = int(model["N"])
    dt = float(model["dt"])
    gamma = float(model["gamma"])
    eta = float(model["eta"])
    mu = float(model["mu"])
    alpha = float(np.exp(-dt / float(model["T_window"])))
    c0 = 1.0 - gamma * dt
    a_R = dt * (eta + mu)
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(node_count, capacity)
    A, edges = base.incidence_matrix(node_count)
    edge_i, edge_j = edges
    expected_edges = {
        EDGE_25: (2, 7),
        EDGE_29: (2, 11),
        EDGE_59: (7, 11),
    }
    for edge, expected in expected_edges.items():
        observed = (int(edge_i[edge]), int(edge_j[edge]))
        if observed != expected:
            raise RuntimeError(f"edge {edge} mapping {observed} != {expected}")

    future_steps = int(manifest["protocol"]["future_steps"])
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
        expected_final = np.asarray(
            data[base.branch_key("continue", args.seed, "B_final")], dtype=float
        ).copy()

    rows: list[dict[str, Any]] = []
    for step in range(future_steps):
        intermediate = augmented.base_intermediates(
            state,
            model,
            capacities,
            A,
            edges,
            args.scale_epsilon,
        )
        B_edges = state.B[edges]
        R_edges = intermediate["R"][edges]
        x = intermediate["x"]
        B_next_edges = intermediate["projected"][edges]
        q2 = float(intermediate["q_scale"][NODE_2])
        q7 = float(intermediate["q_scale"][NODE_7])
        x25 = float(x[EDGE_25])
        x29 = float(x[EDGE_29])
        x59 = float(x[EDGE_59])
        isolation_error = max(
            abs(q2 - (x25 + x29)),
            abs(q7 - (x25 + x59)),
        )
        winner_expected = all(
            int(intermediate["winner_code"][edge]) == winner
            for edge, winner in EXPECTED_WINNERS.items()
        )
        selected_positive = bool(
            min(x25, x29, x59) > 0.0
        )
        minimum_winner_margin = float(
            min(intermediate["winner_margin"][edge] for edge in EXPECTED_WINNERS)
        )
        controllers_clipped = bool(
            intermediate["clipped"][NODE_2]
            and intermediate["clipped"][NODE_7]
        )

        for pair, (edge_a, edge_b) in PAIR_DEFINITIONS.items():
            dB = float(B_edges[edge_a] - B_edges[edge_b])
            dR = float(R_edges[edge_a] - R_edges[edge_b])
            dx = float(x[edge_a] - x[edge_b])
            proposal_prediction = c0 * dB + a_R * dR
            dB_next = float(B_next_edges[edge_a] - B_next_edges[edge_b])
            if pair == "fixed_left":
                sigma = float(intermediate["scales"][NODE_7])
            else:
                sigma = right_projection_coefficient(
                    x25, x29, x59, capacity, args.scale_epsilon
                )
            projection_prediction = sigma * dx

            directed_metrics: dict[str, dict[str, float]] = {}
            for orientation in ("forward", "reverse"):
                if orientation == "forward":
                    index_a = (int(edge_i[edge_a]), int(edge_j[edge_a]))
                    index_b = (int(edge_i[edge_b]), int(edge_j[edge_b]))
                else:
                    index_a = (int(edge_j[edge_a]), int(edge_i[edge_a]))
                    index_b = (int(edge_j[edge_b]), int(edge_i[edge_b]))
                directed_metrics[orientation] = directed_radial_metrics(
                    state.coherence_acc[index_a],
                    state.coherence_acc[index_b],
                    intermediate["phase_factor"][index_a],
                    intermediate["phase_factor"][index_b],
                    intermediate["updated_coherence"][index_a],
                    intermediate["updated_coherence"][index_b],
                    alpha,
                )
            dR_from_directed = 0.5 * (
                directed_metrics["forward"]["magnitude_difference_next"]
                + directed_metrics["reverse"]["magnitude_difference_next"]
            )

            row: dict[str, Any] = {
                "step": step,
                "time": step * dt,
                "pair": pair,
                "edge_a": edge_a,
                "edge_b": edge_b,
                "delta_B": dB,
                "delta_R": dR,
                "delta_x": dx,
                "delta_B_next": dB_next,
                "proposal_prediction": proposal_prediction,
                "proposal_identity_error": abs(dx - proposal_prediction),
                "sigma_projection": sigma,
                "lambda_step": c0 * sigma,
                "projection_prediction": projection_prediction,
                "projection_identity_error": abs(dB_next - projection_prediction),
                "delta_R_from_directed": dR_from_directed,
                "symmetrized_R_identity_error": abs(dR - dR_from_directed),
                "gate_on": bool(intermediate["gate_on"]),
                "controllers_clipped": controllers_clipped,
                "winner_map_expected": winner_expected,
                "selected_positive": selected_positive,
                "minimum_winner_margin": minimum_winner_margin,
                "isolation_error": isolation_error,
                "q2": q2,
                "q7": q7,
                "s2": float(intermediate["scales"][NODE_2]),
                "s7": float(intermediate["scales"][NODE_7]),
            }
            for orientation, metrics in directed_metrics.items():
                for key, value in metrics.items():
                    row[f"{orientation}_{key}"] = value
            rows.append(row)

        augmented.advance_base_state(state, intermediate)

    final_replay_exact = bool(np.array_equal(state.B, expected_final))
    trajectory = pd.DataFrame(rows).sort_values(["pair", "step"]).reset_index(drop=True)
    trajectory["delta_R_next"] = trajectory.groupby("pair", sort=False)[
        "delta_R"
    ].shift(-1)
    trajectory["delta_x_next"] = trajectory.groupby("pair", sort=False)[
        "delta_x"
    ].shift(-1)
    trajectory["recurrence_prediction"] = (
        trajectory["lambda_step"] * trajectory["delta_x"]
        + a_R * trajectory["delta_R_next"]
    )
    trajectory["proposal_recurrence_error"] = np.abs(
        trajectory["delta_x_next"] - trajectory["recurrence_prediction"]
    )

    identity_columns = {
        "proposal_difference": "proposal_identity_error",
        "projected_weight_difference": "projection_identity_error",
        "proposal_recurrence": "proposal_recurrence_error",
        "symmetrized_R": "symmetrized_R_identity_error",
        "radial_forward": "forward_radial_recurrence_error",
        "radial_reverse": "reverse_radial_recurrence_error",
        "magnitude_quotient_forward": "forward_magnitude_quotient_error",
        "magnitude_quotient_reverse": "reverse_magnitude_quotient_error",
    }
    identity_rows: list[dict[str, Any]] = []
    for pair, group in trajectory.groupby("pair", sort=False):
        for identity, column in identity_columns.items():
            values = group[column].to_numpy(float)
            values = values[np.isfinite(values)]
            identity_rows.append(
                {
                    "pair": pair,
                    "identity": identity,
                    "count": int(len(values)),
                    "maximum_absolute_error": float(np.max(values)) if len(values) else np.nan,
                    "median_absolute_error": float(np.median(values)) if len(values) else np.nan,
                }
            )
    identities = pd.DataFrame(identity_rows)

    interval_rows: list[dict[str, Any]] = []
    interval_steps = [
        min(future_steps, max(0, int(round(value / dt))))
        for value in args.intervals
    ]
    interval_steps = sorted(set(interval_steps))
    for pair, group in trajectory.groupby("pair", sort=False):
        group = group.sort_values("step")
        for start, end in zip(interval_steps[:-1], interval_steps[1:]):
            subset = group.loc[(group["step"] >= start) & (group["step"] < end)]
            if len(subset) < 3:
                continue
            dx_fit = fit_log_rate(
                subset["time"].to_numpy(float),
                subset["delta_x"].to_numpy(float),
                args.signal_floor,
            )
            dR_fit = fit_log_rate(
                subset["time"].to_numpy(float),
                subset["delta_R"].to_numpy(float),
                args.signal_floor,
            )
            align_f_fit = fit_log_rate(
                subset["time"].to_numpy(float),
                subset["forward_alignment_residual"].to_numpy(float),
                args.signal_floor,
            )
            align_r_fit = fit_log_rate(
                subset["time"].to_numpy(float),
                subset["reverse_alignment_residual"].to_numpy(float),
                args.signal_floor,
            )
            interval_rows.append(
                {
                    "pair": pair,
                    "start_time": start * dt,
                    "end_time": end * dt,
                    "count": int(len(subset)),
                    "dx_rate": dx_fit["rate"],
                    "dx_R_squared": dx_fit["R_squared"],
                    "dR_rate": dR_fit["rate"],
                    "dR_R_squared": dR_fit["R_squared"],
                    "alignment_forward_rate": align_f_fit["rate"],
                    "alignment_forward_R_squared": align_f_fit["R_squared"],
                    "alignment_reverse_rate": align_r_fit["rate"],
                    "alignment_reverse_R_squared": align_r_fit["R_squared"],
                    "median_lambda_step": float(np.median(subset["lambda_step"])),
                    "maximum_lambda_step": float(np.max(subset["lambda_step"])),
                    "minimum_magnitude_denominator": float(
                        min(
                            subset["forward_magnitude_denominator_next"].min(),
                            subset["reverse_magnitude_denominator_next"].min(),
                        )
                    ),
                    "median_abs_delta_x": float(np.median(np.abs(subset["delta_x"]))),
                    "median_abs_delta_R": float(np.median(np.abs(subset["delta_R"]))),
                    "median_abs_alignment_forward": float(
                        np.median(np.abs(subset["forward_alignment_residual"]))
                    ),
                    "median_abs_alignment_reverse": float(
                        np.median(np.abs(subset["reverse_alignment_residual"]))
                    ),
                }
            )
    intervals = pd.DataFrame(interval_rows)

    atomic_csv(output_dir / "proposal_equalization_trajectory.csv", trajectory)
    atomic_csv(output_dir / "proposal_equalization_identity_summary.csv", identities)
    atomic_csv(output_dir / "proposal_equalization_interval_summary.csv", intervals)
    report = make_report(
        trajectory,
        intervals,
        identities,
        final_replay_exact=final_replay_exact,
        alpha=alpha,
        c0=c0,
    )
    atomic_text(output_dir / "proposal_equalization_report.txt", report)

    source_path = Path(__file__).resolve()
    dependencies = {
        "base": Path(base.__file__).resolve(),
        "augmented": Path(augmented.__file__).resolve(),
    }
    analysis_manifest = {
        "analysis": "AIEF-1.4 conditional proposal-equalization bridge audit",
        "source": {"path": str(source_path), "sha256": sha256(source_path)},
        "dependencies": {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in dependencies.items()
        },
        "command": sys.argv,
        "production_run_hash": DEFAULT_RUN_HASH,
        "exceptional_seed": args.seed,
        "inputs": {
            "npz": {"path": str(Path(args.npz).resolve()), "sha256": sha256(args.npz)},
            "manifest": {
                "path": str(Path(args.manifest).resolve()),
                "sha256": sha256(args.manifest),
            },
        },
        "parameters": {
            "scale_epsilon": args.scale_epsilon,
            "signal_floor": args.signal_floor,
            "intervals": args.intervals,
            "dt": dt,
            "alpha": alpha,
            "c0": c0,
        },
        "final_replay_exact": final_replay_exact,
        "branch_checks": {
            "gate_on_all": bool(trajectory["gate_on"].all()),
            "selected_positive_all": bool(trajectory["selected_positive"].all()),
            "controllers_clipped_all": bool(trajectory["controllers_clipped"].all()),
            "winner_map_expected_all": bool(trajectory["winner_map_expected"].all()),
            "minimum_winner_margin": float(trajectory["minimum_winner_margin"].min()),
            "maximum_isolation_error": float(trajectory["isolation_error"].max()),
        },
        "outputs": [
            "proposal_equalization_trajectory.csv",
            "proposal_equalization_identity_summary.csv",
            "proposal_equalization_interval_summary.csv",
            "proposal_equalization_report.txt",
            "analysis_manifest.json",
        ],
        "interpretation_constraints": [
            "The exceptional seed is one seed/graph realization.",
            "Exact recurrence checks do not prove infinite-time forcing decay.",
            "Interval rate fits are finite-horizon descriptive evidence.",
            "Saved branch persistence does not prove future branch persistence.",
            "No production trajectory or model parameter is changed.",
        ],
    }
    atomic_text(
        output_dir / "analysis_manifest.json",
        json.dumps(analysis_manifest, indent=2, sort_keys=True) + "\n",
    )

    print(report)
    print(f"Saved analysis to {output_dir.resolve()}")


if __name__ == "__main__":
    main()
