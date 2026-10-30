/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFProofs.CompleteGraphIncidence
import AIEFProofsKn.IncMatrixRank
import AIEFProofsKn.CompleteGraphRightInverse
import Mathlib.Algebra.Field.ZMod

/-!
# `dim ker = C(n,2) − n` for the repository's `inc`, for every `n ≥ 3`

All statements here are about the repository's own definitions
`AIEFProofs.CompleteGraphIncidence.inc`, `IsCompleteEdgeList` and `rinv`
(`lean/AIEFProofs/AIEFProofs/CompleteGraphIncidence.lean`, imported unchanged; that file proves
the cases `n = 3, …, 6` one by one). For every edge list `src dst : Fin m → Fin n` that lists
each pair `i < j` exactly once (`IsCompleteEdgeList`) and every `n ≥ 3`:

* `inc_mulVecLin_surjective`: `inc src dst` has full row rank `n`;
* `card_eq_choose_two`: `m = C(n,2)`;
* `finrank_ker_inc`, `finrank_ker_inc_eq_choose`: `dim ker (inc src dst) = m − n = C(n,2) − n`;
* `inc_mul_rinv`: the repository's hand-written `rinv src dst` is a right inverse for every
  `n ≥ 3` (the repository checks this only for `n = 3, …, 6`);
* `finrank_ker_K12_eq_54`: for the 12-node lexicographic edge list (66 edges), `dim ker = 54`.

The general argument is in `AIEFProofsKn.IncMatrixRank`: the left kernel of the unsigned
incidence matrix of a connected non-bipartite graph is trivial over a field of characteristic
`≠ 2`. The hypotheses are sufficient, not necessary (rank = `#V − #bipartite components` in
characteristic `≠ 2`); `not_surjective_char_two` and `exists_left_kernel_K2` show that the two
hypotheses cannot simply be dropped.

This is linear algebra of fixed matrices. It does not say which edges the AIEF dynamics keep,
that the gate selects these kernels, or anything else about the dynamics.
-/

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFProofs
namespace CompleteGraphKn

open Finset Matrix Module SimpleGraph
open AIEFProofs.CompleteGraphIncidence (inc rinv IsCompleteEdgeList)

variable {n m : ℕ}

/-- Entries of `y ᵥ* inc src dst` on an edge with distinct endpoints. -/
theorem vecMul_inc {src dst : Fin m → Fin n} (y : Fin n → ℚ) (e : Fin m)
    (he : src e ≠ dst e) : (y ᵥ* inc src dst) e = y (src e) + y (dst e) := by
  have hsplit : ∀ c, y c * inc src dst c e =
      (if src e = c then y c else 0) + (if dst e = c then y c else 0) := by
    intro c
    rcases eq_or_ne c (src e) with rfl | ha
    · simp [inc, he, Ne.symm he]
    rcases eq_or_ne c (dst e) with rfl | hb
    · simp [inc, ha, Ne.symm ha]
    · simp [inc, ha, hb, Ne.symm ha, Ne.symm hb]
  simp only [vecMul, dotProduct, hsplit, Finset.sum_add_distrib, Finset.sum_ite_eq,
    Finset.mem_univ, if_true]

/-- **Full row rank** of the repository's `inc` for every complete edge list, `n ≥ 3`. -/
theorem inc_mulVecLin_surjective {src dst : Fin m → Fin n} (hc : IsCompleteEdgeList src dst)
    (hn : 3 ≤ n) : Function.Surjective (inc src dst).mulVecLin := by
  refine IncMatrixRank.mulVecLin_surjective_of_vecMul_eq_zero _ fun y hy =>
    IncMatrixRank.eq_zero_of_forall_adj_add_eq_zero (G := (⊤ : SimpleGraph (Fin n)))
      (IncMatrixRank.connected_top_fin hn) (IncMatrixRank.not_isBipartite_top hn) ?_
  have key : ∀ a b : Fin n, a < b → y a + y b = 0 := by
    intro a b hab
    obtain ⟨e, he⟩ : (Finset.univ.filter (fun e => src e = a ∧ dst e = b)).Nonempty :=
      Finset.card_pos.mp (by rw [hc.2 a b hab]; norm_num)
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at he
    have := congrFun hy e
    rw [vecMul_inc y e (ne_of_lt (hc.1 e)), he.1, he.2] at this
    simpa using this
  intro a b hab
  rcases lt_or_gt_of_ne ((top_adj a b).mp hab) with h | h
  · exact key a b h
  · rw [add_comm]; exact key b a h

/-- **General kernel dimension:** `dim ker (inc src dst) = m − n` (`m` = number of edges). -/
theorem finrank_ker_inc {src dst : Fin m → Fin n} (hc : IsCompleteEdgeList src dst)
    (hn : 3 ≤ n) : finrank ℚ (LinearMap.ker (inc src dst).mulVecLin) = m - n := by
  rw [IncMatrixRank.finrank_ker_mulVecLin_of_surjective _ (inc_mulVecLin_surjective hc hn)]
  simp

/-- A complete edge list is a bijection `e ↦ s(src e, dst e)` onto the edges of `K_n`; so
sums over the list are sums over the edge set of `K_n`. -/
theorem sum_edgeList_eq_sum_edgeFinset {src dst : Fin m → Fin n}
    (hc : IsCompleteEdgeList src dst) (f : Sym2 (Fin n) → ℚ) :
    ∑ e, f s(src e, dst e) = ∑ z ∈ (⊤ : SimpleGraph (Fin n)).edgeFinset, f z := by
  refine Finset.sum_bij (fun e _ => s(src e, dst e)) ?_ ?_ ?_ ?_
  · intro e _
    simpa [mem_edgeFinset] using ne_of_lt (hc.1 e)
  · intro a _ b _ hab
    rcases Sym2.eq_iff.mp hab with ⟨h1, h2⟩ | ⟨h1, h2⟩
    · have hone := hc.2 (src a) (dst a) (hc.1 a)
      obtain ⟨x, hx⟩ := Finset.card_eq_one.mp hone
      have ha : a ∈ Finset.univ.filter (fun e => src e = src a ∧ dst e = dst a) := by simp
      have hb : b ∈ Finset.univ.filter (fun e => src e = src a ∧ dst e = dst a) := by
        simp [h1, h2]
      rw [hx, Finset.mem_singleton] at ha hb
      rw [ha, hb]
    · -- `src a = dst b > src b = dst a > src a` is impossible
      have ha := hc.1 a
      have hb := hc.1 b
      rw [h1, h2] at ha
      exact absurd (ha.trans hb) (lt_irrefl _)
  · intro z hz
    induction z using Sym2.ind with
    | _ i j =>
      have hij : i ≠ j := by simpa [mem_edgeFinset] using hz
      have get : ∀ a b : Fin n, a < b → ∃ e, src e = a ∧ dst e = b := by
        intro a b hab
        obtain ⟨e, he⟩ : (Finset.univ.filter (fun e => src e = a ∧ dst e = b)).Nonempty :=
          Finset.card_pos.mp (by rw [hc.2 a b hab]; norm_num)
        exact ⟨e, by simpa using he⟩
      rcases lt_or_gt_of_ne hij with h | h
      · obtain ⟨e, h1, h2⟩ := get i j h
        exact ⟨e, Finset.mem_univ _, by rw [h1, h2]⟩
      · obtain ⟨e, h1, h2⟩ := get j i h
        exact ⟨e, Finset.mem_univ _, by rw [h1, h2, Sym2.eq_swap]⟩
  · intro _ _; rfl

/-- A complete edge list on `n` nodes has `C(n,2)` edges. -/
theorem card_eq_choose_two {src dst : Fin m → Fin n} (hc : IsCompleteEdgeList src dst) :
    m = n.choose 2 := by
  have h := sum_edgeList_eq_sum_edgeFinset hc (fun _ => (1 : ℚ))
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul, mul_one,
    card_edgeFinset_top_eq_card_choose_two] at h
  exact_mod_cast h

/-- **Main theorem (repository form):** for every complete edge list on `n ≥ 3` nodes,
`dim ker (inc src dst) = C(n,2) − n`. -/
theorem finrank_ker_inc_eq_choose {src dst : Fin m → Fin n} (hc : IsCompleteEdgeList src dst)
    (hn : 3 ≤ n) :
    finrank ℚ (LinearMap.ker (inc src dst).mulVecLin) = n.choose 2 - n := by
  rw [finrank_ker_inc hc hn, card_eq_choose_two hc]

/-- On an edge with distinct endpoints, the repository's `inc` column is Mathlib's
`incMatrix` column of `s(src e, dst e)` for `K_n`. -/
theorem inc_apply_eq_incMatrix {src dst : Fin m → Fin n} (e : Fin m) (he : src e ≠ dst e)
    (i : Fin n) :
    inc src dst i e = (⊤ : SimpleGraph (Fin n)).incMatrix ℚ i s(src e, dst e) := by
  have hadj : (⊤ : SimpleGraph (Fin n)).Adj (src e) (dst e) := (top_adj _ _).mpr he
  simp only [inc, incMatrix_apply']
  simp [mk'_mem_incidenceSet_iff, hadj]

/-- The repository's `rinv` entries are the entries of `CompleteGraphRightInverse.rinv`. -/
theorem rinv_eq_rinv {src dst : Fin m → Fin n} (hn : 3 ≤ n) (e : Fin m)
    (he : src e ≠ dst e) (j : Fin n) :
    rinv src dst e j = CompleteGraphRightInverse.rinv n s(src e, dst e) j := by
  rw [CompleteGraphRightInverse.rinv_apply_of_ne hn he]
  rfl

/-- **General right inverse:** `inc src dst * rinv src dst = 1` for every complete edge list
and every `n ≥ 3` (the repository proves this for `n = 3, …, 6` by computation). -/
theorem inc_mul_rinv {src dst : Fin m → Fin n} (hc : IsCompleteEdgeList src dst)
    (hn : 3 ≤ n) : inc src dst * rinv src dst = 1 := by
  ext i j
  have hM := CompleteGraphRightInverse.incMatrix_mul_rinv hn
  have hij := congrFun (congrFun hM i) j
  rw [Matrix.mul_apply] at hij ⊢
  rw [← hij]
  have hne : ∀ e, src e ≠ dst e := fun e => ne_of_lt (hc.1 e)
  calc ∑ e, inc src dst i e * rinv src dst e j
      = ∑ e, (fun z => (⊤ : SimpleGraph (Fin n)).incMatrix ℚ i z *
          CompleteGraphRightInverse.rinv n z j) s(src e, dst e) := by
        refine Finset.sum_congr rfl fun e _ => ?_
        rw [inc_apply_eq_incMatrix e (hne e), rinv_eq_rinv hn e (hne e)]
    _ = ∑ z ∈ (⊤ : SimpleGraph (Fin n)).edgeFinset,
          (⊤ : SimpleGraph (Fin n)).incMatrix ℚ i z * CompleteGraphRightInverse.rinv n z j :=
        sum_edgeList_eq_sum_edgeFinset hc (fun z => (⊤ : SimpleGraph (Fin n)).incMatrix ℚ i z *
          CompleteGraphRightInverse.rinv n z j)
    _ = ∑ z, (⊤ : SimpleGraph (Fin n)).incMatrix ℚ i z *
          CompleteGraphRightInverse.rinv n z j := by
        refine Finset.sum_subset (Finset.subset_univ _) fun z _ hz => ?_
        have : z ∉ (⊤ : SimpleGraph (Fin n)).incidenceSet i := fun h =>
          hz (by simpa [mem_edgeFinset] using h.1)
        simp [incMatrix_apply', this]

/-! ### The 12-node complete graph (lexicographic edge list, 66 edges) -/

/-- Source endpoints of the lexicographic edge list of `K_12`. -/
def src12 : Fin 66 → Fin 12 :=
  ![0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2,
    2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6,
    6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 9, 10]

/-- Target endpoints of the lexicographic edge list of `K_12`. -/
def dst12 : Fin 66 → Fin 12 :=
  ![1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 3, 4, 5, 6,
    7, 8, 9, 10, 11, 4, 5, 6, 7, 8, 9, 10, 11, 5, 6, 7, 8, 9, 10, 11, 6, 7, 8, 9,
    10, 11, 7, 8, 9, 10, 11, 8, 9, 10, 11, 9, 10, 11, 10, 11, 11]

theorem complete12 : IsCompleteEdgeList src12 dst12 := by
  unfold IsCompleteEdgeList src12 dst12; decide +kernel

/-- `dim ker = C(12,2) − 12` for the repository's `inc` on the 12-node edge list. -/
theorem finrank_ker_K12 :
    finrank ℚ (LinearMap.ker (inc src12 dst12).mulVecLin) = Nat.choose 12 2 - 12 :=
  finrank_ker_inc_eq_choose complete12 (by norm_num)

/-- **`dim ker = 54`** for the repository's `inc` on the 12-node, 66-edge complete graph. -/
theorem finrank_ker_K12_eq_54 :
    finrank ℚ (LinearMap.ker (inc src12 dst12).mulVecLin) = 54 := by
  rw [finrank_ker_K12]; decide

/-- The repository's `rinv` is a right inverse for `K_12` too. -/
theorem rinv12 : inc src12 dst12 * rinv src12 dst12 = 1 :=
  inc_mul_rinv complete12 (by norm_num)

/-- The 12-node value agrees with Mathlib's edge-indexed incidence matrix of `K_12`. -/
theorem finrank_ker_K12_eq_edgeIncMatrix_top :
    finrank ℚ (LinearMap.ker (inc src12 dst12).mulVecLin) =
      finrank ℚ (LinearMap.ker
        (IncMatrixRank.edgeIncMatrix ℚ (⊤ : SimpleGraph (Fin 12))).mulVecLin) := by
  rw [finrank_ker_K12, IncMatrixRank.finrank_ker_edgeIncMatrix_top (by norm_num)]

/-! ### The repository's `n = 3, …, 6` results, re-derived from the general theorem -/

theorem finrank_ker_K3_general :
    finrank ℚ (LinearMap.ker (inc CompleteGraphIncidence.src3
      CompleteGraphIncidence.dst3).mulVecLin) = Nat.choose 3 2 - 3 :=
  finrank_ker_inc_eq_choose CompleteGraphIncidence.complete3 (by norm_num)

theorem finrank_ker_K4_general :
    finrank ℚ (LinearMap.ker (inc CompleteGraphIncidence.src4
      CompleteGraphIncidence.dst4).mulVecLin) = Nat.choose 4 2 - 4 :=
  finrank_ker_inc_eq_choose CompleteGraphIncidence.complete4 (by norm_num)

theorem finrank_ker_K5_general :
    finrank ℚ (LinearMap.ker (inc CompleteGraphIncidence.src5
      CompleteGraphIncidence.dst5).mulVecLin) = Nat.choose 5 2 - 5 :=
  finrank_ker_inc_eq_choose CompleteGraphIncidence.complete5 (by norm_num)

theorem finrank_ker_K6_general :
    finrank ℚ (LinearMap.ker (inc CompleteGraphIncidence.src6
      CompleteGraphIncidence.dst6).mulVecLin) = Nat.choose 6 2 - 6 :=
  finrank_ker_inc_eq_choose CompleteGraphIncidence.complete6 (by norm_num)

/-! ### The hypotheses cannot simply be dropped -/

/-- Characteristic `2`: the all-ones vector is a nonzero left-kernel vector of `K_3`. -/
theorem exists_left_kernel_char_two : ∃ y : Fin 3 → ZMod 2, y ≠ 0 ∧
    ∀ a b, (⊤ : SimpleGraph (Fin 3)).Adj a b → y a + y b = 0 :=
  ⟨fun _ => 1, by decide, by decide⟩

/-- Characteristic `2`: the edge incidence map of `K_3` over `ZMod 2` is not surjective. -/
theorem not_surjective_char_two : ¬ Function.Surjective
    (IncMatrixRank.edgeIncMatrix (ZMod 2) (⊤ : SimpleGraph (Fin 3))).mulVecLin := by
  intro hs
  obtain ⟨x, hx⟩ := hs (Pi.single 0 1)
  have key : ∀ v : (⊤ : SimpleGraph (Fin 3)).edgeSet → ZMod 2,
      ∑ i, (IncMatrixRank.edgeIncMatrix (ZMod 2) (⊤ : SimpleGraph (Fin 3)) *ᵥ v) i = 0 := by
    intro v
    simp only [Matrix.mulVec, dotProduct, IncMatrixRank.edgeIncMatrix, Matrix.submatrix_apply,
      id]
    rw [Finset.sum_comm]
    refine Finset.sum_eq_zero fun e _ => ?_
    rw [← Finset.sum_mul]
    have h2 := SimpleGraph.sum_incMatrix_apply_of_mem_edgeSet (R := ZMod 2) (G := ⊤) e.2
    rw [h2]
    exact mul_eq_zero_of_left (by decide) _
  have h := key x
  rw [Matrix.mulVecLin_apply] at hx
  rw [hx] at h
  simp at h

/-- Bipartite: `K_2` over `ℚ` has the `±1` colouring vector in its left kernel. -/
theorem exists_left_kernel_K2 : ∃ y : Fin 2 → ℚ, y ≠ 0 ∧
    ∀ a b, (⊤ : SimpleGraph (Fin 2)).Adj a b → y a + y b = 0 := by
  refine ⟨![1, -1], fun h => by simpa using congrFun h 0, ?_⟩
  intro a b hab
  fin_cases a <;> fin_cases b <;> simp_all

end CompleteGraphKn
end AIEFProofs
