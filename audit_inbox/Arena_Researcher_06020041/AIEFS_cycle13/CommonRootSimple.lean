/- SPDX-License-Identifier: Apache-2.0
Research candidate: simple neutral root of a delayed common-mode polynomial. -/
import Mathlib.Algebra.Polynomial.FieldDivision
import Mathlib.Analysis.Complex.Norm
import Mathlib.Tactic

set_option autoImplicit false
namespace AIEFGate.CommonRootSimple
open Polynomial

noncomputable def commonPoly (d : ℕ) (h : ℝ) : Polynomial ℂ :=
  X ^ (d + 1) - C (((1 - h : ℝ) : ℂ)) * X ^ d - C (h : ℂ)

/-- One is a root for any real h and natural delay. -/
theorem common_root (d : ℕ) (h : ℝ) : (commonPoly d h).IsRoot 1 := by
  unfold IsRoot commonPoly
  simp only [eval_sub, eval_pow, eval_X, one_pow, eval_mul, eval_C]
  push_cast
  ring

/-- The exact derivative at the neutral root. -/
theorem derivative_at_one (d : ℕ) (h : ℝ) :
    (derivative (commonPoly d h)).eval 1 = (((1 + (d : ℝ) * h : ℝ) : ℂ)) := by
  simp [commonPoly, derivative_sub, derivative_mul, derivative_X_pow, eval_sub,
    eval_mul, eval_C, eval_pow, eval_X]
  ring

/-- Under h>0 the unit root has algebraic multiplicity exactly one. -/
theorem root_multiplicity_one (d : ℕ) (h : ℝ) (hh : 0 < h) :
    (commonPoly d h).rootMultiplicity 1 = 1 := by
  have hrpos : 0 < 1 + (d : ℝ) * h := by positivity
  have hdne : (derivative (commonPoly d h)).eval 1 ≠ 0 := by
    rw [derivative_at_one]
    exact_mod_cast (ne_of_gt hrpos)
  have hp : commonPoly d h ≠ 0 := by
    intro he
    apply hdne
    simp [he]
  have hroot := common_root d h
  have hpos : 0 < (commonPoly d h).rootMultiplicity 1 :=
    (rootMultiplicity_pos hp).2 hroot
  have hupper : ¬ 1 < (commonPoly d h).rootMultiplicity 1 := by
    intro ht
    have hder := ((one_lt_rootMultiplicity_iff_isRoot hp).1 ht).2
    exact hdne hder
  omega

end AIEFGate.CommonRootSimple
