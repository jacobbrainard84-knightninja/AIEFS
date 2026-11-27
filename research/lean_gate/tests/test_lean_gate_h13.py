"""Lean H13 DiscreteHalanay: pin DiscreteHalanay.lean (easy floor-exponent discrete Halanay,
namespace AIEFGate.DiscreteHalanay) and its mutants M800-M808 without running Lean.

Statement mutants (numbered from M800 so they do not collide with concurrent H9/H16 work):
  M800 discrete_halanay, 0 ≤ initMax u d := True     (M < 0: u3 = -25/36 > -5/6)
  M801 discrete_halanay, exponent n/(d+1) -> n/d     (fails at n = d on a constant window)
  M802 discrete_halanay, initMax window 0..d-1       (unique max at index d)
  M803 discrete_halanay_decay, a+b < 1 -> a+b ≤ 1    (constant sequence, no decay)
  M804 discrete_halanay, step starts at d+1 ≤ n      (unconstrained jump at n = d+1)
Definition mutants M805-M808 are killed by probe_initMax_spike / probe_windowMax_values /
probe_blockPow_values. Weakening a+b < 1 to a+b ≤ 1 on the written bound of discrete_halanay
is predicted to SURVIVE and is not registered (documented, not a decorative KNOWN_SURVIVORS entry).

The M < 0 counterexample and the other witnesses are re-checked here in exact rationals.

Run: /workspace/venv-pt/bin/pytest -q research/lean_gate/tests/test_lean_gate_h13.py
"""
import hashlib
import re
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_mutation_check as mc  # noqa: E402

REPO = HERE.parents[2]
PROJ = REPO / "lean" / "AIEFGateCore"
F = "DiscreteHalanay.lean"
SRC = (PROJ / "AIEFGateCore" / F).read_text()

STATEMENT = [
    ("M800", "discrete_halanay", "false_bound_neg_initMax"),
    ("M801", "discrete_halanay", "false_bound_wrong_exponent"),
    ("M802", "discrete_halanay", "false_bound_short_window"),
    ("M803", "discrete_halanay_decay", "false_decay_at_q_one"),
    ("M804", "discrete_halanay", "false_step_starts_late"),
]
DEF_STATEMENT = [
    ("M805", "probe_initMax_spike"),
    ("M806", "probe_windowMax_values"),
    ("M807", "probe_blockPow_values"),
    ("M808", "probe_initMax_spike"),
]


def mutants():
    return [m for m in mc.MUTANTS if m[1] == F]


def def_mutants():
    return [m for m in mc.DEF_MUTANTS if m[1] == F]


def test_module_is_imported_and_hash_pinned():
    root = (PROJ / "AIEFGateCore.lean").read_text()
    assert re.search(r"^import AIEFGateCore\.DiscreteHalanay$", root, re.M)
    sums = (PROJ / "AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt").read_text()
    digest = hashlib.sha256((PROJ / "AIEFGateCore" / F).read_bytes()).hexdigest()
    assert f"{digest}  AIEFGateCore/{F}" in sums


def test_no_escape_hatches():
    code = re.sub(r"/-.*?-/", "", SRC, flags=re.S)
    code = re.sub(r"--.*", "", code)
    for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern"):
        assert bad not in code, bad


def test_core_theorems_and_axioms_prints_exist():
    for thm in (
        "discrete_halanay", "discrete_halanay_of_nonneg", "discrete_halanay_d0",
        "discrete_halanay_d0_of_initMax", "discrete_halanay_decay", "discrete_halanay_geom",
        "probe_initMax_spike", "probe_windowMax_values", "probe_blockPow_values",
        "false_bound_neg_initMax", "false_bound_wrong_exponent", "false_bound_short_window",
        "false_step_starts_late", "false_decay_at_q_one", "block_end_succ",
    ):
        assert re.search(rf"^theorem {thm}\b", SRC, re.M), thm
    thms = re.findall(r"^theorem\s+(\S+)", SRC, re.M)
    prints = set(re.findall(r"#print axioms\s+(\S+)", SRC))
    missing = [n for n in thms if n not in prints]
    assert missing == [], missing


def test_consumer_caveat_and_zero_le_M_correction():
    assert "Not progress on O1; no engine claim." in SRC
    assert "Researcher 001 suggested dropping" in SRC
    assert "0 ≤ initMax u d" in SRC
    assert "signed-sample probe" in SRC
    assert "too weak to find this" in SRC
    assert "Correction, not blame." in SRC
    # predicted SURVIVE of a+b ≤ 1 on the written bound is documented, not registered
    assert "predicted to **SURVIVE**" in SRC
    assert not any(m[1] == F for m in mc.KNOWN_SURVIVORS)
    assert "DiscreteHalanay.lean" not in mc.FILE_OPENS


def test_statement_mutants_exact_shape():
    ms = mutants()
    assert [m[0].split("_")[0] for m in ms] == [s[0] for s in STATEMENT]
    for (num, thm, refuter), (name, f, t, edits, closure, term, engine) in zip(STATEMENT, ms):
        assert t == thm and closure == "" and engine is None, name
        assert mc.mutate(SRC, t, edits) != SRC, name
        assert re.search(rf"^theorem {refuter}\b", SRC, re.M), (name, refuter)
        assert term == f"DiscreteHalanay.{refuter} H", name


def test_definition_mutants_exact_shape():
    ms = def_mutants()
    assert [m[0].split("_")[0] for m in ms] == [s[0] for s in DEF_STATEMENT]
    for (num, pin), (name, f, edits, pins) in zip(DEF_STATEMENT, ms):
        assert f == F and pin in pins and set(pins) <= set(mc.VALUE_PROBES[F]), name
        assert mc.mutate_file(SRC, edits) != SRC, name
        assert re.search(rf"^theorem {pin}\b", SRC, re.M), (name, pin)


def test_mutated_statements_change_only_the_named_hypothesis():
    for name, f, t, edits, closure, term, engine in mutants():
        before = mc.statement_prop(SRC, t, closure)
        after = mc.statement_prop(mc.mutate(SRC, t, edits), t, closure)
        assert before != after, name
        assert len(edits) == 1 and edits[0][2] == 1, name


def test_neg_initMax_counterexample_exact():
    """M < 0: d=1, u0=u1=-1, u2=-q, u3=-q^2, q=a+b=5/6. The written bound at n=3 is M q^(3//2)= -q."""
    a, b = Q(1, 2), Q(1, 3)
    q = a + b
    assert q == Q(5, 6) and 0 < q < 1
    u0 = u1 = Q(-1)
    M = max(u0, u1)
    assert M == Q(-1)
    u2 = -q
    u3 = -q * q
    assert u2 == Q(-5, 6) and u3 == Q(-25, 36)
    # delayed equality at n=1: u2 = a u1 + b max(u0, u1)
    assert u2 == a * u1 + b * max(u0, u1)
    # delayed equality at n=2: u3 = a u2 + b max(u1, u2)
    assert u3 == a * u2 + b * max(u1, u2)
    bound = M * q ** (3 // 2)
    assert bound == M * q == Q(-5, 6)
    assert u3 > bound
    assert u3 - bound == Q(5, 36)


def test_wrong_exponent_and_short_window_and_decay_controls_exact():
    a, b = Q(1, 2), Q(1, 3)
    q = a + b
    # n/d at n=d=1 on a constant initial window u=1: 1 ≤ q^1 fails
    assert Q(1) > q ** (1 // 1)
    # short window 0..d-1 with unique max at d=1: initMax on {0} is 0, bound at n=1 is 0
    assert Q(1) > Q(0) * q ** (1 // 2)
    # a+b=1, constant u≡1: the written bound is 1, but any ρ<1 fails at n=d+1
    rho = Q(999, 1000)
    assert Q(1) > Q(1) * rho ** (2 // 2)
    # production exponents: 50/51 = 0, 51/51 = 1; n/d would give 50/50 = 1
    assert 50 // 51 == 0 and 51 // 51 == 1 and 50 // 50 == 1
    assert (Q(5, 6) ** (50 // 51) == 1) and (Q(5, 6) ** (50 // 50) == Q(5, 6))
