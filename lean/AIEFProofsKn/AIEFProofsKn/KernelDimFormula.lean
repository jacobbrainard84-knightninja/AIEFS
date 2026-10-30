/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFProofsKn.CompleteGraphKn

/-!
# `C(n,2) − n = n(n−3)/2` (natural-number arithmetic), and the `n(n−3)/2` form of `dim ker`

Added 2026-10-29 by the AIEFS merge-prep agent (review r026), **not by Researcher 001**; for
Researcher 001 / an auditor to check. The `LEAN-KN-01` ledger statement writes
`dim ker = C(n,2) − n = n(n-3)/2`; `finrank_ker_inc_eq_choose` proves only the `C(n,2) − n` form.
This file proves the arithmetic step in `ℕ` (truncated subtraction, floor division):

* `two_mul_choose_two_sub`: `2 * (C(n,2) − n) = n * (n − 3)` for `n ≥ 3` (no division);
* `choose_two_sub_eq`: `C(n,2) − n = n * (n − 3) / 2` for `n ≥ 3` (the division is exact,
  because `n * (n − 3)` is even);
* `finrank_ker_inc_eq_half`: `dim ker (inc src dst) = n * (n − 3) / 2`.

For `n < 3` the `ℕ` identity can fail or be vacuous (`n = 2`: `C(2,2) − 2 = 0` and
`2 * (2 − 3) / 2 = 0`; `n = 1`, `n = 0` likewise give 0); the theorems assume `3 ≤ n`, as
`finrank_ker_inc_eq_choose` does. Pure arithmetic; nothing about the dynamics.
-/

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFProofs
namespace CompleteGraphKn

open Module
open AIEFProofs.CompleteGraphIncidence (inc IsCompleteEdgeList)

/-- `2 * C(n,2) = n * (n − 1)` in `ℕ`. -/
theorem two_mul_choose_two (n : ℕ) : 2 * n.choose 2 = n * (n - 1) := by
  rw [Nat.choose_two_right]
  exact Nat.mul_div_cancel' (Nat.even_mul_pred_self n).two_dvd

/-- `2 * (C(n,2) − n) = n * (n − 3)` for `n ≥ 3`, in `ℕ`. -/
theorem two_mul_choose_two_sub {n : ℕ} (hn : 3 ≤ n) :
    2 * (n.choose 2 - n) = n * (n - 3) := by
  obtain ⟨k, rfl⟩ : ∃ k, n = k + 3 := ⟨n - 3, by omega⟩
  have h := two_mul_choose_two (k + 3)
  have h1 : k + 3 - 1 = k + 2 := by omega
  have h3 : k + 3 - 3 = k := by omega
  rw [h1] at h
  rw [h3, Nat.mul_sub, h]
  have : (k + 3) * (k + 2) = (k + 3) * k + 2 * (k + 3) := by ring
  omega

/-- `C(n,2) − n = n * (n − 3) / 2` for `n ≥ 3`, in `ℕ` (exact division). -/
theorem choose_two_sub_eq {n : ℕ} (hn : 3 ≤ n) :
    n.choose 2 - n = n * (n - 3) / 2 := by
  rw [← two_mul_choose_two_sub hn, Nat.mul_div_cancel_left _ (by norm_num)]

/-- **`n(n−3)/2` form of the main theorem:** for every complete edge list on `n ≥ 3` nodes,
`dim ker (inc src dst) = n * (n − 3) / 2`. -/
theorem finrank_ker_inc_eq_half {m n : ℕ} {src dst : Fin m → Fin n}
    (hc : IsCompleteEdgeList src dst) (hn : 3 ≤ n) :
    finrank ℚ (LinearMap.ker (inc src dst).mulVecLin) = n * (n - 3) / 2 := by
  rw [finrank_ker_inc_eq_choose hc hn, choose_two_sub_eq hn]

/-- Sanity check: `12 * 9 / 2 = 54`, matching `finrank_ker_K12_eq_54`. -/
example : 12 * (12 - 3) / 2 = 54 := by norm_num

end CompleteGraphKn
end AIEFProofs
