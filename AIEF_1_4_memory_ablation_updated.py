#!/usr/bin/env python3
"""AIEF-1.4 split-state memory-carrier ablation experiment.

One common baseline prefix is simulated per seed through HIST_END. The exact
split state is then deep-cloned into paired future branches that selectively
remove topology, EMA, phase/history, or future driver identity.

The experiment tests maintenance/reconstruction of an already mature topology;
it does not test initial topology formation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import secrets
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

# =============================================================================
# Model and protocol
# =============================================================================

WORKFLOW_VERSION = "AIEF-1.4-memory-ablation-r2"

N = 12

T_SIM = 800.0

DT = 0.01

TAU = 0.5

OMEGA = np.array(
    [
        1.00, 1.02, 1.50, 2.00, 2.01, 1.01,
        1.03, 1.51, 2.02, 2.00, 1.00, 1.04,
    ],
    dtype=float,
)

A = 1.0
Q = 1.5
DELTA = 0.05
ETA = 0.04
GAMMA = 0.015
MU = 0.03
T_WINDOW = 25.0 / float(np.mean(OMEGA))
B_C = 0.12
B_INIT_SCALE = 0.0005
ALPHA = float(np.exp(-DT / T_WINDOW))
BURN_FRACTION = 0.20
HISTORY_END_FRACTION = 0.60
DELAY_STEPS = int(round(TAU / DT))
N_STEPS = int(round(T_SIM / DT))
BURN_END = int(BURN_FRACTION * N_STEPS)
HIST_END = int(HISTORY_END_FRACTION * N_STEPS)
FUTURE_STEPS = N_STEPS - HIST_END
WINDOW_STEPS = int(round(T_WINDOW / DT))
RECOVERY_END = min(5 * WINDOW_STEPS, FUTURE_STEPS)
DIAGNOSTIC_STRIDE = 50
EDGES = np.triu_indices(N, k=1)
N_EDGES = len(EDGES[0])
CAP = (A - DELTA) / Q
GAP_TOL = 1e-9
ZERO_TOL = 1e-12
PROJECTION_NORM_TOL = 1e-14
DEFAULT_MASTER_SEED = 20260714
DEFAULT_N_SEEDS = 40
DEFAULT_RUN_ROOT = "runs"

BRANCHES = (
    "continue",
    "reset_ema",
    "reset_B",
    "reset_B_ema",
    "B_carrier_only",
    "full_reset",
    "future_shuffle",
)

BRANCH_FAMILIES = {
    "reference": ("continue",),
    "memory_ablation": (
        "reset_ema",
        "reset_B",
        "reset_B_ema",
        "B_carrier_only",
        "full_reset",
    ),
    "future_driver_control": ("future_shuffle",),
}

PRIMARY_OUTCOMES = (
    "Weighted_similarity_late",
    "Retention_contrast_late",
    "P_mean_late",
)

PRIMARY_CONTRASTS = (
    ("continue", "reset_B"),
    ("continue", "reset_ema"),
    ("reset_B", "reset_B_ema"),
    ("continue", "future_shuffle"),
    ("B_carrier_only", "full_reset"),
)

HORIZONS = ("full", "immediate", "recovery", "late")

BRANCH_MATRIX_KEYS = (
    "B_final",
    "B_mean_late",
    "P_full",
    "P_immediate",
    "P_recovery",
    "P_late",
    "R_physical_future",
    "R_driver_future",
    "sample_times",
    "density_trajectory",
    "similarity_trajectory",
)

PREFIX_KEYS = (
    "B_at_split",
    "R_physical_past",
    "theta_at_split",
    "coherence_acc_at_split",
    "history_at_split",
    "selected_at_split",
)

BRANCH_SCALAR_KEYS = (
    "D_B_final",
    "P_mean_full",
    "P_mean_immediate",
    "P_mean_recovery",
    "P_mean_late",
    "Weighted_similarity_final",
    "Weighted_similarity_late",
    "Jaccard_final",
    "Retention_selected_late",
    "Emergence_unselected_late",
    "Retention_contrast_late",
    "Corr_Rpast_Pfull",
    "Corr_Rpast_Plate",
    "Total_edge_weight",
    "Mean_row_sum",
    "Max_row_sum",
    "Nonzero_edge_fraction",
    "Effective_edges",
    "Weight_gini",
    "Weight_entropy",
    "r_mean_future",
    "r_mean_late",
    "G_min_future",
    "G_min_pre_future",
    "Pre_gap_violation_fraction",
    "Projection_active_fraction",
    "Projection_active_given_violation",
    "Projection_norm_mean_active",
    "Projection_norm_max",
    "Projection_relative_state_mean_active",
    "Projection_relative_state_max",
    "Projection_relative_update_mean_active",
    "Projection_relative_update_max",
    "Time_to_50pct_continue_final_density",
    "Time_to_90pct_continue_final_density",
    "Time_to_50pct_continue_late_similarity",
    "Time_to_90pct_continue_late_similarity",
    "Minimum_similarity",
    "Time_to_similarity_below_0_9",
    "Time_to_similarity_below_0_5",
    "Late_persistence_ratio_to_continue",
    "Late_similarity_ratio_to_continue",
)


# =============================================================================
# State and accumulator classes
# =============================================================================

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


@dataclass
class ProjectionTotals:
    steps: int = 0
    violations: int = 0
    active: int = 0
    norm_sum: float = 0.0
    norm_max: float = 0.0
    relative_state_sum: float = 0.0
    relative_state_max: float = 0.0
    relative_update_sum: float = 0.0
    relative_update_max: float = 0.0
    g_min: float = np.inf
    g_min_pre: float = np.inf

    def update(self, info: dict[str, Any]) -> None:
        self.steps += 1
        self.violations += int(info["pre_violation"])
        self.g_min = min(self.g_min, float(info["g_min"]))
        self.g_min_pre = min(self.g_min_pre, float(info["g_min_pre"]))
        if info["projection_active"]:
            self.active += 1
            norm = float(info["projection_norm"])
            rel_state = float(info["projection_relative_state"])
            rel_update = float(info["projection_relative_update"])
            self.norm_sum += norm
            self.norm_max = max(self.norm_max, norm)
            self.relative_state_sum += rel_state
            self.relative_state_max = max(self.relative_state_max, rel_state)
            self.relative_update_sum += rel_update
            self.relative_update_max = max(self.relative_update_max, rel_update)

    def metrics(self) -> dict[str, float]:
        active_denominator = max(self.active, 1)
        return {
            "G_min_future": float(self.g_min),
            "G_min_pre_future": float(self.g_min_pre),
            "Pre_gap_violation_fraction": float(self.violations / self.steps),
            "Projection_active_fraction": float(self.active / self.steps),
            "Projection_active_given_violation": float(self.active / self.violations)
            if self.violations
            else np.nan,
            "Projection_norm_mean_active": float(
                self.norm_sum / active_denominator
            ),
            "Projection_norm_max": float(self.norm_max),
            "Projection_relative_state_mean_active": float(
                self.relative_state_sum / active_denominator
            ),
            "Projection_relative_state_max": float(self.relative_state_max),
            "Projection_relative_update_mean_active": float(
                self.relative_update_sum / active_denominator
            ),
            "Projection_relative_update_max": float(self.relative_update_max),
        }


# =============================================================================
# Utility functions
# =============================================================================

def validate_configuration() -> None:
    if OMEGA.shape != (N,) or not np.all(np.isfinite(OMEGA)):
        raise ValueError("OMEGA must contain N finite frequencies")
    if not np.isclose(DELAY_STEPS * DT, TAU, rtol=0.0, atol=1e-12):
        raise ValueError("TAU/DT must be integral")
    if not np.isclose(N_STEPS * DT, T_SIM, rtol=0.0, atol=1e-10):
        raise ValueError("T_SIM/DT must be integral")
    if not (0 <= BURN_END < HIST_END < N_STEPS):
        raise ValueError("invalid analysis windows")
    if not (0 < WINDOW_STEPS < RECOVERY_END < FUTURE_STEPS):
        raise ValueError("future interval is too short for configured horizons")


def parse_master_seed(value: str) -> int:
    if value.strip().lower() == "random":
        return secrets.randbits(64)
    try:
        result = int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "master seed must be a nonnegative integer or 'random'"
        ) from exc
    if result < 0:
        raise argparse.ArgumentTypeError("master seed must be nonnegative")
    return result


def generate_seed_set(master_seed: int, count: int) -> list[int]:
    if count <= 0:
        raise ValueError("seed count must be positive")
    children = np.random.SeedSequence(master_seed).spawn(count)
    seeds = [
        int(child.generate_state(1, dtype=np.uint64)[0])
        for child in children
    ]
    if len(set(seeds)) != len(seeds):
        raise RuntimeError("duplicate generated seeds")
    return seeds


def source_sha256() -> str | None:
    try:
        return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except (NameError, OSError):
        return None


def atomic_write_text(path: str, text: str) -> None:
    temporary = f"{path}.tmp-{os.getpid()}-{time.time_ns()}"
    try:
        with open(temporary, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def save_npz_atomic(path: str, payload: dict[str, Any]) -> None:
    temporary = f"{path}.tmp-{os.getpid()}-{time.time_ns()}.npz"
    try:
        np.savez_compressed(temporary, **payload)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def safe_corr(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    x = x[valid]
    y = y[valid]
    if len(x) < 3 or np.std(x) < ZERO_TOL or np.std(y) < ZERO_TOL:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def cosine_edges(reference: np.ndarray, current: np.ndarray) -> float:
    x = np.asarray(reference[EDGES], dtype=float)
    y = np.asarray(current[EDGES], dtype=float)
    denominator = float(np.linalg.norm(x) * np.linalg.norm(y))
    if denominator <= ZERO_TOL:
        return np.nan
    return float(np.dot(x, y) / denominator)


def jaccard_edges(reference: np.ndarray, current: np.ndarray) -> float:
    x = reference[EDGES] > B_C
    y = current[EDGES] > B_C
    union = np.count_nonzero(x | y)
    if union == 0:
        return np.nan
    return float(np.count_nonzero(x & y) / union)


def effective_number(weights: np.ndarray) -> float:
    weights = np.asarray(weights, dtype=float)
    total = float(np.sum(weights))
    sum_sq = float(np.sum(weights**2))
    if total <= ZERO_TOL or sum_sq <= ZERO_TOL:
        return 0.0
    return total**2 / sum_sq


def gini_coefficient(weights: np.ndarray) -> float:
    x = np.sort(np.asarray(weights, dtype=float))
    total = float(np.sum(x))
    if total <= ZERO_TOL:
        return 0.0
    n = len(x)
    ranks = np.arange(1, n + 1, dtype=float)
    return float(2.0 * np.dot(ranks, x) / (n * total) - (n + 1.0) / n)


def normalized_entropy(weights: np.ndarray) -> float:
    weights = np.asarray(weights, dtype=float)
    total = float(np.sum(weights))
    if total <= ZERO_TOL:
        return 0.0
    probabilities = weights / total
    positive = probabilities > 0.0
    entropy = -float(
        np.sum(probabilities[positive] * np.log(probabilities[positive]))
    )
    return entropy / float(np.log(len(weights)))


def horizon_name(relative_step: int) -> str:
    if relative_step < WINDOW_STEPS:
        return "immediate"
    if relative_step < RECOVERY_END:
        return "recovery"
    return "late"


def compute_R(state: DynamicState) -> np.ndarray:
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
        scale = np.minimum(1.0, CAP / (row_sum_pre + ZERO_TOL))
        B_projected = B_unprojected * np.minimum.outer(scale, scale)
        np.fill_diagonal(B_projected, 0.0)
    correction_norm = float(np.linalg.norm(B_projected - B_unprojected))
    projection_active = bool(correction_norm > PROJECTION_NORM_TOL)
    relative_state = correction_norm / max(
        float(np.linalg.norm(B_unprojected)), ZERO_TOL
    )
    relative_update = correction_norm / max(proposed_update_norm, ZERO_TOL)
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
        "projection_relative_state": relative_state,
        "projection_relative_update": relative_update,
        "g_min_pre": g_min_pre,
        "g_min": g_min,
    }
    return R_physical, R_driver, info


# =============================================================================
# Prefix and interventions
# =============================================================================

def simulate_prefix(seed: int) -> tuple[DynamicState, dict[str, np.ndarray]]:
    root = np.random.SeedSequence(seed)
    init_sequence, _ = root.spawn(2)
    rng = np.random.default_rng(init_sequence)
    theta = rng.random(N) * 2.0 * np.pi
    B = B_INIT_SCALE * rng.random((N, N))
    B = 0.5 * (B + B.T)
    np.fill_diagonal(B, 0.0)
    state = DynamicState(
        theta=theta,
        B=B,
        coherence_acc=np.zeros((N, N), dtype=complex),
        history=deque(
            (theta.copy() for _ in range(DELAY_STEPS + 1)),
            maxlen=DELAY_STEPS + 1,
        ),
    )
    R_past_sum = np.zeros((N, N), dtype=float)
    R_past_count = 0
    unused_rng = np.random.default_rng(0)
    for step in range(HIST_END):
        R_physical, *_ = advance_state(
            state,
            shuffle_driver=False,
            rng=unused_rng,
        )
        if BURN_END <= step < HIST_END:
            R_past_sum += R_physical
            R_past_count += 1
    prefix = {
        "B_at_split": state.B.copy(),
        "R_physical_past": R_past_sum / R_past_count,
        "theta_at_split": state.theta.copy(),
        "coherence_acc_at_split": state.coherence_acc.copy(),
        "history_at_split": np.stack(tuple(state.history)),
        "selected_at_split": (state.B > B_C).astype(np.uint8),
    }
    return state, prefix


def apply_intervention(
    state: DynamicState,
    branch: str,
    rng: np.random.Generator,
) -> None:
    if branch in {"reset_ema", "reset_B_ema", "B_carrier_only", "full_reset"}:
        state.coherence_acc.fill(0.0)
    if branch in {"reset_B", "reset_B_ema", "full_reset"}:
        state.B.fill(0.0)
    if branch in {"B_carrier_only", "full_reset"}:
        state.theta = rng.random(N) * 2.0 * np.pi
        state.history = deque(
            (state.theta.copy() for _ in range(DELAY_STEPS + 1)),
            maxlen=DELAY_STEPS + 1,
        )
    state.B = 0.5 * (state.B + state.B.T)
    np.fill_diagonal(state.B, 0.0)


# =============================================================================
# Future branch simulation
# =============================================================================

def simulate_future(
    split_state: DynamicState,
    prefix: dict[str, np.ndarray],
    branch: str,
    rng: np.random.Generator,
) -> dict[str, Any]:
    state = split_state.clone()
    apply_intervention(state, branch, rng)
    P_sums = {name: np.zeros((N, N), dtype=float) for name in HORIZONS}
    B_sums = {name: np.zeros((N, N), dtype=float) for name in HORIZONS}
    counts = {name: 0 for name in HORIZONS}
    R_physical_sum = np.zeros((N, N), dtype=float)
    R_driver_sum = np.zeros((N, N), dtype=float)
    projection = ProjectionTotals()
    r_sum = 0.0
    r_count = 0
    r_late_sum = 0.0
    r_late_count = 0
    sample_times: list[float] = []
    density_trajectory: list[float] = []
    similarity_trajectory: list[float] = []
    shuffle_driver = branch == "future_shuffle"
    B_reference = prefix["B_at_split"]
    for relative_step in range(FUTURE_STEPS):
        R_physical, R_driver, projection_info = advance_state(
            state,
            shuffle_driver=shuffle_driver,
            rng=rng,
        )
        projection.update(projection_info)
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
            r_sum += r_value
            r_count += 1
            if name == "late":
                r_late_sum += r_value
                r_late_count += 1
            sample_times.append((relative_step + 1) * DT)
            density_trajectory.append(
                float(np.count_nonzero(state.B[EDGES] > B_C) / N_EDGES)
            )
            similarity_trajectory.append(cosine_edges(B_reference, state.B))
    P = {name: P_sums[name] / counts[name] for name in HORIZONS}
    B_mean = {name: B_sums[name] / counts[name] for name in HORIZONS}
    final_weights = state.B[EDGES]
    final_rows = np.sum(state.B, axis=1)
    split_selected = prefix["selected_at_split"][EDGES].astype(bool)
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
        "D_B_final": float(np.count_nonzero(final_weights > B_C) / N_EDGES),
        "P_mean_full": float(np.mean(P["full"][EDGES])),
        "P_mean_immediate": float(np.mean(P["immediate"][EDGES])),
        "P_mean_recovery": float(np.mean(P["recovery"][EDGES])),
        "P_mean_late": float(np.mean(P["late"][EDGES])),
        "Weighted_similarity_final": cosine_edges(B_reference, state.B),
        "Weighted_similarity_late": cosine_edges(B_reference, B_mean["late"]),
        "Jaccard_final": jaccard_edges(B_reference, state.B),
        "Retention_selected_late": retention,
        "Emergence_unselected_late": emergence,
        "Retention_contrast_late": retention - emergence,
        "Corr_Rpast_Pfull": safe_corr(
            prefix["R_physical_past"][EDGES], P["full"][EDGES]
        ),
        "Corr_Rpast_Plate": safe_corr(
            prefix["R_physical_past"][EDGES], P["late"][EDGES]
        ),
        "Total_edge_weight": float(np.sum(final_weights)),
        "Mean_row_sum": float(np.mean(final_rows)),
        "Max_row_sum": float(np.max(final_rows)),
        "Nonzero_edge_fraction": float(np.mean(final_weights > ZERO_TOL)),
        "Effective_edges": effective_number(final_weights),
        "Weight_gini": gini_coefficient(final_weights),
        "Weight_entropy": normalized_entropy(final_weights),
        "r_mean_future": float(r_sum / r_count),
        "r_mean_late": float(r_late_sum / r_late_count),
        "Time_to_50pct_continue_final_density": np.nan,
        "Time_to_90pct_continue_final_density": np.nan,
        "Time_to_50pct_continue_late_similarity": np.nan,
        "Time_to_90pct_continue_late_similarity": np.nan,
        "Minimum_similarity": minimum_similarity,
        "Time_to_similarity_below_0_9": np.nan,
        "Time_to_similarity_below_0_5": np.nan,
        "Late_persistence_ratio_to_continue": np.nan,
        "Late_similarity_ratio_to_continue": np.nan,
        **projection.metrics(),
        "B_final": state.B.copy(),
        "B_mean_late": B_mean["late"],
        "P_full": P["full"],
        "P_immediate": P["immediate"],
        "P_recovery": P["recovery"],
        "P_late": P["late"],
        "R_physical_future": R_physical_sum / FUTURE_STEPS,
        "R_driver_future": R_driver_sum / FUTURE_STEPS,
        "sample_times": sample_times_array,
        "density_trajectory": density_array,
        "similarity_trajectory": similarity_array,
    }
    return result


def time_to_at_least(
    sample_times: np.ndarray,
    values: np.ndarray,
    target: float,
) -> float:
    valid = np.isfinite(values)
    indices = np.flatnonzero(valid & (values >= target))
    return float(sample_times[indices[0]]) if len(indices) else np.nan


def time_to_below(
    sample_times: np.ndarray,
    values: np.ndarray,
    threshold: float,
) -> float:
    valid = np.isfinite(values)
    indices = np.flatnonzero(valid & (values < threshold))
    return float(sample_times[indices[0]]) if len(indices) else np.nan


def run_seed(
    seed: int,
    seed_index: int,
    config_hash: str,
    verify_continue: bool,
) -> dict[str, Any]:
    split_state, prefix = simulate_prefix(seed)
    immutable_snapshot = {
        "theta": split_state.theta.copy(),
        "B": split_state.B.copy(),
        "coherence": split_state.coherence_acc.copy(),
        "history": np.stack(tuple(split_state.history)),
    }
    _, branch_root = np.random.SeedSequence(seed).spawn(2)
    branch_sequences = branch_root.spawn(len(BRANCHES))
    branch_rng_seeds = {
        branch: int(sequence.generate_state(1, dtype=np.uint64)[0])
        for branch, sequence in zip(BRANCHES, branch_sequences)
    }
    branch_results: dict[str, dict[str, Any]] = {}
    for branch in BRANCHES:
        branch_results[branch] = simulate_future(
            split_state,
            prefix,
            branch,
            np.random.default_rng(branch_rng_seeds[branch]),
        )
        if not np.array_equal(split_state.theta, immutable_snapshot["theta"]):
            raise RuntimeError("branch mutation leaked into split theta")
        if not np.array_equal(split_state.B, immutable_snapshot["B"]):
            raise RuntimeError("branch mutation leaked into split B")
        if not np.array_equal(
            split_state.coherence_acc, immutable_snapshot["coherence"]
        ):
            raise RuntimeError("branch mutation leaked into split EMA")
        if not np.array_equal(
            np.stack(tuple(split_state.history)), immutable_snapshot["history"]
        ):
            raise RuntimeError("branch mutation leaked into split history")
    continue_result = branch_results["continue"]
    reference_density = float(continue_result["D_B_final"])
    reference_late_similarity = float(
        continue_result["Weighted_similarity_late"]
    )
    reference_late_persistence = float(continue_result["P_mean_late"])
    for result in branch_results.values():
        times = result["sample_times"]
        density = result["density_trajectory"]
        similarity = result["similarity_trajectory"]
        result["Time_to_50pct_continue_final_density"] = time_to_at_least(
            times, density, 0.5 * reference_density
        )
        result["Time_to_90pct_continue_final_density"] = time_to_at_least(
            times, density, 0.9 * reference_density
        )
        result["Time_to_50pct_continue_late_similarity"] = time_to_at_least(
            times, similarity, 0.5 * reference_late_similarity
        )
        result["Time_to_90pct_continue_late_similarity"] = time_to_at_least(
            times, similarity, 0.9 * reference_late_similarity
        )
        result["Time_to_similarity_below_0_9"] = time_to_below(
            times, similarity, 0.9
        )
        result["Time_to_similarity_below_0_5"] = time_to_below(
            times, similarity, 0.5
        )
        result["Late_persistence_ratio_to_continue"] = (
            float(result["P_mean_late"] / reference_late_persistence)
            if abs(reference_late_persistence) > ZERO_TOL
            else np.nan
        )
        result["Late_similarity_ratio_to_continue"] = (
            float(
                result["Weighted_similarity_late"]
                / reference_late_similarity
            )
            if np.isfinite(reference_late_similarity)
            and abs(reference_late_similarity) > ZERO_TOL
            else np.nan
        )
    if verify_continue:
        duplicate = simulate_future(
            split_state,
            prefix,
            "continue",
            np.random.default_rng(branch_rng_seeds["continue"]),
        )
        for key in ("B_final", "P_full", "P_late"):
            if not np.array_equal(branch_results["continue"][key], duplicate[key]):
                raise RuntimeError(f"continue reproducibility failed for {key}")
    return {
        "seed": int(seed),
        "seed_index": int(seed_index),
        "config_hash": config_hash,
        "prefix": prefix,
        "branches": branch_results,
    }


# =============================================================================
# Checkpoint serialization
# =============================================================================

def flatten_seed_result(result: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "seed": result["seed"],
        "seed_index": result["seed_index"],
        "config_hash": result["config_hash"],
    }
    for key, value in result["prefix"].items():
        payload[f"prefix__{key}"] = value
    for branch, branch_result in result["branches"].items():
        for key, value in branch_result.items():
            payload[f"branch__{branch}__{key}"] = value
    return payload


def unflatten_seed_result(payload: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "seed": int(payload["seed"]),
        "seed_index": int(payload["seed_index"]),
        "config_hash": str(payload["config_hash"]),
        "prefix": {},
        "branches": {branch: {} for branch in BRANCHES},
    }
    for key, value in payload.items():
        if key.startswith("prefix__"):
            result["prefix"][key.split("__", 1)[1]] = value
        elif key.startswith("branch__"):
            _, branch, metric = key.split("__", 2)
            result["branches"][branch][metric] = value
    return result


def load_npz(path: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    with np.load(path, allow_pickle=False) as data:
        for key in data.files:
            value = data[key]
            payload[key] = value.item() if value.ndim == 0 else value.copy()
    return payload


def validate_seed_result(
    result: dict[str, Any], seed: int, config_hash: str
) -> None:
    if result["seed"] != seed or result["config_hash"] != config_hash:
        raise RuntimeError("checkpoint identity/configuration mismatch")
    missing_prefix = set(PREFIX_KEYS) - set(result["prefix"])
    if missing_prefix:
        raise RuntimeError(f"checkpoint missing prefix keys: {missing_prefix}")
    if set(result["branches"]) != set(BRANCHES):
        raise RuntimeError("checkpoint branch set mismatch")
    for branch in BRANCHES:
        missing = (set(BRANCH_SCALAR_KEYS) | set(BRANCH_MATRIX_KEYS)) - set(
            result["branches"][branch]
        )
        if missing:
            raise RuntimeError(f"{branch} checkpoint missing keys: {missing}")


# =============================================================================
# Manifest, output, and CLI
# =============================================================================

def build_manifest(master_seed: int, seeds: list[int]) -> dict[str, Any]:
    return {
        "workflow_version": WORKFLOW_VERSION,
        "source_sha256": source_sha256(),
        "model": {
            "N": N, "T_sim": T_SIM, "dt": DT, "tau": TAU,
            "omega": OMEGA.tolist(), "a": A, "q": Q, "delta": DELTA,
            "eta": ETA, "gamma": GAMMA, "mu": MU,
            "T_window": T_WINDOW, "alpha": ALPHA,
            "B_c": B_C, "B_init_scale": B_INIT_SCALE,
        },
        "protocol": {
            "purpose": "maintenance and reconstruction of mature topology",
            "branches": list(BRANCHES),
            "branch_families": {
                family: list(branches)
                for family, branches in BRANCH_FAMILIES.items()
            },
            "interventions": {
                "continue": "preserve all split state",
                "reset_ema": "zero coherence_acc; preserve B and phase/history",
                "reset_B": "zero B; preserve EMA and phase/history",
                "reset_B_ema": "zero B and coherence_acc; preserve phase/history",
                "B_carrier_only": "preserve B; zero EMA and randomize phase/history; omega remains fixed",
                "full_reset": "zero B and EMA; randomize phase/history; omega remains fixed",
                "future_shuffle": "preserve split state; shuffle only future driver edge identity",
            },
            "primary_outcomes": list(PRIMARY_OUTCOMES),
            "primary_contrasts": [list(pair) for pair in PRIMARY_CONTRASTS],
            "secondary_outcomes": [
                key for key in BRANCH_SCALAR_KEYS
                if key not in PRIMARY_OUTCOMES
            ],
            "n_steps": N_STEPS,
            "hist_end": HIST_END,
            "future_steps": FUTURE_STEPS,
            "window_steps": WINDOW_STEPS,
            "recovery_end": RECOVERY_END,
            "diagnostic_stride": DIAGNOSTIC_STRIDE,
            "primary_horizon": "late",
        },
        "randomization": {
            "master_seed": int(master_seed),
            "paired_seeds": [int(seed) for seed in seeds],
            "seed_generation": "SeedSequence(master_seed).spawn(n_seeds)",
            "branch_generation": "second per-seed child sequence spawns named uint64 branch seeds; verification reuses continue seed",
            "bit_generator": np.random.default_rng(0).bit_generator.__class__.__name__,
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "schema": {
            "prefix_keys": list(PREFIX_KEYS),
            "branch_scalar_keys": list(BRANCH_SCALAR_KEYS),
            "branch_matrix_keys": list(BRANCH_MATRIX_KEYS),
        },
    }


def write_csv_atomic(path: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError("cannot write empty CSV")
    temporary = f"{path}.tmp-{os.getpid()}-{time.time_ns()}"
    try:
        with open(temporary, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def summarize(values: Iterable[float]) -> tuple[float, float, int]:
    x = np.asarray(list(values), dtype=float)
    finite = x[np.isfinite(x)]
    if not len(finite):
        return np.nan, np.nan, 0
    return float(np.mean(finite)), float(np.std(finite)), int(len(finite))


def branch_family(branch: str) -> str:
    for family, members in BRANCH_FAMILIES.items():
        if branch in members:
            return family
    return "unknown"


def print_summary(results: list[dict[str, Any]]) -> None:
    print("=" * 165)
    print("AIEF-1.4 MEMORY-CARRIER ABLATION — mean ± std over paired seeds")
    print("=" * 165)
    print(
        f"{'Branch':<18} {'Family':<22} {'D_B':>13} {'P_late':>13} "
        f"{'P_ratio':>13} {'Sim_late':>13} {'Retention':>13} "
        f"{'Emergence':>13} {'Proj_frac':>13} {'Rel_proj':>13}"
    )
    print("-" * 165)
    keys = (
        "D_B_final",
        "P_mean_late",
        "Late_persistence_ratio_to_continue",
        "Weighted_similarity_late",
        "Retention_selected_late",
        "Emergence_unselected_late",
        "Projection_active_fraction",
        "Projection_relative_state_mean_active",
    )
    for branch in BRANCHES:
        branch_runs = [result["branches"][branch] for result in results]
        cells = []
        for key in keys:
            mean, std, _ = summarize(run[key] for run in branch_runs)
            cells.append(
                "nan±nan" if not np.isfinite(mean) else f"{mean:.3f}±{std:.3f}"
            )
        print(
            f"{branch:<18} {branch_family(branch):<22}"
            + "".join(f" {cell:>13}" for cell in cells)
        )
    print("=" * 165)
    print("P_ratio is P_mean_late(branch) / P_mean_late(continue); it may exceed 1.")
    print("Primary outcomes:", ", ".join(PRIMARY_OUTCOMES))
    print(
        "Primary contrasts:",
        "; ".join(f"{left} vs {right}" for left, right in PRIMARY_CONTRASTS),
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--master-seed", type=parse_master_seed, default=DEFAULT_MASTER_SEED,
        help="fixed integer master seed or 'random' (default: 20260714)",
    )
    parser.add_argument(
        "--n-seeds", type=int, default=DEFAULT_N_SEEDS,
        help=f"paired seed count (default: {DEFAULT_N_SEEDS})",
    )
    parser.add_argument(
        "--run-root", default=DEFAULT_RUN_ROOT,
        help=f"output root (default: {DEFAULT_RUN_ROOT})",
    )
    parser.add_argument(
        "--verify-continue", action="store_true",
        help="repeat the continue branch and require exact equality (smoke tests)",
    )
    return parser.parse_args()


def main() -> None:
    validate_configuration()
    args = parse_arguments()
    seeds = generate_seed_set(int(args.master_seed), args.n_seeds)
    manifest_base = build_manifest(int(args.master_seed), seeds)
    manifest_text = json.dumps(
        manifest_base, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    config_hash = hashlib.sha256(manifest_text.encode()).hexdigest()[:12]
    run_dir = os.path.join(args.run_root, config_hash)
    os.makedirs(run_dir, exist_ok=True)
    manifest = {**manifest_base, "config_hash": config_hash}
    atomic_write_text(
        os.path.join(run_dir, "manifest.json"),
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    print("Running AIEF-1.4 split-state memory-carrier ablation")
    print(f"  master seed:   {args.master_seed}")
    print(f"  paired seeds:  {args.n_seeds}")
    print(f"  configuration: {config_hash}")
    print(f"  output:        {run_dir}")
    all_results: list[dict[str, Any]] = []
    started = time.time()
    for seed_index, seed in enumerate(seeds):
        checkpoint = os.path.join(run_dir, f"seed_{seed}.npz")
        if os.path.exists(checkpoint):
            try:
                result = unflatten_seed_result(load_npz(checkpoint))
                validate_seed_result(result, seed, config_hash)
                status = "loaded"
            except Exception as exc:
                print(f"  invalid checkpoint {checkpoint}: {exc}; recomputing")
                os.remove(checkpoint)
                result = run_seed(
                    seed, seed_index, config_hash, args.verify_continue
                )
                save_npz_atomic(checkpoint, flatten_seed_result(result))
                status = "recomputed"
        else:
            result = run_seed(seed, seed_index, config_hash, args.verify_continue)
            save_npz_atomic(checkpoint, flatten_seed_result(result))
            status = "completed"
        all_results.append(result)
        print(f"  seed {seed_index + 1}/{len(seeds)} {status}")
    print(f"Runtime: {time.time() - started:.1f} s\n")
    scalar_rows: list[dict[str, Any]] = []
    matrix_payload: dict[str, Any] = {}
    for result in all_results:
        seed = result["seed"]
        for key, value in result["prefix"].items():
            matrix_payload[f"prefix_seed_{seed}_{key}"] = value
        for branch in BRANCHES:
            branch_result = result["branches"][branch]
            scalar_rows.append(
                {
                    "seed_index": result["seed_index"],
                    "seed": seed,
                    "branch": branch,
                    "branch_family": branch_family(branch),
                    **{key: branch_result[key] for key in BRANCH_SCALAR_KEYS},
                }
            )
            for key in BRANCH_MATRIX_KEYS:
                matrix_payload[f"{branch}_seed_{seed}_{key}"] = branch_result[key]
    csv_path = os.path.join(run_dir, f"AIEF_1_4_{config_hash}_scalar_summary.csv")
    matrix_path = os.path.join(
        run_dir, f"AIEF_1_4_{config_hash}_branch_diagnostics.npz"
    )
    write_csv_atomic(csv_path, scalar_rows)
    save_npz_atomic(matrix_path, matrix_payload)
    print_summary(all_results)
    print(f"Saved {csv_path}")
    print(f"Saved {matrix_path}")


if __name__ == "__main__":
    main()
