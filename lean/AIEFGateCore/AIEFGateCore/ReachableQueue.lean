/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.EngineStepRef
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Angle

/-!
# Reachable finite history queue (Arena D7)

Research candidate. An engine-order finite queue (index 0 oldest, index `d` newest) with a
drop-oldest/append shift. Every reachable state from a consistent start (current phase equals the
newest slot on the circle) stays consistent, for any next-phase rule; `bad_breaks_reference` shows
an inconsistent start breaks the newest-slot reference. Exact reals; not the Python list or
float64. Value probes and `false_*` witnesses for the mutation harness are appended (SPEC §17).

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D7, deposit sha256 `7ee20295…`; proofs and
statements unchanged from the deposit.
-/

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

/-! ### Value probes and negations used by the mutation harness (SPEC §17)

The probes evaluate `shift`, `view` and `head` at closed data straight from their definitions. -/

/-- One node, `d = 1`: current phase `0`, slot `j` holds `j` (oldest `0`, newest `1`). -/
def probeState : State 1 1 := ⟨fun _ => 0, fun j _ => (j.val : ℝ)⟩

/-- One node, `d = 1`: current phase `0`, oldest slot `π/2`, newest slot `0`. -/
noncomputable def probeQ : State 1 1 :=
  ⟨fun _ => 0, fun j _ => if j.val = 0 then Real.pi / 2 else 0⟩

/-- Shifting in `5`: the newest slot is `5`, the oldest takes the old newest `1`. An unshifted queue
gives oldest `0`; not appending gives newest `1`. -/
theorem probe_shift_values :
    (shift 1 1 probeState (fun _ => 5)).history 1 0 = 5 ∧
      (shift 1 1 probeState (fun _ => 5)).history 0 0 = 1 := by
  constructor <;> simp [shift, probeState]

/-- The newest-first view reads slot `d - k`: lag 0 is the newest `1`, lag 1 the oldest `0`. -/
theorem probe_view_values : view 1 1 probeState 0 0 = 1 ∧ view 1 1 probeState 1 0 = 0 := by
  constructor <;> simp [view, reverseIndex, probeState]

/-- The head reads the OLDEST slot: `0 + 1·(0 + 1·sin(π/2 - 0)) = 1`; the newest slot gives `0`. -/
theorem probe_head_value : head 1 1 1 0 (fun _ _ => 1) probeQ 0 = 1 := by
  simp [head, probeQ]

/-- Dropping consistency from `reachable_consistent` is false (`bad`, `t = 0`). -/
theorem false_reachable_no_consistent :
    ¬ (∀ (n d : ℕ) (next : State n d → Fin n → ℝ) (s : State n d) (_h : True) (t : ℕ),
      Consistent n d (iterate n d next t s)) := by
  intro H
  have h := H 1 1 (fun _ _ => 0) bad trivial 0 0
  simp only [iterate, view, reverseIndex, bad] at h
  exact Real.Angle.pi_ne_zero (by simpa using h.symm)

/-- Dropping `0 < k` from `view_shift` is false (`k = 0`: the newest slot is the appended `5`). -/
theorem false_view_shift_no_pos :
    ¬ (∀ (n d : ℕ) (s : State n d) (out : Fin n → ℝ) (k : Fin (d + 1)) (_hk : True) (i : Fin n),
      view n d (shift n d s out) k i = view n d s ⟨k.val - 1, by have := k.isLt; omega⟩ i) := by
  intro H
  have h := H 1 1 probeState (fun _ => 5) 0 trivial 0
  norm_num [view, shift, reverseIndex, probeState] at h

#print axioms probe_shift_values
#print axioms probe_view_values
#print axioms probe_head_value
#print axioms false_reachable_no_consistent
#print axioms false_view_shift_no_pos

end AIEFGate.ReachableQueue
