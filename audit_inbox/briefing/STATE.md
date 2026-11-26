# Project state (current section refreshed 2026-11-20 5:50 PM MST by Researcher 001)

AIEFS is a hobby math project: an adaptive Kuramoto model (N = 12 oscillators) with Hebbian-style adaptive couplings B, a delay τ = 0.5, an EMA of pairwise coherence R, and a min-endpoint multiplicative capacity gate, together with Lean 4 proofs of some supporting facts.

Items marked **PENDING** have not landed on `main`. Do not cite them as results. Branch verdicts are agent ratings: input only (README rule 7).

## Current state, 2026-11-20 5:50 PM MST (snapshot; PR states read from GitHub at 5:48 PM MST; re-run `git ls-remote origin` before citing)

- **`main` = `7ec6011`**, after PR #48. Earlier today: #46 (H1 metamorphic tests, merged 12:47 PM MST → `0a6a2f6`), #47 (H3 Python mutation tester, `research/h3-py-mutation` @ `e4341ca`, merged 3:57 PM MST → `d7b9fac`), #48 (H3 CI gap tests, `research/h3-gap-tests` @ `1ce14d2`, merged 5:38 PM MST → `7ec6011`; Auditor Seat 002 audit CLEAN WITH NOTES, 6 untargeted surviving mutants listed as follow-ups).
- **Merged since the 2026-11-11 snapshot below:** #28–#30 (mutation-step guard, engine step-order pins, doc drift); #31 Lean P5 (delay buffer, phase increment, coherence EMA); #32, #36 (mutation-check guards); #33 engine step-order round 2; #34, #35 (E22 step-size sweep was run, label stays UNEXPLAINED); #37, #38 c014 TrajectoryInvariants; #39 c016 coherence speed limit; #40 `check_study_paths.py`; #41, #43 phase/frequency lock (SPEC §14); #42 DelayRoots (SPEC §15); #44, #45 Arena intake: CommonRootSimple + EngineStepRef (SPEC §16); #46 H1; #47, #48 H3.
- **Open PR:** #49 `docs/freezing-report-fixes` @ `64b8f8e` (docs only, `research/freezing/REPORT.md`). Three fixes:
  - It scopes the init-gap claim to the production config: 0/200 seeds fail up to B_init_scale 0.08, 141/200 at 0.1 and 200/200 at 0.2, and it is guaranteed for B_init_scale ≤ c/11.
  - L189 `≥ B_c` → `> B_c` in the Thm 2 proof.
  - L138 gated share in the two-endpoint form `u_e·min(1, c/max(S_i, S_j))`; no RES-FREEZE result depends on the one-endpoint form.
  - The share approximation's error was 0.017–0.031 in seeded mixes, from the deposited script; this is an observation, not a bound.
  - Waits on the owner's merge.
- **Gate-form adjudication (open question 16 / TRIAGE R026-S9): done.**
  - Verdict (i): a terminology and citation fix only, and AUD-RATELAW is unaffected.
  - The engine gate is per-edge min-endpoint scaling, `B_unprojected * np.minimum.outer(scale, scale)` (engine L812).
  - Auditor Seat 002 adjudicated (audit-inbox `7d6be91`, notes folded in `fa27403`/`95605fc`). Researcher 001 reviewed it independently: CONCUR WITH NOTES, with exact Fraction witnesses W1–W5 reproduced and run against the engine lines.
- **ERRATA E27** (gate wording/citation, Miller–MacKay quotes with locations, W1/W2 witnesses): `docs/gate-form-errata` @ `755724b`. **PR [#50](https://github.com/jacobbrainard84-knightninja/AIEFS/pull/50) is open** (created 2026-11-21 02:18 MST from the audited sha `755724b`, mergeable, awaiting owner merge). Researcher 001 audited `273dcc3` (CLEAN WITH NOTES), `3b420ae` (FIXES: quote location) and `755724b` (CLEAN: location corrected to "introduction, unnumbered; also §4.3").
- **Outside scan 2026-11-25 10:08 MST (Researcher 001, read-only, leads only, nothing adopted):** top leads are Mathlib `Analysis/ODE/DiscreteGronwall.lean` (already in our pinned Mathlib; cross-check for `upper_geom` and n-step bounds); LeanPool `Kuramoto/Hebbian.lean` (Hebbian joint-Lyapunov template, plus a negative control for where it breaks with delayed EMA and the gate); LeanForControl (discrete Lyapunov/LaSalle, O1 via the history-buffer lift); Carty–Choi–Cicolani–Pignotti arXiv 2406.01703 (delayed Kuramoto sync, the template for O1 after freezing); LeanCert (interval tactics, **only in `trust := kernel` mode, never native_decide**); Hypothesis + python-flint/Arb (gate property tests vs a Fraction oracle; rigorous-bounds check of the E22 residual); arXiv 2611.24268 and 2604.04428 (homeostatic normalization, and two-cluster τ bound cross-checks). No Lean library has a Halanay inequality, which is a possible original contribution. New dependencies are an owner decision.
- **H8 (2026-11-26 ~2:15 PM MST, Researcher 001):** `RESEARCH_LEADS.md` gains verification-level tags for every entry plus the scan additions (Wang–Dong 2025 per zbMATH review; Carty 2406.01703 marked not applicable at τ = 0.5, N = 12). Audit-inbox only, no PR. Blind planted-misstatement control for Auditor Seat 002: box file `review_r001/h8_control/RESEARCH_LEADS_review_copy.md` (one planted false claim; sha256 of the sealed sentence `8b212834…79f5`). Awaiting audit.
- **H10 (2026-11-26 ~1:55 PM MST, Researcher 001):** branch `research/h10-gate-properties` @ `f31da4c` (3 ahead / 0 behind `daa977a`), not a PR. Engine gate block (extracted from the SHA-locked engine, not edited) vs exact Fraction oracle with global pre_violation + eps-band witness; M500–M503 KILLED, M505/M506 SURVIVE, E500 NOT KILLED as predeclared; **M504 predeclared SURVIVES, observed KILLED** (recorded, PREDECLARED unchanged). Spillover on synthetic cases 457/574 rows; real-run impact UNEXPLAINED. pytest 197 passed; 12 checkers rc=0. Awaiting audit.
  - **Second pass 2026-11-25 10:39 MST (correction, add-only):** Carty–Choi–Cicolani–Pignotti 2406.01703 is **not usable at our parameters**. Its conditions need R_ω·τ < π/2 (at τ=0.5, κ+max|Ω| < π, while κ must be large), and its constant c grows like Σ η^j·P(2N,j), which is ≳ 2e18 at N=12. It is a qualitative template only. New leads: Mathlib `Topology/MetricSpace/Contracting.lean` (convergence of B to B* with an explicit rate under frozen R and a frozen gate branch; not O1), Wang–Dong JDE 2025 (κ̇ = μΓ(Δθ) − γκ, the closest prior art to our Hebbian law with decay), Mathlib `Real.Angle` (cross-check for `wrapPhase`), Mathlib `Matrix.IsIrreducible`, Berner et al. arXiv 2304.05652 (related-work anchor) and LeanBlueprint. Alanazi SIADS 2025 is off-model; lasalle-lean is dropped. Cho–Ha–Kang 2025 is unverified (closed access). Proposed plan deltas H16–H19 wait for Auditor Seat 002's review of cd2dd8d.
  - **Auditor review 2026-11-25 (audit-inbox `b15c5e5`, `REVIEW_2026-11-26_auditor_scan_leads.md`):** H8 AGREE (tag each entry with how far it was checked); H9 CHANGE (target `AIEFGate.Freeze.upper_geom`, `discrete_gronwall_prod_general` only); H10 CHANGE (stdlib, not Hypothesis; oracle models the global pre_violation trigger plus an epsilon-band witness); H11 DROP (E22 on main already exact-rational); H12 CHANGE; H13 CHANGE (fixed statement, target paragraph agreed before Lean); H14 DEFER; H15 AGREE cite-only; H16 CHANGE (binding-gate case may be false, UNVERIFIED; probe numerically first); H17 CHANGE (bridge to `toIcoMod`; witness `np.mod(-1e-20, 2*pi) == 2*pi`, occurrence in runs UNEXPLAINED); H18 DROP; H19 DEFER. Split: Auditor authors H9(b)+H16 and H13; Researcher 001 authors H8, H10, H12, H17. Five drafted controls could not fail and are replaced; every mutant's kill/survive outcome is predeclared in its first commit. Researcher 001 accepts the review as the agreed plan. **Nothing is built until the owner gives a usage go-ahead.**
- **PR #51** (`audit-inbox` → `main`, 3,190 files) was opened 2026-11-21 10:05 MST and **closed unmerged by the owner at 10:16 MST**. audit-inbox stays out of main.
- **Outside drops 2026-11-21** (Auditor Seat 002, audit-inbox @ `c9a1111`, TRIAGE (k)): Arena ReachableQueue + EmaNearUnit ACCEPTED AS CANDIDATE WITH NOTES (build together, 2221 jobs, `unshare -rn`, standard axioms only), DIRECTION-7. Researcher 0282416 census rev 2 NEEDS FIX (37/49 rows verbatim; 6 proposal-equalization rows quote asserts that don't exist; 9 false 'never committed' registry rows; 21 vs their 30 unresolved tokens), DIRECTION-3. Researcher 0448126 v2 NEEDS FIX (inline scripts import a non-main engine from /home/user and re-implement the gate; the 'not Bregman' check is printed, not tested; raw log missing; NOT_RUN reasons false because v4/v4.1 are on main), DIRECTION-3.
- **PENDING branches (not on `main`; no PR exists for any of these as of 5:48 PM MST):**
  - `research/lean-gate-ema-radial` @ `0602c77`: EMA radial lemma from Arena (SPEC §17). Audited CLEAN WITH NOTES (Researcher 001: gate 979 decls, mutation 145/145, E 21/21, T 4/4, pytest 381). PR form pending.
  - `fix/validate-theta-history` @ `2c71648`: engine-side guard that `theta == history[-1]`. Audited CLEAN WITH NOTES. PR form pending.
  - `research/h2-engine-invariants` @ `cf340b4`: seeded engine-invariant property tests. PR form pending.
  - `research/h7-spec-pins` @ `e55b418`: held until ema-radial lands.
  - `arena/d4a487cc-aiefs` @ `2af3859`: owner hold; never merge the tree.
- **Owner items:**
  - The AUD-GATE wording (`registry/claims.csv` L47) and the CF02 wording (L11); both now say "node-strength (multiplicative) normalisation". The proposed wording is "symmetric per-edge min-endpoint capacity scaling", via the reconciliation script.
  - The RES-FREEZE-GATED "engine init satisfies" wording.
  - Whether to run `tools/redteam` in CI.
- **Still open:** the real-run impact of gate spillover/overshoot (non-binding rows lose weight; binding rows can end below the cap) is **UNEXPLAINED** and unmeasured.
- On 2026-11-20 the owner approved deleting 21 remote branches that were fully merged or superseded; the north-star evaluation doc was archived under `audit_inbox/salvage/2026-11-20_branch-archive/`.
- **Engine hardening plan (seats):** H1 merged (#46); H2 `cf340b4` PR form pending; H3 merged (#47, #48); H7 held; H5 later; H4 spike last; H6 doc-only.
- **Outside researchers, lanes and teams:** see `README.md` → "Lanes and teams". Every bot has its own lane; extra help is assigned as a support bot on a team lead's lane. Current directions (2026-11-20 5:15 PM MST): Arena DIRECTION-6, Researcher_0282416 DIRECTION-2, Researcher_0448126 DIRECTION-2. Researcher_040282, GPT-6 and Researcher_026 are retired; their open items were reassigned (TRIAGE (j)). (Each direction is in that bot's own `Lead Direction/`.)
- **Inbox layout** changed on 2026-11-20 (audit-inbox `594c23d`): one folder per researcher; `audit_inbox/MOVES.md` maps old paths.

## Historical snapshots (kept for the record; superseded by the section above)

## Update 2026-11-14 (Auditor Seat 002; snapshot, re-run `git ls-remote origin` before citing)
- `main` = `a559e0d` (PR #30 merged; PRs #28, #29, #30 landed since the table below). 0 open PRs at that time.
- Ready for PR, awaiting owner OK: `research/lean-gate-p5` @ `b840419` (Auditor delta check CLEAN WITH NOTES: gate 707 decls, mutation 58/58, E 10/10, typo 3/3).
- Awaiting Researcher 001 audit: `research/engine-step-order-2` @ `a2dc039` (adds d=50 production-delay probes), `fix/lean-mutation-step-guard-2` @ `59a8cc4` (needs main merge), `docs/status-truth-e22` @ `0599a24`.
- New deposits triaged in TRIAGE section (h).

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
| 015 | ClosedLoopCore | audit-inbox `cycle_015/` (not ported) | ADOPT WITH NOTES: delayed read in the phase coupling and dt are unpinned by its probes (F1/F2); fix in the port. See `audit_inbox/Researcher_040282_Inbox/Lead Direction/2026-11-11_REVIEW-2_lean-candidates-c010-c016/`. |
| 012 | EMATracking | audit-inbox `cycle_012/` | ADOPT WITH NOTES (textbook tracking bound; low priority) |
| 016 | CoherenceMotion | audit-inbox `cycle_016/` (imports P5 @ 54037ea) | ADOPT WITH NOTES: R moves at most 2(1−α) ≈ 0.00114 per step at engine α |

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

- **Docs:** `CURRENT_STATUS.md` still stamped 2026-10-23; dead tangent/cocycle paths; freeze wording and "75 rows" stale. Chronicler patch under `audit_inbox/Arena_Chronicler_Inbox/2026-11-08_arena-chronicler_project-chronicler/recommendations/current_status_edits.patch` (apply-checked clean against `ba171d0`; `CURRENT_STATUS.md` is unchanged through `1c30ca5`) (apply from a branch cut from `main`, dual-control). `registry/studies.csv`: **11** unresolved `canonical_entrypoints` tokens in 5 study rows (re-checked 2026-11-09). `lean/AIEFProofsKn/README.md` still says the project is not in CI (false: required row). Architecture doc still says 14 studies / 43 claims (actual 15 / 80).
- **Science follow-ups:** v2 rate-law predeclared rerun; science fixes E–H; `research/freezing/REPORT.md:189` `≥ B_c` → `> B_c` (in open PR #49).
- **Owner items:** G2c (manifest/verifier self-pin gap); ART-0043; claims.csv FreezeCore "branch-only" wording.
- **v4.1:** trust-anchor E24/E25 landed; module remains an **unaudited candidate**. Full scientific audit of v4.1 and a real S01 *analysis* output are still open (distinct from the trust-guard positive control).

## Project map (box-side map, revision 2, 2026-10-29; not in the repo)

- Historical counts from 2026-10-29. Most load-bearing gaps still: **O1**; AUD-TIMESTEP / residual framing after E22; CF12 single-seed scope.
- Its note that "only AIEFProofs is in CI" / FreezeCore `required: false` is **stale**. On `main` @ `1c30ca5`, `lean.yml` requires AIEFProofs, AIEFProofsKn, AIEFFreezeCore, and AIEFGateCore.

## Update 2026-11-15 (Auditor Seat 002)

- main is at `871417d`, after PR #37 (C014) and PR #38 (C014 follow-up).
- Arena_Researcher_06020041 cycles 6–10 have been reviewed. See TRIAGE (i) and `Arena_Researcher_06020041/Lead Direction/2026-11-15_REVIEW-2_cycles6-10/REVIEW.md`. Researcher 001 independently agrees on C6.
  - All results hold only for homogeneous ω and do not support any production claim.
  - C6 is superseded by phaselock. Its JSON dumps contain email addresses and must never be copied to main.
- Pending branches, in landing order:
  1. `research/lean-gate-c016`: Researcher 001's refresh.
  2. `research/lean-gate-phaselock` @ `e50102c`: Researcher 001 is auditing it.
  3. `research/lean-gate-delay-roots`: cycle 9/10 root lemmas, Auditor-authored, needs Researcher 001's audit.
- Mutant numbers shift if c016 takes extra numbers.

- 2026-11-25 (MST) Researcher 001 independent audit of research/arena-bundle @ 82a5a1f (author Auditor Seat 002): CLEAN WITH NOTES. Fresh clone, unshare -rn, SKIP_CACHE=1; reproduced gate PASS (2353 jobs, 0 warnings, 1188 decls, SHA256SUMS 42, 0 escape hatches), standard axioms only, mutants 105/105 + 85/85, E 23/23, T 4/4, pytest 439, all checkers rc 0, handoff checks (a)-(d) confirmed, own red-team (4 harness + 16 pytest variants) as predicted. Notes N1-N7 (N1: two tests can only pass; N3: Omega=0 scope wording; N4: dropped MatrixPhaseBridge caveat; N5: ~12 unmutated theorems; N6: CI 31m43s) for a follow-up branch. Owner opened PR #52 from 82a5a1f and merged it (main daa977ac). Full note: briefing/REVIEW_2026-11-25_r001_arena-bundle_82a5a1f.md.
