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
  sourceIncrement c a Bnew

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

/-- Held source-order interface to the ACTUAL current-main matrix operator. -/
theorem weights_succ (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) :
    BTrace c d theta0 C0 B0 (n + 1) =
      MatrixForm.stepM c.gate
        (PhaseCoherence.sourceDrive c.eta c.mu (newC c (auxTrace c d theta0 C0 B0 n)))
        (BTrace c d theta0 C0 B0 n) := by rfl

theorem theta_succ (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) (i : V) :
    thetaTrace c d theta0 C0 B0 (n + 1) i =
      Researcher040282.Phase.wrapPhase (thetaTrace c d theta0 C0 B0 n i +
        incrementTrace c d theta0 C0 B0 n i) := by rfl

theorem history_succ (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) :
    (auxTrace c d theta0 C0 B0 (n + 1)).history =
      Researcher040282.Delay.shiftAppend d (auxTrace c d theta0 C0 B0 n).history
        (thetaTrace c d theta0 C0 B0 (n + 1)) := by rfl

theorem coherence_succ (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) :
    (auxTrace c d theta0 C0 B0 (n + 1)).C = newC c (auxTrace c d theta0 C0 B0 n) := by rfl

/-- Actual model theta satisfies011's trace with its actual generated increments. -/
theorem theta_eq_phaseTrace (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) : ∀ n,
    thetaTrace c d theta0 C0 B0 n =
      Researcher040282.Phase.phaseTrace theta0 (incrementTrace c d theta0 C0 B0) n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
      funext i
      rw [theta_succ]
      change Researcher040282.Phase.wrapPhase (thetaTrace c d theta0 C0 B0 n i + _) =
        Researcher040282.Phase.wrapPhase (Researcher040282.Phase.phaseTrace theta0 (incrementTrace c d theta0 C0 B0) n i + _)
      rw [ih]

/-- History is proved reachable along THIS coupled recursion, not assumed so. -/
theorem history_eq_historyTrace (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) : ∀ n,
    (auxTrace c d theta0 C0 B0 n).history =
      Researcher040282.Delay.historyTrace d (thetaTrace c d theta0 C0 B0) n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
      rw [history_succ, ih]
      rfl

theorem oldest_correct (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) :
    (auxTrace c d theta0 C0 B0 n).history ⟨0,Nat.zero_lt_succ d⟩ =
      thetaTrace c d theta0 C0 B0 (n - d) := by
  rw [history_eq_historyTrace, Researcher040282.Delay.historyTrace_oldest]

theorem newest_correct (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) :
    (auxTrace c d theta0 C0 B0 n).history ⟨d,Nat.lt_succ_self d⟩ =
      thetaTrace c d theta0 C0 B0 n := by
  rw [history_eq_historyTrace, Researcher040282.Delay.historyTrace_newest]

/-- The actual state read equals the accepted011input, not a supplied arbitrary z. -/
theorem actual_input_eq_phasor (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) (i j : V) :
    rawInput c (auxTrace c d theta0 C0 B0 n) i j =
      Researcher040282.Phase.inputPhasor d theta0 (incrementTrace c d theta0 C0 B0) c.omega c.tau n i j := by
  simp only [rawInput, Researcher040282.Phase.inputPhasor, Researcher040282.Phase.phasor,
    Researcher040282.Delay.historyTrace_oldest]
  rw [oldest_correct]
  change Complex.exp (Complex.I * ((thetaTrace c d theta0 C0 B0 n i - thetaTrace c d theta0 C0 B0 (n-d) j - _ : ℝ) : ℂ)) = _
  rw [theta_eq_phaseTrace, theta_eq_phaseTrace]
  rw [mul_comm]

theorem newC_eq_phaseStep (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (n : ℕ) :
    newC c (auxTrace c d theta0 C0 B0 n) =
      PhaseCoherence.coherenceStep (alpha c) (auxTrace c d theta0 C0 B0 n).C
        d theta0 (incrementTrace c d theta0 C0 B0) c.omega c.tau n := by
  funext i j
  simp only [newC, PhaseCoherence.coherenceStep, PhaseCoherence.coherenceInput]
  rw [actual_input_eq_phasor]

/-- Actual coupled C trajectory is now connected to013, not an arbitrary input. -/
theorem coherence_eq_phaseTrace (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) : ∀ n,
    (auxTrace c d theta0 C0 B0 n).C =
      PhaseCoherence.coherenceTrace (alpha c) C0 d theta0 (incrementTrace c d theta0 C0 B0) c.omega c.tau n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
      rw [coherence_succ, newC_eq_phaseStep, ih]
      rfl

theorem actual_B_structural (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (hc : 0 ≤ c.gate.cap) (he : 0 ≤ c.gate.ε)
    (hB0 : TrajectorySafety.Structural B0) (n : ℕ) :
    TrajectorySafety.Structural (BTrace c d theta0 C0 B0 n) :=
  TrajectorySafety.all_times_structural (fun _ => c.gate) (prepareDrive c) (updateAux c)
    (initialAux d theta0 C0,B0) (fun _ => hc) (fun _ => he) hB0 n

theorem actual_B_capacity (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (hp : EngineGate c.gate) (n : ℕ) (i : V) :
    Capacity.rowS (BTrace c d theta0 C0 B0 (n + 1)) i ≤ c.gate.cap :=
  TrajectorySafety.fixed_parameter_capacity c.gate hp (prepareDrive c) (updateAux c)
    (initialAux d theta0 C0,B0) n i

theorem actual_C_unitDisk (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (hdt : 0 ≤ c.gate.dt) (hTw : 0 < c.Tw)
    (hC0 : ∀ i j, ‖C0 i j‖ ≤ 1) (n : ℕ) (i j : V) :
    ‖(auxTrace c d theta0 C0 B0 n).C i j‖ ≤ 1 := by
  rw [coherence_eq_phaseTrace]
  exact PhaseCoherence.coherenceTrace_unitDisk (alpha c) C0 d theta0
    (incrementTrace c d theta0 C0 B0) c.omega c.tau (alpha_pos c).le
    (alpha_le_one c hdt hTw) hC0 n i j

theorem actual_reported_R_range (c : Config V) (d : ℕ) (theta0 : V → ℝ) (C0 : V → V → ℂ)
    (B0 : TrajectorySafety.Weights V) (hdt : 0 ≤ c.gate.dt) (hTw : 0 < c.Tw)
    (hC0 : ∀ i j, ‖C0 i j‖ ≤ 1) (n : ℕ) (i j : V) :
    0 ≤ newR c (auxTrace c d theta0 C0 B0 n) i j ∧
      newR c (auxTrace c d theta0 C0 B0 n) i j ≤ 1 := by
  change 0 ≤ PhaseCoherence.reported (newC c (auxTrace c d theta0 C0 B0 n)) i j ∧ _
  rw [← coherence_succ]
  exact PhaseCoherence.reported_bounds _ (actual_C_unitDisk c d theta0 C0 B0 hdt hTw hC0 (n+1)) i j

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
    Complex.exp (Complex.I * ((-Real.pi/2 : ℝ) : ℂ)) = -Complex.I := by
  have he : Complex.I * ((-Real.pi/2 : ℝ) : ℂ) = -((Real.pi : ℂ)/2 * Complex.I) := by
    push_cast
    ring
  rw [he]
  exact Complex.exp_neg_pi_div_two_mul_I

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

theorem probe_B_new : BTrace probeConfig 1 probeTheta zeroC zeroB 1 = Capacity.Xo (2/3) := by
  change MatrixForm.stepM probeConfig.gate (drive probeConfig probeAux) zeroB = _
  rw [Capacity.stepM_eq_gateM]
  change Capacity.gateM probeConfig.gate (unprojected probeConfig probeAux zeroB) = _
  rw [probe_unprojected]
  rw [Capacity.gateM_Xo_of_gt probeConfig.gate probe_gate_valid (by norm_num [probeConfig,probeParams])]
  norm_num [scale,probeConfig,probeParams]

theorem probe_increment_generated : incrementTrace probeConfig 1 probeTheta zeroC zeroB 0 0 = 2/3 := by
  change sourceIncrement probeConfig probeAux (BTrace probeConfig 1 probeTheta zeroC zeroB 1) 0 = _
  rw [probe_B_new]
  norm_num [sourceIncrement,TrajectorySafety.sineCoupling,probeAux,initialAux,probeTheta,probeConfig,probeParams,Capacity.Xo,Fin.sum_univ_two]

theorem probe_increment_used :
    usedIncrement probeConfig probeAux zeroB (BTrace probeConfig 1 probeTheta zeroC zeroB 1) 0 = 2/3 := by
  change sourceIncrement probeConfig probeAux (BTrace probeConfig 1 probeTheta zeroC zeroB 1) 0 = _
  exact probe_increment_generated

theorem old_B_increment_zero : sourceIncrement probeConfig probeAux zeroB 0 = 0 := by
  norm_num [sourceIncrement,TrajectorySafety.sineCoupling,probeConfig,probeParams,zeroB]

theorem unprojected_increment_two :
    sourceIncrement probeConfig probeAux (unprojected probeConfig probeAux zeroB) 0 = 2 := by
  rw [probe_unprojected]
  norm_num [sourceIncrement,TrajectorySafety.sineCoupling,probeAux,initialAux,probeTheta,probeConfig,probeParams,Capacity.Xo,Fin.sum_univ_two]

private theorem wrap_two_thirds : Researcher040282.Phase.wrapPhase (2/3) = (2/3 : ℝ) := by
  unfold Researcher040282.Phase.wrapPhase
  have hp : 0 < 2*Real.pi := by positivity
  have hf : Int.floor ((2/3 : ℝ)/(2*Real.pi)) = 0 :=
    Int.floor_eq_zero_iff.mpr ⟨div_nonneg (by norm_num) hp.le,
      (div_lt_one hp).2 (by linarith [Real.two_le_pi])⟩
  rw [hf]
  norm_num

theorem probe_theta_new : thetaTrace probeConfig 1 probeTheta zeroC zeroB 1 0 = 2/3 := by
  rw [theta_succ,probe_increment_generated]
  change Researcher040282.Phase.wrapPhase (0 + 2/3) = _
  simpa using wrap_two_thirds

theorem probe_history_newest :
    (auxTrace probeConfig 1 probeTheta zeroC zeroB 1).history ⟨1,by decide⟩ 0 = 2/3 := by
  have h := congrFun (newest_correct probeConfig 1 probeTheta zeroC zeroB 1) (0 : Fin 2)
  exact h.trans probe_theta_new

/-- Explicit current/oldest argument probe, not a claimed production trajectory. -/
def readProbe : Aux (Fin 2) 1 :=
  ⟨fun _ => Real.pi/2, fun k => if k.val=0 then (fun _ => 0) else (fun _ => Real.pi/2), zeroC⟩

theorem probe_oldest_input : rawInput probeConfig readProbe 0 1 = Complex.I := by
  simpa [rawInput,probeConfig,readProbe] using exp_left_half

def offsetConfig : Config (Fin 2) := { probeConfig with omega := fun _ => 1, tau := Real.pi }
def offsetAux : Aux (Fin 2) 1 := initialAux 1 (fun _ => 0) zeroC

theorem probe_frequency_offset : rawInput offsetConfig offsetAux 0 1 = -1 := by
  simpa [rawInput,offsetConfig,offsetAux,initialAux] using exp_left_neg_pi

end Probes

end Finite
end
end AIEFGate.ClosedLoop

#print axioms AIEFGate.ClosedLoop.delay_positive
#print axioms AIEFGate.ClosedLoop.alpha_pos
#print axioms AIEFGate.ClosedLoop.alpha_le_one
#print axioms AIEFGate.ClosedLoop.weights_succ
#print axioms AIEFGate.ClosedLoop.theta_succ
#print axioms AIEFGate.ClosedLoop.history_succ
#print axioms AIEFGate.ClosedLoop.coherence_succ
#print axioms AIEFGate.ClosedLoop.theta_eq_phaseTrace
#print axioms AIEFGate.ClosedLoop.history_eq_historyTrace
#print axioms AIEFGate.ClosedLoop.oldest_correct
#print axioms AIEFGate.ClosedLoop.newest_correct
#print axioms AIEFGate.ClosedLoop.actual_input_eq_phasor
#print axioms AIEFGate.ClosedLoop.newC_eq_phaseStep
#print axioms AIEFGate.ClosedLoop.coherence_eq_phaseTrace
#print axioms AIEFGate.ClosedLoop.actual_B_structural
#print axioms AIEFGate.ClosedLoop.actual_B_capacity
#print axioms AIEFGate.ClosedLoop.actual_C_unitDisk
#print axioms AIEFGate.ClosedLoop.actual_reported_R_range

#print axioms AIEFGate.ClosedLoop.probe_gate_valid

#print axioms AIEFGate.ClosedLoop.probe_delay_valid

#print axioms AIEFGate.ClosedLoop.probe_Tw_positive

#print axioms AIEFGate.ClosedLoop.probe_alpha

#print axioms AIEFGate.ClosedLoop.probe_C_matrix

#print axioms AIEFGate.ClosedLoop.probe_R_matrix

#print axioms AIEFGate.ClosedLoop.probe_drive_matrix

#print axioms AIEFGate.ClosedLoop.probe_unprojected

#print axioms AIEFGate.ClosedLoop.probe_B_new

#print axioms AIEFGate.ClosedLoop.probe_increment_generated

#print axioms AIEFGate.ClosedLoop.probe_increment_used

#print axioms AIEFGate.ClosedLoop.old_B_increment_zero

#print axioms AIEFGate.ClosedLoop.unprojected_increment_two

#print axioms AIEFGate.ClosedLoop.probe_theta_new

#print axioms AIEFGate.ClosedLoop.probe_history_newest

#print axioms AIEFGate.ClosedLoop.probe_oldest_input

#print axioms AIEFGate.ClosedLoop.probe_frequency_offset
