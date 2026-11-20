import EMATracking
open Researcher040282.EMA Researcher040282.Tracking
noncomputable def controlZ (n : ℕ) : ℂ := if n = 0 then 1 else -1
noncomputable def controlLateZ (n : ℕ) : ℂ := if n < 2 then 1 else -1
example : emaTrajectory (1/2) 1 controlZ 1 - controlZ 1 = 1 := by
  norm_num [emaTrajectory, emaStep, controlZ, Complex.ext_iff]
