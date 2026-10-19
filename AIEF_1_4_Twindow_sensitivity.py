#!/usr/bin/env python3
"""AIEF-1.4 T_window Sensitivity Study Driver.

Parameterized study varying T_window = rho * T_* where T_* = 25 / mean(OMEGA) = 17.5
and rho ∈ {0.5, 0.75, 1, 1.5, 2}.

Study Design:
- For each seed s ∈ seeds (40 seeds)
- For each rho ∈ {0.5, 0.75, 1, 1.5, 2}
- Set T_window = rho * 17.5
- Set alpha = exp(-dt / T_window)
- Full regeneration for each (s, rho) - NO split state reuse
- Branches: continue, reset_ema, reset_B, future_shuffle
- Fixed physical horizons: immediate=0-17.5, recovery=17.5-87.5, late=87.5-320
- EMA-normalized horizons: immediate=0-1 T_window, recovery=1-5 T_window

Output:
- Scalars in CSV: per (seed, rho, branch) scalar outcomes
- Arrays in NPZ: per (seed, rho, branch) trajectory and matrix outcomes

MANDATORY: Baseline equivalence test at rho=1 must pass against frozen production.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import shutil
import sys
import time
import tempfile
from pathlib import Path
from typing import Any

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas is required for production T_window study")
    print("Install with: pip install pandas")
    sys.exit(1)

import numpy as np

# Import the experiment engine
import aief_experiment_engine_v1 as engine


# =============================================================================
# Study Configuration
# =============================================================================

STUDY_NAME = "AIEF_1_4_Twindow_sensitivity"
WORKFLOW_VERSION = "v1.0"

# Frozen production values (from AIEF_1_4_memory_ablation_updated_REAL.py)
FROZEN_N = 12
FROZEN_DT = 0.01
FROZEN_TAU = 0.5
FROZEN_OMEGA = np.array([
    1.00, 1.02, 1.50, 2.00, 2.01, 1.01,
    1.03, 1.51, 2.02, 2.00, 1.00, 1.04
], dtype=float)
FROZEN_A = 1.0
FROZEN_Q = 1.5
FROZEN_DELTA = 0.05
FROZEN_ETA = 0.04
FROZEN_GAMMA = 0.015
FROZEN_MU = 0.03
FROZEN_B_C = 0.12
FROZEN_B_INIT_SCALE = 0.0005

# Derived from frozen values
FROZEN_MEAN_OMEGA = float(np.mean(FROZEN_OMEGA))
FROZEN_T_STAR = 25.0 / FROZEN_MEAN_OMEGA  # 17.5

# Protocol from frozen run
FROZEN_T_SIM = 800.0
FROZEN_N_STEPS = int(round(FROZEN_T_SIM / FROZEN_DT))  # 80000
FROZEN_BURN_END = int(0.20 * FROZEN_N_STEPS)  # 16000
FROZEN_HIST_END = int(0.60 * FROZEN_N_STEPS)  # 48000
FROZEN_FUTURE_STEPS = FROZEN_N_STEPS - FROZEN_HIST_END  # 32000
FROZEN_DELAY_STEPS = int(round(FROZEN_TAU / FROZEN_DT))  # 50
FROZEN_WINDOW_STEPS = int(round(FROZEN_T_STAR / FROZEN_DT))  # 1750
FROZEN_RECOVERY_END = min(5 * FROZEN_WINDOW_STEPS, FROZEN_FUTURE_STEPS)  # 8750

# Rho values for T_window sensitivity
RHO_VALUES = (0.5, 0.75, 1.0, 1.5, 2.0)

# Frozen branch order from AIEF_1_4_memory_ablation_updated_REAL.py
FROZEN_BRANCH_ORDER = (
    "continue",
    "reset_ema",
    "reset_B",
    "reset_B_ema",
    "B_carrier_only",
    "full_reset",
    "future_shuffle",
)

# Study subset of branches
STUDY_BRANCHES = ("continue", "reset_ema", "reset_B", "future_shuffle")

# Fixed physical horizon times (in time units, not steps)
PHYSICAL_IMMEDIATE_END = 17.5
PHYSICAL_RECOVERY_END = 87.5  # Also PHYSICAL_LATE_START
PHYSICAL_FUTURE_END = 320.0

# Defaults
DEFAULT_MASTER_SEED = 20260714
DEFAULT_N_SEEDS = 40
DEFAULT_RUN_ROOT = "runs"

# =============================================================================
# REQUIRED OUTPUT SCHEMA
# =============================================================================

# These are the MINIMUM required outputs that must be present in engine results
# If any are missing, the study should fail with a clear error

REQUIRED_PREFIX_KEYS = (
    "B_at_split",
    "R_physical_past",
    "theta_at_split",
    "coherence_acc_at_split",
    "history_at_split",
    "selected_at_split",
)

REQUIRED_BRANCH_MATRIX_KEYS = (
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

# Primary outcomes (must be present)
# NOW USING FIXED-PHYSICAL HORIZONS as the primary estimands
PRIMARY_OUTCOMES = (
    "Weighted_similarity_late_fixed_physical",
    "Retention_contrast_late_fixed_physical",
    "P_mean_late_fixed_physical",
)

# Secondary outcomes for comparison (normalized EMA)
SECONDARY_OUTCOMES = (
    "Weighted_similarity_late_normalized_EMA",
    "Retention_contrast_late_normalized_EMA",
    "P_mean_late_normalized_EMA",
)

# Backward compatible names (map to normalized EMA for legacy compatibility)
LEGACY_OUTCOMES = (
    "Weighted_similarity_late",
    "Retention_contrast_late", 
    "P_mean_late",
)

# Separate FROZEN vs EXTENDED schemas
# FROZEN keys must exist in historical frozen data
FROZEN_BRANCH_SCALAR_KEYS = (
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
    "Minimum_similarity",
    # Projection diagnostics (in frozen data)
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
)

# P1 #7: Separate study metadata from frozen scalar output
# T_window and rho are study metadata, not part of historical frozen branch scalar schema
STUDY_METADATA_KEYS = (
    "T_window",
    "rho",
)

# EXTENDED keys are new in v1 (dual-horizon)
EXTENDED_BRANCH_SCALAR_KEYS = (
    # Fixed physical horizon scalars (PRIMARY ESTIMANDS)
    "P_mean_late_fixed_physical",
    "Weighted_similarity_late_fixed_physical",
    "Retention_contrast_late_fixed_physical",
    "Corr_Rpast_Plate_fixed_physical",
    "r_mean_late_fixed_physical",
    # Normalized EMA horizon scalars (explicit)
    "P_mean_late_normalized_EMA",
    "Weighted_similarity_late_normalized_EMA",
    "Retention_contrast_late_normalized_EMA",
    "Corr_Rpast_Plate_normalized_EMA",
    "r_mean_late_normalized_EMA",
)

# All required scalar keys (frozen + extended)
REQUIRED_BRANCH_SCALAR_KEYS = FROZEN_BRANCH_SCALAR_KEYS + EXTENDED_BRANCH_SCALAR_KEYS

# P1 #6: Removed DESIRED_BRANCH_SCALAR_KEYS as they are always NaN
# These fields require finalize_historical_branch_metrics() to be called, which is not done
# for individual (seed, rho) runs. The new analysis script computes richer condition-specific
# recovery estimands from trajectories, so these legacy fields are not needed.

# All scalar keys for CSV output (required + study metadata)
BRANCH_SCALAR_KEYS = REQUIRED_BRANCH_SCALAR_KEYS + STUDY_METADATA_KEYS

# P0 #2: Separate frozen and study schemas
# FROZEN keys must exist in historical frozen data (11 keys)
FROZEN_BRANCH_MATRIX_KEYS = REQUIRED_BRANCH_MATRIX_KEYS

# REQUIRED keys for study output - matches engine schema (all frozen + extended keys)
REQUIRED_BRANCH_MATRIX_KEYS = tuple(
    engine.REQUIRED_BRANCH_MATRIX_KEYS
)

# P0 #2: Validate at import that frozen keys are subset of engine keys
if not set(FROZEN_BRANCH_MATRIX_KEYS).issubset(set(REQUIRED_BRANCH_MATRIX_KEYS)):
    missing = set(FROZEN_BRANCH_MATRIX_KEYS) - set(REQUIRED_BRANCH_MATRIX_KEYS)
    raise RuntimeError(
        f"Frozen matrix keys not subset of engine keys: {sorted(missing)}"
    )

# All matrix keys (use engine's full schema)
BRANCH_MATRIX_KEYS = REQUIRED_BRANCH_MATRIX_KEYS


def is_finite_number(value: Any) -> bool:
    """Check if a value is a finite number.
    
    Handles int, float, numpy scalar types, and excludes NaN, inf, -inf, None, strings.
    """
    return (
        isinstance(
            value,
            (
                int,
                float,
                np.integer,
                np.floating,
            ),
        )
        and np.isfinite(value)
    )


def validate_prefix_outputs(prefix: dict[str, Any]) -> None:
    """P0 #5: Validate prefix outputs.
    
    Validates that all required prefix keys are present with correct shapes.
    
    Raises RuntimeError if required keys are missing or have wrong shapes.
    """
    missing = set(REQUIRED_PREFIX_KEYS) - set(prefix)
    if missing:
        raise RuntimeError(f"schema: prefix missing {sorted(missing)}")
    
    expected_shapes = {
        "B_at_split": (FROZEN_N, FROZEN_N),
        "R_physical_past": (FROZEN_N, FROZEN_N),
        "theta_at_split": (FROZEN_N,),
        "coherence_acc_at_split": (FROZEN_N, FROZEN_N),
        "history_at_split": (FROZEN_DELAY_STEPS + 1, FROZEN_N),
        "selected_at_split": (FROZEN_N, FROZEN_N),
    }
    
    for key, expected in expected_shapes.items():
        if key in prefix:
            observed = np.asarray(prefix[key])
            if observed.shape != expected:
                raise RuntimeError(f"schema: prefix {key} shape {observed.shape} != {expected}")


def validate_branch_outputs(
    branch: str,
    branch_result: dict[str, Any],
    expected_rho: float,
    expected_T_window: float,
) -> None:
    """Validate that a branch result contains all required outputs.
    
    P0 #3: Now validates rho and T_window metadata.
    P0 #4: Now validates recovery_end_ema.
    P1 #8: Use engine's REQUIRED_BRANCH_MATRIX_KEYS for matrix validation.
    Also validates array shapes and metadata consistency.
    
    Raises RuntimeError if required keys are missing or have wrong shapes.
    """
    # Validate required scalars
    missing_scalars = set(REQUIRED_BRANCH_SCALAR_KEYS) - set(branch_result.keys())
    
    # P1 #8: Use engine's matrix keys for validation
    missing_matrices = set(engine.REQUIRED_BRANCH_MATRIX_KEYS) - set(branch_result.keys())
    
    # P1 #7: Strengthen matrix shape validation
    # Validate ALL matrix fields that should be N x N
    shape_errors = []
    
    # P1 #7: Define which matrix keys should be 12x12
    MATRIX_12X12_KEYS = tuple(
        key
        for key in engine.REQUIRED_BRANCH_MATRIX_KEYS
        if key not in {
            "sample_times",
            "density_trajectory",
            "similarity_trajectory",
        }
    )
    
    for key in MATRIX_12X12_KEYS:
        if key in branch_result:
            value = np.asarray(branch_result[key])
            if value.shape != (FROZEN_N, FROZEN_N):
                shape_errors.append(f"{key} shape {value.shape} != {(FROZEN_N, FROZEN_N)}")
            if not np.all(np.isfinite(value)):
                shape_errors.append(f"{key} contains non-finite values")
    
    # Validate trajectory lengths
    expected_samples = (FROZEN_FUTURE_STEPS + 50 - 1) // 50  # diagnostic_stride=50
    for key in ("sample_times", "density_trajectory", "similarity_trajectory"):
        if key in branch_result:
            actual_len = len(branch_result[key])
            if actual_len != expected_samples:
                shape_errors.append(f"{key} length {actual_len} != {expected_samples}")
    
    # P1 #8: Validate all trajectory arrays have equal lengths
    if all(key in branch_result for key in ("sample_times", "density_trajectory", "similarity_trajectory")):
        lengths = [len(branch_result[key]) for key in ("sample_times", "density_trajectory", "similarity_trajectory")]
        if len(set(lengths)) > 1:
            shape_errors.append(f"Trajectory length mismatch: {lengths}")
    
    # P1 #8: Validate exact sample-time schedule
    if "sample_times" in branch_result:
        expected_times = (
            np.arange(0, FROZEN_FUTURE_STEPS, 50, dtype=float) + 1.0
        ) * FROZEN_DT
        observed_times = np.asarray(branch_result["sample_times"], dtype=float)
        if not np.array_equal(observed_times, expected_times):
            shape_errors.append(
                "sample_times does not match the expected "
                "0.01-to-319.51 diagnostic schedule"
            )
    
    # Validate horizon metadata consistency
    # P0 #3: Validate rho and T_window with expected values
    # P0 #4: Validate recovery_end_ema
    # P0 #2 FIX: Use expected_rho parameter, not undefined rho variable
    metadata_errors = []
    if "rho" in branch_result:
        # P0 #3: Validate rho matches expected value
        observed_rho = branch_result["rho"]
        if float(observed_rho) != float(expected_rho):
            metadata_errors.append(f"rho={observed_rho} != {expected_rho}")
    else:
        metadata_errors.append("missing rho")
    
    if "T_window" in branch_result:
        # P0 #3: Validate T_window matches expected value
        observed_T_window = branch_result["T_window"]
        if float(observed_T_window) != float(expected_T_window):
            metadata_errors.append(f"T_window={observed_T_window} != {expected_T_window}")
    else:
        metadata_errors.append("missing T_window")
    
    # P1 #8: Use independent expected values, not self-referential from branch_result
    # Validate window_steps using expected_T_window, not branch_result["T_window"]
    if "window_steps" in branch_result:
        expected_window_steps = int(round(expected_T_window / FROZEN_DT))
        if branch_result["window_steps"] != expected_window_steps:
            metadata_errors.append(f"window_steps {branch_result['window_steps']} != {expected_window_steps}")
    else:
        metadata_errors.append("missing window_steps")
    
    if "fixed_immediate_end" in branch_result:
        if branch_result["fixed_immediate_end"] != 1750:
            metadata_errors.append(f"fixed_immediate_end {branch_result['fixed_immediate_end']} != 1750")
    else:
        metadata_errors.append("missing fixed_immediate_end")
    
    if "fixed_recovery_end" in branch_result:
        if branch_result["fixed_recovery_end"] != 8750:
            metadata_errors.append(f"fixed_recovery_end {branch_result['fixed_recovery_end']} != 8750")
    else:
        metadata_errors.append("missing fixed_recovery_end")
    
    # P0 #4: Validate recovery_end_ema using expected_T_window
    if "recovery_end_ema" in branch_result:
        expected_recovery_end = min(
            5 * int(round(expected_T_window / FROZEN_DT)),
            FROZEN_FUTURE_STEPS,
        )
        if branch_result["recovery_end_ema"] != expected_recovery_end:
            metadata_errors.append(f"recovery_end_ema={branch_result['recovery_end_ema']} != {expected_recovery_end}")
    else:
        metadata_errors.append("missing recovery_end_ema")
    
    # Combine all errors
    all_errors = []
    if missing_scalars:
        all_errors.extend([f"missing scalar: {k}" for k in sorted(missing_scalars)[:10]])
    if missing_matrices:
        all_errors.extend([f"missing matrix: {k}" for k in sorted(missing_matrices)[:10]])
    if shape_errors:
        all_errors.extend(shape_errors[:10])
    if metadata_errors:
        all_errors.extend(metadata_errors[:10])
    
    if all_errors:
        raise RuntimeError(
            f"Branch '{branch}' has {len(all_errors)} validation errors: "
            f"{all_errors[:5]}... ({len(all_errors)} total)"
        )


# =============================================================================
# Utility Functions
# =============================================================================

# Note: master-seed is now type=int, no longer supports 'random' for production


def generate_seed_set(master_seed: int, count: int) -> list[int]:
    """Generate deterministic seed set from master seed."""
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


def file_sha256(path: str | os.PathLike[str]) -> str:
    """Compute SHA-256 hash of a file.
    
    Local helper for file hashing - does not depend on engine utilities.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_sha256() -> str | None:
    """Compute SHA-256 of this source file."""
    try:
        return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except (NameError, OSError):
        return None


def atomic_write_text(path: str | Path, text: str) -> None:
    """Write text atomically with fsync."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".tmp-{os.getpid()}-{time.time_ns()}")
    try:
        with open(temporary, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temporary), str(path))
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path: str | Path, data: dict[str, Any]) -> None:
    """Write JSON atomically with fsync."""
    text = json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n"
    atomic_write_text(path, text)


def save_npz_atomic(path: str | Path, payload: dict[str, Any]) -> None:
    """Save NPZ atomically with fsync.
    
    Uses a temporary file with .npz suffix so np.savez_compressed doesn't add extra suffix.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Use tempfile.mkstemp to create a temporary file in the same directory
    fd, temporary = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp.npz",
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            np.savez_compressed(handle, **payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, str(path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_npz(path: str | Path) -> dict[str, Any]:
    """Load NPZ file."""
    payload: dict[str, Any] = {}
    with np.load(str(path), allow_pickle=False) as data:
        for key in data.files:
            value = data[key]
            payload[key] = value.item() if value.ndim == 0 else value.copy()
    return payload


def save_csv_atomic(path: str | Path, dataframe) -> None:
    """Save CSV atomically with fsync."""
    if pd is None:
        raise RuntimeError("pandas is required for CSV output but is not installed")
    
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            dataframe.to_csv(handle, index=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, str(path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


# =============================================================================
# Configuration and Validation
# =============================================================================

def validate_engine_contract() -> None:
    """P1 #12: Validate that driver constants agree with engine.
    
    Ensures driver and engine have consistent frozen production values.
    """
    checks = {
        "N": (FROZEN_N, engine.FROZEN_N),
        "dt": (FROZEN_DT, engine.FROZEN_DT),
        "tau": (FROZEN_TAU, engine.FROZEN_TAU),
        "T_star": (FROZEN_T_STAR, engine.FROZEN_T_STAR),
        "B_c": (FROZEN_B_C, engine.FROZEN_B_C),
        "B_init_scale": (FROZEN_B_INIT_SCALE, engine.FROZEN_B_INIT_SCALE),
    }
    
    for name, (driver_value, engine_value) in checks.items():
        if driver_value != engine_value:
            raise RuntimeError(
                f"Driver/engine {name} mismatch: "
                f"driver={driver_value}, engine={engine_value}"
            )
    
    if not np.array_equal(FROZEN_OMEGA, engine.FROZEN_OMEGA):
        raise RuntimeError(
            f"Driver/engine omega mismatch: "
            f"driver={FROZEN_OMEGA.tolist()}, engine={engine.FROZEN_OMEGA.tolist()}"
        )
    
    # Also check other important constants
    if FROZEN_T_SIM != engine.FROZEN_T_SIM:
        raise RuntimeError(f"Driver/engine T_SIM mismatch: {FROZEN_T_SIM} != {engine.FROZEN_T_SIM}")
    if FROZEN_DELTA != engine.FROZEN_DELTA:
        raise RuntimeError(f"Driver/engine DELTA mismatch: {FROZEN_DELTA} != {engine.FROZEN_DELTA}")
    if FROZEN_ETA != engine.FROZEN_ETA:
        raise RuntimeError(f"Driver/engine ETA mismatch: {FROZEN_ETA} != {engine.FROZEN_ETA}")
    if FROZEN_GAMMA != engine.FROZEN_GAMMA:
        raise RuntimeError(f"Driver/engine GAMMA mismatch: {FROZEN_GAMMA} != {engine.FROZEN_GAMMA}")
    if FROZEN_MU != engine.FROZEN_MU:
        raise RuntimeError(f"Driver/engine MU mismatch: {FROZEN_MU} != {engine.FROZEN_MU}")
    if FROZEN_A != engine.FROZEN_A:
        raise RuntimeError(f"Driver/engine A mismatch: {FROZEN_A} != {engine.FROZEN_A}")
    if FROZEN_Q != engine.FROZEN_Q:
        raise RuntimeError(f"Driver/engine Q mismatch: {FROZEN_Q} != {engine.FROZEN_Q}")
    
    # P1 #10: Strengthen driver/engine contract with additional checks
    extra_checks = {
        "scale_epsilon": (1e-12, engine.FROZEN_ZERO_TOL),
        "delay_steps": (FROZEN_DELAY_STEPS, engine.FROZEN_DELAY_STEPS),
        "window_steps": (FROZEN_WINDOW_STEPS, engine.FROZEN_WINDOW_STEPS),
        "recovery_end": (FROZEN_RECOVERY_END, engine.FROZEN_RECOVERY_END),
    }
    for name, (driver_value, engine_value) in extra_checks.items():
        if driver_value != engine_value:
            raise RuntimeError(
                f"Driver/engine {name} mismatch: driver={driver_value}, engine={engine_value}"
            )
    
    # P1 #10: Validate branch RNG namespace matches
    if tuple(engine.DEFAULT_PROTOCOL_CONFIG.branches) != FROZEN_BRANCH_ORDER:
        raise RuntimeError(
            "Driver/engine frozen branch RNG namespace mismatch"
        )


def create_model_config(rho: float) -> engine.ModelConfig:
    """Create ModelConfig for a given rho value."""
    T_window = rho * FROZEN_T_STAR
    return engine.ModelConfig(
        N=FROZEN_N,
        dt=FROZEN_DT,
        tau=FROZEN_TAU,
        omega=tuple(FROZEN_OMEGA.tolist()),
        a=FROZEN_A,
        q=FROZEN_Q,
        delta=FROZEN_DELTA,
        eta=FROZEN_ETA,
        mu=FROZEN_MU,
        gamma=FROZEN_GAMMA,
        T_window=T_window,
        B_c=FROZEN_B_C,
        B_init_scale=FROZEN_B_INIT_SCALE,
        scale_epsilon=1e-12,
    )


def create_protocol_config() -> engine.ProtocolConfig:
    """Create ProtocolConfig matching frozen production."""
    return engine.ProtocolConfig(
        T_sim=FROZEN_T_SIM,
        burn_end_time=160.0,   # 0.20 * 800
        split_time=480.0,     # 0.60 * 800
        future_duration=320.0, # 800 - 480
        diagnostic_stride=50,
        branches=STUDY_BRANCHES,
    )



# =============================================================================
# Simulation Functions
# =============================================================================

def simulate_seed_rho(
    seed: int,
    rho: float,
    config: engine.ModelConfig,
    protocol: engine.ProtocolConfig,
    study_branches: tuple[str, ...],
) -> dict[str, Any]:
    """Simulate a single (seed, rho) combination.
    
    CRITICAL: Uses FROZEN_BRANCH_ORDER for RNG namespace, but only simulates
    study_branches subset. This ensures future_shuffle gets the 7th RNG sequence
    (not the 4th) as in production.
    
    Returns complete results for all branches at this (seed, rho).
    """
    # Create branch RNGs using FULL frozen branch order for correct namespace
    branch_rngs = engine.make_branch_rngs(seed, FROZEN_BRANCH_ORDER)
    
    # Create a protocol with just the study branches
    study_protocol = engine.ProtocolConfig(
        T_sim=protocol.T_sim,
        burn_end_time=protocol.burn_end_time,
        split_time=protocol.split_time,
        future_duration=protocol.future_duration,
        diagnostic_stride=protocol.diagnostic_stride,
        branches=study_branches,
    )
    
    # P1 #6: Validate study protocol inside simulate_seed_rho()
    try:
        config.validate()
        study_protocol.validate(config)
    except Exception as e:
        raise RuntimeError(f"Protocol validation failed: {e}")
    
    # P1 #6: Require study_branches to match STUDY_BRANCHES
    if tuple(study_branches) != STUDY_BRANCHES:
        raise RuntimeError(
            f"Unexpected study branch set/order: {study_branches}"
        )
    
    # Simulate prefix
    split_state, prefix = engine.simulate_prefix(seed, config, study_protocol)
    
    # P0 #5: Validate prefix outputs
    validate_prefix_outputs(prefix)
    
    # Simulate only study branches, using RNGs from frozen namespace
    branch_results = {}
    for branch in study_branches:
        if branch not in branch_rngs:
            raise RuntimeError(
                f"Branch '{branch}' not in FROZEN_BRANCH_ORDER. "
                f"Cannot map to production RNG namespace."
            )
        rng = branch_rngs[branch]
        branch_result = engine.simulate_future(
            split_state.clone(),
            prefix,
            branch,
            config,
            study_protocol,
            rng,
        )
        
        # P0 #1: Add metadata BEFORE validation
        branch_result["T_window"] = config.T_window
        branch_result["rho"] = rho
        
        # P0 #3-4: Validate branch outputs with expected metadata
        validate_branch_outputs(branch, branch_result, rho, config.T_window)
        
        # P1 #9: Validate branch outputs immediately after simulation
        # Check both primary and secondary outcomes for finiteness
        for key in PRIMARY_OUTCOMES + SECONDARY_OUTCOMES:
            if key not in branch_result:
                raise RuntimeError(
                    f"schema: {branch} missing {key}"
                )
            if not is_finite_number(branch_result[key]):
                raise RuntimeError(
                    f"schema: {branch} has non-finite {key}={branch_result[key]}"
                )
        
        branch_results[branch] = branch_result
    
    return {
        "seed": int(seed),
        "rho": rho,
        "config": {
            "N": config.N,
            "dt": config.dt,
            "tau": config.tau,
            "T_window": config.T_window,
            "alpha": config.alpha,
            "mean_omega": config.mean_omega,
            "T_star": config.T_star,
        },
        "protocol": {
            "T_sim": study_protocol.T_sim,
            "burn_end_time": study_protocol.burn_end_time,
            "split_time": study_protocol.split_time,
            "future_duration": study_protocol.future_duration,
        },
        "prefix": prefix,
        "branches": branch_results,
    }


def run_baseline_equivalence(
    seeds: list[int],
    frozen_manifest_path: str,
    frozen_npz_path: str,
    frozen_csv_path: str,
) -> dict[str, Any]:
    """Run baseline equivalence test at rho=1 (T_window = T_*).
    
    MANDATORY: Must reproduce frozen run exactly for ALL seeds.
    
    Verifies:
    1. Seed list matches frozen manifest exactly (same seeds, same order)
    2. All 40 seeds pass equivalence (if 40 seeds provided)
    3. Engine produces all required outputs
    
    This helper ONLY performs equivalence and returns a result.
    Main handles manifests and output paths.
    """
    import json
    
    # Load frozen manifest to compare seeds
    try:
        with open(frozen_manifest_path, 'r', encoding='utf-8') as f:
            frozen_manifest = json.load(f)
    except FileNotFoundError:
        return {
            "status": "failed",
            "error": f"Frozen manifest not found: {frozen_manifest_path}",
            "seeds_match": False,
        }
    except json.JSONDecodeError as e:
        return {
            "status": "failed",
            "error": f"Frozen manifest is not valid JSON: {frozen_manifest_path} ({e})",
            "seeds_match": False,
        }
    
    # Validate manifest has required structure
    if "randomization" not in frozen_manifest or "paired_seeds" not in frozen_manifest["randomization"]:
        return {
            "status": "failed",
            "error": f"Frozen manifest missing required structure: {frozen_manifest_path}",
            "seeds_match": False,
        }
    
    frozen_seeds = frozen_manifest["randomization"]["paired_seeds"]
    
    # Verify seed list matches frozen manifest EXACTLY
    # This is critical: baseline equivalence tests a specific cohort
    if len(seeds) != len(frozen_seeds):
        return {
            "status": "failed",
            "error": f"Seed count mismatch: generated={len(seeds)}, frozen={len(frozen_seeds)}",
            "frozen_seeds": [int(s) for s in frozen_seeds],
            "generated_seeds": [int(s) for s in seeds],
            "seeds_match": False,
        }
    
    for i, (gen_seed, frozen_seed) in enumerate(zip(seeds, frozen_seeds)):
        if int(gen_seed) != int(frozen_seed):
            return {
                "status": "failed",
                "error": f"Seed mismatch at index {i}: generated={gen_seed}, frozen={frozen_seed}",
                "frozen_seeds": [int(s) for s in frozen_seeds],
                "generated_seeds": [int(s) for s in seeds],
                "seeds_match": False,
            }
    
    # Verify master seed matches
    frozen_master_seed = frozen_manifest["randomization"]["master_seed"]
    # Note: We can't check the generated master seed here as it's not passed,
    # but the seed generation method should match
    
    # Validate frozen CSV path exists
    if not os.path.exists(frozen_csv_path):
        return {
            "status": "failed",
            "error": f"Frozen scalar CSV not found: {frozen_csv_path}",
            "seeds_match": True,
        }
    
    # Create config for rho=1
    config = create_model_config(rho=1.0)
    
    # For baseline equivalence, we need to validate ALL 7 branches
    # to certify the engine as reusable infrastructure
    baseline_protocol = engine.ProtocolConfig(
        T_sim=FROZEN_T_SIM,
        burn_end_time=160.0,
        split_time=480.0,
        future_duration=320.0,
        diagnostic_stride=50,
        branches=FROZEN_BRANCH_ORDER,  # All 7 branches for engine certification
    )
    
    # Run the engine's baseline equivalence test with ALL seeds and ALL 7 branches
    results = engine.run_baseline_equivalence(
        seeds=seeds,
        config=config,
        protocol=baseline_protocol,
        frozen_manifest_path=frozen_manifest_path,
        frozen_npz_path=frozen_npz_path,
        frozen_csv_path=frozen_csv_path,
        branch_order=FROZEN_BRANCH_ORDER,  # Use FULL branch order for RNG namespace
    )
    
    # Add seed comparison info
    results["seed_comparison"] = {
        "generated_seeds": [int(s) for s in seeds],
        "frozen_seeds": [int(s) for s in frozen_seeds],
        "seeds_match": True,
    }
    
    return results


# =============================================================================
# Manifest and Output
# =============================================================================

def build_manifest(
    master_seed: int,
    seeds: list[int],
    rho_values: tuple[float, ...],
) -> dict[str, Any]:
    """Build study manifest."""
    # Compute config hash from model parameters
    model_params = {
        "N": FROZEN_N,
        "dt": FROZEN_DT,
        "tau": FROZEN_TAU,
        "omega": FROZEN_OMEGA.tolist(),
        "a": FROZEN_A,
        "q": FROZEN_Q,
        "delta": FROZEN_DELTA,
        "eta": FROZEN_ETA,
        "gamma": FROZEN_GAMMA,
        "mu": FROZEN_MU,
        "B_c": FROZEN_B_C,
        "B_init_scale": FROZEN_B_INIT_SCALE,
        "T_star": FROZEN_T_STAR,
        # P1 #9: Add scale_epsilon to manifest
        "scale_epsilon": 1e-12,
    }
    
    protocol_params = {
        "T_sim": FROZEN_T_SIM,
        "burn_end_time": 160.0,
        "split_time": 480.0,
        "future_duration": 320.0,
        "diagnostic_stride": 50,
        "branches": list(STUDY_BRANCHES),
    }
    
    study_params = {
        "rho_values": list(rho_values),
        "T_window_values": [rho * FROZEN_T_STAR for rho in rho_values],
        "n_seeds": len(seeds),
        "statistical_unit": "40 seed/graphs",
    }
    
    # Add dependencies - engine and driver source hashes
    dependencies = {}
    
    # Engine source hash
    try:
        engine_path = Path(engine.__file__).resolve()
        engine_hash = file_sha256(engine_path)
        dependencies["aief_experiment_engine_v1"] = {
            "path": str(engine_path),
            "sha256": engine_hash,
        }
    except Exception as e:
        dependencies["aief_experiment_engine_v1"] = {
            "path": "NOT_FOUND",
            "sha256": "NOT_AVAILABLE",
            "error": str(e),
        }
    
    # Driver source hash (this file)
    try:
        driver_path = Path(__file__).resolve()
        driver_hash = file_sha256(driver_path)
        dependencies["AIEF_1_4_Twindow_sensitivity"] = {
            "path": str(driver_path),
            "sha256": driver_hash,
        }
    except Exception as e:
        dependencies["AIEF_1_4_Twindow_sensitivity"] = {
            "path": "NOT_FOUND",
            "sha256": "NOT_AVAILABLE",
            "error": str(e),
        }
    
    manifest = {
        "study_name": STUDY_NAME,
        "workflow_version": WORKFLOW_VERSION,
        "source_sha256": source_sha256(),
        "dependencies": dependencies,
        "model": model_params,
        "protocol": protocol_params,
        "study": study_params,
        "randomization": {
            "master_seed": int(master_seed),
            "paired_seeds": [int(seed) for seed in seeds],
            "seed_generation": "SeedSequence(master_seed).spawn(n_seeds)",
            "branch_generation": "second per-seed child sequence spawns named uint64 branch seeds",
            "bit_generator": np.random.default_rng(0).bit_generator.__class__.__name__,
            # P1 #14: Record the full RNG namespace explicitly
            "branch_rng_namespace": list(FROZEN_BRANCH_ORDER),
            "executed_branches": list(STUDY_BRANCHES),
        },
        # P1 #9: Add pandas to environment
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "platform": platform.platform(),
        },
        "schema": {
            "prefix_keys": list(REQUIRED_PREFIX_KEYS),
            "branch_scalar_keys": list(BRANCH_SCALAR_KEYS),
            "branch_matrix_keys": list(BRANCH_MATRIX_KEYS),
            "required_branch_scalar_keys": list(REQUIRED_BRANCH_SCALAR_KEYS),
            "required_branch_matrix_keys": list(REQUIRED_BRANCH_MATRIX_KEYS),
        },
        "notes": {
            "purpose": "T_window sensitivity study - varying T_window = rho * T_*",
            "T_*": FROZEN_T_STAR,
            "fixed_physical_horizons": {
                "immediate": f"0-{PHYSICAL_IMMEDIATE_END} time units",
                "recovery": f"{PHYSICAL_IMMEDIATE_END}-{PHYSICAL_RECOVERY_END} time units",
                "late": f"{PHYSICAL_RECOVERY_END}-{PHYSICAL_FUTURE_END} time units",
            },
            "ema_normalized_horizons": {
                "immediate": "0-1 T_window",
                "recovery": "1-5 T_window",
                "late": "5 T_window to end",
            },
            "full_regeneration": "Each (seed, rho) pair is independently initialized",
        },
    }
    
    return manifest


def flatten_result(
    seed: int,
    rho: float,
    result: dict[str, Any],
) -> dict[str, Any]:
    """Flatten a (seed, rho) result into a flat dict for NPZ storage."""
    payload: dict[str, Any] = {
        f"seed_{seed}_rho_{rho}_config_T_window": result["config"]["T_window"],
        f"seed_{seed}_rho_{rho}_config_alpha": result["config"]["alpha"],
    }
    
    # Add prefix keys
    for key, value in result["prefix"].items():
        payload[f"prefix_seed_{seed}_rho_{rho}_{key}"] = value
    
    # Add branch results
    for branch, branch_result in result["branches"].items():
        for key, value in branch_result.items():
            if isinstance(value, np.ndarray):
                payload[f"{branch}_seed_{seed}_rho_{rho}_{key}"] = value
            else:
                payload[f"{branch}_seed_{seed}_rho_{rho}_{key}"] = value
    
    return payload


def extract_scalar_row(
    seed: int,
    seed_index: int,
    rho: float,
    branch: str,
    branch_result: dict[str, Any],
) -> dict[str, Any]:
    """Extract a scalar row for CSV output.
    
    P1 #3: Removed duplicate validation call.
    Validation is already performed in simulate_seed_rho() immediately after simulation.
    This function only extracts.
    """
    # P1 #3: Removed duplicate validation - already validated in simulate_seed_rho()
    # The branch_result already has T_window and rho added before validation
    
    row = {
        "seed_index": seed_index,
        "seed": seed,
        "rho": rho,
        "T_window": branch_result.get("T_window", float('nan')),
        "branch": branch,
    }
    
    for key in BRANCH_SCALAR_KEYS:
        if key in branch_result:
            row[key] = branch_result[key]
        else:
            row[key] = float('nan')
    
    return row


# =============================================================================
# Main Execution
# =============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--master-seed",
        type=int,
        default=DEFAULT_MASTER_SEED,
        help="fixed integer master seed (default: 20260714). For production, must match frozen data.",
    )
    parser.add_argument(
        "--n-seeds",
        type=int,
        default=DEFAULT_N_SEEDS,
        help=f"number of seeds (default: {DEFAULT_N_SEEDS})",
    )
    parser.add_argument(
        "--run-root",
        default=DEFAULT_RUN_ROOT,
        help=f"output root directory (default: {DEFAULT_RUN_ROOT})",
    )
    parser.add_argument(
        "--frozen-manifest",
        default=None,
        help="path to frozen manifest for baseline equivalence test. "
             "Generate with: python3 AIEF_1_4_memory_ablation_updated_REAL.py --master-seed 20260714 --n-seeds 40",
    )
    parser.add_argument(
        "--frozen-npz",
        default=None,
        help="path to frozen NPZ for baseline equivalence test. "
             "Generate with: python3 AIEF_1_4_memory_ablation_updated_REAL.py --master-seed 20260714 --n-seeds 40",
    )
    parser.add_argument(
        "--frozen-scalar",
        default=None,
        help="path to frozen scalar CSV for baseline equivalence test. "
             "MANDATORY for scalar validation. Generate with: python3 AIEF_1_4_memory_ablation_updated_REAL.py --master-seed 20260714 --n-seeds 40",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing run directory. Use with caution - will delete existing data.",
    )
    # NOTE: --skip-baseline removed for production safety
    # Baseline equivalence is MANDATORY and cannot be skipped
    # For debugging, use a separate nonproduction namespace
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate configuration and exit without running",
    )
    parser.add_argument(
        "--baseline-only",
        action="store_true",
        help=(
            "run and save the mandatory frozen-baseline "
            "certificate, then exit without launching the grid"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_arguments()
    
    # Generate seeds
    seeds = generate_seed_set(int(args.master_seed), args.n_seeds)
    
    # Build manifest
    manifest = build_manifest(
        master_seed=int(args.master_seed),
        seeds=seeds,
        rho_values=RHO_VALUES,
    )
    
    # Compute config hash
    manifest_text = json.dumps(
        manifest, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    config_hash = hashlib.sha256(manifest_text.encode()).hexdigest()[:12]
    
    # P1 #12: Validate driver/engine contract
    try:
        validate_engine_contract()
    except RuntimeError as e:
        print(f"\nFATAL: Driver/engine contract violation: {e}")
        sys.exit(1)
    
    # Check dry-run mode FIRST to avoid contaminating production directory
    # P0 #1: Dry-run should not require frozen paths
    if args.dry_run:
        # Validate driver/engine contract (already validated above, but keep for clarity)
        try:
            validate_engine_contract()
        except RuntimeError as e:
            print(f"\nDry run: Driver/engine contract violation: {e}")
            sys.exit(1)
        
        # P1 #11: Dry-run should actually validate configuration
        # Validate all levels
        protocol_config = create_protocol_config()
        try:
            # Validate base config (rho=1.0)
            base_config = create_model_config(1.0)
            base_config.validate()
            protocol_config.validate(base_config)
            
            # Validate all rho configs
            for rho in RHO_VALUES:
                config = create_model_config(rho)
                config.validate()
                protocol_config.validate(config)
            
            # Validate study design
            if not set(STUDY_BRANCHES) <= set(FROZEN_BRANCH_ORDER):
                raise ValueError(f"STUDY_BRANCHES {STUDY_BRANCHES} not subset of FROZEN_BRANCH_ORDER {FROZEN_BRANCH_ORDER}")
            if len(STUDY_BRANCHES) != len(set(STUDY_BRANCHES)):
                raise ValueError(f"STUDY_BRANCHES has duplicates: {STUDY_BRANCHES}")
            if len(RHO_VALUES) != len(set(RHO_VALUES)):
                raise ValueError(f"RHO_VALUES has duplicates: {RHO_VALUES}")
            if 1.0 not in RHO_VALUES:
                raise ValueError("RHO_VALUES must include 1.0 for baseline equivalence")
            
            print("Dry run: configuration validated successfully.")
            print(f"  Validated {len(RHO_VALUES)} rho values: {RHO_VALUES}")
            print(f"  Validated {len(STUDY_BRANCHES)} study branches: {STUDY_BRANCHES}")
            print(f"  Validated {args.n_seeds} seeds from master seed {args.master_seed}")
            print(f"Configuration hash: {config_hash}")
            print("To execute, run without --dry-run")
            print(f"Expected run directory: {Path(args.run_root) / config_hash}")
        except Exception as e:
            print(f"Dry run: configuration validation FAILED: {e}")
            sys.exit(1)
        return
    
    # P1 #10: Validate mandatory input paths before creating/deleting run directory
    # This prevents contaminating a production root after a simple path error
    for path_name, path_value in [
        ("frozen-manifest", args.frozen_manifest),
        ("frozen-npz", args.frozen_npz),
        ("frozen-scalar", args.frozen_scalar),
    ]:
        if path_value is None:
            print(f"\n{path_name} path not provided!")
            print("All frozen baseline artifacts are required for production runs.")
            print("To generate frozen data, run:")
            print("  python3 AIEF_1_4_memory_ablation_updated_REAL.py --master-seed 20260714 --n-seeds 40")
            print("Then provide all paths with --frozen-manifest, --frozen-npz, --frozen-scalar")
            sys.exit(1)
        if not os.path.isfile(path_value):
            print(f"\n{path_name} file not found: {path_value}")
            print("To generate frozen data, run:")
            print("  python3 AIEF_1_4_memory_ablation_updated_REAL.py --master-seed 20260714 --n-seeds 40")
            print("Then use the generated run directory path.")
            sys.exit(1)
    
    # Create run directory
    run_dir = Path(args.run_root) / config_hash
    
    # Check if run directory already exists
    if run_dir.exists():
        if args.overwrite:
            # Overwrite mode: remove existing directory
            print(f"Overwriting existing run directory: {run_dir}")
            try:
                shutil.rmtree(run_dir)
            except Exception as e:
                print(f"Cannot overwrite: error removing directory: {e}")
                sys.exit(1)
            run_dir.mkdir(parents=True, exist_ok=True)
        
        else:
            # Default: fail if directory exists
            print(f"Run directory {run_dir} already exists")
            print("Use --overwrite to replace")
            sys.exit(1)
    else:
        # New run directory
        run_dir.mkdir(parents=True, exist_ok=True)
    
    # Save manifest
    manifest["config_hash"] = config_hash
    manifest_path = run_dir / "manifest.json"
    atomic_write_json(manifest_path, manifest)
    
    print(f"{STUDY_NAME}")
    print(f"  master seed:   {args.master_seed}")
    print(f"  n_seeds:      {args.n_seeds}")
    print(f"  rho values:   {RHO_VALUES}")
    print(f"  configuration: {config_hash}")
    print(f"  output:        {run_dir}")
    print()
    
    # Create protocol config (same for all rho)
    protocol = create_protocol_config()
    
    # MANDATORY: Run baseline equivalence test at rho=1
    # This cannot be skipped - baseline equivalence is required for freezeability
    print("=" * 80)
    print("Running MANDATORY baseline equivalence test at rho=1...")
    print("=" * 80)
    
    # Validate all frozen paths are provided (MANDATORY)
    for path_name, path_value in [
        ("frozen-manifest", args.frozen_manifest),
        ("frozen-npz", args.frozen_npz),
        ("frozen-scalar", args.frozen_scalar),
    ]:
        if path_value is None:
            print(f"\n{path_name} path not provided!")
            print("All frozen baseline artifacts are required for production runs.")
            print("To generate frozen data, run:")
            print("  python3 AIEF_1_4_memory_ablation_updated_REAL.py --master-seed 20260714 --n-seeds 40")
            print("Then provide all paths with --frozen-manifest, --frozen-npz, --frozen-scalar")
            sys.exit(1)
        if not os.path.isfile(path_value):
            print(f"\n{path_name} file not found: {path_value}")
            print("To generate frozen data, run:")
            print("  python3 AIEF_1_4_memory_ablation_updated_REAL.py --master-seed 20260714 --n-seeds 40")
            print("Then use the generated run directory path.")
            sys.exit(1)
    
    # Run baseline equivalence - MANDATORY for all seeds
    try:
        baseline_results = run_baseline_equivalence(
            seeds=seeds,
            frozen_manifest_path=args.frozen_manifest,
            frozen_npz_path=args.frozen_npz,
            frozen_csv_path=args.frozen_scalar,
        )
    except Exception as exc:
        # Handle baseline equivalence exception - save failure manifest
        failure_manifest = {
            **manifest,
            "config_hash": config_hash,
            "status": "FAILED",
            "failure_reason": "baseline_equivalence_exception",
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "freezeable": False,
        }
        failure_manifest_path = run_dir / "FAILED_manifest.json"
        atomic_write_json(failure_manifest_path, failure_manifest)
        print(f"\nBaseline equivalence exception occurred!")
        print(f"Failure manifest saved to {failure_manifest_path}")
        print(f"Exception: {type(exc).__name__}: {exc}")
        sys.exit(1)
    
    if baseline_results["status"] != "passed":
        error_msg = baseline_results.get('error', 'unknown')
        print(f"\nBaseline equivalence test FAILED: {error_msg}")
        
        # Check if it's a configuration mismatch
        if "mismatch" in error_msg.lower():
            print("\nConfiguration mismatch detected!")
            print("The frozen data does not match the expected production configuration.")
            print("Expected configuration (from AIEF_1_4_memory_ablation_updated_REAL.py):")
            print(f"  N={FROZEN_N}, DT={FROZEN_DT}, TAU={FROZEN_TAU}")
            print(f"  OMEGA={FROZEN_OMEGA.tolist()}")
            print(f"  T_WINDOW={FROZEN_T_STAR:.6f}")
            print("\nTo generate correct frozen data:")
            print("  python3 AIEF_1_4_memory_ablation_updated_REAL.py --master-seed 20260714 --n-seeds 40")
            print("Then use the generated run directory path with --frozen-manifest and --frozen-npz")
        
        # Save failure manifest with detailed results
        failure_manifest = {
            **manifest,
            "config_hash": config_hash,
            "status": "FAILED",
            "failure_reason": "baseline_equivalence_failed",
            "failure_details": baseline_results,
            "freezeable": False,
        }
        failure_manifest_path = run_dir / "FAILED_manifest.json"
        atomic_write_json(failure_manifest_path, failure_manifest)
        
        # Also save detailed per-seed results
        if "seed_results" in baseline_results:
            baseline_eq_path = run_dir / "baseline_equivalence_by_seed.json"
            atomic_write_json(baseline_eq_path, baseline_results["seed_results"])
            print(f"  Per-seed results saved to {baseline_eq_path}")
        
        print(f"\nFailure manifest saved to {failure_manifest_path}")
        
        sys.exit(1)
    else:
        print("\nBaseline equivalence test PASSED")
        print("=" * 80)
        
        # Save detailed baseline equivalence certificate
        baseline_cert_path = run_dir / "baseline_equivalence_certificate.json"
        atomic_write_json(baseline_cert_path, baseline_results)
        print(f"  Detailed certificate saved to {baseline_cert_path}")
        
        # Save per-seed baseline results separately for easier audit
        if "seed_results" in baseline_results:
            baseline_seed_path = run_dir / "baseline_equivalence_by_seed.json"
            atomic_write_json(baseline_seed_path, baseline_results["seed_results"])
            print(f"  Per-seed results saved to {baseline_seed_path}")
        
        # P0 #3: Update manifest with baseline equivalence certificate
        # Record all frozen input hashes using CORRECT engine key names
        # Engine returns: frozen_manifest_file_sha256, frozen_npz_file_sha256, frozen_scalar_csv_file_sha256
        # Engine also returns: frozen_manifest, frozen_npz, frozen_manifest_hash
        
        frozen_input_hashes = {}
        
        # Get frozen manifest file hash (engine key: frozen_manifest_file_sha256)
        if "frozen_manifest_file_sha256" in baseline_results:
            frozen_input_hashes["manifest_file_sha256"] = baseline_results["frozen_manifest_file_sha256"]
        if "frozen_manifest" in baseline_results:
            frozen_input_hashes["manifest_path"] = baseline_results["frozen_manifest"]
        
        # Get frozen NPZ file hash (engine key: frozen_npz_file_sha256)
        if "frozen_npz_file_sha256" in baseline_results:
            frozen_input_hashes["npz_file_sha256"] = baseline_results["frozen_npz_file_sha256"]
        if "frozen_npz" in baseline_results:
            frozen_input_hashes["npz_path"] = baseline_results["frozen_npz"]
        
        # Get frozen scalar CSV file hash (engine key: frozen_scalar_csv_file_sha256)
        if "frozen_scalar_csv_file_sha256" in baseline_results:
            frozen_input_hashes["scalar_csv_file_sha256"] = baseline_results["frozen_scalar_csv_file_sha256"]
        
        # Get canonical JSON hash of frozen manifest (engine key: frozen_manifest_hash)
        if "frozen_manifest_hash" in baseline_results:
            frozen_input_hashes["manifest_canonical_json_sha256"] = baseline_results["frozen_manifest_hash"]
        
        # Read frozen production source hash from frozen manifest itself
        # This is the proper way - don't search for production source files
        try:
            with open(args.frozen_manifest, 'r', encoding='utf-8') as f:
                frozen_manifest_data = json.load(f)
            if "source_sha256" in frozen_manifest_data:
                frozen_input_hashes["frozen_production_source"] = frozen_manifest_data["source_sha256"]
        except Exception:
            pass
        
        # Also include scalar CSV path for completeness
        if args.frozen_scalar:
            frozen_input_hashes["scalar_csv_path"] = str(Path(args.frozen_scalar).resolve())
        
        manifest["baseline_equivalence"] = {
            "status": "passed",
            "n_seeds_tested": baseline_results["n_seeds"],
            "n_seeds_passed": baseline_results["n_seeds"],
            "engine_source_sha256": baseline_results.get("engine_source_sha256"),
            "frozen_manifest_hash": baseline_results.get("frozen_manifest_hash"),
            "frozen_npz_hash": baseline_results.get("frozen_npz_file_sha256"),
            "frozen_csv_hash": baseline_results.get("frozen_scalar_csv_file_sha256", "N/A"),
            "frozen_production_source_hash": frozen_input_hashes.get("frozen_production_source", "N/A"),
            "frozen_input_hashes": frozen_input_hashes,
            "certificate_path": str(baseline_cert_path),
            "seed_results_path": str(baseline_seed_path) if "seed_results" in baseline_results else "N/A",
            "branches_validated": list(FROZEN_BRANCH_ORDER),  # All 7 branches
        }
        
        # Re-save manifest with baseline certificate
        atomic_write_json(manifest_path, manifest)
        
        # P0 #2: Handle --baseline-only mode
        if args.baseline_only:
            manifest["execution_mode"] = "baseline_only"
            manifest["baseline_certified"] = True
            manifest["freezeable"] = False
            manifest["completion"] = {
                "status": "baseline_only_completed",
                "study_grid_started": False,
                "baseline_passed": True,
            }
            manifest["output_hashes"] = {
                "baseline_certificate": file_sha256(baseline_cert_path),
                "baseline_seed_results": file_sha256(baseline_seed_path) if "seed_results" in baseline_results else "N/A",
            }
            atomic_write_json(manifest_path, manifest)
            print("\nBaseline-only run completed successfully.")
            print("The T_window grid was not started.")
            return
    
    # Run the study
    print("\nRunning T_window sensitivity study...")
    print(f"  rho values: {RHO_VALUES}")
    print(f"  branches: {STUDY_BRANCHES}")
    print(f"  seeds: {len(seeds)}")
    
    all_scalar_rows: list[dict[str, Any]] = []
    all_matrix_payload: dict[str, Any] = {}  # Full payload in memory; checkpoints also written per-condition
    
    # Track condition status
    condition_status = []
    successful_conditions = 0
    failed_conditions = 0
    
    started = time.time()
    total_combinations = len(seeds) * len(RHO_VALUES)
    
    # Fatal error flag for breaking outer loop on schema/config mismatch
    fatal_error = False
    
    for seed_index, seed in enumerate(seeds):
        # Check for fatal error from previous seed
        if fatal_error:
            print(f"  Skipping seed {seed} due to fatal schema/config error")
            break
            
        for rho in RHO_VALUES:
            condition_start = time.time()
            
            # Create config for this rho
            config = create_model_config(rho)
            
            # Checkpoint path for this condition (saved for diagnostic recovery, not resume)
            checkpoint_path = run_dir / f"condition_seed_{seed}_rho_{rho:.2f}.npz"
            
            try:
                # Validate config before simulation
                config.validate()
                protocol.validate(config)
                
                # Run simulation
                result = simulate_seed_rho(
                    seed=seed,
                    rho=rho,
                    config=config,
                    protocol=protocol,
                    study_branches=STUDY_BRANCHES,
                )
                
                # Extract scalar rows
                for branch in STUDY_BRANCHES:
                    branch_result = result["branches"][branch]
                    row = extract_scalar_row(
                        seed=seed,
                        seed_index=seed_index,
                        rho=rho,
                        branch=branch,
                        branch_result=branch_result,
                    )
                    all_scalar_rows.append(row)
                
                # Extract matrix payload
                matrix_payload = flatten_result(seed, rho, result)
                
                # P1 #5: NPZ key-collision detection
                overlap = set(all_matrix_payload) & set(matrix_payload)
                if overlap:
                    raise RuntimeError(
                        f"schema: NPZ key collision: {sorted(overlap)[:10]}"
                    )
                all_matrix_payload.update(matrix_payload)
                
                # Save checkpoint atomically
                save_npz_atomic(checkpoint_path, matrix_payload)
                
                condition_status.append({
                    "seed": seed,
                    "rho": rho,
                    "status": "success",
                    "elapsed_seconds": time.time() - condition_start,
                })
                successful_conditions += 1
                
            except Exception as e:
                error_str = str(e)
                condition_status.append({
                    "seed": seed,
                    "rho": rho,
                    "status": "failed",
                    "error": error_str,
                    "elapsed_seconds": time.time() - condition_start,
                })
                failed_conditions += 1
                print(f"  ERROR: seed={seed}, rho={rho:.2f}: {e}")
                
                # Stop immediately on schema/config mismatch - use fatal flag to break outer loop
                if "schema" in error_str.lower() or "config" in error_str.lower() or "missing" in error_str.lower():
                    print(f"\n  FATAL: Schema/config mismatch detected - stopping immediately")
                    print(f"  This error will affect all remaining conditions")
                    # Set fatal error flag to break outer loop after inner loop
                    fatal_error = True
                    break
            
            # Status
            elapsed = time.time() - started
            current_combination = seed_index * len(RHO_VALUES) + list(RHO_VALUES).index(rho) + 1
            status_str = f"[{current_combination}/{total_combinations}] seed={seed}, rho={rho:.2f} ({elapsed:.1f}s)"
            if successful_conditions + failed_conditions == current_combination:
                print(f"  {status_str}")
    
    # Save condition status table
    # P1 #16: pandas is mandatory (script exits at import without it), so remove dead fallback
    if condition_status:
        # pandas is guaranteed to be available due to import-time check
        status_df = pd.DataFrame(condition_status)
        status_path = run_dir / "twindow_condition_status.csv"
        save_csv_atomic(status_path, status_df)
        print(f"\nCondition status saved to {status_path}")
        
        # Record condition status in manifest
        manifest["condition_status"] = {
            "path": str(status_path),
            "sha256": file_sha256(status_path),
            "expected_rows": total_combinations,
            "successful_rows": successful_conditions,
            "failed_rows": failed_conditions,
        }
        
        # Also record pandas version in environment
        manifest["environment"]["pandas"] = pd.__version__
        
        print(f"  Successful: {successful_conditions}/{total_combinations}")
        print(f"  Failed: {failed_conditions}/{total_combinations}")
    
    # If any conditions failed, mark as non-freezeable
    if failed_conditions > 0:
        manifest["freezeable"] = False
        manifest["failed_conditions"] = failed_conditions
        atomic_write_json(manifest_path, manifest)
        print(f"\nWARNING: {failed_conditions} conditions failed - run is NOT freezeable")
    
    # Validate we have the expected number of scalar rows
    expected_rows = total_combinations * len(STUDY_BRANCHES)
    actual_rows = len(all_scalar_rows)
    if actual_rows != expected_rows:
        print(f"\nERROR: Expected {expected_rows} scalar rows, got {actual_rows}")
        print("Run is INCOMPLETE and NOT freezeable")
        
    # Validate primary outcomes are present and finite
    missing_primary = []
    for row in all_scalar_rows:
        for key in PRIMARY_OUTCOMES:
            if key not in row or not is_finite_number(row[key]):
                missing_primary.append(f"seed={row['seed']}, rho={row['rho']}, branch={row['branch']}, key={key}")
    
    # P1 #5: Validate secondary outcomes are present and finite
    missing_secondary = []
    for row in all_scalar_rows:
        for key in SECONDARY_OUTCOMES:
            if key not in row or not is_finite_number(row[key]):
                missing_secondary.append(f"seed={row['seed']}, rho={row['rho']}, branch={row['branch']}, key={key}")
    
    if missing_primary:
        print(f"\nERROR: {len(missing_primary)} primary outcomes are missing or non-finite!")
        print(f"  First 5 missing: {missing_primary[:5]}")
        print("  This indicates engine is not producing required outputs.")
        print("Run is INCOMPLETE and NOT freezeable")
    
    if missing_secondary:
        print(f"\nERROR: {len(missing_secondary)} secondary outcomes are missing or non-finite!")
        print(f"  First 5 missing: {missing_secondary[:5]}")
        print("  This indicates engine is not producing required outputs.")
        print("Run is INCOMPLETE and NOT freezeable")
    
    # Save outputs
    csv_path = run_dir / f"{STUDY_NAME}_{config_hash}_scalar_summary.csv"
    npz_path = run_dir / f"{STUDY_NAME}_{config_hash}_branch_diagnostics.npz"
    
    # Write CSV
    if all_scalar_rows:
        # Sort by seed_index, rho, branch for consistent ordering
        all_scalar_rows.sort(key=lambda r: (r["seed_index"], r["rho"], r["branch"]))
        
        # Get all fieldnames
        fieldnames = list(all_scalar_rows[0].keys())
        
        temporary_csv = csv_path.with_suffix(csv_path.suffix + ".tmp")
        try:
            with open(temporary_csv, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_scalar_rows)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(str(temporary_csv), str(csv_path))
        finally:
            if temporary_csv.exists():
                temporary_csv.unlink()
    
    # Write NPZ
    if all_matrix_payload:
        save_npz_atomic(npz_path, all_matrix_payload)
    
    # Determine completion status
    # P1 #5: Require both primary and secondary outcomes to be complete
    complete = (
        failed_conditions == 0
        and successful_conditions == total_combinations
        and len(all_scalar_rows) == expected_rows
        and len(missing_primary) == 0
        and len(missing_secondary) == 0
    )
    
    # Top-level freezeable flag
    baseline_passed = baseline_results.get("status") == "passed"
    manifest["freezeable"] = complete and baseline_passed
    
    # Final manifest update with completion status
    manifest["completion"] = {
        "status": "completed" if complete else "incomplete",
        "n_conditions_requested": total_combinations,
        "n_conditions_successful": successful_conditions,
        "n_conditions_failed": failed_conditions,
        "n_scalar_rows": len(all_scalar_rows),
        "n_matrix_entries": len(all_matrix_payload),
        "n_missing_primary_outcomes": len(missing_primary),
        "n_missing_secondary_outcomes": len(missing_secondary),
        "elapsed_seconds": time.time() - started,
        "freezeable": manifest["freezeable"],
    }
    
    # Add output hashes - hash ALL final outputs for complete provenance
    output_hashes = {}
    
    # Main outputs
    if csv_path.exists():
        output_hashes["scalar_csv"] = file_sha256(csv_path)
    if npz_path.exists():
        output_hashes["branch_npz"] = file_sha256(npz_path)
    
    # Condition status
    condition_status_path = run_dir / "twindow_condition_status.csv"
    if condition_status_path.exists():
        output_hashes["condition_status_csv"] = file_sha256(condition_status_path)
    
    # Baseline equivalence certificate
    baseline_cert_path = run_dir / "baseline_equivalence_certificate.json"
    if baseline_cert_path.exists():
        output_hashes["baseline_certificate"] = file_sha256(baseline_cert_path)
    
    # Baseline per-seed results (if saved separately)
    baseline_seed_path = run_dir / "baseline_equivalence_by_seed.json"
    if baseline_seed_path.exists():
        output_hashes["baseline_seed_results"] = file_sha256(baseline_seed_path)
    
    if output_hashes:
        manifest["output_hashes"] = output_hashes
    
    # P1 #15: Condition checkpoints are diagnostic, non-authoritative artifacts
    # The consolidated NPZ is the authority
    manifest["checkpoints"] = {
        "role": "diagnostic, non-authoritative",
        "count": successful_conditions,
        "authoritative_consolidation": str(npz_path),
    }
    
    # Re-save final manifest
    atomic_write_json(manifest_path, manifest)
    
    # Print completion status
    if complete and baseline_passed:
        print(f"\nRun COMPLETED successfully and is FREEZEABLE")
    elif complete and not baseline_passed:
        print(f"\nRun COMPLETED but baseline equivalence FAILED - NOT freezeable")
        # P0 #4: Exit nonzero for non-freezeable runs
        sys.exit(1)
    else:
        print(f"\nRun INCOMPLETE - NOT freezeable")
        if failed_conditions > 0:
            print(f"  Failed conditions: {failed_conditions}/{total_combinations}")
        if len(all_scalar_rows) != expected_rows:
            print(f"  Missing scalar rows: {expected_rows - len(all_scalar_rows)}")
        if len(missing_primary) > 0:
            print(f"  Missing primary outcomes: {len(missing_primary)}")
        # P0 #4: Exit nonzero for non-freezeable runs
        sys.exit(1)
    
    # Print summary
    elapsed = time.time() - started
    print(f"\nCompleted in {elapsed:.1f}s")
    # P1 #17: Print conditionally - only if files exist
    if csv_path.exists():
        print(f"Saved {csv_path}")
    if npz_path.exists():
        print(f"Saved {npz_path}")
    print(f"Manifest: {manifest_path}")
    # Print top-level freezeable flag
    freezeable_status = manifest.get("freezeable", False)
    print(f"Freezeable: {freezeable_status}")
    
    # Quick summary statistics
    print("\n" + "=" * 80)
    print("Summary Statistics by (rho, branch)")
    print("=" * 80)
    
    # Use the missing_primary count already computed earlier
    if missing_primary:
        print(f"WARNING: {len(missing_primary)} primary outcomes are non-finite or missing!")
        print(f"  First 5 missing: {missing_primary[:5]}")
        print("  This indicates engine is not producing required outputs.")
    
    # Group by rho and branch
    for rho in RHO_VALUES:
        for branch in STUDY_BRANCHES:
            rows = [r for r in all_scalar_rows if r["rho"] == rho and r["branch"] == branch]
            if rows:
                # Only show keys that are actually present and not all NaN
                available_keys = [k for k in PRIMARY_OUTCOMES if any(
                    k in r and not (isinstance(r[k], float) and np.isnan(r[k]))
                    for r in rows
                )]
                
                if not available_keys:
                    print(f"  rho={rho:.2f}, branch={branch:<15} | ALL PRIMARY OUTCOMES MISSING/NaN!")
                    continue
                
                stats = {}
                for key in available_keys:
                    values = [r[key] for r in rows if key in r and isinstance(r[key], (int, float)) and not np.isnan(r[key])]
                    if values:
                        # Use sample SD (ddof=1) for descriptive statistics
                        stats[key] = f"{np.mean(values):.4f}±{np.std(values, ddof=1):.4f}"
                    else:
                        stats[key] = "N/A"
                print(f"  rho={rho:.2f}, branch={branch:<15} | " + 
                      " | ".join(f"{k}={stats.get(k, 'N/A')}" for k in available_keys))


if __name__ == "__main__":
    main()
