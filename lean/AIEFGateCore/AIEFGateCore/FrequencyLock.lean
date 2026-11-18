/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.PhaseCoherence

/-!
# Pairwise frequency lock and the delayed coherence EMA

Corrected restatement of cycles 3 and 5 of Arena_Researcher_06020041 (`PhaseLockCoherence.lean`, md5
`038cfbeb…`; `LockedCoherence.lean`, md5 `6554994d…`; both on branch `audit-inbox`, not on `main`).
Those files assumed `∀ n ≥ N, ∀ i, u n i = 0`: every phase increment is zero, i.e. a **frozen**
network. In the engine the natural frequencies average about `1.43`, so increments are never zero
and those theorems never apply. Auditor Seat 002 rated them REWORK; this file is the rework, written
by Auditor Seat 002 (not a copy of the deposit).

The hypothesis here is a **pairwise lock** of one pair `(i, j)`: from step `N` on, nodes `i` and `j`
advance by the same increment (`hlock : ∀ n ≥ N, u n i = c n ∧ u n j = c n`). Nothing is assumed
about any other node; the pair input `coherenceInput … i j` reads only `i` and `j`. `c = 0` is the
old frozen case.

* `input_step_of_common_increment`: if `u n i = c n`, `d ≤ n` and `u (n - d) j = c (n - d)`, the
  input rotates by exactly `phasor (c n − c (n − d))`.
* `coherenceInput_constant_of_periodicPairRate`: if the common rate of the pair repeats with period
  `d` (`c n = c (n − d)` for `n ≥ N + d`), the input is constant from `N + d` on. A constant rate
  (`coherenceInput_constant_of_pairLock`) is the simplest case, not the only one
  (`periodic_rate_input_constant`: delay `2`, rate `π, 0, π, 0, …`).
* `common_rate_input_not_constant`: "the pair moves together" is not enough: with delay `1` and the
  same rate `π, 0, π, …` the input flips sign every step. `c n = c (n − d)` is sufficient, not
  necessary: the exact condition is `c n ≡ c (n − d)` modulo `2π`.
* `coherenceTrace_error_of_pairLock`: under a constant pair lock the EMA error shrinks exactly
  geometrically, `C (N+d+k) i j − z = α^k (C (N+d) i j − z)` with `z` the locked input.
* `coherenceTrace_norm_of_pairLock` and `reported_of_pairLock`: with `0 ≤ α ≤ 1` and `‖C0‖ ≤ 1`,
  `‖C (N+d+k) i j‖ ≥ 1 − 2 α^k` and `reported ≥ 1 − 2 α^k` for that pair, so for `α < 1` its
  reported coherence tends to `1` (at `α = 1` the EMA never moves and the bound says nothing).
  (`α ≤ 1` is used through `coherenceTrace_unitDisk`; for `α > 1` the bound is trivially true
  anyway.) The factor `2` is attained (`pairLock_factor_two_refuted` refutes
  `1 − α^k`). At the engine's `α = exp(−dt / T_window)` (`dt = 0.01`, `T_window ≈ 17.503`,
  `α ≈ 0.999429`) `k = 2427` is the first `k` with `1 − 2 α^k > 1/2`; the error factor `α^k` itself
  is `≤ 1/2` from `k = 1214`.
* `pairLock_nonzero_rate`: the hypothesis is met at the nonzero rate `unitRate = 1`, so it is
  not only the frozen case.

How this relates to O1 (freezing/REPORT.md, cluster locking): O1 predicts that pairs inside a
frequency cluster lock (`R → 1`) and cross-cluster pairs stay below `R_c`. This file proves only the
first half's *consequence*: IF a pair is locked, its reported coherence tends to `1`. It does not
prove that any pair of the engine locks, and it says nothing about cross-cluster pairs.
`reported → 1` means a constant phase difference for the pair (phase-locking value `1`), not equal
phases.

Scope: exact reals. The lock is ASSUMED, not derived from the closed-loop dynamics; nothing about
`B`, float64, or the Python code. `AUD-RATELAW stays UNEXPLAINED`.
-/

set_option autoImplicit false

namespace AIEFGate
namespace FrequencyLock

open AIEFGate.Phase AIEFGate.PhaseCoherence

variable {V : Type*}

noncomputable section

/-- With a common increment at step `n` (node `i`) and at the delayed step (node `j`), the input
rotates by the difference of the two common increments. -/
theorem input_step_of_common_increment
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (c : ℕ → ℝ)
    (n : ℕ) (i j : V) (hn : u n i = c n) (hd : d ≤ n) (hnd : u (n - d) j = c (n - d)) :
    coherenceInput d x0 u omega tau (n + 1) i j =
      coherenceInput d x0 u omega tau n i j * phasor (c n - c (n - d)) := by
  simp only [coherenceInput]
  rw [delayed_input_step]
  simp only [delayedIncrement, if_pos hd, hn, hnd]

/-- A pair locked to a common rate that repeats with period `d` has a constant input from `N + d`
on. -/
theorem coherenceInput_constant_of_periodicPairRate
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (c : ℕ → ℝ)
    (N : ℕ) (i j : V) (hlock : ∀ n, N ≤ n → u n i = c n ∧ u n j = c n)
    (hper : ∀ n, N + d ≤ n → c n = c (n - d))
    (n : ℕ) (hn : N + d ≤ n) :
    coherenceInput d x0 u omega tau n i j = coherenceInput d x0 u omega tau (N + d) i j := by
  induction n, hn using Nat.le_induction with
  | base => rfl
  | succ n hn ih =>
      rw [input_step_of_common_increment d x0 u omega tau c n i j (hlock n (by omega)).1 (by omega)
        (hlock (n - d) (by omega)).2, ← hper n hn, sub_self, ih]
      simp [phasor]

/-- Constant pair lock (the simplest periodic rate): the input does not change from `N + d` on. -/
theorem coherenceInput_constant_of_pairLock
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (c : ℝ)
    (N : ℕ) (i j : V) (hlock : ∀ n, N ≤ n → u n i = c ∧ u n j = c)
    (n : ℕ) (hn : N + d ≤ n) :
    coherenceInput d x0 u omega tau n i j = coherenceInput d x0 u omega tau (N + d) i j :=
  coherenceInput_constant_of_periodicPairRate d x0 u omega tau (fun _ => c) N i j hlock
    (fun _ _ => rfl) n hn

/-- Exact geometric EMA error under a pair lock. -/
theorem coherenceTrace_error_of_pairLock
    (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ)
    (tau : ℝ) (c : ℝ) (N : ℕ) (i j : V) (hlock : ∀ n, N ≤ n → u n i = c ∧ u n j = c) (k : ℕ) :
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
        coherenceInput_constant_of_pairLock d x0 u omega tau c N i j hlock (N + d + k) (by omega)]
      have h : (alpha : ℂ) * coherenceTrace alpha C0 d x0 u omega tau (N + d + k) i j +
            ((1 - alpha : ℝ) : ℂ) * coherenceInput d x0 u omega tau (N + d) i j -
            coherenceInput d x0 u omega tau (N + d) i j =
          (alpha : ℂ) * (coherenceTrace alpha C0 d x0 u omega tau (N + d + k) i j -
            coherenceInput d x0 u omega tau (N + d) i j) := by
        push_cast; ring
      rw [h, ih, pow_succ]
      ring

/-- Under a pair lock, `‖C (N+d+k) i j‖ ≥ 1 − 2 α^k`. -/
theorem coherenceTrace_norm_of_pairLock
    (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ)
    (tau : ℝ) (c : ℝ) (N : ℕ) (i j : V) (hlock : ∀ n, N ≤ n → u n i = c ∧ u n j = c)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1) (k : ℕ) :
    1 - 2 * alpha ^ k ≤ ‖coherenceTrace alpha C0 d x0 u omega tau (N + d + k) i j‖ := by
  set z := coherenceInput d x0 u omega tau (N + d) i j
  set C := coherenceTrace alpha C0 d x0 u omega tau
  have hz : ‖z‖ = 1 := input_norm d x0 u omega tau (N + d) i j
  have hCd : ‖C (N + d) i j‖ ≤ 1 :=
    coherenceTrace_unitDisk alpha C0 d x0 u omega tau ha0 ha1 hC (N + d) i j
  have herr := coherenceTrace_error_of_pairLock alpha C0 d x0 u omega tau c N i j hlock k
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

/-- Under a pair lock, the reported (symmetrised) coherence of that pair is at least `1 − 2 α^k`, so
for `α < 1` it tends to `1`. -/
theorem reported_of_pairLock
    (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ)
    (tau : ℝ) (c : ℝ) (N : ℕ) {i j : V} (hij : i ≠ j)
    (hlock : ∀ n, N ≤ n → u n i = c ∧ u n j = c)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1) (k : ℕ) :
    1 - 2 * alpha ^ k ≤ reported (coherenceTrace alpha C0 d x0 u omega tau (N + d + k)) i j := by
  rw [reported_offdiag _ hij]
  have h1 := coherenceTrace_norm_of_pairLock alpha C0 d x0 u omega tau c N i j hlock ha0 ha1 hC k
  have h2 := coherenceTrace_norm_of_pairLock alpha C0 d x0 u omega tau c N j i
    (fun n hn => (hlock n hn).symm) ha0 ha1 hC k
  linarith

/-! ### Witnesses and refutations -/

/-- The constant rate `1` (the probe rate; not `0`, the frozen case). -/
def unitRate (_ : ℕ) (_ : Fin 2) : ℝ := 1

/-- Value probe: the witness rate is not the frozen rate `0`. -/
theorem probe_unitRate_nonzero : unitRate 0 0 ≠ 0 := by norm_num [unitRate]

/-- The hypothesis is not only the frozen case: at the rate `unitRate = 1 ≠ 0` (delay `3`) it holds
and the input is constant from step `3` on. -/
theorem pairLock_nonzero_rate (x0 : Fin 2 → ℝ) (omega : Fin 2 → ℝ) (tau : ℝ) :
    unitRate 0 0 ≠ 0 ∧ ∀ n, 3 ≤ n → ∀ i j : Fin 2,
      coherenceInput 3 x0 unitRate omega tau n i j =
        coherenceInput 3 x0 unitRate omega tau 3 i j := by
  refine ⟨by norm_num [unitRate], fun n hn i j => ?_⟩
  exact coherenceInput_constant_of_pairLock 3 x0 unitRate omega tau (unitRate 0 0) 0 i j
    (fun _ _ => ⟨rfl, rfl⟩) n (by omega)

/-- Both nodes identical, rate alternating `π, 0, π, …`. -/
def altU (n : ℕ) (_ : Fin 2) : ℝ := if n % 2 = 0 then Real.pi else 0

/-- With delay `1`, a common but time-varying rate flips the input every step: "the pair moves
together" is not enough; a shared rate that does not repeat with period `d` (modulo `2π`) can
flip it. -/
theorem common_rate_input_not_constant (n : ℕ) (hn : 1 ≤ n) :
    coherenceInput 1 (fun _ => 0) altU (fun _ => 0) 0 (n + 1) 0 1 =
      - coherenceInput 1 (fun _ => 0) altU (fun _ => 0) 0 n 0 1 := by
  rw [input_step_of_common_increment 1 (fun _ => 0) altU (fun _ => 0) 0
    (fun m => if m % 2 = 0 then Real.pi else 0) n 0 1 rfl hn rfl]
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

/-- The same non-constant rate `π, 0, π, …` with delay `2` (period `2`) keeps the input constant
from step `2` on: a constant rate is not required. -/
theorem periodic_rate_input_constant (n : ℕ) (hn : 2 ≤ n) :
    coherenceInput 2 (fun _ => 0) altU (fun _ => 0) 0 n 0 1 =
      coherenceInput 2 (fun _ => 0) altU (fun _ => 0) 0 2 0 1 :=
  coherenceInput_constant_of_periodicPairRate 2 (fun _ => 0) altU (fun _ => 0) 0
    (fun m => if m % 2 = 0 then Real.pi else 0) 0 0 1 (fun _ _ => ⟨rfl, rfl⟩)
    (fun m hm => by
      have h : (m - 2) % 2 = m % 2 := by omega
      simp only [h]) n (by omega)

/-- `altU` is not a constant rate. -/
theorem probe_altU_not_constant : altU 0 0 ≠ altU 1 0 := by
  simp [altU, Real.pi_ne_zero]

/-- `altU` has period `2` and is the same at both nodes (value probe for
`periodic_rate_input_constant` and `common_rate_input_not_constant`). -/
theorem probe_altU_period_two : altU 2 1 = altU 0 0 ∧ altU 3 1 = altU 1 0 := by
  simp [altU]

/-- `unitRate` is the same at every step and node (value probe for `pairLock_nonzero_rate`). -/
theorem probe_unitRate_constant : unitRate 7 1 = unitRate 0 0 := by
  simp [unitRate]

/-- The values of `altU` at steps `0` and `1` (value probe, Researcher 001's #41 note 1:
without it an `altU` with `Real.pi / 2` in place of `Real.pi` passed every probe). -/
theorem probe_altU_values : altU 0 0 = Real.pi ∧ altU 1 0 = 0 := by
  simp [altU]

/-- Dropping the period condition is false: delay `1`, rate `π, 0, π, …`, the input at `2` is minus
the input at `1`, so it is not constant from `N + d = 1`. -/
theorem nonperiodic_rate_refuted :
    coherenceInput 1 (fun _ => 0) altU (fun _ => 0) 0 2 0 1 ≠
      coherenceInput 1 (fun _ => 0) altU (fun _ => 0) 0 (0 + 1) 0 1 := by
  rw [common_rate_input_not_constant 1 le_rfl]
  intro h
  have h2 : coherenceInput 1 (fun _ => 0) altU (fun _ => 0) 0 1 (0 : Fin 2) 1 = 0 := by
    linear_combination (-(1 : ℂ) / 2) * h
  exact common_rate_input_ne_zero 1 h2

/-- Lock probe: rate `π/2` on both nodes (`probeU`), delay `0`, `C0 = 1`, `α = 1/2`, so the locked
input is `z = −1` and `C 1 = 1/2 − 1/2 = 0`; the bound `1 − 2 (1/2)^1 = 0` is attained. -/
theorem probe_pairLock_one_step :
    coherenceTrace (1/2) probeC0 0 probeX probeU probeOmega Real.pi (0 + 0 + 1) 0 1 = 0 ∧
    reported (coherenceTrace (1/2) probeC0 0 probeX probeU probeOmega Real.pi (0 + 0 + 1)) 0 1
      = 0 := by
  have hz : ∀ i j : Fin 2, coherenceInput 0 probeX probeU probeOmega Real.pi 0 i j = -1 := by
    intro i j
    simp [coherenceInput, inputPhasor, History.historyTrace, phaseTrace, probeX, probeOmega, phasor]
  have hc : ∀ i j : Fin 2,
      coherenceTrace (1/2) probeC0 0 probeX probeU probeOmega Real.pi 1 i j = 0 := by
    intro i j
    change ((1/2 : ℝ) : ℂ) * probeC0 i j + ((1 - 1/2 : ℝ) : ℂ) *
      coherenceInput 0 probeX probeU probeOmega Real.pi 0 i j = 0
    rw [hz]
    norm_num [probeC0]
  refine ⟨hc 0 1, ?_⟩
  rw [reported_offdiag _ (by decide : (0 : Fin 2) ≠ 1), hc 0 1, hc 1 0]
  simp

/-- `1 − α^k` (factor `2` dropped) is false: at the lock probe it would claim `1/2 ≤ 0`. -/
theorem pairLock_factor_two_refuted :
    ¬ (1 - (1/2 : ℝ) ^ 1 ≤
      reported (coherenceTrace (1/2) probeC0 0 probeX probeU probeOmega Real.pi (0 + 0 + 1))
        0 1) := by
  rw [probe_pairLock_one_step.2]
  norm_num

/-- Same, for the norm form. -/
theorem pairLock_norm_factor_two_refuted :
    ¬ (1 - (1/2 : ℝ) ^ 1 ≤
      ‖coherenceTrace (1/2) probeC0 0 probeX probeU probeOmega Real.pi (0 + 0 + 1) 0 1‖) := by
  rw [probe_pairLock_one_step.1]
  norm_num

/-- Node `0` at rate `π`, node `1` at rate `0`. -/
def splitU (_ : ℕ) (i : Fin 2) : ℝ := if i = 0 then Real.pi else 0

/-- Locking node `i` alone is not enough: with `j` at another rate the input moves (delay `0`). -/
theorem half_lock_refuted :
    coherenceInput 0 (fun _ => 0) splitU (fun _ => 0) 0 1 0 1 ≠
      coherenceInput 0 (fun _ => 0) splitU (fun _ => 0) 0 (0 + 0) 0 1 := by
  intro h
  have hs : coherenceInput 0 (fun _ => 0) splitU (fun _ => 0) 0 1 0 1 =
      coherenceInput 0 (fun _ => 0) splitU (fun _ => 0) 0 0 0 1 * phasor (Real.pi - 0) := by
    simp only [coherenceInput]
    rw [delayed_input_step]
    simp [delayedIncrement, splitU]
  have hp : phasor (Real.pi - 0) = -1 := by simp [phasor, Complex.exp_pi_mul_I]
  have hne := input_norm 0 (fun _ => 0) splitU (fun _ => 0) 0 0 (0 : Fin 2) 1
  rw [hs, hp] at h
  simp only [Nat.add_zero] at h
  have h2 : coherenceInput 0 (fun _ => 0) splitU (fun _ => 0) 0 0 (0 : Fin 2) 1 = 0 := by
    linear_combination (-(1 : ℂ) / 2) * h
  rw [h2, norm_zero] at hne
  exact zero_ne_one hne

/-- Claiming the constant input already from `N` (not `N + d`) is false: delay `2`, rate `π/2`, the
input at `0` is `−1` but at `2` it is `1`. -/
theorem delay_start_refuted :
    coherenceInput 2 probeX probeU probeOmega Real.pi 0 0 1 ≠
      coherenceInput 2 probeX probeU probeOmega Real.pi (0 + 2) 0 1 := by
  have h0 : coherenceInput 2 probeX probeU probeOmega Real.pi 0 0 1 = -1 := by
    simp [coherenceInput, inputPhasor, History.historyTrace, phaseTrace, probeX, probeOmega, phasor]
  have hs : ∀ n, coherenceInput 2 probeX probeU probeOmega Real.pi (n + 1) 0 1 =
      coherenceInput 2 probeX probeU probeOmega Real.pi n 0 1 *
        phasor (probeU n 0 - delayedIncrement 2 probeU n 1) := by
    intro n
    simp only [coherenceInput]
    rw [delayed_input_step]
  have h2 : coherenceInput 2 probeX probeU probeOmega Real.pi (0 + 2) 0 1 = 1 := by
    rw [show (0 + 2 : ℕ) = 1 + 1 from rfl, hs 1, hs 0, h0]
    have hi : phasor (Real.pi / 2) = Complex.I := by
      simp [phasor, Complex.exp_mul_I, Complex.cos_pi_div_two, Complex.sin_pi_div_two]
    simp [delayedIncrement, probeU, hi]
  rw [h0, h2]
  norm_num

end

end FrequencyLock
end AIEFGate

#print axioms AIEFGate.FrequencyLock.input_step_of_common_increment
#print axioms AIEFGate.FrequencyLock.coherenceInput_constant_of_periodicPairRate
#print axioms AIEFGate.FrequencyLock.coherenceInput_constant_of_pairLock
#print axioms AIEFGate.FrequencyLock.coherenceTrace_error_of_pairLock
#print axioms AIEFGate.FrequencyLock.coherenceTrace_norm_of_pairLock
#print axioms AIEFGate.FrequencyLock.reported_of_pairLock
#print axioms AIEFGate.FrequencyLock.pairLock_nonzero_rate
#print axioms AIEFGate.FrequencyLock.probe_unitRate_nonzero
#print axioms AIEFGate.FrequencyLock.common_rate_input_not_constant
#print axioms AIEFGate.FrequencyLock.periodic_rate_input_constant
#print axioms AIEFGate.FrequencyLock.probe_altU_not_constant
#print axioms AIEFGate.FrequencyLock.probe_altU_period_two
#print axioms AIEFGate.FrequencyLock.probe_unitRate_constant
#print axioms AIEFGate.FrequencyLock.probe_altU_values
#print axioms AIEFGate.FrequencyLock.probe_pairLock_one_step
#print axioms AIEFGate.FrequencyLock.pairLock_factor_two_refuted
#print axioms AIEFGate.FrequencyLock.pairLock_norm_factor_two_refuted
#print axioms AIEFGate.FrequencyLock.half_lock_refuted
#print axioms AIEFGate.FrequencyLock.delay_start_refuted
#print axioms AIEFGate.FrequencyLock.nonperiodic_rate_refuted
