import AIEFGateCore.DelayModeBridge
#print axioms AIEFGate.DelayModeBridge.shift_chain
#print axioms AIEFGate.DelayModeBridge.characteristic_of_nonzero_mode
#print axioms AIEFGate.DelayModeBridge.common_mode_bound
#print axioms AIEFGate.DelayModeBridge.transverse_mode_inside
#print axioms AIEFGate.DelayModeBridge.step_mode_equations
#print axioms AIEFGate.DelayModeBridge.common_step_eigenvalue_bound
#print axioms AIEFGate.DelayModeBridge.transverse_step_eigenvalue_inside

-- A zero state satisfies the eigenrelation even for z=2; nonzero is essential.
example :
    (∀ k : ℕ, k ≤ 1 →
      AIEFGate.DelayModeBridge.delayStep 1 ((1 / 2 : ℝ) : ℂ) (-((1 / 2 : ℝ) : ℂ))
        (fun _ : ℕ => (0 : ℂ)) k = (2 : ℂ) * (fun _ : ℕ => (0 : ℂ)) k) ∧
    ¬ ‖(2 : ℂ)‖ < 1 := by
  norm_num [AIEFGate.DelayModeBridge.delayStep]
