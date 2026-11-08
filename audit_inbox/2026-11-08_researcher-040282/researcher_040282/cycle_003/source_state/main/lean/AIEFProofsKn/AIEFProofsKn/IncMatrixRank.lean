/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import Mathlib.Combinatorics.SimpleGraph.IncMatrix
import Mathlib.Combinatorics.SimpleGraph.Bipartite
import Mathlib.Combinatorics.SimpleGraph.Connectivity.Connected
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Tactic.LinearCombination

/-!
# Rank of the unsigned incidence matrix of a connected non-bipartite graph

* `mulVecLin_surjective_of_vecMul_eq_zero`: a matrix over a field whose left kernel is trivial
  has surjective `mulVecLin` (full row rank); `finrank_ker_mulVecLin_of_surjective` is
  rank–nullity, kernel dimension `#cols - #rows`.
* `eq_zero_of_forall_adj_add_eq_zero`: on a connected, non-bipartite graph over a field of
  characteristic `≠ 2`, a vertex function with `y a + y b = 0` on every edge is `0`.
* `incMatrix_mulVecLin_surjective`, `rank_incMatrix`: hence `G.incMatrix K` has rank `#V`.
* `edgeIncMatrix`, `finrank_ker_edgeIncMatrix`: the incidence matrix with columns restricted to
  the actual edges has kernel dimension `#E - #V`.
* `finrank_ker_edgeIncMatrix_top`: for `K_n`, `n ≥ 3`, this is `n.choose 2 - n`.

Scope of the hypotheses. "Connected and non-bipartite" is **sufficient, not necessary**, for the
statements used here. Over a field of characteristic `≠ 2` the rank of the unsigned incidence
matrix is `#V - (number of bipartite connected components)`; this file proves only the
connected non-bipartite case. In characteristic `2` the unsigned and signed incidence matrices
coincide and the rank drops (for `K_3` over `ZMod 2` the map is not surjective; see
`AIEFProofsKn.CompleteGraphKn`).

Why `edgeIncMatrix`. Mathlib's `SimpleGraph.incMatrix` has one column for every element of
`Sym2 V`, including the diagonal elements `s(v, v)` and all non-edges, and those columns are
zero. Its kernel is therefore larger by the number of such columns (for `K_n`:
`finrank_ker_incMatrix_top` gives `#Sym2 (Fin n) - n = C(n,2)`, not `C(n,2) - n`). The
edge-restricted `edgeIncMatrix` is the matrix that matches the repository's `inc`.

This is linear algebra of fixed matrices. It says nothing about the AIEF dynamics.
-/

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFProofs
namespace IncMatrixRank

open Finset Matrix Module SimpleGraph

/-! ### Linear algebra -/

section LinearAlgebra

variable {K : Type*} [Field K] {m ι : Type*} [Fintype m] [Fintype ι]

/-- Trivial left kernel implies surjectivity of `M.mulVecLin` (full row rank). -/
theorem mulVecLin_surjective_of_vecMul_eq_zero (M : Matrix m ι K)
    (h : ∀ y : m → K, y ᵥ* M = 0 → y = 0) : Function.Surjective M.mulVecLin := by
  have hinj : Function.Injective Mᵀ.mulVecLin := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro y hy
    apply h
    rwa [Matrix.mulVecLin_apply, Matrix.mulVec_transpose] at hy
  have hrank : M.rank = Fintype.card m := by
    rw [← Matrix.rank_transpose, Matrix.rank, LinearMap.finrank_range_of_inj hinj,
      Module.finrank_fintype_fun_eq_card]
  have htop : LinearMap.range M.mulVecLin = ⊤ :=
    Submodule.eq_top_of_finrank_eq (by rw [Module.finrank_fintype_fun_eq_card]; exact hrank)
  exact LinearMap.range_eq_top.mp htop

/-- Rank–nullity for a surjective `mulVecLin`. -/
theorem finrank_ker_mulVecLin_of_surjective (M : Matrix m ι K)
    (h : Function.Surjective M.mulVecLin) :
    finrank K (LinearMap.ker M.mulVecLin) = Fintype.card ι - Fintype.card m := by
  have hrn := LinearMap.finrank_range_add_finrank_ker M.mulVecLin
  rw [LinearMap.range_eq_top.mpr h, finrank_top, Module.finrank_fintype_fun_eq_card,
    Module.finrank_fintype_fun_eq_card] at hrn
  omega

end LinearAlgebra

/-! ### Graphs -/

section Graphs

variable {K : Type*} [Field K] {V : Type*} [Fintype V] [DecidableEq V]
  (G : SimpleGraph V) [DecidableRel G.Adj]

omit [Fintype V] [DecidableEq V] in
/-- Along any walk, a function that is "antisymmetric across edges" changes at most by sign. -/
theorem walk_eq_or_eq_neg_of_forall_adj_add_eq_zero {G : SimpleGraph V} {y : V → K}
    (hy : ∀ a b, G.Adj a b → y a + y b = 0) {u v : V} (p : G.Walk u v) :
    y v = y u ∨ y v = -y u := by
  induction p with
  | nil => exact Or.inl rfl
  | @cons a b c h p ih =>
    have hab : y b = -y a := by linear_combination hy a b h
    rcases ih with h1 | h1
    · exact Or.inr (h1.trans hab)
    · exact Or.inl (by rw [h1, hab, neg_neg])

omit [Fintype V] [DecidableEq V] in
/-- On a connected non-bipartite graph over a field of characteristic `≠ 2`, the only
vertex function with `y a + y b = 0` on every edge is `0`. -/
theorem eq_zero_of_forall_adj_add_eq_zero [NeZero (2 : K)] {G : SimpleGraph V}
    (hconn : G.Connected) (hnb : ¬ G.IsBipartite) {y : V → K}
    (hy : ∀ a b, G.Adj a b → y a + y b = 0) : y = 0 := by
  have h2 : ∀ t : K, t + t = 0 → t = 0 := fun t ht => by
    have : (2 : K) * t = 0 := by linear_combination ht
    exact (mul_eq_zero.mp this).resolve_left two_ne_zero
  classical
  funext u
  rw [Pi.zero_apply]
  by_contra hu
  have hpm : ∀ v, y v = y u ∨ y v = -y u := fun v =>
    walk_eq_or_eq_neg_of_forall_adj_add_eq_zero hy (hconn.preconnected u v).some
  refine hnb ⟨Coloring.mk (fun v => if y v = y u then (0 : Fin 2) else 1) ?_⟩
  intro v w hvw
  have hs := hy v w hvw
  split_ifs with h1 h2' h2'
  · exact fun _ => hu (h2 _ (by linear_combination hs - h1 - h2'))
  · decide
  · decide
  · have hv : y v = -y u := (hpm v).resolve_left h1
    have hw : y w = -y u := (hpm w).resolve_left h2'
    exact fun _ => hu (h2 _ (by linear_combination -hs + hv + hw))

/-- Entries of `y ᵥ* G.incMatrix K` on an edge `s(a, b)`. -/
theorem vecMul_incMatrix_mk_of_adj (y : V → K) {a b : V} (h : G.Adj a b) :
    (y ᵥ* G.incMatrix K) s(a, b) = y a + y b := by
  have hent : ∀ c, G.incMatrix K c s(a, b) = if c = a ∨ c = b then 1 else 0 := by
    intro c
    simp only [incMatrix_apply']
    simp [mk'_mem_incidenceSet_iff, h]
  have hsplit : ∀ c, y c * (if c = a ∨ c = b then 1 else 0 : K) =
      (if c = a then y c else 0) + (if c = b then y c else 0) := by
    intro c
    by_cases ha : c = a <;> by_cases hb : c = b
    · exact absurd (ha.symm.trans hb) h.ne
    all_goals simp [ha, hb, h.ne, h.ne.symm]
  simp only [vecMul, dotProduct, hent, hsplit, Finset.sum_add_distrib, Finset.sum_ite_eq',
    Finset.mem_univ, if_true]

/-- **Full row rank.** The unsigned incidence matrix of a connected non-bipartite graph over a
field of characteristic `≠ 2` has surjective `mulVecLin`, i.e. rank `#V`. -/
theorem incMatrix_mulVecLin_surjective [NeZero (2 : K)] (hconn : G.Connected)
    (hnb : ¬ G.IsBipartite) : Function.Surjective (G.incMatrix K).mulVecLin :=
  mulVecLin_surjective_of_vecMul_eq_zero _ fun y hy =>
    eq_zero_of_forall_adj_add_eq_zero hconn hnb fun a b h => by
      rw [← vecMul_incMatrix_mk_of_adj G y h, hy, Pi.zero_apply]

/-- The unsigned incidence matrix of a connected non-bipartite graph has rank `#V`
(characteristic `≠ 2`). -/
theorem rank_incMatrix [NeZero (2 : K)] (hconn : G.Connected) (hnb : ¬ G.IsBipartite) :
    (G.incMatrix K).rank = Fintype.card V := by
  rw [Matrix.rank, LinearMap.range_eq_top.mpr (incMatrix_mulVecLin_surjective G hconn hnb),
    finrank_top, Module.finrank_fintype_fun_eq_card]

variable (K) in
/-- The incidence matrix with columns restricted to actual edges (Mathlib's `incMatrix` has a
column for every element of `Sym2 V`, including the zero columns of the diagonal and of
non-edges). -/
def edgeIncMatrix : Matrix V G.edgeSet K :=
  (G.incMatrix K).submatrix id Subtype.val

/-- The edge-restricted incidence map is surjective (connected, non-bipartite, char `≠ 2`). -/
theorem edgeIncMatrix_mulVecLin_surjective [NeZero (2 : K)] (hconn : G.Connected)
    (hnb : ¬ G.IsBipartite) : Function.Surjective (edgeIncMatrix K G).mulVecLin :=
  mulVecLin_surjective_of_vecMul_eq_zero _ fun y hy =>
    eq_zero_of_forall_adj_add_eq_zero hconn hnb fun a b h => by
      have := congrFun hy ⟨s(a, b), h⟩
      rw [← vecMul_incMatrix_mk_of_adj G y h]
      simpa [edgeIncMatrix, vecMul, dotProduct] using this

/-- **Kernel dimension.** For a connected non-bipartite graph, `dim ker = #E - #V`. -/
theorem finrank_ker_edgeIncMatrix [NeZero (2 : K)] (hconn : G.Connected)
    (hnb : ¬ G.IsBipartite) :
    finrank K (LinearMap.ker (edgeIncMatrix K G).mulVecLin) =
      #G.edgeFinset - Fintype.card V := by
  rw [finrank_ker_mulVecLin_of_surjective _
    (edgeIncMatrix_mulVecLin_surjective G hconn hnb), card_edgeSet]

end Graphs

/-! ### The complete graph `K_n` -/

/-- `K_n` is not bipartite for `n ≥ 3`. -/
theorem not_isBipartite_top {n : ℕ} (hn : 3 ≤ n) : ¬ (⊤ : SimpleGraph (Fin n)).IsBipartite := by
  intro hc
  have := hc.card_le_of_pairwise_adj (id : Fin n → Fin n) (fun i j hij => by simpa using hij)
  simp at this
  omega

/-- `K_n` is connected for `n ≥ 3` (in fact for `n ≥ 1`). -/
theorem connected_top_fin {n : ℕ} (hn : 3 ≤ n) : (⊤ : SimpleGraph (Fin n)).Connected :=
  haveI : Nonempty (Fin n) := ⟨⟨0, by omega⟩⟩
  connected_top

/-- `K_n`, `n ≥ 3`: the unsigned incidence map `ℚ^{Sym2 (Fin n)} → ℚ^n` is surjective. -/
theorem incMatrix_top_mulVecLin_surjective {n : ℕ} (hn : 3 ≤ n) :
    Function.Surjective ((⊤ : SimpleGraph (Fin n)).incMatrix ℚ).mulVecLin :=
  incMatrix_mulVecLin_surjective _ (connected_top_fin hn) (not_isBipartite_top hn)

/-- `K_n`, `n ≥ 3`: the edge-indexed unsigned incidence map is surjective. -/
theorem edgeIncMatrix_top_mulVecLin_surjective {n : ℕ} (hn : 3 ≤ n) :
    Function.Surjective (edgeIncMatrix ℚ (⊤ : SimpleGraph (Fin n))).mulVecLin :=
  edgeIncMatrix_mulVecLin_surjective _ (connected_top_fin hn) (not_isBipartite_top hn)

/-- **Main theorem.** `K_n`, `n ≥ 3`: `dim ker = C(n,2) - n`. -/
theorem finrank_ker_edgeIncMatrix_top {n : ℕ} (hn : 3 ≤ n) :
    finrank ℚ (LinearMap.ker (edgeIncMatrix ℚ (⊤ : SimpleGraph (Fin n))).mulVecLin) =
      n.choose 2 - n := by
  rw [finrank_ker_edgeIncMatrix _ (connected_top_fin hn) (not_isBipartite_top hn)]
  convert congrArg (· - n) (card_edgeFinset_top_eq_card_choose_two (V := Fin n)) using 2 <;>
    simp

/-- Same statement with `n(n-1)/2`. -/
theorem finrank_ker_edgeIncMatrix_top' {n : ℕ} (hn : 3 ≤ n) :
    finrank ℚ (LinearMap.ker (edgeIncMatrix ℚ (⊤ : SimpleGraph (Fin n))).mulVecLin) =
      n * (n - 1) / 2 - n := by
  rw [finrank_ker_edgeIncMatrix_top hn, Nat.choose_two_right]

/-- With Mathlib's `Sym2`-indexed columns (which include the `n` zero diagonal columns
`s(i,i)`), the kernel has dimension `#Sym2 (Fin n) - n = C(n,2)`, not `C(n,2) - n`. -/
theorem finrank_ker_incMatrix_top {n : ℕ} (hn : 3 ≤ n) :
    finrank ℚ (LinearMap.ker ((⊤ : SimpleGraph (Fin n)).incMatrix ℚ).mulVecLin) =
      Fintype.card (Sym2 (Fin n)) - n := by
  rw [finrank_ker_mulVecLin_of_surjective _ (incMatrix_top_mulVecLin_surjective hn),
    Fintype.card_fin]

end IncMatrixRank
end AIEFProofs
