#!/usr/bin/env python3
"""AIEF-1.3 production falsification matrix.

Key properties
--------------
* Reproducibly randomized, paired seed sets generated from one master seed.
* Independent RNG streams for initialization and shuffle_R.
* Exact delayed-state indexing with a constant prehistory.
* Symmetric resonance driver and symmetry-preserving gap projection.
* Non-overlapping past-resonance and future-persistence windows.
* Atomic per-run checkpoints, validated resume, and configuration versioning.
* Scalar, edge-level, concentration, degeneracy, and projection diagnostics.

Examples
--------
Reproduce the default validation seed set:
    python AIEF_1_3_falsification_updated.py

Use a different preregistered seed set:
    python AIEF_1_3_falsification_updated.py --master-seed 20260713 --n-seeds 50

Generate and record a fresh random master seed:
    python AIEF_1_3_falsification_updated.py --master-seed random --n-seeds 50
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
from pathlib import Path
from typing import Any, Iterable

import numpy as np


# ============================================================
# Fixed model/protocol configuration
# ============================================================

# Increment this only when the equations, observables, controls, or data schema
# change. Do not increment it merely to repeat an identical run.
WORKFLOW_VERSION = "AIEF-1.3-production-11"

N = 12
T_SIM = 800.0
DT = 0.01
TAU = 0.5
OMEGA = np.array(
    [
        1.00,
        1.02,
        1.50,
        2.00,
        2.01,
        1.01,
        1.03,
        1.51,
        2.02,
        2.00,
        1.00,
        1.04,
    ],
    dtype=float,
)

A = 1.0
Q = 1.5
DELTA = 0.05
ETA = 0.04
GAMMA = 0.015
MU = 0.03
T_WINDOW = 25.0 / float(np.mean(OMEGA))  # 25 inverse-frequency units
B_C = 0.12
B_INIT_SCALE = 0.0005
D_B_STAR = 0.30
ALPHA = float(np.exp(-DT / T_WINDOW))

CONDITIONS = ("baseline", "shuffle_R", "no_delay", "no_mu", "no_gap")
GAP_TOL = 1e-9
PROJECTION_NORM_TOL = 1e-14
ZERO_TOL = 1e-12
DIAGNOSTIC_STRIDE = 50

DEFAULT_MASTER_SEED = 20260712
DEFAULT_N_SEEDS = 20
DEFAULT_RUN_ROOT = "runs"

# Analysis windows: 20% burn-in, 40% past-resonance window, 40% future window.
BURN_FRACTION = 0.20
HISTORY_END_FRACTION = 0.60

DELAY_STEPS = int(round(TAU / DT))
N_STEPS = int(round(T_SIM / DT))
BURN_END = int(BURN_FRACTION * N_STEPS)
HIST_END = int(HISTORY_END_FRACTION * N_STEPS)
EDGES = np.triu_indices(N, k=1)
N_EDGES = len(EDGES[0])

MATRIX_KEYS = (
    "B_at_split",
    "P_future",
    "R_physical_past",
    "R_driver_past",
    "R_physical_future",
    "R_driver_future",
    "B_final",
)

SCALAR_KEYS = (
    "D_B",
    "Corr_physical",
    "Corr_driver",
    "Phi",
    "r_mean",
    "S_spectral",
    "G_min_final",
    "G_min_over_time",
    "G_min_pre_over_time",
    "P_mean",
    "P_variance",
    "P_max",
    "P_nonzero_fraction",
    "P_degenerate",
    "Cov_physical",
    "Cov_driver",
    "Total_edge_weight",
    "Mean_row_sum",
    "Max_row_sum",
    "Nonzero_edge_fraction",
    "Effective_edges",
    "Weight_gini",
    "Weight_entropy",
    "Pre_gap_violation_fraction",
    "Projection_active_fraction",
    "Projection_norm_mean_active",
    "Projection_norm_max",
)


# ============================================================
# Validation and reproducibility helpers
# ============================================================


def validate_configuration() -> None:
    if N < 2:
        raise ValueError("N must be at least 2")
    if OMEGA.shape != (N,) or not np.all(np.isfinite(OMEGA)):
        raise ValueError("OMEGA must contain exactly N finite frequencies")
    if DT <= 0.0 or T_SIM <= 0.0 or TAU < 0.0 or T_WINDOW <= 0.0:
        raise ValueError("DT, T_SIM, and T_WINDOW must be positive; TAU must be nonnegative")
    if Q <= 0.0 or GAMMA <= 0.0:
        raise ValueError("Q and GAMMA must be positive")
    if not (0.0 <= DELTA < A):
        raise ValueError("DELTA must satisfy 0 <= DELTA < A")
    if B_C < 0.0 or B_INIT_SCALE < 0.0:
        raise ValueError("B_C and B_INIT_SCALE must be nonnegative")
    if not np.isclose(DELAY_STEPS * DT, TAU, rtol=0.0, atol=1e-12):
        raise ValueError("TAU/DT must be an integer for exact delay indexing")
    if not np.isclose(N_STEPS * DT, T_SIM, rtol=0.0, atol=1e-10):
        raise ValueError("T_SIM/DT must be an integer")
    if not (0 <= BURN_END < HIST_END < N_STEPS):
        raise ValueError("Invalid burn/history/future window boundaries")
    if len(set(CONDITIONS)) != len(CONDITIONS):
        raise ValueError("CONDITIONS contains duplicates")


def parse_master_seed(value: str) -> int:
    """Parse an integer master seed or generate one when value is 'random'."""
    if value.strip().lower() == "random":
        return secrets.randbits(64)
    try:
        seed = int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "master seed must be a nonnegative integer or 'random'"
        ) from exc
    if seed < 0:
        raise argparse.ArgumentTypeError("master seed must be nonnegative")
    return seed


def generate_seed_set(master_seed: int, n_seeds: int) -> list[int]:
    """Generate a deterministic randomized seed list from one master seed.

    Each returned seed identifies one paired experiment across all conditions.
    run_aief() splits it into independent initialization and shuffle streams.
    """
    if n_seeds <= 0:
        raise ValueError("n_seeds must be positive")

    root = np.random.SeedSequence(master_seed)
    children = root.spawn(n_seeds)
    seeds = [
        int(child.generate_state(1, dtype=np.uint64)[0])
        for child in children
    ]
    if len(set(seeds)) != len(seeds):
        raise RuntimeError("Generated duplicate seeds; choose another master seed")
    return seeds


def source_sha256() -> str | None:
    try:
        return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except (NameError, OSError):
        return None


def atomic_write_text(path: str, text: str) -> None:
    temp_path = f"{path}.tmp-{os.getpid()}-{time.time_ns()}"
    try:
        with open(temp_path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def save_npz_atomic(path: str, payload: dict[str, Any]) -> None:
    temp_path = f"{path}.tmp-{os.getpid()}-{time.time_ns()}.npz"
    try:
        np.savez_compressed(temp_path, **payload)
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def load_checkpoint(path: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    with np.load(path, allow_pickle=False) as data:
        for key in data.files:
            value = data[key]
            result[key] = value.item() if value.ndim == 0 else value.copy()
    return result


def validate_checkpoint(
    result: dict[str, Any],
    *,
    condition: str,
    seed: int,
    config_hash: str,
) -> None:
    required = {
        "seed",
        "seed_index",
        "condition",
        "config_hash",
        *SCALAR_KEYS,
        *MATRIX_KEYS,
    }
    missing = required - result.keys()
    if missing:
        raise RuntimeError(f"checkpoint missing keys: {sorted(missing)}")
    if result["config_hash"] != config_hash:
        raise RuntimeError("configuration hash mismatch")
    if result["condition"] != condition or int(result["seed"]) != seed:
        raise RuntimeError("checkpoint identity mismatch")
    for key in MATRIX_KEYS:
        matrix = np.asarray(result[key])
        if matrix.shape != (N, N):
            raise RuntimeError(f"checkpoint matrix {key} has shape {matrix.shape}")
        if not np.all(np.isfinite(matrix)):
            raise RuntimeError(f"checkpoint matrix {key} contains nonfinite values")


def summarize(values: Iterable[float]) -> tuple[float, float, int]:
    x = np.asarray(list(values), dtype=float)
    valid = np.isfinite(x)
    if not np.any(valid):
        return np.nan, np.nan, 0
    return float(np.mean(x[valid])), float(np.std(x[valid])), int(np.sum(valid))


def safe_corr(x: np.ndarray, y: np.ndarray, eps: float = ZERO_TOL) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    x = x[valid]
    y = y[valid]
    if len(x) < 3 or np.std(x) < eps or np.std(y) < eps:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def safe_covariance(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    x = x[valid]
    y = y[valid]
    if len(x) < 2:
        return np.nan
    return float(np.mean((x - np.mean(x)) * (y - np.mean(y))))


# ============================================================
# Network diagnostics
# ============================================================


def effective_number(weights: np.ndarray, eps: float = ZERO_TOL) -> float:
    weights = np.asarray(weights, dtype=float)
    total = float(np.sum(weights))
    sum_sq = float(np.sum(weights**2))
    if total <= eps or sum_sq <= eps:
        return 0.0
    return total**2 / sum_sq


def gini_coefficient(weights: np.ndarray, eps: float = ZERO_TOL) -> float:
    x = np.sort(np.asarray(weights, dtype=float))
    total = float(np.sum(x))
    if total <= eps:
        return 0.0
    n = len(x)
    ranks = np.arange(1, n + 1, dtype=float)
    return float(2.0 * np.dot(ranks, x) / (n * total) - (n + 1.0) / n)


def normalized_weight_entropy(weights: np.ndarray, eps: float = ZERO_TOL) -> float:
    weights = np.asarray(weights, dtype=float)
    total = float(np.sum(weights))
    if total <= eps:
        return 0.0
    p = weights / total
    positive = p > 0.0
    entropy = -float(np.sum(p[positive] * np.log(p[positive])))
    max_entropy = float(np.log(len(weights)))
    return entropy / max_entropy if max_entropy > 0.0 else 0.0


# ============================================================
# Model
# ============================================================


def compute_R(
    theta_now: np.ndarray,
    theta_delayed: np.ndarray,
    tau_eff: float,
    coherence_acc: np.ndarray,
) -> np.ndarray:
    dphi = (
        theta_now[:, None]
        - theta_delayed[None, :]
        - ((OMEGA[:, None] + OMEGA[None, :]) / 2.0) * tau_eff
    )
    z_inst = np.exp(1j * dphi)
    coherence_acc[:] = ALPHA * coherence_acc + (1.0 - ALPHA) * z_inst
    return np.abs(coherence_acc)


def run_aief(
    condition: str,
    *,
    seed: int,
    seed_index: int,
    config_hash: str,
) -> dict[str, Any]:
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition: {condition}")

    # Separate streams ensure all conditions have exactly matched initial states,
    # while shuffle_R randomness cannot alter initialization draws.
    stream_root = np.random.SeedSequence(seed)
    init_sequence, shuffle_sequence = stream_root.spawn(2)
    init_rng = np.random.default_rng(init_sequence)
    shuffle_rng = np.random.default_rng(shuffle_sequence)

    theta = init_rng.random(N) * 2.0 * np.pi
    B = B_INIT_SCALE * init_rng.random((N, N))
    B = 0.5 * (B + B.T)
    np.fill_diagonal(B, 0.0)

    coherence_acc = np.zeros((N, N), dtype=complex)
    history = deque(
        (theta.copy() for _ in range(DELAY_STEPS + 1)),
        maxlen=DELAY_STEPS + 1,
    )

    R_physical_sum = np.zeros((N, N), dtype=float)
    R_driver_sum = np.zeros((N, N), dtype=float)
    P_sum = np.zeros((N, N), dtype=float)
    R_physical_future_sum = np.zeros((N, N), dtype=float)
    R_driver_future_sum = np.zeros((N, N), dtype=float)

    r_sum = 0.0
    r_count = 0

    G_min_over_time = np.inf
    G_min_pre_over_time = np.inf
    pre_gap_violation_steps = 0
    projection_active_steps = 0
    projection_norm_sum = 0.0
    projection_norm_max = 0.0
    B_at_split: np.ndarray | None = None

    cap = (A - DELTA) / Q

    for step in range(N_STEPS):
        if step == HIST_END:
            B_at_split = B.copy()

        theta_delayed = theta if condition == "no_delay" else history[0]
        tau_eff = 0.0 if condition == "no_delay" else TAU

        R_physical = compute_R(theta, theta_delayed, tau_eff, coherence_acc)
        R_physical = 0.5 * (R_physical + R_physical.T)
        np.fill_diagonal(R_physical, 0.0)

        R_driver = R_physical
        if condition == "shuffle_R":
            values = R_physical[EDGES].copy()
            shuffle_rng.shuffle(values)
            R_driver = np.zeros_like(R_physical)
            R_driver[EDGES] = values
            R_driver[(EDGES[1], EDGES[0])] = values

        mu_eff = 0.0 if condition == "no_mu" else MU
        B += DT * ((ETA + mu_eff) * R_driver - mu_eff - GAMMA * B)
        B = np.maximum(B, 0.0)
        B = 0.5 * (B + B.T)
        np.fill_diagonal(B, 0.0)

        row_sum_pre = np.sum(B, axis=1)
        G_pre = A - Q * row_sum_pre
        G_min_pre_over_time = min(G_min_pre_over_time, float(np.min(G_pre)))
        pre_violation = bool(np.any(G_pre < DELTA))
        pre_gap_violation_steps += int(pre_violation)

        if condition != "no_gap" and pre_violation:
            B_before = B.copy()
            scale = np.minimum(1.0, cap / (row_sum_pre + ZERO_TOL))
            B *= np.minimum.outer(scale, scale)
            np.fill_diagonal(B, 0.0)

            projection_norm = float(np.linalg.norm(B - B_before))
            if projection_norm > PROJECTION_NORM_TOL:
                projection_active_steps += 1
                projection_norm_sum += projection_norm
                projection_norm_max = max(projection_norm_max, projection_norm)

        row_sum = np.sum(B, axis=1)
        G = A - Q * row_sum
        G_min_step = float(np.min(G))
        G_min_over_time = min(G_min_over_time, G_min_step)

        if condition != "no_gap" and G_min_step < DELTA - GAP_TOL:
            raise RuntimeError(
                f"dominance-gap violation in {condition}, seed={seed}, "
                f"step={step}: {G_min_step}"
            )

        if BURN_END <= step < HIST_END:
            R_physical_sum += R_physical
            R_driver_sum += R_driver

        if step >= HIST_END:
            P_sum += B > B_C
            R_physical_future_sum += R_physical
            R_driver_future_sum += R_driver

        coupling = np.sum(
            B * np.sin(theta_delayed[None, :] - theta[:, None]),
            axis=1,
        )
        theta = np.mod(theta + DT * (OMEGA + coupling), 2.0 * np.pi)
        history.append(theta.copy())

        if step % DIAGNOSTIC_STRIDE == 0:
            r_sum += float(np.abs(np.mean(np.exp(1j * theta))))
            r_count += 1

    if B_at_split is None:
        raise RuntimeError("B_at_split was not captured")

    history_count = HIST_END - BURN_END
    future_count = N_STEPS - HIST_END
    R_physical_bar = R_physical_sum / history_count
    R_driver_bar = R_driver_sum / history_count
    P_future = P_sum / future_count
    R_physical_future_bar = R_physical_future_sum / future_count
    R_driver_future_bar = R_driver_future_sum / future_count

    matrices = {
        "B_at_split": B_at_split,
        "P_future": P_future,
        "R_physical_past": R_physical_bar,
        "R_driver_past": R_driver_bar,
        "R_physical_future": R_physical_future_bar,
        "R_driver_future": R_driver_future_bar,
        "B_final": B.copy(),
    }
    for name, matrix in matrices.items():
        if matrix.shape != (N, N) or not np.all(np.isfinite(matrix)):
            raise FloatingPointError(f"invalid matrix {name} in {condition}, seed={seed}")
        if not np.allclose(matrix, matrix.T, rtol=0.0, atol=1e-10):
            raise RuntimeError(f"asymmetric matrix {name} in {condition}, seed={seed}")

    p_edge = P_future[EDGES]
    r_phys_edge = R_physical_bar[EDGES]
    r_driver_edge = R_driver_bar[EDGES]
    final_weights = B[EDGES]
    final_row_sums = np.sum(B, axis=1)

    corr_physical = safe_corr(p_edge, r_phys_edge)
    corr_driver = safe_corr(p_edge, r_driver_edge)
    cov_physical = safe_covariance(p_edge, r_phys_edge)
    cov_driver = safe_covariance(p_edge, r_driver_edge)

    r_mean = r_sum / r_count
    D_B = float(np.count_nonzero(final_weights > B_C) / N_EDGES)
    Phi = np.nan if D_B < ZERO_TOL else float(r_mean * D_B_STAR / D_B)

    L_final = np.diag(final_row_sums) - B
    eigenvalues = np.clip(np.linalg.eigvalsh(L_final), 0.0, None)
    spectral_total = float(np.sum(eigenvalues))
    if spectral_total < ZERO_TOL:
        S_final = 0.0
    else:
        spectral_probabilities = eigenvalues / spectral_total
        positive = spectral_probabilities > 0.0
        S_final = -float(
            np.sum(
                spectral_probabilities[positive]
                * np.log(spectral_probabilities[positive])
            )
        )

    p_finite = p_edge[np.isfinite(p_edge)]
    P_mean = float(np.mean(p_finite))
    P_variance = float(np.var(p_finite))
    P_max = float(np.max(p_finite))
    P_nonzero_fraction = float(np.mean(p_finite > 0.0))
    P_degenerate = bool(np.std(p_finite) < ZERO_TOL)

    total_edge_weight = float(np.sum(final_weights))
    active_projection_denominator = max(projection_active_steps, 1)

    result: dict[str, Any] = {
        "seed": int(seed),
        "seed_index": int(seed_index),
        "condition": condition,
        "config_hash": config_hash,
        "D_B": D_B,
        "Corr_physical": corr_physical,
        "Corr_driver": corr_driver,
        "Phi": Phi,
        "r_mean": float(r_mean),
        "S_spectral": S_final,
        "G_min_final": float(np.min(A - Q * final_row_sums)),
        "G_min_over_time": float(G_min_over_time),
        "G_min_pre_over_time": float(G_min_pre_over_time),
        "P_mean": P_mean,
        "P_variance": P_variance,
        "P_max": P_max,
        "P_nonzero_fraction": P_nonzero_fraction,
        "P_degenerate": P_degenerate,
        "Cov_physical": cov_physical,
        "Cov_driver": cov_driver,
        "Total_edge_weight": total_edge_weight,
        "Mean_row_sum": float(np.mean(final_row_sums)),
        "Max_row_sum": float(np.max(final_row_sums)),
        "Nonzero_edge_fraction": float(np.mean(final_weights > ZERO_TOL)),
        "Effective_edges": float(effective_number(final_weights)),
        "Weight_gini": float(gini_coefficient(final_weights)),
        "Weight_entropy": float(normalized_weight_entropy(final_weights)),
        "Pre_gap_violation_fraction": float(pre_gap_violation_steps / N_STEPS),
        "Projection_active_fraction": float(projection_active_steps / N_STEPS),
        "Projection_norm_mean_active": float(
            projection_norm_sum / active_projection_denominator
        ),
        "Projection_norm_max": float(projection_norm_max),
        **matrices,
    }
    return result


# ============================================================
# Output
# ============================================================


def build_manifest(master_seed: int, seeds: list[int], n_seeds: int) -> dict[str, Any]:
    return {
        "workflow_version": WORKFLOW_VERSION,
        "source_sha256": source_sha256(),
        "model": {
            "N": N,
            "T_sim": T_SIM,
            "dt": DT,
            "tau": TAU,
            "omega": OMEGA.tolist(),
            "a": A,
            "q": Q,
            "delta": DELTA,
            "eta": ETA,
            "gamma": GAMMA,
            "mu": MU,
            "T_window": T_WINDOW,
            "alpha": ALPHA,
            "B_c": B_C,
            "B_init_scale": B_INIT_SCALE,
            "D_B_star": D_B_STAR,
        },
        "protocol": {
            "conditions": list(CONDITIONS),
            "delay_steps": DELAY_STEPS,
            "n_steps": N_STEPS,
            "burn_fraction": BURN_FRACTION,
            "history_end_fraction": HISTORY_END_FRACTION,
            "burn_end": BURN_END,
            "hist_end": HIST_END,
            "diagnostic_stride": DIAGNOSTIC_STRIDE,
            "gap_tolerance": GAP_TOL,
            "projection_norm_tolerance": PROJECTION_NORM_TOL,
        },
        "randomization": {
            "master_seed": int(master_seed),
            "n_seeds": int(n_seeds),
            "paired_seeds": [int(seed) for seed in seeds],
            "seed_generation": "SeedSequence(master_seed).spawn(n_seeds)",
            "per_run_streams": "SeedSequence(seed).spawn(init, shuffle)",
            "bit_generator": np.random.default_rng(0).bit_generator.__class__.__name__,
        },
        "environment": {
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "platform": platform.platform(),
        },
        "schema": {
            "scalar_keys": list(SCALAR_KEYS),
            "matrix_keys": list(MATRIX_KEYS),
        },
    }


def write_csv_atomic(path: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError("cannot write an empty scalar CSV")
    temp_path = f"{path}.tmp-{os.getpid()}-{time.time_ns()}"
    try:
        with open(temp_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def fmt_metric(values: Iterable[float]) -> tuple[str, int]:
    mean, std, valid = summarize(values)
    if not np.isfinite(mean):
        return "nan±nan", valid
    return f"{mean:.3f}±{std:.3f}", valid


def print_summary(results: dict[str, list[dict[str, Any]]]) -> None:
    print("=" * 150)
    print("AIEF-1.3 FALSIFICATION MATRIX — mean ± std over paired seeds")
    print("=" * 150)
    print(
        f"{'Condition':<12} {'D_B':>13} {'Corr_phys':>13} {'Corr_drv':>13} "
        f"{'Phi':>13} {'r_mean':>13} {'G_min':>13} {'P_mean':>13} "
        f"{'Eff_edges':>13} {'Proj_frac':>13}  valid(Cp/Cd/Phi)"
    )
    print("-" * 150)

    for condition in CONDITIONS:
        runs = results[condition]
        d_b, _ = fmt_metric(run["D_B"] for run in runs)
        corr_p, n_p = fmt_metric(run["Corr_physical"] for run in runs)
        corr_d, n_d = fmt_metric(run["Corr_driver"] for run in runs)
        phi, n_phi = fmt_metric(run["Phi"] for run in runs)
        r_mean, _ = fmt_metric(run["r_mean"] for run in runs)
        g_min, _ = fmt_metric(run["G_min_over_time"] for run in runs)
        p_mean, _ = fmt_metric(run["P_mean"] for run in runs)
        effective, _ = fmt_metric(run["Effective_edges"] for run in runs)
        projection, _ = fmt_metric(run["Projection_active_fraction"] for run in runs)
        print(
            f"{condition:<12} {d_b:>13} {corr_p:>13} {corr_d:>13} "
            f"{phi:>13} {r_mean:>13} {g_min:>13} {p_mean:>13} "
            f"{effective:>13} {projection:>13}  {n_p}/{n_d}/{n_phi}"
        )

    print("=" * 150)
    print("Corr_phys: past physical resonance vs future persistence.")
    print("Corr_drv: past adaptation driver vs future persistence.")
    print("P_mean: mean future-window threshold persistence over unique edges.")
    print("Eff_edges: concentration-based effective number of final undirected edges.")
    print("Proj_frac: fraction of integration steps with an active gap projection.")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--master-seed",
        type=parse_master_seed,
        default=DEFAULT_MASTER_SEED,
        help=(
            "master seed for the paired randomized seed set; use 'random' to "
            "generate and record a fresh 64-bit master seed "
            f"(default: {DEFAULT_MASTER_SEED})"
        ),
    )
    parser.add_argument(
        "--n-seeds",
        type=int,
        default=DEFAULT_N_SEEDS,
        help=f"number of paired seeds (default: {DEFAULT_N_SEEDS})",
    )
    parser.add_argument(
        "--run-root",
        default=DEFAULT_RUN_ROOT,
        help=f"root output directory (default: {DEFAULT_RUN_ROOT})",
    )
    return parser.parse_args()


def main() -> None:
    validate_configuration()
    args = parse_arguments()
    if args.n_seeds <= 0:
        raise ValueError("--n-seeds must be positive")

    master_seed = int(args.master_seed)
    seeds = generate_seed_set(master_seed, args.n_seeds)
    manifest_base = build_manifest(master_seed, seeds, args.n_seeds)
    manifest_text = json.dumps(
        manifest_base,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    config_hash = hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()[:12]
    run_dir = os.path.join(args.run_root, config_hash)
    os.makedirs(run_dir, exist_ok=True)

    manifest = {**manifest_base, "config_hash": config_hash}
    manifest_path = os.path.join(run_dir, "manifest.json")
    atomic_write_text(
        manifest_path,
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )

    print("Running AIEF-1.3 production workflow")
    print(f"  workflow version: {WORKFLOW_VERSION}")
    print(f"  master seed:      {master_seed}")
    print(f"  paired seeds:     {args.n_seeds}")
    print(f"  configuration:    {config_hash}")
    print(f"  output:           {run_dir}")

    results: dict[str, list[dict[str, Any]]] = {
        condition: [] for condition in CONDITIONS
    }
    start_time = time.time()

    for condition in CONDITIONS:
        for seed_index, seed in enumerate(seeds):
            run_file = os.path.join(
                run_dir,
                f"{condition}_seed_{seed}.npz",
            )

            if os.path.exists(run_file):
                try:
                    result = load_checkpoint(run_file)
                    validate_checkpoint(
                        result,
                        condition=condition,
                        seed=seed,
                        config_hash=config_hash,
                    )
                    status = "loaded"
                except Exception as exc:
                    print(f"  invalid checkpoint {run_file}: {exc}; recomputing")
                    os.remove(run_file)
                    result = run_aief(
                        condition,
                        seed=seed,
                        seed_index=seed_index,
                        config_hash=config_hash,
                    )
                    save_npz_atomic(run_file, result)
                    status = "recomputed"
            else:
                result = run_aief(
                    condition,
                    seed=seed,
                    seed_index=seed_index,
                    config_hash=config_hash,
                )
                save_npz_atomic(run_file, result)
                status = "completed"

            results[condition].append(result)
            if (seed_index + 1) % 5 == 0 or seed_index + 1 == len(seeds):
                print(
                    f"  {condition}: {seed_index + 1}/{len(seeds)} seeds "
                    f"available (last {status})"
                )

    elapsed = time.time() - start_time
    print(f"Total runtime: {elapsed:.1f} s\n")

    expected_runs = len(CONDITIONS) * len(seeds)
    actual_runs = sum(len(runs) for runs in results.values())
    if actual_runs != expected_runs:
        raise RuntimeError(f"incomplete result set: {actual_runs}/{expected_runs}")

    matrix_output: dict[str, np.ndarray] = {}
    scalar_rows: list[dict[str, Any]] = []

    for condition in CONDITIONS:
        for result in results[condition]:
            prefix = f"{condition}_seed_{result['seed']}"
            for key in MATRIX_KEYS:
                matrix_output[f"{prefix}_{key}"] = np.asarray(result[key])

            scalar_rows.append(
                {
                    "condition": condition,
                    "seed_index": int(result["seed_index"]),
                    "seed": int(result["seed"]),
                    **{key: result[key] for key in SCALAR_KEYS},
                }
            )

    if len(matrix_output) != expected_runs * len(MATRIX_KEYS):
        raise RuntimeError("incomplete matrix aggregate")

    matrix_path = os.path.join(
        run_dir,
        f"AIEF_1_3_{config_hash}_edge_diagnostics.npz",
    )
    csv_path = os.path.join(
        run_dir,
        f"AIEF_1_3_{config_hash}_scalar_summary.csv",
    )
    save_npz_atomic(matrix_path, matrix_output)
    write_csv_atomic(csv_path, scalar_rows)

    print_summary(results)
    print(f"Saved run artifacts to {run_dir}")
    print(f"  {os.path.basename(manifest_path)}")
    print(f"  {os.path.basename(matrix_path)}")
    print(f"  {os.path.basename(csv_path)}")
    print("  per-condition/per-seed checkpoint files")


if __name__ == "__main__":
    main()
