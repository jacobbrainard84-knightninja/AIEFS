/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.MatrixPhaseBridge
import AIEFGateCore.ReachableQueue

/-!
# Finite queue composed with the matrix bridge (Arena D8)

Research candidate. Views the finite `ReachableQueue` state as the newest-first
`MatrixPhaseBridge` state, transfers consistency, and shows that from a constant initial queue
every fixed-`W` iterate agrees with the matrix reference on every retained circle coordinate.
Value probes and a `false_*` witness are appended (SPEC §17).

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D8, deposit sha256 `7a1b1b00…`; proofs and
statements unchanged from the deposit.
-/

set_option autoImplicit false
namespace AIEFGate.QueueComposition

open MatrixPhaseBridge ReachableQueue

/-- Finite oldest-first queue viewed as the earlier newest-first abstract state.
The arbitrary zero tail is never observed in retained slots. -/
def abstractState (n d : ℕ) (s : ReachableQueue.State n d) : MatrixPhaseBridge.State n :=
  ⟨s.theta, fun k i => if h : k ≤ d then ReachableQueue.view n d s ⟨k, by omega⟩ i else 0⟩

/-- Translate the finite queue invariant to the exact hypothesis used by the bridge. -/
theorem consistent_transfer (n d : ℕ) (s : ReachableQueue.State n d)
    (h : ReachableQueue.Consistent n d s) :
    MatrixPhaseBridge.Consistent n (abstractState n d s) := by
  intro i
  simpa [abstractState] using h i

/-- Standard initial history contains d+1 copies of the initial theta. -/
def initState (n d : ℕ) (theta : Fin n → ℝ) : ReachableQueue.State n d :=
  ⟨theta, fun _ i => theta i⟩

theorem initialized_consistent (n d : ℕ) (theta : Fin n → ℝ) :
    ReachableQueue.Consistent n d (initState n d theta) := by
  intro i
  simp [ReachableQueue.view, initState]

/-- The finite and unbounded models agree on retained queue slots after one step. -/
theorem finite_abstract_step (n d k : ℕ) (dt omega : ℝ)
    (W : Fin n → Fin n → ℝ) (s : ReachableQueue.State n d) (hk : k ≤ d)
    (i : Fin n) :
    ReachableQueue.view n d (ReachableQueue.step n d dt omega W s) ⟨k, by omega⟩ i =
      (MatrixPhaseBridge.engineStep n d dt omega W (abstractState n d s)).history k i := by
  by_cases h0 : k = 0
  · subst k
    simp [ReachableQueue.step, ReachableQueue.shift, ReachableQueue.view,
      ReachableQueue.reverseIndex, ReachableQueue.head, MatrixPhaseBridge.engineStep,
      MatrixPhaseBridge.wrap, abstractState]
  · have hp : 0 < (⟨k, by omega⟩ : Fin (d+1)).val := by simp; omega
    have hs := ReachableQueue.view_shift n d s
      (fun i => toIcoMod Real.two_pi_pos 0 (ReachableQueue.head n d dt omega W s i))
      ⟨k, by omega⟩ hp i
    have hk1 : k - 1 ≤ d := by omega
    have hkd : k ≤ d + 1 := by omega
    simpa [ReachableQueue.step, MatrixPhaseBridge.engineStep, abstractState, h0, hk1, hkd] using hs

/-- Starting with a constant finite queue, every fixed-W iterate satisfies the
old bridge hypothesis and the following step agrees with the matrix reference
on every retained circle coordinate. -/
theorem initialized_trajectory_bridge (n d k t : ℕ) (dt omega : ℝ)
    (W : Fin n → Fin n → ℝ) (theta : Fin n → ℝ) (hd : 0 < d) (hk : k ≤ d)
    (i : Fin n) :
    let s := ReachableQueue.iterate n d
      (fun x => (ReachableQueue.step n d dt omega W x).theta) t (initState n d theta)
    MatrixPhaseBridge.Consistent n (abstractState n d s) ∧
      (ReachableQueue.view n d (ReachableQueue.step n d dt omega W s)
        ⟨k, by omega⟩ i : Real.Angle) =
      (MatrixPhaseBridge.matrixStep n d dt omega W
        (MatrixPhaseBridge.refInput n (abstractState n d s)) k i : Real.Angle) := by
  dsimp only
  let s := ReachableQueue.iterate n d
    (fun x => (ReachableQueue.step n d dt omega W x).theta) t (initState n d theta)
  have hc : ReachableQueue.Consistent n d s :=
    ReachableQueue.reachable_consistent n d _ _ (initialized_consistent n d theta) t
  have hc' := consistent_transfer n d s hc
  constructor
  · exact hc'
  · rw [finite_abstract_step n d k dt omega W s hk i]
    exact MatrixPhaseBridge.matrix_circle_bridge n d k dt omega W (abstractState n d s) hd hk hc' i

#print axioms finite_abstract_step
#print axioms initialized_trajectory_bridge

/-! ### Value probes and a negation used by the mutation harness (SPEC §17) -/

/-- The abstract view is newest-first: lag 0 is the newest finite slot `1`, the unobserved tail
`0`. -/
theorem probe_abstractState_values :
    (abstractState 1 1 ReachableQueue.probeState).history 0 0 = 1 ∧
      (abstractState 1 1 ReachableQueue.probeState).history 1 0 = 0 := by
  constructor <;> simp [abstractState, ReachableQueue.view, ReachableQueue.reverseIndex,
    ReachableQueue.probeState]

/-- The initial queue holds `d + 1` copies of the initial phase. -/
theorem probe_initState_values :
    (initState 1 1 (fun _ => 2)).history 1 0 = 2 ∧ (initState 1 1 (fun _ => 2)).theta 0 = 2 := by
  constructor <;> simp [initState]

/-- Dropping the queue invariant from `consistent_transfer` is false (`ReachableQueue.bad`). -/
theorem false_transfer_no_consistent :
    ¬ (∀ (n d : ℕ) (s : ReachableQueue.State n d) (_h : True),
      MatrixPhaseBridge.Consistent n (abstractState n d s)) := by
  intro H
  have h := H 1 1 ReachableQueue.bad trivial 0
  simp only [abstractState, ReachableQueue.view, ReachableQueue.reverseIndex,
    ReachableQueue.bad] at h
  exact Real.Angle.pi_ne_zero (by simpa using h.symm)

/-- `finite_abstract_step` reading slot `0` of the unbounded step instead of slot `k` is false
(`probeState`, `dt = 0`, `k = 1`: the retained lag-1 value `1` against the new head `0`). Audit
note N5. -/
theorem false_finite_step_head_slot :
    ¬ (∀ (n d k : ℕ) (dt omega : ℝ) (W : Fin n → Fin n → ℝ) (s : ReachableQueue.State n d)
      (hk : k ≤ d) (i : Fin n),
      ReachableQueue.view n d (ReachableQueue.step n d dt omega W s) ⟨k, by omega⟩ i =
        (MatrixPhaseBridge.engineStep n d dt omega W (abstractState n d s)).history 0 i) := by
  intro H
  have h := H 1 1 1 0 0 (fun _ _ => 0) ReachableQueue.probeState le_rfl 0
  simp [ReachableQueue.view, ReachableQueue.step, ReachableQueue.shift, ReachableQueue.reverseIndex,
    ReachableQueue.head, ReachableQueue.probeState, MatrixPhaseBridge.engineStep,
    MatrixPhaseBridge.wrap, abstractState, toIcoMod_apply_left] at h

#print axioms false_finite_step_head_slot
#print axioms probe_abstractState_values
#print axioms probe_initState_values
#print axioms false_transfer_no_consistent
-- deposit theorems that had no `#print axioms` line in the deposit:
#print axioms consistent_transfer
#print axioms initialized_consistent

end AIEFGate.QueueComposition
