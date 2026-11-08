# Audit (Researcher 001): fix/lint-claims-fail-closed @ 588d5ee (Auditor Seat 002's G5b/G6b/G6c/G6d fix)

Date: 2026-10-31, report finished about 12:45 EDT. Repo: jacobbrainard84-knightninja/AIEFS. origin/main = 395ea53. Previous audit: AUDIT_fix3_a428c32_fix5_37b9026.md.
Read-only. Nothing was pushed and no PRs were opened. The work was done in throwaway worktrees (/workspace/wt_lc588, wt_lc588_old with 37b9026's lint_claims.py, wt_lc588_main), all **removed** afterwards. Evidence: /workspace/audit_r001/lc588/evidence/. Harnesses: /workspace/audit_r001/lc588/adv/ (adv_lc.py has 57 cases × old/new × strict/non-strict; swallow_repro.py).
Python: 3.13.5 (system; numpy 2.5.4, pandas 3.0.6), plus 3.12 for the CI unittests. Run as a non-root user, so the chmod 000 tests ran and were not skipped.

## Verdict: **CLEAN WITH NOTES**

The fix is correct and minimal. It closes G5b, G6b, G6c and G6d plus the BOM, non-UTF-8, unreadable and CSV-parse cases with one ERROR line each, exit 1 and no traceback. There are no false positives on main's real tree, and no pinned or hash-listed file changed. Every claimed number reproduced, with two caveats: (1) the "red-team tree identical to a614451" claim is worded inaccurately (no content issue, see C5), and (2) the red-team result of 70 pass / 11 xfail holds only with pandas 3.0.6. Under requirements.txt's pinned pandas==3.1.0, two comparator tests fail. That is pre-existing in a614451 and not caused by this branch (O1).
The new findings are low or low-medium. F1 is pre-existing on 37b9026 and is a one-line follow-up. None of them blocks a merge.

## Claims

| # | Claim | Status | Evidence |
|---|---|---|---|
| C1 | G6b, G6c, G5b and G6d each give one ERROR line, exit 1 and no traceback (G6b was a NOTICE that passed even with --strict) | **Verified** | adv_lc.log. On 37b9026, g6b_renamed (both status columns), g6c_dup_col, g5b_header_only (also header plus blank lines) and g6d_later_dup PASS rc 0. On 588d5ee they give one ERROR and rc 1, with and without --strict. g6d_earlier_dup was already rc 1 on 37b9026 in the real-README setup (see note below), and now gives the explicit 2-headings ERROR. |
| C1b | BOM in claims.csv, README.md or the fallback; a non-UTF-8 byte; chmod 000; a CSV parse error: one ERROR line, exit 1, no traceback | **Verified**, with a qualification | All one ERROR line, rc 1, no traceback (lint_claims.py:86-102, 198-199). The old file gave tracebacks for non-UTF-8, UTF-16, chmod 000 (claims, README and fallback) and field-too-large. Qualification: the fallback file is only read when README has no vocabulary block, so a BOM in an *unused* fallback passes (case bom_fallback_unused). That is consistent and harmless, but the docstring at :41 reads as unconditional. In practice the only reachable csv.Error is "field larger than field limit" (131072); NUL bytes and unterminated quotes do not raise (F1, F6). |
| C2 | Tests assert exact lines, including '== result' | **Verified**, with a nit | CI: assertLines (whole-line match) plus assertResult (last line equals exactly) on every new test except test_bom_fails (test_ci_tools.py:191), which checks the ERROR line and no traceback but not the result line. Red-team: assertLintFails (test_rt_claims_hygiene.py:48) checks rc 1, no traceback, whole lines and the exact last line. |
| C3 | The strict test uses a warning-only input (SSRH-ORIG → Retired / Superseded); it passes without --strict and fails with it | **Verified** | test_rt_claims_hygiene.py:137 asserts `0 error(s), 1 warning(s) -> PASS` / `-> FAIL`. The CI counterpart (test_ci_tools.py:102) was already warning-only at 37b9026 and has been tightened to exact lines. Both pass against 37b9026's lint_claims, as expected, because --strict already worked there. They are rewrites, not new regression controls. |
| C4 | 7 red-team negative controls added; every new CI and red-team test fails against 37b9026's lint_claims.py | **Verified** (the 7 + 7 new tests) | New tests on 588d5ee with 37b9026's lint_claims.py swapped in: **CI** 110 run, failures=6 errors=2. All 7 new CI tests fail (renamed, dup header, header-only, two headings, BOM ×2 subtests, non-UTF-8, unreadable) (ci_newtests_oldlint.log). **Red-team** claims file: all 7 new controls FAIL (renamed ×2 subtests, dup column, header-only, earlier vocab, BOM, non-UTF-8, unreadable) (rt_claims_newtests_oldlint.log). The rewritten strict tests pass on old, as noted in C3. |
| C5 | Red-team tree after merge da85dbd is identical to a614451's | **Not verified as worded**. The substance is fine | `git rev-parse da85dbd:tools/redteam` = 0358ac9 ≠ a614451:tools/redteam = 3f209e4. The whole da85dbd tree equals 37b9026's (`git diff 37b9026 da85dbd` is empty), so the merge only records ancestry. The tools/redteam difference from a614451 is exactly 37b9026's own G5/G6 edits to REDTEAM.md and test_rt_claims_hygiene.py. This is expected because 47a8b31 and a614451 share tree 7a51fed. No red-team content was lost or introduced by the merge. The correct statement would be: "the red-team base content is identical; tools/redteam differs from a614451 only by 37b9026's G5/G6 edits". |
| C6 | REDTEAM.md has no hard-coded counts | **Verified** | The header totals were removed (REDTEAM.md:56-59). The only remaining numbers are per-row "(3 tests)", "(4 tests)" and "(5 tests)", which are row descriptors, and "About 70 s". Nit: :59 "Tables reflect branch `fix/lint-claims-fail-closed`" will be stale once merged. |
| C7 | CI 110 OK | **Verified** | 110 OK on 3.12 and 3.13 (ci_py312.log, ci_py313.log). 103 + 7 new. |
| C8 | Red-team 81 tests: 70 pass, 11 xfail, 0 unexpected, 0 skipped | **Verified with system pandas 3.0.6** | redteam.log: 81 tests, 70 ok, 11 expected failures, 0 skipped, 0 unexpected, rc 0, git status clean. **In a venv with pandas 3.1.0 (the requirements.txt pin) the result is 2 FAIL**: test_csv_cell_off_by_1e_9 and _just_over_tolerance (redteam_auditvenv.log). test_rt_comparator.py, rtcommon.py and the comparator are identical to a614451, so this is not caused by this branch. See O1. |
| C9 | Main's real tree passes lint_claims with and without --strict | **Verified** | 588d5ee's lint_claims run with `--repo` against an origin/main worktree: `checked 76 claim rows; 0 status violation(s)`, `0 error(s), 0 warning(s), 0 notice(s) -> PASS`, rc 0 in both modes (lint_main_tree*.log). |
| C10 | All repo checks rc 0 | **Verified** | checks_588d5ee.log, all rc 0: validate_registry, hygiene_scan --base origin/main, check_artifact_pins (2898 rows), check_current_inventory, verify_inventory_current, check_manifest (145 files / 24 inputs), lint_claims, lint_claims --strict, check_modes --strict. SHA256SUMS: 4 of 5 OK. audits/reproductions/b2a95dfbfbe3/SHA256SUMS fails as on every revision including main (pre-existing; the compare_..._v3.log it lists is missing). |
| C11 | No pinned files touched | **Verified** | 37b9026..588d5ee changes 5 files: registry/artifacts_current.csv (only the 4 rows for the changed files re-hashed, all `not_in_snapshot`), tools/ci/lint_claims.py, tools/ci/tests/test_ci_tools.py, tools/redteam/REDTEAM.md and tools/redteam/test_rt_claims_hygiene.py. The intersection with every registry/artifacts.csv path, every entry of the SHA256SUMS files, the SUMS files themselves, the two lean `*_SHA256SUMS.txt` files, .gitignore, registry/artifacts.csv and check_artifact_pins.py is **empty**. |

Note on C1, G6d: the "earlier duplicate block wins" bypass in my previous audit used an earlier block that *adds* Proved. In adv_lc.py's real-README setup the old file already failed, because the earlier block replaced the vocabulary and the real rows' values were no longer in it. g6d_later_dup (rc 0 → rc 1) and the author's own red-team control (Proved-only earlier block plus a Proved row, which fails on 37b9026) show the change in behaviour.

## Judgement 1: a BOM in README.md as an ERROR

**Sound, with low false-positive risk.** Evidence:
- None of the 3011 tracked files at 588d5ee start with a BOM.
- registry/README.md, registry/claims.csv and tools/ci/claim_statuses.txt have no BOM on any of the 25 origin refs, or in any historical commit that touched README.md or claims.csv.
- The only writer of claims.csv (registry/reconciliation/build_claims_reconciliation.py:497) writes `encoding="utf-8"` (no BOM) and reads without `-sig` (:456), so a BOM there would break the builder as well. Rejecting it is consistent.

For README.md, the error has no security value: the heading is never on line 1, so a BOM could not hide or alter the vocabulary. It also fails closed, with a clear one-line fix message. The only realistic source is an old Windows editor, and the GitHub web editor does not add one. If the owner prefers leniency, the alternative is to strip a README BOM with a WARNING, which --strict would still fail. Either choice is defensible, and the current one is acceptable.

## Edge inputs I tried (adv_lc.log; old = 37b9026, new = 588d5ee)

| Input | old | new | Judgement |
|---|---|---|---|
| CRLF claims.csv; CRLF with 'Proved'; CR-only with 'Proved'; CRLF README (± 'Proved') | PASS / FAIL as expected | same | OK. csv and splitlines normalise |
| Header ` audited_status` / `audited_status ` / `\u200baudited_status` (with 'Proved') | **PASS rc 0** | ERROR "status column 'audited_status' missing" | OK (G6b covers it) |
| Trailing spaces after the whole header line (last column becomes `legacy_list_refs   `) | PASS | PASS | OK (unchecked free-text column) |
| Empty `audited_status` / `artifact_status`, whitespace-only, short row | FAIL | FAIL ("'' is not in the status vocabulary") | OK |
| Status ending in NBSP; Cyrillic homoglyph 'Ѕupported' | FAIL | FAIL | OK (exact match) |
| Extra column `audited_status ` (trailing space) next to the real one, with 'Proved' | PASS | **PASS** | **F2** |
| Extra column `Status` / `status` / `Audited_Status` with 'Proved' in every row | PASS | **PASS** | F2 (by design for free-text columns; see F2) |
| Two empty header names (`,,` at the end of the header) | PASS | ERROR duplicate column '' | OK (fail closed) |
| Quoted newline in `statement`, 'Proved' on the next row | FAIL (line 5) | FAIL (line 5, correct physical line) | OK. Note: for a multi-line row, `line` is the row's *last* physical line (reader.line_num) |
| Quoted newline inside the status value | FAIL | FAIL | OK |
| **Unterminated quote at EOF swallowing an appended 'Proved' row** | PASS | **PASS (also --strict)** | **F1** |
| NUL byte inside a field | PASS | PASS | F6 |
| `## Status vocabulary` quoted inside a code fence later in README | PASS | ERROR (2 headings) | F5 (false positive, fail closed) |
| 4-space-indented `    ## Status vocabulary` (markdown code, not a heading) | PASS | PASS (used as the heading) | F5 |
| `##  Status vocabulary` (2 spaces) earlier, adding Proved | FAIL | FAIL | OK (not a heading match, so not used) |
| Second fence under the same heading adding Proved | FAIL | FAIL | OK (only the first fence is used) |
| claims.csv is a directory; README is a directory; 0-byte claims | FAIL | FAIL | OK |
| UTF-16 claims.csv | FAIL with traceback | ERROR not valid UTF-8 (0xff at offset 0) | OK |

## Findings (ranked)

**F1 (low-medium; pre-existing, also on 37b9026; same "silent pass" class): malformed CSV with an unterminated quote at EOF passes.** tools/ci/lint_claims.py:195 builds `csv.DictReader(...)` with the default `strict=False`, so an unterminated quoted field at EOF is accepted silently. Repro (adv/swallow_repro.py): append `"` to the empty last field (`legacy_list_refs`) of the last row, then a line `FAKE-01,...,Proved,...,Proved,...`. lint_claims prints "checked 76 claim rows; 0 status violation(s)" and PASSes rc 0, also with --strict. The raw file and a raw diff show a 'Proved' row, but `pandas.read_csv` raises "EOF inside string" and `csv.reader(strict=True)` raises "unexpected end of data". check_current_inventory.py:73 (a different file) uses a non-strict DictReader as well. Fix: pass `strict=True` to the DictReader at :195. The existing `except csv.Error` at :198 then reports it as one ERROR line. The real claims.csv parses cleanly in strict mode (76 rows; checked). Add one CI and one red-team control.

**F2 (low): near-duplicate status columns are not checked.** lint_claims.py:207-215 detects duplicates and missing columns by exact name only. A second column `audited_status ` (trailing space) holding 'Proved' passes, and GitHub renders it identically to the real `audited_status`, so a reviewer can read the wrong one. This is a visual variant of G6c. `Status`, `status` and `Audited_Status` also pass, which is acceptable by design because only named columns are linted. Fix: compute duplicates over `h.strip().casefold()`, and ERROR on any header name with leading or trailing whitespace. That is two lines, and the real header has none.

**F3 (low; test coverage):** no test exercises the csv.Error path (lint_claims.py:198-199). Only the field-limit error reaches it today, and F1 would add the strict-mode errors. Tests for BOM, non-UTF-8 and unreadable cover claims.csv (both suites) and README BOM (CI only). There are none for the README or fallback non-UTF-8/unreadable cases or for the fallback BOM. My harness shows they all behave correctly, but nothing pins that behaviour. test_bom_fails (test_ci_tools.py:191) does not assert the result line.

**F4 (low; claim accuracy):** the C5 wording (see above), and REDTEAM.md:59 naming the branch, which goes stale on merge.

**F5 (info):** heading detection is purely line-based (lint_claims.py:111, :118, using `ln.strip() == VOCAB_HEADING`). A quoted heading inside a code fence is a false-positive ERROR (fail closed), and an indented-code "heading" is accepted. Neither occurs in the real README.

**F6 (info):** a NUL byte in claims.csv passes (Python ≥ 3.11 csv accepts NUL). It could be rejected in read_text (:86-102) alongside the BOM check.

**F7 (info):** `--columns ""` lints no status columns and PASSes (lint_claims.py:266 → `checked = []`, no missing-column errors). CI uses the default, so this only matters for manual use. It could ERROR when the column list is empty.

## Out of scope, but please route

**O1 (red-team suite a614451 / comparator; medium for the suite's credibility):** test_rt_comparator.py's `first_finite_numeric_cell` skips `seed_index` (0) and picks the **uint64 `seed` column** (11242426753702356865). There, `v + 1e-9` and `v + 1e-11` are below float64 resolution (`v + 1e-9 == v`). The two "tolerance" tests therefore only rewrite the seed in float notation (≈ 1.1242426753702357e19, an integer change of about 135). They do not test the 1e-12 tolerance, and their verdict depends on the pandas version: they pass under pandas 3.0.6 and **fail (comparator ACCEPTS) under the pinned pandas==3.1.0**, where csv_worst_abs_diff was 6.7e-16. Two consequences:
1. The suite's "70 pass" result depends on the environment.
2. The comparator compares integer columns via `to_numpy(dtype=float)`, so changes to large integer seeds can be invisible.

Suggested fixes: the red-team picks a float column with |v| ~ 1, and the comparator compares integer columns exactly. This is relevant to my separate comparator-v4 audit (f0aadce).

## What to fix before merge (optional; none blocking)
1. `strict=True` at lint_claims.py:195, plus a test (F1).
2. Normalised duplicate detection and an ERROR on whitespace in header names (F2).
3. Reword C5 in the PR description; drop the branch name at REDTEAM.md:59.
