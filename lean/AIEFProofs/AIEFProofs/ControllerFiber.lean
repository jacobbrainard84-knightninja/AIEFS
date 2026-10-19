/-
Copyright (c) 2026 AIEF Proofs. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Data.Matrix.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Linarith

/-!
# Controller-fiber kernel

This file formalizes only the exact 2×3 controller-incidence identity used
for the exceptional K3 fiber.

It does not formalize delay, EMA, admissibility, winner-map persistence,
synchronization, Engine v1 emission of this matrix, or any dynamical
dimension claim.

Scientific mapping of edges
`((2,7), (2,11), (7,11))` to columns, and of controller nodes `{2,7}` to
rows, remains an external audit correspondence.
-/

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFProofs
namespace ControllerFiber

open Matrix Finset

/-- Unsigned incidence of controller nodes `{2,7}` on ordered K3 edges
`((2,7), (2,11), (7,11))`. -/
def CCtrl : Matrix (Fin 2) (Fin 3) ℚ
  | 0, 0 => 1
  | 0, 1 => 1
  | 0, 2 => 0
  | 1, 0 => 1
  | 1, 1 => 0
  | 1, 2 => 1

/-- Canonical unnormalized generator of `ker CCtrl`. -/
def vCtrl : Fin 3 → ℚ
  | 0 => 1
  | 1 => -1
  | 2 => -1

@[simp] lemma CCtrl_00 : CCtrl 0 0 = 1 := rfl
@[simp] lemma CCtrl_01 : CCtrl 0 1 = 1 := rfl
@[simp] lemma CCtrl_02 : CCtrl 0 2 = 0 := rfl
@[simp] lemma CCtrl_10 : CCtrl 1 0 = 1 := rfl
@[simp] lemma CCtrl_11 : CCtrl 1 1 = 0 := rfl
@[simp] lemma CCtrl_12 : CCtrl 1 2 = 1 := rfl

@[simp] lemma vCtrl_zero : vCtrl 0 = 1 := rfl
@[simp] lemma vCtrl_one : vCtrl 1 = -1 := rfl
@[simp] lemma vCtrl_two : vCtrl 2 = -1 := rfl

/-- Explicit expansion of a sum over `Fin 3`. -/
lemma univ_fin3 : (univ : Finset (Fin 3)) = {0, 1, 2} := by
  ext i
  constructor
  · intro
    fin_cases i <;> simp
  · intro
    exact mem_univ i

lemma sum_fin3 (f : Fin 3 → ℚ) : ∑ i, f i = f 0 + f 1 + f 2 := by
  rw [univ_fin3, sum_insert, sum_insert, sum_singleton]
  · ring
  · decide
  · decide

/-- Evaluation of the first controller row. -/
@[simp]
lemma CCtrl_mulVec_apply_zero (x : Fin 3 → ℚ) :
    (CCtrl *ᵥ x) 0 = x 0 + x 1 := by
  simp [Matrix.mulVec, dotProduct, sum_fin3]

/-- Evaluation of the second controller row. -/
@[simp]
lemma CCtrl_mulVec_apply_one (x : Fin 3 → ℚ) :
    (CCtrl *ᵥ x) 1 = x 0 + x 2 := by
  simp [Matrix.mulVec, dotProduct, sum_fin3]

/-- The controller matrix annihilates the canonical fiber generator. -/
theorem CCtrl_mulVec_vCtrl : CCtrl *ᵥ vCtrl = 0 := by
  funext i
  fin_cases i <;> simp

/-- Coordinate form of the controller-kernel equation. -/
theorem CCtrl_mulVec_eq_zero_iff (x : Fin 3 → ℚ) :
    CCtrl *ᵥ x = 0 ↔ x 0 + x 1 = 0 ∧ x 0 + x 2 = 0 := by
  constructor
  · intro h
    constructor
    · have h0 := congrFun h (0 : Fin 2)
      simpa using h0
    · have h1 := congrFun h (1 : Fin 2)
      simpa using h1
  · rintro ⟨h01, h02⟩
    funext i
    fin_cases i
    · simpa using h01
    · simpa using h02

/-- Locked-ratio form of the two controller equations. -/
theorem CCtrl_coords_iff (x : Fin 3 → ℚ) :
    x 0 + x 1 = 0 ∧ x 0 + x 2 = 0 ↔
      x 1 = -x 0 ∧ x 2 = -x 0 := by
  constructor
  · intro ⟨h01, h02⟩
    constructor <;> linarith
  · intro ⟨h1, h2⟩
    constructor <;> linarith

/-- Explicit fiber coordinate form. -/
theorem CCtrl_eq_zero_iff_locked_ratio (x : Fin 3 → ℚ) :
    CCtrl *ᵥ x = 0 ↔ x 1 = -x 0 ∧ x 2 = -x 0 := by
  rw [CCtrl_mulVec_eq_zero_iff, CCtrl_coords_iff]

/-- Every kernel vector is a scalar multiple of `vCtrl`. -/
theorem CCtrl_mulVec_eq_zero_iff_exists_smul (x : Fin 3 → ℚ) :
    CCtrl *ᵥ x = 0 ↔ ∃ a : ℚ, x = a • vCtrl := by
  constructor
  · intro hx
    rcases (CCtrl_mulVec_eq_zero_iff x).mp hx with ⟨h01, h02⟩
    refine ⟨x 0, ?_⟩
    funext i
    fin_cases i
    · simp
    · simp
      linarith
    · simp
      linarith
  · rintro ⟨a, rfl⟩
    apply (CCtrl_mulVec_eq_zero_iff (a • vCtrl)).2
    constructor <;> simp

theorem vCtrl_ne_zero : vCtrl ≠ 0 := by
  intro h
  have h0 := congrFun h (0 : Fin 3)
  simp at h0

end ControllerFiber
end AIEFProofs
