/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.EngineWitness
import AIEFGateCore.MatrixForm

/-!
# (P4a) Guarded-capacity content of the matrix gate, on `Params` / `GateOnM` / `stepM`

Port of the cycle-002 guarded-capacity statements of Researcher 040282 (handle only; source path
`audit_inbox/2026-11-08_researcher-040282/researcher_040282/cycle_002/GateFoundations.lean`
on branch `audit-inbox`, commit `b18a27d`), restated on the definitions of this project instead
of copying the source model: `Params`, `scale`, `EngineGate`, `symM`, `GateOnM`, `stepM`. Every
proof here is written for this project's definitions; the source file was used as a statement
list only.

The matrix gate is factored as `stepM p D Bm = gateM p (symM p D Bm)` (`stepM_eq_gateM`, by `rfl`
up to unfolding), with `gateM p X` the guarded gate of an arbitrary matrix `X`:
`kernelM p X i j = if i = j then 0 else X i j * min (scale p (row i)) (scale p (row j))` and
`gateM p X = if GateOnX p X then kernelM p X else X`.

Theorems (all on this factoring; `X` nonnegative with zero diagonal unless stated):

* `kernel_row_le_cap`: kernel row sums `≤ cap` for `0 ≤ cap` and **`0 ≤ ε`** (the scope in which it
  is proved; nothing is claimed for `ε < 0`, see `false_kernel_row_no_eps`). This is the only
  `ε`-relaxation proved. Everything that involves the guard needs `EngineGate p`, hence `0 < ε`.
* `kernel_row_upper`, `kernel_row_lower`, `kernel_le_input`, `kernel_nonneg`, `kernel_symm`.
* `gateOnX_iff`, `gateM_feasible` (row sums `≤ cap` for `EngineGate p`), `gateM_fixes_feasible`,
  `gateM_idempotent`, `gateM_nonneg`, `gateM_le_input`, `gateM_symm`, `gateM_diag`,
  `gateM_sub_of_rowSum_eq` (equal row sums: the gate is a pointwise multiplier).
* On `stepM` (no symmetry hypothesis on `D`, `Bm` is needed for these): `stepM_row_le_cap`,
  `gateM_stepM` (the gate fixes the engine step output), `stepM_nonneg`.
* Port bridge to the cycle-003 proposal form: `symM_eq_convex`, `stepM_eq_gateM_convex`. For
  `γ ≠ 0`, `preM = (1 - γ dt) B + γ dt (D/γ)`, so `stepM` is the gate of the symmetrised clip of
  that affine combination; it is a convex combination only when `0 ≤ γ dt ≤ 1`
  (`convex_weights_iff`, `preM_between`; negative witness `false_preM_between_no_bound`).
  Statements about the source `weightStep` follow by unfolding its definition and are not part
  of the library.

Negations and non-vacuity (GateCore style, `ε = 10⁻¹²` at the frozen `pE` where possible):
`false_kernel_row_no_eps`, `false_kernel_fixes_boundary`, `false_kernel_idempotent`,
`false_gate_nonexpansive`, `false_fixes_without_feasible`, `false_row_lt_cap`, `false_le_reversed`,
`false_diff_without_equal_rows`, `false_kernel_lower_no_hyp`, `false_gateM_symm_no_hs`,
`false_gateM_feasible_no_link`, `false_stepM_row_no_link`, `gateM_Xo_boundary`,
`witness_gate_active`, `witness_gate_inactive`, `witness_stepM_active`.

Scope: exact reals; any finite linearly ordered node type; the witnesses are `Fin 2` matrices
`Xo a` (off-diagonal entries `a`), not engine states. Nothing about float64: `cap = 19/30` is an
exact real (see `EngineGate`). Not proved here: the Lipschitz/nonexpansiveness (it is refuted),
anything about trajectories.
-/

set_option autoImplicit false

namespace AIEFGate
namespace Capacity

open Finset AIEFGate.MatrixForm

noncomputable section

section General

variable {V : Type*} [Fintype V] [LinearOrder V] (p : Params)

/-- Row sum of a matrix. -/
def rowS (X : V → V → ℝ) (i : V) : ℝ := ∑ j, X i j

/-- Gate test of an arbitrary matrix (as `GateOnM`, with `X` in place of `symM p D Bm`). -/
def GateOnX (X : V → V → ℝ) : Prop :=
  ∃ i, p.gapA - p.gapQ * rowS X i < p.gapDelta

/-- Scaling kernel `x_ij · min(s_i, s_j)` with zero diagonal. -/
def kernelM (X : V → V → ℝ) (i j : V) : ℝ :=
  if i = j then 0 else X i j * min (scale p (rowS X i)) (scale p (rowS X j))

open Classical in
/-- Guarded gate: the kernel if the gate fires, else the matrix unchanged. -/
def gateM (X : V → V → ℝ) (i j : V) : ℝ :=
  if GateOnX p X then kernelM p X i j else X i j

/-- `stepM` is the gate of the symmetrised proposal. -/
theorem stepM_eq_gateM (D Bm : V → V → ℝ) :
    stepM p D Bm = gateM p (symM p D Bm) := rfl

theorem scale_le_one (q : ℝ) : scale p q ≤ 1 := min_le_left _ _

theorem scale_nonneg (hc : 0 ≤ p.cap) (hε : 0 ≤ p.ε) {q : ℝ} (hq : 0 ≤ q) : 0 ≤ scale p q :=
  le_min zero_le_one (div_nonneg hc (by linarith))

omit [LinearOrder V] in
theorem rowS_nonneg {X : V → V → ℝ} (hx : ∀ i j, 0 ≤ X i j) (i : V) : 0 ≤ rowS X i :=
  Finset.sum_nonneg fun j _ => hx i j

/-- `scale(r) · r ≤ cap` for `r ≥ 0`, `0 ≤ cap`, `0 ≤ ε` (the `ε ≥ 0` scope). -/
theorem scale_mul_le_cap (hc : 0 ≤ p.cap) (hε : 0 ≤ p.ε) {r : ℝ} (hr : 0 ≤ r) :
    scale p r * r ≤ p.cap := by
  by_cases h0 : r + p.ε = 0
  · have : r = 0 := by linarith
    subst this; simpa using hc
  · have hpos : 0 < r + p.ε := lt_of_le_of_ne (by linarith) (Ne.symm h0)
    calc scale p r * r ≤ p.cap / (r + p.ε) * r :=
          mul_le_mul_of_nonneg_right (min_le_right _ _) hr
      _ ≤ p.cap := by
          rw [div_mul_eq_mul_div, div_le_iff₀ hpos]
          nlinarith [mul_nonneg hc hε]

theorem kernel_row_upper {X : V → V → ℝ} (hx : ∀ i j, 0 ≤ X i j) (hc : 0 ≤ p.cap)
    (hε : 0 ≤ p.ε) (i : V) :
    ∑ j, kernelM p X i j ≤ scale p (rowS X i) * rowS X i := by
  have hs : 0 ≤ scale p (rowS X i) := scale_nonneg p hc hε (rowS_nonneg hx i)
  calc ∑ j, kernelM p X i j ≤ ∑ j, X i j * scale p (rowS X i) := by
        refine Finset.sum_le_sum fun j _ => ?_
        unfold kernelM
        split_ifs
        · exact mul_nonneg (hx i j) hs
        · exact mul_le_mul_of_nonneg_left (min_le_left _ _) (hx i j)
    _ = scale p (rowS X i) * rowS X i := by
        rw [← Finset.sum_mul, mul_comm]; rfl

/-- **Kernel capacity, `0 ≤ ε` scope.** -/
theorem kernel_row_le_cap {X : V → V → ℝ} (hx : ∀ i j, 0 ≤ X i j) (hc : 0 ≤ p.cap)
    (hε : 0 ≤ p.ε) (i : V) : ∑ j, kernelM p X i j ≤ p.cap :=
  (kernel_row_upper p hx hc hε i).trans (scale_mul_le_cap p hc hε (rowS_nonneg hx i))

theorem kernel_row_lower {X : V → V → ℝ} (hx : ∀ i j, 0 ≤ X i j) (hd : ∀ i, X i i = 0)
    (ℓ : ℝ) (hℓ : ∀ k, ℓ ≤ scale p (rowS X k)) (i : V) :
    ℓ * rowS X i ≤ ∑ j, kernelM p X i j := by
  calc ℓ * rowS X i = ∑ j, ℓ * X i j := by rw [rowS, Finset.mul_sum]
    _ ≤ ∑ j, kernelM p X i j := by
        refine Finset.sum_le_sum fun j _ => ?_
        unfold kernelM
        split_ifs with h
        · subst h; simp [hd]
        · calc ℓ * X i j = X i j * ℓ := mul_comm _ _
            _ ≤ _ := mul_le_mul_of_nonneg_left (le_min (hℓ i) (hℓ j)) (hx i j)

theorem kernel_nonneg {X : V → V → ℝ} (hx : ∀ i j, 0 ≤ X i j) (hc : 0 ≤ p.cap) (hε : 0 ≤ p.ε)
    (i j : V) : 0 ≤ kernelM p X i j := by
  unfold kernelM
  split_ifs
  · exact le_rfl
  · exact mul_nonneg (hx i j) (le_min (scale_nonneg p hc hε (rowS_nonneg hx i))
      (scale_nonneg p hc hε (rowS_nonneg hx j)))

theorem kernel_le_input {X : V → V → ℝ} (hx : ∀ i j, 0 ≤ X i j) (i j : V) :
    kernelM p X i j ≤ X i j := by
  unfold kernelM
  split_ifs
  · exact hx i j
  · exact mul_le_of_le_one_right (hx i j) ((min_le_left _ _).trans (scale_le_one p _))

theorem kernel_symm {X : V → V → ℝ} (hs : ∀ i j, X i j = X j i) (i j : V) :
    kernelM p X i j = kernelM p X j i := by
  unfold kernelM
  by_cases h : i = j
  · subst h; rfl
  · rw [if_neg h, if_neg (Ne.symm h), hs i j, min_comm]

theorem kernel_diag (X : V → V → ℝ) (i : V) : kernelM p X i i = 0 := by simp [kernelM]

omit [LinearOrder V] in
/-- With `EngineGate`, the gate fires iff some row sum exceeds `cap`. -/
theorem gateOnX_iff (hp : EngineGate p) (X : V → V → ℝ) :
    GateOnX p X ↔ ∃ i, p.cap < rowS X i := by
  constructor
  · rintro ⟨i, h⟩
    refine ⟨i, ?_⟩
    by_contra hle
    have hle := not_lt.mp hle
    nlinarith [hp.link, hp.gapQ_pos, mul_le_mul_of_nonneg_left hle hp.gapQ_pos.le]
  · rintro ⟨i, h⟩
    exact ⟨i, by nlinarith [hp.link, mul_lt_mul_of_pos_left h hp.gapQ_pos]⟩

omit [LinearOrder V] in
theorem rowS_le_cap_of_not_gateOn (hp : EngineGate p) {X : V → V → ℝ} (h : ¬ GateOnX p X)
    (i : V) : rowS X i ≤ p.cap := by
  by_contra hlt
  exact h ((gateOnX_iff p hp X).2 ⟨i, not_le.mp hlt⟩)

theorem gateM_diag {X : V → V → ℝ} (hd : ∀ i, X i i = 0) (i : V) : gateM p X i i = 0 := by
  unfold gateM
  split_ifs
  · exact kernel_diag p X i
  · exact hd i

theorem gateM_nonneg {X : V → V → ℝ} (hx : ∀ i j, 0 ≤ X i j) (hc : 0 ≤ p.cap) (hε : 0 ≤ p.ε)
    (i j : V) : 0 ≤ gateM p X i j := by
  unfold gateM
  split_ifs
  · exact kernel_nonneg p hx hc hε i j
  · exact hx i j

theorem gateM_le_input {X : V → V → ℝ} (hx : ∀ i j, 0 ≤ X i j) (i j : V) :
    gateM p X i j ≤ X i j := by
  unfold gateM
  split_ifs
  · exact kernel_le_input p hx i j
  · exact le_rfl

theorem gateM_symm {X : V → V → ℝ} (hs : ∀ i j, X i j = X j i) (i j : V) :
    gateM p X i j = gateM p X j i := by
  unfold gateM
  split_ifs
  · exact kernel_symm p hs i j
  · exact hs i j

/-- **Guarded capacity.** For `EngineGate p` and nonnegative `X`, the gated matrix has every row sum
`≤ cap`. -/
theorem gateM_feasible (hp : EngineGate p) (X : V → V → ℝ) (hx : ∀ i j, 0 ≤ X i j) (i : V) :
    rowS (gateM p X) i ≤ p.cap := by
  by_cases h : GateOnX p X
  · have : rowS (gateM p X) i = ∑ j, kernelM p X i j := by
      unfold rowS gateM; simp only [if_pos h]
    rw [this]
    exact kernel_row_le_cap p hx hp.cap_pos.le hp.eps_pos.le i
  · have : rowS (gateM p X) i = rowS X i := by
      unfold rowS gateM; simp only [if_neg h]
    rw [this]
    exact rowS_le_cap_of_not_gateOn p hp h i

/-- A feasible matrix is a fixed point of the guarded gate. -/
theorem gateM_fixes_feasible (hp : EngineGate p) (X : V → V → ℝ) (hf : ∀ i, rowS X i ≤ p.cap) :
    gateM p X = X := by
  have h : ¬ GateOnX p X := by
    rw [gateOnX_iff p hp]
    rintro ⟨i, hi⟩
    exact absurd (hf i) (not_le.mpr hi)
  funext i j
  unfold gateM
  simp only [if_neg h]

/-- **Idempotence of the guarded gate.** -/
theorem gateM_idempotent (hp : EngineGate p) (X : V → V → ℝ) (hx : ∀ i j, 0 ≤ X i j) :
    gateM p (gateM p X) = gateM p X :=
  gateM_fixes_feasible p hp (gateM p X) (gateM_feasible p hp X hx)

open Classical in
/-- The multiplier the gate applies to entry `(i, j)` of `X`: `min(s_i, s_j)` if the gate fires,
else `1`. -/
def appliedFactor (X : V → V → ℝ) (i j : V) : ℝ :=
  if GateOnX p X then min (scale p (rowS X i)) (scale p (rowS X j)) else 1

/-- For `X`, `Y` with equal row sums the gate acts as one pointwise multiplier. -/
theorem gateM_sub_of_rowSum_eq {X Y : V → V → ℝ} (hX : ∀ i, X i i = 0) (hY : ∀ i, Y i i = 0)
    (hrow : ∀ i, rowS X i = rowS Y i) (i j : V) :
    gateM p X i j - gateM p Y i j =
      (X i j - Y i j) * appliedFactor p X i j := by
  have hg : GateOnX p X ↔ GateOnX p Y := by unfold GateOnX; simp only [hrow]
  unfold gateM appliedFactor
  by_cases h : GateOnX p X
  · rw [if_pos h, if_pos (hg.mp h), if_pos h]
    unfold kernelM
    by_cases hij : i = j
    · subst hij; simp [hX, hY]
    · rw [if_neg hij, if_neg hij, ← hrow i, ← hrow j]; ring
  · rw [if_neg h, if_neg (fun h' => h (hg.mpr h')), if_neg h]; ring

/-! ### On the engine step -/

omit [Fintype V] in
theorem symM_nonneg (D Bm : V → V → ℝ) (i j : V) : 0 ≤ symM p D Bm i j := by
  unfold symM clipM
  split_ifs
  · exact le_rfl
  · exact div_nonneg (add_nonneg (le_max_right _ _) (le_max_right _ _)) two_pos.le

/-- **The engine step respects the capacity** (`EngineGate p`; no symmetry hypothesis needed). -/
theorem stepM_row_le_cap (hp : EngineGate p) (D Bm : V → V → ℝ) (i : V) :
    ∑ j, stepM p D Bm i j ≤ p.cap := by
  rw [stepM_eq_gateM]
  exact gateM_feasible p hp (symM p D Bm) (symM_nonneg p D Bm) i

theorem stepM_nonneg (hp : EngineGate p) (D Bm : V → V → ℝ) (i j : V) :
    0 ≤ stepM p D Bm i j := by
  rw [stepM_eq_gateM]
  exact gateM_nonneg p (symM_nonneg p D Bm) hp.cap_pos.le hp.eps_pos.le i j

/-- The gate fixes the engine step output. -/
theorem gateM_stepM (hp : EngineGate p) (D Bm : V → V → ℝ) :
    gateM p (stepM p D Bm) = stepM p D Bm :=
  gateM_fixes_feasible p hp _ (stepM_row_le_cap p hp D Bm)

/-! ### Port bridge to the convex proposal form -/

omit [Fintype V] [LinearOrder V] in
theorem preM_eq_convex (hγ : p.γ ≠ 0) (D Bm : V → V → ℝ) (i j : V) :
    preM p D Bm i j = (1 - p.γ * p.dt) * Bm i j + p.γ * p.dt * (D i j / p.γ) := by
  unfold preM; field_simp; ring

omit [Fintype V] in
theorem symM_eq_convex (hγ : p.γ ≠ 0) (D Bm : V → V → ℝ) (i j : V) :
    symM p D Bm i j =
      if i = j then 0 else
        (max ((1 - p.γ * p.dt) * Bm i j + p.γ * p.dt * (D i j / p.γ)) 0 +
          max ((1 - p.γ * p.dt) * Bm j i + p.γ * p.dt * (D j i / p.γ)) 0) / 2 := by
  unfold symM clipM
  simp only [preM_eq_convex p hγ]

/-- `stepM` is the guarded gate of the symmetrised clip of the proposal
`(1 - γ dt) B + γ dt (D/γ)`. Only `γ ≠ 0` is assumed, so this is an affine rewriting; the weights
form a genuine convex pair only when `0 ≤ γ dt ≤ 1` (`convex_weights_iff`, `preM_between`;
`false_preM_between_no_bound` shows the bound is needed). The name is kept for the port. -/
theorem stepM_eq_gateM_convex (hγ : p.γ ≠ 0) (D Bm : V → V → ℝ) :
    stepM p D Bm = gateM p (fun i j =>
      if i = j then 0 else
        (max ((1 - p.γ * p.dt) * Bm i j + p.γ * p.dt * (D i j / p.γ)) 0 +
          max ((1 - p.γ * p.dt) * Bm j i + p.γ * p.dt * (D j i / p.γ)) 0) / 2) := by
  rw [stepM_eq_gateM]
  congr 1
  funext i j
  exact symM_eq_convex p hγ D Bm i j

/-- The proposal weights `1 - γ dt` and `γ dt` are both nonnegative (they always sum to `1`)
exactly when `0 ≤ γ dt ≤ 1`. -/
theorem convex_weights_iff :
    (0 ≤ 1 - p.γ * p.dt ∧ 0 ≤ p.γ * p.dt) ↔ (0 ≤ p.γ * p.dt ∧ p.γ * p.dt ≤ 1) := by
  constructor <;> rintro ⟨h1, h2⟩ <;> constructor <;> linarith

omit [Fintype V] [LinearOrder V] in
/-- Under `0 ≤ γ dt ≤ 1` the proposal lies between the old weight `B` and the target `D/γ`. -/
theorem preM_between (hγ : p.γ ≠ 0) (h0 : 0 ≤ p.γ * p.dt) (h1 : p.γ * p.dt ≤ 1)
    (D Bm : V → V → ℝ) (i j : V) :
    min (Bm i j) (D i j / p.γ) ≤ preM p D Bm i j ∧
      preM p D Bm i j ≤ max (Bm i j) (D i j / p.γ) := by
  rw [preM_eq_convex p hγ]
  have hw : 0 ≤ 1 - p.γ * p.dt := by linarith
  constructor
  · nlinarith [mul_le_mul_of_nonneg_left (min_le_left (Bm i j) (D i j / p.γ)) hw,
      mul_le_mul_of_nonneg_left (min_le_right (Bm i j) (D i j / p.γ)) h0]
  · nlinarith [mul_le_mul_of_nonneg_left (le_max_left (Bm i j) (D i j / p.γ)) hw,
      mul_le_mul_of_nonneg_left (le_max_right (Bm i j) (D i j / p.γ)) h0]

end General

/-- Negative witness: without `γ dt ≤ 1` the proposal can leave `[min B (D/γ), max B (D/γ)]`
(`γ = 1`, `dt = 2`, `B = 1`, `D = 0` gives `-1 < 0`), so `preM_between` needs its bound. -/
theorem false_preM_between_no_bound :
    ¬ ∀ (p : Params) (D Bm : Unit → Unit → ℝ) (i j : Unit), p.γ ≠ 0 → 0 ≤ p.γ * p.dt →
      min (Bm i j) (D i j / p.γ) ≤ preM p D Bm i j := by
  intro H
  have h := H ⟨2, 1, 1, 0, 0, 0, 0⟩ (fun _ _ => 0) (fun _ _ => 1) () () (by norm_num) (by norm_num)
  norm_num [preM] at h

/-! ### Negations and non-vacuity witnesses (`Fin 2`) -/

section Witness

open EngineWitness (pE engineGate_pE)

/-- Symmetric `2 × 2` matrix with zero diagonal and off-diagonal entries `a`. -/
def Xo (a : ℝ) : Fin 2 → Fin 2 → ℝ := fun i j => if i = j then 0 else a

theorem Xo_nonneg {a : ℝ} (ha : 0 ≤ a) (i j : Fin 2) : 0 ≤ Xo a i j := by
  unfold Xo; split_ifs <;> simp [ha]

theorem Xo_diag (a : ℝ) (i : Fin 2) : Xo a i i = 0 := by simp [Xo]

theorem Xo_symm (a : ℝ) (i j : Fin 2) : Xo a i j = Xo a j i := by
  unfold Xo; split_ifs with h1 h2 h2 <;> simp_all

theorem Xo_inj {a b : ℝ} (h : Xo a = Xo b) : a = b := by
  have := congrFun (congrFun h 0) 1
  simpa [Xo] using this

theorem rowS_Xo (a : ℝ) (i : Fin 2) : rowS (Xo a) i = a := by
  fin_cases i <;> simp [rowS, Xo, Fin.sum_univ_two]

theorem kernelM_Xo (q : Params) (a : ℝ) : kernelM q (Xo a) = Xo (a * scale q a) := by
  funext i j
  fin_cases i <;> fin_cases j <;> simp [kernelM, Xo, rowS_Xo]

theorem gateM_Xo_of_gt (q : Params) (hq : EngineGate q) {a : ℝ} (ha : q.cap < a) :
    gateM q (Xo a) = Xo (a * scale q a) := by
  have hg : GateOnX q (Xo a) := (gateOnX_iff q hq _).2 ⟨0, by rw [rowS_Xo]; exact ha⟩
  funext i j
  unfold gateM
  rw [if_pos hg, kernelM_Xo]

theorem gateM_Xo_of_le (q : Params) (hq : EngineGate q) {a : ℝ} (ha : a ≤ q.cap) :
    gateM q (Xo a) = Xo a :=
  gateM_fixes_feasible q hq _ (fun i => by rw [rowS_Xo]; exact ha)

theorem scale_pE_ge_cap {a : ℝ} (ha : pE.cap ≤ a) : scale pE a = pE.cap / (a + pE.ε) := by
  have hε : 0 < pE.ε := by simp [pE]
  have hc : 0 < pE.cap := by norm_num [pE]
  unfold scale
  exact min_eq_right ((div_le_one (by linarith)).2 (by linarith))

theorem scale_pE_one_lt : scale pE 1 < 1 := by
  rw [scale_pE_ge_cap (by norm_num [pE])]
  norm_num [pE]

/-- At the boundary `row = cap` the guard leaves the matrix alone. -/
theorem gateM_Xo_boundary : gateM pE (Xo pE.cap) = Xo pE.cap :=
  gateM_Xo_of_le pE engineGate_pE le_rfl

/-- Without the guard the kernel moves the boundary point (`ε > 0`). -/
theorem false_kernel_fixes_boundary : ¬ kernelM pE (Xo pE.cap) = Xo pE.cap := by
  intro h
  rw [kernelM_Xo, scale_pE_ge_cap le_rfl] at h
  have := Xo_inj h
  norm_num [pE] at this

/-- The unguarded kernel is not idempotent (`ε > 0`, boundary input). -/
theorem false_kernel_idempotent :
    ¬ kernelM pE (kernelM pE (Xo pE.cap)) = kernelM pE (Xo pE.cap) := by
  intro h
  rw [kernelM_Xo, kernelM_Xo] at h
  have := Xo_inj h
  norm_num [pE, scale, min_def] at this

/-- The guarded gate is not nonexpansive in the entry value: a boundary jump of size `~ε`. -/
theorem false_gate_nonexpansive :
    ¬ ∀ a b : ℝ, 0 ≤ a → 0 ≤ b →
      |gateM pE (Xo a) 0 1 - gateM pE (Xo b) 0 1| ≤ |a - b| := by
  intro H
  have h := H pE.cap (pE.cap + 1 / 10 ^ 15) (by norm_num [pE]) (by norm_num [pE])
  rw [gateM_Xo_boundary, gateM_Xo_of_gt pE engineGate_pE (by norm_num [pE]),
    scale_pE_ge_cap (by norm_num [pE])] at h
  norm_num [Xo, pE] at h

/-- `gateM_fixes_feasible` needs feasibility. -/
theorem false_fixes_without_feasible : ¬ gateM pE (Xo 1) = Xo 1 := by
  intro h
  rw [gateM_Xo_of_gt pE engineGate_pE (by norm_num [pE])] at h
  have := Xo_inj h
  linarith [scale_pE_one_lt]

/-- The capacity bound of `gateM_feasible` is attained: it cannot be strict. -/
theorem false_row_lt_cap : ¬ rowS (gateM pE (Xo pE.cap)) 0 < pE.cap := by
  rw [gateM_Xo_boundary, rowS_Xo]; exact lt_irrefl _

/-- The gate really shrinks: `X ≤ gateM X` fails. -/
theorem false_le_reversed : ¬ Xo 1 0 1 ≤ gateM pE (Xo 1) 0 1 := by
  rw [gateM_Xo_of_gt pE engineGate_pE (by norm_num [pE])]
  simp only [Xo]
  norm_num
  linarith [scale_pE_one_lt]

theorem appliedFactor_Xo_zero : appliedFactor pE (Xo 0) 0 1 = 1 := by
  have : ¬ GateOnX pE (Xo 0) := by
    rw [gateOnX_iff pE engineGate_pE]
    rintro ⟨i, hi⟩
    rw [rowS_Xo] at hi
    norm_num [pE] at hi
  unfold appliedFactor
  simp only [if_neg this]

/-- The equal-row-sum hypothesis of `gateM_sub_of_rowSum_eq` is needed. -/
theorem false_diff_without_equal_rows :
    ¬ (gateM pE (Xo 0) 0 1 - gateM pE (Xo 1) 0 1 =
      (Xo 0 0 1 - Xo 1 0 1) * appliedFactor pE (Xo 0) 0 1) := by
  intro h
  rw [appliedFactor_Xo_zero, gateM_Xo_of_le pE engineGate_pE (by norm_num [pE]),
    gateM_Xo_of_gt pE engineGate_pE (by norm_num [pE])] at h
  simp only [Xo] at h
  norm_num at h
  linarith [scale_pE_one_lt]

/-- `kernel_row_lower` needs its scale hypothesis (`ℓ = 1`). -/
theorem false_kernel_lower_no_hyp :
    ¬ (1 * rowS (Xo 1) 0 ≤ ∑ j, kernelM pE (Xo 1) 0 j) := by
  rw [kernelM_Xo, rowS_Xo]
  simp only [Fin.sum_univ_two, Xo]
  norm_num
  linarith [scale_pE_one_lt]

/-- A nonsymmetric matrix with row sums `≤ cap`. -/
def Xn : Fin 2 → Fin 2 → ℝ := fun i j => if i = 0 ∧ j = 1 then 1 / 10 else 0

theorem Xn_nonneg (i j : Fin 2) : 0 ≤ Xn i j := by
  unfold Xn; split_ifs <;> norm_num

theorem not_gateOn_Xn : ¬ GateOnX pE Xn := by
  rw [gateOnX_iff pE engineGate_pE]
  rintro ⟨i, hi⟩
  fin_cases i <;> simp [rowS, Xn] at hi <;> norm_num [pE] at hi

/-- `gateM_symm` needs symmetry of the input. -/
theorem false_gateM_symm_no_hs : ¬ gateM pE Xn 0 1 = gateM pE Xn 1 0 := by
  have := gateM_fixes_feasible pE engineGate_pE Xn (fun i => by
    by_contra hlt
    exact not_gateOn_Xn ((gateOnX_iff pE engineGate_pE Xn).2 ⟨i, not_le.mp hlt⟩))
  rw [this]
  simp [Xn]

/-- Parameters whose guard threshold `(gapA - gapDelta)/gapQ = 1` differs from `cap = 1/2`
(`EngineGate` fails: `link`). -/
def pB : Params := ⟨1 / 100, 1, 1 / 2, 1 / 10, 1, 1, 0⟩

/-- `gateM_feasible` needs the link `cap · gapQ = gapA - gapDelta` of `EngineGate`. -/
theorem false_gateM_feasible_no_link : ¬ rowS (gateM pB (Xo (3 / 4))) 0 ≤ pB.cap := by
  have hg : ¬ GateOnX pB (Xo (3 / 4)) := by
    rintro ⟨i, hi⟩
    rw [rowS_Xo] at hi
    norm_num [pB] at hi
  have : gateM pB (Xo (3 / 4)) = Xo (3 / 4) := by
    funext i j; unfold gateM; simp only [if_neg hg]
  rw [this, rowS_Xo]
  norm_num [pB]

/-- `stepM_row_le_cap` needs `EngineGate`: at `pB` (guard threshold `1`, `cap = 1/2`) the
engine step from drive `Xo 75`, `B = 0` (proposal `Xo (3/4)`) is not gated and its row sum
`3/4` exceeds `cap`. -/
theorem false_stepM_row_no_link :
    ¬ ∑ j, stepM pB (Xo 75) (fun _ _ => (0 : ℝ)) 0 j ≤ pB.cap := by
  have hs : symM pB (Xo 75) (fun _ _ => (0 : ℝ)) = Xo (3 / 4) := by
    funext i j
    fin_cases i <;> fin_cases j <;> simp [symM, clipM, preM, Xo, pB] <;> norm_num
  have hg : ¬ GateOnX pB (Xo (3 / 4)) := by
    rintro ⟨i, hi⟩
    rw [rowS_Xo] at hi
    norm_num [pB] at hi
  have : gateM pB (Xo (3 / 4)) = Xo (3 / 4) := by
    funext i j; unfold gateM; simp only [if_neg hg]
  rw [stepM_eq_gateM, hs, this]
  simp only [Fin.sum_univ_two, Xo]
  norm_num [pB]

/-- Negative `ε` (cap `1`, `ε = -1/2`): the kernel row sum exceeds `cap`. -/
def pN : Params := ⟨1 / 100, 1, 1, -1 / 2, 1, 1, 0⟩

/-- `kernel_row_le_cap` needs `0 ≤ ε`; no claim is made for `ε < 0`. -/
theorem false_kernel_row_no_eps : ¬ ∑ j, kernelM pN (Xo (3 / 2)) 0 j ≤ pN.cap := by
  rw [kernelM_Xo]
  simp only [Fin.sum_univ_two, Xo]
  norm_num [scale, pN]

/-- Non-vacuity: the gate fires on `Xo 1` at `pE`, changes it, and the output is strictly below
`cap`. -/
theorem witness_gate_active :
    EngineGate pE ∧ GateOnX pE (Xo 1) ∧ gateM pE (Xo 1) ≠ Xo 1 ∧
      ∀ i, rowS (gateM pE (Xo 1)) i < pE.cap := by
  refine ⟨engineGate_pE, (gateOnX_iff pE engineGate_pE _).2 ⟨0, by rw [rowS_Xo]; norm_num [pE]⟩,
    false_fixes_without_feasible, fun i => ?_⟩
  rw [gateM_Xo_of_gt pE engineGate_pE (by norm_num [pE]), rowS_Xo,
    scale_pE_ge_cap (by norm_num [pE])]
  norm_num [pE]

/-- Non-vacuity: the gate is off on `Xo (1/2)` at `pE` and leaves it fixed. -/
theorem witness_gate_inactive :
    ¬ GateOnX pE (Xo (1 / 2)) ∧ gateM pE (Xo (1 / 2)) = Xo (1 / 2) := by
  refine ⟨?_, gateM_Xo_of_le pE engineGate_pE (by norm_num [pE])⟩
  rw [gateOnX_iff pE engineGate_pE]
  rintro ⟨i, hi⟩
  rw [rowS_Xo] at hi
  norm_num [pE] at hi

/-- Non-vacuity for the `stepM` bridge: drive `Xo 100` from `B = 0` gives the proposal `Xo 1`
(`dt = 1/100`), the gate fires, and the step output differs from the proposal and is `< cap`. -/
theorem witness_stepM_active :
    symM pE (Xo 100) (fun _ _ => (0 : ℝ)) = Xo 1 ∧
    stepM pE (Xo 100) (fun _ _ => (0 : ℝ)) ≠ symM pE (Xo 100) (fun _ _ => (0 : ℝ)) ∧
    ∀ i, ∑ j, stepM pE (Xo 100) (fun _ _ => (0 : ℝ)) i j < pE.cap := by
  have hs : symM pE (Xo 100) (fun _ _ => (0 : ℝ)) = Xo 1 := by
    funext i j
    fin_cases i <;> fin_cases j <;> simp [symM, clipM, preM, Xo, pE]
  refine ⟨hs, ?_, fun i => ?_⟩
  · rw [stepM_eq_gateM, hs]; exact false_fixes_without_feasible
  · have := witness_gate_active.2.2.2 i
    rw [stepM_eq_gateM, hs]; exact this

end Witness

end

end Capacity
end AIEFGate
