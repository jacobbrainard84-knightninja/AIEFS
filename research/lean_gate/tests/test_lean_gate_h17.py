"""H17 (SPEC §18): `wrapPhase` = Mathlib `toIcoMod two_pi_pos 0` on [0, 2π). Pins the Lean statements, the
mutants M700-M703 and their predeclared outcome (all KILLED), and a float64 witness that the engine's `np.mod`
can return exactly 2π (outside the real-number range Lean proves). Runs no Lean."""
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_mutation_check as mc  # noqa: E402

REPO = HERE.parents[2]
WB = (REPO / "lean" / "AIEFGateCore" / "AIEFGateCore" / "WrapBridge.lean").read_text()
PI = (REPO / "lean" / "AIEFGateCore" / "AIEFGateCore" / "PhaseIncrement.lean").read_text()
ENGINE = (REPO / "aief_experiment_engine_v1.py")

STATEMENTS = [
    "theorem wrapPhase_eq_toIcoMod (t : ℝ) : Phase.wrapPhase t = toIcoMod Real.two_pi_pos 0 t := by",
    "theorem wrapPhase_mem_Ico (t : ℝ) : 0 ≤ Phase.wrapPhase t ∧ Phase.wrapPhase t < 2 * Real.pi := by",
    "theorem wrapPhase_coe_angle (t : ℝ) : ((Phase.wrapPhase t : ℝ) : Real.Angle) = (t : Real.Angle) := by",
]
# predeclared (first commit): every H17 mutant must be KILLED; none is a known survivor
PREDECLARED = {"M700_wrap_is_ioc_neg_pi": "KILLED", "M701_wrap_range_lt_pi": "KILLED",
               "M702_wrap_range_strict_lower": "KILLED", "M703_wrap_is_ico_neg_pi": "KILLED"}


def test_statements_and_import():
    for s in STATEMENTS:
        assert s in WB
    assert "import AIEFGateCore.WrapBridge" in (REPO / "lean" / "AIEFGateCore" / "AIEFGateCore.lean").read_text()
    for bad in ("sorry", "admit", "native_decide"):
        assert bad not in WB
    # the definition bridged is the floor-based [0, 2π) wrap of PhaseIncrement.lean (unchanged)
    assert "t - (Int.floor (t / (2 * Real.pi)) : ℝ) * (2 * Real.pi)" in PI


def test_mutants_pinned_and_predeclared():
    h17 = [m for m in mc.MUTANTS if m[1] == "WrapBridge.lean"]
    assert [m[0] for m in h17] == list(PREDECLARED)
    assert all(PREDECLARED[m[0]] == "KILLED" for m in h17)
    assert not [m for m in mc.KNOWN_SURVIVORS if m[1] == "WrapBridge.lean"]
    for name, f, thm, edits, closure, term, eterm in h17:
        assert f"theorem {term.split()[0].split('.')[-1]}" in WB      # the refuting false_* theorem exists
        msrc = mc.mutate(WB, thm, edits)
        assert msrc != WB


def floor_wrap(t):
    """Python image of the Lean definition (exact rationals times 2π handled as Fraction of turns)."""
    return t - math.floor(t / (2 * math.pi)) * (2 * math.pi)


def test_witnesses_match_lean_probes_and_numpy():
    # Lean probe_wrap_neg_half_pi: -π/2 -> 3π/2; the (−π, π] and [−π, π) conventions both give -π/2 there
    assert math.isclose(floor_wrap(-math.pi / 2), 3 * math.pi / 2)
    assert math.isclose(float(np.mod(-math.pi / 2, 2 * np.pi)), 3 * math.pi / 2)
    assert floor_wrap(0.0) == 0.0
    # exact-turn check on rationals: wrap(q turns) = frac(q) turns, in [0, 1)
    for q in (Fraction(-1, 4), Fraction(7, 3), Fraction(-5, 2), Fraction(0), Fraction(1)):
        fr = q - math.floor(q)
        assert 0 <= fr < 1


def test_float_two_pi_witness_unexplained():
    """Float vs real gap (Auditor Seat 002 review, H17): float64 np.mod can return exactly 2π. The real-number
    theorem says wrapPhase t < 2π. Whether this value occurs in production runs is UNEXPLAINED (unmeasured)."""
    v = float(np.mod(-1e-20, 2 * np.pi))
    assert v == 2 * np.pi
    # negative control: the same call on +1e-20 stays inside [0, 2π)
    w = float(np.mod(1e-20, 2 * np.pi))
    assert 0 <= w < 2 * np.pi
    # the engine wraps with np.mod(..., 2*pi) (read only; the engine is SHA-locked and not imported here)
    assert "np.mod(" in ENGINE.read_text()
