import AIEFGateCore.PhaseCoherence

set_option autoImplicit false
namespace AIEFGate.EmaNearUnit

open AIEFGate.PhaseCoherence

/-- If every past input has real projection at least L, zero-start EMA retains
at least (1 - alpha^N) L in that direction. -/
theorem trace_projection_bound {V : Type*} (alpha L : ℝ)
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (i j : V) (N : ℕ) (ha : 0 ≤ alpha) (ha1 : alpha ≤ 1)
    (hin : ∀ k < N, L ≤ (coherenceInput d x0 u omega tau k i j).re) :
    (1 - alpha ^ N) * L ≤
      (coherenceTrace alpha (fun _ _ => 0) d x0 u omega tau N i j).re := by
  induction N with
  | zero => simp [coherenceTrace]
  | succ N ih =>
    have hp := ih (fun k hk => hin k (by omega))
    have hq := hin N (by omega)
    have hmul := mul_le_mul_of_nonneg_left hp ha
    have hinput := mul_le_mul_of_nonneg_left hq (sub_nonneg.mpr ha1)
    simp only [coherenceTrace, coherenceStep, Complex.add_re, Complex.mul_re,
      Complex.ofReal_re, Complex.ofReal_im, zero_mul, sub_zero] 
    rw [pow_succ]
    nlinarith

/-- The result is a norm bound, not an assertion of exact unit coherence. -/
theorem trace_norm_bound {V : Type*} (alpha L : ℝ)
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (i j : V) (N : ℕ) (ha : 0 ≤ alpha) (ha1 : alpha ≤ 1)
    (hin : ∀ k < N, L ≤ (coherenceInput d x0 u omega tau k i j).re) :
    (1 - alpha ^ N) * L ≤
      ‖coherenceTrace alpha (fun _ _ => 0) d x0 u omega tau N i j‖ := by
  exact le_trans (trace_projection_bound alpha L d x0 u omega tau i j N ha ha1 hin)
    (Complex.re_le_norm _)

/-- Readable error budget: phase-projection loss δ plus startup loss α^N. -/
theorem near_unit {V : Type*} (alpha delta epsilon : ℝ)
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (i j : V) (N : ℕ) (ha : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hd : 0 ≤ delta)
    (hin : ∀ k < N, 1 - delta ≤ (coherenceInput d x0 u omega tau k i j).re)
    (budget : alpha ^ N + delta ≤ epsilon) :
    1 - epsilon ≤ ‖coherenceTrace alpha (fun _ _ => 0) d x0 u omega tau N i j‖ := by
  have hp := trace_norm_bound alpha (1 - delta) d x0 u omega tau i j N ha ha1 hin
  have hx : 0 ≤ alpha ^ N * delta := mul_nonneg (pow_nonneg ha _) hd
  nlinarith

/-- Phase spread around zero implies the projection condition for main's
actual input convention, without requiring phase-locking to be proved. -/
theorem near_unit_of_phase_spread {V : Type*} (alpha beta epsilon : ℝ)
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (i j : V) (N : ℕ) (ha : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hb : beta ≤ Real.pi)
    (hspread : ∀ k < N, |Phase.phaseTrace x0 u k i - Phase.phaseTrace x0 u (k - d) j -
      ((omega i + omega j) / 2) * tau| ≤ beta)
    (budget : alpha ^ N + (1 - Real.cos beta) ≤ epsilon) :
    1 - epsilon ≤ ‖coherenceTrace alpha (fun _ _ => 0) d x0 u omega tau N i j‖ := by
  apply near_unit alpha (1 - Real.cos beta) epsilon d x0 u omega tau i j N ha ha1
    (sub_nonneg.mpr (Real.cos_le_one beta)) _ budget
  intro k hk
  have hs := hspread k hk
  have hc := Real.cos_le_cos_of_nonneg_of_le_pi (abs_nonneg _) hb hs
  rw [Real.cos_abs] at hc
  rw [input_engine_convention, mul_comm, Complex.exp_ofReal_mul_I_re]
  linarith

#print axioms near_unit_of_phase_spread
#print axioms trace_projection_bound
#print axioms trace_norm_bound
#print axioms near_unit
end AIEFGate.EmaNearUnit
