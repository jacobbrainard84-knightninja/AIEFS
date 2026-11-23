import AIEFGateCore.EmaNearUnit
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Angle

set_option autoImplicit false
namespace AIEFGate.EmaWrapInvariant

open AIEFGate.PhaseCoherence AIEFGate.EmaNearUnit

/-- Cosine-based closeness to the positive real-axis phasor. -/
def arcBound (phi beta : ℝ) : Prop := Real.cos beta ≤ Real.cos phi

/-- The hypothesis is unchanged by shifting an angle representative by 2π. -/
theorem arcBound_periodic (phi beta : ℝ) (m : ℤ) :
    arcBound (phi + (m : ℝ) * (2 * Real.pi)) beta ↔ arcBound phi beta := by
  simp only [arcBound, Real.cos_add_int_mul_two_pi]

/-- Near-unit bound for the main coherence trace from zero, using a periodic
phasor-alignment hypothesis instead of the unwrapped absolute-value condition. -/
theorem near_unit_circular_spread {V : Type*} (alpha beta epsilon : ℝ)
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (i j : V) (N : ℕ) (ha : 0 ≤ alpha) (ha1 : alpha ≤ 1)
    (hspread : ∀ k < N, arcBound (Phase.phaseTrace x0 u k i -
      Phase.phaseTrace x0 u (k - d) j - ((omega i + omega j) / 2) * tau) beta)
    (budget : alpha ^ N + (1 - Real.cos beta) ≤ epsilon) :
    1 - epsilon ≤ ‖coherenceTrace alpha (fun _ _ => 0) d x0 u omega tau N i j‖ := by
  apply near_unit alpha (1 - Real.cos beta) epsilon d x0 u omega tau i j N ha ha1
    (sub_nonneg.mpr (Real.cos_le_one beta)) _ budget
  intro k hk
  have hc := hspread k hk
  unfold arcBound at hc
  rw [input_engine_convention, mul_comm, Complex.exp_ofReal_mul_I_re]
  linarith

/-- An exact witness: the wrapped representative is 2π - π/60,
while the circular displacement is -π/60 (three degrees). -/
theorem cross_wrap_angle :
    ((2 * Real.pi - Real.pi / 60 : ℝ) : Real.Angle) =
      ((-(Real.pi / 60) : ℝ) : Real.Angle) := by
  simp [Real.Angle.coe_sub, Real.Angle.coe_two_pi, Real.Angle.coe_neg]

theorem cross_wrap_good : arcBound (2 * Real.pi - Real.pi / 60) (Real.pi / 60) := by
  simp [arcBound, Real.cos_two_pi_sub]

theorem cross_wrap_rejected : ¬|2 * Real.pi - Real.pi / 60| ≤ Real.pi / 60 := by
  have hp := Real.pi_pos
  have hx : 0 ≤ 2 * Real.pi - Real.pi / 60 := by linarith
  rw [abs_of_nonneg hx]
  linarith

#print axioms arcBound_periodic
#print axioms near_unit_circular_spread
#print axioms cross_wrap_angle
#print axioms cross_wrap_good
#print axioms cross_wrap_rejected
end AIEFGate.EmaWrapInvariant
