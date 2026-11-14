"""Lean C014: pin TrajectoryInvariants.lean (port of cycle 014 of Researcher 040282, namespace
AIEFGate.TrajectorySafety) and its mutants in lean_mutation_check.py without running Lean.

Mutants (numbered from M71 because M59-M70 are reserved for the c016 port):
  statement M71 post_capacity `(p n).cap` -> `(p (n + 1)).cap`  (refuted by capacity_clock_refuted)
            M72 all_times_structural hInit := True             (refuted by initial_time_refuted)
            M73 post_capacity hp (EngineGate) := True          (refuted by broken_link_refuted, at `pB`)
  definition M74 weightUpdate := symM (gate bypassed)          (probe_gate_scales_row)
             M75 feedbackStep hands U the old B twice          (probe_aux_reads_old_and_new; the survivor of
                                                               Researcher 001's audit of 9b9b3d9)
             M76 feedbackStep hands U the new B twice          (probe_aux_reads_old_and_new)
  equivalence control E11: the `let Bnew` of feedbackStep inlined, must NOT be killed.
The two value probes are recomputed here in exact rational arithmetic from the definitions (hand-checked).

Run: /workspace/venv-pt/bin/pytest -q research/lean_gate/tests/test_lean_gate_c014.py
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
F = "TrajectoryInvariants.lean"
SRC = (PROJ / "AIEFGateCore" / F).read_text()

STATEMENT = [("M71", "post_capacity", "capacity_clock_refuted"),
             ("M72", "all_times_structural", "initial_time_refuted"),
             ("M73", "post_capacity", "broken_link_refuted")]
DEF = [("M74", ["probe_gate_scales_row"]), ("M75", ["probe_aux_reads_old_and_new"]),
       ("M76", ["probe_aux_reads_old_and_new"])]


def c014_statement_mutants():
    return [m for m in mc.MUTANTS if m[1] == F]


def c014_def_mutants():
    return [m for m in mc.DEF_MUTANTS if m[1] == F]


def test_module_is_imported_and_hash_pinned():
    root = (PROJ / "AIEFGateCore.lean").read_text()
    assert re.search(r"^import AIEFGateCore\.TrajectoryInvariants$", root, re.M)
    sums = (PROJ / "AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt").read_text()
    digest = hashlib.sha256((PROJ / "AIEFGateCore" / F).read_bytes()).hexdigest()
    assert f"{digest}  AIEFGateCore/{F}" in sums


def test_no_escape_hatches_and_axioms_printed():
    code = re.sub(r"/-.*?-/", "", SRC, flags=re.S)
    code = re.sub(r"--.*", "", code)
    for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern"):
        assert bad not in code, bad
    for probe in mc.VALUE_PROBES[F]:
        assert re.search(rf"^theorem {probe}\b", SRC, re.M), probe
        assert f"#print axioms AIEFGate.TrajectorySafety.{probe}\n" in SRC, probe


def test_statement_mutants_exact_shape():
    ms = c014_statement_mutants()
    assert [m[0].split("_")[0] for m in ms] == [s[0] for s in STATEMENT]
    assert mc.MUTANTS[-3:] == ms                       # appended after M57, M58
    for (num, thm, refuter), (name, f, t, edits, closure, term, engine) in zip(STATEMENT, ms):
        assert t == thm and closure == mc.TS_VARS and engine is None, name
        assert mc.mutate(SRC, t, edits) != SRC, name   # each edit matches exactly `count` times in the statement
        assert re.search(rf"^theorem {refuter}\b", SRC, re.M), (name, refuter)
        assert term.startswith(f"TrajectorySafety.{refuter} (@H (Fin 2) Unit _ _ "), name
    # the refutation context opens the C014 names the mutated statements use
    assert "open AIEFGate.TrajectorySafety (Weights weightsTrace Structural)" in mc.OPENS


def test_def_mutants_exact_shape_and_value_probe_pins():
    ms = c014_def_mutants()
    assert [m[0].split("_")[0] for m in ms] == [d[0] for d in DEF]
    assert mc.DEF_MUTANTS[-3:] == ms                   # appended after the P5 mutants M37-M56
    for (num, pins), (name, f, edits, got) in zip(DEF, ms):
        assert got == pins and set(got) <= set(mc.VALUE_PROBES[F]), name
        assert mc.mutate_file(SRC, edits) != SRC, name
    assert "symM p D B" in ms[0][2][0][1]
    assert "(U n state.1 state.2 state.2, Bnew)" in ms[1][2][0][1]
    assert "(U n state.1 Bnew Bnew, Bnew)" in ms[2][2][0][1]
    e11 = [c for c in mc.EQUIV_CONTROLS if c[0].startswith("E11_")]
    assert len(e11) == 1 and e11[0][1] == F and mc.mutate_file(SRC, e11[0][2]) != SRC
    assert not [s for s in mc.KNOWN_SURVIVORS if s[1] == F]


def test_numbering_leaves_m59_to_m70_for_c016():
    nums = sorted(int(m[0].split("_")[0][1:]) for m in mc.MUTANTS + mc.DEF_MUTANTS)
    assert not [n for n in nums if 59 <= n <= 70]
    assert [n for n in nums if n >= 71] == [71, 72, 73, 74, 75, 76]
    assert len(nums) == len(set(nums))


# ---- the value probes, recomputed from the definitions (exact rationals) ----------------------------------------

def params(t):
    return dict(zip(("dt", "g", "cap", "eps", "gapA", "gapQ", "gapDelta"), map(Q, t)))


P_WIDE = params((1, 1, 2, 1, 2, 1, 0))
P_TIGHT = params((1, 1, 1, 1, 1, 1, 0))


def Xo(a):
    return [[Q(0), Q(a)], [Q(a), Q(0)]]


def stepM(p, D, B, gate=True):
    pre = [[B[i][j] * (1 - p["g"] * p["dt"]) + p["dt"] * D[i][j] for j in range(2)] for i in range(2)]
    clip = [[max(pre[i][j], Q(0)) for j in range(2)] for i in range(2)]
    sym = [[Q(0) if i == j else (clip[i][j] + clip[j][i]) / 2 for j in range(2)] for i in range(2)]
    rows = [sum(r) for r in sym]
    if not gate or not any(p["gapA"] - p["gapQ"] * r < p["gapDelta"] for r in rows):
        return sym
    sc = [min(Q(1), p["cap"] / (r + p["eps"])) for r in rows]
    return [[Q(0) if i == j else sym[i][j] * min(sc[i], sc[j]) for j in range(2)] for i in range(2)]


def test_model_matches_lean_definitions():
    mf = (PROJ / "AIEFGateCore" / "MatrixForm.lean").read_text()
    assert "  Bm i j + p.dt * (D i j - p.γ * Bm i j)\n" in mf                     # preM, as modelled above
    assert "  max (preM p D Bm i j) 0\n" in mf                                     # clipM
    assert "  if i = j then 0 else (clipM p D Bm i j + clipM p D Bm j i) / 2\n" in mf  # symM
    gm = (PROJ / "AIEFGateCore" / "GateMap.lean").read_text()
    assert "  min 1 (p.cap / (q + p.ε))\n" in gm                                   # scale
    cap = (PROJ / "AIEFGateCore" / "Capacity.lean").read_text()
    assert "  ∃ i, p.gapA - p.gapQ * rowS X i < p.gapDelta\n" in cap               # GateOnX
    assert "  if i = j then 0 else X i j * min (scale p (rowS X i)) (scale p (rowS X j))\n" in cap   # kernelM
    assert "def pTight : Params := ⟨1, 1, 1, 1, 1, 1, 0⟩" in SRC and "def pWide : Params := ⟨1, 1, 2, 1, 2, 1, 0⟩" in SRC


def test_probe_gate_scales_row_value():
    zero = Xo(0)
    assert sum(stepM(P_TIGHT, Xo(3), zero)[0]) == Q(3, 4)          # probe_gate_scales_row
    assert sum(stepM(P_TIGHT, Xo(3), zero, gate=False)[0]) == 3     # M74 (gate bypassed) gives 3
    assert "theorem probe_gate_scales_row : Capacity.rowS (weightUpdate pTight (X 3) zeroB) 0 = 3 / 4" in SRC


def test_probe_aux_reads_old_and_new_value():
    dirty = [[Q(-1), Q(1)], [Q(1), Q(-1)]]
    new = stepM(P_WIDE, Xo(1), dirty)
    assert new == Xo(1)                                              # wide_resets_one
    aux = lambda old, nw: old[0][0] + 10 * nw[0][0]                 # auxOldNew
    assert aux(dirty, new) == -1                                     # probe_aux_reads_old_and_new
    assert aux(dirty, dirty) == -11 and aux(new, new) == 0           # M75 and M76 change the value
    assert "def auxOldNew (_ : ℕ) (_ : ℝ) (Bold Bnew : Weights (Fin 2)) : ℝ := Bold 0 0 + 10 * Bnew 0 0" in SRC
    assert "(trajectory (fun _ => pWide) oneDriveR auxOldNew ((0 : ℝ), dirtyB) 1).1 = -1" in SRC
