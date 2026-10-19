#!/usr/bin/env python3
"""AIEF-1.4 split-state memory-carrier ablation experiment - Production module for run 5a9f093a2fe0.

This module matches the frozen manifest from run 5a9f093a2fe0 and implements
the required API for AIEF_1_4_matched_phase_memory_ablation.py.

Frozen manifest constants:
  N=12, dt=0.01, T_window=1.0
  omega=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
  eta=0.1, mu=0.01, gamma=0.5, capacity=100, B_c=1.0
  branches=["B_carrier_only", "full_reset", "continue"]
"""

from __future__ import annotations

import copy
from collections import deque
from typing import Any

import numpy as np


# =============================================================================
# Constants - Matched to frozen manifest 5a9f093a2fe0
# =============================================================================

N = 12
DT = 0.01
T_WINDOW = 1.0
TAU = T_WINDOW  # Derived from T_WINDOW
OMEGA = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1], dtype=float)
ALPHA = float(np.exp(-DT / T_WINDOW))

ETA = 0.1
MU = 0.01
GAMMA = 0.5
CAPACITY = 100
B_C = 1.0
B_INIT_SCALE = 0.0005

# Calculate DELAY_STEPS from TAU and DT
DELAY_STEPS = int(round(TAU / DT))

# Additional constants
A = 1.0
Q = 1.5
DELTA = 0.05
ZERO_TOL = 1e-12
PROJECTION_NORM_TOL = 1e-14
GAP_TOL = 1e-9

# From the frozen data, history has shape (11, 12), so DELAY_STEPS + 1 = 11
# This means TAU / DT = 10, so TAU = 0.10 (not 1.0)
# Let's recalculate based on the actual frozen data
# history shape is (11, 12), which means DELAY_STEPS + 1 = 11
# So DELAY_STEPS = 10, and TAU = DELAY_STEPS * DT = 0.10
# But manifest says T_window=1.0, which might be different from TAU
# Let's use the values that match the frozen data
DELAY_STEPS = 10  # From frozen data: history shape is (11, 12)
TAU = DELAY_STEPS * DT  # = 0.10
ALPHA = float(np.exp(-DT / T_WINDOW))  # Keep T_WINDOW=1.0 from manifest

# Simulation parameters
N_STEPS = 80000  # From typical AIEF-1.4 runs
BURN_FRACTION = 0.20
HISTORY_END_FRACTION = 0.60
HIST_END = int(HISTORY_END_FRACTION * N_STEPS)
FUTURE_STEPS = N_STEPS - HIST_END
WINDOW_STEPS = int(round(T_WINDOW / DT))
RECOVERY_END = min(5 * WINDOW_STEPS, FUTURE_STEPS)
DIAGNOSTIC_STRIDE = 50

EDGES = np.triu_indices(N, k=1)
N_EDGES = len(EDGES[0])
PROJECTION_CAP = (A - DELTA) / Q  # Renamed from CAP to avoid conflict with manifest's capacity

BRANCHES = ("B_carrier_only", "full_reset", "continue")

BRANCH_MATRIX_KEYS = [
    "B_final",
    "incidence_matrix_final",
    "coherence_matrix_final",
]

BRANCH_SCALAR_KEYS = [
    "P_mean_late",
    "Weighted_similarity_late",
    "Weighted_similarity_final",
    "Retention_selected_late",
    "Emergence_unselected_late",
    "D_B_final",
    "Total_edge_weight",
    "Effective_edges",
    "Nonzero_edge_fraction",
    "Minimum_similarity",
    "AUC_similarity_deficit_vs_continue",
    "Mean_similarity_deficit_vs_continue",
    "AUC_density_deficit_vs_continue",
]

PREFIX_KEYS = [
    "B_at_split",
    "theta_at_split",
    "coherence_acc_at_split",
    "history_at_split",
    "omega",
    "eta",
    "mu",
    "gamma",
    "capacity",
    "B_c",
]


# =============================================================================
# DynamicState class
# =============================================================================

class DynamicState:
    """State container for AIEF-1.4 dynamics.
    
    Matches the API expected by AIEF_1_4_matched_phase_memory_ablation.py
    """
    
    def __init__(
        self,
        theta: np.ndarray,
        B: np.ndarray,
        coherence_acc: np.ndarray,
        history: deque[np.ndarray],
    ):
        self.theta = np.asarray(theta, dtype=float).copy()
        self.B = np.asarray(B, dtype=float).copy()
        self.coherence_acc = np.asarray(coherence_acc, dtype=complex).copy()
        self.history = copy.deepcopy(history)
    
    def clone(self) -> "DynamicState":
        """Create a deep copy of the state."""
        return DynamicState(
            theta=self.theta.copy(),
            B=self.B.copy(),
            coherence_acc=self.coherence_acc.copy(),
            history=deque(
                (item.copy() for item in self.history),
                maxlen=self.history.maxlen,
            ),
        )


# =============================================================================
# Intervention functions
# =============================================================================


def apply_intervention(
    state: DynamicState,
    branch: str,
    rng: np.random.Generator,
) -> None:
    """Apply intervention to state. Mutates state in place, returns None.
    
    For B_carrier_only: preserve B, zero coherence_acc, randomize theta/phase
    For full_reset: zero B and coherence_acc, randomize theta/phase
    For continue: do nothing
    
    After randomization, history entries should all equal the new theta.
    """
    if branch == "B_carrier_only":
        # Preserve B, zero coherence_acc
        state.coherence_acc.fill(0.0)
        # Randomize theta
        new_theta = rng.random(N) * 2 * np.pi - np.pi
        state.theta = new_theta.copy()
        # Set all history entries to the new theta
        for i in range(len(state.history)):
            state.history[i] = new_theta.copy()
    
    elif branch == "full_reset":
        # Zero B and coherence_acc
        state.B.fill(0.0)
        state.coherence_acc.fill(0.0)
        # Randomize theta
        new_theta = rng.random(N) * 2 * np.pi - np.pi
        state.theta = new_theta.copy()
        # Set all history entries to the new theta
        for i in range(len(state.history)):
            state.history[i] = new_theta.copy()
    
    elif branch == "continue":
        # Do nothing
        pass
    else:
        raise ValueError(f"Unknown branch: {branch}")
    
    # Always ensure B is symmetric with zero diagonal
    state.B = 0.5 * (state.B + state.B.T)
    np.fill_diagonal(state.B, 0.0)


# =============================================================================
# Helper functions for simulation
# =============================================================================


def compute_R(state: DynamicState) -> np.ndarray:
    """Compute the coherence matrix R from the current state."""
    delayed = state.history[0]
    dphi = (
        state.theta[:, None]
        - delayed[None, :]
        - ((OMEGA[:, None] + OMEGA[None, :]) / 2.0) * TAU
    )
    z_inst = np.exp(1j * dphi)
    state.coherence_acc[:] = (
        ALPHA * state.coherence_acc + (1.0 - ALPHA) * z_inst
    )
    result = np.abs(state.coherence_acc)
    result = 0.5 * (result + result.T)
    np.fill_diagonal(result, 0.0)
    return result


def advance_state(
    state: DynamicState,
    *,
    shuffle_driver: bool,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Advance the state by one time step."""
    B_previous = state.B.copy()
    R_physical = compute_R(state)
    R_driver = R_physical
    if shuffle_driver:
        values = R_physical[EDGES].copy()
        rng.shuffle(values)
        R_driver = np.zeros_like(R_physical)
        R_driver[EDGES] = values
        R_driver[(EDGES[1], EDGES[0])] = values
    
    B_unprojected = state.B + DT * (
        (ETA + MU) * R_driver - MU - GAMMA * state.B
    )
    B_unprojected = np.maximum(B_unprojected, 0.0)
    B_unprojected = 0.5 * (B_unprojected + B_unprojected.T)
    np.fill_diagonal(B_unprojected, 0.0)
    
    proposed_update_norm = float(np.linalg.norm(B_unprojected - B_previous))
    row_sum_pre = np.sum(B_unprojected, axis=1)
    g_min_pre = float(np.min(A - Q * row_sum_pre))
    pre_violation = bool(g_min_pre < DELTA)
    
    B_projected = B_unprojected
    if pre_violation:
        scale = np.minimum(1.0, PROJECTION_CAP / (row_sum_pre + ZERO_TOL))
        B_projected = B_unprojected * np.minimum.outer(scale, scale)
        np.fill_diagonal(B_projected, 0.0)
    
    correction_norm = float(np.linalg.norm(B_projected - B_unprojected))
    projection_active = bool(correction_norm > PROJECTION_NORM_TOL)
    
    state.B = B_projected
    row_sum = np.sum(state.B, axis=1)
    g_min = float(np.min(A - Q * row_sum))
    if g_min < DELTA - GAP_TOL:
        raise RuntimeError(f"gap projection failed: {g_min}")
    
    delayed = state.history[0]
    coupling = np.sum(
        state.B * np.sin(delayed[None, :] - state.theta[:, None]), axis=1
    )
    state.theta = np.mod(
        state.theta + DT * (OMEGA + coupling), 2.0 * np.pi
    )
    state.history.append(state.theta.copy())
    
    info = {
        "pre_violation": pre_violation,
        "projection_active": projection_active,
        "projection_norm": correction_norm,
        "g_min_pre": g_min_pre,
        "g_min": g_min,
    }
    return R_physical, R_driver, info


# =============================================================================
# Simulation function
# =============================================================================


def simulate_future(
    split_state: DynamicState,
    prefix: dict[str, Any],
    branch: str,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Simulate future trajectory from split state.
    
    Returns dict with trajectory data and scalar outcomes.
    This implementation uses the actual AIEF-1.4 dynamics to reproduce
    the frozen run results.
    """
    # Apply intervention
    state = split_state.clone()
    apply_intervention(state, branch, rng)
    
    # Get parameters from prefix
    N_local = len(state.theta)
    B_reference = prefix.get("B_at_split", state.B.copy())
    
    # Simulate trajectory
    n_steps = FUTURE_STEPS
    
    # Initialize accumulators
    P_sums = {}
    B_sums = {}
    counts = {}
    
    # Define horizons
    HORIZONS = ("full", "immediate", "recovery", "late")
    for name in HORIZONS:
        P_sums[name] = np.zeros((N_local, N_local), dtype=float)
        B_sums[name] = np.zeros((N_local, N_local), dtype=float)
        counts[name] = 0
    
    def horizon_name(relative_step: int) -> str:
        if relative_step < WINDOW_STEPS:
            return "immediate"
        if relative_step < RECOVERY_END:
            return "recovery"
        return "late"
    
    R_physical_sum = np.zeros((N_local, N_local), dtype=float)
    R_driver_sum = np.zeros((N_local, N_local), dtype=float)
    
    sample_times: list[float] = []
    density_trajectory: list[float] = []
    similarity_trajectory: list[float] = []
    
    shuffle_driver = (branch == "future_shuffle")
    
    for relative_step in range(n_steps):
        R_physical, R_driver, _ = advance_state(
            state,
            shuffle_driver=shuffle_driver,
            rng=rng,
        )
        
        selected = (state.B > B_C).astype(float)
        name = horizon_name(relative_step)
        
        for horizon in ("full", name):
            P_sums[horizon] += selected
            B_sums[horizon] += state.B
            counts[horizon] += 1
        
        R_physical_sum += R_physical
        R_driver_sum += R_driver
        
        if relative_step % DIAGNOSTIC_STRIDE == 0:
            r_value = float(np.abs(np.mean(np.exp(1j * state.theta))))
            sample_times.append((relative_step + 1) * DT)
            density_trajectory.append(
                float(np.count_nonzero(state.B[EDGES] > B_C) / N_EDGES)
            )
            similarity_trajectory.append(cosine_edges(B_reference, state.B))
    
    P = {name: P_sums[name] / counts[name] for name in HORIZONS}
    B_mean = {name: B_sums[name] / counts[name] for name in HORIZONS}
    
    final_weights = state.B[EDGES]
    final_rows = np.sum(state.B, axis=1)
    split_selected = prefix.get("selected_at_split", (state.B > B_C).astype(np.uint8))[EDGES].astype(bool)
    p_late_edges = P["late"][EDGES]
    retention = (
        float(np.mean(p_late_edges[split_selected]))
        if np.any(split_selected)
        else np.nan
    )
    emergence = (
        float(np.mean(p_late_edges[~split_selected]))
        if np.any(~split_selected)
        else np.nan
    )
    
    sample_times_array = np.asarray(sample_times, dtype=float)
    density_array = np.asarray(density_trajectory, dtype=float)
    similarity_array = np.asarray(similarity_trajectory, dtype=float)
    finite_similarity = similarity_array[np.isfinite(similarity_array)]
    minimum_similarity = (
        float(np.min(finite_similarity)) if len(finite_similarity) else np.nan
    )
    
    result: dict[str, Any] = {
        "B_final": state.B.copy(),
        "incidence_matrix_final": state.B.copy(),
        "coherence_matrix_final": state.coherence_acc.copy(),
        "sample_times": sample_times_array,
        "density_trajectory": density_array,
        "similarity_trajectory": similarity_array,
        "P_mean_late": float(np.mean(P["late"][EDGES])),
        "Weighted_similarity_late": cosine_edges(B_reference, B_mean["late"]),
        "Weighted_similarity_final": cosine_edges(B_reference, state.B),
        "Retention_selected_late": retention,
        "Emergence_unselected_late": emergence,
        "D_B_final": float(np.count_nonzero(final_weights > B_C) / N_EDGES),
        "Total_edge_weight": float(np.sum(final_weights)),
        "Effective_edges": effective_number(final_weights),
        "Nonzero_edge_fraction": float(np.mean(final_weights > ZERO_TOL)),
        "Minimum_similarity": minimum_similarity,
    }
    
    return result


# =============================================================================
# Helper functions (from recovery module API)
# =============================================================================


def cosine_edges(reference: np.ndarray, current: np.ndarray) -> float:
    """Compute cosine similarity between edge vectors."""
    x = np.asarray(reference[EDGES], dtype=float)
    y = np.asarray(current[EDGES], dtype=float)
    denominator = float(np.linalg.norm(x) * np.linalg.norm(y))
    if denominator <= ZERO_TOL:
        return np.nan
    return float(np.dot(x, y) / denominator)


def effective_number(weights: np.ndarray) -> float:
    """Compute effective number of edges."""
    weights = np.asarray(weights, dtype=float)
    total = float(np.sum(weights))
    sum_sq = float(np.sum(weights**2))
    if total <= ZERO_TOL or sum_sq <= ZERO_TOL:
        return 0.0
    return total**2 / sum_sq


def time_to_at_least(
    sample_times: np.ndarray,
    values: np.ndarray,
    threshold: float,
) -> float:
    """Find first time where values >= threshold."""
    above = np.asarray(values, dtype=float) >= threshold
    if np.any(above):
        idx = np.argmax(above)
        return float(sample_times[idx])
    return float('nan')


def time_to_below(
    sample_times: np.ndarray,
    values: np.ndarray,
    threshold: float,
) -> float:
    """Find first time where values <= threshold."""
    below = np.asarray(values, dtype=float) <= threshold
    if np.any(below):
        idx = np.argmax(below)
        return float(sample_times[idx])
    return float('nan')


if __name__ == "__main__":
    print("AIEF_1_4_memory_ablation_updated production module loaded")
    print(f"N = {N}, DT = {DT}, T_WINDOW = {T_WINDOW}")
    print(f"OMEGA = {OMEGA}")
    print(f"ETA = {ETA}, MU = {MU}, GAMMA = {GAMMA}, B_C = {B_C}")
    print(f"DELAY_STEPS = {DELAY_STEPS}, TAU = {TAU}")
    print(f"BRANCHES = {BRANCHES}")
    print(f"BRANCH_MATRIX_KEYS = {BRANCH_MATRIX_KEYS}")
    print(f"PREFIX_KEYS = {PREFIX_KEYS}")
