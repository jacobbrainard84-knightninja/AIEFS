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
* for every sign of `ρ` (F1 correction, proofs adopted with credit from Researcher 001's audit
  scratch): `scalar_envelope_upper_pos` and `stepM_edge_envelope_upper_pos`, with `ρ⁺ = max ρ 0`, so
  the per-edge upper envelope holds for **every** `γ dt` (given `EngineGate p`);
* engine-witness instance at the frozen `pE` (`dt = 1/100`, `γ = 3/200`, `ρ = 1 - γ dt =
  19997/20000`): `pE_rho`, `stepM_edge_envelope_pE` (drive `D ≤ 1/25`: `B n ≤ ρ^n B 0 + (1 - ρ^n) ·
  8/3`; about `4.2×` looser than the trivial bound `cap = 19/30`, see F4 there), pinned by
  `probe_envelope_pE_orbit`;
* (a), a short corollary only: `upper_geom_via_gronwall` has the statement of
  `AIEFGate.Freeze.upper_geom` (checked by the two `example`s and by `upper_geom_statement_eq`,
  `rfl` on the declarations' types; at `952f87d` that theorem was `A = A` and linked nothing, F5;
  the link from `Freeze.upper_geom` to `AIEFFreezeCore` is the existing text check of
  `test_lean_gate_p4b.py`), and `upper_geom_of_ne_one` records the review finding that `upper_geom`
  needs only `ρ ≠ 1` (with `0 ≤ ρ`), not `ρ < 1`.

Negations (`false_*`): `false_upper_no_rho_nonneg`, `false_upper_no_start_nonneg`,
`false_upper_no_lam_le_one`, `false_lower_no_kappa_nonneg`, `false_lower_no_rho_nonneg`,
`false_upper_geom_rho_one` (`β/0 = 0`), `false_upper_geom_rho_neg`, `false_envelope_gamma_dt_gt_one`
and `false_lower_envelope_gamma_dt_gt_one` (engine-legal `γ dt = 2`, `WeightUpdate.pH`: the
**signed-`ρ`** formulas fail there, a sign artifact; see Scope), `false_variant_gate_after_drive`
(wrong clamp/gate order is not the engine step).

Scope (stated, not hidden): exact reals; `γ dt ≤ 1` is a hypothesis of the signed-`ρ` matrix
theorems (`stepM_edge_envelope_upper/lower`; `γ dt = 1` is covered, `ρ = 0`). `γ dt > 1` is
engine-legal (the engine validates only `γ ≥ 0`) and is **EXCLUDED** from those two theorems, **not
refuted**: their `false_*` witnesses at `pH` fail only because `ρ = 1 - γ dt < 0` makes the
signed-`ρ` right-hand side negative (upper) or too large (lower). The upper envelope at `γ dt > 1`
holds in the `max ρ 0` form (`stepM_edge_envelope_upper_pos`). Correction (F1, Researcher 001 audit
of `952f87d`): `952f87d` said the case "is refuted"; that was wrong. The drive `D n` is an arbitrary
sequence: **conditional, not O1**. In the engine `D = (η + μ) R - μ` and `R` depends on the phases,
which depend on `B`; nothing here says which drive sequences the coupled engine produces. These are
growth envelopes: they give no convergence of `B`, no O1, and no explanation of E22. Nothing about
float64.
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

/-- **Upper envelope for any sign of `ρ`** (correction after the Researcher 001 audit of `952f87d`,
F1): with `ρ⁺ = max ρ 0` in place of `ρ`, the envelope holds for every `ρ`, given `0 ≤ B 0` and `0 ≤
lam n ≤ 1`. Proof adopted, with credit, from Researcher 001's audit scratch (`G2_scalar`). Unlike
`scalar_envelope_upper` this needs `0 ≤ lam n` (it keeps `B n ≥ 0`, so `ρ B n ≤ ρ⁺ B n`). -/
theorem scalar_envelope_upper_pos (B lam d : ℕ → ℝ) (ρ : ℝ) (hB0 : 0 ≤ B 0)
    (hlam0 : ∀ n, 0 ≤ lam n) (hlam1 : ∀ n, lam n ≤ 1)
    (hrec : ∀ n, B (n + 1) = lam n * max 0 (ρ * B n + d n)) (n : ℕ) :
    B n ≤ (max ρ 0) ^ n * B 0 + ∑ k ∈ range n, (max ρ 0) ^ (n - 1 - k) * max 0 (d k) := by
  have hnn : ∀ n, 0 ≤ B n := by
    intro n; cases n with
    | zero => exact hB0
    | succ n => rw [hrec n]; exact mul_nonneg (hlam0 n) (le_max_left _ _)
  have hstep : ∀ n, B (n + 1) ≤ max ρ 0 * B n + max 0 (d n) := by
    intro n
    rw [hrec n]
    have hm : max 0 (ρ * B n + d n) ≤ max ρ 0 * B n + max 0 (d n) := by
      refine max_le (add_nonneg (mul_nonneg (le_max_right _ _) (hnn n)) (le_max_left _ _)) ?_
      have : ρ * B n ≤ max ρ 0 * B n := mul_le_mul_of_nonneg_right (le_max_left _ _) (hnn n)
      linarith [le_max_right 0 (d n)]
    have hlx : lam n * max 0 (ρ * B n + d n) ≤ max 0 (ρ * B n + d n) := by
      have := mul_le_mul_of_nonneg_right (hlam1 n) (le_max_left 0 (ρ * B n + d n))
      linarith
    exact hlx.trans hm
  exact gronwall_const B (fun k => max 0 (d k)) (max ρ 0) (le_max_right _ _) hstep n

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

/-- **Per-edge upper envelope for every `γ dt`** (F1 correction): with `ρ⁺ = max (1 - γ dt) 0` the
envelope needs no `γ dt ≤ 1`; it needs `EngineGate p` (so the applied gate factor is `≥ 0`). So the
engine-legal case `γ dt > 1` is covered (there `ρ⁺ = 0`); `stepM_edge_envelope_upper` is the
signed-`ρ` form, which needs `γ dt ≤ 1` only because a negative `ρ` makes its right-hand side
negative. Adopted, with credit, from Researcher 001's audit scratch (`G2_pH_edge`, generalised here
from `pH` to any `p` with `EngineGate p`). -/
theorem stepM_edge_envelope_upper_pos (hp : EngineGate p)
    (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n)) (hDs : ∀ n i j, D n i j = D n j i)
    (hB0s : ∀ i j, B 0 i j = B 0 j i) {i j : V} (hij : i ≠ j) (hB0 : 0 ≤ B 0 i j) (n : ℕ) :
    B n i j ≤ (max (1 - p.γ * p.dt) 0) ^ n * B 0 i j +
      ∑ k ∈ range n, (max (1 - p.γ * p.dt) 0) ^ (n - 1 - k) * max 0 (p.dt * D k i j) := by
  have hs := trajectory_symmetric p B D hrec hB0s
  refine scalar_envelope_upper_pos (fun n => B n i j)
    (fun n => appliedFactor p (symM p (D n) (B n)) i j) (fun n => p.dt * D n i j) (1 - p.γ * p.dt)
    hB0
    (fun n => appliedFactor_nonneg p hp (symM_nonneg p (D n) (B n)) i j)
    (fun n => appliedFactor_le_one p _ i j) (fun n => ?_) n
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
u = D/γ`). **Weak bound (F4):** `8/3` is about `4.2×` (`80/19`) looser than the trivial bound `cap =
19/30`, which every edge obeys after one step because the gate keeps each row `≤ cap`. This instance
only checks that the general formula fits the engine form at `pE`; it is not a useful bound on the
engine weights. -/
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

/-- A concrete `pE` orbit on `Fin 2`: start `Xo 1` (its proposal row is above `cap`, so the gate
fires at step 0), constant drive `Xo (1/25)`. -/
def orbitPE : ℕ → Fin 2 → Fin 2 → ℝ :=
  fun n => Nat.rec (Xo 1) (fun _ b => stepM pE (Xo (1 / 25)) b) n

/-- **Pin of the headline constants of `stepM_edge_envelope_pE`** (F3; non-vacuity instance after
Researcher 001's audit scratch `I1`, credited): the envelope applied to `orbitPE`, with
`19997/20000` and `8/3` written out. It is closed by `exact`, so a change of either constant in
`stepM_edge_envelope_pE` (weaker or stronger) breaks it (mutant M320). -/
theorem probe_envelope_pE_orbit (n : ℕ) :
    orbitPE n 0 1 ≤ (19997 / 20000 : ℝ) ^ n * 1 + (1 - (19997 / 20000 : ℝ) ^ n) * (8 / 3) := by
  have h := stepM_edge_envelope_pE orbitPE (fun _ => Xo (1 / 25)) (fun n => rfl)
    (fun _ i j => Xo_symm _ i j)
    (fun i j => Xo_symm 1 i j) (i := 0) (j := 1) (by decide) (by norm_num [orbitPE, Xo])
    (fun n => by norm_num [Xo]) n
  have h0 : orbitPE 0 0 1 = 1 := by norm_num [orbitPE, Xo]
  rw [h0] at h
  exact h

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

/-- The types of the two declarations are the same proposition (Lean checks this by `rfl`).

Correction (F5, Researcher 001 audit of `952f87d`): at `952f87d` this theorem was the same written
type on both sides (`A = A`), so it linked nothing; the real link was, and still is, the two
`example`s below. It now states the equality of the declarations' own types (`type_of%`), so it does
mention `Freeze.upper_geom`. -/
theorem upper_geom_statement_eq :
    type_of% @AIEFGate.Freeze.upper_geom = type_of% @upper_geom_via_gronwall := rfl

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

/-- **What `γ dt ≤ 1` does in `stepM_edge_envelope_upper`** (engine-legal `γ dt > 1`: the engine
validates only `γ ≥ 0`). At `WeightUpdate.pH` (`dt = 2`, `γ = 1`, `ρ = -1`) the **signed-`ρ`**
formula fails one step from `Xo 1` with no drive: `B 1 = 0 > -1`. This is a sign artifact, not a
refutation of an envelope at `γ dt > 1`: the right-hand side is negative because `ρ < 0`. The case
`γ dt > 1` is covered by `stepM_edge_envelope_upper_pos` (`max ρ 0`). Correction (F1, Researcher 001
audit of `952f87d`): `952f87d` said this case "is refuted"; that was wrong. The theorem shows only
that this formula needs `γ dt ≤ 1` (mutant M305). -/
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

/-- With no drive at `pH` every nonnegative state steps to the zero proposal (`ρ = -1` clips it). -/
theorem symM_pH_zero_drive (X : Fin 2 → Fin 2 → ℝ) (hX : ∀ a b, 0 ≤ X a b) :
    symM pH 0 X = fun _ _ => 0 := by
  funext a b
  unfold symM clipM preM
  split_ifs
  · rfl
  · have h1 := hX a b; have h2 := hX b a
    rw [max_eq_right (by norm_num [pH]; linarith), max_eq_right (by norm_num [pH]; linarith)]
    norm_num

/-- The `pH` orbit from `Xo 1` with no drive. -/
def orbitPH : ℕ → Fin 2 → Fin 2 → ℝ := fun n => Nat.rec (Xo 1) (fun _ b => stepM pH 0 b) n

theorem orbitPH_one : orbitPH 1 = fun _ _ => 0 := by
  funext a b
  change stepM pH 0 (Xo 1) a b = 0
  rw [stepM_eq_mul_appliedFactor, symM_pH_zero_drive _ (Xo_nonneg (by norm_num))]; simp

theorem orbitPH_two : orbitPH 2 = fun _ _ => 0 := by
  funext a b
  change stepM pH 0 (orbitPH 1) a b = 0
  rw [stepM_eq_mul_appliedFactor,
    symM_pH_zero_drive _ (by rw [orbitPH_one]; intro _ _; exact le_rfl)]
  simp

theorem appliedFactor_pH_zero : appliedFactor pH (fun _ _ : Fin 2 => (0 : ℝ)) 0 1 = 1 := by
  unfold appliedFactor; rw [if_neg]; rintro ⟨i, hi⟩; simp [rowS, pH] at hi; norm_num at hi

/-- `stepM_edge_envelope_lower` needs `γ dt ≤ 1` (coverage gap found by Researcher 001 in the audit
of `952f87d`; negation adopted from its audit scratch `K5_neg`, credited): at `pH` (`ρ = -1`), `D =
0`, `B 0 = Xo 1`, `κ = (1, 1, 0, …)` the lower bound at `n = 2` is `1 > 0 = B 2`. Here the signed
`ρ` makes the lower bound too large (`κ₀ρ · κ₁ρ = 1`). Mutant M317. -/
theorem false_lower_envelope_gamma_dt_gt_one :
    ¬ ∀ (B D : ℕ → Fin 2 → Fin 2 → ℝ) (κ : ℕ → ℝ), (∀ n, B (n + 1) = stepM pH (D n) (B n)) →
      (∀ n i j, D n i j = D n j i) → (∀ i j, B 0 i j = B 0 j i) → ∀ {i j : Fin 2}, i ≠ j →
      (∀ n, 0 ≤ κ n) → (∀ n, κ n ≤ appliedFactor pH (symM pH (D n) (B n)) i j) → ∀ n,
      B 0 i j * ∏ m ∈ range n, (κ m * (1 - pH.γ * pH.dt)) +
        ∑ k ∈ range n, κ k * (pH.dt * D k i j) * ∏ m ∈ Ico (k + 1) n, (κ m * (1 - pH.γ * pH.dt)) ≤
        B n i j := by
  intro H
  have hk : ∀ n, (fun n : ℕ => if n < 2 then (1 : ℝ) else 0) n ≤
      appliedFactor pH (symM pH ((fun _ => (0 : Fin 2 → Fin 2 → ℝ)) n) (orbitPH n)) 0 1 := by
    intro n
    rcases n with _ | _ | n
    · beta_reduce; rw [if_pos (by norm_num)]
      rw [show orbitPH 0 = Xo 1 from rfl, symM_pH_zero_drive _ (Xo_nonneg (by norm_num)),
        appliedFactor_pH_zero]
    · beta_reduce; rw [if_pos (by norm_num)]
      rw [show orbitPH (0 + 1) = orbitPH 1 from rfl, orbitPH_one,
        symM_pH_zero_drive _ (fun _ _ => le_rfl), appliedFactor_pH_zero]
    · beta_reduce; rw [if_neg (by omega)]
      exact appliedFactor_nonneg pH
        ⟨by norm_num [pH], by norm_num [pH], by norm_num [pH], by norm_num [pH]⟩
        (fun a b => by unfold symM clipM; split_ifs <;> positivity) 0 1
  have h := H orbitPH (fun _ => 0) (fun n => if n < 2 then 1 else 0) (fun n => rfl)
    (fun _ _ _ => rfl) (fun i j => Xo_symm 1 i j) (i := 0) (j := 1) (by decide)
    (fun n => by split_ifs <;> norm_num) hk 2
  rw [orbitPH_two] at h
  norm_num [Finset.prod_range_succ, Finset.sum_range_succ, pH, orbitPH, Xo] at h

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
#print axioms probe_envelope_pE_orbit
#print axioms scalar_envelope_upper_pos
#print axioms stepM_edge_envelope_upper_pos
#print axioms upper_geom_statement_eq
#print axioms false_lower_envelope_gamma_dt_gt_one
#print axioms upper_geom_via_gronwall
#print axioms upper_geom_of_ne_one
#print axioms false_envelope_gamma_dt_gt_one
#print axioms false_variant_gate_after_drive

end

end GronwallEnvelope
end AIEFGate
