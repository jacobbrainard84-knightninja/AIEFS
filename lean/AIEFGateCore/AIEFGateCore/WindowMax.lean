/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH; candidate by Arena_Researcher_06020041 (audit-inbox 41335f0)
-/
import AIEFGateCore.EngineStepRef

/-!
# Window max-norm invariant for mean-zero modes (Arena D15)

Research candidate. For a mean-zero spatial mode the linearised `EngineStepRef.phaseStep` acts on
the window by `next` (`reference_link`); for `N ≥ 2` and `0 ≤ c ≤ 2/N` (`c = dt·b`) no window slot
can grow, for all time. Above the threshold (`N = 3`, `d = 1`, `2/3 < c < 1`) one step grows. Only
mean-zero modes: complementary to `HeteroStepRef`, see SPEC §17. Value probe and `false_*`
witnesses appended.

Source: audit-inbox `41335f0` MERGE_MANIFEST, verdict D15, deposit sha256 `5d91183b…`; proofs and
statements unchanged from the deposit.
-/

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.WindowMax
open AIEFGate.EngineStepRef
noncomputable section

/-- A scalar mean-zero spatial mode with window entries indexed by age. -/
def next (n d : ℕ) (c : ℝ) (v : ℕ → ℝ) (k : ℕ) : ℝ :=
  if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - c * v d else v (k - 1)

def iter (n d : ℕ) (c : ℝ) (v : ℕ → ℝ) : ℕ → (ℕ → ℝ)
  | 0 => v
  | k + 1 => next n d c (iter n d c v k)

/-- General N,d head and every copied history slot, linked to main. -/
theorem reference_link (n d : ℕ) (dt b : ℝ) (hn : 1 ≤ n) (hb : 0 < b)
    (mode : Fin n → ℝ) (hm : ∑ j : Fin n, mode j = 0)
    (v : ℕ → ℝ) (i : Fin n) (k : ℕ) :
    HasDerivAt (fun t => phaseStep n d dt 0 b
      (orbitPath n dt 0 1 (fun a j => v a * mode j) t) k i)
      (next n d (dt * b) v k * mode i) 0 := by
  by_cases hk : k = 0
  · subst k
    have hs : (∑ j : Fin n, v d * mode j) = 0 := by
      rw [← Finset.mul_sum, hm, mul_zero]
    have hh := phase_step_head n d dt 0 b 0 1 hn hb (fun a j => v a * mode j) i
    convert hh using 1
    simp [next, hs]
    ring
  · have hh := history_derivative n d k dt 0 b 0 1 (Nat.pos_of_ne_zero hk)
      (fun a j => v a * mode j) i
    simpa [next, hk] using hh

/-- The sharp row-sum bound when N≥2 and 0≤c≤2/N. -/
theorem coefficient_bound (n : ℕ) (c : ℝ) (hn : 2 ≤ n)
    (hc : 0 ≤ c) (ht : (n : ℝ) * c ≤ 2) :
    |1 - ((n : ℝ) - 1) * c| + c ≤ 1 := by
  have hn' : (2 : ℝ) ≤ n := by exact_mod_cast hn
  have hh : |1 - ((n : ℝ) - 1) * c| ≤ 1 - c := by
    rw [abs_le]
    constructor <;> nlinarith
  linarith

/-- A single window update cannot enlarge any component. -/
theorem window_step (n d : ℕ) (c M : ℝ) (v : ℕ → ℝ)
    (hn : 2 ≤ n) (hc : 0 ≤ c) (ht : (n : ℝ) * c ≤ 2)
    (hM : 0 ≤ M) (hv : ∀ k, k ≤ d → |v k| ≤ M) :
    ∀ k, k ≤ d → |next n d c v k| ≤ M := by
  intro k hk
  by_cases h : k = 0
  · subst k
    simp only [next, if_true]
    calc
      |(1 - ((n : ℝ) - 1) * c) * v 0 - c * v d| ≤
          |1 - ((n : ℝ) - 1) * c| * |v 0| + c * |v d| := by
            simpa [abs_mul, abs_of_nonneg hc] using
              (abs_sub ((1 - ((n : ℝ) - 1) * c) * v 0) (c * v d))
      _ ≤ (|1 - ((n : ℝ) - 1) * c| + c) * M := by
            nlinarith [mul_nonneg (abs_nonneg (1 - ((n : ℝ) - 1) * c))
              (sub_nonneg.mpr (hv 0 (Nat.zero_le d))),
              mul_nonneg hc (sub_nonneg.mpr (hv d (le_refl d)))]
      _ ≤ 1 * M := mul_le_mul_of_nonneg_right (coefficient_bound n c hn hc ht) hM
      _ = M := one_mul M
  · have hk' : k - 1 ≤ d := le_trans (Nat.sub_le k 1) hk
    simpa [next, h] using hv (k - 1) hk'

/-- All times, all retained slots: same initial window cap M. -/
theorem window_all_steps (n d : ℕ) (c M : ℝ) (v : ℕ → ℝ)
    (hn : 2 ≤ n) (hc : 0 ≤ c) (ht : (n : ℝ) * c ≤ 2)
    (hM : 0 ≤ M) (hv : ∀ k, k ≤ d → |v k| ≤ M) :
    ∀ t k, k ≤ d → |iter n d c v t k| ≤ M := by
  intro t
  induction t with
  | zero => simpa [iter] using hv
  | succ t ih => exact window_step n d c M (iter n d c v t) hn hc ht hM ih

/-- Above the threshold for N=3,d=1, signs (1,1) realize the exact row sum. -/
theorem exact_growth_witness (c : ℝ) (hc : (2 / 3 : ℝ) < c) (hc1 : c < 1) :
    let v : ℕ → ℝ := fun _ => 1
    |next 3 1 c v 0| = 3 * c - 1 ∧
    |next 3 1 c v 0| > 1 ∧
    ∀ k, k ≤ 1 → |v k| ≤ 1 := by
  dsimp
  have hneg : 1 - 3 * c < 0 := by linarith
  simp only [next, if_true, Nat.cast_ofNat]
  have heq : (1 - ((3 : ℝ) - 1) * c) * 1 - c * 1 = 1 - 3 * c := by ring
  rw [heq, abs_of_neg hneg]
  constructor
  · ring
  constructor
  · linarith
  · intro k hk
    norm_num

#print axioms reference_link
#print axioms coefficient_bound
#print axioms window_step
#print axioms window_all_steps
#print axioms exact_growth_witness

/-! ### Value probes and negations used by the mutation harness (SPEC §17)

The probe evaluates `next` at closed numbers straight from its definition, so a mutated `next` fails
here and not only in a rewrite lemma. Each `false_*` theorem refutes a weakened statement. -/

/-- `next 3 1 (1/4)` on the window `(1, 4)`: head `(1 - 2/4)·1 - (1/4)·4 = -1/2`; slot 1 copies
slot 0. The head coefficient `n` instead of `n - 1` gives `-3/4`, `+ c·v d` gives `3/2`, reading
slot 0
instead of `d` gives `1/4`, and an unshifted slot 1 gives `4`. -/
theorem probe_next_values :
    next 3 1 (1/4) (fun k => if k = 0 then 1 else 4) 0 = -1/2 ∧
      next 3 1 (1/4) (fun k => if k = 0 then 1 else 4) 1 = 1 := by
  constructor <;> norm_num [next]

/-- Dropping `n·c ≤ 2` from `window_step` is false (`N = 3`, `d = 1`, `c = 4/5`, `v = 1`). -/
theorem false_window_step_no_threshold :
    ¬ (∀ (n d : ℕ) (c M : ℝ) (v : ℕ → ℝ) (_hn : 2 ≤ n) (_hc : 0 ≤ c) (_ht : True)
      (_hM : 0 ≤ M) (_hv : ∀ k, k ≤ d → |v k| ≤ M), ∀ k, k ≤ d → |next n d c v k| ≤ M) := by
  intro H
  have h := H 3 1 (4/5) 1 (fun _ => 1) (by norm_num) (by norm_num) trivial (by norm_num)
    (fun _ _ => by norm_num) 0 (by norm_num)
  norm_num [next, abs_le] at h

/-- Dropping `n·c ≤ 2` from `window_all_steps` is false (same instance, `t = 1`). -/
theorem false_window_all_no_threshold :
    ¬ (∀ (n d : ℕ) (c M : ℝ) (v : ℕ → ℝ) (_hn : 2 ≤ n) (_hc : 0 ≤ c) (_ht : True)
      (_hM : 0 ≤ M) (_hv : ∀ k, k ≤ d → |v k| ≤ M), ∀ t k, k ≤ d → |iter n d c v t k| ≤ M) := by
  intro H
  have h := H 3 1 (4/5) 1 (fun _ => 1) (by norm_num) (by norm_num) trivial (by norm_num)
    (fun _ _ => by norm_num) 1 0 (by norm_num)
  norm_num [iter, next, abs_le] at h

/-- Dropping `2 ≤ n` from `coefficient_bound` is false (`n = 1`, `c = 1`: `1 + 1 > 1`). -/
theorem false_coefficient_no_size :
    ¬ (∀ (n : ℕ) (c : ℝ) (_hn : True) (_hc : 0 ≤ c) (_ht : (n : ℝ) * c ≤ 2),
      |1 - ((n : ℝ) - 1) * c| + c ≤ 1) := by
  intro H
  have h := H 1 1 trivial (by norm_num) (by norm_num)
  norm_num at h

#print axioms probe_next_values
#print axioms false_window_step_no_threshold
#print axioms false_window_all_no_threshold
#print axioms false_coefficient_no_size

end
end AIEFGate.WindowMax
