"""Lean intake of Arena_Researcher_06020041 cycles 13 and 21 (SPEC §16): pin CommonRootSimple.lean and
EngineStepRef.lean and their mutants M110-M129 / controls E18-E20 without running Lean.

CommonRootSimple.lean (audit-inbox 380052e): the common-mode polynomial X^(d+1) - (1-h) X^d - h has the simple
root 1 (h > 0), and for 0 < h < 1 it is the only unit-circle root.
EngineStepRef.lean (audit-inbox 8fc0d24): an idealized fixed-weight phase step and its directional derivative at a
prepared rotating history. It is a reference model only; the engine citations are re-checked against the engine
source below, so a moved or edited engine block fails this test.

Run: /workspace/venv-pt/bin/pytest -q research/lean_gate/tests/test_lean_gate_arena_intake.py
"""
import hashlib
import math
import re
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_mutation_check as mc  # noqa: E402

REPO = HERE.parents[2]
PROJ = REPO / "lean" / "AIEFGateCore"
FILES = ("CommonRootSimple.lean", "EngineStepRef.lean")
SRC = {f: (PROJ / "AIEFGateCore" / f).read_text() for f in FILES}

STATEMENT = [("M110", "CommonRootSimple.lean", "root_multiplicity_one", "false_multiplicity_no_pos"),
             ("M111", "CommonRootSimple.lean", "unit_circle_root_unique_and_simple", "false_unit_root_no_upper"),
             ("M112", "CommonRootSimple.lean", "unit_circle_root_unique_and_simple", "false_unit_root_no_pos"),
             ("M113", "CommonRootSimple.lean", "derivative_at_one", "false_derivative_no_delay"),
             ("M114", "EngineStepRef.lean", "orbit_invariant", "false_orbit_backward"),
             ("M115", "EngineStepRef.lean", "orbit_invariant", "false_orbit_no_frequency"),
             ("M116", "EngineStepRef.lean", "head_derivative_block", "false_block_no_pos"),
             ("M117", "EngineStepRef.lean", "history_derivative", "false_history_no_shift"),
             ("M118", "EngineStepRef.lean", "neighbor_derivative", "false_neighbor_current_slot")]


def test_modules_imported_and_hash_pinned():
    root = (PROJ / "AIEFGateCore.lean").read_text()
    sums = (PROJ / "AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt").read_text()
    for f in FILES:
        assert re.search(rf"^import AIEFGateCore\.{f[:-5]}$", root, re.M), f
        digest = hashlib.sha256((PROJ / "AIEFGateCore" / f).read_bytes()).hexdigest()
        assert f"{digest}  AIEFGateCore/{f}" in sums, f


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
    assert [m[0].split("_")[0] for m in ms] == [s[0] for s in STATEMENT]
    ns = {"CommonRootSimple.lean": "CommonRootSimple", "EngineStepRef.lean": "EngineStepRef"}
    for (num, f, thm, refuter), (name, mf, t, edits, closure, term, engine) in zip(STATEMENT, ms):
        assert (mf, t, closure, engine) == (f, thm, "", None), name
        assert len(edits) == 1 and edits[0][2] == 1, name
        assert mc.mutate(SRC[f], t, edits) != SRC[f], name
        assert term == f"{ns[f]}.{refuter} H", name
        assert re.search(rf"^theorem {refuter}\b", SRC[f], re.M), name
        before, after = mc.statement_prop(SRC[f], t, ""), mc.statement_prop(mc.mutate(SRC[f], t, edits), t, "")
        assert before != after, name


def test_def_mutants_and_controls():
    de = [m for m in mc.DEF_MUTANTS if m[1] in FILES]
    assert [int(m[0].split("_")[0][1:]) for m in de] == list(range(119, 130))
    for name, f, edits, pins in de:
        assert mc.mutate_file(SRC[f], edits) != SRC[f], name
        assert pins and set(pins) <= set(mc.VALUE_PROBES[f]), name
    for f in FILES:
        for p in mc.VALUE_PROBES[f]:
            assert p.startswith("probe_") and re.search(rf"^theorem {p}\b", SRC[f], re.M), (f, p)
    eq = [c for c in mc.EQUIV_CONTROLS if c[1] in FILES]
    assert [c[0].split("_")[0] for c in eq] == ["E18", "E19", "E20"]
    for name, f, edits in eq:
        assert mc.mutate_file(SRC[f], edits) != SRC[f], name
    # the refutation files must see the definitions the new statements mention
    for n in ("commonPoly", "clippedWeight phaseHead phaseStep orbitPath", "Polynomial (derivative)"):
        assert n in mc.OPENS, n


def _common(d, h, z):
    return z ** (d + 1) - (1 - h) * z ** d - h


def test_probe_and_witness_values_exact():
    assert _common(1, Q(1, 2), Q(2)) == Q(5, 2) and _common(2, Q(1, 2), Q(2)) == Q(11, 2)   # value probes
    assert all(_common(d, h, Q(1)) == 0 for d in (0, 1, 5) for h in (Q(-1), Q(1, 3), Q(2)))  # common_root
    # derivative at 1 is (d+1) - (1-h) d = 1 + d h: 3/2 at (1, 1/2); 3 != 2 at (2, 1) (M113)
    der = lambda d, h: (d + 1) - (1 - h) * d
    assert der(1, Q(1, 2)) == Q(3, 2) and der(2, Q(1)) == 3 != 1 + Q(1)
    # M110/M112: d = 1, h = -1 gives (X - 1)^2; M111: d = 1, h = 1 has the unit root -1
    assert [_common(1, Q(-1), Q(z)) for z in (0, 2, 3)] == [(z - 1) ** 2 for z in (0, 2, 3)]
    assert _common(1, Q(1), Q(-1)) == 0
    # EngineStepRef value probes: head 2 * (1/4 + 1/2 * sin(pi/2)) = 3/2; orbit 5 - 2*2*3 + 7*2 = 7
    assert math.isclose(0 + 2 * (0.25 + 0.5 * math.sin(math.pi / 2 - 0)), 1.5)
    assert 5 - 2 * 2 * 3 + 7 * 2 == 7
    # the mutants' values differ: self coupling 5/2, current slot 1/2, reversed sine -1/2... all != 3/2
    for v in (2 * (0.25 + 0.5 + 0.5), 2 * 0.25, 2 * (0.25 - 0.5), 2 * 0.25 + 0.5):
        assert not math.isclose(v, 1.5)


def test_engine_citations_match_engine_source():
    eng = (REPO / "aief_experiment_engine_v1.py").read_text().splitlines()
    block = lambda a, b: "\n".join(eng[a - 1:b])
    src = SRC["EngineStepRef.lean"]
    for a, b in ((789, 797), (830, 839), (841, 844)):
        assert f"lines {a}–{b}" in src, (a, b)
    assert "# Update B" in block(789, 797) and "np.maximum(B_unprojected, 0.0)" in block(789, 797)
    assert "np.fill_diagonal(B_unprojected, 0.0)" in block(789, 797)
    assert "# Update theta" in block(830, 839) and "delayed = state.history[0]" in block(830, 839)
    assert "np.sin(delayed[None, :] - state.theta[:, None])" in block(830, 839)
    assert "state.theta + config.dt * (omega_arr + coupling)" in block(830, 839)
    assert "state.history.append(state.theta.copy())" in block(841, 844)
    assert "state.history.pop(0)" in block(841, 844)
