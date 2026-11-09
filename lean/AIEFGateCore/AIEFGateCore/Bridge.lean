/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.RedTeam
import AIEFGateCore.Pinned.ControllerFiberQuotient
import AIEFGateCore.Pinned.CompleteGraphIncidence

/-!
# (P3) Bridge: the gate's controller kernel is the pinned `CCtrl` / `vCtrl` fiber

`lean/AIEFProofs` (hash-pinned) defines the exceptional K3 controller matrix `CCtrl`
(`ControllerFiber.lean`), its kernel generator `vCtrl`, the projectors `PPar`/`PPerp`
(`ControllerFiberProjector.lean`, `ControllerFiberQuotient.lean`) and the unsigned incidence `inc`
with the K3 rays `vRay` (`CompleteGraphIncidence.lean`), all over `ℚ`. `AIEFGateCore` cannot import
that package (its check script forbids Lake path dependencies), so the four pinned modules are
compiled here **verbatim** under `AIEFGateCore/Pinned/` (namespace `AIEFGate.*` instead of
`AIEFProofs.*`, and the internal `import` lines renamed; nothing else changed). The script
`tools/ci/check_pinned_restatement.py` checks that each restated file equals its pinned
source with exactly those line substitutions, and that the pinned source matches its pinned hash in
`lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt`.

This file proves that the objects used by the gate theorems (`incCoeff`, `incAct`, `InCtrlKer`,
`AIEFGate.vRay`, over `ℝ`) are the pinned objects (over `ℚ`, cast to `ℝ`):

* `incCoeff_eq_inc`, `incAct_toR_eq_mulVec`: for any loopless edge list, the gate's incidence
  coefficient / action is the pinned `inc` / `inc *ᵥ ·`;
* `G3_eq_pinned`, `vRay_eq_pinned`, `vRay_two_eq_vCtrl`: the gate's K3 graph and rays are the pinned
  ones, and the gate's `vRay 2` is the pinned `vCtrl`;
* `incAct_G3_ctrlRow`: rows `0, 1` of the gate's incidence action are the rows of `CCtrl`;
* `inCtrlKer_iff_CCtrl`, `inCtrlKer_iff_exists_smul_vCtrl`, `inCtrlKer_iff_smul_vCtrl`: for every
  controller assignment with `J ⊆ {0, 1}` (the audit's gate component), the kernel hypothesis `hker`
  of `stepB_add_smul_of_branch` is exactly `CCtrl *ᵥ x = 0`, i.e. `x ∈ ℚ · vCtrl` (pinned
  `CCtrl_mulVec_eq_zero_iff_exists_smul`), and over `ℝ`, `h ∈ ℝ · vCtrl`;
* `sc_ctrl_eq_of_PPerp_eq`: the controller scales depend on a rational proposal only through the
  pinned transverse part `PPerp` (pinned `CCtrl_eq_iff_PPerp_eq`);
* `stepB_add_smul_vCtrl`: the main gate theorem along the pinned `vCtrl` with `hker` discharged;
* red team: `false_bridge_wrong_vector` (kernel claimed to be spanned by the pinned `vRay 0`) and
  `false_bridge_any_ctrl` (the restriction `J ⊆ {0, 1}` dropped) are refuted.

Scope: K3 and the fixed edge order `(0,1), (0,2), (1,2)` (the pinned `src3`/`dst3`); the node
relabelling `[2, 7, 11] ↦ 0, 1, 2` of the audit is an external correspondence, as in the pinned
files. Nothing here says that the engine selects this controller set.
-/

set_option autoImplicit false

namespace AIEFGate
namespace Bridge

open Matrix Finset
open ControllerFiber (CCtrl vCtrl PPerp)
open CompleteGraphIncidence (inc src3 dst3)
open RedTeam (ctrlPlus_two ker_ctrlPlus_two)

/-- Real cast of a rational edge vector. -/
def toR {m : ℕ} (x : Fin m → ℚ) : Fin m → ℝ := fun e => (x e : ℝ)

@[simp] theorem toR_apply {m : ℕ} (x : Fin m → ℚ) (e : Fin m) : toR x e = (x e : ℝ) := rfl

/-! ## General edge lists: the gate's incidence is the pinned `inc` -/

/-- For a loopless edge list the gate's incidence coefficient is the pinned `inc` entry. -/
theorem incCoeff_eq_inc {n m : ℕ} (src dst : Fin m → Fin n) (hl : ∀ e, src e ≠ dst e)
    (i : Fin n) (e : Fin m) :
    incCoeff (⟨src, dst⟩ : Graph (Fin n) (Fin m)) i e = ((inc src dst i e : ℚ) : ℝ) := by
  unfold incCoeff inc
  simp only [@eq_comm _ i]
  by_cases h1 : src e = i <;> by_cases h2 : dst e = i
  · exact absurd (h1.trans h2.symm) (hl e)
  all_goals simp [h1, h2]

/-- The gate's incidence action on a rational vector is the pinned `inc *ᵥ x`, cast to `ℝ`. -/
theorem incAct_toR_eq_mulVec {n m : ℕ} (src dst : Fin m → Fin n) (hl : ∀ e, src e ≠ dst e)
    (x : Fin m → ℚ) (i : Fin n) :
    incAct (⟨src, dst⟩ : Graph (Fin n) (Fin m)) (toR x) i = (((inc src dst) *ᵥ x) i : ℝ) := by
  simp only [incAct, incCoeff_eq_inc src dst hl, toR, mulVec, dotProduct, Rat.cast_sum,
    Rat.cast_mul]

/-- The gate's full kernel condition is the pinned `inc *ᵥ x = 0`. -/
theorem incAct_toR_eq_zero_iff {n m : ℕ} (src dst : Fin m → Fin n) (hl : ∀ e, src e ≠ dst e)
    (x : Fin m → ℚ) :
    (∀ i, incAct (⟨src, dst⟩ : Graph (Fin n) (Fin m)) (toR x) i = 0) ↔ inc src dst *ᵥ x = 0 := by
  simp only [incAct_toR_eq_mulVec src dst hl, Rat.cast_eq_zero]
  exact ⟨fun h => funext h, fun h i => congrFun h i⟩

/-! ## K3: graph, rays, controller rows -/

/-- The gate's K3 graph is the pinned edge list `(src3, dst3)`. -/
theorem G3_eq_pinned : G3 = ⟨src3, dst3⟩ := rfl

theorem G3_loopless : ∀ e, src3 e ≠ dst3 e := G3_src_ne_dst

/-- The gate's rays are the pinned rays (cast to `ℝ`). -/
theorem vRay_eq_pinned (c : Fin 3) : vRay c = toR (CompleteGraphIncidence.vRay c) := by
  funext e
  fin_cases c <;> fin_cases e <;> simp [vRay, CompleteGraphIncidence.vRay, src3, dst3]

/-- **The gate's direction `vRay 2` is the pinned `vCtrl`** (via the pinned
`CompleteGraphIncidence.vRay_two_eq_vCtrl`). -/
theorem vRay_two_eq_vCtrl : vRay 2 = toR vCtrl := by
  rw [vRay_eq_pinned, CompleteGraphIncidence.vRay_two_eq_vCtrl]

/-- Rows `0, 1` of the gate's incidence action are the rows of the pinned `CCtrl` (via the pinned
`inc3_rows_eq_CCtrl`). -/
theorem incAct_G3_ctrlRow (x : Fin 3 → ℚ) (i : Fin 2) :
    incAct G3 (toR x) (Fin.castSucc i) = ((CCtrl *ᵥ x) i : ℝ) := by
  rw [G3_eq_pinned, incAct_toR_eq_mulVec src3 dst3 G3_loopless]
  congr 1
  simp only [mulVec, dotProduct, CompleteGraphIncidence.inc3_rows_eq_CCtrl]

/-- A K3 controller assignment whose controller set avoids node 2 (`J ⊆ {0, 1}`, the audit's gate
component, nodes `[2, 7, 11] ↦ 0, 1, 2`). -/
def CtrlJ01 (ctrl : Fin 3 → Fin 3) : Prop :=
  (∀ e, ctrl e = G3.src e ∨ ctrl e = G3.dst e) ∧ ∀ e, ctrl e ≠ 2

/-- On a `J ⊆ {0,1}` assignment, edge `(0,2)` is controlled by `0` and edge `(1,2)` by `1`. -/
theorem CtrlJ01.forced {ctrl : Fin 3 → Fin 3} (hc : CtrlJ01 ctrl) :
    ctrl 1 = 0 ∧ ctrl 2 = 1 ∧ (ctrl 0 = 0 ∨ ctrl 0 = 1) := by
  obtain ⟨hm, h2⟩ := hc
  refine ⟨?_, ?_, ?_⟩
  · rcases hm 1 with h | h
    · simpa using h
    · exact absurd (by simpa using h) (h2 1)
  · rcases hm 2 with h | h
    · simpa using h
    · exact absurd (by simpa using h) (h2 2)
  · rcases hm 0 with h | h
    · left; simpa using h
    · right; simpa using h

/-- Both `J ⊆ {0,1}` assignments used by `K3_gate_component_multiplier` satisfy `CtrlJ01`. -/
theorem ctrlJ01_001 : CtrlJ01 ![0, 0, 1] :=
  ⟨fun e => by fin_cases e <;> simp, fun e => by fin_cases e <;> decide⟩

theorem ctrlJ01_101 : CtrlJ01 ![1, 0, 1] :=
  ⟨fun e => by fin_cases e <;> simp, fun e => by fin_cases e <;> decide⟩

theorem ctrlJ01_ctrlPlus_two : CtrlJ01 (ctrlPlus 2) := by
  rw [ctrlPlus_two]; exact ctrlJ01_001

/-- `InCtrlKer` for a `J ⊆ {0,1}` assignment is the pair of row conditions at nodes `0, 1`. -/
theorem inCtrlKer_iff_rows {ctrl : Fin 3 → Fin 3} (hc : CtrlJ01 ctrl) (h : Fin 3 → ℝ) :
    InCtrlKer G3 ctrl h ↔ incAct G3 h 0 = 0 ∧ incAct G3 h 1 = 0 := by
  obtain ⟨h1, h2, h0⟩ := hc.forced
  constructor
  · intro hk
    exact ⟨h1 ▸ hk 1, h2 ▸ hk 2⟩
  · rintro ⟨a, b⟩ e
    fin_cases e
    · rcases h0 with h | h
      · simpa [h] using a
      · simpa [h] using b
    · simpa [h1] using a
    · simpa [h2] using b

/-- **Bridge (matrix form).** For a rational direction and any `J ⊆ {0,1}` controller assignment,
the gate's kernel hypothesis is the pinned `CCtrl *ᵥ x = 0`. -/
theorem inCtrlKer_iff_CCtrl {ctrl : Fin 3 → Fin 3} (hc : CtrlJ01 ctrl) (x : Fin 3 → ℚ) :
    InCtrlKer G3 ctrl (toR x) ↔ CCtrl *ᵥ x = 0 := by
  rw [inCtrlKer_iff_rows hc]
  have r0 := incAct_G3_ctrlRow x 0
  have r1 := incAct_G3_ctrlRow x 1
  simp only [Fin.castSucc_zero, Fin.castSucc_one] at r0 r1
  rw [r0, r1, Rat.cast_eq_zero, Rat.cast_eq_zero]
  constructor
  · rintro ⟨a, b⟩; funext i; fin_cases i
    · exact a
    · exact b
  · intro hz; exact ⟨congrFun hz 0, congrFun hz 1⟩

/-- **Bridge (fiber form).** For a rational direction and any `J ⊆ {0,1}` controller assignment,
the gate's kernel hypothesis holds iff the direction is a rational multiple of the pinned `vCtrl`
(via the pinned `CCtrl_mulVec_eq_zero_iff_exists_smul`). -/
theorem inCtrlKer_iff_exists_smul_vCtrl {ctrl : Fin 3 → Fin 3} (hc : CtrlJ01 ctrl)
    (x : Fin 3 → ℚ) : InCtrlKer G3 ctrl (toR x) ↔ ∃ a : ℚ, x = a • vCtrl :=
  (inCtrlKer_iff_CCtrl hc x).trans (ControllerFiber.CCtrl_mulVec_eq_zero_iff_exists_smul x)

/-- **Bridge (real form).** For every real direction `h` and any `J ⊆ {0,1}` controller
assignment, the gate's kernel hypothesis `InCtrlKer G3 ctrl h` (the `hker` of
`stepB_add_smul_of_branch`) holds iff `h` is a real multiple of the pinned `vCtrl`. -/
theorem inCtrlKer_iff_smul_vCtrl {ctrl : Fin 3 → Fin 3} (hc : CtrlJ01 ctrl) (h : Fin 3 → ℝ) :
    InCtrlKer G3 ctrl h ↔ ∃ a : ℝ, h = a • toR vCtrl := by
  rw [inCtrlKer_iff_rows hc, RedTeam.incAct_eval0, RedTeam.incAct_eval1]
  constructor
  · rintro ⟨a, b⟩
    refine ⟨h 0, funext fun e => ?_⟩
    fin_cases e <;> simp <;> linarith
  · rintro ⟨a, rfl⟩
    simp

/-- The controller scales at a rational proposal depend on it only through the pinned transverse
part `PPerp *ᵥ x` (pinned `CCtrl_eq_iff_PPerp_eq`). -/
theorem sc_ctrl_eq_of_PPerp_eq (p : Params) {ctrl : Fin 3 → Fin 3} (hc : CtrlJ01 ctrl)
    (x y : Fin 3 → ℚ) (hxy : PPerp *ᵥ x = PPerp *ᵥ y) (e : Fin 3) :
    sc p G3 (toR x) (ctrl e) = sc p G3 (toR y) (ctrl e) := by
  have hC := (ControllerFiber.CCtrl_eq_iff_PPerp_eq x y).mpr hxy
  have row : ∀ i : Fin 2, incAct G3 (toR x) (Fin.castSucc i) = incAct G3 (toR y) (Fin.castSucc i) :=
    fun i => by rw [incAct_G3_ctrlRow, incAct_G3_ctrlRow, hC]
  obtain ⟨h1, h2, h0⟩ := hc.forced
  have r0 := row 0
  have r1 := row 1
  simp only [Fin.castSucc_zero, Fin.castSucc_one] at r0 r1
  fin_cases e
  · rcases h0 with h | h
    · simp only [Fin.zero_eta, h, sc, r0]
    · simp only [Fin.zero_eta, h, sc, r1]
  · simp only [Fin.mk_one, h1, sc, r0]
  · simp only [Fin.reduceFinMk, h2, sc, r1]

/-- **Main gate theorem along the pinned `vCtrl`.** For any `J ⊆ {0,1}` controller assignment the
kernel hypothesis is discharged by the bridge, so on the clip/gate/controller branch
`stepB (B + t • a • vCtrl) = stepB B + t (1 - γ dt) · branchScale · (a • vCtrl)`. -/
theorem stepB_add_smul_vCtrl (p : Params) (drive B : Fin 3 → ℝ) (a t : ℝ) (ctrl : Fin 3 → Fin 3)
    (hJ : CtrlJ01 ctrl)
    (hclip : ∀ e, (a • toR vCtrl) e ≠ 0 →
      0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • (a • toR vCtrl)) e)
    (hon : GateOn p G3 (prop p drive B) ↔ GateOn p G3 (prop p drive (B + t • (a • toR vCtrl))))
    (hc0 : IsCtrl p G3 (prop p drive B) ctrl)
    (hc1 : IsCtrl p G3 (prop p drive (B + t • (a • toR vCtrl))) ctrl) :
    stepB p G3 drive (B + t • (a • toR vCtrl)) =
      fun e => stepB p G3 drive B e +
        t * (1 - p.γ * p.dt) * branchScale p G3 drive B ctrl e * (a • toR vCtrl) e :=
  stepB_add_smul_of_branch p G3 drive B _ t ctrl hclip hon
    ((inCtrlKer_iff_smul_vCtrl hJ _).mpr ⟨a, rfl⟩) hc0 hc1

/-! ## Red team: wrong bridge statements are refuted -/

/-- **Wrong kernel vector.** The bridge with the pinned `vCtrl` replaced by the pinned `vRay 0` is
false (`vRay 2` is in the kernel for `ctrl = ![0,0,1]` but is not a multiple of `vRay 0`). -/
theorem false_bridge_wrong_vector : ¬ ∀ (ctrl : Fin 3 → Fin 3), CtrlJ01 ctrl → ∀ h : Fin 3 → ℝ,
    (InCtrlKer G3 ctrl h ↔ ∃ a : ℝ, h = a • toR (CompleteGraphIncidence.vRay 0)) := by
  intro H
  obtain ⟨a, ha⟩ := (H _ ctrlJ01_ctrlPlus_two (vRay 2)).mp ker_ctrlPlus_two
  have h0 := congrFun ha 0
  have h1 := congrFun ha 1
  simp [vRay, CompleteGraphIncidence.vRay, src3, dst3] at h0 h1
  linarith

/-- **Controller set not restricted.** The bridge with `CtrlJ01` weakened to "every edge picks one
of its endpoints" is false (`ctrl = ![0, 0, 2]`: `vCtrl` is not in that kernel). -/
theorem false_bridge_any_ctrl : ¬ ∀ (ctrl : Fin 3 → Fin 3),
    (∀ e, ctrl e = G3.src e ∨ ctrl e = G3.dst e) → ∀ h : Fin 3 → ℝ,
    (InCtrlKer G3 ctrl h ↔ ∃ a : ℝ, h = a • toR vCtrl) := by
  intro H
  have hk := (H ![0, 0, 2] (fun e => by fin_cases e <;> simp) (toR vCtrl)).mpr ⟨1, by simp⟩ 2
  rw [← vRay_two_eq_vCtrl] at hk
  simp only [Matrix.cons_val_two, Matrix.tail_cons, Matrix.head_cons] at hk
  rw [incAct_vRay_self] at hk
  norm_num at hk

end Bridge
end AIEFGate
