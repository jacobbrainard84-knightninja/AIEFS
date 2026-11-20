/- SPDX-License-Identifier: Apache-2.0
Research candidate: an abstract exact-real engine-shaped phase/queue step
agrees on Real.Angle with main's phaseStep under explicit assumptions.
No formal Python correspondence or adaptive-weight theorem. -/
import AIEFGateCore.EngineStepRef
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Angle

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.QueueCircleBridge

/-- State stores current phase and a newest-first history. Python stores these
separately in aief_experiment_engine_v1.py, main
8b49f15407ec76c5701476c7caf035ee03e827d2, lines 582–598. Only entries 0..d
are relevant; matching this function to Python's finite list is assumed. -/
structure State (n : ℕ) where
  theta : Fin n → ℝ
  history : ℕ → Fin n → ℝ

/-- Exact-real reduction to [0,2π), modeling np.mod at lines 836–839. -/
noncomputable def wrap (x : ℝ) : ℝ := toIcoMod Real.two_pi_pos 0 x

/-- Phase head with arbitrary post-update weights. This models phase lines
830–839; B is supplied, not computed by the adaptive engine. -/
noncomputable def engineHead (n d : ℕ) (dt omega : ℝ)
    (B : Fin n → Fin n → ℝ) (s : State n) (i : Fin n) : ℝ :=
  s.theta i + dt * (omega + ∑ j : Fin n,
    B i j * Real.sin (s.history d j - s.theta i))

/-- Append new theta and shift previous newest-first history as in lines
841–844, subject to the stated finite-list correspondence. -/
noncomputable def step (n d : ℕ) (dt omega : ℝ)
    (B : Fin n → Fin n → ℝ) (s : State n) : State n :=
  let out := fun i => wrap (engineHead n d dt omega B s i)
  ⟨out, fun k i => if k = 0 then out i else s.history (k - 1) i⟩

/-- Consistency modulo 2π, not a property guaranteed by DynamicState.validate
(lines 613–680); it is preserved by the modeled step. -/
def Consistent (n : ℕ) (s : State n) : Prop :=
  ∀ i, (s.theta i : Real.Angle) = (s.history 0 i : Real.Angle)

/-- Standard initialization fills the entire queue with current theta,
modeling lines 699–713. -/
def initState (n : ℕ) (theta : Fin n → ℝ) : State n :=
  ⟨theta, fun _ => theta⟩

theorem initialize_consistent (n : ℕ) (theta : Fin n → ℝ) :
    Consistent n (initState n theta) := by
  intro i
  rfl

/-- Every abstract step restores/preserves consistency even if the input
is inconsistent; the output newest entry is assigned the output theta. -/
theorem step_consistent (n d : ℕ) (dt omega : ℝ)
    (B : Fin n → Fin n → ℝ) (s : State n) :
    Consistent n (step n d dt omega B s) := by
  intro i
  rfl

/-- Reference input uses theta for coordinate zero and the stored history for
positive coordinates. Input consistency is needed for the first shift. -/
def refInput (n : ℕ) (s : State n) (k : ℕ) (i : Fin n) : ℝ :=
  if k = 0 then s.theta i else s.history k i

/-- Uniform off-diagonal post-update weights and diagonal erasure correspond
to engine lines 795–797 and 823,830–835. This is assumed, not derived. -/
def UniformWeights (n : ℕ) (B : Fin n → Fin n → ℝ) (b : ℝ) : Prop :=
  (∀ i, B i i = 0) ∧ (∀ i j, i ≠ j → B i j = b)

/-- The post-update uniform-weight head equals the main reference head. -/
theorem head_eq_reference (n d : ℕ) (dt omega b : ℝ)
    (B : Fin n → Fin n → ℝ) (s : State n) (hd : 0 < d) (hb : 0 ≤ b)
    (hB : UniformWeights n B b) (i : Fin n) :
    engineHead n d dt omega B s i =
      EngineStepRef.phaseHead n d dt omega b (refInput n s) i := by
  have hsum : (∑ j : Fin n, B i j * Real.sin (s.history d j - s.theta i)) =
      ∑ j ∈ Finset.univ.erase i, b * Real.sin (s.history d j - s.theta i) := by
    have he := Finset.sum_erase_add Finset.univ
      (fun j => B i j * Real.sin (s.history d j - s.theta i)) (Finset.mem_univ i)
    calc
      _ = (∑ j ∈ Finset.univ.erase i,
          B i j * Real.sin (s.history d j - s.theta i)) +
          B i i * Real.sin (s.history d i - s.theta i) := he.symm
      _ = _ := by
        rw [hB.1 i, zero_mul, add_zero]
        apply Finset.sum_congr rfl
        intro j hj
        rw [hB.2 i j (Ne.symm (Finset.mem_erase.mp hj).1)]
  simp only [engineHead, EngineStepRef.phaseHead, refInput, if_true,
    if_neg (Nat.ne_of_gt hd), EngineStepRef.clippedWeight, max_eq_right hb, hsum]

/-- Each retained output history coordinate agrees on the circle with main's
unwrapped phaseStep, assuming input consistency and uniform post-update B. -/
theorem circle_phase_step (n d k : ℕ) (dt omega b : ℝ)
    (B : Fin n → Fin n → ℝ) (s : State n) (hd : 0 < d) (_hk : k ≤ d)
    (hb : 0 ≤ b) (hB : UniformWeights n B b) (hc : Consistent n s) (i : Fin n) :
    ((step n d dt omega B s).history k i : Real.Angle) =
      (EngineStepRef.phaseStep n d dt omega b (refInput n s) k i : Real.Angle) := by
  by_cases hk : k = 0
  · subst k
    simp only [step, if_true, wrap, Real.Angle.coe_toIcoMod, EngineStepRef.phaseStep]
    rw [head_eq_reference n d dt omega b B s hd hb hB i]
  · by_cases h1 : k = 1
    · subst k
      simp only [step, if_false, one_ne_zero, Nat.sub_self, EngineStepRef.phaseStep,
        refInput, if_true]
      exact (hc i).symm
    · have hsub : k - 1 ≠ 0 := by omega
      simp [step, EngineStepRef.phaseStep, refInput, hk, hsub]

#print axioms initialize_consistent
#print axioms step_consistent
#print axioms head_eq_reference
#print axioms circle_phase_step

end AIEFGate.QueueCircleBridge
