/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFProofs.ControllerFiberProjector

/-!
# Controller-fiber quotient (exceptional K3 matrix `CCtrl`)

Purely algebraic statements about the fixed 2×3 matrix `CCtrl` and the Euclidean
projectors `PPar`, `PPerp` of `ControllerFiberProjector`. For `x y : ℚ^3` the following are
equivalent:

1. `CCtrl x = CCtrl y` (the two controller rows see the same row sums);
2. `x - y = a • vCtrl` for some `a : ℚ`;
3. `PPerp x = PPerp y`;
4. `PPar (x - y) = x - y`.

Nothing here concerns the AIEF dynamics: this does not prove that Engine v1 emits `CCtrl`,
that the controller branch persists, or that any dynamical operator leaves the fiber invariant.
-/

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFProofs
namespace ControllerFiber

open Matrix

/-- `PPerp` is additive on differences. -/
lemma PPerp_mulVec_sub (x y : Fin 3 → ℚ) :
    PPerp *ᵥ (x - y) = PPerp *ᵥ x - PPerp *ᵥ y :=
  Matrix.mulVec_sub PPerp x y

/-- (1) ↔ (2): equal controller images iff the difference lies on the fiber line. -/
theorem CCtrl_eq_iff_exists_smul (x y : Fin 3 → ℚ) :
    CCtrl *ᵥ x = CCtrl *ᵥ y ↔ ∃ a : ℚ, x - y = a • vCtrl := by
  rw [← CCtrl_mulVec_eq_zero_iff_exists_smul, Matrix.mulVec_sub, sub_eq_zero]

/-- (1) ↔ (3): equal controller images iff equal Euclidean transverse parts. -/
theorem CCtrl_eq_iff_PPerp_eq (x y : Fin 3 → ℚ) :
    CCtrl *ᵥ x = CCtrl *ᵥ y ↔ PPerp *ᵥ x = PPerp *ᵥ y := by
  constructor
  · intro h
    rw [PPerp_eq_SPerp_CCtrl, PPerp_eq_SPerp_CCtrl, h]
  · intro h
    rw [← CCtrl_mulVec_PPerp x, ← CCtrl_mulVec_PPerp y, h]

/-- (3) ↔ (4): equal transverse parts iff the difference is fixed by `PPar`. -/
theorem PPerp_eq_iff_PPar_sub (x y : Fin 3 → ℚ) :
    PPerp *ᵥ x = PPerp *ᵥ y ↔ PPar *ᵥ (x - y) = x - y := by
  rw [← sub_eq_zero, ← PPerp_mulVec_sub, PPerp_mulVec]
  constructor
  · intro h
    funext i
    have hi := congrFun h i
    simp only [Pi.zero_apply] at hi
    linarith
  · intro h
    funext i
    simp [h]

/-- The four-way characterisation of the controller fiber, as one statement. -/
theorem controller_fiber_tfae (x y : Fin 3 → ℚ) :
    (CCtrl *ᵥ x = CCtrl *ᵥ y ↔ ∃ a : ℚ, x - y = a • vCtrl) ∧
    (CCtrl *ᵥ x = CCtrl *ᵥ y ↔ PPerp *ᵥ x = PPerp *ᵥ y) ∧
    (CCtrl *ᵥ x = CCtrl *ᵥ y ↔ PPar *ᵥ (x - y) = x - y) :=
  ⟨CCtrl_eq_iff_exists_smul x y, CCtrl_eq_iff_PPerp_eq x y,
    (CCtrl_eq_iff_PPerp_eq x y).trans (PPerp_eq_iff_PPar_sub x y)⟩

end ControllerFiber
end AIEFProofs
