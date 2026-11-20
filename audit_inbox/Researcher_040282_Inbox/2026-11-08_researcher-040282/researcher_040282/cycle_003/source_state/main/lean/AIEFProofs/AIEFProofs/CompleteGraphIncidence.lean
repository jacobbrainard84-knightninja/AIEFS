/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFProofs.ControllerFiber
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-!
# Kernel dimension of the unsigned incidence matrix of `K_n`, `n = 3, …, 6`

For an edge list given by endpoint maps `src dst : Fin m → Fin n`, `inc src dst` is the
unsigned node–edge incidence matrix over `ℚ` (`1` if the node is an endpoint, else `0`).
For `n = 3, 4, 5, 6` we fix the lexicographic edge list of the complete graph `K_n`, certify
by `decide` that it lists every pair `i < j` exactly once, and prove

  `finrank ℚ (ker (inc src dst)) = Nat.choose n 2 - n`   (0, 2, 5, 9).

The proof exhibits an explicit right inverse `S` (`inc * S = 1`), so `inc` is surjective
and rank–nullity gives the kernel dimension. `S e j = 1/(n-1)` if `j` is an endpoint of `e`
and `-1/((n-1)(n-2))` otherwise.

For `K_3` we also prove the row-sum sign pattern of the one-sided rays `v_c`
(`+1` on the edge opposite `c`, `-1` on the two edges at `c`): row `c` of `inc *ᵥ v_c`
is `-2` and the other rows are `0`; and we identify rows `{0, 1}` of the `K_3` incidence
and `v_2` with `CCtrl` and `vCtrl` of `ControllerFiber`.

This is linear algebra of fixed matrices only. It does not prove that the AIEF gate has
these rays as slow directions, the value of any multiplier, or anything about the dynamics.
-/

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFProofs
namespace CompleteGraphIncidence

open Matrix Module

variable {n m : ℕ}

/-- Unsigned incidence matrix of the edge list `(src e, dst e)`. -/
def inc (src dst : Fin m → Fin n) : Matrix (Fin n) (Fin m) ℚ :=
  fun i e => if i = src e ∨ i = dst e then 1 else 0

/-- A matrix with a right inverse has kernel dimension `m - n` (rank–nullity). -/
theorem finrank_ker_of_right_inverse (M : Matrix (Fin n) (Fin m) ℚ)
    (S : Matrix (Fin m) (Fin n) ℚ) (h : M * S = 1) :
    finrank ℚ (LinearMap.ker M.mulVecLin) = m - n := by
  have hsurj : Function.Surjective M.mulVecLin := by
    intro y
    refine ⟨S *ᵥ y, ?_⟩
    rw [Matrix.mulVecLin_apply, Matrix.mulVec_mulVec, h, Matrix.one_mulVec]
  have hrange : LinearMap.range M.mulVecLin = ⊤ := LinearMap.range_eq_top.mpr hsurj
  have hrn := LinearMap.finrank_range_add_finrank_ker M.mulVecLin
  rw [hrange, finrank_top, finrank_fin_fun, finrank_fin_fun] at hrn
  omega

/-- The explicit right inverse used for `K_n`. -/
def rinv (src dst : Fin m → Fin n) : Matrix (Fin m) (Fin n) ℚ :=
  fun e j =>
    if j = src e ∨ j = dst e then 1 / ((n : ℚ) - 1)
    else -1 / (((n : ℚ) - 1) * ((n : ℚ) - 2))

/-! ### Lexicographic edge lists of `K_3`, …, `K_6` -/

def src3 : Fin 3 → Fin 3 := ![0, 0, 1]
def dst3 : Fin 3 → Fin 3 := ![1, 2, 2]
def src4 : Fin 6 → Fin 4 := ![0, 0, 0, 1, 1, 2]
def dst4 : Fin 6 → Fin 4 := ![1, 2, 3, 2, 3, 3]
def src5 : Fin 10 → Fin 5 := ![0, 0, 0, 0, 1, 1, 1, 2, 2, 3]
def dst5 : Fin 10 → Fin 5 := ![1, 2, 3, 4, 2, 3, 4, 3, 4, 4]
def src6 : Fin 15 → Fin 6 := ![0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
def dst6 : Fin 15 → Fin 6 := ![1, 2, 3, 4, 5, 2, 3, 4, 5, 3, 4, 5, 4, 5, 5]

/-- The edge list is exactly the set of pairs `i < j`, each listed once
(every edge satisfies `src < dst`, and each pair `i < j` is hit by exactly one edge). -/
def IsCompleteEdgeList (src dst : Fin m → Fin n) : Prop :=
  (∀ e, src e < dst e) ∧
    ∀ i j : Fin n, i < j → (Finset.univ.filter (fun e => src e = i ∧ dst e = j)).card = 1

theorem complete3 : IsCompleteEdgeList src3 dst3 := by
  unfold IsCompleteEdgeList src3 dst3; decide
theorem complete4 : IsCompleteEdgeList src4 dst4 := by
  unfold IsCompleteEdgeList src4 dst4; decide
theorem complete5 : IsCompleteEdgeList src5 dst5 := by
  unfold IsCompleteEdgeList src5 dst5; decide
theorem complete6 : IsCompleteEdgeList src6 dst6 := by
  unfold IsCompleteEdgeList src6 dst6; decide

theorem rinv3 : inc src3 dst3 * rinv src3 dst3 = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [inc, rinv, src3, dst3, Matrix.mul_apply, Fin.sum_univ_succ] <;>
    norm_num

theorem rinv4 : inc src4 dst4 * rinv src4 dst4 = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [inc, rinv, src4, dst4, Matrix.mul_apply, Fin.sum_univ_succ] <;>
    norm_num

theorem rinv5 : inc src5 dst5 * rinv src5 dst5 = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [inc, rinv, src5, dst5, Matrix.mul_apply, Fin.sum_univ_succ] <;>
    norm_num

theorem rinv6 : inc src6 dst6 * rinv src6 dst6 = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [inc, rinv, src6, dst6, Matrix.mul_apply, Fin.sum_univ_succ] <;>
    norm_num

/-- `dim ker = C(3,2) - 3 = 0`. -/
theorem finrank_ker_K3 :
    finrank ℚ (LinearMap.ker (inc src3 dst3).mulVecLin) = Nat.choose 3 2 - 3 := by
  rw [finrank_ker_of_right_inverse _ _ rinv3]; decide

/-- `dim ker = C(4,2) - 4 = 2`. -/
theorem finrank_ker_K4 :
    finrank ℚ (LinearMap.ker (inc src4 dst4).mulVecLin) = Nat.choose 4 2 - 4 := by
  rw [finrank_ker_of_right_inverse _ _ rinv4]; decide

/-- `dim ker = C(5,2) - 5 = 5`. -/
theorem finrank_ker_K5 :
    finrank ℚ (LinearMap.ker (inc src5 dst5).mulVecLin) = Nat.choose 5 2 - 5 := by
  rw [finrank_ker_of_right_inverse _ _ rinv5]; decide

/-- `dim ker = C(6,2) - 6 = 9`. -/
theorem finrank_ker_K6 :
    finrank ℚ (LinearMap.ker (inc src6 dst6).mulVecLin) = Nat.choose 6 2 - 6 := by
  rw [finrank_ker_of_right_inverse _ _ rinv6]; decide

/-! ### `K_3`: trivial kernel and the one-sided rays `v_c` -/

/-- The `K_3` incidence has trivial kernel (zero lineality of the cycle-kernel fiber). -/
theorem ker_K3_eq_bot : LinearMap.ker (inc src3 dst3).mulVecLin = ⊥ := by
  apply Submodule.finrank_eq_zero.mp
  rw [finrank_ker_K3]; decide

/-- `v c`: `+1` on the edge opposite `c`, `-1` on the two edges incident to `c`. -/
def vRay (c : Fin 3) : Fin 3 → ℚ :=
  fun e => if c = src3 e ∨ c = dst3 e then -1 else 1

/-- Row-sum sign pattern: row `c` of `inc *ᵥ v c` is `-2`. -/
theorem inc_vRay_self (c : Fin 3) : (inc src3 dst3 *ᵥ vRay c) c = -2 := by
  fin_cases c <;> simp [inc, vRay, src3, dst3, Matrix.mulVec, dotProduct, Fin.sum_univ_succ] <;>
    norm_num

/-- Row-sum sign pattern: every other row of `inc *ᵥ v c` is `0`. -/
theorem inc_vRay_other (c i : Fin 3) (h : i ≠ c) : (inc src3 dst3 *ᵥ vRay c) i = 0 := by
  fin_cases c <;> fin_cases i <;>
    simp_all [inc, vRay, src3, dst3, Matrix.mulVec, dotProduct, Fin.sum_univ_succ]

/-- Hence `-v c` raises row `c` by `2` and leaves the other rows unchanged. -/
theorem inc_neg_vRay_self (c : Fin 3) : (inc src3 dst3 *ᵥ (-vRay c)) c = 2 := by
  rw [Matrix.mulVec_neg, Pi.neg_apply, inc_vRay_self]; norm_num

/-- No ray is in the (trivial) kernel. -/
theorem vRay_not_mem_ker (c : Fin 3) : inc src3 dst3 *ᵥ vRay c ≠ 0 := by
  intro h
  have := congrFun h c
  rw [inc_vRay_self] at this
  norm_num at this

/-- Rows `{0, 1}` of the `K_3` incidence are `CCtrl`. -/
theorem inc3_rows_eq_CCtrl (i : Fin 2) (e : Fin 3) :
    inc src3 dst3 (Fin.castSucc i) e = ControllerFiber.CCtrl i e := by
  fin_cases i <;> fin_cases e <;> simp [inc, src3, dst3, ControllerFiber.CCtrl]

/-- The ray at the non-controller node `2` is `vCtrl`. -/
theorem vRay_two_eq_vCtrl : vRay 2 = ControllerFiber.vCtrl := by
  funext e
  fin_cases e <;> simp [vRay, src3, dst3, ControllerFiber.vCtrl]

end CompleteGraphIncidence
end AIEFProofs
