"""theta == history[-1] guard for aief_experiment_engine_v1.DynamicState.

The engine is SHA-256-locked (authority lock, legacy_sources.engine_v1), so its `DynamicState.validate` cannot be
edited. Every engine path that writes a state keeps the newest history entry equal to theta (initialize_state,
advance_state, apply_intervention); validate does not check it. Use `validate_with_theta_history` wherever a state is
built or loaded outside those paths. Equality is exact (np.array_equal): the engine stores `theta.copy()`.
"""
from __future__ import annotations

import numpy as np


def check_theta_history(state) -> None:
    """Raise RuntimeError unless state.theta equals state.history[-1] exactly (shape and values)."""
    if len(state.history) == 0:
        raise RuntimeError("history is empty, so theta == history[-1] cannot hold")
    head = np.asarray(state.history[-1])
    theta = np.asarray(state.theta)
    if head.shape != theta.shape or not np.array_equal(theta, head):
        diff = (
            float(np.max(np.abs(theta - head))) if head.shape == theta.shape else float("nan")
        )
        raise RuntimeError(
            f"theta != history[-1] (max abs difference {diff!r}); the newest history entry must be the current phase"
        )


def validate_with_theta_history(state, config, step: int | None = None) -> None:
    """The engine's own validate first, then the theta == history[-1] check."""
    state.validate(config, step=step)
    check_theta_history(state)
