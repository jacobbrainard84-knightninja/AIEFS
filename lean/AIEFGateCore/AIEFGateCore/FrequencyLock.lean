/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.PhaseCoherence

/-!
# Frequency lock and the delayed coherence EMA

Corrected restatement of cycles 3 and 5 of Arena_Researcher_06020041
(`PhaseLockCoherence.lean`, md5 `038cfbeb…`; `LockedCoherence.lean`, md5 `6554994d…`; both on
branch `audit-inbox`, not on `main`). Those files assumed `∀ n ≥ N, ∀ i, u n i = 0`: every phase
increment is zero, i.e. a **frozen** network. In the engine the natural frequencies average about
`1.43`, so increments are never zero and those theorems never apply. Auditor Seat 002 rated them
REWORK; this file is the rework, written by Auditor Seat 002 (not a copy of the deposit).

The hypothesis here is a **frequency lock**: from step `N` on, every node advances by the same
constant increment `c` (`∀ n ≥ N, ∀ i, u n i = c`). `c = 0` is the old frozen case.

* `input_step_of_common_increment`: if all nodes share the increment `c n` at step `n` and at the
  delayed step `n - d`, the input rotates by exactly `phasor (c n − c (n − d))`. So a common but
  time-varying rate still moves the input when `d > 0`; the delay is what breaks it.
* `common_rate_input_not_constant`: a concrete case of this (delay `1`, all nodes identical,
  increments alternating `π, 0, π, …`): the input flips sign every step. Locking in the sense
  "all nodes move together" is NOT enough with a delay; the rate must be constant.
* `coherenceInput_constant_of_frequencyLock`: under a frequency lock from `N`, the input is
  constant from `N + d` on (the first `d` steps after `N` still read pre-lock phases).
* `coherenceTrace_error_of_frequencyLock`: the EMA error then shrinks exactly geometrically:
  `C (N+d+k) − z = α^k (C (N+d) − z)` with `z` the locked input.
* `coherenceTrace_norm_of_frequencyLock` and `reported_of_frequencyLock`: with `0 ≤ α ≤ 1` and
  `‖C0‖ ≤ 1`, `‖C (N+d+k) i j‖ ≥ 1 − 2 α^k` and, off the diagonal, `reported ≥ 1 − 2 α^k`, so the
  reported coherence tends to `1`. At the engine's `α = exp(−dt / T_window)` (`dt = 0.01`,
  `T_window ≈ 17.503`, so `α ≈ 0.999429`) the bound passes `1/2` only after `k = 2427` steps.

Scope: exact reals. The frequency lock is ASSUMED, not derived from the closed-loop dynamics: this
does **not** prove that the engine locks (O1 stays open), and says nothing about `B`, float64, or
the Python code. `AUD-RATELAW stays UNEXPLAINED`.
-/

set_option autoImplicit false

namespace AIEFGate
namespace FrequencyLock

open AIEFGate.Phase AIEFGate.PhaseCoherence

variable {V : Type*}

noncomputable section

/-- With a common increment at step `n` and at the delayed step, the input rotates by the
difference of the two common increments (before the delay has elapsed, by `c n` alone). -/
theorem input_step_of_common_increment
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (c : ℕ → ℝ)
    (n : ℕ) (i j : V) (hn : u n i = c n) (hd : d ≤ n) (hnd : u (n - d) j = c (n - d)) :
    coherenceInput d x0 u omega tau (n + 1) i j =
      coherenceInput d x0 u omega tau n i j * phasor (c n - c (n - d)) := by
  simp only [coherenceInput]
  rw [delayed_input_step]
  simp only [delayedIncrement, if_pos hd, hn, hnd]

/-- Under a frequency lock from `N` (common constant increment `c`), the coherence input does
not change from `N + d` on. -/
theorem coherenceInput_step_of_frequencyLock
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (c : ℝ)
    (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = c)
    (n : ℕ) (hn : N + d ≤ n) (i j : V) :
    coherenceInput d x0 u omega tau (n + 1) i j = coherenceInput d x0 u omega tau n i j := by
  rw [input_step_of_common_increment d x0 u omega tau (fun _ => c) n i j
    (hlock n (by omega) i) (by omega) (hlock (n - d) (by omega) j)]
  simp [phasor]

theorem coherenceInput_constant_of_frequencyLock
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (c : ℝ)
    (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = c)
    (n : ℕ) (hn : N + d ≤ n) (i j : V) :
    coherenceInput d x0 u omega tau n i j = coherenceInput d x0 u omega tau (N + d) i j := by
  induction n, hn using Nat.le_induction with
  | base => rfl
  | succ n hn ih =>
      rw [coherenceInput_step_of_frequencyLock d x0 u omega tau c N hlock n hn i j, ih]

/-- Exact geometric EMA error under a frequency lock. -/
theorem coherenceTrace_error_of_frequencyLock
    (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ)
    (tau : ℝ) (c : ℝ) (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = c) (i j : V) (k : ℕ) :
    coherenceTrace alpha C0 d x0 u omega tau (N + d + k) i j -
        coherenceInput d x0 u omega tau (N + d) i j =
      (alpha : ℂ) ^ k * (coherenceTrace alpha C0 d x0 u omega tau (N + d) i j -
        coherenceInput d x0 u omega tau (N + d) i j) := by
  induction k with
  | zero => simp
  | succ k ih =>
      have hs : N + d + (k + 1) = (N + d + k) + 1 := by omega
      rw [hs]
      change coherenceStep alpha (coherenceTrace alpha C0 d x0 u omega tau (N + d + k)) d x0 u
          omega tau (N + d + k) i j - _ = _
      rw [coherenceStep,
        coherenceInput_constant_of_frequencyLock d x0 u omega tau c N hlock (N + d + k)
          (by omega) i j]
      have h : (alpha : ℂ) * coherenceTrace alpha C0 d x0 u omega tau (N + d + k) i j +
            ((1 - alpha : ℝ) : ℂ) * coherenceInput d x0 u omega tau (N + d) i j -
            coherenceInput d x0 u omega tau (N + d) i j =
          (alpha : ℂ) * (coherenceTrace alpha C0 d x0 u omega tau (N + d + k) i j -
            coherenceInput d x0 u omega tau (N + d) i j) := by
        push_cast; ring
      rw [h, ih, pow_succ]
      ring

/-- Under a frequency lock, `‖C (N+d+k) i j‖ ≥ 1 − 2 α^k`. -/
theorem coherenceTrace_norm_of_frequencyLock
    (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ)
    (tau : ℝ) (c : ℝ) (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = c)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1) (i j : V) (k : ℕ) :
    1 - 2 * alpha ^ k ≤ ‖coherenceTrace alpha C0 d x0 u omega tau (N + d + k) i j‖ := by
  set z := coherenceInput d x0 u omega tau (N + d) i j
  set C := coherenceTrace alpha C0 d x0 u omega tau
  have hz : ‖z‖ = 1 := input_norm d x0 u omega tau (N + d) i j
  have hCd : ‖C (N + d) i j‖ ≤ 1 :=
    coherenceTrace_unitDisk alpha C0 d x0 u omega tau ha0 ha1 hC (N + d) i j
  have herr := coherenceTrace_error_of_frequencyLock alpha C0 d x0 u omega tau c N hlock i j k
  have hak : ‖(alpha : ℂ) ^ k‖ = alpha ^ k := by
    rw [norm_pow, Complex.norm_of_nonneg ha0]
  have hdiff : ‖C (N + d + k) i j - z‖ ≤ alpha ^ k * 2 := by
    rw [herr, norm_mul, hak]
    apply mul_le_mul_of_nonneg_left _ (pow_nonneg ha0 k)
    calc ‖C (N + d) i j - z‖ ≤ ‖C (N + d) i j‖ + ‖z‖ := norm_sub_le _ _
      _ ≤ 2 := by rw [hz]; linarith
  have htri : ‖z‖ ≤ ‖C (N + d + k) i j‖ + ‖C (N + d + k) i j - z‖ := by
    calc ‖z‖ = ‖C (N + d + k) i j - (C (N + d + k) i j - z)‖ := by ring_nf
      _ ≤ ‖C (N + d + k) i j‖ + ‖C (N + d + k) i j - z‖ := norm_sub_le _ _
  linarith

/-- Under a frequency lock, the reported (symmetrised) coherence is at least `1 − 2 α^k`
off the diagonal, so it tends to `1`. -/
theorem reported_of_frequencyLock
    (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ)
    (tau : ℝ) (c : ℝ) (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = c)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1) {i j : V} (hij : i ≠ j)
    (k : ℕ) :
    1 - 2 * alpha ^ k ≤ reported (coherenceTrace alpha C0 d x0 u omega tau (N + d + k)) i j := by
  rw [reported_offdiag _ hij]
  have h1 := coherenceTrace_norm_of_frequencyLock alpha C0 d x0 u omega tau c N hlock ha0 ha1 hC
    i j k
  have h2 := coherenceTrace_norm_of_frequencyLock alpha C0 d x0 u omega tau c N hlock ha0 ha1 hC
    j i k
  linarith

/-! ### Witnesses -/

/-- The hypothesis is not the frozen case: at rate `1` (every node advances by `1` each step,
delay `3`) the input is constant from step `3` on. -/
theorem frequencyLock_nonzero_rate (x0 : Fin 2 → ℝ) (omega : Fin 2 → ℝ) (tau : ℝ) (n : ℕ)
    (hn : 3 ≤ n) (i j : Fin 2) :
    coherenceInput 3 x0 (fun _ _ => 1) omega tau n i j =
      coherenceInput 3 x0 (fun _ _ => 1) omega tau 3 i j :=
  coherenceInput_constant_of_frequencyLock 3 x0 (fun _ _ => 1) omega tau 1 0
    (fun _ _ _ => rfl) n (by omega) i j

/-- All nodes identical, rate alternating `π, 0, π, …`, delay `1`. -/
def altU (n : ℕ) (_ : Fin 2) : ℝ := if n % 2 = 0 then Real.pi else 0

/-- With a delay, a common but time-varying rate flips the input every step: the constant-rate
hypothesis cannot be weakened to "all nodes move together". -/
theorem common_rate_input_not_constant (n : ℕ) (hn : 1 ≤ n) :
    coherenceInput 1 (fun _ => 0) altU (fun _ => 0) 0 (n + 1) 0 1 =
      - coherenceInput 1 (fun _ => 0) altU (fun _ => 0) 0 n 0 1 := by
  rw [input_step_of_common_increment 1 (fun _ => 0) altU (fun _ => 0) 0
    (fun m => if m % 2 = 0 then Real.pi else 0) n 0 1 rfl hn rfl]
  have hpar : (n - 1) % 2 ≠ n % 2 := by omega
  have hp : phasor ((if n % 2 = 0 then Real.pi else 0) -
      (if (n - 1) % 2 = 0 then Real.pi else 0)) = -1 := by
    rcases Nat.mod_two_eq_zero_or_one n with h | h
    · have h' : (n - 1) % 2 = 1 := by omega
      simp [h, h', phasor, Complex.exp_pi_mul_I]
    · have h' : (n - 1) % 2 = 0 := by omega
      simp [h, h', phasor, Complex.exp_neg, Complex.exp_pi_mul_I]
  rw [hp, mul_neg_one]

theorem common_rate_input_ne_zero (n : ℕ) :
    coherenceInput 1 (fun _ => 0) altU (fun _ => 0) 0 n (0 : Fin 2) 1 ≠ 0 := by
  intro h
  have := input_norm 1 (fun _ => 0) altU (fun _ => 0) 0 n (0 : Fin 2) 1
  rw [h, norm_zero] at this
  exact zero_ne_one this

end

end FrequencyLock
end AIEFGate

#print axioms AIEFGate.FrequencyLock.input_step_of_common_increment
#print axioms AIEFGate.FrequencyLock.coherenceInput_constant_of_frequencyLock
#print axioms AIEFGate.FrequencyLock.coherenceTrace_error_of_frequencyLock
#print axioms AIEFGate.FrequencyLock.coherenceTrace_norm_of_frequencyLock
#print axioms AIEFGate.FrequencyLock.reported_of_frequencyLock
#print axioms AIEFGate.FrequencyLock.common_rate_input_not_constant
#print axioms AIEFGate.FrequencyLock.frequencyLock_nonzero_rate
