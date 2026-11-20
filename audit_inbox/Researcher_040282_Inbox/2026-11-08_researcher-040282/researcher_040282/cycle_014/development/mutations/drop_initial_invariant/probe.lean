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

namespace Counterfactual

/-- Deliberately omit clipping; NOT the implementation used by trajectory. -/
def noClip (p : Params) (D B : Weights V) : Weights V :=
  Capacity.gateM p (fun i j => if i = j then 0 else (preM p D B i j + preM p D B j i) / 2)

/-- Deliberately omit symmetrisation. -/
def noSym (p : Params) (D B : Weights V) : Weights V :=
  Capacity.gateM p (fun i j => if i = j then 0 else clipM p D B i j)

/-- Deliberately retain the diagonal. -/
def noDiag (p : Params) (D B : Weights V) : Weights V :=
  Capacity.gateM p (fun i j => (clipM p D B i j + clipM p D B j i) / 2)

/-- Deliberately bypass the capacity gate. -/
def noGate (p : Params) (D B : Weights V) : Weights V := symM p D B

end Counterfactual


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

/-- Exact-real non-production witnesses; all have EngineGate except pB below. -/
def pWide : Params := ⟨1, 1, 2, 1, 2, 1, 0⟩
def pTight : Params := ⟨1, 1, 1, 1, 1, 1, 0⟩
def pQuarter : Params := ⟨1, 1, 1/4, 1, 1/4, 1, 0⟩

abbrev X := Capacity.Xo

def zeroB : Weights (Fin 2) := fun _ _ => 0
def onesB : Weights (Fin 2) := fun _ _ => 1
def dirtyB : Weights (Fin 2) := fun i j => if i = j then -1 else 1

def asymDrive : Weights (Fin 2) := fun i j => if i = 0 ∧ j = 1 then 2 else 0


def capSchedule (n : ℕ) : Params := if n = 0 then pWide else pQuarter

def oneDrive (_ : ℕ) (_ : Unit) (_ : Weights (Fin 2)) : Weights (Fin 2) := X 1

def keepAux (_ : ℕ) (_ : Unit) (_ _ : Weights (Fin 2)) : Unit := ()

set_option linter.unusedSimpArgs false

example : Structural (weightsTrace (fun _ => pWide) oneDrive keepAux ((),dirtyB) 0) := by
  norm_num [weightUpdate, Counterfactual.noClip, Counterfactual.noSym, Counterfactual.noDiag, Counterfactual.noGate, Structural, weightsTrace, trajectory, feedbackStep, Capacity.gateM, Capacity.GateOnX, Capacity.rowS, stepM, GateOnM, rowM, symM, clipM, preM, scale, pWide, pTight, pQuarter, capSchedule, Capacity.pB, Capacity.Xo, zeroB, onesB, dirtyB, asymDrive, Fin.sum_univ_two, Fin.exists_fin_two, Fin.forall_fin_two]

end
end AIEFGate.TrajectorySafety
