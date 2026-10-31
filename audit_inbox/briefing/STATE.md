# Project state (as of 2026-10-31, America/Toronto)

AIEFS is a hobby math project: an adaptive Kuramoto model (N = 12 oscillators) with Hebbian-style adaptive couplings B, a delay τ = 0.5, an EMA of pairwise coherence R, and a min-endpoint multiplicative capacity gate, together with Lean 4 proofs of some supporting facts.

Items marked **PENDING** have not landed on `main`. Do not cite them as results.

## Branches: snapshot, **not live**

**Retrieved with `git ls-remote` on 2026-10-31 at 12:57 EDT (16:57 UTC) by Researcher 001.** Branch tips move. Re-run `git ls-remote origin` before citing any sha below. Verdicts are agent ratings: input only, see README rule 7.

| What | Tip at retrieval | Status |
|---|---|---|
| `main` | `395ea53` | Merge of PR #2, 2026-10-31 09:38 EDT. It contains PR #1 `integration/round5` (merge `ddc9f46`) and `research/lean-kn` (errata E11). |
| PR #2 `fix/hygiene-allow-data-external` | `c59eabc` | **Merged** into `main` as `395ea53`. It adds an allow-list for binaries under `data/external/` and runs the Lean matrix on every PR. Researcher 001 reviewed it as CLEAN WITH NOTES. Auditor Seat 002 authored it. The branch has been deleted. |
| `research/freezing` / **PR #3** | `f444401` | **Not merged.** The 4-row claim split, the Corollary 4 fix and the novelty rescope **are at `f444401`** (see the freezing section below). Auditor Seat 002 rated the delta **CLEAN, 11/11 checks green**. It is awaiting the owner. Per Researcher 026, update it from `main` before the merge. |
| `research/redteam-negcontrols` / **PR #4** | `a614451` | **Not merged.** Red-team negative-control suite (`tools/redteam`). Rated **SOUND WITH NOTES**. It is awaiting the owner. |
| `fix/comparator-v4-gates` (E14) | `f0aadce` | **Not merged.** Comparator v4. The Researcher 001 audit @ `f0aadce` says **FIXES REQUIRED**: the CSV seed column is compared as a float, and the tolerance tests are no-ops. |
| `fix/errata-old-files-drift` / **PR #5** (E15) | `3645770` | **Not merged.** Researcher 001's delta audit of `340e5b5..3645770` says **CLEAN**. It conflicts with comparator v4 in 4 files (`ERRATA_2026-10-28.md`, `registry/artifacts_current.csv`, `tools/redteam/REDTEAM.md`, `tools/redteam/test_rt_comparator.py`), so it must land after PR #4 and E14. |
| `fix/check-manifest-g1g2` | `14072c3` | **Not merged.** It combines and supersedes `fix/manifest-nonempty` and `fix/check-manifest-missing-verifier`. The Researcher 001 audit says **FIXES REQUIRED**: the verifier is run without `python -I`, so a planted `hashlib.py` beside it defeats the hash check. |
| `fix/lint-claims-fail-closed` | `ad1470a` | **Not merged.** Makes `tools/ci/lint_claims.py` fail closed. It was audited CLEAN WITH NOTES @ `588d5ee`. The tip has since moved to `ad1470a`. |
| `fix/lint-claims-artifacts` | `f495d1c` | **Not merged.** Claims artifact, evidence-scope and Lean-citation checks. It conflicts with fail-closed. |
| `fix/lint-claims-combined` | (none at retrieval) | **Being built.** It is the combination of the two lint-claims branches. |
| `ci/check-sha256sums` | `7c3bbba` | **Not merged.** SHA256SUMS checker. After E14, remove its missing-v3-log allowance. The ruleset does **not** yet require the "SHA256SUMS files" job. |
| `arena/d4a487cc-aiefs` | `2af3859` | Arena's working branch: 180 commits behind `main`, 12 unique commits. **Never merge its tree.** Extract findings into the inbox instead. |
| `audit-inbox` | (this branch) | Drop box, cut from `a991b46`. Its tree is older than `main`. **Never merge it into `main`**, especially `audit_inbox/salvage/` (see README rule 12). A synthetic merge fails `check_current_inventory` with 172 NOT_INVENTORIED errors. |

**Deleted branches:** 5 merged branches were deleted from GitHub after a deep search confirmed all their content is in `main` (owner OK reported by Auditor Seat 002): `audit/nanfix-v2`, `ci/artifact-pins`, `ci/validator-and-lean-matrix`, `fix/hygiene-allow-data-external` and `integration/round5`. Their tips were ancestors of `main`, so their history stays reachable. Their absence was confirmed with `git ls-remote` on 2026-10-31. The check and the two review comments that exist only on PRs are in `audit_inbox/2026-10-31_grok-bot_merged-branch-salvage.md`.

## Key numbers (relax-to-target law Ḃ = (η+μ)R − μ − γB, at the baseline rate constants)

- **Ungated threshold (scalar recurrence only).** Take the *ungated*, constant-R scalar recurrence B_{n+1} = max(0, B_n + dt((η+μ)R − μ − γB_n)). Its equilibrium lies strictly above B_c = 0.12 iff R > R_c = (μ+γB_c)/(η+μ) ≈ **0.454286** (`research/freezing/REPORT.md:114` @ `f444401`, "Ungated ON threshold"; errata **E12** on `research/freezing` gives ≈ 0.454; **PENDING** on `main`).
  - In the full gated model this condition is **not sufficient** while the capacity gate stays active: the update is multiplied by λ_e = min(λ_i, λ_j) ∈ (0,1] (REPORT.md:108).
  - The gated-OFF certificate (Thm 3, REPORT.md:193) is a separate condition.
  - Do not quote 0.4543 as the full-system persistence threshold.
- B* = 0 at R = μ/(η+μ) = **3/7 ≈ 0.4286** for the same ungated scalar recurrence (REPORT.md:113). This is **not** the persistence threshold. Using 0.4286 as that threshold is a known inconsistency in older files.
- The main frozen production cohorts use N = 12, dt = 0.01 and the stated baseline rate constants; across them only τ, T_w and ω vary. Explicitly named ablations (for example `no_mu` or delay removal) and separately labelled exploratory or synthetic analyses (for example exogenous-R freezing checks, finite-difference amplitudes, exploratory gate analyses) are the exceptions.

## Freezing theorem (RES-FREEZE-01): CONDITIONAL

- **Claim:** if, from step T on, every edge's R stays in a band that meets a strict OFF / ON / gated-OFF certificate, then the thresholded set {e : B_e > B_c} is constant for n ≥ T+N.
  - This is not convergence of B.
  - The claim is false without some hypothesis on R.
- **Open:** **O1, closed-loop phase-locking.** The theorem assumes it and nothing proves it.
- **Lean:** `AIEFFreezeCore` covers only the per-edge OFF/ON core, with an existential N. The explicit N is a paper-level real-arithmetic bound that depends on R over [T,∞).
- **On `research/freezing` @ `f444401` (PR #3), not yet on `main`:**
  - The claim is split into 4 rows: `LEAN-FREEZE-CORE`, `RES-FREEZE-GATED`, `RES-FREEZE-NUM` and `RES-FREEZE-NOVELTY` (`registry/claims.csv:71-74` on that branch).
  - The Corollary 4 fix is there too: the proof uses the state-free bound ℓ_f^0 = (1 − ρ_f^{N1})·x*_f in place of the state-dependent ℓ_f (`research/freezing/REPORT.md:221-226`).
  - These are pushed to the branch. They are **PENDING only in the sense that PR #3 is not merged**. Cite them as `research/freezing@f444401`, not as `main`.
- **Novelty:** see `RESEARCH_LEADS.md`. The rescope is at `f444401` (`REPORT.md:16`, row `RES-FREEZE-NOVELTY`): a known variant of Cho–Dong–Ha 2023, with a narrow, plausibly new residual. The search is not exhaustive.

## Errata numbering (`ERRATA_2026-10-28.md`)

- `main` has E1–E11 and E13. E13 is round 5's fix to the reproduction comparator: v2 checked NaN masks but not ±inf masks, and v3 checks both. The verdict is unchanged.
- **E12 is reserved** for `research/freezing`.
- New entries start at **E14**, which `fix/comparator-v4-gates` (comparator v4) takes. **E15 is now taken** by Auditor Seat 002's old-files-drift erratum (`fix/errata-old-files-drift` / PR #5, not merged). The science README-wording draft (`r026-science-draft`) takes the **next free number** when it lands, not E15. If E14 or E15 lands out of order, the later one to reach `main` renumbers its entry.
- Otherwise renumber nothing.

## Project map (box-side map, revision 2, 2026-10-29, built from `research/freezing` cc31533 + `research/lean-kn` 2fc1110; not in the repo)

- 98 claims: 77 in the registry and 21 unregistered.
- By evidence: Lean-proved 4, exact computation 3, argument only 34, floating-point numerics 19, unverified 13, withdrawn (retracted/corrected) 25. 33 rows are conditional.
- Most load-bearing gaps:
  1. **O1** phase-locking with margin (RES-FREEZE-01).
  2. **No dt / step-size study** (AUD-TIMESTEP). The ~2e-8 rate-law residual is untested against dt/2 and dt/4.
  3. **CF12 / AUD-SCOPE-1.4:** the CF chain rests on a single seed (1 of 40), and infinite-time branch persistence is open.
- The map predates the round 5 and PR #2 merges. Its note that "only AIEFProofs is in CI" is stale. `main`'s `lean.yml` now runs AIEFProofs and AIEFProofsKn as required. It also lists AIEFFreezeCore with `required: false`, and that project is not on `main` yet.
