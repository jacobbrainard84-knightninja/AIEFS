#!/usr/bin/env python3
"""AIEF-1.4 T_window Sensitivity Study Analysis Driver v3.

Correct implementation of the prespecified estimands:

1. Regime contrasts: Δ_{s,ρ}^regime(Y) = Y_{s,ρ,continue} - Y_{s,1,continue}
2. Branch DID: I_{s,ρ,b}(Y) = [Y_{s,ρ,b} - Y_{s,ρ,continue}] - [Y_{s,1,b} - Y_{s,1,continue}]
3. Cross-T topology: S_{s,ρ} = cos(B_final_{s,ρ,continue}, B_final_{s,1,continue})
4. Recovery scaling: t_rec / T_window for both horizon systems

Output:
- twindow_paired_regime_contrasts.csv
- twindow_branch_interactions.csv
- twindow_cross_condition_topology.csv
- twindow_recovery_summary.csv
- twindow_sensitivity_report.txt
- analysis_manifest.json

This script implements the 5-stage analysis structure as specified.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# =============================================================================
# Configuration
# =============================================================================

ANALYSIS_VERSION = "v3.0"
STUDY_NAME = "AIEF_1_4_Twindow_sensitivity"

# Expected values (for validation)
EXPECTED_N_SEEDS = 40
EXPECTED_RHO_VALUES = (0.5, 0.75, 1.0, 1.5, 2.0)
EXPECTED_BRANCHES = ("continue", "reset_ema", "reset_B", "future_shuffle")

# P1 #4: Expected frozen baseline branches for certificate validation
EXPECTED_FROZEN_BASELINE_BRANCHES = (
    "continue",
    "reset_ema",
    "reset_B",
    "reset_B_ema",
    "B_carrier_only",
    "full_reset",
    "future_shuffle",
)

# Primary outcomes - FIXED-PHYSICAL HORIZONS (corrected from legacy)
PRIMARY_OUTCOMES = (
    "Weighted_similarity_late_fixed_physical",
    "Retention_contrast_late_fixed_physical",
    "P_mean_late_fixed_physical",
)

# Secondary outcomes - NORMALIZED EMA HORIZONS
SECONDARY_NORMALIZED_OUTCOMES = (
    "Weighted_similarity_late_normalized_EMA",
    "Retention_contrast_late_normalized_EMA", 
    "P_mean_late_normalized_EMA",
)

# Non-continue branches for DID
NON_CONTINUE_BRANCHES = ("reset_ema", "reset_B", "future_shuffle")

# Expected counts
EXPECTED_N_CONDITIONS = EXPECTED_N_SEEDS * len(EXPECTED_RHO_VALUES)
EXPECTED_N_ROWS = EXPECTED_N_CONDITIONS * len(EXPECTED_BRANCHES)
EXPECTED_N_REGIME_CONTRASTS = EXPECTED_N_SEEDS * (len(EXPECTED_RHO_VALUES) - 1) * len(PRIMARY_OUTCOMES)
EXPECTED_N_DID = EXPECTED_N_SEEDS * (len(EXPECTED_RHO_VALUES) - 1) * (len(EXPECTED_BRANCHES) - 1) * len(PRIMARY_OUTCOMES)
EXPECTED_N_TOPOLOGY = EXPECTED_N_SEEDS * (len(EXPECTED_RHO_VALUES) - 1)

# Recovery DID expected count: 40 seeds * 4 non-baseline rho * 3 non-continue branches * 2 systems * 2 metrics * 13 outcomes = 24960
EXPECTED_N_RECOVERY_DID = EXPECTED_N_SEEDS * (len(EXPECTED_RHO_VALUES) - 1) * len(NON_CONTINUE_BRANCHES) * 2 * 2 * 13

# Recovery groups: 5 rho * 4 branches * 2 systems * 2 metrics = 80 groups
EXPECTED_N_RECOVERY_GROUPS = len(EXPECTED_RHO_VALUES) * len(EXPECTED_BRANCHES) * 2 * 2

# Recovery DID groups: 4 rho * 3 branches * 2 systems * 2 metrics * 13 outcomes = 624 groups
EXPECTED_N_RECOVERY_DID_GROUPS = (len(EXPECTED_RHO_VALUES) - 1) * len(NON_CONTINUE_BRANCHES) * 2 * 2 * 13

# Censoring-aware fields that must have 40 finite values per group
RESTRICTED_RECOVERY_FIELDS = (
    "restricted_first_crossing_time",
    "restricted_sustained_time",
    "restricted_held_time",
    "restricted_first_over_Twindow",
    "restricted_sustained_over_Twindow",
    "restricted_held_over_Twindow",
    "auc_deficit_vs_continue",
    "first_crossing_observed",
    "sustained_observed",
    "held_observed",
)

# P0 Issue 2: Recovery DID outcome classification for n validation
# Full-cohort outcomes must have n=40 (all seeds present)
FULL_COHORT_RECOVERY_DID_OUTCOMES = {
    "restricted_first_crossing_time",
    "restricted_sustained_time",
    "restricted_held_time",
    "restricted_first_over_Twindow",
    "restricted_sustained_over_Twindow",
    "restricted_held_over_Twindow",
    "auc_deficit_vs_continue",
    "first_crossing_observed",
    "sustained_observed",
    "held_observed",
}

# Conditional outcomes may have n<40 due to censoring (NaN values excluded from count)
CONDITIONAL_RECOVERY_DID_OUTCOMES = {
    "first_crossing_over_Twindow",
    "sustained_time_over_Twindow",
    "held_time_over_Twindow",
}

# P2: Assert recovery-DID outcome classification is complete at module import
ALL_RECOVERY_DID_OUTCOMES = FULL_COHORT_RECOVERY_DID_OUTCOMES | CONDITIONAL_RECOVERY_DID_OUTCOMES
if len(ALL_RECOVERY_DID_OUTCOMES) != 13:
    raise RuntimeError(
        "Recovery DID outcome classification must contain exactly 13 outcomes"
    )
if FULL_COHORT_RECOVERY_DID_OUTCOMES & CONDITIONAL_RECOVERY_DID_OUTCOMES:
    raise RuntimeError(
        "Recovery DID full-cohort and conditional outcome sets overlap"
    )

# Expected sample time schedule for trajectory validation
# 640 samples from 0.01 to 319.51 with step 0.5
EXPECTED_SAMPLE_TIMES = (np.arange(0, 32000, 50, dtype=float) + 1.0) * 0.01
EXPECTED_N_SAMPLES = len(EXPECTED_SAMPLE_TIMES)


# =============================================================================
# Utility Functions
# =============================================================================

def load_csv_atomic(path: str | Path) -> pd.DataFrame:
    """Load CSV file atomically with validation."""
    path = Path(path)
    
    # Use pandas with explicit dtypes
    df = pd.read_csv(
        path,
        dtype={"seed": str, "branch": str},  # Keep seeds as strings
    )
    
    # Convert numeric columns, coercing errors to NaN
    for col in df.columns:
        if col not in ("seed", "seed_index", "branch", "rho"):
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            except Exception:
                pass
    
    return df


def load_npz_selective(path: str | Path, keys: list[str] | None = None) -> dict[str, Any]:
    """Load only specified keys from NPZ file to save memory.
    
    Raises RuntimeError on corrupt NPZ or load failure.
    """
    path = Path(path)
    payload: dict[str, Any] = {}
    
    if not path.exists():
        raise FileNotFoundError(f"NPZ file not found: {path}")
    
    try:
        with np.load(str(path), allow_pickle=False) as data:
            if keys is None:
                keys = list(data.files)
            for key in keys:
                if key in data:
                    value = data[key]
                    payload[key] = value.item() if value.ndim == 0 else value.copy()
    except Exception as e:
        raise RuntimeError(f"Could not load NPZ {path}: {e}") from e
    
    return payload


def save_csv_atomic(path: str | Path, df: pd.DataFrame) -> None:
    """Save CSV atomically with fsync."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    temp_path = path.with_suffix(path.suffix + f".tmp-{os.getpid()}-{time.time_ns()}")
    try:
        # Write CSV with explicit flush and fsync for data integrity
        with open(temp_path, "w", encoding="utf-8", newline="") as handle:
            df.to_csv(handle, index=False)
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(path)
        # fsync the directory to ensure the replace is visible
        dir_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def save_text_atomic(path: str | Path, text: str) -> None:
    """Save text file atomically with fsync."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    temp_path = path.with_suffix(path.suffix + f".tmp-{os.getpid()}-{time.time_ns()}")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        temp_path.replace(path)
        # fsync the directory
        dir_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def save_json_atomic(path: str | Path, data: dict[str, Any]) -> None:
    """Save JSON atomically with fsync, handling NaN values."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert NaN and infinity to None for JSON serialization
    # Recursively handles nested structures including numpy arrays
    def sanitize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitize(v) for v in obj]
        elif isinstance(obj, tuple):
            return tuple(sanitize(v) for v in obj)
        elif isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return obj
        elif isinstance(obj, (np.integer, np.floating)):
            val = obj.item()
            if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
                return None
            return val
        elif isinstance(obj, np.ndarray):
            # Convert to list and recursively sanitize to preserve structure
            return sanitize(obj.tolist())
        else:
            return obj
    
    temp_path = path.with_suffix(path.suffix + f".tmp-{os.getpid()}-{time.time_ns()}")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(sanitize(data), f, indent=2, sort_keys=True, allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        temp_path.replace(path)
        # fsync the directory
        dir_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def file_sha256(path: str | Path) -> str:
    """Compute SHA-256 hash of a file."""
    import hashlib as hl
    digest = hl.sha256()
    path = Path(path)
    if not path.exists():
        return "FILE_NOT_FOUND"
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


# =============================================================================
# Metric Functions
# =============================================================================

def first_crossing_time(times: np.ndarray, values: np.ndarray, threshold: float) -> tuple[float, bool]:
    """Find first time when values cross above threshold.
    
    Returns (first_crossing_time, observed).
    """
    times = np.asarray(times, dtype=float)
    values = np.asarray(values, dtype=float)
    
    # Handle NaN values by treating them as below threshold
    above_threshold = (np.isfinite(values) & (values >= threshold))
    
    crossing_indices = np.flatnonzero(above_threshold)
    
    if len(crossing_indices) > 0:
        return float(times[crossing_indices[0]]), True
    else:
        return float('nan'), False


def first_time_sustained_for_rest(times: np.ndarray, values: np.ndarray, threshold: float) -> tuple[float, bool]:
    """Find earliest time after which values stay above threshold for rest of trajectory.
    
    Returns (sustained_time, observed).
    """
    times = np.asarray(times, dtype=float)
    values = np.asarray(values, dtype=float)
    
    # Handle NaN values by treating them as below threshold
    condition = (np.isfinite(values) & (values >= threshold))
    
    # Check from the end backwards: find first index where all subsequent values are above threshold
    suffix_all = np.logical_and.accumulate(condition[::-1])[::-1]
    
    sustained_indices = np.flatnonzero(suffix_all)
    
    if len(sustained_indices) > 0:
        return float(times[sustained_indices[0]]), True
    else:
        return float('nan'), False


def first_time_held_for_duration(times: np.ndarray, values: np.ndarray, threshold: float, duration: float) -> tuple[float, bool]:
    """Find earliest time after which values stay above threshold for at least the specified duration.
    
    Returns (held_time, observed).
    """
    times = np.asarray(times, dtype=float)
    values = np.asarray(values, dtype=float)
    
    if len(times) < 2:
        return float('nan'), False
    
    # Calculate sample step
    sample_step = float(times[1] - times[0])
    if sample_step <= 0:
        return float('nan'), False
    
    # Required number of consecutive samples
    required_samples = max(1, int(np.ceil(duration / sample_step)))
    
    # Handle NaN values by treating them as below threshold
    condition = (np.isfinite(values) & (values >= threshold))
    
    # Use sliding window to find runs of sufficient length
    held_time = float('nan')
    observed = False
    
    for i in range(len(condition) - required_samples + 1):
        window = condition[i:i + required_samples]
        if np.all(window):
            held_time = float(times[i])
            observed = True
            break
    
    return held_time, observed


def trapezoidal_auc_deficit(times: np.ndarray, reference: np.ndarray, target: np.ndarray) -> float:
    """Calculate one-sided AUC deficit: integral of max(0, reference - target) using trapezoidal rule.
    
    Handles NaN values by treating them as zero for the deficit calculation.
    Uses np.trapezoid if available, falls back to np.trapz for older NumPy versions.
    
    NaN cosine values (from zero-vector weights) are imputed as zero for recovery
    and AUC calculations only - this is a prespecified recovery-only convention.
    """
    times = np.asarray(times, dtype=float)
    reference = np.asarray(reference, dtype=float)
    target = np.asarray(target, dtype=float)
    
    if len(times) < 2:
        return float('nan')
    
    # Calculate one-sided deficit: max(0, reference - target)
    # Handle NaN by replacing with 0 (prespecified recovery-only convention for undefined zero-vector cosine)
    ref_safe = np.where(np.isfinite(reference), reference, 0.0)
    tgt_safe = np.where(np.isfinite(target), target, 0.0)
    deficit = np.maximum(0.0, ref_safe - tgt_safe)
    
    # Trapezoidal integration - use np.trapezoid if available, else np.trapz
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(deficit, x=times))
    return float(np.trapz(deficit, x=times))


def cosine_similarity(B1: np.ndarray, B2: np.ndarray) -> float:
    """Compute cosine similarity between two B matrices over upper triangle edges."""
    edges = np.triu_indices(B1.shape[0], k=1)
    x = B1[edges]
    y = B2[edges]
    
    norm_x = np.linalg.norm(x)
    norm_y = np.linalg.norm(y)
    
    if norm_x <= 1e-12 or norm_y <= 1e-12:
        return float('nan')
    
    return float(np.dot(x, y) / (norm_x * norm_y))


def jaccard_similarity(B1: np.ndarray, B2: np.ndarray, threshold: float) -> float:
    """Compute Jaccard similarity between two B matrices over upper triangle edges."""
    edges = np.triu_indices(B1.shape[0], k=1)
    x = B1[edges] > threshold
    y = B2[edges] > threshold
    
    union = np.count_nonzero(x | y)
    if union == 0:
        return float('nan')
    
    return float(np.count_nonzero(x & y) / union)


def normalized_distance(B1: np.ndarray, B2: np.ndarray) -> float:
    """Compute normalized L2 distance between two B matrices over upper triangle edges."""
    edges = np.triu_indices(B1.shape[0], k=1)
    x = B1[edges]
    y = B2[edges]
    
    diff = x - y
    norm_diff = np.linalg.norm(diff)
    norm_y = np.linalg.norm(y)
    
    if norm_y <= 1e-12:
        return float('nan')
    
    return float(norm_diff / norm_y)


def validate_topology_matrix(matrix: np.ndarray, key: str) -> np.ndarray:
    """Validate a topology (B_final) matrix for production analysis.
    
    Checks:
    - Shape is exactly (12, 12)
    - All values are finite (no NaN, inf, -inf)
    - Matrix is symmetric (rtol=0, atol=1e-12)
    - Diagonal is exactly zero (rtol=0, atol=1e-12)
    - No negative weights (all values >= -1e-12)
    
    Raises RuntimeError if any check fails.
    """
    matrix = np.asarray(matrix, dtype=float)
    
    if matrix.shape != (12, 12):
        raise RuntimeError(
            f"{key} shape {matrix.shape} != (12, 12)"
        )
    
    if not np.all(np.isfinite(matrix)):
        raise RuntimeError(
            f"{key} contains non-finite values"
        )
    
    if not np.allclose(matrix, matrix.T, rtol=0.0, atol=1e-12):
        raise RuntimeError(f"{key} is not symmetric")
    
    if not np.allclose(np.diag(matrix), 0.0, rtol=0.0, atol=1e-12):
        raise RuntimeError(
            f"{key} diagonal is not zero"
        )
    
    if np.any(matrix < -1e-12):
        raise RuntimeError(
            f"{key} contains negative weights"
        )
    
    return matrix

def compute_recovery_scaling(
    df: pd.DataFrame,
    npz_path: str | Path,
) -> pd.DataFrame:
    """Compute recovery scaling metrics for both horizon systems.
    
    For each seed, rho, branch, and horizon system:
    1. Load: sample_times, density_trajectory, similarity_trajectory
    2. Use the same seed/rho continue branch as reference
    3. Calculate condition-specific targets:
       - Density target: 0.9 * D_B_final_continue (fraction of edges above B_c)
       - Similarity target: 0.9 * S_late_continue (for appropriate horizon system)
    4. Calculate:
       - first_crossing_time: first time metric > target
       - sustained_time: earliest time after which metric stays above target for rest of trajectory
       - held_time: earliest time after which metric stays above target for at least T_window duration
       - censoring indicators for each event type
       - restricted_time: horizon for censored events, event_time for observed events
       - auc_deficit: one-sided integral of (continue_trajectory - branch_trajectory) using trapezoidal rule
       - t_rec / T_window: normalized recovery times
    5. Output separate rows for fixed_physical and normalized_EMA horizon systems
    
    Returns DataFrame with complete recovery metrics.
    """
    # Convert to Path for consistency
    npz_path = Path(npz_path)
    
    # Get unique seeds, rho values, and branches from the data
    seeds = sorted(df["seed"].unique())
    rho_values = sorted([float(r) for r in df["rho"].unique()])
    branches = sorted(df["branch"].unique())
    
    # Build complete list of required keys for all conditions
    # We need: sample_times, density_trajectory, similarity_trajectory for all seed/rho/branch
    all_keys = set()
    for seed in seeds:
        for rho in rho_values:
            for branch in branches:
                prefix = f"{branch}_seed_{seed}_rho_{rho}"
                all_keys.update([
                    f"{prefix}_sample_times",
                    f"{prefix}_density_trajectory", 
                    f"{prefix}_similarity_trajectory",
                ])
    
    # Load all required data in one operation
    print(f"  Loading {len(all_keys)} trajectory arrays from NPZ...")
    npz_data = load_npz_selective(npz_path, keys=list(all_keys))
    
    # Check for missing keys - this should be fatal for production
    missing_keys = [k for k in all_keys if k not in npz_data]
    if missing_keys:
        raise RuntimeError(
            f"Missing trajectory keys in NPZ: {missing_keys[:10]}... "
            f"({len(missing_keys)} total missing). "
            f"This indicates schema mismatch or incomplete simulation."
        )
    
    recovery_rows = []
    
    for seed in seeds:
        for rho in rho_values:
            # Get T_window for this rho from the data
            t_window = float(df[(df["seed"] == seed) & (df["rho"] == rho)]["T_window"].iloc[0])
            
            # Get continue branch reference values for this seed/rho
            cont_row = df[(df["seed"] == seed) & (df["rho"] == rho) & (df["branch"] == "continue")].iloc[0]
            
            # Get reference targets for both horizon systems
            # Density target: 0.9 * D_B_final_continue (fraction of edges above B_c)
            density_target_continue = 0.9 * float(cont_row["D_B_final"])
            
            # Similarity targets for both horizon systems
            similarity_target_fixed = 0.9 * float(cont_row["Weighted_similarity_late_fixed_physical"])
            similarity_target_normalized = 0.9 * float(cont_row["Weighted_similarity_late_normalized_EMA"])
            
            for branch in branches:
                # INCLUDE continue branch for DID calculation
                # For continue: compare trajectory with itself, AUC deficit = 0
                # This makes recovery DID well-defined: [R_{s,ρ,b} - R_{s,ρ,c}] - [R_{s,1,b} - R_{s,1,c}]
                
                prefix = f"{branch}_seed_{seed}_rho_{rho}"
                cont_prefix = f"continue_seed_{seed}_rho_{rho}"
                
                # Load trajectory data
                try:
                    sample_times = np.asarray(npz_data[f"{prefix}_sample_times"], dtype=float)
                    density_trajectory = np.asarray(npz_data[f"{prefix}_density_trajectory"], dtype=float)
                    similarity_trajectory = np.asarray(npz_data[f"{prefix}_similarity_trajectory"], dtype=float)
                    
                    # Load continue (reference) trajectory data
                    cont_sample_times = np.asarray(npz_data[f"{cont_prefix}_sample_times"], dtype=float)
                    cont_density_trajectory = np.asarray(npz_data[f"{cont_prefix}_density_trajectory"], dtype=float)
                    cont_similarity_trajectory = np.asarray(npz_data[f"{cont_prefix}_similarity_trajectory"], dtype=float)
                    
                except Exception as e:
                    raise RuntimeError(f"Error loading trajectory data for seed={seed}, rho={rho}, branch={branch}: {e}")
                
                # P0 #3: Validate trajectory lengths match sample_times
                if not (len(sample_times) == len(density_trajectory) == len(similarity_trajectory)):
                    raise RuntimeError(
                        f"Trajectory length mismatch for seed={seed}, rho={rho}, branch={branch}: "
                        f"times={len(sample_times)}, density={len(density_trajectory)}, similarity={len(similarity_trajectory)}"
                    )
                
                # P0 #3: Also validate that trajectory lengths match between branch and continue
                if len(sample_times) != len(cont_sample_times):
                    raise RuntimeError(
                        f"Sample times length mismatch for seed={seed}, rho={rho}, branch={branch}: "
                        f"branch has {len(sample_times)} times, continue has {len(cont_sample_times)}"
                    )
                if len(density_trajectory) != len(cont_density_trajectory):
                    raise RuntimeError(
                        f"Density trajectory length mismatch for seed={seed}, rho={rho}, branch={branch}: "
                        f"branch has {len(density_trajectory)} points, continue has {len(cont_density_trajectory)}"
                    )
                if len(similarity_trajectory) != len(cont_similarity_trajectory):
                    raise RuntimeError(
                        f"Similarity trajectory length mismatch for seed={seed}, rho={rho}, branch={branch}: "
                        f"branch has {len(similarity_trajectory)} points, continue has {len(cont_similarity_trajectory)}"
                    )
                
                # P0 #4: Validate exact saved-time schedule
                if not np.array_equal(sample_times, EXPECTED_SAMPLE_TIMES):
                    raise RuntimeError(
                        f"Unexpected sample-time schedule for seed={seed}, rho={rho}, branch={branch}. "
                        f"Expected first={EXPECTED_SAMPLE_TIMES[0]}, last={EXPECTED_SAMPLE_TIMES[-1]}, n={EXPECTED_N_SAMPLES}"
                    )
                if not np.array_equal(cont_sample_times, EXPECTED_SAMPLE_TIMES):
                    raise RuntimeError(
                        f"Unexpected continue sample-time schedule for seed={seed}, rho={rho}. "
                        f"Expected first={EXPECTED_SAMPLE_TIMES[0]}, last={EXPECTED_SAMPLE_TIMES[-1]}, n={EXPECTED_N_SAMPLES}"
                    )
                
                # P0 #5: Validate trajectory ranges
                # Density must be finite and in [0, 1]
                if not np.all(np.isfinite(density_trajectory)):
                    raise RuntimeError(
                        f"Density trajectory contains non-finite values for seed={seed}, rho={rho}, branch={branch}"
                    )
                if np.any((density_trajectory < 0.0) | (density_trajectory > 1.0)):
                    raise RuntimeError(
                        f"Density trajectory contains values outside [0,1] for seed={seed}, rho={rho}, branch={branch}"
                    )
                
                # Similarity NaN is permitted for a zero-vector cosine.
                # Infinity is never permitted.
                if np.any(np.isinf(similarity_trajectory)):
                    raise RuntimeError(
                        f"Similarity trajectory contains infinity for "
                        f"seed={seed}, rho={rho}, branch={branch}"
                    )
                finite_similarity = similarity_trajectory[np.isfinite(similarity_trajectory)]
                if len(finite_similarity) > 0 and np.any((finite_similarity < -1.0 - 1e-12) | (finite_similarity > 1.0 + 1e-12)):
                    raise RuntimeError(
                        f"Similarity trajectory contains values outside [-1,1] for seed={seed}, rho={rho}, branch={branch}"
                    )
                
                # Validate continue trajectories as well
                if not np.all(np.isfinite(cont_density_trajectory)):
                    raise RuntimeError(
                        f"Continue density trajectory contains non-finite values for seed={seed}, rho={rho}"
                    )
                if np.any((cont_density_trajectory < 0.0) | (cont_density_trajectory > 1.0)):
                    raise RuntimeError(
                        f"Continue density trajectory contains values outside [0,1] for seed={seed}, rho={rho}"
                    )
                # Similarity NaN is permitted for a zero-vector cosine.
                # Infinity is never permitted.
                if np.any(np.isinf(cont_similarity_trajectory)):
                    raise RuntimeError(
                        f"Continue similarity trajectory contains infinity "
                        f"for seed={seed}, rho={rho}"
                    )
                finite_cont_similarity = cont_similarity_trajectory[np.isfinite(cont_similarity_trajectory)]
                if len(finite_cont_similarity) > 0 and np.any((finite_cont_similarity < -1.0 - 1e-12) | (finite_cont_similarity > 1.0 + 1e-12)):
                    raise RuntimeError(
                        f"Continue similarity trajectory contains values outside [-1,1] for seed={seed}, rho={rho}"
                    )
                
                # Process each horizon system
                for horizon_system, similarity_target in [
                    ("fixed_physical", similarity_target_fixed),
                    ("normalized_EMA", similarity_target_normalized),
                ]:
                    # Process density recovery
                    density_values = density_trajectory
                    density_target = density_target_continue
                    
                    # Calculate first crossing for density
                    density_first_crossing, density_first_observed = first_crossing_time(
                        sample_times, density_values, density_target
                    )
                    
                    # Calculate sustained recovery for density (stays above target for rest of trajectory)
                    density_sustained, density_sustained_observed = first_time_sustained_for_rest(
                        sample_times, density_values, density_target
                    )
                    
                    # Calculate held recovery for density (stays above target for T_window duration)
                    density_held, density_held_observed = first_time_held_for_duration(
                        sample_times, density_values, density_target, t_window
                    )
                    
                    # Calculate AUC deficit for density (one-sided: continue - branch)
                    density_auc_deficit = trapezoidal_auc_deficit(
                        sample_times, cont_density_trajectory, density_values
                    )
                    
                    # Process similarity recovery
                    similarity_values = similarity_trajectory
                    
                    # Calculate first crossing for similarity
                    sim_first_crossing, sim_first_observed = first_crossing_time(
                        sample_times, similarity_values, similarity_target
                    )
                    
                    # Calculate sustained recovery for similarity
                    sim_sustained, sim_sustained_observed = first_time_sustained_for_rest(
                        sample_times, similarity_values, similarity_target
                    )
                    
                    # Calculate held recovery for similarity
                    sim_held, sim_held_observed = first_time_held_for_duration(
                        sample_times, similarity_values, similarity_target, t_window
                    )
                    
                    # Calculate AUC deficit for similarity
                    sim_auc_deficit = trapezoidal_auc_deficit(
                        sample_times, cont_similarity_trajectory, similarity_values
                    )
                    
                    # P1 #10: Calculate discrete held-duration parameters
                    # sample_step is the diagnostic sample spacing (0.5 from EXPECTED_SAMPLE_TIMES)
                    sample_step = float(sample_times[1] - sample_times[0]) if len(sample_times) > 1 else float('nan')
                    required_samples = max(1, int(np.ceil(t_window / sample_step))) if np.isfinite(sample_step) and sample_step > 0 else 0
                    
                    # Calculate restricted times (horizon for censored, event_time for observed)
                    # Use the last sample time as the horizon (not the elapsed difference)
                    horizon_time = float(sample_times[-1]) if len(sample_times) > 0 else float('nan')
                    
                    # P2: Use np.isnan() for semantic clarity - counting NaNs
                    similarity_nan_count = int(np.sum(np.isnan(similarity_trajectory)))
                    cont_similarity_nan_count = int(np.sum(np.isnan(cont_similarity_trajectory)))
                    
                    # For density metrics
                    density_restricted_first = density_first_crossing if density_first_observed else horizon_time
                    density_restricted_sustained = density_sustained if density_sustained_observed else horizon_time
                    density_restricted_held = density_held if density_held_observed else horizon_time
                    
                    # For similarity metrics
                    sim_restricted_first = sim_first_crossing if sim_first_observed else horizon_time
                    sim_restricted_sustained = sim_sustained if sim_sustained_observed else horizon_time
                    sim_restricted_held = sim_held if sim_held_observed else horizon_time
                    
                    # Calculate normalized times (t_rec / T_window)
                    # Raw observed times (conditional on recovery)
                    density_first_over_Twindow = density_first_crossing / t_window if np.isfinite(density_first_crossing) and t_window > 0 else float('nan')
                    density_sustained_over_Twindow = density_sustained / t_window if np.isfinite(density_sustained) and t_window > 0 else float('nan')
                    density_held_over_Twindow = density_held / t_window if np.isfinite(density_held) and t_window > 0 else float('nan')
                    
                    sim_first_over_Twindow = sim_first_crossing / t_window if np.isfinite(sim_first_crossing) and t_window > 0 else float('nan')
                    sim_sustained_over_Twindow = sim_sustained / t_window if np.isfinite(sim_sustained) and t_window > 0 else float('nan')
                    sim_held_over_Twindow = sim_held / t_window if np.isfinite(sim_held) and t_window > 0 else float('nan')
                    
                    # Censoring-aware restricted normalized times (cohort-level estimates)
                    # These use restricted times (horizon for censored, event_time for observed) divided by T_window
                    density_restricted_first_over_Twindow = density_restricted_first / t_window if np.isfinite(density_restricted_first) and t_window > 0 else float('nan')
                    density_restricted_sustained_over_Twindow = density_restricted_sustained / t_window if np.isfinite(density_restricted_sustained) and t_window > 0 else float('nan')
                    density_restricted_held_over_Twindow = density_restricted_held / t_window if np.isfinite(density_restricted_held) and t_window > 0 else float('nan')
                    
                    sim_restricted_first_over_Twindow = sim_restricted_first / t_window if np.isfinite(sim_restricted_first) and t_window > 0 else float('nan')
                    sim_restricted_sustained_over_Twindow = sim_restricted_sustained / t_window if np.isfinite(sim_restricted_sustained) and t_window > 0 else float('nan')
                    sim_restricted_held_over_Twindow = sim_restricted_held / t_window if np.isfinite(sim_restricted_held) and t_window > 0 else float('nan')
                    
                    # Add rows for density metrics
                    # Note: For continue branch, AUC deficit = 0 (comparing trajectory with itself)
                    # P1 #11: Density targets are horizon-independent (same 0.9 * D_B_final_continue for both systems)
                    # P1 #10: Held duration definition is discrete: ceil(T_window / diagnostic_sample_spacing) consecutive saved samples
                    # P1 #5: density_horizon_duplication_note moved to density rows
                    # P2: AUC is horizon-independent - duplicated across horizon labels, must not be pooled
                    recovery_rows.append({
                        "seed": seed,
                        "rho": rho,
                        "T_window": t_window,
                        "branch": branch,
                        "horizon_system": horizon_system,
                        "metric": "density",
                        "target_value": density_target,
                        "target_source": "0.9 * D_B_final_continue",
                        "target_horizon_dependence": "horizon_independent",
                        "held_duration_definition": "ceil(T_window / diagnostic_sample_spacing) consecutive saved samples",
                        "held_required_samples": required_samples,
                        "diagnostic_sample_spacing": sample_step,
                        "auc_horizon": "full_future",
                        "auc_horizon_dependence": "horizon_independent",
                        "density_horizon_duplication_note": "Density recovery rows are duplicated across horizon_system by design. They are horizon-independent and must not be pooled across the two labels.",
                        "first_crossing_time": density_first_crossing,
                        "first_crossing_observed": density_first_observed,
                        "sustained_time": density_sustained,
                        "sustained_observed": density_sustained_observed,
                        "held_time": density_held,
                        "held_observed": density_held_observed,
                        "restricted_first_crossing_time": density_restricted_first,
                        "restricted_sustained_time": density_restricted_sustained,
                        "restricted_held_time": density_restricted_held,
                        "auc_deficit_vs_continue": density_auc_deficit,
                        "first_crossing_over_Twindow": density_first_over_Twindow,
                        "sustained_time_over_Twindow": density_sustained_over_Twindow,
                        "held_time_over_Twindow": density_held_over_Twindow,
                        "restricted_first_over_Twindow": density_restricted_first_over_Twindow,
                        "restricted_sustained_over_Twindow": density_restricted_sustained_over_Twindow,
                        "restricted_held_over_Twindow": density_restricted_held_over_Twindow,
                    })
                    
                    # Add rows for similarity metrics
                    # Similarity targets are horizon-dependent (different for fixed_physical vs normalized_EMA)
                    # P1 #9: Record NaN imputation counts for cosine zero-vector convention
                    # P1 #5: density_horizon_duplication_note moved to density rows
                    recovery_rows.append({
                        "seed": seed,
                        "rho": rho,
                        "T_window": t_window,
                        "branch": branch,
                        "horizon_system": horizon_system,
                        "metric": "similarity",
                        "target_value": similarity_target,
                        "target_source": f"0.9 * Weighted_similarity_late_{horizon_system}",
                        "target_horizon_dependence": "horizon_dependent",
                        "held_duration_definition": "ceil(T_window / diagnostic_sample_spacing) consecutive saved samples",
                        "held_required_samples": required_samples,
                        "diagnostic_sample_spacing": sample_step,
                        "auc_horizon": "full_future",
                        "target_nan_samples_imputed_zero": similarity_nan_count,
                        "reference_nan_samples_imputed_zero": cont_similarity_nan_count,
                        "similarity_nan_convention": "undefined zero-vector cosine imputed as zero for recovery and AUC only",
                        "first_crossing_time": sim_first_crossing,
                        "first_crossing_observed": sim_first_observed,
                        "sustained_time": sim_sustained,
                        "sustained_observed": sim_sustained_observed,
                        "held_time": sim_held,
                        "held_observed": sim_held_observed,
                        "restricted_first_crossing_time": sim_restricted_first,
                        "restricted_sustained_time": sim_restricted_sustained,
                        "restricted_held_time": sim_restricted_held,
                        "auc_deficit_vs_continue": sim_auc_deficit,
                        "first_crossing_over_Twindow": sim_first_over_Twindow,
                        "sustained_time_over_Twindow": sim_sustained_over_Twindow,
                        "held_time_over_Twindow": sim_held_over_Twindow,
                        "restricted_first_over_Twindow": sim_restricted_first_over_Twindow,
                        "restricted_sustained_over_Twindow": sim_restricted_sustained_over_Twindow,
                        "restricted_held_over_Twindow": sim_restricted_held_over_Twindow,
                    })
    
    if not recovery_rows:
        raise RuntimeError("No recovery scaling data computed - check NPZ contents and data structure")
    
    # Validate expected count: 40 seeds × 5 rho × 4 branches × 2 metrics × 2 horizon systems = 3200
    # Now includes continue branch for DID calculation
    expected_count = len(seeds) * len(rho_values) * len(branches) * 2 * 2
    if len(recovery_rows) != expected_count:
        raise RuntimeError(
            f"Expected {expected_count} recovery rows, got {len(recovery_rows)}. "
            f"This may indicate a logic error in recovery calculation."
        )
    
    recovery_df = pd.DataFrame(recovery_rows)
    
    print(f"✅ Stage 4b: Recovery Scaling - {len(recovery_rows)} recovery metrics computed")
    print(f"  Seeds: {recovery_df['seed'].nunique()}, Rho: {recovery_df['rho'].nunique()}, "
          f"Branches: {recovery_df['branch'].nunique()}, Metrics: {recovery_df['metric'].nunique()}, "
          f"Systems: {recovery_df['horizon_system'].nunique()}")
    
    return recovery_df



# =============================================================================
# Stage 1: Validation
# =============================================================================

def validate_run(
    csv_path: str | Path,
    npz_path: str | Path,
    manifest_path: str | Path,
) -> dict[str, Any]:
    """Validate the run before analysis.
    
    Checks:
    - 800 scalar rows (40 seeds × 5 rho × 4 branches)
    - 40 unique seeds
    - 5 rho values per seed
    - 4 branches per seed/rho
    - baseline equivalence passed
    - run is freezeable
    - no duplicate condition keys
    - all primary outcomes are present and numeric
    """
    results = {
        "status": "passed",
        "errors": [],
        "warnings": [],
    }
    
    # Convert to Path objects for consistency
    csv_path = Path(csv_path)
    npz_path = Path(npz_path)
    manifest_path = Path(manifest_path)
    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
    except Exception as e:
        results["status"] = "failed"
        results["errors"].append(f"Cannot load manifest: {e}")
        return results
    
    # P2: Require study manifest format - strict validation
    # This analysis is specifically versioned for AIEF_1_4_Twindow_sensitivity
    # The simulation driver always produces: manifest["study"]["rho_values"], manifest["study"]["T_window_values"], etc.
    required_manifest_paths = (
        ("study", "rho_values"),
        ("study", "T_window_values"),
        ("protocol", "branches"),
        ("randomization", "paired_seeds"),
        ("model", "B_c"),
    )
    
    for section, key in required_manifest_paths:
        if section not in manifest or key not in manifest[section]:
            results["status"] = "failed"
            results["errors"].append(
                f"Simulation manifest missing {section}.{key}"
            )
            return results
    
    # Extract values using only the expected study format
    try:
        manifest_rho_values = tuple(float(r) for r in manifest["study"]["rho_values"])
        manifest_twindow_values = tuple(float(x) for x in manifest["study"]["T_window_values"])
        manifest_branches = tuple(manifest["protocol"]["branches"])
        manifest_seeds = tuple(str(x) for x in manifest["randomization"]["paired_seeds"])
        
        if manifest_rho_values != EXPECTED_RHO_VALUES:
            results["status"] = "failed"
            results["errors"].append(
                f"Manifest rho_values {manifest_rho_values} != expected {EXPECTED_RHO_VALUES}"
            )
            return results
        
        if manifest_branches != EXPECTED_BRANCHES:
            results["status"] = "failed"
            results["errors"].append(
                f"Manifest branches {manifest_branches} != expected {EXPECTED_BRANCHES}"
            )
            return results
        
        if len(manifest_seeds) != EXPECTED_N_SEEDS:
            results["status"] = "failed"
            results["errors"].append(
                f"Manifest has {len(manifest_seeds)} seeds, expected {EXPECTED_N_SEEDS}"
            )
            return results
        
        if len(manifest_twindow_values) != len(EXPECTED_RHO_VALUES):
            results["status"] = "failed"
            results["errors"].append(
                "Manifest T_window_values length mismatch"
            )
            return results
    except Exception as e:
        results["status"] = "failed"
        results["errors"].append(f"Could not validate manifest study values: {e}")
        return results
    
    # Validate condition status - MANDATORY for production
    condition_status_path = Path(csv_path.parent) / "twindow_condition_status.csv"
    if not condition_status_path.exists():
        results["status"] = "failed"
        results["errors"].append("Condition status file not found - REQUIRED for production analysis")
        return results
    
    try:
        condition_df = pd.read_csv(condition_status_path)
        
        # Check for duplicate condition-status rows
        if condition_df.duplicated(subset=["seed", "rho"]).any():
            results["status"] = "failed"
            results["errors"].append("Condition status file has duplicate (seed, rho) rows")
            return results
        
        # Validate status values
        unique_statuses = set(condition_df["status"].unique())
        valid_statuses = {"success", "failed"}
        invalid_statuses = unique_statuses - valid_statuses
        if invalid_statuses:
            results["status"] = "failed"
            results["errors"].append(
                f"Condition status file has invalid status values: {invalid_statuses}"
            )
            return results
        
        successful_conditions = (condition_df["status"] == "success").sum()
        failed_conditions = (condition_df["status"] == "failed").sum()
        total_conditions = len(condition_df)
        
        expected_conditions = EXPECTED_N_CONDITIONS
        if total_conditions != expected_conditions:
            results["status"] = "failed"
            results["errors"].append(
                f"Condition status: expected {expected_conditions} conditions, "
                f"got {total_conditions}"
            )
            return results
        
        if failed_conditions > 0:
            results["status"] = "failed"
            results["errors"].append(
                f"Condition status: {failed_conditions} conditions failed, "
                f"{successful_conditions} succeeded"
            )
            return results
        
        # Validate exact condition coverage matches manifest
        condition_df["seed"] = condition_df["seed"].astype(str)
        condition_df["rho"] = pd.to_numeric(condition_df["rho"], errors="coerce")
        
        observed_conditions = set(
            zip(condition_df["seed"], condition_df["rho"])
        )
        
        # Get expected conditions from manifest - use study format
        manifest_seeds = [str(s) for s in manifest["randomization"]["paired_seeds"]]
        manifest_rho_values = [float(r) for r in manifest["study"]["rho_values"]]
        manifest_branches = manifest["protocol"]["branches"]
        
        expected_conditions_from_manifest = {
            (str(seed), float(rho))
            for seed in manifest_seeds
            for rho in manifest_rho_values
        }
        
        if observed_conditions != expected_conditions_from_manifest:
            missing = expected_conditions_from_manifest - observed_conditions
            extra = observed_conditions - expected_conditions_from_manifest
            if missing:
                results["status"] = "failed"
                results["errors"].append(
                    f"Condition status missing {len(missing)} conditions: {list(missing)[:5]}"
                )
                return results
            if extra:
                results["status"] = "failed"
                results["errors"].append(
                    f"Condition status has {len(extra)} extra conditions: {list(extra)[:5]}"
                )
                return results
        
        # Hash the condition status file
        condition_status_hash = file_sha256(condition_status_path)
        results["condition_status_hash"] = condition_status_hash
        
    except Exception as e:
        results["status"] = "failed"
        results["errors"].append(f"Could not validate condition status: {e}")
        return results
    
    # Check baseline equivalence
    baseline_eq = manifest.get("baseline_equivalence", {})
    if baseline_eq.get("status") != "passed":
        results["status"] = "failed"
        results["errors"].append(
            f"Baseline equivalence not passed: {baseline_eq.get('status', 'unknown')}"
        )
        return results
    
    # Check freezeable status - FAIL if not freezeable
    # Check both top-level and completion.freezeable, default to False
    completion = manifest.get("completion", {})
    freezeable = manifest.get("freezeable", completion.get("freezeable", False))
    
    # Also check completion status
    completion_status = completion.get("status", "")
    n_successful = completion.get("n_conditions_successful", 0)
    n_failed = completion.get("n_conditions_failed", 0)
    n_expected = EXPECTED_N_CONDITIONS
    
    # Must have all conditions successful and explicit freezeable=true
    if not freezeable:
        results["status"] = "failed"
        results["errors"].append("Run is marked as non-freezeable")
        return results
    
    if completion_status != "completed":
        results["status"] = "failed"
        results["errors"].append(f"Run not completed: status={completion_status}")
        return results
    
    if n_successful != n_expected or n_failed != 0:
        results["status"] = "failed"
        results["errors"].append(
            f"Incomplete run: {n_successful}/{n_expected} successful, {n_failed} failed"
        )
        return results
    
    # Load CSV
    try:
        df = load_csv_atomic(csv_path)
    except Exception as e:
        results["status"] = "failed"
        results["errors"].append(f"Cannot load CSV: {e}")
        return results
    
    # Validate row count
    expected_rows = EXPECTED_N_ROWS
    actual_rows = len(df)
    if actual_rows != expected_rows:
        results["status"] = "failed"
        results["errors"].append(
            f"Row count mismatch: expected {expected_rows}, got {actual_rows}"
        )
    
    # Validate unique seeds
    unique_seeds = df["seed"].unique()
    if len(unique_seeds) != EXPECTED_N_SEEDS:
        results["status"] = "failed"
        results["errors"].append(
            f"Seed count mismatch: expected {EXPECTED_N_SEEDS}, got {len(unique_seeds)}"
        )
    
    # Validate rho values
    unique_rho = sorted([float(r) for r in df["rho"].unique()])
    expected_rho = sorted([float(r) for r in EXPECTED_RHO_VALUES])
    if unique_rho != expected_rho:
        results["status"] = "failed"
        results["errors"].append(
            f"Rho values mismatch: expected {expected_rho}, got {unique_rho}"
        )
    
    # Validate branches
    unique_branches = sorted(df["branch"].unique())
    expected_branches = sorted(EXPECTED_BRANCHES)
    if unique_branches != expected_branches:
        results["status"] = "failed"
        results["errors"].append(
            f"Branches mismatch: expected {expected_branches}, got {unique_branches}"
        )
    
    # Validate completeness: each seed/rho/branch combination should exist
    missing_combinations = []
    for seed in unique_seeds:
        seed_data = df[df["seed"] == seed]
        for rho in [float(r) for r in df["rho"].unique()]:
            rho_data = seed_data[seed_data["rho"] == rho]
            for branch in unique_branches:
                if not ((rho_data["branch"] == branch).any()):
                    missing_combinations.append(f"seed={seed}, rho={rho}, branch={branch}")
    
    if missing_combinations:
        results["status"] = "failed"
        results["errors"].append(
            f"Missing {len(missing_combinations)} combinations: {missing_combinations[:5]}"
        )
    
    # Check for duplicates
    duplicate_rows = df.duplicated(subset=["seed", "rho", "branch"])
    if duplicate_rows.any():
        results["status"] = "failed"
        results["errors"].append(
            f"Duplicate rows found: {duplicate_rows.sum()} duplicates"
        )
    
    # Validate exact cohort coverage in CSV matches manifest
    manifest_seeds = [str(s) for s in manifest["randomization"]["paired_seeds"]]
    manifest_rho_values = [float(r) for r in manifest["study"]["rho_values"]]
    manifest_branches = manifest["protocol"]["branches"]
    
    expected_csv_conditions = {
        (str(seed), float(rho), branch)
        for seed in manifest_seeds
        for rho in manifest_rho_values
        for branch in manifest_branches
    }
    
    observed_csv_conditions = set(
        zip(df["seed"], df["rho"], df["branch"])
    )
    
    if observed_csv_conditions != expected_csv_conditions:
        missing = expected_csv_conditions - observed_csv_conditions
        extra = observed_csv_conditions - expected_csv_conditions
        if missing:
            results["status"] = "failed"
            results["errors"].append(
                f"CSV missing {len(missing)} conditions: {list(missing)[:5]}"
            )
            return results
        if extra:
            results["status"] = "failed"
            results["errors"].append(
                f"CSV has {len(extra)} extra conditions: {list(extra)[:5]}"
            )
            return results
    
    # Validate primary and secondary outcomes are present and finite
    all_outcomes = PRIMARY_OUTCOMES + SECONDARY_NORMALIZED_OUTCOMES
    for outcome in all_outcomes:
        if outcome not in df.columns:
            results["status"] = "failed"
            results["errors"].append(f"Outcome '{outcome}' missing from CSV")
        else:
            # Check that values are numeric
            non_numeric = df[outcome].apply(lambda x: not isinstance(x, (int, float, np.number)))
            if non_numeric.any():
                results["status"] = "failed"
                results["errors"].append(
                    f"Outcome '{outcome}' has {non_numeric.sum()} non-numeric values"
                )
            
            # Check that values are finite (not NaN, inf, or -inf)
            non_finite = ~np.isfinite(df[outcome])
            if non_finite.any():
                results["status"] = "failed"
                results["errors"].append(
                    f"Outcome '{outcome}' has {non_finite.sum()} non-finite values"
                )
    
    # P0 #2: Validate T_window exists and is consistent
    # T_window is study metadata, critical for recovery normalization
    if "T_window" not in df.columns:
        results["status"] = "failed"
        results["errors"].append("T_window missing from scalar CSV")
        return results
    else:
        tw = pd.to_numeric(df["T_window"], errors="coerce")
        if (~np.isfinite(tw) | (tw <= 0)).any():
            results["status"] = "failed"
            results["errors"].append("T_window contains non-finite or non-positive values")
            return results
        
        # Validate T_window is consistent across branches for each (seed, rho)
        # Use study manifest format
        rho_values_list = [float(r) for r in manifest["study"]["rho_values"]]
        twindow_values_list = [float(x) for x in manifest["study"]["T_window_values"]]
        
        if len(rho_values_list) != len(twindow_values_list):
            results["status"] = "failed"
            results["errors"].append(
                "Manifest T_window_values length does not match rho_values length"
            )
            return results
        
        for rho, expected_twindow in zip(rho_values_list, twindow_values_list):
            rho_mask = df["rho"] == rho
            values = df.loc[rho_mask, "T_window"].unique()
            if len(values) != 1:
                results["status"] = "failed"
                results["errors"].append(
                    f"rho={rho} has {len(values)} distinct T_window values"
                )
                return results
            elif float(values[0]) != expected_twindow:
                results["status"] = "failed"
                results["errors"].append(
                    f"rho={rho}: T_window={values[0]} != expected {expected_twindow}"
                )
                return results
    
    # P0 #3: Validate D_B_final exists and is valid
    # D_B_final is used for density targets in recovery analysis
    if "D_B_final" not in df.columns:
        results["status"] = "failed"
        results["errors"].append("D_B_final missing from scalar CSV")
        return results
    else:
        density = pd.to_numeric(df["D_B_final"], errors="coerce")
        invalid = (~np.isfinite(density) | (density < 0.0) | (density > 1.0))
        if invalid.any():
            results["status"] = "failed"
            results["errors"].append(
                f"D_B_final has {int(invalid.sum())} invalid values (must be in [0,1])"
            )
            return results
    
    # Get baseline equivalence certificate hash - MANDATORY for production
    baseline_cert_path = Path(csv_path.parent) / "baseline_equivalence_certificate.json"
    if not baseline_cert_path.exists():
        results["status"] = "failed"
        results["errors"].append("Baseline equivalence certificate not found - REQUIRED for production analysis")
        return results
    baseline_cert_hash = file_sha256(baseline_cert_path)
    
    # Validate baseline certificate contents
    try:
        with open(baseline_cert_path, "r") as f:
            certificate = json.load(f)
        cert_status = certificate.get("status", "unknown")
        cert_n_seeds = certificate.get("n_seeds", 0)
        cert_seed_results = certificate.get("seed_results", {})
        
        if cert_status != "passed":
            results["status"] = "failed"
            results["errors"].append(
                f"Baseline certificate status is '{cert_status}', expected 'passed'"
            )
            return results
        
        if cert_n_seeds != EXPECTED_N_SEEDS:
            results["status"] = "failed"
            results["errors"].append(
                f"Baseline certificate has {cert_n_seeds} seeds, expected {EXPECTED_N_SEEDS}"
            )
            return results
        
        if len(cert_seed_results) != EXPECTED_N_SEEDS:
            results["status"] = "failed"
            results["errors"].append(
                f"Baseline certificate has {len(cert_seed_results)} seed results, expected {EXPECTED_N_SEEDS}"
            )
            return results
        
        # P1 #7: Verify baseline certificate cohort matches manifest exactly
        try:
            expected_cert_seeds = {
                str(seed)
                for seed in manifest["randomization"]["paired_seeds"]
            }
            observed_cert_seeds = set(cert_seed_results.keys())
            
            if observed_cert_seeds != expected_cert_seeds:
                missing_seeds = expected_cert_seeds - observed_cert_seeds
                extra_seeds = observed_cert_seeds - expected_cert_seeds
                if missing_seeds:
                    results["status"] = "failed"
                    results["errors"].append(
                        f"Baseline certificate missing {len(missing_seeds)} seeds: {list(missing_seeds)[:5]}"
                    )
                    return results
                if extra_seeds:
                    results["status"] = "failed"
                    results["errors"].append(
                        f"Baseline certificate has {len(extra_seeds)} extra seeds: {list(extra_seeds)[:5]}"
                    )
                    return results
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(
                f"Could not validate baseline certificate seed cohort: {e}"
            )
            return results
        
        # P1 #4: Validate baseline certificate branch set
        try:
            cert_branches = tuple(
                certificate.get("protocol", {}).get("branches", [])
            )
            if cert_branches != EXPECTED_FROZEN_BASELINE_BRANCHES:
                results["status"] = "failed"
                results["errors"].append(
                    f"Baseline certificate branch set/order {cert_branches} != expected "
                    f"{EXPECTED_FROZEN_BASELINE_BRANCHES}"
                )
                return results
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(
                f"Could not validate baseline certificate branch set: {e}"
            )
            return results
        
        for seed_id, seed_result in cert_seed_results.items():
            if seed_result.get("status") != "passed":
                results["status"] = "failed"
                results["errors"].append(
                    f"Baseline certificate seed {seed_id} status is '{seed_result.get('status')}', expected 'passed'"
                )
                return results
    except Exception as e:
        results["status"] = "failed"
        results["errors"].append(f"Could not validate baseline certificate contents: {e}")
        return results
    
    # P0 #4: Verify simulation output hashes against manifest
    # Validate that actual input files match the recorded hashes in the simulation manifest
    recorded_hashes = manifest.get("output_hashes", {})
    
    files_to_verify = {
        "scalar_csv": csv_path,
        "branch_npz": npz_path,
        "condition_status_csv": condition_status_path,
        "baseline_certificate": baseline_cert_path,
    }
    
    for label, path in files_to_verify.items():
        expected_hash = recorded_hashes.get(label)
        observed_hash = file_sha256(path)
        
        if expected_hash is None:
            results["status"] = "failed"
            results["errors"].append(
                f"Simulation manifest missing output hash for {label}"
            )
            return results
        elif observed_hash != expected_hash:
            results["status"] = "failed"
            results["errors"].append(
                f"Hash mismatch for {label}: expected={expected_hash}, observed={observed_hash}"
            )
            return results
    
    # Record validation info
    results["validation"] = {
        "n_rows": actual_rows,
        "n_seeds": len(unique_seeds),
        "n_rho": len(unique_rho),
        "n_branches": len(unique_branches),
        "n_duplicates": int(duplicate_rows.sum()),
        "n_missing_combinations": len(missing_combinations),
        "baseline_equivalence": baseline_eq.get("status"),
        "freezeable": manifest.get("freezeable", False),
        "baseline_certificate_hash": baseline_cert_hash,
    }
    
    # Also expose at top level for manifest generation
    results["baseline_certificate_hash"] = baseline_cert_hash
    
    if results["status"] == "passed":
        print("✅ Stage 1: Validation PASSED")
        print(f"  {actual_rows} rows, {len(unique_seeds)} seeds, {len(unique_rho)} rho, {len(unique_branches)} branches")
    else:
        print("❌ Stage 1: Validation FAILED")
        for error in results["errors"]:
            print(f"  {error}")
        for warning in results["warnings"]:
            print(f"  WARNING: {warning}")
    
    return results


# =============================================================================
# Stage 2: Regime Contrasts
# =============================================================================

def compute_regime_contrasts(
    df: pd.DataFrame,
    outcomes: tuple[str, ...] = PRIMARY_OUTCOMES,
) -> pd.DataFrame:
    """Compute regime contrasts: Δ_{s,ρ}^regime(Y) = Y_{s,ρ,continue} - Y_{s,1,continue}
    
    Uses direct merge instead of pivot to avoid MultiIndex column issues.
    
    For each seed and non-baseline rho, compute the difference between
    the outcome at that rho and the outcome at rho=1 (baseline).
    """
    # Filter to continue branch only
    cont = df.loc[
        df["branch"] == "continue",
        ["seed", "rho", *outcomes],
    ].copy()
    
    # Get baseline (rho=1.0) values
    baseline = (
        cont.loc[cont["rho"] == 1.0]
        .drop(columns="rho")
        .rename(
            columns={
                outcome: f"{outcome}_baseline"
                for outcome in outcomes
            }
        )
    )
    
    # Merge with all rho values
    merged = cont.merge(
        baseline,
        on="seed",
        how="inner",
        validate="many_to_one",
    )
    
    # Filter to non-baseline rho
    merged = merged.loc[merged["rho"] != 1.0]
    
    # Compute contrasts
    rows = []
    for _, row in merged.iterrows():
        for outcome in outcomes:
            value = row[outcome]
            reference = row[f"{outcome}_baseline"]
            
            # Validate that both values are numeric
            if not isinstance(value, (int, float, np.number)) or not isinstance(reference, (int, float, np.number)):
                raise RuntimeError(f"Non-numeric value for {outcome} at seed={row['seed']}, rho={row['rho']}")
            
            rows.append({
                "seed": row["seed"],
                "rho": row["rho"],
                "outcome": outcome,
                "Y_rho_continue": float(value),
                "Y_baseline_continue": float(reference),
                "paired_regime_contrast": float(value - reference),
            })
    
    if not rows:
        raise RuntimeError("No regime contrasts computed - check input data")
    
    # Validate expected count
    expected_count = EXPECTED_N_SEEDS * (len(EXPECTED_RHO_VALUES) - 1) * len(outcomes)
    if len(rows) != expected_count:
        raise RuntimeError(
            f"Expected {expected_count} regime contrasts, got {len(rows)}"
        )
    
    contrasts_df = pd.DataFrame(rows)
    
    print(f"✅ Stage 2: Regime Contrasts - {len(rows)} contrasts computed")
    print(f"  Seeds: {contrasts_df['seed'].nunique()}, Rho values: {contrasts_df['rho'].nunique()}, Outcomes: {contrasts_df['outcome'].nunique()}")
    
    return contrasts_df


# =============================================================================
# Stage 3: Branch Difference-in-Differences
# =============================================================================

def compute_branch_did(
    df: pd.DataFrame,
    outcomes: tuple[str, ...] = PRIMARY_OUTCOMES,
) -> pd.DataFrame:
    """Compute branch DID: I_{s,ρ,b}(Y) = [Y_{s,ρ,b} - Y_{s,ρ,continue}] - [Y_{s,1,b} - Y_{s,1,continue}]
    
    For each seed, non-baseline rho, and non-continue branch, compute the
    difference-in-differences relative to continue branch.
    
    Skips rho=1.0 (baseline) as DID should be zero by construction.
    """
    did_rows = []
    
    for seed in df["seed"].unique():
        seed_data = df[df["seed"] == seed]
        
        for rho in sorted([float(r) for r in df["rho"].unique()]):
            # Skip baseline rho=1.0
            if rho == 1.0:
                continue
            
            rho_data = seed_data[seed_data["rho"] == rho]
            
            # Get baseline (rho=1.0) data for this seed
            baseline_data = seed_data[seed_data["rho"] == 1.0]
            
            for branch in NON_CONTINUE_BRANCHES:
                for outcome in outcomes:
                    # Get Y_{s,ρ,b}
                    y_rho_b_match = rho_data[rho_data["branch"] == branch][outcome]
                    if len(y_rho_b_match) == 0:
                        raise RuntimeError(f"Missing data: seed={seed}, rho={rho}, branch={branch}, outcome={outcome}")
                    y_rho_b = float(y_rho_b_match.iloc[0])
                    
                    # Get Y_{s,ρ,continue}
                    y_rho_c_match = rho_data[rho_data["branch"] == "continue"][outcome]
                    if len(y_rho_c_match) == 0:
                        raise RuntimeError(f"Missing continue data: seed={seed}, rho={rho}, outcome={outcome}")
                    y_rho_c = float(y_rho_c_match.iloc[0])
                    
                    # Get Y_{s,1,b}
                    y_base_b_match = baseline_data[baseline_data["branch"] == branch][outcome]
                    if len(y_base_b_match) == 0:
                        raise RuntimeError(f"Missing baseline data: seed={seed}, branch={branch}, outcome={outcome}")
                    y_base_b = float(y_base_b_match.iloc[0])
                    
                    # Get Y_{s,1,continue}
                    y_base_c_match = baseline_data[baseline_data["branch"] == "continue"][outcome]
                    if len(y_base_c_match) == 0:
                        raise RuntimeError(f"Missing baseline continue data: seed={seed}, outcome={outcome}")
                    y_base_c = float(y_base_c_match.iloc[0])
                    
                    # Compute DID
                    branch_effect_rho = y_rho_b - y_rho_c
                    branch_effect_baseline = y_base_b - y_base_c
                    did = branch_effect_rho - branch_effect_baseline
                    
                    did_rows.append({
                        "seed": seed,
                        "rho": rho,
                        "branch": branch,
                        "outcome": outcome,
                        "Y_rho_branch": y_rho_b,
                        "Y_rho_continue": y_rho_c,
                        "branch_effect_rho": branch_effect_rho,
                        "Y_baseline_branch": y_base_b,
                        "Y_baseline_continue": y_base_c,
                        "branch_effect_baseline": branch_effect_baseline,
                        "difference_in_differences": did,
                    })
    
    # Validate expected count
    expected_count = EXPECTED_N_SEEDS * (len(EXPECTED_RHO_VALUES) - 1) * len(NON_CONTINUE_BRANCHES) * len(outcomes)
    if len(did_rows) != expected_count:
        raise RuntimeError(
            f"Expected {expected_count} DID values, got {len(did_rows)}"
        )
    
    did_df = pd.DataFrame(did_rows)
    
    print(f"✅ Stage 3: Branch DID - {len(did_rows)} DID values computed")
    print(f"  Seeds: {did_df['seed'].nunique()}, Rho: {did_df['rho'].nunique()}, Branches: {did_df['branch'].nunique()}")
    
    return did_df


# =============================================================================
# Stage 4: Cross-T Topology and Recovery
# =============================================================================

def build_continue_b_final_key(seed: str, rho: float) -> str:
    """Build canonical key for B_final matrix."""
    return f"continue_seed_{seed}_rho_{rho}_B_final"


def compute_cross_t_topology(
    npz_path: str | Path,
    seeds: list[str],
    rho_values: list[float],
    b_c: float,
) -> pd.DataFrame:
    """Compute cross-T topology metrics.
    
    For each seed and non-baseline rho, compute:
    - S_{s,ρ} = cos(B_final_{s,ρ,continue}, B_final_{s,1,continue})
    - J_{s,ρ} = Jaccard(B_final_{s,ρ,continue}, B_final_{s,1,continue})
    - D_{s,ρ} = normalized_L2_distance(B_final_{s,ρ,continue}, B_final_{s,1,continue})
    
    Requires exactly EXPECTED_N_TOPOLOGY rows (40 seeds × 4 non-baseline rho = 160).
    Any missing matrix is a schema failure.
    """
    # Convert to Path for consistency
    npz_path = Path(npz_path)
    
    # Build list of exact keys to load
    keys_to_load = []
    for seed in seeds:
        for rho in rho_values:
            keys_to_load.append(build_continue_b_final_key(seed, rho))
    
    # Load only the required B_final matrices
    npz_data = load_npz_selective(npz_path, keys=keys_to_load)
    
    topology_rows = []
    missing_keys = []
    
    for seed in seeds:
        for rho in rho_values:
            if rho == 1.0:
                continue  # Skip baseline
            
            # Get B_final for this (seed, rho, continue)
            rho_key = build_continue_b_final_key(seed, rho)
            baseline_key = build_continue_b_final_key(seed, 1.0)
            
            if rho_key not in npz_data:
                missing_keys.append(rho_key)
                continue
            if baseline_key not in npz_data:
                missing_keys.append(baseline_key)
                continue
            
            B_rho = validate_topology_matrix(npz_data[rho_key], rho_key)
            B_baseline = validate_topology_matrix(npz_data[baseline_key], baseline_key)
            
            # Compute metrics
            cos_sim = cosine_similarity(B_rho, B_baseline)
            jaccard = jaccard_similarity(B_rho, B_baseline, threshold=b_c)
            norm_dist = normalized_distance(B_rho, B_baseline)
            
            # Validate metric outputs are finite
            if not np.isfinite(cos_sim):
                raise RuntimeError(f"cosine_similarity({rho_key}, {baseline_key}) returned non-finite value")
            if not np.isfinite(jaccard):
                raise RuntimeError(f"jaccard_similarity({rho_key}, {baseline_key}) returned non-finite value")
            if not np.isfinite(norm_dist):
                raise RuntimeError(f"normalized_distance({rho_key}, {baseline_key}) returned non-finite value")
            
            topology_rows.append({
                "seed": seed,
                "rho": rho,
                "cross_T_cosine": cos_sim,
                "cross_T_Jaccard": jaccard,
                "cross_T_normalized_distance": norm_dist,
            })
    
    # Validate we have all expected comparisons
    expected_count = EXPECTED_N_TOPOLOGY
    if len(topology_rows) != expected_count:
        raise RuntimeError(
            f"Expected {expected_count} topology comparisons, got {len(topology_rows)}. "
            f"Missing keys: {missing_keys[:10]}"
        )
    
    topology_df = pd.DataFrame(topology_rows)
    
    # P0 #2: Validate topology metrics are all finite
    topology_columns = ("cross_T_cosine", "cross_T_Jaccard", "cross_T_normalized_distance")
    for column in topology_columns:
        if not np.isfinite(topology_df[column]).all():
            raise RuntimeError(
                f"Topology metric {column} contains non-finite values"
            )
    
    # Validate topology group sizes
    topology_sizes = topology_df.groupby("rho").size()
    if len(topology_sizes) != 4:
        raise RuntimeError(
            f"Expected 4 topology rho groups, got {len(topology_sizes)}"
        )
    if not (topology_sizes == EXPECTED_N_SEEDS).all():
        raise RuntimeError(
            f"Topology rho groups do not all contain {EXPECTED_N_SEEDS} seeds"
        )
    
    print(f"✅ Stage 4: Cross-T Topology - {len(topology_rows)} topology comparisons computed")
    print(f"  Seeds: {topology_df['seed'].nunique()}, Rho: {topology_df['rho'].nunique()}")
    
    return topology_df



def compute_recovery_did(
    recovery: pd.DataFrame,
) -> pd.DataFrame:
    """Compute recovery interaction DID: [R_{s,ρ,b} - R_{s,ρ,c}] - [R_{s,1,b} - R_{s,1,c}]
    
    For each seed, non-baseline rho, and NON-CONTINUE branch only, compute the
    difference-in-differences for recovery outcomes relative to continue branch.
    
    Uses restricted times (censoring-aware) and normalized t/T_window as primary outcomes.
    
    Skips rho=1.0 (baseline) as DID should be zero by construction.
    Skips continue branch as it generates trivial zero-DID rows.
    
    Expected count: 40 seeds * 4 non-baseline rho * 3 non-continue branches * 2 systems * 2 metrics * 13 outcomes = 24960
    """
    if recovery.empty:
        return pd.DataFrame()
    
    did_rows = []
    
    seeds = sorted(recovery["seed"].unique())
    rho_values = sorted([float(r) for r in recovery["rho"].unique()])
    horizon_systems = sorted(recovery["horizon_system"].unique())
    metrics = sorted(recovery["metric"].unique())
    
    # Recovery outcomes to compute DID for
    # Prioritize censoring-aware restricted outcomes as primary
    recovery_outcomes = [
        "restricted_first_crossing_time",
        "restricted_sustained_time", 
        "restricted_held_time",
        "restricted_first_over_Twindow",
        "restricted_sustained_over_Twindow",
        "restricted_held_over_Twindow",
        "auc_deficit_vs_continue",
        "first_crossing_over_Twindow",
        "sustained_time_over_Twindow",
        "held_time_over_Twindow",
    ]
    
    # Also compute DID for recovery indicators
    indicator_outcomes = [
        "first_crossing_observed",
        "sustained_observed",
        "held_observed",
    ]
    
    for seed in seeds:
        seed_data = recovery[recovery["seed"] == seed]
        
        for rho in rho_values:
            # Skip baseline rho=1.0
            if rho == 1.0:
                continue
            
            rho_data = seed_data[seed_data["rho"] == rho]
            
            # Get baseline (rho=1.0) data for this seed
            baseline_data = seed_data[seed_data["rho"] == 1.0]
            
            for branch in NON_CONTINUE_BRANCHES:
                # EXCLUDE continue branch - it generates trivial zero-DID rows
                # DID is only defined for non-continue branches: [R_{s,ρ,b} - R_{s,ρ,c}] - [R_{s,1,b} - R_{s,1,c}]

                for horizon_system in horizon_systems:
                    for metric in metrics:
                        # Compute DID for each recovery outcome
                        for outcome in recovery_outcomes:
                            # Get values: R_{s,ρ,b}, R_{s,ρ,c}, R_{s,1,b}, R_{s,1,c}
                            
                            # R_{s,ρ,b}
                            r_rho_b_match = rho_data[
                                (rho_data["branch"] == branch) & 
                                (rho_data["horizon_system"] == horizon_system) &
                                (rho_data["metric"] == metric)
                            ][outcome]
                            
                            # R_{s,ρ,c} (continue branch at same rho)
                            r_rho_c_match = rho_data[
                                (rho_data["branch"] == "continue") & 
                                (rho_data["horizon_system"] == horizon_system) &
                                (rho_data["metric"] == metric)
                            ][outcome]
                            
                            # R_{s,1,b} (baseline rho=1.0, same branch)
                            r_base_b_match = baseline_data[
                                (baseline_data["branch"] == branch) & 
                                (baseline_data["horizon_system"] == horizon_system) &
                                (baseline_data["metric"] == metric)
                            ][outcome]
                            
                            # R_{s,1,c} (baseline rho=1.0, continue)
                            r_base_c_match = baseline_data[
                                (baseline_data["branch"] == "continue") & 
                                (baseline_data["horizon_system"] == horizon_system) &
                                (baseline_data["metric"] == metric)
                            ][outcome]
                            
                            # Validate exactly one match for each cell - missing cells indicate schema error
                            matches = {
                                "rho_branch": r_rho_b_match,
                                "rho_continue": r_rho_c_match,
                                "baseline_branch": r_base_b_match,
                                "baseline_continue": r_base_c_match,
                            }
                            for label, match in matches.items():
                                if len(match) != 1:
                                    raise RuntimeError(
                                        f"Recovery DID requires exactly one {label} row; "
                                        f"seed={seed}, rho={rho}, branch={branch}, "
                                        f"horizon={horizon_system}, metric={metric}, "
                                        f"outcome={outcome}, found={len(match)}"
                                    )
                            
                            r_rho_b = float(r_rho_b_match.iloc[0])
                            r_rho_c = float(r_rho_c_match.iloc[0])
                            r_base_b = float(r_base_b_match.iloc[0])
                            r_base_c = float(r_base_c_match.iloc[0])
                            
                            # Compute DID: [R_{s,ρ,b} - R_{s,ρ,c}] - [R_{s,1,b} - R_{s,1,c}]
                            branch_effect_rho = r_rho_b - r_rho_c
                            branch_effect_baseline = r_base_b - r_base_c
                            did = branch_effect_rho - branch_effect_baseline
                            
                            did_rows.append({
                                "seed": seed,
                                "rho": rho,
                                "branch": branch,
                                "horizon_system": horizon_system,
                                "metric": metric,
                                "outcome": outcome,
                                "R_rho_branch": r_rho_b,
                                "R_rho_continue": r_rho_c,
                                "branch_effect_rho": branch_effect_rho,
                                "R_baseline_branch": r_base_b,
                                "R_baseline_continue": r_base_c,
                                "branch_effect_baseline": branch_effect_baseline,
                                "recovery_difference_in_differences": did,
                            })
                        
                        # Compute DID for recovery indicators (binary outcomes)
                        for outcome in indicator_outcomes:
                            # Get values
                            r_rho_b_match = rho_data[
                                (rho_data["branch"] == branch) & 
                                (rho_data["horizon_system"] == horizon_system) &
                                (rho_data["metric"] == metric)
                            ][outcome]
                            
                            r_rho_c_match = rho_data[
                                (rho_data["branch"] == "continue") & 
                                (rho_data["horizon_system"] == horizon_system) &
                                (rho_data["metric"] == metric)
                            ][outcome]
                            
                            r_base_b_match = baseline_data[
                                (baseline_data["branch"] == branch) & 
                                (baseline_data["horizon_system"] == horizon_system) &
                                (baseline_data["metric"] == metric)
                            ][outcome]
                            
                            r_base_c_match = baseline_data[
                                (baseline_data["branch"] == "continue") & 
                                (baseline_data["horizon_system"] == horizon_system) &
                                (baseline_data["metric"] == metric)
                            ][outcome]
                            
                            # Validate exactly one match for each cell - missing cells indicate schema error
                            matches = {
                                "rho_branch": r_rho_b_match,
                                "rho_continue": r_rho_c_match,
                                "baseline_branch": r_base_b_match,
                                "baseline_continue": r_base_c_match,
                            }
                            for label, match in matches.items():
                                if len(match) != 1:
                                    raise RuntimeError(
                                        f"Recovery DID requires exactly one {label} row; "
                                        f"seed={seed}, rho={rho}, branch={branch}, "
                                        f"horizon={horizon_system}, metric={metric}, "
                                        f"outcome={outcome}, found={len(match)}"
                                    )
                            
                            r_rho_b = float(r_rho_b_match.iloc[0])
                            r_rho_c = float(r_rho_c_match.iloc[0])
                            r_base_b = float(r_base_b_match.iloc[0])
                            r_base_c = float(r_base_c_match.iloc[0])
                            
                            # For binary outcomes, use difference in proportions
                            branch_effect_rho = r_rho_b - r_rho_c
                            branch_effect_baseline = r_base_b - r_base_c
                            did = branch_effect_rho - branch_effect_baseline
                            
                            did_rows.append({
                                "seed": seed,
                                "rho": rho,
                                "branch": branch,
                                "horizon_system": horizon_system,
                                "metric": metric,
                                "outcome": outcome,
                                "R_rho_branch": r_rho_b,
                                "R_rho_continue": r_rho_c,
                                "branch_effect_rho": branch_effect_rho,
                                "R_baseline_branch": r_base_b,
                                "R_baseline_continue": r_base_c,
                                "branch_effect_baseline": branch_effect_baseline,
                                "recovery_difference_in_differences": did,
                            })
    
    if not did_rows:
        return pd.DataFrame()
    
    # Validate exact count: 40 seeds * 4 non-baseline rho * 3 non-continue branches * 2 systems * 2 metrics * 13 outcomes = 24960
    if len(did_rows) != EXPECTED_N_RECOVERY_DID:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_N_RECOVERY_DID} recovery DID rows, got {len(did_rows)}. "
            f"This indicates a logic error - continue branch should be excluded."
        )
    
    did_df = pd.DataFrame(did_rows)
    
    print(f"✅ Stage 4c: Recovery DID - {len(did_rows)} recovery DID values computed")
    print(f"  Seeds: {did_df['seed'].nunique()}, Rho: {did_df['rho'].nunique()}, "
          f"Branches: {did_df['branch'].nunique()}, Systems: {did_df['horizon_system'].nunique()}")
    
    return did_df

def compute_seed_level_summaries(
    regime_contrasts: pd.DataFrame,
    branch_did: pd.DataFrame,
    topology: pd.DataFrame,
    recovery: pd.DataFrame | None = None,
    n_bootstrap: int = 1000,
    bootstrap_seed: int | None = None,
) -> dict[str, pd.DataFrame]:
    """Compute seed-level summaries with bootstrap confidence intervals.
    
    For each outcome and rho, compute:
    - Mean contrast
    - Sample standard deviation
    - 95% bootstrap CI
    
    Uses seeded bootstrap for reproducibility.
    """
    summaries = {}
    
    # Create seeded RNG for bootstrap
    if bootstrap_seed is None:
        raise ValueError("--bootstrap-seed is required for reproducible analysis")
    rng = np.random.default_rng(bootstrap_seed)
    
    # Regime contrast summaries
    if not regime_contrasts.empty:
        # Use named aggregation to avoid MultiIndex columns
        regime_summary = regime_contrasts.groupby(
            ["rho", "outcome"],
            as_index=False,
        ).agg(
            mean=("paired_regime_contrast", "mean"),
            std=("paired_regime_contrast", "std"),
            n=("paired_regime_contrast", "count"),
        )
        
        # Add bootstrap CI
        for (rho, outcome), group in regime_contrasts.groupby(["rho", "outcome"]):
            values = group["paired_regime_contrast"].dropna().values
            if len(values) > 0:
                # Seeded bootstrap
                indices = rng.integers(0, len(values), size=(n_bootstrap, len(values)))
                bootstrap_means = np.mean(values[indices], axis=1)
                
                ci_lower = float(np.percentile(bootstrap_means, 2.5))
                ci_upper = float(np.percentile(bootstrap_means, 97.5))
                
                idx = regime_summary[(regime_summary["rho"] == rho) & (regime_summary["outcome"] == outcome)].index
                regime_summary.loc[idx, "ci_lower"] = ci_lower
                regime_summary.loc[idx, "ci_upper"] = ci_upper
        
        summaries["regime_contrasts"] = regime_summary
        print(f"✅ Stage 5: Regime Contrast Summaries - {len(regime_summary)} groups")
    
    # Branch DID summaries
    if not branch_did.empty:
        did_summary = branch_did.groupby(
            ["rho", "branch", "outcome"],
            as_index=False,
        ).agg(
            mean=("difference_in_differences", "mean"),
            std=("difference_in_differences", "std"),
            n=("difference_in_differences", "count"),
        )
        
        # Add bootstrap CI
        for (rho, branch, outcome), group in branch_did.groupby(["rho", "branch", "outcome"]):
            values = group["difference_in_differences"].dropna().values
            if len(values) > 0:
                indices = rng.integers(0, len(values), size=(n_bootstrap, len(values)))
                bootstrap_means = np.mean(values[indices], axis=1)
                
                ci_lower = float(np.percentile(bootstrap_means, 2.5))
                ci_upper = float(np.percentile(bootstrap_means, 97.5))
                
                idx = did_summary[(did_summary["rho"] == rho) & (did_summary["branch"] == branch) & (did_summary["outcome"] == outcome)].index
                did_summary.loc[idx, "ci_lower"] = ci_lower
                did_summary.loc[idx, "ci_upper"] = ci_upper
        
        summaries["branch_did"] = did_summary
        print(f"✅ Stage 5: Branch DID Summaries - {len(did_summary)} groups")
    
    # Topology summaries
    if not topology.empty:
        # Flatten the aggregation to avoid MultiIndex columns
        topology_summary = topology.groupby("rho", as_index=False).agg(
            cosine_mean=("cross_T_cosine", "mean"),
            cosine_std=("cross_T_cosine", "std"),
            cosine_n=("cross_T_cosine", "count"),
            jaccard_mean=("cross_T_Jaccard", "mean"),
            jaccard_std=("cross_T_Jaccard", "std"),
            jaccard_n=("cross_T_Jaccard", "count"),
            distance_mean=("cross_T_normalized_distance", "mean"),
            distance_std=("cross_T_normalized_distance", "std"),
            distance_n=("cross_T_normalized_distance", "count"),
        )
        
        # Add bootstrap CI for topology metrics (seed-level bootstrap by rho)
        for rho, group in topology.groupby("rho"):
            # Bootstrap cosine similarity
            cosine_values = group["cross_T_cosine"].dropna().values
            if len(cosine_values) > 0:
                indices = rng.integers(0, len(cosine_values), size=(n_bootstrap, len(cosine_values)))
                bootstrap_means = np.mean(cosine_values[indices], axis=1)
                cosine_ci_lower = float(np.percentile(bootstrap_means, 2.5))
                cosine_ci_upper = float(np.percentile(bootstrap_means, 97.5))
                
                idx = topology_summary[topology_summary["rho"] == rho].index
                topology_summary.loc[idx, "cosine_ci_lower"] = cosine_ci_lower
                topology_summary.loc[idx, "cosine_ci_upper"] = cosine_ci_upper
            
            # Bootstrap Jaccard similarity
            jaccard_values = group["cross_T_Jaccard"].dropna().values
            if len(jaccard_values) > 0:
                indices = rng.integers(0, len(jaccard_values), size=(n_bootstrap, len(jaccard_values)))
                bootstrap_means = np.mean(jaccard_values[indices], axis=1)
                jaccard_ci_lower = float(np.percentile(bootstrap_means, 2.5))
                jaccard_ci_upper = float(np.percentile(bootstrap_means, 97.5))
                
                idx = topology_summary[topology_summary["rho"] == rho].index
                topology_summary.loc[idx, "jaccard_ci_lower"] = jaccard_ci_lower
                topology_summary.loc[idx, "jaccard_ci_upper"] = jaccard_ci_upper
            
            # Bootstrap normalized distance
            distance_values = group["cross_T_normalized_distance"].dropna().values
            if len(distance_values) > 0:
                indices = rng.integers(0, len(distance_values), size=(n_bootstrap, len(distance_values)))
                bootstrap_means = np.mean(distance_values[indices], axis=1)
                distance_ci_lower = float(np.percentile(bootstrap_means, 2.5))
                distance_ci_upper = float(np.percentile(bootstrap_means, 97.5))
                
                idx = topology_summary[topology_summary["rho"] == rho].index
                topology_summary.loc[idx, "distance_ci_lower"] = distance_ci_lower
                topology_summary.loc[idx, "distance_ci_upper"] = distance_ci_upper
        
        summaries["topology"] = topology_summary
        print(f"✅ Stage 5: Topology Summaries - {len(topology_summary)} rho values")
    
    # Recovery scaling summaries with bootstrap CI
    if recovery is not None and not recovery.empty:
        # Group by metric, horizon_system, branch, rho and compute summaries
        # Include both raw event times AND censoring-aware restricted times
        recovery_summary = recovery.groupby(
            ["rho", "branch", "horizon_system", "metric"],
            as_index=False,
        ).agg(
            # Raw event times (conditional on observed recovery)
            mean_first_crossing=("first_crossing_time", "mean"),
            std_first_crossing=("first_crossing_time", "std"),
            n_first_crossing=("first_crossing_time", "count"),
            mean_sustained=("sustained_time", "mean"),
            std_sustained=("sustained_time", "std"),
            n_sustained=("sustained_time", "count"),
            mean_held=("held_time", "mean"),
            std_held=("held_time", "std"),
            n_held=("held_time", "count"),
            mean_auc_deficit=("auc_deficit_vs_continue", "mean"),
            std_auc_deficit=("auc_deficit_vs_continue", "std"),
            n_auc_deficit=("auc_deficit_vs_continue", "count"),
            
            # Censoring-aware restricted times (cohort-level estimates)
            mean_restricted_first=("restricted_first_crossing_time", "mean"),
            std_restricted_first=("restricted_first_crossing_time", "std"),
            n_restricted_first=("restricted_first_crossing_time", "count"),
            mean_restricted_sustained=("restricted_sustained_time", "mean"),
            std_restricted_sustained=("restricted_sustained_time", "std"),
            n_restricted_sustained=("restricted_sustained_time", "count"),
            mean_restricted_held=("restricted_held_time", "mean"),
            std_restricted_held=("restricted_held_time", "std"),
            n_restricted_held=("restricted_held_time", "count"),
            
            # Normalized times (t/T_window) - raw observed (conditional on recovery)
            mean_first_over_Twindow=("first_crossing_over_Twindow", "mean"),
            std_first_over_Twindow=("first_crossing_over_Twindow", "std"),
            n_first_over_Twindow=("first_crossing_over_Twindow", "count"),
            mean_sustained_over_Twindow=("sustained_time_over_Twindow", "mean"),
            std_sustained_over_Twindow=("sustained_time_over_Twindow", "std"),
            n_sustained_over_Twindow=("sustained_time_over_Twindow", "count"),
            mean_held_over_Twindow=("held_time_over_Twindow", "mean"),
            std_held_over_Twindow=("held_time_over_Twindow", "std"),
            n_held_over_Twindow=("held_time_over_Twindow", "count"),
            
            # Censoring-aware restricted normalized times (cohort-level estimates)
            mean_restricted_first_over_Twindow=("restricted_first_over_Twindow", "mean"),
            std_restricted_first_over_Twindow=("restricted_first_over_Twindow", "std"),
            n_restricted_first_over_Twindow=("restricted_first_over_Twindow", "count"),
            mean_restricted_sustained_over_Twindow=("restricted_sustained_over_Twindow", "mean"),
            std_restricted_sustained_over_Twindow=("restricted_sustained_over_Twindow", "std"),
            n_restricted_sustained_over_Twindow=("restricted_sustained_over_Twindow", "count"),
            mean_restricted_held_over_Twindow=("restricted_held_over_Twindow", "mean"),
            std_restricted_held_over_Twindow=("restricted_held_over_Twindow", "std"),
            n_restricted_held_over_Twindow=("restricted_held_over_Twindow", "count"),
            
            # Recovery probabilities
            observed_rate_first=("first_crossing_observed", "mean"),
            observed_rate_sustained=("sustained_observed", "mean"),
            observed_rate_held=("held_observed", "mean"),
        )
        
        # Add bootstrap CI for recovery metrics
        for (rho, branch, horizon_system, metric), group in recovery.groupby(["rho", "branch", "horizon_system", "metric"]):
            # Bootstrap first crossing time (conditional on observed)
            first_crossing_values = group["first_crossing_time"].dropna().values
            if len(first_crossing_values) > 0:
                indices = rng.integers(0, len(first_crossing_values), size=(n_bootstrap, len(first_crossing_values)))
                bootstrap_means = np.nanmean(first_crossing_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_first_crossing"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_first_crossing"] = ci_upper
            
            # Bootstrap restricted first crossing time (cohort-level, includes censored)
            restricted_first_values = group["restricted_first_crossing_time"].dropna().values
            if len(restricted_first_values) > 0:
                indices = rng.integers(0, len(restricted_first_values), size=(n_bootstrap, len(restricted_first_values)))
                bootstrap_means = np.nanmean(restricted_first_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_restricted_first"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_restricted_first"] = ci_upper
            
            # Bootstrap restricted sustained time
            restricted_sustained_values = group["restricted_sustained_time"].dropna().values
            if len(restricted_sustained_values) > 0:
                indices = rng.integers(0, len(restricted_sustained_values), size=(n_bootstrap, len(restricted_sustained_values)))
                bootstrap_means = np.nanmean(restricted_sustained_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_restricted_sustained"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_restricted_sustained"] = ci_upper
            
            # Bootstrap restricted held time
            restricted_held_values = group["restricted_held_time"].dropna().values
            if len(restricted_held_values) > 0:
                indices = rng.integers(0, len(restricted_held_values), size=(n_bootstrap, len(restricted_held_values)))
                bootstrap_means = np.nanmean(restricted_held_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_restricted_held"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_restricted_held"] = ci_upper
            
            # Bootstrap normalized first crossing time over T_window
            first_over_Twindow_values = group["first_crossing_over_Twindow"].dropna().values
            if len(first_over_Twindow_values) > 0:
                indices = rng.integers(0, len(first_over_Twindow_values), size=(n_bootstrap, len(first_over_Twindow_values)))
                bootstrap_means = np.nanmean(first_over_Twindow_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_first_over_Twindow"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_first_over_Twindow"] = ci_upper
            
            # Bootstrap normalized sustained time over T_window
            sustained_over_Twindow_values = group["sustained_time_over_Twindow"].dropna().values
            if len(sustained_over_Twindow_values) > 0:
                indices = rng.integers(0, len(sustained_over_Twindow_values), size=(n_bootstrap, len(sustained_over_Twindow_values)))
                bootstrap_means = np.nanmean(sustained_over_Twindow_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_sustained_over_Twindow"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_sustained_over_Twindow"] = ci_upper
            
            # Bootstrap normalized held time over T_window
            held_over_Twindow_values = group["held_time_over_Twindow"].dropna().values
            if len(held_over_Twindow_values) > 0:
                indices = rng.integers(0, len(held_over_Twindow_values), size=(n_bootstrap, len(held_over_Twindow_values)))
                bootstrap_means = np.nanmean(held_over_Twindow_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_held_over_Twindow"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_held_over_Twindow"] = ci_upper
            
            # Bootstrap AUC deficit
            auc_values = group["auc_deficit_vs_continue"].dropna().values
            if len(auc_values) > 0:
                indices = rng.integers(0, len(auc_values), size=(n_bootstrap, len(auc_values)))
                bootstrap_means = np.nanmean(auc_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_auc_deficit"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_auc_deficit"] = ci_upper
            
            # Bootstrap restricted normalized first crossing time over T_window
            restricted_first_over_Twindow_values = group["restricted_first_over_Twindow"].dropna().values
            if len(restricted_first_over_Twindow_values) > 0:
                indices = rng.integers(0, len(restricted_first_over_Twindow_values), size=(n_bootstrap, len(restricted_first_over_Twindow_values)))
                bootstrap_means = np.nanmean(restricted_first_over_Twindow_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_restricted_first_over_Twindow"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_restricted_first_over_Twindow"] = ci_upper
            
            # Bootstrap restricted normalized sustained time over T_window
            restricted_sustained_over_Twindow_values = group["restricted_sustained_over_Twindow"].dropna().values
            if len(restricted_sustained_over_Twindow_values) > 0:
                indices = rng.integers(0, len(restricted_sustained_over_Twindow_values), size=(n_bootstrap, len(restricted_sustained_over_Twindow_values)))
                bootstrap_means = np.nanmean(restricted_sustained_over_Twindow_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_restricted_sustained_over_Twindow"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_restricted_sustained_over_Twindow"] = ci_upper
            
            # Bootstrap restricted normalized held time over T_window
            restricted_held_over_Twindow_values = group["restricted_held_over_Twindow"].dropna().values
            if len(restricted_held_over_Twindow_values) > 0:
                indices = rng.integers(0, len(restricted_held_over_Twindow_values), size=(n_bootstrap, len(restricted_held_over_Twindow_values)))
                bootstrap_means = np.nanmean(restricted_held_over_Twindow_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_restricted_held_over_Twindow"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_restricted_held_over_Twindow"] = ci_upper
            
            # Bootstrap recovery probabilities (observed rates)
            # First crossing observed rate
            first_observed_values = group["first_crossing_observed"].dropna().values
            if len(first_observed_values) > 0:
                indices = rng.integers(0, len(first_observed_values), size=(n_bootstrap, len(first_observed_values)))
                bootstrap_means = np.nanmean(first_observed_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_observed_rate_first"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_observed_rate_first"] = ci_upper
            
            # Sustained observed rate
            sustained_observed_values = group["sustained_observed"].dropna().values
            if len(sustained_observed_values) > 0:
                indices = rng.integers(0, len(sustained_observed_values), size=(n_bootstrap, len(sustained_observed_values)))
                bootstrap_means = np.nanmean(sustained_observed_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_observed_rate_sustained"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_observed_rate_sustained"] = ci_upper
            
            # Held observed rate
            held_observed_values = group["held_observed"].dropna().values
            if len(held_observed_values) > 0:
                indices = rng.integers(0, len(held_observed_values), size=(n_bootstrap, len(held_observed_values)))
                bootstrap_means = np.nanmean(held_observed_values[indices], axis=1)
                ci_lower = float(np.nanpercentile(bootstrap_means, 2.5))
                ci_upper = float(np.nanpercentile(bootstrap_means, 97.5))
                
                idx = recovery_summary[
                    (recovery_summary["rho"] == rho) & 
                    (recovery_summary["branch"] == branch) &
                    (recovery_summary["horizon_system"] == horizon_system) &
                    (recovery_summary["metric"] == metric)
                ].index
                recovery_summary.loc[idx, "ci_lower_observed_rate_held"] = ci_lower
                recovery_summary.loc[idx, "ci_upper_observed_rate_held"] = ci_upper
        
        summaries["recovery"] = recovery_summary
        print(f"✅ Stage 5: Recovery Summaries - {len(recovery_summary)} groups")
    
    return summaries


# =============================================================================
# Report Generation
# =============================================================================

def generate_text_report(
    validation: dict[str, Any],
    regime_contrasts: pd.DataFrame,
    branch_did: pd.DataFrame,
    topology: pd.DataFrame,
    regime_summaries: pd.DataFrame,
    did_summaries: pd.DataFrame,
    topology_summaries: pd.DataFrame,
    recovery_summaries: pd.DataFrame | None = None,
    regime_summaries_secondary: pd.DataFrame | None = None,
    did_summaries_secondary: pd.DataFrame | None = None,
    recovery_did_summary: pd.DataFrame | None = None,
) -> str:
    """Generate human-readable text report."""
    lines = []
    lines.append("=" * 80)
    lines.append("AIEF-1.4 T_window Sensitivity Study - Analysis Report")
    lines.append("=" * 80)
    lines.append("")
    
    # Validation summary
    lines.append("VALIDATION SUMMARY")
    lines.append("-" * 40)
    val = validation.get("validation", {})
    lines.append(f"  Status: {validation.get('status', 'unknown')}")
    lines.append(f"  Rows: {val.get('n_rows', 0)} (expected: {EXPECTED_N_ROWS})")
    lines.append(f"  Seeds: {val.get('n_seeds', 0)} (expected: {EXPECTED_N_SEEDS})")
    lines.append(f"  Rho values: {val.get('n_rho', 0)} (expected: {len(EXPECTED_RHO_VALUES)})")
    lines.append(f"  Branches: {val.get('n_branches', 0)} (expected: {len(EXPECTED_BRANCHES)})")
    lines.append(f"  Duplicates: {val.get('n_duplicates', 0)}")
    lines.append(f"  Missing combinations: {val.get('n_missing_combinations', 0)}")
    lines.append(f"  Baseline equivalence: {val.get('baseline_equivalence', 'unknown')}")
    lines.append(f"  Freezeable: {val.get('freezeable', False)}")
    lines.append("")
    
    # Regime contrasts (Primary - fixed_physical horizons)
    lines.append("REGIME CONTRASTS (Δ = Y_{s,ρ,continue} - Y_{s,1,continue})")
    lines.append("-" * 40)
    lines.append("Primary outcomes: fixed_physical horizons")
    lines.append("")
    if not regime_summaries.empty:
        for rho in sorted(regime_summaries["rho"].unique()):
            rho_data = regime_summaries[regime_summaries["rho"] == rho]
            for outcome in PRIMARY_OUTCOMES:
                out_data = rho_data[rho_data["outcome"] == outcome]
                if not out_data.empty:
                    mean_val = float(out_data["mean"].iloc[0])
                    std_val = float(out_data["std"].iloc[0])
                    n_val = int(out_data["n"].iloc[0])
                    ci_lower = float(out_data.get("ci_lower", float('nan')).iloc[0])
                    ci_upper = float(out_data.get("ci_upper", float('nan')).iloc[0])
                    
                    ci_str = f"[{ci_lower:.4f}, {ci_upper:.4f}]" if not np.isnan(ci_lower) else "N/A"
                    lines.append(f"  rho={rho:.2f}, {outcome}: {mean_val:.4f} ± {std_val:.4f} {ci_str} (n={n_val})")
    else:
        lines.append("  No regime contrast data")
    lines.append("")
    
    # Secondary regime contrasts (normalized_EMA horizons)
    lines.append("SECONDARY REGIME CONTRASTS (Normalized EMA horizons)")
    lines.append("-" * 40)
    if regime_summaries_secondary is not None and not regime_summaries_secondary.empty:
        for rho in sorted(regime_summaries_secondary["rho"].unique()):
            rho_data = regime_summaries_secondary[regime_summaries_secondary["rho"] == rho]
            for outcome in SECONDARY_NORMALIZED_OUTCOMES:
                out_data = rho_data[rho_data["outcome"] == outcome]
                if not out_data.empty:
                    mean_val = float(out_data["mean"].iloc[0])
                    std_val = float(out_data["std"].iloc[0])
                    n_val = int(out_data["n"].iloc[0])
                    ci_lower = float(out_data.get("ci_lower", float('nan')).iloc[0])
                    ci_upper = float(out_data.get("ci_upper", float('nan')).iloc[0])
                    
                    ci_str = f"[{ci_lower:.4f}, {ci_upper:.4f}]" if not np.isnan(ci_lower) else "N/A"
                    lines.append(f"  rho={rho:.2f}, {outcome}: {mean_val:.4f} ± {std_val:.4f} {ci_str} (n={n_val})")
    else:
        lines.append("  No secondary regime contrast data")
    lines.append("")
    
    # Branch DID (Primary - fixed_physical horizons)
    lines.append("BRANCH DIFFERENCE-IN-DIFFERENCES")
    lines.append("-" * 40)
    lines.append("I_{s,ρ,b} = [Y_{s,ρ,b} - Y_{s,ρ,continue}] - [Y_{s,1,b} - Y_{s,1,continue}]")
    lines.append("Primary outcomes: fixed_physical horizons")
    lines.append("")
    if not did_summaries.empty:
        for rho in sorted(did_summaries["rho"].unique()):
            rho_data = did_summaries[did_summaries["rho"] == rho]
            for branch in sorted(rho_data["branch"].unique()):
                branch_data = rho_data[rho_data["branch"] == branch]
                for outcome in PRIMARY_OUTCOMES:
                    out_data = branch_data[branch_data["outcome"] == outcome]
                    if not out_data.empty:
                        mean_val = float(out_data["mean"].iloc[0])
                        std_val = float(out_data["std"].iloc[0])
                        n_val = int(out_data["n"].iloc[0])
                        ci_lower = float(out_data.get("ci_lower", float('nan')).iloc[0])
                        ci_upper = float(out_data.get("ci_upper", float('nan')).iloc[0])
                        
                        ci_str = f"[{ci_lower:.4f}, {ci_upper:.4f}]" if not np.isnan(ci_lower) else "N/A"
                        lines.append(f"  rho={rho:.2f}, branch={branch}, {outcome}: {mean_val:.4f} ± {std_val:.4f} {ci_str} (n={n_val})")
    else:
        lines.append("  No branch DID data")
    lines.append("")
    
    # Secondary Branch DID (normalized_EMA horizons)
    lines.append("SECONDARY BRANCH DIFFERENCE-IN-DIFFERENCES (Normalized EMA)")
    lines.append("-" * 40)
    if did_summaries_secondary is not None and not did_summaries_secondary.empty:
        for rho in sorted(did_summaries_secondary["rho"].unique()):
            rho_data = did_summaries_secondary[did_summaries_secondary["rho"] == rho]
            for branch in sorted(rho_data["branch"].unique()):
                branch_data = rho_data[rho_data["branch"] == branch]
                for outcome in SECONDARY_NORMALIZED_OUTCOMES:
                    out_data = branch_data[branch_data["outcome"] == outcome]
                    if not out_data.empty:
                        mean_val = float(out_data["mean"].iloc[0])
                        std_val = float(out_data["std"].iloc[0])
                        n_val = int(out_data["n"].iloc[0])
                        ci_lower = float(out_data.get("ci_lower", float('nan')).iloc[0])
                        ci_upper = float(out_data.get("ci_upper", float('nan')).iloc[0])
                        
                        ci_str = f"[{ci_lower:.4f}, {ci_upper:.4f}]" if not np.isnan(ci_lower) else "N/A"
                        lines.append(f"  rho={rho:.2f}, branch={branch}, {outcome}: {mean_val:.4f} ± {std_val:.4f} {ci_str} (n={n_val})")
    else:
        lines.append("  No secondary branch DID data")
    lines.append("")
    
    # Cross-T topology
    lines.append("CROSS-T TOPOLOGY METRICS")
    lines.append("-" * 40)
    if not topology_summaries.empty:
        for _, row in topology_summaries.iterrows():
            rho = float(row["rho"])
            lines.append(f"  rho={rho:.2f}:")
            lines.append(f"    Cosine similarity: {float(row['cosine_mean']):.4f} ± {float(row['cosine_std']):.4f} (n={int(row['cosine_n'])})")
            if "cosine_ci_lower" in row and not np.isnan(float(row.get("cosine_ci_lower", float('nan')))):
                lines.append(f"      95% CI: [{float(row['cosine_ci_lower']):.4f}, {float(row['cosine_ci_upper']):.4f}]")
            lines.append(f"    Jaccard similarity: {float(row['jaccard_mean']):.4f} ± {float(row['jaccard_std']):.4f} (n={int(row['jaccard_n'])})")
            if "jaccard_ci_lower" in row and not np.isnan(float(row.get("jaccard_ci_lower", float('nan')))):
                lines.append(f"      95% CI: [{float(row['jaccard_ci_lower']):.4f}, {float(row['jaccard_ci_upper']):.4f}]")
            lines.append(f"    Normalized distance: {float(row['distance_mean']):.4f} ± {float(row['distance_std']):.4f} (n={int(row['distance_n'])})")
            if "distance_ci_lower" in row and not np.isnan(float(row.get("distance_ci_lower", float('nan')))):
                lines.append(f"      95% CI: [{float(row['distance_ci_lower']):.4f}, {float(row['distance_ci_upper']):.4f}]")
    else:
        lines.append("  No cross-T topology data")
    lines.append("")
    
    # Recovery scaling metrics
    lines.append("RECOVERY SCALING METRICS")
    lines.append("-" * 40)
    lines.append("Cohort-level estimates (censoring-aware) and conditional-on-recovery estimates")
    lines.append("")
    if recovery_summaries is not None and not recovery_summaries.empty:
        for _, row in recovery_summaries.iterrows():
            rho = float(row["rho"])
            branch = str(row["branch"])
            horizon_system = str(row["horizon_system"])
            metric = str(row["metric"])
            lines.append(f"  rho={rho:.2f}, branch={branch}, {horizon_system}, {metric}:")
            
            # Cohort-level estimates (includes censored) - restricted times
            lines.append(f"    Cohort-level estimates (all seeds, censoring-aware):")
            lines.append(f"      Mean restricted first crossing: {float(row['mean_restricted_first']):.4f} ± {float(row['std_restricted_first']):.4f} (n={int(row['n_restricted_first'])})")
            if "ci_lower_restricted_first" in row and not np.isnan(float(row.get("ci_lower_restricted_first", float('nan')))):
                lines.append(f"        95% CI: [{float(row['ci_lower_restricted_first']):.4f}, {float(row['ci_upper_restricted_first']):.4f}]")
            lines.append(f"      Mean restricted sustained: {float(row['mean_restricted_sustained']):.4f} ± {float(row['std_restricted_sustained']):.4f} (n={int(row['n_restricted_sustained'])})")
            if "ci_lower_restricted_sustained" in row and not np.isnan(float(row.get("ci_lower_restricted_sustained", float('nan')))):
                lines.append(f"        95% CI: [{float(row['ci_lower_restricted_sustained']):.4f}, {float(row['ci_upper_restricted_sustained']):.4f}]")
            lines.append(f"      Mean restricted held: {float(row['mean_restricted_held']):.4f} ± {float(row['std_restricted_held']):.4f} (n={int(row['n_restricted_held'])})")
            if "ci_lower_restricted_held" in row and not np.isnan(float(row.get("ci_lower_restricted_held", float('nan')))):
                lines.append(f"        95% CI: [{float(row['ci_lower_restricted_held']):.4f}, {float(row['ci_upper_restricted_held']):.4f}]")
            lines.append(f"      AUC deficit: {float(row['mean_auc_deficit']):.4f} ± {float(row['std_auc_deficit']):.4f} (n={int(row['n_auc_deficit'])})")
            if "ci_lower_auc_deficit" in row and not np.isnan(float(row.get("ci_lower_auc_deficit", float('nan')))):
                lines.append(f"        95% CI: [{float(row['ci_lower_auc_deficit']):.4f}, {float(row['ci_upper_auc_deficit']):.4f}]")
            
            # Cohort-level normalized times (restricted t/T_window)
            lines.append(f"    Cohort-level normalized times (restricted, all seeds):")
            lines.append(f"      Mean restricted first/t_window: {float(row.get('mean_restricted_first_over_Twindow', float('nan'))):.4f} ± {float(row.get('std_restricted_first_over_Twindow', float('nan'))):.4f} (n={int(row.get('n_restricted_first_over_Twindow', 0))})")
            if "ci_lower_restricted_first_over_Twindow" in row and not np.isnan(float(row.get("ci_lower_restricted_first_over_Twindow", float('nan')))):
                lines.append(f"        95% CI: [{float(row['ci_lower_restricted_first_over_Twindow']):.4f}, {float(row['ci_upper_restricted_first_over_Twindow']):.4f}]")
            lines.append(f"      Mean restricted sustained/t_window: {float(row.get('mean_restricted_sustained_over_Twindow', float('nan'))):.4f} ± {float(row.get('std_restricted_sustained_over_Twindow', float('nan'))):.4f} (n={int(row.get('n_restricted_sustained_over_Twindow', 0))})")
            if "ci_lower_restricted_sustained_over_Twindow" in row and not np.isnan(float(row.get("ci_lower_restricted_sustained_over_Twindow", float('nan')))):
                lines.append(f"        95% CI: [{float(row['ci_lower_restricted_sustained_over_Twindow']):.4f}, {float(row['ci_upper_restricted_sustained_over_Twindow']):.4f}]")
            lines.append(f"      Mean restricted held/t_window: {float(row.get('mean_restricted_held_over_Twindow', float('nan'))):.4f} ± {float(row.get('std_restricted_held_over_Twindow', float('nan'))):.4f} (n={int(row.get('n_restricted_held_over_Twindow', 0))})")
            if "ci_lower_restricted_held_over_Twindow" in row and not np.isnan(float(row.get("ci_lower_restricted_held_over_Twindow", float('nan')))):
                lines.append(f"        95% CI: [{float(row['ci_lower_restricted_held_over_Twindow']):.4f}, {float(row['ci_upper_restricted_held_over_Twindow']):.4f}]")
            
            # Recovery probabilities with CI
            lines.append(f"    Recovery probabilities (with 95% bootstrap CI):")
            lines.append(f"      First crossing observed: {float(row['observed_rate_first']):.4f}")
            if "ci_lower_observed_rate_first" in row and not np.isnan(float(row.get("ci_lower_observed_rate_first", float('nan')))):
                lines.append(f"        95% CI: [{float(row['ci_lower_observed_rate_first']):.4f}, {float(row['ci_upper_observed_rate_first']):.4f}]")
            lines.append(f"      Sustained recovery observed: {float(row['observed_rate_sustained']):.4f}")
            if "ci_lower_observed_rate_sustained" in row and not np.isnan(float(row.get("ci_lower_observed_rate_sustained", float('nan')))):
                lines.append(f"        95% CI: [{float(row['ci_lower_observed_rate_sustained']):.4f}, {float(row['ci_upper_observed_rate_sustained']):.4f}]")
            lines.append(f"      Held recovery observed: {float(row['observed_rate_held']):.4f}")
            if "ci_lower_observed_rate_held" in row and not np.isnan(float(row.get("ci_lower_observed_rate_held", float('nan')))):
                lines.append(f"        95% CI: [{float(row['ci_lower_observed_rate_held']):.4f}, {float(row['ci_upper_observed_rate_held']):.4f}]")
            
            # Conditional-on-recovery estimates (observed seeds only)
            lines.append(f"    Conditional-on-recovery estimates (observed seeds only):")
            lines.append(f"      First crossing: {float(row['mean_first_crossing']):.4f} ± {float(row['std_first_crossing']):.4f} (n={int(row['n_first_crossing'])})")
            if "ci_lower_first_crossing" in row and not np.isnan(float(row.get("ci_lower_first_crossing", float('nan')))):
                lines.append(f"        95% CI (conditional): [{float(row['ci_lower_first_crossing']):.4f}, {float(row['ci_upper_first_crossing']):.4f}]")
            lines.append(f"      Sustained: {float(row['mean_sustained']):.4f} ± {float(row['std_sustained']):.4f} (n={int(row['n_sustained'])})")
            if "ci_lower_sustained" in row and not np.isnan(float(row.get("ci_lower_sustained", float('nan')))):
                lines.append(f"        95% CI (conditional): [{float(row['ci_lower_sustained']):.4f}, {float(row['ci_upper_sustained']):.4f}]")
            lines.append(f"      Held: {float(row['mean_held']):.4f} ± {float(row['std_held']):.4f} (n={int(row['n_held'])})")
            if "ci_lower_held" in row and not np.isnan(float(row.get("ci_lower_held", float('nan')))):
                lines.append(f"        95% CI (conditional): [{float(row['ci_lower_held']):.4f}, {float(row['ci_upper_held']):.4f}]")
            
            # Conditional-on-recovery normalized times (observed seeds only)
            lines.append(f"    Conditional-on-recovery normalized times (observed seeds only):")
            lines.append(f"      First crossing/t_window: {float(row['mean_first_over_Twindow']):.4f} ± {float(row['std_first_over_Twindow']):.4f} (n={int(row['n_first_over_Twindow'])})")
            if "ci_lower_first_over_Twindow" in row and not np.isnan(float(row.get("ci_lower_first_over_Twindow", float('nan')))):
                lines.append(f"        95% CI (conditional): [{float(row['ci_lower_first_over_Twindow']):.4f}, {float(row['ci_upper_first_over_Twindow']):.4f}]")
            lines.append(f"      Sustained/t_window: {float(row['mean_sustained_over_Twindow']):.4f} ± {float(row['std_sustained_over_Twindow']):.4f} (n={int(row['n_sustained_over_Twindow'])})")
            if "ci_lower_sustained_over_Twindow" in row and not np.isnan(float(row.get("ci_lower_sustained_over_Twindow", float('nan')))):
                lines.append(f"        95% CI (conditional): [{float(row['ci_lower_sustained_over_Twindow']):.4f}, {float(row['ci_upper_sustained_over_Twindow']):.4f}]")
            lines.append(f"      Held/t_window: {float(row['mean_held_over_Twindow']):.4f} ± {float(row['std_held_over_Twindow']):.4f} (n={int(row['n_held_over_Twindow'])})")
            if "ci_lower_held_over_Twindow" in row and not np.isnan(float(row.get("ci_lower_held_over_Twindow", float('nan')))):
                lines.append(f"        95% CI (conditional): [{float(row['ci_lower_held_over_Twindow']):.4f}, {float(row['ci_upper_held_over_Twindow']):.4f}]")
    else:
        lines.append("  No recovery scaling data")
    lines.append("")
    
    # Recovery interaction DID
    lines.append("RECOVERY INTERACTION DID")
    lines.append("-" * 40)
    lines.append("I_{s,ρ,b}^recovery = [R_{s,ρ,b} - R_{s,ρ,continue}] - [R_{s,1,b} - R_{s,1,continue}]")
    lines.append("")
    if recovery_did_summary is not None and not recovery_did_summary.empty:
        for _, row in recovery_did_summary.iterrows():
            rho = float(row["rho"])
            branch = str(row["branch"])
            horizon_system = str(row["horizon_system"])
            metric = str(row["metric"])
            outcome = str(row["outcome"])
            lines.append(f"  rho={rho:.2f}, branch={branch}, {horizon_system}, {metric}, {outcome}:")
            mean_val = float(row["mean"])
            std_val = float(row["std"])
            n_val = int(row["n"])
            ci_lower = float(row.get("ci_lower", float('nan')))
            ci_upper = float(row.get("ci_upper", float('nan')))
            
            ci_str = f"[{ci_lower:.4f}, {ci_upper:.4f}]" if not np.isnan(ci_lower) else "N/A"
            lines.append(f"    DID: {mean_val:.4f} ± {std_val:.4f} {ci_str} (n={n_val})")
    else:
        lines.append("  No recovery DID data")
    lines.append("")
    
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def generate_analysis_manifest(
    csv_path: Path,
    npz_path: Path,
    manifest_path: Path,
    validation: dict[str, Any],
    output_files: dict[str, Path],
    source_path: Path,
    bootstrap_seed: int,
    n_bootstrap: int,
    command_line: str,
) -> dict[str, Any]:
    """Generate analysis manifest with complete provenance."""
    # Compute hashes
    csv_hash = file_sha256(csv_path)
    npz_hash = file_sha256(npz_path)
    manifest_hash = file_sha256(manifest_path)
    source_hash = file_sha256(source_path)
    
    output_hashes = {}
    for name, path in output_files.items():
        output_hashes[name] = file_sha256(path)
    
    manifest = {
        "analysis_version": ANALYSIS_VERSION,
        "timestamp": int(time.time()),
        "study_name": STUDY_NAME,
        
        "source": {
            "path": str(source_path),
            "sha256": source_hash,
        },
        
        "command_line": command_line,
        
        "bootstrap": {
            "seed": bootstrap_seed,
            "n_iterations": n_bootstrap,
        },
        
        "input_hashes": {
            "scalar_csv": csv_hash,
            "branch_npz": npz_hash,
            "simulation_manifest": manifest_hash,
            "condition_status": validation.get("condition_status_hash", "NOT_FOUND"),
            "baseline_certificate": validation.get("baseline_certificate_hash", "NOT_FOUND"),
        },
        
        "validation": validation,
        
        "output_hashes": output_hashes,
        
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
        
        "notes": {
            "primary_outcomes": list(PRIMARY_OUTCOMES),
            "secondary_outcomes": list(SECONDARY_NORMALIZED_OUTCOMES),
            "expected_n_seeds": EXPECTED_N_SEEDS,
            "expected_rho_values": [float(r) for r in EXPECTED_RHO_VALUES],
            "expected_branches": list(EXPECTED_BRANCHES),
            "expected_n_regime_contrasts": EXPECTED_N_REGIME_CONTRASTS,
            "expected_n_did": EXPECTED_N_DID,
            "expected_n_topology": EXPECTED_N_TOPOLOGY,
            # P1 #17: Add recovery expected counts
            "expected_n_recovery_rows": 3200,
            "expected_n_recovery_groups": EXPECTED_N_RECOVERY_GROUPS,
            "expected_n_recovery_did_rows": EXPECTED_N_RECOVERY_DID,
            "expected_n_recovery_did_groups": EXPECTED_N_RECOVERY_DID_GROUPS,
            # P1 #9, #10, #11: Document conventions
            "similarity_nan_recovery_convention": "undefined zero-vector cosine imputed as zero for recovery and AUC only",
            "density_horizon_duplication": "Density recovery rows are duplicated across horizon_system by design. They are horizon-independent and must not be pooled across the two labels.",
            "discrete_held_duration_convention": "ceil(T_window / diagnostic_sample_spacing) consecutive saved samples",
            "horizon_definitions": {
                "fixed_physical": {
                    "immediate": "0-17.5 time units",
                    "recovery": "17.5-87.5 time units", 
                    "late": "87.5-320 time units"
                },
                "normalized_EMA": {
                    "immediate": "0-1×T_window",
                    "recovery": "1-5×T_window",
                    "late": "5×T_window to end"
                }
            },
            "interpretation_constraints": {
                "primary_estimand": "fixed_physical horizons",
                "secondary_estimand": "normalized_EMA horizons",
                "recovery_metrics": "t_rec/T_window for both horizon systems"
            }
        },
    }
    
    return manifest


# =============================================================================
# Main Execution
# =============================================================================

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "run_dir",
        type=str,
        help="run directory containing study outputs",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="output directory for analysis (default: <run_dir>/analysis)",
    )
    parser.add_argument(
        "--n-bootstrap",
        type=int,
        default=1000,
        help="number of bootstrap iterations (default: 1000)",
    )
    parser.add_argument(
        "--bootstrap-seed",
        type=int,
        required=True,
        help="random seed for bootstrap reproducibility (REQUIRED)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="overwrite existing output files (default: fail if outputs exist)",
    )
    return parser.parse_args()


def validate_bootstrap_args(args):
    """Validate bootstrap arguments."""
    if args.n_bootstrap <= 0:
        raise ValueError("--n-bootstrap must be positive")
    if args.bootstrap_seed is None:
        raise ValueError("--bootstrap-seed is required")
    return True


def main() -> None:
    args = parse_arguments()
    
    # Validate bootstrap arguments
    validate_bootstrap_args(args)
    
    # Parse run directory
    run_dir = Path(args.run_dir)
    csv_files = list(run_dir.glob(f"{STUDY_NAME}_*_scalar_summary.csv"))
    npz_files = list(run_dir.glob(f"{STUDY_NAME}_*_branch_diagnostics.npz"))
    manifest_files = list(run_dir.glob("manifest.json"))
    
    if not csv_files:
        print(f"No CSV file found in {run_dir}")
        sys.exit(1)
    if not npz_files:
        print(f"No NPZ file found in {run_dir}")
        sys.exit(1)
    if not manifest_files:
        print(f"No manifest found in {run_dir}")
        sys.exit(1)
    
    # Require exactly one input CSV and NPZ
    if len(csv_files) != 1:
        print(f"Expected exactly one scalar CSV, found {len(csv_files)}: {[p.name for p in csv_files]}")
        sys.exit(1)
    if len(npz_files) != 1:
        print(f"Expected exactly one branch NPZ, found {len(npz_files)}: {[p.name for p in npz_files]}")
        sys.exit(1)
    if len(manifest_files) != 1:
        print(f"Expected exactly one manifest, found {len(manifest_files)}")
        sys.exit(1)
    
    csv_path = csv_files[0]
    npz_path = npz_files[0]
    manifest_path = manifest_files[0]
    
    # P1 #12: Validate inputs BEFORE deleting stale outputs
    # This prevents malformed runs from causing deletion of valid previous analysis
    print(f"Analyzing {run_dir}")
    print(f"  CSV: {csv_path.name}")
    print(f"  NPZ: {npz_path.name}")
    print(f"  Manifest: {manifest_path.name}")
    print()
    
    # Stage 1: Validation - MUST HAPPEN BEFORE any file operations
    print("Stage 1: Validating run...")
    validation = validate_run(csv_path, npz_path, manifest_path)
    
    if validation["status"] == "failed":
        print("\n❌ VALIDATION FAILED - Cannot proceed with analysis")
        for error in validation["errors"]:
            print(f"  {error}")
        for warning in validation["warnings"]:
            print(f"  WARNING: {warning}")
        sys.exit(1)
    
    # Set up output directory with stale-file protection
    if args.output is None:
        output_dir = run_dir / "analysis"
    else:
        output_dir = Path(args.output)
    
    # Save command line for manifest
    command_line = " ".join(sys.argv)
    
    # Now that validation passed, check for and remove stale files
    expected_outputs = [
        "twindow_paired_regime_contrasts.csv",
        "twindow_paired_regime_contrasts_fixed_physical.csv",
        "twindow_paired_regime_contrasts_normalized_EMA.csv",
        "twindow_branch_interactions.csv",
        "twindow_branch_interactions_fixed_physical.csv", 
        "twindow_branch_interactions_normalized_EMA.csv",
        "twindow_cross_condition_topology.csv",
        "twindow_recovery_by_seed.csv",
        "twindow_recovery_summary.csv",
        "twindow_regime_summary.csv",
        "twindow_branch_DID_summary.csv",
        "twindow_topology_summary.csv",
        "twindow_regime_secondary_summary.csv",
        "twindow_branch_DID_secondary_summary.csv",
        "twindow_recovery_interactions.csv",
        "twindow_recovery_interactions_summary.csv",
        "twindow_sensitivity_report.txt",
        "analysis_manifest.json",
    ]
    
    stale_files = []
    if output_dir.exists():
        for expected_file in expected_outputs:
            file_path = output_dir / expected_file
            if file_path.exists():
                stale_files.append(expected_file)
        
        if stale_files and not args.overwrite:
            print(f"❌ Output directory contains stale files: {stale_files[:5]}...")
            print(f"   Use --overwrite to force overwrite, or specify a different --output directory")
            print(f"   This prevents mixing outputs from different analysis versions.")
            sys.exit(1)
        
        # If --overwrite is passed, remove ALL expected files before starting
        if stale_files and args.overwrite:
            print(f"  Removing {len(stale_files)} stale files from output directory...")
            for expected_file in expected_outputs:
                file_path = output_dir / expected_file
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except Exception as e:
                        print(f"  WARNING: Could not remove stale file {expected_file}: {e}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"  Output: {output_dir}")
    print(f"  Bootstrap: {args.n_bootstrap} iterations, seed={args.bootstrap_seed}")
    print()
    
    # Load CSV data
    print("\nLoading scalar data...")
    df = load_csv_atomic(csv_path)
    
    # Get study parameters from manifest
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    seeds = [str(s) for s in manifest["randomization"]["paired_seeds"]]
    # Handle both manifest formats for rho_values
    if "study" in manifest and "rho_values" in manifest["study"]:
        rho_values = [float(r) for r in manifest["study"]["rho_values"]]
    elif "protocol" in manifest and "rho_values" in manifest["protocol"]:
        rho_values = [float(r) for r in manifest["protocol"]["rho_values"]]
    else:
        # If we can't find rho_values, use the unique values from the data
        rho_values = sorted([float(r) for r in df["rho"].unique()])
    branches = manifest["protocol"]["branches"]
    b_c = float(manifest["model"]["B_c"])
    
    print(f"  Loaded {len(df)} rows")
    print(f"  Seeds: {len(seeds)}, Rho: {len(rho_values)}, Branches: {len(branches)}")
    print(f"  B_c: {b_c}")
    
    # Stage 2: Regime Contrasts (Primary outcomes - fixed_physical)
    print("\nStage 2: Computing regime contrasts...")
    regime_contrasts = compute_regime_contrasts(df, PRIMARY_OUTCOMES)
    
    # Add horizon_system column to primary regime contrasts
    regime_contrasts["horizon_system"] = "fixed_physical"
    
    # Stage 2b: Regime Contrasts (Secondary normalized-EMA outcomes)
    print("\nStage 2b: Computing secondary regime contrasts...")
    regime_contrasts_secondary = compute_regime_contrasts(df, SECONDARY_NORMALIZED_OUTCOMES)
    
    # Add horizon_system column to secondary regime contrasts
    regime_contrasts_secondary["horizon_system"] = "normalized_EMA"
    
    # Combine primary and secondary regime contrasts into long format
    regime_contrasts_combined = pd.concat([regime_contrasts, regime_contrasts_secondary], ignore_index=True)
    
    # Stage 3: Branch DID (Primary outcomes - fixed_physical)
    print("\nStage 3: Computing branch difference-in-differences...")
    branch_did = compute_branch_did(df, PRIMARY_OUTCOMES)
    
    # Add horizon_system column to primary branch DID
    branch_did["horizon_system"] = "fixed_physical"
    
    # Stage 3b: Branch DID (Secondary normalized-EMA outcomes)
    print("\nStage 3b: Computing secondary branch difference-in-differences...")
    branch_did_secondary = compute_branch_did(df, SECONDARY_NORMALIZED_OUTCOMES)
    
    # Add horizon_system column to secondary branch DID
    branch_did_secondary["horizon_system"] = "normalized_EMA"
    
    # Combine primary and secondary branch DID into long format
    branch_did_combined = pd.concat([branch_did, branch_did_secondary], ignore_index=True)
    
    # Stage 4: Cross-T Topology
    print("\nStage 4: Computing cross-T topology metrics...")
    topology = compute_cross_t_topology(npz_path, seeds, rho_values, b_c)
    
    # Stage 4b: Recovery Scaling (REQUIRED for production)
    print("\nStage 4b: Computing recovery scaling metrics...")
    recovery = compute_recovery_scaling(df, npz_path)
    
    # Validate recovery groups have exactly 40 seeds each
    print("\n  Validating recovery group sizes...")
    recovery_group_sizes = recovery.groupby(
        ["rho", "branch", "horizon_system", "metric"]
    ).size()
    
    # P0 #5: Validate expected number of recovery groups
    if len(recovery_group_sizes) != EXPECTED_N_RECOVERY_GROUPS:
        raise RuntimeError(
            f"Expected {EXPECTED_N_RECOVERY_GROUPS} recovery groups, "
            f"got {len(recovery_group_sizes)}"
        )
    
    bad_groups = recovery_group_sizes[recovery_group_sizes != EXPECTED_N_SEEDS]
    if not bad_groups.empty:
        raise RuntimeError(
            f"Recovery groups do not all contain {EXPECTED_N_SEEDS} seed-level rows. "
            f"Bad groups: {bad_groups.head().to_dict()}"
        )
    
    # Validate restricted recovery fields have finite values
    print("  Validating restricted recovery fields...")
    for field in RESTRICTED_RECOVERY_FIELDS:
        non_finite = ~np.isfinite(pd.to_numeric(recovery[field], errors="coerce"))
        if non_finite.any():
            raise RuntimeError(
                f"Recovery field '{field}' has {int(non_finite.sum())} non-finite values"
            )
    
    print("  ✅ Recovery validation passed")
    
    # Stage 4c: Recovery Interaction DID
    print("\nStage 4c: Computing recovery interaction DID...")
    recovery_did = compute_recovery_did(recovery)
    
    # Stage 5: Seed-Level Summaries
    print("\nStage 5: Computing seed-level summaries...")
    summaries = compute_seed_level_summaries(
        regime_contrasts, branch_did, topology, recovery,
        n_bootstrap=args.n_bootstrap,
        bootstrap_seed=args.bootstrap_seed,
    )
    
    # Stage 5b: Secondary normalized-EMA summaries
    print("\nStage 5b: Computing secondary seed-level summaries...")
    secondary_summaries = compute_seed_level_summaries(
        regime_contrasts_secondary, branch_did_secondary, pd.DataFrame(), None,
        n_bootstrap=args.n_bootstrap,
        bootstrap_seed=args.bootstrap_seed,
    )
    
    # Validate recovery DID groups have exactly 40 seeds each
    print("\n  Validating recovery DID group sizes...")
    recovery_did_group_sizes = recovery_did.groupby(
        ["rho", "branch", "horizon_system", "metric", "outcome"]
    ).size()
    
    # P0 #5: Validate expected number of recovery DID groups
    if len(recovery_did_group_sizes) != EXPECTED_N_RECOVERY_DID_GROUPS:
        raise RuntimeError(
            f"Expected {EXPECTED_N_RECOVERY_DID_GROUPS} recovery DID groups, "
            f"got {len(recovery_did_group_sizes)}"
        )
    
    if not (recovery_did_group_sizes == EXPECTED_N_SEEDS).all():
        bad_groups = recovery_did_group_sizes[recovery_did_group_sizes != EXPECTED_N_SEEDS]
        raise RuntimeError(
            f"Recovery DID groups do not all contain {EXPECTED_N_SEEDS} seed-level rows. "
            f"Bad groups: {bad_groups.head().to_dict()}"
        )
    print("  ✅ Recovery DID validation passed")
    
    # Stage 5c: Recovery DID summaries
    print("\nStage 5c: Computing recovery DID summaries...")
    recovery_did_summaries = {}
    if not recovery_did.empty:
        recovery_did_summary = recovery_did.groupby(
            ["rho", "branch", "horizon_system", "metric", "outcome"],
            as_index=False,
        ).agg(
            mean=("recovery_difference_in_differences", "mean"),
            std=("recovery_difference_in_differences", "std"),
            n=("recovery_difference_in_differences", "count"),
        )
        
        # Add bootstrap CI
        rng_did = np.random.default_rng(args.bootstrap_seed)
        for (rho, branch, horizon_system, metric, outcome), group in recovery_did.groupby(
            ["rho", "branch", "horizon_system", "metric", "outcome"]
        ):
            values = group["recovery_difference_in_differences"].dropna().values
            if len(values) > 0:
                indices = rng_did.integers(0, len(values), size=(args.n_bootstrap, len(values)))
                bootstrap_means = np.mean(values[indices], axis=1)
                ci_lower = float(np.percentile(bootstrap_means, 2.5))
                ci_upper = float(np.percentile(bootstrap_means, 97.5))
                
                idx = recovery_did_summary[
                    (recovery_did_summary["rho"] == rho) & 
                    (recovery_did_summary["branch"] == branch) &
                    (recovery_did_summary["horizon_system"] == horizon_system) &
                    (recovery_did_summary["metric"] == metric) &
                    (recovery_did_summary["outcome"] == outcome)
                ].index
                recovery_did_summary.loc[idx, "ci_lower"] = ci_lower
                recovery_did_summary.loc[idx, "ci_upper"] = ci_upper
        
        recovery_did_summaries["recovery_did"] = recovery_did_summary
        print(f"✅ Stage 5c: Recovery DID Summaries - {len(recovery_did_summary)} groups")
    
    regime_summaries = summaries.get("regime_contrasts", pd.DataFrame())
    did_summaries = summaries.get("branch_did", pd.DataFrame())
    topology_summaries = summaries.get("topology", pd.DataFrame())
    recovery_summaries = summaries.get("recovery", pd.DataFrame())
    regime_summaries_secondary = secondary_summaries.get("regime_contrasts", pd.DataFrame())
    did_summaries_secondary = secondary_summaries.get("branch_did", pd.DataFrame())
    recovery_did_summary = recovery_did_summaries.get("recovery_did", pd.DataFrame())
    
    # P1 #6: Validate summary group counts
    print("\n  Validating summary group counts...")
    
    # Regime summaries: 4 non-baseline rho * 3 outcomes = 12 groups, each with n=40
    if not regime_summaries.empty:
        if len(regime_summaries) != 12:
            raise RuntimeError(
                f"Expected 12 regime summary groups, got {len(regime_summaries)}"
            )
        if not (regime_summaries["n"] == EXPECTED_N_SEEDS).all():
            bad_groups = regime_summaries[regime_summaries["n"] != EXPECTED_N_SEEDS]
            raise RuntimeError(
                f"Regime summary groups do not all have n={EXPECTED_N_SEEDS}: {bad_groups.to_dict()}"
            )
    
    # Branch DID summaries: 4 non-baseline rho * 3 branches * 3 outcomes = 36 groups, each with n=40
    if not did_summaries.empty:
        if len(did_summaries) != 36:
            raise RuntimeError(
                f"Expected 36 branch DID summary groups, got {len(did_summaries)}"
            )
        if not (did_summaries["n"] == EXPECTED_N_SEEDS).all():
            bad_groups = did_summaries[did_summaries["n"] != EXPECTED_N_SEEDS]
            raise RuntimeError(
                f"Branch DID summary groups do not all have n={EXPECTED_N_SEEDS}: {bad_groups.head().to_dict()}"
            )
    
    # P1 #3: Validate secondary regime and DID summary counts
    # Secondary regime summaries: 4 non-baseline rho * 3 outcomes = 12 groups, each with n=40
    if not regime_summaries_secondary.empty:
        if len(regime_summaries_secondary) != 12:
            raise RuntimeError(
                f"Expected 12 secondary regime summary groups, got {len(regime_summaries_secondary)}"
            )
        if not (regime_summaries_secondary["n"] == EXPECTED_N_SEEDS).all():
            bad_groups = regime_summaries_secondary[regime_summaries_secondary["n"] != EXPECTED_N_SEEDS]
            raise RuntimeError(
                f"Secondary regime summary groups do not all have n={EXPECTED_N_SEEDS}: {bad_groups.to_dict()}"
            )
    
    # Secondary branch DID summaries: 4 non-baseline rho * 3 branches * 3 outcomes = 36 groups, each with n=40
    if not did_summaries_secondary.empty:
        if len(did_summaries_secondary) != 36:
            raise RuntimeError(
                f"Expected 36 secondary branch DID summary groups, got {len(did_summaries_secondary)}"
            )
        if not (did_summaries_secondary["n"] == EXPECTED_N_SEEDS).all():
            bad_groups = did_summaries_secondary[did_summaries_secondary["n"] != EXPECTED_N_SEEDS]
            raise RuntimeError(
                f"Secondary branch DID summary groups do not all have n={EXPECTED_N_SEEDS}: {bad_groups.head().to_dict()}"
            )
    
    # Topology summary: 4 rho rows, each metric n=40
    if not topology_summaries.empty:
        if len(topology_summaries) != 4:
            raise RuntimeError(
                f"Expected 4 topology summary rows (one per non-baseline rho), got {len(topology_summaries)}"
            )
        for col in ["cosine_n", "jaccard_n", "distance_n"]:
            if not (topology_summaries[col] == EXPECTED_N_SEEDS).all():
                raise RuntimeError(
                    f"Topology summary {col} does not all equal {EXPECTED_N_SEEDS}"
                )
    
    # Recovery summaries: 80 groups (5 rho * 4 branches * 2 systems * 2 metrics)
    if not recovery_summaries.empty:
        if len(recovery_summaries) != EXPECTED_N_RECOVERY_GROUPS:
            raise RuntimeError(
                f"Expected {EXPECTED_N_RECOVERY_GROUPS} recovery summary groups, got {len(recovery_summaries)}"
            )
        # Check restricted fields have n=40
        for field in ["n_restricted_first", "n_restricted_sustained", "n_restricted_held",
                     "n_restricted_first_over_Twindow", "n_restricted_sustained_over_Twindow",
                     "n_restricted_held_over_Twindow", "n_auc_deficit"]:
            if field in recovery_summaries.columns:
                if not (recovery_summaries[field] == EXPECTED_N_SEEDS).all():
                    bad_groups = recovery_summaries[recovery_summaries[field] != EXPECTED_N_SEEDS]
                    raise RuntimeError(
                        f"Recovery summary {field} does not all equal {EXPECTED_N_SEEDS}: {bad_groups.head().to_dict()}"
                    )
    
    # Recovery DID summary: 624 groups
    # P0 Issue 2: Distinguish full-cohort vs conditional outcomes for n validation
    if not recovery_did_summary.empty:
        if len(recovery_did_summary) != EXPECTED_N_RECOVERY_DID_GROUPS:
            raise RuntimeError(
                f"Expected {EXPECTED_N_RECOVERY_DID_GROUPS} recovery DID summary groups, got {len(recovery_did_summary)}"
            )
        
        # Full-cohort outcomes must have n=40 for all groups
        full_cohort = recovery_did_summary[
            recovery_did_summary["outcome"].isin(FULL_COHORT_RECOVERY_DID_OUTCOMES)
        ]
        if not (full_cohort["n"] == EXPECTED_N_SEEDS).all():
            bad_groups = full_cohort[full_cohort["n"] != EXPECTED_N_SEEDS]
            raise RuntimeError(
                f"Full-cohort recovery DID summaries do not all have n={EXPECTED_N_SEEDS}: "
                f"{bad_groups.head().to_dict()}"
            )
        
        # Conditional outcomes may have n in [0, 40] due to censoring (NaN excluded from count)
        conditional = recovery_did_summary[
            recovery_did_summary["outcome"].isin(CONDITIONAL_RECOVERY_DID_OUTCOMES)
        ]
        if len(conditional) > 0:
            if np.any((conditional["n"] < 0) | (conditional["n"] > EXPECTED_N_SEEDS)):
                bad_groups = conditional[
                    (conditional["n"] < 0) | (conditional["n"] > EXPECTED_N_SEEDS)
                ]
                raise RuntimeError(
                    f"Conditional recovery DID summary n lies outside [0, 40]: "
                    f"{bad_groups.head().to_dict()}"
                )
    
    print("  ✅ All summary group counts validated")
    
    # Save outputs - construct output_files incrementally
    print("\nSaving outputs...")
    output_files: dict[str, Path] = {}
    
    # Paired regime contrasts (combined primary + secondary)
    regime_contrast_combined_path = output_dir / "twindow_paired_regime_contrasts.csv"
    save_csv_atomic(regime_contrast_combined_path, regime_contrasts_combined)
    output_files["regime_contrasts_combined"] = regime_contrast_combined_path
    print(f"  Saved: {regime_contrast_combined_path.name}")
    
    # Paired regime contrasts (primary only - fixed_physical)
    regime_contrast_path = output_dir / "twindow_paired_regime_contrasts_fixed_physical.csv"
    save_csv_atomic(regime_contrast_path, regime_contrasts)
    output_files["regime_contrasts"] = regime_contrast_path
    print(f"  Saved: {regime_contrast_path.name}")
    
    # Paired regime contrasts (secondary only - normalized_EMA)
    regime_contrast_secondary_path = output_dir / "twindow_paired_regime_contrasts_normalized_EMA.csv"
    save_csv_atomic(regime_contrast_secondary_path, regime_contrasts_secondary)
    output_files["regime_contrasts_secondary"] = regime_contrast_secondary_path
    print(f"  Saved: {regime_contrast_secondary_path.name}")
    
    # Branch DID (combined primary + secondary)
    branch_did_combined_path = output_dir / "twindow_branch_interactions.csv"
    save_csv_atomic(branch_did_combined_path, branch_did_combined)
    output_files["branch_did_combined"] = branch_did_combined_path
    print(f"  Saved: {branch_did_combined_path.name}")
    
    # Branch DID (primary only - fixed_physical)
    branch_did_path = output_dir / "twindow_branch_interactions_fixed_physical.csv"
    save_csv_atomic(branch_did_path, branch_did)
    output_files["branch_did"] = branch_did_path
    print(f"  Saved: {branch_did_path.name}")
    
    # Branch DID (secondary only - normalized_EMA)
    branch_did_secondary_path = output_dir / "twindow_branch_interactions_normalized_EMA.csv"
    save_csv_atomic(branch_did_secondary_path, branch_did_secondary)
    output_files["branch_did_secondary"] = branch_did_secondary_path
    print(f"  Saved: {branch_did_secondary_path.name}")
    
    # Cross-T topology
    if not topology.empty:
        topology_path = output_dir / "twindow_cross_condition_topology.csv"
        save_csv_atomic(topology_path, topology)
        output_files["topology"] = topology_path
        print(f"  Saved: {topology_path.name}")
    
    # Recovery scaling raw output
    if not recovery.empty:
        recovery_raw_path = output_dir / "twindow_recovery_by_seed.csv"
        save_csv_atomic(recovery_raw_path, recovery)
        output_files["recovery_by_seed"] = recovery_raw_path
        print(f"  Saved: {recovery_raw_path.name}")
    
    # Summaries
    if not regime_summaries.empty:
        regime_summary_path = output_dir / "twindow_regime_summary.csv"
        save_csv_atomic(regime_summary_path, regime_summaries)
        output_files["regime_summary"] = regime_summary_path
        print(f"  Saved: {regime_summary_path.name}")
    
    if not did_summaries.empty:
        did_summary_path = output_dir / "twindow_branch_DID_summary.csv"
        save_csv_atomic(did_summary_path, did_summaries)
        output_files["did_summary"] = did_summary_path
        print(f"  Saved: {did_summary_path.name}")
    
    if not topology_summaries.empty:
        topology_summary_path = output_dir / "twindow_topology_summary.csv"
        save_csv_atomic(topology_summary_path, topology_summaries)
        output_files["topology_summary"] = topology_summary_path
        print(f"  Saved: {topology_summary_path.name}")
    
    # Recovery summaries (censoring-aware)
    if not recovery_summaries.empty:
        recovery_summary_path = output_dir / "twindow_recovery_summary.csv"
        save_csv_atomic(recovery_summary_path, recovery_summaries)
        output_files["recovery_summary"] = recovery_summary_path
        print(f"  Saved: {recovery_summary_path.name}")
    
    # Recovery DID (raw)
    if not recovery_did.empty:
        recovery_did_path = output_dir / "twindow_recovery_interactions.csv"
        save_csv_atomic(recovery_did_path, recovery_did)
        output_files["recovery_did"] = recovery_did_path
        print(f"  Saved: {recovery_did_path.name}")
    
    # Recovery DID summaries
    if not recovery_did_summary.empty:
        recovery_did_summary_path = output_dir / "twindow_recovery_interactions_summary.csv"
        save_csv_atomic(recovery_did_summary_path, recovery_did_summary)
        output_files["recovery_did_summary"] = recovery_did_summary_path
        print(f"  Saved: {recovery_did_summary_path.name}")
    
    # Secondary summaries
    if not regime_summaries_secondary.empty:
        regime_summary_secondary_path = output_dir / "twindow_regime_secondary_summary.csv"
        save_csv_atomic(regime_summary_secondary_path, regime_summaries_secondary)
        output_files["regime_summary_secondary"] = regime_summary_secondary_path
        print(f"  Saved: {regime_summary_secondary_path.name}")
    
    if not did_summaries_secondary.empty:
        did_summary_secondary_path = output_dir / "twindow_branch_DID_secondary_summary.csv"
        save_csv_atomic(did_summary_secondary_path, did_summaries_secondary)
        output_files["did_summary_secondary"] = did_summary_secondary_path
        print(f"  Saved: {did_summary_secondary_path.name}")
    
    # Text report
    report = generate_text_report(
        validation, regime_contrasts, branch_did, topology,
        regime_summaries, did_summaries, topology_summaries, 
        recovery_summaries, regime_summaries_secondary, did_summaries_secondary,
        recovery_did_summary
    )
    report_path = output_dir / "twindow_sensitivity_report.txt"
    save_text_atomic(report_path, report)
    output_files["report"] = report_path
    print(f"  Saved: {report_path.name}")
    
    # Analysis manifest
    analysis_manifest = generate_analysis_manifest(
        csv_path, npz_path, manifest_path, validation, output_files,
        source_path=Path(__file__),
        bootstrap_seed=args.bootstrap_seed,
        n_bootstrap=args.n_bootstrap,
        command_line=command_line,
    )
    manifest_path_out = output_dir / "analysis_manifest.json"
    save_json_atomic(manifest_path_out, analysis_manifest)
    output_files["analysis_manifest"] = manifest_path_out
    print(f"  Saved: {manifest_path_out.name}")
    
    # Print report to console
    print("\n" + "=" * 80)
    print("ANALYSIS REPORT")
    print("=" * 80)
    print(report)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
