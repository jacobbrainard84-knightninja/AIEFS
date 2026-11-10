import HistoryBuffer
open Researcher040282.Delay

theorem controlNonzero : historyTrace 2 (fun n : Nat => n) 4 ⟨0, by decide⟩ = 2 := by decide
#print axioms controlNonzero
