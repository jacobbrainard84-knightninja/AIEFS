"""Lean H13 DiscreteHalanay: pin DiscreteHalanay.lean (easy floor-exponent discrete Halanay,
namespace AIEFGate.DiscreteHalanay) and its mutants M800-M808 without running Lean.

Statement mutants (numbered from M800 so they do not collide with concurrent H9/H16 work):
  M800 discrete_halanay, 0 ≤ initMax u d := True     (M < 0: u3 = -25/36 > -5/6)
  M801 discrete_halanay, exponent n/(d+1) -> n/d     (fails at n = d on a constant window)
  M802 discrete_halanay, initMax window 0..d-1       (unique max at index d)
  M803 discrete_halanay_decay, a+b < 1 -> a+b ≤ 1    (constant sequence, no decay)
  M804 discrete_halanay, step starts at d+1 ≤ n      (unconstrained jump at n = d+1)
  M809 discrete_halanay, 0 ≤ a := True                 (a = -1, b = 0, d = 0)
  M810 discrete_halanay, 0 ≤ b := True                 (a = 0, b = -1/2, d = 0)
  M811 discrete_halanay, base a + b -> a               (a = 0, b = 1/2, d = 0)
Definition mutants M805-M808 are killed by probe_initMax_spike / probe_windowMax_values /
probe_blockPow_values. Weakening a+b < 1 to a+b ≤ 1 on the written bound of discrete_halanay
is predicted to SURVIVE and is not registered (documented, not a decorative KNOWN_SURVIVORS entry).

Correction (2026-11-27, audit B2, SPEC §18.7): M800-M808 were declared in the same commit as their
results, so git does not show the prediction first. Prior written predictions (2026-11-26 target note,
outside git) exist only for M801, M802, M803 and the a+b ≤ 1 survivor. M800 was declared after its
counterexample was found; M804-M808 had no earlier written prediction. M809-M811 (Researcher 001's
X3-X5) were predeclared KILLED in a separate text-only commit before they were wired (SPEC §18.6).

Audit F1: the witness values, probe values and docstring numbers are now PARSED from
DiscreteHalanay.lean (and the SPEC / harness / README text) and recomputed from a Python model of
intervalMax / windowMax / initMax / blockPow in exact rationals. A sampled-bound check runs the bound
on many random (a, b, d, initial window) with the adversarial equality tail, with wrong-variant controls.

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
    ("M809", "discrete_halanay", "false_bound_no_a_nonneg"),
    ("M810", "discrete_halanay", "false_bound_no_b_nonneg"),
    ("M811", "discrete_halanay", "false_bound_base_a"),
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
        "false_bound_no_a_nonneg", "false_bound_no_b_nonneg", "false_bound_base_a",
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


# ---------------------------------------------------------------------------------------------
# Audit F1: parse the Lean witness values, probe values and docstring numbers, and recompute them.
# ---------------------------------------------------------------------------------------------
SPEC = (REPO / "research" / "lean_gate" / "SPEC_P1_gate_identities.md").read_text()
HARNESS = (HERE.parent / "lean_mutation_check.py").read_text()
README = (PROJ / "README.md").read_text()


def lean_rat(expr):
    """Parse a closed Lean rational literal: `1`, `-1`, `5 / 6`, `- (25 / 36)`, `(1 : ℝ)`."""
    e = expr.strip().replace("(1 : ℝ)", "1")
    m = re.fullmatch(r"-\s*\((.*)\)", e)
    if m:
        return -lean_rat(m.group(1))
    m = re.fullmatch(r"\((.*)\)", e)
    if m:
        return lean_rat(m.group(1))
    m = re.fullmatch(r"(-?\d+)\s*/\s*(\d+)", e)
    if m:
        return Q(int(m.group(1)), int(m.group(2)))
    m = re.fullmatch(r"-?\d+", e)
    assert m, expr
    return Q(int(e))


def doc_rat(t):
    """Parse a docstring rational `-25/36`, `5/6`, `-1`."""
    a, _, b = t.partition("/")
    return Q(int(a), int(b) if b else 1)


def fmt(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


# Python model of the Lean definitions (Nat subtraction in windowMax, inclusive windows).
def window_max(u, n, d):
    return max(u[k] for k in range(max(n - d, 0), n + 1))


def init_max(u, d):
    return max(u[k] for k in range(0, d + 1))


def block_pow(q, n, d):
    return q ** (n // (d + 1))


def lean_def_value(name):
    m = re.search(rf"^def {name} : ℝ := (.+)$", SRC, re.M)
    assert m, name
    return lean_rat(m.group(1))


A_E, B_E = lean_def_value("aE"), lean_def_value("bE")


def lean_delay1_seq(name, n_max=8):
    """Parse `def name : ℕ → ℝ | 0 => x | 1 => y | n + 2 => aE * name (n + 1) + bE * max (name n) (name (n + 1))`."""
    m = re.search(
        rf"^def {name} : ℕ → ℝ\n  \| 0 => (.+)\n  \| 1 => (.+)\n"
        rf"  \| n \+ 2 => aE \* {name} \(n \+ 1\) \+ bE \* max \({name} n\) \({name} \(n \+ 1\)\)$",
        SRC, re.M)
    assert m, name
    u = [lean_rat(m.group(1)), lean_rat(m.group(2))]
    while len(u) <= n_max:
        n = len(u) - 2
        u.append(A_E * u[n + 1] + B_E * max(u[n], u[n + 1]))
    return u


def lean_theorem_eq(name):
    """RHS of `theorem name : <lhs> = <rhs> := by`."""
    m = re.search(rf"^theorem {name} : (.+?) = (.+?) := by\b.*$", SRC, re.M)
    assert m, name
    return m.group(1), lean_rat(m.group(2))


def test_witness_values_parsed_from_lean_match_exact_model():
    q = A_E + B_E
    assert (A_E, B_E) == (Q(1, 2), Q(1, 3))
    assert lean_theorem_eq("qE_val") == ("aE + bE", q)
    u = lean_delay1_seq("uNeg")
    assert lean_theorem_eq("uNeg_two") == ("uNeg 2", u[2])
    assert lean_theorem_eq("uNeg_three") == ("uNeg 3", u[3])
    assert lean_theorem_eq("uNeg_initMax") == ("initMax uNeg 1", init_max(u, 1))
    h = lean_delay1_seq("uHold1")
    assert lean_theorem_eq("uHold1_initMax") == ("initMax uHold1 1", init_max(h, 1))
    sp = lean_delay1_seq("uSpike1")
    assert lean_theorem_eq("uSpike1_initMax") == ("initMax uSpike1 1", init_max(sp, 1))
    assert lean_theorem_eq("uSpike1_initMax_short") == ("initMax uSpike1 0", init_max(sp, 0))
    # the parsed sequences obey the delayed inequality with equality, as the *_step theorems claim
    for seq in (u, h, sp):
        for n in range(1, len(seq) - 1):
            assert seq[n + 1] == A_E * seq[n] + B_E * window_max(seq, n, 1)


def test_neg_initMax_counterexample_parsed_and_docstring_numbers():
    """M < 0 (M800): the Lean witness uNeg breaks the written bound at n = 3; every docstring copy agrees."""
    q = A_E + B_E
    u = lean_delay1_seq("uNeg")
    M = init_max(u, 1)
    bound = M * block_pow(q, 3, 1)
    assert M < 0 and u[3] > bound and u[3] - bound == Q(5, 36)
    # the refuter evaluates H at n = 3 with d = 1
    assert "have h := H uNeg aE bE 1 aE_nonneg bE_nonneg qE_lt_one trivial hstep 3" in SRC
    spec18 = SPEC[SPEC.index("## 18. Discrete Halanay"):]
    for name, text, want in (("lean", SRC, 2), ("spec18", spec18, 2), ("harness", HARNESS, 1), ("readme", README, 1)):
        found = re.findall(r"(-?\d+/\d+) > (-?\d+/\d+)", text)
        assert len(found) >= want, (name, found)
        for lhs, rhs in found:
            assert (doc_rat(lhs), doc_rat(rhs)) == (u[3], bound), (name, lhs, rhs)
    # the exact strings, rebuilt from the parsed values
    assert f"`u 3 = {fmt(u[3])} > {fmt(bound)} = M * q`" in SRC
    assert f"`d = 1`, `M = {fmt(M)}`" in SRC
    assert f"`{fmt(u[3])} > {fmt(bound)}`" in SRC
    assert f"u3={fmt(u[3])} > {fmt(bound)}" in HARNESS
    assert f"difference `{fmt(u[3] - bound)}`" in SPEC
    assert f"`u 0 = u 1 = {fmt(u[0])}` (so `M = {fmt(M)}`)" in SRC


def _probe(name):
    m = re.search(rf"^theorem {name} :\n(.*?) := by$", SRC, re.M | re.S)
    assert m, name
    return " ".join(m.group(1).split())


def test_probe_values_parsed_from_lean_match_model():
    # probe_initMax_spike: initMax (fun k => if k = S then (1 : ℝ) else 0) D = V
    m = re.fullmatch(r"initMax \(fun k => if k = (\d+) then \(1 : ℝ\) else 0\) (\d+) = (\S+)",
                     _probe("probe_initMax_spike"))
    assert m
    s_idx, d, v = int(m.group(1)), int(m.group(2)), lean_rat(m.group(3))
    spike = [Q(1) if k == s_idx else Q(0) for k in range(d + 2)]
    assert init_max(spike, d) == v == 1
    assert init_max(spike, d - 1) == 0 and max(spike[:1]) == 0      # what M805 / M808 would give
    # probe_windowMax_values: two windowMax values of a spike
    parts = _probe("probe_windowMax_values").split(" ∧ ")
    assert len(parts) == 2
    for part in parts:
        m = re.fullmatch(r"windowMax \(fun k => if k = (\d+) then \(1 : ℝ\) else 0\) (\d+) (\d+) = (\S+)", part)
        assert m, part
        s_idx, n, d, v = int(m.group(1)), int(m.group(2)), int(m.group(3)), lean_rat(m.group(4))
        spike = [Q(1) if k == s_idx else Q(0) for k in range(n + 2)]
        assert window_max(spike, n, d) == v, part
    # current-only windowMax (M806) would give u 1 = 0 on the first part
    assert parts[0].endswith("1 1 = 1")
    # probe_blockPow_values: blockPow (Q) N D = V ∧ ...
    parts = _probe("probe_blockPow_values").split(" ∧ ")
    assert len(parts) == 2
    for part in parts:
        m = re.fullmatch(r"blockPow \((.+?)\) (\d+) (\d+) = (.+)", part)
        assert m, part
        q, n, d, v = lean_rat(m.group(1)), int(m.group(2)), int(m.group(3)), lean_rat(m.group(4))
        assert block_pow(q, n, d) == v, part
        if n == d:
            assert q ** (n // d) != v       # the wrong exponent n / d (M807) would differ
    # docstring of the blockPow probe
    assert "`50 / 51 = 0` and `51 / 51 = 1`" in SRC and 50 // 51 == 0 and 51 // 51 == 1
    assert "`50 / 50 = 1` and `blockPow (5/6) 50 50 = 5/6`" in SRC


def test_new_refuter_docstring_numbers():
    """M809-M811 refuter docstrings: recompute the witness sequences and the failing index."""
    # M809: a = -1, b = 0, d = 0, u = 1, -5, 5, -5, ...
    u = [Q(1)] + [Q(-5) if n % 2 else Q(5) for n in range(1, 12)]
    a, b, d = Q(-1), Q(0), 0
    assert all(u[n + 1] <= a * u[n] + b * window_max(u, n, d) for n in range(11)) and a + b < 1
    assert u[2] > init_max(u, d) * block_pow(a + b, 2, d)
    assert f"`u 2 = {fmt(u[2])} > {fmt(init_max(u, d) * block_pow(a + b, 2, d))} = M * (-1) ^ 2`" in SRC
    # M810: a = 0, b = -1/2, d = 0, u 0 = 1, u n = -10 * (-1/2)^(n-1)
    a, b = Q(0), Q(-1, 2)
    u = [Q(1)] + [Q(-10) * b ** (n - 1) for n in range(1, 12)]
    assert all(u[n + 1] <= a * u[n] + b * window_max(u, n, d) for n in range(11)) and a + b < 1
    rhs = init_max(u, d) * block_pow(a + b, 2, d)
    assert u[2] > rhs and f"`u 2 = {fmt(u[2])} > {fmt(rhs)} = M * (-1/2) ^ 2`" in SRC
    # M811: a = 0, b = 1/2, d = 0, u n = (1/2)^n; base a gives 0 at n = 1
    a, b = Q(0), Q(1, 2)
    u = [b ** n for n in range(12)]
    assert all(u[n + 1] <= a * u[n] + b * window_max(u, n, d) for n in range(11))
    rhs = init_max(u, d) * block_pow(a, 1, d)
    assert u[1] > rhs and f"`u 1 = {fmt(u[1])} > {fmt(rhs)} = M * 0 ^ 1`" in SRC
    # and the correct base a + b holds on the same witness (the mutation is what breaks it)
    assert all(u[n] <= init_max(u, d) * block_pow(a + b, n, d) for n in range(12))


# ---------------------------------------------------------------------------------------------
# Audit F1: the sampled-bound check the target asked for (exact Fractions).
# ---------------------------------------------------------------------------------------------
def _simulate(a, b, d, window, n_max, rng, slack):
    u = list(window)
    for n in range(d, n_max):
        rhs = a * u[n] + b * window_max(u, n, d)
        s = Q(rng.randint(0, 3), rng.randint(1, 4)) if (slack and rng.random() < 0.3) else Q(0)
        u.append(rhs - s)
    return u


def test_sampled_bound_exact_with_adversarial_equality_tail():
    import random
    rng = random.Random(20261127)
    trials = tight = 0
    viol_neg_M = viol_n_div_d = viol_base_a = viol_short = 0
    for t in range(400):
        d = rng.randint(0, 5)
        den = rng.randint(2, 9)
        num_a = rng.randint(0, den - 1)
        num_b = rng.randint(0, den - 1 - num_a)
        a, b = Q(num_a, den), Q(num_b, den)
        if t % 4 == 0:
            a, b = Q(rng.randint(0, 6), 7), Q(0)       # include b = 0 and the a + b near 1 corner
            if a == 0:
                b = Q(6, 7)
        assert 0 <= a and 0 <= b and a + b < 1
        q = a + b
        n_max = 5 * (d + 1) + 3
        if t % 3 == 0:                                  # adversarial: constant window, equality tail
            M0 = Q(rng.randint(0, 5), rng.randint(1, 3))
            window = [M0] * (d + 1)
            slack = False
        else:                                           # mixed-sign window with max ≥ 0
            window = [Q(rng.randint(-6, 6), rng.randint(1, 4)) for _ in range(d + 1)]
            if max(window) < 0:
                window[rng.randint(0, d)] = Q(rng.randint(0, 3))
            slack = rng.random() < 0.5
        u = _simulate(a, b, d, window, n_max, rng, slack)
        M = init_max(u, d)
        assert M >= 0
        for n in range(n_max + 1):
            assert u[n] <= M * block_pow(q, n, d), (a, b, d, window, n)
        trials += 1
        if t % 3 == 0:
            # the adversarial sequence sits on the bound on 0..d and at n = d + 1
            assert all(u[n] == M * block_pow(q, n, d) for n in range(d + 2))
            tight += 1
            if M > 0 and d >= 1 and q ** (d // d) < 1:
                viol_n_div_d += u[d] > M * q ** (d // d)                 # wrong exponent n / d
            if M > 0 and b > 0:
                viol_base_a += u[d + 1] > M * block_pow(a, d + 1, d)     # wrong base a
        if d >= 1 and t % 3 != 0:
            # short window 0..d-1 (wrong variant): unique max at index d
            w = [Q(0)] * d + [Q(1)]
            us = _simulate(a, b, d, w, n_max, rng, False)
            viol_short += us[d] > init_max(us, d - 1) * block_pow(q, d, d)
        # wrong variant: M < 0 (negated window, equality tail) must break the bound for some samples
        if d >= 1 and q > 0:
            wneg = [Q(-1)] * (d + 1)
            un = _simulate(a, b, d, wneg, n_max, rng, False)
            Mn = init_max(un, d)
            viol_neg_M += any(un[n] > Mn * block_pow(q, n, d) for n in range(n_max + 1))
    assert trials == 400 and tight >= 100
    # every wrong variant is caught on the same sampler (controls; counts are not pinned exactly)
    assert viol_n_div_d > 20 and viol_base_a > 20 and viol_short > 50 and viol_neg_M > 50


def test_no_rho_below_one_at_a_plus_b_one_sampled():
    """M803 control, sampled: at a + b = 1, u ≡ 1 obeys the inequality, and every ρ < 1 fails at n = d + 1."""
    import random
    rng = random.Random(803)
    for _ in range(200):
        d = rng.randint(0, 6)
        den = rng.randint(1, 50)
        a = Q(rng.randint(0, den), den)
        b = 1 - a
        u = _simulate(a, b, d, [Q(1)] * (d + 1), 3 * (d + 1), rng, False)
        assert all(x == 1 for x in u)
        rho = Q(rng.randint(0, 999), 1000)
        assert u[d + 1] > init_max(u, d) * rho ** ((d + 1) // (d + 1))


# ---------------------------------------------------------------------------------------------
# Audit F2-F4 and B2: wording pins.
# ---------------------------------------------------------------------------------------------
def test_geom_docstring_corrected_and_not_mutated():
    i = SRC.index("theorem discrete_halanay_geom")
    doc = SRC[SRC.rindex("/--", 0, i):i]
    assert "It is *not* a decay control." in doc
    assert "holds with equality for every `n`" in doc
    assert not any(m[2] == "discrete_halanay_geom" for m in mc.MUTANTS)
    assert "`discrete_halanay_geom` is not mutated" in SPEC
    assert "the only control that tells `a + b < 1` apart from `a + b ≤ 1`" in SPEC


def test_d0_has_no_unused_rate_hypothesis():
    s, e = mc.theorem_span(SRC, "discrete_halanay_d0")
    stmt = SRC[s:e]
    assert "a + b < 1" not in stmt and "(ha : 0 ≤ a)" in stmt and "(hb : 0 ≤ b)" in stmt
    assert "more than `upper_geom`'s `0 ≤ ρ`" in SRC


def test_b2_predeclaration_correction_recorded():
    for text in (SPEC, HARNESS, __doc__):
        assert "M804" in text
    assert "### 18.7 Correction: predeclaration timing" in SPEC
    assert "only for M801, M802, M803 and the `a + b ≤ 1` survivor" in SPEC
    assert "M800 was declared after its counterexample was found" in SPEC
    assert "CORRECTION (2026-11-27, SPEC §18.7; audit B2)" in HARNESS
    assert "### 18.6 Predeclaration of M809–M811" in SPEC


def _sci(x):
    m, e = f"{x:.1e}".split("e")
    return f"{m}e{int(e)}"


def test_f4_rate_looseness_numbers_match_spec():
    """Gated typical a = 2981/3000, b = 19/33000, d = 50 (the target note's consumer numbers)."""
    import math
    a, b, d, N = 2981 / 3000, 19 / 33000, 50, 3000
    q = a + b
    easy = q ** (1 / (d + 1))
    lo, hi = 0.0, 1.0                                    # root of x^(d+1) = a x^d + b in (0, 1)
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if mid ** (d + 1) - a * mid ** d - b > 0 else (mid, hi)
    lam = lo
    he, hs = math.log(2) / -math.log(easy), math.log(2) / -math.log(lam)
    u = [1.0] * (d + 1)
    for n in range(d, N):
        u.append(a * u[n] + b * max(u[n - d:n + 1]))
    floor = q ** (N // (d + 1))
    assert f"half-life of {he:.0f} steps" in SPEC and f"against {hs:.0f}" in SPEC
    assert f"`u 3000 ≈ {_sci(u[N])}`" in SPEC and f"allows `{floor:.3f}`" in SPEC
    assert (round(he), round(hs), _sci(u[N]), f"{floor:.3f}") == (6122, 124, "6.9e-8", "0.715")
    assert max(u[n] / lam ** (n - d) for n in range(d, N + 1)) < 1 + 1e-9
