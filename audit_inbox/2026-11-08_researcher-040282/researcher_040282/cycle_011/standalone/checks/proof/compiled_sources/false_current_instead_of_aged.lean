import PhaseIncrement
open Researcher040282.Phase
noncomputable def controlX0 (_ : Unit) : ℝ := 0
noncomputable def controlOmega (_ : Unit) : ℝ := 0
noncomputable def controlU (n : ℕ) (_ : Unit) : ℝ := if n = 0 then Real.pi / 2 else Real.pi
example : inputPhasor 1 controlX0 controlU controlOmega 1 2 () () = inputPhasor 1 controlX0 controlU controlOmega 1 1 () () * phasor (controlU 1 () - controlU 1 ()) := by
  have hs : inputPhasor 1 controlX0 controlU controlOmega 1 1 () () = Complex.I := by
    have h0 : inputPhasor 1 controlX0 controlU controlOmega 1 0 () () = 1 := by
      simp [inputPhasor, Researcher040282.Delay.historyTrace, phaseTrace, controlX0, controlOmega, phasor]
    have hd : delayedIncrement 1 controlU 0 () = 0 := by simp [delayedIncrement]
    have hi : phasor (controlU 0 ()) = Complex.I := by simp [controlU, phasor]
    have h := delayed_input_step 1 controlX0 controlU controlOmega 1 0 () ()
    rw [h0, hd, sub_zero, one_mul, hi] at h
    exact h
  have hl : inputPhasor 1 controlX0 controlU controlOmega 1 2 () () = -1 := by
    have hs : inputPhasor 1 controlX0 controlU controlOmega 1 1 () () = Complex.I := by
      have h0 : inputPhasor 1 controlX0 controlU controlOmega 1 0 () () = 1 := by
        simp [inputPhasor, Researcher040282.Delay.historyTrace, phaseTrace, controlX0, controlOmega, phasor]
      have hd : delayedIncrement 1 controlU 0 () = 0 := by simp [delayedIncrement]
      have hi : phasor (controlU 0 ()) = Complex.I := by simp [controlU, phasor]
      have h := delayed_input_step 1 controlX0 controlU controlOmega 1 0 () ()
      rw [h0, hd, sub_zero, one_mul, hi] at h
      exact h
    have hi : phasor (controlU 1 () - delayedIncrement 1 controlU 1 ()) = Complex.I := by
      have hd : controlU 1 () - delayedIncrement 1 controlU 1 () = Real.pi / 2 := by
        dsimp [controlU, delayedIncrement]
        ring
      rw [hd]
      simp [phasor]
    have h := delayed_input_step 1 controlX0 controlU controlOmega 1 1 () ()
    rw [hs, hi, Complex.I_mul_I] at h
    exact h
  rw [hl, hs]
  norm_num [phasor, Complex.ext_iff]
