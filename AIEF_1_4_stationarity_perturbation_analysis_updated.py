#!/usr/bin/env python3
"""Mature-stationarity and feasible-perturbation analysis for AIEF-1.4.

Using saved split states, this script:

1. Replays the mature continuation while recording the unconstrained adaptive
   field F and the ideal AIEF directional field P_w(F).
2. Tests whether constraint-balanced adaptive stationarity persists throughout
   the mature future window and records active-set switching.
3. Applies frozen-fast feasible perturbations (radial, interior-mixing, tangent)
   and measures radial restoration and transverse motion.
4. Evolves the same perturbations in the full coupled delayed dynamics over a
   short horizon and measures recovery relative to an unperturbed reference.

The ideal directional field excludes the fixed denominator safeguard. The
actual replay uses the original safeguard so final-state reproduction can be
checked against the frozen AIEF-1.4 output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from collections import deque
from dataclasses import dataclass
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
DEFAULT_OUTPUT_DIR = "aief_1_4_stationarity_perturbation"
DEFAULT_MAX_SEEDS = 5
DEFAULT_DELTAS = "1e-4,1e-3,1e-2,5e-2"
DEFAULT_COUPLED_TIME = 50.0
DEFAULT_SAMPLE_STRIDE = 50
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_STATIONARITY_RATIO_TOL = 1e-8
ZERO_TOL = 1e-14

PERTURBATION_TYPES = (
    "radial_inward",
    "interior_mixing",
    "tangent_face",
)


@dataclass
class DynamicState:
    theta: np.ndarray
    B: np.ndarray
    coherence_acc: np.ndarray
    history: deque[np.ndarray]

    def clone(self) -> "DynamicState":
        return DynamicState(
            theta=self.theta.copy(),
            B=self.B.copy(),
            coherence_acc=self.coherence_acc.copy(),
            history=deque(
                (item.copy() for item in self.history),
                maxlen=self.history.maxlen,
            ),
        )


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
    return sorted(set(values))


def prefix_key(seed: str, metric: str) -> str:
    return f"prefix_seed_{seed}_{metric}"


def branch_key(branch: str, seed: str, metric: str) -> str:
    return f"{branch}_seed_{seed}_{metric}"


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


def load_split_state(
    data: Any,
    seed: str,
) -> DynamicState:
    history_array = np.asarray(data[prefix_key(seed, "history_at_split")], dtype=float)
    return DynamicState(
        theta=np.asarray(data[prefix_key(seed, "theta_at_split")], dtype=float).copy(),
        B=np.asarray(data[prefix_key(seed, "B_at_split")], dtype=float).copy(),
        coherence_acc=np.asarray(
            data[prefix_key(seed, "coherence_acc_at_split")]
        ).copy(),
        history=deque(
            (row.copy() for row in history_array),
            maxlen=len(history_array),
        ),
    )


def positivity_direction(w: np.ndarray, F: np.ndarray) -> np.ndarray:
    modified = F.copy()
    zero = w <= ZERO_TOL
    modified[zero] = np.maximum(F[zero], 0.0)
    return modified


def ideal_directional_field(
    w: np.ndarray,
    F: np.ndarray,
    A: np.ndarray,
    capacities: np.ndarray,
    boundary_tolerance: float,
) -> tuple[np.ndarray, dict[str, Any], np.ndarray, np.ndarray]:
    modified = positivity_direction(w, F)
    row_sum = A @ w
    slack = capacities - row_sum
    saturated = slack <= boundary_tolerance
    effective_capacity = capacities.copy()
    effective_capacity[saturated] = row_sum[saturated]

    row_direction = A @ modified
    alpha = np.zeros(len(capacities), dtype=float)
    outward = saturated & (row_direction > 0.0)
    alpha[outward] = row_direction[outward] / effective_capacity[outward]

    endpoints = [np.flatnonzero(A[:, edge]) for edge in range(A.shape[1])]
    edge_alpha = np.array(
        [max(alpha[nodes[0]], alpha[nodes[1]]) for nodes in endpoints],
        dtype=float,
    )
    field = modified - w * edge_alpha
    info = {
        "F_norm": float(np.linalg.norm(F)),
        "P_F_norm": float(np.linalg.norm(field)),
        "P_F_over_F": float(
            np.linalg.norm(field) / max(np.linalg.norm(F), ZERO_TOL)
        ),
        "zero_edge_count": int(np.sum(w <= ZERO_TOL)),
        "saturated_node_count": int(np.sum(saturated)),
        "outward_saturated_node_count": int(np.sum(outward)),
        "positivity_modified_edge_count": int(
            np.sum((w <= ZERO_TOL) & (F < 0.0))
        ),
        "maximum_capacity_snap": float(
            np.max(np.abs(effective_capacity - capacities))
        ),
    }
    return field, info, saturated, outward


def audit_directional_operator(
    w: np.ndarray,
    F: np.ndarray,
    field: np.ndarray,
    A: np.ndarray,
    capacities: np.ndarray,
    boundary_tolerance: float,
) -> dict[str, float | int | bool]:
    """Numerically audit tangent feasibility, idempotence, and homogeneity."""
    slack = capacities - A @ w
    saturated = slack <= boundary_tolerance
    zero = w <= ZERO_TOL
    row_field = A @ field

    reapplied, _, _, _ = ideal_directional_field(
        w, field, A, capacities, boundary_tolerance
    )
    doubled, _, _, _ = ideal_directional_field(
        w, 2.0 * F, A, capacities, boundary_tolerance
    )

    tangent_zero_violation = (
        float(np.max(np.maximum(-field[zero], 0.0))) if np.any(zero) else 0.0
    )
    tangent_capacity_violation = (
        float(np.max(np.maximum(row_field[saturated], 0.0)))
        if np.any(saturated)
        else 0.0
    )
    idempotence_error = float(np.linalg.norm(reapplied - field))
    homogeneity_error = float(np.linalg.norm(doubled - 2.0 * field))

    return {
        "tangent_zero_edge_violation": tangent_zero_violation,
        "tangent_capacity_violation": tangent_capacity_violation,
        "tangent_feasible": bool(
            tangent_zero_violation <= 1e-10
            and tangent_capacity_violation <= 1e-10
        ),
        "idempotence_error": idempotence_error,
        "idempotence_holds_1e10": bool(idempotence_error <= 1e-10),
        "positive_homogeneity_error": homogeneity_error,
        "positive_homogeneity_holds_1e10": bool(homogeneity_error <= 1e-10),
    }


def permutation_equivariance_error(
    w: np.ndarray,
    F: np.ndarray,
    field: np.ndarray,
    capacities: np.ndarray,
    boundary_tolerance: float,
    seed: str,
) -> float:
    """Check node-relabeling equivariance for one deterministic permutation."""
    node_count = len(capacities)
    A, edges = incidence_matrix(node_count)
    B = vector_to_matrix(w, node_count, edges)
    F_matrix = vector_to_matrix(F, node_count, edges)
    field_matrix = vector_to_matrix(field, node_count, edges)

    rng = deterministic_rng(seed, "operator-permutation")
    permutation = rng.permutation(node_count)
    B_permuted = B[np.ix_(permutation, permutation)]
    F_permuted = F_matrix[np.ix_(permutation, permutation)]
    capacities_permuted = capacities[permutation]
    permuted_field, _, _, _ = ideal_directional_field(
        B_permuted[edges],
        F_permuted[edges],
        A,
        capacities_permuted,
        boundary_tolerance,
    )
    permuted_field_matrix = vector_to_matrix(
        permuted_field, node_count, edges
    )
    restored = np.zeros_like(permuted_field_matrix)
    restored[np.ix_(permutation, permutation)] = permuted_field_matrix
    return float(np.linalg.norm(restored - field_matrix))


def compute_field_and_updated_coherence(
    state: DynamicState,
    model: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    omega = np.asarray(model["omega"], dtype=float)
    dt = float(model["dt"])
    tau = float(model["tau"])
    t_window = float(model["T_window"])
    eta = float(model["eta"])
    mu = float(model["mu"])
    gamma = float(model["gamma"])

    delayed = state.history[0]
    dphi = (
        state.theta[:, None]
        - delayed[None, :]
        - ((omega[:, None] + omega[None, :]) / 2.0) * tau
    )
    alpha = float(np.exp(-dt / t_window))
    updated_coherence = (
        alpha * state.coherence_acc + (1.0 - alpha) * np.exp(1j * dphi)
    )
    R = np.abs(updated_coherence)
    R = 0.5 * (R + R.T)
    np.fill_diagonal(R, 0.0)
    F = (eta + mu) * R - mu - gamma * state.B
    F = 0.5 * (F + F.T)
    np.fill_diagonal(F, 0.0)
    return R, F, updated_coherence


def actual_step(
    state: DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    *,
    audit_operator: bool = True,
) -> dict[str, Any]:
    node_count = state.B.shape[0]
    dt = float(model["dt"])
    omega = np.asarray(model["omega"], dtype=float)
    B_c = float(model["B_c"])

    B_before = state.B.copy()
    _, F_matrix, updated_coherence = compute_field_and_updated_coherence(
        state, model
    )
    w = state.B[edges].copy()
    F = F_matrix[edges].copy()
    P_F, field_info, saturated, outward = ideal_directional_field(
        w, F, A, capacities, boundary_tolerance
    )
    operator_audit = (
        audit_directional_operator(
            w, F, P_F, A, capacities, boundary_tolerance
        )
        if audit_operator
        else {}
    )

    proposal = state.B + dt * F_matrix
    proposal = np.maximum(proposal, 0.0)
    proposal = 0.5 * (proposal + proposal.T)
    np.fill_diagonal(proposal, 0.0)
    proposal_w = proposal[edges]
    row_sum_pre = A @ proposal_w
    violating = row_sum_pre > capacities

    projected = proposal.copy()
    if np.any(violating):
        row_sum_matrix = np.sum(proposal, axis=1)
        scale = np.minimum(
            1.0,
            capacities / (row_sum_matrix + 1e-12),
        )
        projected *= np.minimum.outer(scale, scale)
        np.fill_diagonal(projected, 0.0)

    next_w = projected[edges]
    finite_rate = (next_w - w) / dt
    field_error = finite_rate - P_F

    delayed = state.history[0]
    coupling = np.sum(
        projected * np.sin(delayed[None, :] - state.theta[:, None]), axis=1
    )
    state.B = projected
    state.coherence_acc = updated_coherence
    state.theta = np.mod(state.theta + dt * (omega + coupling), 2.0 * np.pi)
    state.history.append(state.theta.copy())

    return {
        **field_info,
        **operator_audit,
        "actual_update_norm": float(np.linalg.norm(state.B - B_before)),
        "finite_rate_norm": float(np.linalg.norm(finite_rate)),
        "finite_rate_minus_P_F_norm": float(np.linalg.norm(field_error)),
        "finite_rate_P_F_cosine": float(
            finite_rate @ P_F
            / max(
                np.linalg.norm(finite_rate) * np.linalg.norm(P_F),
                np.finfo(float).tiny,
            )
        )
        if np.linalg.norm(P_F) > 1e-12
        else np.nan,
        "actual_projection_active": bool(np.any(violating)),
        "actual_active_node_count": int(np.sum(violating)),
        "threshold_edge_count": int(np.sum(next_w > B_c)),
        "saturated_mask": saturated,
        "outward_mask": outward,
        "zero_mask": w <= ZERO_TOL,
        "P_F": P_F,
        "F": F,
    }


def mask_switch_count(previous: np.ndarray | None, current: np.ndarray) -> int:
    if previous is None:
        return 0
    return int(np.sum(previous != current))


def replay_mature_trajectory(
    split_state: DynamicState,
    expected_final: np.ndarray,
    model: dict[str, Any],
    future_steps: int,
    sample_stride: int,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    stationarity_ratio_tolerance: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    state = split_state.clone()
    B_split_reference = split_state.B.copy()
    split_norm = max(float(np.linalg.norm(B_split_reference)), ZERO_TOL)
    rows: list[dict[str, Any]] = []
    saturated_previous = outward_previous = zero_previous = None
    saturated_switches = outward_switches = zero_switches = 0
    stationary_steps = 0
    ratio_sum = 0.0
    ratio_max = 0.0
    P_F_norm_max = 0.0
    F_norm_sum = 0.0
    idempotence_error_max = 0.0
    homogeneity_error_max = 0.0
    tangent_failure_steps = 0
    idempotence_failure_steps = 0
    homogeneity_failure_steps = 0
    drift_sum = 0.0
    drift_max = 0.0
    exact_unchanged_steps = 0

    for step in range(future_steps):
        info = actual_step(
            state,
            model,
            capacities,
            A,
            edges,
            boundary_tolerance,
        )
        ratio = float(info["P_F_over_F"])
        stationary_steps += int(ratio <= stationarity_ratio_tolerance)
        ratio_sum += ratio
        ratio_max = max(ratio_max, ratio)
        P_F_norm_max = max(P_F_norm_max, float(info["P_F_norm"]))
        F_norm_sum += float(info["F_norm"])
        idempotence_error_max = max(
            idempotence_error_max, float(info["idempotence_error"])
        )
        homogeneity_error_max = max(
            homogeneity_error_max,
            float(info["positive_homogeneity_error"]),
        )
        tangent_failure_steps += int(not info["tangent_feasible"])
        idempotence_failure_steps += int(
            not info["idempotence_holds_1e10"]
        )
        homogeneity_failure_steps += int(
            not info["positive_homogeneity_holds_1e10"]
        )
        drift = float(np.linalg.norm(state.B - B_split_reference) / split_norm)
        drift_sum += drift
        drift_max = max(drift_max, drift)
        exact_unchanged_steps += int(np.array_equal(state.B, B_split_reference))

        saturated_switches += mask_switch_count(
            saturated_previous, info["saturated_mask"]
        )
        outward_switches += mask_switch_count(outward_previous, info["outward_mask"])
        zero_switches += mask_switch_count(zero_previous, info["zero_mask"])
        saturated_previous = info["saturated_mask"].copy()
        outward_previous = info["outward_mask"].copy()
        zero_previous = info["zero_mask"].copy()

        if step % sample_stride == 0:
            rows.append(
                {
                    "step": step,
                    "time_since_split": (step + 1) * float(model["dt"]),
                    "normalized_B_drift_from_split": drift,
                    **{
                        key: value
                        for key, value in info.items()
                        if not isinstance(value, np.ndarray)
                    },
                }
            )

    final_difference = float(np.linalg.norm(state.B - expected_final))
    summary = {
        "future_steps": future_steps,
        "stationary_step_fraction": float(stationary_steps / future_steps),
        "mean_P_F_over_F": float(ratio_sum / future_steps),
        "max_P_F_over_F": ratio_max,
        "max_P_F_norm": P_F_norm_max,
        "mean_F_norm": float(F_norm_sum / future_steps),
        "saturated_active_set_switches": saturated_switches,
        "outward_active_set_switches": outward_switches,
        "zero_edge_set_switches": zero_switches,
        "mean_normalized_B_drift_from_split": float(drift_sum / future_steps),
        "max_normalized_B_drift_from_split": drift_max,
        "exact_B_unchanged_step_fraction": float(
            exact_unchanged_steps / future_steps
        ),
        "tangent_failure_steps": tangent_failure_steps,
        "idempotence_failure_steps": idempotence_failure_steps,
        "homogeneity_failure_steps": homogeneity_failure_steps,
        "max_idempotence_error": idempotence_error_max,
        "max_positive_homogeneity_error": homogeneity_error_max,
        "final_replay_difference_frobenius": final_difference,
        "final_replay_exact": bool(np.array_equal(state.B, expected_final)),
        "final_replay_allclose_1e12": bool(
            np.allclose(state.B, expected_final, rtol=0.0, atol=1e-12)
        ),
    }
    return summary, rows


def deterministic_rng(seed: str, label: str) -> np.random.Generator:
    digest = hashlib.sha256(f"{seed}|{label}".encode()).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "little"))


def strict_interior_reference(
    capacities: np.ndarray,
    A: np.ndarray,
) -> np.ndarray:
    degrees = np.sum(A, axis=1)
    edge_weight = float(np.min(capacities / (2.0 * degrees)))
    return np.full(A.shape[1], edge_weight, dtype=float)


def tangent_direction(
    w: np.ndarray,
    A: np.ndarray,
    capacities: np.ndarray,
    boundary_tolerance: float,
    rng: np.random.Generator,
) -> np.ndarray | None:
    positive = w > ZERO_TOL
    active_nodes = (capacities - A @ w) <= boundary_tolerance
    support_indices = np.flatnonzero(positive)
    if not len(support_indices):
        return None
    active_indices = np.flatnonzero(active_nodes)
    matrix = A[np.ix_(active_indices, support_indices)]
    if matrix.size == 0:
        basis = np.eye(len(support_indices))
    else:
        _, singular_values, vh = np.linalg.svd(matrix, full_matrices=True)
        rank = int(np.sum(singular_values > 1e-10))
        basis = vh[rank:].T
    if basis.shape[1] == 0:
        return None
    coefficients = rng.normal(size=basis.shape[1])
    direction_support = basis @ coefficients
    norm = float(np.linalg.norm(direction_support))
    if norm <= ZERO_TOL:
        return None
    direction_support /= norm
    direction = np.zeros_like(w)
    direction[support_indices] = direction_support
    return direction


def maximum_feasible_amplitude(
    w: np.ndarray,
    direction: np.ndarray,
    A: np.ndarray,
    capacities: np.ndarray,
) -> float:
    limits = [np.inf]
    negative = direction < 0.0
    if np.any(negative):
        limits.append(float(np.min(w[negative] / (-direction[negative]))))
    row_direction = A @ direction
    slack = capacities - A @ w
    outward = row_direction > 0.0
    if np.any(outward):
        limits.append(float(np.min(slack[outward] / row_direction[outward])))
    return max(0.0, min(limits))


def perturb_state(
    w: np.ndarray,
    perturbation: str,
    delta: float,
    A: np.ndarray,
    capacities: np.ndarray,
    boundary_tolerance: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, float, str]:
    norm_w = max(float(np.linalg.norm(w)), ZERO_TOL)
    if perturbation == "radial_inward":
        perturbed = (1.0 - delta) * w
        return perturbed, float(np.linalg.norm(perturbed - w)), "ok"

    if perturbation == "interior_mixing":
        reference = strict_interior_reference(capacities, A)
        perturbed = (1.0 - delta) * w + delta * reference
        return perturbed, float(np.linalg.norm(perturbed - w)), "ok"

    if perturbation == "tangent_face":
        direction = tangent_direction(
            w, A, capacities, boundary_tolerance, rng
        )
        if direction is None:
            return w.copy(), 0.0, "no_tangent_direction"
        requested = delta * norm_w
        maximum = maximum_feasible_amplitude(w, direction, A, capacities)
        amplitude = min(requested, 0.5 * maximum)
        if not np.isfinite(amplitude) or amplitude <= 0.0:
            return w.copy(), 0.0, "zero_feasible_amplitude"
        perturbed = w + amplitude * direction
        return perturbed, amplitude, "ok"

    raise ValueError(f"unknown perturbation {perturbation}")


def frozen_fast_perturbations(
    split_state: DynamicState,
    model: dict[str, Any],
    seed: str,
    deltas: Iterable[float],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
) -> list[dict[str, Any]]:
    _, _, updated_coherence = compute_field_and_updated_coherence(
        split_state, model
    )
    base = split_state.B[edges].copy()
    rows: list[dict[str, Any]] = []

    for perturbation in PERTURBATION_TYPES:
        for delta in deltas:
            rng = deterministic_rng(seed, f"{perturbation}|{delta}")
            perturbed, magnitude, status = perturb_state(
                base,
                perturbation,
                delta,
                A,
                capacities,
                boundary_tolerance,
                rng,
            )
            if status != "ok" or magnitude <= 0.0:
                rows.append(
                    {
                        "seed": seed,
                        "perturbation": perturbation,
                        "delta": delta,
                        "status": status,
                    }
                )
                continue

            B_perturbed = vector_to_matrix(
                perturbed, split_state.B.shape[0], edges
            )
            R = np.abs(updated_coherence)
            R = 0.5 * (R + R.T)
            np.fill_diagonal(R, 0.0)
            F_matrix = (
                (float(model["eta"]) + float(model["mu"])) * R
                - float(model["mu"])
                - float(model["gamma"]) * B_perturbed
            )
            F_matrix = 0.5 * (F_matrix + F_matrix.T)
            np.fill_diagonal(F_matrix, 0.0)
            field, info, _, _ = ideal_directional_field(
                perturbed,
                F_matrix[edges],
                A,
                capacities,
                boundary_tolerance,
            )
            displacement = perturbed - base
            displacement_norm = float(np.linalg.norm(displacement))
            restoring_direction = -displacement
            radial_numerator = float(restoring_direction @ field)
            restoring_coefficient = radial_numerator / max(
                displacement_norm**2, ZERO_TOL
            )
            restoring_component = (
                radial_numerator / max(displacement_norm, ZERO_TOL)
            )
            radial_vector = (
                restoring_component
                * restoring_direction
                / max(displacement_norm, ZERO_TOL)
            )
            transverse = field - radial_vector
            cosine = float(
                restoring_direction @ field
                / max(
                    displacement_norm * np.linalg.norm(field),
                    np.finfo(float).tiny,
                )
            )
            rows.append(
                {
                    "seed": seed,
                    "perturbation": perturbation,
                    "delta": delta,
                    "status": status,
                    "requested_relative_delta": delta,
                    "actual_perturbation_norm": displacement_norm,
                    "relative_perturbation_norm": displacement_norm
                    / max(np.linalg.norm(base), ZERO_TOL),
                    "field_norm": float(np.linalg.norm(field)),
                    "restoring_coefficient": restoring_coefficient,
                    "restoring_cosine": cosine,
                    "radial_component_norm": float(np.linalg.norm(radial_vector)),
                    "transverse_component_norm": float(np.linalg.norm(transverse)),
                    "transverse_to_field_ratio": float(
                        np.linalg.norm(transverse)
                        / max(np.linalg.norm(field), ZERO_TOL)
                    ),
                    **info,
                }
            )
    return rows


def normalized_edge_distance(
    B: np.ndarray,
    reference: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
) -> float:
    x = B[edges]
    y = reference[edges]
    return float(
        np.linalg.norm(x - y) / max(np.linalg.norm(y), ZERO_TOL)
    )


def threshold_jaccard(
    B: np.ndarray,
    reference: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    threshold: float,
) -> float:
    x = B[edges] > threshold
    y = reference[edges] > threshold
    union = int(np.sum(x | y))
    return float(np.sum(x & y) / union) if union else np.nan


def coupled_perturbation_runs(
    split_state: DynamicState,
    model: dict[str, Any],
    seed: str,
    deltas: Iterable[float],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    coupled_steps: int,
    sample_stride: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    threshold = float(model["B_c"])
    reference_state = split_state.clone()
    reference_samples: dict[int, np.ndarray] = {0: reference_state.B.copy()}
    for step in range(1, coupled_steps + 1):
        actual_step(
            reference_state,
            model,
            capacities,
            A,
            edges,
            boundary_tolerance,
            audit_operator=False,
        )
        if step % sample_stride == 0 or step == coupled_steps:
            reference_samples[step] = reference_state.B.copy()

    summary_rows: list[dict[str, Any]] = []
    trajectory_rows: list[dict[str, Any]] = []
    base_w = split_state.B[edges].copy()

    for perturbation in PERTURBATION_TYPES:
        for delta in deltas:
            rng = deterministic_rng(seed, f"coupled|{perturbation}|{delta}")
            perturbed_w, magnitude, status = perturb_state(
                base_w,
                perturbation,
                delta,
                A,
                capacities,
                boundary_tolerance,
                rng,
            )
            if status != "ok" or magnitude <= 0.0:
                summary_rows.append(
                    {
                        "seed": seed,
                        "perturbation": perturbation,
                        "delta": delta,
                        "status": status,
                    }
                )
                continue

            state = split_state.clone()
            state.B = vector_to_matrix(perturbed_w, state.B.shape[0], edges)
            initial_distance = normalized_edge_distance(
                state.B, reference_samples[0], edges
            )
            distances: list[float] = []
            times: list[float] = []

            for step in range(0, coupled_steps + 1):
                if step in reference_samples:
                    reference_B = reference_samples[step]
                    distance = normalized_edge_distance(state.B, reference_B, edges)
                    jaccard = threshold_jaccard(
                        state.B, reference_B, edges, threshold
                    )
                    distances.append(distance)
                    times.append(step * float(model["dt"]))
                    trajectory_rows.append(
                        {
                            "seed": seed,
                            "perturbation": perturbation,
                            "delta": delta,
                            "step": step,
                            "time_since_perturbation": step * float(model["dt"]),
                            "normalized_distance_to_reference": distance,
                            "threshold_jaccard_to_reference": jaccard,
                        }
                    )
                if step == coupled_steps:
                    break
                actual_step(
                    state,
                    model,
                    capacities,
                    A,
                    edges,
                    boundary_tolerance,
                    audit_operator=False,
                )

            distances_array = np.asarray(distances, dtype=float)
            times_array = np.asarray(times, dtype=float)
            threshold_50 = 0.5 * initial_distance
            threshold_10 = 0.1 * initial_distance
            indices_50 = np.flatnonzero(distances_array <= threshold_50)
            indices_10 = np.flatnonzero(distances_array <= threshold_10)
            summary_rows.append(
                {
                    "seed": seed,
                    "perturbation": perturbation,
                    "delta": delta,
                    "status": "ok",
                    "initial_distance": initial_distance,
                    "minimum_distance": float(np.min(distances_array)),
                    "final_distance": float(distances_array[-1]),
                    "final_to_initial_distance_ratio": float(
                        distances_array[-1] / max(initial_distance, ZERO_TOL)
                    ),
                    "time_to_50pct_distance": float(times_array[indices_50[0]])
                    if len(indices_50)
                    else np.nan,
                    "time_to_10pct_distance": float(times_array[indices_10[0]])
                    if len(indices_10)
                    else np.nan,
                }
            )
    return summary_rows, trajectory_rows


def summarize_table(
    frame: pd.DataFrame,
    group_columns: list[str],
) -> pd.DataFrame:
    identifier = set(group_columns) | {"seed", "status"}
    metrics = [column for column in frame.columns if column not in identifier]
    rows: list[dict[str, Any]] = []
    for key, group in frame.groupby(group_columns, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_columns, key))
        for metric in metrics:
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
    stationarity: pd.DataFrame,
    frozen_summary: pd.DataFrame,
    coupled_summary: pd.DataFrame,
) -> str:
    lines = [
        "AIEF mature stationarity and feasible-perturbation analysis",
        "==========================================================",
        "",
        "Mature adaptive stationarity",
        "----------------------------",
    ]
    for _, row in stationarity.iterrows():
        lines.append(
            f"  seed={row['seed']}: stationary_fraction="
            f"{row['stationary_step_fraction']:.6g}, "
            f"mean ||P_w(F)||/||F||={row['mean_P_F_over_F']:.6g}, "
            f"max={row['max_P_F_over_F']:.6g}, "
            f"zero-set switches={int(row['zero_edge_set_switches'])}, "
            f"saturated-set switches={int(row['saturated_active_set_switches'])}, "
            f"max B drift={row['max_normalized_B_drift_from_split']:.6g}, "
            f"tangent/idempotence/homogeneity failures="
            f"{int(row['tangent_failure_steps'])}/"
            f"{int(row['idempotence_failure_steps'])}/"
            f"{int(row['homogeneity_failure_steps'])}, "
            f"equivariance error={row['permutation_equivariance_error']:.3g}, "
            f"replay_exact={row['final_replay_exact']}"
        )

    lines.extend(["", "Frozen-fast restoring diagnostics", "---------------------------------"])
    selected = frozen_summary.loc[
        frozen_summary["metric"].isin(
            [
                "restoring_coefficient",
                "restoring_cosine",
                "transverse_to_field_ratio",
            ]
        )
    ]
    for (perturbation, delta), group in selected.groupby(
        ["perturbation", "delta"]
    ):
        lines.append(f"  {perturbation}, delta={delta:g}")
        for _, row in group.iterrows():
            lines.append(
                f"    {row['metric']}: median={row['median']:.6g}, "
                f"min={row['minimum']:.6g}, max={row['maximum']:.6g}"
            )

    lines.extend(["", "Coupled restoration diagnostics", "-------------------------------"])
    selected_coupled = coupled_summary.loc[
        coupled_summary["metric"].isin(
            [
                "final_to_initial_distance_ratio",
                "time_to_50pct_distance",
                "time_to_10pct_distance",
            ]
        )
    ]
    for (perturbation, delta), group in selected_coupled.groupby(
        ["perturbation", "delta"]
    ):
        lines.append(f"  {perturbation}, delta={delta:g}")
        for _, row in group.iterrows():
            lines.append(
                f"    {row['metric']}: median={row['median']:.6g}, "
                f"valid={int(row['n_valid'])}/{int(row['n_total'])}"
            )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Stationarity refers only to the adaptive B-component, not the full delayed state.",
            "* Frozen-fast restoration holds theta/history/EMA fixed for one instantaneous field evaluation.",
            "* Coupled restoration evolves all state variables and answers a different stability question.",
            "* Positive radial restoration does not exclude large transverse or non-normal motion.",
            "* The ideal directional field excludes the fixed denominator safeguard.",
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
    parser.add_argument("--max-seeds", type=int, default=DEFAULT_MAX_SEEDS)
    parser.add_argument(
        "--deltas", type=parse_float_list, default=parse_float_list(DEFAULT_DELTAS)
    )
    parser.add_argument(
        "--coupled-time", type=float, default=DEFAULT_COUPLED_TIME
    )
    parser.add_argument(
        "--sample-stride", type=int, default=DEFAULT_SAMPLE_STRIDE
    )
    parser.add_argument(
        "--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL
    )
    parser.add_argument(
        "--stationarity-ratio-tol",
        type=float,
        default=DEFAULT_STATIONARITY_RATIO_TOL,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.scalar, args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if (
        args.max_seeds < 0
        or args.coupled_time <= 0.0
        or args.sample_stride <= 0
        or args.boundary_tol < 0.0
        or args.stationarity_ratio_tol < 0.0
    ):
        raise ValueError("invalid command-line settings")
    os.makedirs(args.output_dir, exist_ok=True)

    scalar = pd.read_csv(args.scalar, dtype={"seed": str})
    scalar["seed"] = scalar["seed"].astype(str)
    scalar["branch"] = scalar["branch"].astype(str)
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = manifest["model"]
    node_count = int(model["N"])
    future_steps = int(manifest["protocol"]["future_steps"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(node_count, capacity)
    A, edges = incidence_matrix(node_count)
    coupled_steps = int(round(args.coupled_time / float(model["dt"])))

    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    if args.max_seeds > 0:
        seeds = seeds[: args.max_seeds]

    stationarity_rows: list[dict[str, Any]] = []
    stationarity_timeseries: list[dict[str, Any]] = []
    frozen_rows: list[dict[str, Any]] = []
    coupled_rows: list[dict[str, Any]] = []
    coupled_trajectories: list[dict[str, Any]] = []

    with np.load(args.npz, allow_pickle=False) as data:
        for seed in seeds:
            print(f"Analyzing seed {seed}")
            split_state = load_split_state(data, seed)
            expected_final = np.asarray(
                data[branch_key("continue", seed, "B_final")], dtype=float
            )
            # One split-state node-relabeling equivariance check.
            _, split_F_matrix, _ = compute_field_and_updated_coherence(
                split_state, model
            )
            split_w = split_state.B[edges]
            split_field, _, _, _ = ideal_directional_field(
                split_w,
                split_F_matrix[edges],
                A,
                capacities,
                args.boundary_tol,
            )
            equivariance_error = permutation_equivariance_error(
                split_w,
                split_F_matrix[edges],
                split_field,
                capacities,
                args.boundary_tol,
                seed,
            )

            stationarity, samples = replay_mature_trajectory(
                split_state,
                expected_final,
                model,
                future_steps,
                args.sample_stride,
                capacities,
                A,
                edges,
                args.boundary_tol,
                args.stationarity_ratio_tol,
            )
            stationarity["permutation_equivariance_error"] = equivariance_error
            stationarity_rows.append({"seed": seed, **stationarity})
            stationarity_timeseries.extend(
                {"seed": seed, **row} for row in samples
            )
            frozen_rows.extend(
                frozen_fast_perturbations(
                    split_state,
                    model,
                    seed,
                    args.deltas,
                    capacities,
                    A,
                    edges,
                    args.boundary_tol,
                )
            )
            summaries, trajectories = coupled_perturbation_runs(
                split_state,
                model,
                seed,
                args.deltas,
                capacities,
                A,
                edges,
                args.boundary_tol,
                coupled_steps,
                args.sample_stride,
            )
            coupled_rows.extend(summaries)
            coupled_trajectories.extend(trajectories)

    stationarity_frame = pd.DataFrame(stationarity_rows)
    stationarity_ts_frame = pd.DataFrame(stationarity_timeseries)
    frozen_frame = pd.DataFrame(frozen_rows)
    coupled_frame = pd.DataFrame(coupled_rows)
    coupled_ts_frame = pd.DataFrame(coupled_trajectories)

    frozen_summary = summarize_table(
        frozen_frame, ["perturbation", "delta"]
    )
    coupled_summary = summarize_table(
        coupled_frame, ["perturbation", "delta"]
    )

    outputs = {
        "mature_stationarity_by_seed.csv": stationarity_frame,
        "mature_stationarity_timeseries.csv": stationarity_ts_frame,
        "frozen_fast_perturbations_by_seed.csv": frozen_frame,
        "frozen_fast_perturbation_summary.csv": frozen_summary,
        "coupled_perturbations_by_seed.csv": coupled_frame,
        "coupled_perturbation_summary.csv": coupled_summary,
        "coupled_perturbation_trajectories.csv": coupled_ts_frame,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)

    report = make_report(
        stationarity_frame, frozen_summary, coupled_summary
    )
    with open(
        os.path.join(args.output_dir, "stationarity_perturbation_report.txt"),
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(report)
    print("\n" + report)

    analysis_manifest = {
        "analysis": "AIEF mature stationarity and feasible perturbations",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "source_manifest_path": str(Path(args.manifest).resolve()),
        "source_manifest_sha256": file_sha256(args.manifest),
        "seeds": seeds,
        "deltas": args.deltas,
        "coupled_time": args.coupled_time,
        "sample_stride": args.sample_stride,
        "boundary_tolerance": args.boundary_tol,
        "stationarity_ratio_tolerance": args.stationarity_ratio_tol,
        "perturbation_types": list(PERTURBATION_TYPES),
        "notes": [
            "Stationarity applies only to the adaptive component.",
            "Frozen-fast and coupled restoration are different experiments.",
            "The ideal directional field excludes the denominator safeguard.",
            "Tangent perturbations are restricted to the positive-edge support.",
            "The ideal directional operator is audited for tangent feasibility, idempotence, positive homogeneity, and node-permutation equivariance.",
            "The operator kernel is a positively homogeneous zero set, not assumed to be a linear subspace.",
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
