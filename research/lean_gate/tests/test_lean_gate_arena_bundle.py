"""Lean intake of the Arena bundle (MERGE_MANIFEST 2026-11-25 of Arena_Researcher_06020041, audit-inbox 41335f0;
SPEC §17): pin the 12 modules, their mutants M131-M190 (+ M191-M201, audit follow-up §17.7) / controls E21-E23 and
FILE_OPENS without running Lean.

Modules (deposit sha256 in DEPOSIT below): ReachableQueue, EmaNearUnit, MatrixPhaseBridge (D6 prerequisite),
QueueComposition, EmaWrapInvariant, CausalEMATracking, EMAFiniteSum, TransientBridge, TransientParameter, WindowMax,
HeteroStepRef, HeteroGuard. CoherenceSpeedLimit is deliberately NOT taken in (it overlaps
CoherenceMotion.trace_step_abs_le_min on main).

The deposited statements and proofs must be unchanged: each file, with the repository header, the module doc and the
appended SPEC §17 section removed, must equal the deposit line for line (blank lines ignored). The digest of those
non-blank deposit lines is pinned below, so an edited proof or statement fails here.

Run: /workspace/venv-pt/bin/pytest -q research/lean_gate/tests/test_lean_gate_arena_bundle.py
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

# module -> (sha256 of the deposited file, sha256 of its non-blank lines after the SPDX line is removed)
DEPOSIT = {
    "ReachableQueue": ("7ee2029583564959cf88b6acf3593aef442f991a1df7bc6667bb29e19ded9aa0", "8f28e341a24d179cb393a1fbe25fd9786c39dac1605e9244629279c2aa449ffb"),
    "EmaNearUnit": ("292d1e7a98cf7ff963ac23873839686562a9cb453140d5f21b2d176589a895ec", "4794fbf3497622a93f5b2d09e1a9df7d602fd31398ef1830a326f03e01b84d64"),
    "MatrixPhaseBridge": ("74d44d87e345712b9df9804811fa6586c759e2dcb215eb80a09659a0458fcb62", "227a29e5e12940c12ae0c64a1499ed32abdd008fcf44a8ccd6aff097f9f0dbe7"),
    "QueueComposition": ("7a1b1b006d8695f7bf1073e9034b95eac9093b7e9ea554316bba34438e5d87eb", "84973f6525a6fb1b4c735779e8c644de09bb24db28b7993dc09b9ccde93fff5c"),
    "EmaWrapInvariant": ("5d05160b19e38f4b2ac07e08a0ca3e002dc4682aa629a84283a2523c83b763d4", "973cc49ddd5f3271930785a773442e07f5e45ff316193aea3c25212f54dcbca6"),
    "CausalEMATracking": ("21493f2821130734c1fe900454be57769ec38991506b755290f53f111f1ec958", "0e69dd462c76f70bc9a8310c51dc6524759fdbd1a602cd6d8c233a9185c41ef2"),
    "EMAFiniteSum": ("08a47a74f254509fa3e19afb9fd85f89727793622b9730619f9b62d75a560064", "d8d96ef983e6b76f511f92553901a9d490ec2ed0b27f513d9d9b8b07e3381d87"),
    "TransientBridge": ("5327041b90749144b3f21b09c2e594e6712a427432a5d374daeef8b6f69e1385", "2f30b28ece95d60d99e720795b9e9e6ebf09a967abf86741615a5318c4ccc99e"),
    "TransientParameter": ("51fbb51d0e87c4f9f96c61e93685ccdcf41cd5ce46af699cbd423761ceed8b0c", "9079233041b35394682da3ff7220264cc8eb0bf2aa7c50bf88749fe796e8c27b"),
    "WindowMax": ("5d91183b3a47e41648d1fa63ccdaf3335627aea5d3580342542e8c31f1d2a9d2", "3906198e20088c0dde42002e6d72997c6fcac9be94ccd351f947f4cec2aaef82"),
    "HeteroStepRef": ("9d16831a773330b1258eba3d6a664451e2d6746b1f5f2ee18daaae473b00a46b", "eaa5d347203800eb3205ecf3cdd127124decebf26a42b215769727dbad89bfed"),
    "HeteroGuard": ("9ebe000257ed7b7e1b64f3e956e0a8a56c3c78468ac1d076789c2dfddc564481", "e76bfd888836f49735553838d30879a2026292eaafea51da0eba097da63d386f"),
}
FILES = tuple(f"{m}.lean" for m in DEPOSIT)
SRC = {f: (PROJ / "AIEFGateCore" / f).read_text() for f in FILES}
NS = {f: ("HeteroStepRef" if f == "HeteroGuard.lean" else f[:-5]) for f in FILES}


def deposit_body(src):
    """The file minus the repository header, the first module doc and the appended `/-! ### ` section."""
    assert src.startswith("/-\nCopyright (c) 2026 Jacob Brainard and AIEF contributors.")
    s = src[src.index("-/\n") + 3:]
    i = s.index("/-!\n# ")
    s = s[:i] + s[s.index("\n-/\n", i) + 4:]
    k = s.index("/-! ### ")
    e = s.index("\n", s.rfind("\n#print axioms ") + 1)
    return s[:k] + s[e + 1:]


def test_modules_imported_and_hash_pinned():
    root = (PROJ / "AIEFGateCore.lean").read_text()
    sums = (PROJ / "AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt").read_text()
    for f in FILES:
        assert re.search(rf"^import AIEFGateCore\.{f[:-5]}$", root, re.M), f
        digest = hashlib.sha256((PROJ / "AIEFGateCore" / f).read_bytes()).hexdigest()
        assert f"{digest}  AIEFGateCore/{f}" in sums, f
    assert "CoherenceSpeedLimit" not in root and not (PROJ / "AIEFGateCore" / "CoherenceSpeedLimit.lean").exists()


def test_deposited_statements_and_proofs_unchanged():
    for f in FILES:
        body = "\n".join(l for l in deposit_body(SRC[f]).split("\n") if l.strip())
        assert hashlib.sha256(body.encode()).hexdigest() == DEPOSIT[f[:-5]][1], f
        assert f"deposit sha256 `{DEPOSIT[f[:-5]][0][:8]}…`" in SRC[f], f
        assert f"namespace AIEFGate.{NS[f]}" in SRC[f], f


def test_no_escape_hatches_and_axioms_printed():
    for f, src in SRC.items():
        code = re.sub(r"/-.*?-/", "", src, flags=re.S)
        code = re.sub(r"--.*", "", code)
        for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern"):
            assert bad not in code, (f, bad)
        for thm in re.findall(r"^theorem (\S+)", src, re.M):
            assert re.search(rf"^#print axioms (AIEFGate\.\w+\.)?{thm}$", src, re.M), (f, thm)


def test_statement_mutants_exact_shape():
    ms = [m for m in mc.MUTANTS if m[1] in FILES]
    assert [int(m[0].split("_")[0][1:]) for m in ms] == list(range(131, 157)) + list(range(191, 202))
    for name, f, thm, edits, closure, term, engine in ms:
        assert closure == "" and engine is None, name
        assert len(edits) == 1 and edits[0][2] == 1, name
        assert mc.mutate(SRC[f], thm, edits) != SRC[f], name
        m = re.fullmatch(rf"{NS[f]}\.(false_\w+) H", term)
        assert m and re.search(rf"^theorem {m.group(1)}\b", SRC[f], re.M), name
        assert mc.statement_prop(SRC[f], thm, "") != mc.statement_prop(mc.mutate(SRC[f], thm, edits), thm, ""), name
    assert {m[1] for m in ms} == set(FILES)                     # every module has at least one


def test_def_mutants_probes_and_controls():
    de = [m for m in mc.DEF_MUTANTS if m[1] in FILES]
    assert [int(m[0].split("_")[0][1:]) for m in de] == list(range(157, 191))
    for name, f, edits, pins in de:
        assert mc.mutate_file(SRC[f], edits) != SRC[f], name
        assert pins and set(pins) <= set(mc.VALUE_PROBES[f]), name
    probed = {m[1] for m in de}
    assert probed == set(FILES) - {"EmaNearUnit.lean", "EMAFiniteSum.lean", "HeteroGuard.lean"}   # no own defs
    for f in probed:
        for p in mc.VALUE_PROBES[f]:
            assert p.startswith("probe_") and re.search(rf"^theorem {p}\b", SRC[f], re.M), (f, p)
    eq = [c for c in mc.EQUIV_CONTROLS if c[1] in FILES]
    assert [c[0].split("_")[0] for c in eq] == ["E21", "E22", "E23"]
    for name, f, edits in eq:
        assert mc.mutate_file(SRC[f], edits) != SRC[f], name


def test_file_opens_one_bundle_namespace_each():
    assert set(mc.FILE_OPENS) == set(FILES)
    for f, pre in mc.FILE_OPENS.items():
        opened = re.findall(r"AIEFGate\.(\w+)", pre)
        expect = ["CausalEMATracking", "EMAFiniteSum"] if f == "EMAFiniteSum.lean" else [NS[f]]
        assert opened == expect, f
    # the short names that collide across the bundle are never opened globally
    for short in ("ReachableQueue", "MatrixPhaseBridge", "TransientBridge", "TransientParameter", "WindowMax",
                  "HeteroStepRef"):
        assert f"AIEFGate.{short}" not in mc.OPENS, short
    assert "FILE_OPENS.get(f, \"\")" in (HERE.parent / "lean_mutation_check.py").read_text()


def _flat(text):
    return " ".join(text.split())


def _stmt(f, thm):
    """The statement of `theorem thm` in file f, read from the Lean source (up to `:= by`), whitespace-flattened."""
    m = re.search(rf"^theorem {thm}\b(.*?):= by", SRC[f], re.M | re.S)
    assert m, (f, thm)
    return _flat(m.group(1))


def _def(f, name):
    """The text of `def name` in file f up to the next blank line, whitespace-flattened."""
    m = re.search(rf"^def {name}\b(.*?)\n\n", SRC[f], re.M | re.S)
    assert m, (f, name)
    return _flat(m.group(1))


def _proof_line(f, thm, prefix="have h := H "):
    """The first `have h := H ...` line of the proof of `theorem thm` (the witness instantiation), flattened."""
    s = SRC[f][SRC[f].index(f"theorem {thm}"):]
    s = s[:s.index("\n\n")]
    i = s.index(prefix)
    return _flat(s[i:s.index("\n", i)])


def lean(x):
    """An exact rational in the form the probes write it: `2`, `-1/2`, `3/2`."""
    x = Q(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _next(n, d, c, v, k):           # WindowMax.next (pinned to the Lean def in the test below)
    return (1 - (n - 1) * c) * v[0] - c * v[d] if k == 0 else v[k - 1]


def _lin(dt, row, vd_sum, v0, k, vprev):   # HeteroStepRef.linearStep, one node
    return (1 - dt * row) * v0 + dt * vd_sum if k == 0 else vprev


def _step(c, p):                     # TransientParameter.step (TransientBridge at c = stepSize = 1/4)
    return ((1 - 2 * c) * p[0] - c * p[1], p[0])


def _energy(p):
    return p[0] ** 2 + p[1] ** 2


def _budget(a, E, drift, n):         # CausalEMATracking.budget
    return E if n == 0 else a * _budget(a, E, drift, n - 1) + drift(n - 1)


def test_probe_and_witness_values_exact():
    """Read the probe and witness statements from the Lean sources and recompute their numbers in exact arithmetic.

    The Python models are first pinned to the Lean definitions (text), so a changed definition, a changed probe value or
    a changed witness instance in the .lean file fails here (not only in the Lean build). SPEC §17.5, audit note N1."""
    wm, he = "WindowMax.lean", "HeteroStepRef.lean"
    tb, tp = "TransientBridge.lean", "TransientParameter.lean"
    ce, ef = "CausalEMATracking.lean", "EMAFiniteSum.lean"
    # 1. the models are the Lean definitions
    assert _def(wm, "next") == ("(n d : ℕ) (c : ℝ) (v : ℕ → ℝ) (k : ℕ) : ℝ := "
                                "if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - c * v d else v (k - 1)")
    assert _def(he, "linearStep") == ("(n d : ℕ) (dt : ℝ) (B : Fin n → Fin n → ℝ) (v : ℕ → Fin n → ℝ) (k : ℕ) "
                                      "(i : Fin n) : ℝ := if k = 0 then (1 - dt * row n B i) * v 0 i + "
                                      "dt * ∑ j, B i j * v d j else v (k - 1) i")
    assert _def(he, "row") == "(n : ℕ) (B : Fin n → Fin n → ℝ) (i : Fin n) : ℝ := ∑ j : Fin n, B i j"
    assert _def(tb, "stepSize") == ": ℝ := 1 / 4"
    assert _def(tb, "step") == "(p : ℝ × ℝ) : ℝ × ℝ := ((1 - 2 * stepSize) * p.1 - stepSize * p.2, p.1)"
    assert _def(tp, "step").startswith("(c : ℝ) (p : ℝ × ℝ) : ℝ × ℝ := ((1 - 2 * c) * p.1 - c * p.2, p.1)")
    for f in (tb, tp):
        assert re.search(r"^def energy \(p : ℝ × ℝ\) : ℝ := p\.1 \^ 2 \+ p\.2 \^ 2$", SRC[f], re.M), f
    assert _def(ce, "budget") == ("(alpha E : ℝ) (drift : ℕ → ℝ) : ℕ → ℝ | 0 => E | n + 1 => "
                                  "alpha * budget alpha E drift n + drift n")

    # 2. probes: the right-hand sides in the .lean file equal the model values
    v = {0: Q(1), 1: Q(4)}
    w = "(fun k => if k = 0 then 1 else 4)"
    assert _stmt(wm, "probe_next_values") == (
        f": next 3 1 (1/4) {w} 0 = {lean(_next(3, 1, Q(1, 4), v, 0))} ∧ "
        f"next 3 1 (1/4) {w} 1 = {lean(_next(3, 1, Q(1, 4), v, 1))}")
    b, w = "(fun _ _ => 1)", "(fun k _ => if k = 0 then 1 else 3)"
    assert _stmt(he, "probe_linearStep_values") == (
        f": linearStep 1 1 (1/2) {b} {w} 0 0 = {lean(_lin(Q(1, 2), 1, 1 * 3, 1, 0, None))} ∧ "
        f"linearStep 1 1 (1/2) {b} {w} 1 0 = {lean(_lin(Q(1, 2), 1, 3, 1, 1, 1))}")
    s = _step(Q(1, 4), (1, 2))
    assert _stmt(tb, "probe_step_values") == f": step (1, 2) = ({lean(s[0])}, {lean(s[1])})"
    assert _stmt(tp, "probe_step_values") == f": step (1/4) (1, 2) = ({lean(s[0])}, {lean(s[1])})"
    for f in (tb, tp):
        assert _stmt(f, "probe_energy_value") == f": energy (1, 2) = {lean(_energy((1, 2)))}", f
    assert _stmt(ce, "probe_budget_values") == (
        f": budget 2 0 (fun _ => 1) 1 = {lean(_budget(2, 0, lambda k: 1, 1))} ∧ "
        f"budget 2 1 (fun _ => 0) 2 = {lean(_budget(2, 1, lambda k: 0, 2))}")

    # 3. the mutant values the probe docstrings promise differ from the probe value (M182-M185, M186-M188)
    doc = _flat(SRC[wm][SRC[wm].index("/-- `next 3 1 (1/4)"):SRC[wm].index("theorem probe_next_values")])
    c = Q(1, 4)
    claimed = {"`n - 1` gives": (1 - 3 * c) * 1 - c * 4, "`+ c·v d` gives": (1 - 2 * c) * 1 + c * 4,
               "slot 0 instead of `d` gives": (1 - 2 * c) * 1 - c * 1, "unshifted slot 1 gives": v[1]}
    for phrase, val in claimed.items():
        m = re.search(re.escape(phrase.split(" gives")[0]) + r"[^`]*?gives `(-?\d+(?:/\d+)?)`", doc)
        assert m and Q(m.group(1)) == val != _next(3, 1, c, v, 0 if "slot 1" not in phrase else 1), phrase

    # 4. witnesses: the instance in each `false_*` proof, and the violation it gives
    assert _proof_line(wm, "false_window_step_no_threshold").startswith("have h := H 3 1 (4/5) 1 (fun _ => 1)")
    assert abs(_next(3, 1, Q(4, 5), {0: 1, 1: 1}, 0)) == Q(7, 5) > 1                         # M149 / M150
    assert _proof_line(wm, "false_window_all_no_threshold").startswith("have h := H 3 1 (4/5) 1 (fun _ => 1)")
    assert _proof_line(wm, "false_coefficient_no_size").startswith("have h := H 1 1 trivial")
    assert abs(1 - (1 - 1) * 1) + 1 == 2 > 1                                                  # M151 at n = 1, c = 1
    assert _proof_line(he, "false_window_step_no_row").startswith(
        "have h := H 1 1 1 1 (fun _ _ => 2) (fun k _ => if k = 0 then 1 else -1)")
    assert _lin(1, 2, 2 * -1, 1, 0, None) == -3                                               # M152
    assert _proof_line(he, "false_window_step_no_dt").startswith(
        "have h := H 1 1 (-1) 1 (fun _ _ => 1) (fun k _ => if k = 0 then 1 else -1)")
    assert _lin(-1, 1, -1, 1, 0, None) == 3                                                   # M154
    assert "fun i j => if i = j then 1 else -1" in _flat(SRC[he][SRC[he].index("theorem false_window_step_no_nonneg"):])
    assert (1 - 1 * (1 - 1)) * 1 + 1 * (1 * 1 + (-1) * (-1)) == 3                              # M153, row 0
    assert _proof_line(tb, "false_one_step_factor_one") == "have h := H (1, 0)"
    assert _energy(_step(Q(1, 4), (1, 0))) == Q(5, 4) > 1 * _energy((1, 0))                   # M143
    assert _proof_line(tb, "false_two_step_quarter") == "have h := H (1, -1)"
    assert _energy(_step(Q(1, 4), _step(Q(1, 4), (1, -1)))) == Q(37, 64) > Q(1, 4) * _energy((1, -1))   # M144
    assert _proof_line(tp, "false_one_step_no_upper").startswith("have h := H 2 (1, 0)")
    assert re.search(r"energy \(step c p\) ≤ \(21 / 8 : ℝ\) \* energy p", _stmt(tp, "false_one_step_no_upper"))
    assert _energy(_step(2, (1, 0))) == 10 > Q(21, 8)                                          # M148
    # M146 / M147: the characteristic polynomial z^2 - (1 - 2c) z + c in the statement, at the witnessed root
    poly = "(_hz : z ^ 2 - ((1 - 2 * c : ℝ) : ℂ) * z + (c : ℂ) = 0)"
    for thm, (cc, z) in {"false_stable_no_upper": (2, -1), "false_stable_no_pos": (0, 1)}.items():
        assert poly in _stmt(tp, thm), thm
        assert _proof_line(tp, thm).startswith(f"have h := H {cc} ") and \
            f" {z if z >= 0 else f'({z})'} (by push_cast" in _proof_line(tp, thm)
        assert z ** 2 - (1 - 2 * cc) * z + cc == 0 and abs(z) >= 1, thm
    ind = lambda k: 1 if k == 0 else 0
    assert _proof_line(ef, "false_finite_sum_reversed") == "have h := H 2 0 (fun k => if k = 0 then 1 else 0) 3"
    assert _budget(2, 0, ind, 3) == 4 != sum(2 ** k * ind(k) for k in range(3))                # M141
    assert _proof_line(ef, "false_finite_sum_no_start_decay") == "have h := H 2 1 (fun _ => 0) 1"
    assert _budget(2, 1, lambda k: 0, 1) == 2 != 1                                             # M142


def _spec_section(num):
    spec = (REPO / "research" / "lean_gate" / "SPEC_P1_gate_identities.md").read_text()
    i = spec.index(f"### {num} ")
    return _flat(spec[i:spec.index("\n### ", i + 1)])


def _threshold(expr, n):
    """Evaluate a SPEC threshold such as `1/(N−1)` or `2/N` at N = n, exactly (digits, N, /, −, parentheses only)."""
    e = expr.replace("−", "-").replace(" ", "")
    assert re.fullmatch(r"[0-9N/()+-]+", e), expr
    e = re.sub(r"(\d+)", r"Q(\1)", e).replace("N", f"Q({n})")
    return eval(e, {"Q": Q, "__builtins__": {}})        # noqa: S307 -- restricted to the characters above


def test_window_max_and_hetero_are_complementary():
    """SPEC §17.4, read from the SPEC text and checked against the Lean hypotheses (audit note N1).

    The thresholds in §17.4 are parsed and must equal those implied by the Lean statements: HeteroStepRef.window_step's
    row condition `dt * row n B i ≤ 1` (uniform off-diagonal b, c = dt*b: (N-1)c ≤ 1) and WindowMax's
    `2 ≤ n`, `(n : ℝ) * c ≤ 2` (c ≤ 2/N). Then 1/(N-1) ≤ 2/N for every N ≥ 2, and the §17.4 example (N, c) is checked
    against coefficient_bound and growth_witness as stated in Lean."""
    sec = _spec_section("17.4")
    hrow = re.search(r"\(hrow : ∀ i, dt \* row n B i ≤ (\d+)\)", _stmt("HeteroStepRef.lean", "window_step"))
    cb = _stmt("WindowMax.lean", "coefficient_bound")
    wsize = re.search(r"\(hn : (\d+) ≤ n\)", cb)
    wthr = re.search(r"\(ht : \(n : ℝ\) \* c ≤ (\d+)\)", cb)
    assert hrow and wsize and wthr
    assert cb.endswith("|1 - ((n : ℝ) - 1) * c| + c ≤ 1")
    assert "(hn : 2 ≤ n) (hc : 0 ≤ c) (ht : (n : ℝ) * c ≤ 2)" in _stmt("WindowMax.lean", "window_step")
    h_spec = re.search(r"`\(N−1\)·c ≤ (\d+)`, i\.e\. `c ≤ ([^`]+)`", sec)
    w_spec = re.search(r"allows the larger range `c ≤ ([^`]+)`", sec)
    n_spec = re.search(r"for every `N ≥ (\d+)` \(equal at `N = (\d+)`\)", sec)
    ex = re.search(r"checked at `N = (\d+)`, `c = (\d+)/(\d+)`", sec)
    assert h_spec and w_spec and n_spec and ex, "SPEC §17.4 wording changed; update this test with it"
    assert int(h_spec.group(1)) == int(hrow.group(1)) and int(n_spec.group(1)) == int(wsize.group(1))
    for n in range(int(n_spec.group(1)), 200):
        h_thr, w_thr = _threshold(h_spec.group(2), n), _threshold(w_spec.group(1), n)
        assert h_thr == Q(int(hrow.group(1)), n - 1)          # uniform row: (N-1)·c ≤ bound
        assert w_thr == Q(int(wthr.group(1)), n)              # n·c ≤ bound
        assert h_thr <= w_thr and ((h_thr == w_thr) == (n == int(n_spec.group(2))))
    # the example inside (1/(N-1), 2/N]: a mean-zero mode stays bounded, HeteroStepRef's witness grows
    n, c = int(ex.group(1)), Q(int(ex.group(2)), int(ex.group(3)))
    assert _threshold(h_spec.group(2), n) < c <= _threshold(w_spec.group(1), n)
    assert abs(1 - (n - 1) * c) + c <= 1                                         # coefficient_bound's conclusion
    gw = _stmt("HeteroStepRef.lean", "growth_witness")
    assert "let v : ℕ → Fin n → ℝ := fun k _ => if k = 0 then 1 else -1" in gw
    assert "|linearStep n d dt B v 0 i| = 2 * dt * row n B i - 1" in gw and "(hr : 1 < dt * row n B i)" in gw
    r = (n - 1) * c                                   # dt * row_i at dt = 1, zero diagonal, b = c
    assert r > 1 and abs(_lin(1, r, -r, 1, 0, None)) == 2 * r - 1 > 1


def test_engine_citations_match_engine_source():
    eng = (REPO / "aief_experiment_engine_v1.py").read_text().splitlines()
    block = lambda a, b: "\n".join(eng[a - 1:b])
    mpb, het = SRC["MatrixPhaseBridge.lean"], SRC["HeteroStepRef.lean"]
    for cite in ("lines 823 and 830–839", "lines 841–844", "lines 836–839"):
        assert cite in mpb, cite
    assert "engine lines 830–839" in het
    assert eng[822].strip() == "state.B = B_projected"
    assert "# Update theta" in block(830, 839) and "delayed = state.history[0]" in block(830, 839)
    assert "np.sin(delayed[None, :] - state.theta[:, None])" in block(830, 839)
    assert "np.mod(" in block(836, 839) and "2.0 * np.pi" in block(836, 839)
    assert "state.history.append(state.theta.copy())" in block(841, 844) and "state.history.pop(0)" in block(841, 844)
