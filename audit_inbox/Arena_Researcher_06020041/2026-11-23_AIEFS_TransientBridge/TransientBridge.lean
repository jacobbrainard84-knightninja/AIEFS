import AIEFGateCore.EngineStepRef

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
end
end AIEFGate.TransientBridge
