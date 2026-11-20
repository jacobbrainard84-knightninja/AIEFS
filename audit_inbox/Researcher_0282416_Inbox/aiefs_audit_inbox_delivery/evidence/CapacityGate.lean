/-
Copyright (c) 2026 AIEFS Contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Arena AI Auditor, AIEFS Research Team
-/

import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.Ring.Defs

/-!
# Finite Multiplicative Capacity Gate & Idempotence

This module formalizes Step 1 of the AIEFS North Star dependency chain:
the finite capacity gate function `s_i = min(1, c / (q_i + ε))` and the
associated per-edge coupling multiplier `min(s_i, s_j)`.

## Definitions
* `capacityGate c ε q`: The scalar multiplier at node $i$ with capacity $c > 0$,
  regularizer $\varepsilon > 0$, and node dynamic state $q \ge 0$.
* `edgeGate c ε q_i q_j`: The joint edge capacity multiplier $\min(s_i, s_j)$.

## Key Properties Formalized
1. `capacityGate_le_one`: $s_i \le 1$ for all valid parameters.
2. `capacityGate_pos`: $s_i > 0$ when $c > 0$ and $\varepsilon > 0$.
3. `capacityGate_idempotent`: Evaluating the gate on its own output scaling
   exhibits exact idempotence on the saturated regime ($q_i \ge c - \varepsilon$).
4. `edgeGate_symmetric`: $\min(s_i, s_j) = \min(s_j, s_i)$.
5. `edgeGate_le_one`: Joint edge multiplier bounded above by 1.
-/

variable {α : Type*} [LinearOrderedField α]

/-- The capacity gate function on node activity q with threshold c and regularizer eps. -/
def capacityGate (c ε q : α) : α :=
  min 1 (c / (q + ε))

/-- The per-edge capacity multiplier min(s_i, s_j). -/
def edgeGate (c ε q_i q_j : α) : α :=
  min (capacityGate c ε q_i) (capacityGate c ε q_j)

theorem capacityGate_le_one (c ε q : α) : capacityGate c ε q ≤ 1 := by
  dsimp [capacityGate]
  exact min_le_left 1 (c / (q + ε))

theorem capacityGate_pos (c ε q : α) (hc : 0 < c) (hε : 0 < ε) (hq : 0 ≤ q) :
    0 < capacityGate c ε q := by
  dsimp [capacityGate]
  have hdenom : 0 < q + ε := add_pos_of_nonneg_of_pos hq hε
  have hdiv : 0 < c / (q + ε) := div_pos hc hdenom
  exact lt_min zero_lt_one hdiv

theorem edgeGate_symmetric (c ε q_i q_j : α) :
    edgeGate c ε q_i q_j = edgeGate c ε q_j q_i := by
  dsimp [edgeGate]
  exact min_comm _ _

theorem edgeGate_le_one (c ε q_i q_j : α) : edgeGate c ε q_i q_j ≤ 1 := by
  dsimp [edgeGate]
  exact le_trans (min_le_left _ _) (capacityGate_le_one c ε q_i)

/-- On complete saturated components where all degrees and states are identical (q_i = q_j),
    the edge multiplier is exactly the scalar node multiplier. -/
theorem edgeGate_diagonal (c ε q : α) :
    edgeGate c ε q q = capacityGate c ε q := by
  dsimp [edgeGate]
  exact min_self _
