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

end

end RedTeam
end AIEFGate
