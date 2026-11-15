/- SPDX-License-Identifier: Apache-2.0
Research candidate: common-frequency phase lock, exact P5 model. -/
import AIEFGateCore.PhaseLockCoherence

set_option autoImplicit false
namespace AIEFGate.RotatingLock
variable {V : Type*}

/-- Common constant increments yield constant delayed input after the delay flushes.
The increment `w` need not be zero, so this covers uniformly rotating phase locks. -/
theorem input_step_of_common_increment
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau w : ℝ)
    (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = w)
    (n : ℕ) (hn : N + d ≤ n) (i j : V) :
    PhaseCoherence.coherenceInput d x0 u omega tau (n + 1) i j =
      PhaseCoherence.coherenceInput d x0 u omega tau n i j := by
  simp only [PhaseCoherence.coherenceInput]
  rw [Phase.delayed_input_step]
  have hu : u n i = w := hlock n (by omega) i
  have hd : d ≤ n := by omega
  have huold : u (n - d) j = w := hlock (n - d) (by omega) j
  have hdelay : Phase.delayedIncrement d u n j = w := by
    simp [Phase.delayedIncrement, hd, huold]
  rw [hu, hdelay]
  simp [Phase.phasor]

/-- The input on each directed edge is constant on the entire locked tail. -/
theorem input_eq_of_common_increment
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau w : ℝ)
    (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = w)
    (n : ℕ) (hn : N + d ≤ n) (i j : V) :
    PhaseCoherence.coherenceInput d x0 u omega tau n i j =
      PhaseCoherence.coherenceInput d x0 u omega tau (N + d) i j := by
  induction n, hn using Nat.le_induction with
  | base => rfl
  | succ n hn ih =>
      rw [input_step_of_common_increment d x0 u omega tau w N hlock n hn i j]
      exact ih

/-- Exact EMA error identity for a common-frequency lock. No bound on alpha is assumed. -/
theorem geometric_of_common_increment
    (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ)
    (u : ℕ → V → ℝ) (omega : V → ℝ) (tau w : ℝ)
    (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = w)
    (k : ℕ) (i j : V) :
    PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau (N + d + k) i j -
        PhaseCoherence.coherenceInput d x0 u omega tau (N + d) i j =
      (alpha : ℂ)^k *
        (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau (N + d) i j -
         PhaseCoherence.coherenceInput d x0 u omega tau (N + d) i j) := by
  exact PhaseLockCoherence.coherenceTrace_geometric_of_constant_input alpha C0 d x0 u omega tau
    (N + d) (PhaseCoherence.coherenceInput d x0 u omega tau (N + d) i j) i j
    (fun n hn => input_eq_of_common_increment d x0 u omega tau w N hlock n hn i j) k

end AIEFGate.RotatingLock
