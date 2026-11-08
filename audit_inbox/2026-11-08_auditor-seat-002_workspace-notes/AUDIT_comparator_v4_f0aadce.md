# Audit: comparator v4 gates fix — `fix/comparator-v4-gates` @ `f0aadce` (parent `1250bbd`)

Auditor: Researcher 001 (independent review) · Date: 2026-10-31, ~12:50 EDT
Scope: commit `f0aadce` (10 files), base `gh/main` = `395ea53`. Read-only on GitHub: nothing pushed, no PR opened, no branch changed, no pinned file edited, no one contacted.
Method: fresh detached worktree at `f0aadce` (removed afterwards), CI tests, red-team suite, real-data comparator runs, `sha256sum -c`, all repo checkers, plus an independent 44-case negative-control harness (`cmpv4_f0aadce/rt/rt_r001_f0aadce.py`). Evidence is in `/workspace/audit_r001/cmpv4_f0aadce/evidence/`.

## Verdict: **FIXES REQUIRED** (small)

Every fix the author claims is present and works: the G-A, G-B, G-C/E and stub gates, the v3.log restore, the ERRATUM/E14 text, and the CI and pin results. Three problems remain:

1. **(Medium) The comparator accepts a changed uint64 `seed` in the CSV.** It compares integer CSV columns as float64, so `seed+1` (and any change up to about ±1000) gives **REPRODUCED**.
2. **(Medium) The red-team "tolerance" tests do not test the tolerance, and their result depends on the pandas version.** Under `requirements.txt`'s pinned pandas 3.1.0, **2 of them fail**.
3. **(Low) The G-D claim of "no traceback" is overstated.** Seven malformed-but-parseable or corrupt inputs still crash. They do fail closed (rc 1), but with no verdict.

Finding 2 predates this branch, and finding 1 is in the CSV path the branch touched. Neither is a regression introduced by `f0aadce`. Both are false-accept or test-validity problems in the very gates this branch claims to harden, so they should be fixed before this is treated as final.

## Author claims

| Claim | Status | Evidence |
|---|---|---|
| G-B: `EXPECTED_ZIP_SHA256 = 281bf33b…8d17ad`, the full value matches REPRODUCTION.md:22 | **Verified** | v4.py:46 equals REPRODUCTION.md:22 equals the actual zip sha. The hash covers the zip **bytes themselves** (v4.py:97 `ZIP.read_bytes()`, then parsed from the same bytes, so no TOCTOU). Appending one byte after EOCD (N09) and swapping an inner file (N08) are both rejected. |
| G-B: an exact copy (seed / CSV / branch-diag) is SUSPICIOUS | **Verified, with a caveat** | Relabelled official seeds (N01), a full exact copy (N04–N06 edge cases) and an inner CSV swap (N08) all give SUSPICIOUS or NOT REPRODUCED in both REAL and pin-bypassed (NOPIN) mode. Caveat: the heuristic can be beaten by changing 1 ulp in every seed (N03 NOPIN gives REPRODUCED). So the zip pin is the real control and SUSPICIOUS is defence in depth (finding 4). |
| Real data: seeds differ in 20–47 fields each, max about 6.66e-16 | **Verified** | 15,160 fields compared, 1,255 non-zero; 0 byte-identical seeds; 0 seeds with no differing field. Worst diffs: seed 6.661e-16, CSV 6.661e-16, branch-diag 5.551e-16. |
| Zip side: a missing / empty / unreadable manifest, CSV, branch-diag, seed or stub gives a named NOT REPRODUCED with no traceback; same for text in a numeric cell | **Partly verified** | Missing, empty, corrupt CSV (N31), corrupt branch-diag (N32), non-zip (N33) and text cells all behave as claimed. **Not true for:** a corrupt (bad-CRC) zip seed member (N30, v4.py:185); manifest JSON `null` or `[]` (N25/N26/N29, v4.py:144); `environment: null` (N27, v4.py:154); a non-dict stub (N28, v4.py:282); a missing repo-side source file (N35, v4.py:162). Each of these exits 1 with a traceback and no verdict. See finding 3. |
| G-A: key sets must match apart from the allowed-differ list; an extra null key fails | **Verified** | Red-team `test_manifest_null_key_added` passes. Note: keys on the allowed list may be absent on one side (N23, by design), and a key removed on **both** sides is not checked (N22). |
| G-C/E: `config_hash` is required in every seed; model / protocol / randomization / schema are required in both manifests | **Verified** | v4.py:143–147 and 193–194; red-team `test_seed_config_hash_removed_on_both_sides` and `test_manifest_model_removed_on_both_sides` pass. |
| Stub: content stays ungated (reason in ERRATUM, REPRODUCTION.md:50) but must be present | **Verified** | ERRATUM:113–119; REPRODUCTION.md:50 documents the wrong stub parameters; `test_zip_stub_manifest_missing` passes. |
| v3.log original restored (sha `fcf370da…`, byte-identical to main's SHA256SUMS line) | **Verified** | sha matches main's SHA256SUMS line; `cmp` against the earlier saved original shows them identical. |
| ART-0043 mis-attribution noted in E14 without touching artifacts.csv | **Verified** | ERRATA_2026-10-28.md:266–281. Independently confirmed: root file = `a94acae3…` (39,109 B); `Older files/` copy = `34d37908479f…` (39,239 B, ART-0217); official manifest `source_sha256` = `34d37908479f…`; rerun manifest = `a94acae3…`; the authority lock does not reference the script. artifacts.csv is unchanged. Wording nit: "at import (`add81e6`)": the root source came in `add81e6`, but `runs/5a9f093a2fe0/manifest.json` came in `c4434cb` (same day). |
| The ART-2869 note, CURRENT_STATUS.md:43, PATH_AND_LOCK…:18 and GITHUB_TREE…:48 repeat the wrong claim; prefix `34d37908764a` matches no file | **Verified** | No tracked file or zip member has prefix `34d37908764a` (only `34d37908479f` exists). Also, the "zip copy `4b792e88…`" cited at PATH_AND_LOCK…:18 / GITHUB_TREE…:48 matches no tracked file. |
| CI 103 OK | **Verified** | `evidence/tests_run.log` |
| Red-team: 100 tests, 11 expected failures, 0 unexpected successes | **Verified on the box's pandas 3.0.6** | 89 ok + 11 xfail, 0 skips, 0 unexpected successes; `git status` clean afterwards. **Under pandas 3.1.0 (the requirements.txt pin) 2 tests fail** (finding 2). |
| 16 new tests, 15 of which fail on `1250bbd` | **Verified** | All 16 new tests were run against the `1250bbd` comparator in a separate tree: 15 FAIL, and `test_zip_seed_member_empty` passes (`evidence/new_tests_on_1250bbd.log`). |
| Real data REPRODUCED, exit 0 | **Verified** | Two runs are deterministic; the output equals the committed v4.log body. Versus 1250bbd, only 3 new keys were added and no common key changed. |
| `sha256sum -c` 10/10 | **Verified** | Also lean_recovery 17/17, tools/sync 8/8, AIEFProofs 8/8, AIEFProofsKn 9/9. |
| All checkers rc 0 | **Verified** | validate_registry, hygiene (`--base gh/main --pii`; origin/main was stale locally), check_artifact_pins, check_current_inventory, verify_inventory_current, check_manifest, lint_claims, check_modes --strict: all rc 0 (`evidence/repo_checks.log`). |
| No pinned files touched | **Verified** | `git diff --name-only gh/main f0aadce` touches no artifacts.csv, .gitignore (ART-0001), check_lean.sh, verify_manifest.py, audit_manifest.json, or other SUMS or pin file. Only the local b2a95 SHA256SUMS changed, by design; artifacts_current.csv only updates the changed rows. |

## New findings (ranked)

### 1. MEDIUM: integer CSV columns are compared as float64, so a changed `seed` is accepted
- `compare_b2a95dfbfbe3_v4.py:236` `xs.append(x.to_numpy(dtype=float))`, then `diffs()` (v4.py:65–72) with TOL/RTOL.
- The CSV `seed` column is uint64 (around 1.1e19–1.8e19; 1 ulp in float64 = 2048). Casting to float64 erases any change smaller than about ±1024.
- Repro (harness):

  | Case | Change | Result |
  |---|---|---|
  | N39 | official CSV row 1 `seed` +1 | **rc 0 REPRODUCED** on pandas 3.0.6 and 3.1.0 |
  | N40 | `seed` +1000 in every row | rejected only because one row rounded across a float step (2048) |
  | N43 | `seed_index` +1 (int64, small) | rejected |
  | N42 | the npz `seed` field +1 | rejected; `cmp_arrays` compares int dtypes exactly (v4.py:81) |

- Mitigation already in place: the official CSV is pinned (artifacts.csv ART-1278 and the authority lock), and the zip side is sha-pinned. The gap is in the comparator's own logic, which the gate claims rely on.
- Fix: compare integer-typed columns (`kind in "iu"` on both sides, or integer-looking text) exactly as integers or strings. Apply TOL/RTOL only to float columns. Optionally, also check that the CSV `seed` values equal the npz `seed` fields.

### 2. MEDIUM: the red-team "tolerance" tests perturb the uint64 seed column and pass only because of a parser quirk
- `tools/redteam/test_rt_comparator.py:143–155` (`test_csv_cell_off_by_1e_9`, `test_csv_cell_off_by_just_over_tolerance`) use `first_finite_numeric_cell` (lines 90–101). It skips `seed_index`=0 and so picks `seed` (about 1.12e19). Then `v + 1e-9 == v` and `v + 1e-11 == v` in float64, so **neither test changes any value**.
- Rewriting the cell as a float string makes pandas read the column as float64. On pandas 3.0.6 the other 20-digit integers in that column parse about 1 ulp off, which gives a spurious "worst abs diff 4096 > TOL" and the tests pass by accident (harness N41).
- On pandas 3.1.0 (the pin in requirements.txt:14) the parse is exact, the comparator says REPRODUCED, and **both tests FAIL** ("checker ACCEPTED a known-false input"). See `evidence/tolerance_tests_pandas.log`.
- REDTEAM.md:123 and 180 report these as PASS, which holds only on pandas 3.0.6.
- Fix: pick a real float column (for example `D_B_final`, or the first column whose dtype is float with |v| about 1), assert that the written value differs from the original, and run the red-team suite under the pinned requirements in CI.

### 3. LOW: G-D "no traceback" is overstated; some malformed inputs still crash (fail-closed, rc 1, no verdict)
| Case | Input | Line | Exception |
|---|---|---|---|
| N30 | zip seed member with bad CRC | v4.py:185 (`zbytes = zread(f)` outside try) | BadZipFile |
| N25/N26 | zip manifest `null` / `[]` | v4.py:144 | AttributeError |
| N29 | official manifest `null` | v4.py:144 | AttributeError |
| N27 | zip manifest `environment: null` | v4.py:154 | AttributeError |
| N28 | stub manifest `[1]` | v4.py:282 | AttributeError |
| N35 | `Older files/…py` missing (repo side) | v4.py:162 | FileNotFoundError |

- A caller that checks only rc still rejects, so this is not a false accept.
- It does contradict ERRATUM:102–103 and ERRATUM:151–153 for a corrupt zip seed, and for an "unreadable" manifest if that word is read to include valid-JSON-wrong-type input.
- Fix: wrap v4.py:185; require `isinstance(m, dict)` for both manifests and the stub, and a dict `environment`; guard v4.py:162.

### 4. LOW / INFO: SUSPICIOUS can be bypassed; the zip pin is the only binding control
- In pin-bypassed (NOPIN) mode, these still give REPRODUCED:
  - official seeds relabelled plus 1 ulp on a non-zero cell of every seed (N03);
  - an allowed-differ key removed on one side (N23);
  - a non-required seed key removed on both sides (N22).
- These all need the pin itself to be changed. That pin (v4.py:46) lives in the same folder as its SHA256SUMS, which the same commit can update.
- Recommend that reviewers check that `EXPECTED_ZIP_SHA256` equals REPRODUCTION.md:22 on every change. Optionally, add a CI assert that reads REPRODUCTION.md:22.

### 5. INFO: wording in E14
- ERRATA_2026-10-28.md:275 says "at import (`add81e6`)". The official manifest was added in `c4434cb` (same day, 2026-10-18).

## Negative-control harness summary (44 cases: C00–C01, N01–N43 minus disabled N24; 76 runs across 3 passes, REAL and NOPIN modes)
- Controls: C00 genuine gives REPRODUCED. C01 (rebuilt zip) fails only on the sha in REAL mode and gives REPRODUCED in NOPIN.
- Rejected as expected:
  - relabelled or copied official data (N01, N02, N04–N06, N08);
  - zip byte changes (N09);
  - NaN/inf/-Infinity/1e999/blank cells on either side (N10–N16, N36);
  - CSV rows or columns reordered or rows swapped (N17–N19);
  - a non-required seed key missing on one side (N20/N21);
  - corrupt CSV or branch-diag member (N31/N32);
  - a non-zip file (N33);
  - an object-array npz (N34);
  - an extra seed member (N38).
- Accepted by design in NOPIN only: N07 (1 ulp, within tolerance), N22, N23, N37 (extra non-seed member).
- Not as claimed: N03 NOPIN (finding 4), N25–N30 and N35 tracebacks (finding 3), N39 seed+1 accepted (finding 1).
- Harness note: run 1 used a non-existent seed name and perturbed zero-valued cells, so N03/N07/N10/N11/N16 were invalid there. This was fixed and they were re-run (`rt_r001_run.log`, `rt_r001_run2.log`; `rt_r001_run_buggy_S0.log` is kept for transparency). N39–N43 were added at the parent's request.

## Recommendation on the ART-0043 erratum
Open a **separate erratum through the pin-change process**. Do not fold it into this branch.
- **Correct ART-0043** (artifacts.csv:44). Either:
  - (a) re-point the "official run implementation identity" to `Older files/AIEF_1_4_memory_ablation_updated.py` (`34d37908479f…`, today ART-0217, which should stop being labelled "Superseded … duplicate"); or
  - (b) re-label root `a94acae3…` as the *rerun* `b2a95dfbfbe3` source.

  Also remove the `verify_authority_lock()` claim, since the lock does not reference the script.
- Fix the ART-2869 note ("Worktree root sha256 (34d37908...)").
- Fix CURRENT_STATUS.md:43 (root is `a94acae3…`, not `34d37908…`).
- Fix PATH_AND_LOCK_DEPENDENCY_AUDIT.md:18 and GITHUB_TREE_AND_ZIP_RECONCILIATION.md:48: replace the non-existent prefixes `34d37908764a` and `4b792e88` with full hashes that resolve to real files.
- Update `check_artifact_pins` and artifacts_current via the normal pin-update path. Have a second reviewer confirm the official manifest's `source_sha256` equals the chosen file's sha.

## Housekeeping
- The worktree `/workspace/audit_r001/cmpv4_f0aadce/wt` was removed after the audit. `git status` was clean (0 entries) before removal.
- The temp tree `old1250` (used for the 1250bbd test run) was removed. The `/tmp/pd310` venv was used for the pandas 3.1.0 checks.
