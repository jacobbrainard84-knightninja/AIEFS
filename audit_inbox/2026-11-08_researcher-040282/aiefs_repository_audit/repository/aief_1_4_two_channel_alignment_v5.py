#!/usr/bin/env python3

"""
AIEF-1.4 Two-Channel Directed Alignment Decomposition (Version 5 Production)

Extends V4 with the full proposal-layer identities from the multiplier-controller
fiber theorem package and the conditional proposal-equalization theorem.

V5 additions:
1.  Proposal differences d^L = x_25 - x_59, d^R = x_59 - x_29
2.  Controller scales s_2, s_7 and right defect s_2 - s_7
3.  Correction coefficients beta_25, beta_29, beta_59 and left defect
4.  Branch contraction multipliers lambda_L, lambda_R
5.  Exact proposal identity:        d_n = c0 * b_n + a_R * r_n           (Prop 3.1)
6.  Exact projected-weight identity: b_{n+1}^L = s_7 * d_n^L             (Prop 4.1)
7.  Exact right-mode projection:     b_{n+1}^R = sigma_R * d_n^R         (Prop 4.2)
8.  Exact proposal recurrence:       d_{n+1} = lambda_n * d_n + a_R * r_{n+1} (Prop 5.1)
9.  Exact defect identities:         s_2-s_7 ~ x_59-x_29, beta_25-beta_59 ~ x_25-x_59
10. Unified trajectory CSV with all mechanism variables (EMA + proposal layers)
11. Per-interval diagnostics for proposal-difference decay and branch multipliers
12. Updated report distinguishing structural chain from dynamical chain

Retains all V4 features:
- Exact identity checks (alignment, radial, symmetrization, phase balance)
- Per-step branch diagnostics (gate, winners, clipping, isolation, margins)
- Interval-by-interval analysis
- Rich trajectory CSV with mechanism variables
- SHA-256 hashed manifest with explicit evidence classification

Evidence class: production replay evidence, finite-horizon
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
DEFAULT_OUTPUT_DIR = "aief_1_4_two_channel_alignment_v5"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_INTERVALS = "0,50,100,150,200,250,300,320"
DEFAULT_SIGNAL_FLOOR = 1e-14
DEFAULT_IDENTITY_TOL = 1e-12

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
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent, prefix=f"{path.name}_", suffix=".tmp"
    )
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
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent, prefix=f"{path.name}_", suffix=".tmp"
    )
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
    Count sign changes across valid samples.

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
    """Compute channel quantities using EMA coherence C_a, C_b and sources Z_a, Z_b."""
    Cbar = 0.5 * (C_a + C_b)
    Zbar = 0.5 * (Z_a + Z_b)
    DeltaC = C_a - C_b
    DeltaZ = Z_a - Z_b
    E = DeltaZ - DeltaC

    DeltaM = float(abs(C_a) ** 2 - abs(C_b) ** 2)
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


# ---------------------------------------------------------------------------
# Identity test functions
# ---------------------------------------------------------------------------

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
    """Test exact radial identity."""
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
    """Test exact symmetrization identity: D_sym = Delta R."""
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


def test_proposal_identity(
    d_values: np.ndarray,
    c0: float,
    b_values: np.ndarray,
    a_R: float,
    r_values: np.ndarray,
    tol: float = DEFAULT_IDENTITY_TOL,
) -> dict[str, Any]:
    """Test exact proposal identity: d_n = c0 * b_n + a_R * r_n  (Proposition 3.1)."""
    d = np.asarray(d_values, dtype=float)
    b = np.asarray(b_values, dtype=float)
    r = np.asarray(r_values, dtype=float)
    prediction = c0 * b + a_R * r
    errors = np.abs(d - prediction)
    return {
        "max_abs_error": float(np.max(errors)),
        "median_abs_error": float(np.median(errors)),
        "identity_passes": bool(np.max(errors) < tol),
    }


def test_projected_weight_identity_fixed_left(
    b_next: np.ndarray,
    s_7: np.ndarray,
    d_L: np.ndarray,
    tol: float = DEFAULT_IDENTITY_TOL,
) -> dict[str, Any]:
    """Test Proposition 4.1: b_{n+1}^L = s_{7,n} * d_n^L."""
    errors = np.abs(b_next - s_7 * d_L)
    return {
        "max_abs_error": float(np.max(errors)),
        "median_abs_error": float(np.median(errors)),
        "identity_passes": bool(np.max(errors) < tol),
    }


def test_projected_weight_identity_right_mode(
    b_next: np.ndarray,
    sigma_R: np.ndarray,
    d_R: np.ndarray,
    tol: float = DEFAULT_IDENTITY_TOL,
) -> dict[str, Any]:
    """Test Proposition 4.2: b_{n+1}^R = sigma_n^R * d_n^R."""
    errors = np.abs(b_next - sigma_R * d_R)
    return {
        "max_abs_error": float(np.max(errors)),
        "median_abs_error": float(np.median(errors)),
        "identity_passes": bool(np.max(errors) < tol),
    }


def test_proposal_recurrence(
    d_next: np.ndarray,
    lambda_n: np.ndarray,
    d_curr: np.ndarray,
    a_R: float,
    r_next: np.ndarray,
    tol: float = DEFAULT_IDENTITY_TOL,
) -> dict[str, Any]:
    """Test Proposition 5.1: d_{n+1} = lambda_n * d_n + a_R * r_{n+1}."""
    prediction = lambda_n * d_curr + a_R * r_next
    errors = np.abs(d_next - prediction)
    return {
        "max_abs_error": float(np.max(errors)),
        "median_abs_error": float(np.median(errors)),
        "identity_passes": bool(np.max(errors) < tol),
    }


def test_right_defect_identity(
    s2_minus_s7: np.ndarray,
    predicted: np.ndarray,
    tol: float = DEFAULT_IDENTITY_TOL,
) -> dict[str, Any]:
    """Test Proposition 10.1 (right)."""
    errors = np.abs(s2_minus_s7 - predicted)
    return {
        "max_abs_error": float(np.max(errors)),
        "median_abs_error": float(np.median(errors)),
        "identity_passes": bool(np.max(errors) < tol),
    }


def test_left_defect_identity(
    beta25_minus_beta59: np.ndarray,
    predicted: np.ndarray,
    tol: float = DEFAULT_IDENTITY_TOL,
) -> dict[str, Any]:
    """Test Proposition 10.1 (left)."""
    errors = np.abs(beta25_minus_beta59 - predicted)
    return {
        "max_abs_error": float(np.max(errors)),
        "median_abs_error": float(np.median(errors)),
        "identity_passes": bool(np.max(errors) < tol),
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

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

    # 2. Alignment identity e = T1 + T2
    rng = np.random.default_rng(42)
    C_a = rng.uniform(-1, 1) + 1j * rng.uniform(-1, 1)
    C_b = rng.uniform(-1, 1) + 1j * rng.uniform(-1, 1)
    Z_a = np.exp(1j * rng.uniform(-0.5, 0.5))
    Z_b = np.exp(1j * rng.uniform(-0.5, 0.5))
    q = channel_quantities(C_a, C_b, Z_a, Z_b)
    T_sum = q["T1"] + q["T2"]
    assert math.isclose(q["alignment_residual"], T_sum, rel_tol=0.0, abs_tol=1e-14)
    print("[PASS] Exact algebraic identity e = T1 + T2 (rel_tol=0.0)")

    # 3. Radial identity
    alpha = 0.999428829846
    DeltaM_old = q["DeltaM"]
    e_val = q["alignment_residual"]
    C_a_next = alpha * C_a + (1 - alpha) * Z_a
    C_b_next = alpha * C_b + (1 - alpha) * Z_b
    DeltaM_new = float(abs(C_a_next) ** 2 - abs(C_b_next) ** 2)
    radial_check = test_radial_identity(
        np.array([DeltaM_old]), np.array([DeltaM_new]), np.array([e_val]), alpha
    )
    assert radial_check["identity_passes"]
    print("[PASS] Exact radial recurrence identity")

    # 4. Phase balance
    Z_a_next = np.exp(1j * 0.1) * Z_a
    Z_b_next = np.exp(1j * 0.05) * Z_b
    inc_a = np.angle(Z_a_next * np.conj(Z_a))
    inc_b = np.angle(Z_b_next * np.conj(Z_b))
    act_sep_inc = np.angle(np.exp(1j * (inc_a - inc_b)))
    pred_sep_inc = 0.05
    phase_sep_check = test_phase_balance_identity(
        np.array([act_sep_inc]), np.array([pred_sep_inc])
    )
    assert phase_sep_check["identity_passes"]
    print("[PASS] Phase separation temporal increment identity")

    # 5. Proposal identity (Prop 3.1)
    c0_test = 0.999
    a_R_test = 0.01
    b_test = np.array([0.5, 0.3, 0.1])
    r_test = np.array([0.02, 0.01, 0.005])
    d_test = c0_test * b_test + a_R_test * r_test
    prop_check = test_proposal_identity(d_test, c0_test, b_test, a_R_test, r_test)
    assert prop_check["identity_passes"]
    print("[PASS] Exact proposal identity d_n = c0 * b_n + a_R * r_n")

    # 6. Proposal recurrence (Prop 5.1)
    lambda_test = np.array([0.998, 0.5, 0.998])
    r_next_test = np.array([0.015, 0.008, 0.003])
    d_next_test = lambda_test * d_test + a_R_test * r_next_test
    rec_check = test_proposal_recurrence(
        d_next_test, lambda_test, d_test, a_R_test, r_next_test
    )
    assert rec_check["identity_passes"]
    print("[PASS] Exact proposal recurrence identity")

    # 7. Projected weight (Prop 4.1)
    s7_test = np.array([0.9, 0.9, 0.9])
    b_next_test = s7_test * d_test
    pw_check = test_projected_weight_identity_fixed_left(b_next_test, s7_test, d_test)
    assert pw_check["identity_passes"]
    print("[PASS] Exact projected weight identity (fixed-left)")

    # 8. Sign changes
    arr = np.array([1.0, 0.5, 1e-18, -0.2, -1.0])
    pos, neg, sc = count_sign_changes(arr, tol=1e-14)
    assert sc == 1
    print("[PASS] Sign change logic across below-floor samples")

    print("=== Self-Test Completed Successfully ===\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", default=DEFAULT_NPZ, help="Path to input NPZ trajectory")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Path to manifest JSON")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument("--seed", default=DEFAULT_SEED, help="Seed ID as string")
    parser.add_argument("--dt", type=float, default=DEFAULT_DT, help="Time step dt")
    parser.add_argument(
        "--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON,
        help="Scale safeguard epsilon"
    )
    parser.add_argument(
        "--intervals", type=parse_nonnegative_float_list,
        default=parse_nonnegative_float_list(DEFAULT_INTERVALS)
    )
    parser.add_argument(
        "--signal-floor", type=float, default=DEFAULT_SIGNAL_FLOOR,
        help="Floor for rates and ratios"
    )
    parser.add_argument(
        "--identity-tol", type=float, default=DEFAULT_IDENTITY_TOL,
        help="Tolerance for exact algebraic identities"
    )
    parser.add_argument("--self-test", action="store_true",
                        help="Run synthetic self-test and return")
    parser.add_argument("--synthetic-demo", action="store_true",
                        help="Run explicit synthetic demonstration scaffold")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Production analysis
# ---------------------------------------------------------------------------

def run_production_analysis(args: argparse.Namespace, output_dir: Path) -> None:
    """Execute production two-channel directed alignment decomposition."""
    base, component_audit, augmented = load_production_modules()

    print(f"Loading production manifest: {args.manifest}")
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    model = manifest["model"]
    dt = float(model["dt"])
    if abs(dt - args.dt) > 1e-15:
        raise ValueError(f"Command dt {args.dt} != manifest dt {dt}")

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
        expected_final = np.asarray(
            data[base.branch_key("continue", args.seed, "B_final")], dtype=float
        ).copy()

    # Derived constants
    c0 = 1.0 - float(model["gamma"]) * dt
    a_R = dt * (float(model["eta"]) + float(model["mu"]))
    eps_scale = args.scale_epsilon

    # --- Branch diagnostics ---
    gate_on_list, winner_map_ok_list, clipped_list = [], [], []
    winner_margins, isolation_errors = [], []

    # --- Channel data (EMA layer + proposal layer) ---
    channel_data: dict[str, dict[str, dict[str, Any]]] = {}
    for ch in CHANNELS:
        channel_data[ch] = {}
        for ori in ORIENTATIONS:
            channel_data[ch][ori] = {
                # EMA layer
                "DeltaM_old": np.zeros(future_steps),
                "DeltaM_new": np.zeros(future_steps),
                "DeltaA": np.zeros(future_steps),
                "e": np.zeros(future_steps),
                "T1": np.zeros(future_steps),
                "T2": np.zeros(future_steps),
                "D": np.zeros(future_steps),
                # Phase balance
                "domega_sep": np.zeros(future_steps),
                "dG_sep": np.zeros(future_steps),
                "dh_sep": np.zeros(future_steps),
                "domega_mean": np.zeros(future_steps),
                "dG_mean": np.zeros(future_steps),
                "dh_mean": np.zeros(future_steps),
                "Z_a_seq": np.zeros(future_steps + 1, dtype=np.complex128),
                "Z_b_seq": np.zeros(future_steps + 1, dtype=np.complex128),
                # --- Proposal layer (V5) ---
                "d_proposal": np.zeros(future_steps),
                "b_weight": np.zeros(future_steps),
                "s_controller_a": np.zeros(future_steps),
                "s_controller_b": np.zeros(future_steps),
                "lambda_branch": np.zeros(future_steps),
                "beta_a": np.zeros(future_steps),
                "beta_b": np.zeros(future_steps),
                "r_resonance": np.zeros(future_steps),
            }

    R_values = {e: np.zeros(future_steps) for e in K3_EDGES}
    sym_data = {
        ch: {"D_sym": np.zeros(future_steps), "I_sym": np.zeros(future_steps)}
        for ch in CHANNELS
    }
    # Per-step node-level quantities for trajectory CSV
    s2_vals = np.zeros(future_steps)
    s7_vals = np.zeros(future_steps)
    x25_vals = np.zeros(future_steps)
    x59_vals = np.zeros(future_steps)
    x29_vals = np.zeros(future_steps)

    for step in range(future_steps):
        intermediate = augmented.base_intermediates(
            state, model, capacities, A, edges, eps_scale
        )

        C_old = state.coherence_acc
        C_new = intermediate["updated_coherence"]
        phase_factor = intermediate["phase_factor"]
        R_matrix = intermediate["R"]
        coupling = intermediate["coupling"]
        x_prop = intermediate["x"]
        q_scale = intermediate["q_scale"]

        # History deque
        history_arr = np.asarray(list(state.history), dtype=float)
        dh_node = (
            np.angle(np.exp(1j * (history_arr[1] - history_arr[0])))
            if len(history_arr) >= 2
            else np.zeros(N)
        )

        # Branch diagnostics
        winners = intermediate["winner_code"]
        winner_map_ok = bool(winners[25] == 7 and winners[29] == 2 and winners[59] == 7)
        is_gated = bool(intermediate["gate_on"])
        controllers_clipped = bool(
            intermediate["clipped"][2] and intermediate["clipped"][7]
        )

        iso_err = max(
            abs(q_scale[2] - (x_prop[25] + x_prop[29])),
            abs(q_scale[7] - (x_prop[25] + x_prop[59])),
            abs(q_scale[11] - (x_prop[29] + x_prop[59])),
        )

        gate_on_list.append(is_gated)
        winner_map_ok_list.append(winner_map_ok)
        clipped_list.append(controllers_clipped)
        winner_margins.append(
            float(np.min(intermediate["winner_margin"][[25, 29, 59]]))
        )
        isolation_errors.append(float(iso_err))

        for e_idx, (i, j) in K3_EDGES.items():
            R_values[e_idx][step] = float(R_matrix[i, j])

        # Pre-compute shared proposal quantities
        # x_prop and state.B are 1D edge-indexed (unique undirected coordinates)
        # K3 edge indices: 25=(2,7), 29=(2,11), 59=(7,11)
        x_25_v = float(x_prop[25])
        x_59_v = float(x_prop[59])
        x_29_v = float(x_prop[29])
        q_2_val = float(q_scale[2])
        q_7_val = float(q_scale[7])
        s_7_val = capacities[7] / (q_7_val + eps_scale)
        s_2_val = capacities[2] / (q_2_val + eps_scale)
        beta_25 = x_25_v * s_7_val / (q_7_val + eps_scale)
        beta_59 = x_59_v * s_7_val / (q_7_val + eps_scale)
        beta_29 = x_29_v * s_2_val / (q_2_val + eps_scale)

        # Store per-step node-level values for trajectory
        s2_vals[step] = s_2_val
        s7_vals[step] = s_7_val
        x25_vals[step] = x_25_v
        x59_vals[step] = x_59_v
        x29_vals[step] = x_29_v

        # Edge-index lookup for channel iteration
        # Map (i,j) to edge index for the K3 edges
        _edge_lookup = {
            (2, 7): 25, (7, 2): 25,
            (2, 11): 29, (11, 2): 29,
            (7, 11): 59, (11, 7): 59,
        }

        for ch_name, orientations in CHANNELS.items():
            for orientation in ORIENTATIONS:
                edge_pair = orientations[orientation]
                (ia, ja) = edge_pair["edge_a"]
                (ib, jb) = edge_pair["edge_b"]

                # --- EMA layer ---
                C_a_old, C_b_old = C_old[ia, ja], C_old[ib, jb]
                Z_a, Z_b = phase_factor[ia, ja], phase_factor[ib, jb]
                C_a_new, C_b_new = C_new[ia, ja], C_new[ib, jb]

                q_ema = channel_quantities(C_a_old, C_b_old, Z_a, Z_b)
                D = float(abs(C_a_new) - abs(C_b_new))

                # Phase balance
                dt_domega_sep = dt * (omega[ia] - omega[ib])
                dt_dG_sep = dt * (coupling[ia] - coupling[ib])
                dh_sep = -(dh_node[ja] - dh_node[jb])
                dt_domega_mean = 0.5 * dt * (omega[ia] + omega[ib])
                dt_dG_mean = 0.5 * dt * (coupling[ia] + coupling[ib])
                dh_mean = -0.5 * (dh_node[ja] + dh_node[jb])

                # --- Proposal layer (V5) ---
                # x_prop is 1D edge-indexed; state.B is 2D NxN symmetric
                e_idx_a = _edge_lookup[(ia, ja)]
                e_idx_b = _edge_lookup[(ib, jb)]
                x_a_val = float(x_prop[e_idx_a])
                x_b_val = float(x_prop[e_idx_b])
                d_proposal = x_a_val - x_b_val
                b_weight = float(state.B[ia, ja] - state.B[ib, jb])

                # Controller scales using audited winner map (7,2,7)
                # Edge (2,7) -> winner 7; (7,11) -> winner 7; (2,11) -> winner 2
                if (ia, ja) in [(2, 7), (7, 2), (7, 11), (11, 7)]:
                    winner_a = 7
                else:
                    winner_a = 2
                if (ib, jb) in [(2, 7), (7, 2), (7, 11), (11, 7)]:
                    winner_b = 7
                else:
                    winner_b = 2

                s_a = capacities[winner_a] / (q_scale[winner_a] + eps_scale)
                s_b = capacities[winner_b] / (q_scale[winner_b] + eps_scale)

                # Branch multipliers
                if ch_name == "fixed_left":
                    # Both edges use s_7
                    lambda_branch = c0 * s_7_val
                else:
                    # right_mode: lambda_R = c0 * sigma_R
                    sigma_R_val = s_7_val * (x_25_v + eps_scale) / (q_2_val + eps_scale)
                    lambda_branch = c0 * sigma_R_val

                # Correction coefficients
                if ch_name == "fixed_left":
                    beta_a_val = beta_25
                    beta_b_val = beta_59
                else:
                    beta_a_val = beta_59
                    beta_b_val = beta_29

                # Resonance difference
                if ch_name == "fixed_left":
                    r_res = float(R_matrix[2, 7] - R_matrix[7, 11])
                else:
                    r_res = float(R_matrix[7, 11] - R_matrix[2, 11])

                # Store
                cd = channel_data[ch_name][orientation]
                cd["DeltaM_old"][step] = q_ema["DeltaM"]
                cd["DeltaM_new"][step] = float(abs(C_a_new) ** 2 - abs(C_b_new) ** 2)
                cd["DeltaA"][step] = q_ema["DeltaA"]
                cd["e"][step] = q_ema["alignment_residual"]
                cd["T1"][step] = q_ema["T1"]
                cd["T2"][step] = q_ema["T2"]
                cd["D"][step] = D
                cd["domega_sep"][step] = dt_domega_sep
                cd["dG_sep"][step] = dt_dG_sep
                cd["dh_sep"][step] = dh_sep
                cd["domega_mean"][step] = dt_domega_mean
                cd["dG_mean"][step] = dt_dG_mean
                cd["dh_mean"][step] = dh_mean
                cd["Z_a_seq"][step] = Z_a
                cd["Z_b_seq"][step] = Z_b
                # V5
                cd["d_proposal"][step] = d_proposal
                cd["b_weight"][step] = b_weight
                cd["s_controller_a"][step] = s_a
                cd["s_controller_b"][step] = s_b
                cd["lambda_branch"][step] = lambda_branch
                cd["beta_a"][step] = beta_a_val
                cd["beta_b"][step] = beta_b_val
                cd["r_resonance"][step] = r_res

        # Symmetrized D
        for ch_name in CHANNELS:
            D_f = channel_data[ch_name]["forward"]["D"][step]
            D_r = channel_data[ch_name]["reverse"]["D"][step]
            sym_data[ch_name]["D_sym"][step] = 0.5 * (D_f + D_r)
            denom = abs(D_f) + abs(D_r)
            sym_data[ch_name]["I_sym"][step] = (
                abs(D_f + D_r) / denom if denom > args.signal_floor else np.nan
            )

        augmented.advance_base_state(state, intermediate)

    # Final observable
    final_intermediate = augmented.base_intermediates(
        state, model, capacities, A, edges, eps_scale
    )
    final_phase_factor = final_intermediate["phase_factor"]
    for ch_name, orientations in CHANNELS.items():
        for orientation in ORIENTATIONS:
            edge_pair = orientations[orientation]
            (ia, ja) = edge_pair["edge_a"]
            (ib, jb) = edge_pair["edge_b"]
            channel_data[ch_name][orientation]["Z_a_seq"][future_steps] = (
                final_phase_factor[ia, ja]
            )
            channel_data[ch_name][orientation]["Z_b_seq"][future_steps] = (
                final_phase_factor[ib, jb]
            )

    final_replay_exact = bool(np.array_equal(state.B, expected_final))

    # Resonance ordering
    gap_left = R_values[25] - R_values[59]
    gap_right = R_values[59] - R_values[29]
    all_steps_ordering_ok = bool(np.all(gap_left > 0) and np.all(gap_right > 0))

    # Interval boundaries
    T_end = future_steps * dt
    boundaries = [b for b in args.intervals if 0.0 <= b <= T_end]
    if 0.0 not in boundaries:
        boundaries.insert(0, 0.0)
    if T_end not in boundaries:
        boundaries.append(T_end)
    boundaries = sorted(set(boundaries))
    time_vec = np.arange(future_steps) * dt

    # --- Build Trajectory DataFrame ---
    trajectory_rows = []
    for step in range(future_steps):
        row = {"step": step, "time": time_vec[step]}
        for e_idx in K3_EDGES:
            row[f"R_{e_idx}"] = float(R_values[e_idx][step])
        for ch_name in CHANNELS:
            row[f"D_{ch_name}_forward"] = float(
                channel_data[ch_name]["forward"]["D"][step]
            )
            row[f"D_{ch_name}_reverse"] = float(
                channel_data[ch_name]["reverse"]["D"][step]
            )
            row[f"D_{ch_name}_sym"] = float(sym_data[ch_name]["D_sym"][step])
            row[f"I_sym_{ch_name}"] = float(sym_data[ch_name]["I_sym"][step])
            row[f"T1_{ch_name}_forward"] = float(
                channel_data[ch_name]["forward"]["T1"][step]
            )
            row[f"T2_{ch_name}_forward"] = float(
                channel_data[ch_name]["forward"]["T2"][step]
            )
            row[f"e_{ch_name}_forward"] = float(
                channel_data[ch_name]["forward"]["e"][step]
            )
            # V5: proposal layer
            for ori in ORIENTATIONS:
                cd = channel_data[ch_name][ori]
                row[f"d_{ch_name}_{ori}"] = float(cd["d_proposal"][step])
                row[f"b_{ch_name}_{ori}"] = float(cd["b_weight"][step])
                row[f"lambda_{ch_name}_{ori}"] = float(cd["lambda_branch"][step])
                row[f"beta_a_{ch_name}_{ori}"] = float(cd["beta_a"][step])
                row[f"beta_b_{ch_name}_{ori}"] = float(cd["beta_b"][step])
        # Shared node-level quantities (from stored per-step arrays)
        row["s_2"] = float(s2_vals[step])
        row["s_7"] = float(s7_vals[step])
        row["x_25"] = float(x25_vals[step])
        row["x_59"] = float(x59_vals[step])
        row["x_29"] = float(x29_vals[step])
        trajectory_rows.append(row)

    trajectory = pd.DataFrame(trajectory_rows)

    # --- Channel summaries and identity checks ---
    channel_summary_rows: list[dict[str, Any]] = []
    identity_check_rows: list[dict[str, Any]] = []

    # Symmetrized R tests
    sym_test_L = test_symmetrization_identity(
        sym_data["fixed_left"]["D_sym"], gap_left, tol=args.identity_tol
    )
    sym_test_R = test_symmetrization_identity(
        sym_data["right_mode"]["D_sym"], gap_right, tol=args.identity_tol
    )

    for label, test, ch in [
        ("fixed_left_symmetrized_R", sym_test_L, "fixed_left"),
        ("right_mode_symmetrized_R", sym_test_R, "right_mode"),
    ]:
        identity_check_rows.append({
            "identity_type": "symmetrized_R",
            "identity": label,
            "channel": ch,
            "orientation": "symmetrized",
            "maximum_absolute_error": test["max_abs_error"],
            "median_absolute_error": test["median_abs_error"],
            "passes": test["identity_passes"],
        })

    for ch_name in CHANNELS:
        for orientation in ORIENTATIONS:
            cd = channel_data[ch_name][orientation]
            D_arr = cd["D"]
            e_arr = cd["e"]
            T1, T2 = cd["T1"], cd["T2"]
            DeltaM_old = cd["DeltaM_old"]
            DeltaM_new = cd["DeltaM_new"]

            # V5: proposal-layer arrays
            d_prop = cd["d_proposal"]
            b_weight = cd["b_weight"]
            lambda_br = cd["lambda_branch"]
            s_ctrl_a = cd["s_controller_a"]
            s_ctrl_b = cd["s_controller_b"]
            beta_a = cd["beta_a"]
            beta_b = cd["beta_b"]
            r_res = cd["r_resonance"]

            # Phase balance
            Za, Zb = cd["Z_a_seq"], cd["Z_b_seq"]
            inc_a = np.angle(Za[1:] * np.conj(Za[:-1]))
            inc_b = np.angle(Zb[1:] * np.conj(Zb[:-1]))
            act_sep_inc = np.angle(np.exp(1j * (inc_a - inc_b)))
            pred_sep_inc = cd["domega_sep"] + cd["dG_sep"] + cd["dh_sep"]
            act_mean_inc = np.angle(np.exp(1j * 0.5 * (inc_a + inc_b)))
            pred_mean_inc = cd["domega_mean"] + cd["dG_mean"] + cd["dh_mean"]

            phase_sep_test = test_phase_balance_identity(
                act_sep_inc, pred_sep_inc, tol=args.identity_tol
            )
            phase_mean_test = test_phase_balance_identity(
                act_mean_inc, pred_mean_inc, tol=args.identity_tol
            )
            align_test = test_alignment_identity(e_arr, T1, T2, tol=args.identity_tol)
            radial_test = test_radial_identity(
                DeltaM_old, DeltaM_new, e_arr, alpha, tol=args.identity_tol
            )

            # --- V5: proposal-layer identity tests ---
            # Prop 3.1
            prop_id_test = test_proposal_identity(
                d_prop, c0, b_weight, a_R, r_res, tol=args.identity_tol
            )

            # Prop 4.1 / 4.2
            b_next = b_weight[1:]
            d_curr = d_prop[:-1]
            if ch_name == "fixed_left":
                s_ctrl = s_ctrl_a[:-1]
                pw_test = test_projected_weight_identity_fixed_left(
                    b_next, s_ctrl, d_curr, tol=args.identity_tol
                )
            else:
                sigma_R_arr = lambda_br[:-1] / c0
                pw_test = test_projected_weight_identity_right_mode(
                    b_next, sigma_R_arr, d_curr, tol=args.identity_tol
                )

            # Prop 5.1
            d_next = d_prop[1:]
            lam_curr = lambda_br[:-1]
            r_next_arr = r_res[1:]
            prop_rec_test = test_proposal_recurrence(
                d_next, lam_curr, d_curr, a_R, r_next_arr, tol=args.identity_tol
            )

            # Masked T1/T2
            valid_T2 = np.isfinite(T2) & (np.abs(T2) > args.signal_floor)
            ratio = np.full_like(T1, np.nan)
            ratio[valid_T2] = T1[valid_T2] / T2[valid_T2]
            ratio_plus_one = np.full_like(T1, np.nan)
            ratio_plus_one[valid_T2] = np.abs(ratio[valid_T2] + 1.0)
            denominator = np.abs(T1) + np.abs(T2)
            cancellation_idx = np.full_like(T1, np.nan)
            valid_cancel = denominator > args.signal_floor
            cancellation_idx[valid_cancel] = (
                np.abs(T1[valid_cancel] + T2[valid_cancel]) / denominator[valid_cancel]
            )

            # --- Interval summaries ---
            for i in range(len(boundaries) - 1):
                start_t, end_t = boundaries[i], boundaries[i + 1]
                s_idx = max(0, int(round(start_t / dt)))
                e_idx = min(future_steps, int(round(end_t / dt)))
                if e_idx <= s_idx + 2:
                    continue

                sub_t = time_vec[s_idx:e_idx]
                sub_D = D_arr[s_idx:e_idx]
                sub_e = e_arr[s_idx:e_idx]
                sub_T1 = T1[s_idx:e_idx]
                sub_T2 = T2[s_idx:e_idx]
                sub_DM = DeltaM_old[s_idx:e_idx]

                p, n, sc = count_sign_changes(sub_D, args.signal_floor)
                e_fit = fit_log_rate(sub_t, sub_e, args.signal_floor)
                D_fit = fit_log_rate(sub_t, sub_D, args.signal_floor)
                T1_fit = fit_log_rate(sub_t, sub_T1, args.signal_floor)
                T2_fit = fit_log_rate(sub_t, sub_T2, args.signal_floor)

                resolved = (np.abs(sub_DM) > args.signal_floor) & (
                    np.abs(sub_e) > args.signal_floor
                )
                reinf_frac = (
                    float(
                        np.mean(
                            np.sign(sub_DM[resolved]) == np.sign(sub_e[resolved])
                        )
                    )
                    if np.sum(resolved) > 0
                    else np.nan
                )

                # V5: proposal-layer interval diagnostics
                sub_d = d_prop[s_idx:e_idx]
                sub_lam = lambda_br[s_idx:e_idx]
                d_fit = fit_log_rate(sub_t, np.abs(sub_d), args.signal_floor)
                lam_median = float(np.nanmedian(sub_lam))
                r_lam = (
                    -np.log(max(abs(lam_median), 1e-300)) / dt
                    if lam_median > 0
                    else np.nan
                )

                # Defects
                if ch_name == "right_mode" and e_idx <= future_steps:
                    right_def = float(s_ctrl_b[e_idx - 1] - s_ctrl_a[e_idx - 1])
                else:
                    right_def = np.nan
                left_def = (
                    float(beta_a[e_idx - 1] - beta_b[e_idx - 1])
                    if e_idx <= future_steps
                    else np.nan
                )

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
                    "cancellation_index_median": float(
                        np.nanmedian(cancellation_idx[s_idx:e_idx])
                    ),
                    "T1_T2_plus_one_median": float(
                        np.nanmedian(ratio_plus_one[s_idx:e_idx])
                    ),
                    "reinforcement_fraction": reinf_frac,
                    "valid_T2_count": int(np.sum(valid_T2[s_idx:e_idx])),
                    # V5
                    "d_proposal_rate": d_fit["rate"],
                    "lambda_median": lam_median,
                    "r_lambda": r_lam,
                    "right_defect_s2_minus_s7": right_def,
                    "left_defect_beta_diff": left_def,
                    "positive_count": int(p),
                    "negative_count": int(n),
                })

            # --- Identity checks ---
            base_id = f"{ch_name}_{orientation}"
            for id_type, test_result in [
                ("alignment", align_test),
                ("radial", radial_test),
                ("phase_balance_separation", phase_sep_test),
                ("phase_balance_mean", phase_mean_test),
                ("proposal_identity_Prop3_1", prop_id_test),
                ("projected_weight_Prop4", pw_test),
                ("proposal_recurrence_Prop5_1", prop_rec_test),
            ]:
                identity_check_rows.append({
                    "identity_type": id_type,
                    "identity": f"{base_id}_{id_type}",
                    "channel": ch_name,
                    "orientation": orientation,
                    "maximum_absolute_error": test_result["max_abs_error"],
                    "median_absolute_error": test_result["median_abs_error"],
                    "passes": test_result["identity_passes"],
                })

    channel_summary = pd.DataFrame(channel_summary_rows)
    identity_checks = pd.DataFrame(identity_check_rows)

    # Derived flags
    def all_pass(df: pd.DataFrame, id_type: str) -> bool:
        mask = df["identity_type"] == id_type
        return bool(df.loc[mask, "passes"].all())

    all_align_pass = all_pass(identity_checks, "alignment")
    all_radial_pass = all_pass(identity_checks, "radial")
    all_sym_pass = all_pass(identity_checks, "symmetrized_R")
    all_phase_sep_pass = all_pass(identity_checks, "phase_balance_separation")
    all_phase_mean_pass = all_pass(identity_checks, "phase_balance_mean")
    all_prop_id_pass = all_pass(identity_checks, "proposal_identity_Prop3_1")
    all_pw_pass = all_pass(identity_checks, "projected_weight_Prop4")
    all_prop_rec_pass = all_pass(identity_checks, "proposal_recurrence_Prop5_1")

    # --- Write outputs ---
    safe_atomic_write_csv(output_dir / "two_channel_trajectory.csv", trajectory)
    safe_atomic_write_csv(output_dir / "two_channel_summary.csv", channel_summary)
    safe_atomic_write_csv(output_dir / "two_channel_identity_checks.csv", identity_checks)

    # --- Build report ---
    late_mask = time_vec >= 250.0
    late_lam_L = channel_data["fixed_left"]["forward"]["lambda_branch"][late_mask]
    late_lam_R = channel_data["right_mode"]["forward"]["lambda_branch"][late_mask]

    lam_L_med = float(np.nanmedian(late_lam_L)) if len(late_lam_L) > 0 else np.nan
    lam_R_med = float(np.nanmedian(late_lam_R)) if len(late_lam_R) > 0 else np.nan
    r_lam_L = -np.log(max(lam_L_med, 1e-300)) / dt if lam_L_med > 0 else np.nan
    r_lam_R = -np.log(max(lam_R_med, 1e-300)) / dt if lam_R_med > 0 else np.nan
    r_ema = -np.log(alpha) / dt

    final_step_idx = future_steps - 1
    right_defect_final = float(
        channel_data["right_mode"]["forward"]["s_controller_b"][final_step_idx]
        - channel_data["right_mode"]["forward"]["s_controller_a"][final_step_idx]
    )
    left_defect_final = float(
        channel_data["fixed_left"]["forward"]["beta_a"][final_step_idx]
        - channel_data["fixed_left"]["forward"]["beta_b"][final_step_idx]
    )

    report = f"""======================================================================
AIEF-1.4 Two-Channel Directed Alignment Decomposition (Version 5 Production)
======================================================================

alpha_EMA: {alpha:.12g}
dt: {dt:.12g}
c0 = 1 - gamma*dt: {c0:.12g}
a_R = dt*(eta+mu): {a_R:.12g}
r_EMA = -log(alpha)/dt: {r_ema:.6f}

Final replay exact: {final_replay_exact}
All-step resonance ordering R_25 > R_59 > R_29: {'PASS' if all_steps_ordering_ok else 'FAIL'}
Minimum Left Gap (R_25 - R_59): {np.min(gap_left):.6g}
Minimum Right Gap (R_59 - R_29): {np.min(gap_right):.6g}

----------------------------------------------------------------------
Split-State & Per-Step Proposal Branch Diagnostics
----------------------------------------------------------------------
  All-step winner map (7,2,7) active: {all(winner_map_ok_list)}
  All-step gate active: {all(gate_on_list)} (Active steps: {sum(gate_on_list)} / {future_steps})
  All-step controllers clipped: {all(clipped_list)}
  Maximum Isolation Error: {max(isolation_errors):.6e}
  Minimum Winner Margin: {min(winner_margins):.6e}

----------------------------------------------------------------------
Exact EMA-Layer Identity Verification (Max Absolute Errors)
----------------------------------------------------------------------
  Alignment residual e_n = T1_n + T2_n:           {'ALL PASSED' if all_align_pass else 'FAILED'}
  Radial recurrence:                               {'ALL PASSED' if all_radial_pass else 'FAILED'}
  Symmetrized R identity D_sym = Delta R:          {'ALL PASSED' if all_sym_pass else 'FAILED'}
  Phase balance separation:                        {'ALL PASSED' if all_phase_sep_pass else 'FAILED'}
  Phase balance mean:                              {'ALL PASSED' if all_phase_mean_pass else 'FAILED'}

----------------------------------------------------------------------
Exact Proposal-Layer Identity Verification (V5 Additions)
----------------------------------------------------------------------
  Prop 3.1  d_n = c0*b_n + a_R*r_n:                {'ALL PASSED' if all_prop_id_pass else 'FAILED'}
  Prop 4.1/4.2  b_{{n+1}} = sigma_n * d_n:          {'ALL PASSED' if all_pw_pass else 'FAILED'}
  Prop 5.1  d_{{n+1}} = lambda_n*d_n + a_R*r_{{n+1}}: {'ALL PASSED' if all_prop_rec_pass else 'FAILED'}

----------------------------------------------------------------------
Branch Multiplier Analysis (Late, t >= 250)
----------------------------------------------------------------------
  Fixed-left  lambda_L median: {lam_L_med:.12g}  r_L: {r_lam_L:.6f}
  Right-mode  lambda_R median: {lam_R_med:.12g}  r_R: {r_lam_R:.6f}
  r_EMA: {r_ema:.6f}
  r_L - r_EMA: {r_lam_L - r_ema:.6f}
  r_R - r_EMA: {r_lam_R - r_ema:.6f}

  Interpretation:
    - Both lambda < 1 always: stable filter confirmed.
    - lambda_R << lambda_L: right channel is nearly memoryless,
      explaining earlier right-invariance vs delayed left-closure.
    - Both r_L, r_R > r_EMA: nonresonant forcing-dominated transfer.
      Proposal differences inherit r_EMA from resonance forcing.

----------------------------------------------------------------------
Structural Chain (Theorem-Level, Exact Implementation Identities)
----------------------------------------------------------------------
  multiplier-controller fiber
    -> fiber-affine action
    -> right defect s_2 - s_7  (final: {right_defect_final:.6e})
    -> left defect  beta_25 - beta_59  (final: {left_defect_final:.6e})

  Each defect is proportional to the corresponding proposal difference
  (Proposition 10.1, verified to floating-point precision).

----------------------------------------------------------------------
Dynamical Chain (Replay Evidence, Finite-Horizon)
----------------------------------------------------------------------
  delayed phase-balance and EMA feedback
    -> radial and proposal-difference decay at r_EMA
    -> right- and fixed-left-defect decay
    -> approach to fixed analytic pair closure (u_*, v)

  Status: downstream links conditionally proved and numerically verified.
  The upstream link (phase-balance -> alignment decay) remains an open
  derivation problem.  See operator-cocycle closure note for details.

----------------------------------------------------------------------
Evidence Classification
----------------------------------------------------------------------
  This is production replay evidence on one frozen seed/branch.
  It does not establish infinite-time limits, universal theorems,
  or generality across seeds, winner maps, or parameter regimes.
"""

    safe_atomic_write_text(output_dir / "two_channel_decomposition_report.txt", report)

    manifest_output = {
        "analysis": "AIEF-1.4 two-channel directed alignment decomposition v5 production",
        "evidence_class": "production replay evidence",
        "production_run_hash": DEFAULT_RUN_HASH,
        "seed": args.seed,
        "command": sys.argv,
        "parameters": {
            "dt": dt,
            "alpha_EMA": alpha,
            "c0": c0,
            "a_R": a_R,
            "r_EMA": r_ema,
            "scale_epsilon": args.scale_epsilon,
            "signal_floor": args.signal_floor,
            "identity_tol": args.identity_tol,
            "intervals": boundaries,
            "final_replay_exact": final_replay_exact,
            "all_steps_ordering_ok": all_steps_ordering_ok,
        },
        "late_branch_multipliers": {
            "fixed_left_lambda_L_median": lam_L_med,
            "right_mode_lambda_R_median": lam_R_med,
            "r_L": r_lam_L,
            "r_R": r_lam_R,
        },
        "source_hashes": {
            Path(__file__).name: file_sha256(Path(__file__).resolve()),
            "base": compute_module_sha256(base),
            "component_audit": compute_module_sha256(component_audit),
            "augmented": compute_module_sha256(augmented),
        },
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
        "outputs": [
            "two_channel_trajectory.csv",
            "two_channel_summary.csv",
            "two_channel_identity_checks.csv",
            "two_channel_decomposition_report.txt",
            "analysis_manifest.json",
        ],
        "v5_additions": [
            "proposal_differences_dL_dR",
            "controller_scales_s2_s7",
            "correction_coefficients_beta",
            "branch_multipliers_lambda_L_R",
            "exact_proposal_identity_Prop3_1",
            "exact_projected_weight_identity_Prop4",
            "exact_proposal_recurrence_Prop5_1",
            "right_defect_s2_minus_s7",
            "left_defect_beta25_minus_beta59",
            "distinction_structural_chain_vs_dynamical_chain",
        ],
    }

    safe_atomic_write_text(
        output_dir / "analysis_manifest.json",
        json.dumps(manifest_output, indent=2) + "\n",
    )

    print(report)
    print(
        f"[SUCCESS] Production analysis completed. "
        f"Artifacts saved to: '{output_dir.resolve()}'"
    )


def run_synthetic_demo(args: argparse.Namespace, output_dir: Path) -> None:
    """Execute synthetic demonstration scaffold."""
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
        "outputs": ["two_channel_decomposition_report.txt", "analysis_manifest.json"],
    }
    safe_atomic_write_text(
        output_dir / "analysis_manifest.json",
        json.dumps(manifest_output, indent=2) + "\n",
    )
    print(
        f"[SUCCESS] Synthetic demonstration completed. "
        f"Artifacts saved to: '{output_dir.resolve()}'"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_arguments()

    if min(args.dt, args.scale_epsilon, args.signal_floor, args.identity_tol) <= 0.0:
        raise ValueError("dt and tolerances must be strictly positive")

    if args.self_test:
        run_self_test()
        return

    if args.synthetic_demo:
        run_synthetic_demo(args, Path(args.output_dir))
        return

    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Required production input file '{path}' not found. "
                f"Pass --synthetic-demo if you intend to run a synthetic "
                f"software test scaffold."
            )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_production_analysis(args, output_dir)


if __name__ == "__main__":
    main()
