/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.EngineWitness

/-!
# (P3) Engine-shaped negations (`ε = 10⁻¹² > 0`)

The single-hypothesis counterexamples of `RedTeam` (`false_drop_ker`, `false_drop_hc1`,
`false_drop_clip`, `false_main_no_gamma`, `false_multiplier_no_gamma`) use the toy parameters `p0`
(`ε = 0`, `γ = 1`, `cap = 1`). Here the same negated statements are proved at the frozen production
parameters `pE` of `EngineWitness` (exact reals, `ε = 10⁻¹²`, `EngineGate pE`), on K3 with chosen
inputs:

* `engine_false_drop_ker`: `B = 8/3`, `R = 1`, `h = e0 = (1,0,0)`, `t = 1/10`, `ctrl = ctrlPlus 2`;
  edge 1 moves (`8/3 · cap/(16/3 + u + ε)` vs claim `8/3 · cap/(16/3 + ε)`, `u = t (1 - γdt)`).
* `engine_false_drop_hc1`: `B = 8/3`, `R = 1`, `h = vRay 2`, `t = -1/10`, `ctrl = ctrlPlus 2`;
  at the perturbed state node 2 has the smallest scale.
* `engine_false_drop_clip`: `B = 0`, `R = 0` (`drive = -μ = -3/100`), `h = vRay 2`,
  `t = 1/1000`; the proposal is clipped on edges 1, 2 at both states, the gate is off at both.
* `engine_false_main_no_gamma`, `engine_false_multiplier_no_gamma`: the instance of
  `engine_nonvacuous`, where every hypothesis holds.

`false_drop_hon` has no engine-shaped version: for `EngineGate` parameters `hon` is implied
(`gateOn_iff_of_branch`). `false_drop_hc0`, `false_rel_x_only` and `false_rel_h_only` are not
transcribed to `pE` here (open). Scope as in `EngineWitness`: exact reals, K3 inputs chosen by hand,
not an engine trajectory.
-/

set_option autoImplicit false

namespace AIEFGate
namespace EngineRedTeam

open EngineWitness RedTeam

noncomputable section

theorem hc0_BE : IsCtrl pE G3 (prop pE driveE BE) (ctrlPlus 2) :=
  isCtrl_of_tied (ctrlPlus_mem 2) (fun i j => by rw [sc_BE, sc_BE])

theorem on1_BE : GateOn pE G3 (prop pE driveE (BE + (1 / 10 : ℝ) • vRay 2)) := by
  rw [prop_add_smul_of_clip pE driveE BE (vRay 2) (1 / 10) clip_BE]
  exact gateOn_of_branch_aux pE G3 engineGate_pE _ _ _ _ (fun e => le_max_right _ _)
    ker_ctrlPlus_two hc0_BE gateOn_BE

theorem hon_BE : GateOn pE G3 (prop pE driveE BE) ↔
    GateOn pE G3 (prop pE driveE (BE + (1 / 10 : ℝ) • vRay 2)) :=
  ⟨fun _ => on1_BE, fun _ => gateOn_BE⟩

theorem stepB_BE (e : Fin 3) : stepB pE G3 driveE BE e = 8 / 3 * sE := by
  rw [stepB_of_on gateOn_BE]
  simp only [gated, sc_BE, min_self]
  rw [prop_BE]

theorem sE_pos : 0 < sE := by unfold sE; norm_num

/-- **M4 at engine parameters.** The main theorem with `(1 - γ dt)` dropped is false at `pE`. -/
theorem engine_false_main_no_gamma : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre pE drive B e ∧ 0 ≤ pre pE drive (B + t • h) e) →
    (GateOn pE G3 (prop pE drive B) ↔ GateOn pE G3 (prop pE drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl pE G3 (prop pE drive B) ctrl →
    IsCtrl pE G3 (prop pE drive (B + t • h)) ctrl →
    stepB pE G3 drive (B + t • h) =
      fun e => stepB pE G3 drive B e + t * branchScale pE G3 drive B ctrl e * h e := by
  intro H
  have hm := congrFun (H driveE BE (vRay 2) (1 / 10) (ctrlPlus 2) clip_BE hon_BE ker_ctrlPlus_two
    hc0_BE hc1_BE) 0
  have ht := congrFun (stepB_add_smul_of_branch pE G3 driveE BE (vRay 2) (1 / 10) (ctrlPlus 2)
    clip_BE hon_BE ker_ctrlPlus_two hc0_BE hc1_BE) 0
  rw [hm, branchScale_of_on 0 gateOn_BE, sc_BE] at ht
  have hs := sE_pos
  simp [vRay, pE] at ht
  nlinarith

/-- **M5 at engine parameters.** The multiplier formula with `(1 - γ dt)` dropped is false at
`pE`: the estimator is `(1 - γdt) sE`, the mutant claims `sE`. -/
theorem engine_false_multiplier_no_gamma :
    ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    t ≠ 0 →
    (∀ e, h e ≠ 0 → 0 ≤ pre pE drive B e ∧ 0 ≤ pre pE drive (B + t • h) e) →
    (GateOn pE G3 (prop pE drive B) ↔ GateOn pE G3 (prop pE drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl pE G3 (prop pE drive B) ctrl →
    IsCtrl pE G3 (prop pE drive (B + t • h)) ctrl →
    (∑ e, (stepB pE G3 drive (B + t • h) e - stepB pE G3 drive B e) / t * h e) / ∑ e, h e ^ 2 =
      (∑ e, branchScale pE G3 drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2 := by
  intro H
  have hm := H driveE BE (vRay 2) (1 / 10) (ctrlPlus 2) (by norm_num) clip_BE hon_BE
    ker_ctrlPlus_two hc0_BE hc1_BE
  rw [multiplier_eq_branch_formula pE G3 driveE BE (vRay 2) (1 / 10) (ctrlPlus 2) (by norm_num)
    clip_BE hon_BE ker_ctrlPlus_two hc0_BE hc1_BE] at hm
  have hbs : ∀ e, branchScale pE G3 driveE BE (ctrlPlus 2) e = sE := fun e => by
    rw [branchScale_of_on e gateOn_BE, sc_BE]
  have hs := sE_pos
  simp only [hbs, vRay_sq, Fin.sum_univ_three] at hm
  simp [pE] at hm
  nlinarith

/-- **`hker` is needed, engine parameters.** Single-edge direction `e0` at `BE`, `t = 1/10`,
`ctrl = ctrlPlus 2 = ![0,0,1]`: clip, gate (on at both) and both controller hypotheses hold; edge 1
(where `e0` is `0`) moves because the scale of node 0 drops. -/
theorem engine_false_drop_ker : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre pE drive B e ∧ 0 ≤ pre pE drive (B + t • h) e) →
    (GateOn pE G3 (prop pE drive B) ↔ GateOn pE G3 (prop pE drive (B + t • h))) →
    IsCtrl pE G3 (prop pE drive B) ctrl →
    IsCtrl pE G3 (prop pE drive (B + t • h)) ctrl →
    stepB pE G3 drive (B + t • h) =
      fun e => stepB pE G3 drive B e +
        t * (1 - pE.γ * pE.dt) * branchScale pE G3 drive B ctrl e * h e := by
  intro H
  have hx : prop pE driveE (BE + (1 / 10 : ℝ) • e0) = ![8 / 3 + 19997 / 200000, 8 / 3, 8 / 3] := by
    funext e; fin_cases e <;> simp [prop, pre, pE, driveE, BE, e0] <;> norm_num
  have hclip : ∀ e, e0 e ≠ 0 →
      0 ≤ pre pE driveE BE e ∧ 0 ≤ pre pE driveE (BE + (1 / 10 : ℝ) • e0) e := by
    intro e _; fin_cases e <;> simp [pre, pE, driveE, BE, e0] <;> norm_num
  have on1 : GateOn pE G3 (prop pE driveE (BE + (1 / 10 : ℝ) • e0)) :=
    ⟨0, by rw [hx]; simp [pE]; norm_num⟩
  have hcap : 0 ≤ pE.cap := by simp [pE]; norm_num
  have hε : 0 < pE.ε := by simp [pE]
  have s01 : sc pE G3 (prop pE driveE (BE + (1 / 10 : ℝ) • e0)) 0 =
      sc pE G3 (prop pE driveE (BE + (1 / 10 : ℝ) • e0)) 1 := by
    simp only [sc, hx, incAct_eval0, incAct_eval1]; simp
  have s02 : sc pE G3 (prop pE driveE (BE + (1 / 10 : ℝ) • e0)) 0 ≤
      sc pE G3 (prop pE driveE (BE + (1 / 10 : ℝ) • e0)) 2 := by
    simp only [sc, hx, incAct_eval0, incAct_eval2]
    exact scale_anti pE (by simp; norm_num) (by simp; linarith) hcap
  have hc1 : IsCtrl pE G3 (prop pE driveE (BE + (1 / 10 : ℝ) • e0)) (ctrlPlus 2) := by
    rw [ctrlPlus_two]; intro e
    set y := prop pE driveE (BE + (1 / 10 : ℝ) • e0) with hy
    have s12 : sc pE G3 y 1 ≤ sc pE G3 y 2 := s01 ▸ s02
    fin_cases e
    · exact ⟨by simp, le_rfl, s01.le⟩
    · exact ⟨by simp, le_rfl, s02⟩
    · exact ⟨by simp, le_rfl, s12⟩
  have key := congrFun (H driveE BE e0 (1 / 10) (ctrlPlus 2) hclip
    ⟨fun _ => on1, fun _ => gateOn_BE⟩ hc0_BE hc1) 1
  rw [stepB_of_on on1, stepB_BE] at key
  simp only [gated] at key
  rw [hx] at key
  simp only [sc] at key
  simp [scale, pE, sE, e0] at key
  norm_num at key

/-- **`hc1` is needed, engine parameters.** `t = -1/10` along `vRay 2` at `BE`: clip, gate, kernel
and the base controller hypothesis hold (all tied); at the perturbed state node 2 has the smallest
scale. Edge 1 is `(8/3 + u) · cap/(16/3 + 2u + ε)`, the claim is `(8/3 + u) · sE`. -/
theorem engine_false_drop_hc1 : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre pE drive B e ∧ 0 ≤ pre pE drive (B + t • h) e) →
    (GateOn pE G3 (prop pE drive B) ↔ GateOn pE G3 (prop pE drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl pE G3 (prop pE drive B) ctrl →
    stepB pE G3 drive (B + t • h) =
      fun e => stepB pE G3 drive B e +
        t * (1 - pE.γ * pE.dt) * branchScale pE G3 drive B ctrl e * h e := by
  intro H
  have hx : prop pE driveE (BE + (-1 / 10 : ℝ) • vRay 2) =
      ![8 / 3 - 19997 / 200000, 8 / 3 + 19997 / 200000, 8 / 3 + 19997 / 200000] := by
    funext e; fin_cases e <;> simp [prop, pre, pE, driveE, BE, vRay] <;> norm_num
  have hclip : ∀ e, vRay 2 e ≠ 0 →
      0 ≤ pre pE driveE BE e ∧ 0 ≤ pre pE driveE (BE + (-1 / 10 : ℝ) • vRay 2) e := by
    intro e _; fin_cases e <;> simp [pre, pE, driveE, BE, vRay] <;> norm_num
  have on1 : GateOn pE G3 (prop pE driveE (BE + (-1 / 10 : ℝ) • vRay 2)) :=
    ⟨0, by rw [hx]; simp [pE]; norm_num⟩
  have key := congrFun (H driveE BE (vRay 2) (-1 / 10) (ctrlPlus 2) hclip
    ⟨fun _ => on1, fun _ => gateOn_BE⟩ ker_ctrlPlus_two hc0_BE) 1
  rw [stepB_of_on on1, stepB_BE, branchScale_of_on 1 gateOn_BE, sc_BE] at key
  simp only [gated] at key
  rw [hx] at key
  simp only [sc] at key
  simp [scale, pE, sE, vRay] at key
  norm_num at key

/-- Drive at coherence `R = 0`: `(η+μ)·0 - μ = -3/100`. -/
def driveZ : Fin 3 → ℝ := fun _ => (4 / 100 + 3 / 100) * 0 - 3 / 100

/-- **`hclip` is needed, engine parameters.** `B = 0`, `R = 0`, `h = vRay 2`, `t = 1/1000`: the
proposal is `0` at the base and `(a, 0, 0)` (`a = 13997/20000000`) at the perturbed state
(edges 1, 2 clipped), the gate is off at both, every other hypothesis holds (all scales are `1`);
on edge 1 the map stays `0`, the claim gives `-t (1 - γdt)`. -/
theorem engine_false_drop_clip : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (GateOn pE G3 (prop pE drive B) ↔ GateOn pE G3 (prop pE drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl pE G3 (prop pE drive B) ctrl →
    IsCtrl pE G3 (prop pE drive (B + t • h)) ctrl →
    stepB pE G3 drive (B + t • h) =
      fun e => stepB pE G3 drive B e +
        t * (1 - pE.γ * pE.dt) * branchScale pE G3 drive B ctrl e * h e := by
  intro H
  have hx0 : prop pE driveZ 0 = ![0, 0, 0] := by
    funext e; fin_cases e <;> simp [prop, pre, pE, driveZ] <;> norm_num
  have hx1 : prop pE driveZ (0 + (1 / 1000 : ℝ) • vRay 2) = ![13997 / 20000000, 0, 0] := by
    funext e; fin_cases e <;> simp [prop, pre, pE, driveZ, vRay] <;> norm_num
  have off : ∀ a : ℝ, 0 ≤ a → a ≤ 1 / 100 → ¬ GateOn pE G3 ![a, 0, 0] := by
    intro a h0 h1
    rw [gateOn_iff_exists_gt pE G3 engineGate_pE]
    rintro ⟨i, hi⟩
    fin_cases i <;> simp [pE] at hi <;> norm_num at hi <;> linarith
  have off0 : ¬ GateOn pE G3 (prop pE driveZ 0) := by rw [hx0]; exact off 0 le_rfl (by norm_num)
  have off1 : ¬ GateOn pE G3 (prop pE driveZ (0 + (1 / 1000 : ℝ) • vRay 2)) := by
    rw [hx1]; exact off _ (by norm_num) (by norm_num)
  have one : ∀ a : ℝ, 0 ≤ a → a ≤ 1 / 100 → ∀ i, sc pE G3 ![a, 0, 0] i = 1 := by
    intro a h0 h1 i
    have hq : ∀ q : ℝ, 0 ≤ q → q ≤ 1 / 50 → scale pE q = 1 := by
      intro q hq0 hq1
      unfold scale
      apply min_eq_left
      have hε : (0 : ℝ) < pE.ε := by norm_num [pE]
      rw [le_div_iff₀ (by linarith)]
      simp [pE]; norm_num; linarith
    fin_cases i <;> simp only [sc] <;> apply hq <;> simp <;> linarith
  have hct : ∀ a : ℝ, 0 ≤ a → a ≤ 1 / 100 → IsCtrl pE G3 ![a, 0, 0] (ctrlPlus 2) :=
    fun a h0 h1 => isCtrl_of_tied (ctrlPlus_mem 2)
      (fun i j => by rw [one a h0 h1 i, one a h0 h1 j])
  have key := congrFun (H driveZ 0 (vRay 2) (1 / 1000) (ctrlPlus 2) ⟨fun h => absurd h off0,
      fun h => absurd h off1⟩ ker_ctrlPlus_two
    (by rw [hx0]; exact hct 0 le_rfl (by norm_num))
    (by rw [hx1]; exact hct _ (by norm_num) (by norm_num))) 1
  rw [stepB_of_off off0, stepB_of_off off1, branchScale_of_off 1 off0, hx0, hx1] at key
  simp [vRay, pE] at key
  norm_num at key

end

end EngineRedTeam
end AIEFGate
