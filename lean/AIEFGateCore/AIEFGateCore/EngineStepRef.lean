/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 8fc0d24)
-/
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Deriv
import Mathlib.Analysis.Calculus.Deriv.Add
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-!
# Fixed-weight phase reference step and its directional derivative (Arena cycle 21)

Research candidate. An idealized fixed-weight phase step (common clipped weight, no
shuffle, no active projection, unwrapped angles) with its directional derivative at a
prepared rotating history. Not a proof of correspondence with the Python engine, and not
about adaptive dynamics.
-/
set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.EngineStepRef

/-- Mirror off-diagonal clipping in aief_experiment_engine_v1.py at main
    d2a62b7f9e6456ade8591d5f12c9ccdeed185d19, lines 789–797, in
an intentionally restricted model with a prescribed scalar proposal. -/
noncomputable def clippedWeight (b : ℝ) : ℝ := max 0 b

/-- Mirror phase coupling and update in aief_experiment_engine_v1.py at main
    d2a62b7f9e6456ade8591d5f12c9ccdeed185d19, lines 830–839,
with common fixed off-diagonal weight, no shuffle, and no active projection.
Angles are unwrapped real lifts; modulo is not modeled. -/
noncomputable def phaseHead (n : ℕ) (d : ℕ) (dt omega b : ℝ)
    (x : ℕ → Fin n → ℝ) (i : Fin n) : ℝ :=
  x 0 i + dt * (omega + ∑ j ∈ Finset.univ.erase i,
    clippedWeight b * Real.sin (x d j - x 0 i))

/-- Mirror append/drop in aief_experiment_engine_v1.py at main
    d2a62b7f9e6456ade8591d5f12c9ccdeed185d19, lines 841–844; 0 is newest. -/
noncomputable def phaseStep (n d : ℕ) (dt omega b : ℝ)
    (x : ℕ → Fin n → ℝ) (k : ℕ) (i : Fin n) : ℝ :=
  if k = 0 then phaseHead n d dt omega b x i else x (k - 1) i

/-- Affine perturbation of a prepared homogeneous rotating history. -/
def orbitPath (n : ℕ) (dt Omega theta : ℝ) (v : ℕ → Fin n → ℝ)
    (t : ℝ) (k : ℕ) (i : Fin n) : ℝ :=
  theta - (k : ℝ) * dt * Omega + t * v k i

/-- The prepared rotating history advances by +dt*Omega in the unwrapped
    chart. This uses the specified frequency equation; it is an identity for
    the fixed-weight reference, not for the adaptive engine. -/
theorem orbit_invariant (n d k : ℕ) (dt omega b Omega theta : ℝ)
    (hn : 1 ≤ n) (_hk : k ≤ d)
    (horbit : Omega = omega + ((n : ℝ) - 1) * clippedWeight b *
      Real.sin (-((d : ℝ) * dt * Omega)))
    (v : ℕ → Fin n → ℝ) (i : Fin n) :
    phaseStep n d dt omega b (orbitPath n dt Omega theta v 0) k i =
      orbitPath n dt Omega theta v 0 k i + dt * Omega := by
  by_cases hk : k = 0
  · subst k
    have hcard : ((Finset.univ.erase i).card : ℝ) = (n : ℝ) - 1 := by
      simp [Finset.card_erase_of_mem, Nat.cast_sub hn]
    have hd : theta - (d : ℝ) * dt * Omega - theta =
        -((d : ℝ) * dt * Omega) := by ring
    simp only [phaseStep, if_true, phaseHead, orbitPath, Nat.cast_zero, zero_mul,
      sub_zero, add_zero, hd, Finset.sum_const, nsmul_eq_mul, hcard]
    calc
      _ = theta + dt * (omega + ((n : ℝ) - 1) * clippedWeight b *
          Real.sin (-((d : ℝ) * dt * Omega))) := by ring
      _ = theta + dt * Omega := by rw [← horbit]
  · have hkn : 1 ≤ k := Nat.one_le_iff_ne_zero.mpr hk
    simp only [phaseStep, if_neg hk, orbitPath, zero_mul, add_zero, Nat.cast_sub hkn,
      Nat.cast_one]
    ring

/-- Direct directional derivative of one neighbor sine at the synchronized
history. This is a real derivative in t, not a full Fréchet theorem. -/
theorem neighbor_derivative (n d : ℕ) (dt Omega theta : ℝ)
    (v : ℕ → Fin n → ℝ) (i j : Fin n) :
    HasDerivAt (fun t => Real.sin (orbitPath n dt Omega theta v t d j -
      orbitPath n dt Omega theta v t 0 i))
      (Real.cos ((d : ℝ) * dt * Omega) * (v d j - v 0 i)) 0 := by
  have hd : HasDerivAt (fun t : ℝ => orbitPath n dt Omega theta v t d j -
      orbitPath n dt Omega theta v t 0 i) (v d j - v 0 i) 0 := by
    have ht := ((hasDerivAt_const (0 : ℝ) (theta - (d : ℝ) * dt * Omega)).fun_add
      ((hasDerivAt_id (0 : ℝ)).mul_const (v d j))).fun_sub
      ((hasDerivAt_const (0 : ℝ) theta).fun_add
        ((hasDerivAt_id (0 : ℝ)).mul_const (v 0 i)))
    simpa [orbitPath] using ht
  have hs := hd.sin
  have heq : orbitPath n dt Omega theta v 0 d j -
      orbitPath n dt Omega theta v 0 0 i = -((d : ℝ) * dt * Omega) := by
    simp [orbitPath]
  rw [heq, Real.cos_neg] at hs
  exact hs

/-- Directional head derivative, first stated as a sum over neighbors. -/
theorem head_derivative_raw (n d : ℕ) (dt omega b Omega theta : ℝ)
    (v : ℕ → Fin n → ℝ) (i : Fin n) :
    HasDerivAt (fun t => phaseHead n d dt omega b (orbitPath n dt Omega theta v t) i)
      (v 0 i + dt * ∑ j ∈ Finset.univ.erase i,
        clippedWeight b * (Real.cos ((d : ℝ) * dt * Omega) * (v d j - v 0 i))) 0 := by
  have hs : HasDerivAt (fun t => ∑ j ∈ Finset.univ.erase i,
      clippedWeight b * Real.sin (orbitPath n dt Omega theta v t d j -
        orbitPath n dt Omega theta v t 0 i))
      (∑ j ∈ Finset.univ.erase i,
        clippedWeight b * (Real.cos ((d : ℝ) * dt * Omega) * (v d j - v 0 i))) 0 := by
    apply HasDerivAt.fun_sum
    intro j hj
    exact (neighbor_derivative n d dt Omega theta v i j).const_mul (clippedWeight b)
  have hc : HasDerivAt (fun t : ℝ => orbitPath n dt Omega theta v t 0 i) (v 0 i) 0 := by
    have ht := (hasDerivAt_const (0 : ℝ) theta).fun_add
      ((hasDerivAt_id (0 : ℝ)).mul_const (v 0 i))
    simpa [orbitPath] using ht
  have hp := hc.fun_add ((hasDerivAt_const (0 : ℝ) omega).fun_add hs |>.const_mul dt)
  simpa only [phaseHead, zero_add] using hp

/-- In the strictly positive scalar proposal branch, the directional head
matches the no-self complete-graph phase block. -/
theorem head_derivative_block (n d : ℕ) (dt omega b Omega theta : ℝ)
    (hn : 1 ≤ n) (hb : 0 < b) (v : ℕ → Fin n → ℝ) (i : Fin n) :
    HasDerivAt (fun t => phaseHead n d dt omega b (orbitPath n dt Omega theta v t) i)
      ((1 - ((n : ℝ) - 1) * (dt * b * Real.cos ((d : ℝ) * dt * Omega))) * v 0 i +
        (dt * b * Real.cos ((d : ℝ) * dt * Omega)) *
          ((∑ j : Fin n, v d j) - v d i)) 0 := by
  apply (head_derivative_raw n d dt omega b Omega theta v i).congr_deriv
  have hc : clippedWeight b = b := by simp [clippedWeight, max_eq_right (le_of_lt hb)]
  have hcard : ((Finset.univ.erase i).card : ℝ) = (n : ℝ) - 1 := by
    simp [Finset.card_erase_of_mem, Nat.cast_sub hn]
  have hsum : (∑ j ∈ Finset.univ.erase i, v d j) = (∑ j : Fin n, v d j) - v d i := by
    exact eq_sub_of_add_eq (Finset.sum_erase_add Finset.univ (fun j => v d j) (Finset.mem_univ i))
  simp only [hc, ← Finset.mul_sum, Finset.sum_sub_distrib, Finset.sum_const, nsmul_eq_mul,
    hcard, hsum]
  ring

/-- The phase-step head has exactly the proposed block's directional derivative. -/
theorem phase_step_head (n d : ℕ) (dt omega b Omega theta : ℝ)
    (hn : 1 ≤ n) (hb : 0 < b) (v : ℕ → Fin n → ℝ) (i : Fin n) :
    HasDerivAt (fun t => phaseStep n d dt omega b (orbitPath n dt Omega theta v t) 0 i)
      ((1 - ((n : ℝ) - 1) * (dt * b * Real.cos ((d : ℝ) * dt * Omega))) * v 0 i +
        (dt * b * Real.cos ((d : ℝ) * dt * Omega)) *
          ((∑ j : Fin n, v d j) - v d i)) 0 := by
  simpa only [phaseStep, if_true] using head_derivative_block n d dt omega b Omega theta hn hb v i

/-- Directional derivative of every retained history coordinate 1,...,d. -/
theorem history_derivative (n d k : ℕ) (dt omega b Omega theta : ℝ)
    (hk : 0 < k) (v : ℕ → Fin n → ℝ) (i : Fin n) :
    HasDerivAt (fun t => phaseStep n d dt omega b (orbitPath n dt Omega theta v t) k i)
      (v (k - 1) i) 0 := by
  have ht := (hasDerivAt_const (0 : ℝ) (theta - ((k - 1 : ℕ) : ℝ) * dt * Omega)).fun_add
    ((hasDerivAt_id (0 : ℝ)).mul_const (v (k - 1) i))
  simpa [phaseStep, Nat.ne_of_gt hk, orbitPath] using ht

/-- A concrete perturbation only at the other node's delayed phase. -/
def twoNodeDirection (k : ℕ) (i : Fin 2) : ℝ :=
  if k = 1 ∧ i = 1 then 1 else 0

/-- N=2,d=1, dt=1,b=1/2, Omega=0: the other delayed node
contributes exactly 1/2 to the derivative of node zero. -/
theorem two_node_probe :
    HasDerivAt (fun t => phaseHead 2 1 1 0 (1/2) (orbitPath 2 1 0 0 twoNodeDirection t) 0)
      (1/2) 0 := by
  have ht := head_derivative_block 2 1 1 0 (1/2) 0 0 (by norm_num) (by norm_num) twoNodeDirection 0
  norm_num [twoNodeDirection, Fin.sum_univ_two] at ht ⊢
  exact ht

/-- Delayed self-only direction: self coupling must be absent. -/
def selfDelayDirection (k : ℕ) (i : Fin 2) : ℝ :=
  if k = 1 ∧ i = 0 then 1 else 0

/-- A delayed self perturbation has zero effect on the N=2 reference head. -/
theorem self_coupling_probe :
    HasDerivAt (fun t => phaseHead 2 1 1 0 (1/2)
      (orbitPath 2 1 0 0 selfDelayDirection t) 0) 0 0 := by
  simpa [phaseHead, orbitPath, selfDelayDirection, clippedWeight, Fin.sum_univ_two] using
    (hasDerivAt_const (0 : ℝ) (0 : ℝ))

/-- Two adjacent history coordinates carry different perturbations. -/
def unequalHistoryDirection (k : ℕ) (_i : Fin 2) : ℝ :=
  if k = 0 then 3 else 7

/-- At k=1 the shifted history derivative is 3, not the old k=1 value 7. -/
theorem adjacent_history_probe :
    HasDerivAt (fun t => phaseStep 2 1 1 0 (1/2)
      (orbitPath 2 1 0 0 unequalHistoryDirection t) 1 0) 3 0 ∧
      unequalHistoryDirection 1 0 = 7 := by
  constructor
  · have ht := (hasDerivAt_id (0 : ℝ)).mul_const (3 : ℝ)
    simpa [phaseStep, orbitPath, unequalHistoryDirection] using ht
  · norm_num [unequalHistoryDirection]

/-- Under negative scalar proposal, the clipped derivative is zero, while
    the actual proposed unclipped block expression evaluates to minus one. -/
theorem clipping_probe :
    HasDerivAt (fun t => phaseHead 2 1 1 0 (-1) (orbitPath 2 1 0 0 twoNodeDirection t) 0)
      0 0 ∧
    ((1 - ((2 : ℝ) - 1) * (-1)) * twoNodeDirection 0 0 +
      (-1) * ((∑ j : Fin 2, twoNodeDirection 1 j) - twoNodeDirection 1 0)) = -1 := by
  have ht := head_derivative_raw 2 1 1 0 (-1) 0 0 twoNodeDirection 0
  constructor
  · norm_num [clippedWeight, twoNodeDirection, Fin.sum_univ_two] at ht ⊢
    exact ht
  · norm_num [twoNodeDirection, Fin.sum_univ_two]

/-! ### Value probes and negations used by the mutation harness (M114 ff.)

The value probes evaluate the definitions at concrete data straight from their bodies, so a
mutated definition fails here and not only in a derivative lemma. -/

/-- The clip keeps positive weights and zeroes negative ones. -/
theorem probe_clippedWeight_values : clippedWeight (-1) = 0 ∧ clippedWeight (1/2) = 1/2 := by
  constructor <;> norm_num [clippedWeight]

/-- Every node's delayed phase is `π/2`, every current phase is `0`. -/
noncomputable def probeHist (k : ℕ) (_i : Fin 2) : ℝ := if k = 1 then Real.pi / 2 else 0

/-- Head with `dt = 2`, `ω = 1/4`, `b = 1/2`: one delayed neighbor, so `2 * (1/4 + 1/2)`.
Self coupling would add `1`, reading the current phase gives `1/2`, the reversed sine
gives `-1/2`, and `dt` on `ω` only gives `1`. -/
theorem probe_phaseHead_value : phaseHead 2 1 2 (1/4) (1/2) probeHist 0 = 3/2 := by
  have he : (Finset.univ.erase (0 : Fin 2)) = {1} := by decide
  simp only [phaseHead, he, Finset.sum_singleton, probeHist, clippedWeight]
  norm_num

/-- A history whose slot `k` holds `k * π`. -/
noncomputable def probeLadder (k : ℕ) (_i : Fin 2) : ℝ := (k : ℝ) * Real.pi

/-- The head advances by `dt * ω` (the delayed sine is `sin π = 0`), and slot `k > 0`
takes the old slot `k - 1`. -/
theorem probe_phaseStep_values :
    phaseStep 2 1 1 5 1 probeLadder 0 0 = 5 ∧ phaseStep 2 1 1 5 1 probeLadder 1 0 = 0 ∧
      phaseStep 2 1 1 5 1 probeLadder 2 0 = Real.pi := by
  have he : (Finset.univ.erase (0 : Fin 2)) = {1} := by decide
  refine ⟨?_, ?_, ?_⟩
  · simp only [phaseStep, if_true, phaseHead, he, Finset.sum_singleton, probeLadder, clippedWeight]
    norm_num
  · norm_num [phaseStep, probeLadder]
  · norm_num [phaseStep, probeLadder]

/-- `orbitPath` at `dt = 2`, `Ω = 3`, `θ = 5`, `t = 7`, `k = 2`, `v k i = k`:
`5 - 2*2*3 + 7*2 = 7`. -/
theorem probe_orbitPath_value : orbitPath 1 2 3 5 (fun k _ => (k : ℝ)) 7 2 0 = 7 := by
  norm_num [orbitPath]

/-- The orbit does not move backward by `dt * Ω` (`n = 1`, `d = 0`, `dt = Ω = ω = 1`). -/
theorem false_orbit_backward :
    ¬ (∀ (n d k : ℕ) (dt omega b Omega theta : ℝ) (_hn : 1 ≤ n) (_hk : k ≤ d)
      (_horbit : Omega = omega + ((n : ℝ) - 1) * clippedWeight b *
        Real.sin (-((d : ℝ) * dt * Omega)))
      (v : ℕ → Fin n → ℝ) (i : Fin n),
      phaseStep n d dt omega b (orbitPath n dt Omega theta v 0) k i =
        orbitPath n dt Omega theta v 0 k i - dt * Omega) := by
  intro H
  have hf : (1 : ℝ) = 1 + (((1 : ℕ) : ℝ) - 1) * clippedWeight 0 *
      Real.sin (-(((0 : ℕ) : ℝ) * 1 * 1)) := by norm_num
  have h1 := H 1 0 0 1 1 0 1 0 le_rfl le_rfl hf (fun _ _ => 0) 0
  rw [orbit_invariant 1 0 0 1 1 0 1 0 le_rfl le_rfl hf] at h1
  linarith

/-- Without the frequency equation the orbit identity fails (`ω = 0`, `Ω = 1`). -/
theorem false_orbit_no_frequency :
    ¬ (∀ (n d k : ℕ) (dt omega b Omega theta : ℝ) (_hn : 1 ≤ n) (_hk : k ≤ d)
      (_horbit : True)
      (v : ℕ → Fin n → ℝ) (i : Fin n),
      phaseStep n d dt omega b (orbitPath n dt Omega theta v 0) k i =
        orbitPath n dt Omega theta v 0 k i + dt * Omega) := by
  intro H
  have h1 := H 1 0 0 1 0 0 1 0 le_rfl le_rfl trivial (fun _ _ => 0) 0
  have he : (Finset.univ.erase (0 : Fin 1)) = ∅ := by decide
  simp only [phaseStep, if_true, phaseHead, he, Finset.sum_empty, orbitPath] at h1
  norm_num at h1

/-- The block formula needs `0 < b`: at `b = -1` the clipped head has derivative `0`
(`clipping_probe`) while the block expression is `-1`. -/
theorem false_block_no_pos :
    ¬ (∀ (n d : ℕ) (dt omega b Omega theta : ℝ) (_hn : 1 ≤ n) (_hb : True)
      (v : ℕ → Fin n → ℝ) (i : Fin n),
      HasDerivAt (fun t => phaseHead n d dt omega b (orbitPath n dt Omega theta v t) i)
        ((1 - ((n : ℝ) - 1) * (dt * b * Real.cos ((d : ℝ) * dt * Omega))) * v 0 i +
          (dt * b * Real.cos ((d : ℝ) * dt * Omega)) *
            ((∑ j : Fin n, v d j) - v d i)) 0) := by
  intro H
  have h1 := H 2 1 1 0 (-1) 0 0 (by norm_num) trivial twoNodeDirection 0
  have h2 := h1.unique clipping_probe.1
  norm_num [twoNodeDirection, Fin.sum_univ_two] at h2

/-- History slot `k` takes the old slot `k - 1`, not slot `k` (`adjacent_history_probe`). -/
theorem false_history_no_shift :
    ¬ (∀ (n d k : ℕ) (dt omega b Omega theta : ℝ) (_hk : 0 < k)
      (v : ℕ → Fin n → ℝ) (i : Fin n),
      HasDerivAt (fun t => phaseStep n d dt omega b (orbitPath n dt Omega theta v t) k i)
        (v k i) 0) := by
  intro H
  have h1 := H 2 1 1 1 0 (1/2) 0 0 Nat.one_pos unequalHistoryDirection 0
  have h2 := h1.unique adjacent_history_probe.1
  norm_num [unequalHistoryDirection] at h2

/-- The neighbor sine reads the delayed slot `d`, not the current slot `0`
(`n = 2`, `d = 1`, the other node's delayed phase perturbed). -/
theorem false_neighbor_current_slot :
    ¬ (∀ (n d : ℕ) (dt Omega theta : ℝ) (v : ℕ → Fin n → ℝ) (i j : Fin n),
      HasDerivAt (fun t => Real.sin (orbitPath n dt Omega theta v t d j -
        orbitPath n dt Omega theta v t 0 i))
        (Real.cos ((d : ℝ) * dt * Omega) * (v 0 j - v 0 i)) 0) := by
  intro H
  have h1 := H 2 1 1 0 0 twoNodeDirection 0 1
  have h2 := h1.unique (neighbor_derivative 2 1 1 0 0 twoNodeDirection 0 1)
  norm_num [twoNodeDirection] at h2

#print axioms orbit_invariant
#print axioms neighbor_derivative
#print axioms head_derivative_raw
#print axioms head_derivative_block
#print axioms phase_step_head
#print axioms history_derivative
#print axioms two_node_probe
#print axioms self_coupling_probe
#print axioms adjacent_history_probe
#print axioms clipping_probe
#print axioms probe_clippedWeight_values
#print axioms probe_phaseHead_value
#print axioms probe_phaseStep_values
#print axioms probe_orbitPath_value
#print axioms false_orbit_backward
#print axioms false_orbit_no_frequency
#print axioms false_block_no_pos
#print axioms false_history_no_shift
#print axioms false_neighbor_current_slot

end AIEFGate.EngineStepRef
