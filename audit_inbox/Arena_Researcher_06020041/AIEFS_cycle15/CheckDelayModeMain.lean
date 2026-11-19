import AIEFGateCore.DelayModeMain
#print axioms AIEFGate.DelayModeMain.shift_chain
#print axioms AIEFGate.DelayModeMain.characteristic_of_nonzero_mode
#print axioms AIEFGate.DelayModeMain.common_mode_bound
#print axioms AIEFGate.DelayModeMain.transverse_mode_inside
#print axioms AIEFGate.DelayModeMain.step_mode_equations
#print axioms AIEFGate.DelayModeMain.common_step_eigenvalue_bound
#print axioms AIEFGate.DelayModeMain.transverse_step_eigenvalue_inside

-- A zero state satisfies the eigenrelation even for z=2; nonzero is essential.
example :
    (∀ k : ℕ, k ≤ 1 →
      AIEFGate.DelayModeMain.delayStep 1 ((1 / 2 : ℝ) : ℂ) (-((1 / 2 : ℝ) : ℂ))
        (fun _ : ℕ => (0 : ℂ)) k = (2 : ℂ) * (fun _ : ℕ => (0 : ℂ)) k) ∧
    ¬ ‖(2 : ℂ)‖ < 1 := by
  norm_num [AIEFGate.DelayModeMain.delayStep]

-- Nonvacuity: the constant nonzero vector is a common-mode eigenvector at z=1.
example (d : ℕ) : ∀ k : ℕ, k ≤ d →
    AIEFGate.DelayModeMain.delayStep d (1 / 2 : ℂ) (1 / 2 : ℂ)
      (fun _ : ℕ => (1 : ℂ)) k = (1 : ℂ) * (fun _ : ℕ => (1 : ℂ)) k := by
  intro k hk
  by_cases h0 : k = 0
  · norm_num [AIEFGate.DelayModeMain.delayStep, h0]
  · norm_num [AIEFGate.DelayModeMain.delayStep, h0]
