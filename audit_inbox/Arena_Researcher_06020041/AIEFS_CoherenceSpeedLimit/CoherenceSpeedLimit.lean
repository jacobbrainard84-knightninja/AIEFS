import AIEFGateCore.PhaseCoherence

set_option autoImplicit false
namespace AIEFGate.CoherenceSpeedLimit

open AIEFGate.PhaseCoherence

/-- One directed EMA entry changes by at most twice its innovation weight. -/
theorem directed_motion (alpha : ℝ) (C z : ℂ) (ha : alpha ≤ 1)
    (hC : ‖C‖ ≤ 1) (hz : ‖z‖ = 1) :
    |‖(alpha : ℂ) * C + ((1 - alpha : ℝ) : ℂ) * z‖ - ‖C‖| ≤ 2 * (1 - alpha) := by
  have hcoef : 0 ≤ 1 - alpha := sub_nonneg.mpr ha
  have hsub : (alpha : ℂ) * C + ((1 - alpha : ℝ) : ℂ) * z - C =
      ((1 - alpha : ℝ) : ℂ) * (z - C) := by
    push_cast
    ring
  have hdiff : ‖z - C‖ ≤ 2 := by
    have h := norm_sub_le z C
    linarith
  have hreal : ‖((1 - alpha : ℝ) : ℂ) * (z - C)‖ ≤ 2 * (1 - alpha) := by
    rw [norm_mul, Complex.norm_of_nonneg hcoef]
    nlinarith
  calc
    _ ≤ ‖((alpha : ℂ) * C + ((1 - alpha : ℝ) : ℂ) * z) - C‖ :=
      abs_norm_sub_norm_le _ _
    _ ≤ _ := by rw [hsub]; exact hreal

/-- The bound for the actual symmetrized, zero-diagonal reported coherence. -/
theorem reported_motion {V : Type*} (alpha : ℝ) (C : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha : alpha ≤ 1) (hC : ∀ i j, ‖C i j‖ ≤ 1) (n : ℕ) (i j : V) :
    |reported (coherenceStep alpha C d x0 u omega tau n) i j - reported C i j| ≤
      2 * (1 - alpha) := by
  classical
  by_cases hij : i = j
  · subst j
    simp only [reported_diag, sub_self, abs_zero]
    linarith
  · rw [reported_offdiag _ hij, reported_offdiag _ hij]
    have a := directed_motion alpha (C i j) (coherenceInput d x0 u omega tau n i j)
      ha (hC i j) (input_norm d x0 u omega tau n i j)
    have b := directed_motion alpha (C j i) (coherenceInput d x0 u omega tau n j i)
      ha (hC j i) (input_norm d x0 u omega tau n j i)
    change |‖coherenceStep alpha C d x0 u omega tau n i j‖ - ‖C i j‖| ≤ _ at a
    change |‖coherenceStep alpha C d x0 u omega tau n j i‖ - ‖C j i‖| ≤ _ at b
    have a' := abs_le.mp a
    have b' := abs_le.mp b
    apply abs_le.mpr
    constructor <;> linarith

/-- From a unit-disk start, combine the step bound with R in [0,1]. -/
theorem trace_motion_min {V : Type*} (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1)
    (n : ℕ) (i j : V) :
    |reported (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j -
      reported (coherenceTrace alpha C0 d x0 u omega tau n) i j| ≤
        min 1 (2 * (1 - alpha)) := by
  have hn := coherenceTrace_unitDisk alpha C0 d x0 u omega tau ha0 ha1 hC n
  have hn1 := coherenceTrace_unitDisk alpha C0 d x0 u omega tau ha0 ha1 hC (n + 1)
  have hnR := reported_bounds (coherenceTrace alpha C0 d x0 u omega tau n) hn i j
  have hn1R := reported_bounds (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) hn1 i j
  apply le_min
  · apply abs_le.mpr
    constructor <;> linarith [hnR.1, hnR.2, hn1R.1, hn1R.2]
  · exact reported_motion alpha _ d x0 u omega tau ha1 hn n i j

/-- The coefficient 2 is necessary: alpha=1/2, old value -1, input +1. -/
theorem sharp_direct_probe :
    |‖((1 / 2 : ℝ) : ℂ) * (-1) + ((1 - 1 / 2 : ℝ) : ℂ) * 1‖ -
      ‖(-1 : ℂ)‖| = 1 := by
  norm_num

/-- Two directed entries differ, so a one-sided magnitude is not the report. -/
def asymmetricC (i j : Fin 2) : ℂ := if i = 0 ∧ j = 1 then 1 else 0

/-- Direct values from the model definitions, not from the speed theorem. -/
theorem asymmetric_report_probe :
    reported asymmetricC 0 1 = 1 / 2 ∧
    reported (coherenceStep (1 / 2) asymmetricC 0 (fun _ => 0) (fun _ _ => 0)
      (fun _ => 0) 0 0) 0 1 = 3 / 4 := by
  norm_num [reported, asymmetricC, coherenceStep, coherenceInput, Phase.inputPhasor,
    Phase.phasor, Phase.phaseTrace, History.historyTrace]

#print axioms asymmetric_report_probe
#print axioms directed_motion
#print axioms reported_motion
#print axioms trace_motion_min
#print axioms sharp_direct_probe
end AIEFGate.CoherenceSpeedLimit
