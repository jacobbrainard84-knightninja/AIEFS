/-
Researcher 040282: connect the actual reported-coherence expression to the prior
positive-drive row and gate-floor model. Exact-real component composition only.
A uniform range envelope does not prove sharp ON bands or coupled locking.
-/
import CoherenceEMA
import GateProposalBridge

set_option autoImplicit false
set_option linter.style.header false

namespace Researcher040282.EMA

variable {ι : Type*}

noncomputable def normalizedDrive (eta mu gamma : ℝ) (R : ι → ι → ℝ) (i j : ι) : ℝ :=
  ((eta+mu)*R i j-mu)/gamma

noncomputable def degreeDriveBound (ι : Type*) [Fintype ι] (eta gamma : ℝ) : ℝ :=
  ((Fintype.card ι - 1 : ℕ) : ℝ) * (eta/gamma)

theorem reportedDrive_bounds (eta mu gamma : ℝ) (C : ComplexWeights ι)
    (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (hgamma : 0 < gamma)
    (hC : ∀ i j, ‖C i j‖ ≤ 1) (i j : ι) :
    -mu/gamma ≤ normalizedDrive eta mu gamma (reportedR C) i j ∧
      normalizedDrive eta mu gamma (reportedR C) i j ≤ eta/gamma := by
  have hR0 := reportedR_nonneg C i j
  have hR1 := reportedR_le_one C hC i j
  dsimp only [normalizedDrive]
  constructor
  · apply (div_le_div_iff_of_pos_right hgamma).2
    nlinarith [mul_nonneg (add_nonneg heta hmu) hR0]
  · apply (div_le_div_iff_of_pos_right hgamma).2
    nlinarith [mul_le_mul_of_nonneg_left hR1 (add_nonneg heta hmu)]

theorem reportedDrive_symmetric (eta mu gamma : ℝ) (C : ComplexWeights ι) (i j : ι) :
    normalizedDrive eta mu gamma (reportedR C) i j =
      normalizedDrive eta mu gamma (reportedR C) j i := by
  unfold normalizedDrive
  rw [reportedR_symmetric C i j]

theorem reportedDrive_diag (eta mu gamma : ℝ) (C : ComplexWeights ι) (i : ι) :
    normalizedDrive eta mu gamma (reportedR C) i i = -mu/gamma := by
  simp [normalizedDrive, reportedR]

section Finite

variable [Fintype ι]

theorem reportedDrive_positiveRow_bound (eta mu gamma : ℝ) (C : ComplexWeights ι)
    (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (hgamma : 0 < gamma)
    (hC : ∀ i j, ‖C i j‖ ≤ 1) (i : ι) :
    positiveDriveRow (normalizedDrive eta mu gamma (reportedR C)) i ≤
      degreeDriveBound ι eta gamma := by
  classical
  let u := normalizedDrive eta mu gamma (reportedR C)
  have he : (∑ j ∈ (Finset.univ : Finset ι).erase i, positiveDrive u i j) =
      positiveDriveRow u i := Finset.sum_erase _ (by simp [positiveDrive])
  change positiveDriveRow u i ≤ _
  rw [← he]
  calc
    (∑ j ∈ (Finset.univ : Finset ι).erase i, positiveDrive u i j) ≤
        ∑ j ∈ (Finset.univ : Finset ι).erase i, eta/gamma := by
      apply Finset.sum_le_sum
      intro j hj
      have hji : j ≠ i := (Finset.mem_erase.mp hj).1
      simp only [positiveDrive, if_neg (Ne.symm hji)]
      exact max_le (div_nonneg heta hgamma.le)
        (reportedDrive_bounds eta mu gamma C heta hmu hgamma hC i j).2
    _ = degreeDriveBound ι eta gamma := by
      simp only [Finset.sum_const, Finset.card_erase_of_mem (Finset.mem_univ i),
        Finset.card_univ, nsmul_eq_mul, degreeDriveBound]

theorem phaseUpdatedDrive_positiveRow_bound (alpha eta mu gamma : ℝ)
    (C : ComplexWeights ι) (theta delayed omega : ι → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C i j‖ ≤ 1)
    (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (hgamma : 0 < gamma) (i : ι) :
    positiveDriveRow (normalizedDrive eta mu gamma
      (reportedR (coherenceUpdate alpha C theta delayed omega tau))) i ≤
        degreeDriveBound ι eta gamma :=
  reportedDrive_positiveRow_bound eta mu gamma _ heta hmu hgamma
    (coherenceUpdate_unitDisk alpha C theta delayed omega tau ha0 ha1 hC) i

theorem phaseUpdated_gate_floor (alpha eta mu gamma c eps h : ℝ)
    (C : ComplexWeights ι) (theta delayed omega : ι → ℝ) (tau : ℝ)
    (B : Weights ι) (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1)
    (hC : ∀ i j, ‖C i j‖ ≤ 1)
    (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (hgamma : 0 < gamma)
    (hc : 0 ≤ c) (heps : 0 < eps) (hh0 : 0 ≤ h) (hh1 : h ≤ 1)
    (hB : ∀ i j, 0 ≤ B i j) (hfeas : feasible (fun _ => c) B) (i j : ι) :
    edgeFloor c eps h (degreeDriveBound ι eta gamma) (degreeDriveBound ι eta gamma) ≤
      appliedFactor (fun _ => c) eps (proposal h B (normalizedDrive eta mu gamma
        (reportedR (coherenceUpdate alpha C theta delayed omega tau)))) i j := by
  apply weightStep_factor_lower_of_drive_bounds c eps h B _ hc heps hh0 hh1 hB hfeas
    i j (degreeDriveBound ι eta gamma) (degreeDriveBound ι eta gamma)
  · exact phaseUpdatedDrive_positiveRow_bound alpha eta mu gamma C theta delayed omega tau
      ha0 ha1 hC heta hmu hgamma i
  · exact phaseUpdatedDrive_positiveRow_bound alpha eta mu gamma C theta delayed omega tau
      ha0 ha1 hC heta hmu hgamma j

end Finite
end Researcher040282.EMA

-- Closed-file audit queries.
#print axioms Researcher040282.EMA.reportedDrive_bounds
#print axioms Researcher040282.EMA.reportedDrive_symmetric
#print axioms Researcher040282.EMA.reportedDrive_diag
#print axioms Researcher040282.EMA.reportedDrive_positiveRow_bound
#print axioms Researcher040282.EMA.phaseUpdatedDrive_positiveRow_bound
#print axioms Researcher040282.EMA.phaseUpdated_gate_floor
