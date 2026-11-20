/-
Researcher040282: phase-specific coherence and drive on accepted010/011 inputs.
New file only. Imports unmodified main GateMap/MatrixForm and accepted history/
phase modules. Exact-real source convention, NOT Python/float FFI or locking.
Generic norm bounds do not identify a phase: exact innovations and probes below do.
-/
import AIEFGateCore.MatrixForm
import PhaseIncrement

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFGate.PhaseCoherence

open Complex
open scoped BigOperators


variable {V : Type*}

noncomputable section

/-- IMPLEMENTATION: the only input accepted by this coherence component. -/
def coherenceInput (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ)
    (tau : ℝ) (n : ℕ) (i j : V) : ℂ :=
  Researcher040282.Phase.inputPhasor d x0 u omega tau n i j

/-- Source clock: old read changes first on transition n=D to n=D+1. -/
def lateSource (d : ℕ) (u : ℕ → V → ℝ) (n : ℕ) (j : V) : ℝ :=
  if n < d then 0 else u (n - d) j

/-- Complex EMA updated BEFORE reported R, B and the phase step. -/
def coherenceStep (alpha : ℝ) (C : V → V → ℂ) (d : ℕ) (x0 : V → ℝ)
    (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) : ℂ :=
  (alpha : ℂ) * C i j + ((1 - alpha : ℝ) : ℂ) * coherenceInput d x0 u omega tau n i j

def coherenceTrace (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ)
    (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) : ℕ → V → V → ℂ
  | 0 => C0
  | n + 1 => coherenceStep alpha (coherenceTrace alpha C0 d x0 u omega tau n) d x0 u omega tau n

open Classical in
def reported (C : V → V → ℂ) (i j : V) : ℝ :=
  if i = j then 0 else (‖C i j‖ + ‖C j i‖) / 2

/-- IMPLEMENTATION: unnormalised drive accepted by main's preM/stepM. -/
def sourceDrive (eta mu : ℝ) (C : V → V → ℂ) (i j : V) : ℝ :=
  (eta + mu) * reported C i j - mu

/-- Exact source expression exp(i*dphi), with independent read-time n-D RHS.
Main has no phase state yet; this is an explicit source-convention extension,
not an assertion that an existing main phase model or Python FFI was proved. -/
theorem input_engine_convention (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
    (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) :
    coherenceInput d x0 u omega tau n i j =
      Complex.exp (Complex.I * ((Researcher040282.Phase.phaseTrace x0 u n i - Researcher040282.Phase.phaseTrace x0 u (n - d) j -
        ((omega i + omega j) / 2) * tau : ℝ) : ℂ)) := by
  simp only [coherenceInput, Researcher040282.Phase.inputPhasor, Researcher040282.Delay.historyTrace_oldest, Researcher040282.Phase.phasor]
  rw [mul_comm]

theorem input_norm (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ)
    (tau : ℝ) (n : ℕ) (i j : V) : ‖coherenceInput d x0 u omega tau n i j‖ = 1 := by
  rw [input_engine_convention]
  exact Complex.norm_exp_I_mul_ofReal _

/-- Absolute complex innovation, not just a magnitude or arbitrary-phase bound. -/
theorem innovation_engine_convention (alpha : ℝ) (C : V → V → ℂ)
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ)
    (tau : ℝ) (n : ℕ) (i j : V) :
    coherenceStep alpha C d x0 u omega tau n i j - (alpha : ℂ) * C i j =
      ((1 - alpha : ℝ) : ℂ) * Complex.exp (Complex.I *
        ((Researcher040282.Phase.phaseTrace x0 u n i - Researcher040282.Phase.phaseTrace x0 u (n - d) j -
          ((omega i + omega j) / 2) * tau : ℝ) : ℂ)) := by
  rw [coherenceStep, input_engine_convention]
  ring

theorem lateSource_startup (d : ℕ) (u : ℕ → V → ℝ) (n : ℕ) (j : V)
    (h : n < d) : lateSource d u n j = 0 := by simp [lateSource, h]

/-- Temporal transport of actual source-specific EMA innovations. -/
theorem innovation_transport (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) :
    coherenceTrace alpha C0 d x0 u omega tau (n + 2) i j -
        (alpha : ℂ) * coherenceTrace alpha C0 d x0 u omega tau (n + 1) i j =
      (coherenceTrace alpha C0 d x0 u omega tau (n + 1) i j -
        (alpha : ℂ) * coherenceTrace alpha C0 d x0 u omega tau n i j) *
          Researcher040282.Phase.phasor (u n i - lateSource d u n j) := by
  have hi (k : ℕ) :
      coherenceTrace alpha C0 d x0 u omega tau (k + 1) i j -
        (alpha : ℂ) * coherenceTrace alpha C0 d x0 u omega tau k i j =
          ((1 - alpha : ℝ) : ℂ) * coherenceInput d x0 u omega tau k i j := by
    change coherenceStep alpha (coherenceTrace alpha C0 d x0 u omega tau k) d x0 u omega tau k i j - _ = _
    unfold coherenceStep
    ring
  have hl : lateSource d u n j = Researcher040282.Phase.delayedIncrement d u n j := by
    by_cases h : d ≤ n
    · have hn : ¬n < d := by omega
      simp [lateSource, Researcher040282.Phase.delayedIncrement, h, hn]
    · have hn : n < d := by omega
      simp [lateSource, Researcher040282.Phase.delayedIncrement, h, hn]
  rw [show n + 2 = (n + 1) + 1 by omega, hi, hi, hl]
  simp only [coherenceInput, Researcher040282.Phase.delayed_input_step]
  ring

theorem coherenceTrace_unitDisk (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1) :
    ∀ n i j, ‖coherenceTrace alpha C0 d x0 u omega tau n i j‖ ≤ 1 := by
  intro n
  induction n with
  | zero => exact hC
  | succ n ih =>
      intro i j
      change ‖coherenceStep alpha (coherenceTrace alpha C0 d x0 u omega tau n) d x0 u omega tau n i j‖ ≤ 1
      calc
        _ ≤ ‖(alpha : ℂ) * coherenceTrace alpha C0 d x0 u omega tau n i j‖ +
              ‖((1 - alpha : ℝ) : ℂ) * coherenceInput d x0 u omega tau n i j‖ := norm_add_le _ _
        _ = alpha * ‖coherenceTrace alpha C0 d x0 u omega tau n i j‖ + (1 - alpha) := by
          rw [norm_mul, norm_mul, Complex.norm_of_nonneg ha0,
            Complex.norm_of_nonneg (sub_nonneg.mpr ha1), input_norm, mul_one]
        _ ≤ alpha * 1 + (1 - alpha) := add_le_add (mul_le_mul_of_nonneg_left (ih i j) ha0) le_rfl
        _ = 1 := by ring

theorem reported_bounds (C : V → V → ℂ) (hC : ∀ i j, ‖C i j‖ ≤ 1) (i j : V) :
    0 ≤ reported C i j ∧ reported C i j ≤ 1 := by
  classical
  unfold reported
  split_ifs
  · norm_num
  · constructor
    · positivity
    · have := hC i j
      have := hC j i
      linarith

theorem phase_drive_bounds (eta mu alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1)
    (hC : ∀ i j, ‖C0 i j‖ ≤ 1) (n : ℕ) (i j : V) :
    -mu ≤ sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j ∧
      sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j ≤ eta := by
  have hb := reported_bounds _ (coherenceTrace_unitDisk alpha C0 d x0 u omega tau ha0 ha1 hC (n + 1)) i j
  unfold sourceDrive
  constructor <;> nlinarith [mul_nonneg (add_nonneg heta hmu) hb.1,
    mul_le_mul_of_nonneg_left hb.2 (add_nonneg heta hmu)]

/-- Normalised004drive range on the actual phase-specific trajectory. -/
theorem phase_normalized_drive_bounds (p : AIEFGate.Params) (eta mu alpha : ℝ)
    (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
    (omega : V → ℝ) (tau : ℝ) (heta : 0 ≤ eta) (hmu : 0 ≤ mu)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1)
    (hg : 0 < p.γ) (n : ℕ) (i j : V) :
    -mu / p.γ ≤ sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j / p.γ ∧
      sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j / p.γ ≤ eta / p.γ := by
  have h := phase_drive_bounds eta mu alpha C0 d x0 u omega tau heta hmu ha0 ha1 hC n i j
  exact ⟨(div_le_div_iff_of_pos_right hg).2 h.1, (div_le_div_iff_of_pos_right hg).2 h.2⟩

/-- The old coarse degree envelope, now on the specified phase input.
This does NOT sharpen the N=12 future-band hypothesis. -/
theorem phase_positiveRow_bound [Fintype V] [DecidableEq V]
    (p : AIEFGate.Params) (eta mu alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ)
    (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1)
    (hC : ∀ i j, ‖C0 i j‖ ≤ 1) (hg : 0 < p.γ) (n : ℕ) (i : V) :
    (∑ j ∈ (Finset.univ : Finset V).erase i,
      max 0 (sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j / p.γ)) ≤
      ((Fintype.card V - 1 : ℕ) : ℝ) * (eta / p.γ) := by
  calc
    _ ≤ ∑ _j ∈ (Finset.univ : Finset V).erase i, eta / p.γ := by
      apply Finset.sum_le_sum
      intro j _
      exact max_le (div_nonneg heta hg.le)
        (phase_normalized_drive_bounds p eta mu alpha C0 d x0 u omega tau heta hmu ha0 ha1 hC hg n i j).2
    _ = _ := by simp

/-- Missing eta cannot survive this exact response, even if loose bounds survive. -/
theorem drive_eta_response (eta mu delta : ℝ) (C : V → V → ℂ) (i j : V) :
    sourceDrive (eta + delta) mu C i j - sourceDrive eta mu C i j = delta * reported C i j := by
  unfold sourceDrive
  ring

section MainInterface

/-- Actual current-main preM, not an old/private gate implementation. -/
theorem main_preM_source_formula (p : AIEFGate.Params) (eta mu : ℝ)
    (C : V → V → ℂ) (B : V → V → ℝ) (i j : V) :
    AIEFGate.MatrixForm.preM p (sourceDrive eta mu C) B i j =
      B i j + p.dt * ((eta + mu) * reported C i j - mu - p.γ * B i j) := by
  rfl
/-- After-coherence main interface, with no arbitrary phase/input parameter. -/
theorem main_phase_preM (p : AIEFGate.Params) (eta mu alpha : ℝ)
    (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
    (omega : V → ℝ) (tau : ℝ) (n : ℕ) (B : V → V → ℝ) (i j : V) :
    AIEFGate.MatrixForm.preM p
      (sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1))) B i j =
      B i j + p.dt * ((eta + mu) *
        reported (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j - mu - p.γ * B i j) := by
  rfl
end MainInterface

/-! Nonzero held probes, with source phase convention in their conclusions. -/
def probeX (_ : Fin 2) : ℝ := 0
def probeU (_ : ℕ) (_ : Fin 2) : ℝ := Real.pi / 2
def probeOmega (_ : Fin 2) : ℝ := 1
def probeC0 (_ _ : Fin 2) : ℂ := 1

private theorem reference_zero (d : ℕ) (i j : Fin 2) :
    Researcher040282.Phase.inputPhasor d probeX probeU probeOmega Real.pi 0 i j = -1 := by
  simp [Researcher040282.Phase.inputPhasor, Researcher040282.Delay.historyTrace, Researcher040282.Phase.phaseTrace, probeX, probeOmega, Researcher040282.Phase.phasor]

private theorem reference_step (d n : ℕ) (i j : Fin 2) :
    Researcher040282.Phase.inputPhasor d probeX probeU probeOmega Real.pi (n + 1) i j =
      Researcher040282.Phase.inputPhasor d probeX probeU probeOmega Real.pi n i j *
        (if n < d then Complex.I else 1) := by
  rw [Researcher040282.Phase.delayed_input_step]
  by_cases h : n < d
  · have hn : ¬d ≤ n := by omega
    simp [Researcher040282.Phase.delayedIncrement, hn, h, probeU, Researcher040282.Phase.phasor]
  · have hn : d ≤ n := by omega
    simp [Researcher040282.Phase.delayedIncrement, hn, h, probeU, Researcher040282.Phase.phasor]

private theorem reference_values (i j : Fin 2) :
    Researcher040282.Phase.inputPhasor 2 probeX probeU probeOmega Real.pi 0 i j = -1 ∧
    Researcher040282.Phase.inputPhasor 2 probeX probeU probeOmega Real.pi 1 i j = -Complex.I ∧
    Researcher040282.Phase.inputPhasor 2 probeX probeU probeOmega Real.pi 2 i j = 1 ∧
    Researcher040282.Phase.inputPhasor 2 probeX probeU probeOmega Real.pi 3 i j = 1 := by
  have h0 := reference_zero 2 i j
  have h1 := reference_step 2 0 i j
  have h2 := reference_step 2 1 i j
  have h3 := reference_step 2 2 i j
  norm_num at h1 h2 h3
  constructor
  · exact h0
  constructor
  · rw [h0] at h1; simpa using h1
  constructor
  · rw [h0] at h1
    rw [h1] at h2
    simpa using h2
  · rw [h0] at h1
    rw [h1] at h2
    simp at h2
    rw [h2] at h3
    simpa using h3

theorem probe_coherence_values (i j : Fin 2) :
    coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 1 i j = 0 ∧
    coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2 i j = -Complex.I/2 ∧
    coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 3 i j = 1/2-Complex.I/4 ∧
    coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 4 i j = 3/4-Complex.I/8 := by
  obtain ⟨h0,h1,h2,h3⟩ := reference_values i j
  refine ⟨?_, ?_, ?_, ?_⟩ <;>
    norm_num [coherenceTrace, coherenceStep, coherenceInput, probeC0, h0, h1, h2, h3] <;> ring

theorem probe_late_start : lateSource 2 probeU 1 (0 : Fin 2) = 0 := by
  norm_num [lateSource]

theorem probe_reported_second :
    reported (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2) (0 : Fin 2) 1 = 1/2 := by
  have h := fun i j => (probe_coherence_values i j).2.1
  norm_num [reported, h, Complex.norm_def, Complex.normSq]

theorem probe_drive_second :
    sourceDrive 2 1 (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2) (0 : Fin 2) 1 = 1/2 := by
  rw [sourceDrive, probe_reported_second]
  norm_num

/-! Independent explicit wrong-input values, not a claim that build errors suffice. -/
theorem wrong_delay_value :
    Researcher040282.Phase.inputPhasor 3 probeX probeU probeOmega Real.pi 3 (0 : Fin 2) 1 = Complex.I := by
  have h0 := reference_zero 3 (0 : Fin 2) 1
  have h1 := reference_step 3 0 (0 : Fin 2) 1
  have h2 := reference_step 3 1 (0 : Fin 2) 1
  have h3 := reference_step 3 2 (0 : Fin 2) 1
  norm_num at h1 h2 h3
  rw [h0] at h1
  rw [h1] at h2
  simp at h2
  rw [h2] at h3
  simpa using h3

theorem wrong_younger_value :
    Researcher040282.Phase.inputPhasor 1 probeX probeU probeOmega Real.pi 2 (0 : Fin 2) 1 = -Complex.I := by
  have h0 := reference_zero 1 (0 : Fin 2) 1
  have h1 := reference_step 1 0 (0 : Fin 2) 1
  have h2 := reference_step 1 1 (0 : Fin 2) 1
  norm_num at h1 h2
  rw [h0] at h1
  rw [h1] at h2
  simpa using h2

theorem wrong_current_value :
    Researcher040282.Phase.inputPhasor 0 probeX probeU probeOmega Real.pi 1 (0 : Fin 2) 1 = -1 := by
  have h := reference_step 0 0 (0 : Fin 2) 1
  simpa [reference_zero] using h

theorem wrong_offset_value :
    Researcher040282.Phase.inputPhasor 2 probeX probeU probeOmega 0 0 (0 : Fin 2) 1 = 1 := by
  simp [Researcher040282.Phase.inputPhasor, Researcher040282.Delay.historyTrace, Researcher040282.Phase.phaseTrace, probeX, Researcher040282.Phase.phasor]

theorem early_start_nonzero : probeU 0 (0 : Fin 2) ≠ 0 := by
  unfold probeU
  exact div_ne_zero Real.pi_ne_zero (by norm_num)

/-- Current-main parameter record for a nonzero pre-clip witness. -/
def probeParams : AIEFGate.Params where
  dt := Real.pi / 2
  γ := 1
  cap := 0
  ε := (10 ^ 12 : ℝ)⁻¹
  gapA := 1
  gapQ := 1
  gapDelta := 1

theorem probe_main_preM :
    AIEFGate.MatrixForm.preM probeParams
      (sourceDrive 2 1 (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2))
      (fun _ _ => 0) (0 : Fin 2) 1 = Real.pi / 4 := by
  simp only [AIEFGate.MatrixForm.preM, probe_drive_second, probeParams]
  ring

theorem wrong_delay_refuted :
    Researcher040282.Phase.inputPhasor 3 probeX probeU probeOmega Real.pi 3 (0 : Fin 2) 1 ≠
      coherenceInput 2 probeX probeU probeOmega Real.pi 3 0 1 := by
  rw [wrong_delay_value]
  have h := (reference_values (0 : Fin 2) 1).2.2.2
  rw [coherenceInput, h]
  norm_num [Complex.ext_iff]

theorem wrong_younger_refuted :
    Researcher040282.Phase.inputPhasor 1 probeX probeU probeOmega Real.pi 2 (0 : Fin 2) 1 ≠
      coherenceInput 2 probeX probeU probeOmega Real.pi 2 0 1 := by
  rw [wrong_younger_value]
  have h := (reference_values (0 : Fin 2) 1).2.2.1
  rw [coherenceInput, h]
  norm_num [Complex.ext_iff]

theorem wrong_current_refuted :
    Researcher040282.Phase.inputPhasor 0 probeX probeU probeOmega Real.pi 1 (0 : Fin 2) 1 ≠
      coherenceInput 2 probeX probeU probeOmega Real.pi 1 0 1 := by
  rw [wrong_current_value]
  have h := (reference_values (0 : Fin 2) 1).2.1
  rw [coherenceInput, h]
  norm_num [Complex.ext_iff]

theorem wrong_offset_refuted :
    Researcher040282.Phase.inputPhasor 2 probeX probeU probeOmega 0 0 (0 : Fin 2) 1 ≠
      coherenceInput 2 probeX probeU probeOmega Real.pi 0 0 1 := by
  rw [wrong_offset_value, coherenceInput, reference_zero]
  norm_num

theorem constant_phase_refuted :
    (1 / 2 : ℂ) * probeC0 0 1 + ((1 - 1/2 : ℝ) : ℂ) * Complex.exp 0 ≠
      coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 1 0 1 := by
  rw [(probe_coherence_values (0 : Fin 2) 1).1]
  norm_num [probeC0]

theorem missing_eta_refuted :
    (1 : ℝ) * reported (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2) (0 : Fin 2) 1 - 1 ≠
      sourceDrive 2 1 (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2) 0 1 := by
  rw [probe_reported_second, probe_drive_second]
  norm_num

end
end AIEFGate.PhaseCoherence

#print axioms AIEFGate.PhaseCoherence.input_engine_convention
#print axioms AIEFGate.PhaseCoherence.input_norm
#print axioms AIEFGate.PhaseCoherence.innovation_engine_convention
#print axioms AIEFGate.PhaseCoherence.lateSource_startup
#print axioms AIEFGate.PhaseCoherence.innovation_transport
#print axioms AIEFGate.PhaseCoherence.coherenceTrace_unitDisk
#print axioms AIEFGate.PhaseCoherence.reported_bounds
#print axioms AIEFGate.PhaseCoherence.phase_drive_bounds
#print axioms AIEFGate.PhaseCoherence.drive_eta_response
#print axioms AIEFGate.PhaseCoherence.main_preM_source_formula
#print axioms AIEFGate.PhaseCoherence.probe_coherence_values
#print axioms AIEFGate.PhaseCoherence.probe_late_start
#print axioms AIEFGate.PhaseCoherence.probe_reported_second
#print axioms AIEFGate.PhaseCoherence.probe_drive_second
#print axioms AIEFGate.PhaseCoherence.wrong_delay_value
#print axioms AIEFGate.PhaseCoherence.wrong_younger_value
#print axioms AIEFGate.PhaseCoherence.wrong_current_value
#print axioms AIEFGate.PhaseCoherence.wrong_offset_value
#print axioms AIEFGate.PhaseCoherence.early_start_nonzero

#print axioms AIEFGate.PhaseCoherence.phase_normalized_drive_bounds
#print axioms AIEFGate.PhaseCoherence.main_phase_preM

#print axioms AIEFGate.PhaseCoherence.phase_positiveRow_bound

#print axioms AIEFGate.PhaseCoherence.probe_main_preM

#print axioms AIEFGate.PhaseCoherence.wrong_delay_refuted

#print axioms AIEFGate.PhaseCoherence.wrong_younger_refuted

#print axioms AIEFGate.PhaseCoherence.wrong_current_refuted

#print axioms AIEFGate.PhaseCoherence.wrong_offset_refuted

#print axioms AIEFGate.PhaseCoherence.constant_phase_refuted

#print axioms AIEFGate.PhaseCoherence.missing_eta_refuted
