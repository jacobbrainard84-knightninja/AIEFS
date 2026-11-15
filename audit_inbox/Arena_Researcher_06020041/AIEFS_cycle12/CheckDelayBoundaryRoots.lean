import AIEFGateCore.DelayBoundaryRoots
#print axioms AIEFGate.DelayBoundaryRoots.root_norm_le_one
#print axioms AIEFGate.DelayBoundaryRoots.unit_sum_aligned
#print axioms AIEFGate.DelayBoundaryRoots.common_root_closed_and_unit_unique
#print axioms AIEFGate.DelayBoundaryRoots.two_node_transverse_root_inside

-- Endpoint controls: the strict hypotheses are not cosmetic.
example : (1 : ℂ) ^ (1 + 1) = ((1 - (0 : ℝ) : ℝ) : ℂ) * (1 : ℂ) ^ (1 : ℕ) - (0 : ℂ) ∧
    ¬ ‖(1 : ℂ)‖ < 1 := by norm_num
example : (-1 : ℂ) ^ (1 + 1) = ((1 - (1 : ℝ) : ℝ) : ℂ) * (-1 : ℂ) ^ (1 : ℕ) + (1 : ℂ) ∧
    ‖(-1 : ℂ)‖ = 1 ∧ (-1 : ℂ) ≠ 1 := by norm_num
