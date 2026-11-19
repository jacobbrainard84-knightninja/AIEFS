/- SPDX-License-Identifier: Apache-2.0
Research candidate: a conserved functional of a prescribed aggregated
linear delayed/adaptive recurrence. Not a formalization of the engine. -/
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

set_option autoImplicit false
namespace AIEFGate.NeutralProjection

/-- Aggregates X₀, history sum S, real-EMA row sum U and weight row sum W. -/
structure State where
  x : ℝ
  s : ℝ
  u : ℝ
  w : ℝ

/-- Prescribed step. `tail` is the old delayed mean X_d. For an actual
history of positive delay, S⁺ = S + X₀ − X_d. -/
def step (q rho alpha kappa g tail : ℝ) (v : State) : State :=
  let wnext := rho * v.w + kappa * alpha * v.u
  ⟨(1-q)*v.x + q*tail - g*wnext, v.s + v.x - tail,
   alpha*v.u, wnext⟩

/-- Denominator-cleared neutral functional; valid even at singular parameters. -/
def conserved (q rho alpha kappa g : ℝ) (v : State) : ℝ :=
  (1-rho)*(1-alpha)*(v.x+q*v.s) -
  g*(rho*(1-alpha)*v.w + kappa*alpha*v.u)

theorem conserved_step (q rho alpha kappa g tail : ℝ) (v : State) :
    conserved q rho alpha kappa g (step q rho alpha kappa g tail v) =
      conserved q rho alpha kappa g v := by
  simp only [conserved, step]
  ring

/-- Iterate with any sequence of delayed means: the invariant does not require
assuming they are actually consistent with a delay queue. -/
def evolve (q rho alpha kappa g : ℝ) (tail : ℕ → ℝ) : ℕ → State → State
  | 0, v => v
  | n+1, v => step q rho alpha kappa g (tail n) (evolve q rho alpha kappa g tail n v)

theorem conserved_evolve (q rho alpha kappa g : ℝ) (tail : ℕ → ℝ)
    (n : ℕ) (v : State) :
    conserved q rho alpha kappa g (evolve q rho alpha kappa g tail n v) =
      conserved q rho alpha kappa g v := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [evolve, conserved_step, ih]

/-- Normalized candidate projection. `d` is a real parameter representing
history length; connection to a finite queue is not asserted here. -/
noncomputable def projection (q rho alpha kappa g d : ℝ) (v : State) : ℝ :=
  conserved q rho alpha kappa g v / ((1-rho)*(1-alpha)*(1+d*q))

theorem projection_step (q rho alpha kappa g d tail : ℝ) (v : State) :
    projection q rho alpha kappa g d (step q rho alpha kappa g tail v) =
      projection q rho alpha kappa g d v := by
  simp only [projection, conserved_step]

theorem projection_uniform (q rho alpha kappa g d c : ℝ)
    (hden : (1 - rho) * (1 - alpha) * (1 + d * q) ≠ 0) :
    projection q rho alpha kappa g d ⟨c,d*c,0,0⟩ = c := by
  apply (div_eq_iff hden).2
  simp only [conserved, mul_zero, add_zero, sub_zero]
  ring

/-- The normalized candidate is invariant over arbitrarily many steps. -/
theorem projection_evolve (q rho alpha kappa g d : ℝ) (tail : ℕ → ℝ)
    (n : ℕ) (v : State) :
    projection q rho alpha kappa g d (evolve q rho alpha kappa g tail n v) =
      projection q rho alpha kappa g d v := by
  simp only [projection, conserved_evolve]

/-- If a uniform aggregate state is actually reached, its phase is fixed by
  the initial projection. This does not assert that such a state is reached. -/
theorem uniform_reached_projection (q rho alpha kappa g d c : ℝ)
    (tail : ℕ → ℝ) (n : ℕ) (v : State)
    (hden : (1 - rho) * (1 - alpha) * (1 + d * q) ≠ 0)
    (hreached : evolve q rho alpha kappa g tail n v = ⟨c, d * c, 0, 0⟩) :
    projection q rho alpha kappa g d v = c := by
  rw [← projection_evolve q rho alpha kappa g d tail n v, hreached]
  exact projection_uniform q rho alpha kappa g d c hden

/-- The phase-only aggregate fails to be invariant when weights feed phases. -/
theorem phase_only_counterexample :
    let v : State := ⟨0,0,0,1⟩
    let v' := step (1/2) (1/2) (1/2) 1 1 0 v
    v'.x + (1/2)*v'.s ≠ v.x + (1/2)*v.s := by
  norm_num [step]

end AIEFGate.NeutralProjection
