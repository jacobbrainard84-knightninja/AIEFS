/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.HeteroStepRef

/-!
# Gap guard implies the heterogeneous row condition (Arena D17)

Research candidate (shares the `HeteroStepRef` namespace). The exact-real gap guard `δ - tol ≤ a -
q·row_i` with `0 < q` and `dt·((a - δ + tol)/q) ≤ 1` gives the all-time window invariant of
`HeteroStepRef`; the engine default constants satisfy the cap (exact rationals). Not the float64
guard or adaptive B. `false_*` witnesses appended (SPEC §17).

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D17, deposit sha256 `9ebe0002…`; proofs and
statements unchanged from the deposit.
-/

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

/-! ### Negations used by the mutation harness (SPEC §17) -/

/-- Dropping the cap from `guarded_window_all_steps` is false (`n = 1`, `B = 2`, `a = 2`, `q =
1`). -/
theorem false_guarded_no_cap :
    ¬ (∀ (n d : ℕ) (dt M a q delta tol : ℝ) (B : Fin n → Fin n → ℝ) (v : ℕ → Fin n → ℝ)
      (_hdt : 0 ≤ dt) (_hB : ∀ i j, 0 ≤ B i j) (_hq : 0 < q)
      (_hguard : ∀ i, delta - tol ≤ a - q * row n B i) (_hcap : True)
      (_hM : 0 ≤ M) (_hv : ∀ k, k ≤ d → ∀ i, |v k i| ≤ M),
      ∀ t k, k ≤ d → ∀ i, |iterate n d dt B v t k i| ≤ M) := by
  intro H
  have h := H 1 1 1 1 2 1 0 0 (fun _ _ => 2) (fun k _ => if k = 0 then 1 else -1) (by norm_num)
    (fun _ _ => by norm_num) (by norm_num) (fun _ => by norm_num [row]) trivial (by norm_num)
    (fun k _ _ => by by_cases hk : k = 0 <;> simp [hk]) 1 0 (by norm_num) 0
  norm_num [iterate, linearStep, row, abs_le] at h

/-- Dropping `0 < q` from `guarded_window_all_steps` is false (`q = 0`: the cap reads `dt·0 ≤
1`). -/
theorem false_guarded_no_q :
    ¬ (∀ (n d : ℕ) (dt M a q delta tol : ℝ) (B : Fin n → Fin n → ℝ) (v : ℕ → Fin n → ℝ)
      (_hdt : 0 ≤ dt) (_hB : ∀ i j, 0 ≤ B i j) (_hq : True)
      (_hguard : ∀ i, delta - tol ≤ a - q * row n B i)
      (_hcap : dt * ((a - delta + tol) / q) ≤ 1)
      (_hM : 0 ≤ M) (_hv : ∀ k, k ≤ d → ∀ i, |v k i| ≤ M),
      ∀ t k, k ≤ d → ∀ i, |iterate n d dt B v t k i| ≤ M) := by
  intro H
  have h := H 1 1 1 1 0 0 0 0 (fun _ _ => 2) (fun k _ => if k = 0 then 1 else -1) (by norm_num)
    (fun _ _ => by norm_num) trivial (fun _ => by norm_num [row]) (by norm_num) (by norm_num)
    (fun k _ _ => by by_cases hk : k = 0 <;> simp [hk]) 1 0 (by norm_num) 0
  norm_num [iterate, linearStep, row, abs_le] at h

#print axioms false_guarded_no_cap
#print axioms false_guarded_no_q

end
end AIEFGate.HeteroStepRef
