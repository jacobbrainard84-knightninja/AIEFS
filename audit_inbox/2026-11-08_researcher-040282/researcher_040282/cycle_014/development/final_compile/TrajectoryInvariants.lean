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

omit [LinearOrder V] in
/-- A row envelope controls each nonnegative edge, not just a matrix norm. -/
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

omit [LinearOrder V] in
/-- No phase-locking or small-angle assumption is needed for this envelope. -/
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

section Witnesses

/-- Exact-real non-production witnesses; all have EngineGate except pB below. -/
def pWide : Params := ⟨1, 1, 2, 1, 2, 1, 0⟩
def pTight : Params := ⟨1, 1, 1, 1, 1, 1, 0⟩
def pQuarter : Params := ⟨1, 1, 1/4, 1, 1/4, 1, 0⟩

theorem pWide_engine : EngineGate pWide := by constructor <;> norm_num [pWide]
theorem pTight_engine : EngineGate pTight := by constructor <;> norm_num [pTight]
theorem pQuarter_engine : EngineGate pQuarter := by constructor <;> norm_num [pQuarter]

abbrev X := Capacity.Xo

def zeroB : Weights (Fin 2) := fun _ _ => 0
def onesB : Weights (Fin 2) := fun _ _ => 1
def dirtyB : Weights (Fin 2) := fun i j => if i = j then -1 else 1

def asymDrive : Weights (Fin 2) := fun i j => if i = 0 ∧ j = 1 then 2 else 0

theorem dirty_not_structural : ¬ Structural dirtyB := by
  intro h
  have hd := h.2.2 (0 : Fin 2)
  norm_num [dirtyB] at hd

/-- Main's gamma*dt=1 reset ignores the old B, not a hypothesis of the general proof. -/
private theorem wide_pre (D B : Weights (Fin 2)) : preM pWide D B = D := by
  funext i j
  dsimp [preM, pWide]
  ring

private theorem wide_sym_zero (B : Weights (Fin 2)) : symM pWide (X 0) B = X 0 := by
  funext i j
  fin_cases i <;> fin_cases j <;> simp [symM, clipM, wide_pre, Capacity.Xo]

private theorem wide_sym_one (B : Weights (Fin 2)) : symM pWide (X 1) B = X 1 := by
  funext i j
  fin_cases i <;> fin_cases j <;> simp [symM, clipM, wide_pre, Capacity.Xo]

theorem wide_resets_zero (B : Weights (Fin 2)) : weightUpdate pWide (X 0) B = X 0 := by
  unfold weightUpdate
  rw [Capacity.stepM_eq_gateM, wide_sym_zero]
  exact Capacity.gateM_fixes_feasible pWide pWide_engine _ (by intro i; rw [Capacity.rowS_Xo]; norm_num [pWide])

theorem wide_resets_one (B : Weights (Fin 2)) : weightUpdate pWide (X 1) B = X 1 := by
  unfold weightUpdate
  rw [Capacity.stepM_eq_gateM, wide_sym_one]
  exact Capacity.gateM_fixes_feasible pWide pWide_engine _ (by intro i; rw [Capacity.rowS_Xo]; norm_num [pWide])

theorem dirty_start_repaired : weightUpdate pWide (X 1) dirtyB = X 1 := wide_resets_one dirtyB

open Classical in
/-- Genuine B-feedback: the drive flips when the previous edge is positive. -/
def flipDrive (_ : ℕ) (_ : Unit) (B : Weights (Fin 2)) : Weights (Fin 2) :=
  X (if B 0 1 ≤ 0 then 1 else 0)

def keepAux (_ : ℕ) (_ : Unit) (_ _ : Weights (Fin 2)) : Unit := ()

theorem feedback_three_steps :
    weightsTrace (fun _ => pWide) flipDrive keepAux ((), zeroB) 1 = X 1 ∧
    weightsTrace (fun _ => pWide) flipDrive keepAux ((), zeroB) 2 = X 0 ∧
    weightsTrace (fun _ => pWide) flipDrive keepAux ((), zeroB) 3 = X 1 := by
  have h1 : weightsTrace (fun _ => pWide) flipDrive keepAux ((), zeroB) 1 = X 1 := by
    rw [weightsTrace_succ]
    simpa [weightsTrace, trajectory, flipDrive, zeroB] using wide_resets_one zeroB
  have h2 : weightsTrace (fun _ => pWide) flipDrive keepAux ((), zeroB) 2 = X 0 := by
    rw [weightsTrace_succ, h1]
    simp only [flipDrive, Capacity.Xo]
    norm_num
    exact wide_resets_zero (X 1)
  have h3 : weightsTrace (fun _ => pWide) flipDrive keepAux ((), zeroB) 3 = X 1 := by
    rw [weightsTrace_succ, h2]
    simp only [flipDrive, Capacity.Xo]
    norm_num
    exact wide_resets_one (X 0)
  exact ⟨h1,h2,h3⟩

/-- A complete two-cycle under valid parameters and genuinely state-dependent
bounded drive. Safety is not an eventual-freezing theorem. -/
theorem feedback_two_cycle : ∀ k,
    weightsTrace (fun _ => pWide) flipDrive keepAux ((),zeroB) (2*k) = X 0 ∧
    weightsTrace (fun _ => pWide) flipDrive keepAux ((),zeroB) (2*k+1) = X 1 := by
  intro k
  induction k with
  | zero =>
      constructor
      · change zeroB = X 0
        funext i j
        simp [zeroB, Capacity.Xo]
      · exact feedback_three_steps.1
  | succ k ih =>
      have he : weightsTrace (fun _ => pWide) flipDrive keepAux ((),zeroB) (2*(k+1)) = X 0 := by
        have ht : 2*(k+1) = (2*k+1)+1 := by omega
        rw [ht, weightsTrace_succ, ih.2]
        simp only [flipDrive, Capacity.Xo]
        norm_num
        exact wide_resets_zero (X 1)
      have ho : weightsTrace (fun _ => pWide) flipDrive keepAux ((),zeroB) (2*(k+1)+1) = X 1 := by
        rw [weightsTrace_succ, he]
        simp only [flipDrive, Capacity.Xo]
        norm_num
        exact wide_resets_one (X 0)
      exact ⟨he,ho⟩

theorem feedback_not_eventually_constant :
    ¬ ∃ N c, ∀ n, N ≤ n →
      weightsTrace (fun _ => pWide) flipDrive keepAux ((),zeroB) n 0 1 = c := by
  rintro ⟨N,c,h⟩
  have he := h (2*N) (by omega)
  have ho := h (2*N+1) (by omega)
  rw [(feedback_two_cycle N).1] at he
  rw [(feedback_two_cycle N).2] at ho
  norm_num [Capacity.Xo] at he ho
  linarith

/-- Exact bad-component values, independent of a failed kept proof. -/
theorem noClip_negative : Counterfactual.noClip pWide (X (-1)) zeroB 0 1 = -1 := by
  norm_num [Counterfactual.noClip, Capacity.gateM, Capacity.GateOnX, Capacity.rowS,
    preM, pWide, zeroB, Capacity.Xo, Fin.sum_univ_two, Fin.exists_fin_two]

theorem noSym_asymmetric :
    Counterfactual.noSym pWide asymDrive zeroB 0 1 = 2 ∧
    Counterfactual.noSym pWide asymDrive zeroB 1 0 = 0 := by
  norm_num [Counterfactual.noSym, Capacity.gateM, Capacity.GateOnX, Capacity.rowS,
    clipM, preM, pWide, zeroB, asymDrive, Fin.sum_univ_two, Fin.exists_fin_two]

theorem noDiag_nonzero : Counterfactual.noDiag pWide onesB zeroB 0 0 = 1 := by
  norm_num [Counterfactual.noDiag, Capacity.gateM, Capacity.GateOnX, Capacity.rowS,
    clipM, preM, pWide, zeroB, onesB, Fin.sum_univ_two, Fin.exists_fin_two]

theorem noGate_over_capacity :
    Capacity.rowS (Counterfactual.noGate pTight (X 3) zeroB) 0 = 3 := by
  norm_num [Counterfactual.noGate, Capacity.rowS, symM, clipM, preM,
    pTight, zeroB, Capacity.Xo, Fin.sum_univ_two]

/-- Current versus next capacity: shrinking a future parameter cannot retroactively
bound a state produced by the preceding transition. -/
def capSchedule (n : ℕ) : Params := if n = 0 then pWide else pQuarter

def oneDrive (_ : ℕ) (_ : Unit) (_ : Weights (Fin 2)) : Weights (Fin 2) := X 1

theorem capacity_clock_refuted :
    ¬ Capacity.rowS (weightsTrace capSchedule oneDrive keepAux ((),zeroB) 1) 0 ≤ (capSchedule 1).cap := by
  have h : weightsTrace capSchedule oneDrive keepAux ((),zeroB) 1 = X 1 := by
    rw [weightsTrace_succ]
    simpa [capSchedule, oneDrive, weightsTrace, trajectory] using wide_resets_one zeroB
  rw [h, Capacity.rowS_Xo]
  norm_num [capSchedule, pQuarter]

/-- Reuse main's independent guard-link counterexample; no duplicate gate audit. -/
theorem broken_link_refuted :
    ¬ Capacity.rowS (weightUpdate Capacity.pB (X 75) zeroB) 0 ≤ Capacity.pB.cap :=
  Capacity.false_stepM_row_no_link

/-- A universal all-times safety claim without initial structure is false at time0. -/
theorem initial_time_refuted :
    ¬ Structural (weightsTrace (fun _ => pWide) oneDrive keepAux ((),dirtyB) 0) := by
  exact dirty_not_structural

end Witnesses

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

#print axioms AIEFGate.TrajectorySafety.pWide_engine

#print axioms AIEFGate.TrajectorySafety.pTight_engine

#print axioms AIEFGate.TrajectorySafety.pQuarter_engine

#print axioms AIEFGate.TrajectorySafety.dirty_not_structural

#print axioms AIEFGate.TrajectorySafety.wide_resets_zero

#print axioms AIEFGate.TrajectorySafety.wide_resets_one

#print axioms AIEFGate.TrajectorySafety.dirty_start_repaired

#print axioms AIEFGate.TrajectorySafety.feedback_three_steps

#print axioms AIEFGate.TrajectorySafety.noClip_negative

#print axioms AIEFGate.TrajectorySafety.noSym_asymmetric

#print axioms AIEFGate.TrajectorySafety.noDiag_nonzero

#print axioms AIEFGate.TrajectorySafety.noGate_over_capacity

#print axioms AIEFGate.TrajectorySafety.capacity_clock_refuted

#print axioms AIEFGate.TrajectorySafety.broken_link_refuted

#print axioms AIEFGate.TrajectorySafety.initial_time_refuted

#print axioms AIEFGate.TrajectorySafety.feedback_two_cycle

#print axioms AIEFGate.TrajectorySafety.feedback_not_eventually_constant
