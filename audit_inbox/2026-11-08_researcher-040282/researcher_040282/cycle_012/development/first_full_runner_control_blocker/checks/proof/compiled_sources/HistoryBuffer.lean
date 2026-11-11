/-
Reachable constant-prehistory queue for a D-step delay: D+1 snapshots.
Pure value/index theorem, independent of how the appended trace is generated.
Not a theorem about Python aliasing, floating trigonometry, or phase locking.
-/
import Std

set_option autoImplicit false

universe u

namespace Researcher040282.Delay

abbrev History (d : Nat) (A : Type u) := Fin (d + 1) → A

def shiftAppend {A : Type u} (d : Nat) (h : History d A) (fresh : A) : History d A :=
  fun i => if hi : i.val < d then h ⟨i.val + 1, Nat.succ_lt_succ hi⟩ else fresh

def historyTrace {A : Type u} (d : Nat) (x : Nat → A) : Nat → History d A
  | 0 => fun _ => x 0
  | n + 1 => shiftAppend d (historyTrace d x n) (x (n + 1))

/-- Every queue position, including startup with constant prehistory. -/
theorem historyTrace_index {A : Type u} (d : Nat) (x : Nat → A) :
    ∀ n (i : Fin (d + 1)), historyTrace d x n i = x (n + i.val - d) := by
  intro n
  induction n with
  | zero =>
      intro i
      have hzero : 0 + i.val - d = 0 := by omega
      simp only [historyTrace, hzero]
  | succ n ih =>
      intro i
      simp only [historyTrace, shiftAppend]
      split
      · rename_i hi
        rw [ih]
        congr 1
        change n + (i.val + 1) - d = n + 1 + i.val - d
        omega
      · rename_i hi
        have heq : i.val = d := by omega
        congr 1
        omega

/-- At read time n the oldest phase is n-D, not n-(D+1) or n-D+1. -/
theorem historyTrace_oldest {A : Type u} (d : Nat) (x : Nat → A) (n : Nat) :
    historyTrace d x n ⟨0, Nat.zero_lt_succ d⟩ = x (n - d) := by
  simpa only [Nat.add_zero] using historyTrace_index d x n ⟨0, Nat.zero_lt_succ d⟩

/-- The newest snapshot agrees with the current appended trace value. -/
theorem historyTrace_newest {A : Type u} (d : Nat) (x : Nat → A) (n : Nat) :
    historyTrace d x n ⟨d, Nat.lt_succ_self d⟩ = x n := by
  simpa only [Nat.add_sub_cancel] using historyTrace_index d x n ⟨d, Nat.lt_succ_self d⟩

#print axioms Researcher040282.Delay.historyTrace_index
#print axioms Researcher040282.Delay.historyTrace_oldest
#print axioms Researcher040282.Delay.historyTrace_newest

end Researcher040282.Delay
