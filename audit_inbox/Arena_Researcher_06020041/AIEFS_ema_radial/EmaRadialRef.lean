/- SPDX-License-Identifier: Apache-2.0
Research candidate: normalized directed EMA magnitude directional derivative.
Not a proof of correspondence with Python or an adaptive network theorem. -/
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Deriv
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Analysis.Complex.Norm
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

set_option autoImplicit false
namespace AIEFGate.EmaRadialRef

/-- Real part of a prescribed EMA in coordinates normalized by a unit orbit
phasor. Compare aief_experiment_engine_v1.py at main
63e06d76bafa6d8e3627d31fbbbf5cb4499ae49d, lines 735–745. -/
noncomputable def reStep (alpha u delta t : ℝ) : ℝ :=
  alpha * (1 + t * u) + (1 - alpha) * Real.cos (t * delta)

/-- Imaginary part of the same prescribed normalized EMA. -/
noncomputable def imStep (alpha v delta t : ℝ) : ℝ :=
  alpha * (t * v) + (1 - alpha) * Real.sin (t * delta)

/-- Directed magnitude before the engine's symmetrization and diagonal mask;
compare aief_experiment_engine_v1.py, lines 747–750, at the cited main. -/
noncomputable def magnitude (alpha u v delta t : ℝ) : ℝ :=
  Real.sqrt ((reStep alpha u delta t) ^ 2 + (imStep alpha v delta t) ^ 2)

/-- At the base point the normalized updated EMA is exactly (1,0). -/
theorem base_value (alpha u v delta : ℝ) :
    reStep alpha u delta 0 = 1 ∧ imStep alpha v delta 0 = 0 := by
  simp [reStep, imStep]

theorem real_direction (alpha u delta : ℝ) :
    HasDerivAt (fun t => reStep alpha u delta t) (alpha * u) 0 := by
  have h1 := (hasDerivAt_const (0 : ℝ) (1 : ℝ)).fun_add
    ((hasDerivAt_id (0 : ℝ)).mul_const u)
  have h2 := ((hasDerivAt_id (0 : ℝ)).mul_const delta).cos
  have h := (h1.const_mul alpha).fun_add (h2.const_mul (1 - alpha))
  simpa [reStep] using h

theorem imag_direction (alpha v delta : ℝ) :
    HasDerivAt (fun t => imStep alpha v delta t) (alpha * v + (1 - alpha) * delta) 0 := by
  have h1 := (hasDerivAt_id (0 : ℝ)).mul_const v
  have h2 := ((hasDerivAt_id (0 : ℝ)).mul_const delta).sin
  have h := (h1.const_mul alpha).fun_add (h2.const_mul (1 - alpha))
  simpa [imStep] using h

/-- First-order response of normalized magnitude: phase/imaginary directions
have no contribution at unit coherence. All real alpha are allowed. -/
theorem magnitude_direction (alpha u v delta : ℝ) :
    HasDerivAt (fun t => magnitude alpha u v delta t) (alpha * u) 0 := by
  have hr := (real_direction alpha u delta).pow 2
  have hi := (imag_direction alpha v delta).pow 2
  have hsq := hr.fun_add hi
  have hsq' : HasDerivAt
      (fun t => (reStep alpha u delta t) ^ 2 + (imStep alpha v delta t) ^ 2)
      (2 * alpha * u) 0 := by
    apply hsq.congr_deriv
    simp [reStep, imStep]
    ring
  have hn : (reStep alpha u delta 0) ^ 2 + (imStep alpha v delta 0) ^ 2 ≠ 0 := by
    simp [reStep, imStep]
  have ht := hsq'.sqrt hn
  have hcancel : 2 * alpha * u / 2 = alpha * u := by ring
  simpa [magnitude, reStep, imStep, hcancel] using ht

/-- Exact complex norm of the real-component representation. -/
theorem complex_norm_eq (alpha u v delta t : ℝ) :
    ‖((reStep alpha u delta t : ℂ) + Complex.I * (imStep alpha v delta t : ℂ))‖ =
      magnitude alpha u v delta t := by
  simp [Complex.norm_def, Complex.normSq_apply, magnitude, pow_two]

/-- The same derivative stated directly for the complex norm. -/
theorem complex_norm_direction (alpha u v delta : ℝ) :
    HasDerivAt (fun t => ‖((reStep alpha u delta t : ℂ) +
      Complex.I * (imStep alpha v delta t : ℂ))‖) (alpha * u) 0 := by
  simpa only [complex_norm_eq] using magnitude_direction alpha u v delta

/-- Two directed magnitudes are averaged off diagonal, mirroring
    aief_experiment_engine_v1.py at main
    63e06d76bafa6d8e3627d31fbbbf5cb4499ae49d, lines 747–750. -/
noncomputable def symMagnitude (alpha u₁ v₁ delta₁ u₂ v₂ delta₂ t : ℝ) : ℝ :=
  (magnitude alpha u₁ v₁ delta₁ t + magnitude alpha u₂ v₂ delta₂ t) / 2

/-- Directional derivative after the off-diagonal average. -/
theorem sym_magnitude_direction (alpha u₁ v₁ delta₁ u₂ v₂ delta₂ : ℝ) :
    HasDerivAt (fun t => symMagnitude alpha u₁ v₁ delta₁ u₂ v₂ delta₂ t)
      (alpha * (u₁ + u₂) / 2) 0 := by
  have ht := ((magnitude_direction alpha u₁ v₁ delta₁).fun_add
    (magnitude_direction alpha u₂ v₂ delta₂)).div_const 2
  have heq : (alpha * u₁ + alpha * u₂) / 2 = alpha * (u₁ + u₂) / 2 := by ring
  simpa only [symMagnitude, heq] using ht

/-- Asymmetric radial directions average to three quarters at alpha=1/2. -/
theorem asymmetric_probe :
    HasDerivAt (fun t => symMagnitude (1/2) 1 3 7 2 5 11 t) (3/4) 0 := by
  have ht := sym_magnitude_direction (1/2) 1 3 7 2 5 11
  norm_num at ht ⊢
  exact ht

/-- Concrete probe: radial response is 1/2 even with nonzero phase and
imaginary directions. -/
theorem radial_probe : HasDerivAt (fun t => magnitude (1/2) 1 3 7 t) (1/2) 0 := by
  have ht := magnitude_direction (1/2) 1 3 7
  norm_num at ht ⊢
  exact ht

/-- Pure phase and imaginary perturbations have no first-order magnitude change. -/
theorem angular_probe : HasDerivAt (fun t => magnitude (1/2) 0 3 7 t) 0 0 := by
  have ht := magnitude_direction (1/2) 0 3 7
  norm_num at ht ⊢
  exact ht

#print axioms base_value
#print axioms real_direction
#print axioms imag_direction
#print axioms magnitude_direction
#print axioms complex_norm_eq
#print axioms complex_norm_direction
#print axioms sym_magnitude_direction
#print axioms asymmetric_probe
#print axioms radial_probe
#print axioms angular_probe

end AIEFGate.EmaRadialRef
