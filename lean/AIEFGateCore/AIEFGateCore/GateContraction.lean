/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import Mathlib.Topology.MetricSpace.Contracting
import AIEFGateCore.GronwallEnvelope

/-!
# (H16) Contraction of the engine `B` map: what holds, and the binding-gate case refuted

Plan item H16 (second-pass delta in audit-inbox `791b620`), as changed by the Auditor review
`REVIEW_2026-11-26_auditor_scan_leads.md` (audit-inbox `b15c5e5`, accepted at `66d8174`): the
binding-gate case was flagged "may be false (UNVERIFIED)" and had to be probed numerically before
any Lean. Author Auditor Seat 002, written fresh.

**Probe result (before this file was written; script and output in the branch notes, SPEC §18):**
with a frozen drive `D` (frozen `R`), the one-step map `B ↦ stepM p D B` is **not** a contraction
when the gate fires. On 200 random `N = 12` gate-on states at the engine parameters, the Jacobian's
operator norm was `1.23 … 2.30` in ℓ1, `1.71 … 4.44` in the entry-max norm and `0.89 … 1.52` in ℓ2
(Frobenius), against `1 - γ dt = 0.99985`; exact rational pairs confirm ratios `2.30` (ℓ1), `4.44`
(entry max) and `1.52` (Frobenius). Mechanism (not new): the factor `min(s_i, s_j)`, `s_i = cap /
(row_i + ε)`, depends on `B`; raising one entry lowers `s_i` and so every other entry of rows `i`
and `j`. So the statement "the binding-gate B map is a contraction" is **false**, it is not proved
here, and NORTH_STAR row 7 is not advanced by this file.

Content:

* `stepM_entry_lipschitz_gate_off`, `stepM_entry_lipschitz_gate_off_symm` (the true version where it
  is clear): if the gate does **not** fire at either state, every entry of the step moves by at most
  `(1 - γ dt)` times the input change of that entry (symmetrised). This is a per-pair statement, not
  a global contraction: the gate-off set is not shown invariant, and the gate jumps by `~ε` at its
  trigger (`Capacity.false_gate_nonexpansive`).
* `scalar_map_contracting`, `scalar_map_fixedPoint_tendsto`: with a **frozen** gate factor `lam ∈
  [0, 1]` and frozen drive, the scalar map `x ↦ lam · max 0 (ρ x + d)` is a Banach contraction with
  constant `ρ` (Mathlib `ContractingWith`), so it has a unique fixed point and every orbit converges
  to it. This restates what `Freeze.upper_geom` already gives; it is a short corollary, not a new
  result.
* The refutation, on `Fin 3` at the frozen `pE`, `D = 0`: `B3` (all edges `1/3`) and `B3'` (edge
  `{0,1}` raised to `13/30`). Every row of both proposals is strictly above `cap`
  (`binding_witness_rows`), the ℓ1 distance grows by a factor `> 6/5` (`binding_witness_l1`, exact
  ratio `≈ 1.239`), and edge `{0,2}`, which did not change, moves (`binding_witness_entry`).
  Negations: `false_stepM_l1_nonexpansive_binding`, `false_entry_lipschitz_no_gate_off`,
  `false_entry_lipschitz_gamma_dt_gt_one`, `false_lipschitz_symm_no_symm`,
  `false_contracting_lam_gt_one`. Value probes (definition mutants): `probe_scalarMap_value`,
  `probe_scalarMap_clamp`, `probe_l1_B3`.

Scope: exact reals; frozen `D` (frozen `R`): **conditional, not O1** (in the engine `R` depends on
the phases, which depend on `B`). Not proved and not claimed: convergence of the engine `B`
trajectory; contraction in any norm when the gate fires (refuted in ℓ1 here, and numerically in
entry-max and ℓ2 at `N = 12`; the numerical numbers are not Lean results). Nothing about float64. `γ
dt ≤ 1` is a hypothesis of the gate-off theorem (`γ dt > 1` is engine-legal and excluded).
-/

set_option autoImplicit false

namespace AIEFGate
namespace GateContraction

open Finset AIEFGate.MatrixForm AIEFGate.Capacity AIEFGate.WeightUpdate
open AIEFGate.EngineWitness (pE engineGate_pE)

noncomputable section

/-! ### Gate off: entrywise `(1 - γ dt)`-Lipschitz -/

section GateOff

variable {V : Type*} [Fintype V] [LinearOrder V] (p : Params)

/-- **Gate off at both states:** each entry of the step moves by at most `(1 - γ dt)` times the
symmetrised input change. No symmetry or sign hypothesis on `B`, `B'`, `D`. -/
theorem stepM_entry_lipschitz_gate_off (hh1 : p.γ * p.dt ≤ 1) (D B B' : V → V → ℝ)
    (hoff : ¬ MatrixForm.GateOnM p D B) (hoff' : ¬ MatrixForm.GateOnM p D B') (i j : V) :
    |stepM p D B i j - stepM p D B' i j| ≤
      (1 - p.γ * p.dt) * ((|B i j - B' i j| + |B j i - B' j i|) / 2) := by
  have hρ : 0 ≤ 1 - p.γ * p.dt := by linarith
  have hc : ∀ a b : V,
      |clipM p D B a b - clipM p D B' a b| ≤ (1 - p.γ * p.dt) * |B a b - B' a b| := by
    intro a b
    unfold clipM
    refine (abs_max_sub_max_le_abs _ _ 0).trans (le_of_eq ?_)
    rw [show preM p D B a b - preM p D B' a b = (1 - p.γ * p.dt) * (B a b - B' a b) by
      unfold preM; ring, abs_mul, abs_of_nonneg hρ]
  unfold stepM
  rw [if_neg hoff, if_neg hoff']
  unfold symM
  by_cases hij : i = j
  · simp only [if_pos hij, sub_self, abs_zero]
    positivity
  · simp only [if_neg hij]
    have e : (clipM p D B i j + clipM p D B j i) / 2 - (clipM p D B' i j + clipM p D B' j i) / 2 =
        ((clipM p D B i j - clipM p D B' i j) + (clipM p D B j i - clipM p D B' j i)) / 2 := by ring
    rw [e, abs_div, abs_two]
    have := abs_add_le (clipM p D B i j - clipM p D B' i j) (clipM p D B j i - clipM p D B' j i)
    have h1 := hc i j
    have h2 := hc j i
    rw [div_le_iff₀ (by norm_num : (0 : ℝ) < 2)]
    nlinarith

/-- Symmetric states: `|ΔstepM i j| ≤ (1 - γ dt) |ΔB i j|` when the gate is off at both. -/
theorem stepM_entry_lipschitz_gate_off_symm (hh1 : p.γ * p.dt ≤ 1) (D B B' : V → V → ℝ)
    (hB : ∀ i j, B i j = B j i) (hB' : ∀ i j, B' i j = B' j i)
    (hoff : ¬ MatrixForm.GateOnM p D B) (hoff' : ¬ MatrixForm.GateOnM p D B') (i j : V) :
    |stepM p D B i j - stepM p D B' i j| ≤ (1 - p.γ * p.dt) * |B i j - B' i j| := by
  have h := stepM_entry_lipschitz_gate_off p hh1 D B B' hoff hoff' i j
  rw [hB j i, hB' j i] at h
  linarith

end GateOff

/-! ### Frozen gate factor: a Banach contraction (corollary only) -/

/-- The scalar edge map with a frozen gate factor `lam` and frozen drive `d`. -/
def scalarMap (lam ρ d : ℝ) (x : ℝ) : ℝ := lam * max 0 (ρ * x + d)

theorem scalarMap_dist_le (lam ρ d : ℝ) (hl0 : 0 ≤ lam) (hl1 : lam ≤ 1) (hρ0 : 0 ≤ ρ) (x y : ℝ) :
    dist (GateContraction.scalarMap lam ρ d x) (GateContraction.scalarMap lam ρ d y) ≤
      ρ * dist x y := by
  simp only [Real.dist_eq, scalarMap]
  rw [← mul_sub, abs_mul, abs_of_nonneg hl0]
  have h1 : |max 0 (ρ * x + d) - max 0 (ρ * y + d)| ≤ ρ * |x - y| := by
    rw [max_comm 0, max_comm 0]
    refine (abs_max_sub_max_le_abs _ _ 0).trans (le_of_eq ?_)
    rw [show ρ * x + d - (ρ * y + d) = ρ * (x - y) by ring, abs_mul, abs_of_nonneg hρ0]
  calc lam * |max 0 (ρ * x + d) - max 0 (ρ * y + d)|
        ≤ 1 * |max 0 (ρ * x + d) - max 0 (ρ * y + d)| :=
        mul_le_mul_of_nonneg_right hl1 (abs_nonneg _)
    _ ≤ ρ * |x - y| := by linarith

/-- **Frozen-gate contraction:** `ContractingWith ρ (scalarMap lam ρ d)` for `lam ∈ [0,1]`, `ρ ∈
[0,1)`. -/
theorem scalar_map_contracting (lam ρ d : ℝ) (hl0 : 0 ≤ lam) (hl1 : lam ≤ 1) (hρ0 : 0 ≤ ρ)
    (hρ1 : ρ < 1) :
    ContractingWith (Real.toNNReal ρ) (GateContraction.scalarMap lam ρ d) := by
  refine ⟨?_, LipschitzWith.of_dist_le_mul fun x y => ?_⟩
  · rw [← NNReal.coe_lt_coe, Real.coe_toNNReal _ hρ0]; exact hρ1
  · rw [Real.coe_toNNReal _ hρ0]; exact scalarMap_dist_le lam ρ d hl0 hl1 hρ0 x y

/-- Unique fixed point, and every orbit converges to it (Mathlib's Banach theorem). -/
theorem scalar_map_fixedPoint_tendsto (lam ρ d : ℝ) (hl0 : 0 ≤ lam) (hl1 : lam ≤ 1) (hρ0 : 0 ≤ ρ)
    (hρ1 : ρ < 1) :
    ∃ xs : ℝ, scalarMap lam ρ d xs = xs ∧ (∀ y, scalarMap lam ρ d y = y → y = xs) ∧
      ∀ x0, Filter.Tendsto (fun n => (scalarMap lam ρ d)^[n] x0) Filter.atTop (nhds xs) := by
  have hc := scalar_map_contracting lam ρ d hl0 hl1 hρ0 hρ1
  exact ⟨ContractingWith.fixedPoint _ hc, hc.fixedPoint_isFixedPt,
    fun y hy => hc.fixedPoint_unique hy, fun x0 => hc.tendsto_iterate_fixedPoint x0⟩

/-- `lam ≤ 1` is needed: at `lam = 2`, `ρ = 3/4`, `d = 0` the map sends `1 ↦ 3/2` and `0 ↦ 0`, so it
is not `ρ`-Lipschitz, hence not `ContractingWith ρ`. -/
theorem false_contracting_lam_gt_one :
    ¬ ∀ (lam ρ d : ℝ), 0 ≤ lam → 0 ≤ ρ → ρ < 1 →
      ContractingWith (Real.toNNReal ρ) (GateContraction.scalarMap lam ρ d) := by
  intro H
  have h := (H 2 (3 / 4) 0 (by norm_num) (by norm_num) (by norm_num)).2.dist_le_mul 1 0
  rw [Real.coe_toNNReal _ (by norm_num)] at h
  norm_num [scalarMap, Real.dist_eq] at h

/-- Value probe: `scalarMap (1/2) (1/2) 1 2 = 1/2 · max 0 (1 + 1) = 1`. -/
theorem probe_scalarMap_value : scalarMap (1 / 2) (1 / 2) 1 2 = 1 := by
  norm_num [scalarMap]

/-- Value probe of the clamp: `scalarMap 1 (1/2) (-3) 2 = max 0 (1 - 3) = 0`. -/
theorem probe_scalarMap_clamp : scalarMap 1 (1 / 2) (-3) 2 = 0 := by
  norm_num [scalarMap]

/-! ### The binding-gate refutation on `Fin 3` at `pE`, frozen drive `D = 0` -/

/-- All edges `1/3`. -/
def B3 : Fin 3 → Fin 3 → ℝ := ![![0, 1 / 3, 1 / 3], ![1 / 3, 0, 1 / 3], ![1 / 3, 1 / 3, 0]]

/-- Edge `{0,1}` raised to `13/30`, the others `1/3`. -/
def B3' : Fin 3 → Fin 3 → ℝ := ![![0, 13 / 30, 1 / 3], ![13 / 30, 0, 1 / 3], ![1 / 3, 1 / 3, 0]]

/-- With no drive the symmetrised proposal is the decayed state (nonnegative, symmetric, zero
diagonal). -/
theorem symM_zero_drive (Bm : Fin 3 → Fin 3 → ℝ) (hB : ∀ i j, Bm i j = Bm j i)
    (hd : ∀ i, Bm i i = 0)
    (hn : ∀ i j, 0 ≤ Bm i j) (i j : Fin 3) :
    symM pE (fun _ _ => 0) Bm i j = 19997 / 20000 * Bm i j := by
  unfold symM clipM preM
  by_cases hij : i = j
  · subst hij; simp [hd]
  · rw [if_neg hij, hB j i, max_eq_left (by have := hn i j; norm_num [pE]; linarith)]
    norm_num [pE]; ring

theorem B3_symm (i j : Fin 3) : B3 i j = B3 j i := by
  fin_cases i <;> fin_cases j <;> simp [B3]
theorem B3'_symm (i j : Fin 3) : B3' i j = B3' j i := by
  fin_cases i <;> fin_cases j <;> simp [B3']
theorem B3_nonneg (i j : Fin 3) : 0 ≤ B3 i j := by
  fin_cases i <;> fin_cases j <;> norm_num [B3]
theorem B3'_nonneg (i j : Fin 3) : 0 ≤ B3' i j := by
  fin_cases i <;> fin_cases j <;> norm_num [B3']

theorem symM_B3 (i j : Fin 3) : symM pE (fun _ _ => 0) B3 i j = 19997 / 20000 * B3 i j :=
  symM_zero_drive B3 B3_symm (fun i => by fin_cases i <;> simp [B3]) B3_nonneg i j
theorem symM_B3' (i j : Fin 3) : symM pE (fun _ _ => 0) B3' i j = 19997 / 20000 * B3' i j :=
  symM_zero_drive B3' B3'_symm (fun i => by fin_cases i <;> simp [B3']) B3'_nonneg i j

theorem rowM_B3 (i : Fin 3) : rowM pE (fun _ _ => 0) B3 i = 19997 / 30000 := by
  unfold rowM; simp only [symM_B3, Fin.sum_univ_three]
  fin_cases i <;> simp [B3] <;> norm_num

/-- Row sums of the raised state: `rB = 459931/600000` on rows `0, 1`, `rA` on row `2`. -/
def rowB3' : Fin 3 → ℝ := ![459931 / 600000, 459931 / 600000, 19997 / 30000]

theorem rowM_B3' (i : Fin 3) : rowM pE (fun _ _ => 0) B3' i = rowB3' i := by
  unfold rowM; simp only [symM_B3', Fin.sum_univ_three]
  fin_cases i <;> simp [B3', rowB3'] <;> norm_num

/-- **Both states are deep in the binding region:** every row of both proposals is strictly above
`cap`. -/
theorem binding_witness_rows (i : Fin 3) :
    pE.cap < rowM pE (fun _ _ => 0) B3 i ∧ pE.cap < rowM pE (fun _ _ => 0) B3' i := by
  rw [rowM_B3, rowM_B3']
  constructor
  · norm_num [pE]
  · fin_cases i <;> norm_num [pE, rowB3']

theorem gateOn_of_row {X : Fin 3 → Fin 3 → ℝ} (h : pE.cap < rowM pE (fun _ _ => 0) X 0) :
    GateOnM pE (fun _ _ => 0) X := by
  refine ⟨0, ?_⟩
  have hl := engineGate_pE.link
  norm_num [pE] at h hl ⊢
  linarith

theorem gateOn_B3 : GateOnM pE (fun _ _ => 0) B3 := gateOn_of_row (binding_witness_rows 0).1
theorem gateOn_B3' : GateOnM pE (fun _ _ => 0) B3' := gateOn_of_row (binding_witness_rows 0).2

/-- Gate-on entry formula. -/
theorem stepM_of_gateOn {V : Type*} [Fintype V] [LinearOrder V] (p : Params) (D Bm : V → V → ℝ)
    (h : GateOnM p D Bm) {i j : V} (hij : i ≠ j) :
    stepM p D Bm i j =
      symM p D Bm i j * min (scale p (rowM p D Bm i)) (scale p (rowM p D Bm j)) := by
  unfold stepM; rw [if_pos h, if_neg hij]

/-- `sA = cap/(rA + ε)`, `sB = cap/(rB + ε)` at `rA = 19997/30000`, `rB = 459931/600000`. -/
def sA : ℝ := (19 / 30) / (19997 / 30000 + 1 / 10 ^ 12)
def sB : ℝ := (19 / 30) / (459931 / 600000 + 1 / 10 ^ 12)

theorem scale_rA : scale pE (19997 / 30000) = sA := by
  rw [scale_pE_ge_cap (by norm_num [pE])]; norm_num [pE, sA]
theorem scale_rB : scale pE (459931 / 600000) = sB := by
  rw [scale_pE_ge_cap (by norm_num [pE])]; norm_num [pE, sB]
theorem sB_lt_sA : sB < sA := by norm_num [sA, sB]

theorem step_B3 {i j : Fin 3} (hij : i ≠ j) :
    stepM pE (fun _ _ => 0) B3 i j = 19997 / 20000 * (1 / 3) * sA := by
  rw [stepM_of_gateOn pE _ _ gateOn_B3 hij, symM_B3, rowM_B3, rowM_B3, min_self, scale_rA]
  fin_cases i <;> fin_cases j <;> simp [B3] at hij ⊢

theorem step_B3'_01 : stepM pE (fun _ _ => 0) B3' 0 1 = 19997 / 20000 * (13 / 30) * sB := by
  rw [stepM_of_gateOn pE _ _ gateOn_B3' (by decide), symM_B3', rowM_B3', rowM_B3']
  have h0 : rowB3' 0 = 459931 / 600000 := rfl
  have h1 : rowB3' 1 = 459931 / 600000 := rfl
  rw [h0, h1, min_self, scale_rB]
  simp [B3']

theorem step_B3'_x2 {i : Fin 3} (hi : i ≠ 2) :
    stepM pE (fun _ _ => 0) B3' i 2 = 19997 / 20000 * (1 / 3) * sB := by
  rw [stepM_of_gateOn pE _ _ gateOn_B3' hi, symM_B3', rowM_B3', rowM_B3']
  have h2 : rowB3' 2 = 19997 / 30000 := rfl
  have hB : rowB3' i = 459931 / 600000 := by
    fin_cases i
    · rfl
    · rfl
    · exact absurd rfl hi
  rw [h2, hB, scale_rA, scale_rB, min_eq_left sB_lt_sA.le]
  fin_cases i
  · simp [B3']
  · simp [B3']
  · exact absurd rfl hi

/-- **Edge `{0,2}` did not change, but its image moves** (the gate couples rows). -/
theorem binding_witness_entry :
    B3 0 2 = B3' 0 2 ∧ 0 < stepM pE (fun _ _ => 0) B3 0 2 - stepM pE (fun _ _ => 0) B3' 0 2 := by
  refine ⟨by simp [B3, B3'], ?_⟩
  rw [step_B3 (by decide), step_B3'_x2 (by decide)]
  have := sB_lt_sA
  nlinarith

/-- ℓ1 (entry-sum) distance on `Fin 3` matrices. -/
def l1 (X Y : Fin 3 → Fin 3 → ℝ) : ℝ := ∑ i, ∑ j, |X i j - Y i j|

/-- Value probe: the ℓ1 distance of the two witness states is `2 · (13/30 - 1/3) = 1/5` (proved from
the definitions in the probe itself). -/
theorem probe_l1_B3 : l1 B3 B3' = 1 / 5 := by
  simp only [l1, Fin.sum_univ_three]
  simp only [B3, one_div, Fin.isValue, Matrix.cons_val', Matrix.cons_val_zero,
    Matrix.cons_val_fin_one, B3', sub_self, abs_zero, Matrix.cons_val_one, zero_add,
    Matrix.cons_val, add_zero]
  rw [abs_of_neg (by norm_num)]
  norm_num

theorem step_symm (X : Fin 3 → Fin 3 → ℝ) (i j : Fin 3) :
    stepM pE (fun _ _ => 0) X i j = stepM pE (fun _ _ => 0) X j i := stepM_symm pE _ _ i j

/-- **The ℓ1 distance grows by more than `6/5`** in one step, both states gate-on (exact ratio `≈
1.239`). -/
theorem binding_witness_l1 :
    6 / 5 * l1 B3 B3' < l1 (stepM pE (fun _ _ => 0) B3) (stepM pE (fun _ _ => 0) B3') := by
  rw [probe_l1_B3]
  simp only [l1, Fin.sum_univ_three]
  have d : ∀ i, stepM pE (fun _ _ => 0) B3 i i = 0 ∧ stepM pE (fun _ _ => 0) B3' i i = 0 :=
    fun i => ⟨stepM_diag pE _ _ i, stepM_diag pE _ _ i⟩
  rw [(d 0).1, (d 0).2, (d 1).1, (d 1).2, (d 2).1, (d 2).2,
    step_symm B3 1 0, step_symm B3' 1 0, step_symm B3 2 0, step_symm B3' 2 0,
    step_symm B3 2 1, step_symm B3' 2 1,
    step_B3 (by decide : (0 : Fin 3) ≠ 1), step_B3 (by decide : (0 : Fin 3) ≠ 2),
    step_B3 (by decide : (1 : Fin 3) ≠ 2), step_B3'_01, step_B3'_x2 (by decide : (0 : Fin 3) ≠ 2),
    step_B3'_x2 (by decide : (1 : Fin 3) ≠ 2)]
  have h1 : 19997 / 20000 * (1 / 3) * sA - 19997 / 20000 * (13 / 30) * sB < 0 := by
    norm_num [sA, sB]
  have h2 : 0 < 19997 / 20000 * (1 / 3) * sA - 19997 / 20000 * (1 / 3) * sB := by
    have := sB_lt_sA; nlinarith
  rw [abs_of_neg h1, abs_of_pos h2]
  norm_num [sA, sB]

/-- **H16, binding gate: refuted.** "The frozen-drive B map is ℓ1-nonexpansive on gate-on states" is
false (so no ℓ1 contraction constant `K < 1`, nor `K = 1`, exists there). -/
theorem false_stepM_l1_nonexpansive_binding :
    ¬ ∀ (B B' : Fin 3 → Fin 3 → ℝ), GateOnM pE (fun _ _ => 0) B → GateOnM pE (fun _ _ => 0) B' →
      l1 (stepM pE (fun _ _ => 0) B) (stepM pE (fun _ _ => 0) B') ≤ l1 B B' := by
  intro H
  have h := H B3 B3' gateOn_B3 gateOn_B3'
  have h2 := binding_witness_l1
  have h0 : 0 ≤ l1 B3 B3' := by rw [probe_l1_B3]; norm_num
  linarith

/-- `stepM_entry_lipschitz_gate_off` needs the gate-off hypotheses (`pE`, `Fin 3`, edge `{0,2}`). -/
theorem false_entry_lipschitz_no_gate_off :
    ¬ ∀ (D B B' : Fin 3 → Fin 3 → ℝ) (i j : Fin 3),
      |stepM pE D B i j - stepM pE D B' i j| ≤
        (1 - pE.γ * pE.dt) * ((|B i j - B' i j| + |B j i - B' j i|) / 2) := by
  intro H
  have h := H (fun _ _ => 0) B3 B3' 0 2
  have he := binding_witness_entry
  have e1 : B3 2 0 = B3' 2 0 := by simp [B3, B3']
  rw [he.1, e1, sub_self, sub_self, abs_zero, add_zero, zero_div, mul_zero, abs_nonpos_iff] at h
  linarith [he.2]

/-- `stepM_entry_lipschitz_gate_off` needs `γ dt ≤ 1`: at `WeightUpdate.pH` (`γ dt = 2`, `ρ = -1`),
`D = Xo (1/4)`, `B = Xo 0`, `B' = Xo (1/4)` the gate is off at both and the entry moves by `1/4 > 0
≥ ρ · 1/4`. -/
theorem false_entry_lipschitz_gamma_dt_gt_one :
    ¬ ∀ (D B B' : Fin 2 → Fin 2 → ℝ), ¬ MatrixForm.GateOnM pH D B → ¬ MatrixForm.GateOnM pH D B' →
      ∀ i j, |stepM pH D B i j - stepM pH D B' i j| ≤
        (1 - pH.γ * pH.dt) * ((|B i j - B' i j| + |B j i - B' j i|) / 2) := by
  intro H
  have hoff : ∀ a : ℝ, 0 ≤ a → a ≤ 1 / 4 → ¬ MatrixForm.GateOnM pH (Xo (1 / 4)) (Xo a) := by
    intro a h0 h1 ⟨i, hi⟩
    fin_cases i <;>
      simp only [pH, rowM, symM, Fin.zero_eta, Fin.mk_one, Fin.isValue, clipM, preM, Xo, one_div,
        mul_ite, mul_zero, one_mul, Fin.sum_univ_two, ↓reduceIte, zero_ne_one, one_ne_zero,
        add_self_div_two, zero_add, add_zero, sub_neg, lt_sup_iff] at hi <;>
      rcases hi with hi | hi <;> linarith
  have h := H (Xo (1 / 4)) (Xo 0) (Xo (1 / 4)) (hoff 0 le_rfl (by norm_num))
    (hoff (1 / 4) (by norm_num) le_rfl) 0 1
  unfold stepM at h
  rw [if_neg (hoff 0 le_rfl (by norm_num)), if_neg (hoff (1 / 4) (by norm_num) le_rfl)] at h
  norm_num [symM, clipM, preM, Xo, pH] at h

/-- `stepM_entry_lipschitz_gate_off_symm` needs symmetric states: at `pE`, `D = 0`, changing only
entry `(1,0)` by `1/10` moves the image entry `(0,1)` by `ρ/20 > 0`, though `B 0 1` did not change.
-/
theorem false_lipschitz_symm_no_symm :
    ¬ ∀ (D B B' : Fin 2 → Fin 2 → ℝ), ¬ MatrixForm.GateOnM pE D B → ¬ MatrixForm.GateOnM pE D B' →
      ∀ i j, |stepM pE D B i j - stepM pE D B' i j| ≤ (1 - pE.γ * pE.dt) * |B i j - B' i j| := by
  intro H
  set Z : Fin 2 → Fin 2 → ℝ := fun _ _ => 0 with hZ
  set A : Fin 2 → Fin 2 → ℝ := ![![0, 0], ![1 / 10, 0]] with hA
  have offZ : ¬ MatrixForm.GateOnM pE Z Z := by
    rintro ⟨i, hi⟩
    fin_cases i <;> simp [hZ, rowM, symM, clipM, preM, pE] at hi <;> norm_num at hi
  have offA : ¬ MatrixForm.GateOnM pE Z A := by
    rintro ⟨i, hi⟩
    fin_cases i <;> simp [hZ, hA, rowM, symM, clipM, preM, Fin.sum_univ_two, pE] at hi <;>
      norm_num at hi
  have h := H Z Z A offZ offA 0 1
  unfold stepM at h
  rw [if_neg offZ, if_neg offA] at h
  simp [hZ, hA, symM, clipM, preM, pE] at h
  norm_num at h

#print axioms stepM_entry_lipschitz_gate_off
#print axioms stepM_entry_lipschitz_gate_off_symm
#print axioms scalar_map_contracting
#print axioms scalar_map_fixedPoint_tendsto
#print axioms binding_witness_rows
#print axioms binding_witness_entry
#print axioms binding_witness_l1
#print axioms false_stepM_l1_nonexpansive_binding
#print axioms false_entry_lipschitz_no_gate_off
#print axioms false_contracting_lam_gt_one
#print axioms false_entry_lipschitz_gamma_dt_gt_one
#print axioms false_lipschitz_symm_no_symm
#print axioms probe_scalarMap_value
#print axioms probe_scalarMap_clamp
#print axioms probe_l1_B3

end

end GateContraction
end AIEFGate
