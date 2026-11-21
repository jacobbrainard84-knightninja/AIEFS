/- SPDX-License-Identifier: Apache-2.0
Research candidate: fixed-matrix phase/queue reference and directional derivative.
Session date: 2026-09-11 Atlantic/Reykjavik; lead-note date conflicts, see note.
Not a formalization of Python, adaptive weights, or a stability theorem. -/
import AIEFGateCore.EngineStepRef
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Angle

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

end AIEFGate.MatrixPhaseBridge
