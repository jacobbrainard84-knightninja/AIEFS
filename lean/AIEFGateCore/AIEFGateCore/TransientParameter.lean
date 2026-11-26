/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.EngineStepRef
import AIEFGateCore.DelayRoots

/-!
# The same mode for a parameter c in (0, 1) (Arena D14)

Research candidate, included per the owner's choice of 12 files. For `c = dt·b` the two-slot
update `step c` is the derivative of `EngineStepRef.phaseStep` on the mode; for `0 < c < 1` every
characteristic root and nonzero eigenmode is strictly inside the unit disk, and for `0 ≤ c ≤ 1`
one step gains at most `21/8` in energy. `DelayRoots` is imported but no theorem of it is used.
The range's necessity and an all-time general-`c` bound are not proved here. Value probes and
`false_*` witnesses appended (SPEC §17).

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D14, deposit sha256 `51fbb51d…`; proofs and
statements unchanged from the deposit.
-/

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.TransientParameter
open AIEFGate.EngineStepRef
noncomputable section

def mode (i : Fin 3) : ℝ := if i = 0 then 1 else if i = 1 then -1 else 0

def direction (x y : ℝ) (k : ℕ) (i : Fin 3) : ℝ :=
  if k = 0 then x * mode i else if k = 1 then y * mode i else 0

def step (c : ℝ) (p : ℝ × ℝ) : ℝ × ℝ := ((1 - 2 * c) * p.1 - c * p.2, p.1)
def energy (p : ℝ × ℝ) : ℝ := p.1 ^ 2 + p.2 ^ 2

theorem mode_sum : ∑ i : Fin 3, mode i = 0 := by
  have h20 : (2 : Fin 3) ≠ 0 := by decide
  have h21 : (2 : Fin 3) ≠ 1 := by decide
  norm_num [Fin.sum_univ_three, mode, h20, h21]

/-- The parametric matrix is the derivative of the main reference's head and shift. -/
theorem reference_mode_link (dt b x y : ℝ) (hb : 0 < b) (i : Fin 3) :
    HasDerivAt (fun t => phaseStep 3 1 dt 0 b
      (orbitPath 3 dt 0 1 (direction x y) t) 0 i) ((step (dt * b) (x, y)).1 * mode i) 0 ∧
    HasDerivAt (fun t => phaseStep 3 1 dt 0 b
      (orbitPath 3 dt 0 1 (direction x y) t) 1 i) ((step (dt * b) (x, y)).2 * mode i) 0 := by
  have hs : (∑ j : Fin 3, y * mode j) = 0 := by
    rw [← Finset.mul_sum, mode_sum, mul_zero]
  have hh := phase_step_head 3 1 dt 0 b 0 1 (by norm_num) hb (direction x y) i
  have hq := history_derivative 3 1 1 dt 0 b 0 1 (by norm_num) (direction x y) i
  constructor
  · convert hh using 1
    simp [direction, step, hs]
    ring
  · simpa [direction, step] using hq

/-- For every c in [0,1], a near-sharp one-step energy bound. -/
theorem one_step_bound (c : ℝ) (p : ℝ × ℝ) (hc0 : 0 ≤ c) (hc1 : c ≤ 1) :
    energy (step c p) ≤ (21 / 8 : ℝ) * energy p := by
  rcases p with ⟨x, y⟩
  have hconv : 0 ≤ c * (1 - c) * (2 * x + y) ^ 2 :=
    mul_nonneg (mul_nonneg hc0 (sub_nonneg.mpr hc1)) (sq_nonneg _)
  have h0 : 2 * x ^ 2 ≤ (21 / 8 : ℝ) * (x ^ 2 + y ^ 2) := by
    nlinarith [sq_nonneg x, sq_nonneg y]
  have h1 : 2 * x ^ 2 + 2 * x * y + y ^ 2 ≤
      (21 / 8 : ℝ) * (x ^ 2 + y ^ 2) := by
    nlinarith [sq_nonneg (5 * x - 8 * y), sq_nonneg y]
  have ha := mul_le_mul_of_nonneg_left h0 (sub_nonneg.mpr hc1)
  have hb := mul_le_mul_of_nonneg_left h1 hc0
  dsimp [energy, step]
  nlinarith

/-- Any characteristic root is strictly stable throughout the entire interval. -/
theorem stable_roots (c : ℝ) (hc0 : 0 < c) (hc1 : c < 1) (z : ℂ)
    (hz : z ^ 2 - ((1 - 2 * c : ℝ) : ℂ) * z + (c : ℂ) = 0) : ‖z‖ < 1 := by
  by_contra hn
  have hn1 : 1 ≤ ‖z‖ := not_lt.mp hn
  have hs := Complex.sq_norm z
  rw [Complex.normSq_apply] at hs
  have hr := congrArg Complex.re hz
  have hi := congrArg Complex.im hz
  simp only [pow_two, Complex.mul_re, Complex.mul_im, Complex.sub_re, Complex.sub_im,
    Complex.add_re, Complex.add_im, Complex.ofReal_re, Complex.ofReal_im,
    Complex.zero_re, Complex.zero_im, zero_mul, sub_zero, add_zero] at hr hi
  by_cases hb : z.im = 0
  · have he : z.re ≤ -1 ∨ 1 ≤ z.re := by
      by_cases hp : 0 ≤ z.re
      · right; nlinarith
      · left; nlinarith
    rcases he with hl | hh
    · have hm : 0 ≤ (z.re + 1) * (z.re - 2 + 2 * c) :=
        mul_nonneg_of_nonpos_of_nonpos (by linarith) (by linarith)
      nlinarith
    · have hm : 0 ≤ (z.re - 1) * (z.re + 2 * c) :=
        mul_nonneg (by linarith) (by linarith)
      nlinarith
  · have hf : (2 * z.re - (1 - 2 * c)) * z.im = 0 := by nlinarith [hi]
    have he := (mul_eq_zero.mp hf).resolve_right hb
    nlinarith

/-- A nonzero eigenmode of the complexified two-slot update is stable. -/
theorem eigenmode_stable (c : ℝ) (hc0 : 0 < c) (hc1 : c < 1)
    (z v w : ℂ) (hne : v ≠ 0 ∨ w ≠ 0)
    (h1 : ((1 - 2 * c : ℝ) : ℂ) * v - (c : ℂ) * w = z * v)
    (h2 : v = z * w) : ‖z‖ < 1 := by
  have hw : w ≠ 0 := by
    intro h
    rcases hne with hv | hw
    · apply hv
      simpa [h] using h2
    · exact hw h
  have hm : (z ^ 2 - ((1 - 2 * c : ℝ) : ℂ) * z + (c : ℂ)) * w = 0 := by
    linear_combination -h1 - (z - ((1 - 2 * c : ℝ) : ℂ)) * h2
  exact stable_roots c hc0 hc1 z ((mul_eq_zero.mp hm).resolve_right hw)

/-- Direct concrete value, sensitive to the step's parameter and shift. -/
theorem quarter_probe : energy (step (1 / 4) (1, 0)) = (5 / 4 : ℝ) := by
  norm_num [step, energy]

/-- c=0 is not strictly stable: z=1 is a root. -/
theorem zero_boundary :
    (1 : ℂ) ^ 2 - ((1 - 2 * (0 : ℝ) : ℝ) : ℂ) * 1 + (0 : ℂ) = 0 ∧ ‖(1 : ℂ)‖ = 1 := by
  norm_num

#print axioms reference_mode_link
#print axioms one_step_bound
#print axioms stable_roots
#print axioms eigenmode_stable
#print axioms zero_boundary
#print axioms quarter_probe

/-! ### Value probes and negations used by the mutation harness (SPEC §17) -/

/-- `step (1/4) (1, 2) = (0, 1)`. `1 - c` gives `1/4`, `+ c·p.2` gives `1`, an unshifted second slot
gives `2`. -/
theorem probe_step_values : step (1/4) (1, 2) = (0, 1) := by
  norm_num [step]

/-- The two-slot energy is `x² + y²`. -/
theorem probe_energy_value : energy (1, 2) = 5 := by
  norm_num [energy]

/-- The mean-zero mode is `(1, -1, 0)`. -/
theorem probe_mode_values : mode 0 = 1 ∧ mode 1 = -1 ∧ mode 2 = 0 := by
  have h10 : (1 : Fin 3) ≠ 0 := by decide
  have h20 : (2 : Fin 3) ≠ 0 := by decide
  have h21 : (2 : Fin 3) ≠ 1 := by decide
  refine ⟨?_, ?_, ?_⟩ <;> simp [mode, h10, h20, h21]

/-- Dropping `c < 1` from `stable_roots` is false (`c = 2`: `z² + 3z + 2` has the root `-1`). -/
theorem false_stable_no_upper :
    ¬ (∀ (c : ℝ) (_hc0 : 0 < c) (_hc1 : True) (z : ℂ)
      (_hz : z ^ 2 - ((1 - 2 * c : ℝ) : ℂ) * z + (c : ℂ) = 0), ‖z‖ < 1) := by
  intro H
  have h := H 2 (by norm_num) trivial (-1) (by push_cast; norm_num)
  norm_num at h

/-- Dropping `0 < c` from `stable_roots` is false (`c = 0`: the root `1`, see `zero_boundary`). -/
theorem false_stable_no_pos :
    ¬ (∀ (c : ℝ) (_hc0 : True) (_hc1 : c < 1) (z : ℂ)
      (_hz : z ^ 2 - ((1 - 2 * c : ℝ) : ℂ) * z + (c : ℂ) = 0), ‖z‖ < 1) := by
  intro H
  have h := H 0 trivial (by norm_num) 1 (by push_cast; norm_num)
  norm_num at h

/-- Dropping `c ≤ 1` from `one_step_bound` is false (`c = 2`, `p = (1, 0)`: energy `10`). -/
theorem false_one_step_no_upper :
    ¬ (∀ (c : ℝ) (p : ℝ × ℝ) (_hc0 : 0 ≤ c) (_hc1 : True),
      energy (step c p) ≤ (21 / 8 : ℝ) * energy p) := by
  intro H
  have h := H 2 (1, 0) (by norm_num) trivial
  norm_num [energy, step] at h

#print axioms probe_step_values
#print axioms probe_energy_value
#print axioms probe_mode_values
#print axioms false_stable_no_upper
#print axioms false_stable_no_pos
#print axioms false_one_step_no_upper
-- deposit theorems that had no `#print axioms` line in the deposit:
#print axioms mode_sum

end
end AIEFGate.TransientParameter
