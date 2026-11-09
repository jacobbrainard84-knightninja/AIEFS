/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import Mathlib

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

/-! ## Linear-algebra lemmas -/

theorem incAct_add_smul (x h : E → ℝ) (u : ℝ) (i : V) :
    incAct G (x + u • h) i = incAct G x i + u * incAct G h i := by
  simp only [incAct, Pi.add_apply, Pi.smul_apply, smul_eq_mul, mul_add, sum_add_distrib, mul_sum]
  congr 1
  refine sum_congr rfl fun e _ => ?_
  ring

/-- On a controller kernel direction the controller scales do not move. -/
theorem sc_ctrl_add_smul (x h : E → ℝ) (u : ℝ) (ctrl : E → V) (hker : InCtrlKer G ctrl h) (e : E) :
    sc p G (x + u • h) (ctrl e) = sc p G x (ctrl e) := by
  simp only [sc, incAct_add_smul, hker e, mul_zero, add_zero]

theorem min_eq_ctrl (x : E → ℝ) (ctrl : E → V) (hc : IsCtrl p G x ctrl) (e : E) :
    min (sc p G x (G.src e)) (sc p G x (G.dst e)) = sc p G x (ctrl e) := by
  obtain ⟨hor, h1, h2⟩ := hc e
  rcases hor with h | h
  · rw [h] at h2 ⊢; exact min_eq_left h2
  · rw [h] at h1 ⊢; exact min_eq_right h1

/-- **Gate identity.** For a controller-kernel direction, if `ctrl` is a controller assignment at
both `x` and `x + u h`, the gate output moves by exactly `u · s_ctrl(e) · h_e` on every edge. -/
theorem gated_add_smul_of_branch (x h : E → ℝ) (u : ℝ) (ctrl : E → V)
    (hker : InCtrlKer G ctrl h) (hc0 : IsCtrl p G x ctrl) (hc1 : IsCtrl p G (x + u • h) ctrl) :
    gated p G (x + u • h) = fun e => gated p G x e + u * sc p G x (ctrl e) * h e := by
  funext e
  simp only [gated, min_eq_ctrl p G _ ctrl hc0, min_eq_ctrl p G _ ctrl hc1,
    sc_ctrl_add_smul p G x h u ctrl hker, Pi.add_apply, Pi.smul_apply, smul_eq_mul]
  ring

open Classical in
/-- Effective per-edge scale on the branch: `s_ctrl(e)` if the gate fires at the base proposal, else
1. -/
def branchScale (drive B : E → ℝ) (ctrl : E → V) (e : E) : ℝ :=
  if GateOn p G (prop p drive B) then sc p G (prop p drive B) (ctrl e) else 1

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
  have hx := prop_add_smul_of_clip p drive B h t hclip
  funext e
  by_cases hg : GateOn p G (prop p drive B)
  · have hg' : GateOn p G (prop p drive (B + t • h)) := hon.mp hg
    rw [hx] at hc1 hg'
    have key :=
      gated_add_smul_of_branch p G (prop p drive B) h (t * (1 - p.γ * p.dt)) ctrl hker hc0 hc1
    simp only [stepB, branchScale, hg, if_true, hx, hg', key]
  · have hg' : ¬ GateOn p G (prop p drive (B + t • h)) := fun h' => hg (hon.mpr h')
    rw [hx] at hg'
    simp only [stepB, branchScale, hg, if_false, hx, hg', Pi.add_apply, Pi.smul_apply, smul_eq_mul]
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
      (1 - p.γ * p.dt) * (∑ e, branchScale p G drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2 := by
  rw [stepB_add_smul_of_branch p G drive B h t ctrl hclip hon hker hc0 hc1]
  congr 1
  rw [mul_sum]
  refine sum_congr rfl fun e _ => ?_
  field_simp
  ring

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
    stepB p G drive (B + t • h) - stepB p G drive B = (t * (1 - p.γ * p.dt) * s) • h := by
  rw [stepB_add_smul_of_branch p G drive B h t ctrl hclip hon hker hc0 hc1]
  funext e
  simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul]
  by_cases he : h e = 0
  · simp [he]
  · rw [hs e he]; ring

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

end

end AIEFGate
