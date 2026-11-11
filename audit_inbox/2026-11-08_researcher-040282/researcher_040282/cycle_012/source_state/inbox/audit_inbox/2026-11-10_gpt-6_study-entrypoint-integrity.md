# Part 7 — `registry/studies.csv` canonical-entrypoint integrity

**Agent:** GPT-6  
**Date:** 2026-11-10 (Europe/Tirane)  
**Main reviewed:** `543e7e1aaa11e4c810783806cb180eee36ec5313` (merge PR #23)  
**Main tree:** `9f5469090bdb4e0414b9fb4c5ed4311eced89f00`  
**Audit-inbox tip before deposit:** `0ffca8393c58d369590ffeb13a7aad097276a8c5`  
**Scope:** Independently enumerate the current tracked main tree; check every `canonical_entrypoints` token in the five study rows flagged by OPEN_QUESTIONS item 13; inspect CI coverage and potential renamed/replacement entrypoints.

## Finding

**The 11 unresolved canonical-entrypoint tokens remain unresolved on the live main after PR #23.** The current `registry/studies.csv` is blob `86a39aeaff94502cb8a549da50be4205f8a1d454`. I enumerated the recursive Git tree at main's tree SHA above (3,246 entries; GitHub reported `truncated=false`) and checked each token in the five affected rows. Eleven tokens have no tracked-file match: three root-level globs and eight exact file paths.

This is a registry referential-integrity gap, not evidence that the associated studies or their evidence are scientifically invalid. Some files with related names exist, but none is automatically interchangeable with the missing canonical token.

## Exact unresolved tokens

| `studies.csv` row | Token | Result |
|---:|---|---|
| 3 — `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `AIEF_1_0_*.py` | no tracked match |
| 3 | `AIEF_1_1_*.py` | no tracked match |
| 3 | `AIEF_1_2_*.py` | no tracked match |
| 5 — `AIEF_1_3_DISJOINT_100SEED` | `AIEF_1_3_sensitivity_audit_updated.py` | exact path absent |
| 5 | `AIEF_1_3_persistence_mechanism_test_updated.py` | exact path absent |
| 7 — `AIEF_1_4_MATCHED_PHASE_ABLATION` | `AIEF_1_4_driver_mechanism.py` | exact path absent |
| 10 — `AIEF_1_4_TANGENT_AND_COCYCLE` | `aief_1_4_full_state_tangent_operator.py` | exact path absent |
| 10 | `aief_1_4_history_cocycle_test.py` | exact path absent |
| 10 | `aief_1_4_branch_tangent_comparison.py` | exact path absent |
| 12 — `AIEF_1_4_CONTROLLER_FIBER` | `aief_1_4_intertwining_controller.py` | exact path absent |
| 12 | `aief_1_4_fiber_coordinate_controller.py` | exact path absent |

The other tokens in these five rows were present: AIEF-1.3 paired statistics and closure diagnostics; the matched-phase memory-ablation script; the frozen-driver cocycle script; and the actual-admissibility and component-controller audit scripts. The three glob tokens were checked against the complete recursive tracked-file list, not only root files. No root-level AIEF 1.0/1.1/1.2 script matching those patterns exists.

## Related files and reconciliation leads

These are candidates for human reconciliation, **not verified aliases**:

- AIEF-1.3: `registry/supersessions.csv` blob `c256888eecec39c160a543b756cca5a2558072b5`, rows 15–16, records old-to-updated mappings for the sensitivity audit and persistence-mechanism test. Both the old and updated named script paths are absent from the current main tree. Do not silently substitute another analysis.
- Tangent/cocycle: current tree contains `AIEF_1_4_augmented_tangent_cocycle_analysis.py`, `AIEF_1_4_cocycle_controls_coupled_comparison.py`, and `AIEF_1_4_frozen_driver_cocycle_analysis.py`. The latter is already the fourth token in row 10. The first two may be more current entrypoints for parts of the work, but their scientific and provenance equivalence to the three missing scripts has not been established.
- Controller fiber: current tree contains `AIEF_1_4_intertwining_controller_analysis.py` (case and name differ) and the `aief_1_4_intertwining_controller 02/` evidence directory. Whether this is the intended canonical executable for the absent `aief_1_4_intertwining_controller.py` token needs confirmation. No exact `aief_1_4_fiber_coordinate_controller.py` file was found.

The current-status document repeats some of the stale tangent/cocycle references: `CURRENT_STATUS.md` blob `c51401924a2179ce87eaf107b01515e2d3f4e37f`, line 46 names the same three absent scripts. Its surrounding study summary should be reconciled together with the registry rather than independently patched.

## CI coverage

No current CI check enforces this contract:

- `.github/workflows/repo-checks.yml`, blob `a2f313f82c947c20ea7b717f67b1ad7251f39737`, defines CI-tool tests, claims lint, hygiene, manifest, SHA256SUMS, artifact pins, file modes, current inventory, and analysis tests. There is no study-entrypoint validation step.
- `tools/ci/check_current_inventory.py`, blob `0471299194219395d8e94b12494cdccc474c192e`, lines 2–25 explicitly checks that `registry/artifacts_current.csv` matches tracked files and zip members. It does not validate `registry/studies.csv`.
- `registry/README.md`, blob `b3ab739359393aae5d1e02aded5d4c6885981144`, line 144 describes `studies.csv` as a structured index with entrypoints, but the retrieved README does not define or enforce token-resolution semantics.
- GitHub code search for `canonical_entrypoints` on this repository returned only `registry/studies.csv`; no validator implementation or test currently references the field.

The existing current-inventory CI cannot catch this defect: a file can be perfectly inventoried while a study registry entrypoint points to a nonexistent path.

## Recommended repair path

1. Have the study owners reconcile each missing token against the actual current executable and its evidence. For a retired or historical script, explicitly mark it as historical/archived or remove it from the canonical-entrypoint field through a reviewed registry update. Do not fabricate placeholder scripts just to satisfy a path check.
2. Clarify that semicolon-separated tokens are repo-root-relative paths; exact tokens must be tracked files, and glob tokens must match at least one tracked file. Decide whether a glob with multiple matches is valid or needs explicit cardinality.
3. Add a standard-library CI validator that parses the CSV with `csv.DictReader`, enumerates tracked paths with `git ls-files -z`, rejects empty/unsafe tokens, and fails on missing exact paths or unmatched globs. Add positive and known-false negative unit tests.
4. Run it against all study rows, not just these five, and review `canonical_evidence_paths` separately as a distinct integrity question. Keep the validator independent of `artifacts_current.csv`.

A standalone checker/test prototype accompanies this note. It is not integrated into main CI and has not been run against a full local checkout of main; its six unit tests cover exact/glob success, missing exact/glob rejection, directory-boundary behavior, path traversal and duplicate study IDs.

**Disposition:** deposited as **UNVERIFIED INPUT for independent triage**. No main, registry, CI, CURRENT_STATUS, briefing, TRIAGE or existing inbox file was modified.
