/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
import Mathlib.Tactic.LinearCombination

/-!
# Delay characteristic roots (Arena cycles 9 and 10)

Research candidate. Pure algebra about two characteristic polynomials that appear in the
linearisation of the engine step around the homogeneous-ω rotating orbit (Arena cycle 8):

* `P(λ) = λ^(d+1) - (1-a) λ^d - a` with `0 < a < 1` (phase inside the symmetric subspace):
  every root is `1` or lies strictly inside the unit disk (`1` is always a root; simplicity is
  not proved here).
* `Q(λ) = λ^(d+1) - (1-m h) λ^d + h` with `m ≥ 1`, `0 < h`, `m h < 1` (transverse phase):
  every root lies strictly inside the unit disk.
* The projected-branch weight slope `C ε / (x + ε)^2` is below `1/4` whenever `x > C > 0`.

Scope: these lemmas say nothing about whether the linearisation is correct, about the
projected orbit's non-differentiable tie, about heterogeneous ω, or about production runs.
-/

set_option autoImplicit false

namespace AIEFGate
namespace DelayRoots

open Complex

/-- A point on or outside the unit circle that is within `1 - c` of `c > 0` is `1`. -/
theorem eq_one_of_norm_ge_one_of_near (c : ℝ) (hc : 0 < c) (z : ℂ) (hz : 1 ≤ ‖z‖)
    (hzc : ‖z - (c : ℂ)‖ ≤ 1 - c) : z = 1 := by
  have hle : ‖z‖ ≤ 1 := by
    have h1 : ‖z‖ ≤ ‖z - (c : ℂ)‖ + ‖(c : ℂ)‖ := by
      simpa using norm_le_norm_sub_add z (c : ℂ)
    have h2 : ‖(c : ℂ)‖ = c := by simp [abs_of_pos hc]
    linarith
  have hn : ‖z‖ = 1 := le_antisymm hle hz
  have hsq : z.re ^ 2 + z.im ^ 2 = 1 := by
    have h := Complex.sq_norm z
    rw [hn, Complex.normSq_apply] at h
    nlinarith [h]
  have hsq2 : (z.re - c) ^ 2 + z.im ^ 2 ≤ (1 - c) ^ 2 := by
    have h := Complex.sq_norm (z - (c : ℂ))
    rw [Complex.normSq_apply] at h
    simp only [sub_re, sub_im, ofReal_re, ofReal_im, sub_zero] at h
    have h0 : 0 ≤ ‖z - (c : ℂ)‖ := norm_nonneg _
    nlinarith [hzc, h0, h]
  have hre : 1 ≤ z.re := by nlinarith
  have him : z.im = 0 := by nlinarith
  have hre1 : z.re = 1 := by nlinarith
  apply Complex.ext <;> simp [hre1, him]

/-- Cycle 9: every root of `λ^(d+1) - (1-a) λ^d - a` with `0 < a < 1` is `1` or strictly
inside the unit disk. -/
theorem symRoot_eq_one_or_lt (a : ℝ) (ha0 : 0 < a) (ha1 : a < 1) (d : ℕ) (z : ℂ)
    (hz : z ^ (d + 1) - ((1 - a : ℝ) : ℂ) * z ^ d - (a : ℂ) = 0) :
    z = 1 ∨ ‖z‖ < 1 := by
  by_cases hlt : ‖z‖ < 1
  · exact Or.inr hlt
  left
  replace hlt : 1 ≤ ‖z‖ := not_lt.mp hlt
  have hfac : z ^ d * (z - ((1 - a : ℝ) : ℂ)) = (a : ℂ) := by
    linear_combination hz
  have hnorm : ‖z‖ ^ d * ‖z - ((1 - a : ℝ) : ℂ)‖ = a := by
    have := congrArg norm hfac
    rw [norm_mul, norm_pow] at this
    simpa [abs_of_pos ha0] using this
  have hpow : 1 ≤ ‖z‖ ^ d := one_le_pow₀ hlt
  have hnear : ‖z - ((1 - a : ℝ) : ℂ)‖ ≤ 1 - (1 - a) := by
    have h0 : 0 ≤ ‖z - ((1 - a : ℝ) : ℂ)‖ := norm_nonneg _
    nlinarith
  exact eq_one_of_norm_ge_one_of_near (1 - a) (by linarith) z hlt hnear

/-- Cycle 9: `1` is a root of `P`, together with the arithmetic identity
`(d + 1) - (1 - a) d = 1 + a d`. By the power rule that number is `P'(1)`, but the derivative
itself is not formalised here, so neither `P'(1) ≠ 0` nor simplicity of the root is proved. -/
theorem symRoot_one (a : ℝ) (d : ℕ) :
    (1 : ℂ) ^ (d + 1) - ((1 - a : ℝ) : ℂ) * 1 ^ d - (a : ℂ) = 0 ∧
      ((d + 1 : ℝ) - (1 - a) * d = 1 + a * d) := by
  constructor
  · push_cast; ring
  · ring

/-- Cycle 10: every root of `λ^(d+1) - (1-m h) λ^d + h` with `1 ≤ m`, `0 < h`, `m h < 1`
lies strictly inside the unit disk. -/
theorem transRoot_lt_one (m : ℕ) (hm : 1 ≤ m) (h : ℝ) (h0 : 0 < h) (hmh : (m : ℝ) * h < 1)
    (d : ℕ) (z : ℂ)
    (hz : z ^ (d + 1) - ((1 - m * h : ℝ) : ℂ) * z ^ d + (h : ℂ) = 0) : ‖z‖ < 1 := by
  by_contra hge
  replace hge : 1 ≤ ‖z‖ := not_lt.mp hge
  have hm1 : (1 : ℝ) ≤ m := by exact_mod_cast hm
  have hfac : z ^ d * (z - ((1 - m * h : ℝ) : ℂ)) = -(h : ℂ) := by
    linear_combination hz
  have hnorm : ‖z‖ ^ d * ‖z - ((1 - m * h : ℝ) : ℂ)‖ = h := by
    have := congrArg norm hfac
    rw [norm_mul, norm_pow, norm_neg] at this
    simpa [abs_of_pos h0] using this
  have hpow : 1 ≤ ‖z‖ ^ d := one_le_pow₀ hge
  have h0n : 0 ≤ ‖z - ((1 - m * h : ℝ) : ℂ)‖ := norm_nonneg _
  have hnear0 : ‖z - ((1 - m * h : ℝ) : ℂ)‖ ≤ h := by nlinarith
  have hnear : ‖z - ((1 - m * h : ℝ) : ℂ)‖ ≤ 1 - (1 - m * h) := by nlinarith
  have hz1 := eq_one_of_norm_ge_one_of_near (1 - m * h) (by linarith) z hge hnear
  subst hz1
  have hval : ((1 : ℝ) - (1 - m * h) + h : ℝ) = 0 := by
    have := hz
    simp only [one_pow, mul_one] at this
    have h2 := congrArg Complex.re this
    simpa using h2
  nlinarith

/-- Cycle 9 projected branch: the weight slope `C ε / (x + ε)^2` is below `1/4` when
`x > C > 0` and `ε > 0`. -/
theorem projectedSlope_lt_quarter (C ε x : ℝ) (hC : 0 < C) (hε : 0 < ε) (hx : C < x) :
    C * ε / (x + ε) ^ 2 < 1 / 4 := by
  have hxe : 0 < x + ε := by linarith
  have hpos : 0 < (x + ε) ^ 2 := by positivity
  rw [div_lt_iff₀ hpos]
  nlinarith [sq_nonneg (x - ε)]

/-- `0 < ε` is redundant given `0 < C`: for `ε ≤ 0` the slope is `≤ 0`. (Dropping both `0 < C`
and `0 < ε` is false, see `false_slope_both_negative`.) -/
theorem projectedSlope_lt_quarter_of_C (C ε x : ℝ) (hC : 0 < C) (hx : C < x) :
    C * ε / (x + ε) ^ 2 < 1 / 4 := by
  rcases lt_or_ge 0 ε with hε | hε
  · exact projectedSlope_lt_quarter C ε x hC hε hx
  · have hnum : C * ε ≤ 0 := mul_nonpos_of_nonneg_of_nonpos hC.le hε
    have : C * ε / (x + ε) ^ 2 ≤ 0 := div_nonpos_of_nonpos_of_nonneg hnum (sq_nonneg _)
    linarith

/-- Positive instance at delay `d = 2` (`m = 1`, `h = 1/2`): every root of
`λ^3 - (1/2) λ^2 + 1/2` is strictly inside the unit disk. -/
theorem transRoot_instance_d_two (z : ℂ)
    (hz : z ^ (2 + 1) - ((1 - ((1 : ℕ) : ℝ) * (1 / 2) : ℝ) : ℂ) * z ^ 2 + ((1 / 2 : ℝ) : ℂ) = 0) :
    ‖z‖ < 1 :=
  transRoot_lt_one 1 le_rfl (1 / 2) (by norm_num) (by norm_num) 2 z hz

/-- Positive instance at delay `d = 2` (`a = 1/2`): every root of `λ^3 - (1/2) λ^2 - 1/2` is `1`
or strictly inside the unit disk. -/
theorem symRoot_instance_d_two (z : ℂ)
    (hz : z ^ (2 + 1) - ((1 - 1 / 2 : ℝ) : ℂ) * z ^ 2 - ((1 / 2 : ℝ) : ℂ) = 0) :
    z = 1 ∨ ‖z‖ < 1 :=
  symRoot_eq_one_or_lt (1 / 2) (by norm_num) (by norm_num) 2 z hz

/-! ## Witnesses: each hypothesis is needed (used by the DelayRoots statement mutants) -/

/-- `a = 2`, `d = 1`: `-2` is a root of `P`. -/
theorem symRoot_root_a_two :
    (-2 : ℂ) ^ (1 + 1) - ((1 - 2 : ℝ) : ℂ) * (-2 : ℂ) ^ 1 - ((2 : ℝ) : ℂ) = 0 := by
  push_cast; ring

/-- Without `a < 1` the root `-2` (for `a = 2`) is neither `1` nor inside the disk. -/
theorem false_symRoot_no_upper : ¬ ((-2 : ℂ) = 1 ∨ ‖(-2 : ℂ)‖ < 1) := by
  rintro (h | h)
  · have := congrArg Complex.re h
    norm_num at this
  · norm_num at h

/-- The neutral root `1` is never strictly inside the disk. -/
theorem false_one_inside : ¬ ‖(1 : ℂ)‖ < 1 := by
  norm_num

/-- `m = 0`, `h = 3`, `d = 0`: `-2` is a root of `Q`. -/
theorem transRoot_root_m_zero :
    (-2 : ℂ) ^ (0 + 1) - ((1 - ((0 : ℕ) : ℝ) * 3 : ℝ) : ℂ) * (-2 : ℂ) ^ 0 + ((3 : ℝ) : ℂ) = 0 := by
  push_cast; ring

/-- `m = 1`, `h = 1`, `d = 0`: `-1` is a root of `Q` (here `m h = 1`). -/
theorem transRoot_root_mh_one :
    (-1 : ℂ) ^ (0 + 1) - ((1 - ((1 : ℕ) : ℝ) * 1 : ℝ) : ℂ) * (-1 : ℂ) ^ 0 + ((1 : ℝ) : ℂ) = 0 := by
  push_cast; ring

theorem false_minus_two_inside : ¬ ‖(-2 : ℂ)‖ < 1 := by
  norm_num

theorem false_minus_one_inside : ¬ ‖(-1 : ℂ)‖ < 1 := by
  norm_num

/-- At `x = C = ε = 1` the slope equals `1/4`, so `C < x` cannot be weakened to `C ≤ x`. -/
theorem false_slope_at_boundary : ¬ ((1 : ℝ) * 1 / (1 + 1) ^ 2 < 1 / 4) := by
  norm_num

/-- `a = -2`, `d = 1`: `2` is a root of `P` (`P = (λ - 1)(λ - 2)`), so `0 < a` is needed. -/
theorem symRoot_root_a_neg_two :
    (2 : ℂ) ^ (1 + 1) - ((1 - (-2) : ℝ) : ℂ) * (2 : ℂ) ^ 1 - ((-2 : ℝ) : ℂ) = 0 := by
  push_cast; ring

theorem false_symRoot_two : ¬ ((2 : ℂ) = 1 ∨ ‖(2 : ℂ)‖ < 1) := by
  rintro (h | h)
  · have := congrArg Complex.re h
    norm_num at this
  · norm_num at h

/-- `a = 1`, `d = 1`: `-1` is a root of `P = λ^2 - 1`, so `a < 1` cannot be weakened to `a ≤ 1`. -/
theorem symRoot_root_a_one :
    (-1 : ℂ) ^ (1 + 1) - ((1 - 1 : ℝ) : ℂ) * (-1 : ℂ) ^ 1 - ((1 : ℝ) : ℂ) = 0 := by
  push_cast; ring

theorem false_symRoot_minus_one : ¬ ((-1 : ℂ) = 1 ∨ ‖(-1 : ℂ)‖ < 1) := by
  rintro (h | h)
  · have := congrArg Complex.re h
    norm_num at this
  · norm_num at h

/-- `m = 1`, `h = 0`, `d = 0`: `1` is a root of `Q = λ - 1`, so `0 < h` is needed. -/
theorem transRoot_root_h_zero :
    (1 : ℂ) ^ (0 + 1) - ((1 - ((1 : ℕ) : ℝ) * 0 : ℝ) : ℂ) * (1 : ℂ) ^ 0 + ((0 : ℝ) : ℂ) = 0 := by
  push_cast; ring

/-- `m = h = 1`, `d = 1`: `i` is a root of `Q = λ^2 + 1`, so `m h < 1` cannot be weakened to
`m h ≤ 1` (and the witness has `d ≥ 1`, unlike `transRoot_root_mh_one`). -/
theorem transRoot_root_I :
    Complex.I ^ (1 + 1) - ((1 - ((1 : ℕ) : ℝ) * 1 : ℝ) : ℂ) * Complex.I ^ 1 + ((1 : ℝ) : ℂ) =
      0 := by
  push_cast; simp

theorem false_I_inside : ¬ ‖Complex.I‖ < 1 := by
  simp

/-- `C = ε = -1`, `x = -1/2` (so `x > C`): the slope is `4/9`, so `0 < C` and `0 < ε` cannot
both be dropped. -/
theorem false_slope_both_negative :
    ¬ ((-1 : ℝ) * (-1) / ((-1 / 2) + (-1)) ^ 2 < 1 / 4) := by
  norm_num

end DelayRoots
end AIEFGate

#print axioms AIEFGate.DelayRoots.symRoot_eq_one_or_lt
#print axioms AIEFGate.DelayRoots.symRoot_one
#print axioms AIEFGate.DelayRoots.transRoot_lt_one
#print axioms AIEFGate.DelayRoots.projectedSlope_lt_quarter
#print axioms AIEFGate.DelayRoots.projectedSlope_lt_quarter_of_C
