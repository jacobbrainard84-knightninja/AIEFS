#!/usr/bin/env python3
"""Dense exceptional-K3 transition audit for the frozen AIEF-1.4 run.

The component audit showed that the exceptional support is

    K5 + K3[partially active] + K4,

whereas the other 39 split states have only fully active support components.
This script replays the exceptional continue branch deterministically and
tracks the K3 at every future step.  Its purpose is to decide, from the saved
trajectory, whether the observed 9 -> 8 tangent-dimension switch is exactly the
activation of a second K3 node and whether the local intertwining conditions
change as predicted:

* one saturated K3 node:
      C = [1, 1, 0], dim ker(C)=2, and only the two incident rates must agree;
      the edge between the two unsaturated nodes is a free tangent coordinate;
* two saturated K3 nodes:
      rank(C)=2, dim ker(C)=1, and all three edge rates must agree;
* three saturated K3 nodes:
      C is nonsingular and the K3 tangent nullity is zero.

The audit records node slacks, alpha values, edge coherences, growth terms,
weights, rates, stationarity defects, actual finite weight rates, controller
loads, local tangent/normal field components, least-squares intertwining,
component-scalar intertwining, and the exact rate-equality defect required by
the current K3 active rows.

This script analyzes the existing dt=0.01 trajectory.  It does not by itself
establish a continuum-time active-switch theorem; a genuine timestep study
would require consistently regenerated smaller-dt histories and EMA states.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_face_spectrum_analysis as face
import AIEF_1_4_component_controller_audit as component_audit


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_exceptional_K3_transition"
DEFAULT_EXCEPTIONAL_SEED = "4619122171158768524"
DEFAULT_CHECK_TIMES = "100,120,123,125,150"
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_BOUNDARY_TOL_SWEEP = "1e-12,1e-10,1e-9,1e-8,1e-7"
DEFAULT_SUPPORT_TOL = 1e-14
DEFAULT_RANK_TOL = 1e-10
DEFAULT_RESTORATION_TOLS = "1e-8,1e-10"
DEFAULT_WINDOW_RADIUS = 250
ZERO_TOL = 1e-14


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
    if not values or any(item < 0.0 for item in values):
        raise argparse.ArgumentTypeError("values must be nonnegative")
    return sorted(set(values))


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def masked_relative(
    value: np.ndarray,
    reference: np.ndarray,
    mask: np.ndarray,
) -> float:
    value = np.asarray(value, dtype=float)
    reference = np.asarray(reference, dtype=float)
    mask = np.asarray(mask, dtype=bool)
    if not np.any(mask):
        return np.nan
    return float(
        np.linalg.norm(value[mask])
        / max(np.linalg.norm(reference[mask]), ZERO_TOL)
    )


def identify_partial_K3(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    support_tolerance: float,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    components = face.face_components(
        state, model, capacities, A, edges, boundary_tolerance
    )
    w = np.asarray(components["w"], dtype=float)
    support_indices = np.flatnonzero(w > support_tolerance)
    graph_components = component_audit.connected_support_components(
        len(capacities), support_indices, edges
    )
    candidates: list[tuple[np.ndarray, np.ndarray, int]] = []
    for graph_component in graph_components:
        nodes = graph_component["nodes"]
        component_edges = graph_component["edges"]
        if len(nodes) != 3 or len(component_edges) != 3:
            continue
        node_set = set(map(int, nodes.tolist()))
        complete = all(
            int(edges[0][edge]) in node_set
            and int(edges[1][edge]) in node_set
            for edge in component_edges
        )
        if not complete:
            continue
        saturated_count = int(np.sum(components["saturated"][nodes]))
        candidates.append((nodes, component_edges, saturated_count))

    partial = [item for item in candidates if item[2] < 3]
    if len(partial) != 1:
        description = [
            {
                "nodes": item[0].tolist(),
                "edges": item[1].tolist(),
                "saturated_count": item[2],
            }
            for item in candidates
        ]
        raise RuntimeError(
            "expected exactly one partially active K3 at split; "
            f"found candidates={description}"
        )
    nodes, component_edges, saturated_count = partial[0]
    return nodes, component_edges, {
        "candidate_count": len(candidates),
        "split_saturated_count": saturated_count,
        "all_K3_candidates": [
            {
                "nodes": item[0].tolist(),
                "edges": item[1].tolist(),
                "saturated_count": item[2],
            }
            for item in candidates
        ],
    }


def local_tangent_algebra(
    active_incidence: np.ndarray,
    rates: np.ndarray,
    rank_tolerance: float,
) -> dict[str, Any]:
    active_incidence = np.asarray(active_incidence, dtype=float)
    rates = np.asarray(rates, dtype=float)
    edge_count = len(rates)
    D = -np.diag(rates)

    if active_incidence.size:
        _, singular_values, vh = np.linalg.svd(
            active_incidence, full_matrices=True
        )
        rank = int(np.sum(singular_values > rank_tolerance))
        Q = vh[rank:].T
        L = (active_incidence @ D) @ np.linalg.pinv(
            active_incidence, rcond=1e-12
        )
        denominator = max(
            np.linalg.norm(active_incidence @ D), ZERO_TOL
        )
        least_squares_residual = float(
            np.linalg.norm(active_incidence @ D - L @ active_incidence)
            / denominator
        )
        L_scalar = -float(np.mean(rates)) * np.eye(
            active_incidence.shape[0]
        )
        component_scalar_residual = float(
            np.linalg.norm(
                active_incidence @ D - L_scalar @ active_incidence
            )
            / denominator
        )
    else:
        rank = 0
        Q = np.eye(edge_count)
        L = np.zeros((0, 0))
        L_scalar = np.zeros((0, 0))
        least_squares_residual = 0.0
        component_scalar_residual = 0.0

    P = Q @ Q.T
    commutator_relative = float(
        np.linalg.norm(D @ P - P @ D)
        / max(np.linalg.norm(D), ZERO_TOL)
    )
    J = Q.T @ D @ Q
    contraction_spectrum = np.sort(
        -np.real(np.linalg.eigvals(J))
    )
    return {
        "rank": rank,
        "nullity": int(Q.shape[1]),
        "Q": Q,
        "P": P,
        "D": D,
        "L_least_squares": L,
        "L_component_scalar": L_scalar,
        "J": J,
        "least_squares_residual": least_squares_residual,
        "component_scalar_residual": component_scalar_residual,
        "commutator_relative": commutator_relative,
        "contraction_spectrum": contraction_spectrum,
    }


def required_K3_rate_equality(
    k3_nodes: np.ndarray,
    k3_edges: np.ndarray,
    saturated: np.ndarray,
    rates: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
) -> dict[str, Any]:
    active_nodes = [int(node) for node in k3_nodes if saturated[node]]
    saturated_count = len(active_nodes)
    constrained_edges: list[int] = []
    if saturated_count == 1:
        active_node = active_nodes[0]
        constrained_edges = [
            local_index
            for local_index, edge in enumerate(k3_edges)
            if active_node
            in (int(edges[0][edge]), int(edges[1][edge]))
        ]
        required_values = rates[constrained_edges]
        condition = "one_active_node_incident_pair_equal"
    elif saturated_count == 2:
        constrained_edges = list(range(3))
        required_values = rates
        condition = "two_active_nodes_all_three_equal"
    elif saturated_count == 0:
        required_values = np.asarray([], dtype=float)
        condition = "no_active_rows_invariance_automatic"
    else:
        # For a fully active K3 the signless incidence is nonsingular and the
        # tangent space is zero, so D-invariance is vacuous.
        required_values = np.asarray([], dtype=float)
        condition = "three_active_nodes_zero_tangent_space"

    absolute_defect = (
        float(np.ptp(required_values)) if len(required_values) else 0.0
    )
    relative_defect = float(
        absolute_defect / max(float(np.mean(np.abs(required_values))), ZERO_TOL)
    ) if len(required_values) else 0.0
    return {
        "condition": condition,
        "active_nodes": active_nodes,
        "constrained_local_edge_indices": constrained_edges,
        "absolute_defect": absolute_defect,
        "relative_defect": relative_defect,
    }


def evaluate_state(
    state: base.DynamicState,
    *,
    step: int,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    k3_nodes: np.ndarray,
    k3_edges: np.ndarray,
    initial_support: np.ndarray,
    boundary_tolerance: float,
    support_tolerance: float,
    rank_tolerance: float,
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, np.ndarray],
]:
    components = face.face_components(
        state, model, capacities, A, edges, boundary_tolerance
    )
    R_matrix, _, _ = base.compute_field_and_updated_coherence(state, model)
    R = R_matrix[edges]

    dt = float(model["dt"])
    gamma = float(model["gamma"])
    eta = float(model["eta"])
    mu = float(model["mu"])
    w = np.asarray(components["w"], dtype=float)
    alpha = np.asarray(components["alpha"], dtype=float)
    modified_F = np.asarray(components["modified_F"], dtype=float)
    field = np.asarray(components["field"], dtype=float)
    row_sum = np.asarray(components["row_sum"], dtype=float)
    slack = np.asarray(components["slack"], dtype=float)
    saturated = np.asarray(components["saturated"], dtype=bool)
    outward = np.asarray(components["outward"], dtype=bool)
    endpoint_rate = np.asarray(components["endpoint_rate"], dtype=float)
    controller = np.asarray(components["controller"], dtype=int)
    support = w > support_tolerance
    rates = gamma + endpoint_rate
    growth = (eta + mu) * R - mu

    active_k3_nodes = k3_nodes[saturated[k3_nodes]]
    C_k3 = A[np.ix_(active_k3_nodes, k3_edges)]
    local_rates = rates[k3_edges]
    local_algebra = local_tangent_algebra(
        C_k3, local_rates, rank_tolerance
    )
    equality = required_K3_rate_equality(
        k3_nodes,
        k3_edges,
        saturated,
        local_rates,
        edges,
    )

    local_field = field[k3_edges]
    tangent_field = local_algebra["P"] @ local_field
    normal_field = local_field - tangent_field
    active_constraint_field = C_k3 @ local_field

    K_global = component_audit.build_controller_matrix(
        len(capacities), np.flatnonzero(support), w, controller, edges
    )
    K_alpha = K_global @ alpha
    node_field_sum = A @ field
    rowsum_controller_residual = row_sum * alpha - K_alpha
    outward_identity_defect = (
        row_sum * alpha - K_alpha - node_field_sum
    )
    k3_saturated_mask = saturated[k3_nodes]
    k3_outward_mask = outward[k3_nodes]
    saturated_local_mask = k3_saturated_mask
    outward_local_mask = k3_outward_mask
    unsaturated_local_mask = ~k3_saturated_mask

    expected_locked_rate = 2.0 * eta / float(np.mean(capacities[k3_nodes]))
    expected_locked_weight = float(np.mean(capacities[k3_nodes])) / 2.0
    both_unsaturated_edges = []
    for edge in k3_edges:
        i = int(edges[0][edge])
        j = int(edges[1][edge])
        if not saturated[i] and not saturated[j]:
            both_unsaturated_edges.append(int(edge))

    node_rows: list[dict[str, Any]] = []
    for node in k3_nodes:
        node_rows.append(
            {
                "step": step,
                "state_elapsed_time": step * dt,
                "legacy_reported_time": (step + 1) * dt,
                "node": int(node),
                "saturated": bool(saturated[node]),
                "outward": bool(outward[node]),
                "row_sum": float(row_sum[node]),
                "capacity": float(capacities[node]),
                "slack": float(slack[node]),
                "row_direction_d": float(components["d"][node]),
                "alpha": float(alpha[node]),
                "total_node_rate_gamma_plus_alpha": float(
                    gamma + alpha[node]
                ),
                "K_alpha": float(K_alpha[node]),
                "row_sum_alpha": float(row_sum[node] * alpha[node]),
                "rowsum_controller_residual": float(
                    rowsum_controller_residual[node]
                ),
                "node_field_sum_Ap": float(node_field_sum[node]),
                "outward_exact_identity_defect": float(
                    outward_identity_defect[node]
                ),
                "unsaturated_controller_load": float(
                    K_alpha[node] if not saturated[node] else 0.0
                ),
                "actual_finite_row_sum_rate": np.nan,
            }
        )

    edge_rows: list[dict[str, Any]] = []
    constrained_global_edges = {
        int(k3_edges[index])
        for index in equality["constrained_local_edge_indices"]
    }
    for local_index, edge in enumerate(k3_edges):
        i = int(edges[0][edge])
        j = int(edges[1][edge])
        controlling_node = int(controller[edge])
        edge_rows.append(
            {
                "step": step,
                "state_elapsed_time": step * dt,
                "legacy_reported_time": (step + 1) * dt,
                "local_edge_index": local_index,
                "edge_index": int(edge),
                "node_i": i,
                "node_j": j,
                "node_i_saturated": bool(saturated[i]),
                "node_j_saturated": bool(saturated[j]),
                "both_endpoints_unsaturated": bool(
                    not saturated[i] and not saturated[j]
                ),
                "in_required_equality_set": bool(
                    int(edge) in constrained_global_edges
                ),
                "weight": float(w[edge]),
                "expected_locked_weight_c_over_2": expected_locked_weight,
                "weight_minus_c_over_2": float(
                    w[edge] - expected_locked_weight
                ),
                "R": float(R[edge]),
                "one_minus_R": float(1.0 - R[edge]),
                "growth_g": float(growth[edge]),
                "growth_minus_eta": float(growth[edge] - eta),
                "modified_F": float(modified_F[edge]),
                "ideal_field_p": float(field[edge]),
                "alpha_i": float(alpha[i]),
                "alpha_j": float(alpha[j]),
                "controller_node": controlling_node,
                "controller_alpha": float(alpha[controlling_node]),
                "endpoint_rho": float(endpoint_rate[edge]),
                "contraction_rate": float(rates[edge]),
                "expected_locked_rate_2eta_over_c": expected_locked_rate,
                "rate_minus_expected_locked": float(
                    rates[edge] - expected_locked_rate
                ),
                "rate_minus_gamma": float(rates[edge] - gamma),
                "actual_finite_weight_rate": np.nan,
                "actual_minus_ideal_field": np.nan,
            }
        )

    local_reference = row_sum[k3_nodes] * alpha[k3_nodes]
    summary = {
        "step": step,
        "state_elapsed_time": step * dt,
        "legacy_reported_time": (step + 1) * dt,
        "face_hash": components["face_hash"],
        "global_support_stable": bool(np.array_equal(support, initial_support)),
        "global_support_size": int(np.sum(support)),
        "global_saturated_count": int(np.sum(saturated)),
        "global_stationarity_ratio": float(components["info"]["P_F_over_F"]),
        "K3_saturated_count": int(np.sum(k3_saturated_mask)),
        "K3_outward_count": int(np.sum(k3_outward_mask)),
        "K3_saturated_nodes": ";".join(
            map(str, k3_nodes[k3_saturated_mask].tolist())
        ),
        "K3_unsaturated_nodes": ";".join(
            map(str, k3_nodes[~k3_saturated_mask].tolist())
        ),
        "K3_active_rank": int(local_algebra["rank"]),
        "K3_tangent_nullity": int(local_algebra["nullity"]),
        "required_rate_condition": equality["condition"],
        "required_rate_equality_absolute_defect": equality["absolute_defect"],
        "required_rate_equality_relative_defect": equality["relative_defect"],
        "K3_rate_min": float(np.min(local_rates)),
        "K3_rate_max": float(np.max(local_rates)),
        "K3_rate_spread": float(np.ptp(local_rates)),
        "K3_rates_json": json_compact(local_rates.tolist()),
        "expected_locked_rate_2eta_over_c": expected_locked_rate,
        "maximum_locked_rate_error": float(
            np.max(np.abs(local_rates - expected_locked_rate))
        ),
        "maximum_one_minus_R": float(
            np.max(np.abs(1.0 - R[k3_edges]))
        ),
        "maximum_growth_minus_eta": float(
            np.max(np.abs(growth[k3_edges] - eta))
        ),
        "maximum_weight_minus_c_over_2": float(
            np.max(np.abs(w[k3_edges] - expected_locked_weight))
        ),
        "both_unsaturated_edge_count": len(both_unsaturated_edges),
        "both_unsaturated_edges": ";".join(map(str, both_unsaturated_edges)),
        "least_squares_CDLC_residual": local_algebra[
            "least_squares_residual"
        ],
        "component_scalar_CDLC_residual": local_algebra[
            "component_scalar_residual"
        ],
        "local_tangent_commutator_relative": local_algebra[
            "commutator_relative"
        ],
        "local_contraction_spectrum_json": json_compact(
            local_algebra["contraction_spectrum"].tolist()
        ),
        "K3_field_norm": float(np.linalg.norm(local_field)),
        "K3_field_over_modified_F": float(
            np.linalg.norm(local_field)
            / max(np.linalg.norm(modified_F[k3_edges]), ZERO_TOL)
        ),
        "K3_tangent_field_norm": float(np.linalg.norm(tangent_field)),
        "K3_normal_field_norm": float(np.linalg.norm(normal_field)),
        "K3_normal_to_total_field": float(
            np.linalg.norm(normal_field)
            / max(np.linalg.norm(local_field), ZERO_TOL)
        ),
        "K3_active_constraint_field_norm": float(
            np.linalg.norm(active_constraint_field)
        ),
        "K3_controller_rowsum_residual_relative_saturated": masked_relative(
            rowsum_controller_residual[k3_nodes],
            local_reference,
            saturated_local_mask,
        ),
        "K3_controller_rowsum_residual_relative_outward": masked_relative(
            rowsum_controller_residual[k3_nodes],
            local_reference,
            outward_local_mask,
        ),
        "K3_unsaturated_controller_load_norm": float(
            np.linalg.norm(K_alpha[k3_nodes][unsaturated_local_mask])
        ),
        "K3_unsaturated_controller_load_fraction": float(
            np.linalg.norm(K_alpha[k3_nodes][unsaturated_local_mask])
            / max(np.linalg.norm(K_alpha[k3_nodes]), ZERO_TOL)
        ),
        "K3_actual_finite_field_norm": np.nan,
        "K3_actual_minus_ideal_field_norm": np.nan,
        "actual_projection_active": False,
    }
    matrices = {
        "C_K3": C_k3,
        "D_K3": local_algebra["D"],
        "Q_K3": local_algebra["Q"],
        "P_K3": local_algebra["P"],
        "J_K3": local_algebra["J"],
        "L_K3_least_squares": local_algebra["L_least_squares"],
        "L_K3_component_scalar": local_algebra["L_component_scalar"],
        "K3_rates": local_rates,
        "K3_field": local_field,
        "K3_slacks": slack[k3_nodes],
        "K3_alpha": alpha[k3_nodes],
        "K3_saturated": k3_saturated_mask.astype(np.uint8),
    }
    return summary, node_rows, edge_rows, matrices


def add_actual_step_information(
    summary: dict[str, Any],
    node_rows: list[dict[str, Any]],
    edge_rows: list[dict[str, Any]],
    *,
    before_w: np.ndarray,
    before_row_sum: np.ndarray,
    state_after: base.DynamicState,
    actual_info: dict[str, Any],
    dt: float,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    k3_nodes: np.ndarray,
    k3_edges: np.ndarray,
) -> None:
    after_w = state_after.B[edges]
    finite_edge_rate = (after_w - before_w) / dt
    after_row_sum = A @ after_w
    finite_row_rate = (after_row_sum - before_row_sum) / dt
    local_finite = finite_edge_rate[k3_edges]
    local_ideal = np.asarray([row["ideal_field_p"] for row in edge_rows])
    summary["K3_actual_finite_field_norm"] = float(
        np.linalg.norm(local_finite)
    )
    summary["K3_actual_minus_ideal_field_norm"] = float(
        np.linalg.norm(local_finite - local_ideal)
    )
    summary["actual_projection_active"] = bool(
        actual_info["actual_projection_active"]
    )
    edge_row_by_index = {int(row["edge_index"]): row for row in edge_rows}
    for edge in k3_edges:
        row = edge_row_by_index[int(edge)]
        row["actual_finite_weight_rate"] = float(finite_edge_rate[edge])
        row["actual_minus_ideal_field"] = float(
            finite_edge_rate[edge] - row["ideal_field_p"]
        )
    node_row_by_index = {int(row["node"]): row for row in node_rows}
    for node in k3_nodes:
        node_row_by_index[int(node)]["actual_finite_row_sum_rate"] = float(
            finite_row_rate[node]
        )


def sustained_restoration_step(
    steps: np.ndarray,
    values: np.ndarray,
    start_step: int,
    tolerance: float,
) -> int | None:
    mask = steps >= start_step
    candidate_steps = steps[mask]
    candidate_values = values[mask]
    finite_good = np.isfinite(candidate_values) & (
        candidate_values <= tolerance
    )
    if not len(finite_good):
        return None
    suffix_good = np.logical_and.accumulate(finite_good[::-1])[::-1]
    indices = np.flatnonzero(suffix_good)
    return int(candidate_steps[indices[0]]) if len(indices) else None


def boundary_switch_sensitivity(
    node_frame: pd.DataFrame,
    k3_nodes: np.ndarray,
    tolerances: list[float],
    dt: float,
) -> pd.DataFrame:
    pivot = node_frame.pivot(index="step", columns="node", values="slack")
    rows: list[dict[str, Any]] = []
    for tolerance in tolerances:
        active_count = (pivot[list(k3_nodes)] <= tolerance).sum(axis=1)
        initial_count = int(active_count.iloc[0])
        increased = active_count.to_numpy() > initial_count
        if np.any(increased):
            index = int(np.flatnonzero(increased)[0])
            switch_step = int(active_count.index[index])
            final_count = int(active_count.iloc[-1])
        else:
            switch_step = -1
            final_count = int(active_count.iloc[-1])
        rows.append(
            {
                "boundary_tolerance": tolerance,
                "initial_K3_active_count": initial_count,
                "first_active_count_increase_step": switch_step,
                "state_elapsed_time": switch_step * dt
                if switch_step >= 0
                else np.nan,
                "legacy_reported_time": (switch_step + 1) * dt
                if switch_step >= 0
                else np.nan,
                "final_K3_active_count": final_count,
            }
        )
    return pd.DataFrame(rows)


def stage_label_map(
    check_steps: dict[int, str],
    switch_step: int | None,
    future_steps: int,
) -> dict[int, str]:
    labels: dict[int, list[str]] = {0: ["split"], future_steps: ["late"]}
    for step, label in check_steps.items():
        labels.setdefault(step, []).append(label)
    if switch_step is not None:
        labels.setdefault(max(0, switch_step - 1), []).append("pre_switch")
        labels.setdefault(switch_step, []).append("post_switch")
    return {step: ";".join(values) for step, values in labels.items()}


def make_report(
    summary: pd.DataFrame,
    edge_frame: pd.DataFrame,
    sensitivity: pd.DataFrame,
    *,
    seed: str,
    k3_nodes: np.ndarray,
    k3_edges: np.ndarray,
    switch_steps: list[int],
    restoration_tolerances: list[float],
    dt: float,
    final_replay_exact: bool,
    final_replay_max_error: float,
) -> str:
    split = summary.iloc[0]
    late = summary.iloc[-1]
    first_switch = switch_steps[0] if switch_steps else None
    lines = [
        "AIEF exceptional K3 transition audit",
        "====================================",
        "",
        "Identity and replay",
        "-------------------",
        f"Seed: {seed}",
        f"K3 nodes: {k3_nodes.tolist()}",
        f"K3 edge indices: {k3_edges.tolist()}",
        f"Trajectory rows: {len(summary)}",
        f"Support stable at every recorded state: {bool(summary['global_support_stable'].all())}",
        f"Final replay exact: {final_replay_exact}",
        f"Final replay maximum absolute error: {final_replay_max_error:.6g}",
        "",
        "Active-set transition",
        "---------------------",
        f"K3 active-set switch steps: {switch_steps}",
    ]
    if first_switch is not None:
        pre = summary.loc[summary["step"] == first_switch - 1].iloc[0]
        post = summary.loc[summary["step"] == first_switch].iloc[0]
        lines.extend(
            [
                f"First switch state step: {first_switch}",
                f"First switch state elapsed time: {first_switch * dt:.12g}",
                f"Legacy reported switch time: {(first_switch + 1) * dt:.12g}",
                (
                    "K3 saturated count: "
                    f"{int(pre['K3_saturated_count'])} -> {int(post['K3_saturated_count'])}"
                ),
                (
                    "K3 tangent nullity: "
                    f"{int(pre['K3_tangent_nullity'])} -> {int(post['K3_tangent_nullity'])}"
                ),
                (
                    "Required rate condition: "
                    f"{pre['required_rate_condition']} -> {post['required_rate_condition']}"
                ),
                (
                    "Required equality defect: "
                    f"{pre['required_rate_equality_absolute_defect']:.6g} -> "
                    f"{post['required_rate_equality_absolute_defect']:.6g}"
                ),
                (
                    "Least-squares CD=LC residual: "
                    f"{pre['least_squares_CDLC_residual']:.6g} -> "
                    f"{post['least_squares_CDLC_residual']:.6g}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "Split and late K3 algebra",
            "-------------------------",
            (
                "Split: "
                f"active={int(split['K3_saturated_count'])}, "
                f"nullity={int(split['K3_tangent_nullity'])}, "
                f"rates={split['K3_rates_json']}, "
                f"LS_CDLC={split['least_squares_CDLC_residual']:.3g}, "
                f"scalar_CDLC={split['component_scalar_CDLC_residual']:.3g}"
            ),
            (
                "Late: "
                f"active={int(late['K3_saturated_count'])}, "
                f"nullity={int(late['K3_tangent_nullity'])}, "
                f"rates={late['K3_rates_json']}, "
                f"LS_CDLC={late['least_squares_CDLC_residual']:.3g}, "
                f"scalar_CDLC={late['component_scalar_CDLC_residual']:.3g}"
            ),
            (
                "Late maximum |rate-2eta/c|: "
                f"{late['maximum_locked_rate_error']:.6g}"
            ),
            (
                "Late maximum |1-R|: "
                f"{late['maximum_one_minus_R']:.6g}"
            ),
            (
                "Late maximum |w-c/2|: "
                f"{late['maximum_weight_minus_c_over_2']:.6g}"
            ),
            "",
            "Pre-switch free-edge test",
            "-------------------------",
        ]
    )
    pre_regime = summary.loc[summary["K3_saturated_count"] == 1]
    free_edges = edge_frame.loc[
        (edge_frame["K3_saturated_count"] == 1)
        & edge_frame["both_endpoints_unsaturated"]
    ]
    lines.extend(
        [
            (
                "Maximum one-active required pair-rate defect: "
                f"{pre_regime['required_rate_equality_absolute_defect'].max():.6g}"
            ),
            (
                "Maximum one-active LS CD=LC residual: "
                f"{pre_regime['least_squares_CDLC_residual'].max():.6g}"
            ),
            f"Free unsaturated-unsaturated edge rows: {len(free_edges)}",
            (
                "Maximum |free-edge rate-gamma|: "
                f"{free_edges['rate_minus_gamma'].abs().max():.6g}"
                if len(free_edges)
                else "Maximum |free-edge rate-gamma|: n/a"
            ),
            "",
            "Post-switch restoration",
            "-----------------------",
        ]
    )
    if first_switch is not None:
        steps = summary["step"].to_numpy(int)
        values = summary["least_squares_CDLC_residual"].to_numpy(float)
        for tolerance in restoration_tolerances:
            restored = sustained_restoration_step(
                steps, values, first_switch, tolerance
            )
            if restored is None:
                lines.append(
                    f"Sustained LS CD=LC <= {tolerance:.3g}: not reached"
                )
            else:
                lines.append(
                    f"Sustained LS CD=LC <= {tolerance:.3g}: "
                    f"step={restored}, state_time={restored * dt:.6g}, "
                    f"time_after_switch={(restored - first_switch) * dt:.6g}"
                )

    lines.extend(
        [
            "",
            "Boundary-tolerance switch sensitivity",
            "-------------------------------------",
        ]
    )
    for _, row in sensitivity.iterrows():
        lines.append(
            f"  tol={row['boundary_tolerance']:.3g}: "
            f"initial={int(row['initial_K3_active_count'])}, "
            f"switch_step={int(row['first_active_count_increase_step'])}, "
            f"legacy_time={row['legacy_reported_time']:.6g}, "
            f"final={int(row['final_K3_active_count'])}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Controller balance on active rows does not imply the edge field is zero.",
            "* A nonzero field with C_active p=0 is tangent drift along the current face.",
            "* The all-node controller equation is not imposed on the remaining unsaturated K3 node.",
            "* The one-active and two-active K3 rate conditions are exact finite-dimensional algebra.",
            "* Residuals from this replay are numerical evidence about the saved dt trajectory.",
            "* Continuum switch claims require consistently regenerated smaller-dt runs.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", default=DEFAULT_EXCEPTIONAL_SEED)
    parser.add_argument(
        "--check-times",
        type=base.parse_float_list,
        default=base.parse_float_list(DEFAULT_CHECK_TIMES),
    )
    parser.add_argument(
        "--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL
    )
    parser.add_argument(
        "--boundary-tol-sweep",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_BOUNDARY_TOL_SWEEP),
    )
    parser.add_argument(
        "--support-tol", type=float, default=DEFAULT_SUPPORT_TOL
    )
    parser.add_argument(
        "--rank-tol", type=float, default=DEFAULT_RANK_TOL
    )
    parser.add_argument(
        "--restoration-tols",
        type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_RESTORATION_TOLS),
    )
    parser.add_argument(
        "--window-radius", type=int, default=DEFAULT_WINDOW_RADIUS
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.boundary_tol, args.support_tol, args.rank_tol) <= 0.0:
        raise ValueError("primary tolerances must be positive")
    if args.window_radius < 0:
        raise ValueError("window radius must be nonnegative")

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
        int(round(time_value / dt)): f"time_{time_value:g}".replace(".", "p")
        for time_value in args.check_times
        if int(round(time_value / dt)) <= future_steps
    }

    summary_rows: list[dict[str, Any]] = []
    node_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    matrix_payload: dict[str, np.ndarray] = {}
    switch_steps: list[int] = []

    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
        expected_final = np.asarray(
            data[base.branch_key("continue", args.seed, "B_final")],
            dtype=float,
        ).copy()

        k3_nodes, k3_edges, identification = identify_partial_K3(
            state,
            model,
            capacities,
            A,
            edges,
            args.boundary_tol,
            args.support_tol,
        )
        initial_support = state.B[edges] > args.support_tol
        previous_k3_saturated: np.ndarray | None = None
        previous_matrices: dict[str, np.ndarray] | None = None

        for step in range(future_steps + 1):
            summary, current_node_rows, current_edge_rows, matrices = evaluate_state(
                state,
                step=step,
                model=model,
                capacities=capacities,
                A=A,
                edges=edges,
                k3_nodes=k3_nodes,
                k3_edges=k3_edges,
                initial_support=initial_support,
                boundary_tolerance=args.boundary_tol,
                support_tolerance=args.support_tol,
                rank_tolerance=args.rank_tol,
            )
            current_k3_saturated = np.asarray(
                matrices["K3_saturated"], dtype=bool
            )
            switched = (
                previous_k3_saturated is not None
                and not np.array_equal(
                    current_k3_saturated, previous_k3_saturated
                )
            )
            if switched:
                switch_steps.append(step)
                if previous_matrices is not None:
                    for name, matrix in previous_matrices.items():
                        matrix_payload[f"pre_switch_{name}"] = matrix
                for name, matrix in matrices.items():
                    matrix_payload[f"post_switch_{name}"] = matrix

            if step == 0:
                for name, matrix in matrices.items():
                    matrix_payload[f"split_{name}"] = matrix
            if step in check_steps:
                label = check_steps[step]
                for name, matrix in matrices.items():
                    matrix_payload[f"{label}_{name}"] = matrix

            if step < future_steps:
                before_w = state.B[edges].copy()
                before_row_sum = A @ before_w
                actual_info = base.actual_step(
                    state,
                    model,
                    capacities,
                    A,
                    edges,
                    args.boundary_tol,
                    audit_operator=False,
                )
                add_actual_step_information(
                    summary,
                    current_node_rows,
                    current_edge_rows,
                    before_w=before_w,
                    before_row_sum=before_row_sum,
                    state_after=state,
                    actual_info=actual_info,
                    dt=dt,
                    A=A,
                    edges=edges,
                    k3_nodes=k3_nodes,
                    k3_edges=k3_edges,
                )
            else:
                for name, matrix in matrices.items():
                    matrix_payload[f"late_{name}"] = matrix

            summary_rows.append(summary)
            node_rows.extend(current_node_rows)
            edge_rows.extend(current_edge_rows)
            previous_k3_saturated = current_k3_saturated.copy()
            previous_matrices = {
                name: matrix.copy() for name, matrix in matrices.items()
            }

        final_replay_exact = bool(np.array_equal(state.B, expected_final))
        final_replay_max_error = float(
            np.max(np.abs(state.B - expected_final))
        )

    summary_frame = pd.DataFrame(summary_rows)
    node_frame = pd.DataFrame(node_rows)
    edge_frame = pd.DataFrame(edge_rows)
    first_switch = switch_steps[0] if switch_steps else None
    labels = stage_label_map(check_steps, first_switch, future_steps)
    for frame in (summary_frame, node_frame, edge_frame):
        frame["stage_labels"] = frame["step"].map(labels).fillna("")
        frame["is_transition_window"] = (
            frame["step"].between(
                first_switch - args.window_radius,
                first_switch + args.window_radius,
            )
            if first_switch is not None
            else False
        )
    edge_frame = edge_frame.merge(
        summary_frame[["step", "K3_saturated_count"]],
        on="step",
        how="left",
        validate="many_to_one",
    )

    sensitivity = boundary_switch_sensitivity(
        node_frame,
        k3_nodes,
        args.boundary_tol_sweep,
        dt,
    )
    transition_summary = summary_frame.loc[
        summary_frame["is_transition_window"]
    ].copy()
    transition_nodes = node_frame.loc[node_frame["is_transition_window"]].copy()
    transition_edges = edge_frame.loc[edge_frame["is_transition_window"]].copy()

    component_audit.atomic_write_csv(
        output_dir / "exceptional_K3_step_summary.csv", summary_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "exceptional_K3_node_trajectory.csv", node_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "exceptional_K3_edge_trajectory.csv", edge_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "exceptional_K3_transition_window_summary.csv",
        transition_summary,
    )
    component_audit.atomic_write_csv(
        output_dir / "exceptional_K3_transition_window_nodes.csv",
        transition_nodes,
    )
    component_audit.atomic_write_csv(
        output_dir / "exceptional_K3_transition_window_edges.csv",
        transition_edges,
    )
    component_audit.atomic_write_csv(
        output_dir / "boundary_tolerance_switch_sensitivity.csv",
        sensitivity,
    )
    component_audit.atomic_savez(
        output_dir / "exceptional_K3_key_matrices.npz", matrix_payload
    )

    report = make_report(
        summary_frame,
        edge_frame,
        sensitivity,
        seed=args.seed,
        k3_nodes=k3_nodes,
        k3_edges=k3_edges,
        switch_steps=switch_steps,
        restoration_tolerances=args.restoration_tols,
        dt=dt,
        final_replay_exact=final_replay_exact,
        final_replay_max_error=final_replay_max_error,
    )
    component_audit.atomic_write_text(
        output_dir / "exceptional_K3_transition_report.txt", report
    )

    source_path = Path(__file__).resolve()
    dependency_paths = {
        "stationarity": Path(base.__file__).resolve(),
        "face_spectrum": Path(face.__file__).resolve(),
        "component_audit": Path(component_audit.__file__).resolve(),
    }
    analysis_manifest = {
        "analysis": "AIEF-1.4 dense exceptional K3 transition audit",
        "source": {
            "path": str(source_path),
            "sha256": file_sha256(source_path),
        },
        "dependencies": {
            name: {"path": str(path), "sha256": file_sha256(path)}
            for name, path in dependency_paths.items()
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
        "K3_identification": identification,
        "future_steps": future_steps,
        "dt": dt,
        "switch_steps": switch_steps,
        "final_replay_exact": final_replay_exact,
        "final_replay_max_error": final_replay_max_error,
        "parameters": {
            "boundary_tolerance": args.boundary_tol,
            "boundary_tolerance_sweep": args.boundary_tol_sweep,
            "support_tolerance": args.support_tol,
            "rank_tolerance": args.rank_tol,
            "restoration_tolerances": args.restoration_tols,
            "window_radius": args.window_radius,
            "check_times": args.check_times,
        },
        "outputs": [
            "exceptional_K3_step_summary.csv",
            "exceptional_K3_node_trajectory.csv",
            "exceptional_K3_edge_trajectory.csv",
            "exceptional_K3_transition_window_summary.csv",
            "exceptional_K3_transition_window_nodes.csv",
            "exceptional_K3_transition_window_edges.csv",
            "boundary_tolerance_switch_sensitivity.csv",
            "exceptional_K3_key_matrices.npz",
            "exceptional_K3_transition_report.txt",
        ],
        "interpretation_constraints": [
            "This is a deterministic replay of one frozen seed, not a new independent experiment.",
            "Controller balance on active rows is not full edge stationarity.",
            "The all-node controller equation is not imposed on unsaturated K3 rows.",
            "The K3 rate-equality conditions are exact for the identified active incidence matrix.",
            "The saved dt trajectory cannot by itself prove a continuum active-switch result.",
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
