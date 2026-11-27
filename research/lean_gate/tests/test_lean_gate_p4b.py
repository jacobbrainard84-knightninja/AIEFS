"""Lean P4b: pin the exact-rational values behind WeightUpdate.lean (port of the cycle-003 weight-update bridge of
Researcher 040282, restated on Params / stepM) against an independent exact-rational computation, check that the five
scalar statements restated in Freeze.lean agree textually with lean/AIEFFreezeCore, and pin the shape of the P4b
mutants (M24-M36) of lean_mutation_check.py without running Lean. The single exact mutation-count pin lives here
(the P4a test only asserts >= 23).

Run: /workspace/venv_req_cmp/bin/python -m pytest research/lean_gate/tests -q
"""
import re
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_mutation_check as mc  # noqa: E402

REPO = HERE.parents[2]
GATE = REPO / "lean" / "AIEFGateCore" / "AIEFGateCore"
WU = (GATE / "WeightUpdate.lean").read_text()
FZ = (GATE / "Freeze.lean").read_text()
FREEZECORE = (REPO / "lean" / "AIEFFreezeCore" / "AIEFFreezeCore" / "FreezeCore.lean").read_text()

# pE as exact rationals
DT, GAMMA, CAP, EPS = Fr(1, 100), Fr(15, 1000), Fr(19, 30), Fr(1, 10**12)
H = GAMMA * DT
L = Fr(1, 25)            # maximal drive D = (eta + mu) R - mu at R = 1 (u = D / gamma = 8/3)
BC = Fr(3, 25)
SSTAR = Fr(18999999991, 90000000000)


def envelope(s):
    return (1 - H) * CAP + DT * s


def kappa(s):
    return min(Fr(1), CAP / (envelope(s) + EPS))


def on_gap(s):
    k = kappa(s)
    return k * (DT * L) / (1 - k * (1 - H))


def test_parameters():
    assert H == Fr(3, 20000) and GAMMA * Fr(8, 3) == L and CAP == Fr(19, 30)


def _sstar_claim(s):
    """`s` is exactly 19/90 - 1e-10 and its float64 value is `float(19/90) - 1e-10` (no `or True` escape hatch)."""
    return s == Fr(19, 90) - Fr(1, 10**10) and float(s) == float(Fr(19, 90)) - 1e-10


def test_sstar_claim_is_not_vacuous():
    """The assertion in `test_threshold_is_exact_and_strict` is a real condition: it fails for a perturbed value
    (either the exact part or the float part)."""
    assert _sstar_claim(SSTAR)
    assert not _sstar_claim(SSTAR + Fr(1, 10**10))
    assert not _sstar_claim(Fr(19, 90))
    assert not _sstar_claim(Fr(18999999991, 90000000001))


def test_threshold_is_exact_and_strict():
    assert on_gap(SSTAR) == BC                                  # equality at the threshold: strict `<` fails
    assert not BC < on_gap(SSTAR)                               # false_gap_at_threshold
    eps = Fr(1, 10**9)
    assert BC < on_gap(SSTAR - eps) and not BC < on_gap(SSTAR + eps)
    assert _sstar_claim(SSTAR)                                  # exact rational and its float64 value
    assert abs(float(SSTAR / L) - 5.2777777752777775) < 1e-12   # 5.28 times the maximal drive
    assert abs(float(SSTAR / GAMMA) - 14.0740740) < 1e-6        # in u units (S / gamma)


def test_n12_five_six_neighbours():
    assert not BC < on_gap(Fr(11, 25))                          # onGap_N12_fails
    assert Fr(575, 10000) < on_gap(Fr(11, 25)) < Fr(576, 10000)  # onGap_N12_value
    assert BC < on_gap(Fr(5, 25))                               # onGap_five_neighbours
    assert not BC < on_gap(Fr(6, 25))                           # onGap_six_neighbours_fail
    assert abs(float(on_gap(Fr(11, 25))) - 0.05757575756267218) < 1e-15


def test_small_s_regime_is_kappa_one():
    s = Fr(1, 200)
    assert kappa(s) == 1 and on_gap(s) == Fr(8, 3) > BC           # onGap_of_lt


def test_iff_on_a_grid():
    for k in range(0, 60):
        s = Fr(k, 250)
        assert (BC < on_gap(s)) == (s < SSTAR)                  # onGap_iff (finite sample, not a proof)


def test_witness_instances_hypotheses():
    # witness_on_instance: Si = Sj = L = 1/25 satisfies the gap (one maximally driven neighbour)
    assert BC < on_gap(L)
    # witness_off_instance: U = 1/1000 < gamma * Bc and B0 = 1/5 > Bc
    assert Fr(1, 1000) < GAMMA * BC and Fr(1, 5) > BC


def test_ra_symmetrised_example_for_false_recurrence_no_symm():
    # symM pE (Xo 0) Xn: preM(0,1) = 1/10 + dt (0 - gamma/10) = 99985/1000000, symmetrised value 99985/2000000
    pre = Fr(1, 10) + DT * (0 - GAMMA * Fr(1, 10))
    assert pre == Fr(99985, 1000000) and pre / 2 == Fr(99985, 2000000)
    assert (1 - H) * Fr(1, 10) != pre / 2


def _norm(s):
    return " ".join(s.split())


def _stmt(src, name):
    m = re.search(rf"^(?:theorem|lemma) {re.escape(name)}\b(.*?):=", src, re.M | re.S)
    assert m, name
    return _norm(m.group(1))


def test_freeze_statements_match_freezecore():
    for name in ("upper_geom", "eventually_off", "eventually_on", "edge_eventually_off", "edge_eventually_on"):
        assert _stmt(FZ, name) == _stmt(FREEZECORE, name), name


def test_sources_have_no_banned_markers_and_credit_by_handle_only():
    for body_src in (WU, FZ):
        body = [l for l in body_src.splitlines() if not l.lstrip().startswith(("--", "/-", "*"))]
        for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern"):
            assert not any(bad in l for l in body), bad
        assert "@" not in body_src.replace("@[", "")
    assert "Researcher 040282" in WU and "b18a27d" in WU and "cycle_003" in WU


def test_p4b_mutants_shape():
    names = [m[0] for m in mc.MUTANTS]
    # 36 (M1-M36) + 2 (M57, M58: #27 Capacity follow-ups, appended after the P5 definition mutants M37-M56)
    # + 3 (M71-M73: C014 TrajectoryInvariants.lean statement mutants, see test_lean_gate_c014.py)
    # + 11 (M59-M69: P6 CoherenceMotion statement mutants, see test_lean_gate_c016.py)
    # + 6 (M87-M91, M94: FrequencyLock.lean statement mutants, see test_lean_gate_freqlock.py)
    # + 12 (M95-M106: DelayRoots.lean statement mutants, see test_lean_gate_delayroots.py)
    # + 9 (M110-M118: CommonRootSimple.lean / EngineStepRef.lean, see test_lean_gate_arena_intake.py)
    assert len(names) == 110                                     # the single exact pin (P4a test: >= 23; 105 before §18, 79 before §17, 70 before §16)
    assert names[23].startswith("M24") and names[35].startswith("M36")
    assert names[36].startswith("M57") and names[37].startswith("M58")
    assert {m[1] for m in mc.MUTANTS[23:36]} == {"WeightUpdate.lean"}
    assert {m[1] for m in mc.MUTANTS[36:38]} == {"Capacity.lean"}
    assert [m[2] for m in mc.MUTANTS[36:38]] == ["preM_between", "convex_weights_iff"]
    # the C014, P6, phase-lock and DelayRoots entries are selected by file, not by position
    assert {m[1] for m in mc.MUTANTS[38:]} == {"TrajectoryInvariants.lean", "CoherenceMotion.lean",
                                              "FrequencyLock.lean", "DelayRoots.lean",
                                              "CommonRootSimple.lean", "EngineStepRef.lean",
                                              "ReachableQueue.lean", "QueueComposition.lean", "MatrixPhaseBridge.lean", "EmaNearUnit.lean", "EmaWrapInvariant.lean", "CausalEMATracking.lean", "EMAFiniteSum.lean", "TransientBridge.lean", "TransientParameter.lean", "WindowMax.lean", "HeteroStepRef.lean", "HeteroGuard.lean",
                                              "DiscreteHalanay.lean"}
    assert len([m for m in mc.MUTANTS if m[1] == "DelayRoots.lean"]) == 12
    assert len([m for m in mc.MUTANTS if m[1] == "TrajectoryInvariants.lean"]) == 3
    assert len([m for m in mc.MUTANTS if m[1] == "CoherenceMotion.lean"]) == 11
    assert len([m for m in mc.MUTANTS if m[1] == "FrequencyLock.lean"]) == 6
    assert [m[2] for m in mc.MUTANTS[23:36]] == [
        "rowM_le_upper", "stepM_scalar_recurrence", "appliedFactor_lower", "stepM_factor_lower",
        "trajectory_symmetric", "trajectory_zero_diag", "trajectory_nonneg", "trajectory_good_of_start",
        "edge_eventually_off_from", "edge_eventually_on_from", "edge_eventually_off", "edge_eventually_on",
        "onGap_iff"]
    for m in mc.MUTANTS[23:36]:
        assert "WeightUpdate.false_" in m[5]                     # each refuted by a proved false_* theorem
