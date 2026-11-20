import EMATracking
open Researcher040282.EMA Researcher040282.Tracking
noncomputable def controlZ (n : ℕ) : ℂ := if n = 0 then 1 else -1
noncomputable def controlLateZ (n : ℕ) : ℂ := if n < 2 then 1 else -1
example : ‖emaTrajectory (1/2) 1 controlLateZ 2 - controlLateZ 2‖ ≤ (1 : ℝ) := by
  have h : emaTrajectory (1/2) 1 controlLateZ 2 - controlLateZ 2 = (2 : ℂ) := by
    norm_num [emaTrajectory, emaStep, controlLateZ]
  rw [h, Complex.norm_of_nonneg (by norm_num : (0 : ℝ) ≤ 2)]
  norm_num
