import HistoryBuffer
open Researcher040282.Delay

theorem controlAbstractZero : historyTrace 0 (fun n : Nat => 2*n+3) 7 ⟨0, by decide⟩ = 17 := by decide
#print axioms controlAbstractZero
