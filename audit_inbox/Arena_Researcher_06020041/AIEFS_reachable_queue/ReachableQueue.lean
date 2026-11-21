import AIEFGateCore.EngineStepRef
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Angle

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.ReachableQueue

/-- Engine-order queue: index 0 is oldest; index d is newest. -/
structure State (n d : ℕ) where
  theta : Fin n → ℝ
  history : Fin (d + 1) → Fin n → ℝ

def newestIndex (d : ℕ) : Fin (d + 1) := ⟨d, by omega⟩
def reverseIndex (d : ℕ) (k : Fin (d + 1)) : Fin (d + 1) :=
  ⟨d - k.val, by have := k.isLt; omega⟩

def view (n d : ℕ) (s : State n d) (k : Fin (d + 1)) (i : Fin n) : ℝ :=
  s.history (reverseIndex d k) i

def Consistent (n d : ℕ) (s : State n d) : Prop :=
  ∀ i, (s.theta i : Real.Angle) = (view n d s 0 i : Real.Angle)

/-- Drop oldest and append next theta. The input next theta can be any function;
this is stronger than restricting to a particular weight or phase rule. -/
def shift (n d : ℕ) (s : State n d) (out : Fin n → ℝ) : State n d :=
  ⟨out, fun j i => if h : j.val = d then out i else
    s.history ⟨j.val + 1, by have := j.isLt; omega⟩ i⟩

/-- The appended value makes even an inconsistent input consistent after one step. -/
theorem shift_consistent (n d : ℕ) (s : State n d) (out : Fin n → ℝ) :
    Consistent n d (shift n d s out) := by
  intro i
  simp [view, reverseIndex, shift]

/-- State-dependent steps preserve consistency for arbitrary numbers of steps. -/
def iterate (n d : ℕ) (next : State n d → Fin n → ℝ) : ℕ → State n d → State n d
  | 0, s => s
  | t + 1, s => iterate n d next t (shift n d s (next s))

theorem reachable_consistent (n d : ℕ) (next : State n d → Fin n → ℝ)
    (s : State n d) (h : Consistent n d s) (t : ℕ) :
    Consistent n d (iterate n d next t s) := by
  induction t generalizing s with
  | zero => exact h
  | succ t ih => exact ih _ (shift_consistent n d s (next s))

/-- Newest-first shift at every nonzero retained lag. -/
theorem view_shift (n d : ℕ) (s : State n d) (out : Fin n → ℝ)
    (k : Fin (d + 1)) (hk : k.val > 0) (i : Fin n) :
    view n d (shift n d s out) k i =
      view n d s ⟨k.val - 1, by have := k.isLt; omega⟩ i := by
  unfold view shift reverseIndex
  have hne : d - k.val ≠ d := by have := k.isLt; omega
  simp only [hne, dite_false]
  congr 2
  have := k.isLt
  omega

/-- Matrix head uses oldest stored phase and current theta, as in the engine. -/
noncomputable def head (n d : ℕ) (dt omega : ℝ) (W : Fin n → Fin n → ℝ)
    (s : State n d) (i : Fin n) : ℝ :=
  s.theta i + dt * (omega + ∑ j : Fin n,
    W i j * Real.sin (s.history 0 j - s.theta i))

noncomputable def step (n d : ℕ) (dt omega : ℝ) (W : Fin n → Fin n → ℝ)
    (s : State n d) : State n d :=
  shift n d s (fun i => toIcoMod Real.two_pi_pos 0 (head n d dt omega W s i))

theorem step_reachable_consistent (n d : ℕ) (dt omega : ℝ)
    (W : Fin n → Fin n → ℝ) (s : State n d) (h : Consistent n d s) (t : ℕ) :
    Consistent n d (iterate n d (fun x => (step n d dt omega W x).theta) t s) :=
  reachable_consistent n d _ s h t

/-- An inconsistent finite initial history: current phase zero, newest π. -/
noncomputable def bad : State 1 1 := ⟨fun _ => 0, fun _ _ => Real.pi⟩

/-- At lag one the actual retained newest value differs from the reference
that substitutes theta in slot zero. -/
theorem bad_breaks_reference :
    (view 1 1 (step 1 1 1 0 (fun _ _ => 0) bad) 1 0 : Real.Angle) ≠
    (EngineStepRef.phaseStep 1 1 1 0 0
      (fun k _ => if k = 0 then 0 else Real.pi) 1 0 : Real.Angle) := by
  simpa [view, reverseIndex, step, shift, bad, EngineStepRef.phaseStep] using Real.Angle.pi_ne_zero

#print axioms bad_breaks_reference
#print axioms shift_consistent
#print axioms reachable_consistent
#print axioms view_shift
#print axioms step_reachable_consistent
end AIEFGate.ReachableQueue
