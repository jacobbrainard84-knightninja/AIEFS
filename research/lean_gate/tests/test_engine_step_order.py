"""Engine step-order pins: one advance_state step of main's aief_experiment_engine_v1.py
on tiny hand-computed N=2 states.

Why: the Lean models (013 PhaseCoherenceBridge, 014 TrajectoryInvariants, 015 ClosedLoopCore
candidates) are compared to the engine only by human transcription. These tests run the real
engine code and check the exact values implied by the order those models claim:

  old theta / history[0] -> EMA C updated FIRST -> |C|, symmetrise, diag 0 -> R
  -> B = clip/sym(B + dt((eta+mu)R - mu - gamma B)) -> gap projection if needed
  -> theta += dt(omega + sum_j B_new[i,j] sin(history[0][j] - theta[i])), mod 2 pi
  -> append NEW theta, drop oldest.

Each probe names the wrong orders it rules out (the value under the wrong order is asserted to
differ). Exact values are derived in the comments; floats are compared at 1e-12.

probe_015 reproduces 040282 cycle 015's proved first-step table (C 1/2, R 1/2, drive 2,
B 2/3, theta0 2/3). probe_delay, probe_dt and probe_carry cover the gaps found in the
Auditor review of cycle 015 (F1 delayed read, F2 dt, F3 old-B carry), which that file's own
probes leave open. These are engine facts, not Lean facts; they do not adopt any candidate.
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


def cfg(dt=1.0, tau=1.0, gamma=1.0, T_window=1.0 / math.log(2.0)):
    c = eng.ModelConfig(N=2, dt=dt, tau=tau, omega=(0.0, 0.0), a=1.0, q=1.0, delta=0.0,
                        eta=4.0, mu=0.0, gamma=gamma, T_window=T_window, B_c=0.0,
                        B_init_scale=0.0, scale_epsilon=1.0)
    c.validate()
    assert c.delay_steps == 1
    return c


def xo(v):
    return np.array([[0.0, v], [v, 0.0]])


def step(c, theta, history, B=None):
    st = eng.DynamicState(theta=np.array(theta, dtype=float),
                          B=np.zeros((2, 2)) if B is None else B,
                          coherence_acc=np.zeros((2, 2), dtype=complex),
                          history=[np.array(h, dtype=float) for h in history])
    R, Rd, info = eng.advance_state(st, c, np.random.default_rng(0), shuffle_driver=False)
    return st, R, info


def close(a, b):
    return np.allclose(np.asarray(a), np.asarray(b), rtol=0.0, atol=TOL)


def test_probe_015_first_step_table():
    # theta=(0, pi/2), constant history, C0=B0=0, alpha=1/2, dt=gamma=cap=eps=a=q=1, eta=4.
    c = cfg()
    assert abs(c.alpha - 0.5) < TOL
    st, R, info = step(c, [0.0, PI / 2], [[0.0, PI / 2], [0.0, PI / 2]])
    # z_ij = exp(i(theta_i - theta_j)): diag 1, z01 = -i, z10 = i. NEW C = z/2.
    assert close(st.coherence_acc, np.array([[0.5, -0.5j], [0.5j, 0.5]]))
    # R from NEW C (old C=0 would give R=0; averaging complex C first would give 0).
    assert close(R, xo(0.5))
    # drive 2, preM 2, row sum 2 > cap: scale 1/(2+1) => B = 2/3 (projection fired).
    assert info["pre_violation"] is True
    assert close(st.B, xo(2.0 / 3.0))
    # theta0 += 1*(0 + (2/3) sin(theta_hist_1 - 0)) = 2/3 (OLD B=0 would give 0; unprojected 2).
    assert abs(st.theta[0] - 2.0 / 3.0) < TOL
    assert abs(st.theta[0] - 0.0) > 0.1 and abs(st.theta[0] - 2.0) > 0.1
    # NEW theta appended (appending old theta would leave newest[0] = 0).
    assert len(st.history) == 2
    assert abs(st.history[-1][0] - 2.0 / 3.0) < TOL


def test_probe_delay_coupling_reads_history_oldest():
    # theta = (pi/2, pi/2), history[0] = (0, 0), history[1] = theta. C0=B0=0.
    c = cfg()
    st, R, info = step(c, [PI / 2, PI / 2], [[0.0, 0.0], [PI / 2, PI / 2]])
    # Input reads history[0]: z_ij = exp(i pi/2) = i for all i,j => C = i/2, R = xo(1/2).
    # (Reading newest history would give z = 1, C = 1/2: same |C|, so R alone cannot tell;
    #  the C check does.)
    assert close(st.coherence_acc, np.full((2, 2), 0.5j))
    assert close(R, xo(0.5))
    assert close(st.B, xo(2.0 / 3.0))
    # Coupling reads history[0]: sin(0 - pi/2) = -1 => theta_i = pi/2 - 2/3.
    # Reading CURRENT theta in the sine (040282 c015 F1 mutant) would give sin(0) => pi/2.
    assert close(st.theta, [PI / 2 - 2.0 / 3.0] * 2)
    assert abs(st.theta[0] - PI / 2) > 0.1
    # Shift: oldest is now old history[1] = pi/2, newest the new theta.
    assert close(st.history[0], [PI / 2, PI / 2])
    assert close(st.history[-1], st.theta)


def test_probe_dt_half_no_projection():
    # dt = 1/2, tau = 1/2 (1 delay step), T_window = 1/log 2 => alpha = 2**-1/2.
    c = cfg(dt=0.5, tau=0.5)
    al = 2.0 ** -0.5
    assert abs(c.alpha - al) < TOL
    st, R, info = step(c, [PI / 2, PI / 2], [[0.0, 0.0], [PI / 2, PI / 2]])
    # C = (1-al) i, R = xo(1-al), drive 4(1-al), preM = 0 + dt*drive = 2(1-al) ~ 0.586 < cap.
    assert close(R, xo(1.0 - al))
    assert info["pre_violation"] is False
    b = 2.0 * (1.0 - al)
    assert close(st.B, xo(b))
    # theta = pi/2 + dt*(-b). Omitting dt (c015 F2 mutant) would give pi/2 - b.
    assert close(st.theta, [PI / 2 - 0.5 * b] * 2)
    assert abs(st.theta[0] - (PI / 2 - b)) > 0.1


def test_probe_old_B_carry_partial_step():
    # As probe_dt but B0 = xo(0.2) and gamma*dt = 1/2: the old weights must carry over.
    c = cfg(dt=0.5, tau=0.5)
    al = 2.0 ** -0.5
    st, R, info = step(c, [PI / 2, PI / 2], [[0.0, 0.0], [PI / 2, PI / 2]], B=xo(0.2))
    # preM = 0.2 + 0.5*(4(1-al) - 0 - 1*0.2) = 0.1 + 2(1-al) ~ 0.686 < cap: no projection.
    b = 0.1 + 2.0 * (1.0 - al)
    assert info["pre_violation"] is False
    assert close(st.B, xo(b))
    # A full-reset step (dropping B0, as in the gamma*dt = 1 probes) would give 2(1-al).
    assert abs(st.B[0, 1] - 2.0 * (1.0 - al)) > 0.05
    assert close(st.theta, [PI / 2 - 0.5 * b] * 2)
