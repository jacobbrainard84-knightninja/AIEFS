#!/usr/bin/env python3
"""Entropy-geometry diagnostics on frozen AIEF-1.4 states.

This script does not modify the simulator. It studies the symmetry-coupled
polytope of unique undirected edge weights

    C = {w >= 0 : A w <= c},

where A is the unsigned node-edge incidence matrix. For interior states it uses

    h(w) = sum_e w_e(log w_e - 1)
         + sum_i m_i(log m_i - 1),   m = c - A w.

The script:
* audits exact-zero edges and node-capacity slacks;
* interiorizes boundary states over an epsilon grid;
* computes Hessian spectra and Woodbury inverse checks;
* verifies the coupled inverse-margin map numerically;
* measures local Hessian norms and symmetrized Bregman divergences between
  split, continuation, and intervention topologies.

These are analysis diagnostics. The Hessian norm is local and the Bregman
divergence is not claimed to be a Riemannian geodesic distance.
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
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_SCALAR = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_scalar_summary.csv"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_entropy_geometry"
DEFAULT_EDGE_EPS = "1e-12,1e-9,1e-6,1e-4"
DEFAULT_MARGIN_EPS = "1e-12,1e-9,1e-6,1e-4"
ZERO_TOL = 1e-14

BRANCHES = (
    "continue",
    "reset_ema",
    "reset_B",
    "reset_B_ema",
    "B_carrier_only",
    "full_reset",
    "future_shuffle",
)

GEOMETRY_COMPARISONS = (
    ("B_mean_late", "continue_late_mean"),
    ("B_mean_late", "split"),
    ("B_final", "continue_final"),
    ("B_final", "split"),
)


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_float_list(value: str) -> list[float]:
    try:
        result = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated floats") from exc
    if not result or any(item <= 0.0 for item in result):
        raise argparse.ArgumentTypeError("epsilon values must be positive")
    return sorted(set(result))


def npz_key(branch: str, seed: str, metric: str) -> str:
    return f"{branch}_seed_{seed}_{metric}"


def prefix_key(seed: str, metric: str) -> str:
    return f"prefix_seed_{seed}_{metric}"


def incidence_matrix(node_count: int) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray]]:
    edges = np.triu_indices(node_count, k=1)
    edge_count = len(edges[0])
    incidence = np.zeros((node_count, edge_count), dtype=float)
    incidence[edges[0], np.arange(edge_count)] = 1.0
    incidence[edges[1], np.arange(edge_count)] = 1.0
    return incidence, edges


def edge_vector(B: np.ndarray, edges: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    B = np.asarray(B, dtype=float)
    if B.ndim != 2 or B.shape[0] != B.shape[1]:
        raise ValueError("expected square B matrix")
    if not np.all(np.isfinite(B)):
        raise ValueError("B contains nonfinite values")
    if not np.allclose(B, B.T, rtol=0.0, atol=1e-10):
        raise ValueError("B is asymmetric")
    return B[edges].copy()


def interiorize(
    w: np.ndarray,
    A: np.ndarray,
    capacities: np.ndarray,
    edge_epsilon: float,
    margin_epsilon: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Map a feasible boundary state to a strict interior approximation.

    Uses w_eps = edge_epsilon * 1 + alpha * w with the largest alpha <= 1
    that leaves at least margin_epsilon slack at every node.
    """
    w = np.asarray(w, dtype=float)
    degrees = np.sum(A, axis=1)
    remaining_after_floor = capacities - margin_epsilon - degrees * edge_epsilon
    if np.any(remaining_after_floor <= 0.0):
        raise ValueError(
            "edge/margin epsilons are infeasible for the node capacities"
        )

    row_mass = A @ w
    ratios = np.full(len(capacities), np.inf, dtype=float)
    positive = row_mass > 0.0
    ratios[positive] = remaining_after_floor[positive] / row_mass[positive]
    alpha = float(min(1.0, np.min(ratios)))
    if alpha < 0.0:
        raise ValueError("interiorization produced a negative scale")

    w_interior = edge_epsilon + alpha * w
    margins = capacities - A @ w_interior
    if np.any(w_interior <= 0.0) or np.any(margins <= 0.0):
        raise RuntimeError("interiorization failed to reach the strict interior")
    if np.min(margins) < margin_epsilon - 1e-12:
        raise RuntimeError("interiorization failed the requested margin floor")
    return w_interior, margins, alpha


def entropy_value(w: np.ndarray, margins: np.ndarray) -> float:
    return float(
        np.sum(w * (np.log(w) - 1.0))
        + np.sum(margins * (np.log(margins) - 1.0))
    )


def entropy_gradient(w: np.ndarray, margins: np.ndarray, A: np.ndarray) -> np.ndarray:
    return np.log(w) - A.T @ np.log(margins)


def entropy_hessian(w: np.ndarray, margins: np.ndarray, A: np.ndarray) -> np.ndarray:
    return np.diag(1.0 / w) + A.T @ np.diag(1.0 / margins) @ A


def woodbury_inverse(w: np.ndarray, margins: np.ndarray, A: np.ndarray) -> np.ndarray:
    D_w = np.diag(w)
    middle = np.diag(margins) + A @ D_w @ A.T
    return D_w - D_w @ A.T @ np.linalg.solve(middle, A @ D_w)


def bregman_divergence(
    x: np.ndarray,
    margins_x: np.ndarray,
    y: np.ndarray,
    margins_y: np.ndarray,
    A: np.ndarray,
) -> float:
    return float(
        entropy_value(x, margins_x)
        - entropy_value(y, margins_y)
        - entropy_gradient(y, margins_y, A) @ (x - y)
    )


def inverse_margins_newton(
    z_matrix: np.ndarray,
    capacities: np.ndarray,
    *,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> tuple[np.ndarray, int, float, bool]:
    """Solve m_i * (1 + sum_j z_ij m_j) = c_i by damped Newton."""
    node_count = len(capacities)
    margins = 0.5 * capacities.copy()

    def residual(m: np.ndarray) -> np.ndarray:
        return m * (1.0 + z_matrix @ m) - capacities

    current = residual(margins)
    current_norm = float(np.linalg.norm(current, ord=np.inf))
    for iteration in range(1, max_iterations + 1):
        if current_norm <= tolerance:
            return margins, iteration - 1, current_norm, True
        zm = z_matrix @ margins
        jacobian = np.diag(1.0 + zm) + np.diag(margins) @ z_matrix
        step = np.linalg.solve(jacobian, -current)

        damping = 1.0
        accepted = False
        while damping >= 2.0**-30:
            candidate = margins + damping * step
            if np.all(candidate > 0.0):
                candidate_residual = residual(candidate)
                candidate_norm = float(
                    np.linalg.norm(candidate_residual, ord=np.inf)
                )
                if candidate_norm < current_norm:
                    margins = candidate
                    current = candidate_residual
                    current_norm = candidate_norm
                    accepted = True
                    break
            damping *= 0.5
        if not accepted:
            return margins, iteration, current_norm, False

    return margins, max_iterations, current_norm, current_norm <= tolerance


def inverse_map_verification(
    w: np.ndarray,
    margins: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    capacities: np.ndarray,
) -> dict[str, float | int | bool]:
    psi = np.log(w) - (
        np.log(margins[edges[0]]) + np.log(margins[edges[1]])
    )
    z_edges = np.exp(psi)
    z_matrix = np.zeros((len(capacities), len(capacities)), dtype=float)
    z_matrix[edges] = z_edges
    z_matrix[(edges[1], edges[0])] = z_edges

    recovered_margins, iterations, residual, converged = inverse_margins_newton(
        z_matrix, capacities
    )
    recovered_w = (
        z_edges
        * recovered_margins[edges[0]]
        * recovered_margins[edges[1]]
    )
    return {
        "inverse_converged": bool(converged),
        "inverse_iterations": int(iterations),
        "inverse_residual_inf": float(residual),
        "margin_reconstruction_relative_error": float(
            np.linalg.norm(recovered_margins - margins)
            / max(np.linalg.norm(margins), ZERO_TOL)
        ),
        "edge_reconstruction_relative_error": float(
            np.linalg.norm(recovered_w - w) / max(np.linalg.norm(w), ZERO_TOL)
        ),
    }


def hessian_diagnostics(
    w: np.ndarray,
    margins: np.ndarray,
    A: np.ndarray,
) -> dict[str, float]:
    H = entropy_hessian(w, margins, A)
    eigenvalues = np.linalg.eigvalsh(H)
    H_inverse_direct = np.linalg.inv(H)
    H_inverse_woodbury = woodbury_inverse(w, margins, A)
    identity_error = np.linalg.norm(H @ H_inverse_woodbury - np.eye(len(w)))
    inverse_error = np.linalg.norm(H_inverse_woodbury - H_inverse_direct) / max(
        np.linalg.norm(H_inverse_direct), ZERO_TOL
    )
    return {
        "hessian_lambda_min": float(eigenvalues[0]),
        "hessian_lambda_max": float(eigenvalues[-1]),
        "hessian_condition_number": float(eigenvalues[-1] / eigenvalues[0]),
        "inverse_metric_lambda_min": float(1.0 / eigenvalues[-1]),
        "inverse_metric_lambda_max": float(1.0 / eigenvalues[0]),
        "max_edge_curvature_1_over_w": float(np.max(1.0 / w)),
        "max_margin_curvature_1_over_m": float(np.max(1.0 / margins)),
        "woodbury_relative_inverse_error": float(inverse_error),
        "woodbury_identity_error_frobenius": float(identity_error),
    }


def load_inputs(
    scalar_path: str,
    manifest_path: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not os.path.isfile(scalar_path):
        raise FileNotFoundError(scalar_path)
    if not os.path.isfile(manifest_path):
        raise FileNotFoundError(manifest_path)
    scalar = pd.read_csv(scalar_path, dtype={"seed": str})
    scalar["seed"] = scalar["seed"].astype(str)
    scalar["branch"] = scalar["branch"].astype(str)
    if scalar.duplicated(["seed", "branch"]).any():
        raise ValueError("duplicate seed/branch rows")
    if set(scalar["branch"]) != set(BRANCHES):
        raise ValueError("unexpected branch set")
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    return scalar, manifest


def raw_boundary_audit(
    scalar: pd.DataFrame,
    npz_path: str,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    seed_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    margin_rows: list[dict[str, Any]] = []

    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            B = np.asarray(data[prefix_key(seed, "B_at_split")], dtype=float)
            w = edge_vector(B, edges)
            margins = capacities - A @ w
            positive_weights = w[w > 0.0]
            seed_rows.append(
                {
                    "seed": seed,
                    "edge_count": int(len(w)),
                    "exact_zero_edge_count": int(np.sum(w == 0.0)),
                    "exact_zero_edge_fraction": float(np.mean(w == 0.0)),
                    "minimum_positive_edge": float(np.min(positive_weights))
                    if len(positive_weights)
                    else np.nan,
                    "positive_edge_q01": float(np.quantile(positive_weights, 0.01))
                    if len(positive_weights)
                    else np.nan,
                    "positive_edge_q10": float(np.quantile(positive_weights, 0.10))
                    if len(positive_weights)
                    else np.nan,
                    "minimum_margin": float(np.min(margins)),
                    "median_margin": float(np.median(margins)),
                    "maximum_margin": float(np.max(margins)),
                    "margin_le_1e_minus_12_fraction": float(np.mean(margins <= 1e-12)),
                    "margin_le_1e_minus_9_fraction": float(np.mean(margins <= 1e-9)),
                    "margin_le_1e_minus_6_fraction": float(np.mean(margins <= 1e-6)),
                    "margin_le_1e_minus_3_fraction": float(np.mean(margins <= 1e-3)),
                }
            )
            for edge_index, value in enumerate(w):
                edge_rows.append(
                    {
                        "seed": seed,
                        "edge_index": edge_index,
                        "node_i": int(edges[0][edge_index]),
                        "node_j": int(edges[1][edge_index]),
                        "weight": float(value),
                    }
                )
            for node, value in enumerate(margins):
                margin_rows.append(
                    {
                        "seed": seed,
                        "node": node,
                        "margin": float(value),
                    }
                )
    return pd.DataFrame(seed_rows), pd.DataFrame(edge_rows), pd.DataFrame(margin_rows)


def geometry_grid(
    scalar: pd.DataFrame,
    npz_path: str,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    edge_epsilons: Iterable[float],
    margin_epsilons: Iterable[float],
) -> tuple[pd.DataFrame, dict[tuple[str, float, float], dict[str, Any]]]:
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    rows: list[dict[str, Any]] = []
    cache: dict[tuple[str, float, float], dict[str, Any]] = {}

    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            B_split = np.asarray(data[prefix_key(seed, "B_at_split")], dtype=float)
            raw = edge_vector(B_split, edges)
            for edge_epsilon in edge_epsilons:
                for margin_epsilon in margin_epsilons:
                    try:
                        w, margins, alpha = interiorize(
                            raw, A, capacities, edge_epsilon, margin_epsilon
                        )
                        diagnostics = hessian_diagnostics(w, margins, A)
                        inverse = inverse_map_verification(
                            w, margins, edges, capacities
                        )
                        status = "ok"
                    except Exception as exc:
                        w = margins = None
                        alpha = np.nan
                        diagnostics = {}
                        inverse = {}
                        status = f"failed:{type(exc).__name__}:{exc}"

                    row = {
                        "seed": seed,
                        "edge_epsilon": edge_epsilon,
                        "margin_epsilon": margin_epsilon,
                        "status": status,
                        "interiorization_alpha": alpha,
                        "minimum_interior_edge": float(np.min(w))
                        if w is not None
                        else np.nan,
                        "minimum_interior_margin": float(np.min(margins))
                        if margins is not None
                        else np.nan,
                        **diagnostics,
                        **inverse,
                    }
                    rows.append(row)
                    if w is not None and margins is not None:
                        cache[(seed, edge_epsilon, margin_epsilon)] = {
                            "w": w,
                            "margins": margins,
                            "H": entropy_hessian(w, margins, A),
                        }
    return pd.DataFrame(rows), cache


def geometry_distances(
    scalar: pd.DataFrame,
    npz_path: str,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    edge_epsilons: Iterable[float],
    margin_epsilons: Iterable[float],
) -> pd.DataFrame:
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    rows: list[dict[str, Any]] = []

    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            split_raw = edge_vector(
                np.asarray(data[prefix_key(seed, "B_at_split")], dtype=float),
                edges,
            )
            continue_late_raw = edge_vector(
                np.asarray(
                    data[npz_key("continue", seed, "B_mean_late")], dtype=float
                ),
                edges,
            )
            continue_final_raw = edge_vector(
                np.asarray(data[npz_key("continue", seed, "B_final")], dtype=float),
                edges,
            )

            for edge_epsilon in edge_epsilons:
                for margin_epsilon in margin_epsilons:
                    references: dict[str, tuple[np.ndarray, np.ndarray]] = {}
                    for name, raw in (
                        ("split", split_raw),
                        ("continue_late_mean", continue_late_raw),
                        ("continue_final", continue_final_raw),
                    ):
                        try:
                            w_ref, m_ref, _ = interiorize(
                                raw,
                                A,
                                capacities,
                                edge_epsilon,
                                margin_epsilon,
                            )
                            references[name] = (w_ref, m_ref)
                        except Exception:
                            continue

                    for branch in BRANCHES:
                        for matrix_key, reference_name in GEOMETRY_COMPARISONS:
                            if reference_name not in references:
                                continue
                            raw = edge_vector(
                                np.asarray(
                                    data[npz_key(branch, seed, matrix_key)],
                                    dtype=float,
                                ),
                                edges,
                            )
                            try:
                                x, margins_x, _ = interiorize(
                                    raw,
                                    A,
                                    capacities,
                                    edge_epsilon,
                                    margin_epsilon,
                                )
                            except Exception:
                                continue
                            y, margins_y = references[reference_name]
                            delta = x - y
                            H_y = entropy_hessian(y, margins_y, A)
                            euclidean = float(np.linalg.norm(delta))
                            local_metric_sq = float(delta @ H_y @ delta)
                            divergence_xy = bregman_divergence(
                                x, margins_x, y, margins_y, A
                            )
                            divergence_yx = bregman_divergence(
                                y, margins_y, x, margins_x, A
                            )
                            rows.append(
                                {
                                    "seed": seed,
                                    "branch": branch,
                                    "matrix_key": matrix_key,
                                    "reference": reference_name,
                                    "edge_epsilon": edge_epsilon,
                                    "margin_epsilon": margin_epsilon,
                                    "euclidean_edge_distance": euclidean,
                                    "local_metric_norm_at_reference": math.sqrt(
                                        max(local_metric_sq, 0.0)
                                    ),
                                    "bregman_branch_to_reference": divergence_xy,
                                    "bregman_reference_to_branch": divergence_yx,
                                    "symmetrized_bregman": divergence_xy
                                    + divergence_yx,
                                }
                            )
    return pd.DataFrame(rows)


def summarize_numeric_table(
    frame: pd.DataFrame,
    group_columns: list[str],
    value_columns: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for group_key, group in frame.groupby(group_columns, dropna=False):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        base = dict(zip(group_columns, group_key))
        for value_column in value_columns:
            if value_column not in group.columns:
                continue
            raw = pd.to_numeric(group[value_column], errors="coerce").to_numpy(float)
            values = raw[np.isfinite(raw)]
            rows.append(
                {
                    **base,
                    "metric": value_column,
                    "n_total": int(len(raw)),
                    "n_valid": int(len(values)),
                    "mean": float(np.mean(values)) if len(values) else np.nan,
                    "std": float(np.std(values)) if len(values) else np.nan,
                    "median": float(np.median(values)) if len(values) else np.nan,
                    "minimum": float(np.min(values)) if len(values) else np.nan,
                    "maximum": float(np.max(values)) if len(values) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def make_report(
    boundary: pd.DataFrame,
    grid_summary: pd.DataFrame,
    distance_summary: pd.DataFrame,
) -> str:
    lines = [
        "AIEF-1.4 entropy-geometry boundary and conditioning diagnostics",
        "================================================================",
        "",
        "The metric is evaluated only after explicit interiorization.",
        "Bregman divergence is not interpreted as geodesic distance.",
        "",
        "Raw mature-state boundary occupancy",
        "-----------------------------------",
        f"Seeds: {len(boundary)}",
        f"Mean exact-zero edge fraction: {boundary['exact_zero_edge_fraction'].mean():.6g}",
        f"Median minimum positive edge: {boundary['minimum_positive_edge'].median():.6g}",
        f"Median minimum node margin: {boundary['minimum_margin'].median():.6g}",
        f"Mean fraction of node margins <= 1e-12: {boundary['margin_le_1e_minus_12_fraction'].mean():.6g}",
        "",
        "Interior Hessian conditioning",
        "-----------------------------",
    ]

    selected = grid_summary.loc[
        grid_summary["metric"].isin(
            [
                "hessian_condition_number",
                "woodbury_relative_inverse_error",
                "edge_reconstruction_relative_error",
                "margin_reconstruction_relative_error",
            ]
        )
    ]
    for (edge_eps, margin_eps), group in selected.groupby(
        ["edge_epsilon", "margin_epsilon"]
    ):
        lines.append(f"  edge_eps={edge_eps:g}, margin_eps={margin_eps:g}")
        for _, row in group.iterrows():
            lines.append(
                f"    {row['metric']}: median={row['median']:.6g}, "
                f"max={row['maximum']:.6g}, valid={int(row['n_valid'])}/{int(row['n_total'])}"
            )

    lines.extend(["", "Selected intrinsic-distance diagnostics", "---------------------------------------"])
    selected_distance = distance_summary.loc[
        (distance_summary["branch"].isin(["reset_B", "reset_ema", "full_reset"]))
        & (distance_summary["matrix_key"] == "B_mean_late")
        & (distance_summary["reference"] == "continue_late_mean")
        & (distance_summary["metric"].isin(["euclidean_edge_distance", "local_metric_norm_at_reference", "symmetrized_bregman"]))
    ]
    for (branch, edge_eps, margin_eps), group in selected_distance.groupby(
        ["branch", "edge_epsilon", "margin_epsilon"]
    ):
        lines.append(
            f"  {branch}, edge_eps={edge_eps:g}, margin_eps={margin_eps:g}"
        )
        for _, row in group.iterrows():
            lines.append(
                f"    {row['metric']}: median={row['median']:.6g}, "
                f"max={row['maximum']:.6g}"
            )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* The entropy potential is a natural choice, not a uniquely canonical metric.",
            "* Metric scale and dimensional normalization remain modeling choices.",
            "* Existing AIEF states lie on the boundary; epsilon dependence is substantive.",
            "* Local metric norms are not global geodesic distances.",
            "* This script does not define mirror dynamics or claim that geometry stores memory.",
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
    parser.add_argument(
        "--edge-eps",
        type=parse_float_list,
        default=parse_float_list(DEFAULT_EDGE_EPS),
        help=f"comma-separated edge floors (default: {DEFAULT_EDGE_EPS})",
    )
    parser.add_argument(
        "--margin-eps",
        type=parse_float_list,
        default=parse_float_list(DEFAULT_MARGIN_EPS),
        help=f"comma-separated margin floors (default: {DEFAULT_MARGIN_EPS})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.scalar, args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    os.makedirs(args.output_dir, exist_ok=True)

    scalar, manifest = load_inputs(args.scalar, args.manifest)
    node_count = int(manifest["model"]["N"])
    capacity_value = (
        float(manifest["model"]["a"])
        - float(manifest["model"]["delta"])
    ) / float(manifest["model"]["q"])
    capacities = np.full(node_count, capacity_value, dtype=float)
    A, edges = incidence_matrix(node_count)

    boundary, raw_edges, raw_margins = raw_boundary_audit(
        scalar, args.npz, capacities, A, edges
    )
    grid, _ = geometry_grid(
        scalar,
        args.npz,
        capacities,
        A,
        edges,
        args.edge_eps,
        args.margin_eps,
    )
    distances = geometry_distances(
        scalar,
        args.npz,
        capacities,
        A,
        edges,
        args.edge_eps,
        args.margin_eps,
    )

    grid_summary = summarize_numeric_table(
        grid,
        ["edge_epsilon", "margin_epsilon"],
        [
            "interiorization_alpha",
            "minimum_interior_edge",
            "minimum_interior_margin",
            "hessian_lambda_min",
            "hessian_lambda_max",
            "hessian_condition_number",
            "inverse_metric_lambda_min",
            "inverse_metric_lambda_max",
            "max_edge_curvature_1_over_w",
            "max_margin_curvature_1_over_m",
            "woodbury_relative_inverse_error",
            "woodbury_identity_error_frobenius",
            "inverse_iterations",
            "inverse_residual_inf",
            "margin_reconstruction_relative_error",
            "edge_reconstruction_relative_error",
        ],
    )
    distance_summary = summarize_numeric_table(
        distances,
        ["branch", "matrix_key", "reference", "edge_epsilon", "margin_epsilon"],
        [
            "euclidean_edge_distance",
            "local_metric_norm_at_reference",
            "bregman_branch_to_reference",
            "bregman_reference_to_branch",
            "symmetrized_bregman",
        ],
    )

    outputs = {
        "boundary_occupancy_by_seed.csv": boundary,
        "raw_edge_weights.csv": raw_edges,
        "raw_node_margins.csv": raw_margins,
        "interior_geometry_by_seed.csv": grid,
        "interior_geometry_summary.csv": grid_summary,
        "intrinsic_distances_by_seed.csv": distances,
        "intrinsic_distances_summary.csv": distance_summary,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)

    report = make_report(boundary, grid_summary, distance_summary)
    report_path = os.path.join(args.output_dir, "entropy_geometry_report.txt")
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report)
    print(report)

    analysis_manifest = {
        "analysis": "AIEF-1.4 entropy geometry diagnostics",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "source_manifest_path": str(Path(args.manifest).resolve()),
        "source_manifest_sha256": file_sha256(args.manifest),
        "edge_epsilons": args.edge_eps,
        "margin_epsilons": args.margin_eps,
        "capacity": capacity_value,
        "node_count": node_count,
        "edge_count": int(A.shape[1]),
        "potential": "sum w(log w-1) + sum m(log m-1), m=c-Aw",
        "notes": [
            "The potential is natural but not uniquely canonical.",
            "Raw AIEF states are on the boundary and require interiorization.",
            "Bregman divergence is not geodesic distance.",
            "No mirror dynamics are implemented by this diagnostic.",
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
