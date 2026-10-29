# Conditional finite-time support freezing (AIEF discrete model)

Research note, added 2026-10-29. Full write-up: [`REPORT.md`](REPORT.md). Ledger row: `RES-FREEZE-01` in
`registry/claims.csv`. Lean: [`lean/AIEFFreezeCore`](../../lean/AIEFFreezeCore/README.md).

## Scope, in one paragraph

This is a **conditional theorem**. It says that if, from some step T on, every edge's coherence R_e stays in
a band that satisfies one of three strict certificate inequalities (OFF, ON, gated-OFF), then every edge's
status `B_e > B_c` is constant from step T + N on. The hypothesis amounts to **phase-locking (and drifting)
with a margin**, and whether the closed-loop AIEF dynamics (phases + delay + EMA + gated weights) always
produce it is **open** (REPORT.md §3.5, O1). Without some hypothesis on R the statement is false: an
exogenous periodic R makes an edge flip forever (§3.4).

## What is proven, and where

| Statement (REPORT.md §3) | Status | In Lean? |
|---|---|---|
| Lemma 1 (gate sandwich: row sums ≤ c, gate factor bracketed by drive quantities) | PROVEN (paper proof), unconditional | no |
| Theorem 2 (OFF and ON certificates, explicit N) | PROVEN (paper proof), conditional on R on [T,∞) | per-edge ∃N form only: `edge_eventually_off`, `edge_eventually_on` (via `upper_geom`, `eventually_off`, `eventually_on`) |
| Theorem 3 (gated-OFF certificate for large locked cliques) | PROVEN (paper proof), conditional | no |
| Corollary 4 (limit form) | PROVEN (paper proof), conditional | no |
| Unconditional freezing for the weight map | FALSE (numerical counterexample, §3.4) | n/a |
| Closed-loop locking with margin (O1), ties (O2), multistability (O3), a-priori N (O4) | OPEN | no |

"PROVEN (paper proof)" means a written proof in REPORT.md, checked by a read-only audit (verdict: sound with
wording fixes, all applied, §9); it is not machine-checked. The Lean file covers only the scalar comparison
core and the per-edge OFF/ON statements (with `max(0,·)` clipping and an arbitrary gate factor), and those
are existential (`∃ N`).

## Caveats that must travel with any citation

* **Explicit N: real arithmetic only, paper-level.** The explicit N formulas are proven for the
  real-arithmetic map, on paper; Lean has only `∃ N`. On float64, rounding in the B update can break the
  explicit N at tiny margins (a 1e-13 OFF margin gave a last flip 492 steps after the predicted freeze), so
  `freeze_check.py` only certifies when the margin is ≥ `MARGIN_GUARD` = 1e-9 (an engineering bound, not
  a proven float error bound). REPORT.md §3.6.
* **7-clique certificate needs R spread ≲ 2e-4.** The gated-OFF certificate (Thm 3) for a locked group of 7
  is only issued when the R band on the group is very tight: spread ≲ 2e-4 (issued for w ≤ 2e-4, not for
  w ≥ 3e-4, although the group stays OFF). `clique7_check.py`, REPORT.md §3 Thm 3.
* **Numerics: 1,412 certified (run, T) pairs, 0 violations.** "Certified" means all 66 edges certified at T
  with the R-band hypotheses checked only over the **finite simulated window [T, 80000)** (steps up to
  80000), not over [T, ∞). 5 repo seeds plus no-delay, random-ω, near-identical-ω stress and B-reset
  variants. `results.json`, `run_log.txt`, REPORT.md §4.
* **Novelty: plausibly new as a model-specific result, but elementary.** The core is comparison with a
  scalar affine contraction. The search (arXiv API queries and a short web search on 2026-10-28) found no
  prior statement of finite-time threshold-support freezing with an explicit bound for adaptive/Hebbian
  Kuramoto networks under a capacity gate; closest work is asymptotic (e.g. edge snapping, Hebbian
  constraints). The search was **not exhaustive** (no full-text search, no Google Scholar). REPORT.md §5.

## Files and how to re-run (from the repo root; needs numpy)

| file | what |
|---|---|
| `freeze_check.py` | simulator (exact re-implementation of the default engine step), certificates, checks, counterexample; writes `results.json` here. `--crosscheck` compares 3000 steps with the repo engine `aief_experiment_engine_v1.py` (imported read-only); `--out PATH` writes elsewhere |
| `results.json`, `run_log.txt` | main numerical results (with the margin guard) |
| `guard_check.py`, `guard_check.json`, `guard_check_log.txt` | float-margin test, unguarded vs guarded |
| `clique7_check.py`, `clique7_check.json`, `clique7_check_log.txt` | 7-clique R-spread test of the Thm 3 certificate |
| `margins.py`, `margins.json` | certificate margins at T = 48000 |
| `arxiv_search.py`, `arxiv_search2.py`, `arxiv_search_log.json` | arXiv query log of the novelty search (network access; not needed to re-run anything else) |
| `inrepo_rerun_log.txt` | 2026-10-29 in-repo re-run: engine cross-check 0.0, all JSON outputs byte-identical |
| `lean/check.sh` | runs `lean/AIEFFreezeCore/check_lean_freeze.sh` |

```
python research/freezing/freeze_check.py --crosscheck --out /tmp/results.json   # several minutes
python research/freezing/guard_check.py      # rewrites guard_check.json here
python research/freezing/clique7_check.py    # rewrites clique7_check.json here
python research/freezing/margins.py          # rewrites margins.json here
SKIP_CACHE=1 research/freezing/lean/check.sh
```

All scripts resolve paths relative to their own location and import nothing from outside the repo.
They are not run by CI. The pre-audit backups of the original scratch directory are not included.
