/- SPDX-License-Identifier: Apache-2.0
Research candidate: a strict unit-disk lemma for delayed transverse modes. -/
import Mathlib.Analysis.Complex.Norm
import Mathlib.Tactic

set_option autoImplicit false
namespace AIEFGate.DelayRootBound

/-- Strict unit-disk bound for roots of `z^(d+1) = a*z^d - b` when
`a,b ≥ 0` and `a+b < 1`. In particular this covers the transverse
polynomial from the interior N≥3 synchronized complete-graph orbit under
`h > 0` and `(N-1)*h < 1`. It does not cover the boundary case N=2. -/
theorem transverse_root_inside (d : ℕ) (z : ℂ) (a b : ℝ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hs : a + b < 1)
    (hroot : z ^ (d + 1) = (a : ℂ) * z ^ d - (b : ℂ)) : ‖z‖ < 1 := by
  by_contra hn
  have hz : 1 ≤ ‖z‖ := le_of_not_gt hn
  have hp : 1 ≤ ‖z‖ ^ d := one_le_pow₀ hz
  have htriangle := norm_sub_le ((a : ℂ) * z ^ d) (b : ℂ)
  have ht : ‖z‖ ^ d * ‖z‖ ≤ a * ‖z‖ ^ d + b := by
    rw [← norm_pow, ← norm_mul, ← pow_succ, hroot]
    simpa [norm_mul, norm_pow, Complex.norm_real, Real.norm_eq_abs,
      abs_of_nonneg ha, abs_of_nonneg hb] using htriangle
  have h1 : 0 ≤ b * (‖z‖ ^ d - 1) := mul_nonneg hb (by linarith)
  have h2 : 0 ≤ (‖z‖ ^ d) * (‖z‖ - 1) :=
    mul_nonneg (by positivity) (by linarith)
  have h3 : 0 < (‖z‖ ^ d) * (1 - (a + b)) :=
    mul_pos (by positivity) (by linarith)
  nlinarith

/-- The strict bound for the transverse complete-graph mode when there are at least
three nodes (`m` is the number of neighbours). This is a root statement only. -/
theorem complete_graph_transverse_root_inside (d m : ℕ) (z : ℂ) (h : ℝ)
    (hm : 2 ≤ m) (hh : 0 < h) (hmh : (m : ℝ) * h < 1)
    (hroot : z ^ (d + 1) = ((1 - (m : ℝ) * h : ℝ) : ℂ) * z ^ d - (h : ℂ)) :
    ‖z‖ < 1 := by
  have hmreal : (2 : ℝ) ≤ (m : ℝ) := by exact_mod_cast hm
  apply transverse_root_inside d z (1 - (m : ℝ) * h) h
  · linarith
  · linarith
  · nlinarith
  · exact hroot

/-- Weakening `a+b<1` to `a+b≤1` without other assumptions is false. -/
theorem nonstrict_boundary_counterexample :
    (0 : ℝ) + 1 ≤ 1 ∧
    (-1 : ℂ) ^ (0 + 1) = ((0 : ℝ) : ℂ) * (-1 : ℂ) ^ (0 : ℕ) - ((1 : ℝ) : ℂ) ∧
    ¬ ‖(-1 : ℂ)‖ < 1 := by
  norm_num

end AIEFGate.DelayRootBound
