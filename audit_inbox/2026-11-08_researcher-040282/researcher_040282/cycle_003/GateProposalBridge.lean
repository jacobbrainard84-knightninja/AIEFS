import GateFoundations
import FreezeCore
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
Exact-real proposal / guarded capacity / scalar-comparison bridge.
The diagonal mask and global guard are explicit. Source-side symmetrization
is identified only under symmetric weights and drive. No theorem here proves
Python/float64 equivalence, phase locking, delayed evolution, or EMA correctness.
-/

set_option autoImplicit false
noncomputable section
open scoped BigOperators

namespace Researcher040282

variable {ι : Type*} [Fintype ι]

def positiveDrive (u : Weights ι) (i j : ι) : ℝ := by
  classical
  exact if i = j then 0 else max 0 (u i j)

def positiveDriveRow (u : Weights ι) (i : ι) : ℝ := ∑ j, positiveDrive u i j

def proposal (h : ℝ) (B u : Weights ι) : Weights ι := by
  classical
  exact fun i j => if i = j then 0 else max 0 ((1-h)*B i j + h*u i j)

def symmetrizedProposal (h : ℝ) (B u : Weights ι) : Weights ι := by
  classical
  exact fun i j => if i = j then 0 else
    (max 0 ((1-h)*B i j+h*u i j) + max 0 ((1-h)*B j i+h*u j i))/2

def appliedNodeScale (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i : ι) : ℝ := by
  classical
  exact if feasible c W then 1 else nodeScale c ε W i

def scaleFloor (c ε M : ℝ) : ℝ := min 1 (c / (M + ε))
def driveEnvelope (c h S : ℝ) : ℝ := (1-h)*c + h*S

def edgeFloor (c ε h Si Sj : ℝ) : ℝ :=
  scaleFloor c ε (max (driveEnvelope c h Si) (driveEnvelope c h Sj))

def weightStep (c ε h : ℝ) (B u : Weights ι) : Weights ι :=
  gate (fun _ => c) ε (proposal h B u)

theorem normalized_affine_identity (γ dt η μ b R : ℝ) (hγ : γ ≠ 0) :
    (1-γ*dt)*b + (γ*dt)*(((η+μ)*R-μ)/γ) =
      b + dt*((η+μ)*R-μ-γ*b) := by
  field_simp [hγ]
  ring

theorem gap_capacity_iff (a δ q r : ℝ) (hq : 0 < q) :
    δ ≤ a-q*r ↔ r ≤ (a-δ)/q := by
  rw [le_div_iff₀ hq]
  constructor <;> intro hh <;> nlinarith

omit [Fintype ι] in
theorem positiveDrive_nonneg (u : Weights ι) (i j : ι) :
    0 ≤ positiveDrive u i j := by
  classical
  unfold positiveDrive
  split_ifs
  · exact le_rfl
  · exact le_max_left _ _

theorem positiveDriveRow_nonneg (u : Weights ι) (i : ι) :
    0 ≤ positiveDriveRow u i := by
  exact Finset.sum_nonneg (fun j _ => positiveDrive_nonneg u i j)

omit [Fintype ι] in
theorem proposal_nonneg (h : ℝ) (B u : Weights ι) :
    ∀ i j, 0 ≤ proposal h B u i j := by
  classical
  intro i j
  unfold proposal
  split_ifs
  · exact le_rfl
  · exact le_max_left _ _

omit [Fintype ι] in
theorem proposal_zero_diag (h : ℝ) (B u : Weights ι) :
    ∀ i, proposal h B u i i = 0 := by
  classical
  intro i
  simp [proposal]

omit [Fintype ι] in
theorem proposal_apply_of_ne (h : ℝ) (B u : Weights ι) (i j : ι) (hij : i ≠ j) :
    proposal h B u i j = max 0 ((1-h)*B i j + h*u i j) := by
  classical
  simp only [proposal, if_neg hij]

omit [Fintype ι] in
theorem proposal_symmetric (h : ℝ) (B u : Weights ι)
    (hB : ∀ i j, B i j = B j i) (hu : ∀ i j, u i j = u j i) :
    ∀ i j, proposal h B u i j = proposal h B u j i := by
  classical
  intro i j
  by_cases hij : i = j
  · subst j; rfl
  · simp only [proposal, if_neg hij, if_neg (Ne.symm hij), hB i j, hu i j]

omit [Fintype ι] in
theorem proposal_eq_symmetrized (h : ℝ) (B u : Weights ι)
    (hB : ∀ i j, B i j = B j i) (hu : ∀ i j, u i j = u j i) (i j : ι) :
    proposal h B u i j = symmetrizedProposal h B u i j := by
  classical
  by_cases hij : i = j
  · simp only [proposal, symmetrizedProposal, if_pos hij]
  · simp only [proposal, symmetrizedProposal, if_neg hij]
    rw [hB j i, hu j i]
    ring

omit [Fintype ι] in
theorem proposal_entry_upper (h : ℝ) (B u : Weights ι)
    (hh0 : 0 ≤ h) (hh1 : h ≤ 1) (hB : ∀ i j, 0 ≤ B i j) (i j : ι) :
    proposal h B u i j ≤ (1-h)*B i j + h*positiveDrive u i j := by
  classical
  have hcoef : 0 ≤ 1-h := sub_nonneg.mpr hh1
  by_cases hij : i = j
  · simp only [proposal, positiveDrive, if_pos hij, mul_zero, add_zero]
    exact mul_nonneg hcoef (hB i j)
  · simp only [proposal, positiveDrive, if_neg hij]
    apply max_le
    · exact add_nonneg (mul_nonneg hcoef (hB i j))
        (mul_nonneg hh0 (le_max_left _ _))
    · exact add_le_add (le_refl _) (mul_le_mul_of_nonneg_left (le_max_right 0 (u i j)) hh0)

theorem proposal_row_upper (h : ℝ) (B u : Weights ι)
    (hh0 : 0 ≤ h) (hh1 : h ≤ 1) (hB : ∀ i j, 0 ≤ B i j) (i : ι) :
    rowSum (proposal h B u) i ≤ (1-h)*rowSum B i + h*positiveDriveRow u i := by
  unfold rowSum
  calc
    (∑ j, proposal h B u i j) ≤ ∑ j, ((1-h)*B i j + h*positiveDrive u i j) :=
      Finset.sum_le_sum (fun j _ => proposal_entry_upper h B u hh0 hh1 hB i j)
    _ = (1-h)*(∑ j, B i j) + h*positiveDriveRow u i := by
      simp only [positiveDriveRow, Finset.sum_add_distrib, Finset.mul_sum]

theorem proposal_row_upper_of_feasible (c h : ℝ) (B u : Weights ι)
    (hh0 : 0 ≤ h) (hh1 : h ≤ 1) (hB : ∀ i j, 0 ≤ B i j)
    (hf : feasible (fun _ => c) B) (i : ι) :
    rowSum (proposal h B u) i ≤ driveEnvelope c h (positiveDriveRow u i) := by
  exact (proposal_row_upper h B u hh0 hh1 hB i).trans
    (add_le_add (mul_le_mul_of_nonneg_left (hf i) (sub_nonneg.mpr hh1)) (le_refl _))

theorem appliedFactor_eq_min_appliedNodeScale (c : ι → ℝ) (ε : ℝ)
    (W : Weights ι) (i j : ι) :
    appliedFactor c ε W i j = min (appliedNodeScale c ε W i) (appliedNodeScale c ε W j) := by
  classical
  by_cases hf : feasible c W <;> simp [appliedFactor, appliedNodeScale, hf]

theorem appliedFactor_comm (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i j : ι) :
    appliedFactor c ε W i j = appliedFactor c ε W j i := by
  rw [appliedFactor_eq_min_appliedNodeScale, appliedFactor_eq_min_appliedNodeScale, min_comm]

theorem gate_eq_mul_appliedFactor (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i j : ι) :
    gate c ε W i j = W i j * appliedFactor c ε W i j := by
  classical
  by_cases hf : feasible c W <;> simp [gate, appliedFactor, kernel, hf]

theorem appliedNodeScale_nonneg (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) (i : ι) :
    0 ≤ appliedNodeScale c ε W i := by
  classical
  by_cases hf : feasible c W
  · simp [appliedNodeScale, hf]
  · simpa only [appliedNodeScale, if_neg hf] using nodeScale_nonneg c ε W hc hε hW i

theorem appliedNodeScale_le_one (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i : ι) :
    appliedNodeScale c ε W i ≤ 1 := by
  classical
  by_cases hf : feasible c W
  · simp [appliedNodeScale, hf]
  · simpa only [appliedNodeScale, if_neg hf] using nodeScale_le_one c ε W i

theorem appliedFactor_nonneg (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) (i j : ι) :
    0 ≤ appliedFactor c ε W i j := by
  rw [appliedFactor_eq_min_appliedNodeScale]
  exact le_min (appliedNodeScale_nonneg c ε W hc hε hW i)
    (appliedNodeScale_nonneg c ε W hc hε hW j)

theorem appliedFactor_le_one (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i j : ι) :
    appliedFactor c ε W i j ≤ 1 := by
  rw [appliedFactor_eq_min_appliedNodeScale]
  exact (min_le_left _ _).trans (appliedNodeScale_le_one c ε W i)

theorem appliedNodeScale_mul_row_le_capacity (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) (i : ι) :
    appliedNodeScale c ε W i * rowSum W i ≤ c i := by
  classical
  by_cases hf : feasible c W
  · simpa only [appliedNodeScale, if_pos hf, one_mul] using hf i
  · simp only [appliedNodeScale, if_neg hf]
    have hr : 0 ≤ rowSum W i := rowSum_nonneg W hW i
    have hd : 0 < rowSum W i + ε := add_pos_of_nonneg_of_pos hr hε
    calc
      nodeScale c ε W i * rowSum W i ≤ (c i/(rowSum W i+ε))*rowSum W i :=
        mul_le_mul_of_nonneg_right (min_le_right _ _) hr
      _ ≤ (c i/(rowSum W i+ε))*(rowSum W i+ε) :=
        mul_le_mul_of_nonneg_left (le_add_of_nonneg_right hε.le)
          (div_nonneg (hc i) hd.le)
      _ = c i := div_mul_cancel₀ _ hd.ne'

theorem appliedFactor_mul_row_le_capacity (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) (i j : ι) :
    appliedFactor c ε W i j * rowSum W i ≤ c i := by
  have hfactor : appliedFactor c ε W i j ≤ appliedNodeScale c ε W i := by
    rw [appliedFactor_eq_min_appliedNodeScale]; exact min_le_left _ _
  exact (mul_le_mul_of_nonneg_right hfactor (rowSum_nonneg W hW i)).trans
    (appliedNodeScale_mul_row_le_capacity c ε W hc hε hW i)

theorem appliedNodeScale_le_capacity_div_row (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j)
    (i : ι) (hr : 0 < rowSum W i) :
    appliedNodeScale c ε W i ≤ c i / rowSum W i := by
  exact (le_div_iff₀ hr).mpr (appliedNodeScale_mul_row_le_capacity c ε W hc hε hW i)

theorem appliedFactor_le_capacity_div_row (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j)
    (i j : ι) (hr : 0 < rowSum W i) :
    appliedFactor c ε W i j ≤ c i / rowSum W i := by
  exact (le_div_iff₀ hr).mpr (appliedFactor_mul_row_le_capacity c ε W hc hε hW i j)

theorem appliedFactor_ratio_upper (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j)
    (i j : ι) (hri : 0 < rowSum W i) (hrj : 0 < rowSum W j) :
    appliedFactor c ε W i j ≤ min 1 (min (c i / rowSum W i) (c j / rowSum W j)) := by
  apply le_min (appliedFactor_le_one c ε W i j)
  apply le_min (appliedFactor_le_capacity_div_row c ε W hc hε hW i j hri)
  rw [appliedFactor_comm c ε W i j]
  exact appliedFactor_le_capacity_div_row c ε W hc hε hW j i hrj

theorem scaleFloor_pos (c ε M : ℝ) (hc : 0 < c) (hε : 0 < ε) (hM : 0 ≤ M) :
    0 < scaleFloor c ε M := by
  exact lt_min zero_lt_one (div_pos hc (add_pos_of_nonneg_of_pos hM hε))

theorem scaleFloor_le_one (c ε M : ℝ) : scaleFloor c ε M ≤ 1 := min_le_left _ _

theorem appliedNodeScale_lower_of_row_upper (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j)
    (i : ι) (M : ℝ) (hM : rowSum W i ≤ M) :
    scaleFloor (c i) ε M ≤ appliedNodeScale c ε W i := by
  classical
  by_cases hf : feasible c W
  · simpa only [appliedNodeScale, if_pos hf] using scaleFloor_le_one (c i) ε M
  · simp only [appliedNodeScale, if_neg hf]
    have hrpos : 0 < rowSum W i+ε := add_pos_of_nonneg_of_pos (rowSum_nonneg W hW i) hε
    have hMpos : 0 < M+ε := lt_of_lt_of_le hrpos (add_le_add hM (le_refl ε))
    have hdiv : c i/(M+ε) ≤ c i/(rowSum W i+ε) :=
      (div_le_div_iff₀ hMpos hrpos).mpr
        (mul_le_mul_of_nonneg_left (add_le_add hM (le_refl ε)) (hc i))
    exact min_le_min (le_refl 1) hdiv

theorem appliedFactor_lower_of_row_uppers (c ε : ℝ) (W : Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j)
    (i j : ι) (Mi Mj : ℝ) (hi : rowSum W i ≤ Mi) (hj : rowSum W j ≤ Mj) :
    scaleFloor c ε (max Mi Mj) ≤ appliedFactor (fun _ => c) ε W i j := by
  rw [appliedFactor_eq_min_appliedNodeScale]
  exact le_min
    (appliedNodeScale_lower_of_row_upper (fun _ => c) ε W (fun _ => hc) hε hW i _
      (hi.trans (le_max_left _ _)))
    (appliedNodeScale_lower_of_row_upper (fun _ => c) ε W (fun _ => hc) hε hW j _
      (hj.trans (le_max_right _ _)))

theorem driveEnvelope_nonneg (c h S : ℝ) (hc : 0 ≤ c) (hh0 : 0 ≤ h)
    (hh1 : h ≤ 1) (hS : 0 ≤ S) : 0 ≤ driveEnvelope c h S := by
  exact add_nonneg (mul_nonneg (sub_nonneg.mpr hh1) hc) (mul_nonneg hh0 hS)

theorem edgeFloor_pos (c ε h Si Sj : ℝ) (hc : 0 < c) (hε : 0 < ε)
    (hh0 : 0 ≤ h) (hh1 : h ≤ 1) (hSi : 0 ≤ Si) :
    0 < edgeFloor c ε h Si Sj := by
  exact scaleFloor_pos c ε _ hc hε
    ((driveEnvelope_nonneg c h Si hc.le hh0 hh1 hSi).trans (le_max_left _ _))

theorem edgeFloor_le_one (c ε h Si Sj : ℝ) : edgeFloor c ε h Si Sj ≤ 1 :=
  scaleFloor_le_one _ _ _

theorem weightStep_nonneg (c ε h : ℝ) (B u : Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) : ∀ i j, 0 ≤ weightStep c ε h B u i j := by
  exact gate_nonneg (fun _ => c) ε (proposal h B u) (fun _ => hc) hε (proposal_nonneg h B u)

theorem weightStep_feasible (c ε h : ℝ) (B u : Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) : feasible (fun _ => c) (weightStep c ε h B u) := by
  exact gate_feasible (fun _ => c) ε (proposal h B u) (fun _ => hc) hε (proposal_nonneg h B u)

theorem weightStep_symmetric (c ε h : ℝ) (B u : Weights ι)
    (hB : ∀ i j, B i j = B j i) (hu : ∀ i j, u i j = u j i) :
    ∀ i j, weightStep c ε h B u i j = weightStep c ε h B u j i := by
  exact gate_symmetric (fun _ => c) ε (proposal h B u) (proposal_symmetric h B u hB hu)

theorem weightStep_zero_diag (c ε h : ℝ) (B u : Weights ι) :
    ∀ i, weightStep c ε h B u i i = 0 := by
  exact gate_zero_diag (fun _ => c) ε (proposal h B u) (proposal_zero_diag h B u)

theorem weightStep_scalar_recurrence (c ε h : ℝ) (B u : Weights ι)
    (i j : ι) (hij : i ≠ j) :
    weightStep c ε h B u i j = appliedFactor (fun _ => c) ε (proposal h B u) i j *
      max 0 ((1-h)*B i j+h*u i j) := by
  calc
    weightStep c ε h B u i j = proposal h B u i j *
      appliedFactor (fun _ => c) ε (proposal h B u) i j :=
      gate_eq_mul_appliedFactor (fun _ => c) ε (proposal h B u) i j
    _ = _ := by rw [proposal_apply_of_ne h B u i j hij, mul_comm]

theorem weightStep_factor_lower_of_drive_bounds (c ε h : ℝ) (B u : Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hh0 : 0 ≤ h) (hh1 : h ≤ 1)
    (hB : ∀ i j, 0 ≤ B i j) (hf : feasible (fun _ => c) B)
    (i j : ι) (Si Sj : ℝ) (hSi : positiveDriveRow u i ≤ Si)
    (hSj : positiveDriveRow u j ≤ Sj) :
    edgeFloor c ε h Si Sj ≤ appliedFactor (fun _ => c) ε (proposal h B u) i j := by
  apply appliedFactor_lower_of_row_uppers c ε (proposal h B u) hc hε
    (proposal_nonneg h B u) i j (driveEnvelope c h Si) (driveEnvelope c h Sj)
  · exact (proposal_row_upper_of_feasible c h B u hh0 hh1 hB hf i).trans
      (add_le_add (le_refl _) (mul_le_mul_of_nonneg_left hSi hh0))
  · exact (proposal_row_upper_of_feasible c h B u hh0 hh1 hB hf j).trans
      (add_le_add (le_refl _) (mul_le_mul_of_nonneg_left hSj hh0))

theorem trajectory_nonneg (c ε h : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hB0 : ∀ i j, 0 ≤ B 0 i j)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n)) :
    ∀ n i j, 0 ≤ B n i j := by
  intro n
  cases n with
  | zero => exact hB0
  | succ n => rw [hrec n]; exact weightStep_nonneg c ε h (B n) (u n) hc hε

theorem trajectory_feasible_from_first (c ε h : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n)) :
    ∀ n, feasible (fun _ => c) (B (n+1)) := by
  intro n
  rw [hrec n]
  exact weightStep_feasible c ε h (B n) (u n) hc hε

theorem trajectory_good_of_start (c ε h : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hB0 : ∀ i j, 0 ≤ B 0 i j)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n))
    (T : ℕ) (hstart : feasible (fun _ => c) (B 0) ∨ 1 ≤ T) :
    ∀ n, T ≤ n → (∀ i j, 0 ≤ B n i j) ∧ feasible (fun _ => c) (B n) := by
  intro n hn
  cases n with
  | zero =>
      rcases hstart with hf | hT
      · exact ⟨hB0, hf⟩
      · have hbad : (1 : ℕ) ≤ 0 := hT.trans hn
        simp at hbad
  | succ n =>
      rw [hrec n]
      exact ⟨weightStep_nonneg c ε h (B n) (u n) hc hε,
        weightStep_feasible c ε h (B n) (u n) hc hε⟩

theorem adaptive_edge_eventually_off (c ε h U Bc : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hh0 : 0 < h) (hh1 : h < 1)
    (i j : ι) (hij : i ≠ j) (hB0 : 0 ≤ B 0 i j)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n))
    (hu : ∀ n, u n i j ≤ U) (hU0 : 0 ≤ U) (hUc : U < Bc) :
    ∃ N, ∀ n ≥ N, B n i j < Bc := by
  exact AIEFFreeze.edge_eventually_off (fun n => B n i j) (fun n => u n i j)
    (fun n => appliedFactor (fun _ => c) ε (proposal h (B n) (u n)) i j)
    h U Bc hh0 hh1 hB0
    (fun n => appliedFactor_nonneg (fun _ => c) ε _ (fun _ => hc) hε
      (proposal_nonneg h (B n) (u n)) i j)
    (fun n => appliedFactor_le_one (fun _ => c) ε _ i j)
    (fun n => by rw [hrec n]; exact weightStep_scalar_recurrence c ε h (B n) (u n) i j hij)
    hu hU0 hUc

theorem adaptive_edge_eventually_on (c ε h Si Sj L Bc : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 < c) (hε : 0 < ε) (hh0 : 0 < h) (hh1 : h < 1)
    (hB0 : ∀ i j, 0 ≤ B 0 i j) (hf0 : feasible (fun _ => c) (B 0))
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n))
    (i j : ι) (hij : i ≠ j) (hSi : ∀ n, positiveDriveRow (u n) i ≤ Si)
    (hSj : ∀ n, positiveDriveRow (u n) j ≤ Sj)
    (hL : ∀ n, L ≤ u n i j) (hL0 : 0 ≤ L)
    (hgap : Bc < edgeFloor c ε h Si Sj * h * L /
      (1-edgeFloor c ε h Si Sj*(1-h))) :
    ∃ N, ∀ n ≥ N, B n i j > Bc := by
  have hS0 : 0 ≤ Si := (positiveDriveRow_nonneg (u 0) i).trans (hSi 0)
  have hk0 : 0 < edgeFloor c ε h Si Sj := edgeFloor_pos c ε h Si Sj hc hε hh0.le hh1.le hS0
  have hklam : ∀ n, edgeFloor c ε h Si Sj ≤
      appliedFactor (fun _ => c) ε (proposal h (B n) (u n)) i j := by
    intro n
    obtain ⟨hBn, hfn⟩ := trajectory_good_of_start c ε h B u hc.le hε hB0 hrec 0
      (Or.inl hf0) n (Nat.zero_le n)
    exact weightStep_factor_lower_of_drive_bounds c ε h (B n) (u n) hc.le hε
      hh0.le hh1.le hBn hfn i j Si Sj (hSi n) (hSj n)
  exact AIEFFreeze.edge_eventually_on (fun n => B n i j) (fun n => u n i j)
    (fun n => appliedFactor (fun _ => c) ε (proposal h (B n) (u n)) i j)
    h (edgeFloor c ε h Si Sj) L Bc hh0 hh1 hk0 (edgeFloor_le_one _ _ _ _ _) hklam
    (fun n => by rw [hrec n]; exact weightStep_scalar_recurrence c ε h (B n) (u n) i j hij)
    (hB0 i j) hL hL0 hgap

theorem adaptive_edge_eventually_on_from (c ε h Si Sj L Bc : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 < c) (hε : 0 < ε) (hh0 : 0 < h) (hh1 : h < 1)
    (hB0 : ∀ i j, 0 ≤ B 0 i j)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n))
    (T : ℕ) (hstart : feasible (fun _ => c) (B 0) ∨ 1 ≤ T)
    (i j : ι) (hij : i ≠ j) (hSi : ∀ n, positiveDriveRow (u (T+n)) i ≤ Si)
    (hSj : ∀ n, positiveDriveRow (u (T+n)) j ≤ Sj)
    (hL : ∀ n, L ≤ u (T+n) i j) (hL0 : 0 ≤ L)
    (hgap : Bc < edgeFloor c ε h Si Sj * h * L /
      (1-edgeFloor c ε h Si Sj*(1-h))) :
    ∃ N, ∀ n ≥ N, B (T+n) i j > Bc := by
  obtain ⟨hBT, hfT⟩ := trajectory_good_of_start c ε h B u hc.le hε hB0 hrec T hstart T le_rfl
  apply adaptive_edge_eventually_on c ε h Si Sj L Bc (fun n => B (T+n)) (fun n => u (T+n))
    hc hε hh0 hh1 hBT hfT
    (fun n => by simpa only [Nat.add_assoc] using hrec (T+n))
    i j hij hSi hSj hL hL0 hgap

theorem adaptive_edge_eventually_off_from (c ε h U Bc : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hh0 : 0 < h) (hh1 : h < 1)
    (hB0 : ∀ i j, 0 ≤ B 0 i j)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n))
    (T : ℕ) (i j : ι) (hij : i ≠ j)
    (hu : ∀ n, u (T+n) i j ≤ U) (hU0 : 0 ≤ U) (hUc : U < Bc) :
    ∃ N, ∀ n ≥ N, B (T+n) i j < Bc := by
  apply adaptive_edge_eventually_off c ε h U Bc (fun n => B (T+n)) (fun n => u (T+n))
    hc hε hh0 hh1 i j hij (trajectory_nonneg c ε h B u hc hε hB0 hrec T i j)
    (fun n => by simpa only [Nat.add_assoc] using hrec (T+n)) hu hU0 hUc

end Researcher040282

#print axioms Researcher040282.normalized_affine_identity
#print axioms Researcher040282.gap_capacity_iff
#print axioms Researcher040282.positiveDrive_nonneg
#print axioms Researcher040282.positiveDriveRow_nonneg
#print axioms Researcher040282.proposal_nonneg
#print axioms Researcher040282.proposal_zero_diag
#print axioms Researcher040282.proposal_apply_of_ne
#print axioms Researcher040282.proposal_symmetric
#print axioms Researcher040282.proposal_eq_symmetrized
#print axioms Researcher040282.proposal_entry_upper
#print axioms Researcher040282.proposal_row_upper
#print axioms Researcher040282.proposal_row_upper_of_feasible
#print axioms Researcher040282.appliedFactor_eq_min_appliedNodeScale
#print axioms Researcher040282.appliedFactor_comm
#print axioms Researcher040282.gate_eq_mul_appliedFactor
#print axioms Researcher040282.appliedNodeScale_nonneg
#print axioms Researcher040282.appliedNodeScale_le_one
#print axioms Researcher040282.appliedFactor_nonneg
#print axioms Researcher040282.appliedFactor_le_one
#print axioms Researcher040282.appliedNodeScale_mul_row_le_capacity
#print axioms Researcher040282.appliedFactor_mul_row_le_capacity
#print axioms Researcher040282.appliedNodeScale_le_capacity_div_row
#print axioms Researcher040282.appliedFactor_le_capacity_div_row
#print axioms Researcher040282.appliedFactor_ratio_upper
#print axioms Researcher040282.scaleFloor_pos
#print axioms Researcher040282.scaleFloor_le_one
#print axioms Researcher040282.appliedNodeScale_lower_of_row_upper
#print axioms Researcher040282.appliedFactor_lower_of_row_uppers
#print axioms Researcher040282.driveEnvelope_nonneg
#print axioms Researcher040282.edgeFloor_pos
#print axioms Researcher040282.edgeFloor_le_one
#print axioms Researcher040282.weightStep_nonneg
#print axioms Researcher040282.weightStep_feasible
#print axioms Researcher040282.weightStep_symmetric
#print axioms Researcher040282.weightStep_zero_diag
#print axioms Researcher040282.weightStep_scalar_recurrence
#print axioms Researcher040282.weightStep_factor_lower_of_drive_bounds
#print axioms Researcher040282.trajectory_nonneg
#print axioms Researcher040282.trajectory_feasible_from_first
#print axioms Researcher040282.trajectory_good_of_start
#print axioms Researcher040282.adaptive_edge_eventually_off
#print axioms Researcher040282.adaptive_edge_eventually_on
#print axioms Researcher040282.adaptive_edge_eventually_on_from
#print axioms Researcher040282.adaptive_edge_eventually_off_from
