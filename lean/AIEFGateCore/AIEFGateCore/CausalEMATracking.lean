/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.PhaseCoherence

/-!
# Causal tracking error of the coherence EMA (Arena D9)

Research candidate. The EMA error against the current input obeys `e(n+1) = α e(n) - (input(n+1) -
input(n))` (new input motion has coefficient one), so `‖e n‖ ≤ budget α ‖e 0‖ drift n` with the
delayed-increment drift. Holds for `0 ≤ α` (α = 0 and 1 allowed). Value probe and `false_*`
witnesses appended (SPEC §17).

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D9, deposit sha256 `21493f28…`; proofs and
statements unchanged from the deposit.
-/

set_option autoImplicit false
namespace AIEFGate.CausalEMATracking

open AIEFGate.PhaseCoherence

/-- A chronological error budget. The most recent variation is unscaled. -/
def budget (alpha E : ℝ) (drift : ℕ → ℝ) : ℕ → ℝ
  | 0 => E
  | n + 1 => alpha * budget alpha E drift n + drift n

/-- Main's directed EMA error relative to the input available at time n. -/
noncomputable def error {V : Type*} (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (n : ℕ) (i j : V) : ℂ :=
  coherenceTrace alpha C0 d x0 u omega tau n i j -
    coherenceInput d x0 u omega tau n i j

/-- Causal identity: new input motion has coefficient one, not 1-alpha. -/
theorem tracking_identity {V : Type*} (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (n : ℕ) (i j : V) :
    error alpha C0 d x0 u omega tau (n + 1) i j =
      (alpha : ℂ) * error alpha C0 d x0 u omega tau n i j -
        (coherenceInput d x0 u omega tau (n + 1) i j -
          coherenceInput d x0 u omega tau n i j) := by
  simp only [error, coherenceTrace, coherenceStep, Complex.ofReal_sub, Complex.ofReal_one]
  ring

/-- One-step tracking estimate, allowing alpha = 0 or alpha = 1. -/
theorem tracking_step_bound {V : Type*} (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha : 0 ≤ alpha) (n : ℕ) (i j : V) :
    ‖error alpha C0 d x0 u omega tau (n + 1) i j‖ ≤
      alpha * ‖error alpha C0 d x0 u omega tau n i j‖ +
        ‖coherenceInput d x0 u omega tau (n + 1) i j -
          coherenceInput d x0 u omega tau n i j‖ := by
  rw [tracking_identity]
  calc
    _ ≤ ‖(alpha : ℂ) * error alpha C0 d x0 u omega tau n i j‖ +
      ‖coherenceInput d x0 u omega tau (n + 1) i j -
        coherenceInput d x0 u omega tau n i j‖ := norm_sub_le _ _
    _ = _ := by rw [norm_mul, Complex.norm_of_nonneg ha]

/-- Re-derived C012 bound for main's wrapped, delayed phasor input. -/
theorem delayed_tracking_bound {V : Type*} (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha : 0 ≤ alpha) (n : ℕ) (i j : V) :
    ‖error alpha C0 d x0 u omega tau n i j‖ ≤
      budget alpha ‖error alpha C0 d x0 u omega tau 0 i j‖
        (fun k => |u k i - Phase.delayedIncrement d u k j|) n := by
  induction n with
  | zero => simp [budget]
  | succ n ih =>
    have hstep := tracking_step_bound alpha C0 d x0 u omega tau ha n i j
    have hinput := Phase.delayed_input_chord_bound d x0 u omega tau n i j
    have hscaled := mul_le_mul_of_nonneg_left ih ha
    change ‖coherenceInput d x0 u omega tau (n + 1) i j -
      coherenceInput d x0 u omega tau n i j‖ ≤ _ at hinput
    simp only [budget]
    linarith

/-- At alpha 1 the old-input EMA does not move, but tracking error can jump. -/
theorem drift_factor_one_probe :
    ‖((1 : ℂ) * 1 + ((1 - 1 : ℝ) : ℂ) * 1) - (-1 : ℂ)‖ = 2 := by
  norm_num

#print axioms tracking_identity
#print axioms tracking_step_bound
#print axioms delayed_tracking_bound
#print axioms drift_factor_one_probe

/-! ### Value probe and negations used by the mutation harness (SPEC §17) -/

/-- `budget 2 0 1` after one step is the newest drift `1` (unscaled); `budget 2 1 0` after two steps
is `2^2 = 4`. A `(1 - α)` drift factor gives `-1`, no decay gives `1`, a zero start gives `0`. -/
theorem probe_budget_values :
    budget 2 0 (fun _ => 1) 1 = 1 ∧ budget 2 1 (fun _ => 0) 2 = 4 := by
  constructor <;> norm_num [budget]

/-- The constant start `C0 = 10` is at distance at least `9` from any unit input. -/
theorem far_start {V : Type*} (alpha : ℝ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
    (omega : V → ℝ) (tau : ℝ) (i j : V) :
    9 ≤ ‖error alpha (fun _ _ => 10) d x0 u omega tau 0 i j‖ := by
  have h := norm_sub_norm_le (10 : ℂ) (coherenceInput d x0 u omega tau 0 i j)
  rw [input_norm] at h
  simp only [error, coherenceTrace]
  norm_num at h ⊢
  linarith

/-- Dropping `0 ≤ α` from `tracking_step_bound` is false (`α = -1`, `C0 = 10`, `n = 0`). -/
theorem false_step_bound_no_nonneg :
    ¬ (∀ {V : Type*} (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
      (omega : V → ℝ) (tau : ℝ) (_ha : True) (n : ℕ) (i j : V),
      ‖error alpha C0 d x0 u omega tau (n + 1) i j‖ ≤
        alpha * ‖error alpha C0 d x0 u omega tau n i j‖ +
          ‖coherenceInput d x0 u omega tau (n + 1) i j -
            coherenceInput d x0 u omega tau n i j‖) := by
  intro H
  have h := @H PUnit (-1) (fun _ _ => 10) 0 (fun _ => 0) (fun _ _ => 0) (fun _ => 0) 0 trivial 0
    PUnit.unit PUnit.unit
  have h9 := far_start (-1) 0 (fun _ => 0) (fun _ _ => 0) (fun _ => 0) 0 PUnit.unit PUnit.unit
  have hd := norm_sub_le
    (coherenceInput 0 (fun (_ : PUnit) => (0 : ℝ)) (fun _ _ => 0) (fun _ => 0) 0 1
    PUnit.unit PUnit.unit) (coherenceInput 0 (fun (_ : PUnit) => (0 : ℝ)) (fun _ _ => 0)
    (fun _ => 0) 0 0 PUnit.unit PUnit.unit)
  rw [input_norm, input_norm] at hd
  have h0 := norm_nonneg (error (-1) (fun (_ _ : PUnit) => (10 : ℂ)) 0 (fun _ => 0) (fun _ _ => 0)
    (fun _ => 0) 0 1 PUnit.unit PUnit.unit)
  linarith

/-- Dropping `0 ≤ α` from `delayed_tracking_bound` is false (`α = -1`, `C0 = 10`, `u = 0`, `n =
1`). -/
theorem false_delayed_bound_no_nonneg :
    ¬ (∀ {V : Type*} (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
      (omega : V → ℝ) (tau : ℝ) (_ha : True) (n : ℕ) (i j : V),
      ‖error alpha C0 d x0 u omega tau n i j‖ ≤
        budget alpha ‖error alpha C0 d x0 u omega tau 0 i j‖
          (fun k => |u k i - Phase.delayedIncrement d u k j|) n) := by
  intro H
  have h := @H PUnit (-1) (fun _ _ => 10) 0 (fun _ => 0) (fun _ _ => 0) (fun _ => 0) 0 trivial 1
    PUnit.unit PUnit.unit
  have h9 := far_start (-1) 0 (fun _ => 0) (fun _ _ => 0) (fun _ => 0) 0 PUnit.unit PUnit.unit
  have h0 := norm_nonneg (error (-1) (fun (_ _ : PUnit) => (10 : ℂ)) 0 (fun _ => 0) (fun _ _ => 0)
    (fun _ => 0) 0 1 PUnit.unit PUnit.unit)
  simp only [budget, Phase.delayedIncrement] at h
  norm_num at h
  linarith

#print axioms probe_budget_values
#print axioms far_start
#print axioms false_step_bound_no_nonneg
#print axioms false_delayed_bound_no_nonneg

end AIEFGate.CausalEMATracking
