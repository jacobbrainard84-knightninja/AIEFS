/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 380052e)
-/
import AIEFGateCore.DelayRoots
import Mathlib.Algebra.Polynomial.FieldDivision

/-!
# Simple neutral root of the delayed common-mode polynomial (Arena cycle 13)

Research candidate. `commonPoly d h = X^(d+1) - (1-h) X^d - h` over `ℂ` has the root `1`
for every `h`, with derivative `1 + d*h` there; for `h > 0` that root is simple, and for
`0 < h < 1` it is the only unit-circle root (location bound from `DelayRoots`).
Probes show both hypotheses are needed.
-/
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

/-- For 0<h<1, a unit-circle common-polynomial root is 1 and has
algebraic multiplicity one. The location bound comes from main DelayRoots. -/
theorem unit_circle_root_unique_and_simple (d : ℕ) (h : ℝ) (z : ℂ)
    (hh : 0 < h) (hh1 : h < 1)
    (hz : (commonPoly d h).IsRoot z) (hunit : ‖z‖ = 1) :
    z = 1 ∧ (commonPoly d h).rootMultiplicity z = 1 := by
  have hp : z ^ (d + 1) - ((1 - h : ℝ) : ℂ) * z ^ d - (h : ℂ) = 0 := by
    simpa [IsRoot, commonPoly] using hz
  rcases AIEFGate.DelayRoots.symRoot_eq_one_or_lt h hh hh1 d z hp with heq | hlt
  · subst z
    exact ⟨rfl, root_multiplicity_one d h hh⟩
  · exact False.elim ((ne_of_lt hlt) hunit)

/-- Exact boundary probe: dropping positivity permits a double root. -/
theorem negative_parameter_double_polynomial :
    commonPoly 1 (-1) = (X - 1) ^ 2 := by
  simp [commonPoly]
  ring

/-- The negative-parameter probe has algebraic multiplicity exactly two. -/
theorem negative_parameter_double_root :
    (commonPoly 1 (-1)).rootMultiplicity 1 = 2 := by
  rw [negative_parameter_double_polynomial]
  simpa using (rootMultiplicity_X_sub_C_pow (1 : ℂ) 2)

/-- At h=1, d=1, the other unit root rules out weakening h<1 to h≤1. -/
theorem upper_boundary_other_unit_root :
    (commonPoly 1 1).IsRoot (-1) ∧ ‖(-1 : ℂ)‖ = 1 ∧ (-1 : ℂ) ≠ 1 := by
  constructor
  · norm_num [IsRoot, commonPoly]
  · constructor <;> norm_num

/-- Exact coefficient/derivative probe for d=1, h=1/2. -/
theorem derivative_probe :
    (derivative (commonPoly 1 (1/2))).eval 1 = (3/2 : ℂ) := by
  rw [derivative_at_one]
  norm_num

/-! ### Value probes and negations used by the mutation harness (M110 ff.)

The value probes evaluate `commonPoly` at concrete data straight from the definition, so a
mutated `commonPoly` fails here and not only in a brittle rewrite lemma. -/

/-- `X^2 - (1/2) X - 1/2` at `2` is `5/2`. -/
theorem probe_commonPoly_eval_d1 : (commonPoly 1 (1/2)).eval 2 = (5/2 : ℂ) := by
  simp only [commonPoly, eval_sub, eval_mul, eval_pow, eval_X, eval_C]
  push_cast
  norm_num

/-- `X^3 - (1/2) X^2 - 1/2` at `2` is `11/2`. -/
theorem probe_commonPoly_eval_d2 : (commonPoly 2 (1/2)).eval 2 = (11/2 : ℂ) := by
  simp only [commonPoly, eval_sub, eval_mul, eval_pow, eval_X, eval_C]
  push_cast
  norm_num

/-- Dropping `0 < h` from `root_multiplicity_one` is false (`d = 1`, `h = -1`). -/
theorem false_multiplicity_no_pos :
    ¬ (∀ (d : ℕ) (h : ℝ) (_hh : True), (commonPoly d h).rootMultiplicity 1 = 1) := by
  intro H
  have h1 := H 1 (-1) trivial
  rw [negative_parameter_double_root] at h1
  omega

/-- Dropping `h < 1` from `unit_circle_root_unique_and_simple` is false
(`d = 1`, `h = 1`, `z = -1`). -/
theorem false_unit_root_no_upper :
    ¬ (∀ (d : ℕ) (h : ℝ) (z : ℂ) (_hh : 0 < h) (_hh1 : True)
      (_hz : (commonPoly d h).IsRoot z) (_hunit : ‖z‖ = 1),
      z = 1 ∧ (commonPoly d h).rootMultiplicity z = 1) := by
  intro H
  have h1 := (H 1 1 (-1) (by norm_num) trivial upper_boundary_other_unit_root.1
    upper_boundary_other_unit_root.2.1).1
  exact upper_boundary_other_unit_root.2.2 h1

/-- Dropping `0 < h` from `unit_circle_root_unique_and_simple` is false
(`d = 1`, `h = -1`, `z = 1`: a double root). -/
theorem false_unit_root_no_pos :
    ¬ (∀ (d : ℕ) (h : ℝ) (z : ℂ) (_hh : True) (_hh1 : h < 1)
      (_hz : (commonPoly d h).IsRoot z) (_hunit : ‖z‖ = 1),
      z = 1 ∧ (commonPoly d h).rootMultiplicity z = 1) := by
  intro H
  have h1 := (H 1 (-1) 1 trivial (by norm_num) (common_root 1 (-1)) (by norm_num)).2
  rw [negative_parameter_double_root] at h1
  omega

/-- The derivative at one is not `1 + h` (the delay factor matters: `d = 2`, `h = 1`). -/
theorem false_derivative_no_delay :
    ¬ (∀ (d : ℕ) (h : ℝ),
      (derivative (commonPoly d h)).eval 1 = (((1 + h : ℝ) : ℂ))) := by
  intro H
  have h1 := H 2 1
  rw [derivative_at_one] at h1
  norm_num at h1

end AIEFGate.CommonRootSimple

#print axioms AIEFGate.CommonRootSimple.common_root
#print axioms AIEFGate.CommonRootSimple.derivative_at_one
#print axioms AIEFGate.CommonRootSimple.root_multiplicity_one
#print axioms AIEFGate.CommonRootSimple.unit_circle_root_unique_and_simple
#print axioms AIEFGate.CommonRootSimple.negative_parameter_double_polynomial
#print axioms AIEFGate.CommonRootSimple.negative_parameter_double_root
#print axioms AIEFGate.CommonRootSimple.upper_boundary_other_unit_root
#print axioms AIEFGate.CommonRootSimple.derivative_probe
#print axioms AIEFGate.CommonRootSimple.probe_commonPoly_eval_d1
#print axioms AIEFGate.CommonRootSimple.probe_commonPoly_eval_d2
#print axioms AIEFGate.CommonRootSimple.false_multiplicity_no_pos
#print axioms AIEFGate.CommonRootSimple.false_unit_root_no_upper
#print axioms AIEFGate.CommonRootSimple.false_unit_root_no_pos
#print axioms AIEFGate.CommonRootSimple.false_derivative_no_delay
