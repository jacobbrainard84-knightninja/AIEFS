/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.Freeze
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Order.Interval.Finset.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# H13. Discrete Halanay inequality (easy floor-exponent form)

Agreed target (Auditor Seat 002, agreed by Researcher 001 with changes; this file implements the
corrected statement). For a fixed delay `d`, a nonnegative initial-window maximum
`M := initMax u d` (the max of `u` on the inclusive window `0..d`), and `0 ≤ a`, `0 ≤ b`,
`a + b < 1`, if the delayed inequality

  `u (n + 1) ≤ a * u n + b * windowMax u n d`

holds for every `n ≥ d`, then

  `u n ≤ M * (a + b) ^ (n / (d + 1))`

with natural-number (floor) division.

**Hypothesis `0 ≤ M`, not `u ≥ 0` everywhere.** Researcher 001 suggested dropping `u ≥ 0` as
unused. That change is wrong for the written bound when `M < 0`: the counterexample
`d = 1`, `u 0 = u 1 = -1` (so `M = -1`), `u 2 = -q`, `u 3 = -q^2` with `q = a + b ∈ (0, 1)`
obeys the delayed inequality, but `u 3 = -q^2 > -q = M * q ^ (3 / 2)` (see
`false_bound_neg_initMax`, exact rationals `a = 1/2`, `b = 1/3`, `q = 5/6`,
`-25/36 > -5/6`). The earlier signed-sample probe (16 random mixed-sign initial windows,
16/16 held) was too weak to find this: it never sat `M` strictly below 0 with the
equality tail. Correction, not blame. The weakest correct hypothesis used here is
`0 ≤ initMax u d`. Nonnegativity of `u` on all of `ℕ` is a corollary
(`discrete_halanay_of_nonneg`). For `M ≥ 0` the block bounds `M * q ^ k` are
nonincreasing, which is what the block induction uses.

**Not progress on O1; no engine claim.** This is an abstract lemma about a real sequence.
It does not assert that any engine phase, frequency, `R`, or `B` quantity satisfies the
delayed inequality, and it is not a synchronization or basin result. The engine `B` law
is delay-free (`WeightUpdate.stepM_scalar_recurrence`). A Halanay hypothesis on a fully
nonlinear phase diameter is essentially O1 and is unproven. Application to AIEFS
dynamics is a later, separately audited item (NORTH_STAR step 8). Production
`d = 50` is the intended parameter (`FROZEN_DELAY_STEPS`); the lemma is for general `d`.

The `d = 0` corollary `discrete_halanay_d0` is `AIEFGate.Freeze.upper_geom` with `β = 0`
(and `ρ = a + b`). That form does *not* need `0 ≤ u 0`. The general floor-exponent
result still requires `0 ≤ M` when the window can be longer than one point.

A weakening of `a + b < 1` to `a + b ≤ 1` on the *written* bound of `discrete_halanay`
is predicted to **SURVIVE** (at `a + b = 1` the bound is `M`, and `u n ≤ M` still holds).
It is not registered as a mutant. The killable control is the decay corollary
`discrete_halanay_decay` (`∃ ρ < 1, ∀ n, u n ≤ M * ρ ^ (n / (d + 1))`), which is false
for the constant sequence at `a + b = 1` (`false_decay_at_q_one`).
-/

set_option autoImplicit false
set_option linter.style.header false

open Finset

namespace AIEFGate
namespace DiscreteHalanay

noncomputable section

/-- Maximum of `u` on the inclusive integer interval `[lo, hi]`. -/
def intervalMax (u : ℕ → ℝ) (lo hi : ℕ) (hle : lo ≤ hi) : ℝ :=
  (Finset.Icc lo hi).sup' (Finset.nonempty_Icc.mpr hle) u

/-- Maximum of `u` on the delayed window `[n - d, n]` (Nat subtraction). For `n ≥ d` this is
`[n - d, n]`. -/
def windowMax (u : ℕ → ℝ) (n d : ℕ) : ℝ :=
  intervalMax u (n - d) n (Nat.sub_le n d)

/-- Maximum of `u` on the initial window `0..d` inclusive. Production `d = 50`. -/
def initMax (u : ℕ → ℝ) (d : ℕ) : ℝ :=
  intervalMax u 0 d (Nat.zero_le d)

/-- Easy Halanay factor: `(a + b) ^ (n / (d + 1))` with Nat floor division. -/
def blockPow (q : ℝ) (n d : ℕ) : ℝ :=
  q ^ (n / (d + 1))

/-! ### Interval-max calculus -/

theorem intervalMax_le (u : ℕ → ℝ) (lo hi : ℕ) (hle : lo ≤ hi) {k : ℕ}
    (hlo : lo ≤ k) (hhi : k ≤ hi) : u k ≤ intervalMax u lo hi hle := by
  have hk : k ∈ Finset.Icc lo hi := Finset.mem_Icc.mpr ⟨hlo, hhi⟩
  exact (Finset.le_sup'_iff (Finset.nonempty_Icc.mpr hle) (f := u)).mpr ⟨k, hk, le_rfl⟩

theorem le_intervalMax (u : ℕ → ℝ) (lo hi : ℕ) (hle : lo ≤ hi) {m : ℝ}
    (hm : ∀ k, lo ≤ k → k ≤ hi → u k ≤ m) : intervalMax u lo hi hle ≤ m := by
  exact (Finset.sup'_le_iff (Finset.nonempty_Icc.mpr hle) (f := u)).mpr fun k hk => by
    rcases Finset.mem_Icc.mp hk with ⟨h1, h2⟩
    exact hm k h1 h2

theorem initMax_le (u : ℕ → ℝ) (d : ℕ) {k : ℕ} (hk : k ≤ d) : u k ≤ initMax u d :=
  intervalMax_le u 0 d (Nat.zero_le d) (Nat.zero_le k) hk

theorem le_initMax (u : ℕ → ℝ) (d : ℕ) {m : ℝ}
    (hm : ∀ k, k ≤ d → u k ≤ m) : initMax u d ≤ m :=
  le_intervalMax u 0 d (Nat.zero_le d) (fun k _ h2 => hm k h2)

theorem windowMax_le (u : ℕ → ℝ) (n d : ℕ) {k : ℕ}
    (hlo : n - d ≤ k) (hhi : k ≤ n) : u k ≤ windowMax u n d :=
  intervalMax_le u (n - d) n (Nat.sub_le n d) hlo hhi

theorem le_windowMax (u : ℕ → ℝ) (n d : ℕ) {m : ℝ}
    (hm : ∀ k, n - d ≤ k → k ≤ n → u k ≤ m) : windowMax u n d ≤ m :=
  le_intervalMax u (n - d) n (Nat.sub_le n d) hm

theorem u_le_windowMax (u : ℕ → ℝ) (n d : ℕ) : u n ≤ windowMax u n d :=
  windowMax_le u n d (Nat.sub_le n d) le_rfl

theorem initMax_eq_windowMax (u : ℕ → ℝ) (d : ℕ) : initMax u d = windowMax u d d := by
  simp [initMax, windowMax]

#print axioms intervalMax_le
#print axioms le_intervalMax
#print axioms initMax_le
#print axioms le_initMax
#print axioms windowMax_le
#print axioms le_windowMax
#print axioms u_le_windowMax
#print axioms initMax_eq_windowMax

/-- The delayed one-step bound, contracted to a multiple of the current window max. -/
theorem step_le_window (u : ℕ → ℝ) (a b : ℝ) (d : ℕ)
    (ha : 0 ≤ a) (hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d)
    {n : ℕ} (hn : d ≤ n) : u (n + 1) ≤ (a + b) * windowMax u n d := by
  have hu : u n ≤ windowMax u n d := u_le_windowMax u n d
  calc
    u (n + 1) ≤ a * u n + b * windowMax u n d := hstep n hn
    _ ≤ a * windowMax u n d + b * windowMax u n d :=
      add_le_add (mul_le_mul_of_nonneg_left hu ha) le_rfl
    _ = (a + b) * windowMax u n d := by ring

#print axioms step_le_window

/-- If the window max at `n₀ ≥ d` is nonpositive, it stays nonpositive and every later
`u` is nonpositive. -/
theorem stay_nonpos (u : ℕ → ℝ) (a b : ℝ) (d : ℕ)
    (ha : 0 ≤ a) (hb : 0 ≤ b)
    (hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d)
    {n₀ : ℕ} (hn : d ≤ n₀) (hW : windowMax u n₀ d ≤ 0) :
    (∀ t, windowMax u (n₀ + t) d ≤ 0) ∧ ∀ t, 1 ≤ t → u (n₀ + t) ≤ 0 := by
  have hq0 : 0 ≤ a + b := add_nonneg ha hb
  have hWle : ∀ t, windowMax u (n₀ + t) d ≤ 0 := by
    intro t
    induction t with
    | zero => simpa using hW
    | succ t ih =>
      have hn' : d ≤ n₀ + t := by omega
      refine le_windowMax u (n₀ + t + 1) d ?_
      intro k hk1 hk2
      have hshift : n₀ + t + 1 - d = n₀ + t - d + 1 := by omega
      have hk1' : n₀ + t - d + 1 ≤ k := by rw [hshift] at hk1; exact hk1
      rcases le_or_gt k (n₀ + t) with hkn | hnk
      · exact le_trans
          (windowMax_le u (n₀ + t) d (le_trans (Nat.le_add_right _ 1) hk1') hkn) ih
      · have hk_eq : k = n₀ + t + 1 := by omega
        have hnext : u (n₀ + t + 1) ≤ (a + b) * windowMax u (n₀ + t) d :=
          step_le_window u a b d ha hstep hn'
        have : (a + b) * windowMax u (n₀ + t) d ≤ 0 :=
          mul_nonpos_of_nonneg_of_nonpos hq0 ih
        simpa [hk_eq] using le_trans hnext this
  refine ⟨hWle, ?_⟩
  intro t ht
  have ht' : t = (t - 1) + 1 := by omega
  have hn' : d ≤ n₀ + (t - 1) := by omega
  have hnext : u (n₀ + (t - 1) + 1) ≤ (a + b) * windowMax u (n₀ + (t - 1)) d :=
    step_le_window u a b d ha hstep hn'
  have : (a + b) * windowMax u (n₀ + (t - 1)) d ≤ 0 :=
    mul_nonpos_of_nonneg_of_nonpos hq0 (hWle (t - 1))
  have : u (n₀ + (t - 1) + 1) ≤ 0 := le_trans hnext this
  convert this using 2
  omega

#print axioms stay_nonpos

/-- From a time `n₀ ≥ d` at which the window max `W` is nonnegative, every later window
max is `≤ W` and every later value is `≤ (a + b) * W`. -/
theorem future_le_of_window_nonneg (u : ℕ → ℝ) (a b : ℝ) (d : ℕ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hq1 : a + b ≤ 1)
    (hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d)
    {n₀ : ℕ} (hn : d ≤ n₀) (hW : 0 ≤ windowMax u n₀ d) :
    (∀ t, windowMax u (n₀ + t) d ≤ windowMax u n₀ d) ∧
      ∀ t, 1 ≤ t → u (n₀ + t) ≤ (a + b) * windowMax u n₀ d := by
  have hq0 : 0 ≤ a + b := add_nonneg ha hb
  have hWle : ∀ t, windowMax u (n₀ + t) d ≤ windowMax u n₀ d := by
    intro t
    induction t with
    | zero => simp
    | succ t ih =>
      have hn' : d ≤ n₀ + t := by omega
      refine le_windowMax u (n₀ + t + 1) d ?_
      intro k hk1 hk2
      have hshift : n₀ + t + 1 - d = n₀ + t - d + 1 := by omega
      have hk1' : n₀ + t - d + 1 ≤ k := by rw [hshift] at hk1; exact hk1
      rcases le_or_gt k (n₀ + t) with hkn | hnk
      · exact le_trans
          (windowMax_le u (n₀ + t) d (le_trans (Nat.le_add_right _ 1) hk1') hkn) ih
      · have hk_eq : k = n₀ + t + 1 := by omega
        have hnext : u (n₀ + t + 1) ≤ (a + b) * windowMax u (n₀ + t) d :=
          step_le_window u a b d ha hstep hn'
        have : u (n₀ + t + 1) ≤ windowMax u n₀ d := by
          by_cases hpos : 0 ≤ windowMax u (n₀ + t) d
          · have : (a + b) * windowMax u (n₀ + t) d ≤ windowMax u (n₀ + t) d :=
              mul_le_of_le_one_left hpos hq1
            exact le_trans (le_trans hnext this) ih
          · have hneg : windowMax u (n₀ + t) d < 0 := lt_of_not_ge hpos
            have : (a + b) * windowMax u (n₀ + t) d ≤ 0 :=
              mul_nonpos_of_nonneg_of_nonpos hq0 hneg.le
            exact le_trans (le_trans hnext this) hW
        simpa [hk_eq] using this
  refine ⟨hWle, ?_⟩
  intro t ht
  have hn' : d ≤ n₀ + (t - 1) := by omega
  have hnext : u (n₀ + (t - 1) + 1) ≤ (a + b) * windowMax u (n₀ + (t - 1)) d :=
    step_le_window u a b d ha hstep hn'
  have : (a + b) * windowMax u (n₀ + (t - 1)) d ≤ (a + b) * windowMax u n₀ d :=
    mul_le_mul_of_nonneg_left (hWle (t - 1)) hq0
  have : u (n₀ + (t - 1) + 1) ≤ (a + b) * windowMax u n₀ d := le_trans hnext this
  convert this using 2
  omega

#print axioms future_le_of_window_nonneg

/-- End of block `j` plus one: `d + j * (d + 1) + 1 = (j + 1) * (d + 1)`. -/
theorem block_end_succ (d j : ℕ) : d + j * (d + 1) + 1 = (j + 1) * (d + 1) := by
  ring

#print axioms block_end_succ

/-- The main easy discrete Halanay bound. Hypothesis `0 ≤ initMax u d`, not pointwise
nonnegativity of `u`. -/
theorem discrete_halanay (u : ℕ → ℝ) (a b : ℝ) (d : ℕ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hq : a + b < 1)
    (hM : 0 ≤ initMax u d)
    (hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d) :
    ∀ n, u n ≤ initMax u d * blockPow (a + b) n d := by
  intro n
  set M := initMax u d
  set q := a + b
  have hq0 : 0 ≤ q := add_nonneg ha hb
  have hq1 : q ≤ 1 := le_of_lt hq
  have hWd : windowMax u d d = M := (initMax_eq_windowMax u d).symm
  -- Block `j` is the interval `[j * (d + 1), d + j * (d + 1)]`.
  -- We prove the window max at the end of the block, and every value in the block,
  -- is `≤ M * q ^ j`.
  have hblock : ∀ j,
      windowMax u (d + j * (d + 1)) d ≤ M * q ^ j ∧
        ∀ k, j * (d + 1) ≤ k → k ≤ d + j * (d + 1) → u k ≤ M * q ^ j := by
    intro j
    induction j with
    | zero =>
      refine ⟨?_, ?_⟩
      · simp [hWd]
      · intro k hk1 hk2
        have hk : k ≤ d := by omega
        simpa [pow_zero, mul_one] using initMax_le u d hk
    | succ j ih =>
      set n₀ := d + j * (d + 1)
      have hn0 : d ≤ n₀ := by omega
      have hWj : windowMax u n₀ d ≤ M * q ^ j := ih.1
      have hUj := ih.2
      -- The next block is `[n₀ + 1, n₀ + (d + 1)]`.
      have hstart : (j + 1) * (d + 1) = n₀ + 1 := by
        simp [n₀]; ring
      have hend : d + (j + 1) * (d + 1) = n₀ + (d + 1) := by
        simp [n₀]; ring
      by_cases hpos : 0 ≤ windowMax u n₀ d
      · have hfut := future_le_of_window_nonneg u a b d ha hb hq1 hstep hn0 hpos
        have hval : ∀ k, n₀ + 1 ≤ k → k ≤ n₀ + (d + 1) → u k ≤ q * windowMax u n₀ d := by
          intro k hk1 hk2
          have : 1 ≤ k - n₀ := by omega
          have := hfut.2 (k - n₀) this
          simpa [Nat.add_sub_of_le (by omega : n₀ ≤ k)] using this
        have hbound : q * windowMax u n₀ d ≤ M * q ^ (j + 1) := by
          have := mul_le_mul_of_nonneg_left hWj hq0
          simpa [pow_succ, mul_assoc, mul_left_comm, mul_comm] using this
        constructor
        · rw [hend]
          refine le_trans ?_ hbound
          refine le_windowMax u (n₀ + (d + 1)) d ?_
          intro k hk1 hk2
          have : n₀ + 1 ≤ k := by omega
          exact hval k this hk2
        · intro k hk1 hk2
          rw [hstart] at hk1
          rw [hend] at hk2
          exact le_trans (hval k hk1 hk2) hbound
      · have hneg : windowMax u n₀ d < 0 := lt_of_not_ge hpos
        have hstay := stay_nonpos u a b d ha hb hstep hn0 hneg.le
        have hMpow : 0 ≤ M * q ^ (j + 1) := mul_nonneg hM (pow_nonneg hq0 _)
        constructor
        · refine le_trans ?_ hMpow
          rw [hend]
          refine le_windowMax u (n₀ + (d + 1)) d ?_
          intro k hk1 hk2
          have : 1 ≤ k - n₀ := by omega
          have := hstay.2 (k - n₀) this
          simpa [Nat.add_sub_of_le (by omega : n₀ ≤ k)] using this
        · intro k hk1 hk2
          rw [hstart] at hk1
          have : 1 ≤ k - n₀ := by omega
          have := hstay.2 (k - n₀) this
          exact le_trans (by simpa [Nat.add_sub_of_le (by omega : n₀ ≤ k)] using this) hMpow
  -- `n` lies in block `j = n / (d + 1)`.
  set j := n / (d + 1)
  have hlo : j * (d + 1) ≤ n := by
    have h := Nat.mul_div_le n (d + 1)
    -- `(d + 1) * (n / (d + 1)) ≤ n`
    simpa [j, mul_comm] using h
  have hhi : n ≤ d + j * (d + 1) := by
    have h := Nat.lt_mul_div_succ n (Nat.succ_pos d)
    -- `n < (d + 1) * (n / (d + 1) + 1)`
    have : n < (j + 1) * (d + 1) := by
      simpa [j, Nat.succ_eq_add_one, mul_comm, add_comm, add_left_comm] using h
    have : n + 1 ≤ (j + 1) * (d + 1) := this
    have hse := block_end_succ d j
    omega
  simpa [blockPow] using (hblock j).2 n hlo hhi

#print axioms discrete_halanay

/-- Pointwise nonnegativity of `u` implies `0 ≤ initMax u d`, so the bound follows. -/
theorem discrete_halanay_of_nonneg (u : ℕ → ℝ) (a b : ℝ) (d : ℕ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hq : a + b < 1)
    (hnn : ∀ n, 0 ≤ u n)
    (hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d) :
    ∀ n, u n ≤ initMax u d * blockPow (a + b) n d :=
  discrete_halanay u a b d ha hb hq (le_trans (hnn 0) (initMax_le u d (Nat.zero_le d))) hstep

#print axioms discrete_halanay_of_nonneg

/-- The delay-free special case `d = 0`. This is `AIEFGate.Freeze.upper_geom` with `β = 0`
and `ρ = a + b`. Unlike `discrete_halanay`, it does not require `0 ≤ u 0`. When `d = 0`
the delayed inequality is `u (n + 1) ≤ (a + b) * u n` for every `n`, and the floor
exponent is `n / 1 = n`. -/
theorem discrete_halanay_d0 (u : ℕ → ℝ) (a b : ℝ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hq : a + b < 1)
    (hstep : ∀ n, u (n + 1) ≤ (a + b) * u n) :
    ∀ n, u n ≤ (a + b) ^ n * u 0 := by
  intro n
  have h := AIEFGate.Freeze.upper_geom u (a + b) 0 (add_nonneg ha hb) hq
    (fun k => by simpa using hstep k) n
  simpa using h

#print axioms discrete_halanay_d0

/-- When `0 ≤ u 0`, the `d = 0` case of `discrete_halanay` agrees with `discrete_halanay_d0`. -/
theorem windowMax_delay_zero (u : ℕ → ℝ) (n : ℕ) : windowMax u n 0 = u n := by
  simp [windowMax, intervalMax, Finset.Icc_self]

theorem initMax_delay_zero (u : ℕ → ℝ) : initMax u 0 = u 0 := by
  simp [initMax, intervalMax, Finset.Icc_self]

#print axioms windowMax_delay_zero
#print axioms initMax_delay_zero

theorem discrete_halanay_d0_of_initMax (u : ℕ → ℝ) (a b : ℝ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hq : a + b < 1)
    (hM : 0 ≤ u 0)
    (hstep : ∀ n, u (n + 1) ≤ (a + b) * u n) :
    ∀ n, u n ≤ initMax u 0 * blockPow (a + b) n 0 := by
  have hstep' : ∀ n, 0 ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n 0 := by
    intro n _
    rw [windowMax_delay_zero]
    have := hstep n
    linarith
  have hM' : 0 ≤ initMax u 0 := by
    simpa [initMax_delay_zero] using hM
  exact discrete_halanay u a b 0 ha hb hq hM' hstep'

#print axioms discrete_halanay_d0_of_initMax

/-- Killable decay form: there is a ratio `ρ < 1` such that
`u n ≤ M * ρ ^ (n / (d + 1))`. The constant sequence at `a + b = 1` kills the same
claim with `a + b < 1` dropped (`false_decay_at_q_one`). -/
theorem discrete_halanay_decay (u : ℕ → ℝ) (a b : ℝ) (d : ℕ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hq_decay : a + b < 1)
    (hM : 0 ≤ initMax u d)
    (hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d) :
    ∃ ρ, 0 ≤ ρ ∧ ρ < 1 ∧ ∀ n, u n ≤ initMax u d * ρ ^ (n / (d + 1)) := by
  refine ⟨a + b, add_nonneg ha hb, hq_decay, ?_⟩
  intro n
  simpa [blockPow] using discrete_halanay u a b d ha hb hq_decay hM hstep n

#print axioms discrete_halanay_decay

/-- Geometric (single-ratio) form: with `ρ = q ^ (1 / (d + 1))` in the reals (`Real.rpow`)
and `0 < q < 1`, one has `u n ≤ M * (ρ ^ n / ρ ^ d)`. This is looser than the floor
bound, and is the `Real.rpow` spelling of the decay control. -/
theorem discrete_halanay_geom (u : ℕ → ℝ) (a b : ℝ) (d : ℕ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hq0 : 0 < a + b) (hq : a + b < 1)
    (hM : 0 ≤ initMax u d)
    (hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d) :
    let q := a + b
    let ρ := Real.rpow q (1 / (d + 1 : ℝ))
    ∀ n, u n ≤ initMax u d * (ρ ^ n / ρ ^ d) := by
  intro q ρ n
  have hqnn : 0 ≤ q := le_of_lt hq0
  have hρ0 : 0 < ρ := Real.rpow_pos_of_pos hq0 _
  have hρ1 : ρ < 1 := by
    have hy : 0 < (1 / (d + 1 : ℝ)) := by
      have : (0 : ℝ) < d + 1 := by exact_mod_cast Nat.succ_pos d
      exact one_div_pos.mpr this
    exact Real.rpow_lt_one hqnn hq hy
  have hρd : ρ ^ d ≠ 0 := pow_ne_zero _ hρ0.ne'
  have hmain := discrete_halanay u a b d ha hb hq hM hstep n
  have hnpow : ∀ k : ℕ, Real.rpow ρ (k : ℝ) = ρ ^ k :=
    fun k => Real.rpow_natCast ρ k
  have hqρ : q = ρ ^ (d + 1) := by
    have hmul : (1 / (d + 1 : ℝ)) * (d + 1) = 1 := by
      have : (d + 1 : ℝ) ≠ 0 := by exact_mod_cast (Nat.succ_ne_zero d)
      field_simp
    have hrpow : Real.rpow ρ (d + 1 : ℝ) =
        Real.rpow q ((1 / (d + 1 : ℝ)) * (d + 1)) := by
      change Real.rpow (Real.rpow q (1 / (d + 1 : ℝ))) (d + 1 : ℝ) = _
      exact (Real.rpow_mul hqnn (1 / (d + 1 : ℝ)) (d + 1 : ℝ)).symm
    calc
      q = Real.rpow q 1 := (Real.rpow_one q).symm
      _ = Real.rpow q ((1 / (d + 1 : ℝ)) * (d + 1)) := by rw [hmul]
      _ = Real.rpow ρ (d + 1 : ℝ) := hrpow.symm
      _ = ρ ^ (d + 1) := by
        simpa using hnpow (d + 1)
  have hj : q ^ (n / (d + 1)) = ρ ^ ((d + 1) * (n / (d + 1))) := by
    rw [hqρ, ← pow_mul]
  have hexp : n ≤ (d + 1) * (n / (d + 1)) + d := by
    have hmod : n % (d + 1) < d + 1 := Nat.mod_lt n (Nat.succ_pos d)
    have hmod' : n % (d + 1) ≤ d := Nat.lt_succ_iff.mp (by simpa [Nat.succ_eq_add_one] using hmod)
    have hdiv : (d + 1) * (n / (d + 1)) + n % (d + 1) = n := Nat.div_add_mod n (d + 1)
    omega
  have hpow : ρ ^ ((d + 1) * (n / (d + 1)) + d) ≤ ρ ^ n :=
    pow_le_pow_of_le_one hρ0.le hρ1.le hexp
  have : initMax u d * q ^ (n / (d + 1)) ≤ initMax u d * (ρ ^ n / ρ ^ d) := by
    have : ρ ^ ((d + 1) * (n / (d + 1))) ≤ ρ ^ n / ρ ^ d := by
      have hrew : ρ ^ ((d + 1) * (n / (d + 1))) * ρ ^ d =
          ρ ^ ((d + 1) * (n / (d + 1)) + d) := (pow_add _ _ _).symm
      rw [le_div_iff₀ (pow_pos hρ0 d), hrew]
      exact hpow
    simpa [hj] using mul_le_mul_of_nonneg_left this hM
  exact le_trans (by simpa [blockPow] using hmain) this

#print axioms discrete_halanay_geom

/-! ### Value probes (closed rationals; unfold the definitions in the probe itself) -/

/-- `initMax` of a spike at index 50, delay 50, is 1 (the unique max is inside `0..d`).
A short window `0..d-1` would give 0. -/
theorem probe_initMax_spike :
    initMax (fun k => if k = 50 then (1 : ℝ) else 0) 50 = 1 := by
  set u : ℕ → ℝ := fun k => if k = 50 then (1 : ℝ) else 0
  unfold initMax intervalMax
  apply le_antisymm
  · refine Finset.sup'_le _ _ ?_
    intro k hk
    simp only [Finset.mem_Icc] at hk
    by_cases h : k = 50
    · simp [u, h]
    · simp [u, h]
  · rw [Finset.le_sup'_iff]
    exact ⟨50, by simp, by simp [u]⟩

/-- `windowMax` on `[0, 1]` of a spike at 0 is 1; on `[1, 1]` it is 0. -/
theorem probe_windowMax_values :
    windowMax (fun k => if k = 0 then (1 : ℝ) else 0) 1 1 = 1 ∧
      windowMax (fun k => if k = 0 then (1 : ℝ) else 0) 1 0 = 0 := by
  set u : ℕ → ℝ := fun k => if k = 0 then (1 : ℝ) else 0
  constructor
  · unfold windowMax intervalMax
    apply le_antisymm
    · refine Finset.sup'_le _ _ ?_
      intro k hk
      simp only [Finset.mem_Icc] at hk
      by_cases h : k = 0
      · simp [u, h]
      · simp [u, h]
    · rw [Finset.le_sup'_iff]
      exact ⟨0, by simp, by simp [u]⟩
  · unfold windowMax intervalMax
    simp [u, Finset.Icc_self]

/-- Floor exponents at production `d = 50`: `50 / 51 = 0` and `51 / 51 = 1`. The wrong
exponent `n / d` would give `50 / 50 = 1` and `blockPow (5/6) 50 50 = 5/6`. -/
theorem probe_blockPow_values :
    blockPow (5 / 6) 50 50 = 1 ∧ blockPow (5 / 6) 51 50 = 5 / 6 := by
  constructor
  · have : (50 : ℕ) / 51 = 0 := by norm_num
    simp [blockPow, this]
  · have : (51 : ℕ) / 51 = 1 := by norm_num
    simp [blockPow, this]

#print axioms probe_initMax_spike
#print axioms probe_windowMax_values
#print axioms probe_blockPow_values

/-! ### Witness sequences and `false_*` (predeclared kills)

Recursive tails are written with a two-term `max` (delay 1) so Lean sees the structural
recursion. These are only used as red-team witnesses, not as engine models. -/

def aE : ℝ := 1 / 2
def bE : ℝ := 1 / 3

theorem aE_nonneg : 0 ≤ aE := by norm_num [aE]
theorem bE_nonneg : 0 ≤ bE := by norm_num [bE]
theorem qE_lt_one : aE + bE < 1 := by norm_num [aE, bE]
theorem qE_val : aE + bE = 5 / 6 := by norm_num [aE, bE]

#print axioms aE_nonneg
#print axioms bE_nonneg
#print axioms qE_lt_one
#print axioms qE_val

/-- Constant 1 on `{0, 1}`, then the equality tail for delay 1. -/
def uHold1 : ℕ → ℝ
  | 0 => 1
  | 1 => 1
  | n + 2 => aE * uHold1 (n + 1) + bE * max (uHold1 n) (uHold1 (n + 1))

/-- Unique maximum at index 1, then the equality tail for delay 1. -/
def uSpike1 : ℕ → ℝ
  | 0 => 0
  | 1 => 1
  | n + 2 => aE * uSpike1 (n + 1) + bE * max (uSpike1 n) (uSpike1 (n + 1))

/-- The `M < 0` counterexample: `u 0 = u 1 = -1`, then the equality tail. -/
def uNeg : ℕ → ℝ
  | 0 => -1
  | 1 => -1
  | n + 2 => aE * uNeg (n + 1) + bE * max (uNeg n) (uNeg (n + 1))

/-- Late unconstrained `u 2 = 2`. Values are nonnegative, so a late-start hypothesis holds
for `n ≥ 2` while the bound already fails at `n = 2`. -/
def uLate : ℕ → ℝ
  | 0 => 1
  | 1 => 1
  | 2 => 2
  | _ => 0

theorem windowMax_d1 (u : ℕ → ℝ) (n : ℕ) (hn : 1 ≤ n) :
    windowMax u n 1 = max (u (n - 1)) (u n) := by
  have hI : Finset.Icc (n - 1) n = {n - 1, n} := by
    ext k
    simp [Finset.mem_Icc]
    omega
  simp [windowMax, intervalMax, hI, max_comm]

theorem uHold1_step {n : ℕ} (hn : 1 ≤ n) :
    uHold1 (n + 1) = aE * uHold1 n + bE * windowMax uHold1 n 1 := by
  have hw := windowMax_d1 uHold1 n hn
  match n with
  | 0 => cases hn
  | n + 1 =>
    simp [uHold1, hw]

theorem uSpike1_step {n : ℕ} (hn : 1 ≤ n) :
    uSpike1 (n + 1) = aE * uSpike1 n + bE * windowMax uSpike1 n 1 := by
  have hw := windowMax_d1 uSpike1 n hn
  match n with
  | 0 => cases hn
  | n + 1 =>
    simp [uSpike1, hw]

theorem uNeg_step {n : ℕ} (hn : 1 ≤ n) :
    uNeg (n + 1) = aE * uNeg n + bE * windowMax uNeg n 1 := by
  have hw := windowMax_d1 uNeg n hn
  match n with
  | 0 => cases hn
  | n + 1 =>
    simp [uNeg, hw]

theorem uNeg_two : uNeg 2 = - (5 / 6) := by
  simp [uNeg, aE, bE]
  norm_num

theorem uNeg_three : uNeg 3 = - (25 / 36) := by
  -- u 3 = a * u 2 + b * max(u 1, u 2) = (1/2)*(-5/6) + (1/3)*max(-1, -5/6)
  simp [uNeg, aE, bE]
  norm_num

theorem uNeg_initMax : initMax uNeg 1 = -1 := by
  have hle : initMax uNeg 1 ≤ (-1 : ℝ) := by
    refine le_initMax uNeg 1 ?_
    intro k hk
    have : k = 0 ∨ k = 1 := by omega
    rcases this with rfl | rfl <;> simp [uNeg]
  have hge : (-1 : ℝ) ≤ initMax uNeg 1 := by
    simpa [uNeg] using initMax_le uNeg 1 (by norm_num : (0 : ℕ) ≤ 1)
  linarith

theorem uHold1_initMax : initMax uHold1 1 = 1 := by
  apply le_antisymm
  · refine le_initMax uHold1 1 ?_
    intro k hk
    have : k = 0 ∨ k = 1 := by omega
    rcases this with rfl | rfl <;> simp [uHold1]
  · simpa [uHold1] using initMax_le uHold1 1 (by norm_num : (0 : ℕ) ≤ 1)

theorem uSpike1_initMax : initMax uSpike1 1 = 1 := by
  apply le_antisymm
  · refine le_initMax uSpike1 1 ?_
    intro k hk
    have : k = 0 ∨ k = 1 := by omega
    rcases this with rfl | rfl <;> simp [uSpike1]
  · simpa [uSpike1] using initMax_le uSpike1 1 (by norm_num : (1 : ℕ) ≤ 1)

theorem uSpike1_initMax_short : initMax uSpike1 0 = 0 := by
  simpa [uSpike1] using initMax_delay_zero uSpike1

theorem uLate_initMax : initMax uLate 1 = 1 := by
  apply le_antisymm
  · refine le_initMax uLate 1 ?_
    intro k hk
    have : k = 0 ∨ k = 1 := by omega
    rcases this with rfl | rfl <;> simp [uLate]
  · simpa [uLate] using initMax_le uLate 1 (by norm_num : (0 : ℕ) ≤ 1)

theorem uLate_nonneg (n : ℕ) : 0 ≤ uLate n := by
  unfold uLate
  split <;> norm_num

#print axioms windowMax_d1
#print axioms uHold1_step
#print axioms uSpike1_step
#print axioms uNeg_step
#print axioms uNeg_two
#print axioms uNeg_three
#print axioms uNeg_initMax
#print axioms uHold1_initMax
#print axioms uSpike1_initMax
#print axioms uSpike1_initMax_short
#print axioms uLate_initMax
#print axioms uLate_nonneg

/-- Dropping `0 ≤ M` is false: `d = 1`, `M = -1`, `u 3 = -25/36 > -5/6 = M * q`. -/
theorem false_bound_neg_initMax :
    ¬ (∀ (u : ℕ → ℝ) (a b : ℝ) (d : ℕ) (_ha : 0 ≤ a) (_hb : 0 ≤ b) (_hq : a + b < 1)
      (_hM : True) (_hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d),
      ∀ n, u n ≤ initMax u d * blockPow (a + b) n d) := by
  intro H
  have hstep : ∀ n, 1 ≤ n → uNeg (n + 1) ≤ aE * uNeg n + bE * windowMax uNeg n 1 := by
    intro n hn
    exact (uNeg_step hn).le
  have h := H uNeg aE bE 1 aE_nonneg bE_nonneg qE_lt_one trivial hstep 3
  have hb : blockPow (aE + bE) 3 1 = 5 / 6 := by
    have : (3 : ℕ) / 2 = 1 := by norm_num
    simp [blockPow, qE_val, this]
  have : uNeg 3 ≤ initMax uNeg 1 * (5 / 6) := by simpa [hb] using h
  rw [uNeg_three, uNeg_initMax] at this
  norm_num at this

/-- The wrong exponent `n / d` fails at `n = d` on a constant initial window. -/
theorem false_bound_wrong_exponent :
    ¬ (∀ (u : ℕ → ℝ) (a b : ℝ) (d : ℕ) (_ha : 0 ≤ a) (_hb : 0 ≤ b) (_hq : a + b < 1)
      (_hM : 0 ≤ initMax u d)
      (_hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d),
      ∀ n, u n ≤ initMax u d * (a + b) ^ (n / d)) := by
  intro H
  have hM : 0 ≤ initMax uHold1 1 := by simp [uHold1_initMax]
  have hstep : ∀ n, 1 ≤ n →
      uHold1 (n + 1) ≤ aE * uHold1 n + bE * windowMax uHold1 n 1 := by
    intro n hn
    exact (uHold1_step hn).le
  have h := H uHold1 aE bE 1 aE_nonneg bE_nonneg qE_lt_one hM hstep 1
  have : (1 : ℝ) ≤ 5 / 6 := by
    have : (1 : ℕ) / 1 = 1 := by norm_num
    simpa [uHold1, uHold1_initMax, qE_val, this] using h
  norm_num at this

/-- The short initial window `0..d-1` fails when the unique max is at index `d`. -/
theorem false_bound_short_window :
    ¬ (∀ (u : ℕ → ℝ) (a b : ℝ) (d : ℕ) (_ha : 0 ≤ a) (_hb : 0 ≤ b) (_hq : a + b < 1)
      (_hM : 0 ≤ initMax u d)
      (_hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d),
      ∀ n, u n ≤ initMax u (d - 1) * blockPow (a + b) n d) := by
  intro H
  have hM : 0 ≤ initMax uSpike1 1 := by simp [uSpike1_initMax]
  have hstep : ∀ n, 1 ≤ n →
      uSpike1 (n + 1) ≤ aE * uSpike1 n + bE * windowMax uSpike1 n 1 := by
    intro n hn
    exact (uSpike1_step hn).le
  have h := H uSpike1 aE bE 1 aE_nonneg bE_nonneg qE_lt_one hM hstep 1
  have : (1 : ℝ) ≤ 0 := by
    have : (1 : ℕ) / 2 = 0 := by norm_num
    simpa [uSpike1, uSpike1_initMax_short, blockPow, this] using h
  norm_num at this

/-- Starting the delayed inequality at `d + 1 ≤ n` (one step late) is false. -/
theorem false_step_starts_late :
    ¬ (∀ (u : ℕ → ℝ) (a b : ℝ) (d : ℕ) (_ha : 0 ≤ a) (_hb : 0 ≤ b) (_hq : a + b < 1)
      (_hM : 0 ≤ initMax u d)
      (_hstep : ∀ n, d + 1 ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d),
      ∀ n, u n ≤ initMax u d * blockPow (a + b) n d) := by
  intro H
  have hM : 0 ≤ initMax uLate 1 := by simp [uLate_initMax]
  have hstep : ∀ n, 1 + 1 ≤ n → uLate (n + 1) ≤ aE * uLate n + bE * windowMax uLate n 1 := by
    intro n hn
    have : uLate (n + 1) = 0 := by
      match n with
      | 0 | 1 => omega
      | 2 => rfl
      | n + 3 => rfl
    have hrhs : 0 ≤ aE * uLate n + bE * windowMax uLate n 1 :=
      add_nonneg (mul_nonneg aE_nonneg (uLate_nonneg n))
        (mul_nonneg bE_nonneg (le_trans (uLate_nonneg n) (u_le_windowMax uLate n 1)))
    simpa [this] using hrhs
  have h := H uLate aE bE 1 aE_nonneg bE_nonneg qE_lt_one hM hstep 2
  have : (2 : ℝ) ≤ 5 / 6 := by
    have : (2 : ℕ) / 2 = 1 := by norm_num
    simpa [uLate, uLate_initMax, blockPow, qE_val, this] using h
  norm_num at this

/-- The decay claim is false at `a + b = 1` for the constant sequence `u ≡ 1`. -/
theorem false_decay_at_q_one :
    ¬ (∀ (u : ℕ → ℝ) (a b : ℝ) (d : ℕ) (_ha : 0 ≤ a) (_hb : 0 ≤ b) (_hq : a + b ≤ 1)
      (_hM : 0 ≤ initMax u d)
      (_hstep : ∀ n, d ≤ n → u (n + 1) ≤ a * u n + b * windowMax u n d),
      ∃ ρ, 0 ≤ ρ ∧ ρ < 1 ∧ ∀ n, u n ≤ initMax u d * ρ ^ (n / (d + 1))) := by
  intro H
  let u : ℕ → ℝ := fun _ => 1
  have hMval : initMax u 1 = 1 := by
    apply le_antisymm
    · exact le_initMax u 1 (fun _ _ => le_rfl)
    · simpa [u] using initMax_le u 1 (by norm_num : (0 : ℕ) ≤ 1)
  have hM : 0 ≤ initMax u 1 := by simp [hMval]
  have hw : ∀ n, windowMax u n 1 = 1 := by
    intro n
    apply le_antisymm
    · exact le_windowMax u n 1 (fun _ _ _ => le_rfl)
    · simpa [u] using u_le_windowMax u n 1
  have hstep : ∀ n, 1 ≤ n → u (n + 1) ≤ (1 / 2 : ℝ) * u n + (1 / 2 : ℝ) * windowMax u n 1 := by
    intro n _
    simp [u, hw n]
    norm_num
  obtain ⟨ρ, hρ0, hρ1, hρ⟩ :=
    H u (1 / 2) (1 / 2) 1 (by norm_num) (by norm_num) (by norm_num) hM hstep
  have h2 := hρ 2
  have : (2 : ℕ) / 2 = 1 := by norm_num
  have : (1 : ℝ) ≤ ρ := by
    simpa [u, hMval, this] using h2
  exact (not_le_of_gt hρ1) this

#print axioms false_bound_neg_initMax
#print axioms false_bound_wrong_exponent
#print axioms false_bound_short_window
#print axioms false_step_starts_late
#print axioms false_decay_at_q_one

end
end DiscreteHalanay
end AIEFGate
