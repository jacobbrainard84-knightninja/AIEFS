"""theta == history[-1] guard for the pinned engine's DynamicState (audit-inbox direction 4, queue bridge).

The engine (`aief_experiment_engine_v1.py`) is SHA-256-locked in the authority lock, so the guard cannot be added to
`DynamicState.validate` itself. It lives in `research/engine_guards/theta_history.py` and wraps validate. Every engine
path that writes the state keeps `history[-1] == theta`: initialize_state (history = copies of theta), advance_state
(appends theta.copy() after the update) and apply_intervention (history = copies of the new theta). validate checks
shapes, finiteness and B, but not this link, so a hand-built or deserialised state with a stale head passes it.
"""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import aief_experiment_engine_v1 as eng  # noqa: E402
from research.engine_guards.theta_history import check_theta_history, validate_with_theta_history  # noqa: E402

CFG = eng.DEFAULT_MODEL_CONFIG


def _fresh(seed=7):
    return eng.initialize_state(seed, CFG)


def _mismatched(seed=7):
    s = _fresh(seed)
    s.theta = s.theta.copy()
    s.theta[0] = s.theta[0] + 0.25
    return s


def test_engine_validate_misses_mismatch():
    """Documents the gap: the pinned validate accepts a state whose theta is not the newest history entry."""
    s = _mismatched()
    assert not np.array_equal(s.theta, s.history[-1])
    s.validate(CFG)  # no exception: the gap this guard closes


def test_guard_rejects_mismatch():
    with pytest.raises(RuntimeError, match="history\\[-1\\]"):
        check_theta_history(_mismatched())
    with pytest.raises(RuntimeError, match="history\\[-1\\]"):
        validate_with_theta_history(_mismatched(), CFG)


def test_guard_rejects_older_slot_match_only():
    """theta equal to an older slot but not the newest one is still rejected."""
    s = _fresh()
    s.history[-1] = s.history[-1] + 1.0
    assert np.array_equal(s.theta, s.history[0])
    with pytest.raises(RuntimeError):
        check_theta_history(s)


def test_guard_runs_engine_validate_first():
    s = _fresh()
    s.history = s.history[:-1]  # wrong length: engine validate must raise, not the guard
    with pytest.raises(RuntimeError, match="History length"):
        validate_with_theta_history(s, CFG)


def test_guard_accepts_initialized_state():
    validate_with_theta_history(_fresh(), CFG)


def test_guard_accepts_after_engine_steps():
    s = _fresh(11)
    rng = np.random.default_rng(11)
    for step in range(CFG.delay_steps + 3):  # past one full history wrap
        eng.advance_state(s, CFG, rng)
        validate_with_theta_history(s, CFG, step=step)


def test_guard_accepts_clone():
    validate_with_theta_history(_fresh().clone(), CFG)


def test_guard_call_order_validate_then_check(monkeypatch):
    """#N1 (R001 audit of ff3ddf5): pin the ORDER, engine validate first, then the guard (a spy on both)."""
    import research.engine_guards.theta_history as th
    calls = []
    s = _fresh()
    real_validate = s.validate
    s.validate = lambda config, step=None: (calls.append("validate"), real_validate(config, step=step))
    real_check = th.check_theta_history
    monkeypatch.setattr(th, "check_theta_history", lambda st: (calls.append("check"), real_check(st)))
    th.validate_with_theta_history(s, CFG, step=3)
    assert calls == ["validate", "check"]


def test_guard_rejects_empty_history():
    s = _fresh()
    s.history = []
    with pytest.raises(RuntimeError, match="history is empty"):
        check_theta_history(s)


def test_guard_rejects_shape_mismatch():
    s = _fresh()
    s.history[-1] = np.append(s.history[-1], 0.0)
    with pytest.raises(RuntimeError, match="shape"):
        check_theta_history(s)


@pytest.mark.parametrize("where", ["theta", "head"])
def test_guard_rejects_nan_with_clear_message(where):
    s = _fresh()
    if where == "theta":
        s.theta = s.theta.copy()
        s.theta[1] = np.nan
    else:
        s.history[-1] = s.history[-1].copy()
        s.history[-1][1] = np.nan
    with pytest.raises(RuntimeError, match="non-finite"):
        check_theta_history(s)


def test_guard_rejects_rewrapped_angle():
    """Exact equality is intentional: 0.0 vs 2*pi is the same angle but not what the engine stores."""
    s = _fresh()
    s.theta = s.theta.copy()
    s.theta[0] = 0.0
    s.history[-1] = s.theta.copy()
    s.history[-1][0] = 2.0 * np.pi
    with pytest.raises(RuntimeError, match="history\\[-1\\]"):
        check_theta_history(s)


@pytest.mark.parametrize("branch", sorted(eng.KNOWN_BRANCHES))
def test_guard_accepts_after_apply_intervention(branch):
    s = _fresh(13)
    rng = np.random.default_rng(13)
    for _ in range(3):
        eng.advance_state(s, CFG, rng)
    eng.apply_intervention(s, branch, CFG, np.random.default_rng(14))
    validate_with_theta_history(s, CFG)
    eng.advance_state(s, CFG, rng)
    validate_with_theta_history(s, CFG)
