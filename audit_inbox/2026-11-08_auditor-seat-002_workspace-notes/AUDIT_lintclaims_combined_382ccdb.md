# Independent audit: lint-claims combined

**Verdict: CLEAN WITH NOTES**

Audited 2026-11-07 07:34 (Europe/Tirane).
Target: `382ccdb9d19b2c7f1dd3c23aa0ff774f56c5a5a8`, `origin/fix/lint-claims-combined`.
Baseline: current fetched `origin/main`, `2e55eb5`.

## Method and boundaries

Performed personally with local git, source reads, independent temporary-fixture probes, and Python stdlib unittest in `/tmp/lcc`. Fetched origin first and verified the remote tip. No cloud agents, pytest, branch edits, commits, pushes, deletions, or PR creation. The target worktree was clean before testing and remained tracked-clean afterward. This replaces the earlier blocked/stub audit; that stub was not a verdict.

This is an audit of the lint hardening and its merge, not a new independent proof of the scientific claims or a rerun of every Lean project. The lint cannot certify that a cited theorem proves a ledger statement.

## Findings

### N1 — F5 remains an explicit low-severity GAP

`tools/ci/lint_claims.py:233-255` uses `ln.strip()` to recognize the vocabulary heading and fences. A four-space-indented `    ## Status vocabulary` line is therefore accepted as an actual Markdown heading. An altered block can add `Proved`; an associated claim then passes, also though the heading renders as code. My independent probe reproduced exit 0 at both main and the audited tip. The red-team case `test_GAP_indented_vocabulary_heading` at lines 462-470 records this as an expected failure, not a fixed vulnerability. The documentation correctly still calls it a GAP. Bot-fixable follow-up: reject Markdown code-indented headings/fences (ideally also fenced-code context), add positive heading controls, promote F5 out of expectedFailure, and regenerate only the current inventory. This is pre-existing, explicitly scoped and disclosed, not merge damage; it does not block the other hardening from being reviewed in a PR.

### N2 — Cited Lean file existence is not theorem verification

`check_artifacts` (`lint_claims.py:156-180`) requires an existing `.lean` file for a formal scope or recognized Lean-proof wording, but does not inspect its theorem content. A deliberately false numerical theorem citing an unrelated existing Lean file is still accepted, as the explicit `test_GAP_lean_file_content_not_checked` shows. This is a documented scope limit, not scientific validation. Lexical wording recognition has bounded regex windows (40/20 characters); these are text heuristics, not tuned numerical scientific tolerances. Actual proof/claim correspondence remains a human/research review responsibility.

### N3 — One narrow missing-artifact exception remains visible

The production allow-list has exactly one `(claim_id, path)` entry, `AUD-REPRO-B2A95` and the absent reproduction comparison log. The lint prints one NOTICE, even under `--strict`; it is not claiming that log exists. It rejects unrelated missing artifacts and stale allow-list entries (restored file or removed citation). Restoring the log or correcting its ledger citation is a separate bot/research follow-up, not a reason to widen the exception. The synthetic exception injected by tests is test-only, not a production weakening flag.

## Requested fail-closed checks

Source review and actual negative controls confirm:

| Case | Audited behavior |
|---|---|
| G5b: header only / zero rows | ERROR, exit 1 (`_lint_rows:413-414`) |
| G6b: missing/renamed status column | ERROR, exit 1 (`356-359`); tested with and without strict |
| G6c: duplicate headers | ERROR, exit 1 (`339-355`); shadowed values cannot produce success |
| G6d: multiple vocabulary headings | ERROR, exit 1 (`273-277`), no first-block-wins pass |
| BOM | explicit BOM ERROR, exit 1, no traceback (`214-216`) |
| Non-UTF-8 | byte/offset diagnostic, exit 1, no traceback (`221-226`) |
| Unreadable file | `cannot be read (PermissionError: Permission denied)`, exit 1 (`208-213`) |
| F1: unterminated quote swallowing appended row | strict CSV reader raises parse ERROR, exit 1, also with strict (`322-330`) |
| F2: whitespace/casefold header duplicates | normalized duplicate ERROR, exit 1; whitespace additionally diagnosed |
| NUL | explicit offset ERROR, exit 1 (`217-220`) |
| Empty `--columns` | ERROR before checking rows, exit 1 (`299-302`) |
| Strict mode | warning-only input: exit 0 normally, exit 1 with strict; errors fail in either mode (`441`) |
| F5: indented heading | still GAP, not fixed; see N1 |

Unit coverage also exercises BOM/non-UTF-8 in README and fallback, malformed quote text mid-file, and unreadable README/fallback. These permission tests were not skipped in the CI test run. I additionally injected a PermissionError at the file reader boundary and checked its exact diagnostic; that supplemental simulated error is not being represented as a chmod-based OS test.

The independent script `independent_lint_probes.py` runs 17 cases against both main's extracted linter and the target linter on the same temporary mirror, preserving the actual ledger and artifact tree. Full outputs: `independent_lint_probes.json`. Main accepts G5b/G6b/G6c/G6d, empty-columns and swallowed-row probes that the target rejects. Both accept the positive control and F5. Both correctly distinguish the warning-only strict control. Some bad-byte/header inputs also fail on main for different/less precise reasons: the report does not claim every fixture was previously a silent pass.

## Was deleting `test_vocabulary_missing_is_caught_with_strict` intentional?

**Yes: the historical deletion at `588d5ee` was intentional, not an accidentally dropped strict-mode guarantee.** Its commit message explicitly says the strict test was changed to a warning-only input (PASS without strict, FAIL with it). After missing vocabulary became an unconditional ERROR, that old missing-vocabulary test no longer proved strict actually changed the verdict. `test_vocabulary_missing_fails_without_strict` covers the fail-closed rule; `test_strict_fails_a_warning_only_input` and unit `test_strict_turns_warning_into_failure` cover strict's distinct behavior.

Important correction to the premise: **at `382ccdb`, the old named red-team test is present again**, at `tools/redteam/test_rt_claims_hygiene.py:318-324` (retained from the other side of the combine). It is redundant but valid and ran successfully. Nothing needs restoring. My independent matrix also tests missing vocabulary with and without strict.

## Combine integrity

Both `f495d1c` (A/artifacts) and `ad1470a` (fail-closed) are ancestors of the audited tip. The merge parents are `84622dc` and `2e55eb5`.

Ancestry alone was not used as a substitute for review. I read the diffs from each side and the whole resulting linter/tests. A's `resolve_artifact`, `parse_scope_vocab`, and `check_artifacts` functions are AST-identical in the target. A's required artifact-column failures and stale allow-list validation remain connected to the row-checking flow. The fail-closed `read_text` function is AST-identical; strict CSV parsing, duplicate normalization, missing columns/registry/vocabulary, zero rows, NUL and empty-columns checks all remain active alongside the artifact checks.

Changed test names are deliberate behavior updates, not lost coverage: A's notice-only missing-registry and warning-only missing-vocabulary tests become unconditional rejection tests; its retired-origin warning test becomes a stronger paired strict control. The old GAP names for missing registry/vocabulary and nonexistent artifacts/false formal claims are promoted to normal rejecting negative tests. `union_test_names.json` records the raw name comparison. The intended union is intact.

## Anti-tautology / owner checklist

No always-pass or tautological tests were found in the changed tests. Positive controls require exit 0; negatives invoke the real linter and require nonzero/exact diagnostics, many with exact error counts and result lines. The strict controls use the same warning-only input twice and require opposite verdicts. Several combined artifact negatives use `assertRejected` (nonzero plus message) rather than exact exit 1; that is somewhat weaker, but not vacuous. The gap decorator only treats the explicit 'checker ACCEPTED' assertion as an expected failure: unrelated broken fixtures become visible skips; a newly working checker becomes an unexpected success.

The unit suite clears the live missing-artifact allow-list only in synthetic temporary repos, whose rows do not cite the real entry. Full-tree red-team controls separately use and exercise the real entry and stale-entry checks. This is fixture isolation, not a synthetic production manifest. The inventory check regenerates hashes from bytes and compares canonical content; it does not validate scientific truth. No scientific seed selection, numerical threshold/tolerance loosening, NaN comparisons, unconditional pass return, new broad silent fallback, or pinned-file manipulation appears in the branch diff. The pre-existing status fallback is explicit, announces use, and fails if neither source yields values; malformed input yields errors rather than a successful fallback.

## Inventory, pinned files, and refresh integrity

Only five paths differ from main:

- `registry/artifacts_current.csv`
- `tools/ci/lint_claims.py`
- `tools/ci/tests/test_ci_tools.py`
- `tools/redteam/REDTEAM.md`
- `tools/redteam/test_rt_claims_hygiene.py`

The inventory has **3401 data rows**, matches deterministic regeneration in memory, and differs from main only in the hashes/sizes of the four changed tooling/documentation files. The generator and pin validator themselves are unchanged. The snapshot `registry/artifacts.csv`, manifests, SHA256SUMS, scientific scripts, and Lean source files have no branch-specific modifications. Pin validation passed with its pre-existing 7 known-changed and 52 known-missing entries; those are not new exemptions introduced here.

For `84622dc..382ccdb`, all 39 changed paths belong to the incoming-main change set. Every changed path other than the regenerated inventory and combined red-team documentation is byte-identical to incoming `2e55eb5`. The documentation delta from pre-refresh is exactly the incoming matched-phase-anchor section, preserving the lint sections; the linter, unit test file and claims red-team file are byte-identical before/after refresh. No evidence of merge damage or a lost side was found. `git diff --check 2e55eb5..382ccdb` passes.

## Executed checks

- `python3 -m unittest discover -s tools/ci/tests -v`: **120 tests, OK**, no skips. Log: `ci_tests_382ccdb.log`.
- `python3 -m unittest discover -s tools/redteam -v`: **109 tests, OK (expected failures=12)**: 97 ordinary successes, 12 confirmed GAPs, no skips, no unexpected successes. Log: `redteam_382ccdb.log`. This actual discovery count supersedes any earlier aggregate counts in handoff notes. The 12 GAPs are: claims F5 and Lean content (2); hygiene full-scan binary warning, token in large text, token in allowed binary (3); comparator swapped branch labels and manifest schema (2); empty-data manifest and missing-verifier wrapper (2); Lean marker attribute-prefixed axiom and hidden admitGoal (2); missing matched-phase anchor rows (1). These are known-false inputs still accepted by their respective gates, not successful negative rejection controls.
- `python3 tools/ci/lint_claims.py`, also `--strict`: **80 rows, 0 errors, 0 warnings, 1 known-missing NOTICE, PASS**.
- `python3 tools/ci/check_artifact_pins.py`: **2898 rows, 0 errors**, 2839 matching, 7 known-changed, 52 known-missing.
- `python3 tools/ci/check_current_inventory.py`: **0 errors, PASS** (in-memory regeneration; no branch edit).
- `python3 tools/ci/check_manifest.py`: **1 verifier, 0 failed**, 145 published files and 24 inputs checked; verifier explicitly notes 2 post-manifest logs not hashed.
- `python3 tools/ci/check_modes.py`: **0 errors, 119 warnings**, PASS.
- `python3 tools/ci/hygiene_scan.py --base 2e55eb5`: **0 errors, 0 warnings**, PASS.
- `python3 tools/ci/hygiene_scan.py`: **0 errors, 3 existing BIG_FILE warnings**, PASS; change-scoped scan above is clean. Log: `hygiene_full_382ccdb.log`.
- Independent 17-case matrix and supplemental read-error diagnostic: all observations matched the stated expectations.

Commands were not retried after failures; expected rejection of a negative fixture is not an infrastructure failure. No pinned files were edited to make a test pass.

## Recommendation / ownership

A PR for this exact tip is appropriate: it is a useful, independently reviewed hardening union, **CLEAN WITH NOTES**, not a claim that every red-team GAP is closed. Opening/posting is outside this report-only task and was not done. Check the forge's CI at the exact tip before presenting it as merge-ready; this audit does not assert remote CI or fresh Lean builds are green.

Bot-fixable follow-ups: F5 parser tightening and promotion of its GAP test; resolve the narrow missing-log citation; optionally consolidate the redundant strict missing-vocabulary test. Research/owner judgment: substantive ledger-to-theorem correspondence, acceptance/prioritization of documented scope limits, and final merge approval. No user input was needed to perform this audit.

Usage checked during the audit: **1.8% of weekly usage limit**, below the owner's 50% stop threshold. No other agent or user was messaged.
