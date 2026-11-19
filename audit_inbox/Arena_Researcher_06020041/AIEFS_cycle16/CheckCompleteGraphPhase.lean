import AIEFGateCore.CompleteGraphPhase
open scoped BigOperators
open AIEFGate.CompleteGraphPhase
#print axioms AIEFGate.CompleteGraphPhase.total_sub_self
#print axioms AIEFGate.CompleteGraphPhase.transverse_step
#print axioms AIEFGate.CompleteGraphPhase.transverse_eigenvalue_inside
#print axioms AIEFGate.CompleteGraphPhase.constant_neighbour_sum
#print axioms AIEFGate.CompleteGraphPhase.common_step
#print axioms AIEFGate.CompleteGraphPhase.common_eigenvalue_bound

-- Value probe: retaining the diagonal would change this phase-block output.
def probeState (t : ℕ) (i : Fin 2) : ℂ := if t = 1 ∧ i = 0 then 1 else 0
example : phaseStep 2 1 (1 / 2) probeState 0 0 = 0 ∧
    ((1 / 2 : ℂ) * (∑ j : Fin 2, probeState 1 j)) = (1 / 2 : ℂ) := by
  norm_num [phaseStep, probeState, Fin.sum_univ_two]
