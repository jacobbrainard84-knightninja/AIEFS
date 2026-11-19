/- SPDX-License-Identifier: Apache-2.0
Research candidate: mode bounds for a proposed complete-graph phase block.
This is not a proof that the AIEFS engine's Jacobian equals this block. -/
import AIEFGateCore.DelayModeMain

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.CompleteGraphPhase

/-- A proposed complexified phase-delay block. The total-minus-self term is
    the sum over neighbours on a complete graph with no self-loop. -/
def phaseStep (n d : ℕ) (h : ℝ) (x : ℕ → Fin n → ℂ) (k : ℕ) (i : Fin n) : ℂ :=
  if k = 0 then
    ((1 - ((n - 1 : ℕ) : ℝ) * h : ℝ) : ℂ) * x 0 i +
      (h : ℂ) * ((∑ j : Fin n, x d j) - x d i)
  else x (k - 1) i

/-- On a complete graph, total minus self equals the sum over the other nodes. -/
theorem total_sub_self (n : ℕ) (y : Fin n → ℂ) (i : Fin n) :
    (∑ j : Fin n, y j) - y i = ∑ j ∈ Finset.univ.erase i, y j := by
  have hs := Finset.sum_erase_add (s := Finset.univ) y (Finset.mem_univ i)
  linear_combination -hs

/-- For a delayed zero-sum state each node sees the scalar transverse shift. -/
theorem transverse_step (n d : ℕ) (h : ℝ) (x : ℕ → Fin n → ℂ)
    (hzero : (∑ j : Fin n, x d j) = 0) (k : ℕ) (i : Fin n) :
    phaseStep n d h x k i =
      DelayModeMain.delayStep d ((1 - ((n - 1 : ℕ) : ℝ) * h : ℝ) : ℂ)
        (-(h : ℂ)) (fun t => x t i) k := by
  by_cases hk : k = 0
  · simp [phaseStep, DelayModeMain.delayStep, hk, hzero, mul_neg]
  · simp [phaseStep, DelayModeMain.delayStep, hk]

/-- A nonzero eigenmode with zero sum on the delayed slice is strictly inside
the disk for n≥2 and 0 < (n−1)h < 1. -/
theorem transverse_eigenvalue_inside (n d : ℕ) (h : ℝ) (z : ℂ)
    (x : ℕ → Fin n → ℂ) (hn : 2 ≤ n) (hh : 0 < h)
    (hmh : (((n - 1 : ℕ) : ℝ) * h) < 1)
    (hzero : (∑ j : Fin n, x d j) = 0)
    (heigen : ∀ k, k ≤ d → ∀ i, phaseStep n d h x k i = z * x k i)
    (hnonzero : ∃ k, k ≤ d ∧ ∃ i, x k i ≠ 0) : ‖z‖ < 1 := by
  obtain ⟨k, hk, i, hki⟩ := hnonzero
  have hm : 1 ≤ n - 1 := by omega
  apply DelayModeMain.transverse_step_eigenvalue_inside d (n - 1) z h (fun t => x t i)
    hm hh hmh
  · intro t ht
    rw [← transverse_step n d h x hzero t i]
    exact heigen t ht i
  · exact ⟨k, hk, hki⟩

/-- The complete-graph neighbour sum on a constant slice equals (n−1) copies. -/
theorem constant_neighbour_sum (n : ℕ) (hn : 1 ≤ n) (y : Fin n → ℂ)
    (hconst : ∀ i j, y i = y j) (i : Fin n) :
    (∑ j : Fin n, y j) - y i = (((n - 1 : ℕ) : ℂ)) * y i := by
  have hsum : (∑ j : Fin n, y j) = (n : ℂ) * y i := by
    calc
      (∑ j : Fin n, y j) = ∑ _j : Fin n, y i := by
        apply Finset.sum_congr rfl
        intro j hj
        exact hconst j i
      _ = (n : ℂ) * y i := by simp
  rw [hsum]
  have heq : (n - 1 : ℕ) + 1 = n := by omega
  have hcast : (((n - 1 : ℕ) : ℂ)) + 1 = (n : ℂ) := by exact_mod_cast heq
  rw [← hcast]
  ring

/-- On a delayed node-constant state each node sees the scalar common shift. -/
theorem common_step (n d : ℕ) (h : ℝ) (x : ℕ → Fin n → ℂ)
    (hn : 1 ≤ n) (hconst : ∀ i j, x d i = x d j) (k : ℕ) (i : Fin n) :
    phaseStep n d h x k i =
      DelayModeMain.delayStep d ((1 - (((n - 1 : ℕ) : ℝ) * h) : ℝ) : ℂ)
        ((((n - 1 : ℕ) : ℝ) * h : ℝ) : ℂ) (fun t => x t i) k := by
  by_cases hk : k = 0
  · simp only [phaseStep, DelayModeMain.delayStep, hk, if_true]
    rw [constant_neighbour_sum n hn (x d) hconst i]
    push_cast
    ring
  · simp [phaseStep, DelayModeMain.delayStep, hk]

/-- A nonzero eigenmode with a constant delayed slice is bounded in the disk,
and 1 is its only possible unit-circle value. -/
theorem common_eigenvalue_bound (n d : ℕ) (h : ℝ) (z : ℂ)
    (x : ℕ → Fin n → ℂ) (hn : 2 ≤ n) (hh : 0 < h)
    (hmh : (((n - 1 : ℕ) : ℝ) * h) < 1)
    (hconst : ∀ i j, x d i = x d j)
    (heigen : ∀ k, k ≤ d → ∀ i, phaseStep n d h x k i = z * x k i)
    (hnonzero : ∃ k, k ≤ d ∧ ∃ i, x k i ≠ 0) :
    ‖z‖ ≤ 1 ∧ (‖z‖ = 1 → z = 1) := by
  obtain ⟨k, hk, i, hki⟩ := hnonzero
  have hm : 0 < (((n - 1 : ℕ) : ℝ) * h) := by
    have hmnat : 0 < n - 1 := by omega
    positivity
  apply DelayModeMain.common_step_eigenvalue_bound d z (((n - 1 : ℕ) : ℝ) * h)
    (fun t => x t i) hm hmh
  · intro t ht
    rw [← common_step n d h x (by omega) hconst t i]
    exact heigen t ht i
  · exact ⟨k, hk, hki⟩

end AIEFGate.CompleteGraphPhase
