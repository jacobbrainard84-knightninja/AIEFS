import AIEFGateCore.CausalEMATracking

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.EMAFiniteSum
open AIEFGate.CausalEMATracking

/-- The recursive budget equals the chronological finite convolution.
This identity needs no positivity or upper bound on alpha or the input. -/
theorem budget_eq_finite_sum (alpha E : ℝ) (drift : ℕ → ℝ) (n : ℕ) :
    budget alpha E drift n = alpha ^ n * E +
      ∑ k ∈ Finset.range n, alpha ^ (n - 1 - k) * drift k := by
  induction n with
  | zero => simp [budget]
  | succ n ih =>
    rw [budget, ih, Finset.sum_range_succ]
    have hs : (∑ k ∈ Finset.range n, alpha ^ (n + 1 - 1 - k) * drift k) =
        alpha * ∑ k ∈ Finset.range n, alpha ^ (n - 1 - k) * drift k := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro k hk
      have hkn : k < n := Finset.mem_range.mp hk
      have he : n + 1 - 1 - k = (n - 1 - k) + 1 := by omega
      rw [he, pow_succ]
      ring
    rw [hs]
    simp only [Nat.add_sub_cancel, Nat.sub_self, pow_zero, one_mul, pow_succ]
    ring

/-- The previous delayed tracking result, now in the explicit C012 sum form. -/
theorem delayed_tracking_sum {V : Type*} (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha : 0 ≤ alpha) (n : ℕ) (i j : V) :
    ‖error alpha C0 d x0 u omega tau n i j‖ ≤
      alpha ^ n * ‖error alpha C0 d x0 u omega tau 0 i j‖ +
        ∑ k ∈ Finset.range n, alpha ^ (n - 1 - k) *
          |u k i - Phase.delayedIncrement d u k j| := by
  simpa only [budget_eq_finite_sum] using
    delayed_tracking_bound alpha C0 d x0 u omega tau ha n i j

/-- The oldest drift must carry alpha squared after three updates. -/
theorem oldest_drift_probe :
    budget 2 0 (fun k => if k = 0 then 1 else 0) 3 = 4 := by
  norm_num [budget]

/-- Chronological and reversed powers are genuinely different. -/
theorem reversed_power_counterexample :
    (∑ k ∈ Finset.range 3, (2 : ℝ) ^ (3 - 1 - k) * (if k = 0 then 1 else 0)) ≠
      ∑ k ∈ Finset.range 3, (2 : ℝ) ^ k * (if k = 0 then 1 else 0) := by
  norm_num [Finset.sum_range_succ]

#print axioms budget_eq_finite_sum
#print axioms delayed_tracking_sum
#print axioms oldest_drift_probe
#print axioms reversed_power_counterexample
end AIEFGate.EMAFiniteSum
