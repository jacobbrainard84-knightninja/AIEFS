# Project state (as of 2026-11-11 04:30 Europe/Tirane; refreshed by Auditor Seat 002)

AIEFS is a hobby math project: an adaptive Kuramoto model (N = 12 oscillators) with Hebbian-style adaptive couplings B, a delay τ = 0.5, an EMA of pairwise coherence R, and a min-endpoint multiplicative capacity gate, together with Lean 4 proofs of some supporting facts.

Items marked **PENDING** have not landed on `main`. Do not cite them as results. Items marked **IN PROGRESS** are on a non-main branch and are not yet dual-control-audited / merged.

## Branches: snapshot, **not live**

**Retrieved with `git ls-remote origin` on 2026-11-11 at 04:30 Europe/Tirane (03:30 UTC) by Auditor Seat 002.** Branch tips move. Re-run `git ls-remote origin` before citing any sha below. Verdicts are agent ratings: input only, see README rule 7.

On 2026-11-11 the owner approved deleting 20 remote branches that were fully merged into `main`, fully contained in `audit-inbox`, or superseded (`fix/comparator-v4-gates`, replaced by PR #8). Their PRs keep the commits. Old shas cited elsewhere in this folder still resolve through the PRs.

| What | Tip at retrieval | Status |
|---|---|---|
| `main` | `1c30ca5` (`1c30ca56e56f11517d1e04f90d521a5aa6990c52`) | Merge of PR #27 (2026-11-10 15:30 UTC). Contains PRs #1–#5, #7–#12, #17–#27. |
| PR #23 `fix/v41-followup-notes` | merge `543e7e1` | **Merged.** ERRATA **E26**: no NPZ path fallback, full post-guard swap test, cert-root test. v4.1 is still an unaudited candidate. |
| PR #24 `research/lean-gate-p3` | merge `b198a77` | **Merged.** Lean P3: bridge to pinned `CCtrl`/`vCtrl`, n-step branch persistence, engine-shaped negations. |
| PR #25 `research/lean-gate-p4a` | merge `3c5c0ef` | **Merged.** Lean P4a `Capacity.lean`: guarded capacity (port of Researcher 040282 cycle 002). |
| PR #26 `research/lean-gate-p4b` | merge `4988600` | **Merged.** Lean P4b `Freeze.lean`, `WeightUpdate.lean`: weight-update bridge (port of 040282 cycle 003). |
| PR #27 `fix/lean-gate-followups` | merge `1c30ca5` | **Merged.** `preM_between` bounds, `convex_weights_iff`; CI now runs the Lean-gate mutation check (lean.yml, AIEFGateCore row) and `research/lean_gate/tests` (repo-checks). |
| Earlier merges (context) | — | #17–#22: E19–E22, E24–E25, Lean P1/P2. #3 `research/freezing` (AIEFFreezeCore). #4 red team. #5 E15. #7–#12: lint, comparator v4/E14, manifest G1/G2, upload_new, check-sha256sums, R026 cleanup/E16–E18. |
| `research/lean-gate-p5` | `54037ea` | **IN PROGRESS (author Researcher 001).** Ports of 040282 cycles 010 (HistoryBuffer), 011 (PhaseIncrement) and 013 (PhaseCoherenceBridge), mutants M37+. Auditor delta-audit CLEAN WITH NOTES at `54037ea`, but it is 5 behind `main` and conflicts in 6 files; needs a merge refresh (no rebase) and a fresh delta check before any PR. |
| `research/lean-gate-c014` | `9b9b3d9` | **IN PROGRESS (author Auditor Seat 002).** Port of 040282 cycle 014 `TrajectoryInvariants.lean` (namespace `AIEFGate.TrajectorySafety`). Local gate PASS 677 decls. Awaits Researcher 001 audit; lands after P5. |
| `fix/lean-mutation-step-guard` | `871434e` | **IN PROGRESS (author Auditor Seat 002).** Test that lean.yml keeps exactly one mutation-check step wired to a real matrix row. Awaits Researcher 001 audit. |
| `research/engine-step-order` | `99456c5` | **IN PROGRESS (author Auditor Seat 002).** `research/lean_gate/tests/test_engine_step_order.py`: runs main's real `advance_state` on 4 exact N=2 states (step order, delay read, dt, old-B carry). Awaits Researcher 001 audit. |
| `fix/manifest-nonempty` | `92993eb` | Owner item. Do not delete without the owner. |
| `audit-inbox` | (this branch) | Drop box. **Never merge it into `main`**, especially `audit_inbox/salvage/` (README rule 12). |
| `arena/d4a487cc-aiefs` | `2af3859` | Arena working branch (rounds 5–10, not copied anywhere else). **Never merge its tree.** |
| `research/aiefs-northstar-evaluation` | `003522e` | One planning doc (`research/northstar/AIEFS_NORTHSTAR_EVALUATION_2026-11-08.md`); PR #13 closed unmerged; the doc exists only on this branch. |

## Researcher 040282 Lean candidates (agent ratings, input only)

| Cycle | File | Where | Auditor rating |
|---|---|---|---|
| 002 | Capacity | `main` (PR #25) | ported |
| 003 | Freeze / WeightUpdate | `main` (PR #26) | ported |
| 010 | HistoryBuffer | P5 branch | ADOPT |
| 011 | PhaseIncrement | P5 branch | ADOPT as a building block (does not alone close the C004 gap) |
| 013 | PhaseCoherenceBridge | P5 branch | ADOPT WITH NOTES (two node-uniform probe survivors) |
| 014 | TrajectoryInvariants | `research/lean-gate-c014` | ADOPT WITH NOTES (pWide witnesses use a full-reset step; not about engine params) |
| 015 | ClosedLoopCore | owner-held, not yet deposited | ADOPT WITH NOTES: delayed read in the phase coupling and dt are unpinned by its probes (F1/F2); fix in the port. See `audit_inbox/2026-11-11_auditor-seat-002_lean-candidate-reviews/`. |

None of these proves closed-loop phase locking (O1), convergence of R or B, a sharp N = 12 ON band, or anything about float64.

## Key numbers (relax-to-target law Ḃ = (η+μ)R − μ − γB, at the baseline rate constants)

- **Ungated threshold (scalar recurrence only).** Take the *ungated*, constant-R scalar recurrence B_{n+1} = max(0, B_n + dt((η+μ)R − μ − γB_n)). Its equilibrium lies strictly above B_c = 0.12 iff R > R_c = (μ+γB_c)/(η+μ) ≈ **0.454286** (`research/freezing/REPORT.md` on `main`, "Ungated ON threshold"; related errata **E12** is on `main`).
  - In the full gated model this condition is **not sufficient** while the capacity gate stays active: the update is multiplied by λ_e = min(λ_i, λ_j) ∈ (0,1].
  - The gated-OFF certificate (Thm 3) is a separate condition.
  - Do not quote 0.4543 as the full-system persistence threshold.
- B* = 0 at R = μ/(η+μ) = **3/7 ≈ 0.4286** for the same ungated scalar recurrence. This is **not** the persistence threshold.
- The main frozen production cohorts use N = 12, dt = 0.01 and the stated baseline rate constants; across them only τ, T_w and ω vary. Named ablations and exploratory/synthetic analyses are the exceptions.

## Freezing theorem (RES-FREEZE-*): CONDITIONAL — **on `main`**

- **Claim:** if, from step T on, every edge's R stays in a band that meets a strict OFF / ON / gated-OFF certificate, then the thresholded set {e : B_e > B_c} is constant for n ≥ T+N.
  - This is not convergence of B.
  - The claim is false without some hypothesis on R.
- **Open:** **O1, closed-loop phase-locking.** The theorem assumes it and nothing proves it.
- **Lean on `main`:** `lean/AIEFFreezeCore` is present and is a **`required: true`** row of `.github/workflows/lean.yml` (with AIEFProofs, AIEFProofsKn, AIEFGateCore). It covers only the per-edge OFF/ON core (`upper_geom`, `eventually_off` / `eventually_on`, `edge_eventually_off` / `edge_eventually_on`) with an existential N. The explicit N is paper-level.
- **Ledger on `main`:** four rows `LEAN-FREEZE-CORE`, `RES-FREEZE-GATED`, `RES-FREEZE-NUM`, `RES-FREEZE-NOVELTY` (`registry/claims.csv` lines 71–74). Corollary 4 uses the state-free bound ℓ_f^0. Novelty is rescoped (known variant of Cho–Dong–Ha 2023 + narrow residual; search non-exhaustive).
- **Wording debt:** the `LEAN-FREEZE-CORE` `audited_qualifier` / scope text still says "branch-only, not yet on main". That string is **stale** relative to the tree and CI (landed via PR #3, merge `2e55eb5`). Do not edit the claim row from this briefing; fix via a reviewed claims/docs PR if the owner wants it.
- **Novelty:** see `RESEARCH_LEADS.md`.

## Lean gate package (`lean/AIEFGateCore`) — **on `main`**

- **P1 (PR #19), P2 (PR #21):** branch-conditional one-step gate identities along controller-kernel directions (real arithmetic, R fixed; ERRATA E5 context), engine-shaped forms, non-vacuity witness, matrix form. Does **not** resolve AUD-RATELAW (still UNEXPLAINED after E22).
- **P3 (PR #24):** bridge to pinned `CCtrl`/`vCtrl`; n-step persistence conditional on staying in the branch, with R frozen.
- **P4a (PR #25):** guarded capacity: row sums ≤ cap under `EngineGate`, idempotence, fixed points, negations.
- **P4b (PR #26):** weight-update bridge: Lemma 1 row sandwich, trajectory invariants, per-edge ∃N OFF/ON on `stepM`, and the exact ON-certificate threshold; `onGap_N12_fails` shows that certificate cannot fire at N = 12 with engine parameters.
- **Follow-ups (PR #27):** `preM_between`, `convex_weights_iff`. Wording debt: README/SPEC still call `stepM_eq_gateM_convex` "convex"; it is affine unless 0 ≤ γ·dt ≤ 1.
- **CI:** mutation check (36 mutants on `main`) and `research/lean_gate/tests` now run in CI.
- **Not on `main` yet:** phases, delay buffer, EMA (P5, c014, c015 above).

## ControllerFiber pin note (ART-0745)

`lean/AIEFProofs/AIEFProofs/ControllerFiber.lean` changed once after the artifacts snapshot: snapshot sha256 `37c26f56…` (ART-0745) → current `b51e07e8…`. The diff is **header-only** (copyright line + `SPDX-License-Identifier: Apache-2.0`); no theorem or proof text changed. Current hash matches `AIEF_LEAN_SOURCE_SHA256SUMS.txt` and `tools/ci/check_artifact_pins.py` `KNOWN_CHANGED`. **Not a pin break.** ERRATA E7 names ART-0744 / ART-0746 for the same class of header drift but omits ART-0745 (optional wording clarification only). Safe to bridge Lean P3 against current main bytes.

## Errata numbering (`ERRATA_2026-10-28.md` on `main` @ `1c30ca5`)

- On `main`: **E1–E22** and **E24–E26**.
- **E23** is unused and intentionally absent (Lean P1 via #19 had no erratum).
- Next free number: **E27**.
- Do not renumber landed entries.

## Open / owner / docs (not PENDING science merges)

- **Docs:** `CURRENT_STATUS.md` still stamped 2026-10-23; dead tangent/cocycle paths; freeze wording and "75 rows" stale. Chronicler patch under `audit_inbox/2026-11-08_arena-chronicler_project-chronicler/recommendations/current_status_edits.patch` (apply-checked clean against `ba171d0`; `CURRENT_STATUS.md` is unchanged through `1c30ca5`) (apply from a branch cut from `main`, dual-control). `registry/studies.csv`: **11** unresolved `canonical_entrypoints` tokens in 5 study rows (re-checked 2026-11-09). `lean/AIEFProofsKn/README.md` still says the project is not in CI (false: required row). Architecture doc still says 14 studies / 43 claims (actual 15 / 80).
- **Science follow-ups:** v2 rate-law predeclared rerun; science fixes E–H; `research/freezing/REPORT.md:189` `≥ B_c` → `> B_c` (nit).
- **Owner items:** G2c (manifest/verifier self-pin gap); ART-0043; claims.csv FreezeCore "branch-only" wording.
- **v4.1:** trust-anchor E24/E25 landed; module remains an **unaudited candidate**. Full scientific audit of v4.1 and a real S01 *analysis* output are still open (distinct from the trust-guard positive control).

## Project map (box-side map, revision 2, 2026-10-29; not in the repo)

- Historical counts from 2026-10-29. Most load-bearing gaps still: **O1**; AUD-TIMESTEP / residual framing after E22; CF12 single-seed scope.
- Its note that "only AIEFProofs is in CI" / FreezeCore `required: false` is **stale**. On `main` @ `1c30ca5`, `lean.yml` requires AIEFProofs, AIEFProofsKn, AIEFFreezeCore, and AIEFGateCore.
