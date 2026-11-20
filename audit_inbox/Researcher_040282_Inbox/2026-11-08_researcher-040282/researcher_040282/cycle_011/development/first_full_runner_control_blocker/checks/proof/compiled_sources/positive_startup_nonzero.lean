import PhaseIncrement
open Researcher040282.Phase
noncomputable def controlX0 (_ : Unit) : ℝ := 0
noncomputable def controlOmega (_ : Unit) : ℝ := 0
noncomputable def controlU (n : ℕ) (_ : Unit) : ℝ := if n = 0 then Real.pi / 2 else Real.pi
theorem controlStartup : inputPhasor 1 controlX0 controlU controlOmega 1 1 () () = Complex.I := by
  have h0 : inputPhasor 1 controlX0 controlU controlOmega 1 0 () () = 1 := by
    simp [inputPhasor, Researcher040282.Delay.historyTrace_oldest, phaseTrace, controlX0, controlOmega, phasor]
  have hd : delayedIncrement 1 controlU 0 () = 0 := by simp [delayedIncrement]
  have hi : phasor (controlU 0 ()) = Complex.I := by simp [controlU, phasor]
  have h := delayed_input_step 1 controlX0 controlU controlOmega 1 0 () ()
  rw [h0, hd, sub_zero, one_mul, hi] at h
  exact h
#print axioms controlStartup
