/-
Causal tracking of a moving phasor input by the actual old-input EMA recurrence.
Exact-real component composition, not floating FFI or closed-loop phase locking.
Finite bounds require alpha nonnegative, not strict contraction or alpha < 1.
-/
import CoherenceEMA
import PhaseIncrement

set_option autoImplicit false
set_option linter.style.header false

open scoped BigOperators

namespace Researcher040282.Tracking

open Researcher040282.EMA

variable {ι : Type*}

noncomputable def trackingBudget (alpha E0 : ℝ) (a : ℕ → ℝ) (n : ℕ) : ℝ :=
  alpha ^ n * E0 + ∑ k ∈ Finset.range n, alpha ^ (n - 1 - k) * a k

noncomputable def delayedPhaseInput (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) : ℂ :=
  phaseInput (Researcher040282.Phase.phaseTrace x0 u n)
    (Researcher040282.Delay.historyTrace d (Researcher040282.Phase.phaseTrace x0 u) n
      ⟨0, Nat.zero_lt_succ d⟩) omega tau i j

/-- Input motion has coefficient one: C_(n+1) consumes z_n, not z_(n+1). -/
theorem tracking_error_step (alpha : ℝ) (C0 : ℂ) (z : ℕ → ℂ) (n : ℕ) :
    emaTrajectory alpha C0 z (n + 1) - z (n + 1) =
      (alpha : ℂ) * (emaTrajectory alpha C0 z n - z n) - (z (n + 1) - z n) := by
  change emaStep alpha (emaTrajectory alpha C0 z n) (z n) - z (n + 1) = _
  unfold emaStep
  push_cast
  ring

/-- The newest input variation has weight one; initial error is not discarded. -/
theorem tracking_error_budget (alpha : ℝ) (C0 : ℂ) (z : ℕ → ℂ)
    (ha : 0 ≤ alpha) (n : ℕ) :
    ‖emaTrajectory alpha C0 z n - z n‖ ≤
      trackingBudget alpha ‖C0 - z 0‖ (fun k => ‖z (k + 1) - z k‖) n := by
  have hb (E0 : ℝ) (a : ℕ → ℝ) (m : ℕ) :
      trackingBudget alpha E0 a (m + 1) = alpha * trackingBudget alpha E0 a m + a m := by
    unfold trackingBudget
    rw [Finset.sum_range_succ]
    have hs : (∑ k ∈ Finset.range m, alpha ^ (m + 1 - 1 - k) * a k) =
        alpha * ∑ k ∈ Finset.range m, alpha ^ (m - 1 - k) * a k := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro k hk
      have hk0 : k < m := Finset.mem_range.mp hk
      have he : m + 1 - 1 - k = (m - 1 - k) + 1 := by omega
      rw [he, pow_succ]
      ring
    rw [hs]
    have ht : m + 1 - 1 - m = 0 := by omega
    rw [ht, pow_zero, one_mul, pow_succ]
    ring
  induction n with
  | zero => simp [emaTrajectory, trackingBudget]
  | succ n ih =>
      calc
        ‖emaTrajectory alpha C0 z (n + 1) - z (n + 1)‖ =
            ‖(alpha : ℂ) * (emaTrajectory alpha C0 z n - z n) - (z (n + 1) - z n)‖ := by
          rw [tracking_error_step]
        _ ≤ ‖(alpha : ℂ) * (emaTrajectory alpha C0 z n - z n)‖ + ‖z (n + 1) - z n‖ :=
          norm_sub_le _ _
        _ = alpha * ‖emaTrajectory alpha C0 z n - z n‖ + ‖z (n + 1) - z n‖ := by
          rw [norm_mul, Complex.norm_of_nonneg ha]
        _ ≤ alpha * trackingBudget alpha ‖C0 - z 0‖ (fun k => ‖z (k + 1) - z k‖) n +
            ‖z (n + 1) - z n‖ :=
          add_le_add (mul_le_mul_of_nonneg_left ih ha) le_rfl
        _ = trackingBudget alpha ‖C0 - z 0‖ (fun k => ‖z (k + 1) - z k‖) (n + 1) :=
          (hb _ _ n).symm

/-- Definition-level composition of the old EMA and startup-aware delayed phasor. -/
theorem delayed_phase_tracking_budget (alpha : ℝ) (C0 : ℂ) (ha : 0 ≤ alpha)
    (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ) (omega : ι → ℝ) (tau : ℝ)
    (n : ℕ) (i j : ι) :
    ‖emaTrajectory alpha C0 (fun k => delayedPhaseInput d x0 u omega tau k i j) n -
        delayedPhaseInput d x0 u omega tau n i j‖ ≤
      trackingBudget alpha ‖C0 - delayedPhaseInput d x0 u omega tau 0 i j‖
        (fun k => |u k i - Researcher040282.Phase.delayedIncrement d u k j|) n := by
  apply (tracking_error_budget alpha C0 (fun k => delayedPhaseInput d x0 u omega tau k i j) ha n).trans
  unfold trackingBudget
  apply add_le_add le_rfl
  apply Finset.sum_le_sum
  intro k _
  apply mul_le_mul_of_nonneg_left _ (pow_nonneg ha _)
  change ‖Researcher040282.Phase.inputPhasor d x0 u omega tau (k + 1) i j -
      Researcher040282.Phase.inputPhasor d x0 u omega tau k i j‖ ≤ _
  exact Researcher040282.Phase.delayed_input_chord_bound d x0 u omega tau k i j

#print axioms Researcher040282.Tracking.tracking_error_step
#print axioms Researcher040282.Tracking.tracking_error_budget
#print axioms Researcher040282.Tracking.delayed_phase_tracking_budget

end Researcher040282.Tracking
