/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFProofsKn.IncMatrixRank

/-!
# Explicit right inverse of the incidence matrix of `K_n`, all `n ≥ 3`

`rinv = Mᵀ Q⁻¹`, where `M` is Mathlib's (`Sym2`-indexed) unsigned incidence matrix of `K_n`,
`Q = M Mᵀ = (n-2) I + J` is the signless Laplacian of `K_n` and
`Q⁻¹ = (1/(n-2)) (I - J/(2(n-1)))`. We prove `M * rinv = 1` for all `n ≥ 3`, and that the
entries of `rinv` on an edge `s(a, b)` are the hand formula used by the repository's
`CompleteGraphIncidence.rinv` (`1/(n-1)` at the endpoints, `-1/((n-1)(n-2))` elsewhere).
-/

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFProofs
namespace CompleteGraphRightInverse

open Finset Matrix Module SimpleGraph

variable {n : ℕ}

/-- The all-ones matrix `J`. -/
def J (n : ℕ) : Matrix (Fin n) (Fin n) ℚ := Matrix.of fun _ _ => 1

theorem J_mul_J : J n * J n = (n : ℚ) • J n := by
  ext i j; simp [J, Matrix.mul_apply]

/-- `M Mᵀ = (n-2) I + J` (signless Laplacian of `K_n`). -/
theorem incMatrix_mul_transpose_top (hn : 2 ≤ n) :
    (⊤ : SimpleGraph (Fin n)).incMatrix ℚ * ((⊤ : SimpleGraph (Fin n)).incMatrix ℚ)ᵀ =
      ((n : ℚ) - 2) • (1 : Matrix (Fin n) (Fin n) ℚ) + J n := by
  rw [incMatrix_mul_transpose]
  ext i j
  by_cases h : i = j
  · subst h
    simp [J, complete_graph_degree, Nat.cast_sub (by omega : 1 ≤ n)]
    ring
  · simp [J, h]

/-- `Q⁻¹ = (1/(n-2)) (I - J/(2(n-1)))`. -/
def Qinv (n : ℕ) : Matrix (Fin n) (Fin n) ℚ :=
  (1 / ((n : ℚ) - 2)) • ((1 : Matrix (Fin n) (Fin n) ℚ) - (1 / (2 * ((n : ℚ) - 1))) • J n)

theorem Q_mul_Qinv (hn : 3 ≤ n) :
    (((n : ℚ) - 2) • (1 : Matrix (Fin n) (Fin n) ℚ) + J n) * Qinv n = 1 := by
  have h2 : (n : ℚ) - 2 ≠ 0 := by
    have : (3 : ℚ) ≤ n := by exact_mod_cast hn
    linarith
  have h1 : (n : ℚ) - 1 ≠ 0 := by
    have : (3 : ℚ) ≤ n := by exact_mod_cast hn
    linarith
  unfold Qinv
  simp only [Matrix.mul_smul, Matrix.add_mul, Matrix.mul_sub, Matrix.smul_mul, Matrix.one_mul,
    Matrix.mul_one, J_mul_J]
  ext i j
  by_cases h : i = j
  · subst h
    simp [J]
    field_simp
    ring
  · simp [J, h]
    field_simp
    ring_nf
    simp

/-- The right inverse `rinv = Mᵀ Q⁻¹`, rows indexed by `Sym2 (Fin n)`. -/
def rinv (n : ℕ) : Matrix (Sym2 (Fin n)) (Fin n) ℚ :=
  ((⊤ : SimpleGraph (Fin n)).incMatrix ℚ)ᵀ * Qinv n

/-- **`M · rinv = I`** for every `n ≥ 3`. -/
theorem incMatrix_mul_rinv (hn : 3 ≤ n) :
    (⊤ : SimpleGraph (Fin n)).incMatrix ℚ * rinv n = 1 := by
  rw [rinv, ← Matrix.mul_assoc, incMatrix_mul_transpose_top (by omega), Q_mul_Qinv hn]

/-- Entries of `rinv` on an edge `s(a, b)` agree with the repository's hand formula:
`1/(n-1)` at the endpoints and `-1/((n-1)(n-2))` elsewhere. -/
theorem rinv_apply_of_ne (hn : 3 ≤ n) {a b : Fin n} (hab : a ≠ b) (j : Fin n) :
    rinv n s(a, b) j =
      if j = a ∨ j = b then 1 / ((n : ℚ) - 1) else -1 / (((n : ℚ) - 1) * ((n : ℚ) - 2)) := by
  have hadj : (⊤ : SimpleGraph (Fin n)).Adj a b := (top_adj a b).mpr hab
  have hcol : rinv n s(a, b) j = Qinv n a j + Qinv n b j := by
    have := IncMatrixRank.vecMul_incMatrix_mk_of_adj (K := ℚ) (⊤ : SimpleGraph (Fin n))
      (fun k => Qinv n k j) hadj
    rw [← this]
    simp [rinv, Matrix.mul_apply, vecMul, dotProduct, mul_comm]
  have h2 : (n : ℚ) - 2 ≠ 0 := by
    have : (3 : ℚ) ≤ n := by exact_mod_cast hn
    linarith
  have h1 : (n : ℚ) - 1 ≠ 0 := by
    have : (3 : ℚ) ≤ n := by exact_mod_cast hn
    linarith
  rw [hcol]
  by_cases ha : j = a
  · subst ha
    simp [Qinv, J, hab, Ne.symm hab]
    field_simp
    ring
  by_cases hb : j = b
  · subst hb
    simp [Qinv, J, ha, Ne.symm ha]
    field_simp
    ring
  simp [Qinv, J, ha, hb, Ne.symm ha, Ne.symm hb]
  field_simp
  ring

end CompleteGraphRightInverse
end AIEFProofs
