# H12: where the LeanPool Hebbian joint-energy argument breaks for AIEFS

Plan item H12 (audit-inbox `PLAN_2026-11-25_scan_leads.md`) as changed by Auditor Seat 002's review
(`REVIEW_2026-11-26_auditor_scan_leads.md`, `b15c5e5`): a note with citations only, **no LeanPool or kuramoto-lean code
copied or vendored, no Lean or toolchain change**, no "EMA rate → 1" framing, no loose "not a gradient" Lean lemma,
Wang–Dong as a second contrast target, and a numerical red team on an engine copy. Author Researcher 001; auditor
Auditor Seat 002. Numbering: M600 ff. (engine regimes), N600 ff. (negative controls).

## 1. The two contrast targets (citations only)
- **LeanPool `Kuramoto/Hebbian.lean`** (Apache-2.0; port of velvetmonkey/kuramoto-lean, MIT),
  https://github.com/LeanPool/lean-pool/blob/main/LeanPool/Kuramoto/Hebbian.lean. The source was read, not built.
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
| M600 | identical ω (mean of production ω), rotating frame, all pre-gate steps | INCREASE FOUND | INCREASE FOUND: 3466 of 8793 states; worst s = 0.288 with \|∇E\|\|F\| = 1.47 (seed 1, step 1554) |
| M601 | as M600, only after EMA warm-up (step ≥ 8751) | NOT REACHED | NOT REACHED: the gate fires at steps 1757–1762 in every seed |
| M602 | production (heterogeneous) ω, lab frame | NO INCREASE | NO INCREASE (11080 states) |
| N600 | control: weight drive replaced by c·cos (exact gradient) | NO INCREASE | NO INCREASE (8793 states) |
| N601 | control: weight drive −c·cos (the detector must fire) | INCREASE FOUND | INCREASE FOUND (8793 of 8793) |

**Observation (added with the results, not predeclared):** the candidate E itself, evaluated on the engine copy's
actual steps in regime M600, rises on 519–778 of the ~1758 pre-gate steps per seed. In 4 of 5 seeds it ends far above
its start (≈0.008 → 1.0–1.5). See `discrete_energy_observation()`.

How to read this:
- **M600 is the counterexample** the plan asked for. In a regime with no delay, no gate and a fixed non-degenerate α,
  the LeanPool-shaped joint energy is not a Lyapunov function for the engine law. N600 shows the computation is right
  where the energy must decrease, and N601 shows the detector can fire.
- The likely mechanism is obstruction 1 (weights grow on pairs locked at an offset). It is consistent with the data
  but **not separately verified** pair by pair.
- **M602 is not evidence of an energy structure.** With heterogeneous ω the −Σ ω_i θ_i drift term contributes
  −|θ̇|² ≈ −N·ω̄², which swamps the weight term. That candidate is insensitive, not valid.
- **The regime is short.** Since the gate fires at about step 1760 (t ≈ 17.6), "gate inactive" covers only the
  EMA transient; after warm-up the gate is always involved. No non-degenerate regime with a joint energy was found.

## 4. What this does not claim
- There is no Lean statement and no "the drive is not ∂E of any energy" lemma (per the review: stated loosely that is
  either trivial or unprovable).
- The result is about one candidate energy family, the LeanPool shape with R standing in for cos. It does not show
  that no Lyapunov function exists on (θ, B, acc).
- Wang–Dong is cited from a third-party review only.
- No code was copied. Reuse (H15) stays deferred and cite-only by default.

Reproduce: `unshare -rn python research/hebbian_contrast/energy_redteam_h12.py` (≈7 s); pytest
`research/lean_gate/tests/test_hebbian_contrast_h12.py`.
