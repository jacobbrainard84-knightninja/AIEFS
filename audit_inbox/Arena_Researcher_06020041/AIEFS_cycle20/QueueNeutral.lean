/- SPDX-License-Identifier: Apache-2.0
Exact scalar delay-history model linked to the Cycle 19 aggregate invariant.
This does not derive the model from the engine or prove convergence. -/
import AIEFGateCore.NeutralProjection
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

set_option autoImplicit false
open scoped BigOperators
namespace AIEFGate.QueueNeutral

/-- Head is index zero; indices beyond d are irrelevant to the stated results. -/
structure State where
  history : ℕ → ℝ
  u : ℝ
  w : ℝ

def histSum (d : ℕ) (x : ℕ → ℝ) : ℝ :=
  ∑ k ∈ Finset.range d, x (k + 1)

def aggregate (d : ℕ) (v : State) : NeutralProjection.State :=
  ⟨v.history 0, histSum d v.history, v.u, v.w⟩

def shift (head : ℝ) (x : ℕ → ℝ) (k : ℕ) : ℝ :=
  if k = 0 then head else x (k - 1)

def step (d : ℕ) (q rho alpha kappa g : ℝ) (v : State) : State :=
  let wnext := rho * v.w + kappa * alpha * v.u
  let head := (1 - q) * v.history 0 + q * v.history d - g * wnext
  ⟨shift head v.history, alpha * v.u, wnext⟩

/-- Sum of the new delayed slots is the old sum plus current minus tail. -/
theorem histSum_shift (d : ℕ) (head : ℝ) (x : ℕ → ℝ) :
    histSum d (shift head x) = histSum d x + x 0 - x d := by
  unfold histSum
  have hs : (∑ k ∈ Finset.range d, x k) + x d =
      (∑ k ∈ Finset.range d, x (k + 1)) + x 0 := by
    rw [← Finset.sum_range_succ, Finset.sum_range_succ']
  have hshift : (∑ k ∈ Finset.range d, shift head x (k + 1)) =
      ∑ k ∈ Finset.range d, x k := by
    apply Finset.sum_congr rfl
    intro k hk
    simp [shift]
  rw [hshift]
  exact eq_sub_of_add_eq hs

/-- A real queue step projects exactly to the Cycle 19 aggregate recurrence. -/
theorem aggregate_step (d : ℕ) (q rho alpha kappa g : ℝ) (v : State) :
    aggregate d (step d q rho alpha kappa g v) =
      NeutralProjection.step q rho alpha kappa g (v.history d) (aggregate d v) := by
  cases v with
  | mk x u w =>
    simp only [aggregate, step, shift, if_true, NeutralProjection.step,
      histSum_shift]

/-- The conserved quantity now applies to a consistent queue, not a freely
chosen tail at each step. -/
theorem queue_conserved_step (d : ℕ) (q rho alpha kappa g : ℝ) (v : State) :
    NeutralProjection.conserved q rho alpha kappa g
      (aggregate d (step d q rho alpha kappa g v)) =
    NeutralProjection.conserved q rho alpha kappa g (aggregate d v) := by
  rw [aggregate_step, NeutralProjection.conserved_step]

/-- Iteration repeatedly reads its tail from the current queue. -/
def evolve (d : ℕ) (q rho alpha kappa g : ℝ) : ℕ → State → State
  | 0, v => v
  | n + 1, v => step d q rho alpha kappa g (evolve d q rho alpha kappa g n v)

theorem queue_conserved_evolve (d n : ℕ) (q rho alpha kappa g : ℝ) (v : State) :
    NeutralProjection.conserved q rho alpha kappa g
      (aggregate d (evolve d q rho alpha kappa g n v)) =
    NeutralProjection.conserved q rho alpha kappa g (aggregate d v) := by
  induction n with
  | zero => rfl
  | succ n ih =>
      simp only [evolve, queue_conserved_step, ih]

end AIEFGate.QueueNeutral
