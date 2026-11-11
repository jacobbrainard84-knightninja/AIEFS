/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0

/-!
# (P5) Constant-prehistory delay queue, restated inside `AIEFGateCore`

Statements and proofs of `HistoryBuffer.lean` of cycle 010 (and the identical copy in cycle 011)
of Researcher 040282 (handle only;
`audit_inbox/2026-11-08_researcher-040282/researcher_040282/cycle_010/proposal/HistoryBuffer.lean`
on branch `audit-inbox`, commit `1b5ae52`, md5 `fe47db36…`), moved into this project's namespace
`AIEFGate.History`. Nothing is imported from the deposit. Audited by Auditor Seat 002 (3 theorems,
standard axioms, statements honest). Differences from the source: namespace and docstrings only
(`research/lean_gate/tests/test_lean_gate_p5.py` checks the three statements textually against the
deposit text recorded there).

A queue of `D + 1` snapshots with constant prehistory (`x 0` before time 0): slot `i` at read
time `n` holds
`x (n + i - D)` (natural subtraction). The oldest slot is `x (n - D)`, the newest `x n`.

Scope: pure value/index statements, independent of how the appended trace is generated. Nothing
is claimed about Python aliasing (`aief_experiment_engine_v1.py` history buffer), floating
trigonometry or phase locking.
-/

set_option autoImplicit false

universe u

namespace AIEFGate
namespace History

abbrev Hist (d : Nat) (A : Type u) := Fin (d + 1) → A

def shiftAppend {A : Type u} (d : Nat) (h : Hist d A) (fresh : A) : Hist d A :=
  fun i => if hi : i.val < d then h ⟨i.val + 1, Nat.succ_lt_succ hi⟩ else fresh

def historyTrace {A : Type u} (d : Nat) (x : Nat → A) : Nat → Hist d A
  | 0 => fun _ => x 0
  | n + 1 => shiftAppend d (historyTrace d x n) (x (n + 1))

/-- Every queue position, including startup with constant prehistory. -/
theorem historyTrace_index {A : Type u} (d : Nat) (x : Nat → A) :
    ∀ n (i : Fin (d + 1)), historyTrace d x n i = x (n + i.val - d) := by
  intro n
  induction n with
  | zero =>
      intro i
      have hzero : 0 + i.val - d = 0 := by omega
      simp only [historyTrace, hzero]
  | succ n ih =>
      intro i
      simp only [historyTrace, shiftAppend]
      split
      · rename_i hi
        rw [ih]
        congr 1
        change n + (i.val + 1) - d = n + 1 + i.val - d
        omega
      · rename_i hi
        have heq : i.val = d := by omega
        congr 1
        omega

/-- At read time n the oldest phase is n-D, not n-(D+1) or n-D+1. -/
theorem historyTrace_oldest {A : Type u} (d : Nat) (x : Nat → A) (n : Nat) :
    historyTrace d x n ⟨0, Nat.zero_lt_succ d⟩ = x (n - d) := by
  simpa only [Nat.add_zero] using historyTrace_index d x n ⟨0, Nat.zero_lt_succ d⟩

/-- The newest snapshot agrees with the current appended trace value. -/
theorem historyTrace_newest {A : Type u} (d : Nat) (x : Nat → A) (n : Nat) :
    historyTrace d x n ⟨d, Nat.lt_succ_self d⟩ = x n := by
  simpa only [Nat.add_sub_cancel] using historyTrace_index d x n ⟨d, Nat.lt_succ_self d⟩

end History
end AIEFGate
