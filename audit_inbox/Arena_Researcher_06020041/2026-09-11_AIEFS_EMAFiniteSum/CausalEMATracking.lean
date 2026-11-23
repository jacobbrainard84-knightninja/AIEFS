import AIEFGateCore.PhaseCoherence

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
end AIEFGate.CausalEMATracking
