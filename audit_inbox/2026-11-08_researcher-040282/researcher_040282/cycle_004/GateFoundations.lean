import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.Field.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.NormNum

/-!
Finite post-positivity capacity-map foundations.

Scope: exact real arithmetic. The activation guard is part of the definition.
No statement here concerns the complete adaptive phase/EMA/delay evolution or
rounding behavior. Nonnegative node-dependent capacities generalize the uniform
capacity used by the engine. Rational examples below are exact counterexamples.
-/

set_option autoImplicit false

noncomputable section
open scoped BigOperators

namespace Researcher040282

variable {ι : Type*} [Fintype ι]

abbrev Weights (ι : Type*) := ι → ι → ℝ

def rowSum (W : Weights ι) (i : ι) : ℝ := ∑ j, W i j

def nodeScale (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i : ι) : ℝ :=
  min 1 (c i / (rowSum W i + ε))

def kernel (c : ι → ℝ) (ε : ℝ) (W : Weights ι) : Weights ι :=
  fun i j => W i j * min (nodeScale c ε W i) (nodeScale c ε W j)

def feasible (c : ι → ℝ) (W : Weights ι) : Prop :=
  ∀ i, rowSum W i ≤ c i

def gate (c : ι → ℝ) (ε : ℝ) (W : Weights ι) : Weights ι := by
  classical
  exact if feasible c W then W else kernel c ε W

def appliedFactor (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i j : ι) : ℝ := by
  classical
  exact if feasible c W then 1 else min (nodeScale c ε W i) (nodeScale c ε W j)

theorem rowSum_nonneg (W : Weights ι) (hW : ∀ i j, 0 ≤ W i j) (i : ι) :
    0 ≤ rowSum W i := by
  exact Finset.sum_nonneg (fun j _ => hW i j)

theorem nodeScale_nonneg (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) (i : ι) :
    0 ≤ nodeScale c ε W i := by
  apply le_min zero_le_one
  exact div_nonneg (hc i) (le_of_lt (add_pos_of_nonneg_of_pos (rowSum_nonneg W hW i) hε))

theorem nodeScale_le_one (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i : ι) :
    nodeScale c ε W i ≤ 1 :=
  min_le_left _ _

theorem kernel_nonneg (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) :
    ∀ i j, 0 ≤ kernel c ε W i j := by
  intro i j
  exact mul_nonneg (hW i j)
    (le_min (nodeScale_nonneg c ε W hc hε hW i) (nodeScale_nonneg c ε W hc hε hW j))

theorem kernel_le_input (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i j, 0 ≤ W i j) (i j : ι) :
    kernel c ε W i j ≤ W i j := by
  calc
    kernel c ε W i j ≤ W i j * 1 :=
      mul_le_mul_of_nonneg_left
        (le_trans (min_le_left _ _) (nodeScale_le_one c ε W i)) (hW i j)
    _ = W i j := mul_one _

theorem kernel_symmetric (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i j, W i j = W j i) :
    ∀ i j, kernel c ε W i j = kernel c ε W j i := by
  intro i j
  unfold kernel
  rw [hW i j, min_comm]

theorem kernel_zero_diag (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i, W i i = 0) :
    ∀ i, kernel c ε W i i = 0 := by
  intro i
  simp only [kernel, hW i, zero_mul]

theorem kernel_row_lower (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (ℓ : ℝ)
    (hW : ∀ i j, 0 ≤ W i j) (hℓ : ∀ i, ℓ ≤ nodeScale c ε W i) (i : ι) :
    ℓ * rowSum W i ≤ rowSum (kernel c ε W) i := by
  unfold rowSum kernel
  rw [Finset.mul_sum]
  apply Finset.sum_le_sum
  intro j _
  simpa only [mul_comm] using
    mul_le_mul_of_nonneg_left (le_min (hℓ i) (hℓ j)) (hW i j)

theorem kernel_row_upper (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i j, 0 ≤ W i j) (i : ι) :
    rowSum (kernel c ε W) i ≤ nodeScale c ε W i * rowSum W i := by
  unfold rowSum kernel
  rw [Finset.mul_sum]
  apply Finset.sum_le_sum
  intro j _
  simpa only [mul_comm] using mul_le_mul_of_nonneg_left
    (min_le_left (nodeScale c ε W i) (nodeScale c ε W j)) (hW i j)

theorem kernel_feasible (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) :
    feasible c (kernel c ε W) := by
  intro i
  have hr : 0 ≤ rowSum W i := rowSum_nonneg W hW i
  have hd : 0 < rowSum W i + ε := add_pos_of_nonneg_of_pos hr hε
  calc
    rowSum (kernel c ε W) i ≤ nodeScale c ε W i * rowSum W i :=
      kernel_row_upper c ε W hW i
    _ ≤ (c i / (rowSum W i + ε)) * rowSum W i :=
      mul_le_mul_of_nonneg_right (min_le_right _ _) hr
    _ ≤ (c i / (rowSum W i + ε)) * (rowSum W i + ε) :=
      mul_le_mul_of_nonneg_left (le_add_of_nonneg_right (le_of_lt hε))
        (div_nonneg (hc i) (le_of_lt hd))
    _ = c i := div_mul_cancel₀ _ (ne_of_gt hd)

theorem gate_fixes_feasible (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : feasible c W) : gate c ε W = W := by
  classical
  simp only [gate, if_pos hW]

theorem gate_feasible (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) :
    feasible c (gate c ε W) := by
  classical
  by_cases hf : feasible c W
  · simpa only [gate, if_pos hf] using hf
  · simpa only [gate, if_neg hf] using kernel_feasible c ε W hc hε hW

theorem gate_idempotent (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) :
    gate c ε (gate c ε W) = gate c ε W :=
  gate_fixes_feasible c ε (gate c ε W) (gate_feasible c ε W hc hε hW)

theorem gate_nonneg (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) :
    ∀ i j, 0 ≤ gate c ε W i j := by
  classical
  by_cases hf : feasible c W
  · simpa only [gate, if_pos hf] using hW
  · simpa only [gate, if_neg hf] using kernel_nonneg c ε W hc hε hW

theorem gate_symmetric (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i j, W i j = W j i) :
    ∀ i j, gate c ε W i j = gate c ε W j i := by
  classical
  by_cases hf : feasible c W
  · simpa only [gate, if_pos hf] using hW
  · simpa only [gate, if_neg hf] using kernel_symmetric c ε W hW

theorem gate_zero_diag (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i, W i i = 0) :
    ∀ i, gate c ε W i i = 0 := by
  classical
  by_cases hf : feasible c W
  · simpa only [gate, if_pos hf] using hW
  · simpa only [gate, if_neg hf] using kernel_zero_diag c ε W hW

theorem scale_eq_of_rowSum_eq (c : ι → ℝ) (ε : ℝ) (U W : Weights ι)
    (h : ∀ i, rowSum U i = rowSum W i) (i : ι) :
    nodeScale c ε U i = nodeScale c ε W i := by
  rw [nodeScale, nodeScale, h i]

theorem gate_difference_of_rowSum_eq (c : ι → ℝ) (ε : ℝ) (U W : Weights ι)
    (h : ∀ i, rowSum U i = rowSum W i) (i j : ι) :
    gate c ε U i j - gate c ε W i j =
      (U i j - W i j) * appliedFactor c ε W i j := by
  classical
  have hiff : feasible c U ↔ feasible c W := by
    simp only [feasible, h]
  by_cases hw : feasible c W
  · have hu : feasible c U := hiff.mpr hw
    simp only [gate, appliedFactor, if_pos hu, if_pos hw, mul_one]
  · have hu : ¬ feasible c U := fun hh => hw (hiff.mp hh)
    simp only [gate, appliedFactor, if_neg hu, if_neg hw, kernel]
    rw [scale_eq_of_rowSum_eq c ε U W h i, scale_eq_of_rowSum_eq c ε U W h j]
    exact (sub_mul _ _ _).symm

-- Exact scalar restrictions of a single-edge example, embeddable in 12 nodes.
def ratKernel (c ε x : ℚ) : ℚ := x * min 1 (c / (x + ε))
def ratGate (c ε x : ℚ) : ℚ := if x ≤ c then x else ratKernel c ε x

theorem rat_guard_fixes_boundary :
    ratGate (19/30) (1/1000000000000) (19/30) = (19/30) := by
  norm_num [ratGate]

theorem rat_kernel_not_idempotent :
    ratKernel (19/30) (1/1000000000000)
      (ratKernel (19/30) (1/1000000000000) (19/30)) ≠
      ratKernel (19/30) (1/1000000000000) (19/30) := by
  norm_num [ratKernel]

theorem rat_gate_not_nonexpansive :
    |ratGate (19/30) (1/1000000000000) ((19/30)+(1/2000000000000)) -
      ratGate (19/30) (1/1000000000000) (19/30)| >
      |((19/30)+(1/2000000000000):ℚ) - (19/30)| := by
  norm_num [ratGate, ratKernel]

theorem rat_negative_epsilon_breaks_capacity :
    ratGate 1 (-1/2) (3/2) > (1:ℚ) := by
  norm_num [ratGate, ratKernel]

end Researcher040282

#print axioms Researcher040282.rowSum_nonneg
#print axioms Researcher040282.nodeScale_nonneg
#print axioms Researcher040282.nodeScale_le_one
#print axioms Researcher040282.kernel_nonneg
#print axioms Researcher040282.kernel_le_input
#print axioms Researcher040282.kernel_symmetric
#print axioms Researcher040282.kernel_zero_diag
#print axioms Researcher040282.kernel_row_lower
#print axioms Researcher040282.kernel_row_upper
#print axioms Researcher040282.kernel_feasible
#print axioms Researcher040282.gate_fixes_feasible
#print axioms Researcher040282.gate_feasible
#print axioms Researcher040282.gate_idempotent
#print axioms Researcher040282.gate_nonneg
#print axioms Researcher040282.gate_symmetric
#print axioms Researcher040282.gate_zero_diag
#print axioms Researcher040282.scale_eq_of_rowSum_eq
#print axioms Researcher040282.gate_difference_of_rowSum_eq
#print axioms Researcher040282.rat_guard_fixes_boundary
#print axioms Researcher040282.rat_kernel_not_idempotent
#print axioms Researcher040282.rat_gate_not_nonexpansive
#print axioms Researcher040282.rat_negative_epsilon_breaks_capacity
