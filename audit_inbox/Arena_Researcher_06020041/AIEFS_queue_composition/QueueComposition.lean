import AIEFGateCore.MatrixPhaseBridge
import AIEFGateCore.ReachableQueue

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
end AIEFGate.QueueComposition
