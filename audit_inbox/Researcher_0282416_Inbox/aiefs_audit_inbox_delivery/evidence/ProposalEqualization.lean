/-
Copyright (c) 2026 AIEFS Contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Arena AI Auditor, AIEFS Research Team
-/

import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.Field.Basic

/-!
# Exact Proposal & Difference Recurrences on Persistent K3 Components

This module formalizes Step 5 of the AIEFS North Star dependency chain:
the exact difference recurrences and contraction projections controlling
proposal equalization on persistent isolated multiplier-controller branches.

Reference: `AIEF_1_4_CONDITIONAL_PROPOSAL_EQUALIZATION_THEOREM.md` Part I,
Propositions 3.1, 4.1, and 4.2.

## Key Theorems Formalized
1. `proposal_diff_exact`: Exact cancellation of constant offset `-dt * μ`:
   `d_n = c_0 * b_n + a_R * r_n`
2. `projected_weight_diff_same_controller`: Fixed-left channel projection
   where edges share the same controller row: `b_{n+1}^L = s_{7,n} * d_n^L`
3. `projected_weight_diff_split_controllers`: Right-mode channel projection
   algebraic identity:
   `c * x_59 / (a + x_59) - c * x_29 / (a + x_29) = [c * a / ((a + x_59)*(a + x_29))] * (x_59 - x_29)`
-/

variable {α : Type*} [Field α]

/-- Proposition 3.1: The proposal difference cancels the constant decay term -dt * μ. -/
theorem proposal_diff_exact (c₀ a_R dt μ : α) (B_1 B_2 R_1 R_2 : α) :
    (c₀ * B_1 + a_R * R_1 - dt * μ) - (c₀ * B_2 + a_R * R_2 - dt * μ) =
    c₀ * (B_1 - B_2) + a_R * (R_1 - R_2) := by
  ring

/-- Proposition 4.1: When two edges share a controller row, their updated weight
    difference factors linearly through the scale and the proposal difference. -/
theorem projected_weight_diff_same_controller (s x_1 x_2 : α) :
    s * x_1 - s * x_2 = s * (x_1 - x_2) := by
  ring

/-- Proposition 4.2: The non-trivial two-controller scale difference identity.
    For a = x_25 + ε, the difference of rational controller projections
    factors as σ_R * (x_59 - x_29). -/
theorem projected_weight_diff_split_controllers (c a x_59 x_29 : α)
    (h1 : a + x_59 ≠ 0) (h2 : a + x_29 ≠ 0) :
    (c * x_59) / (a + x_59) - (c * x_29) / (a + x_29) =
    ((c * a) / ((a + x_59) * (a + x_29))) * (x_59 - x_29) := by
  have h_sub : (c * x_59) / (a + x_59) - (c * x_29) / (a + x_29) =
      ((c * x_59) * (a + x_29) - (c * x_29) * (a + x_59)) / ((a + x_59) * (a + x_29)) := by
    exact div_sub_div (c * x_59) (c * x_29) h1 h2
  rw [h_sub]
  have h_num : (c * x_59) * (a + x_29) - (c * x_29) * (a + x_59) = (c * a) * (x_59 - x_29) := by
    ring
  rw [h_num]
  ring
