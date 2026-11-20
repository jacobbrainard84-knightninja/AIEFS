/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.Capacity
import AIEFGateCore.Freeze

/-!
# (P4b) Weight-update bridge on `Params` / `stepM`: row sandwich, gate-factor floor, trajectory
# invariants, per-edge freezing, and the exact ON-certificate threshold

Port of the cycle-003 statements of Researcher 040282 (handle only; source path
`audit_inbox/2026-11-08_researcher-040282/researcher_040282/cycle_003/GateProposalBridge.lean`
on branch `audit-inbox`, commit `b18a27d`), restated on this project's definitions (`Params`,
`scale`,
`EngineGate`, `symM`, `rowM`, `stepM`, `Capacity.appliedFactor`) and written afresh; the source file
was used as a statement list only. The source's own `weightStep c ε h B u` is, for symmetric `B`,
`D`,
`γ > 0`, `h = γ dt`, `u = D/γ`, the step `stepM p D B` (checked on paper and by
`symM_eq_source_proposal`;
the source's `weightStep` is not imported). Differences from the source, all deliberate:

* no division by `γ`: the drive is `D` and the proposal is `preM = B + dt (D - γ B) = (1 - γ dt) B
  + dt D`;
  `0 < γ`, `0 < dt`, `γ dt < 1` are explicit hypotheses of the edge theorems (the engine validates
  only
  `γ ≥ 0`, so `γ = 0` and `γ dt ≥ 1` are engine-legal but not covered);
* `EngineGate p` (`ε > 0`, link `cap · q = a - δ`) replaces the source's `0 < ε` / `0 ≤ c`;
* the redundant initial-feasibility hypothesis `hf0` of the source ON theorem is dropped:
  `edge_eventually_on`
  needs no hypothesis on `B 0` at all (one step already gives a symmetric, nonnegative,
  zero-diagonal, feasible
  matrix), and `edge_eventually_*_from` state the exact start condition `Good p (B 0) ∨ 1 ≤ T`;
* new (not in the source): `trajectory_symmetric`, `trajectory_zero_diag` (the source never proves
  that `B`
  stays symmetric, it assumes it), `Good` and `good_step`, the exact ON-threshold `onGap_iff`
  and its N = 12 negative lemma `onGap_N12_fails`.

Content (hypotheses stated in each theorem; `B`, `D` symmetric, `B ≥ 0` where noted):

* `rowM_le_upper` / `rowM_le_envelope` (Lemma 1 upper sandwich of the proposal row sum),
  `appliedFactor_lower`, `stepM_factor_lower` (gate-factor floor `edgeFloor` from drive bounds),
  `stepM_scalar_recurrence` (`B⁺_ij = factor · max 0 ((1 - γ dt) B_ij + dt D_ij)`);
* `Good`, `good_step`, `trajectory_symmetric`, `trajectory_zero_diag`, `trajectory_nonneg`,
  `trajectory_feasible_from_first`, `trajectory_good_of_start`;
* `edge_eventually_off_from`, `edge_eventually_on_from`, `edge_eventually_off`, `edge_eventually_on`
  (per-edge ∃N OFF / ON for the guarded matrix recurrence; the hypotheses on `D` are infinite-tail
  bands
  that the engine is not shown to meet);
* `onGap_iff`, `onGap_N12_fails`, `onGap_five_neighbours`, `onGap_six_neighbours_fail`: at the
  frozen
  parameters `pE` (`dt = 1/100`, `γ = 3/200`, `cap = 19/30`, `ε = 10⁻¹²`), maximal drive `D = 1/25`
  (`η = 0.04`
  at `R = 1`; `u = D/γ = 8/3`), `B_c = 3/25` and positive drive-row bound `S` (the coarse `(N -
  1)·D` envelope is
  `S = 11/25` at `N = 12`), the ON hypothesis `hgap` holds iff `S < 18999999991/90000000000`
  (`= 0.21111…`, `5.2777…` times the maximal drive; in `u` units `S/γ < 14.074074…`).
  At `N = 12` it fails (`gap ∈ (0.0575, 0.0576)`), at five maximally driven neighbours it holds, at
  six it fails.
  This says the ON *hypothesis* is not certified by the coarse envelope at `N = 12`; it does not say
  that ON fails.

ε scope, exactly as proved: all gate statements here use `EngineGate p` (hence `ε > 0`); the only
`ε ≥ 0` result
is `Capacity.kernel_row_le_cap` (P4a). Nothing here is proved for `ε ≤ 0`.

Negations and non-vacuity: `false_rowM_upper_no_hh1`, `false_recurrence_no_symm`,
`false_factor_lower_no_rowbound`,
`false_factor_lower_no_drivebounds`, `false_trajectory_symmetric_no_start`,
`false_trajectory_diag_no_start`,
`false_trajectory_nonneg_no_start`, `false_good_no_start`, `false_off_no_gap`, `false_on_no_gap`,
`false_gap_at_threshold`, `witness_on_instance`, `witness_off_instance`,
`witness_trajectory_not_good_at_zero`.

Scope: exact reals, any finite linearly ordered node type, witnesses are `Fin 2`. Nothing about
float64,
phase dynamics, the EMA, or whether the coupled engine produces drive sequences satisfying the band
hypotheses.
-/

set_option autoImplicit false

namespace AIEFGate
namespace WeightUpdate

open Finset AIEFGate.MatrixForm AIEFGate.Capacity

noncomputable section

section General

variable {V : Type*} [Fintype V] [LinearOrder V] (p : Params)

/-- Positive off-diagonal part of a drive matrix. -/
def pdrive (D : V → V → ℝ) (i j : V) : ℝ := if i = j then 0 else max 0 (D i j)

/-- Positive drive row sum. -/
def pdriveRow (D : V → V → ℝ) (i : V) : ℝ := ∑ j, pdrive D i j

/-- Row-sum envelope of the proposal when the previous matrix is feasible and the positive drive
row sum is
`≤ S`: `(1 - γ dt) cap + dt S`. -/
def envelope (S : ℝ) : ℝ := (1 - p.γ * p.dt) * p.cap + p.dt * S

/-- Uniform lower bound on the gate factor of the edge `(i, j)` from drive row bounds `Si`, `Sj`. -/
def edgeFloor (Si Sj : ℝ) : ℝ := scale p (max (envelope p Si) (envelope p Sj))

omit [Fintype V] in
theorem pdrive_nonneg (D : V → V → ℝ) (i j : V) : 0 ≤ pdrive D i j := by
  unfold pdrive; split_ifs
  · exact le_rfl
  · exact le_max_left _ _

theorem pdriveRow_nonneg (D : V → V → ℝ) (i : V) : 0 ≤ pdriveRow D i :=
  Finset.sum_nonneg fun j _ => pdrive_nonneg D i j

omit [Fintype V] [LinearOrder V] in
theorem preM_eq_affine (D Bm : V → V → ℝ) (i j : V) :
    preM p D Bm i j = (1 - p.γ * p.dt) * Bm i j + p.dt * D i j := by
  unfold preM; ring

omit [Fintype V] in
/-- On symmetric `B`, `D` the symmetrised proposal is the clipped proposal off the diagonal. -/
theorem symM_eq_clip (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i)
    (hB : ∀ i j, Bm i j = Bm j i) {i j : V} (hij : i ≠ j) :
    symM p D Bm i j = max 0 ((1 - p.γ * p.dt) * Bm i j + p.dt * D i j) := by
  have h : clipM p D Bm j i = clipM p D Bm i j := by
    unfold clipM preM; rw [hB j i, hD j i]
  unfold symM
  rw [if_neg hij, h]
  unfold clipM
  rw [preM_eq_affine, max_comm]
  ring

omit [Fintype V] in
/-- The source proposal `max 0 ((1 - h) B + h u)` with `h = γ dt`, `u = D/γ` (`γ ≠ 0`). -/
theorem symM_eq_source_proposal (hγ : p.γ ≠ 0) (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i)
    (hB : ∀ i j, Bm i j = Bm j i) {i j : V} (hij : i ≠ j) :
    symM p D Bm i j =
      max 0 ((1 - p.γ * p.dt) * Bm i j + (p.γ * p.dt) * (D i j / p.γ)) := by
  rw [symM_eq_clip p D Bm hD hB hij]
  congr 2
  field_simp

omit [Fintype V] in
theorem symM_entry_upper (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i)
    (hB : ∀ i j, Bm i j = Bm j i) (hdt : 0 ≤ p.dt) (hh1 : p.γ * p.dt ≤ 1)
    (hB0 : ∀ i j, 0 ≤ Bm i j) (i j : V) :
    symM p D Bm i j ≤ (1 - p.γ * p.dt) * Bm i j + p.dt * pdrive D i j := by
  have hc : 0 ≤ 1 - p.γ * p.dt := sub_nonneg.mpr hh1
  by_cases hij : i = j
  · subst hij
    simp only [symM, pdrive, if_true, mul_zero, add_zero]
    exact mul_nonneg hc (hB0 i i)
  · rw [symM_eq_clip p D Bm hD hB hij]
    simp only [pdrive, if_neg hij]
    exact max_le (add_nonneg (mul_nonneg hc (hB0 i j)) (mul_nonneg hdt (le_max_left _ _)))
      (add_le_add le_rfl (mul_le_mul_of_nonneg_left (le_max_right _ _) hdt))

/-- **Lemma 1, upper sandwich of the proposal row sum.** For symmetric `B ≥ 0` and symmetric `D`,
`0 ≤ dt`, `γ dt ≤ 1`: `rowM ≤ (1 - γ dt) rowS B + dt · pdriveRow D`. -/
theorem rowM_le_upper (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i)
    (hB : ∀ i j, Bm i j = Bm j i) (hdt : 0 ≤ p.dt) (hh1 : p.γ * p.dt ≤ 1)
    (hB0 : ∀ i j, 0 ≤ Bm i j) (i : V) :
    rowM p D Bm i ≤ (1 - p.γ * p.dt) * rowS Bm i + p.dt * pdriveRow D i := by
  unfold rowM
  calc ∑ j, symM p D Bm i j ≤ ∑ j, ((1 - p.γ * p.dt) * Bm i j + p.dt * pdrive D i j) :=
        Finset.sum_le_sum fun j _ => symM_entry_upper p D Bm hD hB hdt hh1 hB0 i j
    _ = (1 - p.γ * p.dt) * rowS Bm i + p.dt * pdriveRow D i := by
        simp only [rowS, pdriveRow, Finset.sum_add_distrib, Finset.mul_sum]

/-- **Lemma 1, envelope form.** If `B` is feasible (`rowS B ≤ cap`) and `pdriveRow D i ≤ S`, the
proposal row sum is `≤ (1 - γ dt) cap + dt S`. -/
theorem rowM_le_envelope (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i)
    (hB : ∀ i j, Bm i j = Bm j i) (hdt : 0 ≤ p.dt) (hh1 : p.γ * p.dt ≤ 1)
    (hB0 : ∀ i j, 0 ≤ Bm i j) (hf : ∀ i, rowS Bm i ≤ p.cap) (i : V) {S : ℝ}
    (hS : pdriveRow D i ≤ S) : rowM p D Bm i ≤ envelope p S := by
  refine (rowM_le_upper p D Bm hD hB hdt hh1 hB0 i).trans ?_
  unfold envelope
  exact add_le_add (mul_le_mul_of_nonneg_left (hf i) (sub_nonneg.mpr hh1))
    (mul_le_mul_of_nonneg_left hS hdt)

/-- `appliedFactor` is the multiplier of the proposal entry: `gateM X = X · appliedFactor X` (zero
diagonal). -/
theorem gateM_eq_mul_appliedFactor (X : V → V → ℝ) (hd : ∀ i, X i i = 0) (i j : V) :
    gateM p X i j = X i j * appliedFactor p X i j := by
  unfold gateM appliedFactor kernelM
  by_cases hg : GateOnX p X
  · simp only [if_pos hg]
    by_cases hij : i = j
    · subst hij; simp [hd]
    · simp only [if_neg hij]
  · simp only [if_neg hg, mul_one]

theorem stepM_eq_mul_appliedFactor (D Bm : V → V → ℝ) (i j : V) :
    stepM p D Bm i j = symM p D Bm i j * appliedFactor p (symM p D Bm) i j := by
  rw [stepM_eq_gateM]
  exact gateM_eq_mul_appliedFactor p _ (symM_diag p D Bm) i j

/-- **Scalar recurrence of one edge** (`i ≠ j`, symmetric `B`, `D`):
`B⁺_ij = factor_ij · max 0 ((1 - γ dt) B_ij + dt D_ij)`. -/
theorem stepM_scalar_recurrence (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i)
    (hB : ∀ i j, Bm i j = Bm j i) {i j : V} (hij : i ≠ j) :
    stepM p D Bm i j =
      appliedFactor p (symM p D Bm) i j *
        max 0 ((1 - p.γ * p.dt) * Bm i j + p.dt * D i j) := by
  rw [stepM_eq_mul_appliedFactor, symM_eq_clip p D Bm hD hB hij, mul_comm]

omit [LinearOrder V] in
theorem appliedFactor_le_one (X : V → V → ℝ) (i j : V) : appliedFactor p X i j ≤ 1 := by
  unfold appliedFactor
  split_ifs
  · exact (min_le_left _ _).trans (scale_le_one p _)
  · exact le_rfl

omit [LinearOrder V] in
theorem appliedFactor_nonneg (hp : EngineGate p) {X : V → V → ℝ} (hx : ∀ i j, 0 ≤ X i j)
    (i j : V) : 0 ≤ appliedFactor p X i j := by
  unfold appliedFactor
  split_ifs
  · exact le_min (scale_nonneg p hp.cap_pos.le hp.eps_pos.le (rowS_nonneg hx i))
      (scale_nonneg p hp.cap_pos.le hp.eps_pos.le (rowS_nonneg hx j))
  · exact zero_le_one

omit [LinearOrder V] in
/-- **Gate-factor floor from row bounds.** If `rowS X i ≤ Mi` and `rowS X j ≤ Mj` (`X ≥ 0`), the
factor
the gate applies to entry `(i, j)` is `≥ scale (max Mi Mj)`. -/
theorem appliedFactor_lower (hp : EngineGate p) {X : V → V → ℝ} (hx : ∀ i j, 0 ≤ X i j)
    (i j : V) {Mi Mj : ℝ} (hi : rowS X i ≤ Mi) (hj : rowS X j ≤ Mj) :
    scale p (max Mi Mj) ≤ appliedFactor p X i j := by
  unfold appliedFactor
  split_ifs
  · refine le_min ?_ ?_
    · exact AIEFGate.scale_anti p (hi.trans (le_max_left _ _))
        (add_pos_of_nonneg_of_pos (rowS_nonneg hx i) hp.eps_pos) hp.cap_pos.le
    · exact AIEFGate.scale_anti p (hj.trans (le_max_right _ _))
        (add_pos_of_nonneg_of_pos (rowS_nonneg hx j) hp.eps_pos) hp.cap_pos.le
  · exact scale_le_one p _

omit [Fintype V] [LinearOrder V] in
theorem envelope_nonneg (hp : EngineGate p) (hdt : 0 ≤ p.dt) (hh1 : p.γ * p.dt ≤ 1) {S : ℝ}
    (hS : 0 ≤ S) : 0 ≤ envelope p S :=
  add_nonneg (mul_nonneg (sub_nonneg.mpr hh1) hp.cap_pos.le) (mul_nonneg hdt hS)

omit [Fintype V] [LinearOrder V] in
theorem edgeFloor_pos (hp : EngineGate p) (hdt : 0 ≤ p.dt) (hh1 : p.γ * p.dt ≤ 1) {Si Sj : ℝ}
    (hSi : 0 ≤ Si) : 0 < edgeFloor p Si Sj := by
  unfold edgeFloor scale
  exact lt_min zero_lt_one (div_pos hp.cap_pos (add_pos_of_nonneg_of_pos
    ((envelope_nonneg p hp hdt hh1 hSi).trans (le_max_left _ _)) hp.eps_pos))

omit [Fintype V] [LinearOrder V] in
theorem edgeFloor_le_one (Si Sj : ℝ) : edgeFloor p Si Sj ≤ 1 := scale_le_one p _

/-- **Gate-factor floor from drive bounds.** For feasible symmetric `B ≥ 0`, symmetric `D` and
positive
drive row sums `≤ Si`, `≤ Sj`, the factor applied to the proposal entry `(i, j)` is `≥ edgeFloor p
Si Sj`. -/
theorem stepM_factor_lower (hp : EngineGate p) (hdt : 0 ≤ p.dt) (hh1 : p.γ * p.dt ≤ 1)
    (D Bm : V → V → ℝ) (hD : ∀ i j, D i j = D j i) (hB : ∀ i j, Bm i j = Bm j i)
    (hB0 : ∀ i j, 0 ≤ Bm i j) (hf : ∀ i, rowS Bm i ≤ p.cap) (i j : V) {Si Sj : ℝ}
    (hSi : pdriveRow D i ≤ Si) (hSj : pdriveRow D j ≤ Sj) :
    edgeFloor p Si Sj ≤ appliedFactor p (symM p D Bm) i j :=
  appliedFactor_lower p hp (symM_nonneg p D Bm) i j
    (rowM_le_envelope p D Bm hD hB hdt hh1 hB0 hf i hSi)
    (rowM_le_envelope p D Bm hD hB hdt hh1 hB0 hf j hSj)

/-! ### Trajectory invariants -/

/-- The regular states of the engine matrix: nonnegative, symmetric, zero diagonal, row sums `≤
cap`. -/
def Good (X : V → V → ℝ) : Prop :=
  (∀ i j, 0 ≤ X i j) ∧ (∀ i j, X i j = X j i) ∧ (∀ i, X i i = 0) ∧ ∀ i, rowS X i ≤ p.cap

/-- One engine step always lands in `Good` (`EngineGate p`; no hypothesis on `D` or `B`). -/
theorem good_step (hp : EngineGate p) (D Bm : V → V → ℝ) : Good p (stepM p D Bm) :=
  ⟨stepM_nonneg p hp D Bm, stepM_symm p D Bm, stepM_diag p D Bm, stepM_row_le_cap p hp D Bm⟩

variable (B D : ℕ → V → V → ℝ)

/-- **B stays symmetric.** If `B 0` is symmetric, every `B n` is (`B (n+1)` is symmetric
unconditionally). -/
theorem trajectory_symmetric (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n))
    (hB0 : ∀ i j, B 0 i j = B 0 j i) : ∀ n i j, B n i j = B n j i := by
  intro n
  cases n with
  | zero => exact hB0
  | succ n => intro i j; rw [hrec n]; exact stepM_symm p _ _ i j

/-- **B keeps a zero diagonal** (if `B 0` has one). -/
theorem trajectory_zero_diag (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n))
    (hB0 : ∀ i, B 0 i i = 0) : ∀ n i, B n i i = 0 := by
  intro n
  cases n with
  | zero => exact hB0
  | succ n => intro i; rw [hrec n]; exact stepM_diag p _ _ i

/-- **B stays nonnegative** (if `B 0` is). -/
theorem trajectory_nonneg (hp : EngineGate p) (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n))
    (hB0 : ∀ i j, 0 ≤ B 0 i j) : ∀ n i j, 0 ≤ B n i j := by
  intro n
  cases n with
  | zero => exact hB0
  | succ n => intro i j; rw [hrec n]; exact stepM_nonneg p hp _ _ i j

/-- **Feasible from the first step on** (no hypothesis on `B 0`). -/
theorem trajectory_feasible_from_first (hp : EngineGate p)
    (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n)) : ∀ n i, rowS (B (n + 1)) i ≤ p.cap := by
  intro n i; rw [hrec n]; exact stepM_row_le_cap p hp _ _ i

/-- **`Good` from `T` on**, if `B 0` is `Good` or `T ≥ 1`. -/
theorem trajectory_good_of_start (hp : EngineGate p) (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n))
    (T : ℕ) (hstart : Good p (B 0) ∨ 1 ≤ T) : ∀ n, T ≤ n → Good p (B n) := by
  intro n hn
  cases n with
  | zero =>
      rcases hstart with h | h
      · exact h
      · omega
  | succ n => rw [hrec n]; exact good_step p hp _ _

/-! ### Per-edge freezing for the guarded matrix recurrence -/

/-- **Edge OFF.** Drive `D (T+n) i j ≤ U` with `0 ≤ U < γ B_c` (fixed point `U/γ < B_c`): eventually
`B (T+n) i j < B_c`. -/
theorem edge_eventually_off_from (hp : EngineGate p) (hdt : 0 < p.dt) (hh1 : p.γ * p.dt < 1)
    (hγ : 0 < p.γ) (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n))
    (hDs : ∀ n i j, D n i j = D n j i) (T : ℕ) (hstart : Good p (B 0) ∨ 1 ≤ T)
    (i j : V) (hij : i ≠ j) (U Bc : ℝ) (hu : ∀ n, D (T + n) i j ≤ U) (hU0 : 0 ≤ U)
    (hUc : U < p.γ * Bc) : ∃ N, ∀ n ≥ N, B (T + n) i j < Bc := by
  have hgood := trajectory_good_of_start p B D hp hrec T hstart
  refine Freeze.edge_off (fun n => B (T + n) i j) (fun n => p.dt * D (T + n) i j)
    (fun n => appliedFactor p (symM p (D (T + n)) (B (T + n))) i j) (p.γ * p.dt) (p.dt * U) Bc
    (mul_pos hγ hdt) hh1 ((hgood T le_rfl).1 i j) (fun n => ?_) (fun n => ?_) (fun n => ?_)
    (fun n => ?_) (mul_nonneg hdt.le hU0) (by nlinarith [mul_lt_mul_of_pos_left hUc hdt])
  · exact appliedFactor_nonneg p hp (symM_nonneg p _ _) i j
  · exact appliedFactor_le_one p _ i j
  · have h1 := stepM_scalar_recurrence p (D (T + n)) (B (T + n)) (hDs _)
      (hgood (T + n) (by omega)).2.1 hij
    simp only [← Nat.add_assoc]
    rw [hrec (T + n), h1]
  · exact mul_le_mul_of_nonneg_left (hu n) hdt.le

/-- **Edge ON.** `D (T+n) i j ≥ L ≥ 0`, positive drive rows `≤ Si, Sj`, and
`B_c < κ · dt L / (1 - κ (1 - γ dt))` with `κ = edgeFloor`: eventually `B (T+n) i j > B_c`. -/
theorem edge_eventually_on_from (hp : EngineGate p) (hdt : 0 < p.dt) (hh1 : p.γ * p.dt < 1)
    (hγ : 0 < p.γ) (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n))
    (hDs : ∀ n i j, D n i j = D n j i) (T : ℕ) (hstart : Good p (B 0) ∨ 1 ≤ T)
    (i j : V) (hij : i ≠ j) (Si Sj L Bc : ℝ)
    (hSi : ∀ n, pdriveRow (D (T + n)) i ≤ Si) (hSj : ∀ n, pdriveRow (D (T + n)) j ≤ Sj)
    (hL : ∀ n, L ≤ D (T + n) i j) (hL0 : 0 ≤ L)
    (hgap : Bc < edgeFloor p Si Sj * (p.dt * L) / (1 - edgeFloor p Si Sj * (1 - p.γ * p.dt))) :
    ∃ N, ∀ n ≥ N, Bc < B (T + n) i j := by
  have hgood := trajectory_good_of_start p B D hp hrec T hstart
  have hS0 : 0 ≤ Si := (pdriveRow_nonneg _ i).trans (hSi 0)
  refine Freeze.edge_on (fun n => B (T + n) i j) (fun n => p.dt * D (T + n) i j)
    (fun n => appliedFactor p (symM p (D (T + n)) (B (T + n))) i j) (p.γ * p.dt)
    (edgeFloor p Si Sj) (p.dt * L) Bc (mul_pos hγ hdt) hh1
    (edgeFloor_pos p hp hdt.le hh1.le hS0) (edgeFloor_le_one p Si Sj) (fun n => ?_) (fun n => ?_)
    ((hgood T le_rfl).1 i j) (fun n => mul_le_mul_of_nonneg_left (hL n) hdt.le)
    (mul_nonneg hdt.le hL0) hgap
  · obtain ⟨hB0, hBs, _, hBf⟩ := hgood (T + n) (by omega)
    exact stepM_factor_lower p hp hdt.le hh1.le (D (T + n)) (B (T + n)) (hDs _) hBs hB0 hBf i j
      (hSi n) (hSj n)
  · have h1 := stepM_scalar_recurrence p (D (T + n)) (B (T + n)) (hDs _)
      (hgood (T + n) (by omega)).2.1 hij
    simp only [← Nat.add_assoc]
    rw [hrec (T + n), h1]

/-- **Edge OFF, from `n = 0`, no hypothesis on `B 0`.** -/
theorem edge_eventually_off (hp : EngineGate p) (hdt : 0 < p.dt) (hh1 : p.γ * p.dt < 1)
    (hγ : 0 < p.γ) (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n))
    (hDs : ∀ n i j, D n i j = D n j i)
    (i j : V) (hij : i ≠ j) (U Bc : ℝ) (hu : ∀ n, D n i j ≤ U) (hU0 : 0 ≤ U)
    (hUc : U < p.γ * Bc) : ∃ N, ∀ n ≥ N, B n i j < Bc := by
  obtain ⟨N, hN⟩ := edge_eventually_off_from p B D hp hdt hh1 hγ hrec hDs 1 (Or.inr le_rfl) i j hij
    U Bc (fun n => hu _) hU0 hUc
  refine ⟨N + 1, fun n hn => ?_⟩
  have := hN (n - 1) (by omega)
  rwa [show 1 + (n - 1) = n by omega] at this

/-- **Edge ON, from `n = 0`, no initial-feasibility hypothesis and no hypothesis on `B 0`** (the
source ON statement assumes initial feasibility; that is redundant). -/
theorem edge_eventually_on (hp : EngineGate p) (hdt : 0 < p.dt) (hh1 : p.γ * p.dt < 1)
    (hγ : 0 < p.γ) (hrec : ∀ n, B (n + 1) = stepM p (D n) (B n))
    (hDs : ∀ n i j, D n i j = D n j i)
    (i j : V) (hij : i ≠ j) (Si Sj L Bc : ℝ)
    (hSi : ∀ n, pdriveRow (D n) i ≤ Si) (hSj : ∀ n, pdriveRow (D n) j ≤ Sj)
    (hL : ∀ n, L ≤ D n i j) (hL0 : 0 ≤ L)
    (hgap : Bc < edgeFloor p Si Sj * (p.dt * L) / (1 - edgeFloor p Si Sj * (1 - p.γ * p.dt))) :
    ∃ N, ∀ n ≥ N, Bc < B n i j := by
  obtain ⟨N, hN⟩ := edge_eventually_on_from p B D hp hdt hh1 hγ hrec hDs 1 (Or.inr le_rfl) i j hij
    Si Sj L Bc (fun n => hSi _) (fun n => hSj _) (fun n => hL _) hL0 hgap
  refine ⟨N + 1, fun n hn => ?_⟩
  have := hN (n - 1) (by omega)
  rwa [show 1 + (n - 1) = n by omega] at this

end General

/-! ### Exact ON-certificate threshold at the frozen parameters -/

section Threshold

open EngineWitness (pE engineGate_pE)

/-- The ON-hypothesis value `κ · dt L / (1 - κ (1 - γ dt))` of `edge_eventually_on` at `pE`,
maximal drive
`L = 1/25` (`η = 0.04`, `R = 1`) and equal positive-drive-row bounds `S` (`κ = edgeFloor pE S S`).
-/
def onGap (S : ℝ) : ℝ :=
  edgeFloor pE S S * (pE.dt * (1 / 25)) / (1 - edgeFloor pE S S * (1 - pE.γ * pE.dt))

/-- The exact threshold: `B_c = 3/25 < onGap S ↔ S < Sstar`, `Sstar = 18999999991/90000000000 =
0.2111…`. -/
def Sstar : ℝ := 18999999991 / 90000000000

theorem onGap_of_ge (S : ℝ) (hS0 : 0 ≤ S) (hS : pE.cap ≤ envelope pE S + pE.ε) :
    onGap S = pE.cap * (pE.dt * (1 / 25)) / (pE.dt * S + pE.ε) := by
  have hε : 0 < pE.ε := engineGate_pE.eps_pos
  have hE : 0 < envelope pE S + pE.ε := lt_of_lt_of_le engineGate_pE.cap_pos hS
  have hk : edgeFloor pE S S = pE.cap / (envelope pE S + pE.ε) := by
    unfold edgeFloor scale
    rw [max_self]
    exact min_eq_right ((div_le_one hE).2 hS)
  have hden : pE.dt * S + pE.ε = (envelope pE S + pE.ε) - pE.cap * (1 - pE.γ * pE.dt) := by
    unfold envelope; ring
  unfold onGap
  rw [hk, hden]
  have hpos : 0 < (envelope pE S + pE.ε) - pE.cap * (1 - pE.γ * pE.dt) := by
    rw [← hden]
    have : 0 ≤ pE.dt * S := mul_nonneg (by norm_num [pE]) hS0
    linarith
  field_simp

theorem onGap_of_lt (S : ℝ) (hS0 : 0 ≤ S) (hS : envelope pE S + pE.ε < pE.cap) :
    onGap S = 8 / 3 := by
  have hk : edgeFloor pE S S = 1 := by
    unfold edgeFloor scale
    rw [max_self]
    exact min_eq_left ((one_le_div (by simp only [envelope, pE]; nlinarith)).2 hS.le)
  unfold onGap
  rw [hk]
  norm_num [pE]

/-- **Exact ON-certificate threshold (`pE`, `B_c = 3/25`, `L = 1/25`, `S ≥ 0`).** The ON hypothesis
`hgap`
of `edge_eventually_on` holds iff the positive-drive-row bound is `S < 18999999991/90000000000`. -/
theorem onGap_iff (S : ℝ) (hS : 0 ≤ S) : 3 / 25 < onGap S ↔ S < Sstar := by
  by_cases h : pE.cap ≤ envelope pE S + pE.ε
  · rw [onGap_of_ge S hS h]
    have hd : 0 < pE.dt * S + pE.ε := by
      have : 0 < pE.ε := engineGate_pE.eps_pos
      have : 0 ≤ pE.dt * S := mul_nonneg (by norm_num [pE]) hS
      linarith
    rw [lt_div_iff₀ hd]
    norm_num [pE, Sstar]
    constructor <;> intro h' <;> linarith
  · rw [onGap_of_lt S hS (not_le.mp h)]
    have : S < Sstar := by
      have := not_le.mp h
      norm_num [envelope, pE, Sstar] at this ⊢
      linarith
    simp only [this, iff_true]
    norm_num

/-- At `N = 12` the coarse envelope `S = 11 · (1/25) = 11/25` does **not** satisfy the ON hypothesis
`B_c = 3/25 < onGap S` (`onGap (11/25) ≈ 0.0576`). This is a statement about the hypothesis, not a
statement that ON fails. -/
theorem onGap_N12_fails : ¬ 3 / 25 < onGap (11 / 25) := by
  rw [onGap_iff _ (by norm_num)]
  norm_num [Sstar]

theorem onGap_N12_value : 575 / 10000 < onGap (11 / 25) ∧ onGap (11 / 25) < 576 / 10000 := by
  rw [onGap_of_ge _ (by norm_num) (by norm_num [envelope, pE])]
  norm_num [pE]

/-- Five maximally driven neighbours (`S = 5/25`): the ON hypothesis holds. -/
theorem onGap_five_neighbours : 3 / 25 < onGap (5 / 25) := by
  rw [onGap_iff _ (by norm_num)]
  norm_num [Sstar]

/-- Six maximally driven neighbours (`S = 6/25`): it fails. -/
theorem onGap_six_neighbours_fail : ¬ 3 / 25 < onGap (6 / 25) := by
  rw [onGap_iff _ (by norm_num)]
  norm_num [Sstar]

/-- At the threshold itself the ON hypothesis fails (strictness of `onGap_iff`). -/
theorem false_gap_at_threshold : ¬ 3 / 25 < onGap Sstar := by
  rw [onGap_iff _ (by norm_num [Sstar])]
  exact lt_irrefl _

end Threshold

/-! ### Negations and non-vacuity witnesses (`Fin 2`) -/

section Witness

open EngineWitness (pE engineGate_pE)

/-- Parameters with `γ dt = 2 > 1` (an `EngineGate`, `cap = 1`, `ε = 1`). -/
def pH : Params := ⟨2, 1, 1, 1, 1, 1, 0⟩

/-- Orbit of `stepM pE` from `B0` under the drive sequence `D` (on `Fin 2`). -/
def orbit (D : ℕ → Fin 2 → Fin 2 → ℝ) (B0 : Fin 2 → Fin 2 → ℝ) : ℕ → Fin 2 → Fin 2 → ℝ
  | 0 => B0
  | n + 1 => stepM pE (D n) (orbit D B0 n)

/-- Positive drive row sum of `Xo a`. -/
theorem pdriveRow_Xo {a : ℝ} (ha : 0 ≤ a) (i : Fin 2) : pdriveRow (Xo a) i = a := by
  fin_cases i <;> simp [pdriveRow, pdrive, Xo, Fin.sum_univ_two, ha]

/-- `γ dt ≤ 1` is needed for the row sandwich (here `γ dt = 2`). -/
theorem false_rowM_upper_no_hh1 :
    ¬ rowM pH (Xo 0) (Xo 1) 0 ≤
      (1 - pH.γ * pH.dt) * rowS (Xo 1) 0 + pH.dt * pdriveRow (Xo 0) 0 := by
  rw [pdriveRow_Xo le_rfl, rowS_Xo]
  have : rowM pH (Xo 0) (Xo 1) 0 = 0 := by
    simp [rowM, symM, clipM, preM, Fin.sum_univ_two, Xo, pH]
  rw [this]
  norm_num [pH]

/-- A non-symmetric `B` with row sums `≤ cap`. -/
theorem symM_pE_Xn : symM pE (Xo 0) Xn = fun i j => if i = j then 0 else 99985 / 2000000 := by
  funext i j
  fin_cases i <;> fin_cases j <;> simp [symM, clipM, preM, Xo, Xn, pE] <;> norm_num

theorem not_gateOn_symM_Xn : ¬ GateOnX pE (symM pE (Xo 0) Xn) := by
  rw [gateOnX_iff pE engineGate_pE, symM_pE_Xn]
  rintro ⟨i, hi⟩
  fin_cases i <;> simp [rowS, Fin.sum_univ_two] at hi <;> norm_num [pE] at hi

/-- The symmetry of `B` is needed for the scalar recurrence. -/
theorem false_recurrence_no_symm :
    ¬ stepM pE (Xo 0) Xn 0 1 =
      appliedFactor pE (symM pE (Xo 0) Xn) 0 1 *
        max 0 ((1 - pE.γ * pE.dt) * Xn 0 1 + pE.dt * Xo 0 0 1) := by
  intro h
  have hf : appliedFactor pE (symM pE (Xo 0) Xn) 0 1 = 1 := by
    unfold appliedFactor; rw [if_neg not_gateOn_symM_Xn]
  have hs : stepM pE (Xo 0) Xn = symM pE (Xo 0) Xn := by
    rw [stepM_eq_gateM]
    exact gateM_fixes_feasible pE engineGate_pE _ (fun i => by
      rw [symM_pE_Xn]; fin_cases i <;> simp [rowS, Fin.sum_univ_two] <;> norm_num [pE])
  rw [hs, hf, symM_pE_Xn] at h
  norm_num [Xn, Xo, pE] at h

/-- A nonnegative matrix with row `0` summing to `1 > cap` and row `1` summing to `0`. -/
def Xr : Fin 2 → Fin 2 → ℝ := fun i j => if i = 0 ∧ j = 1 then 1 else 0

theorem Xr_nonneg (i j : Fin 2) : 0 ≤ Xr i j := by
  unfold Xr; split_ifs <;> norm_num

theorem gateOn_Xr : GateOnX pE Xr :=
  (gateOnX_iff pE engineGate_pE _).2 ⟨0, by simp [rowS, Xr]; norm_num [pE]⟩

/-- The row bounds `rowS X i ≤ Mi` are needed for the gate-factor floor (`Mi = Mj = 0`, row `0` has
sum `1`). -/
theorem false_factor_lower_no_rowbound :
    ¬ scale pE (max 0 0) ≤ appliedFactor pE Xr 0 1 := by
  intro h
  have h1 : scale pE (max 0 0) = 1 := by
    simp only [scale, max_self]
    exact min_eq_left (by
      rw [le_div_iff₀ (by norm_num [pE])]; norm_num [pE])
  have h2 : appliedFactor pE Xr 0 1 ≤ scale pE 1 := by
    unfold appliedFactor
    rw [if_pos gateOn_Xr]
    refine (min_le_left _ _).trans ?_
    simp [rowS, Xr]
  rw [h1] at h
  linarith [h2, scale_pE_one_lt]

/-- The drive-row bounds are needed for `stepM_factor_lower` (`D = Xo 100`, `Si = Sj = 0`). -/
theorem false_factor_lower_no_drivebounds :
    ¬ edgeFloor pE 0 0 ≤ appliedFactor pE (symM pE (Xo 100) (fun _ _ => (0 : ℝ))) 0 1 := by
  intro h
  have hs : symM pE (Xo 100) (fun _ _ => (0 : ℝ)) = Xo 1 := witness_stepM_active.1
  have h1 : edgeFloor pE 0 0 = 1 := by
    unfold edgeFloor scale
    rw [max_self]
    exact min_eq_left (by
      rw [le_div_iff₀ (by norm_num [envelope, pE])]; norm_num [envelope, pE])
  have hg : GateOnX pE (Xo 1) :=
    (gateOnX_iff pE engineGate_pE _).2 ⟨0, by rw [rowS_Xo]; norm_num [pE]⟩
  rw [hs, h1] at h
  unfold appliedFactor at h
  rw [if_pos hg, rowS_Xo, rowS_Xo, min_self] at h
  linarith [scale_pE_one_lt]

/-- Without the hypothesis on `B 0` the orbit need not be symmetric (`n = 0`). -/
theorem false_trajectory_symmetric_no_start :
    ¬ orbit (fun _ => Xo 0) Xn 0 0 1 = orbit (fun _ => Xo 0) Xn 0 1 0 := by
  change Xn 0 1 ≠ Xn 1 0
  simp [Xn]

/-- Without the hypothesis on `B 0` the orbit need not have a zero diagonal. -/
theorem false_trajectory_diag_no_start :
    ¬ orbit (fun _ => Xo 0) (fun _ _ => 1) 0 0 0 = 0 := by
  change (1 : ℝ) ≠ 0
  norm_num

/-- Without the hypothesis on `B 0` the orbit need not be nonnegative. -/
theorem false_trajectory_nonneg_no_start :
    ¬ 0 ≤ orbit (fun _ => Xo 0) (fun _ _ => -1) 0 0 0 := by
  change ¬ (0 : ℝ) ≤ -1
  norm_num

/-- The start condition of `trajectory_good_of_start` is needed (`T = 0`, `B 0 = Xo 1` has row sum
`1 > cap`). -/
theorem false_good_no_start : ¬ Good pE (orbit (fun _ => Xo 0) (Xo 1) 0) := by
  intro h
  have := h.2.2.2 0
  change rowS (Xo 1) 0 ≤ pE.cap at this
  rw [rowS_Xo] at this
  norm_num [pE] at this

/-- ON instance: `B 0 = 0`, constant maximal drive `D = Xo (1/25)`. -/
def Bon : ℕ → Fin 2 → Fin 2 → ℝ := orbit (fun _ => Xo (1 / 25)) (fun _ _ => 0)

/-- OFF instance: `B 0 = Xo (1/5)` (above `B_c`), constant small drive `D = Xo (1/1000)`. -/
def Boff : ℕ → Fin 2 → Fin 2 → ℝ := orbit (fun _ => Xo (1 / 1000)) (Xo (1 / 5))

theorem good_zero : Good pE (fun _ _ : Fin 2 => (0 : ℝ)) := by
  refine ⟨fun _ _ => le_rfl, fun _ _ => rfl, fun _ => rfl, fun i => ?_⟩
  simp [rowS]; norm_num [pE]

/-- **Non-vacuity of `edge_eventually_on`** at the frozen parameters `pE`, with the engine's
`B_c = 3/25`: every hypothesis is discharged (`EngineGate pE`, `0 < γ`, `0 < dt`, `γ dt < 1`,
symmetric
drive, `Si = Sj = L = 1/25`, `hgap` by `onGap_iff`), and the conclusion `3/25 < B_n(0,1)` is not
trivial. -/
theorem witness_on_instance : ∃ N, ∀ n ≥ N, (3 / 25 : ℝ) < Bon n 0 1 :=
  edge_eventually_on pE Bon (fun _ => Xo (1 / 25)) engineGate_pE (by norm_num [pE])
    (by norm_num [pE]) (by norm_num [pE]) (fun n => rfl) (fun n i j => Xo_symm _ i j) 0 1
    (by decide) (1 / 25) (1 / 25) (1 / 25) (3 / 25) (fun n => (pdriveRow_Xo (by norm_num) 0).le)
    (fun n => (pdriveRow_Xo (by norm_num) 1).le)
    (fun n => by simp [Xo]) (by norm_num)
    ((onGap_iff _ (by norm_num)).2 (by norm_num [Sstar]))

/-- **Non-vacuity of `edge_eventually_off`**: starts above `B_c` and ends below. -/
theorem witness_off_instance :
    (3 / 25 : ℝ) < Boff 0 0 1 ∧ ∃ N, ∀ n ≥ N, Boff n 0 1 < (3 / 25 : ℝ) := by
  refine ⟨by simp [Boff, orbit, Xo]; norm_num, ?_⟩
  exact edge_eventually_off pE Boff (fun _ => Xo (1 / 1000)) engineGate_pE (by norm_num [pE])
    (by norm_num [pE]) (by norm_num [pE]) (fun n => rfl) (fun n i j => Xo_symm _ i j) 0 1
    (by decide) (1 / 1000) (3 / 25) (fun n => by simp [Xo]) (by norm_num) (by norm_num [pE])

/-- The ON claim needs its gap hypothesis: the OFF instance satisfies all other hypotheses of the ON
theorem (`L = Si = Sj = 1/1000`) yet ends below `B_c`. -/
theorem false_on_no_gap : ¬ ∃ N, ∀ n ≥ N, (3 / 25 : ℝ) < Boff n 0 1 := by
  rintro ⟨N, h⟩
  obtain ⟨N0, h0⟩ := witness_off_instance.2
  have := h (N + N0) (by omega)
  have := h0 (N + N0) (by omega)
  linarith

theorem false_on_no_gap_from : ¬ ∃ N, ∀ n ≥ N, (3 / 25 : ℝ) < Boff (1 + n) 0 1 := by
  rintro ⟨N, h⟩
  obtain ⟨N0, h0⟩ := witness_off_instance.2
  have := h (N + N0) (by omega)
  have := h0 (1 + (N + N0)) (by omega)
  linarith

/-- The OFF claim needs its gap hypothesis: the ON instance satisfies all other hypotheses of the
OFF
theorem (`U = 1/25`) yet ends above `B_c`. -/
theorem false_off_no_gap : ¬ ∃ N, ∀ n ≥ N, Bon n 0 1 < (3 / 25 : ℝ) := by
  rintro ⟨N, h⟩
  obtain ⟨N0, h0⟩ := witness_on_instance
  have := h (N + N0) (by omega)
  have := h0 (N + N0) (by omega)
  linarith

theorem false_off_no_gap_from : ¬ ∃ N, ∀ n ≥ N, Bon (1 + n) 0 1 < (3 / 25 : ℝ) := by
  rintro ⟨N, h⟩
  obtain ⟨N0, h0⟩ := witness_on_instance
  have := h (N + N0) (by omega)
  have := h0 (1 + (N + N0)) (by omega)
  linarith

/-- The orbit from a non-`Good` start is `Good` after one step (non-vacuity of `good_step`). -/
theorem witness_trajectory_not_good_at_zero :
    ¬ Good pE (orbit (fun _ => Xo 0) (Xo 1) 0) ∧ Good pE (orbit (fun _ => Xo 0) (Xo 1) 1) :=
  ⟨false_good_no_start, good_step pE engineGate_pE _ _⟩

end Witness

end

end WeightUpdate
end AIEFGate
