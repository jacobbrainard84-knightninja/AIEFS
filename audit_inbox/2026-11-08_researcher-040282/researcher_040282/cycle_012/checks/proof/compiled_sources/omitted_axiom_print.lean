import EMATracking
open Researcher040282.EMA Researcher040282.Tracking
noncomputable def controlZ (n : ℕ) : ℂ := if n = 0 then 1 else -1
noncomputable def controlLateZ (n : ℕ) : ℂ := if n < 2 then 1 else -1
theorem controlNoPrint : True := by trivial
