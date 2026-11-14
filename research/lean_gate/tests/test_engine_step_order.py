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

probe_memory_mu_sym, probe_clip and probe_wrap cover the gaps Researcher 001 found in the
first version (EMA memory term, mu, |C| symmetrisation, the max(0, .) clip, mod 2 pi).
test_probe_d50_* run the production delay length (delay_steps = 50, a 51-slot queue; GPT-6 inbox note
2026-11-13). test_negative_controls runs every probe against 16 one-line mutants of a temporary copy of the
engine and requires each mutant to fail at least one probe, so the controls are committed.
"""
import importlib.util
import pytest
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
import aief_experiment_engine_v1 as eng  # noqa: E402

TOL = 1e-12
PI = math.pi


def cfg(dt=1.0, tau=1.0, gamma=1.0, T_window=1.0 / math.log(2.0), mu=0.0, omega=(0.0, 0.0),
        m=None, eta=4.0, delay=1):
    m = m or eng
    c = m.ModelConfig(N=2, dt=dt, tau=tau, omega=omega, a=1.0, q=1.0, delta=0.0,
                        eta=eta, mu=mu, gamma=gamma, T_window=T_window, B_c=0.0,
                        B_init_scale=0.0, scale_epsilon=1.0)
    c.validate()
    assert c.delay_steps == delay
    return c


def xo(v):
    return np.array([[0.0, v], [v, 0.0]])


def step(c, theta, history, B=None, C0=None, m=None):
    m = m or eng
    st = m.DynamicState(theta=np.array(theta, dtype=float),
                        B=np.zeros((2, 2)) if B is None else B,
                        coherence_acc=(np.zeros((2, 2), dtype=complex) if C0 is None
                                       else np.array(C0, dtype=complex)),
                        history=[np.array(h, dtype=float) for h in history])
    R, Rd, info = m.advance_state(st, c, np.random.default_rng(0), shuffle_driver=False)
    return st, R, info


def close(a, b):
    return np.allclose(np.asarray(a), np.asarray(b), rtol=0.0, atol=TOL)


def test_probe_015_first_step_table(m=None):
    # theta=(0, pi/2), constant history, C0=B0=0, alpha=1/2, dt=gamma=cap=eps=a=q=1, eta=4.
    c = cfg(m=m)
    assert abs(c.alpha - 0.5) < TOL
    st, R, info = step(c, m=m, theta=[0.0, PI / 2], history=[[0.0, PI / 2], [0.0, PI / 2]])
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
    # theta1 += (2/3) sin(history[0][0] - pi/2) = -2/3.
    assert abs(st.theta[1] - (PI / 2 - 2.0 / 3.0)) < TOL
    # NEW theta appended (appending old theta would leave newest[0] = 0).
    assert len(st.history) == 2
    assert abs(st.history[-1][0] - 2.0 / 3.0) < TOL


def test_probe_delay_coupling_reads_history_oldest(m=None):
    # theta = (pi/2, pi/2), history[0] = (0, 0), history[1] = theta. C0=B0=0.
    c = cfg(m=m)
    st, R, info = step(c, m=m, theta=[PI / 2, PI / 2], history=[[0.0, 0.0], [PI / 2, PI / 2]])
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


def test_probe_dt_half_no_projection(m=None):
    # dt = 1/2, tau = 1/2 (1 delay step), T_window = 1/log 2 => alpha = 2**-1/2.
    c = cfg(dt=0.5, tau=0.5, m=m)
    al = 2.0 ** -0.5
    assert abs(c.alpha - al) < TOL
    st, R, info = step(c, m=m, theta=[PI / 2, PI / 2], history=[[0.0, 0.0], [PI / 2, PI / 2]])
    # C = (1-al) i, R = xo(1-al), drive 4(1-al), preM = 0 + dt*drive = 2(1-al) ~ 0.586 < cap.
    assert close(R, xo(1.0 - al))
    assert info["pre_violation"] is False
    b = 2.0 * (1.0 - al)
    assert close(st.B, xo(b))
    # theta = pi/2 + dt*(-b). Omitting dt (c015 F2 mutant) would give pi/2 - b.
    assert close(st.theta, [PI / 2 - 0.5 * b] * 2)
    assert abs(st.theta[0] - (PI / 2 - b)) > 0.1


def test_probe_old_B_carry_partial_step(m=None):
    # As probe_dt but B0 = xo(0.2) and gamma*dt = 1/2: the old weights must carry over.
    c = cfg(dt=0.5, tau=0.5, m=m)
    al = 2.0 ** -0.5
    st, R, info = step(c, m=m, theta=[PI / 2, PI / 2], history=[[0.0, 0.0], [PI / 2, PI / 2]], B=xo(0.2))
    # preM = 0.2 + 0.5*(4(1-al) - 0 - 1*0.2) = 0.1 + 2(1-al) ~ 0.686 < cap: no projection.
    b = 0.1 + 2.0 * (1.0 - al)
    assert info["pre_violation"] is False
    assert close(st.B, xo(b))
    # A full-reset step (dropping B0, as in the gamma*dt = 1 probes) would give 2(1-al).
    assert abs(st.B[0, 1] - 2.0 * (1.0 - al)) > 0.05
    assert close(st.theta, [PI / 2 - 0.5 * b] * 2)


def test_probe_memory_mu_sym(m=None):
    # dt = tau = 1/2, alpha = al = 2**-1/2, mu = 1, B0 = 0, z_ij = i for all i, j (as probe_dt).
    # C0 = [[0, 1], [0, 0]]: NEW C01 = al + (1-al) i, C10 = (1-al) i.
    c = cfg(dt=0.5, tau=0.5, mu=1.0, m=m)
    al = 2.0 ** -0.5
    st, R, info = step(c, m=m, theta=[PI / 2, PI / 2], history=[[0.0, 0.0], [PI / 2, PI / 2]],
                       C0=[[0.0, 1.0], [0.0, 0.0]])
    assert close(st.coherence_acc[0, 1], al + (1.0 - al) * 1j)
    a01 = math.hypot(al, 1.0 - al)
    r = 0.5 * (a01 + (1.0 - al))
    # Symmetrised R; dropping the memory term would give 1-al, no symmetrisation R01 = a01.
    assert close(R, xo(r))
    assert abs(r - (1.0 - al)) > 0.1 and abs(r - a01) > 0.1
    # drive = (eta+mu) R - mu = 5r - 1; preM = dt*drive ~ 0.823 < cap: no projection.
    b = 0.5 * (5.0 * r - 1.0)
    assert info["pre_violation"] is False
    assert close(st.B, xo(b))
    # Without mu: 0.5*4r ~ 1.058 (projected). Without the -mu offset: 0.5*5r ~ 1.32.
    assert close(st.theta, [PI / 2 - 0.5 * b] * 2)


def test_probe_clip(m=None):
    # As probe_dt with mu = 4: drive = 8(1-al) - 4 < 0, so B is clipped to 0 and theta stays put.
    c = cfg(dt=0.5, tau=0.5, mu=4.0, m=m)
    al = 2.0 ** -0.5
    assert 8.0 * (1.0 - al) - 4.0 < -1.0
    st, R, info = step(c, m=m, theta=[PI / 2, PI / 2], history=[[0.0, 0.0], [PI / 2, PI / 2]])
    assert close(st.B, np.zeros((2, 2)))
    assert close(st.theta, [PI / 2, PI / 2])


def test_probe_wrap(m=None):
    # omega = (1, 1), dt = tau = 1/2, constant history = theta = 2 pi - 0.1, B0 = 0.
    # z = exp(-i omega tau) => R = 1-al, sine term 0, theta = 2 pi - 0.1 + 0.5 = 2 pi + 0.4 -> 0.4.
    c = cfg(dt=0.5, tau=0.5, omega=(1.0, 1.0), m=m)
    t0 = 2.0 * PI - 0.1
    st, R, info = step(c, m=m, theta=[t0, t0], history=[[t0, t0], [t0, t0]])
    al = 2.0 ** -0.5
    assert close(st.coherence_acc[0, 1], (1.0 - al) * np.exp(-0.5j))
    assert close(st.theta, [0.4, 0.4])


# ---- production delay length (GPT-6 inbox note 2026-11-13: the probes above use a 1-step queue) ----
D50 = dict(dt=0.01, tau=0.5, delay=50)   # FROZEN_DT, FROZEN_TAU: delay_steps = round(tau/dt) = 50


def marker_history(n=51):
    # 51 pairwise-distinct phase vectors, so every slot is identifiable
    return [np.array([0.1 + 0.01 * k, 3.0 - 0.02 * k]) for k in range(n)]


def test_probe_d50_config_and_init(m=None):
    m = m or eng
    assert m.FROZEN_DELAY_STEPS == 50 and round(m.FROZEN_TAU / m.FROZEN_DT) == 50
    c = cfg(m=m, **D50)
    st = m.initialize_state(7, c)
    assert len(st.history) == 51                                  # delay_steps + 1 slots
    assert len({id(h) for h in st.history}) == 51                 # separate arrays (DynamicState copies each slot)
    assert all(np.array_equal(h, st.theta) for h in st.history)


def test_probe_d50_reads_slot0_only(m=None):
    # One step at delay 50 with nonzero B: changing slots 1..50 changes nothing, changing slot 0 changes
    # R and theta. Pins that both the C input and the sine coupling read history[0] of a 51-slot queue.
    m = m or eng
    c = cfg(m=m, gamma=0.015, omega=(1.0, 2.0), **D50)
    theta = [1.0, 2.5]
    H = marker_history()
    C0 = [[0.0, 0.5], [0.5, 0.0]]                                 # C0 != 0, so |C| depends on the input phase
    H2 = [H[0]] + [h + 0.7 for h in H[1:]]
    H3 = [H[0] + np.array([0.4, -0.3])] + H[1:]
    a, Ra, _ = step(c, theta, H, B=xo(0.1), C0=C0, m=m)
    b, Rb, _ = step(c, theta, H2, B=xo(0.1), C0=C0, m=m)
    d, Rd, _ = step(c, theta, H3, B=xo(0.1), C0=C0, m=m)
    assert close(Ra, Rb) and close(a.theta, b.theta) and close(a.B, b.B)
    assert not close(Ra, Rd) and not close(a.theta, d.theta)
    assert len(a.history) == 51 and close(a.history[-1], a.theta) and close(a.history[0], H[1])


def test_probe_d50_queue_aging(m=None):
    # eta = 0, mu = 1 keeps B = 0 (drive R - 1 <= 0, clipped), so theta_{n+1} = theta_n + dt*omega mod 2pi
    # exactly as the engine computes it. Over 120 steps from a 51-slot marker queue the queue before step n
    # must be S[n:n+51], where S = initial queue + every appended theta: the oldest slot is the phase from
    # exactly 50 steps earlier (tau/dt), the length stays 51 and the newest slot is the new theta.
    m = m or eng
    c = cfg(m=m, mu=1.0, eta=0.0, omega=(1.0, 2.0), **D50)
    H = marker_history()
    st = m.DynamicState(theta=H[-1].copy(), B=np.zeros((2, 2)),
                        coherence_acc=np.zeros((2, 2), dtype=complex), history=[h.copy() for h in H])
    S = [h.copy() for h in H]
    for n in range(120):
        assert len(st.history) == 51
        for k in range(51):
            assert np.array_equal(st.history[k], S[n + k]), (n, k)
        m.advance_state(st, c, np.random.default_rng(0), shuffle_driver=False)
        assert np.array_equal(st.B, np.zeros((2, 2)))
        S.append(st.theta.copy())
        assert np.array_equal(st.history[-1], st.theta)
    # first live delayed value: from a constant start queue, history[0] is still theta0 before step 50
    # and becomes the first appended phase before step 51
    st = m.initialize_state(3, c)
    t0 = st.theta.copy()
    for n in range(52):
        if n <= 50:
            assert np.array_equal(st.history[0], t0), n
        else:
            assert not np.array_equal(st.history[0], t0) and np.array_equal(st.history[0], first)
        m.advance_state(st, c, np.random.default_rng(0), shuffle_driver=False)
        if n == 0:
            first = st.theta.copy()


PROBES = [test_probe_d50_config_and_init, test_probe_d50_reads_slot0_only, test_probe_d50_queue_aging,
          test_probe_015_first_step_table, test_probe_delay_coupling_reads_history_oldest,
          test_probe_dt_half_no_projection, test_probe_old_B_carry_partial_step,
          test_probe_memory_mu_sym, test_probe_clip, test_probe_wrap]

# (name, exact source text, replacement, which occurrence: 0 = the only one, 1 = first of two)
MUTANTS = [
    ("sine_reads_current", "np.sin(delayed[None, :] - state.theta[:, None])",
     "np.sin(state.theta[None, :] - state.theta[:, None])"),
    ("theta_dt_omitted", "state.theta + config.dt * (omega_arr + coupling)",
     "state.theta + (omega_arr + coupling)"),
    ("phase_uses_old_B", "state.B * np.sin(", "B_previous * np.sin("),
    ("input_reads_newest", "delayed = state.history[0]", "delayed = state.history[-1]"),
    ("no_B_carry", "B_unprojected = state.B + config.dt * (", "B_unprojected = 0.0 + config.dt * ("),
    ("ema_memory_dropped", "config.alpha * state.coherence_acc + (1.0 - config.alpha) * z_inst",
     "(1.0 - config.alpha) * z_inst"),
    ("no_symmetrise_R", "result = 0.5 * (result + result.T)", "result = result"),
    ("mu_gain_dropped", "(config.eta + config.mu) * R_driver", "config.eta * R_driver"),
    ("mu_offset_dropped", "        - config.mu\n", "\n"),
    ("no_clip", "B_unprojected = np.maximum(B_unprojected, 0.0)", "B_unprojected = B_unprojected"),
    ("no_mod_2pi", "        2.0 * np.pi\n    )", "        1e300\n    )"),
    ("append_stale_theta", "state.history.append(state.theta.copy())",
     "state.history.append(state.history[-1].copy())"),
    # (Two further edits are equivalent and so are NOT in this list: `> delay_steps` instead of `> delay_steps + 1`,
    # because one pop per step keeps a 51-slot start at 51, and `theta` instead of `theta.copy()` in
    # initialize_state, because DynamicState copies every slot.)
    # The three entries below are real, counted mutants. queue_one_long and pop_newest are killed by value asserts;
    # init_one_short is killed by the 51-slot length assert in test_probe_d50_config_and_init.
    ("queue_one_long", "if len(state.history) > config.delay_steps + 1:",
     "if len(state.history) > config.delay_steps + 2:"),
    ("init_one_short", "history = [theta.copy() for _ in range(config.delay_steps + 1)]",
     "history = [theta.copy() for _ in range(config.delay_steps)]"),
    ("pop_newest", "state.history.pop(0)", "state.history.pop(-2)"),
    ("R_from_old_C", "    # Update EMA\n", "    old_abs = np.abs(state.coherence_acc)\n    # Update EMA\n"),
]


def _load_mutant(tmp_path, name, old, new):
    src = (REPO / "aief_experiment_engine_v1.py").read_text()
    n = src.count(old)
    assert n >= 1, f"{name}: anchor not found"
    if name == "R_from_old_C":
        assert n == 1
        src = src.replace(old, new, 1).replace("result = np.abs(state.coherence_acc)",
                                               "result = old_abs", 1)
    else:
        assert n == 1 or name == "input_reads_newest", f"{name}: anchor not unique"
        src = src.replace(old, new, 1)  # first occurrence (compute_R for input_reads_newest)
    f = tmp_path / f"eng_{name}.py"
    f.write_text(src)
    spec = importlib.util.spec_from_file_location(f"eng_{name}", f)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_probes_pass_on_unmodified_copy(tmp_path):
    mod = _load_mutant(tmp_path, "identity", "def advance_state(", "def advance_state(")
    for p in PROBES:
        p(m=mod)


@pytest.mark.parametrize("name,old,new", MUTANTS, ids=[x[0] for x in MUTANTS])
def test_negative_controls(tmp_path, name, old, new):
    mod = _load_mutant(tmp_path, name, old, new)
    failed = []
    for p in PROBES:
        try:
            p(m=mod)
        except (AssertionError, RuntimeError, FloatingPointError):
            failed.append(p.__name__)
    assert failed, f"mutant {name} survived every probe"
