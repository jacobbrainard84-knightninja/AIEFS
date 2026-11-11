#!/usr/bin/env python3
"""Local one-step comparison of AIEF admissibility and entropy-dual updates.

For stored AIEF-1.4 split states, this script compares:

1. The actual AIEF positivity clip + symmetric row-cap admissibility map.
2. A coordinate-equivalent dual Euler step:
       psi+ = psi + dt * H(w) F(w)
3. A mirror-preconditioned dual Euler step:
       psi+ = psi + dt * F(w) / beta

All methods start from the same explicitly interiorized symmetric edge state.
The comparison is swept over timestep, edge floor, node-margin floor, and
mirror metric scale beta.

This is a local diagnostic, not an AIEF-1.5 simulator. The entropy-dual update
is a new vector field unless the H(w) factor is included.
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
DEFAULT_OUTPUT_DIR = "aief_1_4_local_update_comparison"
# Boundary Hessians are extremely stiff; include timesteps small enough to
# enter the asymptotic regime of the coordinate-equivalent dual Euler step.
DEFAULT_DT = "0.01,0.001,0.0001,0.00001,0.000001"
DEFAULT_EDGE_EPS = "1e-4,1e-5,1e-6"
DEFAULT_MARGIN_EPS = "1e-4,1e-5,1e-6"
DEFAULT_BETA = "0.1,1,10"
DEFAULT_MAX_SEEDS = 5
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
    edge_count = len(edges[0])
    A = np.zeros((node_count, edge_count), dtype=float)
    A[edges[0], np.arange(edge_count)] = 1.0
    A[edges[1], np.arange(edge_count)] = 1.0
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


def interiorize(
    w: np.ndarray,
    A: np.ndarray,
    capacities: np.ndarray,
    edge_epsilon: float,
    margin_epsilon: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    degrees = np.sum(A, axis=1)
    available = capacities - margin_epsilon - degrees * edge_epsilon
    if np.any(available <= 0.0):
        raise ValueError("infeasible epsilon pair")
    row_mass = A @ w
    ratios = np.full(len(capacities), np.inf)
    positive = row_mass > 0.0
    ratios[positive] = available[positive] / row_mass[positive]
    alpha = float(min(1.0, np.min(ratios)))
    w_interior = edge_epsilon + alpha * w
    margins = capacities - A @ w_interior
    if np.any(w_interior <= 0.0) or np.any(margins <= 0.0):
        raise RuntimeError("failed to interiorize")
    return w_interior, margins, alpha


def entropy_gradient(w: np.ndarray, margins: np.ndarray, A: np.ndarray) -> np.ndarray:
    return np.log(w) - A.T @ np.log(margins)


def entropy_hessian(w: np.ndarray, margins: np.ndarray, A: np.ndarray) -> np.ndarray:
    return np.diag(1.0 / w) + A.T @ np.diag(1.0 / margins) @ A


def inverse_from_psi(
    psi: np.ndarray,
    capacities: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    initial_margins: np.ndarray,
    *,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> tuple[np.ndarray, np.ndarray, int, float, bool]:
    """Invert psi using Newton on the strictly convex log-margin objective."""
    if np.any(~np.isfinite(psi)) or np.max(psi) > 700.0:
        raise FloatingPointError("dual coordinate overflow")
    z_edges = np.exp(psi)
    node_count = len(capacities)
    Z = np.zeros((node_count, node_count), dtype=float)
    Z[edges] = z_edges
    Z[(edges[1], edges[0])] = z_edges

    y = np.log(np.maximum(initial_margins, np.finfo(float).tiny))

    def objective(y_value: np.ndarray) -> float:
        if np.any(~np.isfinite(y_value)) or np.max(y_value) > 700.0:
            return np.inf
        with np.errstate(over="ignore", invalid="ignore"):
            m = np.exp(y_value)
            value = np.sum(m) + 0.5 * m @ Z @ m - capacities @ y_value
        return float(value) if np.isfinite(value) else np.inf

    def gradient_hessian(y_value: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        m = np.exp(y_value)
        Zm = Z @ m
        gradient = m * (1.0 + Zm) - capacities
        hessian = np.diag(m * (1.0 + Zm)) + np.diag(m) @ Z @ np.diag(m)
        return gradient, hessian

    value = objective(y)
    for iteration in range(max_iterations + 1):
        gradient, hessian = gradient_hessian(y)
        residual = float(np.linalg.norm(gradient, ord=np.inf))
        if residual <= tolerance:
            margins = np.exp(y)
            w = z_edges * margins[edges[0]] * margins[edges[1]]
            return w, margins, iteration, residual, True
        if iteration == max_iterations:
            break
        step = np.linalg.solve(hessian, -gradient)
        damping = 1.0
        accepted = False
        while damping >= 2.0**-30:
            candidate = y + damping * step
            candidate_value = objective(candidate)
            if np.isfinite(candidate_value):
                candidate_gradient, _ = gradient_hessian(candidate)
                candidate_residual = float(
                    np.linalg.norm(candidate_gradient, ord=np.inf)
                )
                # Residual decrease is more robust than objective Armijo when
                # psi+ is extremely close to psi and objective differences are
                # at floating-point resolution.
                if (
                    candidate_residual <= tolerance
                    or candidate_residual < residual * (1.0 - 1e-4 * damping)
                ):
                    y = candidate
                    value = candidate_value
                    accepted = True
                    break
            damping *= 0.5
        if not accepted:
            break

    margins = np.exp(y)
    w = z_edges * margins[edges[0]] * margins[edges[1]]
    gradient, _ = gradient_hessian(y)
    return w, margins, max_iterations, float(np.linalg.norm(gradient, ord=np.inf)), False


def compute_resonance_and_field(
    *,
    theta: np.ndarray,
    delayed_theta: np.ndarray,
    coherence_acc: np.ndarray,
    omega: np.ndarray,
    B: np.ndarray,
    dt: float,
    tau: float,
    t_window: float,
    eta: float,
    mu: float,
    gamma: float,
) -> tuple[np.ndarray, np.ndarray]:
    dphi = (
        theta[:, None]
        - delayed_theta[None, :]
        - ((omega[:, None] + omega[None, :]) / 2.0) * tau
    )
    z_inst = np.exp(1j * dphi)
    alpha = float(np.exp(-dt / t_window))
    updated_acc = alpha * coherence_acc + (1.0 - alpha) * z_inst
    R = np.abs(updated_acc)
    R = 0.5 * (R + R.T)
    np.fill_diagonal(R, 0.0)
    F = (eta + mu) * R - mu - gamma * B
    F = 0.5 * (F + F.T)
    np.fill_diagonal(F, 0.0)
    return R, F


def actual_aief_step(
    w: np.ndarray,
    F: np.ndarray,
    dt: float,
    capacities: np.ndarray,
    A: np.ndarray,
    node_count: int,
    edges: tuple[np.ndarray, np.ndarray],
) -> tuple[np.ndarray, dict[str, Any]]:
    B = vector_to_matrix(w, node_count, edges)
    proposal = B + dt * F
    proposal = np.maximum(proposal, 0.0)
    proposal = 0.5 * (proposal + proposal.T)
    np.fill_diagonal(proposal, 0.0)
    proposal_w = proposal[edges]
    pre_slack = capacities - A @ proposal_w
    active_nodes = pre_slack < 0.0

    projected = proposal.copy()
    if np.any(active_nodes):
        row_sum = np.sum(proposal, axis=1)
        scale = np.minimum(1.0, capacities / (row_sum + 1e-12))
        projected *= np.minimum.outer(scale, scale)
        np.fill_diagonal(projected, 0.0)
    next_w = projected[edges]
    return next_w, {
        "positivity_clipped_edges": int(np.sum((w + dt * F[edges]) < 0.0)),
        "active_capacity_nodes": int(np.sum(active_nodes)),
        "proposal_increment_norm": float(np.linalg.norm(proposal_w - w)),
        "projection_correction_norm": float(np.linalg.norm(next_w - proposal_w)),
    }


def rank_correlation(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3:
        return np.nan
    xr = pd.Series(x).rank(method="average").to_numpy(float)
    yr = pd.Series(y).rank(method="average").to_numpy(float)
    if np.std(xr) <= ZERO_TOL or np.std(yr) <= ZERO_TOL:
        return np.nan
    return float(np.corrcoef(xr, yr)[0, 1])


def jaccard_threshold(x: np.ndarray, y: np.ndarray, threshold: float) -> float:
    xs = x > threshold
    ys = y > threshold
    union = np.sum(xs | ys)
    return float(np.sum(xs & ys) / union) if union else np.nan


def top_k_overlap(x: np.ndarray, y: np.ndarray, k: int) -> float:
    if k <= 0:
        return np.nan
    ix = set(np.argpartition(x, -k)[-k:])
    iy = set(np.argpartition(y, -k)[-k:])
    return float(len(ix & iy) / k)


def method_row(
    *,
    seed: str,
    method: str,
    beta: float | None,
    dt: float,
    edge_epsilon: float,
    margin_epsilon: float,
    alpha: float,
    w: np.ndarray,
    next_w: np.ndarray,
    capacities: np.ndarray,
    A: np.ndarray,
    threshold: float,
    status: str,
    solver_iterations: int | None = None,
    solver_residual: float | None = None,
    solver_converged: bool | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    increment = next_w - w
    margins = capacities - A @ next_w
    selected_count = int(np.sum(w > threshold))
    row = {
        "seed": seed,
        "method": method,
        "beta": beta,
        "dt": dt,
        "edge_epsilon": edge_epsilon,
        "margin_epsilon": margin_epsilon,
        "interiorization_alpha": alpha,
        "status": status,
        "increment_norm": float(np.linalg.norm(increment)),
        "increment_rate_norm": float(np.linalg.norm(increment) / dt),
        "minimum_next_edge": float(np.min(next_w)),
        "minimum_next_margin": float(np.min(margins)),
        "negative_edge_count": int(np.sum(next_w < 0.0)),
        "capacity_violation_count": int(np.sum(margins < -1e-10)),
        "threshold_selected_count": int(np.sum(next_w > threshold)),
        "threshold_jaccard_with_start": jaccard_threshold(w, next_w, threshold),
        "top_k_overlap_with_start": top_k_overlap(w, next_w, selected_count),
        "edge_rank_correlation_with_start": rank_correlation(w, next_w),
        "solver_iterations": solver_iterations,
        "solver_residual": solver_residual,
        "solver_converged": solver_converged,
    }
    if extra:
        row.update(extra)
    return row


def compare_increments(
    left: np.ndarray,
    right: np.ndarray,
    dt: float,
) -> dict[str, float]:
    difference = left - right
    left_norm = float(np.linalg.norm(left))
    right_norm = float(np.linalg.norm(right))
    denominator = left_norm * right_norm
    cosine = (
        float(left @ right / denominator)
        if np.isfinite(denominator) and denominator > np.finfo(float).tiny
        else np.nan
    )
    return {
        "increment_discrepancy_norm": float(np.linalg.norm(difference)),
        "discrepancy_rate_norm": float(np.linalg.norm(difference) / dt),
        "discrepancy_over_dt_squared": float(np.linalg.norm(difference) / (dt**2)),
        "relative_discrepancy_to_left": float(
            np.linalg.norm(difference) / max(left_norm, ZERO_TOL)
        ),
        "increment_cosine": cosine,
    }


def run_comparison(
    scalar: pd.DataFrame,
    npz_path: str,
    manifest: dict[str, Any],
    dt_values: Iterable[float],
    edge_eps_values: Iterable[float],
    margin_eps_values: Iterable[float],
    beta_values: Iterable[float],
    max_seeds: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    model = manifest["model"]
    node_count = int(model["N"])
    omega = np.asarray(model["omega"], dtype=float)
    tau = float(model["tau"])
    t_window = float(model["T_window"])
    eta = float(model["eta"])
    mu = float(model["mu"])
    gamma = float(model["gamma"])
    threshold = float(model["B_c"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(node_count, capacity)
    A, edges = incidence_matrix(node_count)

    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    if max_seeds > 0:
        seeds = seeds[:max_seeds]

    method_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []

    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            B_split = np.asarray(data[prefix_key(seed, "B_at_split")], dtype=float)
            theta = np.asarray(data[prefix_key(seed, "theta_at_split")], dtype=float)
            coherence = np.asarray(
                data[prefix_key(seed, "coherence_acc_at_split")]
            )
            history = np.asarray(data[prefix_key(seed, "history_at_split")], dtype=float)
            delayed = history[0]
            raw_w = B_split[edges]

            for edge_epsilon in edge_eps_values:
                for margin_epsilon in margin_eps_values:
                    try:
                        w, margins, alpha = interiorize(
                            raw_w,
                            A,
                            capacities,
                            edge_epsilon,
                            margin_epsilon,
                        )
                    except Exception as exc:
                        method_rows.append(
                            {
                                "seed": seed,
                                "method": "interiorization",
                                "dt": np.nan,
                                "edge_epsilon": edge_epsilon,
                                "margin_epsilon": margin_epsilon,
                                "status": f"failed:{type(exc).__name__}:{exc}",
                            }
                        )
                        continue

                    B_interior = vector_to_matrix(w, node_count, edges)
                    psi = entropy_gradient(w, margins, A)
                    H = entropy_hessian(w, margins, A)
                    hessian_eigenvalues = np.linalg.eigvalsh(H)
                    hessian_condition = float(
                        hessian_eigenvalues[-1] / hessian_eigenvalues[0]
                    )

                    for dt in dt_values:
                        _, F_matrix = compute_resonance_and_field(
                            theta=theta,
                            delayed_theta=delayed,
                            coherence_acc=coherence,
                            omega=omega,
                            B=B_interior,
                            dt=dt,
                            tau=tau,
                            t_window=t_window,
                            eta=eta,
                            mu=mu,
                            gamma=gamma,
                        )
                        F = F_matrix[edges]

                        current_w, current_extra = actual_aief_step(
                            w,
                            F_matrix,
                            dt,
                            capacities,
                            A,
                            node_count,
                            edges,
                        )
                        method_rows.append(
                            method_row(
                                seed=seed,
                                method="current_admissibility",
                                beta=None,
                                dt=dt,
                                edge_epsilon=edge_epsilon,
                                margin_epsilon=margin_epsilon,
                                alpha=alpha,
                                w=w,
                                next_w=current_w,
                                capacities=capacities,
                                A=A,
                                threshold=threshold,
                                status="ok",
                                extra={
                                    **current_extra,
                                    "hessian_condition_number": hessian_condition,
                                    "field_norm": float(np.linalg.norm(F)),
                                },
                            )
                        )

                        method_next: dict[str, np.ndarray] = {
                            "current_admissibility": current_w
                        }

                        # Coordinate-equivalent dual Euler.
                        try:
                            coord_psi = psi + dt * (H @ F)
                            coord_w, _, iterations, residual, converged = inverse_from_psi(
                                coord_psi,
                                capacities,
                                edges,
                                margins,
                            )
                            status = "ok" if converged else "solver_not_converged"
                            method_rows.append(
                                method_row(
                                    seed=seed,
                                    method="coordinate_equivalent_dual",
                                    beta=None,
                                    dt=dt,
                                    edge_epsilon=edge_epsilon,
                                    margin_epsilon=margin_epsilon,
                                    alpha=alpha,
                                    w=w,
                                    next_w=coord_w,
                                    capacities=capacities,
                                    A=A,
                                    threshold=threshold,
                                    status=status,
                                    solver_iterations=iterations,
                                    solver_residual=residual,
                                    solver_converged=converged,
                                    extra={
                                        "hessian_condition_number": hessian_condition,
                                        "field_norm": float(np.linalg.norm(F)),
                                    },
                                )
                            )
                            if converged:
                                method_next["coordinate_equivalent_dual"] = coord_w
                        except Exception as exc:
                            method_rows.append(
                                {
                                    "seed": seed,
                                    "method": "coordinate_equivalent_dual",
                                    "beta": np.nan,
                                    "dt": dt,
                                    "edge_epsilon": edge_epsilon,
                                    "margin_epsilon": margin_epsilon,
                                    "interiorization_alpha": alpha,
                                    "status": f"failed:{type(exc).__name__}:{exc}",
                                    "hessian_condition_number": hessian_condition,
                                }
                            )

                        # Mirror-preconditioned dual Euler for each beta.
                        for beta in beta_values:
                            method_name = f"mirror_beta_{beta:g}"
                            try:
                                mirror_psi = psi + dt * F / beta
                                mirror_w, _, iterations, residual, converged = inverse_from_psi(
                                    mirror_psi,
                                    capacities,
                                    edges,
                                    margins,
                                )
                                status = "ok" if converged else "solver_not_converged"
                                method_rows.append(
                                    method_row(
                                        seed=seed,
                                        method=method_name,
                                        beta=beta,
                                        dt=dt,
                                        edge_epsilon=edge_epsilon,
                                        margin_epsilon=margin_epsilon,
                                        alpha=alpha,
                                        w=w,
                                        next_w=mirror_w,
                                        capacities=capacities,
                                        A=A,
                                        threshold=threshold,
                                        status=status,
                                        solver_iterations=iterations,
                                        solver_residual=residual,
                                        solver_converged=converged,
                                        extra={
                                            "hessian_condition_number": hessian_condition,
                                            "field_norm": float(np.linalg.norm(F)),
                                        },
                                    )
                                )
                                if converged:
                                    method_next[method_name] = mirror_w
                            except Exception as exc:
                                method_rows.append(
                                    {
                                        "seed": seed,
                                        "method": method_name,
                                        "beta": beta,
                                        "dt": dt,
                                        "edge_epsilon": edge_epsilon,
                                        "margin_epsilon": margin_epsilon,
                                        "interiorization_alpha": alpha,
                                        "status": f"failed:{type(exc).__name__}:{exc}",
                                        "hessian_condition_number": hessian_condition,
                                    }
                                )

                        # Pairwise increment comparisons.
                        comparison_pairs = []
                        if "coordinate_equivalent_dual" in method_next:
                            comparison_pairs.append(
                                ("current_admissibility", "coordinate_equivalent_dual")
                            )
                        for beta in beta_values:
                            mirror_name = f"mirror_beta_{beta:g}"
                            if mirror_name in method_next:
                                comparison_pairs.append(
                                    ("current_admissibility", mirror_name)
                                )
                                if "coordinate_equivalent_dual" in method_next:
                                    comparison_pairs.append(
                                        ("coordinate_equivalent_dual", mirror_name)
                                    )

                        for left_name, right_name in comparison_pairs:
                            left_increment = method_next[left_name] - w
                            right_increment = method_next[right_name] - w
                            metrics = compare_increments(
                                left_increment, right_increment, dt
                            )
                            comparison_rows.append(
                                {
                                    "seed": seed,
                                    "left_method": left_name,
                                    "right_method": right_name,
                                    "dt": dt,
                                    "edge_epsilon": edge_epsilon,
                                    "margin_epsilon": margin_epsilon,
                                    "hessian_condition_number": hessian_condition,
                                    **metrics,
                                    "next_threshold_jaccard": jaccard_threshold(
                                        method_next[left_name],
                                        method_next[right_name],
                                        threshold,
                                    ),
                                    "next_rank_correlation": rank_correlation(
                                        method_next[left_name],
                                        method_next[right_name],
                                    ),
                                }
                            )

    return pd.DataFrame(method_rows), pd.DataFrame(comparison_rows)


def convergence_orders(comparisons: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_columns = [
        "seed",
        "left_method",
        "right_method",
        "edge_epsilon",
        "margin_epsilon",
    ]
    for group_key, group in comparisons.groupby(group_columns):
        group = group.sort_values("dt")
        dt = group["dt"].to_numpy(float)
        discrepancy = group["increment_discrepancy_norm"].to_numpy(float)
        valid = (dt > 0.0) & (discrepancy > 0.0) & np.isfinite(discrepancy)
        if np.sum(valid) >= 2:
            valid_dt = dt[valid]
            valid_discrepancy = discrepancy[valid]
            order = np.argsort(valid_dt)
            # Estimate local order from at most the three smallest timesteps;
            # larger steps can be far outside the asymptotic regime.
            use = order[: min(3, len(order))]
            slope, intercept = np.polyfit(
                np.log(valid_dt[use]), np.log(valid_discrepancy[use]), 1
            )
        else:
            slope = intercept = np.nan
        rows.append(
            {
                **dict(zip(group_columns, group_key)),
                "n_dt": int(np.sum(valid)),
                "n_dt_fit": int(min(3, np.sum(valid))),
                "increment_discrepancy_order": float(slope),
                "log_intercept": float(intercept),
                "smallest_dt": float(np.min(dt)) if len(dt) else np.nan,
                "smallest_dt_discrepancy_rate": float(
                    group.loc[group["dt"].idxmin(), "discrepancy_rate_norm"]
                )
                if len(group)
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


def summarize_table(
    frame: pd.DataFrame,
    group_columns: list[str],
    metrics: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for group_key, group in frame.groupby(group_columns, dropna=False):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        base = dict(zip(group_columns, group_key))
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
    methods: pd.DataFrame,
    comparison_summary: pd.DataFrame,
    order_summary: pd.DataFrame,
) -> str:
    lines = [
        "AIEF local admissibility versus entropy-dual one-step comparison",
        "================================================================",
        "",
        "All methods start from the same explicitly interiorized mature state.",
        "Coordinate-equivalent and mirror dual updates are distinct constructions.",
        "",
        "Solver status",
        "-------------",
    ]
    status = (
        methods.groupby(["method", "status"], dropna=False)
        .size()
        .reset_index(name="count")
    )
    for _, row in status.iterrows():
        lines.append(
            f"  {row['method']} / {row['status']}: {int(row['count'])}"
        )

    lines.extend(["", "Selected comparison summaries", "-----------------------------"])
    edge_values = sorted(comparison_summary["edge_epsilon"].dropna().unique())
    margin_values = sorted(comparison_summary["margin_epsilon"].dropna().unique())
    representative_edge = edge_values[len(edge_values) // 2]
    representative_margin = margin_values[len(margin_values) // 2]
    selected_pairs = {
        ("current_admissibility", "coordinate_equivalent_dual"),
        ("current_admissibility", "mirror_beta_1"),
    }
    pair_mask = comparison_summary.apply(
        lambda row: (row["left_method"], row["right_method"]) in selected_pairs,
        axis=1,
    )
    selected = comparison_summary.loc[
        pair_mask
        & (comparison_summary["edge_epsilon"] == representative_edge)
        & (comparison_summary["margin_epsilon"] == representative_margin)
        & comparison_summary["metric"].isin(
            [
                "increment_discrepancy_norm",
                "discrepancy_rate_norm",
                "relative_discrepancy_to_left",
                "increment_cosine",
            ]
        )
    ]
    lines.append(
        f"  representative interiorization: edge_eps={representative_edge:g}, "
        f"margin_eps={representative_margin:g}"
    )
    for (left, right, edge_eps, margin_eps, dt), group in selected.groupby(
        [
            "left_method",
            "right_method",
            "edge_epsilon",
            "margin_epsilon",
            "dt",
        ]
    ):
        lines.append(
            f"  {left} vs {right}; edge_eps={edge_eps:g}, "
            f"margin_eps={margin_eps:g}, dt={dt:g}"
        )
        for _, row in group.iterrows():
            lines.append(
                f"    {row['metric']}: median={row['median']:.6g}, "
                f"max={row['maximum']:.6g}, valid={int(row['n_valid'])}/{int(row['n_total'])}"
            )

    lines.extend(["", "Estimated discrepancy orders", "----------------------------"])
    order_rows = order_summary.loc[
        order_summary["metric"] == "increment_discrepancy_order"
    ]
    for (left, right), group in order_rows.groupby(
        ["left_method", "right_method"]
    ):
        # Each row is already a seed-aggregated epsilon-specific summary.
        values = group["median"].to_numpy(float)
        values = values[np.isfinite(values)]
        lines.append(
            f"  {left} vs {right}: median order="
            f"{np.median(values):.6g}, valid_epsilon_pairs={len(values)}"
            if len(values)
            else f"  {left} vs {right}: no valid order estimates"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* O(dt^2) increment discrepancy indicates first-order consistency.",
            "* O(dt) increment discrepancy indicates different limiting vector fields.",
            "* Results depend jointly on timestep, edge floor, margin floor, and beta.",
            "* The actual AIEF admissibility map is used; it is not assumed to be an orthogonal projection.",
            "* Mirror_beta updates define metric-preconditioned dynamics, not coordinate changes.",
            "* This is a one-step local comparison, not evidence of long-time attractor equivalence.",
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
    parser.add_argument("--dt", type=parse_float_list, default=parse_float_list(DEFAULT_DT))
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
    parser.add_argument(
        "--beta", type=parse_float_list, default=parse_float_list(DEFAULT_BETA)
    )
    parser.add_argument(
        "--max-seeds",
        type=int,
        default=DEFAULT_MAX_SEEDS,
        help="representative seeds to analyze; 0 means all (default: 5)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.scalar, args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if args.max_seeds < 0:
        raise ValueError("max-seeds must be nonnegative")
    os.makedirs(args.output_dir, exist_ok=True)

    scalar = pd.read_csv(args.scalar, dtype={"seed": str})
    scalar["seed"] = scalar["seed"].astype(str)
    scalar["branch"] = scalar["branch"].astype(str)
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    methods, comparisons = run_comparison(
        scalar,
        args.npz,
        manifest,
        args.dt,
        args.edge_eps,
        args.margin_eps,
        args.beta,
        args.max_seeds,
    )
    orders = convergence_orders(comparisons)

    method_summary = summarize_table(
        methods,
        ["method", "beta", "edge_epsilon", "margin_epsilon", "dt"],
        [
            "increment_norm",
            "increment_rate_norm",
            "minimum_next_edge",
            "minimum_next_margin",
            "threshold_selected_count",
            "threshold_jaccard_with_start",
            "top_k_overlap_with_start",
            "edge_rank_correlation_with_start",
            "solver_iterations",
            "solver_residual",
            "hessian_condition_number",
            "field_norm",
            "proposal_increment_norm",
            "projection_correction_norm",
        ],
    )
    comparison_summary = summarize_table(
        comparisons,
        [
            "left_method",
            "right_method",
            "edge_epsilon",
            "margin_epsilon",
            "dt",
        ],
        [
            "increment_discrepancy_norm",
            "discrepancy_rate_norm",
            "discrepancy_over_dt_squared",
            "relative_discrepancy_to_left",
            "increment_cosine",
            "next_threshold_jaccard",
            "next_rank_correlation",
        ],
    )
    order_summary = summarize_table(
        orders,
        ["left_method", "right_method", "edge_epsilon", "margin_epsilon"],
        ["increment_discrepancy_order", "smallest_dt_discrepancy_rate"],
    )

    outputs = {
        "one_step_methods_by_seed.csv": methods,
        "one_step_method_summary.csv": method_summary,
        "one_step_comparisons_by_seed.csv": comparisons,
        "one_step_comparison_summary.csv": comparison_summary,
        "one_step_convergence_orders_by_seed.csv": orders,
        "one_step_convergence_order_summary.csv": order_summary,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)

    report = make_report(methods, comparison_summary, order_summary)
    with open(
        os.path.join(args.output_dir, "local_update_comparison_report.txt"),
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(report)
    print(report)

    analysis_manifest = {
        "analysis": "AIEF local current/coordinate/mirror one-step comparison",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "source_manifest_path": str(Path(args.manifest).resolve()),
        "source_manifest_sha256": file_sha256(args.manifest),
        "dt_values": args.dt,
        "edge_epsilons": args.edge_eps,
        "margin_epsilons": args.margin_eps,
        "beta_values": args.beta,
        "max_seeds": args.max_seeds,
        "methods": [
            "current_admissibility",
            "coordinate_equivalent_dual",
            "mirror_beta_*",
        ],
        "notes": [
            "All comparisons start from the same interiorized split state.",
            "Current AIEF map is positivity clipping plus symmetric row scaling.",
            "Coordinate-equivalent dual Euler uses psi += dt * H(w)F.",
            "Mirror Euler uses psi += dt * F / beta and changes the vector field.",
            "No long-time mirror simulation is performed.",
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
