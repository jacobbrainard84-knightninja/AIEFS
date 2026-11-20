/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.Persistence
import AIEFGateCore.EngineWitness

/-!
# (P3) Non-vacuity of branch persistence for every `n`, engine-shaped parameters, gate firing

At the frozen production parameters `pE` (exact reals, `ε = 10⁻¹²`), on K3 with frozen coherence
`R = 1` (`drive = 1/25`), start at the tied state `BE = 8/3` and perturb along `vRay 2` (the pinned
`vCtrl`, `Bridge.vRay_two_eq_vCtrl`) with `t = 1/10`. The base trajectory stays constant on the
three edges, `B_k = bseq k`, with `bseq (k+1) = x_k · scale(2 x_k)`,
`x_k = bseq k + dt (1/25 - γ bseq k)`.
`engine_gated_persistence` proves, for every `n`:

* the gate fires at every step and the scale is binding (`sP k < 1`);
* the hypothesis `UniformBranch` of `iterate_stepB_add_smul_of_branch` holds at every step `k < n`
  (controller `ctrlPlus 2`, scale `sP k`);
* hence `stepB^[n] (BE + (1/10) vRay 2) = stepB^[n] BE + (1/10 ∏_{k<n} (1 - γ dt) sP k) • vRay 2`.

The key invariant (`inv_step`) is that `2 x_k > cap` is preserved by the map; the margin is about
`4.5 · 10⁻⁴` in `x`, coming from the drive term `dt · 1/25`.

Scope: exact reals; K3, not the 12-node engine; `R` frozen at `1` (no phase dynamics); all three
edges tied, so this is the symmetric (`+vRay 2`, `t > 0`) side only; the `-vRay 2` side leaves the
branch after one step (`K3_tied_minus_not_eigen`).
-/

set_option autoImplicit false

namespace AIEFGate
namespace PersistenceWitness

open EngineWitness RedTeam

noncomputable section

/-- Constant edge vector. -/
def cst (b : ℝ) : Fin 3 → ℝ := fun _ => b

/-- The (unclipped) proposal at a constant state with `drive = 1/25`. -/
def xE (b : ℝ) : ℝ := b + pE.dt * ((4 / 100 + 3 / 100) * 1 - 3 / 100 - pE.γ * b)

/-- One gated step on a constant state. -/
def F (b : ℝ) : ℝ := xE b * scale pE (2 * xE b)

/-- The base trajectory from `BE = 8/3`. -/
def bseq : ℕ → ℝ
  | 0 => 8 / 3
  | k + 1 => F (bseq k)

/-- The branch scale at step `k`. -/
def sP (k : ℕ) : ℝ := scale pE (2 * xE (bseq k))

theorem driveE_eq : driveE = cst ((4 / 100 + 3 / 100) * 1 - 3 / 100) := rfl

theorem incAct_cst (x : ℝ) (i : Fin 3) : incAct G3 (cst x) i = 2 * x := by
  fin_cases i <;> simp [cst] <;> ring

theorem sc_cst (x : ℝ) (i : Fin 3) : sc pE G3 (cst x) i = scale pE (2 * x) := by
  simp [sc, incAct_cst]

theorem pre_cst (b : ℝ) (e : Fin 3) : pre pE driveE (cst b) e = xE b := by
  simp [pre, xE, driveE, cst]

theorem prop_cst (b : ℝ) (hx : 0 ≤ xE b) : prop pE driveE (cst b) = cst (xE b) := by
  funext e; simp only [prop, pre_cst, max_eq_left hx, cst]

theorem gateOn_cst_iff (y : Fin 3 → ℝ) : GateOn pE G3 y ↔ ∃ i, pE.cap < incAct G3 y i :=
  gateOn_iff_exists_gt pE G3 engineGate_pE y

theorem cap_eq : pE.cap = 19 / 30 := by simp [pE]; norm_num

theorem scale_eq_of_gt (q : ℝ) (hq : pE.cap < q) : scale pE q = pE.cap / (q + pE.ε) := by
  unfold scale
  have hε : 0 < pE.ε := by simp [pE]
  have : pE.cap / (q + pE.ε) < 1 := by
    rw [div_lt_one (by linarith [cap_eq])]; linarith
  exact min_eq_right this.le

theorem scale_nonneg (q : ℝ) (hq : 0 ≤ q) : 0 ≤ scale pE q := by
  unfold scale
  have hε : 0 < pE.ε := by simp [pE]
  exact le_min zero_le_one (div_nonneg (by rw [cap_eq]; norm_num) (by linarith))

theorem scale_le_one (q : ℝ) : scale pE q ≤ 1 := min_le_left _ _

/-- Invariant along the base trajectory. -/
def Inv (b : ℝ) : Prop := 0 ≤ b ∧ pE.cap < 2 * xE b

theorem inv_zero : Inv (bseq 0) := by
  refine ⟨by norm_num [bseq], ?_⟩
  simp only [bseq, xE, pE]; norm_num

/-- **The gate keeps firing**: `2 x > cap` is preserved by one gated step. -/
theorem inv_step (b : ℝ) (hb : Inv b) : Inv (F b) := by
  obtain ⟨hb0, hg⟩ := hb
  rw [cap_eq] at hg
  set x := xE b with hxdef
  have hε : pE.ε = 1 / 10 ^ 12 := rfl
  have hx : 19 / 60 < x := by linarith
  have hd : 0 < 2 * x + pE.ε := by rw [hε]; positivity
  have hs : scale pE (2 * x) = 19 / 30 / (2 * x + pE.ε) := by
    rw [scale_eq_of_gt _ (by rw [cap_eq]; linarith), cap_eq]
  set y := F b with hydef
  have hy : y * (2 * x + pE.ε) = 19 / 30 * x := by
    rw [hydef, F, ← hxdef, hs]; field_simp
  have hy0 : 0 ≤ y := by
    rw [hydef, F, ← hxdef]; exact mul_nonneg (by linarith) (scale_nonneg _ (by linarith))
  have hyle : y ≤ 19 / 60 := by nlinarith
  have hylo : 19 / 30 - 2 * y ≤ pE.ε := by nlinarith
  refine ⟨hy0, ?_⟩
  rw [cap_eq]
  simp only [xE, pE] at hylo ⊢
  nlinarith

theorem inv_bseq (k : ℕ) : Inv (bseq k) := by
  induction k with
  | zero => exact inv_zero
  | succ k ih => exact inv_step _ ih

theorem xE_pos (b : ℝ) (hb : Inv b) : 19 / 60 < xE b := by
  have := hb.2; rw [cap_eq] at this; linarith

theorem stepB_cst (b : ℝ) (hb : Inv b) : stepB pE G3 driveE (cst b) = cst (F b) := by
  have hx := xE_pos b hb
  have hp := prop_cst b (by linarith)
  have hon : GateOn pE G3 (prop pE driveE (cst b)) := by
    rw [hp, gateOn_cst_iff]; exact ⟨0, by rw [incAct_cst]; exact hb.2⟩
  rw [stepB_of_on hon, hp]
  funext e
  simp [gated, sc_cst, F, cst]

theorem iterate_BE (k : ℕ) : (stepB pE G3 driveE)^[k] BE = cst (bseq k) := by
  induction k with
  | zero => rfl
  | succ k ih => rw [Function.iterate_succ_apply', ih, stepB_cst _ (inv_bseq k)]; rfl

theorem sP_lt_one (k : ℕ) : sP k < 1 := by
  have hg := (inv_bseq k).2
  have hε : 0 < pE.ε := by simp [pE]
  unfold sP
  rw [scale_eq_of_gt _ hg, div_lt_one (by linarith [cap_eq])]
  linarith

theorem factor_mem (j : ℕ) : 0 ≤ (1 - pE.γ * pE.dt) * sP j ∧ (1 - pE.γ * pE.dt) * sP j ≤ 1 := by
  have h0 : 0 ≤ sP j := scale_nonneg _ (by linarith [xE_pos _ (inv_bseq j)])
  have h1 := scale_le_one (2 * xE (bseq j))
  have hg : 1 - pE.γ * pE.dt = 1 - 15 / 1000 * (1 / 100) := by simp [pE]
  rw [hg]
  constructor
  · positivity
  · unfold sP; nlinarith

/-- `UniformBranch` holds at every constant invariant state for every amplitude in `[0, 1/10]`. -/
theorem uniformBranch_cst (b a : ℝ) (hb : Inv b) (ha0 : 0 ≤ a) (ha1 : a ≤ 1 / 10) :
    UniformBranch pE G3 driveE (cst b) (vRay 2) a (scale pE (2 * xE b)) (ctrlPlus 2) := by
  have hx := xE_pos b hb
  have hγ : 1 - pE.γ * pE.dt = 1 - 15 / 1000 * (1 / 100) := by simp [pE]
  set u := a * (1 - pE.γ * pE.dt) with hu
  have hu0 : 0 ≤ u := by rw [hu, hγ]; positivity
  have hu1 : u ≤ 1 / 10 := by rw [hu, hγ]; nlinarith
  have hclip : ∀ e, vRay 2 e ≠ 0 →
      0 ≤ pre pE driveE (cst b) e ∧ 0 ≤ pre pE driveE (cst b + a • vRay 2) e := by
    intro e _
    rw [pre_add_smul, pre_cst]
    refine ⟨by linarith, ?_⟩
    have hv : -1 ≤ vRay 2 e := by unfold vRay; split_ifs <;> norm_num
    have : a * (1 - pE.γ * pE.dt) * vRay 2 e = u * vRay 2 e := by rw [hu]
    rw [this]; nlinarith
  have hp1 : prop pE driveE (cst b + a • vRay 2) = cst (xE b) + u • vRay 2 := by
    rw [prop_add_smul_of_clip pE driveE (cst b) (vRay 2) a hclip, prop_cst b (by linarith)]
  have hp0' : prop pE driveE (cst b) = cst (xE b) := prop_cst b (by linarith)
  have on0 : GateOn pE G3 (prop pE driveE (cst b)) := by
    rw [hp0', gateOn_cst_iff]; exact ⟨0, by rw [incAct_cst]; exact hb.2⟩
  have on1 : GateOn pE G3 (prop pE driveE (cst b + a • vRay 2)) := by
    rw [hp1, gateOn_cst_iff]
    exact ⟨0, by
      rw [incAct_add_smul, incAct_cst, incAct_vRay_other 2 0 (by decide)]; simpa using hb.2⟩
  have hc0 : IsCtrl pE G3 (prop pE driveE (cst b)) (ctrlPlus 2) := by
    rw [hp0']; exact isCtrl_of_tied (ctrlPlus_mem 2) (fun i j => by rw [sc_cst, sc_cst])
  have hc1 : IsCtrl pE G3 (prop pE driveE (cst b + a • vRay 2)) (ctrlPlus 2) := by
    rw [hp1]
    have hge : ∀ k, scale pE (2 * xE b) ≤ sc pE G3 (cst (xE b) + u • vRay 2) k := by
      intro k
      by_cases hk : k = 2
      · subst hk
        rw [sc_add_smul_vRay_self, incAct_cst]
        refine scale_anti pE (by linarith) ?_ (by rw [cap_eq]; norm_num)
        have hε : 0 < pE.ε := by simp [pE]
        linarith
      · rw [sc_add_smul_vRay_other pE _ _ 2 k hk, sc_cst]
    intro e
    have heq : sc pE G3 (cst (xE b) + u • vRay 2) (ctrlPlus 2 e) = scale pE (2 * xE b) := by
      rw [sc_add_smul_vRay_other pE _ _ 2 _ (ctrlPlus_ne 2 e), sc_cst]
    exact ⟨ctrlPlus_mem 2 e, heq ▸ hge _, heq ▸ hge _⟩
  refine ⟨hclip, ⟨fun _ => on1, fun _ => on0⟩,
    inCtrlKerOn_of_inCtrlKer G3 ker_ctrlPlus_two _, isCtrlOn_of_isCtrl pE G3 hc0 _,
    isCtrlOn_of_isCtrl pE G3 hc1 _, fun e _ => ?_⟩
  rw [branchScale_of_on e on0, hp0', sc_cst]

/-- **(P3) Engine-shaped persistence for every `n`, gate firing, binding scale.** -/
theorem engine_gated_persistence (n : ℕ) :
    (∀ k, GateOn pE G3 (prop pE driveE ((stepB pE G3 driveE)^[k] BE)) ∧ sP k < 1) ∧
    (∀ k < n, UniformBranch pE G3 driveE ((stepB pE G3 driveE)^[k] BE) (vRay 2)
      (amp pE (1 / 10) sP k) (sP k) (ctrlPlus 2)) ∧
    (stepB pE G3 driveE)^[n] (BE + (1 / 10 : ℝ) • vRay 2) =
      (stepB pE G3 driveE)^[n] BE + amp pE (1 / 10) sP n • vRay 2 := by
  have hbr : ∀ k, UniformBranch pE G3 driveE ((stepB pE G3 driveE)^[k] BE) (vRay 2)
      (amp pE (1 / 10) sP k) (sP k) (ctrlPlus 2) := by
    intro k
    have ha := amp_mem_Icc pE (1 / 10) (by norm_num) sP factor_mem k
    rw [iterate_BE]
    exact uniformBranch_cst _ _ (inv_bseq k) ha.1 ha.2
  refine ⟨fun k => ⟨?_, sP_lt_one k⟩, fun k _ => hbr k, ?_⟩
  · rw [iterate_BE, prop_cst _ (by linarith [xE_pos _ (inv_bseq k)]), gateOn_cst_iff]
    exact ⟨0, by rw [incAct_cst]; exact (inv_bseq k).2⟩
  · exact iterate_stepB_add_smul_of_branch pE G3 driveE BE (vRay 2) (1 / 10) sP
      (fun _ => ctrlPlus 2) n (fun k _ => hbr k)

/-- **Wrong persistence statement is false** (red team, mutant M13 of `lean_mutation_check.py`):
`iterate_stepB_add_smul_of_branch` with the amplitude `amp n` replaced by `t` (no decay of the
perturbation) fails at `pE` for `n = 1` on the `engine_gated_persistence` instance, where every
hypothesis holds: the true amplitude is `t (1 - γdt) sP 0 < t`. -/
theorem false_iterate_no_decay : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (s : ℕ → ℝ)
    (ctrl : ℕ → Fin 3 → Fin 3) (n : ℕ),
    (∀ k < n, UniformBranch pE G3 drive ((stepB pE G3 drive)^[k] B) h (amp pE t s k) (s k)
      (ctrl k)) →
    (stepB pE G3 drive)^[n] (B + t • h) = (stepB pE G3 drive)^[n] B + t • h := by
  intro H
  obtain ⟨-, hbr, htrue⟩ := engine_gated_persistence 1
  have hm := H driveE BE (vRay 2) (1 / 10) sP (fun _ => ctrlPlus 2) 1 hbr
  rw [htrue] at hm
  have h0 := congrFun (add_left_cancel hm) 0
  simp only [Pi.smul_apply, smul_eq_mul, amp, Finset.prod_range_one] at h0
  have hv : vRay 2 0 = 1 := by simp [vRay]
  rw [hv, mul_one, mul_one] at h0
  have hs := sP_lt_one 0
  have hf := factor_mem 0
  have hg : 1 - pE.γ * pE.dt = 1 - 15 / 1000 * (1 / 100) := by simp [pE]
  rw [hg] at h0 hf
  nlinarith

end

end PersistenceWitness
end AIEFGate
