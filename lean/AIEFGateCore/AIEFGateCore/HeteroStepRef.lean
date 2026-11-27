/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.EngineStepRef

/-!
# Heterogeneous fixed-B phase step and its window invariant (Arena D17)

Research candidate. A fixed (unclipped) matrix `B` in the phase head, equal to the scalar
`EngineStepRef.phaseStep` for a common off-diagonal weight, its derivative `linearStep` at Ω = 0,
and an all-time window max-norm invariant when `dt ≥ 0`, `B ≥ 0` and `dt·row_i(B) ≤ 1` for every
row (uniform case `c ≤ 1/(N-1)`), for ALL perturbations; a failing row has an explicit growth
witness. Fixed B: no modulo, shuffle, B dynamics or gate. Complementary to `WindowMax`, see SPEC
§17. Value probes and `false_*` witnesses appended.

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D17, deposit sha256 `9d16831a…`; proofs and
statements unchanged from the deposit.
-/

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.HeteroStepRef
open AIEFGate.EngineStepRef
noncomputable section

/-- Mirrors the fixed-B unwrapped phase coupling in engine lines 830–839.
    Excludes modulo, shuffle, B dynamics and the gate; B is not clipped here. -/
def phaseHeadW (n d : ℕ) (dt omega : ℝ) (B : Fin n → Fin n → ℝ)
    (x : ℕ → Fin n → ℝ) (i : Fin n) : ℝ :=
  x 0 i + dt * (omega + ∑ j ∈ Finset.univ.erase i,
    B i j * Real.sin (x d j - x 0 i))

def phaseStepW (n d : ℕ) (dt omega : ℝ) (B : Fin n → Fin n → ℝ)
    (x : ℕ → Fin n → ℝ) (k : ℕ) (i : Fin n) : ℝ :=
  if k = 0 then phaseHeadW n d dt omega B x i else x (k - 1) i

/-- The new step exactly recovers main's scalar step for common off-diagonal B. -/
theorem agrees_main (n d : ℕ) (dt omega b : ℝ) (B : Fin n → Fin n → ℝ)
    (hB : ∀ i j, i ≠ j → B i j = clippedWeight b)
    (x : ℕ → Fin n → ℝ) (k : ℕ) (i : Fin n) :
    phaseStepW n d dt omega B x k i = phaseStep n d dt omega b x k i := by
  by_cases hk : k = 0
  · simp only [phaseStepW, phaseStep, hk, if_true, phaseHeadW, phaseHead]
    have hs : (∑ j ∈ Finset.univ.erase i, B i j * Real.sin (x d j - x 0 i)) =
        ∑ j ∈ Finset.univ.erase i, clippedWeight b * Real.sin (x d j - x 0 i) := by
      apply Finset.sum_congr rfl
      intro j hj
      rw [hB i j (Ne.symm (Finset.ne_of_mem_erase hj))]
    rw [hs]
  · simp [phaseStepW, phaseStep, hk]

def row (n : ℕ) (B : Fin n → Fin n → ℝ) (i : Fin n) : ℝ :=
  ∑ j : Fin n, B i j

def linearStep (n d : ℕ) (dt : ℝ) (B : Fin n → Fin n → ℝ)
    (v : ℕ → Fin n → ℝ) (k : ℕ) (i : Fin n) : ℝ :=
  if k = 0 then (1 - dt * row n B i) * v 0 i + dt * ∑ j, B i j * v d j
  else v (k - 1) i

def iterate (n d : ℕ) (dt : ℝ) (B : Fin n → Fin n → ℝ)
    (v : ℕ → Fin n → ℝ) : ℕ → (ℕ → Fin n → ℝ)
  | 0 => v
  | t + 1 => linearStep n d dt B (iterate n d dt B v t)

/-- Weighted head derivative at the prepared rotating orbit. -/
theorem weighted_head_derivative (n d : ℕ) (dt omega Omega theta : ℝ)
    (B : Fin n → Fin n → ℝ) (hdiag : ∀ i, B i i = 0)
    (v : ℕ → Fin n → ℝ) (i : Fin n) :
    HasDerivAt (fun t => phaseHeadW n d dt omega B (orbitPath n dt Omega theta v t) i)
      ((1 - dt * row n B i * Real.cos ((d : ℝ) * dt * Omega)) * v 0 i +
        dt * Real.cos ((d : ℝ) * dt * Omega) * ∑ j, B i j * v d j) 0 := by
  have hs : HasDerivAt (fun t => ∑ j ∈ Finset.univ.erase i,
      B i j * Real.sin (orbitPath n dt Omega theta v t d j -
        orbitPath n dt Omega theta v t 0 i))
      (∑ j ∈ Finset.univ.erase i,
        B i j * (Real.cos ((d : ℝ) * dt * Omega) * (v d j - v 0 i))) 0 := by
    apply HasDerivAt.fun_sum
    intro j hj
    exact (neighbor_derivative n d dt Omega theta v i j).const_mul (B i j)
  have hc : HasDerivAt (fun t : ℝ => orbitPath n dt Omega theta v t 0 i) (v 0 i) 0 := by
    have hh := (hasDerivAt_const (0 : ℝ) theta).fun_add
      ((hasDerivAt_id (0 : ℝ)).mul_const (v 0 i))
    simpa [orbitPath] using hh
  have hp := hc.fun_add ((hasDerivAt_const (0 : ℝ) omega).fun_add hs |>.const_mul dt)
  apply (show HasDerivAt (fun t => phaseHeadW n d dt omega B
      (orbitPath n dt Omega theta v t) i) _ 0 by simpa [phaseHeadW] using hp).congr_deriv
  simp only [hdiag, zero_mul, sub_zero, row, mul_sub, Finset.sum_sub_distrib]
  have hfact (f : Fin n → ℝ) :
      (∑ j, B i j * (Real.cos ((d : ℝ) * dt * Omega) * f j)) =
        Real.cos ((d : ℝ) * dt * Omega) * ∑ j, B i j * f j := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro j hj
    ring
  rw [hfact (fun j => v d j), hfact (fun _ => v 0 i), ← Finset.sum_mul]
  ring

/-- Full step derivative at Ω=0; retained slots use main's history derivative. -/
theorem weighted_step_derivative (n d : ℕ) (dt omega theta : ℝ)
    (B : Fin n → Fin n → ℝ) (hdiag : ∀ i, B i i = 0)
    (v : ℕ → Fin n → ℝ) (k : ℕ) (i : Fin n) :
    HasDerivAt (fun t => phaseStepW n d dt omega B (orbitPath n dt 0 theta v t) k i)
      (linearStep n d dt B v k i) 0 := by
  by_cases hk : k = 0
  · subst k
    simpa [phaseStepW, linearStep] using weighted_head_derivative n d dt omega 0 theta B hdiag v i
  · have hh := history_derivative n d k dt omega 0 0 theta (Nat.pos_of_ne_zero hk) v i
    simpa [phaseStepW, phaseStep, linearStep, hk] using hh

/-- One step is a convex combination of current and delayed components. -/
theorem window_step (n d : ℕ) (dt M : ℝ) (B : Fin n → Fin n → ℝ)
    (v : ℕ → Fin n → ℝ) (hdt : 0 ≤ dt) (hB : ∀ i j, 0 ≤ B i j)
    (hrow : ∀ i, dt * row n B i ≤ 1) (_hM : 0 ≤ M)
    (hv : ∀ k, k ≤ d → ∀ i, |v k i| ≤ M) :
    ∀ k, k ≤ d → ∀ i, |linearStep n d dt B v k i| ≤ M := by
  intro k hk i
  by_cases hz : k = 0
  · subst k
    have ha : 0 ≤ 1 - dt * row n B i := sub_nonneg.mpr (hrow i)
    have hs : |∑ j, B i j * v d j| ≤ row n B i * M := by
      calc
        |∑ j, B i j * v d j| ≤ ∑ j, |B i j * v d j| := Finset.abs_sum_le_sum_abs _ _
        _ ≤ ∑ j, B i j * M := by
          apply Finset.sum_le_sum
          intro j hj
          rw [abs_mul, abs_of_nonneg (hB i j)]
          exact mul_le_mul_of_nonneg_left (hv d (le_refl d) j) (hB i j)
        _ = row n B i * M := by simp [row, Finset.sum_mul]
    simp only [linearStep, if_true]
    calc
      |(1 - dt * row n B i) * v 0 i + dt * ∑ j, B i j * v d j| ≤
          (1 - dt * row n B i) * |v 0 i| + dt * |∑ j, B i j * v d j| := by
            simpa [abs_mul, abs_of_nonneg ha, abs_of_nonneg hdt] using
              (abs_add_le ((1 - dt * row n B i) * v 0 i) (dt * ∑ j, B i j * v d j))
      _ ≤ (1 - dt * row n B i) * M + dt * (row n B i * M) := by
        exact add_le_add (mul_le_mul_of_nonneg_left (hv 0 (Nat.zero_le d) i) ha)
          (mul_le_mul_of_nonneg_left hs hdt)
      _ = M := by ring
  · simpa [linearStep, hz] using hv (k - 1) (le_trans (Nat.sub_le k 1) hk) i

theorem window_all_steps (n d : ℕ) (dt M : ℝ) (B : Fin n → Fin n → ℝ)
    (v : ℕ → Fin n → ℝ) (hdt : 0 ≤ dt) (hB : ∀ i j, 0 ≤ B i j)
    (hrow : ∀ i, dt * row n B i ≤ 1) (hM : 0 ≤ M)
    (hv : ∀ k, k ≤ d → ∀ i, |v k i| ≤ M) :
    ∀ t k, k ≤ d → ∀ i, |iterate n d dt B v t k i| ≤ M := by
  intro t
  induction t with
  | zero => simpa [iterate] using hv
  | succ t ih => exact window_step n d dt M B (iterate n d dt B v t) hdt hB hrow hM ih

/-- Guard algebra; valid for both gate branches on non-raising exact-real steps. -/
theorem guard_row_bound (a q delta tol r : ℝ) (hq : 0 < q)
    (hguard : delta - tol ≤ a - q * r) : r ≤ (a - delta + tol) / q := by
  apply (le_div_iff₀ hq).2
  nlinarith

/-- For d≥1, a failing row has an exact head growth witness. -/
theorem growth_witness (n d : ℕ) (dt : ℝ) (B : Fin n → Fin n → ℝ)
    (i : Fin n) (hd : 0 < d) (hr : 1 < dt * row n B i) :
    let v : ℕ → Fin n → ℝ := fun k _ => if k = 0 then 1 else -1
    (∀ k, k ≤ d → ∀ j, |v k j| ≤ 1) ∧
    |linearStep n d dt B v 0 i| = 2 * dt * row n B i - 1 ∧
    1 < |linearStep n d dt B v 0 i| := by
  dsimp
  have hd' : d ≠ 0 := Nat.ne_of_gt hd
  simp only [linearStep, if_true, if_neg hd']
  have hs : (∑ j : Fin n, B i j * (-1 : ℝ)) = -row n B i := by
    simp [row, Finset.sum_neg_distrib]
  rw [hs]
  have he : (1 - dt * row n B i) * 1 + dt * (-row n B i) = 1 - 2 * dt * row n B i := by ring
  rw [he, abs_of_neg (by nlinarith : 1 - 2 * dt * row n B i < 0)]
  constructor
  · intro k hk j
    by_cases hk0 : k = 0 <;> simp [hk0]
  constructor <;> nlinarith

#print axioms agrees_main
#print axioms weighted_head_derivative
#print axioms weighted_step_derivative
#print axioms window_step
#print axioms window_all_steps
#print axioms guard_row_bound
#print axioms growth_witness

/-! ### Value probes and negations used by the mutation harness (SPEC §17)

The probes evaluate `phaseHeadW`, `linearStep` and `row` at closed numbers straight from their
definitions. Each `false_*` theorem refutes a weakened `window_step`. -/

/-- `linearStep` with `n = 1`, `d = 1`, `dt = 1/2`, `B = 1`, window `(1, 3)`: head
`(1 - 1/2)·1 + (1/2)·3 = 2`, slot 1 copies slot 0. `1 + dt·row` gives `3`, reading slot 0 in the sum
gives `1`, a row sum without the diagonal gives `5/2`, an unshifted slot 1 gives `3`. -/
theorem probe_linearStep_values :
    linearStep 1 1 (1/2) (fun _ _ => 1) (fun k _ => if k = 0 then 1 else 3) 0 0 = 2 ∧
      linearStep 1 1 (1/2) (fun _ _ => 1) (fun k _ => if k = 0 then 1 else 3) 1 0 = 1 := by
  constructor <;> norm_num [linearStep, row]

/-- Head with `dt = 2`, `ω = 1/4`, `B = 1/2` on `EngineStepRef.probeHist`: one delayed neighbour,
so `2·(1/4 + 1/2) = 3/2`. Reading the current slot of the neighbour gives `1/2`. -/
theorem probe_phaseHeadW_value :
    phaseHeadW 2 1 2 (1/4) (fun _ _ => 1/2) probeHist 0 = 3/2 := by
  have he : (Finset.univ.erase (0 : Fin 2)) = {1} := by decide
  simp only [phaseHeadW, he, Finset.sum_singleton, probeHist]
  norm_num

/-- Dropping the row condition from `window_step` is false (`n = 1`, `B = 2`, `dt = 1`: head
`-3`). -/
theorem false_window_step_no_row :
    ¬ (∀ (n d : ℕ) (dt M : ℝ) (B : Fin n → Fin n → ℝ) (v : ℕ → Fin n → ℝ) (_hdt : 0 ≤ dt)
      (_hB : ∀ i j, 0 ≤ B i j) (_hrow : True) (_hM : 0 ≤ M)
      (_hv : ∀ k, k ≤ d → ∀ i, |v k i| ≤ M),
      ∀ k, k ≤ d → ∀ i, |linearStep n d dt B v k i| ≤ M) := by
  intro H
  have h := H 1 1 1 1 (fun _ _ => 2) (fun k _ => if k = 0 then 1 else -1) (by norm_num)
    (fun _ _ => by norm_num) trivial (by norm_num)
    (fun k _ _ => by by_cases hk : k = 0 <;> simp [hk]) 0 (by norm_num) 0
  norm_num [linearStep, row, abs_le] at h

/-- Dropping `0 ≤ B` from `window_step` is false (`n = 2`, `B = [[1,-1],[-1,1]]`, row sums `0`). -/
theorem false_window_step_no_nonneg :
    ¬ (∀ (n d : ℕ) (dt M : ℝ) (B : Fin n → Fin n → ℝ) (v : ℕ → Fin n → ℝ) (_hdt : 0 ≤ dt)
      (_hB : True) (_hrow : ∀ i, dt * row n B i ≤ 1) (_hM : 0 ≤ M)
      (_hv : ∀ k, k ≤ d → ∀ i, |v k i| ≤ M),
      ∀ k, k ≤ d → ∀ i, |linearStep n d dt B v k i| ≤ M) := by
  intro H
  have h := H 2 1 1 1 (fun i j => if i = j then 1 else -1)
    (fun k i => if k = 0 then 1 else if i = 0 then 1 else -1) (by norm_num) trivial
    (fun i => by fin_cases i <;> simp [row, Fin.sum_univ_two]) (by norm_num)
    (fun k _ i => by by_cases hk : k = 0 <;> by_cases hi : i = 0 <;> simp [hk, hi])
    0 (by norm_num) 0
  norm_num [linearStep, row, Fin.sum_univ_two, abs_le] at h

/-- Dropping `0 ≤ dt` from `window_step` is false (`n = 1`, `B = 1`, `dt = -1`: head `3`). -/
theorem false_window_step_no_dt :
    ¬ (∀ (n d : ℕ) (dt M : ℝ) (B : Fin n → Fin n → ℝ) (v : ℕ → Fin n → ℝ) (_hdt : True)
      (_hB : ∀ i j, 0 ≤ B i j) (_hrow : ∀ i, dt * row n B i ≤ 1) (_hM : 0 ≤ M)
      (_hv : ∀ k, k ≤ d → ∀ i, |v k i| ≤ M),
      ∀ k, k ≤ d → ∀ i, |linearStep n d dt B v k i| ≤ M) := by
  intro H
  have h := H 1 1 (-1) 1 (fun _ _ => 1) (fun k _ => if k = 0 then 1 else -1) trivial
    (fun _ _ => by norm_num) (fun _ => by norm_num [row]) (by norm_num)
    (fun k _ _ => by by_cases hk : k = 0 <;> simp [hk]) 0 (by norm_num) 0
  norm_num [linearStep, row, abs_le] at h

/-- Dropping the row condition from `window_all_steps` is false (`n = 1`, `B = 2`, `dt = 1`,
`t = 1`: head `-3`). Audit note N5. -/
theorem false_window_all_no_row :
    ¬ (∀ (n d : ℕ) (dt M : ℝ) (B : Fin n → Fin n → ℝ) (v : ℕ → Fin n → ℝ) (_hdt : 0 ≤ dt)
      (_hB : ∀ i j, 0 ≤ B i j) (_hrow : True) (_hM : 0 ≤ M)
      (_hv : ∀ k, k ≤ d → ∀ i, |v k i| ≤ M),
      ∀ t k, k ≤ d → ∀ i, |iterate n d dt B v t k i| ≤ M) := by
  intro H
  have h := H 1 1 1 1 (fun _ _ => 2) (fun k _ => if k = 0 then 1 else -1) (by norm_num)
    (fun _ _ => by norm_num) trivial (by norm_num)
    (fun k _ _ => by by_cases hk : k = 0 <;> simp [hk]) 1 0 (by norm_num) 0
  norm_num [iterate, linearStep, row, abs_le] at h

#print axioms false_window_all_no_row
#print axioms probe_linearStep_values
#print axioms probe_phaseHeadW_value
#print axioms false_window_step_no_row
#print axioms false_window_step_no_nonneg
#print axioms false_window_step_no_dt

end
end AIEFGate.HeteroStepRef
