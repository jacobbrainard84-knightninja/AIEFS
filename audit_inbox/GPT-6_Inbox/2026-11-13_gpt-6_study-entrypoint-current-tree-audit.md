# GPT-6 review — current-tree study entrypoint integrity

- Agent: GPT-6
- Date: 2026-11-13 (Europe/Tirane)
- Main reviewed: `a559e0d30458bb01989ac47225675d6baec518b8`
- Main tree: `bfafbf1deb4e0ec58fa1fa0ec115bb9193efdc1c`
- Inbox branch before deposit: `69221804302921302ca1500ed79d5400cc3663ac`
- Scope: re-check every `registry/studies.csv` canonical-entrypoint token on current main; verify CI coverage and stale status references; static audit of the previously deposited checker prototype.
- Method: fetched the complete recursive Git tree for the exact main commit and parsed the current studies CSV independently. Reviewed the inbox checker and tests as untrusted text only. **Did not execute either inbox script or its tests.**

## 1. Current-main referential-integrity result

**Classification: confirmed registry integrity gap.**

At main `a559e0d30458bb01989ac47225675d6baec518b8`, the recursive Git tree is `bfafbf1deb4e0ec58fa1fa0ec115bb9193efdc1c`: 3,265 entries, 3,095 blobs, GitHub reports `truncated=false`. The current `registry/studies.csv` blob is `86a39aeaff94502cb8a549da50be4205f8a1d454`.

I independently parsed all **15 study rows / 37 canonical-entrypoint tokens** and compared them with every tracked blob path in that tree. **11 tokens do not resolve**:

| CSV line | Study ID | Missing token | Check |
|---:|---|---|---|
| 3 | `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `AIEF_1_0_*.py` | glob, zero matches |
| 3 | same | `AIEF_1_1_*.py` | glob, zero matches |
| 3 | same | `AIEF_1_2_*.py` | glob, zero matches |
| 5 | `AIEF_1_3_DISJOINT_100SEED` | `AIEF_1_3_sensitivity_audit_updated.py` | exact path absent |
| 5 | same | `AIEF_1_3_persistence_mechanism_test_updated.py` | exact path absent |
| 7 | `AIEF_1_4_MATCHED_PHASE_ABLATION` | `AIEF_1_4_driver_mechanism.py` | exact path absent |
| 10 | `AIEF_1_4_TANGENT_AND_COCYCLE` | `aief_1_4_full_state_tangent_operator.py` | exact path absent |
| 10 | same | `aief_1_4_history_cocycle_test.py` | exact path absent |
| 10 | same | `aief_1_4_branch_tangent_comparison.py` | exact path absent |
| 12 | `AIEF_1_4_CONTROLLER_FIBER` | `aief_1_4_intertwining_controller.py` | exact path absent |
| 12 | same | `aief_1_4_fiber_coordinate_controller.py` | exact path absent |

The other 26 tokens in all 15 rows resolved. This is the same 11-token set as the earlier Part 7 note, but it has now been rechecked against the current `main` tree after PRs #28–#30. The CSV blob itself remains the same blob as in that earlier review.

This is a **registry referential-integrity defect**, not evidence that the associated studies, evidence directories or scientific conclusions are invalid. No alias has been inferred solely from a similar filename.

## 2. Related paths are leads, not verified replacements

The current tree includes several related but differently named files, including:
- `AIEF_1_3_analysis.py`, `AIEF_1_3_falsification_updated.py`, and the extant `AIEF_1_3_paired_statistics_updated.py` / `AIEF_1_3_closure_diagnostics_updated.py`;
- `AIEF_1_4_augmented_tangent_cocycle_analysis.py`, `AIEF_1_4_cocycle_controls_coupled_comparison.py`, and `AIEF_1_4_frozen_driver_cocycle_analysis.py`;
- `AIEF_1_4_intertwining_controller_analysis.py`.

These are not byte/path matches for the missing tokens, and their scientific/provenance equivalence has not been established here. In particular, `registry/supersessions.csv`, blob `c256888eecec39c160a543b756cca5a2558072b5`, lines 15–16, maps the old AIEF-1.3 sensitivity and persistence scripts to the same updated filenames that are absent from the current tree. This is a broken lineage target, not permission to substitute a different analysis.

The tangent/cocycle discrepancy is repeated in `CURRENT_STATUS.md`, blob `c51401924a2179ce87eaf107b01515e2d3f4e37f`, line 46, which still lists the three missing entrypoints. The controller-fiber row in `studies.csv` line 12 also needs explicit reconciliation against the current `AIEF_1_4_intertwining_controller_analysis.py` and evidence folder; the latter is not automatically the same executable as the missing root-level token.

## 3. CI does not currently enforce this field

The active `.github/workflows/repo-checks.yml`, blob `790a1e429d01b1f17f97cada9b7db43325cec79d`, has jobs for CI-tool self-tests, claims lint, hygiene, manifests, SHA256SUMS, artifact pins, file modes, current inventory and analysis tests (lines 23–208). It has no study-entrypoint validation step. A current-tree path search also finds no study/entrypoint checker under `tools/ci/`.

The existing `tools/ci/check_current_inventory.py`, blob `0471299194219395d8e94b12494cdccc474c192e`, lines 2–25, checks the generated `registry/artifacts_current.csv` against tracked files and ZIP members. That is not a substitute for validating `registry/studies.csv`'s references. The registry README, blob `b3ab739359393aae5d1e02aded5d4c6885981144`, line 144, describes `studies.csv` as an index containing entrypoints, but does not specify their matching/glob rules.

## 4. Static review of the previously deposited checker prototype

**Classification: prototype has a wildcard path-boundary defect; do not integrate it unchanged.**

The prior inbox prototype `audit_inbox/2026-11-10_gpt-6_check_study_entrypoints.py`, blob `e10bb1c7edfd04f0267273f665327962475bbb26`, lines 23–26, uses:

```python
fnmatch.fnmatchcase(path, token) and (
    "/" not in token or path.count("/") == token.count("/")
)
```

When a glob token has no slash, the first disjunct is always true, so the code does not impose a root-level path restriction. Python's `fnmatch` wildcard `*` can match a slash; consequently a token such as `*.py` can match a nested tracked path such as `nested/entry.py`. If `canonical_entrypoints` means repository-root-relative entrypoint patterns, that is a false acceptance.

The companion test `audit_inbox/2026-11-10_gpt-6_test_check_study_entrypoints.py`, blob `0db012ab180f1dcd7f34c3613e19157b98e83e12`, lines 14–16, does not catch this: the test pattern `AIEF_1_0_*.py` cannot match `archive/AIEF_1_0_old.py` even without a path-depth check, because the unmatched `archive/` prefix comes before the pattern's literal `AIEF` prefix.

A discriminating negative test is:
- pattern: `*.py`
- tracked set: `{"nested/entry.py"}`
- expected: no match for a root-level glob.

For root-relative semantics, require `path.count("/") == token.count("/")` for every glob (or use a matcher with explicit path-separator semantics). If recursive globs are intended, define and test that behavior separately, e.g. explicit `**`. Also decide whether globs may resolve to multiple matches; the current prototype accepts any nonempty match set.

This is a static review only. The inbox prototype remains untrusted and was not executed. The prototype's six reported test passes are submitter-provided evidence, not independent verification.

## 5. Recommended repair path

1. Reconcile each missing token against the actual current executable and its evidence. For retired/historical material, mark the path as archived or update/remove the canonical token through a reviewed registry change; do not create placeholder scripts.
2. Define `canonical_entrypoints` path semantics explicitly: repository-root-relative exact tracked-file paths and a narrowly specified glob syntax/cardinality rule.
3. Repair the prototype's slashless-glob handling and add the discriminating nested-path negative control above, alongside exact-path, no-match, traversal, duplicate-ID and malformed-column controls.
4. Add an independent standard-library validator and its tests to `tools/ci/`, then wire them into the existing `repo-checks` workflow. Validate all 15 rows. Check `canonical_evidence_paths` separately rather than silently expanding this validator's scope.

## Scope and disposition

- Current main tree independently checked: **15 rows, 37 tokens, 11 unresolved**.
- Current-tree CI configuration read; no tests or scripts executed.
- The earlier study-entrypoint submission remains `NEW` / untriaged in `audit_inbox/TRIAGE.md`, blob `f1dfe9d800d710e7d9590bce15b25bf209da4eb8`, line 150.
- No main, registry, CURRENT_STATUS, workflow, briefing, TRIAGE or existing inbox file was changed.

**UNVERIFIED INPUT — not independently triaged or promoted.**
