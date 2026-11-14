/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.PhaseCoherence
import Mathlib.Analysis.Complex.Norm

/-!
# (Cycle 3) Phase-locked coherence — a phase/delay-dependent result

Unlike c016 `CoherenceMotion` (a speed limit that holds for any unit-norm input sequence),
these theorems use the actual phase trace and the delay queue: `inputPhasor` reads
`phaseTrace n i` and the oldest delayed phase `phaseTrace (n - d) j`.

1. `coherenceInput_constant_after_lock`: if the phase increments `u n i` vanish for all
   `n ≥ N`, then `coherenceInput` is constant from `N + d` on. The delay `d` sets the
   startup-to-live boundary. Proved from `Phase.delayed_input_step` and
   `Phase.delayedIncrement`.
2. `coherenceTrace_geometric_of_constant_input`: with a constant input `z`, the EMA error
   obeys `C_{n0+k} - z = α^k (C_{n0} - z)`; contraction requires `|α| < 1`.
3. `coherenceStep_norm_mono_of_aligned`: if the EMA state is aligned with the
   phase/delay-derived input `z` and has magnitude `r ≤ 1`, the next magnitude is at least
   `r` — a precise, conditional "R can only go up" statement.

Scope: exact reals; the locking hypothesis is ASSUMED, not derived from the closed-loop
dynamics. No float64, no Lean/Python equivalence, no claim that locking occurs, no
convergence of `B`, no phase-locking proof (O1 remains open). The `reported` symmetrisation
and zero diagonal are not used here; `AUD-RATELAW stays UNEXPLAINED`.
-/

set_option autoImplicit false

namespace AIEFGate
namespace PhaseLockCoherence

open scoped BigOperators

variable {V : Type*}

noncomputable section

/-- Phase increments vanish from `N` ⇒ the coherence input is constant from `N + d`.

The delay appears twice: in `delayedIncrement d u n j` (which reads `u (n - d)`) and in the
`N + d` boundary that guarantees `n - d ≥ N`. Dropping `+ d` makes the proof fail, so the
delay is genuinely used. -/
theorem coherenceInput_constant_after_lock
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = 0)
    (n : ℕ) (hn : N + d ≤ n) (i j : V) :
    PhaseCoherence.coherenceInput d x0 u omega tau (n + 1) i j =
      PhaseCoherence.coherenceInput d x0 u omega tau n i j := by
  simp only [PhaseCoherence.coherenceInput]
  rw [Phase.delayed_input_step]
  have hun : u n i = 0 := hlock n (by omega) i
  have hd : d ≤ n := by omega
  have hnd : N ≤ n - d := by omega
  have hud : u (n - d) j = 0 := hlock (n - d) hnd j
  have hdi : Phase.delayedIncrement d u n j = 0 := by
    simp [Phase.delayedIncrement, hd, hud]
  rw [hun, hdi]
  simp [Phase.phasor]

/-- EMA error contracts geometrically when the coherence input is constant `z` from `n0`. -/
theorem coherenceTrace_geometric_of_constant_input
    (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ)
    (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (n0 : ℕ) (z : ℂ) (i j : V)
    (hconst : ∀ n, n0 ≤ n →
      PhaseCoherence.coherenceInput d x0 u omega tau n i j = z) :
    ∀ k : ℕ,
      PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau (n0 + k) i j - z =
        (alpha : ℂ) ^ k *
          (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n0 i j - z) := by
  intro k
  induction k with
  | zero => simp
  | succ k ih =>
      have hn0 : n0 ≤ n0 + k := by omega
      have hs : n0 + (k + 1) = (n0 + k) + 1 := by omega
      rw [hs]
      simp only [PhaseCoherence.coherenceTrace]
      rw [PhaseCoherence.coherenceStep]
      rw [hconst (n0 + k) hn0]
      have hstep :
          (alpha : ℂ) *
              PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau (n0 + k) i j +
            ((1 - alpha : ℝ) : ℂ) * z - z =
          (alpha : ℂ) *
            (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau (n0 + k) i j - z) := by
        push_cast
        ring
      rw [hstep, ih]
      rw [pow_succ]
      ring

/-- If the directed EMA state at `(i,j)` is aligned
with the phase/delay-derived coherence input `z` and has magnitude `r ≤ 1`, the one-step
magnitude does not decrease.

Hypotheses are explicit: `0 ≤ alpha ≤ 1`, `0 ≤ r ≤ 1`, `‖z‖ = 1` (from `input_norm`),
and `C i j = (r : ℂ) * z`. No claim about `C j i`, the diagonal, `reported`, or later
steps. -/
theorem coherenceStep_norm_mono_of_aligned
    (alpha r : ℝ) (C : V → V → ℂ) (d : ℕ) (x0 : V → ℝ)
    (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hr0 : 0 ≤ r) (hr1 : r ≤ 1)
    (halign : C i j = (r : ℂ) * PhaseCoherence.coherenceInput d x0 u omega tau n i j) :
    ‖C i j‖ ≤ ‖PhaseCoherence.coherenceStep alpha C d x0 u omega tau n i j‖ := by
  let z : ℂ := PhaseCoherence.coherenceInput d x0 u omega tau n i j
  have hz : ‖z‖ = 1 := by
    simpa [z] using PhaseCoherence.input_norm d x0 u omega tau n i j
  have hC : C i j = (r : ℂ) * z := by simpa [z] using halign
  have hcoef_nonneg : 0 ≤ alpha * r + (1 - alpha) := by
    nlinarith [mul_nonneg ha0 hr0, sub_nonneg.mpr ha1]
  have hcoef_ge : r ≤ alpha * r + (1 - alpha) := by
    have hp : 0 ≤ (1 - alpha) * (1 - r) :=
      mul_nonneg (sub_nonneg.mpr ha1) (by linarith)
    nlinarith
  have hstep :
      (alpha : ℂ) * ((r : ℂ) * z) + ((1 - alpha : ℝ) : ℂ) * z =
        (((alpha * r + (1 - alpha) : ℝ) : ℂ)) * z := by
    push_cast
    ring
  have hnorm_r : ‖(r : ℂ)‖ = r := by
    have hsq := Complex.norm_mul_self_eq_normSq (r : ℂ)
    rw [Complex.normSq_ofReal] at hsq
    nlinarith [norm_nonneg (r : ℂ)]
  have hnorm_coef : ‖(((alpha * r + (1 - alpha) : ℝ) : ℂ))‖ =
      alpha * r + (1 - alpha) := by
    have hsq := Complex.norm_mul_self_eq_normSq
      (((alpha * r + (1 - alpha) : ℝ) : ℂ))
    rw [Complex.normSq_ofReal] at hsq
    nlinarith [norm_nonneg (((alpha * r + (1 - alpha) : ℝ) : ℂ))]
  rw [PhaseCoherence.coherenceStep, hC, hstep]
  calc
    ‖(r : ℂ) * z‖ = r := by
      rw [norm_mul, hnorm_r, hz, mul_one]
    _ ≤ alpha * r + (1 - alpha) := hcoef_ge
    _ = ‖(((alpha * r + (1 - alpha) : ℝ) : ℂ)) * z‖ := by
      rw [norm_mul, hnorm_coef, hz, mul_one]

end
end PhaseLockCoherence
end AIEFGate
