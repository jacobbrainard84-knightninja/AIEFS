import HistoryBuffer
open Researcher040282.Delay

example : historyTrace 2 (fun n : Nat => n) 4 ⟨2, by decide⟩ = 3 := by decide
