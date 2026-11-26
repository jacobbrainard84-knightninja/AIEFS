/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import AIEFGateCore.PhaseIncrement
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Angle
import Mathlib.Algebra.Order.ToIntervalMod

/-!
# (H17) `wrapPhase` is Mathlib's `toIcoMod` on `[0, 2π)`

Plan item H17 (audit-inbox `PLAN_2026-11-25_scan_leads.md`, as changed by Auditor Seat 002's review
`REVIEW_2026-11-26_auditor_scan_leads.md`). The bridge goes to `toIcoMod`, not only to `Real.Angle`:
coercion to `Real.Angle` forgets the representative, so an `Angle` equality alone cannot tell a
`[0, 2π)` wrap from a `(−π, π]` one.

* `wrapPhase_eq_toIcoMod`: `wrapPhase t = toIcoMod two_pi_pos 0 t` (the `[0, 2π)` convention).
* `wrapPhase_mem_Ico`: `0 ≤ wrapPhase t < 2π`.
* `wrapPhase_coe_angle`: as an `Angle`, `wrapPhase t` is `t` (corollary; it does not discriminate).
* `false_*`: refutations of the conventions `wrapPhase` is *not* (used by mutants M700–M703).

Scope: exact reals. The engine wraps with float64 `np.mod(θ, 2π)`, which can return exactly
`2π` (e.g. `np.mod(-1e-20, 2π)`), outside the real range proved here; the phasor is unaffected.
Whether that value occurs in production runs is UNEXPLAINED/unmeasured (see the Python test
`test_lean_gate_h17.py`, which pins the witness).
-/

set_option autoImplicit false

namespace AIEFGate
namespace WrapBridge

theorem wrapPhase_eq_toIcoMod (t : ℝ) : Phase.wrapPhase t = toIcoMod Real.two_pi_pos 0 t := by
  rw [toIcoMod, toIcoDiv_eq_floor, zsmul_eq_mul, sub_zero]
  rfl

theorem wrapPhase_mem_Ico (t : ℝ) : 0 ≤ Phase.wrapPhase t ∧ Phase.wrapPhase t < 2 * Real.pi := by
  have h := toIcoMod_mem_Ico Real.two_pi_pos 0 t
  rw [← wrapPhase_eq_toIcoMod, zero_add] at h
  exact ⟨h.1, h.2⟩

theorem wrapPhase_coe_angle (t : ℝ) : ((Phase.wrapPhase t : ℝ) : Real.Angle) = (t : Real.Angle) := by
  rw [wrapPhase_eq_toIcoMod]
  exact Real.Angle.coe_toIcoMod t 0

/-- Value probe: `−π/2` wraps to `3π/2` (floor of `−1/4` is `−1`). -/
theorem probe_wrap_neg_half_pi : Phase.wrapPhase (-(Real.pi / 2)) = 3 * Real.pi / 2 := by
  rw [wrapPhase_eq_toIcoMod, toIcoMod_eq_iff]
  refine ⟨⟨by linarith [Real.pi_pos], by linarith [Real.pi_pos]⟩, -1, ?_⟩
  simp only [neg_smul, one_smul]
  ring

/-- Value probe: `0` wraps to `0`. -/
theorem probe_wrap_zero : Phase.wrapPhase 0 = 0 := by
  simp [Phase.wrapPhase]

/-- `wrapPhase` is not the `(−π, π]` wrap (witness `t = −π/2`). -/
theorem false_wrap_toIocMod_neg_pi :
    ¬ ∀ t : ℝ, Phase.wrapPhase t = toIocMod Real.two_pi_pos (-Real.pi) t := by
  intro H
  have h1 := H (-(Real.pi / 2))
  rw [probe_wrap_neg_half_pi, (toIocMod_eq_self Real.two_pi_pos).2
    ⟨by linarith [Real.pi_pos], by linarith [Real.pi_pos]⟩] at h1
  linarith [Real.pi_pos]

/-- `wrapPhase` is not the `[−π, π)` wrap (witness `t = −π/2`). -/
theorem false_wrap_toIcoMod_neg_pi :
    ¬ ∀ t : ℝ, Phase.wrapPhase t = toIcoMod Real.two_pi_pos (-Real.pi) t := by
  intro H
  have h1 := H (-(Real.pi / 2))
  rw [probe_wrap_neg_half_pi, (toIcoMod_eq_self Real.two_pi_pos).2
    ⟨by linarith [Real.pi_pos], by linarith [Real.pi_pos]⟩] at h1
  linarith [Real.pi_pos]

/-- The range is not `[0, π)` (witness `t = −π/2 ↦ 3π/2`). -/
theorem false_wrap_lt_pi : ¬ ∀ t : ℝ, 0 ≤ Phase.wrapPhase t ∧ Phase.wrapPhase t < Real.pi := by
  intro H
  have h1 := (H (-(Real.pi / 2))).2
  rw [probe_wrap_neg_half_pi] at h1
  linarith [Real.pi_pos]

/-- The lower end is attained: the range is not `(0, 2π)` (witness `t = 0`). -/
theorem false_wrap_pos : ¬ ∀ t : ℝ, 0 < Phase.wrapPhase t ∧ Phase.wrapPhase t < 2 * Real.pi := by
  intro H
  have h1 := (H 0).1
  rw [probe_wrap_zero] at h1
  exact lt_irrefl 0 h1

end WrapBridge
end AIEFGate
