/-
Researcher040282: additive coherence/R movement bounds.
UNMERGED team P5 branch54037ea, approved branch scope; NOT current main.
Imports team module/namespace, no flat015imports or widened state model.
The coupled non-reset/history probe remains DEFERRED until the main port.
-/
import AIEFGateCore.PhaseCoherence

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFGate.CoherenceMotion

open scoped BigOperators

variable {V : Type*}

noncomputable section

/-- Observable wrapper only; no new state or new coherence recurrence. -/
def rTrace (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ)
    (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) : ℝ :=
  PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n) i j

section ValueProbes

def valueX (_ : Fin 2) : ℝ := 0
def valueU (_ : ℕ) (_ : Fin 2) : ℝ := 0
def valueOmega (_ : Fin 2) : ℝ := 1
def valueC (c : ℂ) (_ _ : Fin 2) : ℂ := c

private theorem value_phase_zero (n : ℕ) (i : Fin 2) :
    Phase.phaseTrace valueX valueU n i = 0 := by
  induction n with
  | zero => rfl
  | succ n ih =>
      change Phase.wrapPhase (Phase.phaseTrace valueX valueU n i + 0) = 0
      rw [ih]
      simp [Phase.wrapPhase]

private theorem value_input (n : ℕ) (i j : Fin 2) :
    PhaseCoherence.coherenceInput 1 valueX valueU valueOmega Real.pi n i j = -1 := by
  have he : Complex.exp (Complex.I * ((-Real.pi : ℝ) : ℂ)) = -1 := by
    have hh : Complex.I * ((-Real.pi : ℝ) : ℂ) = -((Real.pi : ℂ)*Complex.I) := by
      push_cast
      ring
    rw [hh]
    exact Complex.exp_neg_pi_mul_I
  rw [PhaseCoherence.input_engine_convention]
  simpa [value_phase_zero,valueOmega] using he

private theorem value_first (alpha : ℝ) (c : ℂ) (i j : Fin 2) :
    PhaseCoherence.coherenceTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi 1 i j =
      (alpha : ℂ)*c - ((1-alpha : ℝ) : ℂ) := by
  change (alpha : ℂ)*valueC c i j + ((1-alpha : ℝ) : ℂ)*
    PhaseCoherence.coherenceInput 1 valueX valueU valueOmega Real.pi 0 i j = _
  rw [value_input]
  unfold valueC
  ring

private theorem value_second (i j : Fin 2) :
    PhaseCoherence.coherenceTrace (3/4) (valueC 1) 1 valueX valueU valueOmega Real.pi 2 i j = 1/8 := by
  change ((3/4 : ℝ) : ℂ)*PhaseCoherence.coherenceTrace (3/4) (valueC 1) 1 valueX valueU valueOmega Real.pi 1 i j +
    ((1-3/4 : ℝ) : ℂ)*PhaseCoherence.coherenceInput 1 valueX valueU valueOmega Real.pi 1 i j = _
  rw [value_first,value_input]
  norm_num

/-- Probe shorthand only, not a new coherence/state model. -/
def Rval (alpha : ℝ) (c : ℂ) (n : ℕ) : ℝ :=
  rTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi n 0 1


private theorem fixed_R0 (alpha : ℝ) (c : ℂ) :
    PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi 0) (0 : Fin 2) 1 = ‖c‖ := by
  change PhaseCoherence.reported (valueC c) (0 : Fin 2) 1 = _
  rw [PhaseCoherence.reported_offdiag _ (by decide)]
  unfold valueC
  ring
private theorem fixed_R1 (alpha : ℝ) (c : ℂ) :
    PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi 1) (0 : Fin 2) 1 = ‖(alpha : ℂ)*c-((1-alpha : ℝ):ℂ)‖ := by
  rw [PhaseCoherence.reported_offdiag _ (by decide),value_first,value_first]
  ring
private theorem fixed_R2 :
    PhaseCoherence.reported (PhaseCoherence.coherenceTrace (3/4) (valueC 1) 1 valueX valueU valueOmega Real.pi 2) (0 : Fin 2) 1 = 1/8 := by
  rw [PhaseCoherence.reported_offdiag _ (by decide),value_second,value_second]
  norm_num [Complex.norm_def,Complex.normSq]

set_option linter.unusedSimpArgs false

theorem positive0 : Rval (1/2) 1 0 = 1 := by
  norm_num [Rval,rTrace,fixed_R0,fixed_R1,fixed_R2,Complex.norm_def,Complex.normSq]

theorem positive1 : Rval (1/2) 1 1 = 0 := by
  norm_num [Rval,rTrace,fixed_R0,fixed_R1,fixed_R2,Complex.norm_def,Complex.normSq]

theorem positive2 : Rval (1/2) 0 1 = 1/2 := by
  norm_num [Rval,rTrace,fixed_R0,fixed_R1,fixed_R2,Complex.norm_def,Complex.normSq]

theorem positive3 : Rval (-1) 1 1 = 3 := by
  norm_num [Rval,rTrace,fixed_R0,fixed_R1,fixed_R2,Complex.norm_def,Complex.normSq]

theorem positive4 : Rval 2 0 1 = 1 := by
  norm_num [Rval,rTrace,fixed_R0,fixed_R1,fixed_R2,Complex.norm_def,Complex.normSq]

theorem positive5 : Rval (1/2) 3 0 = 3 ∧ Rval (1/2) 3 1 = 1 := by
  norm_num [Rval,rTrace,fixed_R0,fixed_R1,fixed_R2,Complex.norm_def,Complex.normSq]

theorem positive6 : Rval (3/4) 1 2 = 1/8 := by
  norm_num [Rval,rTrace,fixed_R0,fixed_R1,fixed_R2,Complex.norm_def,Complex.normSq]

end ValueProbes
end
end AIEFGate.CoherenceMotion
