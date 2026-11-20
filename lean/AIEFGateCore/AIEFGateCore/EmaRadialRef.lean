/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox db0638f)
-/
import AIEFGateCore.PhaseCoherence
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Deriv
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Analysis.Complex.Norm
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-!
# Directed EMA magnitude: directional derivative at unit coherence (Arena, audit-inbox db0638f)

Research candidate. Along the stipulated normalized path `old(t) = 1 + t(u + iv)`,
`input(t) = exp(i t δ)`, the updated EMA `α old + (1-α) input` has real-part derivative `αu`,
imaginary-part derivative `αv + (1-α)δ`, and magnitude derivative `αu` at `t = 0`; the
off-diagonal average of two such magnitudes has derivative `α(u₁+u₂)/2`.
`coherenceStep_eq_path` / `coherenceStep_norm_eq_magnitude` connect the path to
`PhaseCoherence.coherenceStep` under explicit hypotheses on the old EMA entry and the input
phasor (common unit phasor `p`). Unit coherence at the base point is a hypothesis: the engine's
EMA starts at `0` and only approaches unit modulus. Not an engine correspondence proof.
-/
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


/-! ### Bridge to `PhaseCoherence.coherenceStep` (added at intake) -/

/-- The EMA path as one complex number. -/
theorem path_eq (alpha u v delta t : ℝ) :
    ((reStep alpha u delta t : ℂ) + Complex.I * (imStep alpha v delta t : ℂ)) =
      (alpha : ℂ) * (1 + (t : ℂ) * ((u : ℂ) + Complex.I * (v : ℂ))) +
        ((1 - alpha : ℝ) : ℂ) * Complex.exp (Complex.I * ((t * delta : ℝ) : ℂ)) := by
  rw [mul_comm Complex.I ((t * delta : ℝ) : ℂ), Complex.exp_mul_I,
    ← Complex.ofReal_cos, ← Complex.ofReal_sin]
  apply Complex.ext <;> simp [reStep, imStep] <;> ring

/-- If the old EMA entry is `p * old(t)` and the input phasor is `p * exp(i t δ)`, then
`coherenceStep` is `p` times the stipulated path. -/
theorem coherenceStep_eq_path {V : Type*} (alpha : ℝ) (C : V → V → ℂ) (d : ℕ) (x0 : V → ℝ)
    (u0 : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) (p : ℂ)
    (u v delta t : ℝ)
    (hC : C i j = p * (1 + (t : ℂ) * ((u : ℂ) + Complex.I * (v : ℂ))))
    (hin : PhaseCoherence.coherenceInput d x0 u0 omega tau n i j =
      p * Complex.exp (Complex.I * ((t * delta : ℝ) : ℂ))) :
    PhaseCoherence.coherenceStep alpha C d x0 u0 omega tau n i j =
      p * ((reStep alpha u delta t : ℂ) + Complex.I * (imStep alpha v delta t : ℂ)) := by
  rw [path_eq, PhaseCoherence.coherenceStep, hC, hin]
  ring

/-- With a unit common phasor, the magnitude of `coherenceStep` is `magnitude`. -/
theorem coherenceStep_norm_eq_magnitude {V : Type*} (alpha : ℝ) (C : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u0 : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) (p : ℂ)
    (hp : ‖p‖ = 1) (u v delta t : ℝ)
    (hC : C i j = p * (1 + (t : ℂ) * ((u : ℂ) + Complex.I * (v : ℂ))))
    (hin : PhaseCoherence.coherenceInput d x0 u0 omega tau n i j =
      p * Complex.exp (Complex.I * ((t * delta : ℝ) : ℂ))) :
    ‖PhaseCoherence.coherenceStep alpha C d x0 u0 omega tau n i j‖ =
      magnitude alpha u v delta t := by
  rw [coherenceStep_eq_path alpha C d x0 u0 omega tau n i j p u v delta t hC hin, norm_mul, hp,
    one_mul, complex_norm_eq]

/-! ### Value probes and refutations (added at intake) -/

/-- Direct values: `reStep (1/2) 1 0 0 = 1`, `reStep (1/4) 2 0 1 = 3/2`. A sine for the input
cosine gives `1/2` at the first; `α` in place of `1-α` gives `1` at the second. -/
theorem probe_reStep_values : reStep (1/2) 1 0 0 = 1 ∧ reStep (1/4) 2 0 1 = 3/2 := by
  refine ⟨?_, ?_⟩ <;> norm_num [reStep]

/-- `imStep (1/2) 2 0 1 = 1`; a cosine for the input sine gives `3/2`. -/
theorem probe_imStep_value : imStep (1/2) 2 0 1 = 1 := by
  norm_num [imStep]

/-- `magnitude (1/2) 1 4 0 1 = 5/2` (real part `3/2`, imaginary part `2`). Dropping the square
root gives `25/4`; dropping the imaginary part gives `3/2`. -/
theorem probe_magnitude_value : magnitude (1/2) 1 4 0 1 = 5/2 := by
  rw [magnitude, show (reStep (1/2) 1 0 1) ^ 2 + (imStep (1/2) 4 0 1) ^ 2 = (5/2 : ℝ) ^ 2 by
    norm_num [reStep, imStep]]
  exact Real.sqrt_sq (by norm_num)

/-- `symMagnitude` of the directions `(1, 4, 0)` and `(-1, 0, 0)` at `t = 1` is
`(5/2 + 1/2)/2 = 3/2`; the first magnitude alone gives `5/2`, the sum without `/2` gives `3`. -/
theorem probe_symMagnitude_value : symMagnitude (1/2) 1 4 0 (-1) 0 0 1 = 3/2 := by
  have h2 : magnitude (1/2) (-1) 0 0 1 = 1/2 := by
    rw [magnitude, show (reStep (1/2) (-1) 0 1) ^ 2 + (imStep (1/2) 0 0 1) ^ 2 = (1/2 : ℝ) ^ 2 by
      norm_num [reStep, imStep]]
    exact Real.sqrt_sq (by norm_num)
  rw [symMagnitude, probe_magnitude_value, h2]
  norm_num

theorem false_real_no_alpha :
    ¬ (∀ alpha u delta : ℝ, HasDerivAt (fun t => reStep alpha u delta t) u 0) := by
  intro H
  have := (H 0 1 0).unique (real_direction 0 1 0)
  norm_num at this

theorem false_imag_no_input :
    ¬ (∀ alpha v delta : ℝ, HasDerivAt (fun t => imStep alpha v delta t) (alpha * v) 0) := by
  intro H
  have := (H 0 0 1).unique (imag_direction 0 0 1)
  norm_num at this

theorem false_magnitude_no_alpha :
    ¬ (∀ alpha u v delta : ℝ, HasDerivAt (fun t => magnitude alpha u v delta t) u 0) := by
  intro H
  have := (H (1/2) 1 0 0).unique (magnitude_direction (1/2) 1 0 0)
  norm_num at this

theorem false_magnitude_angular :
    ¬ (∀ alpha u v delta : ℝ, HasDerivAt (fun t => magnitude alpha u v delta t)
      (alpha * u + (1 - alpha) * delta) 0) := by
  intro H
  have := (H (1/2) 0 0 1).unique (magnitude_direction (1/2) 0 0 1)
  norm_num at this

theorem false_sym_first_only :
    ¬ (∀ alpha u₁ v₁ delta₁ u₂ v₂ delta₂ : ℝ,
      HasDerivAt (fun t => symMagnitude alpha u₁ v₁ delta₁ u₂ v₂ delta₂ t) (alpha * u₁) 0) := by
  intro H
  have := (H 1 0 0 0 2 0 0).unique (sym_magnitude_direction 1 0 0 0 2 0 0)
  norm_num at this

#print axioms path_eq
#print axioms coherenceStep_eq_path
#print axioms coherenceStep_norm_eq_magnitude
#print axioms probe_reStep_values
#print axioms probe_imStep_value
#print axioms probe_magnitude_value
#print axioms probe_symMagnitude_value
#print axioms false_real_no_alpha
#print axioms false_imag_no_input
#print axioms false_magnitude_no_alpha
#print axioms false_magnitude_angular
#print axioms false_sym_first_only

end AIEFGate.EmaRadialRef
