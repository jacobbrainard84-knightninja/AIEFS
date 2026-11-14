"""Production-delay engine probes: the real 51-slot history buffer at dt=0.01, tau=0.5.

Why this file exists
--------------------
``research/lean_gate/tests/test_engine_step_order.py`` runs the real ``advance_state``
on exact N=2 states, but its helper hard-asserts ``c.delay_steps == 1`` (line 40 of that
file). The frozen production constants in ``aief_experiment_engine_v1.py`` are
``FROZEN_DT = 0.01``, ``FROZEN_TAU = 0.5`` (lines 64-65), so ``delay_steps = 50`` and
``initialize_state`` creates ``delay_steps + 1 = 51`` history slots (line 711).
``compute_R`` reads ``state.history[0]`` (line 729), the phase coupling reads
``state.history[0]`` (lines 830-835), and each step appends the new phase and pops the
oldest entry (lines 841-844).

The Lean P5 ``HistoryBuffer`` theorems are general in the delay ``D``, but they are
abstract sequence functions; they do not check the Python list/aliasing contract or the
startup-to-live-delay boundary. These tests exercise that contract on the real engine.
They are engine facts, not Lean facts. They do not claim anything about float64 phase
locking, and they do not promote any Lean candidate.

Wrong orders each probe rules out (the value under the wrong order is asserted to differ):
  * reading ``history[1]`` or the newest slot instead of ``history[0]``;
  * aliasing the 51 initial copies of theta;
  * appending the old theta, or failing to pop exactly one oldest slot;
  * reading current theta in the sine coupling (the c015 F1 mutant).
Expected values are hand-derived, not obtained by calling the engine's own ``compute_R``.
"""
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
import aief_experiment_engine_v1 as eng  # noqa: E402

TOL = 1e-12
PI = math.pi


def production_config(**overrides):
    """Frozen production parameters, with named, explicit overrides."""
    params = dict(
        N=eng.FROZEN_N,
        dt=eng.FROZEN_DT,
        tau=eng.FROZEN_TAU,
        omega=tuple(float(x) for x in eng.FROZEN_OMEGA),
        a=eng.FROZEN_A,
        q=eng.FROZEN_Q,
        delta=eng.FROZEN_DELTA,
        eta=eng.FROZEN_ETA,
        mu=eng.FROZEN_MU,
        gamma=eng.FROZEN_GAMMA,
        T_window=eng.FROZEN_T_WINDOW,
        B_c=eng.FROZEN_B_C,
        B_init_scale=eng.FROZEN_B_INIT_SCALE,
        scale_epsilon=1e-12,
    )
    params.update(overrides)
    c = eng.ModelConfig(**params)
    c.validate()
    return c


def test_production_delay_configuration_and_initialisation():
    """dt=0.01 / tau=0.5 gives D=50, a 51-slot history, and independent copies."""
    c = production_config()
    assert c.delay_steps == 50
    assert c.dt == 0.01 and c.tau == 0.5
    assert abs(c.alpha - eng.FROZEN_ALPHA) < TOL
    # The d=1 step-order probes are unit-delay probes, not production-delay coverage.
    assert c.delay_steps != 1

    st = eng.initialize_state(20260814, c)
    assert st.N == eng.FROZEN_N
    assert len(st.history) == c.delay_steps + 1 == 51
    for h in st.history:
        assert np.array_equal(h, st.theta)

    # initialize_state must copy theta for each slot, not alias one array.
    st.history[0][0] = 123.0
    assert st.history[1][0] != 123.0
    assert st.history[50][0] != 123.0
    assert st.theta[0] != 123.0


def test_production_delay_buffer_aging_and_oldest_slot():
    """51 non-constant slots age one place per step; EMA source is always slot 0.

    With omega=0 and eta=mu=gamma=0 the weights stay zero, so theta is constant and
    every appended phase is that same theta. Before step n (n = 0..50) the oldest
    slot must be initial_history[n]; at n=50 it is the last initial slot, and after
    that step the oldest slot is the first *live* delayed value (the appended theta).
    """
    c = production_config(
        omega=(0.0,) * eng.FROZEN_N,
        eta=0.0, mu=0.0, gamma=0.0,
        a=1.0, q=1.0, delta=0.05,
        B_init_scale=0.0,
    )
    assert c.delay_steps == 50

    theta = np.linspace(0.0, 1.0, eng.FROZEN_N)
    initial = [np.full(eng.FROZEN_N, k / 100.0) for k in range(51)]
    st = eng.DynamicState(
        theta=theta,
        B=np.zeros((eng.FROZEN_N, eng.FROZEN_N)),
        coherence_acc=np.zeros((eng.FROZEN_N, eng.FROZEN_N), dtype=complex),
        history=initial,
    )
    rng = np.random.default_rng(0)
    alpha = c.alpha
    C_expected = np.zeros((eng.FROZEN_N, eng.FROZEN_N), dtype=complex)

    for n in range(51):
        # Before each call: oldest slot is initial_history[min(n, 50)].
        expected_oldest = initial[min(n, 50)]
        assert np.array_equal(st.history[0], expected_oldest), f"oldest slot drift at step {n}"

        # Independent hand-derived EMA source: omega=0, tau offset=0, so
        # z_inst[i,j] = exp(i(theta_i - delayed_j)). This is not a call to compute_R.
        z_inst = np.exp(1j * (theta[:, None] - expected_oldest[None, :]))
        C_expected = alpha * C_expected + (1.0 - alpha) * z_inst

        R, R_driver, info = eng.advance_state(st, c, rng, shuffle_driver=False)

        assert np.allclose(st.coherence_acc, C_expected, rtol=0.0, atol=TOL), \
            f"EMA did not read slot 0 at step {n}"
        assert np.allclose(R, R_driver, rtol=0.0, atol=TOL)
        assert info["pre_violation"] is False
        assert len(st.history) == 51, f"history length changed at step {n}"
        assert np.array_equal(st.history[-1], theta), f"newest slot is not the appended theta at step {n}"
        assert np.array_equal(st.theta, theta), f"theta moved at step {n}"

    # The n=50 boundary consumed initial_history[50]; every initial slot is now gone.
    assert np.array_equal(st.history[0], theta)
    assert all(np.array_equal(h, theta) for h in st.history)


def test_production_delay_coupling_reads_oldest_slot():
    """At D=50, the sine coupling and compute_R read history[0], not slot 1/current/newest.

    N=2 hand-derived state: theta=(0, pi/2), omega=0, B0=C0=0, eta=4, mu=gamma=0,
    T_window=1/log(2). With history[0]=(0,0):
      z = [[1,1],[i,i]] => R = (1-alpha)*[[0,1],[1,0]]
      B_new = dt*eta*(1-alpha)*[[0,1],[1,0]] = b*[[0,1],[1,0]], b = 0.04*(1-alpha)
      theta_new[1] = pi/2 + dt*b*sin(0 - pi/2) = pi/2 - dt*b.
    Reading history[1]=(pi,pi) or the newest slot would give a different theta;
    reading CURRENT theta (c015 F1) would leave theta unchanged.
    """
    c = production_config(
        N=2, dt=0.01, tau=0.5,
        omega=(0.0, 0.0),
        a=1.0, q=1.0, delta=0.05,
        eta=4.0, mu=0.0, gamma=0.0,
        T_window=1.0 / math.log(2.0),
        B_init_scale=0.0,
        scale_epsilon=1.0,
    )
    assert c.delay_steps == 50
    alpha = c.alpha
    assert 0.0 < alpha < 1.0

    theta = np.array([0.0, PI / 2])
    history = [np.full(2, k / 100.0) for k in range(51)]
    history[0] = np.array([0.0, 0.0])
    history[1] = np.array([PI, PI])          # distinguishes slot 0 from slot 1
    history[50] = np.array([PI / 2, PI / 2])  # distinguishes slot 0 from newest
    st = eng.DynamicState(
        theta=theta,
        B=np.zeros((2, 2)),
        coherence_acc=np.zeros((2, 2), dtype=complex),
        history=history,
    )
    rng = np.random.default_rng(0)

    b = c.dt * c.eta * (1.0 - alpha)
    expected_R = np.array([[0.0, 1.0 - alpha], [1.0 - alpha, 0.0]])
    expected_theta = np.array([0.0, PI / 2 - c.dt * b])

    R, R_driver, info = eng.advance_state(st, c, rng, shuffle_driver=False)

    assert np.allclose(R, expected_R, rtol=0.0, atol=TOL)
    assert np.allclose(st.B, np.array([[0.0, b], [b, 0.0]]), rtol=0.0, atol=TOL)
    assert np.allclose(st.theta, expected_theta, rtol=0.0, atol=TOL)
    # Negative controls: the wrong orders give visibly different values.
    assert abs(st.theta[1] - PI / 2) > 1e-6            # current theta in the sine (F1)
    assert abs(st.theta[1] - (PI / 2 + c.dt * b)) > 1e-6  # slot 1 = (pi, pi)
    assert len(st.history) == 51
    assert np.array_equal(st.history[0], np.array([PI, PI]))  # old slot 1 is now oldest
    assert np.array_equal(st.history[-1], expected_theta)
