/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.PhaseCoherence

/-!
# (P6) A per-step speed limit on the reported coherence `R`: `|ΔR| ≤ min 1 (2 (1 - α))`

Port of `CoherenceMotion.lean` of cycle 016 of Researcher 040282 (handle only; the deposit is on
branch `audit-inbox` at
`audit_inbox/2026-11-08_researcher-040282/researcher_040282/cycle_016/CoherenceMotion.lean`, md5
`079a72f37e16e2187a913b96e28ab605`; it was supplied by the owner). The deposit imported the
unmerged P5 branch at `54037ea`; this port imports the merged `AIEFGateCore.PhaseCoherence`
(namespace `AIEFGate.PhaseCoherence`, `AIEFGate.Phase`), whose names are the ones the deposit
used. Statements and proofs of the ten theorems and of the eleven value-probe statements are
as deposited. Audited by Auditor Seat 002 (ADOPT WITH NOTES); the notes N1-N4 are applied here.

**What this file says.** For the coherence EMA `C_{n+1} = α C_n + (1 - α) z_{n+1}` with unit-modulus
input `z` and `0 ≤ α ≤ 1`, the reported coherence `R` (the symmetrised modulus,
`PhaseCoherence.reported`) satisfies `α R - (1 - α) ≤ R' ≤ α R + (1 - α)` and
`|R' - R| ≤ (1 - α) (1 + R)`. If every entry of the initial `C0` is in the unit disk this gives
`|R_{n+1} - R_n| ≤ min 1 (2 (1 - α))` (`trace_step_abs_le_min`), and the diagonal is `0`. At the
engine `α = exp (-dt / T_window) = 0.99942883…` (`dt = 1/100`, `T_window = 25 / mean ω`,
`mean ω = 857/600`, `aief_experiment_engine_v1.py` `FROZEN_ALPHA`) that is `2 (1 - α) ≈ 0.00114`
per step (`engine_step_value`), so in exact arithmetic `R` needs at least about 875 steps to go
from `0` to `1`.

**What this file does NOT say (auditor note N1).** It is a *speed limit*, not dynamics. The proof
is the triangle inequality on an exponential moving average with unit-norm inputs. It uses **no
phase structure, no delay, no `ω`, no `B`**: the same bound holds for ANY unit input sequence, so
it says nothing about what `R` does, only how fast it can move. It does not say `R` converges,
locks, or stays near any value; it does not involve `B`, the clip/projection, or the gate.

**Other limits.** (N2) The deposited probes are node-uniform (constant `C`, zero phases, input
`-1` everywhere) and so do not exercise the `|C i j|` vs `|C j i|` symmetrisation of `reported`;
`probe_asym_state` (new here) does. For `α < 1/2` the `min` is just `1`, which is trivial
because `R ∈ [0, 1]`. (N4) `α` is an exact real; the engine's float64 `α` is not exactly that
real (the bound is about exact reals, as the author states). Exact reals only, not float64.
The deposit's coupled non-reset/history probe stays deferred.

**Changes against the deposit** (statements unchanged):
* the import line and namespaces are as deposited (`import AIEFGateCore.PhaseCoherence`; the
  merged P5 module has the names the deposit used); the deposit's header comment ("UNMERGED team
  P5 branch 54037ea") is replaced by the project header and this docstring;
* `1/2 ≤ alpha` is written `1 / 2 ≤ alpha` in `factor_two_attained` and a few long lines are
  re-wrapped, for the Mathlib linters (warnings fail the gate);
* the trailing `#print axioms` lines are removed (`check_lean_gate.sh` step 7 audits every
  declaration);
* the probe proofs were rewritten so that each *proves its value from the definitions* (through
  `reported`, `coherenceTrace` and `rTrace` unfolded in the probe itself). The deposit's probes
  rewrote with private helper lemmas stated about `rTrace`; with `rTrace` mutated to read
  trace `n + 1`, only those helpers (and the rewrite lemmas) failed and `probe_half_drop` and
  `probe_half_increase` still built, so the mutation check could not credit them;
* new: `probe_diagonal_zero`; `probe_asym_state` (N2, asymmetric state `C0 0 1 = 1`, other
  entries `0`: `R = 1/2` then `1/4`, one-sided `R` would read `1` then `0`); the engine-`α` probes
  `alphaE`, `engine_speed_limit_value` (`0.00114 < 2 (1 - α) < 0.00115`),
  `engine_factor_two_attained`, `engine_step_value`, `engine_factor_one_refuted`; and the
  negations `diagonal_one_refuted` and `half_increase_upper_refuted` that the mutation check
  (`lean_mutation_check.py`, M59 ff.) uses to refute weakened versions of the statements above.
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
    |rTrace alpha C0 d x0 u omega tau (n+1) i j - rTrace alpha C0 d x0 u omega tau n i j| ≤
      2*(1-alpha) := by
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

/-- One EMA step from any state `C` with the probe input `-1`: `C₁ = α C - (1 - α)`. -/
private theorem value_first_gen (alpha : ℝ) (C : Fin 2 → Fin 2 → ℂ) (i j : Fin 2) :
    PhaseCoherence.coherenceTrace alpha C 1 valueX valueU valueOmega Real.pi 1 i j =
      (alpha : ℂ)*C i j - ((1-alpha : ℝ) : ℂ) := by
  change (alpha : ℂ)*C i j + ((1-alpha : ℝ) : ℂ)*
    PhaseCoherence.coherenceInput 1 valueX valueU valueOmega Real.pi 0 i j = _
  rw [value_input]
  ring

private theorem value_first (alpha : ℝ) (c : ℂ) (i j : Fin 2) :
    PhaseCoherence.coherenceTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi 1 i j =
      (alpha : ℂ)*c - ((1-alpha : ℝ) : ℂ) :=
  value_first_gen alpha (valueC c) i j

private theorem value_zero (alpha : ℝ) (C : Fin 2 → Fin 2 → ℂ) :
    PhaseCoherence.coherenceTrace alpha C 1 valueX valueU valueOmega Real.pi 0 = C := rfl

/-- Probe shorthand only, not a new coherence/state model. -/
def Rval (alpha : ℝ) (c : ℂ) (n : ℕ) : ℝ :=
  rTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi n 0 1

theorem probe_half_drop : Rval (1/2) 1 0 = 1 ∧ Rval (1/2) 1 1 = 0 := by
  unfold Rval rTrace
  norm_num [PhaseCoherence.reported, value_first, value_zero, valueC]

theorem probe_half_increase : Rval (1/2) 0 0 = 0 ∧ Rval (1/2) 0 1 = 1/2 := by
  unfold Rval rTrace
  norm_num [PhaseCoherence.reported, value_first, value_zero, valueC]

/-- The factor2 is attained for alpha>=1/2; not a claim of global optimality for
all alpha or production zero-initialised trajectories. -/
theorem factor_two_attained (alpha : ℝ) (hh : 1 / 2 ≤ alpha) (ha1 : alpha ≤ 1) :
    |Rval alpha 1 1 - Rval alpha 1 0| = 2*(1-alpha) := by
  unfold Rval rTrace
  norm_num [PhaseCoherence.reported, value_first, value_zero, valueC]
  have he : (alpha : ℂ) - (1 - (alpha : ℂ)) = ((2*alpha-1 : ℝ) : ℂ) := by
    push_cast
    ring
  rw [he,Complex.norm_of_nonneg (by linarith : 0 ≤ 2*alpha-1)]
  rw [abs_of_nonpos (by linarith : 2*alpha-1-1 ≤ 0)]
  ring

theorem increase_factor_attained (alpha : ℝ) (ha1 : alpha ≤ 1) :
    Rval alpha 0 1 - Rval alpha 0 0 = 1-alpha := by
  unfold Rval rTrace
  norm_num [PhaseCoherence.reported, value_first, value_zero, valueC]
  have he : (alpha : ℂ) - 1 = ((alpha - 1 : ℝ) : ℂ) := by
    push_cast
    ring
  rw [he,Complex.norm_real,Real.norm_eq_abs,abs_of_nonpos (by linarith : alpha - 1 ≤ 0)]
  ring

private theorem value_second (i j : Fin 2) :
    PhaseCoherence.coherenceTrace (3/4) (valueC 1) 1 valueX valueU valueOmega Real.pi 2 i j =
      1/8 := by
  change ((3/4 : ℝ) : ℂ)*PhaseCoherence.coherenceTrace (3/4) (valueC 1) 1 valueX valueU
    valueOmega Real.pi 1 i j +
    ((1-3/4 : ℝ) : ℂ)*PhaseCoherence.coherenceInput 1 valueX valueU valueOmega Real.pi 1 i j = _
  rw [value_first,value_input]
  norm_num

theorem probe_two_step : Rval (3/4) 1 0 = 1 ∧ Rval (3/4) 1 2 = 1/8 := by
  unfold Rval rTrace
  norm_num [PhaseCoherence.reported, value_second, value_zero, valueC]

theorem factor_one_refuted : ¬ |Rval (1/2) 1 1 - Rval (1/2) 1 0| ≤ 1-(1/2 : ℝ) := by
  rw [probe_half_drop.1,probe_half_drop.2]
  norm_num

theorem increase_only_abs_refuted :
    ¬ |Rval (1/2) 1 1 - Rval (1/2) 1 0| ≤ (1-(1/2 : ℝ))*(1-Rval (1/2) 1 0) := by
  rw [probe_half_drop.1,probe_half_drop.2]
  norm_num

theorem negative_alpha_upper_refuted :
    ¬ Rval (-1) 1 1 ≤ (-1 : ℝ)*Rval (-1) 1 0 + (1-(-1 : ℝ)) := by
  unfold Rval rTrace
  norm_num [PhaseCoherence.reported, value_first, value_zero, valueC,
    Complex.norm_def,Complex.normSq]

theorem alpha_gt_one_upper_refuted :
    ¬ Rval 2 0 1 ≤ (2 : ℝ)*Rval 2 0 0 + (1-(2 : ℝ)) := by
  unfold Rval rTrace
  norm_num [PhaseCoherence.reported, value_first, value_zero, valueC,
    Complex.norm_def,Complex.normSq]

theorem nonunit_initial_refuted :
    ¬ |Rval (1/2) 3 1 - Rval (1/2) 3 0| ≤ 2*(1-(1/2 : ℝ)) := by
  unfold Rval rTrace
  norm_num [PhaseCoherence.reported, value_first, value_zero, valueC,
    Complex.norm_def,Complex.normSq]

theorem two_step_one_allowance_refuted :
    ¬ |Rval (3/4) 1 2 - Rval (3/4) 1 0| ≤ 2*(1-(3/4 : ℝ)) := by
  rw [probe_two_step.1,probe_two_step.2]
  norm_num

/-- Diagonal probe: the diagonal of `R` is `0` at every read, also when `C0` has diagonal `1`. -/
theorem probe_diagonal_zero :
    rTrace (1/2) (valueC 1) 1 valueX valueU valueOmega Real.pi 0 0 0 = 0 ∧
    rTrace (1/2) (valueC 1) 1 valueX valueU valueOmega Real.pi 1 1 1 = 0 := by
  unfold rTrace
  norm_num [PhaseCoherence.reported]

theorem diagonal_one_refuted :
    ¬ rTrace (1/2) (valueC 1) 1 valueX valueU valueOmega Real.pi 1 1 1 = 1 := by
  rw [trace_diagonal]
  norm_num

theorem half_increase_upper_refuted :
    ¬ Rval (1/2) 0 1 ≤ (1/2 : ℝ)*Rval (1/2) 0 0 + (1-(1/2 : ℝ))/2 := by
  rw [probe_half_increase.1,probe_half_increase.2]
  norm_num

/-! (N2) Asymmetric-state probe. `C0 0 1 = 1` and every other entry `0`, so `‖C0 0 1‖ = 1` and
`‖C0 1 0‖ = 0`. With `α = 1/2` and input `-1`: `R_0 = (1 + 0)/2 = 1/2`, and
`C_1 0 1 = 1/2 - 1/2 = 0`, `C_1 1 0 = -1/2`, so `R_1 = (0 + 1/2)/2 = 1/4`. A one-sided `R`
(`‖C 0 1‖` only) would read `1` and `0`. -/

def valueCA (i j : Fin 2) : ℂ := if i = 0 ∧ j = 1 then 1 else 0

/-- Probe shorthand only, not a new coherence/state model. -/
def RvalA (alpha : ℝ) (n : ℕ) : ℝ :=
  rTrace alpha valueCA 1 valueX valueU valueOmega Real.pi n 0 1

theorem probe_asym_state : RvalA (1/2) 0 = 1/2 ∧ RvalA (1/2) 1 = 1/4 := by
  unfold RvalA rTrace
  norm_num [PhaseCoherence.reported, value_first_gen, value_zero, valueCA]

/-! The engine `α` as an exact real: `α = exp (-dt / T_window)` with `dt = 1/100`,
`T_window = 25 / mean ω` and `mean ω = 857/600` (`FROZEN_DT`, `FROZEN_T_WINDOW`,
`FROZEN_MEAN_OMEGA` of `aief_experiment_engine_v1.py`; `FROZEN_ALPHA = 0.9994288298464774` in
float64). `2 (1 - α) = 0.00114234…`. Exact reals; the engine's float64 `α` is not this real. -/

def alphaE : ℝ := Real.exp (-((1/100) / (25 / (857/600))))

private theorem alphaE_range : 1/2 ≤ alphaE ∧ alphaE < 1 := by
  have e : alphaE = Real.exp (-(857/1500000)) := by
    unfold alphaE
    norm_num
  have h1 := Real.one_sub_le_exp_neg (857/1500000 : ℝ)
  have h3 : Real.exp (-(857/1500000 : ℝ)) < 1 :=
    Real.exp_lt_one_iff.mpr (by norm_num)
  rw [e]
  constructor <;> linarith

/-- Closed-number probe at the engine `α`: `0.00114 < 2 (1 - α) < 0.00115`. -/
theorem engine_speed_limit_value :
    (114 : ℝ)/100000 < 2*(1-alphaE) ∧ 2*(1-alphaE) < 115/100000 := by
  have e : alphaE = Real.exp (-(857/1500000)) := by
    unfold alphaE
    norm_num
  have h1 := Real.one_sub_le_exp_neg (857/1500000 : ℝ)
  have h2 : Real.exp (-(857/1500000 : ℝ)) * (1 + 857/1500000) ≤ 1 := by
    calc Real.exp (-(857/1500000 : ℝ)) * (1 + 857/1500000)
        ≤ Real.exp (-(857/1500000 : ℝ)) * Real.exp (857/1500000) := by
          apply mul_le_mul_of_nonneg_left _ (Real.exp_pos _).le
          linarith [Real.add_one_le_exp (857/1500000 : ℝ)]
      _ = 1 := by rw [← Real.exp_add]; simp
  rw [e]
  constructor <;> linarith

/-- At the engine `α` the factor 2 is attained: one step moves `R` by exactly `2 (1 - α)`. -/
theorem engine_factor_two_attained :
    |Rval alphaE 1 1 - Rval alphaE 1 0| = 2*(1-alphaE) := by
  have hr := alphaE_range
  unfold Rval rTrace
  norm_num [PhaseCoherence.reported, value_first, value_zero, valueC]
  have he : (alphaE : ℂ) - (1 - (alphaE : ℂ)) = ((2*alphaE-1 : ℝ) : ℂ) := by
    push_cast
    ring
  rw [he,Complex.norm_of_nonneg (by linarith : 0 ≤ 2*alphaE-1)]
  rw [abs_of_nonpos (by linarith : 2*alphaE-1-1 ≤ 0)]
  ring

/-- The per-step movement of `R` at the engine `α` is `0.00114…`, not `0.5`. -/
theorem engine_step_value :
    (114 : ℝ)/100000 < |Rval alphaE 1 1 - Rval alphaE 1 0| ∧
      |Rval alphaE 1 1 - Rval alphaE 1 0| < 115/100000 := by
  rw [engine_factor_two_attained]
  exact engine_speed_limit_value

theorem engine_factor_one_refuted :
    ¬ |Rval alphaE 1 1 - Rval alphaE 1 0| ≤ 1-alphaE := by
  rw [engine_factor_two_attained]
  have hr := alphaE_range
  linarith

end ValueProbes

end
end AIEFGate.CoherenceMotion
