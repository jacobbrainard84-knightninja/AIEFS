/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import Mathlib.Analysis.Calculus.Deriv.Add
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Analysis.Calculus.Deriv.Inv
import Mathlib.Analysis.Calculus.Deriv.Comp
import Mathlib.Analysis.Calculus.Deriv.Shift
import Mathlib.Topology.Algebra.Order.Field
import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Fin.VecNotation
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.FunProp
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Push
import Mathlib.Tactic.Linter

/-!
# Branch-conditional affinity of the one-step capacity-gate map

Real-arithmetic model of the `B` part of one engine-v1 `advance_state` step
(`aief_experiment_engine_v1.py:790-823`) with the coherence `R` held fixed (ERRATA E5: `R` is
computed before `B` is read in the step, so a `B`-only perturbation does not change it):

* proposal  `x = max(B + dt (drive - γ B), 0)` per edge, with `drive = (η+μ) R - μ`;
* row sums  `q_i = Σ_{e ∋ i} x_e` (unsigned incidence);
* scales    `s_i = min 1 (c / (q_i + ε))`;
* gate      `B'_e = x_e · min (s_src e) (s_dst e)` if the gate test fires, `B'_e = x_e` otherwise.

Main result (`stepB_add_smul_of_branch`): on a fixed branch (same clip pattern on the support of
`h`, same gate decision, a fixed controller endpoint `ctrl e` that wins or ties the endpoint minimum
on every edge at both states) and for a direction `h` in the controller kernel (`(A h)_{ctrl e} = 0`
for all `e`),

  `stepB (B + t • h) = stepB B + t (1 - γ dt) · s_ctrl · h`   (exactly, coordinatewise).

So the map is affine along `h` and the Rayleigh multiplier `⟨ΔB', h⟩ / (t ⟨h, h⟩)` is the
`t`-independent constant `(1 - γ dt) Σ s_ctrl(e) h_e² / Σ h_e²` (`multiplier_eq_branch_formula`).

Scope: real numbers, not float64; edge-vector form (one coordinate per unordered pair), not the
symmetric 12 × 12 matrix; one step only. Nothing here is about phases, delay, the EMA, persistence
of the branch over time, or the closed-form clique multiplier `λ_k`.
-/

set_option autoImplicit false

namespace AIEFGate

open Finset

/-- Scalar engine parameters entering the `B` update and the capacity gate. `gapA - gapQ * q_i <
gapDelta` is the engine's gate test (`config.a`, `config.q`, `config.delta`).
-/
structure Params where
  dt : ℝ
  γ : ℝ
  cap : ℝ
  ε : ℝ
  gapA : ℝ
  gapQ : ℝ
  gapDelta : ℝ

/-- An edge list: the two endpoints of every edge. -/
structure Graph (V E : Type*) where
  src : E → V
  dst : E → V

noncomputable section

section Proposal

variable {E : Type*} (p : Params)

/-- Pre-clip proposal `B + dt (drive - γ B)` (engine `:790-794`, with `drive = (η+μ) R - μ`). -/
def pre (drive B : E → ℝ) (e : E) : ℝ :=
  B e + p.dt * (drive e - p.γ * B e)

/-- Clipped proposal `max(pre, 0)` (engine `:795`). -/
def prop (drive B : E → ℝ) (e : E) : ℝ :=
  max (pre p drive B e) 0

/-- Endpoint scale `min(1, c / (q + ε))` (engine `:811`). -/
def scale (q : ℝ) : ℝ :=
  min 1 (p.cap / (q + p.ε))

theorem pre_add_smul (drive B h : E → ℝ) (t : ℝ) (e : E) :
    pre p drive (B + t • h) e = pre p drive B e + t * (1 - p.γ * p.dt) * h e := by
  simp only [pre, Pi.add_apply, Pi.smul_apply, smul_eq_mul]
  ring

/-- Clip branch: if the pre-clip proposal is nonnegative at both states on every edge where `h ≠ 0`,
the clipped proposal moves affinely: `x(B + t h) = x(B) + t (1 - γ dt) h`. -/
theorem prop_add_smul_of_clip (drive B h : E → ℝ) (t : ℝ)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e) :
    prop p drive (B + t • h) = prop p drive B + (t * (1 - p.γ * p.dt)) • h := by
  funext e
  simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul]
  by_cases he : h e = 0
  · simp only [prop, pre_add_smul, he, mul_zero, add_zero]
  · obtain ⟨h0, h1⟩ := hclip e he
    simp only [prop, max_eq_left h0, max_eq_left h1]
    rw [pre_add_smul]

end Proposal

variable {V E : Type*} [DecidableEq V] [Fintype E]
variable (p : Params) (G : Graph V E)

/-- Unsigned incidence coefficient `A_{i e}` (1 per endpoint equal to `i`). -/
def incCoeff (i : V) (e : E) : ℝ :=
  (if G.src e = i then 1 else 0) + (if G.dst e = i then 1 else 0)

/-- Unsigned incidence action `(A h)_i = Σ_e A_{i e} h_e`; for `h = x` this is the row sum `q_i`. -/
def incAct (h : E → ℝ) (i : V) : ℝ :=
  ∑ e, incCoeff G i e * h e

/-- Endpoint scale of node `i` for proposal `x`. -/
def sc (x : E → ℝ) (i : V) : ℝ :=
  scale p (incAct G x i)

/-- Gated output `x_e · min(s_src, s_dst)` (engine `:812`). -/
def gated (x : E → ℝ) (e : E) : ℝ :=
  x e * min (sc p G x (G.src e)) (sc p G x (G.dst e))

/-- Engine gate test `min_i (a - q · q_i) < delta` (engine `:804-805`). -/
def GateOn (x : E → ℝ) : Prop :=
  ∃ i, p.gapA - p.gapQ * incAct G x i < p.gapDelta

open Classical in
/-- One `B`-only engine step: gate applied iff the gate test fires (engine `:808-823`). -/
def stepB (drive B : E → ℝ) : E → ℝ :=
  if GateOn p G (prop p drive B) then gated p G (prop p drive B) else prop p drive B

/-- `ctrl` is a controller assignment for `x`: on every edge it picks an endpoint whose scale is `≤`
the other endpoint's (it wins or ties the endpoint minimum). -/
def IsCtrl (x : E → ℝ) (ctrl : E → V) : Prop :=
  ∀ e, (ctrl e = G.src e ∨ ctrl e = G.dst e) ∧
    sc p G x (ctrl e) ≤ sc p G x (G.src e) ∧ sc p G x (ctrl e) ≤ sc p G x (G.dst e)

/-- `h` lies in the controller kernel `ker A_J`, `J = range ctrl`. -/
def InCtrlKer (ctrl : E → V) (h : E → ℝ) : Prop :=
  ∀ e, incAct G h (ctrl e) = 0

/-- (P2) The edges that matter for the one-step identity along `h` at the base proposal `x`:
`x_e ≠ 0` or `h_e ≠ 0`. On every other edge both sides of the identity are `0` whatever the
controller, so no controller or kernel condition is needed there. -/
def Rel (x h : E → ℝ) (e : E) : Prop :=
  x e ≠ 0 ∨ h e ≠ 0

/-- (P2) `IsCtrl` required only on the edges satisfying `S`. -/
def IsCtrlOn (S : E → Prop) (x : E → ℝ) (ctrl : E → V) : Prop :=
  ∀ e, S e → (ctrl e = G.src e ∨ ctrl e = G.dst e) ∧
    sc p G x (ctrl e) ≤ sc p G x (G.src e) ∧ sc p G x (ctrl e) ≤ sc p G x (G.dst e)

/-- (P2) `InCtrlKer` required only on the edges satisfying `S`: `(A h)_{ctrl e} = 0` for `S e`. -/
def InCtrlKerOn (S : E → Prop) (ctrl : E → V) (h : E → ℝ) : Prop :=
  ∀ e, S e → incAct G h (ctrl e) = 0

/-- The all-edge controller hypothesis implies the restricted one, for any edge set `S`. -/
theorem isCtrlOn_of_isCtrl {x : E → ℝ} {ctrl : E → V} (hc : IsCtrl p G x ctrl) (S : E → Prop) :
    IsCtrlOn p G S x ctrl := fun e _ => hc e

/-- The all-edge kernel hypothesis implies the restricted one, for any edge set `S`. -/
theorem inCtrlKerOn_of_inCtrlKer {ctrl : E → V} {h : E → ℝ} (hk : InCtrlKer G ctrl h)
    (S : E → Prop) : InCtrlKerOn G S ctrl h := fun e _ => hk e

/-! ## Linear-algebra lemmas -/

theorem incAct_add_smul (x h : E → ℝ) (u : ℝ) (i : V) :
    incAct G (x + u • h) i = incAct G x i + u * incAct G h i := by
  simp only [incAct, Pi.add_apply, Pi.smul_apply, smul_eq_mul, mul_add, sum_add_distrib, mul_sum]
  congr 1
  refine sum_congr rfl fun e _ => ?_
  ring

/-- (P2) A node whose row of `A h` vanishes keeps its scale along `h`. -/
theorem sc_add_smul_of_incAct_zero (x h : E → ℝ) (u : ℝ) (i : V) (hi : incAct G h i = 0) :
    sc p G (x + u • h) i = sc p G x i := by
  simp only [sc, incAct_add_smul, hi, mul_zero, add_zero]

/-- On a controller kernel direction the controller scales do not move. -/
theorem sc_ctrl_add_smul (x h : E → ℝ) (u : ℝ) (ctrl : E → V) (hker : InCtrlKer G ctrl h) (e : E) :
    sc p G (x + u • h) (ctrl e) = sc p G x (ctrl e) :=
  sc_add_smul_of_incAct_zero p G x h u (ctrl e) (hker e)

/-- (P2) Per-edge form: if `ctrl e` is a minimal-scale endpoint of `e`, the endpoint minimum is
`s_ctrl(e)`. -/
theorem min_eq_ctrl_edge (x : E → ℝ) (ctrl : E → V) (e : E)
    (hc : (ctrl e = G.src e ∨ ctrl e = G.dst e) ∧
      sc p G x (ctrl e) ≤ sc p G x (G.src e) ∧ sc p G x (ctrl e) ≤ sc p G x (G.dst e)) :
    min (sc p G x (G.src e)) (sc p G x (G.dst e)) = sc p G x (ctrl e) := by
  obtain ⟨hor, h1, h2⟩ := hc
  rcases hor with h | h
  · rw [h] at h2 ⊢; exact min_eq_left h2
  · rw [h] at h1 ⊢; exact min_eq_right h1

theorem min_eq_ctrl (x : E → ℝ) (ctrl : E → V) (hc : IsCtrl p G x ctrl) (e : E) :
    min (sc p G x (G.src e)) (sc p G x (G.dst e)) = sc p G x (ctrl e) :=
  min_eq_ctrl_edge p G x ctrl e (hc e)

/-- (P2) **Gate identity, per-edge hypotheses.** The controller and kernel conditions are needed
only
on the edges with `x_e ≠ 0` or `h_e ≠ 0` (`Rel x h`); on the remaining edges both sides are `0`. -/
theorem gated_add_smul_of_branch_on (x h : E → ℝ) (u : ℝ) (ctrl : E → V)
    (hker : InCtrlKerOn G (Rel x h) ctrl h) (hc0 : IsCtrlOn p G (Rel x h) x ctrl)
    (hc1 : IsCtrlOn p G (Rel x h) (x + u • h) ctrl) :
    gated p G (x + u • h) = fun e => gated p G x e + u * sc p G x (ctrl e) * h e := by
  funext e
  by_cases hr : Rel x h e
  · simp only [gated, min_eq_ctrl_edge p G _ ctrl e (hc0 e hr),
      min_eq_ctrl_edge p G _ ctrl e (hc1 e hr),
      sc_add_smul_of_incAct_zero p G x h u (ctrl e) (hker e hr), Pi.add_apply, Pi.smul_apply,
      smul_eq_mul]
    ring
  · simp only [Rel, not_or, not_not] at hr
    simp [gated, hr.1, hr.2]

/-- **Gate identity.** For a controller-kernel direction, if `ctrl` is a controller assignment at
both `x` and `x + u h`, the gate output moves by exactly `u · s_ctrl(e) · h_e` on every edge. -/
theorem gated_add_smul_of_branch (x h : E → ℝ) (u : ℝ) (ctrl : E → V)
    (hker : InCtrlKer G ctrl h) (hc0 : IsCtrl p G x ctrl) (hc1 : IsCtrl p G (x + u • h) ctrl) :
    gated p G (x + u • h) = fun e => gated p G x e + u * sc p G x (ctrl e) * h e :=
  gated_add_smul_of_branch_on p G x h u ctrl (inCtrlKerOn_of_inCtrlKer G hker _)
    (isCtrlOn_of_isCtrl p G hc0 _) (isCtrlOn_of_isCtrl p G hc1 _)

open Classical in
/-- Effective per-edge scale on the branch: `s_ctrl(e)` if the gate fires at the base proposal, else
1. -/
def branchScale (drive B : E → ℝ) (ctrl : E → V) (e : E) : ℝ :=
  if GateOn p G (prop p drive B) then sc p G (prop p drive B) (ctrl e) else 1

/-- (P2) **Main theorem, per-edge hypotheses.** As `stepB_add_smul_of_branch`, but the kernel and
controller hypotheses are required only on the edges with `x_e ≠ 0` or `h_e ≠ 0`, where
`x = prop drive B` is the base proposal (`Rel x h`). Restricting further to `x_e ≠ 0` alone or to
`h_e ≠ 0` alone is false (`RedTeam.false_rel_x_only`, `RedTeam.false_rel_h_only`). -/
theorem stepB_add_smul_of_branch_on (drive B h : E → ℝ) (t : ℝ) (ctrl : E → V)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hon : GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h)))
    (hker : InCtrlKerOn G (Rel (prop p drive B) h) ctrl h)
    (hc0 : IsCtrlOn p G (Rel (prop p drive B) h) (prop p drive B) ctrl)
    (hc1 : IsCtrlOn p G (Rel (prop p drive B) h) (prop p drive (B + t • h)) ctrl) :
    stepB p G drive (B + t • h) =
      fun e => stepB p G drive B e +
        t * (1 - p.γ * p.dt) * branchScale p G drive B ctrl e * h e := by
  have hx := prop_add_smul_of_clip p drive B h t hclip
  funext e
  by_cases hg : GateOn p G (prop p drive B)
  · have hg' : GateOn p G (prop p drive (B + t • h)) := hon.mp hg
    rw [hx] at hc1 hg'
    have key :=
      gated_add_smul_of_branch_on p G (prop p drive B) h (t * (1 - p.γ * p.dt)) ctrl hker hc0 hc1
    simp only [stepB, branchScale, hg, if_true, hx, hg', key]
  · have hg' : ¬ GateOn p G (prop p drive (B + t • h)) := fun h' => hg (hon.mpr h')
    rw [hx] at hg'
    simp only [stepB, branchScale, hg, if_false, hx, hg', Pi.add_apply, Pi.smul_apply, smul_eq_mul]
    ring

/-- **Main theorem (one step, fixed branch).** Same clip pattern on `supp h`, same gate decision, a
fixed controller assignment at both states, and `h ∈ ker A_J`: then the one-step map is exactly
affine along `h`,
`stepB (B + t h) = stepB B + t (1 - γ dt) · branchScale · h`. -/
theorem stepB_add_smul_of_branch (drive B h : E → ℝ) (t : ℝ) (ctrl : E → V)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hon : GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h)))
    (hker : InCtrlKer G ctrl h)
    (hc0 : IsCtrl p G (prop p drive B) ctrl)
    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl) :
    stepB p G drive (B + t • h) =
      fun e => stepB p G drive B e +
        t * (1 - p.γ * p.dt) * branchScale p G drive B ctrl e * h e := by
  exact stepB_add_smul_of_branch_on p G drive B h t ctrl hclip hon
    (inCtrlKerOn_of_inCtrlKer G hker _) (isCtrlOn_of_isCtrl p G hc0 _)
    (isCtrlOn_of_isCtrl p G hc1 _)

/-- (P2) **Constant multiplier, per-edge hypotheses** (hypotheses of
`stepB_add_smul_of_branch_on`). -/
theorem multiplier_eq_branch_formula_on (drive B h : E → ℝ) (t : ℝ) (ctrl : E → V) (ht : t ≠ 0)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hon : GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h)))
    (hker : InCtrlKerOn G (Rel (prop p drive B) h) ctrl h)
    (hc0 : IsCtrlOn p G (Rel (prop p drive B) h) (prop p drive B) ctrl)
    (hc1 : IsCtrlOn p G (Rel (prop p drive B) h) (prop p drive (B + t • h)) ctrl) :
    (∑ e, (stepB p G drive (B + t • h) e - stepB p G drive B e) / t * h e) / ∑ e, h e ^ 2 =
      (1 - p.γ * p.dt) * (∑ e, branchScale p G drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2 := by
  rw [stepB_add_smul_of_branch_on p G drive B h t ctrl hclip hon hker hc0 hc1]
  congr 1
  rw [mul_sum]
  refine sum_congr rfl fun e _ => ?_
  field_simp
  ring

/-- **Constant multiplier.** Under the hypotheses of `stepB_add_smul_of_branch`, for `t ≠ 0` the
audit's estimator `⟨(B'(B + t h) - B'(B)) / t, h⟩ / ⟨h, h⟩` equals the `t`-independent branch
formula `(1 - γ dt) Σ_e branchScale_e h_e² / Σ_e h_e²`. -/
theorem multiplier_eq_branch_formula (drive B h : E → ℝ) (t : ℝ) (ctrl : E → V) (ht : t ≠ 0)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hon : GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h)))
    (hker : InCtrlKer G ctrl h)
    (hc0 : IsCtrl p G (prop p drive B) ctrl)
    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl) :
    (∑ e, (stepB p G drive (B + t • h) e - stepB p G drive B e) / t * h e) / ∑ e, h e ^ 2 =
      (1 - p.γ * p.dt) * (∑ e, branchScale p G drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2 :=
  multiplier_eq_branch_formula_on p G drive B h t ctrl ht hclip hon
    (inCtrlKerOn_of_inCtrlKer G hker _) (isCtrlOn_of_isCtrl p G hc0 _)
    (isCtrlOn_of_isCtrl p G hc1 _)

/-- (P2) **Exact eigenvector, per-edge hypotheses** (hypotheses of `stepB_add_smul_of_branch_on`).
-/
theorem stepB_sub_eq_smul_of_uniform_on (drive B h : E → ℝ) (t s : ℝ) (ctrl : E → V)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hon : GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h)))
    (hker : InCtrlKerOn G (Rel (prop p drive B) h) ctrl h)
    (hc0 : IsCtrlOn p G (Rel (prop p drive B) h) (prop p drive B) ctrl)
    (hc1 : IsCtrlOn p G (Rel (prop p drive B) h) (prop p drive (B + t • h)) ctrl)
    (hs : ∀ e, h e ≠ 0 → branchScale p G drive B ctrl e = s) :
    stepB p G drive (B + t • h) - stepB p G drive B = (t * (1 - p.γ * p.dt) * s) • h := by
  rw [stepB_add_smul_of_branch_on p G drive B h t ctrl hclip hon hker hc0 hc1]
  funext e
  simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul]
  by_cases he : h e = 0
  · simp [he]
  · rw [hs e he]; ring

/-- **Exact eigenvector (state formula).** If moreover the branch scale is a single constant `s` on
the support of `h` (all controller scales equal, e.g. an all-tied clique), `h` is mapped to a
multiple of itself: `stepB (B + t h) - stepB B = (t (1 - γ dt) s) • h`. -/
theorem stepB_sub_eq_smul_of_uniform (drive B h : E → ℝ) (t s : ℝ) (ctrl : E → V)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hon : GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h)))
    (hker : InCtrlKer G ctrl h)
    (hc0 : IsCtrl p G (prop p drive B) ctrl)
    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl)
    (hs : ∀ e, h e ≠ 0 → branchScale p G drive B ctrl e = s) :
    stepB p G drive (B + t • h) - stepB p G drive B = (t * (1 - p.γ * p.dt) * s) • h :=
  stepB_sub_eq_smul_of_uniform_on p G drive B h t s ctrl hclip hon
    (inCtrlKerOn_of_inCtrlKer G hker _) (isCtrlOn_of_isCtrl p G hc0 _)
    (isCtrlOn_of_isCtrl p G hc1 _) hs

/-! ## Persistence of the clip / gate part of the branch for small `t` -/

open Filter Topology in
/-- If the pre-clip proposal is strictly positive on every edge and the gate test fires at the base
proposal, then for all `t` near `0` the clip pattern is unchanged (nothing clipped) and the gate
still fires at `B + t h`. (The controller part of the branch is *not* covered here: at a tie it can
fail on one side; see `AIEFGateCore.K3`.) -/
theorem eventually_clip_gate (drive B h : E → ℝ) (hpre : ∀ e, 0 < pre p drive B e)
    (hon : GateOn p G (prop p drive B)) :
    ∀ᶠ t in 𝓝 (0 : ℝ),
      (∀ e, 0 ≤ pre p drive (B + t • h) e) ∧ GateOn p G (prop p drive (B + t • h)) := by
  have hcont (e : E) : Tendsto (fun t : ℝ => pre p drive B e + t * (1 - p.γ * p.dt) * h e)
      (𝓝 0) (𝓝 (pre p drive B e)) := by
    have : Continuous fun t : ℝ => pre p drive B e + t * (1 - p.γ * p.dt) * h e := by fun_prop
    simpa using this.tendsto 0
  have hpos : ∀ᶠ t in 𝓝 (0 : ℝ), ∀ e, 0 < pre p drive (B + t • h) e := by
    rw [eventually_all]
    intro e
    filter_upwards [(hcont e).eventually_const_lt (hpre e)] with t ht
    rw [pre_add_smul]; exact ht
  obtain ⟨i, hi⟩ := hon
  have hq : Tendsto (fun t : ℝ => p.gapA - p.gapQ * (incAct G (prop p drive B) i +
      t * (1 - p.γ * p.dt) * incAct G h i)) (𝓝 0)
      (𝓝 (p.gapA - p.gapQ * incAct G (prop p drive B) i)) := by
    have : Continuous fun t : ℝ => p.gapA - p.gapQ * (incAct G (prop p drive B) i +
        t * (1 - p.γ * p.dt) * incAct G h i) := by fun_prop
    simpa using this.tendsto 0
  filter_upwards [hpos, hq.eventually_lt_const hi] with t ht hg
  refine ⟨fun e => (ht e).le, i, ?_⟩
  rw [prop_add_smul_of_clip p drive B h t (fun e _ => ⟨(hpre e).le, (ht e).le⟩), incAct_add_smul]
  convert hg using 2

/-! ## Engine-shaped gate: the gate-decision hypothesis is redundant

In the engine `capacity = (a - delta) / q` with `q > 0`, so the gate test `a - q·q_i < delta` is
`q_i > capacity`. With `cap > 0`, `ε > 0` and nonnegative proposals, the node that fires the gate
has the smallest scale on its edges; if it moved, the controller hypotheses would fail at one of
the states.

Scope: `EngineGate` is the real-arithmetic idealisation of the engine config
(`dt = 1/100`, `γ = 3/200`, `cap = 19/30`, `ε = 10⁻¹²`, `a = 1`, `q = 3/2`, `delta = 1/20`;
see `engineGate_ideal`). The float engine stores `capacity = 0.6333…` rounded, for which
`cap·q - (a - delta) ≈ -4.2e-17 ≠ 0` exactly, so these theorems do not apply verbatim to the
exact-rational transcription of float engine values. -/

/-- Engine-shaped gate parameters. -/
structure EngineGate (p : Params) : Prop where
  link : p.cap * p.gapQ = p.gapA - p.gapDelta
  gapQ_pos : 0 < p.gapQ
  cap_pos : 0 < p.cap
  eps_pos : 0 < p.ε

/-- The idealised engine configuration is engine-shaped (non-vacuity of `EngineGate`). -/
theorem engineGate_ideal :
    EngineGate ⟨1 / 100, 3 / 200, 19 / 30, 1 / 10 ^ 12, 1, 3 / 2, 1 / 20⟩ := by
  constructor <;> norm_num

theorem gateOn_iff_exists_gt (hp : EngineGate p) (x : E → ℝ) :
    GateOn p G x ↔ ∃ i, p.cap < incAct G x i := by
  unfold GateOn
  refine exists_congr fun i => ?_
  constructor
  · intro h; nlinarith [hp.link, hp.gapQ_pos]
  · intro h; nlinarith [hp.link, hp.gapQ_pos]

theorem incAct_nonneg (x : E → ℝ) (hx : ∀ e, 0 ≤ x e) (i : V) : 0 ≤ incAct G x i := by
  unfold incAct incCoeff
  refine Finset.sum_nonneg fun e _ => mul_nonneg ?_ (hx e)
  split_ifs <;> norm_num

/-- (P2) Per-edge form of `gateOn_of_branch_aux`: kernel and controller conditions only on the edges
with `h_e ≠ 0`. -/
theorem gateOn_of_branch_aux_on (hp : EngineGate p) (x h : E → ℝ) (u : ℝ) (ctrl : E → V)
    (hx : ∀ e, 0 ≤ x e) (hker : InCtrlKerOn G (fun e => h e ≠ 0) ctrl h)
    (hc0 : IsCtrlOn p G (fun e => h e ≠ 0) x ctrl)
    (hon : GateOn p G x) : GateOn p G (x + u • h) := by
  rw [gateOn_iff_exists_gt p G hp] at hon ⊢
  obtain ⟨k, hk⟩ := hon
  by_cases hAk : incAct G h k = 0
  · exact ⟨k, by rw [incAct_add_smul, hAk, mul_zero, add_zero]; exact hk⟩
  · obtain ⟨e, -, he⟩ := Finset.exists_ne_zero_of_sum_ne_zero hAk
    have hke : G.src e = k ∨ G.dst e = k := by
      by_contra hne
      push Not at hne
      apply he
      simp [incCoeff, hne.1, hne.2]
    have hhe : h e ≠ 0 := right_ne_zero_of_mul he
    set j := ctrl e
    have hj0 : incAct G h j = 0 := hker e hhe
    have hsk : sc p G x j ≤ sc p G x k := by
      obtain ⟨-, h1, h2⟩ := hc0 e hhe
      rcases hke with h | h
      · rw [← h]; exact h1
      · rw [← h]; exact h2
    have hqk : 0 < incAct G x k + p.ε := by linarith [incAct_nonneg G x hx k, hp.eps_pos]
    have hqj : 0 < incAct G x j + p.ε := by linarith [incAct_nonneg G x hx j, hp.eps_pos]
    have hlt : p.cap / (incAct G x k + p.ε) < 1 := by
      rw [div_lt_one hqk]; linarith [hp.eps_pos]
    have hsk' : sc p G x k = p.cap / (incAct G x k + p.ε) := by
      simp only [sc, scale]; exact min_eq_right hlt.le
    have hsj' : p.cap / (incAct G x j + p.ε) ≤ p.cap / (incAct G x k + p.ε) := by
      have hlt' : sc p G x j < 1 := lt_of_le_of_lt hsk (hsk' ▸ hlt)
      simp only [sc, scale] at hlt'
      have hm : min 1 (p.cap / (incAct G x j + p.ε)) = p.cap / (incAct G x j + p.ε) := by
        rcases min_lt_iff.mp hlt' with h | h
        · exact absurd h (lt_irrefl 1)
        · exact min_eq_right h.le
      have := hsk
      rw [hsk'] at this
      simp only [sc, scale] at this
      rwa [hm] at this
    have hqle : incAct G x k + p.ε ≤ incAct G x j + p.ε :=
      (div_le_div_iff_of_pos_left hp.cap_pos hqj hqk).mp hsj'
    exact ⟨j, by rw [incAct_add_smul, hj0, mul_zero, add_zero]; linarith⟩

theorem gateOn_of_branch_aux (hp : EngineGate p) (x h : E → ℝ) (u : ℝ) (ctrl : E → V)
    (hx : ∀ e, 0 ≤ x e) (hker : InCtrlKer G ctrl h) (hc0 : IsCtrl p G x ctrl)
    (hon : GateOn p G x) : GateOn p G (x + u • h) :=
  gateOn_of_branch_aux_on p G hp x h u ctrl hx (inCtrlKerOn_of_inCtrlKer G hker _)
    (isCtrlOn_of_isCtrl p G hc0 _) hon

/-- (P2) Per-edge form of `gateOn_iff_of_branch` (conditions only on edges with `h_e ≠ 0`). -/
theorem gateOn_iff_of_branch_on (hp : EngineGate p) (x h : E → ℝ) (u : ℝ) (ctrl : E → V)
    (hx : ∀ e, 0 ≤ x e) (hx' : ∀ e, 0 ≤ (x + u • h) e)
    (hker : InCtrlKerOn G (fun e => h e ≠ 0) ctrl h)
    (hc0 : IsCtrlOn p G (fun e => h e ≠ 0) x ctrl)
    (hc1 : IsCtrlOn p G (fun e => h e ≠ 0) (x + u • h) ctrl) :
    GateOn p G x ↔ GateOn p G (x + u • h) := by
  refine ⟨gateOn_of_branch_aux_on p G hp x h u ctrl hx hker hc0, fun hon => ?_⟩
  have := gateOn_of_branch_aux_on p G hp (x + u • h) h (-u) ctrl hx' hker hc1 hon
  have hxx : x + u • h + (-u) • h = x := by
    funext e; simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul]; ring
  rwa [hxx] at this

/-- **The gate-decision hypothesis is implied** for engine-shaped parameters: if `h ∈ ker A_J` and
`ctrl` is a controller assignment at both (nonnegative) proposals, the gate fires at one iff at the
other. -/
theorem gateOn_iff_of_branch (hp : EngineGate p) (x h : E → ℝ) (u : ℝ) (ctrl : E → V)
    (hx : ∀ e, 0 ≤ x e) (hx' : ∀ e, 0 ≤ (x + u • h) e) (hker : InCtrlKer G ctrl h)
    (hc0 : IsCtrl p G x ctrl) (hc1 : IsCtrl p G (x + u • h) ctrl) :
    GateOn p G x ↔ GateOn p G (x + u • h) :=
  gateOn_iff_of_branch_on p G hp x h u ctrl hx hx' (inCtrlKerOn_of_inCtrlKer G hker _)
    (isCtrlOn_of_isCtrl p G hc0 _) (isCtrlOn_of_isCtrl p G hc1 _)

/-- (P2) **Main theorem without `hon`, engine-shaped gate, per-edge hypotheses.** Kernel and
controller conditions only on the edges with `x_e ≠ 0` or `h_e ≠ 0` (`x = prop drive B`). -/
theorem stepB_add_smul_of_branch_engine_on (hp : EngineGate p) (drive B h : E → ℝ) (t : ℝ)
    (ctrl : E → V)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hker : InCtrlKerOn G (Rel (prop p drive B) h) ctrl h)
    (hc0 : IsCtrlOn p G (Rel (prop p drive B) h) (prop p drive B) ctrl)
    (hc1 : IsCtrlOn p G (Rel (prop p drive B) h) (prop p drive (B + t • h)) ctrl) :
    stepB p G drive (B + t • h) =
      fun e => stepB p G drive B e +
        t * (1 - p.γ * p.dt) * branchScale p G drive B ctrl e * h e := by
  have hx := prop_add_smul_of_clip p drive B h t hclip
  have hnn : ∀ (B' : E → ℝ) e, 0 ≤ prop p drive B' e := fun _ _ => le_max_right _ _
  have hon : GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h)) := by
    have hc1' := hc1
    rw [hx]
    rw [hx] at hc1'
    exact gateOn_iff_of_branch_on p G hp _ h _ ctrl (hnn B) (hx ▸ hnn (B + t • h))
      (fun e he => hker e (Or.inr he)) (fun e he => hc0 e (Or.inr he))
      (fun e he => hc1' e (Or.inr he))
  exact stepB_add_smul_of_branch_on p G drive B h t ctrl hclip hon hker hc0 hc1

/-- **Main theorem without `hon`, engine-shaped gate.** -/
theorem stepB_add_smul_of_branch_engine (hp : EngineGate p) (drive B h : E → ℝ) (t : ℝ)
    (ctrl : E → V)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hker : InCtrlKer G ctrl h)
    (hc0 : IsCtrl p G (prop p drive B) ctrl)
    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl) :
    stepB p G drive (B + t • h) =
      fun e => stepB p G drive B e +
        t * (1 - p.γ * p.dt) * branchScale p G drive B ctrl e * h e :=
  stepB_add_smul_of_branch_engine_on p G hp drive B h t ctrl hclip
    (inCtrlKerOn_of_inCtrlKer G hker _) (isCtrlOn_of_isCtrl p G hc0 _)
    (isCtrlOn_of_isCtrl p G hc1 _)

end

end AIEFGate
