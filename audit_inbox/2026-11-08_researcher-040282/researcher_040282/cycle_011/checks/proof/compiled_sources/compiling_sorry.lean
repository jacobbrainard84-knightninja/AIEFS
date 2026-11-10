import PhaseIncrement
open Researcher040282.Phase
noncomputable def controlX0 (_ : Unit) : ℝ := 0
noncomputable def controlOmega (_ : Unit) : ℝ := 0
noncomputable def controlU (n : ℕ) (_ : Unit) : ℝ := if n = 0 then Real.pi / 2 else Real.pi
theorem controlSorry : False := by sorry
#print axioms controlSorry
