"""Lean DelayRoots: pin DelayRoots.lean (root lemmas for the delay characteristic polynomials of
Arena_Researcher_06020041 cycles 9/10, namespace AIEFGate.DelayRoots) and its mutants without running Lean.

Statement mutants (numbered from M95; selected by file, so later ports can append):
  M95 symRoot_eq_one_or_lt ha1 (a < 1) := True          (a = 2, d = 1: root -2)
  M96 symRoot_eq_one_or_lt drops the neutral root `z = 1 ∨` (the root 1 itself)
  M97 transRoot_lt_one hm (1 ≤ m) := True               (m = 0, h = 3, d = 0: root -2)
  M98 transRoot_lt_one hmh (m h < 1) := True            (m = h = 1, d = 0: root -1)
  M99 projectedSlope_lt_quarter `C < x` -> `C ≤ x`      (C = ε = x = 1: slope 1/4)
  M100 symRoot_eq_one_or_lt ha0 (0 < a) := True          (a = -2, d = 1: root 2)
  M101 transRoot_lt_one h0 (0 < h) := True               (m = 1, h = 0, d = 0: root 1)
  M102 symRoot_eq_one_or_lt `a < 1` -> `a ≤ 1`           (a = 1, d = 1: root -1)
  M103 transRoot_lt_one `m h < 1` -> `m h ≤ 1`          (m = h = 1, d = 1: root i)
  M104 projectedSlope_lt_quarter 0 < C, 0 < ε := True   (C = ε = -1, x = -1/2: slope 4/9)
The witness roots are re-checked here in exact arithmetic (Gaussian integers / rationals).

Run: /workspace/venv-pt/bin/pytest -q research/lean_gate/tests/test_lean_gate_delayroots.py
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
F = "DelayRoots.lean"
SRC = (PROJ / "AIEFGateCore" / F).read_text()

STATEMENT = [("M95", "symRoot_eq_one_or_lt", "false_symRoot_no_upper", "symRoot_root_a_two"),
             ("M96", "symRoot_eq_one_or_lt", "false_one_inside", "symRoot_one"),
             ("M97", "transRoot_lt_one", "false_minus_two_inside", "transRoot_root_m_zero"),
             ("M98", "transRoot_lt_one", "false_minus_one_inside", "transRoot_root_mh_one"),
             ("M99", "projectedSlope_lt_quarter", "false_slope_at_boundary", None),
             ("M100", "symRoot_eq_one_or_lt", "false_symRoot_two", "symRoot_root_a_neg_two"),
             ("M101", "transRoot_lt_one", "false_one_inside", "transRoot_root_h_zero"),
             ("M102", "symRoot_eq_one_or_lt", "false_symRoot_minus_one", "symRoot_root_a_one"),
             ("M103", "transRoot_lt_one", "false_I_inside", "transRoot_root_I"),
             ("M104", "projectedSlope_lt_quarter", "false_slope_both_negative", None),
             ("M105", "projectedSlope_lt_quarter_of_C", "false_slope_both_negative", None),
             ("M106", "projectedSlope_lt_quarter_of_C", "false_slope_at_boundary", None)]


def mutants():
    return [m for m in mc.MUTANTS if m[1] == F]


def test_module_is_imported_and_hash_pinned():
    root = (PROJ / "AIEFGateCore.lean").read_text()
    assert re.search(r"^import AIEFGateCore\.DelayRoots$", root, re.M)
    sums = (PROJ / "AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt").read_text()
    digest = hashlib.sha256((PROJ / "AIEFGateCore" / F).read_bytes()).hexdigest()
    assert f"{digest}  AIEFGateCore/{F}" in sums


def test_no_escape_hatches():
    code = re.sub(r"/-.*?-/", "", SRC, flags=re.S)
    code = re.sub(r"--.*", "", code)
    for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern"):
        assert bad not in code, bad
    for thm in ("symRoot_eq_one_or_lt", "transRoot_lt_one", "projectedSlope_lt_quarter", "symRoot_one",
                "eq_one_of_norm_ge_one_of_near", "projectedSlope_lt_quarter_of_C", "transRoot_instance_d_two",
                "symRoot_instance_d_two"):
        assert re.search(rf"^theorem {thm}\b", SRC, re.M), thm


def test_statement_mutants_exact_shape():
    ms = mutants()
    assert [m[0].split("_")[0] for m in ms] == [s[0] for s in STATEMENT]
    for (num, thm, refuter, root), (name, f, t, edits, closure, term, engine) in zip(STATEMENT, ms):
        assert t == thm and closure == "" and engine is None, name
        assert mc.mutate(SRC, t, edits) != SRC, name
        assert re.search(rf"^theorem {refuter}\b", SRC, re.M), (name, refuter)
        assert term.startswith(f"DelayRoots.{refuter} (H "), name
        if root:
            assert f"DelayRoots.{root}" in term and re.search(rf"^theorem {root}\b", SRC, re.M), name


def test_mutated_statements_change_only_the_named_hypothesis():
    for name, f, t, edits, closure, term, engine in mutants():
        before = mc.statement_prop(SRC, t, closure)
        after = mc.statement_prop(mc.mutate(SRC, t, edits), t, closure)
        assert before != after, name
        assert len(edits) == 1 and edits[0][2] == 1, name


def _poly(z, d, lead, const):
    """z^(d+1) - lead*z^d + const for z a Gaussian integer (re, im) with Fraction parts."""
    def mul(a, b):
        return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])
    p = (Q(1), Q(0))
    for _ in range(d):
        p = mul(p, z)
    zd1 = mul(p, z)
    return (zd1[0] - lead * p[0] + const, zd1[1] - lead * p[1])


def test_witness_roots_exact():
    # M95: a = 2, d = 1, z = -2 is a root of P = z^2 - (1-a) z - a
    assert _poly((Q(-2), Q(0)), 1, Q(1) - 2, -Q(2)) == (0, 0)
    # M96: z = 1 is a root of P for every a and d
    for a in (Q(1, 2), Q(1, 7)):
        for d in (0, 1, 50):
            assert _poly((Q(1), Q(0)), d, 1 - a, -a) == (0, 0)
    # M97: m = 0, h = 3, d = 0, z = -2;  M98: m = h = 1, d = 0, z = -1  (Q = z^(d+1) - (1-mh) z^d + h)
    assert _poly((Q(-2), Q(0)), 0, Q(1) - 0 * 3, Q(3)) == (0, 0)
    assert _poly((Q(-1), Q(0)), 0, Q(1) - 1 * 1, Q(1)) == (0, 0)
    # M99: C = eps = x = 1 gives exactly 1/4
    assert Q(1) * 1 / (1 + 1) ** 2 == Q(1, 4)
    # M100: a = -2, d = 1, z = 2;  M102: a = 1, d = 1, z = -1  (P = z^(d+1) - (1-a) z^d - a)
    assert _poly((Q(2), Q(0)), 1, Q(1) - (-2), Q(2)) == (0, 0)
    assert _poly((Q(-1), Q(0)), 1, Q(1) - 1, -Q(1)) == (0, 0)
    # M101: m = 1, h = 0, d = 0, z = 1;  M103: m = h = 1, d = 1, z = i
    assert _poly((Q(1), Q(0)), 0, Q(1) - 1 * 0, Q(0)) == (0, 0)
    assert _poly((Q(0), Q(1)), 1, Q(1) - 1 * 1, Q(1)) == (0, 0)
    # M104: C = eps = -1, x = -1/2 (x > C) gives 4/9 > 1/4
    C, e, x = Q(-1), Q(-1), Q(-1, 2)
    assert x > C and C * e / (x + e) ** 2 == Q(4, 9) > Q(1, 4)


def test_eps_redundant_given_C_numerically():
    # 0 < C, C < x, eps <= 0 (and x + eps != 0): slope <= 0 < 1/4, the content of projectedSlope_lt_quarter_of_C
    for C in (Q(1, 3), Q(1), Q(5)):
        for x in (C + Q(1, 7), C + 3):
            for e in (Q(0), -Q(1, 10), -x / 2, -2 * x):
                assert C * e / (x + e) ** 2 <= 0


def test_axioms_printed():
    for thm in ("symRoot_eq_one_or_lt", "symRoot_one", "transRoot_lt_one", "projectedSlope_lt_quarter",
                "projectedSlope_lt_quarter_of_C"):
        assert f"#print axioms AIEFGate.DelayRoots.{thm}" in SRC, thm
