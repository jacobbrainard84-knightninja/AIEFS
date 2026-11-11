/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.K3

/-!
# Red team: known-false variants are refuted, and the hypotheses are satisfiable

A concrete all-tied K3 instance (`dt = 1/10`, `γ = 1`, `cap = 1`, `ε = 0`, gate test `1 - q_i < 0`,
`drive = 0`, `B = 1` on every edge: proposal `x = 9/10`, row sums `9/5`, all scales `5/9`).

* `nonvacuous_plus`: the hypotheses of `K3_tied_plus_exact` hold at `t = 1/10` (so the main theorem
  is not vacuous) and the response is `(t (1-γdt) s) • vRay 2 = (1/20) • vRay 2`.
* `false_drop_kernel`: dropping `h ∈ ker A_J` (single-edge direction) makes the affine claim false.
* `false_wrong_constant`: dropping the factor `(1 - γ dt)` makes the claim false.
* `false_two_sided`: dropping the branch condition (using the `+vRay` formula at `t < 0`) is false.
* `false_branch_eq_state`: "exact branch multiplier = state formula" is false when `s₀ ≠ s₁`.
* `false_drop_clip`, `false_drop_hon`, `false_drop_ker`, `false_drop_hc0`, `false_drop_hc1`: the
  main theorem `stepB_add_smul_of_branch` with exactly one hypothesis dropped is false, witnessed by
  an instance where every other hypothesis holds (`false_drop_hon` uses the non-engine gate `pLow`).
-/

set_option autoImplicit false

namespace AIEFGate
namespace RedTeam

noncomputable section

/-- Concrete parameters. -/
def p0 : Params := ⟨1 / 10, 1, 1, 0, 1, 1, 0⟩

/-- Zero drive (`(η+μ) R - μ = 0`). -/
def drive0 : Fin 3 → ℝ := fun _ => 0

/-- Base state: `B = 1` on every edge. -/
def B0 : Fin 3 → ℝ := fun _ => 1

/-- Single-edge direction on edge `(0,1)` (not in any controller kernel containing node 0 or 1). -/
def e0 : Fin 3 → ℝ := ![1, 0, 0]

theorem prop_eval (B : Fin 3 → ℝ) (e : Fin 3) (h : 0 ≤ B e) :
    prop p0 drive0 B e = 9 / 10 * B e := by
  simp only [prop, pre, p0, drive0]
  rw [max_eq_left (by nlinarith)]
  ring

@[simp] theorem incAct_eval0 (x : Fin 3 → ℝ) : incAct G3 x 0 = x 0 + x 1 := by
  simp [incAct_G3, incCoeff]

@[simp] theorem incAct_eval1 (x : Fin 3 → ℝ) : incAct G3 x 1 = x 0 + x 2 := by
  simp [incAct_G3, incCoeff]

@[simp] theorem incAct_eval2 (x : Fin 3 → ℝ) : incAct G3 x 2 = x 1 + x 2 := by
  simp [incAct_G3, incCoeff]

theorem prop_B0 : prop p0 drive0 B0 = fun _ => 9 / 10 := by
  funext e; rw [prop_eval _ _ (by simp [B0])]; simp [B0]

theorem sc_B0 (i : Fin 3) : sc p0 G3 (prop p0 drive0 B0) i = 5 / 9 := by
  rw [prop_B0]
  fin_cases i <;> simp [sc, scale, p0] <;> norm_num

theorem gateOn_of (x : Fin 3 → ℝ) (h : 1 < x 0 + x 1) : GateOn p0 G3 x :=
  ⟨0, by simp only [p0, incAct_eval0]; linarith⟩

theorem stepB_B0 (e : Fin 3) : stepB p0 G3 drive0 B0 e = 1 / 2 := by
  have hon : GateOn p0 G3 (prop p0 drive0 B0) := gateOn_of _ (by rw [prop_B0]; norm_num)
  simp only [stepB, if_pos hon, gated, sc_B0, min_self]
  rw [prop_B0]
  norm_num

/-- Non-vacuity: every hypothesis of `K3_tied_plus_exact` holds at `t = 1/10`, `c = 2`. -/
theorem nonvacuous_plus :
    stepB p0 G3 drive0 (B0 + (1 / 10 : ℝ) • vRay 2) - stepB p0 G3 drive0 B0 =
      ((1 / 20 : ℝ)) • vRay 2 := by
  have hv : ∀ e, 0 ≤ (B0 + (1 / 10 : ℝ) • vRay 2) e := by
    intro e; fin_cases e <;> simp [B0, vRay] <;> norm_num
  have key := K3_tied_plus_exact p0 drive0 B0 2 (1 / 10) (by norm_num) (by simp [p0]; norm_num)
    (by simp [p0])
    (by rw [prop_B0]; simp [p0]; norm_num)
    (fun e => ⟨by simp [pre, p0, drive0, B0]; norm_num, by
      have := hv e; simp only [pre, p0, drive0]; nlinarith⟩)
    (gateOn_of _ (by rw [prop_B0]; norm_num))
    (gateOn_of _ (by
      rw [prop_eval _ _ (hv 0), prop_eval _ _ (hv 1)]; simp [B0, vRay]; norm_num))
    (fun i j => by rw [sc_B0, sc_B0])
  rw [key, sc_B0]
  congr 1
  simp [p0]; norm_num

/-- **Known-false (kernel condition dropped).** Along the single-edge direction `e0` the map is
*not* `B' + t (1-γdt) s e0`: at `t = 1` edge 0 gives `2/3`, the claim gives `1`. -/
theorem false_drop_kernel :
    ¬ ∀ t : ℝ, stepB p0 G3 drive0 (B0 + t • e0) =
        stepB p0 G3 drive0 B0 + (t * (1 - p0.γ * p0.dt) * (5 / 9)) • e0 := by
  intro h
  have h1 := congrFun (h 1) 0
  have hnn : ∀ e, 0 ≤ (B0 + (1 : ℝ) • e0) e := by
    intro e; fin_cases e <;> simp [B0, e0]
  have hon : GateOn p0 G3 (prop p0 drive0 (B0 + (1 : ℝ) • e0)) := gateOn_of _ (by
    rw [prop_eval _ _ (hnn 0), prop_eval _ _ (hnn 1)]; simp [B0, e0]; norm_num)
  have hx : prop p0 drive0 (B0 + (1 : ℝ) • e0) = ![9 / 5, 9 / 10, 9 / 10] := by
    funext e; rw [prop_eval _ _ (hnn e)]; fin_cases e <;> (simp [B0, e0]; try norm_num)
  rw [stepB, if_pos hon, hx] at h1
  simp only [gated, sc, scale, Pi.add_apply, Pi.smul_apply, smul_eq_mul,
    stepB_B0] at h1
  simp [p0, e0] at h1
  norm_num at h1

/-- **Known-false (wrong constant).** The response is not `(t s) • vRay 2` (factor `1 - γdt`
dropped). -/
theorem false_wrong_constant :
    stepB p0 G3 drive0 (B0 + (1 / 10 : ℝ) • vRay 2) - stepB p0 G3 drive0 B0 ≠
      ((1 / 10 : ℝ) * (5 / 9)) • vRay 2 := by
  rw [nonvacuous_plus]
  intro h
  have := congrFun h 0
  simp [vRay] at this
  norm_num at this

/-- **Known-false (branch condition dropped).** The `+vRay 2` formula does not extend to `t < 0`: at
`t = -1/2` edge 1 (at node 2) moves by `0`, the formula says `1/4`. -/
theorem false_two_sided :
    ¬ ∀ t : ℝ, stepB p0 G3 drive0 (B0 + t • vRay 2) - stepB p0 G3 drive0 B0 =
        (t * (1 - p0.γ * p0.dt) * (5 / 9)) • vRay 2 := by
  intro h
  have h1 := congrFun (h (-1 / 2)) 1
  have hnn : ∀ e, 0 ≤ (B0 + (-1 / 2 : ℝ) • vRay 2) e := by
    intro e; fin_cases e <;> simp [B0, vRay] <;> norm_num
  have hx : prop p0 drive0 (B0 + (-1 / 2 : ℝ) • vRay 2) = ![9 / 20, 27 / 20, 27 / 20] := by
    funext e; rw [prop_eval _ _ (hnn e)]; fin_cases e <;> simp [B0, vRay] <;> norm_num
  have hon : GateOn p0 G3 (prop p0 drive0 (B0 + (-1 / 2 : ℝ) • vRay 2)) := gateOn_of _ (by
    rw [hx]; simp; norm_num)
  rw [Pi.sub_apply, stepB, if_pos hon, hx, stepB_B0] at h1
  simp only [gated, sc, scale, Pi.smul_apply, smul_eq_mul] at h1
  simp [p0, vRay] at h1
  norm_num at h1

/-- **Known-false.** The exact branch multiplier of the gate component is not the state formula in
general (`a = 1`, `s₀ = 0`, `s₁ = 1`: `1/3 ≠ 1/2`). -/
theorem false_branch_eq_state :
    ¬ ∀ a s0 s1 : ℝ, a * (min s0 s1 + s0 + s1) / 3 = a * ((s0 + s1) / 2) := by
  intro h
  have := h 1 0 1
  norm_num at this

/-! ## Single-hypothesis counterexamples for the main theorem

Each theorem below is the negation of `stepB_add_smul_of_branch` (specialised to `G3`) with exactly
one hypothesis dropped, witnessed by an instance in which every *other* hypothesis holds. Together
they show that each of `hclip`, `hon`, `hker`, `hc0`, `hc1` is needed for the statement, not only
for its proof. `false_drop_hon` needs a gate test that is not the engine's (`gapQ = -1 < 0`): for
engine-shaped parameters `hon` is redundant (`stepB_add_smul_of_branch_engine`). -/

theorem stepB_of_on {p : Params} {drive B : Fin 3 → ℝ} (h : GateOn p G3 (prop p drive B)) :
    stepB p G3 drive B = gated p G3 (prop p drive B) := by
  simp [stepB, h]

theorem stepB_of_off {p : Params} {drive B : Fin 3 → ℝ} (h : ¬ GateOn p G3 (prop p drive B)) :
    stepB p G3 drive B = prop p drive B := by
  simp [stepB, h]

theorem branchScale_of_on {p : Params} {drive B : Fin 3 → ℝ} {ctrl : Fin 3 → Fin 3} (e : Fin 3)
    (h : GateOn p G3 (prop p drive B)) :
    branchScale p G3 drive B ctrl e = sc p G3 (prop p drive B) (ctrl e) := by
  simp [branchScale, h]

theorem branchScale_of_off {p : Params} {drive B : Fin 3 → ℝ} {ctrl : Fin 3 → Fin 3} (e : Fin 3)
    (h : ¬ GateOn p G3 (prop p drive B)) : branchScale p G3 drive B ctrl e = 1 := by
  simp [branchScale, h]

/-- `ctrlPlus 2 = ![0, 0, 1]`. -/
theorem ctrlPlus_two : ctrlPlus 2 = ![0, 0, 1] := by
  funext e; fin_cases e <;> rfl

theorem isCtrl_of_tied {p : Params} {x : Fin 3 → ℝ} {ctrl : Fin 3 → Fin 3}
    (hmem : ∀ e, ctrl e = G3.src e ∨ ctrl e = G3.dst e) (ht : ∀ i j, sc p G3 x i = sc p G3 x j) :
    IsCtrl p G3 x ctrl :=
  fun e => ⟨hmem e, (ht _ _).le, (ht _ _).le⟩

theorem ker_ctrlPlus_two : InCtrlKer G3 (ctrlPlus 2) (vRay 2) :=
  fun e => incAct_vRay_other 2 _ (ctrlPlus_ne 2 e)

/-- Constant drive `-10`: the proposal is clipped to `0` on every edge. -/
def driveNeg : Fin 3 → ℝ := fun _ => -10

theorem prop_driveNeg (B : Fin 3 → ℝ) (hB : ∀ e, B e ≤ 11 / 10) : prop p0 driveNeg B = 0 := by
  funext e
  have := hB e
  simp only [prop, pre, p0, driveNeg, Pi.zero_apply]
  exact max_eq_right (by nlinarith)

theorem not_gateOn_zero : ¬ GateOn p0 G3 0 := by
  rintro ⟨i, hi⟩
  fin_cases i <;> simp [p0] at hi <;> linarith

/-- **`hclip` is needed.** With `drive = -10` the proposal is clipped to `0` at `B0` and at
`B0 + (1/10) vRay 2`, so `stepB = 0` at both, the gate is off at both, and every other hypothesis
holds; the claimed identity gives `9/100` on edge 0. -/
theorem false_drop_clip : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl p0 G3 (prop p0 drive B) ctrl →
    IsCtrl p0 G3 (prop p0 drive (B + t • h)) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e +
        t * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive B ctrl e * h e := by
  intro H
  have hx0 : prop p0 driveNeg B0 = 0 := prop_driveNeg B0 (by intro e; simp [B0]; norm_num)
  have hx1 : prop p0 driveNeg (B0 + (1 / 10 : ℝ) • vRay 2) = 0 :=
    prop_driveNeg _ (by intro e; fin_cases e <;> simp [B0, vRay] <;> norm_num)
  have hct : IsCtrl p0 G3 0 (ctrlPlus 2) :=
    isCtrl_of_tied (ctrlPlus_mem 2) (fun i j => by simp [sc, incAct])
  have key := congrFun (H driveNeg B0 (vRay 2) (1 / 10) (ctrlPlus 2) (by rw [hx0, hx1])
    ker_ctrlPlus_two (by rw [hx0]; exact hct) (by rw [hx1]; exact hct)) 0
  have off0 : ¬ GateOn p0 G3 (prop p0 driveNeg B0) := by rw [hx0]; exact not_gateOn_zero
  have off1 : ¬ GateOn p0 G3 (prop p0 driveNeg (B0 + (1 / 10 : ℝ) • vRay 2)) := by
    rw [hx1]; exact not_gateOn_zero
  rw [stepB_of_off off0, stepB_of_off off1, branchScale_of_off 0 off0, hx0, hx1] at key
  simp [vRay, p0] at key
  norm_num at key

/-- **`hker` is needed** (main-theorem form of `false_drop_kernel`). Single-edge direction `e0`,
`t = 1`, `ctrl = ![0, 0, 1]`: clip, gate and both controller hypotheses hold; edge 0 is `2/3`, the
claim gives `1`. -/
theorem false_drop_ker : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre p0 drive B e ∧ 0 ≤ pre p0 drive (B + t • h) e) →
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    IsCtrl p0 G3 (prop p0 drive B) ctrl →
    IsCtrl p0 G3 (prop p0 drive (B + t • h)) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e +
        t * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive B ctrl e * h e := by
  intro H
  have hnn : ∀ e, 0 ≤ (B0 + (1 : ℝ) • e0) e := by intro e; fin_cases e <;> simp [B0, e0]
  have hx : prop p0 drive0 (B0 + (1 : ℝ) • e0) = ![9 / 5, 9 / 10, 9 / 10] := by
    funext e; rw [prop_eval _ _ (hnn e)]; fin_cases e <;> (simp [B0, e0]; try norm_num)
  have on0 : GateOn p0 G3 (prop p0 drive0 B0) := gateOn_of _ (by rw [prop_B0]; norm_num)
  have on1 : GateOn p0 G3 (prop p0 drive0 (B0 + (1 : ℝ) • e0)) := gateOn_of _ (by
    rw [hx]; simp; norm_num)
  have hmem : ∀ e, (![0, 0, 1] : Fin 3 → Fin 3) e = G3.src e ∨
      (![0, 0, 1] : Fin 3 → Fin 3) e = G3.dst e := by
    intro e; fin_cases e <;> simp
  have hc1 : IsCtrl p0 G3 (prop p0 drive0 (B0 + (1 : ℝ) • e0)) ![0, 0, 1] := by
    rw [hx]; intro e
    fin_cases e <;> refine ⟨by simp, ?_, ?_⟩ <;> simp [sc, scale, p0] <;> norm_num
  have key := congrFun (H drive0 B0 e0 1 ![0, 0, 1]
    (fun e _ => ⟨by simp [pre, p0, drive0, B0]; norm_num, by
      have := hnn e; simp only [pre, p0, drive0]; nlinarith⟩)
    ⟨fun _ => on1, fun _ => on0⟩ (isCtrl_of_tied hmem (fun i j => by rw [sc_B0, sc_B0])) hc1) 0
  rw [stepB_of_on on1, branchScale_of_on 0 on0, sc_B0, stepB_B0, hx] at key
  simp [gated, sc, scale, p0, e0] at key
  norm_num at key

/-- **`hc1` is needed** (main-theorem form of `false_two_sided`). `t = -1/2` along `vRay 2`: clip,
gate, kernel and the base controller hypothesis hold (all tied); at the perturbed state node 2 has
the smallest scale, so `ctrlPlus 2` is not a controller assignment there. Edge 1 moves by `0`, the
claim gives `1/4`. -/
theorem false_drop_hc1 : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre p0 drive B e ∧ 0 ≤ pre p0 drive (B + t • h) e) →
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl p0 G3 (prop p0 drive B) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e +
        t * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive B ctrl e * h e := by
  intro H
  have hnn : ∀ e, 0 ≤ (B0 + (-1 / 2 : ℝ) • vRay 2) e := by
    intro e; fin_cases e <;> simp [B0, vRay] <;> norm_num
  have hx : prop p0 drive0 (B0 + (-1 / 2 : ℝ) • vRay 2) = ![9 / 20, 27 / 20, 27 / 20] := by
    funext e; rw [prop_eval _ _ (hnn e)]; fin_cases e <;> simp [B0, vRay] <;> norm_num
  have on0 : GateOn p0 G3 (prop p0 drive0 B0) := gateOn_of _ (by rw [prop_B0]; norm_num)
  have on1 : GateOn p0 G3 (prop p0 drive0 (B0 + (-1 / 2 : ℝ) • vRay 2)) := gateOn_of _ (by
    rw [hx]; simp; norm_num)
  have key := congrFun (H drive0 B0 (vRay 2) (-1 / 2) (ctrlPlus 2)
    (fun e _ => ⟨by simp [pre, p0, drive0, B0]; norm_num, by
      have := hnn e; simp only [pre, p0, drive0]; nlinarith⟩)
    ⟨fun _ => on1, fun _ => on0⟩ ker_ctrlPlus_two
    (isCtrl_of_tied (ctrlPlus_mem 2) (fun i j => by rw [sc_B0, sc_B0]))) 1
  rw [stepB_of_on on1, branchScale_of_on 1 on0, stepB_B0, hx, sc_B0] at key
  simp [gated, sc, scale, p0, vRay] at key
  norm_num at key

/-- Base state for `false_drop_hc0`: `B = (1, 6/5, 6/5)`, so node 2 is the most loaded. -/
def Bc : Fin 3 → ℝ := ![1, 6 / 5, 6 / 5]

/-- **`hc0` is needed.** At `Bc` node 2 has the smallest scale (`25/54 < 50/99`), so `ctrlPlus 2`
is not a controller assignment at the base; at `Bc + (1/10) vRay 2` all three scales tie at `50/99`
(so `hc1` holds), and clip, gate and kernel hold. Edge 1: the map moves by `0`, the claim gives
`-1/22`. -/
theorem false_drop_hc0 : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre p0 drive B e ∧ 0 ≤ pre p0 drive (B + t • h) e) →
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl p0 G3 (prop p0 drive (B + t • h)) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e +
        t * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive B ctrl e * h e := by
  intro H
  have hnn0 : ∀ e, 0 ≤ Bc e := by intro e; fin_cases e <;> simp [Bc] <;> norm_num
  have hnn : ∀ e, 0 ≤ (Bc + (1 / 10 : ℝ) • vRay 2) e := by
    intro e; fin_cases e <;> simp [Bc, vRay] <;> norm_num
  have hx0 : prop p0 drive0 Bc = ![9 / 10, 27 / 25, 27 / 25] := by
    funext e; rw [prop_eval _ _ (hnn0 e)]; fin_cases e <;> simp [Bc] <;> norm_num
  have hx : prop p0 drive0 (Bc + (1 / 10 : ℝ) • vRay 2) = fun _ => 99 / 100 := by
    funext e; rw [prop_eval _ _ (hnn e)]; fin_cases e <;> simp [Bc, vRay] <;> norm_num
  have on0 : GateOn p0 G3 (prop p0 drive0 Bc) := gateOn_of _ (by rw [hx0]; simp; norm_num)
  have on1 : GateOn p0 G3 (prop p0 drive0 (Bc + (1 / 10 : ℝ) • vRay 2)) := gateOn_of _ (by
    rw [hx]; norm_num)
  have hc1 : IsCtrl p0 G3 (prop p0 drive0 (Bc + (1 / 10 : ℝ) • vRay 2)) (ctrlPlus 2) := by
    rw [hx]; exact isCtrl_of_tied (ctrlPlus_mem 2) (fun i j => by
      fin_cases i <;> fin_cases j <;> simp [sc])
  have key := congrFun (H drive0 Bc (vRay 2) (1 / 10) (ctrlPlus 2)
    (fun e _ => ⟨by have := hnn0 e; simp only [pre, p0, drive0]; nlinarith, by
      have := hnn e; simp only [pre, p0, drive0]; nlinarith⟩)
    ⟨fun _ => on1, fun _ => on0⟩ ker_ctrlPlus_two hc1) 1
  rw [stepB_of_on on1, stepB_of_on on0, branchScale_of_on 1 on0, hx, hx0, ctrlPlus_two] at key
  simp [gated, sc, scale, p0, vRay] at key
  norm_num at key

/-- Gate test that fires when some row sum is *below* `17/10` (`gapA = 0`, `gapQ = -1`,
`gapDelta = 17/10`); otherwise as `p0`. Not an engine gate: the engine has `gapQ = config.q > 0` and
`cap = (gapA - gapDelta)/gapQ`. -/
def pLow : Params := ⟨1 / 10, 1, 1, 0, 0, -1, 17 / 10⟩

theorem prop_eval_pLow (B : Fin 3 → ℝ) (e : Fin 3) (h : 0 ≤ B e) :
    prop pLow drive0 B e = 9 / 10 * B e := by
  simp only [prop, pre, pLow, drive0]
  rw [max_eq_left (by nlinarith)]
  ring

/-- **`hon` is needed (for general `Params`).** With the non-engine gate test `pLow`, the gate is
off at `B0` (all row sums `9/5`) and on at `B0 + (1/10) vRay 2` (row sum of node 2 drops to
`81/50`); clip, kernel and both controller hypotheses hold. Edge 0 is `11/20`, the claim gives
`99/100`. Limit: `pLow` is not engine-shaped. For engine-shaped parameters
(`EngineGate`: `cap·gapQ = gapA - gapDelta`, `gapQ > 0`, `cap > 0`, `ε > 0`) `hon` is *implied* by
the other hypotheses (`gateOn_iff_of_branch`, `stepB_add_smul_of_branch_engine` in
`GateMap.lean`), so no such counterexample exists there. Note `p0` (`ε = 0`) is not
engine-shaped either. -/
theorem false_drop_hon : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre pLow drive B e ∧ 0 ≤ pre pLow drive (B + t • h) e) →
    InCtrlKer G3 ctrl h →
    IsCtrl pLow G3 (prop pLow drive B) ctrl →
    IsCtrl pLow G3 (prop pLow drive (B + t • h)) ctrl →
    stepB pLow G3 drive (B + t • h) =
      fun e => stepB pLow G3 drive B e +
        t * (1 - pLow.γ * pLow.dt) * branchScale pLow G3 drive B ctrl e * h e := by
  intro H
  have hnn : ∀ e, 0 ≤ (B0 + (1 / 10 : ℝ) • vRay 2) e := by
    intro e; fin_cases e <;> simp [B0, vRay] <;> norm_num
  have hx0 : prop pLow drive0 B0 = fun _ => 9 / 10 := by
    funext e; rw [prop_eval_pLow _ _ (by simp [B0])]; simp [B0]
  have hx : prop pLow drive0 (B0 + (1 / 10 : ℝ) • vRay 2) = ![99 / 100, 81 / 100, 81 / 100] := by
    funext e; rw [prop_eval_pLow _ _ (hnn e)]; fin_cases e <;> simp [B0, vRay] <;> norm_num
  have off0 : ¬ GateOn pLow G3 (prop pLow drive0 B0) := by
    rw [hx0]; rintro ⟨i, hi⟩; fin_cases i <;> simp [pLow] at hi <;> linarith
  have on1 : GateOn pLow G3 (prop pLow drive0 (B0 + (1 / 10 : ℝ) • vRay 2)) :=
    ⟨2, by rw [hx]; simp [pLow]; norm_num⟩
  have hc0 : IsCtrl pLow G3 (prop pLow drive0 B0) (ctrlPlus 2) := by
    rw [hx0]; exact isCtrl_of_tied (ctrlPlus_mem 2) (fun i j => by
      fin_cases i <;> fin_cases j <;> simp [sc])
  have hc1 : IsCtrl pLow G3 (prop pLow drive0 (B0 + (1 / 10 : ℝ) • vRay 2)) (ctrlPlus 2) := by
    rw [hx, ctrlPlus_two]; intro e
    fin_cases e <;> refine ⟨by simp, ?_, ?_⟩ <;> simp [sc, scale, pLow] <;> norm_num
  have key := congrFun (H drive0 B0 (vRay 2) (1 / 10) (ctrlPlus 2)
    (fun e _ => ⟨by simp [pre, pLow, drive0, B0]; norm_num, by
      have := hnn e; simp only [pre, pLow, drive0]; nlinarith⟩)
    ker_ctrlPlus_two hc0 hc1) 0
  rw [stepB_of_on on1, stepB_of_off off0, branchScale_of_off 0 off0, hx, hx0] at key
  simp [gated, sc, scale, pLow, vRay] at key
  norm_num at key


/-! ## P2 red team

* `false_main_no_gamma`, `false_multiplier_no_gamma`: the main theorem / the multiplier formula
with the
  factor `(1 - γ dt)` dropped (mutants M4 / M5 of `lean_mutation_check.py`) are false, on an
  instance
  where every hypothesis holds (`p0`, `drive0`, `B0`, `vRay 2`, `t = 1/10`, `ctrlPlus 2`).
* `false_rel_x_only`, `false_rel_h_only`: the per-edge theorem `stepB_add_smul_of_branch_on` with
its
  edge set `Rel x h` (`x_e ≠ 0 ∨ h_e ≠ 0`) shrunk to `x_e ≠ 0` alone, or to `h_e ≠ 0` alone, is
  false.
* `rel_strictly_weaker`: an instance where the per-edge hypotheses hold but the all-edge kernel
  hypothesis fails for *every* controller assignment, so `stepB_add_smul_of_branch_on` applies where
  `stepB_add_smul_of_branch` cannot.
-/

/-- Perturbed proposal of the standard witness. -/
theorem prop_B0_plus :
    prop p0 drive0 (B0 + (1 / 10 : ℝ) • vRay 2) = ![99 / 100, 81 / 100, 81 / 100] := by
  have hnn : ∀ e, 0 ≤ (B0 + (1 / 10 : ℝ) • vRay 2) e := by
    intro e; fin_cases e <;> simp [B0, vRay] <;> norm_num
  funext e; rw [prop_eval _ _ (hnn e)]; fin_cases e <;> simp [B0, vRay] <;> norm_num

theorem w_clip : ∀ e, vRay 2 e ≠ 0 →
    0 ≤ pre p0 drive0 B0 e ∧ 0 ≤ pre p0 drive0 (B0 + (1 / 10 : ℝ) • vRay 2) e := by
  have hnn : ∀ e, 0 ≤ (B0 + (1 / 10 : ℝ) • vRay 2) e := by
    intro e; fin_cases e <;> simp [B0, vRay] <;> norm_num
  exact fun e _ => ⟨by simp [pre, p0, drive0, B0]; norm_num, by
    have := hnn e; simp only [pre, p0, drive0]; nlinarith⟩

theorem w_on0 : GateOn p0 G3 (prop p0 drive0 B0) := gateOn_of _ (by rw [prop_B0]; norm_num)

theorem w_on1 : GateOn p0 G3 (prop p0 drive0 (B0 + (1 / 10 : ℝ) • vRay 2)) :=
  gateOn_of _ (by rw [prop_B0_plus]; simp; norm_num)

theorem w_hc0 : IsCtrl p0 G3 (prop p0 drive0 B0) (ctrlPlus 2) :=
  isCtrl_of_tied (ctrlPlus_mem 2) (fun i j => by rw [sc_B0, sc_B0])

theorem w_hc1 : IsCtrl p0 G3 (prop p0 drive0 (B0 + (1 / 10 : ℝ) • vRay 2)) (ctrlPlus 2) := by
  rw [prop_B0_plus, ctrlPlus_two]; intro e
  fin_cases e <;> refine ⟨by simp, ?_, ?_⟩ <;> simp [sc, scale, p0] <;> norm_num

/-- **M4 is false.** The main theorem with the factor `(1 - γ dt)` dropped fails on an instance
where
every hypothesis holds: on edge 0 the map moves by `1/20`, the mutant claims `1/18`. -/
theorem false_main_no_gamma : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre p0 drive B e ∧ 0 ≤ pre p0 drive (B + t • h) e) →
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl p0 G3 (prop p0 drive B) ctrl →
    IsCtrl p0 G3 (prop p0 drive (B + t • h)) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e + t * branchScale p0 G3 drive B ctrl e * h e := by
  intro H
  have hon : GateOn p0 G3 (prop p0 drive0 B0) ↔
      GateOn p0 G3 (prop p0 drive0 (B0 + (1 / 10 : ℝ) • vRay 2)) := ⟨fun _ => w_on1, fun _ => w_on0⟩
  have hm := congrFun (H drive0 B0 (vRay 2) (1 / 10) (ctrlPlus 2) w_clip hon ker_ctrlPlus_two
    w_hc0 w_hc1) 0
  have ht := congrFun (stepB_add_smul_of_branch p0 G3 drive0 B0 (vRay 2) (1 / 10) (ctrlPlus 2)
    w_clip hon ker_ctrlPlus_two w_hc0 w_hc1) 0
  rw [hm, branchScale_of_on 0 w_on0, sc_B0] at ht
  simp [vRay, p0] at ht

/-- **M5 is false.** The multiplier formula with the factor `(1 - γ dt)` dropped fails on an
instance
where every hypothesis holds: the estimator is `1/2`, the mutant claims `5/9`. -/
theorem false_multiplier_no_gamma : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    t ≠ 0 →
    (∀ e, h e ≠ 0 → 0 ≤ pre p0 drive B e ∧ 0 ≤ pre p0 drive (B + t • h) e) →
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl p0 G3 (prop p0 drive B) ctrl →
    IsCtrl p0 G3 (prop p0 drive (B + t • h)) ctrl →
    (∑ e, (stepB p0 G3 drive (B + t • h) e - stepB p0 G3 drive B e) / t * h e) / ∑ e, h e ^ 2 =
      (∑ e, branchScale p0 G3 drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2 := by
  intro H
  have hon : GateOn p0 G3 (prop p0 drive0 B0) ↔
      GateOn p0 G3 (prop p0 drive0 (B0 + (1 / 10 : ℝ) • vRay 2)) := ⟨fun _ => w_on1, fun _ => w_on0⟩
  have hm := H drive0 B0 (vRay 2) (1 / 10) (ctrlPlus 2) (by norm_num) w_clip hon ker_ctrlPlus_two
    w_hc0 w_hc1
  rw [multiplier_eq_branch_formula p0 G3 drive0 B0 (vRay 2) (1 / 10) (ctrlPlus 2) (by norm_num)
    w_clip hon ker_ctrlPlus_two w_hc0 w_hc1] at hm
  have hbs : ∀ e, branchScale p0 G3 drive0 B0 (ctrlPlus 2) e = 5 / 9 := fun e => by
    rw [branchScale_of_on e w_on0, sc_B0]
  simp only [hbs, vRay_sq, Fin.sum_univ_three] at hm
  simp [p0] at hm
  norm_num at hm

/-- Base for `false_rel_x_only`: edge `(0,1)` empty, `B = (0, 2, 2)`. -/
def Bx : Fin 3 → ℝ := ![0, 2, 2]

/-- Controller for `false_rel_x_only`: node 2 on edges 1, 2 (node 0 on the empty edge 0). -/
def ctrlX : Fin 3 → Fin 3 := ![0, 2, 2]

/-- **The edge set cannot be shrunk to `x_e ≠ 0`.** Per-edge theorem with `Rel x h` replaced by
`x_e ≠ 0`: at `Bx = (0,2,2)` along `e0`, `t = 1`, every hypothesis holds (edge 0 has `x_0 = 0`, so
it
carries no condition), but edge 0 moves to `1/3` while the claim gives `1/2`. -/
theorem false_rel_x_only : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre p0 drive B e ∧ 0 ≤ pre p0 drive (B + t • h) e) →
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    InCtrlKerOn G3 (fun e => prop p0 drive B e ≠ 0) ctrl h →
    IsCtrlOn p0 G3 (fun e => prop p0 drive B e ≠ 0) (prop p0 drive B) ctrl →
    IsCtrlOn p0 G3 (fun e => prop p0 drive B e ≠ 0) (prop p0 drive (B + t • h)) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e +
        t * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive B ctrl e * h e := by
  intro H
  have hnn0 : ∀ e, 0 ≤ Bx e := by intro e; fin_cases e <;> simp [Bx]
  have hnn : ∀ e, 0 ≤ (Bx + (1 : ℝ) • e0) e := by intro e; fin_cases e <;> simp [Bx, e0]
  have hx0 : prop p0 drive0 Bx = ![0, 9 / 5, 9 / 5] := by
    funext e; rw [prop_eval _ _ (hnn0 e)]; fin_cases e <;> simp [Bx] <;> norm_num
  have hx : prop p0 drive0 (Bx + (1 : ℝ) • e0) = ![9 / 10, 9 / 5, 9 / 5] := by
    funext e; rw [prop_eval _ _ (hnn e)]; fin_cases e <;> simp [Bx, e0] <;> norm_num
  have on0 : GateOn p0 G3 (prop p0 drive0 Bx) := gateOn_of _ (by rw [hx0]; simp; norm_num)
  have on1 : GateOn p0 G3 (prop p0 drive0 (Bx + (1 : ℝ) • e0)) :=
    gateOn_of _ (by rw [hx]; simp; norm_num)
  have hker : InCtrlKerOn G3 (fun e => prop p0 drive0 Bx e ≠ 0) ctrlX e0 := by
    intro e he; rw [hx0] at he; fin_cases e
    · simp at he
    all_goals simp [ctrlX, e0]
  have hc0 : IsCtrlOn p0 G3 (fun e => prop p0 drive0 Bx e ≠ 0) (prop p0 drive0 Bx) ctrlX := by
    intro e he; rw [hx0] at he ⊢; fin_cases e
    · simp at he
    all_goals (refine ⟨by simp [ctrlX], ?_, ?_⟩ <;> simp [ctrlX, sc, scale, p0]; norm_num)
  have hc1 : IsCtrlOn p0 G3 (fun e => prop p0 drive0 Bx e ≠ 0)
      (prop p0 drive0 (Bx + (1 : ℝ) • e0)) ctrlX := by
    intro e he; rw [hx0] at he; rw [hx]; fin_cases e
    · simp at he
    all_goals (refine ⟨by simp [ctrlX], ?_, ?_⟩ <;> simp [ctrlX, sc, scale, p0]; norm_num)
  have key := congrFun (H drive0 Bx e0 1 ctrlX
    (fun e _ => ⟨by have := hnn0 e; simp only [pre, p0, drive0]; nlinarith, by
      have := hnn e; simp only [pre, p0, drive0]; nlinarith⟩)
    ⟨fun _ => on1, fun _ => on0⟩ hker hc0 hc1) 0
  rw [stepB_of_on on1, stepB_of_on on0, branchScale_of_on 0 on0, hx, hx0] at key
  simp [gated, sc, scale, p0, e0, ctrlX] at key
  norm_num at key

/-- Base for `false_rel_h_only`: `B = (2, 2, 1)`, node 0 the most loaded. -/
def Bh : Fin 3 → ℝ := ![2, 2, 1]

/-- Direction for `false_rel_h_only`: `(1, -1, 0)`, zero on edge `(1,2)`, `(A h)_0 = 0`. -/
def hd : Fin 3 → ℝ := ![1, -1, 0]

/-- **The edge set cannot be shrunk to `h_e ≠ 0`.** Per-edge theorem with `Rel x h` replaced by
`h_e ≠ 0`: at `Bh = (2,2,1)` along `hd = (1,-1,0)`, `t = 1/10`, `ctrl = (0,0,1)`, every hypothesis
holds, but on edge 2 (`h_2 = 0`, `x_2 = 9/10 ≠ 0`) the endpoint minimum moves: the map gives
`10/31`,
the claim `1/3`. -/
theorem false_rel_h_only : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre p0 drive B e ∧ 0 ≤ pre p0 drive (B + t • h) e) →
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    InCtrlKerOn G3 (fun e => h e ≠ 0) ctrl h →
    IsCtrlOn p0 G3 (fun e => h e ≠ 0) (prop p0 drive B) ctrl →
    IsCtrlOn p0 G3 (fun e => h e ≠ 0) (prop p0 drive (B + t • h)) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e +
        t * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive B ctrl e * h e := by
  intro H
  have hnn0 : ∀ e, 0 ≤ Bh e := by intro e; fin_cases e <;> simp [Bh]
  have hnn : ∀ e, 0 ≤ (Bh + (1 / 10 : ℝ) • hd) e := by
    intro e; fin_cases e <;> simp [Bh, hd] <;> norm_num
  have hx0 : prop p0 drive0 Bh = ![9 / 5, 9 / 5, 9 / 10] := by
    funext e; rw [prop_eval _ _ (hnn0 e)]; fin_cases e <;> simp [Bh] <;> norm_num
  have hx : prop p0 drive0 (Bh + (1 / 10 : ℝ) • hd) = ![189 / 100, 171 / 100, 9 / 10] := by
    funext e; rw [prop_eval _ _ (hnn e)]; fin_cases e <;> simp [Bh, hd] <;> norm_num
  have on0 : GateOn p0 G3 (prop p0 drive0 Bh) := gateOn_of _ (by rw [hx0]; simp; norm_num)
  have on1 : GateOn p0 G3 (prop p0 drive0 (Bh + (1 / 10 : ℝ) • hd)) :=
    gateOn_of _ (by rw [hx]; simp; norm_num)
  have hker : InCtrlKerOn G3 (fun e => hd e ≠ 0) ![0, 0, 1] hd := by
    intro e he; fin_cases e
    · simp [hd]
    · simp [hd]
    · simp [hd] at he
  have hc0 : IsCtrlOn p0 G3 (fun e => hd e ≠ 0) (prop p0 drive0 Bh) ![0, 0, 1] := by
    intro e he; rw [hx0]; fin_cases e
    · (refine ⟨by simp, ?_, ?_⟩ <;> simp [sc, scale, p0]); norm_num
    · (refine ⟨by simp, ?_, ?_⟩ <;> simp [sc, scale, p0]); norm_num
    · simp [hd] at he
  have hc1 : IsCtrlOn p0 G3 (fun e => hd e ≠ 0) (prop p0 drive0 (Bh + (1 / 10 : ℝ) • hd))
      ![0, 0, 1] := by
    intro e he; rw [hx]; fin_cases e
    · (refine ⟨by simp, ?_, ?_⟩ <;> simp [sc, scale, p0]); norm_num
    · (refine ⟨by simp, ?_, ?_⟩ <;> simp [sc, scale, p0]); norm_num
    · simp [hd] at he
  have key := congrFun (H drive0 Bh hd (1 / 10) ![0, 0, 1]
    (fun e _ => ⟨by have := hnn0 e; simp only [pre, p0, drive0]; nlinarith, by
      have := hnn e; simp only [pre, p0, drive0]; nlinarith⟩)
    ⟨fun _ => on1, fun _ => on0⟩ hker hc0 hc1) 2
  rw [stepB_of_on on1, stepB_of_on on0, hx, hx0] at key
  simp [gated, sc, scale, p0, hd] at key
  norm_num at key

/-- Direction for `rel_strictly_weaker`: `(0, 1, -1)`; `(A h)_0 = 1`, `(A h)_1 = -1`,
`(A h)_2 = 0`. -/
def hw : Fin 3 → ℝ := ![0, 1, -1]

/-- **The per-edge hypotheses are strictly weaker than the all-edge ones.** At `Bx = (0,2,2)` along
`hw = (0,1,-1)`, `t = 1/10`, `ctrl = ctrlX = (0,2,2)`: all hypotheses of
`stepB_add_smul_of_branch_on` hold, while `InCtrlKer G3 ctrl hw` (the all-edge kernel hypothesis of
`stepB_add_smul_of_branch`) fails for every controller assignment `ctrl` (edge 0 has no endpoint
with
`(A hw)_i = 0`). The conclusion is then the per-edge theorem's identity. -/
theorem rel_strictly_weaker :
    (∀ ctrl : Fin 3 → Fin 3, (∀ e, ctrl e = G3.src e ∨ ctrl e = G3.dst e) →
      ¬ InCtrlKer G3 ctrl hw) ∧
    (∀ e, hw e ≠ 0 → 0 ≤ pre p0 drive0 Bx e ∧ 0 ≤ pre p0 drive0 (Bx + (1 / 10 : ℝ) • hw) e) ∧
    GateOn p0 G3 (prop p0 drive0 Bx) ∧ GateOn p0 G3 (prop p0 drive0 (Bx + (1 / 10 : ℝ) • hw)) ∧
    InCtrlKerOn G3 (Rel (prop p0 drive0 Bx) hw) ctrlX hw ∧
    IsCtrlOn p0 G3 (Rel (prop p0 drive0 Bx) hw) (prop p0 drive0 Bx) ctrlX ∧
    IsCtrlOn p0 G3 (Rel (prop p0 drive0 Bx) hw) (prop p0 drive0 (Bx + (1 / 10 : ℝ) • hw)) ctrlX ∧
    stepB p0 G3 drive0 (Bx + (1 / 10 : ℝ) • hw) =
      fun e => stepB p0 G3 drive0 Bx e +
        (1 / 10) * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive0 Bx ctrlX e * hw e := by
  have hnn0 : ∀ e, 0 ≤ Bx e := by intro e; fin_cases e <;> simp [Bx]
  have hnn : ∀ e, 0 ≤ (Bx + (1 / 10 : ℝ) • hw) e := by
    intro e; fin_cases e <;> simp [Bx, hw] <;> norm_num
  have hx0 : prop p0 drive0 Bx = ![0, 9 / 5, 9 / 5] := by
    funext e; rw [prop_eval _ _ (hnn0 e)]; fin_cases e <;> simp [Bx] <;> norm_num
  have hx : prop p0 drive0 (Bx + (1 / 10 : ℝ) • hw) = ![0, 189 / 100, 171 / 100] := by
    funext e; rw [prop_eval _ _ (hnn e)]; fin_cases e <;> simp [Bx, hw] <;> norm_num
  have hclip : ∀ e, hw e ≠ 0 → 0 ≤ pre p0 drive0 Bx e ∧
      0 ≤ pre p0 drive0 (Bx + (1 / 10 : ℝ) • hw) e :=
    fun e _ => ⟨by have := hnn0 e; simp only [pre, p0, drive0]; nlinarith, by
      have := hnn e; simp only [pre, p0, drive0]; nlinarith⟩
  have on0 : GateOn p0 G3 (prop p0 drive0 Bx) := ⟨2, by rw [hx0]; simp [p0]; norm_num⟩
  have on1 : GateOn p0 G3 (prop p0 drive0 (Bx + (1 / 10 : ℝ) • hw)) :=
    ⟨2, by rw [hx]; simp [p0]; norm_num⟩
  have hrel : ∀ e, Rel (prop p0 drive0 Bx) hw e ↔ e ≠ 0 := by
    intro e; rw [hx0]; fin_cases e <;> simp [Rel, hw]
  have hker : InCtrlKerOn G3 (Rel (prop p0 drive0 Bx) hw) ctrlX hw := by
    intro e he; rw [hrel] at he; fin_cases e
    · exact absurd rfl he
    all_goals simp [ctrlX, hw]
  have hc0 : IsCtrlOn p0 G3 (Rel (prop p0 drive0 Bx) hw) (prop p0 drive0 Bx) ctrlX := by
    intro e he; rw [hrel] at he; rw [hx0]; fin_cases e
    · exact absurd rfl he
    all_goals (refine ⟨by simp [ctrlX], ?_, ?_⟩ <;> simp [ctrlX, sc, scale, p0]; norm_num)
  have hc1 : IsCtrlOn p0 G3 (Rel (prop p0 drive0 Bx) hw)
      (prop p0 drive0 (Bx + (1 / 10 : ℝ) • hw)) ctrlX := by
    intro e he; rw [hrel] at he; rw [hx]; fin_cases e
    · exact absurd rfl he
    all_goals (refine ⟨by simp [ctrlX], ?_, ?_⟩ <;> simp [ctrlX, sc, scale, p0]; norm_num)
  refine ⟨?_, hclip, on0, on1, hker, hc0, hc1,
    stepB_add_smul_of_branch_on p0 G3 drive0 Bx hw (1 / 10) ctrlX hclip ⟨fun _ => on1, fun _ => on0⟩
      hker hc0 hc1⟩
  intro ctrl hmem hk
  have h0 := hk 0
  rcases hmem 0 with h | h <;> rw [h] at h0 <;> simp [hw] at h0

end

end RedTeam
end AIEFGate
