#!/usr/bin/env python3
"""AIEF Experiment Engine v1 - Parameterized simulation kernel.

This is a reusable, validated simulation engine that reproduces the frozen
AIEF-1.4 production run exactly and supports parameterized studies.

FROZEN PRODUCTION VALUES (from AIEF_1_4_memory_ablation_updated_REAL.py):
  N = 12
  DT = 0.01
  TAU = 0.5
  OMEGA = [1.00, 1.02, 1.50, 2.00, 2.01, 1.01, 1.03, 1.51, 2.02, 2.00, 1.00, 1.04]
  A = 1.0
  Q = 1.5
  DELTA = 0.05
  ETA = 0.04
  GAMMA = 0.015
  MU = 0.03
  T_WINDOW = 25.0 / mean(OMEGA) = 17.5
  B_C = 0.12
  B_INIT_SCALE = 0.0005

PROTOCOL (from frozen run):
  T_SIM = 800.0
  N_STEPS = int(round(T_SIM / DT)) = 80000
  BURN_END = int(0.20 * N_STEPS) = 16000 steps = 160.0 time units
  HIST_END = int(0.60 * N_STEPS) = 48000 steps = 480.0 time units
  FUTURE_STEPS = N_STEPS - HIST_END = 32000 steps = 320.0 time units
  DELAY_STEPS = int(round(TAU / DT)) = 50
  WINDOW_STEPS = int(round(T_WINDOW / DT)) = 1750
  RECOVERY_END = min(5 * WINDOW_STEPS, FUTURE_STEPS) = 8750

Architecture:
  - ModelConfig: frozen dataclass for all model parameters
  - ProtocolConfig: frozen dataclass for protocol parameters
  - DynamicState: state container (immutable where possible)
  - Core functions: initialize, advance, simulate, interventions
  - Validation: baseline equivalence test

NOTE: This is a candidate reference implementation. After passing 40/40 baseline
      equivalence tests, it will be frozen as the reference implementation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


# =============================================================================
# Frozen Production Constants (DO NOT CHANGE)
# =============================================================================

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
FROZEN_ZERO_TOL = 1e-12
FROZEN_PROJECTION_NORM_TOL = 1e-14
FROZEN_GAP_TOL = 1e-9

# Derived from frozen values
FROZEN_MEAN_OMEGA = float(np.mean(FROZEN_OMEGA))  # 1.428333...
FROZEN_T_STAR = 25.0 / FROZEN_MEAN_OMEGA  # 17.502917152858814
FROZEN_T_WINDOW = FROZEN_T_STAR  # 17.502917152858814 (exact, NOT rounded)
FROZEN_ALPHA = float(np.exp(-FROZEN_DT / FROZEN_T_WINDOW))
FROZEN_CAPACITY = (FROZEN_A - FROZEN_DELTA) / FROZEN_Q

# Protocol from frozen run
FROZEN_T_SIM = 800.0
FROZEN_N_STEPS = int(round(FROZEN_T_SIM / FROZEN_DT))  # 80000
FROZEN_BURN_END = int(0.20 * FROZEN_N_STEPS)  # 16000
FROZEN_HIST_END = int(0.60 * FROZEN_N_STEPS)  # 48000
FROZEN_FUTURE_STEPS = FROZEN_N_STEPS - FROZEN_HIST_END  # 32000
FROZEN_DELAY_STEPS = int(round(FROZEN_TAU / FROZEN_DT))  # 50
FROZEN_WINDOW_STEPS = int(round(FROZEN_T_WINDOW / FROZEN_DT))  # 1750
FROZEN_RECOVERY_END = min(5 * FROZEN_WINDOW_STEPS, FROZEN_FUTURE_STEPS)  # 8750

# Fixed physical horizon boundaries (in time units, NOT T_window dependent)
# These are the PRIMARY estimand horizons
FIXED_PHYSICAL_IMMEDIATE_END = 17.5
FIXED_PHYSICAL_RECOVERY_END = 87.5
FIXED_PHYSICAL_FUTURE_END = 320.0

# Derived fixed physical horizon steps
FIXED_PHYSICAL_IMMEDIATE_STEPS = int(round(FIXED_PHYSICAL_IMMEDIATE_END / FROZEN_DT))  # 1750
FIXED_PHYSICAL_RECOVERY_STEPS = int(round(FIXED_PHYSICAL_RECOVERY_END / FROZEN_DT))  # 8750

# Baseline horizon metadata for validation
BASELINE_HORIZON_METADATA = {
    "window_steps": FROZEN_WINDOW_STEPS,
    "recovery_end_ema": FROZEN_RECOVERY_END,
    "fixed_immediate_end": FIXED_PHYSICAL_IMMEDIATE_STEPS,
    "fixed_recovery_end": FIXED_PHYSICAL_RECOVERY_STEPS,
}


# =============================================================================
# Model Configuration
# =============================================================================

@dataclass(frozen=True)
class ModelConfig:
    """Immutable model configuration.
    
    All model-changing quantities must come from here. No hidden module globals.
    """
    # Core parameters
    N: int
    dt: float
    tau: float
    omega: tuple[float, ...]  # Immutable tuple
    
    # Coupling parameters
    a: float
    q: float
    delta: float
    
    # Dynamics parameters
    eta: float
    mu: float
    gamma: float
    
    # EMA/threshold parameters
    T_window: float
    B_c: float
    B_init_scale: float
    scale_epsilon: float = 1e-12
    
    # Derived properties
    @property
    def mean_omega(self) -> float:
        """Mean of omega frequencies."""
        return float(np.mean(self.omega))
    
    @property
    def T_star(self) -> float:
        """T_* = 25 / mean(omega)"""
        return 25.0 / self.mean_omega
    
    @property
    def alpha(self) -> float:
        """EMA smoothing factor: exp(-dt / T_window)"""
        return float(np.exp(-self.dt / self.T_window))
    
    @property
    def capacity(self) -> float:
        """Projection capacity: (a - delta) / q"""
        return (self.a - self.delta) / self.q
    
    @property
    def delay_steps(self) -> int:
        """Delay steps: round(tau / dt)"""
        return int(round(self.tau / self.dt))
    
    def validate(self) -> None:
        """Validate model configuration with strict consistency checks.
        
        Uses rtol=0, atol=0 for exact compatibility with frozen production.
        All scalar parameters must be finite.
        """
        # P0 #5: Validate N is a positive integer (not a float)
        if (
            isinstance(self.N, (bool, np.bool_))
            or not isinstance(self.N, (int, np.integer))
            or self.N <= 0
        ):
            raise ValueError("N must be a positive integer")
        
        # Validate all other scalar parameters are finite
        if not np.isfinite(self.dt) or self.dt <= 0:
            raise ValueError("dt must be finite and positive")
        if not np.isfinite(self.tau) or self.tau <= 0:
            raise ValueError("tau must be finite and positive")
        if not np.isfinite(self.a) or self.a <= 0:
            raise ValueError("a must be finite and positive")
        if not np.isfinite(self.q) or self.q <= 0:
            raise ValueError("q must be finite and positive")
        if not np.isfinite(self.delta) or self.delta < 0:
            raise ValueError("delta must be finite and nonnegative")
        if not np.isfinite(self.eta) or self.eta < 0:
            raise ValueError("eta must be finite and nonnegative")
        if not np.isfinite(self.mu) or self.mu < 0:
            raise ValueError("mu must be finite and nonnegative")
        if not np.isfinite(self.gamma) or self.gamma < 0:
            raise ValueError("gamma must be finite and nonnegative")
        if not np.isfinite(self.T_window) or self.T_window <= 0:
            raise ValueError("T_window must be finite and positive")
        if not np.isfinite(self.B_c) or self.B_c < 0:
            raise ValueError("B_c must be finite and nonnegative")
        if not np.isfinite(self.B_init_scale) or self.B_init_scale < 0:
            raise ValueError("B_init_scale must be finite and nonnegative")
        if not np.isfinite(self.scale_epsilon) or self.scale_epsilon <= 0:
            raise ValueError("scale_epsilon must be finite and positive")
        
        # Validate N is positive integer
        if self.N <= 0:
            raise ValueError("N must be positive")
        
        # Validate omega
        if len(self.omega) != self.N:
            raise ValueError(f"omega must have {self.N} elements")
        if not np.all(np.isfinite(self.omega)):
            raise ValueError("omega must contain only finite values")
        
        # Validate derived values
        if not (0 < self.alpha <= 1):
            raise ValueError(f"alpha={self.alpha} must be in (0, 1]")
        if self.capacity < 0:
            raise ValueError(f"capacity={self.capacity} must be nonnegative")
        
        # Strict consistency: delay_steps * dt must equal tau (exact)
        if not np.isclose(self.delay_steps * self.dt, self.tau, rtol=0.0, atol=0.0):
            raise ValueError(
                f"delay_steps * dt ({self.delay_steps} * {self.dt} = {self.delay_steps * self.dt}) "
                f"must equal tau ({self.tau}) exactly"
            )


@dataclass(frozen=True)
class ProtocolConfig:
    """Protocol configuration for experiment execution."""
    # Simulation time parameters (in time units, not steps)
    T_sim: float
    burn_end_time: float
    split_time: float
    future_duration: float
    
    # Diagnostics
    diagnostic_stride: int
    
    # Branches to simulate
    branches: tuple[str, ...]
    
    def n_steps(self, model: ModelConfig) -> int:
        """Total steps."""
        return int(round(self.T_sim / model.dt))
    
    def burn_end(self, model: ModelConfig) -> int:
        """Burn-in end step."""
        return int(round(self.burn_end_time / model.dt))
    
    def hist_end(self, model: ModelConfig) -> int:
        """History end step (split point)."""
        return int(round(self.split_time / model.dt))
    
    def future_steps(self, model: ModelConfig) -> int:
        """Future simulation steps."""
        return int(round(self.future_duration / model.dt))
    
    def validate(self, model: ModelConfig) -> None:
        """Validate protocol against model with strict consistency checks.
        
        Uses rtol=0, atol=0 for exact compatibility with frozen production.
        """
        # P0 #6: Validate protocol values are finite
        if not np.all(np.isfinite([self.T_sim, self.burn_end_time, self.split_time, self.future_duration])):
            raise ValueError("All protocol time parameters must be finite")
        
        # P0 #6: Validate branches are non-empty and have no duplicates
        if not self.branches:
            raise ValueError("branches must be nonempty")
        if len(self.branches) != len(set(self.branches)):
            raise ValueError("protocol branches contain duplicates")
        
        # P1 #10-11: Validation hardening - integer validation
        # Validate diagnostic_stride is a positive integer (not bool)
        if (
            isinstance(self.diagnostic_stride, (bool, np.bool_))
            or not isinstance(self.diagnostic_stride, (int, np.integer))
            or self.diagnostic_stride <= 0
        ):
            raise ValueError("diagnostic_stride must be a positive integer")
        
        if self.T_sim <= 0:
            raise ValueError("T_sim must be positive")
        if not (0 < self.burn_end_time < self.split_time < self.T_sim):
            raise ValueError("Invalid time parameters: must have 0 < burn_end < split < T_sim")
        if self.future_duration <= 0:
            raise ValueError("future_duration must be positive")
        if self.diagnostic_stride <= 0:
            raise ValueError("diagnostic_stride must be positive")
        
        # Strict consistency: split_time + future_duration must equal T_sim
        if not np.isclose(self.split_time + self.future_duration, self.T_sim, rtol=0.0, atol=0.0):
            raise ValueError(
                f"split_time ({self.split_time}) + future_duration ({self.future_duration}) "
                f"= {self.split_time + self.future_duration} must equal T_sim ({self.T_sim}) exactly"
            )
        
        # Validate that all time parameters are compatible with dt (exact divisibility)
        if not np.isclose(self.T_sim / model.dt, round(self.T_sim / model.dt), rtol=0.0, atol=0.0):
            raise ValueError(f"T_sim ({self.T_sim}) must be divisible by dt ({model.dt}) exactly")
        if not np.isclose(self.burn_end_time / model.dt, round(self.burn_end_time / model.dt), rtol=0.0, atol=0.0):
            raise ValueError(f"burn_end_time ({self.burn_end_time}) must be divisible by dt ({model.dt}) exactly")
        if not np.isclose(self.split_time / model.dt, round(self.split_time / model.dt), rtol=0.0, atol=0.0):
            raise ValueError(f"split_time ({self.split_time}) must be divisible by dt ({model.dt}) exactly")
        if not np.isclose(self.future_duration / model.dt, round(self.future_duration / model.dt), rtol=0.0, atol=0.0):
            raise ValueError(f"future_duration ({self.future_duration}) must be divisible by dt ({model.dt}) exactly")


# Default frozen production configuration
# NOTE: T_window must be the EXACT value 25.0/mean(OMEGA), not rounded
DEFAULT_MODEL_CONFIG = ModelConfig(
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
    T_window=FROZEN_T_WINDOW,  # 17.502917152858814 (exact)
    B_c=FROZEN_B_C,
    B_init_scale=FROZEN_B_INIT_SCALE,
    scale_epsilon=FROZEN_ZERO_TOL,
)

# Default protocol matching frozen run
DEFAULT_PROTOCOL_CONFIG = ProtocolConfig(
    T_sim=FROZEN_T_SIM,
    burn_end_time=160.0,   # 0.20 * 800
    split_time=480.0,     # 0.60 * 800
    future_duration=320.0, # 800 - 480
    diagnostic_stride=50,
    branches=("continue", "reset_ema", "reset_B", "reset_B_ema", "B_carrier_only", "full_reset", "future_shuffle"),
)


# =============================================================================
# Cached Utility Values
# =============================================================================

# Cache for compute_edges to avoid recomputing on every step
_EDGES_CACHE: dict[int, tuple[np.ndarray, np.ndarray]] = {}

# Cache for omega array conversion
_OMEGA_ARRAY_CACHE: dict[tuple[float, ...], np.ndarray] = {}


# =============================================================================
# Utility Functions
# =============================================================================

def compute_edges(N: int) -> tuple[np.ndarray, np.ndarray]:
    """Get upper triangle indices for edges.
    
    Cached to avoid recomputing on every step.
    """
    if N not in _EDGES_CACHE:
        _EDGES_CACHE[N] = np.triu_indices(N, k=1)
    return _EDGES_CACHE[N]


def get_omega_array(omega_tuple: tuple[float, ...]) -> np.ndarray:
    """Get omega as numpy array with caching.
    
    Cached to avoid recomputing on every step.
    """
    if omega_tuple not in _OMEGA_ARRAY_CACHE:
        _OMEGA_ARRAY_CACHE[omega_tuple] = np.asarray(omega_tuple, dtype=float)
    return _OMEGA_ARRAY_CACHE[omega_tuple]


def validate_B_matrix(B: np.ndarray, N: int, eps: float = FROZEN_ZERO_TOL) -> None:
    """Validate B matrix: symmetric, nonnegative, zero diagonal."""
    if B.shape != (N, N):
        raise ValueError(f"B shape {B.shape} != ({N}, {N})")
    # Recommended #5: Use strict rtol=0.0, atol=FROZEN_ZERO_TOL
    if not np.allclose(B, B.T, rtol=0.0, atol=eps):
        raise ValueError("B is not symmetric")
    if not np.allclose(np.diag(B), 0, rtol=0.0, atol=eps):
        raise ValueError("B diagonal is not zero")
    if np.any(B < -eps):
        raise ValueError("B has negative entries")


def file_sha256(path: str | os.PathLike[str]) -> str:
    """Compute SHA-256 hash of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_sha256(arr: np.ndarray) -> str:
    """Compute SHA-256 hash of a numpy array."""
    digest = hashlib.sha256()
    shape_bytes = np.asarray(arr.shape, dtype=np.int64).tobytes()
    digest.update(shape_bytes)
    digest.update(arr.dtype.str.encode())
    contiguous = np.ascontiguousarray(arr)
    if contiguous.size > 0:
        digest.update(contiguous.tobytes())
    return digest.hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    """Write text atomically with fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(tmp_path), str(path))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically with fsync."""
    text = json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n"
    atomic_write_text(path, text)


def atomic_write_npz(path: Path, **kwargs: Any) -> None:
    """Write NPZ atomically with fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp.npz")
    try:
        with os.fdopen(fd, "wb") as handle:
            np.savez(handle, **kwargs)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(tmp_path), str(path))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# =============================================================================
# RNG Utilities (matching frozen production exactly)
# =============================================================================

def make_seed_sequence(seed: int, child_index: int) -> int:
    """Generate a child seed from SeedSequence(seed).spawn(...)[child_index].
    
    This matches the frozen production RNG hierarchy exactly.
    """
    from numpy.random import SeedSequence
    root = SeedSequence(seed)
    children = root.spawn(child_index + 1)
    return int(children[child_index].generate_state(1, dtype=np.uint64)[0])


def make_prefix_rng(seed: int) -> np.random.Generator:
    """Create prefix RNG matching frozen production exactly.
    
    Frozen production does:
        root = np.random.SeedSequence(seed)
        init_sequence, _ = root.spawn(2)
        rng = np.random.default_rng(init_sequence)
    
    NOTE: default_rng(SeedSequence_object) is NOT the same as
          default_rng(SeedSequence_object.generate_state(...))
    The production uses the SeedSequence object directly.
    """
    from numpy.random import SeedSequence
    root = SeedSequence(seed)
    init_sequence, _ = root.spawn(2)
    return np.random.default_rng(init_sequence)


def make_branch_rngs(seed: int, branch_order: tuple[str, ...]) -> dict[str, np.random.Generator]:
    """Create branch RNGs matching frozen production algorithm.
    
    Frozen: _, branch_root = SeedSequence(seed).spawn(2)
           branch_sequences = branch_root.spawn(len(branch_order))
           branch_rng_seeds = {branch: int(sequence.generate_state(1, dtype=np.uint64)[0])
                              for branch, sequence in zip(branch_order, branch_sequences)}
    """
    from numpy.random import SeedSequence
    root = SeedSequence(seed)
    _, branch_root = root.spawn(2)
    branch_sequences = branch_root.spawn(len(branch_order))
    
    return {
        branch: np.random.default_rng(int(sequence.generate_state(1, dtype=np.uint64)[0]))
        for branch, sequence in zip(branch_order, branch_sequences)
    }


# =============================================================================
# Projection Accumulator (matching production)
# =============================================================================

@dataclass
class ProjectionTotals:
    """Accumulator for projection diagnostics - exact match to production."""
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
        """Update accumulator with step info."""
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
        """Compute final metrics from accumulated values."""
        active_denominator = max(self.active, 1)
        return {
            "G_min_future": float(self.g_min),
            "G_min_pre_future": float(self.g_min_pre),
            "Pre_gap_violation_fraction": float(self.violations / self.steps),
            "Projection_active_fraction": float(self.active / self.steps),
            "Projection_active_given_violation": float(self.active / self.violations)
                if self.violations > 0
                else float('nan'),
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
# Dynamic State
# =============================================================================

class DynamicState:
    """State container for AIEF-1.4 dynamics.
    
    Matches the frozen production implementation exactly.
    """
    
    def __init__(
        self,
        theta: np.ndarray,
        B: np.ndarray,
        coherence_acc: np.ndarray,
        history: list[np.ndarray] | np.ndarray,
    ):
        self.theta = np.asarray(theta, dtype=float).copy()
        self.B = np.asarray(B, dtype=float).copy()
        self.coherence_acc = np.asarray(coherence_acc, dtype=complex).copy()
        
        # Handle history input - ensure it's a list of arrays
        if isinstance(history, np.ndarray):
            # If it's a 2D array, convert to list of 1D arrays
            self.history = [np.asarray(h, dtype=float).copy() for h in history]
        else:
            self.history = [np.asarray(h, dtype=float).copy() for h in history]
    
    def clone(self) -> "DynamicState":
        """Create a deep copy of the state."""
        return DynamicState(
            theta=self.theta.copy(),
            B=self.B.copy(),
            coherence_acc=self.coherence_acc.copy(),
            history=[h.copy() for h in self.history],
        )
    
    @property
    def N(self) -> int:
        return len(self.theta)
    
    def validate(self, config: ModelConfig, step: int | None = None) -> None:
        """Validate state consistency.
        
        Checks:
        - State dimension matches config.N
        - History length is exactly delay_steps + 1
        - All arrays have correct shapes
        - B matrix is symmetric, zero-diagonal, non-negative
        - All history vectors have shape (N,)
        - All arrays are finite
        """
        # Check state dimension matches config
        if self.N != config.N:
            raise RuntimeError(
                f"State N ({self.N}) does not match config N ({config.N})"
            )
        
        # Check history length
        expected_history_len = config.delay_steps + 1
        if len(self.history) != expected_history_len:
            raise RuntimeError(
                f"History length {len(self.history)} != expected {expected_history_len} "
                f"(delay_steps={config.delay_steps}) at step {step}"
            )
        
        # Check all history vectors have correct shape
        for i, h in enumerate(self.history):
            if h.shape != (self.N,):
                raise RuntimeError(
                    f"History[{i}] shape {h.shape} != ({self.N},)"
                )
        
        # Check theta shape
        if self.theta.shape != (self.N,):
            raise RuntimeError(f"theta shape {self.theta.shape} != ({self.N},)")
        
        # Check B shape
        if self.B.shape != (self.N, self.N):
            raise RuntimeError(f"B shape {self.B.shape} != ({self.N}, {self.N})")
        
        # Check coherence_acc shape
        if self.coherence_acc.shape != (self.N, self.N):
            raise RuntimeError(f"coherence_acc shape {self.coherence_acc.shape} != ({self.N}, {self.N})")
        
        # Check all arrays are finite
        if not np.all(np.isfinite(self.theta)):
            raise RuntimeError("theta contains non-finite values")
        if not np.all(np.isfinite(self.B)):
            raise RuntimeError("B contains non-finite values")
        if not np.all(np.isfinite(self.coherence_acc)):
            raise RuntimeError("coherence_acc contains non-finite values")
        for i, h in enumerate(self.history):
            if not np.all(np.isfinite(h)):
                raise RuntimeError(f"History[{i}] contains non-finite values")
        
        # Check B symmetry
        # Recommended #5: Use strict rtol=0.0, atol=FROZEN_ZERO_TOL
        if not np.allclose(self.B, self.B.T, rtol=0.0, atol=FROZEN_ZERO_TOL):
            raise RuntimeError("B matrix is not symmetric")
        
        # Check B diagonal
        if not np.allclose(np.diag(self.B), 0, rtol=0.0, atol=FROZEN_ZERO_TOL):
            raise RuntimeError("B matrix diagonal is not zero")
        
        # Check B non-negativity
        if np.any(self.B < -FROZEN_ZERO_TOL):
            raise RuntimeError("B matrix has negative entries")


# =============================================================================
# Simulation Core (exact reproduction of frozen production)
# =============================================================================

def initialize_state(
    seed: int,
    config: ModelConfig,
) -> DynamicState:
    """Initialize state from seed using frozen algorithm exactly.
    
    Matches production: simulate_prefix() initialization.
    Uses: root = SeedSequence(seed); init_sequence, _ = root.spawn(2)
          rng = default_rng(init_sequence)
    """
    N = config.N
    rng = make_prefix_rng(seed)
    
    # Initialize theta: uniform in [0, 2*pi) - matching production
    theta = rng.random(N) * 2.0 * np.pi
    
    # Initialize B: small random symmetric matrix
    B = config.B_init_scale * rng.random((N, N))
    B = 0.5 * (B + B.T)
    np.fill_diagonal(B, 0.0)
    
    # Initialize coherence accumulator
    coherence_acc = np.zeros((N, N), dtype=complex)
    
    # Initialize history: DELAY_STEPS + 1 copies of theta
    history = [theta.copy() for _ in range(config.delay_steps + 1)]
    
    return DynamicState(
        theta=theta,
        B=B,
        coherence_acc=coherence_acc,
        history=history,
    )


def compute_R(
    state: DynamicState,
    config: ModelConfig,
) -> np.ndarray:
    """Compute coherence matrix R from current state.
    
    Exact reproduction of production compute_R().
    """
    N = state.N
    delayed = state.history[0]
    
    # Convert omega to numpy array for indexing (cached)
    omega_arr = get_omega_array(config.omega)
    
    dphi = (
        state.theta[:, None]
        - delayed[None, :]
        - ((omega_arr[:, None] + omega_arr[None, :]) / 2.0) * config.tau
    )
    z_inst = np.exp(1j * dphi)
    
    # Update EMA
    state.coherence_acc[:] = (
        config.alpha * state.coherence_acc + (1.0 - config.alpha) * z_inst
    )
    
    # Compute magnitude and symmetrize
    result = np.abs(state.coherence_acc)
    result = 0.5 * (result + result.T)
    np.fill_diagonal(result, 0.0)
    
    return result


def advance_state(
    state: DynamicState,
    config: ModelConfig,
    rng: np.random.Generator,
    shuffle_driver: bool = False,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Advance state by one time step.
    
    Exact reproduction of production advance_state().
    Returns (R_physical, R_driver, info).
    
    Production also returns projection diagnostics:
    - projection_active: whether correction was applied
    - projection_norm: norm of correction
    - projection_relative_state: correction_norm / ||B_unprojected||
    - projection_relative_update: correction_norm / ||B_unprojected - B_previous||
    """
    N = state.N
    edges = compute_edges(N)
    
    # Store previous B for projection
    B_previous = state.B.copy()
    
    # Compute R matrices
    R_physical = compute_R(state, config)
    R_driver = R_physical
    
    if shuffle_driver:
        values = R_physical[edges].copy()
        rng.shuffle(values)
        R_driver = np.zeros_like(R_physical)
        R_driver[edges] = values
        R_driver[(edges[1], edges[0])] = values
    
    # Update B
    B_unprojected = state.B + config.dt * (
        (config.eta + config.mu) * R_driver
        - config.mu
        - config.gamma * state.B
    )
    B_unprojected = np.maximum(B_unprojected, 0.0)
    B_unprojected = 0.5 * (B_unprojected + B_unprojected.T)
    np.fill_diagonal(B_unprojected, 0.0)
    
    # Projection diagnostics (matching production exactly)
    proposed_update_norm = float(np.linalg.norm(B_unprojected - B_previous))
    
    # Check gap constraint
    row_sum_pre = np.sum(B_unprojected, axis=1)
    g_min_pre = float(np.min(config.a - config.q * row_sum_pre))
    pre_violation = bool(g_min_pre < config.delta)
    
    # Project if needed
    B_projected = B_unprojected
    correction_norm = 0.0
    if pre_violation:
        scale = np.minimum(1.0, config.capacity / (row_sum_pre + config.scale_epsilon))
        B_projected = B_unprojected * np.minimum.outer(scale, scale)
        np.fill_diagonal(B_projected, 0.0)
        correction_norm = float(np.linalg.norm(B_projected - B_unprojected))
    
    projection_active = bool(correction_norm > FROZEN_PROJECTION_NORM_TOL)
    relative_state = correction_norm / max(
        float(np.linalg.norm(B_unprojected)), FROZEN_ZERO_TOL
    )
    relative_update = correction_norm / max(proposed_update_norm, FROZEN_ZERO_TOL)
    
    # Validate projection
    state.B = B_projected
    row_sum = np.sum(state.B, axis=1)
    g_min = float(np.min(config.a - config.q * row_sum))
    # Recommended #4: Use named constant FROZEN_GAP_TOL
    if g_min < config.delta - FROZEN_GAP_TOL:
        raise RuntimeError(f"Gap projection failed: g_min={g_min}")
    
    # Update theta
    delayed = state.history[0]
    omega_arr = get_omega_array(config.omega)
    coupling = np.sum(
        state.B * np.sin(delayed[None, :] - state.theta[:, None]), axis=1
    )
    state.theta = np.mod(
        state.theta + config.dt * (omega_arr + coupling), 
        2.0 * np.pi
    )
    
    # Update history
    state.history.append(state.theta.copy())
    if len(state.history) > config.delay_steps + 1:
        state.history.pop(0)
    
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


def simulate_prefix(
    seed: int,
    config: ModelConfig,
    protocol: ProtocolConfig,
) -> tuple[DynamicState, dict[str, Any]]:
    """Simulate prefix up to split_time.
    
    Exact reproduction of production simulate_prefix().
    Returns (state, prefix_dict).
    
    Production uses:
        root = SeedSequence(seed)
        init_sequence, _ = root.spawn(2)
        rng = default_rng(init_sequence)  # for initialization
        
        Then in the loop, uses:
        unused_rng = default_rng(0)  # for advance_state when shuffle_driver=False
    """
    N = config.N
    edges = compute_edges(N)
    
    # Initialize state (uses init_sequence via make_prefix_rng)
    state = initialize_state(seed, config)
    
    # Get RNG for prefix simulation loop
    # Production uses unused_rng = default_rng(0) for the advance_state calls
    # when shuffle_driver=False
    unused_rng = np.random.default_rng(0)
    
    # Simulate to split point
    R_past_sum = np.zeros((N, N), dtype=float)
    R_past_count = 0
    
    burn_end = protocol.burn_end(config)
    hist_end = protocol.hist_end(config)
    
    for step in range(hist_end):
        R_physical, _, _ = advance_state(state, config, unused_rng, shuffle_driver=False)
        
        # P1 #10-11: State validation at transition boundaries
        if step == burn_end or step == hist_end - 1:
            state.validate(config, step)
        
        if burn_end <= step < hist_end:
            R_past_sum += R_physical
            R_past_count += 1
    
    prefix = {
        "B_at_split": state.B.copy(),
        "R_physical_past": R_past_sum / R_past_count if R_past_count > 0 else np.zeros((N, N)),
        "theta_at_split": state.theta.copy(),
        "coherence_acc_at_split": state.coherence_acc.copy(),
        "history_at_split": np.stack(state.history),
        "selected_at_split": (state.B > config.B_c).astype(np.uint8),
    }
    
    return state, prefix


def apply_intervention(
    state: DynamicState,
    branch: str,
    config: ModelConfig,
    rng: np.random.Generator,
) -> None:
    """Apply intervention to state. Mutates in place.
    
    Exact reproduction of production apply_intervention().
    """
    # Validate branch is known
    if branch not in KNOWN_BRANCHES:
        raise ValueError(f"Unknown branch '{branch}'. Known branches: {sorted(KNOWN_BRANCHES)}")
    
    N = state.N
    
    if branch in {"reset_ema", "reset_B_ema", "B_carrier_only", "full_reset"}:
        # Zero coherence accumulator
        state.coherence_acc.fill(0.0)
    
    if branch in {"reset_B", "reset_B_ema", "full_reset"}:
        # Zero B
        state.B.fill(0.0)
    
    if branch in {"B_carrier_only", "full_reset"}:
        # Randomize theta and history
        new_theta = rng.random(N) * 2.0 * np.pi
        state.theta = new_theta
        state.history = [new_theta.copy() for _ in range(config.delay_steps + 1)]
    
    # Ensure symmetry
    state.B = 0.5 * (state.B + state.B.T)
    np.fill_diagonal(state.B, 0.0)


def simulate_future(
    split_state: DynamicState,
    prefix: dict[str, Any],
    branch: str,
    config: ModelConfig,
    protocol: ProtocolConfig,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Simulate future trajectory from split state.
    
    Reproduces production simulate_future() with ALL required outputs.
    
    CRITICAL: Now accumulates BOTH horizon systems:
    
    Fixed Physical Horizons (time-based, NOT T_window dependent):
    - immediate: 0 to 17.5 time units
    - recovery: 17.5 to 87.5 time units  
    - late: 87.5 to 320 time units
    
    EMA-Normalized Horizons (T_window dependent):
    - immediate: 0 to 1*T_window
    - recovery: 1*T_window to 5*T_window
    - late: 5*T_window to end
    
    At rho=1 (T_window=17.502917...), the fixed physical and normalized horizons
    are approximately aligned but use exact step boundaries.
    
    Production accumulates:
    - P_full, P_immediate, P_recovery, P_late (incidence matrices)
    - B_mean_full, B_mean_immediate, B_mean_recovery, B_mean_late
    - R_physical_future, R_driver_future
    - Projection diagnostics via ProjectionTotals
    - Various scalar metrics
    
    Uses horizon system from production for normalized:
    - WINDOW_STEPS = round(T_window / dt)
    - RECOVERY_END = min(5 * WINDOW_STEPS, FUTURE_STEPS)
    
    For fixed physical:
    - FIXED_IMMEDIATE_END = round(17.5 / dt)
    - FIXED_RECOVERY_END = round(87.5 / dt)
    """
    state = split_state.clone()
    apply_intervention(state, branch, config, rng)
    
    N = state.N
    edges = compute_edges(N)
    future_steps = protocol.future_steps(config)
    
    # Compute horizon step boundaries
    # Normalized EMA horizons (T_window dependent)
    window_steps = int(round(config.T_window / config.dt))
    recovery_end_ema = min(5 * window_steps, future_steps)
    
    # Fixed physical horizons (NOT T_window dependent)
    # These use the production's physical time boundaries: 17.5, 87.5, 320
    fixed_immediate_end = int(round(17.5 / config.dt))   # 17.5 time units
    fixed_recovery_end = int(round(87.5 / config.dt))    # 87.5 time units
    # Late goes from 87.5 to end (320 time units)
    
    # Clamp all boundaries to future_steps
    recovery_end_ema = min(recovery_end_ema, future_steps)
    fixed_immediate_end = min(fixed_immediate_end, future_steps)
    fixed_recovery_end = min(fixed_recovery_end, future_steps)
    
    # Initialize accumulators for BOTH horizon systems
    # P matrices (incidence: B > B_c as 0/1)
    P_sums_ema = {
        "full": np.zeros((N, N), dtype=float),
        "immediate": np.zeros((N, N), dtype=float),
        "recovery": np.zeros((N, N), dtype=float),
        "late": np.zeros((N, N), dtype=float),
    }
    P_sums_fixed = {
        "full": np.zeros((N, N), dtype=float),
        "immediate": np.zeros((N, N), dtype=float),
        "recovery": np.zeros((N, N), dtype=float),
        "late": np.zeros((N, N), dtype=float),
    }
    
    # B matrices (mean B values)
    B_sums_ema = {
        "full": np.zeros((N, N), dtype=float),
        "immediate": np.zeros((N, N), dtype=float),
        "recovery": np.zeros((N, N), dtype=float),
        "late": np.zeros((N, N), dtype=float),
    }
    B_sums_fixed = {
        "full": np.zeros((N, N), dtype=float),
        "immediate": np.zeros((N, N), dtype=float),
        "recovery": np.zeros((N, N), dtype=float),
        "late": np.zeros((N, N), dtype=float),
    }
    
    # Counts for each horizon in both systems
    counts_ema = {"full": 0, "immediate": 0, "recovery": 0, "late": 0}
    counts_fixed = {"full": 0, "immediate": 0, "recovery": 0, "late": 0}
    
    # R matrices
    R_physical_sum = np.zeros((N, N), dtype=float)
    R_driver_sum = np.zeros((N, N), dtype=float)
    
    # Projection accumulator (matching production)
    projection = ProjectionTotals()
    
    # Trajectory accumulators
    sample_times = []
    density_trajectory = []
    similarity_trajectory = []
    
    # For retention/emergence calculations
    r_sum = 0.0
    r_count = 0
    r_late_ema_sum = 0.0
    r_late_ema_count = 0
    r_late_fixed_sum = 0.0
    r_late_fixed_count = 0
    
    B_reference = prefix["B_at_split"]
    shuffle_driver = (branch == "future_shuffle")
    
    for step in range(future_steps):
        R_physical, R_driver, info = advance_state(
            state, config, rng, shuffle_driver=shuffle_driver
        )
        
        # Update projection accumulator
        projection.update(info)
        
        # P1 #10-11: State validation at transition boundaries
        if step == 0 or step == window_steps or step == recovery_end_ema or step == fixed_immediate_end or step == fixed_recovery_end:
            state.validate(config, step)
        
        # Accumulate R matrices
        R_physical_sum += R_physical
        R_driver_sum += R_driver
        
        # Determine which horizons this step belongs to for BOTH systems
        selected = (state.B > config.B_c).astype(float)
        
        # === EMA-Normalized Horizons ===
        # Full: all steps
        P_sums_ema["full"] += selected
        B_sums_ema["full"] += state.B
        counts_ema["full"] += 1
        
        # immediate: 0 to window_steps (exclusive)
        if step < window_steps:
            P_sums_ema["immediate"] += selected
            B_sums_ema["immediate"] += state.B
            counts_ema["immediate"] += 1
        
        # recovery: window_steps to recovery_end_ema (exclusive)
        if window_steps <= step < recovery_end_ema:
            P_sums_ema["recovery"] += selected
            B_sums_ema["recovery"] += state.B
            counts_ema["recovery"] += 1
        
        # late: recovery_end_ema to end
        if recovery_end_ema <= step:
            P_sums_ema["late"] += selected
            B_sums_ema["late"] += state.B
            counts_ema["late"] += 1
        
        # === Fixed Physical Horizons ===
        # Full: all steps (same as EMA)
        P_sums_fixed["full"] += selected
        B_sums_fixed["full"] += state.B
        counts_fixed["full"] += 1
        
        # immediate: 0 to fixed_immediate_end (exclusive)
        if step < fixed_immediate_end:
            P_sums_fixed["immediate"] += selected
            B_sums_fixed["immediate"] += state.B
            counts_fixed["immediate"] += 1
        
        # recovery: fixed_immediate_end to fixed_recovery_end (exclusive)
        if fixed_immediate_end <= step < fixed_recovery_end:
            P_sums_fixed["recovery"] += selected
            B_sums_fixed["recovery"] += state.B
            counts_fixed["recovery"] += 1
        
        # late: fixed_recovery_end to end
        if fixed_recovery_end <= step:
            P_sums_fixed["late"] += selected
            B_sums_fixed["late"] += state.B
            counts_fixed["late"] += 1
        
        # Trajectory sampling - CRITICAL: r_mean_late is ONLY accumulated here
        if step % protocol.diagnostic_stride == 0:
            t = (step + 1) * config.dt
            sample_times.append(t)
            
            # Density: fraction of edges above B_c
            density = float(np.count_nonzero(state.B[edges] > config.B_c) / len(edges[0]))
            density_trajectory.append(density)
            
            # Similarity: cosine between current and reference B
            B_vec = state.B[edges]
            B_ref_vec = B_reference[edges]
            norm_B = np.linalg.norm(B_vec)
            norm_ref = np.linalg.norm(B_ref_vec)
            if norm_B > 0 and norm_ref > 0:
                similarity = float(np.dot(B_vec, B_ref_vec) / (norm_B * norm_ref))
            else:
                similarity = float('nan')
            similarity_trajectory.append(similarity)
            
            # Track overall r
            r_value = float(np.abs(np.mean(np.exp(1j * state.theta))))
            r_sum += r_value
            r_count += 1
            
            # Track late-phase r for BOTH horizon systems
            if recovery_end_ema <= step:
                r_late_ema_sum += r_value
                r_late_ema_count += 1
            
            if fixed_recovery_end <= step:
                r_late_fixed_sum += r_value
                r_late_fixed_count += 1
    
    # Compute mean matrices for BOTH horizon systems
    P_ema = {name: P_sums_ema[name] / counts_ema[name] if counts_ema[name] > 0 else np.zeros((N, N)) 
             for name in ["full", "immediate", "recovery", "late"]}
    P_fixed = {name: P_sums_fixed[name] / counts_fixed[name] if counts_fixed[name] > 0 else np.zeros((N, N))
               for name in ["full", "immediate", "recovery", "late"]}
    
    B_mean_ema = {name: B_sums_ema[name] / counts_ema[name] if counts_ema[name] > 0 else np.zeros((N, N))
                  for name in ["full", "immediate", "recovery", "late"]}
    B_mean_fixed = {name: B_sums_fixed[name] / counts_fixed[name] if counts_fixed[name] > 0 else np.zeros((N, N))
                    for name in ["full", "immediate", "recovery", "late"]}
    
    # Compute R means
    R_physical_mean = R_physical_sum / future_steps if future_steps > 0 else np.zeros((N, N))
    R_driver_mean = R_driver_sum / future_steps if future_steps > 0 else np.zeros((N, N))
    
    # Final state
    B_final = state.B.copy()
    final_weights = state.B[edges]
    final_rows = np.sum(state.B, axis=1)
    
    # Retention and emergence for BOTH horizon systems
    split_selected = prefix["selected_at_split"][edges].astype(bool)
    
    # EMA-normalized
    p_late_edges_ema = P_ema["late"][edges]
    retention_ema = (
        float(np.mean(p_late_edges_ema[split_selected]))
        if np.any(split_selected)
        else float('nan')
    )
    emergence_ema = (
        float(np.mean(p_late_edges_ema[~split_selected]))
        if np.any(~split_selected)
        else float('nan')
    )
    
    # Fixed physical
    p_late_edges_fixed = P_fixed["late"][edges]
    retention_fixed = (
        float(np.mean(p_late_edges_fixed[split_selected]))
        if np.any(split_selected)
        else float('nan')
    )
    emergence_fixed = (
        float(np.mean(p_late_edges_fixed[~split_selected]))
        if np.any(~split_selected)
        else float('nan')
    )
    
    # Minimum similarity from trajectory
    similarity_array = np.array(similarity_trajectory, dtype=float)
    finite_similarity = similarity_array[np.isfinite(similarity_array)]
    minimum_similarity = (
        float(np.min(finite_similarity)) if len(finite_similarity) > 0
        else float('nan')
    )
    
    # Build result with BOTH horizon systems
    result = {
        # === Matrix outputs for EMA-normalized horizons (backward compatible) ===
        "B_final": B_final,
        "B_mean_late": B_mean_ema["late"],
        "P_full": P_ema["full"],
        "P_immediate": P_ema["immediate"],
        "P_recovery": P_ema["recovery"],
        "P_late": P_ema["late"],
        "R_physical_future": R_physical_mean,
        "R_driver_future": R_driver_mean,
        
        # === Matrix outputs for FIXED-PHYSICAL horizons (NEW) ===
        "B_mean_late_fixed_physical": B_mean_fixed["late"],
        "P_full_fixed_physical": P_fixed["full"],
        "P_immediate_fixed_physical": P_fixed["immediate"],
        "P_recovery_fixed_physical": P_fixed["recovery"],
        "P_late_fixed_physical": P_fixed["late"],
        
        # === Matrix outputs for NORMALIZED-EMA horizons (NEW - explicit) ===
        "B_mean_late_normalized_EMA": B_mean_ema["late"],
        "P_full_normalized_EMA": P_ema["full"],
        "P_immediate_normalized_EMA": P_ema["immediate"],
        "P_recovery_normalized_EMA": P_ema["recovery"],
        "P_late_normalized_EMA": P_ema["late"],
        
        # Trajectory outputs
        "sample_times": np.array(sample_times, dtype=float),
        "density_trajectory": np.array(density_trajectory, dtype=float),
        "similarity_trajectory": np.array(similarity_trajectory, dtype=float),
        
        # Scalar outcomes - EMA-normalized (backward compatible names)
        "D_B_final": float(np.count_nonzero(final_weights > config.B_c) / len(edges[0])),
        "P_mean_full": float(np.mean(P_ema["full"][edges])),
        "P_mean_immediate": float(np.mean(P_ema["immediate"][edges])),
        "P_mean_recovery": float(np.mean(P_ema["recovery"][edges])),
        "P_mean_late": float(np.mean(P_ema["late"][edges])),
        
        # Scalar outcomes - FIXED-PHYSICAL (NEW - primary estimands)
        "P_mean_full_fixed_physical": float(np.mean(P_fixed["full"][edges])),
        "P_mean_immediate_fixed_physical": float(np.mean(P_fixed["immediate"][edges])),
        "P_mean_recovery_fixed_physical": float(np.mean(P_fixed["recovery"][edges])),
        "P_mean_late_fixed_physical": float(np.mean(P_fixed["late"][edges])),
        
        # Scalar outcomes - NORMALIZED-EMA (NEW - explicit)
        "P_mean_full_normalized_EMA": float(np.mean(P_ema["full"][edges])),
        "P_mean_immediate_normalized_EMA": float(np.mean(P_ema["immediate"][edges])),
        "P_mean_recovery_normalized_EMA": float(np.mean(P_ema["recovery"][edges])),
        "P_mean_late_normalized_EMA": float(np.mean(P_ema["late"][edges])),
        
        # Similarity metrics - BOTH systems
        "Weighted_similarity_final": cosine_edges(B_reference, B_final, edges),
        "Weighted_similarity_late": cosine_edges(B_reference, B_mean_ema["late"], edges),
        "Weighted_similarity_late_fixed_physical": cosine_edges(B_reference, B_mean_fixed["late"], edges),
        "Weighted_similarity_late_normalized_EMA": cosine_edges(B_reference, B_mean_ema["late"], edges),
        "Jaccard_final": jaccard_edges(B_reference, B_final, edges, config.B_c),
        "Jaccard_final_fixed_physical": jaccard_edges(B_reference, B_final, edges, config.B_c),
        
        # Retention/emergence - BOTH systems
        "Retention_selected_late": retention_ema,
        "Emergence_unselected_late": emergence_ema,
        "Retention_contrast_late": retention_ema - emergence_ema,
        "Retention_selected_late_fixed_physical": retention_fixed,
        "Emergence_unselected_late_fixed_physical": emergence_fixed,
        "Retention_contrast_late_fixed_physical": retention_fixed - emergence_fixed,
        "Retention_selected_late_normalized_EMA": retention_ema,
        "Emergence_unselected_late_normalized_EMA": emergence_ema,
        "Retention_contrast_late_normalized_EMA": retention_ema - emergence_ema,
        
        # Correlations with past R - BOTH systems
        "Corr_Rpast_Pfull": safe_corr(prefix["R_physical_past"][edges], P_ema["full"][edges]),
        "Corr_Rpast_Plate": safe_corr(prefix["R_physical_past"][edges], P_ema["late"][edges]),
        "Corr_Rpast_Pfull_fixed_physical": safe_corr(prefix["R_physical_past"][edges], P_fixed["full"][edges]),
        "Corr_Rpast_Plate_fixed_physical": safe_corr(prefix["R_physical_past"][edges], P_fixed["late"][edges]),
        "Corr_Rpast_Pfull_normalized_EMA": safe_corr(prefix["R_physical_past"][edges], P_ema["full"][edges]),
        "Corr_Rpast_Plate_normalized_EMA": safe_corr(prefix["R_physical_past"][edges], P_ema["late"][edges]),
        
        # Weight statistics (same for both - based on final state)
        "Total_edge_weight": float(np.sum(final_weights)),
        "Mean_row_sum": float(np.mean(final_rows)),
        "Max_row_sum": float(np.max(final_rows)),
        "Nonzero_edge_fraction": float(np.mean(final_weights > config.scale_epsilon)),
        "Effective_edges": effective_number(final_weights),
        "Weight_gini": gini_coefficient(final_weights),
        "Weight_entropy": normalized_entropy(final_weights),
        
        # Order parameter - BOTH systems
        "r_mean_future": float(r_sum / r_count) if r_count > 0 else float('nan'),
        "r_mean_late": float(r_late_ema_sum / r_late_ema_count) if r_late_ema_count > 0 else float('nan'),
        "r_mean_late_fixed_physical": float(r_late_fixed_sum / r_late_fixed_count) if r_late_fixed_count > 0 else float('nan'),
        "r_mean_late_normalized_EMA": float(r_late_ema_sum / r_late_ema_count) if r_late_ema_count > 0 else float('nan'),
        
        # Minimum similarity
        "Minimum_similarity": minimum_similarity,
        
        # Projection diagnostics (from ProjectionTotals)
        **projection.metrics(),
        
        # Horizon metadata
        "window_steps": window_steps,
        "recovery_end_ema": recovery_end_ema,
        "fixed_immediate_end": fixed_immediate_end,
        "fixed_recovery_end": fixed_recovery_end,
    }
    
    return result


# =============================================================================
# Metric Helpers
# =============================================================================

def cosine_edges(reference: np.ndarray, current: np.ndarray, edges: tuple[np.ndarray, np.ndarray] | None = None) -> float:
    """Compute cosine similarity between reference and current B matrices over edges.
    
    If edges is None, computes over all upper triangle edges.
    """
    if edges is None:
        N = reference.shape[0]
        edges = compute_edges(N)
    
    x = np.asarray(reference[edges], dtype=float)
    y = np.asarray(current[edges], dtype=float)
    denominator = float(np.linalg.norm(x) * np.linalg.norm(y))
    if denominator <= 1e-12:
        return float('nan')
    return float(np.dot(x, y) / denominator)


def jaccard_edges(reference: np.ndarray, current: np.ndarray, edges: tuple[np.ndarray, np.ndarray] | None = None, threshold: float = FROZEN_ZERO_TOL) -> float:
    """Compute Jaccard similarity between reference and current B matrices over edges.
    
    Uses B > threshold as the threshold for edge presence.
    If edges is None, computes over all upper triangle edges.
    
    Matches production: jaccard_edges(B_reference, state.B) uses B > B_C
    """
    if edges is None:
        N = reference.shape[0]
        edges = compute_edges(N)
    
    x = reference[edges] > threshold
    y = current[edges] > threshold
    union = np.count_nonzero(x | y)
    if union == 0:
        return float('nan')
    return float(np.count_nonzero(x & y) / union)


def safe_corr(x: np.ndarray, y: np.ndarray) -> float:
    """Compute correlation coefficient safely."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    x = x[valid]
    y = y[valid]
    if len(x) < 3 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return float('nan')
    return float(np.corrcoef(x, y)[0, 1])


def effective_number(weights: np.ndarray) -> float:
    """Compute effective number of edges."""
    weights = np.asarray(weights, dtype=float)
    total = float(np.sum(weights))
    sum_sq = float(np.sum(weights**2))
    if total <= 1e-12 or sum_sq <= 1e-12:
        return 0.0
    return total**2 / sum_sq


def gini_coefficient(weights: np.ndarray) -> float:
    """Compute Gini coefficient."""
    x = np.sort(np.asarray(weights, dtype=float))
    total = float(np.sum(x))
    if total <= 1e-12:
        return 0.0
    n = len(x)
    ranks = np.arange(1, n + 1, dtype=float)
    return float(2.0 * np.dot(ranks, x) / (n * total) - (n + 1.0) / n)


def normalized_entropy(weights: np.ndarray) -> float:
    """Compute normalized entropy."""
    weights = np.asarray(weights, dtype=float)
    total = float(np.sum(weights))
    if total <= 1e-12:
        return 0.0
    probabilities = weights / total
    positive = probabilities > 0.0
    entropy = -float(np.sum(probabilities[positive] * np.log(probabilities[positive])))
    return entropy / float(np.log(len(weights)))


def time_to_at_least(
    sample_times: np.ndarray,
    values: np.ndarray,
    target: float,
) -> float:
    """Find the first time at which values reach at least the target.
    
    Matches frozen production exactly.
    Returns NaN if target is never reached.
    """
    sample_times = np.asarray(sample_times, dtype=float)
    values = np.asarray(values, dtype=float)
    valid = np.isfinite(values)
    indices = np.flatnonzero(valid & (values >= target))
    return float(sample_times[indices[0]]) if len(indices) > 0 else float('nan')


def time_to_below(
    sample_times: np.ndarray,
    values: np.ndarray,
    threshold: float,
) -> float:
    """Find the first time at which values drop below the threshold.
    
    Matches frozen production exactly.
    Returns NaN if threshold is never dropped below.
    """
    sample_times = np.asarray(sample_times, dtype=float)
    values = np.asarray(values, dtype=float)
    valid = np.isfinite(values)
    indices = np.flatnonzero(valid & (values < threshold))
    return float(sample_times[indices[0]]) if len(indices) > 0 else float('nan')


def finalize_historical_branch_metrics(
    branch_results: dict[str, dict[str, Any]],
) -> None:
    """Compute and add the 8 historical scalar fields that compare branches to continue.
    
    These fields are computed in frozen production by run_seed() after all branches
    are simulated. They must be computed here to match the frozen schema.
    
    The 8 fields are:
    - Time_to_50pct_continue_final_density
    - Time_to_90pct_continue_final_density
    - Time_to_50pct_continue_late_similarity
    - Time_to_90pct_continue_late_similarity
    - Time_to_similarity_below_0_9
    - Time_to_similarity_below_0_5
    - Late_persistence_ratio_to_continue
    - Late_similarity_ratio_to_continue
    
    These are computed for each branch relative to the continue branch reference values.
    """
    # Get continue branch results for reference
    if "continue" not in branch_results:
        raise RuntimeError("continue branch is required for historical metric computation")
    
    continue_result = branch_results["continue"]
    
    # Get reference values from continue branch
    reference_density = float(continue_result["D_B_final"])
    reference_late_similarity = float(continue_result["Weighted_similarity_late"])
    reference_late_persistence = float(continue_result["P_mean_late"])
    
    for branch, result in branch_results.items():
        # Use direct indexing to fail if keys are missing
        times = result["sample_times"]
        density = result["density_trajectory"]
        similarity = result["similarity_trajectory"]
        
        # Compute time-based metrics relative to continue branch reference
        
        # Compute time-based metrics relative to continue branch reference
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
        
        # Compute ratio metrics - use direct indexing to fail if missing
        branch_late_persistence = float(result["P_mean_late"])
        branch_late_similarity = float(result["Weighted_similarity_late"])
        
        # P0 #8: Restore literal frozen persistence-ratio logic
        # Frozen production uses: if abs(reference_late_persistence) > ZERO_TOL
        # NOT: if np.isfinite(reference_late_persistence) and abs(...) > ZERO_TOL
        # For persistence ratio, use the exact frozen condition
        if abs(reference_late_persistence) > FROZEN_ZERO_TOL:
            result["Late_persistence_ratio_to_continue"] = (
                branch_late_persistence / reference_late_persistence
            )
        else:
            result["Late_persistence_ratio_to_continue"] = float('nan')
        
        # For similarity ratio, keep the np.isfinite() check as frozen source uses it there
        if np.isfinite(reference_late_similarity) and abs(reference_late_similarity) > FROZEN_ZERO_TOL:
            result["Late_similarity_ratio_to_continue"] = (
                branch_late_similarity / reference_late_similarity
            )
        else:
            result["Late_similarity_ratio_to_continue"] = float('nan')


# =============================================================================
# Required Output Schema for Baseline Equivalence
# =============================================================================
# 
# IMPORTANT: We separate FROZEN keys (must exist in historical NPZ) from
# EXTENDED keys (new in v1, only validated internally at rho=1).
#
# The frozen NPZ does NOT contain dual-horizon keys, so baseline equivalence
# must only check FROZEN keys against historical data.

# Required prefix keys for baseline equivalence
REQUIRED_PREFIX_KEYS = (
    "B_at_split",
    "R_physical_past",
    "theta_at_split",
    "coherence_acc_at_split",
    "history_at_split",
    "selected_at_split",
)

# These are the keys that MUST exist in the frozen NPZ for baseline equivalence
FROZEN_BRANCH_MATRIX_KEYS = (
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

# These are the NEW keys introduced in v1 for dual-horizon support
# They will NOT exist in frozen NPZ, so baseline equivalence skips them
EXTENDED_BRANCH_MATRIX_KEYS = (
    "B_mean_late_fixed_physical",
    "P_full_fixed_physical",
    "P_immediate_fixed_physical",
    "P_recovery_fixed_physical",
    "P_late_fixed_physical",
    "B_mean_late_normalized_EMA",
    "P_full_normalized_EMA",
    "P_immediate_normalized_EMA",
    "P_recovery_normalized_EMA",
    "P_late_normalized_EMA",
)

# Extended matrix equivalence map for internal consistency validation at rho=1
# Maps extended matrix keys to their frozen equivalents
EXTENDED_MATRIX_EQUIVALENCE_MAP = {
    "B_mean_late_fixed_physical": "B_mean_late",
    "P_full_fixed_physical": "P_full",
    "P_immediate_fixed_physical": "P_immediate",
    "P_recovery_fixed_physical": "P_recovery",
    "P_late_fixed_physical": "P_late",
    "B_mean_late_normalized_EMA": "B_mean_late",
    "P_full_normalized_EMA": "P_full",
    "P_immediate_normalized_EMA": "P_immediate",
    "P_recovery_normalized_EMA": "P_recovery",
    "P_late_normalized_EMA": "P_late",
}

# All matrix keys (frozen + extended)
REQUIRED_BRANCH_MATRIX_KEYS = FROZEN_BRANCH_MATRIX_KEYS + EXTENDED_BRANCH_MATRIX_KEYS

# P0 #7: Matrix schema-map integrity should mirror scalar integrity
# Validate no duplicates in extended matrix keys
if len(EXTENDED_BRANCH_MATRIX_KEYS) != len(set(EXTENDED_BRANCH_MATRIX_KEYS)):
    duplicates = [k for k in EXTENDED_BRANCH_MATRIX_KEYS if list(EXTENDED_BRANCH_MATRIX_KEYS).count(k) > 1]
    raise RuntimeError(f"Duplicate extended matrix schema keys: {sorted(set(duplicates))}")

# Validate matrix map consistency
if set(EXTENDED_BRANCH_MATRIX_KEYS) != set(EXTENDED_MATRIX_EQUIVALENCE_MAP.keys()):
    missing_map = set(EXTENDED_BRANCH_MATRIX_KEYS) - set(EXTENDED_MATRIX_EQUIVALENCE_MAP.keys())
    extra_map = set(EXTENDED_MATRIX_EQUIVALENCE_MAP.keys()) - set(EXTENDED_BRANCH_MATRIX_KEYS)
    raise RuntimeError(
        f"Extended matrix map mismatch: "
        f"missing={sorted(missing_map)}, extra={sorted(extra_map)}"
    )

# FROZEN BRANCH SCALAR KEYS: All 42 historical fields from frozen production
# These MUST exist in the frozen CSV and are validated against it
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
    # Historical cross-branch time-based metrics (from frozen production)
    "Time_to_50pct_continue_final_density",
    "Time_to_90pct_continue_final_density",
    "Time_to_50pct_continue_late_similarity",
    "Time_to_90pct_continue_late_similarity",
    "Time_to_similarity_below_0_9",
    "Time_to_similarity_below_0_5",
    "Late_persistence_ratio_to_continue",
    "Late_similarity_ratio_to_continue",
)

# EXTENDED BRANCH SCALAR KEYS: New fields in v1 for dual-horizon support
# These do NOT exist in frozen CSV/NPZ, so are validated internally at rho=1
EXTENDED_BRANCH_SCALAR_KEYS = (
    # Fixed physical horizon scalars (PRIMARY ESTIMANDS)
    "P_mean_late_fixed_physical",
    "Weighted_similarity_late_fixed_physical",
    "Retention_contrast_late_fixed_physical",
    "Corr_Rpast_Plate_fixed_physical",
    "r_mean_late_fixed_physical",
    # Normalized EMA horizon scalars (NEW - explicit)
    "P_mean_late_normalized_EMA",
    "Weighted_similarity_late_normalized_EMA",
    "Retention_contrast_late_normalized_EMA",
    "Corr_Rpast_Plate_normalized_EMA",
    "r_mean_late_normalized_EMA",
    # Additional extended scalars for complete coverage
    "P_mean_full_fixed_physical",
    "P_mean_immediate_fixed_physical",
    "P_mean_recovery_fixed_physical",
    "P_mean_full_normalized_EMA",
    "P_mean_immediate_normalized_EMA",
    "P_mean_recovery_normalized_EMA",
    "Retention_selected_late_fixed_physical",
    "Emergence_unselected_late_fixed_physical",
    "Retention_selected_late_normalized_EMA",
    "Emergence_unselected_late_normalized_EMA",
    "Corr_Rpast_Pfull_fixed_physical",
    "Corr_Rpast_Pfull_normalized_EMA",
    "Jaccard_final_fixed_physical",
)

# Extended scalar equivalence map for internal consistency validation at rho=1
# Maps extended keys to their frozen equivalents
EXTENDED_SCALAR_EQUIVALENCE_MAP = {
    "P_mean_full_fixed_physical": "P_mean_full",
    "P_mean_immediate_fixed_physical": "P_mean_immediate",
    "P_mean_recovery_fixed_physical": "P_mean_recovery",
    "P_mean_late_fixed_physical": "P_mean_late",
    "P_mean_full_normalized_EMA": "P_mean_full",
    "P_mean_immediate_normalized_EMA": "P_mean_immediate",
    "P_mean_recovery_normalized_EMA": "P_mean_recovery",
    "P_mean_late_normalized_EMA": "P_mean_late",
    "Weighted_similarity_late_fixed_physical": "Weighted_similarity_late",
    "Weighted_similarity_late_normalized_EMA": "Weighted_similarity_late",
    "Retention_contrast_late_fixed_physical": "Retention_contrast_late",
    "Retention_contrast_late_normalized_EMA": "Retention_contrast_late",
    "Corr_Rpast_Plate_fixed_physical": "Corr_Rpast_Plate",
    "Corr_Rpast_Plate_normalized_EMA": "Corr_Rpast_Plate",
    "Corr_Rpast_Pfull_fixed_physical": "Corr_Rpast_Pfull",
    "Corr_Rpast_Pfull_normalized_EMA": "Corr_Rpast_Pfull",
    "r_mean_late_fixed_physical": "r_mean_late",
    "r_mean_late_normalized_EMA": "r_mean_late",
    "Retention_selected_late_fixed_physical": "Retention_selected_late",
    "Retention_selected_late_normalized_EMA": "Retention_selected_late",
    "Emergence_unselected_late_fixed_physical": "Emergence_unselected_late",
    "Emergence_unselected_late_normalized_EMA": "Emergence_unselected_late",
    "Jaccard_final_fixed_physical": "Jaccard_final",
}

# Validate no duplicates in extended scalar keys
if len(EXTENDED_BRANCH_SCALAR_KEYS) != len(set(EXTENDED_BRANCH_SCALAR_KEYS)):
    duplicates = [k for k in EXTENDED_BRANCH_SCALAR_KEYS if list(EXTENDED_BRANCH_SCALAR_KEYS).count(k) > 1]
    raise RuntimeError(f"Duplicate extended scalar schema keys: {sorted(set(duplicates))}")

# Validate schema-map consistency
if set(EXTENDED_BRANCH_SCALAR_KEYS) != set(EXTENDED_SCALAR_EQUIVALENCE_MAP.keys()):
    missing_map = set(EXTENDED_BRANCH_SCALAR_KEYS) - set(EXTENDED_SCALAR_EQUIVALENCE_MAP.keys())
    extra_map = set(EXTENDED_SCALAR_EQUIVALENCE_MAP.keys()) - set(EXTENDED_BRANCH_SCALAR_KEYS)
    raise RuntimeError(
        f"Extended scalar map mismatch: "
        f"missing mappings={sorted(missing_map)}, extra mappings={sorted(extra_map)}"
    )

# All required scalar keys (frozen + extended)
REQUIRED_BRANCH_SCALAR_KEYS = FROZEN_BRANCH_SCALAR_KEYS + EXTENDED_BRANCH_SCALAR_KEYS


# =============================================================================
# Baseline Equivalence Test
# =============================================================================

def exact_array_equal_with_nan(a: np.ndarray, b: np.ndarray) -> bool:
    """Compare arrays with NaN-aware exact equality."""
    a = np.asarray(a)
    b = np.asarray(b)
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    if np.issubdtype(a.dtype, np.floating) or np.issubdtype(a.dtype, np.complexfloating):
        a_nan = np.isnan(a)
        b_nan = np.isnan(b)
        if not np.array_equal(a_nan, b_nan):
            return False
        finite = ~a_nan
        return np.array_equal(a[finite], b[finite])
    return np.array_equal(a, b)


def run_baseline_equivalence(
    seeds: list[int],
    config: ModelConfig,
    protocol: ProtocolConfig,
    frozen_manifest_path: str,
    frozen_npz_path: str,
    branch_order: tuple[str, ...],
    frozen_csv_path: str | None = None,
) -> dict[str, Any]:
    """Run baseline equivalence test at rho=1 (T_window = T_*).
    
    MANDATORY: Must reproduce frozen run exactly for all seeds.
    
    This function validates that the engine produces EXACTLY the same outputs
    as the frozen production run for all required keys.
    
    Requires NaN-aware exact equality for ALL required schema keys:
    - All prefix keys
    - All branch matrix keys
    - All branch scalar keys
    
    Returns:
        status: "passed" | "failed" | "not_run"
        seed_results: per-seed validation details
        engine_source_sha256: hash of this engine source
        frozen_manifest_hash: hash of frozen manifest
        frozen_npz_hash: hash of frozen NPZ
    """
    import numpy as np
    from pathlib import Path
    import hashlib
    
    # Preflight validation: validate config and protocol before any simulation
    try:
        config.validate()
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Config validation failed: {e}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()) if frozen_manifest_path else None,
            "frozen_npz": str(Path(frozen_npz_path).resolve()) if frozen_npz_path else None,
            "frozen_csv_path": frozen_csv_path,
        }
    
    try:
        protocol.validate(config)
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Protocol validation failed: {e}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()) if frozen_manifest_path else None,
            "frozen_npz": str(Path(frozen_npz_path).resolve()) if frozen_npz_path else None,
            "frozen_csv_path": frozen_csv_path,
        }
    
    # Helper function to compute source hash
    def _source_sha256() -> str | None:
        try:
            return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        except (NameError, OSError):
            return None
    
    # P1 #6: Preflight all authority files - check existence before opening
    # Check frozen manifest exists
    if not os.path.isfile(frozen_manifest_path):
        return {
            "status": "failed",
            "error": f"Frozen manifest not found: {frozen_manifest_path}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()) if frozen_manifest_path else None,
            "frozen_npz": str(Path(frozen_npz_path).resolve()) if frozen_npz_path else None,
            "frozen_csv_path": frozen_csv_path,
        }
    
    # Check frozen NPZ exists
    if not os.path.isfile(frozen_npz_path):
        return {
            "status": "failed",
            "error": f"Frozen NPZ not found: {frozen_npz_path}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()) if frozen_manifest_path else None,
            "frozen_npz": str(Path(frozen_npz_path).resolve()) if frozen_npz_path else None,
            "frozen_csv_path": frozen_csv_path,
        }
    
    # Early failure: frozen scalar CSV is required for scalar equivalence
    if frozen_csv_path is None:
        return {
            "status": "failed",
            "error": "frozen scalar CSV is required for scalar equivalence",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": None,
        }
    
    # Check frozen CSV exists (if provided)
    if frozen_csv_path is not None and not os.path.isfile(frozen_csv_path):
        return {
            "status": "failed",
            "error": f"Frozen scalar CSV not found: {frozen_csv_path}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": frozen_csv_path,
        }
    
    # Record engine source hash
    engine_source_hash = _source_sha256()
    
    results = {
        "status": "not_run",
        "config": {
            "N": config.N,
            "dt": config.dt,
            "tau": config.tau,
            "mean_omega": config.mean_omega,
            "T_window": config.T_window,
            "T_star": config.T_star,
            "alpha": config.alpha,
            "a": config.a,
            "q": config.q,
            "delta": config.delta,
            "eta": config.eta,
            "mu": config.mu,
            "gamma": config.gamma,
            "B_c": config.B_c,
            "B_init_scale": config.B_init_scale,
            "scale_epsilon": config.scale_epsilon,
            "capacity": config.capacity,
            "delay_steps": config.delay_steps,
        },
        "protocol": {
            "T_sim": protocol.T_sim,
            "burn_end_time": protocol.burn_end_time,
            "split_time": protocol.split_time,
            "future_duration": protocol.future_duration,
            "diagnostic_stride": protocol.diagnostic_stride,
            "branches": list(protocol.branches),
        },
        "n_seeds": len(seeds),
        "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
        "frozen_npz": str(Path(frozen_npz_path).resolve()),
        "engine_source_sha256": engine_source_hash,
        "seed_results": {},
    }
    
    # P0 #9: Catch malformed manifest - wrap in try/except
    try:
        # Load frozen manifest
        with open(frozen_manifest_path, "r") as f:
            frozen_manifest = json.load(f)
        
        # Validate required manifest structure before indexing
        if "randomization" not in frozen_manifest:
            return {
                "status": "failed",
                "error": "Frozen manifest missing 'randomization' section",
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        if "protocol" not in frozen_manifest:
            return {
                "status": "failed",
                "error": "Frozen manifest missing 'protocol' section",
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        if "model" not in frozen_manifest:
            return {
                "status": "failed",
                "error": "Frozen manifest missing 'model' section",
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        if "schema" not in frozen_manifest:
            return {
                "status": "failed",
                "error": "Frozen manifest missing 'schema' section",
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        
        if "paired_seeds" not in frozen_manifest["randomization"]:
            return {
                "status": "failed",
                "error": "Frozen manifest missing 'randomization.paired_seeds'",
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        if "branches" not in frozen_manifest["protocol"]:
            return {
                "status": "failed",
                "error": "Frozen manifest missing 'protocol.branches'",
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        
        # P0 #10: Compare manifest schema to expected frozen schema
        # Validate schema structure
        manifest_schema = frozen_manifest.get("schema", {})
        
        manifest_prefix = tuple(manifest_schema.get("prefix_keys", []))
        manifest_matrices = tuple(manifest_schema.get("branch_matrix_keys", []))
        manifest_scalars = tuple(manifest_schema.get("branch_scalar_keys", []))
        
        # Nonblocking #6: Check manifest schema uniqueness
        for schema_name, schema_values in (
            ("prefix_keys", manifest_prefix),
            ("branch_matrix_keys", manifest_matrices),
            ("branch_scalar_keys", manifest_scalars),
        ):
            if len(schema_values) != len(set(schema_values)):
                duplicates = [v for v in schema_values if list(schema_values).count(v) > 1]
                return {
                    "status": "failed",
                    "error": (
                        f"Frozen manifest schema "
                        f"{schema_name} contains duplicates: {sorted(set(duplicates))}"
                    ),
                    "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                    "frozen_npz": str(Path(frozen_npz_path).resolve()),
                    "frozen_csv_path": frozen_csv_path,
                }
        
        # Validate prefix keys
        if set(manifest_prefix) != set(REQUIRED_PREFIX_KEYS):
            missing_prefix = set(REQUIRED_PREFIX_KEYS) - set(manifest_prefix)
            extra_prefix = set(manifest_prefix) - set(REQUIRED_PREFIX_KEYS)
            return {
                "status": "failed",
                "error": (
                    f"Manifest prefix_keys mismatch: "
                    f"missing={sorted(missing_prefix)}, extra={sorted(extra_prefix)}"
                ),
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        
        # Validate matrix keys - compare unique sets
        if set(manifest_matrices) != set(FROZEN_BRANCH_MATRIX_KEYS):
            missing_matrices = set(FROZEN_BRANCH_MATRIX_KEYS) - set(manifest_matrices)
            extra_matrices = set(manifest_matrices) - set(FROZEN_BRANCH_MATRIX_KEYS)
            return {
                "status": "failed",
                "error": (
                    f"Manifest branch_matrix_keys mismatch: "
                    f"missing={sorted(missing_matrices)}, extra={sorted(extra_matrices)}"
                ),
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        
        # Validate scalar keys - compare unique sets
        if set(manifest_scalars) != set(FROZEN_BRANCH_SCALAR_KEYS):
            missing_scalars = set(FROZEN_BRANCH_SCALAR_KEYS) - set(manifest_scalars)
            extra_scalars = set(manifest_scalars) - set(FROZEN_BRANCH_SCALAR_KEYS)
            return {
                "status": "failed",
                "error": (
                    f"Manifest branch_scalar_keys mismatch: "
                    f"missing={sorted(missing_scalars)}, extra={sorted(extra_scalars)}"
                ),
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
    except (json.JSONDecodeError, OSError) as e:
        return {
            "status": "failed",
            "error": f"Malformed frozen manifest {frozen_manifest_path}: {e}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": frozen_csv_path,
        }
    
    # P0 #4: Validate seed/branch authority - seeds and branches must match manifest
    manifest_seeds = [int(x) for x in frozen_manifest["randomization"]["paired_seeds"]]
    manifest_branches = tuple(frozen_manifest["protocol"]["branches"])
    if list(seeds) != manifest_seeds:
        return {
            "status": "failed",
            "error": f"Seed authority mismatch: seeds={seeds}, manifest={manifest_seeds}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": frozen_csv_path,
        }
    if tuple(branch_order) != manifest_branches:
        return {
            "status": "failed",
            "error": f"Branch authority mismatch: branch_order={branch_order}, manifest={manifest_branches}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": frozen_csv_path,
        }
    
    # P0 #1: Validate protocol.branches matches manifest branches
    # This is critical: branch_order defines RNG namespace, but protocol.branches defines executed branches
    # Both must match the frozen manifest to prevent false-pass
    if tuple(protocol.branches) != manifest_branches:
        return {
            "status": "failed",
            "error": (
                "Executed baseline branch mismatch: "
                f"protocol.branches={protocol.branches}, "
                f"manifest={manifest_branches}"
            ),
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": frozen_csv_path,
        }
    
    # P0 #3: Validate baseline horizon metadata
    # At rho=1 (T_window = T_star), horizon metadata must match frozen values
    if math.isclose(config.T_window, config.T_star, rel_tol=0.0, abs_tol=0.0):
        expected_metadata = BASELINE_HORIZON_METADATA
        actual_window_steps = int(round(config.T_window / config.dt))
        actual_recovery_end_ema = min(5 * actual_window_steps, protocol.future_steps(config))
        actual_fixed_immediate_end = int(round(17.5 / config.dt))
        actual_fixed_recovery_end = int(round(87.5 / config.dt))
        
        if actual_window_steps != expected_metadata["window_steps"]:
            return {
                "status": "failed",
                "error": f"window_steps mismatch: actual={actual_window_steps}, expected={expected_metadata['window_steps']}",
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        if actual_recovery_end_ema != expected_metadata["recovery_end_ema"]:
            return {
                "status": "failed",
                "error": f"recovery_end_ema mismatch: actual={actual_recovery_end_ema}, expected={expected_metadata['recovery_end_ema']}",
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        if actual_fixed_immediate_end != expected_metadata["fixed_immediate_end"]:
            return {
                "status": "failed",
                "error": f"fixed_immediate_end mismatch: actual={actual_fixed_immediate_end}, expected={expected_metadata['fixed_immediate_end']}",
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
        if actual_fixed_recovery_end != expected_metadata["fixed_recovery_end"]:
            return {
                "status": "failed",
                "error": f"fixed_recovery_end mismatch: actual={actual_fixed_recovery_end}, expected={expected_metadata['fixed_recovery_end']}",
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
    
    # P0 #9: Catch malformed NPZ - wrap in try/except
    try:
        # Load frozen data
        with np.load(frozen_npz_path, allow_pickle=False) as frozen_data:
            frozen_files = dict(frozen_data)
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Malformed frozen NPZ {frozen_npz_path}: {e}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": frozen_csv_path,
        }
    
    # P1 #7: Preflight NPZ schema - validate expected keys exist
    # Check prefix keys for all seeds
    for seed in seeds:
        seed_str = str(seed)
        for key in REQUIRED_PREFIX_KEYS:
            frozen_key = f"prefix_seed_{seed_str}_{key}"
            if frozen_key not in frozen_files:
                return {
                    "status": "failed",
                    "error": f"Missing NPZ key: {frozen_key}",
                    "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                    "frozen_npz": str(Path(frozen_npz_path).resolve()),
                    "frozen_csv_path": frozen_csv_path,
                }
    
    # Check branch matrix keys for all seeds and branches
    for seed in seeds:
        seed_str = str(seed)
        for branch in branch_order:
            for key in FROZEN_BRANCH_MATRIX_KEYS:
                frozen_key = f"{branch}_seed_{seed_str}_{key}"
                if frozen_key not in frozen_files:
                    return {
                        "status": "failed",
                        "error": f"Missing NPZ key: {frozen_key}",
                        "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                        "frozen_npz": str(Path(frozen_npz_path).resolve()),
                        "frozen_csv_path": frozen_csv_path,
                    }
    
    # Load frozen scalar CSV - REQUIRED for scalar equivalence
    # Fail immediately if CSV is missing or invalid
    if frozen_csv_path is None or not os.path.isfile(frozen_csv_path):
        return {
            "status": "failed",
            "error": f"Frozen scalar CSV not found: {frozen_csv_path}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": frozen_csv_path,
        }
    
    frozen_scalar_csv: dict[str, dict[str, Any]] = {}
    try:
        import csv
        with open(frozen_csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for line_number, row in enumerate(reader, start=2):
                seed_id = row.get("seed", "")
                branch = row.get("branch", "")
                # Nonblocking #7: Reject malformed rows explicitly
                if not seed_id or not branch:
                    return {
                        "status": "failed",
                        "error": (
                            f"Frozen CSV line {line_number} "
                            f"missing seed or branch"
                        ),
                        "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                        "frozen_npz": str(Path(frozen_npz_path).resolve()),
                        "frozen_csv_path": frozen_csv_path,
                    }
                key = f"{branch}_seed_{seed_id}"
                # P1 #5: CSV duplicate detection - fail if duplicate (seed, branch) rows
                if key in frozen_scalar_csv:
                    return {
                        "status": "failed",
                        "error": f"Duplicate CSV row detected for {key}",
                        "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                        "frozen_npz": str(Path(frozen_npz_path).resolve()),
                        "frozen_csv_path": frozen_csv_path,
                    }
                frozen_scalar_csv[key] = {}
                for k, v in row.items():
                    if k not in ("seed", "seed_index", "branch", "rho", "T_window"):
                        try:
                            frozen_scalar_csv[key][k] = float(v)
                        except (ValueError, TypeError):
                            frozen_scalar_csv[key][k] = v
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Could not load frozen CSV {frozen_csv_path}: {e}",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": frozen_csv_path,
        }
    
    # P0 #3: Validate exact CSV key coverage
    # Expected: all seeds × all branch_order combinations
    expected_csv_keys = {
        f"{branch}_seed_{seed}"
        for seed in seeds
        for branch in branch_order
    }
    actual_csv_keys = set(frozen_scalar_csv.keys())
    
    if actual_csv_keys != expected_csv_keys:
        missing = sorted(expected_csv_keys - actual_csv_keys)
        extra = sorted(actual_csv_keys - expected_csv_keys)
        return {
            "status": "failed",
            "error": (
                "Frozen CSV condition-key mismatch: "
                f"{len(missing)} missing, {len(extra)} extra"
            ),
            "missing_csv_keys": missing,
            "extra_csv_keys": extra,
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": frozen_csv_path,
        }
    
    # Validate all expected scalar columns exist in every CSV row
    for csv_key, row_values in frozen_scalar_csv.items():
        missing = set(FROZEN_BRANCH_SCALAR_KEYS) - set(row_values)
        if missing:
            return {
                "status": "failed",
                "error": f"Frozen CSV row {csv_key} missing {len(missing)} required fields",
                "missing_columns": sorted(missing),
                "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
                "frozen_npz": str(Path(frozen_npz_path).resolve()),
                "frozen_csv_path": frozen_csv_path,
            }
    
    # Validate frozen CSV has all expected seeds and branches
    # Expected: 40 seeds × 7 branches = 280 rows
    expected_csv_rows = len(seeds) * len(branch_order)
    actual_csv_rows = len(frozen_scalar_csv)
    if actual_csv_rows != expected_csv_rows:
        return {
            "status": "failed",
            "error": f"Frozen CSV has {actual_csv_rows} rows, expected {expected_csv_rows} (40 seeds × 7 branches)",
            "frozen_manifest": str(Path(frozen_manifest_path).resolve()),
            "frozen_npz": str(Path(frozen_npz_path).resolve()),
            "frozen_csv_path": frozen_csv_path,
        }
    
    # Record frozen hashes - use actual file hashes, not canonical JSON hashes
    # Record frozen hashes - use actual file hashes, not canonical JSON hashes
    results["frozen_manifest_file_sha256"] = file_sha256(frozen_manifest_path)
    results["frozen_npz_file_sha256"] = file_sha256(frozen_npz_path)
    if frozen_csv_path is not None and os.path.exists(frozen_csv_path):
        results["frozen_scalar_csv_file_sha256"] = file_sha256(frozen_csv_path)
    
    # Also record engine source hash
    results["engine_source_sha256"] = engine_source_hash
    
    # Also keep canonical JSON hash for reference
    results["frozen_manifest_hash"] = hashlib.sha256(
        json.dumps(frozen_manifest, sort_keys=True).encode()
    ).hexdigest()
    
    # Validate config matches frozen manifest model - use EXACT equality
    frozen_model = frozen_manifest["model"]
    
    # Check N
    if frozen_model["N"] != config.N:
        results["status"] = "failed"
        results["error"] = f"N mismatch: config={config.N}, frozen={frozen_model['N']}"
        return results
    
    # Check omega - use exact equality
    frozen_omega_arr = np.array(frozen_model["omega"], dtype=float)
    config_omega_arr = np.array(list(config.omega), dtype=float)
    if not np.array_equal(frozen_omega_arr, config_omega_arr):
        results["status"] = "failed"
        results["error"] = f"omega mismatch: frozen={frozen_model['omega']}, config={list(config.omega)}"
        return results
    
    # Check all other model params with EXACT equality (rtol=0, atol=0)
    model_checks = [
        ("dt", frozen_model["dt"], config.dt),
        ("tau", frozen_model["tau"], config.tau),
        ("a", frozen_model["a"], config.a),
        ("q", frozen_model["q"], config.q),
        ("delta", frozen_model["delta"], config.delta),
        ("eta", frozen_model["eta"], config.eta),
        ("mu", frozen_model["mu"], config.mu),
        ("gamma", frozen_model["gamma"], config.gamma),
        ("B_c", frozen_model["B_c"], config.B_c),
        ("B_init_scale", frozen_model.get("B_init_scale", 0.0), config.B_init_scale),
        ("T_window", frozen_model["T_window"], config.T_window),
    ]
    
    for name, frozen_val, config_val in model_checks:
        if not np.isclose(frozen_val, config_val, rtol=0.0, atol=0.0):
            results["status"] = "failed"
            results["error"] = f"{name} mismatch: frozen={frozen_val}, config={config_val}"
            return results
    
    # Check derived values
    # Recommended #3: Use exact comparison for alpha (rtol=0, atol=0)
    if not np.isclose(frozen_model.get("alpha", 0.0), config.alpha, rtol=0.0, atol=0.0):
        results["status"] = "failed"
        results["error"] = f"alpha mismatch: frozen={frozen_model.get('alpha')}, config={config.alpha}"
        return results
    
    # P0 #4: Explicitly validate the frozen protocol and safeguard
    # Validate protocol quantities against frozen constants and manifest
    frozen_protocol = frozen_manifest.get("protocol", {})
    
    # P0 #2: T_sim is stored in model section, not protocol
    protocol_checks = [
        ("T_sim", protocol.T_sim, FROZEN_T_SIM, frozen_model.get("T_sim")),
        ("n_steps", protocol.n_steps(config), FROZEN_N_STEPS, frozen_protocol.get("n_steps")),
        ("burn_end", protocol.burn_end(config), FROZEN_BURN_END, frozen_protocol.get("burn_end")),
        ("hist_end", protocol.hist_end(config), FROZEN_HIST_END, frozen_protocol.get("hist_end")),
        ("future_steps", protocol.future_steps(config), FROZEN_FUTURE_STEPS, frozen_protocol.get("future_steps")),
        ("diagnostic_stride", protocol.diagnostic_stride, 50, frozen_protocol.get("diagnostic_stride")),
        ("scale_epsilon", config.scale_epsilon, FROZEN_ZERO_TOL, frozen_model.get("scale_epsilon", FROZEN_ZERO_TOL)),
    ]
    
    # P0 #2: Also add manifest checks for horizon fields
    # At rho=1, window_steps and recovery_end should match frozen protocol values
    if math.isclose(config.T_window, config.T_star, rel_tol=0.0, abs_tol=0.0):
        actual_window_steps = int(round(config.T_window / config.dt))
        actual_recovery_end = min(5 * actual_window_steps, protocol.future_steps(config))
        protocol_checks.extend([
            ("window_steps", actual_window_steps, FROZEN_WINDOW_STEPS, frozen_protocol.get("window_steps")),
            ("recovery_end", actual_recovery_end, FROZEN_RECOVERY_END, frozen_protocol.get("recovery_end")),
        ])
    
    for name, observed, expected_frozen, expected_manifest in protocol_checks:
        # Check against frozen constant first
        if observed != expected_frozen:
            results["status"] = "failed"
            results["error"] = (
                f"{name} mismatch: observed={observed}, "
                f"expected (frozen)={expected_frozen}"
            )
            return results
        
        # Also check against manifest if available
        if expected_manifest is not None and observed != expected_manifest:
            results["status"] = "failed"
            results["error"] = (
                f"{name} mismatch: observed={observed}, "
                f"expected (manifest)={expected_manifest}"
            )
            return results
    
    # Now run actual equivalence test for each seed
    print("Running baseline equivalence test...")
    all_passed = True
    
    for seed in seeds:
        seed_str = str(seed)
        seed_results = {"status": "passed", "checks": {}, "max_diffs": {}, "errors": {}}
        
        try:
            # Simulate with our engine
            split_state, prefix = simulate_prefix(seed, config, protocol)
            branch_rngs = make_branch_rngs(seed, branch_order)
            
            # Simulate each branch
            engine_results = {}
            for branch in protocol.branches:
                rng = branch_rngs[branch]
                engine_results[branch] = simulate_future(
                    split_state.clone(),
                    prefix,
                    branch,
                    config,
                    protocol,
                    rng,
                )
            
            # CRITICAL: Compute historical cross-branch metrics (the 8 time-based fields)
            # These must be computed AFTER all branches are simulated
            if "continue" in engine_results:
                finalize_historical_branch_metrics(engine_results)
            
            # Check prefix state - iterate over REQUIRED_PREFIX_KEYS
            for key in REQUIRED_PREFIX_KEYS:
                engine_val = prefix.get(key)
                frozen_key = f"prefix_seed_{seed_str}_{key}"
                frozen_val = frozen_files.get(frozen_key)
                
                if frozen_val is None:
                    seed_results["status"] = "failed"
                    seed_results["checks"][f"prefix_{key}_present_in_frozen"] = False
                    all_passed = False
                    continue
                else:
                    seed_results["checks"][f"prefix_{key}_present_in_frozen"] = True
                
                if exact_array_equal_with_nan(engine_val, frozen_val):
                    seed_results["checks"][f"prefix_{key}_exact"] = True
                else:
                    seed_results["checks"][f"prefix_{key}_exact"] = False
                    seed_results["status"] = "failed"
                    all_passed = False
                    if isinstance(engine_val, np.ndarray) and isinstance(frozen_val, np.ndarray):
                        if engine_val.shape != frozen_val.shape:
                            seed_results["errors"][f"prefix_{key}_shape_mismatch"] = f"engine shape {engine_val.shape} != frozen shape {frozen_val.shape}"
                            seed_results["max_diffs"][f"prefix_{key}"] = None
                        else:
                            e = np.where(np.isnan(engine_val), 0.0, engine_val)
                            f = np.where(np.isnan(frozen_val), 0.0, frozen_val)
                            seed_results["max_diffs"][f"prefix_{key}"] = float(np.max(np.abs(e - f)))
                    else:
                        seed_results["max_diffs"][f"prefix_{key}"] = None
            
            # Check branch outputs - separate FROZEN vs EXTENDED keys
            for branch in protocol.branches:
                engine_branch = engine_results[branch]
                frozen_prefix = f"{branch}_seed_{seed_str}"
                
                # P0 #2: Validate horizon metadata in branch outputs
                # The preflight verifies config would produce correct metadata,
                # but we must verify each returned engine_branch actually contains those values
                if math.isclose(config.T_window, config.T_star, rel_tol=0.0, abs_tol=0.0):
                    for key, expected in BASELINE_HORIZON_METADATA.items():
                        observed = engine_branch.get(key)
                        passed = (
                            isinstance(observed, (int, np.integer))
                            and int(observed) == int(expected)
                        )
                        seed_results["checks"][f"{branch}_{key}_baseline_exact"] = passed
                        if not passed:
                            seed_results["status"] = "failed"
                            seed_results["errors"][f"{branch}_{key}_baseline_mismatch"] = (
                                f"observed={observed!r}, expected={expected!r}"
                            )
                            all_passed = False
                
                # === FROZEN MATRIX KEYS: Must exist in historical NPZ ===
                for key in FROZEN_BRANCH_MATRIX_KEYS:
                    engine_val = engine_branch.get(key)
                    frozen_key = f"{frozen_prefix}_{key}"
                    frozen_val = frozen_files.get(frozen_key)
                    
                    if frozen_val is None:
                        seed_results["status"] = "failed"
                        seed_results["checks"][f"{branch}_{key}_present_in_frozen"] = False
                        all_passed = False
                        continue
                    else:
                        seed_results["checks"][f"{branch}_{key}_present_in_frozen"] = True
                    
                    if engine_val is None:
                        seed_results["status"] = "failed"
                        seed_results["checks"][f"{branch}_{key}_present_in_engine"] = False
                        all_passed = False
                        continue
                    else:
                        seed_results["checks"][f"{branch}_{key}_present_in_engine"] = True
                    
                    if exact_array_equal_with_nan(engine_val, frozen_val):
                        seed_results["checks"][f"{branch}_{key}_exact"] = True
                    else:
                        seed_results["checks"][f"{branch}_{key}_exact"] = False
                        seed_results["status"] = "failed"
                        all_passed = False
                        if isinstance(engine_val, np.ndarray) and isinstance(frozen_val, np.ndarray):
                            if engine_val.shape != frozen_val.shape:
                                seed_results["errors"][f"{branch}_{key}_shape_mismatch"] = f"engine shape {engine_val.shape} != frozen shape {frozen_val.shape}"
                                seed_results["max_diffs"][f"{branch}_{key}"] = None
                            else:
                                e = np.where(np.isnan(engine_val), 0.0, engine_val)
                                f = np.where(np.isnan(frozen_val), 0.0, frozen_val)
                                seed_results["max_diffs"][f"{branch}_{key}"] = float(np.max(np.abs(e - f)))
                        else:
                            seed_results["max_diffs"][f"{branch}_{key}"] = None
                
                # === EXTENDED MATRIX KEYS: Validate internally at rho=1 ===
                # These do NOT exist in frozen NPZ. At rho=1, both horizon systems
                # should produce identical results (1750 and 8750 steps match).
                if math.isclose(config.T_window, config.T_star, rel_tol=0.0, abs_tol=0.0):
                    for key in EXTENDED_BRANCH_MATRIX_KEYS:
                        engine_val = engine_branch.get(key)
                        if engine_val is None:
                            seed_results["status"] = "failed"
                            seed_results["checks"][f"{branch}_{key}_present_in_engine"] = False
                            all_passed = False
                            continue
                        else:
                            seed_results["checks"][f"{branch}_{key}_present_in_engine"] = True
                        
                        # Use module-level map for consistency - direct indexing
                        frozen_equiv_key = EXTENDED_MATRIX_EQUIVALENCE_MAP[key]
                        if frozen_equiv_key:
                            engine_frozen_equiv = engine_branch.get(frozen_equiv_key)
                            if engine_frozen_equiv is not None:
                                if exact_array_equal_with_nan(engine_val, engine_frozen_equiv):
                                    seed_results["checks"][f"{branch}_{key}_equals_frozen_at_rho1"] = True
                                else:
                                    seed_results["checks"][f"{branch}_{key}_equals_frozen_at_rho1"] = False
                                    seed_results["status"] = "failed"
                                    all_passed = False
                                    if isinstance(engine_val, np.ndarray) and isinstance(engine_frozen_equiv, np.ndarray):
                                        if engine_val.shape != engine_frozen_equiv.shape:
                                            seed_results["errors"][f"{branch}_{key}_shape_mismatch"] = f"engine shape {engine_val.shape} != equiv shape {engine_frozen_equiv.shape}"
                                            seed_results["max_diffs"][f"{branch}_{key}_vs_frozen"] = None
                                        else:
                                            e = np.where(np.isnan(engine_val), 0.0, engine_val)
                                            f = np.where(np.isnan(engine_frozen_equiv), 0.0, engine_frozen_equiv)
                                            seed_results["max_diffs"][f"{branch}_{key}_vs_frozen"] = float(np.max(np.abs(e - f)))
                                    else:
                                        seed_results["max_diffs"][f"{branch}_{key}_vs_frozen"] = None
                
                # === SCALAR KEYS ===
                # Use module-level constants for consistency
                # FROZEN_BRANCH_SCALAR_KEYS: All 42 historical fields from frozen production
                # EXTENDED_BRANCH_SCALAR_KEYS: New fields in v1 for dual-horizon support
                
                for key in FROZEN_BRANCH_SCALAR_KEYS:
                    engine_val = engine_branch.get(key)
                    
                    # P1 #8: Use CSV as authority, not NPZ fallback
                    # Get from CSV only (production stores scalars in CSV)
                    frozen_val = None
                    csv_key = f"{branch}_seed_{seed_str}"
                    if csv_key in frozen_scalar_csv and key in frozen_scalar_csv[csv_key]:
                        frozen_val = frozen_scalar_csv[csv_key][key]
                    
                    # FROZEN scalars MUST exist in historical data
                    if frozen_val is None:
                        seed_results["status"] = "failed"
                        seed_results["checks"][f"{branch}_{key}_present_in_frozen"] = False
                        all_passed = False
                        continue
                    else:
                        seed_results["checks"][f"{branch}_{key}_present_in_frozen"] = True
                    
                    if engine_val is None:
                        seed_results["status"] = "failed"
                        seed_results["checks"][f"{branch}_{key}_present_in_engine"] = False
                        all_passed = False
                        continue
                    else:
                        seed_results["checks"][f"{branch}_{key}_present_in_engine"] = True
                    
                    # For scalars, compare directly - DO NOT silently skip
                    # Normalize to scalar value
                    try:
                        engine_scalar = float(engine_val)
                    except (TypeError, ValueError) as e:
                        seed_results["status"] = "failed"
                        seed_results["checks"][f"{branch}_{key}_is_scalar"] = False
                        seed_results["errors"][f"{branch}_{key}_type_error"] = f"Cannot convert to float: {type(engine_val).__name__}: {e}"
                        all_passed = False
                        continue
                    
                    try:
                        frozen_scalar = float(frozen_val)
                    except (TypeError, ValueError) as e:
                        seed_results["status"] = "failed"
                        seed_results["checks"][f"{branch}_{key}_frozen_is_scalar"] = False
                        seed_results["errors"][f"{branch}_{key}_frozen_type_error"] = f"Cannot convert frozen to float: {type(frozen_val).__name__}: {e}"
                        all_passed = False
                        continue
                    
                    # Compare with exact equality (rtol=0, atol=0)
                    engine_is_nan = bool(np.isnan(engine_scalar))
                    frozen_is_nan = bool(np.isnan(frozen_scalar))
                    
                    if engine_is_nan and frozen_is_nan:
                        seed_results["checks"][f"{branch}_{key}_exact"] = True
                    elif np.isclose(engine_scalar, frozen_scalar, rtol=0.0, atol=0.0):
                        seed_results["checks"][f"{branch}_{key}_exact"] = True
                    else:
                        seed_results["checks"][f"{branch}_{key}_exact"] = False
                        seed_results["status"] = "failed"
                        all_passed = False
                        seed_results["max_diffs"][f"{branch}_{key}"] = float(abs(engine_scalar - frozen_scalar)) if not (engine_is_nan or frozen_is_nan) else None
                
                # === EXTENDED SCALAR KEYS: Validate internally at rho=1 ===
                if math.isclose(config.T_window, config.T_star, rel_tol=0.0, abs_tol=0.0):
                    for key in EXTENDED_BRANCH_SCALAR_KEYS:
                        engine_val = engine_branch.get(key)
                        if engine_val is None:
                            seed_results["status"] = "failed"
                            seed_results["checks"][f"{branch}_{key}_present_in_engine"] = False
                            all_passed = False
                            continue
                        else:
                            seed_results["checks"][f"{branch}_{key}_present_in_engine"] = True
                        
                        # Use module-level map for consistency - direct indexing
                        frozen_equiv = EXTENDED_SCALAR_EQUIVALENCE_MAP[key]
                        if frozen_equiv:
                            # Get the engine's own frozen-equivalent value
                            engine_frozen_equiv = engine_branch.get(frozen_equiv)
                            
                            if engine_frozen_equiv is None:
                                seed_results["status"] = "failed"
                                seed_results["checks"][f"{branch}_{frozen_equiv}_present_in_engine"] = False
                                all_passed = False
                                continue
                            
                            # Validate internal consistency: extended should equal frozen equivalent
                            try:
                                engine_scalar = float(engine_val)
                                equiv_scalar = float(engine_frozen_equiv)
                            except (TypeError, ValueError) as e:
                                seed_results["status"] = "failed"
                                seed_results["checks"][f"{branch}_{key}_internal_consistency"] = False
                                seed_results["errors"][f"{branch}_{key}_internal_type_error"] = str(e)
                                all_passed = False
                                continue
                            
                            engine_is_nan = bool(np.isnan(engine_scalar))
                            equiv_is_nan = bool(np.isnan(equiv_scalar))
                            
                            if engine_is_nan and equiv_is_nan:
                                seed_results["checks"][f"{branch}_{key}_internal_exact"] = True
                            elif np.isclose(engine_scalar, equiv_scalar, rtol=0.0, atol=0.0):
                                seed_results["checks"][f"{branch}_{key}_internal_exact"] = True
                            else:
                                seed_results["checks"][f"{branch}_{key}_internal_exact"] = False
                                seed_results["status"] = "failed"
                                all_passed = False
                                seed_results["max_diffs"][f"{branch}_{key}_internal"] = float(abs(engine_scalar - equiv_scalar)) if not (engine_is_nan or equiv_is_nan) else None
        
        except Exception as e:
            seed_results["status"] = "failed"
            seed_results["error"] = str(e)
            import traceback
            seed_results["traceback"] = traceback.format_exc()
            all_passed = False
        
        results["seed_results"][seed_str] = seed_results
        print(f"  Seed {seed_str}: {seed_results['status']}")
    
    if all_passed:
        results["status"] = "passed"
        print("Baseline equivalence: PASSED")
    else:
        results["status"] = "failed"
        print("Baseline equivalence: FAILED")
        # Print details of failures
        for seed_str, seed_results in results["seed_results"].items():
            if seed_results.get("status") != "passed":
                print(f"  Seed {seed_str} failures:")
                for check, val in seed_results.get("checks", {}).items():
                    if not val:
                        print(f"    CHECK FAILED: {check}")
                for key, val in seed_results.get("max_diffs", {}).items():
                    print(f"    MAX DIFF: {key} = {val}")
    
    return results


# =============================================================================
# Main API
# =============================================================================

# Known branches - allowlist for validation
KNOWN_BRANCHES = frozenset({
    "continue",
    "reset_ema",
    "reset_B",
    "reset_B_ema",
    "B_carrier_only",
    "full_reset",
    "future_shuffle",
})


def run_seed(
    seed: int,
    config: ModelConfig,
    protocol: ProtocolConfig,
    branch_order: tuple[str, ...],
) -> dict[str, Any]:
    """Run a single seed through prefix + all branches.
    
    CRITICAL: branch_order defines the FULL frozen RNG namespace (7 branches).
    protocol.branches defines which branches are actually executed.
    
    This ensures future_shuffle gets the 7th RNG sequence (not the 4th)
    as in production, even when only 4 study branches are executed.
    
    Returns complete seed results with all branches.
    """
    # Preflight validation: validate config and protocol
    config.validate()
    protocol.validate(config)
    
    # Nonblocking #8: Require continue branch for historical metrics
    if "continue" not in protocol.branches:
        raise ValueError(
            "run_seed requires the continue branch "
            "to compute historical cross-branch metrics"
        )
    
    # Validate all protocol branches are known
    for branch in protocol.branches:
        if branch not in KNOWN_BRANCHES:
            raise ValueError(
                f"Unknown branch '{branch}'. Known branches: {sorted(KNOWN_BRANCHES)}"
            )
    
    # Validate all protocol branches are in branch_order (for RNG namespace)
    for branch in protocol.branches:
        if branch not in branch_order:
            raise ValueError(
                f"Branch '{branch}' in protocol.branches but not in branch_order. "
                f"branch_order must include all protocol branches for correct RNG namespace."
            )
    
    # Validate branch_order has no duplicates and all are known
    if len(branch_order) != len(set(branch_order)):
        raise ValueError(f"branch_order has duplicate branches: {branch_order}")
    for branch in branch_order:
        if branch not in KNOWN_BRANCHES:
            raise ValueError(f"Unknown branch '{branch}' in branch_order. Known branches: {sorted(KNOWN_BRANCHES)}")
    
    # Simulate prefix
    split_state, prefix = simulate_prefix(seed, config, protocol)
    
    # Create branch RNGs using frozen algorithm with FULL branch_order
    branch_rngs = make_branch_rngs(seed, branch_order)
    
    # Execute only the branches in protocol.branches, but use RNGs from branch_order
    branch_results = {}
    for branch in protocol.branches:
        if branch not in branch_rngs:
            raise ValueError(
                f"Branch '{branch}' not found in branch_rngs. "
                f"This indicates branch_order={branch_order} does not match the RNG namespace. "
                f"Registered branches: {list(branch_rngs.keys())}"
            )
        rng = branch_rngs[branch]
        
        branch_results[branch] = simulate_future(
            split_state.clone(),
            prefix,
            branch,
            config,
            protocol,
            rng,
        )
    
    # Compute historical cross-branch metrics (the 8 time-based fields)
    # These must be computed AFTER all branches are simulated
    if "continue" in branch_results:
        finalize_historical_branch_metrics(branch_results)
    
    return {
        "seed": int(seed),
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
            "T_sim": protocol.T_sim,
            "burn_end_time": protocol.burn_end_time,
            "split_time": protocol.split_time,
            "future_duration": protocol.future_duration,
        },
        "prefix": prefix,
        "branches": branch_results,
    }


if __name__ == "__main__":
    # Quick validation
    config = DEFAULT_MODEL_CONFIG
    config.validate()
    protocol = DEFAULT_PROTOCOL_CONFIG
    protocol.validate(config)
    
    print(f"Engine v1 loaded successfully")
    print(f"  N={config.N}, dt={config.dt}, tau={config.tau}")
    print(f"  T_window={config.T_window}, alpha={config.alpha:.6f}")
    print(f"  mean_omega={config.mean_omega:.6f}, T_*={config.T_star:.6f}")
    print(f"  delay_steps={config.delay_steps}")
    print(f"  Protocol: T_sim={protocol.T_sim}, burn={protocol.burn_end_time}, "
          f"split={protocol.split_time}, future={protocol.future_duration}")
