"""Lean P6: CoherenceMotion.lean (port of cycle 016 of Researcher 040282, md5 079a72f37e16e2187a913b96e28ab605): the
per-step speed limit |R_{n+1} - R_n| <= min 1 (2 (1 - alpha)) of the reported coherence R.

Without running Lean this test pins (a) that the restated statements agree with the deposit (whitespace removed; the
deposit is on branch audit-inbox under 2026-11-08_researcher-040282/.../cycle_016/CoherenceMotion.lean), (b) the closed
numbers behind the value probes against an independent exact-rational / float simulation of the EMA (zero phases, input
-1, exactly the probe data; hand-written, NOT proved against the engine), including the engine alpha
exp(-dt / T_window) = FROZEN_ALPHA read from aief_experiment_engine_v1.py, and a randomised check of the theorem itself,
(c) the scope wording demanded by Auditor Seat 002's review (ADOPT WITH NOTES: N1 speed limit only, N2 node-uniform
probes, N3 merged names, N4 float alpha), and (d) the exact shape and count of the P6 mutants (M59-M70, M79-M86; M71-M78 are C014's), their
declared value probes, the equivalence controls (E12-E15) and the typo control (T4) of lean_mutation_check.py.

Run: /workspace/venv_req_cmp/bin/python -m pytest research/lean_gate/tests -q
"""
import hashlib
import math
import random
import re
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_mutation_check as mc  # noqa: E402

REPO = HERE.parents[2]
PROJ = REPO / "lean" / "AIEFGateCore"
CM = (PROJ / "AIEFGateCore" / "CoherenceMotion.lean").read_text()
ENGINE = (REPO / "aief_experiment_engine_v1.py").read_text()
DEPOSIT_MD5 = "079a72f37e16e2187a913b96e28ab605"

# Statements of the deposit, all whitespace removed (the port only re-wraps lines and writes `1 / 2` for `1/2`).
DEPOSIT_STATEMENTS = {
    'complex_step_bounds':
        '(alpha:ℝ)(Cz:ℂ)(ha0:0≤alpha)(ha1:alpha≤1)(hz:‖z‖=1):alpha*‖C‖-(1-alpha)≤‖(alpha:ℂ)*C+((1-alpha:ℝ):ℂ)*z‖∧‖(alpha:ℂ)*C+((1-alpha:ℝ):ℂ)*z‖≤alpha*‖C‖+(1-alpha)',
    'reported_nonneg':
        '(C:V→V→ℂ)(ij:V):0≤PhaseCoherence.reportedCij',
    'reported_step_bounds':
        '(alpha:ℝ)(C:V→V→ℂ)(d:ℕ)(x0:V→ℝ)(u:ℕ→V→ℝ)(omega:V→ℝ)(tau:ℝ)(ha0:0≤alpha)(ha1:alpha≤1)(n:ℕ)(ij:V):alpha*PhaseCoherence.reportedCij-(1-alpha)≤PhaseCoherence.reported(PhaseCoherence.coherenceStepalphaCdx0uomegataun)ij∧PhaseCoherence.reported(PhaseCoherence.coherenceStepalphaCdx0uomegataun)ij≤alpha*PhaseCoherence.reportedCij+(1-alpha)',
    'reported_step_signed':
        '(alpha:ℝ)(C:V→V→ℂ)(d:ℕ)(x0:V→ℝ)(u:ℕ→V→ℝ)(omega:V→ℝ)(tau:ℝ)(ha0:0≤alpha)(ha1:alpha≤1)(n:ℕ)(ij:V):-(1-alpha)*(1+PhaseCoherence.reportedCij)≤PhaseCoherence.reported(PhaseCoherence.coherenceStepalphaCdx0uomegataun)ij-PhaseCoherence.reportedCij∧PhaseCoherence.reported(PhaseCoherence.coherenceStepalphaCdx0uomegataun)ij-PhaseCoherence.reportedCij≤(1-alpha)*(1-PhaseCoherence.reportedCij)',
    'reported_step_abs_state_bound':
        '(alpha:ℝ)(C:V→V→ℂ)(d:ℕ)(x0:V→ℝ)(u:ℕ→V→ℝ)(omega:V→ℝ)(tau:ℝ)(ha0:0≤alpha)(ha1:alpha≤1)(n:ℕ)(ij:V):|PhaseCoherence.reported(PhaseCoherence.coherenceStepalphaCdx0uomegataun)ij-PhaseCoherence.reportedCij|≤(1-alpha)*(1+PhaseCoherence.reportedCij)',
    'trace_step_bounds':
        '(alpha:ℝ)(C0:V→V→ℂ)(d:ℕ)(x0:V→ℝ)(u:ℕ→V→ℝ)(omega:V→ℝ)(tau:ℝ)(ha0:0≤alpha)(ha1:alpha≤1)(n:ℕ)(ij:V):alpha*rTracealphaC0dx0uomegataunij-(1-alpha)≤rTracealphaC0dx0uomegatau(n+1)ij∧rTracealphaC0dx0uomegatau(n+1)ij≤alpha*rTracealphaC0dx0uomegataunij+(1-alpha)',
    'trace_step_abs_state_bound':
        '(alpha:ℝ)(C0:V→V→ℂ)(d:ℕ)(x0:V→ℝ)(u:ℕ→V→ℝ)(omega:V→ℝ)(tau:ℝ)(ha0:0≤alpha)(ha1:alpha≤1)(n:ℕ)(ij:V):|rTracealphaC0dx0uomegatau(n+1)ij-rTracealphaC0dx0uomegataunij|≤(1-alpha)*(1+rTracealphaC0dx0uomegataunij)',
    'trace_step_abs_le':
        '(alpha:ℝ)(C0:V→V→ℂ)(d:ℕ)(x0:V→ℝ)(u:ℕ→V→ℝ)(omega:V→ℝ)(tau:ℝ)(ha0:0≤alpha)(ha1:alpha≤1)(hC0:∀ij,‖C0ij‖≤1)(n:ℕ)(ij:V):|rTracealphaC0dx0uomegatau(n+1)ij-rTracealphaC0dx0uomegataunij|≤2*(1-alpha)',
    'trace_step_abs_le_min':
        '(alpha:ℝ)(C0:V→V→ℂ)(d:ℕ)(x0:V→ℝ)(u:ℕ→V→ℝ)(omega:V→ℝ)(tau:ℝ)(ha0:0≤alpha)(ha1:alpha≤1)(hC0:∀ij,‖C0ij‖≤1)(n:ℕ)(ij:V):|rTracealphaC0dx0uomegatau(n+1)ij-rTracealphaC0dx0uomegataunij|≤min1(2*(1-alpha))',
    'trace_diagonal':
        '(alpha:ℝ)(C0:V→V→ℂ)(d:ℕ)(x0:V→ℝ)(u:ℕ→V→ℝ)(omega:V→ℝ)(tau:ℝ)(n:ℕ)(i:V):rTracealphaC0dx0uomegataunii=0',
    'probe_half_drop':
        ':Rval(1/2)10=1∧Rval(1/2)11=0',
    'probe_half_increase':
        ':Rval(1/2)00=0∧Rval(1/2)01=1/2',
    'factor_two_attained':
        '(alpha:ℝ)(hh:1/2≤alpha)(ha1:alpha≤1):|Rvalalpha11-Rvalalpha10|=2*(1-alpha)',
    'increase_factor_attained':
        '(alpha:ℝ)(ha1:alpha≤1):Rvalalpha01-Rvalalpha00=1-alpha',
    'probe_two_step':
        ':Rval(3/4)10=1∧Rval(3/4)12=1/8',
    'factor_one_refuted':
        ':¬|Rval(1/2)11-Rval(1/2)10|≤1-(1/2:ℝ)',
    'increase_only_abs_refuted':
        ':¬|Rval(1/2)11-Rval(1/2)10|≤(1-(1/2:ℝ))*(1-Rval(1/2)10)',
    'negative_alpha_upper_refuted':
        ':¬Rval(-1)11≤(-1:ℝ)*Rval(-1)10+(1-(-1:ℝ))',
    'alpha_gt_one_upper_refuted':
        ':¬Rval201≤(2:ℝ)*Rval200+(1-(2:ℝ))',
    'nonunit_initial_refuted':
        ':¬|Rval(1/2)31-Rval(1/2)30|≤2*(1-(1/2:ℝ))',
    'two_step_one_allowance_refuted':
        ':¬|Rval(3/4)12-Rval(3/4)10|≤2*(1-(3/4:ℝ))',
}


def _ws(s):
    return "".join(s.split())


def _stmt(src, name):
    m = re.search(rf"^theorem {re.escape(name)}\b(.*?):=", src, re.M | re.S)
    assert m, name
    return _ws(m.group(1))


# ---- (a) statements agree with the deposit ---------------------------------------------------------------------

def test_restated_statements_match_deposit():
    assert len(DEPOSIT_STATEMENTS) == 21
    for name, want in DEPOSIT_STATEMENTS.items():
        assert _stmt(CM, name) == want, name
    m = re.search(r"^def rTrace\b(.*?):=\s*(.*?)\n\n", CM, re.M | re.S)
    assert _ws(m.group(2)) == _ws("PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n) i j")
    assert _ws(m.group(1)).endswith("(n:ℕ)(ij:V):ℝ")


def test_namespace_imports_and_root_import():
    assert "import AIEFGateCore.PhaseCoherence" in CM                    # N3: merged P5 module, not the 54037ea snapshot
    assert "namespace AIEFGate.CoherenceMotion" in CM and "end AIEFGate.CoherenceMotion" in CM
    assert "Imports team module/namespace" not in CM and "flat015" not in CM   # the deposit's header comment is gone
    root = (PROJ / "AIEFGateCore.lean").read_text().split()
    assert "import AIEFGateCore.CoherenceMotion" in (PROJ / "AIEFGateCore.lean").read_text()
    assert root.count("AIEFGateCore.CoherenceMotion") == 1
    assert not re.search(r"^#print axioms", CM, re.M)                      # step 7 of check_lean_gate.sh audits everything


def test_sources_have_no_banned_markers_credit_by_handle_only():
    body = [l for l in CM.splitlines() if not l.lstrip().startswith(("--", "/-", "*"))]
    for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern"):
        assert not any(bad in l for l in body), bad
    assert "@" not in CM.replace("@[", "")                                 # no e-mail address
    assert "Researcher 040282" in CM and DEPOSIT_MD5 in CM and "cycle 016" in CM


def test_sha_sums_cover_the_new_file():
    sums = (PROJ / "AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt").read_text().splitlines()
    entry = [l for l in sums if l.endswith("AIEFGateCore/CoherenceMotion.lean")]
    assert len(entry) == 1
    assert entry[0].split()[0] == hashlib.sha256((PROJ / "AIEFGateCore" / "CoherenceMotion.lean").read_bytes()).hexdigest()
    root = [l for l in sums if l.endswith(" AIEFGateCore.lean") or l.endswith("*AIEFGateCore.lean")]
    assert root and root[0].split()[0] == hashlib.sha256((PROJ / "AIEFGateCore.lean").read_bytes()).hexdigest()


# ---- (c) review notes: scope wording ---------------------------------------------------------------------------

def test_scope_docstring_states_what_it_does_not_say():
    doc = " ".join(CM.split("-/")[1].split())                               # the module docstring (after the header)
    assert "speed limit" in doc and "NOT say" in doc
    for phrase in ("no phase structure, no delay, no `ω`, no `B`", "ANY unit input sequence", "not dynamics",
                   "does not say `R` converges"):
        assert phrase in doc, phrase
    assert "node-uniform" in doc and "probe_asym_state" in doc               # N2
    assert "float64" in doc and "exact reals" in doc.lower()                 # N4
    assert "α < 1/2" in doc                                                  # N2: the min is trivial below 1/2
    assert "0.00114" in doc and "875.4" in doc and "`876`" in doc            # the engine number and what it means
    assert "only a coarser lower bound" in doc and "coarser" in doc          # audit N2: no overclaim for the step count
    assert "sharp" not in doc and "tight" not in doc                         # nothing is claimed sharp
    assert "1214" in doc and "trace_rise_bound" in doc and "trace_fall_bound" in doc and "4031" in doc
    assert "engine_rise_half_not_before_1214" in doc and "engine_fall_zero_not_before_1214" in doc
    assert "needs at least about 875 steps to go\nfrom `0` to `1`" not in CM                      # the old, misleading wording
    assert "supplied by the owner" in doc and DEPOSIT_MD5 in doc


# ---- (b) closed numbers against an independent exact simulation ------------------------------------------------

def reported(C, i, j):
    return Fr(0) if i == j else (abs(C[i][j]) + abs(C[j][i])) / 2


def step(alpha, C, z=Fr(-1)):
    """C' = alpha C + (1 - alpha) z for every entry (real data only: zero phases, input -1)."""
    return [[alpha * C[i][j] + (1 - alpha) * z for j in range(2)] for i in range(2)]


def trace(alpha, C0, n):
    C = C0
    for _ in range(n):
        C = step(alpha, C)
    return C


def uniform(c):
    return [[Fr(c), Fr(c)], [Fr(c), Fr(c)]]


def R(alpha, C0, n):
    return reported(trace(alpha, C0, n), 0, 1)


def test_deposit_probe_values():
    h = Fr(1, 2)
    assert (R(h, uniform(1), 0), R(h, uniform(1), 1)) == (1, 0)                   # probe_half_drop
    assert (R(h, uniform(0), 0), R(h, uniform(0), 1)) == (0, Fr(1, 2))            # probe_half_increase
    q = Fr(3, 4)
    assert (R(q, uniform(1), 0), R(q, uniform(1), 2)) == (1, Fr(1, 8))            # probe_two_step
    assert abs(R(h, uniform(1), 1) - R(h, uniform(1), 0)) == 2 * (1 - h)          # factor_two_attained at 1/2
    assert abs(R(q, uniform(1), 1) - R(q, uniform(1), 0)) == 2 * (1 - q)          # ... and at 3/4
    assert R(q, uniform(0), 1) - R(q, uniform(0), 0) == 1 - q                      # increase_factor_attained
    # the refuted weakenings
    assert abs(R(h, uniform(1), 1) - R(h, uniform(1), 0)) > 1 - h                  # factor_one_refuted
    assert abs(R(h, uniform(1), 1) - R(h, uniform(1), 0)) > (1 - h) * (1 - R(h, uniform(1), 0)) + 0   # increase_only_abs_refuted
    assert abs(R(q, uniform(1), 2) - R(q, uniform(1), 0)) > 2 * (1 - q)           # two_step_one_allowance_refuted
    assert abs(R(h, uniform(3), 1) - R(h, uniform(3), 0)) > 2 * (1 - h)           # nonunit_initial_refuted
    m = Fr(-1)
    assert R(m, uniform(1), 1) > m * R(m, uniform(1), 0) + (1 - m)                 # negative_alpha_upper_refuted
    t = Fr(2)
    assert R(t, uniform(0), 1) > t * R(t, uniform(0), 0) + (1 - t)                 # alpha_gt_one_upper_refuted
    assert R(h, uniform(0), 1) > h * R(h, uniform(0), 0) + (1 - h) / 2             # half_increase_upper_refuted (M68)


def test_diagonal_probe_and_asymmetric_state_probe_values():
    h = Fr(1, 2)
    C = uniform(1)
    assert reported(C, 0, 0) == 0 and reported(trace(h, C, 1), 1, 1) == 0          # probe_diagonal_zero
    A = [[Fr(0), Fr(1)], [Fr(0), Fr(0)]]                                           # valueCA: only entry (0, 1) is 1
    assert (R(h, A, 0), R(h, A, 1)) == (Fr(1, 2), Fr(1, 4))                        # probe_asym_state
    one_sided = lambda n: abs(trace(h, A, n)[0][1])
    assert (one_sided(0), one_sided(1)) == (1, 0)                                  # what a one-sided R (M79) would read
    # N2: the node-uniform probes cannot tell the two readings apart; the asymmetric one can
    for c in (0, 1, 3):
        for n in (0, 1, 2):
            assert abs(trace(h, uniform(c), n)[0][1]) == R(h, uniform(c), n)


def _engine_alpha_exact():
    dt = float(re.search(r"^FROZEN_DT = ([0-9.]+)", ENGINE, re.M).group(1))
    block = re.search(r"^FROZEN_OMEGA = np\.array\(\[(.*?)\]", ENGINE, re.M | re.S).group(1)
    omegas = [Fr(x) for x in re.findall(r"[0-9]+\.[0-9]+", block)]
    assert len(omegas) == 12
    mean = sum(omegas) / 12
    return Fr(dt).limit_denominator(1000), mean


def test_engine_alpha_constant_and_value_probe():
    dt, mean = _engine_alpha_exact()
    assert dt == Fr(1, 100) and mean == Fr(857, 600)                               # FROZEN_DT, mean(FROZEN_OMEGA)
    assert "FROZEN_T_STAR = 25.0 / FROZEN_MEAN_OMEGA" in ENGINE and "FROZEN_T_WINDOW = FROZEN_T_STAR" in ENGINE
    assert "FROZEN_ALPHA = float(np.exp(-FROZEN_DT / FROZEN_T_WINDOW))" in ENGINE
    t_window = 25 / mean
    x = dt / t_window
    assert x == Fr(857, 1500000)                                                   # alphaE = exp(-(857/1500000))
    alpha = math.exp(-float(x))
    assert abs(alpha - 0.9994288298464774) < 1e-15                                 # FROZEN_ALPHA (float64) in the engine
    limit = 2 * (1 - alpha)
    assert 0.00114 < limit < 0.00115 and abs(limit - 0.0011423403070451865) < 1e-15   # engine_speed_limit_value
    # the Lean proof's two bounds, in exact rationals: 1 - x <= exp(-x) <= 1/(1 + x)
    lo, hi = 1 - x, 1 / (1 + x)
    assert lo <= Fr(alpha) <= hi
    assert Fr(114, 100000) < 2 * (1 - hi) and 2 * (1 - lo) < Fr(115, 100000)
    # engine_factor_two_attained / engine_step_value / engine_factor_one_refuted, float version of the simulation
    a = Fr(alpha)
    step_move = abs(R(a, uniform(1), 1) - R(a, uniform(1), 0))
    assert abs(float(step_move) - limit) < 1e-12 and float(step_move) > 1 - alpha
    assert 1 / limit > 875 and 1 / limit < 876                                     # ~875 steps for a change of size 1


def test_rise_is_slower_than_a_fall_audit_n2():
    """Audit note N2 (d551540): the 875 (really 876) steps of the per-step bound are only a coarse lower bound. From R_0 = 0
    the upper envelope gives 1 - R_n >= alpha^n, so R never reaches 1; reaching 1/2 takes at least 1214 steps
    (alpha^1213 > 1/2 > alpha^1214, the closed numbers `engine_pow_1213_gt_half` / `engine_pow_1214_lt_half`) and 0.9 at
    least 4031. Attained by the probe data (constant input -1 from C0 = 0 gives R_n = 1 - alpha^n exactly). Mirror: from
    R_0 = 1 the lower envelope gives 1 + R_n >= 2 alpha^n, so R > 0 for n <= 1213 (`engine_fall_zero_not_before_1214`),
    attained by constant input -1 from C0 = 1 (R_n = |2 alpha^n - 1|); a fall from 1 to 0 is NOT sharp at 876."""
    x = Fr(857, 1500000)
    a = math.exp(-float(x))
    assert a ** 1213 > 0.5 > a ** 1214 and 1214 == math.ceil(math.log(2) / float(x))
    assert a ** 4030 > 0.1 > a ** 4031 and 4031 == math.ceil(math.log(10) / float(x))
    assert math.log(2) / float(x) > 1213 and math.log(2) / float(x) < 1214          # 1213.2: "at least about 1213", 1214 exact
    # the same by the rise bound's own recursion and by the explicit EMA with constant input -1 from C0 = 0
    r_bound = Fr(0)
    for n in range(1, 1300):
        r_bound = Fr(a).limit_denominator(10**12) * r_bound + (1 - Fr(a).limit_denominator(10**12))  # upper envelope, R_0 = 0
        assert r_bound < 1
        if n == 1213:
            assert r_bound < Fr(1, 2)
        if n == 1214:
            assert r_bound > Fr(1, 2)
    C = complex(0)
    for n in range(1, 1215):
        C = a * C + (1 - a) * (-1)
        assert (abs(C) < 0.5) == (n <= 1213) and abs(C) < 1
    # the per-step bound alone: a change of size 1 needs at least 1/(2(1-a)) = 875.4 steps, i.e. 876 (a weak bound)
    assert math.ceil(1 / (2 * (1 - a))) == 876
    # the mirror (fall from R_0 = 1 under constant input -1, C0 = 1): R_n = |2 a^n - 1| > 0 for n <= 1213, 0 at 1214 is
    # already past the zero crossing, and the lower envelope 1 + R_n >= 2 a^n holds with equality while 2 a^n - 1 > 0
    C = complex(1)
    for n in range(1, 1215):
        C = a * C + (1 - a) * (-1)
        assert abs(C) > 0 and abs(C) >= 2 * a ** n - 1 - 1e-12 and (C.real > 0) == (n <= 1213)


def test_engine_alpha_numerator_is_pinned_exactly_audit_n3():
    """Audit note N3 (d551540): the mean-omega numerator 857 is pinned exactly. `alphaE_exact` states the equality, and the
    closed numbers alpha^1213 > 1/2 > alpha^1214 hold for the numerator 857 only among the integers: 856 and 858 each break
    one of them (see SPEC 13.4 for the Lean-side kill of both near misses)."""
    def holds(num):
        x = num / 1500000
        return math.exp(-1213 * x) > 0.5 > math.exp(-1214 * x)
    assert holds(857) and not holds(856) and not holds(858)
    assert [n for n in range(800, 900) if holds(n)] == [857]
    assert re.search(r"^theorem alphaE_exact : alphaE = Real\.exp \(-\(857/1500000\)\)", CM, re.M)
    assert {"alphaE_exact", "engine_pow_1213_gt_half", "engine_pow_1214_lt_half"} <= set(mc.VP_MOT)


def test_theorem_holds_on_random_unit_inputs():
    """trace_step_abs_le_min, trace_step_bounds and trace_step_abs_state_bound on random unit-modulus input sequences
    (any phases: the bound does not use them) and random initial C0 in the unit disk, in float64 with a tolerance."""
    rnd = random.Random(20261114)
    for _ in range(300):
        alpha = rnd.choice([rnd.random(), 0.5 + 0.5 * rnd.random(), 1 - 1e-3 * rnd.random(), 0.0, 1.0])
        n = 3
        C = [[0j] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                r, th = rnd.random(), rnd.uniform(0, 2 * math.pi)
                C[i][j] = r * complex(math.cos(th), math.sin(th))
        rep = lambda M, i, j: 0.0 if i == j else (abs(M[i][j]) + abs(M[j][i])) / 2
        for _ in range(8):
            z = [[complex(math.cos(t), math.sin(t)) for t in (rnd.uniform(0, 2 * math.pi) for _ in range(n))]
                 for _ in range(n)]
            C2 = [[alpha * C[i][j] + (1 - alpha) * z[i][j] for j in range(n)] for i in range(n)]
            for i in range(n):
                for j in range(n):
                    r0, r1 = rep(C, i, j), rep(C2, i, j)
                    assert abs(r1 - r0) <= min(1.0, 2 * (1 - alpha)) + 1e-12
                    assert abs(r1 - r0) <= (1 - alpha) * (1 + r0) + 1e-12
                    assert alpha * r0 - (1 - alpha) - 1e-12 <= r1 <= alpha * r0 + (1 - alpha) + 1e-12
                assert rep(C2, i, i) == 0.0
            C = C2


# ---- (d) mutants of lean_mutation_check.py ---------------------------------------------------------------------

P6_STATEMENT = [m for m in mc.MUTANTS if m[1] == "CoherenceMotion.lean"]       # selected by file, not by position
P6_DEF = [m for m in mc.DEF_MUTANTS if m[1] == "CoherenceMotion.lean"]
P6_EQUIV = [c for c in mc.EQUIV_CONTROLS if c[1] == "CoherenceMotion.lean"]
P6_TYPO = [c for c in mc.TYPO_CONTROLS if c[1] == "CoherenceMotion.lean"]


def test_p6_mutants_exact_counts_and_numbering():
    assert len(P6_STATEMENT) == 11 and len(P6_DEF) == 9
    assert [int(m[0].split("_")[0][1:]) for m in P6_STATEMENT] == list(range(59, 70))
    assert [int(m[0].split("_")[0][1:]) for m in P6_DEF] == [70] + list(range(79, 87))
    assert all(m[1] == "CoherenceMotion.lean" for m in P6_STATEMENT)
    assert {m[0] for m in mc.MUTANTS if m[1] != "CoherenceMotion.lean"}.isdisjoint({m[0] for m in P6_STATEMENT})
    # numbering: M59-M70 are numbered after M58, M79-M86 after C014's M71-M78 (C014 owns M71-M78, E11)
    nums = lambda ms: [int(m[0].split("_")[0][1:]) for m in ms]
    c014 = nums([m for m in mc.MUTANTS + mc.DEF_MUTANTS if m[1] == "TrajectoryInvariants.lean"])
    assert sorted(c014) == list(range(71, 79)) and not set(c014) & set(nums(P6_STATEMENT) + nums(P6_DEF))
    allnums = nums(mc.MUTANTS) + nums(mc.DEF_MUTANTS)
    # the phase-lock port (FrequencyLock.lean, SPEC §14) is numbered after P6: M87-M94, E16
    lock = nums([m for m in mc.MUTANTS + mc.DEF_MUTANTS if m[1] == "FrequencyLock.lean"])
    assert sorted(lock) == list(range(87, 95)) + [107, 108, 109]   # M107-M109: #41 note 1, after DelayRoots
    # the DelayRoots port (DelayRoots.lean, SPEC §15) is numbered after the phase lock: M95-M106
    roots = nums([m for m in mc.MUTANTS + mc.DEF_MUTANTS if m[1] == "DelayRoots.lean"])
    assert sorted(roots) == list(range(95, 107))
    # the Arena cycle 13/21 intake (CommonRootSimple.lean, EngineStepRef.lean, SPEC §16): M110-M129
    arena = nums([m for m in mc.MUTANTS + mc.DEF_MUTANTS if m[1] in ("CommonRootSimple.lean", "EngineStepRef.lean")])
    assert sorted(arena) == list(range(110, 131))
    # the Arena bundle intake (12 modules, SPEC §17): M131-M156 statement, M157-M190 definition
    bundle = nums([m for m in mc.MUTANTS + mc.DEF_MUTANTS if m[1] in mc.FILE_OPENS])
    assert sorted(bundle) == list(range(131, 191))
    assert len(allnums) == len(set(allnums)) == 190 == len(mc.MUTANTS) + len(mc.DEF_MUTANTS)
    assert (len(mc.MUTANTS), len(mc.DEF_MUTANTS)) == (105, 85)
    assert [c[0].split("_")[0] for c in P6_EQUIV] == ["E12", "E13", "E14", "E15"]   # E11 is C014's
    eqn = [c[0].split("_")[0] for c in mc.EQUIV_CONTROLS + mc.TYPO_CONTROLS]
    assert len(eqn) == len(set(eqn)) == 27                                          # unique across ports: E1-E23, T1-T4
    assert [c[0].split("_")[0] for c in P6_TYPO] == ["T4"]
    assert mc.KNOWN_SURVIVORS == []
    allnames = [m[0] for m in mc.MUTANTS] + [m[0] for m in mc.DEF_MUTANTS] + [c[0] for c in mc.EQUIV_CONTROLS + mc.TYPO_CONTROLS]
    assert len(allnames) == len(set(allnames))


def test_p6_statement_mutants_apply_once_and_are_refuted_by_named_theorems():
    for name, f, thm, edits, closure, term, eterm in P6_STATEMENT:
        assert re.search(rf"^theorem {thm}\b", CM, re.M), name
        assert mc.mutate(CM, thm, edits) != CM, name                               # each edit matches exactly `count`
        assert closure == "{V : Type}" and eterm is None
        used = [u for u in re.findall(r"CoherenceMotion\.([A-Za-z_]+)", term) if not u.startswith("value")]
        assert used and all(re.search(rf"^theorem {u}\b", CM, re.M) for u in used), name
    by = {m[0].split("_")[0]: m for m in P6_STATEMENT}
    # the review's suggested mutant: the bound with (1 - alpha)/2 instead of 2 (1 - alpha)
    assert by["M60"][3] == [("2*(1-alpha)", "(1-alpha)/2", 1)] and by["M60"][2] == "trace_step_abs_le"
    assert by["M59"][3] == [("2*(1-alpha)", "(1-alpha)", 1)]
    assert by["M63"][2] == "trace_step_abs_le_min" and "min 1 (1-alpha)" in by["M63"][3][0][1]
    assert {by["M61"][3][0][1], by["M64"][3][0][1]} == {"(hC0 : True)"}             # unit-disk hypothesis necessary
    assert by["M66"][3][0][1] == "(ha0 : True)" and by["M67"][3][0][1] == "(ha1 : True)"   # alpha in [0, 1] necessary
    assert "(n+2)" in by["M62"][3][0][1]                                           # two steps do not share one allowance
    assert by["M69"][2] == "trace_diagonal"


def test_p6_def_mutants_pins_are_probes_and_edits_apply():
    for name, f, edits, pins in P6_DEF:
        assert mc.mutate_file(CM, edits) != CM, name
        assert pins and set(pins) <= set(mc.VP_MOT), (name, pins)
    for p in mc.VP_MOT:
        assert re.search(rf"^theorem {p}\b", CM, re.M), p
    for name, f, edits in P6_EQUIV + P6_TYPO:
        assert mc.mutate_file(CM, edits) != CM, name
    assert mc.VALUE_PROBES["CoherenceMotion.lean"] is mc.VP_MOT
    # rewrite lemmas and refutations earn no credit
    for p in mc.VP_MOT:
        assert p.startswith(("probe_", "engine_", "alphaE_exact")) and not p.endswith("_refuted")
    pins = {m[0].split("_")[0]: m[3] for m in P6_DEF}
    assert pins["M79"] == ["probe_asym_state"] and pins["M80"] == ["probe_diagonal_zero"]       # N2 and the diagonal
    assert all(pins[k] == mc.PIN_ALPHA_E for k in ("M82", "M83", "M84", "M85", "M86"))         # the engine alpha
    assert {"engine_speed_limit_value", "alphaE_exact"} <= set(mc.PIN_ALPHA_E)                   # audit N3: exact pin
    assert set(pins["M70"]) == {"probe_half_drop", "probe_half_increase", "probe_two_step", "engine_factor_two_attained"}


def test_every_new_probe_has_an_equivalence_control_and_a_mutant():
    new_probes = {"probe_asym_state", "probe_diagonal_zero", "engine_speed_limit_value", "engine_factor_two_attained",
                  "alphaE_exact", "engine_pow_1213_gt_half", "engine_pow_1214_lt_half"}
    assert new_probes <= set(mc.VP_MOT)
    credited = {p for m in P6_DEF for p in m[3]}
    assert new_probes <= credited                                                   # each is some mutant's declared pin
    eq = {c[0].split("_")[0]: c[2][0][1] for c in P6_EQUIV}
    # E12 reads reported at (j, i): same observable (reported_symm) -> must keep the rTrace probes
    assert "coherenceTrace alpha C0 d x0 u omega tau n) j i" in eq["E12"]
    # E14 writes the symmetrisation out: the control for probe_asym_state / M79
    assert "‖PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n j i‖) / 2" in eq["E14"]
    # E13 / E15 are the same real alphaE: controls for the engine-alpha probes (incl. alphaE_exact and the closed numbers)
    assert "857 / 1500000" in eq["E13"] and "15000 / 857" in eq["E15"]
    assert Fr(1, 100) / (Fr(15000, 857)) == Fr(1, 100) / (25 / Fr(857, 600)) == Fr(857, 1500000)
    assert "reportedXX" in P6_TYPO[0][2][0][1]


def test_p6_mutant_values_differ_from_the_probes():
    """The pinned probes really see the mutated readings (float, exact rationals): this is the semantic content that the
    Lean harness only observes as `probe fails to build`."""
    h, q = Fr(1, 2), Fr(3, 4)
    A = [[Fr(0), Fr(1)], [Fr(0), Fr(0)]]
    # M70: reading trace n + 1 shifts every probe
    assert R(h, uniform(1), 1) != R(h, uniform(1), 0) and R(q, uniform(1), 3) != R(q, uniform(1), 2)
    # M81: one step from C0 at every n (instead of n steps)
    assert R(q, uniform(1), 1) != R(q, uniform(1), 2)
    # M79: one-sided R reads (1, 0) on the asymmetric state, the true R is (1/2, 1/4)
    assert abs(trace(h, A, 0)[0][1]) != R(h, A, 0)
    # M80: diagonal one
    assert reported(uniform(1), 0, 0) == 0 != 1
    # M82-M86: engine alpha with dt x10, mean omega 1, flipped sign, or mean omega numerator 856/858
    for x in (Fr(857, 150000), Fr(1, 2500)):
        a = math.exp(-float(x))
        assert not (0.00114 < 2 * (1 - a) < 0.00115)
    assert not (0.00114 < 2 * (1 - math.exp(float(Fr(857, 1500000)))) < 0.00115)
    # M85 / M86 (audit N3): the near-miss numerators stay INSIDE the old range pin (0.00114 < 2(1-alpha) < 0.00115) and
    # are caught only by the closed numbers alpha^1213 > 1/2 > alpha^1214 (856: alpha^1214 > 1/2; 858: alpha^1213 < 1/2)
    for num in (856, 858):
        a = math.exp(-num / 1500000)
        assert 0.00114 < 2 * (1 - a) < 0.00115
    a856, a858 = math.exp(-856 / 1500000), math.exp(-858 / 1500000)
    assert a856 ** 1214 > 0.5 and a858 ** 1213 < 0.5
    by_name = {m[0].split("_")[0]: m for m in P6_DEF}
    assert "(856/600)" in by_name["M85"][2][0][1] and "(858/600)" in by_name["M86"][2][0][1]


def test_readme_and_spec_record_p6():
    readme = (PROJ / "README.md").read_text()
    spec = (REPO / "research" / "lean_gate" / "SPEC_P1_gate_identities.md").read_text()
    assert "CoherenceMotion.lean" in readme and "(P6)" in readme and "079a72f3" in readme
    assert "86 mutants" in readme and "M59–M69" in readme and "M70 and M79–M86" in readme
    assert re.search(r"^## 13\. P6 ", spec, re.M) and re.search(r"^## 12\. C014 ", spec, re.M)
    sec = spec[spec.index("## 13. P6"):]
    assert not re.search(r"(?<![0-9.])12\.[1-6]\b", sec), "stale 12.x cross-reference in section 13"
    for needle in (DEPOSIT_MD5, "owner-supplied", "ADOPT WITH NOTES", "speed limit", "no phase", "N1", "N2", "N3", "N4",
                   "M59", "M86", "1214", "AUD-RATELAW stays UNEXPLAINED"):
        assert needle in sec, needle
