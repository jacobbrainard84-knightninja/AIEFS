# Project state (as of 2026-10-31, America/Toronto)

AIEFS is a hobby math project: an adaptive Kuramoto model (N = 12 oscillators) with Hebbian-style adaptive couplings B, a delay τ = 0.5, an EMA of pairwise coherence R, and a min-endpoint multiplicative capacity gate, together with Lean 4 proofs of some supporting facts.

Items marked **PENDING** have not landed on `main`. Do not cite them as results.

## Branches (checked with `git ls-remote` on 2026-10-31)

| What | Status |
|---|---|
| `main` | tip `395ea53` (merge of PR #2, 2026-10-31 09:38 EDT). It contains PR #1 `integration/round5` (merge `ddc9f46`) and `research/lean-kn` (errata E11). |
| PR #2 `fix/hygiene-allow-data-external` (head `c59eabc`) | **Merged** into `main` as `395ea53`. It adds an allow-list for binaries under `data/external/` and runs the Lean matrix on every PR. Auditor Seat 002 rated it CLEAN WITH NOTES before the merge. |
| `research/freezing` | tip `85ba0a6`. **Not merged.** The freezing work (RES-FREEZE-01, `lean/AIEFFreezeCore`, errata E12) lives only here. |
| `audit-inbox` | This drop-box branch, cut from `a991b46`. Its tree is older than `main`. |

## Key numbers (relax-to-target law Ḃ = (η+μ)R − μ − γB, at the single parameter set used everywhere)

- Settle-above-threshold condition: an edge settles above B_c = 0.12 iff R > (μ+γB_c)/(η+μ) ≈ **0.4543** (REPORT.md:213 on `research/freezing`; errata **E12** on `research/freezing`, which states it as ≈ 0.454; **PENDING** on `main`).
- B* = 0 at R = μ/(η+μ) = **3/7 ≈ 0.4286** (REPORT.md:113). This is **not** the persistence threshold. Using 0.4286 as that threshold is a known inconsistency in older files.
- All numerics use N = 12 and dt = 0.01 with one set of rate constants. Only τ, T_w and ω vary.

## Freezing theorem (RES-FREEZE-01): CONDITIONAL

- **Claim:** if, from step T on, every edge's R stays in a band that meets a strict OFF / ON / gated-OFF certificate, then the thresholded set {e : B_e > B_c} is constant for n ≥ T+N.
  - This is not convergence of B.
  - The claim is false without some hypothesis on R.
- **Open:** **O1, closed-loop phase-locking.** The theorem assumes it and nothing proves it.
- **Lean:** `AIEFFreezeCore` covers only the per-edge OFF/ON core, with an existential N. The explicit N is a paper-level real-arithmetic bound that depends on R over [T,∞).
- **PENDING (branch `research/freezing`, not yet pushed there):**
  - split the claim into 4 rows: `LEAN-FREEZE-CORE`, `RES-FREEZE-GATED`, `RES-FREEZE-NUM`, `RES-FREEZE-NOVELTY`;
  - the Corollary 4 fix: use the state-free bound ℓ_f^0 = (1 − ρ^{N1}) x* in place of the state-dependent ℓ_f. No row may cite Cor 4 until this lands.
- **Novelty:** see `RESEARCH_LEADS.md`. A rescope has been proposed. Auditor Seat 002 agreed with changes, and the ledger row is **PENDING** on `research/freezing`.

## Errata numbering (`ERRATA_2026-10-28.md`)

- `main` has E1–E11 and E13. E13 is round 5's fix to the reproduction comparator: v2 checked NaN masks but not ±inf masks, and v3 checks both. The verdict is unchanged.
- **E12 is reserved** for `research/freezing`.
- New entries start at **E14**. The README-wording draft on `r026-science-draft` is provisionally "E14 (DRAFT)".
- Renumber nothing.

## Project map (box-side map, revision 2, 2026-10-29, built from `research/freezing` cc31533 + `research/lean-kn` 2fc1110; not in the repo)

- 98 claims: 77 in the registry and 21 unregistered.
- By evidence: Lean-proved 4, exact computation 3, argument only 34, floating-point numerics 19, unverified 13, withdrawn (retracted/corrected) 25. 33 rows are conditional.
- Most load-bearing gaps:
  1. **O1** phase-locking with margin (RES-FREEZE-01).
  2. **No dt / step-size study** (AUD-TIMESTEP). The ~2e-8 rate-law residual is untested against dt/2 and dt/4.
  3. **CF12 / AUD-SCOPE-1.4:** the CF chain rests on a single seed (1 of 40), and infinite-time branch persistence is open.
- The map predates the round 5 and PR #2 merges. Its note that "only AIEFProofs is in CI" is stale. `main`'s `lean.yml` now runs AIEFProofs and AIEFProofsKn as required. It also lists AIEFFreezeCore with `required: false`, and that project is not on `main` yet.
