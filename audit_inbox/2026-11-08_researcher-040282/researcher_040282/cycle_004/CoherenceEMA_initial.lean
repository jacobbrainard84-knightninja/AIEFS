/-
Researcher 040282: exact-real complex EMA and reported coherence component.
Prescribed real phase/delayed vectors are inputs, not a proof of coupled locking.
C is directed and may have a nonzero diagonal. Only reported R is symmetrized
and zero-diagonal. The source returns R AFTER updating C.
-/
import Mathlib.Analysis.Complex.Trigonometric
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

set_option autoImplicit false
set_option linter.style.header false

open Filter
open scoped Topology

namespace Researcher040282.EMA

variable {ι : Type*}

abbrev ComplexWeights (ι : Type*) := ι → ι → ℂ

noncomputable def physicalAlpha (dt Tw : ℝ) : ℝ := Real.exp (-dt / Tw)

noncomputable def phaseInput (theta delayed omega : ι → ℝ) (tau : ℝ)
    (i j : ι) : ℂ :=
  Complex.exp (((theta i - delayed j - ((omega i + omega j) / 2) * tau : ℝ) : ℂ) * Complex.I)

noncomputable def emaStep (alpha : ℝ) (C z : ℂ) : ℂ :=
  (alpha : ℂ) * C + ((1 - alpha : ℝ) : ℂ) * z

noncomputable def emaTrajectory (alpha : ℝ) (C0 : ℂ) (z : ℕ → ℂ) : ℕ → ℂ
  | 0 => C0
  | n + 1 => emaStep alpha (emaTrajectory alpha C0 z n) (z n)

noncomputable def coherenceUpdate (alpha : ℝ) (C : ComplexWeights ι)
    (theta delayed omega : ι → ℝ) (tau : ℝ) : ComplexWeights ι :=
  fun i j => emaStep alpha (C i j) (phaseInput theta delayed omega tau i j)

noncomputable def reportedR (C : ComplexWeights ι) (i j : ι) : ℝ := by
  classical
  exact if i = j then 0 else (‖C i j‖ + ‖C j i‖) / 2

noncomputable def matrixTrajectory (alpha : ℝ) (C0 : ComplexWeights ι)
    (z : ℕ → ComplexWeights ι) (n : ℕ) : ComplexWeights ι :=
  fun i j => emaTrajectory alpha (C0 i j) (fun m => z m i j) n

theorem phaseInput_norm (theta delayed omega : ι → ℝ) (tau : ℝ) (i j : ι) :
    ‖phaseInput theta delayed omega tau i j‖ = 1 := by
  simp [phaseInput, Complex.norm_exp]

theorem physicalAlpha_pos (dt Tw : ℝ) : 0 < physicalAlpha dt Tw :=
  Real.exp_pos _

theorem physicalAlpha_lt_one (dt Tw : ℝ) (hdt : 0 < dt) (hTw : 0 < Tw) :
    physicalAlpha dt Tw < 1 := by
  rw [physicalAlpha, Real.exp_lt_one_iff, neg_div]
  have := div_pos hdt hTw
  linarith

theorem emaStep_norm_le (alpha : ℝ) (C z : ℂ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) :
    ‖emaStep alpha C z‖ ≤ alpha * ‖C‖ + (1-alpha) * ‖z‖ := by
  calc
    ‖emaStep alpha C z‖ ≤ ‖(alpha : ℂ) * C‖ + ‖((1-alpha : ℝ) : ℂ) * z‖ :=
      norm_add_le _ _
    _ = alpha * ‖C‖ + (1-alpha) * ‖z‖ := by
      rw [norm_mul, norm_mul, Complex.norm_of_nonneg ha0,
        Complex.norm_of_nonneg (sub_nonneg.mpr ha1)]

theorem emaStep_unitDisk (alpha : ℝ) (C z : ℂ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ‖C‖ ≤ 1) (hz : ‖z‖ ≤ 1) :
    ‖emaStep alpha C z‖ ≤ 1 := by
  calc
    ‖emaStep alpha C z‖ ≤ alpha * ‖C‖ + (1-alpha) * ‖z‖ :=
      emaStep_norm_le alpha C z ha0 ha1
    _ ≤ alpha * 1 + (1-alpha) * 1 :=
      add_le_add (mul_le_mul_of_nonneg_left hC ha0)
        (mul_le_mul_of_nonneg_left hz (sub_nonneg.mpr ha1))
    _ = 1 := by ring

theorem emaTrajectory_unitDisk (alpha : ℝ) (C0 : ℂ) (z : ℕ → ℂ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ‖C0‖ ≤ 1)
    (hz : ∀ n, ‖z n‖ ≤ 1) : ∀ n, ‖emaTrajectory alpha C0 z n‖ ≤ 1 := by
  intro n
  induction n with
  | zero => exact hC
  | succ n ih => exact emaStep_unitDisk alpha _ _ ha0 ha1 ih (hz n)

theorem coherenceUpdate_unitDisk (alpha : ℝ) (C : ComplexWeights ι)
    (theta delayed omega : ι → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C i j‖ ≤ 1) :
    ∀ i j, ‖coherenceUpdate alpha C theta delayed omega tau i j‖ ≤ 1 := by
  intro i j
  exact emaStep_unitDisk alpha _ _ ha0 ha1 (hC i j)
    (phaseInput_norm theta delayed omega tau i j).le

theorem reportedR_nonneg (C : ComplexWeights ι) (i j : ι) :
    0 ≤ reportedR C i j := by
  classical
  unfold reportedR
  split_ifs <;> positivity

theorem reportedR_symmetric (C : ComplexWeights ι) (i j : ι) :
    reportedR C i j = reportedR C j i := by
  classical
  by_cases h : i = j
  · subst j; rfl
  · simp only [reportedR, if_neg h, if_neg (Ne.symm h)]
    ring

theorem reportedR_diag (C : ComplexWeights ι) (i : ι) : reportedR C i i = 0 := by
  simp [reportedR]

theorem reportedR_le_one (C : ComplexWeights ι) (hC : ∀ i j, ‖C i j‖ ≤ 1) (i j : ι) :
    reportedR C i j ≤ 1 := by
  classical
  by_cases h : i = j
  · simp [reportedR, h]
  · simp only [reportedR, if_neg h]
    have := hC i j
    have := hC j i
    linarith

theorem reportedR_lipschitz (C D : ComplexWeights ι) (i j : ι) :
    |reportedR C i j - reportedR D i j| ≤
      (‖C i j - D i j‖ + ‖C j i - D j i‖) / 2 := by
  classical
  by_cases h : i = j
  · subst j
    simp only [reportedR, if_pos rfl, sub_self, abs_zero]
    positivity
  · simp only [reportedR, if_neg h]
    have h1 := abs_norm_sub_norm_le (C i j) (D i j)
    have h2 := abs_norm_sub_norm_le (C j i) (D j i)
    rw [show (‖C i j‖ + ‖C j i‖) / 2 - (‖D i j‖ + ‖D j i‖) / 2 =
      ((‖C i j‖ - ‖D i j‖) + (‖C j i‖ - ‖D j i‖)) / 2 by ring,
      abs_div, abs_of_pos (by norm_num : (0 : ℝ) < 2)]
    exact div_le_div_of_nonneg_right
      ((abs_add_le _ _).trans (add_le_add h1 h2)) (by norm_num)

theorem ema_difference (alpha : ℝ) (C D z w : ℂ) :
    emaStep alpha C z - emaStep alpha D w =
      (alpha : ℂ) * (C-D) + ((1-alpha : ℝ) : ℂ) * (z-w) := by
  unfold emaStep
  ring

theorem ema_same_input_difference (alpha : ℝ) (C D z : ℂ) :
    emaStep alpha C z - emaStep alpha D z = (alpha : ℂ) * (C-D) := by
  rw [ema_difference, sub_self, mul_zero, add_zero]

theorem trajectory_same_input_difference (alpha : ℝ) (C0 D0 : ℂ)
    (z : ℕ → ℂ) (n : ℕ) :
    emaTrajectory alpha C0 z n - emaTrajectory alpha D0 z n =
      (alpha : ℂ)^n * (C0-D0) := by
  induction n with
  | zero => simp [emaTrajectory]
  | succ n ih =>
    change emaStep alpha (emaTrajectory alpha C0 z n) (z n) -
      emaStep alpha (emaTrajectory alpha D0 z n) (z n) = _
    rw [ema_same_input_difference, ih, pow_succ]
    ring

theorem trajectory_same_input_norm (alpha : ℝ) (C0 D0 : ℂ)
    (z : ℕ → ℂ) (n : ℕ) (ha0 : 0 ≤ alpha) :
    ‖emaTrajectory alpha C0 z n - emaTrajectory alpha D0 z n‖ =
      alpha^n * ‖C0-D0‖ := by
  rw [trajectory_same_input_difference, norm_mul, norm_pow, Complex.norm_of_nonneg ha0]

theorem constant_closed_form (alpha : ℝ) (C0 z : ℂ) (n : ℕ) :
    emaTrajectory alpha C0 (fun _ => z) n = z + (alpha : ℂ)^n * (C0-z) := by
  induction n with
  | zero =>
    simp only [emaTrajectory, pow_zero, one_mul]
    ring
  | succ n ih =>
    change emaStep alpha (emaTrajectory alpha C0 (fun _ => z) n) z = _
    rw [ih]
    simp only [emaStep, pow_succ]
    push_cast
    ring

theorem constant_error_norm (alpha : ℝ) (C0 z : ℂ) (n : ℕ) (ha0 : 0 ≤ alpha) :
    ‖emaTrajectory alpha C0 (fun _ => z) n - z‖ = alpha^n * ‖C0-z‖ := by
  rw [constant_closed_form]
  rw [show z + (alpha : ℂ)^n * (C0-z) - z = (alpha : ℂ)^n * (C0-z) by ring]
  rw [norm_mul, norm_pow, Complex.norm_of_nonneg ha0]

theorem constant_zero_norm (alpha : ℝ) (z : ℂ) (n : ℕ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hz : ‖z‖ = 1) :
    ‖emaTrajectory alpha 0 (fun _ => z) n‖ = 1-alpha^n := by
  have heq : emaTrajectory alpha 0 (fun _ => z) n = ((1-alpha^n : ℝ) : ℂ) * z := by
    rw [constant_closed_form]
    push_cast
    ring
  rw [heq, norm_mul, Complex.norm_of_nonneg (sub_nonneg.mpr (pow_le_one₀ ha0 ha1)),
    hz, mul_one]

theorem constant_converges (alpha : ℝ) (C0 z : ℂ) (ha0 : 0 ≤ alpha) (ha1 : alpha < 1) :
    Tendsto (emaTrajectory alpha C0 (fun _ => z)) atTop (𝓝 z) := by
  have hp : Tendsto (fun n : ℕ => (alpha : ℂ)^n) atTop (𝓝 0) :=
    tendsto_pow_atTop_nhds_zero_of_norm_lt_one (by
      rw [Complex.norm_of_nonneg ha0]
      exact ha1)
  have ht : Tendsto (fun n : ℕ => z + (alpha : ℂ)^n * (C0-z)) atTop
      (𝓝 (z + 0 * (C0-z))) := tendsto_const_nhds.add (hp.mul_const (C0-z))
  simpa only [zero_mul, add_zero, ← constant_closed_form] using ht

theorem matrix_same_input_reported_bound (alpha : ℝ) (C0 D0 : ComplexWeights ι)
    (z : ℕ → ComplexWeights ι) (n : ℕ) (ha0 : 0 ≤ alpha) (i j : ι) :
    |reportedR (matrixTrajectory alpha C0 z n) i j -
      reportedR (matrixTrajectory alpha D0 z n) i j| ≤
      alpha^n * (‖C0 i j - D0 i j‖ + ‖C0 j i - D0 j i‖) / 2 := by
  calc
    _ ≤ (‖matrixTrajectory alpha C0 z n i j - matrixTrajectory alpha D0 z n i j‖ +
        ‖matrixTrajectory alpha C0 z n j i - matrixTrajectory alpha D0 z n j i‖) / 2 :=
      reportedR_lipschitz _ _ i j
    _ = _ := by
      simp only [matrixTrajectory, trajectory_same_input_norm alpha _ _ _ n ha0]
      ring

theorem constant_zero_reported (alpha : ℝ) (z : ComplexWeights ι) (n : ℕ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hz : ∀ i j, ‖z i j‖ = 1)
    (i j : ι) (hij : i ≠ j) :
    reportedR (matrixTrajectory alpha (fun _ _ => 0) (fun _ => z) n) i j =
      1-alpha^n := by
  simp only [reportedR, if_neg hij, matrixTrajectory]
  rw [constant_zero_norm alpha (z i j) n ha0 ha1 (hz i j),
    constant_zero_norm alpha (z j i) n ha0 ha1 (hz j i)]
  ring

end Researcher040282.EMA

-- Closed-file audit queries.
#print axioms Researcher040282.EMA.phaseInput_norm
#print axioms Researcher040282.EMA.physicalAlpha_pos
#print axioms Researcher040282.EMA.physicalAlpha_lt_one
#print axioms Researcher040282.EMA.emaStep_norm_le
#print axioms Researcher040282.EMA.emaStep_unitDisk
#print axioms Researcher040282.EMA.emaTrajectory_unitDisk
#print axioms Researcher040282.EMA.coherenceUpdate_unitDisk
#print axioms Researcher040282.EMA.reportedR_nonneg
#print axioms Researcher040282.EMA.reportedR_symmetric
#print axioms Researcher040282.EMA.reportedR_diag
#print axioms Researcher040282.EMA.reportedR_le_one
#print axioms Researcher040282.EMA.reportedR_lipschitz
#print axioms Researcher040282.EMA.ema_difference
#print axioms Researcher040282.EMA.ema_same_input_difference
#print axioms Researcher040282.EMA.trajectory_same_input_difference
#print axioms Researcher040282.EMA.trajectory_same_input_norm
#print axioms Researcher040282.EMA.constant_closed_form
#print axioms Researcher040282.EMA.constant_error_norm
#print axioms Researcher040282.EMA.constant_zero_norm
#print axioms Researcher040282.EMA.constant_converges
#print axioms Researcher040282.EMA.matrix_same_input_reported_bound
#print axioms Researcher040282.EMA.constant_zero_reported
