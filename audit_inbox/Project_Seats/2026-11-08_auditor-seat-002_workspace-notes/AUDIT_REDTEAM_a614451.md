# Auditor Seat 002: audit of audit-inbox @ 93a2364 and research/redteam-negcontrols @ a614451

- **Date:** 2026-10-31 (America/Toronto, EDT).
- **Repo:** jacobbrainard84-knightninja/AIEFS. main = 395ea53.
- **Worktrees (detached):** /workspace/review_r026/wt_inbox (93a2364) and /workspace/review_r026/wt_redteam (a614451). wt_freeze and wt_salvage were not touched.
- **Remote:** read-only. Nothing was pushed, and no PRs or comments were made.
- **Evidence:** /workspace/review_r026/logs/redteam_run1.log, redteam_audit/{trace_run.py, trace.json, gap_repro.sh, gap_repro.log}.
- **Environment:** Python 3.13.5 for the main run, plus 3.12 for the exit-code check (CI uses 3.12). lake was available.

---------------------------------------------------------------------
## Task A: audit-inbox 93a2364 (diff vs 8afd582). Verdict: CLEAN WITH NOTES

**Scope.** `git diff --name-only 8afd582 93a2364` lists only 3 files, all under audit_inbox/briefing/: OPEN_QUESTIONS.md, README.md and STATE.md. Nothing outside audit_inbox/ changed.

| Check | Result |
|---|---|
| Red-team rule 10 | Present in README.md:31, "Standing priority: red-team the checks (owner)". The old rule 10 is renumbered to 11. |
| §0b ideas | Present in OPEN_QUESTIONS.md "### 0b. Red teaming (owner)". It lists tampered hashes, 0.40/0.50 vs 0.4543, a false proved row, NaN/±inf, a corrupted seed, a PASSED manifest with no data, sorry/extra axiom, a nonexistent artifact, and swapped expected/actual. |
| PR #2 attribution | STATE.md: "Researcher 001 reviewed it as CLEAN WITH NOTES (PR #2 comment, 2026-10-30 22:00 EDT). Auditor Seat 002 authored the PR." Live GitHub agrees: the comment "Researcher 001 audit of PR #2 @ c59eabc: CLEAN WITH NOTES" was created 2026-10-31T02:00:06Z (22:00 EDT Oct 30). PR #2 head is c59eabc, merged 2026-10-31 09:38 EDT as 395ea53. Every PR and comment is posted by the owner account, so GitHub cannot confirm which seat wrote what; the comment body's self-label is the only evidence. |
| Rule 3 branch deletion | README.md:24: "No force-push, rebase of pushed commits, or deleting other people's commits or branches without the owner's approval." OK. |
| 5 merged branches deleted | STATE.md:16 names all 5. Live check: the activity API shows branch_deletion for all 5 at 2026-10-31 10:53 EDT. Their tips (cbf2ae7, a64d90e, 249ea3f, c59eabc, 893e0b6) are all ancestors of origin/main. ls-remote confirms they are gone. The cited salvage doc exists. |
| Secrets/PII | grep is clean. The commit author is the noreply address. |

**Nits.** These do not block, but the next edit should fix them:
1. **The text never says the owner approved the deletion.** STATE.md:16 says "deleted ... after their content was confirmed to be in main". It does not mention the owner's approval or the deep search, which the brief asked to be noted. Suggested wording: "deleted with the owner's approval after a deep search for unique content (salvage doc)".
2. **Wrong section reference.** README rule 10 says "Ideas are in `OPEN_QUESTIONS.md` §0". The section is titled §0b.

---------------------------------------------------------------------
## Task B: research/redteam-negcontrols @ a614451. Verdict: SOUND WITH NOTES (no false GAPs and no false PASSes today; there are latent weaknesses, listed below)

### Run
`python3 -m unittest discover -s tools/redteam -v` ran 74 tests: 61 ok, 13 expected failures and 0 skipped. It took 67 s and exited 0. This matches the claim exactly.

### B1. Every GAP reproduces independently (gap_repro.sh, run against the real scripts)

| # | GAP | Source cite | Independent reproduction |
|---|---|---|---|
| G1 | PASSED manifest with no data | verify_manifest.py (36 lines) does not require any file or input to be listed | `OK`, rc 0 |
| G2 | verifier missing is skipped | check_manifest.py:40-42 does `NOTICE ... continue`, and exits 0 when 0 verifiers run | `PASS`, rc 0 |
| G3 | claims.csv missing | lint_claims.py:127-129 prints a notice and returns | rc 0 |
| G4 | vocab missing skips value checks | lint_claims.py:132-133 only warns (CI runs it non-strict) | rc 0 |
| G5 | row cites a nonexistent artifact | only artifact_status/audited_status are linted; supporting_artifacts is never resolved | rc 0 |
| G6 | false claim marked proved | no semantic cross-check against evidence | rc 0 |
| G7 | full scan: binary outside the allowed folders | hygiene_scan.py:271-277 raises a BINARY_OUTSIDE warning only | WARNING, rc 0 |
| G8 | token inside a binary in an allowed folder | binaries are never content-scanned | stored zip under runs/, rc 0 |
| G9 | token in a text file over 10 MiB | hygiene_scan.py:278-280 skips the file (max_scan_mb=10) | 11 MiB file gives rc 0; the small-file control gives rc 1 |
| G10 | CSV branch labels swapped | compare_b2a95dfbfbe3_v3.py:113 computes csv_nonnumeric_equal, which is missing from `ok` (lines 130-131) | csv_nonnumeric_equal=false, but REPRODUCED, rc 0 |
| G11 | manifest schema changed | v3.py:65 computes schema_equal, which is not in `ok` | schema_equal=false, but REPRODUCED, rc 0 |
| G12 | `@[simp] axiom` | check_lean.sh:158 only matches `^\s*(private\|protected)?\s*axiom` | marker scan rc 0 ("hits=0") |
| G13 | sorry hidden via `Lean.Elab.admitGoal` | no marker word appears in the source | marker scan rc 0 |

Step 7 (`#aief_axiom_audit`) catches both G12 and G13: it prints DISALLOWED [sorryAx] and [rt_ax], and check_lean.sh:215-219 turns that into `fail 7`.

**Extra GAP found next to G12:** `noncomputable axiom rt_ax2 : Nat` also passes the marker scan (rc 0). Step 7 should still catch it.

**Conclusion: no false GAPs.**

### B2. PASS genuineness: all 61 traced, not just 15 (trace.json records rc and the output tail for each)

**How the 61 PASSes break down:**

| Category | Count | What it covers |
|---|---|---|
| Controls | 9 | 8 × test_00 plus the comparator selftest |
| Real checker script, run the way CI or the auditors run it | 37 | ArtifactPins 4, AuditManifest 5, ManifestWrapper 1, ClaimsLint 6, Hygiene 7, Comparator 14 |
| Code extracted from a pinned script, run in a substitute harness | 13 | MarkerScan 4 and AxiomAudit 5 (heredocs pulled from check_lean.sh and run on a toy project); SwappedExpectedActual 4 (`cmp_arrays` exec'd via ast from v3.py) |
| Self-referential | 2 (+1 control) | SettleThreshold 0.40/0.50 tests the suite's own simulation. No repo checker is exercised, so these should not count as checker PASSes. |

Every real rejection fails for the right reason (correct ERROR/FAIL line, no Traceback), with these exceptions and latent risks:
- **Crash counted as PASS.** Comparator `seed_file_bytes_corrupted` and `seed_file_deleted` are rejected by a Python Traceback (np.load/FileNotFoundError). The test only checks rc≠0 and that REPRODUCED is absent. This fails closed and is documented, but a crash is not a verdict.
- **No needle.** The 6 ClaimsLint PASS tests (outside vocab, trailing space, wrong case, duplicate, empty id, `--strict` vocab missing) assert nothing about the output, so any nonzero exit, including a crash, would pass. Today the output shows real ERROR lines. Fix: add needles such as "not in the status vocabulary", "duplicate claim_id" and "empty claim_id".
- **Weak needles:** "FAIL" (wrapper), "SHA256" and "INPUT".
- **Pin tests and self-pins.** ArtifactPins uses `--no-git`. "Pin rewritten to match" and "row citing nonexistent artifact" are caught only through the REGISTRY_CHANGED self-pin of artifacts.csv, which is correct but indirect.
- **check_lean.sh wiring is untested.** The Lean tests never run the script itself, so its step-6/7 wiring and exit codes are untested. I checked the wiring by reading lines 140-166 and 215-234, and it looks right.

**Conclusion: no false PASSes in practice.**

### B3. Reporting and exit-code semantics
- **How a GAP is recorded.** A GAP is recorded only when the AssertionError contains "checker ACCEPTED a known-false input" (`rtcommon.gap`, which uses expectedFailure). Any other exception in a GAP test becomes a skip ("GAP fixture broken").
- **Exit 0 with all 13 GAPs present** is by design, because GAPs are documented findings.
- **A fixed checker gives an unexpected success, and the run exits 1.** Confirmed on Python 3.13 and 3.12 with a probe test, so a fix forces the GAP test to be converted. This is the right ratchet.
- **Weakness 1: skips are silent.** A broken GAP fixture, or a missing lake or zip, makes that test skip, and a run with only skips exits 0 (confirmed). A CI wrapper should fail when the skip count is above 0, or when tests other than the expected Lean ones are skipped.
- **Weakness 2: a crash in a GAP test can look like "fixed".** GAP tests mostly have no needles. If the checker crashes (rc≠0), that counts as an unexpected success and looks like a fix. When a GAP is converted, the new PASS test must assert a specific rejection needle.
- **Weakness 3: nothing locks the GAP set.** Someone could add @gap to a regressed test. Fix: put an expected-GAP list in REDTEAM.md and add a test that asserts the set of `test_GAP_*` names equals that list.
- **Not in CI.** The redteam suite is not part of CI.

### B4. Fixtures and cleanup
- Fixtures are built under tempfile dirs, using a symlink farm. `tamper` unlinks the symlink and writes a new file, so the repo files are never written to.
- After the run, `git status --porcelain --ignored` showed only `tools/redteam/__pycache__/`. /tmp had 0 aiefs_redteam leftovers.
- **Nit:** __pycache__ is created inside the tree. It is ignored, but REDTEAM.md itself notes that a stray `__pycache__/*.pyc` can trip `check_artifact_pins --no-git`. Set PYTHONDONTWRITEBYTECODE=1 in the suite runner.

### B5. Scope, inventory, pinned files and main CI (all on a614451)
- **Scope.** `git diff --name-only origin/main...a614451` lists registry/artifacts_current.csv plus 7 files under tools/redteam/. REDTEAM.md is at tools/redteam/REDTEAM.md, not the repo root. The branch is a single commit.
- **Inventory.** The 7 added artifacts_current.csv rows are exactly the 7 tools/redteam files. `python3 registry/reconciliation/build_current_inventory.py` wrote 3369 rows, and `git status --porcelain` was empty afterwards, so there is no diff.
- **Pinned files untouched:** audit_manifest.json, registry/artifacts.csv, lean_recovery/SHA256SUMS, AIEF_LEAN_SOURCE_SHA256SUMS.txt and tools/sync/SHA256SUMS (grep of the diff found 0 hits).
- **CI on the branch:**
  - `unittest discover -s tools/ci/tests`: 103 tests OK.
  - `hygiene_scan --base origin/main --pii`: 0 errors, 0 warnings, PASS.
  - Full hygiene scan: 0 errors, 3 warnings, PASS.
  - `check_modes --strict`: PASS.
  - lint_claims, check_manifest (1 verifier), check_artifact_pins, check_current_inventory and verify_inventory_current: all PASS.
- **Cleanup.** The CI tools created `__pycache__` directories, and I deleted them afterwards.

### B6. Severity ranking (High = a false science result could land on main with green checks)

| Rank | GAP(s) | Severity | Why |
|---|---|---|---|
| 1 | G10 comparator ignores csv_nonnumeric_equal | **High** | Relabelled branches (numbers attributed to the wrong branch) still report REPRODUCED. |
| 2 | G5 lint ignores supporting_artifacts; G6 false "proved" claim | **High** | A claim can cite evidence that doesn't exist, or claim a proof with no Lean backing. |
| 3 | G1 verify_manifest accepts an empty PASSED manifest | High/Med | Gives a PASSED stamp with nothing verified. |
| 4 | G2 check_manifest exits 0 when the verifier is missing | Med/High | Deleting or renaming the verifier silently switches the CI step off (there is only one verifier). |
| 5 | G3/G4 lint_claims missing claims.csv or vocab gives rc 0 | Medium | Deleting a file silently switches the lint off. |
| 6 | G11 comparator does not gate schema_equal | Medium | Arrays are compared directly anyway, so this is mostly metadata, but the schema drift goes unflagged. |
| 7 | G7/G8/G9 hygiene (full-scan warn-only, binaries not scanned, >10 MiB skipped) | Med (security) / Low (science) | |
| 8 | G12/G13 (+ noncomputable axiom) marker scan | Low | Step 7 catches them. The only risk is when step 6 runs without step 7. |

### Missed GAPs (not in the suite)
- **M1, High/Med: reproduction SHA256SUMS is broken and unchecked.** audits/reproductions/b2a95dfbfbe3/SHA256SUMS lists compare_b2a95dfbfbe3_v3.log, which does not exist, so `sha256sum -c` gives rc 1. CI is still green.
  - Nothing in .github or tools/ci verifies any SHA256SUMS file.
  - The audits/reproductions/b2a95dfbfbe3 directory has 0 rows in registry/artifacts.csv, so check_artifact_pins does not cover it either.
  - The other three SUMS files currently verify (rc 0), but nothing in CI checks them. AIEF_LEAN_SOURCE_SHA256SUMS is checked only by check_lean.sh step 2, which is local; lean.yml runs only lean_presence.
- **M2: the comparator does not run in CI.**
- **M3: other comparator fields are computed but not gated:** manifest_keys_differing (v3:66), source_diff_code_lines (v3:79), zip_stub_model_matches_official (v3:128) and the config_hash label (v3:89).
- **M4: comparator TOL=1e-12 is absolute only.** There is no relative check, so a large-magnitude value can never pass and a tiny-magnitude value can be wildly off and still pass. NaN at the same position is accepted by design; this should be documented.
- **M5: the marker scan misses `noncomputable axiom`** (reproduced above).
- **M6: no fail-closed tests for check_current_inventory or check_modes** when their input files are missing.
- **M7: nothing checks the data/external SOURCE.md provenance.**
- **M8: suite meta-issues** (from B3): skips are silent, no needles on the lint PASS tests, no locked GAP list, and the suite is not in CI.

### B7. Proposed fix split

Rules for every branch:
- One checker per branch, cut from main, in severity order.
- The writer and auditor seats alternate between Researcher 001 and Auditor Seat 002.
- Each branch converts its `test_GAP_*` test(s) into normal tests that assert a specific rejection needle, and updates REDTEAM.md and the expected-GAP list.
- Each branch must keep the 103 tools/ci tests and the full redteam suite green (0 unexpected successes, 0 skips), plus hygiene, check_modes --strict and the inventory regeneration.
- Pinned files are not edited; each fix ships as a new version or a wrapper.

| # | Branch | Fixes | Writer | Auditor |
|---|---|---|---|---|
| 1 | fix/comparator-v4-gates | New compare_b2a95dfbfbe3_v4.py (v3 stays as the audit-trail record). Adds csv_nonnumeric_equal and schema_equal to `ok`, and optionally gates manifest_keys_differing against an allowlist. Regenerates the local SHA256SUMS including a real v4.log. Flips G10 and G11, and fixes M1 for this directory. | Auditor Seat 002 | Researcher 001 |
| 2 | fix/lint-claims-artifacts | Resolves each supporting_artifacts path (it must exist in the tree or the registry). Rows with evidence_scope "Formal proof" or a "proved" status must cite lean/… theorem files. Flips G5 and G6. | Researcher 001 | Auditor Seat 002 |
| 3 | fix/check-manifest-missing-verifier | A missing verifier is an ERROR, and 0 verifiers run means FAIL. Flips G2. | Auditor Seat 002 | Researcher 001 |
| 4 | fix/manifest-nonempty | A non-empty-coverage check in check_manifest, or a new verify_manifest_v2: a PASSED manifest must list at least 1 data file and non-empty inputs. Flips G1. | Researcher 001 | Auditor Seat 002 |
| 5 | fix/lint-claims-fail-closed | Missing claims.csv or vocab is an error even when non-strict. Flips G3 and G4. Must also update any of the 103 CI tests that assume notice behaviour. | Auditor Seat 002 | Researcher 001 |
| 6 | ci/check-sha256sums | New tools/ci/check_sha256sums.py that verifies every pinned SHA256SUMS file (audits/**, lean SUMS, lean_recovery, tools/sync), wired into repo-checks.yml, plus a new redteam test. Covers M1. | Researcher 001 | Auditor Seat 002 |
| 7 | fix/hygiene-scan-hardening | Full-scan BINARY_OUTSIDE becomes an error; zip members are scanned (or the zip's text members are listed); text over 10 MiB is scanned in chunks or fails. Flips G7, G8 and G9. Could split into 7a/7b/7c if needed. | Auditor Seat 002 | Researcher 001 |
| 8 | fix/lean-marker-regex | The axiom regex allows attribute and modifier prefixes (`@[..]`, noncomputable, private, protected), and admitGoal/mkSorry/elab-sorry patterns are added. Flips G12, G13 and M5. Touches check_lean.sh, so the AIEF_LEAN pins and lock-hash rules apply; check whether check_lean.sh is itself pinned before editing. | Researcher 001 | Auditor Seat 002 |
| 9 | (optional) ci/redteam-in-ci | Runs the suite in CI and fails on any skip or unexpected success. Adds needles to the lint PASS tests, locks the GAP list, and sets PYTHONDONTWRITEBYTECODE. Because Researcher 001 wrote the suite, Auditor Seat 002 audits it. | Researcher 001 | Auditor Seat 002 |
