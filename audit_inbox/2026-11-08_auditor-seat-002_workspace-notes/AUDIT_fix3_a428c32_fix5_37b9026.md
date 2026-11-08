# Audit (Researcher 001 auditor seat): fix/check-manifest-missing-verifier @ a428c32 (G2), fix/lint-claims-fail-closed @ 37b9026 (G5/G6)

Date: 2026-10-31, run 12:05–12:20 EDT. Repo: jacobbrainard84-knightninja/AIEFS, origin/main = 395ea53, red-team base = research/redteam-negcontrols @ a614451.
Local only. Nothing was pushed, no PRs were opened, main was not touched and nobody was contacted. Work is in /workspace/audit_r001/fix35/ (one clone, `repo/`; evidence in `evidence/`; harnesses in `adv/`).
Environment: Python 3.13.5. CI uses 3.12 and pytest isn't installed, so the pytest steps were not run. They weren't in the requested list.

## Verdicts

| Branch | Verdict | One line |
|---|---|---|
| a428c32 (G2) | **CLEAN WITH NOTES** | The fix is correct and minimal, the claimed numbers reproduce exactly and no pinned files are touched. There is a new GAP: a stub or empty verifier still PASSes (G2b). Small doc nits. It needs a rebase onto a614451 and a fixture update when combined with b166c03. |
| 37b9026 (G5/G6) | **FIXES REQUIRED** (small) | G5 and G6 are correctly closed, the claimed numbers reproduce and there are no false positives on main. But the same function still silently skips status checks when a status column is renamed or duplicated. That is the same failure class G6 fixes, and it's a confirmed end-to-end bypass of every repo check. A header-only claims.csv and an earlier duplicate vocab block also PASS. These take about 10 lines to fix in the same branch. |

## 1. Refs, scope and pinned files

- Both branches contain main 395ea53. **Neither sits on a614451**. Each carries its own copy of the red-team commit: a428c32 and 37b9026 on 47a8b31, b166c03 on 33d34ca. The copies have the same tree (7a51fed) and parent (395ea53) but a different SHA, so git sees add/add conflicts (see §5).
- Diff vs its base, a428c32: tools/ci/check_manifest.py, the new tools/ci/tests/test_check_manifest.py (5 tests), tools/redteam/REDTEAM.md, tools/redteam/test_rt_hashes.py (GAP converted to `test_verifier_missing_fails`) and registry/artifacts_current.csv (regenerated).
- Diff vs its base, 37b9026: tools/ci/lint_claims.py (2 hunks), tools/ci/tests/test_ci_tools.py (2 tests updated), tools/redteam/test_rt_claims_hygiene.py, tools/redteam/REDTEAM.md and registry/artifacts_current.csv.
- Pinned-file intersection is **empty** for a428c32, 37b9026 and b166c03. I checked every path in registry/artifacts.csv, every entry of the 5 SHA256SUMS files, the SHA256SUMS files themselves, the root .gitignore (ART-0001), registry/artifacts.csv and tools/ci/check_artifact_pins.py.
- The diffs are minimal. The only change outside the fix plus its tests and docs is the regenerated inventory, which is required.

## 2. Re-run results (evidence/checks_<label>.log, summary_<label>.txt)

| Rev | CI unittest | Red-team | validate_registry | hygiene --base origin/main | pins | current_inv | verify_inv | check_manifest | lint_claims | check_modes --strict |
|---|---|---|---|---|---|---|---|---|---|---|
| main 395ea53 | 103 OK | n/a (no suite) | PASS | PASS | PASS (2898 rows) | PASS | PASS | PASS (145 files / 24 inputs) | PASS (76 rows, 0 violations) | PASS |
| a614451 | 103 OK | 74 tests, 13 expected GAPs | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| **a428c32** | **108 OK** | **74, 12 expected GAPs, 0 unexpected successes** | PASS | PASS (10 files) | PASS | PASS | PASS | PASS | PASS | PASS |
| **37b9026** | **103 OK** | **74, 11 expected GAPs, 0 unexpected successes** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| scratch/combo 7ac16e9 | 108 OK | 76, 9 expected GAPs | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

- Both teams' claimed numbers are **confirmed**. The working tree was clean after every run.
- `audits/reproductions/b2a95dfbfbe3/SHA256SUMS` fails `sha256sum -c` on **every rev including main**, because compare_b2a95dfbfbe3_v3.log is listed but not in the tree. This is pre-existing and unrelated to these branches. The other 4 SUMS files are OK everywhere.
- No false positives on main's data: lint_claims at 37b9026 and check_manifest at a428c32 both PASS on the real registry and manifests.

## 3. a428c32 (G2): adversarial results (adv/adv_g2.py; evidence/adv_g2.log, adv_g2_main_fix3.json, adv_g2_b166_combo.json)

| # | Input | main | a428c32 | Judgement |
|---|---|---|---|---|
| 1 | verifier path is a directory | PASS rc0 (gap) | ERROR "manifest verifier missing ... NOT checked", rc1 | OK. The text says "missing" for a directory; acceptable |
| 2 | dangling symlink | PASS rc0 | ERROR missing, rc1 | OK |
| 3 | file renamed (case change) | PASS rc0 | ERROR missing, rc1 | OK |
| 4 | whole evidence folder removed | PASS rc0 | ERROR missing, rc1 | OK |
| 5 | chmod 000 | rc1 "exited 2" + python "can't open file" | same | OK |
| 6 | syntax error | rc1 | rc1 | OK |
| 7 | verifier SIGKILLs itself | rc1 "exited -9" | same | OK |
| 8 | empty audit_manifest.json | rc1 "exited 2" | same | OK |
| 9 | **0-byte verifier** | PASS rc0 | **PASS rc0** | **NEW GAP G2b** |
| 10 | **`sys.exit(0)`, no output** | PASS | **PASS** | **G2b** |
| 11 | **comment-only verifier** | PASS | **PASS** | **G2b** |
| 12 | **prints "FAILED", exits 0** | PASS | **PASS** | **G2b** |
| 13 | **symlink to an outside exit-0 stub** | PASS | **PASS** | **G2b** |

The results are identical on the b166c03 + a428c32 combo. b166's coverage check reads the manifest itself, not the verifier, so it doesn't catch this.

**G2b (new GAP):** check_manifest trusts rc 0 from whatever file is at the verifier path. `verify_manifest.py` is not pinned in registry/artifacts.csv: no `verify_manifest` rows and no `AI Agent Audits/evidence` rows. The only place it's listed is its own audit_manifest.json, which a stub never checks. The bypass requires a deliberate edit, but so does G2. Suggested fixes (either one):
- (a) Before running the verifier, check_manifest checks its sha256 against `files_sha256["evidence/verify_manifest.py"]` in the manifest. It already loads the manifest in the b166 combo.
- (b) Require a success line from the verifier (e.g. `checked N published files ... OK`) and parse N > 0.

(a) is stronger. Neither option touches pinned files.

**Notes:**
- REDTEAM.md line 56 still says "74 tests: 61 PASS incl. 11 controls, 13 GAP". It should be 62/12 on this branch.
- The G2 table row still cites "check_manifest.py (line 41)".
- The 5 new tests use substring needles, not exact messages. That's fine, but it should be described that way.

## 4. 37b9026 (G5/G6): adversarial results (adv/adv_g56.py, 33 cases, run against main's and the fix's lint_claims in temp repos built from the real README, claims.csv and claim_statuses.txt; evidence/adv_g56.log/.json)

**Newly fail closed on 37b9026 (all PASS rc0 on main).** Each gives a "no status vocabulary found ... status values were NOT checked" ERROR, rc1:
- vocab heading case changed
- heading misspelled
- heading at ### level
- empty fence
- unterminated fence
- prose between the heading and the fence
- a duplicate section whose first fence is empty
- README missing (placeholder fallback)

claims.csv as a directory or a dangling symlink now gives "claims registry missing, nothing was linted", rc1.

**Already failing on main and still failing (OK):**
- 0-byte claims.csv, whitespace-only, `;` delimiter, tab delimiter, and `claim_id` renamed all give "no 'claim_id' column".
- Extra field: caught.
- Duplicate id with trailing space: caught.

**Fail closed but with a poor message (note):**
- A BOM in claims.csv gives "no 'claim_id' column", which is misleading. Open with `utf-8-sig` or report the BOM explicitly.
- A non-UTF-8 byte and chmod 000 give rc1 with a Python traceback.

**Acceptable PASS:**
- CRLF claims.csv. Normalised by csv; a CRLF row with 'Proved' is still caught.
- CRLF or BOM in README. Vocab still parsed and still enforced.
- Trailing spaces on the heading. Still parsed.
- A *later* duplicate vocab section. First block wins; harmless.

**NEW GAPs (PASS rc0 on main and on 37b9026):**
- **G6b (high): status column renamed.** For example, `audited_status` → `audited_status_v2` with a row set to `Proved`. lint_claims only emits a NOTICE ("linting (none)") and PASSes, **even with --strict**. Confirmed end to end on the 37b9026 tree, with the inventory regenerated: lint_claims, lint_claims --strict, check_current_inventory, verify_inventory_current, check_artifact_pins (registry/claims.csv is not pinned), hygiene_scan and check_modes --strict **all PASS**. The tree was restored afterwards and git status is clean. Renaming `artifact_status` is caught only crudely, by a KeyError traceback in verify_inventory_current. This is the same "status values were NOT checked → PASS" class that G6 fixes, in the same function.
- **G6c: duplicate `audited_status` header column** with `Proved` in the first copy. DictReader keeps the last copy, so the bad value is shadowed and the file PASSes.
- **G5b: header-only claims.csv (0 rows)** PASSes, "linted 0 rows". This is the claims analogue of G1 (b166c03).
- **G6d: an *earlier* duplicate "## Status vocabulary" block** that adds `Proved` wins silently, so `Proved` becomes legal.

**Required fix (small, in lint_claims.py; suggested):**
- ERROR if an expected status column (`audited_status`, `artifact_status`) is missing from the header.
- ERROR on duplicate header names.
- ERROR when there are 0 data rows.
- ERROR on more than one vocab heading. Alternatively, fail if the vocab sections differ.

Add the 4 cases above as red-team tests. With these, the branch would be CLEAN.

**Notes:**
- REDTEAM.md line 56 is stale here too. It should be 63/11.
- "All 6 ClaimsLint PASS tests assert exact messages": they assert **substring needles** (`assertRejected(rc, out, *needles)`), not exact messages. That is true of the 6 tests, but the wording overstates it.
- The `--strict` test's needle "no status vocabulary found" now also appears without --strict, so that test no longer proves --strict does anything. Assert something specific to strict mode instead.

## 5. Overlap and merges (scratch branches, local only)

| Merge | Conflicts |
|---|---|
| a428c32 + b166c03 | artifacts_current.csv, check_manifest.py, REDTEAM.md, test_rt_hashes.py |
| a428c32 + a614451 | artifacts_current.csv, REDTEAM.md, test_rt_hashes.py |
| 37b9026 + a614451 | artifacts_current.csv, REDTEAM.md, test_rt_claims_hygiene.py |
| a428c32 + 37b9026 | artifacts_current.csv only |

- Every red-team-file conflict comes **only from the rewritten base**: three copies of the same tree under different SHAs.
- `git rebase --onto a614451 47a8b31` (or `33d34ca`) is clean for all three branches, and the resulting diffs are identical to the originals:
  - a428c32 → 6d19a5b
  - 37b9026 → 38017af
  - b166c03 → 038c23e
- **Real conflict:** check_manifest.py between G1 and G2. Resolve it by keeping both:
  - the G2 missing-verifier ERROR
  - b166's coverage block and paragraph
  - exit-code doc: "1 = a verifier failed or is missing, or its manifest covers no data"
  - drop the obsolete `ran == 0` notice
- **Semantic conflict:** after merging, 2 tests in a428c32's new test_check_manifest.py fail: `test_passing_verifier_passes` and `test_no_inputs_flag_drops_inputs_arg`. Their stub verifier has no audit_manifest.json, so b166's coverage check reports "cannot read manifest". Fix: the `verifier()` helper writes evidence/data.txt plus an audit_manifest.json with a matching files_sha256 and a non-empty inputs_sha256.

**Recommended combination** (built and verified as scratch/combo 7ac16e9 = a614451 → b166c03 → a428c32 → 37b9026 → regenerated artifacts_current.csv → fixture fix):
1. Merge a614451 first.
2. Rebase each fix branch with `--onto a614451`.
3. Merge b166c03 (G1), then a428c32 (G2) with the check_manifest.py resolution and the fixture update above, then 37b9026 (G5/G6) after its §4 fix.
4. Regenerate registry/artifacts_current.csv once at the end.

Combo result: 108 CI OK; red-team 76 tests, 9 expected GAPs, 0 unexpected successes; all repo checks PASS (except the pre-existing b2a95 SUMS).
The patches are in fix35/evidence/combo_patches/ and the resolution diff is in evidence/combo_check_manifest_resolution.diff.

## 6. New GAPs to add to REDTEAM.md
- G2b: a stub verifier (empty, exit-0, or printing FAILED) PASSes check_manifest. The verifier isn't pinned.
- G5b: a header-only claims.csv PASSes.
- G6b: a renamed status column skips status linting and PASSes, even with --strict. Full CI bypass confirmed.
- G6c: a duplicate status column shadows bad values.
- G6d: an earlier duplicate vocab section silently redefines the vocabulary.
