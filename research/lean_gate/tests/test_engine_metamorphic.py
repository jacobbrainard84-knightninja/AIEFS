"""H1 metamorphic tests for aief_experiment_engine_v1.py (truthfulness hardening plan, 2026-11-20).

These tests run the real, SHA-locked engine (it is imported, never edited) and check relations that
follow from its update equations, not tuned numbers. One advance_state step is, with
abar_ij = (omega_i + omega_j) / 2 and d = history[0] (the delayed phases):

  (E1) dphi_ij = theta_i - d_j - abar_ij * tau,      z_ij = exp(i dphi_ij)
  (E2) C'      = alpha C + (1 - alpha) z
  (E3) R       = sym(|C'|) with zero diagonal         (R_driver = R, or a seeded shuffle of R's edges)
  (E4) B'      = proj(sym(max(0, B + dt((eta + mu) R_driver - mu - gamma B))))
               proj: if min_i(a - q rowsum_i) < delta, B'_ij *= min(s_i, s_j), s_i = min(1, cap/(rowsum_i+eps))
  (E5) theta'_i = (theta_i + dt(omega_i + sum_j B'_ij sin(d_j - theta_i))) mod 2 pi
  (E6) history.append(theta'); history.pop(0)

Relations tested (all with shuffle_driver=False except where stated):
  1. global phase shift      theta, history -> +c       => theta(t) -> theta(t) + c, B, |C|, R unchanged
  2. node relabeling         permute every node-indexed object => every output permuted the same way
  3. zero coupling           B0 = 0, eta = 0            => B stays 0 and theta(t) = theta0 + omega t (mod 2 pi)
  4. omega flip              theta, history -> -theta, omega -> -omega, C -> conj(C), B unchanged
                             => mirrored trajectory (derivation in test_omega_flip_mirrors_trajectory)
  5. seed determinism        same seed => bit-identical run_seed output; different seed => different output

Only 5 is bit-exact. 1-4 compare circularly (wrapped angle difference) with a written tolerance.
Negative controls: each relation is also checked against (a) a deliberately wrong reference
(wrong shift, wrong permutation, missing conj, changed seed) and (b) one-line mutants of a temporary
copy of the engine; every control must be DETECTED (error above tolerance / outputs differ).
"""
import dataclasses
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
import aief_experiment_engine_v1 as eng  # noqa: E402

TWO_PI = 2.0 * math.pi
N = eng.FROZEN_N
N_STEPS = 2000  # 20 time units at dt = 0.01: 40 delay lengths (tau = 0.5) and > 1 EMA window.
N_STEPS_MUT = 400  # shorter horizon for the mutant controls; every mutant is caught well within it.

# Tolerance for relations 1, 2, 4 (radians for theta; absolute for B, |C|, R).
# Reason: mathematically these relations are exact; in floats the transformed run differs only by
# rounding (theta + c and mod 2 pi round at ~ulp(2 pi) = 8.9e-16; permuted row sums change summation
# order; mod(-theta, 2 pi) rounds). Scratch runs (notes file) over 2000 steps measured at most
# 4.1e-13 (eta = 2, projection firing every step) and 2.5e-14 (frozen config). 1e-10 leaves >= 240x
# margin over the worst measured value, while every negative control below errs by >= 1e-5.
REL_TOL = 1e-10

# Tolerance for relation 3 (closed form theta0 + n dt omega vs the engine's iterated mod-2pi sums).
# Reason: per step the engine rounds once in the add and once in np.mod, each <= ulp(2 pi + dt|omega|)
# ~ 8.9e-16, so after n = 2000 steps the drift is <= ~2 * 2000 * 8.9e-16 = 3.6e-12 (measured 3.0e-13).
# 1e-10 is > 25x the analytic bound. (The step-by-step recursion itself matches bit for bit, which the
# notes report; the test uses the closed form so it checks the physics, not the code against itself.)
ZC_TOL = 1e-10

# Minimum error a negative control must show to count as DETECTED: well above REL_TOL.
DETECT = 1e3 * REL_TOL


def circ(a, b):
    """Max wrapped angular distance |a - b| in (-pi, pi], elementwise over arrays."""
    return float(np.max(np.abs(np.angle(np.exp(1j * (np.asarray(a) - np.asarray(b)))))))


def maxabs(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def config(m=eng, eta=None, omega=None):
    c = m.DEFAULT_MODEL_CONFIG
    kw = {}
    if eta is not None:
        kw["eta"] = eta
    if omega is not None:
        kw["omega"] = tuple(float(x) for x in omega)
    c = dataclasses.replace(c, **kw)
    c.validate()
    return c


def random_state(seed, c, m=eng, B_scale=0.05, C_scale=0.9):
    """Generic (non-symmetric-phase) state: random theta, a non-constant 51-slot history whose newest
    slot equals theta, random symmetric nonnegative B with zero diagonal, random complex C with |C| < 1."""
    rng = np.random.default_rng(seed)
    th = rng.random(N) * TWO_PI
    hist = [np.mod(th + 0.3 * rng.standard_normal(N), TWO_PI) for _ in range(c.delay_steps)] + [th.copy()]
    B = rng.random((N, N)) * B_scale
    B = 0.5 * (B + B.T)
    np.fill_diagonal(B, 0.0)
    C = C_scale * rng.random((N, N)) * np.exp(1j * TWO_PI * rng.random((N, N)))
    return m.DynamicState(theta=th, B=B, coherence_acc=C, history=hist)


def run(st, c, n, m=eng, shuffle=False, rng_seed=0):
    """Advance n steps; return per-step (theta, B, C, R) and the number of projection steps."""
    rng = np.random.default_rng(rng_seed)
    out, proj = [], 0
    for _ in range(n):
        R, _, info = m.advance_state(st, c, rng, shuffle_driver=shuffle)
        proj += int(info["projection_active"])
        out.append((st.theta.copy(), st.B.copy(), st.coherence_acc.copy(), R.copy()))
    return out, proj


# ---------------------------------------------------------------------------- relation checkers
# Each returns the max error of the relation; the real engine must give <= REL_TOL, and every
# negative control must give >= DETECT.

def shift_error(c, n, m=eng, shift=1.234, claimed_shift=None, seed=11):
    claimed_shift = shift if claimed_shift is None else claimed_shift
    s0 = random_state(seed, c, m)
    b = s0.clone()
    b.theta = np.mod(b.theta + shift, TWO_PI)
    b.history = [np.mod(h + shift, TWO_PI) for h in b.history]
    ra, _ = run(s0.clone(), c, n, m)
    rb, _ = run(b, c, n, m)
    e = 0.0
    for (ta, Ba, Ca, Ra), (tb, Bb, Cb, Rb) in zip(ra, rb):
        e = max(e, circ(ta + claimed_shift, tb), maxabs(Ba, Bb), maxabs(np.abs(Ca), np.abs(Cb)), maxabs(Ra, Rb))
    return e


def perm_error(c, n, m=eng, perm_seed=7, claimed_perm=None, seed=12):
    p = np.random.default_rng(perm_seed).permutation(N)
    q = p if claimed_perm is None else claimed_perm
    s0 = random_state(seed, c, m)
    cp = dataclasses.replace(c, omega=tuple(np.asarray(c.omega)[p].tolist()))
    b = m.DynamicState(theta=s0.theta[p], B=s0.B[np.ix_(p, p)], coherence_acc=s0.coherence_acc[np.ix_(p, p)],
                       history=[h[p] for h in s0.history])
    ra, _ = run(s0.clone(), c, n, m)
    rb, _ = run(b, cp, n, m)
    e = 0.0
    for (ta, Ba, Ca, Ra), (tb, Bb, Cb, Rb) in zip(ra, rb):
        e = max(e, circ(ta[q], tb), maxabs(Ba[np.ix_(q, q)], Bb), maxabs(Ca[np.ix_(q, q)], Cb), maxabs(Ra[np.ix_(q, q)], Rb))
    return e


def flip_error(c, n, m=eng, conj_C=True, flip_omega=True, seed=13, shuffle=False):
    s0 = random_state(seed, c, m)
    cf = dataclasses.replace(c, omega=tuple((-np.asarray(c.omega) if flip_omega else np.asarray(c.omega)).tolist()))
    b = m.DynamicState(theta=np.mod(-s0.theta, TWO_PI), B=s0.B,
                       coherence_acc=np.conj(s0.coherence_acc) if conj_C else s0.coherence_acc,
                       history=[np.mod(-h, TWO_PI) for h in s0.history])
    ra, _ = run(s0.clone(), c, n, m, shuffle=shuffle)
    rb, _ = run(b, cf, n, m, shuffle=shuffle)
    e = 0.0
    for (ta, Ba, Ca, Ra), (tb, Bb, Cb, Rb) in zip(ra, rb):
        e = max(e, circ(-ta, tb), maxabs(Ba, Bb), maxabs(np.conj(Ca), Cb), maxabs(Ra, Rb))
    return e


def zero_coupling_error(c, n, m=eng, seed=14, mu=None):
    c = dataclasses.replace(c, eta=0.0, **({} if mu is None else {"mu": mu}))
    c.validate()
    st = random_state(seed, c, m)
    st.B = np.zeros((N, N))
    th0 = st.theta.copy()
    w = np.asarray(c.omega)
    out, _ = run(st, c, n, m)
    e = 0.0
    for k, (th, B, _, _) in enumerate(out, start=1):
        e = max(e, circ(th, th0 + k * c.dt * w), float(np.max(np.abs(B))))
    return e


# ---------------------------------------------------------------------------- relation tests

@pytest.mark.parametrize("eta", [eng.FROZEN_ETA, 2.0], ids=["frozen_eta", "eta2_projection_every_step"])
def test_global_phase_shift(eta):
    c = config(eta=eta)
    assert shift_error(c, N_STEPS) <= REL_TOL


@pytest.mark.parametrize("eta", [eng.FROZEN_ETA, 2.0], ids=["frozen_eta", "eta2_projection_every_step"])
def test_node_relabeling(eta):
    c = config(eta=eta)
    assert perm_error(c, N_STEPS) <= REL_TOL


@pytest.mark.parametrize("mu", [None, 0.5], ids=["frozen_mu", "mu_half_clip_active"])
def test_zero_coupling_free_rotation(mu):
    # eta = 0 and B0 = 0: B' = max(0, dt(mu R - mu)) = 0 since R <= 1 when |C0| <= 1 (C0 scale 0.9 here),
    # so coupling = sum_j 0 * sin(.) = 0 and theta_n = theta0 + n dt omega (mod 2 pi). With mu > 0 the
    # max(0, .) clip is what keeps B at 0, so that branch is exercised too.
    assert zero_coupling_error(config(), N_STEPS, mu=mu) <= ZC_TOL


@pytest.mark.parametrize("eta,shuffle", [(eng.FROZEN_ETA, False), (2.0, False), (2.0, True)],
                         ids=["frozen_eta", "eta2_projection_every_step", "eta2_shuffle_driver_same_rng"])
def test_omega_flip_mirrors_trajectory(eta, shuffle):
    """Derivation (from the engine's actual equations E1-E6 above), map S:
       theta -> -theta (mod 2pi), every history slot -> -slot (mod 2pi), omega -> -omega, C -> conj(C), B -> B.
    E1: dphi^S_ij = -theta_i + d_j + abar_ij tau = -dphi_ij (abar is linear in omega, so it flips too),
        hence z^S = conj(z). Reducing mod 2pi first only adds multiples of 2pi, which exp ignores.
    E2: C'^S = alpha conj(C) + (1 - alpha) conj(z) = conj(C') (alpha real).
    E3: |conj(C')| = |C'|, so R^S = R. The shuffle permutes R's edge values with the rng only, so with
        the same rng seed R_driver^S = R_driver as well.
    E4: B' depends only on B and R_driver (no phase, no omega), so B'^S = B'; the projection is a function
        of B_unprojected only, so it fires identically.
    E5: theta'^S_i = -theta_i + dt(-omega_i + sum_j B'_ij sin(-d_j + theta_i))
                   = -(theta_i + dt(omega_i + sum_j B'_ij sin(d_j - theta_i)))   (sin odd)
        = -theta'_i, and mod 2pi preserves this circularly.
    E6: the appended slot is -theta', so the history stays mirrored and the induction continues.
    No noise term enters the step, gap/clip/projection act on B only, and every phase enters through an
    odd (sin) or conjugating (exp) map, so the relation HOLDS for this engine: not xfail.
    (The relation needs omega -> -omega: the phase advance dt*omega is not odd in theta alone. The
    control flip_omega=False below confirms the check sees that.)
    """
    c = config(eta=eta)
    assert flip_error(c, N_STEPS, shuffle=shuffle) <= REL_TOL


def _small_protocol():
    return eng.ProtocolConfig(T_sim=4.0, burn_end_time=1.0, split_time=2.0, future_duration=2.0,
                              diagnostic_stride=50, branches=eng.DEFAULT_PROTOCOL_CONFIG.branches)


def _flatten(obj, prefix=""):
    """Flatten a run_seed result into {path: value} for exact comparison."""
    out = {}
    if isinstance(obj, dict):
        for k in sorted(obj, key=str):
            out.update(_flatten(obj[k], f"{prefix}/{k}"))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            out.update(_flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def _bit_equal(a, b):
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        a, b = np.asarray(a), np.asarray(b)
        return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()
    if isinstance(a, float) and isinstance(b, float):
        return np.float64(a).tobytes() == np.float64(b).tobytes()  # NaN == NaN bitwise, -0.0 != 0.0
    return type(a) is type(b) and a == b


def run_diff(seed_a, seed_b, m=eng):
    """Number of differing leaves between two full run_seed calls (all 7 branches, incl. future_shuffle
    and the theta-randomising resets, so every rng stream is consumed)."""
    c = config(m=m)
    p = _small_protocol()
    fa = _flatten(m.run_seed(seed_a, c, p, eng.DEFAULT_PROTOCOL_CONFIG.branches))
    fb = _flatten(m.run_seed(seed_b, c, p, eng.DEFAULT_PROTOCOL_CONFIG.branches))
    assert fa.keys() == fb.keys()
    return sum(not _bit_equal(fa[k], fb[k]) for k in fa), len(fa)


def test_seed_determinism_bit_exact():
    diff, total = run_diff(20261120, 20261120)
    assert total > 100 and diff == 0


# ---------------------------------------------------------------------------- negative controls

def test_control_wrong_shift_detected():
    assert shift_error(config(), N_STEPS_MUT, claimed_shift=1.234 + 1e-5) >= DETECT


def test_control_wrong_permutation_detected():
    p = np.random.default_rng(7).permutation(N)
    q = p.copy()
    q[[0, 1]] = q[[1, 0]]  # one transposition away from the true relabeling
    assert perm_error(config(), N_STEPS_MUT, claimed_perm=q) >= DETECT


def test_control_flip_without_conj_detected():
    assert flip_error(config(), N_STEPS_MUT, conj_C=False) >= DETECT


def test_control_flip_without_omega_flip_detected():
    assert flip_error(config(), N_STEPS_MUT, flip_omega=False) >= DETECT


def test_control_different_seed_detected():
    diff, total = run_diff(20261120, 20261121)
    assert diff > 0


# One-line mutants of a temporary copy of the engine. Each names the relation(s) it must break.
# The mutants model realistic bug classes: an absolute-phase dependence, a label-dependent term,
# a phase lag that breaks odd symmetry, coupling leakage when B = 0, and unseeded randomness.
MUTANTS = [
    # absolute phase enters the drive: breaks the shift relation (sin(theta) is odd, so flip survives it)
    ("abs_phase_in_drive", "state.theta + config.dt * (omega_arr + coupling)",
     "state.theta + config.dt * (omega_arr + coupling + 0.01 * np.sin(state.theta))", ("shift",)),
    # absolute phase enters the coherence input
    ("abs_phase_in_coherence", "z_inst = np.exp(1j * dphi)",
     "z_inst = np.exp(1j * (dphi + 0.1 * np.cos(state.theta[:, None])))", ("shift", "flip")),
    # node 0 gets a label-dependent kick: breaks relabeling
    ("label_dependent_kick", "coupling = np.sum(",
     "coupling = np.eye(len(state.theta))[0] * 0.01 + np.sum(", ("perm",)),
    # projection scale paired with the wrong (reversed) row: breaks relabeling
    ("projection_scale_reversed", "np.minimum.outer(scale, scale)",
     "np.minimum.outer(scale, scale[::-1])", ("perm",)),
    # Sakaguchi-type phase lag: shift- and label-equivariant but not odd, so it must break the flip
    ("phase_lag_in_coupling", "np.sin(delayed[None, :] - state.theta[:, None])",
     "np.sin(delayed[None, :] - state.theta[:, None] + 0.3)", ("flip",)),
    # coupling leaks through when B = 0
    ("coupling_leak", "state.B * np.sin(delayed", "(state.B + 1e-3) * np.sin(delayed", ("zero",)),
    # phase advance without dt
    ("theta_dt_omitted", "state.theta + config.dt * (omega_arr + coupling)",
     "state.theta + (omega_arr + coupling)", ("zero",)),
    # unseeded entropy in initialisation: breaks determinism
    ("unseeded_init", "theta = rng.random(N) * 2.0 * np.pi\n    \n    # Initialize B",
     "theta = np.random.default_rng().random(N) * 2.0 * np.pi\n    \n    # Initialize B", ("seed",)),
]


def _load_mutant(tmp_path, name, old, new):
    src = (REPO / "aief_experiment_engine_v1.py").read_text()
    assert src.count(old) >= 1, f"mutant {name}: anchor not found (engine changed?)"
    src = src.replace(old, new, 1)
    f = tmp_path / f"eng_meta_{name}.py"
    f.write_text(src)
    spec = importlib.util.spec_from_file_location(f"eng_meta_{name}", f)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses needs the module registered
    spec.loader.exec_module(mod)
    return mod


def _relation_error(rel, m):
    c = config(m=m)
    if rel == "shift":
        return shift_error(c, N_STEPS_MUT, m)
    if rel == "perm":
        # eta = 2 so the projection fires every step (projection_scale_reversed is only visible then)
        return perm_error(config(m=m, eta=2.0), N_STEPS_MUT, m)
    if rel == "flip":
        return flip_error(c, N_STEPS_MUT, m)
    if rel == "zero":
        return zero_coupling_error(c, N_STEPS_MUT, m)
    raise AssertionError(rel)


def test_relations_hold_on_unmodified_copy(tmp_path):
    m = _load_mutant(tmp_path, "identity", "def advance_state(", "def advance_state(")
    for rel in ("shift", "perm", "flip", "zero"):
        assert _relation_error(rel, m) <= REL_TOL, rel
    assert run_diff(5, 5, m)[0] == 0


@pytest.mark.parametrize("name,old,new,rels", MUTANTS, ids=[x[0] for x in MUTANTS])
def test_negative_control_mutants(tmp_path, name, old, new, rels):
    m = _load_mutant(tmp_path, name, old, new)
    for rel in rels:
        if rel == "seed":
            assert run_diff(5, 5, m)[0] > 0, f"{name}: same seed still bit-identical"
        else:
            assert _relation_error(rel, m) >= DETECT, f"{name}: relation {rel} not broken"
