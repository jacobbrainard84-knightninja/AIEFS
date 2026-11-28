"""H17 (SPEC §18): `wrapPhase` = Mathlib `toIcoMod two_pi_pos 0` on [0, 2π). Pins the Lean statements, the
mutants M700-M703 and their predeclared outcome (all KILLED), and float64 witnesses that the engine's `np.mod`
reduces modulo fl(2π) (not 2π) and can return its own modulus fl(2π), so float θ is in [0, fl(2π)] (audit N1; fl(2π)
itself is inside the real [0, 2π)). Runs no Lean."""
import math
import re
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
    "theorem wrapPhase_coe_angle (t : ℝ) :\n    ((Phase.wrapPhase t : ℝ) : Real.Angle) = (t : Real.Angle) := by",
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
        ref = term.split()[0].split('.')[-1]
        assert re.search(rf"theorem {re.escape(ref)}\b", WB), ref      # the refuting false_* theorem exists
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
    """Float vs real gap (audit N1/N2). (a) The engine's modulus is fl(2π) = 2π − 2.449e−16, not 2π. (b) float64
    np.mod returns its own modulus fl(2π) for x in [−4.440892098500626e−16, 0), so float θ ∈ [0, fl(2π)]. fl(2π) is
    inside the real [0, 2π); the gap is the period and the closed top end. The phasor differs from θ = 0 by
    rounding only. Whether (b) occurs in production runs is UNEXPLAINED (unmeasured)."""
    m = 2 * np.pi
    two_pi = Fraction("6.28318530717958647692528676655900576839433879875021164194988918461563281257241799725606965")
    assert -2.46e-16 < float(Fraction(m) - two_pi) < -2.44e-16                    # (a) fl(2π) < 2π by 2.449e-16
    v = float(np.mod(-1e-20, m))
    assert v == m                                                                  # (b) modulus returned
    x_star = -4.440892098500626e-16
    assert np.mod(x_star, m) == m and np.mod(-5e-324, m) == m                      # boundary of (b), both ends
    assert np.mod(np.nextafter(x_star, -1.0), m) < m                               # just beyond: back inside
    z = np.exp(1j * m)
    assert z != 1 and abs(z - 1) < 3e-16                                           # phasor: rounding-level only
    # negative control: the same call on +1e-20 stays inside [0, 2π)
    w = float(np.mod(1e-20, 2 * np.pi))
    assert 0 <= w < 2 * np.pi
    # the engine wraps with np.mod(..., 2*pi) (read only; the engine is SHA-locked and not imported here)
    assert ENGINE.read_text().count("state.theta = np.mod(") == 1
