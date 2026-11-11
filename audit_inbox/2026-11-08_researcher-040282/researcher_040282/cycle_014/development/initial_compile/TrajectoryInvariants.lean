/-
Researcher040282: all-step weight safety for arbitrary causal feedback driving.
Uses current main stepM/Capacity; no frozen-R or desired-band hypothesis.
Exact reals, not a complete oscillator-state instantiation or float64 FFI.
-/
import AIEFGateCore.Capacity
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFGate.TrajectorySafety

open Finset AIEFGate.MatrixForm
open scoped BigOperators

variable {V S : Type*} [Fintype V] [LinearOrder V]

abbrev Weights (V : Type*) := V → V → ℝ

noncomputable section

/-- IMPLEMENTATION: real matrix operator from current main. -/
def weightUpdate (p : Params) (D B : Weights V) : Weights V := stepM p D B

def Structural (B : Weights V) : Prop :=
  (∀ i j, 0 ≤ B i j) ∧ (∀ i j, B i j = B j i) ∧ (∀ i, B i i = 0)

/-- Drive is allowed to read the old auxiliary state AND old B. New B is computed
before the auxiliary update, which can use both old and new B (as the phase does).
No restriction, invariant, symmetry or future-tail premise is imposed on F/U. -/
def feedbackStep (p : ℕ → Params) (F : ℕ → S → Weights V → Weights V)
    (U : ℕ → S → Weights V → Weights V → S) (n : ℕ)
    (state : S × Weights V) : S × Weights V :=
  let Bnew := weightUpdate (p n) (F n state.1 state.2) state.2
  (U n state.1 state.2 Bnew, Bnew)

def trajectory (p : ℕ → Params) (F : ℕ → S → Weights V → Weights V)
    (U : ℕ → S → Weights V → Weights V → S) (initial : S × Weights V) :
    ℕ → S × Weights V
  | 0 => initial
  | n + 1 => feedbackStep p F U n (trajectory p F U initial n)

def weightsTrace (p : ℕ → Params) (F : ℕ → S → Weights V → Weights V)
    (U : ℕ → S → Weights V → Weights V → S) (initial : S × Weights V)
    (n : ℕ) : Weights V := (trajectory p F U initial n).2

theorem weightsTrace_succ (p : ℕ → Params) (F : ℕ → S → Weights V → Weights V)
    (U : ℕ → S → Weights V → Weights V → S) (initial : S × Weights V) (n : ℕ) :
    weightsTrace p F U initial (n + 1) =
      weightUpdate (p n) (F n (trajectory p F U initial n).1 (weightsTrace p F U initial n))
        (weightsTrace p F U initial n) := rfl

/-- Reuse one-step main facts; structural safety needs only cap,epsilon>=0.
No structural/feasibility/symmetry premise on D or B, no gamma/dt stability guard. -/
theorem weightUpdate_structural (p : Params) (hc : 0 ≤ p.cap) (he : 0 ≤ p.ε)
    (D B : Weights V) : Structural (weightUpdate p D B) := by
  refine ⟨?_, ?_, ?_⟩
  · intro i j
    change 0 ≤ stepM p D B i j
    rw [Capacity.stepM_eq_gateM]
    exact Capacity.gateM_nonneg p (Capacity.symM_nonneg p D B) hc he i j
  · exact stepM_symm p D B
  · exact stepM_diag p D B

/-- Every positive-time state is repaired by its most recent step. Only that
step's sign hypotheses are needed; no assumptions about earlier steps or B0. -/
theorem positive_time_structural (p : ℕ → Params)
    (F : ℕ → S → Weights V → Weights V) (U : ℕ → S → Weights V → Weights V → S)
    (initial : S × Weights V) (n : ℕ) (hc : 0 ≤ (p n).cap) (he : 0 ≤ (p n).ε) :
    Structural (weightsTrace p F U initial (n + 1)) := by
  rw [weightsTrace_succ]
  exact weightUpdate_structural (p n) hc he _ _

/-- Including time zero correctly requires the initial structural invariant. -/
theorem all_times_structural (p : ℕ → Params)
    (F : ℕ → S → Weights V → Weights V) (U : ℕ → S → Weights V → Weights V → S)
    (initial : S × Weights V) (hc : ∀ n, 0 ≤ (p n).cap) (he : ∀ n, 0 ≤ (p n).ε)
    (hInit : Structural initial.2) : ∀ n, Structural (weightsTrace p F U initial n) := by
  intro n
  cases n with
  | zero => exact hInit
  | succ n => exact positive_time_structural p F U initial n (hc n) (he n)

/-- Capacity is tied to the parameters USED in this transition, not p_(n+1).
No initial feasibility and no restriction on the state-dependent drive. -/
theorem post_capacity (p : ℕ → Params) (F : ℕ → S → Weights V → Weights V)
    (U : ℕ → S → Weights V → Weights V → S) (initial : S × Weights V)
    (n : ℕ) (hp : EngineGate (p n)) (i : V) :
    Capacity.rowS (weightsTrace p F U initial (n + 1)) i ≤ (p n).cap := by
  rw [weightsTrace_succ]
  exact Capacity.stepM_row_le_cap (p n) hp _ _ i

theorem fixed_parameter_capacity (p : Params) (hp : EngineGate p)
    (F : ℕ → S → Weights V → Weights V) (U : ℕ → S → Weights V → Weights V → S)
    (initial : S × Weights V) (n : ℕ) (i : V) :
    Capacity.rowS (weightsTrace (fun _ => p) F U initial (n + 1)) i ≤ p.cap :=
  post_capacity (fun _ => p) F U initial n hp i

/-- A row envelope controls each nonnegative edge, not just a matrix norm. -/
omit [LinearOrder V] in
theorem entry_envelope (B : Weights V) (c : ℝ) (hn : ∀ i j, 0 ≤ B i j)
    (hr : ∀ i, Capacity.rowS B i ≤ c) (i j : V) : 0 ≤ B i j ∧ B i j ≤ c := by
  have hle : B i j ≤ ∑ k, B i k :=
    Finset.single_le_sum (fun k _ => hn i k) (Finset.mem_univ j)
  exact ⟨hn i j, hle.trans (hr i)⟩

theorem post_entry_envelope (p : ℕ → Params) (F : ℕ → S → Weights V → Weights V)
    (U : ℕ → S → Weights V → Weights V → S) (initial : S × Weights V)
    (n : ℕ) (hp : EngineGate (p n)) (i j : V) :
    0 ≤ weightsTrace p F U initial (n + 1) i j ∧
      weightsTrace p F U initial (n + 1) i j ≤ (p n).cap := by
  exact entry_envelope _ _
    (positive_time_structural p F U initial n hp.cap_pos.le hp.eps_pos.le).1
    (post_capacity p F U initial n hp) i j

/-- The actual delayed-minus-current sine convention, with NEW weights. -/
def sineCoupling (B : Weights V) (theta delayed : V → ℝ) (i : V) : ℝ :=
  ∑ j, B i j * Real.sin (delayed j - theta i)

/-- No phase-locking or small-angle assumption is needed for this envelope. -/
omit [LinearOrder V] in
theorem sineCoupling_bound (B : Weights V) (c : ℝ) (theta delayed : V → ℝ)
    (hn : ∀ i j, 0 ≤ B i j) (hr : ∀ i, Capacity.rowS B i ≤ c) (i : V) :
    |sineCoupling B theta delayed i| ≤ c := by
  calc
    _ ≤ ∑ j, |B i j * Real.sin (delayed j - theta i)| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ j, B i j * |Real.sin (delayed j - theta i)| := by
      apply Finset.sum_congr rfl
      intro j _
      rw [abs_mul, abs_of_nonneg (hn i j)]
    _ ≤ ∑ j, B i j * 1 := by
      apply Finset.sum_le_sum
      intro j _
      exact mul_le_mul_of_nonneg_left (Real.abs_sin_le_one _) (hn i j)
    _ = Capacity.rowS B i := by simp [Capacity.rowS]
    _ ≤ c := hr i

theorem post_sineCoupling_bound (p : ℕ → Params)
    (F : ℕ → S → Weights V → Weights V) (U : ℕ → S → Weights V → Weights V → S)
    (initial : S × Weights V) (n : ℕ) (hp : EngineGate (p n))
    (theta delayed : V → ℝ) (i : V) :
    |sineCoupling (weightsTrace p F U initial (n + 1)) theta delayed i| ≤ (p n).cap := by
  exact sineCoupling_bound _ _ theta delayed
    (positive_time_structural p F U initial n hp.cap_pos.le hp.eps_pos.le).1
    (post_capacity p F U initial n hp) i

/-- Source-shaped phase increment; this is not a definition of the whole phase loop. -/
def phaseIncrement (p : ℕ → Params) (F : ℕ → S → Weights V → Weights V)
    (U : ℕ → S → Weights V → Weights V → S) (initial : S × Weights V)
    (omega theta delayed : V → ℝ) (n : ℕ) (i : V) : ℝ :=
  (p n).dt * (omega i + sineCoupling (weightsTrace p F U initial (n + 1)) theta delayed i)

theorem post_phaseIncrement_bound (p : ℕ → Params)
    (F : ℕ → S → Weights V → Weights V) (U : ℕ → S → Weights V → Weights V → S)
    (initial : S × Weights V) (omega theta delayed : V → ℝ)
    (n : ℕ) (hp : EngineGate (p n)) (i : V) :
    |phaseIncrement p F U initial omega theta delayed n i| ≤ |(p n).dt| * (|omega i| + (p n).cap) := by
  rw [phaseIncrement, abs_mul]
  apply mul_le_mul_of_nonneg_left _ (abs_nonneg _)
  exact (abs_add_le _ _).trans
    (add_le_add le_rfl (post_sineCoupling_bound p F U initial n hp theta delayed i))

end
end AIEFGate.TrajectorySafety

#print axioms AIEFGate.TrajectorySafety.weightsTrace_succ
#print axioms AIEFGate.TrajectorySafety.weightUpdate_structural
#print axioms AIEFGate.TrajectorySafety.positive_time_structural
#print axioms AIEFGate.TrajectorySafety.all_times_structural
#print axioms AIEFGate.TrajectorySafety.post_capacity
#print axioms AIEFGate.TrajectorySafety.fixed_parameter_capacity
#print axioms AIEFGate.TrajectorySafety.entry_envelope
#print axioms AIEFGate.TrajectorySafety.post_entry_envelope
#print axioms AIEFGate.TrajectorySafety.sineCoupling_bound
#print axioms AIEFGate.TrajectorySafety.post_sineCoupling_bound
#print axioms AIEFGate.TrajectorySafety.post_phaseIncrement_bound
