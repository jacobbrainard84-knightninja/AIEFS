import EMATracking
open Researcher040282.EMA Researcher040282.Tracking
noncomputable def controlZ (n : ℕ) : ℂ := if n = 0 then 1 else -1
noncomputable def controlLateZ (n : ℕ) : ℂ := if n < 2 then 1 else -1
theorem controlAlphaZero : emaTrajectory 0 1 controlZ 1 - controlZ 1 = 2 := by
  norm_num [emaTrajectory, emaStep, controlZ]
#print axioms controlAlphaZero
