/-
Researcher040282: additive coherence/R movement bounds.
UNMERGED team P5 branch54037ea, approved branch scope; NOT current main.
Imports team module/namespace, no flat015imports or widened state model.
The coupled non-reset/history probe remains DEFERRED until the main port.
-/
import AIEFGateCore.PhaseCoherence

set_option autoImplicit false
set_option linter.style.header false

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
      ‖PhaseCoherence.coherenceStep alpha C d x0 u omega tau n i j‖ ≤ alpha * ‖C i j‖ + (1-alpha) at hij
    change alpha * ‖C j i‖ - (1-alpha) ≤
        ‖PhaseCoherence.coherenceStep alpha C d x0 u omega tau n j i‖ ∧
      ‖PhaseCoherence.coherenceStep alpha C d x0 u omega tau n j i‖ ≤ alpha * ‖C j i‖ + (1-alpha) at hji
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
  · exact h.1
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
  exact reported_step_abs_state_bound alpha (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n)
    d x0 u omega tau ha0 ha1 n i j

/-- Current unit-disk range is inherited from C0, not postulated as a future band. -/
theorem trace_step_abs_le (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC0 : ∀ i j, ‖C0 i j‖ ≤ 1)
    (n : ℕ) (i j : V) :
    |rTrace alpha C0 d x0 u omega tau (n+1) i j - rTrace alpha C0 d x0 u omega tau n i j| ≤ 2*(1-alpha) := by
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

end
end AIEFGate.CoherenceMotion

#print axioms AIEFGate.CoherenceMotion.complex_step_bounds
#print axioms AIEFGate.CoherenceMotion.reported_nonneg
#print axioms AIEFGate.CoherenceMotion.reported_step_bounds
#print axioms AIEFGate.CoherenceMotion.reported_step_signed
#print axioms AIEFGate.CoherenceMotion.reported_step_abs_state_bound
#print axioms AIEFGate.CoherenceMotion.trace_step_bounds
#print axioms AIEFGate.CoherenceMotion.trace_step_abs_state_bound
#print axioms AIEFGate.CoherenceMotion.trace_step_abs_le
#print axioms AIEFGate.CoherenceMotion.trace_step_abs_le_min
#print axioms AIEFGate.CoherenceMotion.trace_diagonal
