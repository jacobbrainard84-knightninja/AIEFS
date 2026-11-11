/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.GateMap

/-!
# K3 specialisations of the gate identity

Edges are ordered `(0,1), (0,2), (1,2)` (as `src3`/`dst3` in the pinned `lean/AIEFProofs`). For a
node `c`, `vRay c` is `+1` on the edge opposite `c` and `-1` on the two edges at `c`, so `(A vRay
c)_c = -2` and `(A vRay c)_j = 0` for `j ≠ c`.

* `K3_gate_component_multiplier`: the audit's gate component (nodes `[2,7,11] ↦ 0,1,2`, controllers
  `J = {0,1}`, node 2 untied) has the exact one-step multiplier `(1-γdt)(min s₀ s₁ + s₀ + s₁)/3`
  along `vRay 2`, and this differs from the state formula `(1-γdt)(s₀+s₁)/2` by exactly
  `(1-γdt)|s₀-s₁|/6`.
* `K3_tied_plus_exact` / `K3_tied_plus_hasDerivWithinAt`: all three scales tied; along `+vRay c` (`t
  ≥ 0`) the map is exactly `B' + t (1-γdt) s · vRay c`; right derivative `(1-γdt) s · vRay c`.
* `K3_tied_minus_exact` / `K3_tied_minus_hasDerivWithinAt` / `K3_tied_minus_not_eigen`: along `-vRay
  c` the controller of the two edges at `c` switches to `c`; the exact response there is the
  rational function `(x_e + τa) · cap / (q_c + 2τa + ε)`, whose right derivative `a s (1 - 2
  x_e/(q_c+ε))` is not `a s` unless `x_e = 0`: `-vRay c` is not an eigen-direction.
-/

set_option autoImplicit false

namespace AIEFGate

open Finset Filter Topology

noncomputable section

/-- The K3 edge list `(0,1), (0,2), (1,2)`. -/
def G3 : Graph (Fin 3) (Fin 3) := ⟨![0, 0, 1], ![1, 2, 2]⟩

@[simp] theorem G3_src0 : G3.src 0 = 0 := rfl
@[simp] theorem G3_src1 : G3.src 1 = 0 := rfl
@[simp] theorem G3_src2 : G3.src 2 = 1 := rfl
@[simp] theorem G3_dst0 : G3.dst 0 = 1 := rfl
@[simp] theorem G3_dst1 : G3.dst 1 = 2 := rfl
@[simp] theorem G3_dst2 : G3.dst 2 = 2 := rfl

/-- One-sided K3 direction for node `c`: `-1` on the edges at `c`, `+1` on the opposite edge. -/
def vRay (c : Fin 3) (e : Fin 3) : ℝ :=
  if G3.src e = c ∨ G3.dst e = c then -1 else 1

theorem incAct_G3 (h : Fin 3 → ℝ) (i : Fin 3) :
    incAct G3 h i = incCoeff G3 i 0 * h 0 + incCoeff G3 i 1 * h 1 + incCoeff G3 i 2 * h 2 := by
  simp [incAct, Fin.sum_univ_three]

theorem incAct_vRay_self (c : Fin 3) : incAct G3 (vRay c) c = -2 := by
  rw [incAct_G3]; fin_cases c <;> simp [incCoeff, vRay] <;> norm_num

theorem incAct_vRay_other (c j : Fin 3) (h : j ≠ c) : incAct G3 (vRay c) j = 0 := by
  rw [incAct_G3]; fin_cases c <;> fin_cases j <;> simp_all [incCoeff, vRay]

theorem vRay_sq (c e : Fin 3) : vRay c e ^ 2 = 1 := by
  unfold vRay; split_ifs <;> norm_num

/-- `scale` is antitone in the row sum where `q + ε > 0` and `cap ≥ 0`. -/
theorem scale_anti (p : Params) {q q' : ℝ} (hq : q' ≤ q) (hpos : 0 < q' + p.ε) (hcap : 0 ≤ p.cap) :
    scale p q ≤ scale p q' := by
  unfold scale
  apply min_le_min_left
  exact div_le_div_of_nonneg_left hcap hpos (by linarith)

variable (p : Params) (drive B : Fin 3 → ℝ)

/-! ## The audit's gate component: `J = {0,1}`, node 2 untied -/

/-- **Gate component.** Nodes `0,1` control (node 2's scale is `≥` both at the base and the
perturbed proposal); along `vRay 2` the audit's multiplier estimator equals `(1-γdt)(min s₀ s₁ + s₀
+ s₁)/3` for every admissible `t ≠ 0`. -/
theorem K3_gate_component_multiplier (t : ℝ) (ht : t ≠ 0)
    (hclip : ∀ e, 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • vRay 2) e)
    (hon : GateOn p G3 (prop p drive B)) (hon' : GateOn p G3 (prop p drive (B + t • vRay 2)))
    (h20 : sc p G3 (prop p drive B) 0 ≤ sc p G3 (prop p drive B) 2)
    (h21 : sc p G3 (prop p drive B) 1 ≤ sc p G3 (prop p drive B) 2)
    (h20' : sc p G3 (prop p drive (B + t • vRay 2)) 0 ≤ sc p G3 (prop p drive (B + t • vRay 2)) 2)
    (h21' : sc p G3 (prop p drive (B + t • vRay 2)) 1 ≤ sc p G3 (prop p drive (B + t • vRay 2)) 2) :
    (∑ e, (stepB p G3 drive (B + t • vRay 2) e - stepB p G3 drive B e) / t * vRay 2 e) /
        ∑ e, vRay 2 e ^ 2 =
      (1 - p.γ * p.dt) *
        (min (sc p G3 (prop p drive B) 0) (sc p G3 (prop p drive B) 1) +
          sc p G3 (prop p drive B) 0 + sc p G3 (prop p drive B) 1) / 3 := by
  have hx := prop_add_smul_of_clip p drive B (vRay 2) t (fun e _ => hclip e)
  have hon2 : GateOn p G3 (prop p drive B) ↔ GateOn p G3 (prop p drive (B + t • vRay 2)) :=
    ⟨fun _ => hon', fun _ => hon⟩
  -- the controller scales at nodes 0, 1 do not move
  have hs0 : sc p G3 (prop p drive (B + t • vRay 2)) 0 = sc p G3 (prop p drive B) 0 := by
    simp only [hx, sc, incAct_add_smul, incAct_vRay_other 2 0 (by decide), mul_zero, add_zero]
  have hs1 : sc p G3 (prop p drive (B + t • vRay 2)) 1 = sc p G3 (prop p drive B) 1 := by
    simp only [hx, sc, incAct_add_smul, incAct_vRay_other 2 1 (by decide), mul_zero, add_zero]
  have hsum3 : ∑ e, vRay 2 e ^ 2 = 3 := by simp [vRay_sq]
  have hker_of (ctrl : Fin 3 → Fin 3) (hc : ∀ e, ctrl e ≠ 2) : InCtrlKer G3 ctrl (vRay 2) :=
    fun e => incAct_vRay_other 2 (ctrl e) (hc e)
  by_cases h01 : sc p G3 (prop p drive B) 0 ≤ sc p G3 (prop p drive B) 1
  · let ctrl : Fin 3 → Fin 3 := ![0, 0, 1]
    have hker : InCtrlKer G3 ctrl (vRay 2) := hker_of ctrl (by decide)
    have mk : ∀ y : Fin 3 → ℝ, sc p G3 y 0 ≤ sc p G3 y 1 → sc p G3 y 0 ≤ sc p G3 y 2 →
        sc p G3 y 1 ≤ sc p G3 y 2 → IsCtrl p G3 y ctrl := by
      intro y a b c e
      fin_cases e <;> simp [ctrl, a, b, c]
    have hc0 := mk (prop p drive B) h01 h20 h21
    have hc1 := mk (prop p drive (B + t • vRay 2)) (by rw [hs0, hs1]; exact h01) h20' h21'
    rw [multiplier_eq_branch_formula p G3 drive B (vRay 2) t ctrl ht (fun e _ => hclip e) hon2 hker
      hc0 hc1, hsum3]
    simp [branchScale, hon, Fin.sum_univ_three, vRay_sq, ctrl, min_eq_left h01]
  · push Not at h01
    let ctrl : Fin 3 → Fin 3 := ![1, 0, 1]
    have hker : InCtrlKer G3 ctrl (vRay 2) := hker_of ctrl (by decide)
    have mk : ∀ y : Fin 3 → ℝ, sc p G3 y 1 ≤ sc p G3 y 0 → sc p G3 y 0 ≤ sc p G3 y 2 →
        sc p G3 y 1 ≤ sc p G3 y 2 → IsCtrl p G3 y ctrl := by
      intro y a b c e
      fin_cases e <;> simp [ctrl, a, b, c]
    have hc0 := mk (prop p drive B) h01.le h20 h21
    have hc1 := mk (prop p drive (B + t • vRay 2)) (by rw [hs0, hs1]; exact h01.le) h20' h21'
    rw [multiplier_eq_branch_formula p G3 drive B (vRay 2) t ctrl ht (fun e _ => hclip e) hon2 hker
      hc0 hc1, hsum3]
    simp [branchScale, hon, Fin.sum_univ_three, vRay_sq, ctrl, min_eq_right h01.le]

/-- The exact branch multiplier of the gate component differs from the audit's state formula
`(1-γdt) · mean(s_J)` by exactly `(1-γdt) |s₀ - s₁| / 6`. -/
theorem K3_gate_branch_sub_state (a s0 s1 : ℝ) :
    a * (min s0 s1 + s0 + s1) / 3 - a * ((s0 + s1) / 2) = -(a * |s0 - s1| / 6) := by
  rcases le_total s0 s1 with h | h
  · rw [min_eq_left h, abs_of_nonpos (by linarith)]; ring
  · rw [min_eq_right h, abs_of_nonneg (by linarith)]; ring

/-! ## All-tied K3: one-sided identities along `±vRay c` -/

theorem sc_add_smul_vRay_other (x : Fin 3 → ℝ) (u : ℝ) (c j : Fin 3) (h : j ≠ c) :
    sc p G3 (x + u • vRay c) j = sc p G3 x j := by
  simp only [sc, incAct_add_smul, incAct_vRay_other c j h, mul_zero, add_zero]

theorem sc_add_smul_vRay_self (x : Fin 3 → ℝ) (u : ℝ) (c : Fin 3) :
    sc p G3 (x + u • vRay c) c = scale p (incAct G3 x c - 2 * u) := by
  simp only [sc, incAct_add_smul, incAct_vRay_self]
  ring_nf

theorem G3_src_ne_dst (e : Fin 3) : G3.src e ≠ G3.dst e := by
  fin_cases e <;> decide

/-- Controller for the `+vRay c` side: the endpoint other than `c` (on the opposite edge, `src`). -/
def ctrlPlus (c : Fin 3) (e : Fin 3) : Fin 3 :=
  if G3.src e = c then G3.dst e else G3.src e

theorem ctrlPlus_ne (c e : Fin 3) : ctrlPlus c e ≠ c := by
  unfold ctrlPlus
  split_ifs with h
  · intro h'; exact G3_src_ne_dst e (h.trans h'.symm)
  · exact h

theorem ctrlPlus_mem (c e : Fin 3) : ctrlPlus c e = G3.src e ∨ ctrlPlus c e = G3.dst e := by
  unfold ctrlPlus; split_ifs <;> simp

/-- **All-tied K3, `+vRay c` side, exact.** If all three endpoint scales are equal (`s`), then for
every `t ≥ 0` on the clip/gate branch (and `q_c - 2t(1-γdt) + ε > 0`, `γdt ≤ 1`, `cap ≥ 0`):
`stepB (B + t vRay c) - stepB B = (t (1-γdt) s) • vRay c`. -/
theorem K3_tied_plus_exact (c : Fin 3) (t : ℝ) (ht : 0 ≤ t) (ha : 0 ≤ 1 - p.γ * p.dt)
    (hcap : 0 ≤ p.cap)
    (hpos : 0 < incAct G3 (prop p drive B) c - 2 * (t * (1 - p.γ * p.dt)) + p.ε)
    (hclip : ∀ e, 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • vRay c) e)
    (hon : GateOn p G3 (prop p drive B)) (hon' : GateOn p G3 (prop p drive (B + t • vRay c)))
    (htie : ∀ i j, sc p G3 (prop p drive B) i = sc p G3 (prop p drive B) j) :
    stepB p G3 drive (B + t • vRay c) - stepB p G3 drive B =
      (t * (1 - p.γ * p.dt) * sc p G3 (prop p drive B) c) • vRay c := by
  have hx := prop_add_smul_of_clip p drive B (vRay c) t (fun e _ => hclip e)
  have hker : InCtrlKer G3 (ctrlPlus c) (vRay c) :=
    fun e => incAct_vRay_other c _ (ctrlPlus_ne c e)
  have hc0 : IsCtrl p G3 (prop p drive B) (ctrlPlus c) :=
    fun e => ⟨ctrlPlus_mem c e, (htie _ _).le, (htie _ _).le⟩
  have hge : ∀ k, sc p G3 (prop p drive B) c ≤ sc p G3 (prop p drive (B + t • vRay c)) k := by
    intro k
    rw [hx]
    by_cases hk : k = c
    · subst hk
      rw [sc_add_smul_vRay_self]
      exact scale_anti p (by nlinarith) hpos hcap
    · rw [sc_add_smul_vRay_other p _ _ c k hk]; exact (htie _ _).le
  have hc1 : IsCtrl p G3 (prop p drive (B + t • vRay c)) (ctrlPlus c) := by
    intro e
    have heq : sc p G3 (prop p drive (B + t • vRay c)) (ctrlPlus c e) =
        sc p G3 (prop p drive B) c := by
      rw [hx, sc_add_smul_vRay_other p _ _ c _ (ctrlPlus_ne c e)]; exact htie _ _
    exact ⟨ctrlPlus_mem c e, heq ▸ hge _, heq ▸ hge _⟩
  refine stepB_sub_eq_smul_of_uniform p G3 drive B (vRay c) t _ (ctrlPlus c) (fun e _ => hclip e)
    ⟨fun _ => hon', fun _ => hon⟩ hker hc0 hc1 ?_
  intro e _
  simp only [branchScale, hon, if_true]
  exact htie _ _

/-- **All-tied K3, `-vRay c` side, exact.** For `τ ≥ 0` (perturbation `B - τ vRay c`), with node `c`
saturated at the base (`cap / (q_c + ε) ≤ 1`, `q_c + ε > 0`): node `c` becomes the controller of its
two edges and the response is the rational function below; the opposite edge moves linearly. -/
theorem K3_tied_minus_exact (c : Fin 3) (τ : ℝ) (hτ : 0 ≤ τ) (ha : 0 ≤ 1 - p.γ * p.dt)
    (hcap : 0 ≤ p.cap) (hqpos : 0 < incAct G3 (prop p drive B) c + p.ε)
    (hsat : p.cap / (incAct G3 (prop p drive B) c + p.ε) ≤ 1)
    (hclip : ∀ e, 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + (-τ) • vRay c) e)
    (hon' : GateOn p G3 (prop p drive (B + (-τ) • vRay c)))
    (htie : ∀ i j, sc p G3 (prop p drive B) i = sc p G3 (prop p drive B) j) (e : Fin 3) :
    stepB p G3 drive (B + (-τ) • vRay c) e =
      if G3.src e = c ∨ G3.dst e = c then
        (prop p drive B e + τ * (1 - p.γ * p.dt)) *
          (p.cap / (incAct G3 (prop p drive B) c + 2 * (τ * (1 - p.γ * p.dt)) + p.ε))
      else (prop p drive B e - τ * (1 - p.γ * p.dt)) * sc p G3 (prop p drive B) c := by
  have hx := prop_add_smul_of_clip p drive B (vRay c) (-τ) (fun e _ => hclip e)
  set x := prop p drive B with hxdef
  set a := 1 - p.γ * p.dt with hadef
  set q := incAct G3 x c with hqdef
  have hta : 0 ≤ τ * a := mul_nonneg hτ ha
  have hs : sc p G3 x c = p.cap / (q + p.ε) := by
    simp only [sc, scale, ← hqdef]; exact min_eq_right hsat
  have hsc_c : sc p G3 (prop p drive (B + (-τ) • vRay c)) c = p.cap / (q + 2 * (τ * a) + p.ε) := by
    rw [hx, sc_add_smul_vRay_self]
    have hq2 : incAct G3 x c - 2 * (-τ * a) = q + 2 * (τ * a) := by rw [← hqdef]; ring
    simp only [scale, hq2]
    apply min_eq_right
    refine le_trans ?_ hsat
    apply div_le_div_of_nonneg_left hcap hqpos
    nlinarith
  have hsc_c_le : p.cap / (q + 2 * (τ * a) + p.ε) ≤ sc p G3 x c := by
    rw [hs]; exact div_le_div_of_nonneg_left hcap hqpos (by nlinarith)
  have hsc_o : ∀ j, j ≠ c → sc p G3 (prop p drive (B + (-τ) • vRay c)) j = sc p G3 x c := by
    intro j hj; rw [hx, sc_add_smul_vRay_other p _ _ c j hj]; exact htie _ _
  have hy : prop p drive (B + (-τ) • vRay c) e = x e + (-τ * a) * vRay c e := by
    rw [hx]; rfl
  simp only [stepB, hon', if_true, gated, hy]
  by_cases hec : G3.src e = c ∨ G3.dst e = c
  · rw [if_pos hec]
    have hv : vRay c e = -1 := by simp [vRay, hec]
    have hmin : min (sc p G3 (prop p drive (B + (-τ) • vRay c)) (G3.src e))
        (sc p G3 (prop p drive (B + (-τ) • vRay c)) (G3.dst e)) =
        p.cap / (q + 2 * (τ * a) + p.ε) := by
      rcases hec with h | h
      · rw [h, hsc_c, hsc_o _ (fun h' => G3_src_ne_dst e (h.trans h'.symm))]
        exact min_eq_left hsc_c_le
      · rw [h, hsc_c, hsc_o _ (fun h' => G3_src_ne_dst e (h'.trans h.symm))]
        exact min_eq_right hsc_c_le
    rw [hmin, hv]; ring
  · rw [if_neg hec]
    push Not at hec
    have hv : vRay c e = 1 := by simp [vRay, hec.1, hec.2]
    rw [hsc_o _ hec.1, hsc_o _ hec.2, min_self, hv]; ring

/-! ## One-sided derivatives at the all-tied K3 point -/

open Filter Topology

/-- **Right derivative along `+vRay c`** (all tied, strict clip, gate on): the one-sided derivative
of the true one-step map is the eigen-response `(1-γdt) s · vRay c`. -/
theorem K3_tied_plus_hasDerivWithinAt (c e : Fin 3) (ha : 0 ≤ 1 - p.γ * p.dt) (hcap : 0 ≤ p.cap)
    (hpre : ∀ e, 0 < pre p drive B e) (hon : GateOn p G3 (prop p drive B))
    (hqpos : 0 < incAct G3 (prop p drive B) c + p.ε)
    (htie : ∀ i j, sc p G3 (prop p drive B) i = sc p G3 (prop p drive B) j) :
    HasDerivWithinAt (fun t : ℝ => stepB p G3 drive (B + t • vRay c) e)
      ((1 - p.γ * p.dt) * sc p G3 (prop p drive B) c * vRay c e) (Set.Ici (0 : ℝ)) 0 := by
  set k := (1 - p.γ * p.dt) * sc p G3 (prop p drive B) c * vRay c e
  have hlin :
      HasDerivWithinAt (fun t : ℝ => stepB p G3 drive B e + t * k) k (Set.Ici (0 : ℝ)) 0 := by
    simpa using (((hasDerivAt_id (0 : ℝ)).mul_const k).const_add
      (stepB p G3 drive B e)).hasDerivWithinAt
  have hposT :
      Tendsto (fun t : ℝ => incAct G3 (prop p drive B) c - 2 * (t * (1 - p.γ * p.dt)) + p.ε)
      (𝓝 0) (𝓝 (incAct G3 (prop p drive B) c + p.ε)) := by
    have : Continuous fun t : ℝ =>
        incAct G3 (prop p drive B) c - 2 * (t * (1 - p.γ * p.dt)) + p.ε := by fun_prop
    simpa using this.tendsto 0
  have hev : ∀ᶠ t in 𝓝[Set.Ici 0] (0 : ℝ),
      stepB p G3 drive (B + t • vRay c) e = stepB p G3 drive B e + t * k := by
    filter_upwards [self_mem_nhdsWithin,
      nhdsWithin_le_nhds (eventually_clip_gate p G3 drive B (vRay c) hpre hon),
      nhdsWithin_le_nhds (hposT.eventually_const_lt hqpos)] with t ht hbr hq
    have := congrFun (K3_tied_plus_exact p drive B c t ht ha hcap hq
      (fun e => ⟨(hpre e).le, hbr.1 e⟩) hon hbr.2 htie) e
    simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul] at this
    simp only [k]; linarith
  exact hlin.congr_of_eventuallyEq hev (by simp)

/-- **Right derivative along `-vRay c`** on an edge `e` at `c` (all tied, node `c` saturated, strict
clip, gate on): the one-sided derivative of the true one-step map in `τ` (input `B - τ vRay c`) is
`(1-γdt) s (1 - 2 x_e / (q_c + ε))`, `s = cap / (q_c + ε)`. -/
theorem K3_tied_minus_hasDerivWithinAt (c e : Fin 3) (hec : G3.src e = c ∨ G3.dst e = c)
    (ha : 0 ≤ 1 - p.γ * p.dt) (hcap : 0 ≤ p.cap)
    (hpre : ∀ e, 0 < pre p drive B e) (hon : GateOn p G3 (prop p drive B))
    (hqpos : 0 < incAct G3 (prop p drive B) c + p.ε)
    (hsat : p.cap / (incAct G3 (prop p drive B) c + p.ε) ≤ 1)
    (htie : ∀ i j, sc p G3 (prop p drive B) i = sc p G3 (prop p drive B) j) :
    HasDerivWithinAt (fun τ : ℝ => stepB p G3 drive (B + (-τ) • vRay c) e)
      ((1 - p.γ * p.dt) * sc p G3 (prop p drive B) c *
        (1 - 2 * prop p drive B e / (incAct G3 (prop p drive B) c + p.ε))) (Set.Ici (0 : ℝ)) 0 := by
  set x := prop p drive B with hxdef
  set a := 1 - p.γ * p.dt with hadef
  set q := incAct G3 x c with hqdef
  have hs : sc p G3 x c = p.cap / (q + p.ε) := by
    simp only [sc, scale, ← hqdef]; exact min_eq_right hsat
  have hne : q + 2 * (0 * a) + p.ε ≠ 0 := by rw [zero_mul, mul_zero, add_zero]; exact hqpos.ne'
  have hnum : HasDerivAt (fun τ : ℝ => x e + τ * a) a 0 := by
    simpa using ((hasDerivAt_id (0 : ℝ)).mul_const a).const_add (x e)
  have hden : HasDerivAt (fun τ : ℝ => q + 2 * (τ * a) + p.ε) (2 * a) 0 := by
    simpa using ((((hasDerivAt_id (0 : ℝ)).mul_const a).const_mul 2).const_add q).add_const p.ε
  have hf := hnum.fun_mul ((hasDerivAt_const (0 : ℝ) p.cap).fun_div hden hne)
  have hval : a * (p.cap / (q + 2 * (0 * a) + p.ε)) +
      (x e + 0 * a) * ((0 * (q + 2 * (0 * a) + p.ε) - p.cap * (2 * a)) /
        (q + 2 * (0 * a) + p.ε) ^ 2) = a * sc p G3 x c * (1 - 2 * x e / (q + p.ε)) := by
    have hqe : q + p.ε ≠ 0 := hqpos.ne'
    rw [hs]; simp only [zero_mul, mul_zero, add_zero, zero_sub]; field_simp; ring
  rw [hval] at hf
  have hev : ∀ᶠ τ in 𝓝[Set.Ici 0] (0 : ℝ),
      stepB p G3 drive (B + (-τ) • vRay c) e =
        (x e + τ * a) * (p.cap / (q + 2 * (τ * a) + p.ε)) := by
    have hneg : Tendsto (fun τ : ℝ => -τ) (𝓝 0) (𝓝 0) := by
      simpa using (continuous_neg.tendsto (0 : ℝ))
    filter_upwards [self_mem_nhdsWithin,
      nhdsWithin_le_nhds (hneg.eventually (eventually_clip_gate p G3 drive B (vRay c) hpre hon))]
      with τ hτ hbr
    rw [K3_tied_minus_exact p drive B c τ hτ ha hcap hqpos hsat
      (fun e => ⟨(hpre e).le, hbr.1 e⟩) hbr.2 htie e, if_pos hec]
  have h0 := K3_tied_minus_exact p drive B c 0 le_rfl ha hcap hqpos hsat
    (fun e => ⟨(hpre e).le, by simpa using (hpre e).le⟩) (by simpa using hon) htie e
  rw [if_pos hec] at h0
  exact hf.hasDerivWithinAt.congr_of_eventuallyEq hev (by simpa using h0)

/-- **`-vRay c` is not an eigen-direction.** The right derivative along `-vRay c` on an edge at `c`
differs from the eigen-response `(1-γdt) s · (-vRay c)_e = (1-γdt) s` whenever `γdt ≠ 1`, `s ≠ 0`,
`x_e ≠ 0` and `q_c + ε ≠ 0`; so the tied K3 response is one-sided (not odd, not linear). -/
theorem K3_tied_minus_not_eigen (c e : Fin 3) (hec : G3.src e = c ∨ G3.dst e = c) (a s xe qe : ℝ)
    (ha : a ≠ 0) (hs : s ≠ 0) (hx : xe ≠ 0) (hq : qe ≠ 0) :
    a * s * (1 - 2 * xe / qe) ≠ a * s * (-vRay c e) := by
  have hv : vRay c e = -1 := by simp [vRay, hec]
  rw [hv, neg_neg, mul_one]
  intro h
  have h2 : a * s * (2 * xe / qe) = 0 := by linarith
  exact mul_ne_zero (mul_ne_zero ha hs) (div_ne_zero (mul_ne_zero two_ne_zero hx) hq) h2

end

end AIEFGate
