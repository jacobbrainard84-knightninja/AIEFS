/-
Copyright (c) 2026 AIEF Proofs. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
import AIEFProofs.ControllerFiber
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Data.Matrix.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Abel

/-!
# Euclidean controller-fiber projector

This file constructs the Euclidean rank-one projector onto
`ker CCtrl = span {vCtrl}` and its complementary projector.

```
PPar  = (1/3) • (vCtrl ⊗ vCtrl)
PPerp = I - PPar
```

These are exact algebraic maps on `ℚ^3`.

They are **not** the implemented AIEF admissibility / capacity projection.
The name used throughout is:

  Euclidean controller-fiber projector

Dynamical invariance of an operator `K` along the fiber still requires
`K ∘ PPar = PPar ∘ K ∘ PPar`, or equivalently vanishing leakage
`PPerp ∘ K ∘ PPar`. That is not proved here.

For the exceptional selected block, exact right invariance of the
implemented map still requires `s_2 = s_7`. The finite replay approaches
that one-sidedly; it is not an identity.
-/

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFProofs
namespace ControllerFiber

open Matrix Finset

/-- Euclidean projector onto `span {vCtrl}`.
Not the implemented AIEF admissibility map. -/
def PPar : Matrix (Fin 3) (Fin 3) ℚ
  | i, j => (1 / 3 : ℚ) * vCtrl i * vCtrl j

/-- Complementary Euclidean projector. -/
def PPerp : Matrix (Fin 3) (Fin 3) ℚ
  | i, j => (if i = j then (1 : ℚ) else 0) - PPar i j

@[simp] lemma PPar_apply (i j : Fin 3) :
    PPar i j = (1 / 3 : ℚ) * vCtrl i * vCtrl j := rfl

lemma vCtrl_dot_vCtrl : ∑ i, vCtrl i * vCtrl i = 3 := by
  rw [sum_fin3]
  simp
  ring

lemma vCtrl_dot_smul (a : ℚ) :
    ∑ i, vCtrl i * (a * vCtrl i) = 3 * a := by
  rw [sum_fin3]
  simp
  ring

/-- `PPar` acts by the scalar `(vCtrl ⬝ x) / 3` along `vCtrl`. -/
lemma PPar_mulVec (x : Fin 3 → ℚ) :
    PPar *ᵥ x = ((1 / 3 : ℚ) * ∑ j, vCtrl j * x j) • vCtrl := by
  funext i
  simp [Matrix.mulVec, dotProduct, sum_fin3, Pi.smul_apply]
  ring

lemma PPar_mulVec_vCtrl : PPar *ᵥ vCtrl = vCtrl := by
  rw [PPar_mulVec, vCtrl_dot_vCtrl]
  funext i
  simp

lemma PPerp_mulVec (x : Fin 3 → ℚ) :
    PPerp *ᵥ x = fun i => x i - (PPar *ᵥ x) i := by
  funext i
  have hx :
      (PPerp *ᵥ x) i
        = ∑ j, ((if i = j then (1 : ℚ) else 0) - PPar i j) * x j := by
    simp [Matrix.mulVec, dotProduct, PPerp, sum_fin3]
  have hsplit :
      ∑ j, ((if i = j then (1 : ℚ) else 0) - PPar i j) * x j
        = ∑ j, (if i = j then (1 : ℚ) else 0) * x j
          - ∑ j, PPar i j * x j := by
    rw [sum_fin3, sum_fin3, sum_fin3]
    ring
  have hid :
      ∑ j, (if i = j then (1 : ℚ) else 0) * x j = x i := by
    rw [sum_fin3]
    fin_cases i <;> simp
  have hP :
      ∑ j, PPar i j * x j = (PPar *ᵥ x) i := by
    simp [Matrix.mulVec, dotProduct, sum_fin3]
  calc
    (PPerp *ᵥ x) i
        = ∑ j, (if i = j then (1 : ℚ) else 0) * x j
          - ∑ j, PPar i j * x j := by
          rw [hx, hsplit]
    _ = x i - (PPar *ᵥ x) i := by
          rw [hid, hP]

/-- Idempotence: `P∥² = P∥` as an action on vectors. -/
theorem PPar_sq_mulVec (x : Fin 3 → ℚ) :
    PPar *ᵥ (PPar *ᵥ x) = PPar *ᵥ x := by
  rw [PPar_mulVec x, PPar_mulVec]
  have hS :
      ∑ j, vCtrl j *
          (((1 / 3 : ℚ) * ∑ k, vCtrl k * x k) * vCtrl j)
        = ∑ k, vCtrl k * x k := by
    rw [vCtrl_dot_smul]
    ring
  funext i
  simp only [Pi.smul_apply, smul_eq_mul, hS]

/-- Orthogonality: `P∥ P⊥ = 0` as an action on vectors. -/
theorem PPar_mulVec_PPerp (x : Fin 3 → ℚ) :
    PPar *ᵥ (PPerp *ᵥ x) = 0 := by
  rw [PPerp_mulVec, PPar_mulVec]
  have hdiff :
      ∑ j, vCtrl j * (x j - (PPar *ᵥ x) j) = 0 := by
    have hPx : PPar *ᵥ x =
        ((1 / 3 : ℚ) * ∑ k, vCtrl k * x k) • vCtrl := PPar_mulVec x
    rw [hPx, sum_fin3]
    simp only [Pi.smul_apply, smul_eq_mul, sum_fin3, vCtrl_zero, vCtrl_one, vCtrl_two]
    ring
  funext i
  simp only [Pi.smul_apply, smul_eq_mul, hdiff]
  simp

/-- Idempotence: `P⊥² = P⊥` as an action on vectors. -/
theorem PPerp_sq_mulVec (x : Fin 3 → ℚ) :
    PPerp *ᵥ (PPerp *ᵥ x) = PPerp *ᵥ x := by
  rw [PPerp_mulVec (PPerp *ᵥ x), PPar_mulVec_PPerp]
  funext i
  simp

/-- Complementary orthogonality: `P⊥ P∥ = 0`. -/
theorem PPerp_mulVec_PPar (x : Fin 3 → ℚ) :
    PPerp *ᵥ (PPar *ᵥ x) = 0 := by
  rw [PPerp_mulVec, PPar_sq_mulVec]
  funext i
  simp

/-- The Euclidean fiber vector is annihilated by `CCtrl`. -/
theorem CCtrl_mulVec_PPar (x : Fin 3 → ℚ) :
    CCtrl *ᵥ (PPar *ᵥ x) = 0 := by
  rw [PPar_mulVec]
  have hx :
      CCtrl *ᵥ (((1 / 3 : ℚ) * ∑ j, vCtrl j * x j) • vCtrl)
        = ((1 / 3 : ℚ) * ∑ j, vCtrl j * x j) • (CCtrl *ᵥ vCtrl) := by
    funext i
    simp [Matrix.mulVec, dotProduct, sum_fin3, Pi.smul_apply]
    ring
  rw [hx, CCtrl_mulVec_vCtrl]
  simp

/-- Range of `PPar` is exactly `ker CCtrl`. -/
theorem range_PPar_iff_ker_CCtrl (x : Fin 3 → ℚ) :
    (∃ y, PPar *ᵥ y = x) ↔ CCtrl *ᵥ x = 0 := by
  constructor
  · rintro ⟨y, hy⟩
    rw [← hy]
    exact CCtrl_mulVec_PPar y
  · intro hx
    refine ⟨x, ?_⟩
    rcases (CCtrl_mulVec_eq_zero_iff_exists_smul x).mp hx with ⟨a, ha⟩
    rw [ha, PPar_mulVec]
    funext i
    simp only [Pi.smul_apply, smul_eq_mul, vCtrl_dot_smul]
    ring

/-- Direct-sum decomposition of the ambient edge space. -/
theorem id_eq_PPar_add_PPerp (x : Fin 3 → ℚ) :
    x = (fun i => (PPar *ᵥ x) i + (PPerp *ᵥ x) i) := by
  funext i
  simp [PPerp_mulVec]

end ControllerFiber
end AIEFProofs
