# H12: where the LeanPool Hebbian joint-energy argument breaks for AIEFS

Plan item H12 (audit-inbox `PLAN_2026-11-25_scan_leads.md`) as changed by Auditor Seat 002's review
(`REVIEW_2026-11-26_auditor_scan_leads.md`, `b15c5e5`): a note with citations only, **no LeanPool or kuramoto-lean code
copied or vendored, no Lean or toolchain change**, no "EMA rate → 1" framing, no loose "not a gradient" Lean lemma,
Wang–Dong as a second contrast target, and a numerical red team on an engine copy. Author Researcher 001; auditor
Auditor Seat 002. Numbering: M600 ff. (engine regimes), N600 ff. (negative controls).

## 1. The two contrast targets (citations only)
- **LeanPool `Kuramoto/Hebbian.lean`**, read at commit `1044203bbfebffdb301fa3a9ec1c4c7982616e3b`:
  https://github.com/LeanPool/lean-pool/blob/1044203bbfebffdb301fa3a9ec1c4c7982616e3b/LeanPool/Kuramoto/Hebbian.lean.
  The source was read, not built.
  - **Licence: Apache-2.0.** The file header says "Released under Apache 2.0 license", the repo `LICENSE` is the Apache
    License 2.0, and GitHub reports `Apache-2.0` for the repo.
  - Provenance: LeanPool's import commit `ff8c927` ("[import] Kuramoto") says it was ported from
    velvetmonkey/kuramoto-lean, and GitHub reports that upstream repo as MIT. The MIT licence applies to the
    upstream repo only; the LeanPool file we cite is Apache-2.0.
  Weight flow `(K/2)·cos(θj−θi) − λ·W_ij`, energy = weighted Kuramoto potential + (λ/2)‖W‖²_F; theorem
  `hebbian_joint_lyapunov_descent`: for symmetric W the joint flow does not increase the energy.
- **Wang & Dong, JDE 441 (2025) 113475**, https://doi.org/10.1016/j.jde.2025.113475. **Read through the zbMATH/MaRDI
  review only; full text not read.** θ̇_i = ω_i + Σ a_ij κ_ij sin(θj−θi), κ̇_ij = μΓ(θi−θj) − γκ_ij, with Γ = cos
  (Hebbian) or |sin| (anti-Hebbian).
  - My own observation, **not a claim about the paper's proofs:** with Γ = cos the law has the same gradient shape
    as LeanPool's, using E = −Σ_{i<j} a_ij κ_ij cos(θj−θi) + (γ/2μ) Σ κ_ij² − Σ ω_i θ_i.
  - With Γ = |sin| it does not: the phase law fixes the coupling term in E as −κ cos, so the weight drive would have
    to be cos.

## 2. The AIEFS law and the exact obstructions
Engine (`aief_experiment_engine_v1.py`, sha256 `ca4593fd…acdede`):
- θ̇_i = ω_i + Σ_j B_ij sin(θ_j(t−τ) − θ_i).
- Ḃ_ij = (η+μ)R_ij − μ − γB_ij, then clipped at 0 and passed through the min-endpoint gate.
- R_ij = |acc_ij|, where acc ← α·acc + (1−α)·exp(i·Δφ_ij) is a complex EMA (α = exp(−dt/T_window) = 0.99943).

For the LeanPool argument to apply, the weight drive must equal c·cos(θj−θi) on the same state space. Four things stop
it:
1. **Phase-offset invariance.** R depends on how steady Δφ is, not on Δφ itself. A pair locked at any constant offset,
   including anti-phase, has R → 1 and its weight grows. That increases −B cos(Δθ) whenever cos(Δθ) < 1.
2. **Memory.** R is a function of the EMA state acc, which is not in (θ, B). An energy in (θ, B) alone cannot see it.
   Adding acc to the state would need a new candidate energy, and none was found (§4).
3. **Delay** τ = 0.5 in the phase law. Removed in the red team (τ = 0) to show that the obstruction is not only the
   delay.
4. **The gate** (non-smooth, per-edge min of endpoint scales). Excluded in the red team (only steps before the first
   trigger count).

## 3. Red team (non-degenerate regime: τ = 0, fixed production α ∈ (0,1), gate inactive)
`energy_redteam_h12.py` loads a **copy** of the SHA-locked engine (sha checked). It sets τ = 0 with
`dataclasses.replace`; `ModelConfig.validate()` would reject τ = 0, so this regime is outside the validated domain
(disclosed). It then evaluates the exact continuous-time rate s = ∇E·F of the LeanPool-shaped candidate:
- E(θ, B) = −Σ w_i θ_i − Σ_{i<j} B_ij cos(θj−θi) + (1/c) Σ_{i<j}(μB_ij + γB_ij²/2), with c = η+μ.
- s is evaluated at every engine state before the first gate trigger, 5 seeds.
- F_B is projected to 0 at clipped edges.
- An increase counts only if s > 1e-9·|∇E|·|F|.

Predeclared in the first commit (`0da17b7`), before any run. All five matched:

| ID | Regime | Predeclared | Observed |
|---|---|---|---|
| M600 | identical ω (mean of production ω), rotating frame, all pre-gate steps; **τ = 0, outside `ModelConfig.validate` (requires τ > 0)** | INCREASE FOUND | INCREASE FOUND: 3466 of 8793 states; worst s = 0.288 with \|∇E\|\|F\| = 1.47 (seed 1, step 1554) |
| M601 | as M600, only after EMA warm-up (step ≥ 8751) | NOT REACHED | NOT REACHED: the gate fires at steps 1757–1762 in every seed |
| M602 | production (heterogeneous) ω, lab frame | NO INCREASE | NO INCREASE (11080 states) |
| N600 | control: weight drive replaced by c·cos (exact gradient) | NO INCREASE | NO INCREASE (8793 states) |
| N601 | control: weight drive −c·cos (the detector must fire) | INCREASE FOUND | INCREASE FOUND (8793 of 8793) |

**Observation (added with the results, not predeclared):** the candidate E itself, evaluated on the engine copy's
actual steps in regime M600, rises on 519–778 of the ~1758 pre-gate steps per seed. In 4 of 5 seeds it ends far above
its start (≈0.008 → 1.0–1.5). See `discrete_energy_observation()`.

How to read this:
- **M600 is the counterexample** the plan asked for (**τ = 0, outside `ModelConfig.validate`, which requires τ > 0**).
  In a regime with no delay, no gate and a fixed non-degenerate α, the LeanPool-shaped joint energy is not a Lyapunov
  function for the engine law.
  - The engine-legal sibling τ = dt = 0.01 (delay_steps = 1) passes `validate()` and gives **3469 increases out of
    8792 states** (`tau_dt_observation()`; observation added in the audit follow-up, not predeclared; reproduced
    by Researcher 001 and pinned in the test). It is an approximation: the candidate uses the undelayed rate while the
    phase law reads a one-step-delayed state. So the result does not depend on leaving the validated domain. N600 shows the computation is right
  where the energy must decrease, and N601 shows the detector can fire.
- The likely mechanism is obstruction 1 (weights grow on pairs locked at an offset). It is consistent with the data
  but **not separately verified** pair by pair.
- **M602 is not evidence of an energy structure.** With heterogeneous ω the −Σ ω_i θ_i drift term contributes
  −|θ̇|² ≈ −Σ_i ω_i², which swamps the weight term. That candidate is insensitive, not valid.
- **The regime is short.** Since the gate fires at about step 1760 (t ≈ 17.6), "gate inactive" covers only the
  EMA transient. In all 5 seeds of this regime (identical ω, τ = 0, default parameters), the gate fires before
  warm-up. This was not checked for other seeds, frequencies, delays or parameters. No non-degenerate regime with a joint energy was found.

## 4. What this does not claim
- There is no Lean statement and no "the drive is not ∂E of any energy" lemma (per the review: stated loosely that is
  either trivial or unprovable).
- The result is about one candidate energy family, the LeanPool shape with R standing in for cos. It does not show
  that no Lyapunov function exists on (θ, B, acc).
- Wang–Dong is cited from a third-party review only.
- No code was copied. Reuse (H15) stays deferred and cite-only by default.

Reproduce: `unshare -rn python research/hebbian_contrast/energy_redteam_h12.py` (≈7 s); pytest
`research/lean_gate/tests/test_hebbian_contrast_h12.py`.

## 5. Audit follow-up (Auditor Seat 002, CLEAN WITH NOTES on `4debc9f`)
- T1: τ = 0 caveat added to the M600 row and headline; τ = dt sibling added (3469/8792).
- W1: the "gate before warm-up" sentence is scoped to the 5 seeds × identical ω × τ = 0 × default parameters.
- C1: the engine copy now asserts the full 64-hex sha256 (the old comment claimed a registry check that did not exist).
- R1: the test pins counted/increases (M600 8793/3466, M602 11080/0, N600, N601), the worst state, the trigger
  steps, the per-seed rising counts, 4 of 5 seeds ending higher and the τ = dt numbers.
- Minor: Σ_i ω_i² in M602; `discrete_energy_observation()` moved above `__main__`; LeanPool licence and commit stated.
- R1 check, re-run by Researcher 001 on the auditor's 5 surviving wrong variants (copies in /tmp, `unshare -rn`):
  - The pins kill four of them:
    - 1/c dropped from g_B: killed.
    - μ dropped from F_B: killed.
    - REL_TOL 0.5: killed.
    - Sign of the cos term in the discrete energy flipped: killed.
  - **The variant with the clip projection removed survived the pins**: same counts (8793/3466, 11080/0) and the
    same per-seed numbers, even though its s differs at 978 of 1757 states in seed 1. Removing the clip changes s
    without changing any increase decision. A plausible reason is that clipped pairs tend to make s more negative;
    that is **not verified**.
  - A direct unit test of the clip (`test_clip_projection_in_rate`, hand-built state with B_ij = 0 and a negative
    drive) was added, and it kills that variant.
