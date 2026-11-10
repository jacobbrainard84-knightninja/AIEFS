import HistoryBuffer
open Researcher040282.Delay

example : historyTrace 2 (fun n : Nat => n) 4 ⟨0, by decide⟩ = 1 := by decide
