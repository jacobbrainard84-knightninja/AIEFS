/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.GateMap
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Ring.Finset

/-!
# (P3) Branch persistence: `n` steps of `stepB` along a uniform-scale kernel direction

`stepB_sub_eq_smul_of_uniform_on` is a one-step statement. Here it is iterated: if at every step
`k < n` the base trajectory `B_k = stepB^[k] B` and the perturbed state `B_k + t_k h` lie on one
uniform-scale branch (`UniformBranch`, an explicit hypothesis: same clip pattern on `supp h`, same
gate decision, a fixed controller assignment valid at both states on the relevant edges, `h` in its
kernel there, and a single branch scale `s_k` on `supp h`), then

  `stepB^[n] (B + t • h) = stepB^[n] B + (t ∏_{k<n} (1 - γ dt) s_k) • h`   (exactly).

Scope: the drive `(η+μ) R - μ` is held fixed over all `n` steps (`R` frozen; in the engine `R`
moves with the phases, so this is the `B`-subsystem with frozen coherence, not the engine). The
branch hypothesis is assumed at every step, not derived; it is shown satisfiable for all `n` at
engine-shaped parameters in `PersistenceWitness`. A uniform scale on `supp h` is needed for the
perturbation to stay a multiple of `h`; with non-uniform scales the direction itself changes after
one step and this statement does not apply.
-/

set_option autoImplicit false

namespace AIEFGate

open Finset

noncomputable section

variable {V E : Type*} [DecidableEq V] [Fintype E]
variable (p : Params) (G : Graph V E)

/-- The hypotheses of `stepB_sub_eq_smul_of_uniform_on` at one step (base `B`, amplitude `t`,
branch scale `s`, controller assignment `ctrl`). -/
def UniformBranch (drive B h : E → ℝ) (t s : ℝ) (ctrl : E → V) : Prop :=
  (∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e) ∧
  (GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h))) ∧
  InCtrlKerOn G (Rel (prop p drive B) h) ctrl h ∧
  IsCtrlOn p G (Rel (prop p drive B) h) (prop p drive B) ctrl ∧
  IsCtrlOn p G (Rel (prop p drive B) h) (prop p drive (B + t • h)) ctrl ∧
  ∀ e, h e ≠ 0 → branchScale p G drive B ctrl e = s

/-- One step on a uniform branch: the perturbation stays a multiple of `h`. -/
theorem stepB_add_smul_of_uniformBranch (drive B h : E → ℝ) (t s : ℝ) (ctrl : E → V)
    (hb : UniformBranch p G drive B h t s ctrl) :
    stepB p G drive (B + t • h) = stepB p G drive B + (t * (1 - p.γ * p.dt) * s) • h := by
  obtain ⟨hclip, hon, hker, hc0, hc1, hs⟩ := hb
  rw [← stepB_sub_eq_smul_of_uniform_on p G drive B h t s ctrl hclip hon hker hc0 hc1 hs]
  abel

/-- Amplitude of the perturbation after `k` steps: `t ∏_{j<k} (1 - γ dt) s_j`. -/
def amp (t : ℝ) (s : ℕ → ℝ) (k : ℕ) : ℝ :=
  t * ∏ j ∈ range k, ((1 - p.γ * p.dt) * s j)

theorem amp_zero (t : ℝ) (s : ℕ → ℝ) : amp p t s 0 = t := by simp [amp]

theorem amp_succ (t : ℝ) (s : ℕ → ℝ) (k : ℕ) :
    amp p t s (k + 1) = amp p t s k * (1 - p.γ * p.dt) * s k := by
  simp only [amp, prod_range_succ]; ring

/-- **Branch persistence (n steps).** If for every `k < n` the base trajectory `stepB^[k] B` and
the perturbed state `stepB^[k] B + amp k • h` satisfy `UniformBranch` (scale `s k`, controller
`ctrl k`), then after `n` steps the perturbation is exactly `amp n • h`:
`stepB^[n] (B + t • h) = stepB^[n] B + (t ∏_{k<n} (1 - γ dt) s_k) • h`. -/
theorem iterate_stepB_add_smul_of_branch (drive B h : E → ℝ) (t : ℝ) (s : ℕ → ℝ)
    (ctrl : ℕ → E → V) (n : ℕ)
    (hbr : ∀ k < n, UniformBranch p G drive ((stepB p G drive)^[k] B) h (amp p t s k) (s k)
      (ctrl k)) :
    (stepB p G drive)^[n] (B + t • h) = (stepB p G drive)^[n] B + amp p t s n • h := by
  induction n with
  | zero => simp [amp_zero]
  | succ n ih =>
    rw [Function.iterate_succ_apply', Function.iterate_succ_apply',
      ih (fun k hk => hbr k (Nat.lt_succ_of_lt hk)),
      stepB_add_smul_of_uniformBranch p G drive _ h _ (s n) (ctrl n) (hbr n (Nat.lt_succ_self n)),
      amp_succ]

/-- The amplitude stays in `[0, t]` when every step factor `(1 - γ dt) s_j` is in `[0, 1]`. -/
theorem amp_mem_Icc (t : ℝ) (ht : 0 ≤ t) (s : ℕ → ℝ)
    (hs : ∀ j, 0 ≤ (1 - p.γ * p.dt) * s j ∧ (1 - p.γ * p.dt) * s j ≤ 1) (k : ℕ) :
    0 ≤ amp p t s k ∧ amp p t s k ≤ t := by
  have h0 : 0 ≤ ∏ j ∈ range k, ((1 - p.γ * p.dt) * s j) :=
    prod_nonneg fun j _ => (hs j).1
  have h1 : ∏ j ∈ range k, ((1 - p.γ * p.dt) * s j) ≤ 1 :=
    prod_le_one (fun j _ => (hs j).1) (fun j _ => (hs j).2)
  exact ⟨mul_nonneg ht h0, by unfold amp; nlinarith⟩

end

end AIEFGate
