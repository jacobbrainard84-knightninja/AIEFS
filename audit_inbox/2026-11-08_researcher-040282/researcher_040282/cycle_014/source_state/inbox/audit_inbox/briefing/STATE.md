# Project state (as of 2026-11-09, America/Los_Angeles)

AIEFS is a hobby math project: an adaptive Kuramoto model (N = 12 oscillators) with Hebbian-style adaptive couplings B, a delay τ = 0.5, an EMA of pairwise coherence R, and a min-endpoint multiplicative capacity gate, together with Lean 4 proofs of some supporting facts.

Items marked **PENDING** have not landed on `main`. Do not cite them as results. Items marked **IN PROGRESS** are on a non-main branch and are not yet dual-control-audited / merged.

## Branches: snapshot, **not live**

**Retrieved with `git ls-remote` / local refs on 2026-11-09 at 12:06 PST (20:06 UTC) by Researcher 001.** Branch tips move. Re-run `git ls-remote origin` before citing any sha below. Verdicts are agent ratings: input only, see README rule 7.

| What | Tip at retrieval | Status |
|---|---|---|
| `main` | `ba171d0` (`ba171d062cbfe860fb3a4839b0f8ac6714527bf0`) | Merge of PR #22 (2026-11-09). Contains PRs #1–#5, #7–#12, and **#17–#22** (see below). |
| PR #17 `fix/040282-f4-f6-f7` | merge `473f929` | **Merged.** ERRATA **E19–E21** (F4 bridge self-test winner branch; F6 complex-NaN component; F7 oracle duplicate condition-status rows) plus modular suite growth. |
| PR #18 `research/rate-law-delta-sweep` | merge `27a7a9d` | **Merged.** ERRATA **E22**: AUD-RATELAW step-size sweep on the single gap component was run; under the predeclared rule the label stays **UNEXPLAINED**. Do not start a parallel sweep. |
| PR #19 `research/lean-gate-identities` | merge `525054d` | **Merged.** Lean P1 gate identities in `lean/AIEFGateCore` (required CI row). |
| PR #20 `fix/v41-trust-anchor` | merge `0f06ff0` | **Merged.** ERRATA **E24**: v4.1 `validate_run` bound to committed S01 pins (`TRUSTED_S01_POLICY` / `verify_trusted_inputs`). **E23 is unused and intentionally absent** (Lean P1 landed without an erratum). v4.1 remains an unaudited candidate (`--allow-unaudited-candidate`). |
| PR #21 `research/lean-gate-p2` | merge `0e00f98` | **Merged.** Lean P2: weakened on-support hypotheses, engine non-vacuity witness, matrix form, hardened mutation check (M1–M3 name-reference carried by step-(b) refutations). |
| PR #22 `fix/v41-trust-anchor-followup` | merge `ba171d0` | **Merged.** ERRATA **E25**: read inputs once (`O_NOFOLLOW` + `fstat`); keyword-only `policy`; run-dir name is a sanity check; in-process bypasses documented as out of scope. |
| Earlier merges (context) | — | PR #3 `research/freezing` → `2e55eb5` (**AIEFFreezeCore on main**; four freeze ledger rows). PR #4 red-team. PR #5 E15. PR #7 lint-claims. PR #8 comparator v4 / E14. PR #9 manifest G1/G2. PR #10 upload_new F1/F2. PR #11 check-sha256sums. PR #12 R026 cleanup / E16–E18. |
| `research/lean-gate-p3` | local tip = `ba171d0` (**not on `origin`**) | **IN PROGRESS (Researcher 001).** Lean P3: bridge to pinned `lean/AIEFProofs` `ControllerFiber` `CCtrl`/`vCtrl`, branch persistence, engine-shaped negations, semantic M1–M3. Worktree dirty / not pushed; **not audited**; no PR. |
| `fix/v41-followup-notes` | `19dbba3` | **IN PROGRESS.** Closes R001 notes 1/2/4/5 on the E25 follow-up; intended ERRATA **E26**. Under Auditor Seat 002 independent audit; no PR until verdict. 1 ahead of `main` `ba171d0`. |
| `audit-inbox` | (this branch) | Drop box. **Never merge it into `main`**, especially `audit_inbox/salvage/` (README rule 12). |
| `arena/d4a487cc-aiefs` | (stale vs main) | Arena working branch. **Never merge its tree.** Extract findings into the inbox instead. |
| `arena/eae4f5a6-aiefs` | `bf0c62d` | Chronicler deposit tip (PR #15 into audit-inbox). Ancestor of current inbox tip. **Not for main.** |
| `research/aiefs-northstar-evaluation` | `003522e` | One planning doc (`research/northstar/AIEFS_NORTHSTAR_EVALUATION_2026-11-08.md`) based at `eb3933c`. Useful memo; P0 rate-law sweep is already E22. |

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

- **P1 (PR #19):** branch-conditional one-step gate identities along controller-kernel directions (real arithmetic, R fixed; ERRATA E5 context). Does **not** resolve AUD-RATELAW (still UNEXPLAINED after E22).
- **P2 (PR #21):** on-support weakening, engine-shaped forms, non-vacuity witness at frozen production parameters, matrix↔edge-vector form for symmetric B/drive, hardened mutation check.
- **P3:** not on `main`. See `research/lean-gate-p3` above.

## ControllerFiber pin note (ART-0745)

`lean/AIEFProofs/AIEFProofs/ControllerFiber.lean` changed once after the artifacts snapshot: snapshot sha256 `37c26f56…` (ART-0745) → current `b51e07e8…`. The diff is **header-only** (copyright line + `SPDX-License-Identifier: Apache-2.0`); no theorem or proof text changed. Current hash matches `AIEF_LEAN_SOURCE_SHA256SUMS.txt` and `tools/ci/check_artifact_pins.py` `KNOWN_CHANGED`. **Not a pin break.** ERRATA E7 names ART-0744 / ART-0746 for the same class of header drift but omits ART-0745 (optional wording clarification only). Safe to bridge Lean P3 against current main bytes.

## Errata numbering (`ERRATA_2026-10-28.md` on `main` @ `ba171d0`)

- On `main`: **E1–E22** and **E24–E25**.
- **E23** is unused and intentionally absent (Lean P1 via #19 had no erratum).
- Next intended append: **E26** on `fix/v41-followup-notes` (not merged).
- Do not renumber landed entries.

## Open / owner / docs (not PENDING science merges)

- **Docs:** `CURRENT_STATUS.md` still stamped 2026-10-23; dead tangent/cocycle paths; freeze wording and "75 rows" stale. Chronicler patch under `audit_inbox/2026-11-08_arena-chronicler_project-chronicler/recommendations/current_status_edits.patch` still apply-checks clean against `ba171d0` (apply from a branch cut from `main`, dual-control). `registry/studies.csv`: **11** unresolved `canonical_entrypoints` tokens in 5 study rows (re-checked 2026-11-09). `lean/AIEFProofsKn/README.md` still says the project is not in CI (false: required row). Architecture doc still says 14 studies / 43 claims (actual 15 / 80).
- **Science follow-ups:** v2 rate-law predeclared rerun; science fixes E–H; `research/freezing/REPORT.md:189` `≥ B_c` → `> B_c` (nit).
- **Owner items:** add Lean (AIEFGateCore) to the branch ruleset if desired; G2c (manifest/verifier self-pin gap); ART-0043; claims.csv FreezeCore "branch-only" wording.
- **v4.1:** trust-anchor E24/E25 landed; module remains an **unaudited candidate**. Full scientific audit of v4.1 and a real S01 *analysis* output are still open (distinct from the trust-guard positive control).

## Project map (box-side map, revision 2, 2026-10-29; not in the repo)

- Historical counts from 2026-10-29. Most load-bearing gaps still: **O1**; AUD-TIMESTEP / residual framing after E22; CF12 single-seed scope.
- Its note that "only AIEFProofs is in CI" / FreezeCore `required: false` is **stale**. On `main` @ `ba171d0`, `lean.yml` requires AIEFProofs, AIEFProofsKn, AIEFFreezeCore, and AIEFGateCore.
