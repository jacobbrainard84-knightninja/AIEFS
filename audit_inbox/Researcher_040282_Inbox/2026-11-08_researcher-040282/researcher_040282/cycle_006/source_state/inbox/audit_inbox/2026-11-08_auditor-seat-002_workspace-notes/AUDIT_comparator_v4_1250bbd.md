# Audit: comparator v4 (`fix/comparator-v4-gates` @ 1250bbd, Auditor Seat 002)

Auditor: Grok Bot (seat r001) · Date: 2026-10-31 (America/Toronto, EDT)
Scope: `jacobbrainard84-knightninja/AIEFS`, branch `fix/comparator-v4-gates` @ `1250bbd` = main `395ea53` + `0ed36da` (cherry-pick of red-team suite `a614451`) + the fix.
Constraints kept: nothing pushed, no PRs opened or merged, main not touched, nobody contacted. All work is under `/workspace/audit_r001/`.

## Verdict: **CLEAN WITH NOTES**

The fix does what it claims. I found no loosened tolerance and no faked or hard-coded result. The genuine data still REPRODUCES deterministically. Every suite and repo check passes. Seat 002's own red-team cases G10 and G11 are now real, message-asserting tests.

My 41 adversarial cases turned up five new gaps (G-A to G-E). None changes the verdict on the genuine data, and none is a regression from v3. The most important one for the "built-in result" concern is **G-B**: v4 computes the rerun zip's sha256 but does not gate it, and no CI pin covers the zip. A substituted zip containing the official seeds relabelled to the rerun id passes as REPRODUCED with diff 0. I recommend a small v5 or follow-up, listed below. It is not needed to accept this branch.

One claim is overstated: "missing files give a verdict, not a crash." That holds for the official side and for seed files. Missing or garbled **zip-side** manifest, CSV or stub-manifest files, and text in a numeric CSV cell, still crash with a traceback (rc 1). Those crashes are fail-closed (the run never says REPRODUCED), so this is a note, not a fix requirement.

## Setup
- Worktree: `/workspace/audit_r001/comparator_v4/wt`, detached at `1250bbd`.
  - Files under 1 MB are real copies.
  - The 99 files of 1 MB or more are hardlinks into `/workspace/review_r026/wt_cmpv4`, because the disk was full.
  - `git read-tree HEAD && git update-index --refresh` gives a clean status, so every file is hash-verified against the commit. The status was still clean (0 entries) after all runs.
- Base for diff checks: `gh/main` = `395ea53`. The worktree's `origin/main` is stale.
- Evidence: `/workspace/audit_r001/comparator_v4/evidence/`
- My harness: `/workspace/audit_r001/comparator_v4/redteam_r001/rt_r001_v4.py`
  - Each case builds a temp workspace (symlinks plus copies) and, for zip-side cases, a rebuilt temp zip. It never writes to the repo.

## Claim-by-claim

| # | Claim | Result | Evidence |
|---|---|---|---|
| 1 | Cherry-pick is faithful | ✅ | `a614451` (fetched via `research/redteam-negcontrols`) and `0ed36da` have the same patch-id (`922a6a4f…`), an empty tree diff, and the same parent, `395ea53` |
| 2 | v4 added; v1–v3 untouched | ✅ | `git diff gh/main 1250bbd` touches 15 files and no v1/v2/v3 `.py`. Applying `v3_to_v4.diff` to v3 with `patch` gives v4 byte-for-byte |
| 3 | G10 (CSV text labels) and G11 (manifest schema) gated | ✅ | `csv_nonnumeric_columns=[branch, branch_family]` is compared cell-wise. `schema` is in the ok-conditions. Red-team G10 is `test_csv_branch_labels_swapped` and G11 is `test_manifest_schema_changed`; both are normal tests that assert the problem message |
| 4 | Only `config_hash` / `environment` / `source_sha256` may differ; `config_hash` must equal the run id | ✅ with gap G-A | My cases 04, 05, 07 and 10 reject. Case 06 (a key added with a `null` value) is accepted |
| 5 | `source_sha256` must match the source | ✅ | Case 10 (hash not updated) rejects. Both manifests' hashes match the tracked files: official = `Older files/…py` `34d37908…`, rerun = root `…py` `a94acae3…` |
| 6 | Source diff must be exactly the one-line rewrite | ✅ | Case 08 (an extra code line, hash updated) rejects with "3 code line(s)". Case 08b (a second existing line edited) rejects with "4 code lines". Case 09 (a comment-only line) is accepted by design: blank and comment lines are ignored and reported |
| 7 | Seed labels and names match 1:1 | ✅ with gap G-C | Cases 03, 11, 12, 13, 14, 15 and 16 reject. Case 35 (the `config_hash` field removed from every seed on both sides) is accepted |
| 8 | Missing files → verdict, not crash | ⚠️ partial (G-D) | Official-side files and seed files: verdict ✅ (cases 25 and 26, plus Seat 002's tests). Zip-side manifest, CSV or stub manifest missing or empty, and text in a numeric cell: traceback, rc 1 (cases 24, 27, 32, 33, 34) |
| 9 | RTOL 1e-12 on top of the absolute TOL | ✅ (tighter only) | Case 17 (0 → 1e-300, rel 1.0) rejects. Case 18 (0 → 5e-13) rejects. Case 20 (×(1+1e-11)) rejects. `TOL` is still 1e-12, `wa > TOL` is the exact complement of v3's `<= TOL`, and all of v3's ok-conditions are kept |
| 10 | `zip_stub_model` ungated; reason at REPRODUCTION.md:50 | ✅ (wording) | Line 50 documents that the stub has the wrong parameters and that the script reports `…matches_official: false`. "Ungated" itself is stated in the v4 docstring and in E14, not at line 50 |
| 11 | Real data REPRODUCES (problems [], max abs 6.66e-16) | ✅ | Two runs each of v3 and v4 gave identical output, rc 0, REPRODUCED. v4: seed worst abs 6.661e-16 (rel 8.47e-16); CSV abs 6.66e-16 (rel 1.154e-15); branch_diag abs 5.55e-16; 15,160 fields, 1,255 nonzero diffs, 0 byte-identical seeds |
| 12 | Red-team: 84 tests, 73 OK, 11 GAP | ✅ | 84 ran: 73 ok, 11 expected-failure, 0 skipped (the lake is present), about 96 s. `evidence/redteam_full.log` |
| 13 | 103 CI tests; all repo checks pass | ✅ | `tools/ci/tests`: 103 OK. All checks rc 0 (see below) |
| 14 | v3.log regenerated with unchanged v3 and force-added | ✅ with note | The committed v3 and v4 log bodies are byte-identical to my re-runs, apart from a hand-added header (command, commit, versions, date) and a trailing `exit 0`. The output has no timestamps, so it is deterministic |
| 15 | SHA256SUMS covers 10 files; `sha256sum -c` passes | ✅ | 10/10 OK on the branch. On main, the check fails because v3.log is missing (confirmed) |
| 16 | ERRATA E14 is used for v4 | ✅ | E14 was appended after E13 and accurately describes the gates, the RTOL, the ungated stub, the 6.66e-16 / 1.15e-15 results and the v3.log regeneration |

Repo checks, all rc 0 / PASS:
- `validate_registry_against_tree`
- `hygiene_scan --base gh/main --pii`: 15 files, 0 errors, 0 warnings
- full `hygiene_scan`: 3 BIG_FILE warnings
- `check_artifact_pins`: 2,898 rows, 2,839 match, 7 known-changed, 52 known-missing
- `check_current_inventory`
- `verify_inventory_current`: ALL GATES PASSED
- `check_manifest`: 145 files, 24 inputs
- `lint_claims`: 76 rows, 0 violations
- `check_modes --strict`: 119 warnings
- `sha256sum -c` in lean_recovery (17), b2a95 (10), tools/sync (8), AIEFProofs (8) and AIEFProofsKn (9)

Logs: `evidence/tests_run.log`, `evidence/repo_checks.log`.

## My red-team of v4 (41 cases; `evidence/rt_r001_run.log`, `rt_r001_results.json`, `rt_r001_extra.log`)

**Rejected correctly, with a meaningful message:**
- 01: `branch_family` swap
- 02: seed field swap
- 03: `config_hash` label swap
- 04 / 05: manifest key added / removed
- 07: nested model key changed
- 08 / 08b: two-line source changes
- 10: stale `source_sha256`
- 11: seed rename
- 12: rotated seed contents
- 13: swapped and relabelled seeds
- 14: duplicated seed (official)
- 15: duplicate zip member plus a dropped seed
- 16: 41 members
- 17 / 18: values near zero
- 20: relative perturbation of 1e-11
- 21: blank `branch` cell
- 22: all-blank `branch_family`
- 23: blank versus the literal `"nan"`
- 25: empty official CSV
- 26: header-only CSV
- 28: official manifest replaced by the stub's (right id, wrong run; caught on model/protocol/randomization/schema)
- 30: stub CSV and diagnostics substituted
- 40: whole CSV rows reordered

**Accepted, by design:**
- 09: comment-only source line
- 19: `-0.0`
- 29: official manifest equal to the rerun manifest with the id and hash fixed (this is an environment-only change)
- 36: environment changed
- 37: control
- 38: an extra unrelated file in the run directory (ignored, informational)

### New gaps (not in Seat 002's 11)

- **G-B (medium; "built-in result" risk).** Case 31: the zip's rerun seeds were replaced by the official seeds with `config_hash` relabelled to the rerun id. v4 returned REPRODUCED with diff 0 and rc 0.
  - v4 computes `zip_sha256` (genuine value `281bf33be105cb62…`, recorded in REPRODUCTION.md line 22) but never compares it to a constant.
  - The zip is **not** in the frozen `registry/artifacts.csv`. It appears only in the regenerated `registry/artifacts_current.csv:436`, so `check_artifact_pins` does not protect it, and a regenerated inventory would follow any replacement.
  - `seed_files_byte_identical` and `seed_fields_nonzero_diff` (1,255 of 15,160 on the genuine data) are also computed but not gated. An "every field exactly 0" rerun is a strong copy signal, and it is invisible to the gates.
  - Fix: add `EXPECTED_ZIP_SHA256 = "281bf33b…"` as a gate. Optionally, also flag `nonzero_diff == 0` across all seeds as suspicious.
- **G-A (low).** Case 06: a manifest key added with the value `null` is accepted, because the differing-keys check uses `.get()` on both sides instead of comparing key sets. The official manifest is pinned (ART-1279), so in-repo this needs a pin change as well. Fix: compare `set(mz) ^ set(mo)`.
- **G-C / G-E (low).** These are vacuous gates when a field is missing on both sides:
  - Case 35: `config_hash` removed from all seeds. The label gate runs only if the field is present.
  - Case 39: the `model` block removed from both manifests. `None == None` counts as equal.

  v3 would have crashed on the second. Fix: require the presence of `model`, `protocol`, `randomization`, `schema` and per-seed `config_hash`. Both cases need zip tampering, so G-B's fix also mitigates them.
- **G-D (fail-closed crashes; contradicts claim 8 for the zip side).** None of these gives a verdict:
  - Case 24: text `abc` in a numeric official CSV cell gives a `ValueError` at `to_numpy(dtype=float)` (line 176).
  - Case 27: empty zip CSV gives `EmptyDataError` (line 167).
  - Case 32: zip manifest missing gives `KeyError` (line 101).
  - Case 33: zip CSV missing.
  - Case 34: zip *stub* manifest missing (line 211). This is an informational-only key that aborts the whole comparison.

  All exit rc 1 with a traceback, so nothing false is reported, but there is no verdict. Fix: wrap these reads like the official-side reads are wrapped, and use `pd.to_numeric(errors="coerce")` together with a non-numeric-cell problem.

### Loosened tolerances / false results
- No tolerance was loosened. `TOL` is unchanged at 1e-12, `RTOL` only adds rejections, and every v3 ok-condition (model/protocol/randomization equality, counts == 40, `wa <= TOL`) is still there.
- I found no hard-coded verdict, special-casing of the genuine run ids that bypasses checks, or swallowed exceptions that turn into a pass. The only constants are the run ids, paths, the one-line expected diff, and the set of expected differing keys, and each of them makes the check stricter.

## Notes
1. **v3.log re-pin.** The original v3.log pinned by E13 (`fcf370da…`) still exists on this box at `/workspace/review_r026/wt/audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v3.log` (copy in `evidence/original_v3_fcf370da.log`).
   - Its JSON body is identical to the regenerated log.
   - It differs only in the header (commit `cbf2ae7`, pandas 3.1.0, 2026-10-29) and an extra `--selftest` section.
   - Restoring it would have kept E13's pin instead of re-pinning to `01c057c9…`. Re-pinning is acceptable and disclosed in E14.
2. **.gitignore.** Line 23 (`*.log`) ignores all three logs under `audits/` (`git check-ignore` confirms). The existing negation covers only `AI Agent Audits/**`, so future logs there will silently go uncommitted unless force-added. This is the same failure E14 fixes. Recommend adding `!audits/**/*.log`.
3. **Committed logs' headers** are hand-added (command, commit, versions, date). They are not program output, which is fine and accurate.
4. **Pre-existing, out of scope (on main):** in `registry/artifacts.csv`, ART-0043 describes root `AIEF_1_4_memory_ablation_updated.py` (`a94acae3…`) as authority-locked by `runs/5a9f093a2fe0/manifest.json` `source_sha256`. That manifest actually records `34d37908…`, the `Older files/` copy, which ART-2869's note also says. v4's mapping matches the data, so the ART-0043 note looks wrong.
5. `registry/claims.csv` (AUD-REPRO-B2A95) and `build_claims_reconciliation.py` still cite v3.log. E14 discloses this as an owner decision.
6. My worktree hardlinks Seat 002's big files. Content is git-verified, so this does not affect the results.

## Recommended follow-ups (priority order)
1. Gate `zip_sha256` against `281bf33b…` (G-B). Consider flagging the case where every seed field has zero difference.
2. Wrap the zip-side reads and coerce numeric CSV columns so they give a verdict, not a crash (G-D).
3. Compare manifest key sets, and require the presence of the gated keys and per-seed `config_hash` (G-A, G-C, G-E).
4. Add `!audits/**/*.log` to `.gitignore`.
5. Add my cases 06, 24, 27, 31–35 and 39 to `tools/redteam/test_rt_comparator.py` as GAP expected-failures.
