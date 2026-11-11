/-
Researcher040282: concrete exact-real non-shuffled phase/history/EMA/B recursion.
Current main supplies the actual B operator;013/014are explicit candidate deps.
This is a proposed real reference model, NOT Python/float FFI or phase locking.
-/
import PhaseCoherenceBridge
import TrajectoryInvariants

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFGate.ClosedLoop

open scoped BigOperators

structure Config (V : Type*) where
  gate : Params
  eta : ℝ
  mu : ℝ
  Tw : ℝ
  tau : ℝ
  omega : V → ℝ

structure Aux (V : Type*) (d : ℕ) where
  theta : V → ℝ
  history : Fin (d + 1) → V → ℝ
  C : V → V → ℂ

variable {V : Type*} {d : ℕ}

noncomputable section

def alpha (c : Config V) : ℝ := Real.exp (-c.gate.dt / c.Tw)

def DelayConsistent (c : Config V) (d : ℕ) : Prop :=
  0 < c.gate.dt ∧ 0 < c.tau ∧ (d : ℝ) * c.gate.dt = c.tau

theorem delay_positive (c : Config V) (d : ℕ) (h : DelayConsistent c d) : 0 < d := by
  obtain ⟨hdt,htau,heq⟩ := h
  by_contra hn
  have hd : d = 0 := by omega
  subst d
  norm_num at heq
  linarith

theorem alpha_pos (c : Config V) : 0 < alpha c := Real.exp_pos _

theorem alpha_le_one (c : Config V) (hdt : 0 ≤ c.gate.dt) (hTw : 0 < c.Tw) : alpha c ≤ 1 := by
  apply Real.exp_le_one_iff.mpr
  exact div_nonpos_of_nonpos_of_nonneg (neg_nonpos.mpr hdt) hTw.le

def initialAux (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ) : Aux V d :=
  ⟨theta0, fun _ => theta0, C0⟩

/-- IMPLEMENTATION: source old-theta/oldest-history/pair-mean-frequency convention. -/
def rawInput (c : Config V) (a : Aux V d) (i j : V) : ℂ :=
  Complex.exp (Complex.I * ((a.theta i - a.history ⟨0, Nat.zero_lt_succ d⟩ j -
    ((c.omega i + c.omega j) / 2) * c.tau : ℝ) : ℂ))

/-- Source updates directed complex C before taking magnitudes. -/
def newC (c : Config V) (a : Aux V d) (i j : V) : ℂ :=
  (alpha c : ℂ) * a.C i j + ((1 - alpha c : ℝ) : ℂ) * rawInput c a i j

open Classical in
def complexMeanWrong (C : V → V → ℂ) (i j : V) : ℝ :=
  if i = j then 0 else ‖(C i j + C j i) / 2‖

/-- IMPLEMENTATION: abs first, then real symmetrisation, diagonal zero. -/
def newR (c : Config V) (a : Aux V d) : V → V → ℝ :=
  PhaseCoherence.reported (newC c a)

def drive (c : Config V) (a : Aux V d) (i j : V) : ℝ :=
  (c.eta + c.mu) * newR c a i j - c.mu

section Finite
variable [Fintype V] [LinearOrder V]

/-- Pure old-state preparation. Current-step R does not read/update B. -/
def prepareDrive (c : Config V) (_ : ℕ) (a : Aux V d) (_ : TrajectorySafety.Weights V) :
    TrajectorySafety.Weights V := drive c a

def sourceIncrement (c : Config V) (a : Aux V d) (Bnew : TrajectorySafety.Weights V) (i : V) : ℝ :=
  c.gate.dt * (c.omega i + TrajectorySafety.sineCoupling Bnew a.theta
    (a.history ⟨0, Nat.zero_lt_succ d⟩) i)

def unprojected (c : Config V) (a : Aux V d) (Bold : TrajectorySafety.Weights V) :
    TrajectorySafety.Weights V := MatrixForm.symM c.gate (drive c a) Bold

/-- IMPLEMENTATION: phase must consume NEW gated B, not old or unprojected B. -/
def usedIncrement (c : Config V) (a : Aux V d) (_Bold Bnew : TrajectorySafety.Weights V) : V → ℝ :=
  sourceIncrement c a (unprojected c a _Bold)

def nextTheta (c : Config V) (a : Aux V d) (Bold Bnew : TrajectorySafety.Weights V) (i : V) : ℝ :=
  Researcher040282.Phase.wrapPhase (a.theta i + usedIncrement c a Bold Bnew i)

/-- IMPLEMENTATION: append NEW theta; the C expression is pure and identical to F's. -/
def updateAux (c : Config V) (_ : ℕ) (a : Aux V d) (Bold Bnew : TrajectorySafety.Weights V) : Aux V d :=
  ⟨nextTheta c a Bold Bnew,
    Researcher040282.Delay.shiftAppend d a.history (nextTheta c a Bold Bnew),
    newC c a⟩

def run (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) : ℕ → Aux V d × TrajectorySafety.Weights V :=
  TrajectorySafety.trajectory (fun _ => c.gate) (prepareDrive c) (updateAux c) (initialAux d theta0 C0, B0)

def auxTrace (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) : Aux V d := (run c d theta0 C0 B0 n).1

def BTrace (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) : TrajectorySafety.Weights V := (run c d theta0 C0 B0 n).2

def thetaTrace (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) : V → ℝ := (auxTrace c d theta0 C0 B0 n).theta

/-- Generated from actual NEW model weights; not an independently prescribed u. -/
def incrementTrace (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) : V → ℝ :=
  sourceIncrement c (auxTrace c d theta0 C0 B0 n) (BTrace c d theta0 C0 B0 (n + 1))

section Probes

def probeParams : Params := ⟨1,1,1,1,1,1,0⟩
def probeConfig : Config (Fin 2) :=
  ⟨probeParams,4,0,(Real.log 2)⁻¹,1,fun _ => 0⟩
def probeTheta : Fin 2 → ℝ := ![0,Real.pi/2]
def zeroC : Fin 2 → Fin 2 → ℂ := fun _ _ => 0
def zeroB : TrajectorySafety.Weights (Fin 2) := fun _ _ => 0
def probeAux : Aux (Fin 2) 1 := initialAux 1 probeTheta zeroC

theorem probe_gate_valid : EngineGate probeConfig.gate := by constructor <;> norm_num [probeConfig,probeParams]
theorem probe_delay_valid : DelayConsistent probeConfig 1 := by norm_num [DelayConsistent,probeConfig,probeParams]
theorem probe_Tw_positive : 0 < probeConfig.Tw := by
  change 0 < (Real.log 2)⁻¹
  exact inv_pos.mpr (Real.log_pos (by norm_num))

theorem probe_alpha : alpha probeConfig = 1/2 := by
  simp [alpha,probeConfig,probeParams,div_inv_eq_mul,Real.exp_neg,
    Real.exp_log (by norm_num : (0 : ℝ) < 2)]

private theorem exp_left_half :
    Complex.exp (Complex.I * ((Real.pi/2 : ℝ) : ℂ)) = Complex.I := by
  push_cast
  rw [mul_comm]
  exact Complex.exp_pi_div_two_mul_I

private theorem exp_left_neg_half :
    Complex.exp (-(Complex.I * ((Real.pi/2 : ℝ) : ℂ))) = -Complex.I := by
  rw [Complex.exp_neg,exp_left_half]
  simp

private theorem exp_left_neg_pi :
    Complex.exp (Complex.I * ((-Real.pi : ℝ) : ℂ)) = -1 := by
  have he : Complex.I * ((-Real.pi : ℝ) : ℂ) = -((Real.pi : ℂ) * Complex.I) := by
    push_cast
    ring
  rw [he]
  exact Complex.exp_neg_pi_mul_I

private theorem raw_probe_matrix :
    rawInput probeConfig probeAux = ![![1,-Complex.I],![Complex.I,1]] := by
  funext i j
  fin_cases i <;> fin_cases j
  · norm_num [rawInput,probeAux,initialAux,probeConfig,probeTheta]
  · simpa [rawInput,probeAux,initialAux,probeConfig,probeTheta] using exp_left_neg_half
  · simpa [rawInput,probeAux,initialAux,probeConfig,probeTheta] using exp_left_half
  · norm_num [rawInput,probeAux,initialAux,probeConfig,probeTheta]

theorem probe_C_matrix :
    newC probeConfig probeAux = ![![1/2,-Complex.I/2],![Complex.I/2,1/2]] := by
  funext i j
  simp only [newC,probe_alpha,raw_probe_matrix]
  fin_cases i <;> fin_cases j <;>
    norm_num [probeAux,initialAux,zeroC] <;> ring

theorem probe_R_matrix : newR probeConfig probeAux = Capacity.Xo (1/2) := by
  rw [newR,probe_C_matrix]
  funext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [PhaseCoherence.reported,Capacity.Xo,Complex.norm_def,Complex.normSq]

theorem probe_drive_matrix : drive probeConfig probeAux = Capacity.Xo 2 := by
  funext i j
  simp only [drive,probe_R_matrix]
  fin_cases i <;> fin_cases j <;> norm_num [probeConfig,Capacity.Xo]

theorem probe_unprojected : unprojected probeConfig probeAux zeroB = Capacity.Xo 2 := by
  rw [unprojected,probe_drive_matrix]
  funext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [MatrixForm.symM,MatrixForm.clipM,MatrixForm.preM,probeConfig,probeParams,zeroB,Capacity.Xo]

private theorem wrap_two_thirds : Researcher040282.Phase.wrapPhase (2/3) = (2/3 : ℝ) := by
  unfold Researcher040282.Phase.wrapPhase
  have hp : 0 < 2*Real.pi := by positivity
  have hf : Int.floor ((2/3 : ℝ)/(2*Real.pi)) = 0 :=
    Int.floor_eq_zero_iff.mpr ⟨div_nonneg (by norm_num) hp.le,
      (div_lt_one hp).2 (by linarith [Real.two_le_pi])⟩
  rw [hf]
  norm_num

/-- Explicit current/oldest argument probe, not a claimed production trajectory. -/
def readProbe : Aux (Fin 2) 1 :=
  ⟨fun _ => Real.pi/2, fun k => if k.val=0 then (fun _ => 0) else (fun _ => Real.pi/2), zeroC⟩

def offsetConfig : Config (Fin 2) := { probeConfig with omega := fun _ => 1, tau := Real.pi }
def offsetAux : Aux (Fin 2) 1 := initialAux 1 (fun _ => 0) zeroC


set_option linter.unusedSimpArgs false

example : usedIncrement probeConfig probeAux zeroB (Capacity.Xo (2/3)) 0 = 2/3 := by
  norm_num [usedIncrement, sourceIncrement, TrajectorySafety.sineCoupling, probeAux, initialAux, probeTheta, probeConfig, probeParams, Capacity.Xo, zeroB, Fin.sum_univ_two, probe_unprojected]

end Probes
end Finite
end
end AIEFGate.ClosedLoop
