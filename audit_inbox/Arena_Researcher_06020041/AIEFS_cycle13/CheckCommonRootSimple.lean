import AIEFGateCore.CommonRootSimple
open Polynomial AIEFGate.CommonRootSimple
#print axioms AIEFGate.CommonRootSimple.common_root
#print axioms AIEFGate.CommonRootSimple.derivative_at_one
#print axioms AIEFGate.CommonRootSimple.root_multiplicity_one

-- Negative control: if h is allowed to be -1, d=1 gives a double root at 1.
example : commonPoly 1 (-1) = (X - 1) ^ 2 := by
  simp [commonPoly]
  ring
example : (derivative (commonPoly 1 (-1))).eval 1 = 0 := by
  rw [derivative_at_one]
  norm_num
