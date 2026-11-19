/- SPDX-License-Identifier: Apache-2.0
Research candidate: finite delayed shift eigenmodes and characteristic roots. -/
import AIEFGateCore.DelayRoots

set_option autoImplicit false
namespace AIEFGate.DelayModeMain

/-- A length-d shift chain relates its head and last entry. -/
theorem shift_chain (d : ℕ) (z : ℂ) (v : ℕ → ℂ)
    (hshift : ∀ k, k < d → v k = z * v (k + 1)) :
    v 0 = z ^ d * v d := by
  induction d generalizing v with
  | zero => simp
  | succ d ih =>
      have hs : ∀ k, k < d → (fun n => v (n + 1)) k =
          z * (fun n => v (n + 1)) (k + 1) := by
        intro k hk
        simpa [Nat.add_assoc] using hshift (k + 1) (by omega)
      have hv := ih (fun n => v (n + 1)) hs
      simp only [zero_add] at hv
      rw [hshift 0 (by omega), hv, pow_succ]
      ring

/-- Every nonzero eigenmode of a finite delayed shift and feedback equation satisfies
its characteristic equation. The state uses indices 0 through d; indices above d
are irrelevant. -/
theorem characteristic_of_nonzero_mode (d : ℕ) (z a b : ℂ) (v : ℕ → ℂ)
    (hshift : ∀ k, k < d → v k = z * v (k + 1))
    (hfeedback : z * v 0 = a * v 0 + b * v d)
    (hnonzero : ∃ k, k ≤ d ∧ v k ≠ 0) :
    z ^ (d + 1) = a * z ^ d + b := by
  have hlast : v d ≠ 0 := by
    obtain ⟨k, hk, hkn⟩ := hnonzero
    intro hz
    apply hkn
    have hs : ∀ t, t < d - k → (fun n => v (k + n)) t =
        z * (fun n => v (k + n)) (t + 1) := by
      intro t ht
      simpa [Nat.add_assoc] using hshift (k + t) (by omega)
    have hc := shift_chain (d - k) z (fun n => v (k + n)) hs
    simp only [add_zero] at hc
    have heq : k + (d - k) = d := by omega
    rw [heq, hz, mul_zero] at hc
    exact hc
  have hhead := shift_chain d z v hshift
  have hp : (z ^ (d + 1) - a * z ^ d - b) * v d = 0 := by
    calc
      _ = z * (z ^ d * v d) - (a * (z ^ d * v d) + b * v d) := by
        rw [pow_succ]
        ring
      _ = 0 := by rw [← hhead]; exact sub_eq_zero.mpr hfeedback
  have hzero := (mul_eq_zero.mp hp).resolve_right hlast
  linear_combination hzero

/-- A nonzero common-mode shift eigenvector has an eigenvalue in the closed disk;
only 1 can lie on the unit circle. -/
theorem common_mode_bound (d : ℕ) (z : ℂ) (h : ℝ) (v : ℕ → ℂ)
    (hh : 0 < h) (hh1 : h < 1)
    (hshift : ∀ k, k < d → v k = z * v (k + 1))
    (hfeedback : z * v 0 = ((1 - h : ℝ) : ℂ) * v 0 + (h : ℂ) * v d)
    (hnonzero : ∃ k, k ≤ d ∧ v k ≠ 0) :
    ‖z‖ ≤ 1 ∧ (‖z‖ = 1 → z = 1) := by
  have hc := characteristic_of_nonzero_mode d z ((1 - h : ℝ) : ℂ) (h : ℂ) v
    hshift hfeedback hnonzero
  have hp : z ^ (d + 1) - ((1 - h : ℝ) : ℂ) * z ^ d - (h : ℂ) = 0 := by
    linear_combination hc
  rcases DelayRoots.symRoot_eq_one_or_lt h hh hh1 d z hp with heq | hlt
  · subst z
    simp
  · exact ⟨le_of_lt hlt, fun heq => by linarith⟩

/-- A nonzero transverse-mode eigenvector has eigenvalue strictly inside the disk,
including the N=2 boundary case. `m` is the number of neighbours. -/
theorem transverse_mode_inside (d m : ℕ) (z : ℂ) (h : ℝ) (v : ℕ → ℂ)
    (hm : 1 ≤ m) (hh : 0 < h) (hmh : (m : ℝ) * h < 1)
    (hshift : ∀ k, k < d → v k = z * v (k + 1))
    (hfeedback : z * v 0 = ((1 - (m : ℝ) * h : ℝ) : ℂ) * v 0 - (h : ℂ) * v d)
    (hnonzero : ∃ k, k ≤ d ∧ v k ≠ 0) : ‖z‖ < 1 := by
  have hf : z * v 0 = ((1 - (m : ℝ) * h : ℝ) : ℂ) * v 0 + (-(h : ℂ)) * v d := by
    simpa [sub_eq_add_neg] using hfeedback
  have hc := characteristic_of_nonzero_mode d z ((1 - (m : ℝ) * h : ℝ) : ℂ)
    (-(h : ℂ)) v hshift hf hnonzero
  have hc' : z ^ (d + 1) = ((1 - (m : ℝ) * h : ℝ) : ℂ) * z ^ d - (h : ℂ) := by
    simpa [sub_eq_add_neg] using hc
  have hp : z ^ (d + 1) - ((1 - (m : ℝ) * h : ℝ) : ℂ) * z ^ d + (h : ℂ) = 0 := by
    linear_combination hc'
  exact DelayRoots.transRoot_lt_one m hm h hh hmh d z hp

/-- A scalar delayed feedback step. Only the entries 0 through d form the
state; values at indices above d are irrelevant to the theorems below. -/
def delayStep (d : ℕ) (a b : ℂ) (v : ℕ → ℂ) (k : ℕ) : ℂ :=
  if k = 0 then a * v 0 + b * v d else v (k - 1)

/-- A pointwise eigenrelation of the explicit shift map implies the mode equations. -/
theorem step_mode_equations (d : ℕ) (z a b : ℂ) (v : ℕ → ℂ)
    (heigen : ∀ k, k ≤ d → delayStep d a b v k = z * v k) :
    (∀ k, k < d → v k = z * v (k + 1)) ∧
      z * v 0 = a * v 0 + b * v d := by
  constructor
  · intro k hk
    have he := heigen (k + 1) (by omega)
    simpa [delayStep] using he
  · have he := heigen 0 (by omega)
    simpa [delayStep] using he.symm

/-- Eigenvalues of the explicit common delayed shift map lie in the closed unit
 disk, with 1 the only possible unit-circle eigenvalue. -/
theorem common_step_eigenvalue_bound (d : ℕ) (z : ℂ) (h : ℝ) (v : ℕ → ℂ)
    (hh : 0 < h) (hh1 : h < 1)
    (heigen : ∀ k, k ≤ d →
      delayStep d ((1 - h : ℝ) : ℂ) (h : ℂ) v k = z * v k)
    (hnonzero : ∃ k, k ≤ d ∧ v k ≠ 0) :
    ‖z‖ ≤ 1 ∧ (‖z‖ = 1 → z = 1) := by
  obtain ⟨hs, hf⟩ := step_mode_equations d z ((1 - h : ℝ) : ℂ) (h : ℂ) v heigen
  exact common_mode_bound d z h v hh hh1 hs hf hnonzero

/-- Eigenvalues of the explicit transverse delayed shift map lie strictly inside
 the unit disk for every m ≥ 1, including the two-node case. -/
theorem transverse_step_eigenvalue_inside (d m : ℕ) (z : ℂ) (h : ℝ) (v : ℕ → ℂ)
    (hm : 1 ≤ m) (hh : 0 < h) (hmh : (m : ℝ) * h < 1)
    (heigen : ∀ k, k ≤ d →
      delayStep d ((1 - (m : ℝ) * h : ℝ) : ℂ) (-(h : ℂ)) v k = z * v k)
    (hnonzero : ∃ k, k ≤ d ∧ v k ≠ 0) : ‖z‖ < 1 := by
  obtain ⟨hs, hf⟩ := step_mode_equations d z ((1 - (m : ℝ) * h : ℝ) : ℂ)
    (-(h : ℂ)) v heigen
  have hf' : z * v 0 = ((1 - (m : ℝ) * h : ℝ) : ℂ) * v 0 - (h : ℂ) * v d := by
    simpa [sub_eq_add_neg] using hf
  exact transverse_mode_inside d m z h v hm hh hmh hs hf' hnonzero

end AIEFGate.DelayModeMain
