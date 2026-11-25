/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.PhaseCoherence

/-!
# Near-unit bound for the zero-start coherence EMA (Arena D7)

Research candidate. If every past input has real projection at least `L`, the zero-start coherence
trace keeps `(1 - α^N) L` in that direction, so a phase-spread hypothesis gives `1 - ε ≤ ‖trace‖`
with budget `α^N + δ ≤ ε`. The phase spread is ASSUMED; locking is not proved. `false_*` witnesses
for the mutation harness are appended (SPEC §17).

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D7, deposit sha256 `292d1e7a…`; proofs and
statements unchanged from the deposit.
-/

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

/-! ### Negations used by the mutation harness (SPEC §17)

At `N = 0` the zero-start trace is `0`, so the claim `1 - ε ≤ ‖trace‖` needs `ε ≥ 1`. -/

/-- Dropping the startup loss `α^N` from the budget of `near_unit` is false (`N = 0`, `ε = 0`). -/
theorem false_near_unit_no_startup :
    ¬ (∀ {V : Type*} (alpha delta epsilon : ℝ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
      (omega : V → ℝ) (tau : ℝ) (i j : V) (N : ℕ) (_ha : 0 ≤ alpha) (_ha1 : alpha ≤ 1)
      (_hd : 0 ≤ delta) (_hin : ∀ k < N, 1 - delta ≤ (coherenceInput d x0 u omega tau k i j).re)
      (_budget : delta ≤ epsilon),
      1 - epsilon ≤ ‖coherenceTrace alpha (fun _ _ => 0) d x0 u omega tau N i j‖) := by
  intro H
  have h := @H PUnit 0 0 0 0 (fun _ => 0) (fun _ _ => 0) (fun _ => 0) 0 PUnit.unit PUnit.unit 0
    le_rfl zero_le_one le_rfl (fun k hk => absurd hk (Nat.not_lt_zero k)) le_rfl
  norm_num [coherenceTrace] at h

/-- Dropping `0 ≤ δ` from `near_unit` is false (`N = 0`, `δ = -1`, `ε = 0`: budget `1 - 1 ≤ 0`). -/
theorem false_near_unit_no_delta_nonneg :
    ¬ (∀ {V : Type*} (alpha delta epsilon : ℝ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
      (omega : V → ℝ) (tau : ℝ) (i j : V) (N : ℕ) (_ha : 0 ≤ alpha) (_ha1 : alpha ≤ 1)
      (_hd : True) (_hin : ∀ k < N, 1 - delta ≤ (coherenceInput d x0 u omega tau k i j).re)
      (_budget : alpha ^ N + delta ≤ epsilon),
      1 - epsilon ≤ ‖coherenceTrace alpha (fun _ _ => 0) d x0 u omega tau N i j‖) := by
  intro H
  have h := @H PUnit 0 (-1) 0 0 (fun _ => 0) (fun _ _ => 0) (fun _ => 0) 0 PUnit.unit PUnit.unit 0
    le_rfl zero_le_one trivial (fun k hk => absurd hk (Nat.not_lt_zero k)) (by norm_num)
  norm_num [coherenceTrace] at h

#print axioms false_near_unit_no_startup
#print axioms false_near_unit_no_delta_nonneg

end AIEFGate.EmaNearUnit
