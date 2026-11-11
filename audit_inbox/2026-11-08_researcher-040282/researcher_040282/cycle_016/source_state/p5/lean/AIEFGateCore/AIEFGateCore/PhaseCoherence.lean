/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.MatrixForm
import AIEFGateCore.PhaseIncrement

/-!
# (P5) Phase-specific coherence EMA and drive on `Params` / `preM` / `stepM`

Port of `PhaseCoherenceBridge.lean` of cycle 013 of Researcher 040282 (handle only; the file was
supplied by the owner and is **not** on branch `audit-inbox`, md5
`410275adc4ea837a6384cefe2d545c2d`; its inputs, cycles 010 and 011, are on `audit-inbox` at
commit `1b5ae52`, see `HistoryBuffer.lean` and `PhaseIncrement.lean`). The definitions and
statements of the source are restated here on top of `AIEFGate.Phase.inputPhasor` and `main`'s
`Params`/`MatrixForm.preM`/`MatrixForm.stepM`; the proofs are those of the source, adapted.
Audited by Auditor Seat 002 (ADOPT WITH NOTES); the notes N1-N3 and N5 are applied here:

* N1: `reported_symm`, `reported_offdiag` and the asymmetric, node-dependent probe
  (`probe_asym_*`): with delay `D = 1`, increments `π/2` on node 0 and `0` on node 1 and zero
  initial coherence, `‖C 0 1‖ = √5/4 ≠ 3/4 = ‖C 1 0‖`, and the reported value is the average
  `(3 + √5)/8`, so the one-sided `‖C i j‖` is refuted.
* N2: `reported_diag` (`reported C i i = 0`) and `sourceDrive_diag`.
* N3: the former `wrong_*_refuted` lemmas are renamed `inputPhasor_*_differs`; they are facts about
  the function `Phase.inputPhasor` at other `d`/`τ`, **not** mutation evidence. The mutation
  evidence is in `research/lean_gate/lean_mutation_check.py` (M37 ff.), where a mutated
  *definition* of this file is elaborated and the pinned theorems must fail.
* N5: the asymmetric probe starts from `C0 = 0`, like the engine (`coherence_acc` is
  zero-initialised).

**Transcription is hand-checked, not proved against Python.** `coherenceInput` is read off
`aief_experiment_engine_v1.py` `compute_R` (about lines 735-751: `dphi = theta_i - delayed_j -
mean(omega) tau`, EMA `alpha C + (1 - alpha) z`, `abs`, symmetrisation `0.5 (R + R^T)`, zero
diagonal) and `reported`/`sourceDrive` off the `advance_state` drive (about lines 790-794:
`B + dt ((eta + mu) R - mu - gamma B)`). Main has no phase state; `input_engine_convention` is a
source-convention statement, not a proof about the Python code or float64.

Scope: exact reals. Not covered: the trajectory of `B` itself, phase locking, the clip/projection
(`np.maximum`, symmetrisation of `B`) and `shuffle_driver`.
-/

set_option autoImplicit false

namespace AIEFGate
namespace PhaseCoherence

open Complex
open AIEFGate.Phase AIEFGate.History
open scoped BigOperators

variable {V : Type*}

noncomputable section

/-- IMPLEMENTATION: the only input accepted by this coherence component. -/
def coherenceInput (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ)
    (tau : ℝ) (n : ℕ) (i j : V) : ℂ :=
  inputPhasor d x0 u omega tau n i j

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
      Complex.exp (Complex.I * ((phaseTrace x0 u n i - phaseTrace x0 u (n - d) j -
        ((omega i + omega j) / 2) * tau : ℝ) : ℂ)) := by
  simp only [coherenceInput, inputPhasor, historyTrace_oldest, phasor]
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
        ((phaseTrace x0 u n i - phaseTrace x0 u (n - d) j -
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
          phasor (u n i - lateSource d u n j) := by
  have hi (k : ℕ) :
      coherenceTrace alpha C0 d x0 u omega tau (k + 1) i j -
        (alpha : ℂ) * coherenceTrace alpha C0 d x0 u omega tau k i j =
          ((1 - alpha : ℝ) : ℂ) * coherenceInput d x0 u omega tau k i j := by
    change coherenceStep alpha (coherenceTrace alpha C0 d x0 u omega tau k) d x0 u omega tau k
      i j - _ = _
    unfold coherenceStep
    ring
  have hl : lateSource d u n j = delayedIncrement d u n j := by
    by_cases h : d ≤ n
    · have hn : ¬n < d := by omega
      simp [lateSource, delayedIncrement, h, hn]
    · have hn : n < d := by omega
      simp [lateSource, delayedIncrement, h, hn]
  rw [show n + 2 = (n + 1) + 1 by omega, hi, hi, hl]
  simp only [coherenceInput, delayed_input_step]
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
      change ‖coherenceStep alpha (coherenceTrace alpha C0 d x0 u omega tau n) d x0 u omega tau
        n i j‖ ≤ 1
      calc
        _ ≤ ‖(alpha : ℂ) * coherenceTrace alpha C0 d x0 u omega tau n i j‖ +
              ‖((1 - alpha : ℝ) : ℂ) * coherenceInput d x0 u omega tau n i j‖ :=
          norm_add_le _ _
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
  have hb := reported_bounds _
    (coherenceTrace_unitDisk alpha C0 d x0 u omega tau ha0 ha1 hC (n + 1)) i j
  unfold sourceDrive
  constructor <;> nlinarith [mul_nonneg (add_nonneg heta hmu) hb.1,
    mul_le_mul_of_nonneg_left hb.2 (add_nonneg heta hmu)]

/-- Normalised004drive range on the actual phase-specific trajectory. -/
theorem phase_normalized_drive_bounds (p : AIEFGate.Params) (eta mu alpha : ℝ)
    (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
    (omega : V → ℝ) (tau : ℝ) (heta : 0 ≤ eta) (hmu : 0 ≤ mu)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1)
    (hg : 0 < p.γ) (n : ℕ) (i j : V) :
    -mu / p.γ ≤
        sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j / p.γ ∧
      sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j / p.γ ≤
        eta / p.γ := by
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
        (phase_normalized_drive_bounds p eta mu alpha C0 d x0 u omega tau heta hmu ha0 ha1 hC hg
          n i j).2
    _ = _ := by simp

/-- Missing eta cannot survive this exact response, even if loose bounds survive. -/
theorem drive_eta_response (eta mu delta : ℝ) (C : V → V → ℂ) (i j : V) :
    sourceDrive (eta + delta) mu C i j - sourceDrive eta mu C i j = delta * reported C i j := by
  unfold sourceDrive
  ring

/-- (N2) The reported coherence has a zero diagonal (engine `fill_diagonal(R, 0)`). -/
theorem reported_diag (C : V → V → ℂ) (i : V) : reported C i i = 0 := by
  simp [reported]

/-- (N1) Off the diagonal the reported value is the average of the two directed magnitudes. -/
theorem reported_offdiag (C : V → V → ℂ) {i j : V} (h : i ≠ j) :
    reported C i j = (‖C i j‖ + ‖C j i‖) / 2 := by
  simp [reported, h]

/-- (N1) The reported coherence is symmetric (engine `0.5 * (R + R.T)`), although `C` need not
be. -/
theorem reported_symm (C : V → V → ℂ) (i j : V) : reported C i j = reported C j i := by
  by_cases h : i = j
  · subst h; rfl
  · rw [reported_offdiag C h, reported_offdiag C (Ne.symm h), add_comm]

theorem sourceDrive_diag (eta mu : ℝ) (C : V → V → ℂ) (i : V) : sourceDrive eta mu C i i = -mu := by
  simp [sourceDrive, reported_diag]

theorem sourceDrive_symm (eta mu : ℝ) (C : V → V → ℂ) (i j : V) :
    sourceDrive eta mu C i j = sourceDrive eta mu C j i := by
  simp only [sourceDrive, reported_symm C i j]

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

/-- The phase drive satisfies the symmetry hypothesis of `main`'s `stepM_eq_stepB`: the matrix
step with the phase-specific drive equals the edge-vector step. -/
theorem main_phase_stepM_eq_stepB [Fintype V] [LinearOrder V] (p : AIEFGate.Params)
    (eta mu alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ)
    (omega : V → ℝ) (tau : ℝ) (n : ℕ) (B : V → V → ℝ) (hB : ∀ i j, B i j = B j i)
    (e : AIEFGate.MatrixForm.CE V) :
    AIEFGate.MatrixForm.stepM p
        (sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1))) B e.1.1 e.1.2 =
      AIEFGate.stepB p (AIEFGate.MatrixForm.KG V)
        (AIEFGate.MatrixForm.toEdge
          (sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1))))
        (AIEFGate.MatrixForm.toEdge B) e :=
  AIEFGate.MatrixForm.stepM_eq_stepB p _ B (sourceDrive_symm _ _ _) hB e

end MainInterface

/-! Nonzero held probes (node-uniform, `C0 = 1`), with the source phase convention in their
conclusions. -/
def probeX (_ : Fin 2) : ℝ := 0
def probeU (_ : ℕ) (_ : Fin 2) : ℝ := Real.pi / 2
def probeOmega (_ : Fin 2) : ℝ := 1
def probeC0 (_ _ : Fin 2) : ℂ := 1

private theorem reference_zero (d : ℕ) (i j : Fin 2) :
    inputPhasor d probeX probeU probeOmega Real.pi 0 i j = -1 := by
  simp [inputPhasor, historyTrace, phaseTrace, probeX, probeOmega, phasor]

private theorem reference_step (d n : ℕ) (i j : Fin 2) :
    inputPhasor d probeX probeU probeOmega Real.pi (n + 1) i j =
      inputPhasor d probeX probeU probeOmega Real.pi n i j *
        (if n < d then Complex.I else 1) := by
  rw [delayed_input_step]
  by_cases h : n < d
  · have hn : ¬d ≤ n := by omega
    simp [delayedIncrement, hn, h, probeU, phasor]
  · have hn : d ≤ n := by omega
    simp [delayedIncrement, hn, h, probeU, phasor]

private theorem reference_values (i j : Fin 2) :
    inputPhasor 2 probeX probeU probeOmega Real.pi 0 i j = -1 ∧
    inputPhasor 2 probeX probeU probeOmega Real.pi 1 i j = -Complex.I ∧
    inputPhasor 2 probeX probeU probeOmega Real.pi 2 i j = 1 ∧
    inputPhasor 2 probeX probeU probeOmega Real.pi 3 i j = 1 := by
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
    norm_num at h2
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

/-- Value of the input at read time `0` with `ω = 1`, `τ = π` (nonzero offset
`(ω_i+ω_j)/2 · τ = π`): `exp(i (0 − 0 − π)) = −1`; with the offset dropped it would be `1`. -/
theorem probe_input_offset_value :
    coherenceInput 2 probeX probeU probeOmega Real.pi 0 0 1 = -1 := by
  simp [coherenceInput, inputPhasor, historyTrace, phaseTrace, probeX, probeOmega, phasor]

theorem probe_late_start : lateSource 2 probeU 1 (0 : Fin 2) = 0 := by
  norm_num [lateSource]

theorem probe_reported_second :
    reported (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2) (0 : Fin 2) 1 =
      1/2 := by
  have h := fun i j => (probe_coherence_values i j).2.1
  norm_num [reported, h, Complex.norm_def, Complex.normSq]

theorem probe_drive_second :
    sourceDrive 2 1 (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2) (0 : Fin 2)
      1 = 1/2 := by
  rw [sourceDrive, probe_reported_second]
  norm_num

/-! Facts about `Phase.inputPhasor` at other `d`/`τ` (and two arithmetic comparisons), compared
with the `d = 2` input of the held probe. They are facts about the function from cycle 011, NOT
evidence that a mutated implementation of this file is caught (see the mutation check, M37 ff.). -/
theorem inputPhasor_delay_three_value :
    inputPhasor 3 probeX probeU probeOmega Real.pi 3 (0 : Fin 2) 1 = Complex.I := by
  have h0 := reference_zero 3 (0 : Fin 2) 1
  have h1 := reference_step 3 0 (0 : Fin 2) 1
  have h2 := reference_step 3 1 (0 : Fin 2) 1
  have h3 := reference_step 3 2 (0 : Fin 2) 1
  norm_num at h1 h2 h3
  rw [h0] at h1
  rw [h1] at h2
  norm_num at h2
  rw [h2] at h3
  simpa using h3

theorem inputPhasor_delay_one_value :
    inputPhasor 1 probeX probeU probeOmega Real.pi 2 (0 : Fin 2) 1 = -Complex.I := by
  have h0 := reference_zero 1 (0 : Fin 2) 1
  have h1 := reference_step 1 0 (0 : Fin 2) 1
  have h2 := reference_step 1 1 (0 : Fin 2) 1
  norm_num at h1 h2
  rw [h0] at h1
  rw [h1] at h2
  simpa using h2

theorem inputPhasor_delay_zero_value :
    inputPhasor 0 probeX probeU probeOmega Real.pi 1 (0 : Fin 2) 1 = -1 := by
  have h := reference_step 0 0 (0 : Fin 2) 1
  simpa [reference_zero] using h

theorem inputPhasor_no_offset_value :
    inputPhasor 2 probeX probeU probeOmega 0 0 (0 : Fin 2) 1 = 1 := by
  simp [inputPhasor, historyTrace, phaseTrace, probeX, phasor]

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

theorem inputPhasor_delay_three_differs :
    inputPhasor 3 probeX probeU probeOmega Real.pi 3 (0 : Fin 2) 1 ≠
      coherenceInput 2 probeX probeU probeOmega Real.pi 3 0 1 := by
  rw [inputPhasor_delay_three_value]
  have h := (reference_values (0 : Fin 2) 1).2.2.2
  rw [coherenceInput, h]
  norm_num [Complex.ext_iff]

theorem inputPhasor_delay_one_differs :
    inputPhasor 1 probeX probeU probeOmega Real.pi 2 (0 : Fin 2) 1 ≠
      coherenceInput 2 probeX probeU probeOmega Real.pi 2 0 1 := by
  rw [inputPhasor_delay_one_value]
  have h := (reference_values (0 : Fin 2) 1).2.2.1
  rw [coherenceInput, h]
  norm_num [Complex.ext_iff]

theorem inputPhasor_delay_zero_differs :
    inputPhasor 0 probeX probeU probeOmega Real.pi 1 (0 : Fin 2) 1 ≠
      coherenceInput 2 probeX probeU probeOmega Real.pi 1 0 1 := by
  rw [inputPhasor_delay_zero_value]
  have h := (reference_values (0 : Fin 2) 1).2.1
  rw [coherenceInput, h]
  norm_num [Complex.ext_iff]

theorem inputPhasor_no_offset_differs :
    inputPhasor 2 probeX probeU probeOmega 0 0 (0 : Fin 2) 1 ≠
      coherenceInput 2 probeX probeU probeOmega Real.pi 0 0 1 := by
  rw [inputPhasor_no_offset_value, coherenceInput, reference_zero]
  norm_num

theorem constant_input_differs :
    (1 / 2 : ℂ) * probeC0 0 1 + ((1 - 1/2 : ℝ) : ℂ) * Complex.exp 0 ≠
      coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 1 0 1 := by
  rw [(probe_coherence_values (0 : Fin 2) 1).1]
  norm_num [probeC0]

theorem drive_without_eta_differs :
    (1 : ℝ) * reported (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2)
        (0 : Fin 2) 1 - 1 ≠
      sourceDrive 2 1 (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2) 0 1 := by
  rw [probe_reported_second, probe_drive_second]
  norm_num

/-! (N1, N5) Asymmetric, node-dependent probe with the engine's zero initial coherence.
`D = 1`, `x0 = 0`, `ω = 0`, `τ = 0`; node 0 advances by `π/2` per step, node 1 not at all, `C0 = 0`,
`α = 1/2`. Then `C₁ = 1/2` everywhere and `C₂ 0 j = 1/4 + i/2`, `C₂ 1 j = 3/4`, so the directed
magnitudes differ and the reported value must be their average. -/

def probeU2 (_ : ℕ) (i : Fin 2) : ℝ := if i = 0 then Real.pi / 2 else 0
def probeOmega0 (_ : Fin 2) : ℝ := 0
def probeC00 (_ _ : Fin 2) : ℂ := 0

private theorem asym_input_zero (i j : Fin 2) :
    inputPhasor 1 probeX probeU2 probeOmega0 0 0 i j = 1 := by
  simp [inputPhasor, historyTrace, phaseTrace, probeX, probeOmega0, phasor]

private theorem asym_input_one (i j : Fin 2) :
    inputPhasor 1 probeX probeU2 probeOmega0 0 1 i j = if i = 0 then Complex.I else 1 := by
  rw [delayed_input_step, asym_input_zero]
  fin_cases i <;> simp [delayedIncrement, probeU2, phasor]

theorem probe_asym_coherence_values (j : Fin 2) :
    (∀ i, coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 1 i j = 1/2) ∧
    coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 2 0 j = 1/4 + Complex.I/2 ∧
    coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 2 1 j = 3/4 := by
  have h1 := asym_input_one
  have h0 := asym_input_zero
  refine ⟨fun i => ?_, ?_, ?_⟩ <;>
    (norm_num [coherenceTrace, coherenceStep, coherenceInput, probeC00, h0, h1]; try ring)

/-- The two directed magnitudes differ on the asymmetric probe: `√5/4` against `3/4`. -/
theorem probe_asym_directed_magnitudes :
    ‖coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 2 0 1‖ = Real.sqrt 5 / 4 ∧
    ‖coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 2 1 0‖ = 3 / 4 := by
  obtain ⟨-, h01, h10⟩ := probe_asym_coherence_values 1
  obtain ⟨-, -, h10'⟩ := probe_asym_coherence_values 0
  rw [h01]
  rw [h10']
  constructor
  · rw [Complex.norm_def]
    have : Complex.normSq (1 / 4 + Complex.I / 2) = (Real.sqrt 5 / 4) ^ 2 := by
      rw [div_pow, Real.sq_sqrt (by norm_num)]
      simp [Complex.normSq_apply]
      norm_num
    rw [this, Real.sqrt_sq (by positivity)]
  · norm_num [Complex.norm_def, Complex.normSq]

theorem probe_asym_directed_ne :
    ‖coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 2 0 1‖ ≠
      ‖coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 2 1 0‖ := by
  rw [probe_asym_directed_magnitudes.1, probe_asym_directed_magnitudes.2]
  intro h
  have h5 : Real.sqrt 5 = 3 := by linarith
  have : (5 : ℝ) = 9 := by
    calc (5 : ℝ) = Real.sqrt 5 ^ 2 := (Real.sq_sqrt (by norm_num)).symm
      _ = 9 := by rw [h5]; norm_num
  norm_num at this

/-- (N1) The reported value is the symmetrised average `(3 + √5)/8`, strictly between the two
directed magnitudes; the one-sided `‖C i j‖` (`√5/4`) or `‖C j i‖` (`3/4`) is not it. Proved
directly from the definition of `reported` (not through `reported_offdiag`), so that a mutated
`reported` fails here as well. -/
theorem probe_asym_reported :
    reported (coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 2) (0 : Fin 2) 1 =
      (3 + Real.sqrt 5) / 8 := by
  unfold reported
  rw [if_neg (by decide), probe_asym_directed_magnitudes.1, probe_asym_directed_magnitudes.2]
  ring

theorem probe_asym_reported_swapped :
    reported (coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 2) (1 : Fin 2) 0 =
      (3 + Real.sqrt 5) / 8 := by
  unfold reported
  rw [if_neg (by decide), probe_asym_directed_magnitudes.1, probe_asym_directed_magnitudes.2]
  ring

theorem probe_asym_drive :
    sourceDrive 2 1 (coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 2) (0 : Fin 2)
      1 = 3 * ((3 + Real.sqrt 5) / 8) - 1 := by
  rw [sourceDrive, probe_asym_reported]
  ring

/-- The diagonal of the same trajectory is reported as `0`, although `C₂ 0 0 = 1/4 + i/2`. -/
theorem probe_asym_reported_diag :
    reported (coherenceTrace (1/2) probeC00 1 probeX probeU2 probeOmega0 0 2) (0 : Fin 2) 0 =
      0 := by
  unfold reported
  rw [if_pos rfl]

/-- `α = 1/2` is self-dual (`α = 1 - α`), so the probes above cannot see an `α ↔ 1 - α` swap;
with `α = 1/4` and `C0 = 0`, `C₁ = (1 - α) z₀ = 3/4` (a swap would give `1/4`). -/
theorem probe_alpha_quarter (i j : Fin 2) :
    coherenceTrace (1/4) probeC00 1 probeX probeU2 probeOmega0 0 1 i j = 3/4 := by
  have h0 := asym_input_zero
  norm_num [coherenceTrace, coherenceStep, coherenceInput, probeC00, h0]

end
end PhaseCoherence
end AIEFGate
