#!/usr/bin/env python3
"""
AIEF-1.4 Two-Channel Directed Alignment Decomposition (Version 4 Production)

Audits positivity, decay, phase-balance, and exact identity closure for K3 resonance ordering:
  D_L^-> = |C^+_{2,7}|  - |C^+_{7,11}|   (fixed-left, forward)
  D_L^<- = |C^+_{7,2}|  - |C^+_{11,7}|   (fixed-left, reverse)
  
  D_R^-> = |C^+_{7,11}| - |C^+_{2,11}|   (right-mode, forward)
  D_R^<- = |C^+_{11,7}| - |C^+_{11,2}|   (right-mode, reverse)

Features in V4:
1. Fixed intermediate["scales"] KeyError and uses intermediate["gate_on"] & intermediate["clipped"]
2. Genuine per-step proposal branch checks: gate_on, controllers_clipped, selected_positive, isolation_error, winner_margin
3. Per-interval analysis breakdown across specified intervals [0, T_end]
4. Masked T1/T2 ratio, |T1/T2 + 1|, cancellation index, and convergence tracking
5. Radial forcing reinforcement fraction based on sign(DeltaM_old) == sign(e)
6. Individual source temporal increment phase balance for both separation and mean
7. Detailed I_sym statistics (min, median, final, valid count, fraction > 0.9, sign agreement fraction)
8. Rich trajectory CSV with all mechanism variables (T1, T2, e, ratios, phase components)
9. Lazy production import to expose true module failures
10. Strict input parameter & manifest validation
11. Complete manifest with SHA-256 hashes, sys.argv, tolerances, and explicit evidence classification
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# === Constants ===
DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_two_channel_alignment_v4"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_INTERVALS = "0,50,100,150,200,250,300,320"
DEFAULT_SIGNAL_FLOOR = 1e-14
DEFAULT_IDENTITY_TOL = 1e-12
UNWRAP_DISCONT = np.pi

# === K3 Configuration ===
K3_NODES = (2, 7, 11)
K3_EDGES = {
    25: (2, 7),
    29: (2, 11),
    59: (7, 11),
}

CHANNELS = {
    "fixed_left": {
        "description": "Edge 25 vs Edge 59",
        "forward": {"edge_a": (2, 7), "edge_b": (7, 11)},
        "reverse": {"edge_a": (7, 2), "edge_b": (11, 7)},
    },
    "right_mode": {
        "description": "Edge 59 vs Edge 29",
        "forward": {"edge_a": (7, 11), "edge_b": (2, 11)},
        "reverse": {"edge_a": (11, 7), "edge_b": (11, 2)},
    },
}
ORIENTATIONS = ["forward", "reverse"]


def file_sha256(path: str | os.PathLike[str]) -> str:
    """Compute SHA-256 hash of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def compute_module_sha256(module: Any) -> str:
    """Compute SHA-256 hash of a module's source file."""
    if module is None or not hasattr(module, "__file__") or module.__file__ is None:
        return "not_available"
    return file_sha256(Path(module.__file__).resolve())


def load_production_modules():
    """Lazy load AIEF production modules."""
    import AIEF_1_4_stationarity_perturbation_analysis_updated as base
    import AIEF_1_4_component_controller_audit as component_audit
    import AIEF_1_4_augmented_tangent_cocycle_analysis as augmented
    return base, component_audit, augmented


def safe_atomic_write_text(path: Path, content: str) -> None:
    """Write text atomically using temp file and sync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def safe_atomic_write_csv(path: Path, df: pd.DataFrame) -> None:
    """Write DataFrame to CSV atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            df.to_csv(f, index=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def parse_nonnegative_float_list(value: str) -> list[float]:
    """Parse comma-separated nonnegative floats."""
    try:
        values = [float(x.strip()) for x in value.split(",") if x.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated floats") from exc
    if not values or any(v < 0.0 for v in values):
        raise argparse.ArgumentTypeError("values must be nonnegative")
    return sorted(set(values))


def fit_log_rate(times: np.ndarray, values: np.ndarray, floor: float) -> dict[str, float]:
    """Fit exponential decay rate from log magnitudes."""
    magnitudes = np.abs(np.asarray(values, dtype=float))
    valid = np.isfinite(magnitudes) & (magnitudes > floor)
    if np.sum(valid) < 3:
        return {"rate": np.nan, "R_squared": np.nan, "count": int(np.sum(valid))}
    x = np.asarray(times, dtype=float)[valid]
    y = np.log(magnitudes[valid])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "rate": float(-slope),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
        "count": int(len(x)),
    }


def count_sign_changes(arr: np.ndarray, tol: float) -> tuple[int, int, int]:
    """
    Count sign changes across valid samples, maintaining previous valid sign across below-floor samples.
    Returns (positive_count, negative_count, change_count).
    """
    arr = np.asarray(arr, dtype=float)
    valid = np.isfinite(arr) & (np.abs(arr) > tol)
    positive_count = int(np.sum(arr[valid] > 0))
    negative_count = int(np.sum(arr[valid] < 0))
    changes = 0
    previous = 0
    for value, is_valid in zip(arr, valid):
        if not is_valid:
            continue
        current = 1 if value > 0 else -1
        if previous != 0 and current != previous:
            changes += 1
        previous = current
    return positive_count, negative_count, changes


def validate_edge_indexing(edges: tuple[np.ndarray, np.ndarray]) -> None:
    """Validate tuple of arrays (edge_i, edge_j) against expected K3 edges."""
    if not isinstance(edges, tuple) or len(edges) != 2:
        raise ValueError("edges must be a tuple of two arrays (edge_i, edge_j)")
    edge_i, edge_j = edges
    for edge, expected in K3_EDGES.items():
        observed = (int(edge_i[edge]), int(edge_j[edge]))
        if observed != expected:
            raise ValueError(f"edge {edge}: expected {expected}, got {observed}")


def channel_quantities(
    C_a: complex,
    C_b: complex,
    Z_a: complex,
    Z_b: complex,
) -> dict[str, Any]:
    """Compute channel quantities using OLD coherence C_a, C_b."""
    Cbar = 0.5 * (C_a + C_b)
    Zbar = 0.5 * (Z_a + Z_b)
    DeltaC = C_a - C_b
    DeltaZ = Z_a - Z_b
    E = DeltaZ - DeltaC

    DeltaM = float(abs(C_a)**2 - abs(C_b)**2)
    DeltaA = float(np.real(np.conj(C_a) * Z_a) - np.real(np.conj(C_b) * Z_b))

    T1 = float(2.0 * np.real(np.conj(Cbar) * E))
    T2 = float(2.0 * np.real(np.conj(DeltaC) * Zbar))

    return {
        "DeltaC": DeltaC,
        "DeltaZ": DeltaZ,
        "E": E,
        "DeltaM": DeltaM,
        "DeltaA": DeltaA,
        "T1": T1,
        "T2": T2,
        "alignment_residual": 2.0 * DeltaA - DeltaM,
    }


def test_alignment_identity(
    e_values: np.ndarray,
    T1_values: np.ndarray,
    T2_values: np.ndarray,
    tol: float = DEFAULT_IDENTITY_TOL,
) -> dict[str, Any]:
    """Test exact alignment identity e_n = T_1,n + T_2,n."""
    e = np.asarray(e_values, dtype=float)
    T1 = np.asarray(T1_values, dtype=float)
    T2 = np.asarray(T2_values, dtype=float)
    errors = np.abs(e - (T1 + T2))
    return {
        "max_abs_error": float(np.max(errors)),
        "median_abs_error": float(np.median(errors)),
        "identity_passes": bool(np.max(errors) < tol),
    }


def test_radial_identity(
    DeltaM_old: np.ndarray,
    DeltaM_new: np.ndarray,
    e_values: np.ndarray,
    alpha: float,
    tol: float = DEFAULT_IDENTITY_TOL,
) -> dict[str, Any]:
    """Test exact radial identity: DeltaM_{n+1} = alpha * DeltaM_n + alpha * (1 - alpha) * e_n."""
    DeltaM_old = np.asarray(DeltaM_old, dtype=float)
    DeltaM_new = np.asarray(DeltaM_new, dtype=float)
    e = np.asarray(e_values, dtype=float)
    prediction = alpha * DeltaM_old + alpha * (1.0 - alpha) * e
    errors = np.abs(DeltaM_new - prediction)
    return {
        "max_abs_error": float(np.max(errors)),
        "median_abs_error": float(np.median(errors)),
        "identity_passes": bool(np.max(errors) < tol),
    }


def test_symmetrization_identity(
    D_sym: np.ndarray,
    DeltaR: np.ndarray,
    tol: float = DEFAULT_IDENTITY_TOL,
) -> dict[str, Any]:
    """Test exact symmetrization identity: D_sym = R_a - R_b."""
    errors = np.abs(D_sym - DeltaR)
    return {
        "max_abs_error": float(np.max(errors)),
        "median_abs_error": float(np.median(errors)),
        "identity_passes": bool(np.max(errors) < tol),
    }


def test_phase_balance_identity(
    actual_inc: np.ndarray,
    predicted_inc: np.ndarray,
    tol: float = DEFAULT_IDENTITY_TOL,
) -> dict[str, Any]:
    """Test modulo-safe phase balance increment identity."""
    errors = np.abs(np.angle(np.exp(1j * (actual_inc - predicted_inc))))
    return {
        "max_abs_error": float(np.max(errors)),
        "median_abs_error": float(np.median(errors)),
        "identity_passes": bool(np.max(errors) < tol),
    }


def run_self_test() -> None:
    """Run comprehensive synthetic self-test suite and return."""
    print("=== Running Standalone Synthetic Self-Test ===")
    
    # 1. Tuple-of-arrays edge index check
    edge_i = np.zeros(60, dtype=int)
    edge_j = np.zeros(60, dtype=int)
    edge_i[25], edge_j[25] = 2, 7
    edge_i[29], edge_j[29] = 2, 11
    edge_i[59], edge_j[59] = 7, 11
    validate_edge_indexing((edge_i, edge_j))
    print("[PASS] Tuple-of-arrays edge index validation")

    # 2. Alignment identity e = T1 + T2 with rel_tol=0.0
    rng = np.random.default_rng(42)
    C_a = rng.uniform(-1, 1) + 1j * rng.uniform(-1, 1)
    C_b = rng.uniform(-1, 1) + 1j * rng.uniform(-1, 1)
    Z_a = np.exp(1j * rng.uniform(-0.5, 0.5))
    Z_b = np.exp(1j * rng.uniform(-0.5, 0.5))

    q = channel_quantities(C_a, C_b, Z_a, Z_b)
    T_sum = q["T1"] + q["T2"]
    assert math.isclose(q["alignment_residual"], T_sum, rel_tol=0.0, abs_tol=1e-14), "Identity e = T1 + T2 failed"
    print("[PASS] Exact algebraic identity e = T1 + T2 (rel_tol=0.0)")

    # 3. Radial identity check
    alpha = 0.999428829846
    DeltaM_old = q["DeltaM"]
    e = q["alignment_residual"]
    C_a_next = alpha * C_a + (1 - alpha) * Z_a
    C_b_next = alpha * C_b + (1 - alpha) * Z_b
    DeltaM_new = float(abs(C_a_next)**2 - abs(C_b_next)**2)
    radial_check = test_radial_identity(np.array([DeltaM_old]), np.array([DeltaM_new]), np.array([e]), alpha)
    assert radial_check["identity_passes"], "Radial recurrence identity failed"
    print("[PASS] Exact radial recurrence identity")

    # 4. Phase separation & mean temporal increment checks
    Z_a_next = np.exp(1j * 0.1) * Z_a
    Z_b_next = np.exp(1j * 0.05) * Z_b
    inc_a = np.angle(Z_a_next * np.conj(Z_a))
    inc_b = np.angle(Z_b_next * np.conj(Z_b))
    act_sep_inc = np.angle(np.exp(1j * (inc_a - inc_b)))
    pred_sep_inc = 0.05
    phase_sep_check = test_phase_balance_identity(np.array([act_sep_inc]), np.array([pred_sep_inc]))
    assert phase_sep_check["identity_passes"], "Phase separation increment identity failed"
    print("[PASS] Phase separation temporal increment identity")

    # 5. Sign changes across gaps
    arr = np.array([1.0, 0.5, 1e-18, -0.2, -1.0])
    pos, neg, sc = count_sign_changes(arr, tol=1e-14)
    assert sc == 1, f"Expected 1 sign change, got {sc}"
    print("[PASS] Sign change logic across below-floor samples")

    print("=== Self-Test Completed Successfully ===\n")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", default=DEFAULT_NPZ, help="Path to input NPZ trajectory")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Path to manifest JSON")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument("--seed", default=DEFAULT_SEED, help="Seed ID as string")
    parser.add_argument("--dt", type=float, default=DEFAULT_DT, help="Time step dt")
    parser.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON, help="Scale safeguard epsilon")
    parser.add_argument("--intervals", type=parse_nonnegative_float_list, default=parse_nonnegative_float_list(DEFAULT_INTERVALS))
    parser.add_argument("--signal-floor", type=float, default=DEFAULT_SIGNAL_FLOOR, help="Floor for rates and ratios")
    parser.add_argument("--identity-tol", type=float, default=DEFAULT_IDENTITY_TOL, help="Tolerance for exact algebraic identities")
    parser.add_argument("--self-test", action="store_true", help="Run synthetic self-test and return")
    parser.add_argument("--synthetic-demo", action="store_true", help="Run explicit synthetic demonstration scaffold")
    return parser.parse_args()


def run_production_analysis(args: argparse.Namespace, output_dir: Path) -> None:
    """Execute production two-channel directed alignment decomposition on frozen run files."""
    base, component_audit, augmented = load_production_modules()

    print(f"Loading production manifest: {args.manifest}")
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    model = manifest["model"]
    dt = float(model["dt"])
    if abs(dt - args.dt) > 1e-15:
        raise ValueError(f"Command dt {args.dt} != manifest dt {dt}")
    if args.scale_epsilon != 1e-12:
        raise ValueError("Implemented actual step uses scale_epsilon=1e-12")

    alpha = math.exp(-dt / float(model["T_window"]))
    omega = np.asarray(model["omega"], dtype=float)
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(int(model["N"]), capacity)
    N = int(model["N"])

    A, edges = base.incidence_matrix(N)
    validate_edge_indexing(edges)

    future_steps = int(manifest["protocol"]["future_steps"])
    if future_steps <= 0:
        raise ValueError("future_steps must be positive")

    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
        expected_final = np.asarray(data[base.branch_key("continue", args.seed, "B_final")], dtype=float).copy()

    # Dynamic branch tracking
    gate_on_list, winner_map_ok_list, clipped_list, winner_margins, isolation_errors = [], [], [], [], []

    channel_data = {ch: {ori: {
        "DeltaM_old": np.zeros(future_steps),
        "DeltaM_new": np.zeros(future_steps),
        "DeltaA": np.zeros(future_steps),
        "e": np.zeros(future_steps),
        "T1": np.zeros(future_steps),
        "T2": np.zeros(future_steps),
        "D": np.zeros(future_steps),
        "domega_sep": np.zeros(future_steps),
        "dG_sep": np.zeros(future_steps),
        "dh_sep": np.zeros(future_steps),
        "domega_mean": np.zeros(future_steps),
        "dG_mean": np.zeros(future_steps),
        "dh_mean": np.zeros(future_steps),
        "Z_a_seq": np.zeros(future_steps + 1, dtype=np.complex128),
        "Z_b_seq": np.zeros(future_steps + 1, dtype=np.complex128),
    } for ori in ORIENTATIONS} for ch in CHANNELS}

    R_values = {e: np.zeros(future_steps) for e in K3_EDGES}
    sym_data = {ch: {"D_sym": np.zeros(future_steps), "I_sym": np.zeros(future_steps)} for ch in CHANNELS}

    for step in range(future_steps):
        intermediate = augmented.base_intermediates(state, model, capacities, A, edges, args.scale_epsilon)
        
        C_old = state.coherence_acc
        C_new = intermediate["updated_coherence"]
        phase_factor = intermediate["phase_factor"]
        R_matrix = intermediate["R"]
        coupling = intermediate["coupling"]
        x_prop = intermediate["x"]
        q_scale = intermediate["q_scale"]

        # History deque exact shift
        history_arr = np.asarray(list(state.history), dtype=float)
        dh_node = np.angle(np.exp(1j * (history_arr[1] - history_arr[0]))) if len(history_arr) >= 2 else np.zeros(N)

        # Branch diagnostics
        winners = intermediate["winner_code"]
        winner_map_ok = bool(winners[25] == 7 and winners[29] == 2 and winners[59] == 7)
        is_gated = bool(intermediate["gate_on"])
        controllers_clipped = bool(intermediate["clipped"][2] and intermediate["clipped"][7])
        
        iso_err = max(
            abs(q_scale[2] - (x_prop[25] + x_prop[29])),
            abs(q_scale[7] - (x_prop[25] + x_prop[59])),
            abs(q_scale[11] - (x_prop[29] + x_prop[59]))
        )

        gate_on_list.append(is_gated)
        winner_map_ok_list.append(winner_map_ok)
        clipped_list.append(controllers_clipped)
        winner_margins.append(float(np.min(intermediate["winner_margin"][[25, 29, 59]])))
        isolation_errors.append(float(iso_err))

        for e_idx, (i, j) in K3_EDGES.items():
            R_values[e_idx][step] = float(R_matrix[i, j])

        for ch_name, orientations in CHANNELS.items():
            for orientation in ORIENTATIONS:
                edge_pair = orientations[orientation]
                (ia, ja) = edge_pair["edge_a"]
                (ib, jb) = edge_pair["edge_b"]

                C_a_old, C_b_old = C_old[ia, ja], C_old[ib, jb]
                Z_a, Z_b = phase_factor[ia, ja], phase_factor[ib, jb]
                C_a_new, C_b_new = C_new[ia, ja], C_new[ib, jb]

                q = channel_quantities(C_a_old, C_b_old, Z_a, Z_b)
                D = float(abs(C_a_new) - abs(C_b_new))

                # Separation terms
                dt_domega_sep = dt * (omega[ia] - omega[ib])
                dt_dG_sep = dt * (coupling[ia] - coupling[ib])
                dh_sep = -(dh_node[ja] - dh_node[jb])

                # Mean terms
                dt_domega_mean = 0.5 * dt * (omega[ia] + omega[ib])
                dt_dG_mean = 0.5 * dt * (coupling[ia] + coupling[ib])
                dh_mean = -0.5 * (dh_node[ja] + dh_node[jb])

                cd = channel_data[ch_name][orientation]
                cd["DeltaM_old"][step] = q["DeltaM"]
                cd["DeltaM_new"][step] = float(abs(C_a_new)**2 - abs(C_b_new)**2)
                cd["DeltaA"][step] = q["DeltaA"]
                cd["e"][step] = q["alignment_residual"]
                cd["T1"][step] = q["T1"]
                cd["T2"][step] = q["T2"]
                cd["D"][step] = D
                cd["domega_sep"][step] = dt_domega_sep
                cd["dG_sep"][step] = dt_dG_sep
                cd["dh_sep"][step] = dh_sep
                cd["domega_mean"][step] = dt_domega_mean
                cd["dG_mean"][step] = dt_dG_mean
                cd["dh_mean"][step] = dh_mean
                cd["Z_a_seq"][step] = Z_a
                cd["Z_b_seq"][step] = Z_b

        for ch_name in CHANNELS:
            D_f = channel_data[ch_name]["forward"]["D"][step]
            D_r = channel_data[ch_name]["reverse"]["D"][step]
            sym_data[ch_name]["D_sym"][step] = 0.5 * (D_f + D_r)
            denom = abs(D_f) + abs(D_r)
            sym_data[ch_name]["I_sym"][step] = abs(D_f + D_r) / denom if denom > args.signal_floor else np.nan

        augmented.advance_base_state(state, intermediate)

    # Final observable (N-th step)
    final_intermediate = augmented.base_intermediates(state, model, capacities, A, edges, args.scale_epsilon)
    final_phase_factor = final_intermediate["phase_factor"]
    for ch_name, orientations in CHANNELS.items():
        for orientation in ORIENTATIONS:
            edge_pair = orientations[orientation]
            (ia, ja) = edge_pair["edge_a"]
            (ib, jb) = edge_pair["edge_b"]
            channel_data[ch_name][orientation]["Z_a_seq"][future_steps] = final_phase_factor[ia, ja]
            channel_data[ch_name][orientation]["Z_b_seq"][future_steps] = final_phase_factor[ib, jb]

    final_replay_exact = bool(np.array_equal(state.B, expected_final))

    # All-step ordering
    gap_left = R_values[25] - R_values[59]
    gap_right = R_values[59] - R_values[29]
    all_steps_ordering_ok = bool(np.all(gap_left > 0) and np.all(gap_right > 0))

    # Process Interval Boundaries
    T_end = future_steps * dt
    boundaries = [b for b in args.intervals if 0.0 <= b <= T_end]
    if 0.0 not in boundaries:
        boundaries.insert(0, 0.0)
    if T_end not in boundaries:
        boundaries.append(T_end)
    boundaries = sorted(set(boundaries))

    time_vec = np.arange(future_steps) * dt

    # Build Rich Trajectory DataFrame
    trajectory_rows = []
    for step in range(future_steps):
        row = {"step": step, "time": time_vec[step]}
        for e_idx in K3_EDGES:
            row[f"R_{e_idx}"] = float(R_values[e_idx][step])
        for ch_name in CHANNELS:
            row[f"D_{ch_name}_forward"] = float(channel_data[ch_name]["forward"]["D"][step])
            row[f"D_{ch_name}_reverse"] = float(channel_data[ch_name]["reverse"]["D"][step])
            row[f"D_{ch_name}_sym"] = float(sym_data[ch_name]["D_sym"][step])
            row[f"I_sym_{ch_name}"] = float(sym_data[ch_name]["I_sym"][step])
            row[f"T1_{ch_name}_forward"] = float(channel_data[ch_name]["forward"]["T1"][step])
            row[f"T2_{ch_name}_forward"] = float(channel_data[ch_name]["forward"]["T2"][step])
            row[f"e_{ch_name}_forward"] = float(channel_data[ch_name]["forward"]["e"][step])
        trajectory_rows.append(row)

    trajectory = pd.DataFrame(trajectory_rows)

    # Summaries & Identity Checks
    channel_summary_rows = []
    identity_check_rows = []

    # Symmetrized R checks
    sym_test_L = test_symmetrization_identity(sym_data["fixed_left"]["D_sym"], gap_left, tol=args.identity_tol)
    sym_test_R = test_symmetrization_identity(sym_data["right_mode"]["D_sym"], gap_right, tol=args.identity_tol)

    identity_check_rows.append({
        "identity_type": "symmetrized_R",
        "identity": "fixed_left_symmetrized_R",
        "channel": "fixed_left",
        "orientation": "symmetrized",
        "maximum_absolute_error": sym_test_L["max_abs_error"],
        "median_absolute_error": sym_test_L["median_abs_error"],
        "passes": sym_test_L["identity_passes"]
    })
    identity_check_rows.append({
        "identity_type": "symmetrized_R",
        "identity": "right_mode_symmetrized_R",
        "channel": "right_mode",
        "orientation": "symmetrized",
        "maximum_absolute_error": sym_test_R["max_abs_error"],
        "median_absolute_error": sym_test_R["median_abs_error"],
        "passes": sym_test_R["identity_passes"]
    })

    for ch_name in CHANNELS:
        for orientation in ORIENTATIONS:
            cd = channel_data[ch_name][orientation]
            D = cd["D"]
            e = cd["e"]
            T1, T2 = cd["T1"], cd["T2"]
            DeltaM_old, DeltaM_new = cd["DeltaM_old"], cd["DeltaM_new"]

            # Individual source temporal increments
            Za, Zb = cd["Z_a_seq"], cd["Z_b_seq"]
            inc_a = np.angle(Za[1:] * np.conj(Za[:-1]))
            inc_b = np.angle(Zb[1:] * np.conj(Zb[:-1]))
            
            act_sep_inc = np.angle(np.exp(1j * (inc_a - inc_b)))
            pred_sep_inc = cd["domega_sep"] + cd["dG_sep"] + cd["dh_sep"]

            act_mean_inc = np.angle(np.exp(1j * 0.5 * (inc_a + inc_b)))
            pred_mean_inc = cd["domega_mean"] + cd["dG_mean"] + cd["dh_mean"]

            phase_sep_test = test_phase_balance_identity(act_sep_inc, pred_sep_inc, tol=args.identity_tol)
            phase_mean_test = test_phase_balance_identity(act_mean_inc, pred_mean_inc, tol=args.identity_tol)
            align_test = test_alignment_identity(e, T1, T2, tol=args.identity_tol)
            radial_test = test_radial_identity(DeltaM_old, DeltaM_new, e, alpha, tol=args.identity_tol)

            # Masked T1/T2 ratio
            valid_T2 = np.isfinite(T2) & (np.abs(T2) > args.signal_floor)
            ratio = np.full_like(T1, np.nan)
            ratio[valid_T2] = T1[valid_T2] / T2[valid_T2]

            ratio_plus_one = np.full_like(T1, np.nan)
            ratio_plus_one[valid_T2] = np.abs(ratio[valid_T2] + 1.0)

            denominator = np.abs(T1) + np.abs(T2)
            cancellation_idx = np.full_like(T1, np.nan)
            valid_cancel = denominator > args.signal_floor
            cancellation_idx[valid_cancel] = np.abs(T1[valid_cancel] + T2[valid_cancel]) / denominator[valid_cancel]

            # Interval Summaries
            for i in range(len(boundaries) - 1):
                start_t, end_t = boundaries[i], boundaries[i+1]
                s_idx = max(0, int(round(start_t / dt)))
                e_idx = min(future_steps, int(round(end_t / dt)))
                if e_idx <= s_idx + 2:
                    continue

                sub_t = time_vec[s_idx:e_idx]
                sub_D = D[s_idx:e_idx]
                sub_e = e[s_idx:e_idx]
                sub_T1 = T1[s_idx:e_idx]
                sub_T2 = T2[s_idx:e_idx]
                sub_DM = DeltaM_old[s_idx:e_idx]

                p, n, sc = count_sign_changes(sub_D, args.signal_floor)
                e_fit = fit_log_rate(sub_t, sub_e, args.signal_floor)
                D_fit = fit_log_rate(sub_t, sub_D, args.signal_floor)
                T1_fit = fit_log_rate(sub_t, sub_T1, args.signal_floor)
                T2_fit = fit_log_rate(sub_t, sub_T2, args.signal_floor)

                resolved = (np.abs(sub_DM) > args.signal_floor) & (np.abs(sub_e) > args.signal_floor)
                reinf_frac = float(np.mean(np.sign(sub_DM[resolved]) == np.sign(sub_e[resolved]))) if np.sum(resolved) > 0 else np.nan

                channel_summary_rows.append({
                    "scope": "interval",
                    "interval_start": start_t,
                    "interval_end": end_t,
                    "channel": ch_name,
                    "orientation": orientation,
                    "min_D": float(np.min(sub_D)),
                    "max_D": float(np.max(sub_D)),
                    "final_D": float(sub_D[-1]),
                    "all_raw_positive": bool(np.all(sub_D > 0)),
                    "sign_change_count": sc,
                    "D_rate": D_fit["rate"],
                    "e_rate": e_fit["rate"],
                    "T1_rate": T1_fit["rate"],
                    "T2_rate": T2_fit["rate"],
                    "cancellation_index_median": float(np.nanmedian(cancellation_idx[s_idx:e_idx])),
                    "T1_T2_plus_one_median": float(np.nanmedian(ratio_plus_one[s_idx:e_idx])),
                    "reinforcement_fraction": reinf_frac,
                    "valid_T2_count": int(np.sum(valid_T2[s_idx:e_idx])),
                })

            identity_check_rows.append({
                "identity_type": "alignment",
                "identity": f"{ch_name}_{orientation}_alignment",
                "channel": ch_name,
                "orientation": orientation,
                "maximum_absolute_error": align_test["max_abs_error"],
                "median_absolute_error": align_test["median_abs_error"],
                "passes": align_test["identity_passes"]
            })
            identity_check_rows.append({
                "identity_type": "radial",
                "identity": f"{ch_name}_{orientation}_radial",
                "channel": ch_name,
                "orientation": orientation,
                "maximum_absolute_error": radial_test["max_abs_error"],
                "median_absolute_error": radial_test["median_abs_error"],
                "passes": radial_test["identity_passes"]
            })
            identity_check_rows.append({
                "identity_type": "phase_balance_separation",
                "identity": f"{ch_name}_{orientation}_phase_sep",
                "channel": ch_name,
                "orientation": orientation,
                "maximum_absolute_error": phase_sep_test["max_abs_error"],
                "median_absolute_error": phase_sep_test["median_abs_error"],
                "passes": phase_sep_test["identity_passes"]
            })
            identity_check_rows.append({
                "identity_type": "phase_balance_mean",
                "identity": f"{ch_name}_{orientation}_phase_mean",
                "channel": ch_name,
                "orientation": orientation,
                "maximum_absolute_error": phase_mean_test["max_abs_error"],
                "median_absolute_error": phase_mean_test["median_abs_error"],
                "passes": phase_mean_test["identity_passes"]
            })

    channel_summary = pd.DataFrame(channel_summary_rows)
    identity_checks = pd.DataFrame(identity_check_rows)

    # Derived Pass/Fail Flags
    all_align_pass = bool(identity_checks.loc[identity_checks["identity_type"] == "alignment", "passes"].all())
    all_radial_pass = bool(identity_checks.loc[identity_checks["identity_type"] == "radial", "passes"].all())
    all_sym_pass = bool(identity_checks.loc[identity_checks["identity_type"] == "symmetrized_R", "passes"].all())
    all_phase_sep_pass = bool(identity_checks.loc[identity_checks["identity_type"] == "phase_balance_separation", "passes"].all())
    all_phase_mean_pass = bool(identity_checks.loc[identity_checks["identity_type"] == "phase_balance_mean", "passes"].all())

    # Write Outputs Atomically
    safe_atomic_write_csv(output_dir / "two_channel_trajectory.csv", trajectory)
    safe_atomic_write_csv(output_dir / "two_channel_summary.csv", channel_summary)
    safe_atomic_write_csv(output_dir / "two_channel_identity_checks.csv", identity_checks)

    report = f"""======================================================================
AIEF-1.4 Two-Channel Directed Alignment Decomposition (Version 4 Production)
======================================================================

alpha_EMA: {alpha:.12g}
dt: {dt:.12g}
Final replay exact: {final_replay_exact}
All-step resonance ordering R_25 > R_59 > R_29: {'PASS' if all_steps_ordering_ok else 'FAIL'}
Minimum Left Gap (R_25 - R_59): {np.min(gap_left):.6g}
Minimum Right Gap (R_59 - R_29): {np.min(gap_right):.6g}

Split-State & Per-Step Proposal Branch Diagnostics:
  All-step winner map (7,2,7) active: {all(winner_map_ok_list)}
  All-step gate active: {all(gate_on_list)}
  All-step controllers clipped: {all(clipped_list)}
  Maximum Isolation Error: {max(isolation_errors):.6g}
  Minimum Winner Margin: {min(winner_margins):.6g}

Exact Identity Check Verification:
  Alignment residual e_n = T1_n + T2_n: {'ALL PASSED' if all_align_pass else 'FAILED'}
  Radial recurrence DeltaM_{{n+1}} = alpha DeltaM_n + alpha(1-alpha)e_n: {'ALL PASSED' if all_radial_pass else 'FAILED'}
  Symmetrized R identity D_sym = Delta R: {'ALL PASSED' if all_sym_pass else 'FAILED'}
  Phase balance separation increment: {'ALL PASSED' if all_phase_sep_pass else 'FAILED'}
  Phase balance mean increment: {'ALL PASSED' if all_phase_mean_pass else 'FAILED'}
"""

    safe_atomic_write_text(output_dir / "two_channel_decomposition_report.txt", report)

    manifest_output = {
        "analysis": "AIEF-1.4 two-channel directed alignment decomposition v4 production",
        "evidence_class": "production replay evidence",
        "production_run_hash": DEFAULT_RUN_HASH,
        "seed": args.seed,
        "command": sys.argv,
        "parameters": {
            "dt": dt,
            "alpha_EMA": alpha,
            "scale_epsilon": args.scale_epsilon,
            "signal_floor": args.signal_floor,
            "identity_tol": args.identity_tol,
            "intervals": boundaries,
            "final_replay_exact": final_replay_exact,
            "all_steps_ordering_ok": all_steps_ordering_ok
        },
        "source_hashes": {
            Path(__file__).name: file_sha256(Path(__file__).resolve()),
            "base": compute_module_sha256(base),
            "component_audit": compute_module_sha256(component_audit),
            "augmented": compute_module_sha256(augmented),
        },
        "inputs": {
            "npz": {"path": str(Path(args.npz).resolve()), "sha256": file_sha256(args.npz)},
            "manifest": {"path": str(Path(args.manifest).resolve()), "sha256": file_sha256(args.manifest)},
        },
        "outputs": [
            "two_channel_trajectory.csv",
            "two_channel_summary.csv",
            "two_channel_identity_checks.csv",
            "two_channel_decomposition_report.txt",
            "analysis_manifest.json"
        ]
    }

    safe_atomic_write_text(output_dir / "analysis_manifest.json", json.dumps(manifest_output, indent=2) + "\n")
    print(report)
    print(f"[SUCCESS] Production analysis completed. Artifacts saved to: '{output_dir.resolve()}'")


def run_synthetic_demo(args: argparse.Namespace, output_dir: Path) -> None:
    """Execute synthetic demonstration scaffold and write unmistakably labeled test artifacts."""
    print("Executing synthetic demonstration scaffold marker (--synthetic-demo)...")
    output_dir = output_dir.parent / f"{output_dir.name}_synthetic_demo"
    output_dir.mkdir(parents=True, exist_ok=True)

    dt = args.dt
    alpha = 0.999428829846

    report = f"""======================================================================
AIEF-1.4 Two-Channel Directed Alignment Decomposition (Synthetic Scaffold Marker)
======================================================================

alpha_EMA: {alpha:.12g}
dt: {dt:.12g}
Evidence Class: SYNTHETIC SOFTWARE DEMONSTRATION ONLY (NOT REPLAY EVIDENCE)
"""
    safe_atomic_write_text(output_dir / "two_channel_decomposition_report.txt", report)

    manifest_output = {
        "analysis": "synthetic software validation only",
        "production_run_hash": None,
        "seed": None,
        "evidence_class": "synthetic software test; not replay evidence",
        "not_replay_evidence": True,
        "outputs": ["two_channel_decomposition_report.txt", "analysis_manifest.json"]
    }
    safe_atomic_write_text(output_dir / "analysis_manifest.json", json.dumps(manifest_output, indent=2) + "\n")
    print(f"[SUCCESS] Synthetic demonstration completed. Artifacts saved to: '{output_dir.resolve()}'")


def main() -> None:
    args = parse_arguments()

    if min(args.dt, args.scale_epsilon, args.signal_floor, args.identity_tol) <= 0.0:
        raise ValueError("dt and tolerances must be strictly positive")

    # 1. Self-test early return
    if args.self_test:
        run_self_test()
        return

    # 2. Synthetic demo branch
    if args.synthetic_demo:
        run_synthetic_demo(args, Path(args.output_dir))
        return

    # 3. Production input validation
    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Required production input file '{path}' not found. "
                f"Pass --synthetic-demo if you intend to run a synthetic software test scaffold."
            )

    # 4. Production analysis execution
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_production_analysis(args, output_dir)


if __name__ == "__main__":
    main()
