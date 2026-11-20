#!/usr/bin/env python3
"""Audit the actual finite-step AIEF admissibility branch and its derivative.

This script addresses the operator mismatch exposed by the exceptional K3:

1. the ideal infinitesimal directional operator;
2. the finite Euler proposal;
3. the global projection gate;
4. node scale clipping and numerical scales;
5. the edge endpoint-winner map from min(scale_i, scale_j);
6. the branchwise Jacobian (or directional derivative at ties);
7. the post-hoc slack classifier.

It replays the frozen exceptional continue branch and logs the exact proposal,
scale, winner, and classifier data at every step.  It then differentiates the
implemented admissibility map on strict branches, checks the formula against
branch-preserving finite differences, and checks directional derivatives at
winner ties.

The post-positivity admissibility stage is represented exactly as

    A_eps(x) = M(A x) x,

up to floating summation-order differences between matrix row sums and the
edge-incidence representation.  On a fixed row-sum fiber A h = 0, this map is
exactly linear as long as x+h remains nonnegative.

This is a deterministic analysis of an existing frozen seed.  It does not
create an independent experiment and does not by itself prove a dt -> 0
convergence theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_component_controller_audit as component_audit
import AIEF_1_4_exceptional_K3_transition_audit as k3_audit


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_actual_admissibility_branch"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_CHECK_TIMES = "100,113.8,113.81,113.82,120,123,124.04,124.05,125,150"
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_SUPPORT_TOL = 1e-14
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_NUMERIC_TIE_TOL = 1e-12
DEFAULT_FD_STEPS = "1e-4,3e-5,1e-5,3e-6,1e-6,3e-7,1e-7,3e-8,1e-8"
DEFAULT_DIRECTION_COUNT = 5
DEFAULT_DIRECTION_SEED = 20260723
ZERO_TOL = 1e-14


def file_sha256(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def parse_positive_float_list(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated floats") from exc
    if not values or any(item <= 0.0 for item in values):
        raise argparse.ArgumentTypeError("values must be positive")
    return sorted(set(values), reverse=True)


def edge_pair(edge: int, edges: tuple[np.ndarray, np.ndarray]) -> tuple[int, int]:
    return int(edges[0][edge]), int(edges[1][edge])


def proposal_and_admissibility_branch(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    scale_epsilon: float,
) -> dict[str, Any]:
    """Reproduce the proposal and scaling portion of base.actual_step exactly."""
    dt = float(model["dt"])
    R_matrix, F_matrix, updated_coherence = base.compute_field_and_updated_coherence(
        state, model
    )
    w = state.B[edges].copy()
    F = F_matrix[edges].copy()

    proposal_matrix = state.B + dt * F_matrix
    proposal_matrix = np.maximum(proposal_matrix, 0.0)
    proposal_matrix = 0.5 * (proposal_matrix + proposal_matrix.T)
    np.fill_diagonal(proposal_matrix, 0.0)
    x = proposal_matrix[edges].copy()

    # actual_step uses incidence row sums for the gate and np.sum(matrix) for
    # scaling.  They are mathematically identical but can differ in floating
    # summation order, so both are retained.
    q_gate = A @ x
    q_scale = np.sum(proposal_matrix, axis=1)
    violating = q_gate > capacities
    gate_on = bool(np.any(violating))

    if gate_on:
        scales = np.minimum(
            1.0,
            capacities / (q_scale + scale_epsilon),
        )
        edge_scales = np.minimum(scales[edges[0]], scales[edges[1]])
        projected_matrix = proposal_matrix.copy()
        projected_matrix *= np.minimum.outer(scales, scales)
        np.fill_diagonal(projected_matrix, 0.0)
        y = projected_matrix[edges].copy()
    else:
        scales = np.ones(len(capacities), dtype=float)
        edge_scales = np.ones(len(x), dtype=float)
        projected_matrix = proposal_matrix.copy()
        y = x.copy()

    clipped = gate_on & (scales < 1.0)
    beta = -np.log(np.maximum(scales, np.finfo(float).tiny)) / dt
    z = w + dt * F
    positivity_positive = z > 0.0
    proposal_direction = (x - w) / dt
    d_proposal = A @ proposal_direction
    current_row_sum = A @ w
    slack = capacities - current_row_sum
    proposal_excess = q_gate - capacities
    projection_ratio = np.full(len(capacities), np.nan)
    positive_d = d_proposal > 0.0
    positive_slack = slack > 0.0
    valid_ratio = positive_d & positive_slack
    projection_ratio[valid_ratio] = (
        dt * d_proposal[valid_ratio] / slack[valid_ratio]
    )
    projection_ratio[positive_d & ~positive_slack] = np.inf

    winner_code = np.full(len(x), -1, dtype=int)
    winner_exact_tie = np.zeros(len(x), dtype=bool)
    winner_margin = np.abs(scales[edges[0]] - scales[edges[1]])
    for edge, (i_raw, j_raw) in enumerate(zip(edges[0], edges[1])):
        i = int(i_raw)
        j = int(j_raw)
        if not gate_on or (scales[i] == 1.0 and scales[j] == 1.0):
            winner_code[edge] = -1  # unscaled / smooth identity edge
        elif scales[i] < scales[j]:
            winner_code[edge] = i
        elif scales[j] < scales[i]:
            winner_code[edge] = j
        else:
            winner_code[edge] = -2  # active endpoint tie
            winner_exact_tie[edge] = True

    return {
        "R_matrix": R_matrix,
        "F_matrix": F_matrix,
        "updated_coherence": updated_coherence,
        "w": w,
        "F": F,
        "z_prepositivity": z,
        "positivity_positive": positivity_positive,
        "proposal_matrix": proposal_matrix,
        "x": x,
        "q_gate": q_gate,
        "q_scale": q_scale,
        "row_sum_summation_difference": q_gate - q_scale,
        "violating": violating,
        "gate_on": gate_on,
        "scales": scales,
        "clipped": clipped,
        "beta": beta,
        "edge_scales": edge_scales,
        "winner_code": winner_code,
        "winner_exact_tie": winner_exact_tie,
        "winner_margin": winner_margin,
        "projected_matrix": projected_matrix,
        "y": y,
        "current_row_sum": current_row_sum,
        "slack": slack,
        "proposal_direction": proposal_direction,
        "d_proposal": d_proposal,
        "proposal_excess": proposal_excess,
        "projection_ratio": projection_ratio,
        "scale_epsilon": float(scale_epsilon),
    }


def admissibility_from_nonnegative_proposal(
    x: np.ndarray,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    scale_epsilon: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Pure edge-coordinate implementation of the post-positivity map."""
    x = np.asarray(x, dtype=float)
    q = A @ x
    violating = q > capacities
    gate_on = bool(np.any(violating))
    if gate_on:
        scales = np.minimum(1.0, capacities / (q + scale_epsilon))
        edge_scales = np.minimum(scales[edges[0]], scales[edges[1]])
        y = x * edge_scales
    else:
        scales = np.ones(len(capacities), dtype=float)
        edge_scales = np.ones(len(x), dtype=float)
        y = x.copy()
    clipped = gate_on & (scales < 1.0)
    winner_code = np.full(len(x), -1, dtype=int)
    for edge, (i_raw, j_raw) in enumerate(zip(edges[0], edges[1])):
        i = int(i_raw)
        j = int(j_raw)
        if not gate_on or (scales[i] == 1.0 and scales[j] == 1.0):
            winner_code[edge] = -1
        elif scales[i] < scales[j]:
            winner_code[edge] = i
        elif scales[j] < scales[i]:
            winner_code[edge] = j
        else:
            winner_code[edge] = -2
    return y, {
        "q": q,
        "violating": violating,
        "gate_on": gate_on,
        "scales": scales,
        "clipped": clipped,
        "edge_scales": edge_scales,
        "winner_code": winner_code,
    }


def map_branch_signature(
    branch: dict[str, Any],
    selected_nodes: np.ndarray,
    selected_edges: np.ndarray,
) -> str:
    return json_compact(
        {
            "gate": int(branch["gate_on"]),
            "clipped": branch["clipped"][selected_nodes].astype(int).tolist(),
            "winners": branch["winner_code"][selected_edges].astype(int).tolist(),
            "positive": branch["positivity_positive"][selected_edges]
            .astype(int)
            .tolist(),
        }
    )


def effective_edge_branch_signature(
    branch: dict[str, Any],
    selected_edges: np.ndarray,
) -> str:
    """Signature of formulas actually applied to the selected edge outputs."""
    return json_compact(
        {
            "gate": int(branch["gate_on"]),
            "winners": branch["winner_code"][selected_edges].astype(int).tolist(),
            "positive": branch["positivity_positive"][selected_edges]
            .astype(int)
            .tolist(),
        }
    )


def diagnostic_signature(
    branch: dict[str, Any],
    selected_nodes: np.ndarray,
    selected_edges: np.ndarray,
    classifier: np.ndarray,
) -> str:
    return json_compact(
        {
            "map": json.loads(
                map_branch_signature(branch, selected_nodes, selected_edges)
            ),
            "violating": branch["violating"][selected_nodes]
            .astype(int)
            .tolist(),
            "classifier": classifier[selected_nodes].astype(int).tolist(),
        }
    )


def analytic_branch_jacobian(
    x: np.ndarray,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    scale_epsilon: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Classical Jacobian on a strict branch; tied active rows are NaN."""
    _, info = admissibility_from_nonnegative_proposal(
        x, capacities, A, edges, scale_epsilon
    )
    edge_count = len(x)
    J = np.zeros((edge_count, edge_count), dtype=float)
    nonsmooth_edges: list[int] = []
    if not info["gate_on"]:
        return np.eye(edge_count), {
            **info,
            "nonsmooth_edges": nonsmooth_edges,
            "classical_jacobian_exists": True,
        }

    q = info["q"]
    scales = info["scales"]
    for edge, (i_raw, j_raw) in enumerate(zip(edges[0], edges[1])):
        i = int(i_raw)
        j = int(j_raw)
        if scales[i] == 1.0 and scales[j] == 1.0:
            J[edge, edge] = 1.0
            continue
        if scales[i] < scales[j]:
            winner = i
        elif scales[j] < scales[i]:
            winner = j
        else:
            J[edge, :] = np.nan
            nonsmooth_edges.append(edge)
            continue
        scale = scales[winner]
        J[edge, edge] = scale
        J[edge, :] -= (
            x[edge] * scale / (q[winner] + scale_epsilon)
        ) * A[winner, :]

    return J, {
        **info,
        "nonsmooth_edges": nonsmooth_edges,
        "classical_jacobian_exists": not nonsmooth_edges,
    }


def directional_derivative_admissibility(
    x: np.ndarray,
    h: np.ndarray,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    scale_epsilon: float,
    boundary_tolerance: float = 1e-14,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Directional derivative away from the safeguarded global-gate jump.

    The formula handles strict winners, active endpoint ties, and scale-clipping
    boundaries.  It intentionally refuses the global gate boundary because the
    fixed-epsilon implementation is discontinuous there.
    """
    y, info = admissibility_from_nonnegative_proposal(
        x, capacities, A, edges, scale_epsilon
    )
    del y
    q = info["q"]
    gate_margin = float(np.max(q - capacities))
    if abs(gate_margin) <= boundary_tolerance:
        raise ValueError("directional derivative not defined at safeguarded global gate")
    if not info["gate_on"]:
        return h.copy(), {**info, "node_scale_derivative": np.zeros(len(q))}

    dq = A @ h
    scales = info["scales"]
    ds = np.zeros(len(q), dtype=float)
    clip_margin = q + scale_epsilon - capacities
    for node in range(len(q)):
        if clip_margin[node] > boundary_tolerance:
            ds[node] = -(
                scales[node] / (q[node] + scale_epsilon)
            ) * dq[node]
        elif clip_margin[node] < -boundary_tolerance:
            ds[node] = 0.0
        else:
            # s_i(q)=min(1,c/(q+eps)) at the clipping boundary.
            rational_derivative = -dq[node] / capacities[node]
            ds[node] = min(0.0, rational_derivative)

    derivative = np.empty(len(x), dtype=float)
    for edge, (i_raw, j_raw) in enumerate(zip(edges[0], edges[1])):
        i = int(i_raw)
        j = int(j_raw)
        if scales[i] < scales[j]:
            dm = ds[i]
        elif scales[j] < scales[i]:
            dm = ds[j]
        else:
            dm = min(ds[i], ds[j])
        multiplier = min(scales[i], scales[j])
        derivative[edge] = multiplier * h[edge] + x[edge] * dm
    return derivative, {**info, "node_scale_derivative": ds}


def certified_subspace_branch_radius(
    x: np.ndarray,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    selected_edges: np.ndarray,
    scale_epsilon: float,
) -> tuple[float, dict[str, float]]:
    """Certified Euclidean radius for perturbations on selected edge columns."""
    _, info = admissibility_from_nonnegative_proposal(
        x, capacities, A, edges, scale_epsilon
    )
    A_sub = A[:, selected_edges]
    distances: dict[str, float] = {}

    # Nonnegativity of selected proposal edges.
    distances["positivity"] = float(np.min(x[selected_edges]))

    # Preserve the global gate.  If on, it is sufficient to retain one
    # violating witness.  If off, every proposal row must remain below c.
    q = info["q"]
    row_norms = np.linalg.norm(A_sub, axis=1)
    if info["gate_on"]:
        witness_distances = []
        for node in np.flatnonzero(q > capacities):
            if row_norms[node] == 0.0:
                witness_distances.append(np.inf)
            else:
                witness_distances.append(
                    float((q[node] - capacities[node]) / row_norms[node])
                )
        distances["global_gate"] = (
            max(witness_distances) if witness_distances else 0.0
        )
    else:
        gate_distances = []
        for node in range(len(q)):
            if row_norms[node] > 0.0:
                gate_distances.append(
                    float((capacities[node] - q[node]) / row_norms[node])
                )
        distances["global_gate"] = min(gate_distances) if gate_distances else np.inf

    # Preserve scale clipping for all affected rows.
    clip_distances = []
    for node in range(len(q)):
        if row_norms[node] > 0.0:
            clip_distances.append(
                float(
                    abs(q[node] + scale_epsilon - capacities[node])
                    / row_norms[node]
                )
            )
    distances["scale_clipping"] = min(clip_distances) if clip_distances else np.inf

    # Preserve strict active-active endpoint winners.  One-active/one-inactive
    # order is already protected by scale-clipping persistence.
    winner_distances = []
    scales = info["scales"]
    for edge in selected_edges:
        i, j = edge_pair(int(edge), edges)
        if scales[i] < 1.0 and scales[j] < 1.0:
            coefficient = capacities[i] * A_sub[j] - capacities[j] * A_sub[i]
            coefficient_norm = float(np.linalg.norm(coefficient))
            affine_value = float(
                capacities[i] * (q[j] + scale_epsilon)
                - capacities[j] * (q[i] + scale_epsilon)
            )
            if coefficient_norm == 0.0:
                winner_distances.append(
                    np.inf if affine_value != 0.0 else 0.0
                )
            else:
                winner_distances.append(abs(affine_value) / coefficient_norm)
    distances["winner"] = min(winner_distances) if winner_distances else np.inf

    radius = float(min(distances.values()))
    return radius, distances


def finite_difference_jacobian_validation(
    label: str,
    x: np.ndarray,
    selected_edges: np.ndarray,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    scale_epsilon: float,
    fd_steps: list[float],
) -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    J, info = analytic_branch_jacobian(
        x, capacities, A, edges, scale_epsilon
    )
    radius, radius_parts = certified_subspace_branch_radius(
        x, capacities, A, edges, selected_edges, scale_epsilon
    )
    rows: list[dict[str, Any]] = []
    base_y, base_info = admissibility_from_nonnegative_proposal(
        x, capacities, A, edges, scale_epsilon
    )
    selected_nodes = np.unique(
        np.concatenate(
            [edges[0][selected_edges], edges[1][selected_edges]]
        )
    )
    base_signature = json_compact(
        {
            "gate": int(base_info["gate_on"]),
            "clipped": base_info["clipped"][selected_nodes].astype(int).tolist(),
            "winners": base_info["winner_code"][selected_edges].astype(int).tolist(),
        }
    )
    del base_y

    selected_analytic = J[np.ix_(selected_edges, selected_edges)]
    for requested_step in fd_steps:
        step = requested_step
        if np.isfinite(radius):
            step = min(step, 0.2 * radius)
        if step <= 0.0 or step < 10.0 * np.finfo(float).eps:
            continue
        numerical = np.empty((len(selected_edges), len(selected_edges)))
        branch_preserved = True
        nonnegative = True
        for local_column, edge in enumerate(selected_edges):
            direction = np.zeros(len(x), dtype=float)
            direction[edge] = 1.0
            x_plus = x + step * direction
            x_minus = x - step * direction
            if np.any(x_minus < 0.0):
                nonnegative = False
                branch_preserved = False
                numerical[:, local_column] = np.nan
                continue
            y_plus, plus_info = admissibility_from_nonnegative_proposal(
                x_plus, capacities, A, edges, scale_epsilon
            )
            y_minus, minus_info = admissibility_from_nonnegative_proposal(
                x_minus, capacities, A, edges, scale_epsilon
            )
            for perturbed_info in (plus_info, minus_info):
                signature = json_compact(
                    {
                        "gate": int(perturbed_info["gate_on"]),
                        "clipped": perturbed_info["clipped"][selected_nodes]
                        .astype(int)
                        .tolist(),
                        "winners": perturbed_info["winner_code"][selected_edges]
                        .astype(int)
                        .tolist(),
                    }
                )
                branch_preserved &= signature == base_signature
            numerical[:, local_column] = (
                y_plus[selected_edges] - y_minus[selected_edges]
            ) / (2.0 * step)

        analytic_finite = np.all(np.isfinite(selected_analytic))
        if analytic_finite and np.all(np.isfinite(numerical)):
            absolute_error = float(np.linalg.norm(numerical - selected_analytic))
            relative_error = float(
                absolute_error / max(np.linalg.norm(selected_analytic), ZERO_TOL)
            )
            maximum_error = float(np.max(np.abs(numerical - selected_analytic)))
        else:
            absolute_error = relative_error = maximum_error = np.nan
        rows.append(
            {
                "label": label,
                "requested_step": requested_step,
                "used_step": step,
                "certified_radius": radius,
                "radius_positivity": radius_parts["positivity"],
                "radius_global_gate": radius_parts["global_gate"],
                "radius_scale_clipping": radius_parts["scale_clipping"],
                "radius_winner": radius_parts["winner"],
                "classical_jacobian_exists_globally": bool(
                    info["classical_jacobian_exists"]
                ),
                "selected_analytic_finite": bool(analytic_finite),
                "branch_preserved": bool(branch_preserved),
                "nonnegative": bool(nonnegative),
                "matrix_absolute_error": absolute_error,
                "matrix_relative_error": relative_error,
                "matrix_maximum_error": maximum_error,
            }
        )
    return rows, {
        "J_full": J,
        "J_selected": selected_analytic,
        "x": x,
        "scales": info["scales"],
        "certified_radius": np.asarray([radius]),
    }


def directional_validation(
    label: str,
    x: np.ndarray,
    selected_edges: np.ndarray,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    scale_epsilon: float,
    direction_count: int,
    direction_seed: int,
    fd_steps: list[float],
) -> list[dict[str, Any]]:
    rng = np.random.default_rng(direction_seed)
    base_y, _ = admissibility_from_nonnegative_proposal(
        x, capacities, A, edges, scale_epsilon
    )
    rows: list[dict[str, Any]] = []
    directions: list[np.ndarray] = []
    # Coordinate-combination directions plus deterministic random directions.
    for local_index in range(min(len(selected_edges), direction_count)):
        local = np.zeros(len(selected_edges))
        local[local_index] = 1.0
        if len(selected_edges) > 1:
            local[(local_index + 1) % len(selected_edges)] = -0.5
        directions.append(local / np.linalg.norm(local))
    while len(directions) < direction_count:
        local = rng.normal(size=len(selected_edges))
        local /= np.linalg.norm(local)
        directions.append(local)

    for direction_id, local_direction in enumerate(directions):
        h = np.zeros(len(x), dtype=float)
        h[selected_edges] = local_direction
        try:
            predicted, _ = directional_derivative_admissibility(
                x,
                h,
                capacities,
                A,
                edges,
                scale_epsilon,
            )
            derivative_defined = True
        except ValueError:
            predicted = np.full(len(x), np.nan)
            derivative_defined = False
        for step in fd_steps:
            if np.any(x + step * h < 0.0):
                continue
            y_step, _ = admissibility_from_nonnegative_proposal(
                x + step * h,
                capacities,
                A,
                edges,
                scale_epsilon,
            )
            observed = (y_step - base_y) / step
            if derivative_defined:
                absolute_error = float(
                    np.linalg.norm(
                        observed[selected_edges] - predicted[selected_edges]
                    )
                )
                relative_error = float(
                    absolute_error
                    / max(
                        np.linalg.norm(predicted[selected_edges]), ZERO_TOL
                    )
                )
            else:
                absolute_error = relative_error = np.nan
            rows.append(
                {
                    "label": label,
                    "direction_id": direction_id,
                    "step": step,
                    "directional_derivative_defined": derivative_defined,
                    "absolute_error_selected": absolute_error,
                    "relative_error_selected": relative_error,
                    "predicted_norm_selected": float(
                        np.linalg.norm(predicted[selected_edges])
                    )
                    if derivative_defined
                    else np.nan,
                    "observed_norm_selected": float(
                        np.linalg.norm(observed[selected_edges])
                    ),
                }
            )
    return rows


def winner_label(code: int) -> str:
    if code == -1:
        return "unscaled"
    if code == -2:
        return "tie"
    return f"node_{code}"


def stage_label_for_time(time_value: float) -> str:
    return f"time_{time_value:g}".replace(".", "p")


def make_report(
    step_frame: pd.DataFrame,
    node_frame: pd.DataFrame,
    edge_frame: pd.DataFrame,
    events: pd.DataFrame,
    jacobian_validation: pd.DataFrame,
    directional: pd.DataFrame,
    *,
    seed: str,
    k3_nodes: np.ndarray,
    k3_edges: np.ndarray,
    final_replay_exact: bool,
    final_replay_max_error: float,
    projected_reproduction_max_error: float,
    numeric_tie_tolerance: float,
) -> str:
    lines = [
        "AIEF actual finite-step admissibility branch audit",
        "==================================================",
        "",
        "Identity and replay",
        "-------------------",
        f"Seed: {seed}",
        f"K3 nodes: {k3_nodes.tolist()}",
        f"K3 edges: {k3_edges.tolist()}",
        f"Trajectory states: {len(step_frame)}",
        f"Final replay exact: {final_replay_exact}",
        f"Final replay maximum error: {final_replay_max_error:.6g}",
        f"Maximum pure-map versus executed projection error: {projected_reproduction_max_error:.6g}",
        f"Maximum incidence/matrix row-sum discrepancy: {step_frame['row_sum_summation_difference_max'].max():.6g}",
        "",
        "First node events",
        "-----------------",
    ]
    for node in k3_nodes:
        node_events = events.loc[events["node"] == int(node)]
        for event_type in ("proposal_violation_on", "scale_clipping_on", "classifier_on"):
            matching = node_events.loc[node_events["event_type"] == event_type]
            if len(matching):
                row = matching.iloc[0]
                lines.append(
                    f"  node {int(node)} {event_type}: step={int(row['step'])}, "
                    f"time={row['state_elapsed_time']:.6g}, "
                    f"scale={row['scale']:.12g}, beta={row['beta']:.6g}"
                )
            else:
                lines.append(f"  node {int(node)} {event_type}: not observed")

    lines.extend(["", "K3 edge winner evolution", "------------------------"])
    for edge in k3_edges:
        rows = events.loc[
            (events["edge"] == int(edge))
            & (events["event_type"].isin(["initial_winner", "winner_change"]))
        ]
        labels = []
        for _, row in rows.iterrows():
            labels.append(
                f"step {int(row['step'])}: {row['winner_label']} "
                f"(margin={row['winner_margin']:.3g})"
            )
        edge_detail = edge_frame.loc[edge_frame["edge"] == int(edge)].iloc[0]
        lines.append(
            f"  edge {int(edge)}=({int(edge_detail['node_i'])},{int(edge_detail['node_j'])}): "
            + ("; ".join(labels) if labels else "no events")
        )

    node11_violation = events.loc[
        (events["node"] == 11)
        & (events["event_type"] == "proposal_violation_on")
    ]
    if len(node11_violation):
        step = int(node11_violation.iloc[0]["step"])
        at_step = edge_frame.loc[edge_frame["step"] == step]
        lines.extend(
            [
                "",
                f"Winner map at node-11 first violation (step {step})",
                "-" * 52,
            ]
        )
        for _, row in at_step.iterrows():
            lines.append(
                f"  edge {int(row['edge'])}=({int(row['node_i'])},{int(row['node_j'])}): "
                f"winner={row['winner_label']}, margin={row['winner_margin']:.6g}"
            )

    stratum_changes = events.loc[
        events["event_type"] == "stratum_signature_change"
    ]
    effective_changes = events.loc[
        events["event_type"] == "effective_edge_branch_change"
    ]
    lines.extend(
        [
            "",
            "Stratum and effective-edge branch changes",
            "-----------------------------------------",
            f"Stratum-signature changes: {len(stratum_changes)}",
            f"Effective-edge branch changes: {len(effective_changes)}",
        ]
    )
    for _, row in effective_changes.head(20).iterrows():
        lines.append(
            f"  effective change step={int(row['step'])}, "
            f"time={row['state_elapsed_time']:.6g}"
        )
    if len(effective_changes) > 20:
        lines.append(
            f"  ... {len(effective_changes) - 20} additional effective changes in CSV"
        )

    lines.extend(["", "Branchwise Jacobian validation", "------------------------------"])
    valid = jacobian_validation.loc[
        jacobian_validation["matrix_relative_error"].notna()
        & jacobian_validation["branch_preserved"]
    ]
    if len(valid):
        lines.append(
            f"Validated rows: {len(valid)}, median relative error={valid['matrix_relative_error'].median():.6g}, "
            f"maximum={valid['matrix_relative_error'].max():.6g}"
        )
    else:
        lines.append("No strict branch-preserving classical-Jacobian rows were available.")

    lines.extend(["", "Directional derivative validation", "---------------------------------"])
    directional_valid = directional.loc[
        directional["relative_error_selected"].notna()
    ]
    if len(directional_valid):
        smallest = (
            directional_valid.sort_values("step")
            .groupby(["label", "direction_id"], as_index=False)
            .first()
        )
        lines.append(
            f"Directions at smallest steps: {len(smallest)}, "
            f"median relative error={smallest['relative_error_selected'].median():.6g}, "
            f"maximum={smallest['relative_error_selected'].max():.6g}"
        )
    else:
        lines.append("No directional derivative validations were available.")

    lines.extend(
        [
            "",
            "Late scale geometry",
            "-------------------",
        ]
    )
    late_nodes = node_frame.loc[node_frame["step"] == node_frame["step"].max()]
    for _, row in late_nodes.iterrows():
        lines.append(
            f"  node {int(row['node'])}: scale={row['scale']:.12g}, "
            f"beta={row['beta']:.6g}, violation={bool(row['proposal_violating'])}, "
            f"clipped={bool(row['scale_clipped'])}"
        )
    lines.append(f"Numeric tie reporting tolerance: {numeric_tie_tolerance:.3g}")

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Proposal violation, scale clipping, edge winner status, and slack classification are distinct.",
            "* A node scale affects an edge only if it wins or ties the endpoint minimum.",
            "* The classical Jacobian formula is used only on strict locally constant winner strata.",
            "* Active endpoint ties are tested with directional rather than symmetric derivatives.",
            "* The fixed safeguard and global gate create a tiny discontinuity at gate onset.",
            "* Finite-step spectra are not automatically continuous-generator spectra.",
            "* This one-seed deterministic replay is not independent population evidence.",
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
    parser.add_argument(
        "--check-times",
        type=base.parse_float_list,
        default=base.parse_float_list(DEFAULT_CHECK_TIMES),
    )
    parser.add_argument(
        "--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL
    )
    parser.add_argument(
        "--support-tol", type=float, default=DEFAULT_SUPPORT_TOL
    )
    parser.add_argument(
        "--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON
    )
    parser.add_argument(
        "--numeric-tie-tol", type=float, default=DEFAULT_NUMERIC_TIE_TOL
    )
    parser.add_argument(
        "--fd-steps",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_FD_STEPS),
    )
    parser.add_argument(
        "--direction-count", type=int, default=DEFAULT_DIRECTION_COUNT
    )
    parser.add_argument(
        "--direction-seed", type=int, default=DEFAULT_DIRECTION_SEED
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(
        args.boundary_tol,
        args.support_tol,
        args.scale_epsilon,
        args.numeric_tie_tol,
    ) <= 0.0:
        raise ValueError("all tolerances and epsilon must be positive")
    if args.direction_count <= 0:
        raise ValueError("direction-count must be positive")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = manifest["model"]
    node_count = int(model["N"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(
        model["q"]
    )
    capacities = np.full(node_count, capacity, dtype=float)
    A, edges = base.incidence_matrix(node_count)
    dt = float(model["dt"])
    future_steps = int(manifest["protocol"]["future_steps"])
    check_steps = {
        int(round(time_value / dt)): stage_label_for_time(time_value)
        for time_value in args.check_times
        if int(round(time_value / dt)) <= future_steps
    }

    step_rows: list[dict[str, Any]] = []
    node_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    key_states: dict[int, base.DynamicState] = {}
    key_labels: dict[int, set[str]] = defaultdict(set)
    projected_reproduction_max_error = 0.0

    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
        expected_final = np.asarray(
            data[base.branch_key("continue", args.seed, "B_final")],
            dtype=float,
        ).copy()
        k3_nodes, k3_edges, k3_identification = k3_audit.identify_partial_K3(
            state,
            model,
            capacities,
            A,
            edges,
            args.boundary_tol,
            args.support_tol,
        )

        previous_branch: dict[str, Any] | None = None
        previous_classifier: np.ndarray | None = None
        previous_map_signature: str | None = None
        previous_effective_signature: str | None = None
        first_node_event_seen: set[tuple[str, int]] = set()
        first_winner_change_seen: set[int] = set()
        previous_state: base.DynamicState | None = None

        for step in range(future_steps + 1):
            state_at_step = state.clone()
            branch = proposal_and_admissibility_branch(
                state,
                model,
                capacities,
                A,
                edges,
                args.scale_epsilon,
            )
            classifier = branch["slack"] <= args.boundary_tol
            map_signature = map_branch_signature(
                branch, k3_nodes, k3_edges
            )
            effective_signature = effective_edge_branch_signature(
                branch, k3_edges
            )
            diag_signature = diagnostic_signature(
                branch, k3_nodes, k3_edges, classifier
            )
            stage_labels: list[str] = []
            if step == 0:
                stage_labels.append("split")
                key_states[step] = state.clone()
                key_labels[step].add("split")
            if step == future_steps:
                stage_labels.append("late")
                key_states[step] = state.clone()
                key_labels[step].add("late")
            if step in check_steps:
                stage_labels.append(check_steps[step])
                key_states[step] = state.clone()
                key_labels[step].add(check_steps[step])

            for node in k3_nodes:
                node = int(node)
                node_conditions = {
                    "proposal_violation_on": bool(branch["violating"][node]),
                    "scale_clipping_on": bool(branch["clipped"][node]),
                    "classifier_on": bool(classifier[node]),
                }
                for event_type, condition in node_conditions.items():
                    previous_condition = False
                    if previous_branch is not None:
                        if event_type == "proposal_violation_on":
                            previous_condition = bool(previous_branch["violating"][node])
                        elif event_type == "scale_clipping_on":
                            previous_condition = bool(previous_branch["clipped"][node])
                        else:
                            previous_condition = bool(previous_classifier[node])
                    if condition and not previous_condition:
                        event_rows.append(
                            {
                                "step": step,
                                "state_elapsed_time": step * dt,
                                "event_type": event_type,
                                "node": node,
                                "edge": -1,
                                "scale": float(branch["scales"][node]),
                                "beta": float(branch["beta"][node]),
                                "winner_label": "",
                                "winner_margin": np.nan,
                            }
                        )
                        if (event_type, node) not in first_node_event_seen:
                            key_states[step] = state.clone()
                            key_labels[step].add(f"{event_type}_node_{node}")
                            if previous_state is not None and step > 0:
                                key_states.setdefault(step - 1, previous_state.clone())
                                key_labels[step - 1].add(
                                    f"pre_{event_type}_node_{node}"
                                )
                            first_node_event_seen.add((event_type, node))

            for edge in k3_edges:
                edge = int(edge)
                current_winner = int(branch["winner_code"][edge])
                if step == 0:
                    event_rows.append(
                        {
                            "step": step,
                            "state_elapsed_time": step * dt,
                            "event_type": "initial_winner",
                            "node": -1,
                            "edge": edge,
                            "scale": np.nan,
                            "beta": np.nan,
                            "winner_label": winner_label(current_winner),
                            "winner_margin": float(branch["winner_margin"][edge]),
                        }
                    )
                elif current_winner != int(previous_branch["winner_code"][edge]):
                    event_rows.append(
                        {
                            "step": step,
                            "state_elapsed_time": step * dt,
                            "event_type": "winner_change",
                            "node": -1,
                            "edge": edge,
                            "scale": np.nan,
                            "beta": np.nan,
                            "winner_label": winner_label(current_winner),
                            "winner_margin": float(branch["winner_margin"][edge]),
                        }
                    )
                    if edge not in first_winner_change_seen:
                        key_states[step] = state.clone()
                        key_labels[step].add(f"winner_change_edge_{edge}")
                        if previous_state is not None:
                            key_states.setdefault(step - 1, previous_state.clone())
                            key_labels[step - 1].add(f"pre_winner_change_edge_{edge}")
                        first_winner_change_seen.add(edge)

            if previous_map_signature is not None and map_signature != previous_map_signature:
                event_rows.append(
                    {
                        "step": step,
                        "state_elapsed_time": step * dt,
                        "event_type": "stratum_signature_change",
                        "node": -1,
                        "edge": -1,
                        "scale": np.nan,
                        "beta": np.nan,
                        "winner_label": "",
                        "winner_margin": np.nan,
                    }
                )
            if (
                previous_effective_signature is not None
                and effective_signature != previous_effective_signature
            ):
                event_rows.append(
                    {
                        "step": step,
                        "state_elapsed_time": step * dt,
                        "event_type": "effective_edge_branch_change",
                        "node": -1,
                        "edge": -1,
                        "scale": np.nan,
                        "beta": np.nan,
                        "winner_label": "",
                        "winner_margin": np.nan,
                    }
                )

            pure_y, _ = admissibility_from_nonnegative_proposal(
                branch["x"], capacities, A, edges, args.scale_epsilon
            )
            pure_map_error = float(np.max(np.abs(pure_y - branch["y"])))

            step_rows.append(
                {
                    "step": step,
                    "state_elapsed_time": step * dt,
                    "stage_labels": ";".join(stage_labels),
                    "global_gate_on": bool(branch["gate_on"]),
                    "global_violating_count": int(np.sum(branch["violating"])),
                    "global_scale_clipped_count": int(np.sum(branch["clipped"])),
                    "K3_violating_count": int(np.sum(branch["violating"][k3_nodes])),
                    "K3_scale_clipped_count": int(np.sum(branch["clipped"][k3_nodes])),
                    "K3_classifier_count": int(np.sum(classifier[k3_nodes])),
                    "K3_numeric_tie_count": int(
                        np.sum(branch["winner_margin"][k3_edges] <= args.numeric_tie_tol)
                    ),
                    "K3_exact_active_tie_count": int(
                        np.sum(branch["winner_exact_tie"][k3_edges])
                    ),
                    "K3_minimum_winner_margin": float(
                        np.min(branch["winner_margin"][k3_edges])
                    ),
                    "K3_scales_json": json_compact(
                        branch["scales"][k3_nodes].tolist()
                    ),
                    "K3_beta_json": json_compact(
                        branch["beta"][k3_nodes].tolist()
                    ),
                    "K3_winners_json": json_compact(
                        [winner_label(int(branch["winner_code"][edge])) for edge in k3_edges]
                    ),
                    "stratum_signature": map_signature,
                    "effective_edge_branch_signature": effective_signature,
                    "diagnostic_signature": diag_signature,
                    "row_sum_summation_difference_max": float(
                        np.max(np.abs(branch["row_sum_summation_difference"]))
                    ),
                    "pure_edge_map_vs_matrix_projection_error": pure_map_error,
                }
            )

            for node in k3_nodes:
                node = int(node)
                node_rows.append(
                    {
                        "step": step,
                        "state_elapsed_time": step * dt,
                        "node": node,
                        "current_row_sum": float(branch["current_row_sum"][node]),
                        "slack": float(branch["slack"][node]),
                        "proposal_row_sum_gate": float(branch["q_gate"][node]),
                        "proposal_row_sum_scale": float(branch["q_scale"][node]),
                        "proposal_excess": float(branch["proposal_excess"][node]),
                        "proposal_row_direction": float(branch["d_proposal"][node]),
                        "projection_ratio": float(branch["projection_ratio"][node]),
                        "proposal_violating": bool(branch["violating"][node]),
                        "scale_clipped": bool(branch["clipped"][node]),
                        "scale": float(branch["scales"][node]),
                        "beta": float(branch["beta"][node]),
                        "classifier_saturated": bool(classifier[node]),
                        "actual_finite_row_sum_rate": np.nan,
                    }
                )

            for edge in k3_edges:
                edge = int(edge)
                i, j = edge_pair(edge, edges)
                edge_rows.append(
                    {
                        "step": step,
                        "state_elapsed_time": step * dt,
                        "edge": edge,
                        "node_i": i,
                        "node_j": j,
                        "proposal_weight": float(branch["x"][edge]),
                        "projected_weight": float(branch["y"][edge]),
                        "edge_scale": float(branch["edge_scales"][edge]),
                        "node_i_scale": float(branch["scales"][i]),
                        "node_j_scale": float(branch["scales"][j]),
                        "node_i_beta": float(branch["beta"][i]),
                        "node_j_beta": float(branch["beta"][j]),
                        "winner": int(branch["winner_code"][edge]),
                        "winner_label": winner_label(int(branch["winner_code"][edge])),
                        "winner_margin": float(branch["winner_margin"][edge]),
                        "numeric_tie": bool(
                            branch["winner_margin"][edge] <= args.numeric_tie_tol
                        ),
                        "exact_active_tie": bool(branch["winner_exact_tie"][edge]),
                        "actual_finite_weight_rate": np.nan,
                    }
                )

            if step < future_steps:
                before_w = state.B[edges].copy()
                before_rows = A @ before_w
                actual_info = base.actual_step(
                    state,
                    model,
                    capacities,
                    A,
                    edges,
                    args.boundary_tol,
                    audit_operator=False,
                )
                del actual_info
                projected_error = float(
                    np.max(np.abs(state.B - branch["projected_matrix"]))
                )
                projected_reproduction_max_error = max(
                    projected_reproduction_max_error, projected_error
                )
                after_w = state.B[edges]
                after_rows = A @ after_w
                finite_edge_rate = (after_w - before_w) / dt
                finite_row_rate = (after_rows - before_rows) / dt
                for row in node_rows[-len(k3_nodes):]:
                    row["actual_finite_row_sum_rate"] = float(
                        finite_row_rate[int(row["node"])]
                    )
                edge_row_lookup = {
                    int(row["edge"]): row for row in edge_rows[-len(k3_edges):]
                }
                for edge in k3_edges:
                    edge_row_lookup[int(edge)]["actual_finite_weight_rate"] = float(
                        finite_edge_rate[int(edge)]
                    )

            previous_state = state_at_step
            previous_branch = branch
            previous_classifier = classifier.copy()
            previous_map_signature = map_signature
            previous_effective_signature = effective_signature

        final_replay_exact = bool(np.array_equal(state.B, expected_final))
        final_replay_max_error = float(np.max(np.abs(state.B - expected_final)))

    step_frame = pd.DataFrame(step_rows)
    node_frame = pd.DataFrame(node_rows)
    edge_frame = pd.DataFrame(edge_rows)
    events_frame = pd.DataFrame(event_rows)

    jacobian_rows: list[dict[str, Any]] = []
    directional_rows: list[dict[str, Any]] = []
    matrix_payload: dict[str, np.ndarray] = {}
    used_matrix_labels: set[str] = set()
    for step in sorted(key_states):
        state = key_states[step]
        branch = proposal_and_admissibility_branch(
            state,
            model,
            capacities,
            A,
            edges,
            args.scale_epsilon,
        )
        labels = sorted(key_labels[step]) or [f"step_{step}"]
        label = f"step_{step}__" + "__".join(labels)
        if label in used_matrix_labels:
            continue
        used_matrix_labels.add(label)
        validation, matrices = finite_difference_jacobian_validation(
            label,
            branch["x"],
            k3_edges,
            capacities,
            A,
            edges,
            args.scale_epsilon,
            args.fd_steps,
        )
        jacobian_rows.extend(validation)
        directional_rows.extend(
            directional_validation(
                label,
                branch["x"],
                k3_edges,
                capacities,
                A,
                edges,
                args.scale_epsilon,
                args.direction_count,
                args.direction_seed + step,
                args.fd_steps,
            )
        )
        safe_label = "".join(
            character if character.isalnum() else "_" for character in label
        )
        for name, matrix in matrices.items():
            matrix_payload[f"{safe_label}_{name}"] = np.asarray(matrix)

    jacobian_frame = pd.DataFrame(jacobian_rows)
    directional_frame = pd.DataFrame(directional_rows)

    component_audit.atomic_write_csv(
        output_dir / "actual_branch_step_summary.csv", step_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "actual_branch_node_trajectory.csv", node_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "actual_branch_edge_trajectory.csv", edge_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "actual_branch_events.csv", events_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "branch_jacobian_validation.csv", jacobian_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "directional_derivative_validation.csv", directional_frame
    )
    component_audit.atomic_savez(
        output_dir / "actual_branch_key_matrices.npz", matrix_payload
    )

    # Attach no hidden metadata to CSV; the report reads endpoint pairs from
    # explicit edge-frame columns.
    report = make_report(
        step_frame,
        node_frame,
        edge_frame,
        events_frame,
        jacobian_frame,
        directional_frame,
        seed=args.seed,
        k3_nodes=k3_nodes,
        k3_edges=k3_edges,
        final_replay_exact=final_replay_exact,
        final_replay_max_error=final_replay_max_error,
        projected_reproduction_max_error=projected_reproduction_max_error,
        numeric_tie_tolerance=args.numeric_tie_tol,
    )
    component_audit.atomic_write_text(
        output_dir / "actual_admissibility_branch_report.txt", report
    )

    source_path = Path(__file__).resolve()
    dependencies = {
        "stationarity": Path(base.__file__).resolve(),
        "component_audit": Path(component_audit.__file__).resolve(),
        "K3_transition_audit": Path(k3_audit.__file__).resolve(),
    }
    analysis_manifest = {
        "analysis": "AIEF-1.4 actual finite-step admissibility branch and derivative audit",
        "source": {
            "path": str(source_path),
            "sha256": file_sha256(source_path),
        },
        "dependencies": {
            name: {"path": str(path), "sha256": file_sha256(path)}
            for name, path in dependencies.items()
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
        "K3_nodes": k3_nodes.tolist(),
        "K3_edges": k3_edges.tolist(),
        "K3_identification": k3_identification,
        "future_steps": future_steps,
        "dt": dt,
        "scale_epsilon": args.scale_epsilon,
        "boundary_classifier_tolerance": args.boundary_tol,
        "support_tolerance": args.support_tol,
        "numeric_tie_tolerance": args.numeric_tie_tol,
        "fd_steps": args.fd_steps,
        "direction_count": args.direction_count,
        "direction_seed": args.direction_seed,
        "final_replay_exact": final_replay_exact,
        "final_replay_max_error": final_replay_max_error,
        "projected_reproduction_max_error": projected_reproduction_max_error,
        "outputs": [
            "actual_branch_step_summary.csv",
            "actual_branch_node_trajectory.csv",
            "actual_branch_edge_trajectory.csv",
            "actual_branch_events.csv",
            "branch_jacobian_validation.csv",
            "directional_derivative_validation.csv",
            "actual_branch_key_matrices.npz",
            "actual_admissibility_branch_report.txt",
        ],
        "interpretation_constraints": [
            "Proposal violation, scale clipping, endpoint winner status, and slack classification are distinct.",
            "Stratum-signature changes are separated from changes in the formulas applied to selected edge outputs.",
            "The branchwise classical Jacobian is asserted only on strict constant-winner strata.",
            "The directional formula is used at endpoint ties away from the safeguarded global-gate discontinuity.",
            "The post-positivity map is exactly fiber-linear on Ax=q within the nonnegative domain.",
            "Finite-step branch spectra are not automatically continuous-generator spectra.",
            "This deterministic replay of one frozen seed is not independent population evidence.",
        ],
    }
    component_audit.atomic_write_text(
        output_dir / "analysis_manifest.json",
        json.dumps(analysis_manifest, indent=2, sort_keys=True) + "\n",
    )

    print(report)
    print(f"Saved analysis to {output_dir.resolve()}")


if __name__ == "__main__":
    main()
