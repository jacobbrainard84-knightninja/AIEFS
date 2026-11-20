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

Weight-path coverage (A002/R001 review of 34c44ec): every relation run also asserts that the Hebbian weight
update and the gap projection are genuinely active (B nonzero at every step, B moves, >= MIN_PROJ projection
steps), so a relation cannot pass vacuously on B = 0. States come from two sources: "random" (generic
history, random B and C) and "native" (the engine's own initialize_state with B_init_scale = 0.05 and eta = 2).
The frozen-eta native start is NOT used for relations: there B decays to 0 by step ~1190 with 0 projection
steps (C starts at 0, so (eta + mu) R - mu < 0), which would make the weight path vacuous.

Known blind spot (documented, asserted): weight-path bugs that keep the update symmetric and label-free
(Hebbian sign, eta gain, projection bound, min->max in the projection) preserve all four symmetries, so no
symmetry relation can catch them. test_weight_path_mutants asserts this honestly and asserts that the
weight-decay closed form below and/or test_engine_step_order.py's value probes do catch each one.
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

# Coverage floors for the weight path (measured counts are in the notes file).
# MIN_PROJ: projection steps per 2000-step relation run; measured 526..1998 on the configs used, so 100 is
#   a floor that only a vacuous (B ~ 0 or under-capacity) run would miss.
# MIN_B: smallest per-step max_ij B allowed; measured >= 0.04 on the configs used (B never dies out).
# MIN_B_MOVE: max_ij |B_final - B0| must exceed this; measured >= 0.11, so the weights really evolve.
MIN_PROJ = 100
MIN_B = 0.01
MIN_B_MOVE = 0.05


def circ(a, b):
    """Max wrapped angular distance |a - b| in (-pi, pi], elementwise over arrays."""
    return float(np.max(np.abs(np.angle(np.exp(1j * (np.asarray(a) - np.asarray(b)))))))


def maxabs(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def config(m=eng, eta=None, omega=None, B_init_scale=None):
    c = m.DEFAULT_MODEL_CONFIG
    kw = {} if B_init_scale is None else {"B_init_scale": B_init_scale}
    if eta is not None:
        kw["eta"] = eta
    if omega is not None:
        kw["omega"] = tuple(float(x) for x in omega)
    c = dataclasses.replace(c, **kw)
    c.validate()
    return c


def make_state(source, seed, c, m=eng):
    if source == "random":
        return random_state(seed, c, m)
    if source == "native":
        return m.initialize_state(seed, c)  # c must carry B_init_scale > 0 (see CONFIGS)
    raise AssertionError(source)


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
    B0 = st.B.copy()
    for _ in range(n):
        R, _, info = m.advance_state(st, c, rng, shuffle_driver=shuffle)
        proj += int(info["projection_active"])
        out.append((st.theta.copy(), st.B.copy(), st.coherence_acc.copy(), R.copy()))
    cov = {"proj_steps": proj, "min_step_Bmax": float(min(float(np.max(o[1])) for o in out)),
           "B_move": float(np.max(np.abs(out[-1][1] - B0))),
           "zero_offdiag_final": int(np.count_nonzero(out[-1][1] == 0.0) - len(B0))}
    return out, cov


def assert_weight_path_active(cov):
    assert cov["proj_steps"] >= MIN_PROJ, cov
    assert cov["min_step_Bmax"] >= MIN_B, cov
    assert cov["B_move"] >= MIN_B_MOVE, cov


# ---------------------------------------------------------------------------- relation checkers
# Each returns the max error of the relation; the real engine must give <= REL_TOL, and every
# negative control must give >= DETECT.

def shift_error(c, n, m=eng, shift=1.234, claimed_shift=None, seed=11, source="random", return_cov=False):
    claimed_shift = shift if claimed_shift is None else claimed_shift
    s0 = make_state(source, seed, c, m)
    b = s0.clone()
    b.theta = np.mod(b.theta + shift, TWO_PI)
    b.history = [np.mod(h + shift, TWO_PI) for h in b.history]
    ra, cov = run(s0.clone(), c, n, m)
    rb, _ = run(b, c, n, m)
    e = 0.0
    for (ta, Ba, Ca, Ra), (tb, Bb, Cb, Rb) in zip(ra, rb):
        e = max(e, circ(ta + claimed_shift, tb), maxabs(Ba, Bb), maxabs(np.abs(Ca), np.abs(Cb)), maxabs(Ra, Rb))
    return (e, cov) if return_cov else e


def perm_error(c, n, m=eng, perm_seed=7, claimed_perm=None, seed=12, source="random", return_cov=False):
    p = np.random.default_rng(perm_seed).permutation(N)
    q = p if claimed_perm is None else claimed_perm
    s0 = make_state(source, seed, c, m)
    cp = dataclasses.replace(c, omega=tuple(np.asarray(c.omega)[p].tolist()))
    b = m.DynamicState(theta=s0.theta[p], B=s0.B[np.ix_(p, p)], coherence_acc=s0.coherence_acc[np.ix_(p, p)],
                       history=[h[p] for h in s0.history])
    ra, cov = run(s0.clone(), c, n, m)
    rb, _ = run(b, cp, n, m)
    e = 0.0
    for (ta, Ba, Ca, Ra), (tb, Bb, Cb, Rb) in zip(ra, rb):
        e = max(e, circ(ta[q], tb), maxabs(Ba[np.ix_(q, q)], Bb), maxabs(Ca[np.ix_(q, q)], Cb), maxabs(Ra[np.ix_(q, q)], Rb))
    return (e, cov) if return_cov else e


def flip_error(c, n, m=eng, conj_C=True, flip_omega=True, seed=13, shuffle=False, source="random",
               return_cov=False):
    s0 = make_state(source, seed, c, m)
    cf = dataclasses.replace(c, omega=tuple((-np.asarray(c.omega) if flip_omega else np.asarray(c.omega)).tolist()))
    b = m.DynamicState(theta=np.mod(-s0.theta, TWO_PI), B=s0.B,
                       coherence_acc=np.conj(s0.coherence_acc) if conj_C else s0.coherence_acc,
                       history=[np.mod(-h, TWO_PI) for h in s0.history])
    ra, cov = run(s0.clone(), c, n, m, shuffle=shuffle)
    rb, _ = run(b, cf, n, m, shuffle=shuffle)
    e = 0.0
    for (ta, Ba, Ca, Ra), (tb, Bb, Cb, Rb) in zip(ra, rb):
        e = max(e, circ(-ta, tb), maxabs(Ba, Bb), maxabs(np.conj(Ca), Cb), maxabs(Ra, Rb))
    return (e, cov) if return_cov else e


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


def weight_decay_error(c, n, m=eng, seed=15):
    """Zero-drive weight decay: eta = mu = 0 gives B' = max(0, B - dt gamma B) = (1 - dt gamma) B (no clip since
    B >= 0 and dt gamma = 1.5e-4 < 1; row sums only shrink, so starting under capacity the projection never fires).
    Hence B_n = (1 - dt gamma)^n B0 exactly in math, for ANY phase dynamics (B never reads theta here). This is the
    one relation in the file that pins a weight-path VALUE rather than a symmetry."""
    c = dataclasses.replace(c, eta=0.0, mu=0.0)
    c.validate()
    st = random_state(seed, c, m)
    st.B = 0.5 * st.B  # max row sum ~0.3 < capacity 0.633: projection inactive by construction
    B0 = st.B.copy()
    assert float(np.max(np.sum(B0, axis=1))) < c.capacity
    out, _ = run(st, c, n, m)
    return max(maxabs(B, B0 * (1.0 - c.dt * c.gamma) ** k) for k, (_, B, _, _) in enumerate(out, start=1))


# Relation-run configurations: (id, source, eta, B_init_scale). All have an active weight path (asserted).
CONFIGS = [
    ("random_frozen_eta", "random", eng.FROZEN_ETA, None),
    ("random_eta2", "random", 2.0, None),
    ("native_init_eta2_Binit0.05", "native", 2.0, 0.05),
]
CIDS = [x[0] for x in CONFIGS]


# ---------------------------------------------------------------------------- relation tests

@pytest.mark.parametrize("cid,source,eta,binit", CONFIGS, ids=CIDS)
def test_global_phase_shift(cid, source, eta, binit):
    e, cov = shift_error(config(eta=eta, B_init_scale=binit), N_STEPS, source=source, return_cov=True)
    assert_weight_path_active(cov)
    assert e <= REL_TOL


@pytest.mark.parametrize("cid,source,eta,binit", CONFIGS, ids=CIDS)
def test_node_relabeling(cid, source, eta, binit):
    e, cov = perm_error(config(eta=eta, B_init_scale=binit), N_STEPS, source=source, return_cov=True)
    assert_weight_path_active(cov)
    assert e <= REL_TOL


def test_zero_drive_weight_decay():
    # Tolerance REL_TOL: (1 - dt gamma)^k and the engine's repeated multiply-add each round at ~1 ulp of B
    # (<= 0.03 * 2.2e-16) per step; measured 6.4e-16 over 2000 steps.
    assert weight_decay_error(config(), N_STEPS) <= REL_TOL


@pytest.mark.parametrize("mu", [None, 0.5], ids=["frozen_mu", "mu_half_clip_active"])
def test_zero_coupling_free_rotation(mu):
    # eta = 0 and B0 = 0: B' = max(0, dt(mu R - mu)) = 0 since R <= 1 when |C0| <= 1 (C0 scale 0.9 here),
    # so coupling = sum_j 0 * sin(.) = 0 and theta_n = theta0 + n dt omega (mod 2 pi). With mu > 0 the
    # max(0, .) clip is what keeps B at 0, so that branch is exercised too.
    assert zero_coupling_error(config(), N_STEPS, mu=mu) <= ZC_TOL


@pytest.mark.parametrize("cid,source,eta,binit,shuffle", [x + (False,) for x in CONFIGS] +
                         [("random_eta2_shuffle", "random", 2.0, None, True)],
                         ids=CIDS + ["random_eta2_shuffle_driver_same_rng"])
def test_omega_flip_mirrors_trajectory(cid, source, eta, binit, shuffle):
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
    c = config(eta=eta, B_init_scale=binit)
    e, cov = flip_error(c, N_STEPS, shuffle=shuffle, source=source, return_cov=True)
    assert_weight_path_active(cov)
    assert e <= REL_TOL


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


# Seed config for the determinism tests: eta = 2 and B_init_scale = 0.05 so B is nonzero and the projection
# fires at T_sim = 4 (with the frozen eta and B_init_scale, B is exactly 0 at the split and at every branch end at
# this horizon, which made 622/648 output leaves seed-independent in 34c44ec).
SEED_CFG = {"eta": 2.0, "B_init_scale": 0.05}
BRANCHES = eng.DEFAULT_PROTOCOL_CONFIG.branches


def seed_run(seed, m=eng, cfg=None):
    c = config(m=m, **(SEED_CFG if cfg is None else cfg))
    return _flatten(m.run_seed(seed, c, _small_protocol(), BRANCHES))


def run_diff(seed_a, seed_b, m=eng, cfg=None):
    """(number of differing leaves, total leaves) between two full run_seed calls (all 7 branches, incl.
    future_shuffle and the theta-randomising resets, so every rng stream is consumed)."""
    fa, fb = seed_run(seed_a, m, cfg), seed_run(seed_b, m, cfg)
    assert fa.keys() == fb.keys()
    return sum(not _bit_equal(fa[k], fb[k]) for k in fa), len(fa)


@pytest.mark.parametrize("cfg", [SEED_CFG, {}], ids=["eta2_Binit0.05", "frozen"])
def test_seed_determinism_bit_exact(cfg):
    diff, total = run_diff(20261120, 20261120, cfg=cfg)
    assert total > 100 and diff == 0


def test_seed_config_weight_path_active():
    # Coverage: the seeded run really carries weights, so the seed controls below see the B paths.
    f = seed_run(20261120)
    assert float(np.max(f["/prefix/B_at_split"])) >= MIN_B
    for br in BRANCHES:
        assert float(np.max(f[f"/branches/{br}/B_final"])) >= MIN_B, br


# What the seed controls in this engine (read from initialize_state / make_prefix_rng / make_branch_rngs /
# apply_intervention / advance_state): (i) the initial theta and (ii) the initial B (B_init_scale * U[0,1),
# symmetrised) via the prefix stream; history starts as copies of theta and C starts at 0 (not seeded);
# (iii) one branch stream per branch: future_shuffle uses it to shuffle R's edge values every step, and
# B_carrier_only / full_reset use it to redraw theta and history at the split. continue, reset_ema, reset_B and
# reset_B_ema draw nothing from their stream. The two controls below check (i)+(ii) and (iii) separately.
SEED_SENSITIVE_PREFIX = ("/prefix/theta_at_split", "/prefix/B_at_split", "/prefix/history_at_split",
                         "/prefix/coherence_acc_at_split")


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


def test_control_different_seed_changes_prefix_and_every_branch_B():
    fa, fb = seed_run(20261120), seed_run(20261121)
    for k in SEED_SENSITIVE_PREFIX + tuple(f"/branches/{br}/B_final" for br in BRANCHES):
        assert not _bit_equal(fa[k], fb[k]), k
        # not just a last-bit difference: B and theta move by far more than rounding
        assert maxabs(fa[k], fb[k]) >= DETECT, k


def test_control_branch_stream_seed_used_exactly_where_documented():
    # Same split state, branch rngs from two different seeds: only the rng-consuming branches may change.
    c = config(**SEED_CFG)
    p = _small_protocol()
    split, prefix = eng.simulate_prefix(20261120, c, p)
    ra, rb = eng.make_branch_rngs(20261120, BRANCHES), eng.make_branch_rngs(20261121, BRANCHES)
    for br in BRANCHES:
        Ba = eng.simulate_future(split.clone(), prefix, br, c, p, ra[br])["B_final"]
        Bb = eng.simulate_future(split.clone(), prefix, br, c, p, rb[br])["B_final"]
        if br in ("future_shuffle", "B_carrier_only", "full_reset"):
            assert maxabs(Ba, Bb) >= DETECT, br
        else:
            assert _bit_equal(Ba, Bb), br


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


# ---------------------------------------------------------------------------- weight-path mutants
# Bugs in the Hebbian update / projection that keep it symmetric, label-free and phase-free. Expectation
# (derived, then confirmed by run): the shift, flip and zero-coupling relations CANNOT see them, because B'
# depends on (B, R) only and R is invariant under those maps whatever the B rule is. They must instead be caught
# by the weight-decay closed form (gamma path only) or by test_engine_step_order.py's exact-value probes.
# "decay" marks the mutants the decay relation must catch; "guard" marks one only the engine's runtime gap guard
# catches (during an eta = 2 relation run); every other mutant must fail >= 1 step-order probe.
WEIGHT_MUTANTS = [
    ("hebbian_sign", "(config.eta + config.mu) * R_driver", "-(config.eta + config.mu) * R_driver", ()),
    ("eta_gain_doubled", "(config.eta + config.mu) * R_driver", "(2 * config.eta + config.mu) * R_driver", ()),
    ("gamma_sign", "- config.gamma * state.B", "+ config.gamma * state.B", ("decay",)),
    ("projection_bound_half", "config.capacity / (row_sum_pre + config.scale_epsilon)",
     "0.5 * config.capacity / (row_sum_pre + config.scale_epsilon)", ()),
    # min -> max pairs each B_ij with the LARGER row scale, so a heavy row keeps too much weight. At N = 2 (all
    # step-order probes) both row sums are equal, s_0 = s_1, and min = max: the probes cannot see it (probe gap,
    # reported in the H1 notes). It is caught only by the engine's own gap guard (RuntimeError "Gap projection
    # failed") once row sums differ, which the eta = 2 relation runs reach: "guard".
    ("projection_min_to_max", "np.minimum.outer(scale, scale)", "np.maximum.outer(scale, scale)", ("guard",)),
]


def _step_order_module():
    f = Path(__file__).with_name("test_engine_step_order.py")
    spec = importlib.util.spec_from_file_location("_h1_step_order_probes", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("name,old,new,caught", WEIGHT_MUTANTS, ids=[x[0] for x in WEIGHT_MUTANTS])
def test_weight_path_mutants(tmp_path, name, old, new, caught):
    m = _load_mutant(tmp_path, name, old, new)
    c = config(m=m)
    # Documented blind spot: symmetry relations still hold on the mutant (frozen eta, B active, projection firing).
    e, cov = shift_error(c, N_STEPS_MUT, m, return_cov=True)
    assert e <= REL_TOL, f"{name}: shift now detects a weight-path bug; update the blind-spot note"
    assert flip_error(c, N_STEPS_MUT, m) <= REL_TOL, f"{name}: flip now detects it; update the note"
    d = weight_decay_error(c, N_STEPS_MUT, m)
    if "decay" in caught:
        assert d >= DETECT, f"{name}: weight-decay relation missed it"
    else:
        assert d <= REL_TOL, f"{name}: decay relation result changed; update the note"
    if "guard" in caught:
        with pytest.raises(RuntimeError, match="Gap projection failed"):
            perm_error(config(m=m, eta=2.0), N_STEPS_MUT, m)
        return
    so = _step_order_module()
    failing = []
    for pname in sorted(n for n in dir(so) if n.startswith("test_probe_")):
        try:
            getattr(so, pname)(m=m)
        except (AssertionError, RuntimeError):
            failing.append(pname)
    assert failing, f"{name}: NO test catches this weight-path mutant"


# ---------------------------------------------------------------------------- projection-scale exact probes
PROJ_TOL = 1e-12  # each expected value is one or two float ops on short binary fractions: error <= a few ulp ~ 1e-15.


def _proj_cfg(m=eng):
    # N = 3, a = 4, q = 1, delta = 0 => capacity 4; scale_epsilon = 1 gives slack below capacity (see case A).
    # eta = mu = gamma = 0 => B_unprojected = max(0, B0 + dt*(0*R - 0 - 0*B0)) = B0 exactly, symmetric, zero diagonal.
    # omega = 0, theta = history = 0 => coupling sin(0) = 0, phases stay 0: only the projection acts.
    c = m.ModelConfig(N=3, dt=1.0, tau=1.0, omega=(0.0, 0.0, 0.0), a=4.0, q=1.0, delta=0.0, eta=0.0, mu=0.0,
                      gamma=0.0, T_window=1.0, B_c=0.0, B_init_scale=0.0, scale_epsilon=1.0)
    c.validate()
    return c


def _proj_step(B0, m=eng):
    c = _proj_cfg(m)
    z = np.zeros(3)
    st = m.DynamicState(theta=z, B=np.array(B0, dtype=float), coherence_acc=np.zeros((3, 3), dtype=complex),
                        history=[z, z])
    _, _, info = m.advance_state(st, c, np.random.default_rng(0), shuffle_driver=False)
    return st.B, info


def _sym3(b01, b02, b12):
    return np.array([[0.0, b01, b02], [b01, 0.0, b12], [b02, b12, 0.0]])


def probe_projection_case_A(m=eng):
    """All scales < 1 and DISTINCT (kills min -> max in np.minimum.outer).
    B0: b01 = b02 = 3, b12 = 5/2. Row sums r = (6, 11/2, 11/2) > cap 4 -> pre_violation, g_min_pre = 4 - 6 = -2.
    s_i = min(1, 4/(r_i + 1)): s0 = 4/7, s1 = s2 = 4/(13/2) = 8/13 (both < 1, s0 < s1).
    Engine: B_ij *= min(s_i, s_j):
      b01 = b02 = 3 * min(4/7, 8/13) = 12/7,  b12 = (5/2) * 8/13 = 20/13.
      rows (24/7, 12/7 + 20/13 = 296/91, 296/91) -> g_min = 4 - 24/7 = 4/7 >= 0 (engine guard passes).
    min->max mutant: b01 = b02 = 3 * 8/13 = 24/13 (row 0 = 48/13 < 4, so the engine guard does NOT fire and
    only these asserts can catch it); differs from 12/7 by 12/91.
    Dropping min(1, .) is equivalent here (all scales < 1); case B covers it."""
    B, info = _proj_step(_sym3(3.0, 3.0, 2.5), m)
    assert info["pre_violation"] is True and info["projection_active"] is True
    assert abs(info["g_min_pre"] - (-2.0)) < PROJ_TOL
    assert np.allclose(B, _sym3(12 / 7, 12 / 7, 20 / 13), rtol=0.0, atol=PROJ_TOL), B
    assert abs(info["g_min"] - 4 / 7) < PROJ_TOL


def probe_projection_case_B(m=eng):
    """Heavy node 0, light pair (1, 2) whose raw scales are > 1 (kills dropping min(1, .)).
    B0: b01 = b02 = 5/2, b12 = 1/4. r = (5, 11/4, 11/4); pre_violation (5 > 4), g_min_pre = -1.
    Raw 4/(r_i + 1): node 0: 4/6 = 2/3 (< 1); nodes 1, 2: 4/(15/4) = 16/15 (> 1) -> clipped to s = 1.
    Engine: b01 = b02 = (5/2) * min(2/3, 1) = 5/3, b12 = (1/4) * min(1, 1) = 1/4 (unchanged: scale >= 1 path).
      rows (10/3, 5/3 + 1/4 = 23/12, 23/12) -> g_min = 4 - 10/3 = 2/3.
    No-min(1, .) mutant: b12 = (1/4) * 16/15 = 4/15 (rows 29/15 < 4: engine guard silent, only these asserts
    catch it). (min->max here gives b01 = 5/2, row 0 = 5 > 4 and the engine guard raises; case A catches it
    by value instead.)"""
    B, info = _proj_step(_sym3(2.5, 2.5, 0.25), m)
    assert info["pre_violation"] is True and info["projection_active"] is True
    assert abs(info["g_min_pre"] - (-1.0)) < PROJ_TOL
    assert np.allclose(B, _sym3(5 / 3, 5 / 3, 0.25), rtol=0.0, atol=PROJ_TOL), B
    assert abs(info["g_min"] - 2 / 3) < PROJ_TOL


def test_projection_scale_exact_values():
    probe_projection_case_A()
    probe_projection_case_B()


PROJ_MUTANTS = [
    # (name, old, new, case whose OWN asserts must fail with AssertionError)
    ("projection_min_to_max", "np.minimum.outer(scale, scale)", "np.maximum.outer(scale, scale)", "A"),
    ("projection_no_clip_at_1", "scale = np.minimum(1.0, config.capacity / (row_sum_pre + config.scale_epsilon))",
     "scale = config.capacity / (row_sum_pre + config.scale_epsilon)", "B"),
]


def test_projection_probes_pass_on_unmodified_copy(tmp_path):
    m = _load_mutant(tmp_path, "proj_identity", "def advance_state(", "def advance_state(")
    probe_projection_case_A(m)
    probe_projection_case_B(m)


@pytest.mark.parametrize("name,old,new,case", PROJ_MUTANTS, ids=[x[0] for x in PROJ_MUTANTS])
def test_projection_scale_mutants_killed_by_own_asserts(tmp_path, name, old, new, case):
    m = _load_mutant(tmp_path, name, old, new)
    probe = probe_projection_case_A if case == "A" else probe_projection_case_B
    # AssertionError, not RuntimeError: the value asserts catch it, not the engine's capacity self-check.
    with pytest.raises(AssertionError):
        probe(m)
