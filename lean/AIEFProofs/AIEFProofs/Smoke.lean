import Mathlib

set_option autoImplicit false

namespace AIEFProofs

example (x y : ℝ) : x + y = y + x := by
  ring

example (x : ℝ) : x - x = 0 := by
  ring

end AIEFProofs
