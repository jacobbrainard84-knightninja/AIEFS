# Independent re-audit: ci/check-sha256sums @ c47ed8a

Auditor: Grok Bot, for Researcher 001. Date: 2026-11-08 16:11 Europe/Tirane (UTC+0100). The implementation handoff (`/workspace/review_r026/FIX_sha256sums_SB1_c47ed8a.md`) was treated as unverified and not relied on. No contact, PR, push, merge, rebase, commit, or branch edits. The detached audit worktree was not edited. Plants and mutations ran only in a separate disposable clone, which was deleted afterward.

## Verdict: **CLEAN WITH NOTES — S-B1 closed**

The checker now has the same pre-import self-reexec as main's `check_manifest.py`: lines 40–43 match main's lines 59–62 character for character, and the only earlier statement is `import sys as _sys`. A plain, unisolated `python tools/ci/check_sha256sums.py` run (the CI invocation, unchanged) therefore re-executes itself as `-I -B` before argparse, hashlib, re, or subprocess can be imported. Replaying the original S-B1 digest-proxy `tools/ci/hashlib.py` and a forging `tools/ci/argparse.py` against a really tampered `tools/sync/download_new.sh` now gives **MISMATCH, FAIL, rc 1** on Python 3.12.16 and 3.13.5, both with and without `-I -B`. The unmodified tree PASSes (7 lists, 61 verified) in all four modes. With the re-exec disabled in the disposable copy, the same plants false-PASS again (rc 0, 61 verified), so the plants work and the fix is what stops them. The new script-level tests fail under that mutation. Notes only; no new blocker.

## Scope and ancestry

- Tip `c47ed8ad408f7431e6dcf37f468073564f6a8e00`, sole parent `18e542c846bb683ad722c1ea15b809dd07c32feb` (the previously audited tip).
- After fetching, `origin/main` = `942f8526daee5ac547f2e422101fa95c61eeef41` (unchanged). `main...tip` = behind 0 / ahead 7. Final `ls-remote` confirms both refs. `gh pr list --head ci/check-sha256sums --state all` shows no PR.
- `18e542c..c47ed8a` changes exactly 4 files (+224/−8): `tools/ci/check_sha256sums.py` (+12, the re-exec plus a docstring paragraph; nothing else changed), new `tools/ci/tests/test_check_sha256sums.py` (183 lines), `tools/redteam/REDTEAM.md` (docs), and `registry/artifacts_current.csv` (the checker and REDTEAM hash/size rows changed, one row added for the new test).
- Versus main: 7 files, the previous 6 plus the new test. No SHA256SUMS, `*SHA256SUMS*.txt`, or lock-hash list differs from main or from the parent. The workflow and `tools/redteam/test_rt_sha256sums.py` are unchanged from the parent. `check_manifest.py` and `lean.yml` are byte-identical to main. `git diff --check origin/main...HEAD` exits 0.
- Audit worktree: `/workspace/audit_r001/sha256sums_c47ed8a` (detached, clean at the end).

## Findings

| ID | Status | Finding / evidence |
|---|---|---|
| S-B1 | **CLOSED** | The re-exec runs before any shadowable import and covers the unisolated CI launch. Plant replay: unisolated and isolated runs both FAIL rc 1 on 3.12 and 3.13. Mutation proves the plants work. `plant_controls.log`, `mut_disabled_plants.log`. |
| Tests | VERIFIED | The 7 new tests run a copy of the real checker as a script from a synthetic repo's `tools/ci/` and assert the exact MISMATCH and FAIL lines. Controls cover the clean tree (plain and `-I -B`), a harmless sibling file, and tampering with no plant. Plant tests cover the digest proxy, forging hashlib/argparse/re/subprocess, and a PYTHONPATH hashlib. A structural AST test checks what precedes the re-exec. |
| Mutation counts | NOTE (wording) | "Disabling fails 6" counts failures including subtests: 3 test methods fail, one with 4 subtests. "Deleting fails 7" adds the structural test (4 methods). I reproduced both numbers exactly, so this is a wording point only. |
| D1 | **CLOSED** | REDTEAM now labels 5/49 and 6/51 as historical and 7/61 as current. It says the v3 exception was retired and that `ALLOWED_MISSING` is empty, which matches the code (`ALLOWED_MISSING = {}`). No live missing-v3 claim remains. |
| N1 | RESIDUAL (unchanged bound) | Interpreter startup hooks (sitecustomize/usercustomize from the environment) run before any script code. This is the same documented bound as the manifest checker. Not replayed; not promoted. |
| G2c | EXISTING OWNER ITEM | Unchanged. |
| Inventory | VERIFIED | The regenerated inventory is byte-identical to the tracked CSV: **3410 data rows**. `check_current_inventory.py` PASSes. |

## Plant replay (disposable clone of c47ed8a; `PYTHON*` env stripped; cwd = repo root; `python tools/ci/check_sha256sums.py`)

| Case | 3.12.16 plain | 3.12.16 `-I -B` | 3.13.5 plain | 3.13.5 `-I -B` |
|---|---|---|---|---|
| Clean tree | PASS rc 0, 61 verified | PASS rc 0 | PASS rc 0 | PASS rc 0 |
| download_new.sh tampered, no plant | FAIL rc 1, MISMATCH | FAIL rc 1 | FAIL rc 1 | FAIL rc 1 |
| Tampered + `tools/ci/hashlib.py` digest proxy (original S-B1 plant) | **FAIL rc 1, MISMATCH** | FAIL rc 1 | **FAIL rc 1** | FAIL rc 1 |
| Tampered + `tools/ci/argparse.py` printing PASS + `os._exit(0)` | **FAIL rc 1, MISMATCH** (forged line never printed) | FAIL rc 1 | **FAIL rc 1** | FAIL rc 1 |
| Restored clean tree | PASS rc 0, 61 verified | PASS rc 0 | PASS rc 0 | PASS rc 0 |
| *Mutation: re-exec disabled*, hashlib proxy | **false PASS rc 0, 61 verified** | FAIL rc 1 | **false PASS rc 0** | FAIL rc 1 |
| *Mutation: re-exec disabled*, argparse forge | **forged PASS rc 0** | FAIL rc 1 | **forged PASS rc 0** | FAIL rc 1 |

## What ran / independent counts

- `python3 -m unittest discover -s tools/ci/tests` (3.13.5): **163 tests, OK** (156 + 7).
- `test_check_sha256sums.py` alone: **7/7 OK** on 3.13.5 and **7/7 OK** on 3.12.16.
- Mutation (disposable clone only, reverted): condition replaced by `if False and ...` → **FAILED (failures=6)**, all in the shadow and PYTHONPATH tests. Block deleted → **FAILED (failures=7)**, adding the structural test.
- `python3 tools/ci/check_sha256sums.py` and `python3 -I -B tools/ci/check_sha256sums.py` on the clean worktree: **PASS**, 7 lists / 61 verified / 0 errors, rc 0.
- `check_current_inventory.py`: PASS. Generator `--stdout` compared with `cmp`: identical, 3410 rows.
- 28 plant/control invocations in total (20 on the fix tip, 8 under mutation).

**Skipped:** the full red-team suite (190 tests), because `test_rt_sha256sums.py` and the workflow did not change from the parent and the REDTEAM.md change is docs only (the parent run is in the prior audit). Also skipped: the Lean or full GitHub Actions matrix, remote CI, N1 startup-hook replay, and any broader module-shadow sweep beyond the S-B1 plants (scoped per brief).

## Evidence

Directory: `/workspace/audit_r001/sha256sums_evidence_c47ed8a/`
- `stat_parent.log`, `stat_main.log`, `diff_18e542c_c47ed8a.txt`, `remote_final.log`, `final_status.log`
- `plant_controls.py`, `plant_controls.log` (authoritative fix-tip results), per-case logs `{A..E}_*_{py312,py313}[_isolated].log` (overwritten by the mutation run, see note)
- `mut_disabled_tests.log`, `mut_disabled_plants.log`, `mut_disabled_plant_results.json`, `mut_deleted_tests.log`
- `ci.log`, `new_tests.log`, `new_tests_py312.log`, `checker.log`, `isolated.log`, `inventory.log`, `regenerated.csv`

No external actions taken. The disposable clone `/workspace/audit_r001/sha256sums_probe_c47ed8a` was deleted after use. Its per-case logs from the mutation run overwrote the same-named fix-tip per-case logs, so `plant_controls.log` is the authoritative fix-tip record, and `mut_disabled_plants.log` / `mut_disabled_plant_results.json` hold the mutation results.
