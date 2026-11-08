# Audit: comparator v4 / E14 port — `fix/comparator-v4-from-main` @ `74936b3`

Auditor: Auditor Seat 002 · Date: 2026-11-07 (~08:00 Europe/Tirane)
Scope: commit `74936b3` (port of reviewed `fix/comparator-v4-gates` @ `902abe8` onto `main` @ `2e55eb5`). Read-only: no push, no PR, no pinned-file edit.

## Verdict: **CLEAN** for the comparator port, with one process note (must refresh onto current main before PR)

The reviewed comparator payload from `902abe8` is present and byte-identical for the reproduction and red-team comparator files. Gates that closed Researcher's FIXES REQUIRED on `f0aadce` (O1 exact integer CSV compare; named NOT REPRODUCED instead of traceback; float-column tolerance tests) are present and pass under requirements-pinned pandas 3.1.0.

### Process note (blocks PR as-is)
- Branch tip is 1 commit ahead of `2e55eb5`, but current `origin/main` is `58d5543` (PR #7 `fix/lint-claims-combined` merged).
- `git merge-tree` against current main reports conflicts in `registry/artifacts_current.csv` (both sides changed).
- Action for Researcher 001: rebase or re-port onto current main, regenerate `artifacts_current.csv`, then open the PR. Do not merge `74936b3` as-is.

### Port fidelity (`902abe8` vs `74936b3`)
| Path | Match |
|---|---|
| `audits/reproductions/b2a95dfbfbe3/{SHA256SUMS,ERRATUM,v3.log,v3_to_v4.diff,v4.log,v4.py}` | SAME |
| `tools/redteam/test_rt_comparator.py` | SAME |
| `ERRATA_2026-10-28.md`, `tools/redteam/REDTEAM.md`, `registry/artifacts_current.csv` | DIFF (expected: main already had E12/E15 and later inventory; E14 is present and ordered before E15) |

### Evidence (box)
Worktree: `/workspace/wt_cmp_from_main` @ `74936b3`
Logs: `/workspace/audit_r001/cmpv4_74936b3/evidence/`

| Check | Result |
|---|---|
| `sha256sum -c` (10 files) | OK |
| Red-team (`unittest discover -s tools/redteam`, pandas 3.1.0 / numpy 2.5.1) | Ran 120, OK, expected failures=12; dirty tree empty |
| CI tool self-tests | Ran 103, OK |
| Real `compare_b2a95dfbfbe3_v4.py` | exit 0, verdict REPRODUCED, `problems: []`; O1 keys present (`csv_integer_columns`, empty `csv_integer_cells_differing`) |
| Committed v4.log vs this run | Verdict equal; `csv_worst_rel_diff` differs at ~1e-16 (8.47e-16 vs 1.15e-15), both << TOL 1e-12. Info only. |
| `check_artifact_pins`, `check_current_inventory`, `verify_inventory_current`, `check_manifest`, `lint_claims`, `check_modes --strict`, `hygiene_scan --base origin/main --pii` | all rc 0 |

### Hoped-for-result hunt (checklist)
- Integer CSV path no longer float-casts seeds (O1); red-team `test_O1_csv_seed_plus_1` and float tolerance tests target float columns.
- No always-pass: 12 named expected failures remain; suite not empty of negatives.
- Zip pin and SUSPICIOUS exact-copy gates retained from prior review.
- No edits to hash-pinned `artifacts.csv` / audit_manifest in the diff vs base.

### Out of scope / next serial
- Independent CLEAN of merged lint-claims-combined on main was still pending per earlier notes; owner already merged PR #7. Not re-opened here.
- After this PR lands on main: audit/refresh `fix/check-manifest-g1g2`, then `ci/check-sha256sums`, then `fix/r026-cleanup`.
