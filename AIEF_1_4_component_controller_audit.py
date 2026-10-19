#!/usr/bin/env python3
"""Component, locking, controller, and explicit-intertwiner audit for AIEF-1.4.

This analysis is deliberately downstream of the frozen AIEF-1.4 run.  It does
not generate new simulations or alter saved states.  It tests the proposed
mechanistic chain

    locked active edges + edge stationarity + saturated support nodes
        -> controller equilibrium on the active rows
        -> constant alpha on each support component
        -> regular components with rate k*eta/c and weight c/k
        -> a component-scalar explicit intertwiner C D = L_component C
        -> complete tangent spectra from signless-incidence nullities.

The script also evaluates the exceptional seed at split, requested checkpoint,
pre-switch, post-switch, and late states.  Controller residuals are separated
between outward saturated, all saturated, and unsaturated rows.  This is
important because diag(c) alpha = K alpha is not an equation on arbitrary
unsaturated rows.

Principal outputs
-----------------
state_mechanism_summary.csv
    One row per split state and exceptional stage.
component_mechanism_audit.csv
    Support-component topology, locking, regularity, rates, weights, and
    signless-incidence nullities.
controller_residual_by_node.csv
    Per-node masked controller diagnostics, including the exact outward-row
    identity involving the edge-stationarity defect.
edge_locking_balance_audit.csv
    Per-positive-edge R, growth, weight, controller, rate, and balance values.
component_controller_matrices.npz
    C, D, least-squares L, explicit component L, K, tangent projector, and J.
component_controller_report.txt
analysis_manifest.json

No claim that the ideal admissibility map is directionally differentiable is
made here.  All tangent conclusions remain conditional on the fixed-stratum
operator already derived in the preceding analyses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections import deque
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_face_spectrum_analysis as face


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_SCALAR = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_scalar_summary.csv"
)
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_component_controller_audit"
DEFAULT_EXCEPTIONAL_SEED = "4619122171158768524"
DEFAULT_EXCEPTIONAL_CHECK_TIMES = "100,120,123,125,150"
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_SUPPORT_TOL = 1e-14
DEFAULT_RATE_TOL = 1e-8
DEFAULT_LOCK_TOL = 1e-8
DEFAULT_BALANCE_TOL = 1e-8
DEFAULT_RANK_TOL = 1e-10
ZERO_TOL = 1e-14


def file_sha256(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_dumps(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def atomic_write_text(path: str | os.PathLike[str], text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
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


def atomic_write_csv(path: str | os.PathLike[str], frame: pd.DataFrame) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    os.close(fd)
    try:
        frame.to_csv(temporary, index=False)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def atomic_savez(path: str | os.PathLike[str], payload: dict[str, np.ndarray]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".npz", dir=path.parent
    )
    os.close(fd)
    try:
        np.savez_compressed(temporary, **payload)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


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


def maximum_absolute(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    return float(np.max(np.abs(values))) if values.size else 0.0


def connected_support_components(
    node_count: int,
    support_indices: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
) -> list[dict[str, np.ndarray]]:
    """Return deterministic edge-containing connected support components."""
    adjacency: list[list[tuple[int, int]]] = [[] for _ in range(node_count)]
    for edge in np.asarray(support_indices, dtype=int):
        i = int(edges[0][edge])
        j = int(edges[1][edge])
        adjacency[i].append((j, int(edge)))
        adjacency[j].append((i, int(edge)))

    visited = np.zeros(node_count, dtype=bool)
    result: list[dict[str, np.ndarray]] = []
    for start in range(node_count):
        if visited[start] or not adjacency[start]:
            continue
        queue: deque[int] = deque([start])
        visited[start] = True
        nodes: list[int] = []
        component_edges: set[int] = set()
        while queue:
            node = queue.popleft()
            nodes.append(node)
            for neighbor, edge in adjacency[node]:
                component_edges.add(edge)
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        result.append(
            {
                "nodes": np.asarray(sorted(nodes), dtype=int),
                "edges": np.asarray(sorted(component_edges), dtype=int),
            }
        )
    result.sort(key=lambda item: int(item["nodes"][0]))
    return result


def component_bipartite(
    nodes: np.ndarray,
    component_edges: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
) -> bool:
    node_set = set(map(int, nodes.tolist()))
    adjacency: dict[int, list[int]] = {node: [] for node in node_set}
    for edge in component_edges:
        i = int(edges[0][edge])
        j = int(edges[1][edge])
        adjacency[i].append(j)
        adjacency[j].append(i)
    colors: dict[int, int] = {}
    for start in sorted(node_set):
        if start in colors:
            continue
        colors[start] = 0
        queue: deque[int] = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in adjacency[node]:
                if neighbor not in colors:
                    colors[neighbor] = 1 - colors[node]
                    queue.append(neighbor)
                elif colors[neighbor] == colors[node]:
                    return False
    return True


def support_degrees(
    nodes: np.ndarray,
    component_edges: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
) -> np.ndarray:
    lookup = {int(node): index for index, node in enumerate(nodes)}
    degrees = np.zeros(len(nodes), dtype=int)
    for edge in component_edges:
        degrees[lookup[int(edges[0][edge])]] += 1
        degrees[lookup[int(edges[1][edge])]] += 1
    return degrees


def build_controller_matrix(
    node_count: int,
    support_indices: np.ndarray,
    w: np.ndarray,
    controller: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
) -> np.ndarray:
    K = np.zeros((node_count, node_count), dtype=float)
    for edge in support_indices:
        i = int(edges[0][edge])
        j = int(edges[1][edge])
        controlling_node = int(controller[edge])
        K[i, controlling_node] += w[edge]
        K[j, controlling_node] += w[edge]
    return K


def spectrum_error(left: np.ndarray, right: np.ndarray) -> float:
    left = np.sort(np.asarray(left, dtype=float))
    right = np.sort(np.asarray(right, dtype=float))
    if len(left) != len(right):
        return np.inf
    return float(np.max(np.abs(left - right))) if len(left) else 0.0


def safe_stage_key(seed: str, stage: str) -> str:
    cleaned = "".join(character if character.isalnum() else "_" for character in stage)
    return f"seed_{seed}_{cleaned}"


def audit_state(
    state: base.DynamicState,
    *,
    seed: str,
    state_kind: str,
    stage: str,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    support_tolerance: float,
    rate_tolerance: float,
    lock_tolerance: float,
    balance_tolerance: float,
    rank_tolerance: float,
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, np.ndarray],
]:
    components = face.face_components(
        state, model, capacities, A, edges, boundary_tolerance
    )
    R_matrix, _, _ = base.compute_field_and_updated_coherence(state, model)
    R = R_matrix[edges]

    gamma = float(model["gamma"])
    eta = float(model["eta"])
    mu = float(model["mu"])
    w = np.asarray(components["w"], dtype=float)
    modified_F = np.asarray(components["modified_F"], dtype=float)
    alpha = np.asarray(components["alpha"], dtype=float)
    row_sum = np.asarray(components["row_sum"], dtype=float)
    slack = np.asarray(components["slack"], dtype=float)
    saturated = np.asarray(components["saturated"], dtype=bool)
    outward = np.asarray(components["outward"], dtype=bool)
    endpoint_rate = np.asarray(components["endpoint_rate"], dtype=float)
    controller = np.asarray(components["controller"], dtype=int)
    Q = np.asarray(components["basis"], dtype=float)

    # Respect a user-specified support tolerance for this audit.  The frozen
    # face analysis uses 1e-14; disagreement is surfaced rather than hidden.
    support = w > support_tolerance
    face_support = np.asarray(components["support"], dtype=bool)
    support_indices = np.flatnonzero(support)
    positive_nodes = (A[:, support] @ np.ones(np.sum(support))) > 0 if np.any(support) else np.zeros(len(capacities), dtype=bool)

    rates_all = gamma + endpoint_rate
    growth = (eta + mu) * R - mu
    stationarity_defect = modified_F - w * endpoint_rate
    node_stationarity_defect = A @ stationarity_defect
    zero_edge_positive_forcing = (
        float(np.max(np.maximum(modified_F[~support], 0.0)))
        if np.any(~support)
        else 0.0
    )

    K = build_controller_matrix(
        len(capacities), support_indices, w, controller, edges
    )
    K_alpha = K @ alpha
    capacity_controller_residual = capacities * alpha - K_alpha
    rowsum_controller_residual = row_sum * alpha - K_alpha
    outward_identity_defect = (
        row_sum * alpha - K_alpha - node_stationarity_defect
    )

    positive_degree = (
        A[:, support] @ np.ones(np.sum(support))
        if np.any(support)
        else np.zeros(len(capacities))
    ).astype(int)

    graph_components = connected_support_components(
        len(capacities), support_indices, edges
    )
    node_component = np.full(len(capacities), -1, dtype=int)
    edge_component = np.full(len(w), -1, dtype=int)
    component_rows: list[dict[str, Any]] = []

    predicted_component_spectrum: list[float] = []
    component_rate_means: dict[int, float] = {}
    component_mechanism_passes: list[bool] = []
    component_uniform_passes: list[bool] = []

    for component_id, graph_component in enumerate(graph_components):
        nodes = graph_component["nodes"]
        component_edges = graph_component["edges"]
        node_component[nodes] = component_id
        edge_component[component_edges] = component_id
        degrees = support_degrees(nodes, component_edges, edges)
        regular = bool(len(degrees) and np.all(degrees == degrees[0]))
        regular_degree = int(degrees[0]) if regular else -1
        complete = bool(
            len(component_edges) == len(nodes) * (len(nodes) - 1) // 2
        )
        bipartite = component_bipartite(nodes, component_edges, edges)

        unsigned_incidence = A[np.ix_(nodes, component_edges)]
        unsigned_rank = int(
            np.linalg.matrix_rank(unsigned_incidence, tol=rank_tolerance)
        )
        unsigned_nullity = int(len(component_edges) - unsigned_rank)
        active_nodes = nodes[saturated[nodes]]
        active_incidence = A[np.ix_(active_nodes, component_edges)]
        active_rank = int(
            np.linalg.matrix_rank(active_incidence, tol=rank_tolerance)
        ) if active_incidence.size else 0
        active_nullity = int(len(component_edges) - active_rank)

        component_rates = rates_all[component_edges]
        component_rate_mean = float(np.mean(component_rates))
        component_rate_spread = float(np.ptp(component_rates))
        component_rate_means[component_id] = component_rate_mean
        component_alpha = alpha[nodes]
        component_R = R[component_edges]
        component_growth = growth[component_edges]
        component_w = w[component_edges]
        component_defect = stationarity_defect[component_edges]

        expected_rate = (
            regular_degree * eta / float(np.mean(capacities[nodes]))
            if regular and regular_degree > 0
            else np.nan
        )
        expected_weight = (
            float(np.mean(capacities[nodes])) / regular_degree
            if regular and regular_degree > 0
            else np.nan
        )
        rate_error = (
            maximum_absolute(component_rates - expected_rate)
            if np.isfinite(expected_rate)
            else np.nan
        )
        weight_error = (
            maximum_absolute(component_w - expected_weight)
            if np.isfinite(expected_weight)
            else np.nan
        )
        locked = bool(maximum_absolute(1.0 - component_R) <= lock_tolerance)
        rate_uniform = bool(component_rate_spread <= rate_tolerance)
        alpha_uniform = bool(np.ptp(component_alpha) <= rate_tolerance)
        balanced = bool(
            np.linalg.norm(component_defect)
            / max(np.linalg.norm(modified_F[component_edges]), ZERO_TOL)
            <= balance_tolerance
        )
        all_saturated = bool(np.all(saturated[nodes]))
        all_outward = bool(np.all(outward[nodes]))
        mechanism_pass = bool(
            all_saturated
            and all_outward
            and regular
            and locked
            and balanced
            and zero_edge_positive_forcing <= balance_tolerance
            and rate_uniform
            and alpha_uniform
            and np.isfinite(rate_error)
            and rate_error <= rate_tolerance
            and np.isfinite(weight_error)
            and weight_error <= lock_tolerance
        )
        component_mechanism_passes.append(mechanism_pass)
        component_uniform_passes.append(rate_uniform)
        predicted_component_spectrum.extend(
            [component_rate_mean] * active_nullity
        )

        theoretical_rank = (
            len(nodes) - 1 if bipartite else len(nodes)
        )
        theoretical_nullity = int(len(component_edges) - theoretical_rank)
        clique_nullity = int(
            len(nodes) * (len(nodes) - 3) // 2
        ) if complete and len(nodes) >= 3 else np.nan

        component_rows.append(
            {
                "seed": seed,
                "state_kind": state_kind,
                "stage": stage,
                "component_id": component_id,
                "node_indices": ";".join(map(str, nodes.tolist())),
                "edge_indices": ";".join(map(str, component_edges.tolist())),
                "node_count": int(len(nodes)),
                "edge_count": int(len(component_edges)),
                "degree_values_json": json_dumps(degrees.tolist()),
                "degree_min": int(np.min(degrees)),
                "degree_max": int(np.max(degrees)),
                "regular": regular,
                "regular_degree": regular_degree if regular else np.nan,
                "complete_graph": complete,
                "bipartite": bipartite,
                "all_nodes_saturated": all_saturated,
                "all_nodes_outward": all_outward,
                "unsigned_incidence_rank": unsigned_rank,
                "unsigned_incidence_rank_formula": theoretical_rank,
                "unsigned_incidence_rank_formula_matches": bool(
                    unsigned_rank == theoretical_rank
                ),
                "unsigned_nullity": unsigned_nullity,
                "unsigned_nullity_formula": theoretical_nullity,
                "active_saturated_node_count": int(len(active_nodes)),
                "active_incidence_rank": active_rank,
                "active_tangent_nullity": active_nullity,
                "complete_graph_nullity": clique_nullity,
                "component_rate_mean": component_rate_mean,
                "component_rate_min": float(np.min(component_rates)),
                "component_rate_max": float(np.max(component_rates)),
                "component_rate_spread": component_rate_spread,
                "component_rate_uniform": rate_uniform,
                "alpha_min": float(np.min(component_alpha)),
                "alpha_max": float(np.max(component_alpha)),
                "alpha_spread": float(np.ptp(component_alpha)),
                "alpha_uniform": alpha_uniform,
                "expected_degree_rate": expected_rate,
                "maximum_degree_rate_error": rate_error,
                "weight_mean": float(np.mean(component_w)),
                "weight_min": float(np.min(component_w)),
                "weight_max": float(np.max(component_w)),
                "weight_spread": float(np.ptp(component_w)),
                "expected_weight_c_over_k": expected_weight,
                "maximum_c_over_k_weight_error": weight_error,
                "R_min": float(np.min(component_R)),
                "R_mean": float(np.mean(component_R)),
                "maximum_one_minus_R": maximum_absolute(1.0 - component_R),
                "locked_R_within_tolerance": locked,
                "growth_mean": float(np.mean(component_growth)),
                "growth_spread": float(np.ptp(component_growth)),
                "maximum_growth_minus_eta": maximum_absolute(
                    component_growth - eta
                ),
                "edge_balance_relative": float(
                    np.linalg.norm(component_defect)
                    / max(
                        np.linalg.norm(modified_F[component_edges]),
                        ZERO_TOL,
                    )
                ),
                "edge_balance_within_tolerance": balanced,
                "conditional_regular_component_mechanism_pass": mechanism_pass,
            }
        )

    # C and D are restricted to the same support convention used in this audit.
    saturated_indices = np.flatnonzero(saturated)
    C = A[np.ix_(saturated_indices, support_indices)]
    D = -np.diag(rates_all[support_indices])
    if C.size:
        L_least_squares = (C @ D) @ np.linalg.pinv(C, rcond=1e-12)
        least_squares_residual = float(
            np.linalg.norm(C @ D - L_least_squares @ C)
            / max(np.linalg.norm(C @ D), ZERO_TOL)
        )
    else:
        L_least_squares = np.zeros((len(saturated_indices), len(saturated_indices)))
        least_squares_residual = 0.0

    # Explicit mechanism: each saturated node row receives the mean rate of
    # its support component.  If D is component-scalar this proves CD=L C
    # without fitting L.  Isolated saturated rows do not act on C and get 0.
    L_component = np.zeros_like(L_least_squares)
    for local_row, node in enumerate(saturated_indices):
        component_id = int(node_component[node])
        if component_id >= 0:
            L_component[local_row, local_row] = -component_rate_means[component_id]
    explicit_residual = float(
        np.linalg.norm(C @ D - L_component @ C)
        / max(np.linalg.norm(C @ D), ZERO_TOL)
    ) if C.size else 0.0
    fitted_explicit_action_difference = float(
        np.linalg.norm((L_least_squares - L_component) @ C)
        / max(np.linalg.norm(C @ D), ZERO_TOL)
    ) if C.size else 0.0

    # Build the tangent basis using the audit support.  Usually this is exactly
    # the frozen face basis; the support mismatch flag catches any difference.
    if len(support_indices):
        audit_constraint = C
        if audit_constraint.size:
            _, singular_values, vh = np.linalg.svd(
                audit_constraint, full_matrices=True
            )
            rank = int(np.sum(singular_values > rank_tolerance))
            support_basis = vh[rank:].T
        else:
            support_basis = np.eye(len(support_indices))
        Q_audit = np.zeros((len(w), support_basis.shape[1]))
        Q_audit[support_indices, :] = support_basis
    else:
        Q_audit = np.zeros((len(w), 0))
    P_tangent = Q_audit @ Q_audit.T
    D_full = np.diag(-rates_all)
    J = Q_audit.T @ D_full @ Q_audit
    observed_contraction_spectrum = np.sort(
        -np.real(np.linalg.eigvals(J))
    )
    predicted_component_spectrum_array = np.sort(
        np.asarray(predicted_component_spectrum, dtype=float)
    )
    component_spectrum_error = spectrum_error(
        observed_contraction_spectrum,
        predicted_component_spectrum_array,
    )
    commutator_relative = float(
        np.linalg.norm(D_full @ P_tangent - P_tangent @ D_full)
        / max(np.linalg.norm(D_full), ZERO_TOL)
    )

    node_rows: list[dict[str, Any]] = []
    for node in range(len(capacities)):
        node_rows.append(
            {
                "seed": seed,
                "state_kind": state_kind,
                "stage": stage,
                "node": node,
                "support_component_id": int(node_component[node]),
                "positive_support_degree": int(positive_degree[node]),
                "positive_support_node": bool(positive_nodes[node]),
                "saturated": bool(saturated[node]),
                "outward": bool(outward[node]),
                "row_sum": float(row_sum[node]),
                "capacity": float(capacities[node]),
                "slack": float(slack[node]),
                "alpha": float(alpha[node]),
                "total_node_rate_gamma_plus_alpha": float(gamma + alpha[node]),
                "K_alpha": float(K_alpha[node]),
                "capacity_alpha": float(capacities[node] * alpha[node]),
                "row_sum_alpha": float(row_sum[node] * alpha[node]),
                "capacity_controller_residual": float(
                    capacity_controller_residual[node]
                ),
                "rowsum_controller_residual": float(
                    rowsum_controller_residual[node]
                ),
                "node_stationarity_defect_Ap": float(
                    node_stationarity_defect[node]
                ),
                "outward_exact_identity_defect": float(
                    outward_identity_defect[node]
                ),
                "unsaturated_controller_load": float(
                    K_alpha[node] if not saturated[node] else 0.0
                ),
            }
        )

    edge_rows: list[dict[str, Any]] = []
    for edge in support_indices:
        i = int(edges[0][edge])
        j = int(edges[1][edge])
        controlling_node = int(controller[edge])
        regular_degree = np.nan
        component_id = int(edge_component[edge])
        if component_id >= 0:
            component_row = component_rows[component_id]
            regular_degree = component_row["regular_degree"]
        edge_rows.append(
            {
                "seed": seed,
                "state_kind": state_kind,
                "stage": stage,
                "edge_index": int(edge),
                "node_i": i,
                "node_j": j,
                "support_component_id": component_id,
                "component_regular_degree": regular_degree,
                "weight": float(w[edge]),
                "R": float(R[edge]),
                "one_minus_R": float(1.0 - R[edge]),
                "growth_g": float(growth[edge]),
                "growth_minus_eta": float(growth[edge] - eta),
                "modified_F": float(modified_F[edge]),
                "alpha_i": float(alpha[i]),
                "alpha_j": float(alpha[j]),
                "controller_node": controlling_node,
                "controller_alpha": float(alpha[controlling_node]),
                "endpoint_rho": float(endpoint_rate[edge]),
                "contraction_rate_gamma_plus_rho": float(rates_all[edge]),
                "stationarity_defect": float(stationarity_defect[edge]),
                "expected_weight_from_growth_over_rate": float(
                    growth[edge] / rates_all[edge]
                ) if abs(rates_all[edge]) > ZERO_TOL else np.nan,
            }
        )

    topology_labels: list[str] = []
    rate_labels: list[str] = []
    for row in component_rows:
        if row["complete_graph"]:
            topology = f"K{int(row['node_count'])}"
        else:
            degree_label = (
                str(int(row["regular_degree"]))
                if np.isfinite(row["regular_degree"])
                else "irregular"
            )
            topology = (
                f"G(n={int(row['node_count'])},m={int(row['edge_count'])},"
                f"k={degree_label},bip={int(bool(row['bipartite']))})"
            )
        if not row["all_nodes_saturated"]:
            topology += "[partial-active]"
        topology_labels.append(topology)
        rate_labels.append(
            f"{row['component_rate_mean']:.12g}x{int(row['active_tangent_nullity'])}"
        )

    active_saturated = saturated & positive_nodes
    active_outward = outward & positive_nodes
    unsaturated_positive = (~saturated) & positive_nodes
    all_rows = np.ones(len(capacities), dtype=bool)
    capacity_relative_all = masked_relative(
        capacity_controller_residual,
        capacities * alpha,
        all_rows,
    )
    capacity_relative_active_saturated = masked_relative(
        capacity_controller_residual,
        capacities * alpha,
        active_saturated,
    )
    rowsum_relative_active_saturated = masked_relative(
        rowsum_controller_residual,
        row_sum * alpha,
        active_saturated,
    )
    rowsum_relative_active_outward = masked_relative(
        rowsum_controller_residual,
        row_sum * alpha,
        active_outward,
    )
    outward_identity_relative = masked_relative(
        outward_identity_defect,
        row_sum * alpha,
        active_outward,
    )
    unsaturated_load_fraction = float(
        np.linalg.norm(K_alpha[unsaturated_positive])
        / max(np.linalg.norm(K_alpha[positive_nodes]), ZERO_TOL)
    ) if np.any(positive_nodes) else np.nan

    state_summary = {
        "seed": seed,
        "state_kind": state_kind,
        "stage": stage,
        "face_hash": components["face_hash"],
        "support_size": int(np.sum(support)),
        "face_support_size": int(np.sum(face_support)),
        "support_mask_matches_face_analysis": bool(
            np.array_equal(support, face_support)
        ),
        "positive_support_node_count": int(np.sum(positive_nodes)),
        "support_component_count": int(len(graph_components)),
        "component_topology_signature": "+".join(topology_labels),
        "component_rate_nullity_signature": "+".join(rate_labels),
        "saturated_node_count": int(np.sum(saturated)),
        "outward_node_count": int(np.sum(outward)),
        "all_positive_support_nodes_saturated": bool(
            np.all(saturated[positive_nodes]) if np.any(positive_nodes) else True
        ),
        "all_positive_support_nodes_outward": bool(
            np.all(outward[positive_nodes]) if np.any(positive_nodes) else True
        ),
        "tangent_dimension": int(Q_audit.shape[1]),
        "face_tangent_dimension": int(Q.shape[1]),
        "sum_component_active_nullities": int(
            sum(row["active_tangent_nullity"] for row in component_rows)
        ),
        "component_nullities_cover_tangent": bool(
            sum(row["active_tangent_nullity"] for row in component_rows)
            == Q_audit.shape[1]
        ),
        "all_components_rate_uniform": bool(
            all(component_uniform_passes)
        ),
        "all_components_conditional_mechanism_pass": bool(
            all(component_mechanism_passes)
        ),
        "least_squares_CDLC_residual_relative": least_squares_residual,
        "explicit_component_CDLC_residual_relative": explicit_residual,
        "fitted_vs_explicit_action_difference_relative": (
            fitted_explicit_action_difference
        ),
        "tangent_commutator_relative": commutator_relative,
        "component_spectrum_max_error": component_spectrum_error,
        "component_spectrum_matches_rate_tolerance": bool(
            component_spectrum_error <= rate_tolerance
        ),
        "observed_contraction_spectrum_json": json_dumps(
            observed_contraction_spectrum.tolist()
        ),
        "predicted_component_spectrum_json": json_dumps(
            predicted_component_spectrum_array.tolist()
        ),
        "edge_stationarity_relative": float(
            np.linalg.norm(stationarity_defect)
            / max(np.linalg.norm(modified_F), ZERO_TOL)
        ),
        "support_edge_stationarity_relative": float(
            np.linalg.norm(stationarity_defect[support])
            / max(np.linalg.norm(modified_F[support]), ZERO_TOL)
        ) if np.any(support) else 0.0,
        "maximum_zero_edge_positive_forcing": zero_edge_positive_forcing,
        "controller_capacity_residual_relative_all_nodes": capacity_relative_all,
        "controller_capacity_residual_relative_active_saturated": (
            capacity_relative_active_saturated
        ),
        "controller_rowsum_residual_relative_active_saturated": (
            rowsum_relative_active_saturated
        ),
        "controller_rowsum_residual_relative_active_outward": (
            rowsum_relative_active_outward
        ),
        "outward_exact_identity_residual_relative": outward_identity_relative,
        "unsaturated_positive_controller_load_fraction": (
            unsaturated_load_fraction
        ),
        "maximum_capacity_vs_rowsum_alpha_difference": maximum_absolute(
            (capacities - row_sum) * alpha
        ),
        "maximum_one_minus_R_on_support": maximum_absolute(1.0 - R[support])
        if np.any(support)
        else 0.0,
        "maximum_growth_minus_eta_on_support": maximum_absolute(
            growth[support] - eta
        ) if np.any(support) else 0.0,
    }

    matrices = {
        "C_active": C,
        "D_channel": D,
        "L_least_squares": L_least_squares,
        "L_component_explicit": L_component,
        "K_controller": K,
        "P_tangent": P_tangent,
        "J_tangent": J,
        "node_component": node_component,
        "edge_component": edge_component,
    }
    return state_summary, component_rows, node_rows, edge_rows, matrices


def format_metric(value: Any) -> str:
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.6g}"
    return str(value)


def make_report(
    state_summary: pd.DataFrame,
    components: pd.DataFrame,
    exceptional_seed: str,
    tolerances: dict[str, float],
) -> str:
    split = state_summary.loc[state_summary["state_kind"] == "split"]
    exceptional = state_summary.loc[
        state_summary["state_kind"] == "exceptional_stage"
    ]
    component_split = components.loc[components["state_kind"] == "split"]

    lines = [
        "AIEF component, controller, and explicit-intertwiner audit",
        "========================================================",
        "",
        "Frozen split states",
        "-------------------",
        f"Seeds: {len(split)}",
        (
            "All positive support nodes saturated: "
            f"{int(split['all_positive_support_nodes_saturated'].sum())}/{len(split)}"
        ),
        (
            "All components rate-uniform: "
            f"{int(split['all_components_rate_uniform'].sum())}/{len(split)}"
        ),
        (
            "All components pass the full conditional mechanism audit: "
            f"{int(split['all_components_conditional_mechanism_pass'].sum())}/{len(split)}"
        ),
        (
            "Explicit component spectra match: "
            f"{int(split['component_spectrum_matches_rate_tolerance'].sum())}/{len(split)}"
        ),
        (
            "Median least-squares CD=LC residual: "
            f"{split['least_squares_CDLC_residual_relative'].median():.6g}"
        ),
        (
            "Median explicit-component CD=LC residual: "
            f"{split['explicit_component_CDLC_residual_relative'].median():.6g}"
        ),
        (
            "Maximum explicit-component CD=LC residual: "
            f"{split['explicit_component_CDLC_residual_relative'].max():.6g}"
        ),
        (
            "Maximum component-spectrum error: "
            f"{split['component_spectrum_max_error'].max():.6g}"
        ),
        "",
        "Split-state support components",
        "------------------------------",
    ]

    if len(component_split):
        grouped = (
            component_split.groupby(
                [
                    "node_count",
                    "edge_count",
                    "regular_degree",
                    "complete_graph",
                    "bipartite",
                    "active_tangent_nullity",
                ],
                dropna=False,
            )
            .size()
            .reset_index(name="component_count")
            .sort_values(
                ["regular_degree", "node_count", "edge_count"],
                na_position="last",
            )
        )
        for _, row in grouped.iterrows():
            lines.append(
                "  "
                f"n={int(row['node_count'])}, m={int(row['edge_count'])}, "
                f"k={format_metric(row['regular_degree'])}, "
                f"complete={bool(row['complete_graph'])}, "
                f"bipartite={bool(row['bipartite'])}, "
                f"nullity={int(row['active_tangent_nullity'])}: "
                f"count={int(row['component_count'])}"
            )

    lines.extend(["", "Split-state component combinations", "----------------------------------"])
    combinations = (
        split.groupby("component_topology_signature", dropna=False)
        .size()
        .reset_index(name="seed_count")
        .sort_values(["seed_count", "component_topology_signature"], ascending=[False, True])
    )
    for _, row in combinations.iterrows():
        lines.append(
            f"  {row['component_topology_signature']}: seeds={int(row['seed_count'])}"
        )

    lines.extend(
        [
            "",
            "Controller residual decomposition at split",
            "------------------------------------------",
            (
                "Median all-node capacity residual: "
                f"{split['controller_capacity_residual_relative_all_nodes'].median():.6g}"
            ),
            (
                "Median active-saturated row-sum residual: "
                f"{split['controller_rowsum_residual_relative_active_saturated'].median():.6g}"
            ),
            (
                "Median active-outward row-sum residual: "
                f"{split['controller_rowsum_residual_relative_active_outward'].median():.6g}"
            ),
            (
                "Maximum exact outward identity defect: "
                f"{split['outward_exact_identity_residual_relative'].max():.6g}"
            ),
            (
                "Maximum unsaturated positive-node controller-load fraction: "
                f"{split['unsaturated_positive_controller_load_fraction'].max():.6g}"
            ),
            "",
            f"Exceptional stages for seed {exceptional_seed}",
            "-" * (28 + len(exceptional_seed)),
        ]
    )
    for _, row in exceptional.iterrows():
        lines.append(
            f"  {row['stage']}: "
            f"dim={int(row['tangent_dimension'])}, "
            f"components={int(row['support_component_count'])}, "
            f"all_support_saturated={bool(row['all_positive_support_nodes_saturated'])}, "
            f"LS_CDLC={row['least_squares_CDLC_residual_relative']:.3g}, "
            f"explicit_CDLC={row['explicit_component_CDLC_residual_relative']:.3g}, "
            f"all_controller={row['controller_capacity_residual_relative_all_nodes']:.3g}, "
            f"sat_controller={row['controller_rowsum_residual_relative_active_saturated']:.3g}, "
            f"unsat_load={row['unsaturated_positive_controller_load_fraction']:.3g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Least-squares and explicit-component intertwiners are separate diagnostics.",
            "* The all-node controller equation is not required on unsaturated rows.",
            "* The outward identity with A p is an implementation identity, not an equilibrium test.",
            "* Degree rates k*eta/c require locked R=1, saturation, and edge stationarity.",
            "* Complete-graph labels are accepted only when directly verified from support edges.",
            "* Signless-incidence nullity is not the usual oriented graph cycle-space dimension.",
            "* Exceptional post-switch deviations require timestep/tolerance convergence before a continuum claim.",
            "",
            "Tolerances",
            "----------",
        ]
    )
    for key, value in tolerances.items():
        lines.append(f"  {key}: {value:.6g}")
    lines.append("")
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scalar", default=DEFAULT_SCALAR)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--exceptional-seed", default=DEFAULT_EXCEPTIONAL_SEED)
    parser.add_argument(
        "--exceptional-check-times",
        type=base.parse_float_list,
        default=base.parse_float_list(DEFAULT_EXCEPTIONAL_CHECK_TIMES),
    )
    parser.add_argument(
        "--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL
    )
    parser.add_argument(
        "--support-tol", type=float, default=DEFAULT_SUPPORT_TOL
    )
    parser.add_argument("--rate-tol", type=float, default=DEFAULT_RATE_TOL)
    parser.add_argument("--lock-tol", type=float, default=DEFAULT_LOCK_TOL)
    parser.add_argument(
        "--balance-tol", type=float, default=DEFAULT_BALANCE_TOL
    )
    parser.add_argument("--rank-tol", type=float, default=DEFAULT_RANK_TOL)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    input_paths = [args.scalar, args.npz, args.manifest]
    for path in input_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    tolerances = {
        "boundary_tolerance": float(args.boundary_tol),
        "support_tolerance": float(args.support_tol),
        "rate_tolerance": float(args.rate_tol),
        "locking_tolerance": float(args.lock_tol),
        "balance_tolerance": float(args.balance_tol),
        "rank_tolerance": float(args.rank_tol),
    }
    if any(value <= 0.0 for value in tolerances.values()):
        raise ValueError("all tolerances must be positive")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scalar = pd.read_csv(args.scalar, dtype={"seed": str})
    scalar["seed"] = scalar["seed"].astype(str)
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = manifest["model"]
    node_count = int(model["N"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(
        model["q"]
    )
    capacities = np.full(node_count, capacity, dtype=float)
    A, edges = base.incidence_matrix(node_count)
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].unique(),
        key=int,
    )
    if not seeds:
        raise ValueError("no continue-branch seeds found in scalar summary")
    if args.exceptional_seed not in seeds:
        raise ValueError(
            f"exceptional seed {args.exceptional_seed} is not in continue seeds"
        )

    state_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    node_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    matrix_payload: dict[str, np.ndarray] = {}
    exceptional_transition: dict[str, Any] = {}

    def consume_state(
        state: base.DynamicState,
        seed: str,
        state_kind: str,
        stage: str,
    ) -> None:
        summary, component_detail, node_detail, edge_detail, matrices = audit_state(
            state,
            seed=seed,
            state_kind=state_kind,
            stage=stage,
            model=model,
            capacities=capacities,
            A=A,
            edges=edges,
            boundary_tolerance=args.boundary_tol,
            support_tolerance=args.support_tol,
            rate_tolerance=args.rate_tol,
            lock_tolerance=args.lock_tol,
            balance_tolerance=args.balance_tol,
            rank_tolerance=args.rank_tol,
        )
        state_rows.append(summary)
        component_rows.extend(component_detail)
        node_rows.extend(node_detail)
        edge_rows.extend(edge_detail)
        key = safe_stage_key(seed, f"{state_kind}_{stage}")
        for name, matrix in matrices.items():
            matrix_payload[f"{key}_{name}"] = np.asarray(matrix)

    with np.load(args.npz, allow_pickle=False) as data:
        for seed in seeds:
            consume_state(
                base.load_split_state(data, seed),
                seed,
                "split",
                "split",
            )

        stages, exceptional_transition = face.exceptional_states(
            data,
            args.exceptional_seed,
            manifest,
            capacities,
            A,
            edges,
            args.boundary_tol,
            args.exceptional_check_times,
        )
        preferred_order = {
            "split": 0,
            "time_100": 10,
            "time_120": 20,
            "time_123": 30,
            "pre_switch": 40,
            "post_switch": 50,
            "time_125": 60,
            "time_150": 70,
            "late": 100,
        }
        for stage, state in sorted(
            stages.items(), key=lambda item: (preferred_order.get(item[0], 80), item[0])
        ):
            consume_state(
                state,
                args.exceptional_seed,
                "exceptional_stage",
                stage,
            )

    state_frame = pd.DataFrame(state_rows)
    component_frame = pd.DataFrame(component_rows)
    node_frame = pd.DataFrame(node_rows)
    edge_frame = pd.DataFrame(edge_rows)

    atomic_write_csv(output_dir / "state_mechanism_summary.csv", state_frame)
    atomic_write_csv(
        output_dir / "component_mechanism_audit.csv", component_frame
    )
    atomic_write_csv(
        output_dir / "controller_residual_by_node.csv", node_frame
    )
    atomic_write_csv(
        output_dir / "edge_locking_balance_audit.csv", edge_frame
    )
    atomic_savez(
        output_dir / "component_controller_matrices.npz", matrix_payload
    )

    report = make_report(
        state_frame,
        component_frame,
        args.exceptional_seed,
        tolerances,
    )
    atomic_write_text(output_dir / "component_controller_report.txt", report)

    source_path = Path(__file__).resolve()
    analysis_manifest = {
        "analysis": "AIEF-1.4 component/controller/explicit-intertwiner audit",
        "created_by_source": str(source_path),
        "source_sha256": file_sha256(source_path),
        "dependency_sources": {
            "AIEF_1_4_stationarity_perturbation_analysis_updated": {
                "path": str(Path(base.__file__).resolve()),
                "sha256": file_sha256(Path(base.__file__).resolve()),
            },
            "AIEF_1_4_face_spectrum_analysis": {
                "path": str(Path(face.__file__).resolve()),
                "sha256": file_sha256(Path(face.__file__).resolve()),
            },
        },
        "command": sys.argv,
        "inputs": {
            "scalar": {
                "path": str(Path(args.scalar).resolve()),
                "sha256": file_sha256(args.scalar),
            },
            "npz": {
                "path": str(Path(args.npz).resolve()),
                "sha256": file_sha256(args.npz),
            },
            "manifest": {
                "path": str(Path(args.manifest).resolve()),
                "sha256": file_sha256(args.manifest),
            },
        },
        "frozen_run_hash": DEFAULT_RUN_HASH,
        "seed_count": len(seeds),
        "seeds": seeds,
        "exceptional_seed": args.exceptional_seed,
        "exceptional_check_times": args.exceptional_check_times,
        "exceptional_transition": exceptional_transition,
        "tolerances": tolerances,
        "model_constants_used_in_mechanism": {
            "gamma": float(model["gamma"]),
            "eta": float(model["eta"]),
            "mu": float(model["mu"]),
            "capacity": capacity,
            "eta_over_capacity": float(model["eta"]) / capacity,
        },
        "outputs": [
            "state_mechanism_summary.csv",
            "component_mechanism_audit.csv",
            "controller_residual_by_node.csv",
            "edge_locking_balance_audit.csv",
            "component_controller_matrices.npz",
            "component_controller_report.txt",
        ],
        "interpretation_constraints": [
            "This is a deterministic analysis of the frozen cohort, not a new experiment.",
            "Repeated workflow runs with the same seeds are not independent evidence.",
            "The all-node controller equation is not imposed on unsaturated rows.",
            "The exact outward identity includes the node stationarity defect A p.",
            "Degree-rate and c/k weight predictions require the audited locking and stationarity assumptions.",
            "Complete-graph status is computed from the actual support, not inferred from spectra.",
            "Fixed-stratum tangent results do not prove directional differentiability through active-set switches.",
        ],
    }
    atomic_write_text(
        output_dir / "analysis_manifest.json",
        json.dumps(analysis_manifest, indent=2, sort_keys=True) + "\n",
    )

    print(report)
    print(f"Saved analysis to {output_dir.resolve()}")


if __name__ == "__main__":
    main()
