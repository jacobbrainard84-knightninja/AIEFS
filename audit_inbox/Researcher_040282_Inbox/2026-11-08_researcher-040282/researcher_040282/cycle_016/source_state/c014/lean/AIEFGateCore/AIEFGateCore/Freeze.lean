/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-!
# (P4b) Scalar comparison core of finite-time freezing, restated inside `AIEFGateCore`

`AIEFGateCore` may not depend on `lean/AIEFFreezeCore` (`check_lean_gate.sh` step 2 forbids path
dependencies), so the five scalar statements of `lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean`
(`AIEFFreeze.upper_geom`, `eventually_off`, `eventually_on`, `edge_eventually_off`,
`edge_eventually_on`) are restated here with the same statements and proofs adapted to this file
(`research/lean_gate/tests/test_lean_gate_p4b.py` checks that the five statements agree textually
with
the `AIEFFreezeCore` source). `FreezeCore.lean` itself is not edited.

On top of them, `edge_off` / `edge_on` are the same two edge theorems in the additive-drive form
`B⁺ = λ · max 0 ((1 - h) B + d)` (drive term `d = h·u` of the source, no division by `h`), which is
the form
the engine matrix step takes (`WeightUpdate.lean`: `d = dt · D`, `h = γ dt`).

Scope: exact reals; `∃ N` conclusions (no explicit `N`); nothing about phases, delay or the EMA.
-/

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFGate
namespace Freeze

/-- Affine contraction comparison: x_{n+1} ≤ ρ x_n + β with ρ ∈ [0,1) gives
`x n - U ≤ ρ^n (x 0 - U)` where `U = β/(1-ρ)`. -/
lemma upper_geom (x : ℕ → ℝ) (ρ β : ℝ) (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hstep : ∀ n, x (n + 1) ≤ ρ * x n + β) :
    ∀ n, x n - β / (1 - ρ) ≤ ρ ^ n * (x 0 - β / (1 - ρ)) := by
  have h1 : (1 - ρ) ≠ 0 := by linarith
  intro n
  induction n with
  | zero => simp
  | succ k ih =>
    have key : x (k + 1) - β / (1 - ρ) ≤ ρ * (x k - β / (1 - ρ)) := by
      have : ρ * x k + β - β / (1 - ρ) = ρ * (x k - β / (1 - ρ)) := by
        field_simp; ring
      linarith [hstep k]
    calc x (k + 1) - β / (1 - ρ) ≤ ρ * (x k - β / (1 - ρ)) := key
      _ ≤ ρ * (ρ ^ k * (x 0 - β / (1 - ρ))) := mul_le_mul_of_nonneg_left ih hρ0
      _ = ρ ^ (k + 1) * (x 0 - β / (1 - ρ)) := by ring

/-- OFF freezing: if the comparison fixed point is strictly below the threshold,
the status is eventually (and from then on forever) OFF. -/
theorem eventually_off (x : ℕ → ℝ) (ρ β Bc : ℝ) (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hstep : ∀ n, x (n + 1) ≤ ρ * x n + β) (hgap : β / (1 - ρ) < Bc) :
    ∃ N, ∀ n ≥ N, x n < Bc := by
  set U := β / (1 - ρ)
  set A := |x 0 - U| + 1
  have hA : 0 < A := by positivity
  have hm : 0 < (Bc - U) / A := div_pos (by linarith) hA
  obtain ⟨N, hN⟩ := exists_pow_lt_of_lt_one hm hρ1
  refine ⟨N, fun n hn => ?_⟩
  have hg := upper_geom x ρ β hρ0 hρ1 hstep n
  have hpow : ρ ^ n ≤ ρ ^ N := pow_le_pow_of_le_one hρ0 hρ1.le hn
  have hpn : 0 ≤ ρ ^ n := pow_nonneg hρ0 n
  have h2 : ρ ^ n * (x 0 - U) ≤ ρ ^ n * A :=
    mul_le_mul_of_nonneg_left (by have := le_abs_self (x 0 - U); linarith) hpn
  have h3 : ρ ^ n * A < (Bc - U) / A * A :=
    mul_lt_mul_of_pos_right (lt_of_le_of_lt hpow hN) hA
  rw [div_mul_cancel₀ _ hA.ne'] at h3
  linarith

/-- ON freezing: lower comparison with fixed point strictly above threshold. -/
theorem eventually_on (x : ℕ → ℝ) (ρ β Bc : ℝ) (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hstep : ∀ n, ρ * x n + β ≤ x (n + 1)) (hgap : Bc < β / (1 - ρ)) :
    ∃ N, ∀ n ≥ N, Bc < x n := by
  have h := eventually_off (fun n => - x n) ρ (-β) (-Bc) hρ0 hρ1
    (fun n => by have := hstep n; linarith)
    (by rw [neg_div]; linarith)
  obtain ⟨N, hN⟩ := h
  exact ⟨N, fun n hn => by have := hN n hn; simp at this; linarith⟩

/-- One AIEF edge, OFF case. `lam n ∈ [0,1]` is the (arbitrary, gate-dependent)
scaling factor, `u n ≤ U` the drive. Gate-independent. -/
theorem edge_eventually_off (B u lam : ℕ → ℝ) (h U Bc : ℝ)
    (hh0 : 0 < h) (hh1 : h < 1) (hB0 : 0 ≤ B 0)
    (hlam0 : ∀ n, 0 ≤ lam n) (hlam1 : ∀ n, lam n ≤ 1)
    (hrec : ∀ n, B (n + 1) = lam n * max 0 ((1 - h) * B n + h * u n))
    (hu : ∀ n, u n ≤ U) (hU0 : 0 ≤ U) (hUc : U < Bc) :
    ∃ N, ∀ n ≥ N, B n < Bc := by
  have hnn : ∀ n, 0 ≤ B n := by
    intro n; cases n with
    | zero => exact hB0
    | succ k => rw [hrec k]; exact mul_nonneg (hlam0 k) (le_max_left _ _)
  have hstep : ∀ n, B (n + 1) ≤ (1 - h) * B n + h * U := by
    intro n
    rw [hrec n]
    have hpos : 0 ≤ (1 - h) * B n + h * U :=
      add_nonneg (mul_nonneg (by linarith) (hnn n)) (mul_nonneg hh0.le hU0)
    have hmax : max 0 ((1 - h) * B n + h * u n) ≤ (1 - h) * B n + h * U :=
      max_le hpos (by nlinarith [hu n])
    calc lam n * max 0 ((1 - h) * B n + h * u n)
        ≤ 1 * max 0 ((1 - h) * B n + h * u n) :=
          mul_le_mul_of_nonneg_right (hlam1 n) (le_max_left _ _)
      _ ≤ (1 - h) * B n + h * U := by linarith
  refine eventually_off B (1 - h) (h * U) Bc (by linarith) (by linarith) hstep ?_
  rw [show (1 - (1 - h)) = h by ring, mul_div_cancel_left₀ _ hh0.ne']
  exact hUc

/-- One AIEF edge, ON case, with a uniform lower bound `κ ≤ lam n` on the gate
factor (supplied in the paper argument by Lemma 1 from row-sum bounds) and a
drive lower bound `L ≤ u n`. Fixed point `κ h L / (1 - κ(1-h)) > Bc`. -/
theorem edge_eventually_on (B u lam : ℕ → ℝ) (h κ L Bc : ℝ)
    (hh0 : 0 < h) (hh1 : h < 1) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hlam : ∀ n, κ ≤ lam n)
    (hrec : ∀ n, B (n + 1) = lam n * max 0 ((1 - h) * B n + h * u n))
    (hB0 : 0 ≤ B 0) (hu : ∀ n, L ≤ u n) (hL : 0 ≤ L)
    (hgap : Bc < κ * h * L / (1 - κ * (1 - h))) :
    ∃ N, ∀ n ≥ N, Bc < B n := by
  have hnn : ∀ n, 0 ≤ B n := by
    intro n; cases n with
    | zero => exact hB0
    | succ k => rw [hrec k]; exact mul_nonneg (hκ0.le.trans (hlam k)) (le_max_left _ _)
  have hstep : ∀ n, κ * (1 - h) * B n + κ * h * L ≤ B (n + 1) := by
    intro n
    rw [hrec n]
    have hin : (1 - h) * B n + h * L ≤ max 0 ((1 - h) * B n + h * u n) :=
      le_max_of_le_right (by nlinarith [hu n])
    have hin0 : 0 ≤ (1 - h) * B n + h * L :=
      add_nonneg (mul_nonneg (by linarith) (hnn n)) (mul_nonneg hh0.le hL)
    calc κ * (1 - h) * B n + κ * h * L = κ * ((1 - h) * B n + h * L) := by ring
      _ ≤ lam n * ((1 - h) * B n + h * L) := mul_le_mul_of_nonneg_right (hlam n) hin0
      _ ≤ lam n * max 0 ((1 - h) * B n + h * u n) :=
          mul_le_mul_of_nonneg_left hin (hκ0.le.trans (hlam n))
  exact eventually_on B (κ * (1 - h)) (κ * h * L) Bc
    (mul_nonneg hκ0.le (by linarith)) (by nlinarith) hstep hgap

/-- **Additive-drive OFF form.** `B⁺ = λ · max 0 ((1 - h) B + d)` with `d n ≤ V`, `0 ≤ V` and
`V < h · Bc` (fixed point `V / h < Bc`). With `d = h·u`, `V = h·U` this is `edge_eventually_off`. -/
theorem edge_off (B d lam : ℕ → ℝ) (h V Bc : ℝ)
    (hh0 : 0 < h) (hh1 : h < 1) (hB0 : 0 ≤ B 0)
    (hlam0 : ∀ n, 0 ≤ lam n) (hlam1 : ∀ n, lam n ≤ 1)
    (hrec : ∀ n, B (n + 1) = lam n * max 0 ((1 - h) * B n + d n))
    (hd : ∀ n, d n ≤ V) (hV0 : 0 ≤ V) (hVc : V < h * Bc) :
    ∃ N, ∀ n ≥ N, B n < Bc := by
  refine edge_eventually_off B (fun n => d n / h) lam h (V / h) Bc hh0 hh1 hB0 hlam0 hlam1
    (fun n => ?_) (fun n => ?_) (div_nonneg hV0 hh0.le) ?_
  · rw [hrec n, mul_div_cancel₀ _ hh0.ne']
  · exact div_le_div_of_nonneg_right (hd n) hh0.le
  · rw [div_lt_iff₀ hh0]; linarith

/-- **Additive-drive ON form.** `d n ≥ M ≥ 0`, `κ ≤ λ n`, fixed point `κ M / (1 - κ (1 - h)) > Bc`.
With `d = h·u`, `M = h·L` this is `edge_eventually_on`. -/
theorem edge_on (B d lam : ℕ → ℝ) (h κ M Bc : ℝ)
    (hh0 : 0 < h) (hh1 : h < 1) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hlam : ∀ n, κ ≤ lam n)
    (hrec : ∀ n, B (n + 1) = lam n * max 0 ((1 - h) * B n + d n))
    (hB0 : 0 ≤ B 0) (hd : ∀ n, M ≤ d n) (hM : 0 ≤ M)
    (hgap : Bc < κ * M / (1 - κ * (1 - h))) :
    ∃ N, ∀ n ≥ N, Bc < B n := by
  refine edge_eventually_on B (fun n => d n / h) lam h κ (M / h) Bc hh0 hh1 hκ0 hκ1 hlam
    (fun n => ?_) hB0 (fun n => ?_) (div_nonneg hM hh0.le) ?_
  · rw [hrec n, mul_div_cancel₀ _ hh0.ne']
  · exact div_le_div_of_nonneg_right (hd n) hh0.le
  · have : κ * h * (M / h) = κ * M := by field_simp
    rw [this]; exact hgap

end Freeze
end AIEFGate
