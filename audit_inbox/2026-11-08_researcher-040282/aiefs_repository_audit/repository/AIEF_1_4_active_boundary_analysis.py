#!/usr/bin/env python3
"""Active-boundary analysis for the AIEF admissibility map.

This script performs the next local-analysis stage:

1. Implements the candidate directional field of the ideal AIEF clip-and-scale
   admissibility map at exact active boundary states.
2. Verifies the field with finite differences over a small timestep grid.
3. Stratifies prior one-step comparisons by inactive/capacity/positivity strata.
4. Decomposes unconstrained forcing, the AIEF boundary field, and mirror motion
   in the entropy-Hessian eigenbasis.
5. Computes the optimally scaled mirror field and irreducible directional error.
6. Extracts coupled epsilon/timestep paths from the previous cross-product run.

The ideal admissibility map intentionally omits the fixed 1e-12 denominator
safeguard. The safeguard is a numerical implementation detail with a different
formal dt->0 limit.
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


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_SCALAR = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_scalar_summary.csv"
)
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_METHODS = (
    "aief_1_4_local_update_comparison/one_step_methods_by_seed.csv"
)
DEFAULT_COMPARISONS = (
    "aief_1_4_local_update_comparison/one_step_comparisons_by_seed.csv"
)
DEFAULT_OUTPUT_DIR = "aief_1_4_active_boundary_analysis"
DEFAULT_BOUNDARY_DT = "1e-2,1e-3,1e-4,1e-5,1e-6,1e-7,1e-8"
DEFAULT_EDGE_EPS = "1e-4,1e-5,1e-6"
DEFAULT_MARGIN_EPS = "1e-4,1e-5,1e-6"
DEFAULT_MAX_SEEDS = 5
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
    if not values or any(item <= 0.0 for item in values):
        raise argparse.ArgumentTypeError("all values must be positive")
    return sorted(set(values), reverse=True)


def prefix_key(seed: str, metric: str) -> str:
    return f"prefix_seed_{seed}_{metric}"


def incidence_matrix(node_count: int) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray]]:
    edges = np.triu_indices(node_count, k=1)
    A = np.zeros((node_count, len(edges[0])), dtype=float)
    A[edges[0], np.arange(len(edges[0]))] = 1.0
    A[edges[1], np.arange(len(edges[0]))] = 1.0
    return A, edges


def vector_to_matrix(
    w: np.ndarray,
    node_count: int,
    edges: tuple[np.ndarray, np.ndarray],
) -> np.ndarray:
    B = np.zeros((node_count, node_count), dtype=float)
    B[edges] = w
    B[(edges[1], edges[0])] = w
    return B


def compute_split_field(
    data: Any,
    seed: str,
    manifest: dict[str, Any],
    edges: tuple[np.ndarray, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    model = manifest["model"]
    B = np.asarray(data[prefix_key(seed, "B_at_split")], dtype=float)
    theta = np.asarray(data[prefix_key(seed, "theta_at_split")], dtype=float)
    coherence = np.asarray(data[prefix_key(seed, "coherence_acc_at_split")])
    history = np.asarray(data[prefix_key(seed, "history_at_split")], dtype=float)
    delayed = history[0]
    omega = np.asarray(model["omega"], dtype=float)
    dt = float(model["dt"])
    tau = float(model["tau"])
    t_window = float(model["T_window"])
    eta = float(model["eta"])
    mu = float(model["mu"])
    gamma = float(model["gamma"])

    dphi = (
        theta[:, None]
        - delayed[None, :]
        - ((omega[:, None] + omega[None, :]) / 2.0) * tau
    )
    alpha = float(np.exp(-dt / t_window))
    updated_coherence = alpha * coherence + (1.0 - alpha) * np.exp(1j * dphi)
    R = np.abs(updated_coherence)
    R = 0.5 * (R + R.T)
    np.fill_diagonal(R, 0.0)
    F = (eta + mu) * R - mu - gamma * B
    F = 0.5 * (F + F.T)
    np.fill_diagonal(F, 0.0)
    return B[edges].copy(), F[edges].copy()


def positivity_direction(w: np.ndarray, F: np.ndarray) -> np.ndarray:
    result = F.copy()
    zero = w <= ZERO_TOL
    result[zero] = np.maximum(F[zero], 0.0)
    return result


def analytic_boundary_field(
    w: np.ndarray,
    F: np.ndarray,
    A: np.ndarray,
    capacities: np.ndarray,
    boundary_tolerance: float,
) -> tuple[np.ndarray, dict[str, Any], np.ndarray]:
    """Candidate directional field for the ideal AIEF admissibility map."""
    p_direction = positivity_direction(w, F)
    row_sum = A @ w
    slack = capacities - row_sum
    saturated = slack <= boundary_tolerance

    # Snap numerically saturated capacities to the observed row sum. This
    # removes the old denominator safeguard/slack from the idealized derivative
    # test while recording the size of the snap.
    effective_capacities = capacities.copy()
    effective_capacities[saturated] = row_sum[saturated]

    row_direction = A @ p_direction
    alpha = np.zeros(len(capacities), dtype=float)
    outward = saturated & (row_direction > 0.0)
    alpha[outward] = row_direction[outward] / effective_capacities[outward]
    endpoints = [np.flatnonzero(A[:, edge]) for edge in range(A.shape[1])]
    edge_alpha = np.array(
        [max(alpha[nodes[0]], alpha[nodes[1]]) for nodes in endpoints],
        dtype=float,
    )
    field = p_direction - w * edge_alpha
    info = {
        "zero_edge_count": int(np.sum(w <= ZERO_TOL)),
        "saturated_node_count": int(np.sum(saturated)),
        "outward_saturated_node_count": int(np.sum(outward)),
        "positivity_modified_edge_count": int(
            np.sum((w <= ZERO_TOL) & (F < 0.0))
        ),
        "maximum_capacity_snap": float(
            np.max(np.abs(effective_capacities - capacities))
        ),
        "field_norm": float(np.linalg.norm(field)),
        "unconstrained_field_norm": float(np.linalg.norm(F)),
    }
    return field, info, effective_capacities


def ideal_admissibility_map(
    w: np.ndarray,
    F: np.ndarray,
    dt: float,
    A: np.ndarray,
    capacities: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Exact ideal clip + symmetric endpoint scaling, with no denominator eps."""
    proposal = np.maximum(w + dt * F, 0.0)
    row_sum = A @ proposal
    scale = np.ones(len(capacities), dtype=float)
    violating = row_sum > capacities
    scale[violating] = capacities[violating] / row_sum[violating]

    endpoints = [np.flatnonzero(A[:, edge]) for edge in range(A.shape[1])]
    edge_scale = np.array(
        [min(scale[nodes[0]], scale[nodes[1]]) for nodes in endpoints],
        dtype=float,
    )
    result = proposal * edge_scale
    return result, {
        "positivity_clipped_edges": int(np.sum((w + dt * F) < 0.0)),
        "active_capacity_nodes": int(np.sum(violating)),
        "minimum_margin": float(np.min(capacities - A @ result)),
    }


def finite_difference_boundary_validation(
    scalar: pd.DataFrame,
    npz_path: str,
    manifest: dict[str, Any],
    dt_values: Iterable[float],
    max_seeds: int,
    boundary_tolerance: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    node_count = int(manifest["model"]["N"])
    capacity = (
        float(manifest["model"]["a"])
        - float(manifest["model"]["delta"])
    ) / float(manifest["model"]["q"])
    capacities = np.full(node_count, capacity)
    A, edges = incidence_matrix(node_count)
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    if max_seeds > 0:
        seeds = seeds[:max_seeds]

    rows: list[dict[str, Any]] = []
    field_rows: list[dict[str, Any]] = []
    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            w, physical_F = compute_split_field(data, seed, manifest, edges)
            field_scale = max(float(np.linalg.norm(physical_F)), 1.0)
            random_seed = int.from_bytes(
                hashlib.sha256(f"boundary-probe|{seed}".encode()).digest()[:8],
                "little",
            )
            rng = np.random.default_rng(random_seed)
            random_probe = rng.normal(size=len(w))
            random_probe *= field_scale / np.linalg.norm(random_probe)
            outward_probe = np.ones(len(w), dtype=float)
            outward_probe *= field_scale / np.linalg.norm(outward_probe)
            directions = {
                "physical_field": physical_F,
                "random_probe": random_probe,
                "outward_probe": outward_probe,
            }

            for direction_name, direction in directions.items():
                field, info, effective_capacities = analytic_boundary_field(
                    w, direction, A, capacities, boundary_tolerance
                )
                field_rows.append(
                    {"seed": seed, "direction": direction_name, **info}
                )
                field_norm = float(np.linalg.norm(field))
                for dt in dt_values:
                    next_w, map_info = ideal_admissibility_map(
                        w, direction, dt, A, effective_capacities
                    )
                    finite_rate = (next_w - w) / dt
                    error = finite_rate - field
                    finite_norm = float(np.linalg.norm(finite_rate))
                    denominator = finite_norm * field_norm
                    rows.append(
                        {
                            "seed": seed,
                            "direction": direction_name,
                            "dt": dt,
                            "analytic_field_norm": field_norm,
                            "finite_rate_norm": finite_norm,
                            "rate_error_norm": float(np.linalg.norm(error)),
                            "increment_error_norm": float(np.linalg.norm(error) * dt),
                            "relative_rate_error": float(
                                np.linalg.norm(error) / field_norm
                            )
                            if field_norm > 1e-10
                            else np.nan,
                            "rate_cosine": float(finite_rate @ field / denominator)
                            if denominator > np.finfo(float).tiny
                            and field_norm > 1e-10
                            else np.nan,
                            "numerically_stationary_direction": bool(
                                field_norm <= 1e-10
                            ),
                            **map_info,
                        }
                    )
    validation = pd.DataFrame(rows)

    order_rows: list[dict[str, Any]] = []
    for (seed, direction), group in validation.groupby(["seed", "direction"]):
        group = group.sort_values("dt")
        dt = group["dt"].to_numpy(float)
        rate_error = group["rate_error_norm"].to_numpy(float)
        field_norm = float(group["analytic_field_norm"].iloc[0])
        valid = (
            (rate_error > 100.0 * np.finfo(float).eps)
            & np.isfinite(rate_error)
            & (field_norm > 1e-10)
        )
        if np.sum(valid) >= 2:
            dt_valid = dt[valid]
            error_valid = rate_error[valid]
            use = np.argsort(dt_valid)[: min(3, np.sum(valid))]
            slope, intercept = np.polyfit(
                np.log(dt_valid[use]), np.log(error_valid[use]), 1
            )
        else:
            slope = intercept = np.nan
        order_rows.append(
            {
                "seed": seed,
                "direction": direction,
                "analytic_field_norm": field_norm,
                "numerically_stationary_direction": bool(field_norm <= 1e-10),
                "n_dt": int(np.sum(valid)),
                "rate_error_order": float(slope),
                "increment_error_order": float(slope + 1.0)
                if np.isfinite(slope)
                else np.nan,
                "log_intercept": float(intercept),
                "smallest_dt_rate_error": float(rate_error[0]),
            }
        )
    field_frame = pd.DataFrame(field_rows)
    order_frame = pd.DataFrame(order_rows)
    return validation, field_frame.merge(
        order_frame, on=["seed", "direction"], how="left"
    )

def classify_stratum(active_nodes: float, clipped_edges: float) -> str:
    capacity = active_nodes > 0
    positivity = clipped_edges > 0
    if capacity and positivity:
        return "capacity_and_positivity_active"
    if capacity:
        return "capacity_active"
    if positivity:
        return "positivity_active"
    return "interior_inactive"


def active_stratified_analysis(
    methods_path: str,
    comparisons_path: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    methods = pd.read_csv(methods_path, dtype={"seed": str})
    comparisons = pd.read_csv(comparisons_path, dtype={"seed": str})
    current = methods.loc[methods["method"] == "current_admissibility"].copy()
    keys = ["seed", "dt", "edge_epsilon", "margin_epsilon"]
    current = current[
        keys + ["active_capacity_nodes", "positivity_clipped_edges"]
    ]
    merged = comparisons.merge(current, on=keys, how="left", validate="many_to_one")
    merged["active_stratum"] = [
        classify_stratum(a, p)
        for a, p in zip(
            pd.to_numeric(merged["active_capacity_nodes"], errors="coerce").fillna(0),
            pd.to_numeric(merged["positivity_clipped_edges"], errors="coerce").fillna(0),
        )
    ]

    rows: list[dict[str, Any]] = []
    group_columns = [
        "seed",
        "left_method",
        "right_method",
        "edge_epsilon",
        "margin_epsilon",
        "active_stratum",
    ]
    for group_key, group in merged.groupby(group_columns):
        group = group.sort_values("dt")
        dt = group["dt"].to_numpy(float)
        discrepancy = group["increment_discrepancy_norm"].to_numpy(float)
        valid = (dt > 0.0) & (discrepancy > 0.0) & np.isfinite(discrepancy)
        if np.sum(valid) >= 2:
            dt_valid = dt[valid]
            discrepancy_valid = discrepancy[valid]
            order = np.argsort(dt_valid)[: min(3, np.sum(valid))]
            slope, _ = np.polyfit(
                np.log(dt_valid[order]),
                np.log(discrepancy_valid[order]),
                1,
            )
        else:
            slope = np.nan
        rows.append(
            {
                **dict(zip(group_columns, group_key)),
                "n_dt": int(np.sum(valid)),
                "increment_discrepancy_order": float(slope),
                "rate_discrepancy_order": float(slope - 1.0)
                if np.isfinite(slope)
                else np.nan,
                "smallest_dt": float(np.min(dt)) if len(dt) else np.nan,
                "smallest_dt_discrepancy_rate": float(
                    group.loc[group["dt"].idxmin(), "discrepancy_rate_norm"]
                )
                if len(group)
                else np.nan,
            }
        )
    return merged, pd.DataFrame(rows)


def interiorize(
    w: np.ndarray,
    A: np.ndarray,
    capacities: np.ndarray,
    edge_epsilon: float,
    margin_epsilon: float,
) -> tuple[np.ndarray, np.ndarray]:
    degrees = np.sum(A, axis=1)
    available = capacities - margin_epsilon - degrees * edge_epsilon
    row_mass = A @ w
    ratios = np.full(len(capacities), np.inf)
    positive = row_mass > 0.0
    ratios[positive] = available[positive] / row_mass[positive]
    alpha = float(min(1.0, np.min(ratios)))
    w_int = edge_epsilon + alpha * w
    margins = capacities - A @ w_int
    if np.any(w_int <= 0.0) or np.any(margins <= 0.0):
        raise RuntimeError("interiorization failed")
    return w_int, margins


def entropy_hessian(w: np.ndarray, margins: np.ndarray, A: np.ndarray) -> np.ndarray:
    return np.diag(1.0 / w) + A.T @ np.diag(1.0 / margins) @ A


def effective_modes(probabilities: np.ndarray) -> float:
    denominator = float(np.sum(probabilities**2))
    return 1.0 / denominator if denominator > ZERO_TOL else 0.0


def eigenspace_and_optimal_beta(
    scalar: pd.DataFrame,
    npz_path: str,
    manifest: dict[str, Any],
    edge_eps_values: Iterable[float],
    margin_eps_values: Iterable[float],
    max_seeds: int,
    boundary_tolerance: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    node_count = int(manifest["model"]["N"])
    capacity = (
        float(manifest["model"]["a"])
        - float(manifest["model"]["delta"])
    ) / float(manifest["model"]["q"])
    capacities = np.full(node_count, capacity)
    A, edges = incidence_matrix(node_count)
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    if max_seeds > 0:
        seeds = seeds[:max_seeds]

    mode_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            raw_w, F = compute_split_field(data, seed, manifest, edges)
            V, _, _ = analytic_boundary_field(
                raw_w, F, A, capacities, boundary_tolerance
            )
            for edge_epsilon in edge_eps_values:
                for margin_epsilon in margin_eps_values:
                    w, margins = interiorize(
                        raw_w, A, capacities, edge_epsilon, margin_epsilon
                    )
                    H = entropy_hessian(w, margins, A)
                    eigenvalues, eigenvectors = np.linalg.eigh(H)
                    coefficients_F = eigenvectors.T @ F
                    coefficients_A = eigenvectors.T @ V
                    mirror_coefficients = coefficients_F / eigenvalues
                    mirror = eigenvectors @ mirror_coefficients

                    energy_F = coefficients_F**2
                    energy_A = coefficients_A**2
                    energy_M = mirror_coefficients**2
                    pF = energy_F / max(float(np.sum(energy_F)), ZERO_TOL)
                    pA = energy_A / max(float(np.sum(energy_A)), ZERO_TOL)
                    pM = energy_M / max(float(np.sum(energy_M)), ZERO_TOL)
                    high_count = max(1, int(math.ceil(0.1 * len(eigenvalues))))
                    high = np.argsort(eigenvalues)[-high_count:]

                    V_norm = float(np.linalg.norm(V))
                    mirror_norm = float(np.linalg.norm(mirror))
                    boundary_stationary = bool(V_norm <= 1e-10)
                    denominator = float(mirror @ mirror)
                    alignment = float(V @ mirror)
                    if boundary_stationary:
                        a_star = 0.0
                        beta_star = np.inf
                        directional_residual = np.nan
                        cosine = np.nan
                    else:
                        a_star = (
                            max(0.0, alignment / denominator)
                            if denominator > 0.0
                            else 0.0
                        )
                        beta_star = 1.0 / a_star if a_star > 0.0 else np.inf
                        optimized = a_star * mirror
                        directional_residual = float(
                            np.linalg.norm(V - optimized) / V_norm
                        )
                        cosine = float(
                            V @ mirror
                            / max(V_norm * mirror_norm, np.finfo(float).tiny)
                        )

                    summary_rows.append(
                        {
                            "seed": seed,
                            "edge_epsilon": edge_epsilon,
                            "margin_epsilon": margin_epsilon,
                            "hessian_condition_number": float(
                                eigenvalues[-1] / eigenvalues[0]
                            ),
                            "forcing_high_curvature_decile_fraction": float(
                                np.sum(pF[high])
                            ),
                            "admissibility_high_curvature_decile_fraction": float(
                                np.sum(pA[high])
                            ),
                            "mirror_high_curvature_decile_fraction": float(
                                np.sum(pM[high])
                            ),
                            "forcing_effective_modes": effective_modes(pF),
                            "admissibility_effective_modes": effective_modes(pA),
                            "mirror_effective_modes": effective_modes(pM),
                            "V_A_norm": V_norm,
                            "boundary_field_stationary": boundary_stationary,
                            "unconstrained_F_norm": float(np.linalg.norm(F)),
                            "mirror_unscaled_norm": mirror_norm,
                            "V_A_mirror_cosine": cosine,
                            "optimal_a_1_over_beta": a_star,
                            "optimal_beta": beta_star,
                            "optimized_mirror_directional_residual": directional_residual,
                        }
                    )

                    order = np.argsort(eigenvalues)
                    for rank, index in enumerate(order):
                        mode_rows.append(
                            {
                                "seed": seed,
                                "edge_epsilon": edge_epsilon,
                                "margin_epsilon": margin_epsilon,
                                "mode_rank_low_to_high_curvature": rank + 1,
                                "eigenvalue": float(eigenvalues[index]),
                                "coefficient_F": float(coefficients_F[index]),
                                "coefficient_V_A": float(coefficients_A[index]),
                                "coefficient_mirror": float(
                                    mirror_coefficients[index]
                                ),
                                "forcing_energy_fraction": float(pF[index]),
                                "admissibility_energy_fraction": float(pA[index]),
                                "mirror_energy_fraction": float(pM[index]),
                            }
                        )
    return pd.DataFrame(summary_rows), pd.DataFrame(mode_rows)


def coupled_path_analysis(comparisons: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = comparisons.copy()
    frame["kappa_edge"] = frame["edge_epsilon"] / frame["dt"]
    frame["kappa_margin"] = frame["margin_epsilon"] / frame["dt"]
    # Powers-of-ten grids are expected; rounding log ratios makes exact paths.
    frame["log10_kappa_edge"] = np.round(np.log10(frame["kappa_edge"]), 8)
    frame["log10_kappa_margin"] = np.round(np.log10(frame["kappa_margin"]), 8)

    rows: list[dict[str, Any]] = []
    group_columns = [
        "seed",
        "left_method",
        "right_method",
        "log10_kappa_edge",
        "log10_kappa_margin",
    ]
    for group_key, group in frame.groupby(group_columns):
        group = group.sort_values("dt")
        dt = group["dt"].to_numpy(float)
        discrepancy = group["increment_discrepancy_norm"].to_numpy(float)
        valid = (dt > 0.0) & (discrepancy > 0.0) & np.isfinite(discrepancy)
        if np.sum(valid) >= 2:
            dt_valid = dt[valid]
            discrepancy_valid = discrepancy[valid]
            use = np.argsort(dt_valid)[: min(3, np.sum(valid))]
            slope, _ = np.polyfit(
                np.log(dt_valid[use]), np.log(discrepancy_valid[use]), 1
            )
        else:
            slope = np.nan
        rows.append(
            {
                **dict(zip(group_columns, group_key)),
                "kappa_edge": float(10 ** group_key[-2]),
                "kappa_margin": float(10 ** group_key[-1]),
                "n_dt": int(np.sum(valid)),
                "increment_discrepancy_order": float(slope),
                "rate_discrepancy_order": float(slope - 1.0)
                if np.isfinite(slope)
                else np.nan,
                "smallest_dt": float(np.min(dt)),
                "smallest_dt_rate_error": float(
                    group.loc[group["dt"].idxmin(), "discrepancy_rate_norm"]
                ),
                "active_capacity_fraction": float(
                    np.mean(group["active_capacity_nodes"] > 0)
                )
                if "active_capacity_nodes" in group
                else np.nan,
            }
        )
    return frame, pd.DataFrame(rows)


def summarize(
    frame: pd.DataFrame,
    group_columns: list[str],
    metrics: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, group in frame.groupby(group_columns, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_columns, key))
        for metric in metrics:
            if metric not in group.columns:
                continue
            raw = pd.to_numeric(group[metric], errors="coerce").to_numpy(float)
            finite = raw[np.isfinite(raw)]
            rows.append(
                {
                    **base,
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
    boundary_order: pd.DataFrame,
    stratified_orders: pd.DataFrame,
    eigen_summary: pd.DataFrame,
    coupled_summary: pd.DataFrame,
) -> str:
    lines = [
        "AIEF active-boundary directional-field analysis",
        "================================================",
        "",
        "The analytic field is derived for the ideal map without the fixed denominator safeguard.",
        "",
        "Ideal boundary-field finite-difference verification",
        "----------------------------------------------------",
    ]
    for direction, group in boundary_order.groupby("direction"):
        rate_orders = group["rate_error_order"].to_numpy(float)
        rate_orders = rate_orders[np.isfinite(rate_orders)]
        increment_orders = group["increment_error_order"].to_numpy(float)
        increment_orders = increment_orders[np.isfinite(increment_orders)]
        lines.append(
            f"  {direction}: median field norm="
            f"{group['field_norm'].median():.6g}, "
            f"stationary={int(group['numerically_stationary_direction'].sum())}/{len(group)}, "
            f"median rate-error order="
            f"{np.median(rate_orders):.6g}, "
            f"median increment-error order="
            f"{np.median(increment_orders):.6g}"
            if len(rate_orders) and len(increment_orders)
            else
            f"  {direction}: median field norm={group['field_norm'].median():.6g}, "
            f"stationary={int(group['numerically_stationary_direction'].sum())}/{len(group)}, "
            "order not estimable above numerical floor"
        )
    lines.append(
        f"  median maximum capacity snap: "
        f"{boundary_order['maximum_capacity_snap'].median():.6g}"
    )

    lines.extend(["", "Active-stratified coordinate orders", "-----------------------------------"])
    for (left, right, stratum), group in stratified_orders.groupby(
        ["left_method", "right_method", "active_stratum"]
    ):
        values = group["increment_discrepancy_order"].to_numpy(float)
        values = values[np.isfinite(values)]
        lines.append(
            f"  {left} vs {right} / {stratum}: "
            f"median order={np.median(values):.6g}, valid={len(values)}"
            if len(values)
            else f"  {left} vs {right} / {stratum}: no valid orders"
        )

    lines.extend(["", "Optimal mirror scaling", "----------------------"])
    for (edge_eps, margin_eps), group in eigen_summary.groupby(
        ["edge_epsilon", "margin_epsilon"]
    ):
        stationary_count = int(group["boundary_field_stationary"].sum())
        beta_values = group["optimal_beta"].to_numpy(float)
        beta_values = beta_values[np.isfinite(beta_values)]
        beta_text = f"{np.median(beta_values):.6g}" if len(beta_values) else "not-defined"
        residual_values = group["optimized_mirror_directional_residual"].to_numpy(float)
        residual_values = residual_values[np.isfinite(residual_values)]
        cosine_values = group["V_A_mirror_cosine"].to_numpy(float)
        cosine_values = cosine_values[np.isfinite(cosine_values)]
        residual_text = (
            f"{np.median(residual_values):.6g}" if len(residual_values) else "not-defined"
        )
        cosine_text = (
            f"{np.median(cosine_values):.6g}" if len(cosine_values) else "not-defined"
        )
        lines.append(
            f"  edge_eps={edge_eps:g}, margin_eps={margin_eps:g}: "
            f"stationary boundary fields={stationary_count}/{len(group)}, "
            f"median beta*={beta_text}, "
            f"median directional residual={residual_text}, "
            f"median cosine={cosine_text}"
        )

    lines.extend(["", "Coupled epsilon/dt paths", "------------------------"])
    valid_paths = coupled_summary.loc[coupled_summary["n_dt"] >= 2]
    lines.append(f"  paths with >=2 timesteps: {len(valid_paths)}")
    if len(valid_paths):
        lines.append(
            f"  median increment order: "
            f"{valid_paths['increment_discrepancy_order'].median():.6g}"
        )
        lines.append(
            f"  median active-capacity fraction: "
            f"{valid_paths['active_capacity_fraction'].median():.6g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* The analytic field is a candidate Hadamard/Bouligand directional derivative of the ideal map.",
            "* The fixed denominator safeguard has a different formal dt->0 limit.",
            "* Interior p≈2 results do not establish active-boundary equivalence.",
            "* beta* removes scalar speed mismatch but not directional disagreement.",
            "* Hessian eigenspaces depend strongly on interiorization epsilon.",
            "* Coupled epsilon/dt path dependence remains an open singular-limit question.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scalar", default=DEFAULT_SCALAR)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--methods", default=DEFAULT_METHODS)
    parser.add_argument("--comparisons", default=DEFAULT_COMPARISONS)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--boundary-dt",
        type=parse_float_list,
        default=parse_float_list(DEFAULT_BOUNDARY_DT),
    )
    parser.add_argument(
        "--edge-eps",
        type=parse_float_list,
        default=parse_float_list(DEFAULT_EDGE_EPS),
    )
    parser.add_argument(
        "--margin-eps",
        type=parse_float_list,
        default=parse_float_list(DEFAULT_MARGIN_EPS),
    )
    parser.add_argument("--max-seeds", type=int, default=DEFAULT_MAX_SEEDS)
    parser.add_argument(
        "--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (
        args.scalar,
        args.npz,
        args.manifest,
        args.methods,
        args.comparisons,
    ):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if args.max_seeds < 0 or args.boundary_tol < 0.0:
        raise ValueError("invalid max-seeds or boundary tolerance")
    os.makedirs(args.output_dir, exist_ok=True)

    scalar = pd.read_csv(args.scalar, dtype={"seed": str})
    scalar["seed"] = scalar["seed"].astype(str)
    scalar["branch"] = scalar["branch"].astype(str)
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    boundary_validation, boundary_orders = finite_difference_boundary_validation(
        scalar,
        args.npz,
        manifest,
        args.boundary_dt,
        args.max_seeds,
        args.boundary_tol,
    )
    stratified_comparisons, stratified_orders = active_stratified_analysis(
        args.methods, args.comparisons
    )
    eigen_summary, eigen_modes = eigenspace_and_optimal_beta(
        scalar,
        args.npz,
        manifest,
        args.edge_eps,
        args.margin_eps,
        args.max_seeds,
        args.boundary_tol,
    )

    # Add current-map activity information before coupled-path extraction.
    methods = pd.read_csv(args.methods, dtype={"seed": str})
    current = methods.loc[methods["method"] == "current_admissibility"]
    activity_columns = [
        "seed",
        "dt",
        "edge_epsilon",
        "margin_epsilon",
        "active_capacity_nodes",
        "positivity_clipped_edges",
    ]
    comparisons = pd.read_csv(args.comparisons, dtype={"seed": str}).merge(
        current[activity_columns],
        on=["seed", "dt", "edge_epsilon", "margin_epsilon"],
        how="left",
        validate="many_to_one",
    )
    coupled_rows, coupled_summary = coupled_path_analysis(comparisons)

    eigen_aggregate = summarize(
        eigen_summary,
        ["edge_epsilon", "margin_epsilon"],
        [
            "hessian_condition_number",
            "forcing_high_curvature_decile_fraction",
            "admissibility_high_curvature_decile_fraction",
            "mirror_high_curvature_decile_fraction",
            "forcing_effective_modes",
            "admissibility_effective_modes",
            "mirror_effective_modes",
            "boundary_field_stationary",
            "V_A_norm",
            "unconstrained_F_norm",
            "V_A_mirror_cosine",
            "optimal_beta",
            "optimized_mirror_directional_residual",
        ],
    )
    stratified_aggregate = summarize(
        stratified_orders,
        ["left_method", "right_method", "active_stratum"],
        ["increment_discrepancy_order", "rate_discrepancy_order"],
    )

    outputs = {
        "boundary_field_finite_difference.csv": boundary_validation,
        "boundary_field_convergence_orders.csv": boundary_orders,
        "active_stratified_comparisons.csv": stratified_comparisons,
        "active_stratified_orders_by_seed.csv": stratified_orders,
        "active_stratified_order_summary.csv": stratified_aggregate,
        "hessian_eigenspace_summary_by_seed.csv": eigen_summary,
        "hessian_eigenmodes.csv": eigen_modes,
        "hessian_eigenspace_summary.csv": eigen_aggregate,
        "coupled_epsilon_dt_rows.csv": coupled_rows,
        "coupled_epsilon_dt_summary.csv": coupled_summary,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)

    report = make_report(
        boundary_orders,
        stratified_orders,
        eigen_summary,
        coupled_summary,
    )
    with open(
        os.path.join(args.output_dir, "active_boundary_report.txt"),
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(report)
    print(report)

    analysis_manifest = {
        "analysis": "AIEF active-boundary directional-field diagnostics",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "source_manifest_path": str(Path(args.manifest).resolve()),
        "source_manifest_sha256": file_sha256(args.manifest),
        "methods_path": str(Path(args.methods).resolve()),
        "methods_sha256": file_sha256(args.methods),
        "comparisons_path": str(Path(args.comparisons).resolve()),
        "comparisons_sha256": file_sha256(args.comparisons),
        "boundary_dt": args.boundary_dt,
        "edge_epsilons": args.edge_eps,
        "margin_epsilons": args.margin_eps,
        "max_seeds": args.max_seeds,
        "boundary_tolerance": args.boundary_tol,
        "ideal_boundary_field": "V_e = clipped_F_e - w_e * max(alpha_i, alpha_j)",
        "notes": [
            "Ideal map excludes the fixed denominator safeguard.",
            "Current implementation safeguard has a different formal dt->0 limit.",
            "Interior p≈2 does not prove active-boundary equivalence.",
            "Optimal beta is a local scalar calibration, not a global model fit.",
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
