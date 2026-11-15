/- SPDX-License-Identifier: Apache-2.0
Research candidate: delayed roots at the unit-sum boundary. -/
import Mathlib.Analysis.Complex.Norm
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Tactic

set_option autoImplicit false
namespace AIEFGate.DelayBoundaryRoots

/-- A root of the delayed equation cannot lie outside the unit disk
when the nonnegative coefficient norms sum to at most one. -/
theorem root_norm_le_one (d : ℕ) (z s : ℂ) (a b : ℝ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hs : a + b ≤ 1) (hns : ‖s‖ = b)
    (hroot : z ^ (d + 1) = (a : ℂ) * z ^ d + s) : ‖z‖ ≤ 1 := by
  by_contra hn
  have hz : 1 < ‖z‖ := lt_of_not_ge hn
  have hp : 1 ≤ ‖z‖ ^ d := one_le_pow₀ (le_of_lt hz)
  have htriangle := norm_add_le ((a : ℂ) * z ^ d) s
  have ht : ‖z‖ ^ d * ‖z‖ ≤ a * ‖z‖ ^ d + b := by
    rw [← norm_pow, ← norm_mul, ← pow_succ, hroot]
    simpa [norm_mul, norm_pow, Complex.norm_real, Real.norm_eq_abs,
      abs_of_nonneg ha, hns] using htriangle
  have h1 : 0 ≤ b * (‖z‖ ^ d - 1) := mul_nonneg hb (by linarith)
  have h2 : 0 < (‖z‖ ^ d) * (‖z‖ - 1) := mul_pos (by positivity) (by linarith)
  have h3 : 0 ≤ (‖z‖ ^ d) * (1 - (a + b)) :=
    mul_nonneg (by positivity) (by linarith)
  nlinarith

/-- Equality in the convex unit-circle triangle forces the two terms to align. -/
theorem unit_sum_aligned (w s : ℂ) (a b : ℝ)
    (ha : 0 < a) (_hb : 0 ≤ b) (hs : a + b = 1)
    (hw : ‖w‖ = 1) (hns : ‖s‖ = b)
    (htotal : ‖(a : ℂ) * w + s‖ = 1) : (b : ℂ) * w = s := by
  have heq : ‖(a : ℂ) * w + s‖ = ‖(a : ℂ) * w‖ + ‖s‖ := by
    rw [htotal, norm_mul, Complex.norm_real, Real.norm_eq_abs, abs_of_pos ha, hw, mul_one, hns]
    linarith
  have he := (norm_add_eq_iff_real).mp heq
  simp only [norm_mul, Complex.norm_real, Real.norm_eq_abs, abs_of_pos ha, hw, mul_one, hns,
    Complex.real_smul] at he
  have hane : (a : ℂ) ≠ 0 := by exact_mod_cast (ne_of_gt ha)
  apply mul_left_cancel₀ hane
  calc
    (a : ℂ) * ((b : ℂ) * w) = (b : ℂ) * ((a : ℂ) * w) := by ring
    _ = (a : ℂ) * s := he

/-- For the common delayed mode, every root is in the closed unit disk and
its only possible unit-circle root is 1. -/
theorem common_root_closed_and_unit_unique (d : ℕ) (z : ℂ) (h : ℝ)
    (hh : 0 < h) (hh1 : h < 1)
    (hroot : z ^ (d + 1) = ((1 - h : ℝ) : ℂ) * z ^ d + (h : ℂ)) :
    ‖z‖ ≤ 1 ∧ (‖z‖ = 1 → z = 1) := by
  have hpos : 0 < 1 - h := by linarith
  have hnorm : ‖(h : ℂ)‖ = h := by
    simp [Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg (le_of_lt hh)]
  constructor
  · apply root_norm_le_one d z (h : ℂ) (1 - h) h (by linarith) (by linarith) (by linarith) hnorm
    exact hroot
  · intro hz
    have hw : ‖z ^ d‖ = 1 := by simp [norm_pow, hz]
    have ht : ‖((1 - h : ℝ) : ℂ) * z ^ d + (h : ℂ)‖ = 1 := by
      rw [← hroot, norm_pow, hz]
      simp
    have halign := unit_sum_aligned (z ^ d) (h : ℂ) (1 - h) h hpos
      (by linarith) (by linarith) hw hnorm ht
    have hhne : (h : ℂ) ≠ 0 := by exact_mod_cast (ne_of_gt hh)
    have hpow : z ^ d = 1 := by
      apply mul_left_cancel₀ hhne
      simpa using halign
    have he : z = ((1 - h : ℝ) : ℂ) + (h : ℂ) := by
      simpa [pow_succ, hpow] using hroot
    push_cast at he
    linear_combination he

/-- The N=2 transverse-mode roots lie strictly inside the unit disk.
This treats the boundary `a+b=1` not covered by the Cycle 11 strict-sum lemma. -/
theorem two_node_transverse_root_inside (d : ℕ) (z : ℂ) (h : ℝ)
    (hh : 0 < h) (hh1 : h < 1)
    (hroot : z ^ (d + 1) = ((1 - h : ℝ) : ℂ) * z ^ d - (h : ℂ)) :
    ‖z‖ < 1 := by
  have hpos : 0 < 1 - h := by linarith
  have hnorm : ‖-(h : ℂ)‖ = h := by
    simp [Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg (le_of_lt hh)]
  have hroot' : z ^ (d + 1) = ((1 - h : ℝ) : ℂ) * z ^ d + (-(h : ℂ)) := by
    simpa [sub_eq_add_neg] using hroot
  have hle := root_norm_le_one d z (-(h : ℂ)) (1 - h) h
    (by linarith) (by linarith) (by linarith) hnorm hroot'
  by_contra hn
  have hz : ‖z‖ = 1 := le_antisymm hle (le_of_not_gt hn)
  have hw : ‖z ^ d‖ = 1 := by simp [norm_pow, hz]
  have ht : ‖((1 - h : ℝ) : ℂ) * z ^ d + (-(h : ℂ))‖ = 1 := by
    rw [← hroot', norm_pow, hz]
    simp
  have halign := unit_sum_aligned (z ^ d) (-(h : ℂ)) (1 - h) h hpos
    (by linarith) (by linarith) hw hnorm ht
  have hhne : (h : ℂ) ≠ 0 := by exact_mod_cast (ne_of_gt hh)
  have hpow : z ^ d = -1 := by
    apply mul_left_cancel₀ hhne
    simpa using halign
  have hzneg : -z = -1 := by
    calc
      -z = z ^ d * z := by rw [hpow]; ring
      _ = z ^ (d + 1) := by rw [pow_succ]
      _ = ((1 - h : ℝ) : ℂ) * z ^ d - (h : ℂ) := hroot
      _ = -1 := by rw [hpow]; push_cast; ring
  have hz1 : z = 1 := neg_injective hzneg
  rw [hz1] at hpow
  norm_num at hpow

end AIEFGate.DelayBoundaryRoots
