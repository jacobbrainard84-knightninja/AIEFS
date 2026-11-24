import AIEFGateCore.HeteroStepRef

set_option autoImplicit false
namespace AIEFGate.HeteroStepRef
noncomputable section

/-- The guard bound implies the fixed-B model's all-time window invariant. -/
theorem guarded_window_all_steps (n d : ℕ) (dt M a q delta tol : ℝ)
    (B : Fin n → Fin n → ℝ) (v : ℕ → Fin n → ℝ)
    (hdt : 0 ≤ dt) (hB : ∀ i j, 0 ≤ B i j) (hq : 0 < q)
    (hguard : ∀ i, delta - tol ≤ a - q * row n B i)
    (hcap : dt * ((a - delta + tol) / q) ≤ 1)
    (hM : 0 ≤ M) (hv : ∀ k, k ≤ d → ∀ i, |v k i| ≤ M) :
    ∀ t k, k ≤ d → ∀ i, |iterate n d dt B v t k i| ≤ M := by
  apply window_all_steps n d dt M B v hdt hB
  · intro i
    exact le_trans (mul_le_mul_of_nonneg_left (guard_row_bound a q delta tol (row n B i)
      hq (hguard i)) hdt) hcap
  · exact hM
  · exact hv

/-- Exact-rational comparison for the read default constants. -/
theorem engine_constants_safe :
    (1 / 100 : ℝ) * ((1 - 1 / 20 + 1 / 1000000000) / (3 / 2)) < 1 := by
  norm_num

#print axioms guarded_window_all_steps
#print axioms engine_constants_safe
end
end AIEFGate.HeteroStepRef
