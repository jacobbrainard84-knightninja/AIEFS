/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.GateMap

/-!
# (P2) Matrix form of the one-step `B` map equals the edge-vector form

The engine (`aief_experiment_engine_v1.py:790-813`) works on the `N × N` matrix `B`: proposal
`max(B + dt((η+μ)R − μ − γB), 0)`, symmetrisation `0.5 (x + xᵀ)`, zero diagonal, row sums, scales,
`x * minimum.outer(scale, scale)`, zero diagonal. `GateMap.lean` models it on edge vectors (one
coordinate per unordered pair). Here the matrix form `stepM` is written out and proved equal to the
edge-vector `stepB` on the complete graph `KG V` (edges = pairs `i < j`), for symmetric `B` and
symmetric drive (`stepM_eq_stepB`); the matrix output is symmetric with zero diagonal
(`stepM_symm`, `stepM_diag`), so it is determined by its edge values.

The symmetry hypotheses are needed: `false_matrix_no_symm` refutes the statement without them.

Scope: exact reals; any finite linearly ordered node type (the engine has `Fin 12`); the drive is an
arbitrary symmetric matrix (the engine's is `(η+μ)R − μ` with `R` symmetric). The diagonal of `B`
and of the drive is arbitrary (it is overwritten by the zero diagonal). Nothing about float64.
-/

set_option autoImplicit false

namespace AIEFGate
namespace MatrixForm

open Finset

/-- Unordered pairs of nodes, represented as ordered pairs `i < j`. -/
abbrev CE (V : Type*) [LinearOrder V] := {q : V × V // q.1 < q.2}

def KG (V : Type*) [LinearOrder V] : Graph V (CE V) := ⟨fun e => e.1.1, fun e => e.1.2⟩

def toEdge {V : Type*} [LinearOrder V] (M : V → V → ℝ) : CE V → ℝ := fun e => M e.1.1 e.1.2

variable {V : Type*} [Fintype V] [LinearOrder V]

theorem sum_CE (f : V × V → ℝ) :
    ∑ e : CE V, f e.1 = ∑ a, ∑ b, if a < b then f (a, b) else 0 := by
  rw [← Fintype.sum_prod_type', ← Finset.sum_filter]
  exact (Finset.sum_subtype _ (by simp) f).symm

theorem incAct_KG (x : V → V → ℝ) (i : V) :
    incAct (KG V) (toEdge x) i =
      ∑ j, ((if i < j then x i j else 0) + (if j < i then x j i else 0)) := by
  unfold incAct incCoeff toEdge KG
  simp only
  rw [sum_CE (fun q => ((if q.1 = i then (1:ℝ) else 0) + (if q.2 = i then 1 else 0)) * x q.1 q.2)]
  have h1 : ∀ a b : V,
      (if a < b then ((if a = i then (1:ℝ) else 0) + (if b = i then 1 else 0)) * x a b
      else 0) = (if a = i then (if a < b then x a b else 0) else 0) +
        (if b = i then (if a < b then x a b else 0) else 0) := by
    intro a b; split_ifs <;> simp_all
  simp only [h1, Finset.sum_add_distrib]
  rw [Finset.sum_comm (f := fun a b => if b = i then (if a < b then x a b else 0) else 0)]
  congr 1 <;> rw [Finset.sum_eq_single i (fun b _ hb => by simp [hb]) (by simp)] <;> simp
/-- Row sum of a symmetric zero-diagonal matrix = unsigned incidence action on its edge vector. -/
theorem rowSum_eq_incAct (x : V → V → ℝ) (hs : ∀ i j, x i j = x j i) (hd : ∀ i, x i i = 0)
    (i : V) : ∑ j, x i j = incAct (KG V) (toEdge x) i := by
  rw [incAct_KG]
  refine Finset.sum_congr rfl fun j _ => ?_
  rcases lt_trichotomy i j with h | h | h
  · simp [h, not_lt.mpr h.le]
  · subst h; simp [hd]
  · simp [h, not_lt.mpr h.le, hs j i]

variable (p : Params)

noncomputable section

/-- Matrix pre-clip proposal `B + dt (D − γ B)` (engine `:790-794`, `D = (η+μ)R − μ`). -/
def preM (D Bm : V → V → ℝ) (i j : V) : ℝ :=
  Bm i j + p.dt * (D i j - p.γ * Bm i j)

/-- Clipped matrix proposal (engine `:795`). -/
def clipM (D Bm : V → V → ℝ) (i j : V) : ℝ :=
  max (preM p D Bm i j) 0

/-- Symmetrised proposal with zero diagonal (engine `:796-797`). -/
def symM (D Bm : V → V → ℝ) (i j : V) : ℝ :=
  if i = j then 0 else (clipM p D Bm i j + clipM p D Bm j i) / 2

/-- Row sums (engine `:803`). -/
def rowM (D Bm : V → V → ℝ) (i : V) : ℝ :=
  ∑ j, symM p D Bm i j

/-- Matrix gate test (engine `:804-805`). -/
def GateOnM (D Bm : V → V → ℝ) : Prop :=
  ∃ i, p.gapA - p.gapQ * rowM p D Bm i < p.gapDelta

open Classical in
/-- Matrix one-step `B` map (engine `:808-813`): gated `x_ij · min(s_i, s_j)` with zero diagonal if
the gate fires, else the symmetrised proposal. -/
def stepM (D Bm : V → V → ℝ) (i j : V) : ℝ :=
  if GateOnM p D Bm then
    (if i = j then 0 else symM p D Bm i j * min (scale p (rowM p D Bm i)) (scale p (rowM p D Bm j)))
  else symM p D Bm i j

omit [Fintype V] in
theorem symM_symm (D Bm : V → V → ℝ) (i j : V) : symM p D Bm i j = symM p D Bm j i := by
  unfold symM
  by_cases h : i = j
  · subst h; rfl
  · rw [if_neg h, if_neg (Ne.symm h)]; ring

omit [Fintype V] in
theorem symM_diag (D Bm : V → V → ℝ) (i : V) : symM p D Bm i i = 0 := by
  simp [symM]

/-- **The matrix output is symmetric.** -/
theorem stepM_symm (D Bm : V → V → ℝ) (i j : V) : stepM p D Bm i j = stepM p D Bm j i := by
  unfold stepM
  split_ifs with hg h1 h2 h2
  · rfl
  · exact absurd h1.symm h2
  · exact absurd h2.symm h1
  · rw [symM_symm p D Bm i j, min_comm]
  · exact symM_symm p D Bm i j

/-- **The matrix output has zero diagonal.** -/
theorem stepM_diag (D Bm : V → V → ℝ) (i : V) : stepM p D Bm i i = 0 := by
  unfold stepM; split_ifs <;> simp [symM_diag]

omit [Fintype V] in
/-- For symmetric `B` and drive, the symmetrised matrix proposal restricted to edges is the
edge-vector proposal `prop`. -/
theorem toEdge_symM (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i) (hB : ∀ i j, Bm i j = Bm j i) :
    toEdge (symM p D Bm) = prop p (toEdge D) (toEdge Bm) := by
  funext e
  have hne : e.1.1 ≠ e.1.2 := ne_of_lt e.2
  simp only [toEdge, symM, if_neg hne, clipM, preM, prop, pre, hD e.1.2 e.1.1, hB e.1.2 e.1.1]
  ring

theorem rowM_eq_incAct (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i)
    (hB : ∀ i j, Bm i j = Bm j i) (i : V) :
    rowM p D Bm i = incAct (KG V) (prop p (toEdge D) (toEdge Bm)) i := by
  rw [rowM, rowSum_eq_incAct _ (symM_symm p D Bm) (symM_diag p D Bm), toEdge_symM p D Bm hD hB]

theorem gateOnM_iff (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i)
    (hB : ∀ i j, Bm i j = Bm j i) :
    GateOnM p D Bm ↔ GateOn p (KG V) (prop p (toEdge D) (toEdge Bm)) := by
  unfold GateOnM GateOn
  simp only [rowM_eq_incAct p D Bm hD hB]

/-- **(P2) Matrix form = edge-vector form.** For symmetric `B` and symmetric drive `D`, the engine's
matrix one-step map, read on any edge `i < j`, equals the edge-vector `stepB` on the complete graph
with edge-vector inputs `toEdge D`, `toEdge B`. With `stepM_symm` and `stepM_diag` this determines
the
whole matrix output. -/
theorem stepM_eq_stepB (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i)
    (hB : ∀ i j, Bm i j = Bm j i) (e : CE V) :
    stepM p D Bm e.1.1 e.1.2 = stepB p (KG V) (toEdge D) (toEdge Bm) e := by
  have hne : e.1.1 ≠ e.1.2 := ne_of_lt e.2
  have hx : symM p D Bm e.1.1 e.1.2 = prop p (toEdge D) (toEdge Bm) e :=
    congrFun (toEdge_symM p D Bm hD hB) e
  unfold stepM stepB
  by_cases hg : GateOnM p D Bm
  · have hg' := (gateOnM_iff p D Bm hD hB).mp hg
    rw [if_pos hg, if_pos hg', if_neg hne, hx]
    simp only [gated, sc, rowM_eq_incAct p D Bm hD hB]
    rfl
  · have hg' : ¬ GateOn p (KG V) (prop p (toEdge D) (toEdge Bm)) :=
      fun h => hg ((gateOnM_iff p D Bm hD hB).mpr h)
    rw [if_neg hg, if_neg hg', hx]

/-- Concrete parameters for the negative control (`p0` of `RedTeam`: `dt = 1/10`, `γ = 1`,
`cap = 1`, `ε = 0`, gate fires iff some row sum exceeds 1). -/
def pT : Params := ⟨1 / 10, 1, 1, 0, 1, 1, 0⟩

/-- A non-symmetric `B` on two nodes: `B₀₁ = 1`, `B₁₀ = 0`. -/
def Bns : Fin 2 → Fin 2 → ℝ := ![![0, 1], ![0, 0]]

/-- **The symmetry hypotheses of `stepM_eq_stepB` are needed.** For the non-symmetric `Bns` (zero
drive) the matrix map averages `B₀₁` and `B₁₀` (`9/20`), the edge-vector map reads `B₀₁` only
(`9/10`); the gate is off in both. -/
theorem false_matrix_no_symm : ¬ ∀ (D Bm : Fin 2 → Fin 2 → ℝ) (e : CE (Fin 2)),
    stepM pT D Bm e.1.1 e.1.2 = stepB pT (KG (Fin 2)) (toEdge D) (toEdge Bm) e := by
  intro H
  have key := H 0 Bns ⟨(0, 1), by decide⟩
  have hsym : ∀ i j : Fin 2, symM pT 0 Bns i j = if i = j then 0 else 9 / 20 := by
    intro i j; fin_cases i <;> fin_cases j <;> simp [symM, clipM, preM, Bns, pT] <;> norm_num
  have hrow : ∀ i : Fin 2, rowM pT 0 Bns i = 9 / 20 := by
    intro i; fin_cases i <;> simp [rowM, hsym, Fin.sum_univ_two]
  have hoffM : ¬ GateOnM pT 0 Bns := by
    rintro ⟨i, hi⟩; rw [hrow] at hi; simp [pT] at hi; norm_num at hi
  have hprop : prop pT (toEdge 0) (toEdge Bns) = toEdge (clipM pT 0 Bns) := rfl
  have hclip : ∀ i j : Fin 2, clipM pT 0 Bns i j = if i = 0 ∧ j = 1 then 9 / 10 else 0 := by
    intro i j; fin_cases i <;> fin_cases j <;> (simp [clipM, preM, Bns, pT]; try norm_num)
  have hoff : ¬ GateOn pT (KG (Fin 2)) (prop pT (toEdge 0) (toEdge Bns)) := by
    rintro ⟨i, hi⟩
    rw [hprop, incAct_KG] at hi
    fin_cases i <;> simp only [Fin.sum_univ_two, hclip] at hi <;> simp [pT] at hi <;> norm_num at hi
  unfold stepM stepB at key
  rw [if_neg hoffM, if_neg hoff, hsym, hprop] at key
  simp [toEdge, hclip] at key
  norm_num at key

end

end MatrixForm
end AIEFGate
