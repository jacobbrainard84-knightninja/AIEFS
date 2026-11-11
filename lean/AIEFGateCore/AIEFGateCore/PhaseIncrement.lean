/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.HistoryBuffer
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
import Mathlib.Algebra.Order.Archimedean.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

/-!
# (P5) Modulo-safe coherence-input motion for a delay queue, restated inside `AIEFGateCore`

Statements and proofs of `PhaseIncrement.lean` of cycle 011 of Researcher 040282 (handle only;
`audit_inbox/2026-11-08_researcher-040282/researcher_040282/cycle_011/proposal/PhaseIncrement.lean`
on branch `audit-inbox`, commit `1b5ae52`, md5 `b26f225f…`), moved into the namespace
`AIEFGate.Phase` on top of `AIEFGate.History` (`HistoryBuffer.lean`). Differences from the source:
namespace, the `History` import, docstrings; the three statements are checked textually by
`research/lean_gate/tests/test_lean_gate_p5.py`. Audited by Auditor Seat 002 (statements honest,
standard axioms).

* `phasor_wrap`: floor-based wrapping changes an angle only by a multiple of `2π`.
* `delayed_input_step`: `z_{n+1} = z_n · exp(i (u_n i − L_n j))` with `L_n = 0` for `n < D`,
  `u_{n−D}` for `n ≥ D`. Because the step is a ratio, the static offset `(ω_i + ω_j)/2 · τ`
  cancels: **these three theorems say nothing about the offset** (dropping it survives in this
  file; `PhaseCoherence.input_engine_convention` pins it).
* `delayed_input_chord_bound`: circular chord bound.

Scope: exact reals (no floating remainder, no allocation); arbitrary increments (possibly
feedback-generated); not the C/R/B evolution and not phase locking.
-/

set_option autoImplicit false

namespace AIEFGate
namespace Phase


variable {ι : Type*}

noncomputable def phasor (t : ℝ) : ℂ := Complex.exp ((t : ℂ) * Complex.I)

noncomputable def wrapPhase (t : ℝ) : ℝ :=
  t - (Int.floor (t / (2 * Real.pi)) : ℝ) * (2 * Real.pi)

noncomputable def phaseTrace (x0 : ι → ℝ) (u : ℕ → ι → ℝ) : ℕ → ι → ℝ
  | 0 => x0
  | n + 1 => fun i => wrapPhase (phaseTrace x0 u n i + u n i)

noncomputable def inputPhasor (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) : ℂ :=
  phasor (phaseTrace x0 u n i -
    AIEFGate.History.historyTrace d (phaseTrace x0 u) n ⟨0, Nat.zero_lt_succ d⟩ j -
    ((omega i + omega j) / 2) * tau)

noncomputable def delayedIncrement (d : ℕ) (u : ℕ → ι → ℝ) (n : ℕ) (j : ι) : ℝ :=
  if d ≤ n then u (n - d) j else 0

/-- Floor-based wrapping changes an angle only by an integer period. -/
theorem phasor_wrap (t : ℝ) : phasor (wrapPhase t) = phasor t := by
  unfold phasor wrapPhase
  push_cast
  rw [sub_mul, Complex.exp_sub, mul_assoc]
  simp only [Complex.exp_int_mul_two_pi_mul_I, div_one]

/-- Startup has zero delayed increment; the first live delayed increment is n=D. -/
theorem delayed_input_step (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) :
    inputPhasor d x0 u omega tau (n + 1) i j =
      inputPhasor d x0 u omega tau n i j *
        phasor (u n i - delayedIncrement d u n j) := by
  have hadd (a b : ℝ) : phasor (a + b) = phasor a * phasor b := by
    simp only [phasor, Complex.ofReal_add, add_mul, Complex.exp_add]
  have hsub (a b : ℝ) : phasor (a - b) = phasor a / phasor b := by
    simp only [phasor, Complex.ofReal_sub, sub_mul, Complex.exp_sub]
  have hstep (k : ℕ) (r : ι) :
      phasor (phaseTrace x0 u (k + 1) r) = phasor (phaseTrace x0 u k r) * phasor (u k r) := by
    change phasor (wrapPhase (phaseTrace x0 u k r + u k r)) = _
    rw [phasor_wrap, hadd]
  have hz : phasor 0 = 1 := by simp [phasor]
  simp only [inputPhasor, AIEFGate.History.historyTrace_oldest, hsub]
  by_cases hd : d ≤ n
  · have hs : n + 1 - d = (n - d) + 1 := by omega
    rw [hs, hstep, hstep]
    simp only [delayedIncrement, if_pos hd]
    field_simp [phasor, Complex.exp_ne_zero]
  · have h0 : n - d = 0 := by omega
    have h1 : n + 1 - d = 0 := by omega
    simp only [h0, h1, hstep, delayedIncrement, if_neg hd, hz, div_one]
    field_simp [phasor, Complex.exp_ne_zero]

/-- Circular chord bound, NOT a Euclidean difference of stored representatives. -/
theorem delayed_input_chord_bound (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) :
    ‖inputPhasor d x0 u omega tau (n + 1) i j - inputPhasor d x0 u omega tau n i j‖ ≤
      |u n i - delayedIncrement d u n j| := by
  rw [delayed_input_step]
  have heq : inputPhasor d x0 u omega tau n i j * phasor (u n i - delayedIncrement d u n j) -
      inputPhasor d x0 u omega tau n i j =
      inputPhasor d x0 u omega tau n i j *
        (phasor (u n i - delayedIncrement d u n j) - 1) := by ring
  rw [heq, norm_mul]
  have hnorm : ‖inputPhasor d x0 u omega tau n i j‖ = 1 := by
    unfold inputPhasor phasor
    exact Complex.norm_exp_ofReal_mul_I _
  rw [hnorm, one_mul]
  simpa only [phasor, mul_comm, Real.norm_eq_abs] using
    (Real.norm_exp_I_mul_ofReal_sub_one_le (x := u n i - delayedIncrement d u n j))

/-! (P5, audit fix) Closed-form VALUE probes of the two definitions the theorems above are about.
They are proved from the definitions (not through `delayed_input_step`), so that a mutated
definition fails here by its value, not only through a rewrite lemma. -/

/-- `delayedIncrement 2` of the increment sequence `u n = n + 1`: `0, 0, u 0, u 1`. -/
theorem probe_delayed_increment_values :
    delayedIncrement 2 (fun (n : ℕ) (_ : Unit) => (n : ℝ) + 1) 0 () = 0 ∧
    delayedIncrement 2 (fun (n : ℕ) (_ : Unit) => (n : ℝ) + 1) 1 () = 0 ∧
    delayedIncrement 2 (fun (n : ℕ) (_ : Unit) => (n : ℝ) + 1) 2 () = 1 ∧
    delayedIncrement 2 (fun (n : ℕ) (_ : Unit) => (n : ℝ) + 1) 3 () = 2 := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [delayedIncrement]

/-- One-step value of the input phasor with delay `D = 1`: node 0 advances by `π/2`, so
`z₁ 0 0 = exp(i (θ₁ 0 − θ₀ 0)) = i`; reading the newest slot would give `1`. -/
theorem probe_input_delay_values :
    inputPhasor 1 (fun _ : Fin 2 => (0 : ℝ)) (fun _ i => if i = 0 then Real.pi / 2 else 0)
      (fun _ => (0 : ℝ)) 0 1 0 0 = Complex.I := by
  have hw : wrapPhase (Real.pi / 2) = Real.pi / 2 := by
    unfold wrapPhase
    have h : Int.floor (Real.pi / 2 / (2 * Real.pi)) = 0 := by
      rw [Int.floor_eq_zero_iff, Set.mem_Ico]
      constructor
      · positivity
      · rw [div_lt_one (by positivity)]
        linarith [Real.pi_pos]
    rw [h]
    simp
  unfold inputPhasor
  rw [AIEFGate.History.historyTrace_oldest]
  simp [phaseTrace, hw, phasor]

/-- (N2) Asymmetric-`ω` value probe of the static offset `(ω_i + ω_j)/2 · τ`: `D = 1`, `x0 = 0`, no
increments, `τ = π`, `ω = (1, 0)` (the two nodes differ). The offset is the MEAN of the two natural
frequencies, so the input is `exp(−i π) = −1` for `(0,0)`, `exp(−i π/2) = −i` for both `(0,1)`
and `(1,0)`, and `1` for `(1,1)`. Using `ω_i` only, `ω_j` only, a node-uniform `ω`, or no offset
changes at least one of the four values. -/
theorem probe_input_asym_omega_value :
    inputPhasor 1 (fun _ : Fin 2 => (0 : ℝ)) (fun _ _ => (0 : ℝ))
      (fun i : Fin 2 => if i = 0 then (1 : ℝ) else 0) Real.pi 0 0 0 = -1 ∧
    inputPhasor 1 (fun _ : Fin 2 => (0 : ℝ)) (fun _ _ => (0 : ℝ))
      (fun i : Fin 2 => if i = 0 then (1 : ℝ) else 0) Real.pi 0 0 1 = -Complex.I ∧
    inputPhasor 1 (fun _ : Fin 2 => (0 : ℝ)) (fun _ _ => (0 : ℝ))
      (fun i : Fin 2 => if i = 0 then (1 : ℝ) else 0) Real.pi 0 1 0 = -Complex.I ∧
    inputPhasor 1 (fun _ : Fin 2 => (0 : ℝ)) (fun _ _ => (0 : ℝ))
      (fun i : Fin 2 => if i = 0 then (1 : ℝ) else 0) Real.pi 0 1 1 = 1 := by
  have hI : Complex.exp (2⁻¹ * (Real.pi : ℂ) * Complex.I) = Complex.I := by
    rw [show 2⁻¹ * (Real.pi : ℂ) * Complex.I = (Real.pi : ℂ) / 2 * Complex.I by ring]
    exact Complex.exp_pi_div_two_mul_I
  refine ⟨?_, ?_, ?_, ?_⟩ <;>
    (unfold inputPhasor; rw [AIEFGate.History.historyTrace_oldest];
     simp [phaseTrace, phasor, Complex.exp_neg, hI])

end Phase
end AIEFGate
