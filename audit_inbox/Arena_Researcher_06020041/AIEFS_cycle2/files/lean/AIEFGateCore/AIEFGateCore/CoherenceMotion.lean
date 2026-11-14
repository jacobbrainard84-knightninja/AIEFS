/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0


import AIEFGateCore.PhaseCoherence

/-!
# (c016) One-step coherence / reported-R movement bounds

Port of Researcher 040282 cycle 016 `CoherenceMotion.lean`
(deposit on `audit-inbox`, commit `0f189d0`, md5 `079a72f3...`),
reviewed by Auditor Seat 002 as **ADOPT WITH NOTES** in
`audit_inbox/2026-11-11_auditor-seat-002_lean-candidate-reviews/`
`2026-11-11_audit_040282_c012_c016.md`.
Statements and proofs are unchanged. Differences from the deposit:
standard header, this docstring, removal of the trailing
`#print axioms` lines (step 7 of `check_lean_gate.sh` prints them),
and one added negative control `false_trace_step_abs_le_half` for M59.

Engine meaning: `alpha = exp(-0.01/17.5029...) = 0.99942883...`, so `2*(1-alpha) = 0.00114...`.
In exact reals, `R` can move by at most `0.00114` per step, so 0 -> 1 needs at least ~875 steps
(~8.75 time units). This is the first quantitative statement about `R` along the real step.

**Scope — a speed limit, not dynamics.** The proof is the triangle inequality on an EMA with
unit-norm inputs. It never uses the phases, the delay, `omega` or `B`: it holds for ANY unit-norm
input sequence. It is not a result about phase locking, the delay queue, float64 rounding or the
closed-loop system. It depends on P5 `PhaseCoherence` (hand-checked against the Python convention,
not proved). `AUD-RATELAW stays UNEXPLAINED`. The next genuinely new theorem should use the phases
or the delay, e.g. a condition under which `R` can only increase.
-/

set_option autoImplicit false

namespace AIEFGate.CoherenceMotion

open scoped BigOperators

variable {V : Type*}

noncomputable section

/-- Pure norm inequality, not a replacement coherence/model definition. -/
theorem complex_step_bounds (alpha : ℝ) (C z : ℂ) (ha0 : 0 ≤ alpha)
    (ha1 : alpha ≤ 1) (hz : ‖z‖ = 1) :
    alpha * ‖C‖ - (1-alpha) ≤ ‖(alpha : ℂ)*C + ((1-alpha : ℝ) : ℂ)*z‖ ∧
      ‖(alpha : ℂ)*C + ((1-alpha : ℝ) : ℂ)*z‖ ≤ alpha * ‖C‖ + (1-alpha) := by
  have halpha : ‖(alpha : ℂ)‖ = alpha := Complex.norm_of_nonneg ha0
  have hbeta : ‖((1-alpha : ℝ) : ℂ)*z‖ = 1-alpha := by
    rw [norm_mul,Complex.norm_of_nonneg (sub_nonneg.mpr ha1),hz,mul_one]
  constructor
  · have h := norm_sub_le ((alpha : ℂ)*C + ((1-alpha : ℝ) : ℂ)*z)
        (((1-alpha : ℝ) : ℂ)*z)
    rw [add_sub_cancel_right,norm_mul,halpha,hbeta] at h
    linarith
  · calc
      _ ≤ ‖(alpha : ℂ)*C‖ + ‖((1-alpha : ℝ) : ℂ)*z‖ := norm_add_le _ _
      _ = _ := by rw [norm_mul,halpha,hbeta]

theorem reported_nonneg (C : V → V → ℂ) (i j : V) :
    0 ≤ PhaseCoherence.reported C i j := by
  classical
  unfold PhaseCoherence.reported
  split_ifs <;> positivity

/-- Derived one-step envelope for the actual P5coherenceStep, not an assumed Rband.
No initial-unit-disk premise is needed for this state-dependent statement. -/
theorem reported_step_bounds (alpha : ℝ) (C : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (n : ℕ) (i j : V) :
    alpha * PhaseCoherence.reported C i j - (1-alpha) ≤
      PhaseCoherence.reported (PhaseCoherence.coherenceStep alpha C d x0 u omega tau n) i j ∧
    PhaseCoherence.reported (PhaseCoherence.coherenceStep alpha C d x0 u omega tau n) i j ≤
      alpha * PhaseCoherence.reported C i j + (1-alpha) := by
  classical
  by_cases h : i = j
  · subst j
    rw [PhaseCoherence.reported_diag,PhaseCoherence.reported_diag]
    constructor <;> nlinarith
  · rw [PhaseCoherence.reported_offdiag _ h,PhaseCoherence.reported_offdiag _ h]
    have hij := complex_step_bounds alpha (C i j)
      (PhaseCoherence.coherenceInput d x0 u omega tau n i j) ha0 ha1
      (PhaseCoherence.input_norm d x0 u omega tau n i j)
    have hji := complex_step_bounds alpha (C j i)
      (PhaseCoherence.coherenceInput d x0 u omega tau n j i) ha0 ha1
      (PhaseCoherence.input_norm d x0 u omega tau n j i)
    change alpha * ‖C i j‖ - (1-alpha) ≤
        ‖PhaseCoherence.coherenceStep alpha C d x0 u omega tau n i j‖ ∧
      ‖PhaseCoherence.coherenceStep alpha C d x0 u omega tau n i j‖ ≤
        alpha * ‖C i j‖ + (1-alpha) at hij
    change alpha * ‖C j i‖ - (1-alpha) ≤
        ‖PhaseCoherence.coherenceStep alpha C d x0 u omega tau n j i‖ ∧
      ‖PhaseCoherence.coherenceStep alpha C d x0 u omega tau n j i‖ ≤
        alpha * ‖C j i‖ + (1-alpha) at hji
    constructor <;> nlinarith [hij.1,hij.2,hji.1,hji.2]

/-- Increase and decrease are not governed by the same smaller coefficient. -/
theorem reported_step_signed (alpha : ℝ) (C : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (n : ℕ) (i j : V) :
    -(1-alpha)*(1 + PhaseCoherence.reported C i j) ≤
      PhaseCoherence.reported (PhaseCoherence.coherenceStep alpha C d x0 u omega tau n) i j -
        PhaseCoherence.reported C i j ∧
    PhaseCoherence.reported (PhaseCoherence.coherenceStep alpha C d x0 u omega tau n) i j -
        PhaseCoherence.reported C i j ≤ (1-alpha)*(1 - PhaseCoherence.reported C i j) := by
  have h := reported_step_bounds alpha C d x0 u omega tau ha0 ha1 n i j
  constructor <;> nlinarith [h.1,h.2]

theorem reported_step_abs_state_bound (alpha : ℝ) (C : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (n : ℕ) (i j : V) :
    |PhaseCoherence.reported (PhaseCoherence.coherenceStep alpha C d x0 u omega tau n) i j -
        PhaseCoherence.reported C i j| ≤ (1-alpha)*(1 + PhaseCoherence.reported C i j) := by
  have h := reported_step_signed alpha C d x0 u omega tau ha0 ha1 n i j
  apply abs_le.mpr
  constructor
  · simpa only [neg_mul] using h.1
  · nlinarith [h.2,mul_nonneg (sub_nonneg.mpr ha1) (reported_nonneg C i j)]

/-- Observable wrapper only; no new state or new coherence recurrence. -/
def rTrace (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ)
    (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) : ℝ :=
  PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n) i j

theorem trace_step_bounds (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (n : ℕ) (i j : V) :
    alpha * rTrace alpha C0 d x0 u omega tau n i j - (1-alpha) ≤
      rTrace alpha C0 d x0 u omega tau (n+1) i j ∧
    rTrace alpha C0 d x0 u omega tau (n+1) i j ≤
      alpha * rTrace alpha C0 d x0 u omega tau n i j + (1-alpha) := by
  exact reported_step_bounds alpha (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n)
    d x0 u omega tau ha0 ha1 n i j

theorem trace_step_abs_state_bound (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (n : ℕ) (i j : V) :
    |rTrace alpha C0 d x0 u omega tau (n+1) i j - rTrace alpha C0 d x0 u omega tau n i j| ≤
      (1-alpha)*(1 + rTrace alpha C0 d x0 u omega tau n i j) := by
  exact reported_step_abs_state_bound alpha
    (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n)
    d x0 u omega tau ha0 ha1 n i j

/-- Current unit-disk range is inherited from C0, not postulated as a future band. -/
theorem trace_step_abs_le (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC0 : ∀ i j, ‖C0 i j‖ ≤ 1)
    (n : ℕ) (i j : V) :
    |rTrace alpha C0 d x0 u omega tau (n + 1) i j -
      rTrace alpha C0 d x0 u omega tau n i j| ≤ 2*(1-alpha) := by
  have hr := PhaseCoherence.reported_bounds _
    (PhaseCoherence.coherenceTrace_unitDisk alpha C0 d x0 u omega tau ha0 ha1 hC0 n) i j
  have h := trace_step_abs_state_bound alpha C0 d x0 u omega tau ha0 ha1 n i j
  change 0 ≤ rTrace alpha C0 d x0 u omega tau n i j ∧
    rTrace alpha C0 d x0 u omega tau n i j ≤ 1 at hr
  nlinarith [mul_le_mul_of_nonneg_left hr.2 (sub_nonneg.mpr ha1)]

theorem trace_step_abs_le_min (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC0 : ∀ i j, ‖C0 i j‖ ≤ 1)
    (n : ℕ) (i j : V) :
    |rTrace alpha C0 d x0 u omega tau (n+1) i j - rTrace alpha C0 d x0 u omega tau n i j| ≤
      min 1 (2*(1-alpha)) := by
  have h0 := PhaseCoherence.reported_bounds _
    (PhaseCoherence.coherenceTrace_unitDisk alpha C0 d x0 u omega tau ha0 ha1 hC0 n) i j
  have h1 := PhaseCoherence.reported_bounds _
    (PhaseCoherence.coherenceTrace_unitDisk alpha C0 d x0 u omega tau ha0 ha1 hC0 (n+1)) i j
  change 0 ≤ rTrace alpha C0 d x0 u omega tau n i j ∧
    rTrace alpha C0 d x0 u omega tau n i j ≤ 1 at h0
  change 0 ≤ rTrace alpha C0 d x0 u omega tau (n+1) i j ∧
    rTrace alpha C0 d x0 u omega tau (n+1) i j ≤ 1 at h1
  apply le_min _ (trace_step_abs_le alpha C0 d x0 u omega tau ha0 ha1 hC0 n i j)
  apply abs_le.mpr
  constructor <;> nlinarith [h0.1,h0.2,h1.1,h1.2]

theorem trace_diagonal (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i : V) :
    rTrace alpha C0 d x0 u omega tau n i i = 0 := PhaseCoherence.reported_diag _ i

section ValueProbes

def valueX (_ : Fin 2) : ℝ := 0
def valueU (_ : ℕ) (_ : Fin 2) : ℝ := 0
def valueOmega (_ : Fin 2) : ℝ := 1
def valueC (c : ℂ) (_ _ : Fin 2) : ℂ := c

private theorem value_phase_zero (n : ℕ) (i : Fin 2) :
    Phase.phaseTrace valueX valueU n i = 0 := by
  induction n with
  | zero => rfl
  | succ n ih =>
      change Phase.wrapPhase (Phase.phaseTrace valueX valueU n i + 0) = 0
      rw [ih]
      simp [Phase.wrapPhase]

private theorem value_input (n : ℕ) (i j : Fin 2) :
    PhaseCoherence.coherenceInput 1 valueX valueU valueOmega Real.pi n i j = -1 := by
  have he : Complex.exp (Complex.I * ((-Real.pi : ℝ) : ℂ)) = -1 := by
    have hh : Complex.I * ((-Real.pi : ℝ) : ℂ) = -((Real.pi : ℂ)*Complex.I) := by
      push_cast
      ring
    rw [hh]
    exact Complex.exp_neg_pi_mul_I
  rw [PhaseCoherence.input_engine_convention]
  simpa [value_phase_zero,valueOmega] using he

private theorem value_first (alpha : ℝ) (c : ℂ) (i j : Fin 2) :
    PhaseCoherence.coherenceTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi 1 i j =
      (alpha : ℂ)*c - ((1-alpha : ℝ) : ℂ) := by
  change (alpha : ℂ)*valueC c i j + ((1-alpha : ℝ) : ℂ)*
    PhaseCoherence.coherenceInput 1 valueX valueU valueOmega Real.pi 0 i j = _
  rw [value_input]
  unfold valueC
  ring

private theorem value_r0 (alpha : ℝ) (c : ℂ) :
    rTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi 0 0 1 = ‖c‖ := by
  change PhaseCoherence.reported (valueC c) (0 : Fin 2) 1 = _
  rw [PhaseCoherence.reported_offdiag _ (by decide)]
  unfold valueC
  ring

private theorem value_r1 (alpha : ℝ) (c : ℂ) :
    rTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi 1 0 1 =
      ‖(alpha : ℂ)*c - ((1-alpha : ℝ) : ℂ)‖ := by
  unfold rTrace
  rw [PhaseCoherence.reported_offdiag _ (by decide),value_first,value_first]
  ring

/-- Probe shorthand only, not a new coherence/state model. -/
def Rval (alpha : ℝ) (c : ℂ) (n : ℕ) : ℝ :=
  rTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi n 0 1

theorem probe_half_drop : Rval (1/2) 1 0 = 1 ∧ Rval (1/2) 1 1 = 0 := by
  unfold Rval
  rw [value_r0,value_r1]
  norm_num

theorem probe_half_increase : Rval (1/2) 0 0 = 0 ∧ Rval (1/2) 0 1 = 1/2 := by
  unfold Rval
  rw [value_r0,value_r1]
  norm_num [Complex.norm_def,Complex.normSq]

/-- The factor2 is attained for alpha>=1/2; not a claim of global optimality for
all alpha or production zero-initialised trajectories. -/
theorem factor_two_attained (alpha : ℝ) (hh : 1 / 2 ≤ alpha) (ha1 : alpha ≤ 1) :
    |Rval alpha 1 1 - Rval alpha 1 0| = 2*(1-alpha) := by
  unfold Rval
  rw [value_r0,value_r1]
  have he : (alpha : ℂ)*1 - ((1-alpha : ℝ) : ℂ) = ((2*alpha-1 : ℝ) : ℂ) := by
    push_cast
    ring
  rw [he,Complex.norm_of_nonneg (by linarith : 0 ≤ 2*alpha-1),norm_one]
  rw [abs_of_nonpos (by linarith : 2*alpha-1-1 ≤ 0)]
  ring

theorem increase_factor_attained (alpha : ℝ) (ha1 : alpha ≤ 1) :
    Rval alpha 0 1 - Rval alpha 0 0 = 1-alpha := by
  unfold Rval
  rw [value_r0,value_r1]
  simp only [mul_zero,zero_sub,norm_neg,norm_zero,sub_zero]
  exact Complex.norm_of_nonneg (sub_nonneg.mpr ha1)

private theorem value_second (i j : Fin 2) :
    PhaseCoherence.coherenceTrace (3/4) (valueC 1) 1 valueX valueU valueOmega Real.pi 2 i j
      = 1/8 := by
  change ((3/4 : ℝ) : ℂ) *
      PhaseCoherence.coherenceTrace (3/4) (valueC 1) 1 valueX valueU valueOmega Real.pi 1 i j +
    ((1-3/4 : ℝ) : ℂ)*PhaseCoherence.coherenceInput 1 valueX valueU valueOmega Real.pi 1 i j = _
  rw [value_first,value_input]
  norm_num

theorem probe_two_step : Rval (3/4) 1 0 = 1 ∧ Rval (3/4) 1 2 = 1/8 := by
  unfold Rval
  rw [value_r0]
  constructor
  · norm_num
  · unfold rTrace
    rw [PhaseCoherence.reported_offdiag _ (by decide),value_second,value_second]
    norm_num [Complex.norm_def,Complex.normSq]

theorem factor_one_refuted : ¬ |Rval (1/2) 1 1 - Rval (1/2) 1 0| ≤ 1-(1/2 : ℝ) := by
  rw [probe_half_drop.1,probe_half_drop.2]
  norm_num

theorem increase_only_abs_refuted :
    ¬ |Rval (1/2) 1 1 - Rval (1/2) 1 0| ≤ (1-(1/2 : ℝ))*(1-Rval (1/2) 1 0) := by
  rw [probe_half_drop.1,probe_half_drop.2]
  norm_num

theorem negative_alpha_upper_refuted :
    ¬ Rval (-1) 1 1 ≤ (-1 : ℝ)*Rval (-1) 1 0 + (1-(-1 : ℝ)) := by
  unfold Rval
  rw [value_r0,value_r1]
  norm_num [Complex.norm_def,Complex.normSq]

theorem alpha_gt_one_upper_refuted :
    ¬ Rval 2 0 1 ≤ (2 : ℝ)*Rval 2 0 0 + (1-(2 : ℝ)) := by
  unfold Rval
  rw [value_r0,value_r1]
  norm_num [Complex.norm_def,Complex.normSq]

theorem nonunit_initial_refuted :
    ¬ |Rval (1/2) 3 1 - Rval (1/2) 3 0| ≤ 2*(1-(1/2 : ℝ)) := by
  unfold Rval
  rw [value_r0,value_r1]
  norm_num [Complex.norm_def,Complex.normSq]

theorem two_step_one_allowance_refuted :
    ¬ |Rval (3/4) 1 2 - Rval (3/4) 1 0| ≤ 2*(1-(3/4 : ℝ)) := by
  rw [probe_two_step.1,probe_two_step.2]
  norm_num


/-- Negative control for mutation M59: the one-step bound cannot be halved. -/
theorem false_trace_step_abs_le_half
    (H : ∀ {V : Type} (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
       (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
       (_ha0 : 0 ≤ alpha) (_ha1 : alpha ≤ 1)
       (_hC0 : ∀ i j, ‖C0 i j‖ ≤ 1) (n : ℕ) (i j : V),
       |rTrace alpha C0 d x0 u omega tau (n + 1) i j -
         rTrace alpha C0 d x0 u omega tau n i j| ≤ (1 - alpha) / 2) : False := by
  have h := @H (Fin 2) (1/2 : ℝ) (valueC 1) 1 valueX valueU valueOmega Real.pi
      (by norm_num) (by norm_num) (by intro i j; simp [valueC]) 0 0 1
  have h' : |Rval (1/2) 1 1 - Rval (1/2) 1 0| ≤ (1 - (1/2 : ℝ)) / 2 := by
    simpa [Rval] using h
  rw [probe_half_drop.1, probe_half_drop.2] at h'
  norm_num at h'

end ValueProbes

end
end AIEFGate.CoherenceMotion
