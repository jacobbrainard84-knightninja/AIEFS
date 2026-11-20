"""Lean intake of Arena_Researcher_06020041's EMA radial note (SPEC §17): pin EmaRadialRef.lean and its mutants
M131-M142 / control E21 without running Lean.

EmaRadialRef.lean (audit-inbox db0638f, AIEFS_ema_radial/): along the stipulated normalized path
old(t) = 1 + t(u + iv), input(t) = exp(i t delta), the EMA alpha*old + (1-alpha)*input has magnitude derivative
alpha*u at t = 0. coherenceStep_eq_path / coherenceStep_norm_eq_magnitude connect it to
PhaseCoherence.coherenceStep under explicit hypotheses only; the engine citations are re-checked below.

Run: /workspace/venv-pt/bin/pytest -q research/lean_gate/tests/test_lean_gate_ema_radial.py
"""
import cmath
import hashlib
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_mutation_check as mc  # noqa: E402

REPO = HERE.parents[2]
PROJ = REPO / "lean" / "AIEFGateCore"
F = "EmaRadialRef.lean"
SRC = (PROJ / "AIEFGateCore" / F).read_text()

STATEMENT = [("M131", "real_direction", "false_real_no_alpha"),
             ("M132", "imag_direction", "false_imag_no_input"),
             ("M133", "magnitude_direction", "false_magnitude_no_alpha"),
             ("M134", "magnitude_direction", "false_magnitude_angular"),
             ("M135", "sym_magnitude_direction", "false_sym_first_only")]


def test_module_imported_and_hash_pinned():
    root = (PROJ / "AIEFGateCore.lean").read_text()
    sums = (PROJ / "AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt").read_text()
    assert re.search(r"^import AIEFGateCore\.EmaRadialRef$", root, re.M)
    assert re.search(r"^import AIEFGateCore\.PhaseCoherence$", SRC, re.M)
    digest = hashlib.sha256((PROJ / "AIEFGateCore" / F).read_bytes()).hexdigest()
    assert f"{digest}  AIEFGateCore/{F}" in sums


def test_no_escape_hatches_and_axioms_printed():
    code = re.sub(r"/-.*?-/", "", SRC, flags=re.S)
    code = re.sub(r"--.*", "", code)
    for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern"):
        assert bad not in code, bad
    for thm in re.findall(r"^theorem (\S+)", SRC, re.M):
        assert re.search(rf"^#print axioms (AIEFGate\.\w+\.)?{thm}$", SRC, re.M), thm


def test_bridge_to_coherence_step_is_stated_with_hypotheses():
    for thm in ("path_eq", "coherenceStep_eq_path", "coherenceStep_norm_eq_magnitude"):
        assert re.search(rf"^theorem {thm}\b", SRC, re.M), thm
    span = SRC[SRC.index("theorem coherenceStep_norm_eq_magnitude"):]
    span = span[:span.index(":= by")]
    assert "(hp : ‖p‖ = 1)" in span and "(hC : C i j =" in span and "PhaseCoherence.coherenceInput" in span
    assert "‖PhaseCoherence.coherenceStep" in span and "magnitude alpha u v delta t" in span


def test_statement_mutants_exact_shape():
    ms = [m for m in mc.MUTANTS if m[1] == F]
    assert [m[0].split("_")[0] for m in ms] == [s[0] for s in STATEMENT]
    for (num, thm, refuter), (name, mf, t, edits, closure, term, engine) in zip(STATEMENT, ms):
        assert (mf, t, closure, engine) == (F, thm, "", None), name
        assert len(edits) == 1 and edits[0][2] == 1, name
        assert mc.mutate(SRC, t, edits) != SRC, name
        assert term == f"EmaRadialRef.{refuter} H", name
        assert re.search(rf"^theorem {refuter}\b", SRC, re.M), name
        assert mc.statement_prop(SRC, t, "") != mc.statement_prop(mc.mutate(SRC, t, edits), t, ""), name


def test_definition_mutants_and_control():
    de = [m for m in mc.DEF_MUTANTS if m[1] == F]
    assert [int(m[0].split("_")[0][1:]) for m in de] == list(range(136, 143))
    for name, f, edits, pins in de:
        assert mc.mutate_file(SRC, edits) != SRC, name
        assert pins and set(pins) <= set(mc.VALUE_PROBES[F]), name
    for p in mc.VALUE_PROBES[F]:
        assert p.startswith("probe_") and re.search(rf"^theorem {p}\b", SRC, re.M), p
    eq = [c for c in mc.EQUIV_CONTROLS if c[1] == F]
    assert [c[0].split("_")[0] for c in eq] == ["E21"]
    assert mc.mutate_file(SRC, eq[0][2]) != SRC
    assert "open AIEFGate.EmaRadialRef (reStep imStep magnitude symMagnitude)" in mc.OPENS


def _re(a, u, d, t, f=math.cos, w=None):
    return a * (1 + t * u) + ((1 - a) if w is None else w) * f(t * d)


def _im(a, v, d, t, f=math.sin):
    return a * (t * v) + (1 - a) * f(t * d)


def _mag(a, u, v, d, t):
    return math.hypot(_re(a, u, d, t), _im(a, v, d, t))


def test_probe_values_and_mutant_values_exact():
    assert _re(0.5, 1, 0, 0) == 1 and math.isclose(_re(0.25, 2, 0, 1), 1.5)
    assert math.isclose(_re(0.5, 1, 0, 0, math.sin), 0.5)              # M136
    assert math.isclose(_re(0.25, 2, 0, 1, w=0.25), 1.0)               # M137
    assert math.isclose(_im(0.5, 2, 0, 1), 1.0) and math.isclose(_im(0.5, 2, 0, 1, math.cos), 1.5)   # M138
    assert math.isclose(_mag(0.5, 1, 4, 0, 1), 2.5)
    assert math.isclose(_re(0.5, 1, 0, 1) ** 2 + _im(0.5, 4, 0, 1) ** 2, 6.25)   # M139: 25/4
    assert math.isclose(abs(_re(0.5, 1, 0, 1)), 1.5)                   # M140
    m1, m2 = _mag(0.5, 1, 4, 0, 1), _mag(0.5, -1, 0, 0, 1)
    assert math.isclose((m1 + m2) / 2, 1.5) and math.isclose(m1, 2.5) and math.isclose(m1 + m2, 3.0)   # M141/M142


def test_path_matches_coherence_step_numerically():
    # alpha*p*old + (1-alpha)*p*exp(i t delta) has modulus magnitude(...) for |p| = 1
    for a, u, v, d, t, th in ((0.5, 1, 4, 0, 1, 0.3), (0.9, -0.2, 0.7, 1.3, 0.05, 2.0)):
        p = cmath.exp(1j * th)
        step = a * p * (1 + t * complex(u, v)) + (1 - a) * p * cmath.exp(1j * t * d)
        assert math.isclose(abs(step), _mag(a, u, v, d, t))


def test_engine_citations_match_engine_source():
    eng = (REPO / "aief_experiment_engine_v1.py").read_text().splitlines()
    block = lambda a, b: "\n".join(eng[a - 1:b])
    assert "lines 735–745" in SRC and "lines 747–750" in SRC
    assert "z_inst = np.exp(1j * dphi)" in block(735, 745) and "# Update EMA" in block(735, 745)
    assert "config.alpha * state.coherence_acc + (1.0 - config.alpha) * z_inst" in block(735, 745)
    assert "np.abs(state.coherence_acc)" in block(747, 750) and "0.5 * (result + result.T)" in block(747, 750)
    assert "np.fill_diagonal(result, 0.0)" in block(747, 750)
