/- SPDX-License-Identifier: Apache-2.0
Complete-graph node sums commute with the stipulated scalar queue map.
Not an engine derivative proof. -/
import AIEFGateCore.QueueNeutral
import Mathlib.Algebra.BigOperators.Ring.Finset

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.NodeQueueNeutral

structure State (n : ℕ) where
  history : ℕ → Fin n → ℝ
  u : Fin n → ℝ
  w : Fin n → ℝ

def total (n : ℕ) (v : State n) : QueueNeutral.State :=
  ⟨fun k => ∑ i : Fin n, v.history k i,
    ∑ i : Fin n, v.u i, ∑ i : Fin n, v.w i⟩

def step (n d : ℕ) (h rho alpha kappa g : ℝ) (v : State n) : State n :=
  let q := ((n : ℝ) - 1) * h
  let wnext := fun i => rho * v.w i + kappa * alpha * v.u i
  let head := fun i => (1 - q) * v.history 0 i +
    h * ((∑ j : Fin n, v.history d j) - v.history d i) - g * wnext i
  ⟨fun k i => QueueNeutral.shift (head i) (fun t => v.history t i) k,
    fun i => alpha * v.u i, wnext⟩

theorem neighbour_total (n : ℕ) (y : Fin n → ℝ) :
    (∑ i : Fin n, ((∑ j : Fin n, y j) - y i)) =
      ((n : ℝ) - 1) * (∑ j : Fin n, y j) := by
  simp only [Finset.sum_sub_distrib, Finset.sum_const, Finset.card_fin, nsmul_eq_mul]
  ring

/-- Summing the stipulated complete-graph node step gives the scalar queue
step, including the adaptive forcing. No eigenmode assumption is required. -/
theorem total_step (n d : ℕ) (h rho alpha kappa g : ℝ) (v : State n) :
    total n (step n d h rho alpha kappa g v) =
      QueueNeutral.step d (((n : ℝ) - 1) * h) rho alpha kappa g (total n v) := by
  simp only [total, step, QueueNeutral.step, QueueNeutral.State.mk.injEq]
  constructor
  · funext k
    by_cases hk : k = 0
    · subst k
      simp only [QueueNeutral.shift, if_true, Finset.sum_sub_distrib,
        Finset.sum_add_distrib, ← Finset.mul_sum, Finset.sum_const,
        Finset.card_fin, nsmul_eq_mul]
      ring
    · simp [QueueNeutral.shift, hk]
  · constructor <;> simp [Finset.sum_add_distrib, ← Finset.mul_sum]

/-- The aggregate invariant holds for the full stipulated node step. -/
theorem node_conserved_step (n d : ℕ) (h rho alpha kappa g : ℝ) (v : State n) :
    NeutralProjection.conserved (((n : ℝ) - 1) * h) rho alpha kappa g
      (QueueNeutral.aggregate d (total n (step n d h rho alpha kappa g v))) =
    NeutralProjection.conserved (((n : ℝ) - 1) * h) rho alpha kappa g
      (QueueNeutral.aggregate d (total n v)) := by
  rw [total_step, QueueNeutral.queue_conserved_step]

def evolve (n d : ℕ) (h rho alpha kappa g : ℝ) : ℕ → State n → State n
  | 0, v => v
  | t + 1, v => step n d h rho alpha kappa g (evolve n d h rho alpha kappa g t v)

theorem node_conserved_evolve (n d t : ℕ) (h rho alpha kappa g : ℝ) (v : State n) :
    NeutralProjection.conserved (((n : ℝ) - 1) * h) rho alpha kappa g
      (QueueNeutral.aggregate d (total n (evolve n d h rho alpha kappa g t v))) =
    NeutralProjection.conserved (((n : ℝ) - 1) * h) rho alpha kappa g
      (QueueNeutral.aggregate d (total n v)) := by
  induction t with
  | zero => rfl
  | succ t ih => simp only [evolve, node_conserved_step, ih]

end AIEFGate.NodeQueueNeutral
