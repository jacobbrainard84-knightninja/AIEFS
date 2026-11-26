/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import Mathlib.Analysis.ODE.DiscreteGronwall
import AIEFGateCore.Freeze
import AIEFGateCore.WeightUpdate
import AIEFGateCore.EngineWitness

/-!
# (H9) n-step envelopes of the engine `B` recurrence with a time-varying drive

Plan item H9 of `audit_inbox/briefing/PLAN_2026-11-25_scan_leads.md` (audit-inbox `cd2dd8d`), as
changed by the Auditor review `REVIEW_2026-11-26_auditor_scan_leads.md` (audit-inbox `b15c5e5`,
accepted at `66d8174`). Author Auditor Seat 002, written fresh. The only Mathlib Grönwall lemma used
is the product form `discrete_gronwall_prod_general` (`Mathlib/Analysis/ODE/DiscreteGronwall.lean`);
the exponential form `discrete_gronwall` is a growth bound `(1 + c)` and cannot give decay, so it is
not used.

Content:

* (b), the deliverable: explicit n-step envelopes of the clamped recurrence `B (n+1) = lam n · max 0
  (ρ · B n + d n)` with a **time-varying** drive `d`: `scalar_envelope_upper` (`B n ≤ ρ^n B 0 +
  ∑_{k<n} ρ^(n-1-k) · max 0 (d k)`; needs `0 ≤ ρ`, `0 ≤ B 0`, `lam n ≤ 1`, and **not** `0 ≤ lam n`),
  `scalar_envelope_lower` (time-varying gate floor `κ n ≤ lam n`, `0 ≤ κ n`, `0 ≤ ρ`; no sign
  condition on `B` or `d`);
* the same on the engine matrix step `stepM` (`WeightUpdate.stepM_scalar_recurrence`), per edge:
  `edge_recurrence`, `stepM_edge_envelope_upper`, `stepM_edge_envelope_lower`;
* engine-witness instance at the frozen `pE` (`dt = 1/100`, `γ = 3/200`, `ρ = 1 - γ dt =
  19997/20000`): `pE_rho`, `stepM_edge_envelope_pE` (drive `D ≤ 1/25`: `B n ≤ ρ^n B 0 + (1 - ρ^n) ·
  8/3`);
* (a), a short corollary only: `upper_geom_via_gronwall` has the statement of
  `AIEFGate.Freeze.upper_geom` (checked by `upper_geom_statement_eq`, `rfl` on the two types; the
  link from `Freeze.upper_geom` to `AIEFFreezeCore` is the existing text check of
  `test_lean_gate_p4b.py`), and `upper_geom_of_ne_one` records the review finding that `upper_geom`
  needs only `ρ ≠ 1` (with `0 ≤ ρ`), not `ρ < 1`.

Negations (`false_*`): `false_upper_no_rho_nonneg`, `false_upper_no_start_nonneg`,
`false_upper_no_lam_le_one`, `false_lower_no_kappa_nonneg`, `false_lower_no_rho_nonneg`,
`false_upper_geom_rho_one` (`β/0 = 0`), `false_upper_geom_rho_neg`, `false_envelope_gamma_dt_gt_one`
(engine-legal `γ dt = 2`, `WeightUpdate.pH`), `false_variant_gate_after_drive` (wrong clamp/gate
order is not the engine step).

Scope (stated, not hidden): exact reals; `γ dt ≤ 1` is a hypothesis of every matrix theorem here (`γ
dt = 1` is covered, `ρ = 0`; `γ dt > 1` is engine-legal, since the engine validates only `γ ≥ 0`,
and is refuted by `false_envelope_gamma_dt_gt_one`). The drive `D n` is an arbitrary sequence:
**conditional, not O1**. In the engine `D = (η + μ) R - μ` and `R` depends on the phases, which
depend on `B`; nothing here says which drive sequences the coupled engine produces. These are growth
envelopes: they give no convergence of `B`, no O1, and no explanation of E22. Nothing about float64.
-/

set_option autoImplicit false

namespace AIEFGate
namespace GronwallEnvelope

open Finset AIEFGate.MatrixForm AIEFGate.Capacity AIEFGate.WeightUpdate

noncomputable section

/-! ### Scalar envelopes (time-varying drive) -/

/-- Constant-coefficient product form of `discrete_gronwall_prod_general` from `0`, in chronological
powers. -/
theorem gronwall_const (u b : ℕ → ℝ) (ρ : ℝ) (hρ0 : 0 ≤ ρ)
    (hu : ∀ n, u (n + 1) ≤ ρ * u n + b n) (n : ℕ) :
    u n ≤ ρ ^ n * u 0 + ∑ k ∈ range n, ρ ^ (n - 1 - k) * b k := by
  have h := discrete_gronwall_prod_general (u := u) (b := b) (c := fun _ => ρ) (n₀ := 0)
    (fun n _ => hu n) (fun _ _ => hρ0) (Nat.zero_le n)
  simp only [prod_const, Nat.card_Ico, Nat.sub_zero] at h
  rw [← range_eq_Ico] at h
  have hs : ∑ k ∈ range n, b k * ρ ^ (n - (k + 1)) = ∑ k ∈ range n, ρ ^ (n - 1 - k) * b k := by
    refine sum_congr rfl fun k _ => ?_
    rw [show n - (k + 1) = n - 1 - k by omega, mul_comm]
  rw [hs, mul_comm (u 0)] at h
  exact h

/-- **Upper envelope, time-varying drive.** `B (n+1) = lam n · max 0 (ρ B n + d n)` with `0 ≤ ρ`,
`lam n ≤ 1` and `0 ≤ B 0`. No sign condition on `lam` is needed. -/
theorem scalar_envelope_upper (B lam d : ℕ → ℝ) (ρ : ℝ) (hρ0 : 0 ≤ ρ) (hB0 : 0 ≤ B 0)
    (hlam1 : ∀ n, lam n ≤ 1)
    (hrec : ∀ n, B (n + 1) = lam n * max 0 (ρ * B n + d n)) (n : ℕ) :
    B n ≤ ρ ^ n * B 0 + ∑ k ∈ range n, ρ ^ (n - 1 - k) * max 0 (d k) := by
  set u : ℕ → ℝ := fun n => max (B n) 0 with hu
  have hstep : ∀ n, u (n + 1) ≤ ρ * u n + max 0 (d n) := by
    intro n
    have hun : 0 ≤ u n := le_max_right _ _
    have hm : max 0 (ρ * B n + d n) ≤ ρ * u n + max 0 (d n) := by
      refine max_le (add_nonneg (mul_nonneg hρ0 hun) (le_max_left _ _)) ?_
      have : ρ * B n ≤ ρ * u n := mul_le_mul_of_nonneg_left (le_max_left _ _) hρ0
      linarith [le_max_right 0 (d n)]
    have hrhs : 0 ≤ ρ * u n + max 0 (d n) := add_nonneg (mul_nonneg hρ0 hun) (le_max_left _ _)
    have hlx : lam n * max 0 (ρ * B n + d n) ≤ max 0 (ρ * B n + d n) := by
      have := mul_le_mul_of_nonneg_right (hlam1 n) (le_max_left 0 (ρ * B n + d n))
      linarith
    change max (B (n + 1)) 0 ≤ _
    rw [hrec n]
    exact max_le (hlx.trans hm) hrhs
  have h := gronwall_const u (fun k => max 0 (d k)) ρ hρ0 hstep n
  have h0 : u 0 = B 0 := max_eq_left hB0
  rw [h0] at h
  exact (le_max_left (B n) 0).trans h

/-- **Lower envelope, time-varying gate floor.** `κ n ≤ lam n`, `0 ≤ κ n`, `0 ≤ ρ`; no sign
condition on `B` or `d`. -/
theorem scalar_envelope_lower (B lam κ d : ℕ → ℝ) (ρ : ℝ) (hρ0 : 0 ≤ ρ)
    (hκ0 : ∀ n, 0 ≤ κ n) (hκ : ∀ n, κ n ≤ lam n)
    (hrec : ∀ n, B (n + 1) = lam n * max 0 (ρ * B n + d n)) (n : ℕ) :
    B 0 * ∏ i ∈ range n, (κ i * ρ) +
      ∑ k ∈ range n, κ k * d k * ∏ i ∈ Ico (k + 1) n, (κ i * ρ) ≤ B n := by
  have hstep : ∀ n, -B (n + 1) ≤ (κ n * ρ) * (-B n) + (-(κ n * d n)) := by
    intro n
    rw [hrec n]
    have h1 : κ n * (ρ * B n + d n) ≤ κ n * max 0 (ρ * B n + d n) :=
      mul_le_mul_of_nonneg_left (le_max_right _ _) (hκ0 n)
    have h2 : κ n * max 0 (ρ * B n + d n) ≤ lam n * max 0 (ρ * B n + d n) :=
      mul_le_mul_of_nonneg_right (hκ n) (le_max_left _ _)
    nlinarith
  have h := discrete_gronwall_prod_general (u := fun n => -B n) (b := fun n => -(κ n * d n))
    (c := fun n => κ n * ρ) (n₀ := 0) (fun n _ => hstep n)
    (fun n _ => mul_nonneg (hκ0 n) hρ0) (Nat.zero_le n)
  rw [← range_eq_Ico] at h
  simp only [neg_mul, sum_neg_distrib] at h
  linarith

/-! ### Engine matrix step, per edge -/

section Matrix

variable {V : Type*} [Fintype V] [LinearOrder V] (p : Params)

/-- The engine form of one edge (restates `WeightUpdate.stepM_scalar_recurrence`): the gate factor
multiplies the clamped decayed-plus-driven proposal. -/
theorem edge_recurrence (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i)
    (hB : ∀ i j, Bm i j = Bm j i) {i j : V} (hij : i ≠ j) :
    stepM p D Bm i j =
      appliedFactor p (symM p D Bm) i j * max 0 ((1 - p.γ * p.dt) * Bm i j + p.dt * D i j) :=
  stepM_scalar_recurrence p D Bm hD hB hij

variable (B D : ℕ → V → V → ℝ)

/-- **Per-edge upper envelope of the engine trajectory**, time-varying drive. -/
theorem stepM_edge_envelope_upper (hh1 : p.γ * p.dt ≤ 1)
    (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n)) (hDs : ∀ n i j, D n i j = D n j i)
    (hB0s : ∀ i j, B 0 i j = B 0 j i) {i j : V} (hij : i ≠ j) (hB0 : 0 ≤ B 0 i j) (n : ℕ) :
    B n i j ≤ (1 - p.γ * p.dt) ^ n * B 0 i j +
      ∑ k ∈ range n, (1 - p.γ * p.dt) ^ (n - 1 - k) * max 0 (p.dt * D k i j) := by
  have hs := trajectory_symmetric p B D hrec hB0s
  refine scalar_envelope_upper (fun n => B n i j)
    (fun n => appliedFactor p (symM p (D n) (B n)) i j) (fun n => p.dt * D n i j)
    (1 - p.γ * p.dt) (by linarith) hB0 (fun n => appliedFactor_le_one p _ i j) (fun n => ?_) n
  rw [hrec n]
  exact edge_recurrence p (D n) (B n) (hDs n) (hs n) hij

/-- **Per-edge lower envelope**, with a time-varying floor `κ n` on the applied gate factor
(supplied, e.g., by `WeightUpdate.stepM_factor_lower` from drive row bounds). -/
theorem stepM_edge_envelope_lower (hh1 : p.γ * p.dt ≤ 1) (κ : ℕ → ℝ)
    (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n)) (hDs : ∀ n i j, D n i j = D n j i)
    (hB0s : ∀ i j, B 0 i j = B 0 j i) {i j : V} (hij : i ≠ j) (hκ0 : ∀ n, 0 ≤ κ n)
    (hκ : ∀ n, κ n ≤ appliedFactor p (symM p (D n) (B n)) i j) (n : ℕ) :
    B 0 i j * ∏ m ∈ range n, (κ m * (1 - p.γ * p.dt)) +
      ∑ k ∈ range n, κ k * (p.dt * D k i j) * ∏ m ∈ Ico (k + 1) n, (κ m * (1 - p.γ * p.dt)) ≤
      B n i j := by
  have hs := trajectory_symmetric p B D hrec hB0s
  refine scalar_envelope_lower (fun n => B n i j)
    (fun n => appliedFactor p (symM p (D n) (B n)) i j) κ (fun n => p.dt * D n i j)
    (1 - p.γ * p.dt) (by linarith) hκ0 hκ (fun n => ?_) n
  rw [hrec n]
  exact edge_recurrence p (D n) (B n) (hDs n) (hs n) hij

end Matrix

/-! ### Engine witness at the frozen parameters `pE` -/

open AIEFGate.EngineWitness (pE)

theorem pE_rho : 1 - pE.γ * pE.dt = 19997 / 20000 := by norm_num [pE]

/-- Geometric sum in chronological powers. -/
theorem geom_chrono (ρ : ℝ) (hρ : ρ ≠ 1) (n : ℕ) :
    ∑ k ∈ range n, ρ ^ (n - 1 - k) = (1 - ρ ^ n) / (1 - ρ) := by
  have h1 : (1 - ρ) ≠ 0 := sub_ne_zero.mpr (Ne.symm hρ)
  have hr : ∑ k ∈ range n, ρ ^ (n - 1 - k) = ∑ k ∈ range n, ρ ^ k :=
    sum_range_reflect (fun k => ρ ^ k) n
  rw [hr, geom_sum_eq hρ n]
  field_simp
  ring

/-- **Engine witness.** At `pE`, with every drive entry `D k i j ≤ 1/25` (the maximal drive `η =
0.04` at `R = 1`), each edge obeys `B n ≤ ρ^n B 0 + (1 - ρ^n) · 8/3` with `ρ = 19997/20000` (`8/3 =
u = D/γ`). -/
theorem stepM_edge_envelope_pE {V : Type*} [Fintype V] [LinearOrder V] (B D : ℕ → V → V → ℝ)
    (hrec : ∀ n, B (n + 1) = stepM pE (D n) (B n)) (hDs : ∀ n i j, D n i j = D n j i)
    (hB0s : ∀ i j, B 0 i j = B 0 j i) {i j : V} (hij : i ≠ j) (hB0 : 0 ≤ B 0 i j)
    (hD : ∀ n, D n i j ≤ 1 / 25) (n : ℕ) :
    B n i j ≤ (19997 / 20000 : ℝ) ^ n * B 0 i j + (1 - (19997 / 20000 : ℝ) ^ n) * (8 / 3) := by
  have h := stepM_edge_envelope_upper pE B D (by norm_num [pE]) hrec hDs hB0s hij hB0 n
  rw [pE_rho] at h
  have hb : ∀ k, max 0 (pE.dt * D k i j) ≤ 1 / 2500 := fun k =>
    max_le (by norm_num) (by have := hD k; norm_num [pE] at this ⊢; linarith)
  have hsum : ∑ k ∈ range n, (19997 / 20000 : ℝ) ^ (n - 1 - k) * max 0 (pE.dt * D k i j) ≤
      ∑ k ∈ range n, (19997 / 20000 : ℝ) ^ (n - 1 - k) * (1 / 2500) :=
    sum_le_sum fun k _ => mul_le_mul_of_nonneg_left (hb k) (by positivity)
  rw [← sum_mul, geom_chrono _ (by norm_num)] at hsum
  have : (1 - (19997 / 20000 : ℝ) ^ n) / (1 - 19997 / 20000) * (1 / 2500) =
      (1 - (19997 / 20000 : ℝ) ^ n) * (8 / 3) := by ring
  linarith

/-! ### (a) `upper_geom` as a corollary of the product form -/

/-- Same statement as `AIEFGate.Freeze.upper_geom`, proved from `discrete_gronwall_prod_general`. -/
theorem upper_geom_via_gronwall (x : ℕ → ℝ) (ρ β : ℝ) (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hstep : ∀ n, x (n + 1) ≤ ρ * x n + β) :
    ∀ n, x n - β / (1 - ρ) ≤ ρ ^ n * (x 0 - β / (1 - ρ)) := by
  intro n
  have h := gronwall_const x (fun _ => β) ρ hρ0 hstep n
  rw [← sum_mul, geom_chrono ρ hρ1.ne n] at h
  have h1 : (1 - ρ) ≠ 0 := by linarith
  have : ρ ^ n * x 0 + (1 - ρ ^ n) / (1 - ρ) * β - β / (1 - ρ) =
      ρ ^ n * (x 0 - β / (1 - ρ)) := by field_simp; ring
  linarith

/-- The two statements are the same proposition (Lean checks this by `rfl`). -/
theorem upper_geom_statement_eq :
    (∀ (x : ℕ → ℝ) (ρ β : ℝ), 0 ≤ ρ → ρ < 1 → (∀ n, x (n + 1) ≤ ρ * x n + β) →
      ∀ n, x n - β / (1 - ρ) ≤ ρ ^ n * (x 0 - β / (1 - ρ))) =
    (∀ (x : ℕ → ℝ) (ρ β : ℝ), 0 ≤ ρ → ρ < 1 → (∀ n, x (n + 1) ≤ ρ * x n + β) →
      ∀ n, x n - β / (1 - ρ) ≤ ρ ^ n * (x 0 - β / (1 - ρ))) := rfl

example : ∀ (x : ℕ → ℝ) (ρ β : ℝ), 0 ≤ ρ → ρ < 1 → (∀ n, x (n + 1) ≤ ρ * x n + β) →
    ∀ n, x n - β / (1 - ρ) ≤ ρ ^ n * (x 0 - β / (1 - ρ)) := AIEFGate.Freeze.upper_geom

example : ∀ (x : ℕ → ℝ) (ρ β : ℝ), 0 ≤ ρ → ρ < 1 → (∀ n, x (n + 1) ≤ ρ * x n + β) →
    ∀ n, x n - β / (1 - ρ) ≤ ρ ^ n * (x 0 - β / (1 - ρ)) := upper_geom_via_gronwall

/-- Review finding (H9): `upper_geom` needs `ρ ≠ 1` and `0 ≤ ρ` only; `ρ < 1` is used only by the `∃
N` theorems built on it. -/
theorem upper_geom_of_ne_one (x : ℕ → ℝ) (ρ β : ℝ) (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≠ 1)
    (hstep : ∀ n, x (n + 1) ≤ ρ * x n + β) :
    ∀ n, x n - β / (1 - ρ) ≤ ρ ^ n * (x 0 - β / (1 - ρ)) := by
  intro n
  have h := gronwall_const x (fun _ => β) ρ hρ0 hstep n
  rw [← sum_mul, geom_chrono ρ hρ1 n] at h
  have h1 : (1 - ρ) ≠ 0 := sub_ne_zero.mpr (Ne.symm hρ1)
  have : ρ ^ n * x 0 + (1 - ρ ^ n) / (1 - ρ) * β - β / (1 - ρ) =
      ρ ^ n * (x 0 - β / (1 - ρ)) := by field_simp; ring
  linarith

/-! ### Negations -/

/-- `scalar_envelope_upper` needs `0 ≤ ρ` (`ρ = -2`, `B 0 = 1`, no drive: `B 1 = 0 > -2`). -/
theorem false_upper_no_rho_nonneg :
    ¬ ∀ (B lam d : ℕ → ℝ) (ρ : ℝ), 0 ≤ B 0 → (∀ n, lam n ≤ 1) →
      (∀ n, B (n + 1) = lam n * max 0 (ρ * B n + d n)) → ∀ n,
      B n ≤ ρ ^ n * B 0 + ∑ k ∈ range n, ρ ^ (n - 1 - k) * max 0 (d k) := by
  intro H
  have h := H (fun n => if n = 0 then 1 else 0) (fun _ => 1) (fun _ => 0) (-2) (by norm_num)
    (fun _ => le_rfl) (fun n => by simp; split_ifs <;> norm_num) 1
  norm_num at h

/-- `scalar_envelope_upper` needs `0 ≤ B 0` (`B 0 = -1`, `ρ = 1/2`, no drive: `B 1 = 0 > -1/2`). -/
theorem false_upper_no_start_nonneg :
    ¬ ∀ (B lam d : ℕ → ℝ) (ρ : ℝ), 0 ≤ ρ → (∀ n, lam n ≤ 1) →
      (∀ n, B (n + 1) = lam n * max 0 (ρ * B n + d n)) → ∀ n,
      B n ≤ ρ ^ n * B 0 + ∑ k ∈ range n, ρ ^ (n - 1 - k) * max 0 (d k) := by
  intro H
  have h := H (fun n => if n = 0 then -1 else 0) (fun _ => 1) (fun _ => 0) (1 / 2) (by norm_num)
    (fun _ => le_rfl) (fun n => by simp; split_ifs <;> norm_num) 1
  norm_num at h

/-- `scalar_envelope_upper` needs `lam n ≤ 1` (`lam = 2`, `B 0 = 0`, `d = 1`: `B 1 = 2 > 1`). -/
theorem false_upper_no_lam_le_one :
    ¬ ∀ (B lam d : ℕ → ℝ) (ρ : ℝ), 0 ≤ ρ → 0 ≤ B 0 →
      (∀ n, B (n + 1) = lam n * max 0 (ρ * B n + d n)) → ∀ n,
      B n ≤ ρ ^ n * B 0 + ∑ k ∈ range n, ρ ^ (n - 1 - k) * max 0 (d k) := by
  intro H
  have h := H (fun n => if n = 0 then 0 else 2) (fun _ => 2) (fun _ => 1) 0 le_rfl (by norm_num)
    (fun n => by simp) 1
  norm_num at h

/-- `scalar_envelope_lower` needs `0 ≤ κ n` (`κ = -1 ≤ lam = 0`, `ρ = 1/2`, `B 0 = -2`, no drive: `B
1 = 0 < 1`). -/
theorem false_lower_no_kappa_nonneg :
    ¬ ∀ (B lam κ d : ℕ → ℝ) (ρ : ℝ), 0 ≤ ρ → (∀ n, κ n ≤ lam n) →
      (∀ n, B (n + 1) = lam n * max 0 (ρ * B n + d n)) → ∀ n,
      B 0 * ∏ i ∈ range n, (κ i * ρ) +
        ∑ k ∈ range n, κ k * d k * ∏ i ∈ Ico (k + 1) n, (κ i * ρ) ≤ B n := by
  intro H
  have h := H (fun n => if n = 0 then -2 else 0) (fun _ => 0) (fun _ => -1) (fun _ => 0) (1 / 2)
    (by norm_num) (fun _ => by norm_num) (fun n => by simp) 1
  norm_num at h

/-- `scalar_envelope_lower` needs `0 ≤ ρ` (`ρ = -1`, `B 0 = 0`, `d = (1, 2)`, `lam = 1`, `κ = (1/2,
1)`: `B 2 = 1 < 3/2`). -/
theorem false_lower_no_rho_nonneg :
    ¬ ∀ (B lam κ d : ℕ → ℝ) (ρ : ℝ), (∀ n, 0 ≤ κ n) → (∀ n, κ n ≤ lam n) →
      (∀ n, B (n + 1) = lam n * max 0 (ρ * B n + d n)) → ∀ n,
      B 0 * ∏ i ∈ range n, (κ i * ρ) +
        ∑ k ∈ range n, κ k * d k * ∏ i ∈ Ico (k + 1) n, (κ i * ρ) ≤ B n := by
  intro H
  have h := H (fun n => if n = 0 then 0 else 1) (fun _ => 1)
    (fun n => if n = 0 then 1 / 2 else 1) (fun n => if n = 0 then 1 else 2) (-1)
    (fun n => by split_ifs <;> norm_num) (fun n => by split_ifs <;> norm_num)
    (fun n => by
      rcases n with _ | n
      · norm_num
      · simp; norm_num) 2
  norm_num [Finset.sum_range_succ, Finset.prod_range_succ] at h

/-- `upper_geom` is false at `ρ = 1` (Lean's `β / 0 = 0`): `x n = n`, `β = 1` gives `1 ≤ 0`. -/
theorem false_upper_geom_rho_one :
    ¬ ∀ (x : ℕ → ℝ) (ρ β : ℝ), 0 ≤ ρ → (∀ n, x (n + 1) ≤ ρ * x n + β) →
      ∀ n, x n - β / (1 - ρ) ≤ ρ ^ n * (x 0 - β / (1 - ρ)) := by
  intro H
  have h := H (fun n => (n : ℝ)) 1 1 (by norm_num) (fun n => by push_cast; linarith) 1
  norm_num at h

/-- `upper_geom` needs `0 ≤ ρ`: `ρ = -1`, `β = 0`, `x = (1, -5, 5, …)` gives `5 ≤ 1`. -/
theorem false_upper_geom_rho_neg :
    ¬ ∀ (x : ℕ → ℝ) (ρ β : ℝ), ρ < 1 → (∀ n, x (n + 1) ≤ ρ * x n + β) →
      ∀ n, x n - β / (1 - ρ) ≤ ρ ^ n * (x 0 - β / (1 - ρ)) := by
  intro H
  have h := H (fun n => if n = 0 then 1 else (-1) ^ n * 5) (-1) 0 (by norm_num)
    (fun n => by
      rcases n with _ | n
      · norm_num
      · simp [pow_succ]) 2
  norm_num at h

/-- **Adversarial witness at `γ dt > 1`** (engine-legal: the engine validates only `γ ≥ 0`). At
`WeightUpdate.pH` (`dt = 2`, `γ = 1`, `ρ = -1`) the edge envelope fails one step from `Xo 1` with no
drive: `B 1 = 0 > -1`. So `γ dt ≤ 1` cannot be dropped from `stepM_edge_envelope_upper`. -/
theorem false_envelope_gamma_dt_gt_one :
    ¬ ∀ (B D : ℕ → Fin 2 → Fin 2 → ℝ), (∀ n, B (n + 1) = stepM pH (D n) (B n)) →
      (∀ n i j, D n i j = D n j i) → (∀ i j, B 0 i j = B 0 j i) → ∀ {i j : Fin 2}, i ≠ j →
      0 ≤ B 0 i j → ∀ n, B n i j ≤ (1 - pH.γ * pH.dt) ^ n * B 0 i j +
        ∑ k ∈ range n, (1 - pH.γ * pH.dt) ^ (n - 1 - k) * max 0 (pH.dt * D k i j) := by
  intro H
  have h := H (fun n => Nat.rec (Xo 1) (fun _ b => stepM pH 0 b) n) (fun _ => 0)
    (fun n => rfl) (fun _ _ _ => rfl) (fun i j => Xo_symm 1 i j) (i := 0) (j := 1)
    (by decide) (by norm_num [Xo]) 1
  have hs : stepM pH 0 (Xo 1) 0 1 = 0 := by
    have hsym : symM pH 0 (Xo 1) = fun _ _ => 0 := by
      funext a b
      fin_cases a <;> fin_cases b <;> simp [symM, clipM, preM, Xo, pH]
    rw [stepM_eq_mul_appliedFactor, hsym]; simp
  change stepM pH 0 (Xo 1) 0 1 ≤ _ at h
  rw [hs] at h
  norm_num [Xo, pH] at h

/-- **Wrong-variant control.** Applying the gate factor to the decayed state *before* adding the
drive (`max 0 (λ (1 - γ dt) B + dt D)`) is not the engine step: at `pE` on `Fin 2`, `B = Xo 1`, `D =
Xo 1` the gate fires and the two forms differ by `dt (1 - λ) ≠ 0`. -/
theorem false_variant_gate_after_drive :
    ¬ ∀ (D Bm : Fin 2 → Fin 2 → ℝ), (∀ i j, D i j = D j i) → (∀ i j, Bm i j = Bm j i) →
      ∀ {i j : Fin 2}, i ≠ j → stepM pE D Bm i j =
        max 0 (appliedFactor pE (symM pE D Bm) i j * ((1 - pE.γ * pE.dt) * Bm i j) +
          pE.dt * D i j) := by
  intro H
  have h := H (Xo 1) (Xo 1) (fun i j => Xo_symm 1 i j) (fun i j => Xo_symm 1 i j) (i := 0) (j := 1)
    (by decide)
  rw [edge_recurrence pE _ _ (fun i j => Xo_symm 1 i j) (fun i j => Xo_symm 1 i j) (by decide)] at h
  have hsym : symM pE (Xo 1) (Xo 1) = Xo (1 - pE.γ * pE.dt + pE.dt) := by
    funext a b
    fin_cases a <;> fin_cases b <;> simp [symM, clipM, preM, Xo, pE] <;> norm_num
  rw [hsym] at h
  have hf : appliedFactor pE (Xo (1 - pE.γ * pE.dt + pE.dt)) 0 1 < 1 := by
    have hon : GateOnX pE (Xo (1 - pE.γ * pE.dt + pE.dt)) := by
      rw [gateOnX_iff pE AIEFGate.EngineWitness.engineGate_pE]
      exact ⟨0, by rw [rowS_Xo]; norm_num [pE]⟩
    unfold appliedFactor
    rw [if_pos hon, rowS_Xo, rowS_Xo, min_self, scale_pE_ge_cap (by norm_num [pE])]
    rw [div_lt_one (by norm_num [pE])]; norm_num [pE]
  have hf0 : 0 ≤ appliedFactor pE (Xo (1 - pE.γ * pE.dt + pE.dt)) 0 1 :=
    appliedFactor_nonneg pE AIEFGate.EngineWitness.engineGate_pE (Xo_nonneg (by norm_num [pE])) 0 1
  simp only [Xo] at h
  norm_num [pE] at h hf hf0
  rw [max_eq_right (by positivity)] at h
  linarith

#print axioms scalar_envelope_upper
#print axioms scalar_envelope_lower
#print axioms stepM_edge_envelope_upper
#print axioms stepM_edge_envelope_lower
#print axioms stepM_edge_envelope_pE
#print axioms upper_geom_via_gronwall
#print axioms upper_geom_of_ne_one
#print axioms false_envelope_gamma_dt_gt_one
#print axioms false_variant_gate_after_drive

end

end GronwallEnvelope
end AIEFGate
