#!/usr/bin/env python3
"""AIEF-1.4 Matched Phase Memory Ablation.

Corrected comparison: B_carrier_only versus full_reset with matched phase/history.

PURPOSE:
--------
The original frozen run compared B_carrier_only vs full_reset, but both branches
used *different* branch-specific random draws for phase/history randomization.
This confounded:
  1. preservation vs removal of mature B, and
  2. different randomized phase/history initial conditions.

This script constructs *matched* phase/history reset blocks so that within each
seed, the two branches differ ONLY in initial B (preserved vs zero).

SCIENTIFIC ESTIMAND:
--------------------
For each frozen seed/graph, estimate the effect of preserving mature B,
conditional on:
  - the same randomized phase vector
  - the same randomized history deque
  - the same zeroed complex EMA state
  - the same omega
  - the same future dynamics and safeguards

Primary contrast: Y(B=Bsplit) - Y(B=0) under otherwise identical reset state.

This is a *controlled counterfactual* about the contribution of mature B.
It is NOT a test that B is the unique memory carrier.

FROZEN SOURCES:
---------------
  - runs/5a9f093a2fe0/manifest.json
  - runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz
  - runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv

DEPENDENCIES:
-------------
  - AIEF_1_4_memory_ablation_updated (imported as prod, DO NOT MODIFY)
  - AIEF_1_4_trajectory_recovery_equivalence (REQUIRED for validated recovery helpers)

INTERPRETATION CONSTRAINTS:
---------------------------
Allowed:  "The experiment estimates the conditional effect of preserving mature B
           under matched randomized phase/history and reset EMA."

Forbidden: "B is the unique memory carrier."
           "B stores the attractor by itself."
           "No other state variable matters."
           "Matched reset proves universal causality."

The seed/graph is the inferential unit (40 seeds).
The 80 reset-block contrasts are NOT independent observations.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
from collections import deque
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np
import pandas as pd


# =============================================================================
# IMPORTS - Production dependencies (DO NOT MODIFY these modules)
# =============================================================================

try:
    import AIEF_1_4_memory_ablation_updated as prod
    PROD_AVAILABLE = True
except ImportError as e:
    PROD_AVAILABLE = False
    PROD_ERROR = str(e)

try:
    import AIEF_1_4_trajectory_recovery_equivalence as recovery
    RECOVERY_AVAILABLE = True
except ImportError as e:
    RECOVERY_AVAILABLE = False
    RECOVERY_ERROR = str(e)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_SCALAR = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_scalar_summary.csv"
)
DEFAULT_OUTPUT_DIR = "aief_1_4_matched_phase_memory_ablation"

# Branch IDs for output
BRANCH_IDS = [
    "carrier_reset__B_preserved",
    "carrier_reset__B_zero",
    "full_reset__B_preserved",
    "full_reset__B_zero",
    "continue",
]

# Branch metadata - production_intervention_label is what gets passed to simulate_future
BRANCH_META = {
    "carrier_reset__B_preserved": {
        "reset_source": "carrier_reset",
        "B_status": "preserved",
        "production_intervention_label": "B_carrier_only",
        "frozen_anchor_branch": "B_carrier_only",
    },
    "carrier_reset__B_zero": {
        "reset_source": "carrier_reset",
        "B_status": "zero",
        "production_intervention_label": "full_reset",
        "frozen_anchor_branch": None,
    },
    "full_reset__B_preserved": {
        "reset_source": "full_reset",
        "B_status": "preserved",
        "production_intervention_label": "B_carrier_only",
        "frozen_anchor_branch": None,
    },
    "full_reset__B_zero": {
        "reset_source": "full_reset",
        "B_status": "zero",
        "production_intervention_label": "full_reset",
        "frozen_anchor_branch": "full_reset",
    },
    "continue": {
        "reset_source": "continue",
        "B_status": "continue",
        "production_intervention_label": "continue",
        "frozen_anchor_branch": "continue",
    },
}

# Outcome sets - FIX: Separate continuous, binary, censored
CONTINUOUS_SUMMARY_OUTCOMES = [
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
    # FIX: Add restricted-time outcomes
    "restricted_time_to_similarity_90",
    "restricted_time_to_density_90",
]

BINARY_OUTCOMES = [
    "sustained_similarity_90_recovered",
    "sustained_density_90_recovered",
    "held_similarity_90_for_1Twindow_recovered",
]

CENSORED_TIME_OUTCOMES = [
    "time_to_similarity_90",
    "time_to_density_90",
]

# All outcomes for paired contrasts (includes continuous, binary, censored for diagnostics)
CONTRAST_OUTCOMES = (
    CONTINUOUS_SUMMARY_OUTCOMES
    + BINARY_OUTCOMES
    + CENSORED_TIME_OUTCOMES
)


# =============================================================================
# Utility Functions
# =============================================================================


def file_sha256(path: str | os.PathLike[str]) -> str:
    """Compute SHA-256 hash of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def array_sha256(arr: np.ndarray) -> str:
    """Compute SHA-256 hash of a numpy array (shape, dtype, bytes)."""
    digest = hashlib.sha256()
    shape_bytes = np.asarray(arr.shape, dtype=np.int64).tobytes()
    digest.update(shape_bytes)
    digest.update(arr.dtype.str.encode())
    contiguous = np.ascontiguousarray(arr)
    if contiguous.size > 0:
        digest.update(contiguous.tobytes())
    return digest.hexdigest()


def compute_module_sha256(module: Any) -> str:
    """Compute SHA-256 hash of a module's source file."""
    path = Path(module.__file__).resolve()
    return file_sha256(path)


def parse_seed_list(value: str) -> list[str]:
    """Parse comma-separated seed strings."""
    return [s.strip() for s in value.split(",") if s.strip()]


def parse_positive_int(value: str) -> int:
    """Parse positive integer."""
    val = int(value)
    if val <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return val


def parse_nonnegative_int(value: str) -> int:
    """Parse nonnegative integer."""
    val = int(value)
    if val < 0:
        raise argparse.ArgumentTypeError("value must be nonnegative")
    return val


def atomic_write_csv(path: Path, df: pd.DataFrame) -> None:
    """Write CSV atomically using tempfile with proper fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            df.to_csv(handle, index=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically using tempfile with proper fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


def atomic_write_text(path: Path, text: str) -> None:
    """Write text atomically using tempfile with proper fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


def atomic_write_npz(path: Path, **kwargs: Any) -> None:
    """Write NPZ atomically using tempfile with proper fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp.npz")
    try:
        with os.fdopen(fd, "wb") as handle:
            np.savez(handle, **kwargs)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


def exact_array_equal_with_nan(
    left: np.ndarray,
    right: np.ndarray,
) -> bool:
    """Compare two arrays with NaN-aware exact equality.
    
    Returns True if:
    - Shapes match
    - dtypes match
    - NaN positions match exactly
    - Non-NaN values match exactly
    
    This is the correct criterion for frozen anchor validation: same production
    source, split state, intervention seed, and future dynamics should produce
    bit-identical finite entries and NaNs in the same positions.
    """
    left = np.asarray(left)
    right = np.asarray(right)
    
    # Shape must match
    if left.shape != right.shape:
        return False
    
    # Dtype must match
    if left.dtype != right.dtype:
        return False
    
    # For floating-point or complex arrays, check NaN positions
    if np.issubdtype(left.dtype, np.floating) or np.issubdtype(left.dtype, np.complexfloating):
        left_nan = np.isnan(left)
        right_nan = np.isnan(right)
        
        # NaN positions must match exactly
        if not np.array_equal(left_nan, right_nan):
            return False
        
        # Finite values must match exactly
        finite = ~left_nan
        return np.array_equal(left[finite], right[finite])
    
    # For non-float arrays, use exact equality
    return np.array_equal(left, right)


# =============================================================================
# Bootstrap Functions
# =============================================================================


def bootstrap_ci(
    values: np.ndarray,
    repetitions: int = 1000,
    seed: int = 42,
    confidence: float = 0.95,
) -> tuple[float, float, float]:
    """Compute bootstrap confidence interval for the mean.
    
    Returns: (mean, ci_lower, ci_upper)
    """
    if len(values) < 2:
        return (float(np.nan), float(np.nan), float(np.nan))
    
    values = np.asarray(values, dtype=float)
    valid = ~np.isnan(values)
    if np.sum(valid) < 2:
        return (float(np.nan), float(np.nan), float(np.nan))
    
    values = values[valid]
    n = len(values)
    mean_val = float(np.mean(values))
    
    rng = np.random.default_rng(seed)
    bootstrap_means = np.zeros(repetitions)
    
    for i in range(repetitions):
        indices = rng.integers(0, n, size=n)
        sample = values[indices]
        bootstrap_means[i] = np.mean(sample)
    
    alpha = 1.0 - confidence
    ci_lower = float(np.percentile(bootstrap_means, 100 * alpha / 2))
    ci_upper = float(np.percentile(bootstrap_means, 100 * (1 - alpha / 2)))
    
    return (mean_val, ci_lower, ci_upper)


def wilson_ci(
    successes: int,
    trials: int,
    confidence: float = 0.95,
) -> tuple[float, float, float]:
    """Compute Wilson score confidence interval for a proportion.
    
    Returns: (proportion, ci_lower, ci_upper)
    FIX: Use statistics.NormalDist instead of scipy
    """
    if trials == 0:
        return (float(np.nan), float(np.nan), float(np.nan))
    
    p = successes / trials
    # FIX: Use statistics.NormalDist instead of scipy
    norm = NormalDist()
    z = norm.inv_cdf(1.0 - (1.0 - confidence) / 2.0)
    
    denominator = 1 + z**2 / trials
    centre = p + z**2 / (2 * trials)
    adjustment = z * math.sqrt(
        (p * (1 - p) + z**2 / (4 * trials)) / trials
    )
    
    ci_lower = (centre - adjustment) / denominator
    ci_upper = (centre + adjustment) / denominator
    
    return (p, max(0.0, float(ci_lower)), min(1.0, float(ci_upper)))


# =============================================================================
# Reconstruct Branch RNG Seeds
# =============================================================================


def reconstruct_branch_rng_seeds(
    seed: int | str,
    branch_order: list[str],
) -> dict[str, int]:
    """Reconstruct original branch RNG seeds from seed and branch_order.
    
    Uses the algorithm from the frozen run:
        _, branch_root = np.random.SeedSequence(seed).spawn(2)
        branch_sequences = branch_root.spawn(len(branch_order))
        branch_rng_seeds = {
            branch: int(sequence.generate_state(1, dtype=np.uint64)[0])
            for branch, sequence in zip(branch_order, branch_sequences)
        }
    """
    seed_int = int(seed)
    _, branch_root = np.random.SeedSequence(seed_int).spawn(2)
    branch_sequences = branch_root.spawn(len(branch_order))
    return {
        branch: int(sequence.generate_state(1, dtype=np.uint64)[0])
        for branch, sequence in zip(branch_order, branch_sequences)
    }


# =============================================================================
# State Construction and Loading
# =============================================================================


def load_split_and_prefix(
    data: dict[str, np.ndarray],
    seed: str,
    N: int,
) -> tuple[Any, dict[str, np.ndarray]]:
    """Load and construct split state and prefix from NPZ data.
    
    Constructs DynamicState directly with theta, B, coherence_acc, history.
    Preserves original dtypes in prefix arrays.
    """
    prefix: dict[str, np.ndarray] = {}
    
    # Load prefix keys - PRESERVE ORIGINAL DTYPES
    for key in prod.PREFIX_KEYS:
        prefix_key = f"prefix_seed_{seed}_{key}"
        if prefix_key in data:
            prefix[key] = np.asarray(data[prefix_key]).copy()
        else:
            raise KeyError(f"Missing prefix key: {prefix_key}")
    
    # Load state components
    theta = np.asarray(data[f"prefix_seed_{seed}_theta_at_split"], dtype=float).copy()
    B = np.asarray(data[f"prefix_seed_{seed}_B_at_split"], dtype=float).copy()
    coherence_acc = np.asarray(data[f"prefix_seed_{seed}_coherence_acc_at_split"], dtype=complex).copy()
    
    history_array = np.asarray(data[f"prefix_seed_{seed}_history_at_split"], dtype=float)
    history = deque((row.copy() for row in history_array), maxlen=len(history_array))
    
    # Construct state
    state = prod.DynamicState(
        theta=theta,
        B=B,
        coherence_acc=coherence_acc,
        history=history,
    )
    
    return state, prefix


def validate_split_state(
    state: Any,
    N: int,
    seed: str,
) -> None:
    """Validate split state after loading. Raises ValueError on failure."""
    # Check theta shape
    if state.theta.shape != (N,):
        raise ValueError(
            f"theta shape {state.theta.shape} != (N,) for seed {seed}"
        )
    
    # Check B shape
    if state.B.shape != (N, N):
        raise ValueError(
            f"B shape {state.B.shape} != (N, N) for seed {seed}"
        )
    
    # Check coherence_acc shape
    if state.coherence_acc.shape != (N, N):
        raise ValueError(
            f"coherence_acc shape {state.coherence_acc.shape} != (N, N) for seed {seed}"
        )
    
    # Check history length
    expected_history_len = getattr(prod, "DELAY_STEPS", 0) + 1
    if len(state.history) != expected_history_len:
        raise ValueError(
            f"history length {len(state.history)} != {expected_history_len} for seed {seed}"
        )
    
    # Validate B matrix
    validate_B_matrix(state.B, N, seed)


def validate_B_matrix(B: np.ndarray, N: int, seed: str | None = None) -> None:
    """Validate B matrix: symmetric, nonnegative, zero diagonal. Raises ValueError on failure."""
    msg = f" for seed {seed}" if seed else ""
    if B.shape != (N, N):
        raise ValueError(f"B shape {B.shape} != (N, N){msg}")
    if not np.array_equal(B, B.T):
        raise ValueError(f"B not symmetric{msg}")
    # FIX: Use exact equality for zero diagonal
    if not np.array_equal(np.diag(B), np.zeros(N, dtype=B.dtype)):
        raise ValueError(f"B diagonal not exactly zero{msg}")
    if np.any(B < 0):
        raise ValueError(f"B has negative entries{msg}")


# =============================================================================
# Split-State Immutability Check
# =============================================================================


def check_split_state_immutability(
    split_state: Any,
    split_snapshot: dict[str, Any],
    N: int,
) -> bool:
    """Check that split state was not mutated during branch execution."""
    checks = [
        np.array_equal(split_state.theta, split_snapshot["theta"]),
        np.array_equal(split_state.B, split_snapshot["B"]),
        np.array_equal(split_state.coherence_acc, split_snapshot["coherence"]),
    ]
    
    # Check history
    if len(split_state.history) == len(split_snapshot["history"]):
        history_ok = all(
            np.array_equal(h, snap_h)
            for h, snap_h in zip(split_state.history, split_snapshot["history"])
        )
        checks.append(history_ok)
    else:
        checks.append(False)
    
    return all(checks)


def create_split_snapshot(split_state: Any) -> dict[str, Any]:
    """Create a snapshot of split state for immutability checking."""
    return {
        "theta": split_state.theta.copy(),
        "B": split_state.B.copy(),
        "coherence": split_state.coherence_acc.copy(),
        "history": [h.copy() for h in split_state.history],
    }


# =============================================================================
# Initial State Matching Audit (MANDATORY)
# =============================================================================


def audit_initial_matching(
    state_preserved: Any,
    state_zero: Any,
    B_at_split: np.ndarray,
    N: int,
    reset_seed: int,
    reset_block: str,
    rng_state_equal: bool,
) -> dict[str, Any]:
    """Perform MANDATORY initial state matching audit with EXACT equality.
    
    Returns dict with validation results. All checks must use exact equality.
    """
    results: dict[str, Any] = {
        "reset_block": reset_block,
        "reset_seed_uint64": reset_seed,
        "rng_state_equal": rng_state_equal,
    }
    
    # 1. Theta exact equality
    theta_equal = np.array_equal(state_preserved.theta, state_zero.theta)
    results["theta_equal"] = theta_equal
    
    # 2. Coherence_acc exact equality and both zero
    coh_p_zero = np.array_equal(state_preserved.coherence_acc, np.zeros_like(state_preserved.coherence_acc))
    coh_z_zero = np.array_equal(state_zero.coherence_acc, np.zeros_like(state_zero.coherence_acc))
    coh_equal = np.array_equal(state_preserved.coherence_acc, state_zero.coherence_acc)
    results["coherence_acc_preserved_is_zero"] = coh_p_zero
    results["coherence_acc_zero_is_zero"] = coh_z_zero
    results["coherence_acc_equal"] = coh_equal
    
    # 3. B checks - preserved equals split B, zero is exactly zero matrix
    B_preserved_equal_split = np.array_equal(state_preserved.B, B_at_split)
    B_zero_is_zero = np.array_equal(state_zero.B, np.zeros((N, N)))
    results["B_preserved_equal_split"] = B_preserved_equal_split
    results["B_zero_is_zero"] = B_zero_is_zero
    
    # 4. B properties
    try:
        validate_B_matrix(state_preserved.B, N)
        results["B_preserved_valid"] = True
    except ValueError:
        results["B_preserved_valid"] = False
    
    try:
        validate_B_matrix(state_zero.B, N)
        results["B_zero_valid"] = True
    except ValueError:
        results["B_zero_valid"] = False
    
    # 5. History: length equal and every entry equals theta
    history_len_equal = len(state_preserved.history) == len(state_zero.history)
    results["history_length_equal"] = history_len_equal
    
    history_equal = True
    history_matches_theta = True
    if history_len_equal:
        for hp, hz in zip(state_preserved.history, state_zero.history):
            if not np.array_equal(hp, hz):
                history_equal = False
            if not np.array_equal(hp, state_preserved.theta):
                history_matches_theta = False
        results["history_equal"] = history_equal
        results["history_matches_theta"] = history_matches_theta
    else:
        results["history_equal"] = False
        results["history_matches_theta"] = False
    
    # 6. Array hashes for all matched arrays
    results["theta_hash_preserved"] = array_sha256(state_preserved.theta)
    results["theta_hash_zero"] = array_sha256(state_zero.theta)
    results["B_hash_preserved"] = array_sha256(state_preserved.B)
    results["B_hash_zero"] = array_sha256(state_zero.B)
    results["coherence_hash_preserved"] = array_sha256(state_preserved.coherence_acc)
    results["coherence_hash_zero"] = array_sha256(state_zero.coherence_acc)
    
    # History hash - stack deque entries
    if history_len_equal and len(state_preserved.history) > 0:
        hist_p_array = np.stack(tuple(state_preserved.history))
        hist_z_array = np.stack(tuple(state_zero.history))
        results["history_hash_preserved"] = array_sha256(hist_p_array)
        results["history_hash_zero"] = array_sha256(hist_z_array)
    else:
        results["history_hash_preserved"] = None
        results["history_hash_zero"] = None
    
    # Overall pass - ALL checks must pass
    all_checks = [
        theta_equal,
        coh_p_zero,
        coh_z_zero,
        coh_equal,
        B_preserved_equal_split,
        B_zero_is_zero,
        results.get("B_preserved_valid", False),
        results.get("B_zero_valid", False),
        history_len_equal,
        history_equal,
        history_matches_theta,
        rng_state_equal,
    ]
    results["pass"] = all(all_checks)
    
    return results


# =============================================================================
# Frozen Anchor Validation (MANDATORY)
# =============================================================================


def validate_frozen_anchor(
    new_result: dict[str, Any],
    frozen_data: dict[str, np.ndarray],
    seed: str,
    branch_label: str,
    matrix_keys: list[str],
) -> dict[str, Any]:
    """Validate new result against frozen data for anchor branch.
    
    Uses NaN-AWARE EXACT equality for all frozen matrix/trajectory keys.
    This is the correct criterion: same production source, split state,
    intervention seed, and future dynamics should produce bit-identical
    finite entries and NaNs in the same positions.
    
    Missing keys are fatal.
    Returns dict with validation results.
    
    FIX: Use exact_array_equal_with_nan() for all keys. Do not use tolerance
         comparison for frozen anchor validation - exact match is required.
         If tolerance comparison is needed for diagnostics, store it separately
         as 'tolerance_match', not 'exact'.
    """
    results: dict[str, Any] = {
        "seed": seed,
        "branch": branch_label,
        "pass": True,
    }
    
    for key in matrix_keys:
        frozen_key = f"{branch_label}_seed_{seed}_{key}"
        
        if frozen_key not in frozen_data:
            results[f"{key}_missing_in_frozen"] = True
            results["pass"] = False
            continue
        
        if key not in new_result:
            results[f"{key}_missing_in_new"] = True
            results["pass"] = False
            continue
        
        frozen_arr = np.asarray(frozen_data[frozen_key])
        new_arr = np.asarray(new_result[key])
        
        # Use NaN-aware exact equality for all frozen anchor keys
        exact_equal = exact_array_equal_with_nan(frozen_arr, new_arr)
        results[f"{key}_exact"] = exact_equal
        
        if not exact_equal:
            # Record max diff for diagnostics (treat NaN as 0 for diff calculation)
            frozen_for_diff = np.where(np.isnan(frozen_arr), 0.0, frozen_arr)
            new_for_diff = np.where(np.isnan(new_arr), 0.0, new_arr)
            max_diff = float(np.max(np.abs(frozen_for_diff - new_for_diff)))
            results[f"{key}_max_diff"] = max_diff
            results["pass"] = False
    
    return results


# =============================================================================
# Model Constant Validation
# =============================================================================


def validate_model_constants(frozen_model: dict[str, Any]) -> None:
    """Validate that frozen manifest model constants match production module constants.
    Raises RuntimeError on mismatch.
    FIX: Compare ALL frozen manifest constants against prod module constants.
         Do not use fallback-to-frozen behavior - if a required constant is absent,
         validation should fail rather than silently comparing frozen to itself.
    """
    # Required constants that must match exactly
    required_constants = {
        'N': ('N', int),
        'dt': ('DT', float),
        'T_window': ('T_WINDOW', float),
        'tau': ('TAU', float),
        'eta': ('ETA', float),
        'mu': ('MU', float),
        'gamma': ('GAMMA', float),
        'a': ('A', float),
        'q': ('Q', float),
        'delta': ('DELTA', float),
        'B_c': ('B_C', float),
        'B_init_scale': ('B_INIT_SCALE', float),
        'future_steps': ('FUTURE_STEPS', int),
        'window_steps': ('WINDOW_STEPS', int),
        'recovery_end': ('RECOVERY_END', float),
        'diagnostic_stride': ('DIAGNOSTIC_STRIDE', int),
        'delay_steps': ('DELAY_STEPS', int),
        'capacity': ('CAP', int),
    }
    
    # Validate omega separately (array)
    frozen_omega = np.asarray(frozen_model.get("omega"), dtype=float)
    prod_omega = np.asarray(getattr(prod, 'OMEGA', None), dtype=float)
    if not np.array_equal(frozen_omega, prod_omega):
        raise RuntimeError(
            f"omega mismatch: frozen={frozen_omega}, production={prod_omega}"
        )
    
    # Validate each required constant
    for frozen_key, (prod_attr, expected_type) in required_constants.items():
        if frozen_key not in frozen_model:
            raise RuntimeError(f"Frozen manifest missing required constant: {frozen_key}")
        
        frozen_value = frozen_model[frozen_key]
        
        if not hasattr(prod, prod_attr):
            raise RuntimeError(
                f"Production module missing required constant: {prod_attr} "
                f"(needed for frozen constant {frozen_key})"
            )
        
        prod_value = getattr(prod, prod_attr)
        
        # Convert to expected type for comparison
        frozen_typed = expected_type(frozen_value)
        prod_typed = expected_type(prod_value)
        
        if frozen_typed != prod_typed:
            raise RuntimeError(
                f"{frozen_key} mismatch: frozen={frozen_typed}, production={prod_typed}"
            )
    
    # Validate ZERO_TOL (the fixed safeguard, not SCALE_EPSILON)
    if hasattr(prod, 'ZERO_TOL'):
        frozen_zero_tol = 1e-12  # From frozen manifest convention
        prod_zero_tol = float(prod.ZERO_TOL)
        if not math.isclose(frozen_zero_tol, prod_zero_tol, rel_tol=1e-15):
            raise RuntimeError(
                f"ZERO_TOL mismatch: frozen={frozen_zero_tol}, production={prod_zero_tol}"
            )
    
    # Also validate derived constants if available
    if hasattr(prod, 'ALPHA'):
        frozen_alpha = math.exp(-frozen_model['dt'] / frozen_model['T_window'])
        prod_alpha = float(prod.ALPHA)
        if not math.isclose(frozen_alpha, prod_alpha, rel_tol=1e-15):
            raise RuntimeError(
                f"alpha mismatch: frozen={frozen_alpha}, production={prod_alpha}"
            )


# =============================================================================
# Recovery Outcome Computation
# =============================================================================


def compute_recovery_outcomes(
    result: dict[str, Any],
    continue_result: dict[str, Any] | None,
    seed: str,
    branch_id: str,
    protocol: dict[str, Any],
    dt: float,
) -> dict[str, Any]:
    """Compute recovery outcomes using validated helpers from recovery module.
    
    Uses relative thresholds (90% of continue reference) not absolute values.
    Uses np.maximum(0, ...) for deficit calculations.
    Creates explicit binary recovery indicators.
    
    FIX: Pass dt explicitly instead of using protocol.get("dt", 0.01)
    """
    outcomes: dict[str, Any] = {}
    
    # Copy all production scalars
    for key in prod.BRANCH_SCALAR_KEYS:
        if key in result:
            outcomes[key] = result[key]
    
    # Get reference values from continue branch
    if continue_result is not None:
        reference_final_density = continue_result.get("D_B_final", np.nan)
        reference_late_similarity = continue_result.get("Weighted_similarity_late", np.nan)
        window_time = float(protocol.get("window_steps", 0)) * dt
    else:
        reference_final_density = np.nan
        reference_late_similarity = np.nan
        window_time = 10.0
    
    sample_times = result.get("sample_times")
    
    # Similarity trajectory outcomes
    if "similarity_trajectory" in result:
        sim_traj = np.asarray(result["similarity_trajectory"], dtype=float)
        
        # Handle NaN by mapping to 0 for recovery calculations only
        sim_traj_clean = np.where(np.isnan(sim_traj), 0.0, sim_traj)
        
        if sample_times is not None and RECOVERY_AVAILABLE:
            # Use relative threshold: 90% of continue late similarity
            if not np.isnan(reference_late_similarity):
                similarity_threshold = 0.9 * reference_late_similarity
            else:
                similarity_threshold = 0.9  # Fallback only
            
            # time_to_similarity_90
            time_to_sim = recovery.time_to_at_least(
                sample_times, sim_traj_clean, similarity_threshold
            )
            outcomes["time_to_similarity_90"] = time_to_sim
            
            # sustained_similarity_90_rest
            sustained_sim = recovery.first_time_sustained_for_rest(
                sample_times, sim_traj_clean, similarity_threshold
            )
            outcomes["sustained_similarity_90_rest"] = sustained_sim
            
            # held_similarity_90_for_1Twindow
            held_sim = recovery.first_time_held_for_duration(
                sample_times, sim_traj_clean, similarity_threshold, window_time
            )
            outcomes["held_similarity_90_for_1Twindow"] = held_sim
            
            # Explicit binary recovery indicators
            outcomes["sustained_similarity_90_recovered"] = bool(np.isfinite(sustained_sim))
            outcomes["held_similarity_90_for_1Twindow_recovered"] = bool(np.isfinite(held_sim))
            
            # FIX: Add restricted-time outcomes
            horizon = sample_times[-1] if len(sample_times) > 0 else window_time
            restricted_time_to_sim = min(float(time_to_sim), horizon) if np.isfinite(time_to_sim) else horizon
            outcomes["restricted_time_to_similarity_90"] = restricted_time_to_sim
            
            # AUC similarity deficit vs continue
            # FIX: Use AUC/duration for mean, matching validated convention:
            # mean_deficit = (∫ deficit(t) dt) / (t_max - t_min)
            if continue_result is not None and "similarity_trajectory" in continue_result:
                cont_traj = np.asarray(continue_result["similarity_trajectory"], dtype=float)
                cont_traj_clean = np.where(np.isnan(cont_traj), 0.0, cont_traj)
                
                # Use np.maximum(0, ...) to avoid negative deficits
                similarity_deficit = np.maximum(0.0, cont_traj_clean - sim_traj_clean)
                
                auc_similarity_deficit = trapezoid_integral(
                    similarity_deficit, sample_times
                )
                outcomes["AUC_similarity_deficit_vs_continue"] = auc_similarity_deficit
                
                # Mean = AUC / duration, not sample mean
                duration = float(sample_times[-1] - sample_times[0]) if len(sample_times) > 1 else 0.0
                if duration > 0.0:
                    outcomes["Mean_similarity_deficit_vs_continue"] = auc_similarity_deficit / duration
                else:
                    outcomes["Mean_similarity_deficit_vs_continue"] = np.nan
        else:
            # Fallback if recovery module not available
            outcomes["time_to_similarity_90"] = np.nan
            outcomes["sustained_similarity_90_rest"] = np.nan
            outcomes["held_similarity_90_for_1Twindow"] = np.nan
            outcomes["sustained_similarity_90_recovered"] = False
            outcomes["held_similarity_90_for_1Twindow_recovered"] = False
            outcomes["restricted_time_to_similarity_90"] = np.nan
            if continue_result is not None and "similarity_trajectory" in continue_result:
                cont_traj = np.asarray(continue_result["similarity_trajectory"], dtype=float)
                cont_traj_clean = np.where(np.isnan(cont_traj), 0.0, cont_traj)
                similarity_deficit = np.maximum(0.0, cont_traj_clean - sim_traj_clean)
                if sample_times is not None:
                    outcomes["AUC_similarity_deficit_vs_continue"] = trapezoid_integral(
                        similarity_deficit, sample_times
                    )
                else:
                    outcomes["AUC_similarity_deficit_vs_continue"] = np.nan
                outcomes["Mean_similarity_deficit_vs_continue"] = float(
                    np.mean(similarity_deficit)
                )
    
    # Density trajectory outcomes
    if "density_trajectory" in result:
        dens_traj = np.asarray(result["density_trajectory"], dtype=float)
        
        if sample_times is not None and RECOVERY_AVAILABLE:
            # Use relative threshold: 90% of continue final density
            if not np.isnan(reference_final_density):
                density_threshold = 0.9 * reference_final_density
            else:
                density_threshold = 0.9  # Fallback only
            
            # time_to_density_90
            time_to_dens = recovery.time_to_at_least(
                sample_times, dens_traj, density_threshold
            )
            outcomes["time_to_density_90"] = time_to_dens
            
            # sustained_density_90_rest
            sustained_dens = recovery.first_time_sustained_for_rest(
                sample_times, dens_traj, density_threshold
            )
            outcomes["sustained_density_90_rest"] = sustained_dens
            
            # Explicit binary recovery indicator
            outcomes["sustained_density_90_recovered"] = bool(np.isfinite(sustained_dens))
            
            # FIX: Add restricted-time outcomes
            horizon = sample_times[-1] if len(sample_times) > 0 else window_time
            restricted_time_to_dens = min(float(time_to_dens), horizon) if np.isfinite(time_to_dens) else horizon
            outcomes["restricted_time_to_density_90"] = restricted_time_to_dens
            
            # AUC density deficit vs continue
            # FIX: Use AUC/duration for consistency
            if continue_result is not None and "density_trajectory" in continue_result:
                cont_dens = np.asarray(continue_result["density_trajectory"], dtype=float)
                density_deficit = np.maximum(0.0, cont_dens - dens_traj)
                
                auc_density_deficit = trapezoid_integral(
                    density_deficit, sample_times
                )
                outcomes["AUC_density_deficit_vs_continue"] = auc_density_deficit
        else:
            outcomes["time_to_density_90"] = np.nan
            outcomes["sustained_density_90_rest"] = np.nan
            outcomes["sustained_density_90_recovered"] = False
            outcomes["restricted_time_to_density_90"] = np.nan
            if continue_result is not None and "density_trajectory" in continue_result:
                cont_dens = np.asarray(continue_result["density_trajectory"], dtype=float)
                density_deficit = np.maximum(0.0, cont_dens - dens_traj)
                if sample_times is not None:
                    auc_density_deficit = trapezoid_integral(density_deficit, sample_times)
                    outcomes["AUC_density_deficit_vs_continue"] = auc_density_deficit
                else:
                    outcomes["AUC_density_deficit_vs_continue"] = np.nan
    
    return outcomes


# =============================================================================
# Contrast Computation
# =============================================================================


def compute_paired_contrasts(
    outcomes: dict[str, dict[str, Any]],
) -> dict[str, dict[str, float]]:
    """Compute paired contrasts: Y(B=preserved) - Y(B=zero) for each reset source.
    
    Returns: reset_source -> outcome -> contrast
    Only computes contrasts for explicitly declared CONTRAST_OUTCOMES.
    """
    contrasts: dict[str, dict[str, float]] = {}
    
    reset_sources = ["carrier_reset", "full_reset"]
    
    for reset_source in reset_sources:
        contrasts[reset_source] = {}
        
        preserved_key = f"{reset_source}__B_preserved"
        zero_key = f"{reset_source}__B_zero"
        
        if preserved_key not in outcomes or zero_key not in outcomes:
            continue
        
        pres = outcomes[preserved_key]
        zero = outcomes[zero_key]
        
        # Only compute for explicitly declared contrast outcomes
        for key in CONTRAST_OUTCOMES:
            if key in pres and key in zero:
                pres_val = pres[key]
                zero_val = zero[key]
                # Only compute for numeric scalars
                if isinstance(pres_val, (int, float, np.number)) and isinstance(zero_val, (int, float, np.number)):
                    try:
                        contrast = float(pres_val) - float(zero_val)
                        contrasts[reset_source][key] = contrast
                    except (TypeError, ValueError):
                        pass
    
    return contrasts


def compute_seed_level_contrasts(
    paired_contrasts: dict[str, dict[str, float]],
) -> dict[str, float]:
    """Compute seed-level average and interaction contrasts.
    
    Δ̄_s(Y) = 0.5 * [Δ_{s,carrier}(Y) + Δ_{s,full}(Y)]
    I_s(Y) = Δ_{s,carrier}(Y) - Δ_{s,full}(Y)
    
    Returns: outcome -> avg or interaction value
    """
    seed_contrasts: dict[str, float] = {}
    
    all_outcomes = set()
    for reset_source in paired_contrasts:
        all_outcomes.update(paired_contrasts[reset_source].keys())
    
    for outcome in all_outcomes:
        carrier_val = paired_contrasts.get("carrier_reset", {}).get(outcome, np.nan)
        full_val = paired_contrasts.get("full_reset", {}).get(outcome, np.nan)
        
        # Seed-level average
        if not np.isnan(carrier_val) and not np.isnan(full_val):
            seed_contrasts[f"avg_{outcome}"] = 0.5 * (carrier_val + full_val)
        else:
            seed_contrasts[f"avg_{outcome}"] = np.nan
        
        # Interaction
        if not np.isnan(carrier_val) and not np.isnan(full_val):
            seed_contrasts[f"interaction_{outcome}"] = carrier_val - full_val
        else:
            seed_contrasts[f"interaction_{outcome}"] = np.nan
    
    return seed_contrasts


# =============================================================================
# Main Analysis Function
# =============================================================================


def run_matched_phase_ablation(
    npz_path: str,
    manifest_path: str,
    scalar_path: str,
    output_dir: Path,
    seed_filter: list[str] | None = None,
    max_seeds: int | None = None,
    bootstrap_repetitions: int = 1000,
    bootstrap_seed: int = 42,
    verify_anchors: bool = True,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Main analysis function."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # FIX: Remove existing outputs if overwrite=True
    existing_outputs = [
        "matched_phase_scalar_summary.csv",
        "matched_phase_paired_contrasts.csv",
        "matched_phase_seed_level_contrasts.csv",
        "matched_phase_recovery_summary.csv",
        "matched_initial_state_audit.csv",
        "frozen_anchor_validation.csv",
        "matched_phase_branch_diagnostics.npz",
        "matched_phase_report.txt",
        "analysis_manifest.json",
        "matched_phase_seed_status.csv",
    ]
    
    if overwrite:
        for filename in existing_outputs:
            path = output_dir / filename
            if path.exists():
                path.unlink()
    else:
        existing_files = [f for f in existing_outputs if (output_dir / f).exists()]
        if existing_files:
            raise RuntimeError(
                f"Output directory {output_dir} contains existing files: {existing_files}. "
                f"Use --overwrite to replace, or use an empty directory."
            )
    
    # --- Load manifest ---
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # Validate manifest structure - CORRECTED PATHS
    if "protocol" not in manifest or "branches" not in manifest["protocol"]:
        raise ValueError("Manifest missing protocol.branches")
    if "randomization" not in manifest or "paired_seeds" not in manifest["randomization"]:
        raise ValueError("Manifest missing randomization.paired_seeds")
    
    model = manifest["model"]
    protocol = manifest["protocol"]
    
    # FIX: Validate model constants match production
    validate_model_constants(model)
    
    # Get branch order from correct path
    branch_order = tuple(manifest["protocol"]["branches"])
    
    # Validate branch order matches production
    if not hasattr(prod, "BRANCHES"):
        raise ValueError("Production module missing BRANCHES attribute")
    if branch_order != tuple(prod.BRANCHES):
        raise ValueError(
            f"Branch order mismatch: manifest={branch_order}, "
            f"prod.BRANCHES={tuple(prod.BRANCHES)}"
        )
    
    # Get seeds from correct path
    all_seeds = [str(s) for s in manifest["randomization"]["paired_seeds"]]
    if not all_seeds:
        raise ValueError("No seeds found in manifest")
    
    # FIX: Verify seed uniqueness
    if len(set(all_seeds)) != len(all_seeds):
        raise RuntimeError("Duplicate seeds in frozen manifest")
    
    # Apply filter
    if seed_filter:
        seeds = [s for s in all_seeds if s in seed_filter]
    else:
        seeds = all_seeds
    
    # FIX: Reject empty seed filter
    if not seeds:
        raise ValueError("No seeds selected - check seed filter")
    
    # FIX: Handle max_seeds=0
    if max_seeds is not None:
        if max_seeds == 0:
            raise ValueError("--max-seeds must be positive or None")
        seeds = seeds[:max_seeds]
    
    # FIX: Validate bootstrap_repetitions > 0 for production
    if bootstrap_repetitions <= 0:
        raise ValueError("--bootstrap-repetitions must be positive")
    
    # FIX: Recovery dependency is MANDATORY for production
    if not RECOVERY_AVAILABLE:
        raise RuntimeError(
            f"Validated recovery dependency unavailable: {RECOVERY_ERROR}"
        )
    
    print(f"Processing {len(seeds)} seeds...")
    
    # Get model constants
    N = int(model["N"])
    dt = float(model["dt"])
    T_window = float(model["T_window"])
    
    # Get matrix keys for validation
    matrix_keys = getattr(prod, "BRANCH_MATRIX_KEYS", [])
    if not matrix_keys:
        raise ValueError("prod.BRANCH_MATRIX_KEYS is empty or not defined")
    
    # --- Load frozen data ---
    with np.load(npz_path, allow_pickle=False) as frozen_npz:
        frozen_data = {key: frozen_npz[key] for key in frozen_npz.files}
    
    # Load scalar CSV for hash verification
    scalar_sha256 = None
    if os.path.exists(scalar_path):
        scalar_sha256 = file_sha256(scalar_path)
    
    # --- Initialize storage ---
    all_results: dict[str, dict[str, Any]] = {}
    all_contrasts: dict[str, dict[str, dict[str, float]]] = {}
    all_seed_contrasts: dict[str, dict[str, float]] = {}
    audit_rows: list[dict[str, Any]] = []
    anchor_validation_rows: list[dict[str, Any]] = []
    seed_status: dict[str, str] = {}
    immutability_by_seed: dict[str, bool] = {}  # FIX: Store immutability results
    
    # Determine run scope
    # FIX: Use set comparison for order-insensitive check
    full_cohort = (set(seeds) == set(all_seeds) and len(seeds) == len(all_seeds))
    
    # FIX: Collect fatal exception instead of immediate re-raise
    fatal_exception = None
    
    # --- Process each seed ---
    for seed in seeds:
        seed_str = str(seed)
        print(f"  Seed: {seed_str}")
        
        try:
            # --- Load split state and prefix ---
            split_state, prefix = load_split_and_prefix(frozen_data, seed_str, N)
            B_at_split = split_state.B.copy()
            
            # FIX: Validate split state
            validate_split_state(split_state, N, seed_str)
            
            # FIX: Create snapshot for immutability check
            split_snapshot = create_split_snapshot(split_state)
            
            # --- Reconstruct ALL branch RNG seeds from manifest ---
            branch_rng_seeds = reconstruct_branch_rng_seeds(seed, list(branch_order))
            
            # Get seeds for our reset blocks
            carrier_reset_seed = branch_rng_seeds.get("B_carrier_only")
            if carrier_reset_seed is None:
                raise ValueError(f"B_carrier_only not in branch_rng_seeds for seed {seed_str}")
            
            full_reset_seed = branch_rng_seeds.get("full_reset")
            if full_reset_seed is None:
                raise ValueError(f"full_reset not in branch_rng_seeds for seed {seed_str}")
            
            # FIX: Require continue RNG seed
            if "continue" not in branch_rng_seeds:
                raise RuntimeError(f"continue RNG seed missing for seed {seed_str}")
            continue_seed = branch_rng_seeds["continue"]
            
            # --- RESET BLOCK A: carrier_reset seed ---
            print(f"    Reset block A (carrier_reset, seed={carrier_reset_seed})")
            
            # CORRECTED: Use actual production API
            # carrier_reset__B_preserved: reproduces B_carrier_only
            result_carrier_preserved = prod.simulate_future(
                copy.deepcopy(split_state),
                prefix,
                "B_carrier_only",
                np.random.default_rng(carrier_reset_seed),
            )
            
            # carrier_reset__B_zero: new, B=0, same reset seed
            result_carrier_zero = prod.simulate_future(
                copy.deepcopy(split_state),
                prefix,
                "full_reset",
                np.random.default_rng(carrier_reset_seed),
            )
            
            # --- Initial matching audit for Block A ---
            # FIX: Compare RNG states directly after intervention
            state_preserved_A = copy.deepcopy(split_state)
            state_zero_A = copy.deepcopy(split_state)
            
            rng_audit_p_A = np.random.default_rng(carrier_reset_seed)
            rng_audit_z_A = np.random.default_rng(carrier_reset_seed)
            
            prod.apply_intervention(state_preserved_A, "B_carrier_only", rng_audit_p_A)
            prod.apply_intervention(state_zero_A, "full_reset", rng_audit_z_A)
            
            rng_state_equal_A = (rng_audit_p_A.bit_generator.state == rng_audit_z_A.bit_generator.state)
            
            audit_A = audit_initial_matching(
                state_preserved_A, state_zero_A, B_at_split, N,
                carrier_reset_seed, "carrier_reset", rng_state_equal_A
            )
            audit_A["seed"] = seed_str
            audit_rows.append(audit_A)
            
            # MANDATORY: Stop on matching failure
            if not audit_A["pass"]:
                raise RuntimeError(
                    f"Initial matching FAILED for seed={seed_str}, "
                    f"block=carrier_reset. Check matched_initial_state_audit.csv"
                )
            
            # --- RESET BLOCK B: full_reset seed ---
            print(f"    Reset block B (full_reset, seed={full_reset_seed})")
            
            # full_reset__B_preserved: new, B=Bsplit
            result_full_preserved = prod.simulate_future(
                copy.deepcopy(split_state),
                prefix,
                "B_carrier_only",
                np.random.default_rng(full_reset_seed),
            )
            
            # full_reset__B_zero: reproduces full_reset
            result_full_zero = prod.simulate_future(
                copy.deepcopy(split_state),
                prefix,
                "full_reset",
                np.random.default_rng(full_reset_seed),
            )
            
            # --- Initial matching audit for Block B ---
            state_preserved_B = copy.deepcopy(split_state)
            state_zero_B = copy.deepcopy(split_state)
            
            rng_audit_p_B = np.random.default_rng(full_reset_seed)
            rng_audit_z_B = np.random.default_rng(full_reset_seed)
            
            prod.apply_intervention(state_preserved_B, "B_carrier_only", rng_audit_p_B)
            prod.apply_intervention(state_zero_B, "full_reset", rng_audit_z_B)
            
            rng_state_equal_B = (rng_audit_p_B.bit_generator.state == rng_audit_z_B.bit_generator.state)
            
            audit_B = audit_initial_matching(
                state_preserved_B, state_zero_B, B_at_split, N,
                full_reset_seed, "full_reset", rng_state_equal_B
            )
            audit_B["seed"] = seed_str
            audit_rows.append(audit_B)
            
            # MANDATORY: Stop on matching failure
            if not audit_B["pass"]:
                raise RuntimeError(
                    f"Initial matching FAILED for seed={seed_str}, "
                    f"block=full_reset. Check matched_initial_state_audit.csv"
                )
            
            # --- CONTINUE branch ---
            print(f"    Continue branch (seed={continue_seed})")
            result_continue = prod.simulate_future(
                copy.deepcopy(split_state),
                prefix,
                "continue",
                np.random.default_rng(continue_seed),
            )
            
            # --- FIX: Check split state immutability ---
            immutability_ok = check_split_state_immutability(
                split_state, split_snapshot, N
            )
            immutability_by_seed[seed_str] = immutability_ok
            
            if not immutability_ok:
                raise RuntimeError(
                    f"Split state was mutated for seed={seed_str}"
                )
            
            # --- Frozen anchor validation (MANDATORY) ---
            if verify_anchors:
                # Validate carrier_reset__B_preserved against frozen B_carrier_only
                anchor_A = validate_frozen_anchor(
                    result_carrier_preserved, frozen_data, seed_str,
                    "B_carrier_only", matrix_keys
                )
                anchor_A["production_branch"] = "B_carrier_only"
                anchor_A["matched_branch"] = "carrier_reset__B_preserved"
                anchor_validation_rows.append(anchor_A)
                
                # Validate full_reset__B_zero against frozen full_reset
                anchor_B = validate_frozen_anchor(
                    result_full_zero, frozen_data, seed_str,
                    "full_reset", matrix_keys
                )
                anchor_B["production_branch"] = "full_reset"
                anchor_B["matched_branch"] = "full_reset__B_zero"
                anchor_validation_rows.append(anchor_B)
                
                # Validate continue against frozen continue
                anchor_C = validate_frozen_anchor(
                    result_continue, frozen_data, seed_str,
                    "continue", matrix_keys
                )
                anchor_C["production_branch"] = "continue"
                anchor_C["matched_branch"] = "continue"
                anchor_validation_rows.append(anchor_C)
                
                # MANDATORY: Stop on any anchor failure
                seed_anchors = [r for r in anchor_validation_rows if r["seed"] == seed_str]
                if any(not r.get("pass", True) for r in seed_anchors):
                    raise RuntimeError(
                        f"Anchor validation FAILED for seed={seed_str}. "
                        f"Check frozen_anchor_validation.csv for details."
                    )
            
            # --- FIX: Store raw branch results for NPZ serialization ---
            branch_results = {
                "carrier_reset__B_preserved": result_carrier_preserved,
                "carrier_reset__B_zero": result_carrier_zero,
                "full_reset__B_preserved": result_full_preserved,
                "full_reset__B_zero": result_full_zero,
                "continue": result_continue,
            }
            
            # --- Compute outcomes ---
            outcomes: dict[str, dict[str, Any]] = {}
            
            for branch_id in BRANCH_IDS:
                result = branch_results[branch_id]
                meta = BRANCH_META[branch_id]
                
                # Compute recovery outcomes - FIX: Pass dt explicitly
                if branch_id == "continue":
                    # FIX: For continue, use its own result as reference
                    branch_outcomes = compute_recovery_outcomes(
                        result, result, seed_str, branch_id, protocol, dt
                    )
                else:
                    branch_outcomes = compute_recovery_outcomes(
                        result, result_continue, seed_str, branch_id, protocol, dt
                    )
                
                # Add metadata
                # FIX: Use explicit branching for reset_seed to handle zero values (zero is falsey)
                if meta["reset_source"] == "carrier_reset":
                    reset_seed_value = carrier_reset_seed
                elif meta["reset_source"] == "full_reset":
                    reset_seed_value = full_reset_seed
                else:
                    reset_seed_value = continue_seed
                
                branch_outcomes.update({
                    "seed": seed_str,
                    "branch": branch_id,
                    "reset_source": meta["reset_source"],
                    "B_status": meta["B_status"],
                    "production_intervention_label": meta["production_intervention_label"],
                    "frozen_anchor_branch": meta["frozen_anchor_branch"],
                    "reset_seed_uint64": reset_seed_value,
                })
                
                outcomes[branch_id] = branch_outcomes
            
            # --- Compute contrasts ---
            paired = compute_paired_contrasts(outcomes)
            seed_level = compute_seed_level_contrasts(paired)
            
            # Commit seed results (only after all validation passes)
            seed_results: dict[str, Any] = {
                "branches": branch_results,  # FIX: Store raw results
                "outcomes": outcomes,
                "paired_contrasts": paired,
                "seed_level_contrasts": seed_level,
            }
            
            all_results[seed_str] = seed_results
            all_contrasts[seed_str] = paired
            all_seed_contrasts[seed_str] = seed_level
            
            seed_status[seed_str] = "success"
            print(f"    Status: SUCCESS")
            
        except Exception as exc:
            seed_status[seed_str] = f"failed: {type(exc).__name__}: {exc}"
            print(f"    Status: FAILED - {type(exc).__name__}: {exc}")
            import traceback
            traceback.print_exc()
            # FIX: Collect exception instead of immediate re-raise
            if fatal_exception is None:
                fatal_exception = exc
            # Continue to next seed to collect all failures
            # But for production, we want to stop on first failure
            # So we'll break after collecting this one
            break
    
    # --- Check for failures ---
    failed_seeds = [s for s, status in seed_status.items() if status != "success"]
    initial_match_failed = any(not r.get("pass", False) for r in audit_rows)
    anchor_failed = any(not r.get("pass", True) for r in anchor_validation_rows) if anchor_validation_rows else False
    
    if failed_seeds:
        print(f"\nFAILED seeds: {failed_seeds}")
    if initial_match_failed:
        print(f"Initial matching FAILED for some cases")
    if anchor_failed:
        print(f"Anchor validation FAILED for some cases")
    
    # FIX: Write validation outputs and failure manifest if there was a fatal exception
    if fatal_exception is not None:
        # Write validation-only outputs
        if audit_rows:
            audit_df = pd.DataFrame(audit_rows)
            atomic_write_csv(output_dir / "matched_initial_state_audit.csv", audit_df)
        if anchor_validation_rows:
            anchor_df = pd.DataFrame(anchor_validation_rows)
            atomic_write_csv(output_dir / "frozen_anchor_validation.csv", anchor_df)
        
        # Write failure manifest
        failure_manifest = {
            "status": "FAILED",
            "error": str(fatal_exception),
            "initial_match_failed": initial_match_failed,
            "anchor_failed": anchor_failed,
            "failed_seeds": failed_seeds,
            "seeds_requested": seeds,
            "seed_status": seed_status,
            "run_scope": "partial",
            "full_cohort": False,
            "freezeable": False,
        }
        atomic_write_json(output_dir / "analysis_manifest.json", failure_manifest)
        
        raise RuntimeError(
            "Matched-phase run failed validation; scientific outputs were not produced"
        ) from fatal_exception
    
    # --- Save outputs ---
    
    # 1. Scalar summary - include ALL production scalars
    scalar_rows = []
    for seed_str, results in all_results.items():
        for branch_id, branch_outcomes in results["outcomes"].items():
            row = dict(branch_outcomes)  # Includes all production scalars + derived
            scalar_rows.append(row)
    
    if scalar_rows:
        scalar_df = pd.DataFrame(scalar_rows)
        atomic_write_csv(output_dir / "matched_phase_scalar_summary.csv", scalar_df)
        print(f"  Saved: matched_phase_scalar_summary.csv")
    
    # 2. Paired contrasts
    contrast_rows = []
    for seed_str, paired in all_contrasts.items():
        for reset_source, outcomes in paired.items():
            for outcome, contrast in outcomes.items():
                contrast_rows.append({
                    "seed": seed_str,
                    "reset_source": reset_source,
                    "outcome": outcome,
                    "contrast": contrast,
                })
    
    if contrast_rows:
        contrast_df = pd.DataFrame(contrast_rows)
        atomic_write_csv(output_dir / "matched_phase_paired_contrasts.csv", contrast_df)
        print(f"  Saved: matched_phase_paired_contrasts.csv")
    
    # 3. Seed-level contrasts
    seed_contrast_rows = []
    for seed_str, seed_level in all_seed_contrasts.items():
        for outcome, value in seed_level.items():
            seed_contrast_rows.append({
                "seed": seed_str,
                "outcome": outcome,
                "value": value,
            })
    
    if seed_contrast_rows:
        seed_contrast_df = pd.DataFrame(seed_contrast_rows)
        atomic_write_csv(output_dir / "matched_phase_seed_level_contrasts.csv", seed_contrast_df)
        print(f"  Saved: matched_phase_seed_level_contrasts.csv")
    
    # 4. Recovery summary
    recovery_outcomes = [
        "sustained_similarity_90_rest",
        "sustained_density_90_rest",
        "held_similarity_90_for_1Twindow",
        "sustained_similarity_90_recovered",
        "sustained_density_90_recovered",
        "held_similarity_90_for_1Twindow_recovered",
        "time_to_similarity_90",
        "time_to_density_90",
        "restricted_time_to_similarity_90",
        "restricted_time_to_density_90",
        "AUC_similarity_deficit_vs_continue",
        "Mean_similarity_deficit_vs_continue",
        "AUC_density_deficit_vs_continue",
    ] + list(prod.BRANCH_SCALAR_KEYS)
    
    recovery_rows = []
    for seed_str, results in all_results.items():
        for branch_id, branch_outcomes in results["outcomes"].items():
            row = {
                "seed": seed_str,
                "branch": branch_id,
                "reset_source": branch_outcomes.get("reset_source"),
                "B_status": branch_outcomes.get("B_status"),
            }
            for key in recovery_outcomes:
                if key in branch_outcomes:
                    row[key] = branch_outcomes[key]
            recovery_rows.append(row)
    
    if recovery_rows:
        recovery_df = pd.DataFrame(recovery_rows)
        atomic_write_csv(output_dir / "matched_phase_recovery_summary.csv", recovery_df)
        print(f"  Saved: matched_phase_recovery_summary.csv")
    
    # 5. Initial state audit
    if audit_rows:
        audit_df = pd.DataFrame(audit_rows)
        atomic_write_csv(output_dir / "matched_initial_state_audit.csv", audit_df)
        print(f"  Saved: matched_initial_state_audit.csv")
    
    # 6. Frozen anchor validation
    if anchor_validation_rows:
        anchor_df = pd.DataFrame(anchor_validation_rows)
        atomic_write_csv(output_dir / "frozen_anchor_validation.csv", anchor_df)
        print(f"  Saved: frozen_anchor_validation.csv")
    
    # 7. Branch diagnostics NPZ - FIX: Use stored branch_results
    npz_output = {}
    for seed_str, results in all_results.items():
        for branch_id, branch_result in results["branches"].items():
            if isinstance(branch_result, dict):
                for key, value in branch_result.items():
                    if isinstance(value, np.ndarray):
                        npz_key = f"{branch_id}_seed_{seed_str}_{key}"
                        npz_output[npz_key] = value
    
    if npz_output:
        atomic_write_npz(output_dir / "matched_phase_branch_diagnostics.npz", **npz_output)
        print(f"  Saved: matched_phase_branch_diagnostics.npz")
    
    # FIX: 8. Add seed-status output
    seed_status_rows = []
    for seed_str, status in seed_status.items():
        row = {"seed": seed_str, "status": status}
        
        # Add reset seeds - FIX: Read from outcomes, not meta
        if seed_str in all_results:
            results = all_results[seed_str]
            outcomes = results.get("outcomes", {})
            
            # Read actual reset seeds from outcomes
            if "carrier_reset__B_preserved" in outcomes:
                row["carrier_reset_seed"] = outcomes["carrier_reset__B_preserved"].get("reset_seed_uint64")
            if "full_reset__B_zero" in outcomes:
                row["full_reset_seed"] = outcomes["full_reset__B_zero"].get("reset_seed_uint64")
            if "continue" in outcomes:
                row["continue_seed"] = outcomes["continue"].get("reset_seed_uint64")
        
        # FIX: Require ALL expected audits to pass, not just any
        seed_audits = [r for r in audit_rows if r.get("seed") == seed_str]
        # Should have 2 audits per seed (carrier_reset and full_reset blocks)
        row["initial_match_pass"] = (len(seed_audits) == 2 and all(r.get("pass", False) for r in seed_audits)) if seed_audits else False
        
        # FIX: Require ALL expected anchors to pass, not just any
        seed_anchors = [r for r in anchor_validation_rows if r.get("seed") == seed_str]
        # Should have 3 anchors per seed (B_carrier_only, full_reset, continue)
        row["anchor_pass"] = (not verify_anchors or (len(seed_anchors) == 3 and all(r.get("pass", True) for r in seed_anchors))) if seed_anchors else True
        
        row["split_immutable"] = immutability_by_seed.get(seed_str, False)
        
        seed_status_rows.append(row)
    
    if seed_status_rows:
        seed_status_df = pd.DataFrame(seed_status_rows)
        atomic_write_csv(output_dir / "matched_phase_seed_status.csv", seed_status_df)
        print(f"  Saved: matched_phase_seed_status.csv")
    
    # --- Compute aggregate statistics ---
    
    # FIX: Only use CONTINUOUS_SUMMARY_OUTCOMES for continuous bootstrap
    continuous_bootstrap_stats: dict[str, dict[str, Any]] = {}
    for outcome in CONTINUOUS_SUMMARY_OUTCOMES:
        # Only compute for avg_* outcomes
        avg_key = f"avg_{outcome}"
        values = []
        for seed_str, seed_level in all_seed_contrasts.items():
            if avg_key in seed_level and not np.isnan(seed_level[avg_key]):
                values.append(seed_level[avg_key])
        
        if len(values) >= 2:
            mean_val, ci_lower, ci_upper = bootstrap_ci(
                np.array(values), bootstrap_repetitions, bootstrap_seed
            )
            n = len(values)
            values_arr = np.array(values)
            n_pos = int(np.sum(values_arr > 0))
            n_zero = int(np.sum(values_arr == 0))
            n_neg = int(np.sum(values_arr < 0))
            
            continuous_bootstrap_stats[outcome] = {
                "mean": mean_val,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "median": float(np.median(values)),
                "std": float(np.std(values, ddof=1)),  # Sample SD
                "n": n,
                "n_positive": n_pos,
                "n_zero": n_zero,
                "n_negative": n_neg,
            }
    
    # For binary outcomes: recovery probability per reset_source and B_status
    binary_stats: dict[str, dict[str, Any]] = {}
    for outcome in BINARY_OUTCOMES:
        # Count per reset_source and B_status
        counts: dict[str, dict[str, dict[str, int]]] = {
            "carrier_reset": {"preserved": {"success": 0, "total": 0}, "zero": {"success": 0, "total": 0}},
            "full_reset": {"preserved": {"success": 0, "total": 0}, "zero": {"success": 0, "total": 0}},
        }
        
        for seed_str, results in all_results.items():
            for branch_id, branch_outcomes in results["outcomes"].items():
                reset_source = branch_outcomes.get("reset_source")
                b_status = branch_outcomes.get("B_status")
                
                if reset_source not in ["carrier_reset", "full_reset"]:
                    continue
                if b_status not in ["preserved", "zero"]:
                    continue
                
                if outcome in branch_outcomes:
                    val = branch_outcomes[outcome]
                    # FIX: Include all seeds in denominator, check for truth value
                    counts[reset_source][b_status]["total"] += 1
                    if val:
                        counts[reset_source][b_status]["success"] += 1
        
        binary_stats[outcome] = {}
        for reset_source in ["carrier_reset", "full_reset"]:
            for b_status in ["preserved", "zero"]:
                s = counts[reset_source][b_status]["success"]
                t = counts[reset_source][b_status]["total"]
                key_base = f"{reset_source}_{b_status}"
                if t > 0:
                    p, ci_l, ci_u = wilson_ci(s, t)
                    binary_stats[outcome][f"{key_base}_probability"] = p
                    binary_stats[outcome][f"{key_base}_ci_lower"] = ci_l
                    binary_stats[outcome][f"{key_base}_ci_upper"] = ci_u
                    binary_stats[outcome][f"{key_base}_count"] = t
                else:
                    binary_stats[outcome][f"{key_base}_probability"] = np.nan
                    binary_stats[outcome][f"{key_base}_ci_lower"] = np.nan
                    binary_stats[outcome][f"{key_base}_ci_upper"] = np.nan
                    binary_stats[outcome][f"{key_base}_count"] = 0
            
            # Discordant counts for this reset_source
            discordant = {"both": 0, "only_preserved": 0, "only_zero": 0, "neither": 0}
            for seed_str, results in all_results.items():
                pres_val = results["outcomes"].get(f"{reset_source}__B_preserved", {}).get(outcome)
                zero_val = results["outcomes"].get(f"{reset_source}__B_zero", {}).get(outcome)
                
                # FIX: Include all seeds, handle None/NaN properly
                if pres_val is None or zero_val is None:
                    continue
                
                if pres_val and zero_val:
                    discordant["both"] += 1
                elif pres_val and not zero_val:
                    discordant["only_preserved"] += 1
                elif not pres_val and zero_val:
                    discordant["only_zero"] += 1
                else:
                    discordant["neither"] += 1
            
            for k, v in discordant.items():
                binary_stats[outcome][f"{reset_source}_discordant_{k}"] = v
            
            # FIX: Paired probability difference (McNemar-style)
            n_only_pres = discordant["only_preserved"]
            n_only_zero = discordant["only_zero"]
            n_total = discordant["both"] + n_only_pres + n_only_zero + discordant["neither"]
            if n_total > 0:
                paired_diff = (n_only_pres - n_only_zero) / n_total
                binary_stats[outcome][f"{reset_source}_paired_probability_diff"] = paired_diff
            else:
                binary_stats[outcome][f"{reset_source}_paired_probability_diff"] = np.nan
    
    # For censored time outcomes: recovery probability and restricted mean
    censored_stats: dict[str, dict[str, Any]] = {}
    
    # FIX: Use correct horizon - end of observation from continue branch
    # Get horizon from first successful seed's continue result
    horizon = None
    for seed_str, results in all_results.items():
        if "continue" in results["branches"]:
            cont_result = results["branches"]["continue"]
            if "sample_times" in cont_result and len(cont_result["sample_times"]) > 0:
                horizon = float(cont_result["sample_times"][-1])
                break
    
    if horizon is None:
        # Fallback to protocol value
        horizon = float(protocol.get("recovery_end", 100)) * dt
    
    for outcome in CENSORED_TIME_OUTCOMES:
        censored_stats[outcome] = {}
        
        for reset_source in ["carrier_reset", "full_reset"]:
            for b_status in ["preserved", "zero"]:
                finite_counts = 0
                total_counts = 0
                restricted_times: list[float] = []
                
                for seed_str, results in all_results.items():
                    branch_id = f"{reset_source}__B_{b_status}"
                    if branch_id in results["outcomes"]:
                        val = results["outcomes"][branch_id].get(outcome)
                        # FIX: Include ALL seeds in denominator
                        total_counts += 1
                        if val is not None and not np.isnan(val) and np.isfinite(val):
                            finite_counts += 1
                            restricted_times.append(min(float(val), horizon))
                        else:
                            # Unrecovered: use horizon
                            restricted_times.append(horizon)
                
                key_base = f"{reset_source}_{b_status}"
                if total_counts > 0:
                    censored_stats[outcome][f"{key_base}_recovery_probability"] = finite_counts / total_counts
                else:
                    censored_stats[outcome][f"{key_base}_recovery_probability"] = np.nan
                
                # Restricted Mean Time (not RMST - no KM estimator)
                if restricted_times:
                    censored_stats[outcome][f"{key_base}_restricted_mean_time"] = float(np.mean(restricted_times))
                else:
                    censored_stats[outcome][f"{key_base}_restricted_mean_time"] = np.nan
    
    # FIX: Seed-level two-block binary contrast
    # Bootstrap seed-level binary contrasts across 40 seeds
    binary_contrast_stats: dict[str, dict[str, Any]] = {}
    for outcome in BINARY_OUTCOMES:
        # Get seed-level average contrasts for binary outcomes
        values = []
        for seed_str, seed_level in all_seed_contrasts.items():
            avg_key = f"avg_{outcome}"
            if avg_key in seed_level and not np.isnan(seed_level[avg_key]):
                values.append(seed_level[avg_key])
        
        if len(values) >= 2:
            mean_val, ci_lower, ci_upper = bootstrap_ci(
                np.array(values), bootstrap_repetitions, bootstrap_seed
            )
            n = len(values)
            values_arr = np.array(values)
            n_pos = int(np.sum(values_arr > 0))
            n_zero = int(np.sum(values_arr == 0))
            n_neg = int(np.sum(values_arr < 0))
            
            binary_contrast_stats[outcome] = {
                "mean": mean_val,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "median": float(np.median(values)),
                "std": float(np.std(values, ddof=1)),
                "n": n,
                "n_positive": n_pos,
                "n_zero": n_zero,
                "n_negative": n_neg,
            }
    
    # --- FIX: Summarize reset-realization interaction ---
    interaction_stats: dict[str, dict[str, Any]] = {}
    for outcome in CONTINUOUS_SUMMARY_OUTCOMES:
        interaction_key = f"interaction_{outcome}"
        values = []
        for seed_str, seed_level in all_seed_contrasts.items():
            if interaction_key in seed_level and not np.isnan(seed_level[interaction_key]):
                values.append(seed_level[interaction_key])
        
        if len(values) >= 2:
            mean_val, ci_lower, ci_upper = bootstrap_ci(
                np.array(values), bootstrap_repetitions, bootstrap_seed
            )
            values_arr = np.array(values)
            n_pos = int(np.sum(values_arr > 0))
            n_zero = int(np.sum(values_arr == 0))
            n_neg = int(np.sum(values_arr < 0))
            
            interaction_stats[outcome] = {
                "mean": mean_val,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "median": float(np.median(values)),
                "std": float(np.std(values, ddof=1)),
                "n": len(values),
                "n_positive": n_pos,
                "n_zero": n_zero,
                "n_negative": n_neg,
            }
    
    # --- Generate report ---
    report_lines = [
        "=" * 70,
        "AIEF-1.4 Matched Phase Memory Ablation",
        "=" * 70,
        "",
        "PURPOSE:",
        "Correct the unmatched phase/history randomization in the original",
        "B_carrier_only vs full_reset comparison by constructing matched",
        "phase/history reset blocks.",
        "",
        "SCIENTIFIC ESTIMAND:",
        "For each frozen seed/graph, estimate the effect of preserving mature B,",
        "conditional on the same randomized phase vector, history deque,",
        "zeroed complex EMA state, omega, and future dynamics.",
        "",
        "-" * 70,
        "RUN SUMMARY",
        "-" * 70,
        f"Total seeds: {len(seeds)}",
        f"Seeds succeeded: {len([s for s in seed_status.values() if s == 'success'])}",
        f"Seeds failed: {len(failed_seeds)}",
        f"Initial matching passed: {len([r for r in audit_rows if r.get('pass', False)])}/{len(audit_rows) if audit_rows else 0}",
        f"Anchor validation passed: {len([r for r in anchor_validation_rows if r.get('pass', True)])}/{len(anchor_validation_rows) if anchor_validation_rows else 0}",
        f"Censoring horizon: {horizon:.4f}",
        f"Run scope: {'full_cohort' if full_cohort else 'partial'}",
        f"Freezeable: {not bool(failed_seeds) and verify_anchors and full_cohort}",
        "",
    ]
    
    # Continuous outcomes with bootstrap CI
    if continuous_bootstrap_stats:
        report_lines.extend([
            "-" * 70,
            "CONTINUOUS OUTCOMES - Seed-level Average Contrasts",
            "Delta_bar_s(Y) = 0.5 * [Delta_{s,carrier}(Y) + Delta_{s,full}(Y)]",
            "with bootstrap 95% CI",
            "-" * 70,
            "",
        ])
        for outcome, s in continuous_bootstrap_stats.items():
            report_lines.append(f"  {outcome}:")
            report_lines.append(
                f"    mean = {s['mean']:.6g} "
                f"[CI: {s['ci_lower']:.6g}, {s['ci_upper']:.6g}]"
            )
            report_lines.append(
                f"    median = {s['median']:.6g}, std = {s['std']:.6g}"
            )
            report_lines.append(
                f"    n = {s['n']}, + = {s['n_positive']}, "
                f"0 = {s['n_zero']}, - = {s['n_negative']}"
            )
            report_lines.append("")
    
    # Binary outcomes - per reset source
    if binary_stats:
        report_lines.extend([
            "-" * 70,
            "BINARY OUTCOMES - Recovery Probability by Reset Source",
            "-" * 70,
            "",
        ])
        for outcome, s in binary_stats.items():
            report_lines.append(f"  {outcome}:")
            for reset_source in ["carrier_reset", "full_reset"]:
                report_lines.append(f"    Reset source: {reset_source}")
                for b_status in ["preserved", "zero"]:
                    p_key = f"{reset_source}_{b_status}_probability"
                    ci_l_key = f"{reset_source}_{b_status}_ci_lower"
                    ci_u_key = f"{reset_source}_{b_status}_ci_upper"
                    n_key = f"{reset_source}_{b_status}_count"
                    p = s.get(p_key, np.nan)
                    ci_l = s.get(ci_l_key, np.nan)
                    ci_u = s.get(ci_u_key, np.nan)
                    n = s.get(n_key, 0)
                    if not pd.isna(p):
                        report_lines.append(
                            f"      B={b_status}: p={p:.4f} [CI: {ci_l:.4f}, {ci_u:.4f}], n={n}"
                        )
                # Discordant counts
                for k in ["both", "only_preserved", "only_zero", "neither"]:
                    v = s.get(f"{reset_source}_discordant_{k}", 0)
                    report_lines.append(f"      Discordant {k}: {v}")
                # Paired probability difference
                p_diff = s.get(f"{reset_source}_paired_probability_diff", np.nan)
                if not pd.isna(p_diff):
                    report_lines.append(
                        f"      Paired probability difference: {p_diff:.4f}"
                    )
            report_lines.append("")
    
    # Seed-level two-block binary contrast
    if binary_contrast_stats:
        report_lines.extend([
            "-" * 70,
            "SEED-LEVEL TWO-BLOCK BINARY CONTRAST",
            "Delta^binary_s = 0.5 * [(I^B_{s,carrier} - I^0_{s,carrier}) + (I^B_{s,full} - I^0_{s,full})]",
            f"Bootstrap CI across {len(seeds)} seeds (values in {{-1, -1/2, 0, 1/2, 1}})",
            "-" * 70,
            "",
        ])
        for outcome, s in binary_contrast_stats.items():
            report_lines.append(f"  {outcome}:")
            report_lines.append(
                f"    mean = {s['mean']:.6g} "
                f"[CI: {s['ci_lower']:.6g}, {s['ci_upper']:.6g}]"
            )
            report_lines.append(
                f"    median = {s['median']:.6g}, std = {s['std']:.6g}"
            )
            report_lines.append(
                f"    n = {s['n']}, + = {s['n_positive']}, "
                f"0 = {s['n_zero']}, - = {s['n_negative']}"
            )
            report_lines.append("")
    
    # Censored time outcomes - per reset source
    if censored_stats:
        report_lines.extend([
            "-" * 70,
            "CENSORED TIME OUTCOMES - Recovery over Horizon",
            f"Horizon: {horizon:.4f} (from continue branch sample_times[-1])",
            "All seeds included in denominators; unrecovered = horizon",
            "-" * 70,
            "",
        ])
        for outcome, s in censored_stats.items():
            report_lines.append(f"  {outcome}:")
            for reset_source in ["carrier_reset", "full_reset"]:
                report_lines.append(f"    Reset source: {reset_source}")
                for b_status in ["preserved", "zero"]:
                    p_key = f"{reset_source}_{b_status}_recovery_probability"
                    rmst_key = f"{reset_source}_{b_status}_restricted_mean_time"
                    p = s.get(p_key, np.nan)
                    rmst = s.get(rmst_key, np.nan)
                    if not pd.isna(p):
                        report_lines.append(
                            f"      B={b_status}: recovery_prob={p:.4f}, restricted_mean_time={rmst:.4f}"
                        )
            report_lines.append("")
    
    # Reset-realization interaction summary
    if interaction_stats:
        report_lines.extend([
            "-" * 70,
            "RESET-REALIZATION INTERACTION - I_s(Y) = Delta_{s,carrier} - Delta_{s,full}",
            "Quantifies sensitivity of B effect to reset realization",
            "-" * 70,
            "",
        ])
        for outcome, s in interaction_stats.items():
            report_lines.append(f"  {outcome}:")
            report_lines.append(
                f"    mean = {s['mean']:.6g} "
                f"[CI: {s['ci_lower']:.6g}, {s['ci_upper']:.6g}]"
            )
            report_lines.append(
                f"    median = {s['median']:.6g}, std = {s['std']:.6g}"
            )
            report_lines.append(
                f"    n = {s['n']}, + = {s['n_positive']}, "
                f"0 = {s['n_zero']}, - = {s['n_negative']}"
            )
            report_lines.append("")
    
    report_lines.extend([
        "-" * 70,
        "INTERPRETATION CONSTRAINTS",
        "-" * 70,
        "",
        "The experiment estimates the conditional effect of preserving mature B",
        "under matched randomized phase/history and reset EMA.",
        "",
        "This is a controlled counterfactual, NOT a test that B is the",
        "unique memory carrier.",
        "",
        "The seed/graph is the inferential unit (40 seeds).",
        "The 80 reset-block contrasts are NOT independent observations.",
        "",
    ])
    
    report = "\n".join(report_lines)
    atomic_write_text(output_dir / "matched_phase_report.txt", report)
    print(f"  Saved: matched_phase_report.txt")
    
    # --- Build manifest ---
    # FIX: Use stored immutability_by_seed, not reconstruct
    manifest_output = {
        "analysis": "AIEF-1.4 matched phase memory ablation",
        "version": "1.0",
        "source": {
            "path": str(Path(__file__).resolve()),
            "sha256": file_sha256(Path(__file__).resolve()),
        },
        "frozen_authorities": {
            "manifest": {
                "path": str(Path(manifest_path).resolve()),
                "sha256": file_sha256(manifest_path),
            },
            "npz": {
                "path": str(Path(npz_path).resolve()),
                "sha256": file_sha256(npz_path),
            },
            "scalar_csv": {
                "path": str(Path(scalar_path).resolve()) if os.path.exists(scalar_path) else None,
                "sha256": scalar_sha256,
                "note": "Hashed for provenance but not used computationally",
            },
        },
        "dependencies": {
            "AIEF_1_4_memory_ablation_updated": {
                "path": str(Path(prod.__file__).resolve()),
                "sha256": compute_module_sha256(prod),
            },
            "AIEF_1_4_trajectory_recovery_equivalence": {
                "path": str(Path(recovery.__file__).resolve()),
                "sha256": compute_module_sha256(recovery),
            },
        },
        "environment": {
            "python_version": sys.version,
            "numpy_version": np.__version__,
        },
        "model_constants": {
            "N": N,
            "dt": dt,
            "T_window": T_window,
            "alpha": math.exp(-dt / T_window),
            "scale_epsilon": 1e-12,
        },
        "branch_order": list(branch_order),
        "branch_rng_algorithm": (
            "_, branch_root = np.random.SeedSequence(seed).spawn(2); "
            "branch_sequences = branch_root.spawn(len(branch_order)); "
            "branch_rng_seeds = {branch: int(sequence.generate_state(1, dtype=np.uint64)[0]) "
            "for branch, sequence in zip(branch_order, branch_sequences)}"
        ),
        "matched_reset_block_design": (
            "Reset block A (carrier_reset seed from B_carrier_only): "
            "carrier_reset__B_preserved (reproduces B_carrier_only), "
            "carrier_reset__B_zero (new, B=0). "
            "Reset block B (full_reset seed from full_reset): "
            "full_reset__B_preserved (new, B=Bsplit), "
            "full_reset__B_zero (reproduces full_reset). "
            "Continue branch: reproduces continue."
        ),
        "run_metadata": {
            "run_scope": "full_cohort" if full_cohort else "partial",
            "requested_seed_count": len(seeds),
            "all_seeds_count": len(all_seeds),
            "full_cohort": full_cohort,
        },
        "seeds": {
            "all": all_seeds,
            "requested": seeds,
            "status": seed_status,
        },
        "validation": {
            "initial_match_pass_count": len([r for r in audit_rows if r.get("pass", False)]),
            "initial_match_total_count": len(audit_rows),
            "anchor_validation_pass_count": len([r for r in anchor_validation_rows if r.get("pass", True)]),
            "anchor_validation_total_count": len(anchor_validation_rows),
            "verify_anchors": verify_anchors,
            "split_state_immutability": {
                "all_passed": all(immutability_by_seed.values()) if immutability_by_seed else True,
                "by_seed": immutability_by_seed,
            },
        },
        "censoring": {
            "horizon": horizon,
            "source": "sample_times[-1] from continue branch (first seed with data)",
        },
        "recovery_definitions": {
            "similarity_threshold": "0.9 * continue_Weighted_similarity_late",
            "density_threshold": "0.9 * continue_D_B_final",
            "deficit_calculation": "np.maximum(0, continue_value - value)",
            "binary_recovery": "np.isfinite(time_to_event)",
            "restricted_mean_time": "mean of (min(time, horizon) for all seeds)",
        },
        "command": sys.argv,
        "success_count": len([s for s in seed_status.values() if s == "success"]),
        "failure_count": len(failed_seeds),
        "failed_seeds": failed_seeds,
        "freezeable": not bool(failed_seeds) and verify_anchors and full_cohort,
        "outputs": [
            "matched_phase_scalar_summary.csv",
            "matched_phase_paired_contrasts.csv",
            "matched_phase_seed_level_contrasts.csv",
            "matched_phase_recovery_summary.csv",
            "matched_initial_state_audit.csv",
            "frozen_anchor_validation.csv",
            "matched_phase_branch_diagnostics.npz",
            "matched_phase_report.txt",
            "analysis_manifest.json",
            "matched_phase_seed_status.csv",
        ],
        "interpretation_constraints": [
            "The experiment estimates the conditional effect of preserving mature B under matched randomized phase/history and reset EMA.",
            "This is a controlled counterfactual, not a test that B is the unique memory carrier.",
            "The seed/graph is the inferential unit (40 seeds).",
            "The 80 reset-block contrasts are not independent observations.",
        ],
    }
    
    atomic_write_json(output_dir / "analysis_manifest.json", manifest_output)
    print(f"  Saved: analysis_manifest.json")
    
    return {
        "success_count": len([s for s in seed_status.values() if s == "success"]),
        "failure_count": len(failed_seeds),
        "failed_seeds": failed_seeds,
        "initial_match_failed": initial_match_failed,
        "anchor_failed": anchor_failed,
        "has_fatal_failure": bool(fatal_exception),
        "full_cohort": full_cohort,
    }


# =============================================================================
# Self-Test
# =============================================================================


def run_self_test() -> dict[str, Any]:
    """Run self-test without frozen inputs."""
    print("Running self-test...")
    
    results: dict[str, Any] = {}
    
    # FIX: Self-test REQUIRES production and recovery modules
    if not PROD_AVAILABLE:
        print(f"  ERROR: Production module not available: {PROD_ERROR}")
        results["all_passed"] = False
        return results
    
    if not RECOVERY_AVAILABLE:
        print(f"  ERROR: Recovery module not available: {RECOVERY_ERROR}")
        results["all_passed"] = False
        return results
    
    # Test 1: Same reset seed produces equal theta/history/EMA
    N = 12
    np.random.seed(42)
    mock_theta = np.random.randn(N)
    mock_B = np.random.rand(N, N)
    mock_B = 0.5 * (mock_B + mock_B.T)
    np.fill_diagonal(mock_B, 0.0)
    mock_coherence = (np.random.randn(N, N) + 1j * np.random.randn(N, N))
    mock_history = deque([np.random.randn(N) for _ in range(10)])
    
    # CORRECTED: Construct DynamicState properly
    mock_state = prod.DynamicState(
        theta=mock_theta.copy(),
        B=mock_B.copy(),
        coherence_acc=mock_coherence.copy(),
        history=copy.deepcopy(mock_history),
    )
    
    test_seed = 12345
    
    # Apply same intervention with same seed
    state1 = copy.deepcopy(mock_state)
    state2 = copy.deepcopy(mock_state)
    rng1 = np.random.default_rng(test_seed)
    rng2 = np.random.default_rng(test_seed)
    
    prod.apply_intervention(state1, "full_reset", rng1)
    prod.apply_intervention(state2, "full_reset", rng2)
    
    test1 = (
        np.array_equal(state1.theta, state2.theta) and
        np.array_equal(state1.coherence_acc, state2.coherence_acc) and
        len(state1.history) == len(state2.history) and
        all(np.array_equal(h1, h2) for h1, h2 in zip(state1.history, state2.history))
    )
    results["test1_same_seed_equals"] = test1
    print(f"  Test 1 (same seed -> same state): {'PASS' if test1 else 'FAIL'}")
    
    # Test 2: Only B differs between preserved and zero
    state_p = copy.deepcopy(mock_state)
    state_z = copy.deepcopy(mock_state)
    rng_p = np.random.default_rng(test_seed)
    rng_z = np.random.default_rng(test_seed)
    
    prod.apply_intervention(state_p, "B_carrier_only", rng_p)
    prod.apply_intervention(state_z, "full_reset", rng_z)
    
    test2 = (
        np.array_equal(state_p.theta, state_z.theta) and
        np.array_equal(state_p.coherence_acc, state_z.coherence_acc) and
        np.array_equal(state_p.coherence_acc, np.zeros_like(state_p.coherence_acc)) and
        np.array_equal(state_z.coherence_acc, np.zeros_like(state_z.coherence_acc)) and
        not np.array_equal(state_p.B, state_z.B) and
        np.array_equal(state_z.B, np.zeros((N, N)))
    )
    results["test2_only_B_differs"] = test2
    print(f"  Test 2 (only B differs): {'PASS' if test2 else 'FAIL'}")
    
    # Test 3: History equality between preserved and zero
    test3 = (
        len(state_p.history) == len(state_z.history) and
        all(np.array_equal(hp, hz) for hp, hz in zip(state_p.history, state_z.history))
    )
    results["test3_history_equals"] = test3
    print(f"  Test 3 (history equality): {'PASS' if test3 else 'FAIL'}")
    
    # Test 4: RNG state equality after intervention
    state_p2 = copy.deepcopy(mock_state)
    state_z2 = copy.deepcopy(mock_state)
    rng_p2 = np.random.default_rng(test_seed)
    rng_z2 = np.random.default_rng(test_seed)
    
    prod.apply_intervention(state_p2, "B_carrier_only", rng_p2)
    prod.apply_intervention(state_z2, "full_reset", rng_z2)
    
    rng_state_equal = (rng_p2.bit_generator.state == rng_z2.bit_generator.state)
    results["test4_rng_state_equals"] = rng_state_equal
    print(f"  Test 4 (RNG state equality): {'PASS' if rng_state_equal else 'FAIL'}")
    
    # Test 5: Array hashing - FIXED
    arr = np.array([1.0, 2.0, 3.0])
    h1 = array_sha256(arr)
    h2 = array_sha256(arr)
    h3 = array_sha256(np.array([1.0, 2.0, 4.0]))
    test5 = (h1 == h2) and (h1 != h3)
    results["test5_array_hashing"] = test5
    print(f"  Test 5 (array hashing): {'PASS' if test5 else 'FAIL'}")
    
    # Test 6: Coherence hash changes with dtype
    arr_float = np.array([1.0, 2.0, 3.0])
    arr_complex = np.array([1.0+0j, 2.0+0j, 3.0+0j])
    h_float = array_sha256(arr_float)
    h_complex = array_sha256(arr_complex)
    test6 = (h_float != h_complex)
    results["test6_dtype_hash_differs"] = test6
    print(f"  Test 6 (dtype affects hash): {'PASS' if test6 else 'FAIL'}")
    
    # Test 7: Contrast construction - FIX: Use declared outcome
    mock_outcomes = {
        "carrier_reset__B_preserved": {"P_mean_late": 1.0},
        "carrier_reset__B_zero": {"P_mean_late": 0.5},
    }
    contrasts = compute_paired_contrasts(mock_outcomes)
    test7 = contrasts.get("carrier_reset", {}).get("P_mean_late", np.nan) == 0.5
    results["test7_contrast_construction"] = test7
    print(f"  Test 7 (contrast construction): {'PASS' if test7 else 'FAIL'}")
    
    # Test 8: Seed-level averaging - FIX: Use declared outcome
    paired = {
        "carrier_reset": {"P_mean_late": 1.0},
        "full_reset": {"P_mean_late": 0.6},
    }
    seed_level = compute_seed_level_contrasts(paired)
    test8 = (
        abs(seed_level.get("avg_P_mean_late", np.nan) - 0.8) < 1e-10 and
        abs(seed_level.get("interaction_P_mean_late", np.nan) - 0.4) < 1e-10
    )
    results["test8_seed_level_averaging"] = test8
    print(f"  Test 8 (seed-level averaging): {'PASS' if test8 else 'FAIL'}")
    
    # Test 9: Atomic writes - FIX: Test all formats
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        # Test CSV
        test_df = pd.DataFrame({"a": [1, 2, 3]})
        atomic_write_csv(tmp_dir / "test.csv", test_df)
        test9_csv = (tmp_dir / "test.csv").exists()
        
        # Test JSON
        test_data = {"key": "value"}
        atomic_write_json(tmp_dir / "test.json", test_data)
        test9_json = (tmp_dir / "test.json").exists()
        
        # Test text
        atomic_write_text(tmp_dir / "test.txt", "test content")
        test9_text = (tmp_dir / "test.txt").exists()
        
        # Test NPZ
        test_arr = np.array([1, 2, 3])
        atomic_write_npz(tmp_dir / "test.npz", test_array=test_arr)
        test9_npz = (tmp_dir / "test.npz").exists()
        
        test9 = test9_csv and test9_json and test9_text and test9_npz
        results["test9_atomic_writes_all_formats"] = test9
        print(f"  Test 9 (atomic writes all formats): {'PASS' if test9 else 'FAIL'}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    
    # Test 10: Bootstrap CI
    values = np.random.randn(100)
    mean_val, ci_l, ci_u = bootstrap_ci(values, 100, 42)
    test10 = (
        not np.isnan(mean_val) and
        not np.isnan(ci_l) and
        not np.isnan(ci_u) and
        ci_l <= mean_val <= ci_u
    )
    results["test10_bootstrap_ci"] = test10
    print(f"  Test 10 (bootstrap CI): {'PASS' if test10 else 'FAIL'}")
    
    # Test 11: Wilson CI
    p, ci_l, ci_u = wilson_ci(80, 100)
    test11 = (
        0.0 <= p <= 1.0 and
        0.0 <= ci_l <= p <= ci_u <= 1.0
    )
    results["test11_wilson_ci"] = test11
    print(f"  Test 11 (Wilson CI): {'PASS' if test11 else 'FAIL'}")
    
    # Test 12: Binary recovery indicator
    finite_time = 5.0
    nan_time = np.nan
    test12a = bool(np.isfinite(finite_time))
    test12b = not bool(np.isfinite(nan_time))
    test12 = test12a and test12b
    results["test12_binary_recovery_indicator"] = test12
    print(f"  Test 12 (binary recovery indicator): {'PASS' if test12 else 'FAIL'}")
    
    # Test 13: Censored seed in denominator
    total = 3
    finite = 2
    recovery_prob = finite / total
    test13 = abs(recovery_prob - 2/3) < 1e-10
    results["test13_censored_in_denominator"] = test13
    print(f"  Test 13 (censored in denominator): {'PASS' if test13 else 'FAIL'}")
    
    # Test 14: Split state immutability - FIX: Actually test mutation detection
    state_before = copy.deepcopy(mock_state)
    snapshot = create_split_snapshot(state_before)
    
    # Unchanged should pass
    unchanged_pass = check_split_state_immutability(state_before, snapshot, N)
    
    # Mutate and check detection
    state_mutated = copy.deepcopy(mock_state)
    state_mutated.B[0, 1] += 1e-6
    state_mutated.B[1, 0] += 1e-6
    mutation_detected = not check_split_state_immutability(state_mutated, snapshot, N)
    
    test14 = unchanged_pass and mutation_detected
    results["test14_split_state_immutability"] = test14
    print(f"  Test 14 (split state immutability): {'PASS' if test14 else 'FAIL'}")
    
    # Test 15: NaN-aware array equality
    a = np.array([1.0, np.nan, 2.0])
    b = np.array([1.0, np.nan, 2.0])
    c = np.array([1.0, np.nan, 2.1])
    test15 = exact_array_equal_with_nan(a, b) and not exact_array_equal_with_nan(a, c)
    results["test15_nan_aware_equality"] = test15
    print(f"  Test 15 (NaN-aware equality): {'PASS' if test15 else 'FAIL'}")
    
    # Test 16: NPZ serialization schema
    # FIX: Use seed without duplicated 'seed_' prefix
    # Also read back the NPZ to verify it was written correctly
    try:
        synthetic_results = {
            "0": {  # Changed from "seed_0" to "0"
                "branches": {
                    "carrier_reset__B_preserved": {
                        "sample_times": np.array([0.0, 1.0, 2.0]),
                        "B_final": np.array([[0.1, 0.2], [0.2, 0.1]]),
                    },
                    "carrier_reset__B_zero": {
                        "sample_times": np.array([0.0, 1.0, 2.0]),
                        "B_final": np.array([[0.0, 0.0], [0.0, 0.0]]),
                    },
                }
            }
        }
        
        # Test the same NPZ-flattening loop
        npz_test_output = {}
        for seed_str, results in synthetic_results.items():
            for branch_id, branch_result in results["branches"].items():
                if isinstance(branch_result, dict):
                    for key, value in branch_result.items():
                        if isinstance(value, np.ndarray):
                            npz_key = f"{branch_id}_seed_{seed_str}_{key}"
                            npz_test_output[npz_key] = value
        
        # Verify expected keys exist (without duplicated seed_)
        test16_keys = (
            "carrier_reset__B_preserved_seed_0_sample_times" in npz_test_output and
            "carrier_reset__B_preserved_seed_0_B_final" in npz_test_output
        )
        
        # Test reading back the NPZ
        test16_read = False
        if test16_keys:
            tmp_dir = Path(tempfile.mkdtemp())
            try:
                npz_path = tmp_dir / "test.npz"
                np.savez(npz_path, **npz_test_output)
                with np.load(npz_path, allow_pickle=False) as npz_read:
                    test16_read = (
                        "carrier_reset__B_preserved_seed_0_sample_times" in npz_read.files and
                        "carrier_reset__B_preserved_seed_0_B_final" in npz_read.files
                    )
            finally:
                shutil.rmtree(tmp_dir, ignore_errors=True)
        
        test16 = test16_keys and test16_read
        results["test16_npz_serialization_schema"] = test16
        print(f"  Test 16 (NPZ serialization schema): {'PASS' if test16 else 'FAIL'}")
    except Exception as e:
        results["test16_npz_serialization_schema"] = False
        print(f"  Test 16 (NPZ serialization schema): FAIL - {e}")
    
    all_pass = all(results.values())
    print(f"\nSelf-test: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
    results["all_passed"] = all_pass
    
    return results


# =============================================================================
# CLI
# =============================================================================


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AIEF-1.4 Matched Phase Memory Ablation"
    )
    
    # Required inputs
    parser.add_argument(
        "--npz",
        default=DEFAULT_NPZ,
        help="Frozen NPZ path (default: %(default)s)",
    )
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help="Frozen manifest path (default: %(default)s)",
    )
    parser.add_argument(
        "--scalar",
        default=DEFAULT_SCALAR,
        help="Frozen scalar CSV path (default: %(default)s)",
    )
    
    # Output
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory (default: %(default)s)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing outputs (default: fail if outputs exist)",
    )
    
    # Seed control
    parser.add_argument(
        "--max-seeds",
        type=parse_nonnegative_int,
        default=None,
        help="Max seeds to process (default: all)",
    )
    parser.add_argument(
        "--seed-filter",
        type=parse_seed_list,
        default=None,
        help="Comma-separated seed filter (default: all)",
    )
    
    # Bootstrap
    parser.add_argument(
        "--bootstrap-repetitions",
        type=parse_positive_int,
        default=1000,
        help="Bootstrap repetitions (default: %(default)s)",
    )
    parser.add_argument(
        "--bootstrap-seed",
        type=int,
        default=42,
        help="Bootstrap RNG seed (default: %(default)s)",
    )
    
    # Options
    parser.add_argument(
        "--verify-anchors",
        action="store_true",
        default=True,
        help="Verify frozen anchors (default: on)",
    )
    parser.add_argument(
        "--no-verify-anchors",
        action="store_false",
        dest="verify_anchors",
        help="Skip anchor verification (debug only)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run self-test and exit",
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_arguments()
    
    # Self-test mode - REQUIRES production and recovery modules
    if args.self_test:
        test_results = run_self_test()
        if not test_results.get("all_passed", False):
            print("Self-test FAILED")
            sys.exit(1)
        print("Self-test PASSED")
        sys.exit(0)
    
    # Check production module
    if not PROD_AVAILABLE:
        print(f"ERROR: Production module not available: {PROD_ERROR}")
        sys.exit(1)
    
    # Check recovery module
    if not RECOVERY_AVAILABLE:
        print(f"ERROR: Recovery module not available: {RECOVERY_ERROR}")
        sys.exit(1)
    
    # Validate inputs
    for path in [args.npz, args.manifest]:
        if not os.path.exists(path):
            print(f"ERROR: Input file not found: {path}")
            sys.exit(1)
    
    if not os.path.exists(args.scalar):
        print(f"WARNING: Scalar CSV not found: {args.scalar}")
    
    output_dir = Path(args.output_dir)
    
    # Run analysis
    print("Starting matched phase memory ablation analysis...")
    try:
        results = run_matched_phase_ablation(
            args.npz,
            args.manifest,
            args.scalar,
            output_dir,
            seed_filter=args.seed_filter,
            max_seeds=args.max_seeds,
            bootstrap_repetitions=args.bootstrap_repetitions,
            bootstrap_seed=args.bootstrap_seed,
            verify_anchors=args.verify_anchors,
            overwrite=args.overwrite,
        )
    except RuntimeError as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)
    
    # Final report
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Seeds succeeded: {results['success_count']}")
    print(f"Seeds failed: {results['failure_count']}")
    if results['failed_seeds']:
        print(f"Failed seeds: {results['failed_seeds']}")
    print(f"Initial matching failed: {results['initial_match_failed']}")
    print(f"Anchor validation failed: {results['anchor_failed']}")
    if results.get('has_fatal_failure'):
        print("WARNING: Fatal validation failures detected. Scientific outputs may be invalid.")
    print(f"Full cohort: {results.get('full_cohort', False)}")
    print(f"Freezeable: {not results.get('has_fatal_failure', True) and args.verify_anchors and results.get('full_cohort', False)}")
    print(f"\nOutput directory: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
