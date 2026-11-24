import AIEFGateCore.EngineStepRef

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
end
end AIEFGate.WindowMax
