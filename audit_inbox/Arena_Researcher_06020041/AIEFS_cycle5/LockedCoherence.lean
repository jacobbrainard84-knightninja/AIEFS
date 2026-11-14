/- SPDX-License-Identifier: Apache-2.0
Workspace research candidate. Depends on unmerged PhaseLockCoherence. -/
import AIEFGateCore.PhaseLockCoherence

set_option autoImplicit false
namespace AIEFGate.LockedCoherence
variable {V : Type*}

/-- Phase freezing gives a constant delayed input after the delay has elapsed. -/
theorem input_eq_at_lock_delay
    (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = 0)
    (n : ℕ) (hn : N + d ≤ n) (i j : V) :
    PhaseCoherence.coherenceInput d x0 u omega tau n i j =
      PhaseCoherence.coherenceInput d x0 u omega tau (N+d) i j := by
  induction n, hn using Nat.le_induction with
  | base => rfl
  | succ n hn ih =>
      rw [PhaseLockCoherence.coherenceInput_constant_after_lock d x0 u omega tau N hlock n hn i j]
      exact ih

/-- Compose the delayed phase result with the exact EMA identity. -/
theorem geometric_after_phase_lock
    (alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ)
    (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ)
    (N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = 0)
    (k : ℕ) (i j : V) :
    PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau (N+d+k) i j -
        PhaseCoherence.coherenceInput d x0 u omega tau (N+d) i j =
      (alpha : ℂ)^k *
        (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau (N+d) i j -
         PhaseCoherence.coherenceInput d x0 u omega tau (N+d) i j) := by
  exact PhaseLockCoherence.coherenceTrace_geometric_of_constant_input alpha C0 d x0 u omega tau
    (N+d) (PhaseCoherence.coherenceInput d x0 u omega tau (N+d) i j) i j
    (fun n hn => input_eq_at_lock_delay d x0 u omega tau N hlock n hn i j) k

end AIEFGate.LockedCoherence
