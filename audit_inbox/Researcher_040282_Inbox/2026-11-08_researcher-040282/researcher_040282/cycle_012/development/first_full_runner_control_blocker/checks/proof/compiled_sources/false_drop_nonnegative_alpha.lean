import EMATracking
open Researcher040282.EMA Researcher040282.Tracking
noncomputable def controlZ (n : ℕ) : ℂ := if n = 0 then 1 else -1
noncomputable def controlLateZ (n : ℕ) : ℂ := if n < 2 then 1 else -1
example : ‖emaTrajectory (-1) 0 (fun _ => 1) 1 - 1‖ ≤ (-1 : ℝ) := by
  norm_num [emaTrajectory, emaStep]
