/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.EngineStepRef

/-!
# Transient energy of one mean-zero mode at c = 1/4 (Arena D13)

Research candidate, included per the owner's choice of 12 files. For `N = 3`, `d = 1`, `dt·b =
1/4` a mean-zero spatial mode follows the two-slot update `step`, whose derivative link to
`EngineStepRef.phaseStep` is proved; the two-slot energy grows at most by `81/64` in one step,
halves every two steps and stays below `81/64` times the start for all time. The Euclidean gain is
largely a queue-copy artifact and must not be cited as engine amplification (MERGE_MANIFEST).
Value probes and `false_*` witnesses appended (SPEC §17).

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D13, deposit sha256 `5327041b…`; proofs and
statements unchanged from the deposit.
-/

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.TransientBridge
open AIEFGate.EngineStepRef
noncomputable section

def stepSize : ℝ := 1 / 4

def mode (i : Fin 3) : ℝ := if i = 0 then 1 else if i = 1 then -1 else 0

def direction (x y : ℝ) (k : ℕ) (i : Fin 3) : ℝ :=
  if k = 0 then x * mode i else if k = 1 then y * mode i else 0

def step (p : ℝ × ℝ) : ℝ × ℝ :=
  ((1 - 2 * stepSize) * p.1 - stepSize * p.2, p.1)

def energy (p : ℝ × ℝ) : ℝ := p.1 ^ 2 + p.2 ^ 2

def evolve : ℕ → ℝ × ℝ → ℝ × ℝ
  | 0, p => p
  | n + 1, p => evolve n (step p)

theorem mode_sum : ∑ i : Fin 3, mode i = 0 := by
  have h20 : (2 : Fin 3) ≠ 0 := by decide
  have h21 : (2 : Fin 3) ≠ 1 := by decide
  norm_num [Fin.sum_univ_three, mode, h20, h21]

/-- Both matrix coordinates are actual derivatives of main's phase step. -/
theorem reference_mode_link (x y : ℝ) (i : Fin 3) :
    HasDerivAt (fun t => phaseStep 3 1 stepSize 0 1
      (orbitPath 3 stepSize 0 1 (direction x y) t) 0 i) ((step (x, y)).1 * mode i) 0 ∧
    HasDerivAt (fun t => phaseStep 3 1 stepSize 0 1
      (orbitPath 3 stepSize 0 1 (direction x y) t) 1 i) ((step (x, y)).2 * mode i) 0 := by
  have hs' : (∑ j : Fin 3, y * mode j) = 0 := by
    rw [← Finset.mul_sum, mode_sum, mul_zero]
  have hh := phase_step_head 3 1 stepSize 0 1 0 1 (by norm_num) (by norm_num)
    (direction x y) i
  have hq := history_derivative 3 1 1 stepSize 0 1 0 1 (by norm_num) (direction x y) i
  constructor
  · convert hh using 1
    simp [direction, step, stepSize, hs']
    ring
  · simpa [direction, step] using hq

/-- Exact growth for one step; norm is on the two delay coordinates. -/
theorem first_step_value : energy (step (1, 0)) = (5 / 4 : ℝ) := by
  norm_num [step, stepSize, energy]

/-- The mode is stable: its complex roots both have norm one half. -/
theorem characteristic_roots (z : ℂ)
    (hz : z ^ 2 - (1 / 2 : ℂ) * z + 1 / 4 = 0) : ‖z‖ = 1 / 2 := by
  have hc : z ^ 3 = -(1 / 8 : ℂ) := by
    linear_combination (z + 1 / 2) * hz
  have hn : ‖z‖ ^ 3 = (1 / 2 : ℝ) ^ 3 := by
    rw [← norm_pow, hc]
    norm_num
  have ho : Odd (3 : ℕ) := by decide
  exact ho.pow_injective hn

/-- Every nonzero eigenvector of the complexified two-slot update has
characteristic polynomial z² − z/2 + 1/4. -/
theorem eigenmode_stable (z v w : ℂ) (hne : v ≠ 0 ∨ w ≠ 0)
    (h1 : (1 / 2 : ℂ) * v - (1 / 4 : ℂ) * w = z * v)
    (h2 : v = z * w) : ‖z‖ = 1 / 2 := by
  have hw : w ≠ 0 := by
    intro h
    rcases hne with hv | hw
    · apply hv
      simpa [h] using h2
    · exact hw h
  have hm : (z ^ 2 - (1 / 2 : ℂ) * z + 1 / 4) * w = 0 := by
    linear_combination -h1 - (z - 1 / 2) * h2
  have hz : z ^ 2 - (1 / 2 : ℂ) * z + 1 / 4 = 0 :=
    (mul_eq_zero.mp hm).resolve_right hw
  exact characteristic_roots z hz

/-- Squared norm of all six node/queue coordinates of this spatial mode. -/
theorem spatial_energy (x y : ℝ) :
    (∑ i : Fin 3, (direction x y 0 i) ^ 2) +
      (∑ i : Fin 3, (direction x y 1 i) ^ 2) = 2 * energy (x, y) := by
  have h20 : (2 : Fin 3) ≠ 0 := by decide
  have h21 : (2 : Fin 3) ≠ 1 := by decide
  norm_num [Fin.sum_univ_three, direction, mode, energy, h20, h21]
  ring

/-- A single step has Euclidean norm at most 9/8 (energy factor 81/64). -/
theorem one_step_bound (p : ℝ × ℝ) : energy (step p) ≤ (81 / 64 : ℝ) * energy p := by
  rcases p with ⟨x, y⟩
  dsimp [energy, step, stepSize]
  nlinarith [sq_nonneg (x + 8 * y), sq_nonneg y]

/-- Every two consecutive steps reduce energy by at least a factor of two. -/
theorem two_step_bound (p : ℝ × ℝ) : energy (step (step p)) ≤ (1 / 2 : ℝ) * energy p := by
  rcases p with ⟨x, y⟩
  dsimp [energy, step, stepSize]
  nlinarith [sq_nonneg (x + y), sq_nonneg x, sq_nonneg y]

theorem energy_nonneg (p : ℝ × ℝ) : 0 ≤ energy p := by
  dsimp [energy]
  positivity

/-- Uniform bound for every iterate, using the two-step contraction. -/
theorem all_steps_bound (n : ℕ) : ∀ p : ℝ × ℝ,
    energy (evolve n p) ≤ (81 / 64 : ℝ) * energy p := by
  induction n using Nat.twoStepInduction with
  | zero =>
    intro p
    simp only [evolve]
    nlinarith [energy_nonneg p]
  | one =>
    intro p
    simpa only [evolve] using one_step_bound p
  | more n ih _ =>
    intro p
    change energy (evolve n (step (step p))) ≤ _
    have h := ih (step (step p))
    have h2 := two_step_bound p
    nlinarith [energy_nonneg p]

/-- From step two onward the perturbation is below its initial energy. -/
theorem after_first_bound (n : ℕ) (p : ℝ × ℝ) :
    energy (evolve (n + 2) p) ≤ (81 / 128 : ℝ) * energy p := by
  change energy (evolve n (step (step p))) ≤ _
  have h := all_steps_bound n (step (step p))
  have h2 := two_step_bound p
  nlinarith

#print axioms all_steps_bound
#print axioms after_first_bound
#print axioms reference_mode_link
#print axioms first_step_value
#print axioms characteristic_roots
#print axioms eigenmode_stable
#print axioms spatial_energy
#print axioms one_step_bound
#print axioms two_step_bound

/-! ### Value probe and negations used by the mutation harness (SPEC §17) -/

/-- `step (1, 2) = ((1 - 1/2)·1 - (1/4)·2, 1) = (0, 1)`. `stepSize = 1/3` gives `-1/3`, `1 - c`
gives
`1/4`, `+ c·p.2` gives `1`, an unshifted second slot gives `2`. -/
theorem probe_step_values : step (1, 2) = (0, 1) := by
  norm_num [step, stepSize]

/-- The two-slot energy is `x² + y²`. -/
theorem probe_energy_value : energy (1, 2) = 5 := by
  norm_num [energy]

/-- `one_step_bound` with factor `1` is false (`p = (1, 0)`: energy `5/4`). -/
theorem false_one_step_factor_one :
    ¬ (∀ (p : ℝ × ℝ), energy (step p) ≤ (1 : ℝ) * energy p) := by
  intro H
  have h := H (1, 0)
  norm_num [energy, step, stepSize] at h

/-- `two_step_bound` with factor `1/4` is false (`p = (1, -1)`: `37/64 > 1/2`). -/
theorem false_two_step_quarter :
    ¬ (∀ (p : ℝ × ℝ), energy (step (step p)) ≤ (1 / 4 : ℝ) * energy p) := by
  intro H
  have h := H (1, -1)
  norm_num [energy, step, stepSize] at h

/-- `all_steps_bound` with factor `1` is false (`n = 1`, `p = (1, 0)`). -/
theorem false_all_steps_factor_one :
    ¬ (∀ (n : ℕ), ∀ p : ℝ × ℝ, energy (evolve n p) ≤ (1 : ℝ) * energy p) := by
  intro H
  have h := H 1 (1, 0)
  norm_num [evolve, energy, step, stepSize] at h

#print axioms probe_step_values
#print axioms probe_energy_value
#print axioms false_one_step_factor_one
#print axioms false_two_step_quarter
#print axioms false_all_steps_factor_one
-- deposit theorems that had no `#print axioms` line in the deposit:
#print axioms mode_sum
#print axioms energy_nonneg

end
end AIEFGate.TransientBridge
