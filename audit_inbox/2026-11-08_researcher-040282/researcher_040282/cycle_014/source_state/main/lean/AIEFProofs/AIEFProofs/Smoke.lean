/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring

/-!
# Smoke test

Two `ring` examples over `ℝ` that check the Mathlib dependency and the `ring` tactic are wired up.
They prove nothing about AIEF. `Mathlib.Data.Real.Basic` supplies `ℝ` and its commutative-ring
instance, and `Mathlib.Tactic.Ring` supplies `ring`. Importing all of `Mathlib` is not needed.
-/

set_option autoImplicit false

namespace AIEFProofs

example (x y : ℝ) : x + y = y + x := by
  ring

example (x : ℝ) : x - x = 0 := by
  ring

end AIEFProofs
