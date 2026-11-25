/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.EmaNearUnit
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Angle

/-!
# Wrap-invariant phase-spread hypothesis for the EMA bound (Arena D9)

Research candidate. Replaces the unwrapped `|phase difference| ≤ β` hypothesis of `EmaNearUnit` by
the `2π`-periodic cosine condition `arcBound`; an exact witness shows a 3-degree spread across the
wrap point is accepted by `arcBound` and rejected by the absolute-value form. Value probe and
`false_*` witness appended (SPEC §17).

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D9, deposit sha256 `5d05160b…`; proofs and
statements unchanged from the deposit.
-/

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

/-! ### Value probe and negation used by the mutation harness (SPEC §17) -/

/-- `arcBound φ β` is `cos β ≤ cos φ`: `φ = 0` is within any `β`, `φ = π` is not within `β = 0`.
The reversed inequality fails the first conjunct (`1 ≤ 0`). -/
theorem probe_arcBound_values : arcBound 0 (Real.pi / 2) ∧ ¬ arcBound Real.pi 0 := by
  constructor
  · simp [arcBound]
  · norm_num [arcBound]

/-- Dropping the startup loss `α^N` from the budget of `near_unit_circular_spread` is false
(`N = 0`, `β = 0`, `ε = 0`). -/
theorem false_circular_no_startup :
    ¬ (∀ {V : Type*} (alpha beta epsilon : ℝ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
      (omega : V → ℝ) (tau : ℝ) (i j : V) (N : ℕ) (_ha : 0 ≤ alpha) (_ha1 : alpha ≤ 1)
      (_hspread : ∀ k < N, arcBound (Phase.phaseTrace x0 u k i -
        Phase.phaseTrace x0 u (k - d) j - ((omega i + omega j) / 2) * tau) beta)
      (_budget : (1 - Real.cos beta) ≤ epsilon),
      1 - epsilon ≤ ‖coherenceTrace alpha (fun _ _ => 0) d x0 u omega tau N i j‖) := by
  intro H
  have h := @H PUnit 0 0 0 0 (fun _ => 0) (fun _ _ => 0) (fun _ => 0) 0 PUnit.unit PUnit.unit 0
    le_rfl zero_le_one (fun k hk => absurd hk (Nat.not_lt_zero k)) (by norm_num)
  norm_num [coherenceTrace] at h

#print axioms probe_arcBound_values
#print axioms false_circular_no_startup

end AIEFGate.EmaWrapInvariant
