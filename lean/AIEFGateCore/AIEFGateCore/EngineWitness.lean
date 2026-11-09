/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.RedTeam

/-!
# (P2) Engine-shaped non-vacuity witness with `ε > 0`

`RedTeam.nonvacuous_plus` uses `p0` (`ε = 0`, `γ = 1`, `cap = 1`), which is not an engine
configuration. Here the hypotheses of the engine-shaped per-edge main theorem
`stepB_add_smul_of_branch_engine_on` are shown to be jointly satisfiable, with a firing gate and a
binding scale (`s < 1`), at the frozen production parameters of `aief_experiment_engine_v1.py`
(`FROZEN_DT = 0.01`, `FROZEN_GAMMA = 0.015`, `FROZEN_A = 1`, `FROZEN_Q = 1.5`,
`FROZEN_DELTA = 0.05`,
`capacity = (a - delta)/q`, `scale_epsilon = FROZEN_ZERO_TOL = 1e-12`, `FROZEN_ETA = 0.04`,
`FROZEN_MU = 0.03`) read as exact reals, on K3 with coherence `R = 1` on every edge
(`drive = (η+μ)·1 - μ = 1/25`) and the fixed point `B = drive/γ = 8/3` of the unclipped update.

Scope: exact reals, not float64 (in particular `cap = 19/30` exactly, see `EngineGate`); a K3
instance, not the 12-node engine state; `R = 1` and `B = 8/3` are chosen inputs, not a state reached
by the engine. It shows the theorem is not vacuous for engine-shaped parameters with `ε > 0`; it
does
not say anything about engine trajectories.
-/

set_option autoImplicit false

namespace AIEFGate
namespace EngineWitness

open RedTeam

noncomputable section

/-- Frozen production parameters as exact reals:
`⟨dt, γ, cap = (a - delta)/q, ε, a, q, delta⟩`. -/
def pE : Params := ⟨1 / 100, 15 / 1000, (1 - 5 / 100) / (3 / 2), 1 / 10 ^ 12, 1, 3 / 2, 5 / 100⟩

/-- `drive = (η + μ) R - μ` with `η = 0.04`, `μ = 0.03` and `R = 1` on every edge. -/
def driveE : Fin 3 → ℝ := fun _ => (4 / 100 + 3 / 100) * 1 - 3 / 100

/-- Base state `B = 8/3 = drive/γ` on every edge (fixed point of the unclipped update). -/
def BE : Fin 3 → ℝ := fun _ => 8 / 3

/-- The binding scale `cap / (q_i + ε)` at the base state (`q_i = 16/3`). -/
def sE : ℝ := (1 - 5 / 100) / (3 / 2) / (16 / 3 + 1 / 10 ^ 12)

theorem engineGate_pE : EngineGate pE := by
  constructor <;> norm_num [pE]

theorem prop_BE : prop pE driveE BE = fun _ => 8 / 3 := by
  funext e
  simp only [prop, pre, pE, driveE, BE]
  norm_num

theorem sE_lt_one : sE < 1 := by
  unfold sE; norm_num

theorem sc_BE (i : Fin 3) : sc pE G3 (prop pE driveE BE) i = sE := by
  have hq : incAct G3 (prop pE driveE BE) i = 16 / 3 := by
    rw [prop_BE]; fin_cases i <;> simp <;> norm_num
  simp only [sc, hq, scale]
  exact min_eq_right sE_lt_one.le

theorem gateOn_BE : GateOn pE G3 (prop pE driveE BE) :=
  ⟨0, by rw [prop_BE]; simp [pE]; norm_num⟩

theorem clip_BE : ∀ e, vRay 2 e ≠ 0 →
    0 ≤ pre pE driveE BE e ∧ 0 ≤ pre pE driveE (BE + (1 / 10 : ℝ) • vRay 2) e := by
  intro e _
  rw [pre_add_smul]
  have h0 : pre pE driveE BE e = 8 / 3 := by simp only [pre, pE, driveE, BE]; norm_num
  rw [h0]
  constructor
  · norm_num
  · unfold vRay; split_ifs <;> simp [pE] <;> norm_num

theorem hc1_BE : IsCtrl pE G3 (prop pE driveE (BE + (1 / 10 : ℝ) • vRay 2)) (ctrlPlus 2) := by
  rw [prop_add_smul_of_clip pE driveE BE (vRay 2) (1 / 10) clip_BE]
  set u : ℝ := 1 / 10 * (1 - pE.γ * pE.dt) with hu
  have hu0 : 0 ≤ u := by rw [hu]; norm_num [pE]
  have hge : ∀ k, sE ≤ sc pE G3 (prop pE driveE BE + u • vRay 2) k := by
    intro k
    by_cases hk : k = 2
    · subst hk
      rw [sc_add_smul_vRay_self, ← sc_BE 2]
      have hq : incAct G3 (prop pE driveE BE) 2 = 16 / 3 := by rw [prop_BE]; simp; norm_num
      unfold sc
      rw [hq]
      refine scale_anti pE (by linarith) ?_ (by simp [pE]; norm_num)
      have : u ≤ 1 / 10 := by rw [hu]; norm_num [pE]
      simp only [pE]; nlinarith
    · rw [sc_add_smul_vRay_other pE _ _ 2 k hk, sc_BE]
  intro e
  have heq : sc pE G3 (prop pE driveE BE + u • vRay 2) (ctrlPlus 2 e) = sE := by
    rw [sc_add_smul_vRay_other pE _ _ 2 _ (ctrlPlus_ne 2 e), sc_BE]
  exact ⟨ctrlPlus_mem 2 e, heq ▸ hge _, heq ▸ hge _⟩

/-- **(P2) Engine-shaped non-vacuity, `ε = 10⁻¹² > 0`.** At the frozen production parameters (exact
reals), K3, `R = 1`, `B = 8/3`, `h = vRay 2`, `t = 1/10`, `ctrl = ctrlPlus 2`: the parameters are
engine-shaped, the gate fires, the scale is binding (`s < 1`), and every hypothesis of
`stepB_add_smul_of_branch_engine_on` holds (here on all edges, so also those of the all-edge
`stepB_add_smul_of_branch_engine`); its conclusion is the explicit response
`stepB (B + t h) - stepB B = (t (1 - γ dt) s) • h` with `s = cap / (16/3 + 10⁻¹²)`. -/
theorem engine_nonvacuous :
    EngineGate pE ∧ 0 < pE.ε ∧ GateOn pE G3 (prop pE driveE BE) ∧ sE < 1 ∧
    (∀ e, vRay 2 e ≠ 0 →
      0 ≤ pre pE driveE BE e ∧ 0 ≤ pre pE driveE (BE + (1 / 10 : ℝ) • vRay 2) e) ∧
    InCtrlKerOn G3 (Rel (prop pE driveE BE) (vRay 2)) (ctrlPlus 2) (vRay 2) ∧
    IsCtrlOn pE G3 (Rel (prop pE driveE BE) (vRay 2)) (prop pE driveE BE) (ctrlPlus 2) ∧
    IsCtrlOn pE G3 (Rel (prop pE driveE BE) (vRay 2))
      (prop pE driveE (BE + (1 / 10 : ℝ) • vRay 2)) (ctrlPlus 2) ∧
    (∀ e, branchScale pE G3 driveE BE (ctrlPlus 2) e = sE) ∧
    stepB pE G3 driveE (BE + (1 / 10 : ℝ) • vRay 2) - stepB pE G3 driveE BE =
      ((1 / 10) * (1 - 15 / 1000 * (1 / 100)) * sE) • vRay 2 := by
  have hker := inCtrlKerOn_of_inCtrlKer G3 ker_ctrlPlus_two (Rel (prop pE driveE BE) (vRay 2))
  have hc0 : IsCtrl pE G3 (prop pE driveE BE) (ctrlPlus 2) :=
    isCtrl_of_tied (ctrlPlus_mem 2) (fun i j => by rw [sc_BE, sc_BE])
  have hbs : ∀ e, branchScale pE G3 driveE BE (ctrlPlus 2) e = sE := fun e => by
    rw [branchScale_of_on e gateOn_BE, sc_BE]
  refine ⟨engineGate_pE, by simp [pE], gateOn_BE, sE_lt_one, clip_BE, hker,
    isCtrlOn_of_isCtrl pE G3 hc0 _, isCtrlOn_of_isCtrl pE G3 hc1_BE _, hbs, ?_⟩
  have key := stepB_add_smul_of_branch_engine_on pE G3 engineGate_pE driveE BE (vRay 2) (1 / 10)
    (ctrlPlus 2) clip_BE hker (isCtrlOn_of_isCtrl pE G3 hc0 _) (isCtrlOn_of_isCtrl pE G3 hc1_BE _)
  rw [key]
  funext e
  simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul, hbs]
  simp only [pE]
  ring

/-- **False variant of `engine_nonvacuous`** (factor `1 - γ dt` dropped): the response is not
`(t s) • vRay 2` (it differs by the factor `1 - 3/20000 ≠ 1`). -/
theorem engine_false_no_gamma :
    stepB pE G3 driveE (BE + (1 / 10 : ℝ) • vRay 2) - stepB pE G3 driveE BE ≠
      ((1 / 10) * sE) • vRay 2 := by
  rw [engine_nonvacuous.2.2.2.2.2.2.2.2.2]
  intro h
  have h0 := congrFun h 0
  have hs : 0 < sE := by unfold sE; norm_num
  simp [vRay] at h0
  nlinarith

end

end EngineWitness
end AIEFGate
