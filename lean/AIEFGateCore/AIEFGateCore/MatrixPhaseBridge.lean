/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.EngineStepRef
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Angle

/-!
# Fixed-matrix phase/queue reference and directional derivative (Arena D6)

Research candidate (deposit note: session date 2026-09-11, Atlantic/Reykjavik; the deposit adds
"lead-note date conflicts, see note", but no such note is in the deposited file, so the date is
unverified). A fixed supplied matrix `W` (not clipped or projected here) in the phase head, an
engine-shaped step with queue shift, and the circle bridge under the consistency hypothesis; the
matrix head reduces to the scalar `EngineStepRef.phaseHead` for a uniform zero-diagonal `W`. Not a
formalization of Python, adaptive weights, or a stability theorem. Value probes and `false_*`
witnesses are appended (SPEC §17).

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D6 prerequisite, deposit sha256 `74d44d87…`;
proofs and statements unchanged from the deposit.
-/

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.MatrixPhaseBridge

/-- A fixed post-update matrix W is supplied, not clipped or projected here.
The phase update mirrors aief_experiment_engine_v1.py at main
0a6a2f62ea9af147cac60a7be30d85d6b37fe52a, lines 823 and 830–839. -/
noncomputable def matrixHead (n d : ℕ) (dt omega : ℝ)
    (W : Fin n → Fin n → ℝ) (x : ℕ → Fin n → ℝ) (i : Fin n) : ℝ :=
  x 0 i + dt * (omega + ∑ j : Fin n, W i j * Real.sin (x d j - x 0 i))

/-- Newest-first reference shift, mirroring engine lines 841–844 at the same main. -/
noncomputable def matrixStep (n d : ℕ) (dt omega : ℝ)
    (W : Fin n → Fin n → ℝ) (x : ℕ → Fin n → ℝ) (k : ℕ) (i : Fin n) : ℝ :=
  if k = 0 then matrixHead n d dt omega W x i else x (k - 1) i

/-- Uniform zero-diagonal post-update matrix; this is an assumption rather than
an engine consequence. -/
def Uniform (n : ℕ) (W : Fin n → Fin n → ℝ) (b : ℝ) : Prop :=
  (∀ i, W i i = 0) ∧ (∀ i j, i ≠ j → W i j = b)

/-- The matrix head reduces to main's scalar reference when its off-diagonal
entries equal a nonnegative b and its diagonal is zero. -/
theorem matrix_to_scalar (n d : ℕ) (dt omega b : ℝ)
    (W : Fin n → Fin n → ℝ) (x : ℕ → Fin n → ℝ)
    (hb : 0 ≤ b) (hW : Uniform n W b) (i : Fin n) :
    matrixHead n d dt omega W x i = EngineStepRef.phaseHead n d dt omega b x i := by
  have hs : (∑ j : Fin n, W i j * Real.sin (x d j - x 0 i)) =
      ∑ j ∈ Finset.univ.erase i, b * Real.sin (x d j - x 0 i) := by
    have he := Finset.sum_erase_add Finset.univ
      (fun j => W i j * Real.sin (x d j - x 0 i)) (Finset.mem_univ i)
    calc
      _ = (∑ j ∈ Finset.univ.erase i, W i j * Real.sin (x d j - x 0 i)) +
          W i i * Real.sin (x d i - x 0 i) := he.symm
      _ = _ := by
        rw [hW.1 i, zero_mul, add_zero]
        apply Finset.sum_congr rfl
        intro j hj
        rw [hW.2 i j (Ne.symm (Finset.mem_erase.mp hj).1)]
  simp only [matrixHead, EngineStepRef.phaseHead, EngineStepRef.clippedWeight,
    max_eq_right hb, hs]

/-- Current phase and separate newest-first history, matching engine state
lines 582–598; correspondence with its finite list is not formalized. -/
structure State (n : ℕ) where
  theta : Fin n → ℝ
  history : ℕ → Fin n → ℝ

/-- Exact-real modulo reduction to [0,2π), modeling engine lines 836–839. -/
noncomputable def wrap (x : ℝ) : ℝ := toIcoMod Real.two_pi_pos 0 x

/-- Engine-shaped step for fixed supplied W, with queue shift (lines 841–844). -/
noncomputable def engineStep (n d : ℕ) (dt omega : ℝ)
    (W : Fin n → Fin n → ℝ) (s : State n) : State n :=
  let head := fun i => s.theta i + dt * (omega + ∑ j : Fin n,
    W i j * Real.sin (s.history d j - s.theta i))
  let out := fun i => wrap (head i)
  ⟨out, fun k i => if k = 0 then out i else s.history (k - 1) i⟩

/-- Current and newest-history phases represent the same circle point.
This is not checked by the engine's state validator at lines 613–680. -/
def Consistent (n : ℕ) (s : State n) : Prop :=
  ∀ i, (s.theta i : Real.Angle) = (s.history 0 i : Real.Angle)

/-- Reference view uses current theta at slot 0 and stored history afterwards. -/
def refInput (n : ℕ) (s : State n) (k : ℕ) (i : Fin n) : ℝ :=
  if k = 0 then s.theta i else s.history k i

/-- Without any uniformity assumption, engine-shaped queue coordinates agree
with the matrix reference on the circle under the consistency hypothesis. -/
theorem matrix_circle_bridge (n d k : ℕ) (dt omega : ℝ)
    (W : Fin n → Fin n → ℝ) (s : State n) (hd : 0 < d) (_hk : k ≤ d)
    (hc : Consistent n s) (i : Fin n) :
    ((engineStep n d dt omega W s).history k i : Real.Angle) =
      (matrixStep n d dt omega W (refInput n s) k i : Real.Angle) := by
  by_cases hk : k = 0
  · subst k
    simp only [engineStep, if_true, wrap, Real.Angle.coe_toIcoMod,
      matrixStep, matrixHead, refInput, if_neg (Nat.ne_of_gt hd)]
  · by_cases h1 : k = 1
    · subst k
      simp only [engineStep, if_false, one_ne_zero, Nat.sub_self, matrixStep,
        refInput, if_true]
      exact (hc i).symm
    · have hsub : k - 1 ≠ 0 := by omega
      simp [engineStep, matrixStep, refInput, hk, hsub]

/-- Directional derivative at a synchronized rotating history, with W held
fixed. No symmetry, positivity or zero diagonal is needed for this identity. -/
theorem matrix_head_direction (n d : ℕ) (dt omega Omega theta : ℝ)
    (W : Fin n → Fin n → ℝ) (v : ℕ → Fin n → ℝ) (i : Fin n) :
    HasDerivAt (fun t => matrixHead n d dt omega W
      (EngineStepRef.orbitPath n dt Omega theta v t) i)
      (v 0 i + dt * ∑ j : Fin n,
        W i j * (Real.cos ((d : ℝ) * dt * Omega) * (v d j - v 0 i))) 0 := by
  have hs : HasDerivAt (fun t => ∑ j : Fin n, W i j * Real.sin
      (EngineStepRef.orbitPath n dt Omega theta v t d j -
       EngineStepRef.orbitPath n dt Omega theta v t 0 i))
      (∑ j : Fin n, W i j * (Real.cos ((d : ℝ) * dt * Omega) * (v d j - v 0 i))) 0 := by
    apply HasDerivAt.fun_sum
    intro j hj
    exact (EngineStepRef.neighbor_derivative n d dt Omega theta v i j).const_mul (W i j)
  have hc : HasDerivAt (fun t : ℝ => EngineStepRef.orbitPath n dt Omega theta v t 0 i)
      (v 0 i) 0 := by
    have ht := (hasDerivAt_const (0 : ℝ) theta).fun_add
      ((hasDerivAt_id (0 : ℝ)).mul_const (v 0 i))
    simpa [EngineStepRef.orbitPath] using ht
  have hp := hc.fun_add ((hasDerivAt_const (0 : ℝ) omega).fun_add hs |>.const_mul dt)
  simpa only [matrixHead, zero_add] using hp

/-- Symmetric three-node test matrix with edge weights 1, 2, 3. -/
def probeW (i j : Fin 3) : ℝ :=
  if i = j then 0 else ((i.val + j.val : ℕ) : ℝ)

/-- Only node one's delayed phase is π/2; all other phases are zero. -/
noncomputable def probeX (k : ℕ) (i : Fin 3) : ℝ :=
  if k = 1 ∧ i = 1 then Real.pi / 2 else 0

/-- The six off-diagonal entries have mean 2. -/
theorem probeW_mean : (∑ i : Fin 3, ∑ j : Fin 3, probeW i j) / 6 = 2 := by
  simp only [Fin.sum_univ_three]
  norm_num [probeW, Fin.ext_iff]

/-- Two edge weights are provably unequal. -/
theorem probeW_nonuniform : probeW 0 1 ≠ probeW 0 2 := by
  norm_num [probeW, Fin.ext_iff]

/-- Nonuniform W does not in general reduce to its mean scalar weight. -/
theorem nonuniform_counterexample :
    matrixHead 3 1 1 0 probeW probeX 0 ≠ EngineStepRef.phaseHead 3 1 1 0 2 probeX 0 := by
  norm_num [matrixHead, EngineStepRef.phaseHead, EngineStepRef.clippedWeight,
    probeW, probeX, Fin.sum_univ_three, Fin.ext_iff]

/-- A deliberately inconsistent current phase / newest queue. -/
noncomputable def inconsistent : State 1 := ⟨fun _ => 0, fun _ _ => Real.pi⟩

/-- Consistency cannot be dropped from the circle queue bridge. -/
theorem inconsistent_counterexample :
    ((engineStep 1 1 1 0 (fun _ _ => 0) inconsistent).history 1 0 : Real.Angle) ≠
      (EngineStepRef.phaseStep 1 1 1 0 0 (refInput 1 inconsistent) 1 0 : Real.Angle) := by
  simpa [engineStep, EngineStepRef.phaseStep, refInput, inconsistent] using Real.Angle.pi_ne_zero

/-- Unequal adjacent history values expose a missing or wrong shift. -/
noncomputable def unequalHistory : State 1 :=
  ⟨fun _ => 0, fun k _ => if k = 0 then Real.pi else 0⟩

/-- Direct value probe for the retained shift, independent of derivative lemmas. -/
example : (engineStep 1 1 1 0 (fun _ _ => 0) unequalHistory).history 1 0 = Real.pi ∧
    unequalHistory.history 1 0 = 0 := by
  simp [engineStep, unequalHistory]

/-- Direct delayed-input probe: the other node contributes sin(π/2)=1. -/
example : matrixHead 3 1 1 0 probeW probeX 0 = 1 := by
  norm_num [matrixHead, probeW, probeX, Fin.sum_univ_three, Fin.ext_iff]

#print axioms matrix_to_scalar
#print axioms matrix_circle_bridge
#print axioms matrix_head_direction
#print axioms probeW_mean
#print axioms probeW_nonuniform
#print axioms nonuniform_counterexample
#print axioms inconsistent_counterexample

/-! ### Value probes and negations used by the mutation harness (SPEC §17)

Named versions of the `example` probes above plus two more, evaluated straight from the
definitions. -/

/-- `matrixHead` on `probeW`, `probeX`: only node one's delayed phase `π/2` contributes
`1·sin(π/2)`.
Reading the current slot gives `0`; a reversed sine gives `-1`. -/
theorem probe_matrixHead_value : matrixHead 3 1 1 0 probeW probeX 0 = 1 := by
  norm_num [matrixHead, probeW, probeX, Fin.sum_univ_three, Fin.ext_iff]

/-- The step shifts the queue: new slot 1 is the old slot 0 (`π`), not the old slot 1 (`0`). -/
theorem probe_engineStep_shift :
    (engineStep 1 1 1 0 (fun _ _ => 0) unequalHistory).history 1 0 = Real.pi := by
  simp [engineStep, unequalHistory]

/-- Delayed slot `d = 1` holds `π/2`, current phase `0`, `W = 1`. -/
noncomputable def probeS : State 1 := ⟨fun _ => 0, fun k _ => if k = 1 then Real.pi / 2 else 0⟩

/-- The engine-shaped head reads the delayed slot `d`: `wrap (0 + 1·(0 + sin(π/2))) = 1`.
Reading slot 0 gives `0`. -/
theorem probe_engineStep_head :
    (engineStep 1 1 1 0 (fun _ _ => 1) probeS).theta 0 = 1 := by
  have hp := Real.two_le_pi
  simp only [engineStep, probeS, wrap, Finset.univ_unique, Finset.sum_singleton, if_true,
    sub_zero, Real.sin_pi_div_two, zero_add, mul_one]
  rw [toIcoMod_eq_self]
  constructor <;> linarith

/-- The reference input reads the current phase at slot 0 and stored history afterwards. -/
theorem probe_refInput_values :
    refInput 1 inconsistent 0 0 = 0 ∧ refInput 1 inconsistent 1 0 = Real.pi := by
  constructor <;> simp [refInput, inconsistent]

/-- Dropping consistency from `matrix_circle_bridge` is false (`inconsistent`, `k = 1`). -/
theorem false_bridge_no_consistent :
    ¬ (∀ (n d k : ℕ) (dt omega : ℝ) (W : Fin n → Fin n → ℝ) (s : State n) (_hd : 0 < d)
      (_hk : k ≤ d) (_hc : True) (i : Fin n),
      ((engineStep n d dt omega W s).history k i : Real.Angle) =
        (matrixStep n d dt omega W (refInput n s) k i : Real.Angle)) := by
  intro H
  have h := H 1 1 1 1 0 (fun _ _ => 0) inconsistent one_pos le_rfl trivial 0
  simp only [engineStep, matrixStep, refInput, inconsistent, one_ne_zero, if_false,
    Nat.sub_self, if_true] at h
  exact Real.Angle.pi_ne_zero (by simpa using h)

/-- Dropping uniformity from `matrix_to_scalar` is false (`probeW`, mean weight `2`). -/
theorem false_scalar_no_uniform :
    ¬ (∀ (n d : ℕ) (dt omega b : ℝ) (W : Fin n → Fin n → ℝ) (x : ℕ → Fin n → ℝ)
      (_hb : 0 ≤ b) (_hW : True) (i : Fin n),
      matrixHead n d dt omega W x i = EngineStepRef.phaseHead n d dt omega b x i) := by
  intro H
  exact nonuniform_counterexample (H 3 1 1 0 2 probeW probeX (by norm_num) trivial 0)

/-- Dropping the factor `cos (d·dt·Ω)` from `matrix_head_direction` is false (`n = d = dt = 1`,
`Ω = π`, `W = 1`, `v = (0, 1)`: derivative `-1`, not `1`; derivatives are unique). Audit note N5. -/
theorem false_head_direction_no_cos :
    ¬ (∀ (n d : ℕ) (dt omega Omega theta : ℝ) (W : Fin n → Fin n → ℝ) (v : ℕ → Fin n → ℝ)
      (i : Fin n),
      HasDerivAt (fun t => matrixHead n d dt omega W
        (EngineStepRef.orbitPath n dt Omega theta v t) i)
        (v 0 i + dt * ∑ j : Fin n, W i j * (v d j - v 0 i)) 0) := by
  intro H
  have h1 := H 1 1 1 0 Real.pi 0 (fun _ _ => 1) (fun k _ => if k = 0 then 0 else 1) 0
  have h2 := matrix_head_direction 1 1 1 0 Real.pi 0 (fun _ _ => 1)
    (fun k _ => if k = 0 then 0 else 1) 0
  have h := h1.unique h2
  norm_num [Real.cos_pi] at h

#print axioms false_head_direction_no_cos
#print axioms probe_matrixHead_value
#print axioms probe_engineStep_shift
#print axioms probe_engineStep_head
#print axioms probe_refInput_values
#print axioms false_bridge_no_consistent
#print axioms false_scalar_no_uniform


end AIEFGate.MatrixPhaseBridge
