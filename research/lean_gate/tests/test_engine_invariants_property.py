"""H2 (truthfulness hardening, agreed revision 2026-11-20): seeded property tests of engine invariants.

The step-order pins (test_engine_step_order.py) check exact values on a few hand-built N=2 states. These tests run
the real, SHA-256-locked aief_experiment_engine_v1.py on a few hundred random VALID configurations and states
(numpy seeded generator, no new dependency) and check, after every step, the invariants the Lean models and the
analysis rely on:

  I1  state.validate passes (history length delay_steps + 1, shapes, finiteness, B symmetric/zero-diag/nonneg).
  I2  theta == history[-1] exactly, theta in [0, 2 pi] -- CLOSED at 2 pi: np.mod(x, 2 pi) returns exactly 2 pi for a
      tiny negative x (float rounding), so [0, 2 pi) is not an engine invariant (test_mod_can_return_two_pi).
  I3  B exactly symmetric, diagonal exactly 0, B >= 0; after every advance_state also the gap
      a - q * rowsum >= delta - FROZEN_GAP_TOL. initialize_state does NOT enforce the gap: with a large B_init_scale the
      initial B can violate it until the first step projects it (test_initial_gap_not_enforced). At the production
      config (B_init_scale 0.0005, N 12) the initial gap holds.
  I4  R (returned by advance_state) symmetric, zero diagonal, 0 <= R <= 1 + 1e-12.
  I5  |coherence_acc| <= 1 + 1e-12 -- CONDITIONAL on |C0| <= 1 and alpha in (0, 1]. alpha = exp(-dt/T_window) lies in
      (0, 1) for every valid config by construction. test_coherence_bound_is_conditional shows the bound FAILS from
      |C0| > 1, so it is a consequence of the start value, not a property of every state.
  I6  the history queue ages oldest-first: once full, new history[:-1] == old history[1:].
  I7  apply_intervention (every branch) keeps I1-I3.
  I8  same seed, same config -> bit-identical trajectory (the only bit-exact claim here).

Config rejection: ModelConfig.validate must reject dt <= 0, non-finite dt, T_window <= 0, and tau not equal to
delay_steps * dt. alpha out of (0, 1] cannot be produced by a config that passes those checks; that is documented,
not tested as a rejection.

test_negative_controls applies 11 one-line mutants to a temporary copy of the engine (the locked file is never edited)
and requires each to break at least one invariant, so a vacuous checker would fail CI. Two further mutants
(B_sym_dropped, B_diag_kept) are equivalent in valid states, with the reason written next to EQUIVALENT, and
test_equivalent_mutants_survive pins that they give bit-identical trajectories.
"""
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
import aief_experiment_engine_v1 as eng  # noqa: E402

SEED = 20261120
N_CASES = 200
TWO_PI = 2.0 * math.pi
DTS = (0.01, 0.02, 0.05, 0.1, 0.25, 0.5)


def random_config(rng, m=eng):
    """A random config that passes ModelConfig.validate (retried until it does)."""
    for _ in range(100):
        N = int(rng.integers(2, 9))
        dt = float(rng.choice(DTS))
        d = int(rng.integers(1, 7))
        a = float(rng.uniform(0.5, 2.0))
        delta = float(rng.uniform(0.0, 0.9 * a))
        c = m.ModelConfig(
            N=N, dt=dt, tau=d * dt, omega=tuple(rng.uniform(-3.0, 3.0, N).tolist()),
            a=a, q=float(rng.uniform(0.2, 3.0)), delta=delta,
            eta=float(rng.uniform(0.0, 5.0)), mu=float(rng.uniform(0.0, 2.0)),
            gamma=float(rng.uniform(0.0, 2.0)), T_window=float(rng.uniform(0.05, 20.0)),
            B_c=0.1, B_init_scale=float(rng.uniform(0.0, 2.0)), scale_epsilon=m.FROZEN_ZERO_TOL)
        try:
            c.validate()
        except ValueError:
            continue
        return c
    raise AssertionError("no valid config in 100 draws")


def check_state(state, c, m=eng, gap=True):
    state.validate(c)                                                        # I1
    assert len(state.history) == c.delay_steps + 1
    assert np.array_equal(state.theta, state.history[-1]), "theta != history[-1]"   # I2
    assert np.all(state.theta >= 0.0) and np.all(state.theta <= TWO_PI)
    assert np.array_equal(state.B, state.B.T), "B not exactly symmetric"   # I3
    assert np.all(np.diag(state.B) == 0.0) and np.all(state.B >= 0.0)
    if gap:
        g = c.a - c.q * np.sum(state.B, axis=1)
        assert np.min(g) >= c.delta - m.FROZEN_GAP_TOL, "gap constraint"
    assert np.max(np.abs(state.coherence_acc)) <= 1.0 + 1e-12, "|C| > 1"    # I5


def check_R(R):                                                              # I4
    assert np.array_equal(R, R.T) and np.all(np.diag(R) == 0.0)
    assert np.all(R >= 0.0) and np.all(R <= 1.0 + 1e-12)


def run_case(case_seed, m=eng, branches=True, stats=None):
    rng = np.random.default_rng(case_seed)
    c = random_config(rng, m)
    s = m.initialize_state(int(rng.integers(0, 2**31)), c)
    check_state(s, c, m, gap=False)   # the gap is enforced by advance_state, not by initialize_state
    step_rng = np.random.default_rng(case_seed + 1)
    for _ in range(2 * c.delay_steps + 3):
        old = [h.copy() for h in s.history]
        R, _, info = m.advance_state(s, c, step_rng)
        if stats is not None:
            stats["steps"] += 1
            stats["projected"] += bool(info["projection_active"])
        check_R(R)
        check_state(s, c, m)
        assert all(np.array_equal(x, y) for x, y in zip(s.history[:-1], old[1:])), "queue aging"   # I6
    if branches:                                                             # I7
        for b in sorted(m.KNOWN_BRANCHES):
            t = s.clone()
            m.apply_intervention(t, b, c, np.random.default_rng(case_seed + 2))
            check_state(t, c, m)
            R, _, _ = m.advance_state(t, c, step_rng)
            check_R(R)
            check_state(t, c, m)
    return s


def test_invariants_hold_on_random_valid_states():
    stats = {"steps": 0, "projected": 0}
    for k in range(N_CASES):
        try:
            run_case(SEED + 1000 * k, stats=stats)
        except AssertionError as e:
            raise AssertionError(f"case {k} (seed {SEED + 1000 * k}): {e}") from None
    # coverage: the gap check is only meaningful if the projection actually fires (2006 main steps, 264 projected at SEED)
    assert stats["steps"] > 1500 and stats["projected"] > 150, stats


def test_production_config_invariants():
    c = eng.DEFAULT_MODEL_CONFIG
    s = eng.initialize_state(0, c)
    rng = np.random.default_rng(SEED)
    for _ in range(c.delay_steps + 5):
        R, _, _ = eng.advance_state(s, c, rng)
        check_R(R)
        check_state(s, c)


def test_coherence_bound_is_conditional():
    """Negative control for I5: from |C0| = 5 the EMA stays above 1 after one step (alpha * 5 - (1 - alpha) > 1)."""
    rng = np.random.default_rng(SEED)
    c = random_config(rng)
    s = eng.initialize_state(1, c)
    s.coherence_acc[:] = 5.0
    eng.advance_state(s, c, rng)
    if c.alpha * 5.0 - (1.0 - c.alpha) > 1.0:
        assert np.max(np.abs(s.coherence_acc)) > 1.0
        with pytest.raises(AssertionError, match=r"\|C\| > 1"):
            check_state(s, c)
    else:
        pytest.fail(f"pick a seed with larger alpha (alpha={c.alpha})")


def test_initial_gap_not_enforced():
    """Documented engine fact: initialize_state scales B by B_init_scale without the gap projection."""
    import dataclasses
    c = dataclasses.replace(eng.DEFAULT_MODEL_CONFIG, B_init_scale=2.0)
    c.validate()
    s = eng.initialize_state(0, c)
    assert np.min(c.a - c.q * np.sum(s.B, axis=1)) < c.delta              # violated at init
    eng.advance_state(s, c, np.random.default_rng(SEED))
    assert np.min(c.a - c.q * np.sum(s.B, axis=1)) >= c.delta - eng.FROZEN_GAP_TOL   # projected after one step
    p = eng.initialize_state(0, eng.DEFAULT_MODEL_CONFIG)
    check_state(p, eng.DEFAULT_MODEL_CONFIG)                                 # production init satisfies it


def test_mod_can_return_two_pi():
    """Why I2 is closed at 2 pi: the engine wraps with np.mod, which rounds a tiny negative phase up to 2 pi."""
    assert np.mod(-1e-20, TWO_PI) == TWO_PI


def test_seed_determinism_bit_exact():                                       # I8
    a, b = run_case(SEED, branches=False), run_case(SEED, branches=False)
    assert np.array_equal(a.theta, b.theta) and np.array_equal(a.B, b.B)
    assert np.array_equal(a.coherence_acc, b.coherence_acc)
    assert all(np.array_equal(x, y) for x, y in zip(a.history, b.history))


@pytest.mark.parametrize("field,value", [("dt", 0.0), ("dt", -0.1), ("dt", float("nan")), ("T_window", 0.0),
                                         ("tau", 0.015)])
def test_invalid_configs_rejected(field, value):
    import dataclasses
    base = dataclasses.replace(eng.DEFAULT_MODEL_CONFIG, dt=0.01, tau=0.5)
    with pytest.raises(ValueError):
        dataclasses.replace(base, **{field: value}).validate()


MUTANTS = [
    ("clip_dropped", "    B_unprojected = np.maximum(B_unprojected, 0.0)\n", "\n"),
    ("projection_dropped", "    if pre_violation:\n", "    if False:\n"),
    ("theta_no_wrap", "    state.theta = np.mod(\n        state.theta + config.dt * (omega_arr + coupling), \n"
                      "        2.0 * np.pi\n    )\n",
     "    state.theta = state.theta + config.dt * (omega_arr + coupling) + 2.0 * np.pi\n"),
    ("history_appends_old_theta", "    state.history.append(state.theta.copy())\n",
     "    state.history.append(delayed.copy())\n"),
    ("history_never_pops", "        state.history.pop(0)\n", "        pass\n"),
    ("history_pops_newest", "        state.history.pop(0)\n", "        state.history.pop(-2)\n"),
    ("ema_weight_sum_not_one", "config.alpha * state.coherence_acc + (1.0 - config.alpha) * z_inst",
     "config.alpha * state.coherence_acc + z_inst"),
    ("R_not_symmetrised", "    result = 0.5 * (result + result.T)\n", "\n"),
    ("R_diag_kept", "    np.fill_diagonal(result, 0.0)\n", "\n"),
    ("intervention_history_stale", "        state.history = [new_theta.copy() for _ in range(config.delay_steps + 1)]\n",
     "\n"),
    ("intervention_no_sym", "    state.B = 0.5 * (state.B + state.B.T)\n    np.fill_diagonal(state.B, 0.0)\n\n\n",
     "    state.B[0, 1] += 0.5\n\n\n"),
]


# Equivalent mutants: these lines are redundant in a valid state, so the invariants CANNOT catch them, and that is
# correct, not a gap. test_equivalent_mutants_survive pins it, so a future engine change that makes them matter shows up.
#  B_sym_dropped: B and R are exactly symmetric, and B + dt((eta+mu)R - mu - gamma B) does the same float operations on
#    equal inputs at (i, j) and (j, i), so the sum is already exactly symmetric.
#  B_diag_kept: B_ii = R_ii = 0, so the diagonal update is -dt*mu <= 0 (mu >= 0 by validate), and the max(., 0) clip
#    before it already makes it 0.
EQUIVALENT = [
    ("B_sym_dropped", "    B_unprojected = 0.5 * (B_unprojected + B_unprojected.T)\n", "\n"),
    ("B_diag_kept", "    np.fill_diagonal(B_unprojected, 0.0)\n", "\n"),
]


def _load_mutant(tmp_path, name, old, new):
    src = (REPO / "aief_experiment_engine_v1.py").read_text()
    assert src.count(old) == 1, f"{name}: anchor not unique ({src.count(old)})"
    f = tmp_path / f"eng_inv_{name}.py"
    f.write_text(src.replace(old, new, 1))
    spec = importlib.util.spec_from_file_location(f"eng_inv_{name}", f)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_invariants_pass_on_unmodified_copy(tmp_path):
    mod = _load_mutant(tmp_path, "identity", "def advance_state(", "def advance_state(")
    for k in range(20):
        run_case(SEED + 1000 * k, m=mod)


@pytest.mark.parametrize("name,old,new", MUTANTS, ids=[x[0] for x in MUTANTS])
def test_negative_controls(tmp_path, name, old, new):
    mod = _load_mutant(tmp_path, name, old, new)
    for k in range(20):
        try:
            run_case(SEED + 1000 * k, m=mod)
        except (AssertionError, RuntimeError, ValueError, FloatingPointError):
            return
    pytest.fail(f"mutant {name} survived 20 random cases")


@pytest.mark.parametrize("name,old,new", EQUIVALENT, ids=[x[0] for x in EQUIVALENT])
def test_equivalent_mutants_survive(tmp_path, name, old, new):
    mod = _load_mutant(tmp_path, name, old, new)
    for k in range(20):
        a, b = run_case(SEED + 1000 * k, m=mod, branches=False), run_case(SEED + 1000 * k, branches=False)
        assert np.array_equal(a.B, b.B) and np.array_equal(a.theta, b.theta), f"{name} is not equivalent (case {k})"
