#!/usr/bin/env python3
"""Exceptional-seed and corrected tangent-perturbation analysis for AIEF-1.4.

This targeted script addresses two open issues:

1. It replays the exceptional mature seed at every timestep, locates active-set
   switches, and records pre/post continuous-weight reorganization.
2. It generates tangent-face directions once per seed/direction ID, reuses each
   direction across all perturbation amplitudes, and compares frozen-fast
   contraction predictions with finely sampled coupled recovery.

The script imports the already validated dynamics and ideal directional field
from AIEF_1_4_stationarity_perturbation_analysis_updated.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

import AIEF_1_4_stationarity_perturbation_analysis_updated as base


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_SCALAR = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_scalar_summary.csv"
)
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_exceptional_tangent"
DEFAULT_EXCEPTIONAL_SEED = "4619122171158768524"
DEFAULT_DELTAS = "1e-4,1e-3,1e-2,5e-2"
DEFAULT_DIRECTIONS = 5
DEFAULT_MAX_SEEDS = 5
DEFAULT_COUPLED_TIME = 15.0
DEFAULT_SAMPLE_STRIDE = 5
DEFAULT_BOUNDARY_TOL = 1e-9
ZERO_TOL = 1e-14


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_float_list(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated floats") from exc
    if not values or any(value <= 0.0 for value in values):
        raise argparse.ArgumentTypeError("all perturbation sizes must be positive")
    return sorted(set(values))


def spectral_metrics(B: np.ndarray) -> dict[str, float]:
    B = 0.5 * (np.asarray(B, dtype=float) + np.asarray(B, dtype=float).T)
    eigenvalues = np.linalg.eigvalsh(B)
    eigenvalues.sort()
    row_sum = np.sum(B, axis=1)
    L = np.diag(row_sum) - B
    laplacian = np.clip(np.linalg.eigvalsh(L), 0.0, None)
    laplacian.sort()
    return {
        "adjacency_lambda1": float(eigenvalues[-1]),
        "adjacency_lambda2": float(eigenvalues[-2]),
        "adjacency_gap12": float(eigenvalues[-1] - eigenvalues[-2]),
        "laplacian_lambda2": float(laplacian[1]),
        "laplacian_lambda_max": float(laplacian[-1]),
    }


def replay_exceptional_seed(
    state: base.DynamicState,
    expected_final: np.ndarray,
    model: dict[str, Any],
    future_steps: int,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    seed: str,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], dict[str, Any]]:
    reference_B = state.B.copy()
    reference_norm = max(float(np.linalg.norm(reference_B)), ZERO_TOL)
    previous_saturated: np.ndarray | None = None
    previous_outward: np.ndarray | None = None
    previous_zero: np.ndarray | None = None
    time_rows: list[dict[str, Any]] = []
    switch_rows: list[dict[str, Any]] = []
    matrices: dict[str, np.ndarray] = {
        "B_split": reference_B.copy(),
    }

    for step in range(future_steps):
        B_before = state.B.copy()
        info = base.actual_step(
            state,
            model,
            capacities,
            A,
            edges,
            boundary_tolerance,
            audit_operator=True,
        )
        saturated = info["saturated_mask"].copy()
        outward = info["outward_mask"].copy()
        zero = info["zero_mask"].copy()

        saturated_changed = (
            previous_saturated is not None
            and not np.array_equal(saturated, previous_saturated)
        )
        outward_changed = (
            previous_outward is not None
            and not np.array_equal(outward, previous_outward)
        )
        zero_changed = (
            previous_zero is not None and not np.array_equal(zero, previous_zero)
        )

        if saturated_changed or outward_changed or zero_changed:
            switch_index = len(switch_rows)
            matrices[f"switch_{switch_index}_B_before"] = B_before
            matrices[f"switch_{switch_index}_B_after"] = state.B.copy()
            changed_saturated = (
                np.flatnonzero(saturated != previous_saturated).tolist()
                if previous_saturated is not None
                else []
            )
            changed_outward = (
                np.flatnonzero(outward != previous_outward).tolist()
                if previous_outward is not None
                else []
            )
            changed_zero = (
                np.flatnonzero(zero != previous_zero).tolist()
                if previous_zero is not None
                else []
            )
            before_spec = spectral_metrics(B_before)
            after_spec = spectral_metrics(state.B)
            switch_rows.append(
                {
                    "seed": seed,
                    "switch_index": switch_index,
                    "step": step,
                    "time_since_split": (step + 1) * float(model["dt"]),
                    "saturated_changed": saturated_changed,
                    "outward_changed": outward_changed,
                    "zero_changed": zero_changed,
                    "changed_saturated_nodes": ";".join(map(str, changed_saturated)),
                    "changed_outward_nodes": ";".join(map(str, changed_outward)),
                    "changed_zero_edges": ";".join(map(str, changed_zero)),
                    "B_step_change_norm": float(np.linalg.norm(state.B - B_before)),
                    **{f"before_{key}": value for key, value in before_spec.items()},
                    **{f"after_{key}": value for key, value in after_spec.items()},
                }
            )

        time_rows.append(
            {
                "seed": seed,
                "step": step,
                "time_since_split": (step + 1) * float(model["dt"]),
                "F_norm": info["F_norm"],
                "P_F_norm": info["P_F_norm"],
                "P_F_over_F": info["P_F_over_F"],
                "normalized_B_drift_from_split": float(
                    np.linalg.norm(state.B - reference_B) / reference_norm
                ),
                "actual_update_norm": info["actual_update_norm"],
                "saturated_node_count": int(np.sum(saturated)),
                "outward_node_count": int(np.sum(outward)),
                "zero_edge_count": int(np.sum(zero)),
                "saturated_changed": saturated_changed,
                "outward_changed": outward_changed,
                "zero_changed": zero_changed,
                "tangent_feasible": info["tangent_feasible"],
                "idempotence_error": info["idempotence_error"],
                "positive_homogeneity_error": info[
                    "positive_homogeneity_error"
                ],
            }
        )
        previous_saturated = saturated
        previous_outward = outward
        previous_zero = zero

    matrices["B_final_replayed"] = state.B.copy()
    timeseries = pd.DataFrame(time_rows)
    switches = pd.DataFrame(switch_rows)

    if len(switches):
        first_switch_step = int(switches.iloc[0]["step"])
        pre = timeseries.loc[timeseries["step"] < first_switch_step]
        post = timeseries.loc[timeseries["step"] >= first_switch_step]
    else:
        first_switch_step = -1
        pre = timeseries
        post = timeseries.iloc[0:0]

    summary = {
        "seed": seed,
        "switch_count": int(len(switches)),
        "first_switch_step": first_switch_step,
        "first_switch_time": float(switches.iloc[0]["time_since_split"])
        if len(switches)
        else np.nan,
        "pre_switch_mean_stationarity_ratio": float(pre["P_F_over_F"].mean())
        if len(pre)
        else np.nan,
        "post_switch_mean_stationarity_ratio": float(post["P_F_over_F"].mean())
        if len(post)
        else np.nan,
        "post_switch_max_stationarity_ratio": float(post["P_F_over_F"].max())
        if len(post)
        else np.nan,
        "maximum_B_drift": float(
            timeseries["normalized_B_drift_from_split"].max()
        ),
        "final_B_drift": float(
            timeseries.iloc[-1]["normalized_B_drift_from_split"]
        ),
        "final_replay_exact": bool(np.array_equal(state.B, expected_final)),
        "final_replay_allclose_1e12": bool(
            np.allclose(state.B, expected_final, rtol=0.0, atol=1e-12)
        ),
    }
    return timeseries, switches, matrices, summary


def tangent_basis(
    w: np.ndarray,
    A: np.ndarray,
    capacities: np.ndarray,
    boundary_tolerance: float,
) -> tuple[np.ndarray, np.ndarray]:
    positive = w > ZERO_TOL
    support_indices = np.flatnonzero(positive)
    active_nodes = np.flatnonzero(
        (capacities - A @ w) <= boundary_tolerance
    )
    if not len(support_indices):
        return np.zeros((len(w), 0)), support_indices

    matrix = A[np.ix_(active_nodes, support_indices)]
    if matrix.size == 0:
        support_basis = np.eye(len(support_indices))
    else:
        _, singular_values, vh = np.linalg.svd(matrix, full_matrices=True)
        rank = int(np.sum(singular_values > 1e-10))
        support_basis = vh[rank:].T

    basis = np.zeros((len(w), support_basis.shape[1]), dtype=float)
    basis[support_indices, :] = support_basis
    return basis, support_indices


def deterministic_direction(
    basis: np.ndarray,
    seed: str,
    direction_id: int,
) -> np.ndarray | None:
    if basis.shape[1] == 0:
        return None
    digest = hashlib.sha256(
        f"fixed-tangent|{seed}|{direction_id}".encode()
    ).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "little"))
    coefficients = rng.normal(size=basis.shape[1])
    direction = basis @ coefficients
    norm = float(np.linalg.norm(direction))
    return direction / norm if norm > ZERO_TOL else None


def fit_exponential_rate(times: np.ndarray, distances: np.ndarray) -> tuple[float, float]:
    if not len(times) or distances[0] <= ZERO_TOL:
        return np.nan, np.nan
    normalized = distances / distances[0]
    valid = (
        (normalized > 1e-6)
        & (normalized <= 1.0 + 1e-8)
        & np.isfinite(normalized)
    )
    if np.sum(valid) < 3:
        return np.nan, np.nan
    x = times[valid]
    y = np.log(normalized[valid])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = np.sum((y - prediction) ** 2)
    total = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1.0 - residual / total if total > 0.0 else np.nan
    return float(-slope), float(r_squared)


def corrected_tangent_analysis(
    split_state: base.DynamicState,
    seed: str,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    deltas: Iterable[float],
    direction_count: int,
    boundary_tolerance: float,
    coupled_steps: int,
    sample_stride: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base_w = split_state.B[edges].copy()
    base_norm = max(float(np.linalg.norm(base_w)), ZERO_TOL)
    basis, support = tangent_basis(
        base_w, A, capacities, boundary_tolerance
    )

    # Shared updated fast-state forcing for all frozen-fast amplitudes.
    _, _, updated_coherence = base.compute_field_and_updated_coherence(
        split_state, model
    )
    R = np.abs(updated_coherence)
    R = 0.5 * (R + R.T)
    np.fill_diagonal(R, 0.0)

    # Unperturbed coupled reference trajectory, sampled at high resolution.
    reference = split_state.clone()
    reference_samples: dict[int, np.ndarray] = {0: reference.B.copy()}
    for step in range(1, coupled_steps + 1):
        base.actual_step(
            reference,
            model,
            capacities,
            A,
            edges,
            boundary_tolerance,
            audit_operator=False,
        )
        if step % sample_stride == 0 or step == coupled_steps:
            reference_samples[step] = reference.B.copy()

    summary_rows: list[dict[str, Any]] = []
    trajectory_rows: list[dict[str, Any]] = []

    for direction_id in range(direction_count):
        direction = deterministic_direction(basis, seed, direction_id)
        if direction is None:
            summary_rows.append(
                {
                    "seed": seed,
                    "direction_id": direction_id,
                    "status": "no_tangent_direction",
                    "basis_dimension": int(basis.shape[1]),
                    "support_size": int(len(support)),
                }
            )
            continue

        maximum = base.maximum_feasible_amplitude(
            base_w, direction, A, capacities
        )
        for delta in deltas:
            requested_amplitude = delta * base_norm
            amplitude = min(requested_amplitude, 0.5 * maximum)
            if not np.isfinite(amplitude) or amplitude <= 1e-12 * base_norm:
                summary_rows.append(
                    {
                        "seed": seed,
                        "direction_id": direction_id,
                        "delta": delta,
                        "status": "amplitude_too_small",
                        "basis_dimension": int(basis.shape[1]),
                        "support_size": int(len(support)),
                        "requested_amplitude": requested_amplitude,
                        "actual_amplitude": amplitude,
                    }
                )
                continue

            perturbed_w = base_w + amplitude * direction
            B_perturbed = base.vector_to_matrix(
                perturbed_w, split_state.B.shape[0], edges
            )
            F_matrix = (
                (float(model["eta"]) + float(model["mu"])) * R
                - float(model["mu"])
                - float(model["gamma"]) * B_perturbed
            )
            F_matrix = 0.5 * (F_matrix + F_matrix.T)
            np.fill_diagonal(F_matrix, 0.0)
            field, info, _, _ = base.ideal_directional_field(
                perturbed_w,
                F_matrix[edges],
                A,
                capacities,
                boundary_tolerance,
            )
            displacement = perturbed_w - base_w
            displacement_norm = float(np.linalg.norm(displacement))
            restore = -displacement
            numerator = float(restore @ field)
            kappa = numerator / max(displacement_norm**2, ZERO_TOL)
            cosine = numerator / max(
                displacement_norm * np.linalg.norm(field),
                np.finfo(float).tiny,
            )
            radial_component = numerator / max(displacement_norm, ZERO_TOL)
            radial_vector = radial_component * restore / max(
                displacement_norm, ZERO_TOL
            )
            transverse = field - radial_vector

            # Coupled trajectory from the same direction and amplitude.
            state = split_state.clone()
            state.B = B_perturbed.copy()
            times: list[float] = []
            distances: list[float] = []
            for step in range(coupled_steps + 1):
                if step in reference_samples:
                    distance = base.normalized_edge_distance(
                        state.B, reference_samples[step], edges
                    )
                    times.append(step * float(model["dt"]))
                    distances.append(distance)
                    trajectory_rows.append(
                        {
                            "seed": seed,
                            "direction_id": direction_id,
                            "delta": delta,
                            "step": step,
                            "time": step * float(model["dt"]),
                            "distance_to_reference": distance,
                        }
                    )
                if step == coupled_steps:
                    break
                base.actual_step(
                    state,
                    model,
                    capacities,
                    A,
                    edges,
                    boundary_tolerance,
                    audit_operator=False,
                )

            times_array = np.asarray(times, dtype=float)
            distance_array = np.asarray(distances, dtype=float)
            observed_rate, observed_r2 = fit_exponential_rate(
                times_array, distance_array
            )
            initial_distance = float(distance_array[0])
            half_indices = np.flatnonzero(distance_array <= 0.5 * initial_distance)
            ten_indices = np.flatnonzero(distance_array <= 0.1 * initial_distance)
            predicted_t50 = math.log(2.0) / kappa if kappa > 0.0 else np.nan
            predicted_t90 = math.log(10.0) / kappa if kappa > 0.0 else np.nan

            summary_rows.append(
                {
                    "seed": seed,
                    "direction_id": direction_id,
                    "delta": delta,
                    "status": "ok",
                    "basis_dimension": int(basis.shape[1]),
                    "support_size": int(len(support)),
                    "requested_amplitude": requested_amplitude,
                    "actual_amplitude": amplitude,
                    "amplitude_fraction_of_requested": amplitude
                    / requested_amplitude,
                    "relative_actual_amplitude": amplitude / base_norm,
                    "maximum_feasible_amplitude": maximum,
                    "frozen_field_norm": float(np.linalg.norm(field)),
                    "frozen_restoring_coefficient": kappa,
                    "frozen_restoring_cosine": cosine,
                    "frozen_transverse_ratio": float(
                        np.linalg.norm(transverse)
                        / max(np.linalg.norm(field), ZERO_TOL)
                    ),
                    "predicted_t50": predicted_t50,
                    "predicted_t90": predicted_t90,
                    "observed_t50": float(times_array[half_indices[0]])
                    if len(half_indices)
                    else np.nan,
                    "observed_t90": float(times_array[ten_indices[0]])
                    if len(ten_indices)
                    else np.nan,
                    "observed_exponential_rate": observed_rate,
                    "observed_exponential_r_squared": observed_r2,
                    "final_distance_ratio": float(
                        distance_array[-1] / max(initial_distance, ZERO_TOL)
                    ),
                    **info,
                }
            )
    return summary_rows, trajectory_rows


def summarize_numeric(
    frame: pd.DataFrame,
    group_columns: list[str],
) -> pd.DataFrame:
    identifiers = set(group_columns) | {"seed", "status"}
    metrics = [column for column in frame.columns if column not in identifiers]
    rows: list[dict[str, Any]] = []
    for key, group in frame.groupby(group_columns, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base_row = dict(zip(group_columns, key))
        for metric in metrics:
            raw = pd.to_numeric(group[metric], errors="coerce").to_numpy(float)
            finite = raw[np.isfinite(raw)]
            rows.append(
                {
                    **base_row,
                    "metric": metric,
                    "n_total": int(len(raw)),
                    "n_valid": int(len(finite)),
                    "mean": float(np.mean(finite)) if len(finite) else np.nan,
                    "std": float(np.std(finite)) if len(finite) else np.nan,
                    "median": float(np.median(finite)) if len(finite) else np.nan,
                    "minimum": float(np.min(finite)) if len(finite) else np.nan,
                    "maximum": float(np.max(finite)) if len(finite) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def make_report(
    exceptional_summary: dict[str, Any],
    tangent_summary: pd.DataFrame,
) -> str:
    lines = [
        "AIEF exceptional-seed and corrected tangent analysis",
        "====================================================",
        "",
        "Exceptional seed",
        "----------------",
    ]
    for key, value in exceptional_summary.items():
        lines.append(f"  {key}: {value}")

    lines.extend(["", "Corrected tangent perturbations", "-------------------------------"])
    selected = tangent_summary.loc[
        tangent_summary["metric"].isin(
            [
                "frozen_restoring_coefficient",
                "frozen_restoring_cosine",
                "frozen_transverse_ratio",
                "observed_exponential_rate",
                "observed_exponential_r_squared",
                "predicted_t50",
                "observed_t50",
                "predicted_t90",
                "observed_t90",
                "final_distance_ratio",
            ]
        )
    ]
    for delta, group in selected.groupby("delta"):
        lines.append(f"  delta={delta:g}")
        for _, row in group.iterrows():
            lines.append(
                f"    {row['metric']}: median={row['median']:.6g}, "
                f"min={row['minimum']:.6g}, max={row['maximum']:.6g}, "
                f"valid={int(row['n_valid'])}/{int(row['n_total'])}"
            )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* The same tangent direction is reused across all amplitudes within each seed/direction ID.",
            "* Directions with negligible feasible amplitude are rejected.",
            "* The exceptional-seed mechanism remains descriptive until its switch is analyzed in detail.",
            "* Predicted tangent times assume local exponential contraction.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scalar", default=DEFAULT_SCALAR)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--exceptional-seed", default=DEFAULT_EXCEPTIONAL_SEED)
    parser.add_argument("--max-seeds", type=int, default=DEFAULT_MAX_SEEDS)
    parser.add_argument("--directions", type=int, default=DEFAULT_DIRECTIONS)
    parser.add_argument(
        "--deltas", type=base.parse_float_list, default=base.parse_float_list(DEFAULT_DELTAS)
    )
    parser.add_argument("--coupled-time", type=float, default=DEFAULT_COUPLED_TIME)
    parser.add_argument("--sample-stride", type=int, default=DEFAULT_SAMPLE_STRIDE)
    parser.add_argument("--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.scalar, args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if (
        args.max_seeds < 0
        or args.directions <= 0
        or args.coupled_time <= 0.0
        or args.sample_stride <= 0
        or args.boundary_tol < 0.0
    ):
        raise ValueError("invalid command-line settings")
    os.makedirs(args.output_dir, exist_ok=True)

    scalar = pd.read_csv(args.scalar, dtype={"seed": str})
    scalar["seed"] = scalar["seed"].astype(str)
    scalar["branch"] = scalar["branch"].astype(str)
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    if args.exceptional_seed not in set(seeds):
        raise ValueError("exceptional seed not found in scalar CSV")
    tangent_seeds = seeds if args.max_seeds == 0 else seeds[: args.max_seeds]

    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = manifest["model"]
    node_count = int(model["N"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(node_count, capacity)
    A, edges = base.incidence_matrix(node_count)
    future_steps = int(manifest["protocol"]["future_steps"])
    coupled_steps = int(round(args.coupled_time / float(model["dt"])))

    with np.load(args.npz, allow_pickle=False) as data:
        exceptional_state = base.load_split_state(
            data, args.exceptional_seed
        )
        expected_final = np.asarray(
            data[base.branch_key("continue", args.exceptional_seed, "B_final")],
            dtype=float,
        )
        exceptional_ts, exceptional_switches, exceptional_matrices, exceptional_summary = (
            replay_exceptional_seed(
                exceptional_state,
                expected_final,
                model,
                future_steps,
                capacities,
                A,
                edges,
                args.boundary_tol,
                args.exceptional_seed,
            )
        )

        tangent_rows: list[dict[str, Any]] = []
        tangent_trajectories: list[dict[str, Any]] = []
        for seed in tangent_seeds:
            print(f"Corrected tangent analysis for seed {seed}")
            split_state = base.load_split_state(data, seed)
            summaries, trajectories = corrected_tangent_analysis(
                split_state,
                seed,
                model,
                capacities,
                A,
                edges,
                args.deltas,
                args.directions,
                args.boundary_tol,
                coupled_steps,
                args.sample_stride,
            )
            tangent_rows.extend(summaries)
            tangent_trajectories.extend(trajectories)

    tangent_frame = pd.DataFrame(tangent_rows)
    tangent_trajectory_frame = pd.DataFrame(tangent_trajectories)
    tangent_summary = summarize_numeric(tangent_frame, ["delta"])

    exceptional_ts.to_csv(
        os.path.join(args.output_dir, "exceptional_seed_timeseries.csv"), index=False
    )
    exceptional_switches.to_csv(
        os.path.join(args.output_dir, "exceptional_seed_switches.csv"), index=False
    )
    np.savez_compressed(
        os.path.join(args.output_dir, "exceptional_seed_switch_matrices.npz"),
        **exceptional_matrices,
    )
    tangent_frame.to_csv(
        os.path.join(args.output_dir, "corrected_tangent_by_seed.csv"), index=False
    )
    tangent_trajectory_frame.to_csv(
        os.path.join(args.output_dir, "corrected_tangent_trajectories.csv"), index=False
    )
    tangent_summary.to_csv(
        os.path.join(args.output_dir, "corrected_tangent_summary.csv"), index=False
    )

    with open(
        os.path.join(args.output_dir, "exceptional_seed_summary.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(exceptional_summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    report = make_report(exceptional_summary, tangent_summary)
    with open(
        os.path.join(args.output_dir, "exceptional_tangent_report.txt"),
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(report)
    print("\n" + report)

    analysis_manifest = {
        "analysis": "AIEF exceptional seed and corrected tangent perturbations",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "source_manifest_path": str(Path(args.manifest).resolve()),
        "source_manifest_sha256": file_sha256(args.manifest),
        "exceptional_seed": args.exceptional_seed,
        "tangent_seeds": tangent_seeds,
        "direction_count_per_seed": args.directions,
        "deltas": args.deltas,
        "coupled_time": args.coupled_time,
        "sample_stride": args.sample_stride,
        "boundary_tolerance": args.boundary_tol,
        "notes": [
            "One tangent direction is reused across all amplitudes per seed/direction ID.",
            "B_carrier_only/full_reset phase matching is not addressed by this script.",
            "Exceptional-seed results concern continuous weights, not only threshold support.",
        ],
    }
    with open(
        os.path.join(args.output_dir, "analysis_manifest.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(analysis_manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(f"Saved analysis to {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
