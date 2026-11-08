# Audit: fix/check-manifest-g1g2 @ 92c5d77 (cd64939 G2b follow-up + bff8bb8 merge of main ad58a46 + 92c5d77 tests), Auditor Seat 002

Auditor: Grok Bot, for Researcher 001. Date: 2026-11-07, about 09:40 Europe/Tirane (UTC+1). The audit was read-only. I worked in a throwaway clone at `/workspace/audit_r001/g1g2_92c5d77` plus scratch worktrees that I later removed. Scratch commits were local only and never pushed. I contacted no one and opened no PR. At the end of the audit, origin still had `fix/check-manifest-g1g2` = 92c5d77 and `main` = ad58a46.

## Verdict: **FIXES REQUIRED** (one blocker; everything else checks out)

The three pieces do what they claim:
- **cd64939** closes my 14072c3 findings F1, F3, F4, F5 and F6.
- **bff8bb8** is a correct merge. Only the two files reported conflict, the resolution matches the stated policy line for line, and nothing from either side was lost.
- **92c5d77** adds four coverage tests. Each one kills its own mutant.
- `check_manifest.py` is byte-identical at cd64939, bff8bb8 and 92c5d77 (blob `9359bbec`).
- All counts reproduce: CI 153 OK, red-team 173 OK with 9 expected failures, pins 2839/7/52, inventory 3406 rows byte-identical.
- No pinned file was touched.

**B1, the blocker: an F1-class shadow-module bypass one level up, in the wrapper itself.** CI runs `python tools/ci/check_manifest.py` without `-I` (`.github/workflows/repo-checks.yml:97`), so `tools/ci/` is `sys.path[0]` for the wrapper. I reproduced it end to end:
- I committed a 10-line `tools/ci/hashlib.py`. When `argv[0]` is `check_manifest.py` and there is no `--repo`, it prints `== result: 1 verifier(s) run, 0 failed -> PASS` and exits 0. Otherwise it transparently re-exports the real hashlib.
- I tampered `AI Agent Audits/AIEFS_audit.md` and regenerated the inventory.
- With that, **every CI check passed**: check_manifest (both modes), hygiene ± `--pii`, check_modes `--strict`, lint_claims ± `--strict`, check_artifact_pins, check_current_inventory, verify_inventory_current, validate_registry, and CI self-tests 153 OK.
- The verifier, the manifest and check_manifest.py were all untouched. The same tree run as `python -I tools/ci/check_manifest.py` gives `SIZE AIEFS_audit.md: 23098 != 23088`, FAIL.
- The json, subprocess, argparse and re variants pass too. Only the red-team suite catches it (12 failures in `test_rt_hashes`), and red-team is not in CI.

This is the same mechanism and the same stealth profile as F1 (a new `.py` file, no change to any authenticated or security file). The only difference is where the file sits. It is not in this branch's repo docs: `test_rt_hashes.py:331-332` mentions only PYTHONPATH and calls wrapper hijack "outside this check's threat model". The author's out-of-repo write-up lists it as "low, no new capability".

It is pre-existing on main, so it is not a regression, and the branch is a strict improvement. But the brief makes an F1-class isolation hole a blocker, and the fix is small and inside the branch. **Fix (tested in scratch):**
- Add 4 lines at the very top of check_manifest.py, before the other imports:
  ```python
  import sys as _sys
  if __name__ == "__main__" and not _sys.flags.isolated:
      import os as _os
      _os.execv(_sys.executable, [_sys.executable, "-I", "-B", _os.path.abspath(__file__)] + _sys.argv[1:])
  ```
  `os` is already in `sys.modules` from interpreter start-up, so a `tools/ci/os.py` cannot intercept it.
- Results with the fix:
  - `tools/ci/{hashlib,json,subprocess,argparse,re,os,stat}.py` all FAIL correctly.
  - The PYTHONPATH hijack FAILs correctly.
  - The clean tree PASSes in both modes, and CI self-tests are 153 OK.
- Also add a CI or red-team test (for example, run the wrapper as a subprocess with a planted `tools/ci/hashlib.py` in a temp repo copy and expect FAIL), and a written reason in REDTEAM.md.
- An equivalent alternative is `python -I tools/ci/check_manifest.py` in the workflow. The self-re-exec is better because it also protects local runs and needs no workflow edit.

If the owner explicitly accepts B1 as a documented residual instead, it must at least be written into REDTEAM.md / the docstring next to G2c, and everything else in this audit would then be **CLEAN WITH NOTES**.

## Status of my 14072c3 findings

| # | 14072c3 finding | Status @ 92c5d77 | Evidence |
|---|---|---|---|
| F1 HIGH | verifier ran without `-I`; shadow hashlib/json/glob/pathlib beside it forged OK | **CLOSED** for the verifier. It runs as `python -I -B -c BOOTSTRAP` from the hashed bytes, and an unlisted `*.py` or `__pycache__` beside it is refused before it runs. Shadows that are unlisted (refused), listed and hashed (ignored, real verifier FAILs), in the repo root/cwd, or `.pyc`/package/`.so`/`.pyw`/subfolder/`.pth`/sitecustomize/usercustomize all FAIL. The unisolated control still forges OK, so the attack is real. **The same class is still open one level up (B1).** | adv_g2b_py312.log, adv_g2c_python3.1{2,3}.log, replay_extra.log, attackC_checks.log |
| F2 MED | docs claimed audit_manifest.json is pinned in artifacts.csv | **CLOSED as documentation; residual honest.** No false "pinned" claim remains (grep). artifacts.csv has 0 `AI Agent Audits/` rows. The docstring (`:41-49`), REDTEAM.md (row G2c at `:98`, correction note at `:337-345`) and the `@gap("G2c…")` xfail in test_rt_hashes.py say plainly that a re-pinned stub passes CI. Owner item, not a blocker. | grep output in this audit |
| F3 LOW | duplicate summaries / problem lines before OK accepted | **CLOSED.** The last two non-empty stdout lines must be `[success, "OK"]`, each exactly once, with no PROBLEM-regex line on stdout or stderr. Duplicate summary → FAIL; `FAILED`/`SHA256`/`MISSING`/`UNLISTED`/`INPUT` lines → FAIL. Residual (note N3): the regex is narrow; lowercase or variant wording passes. That only matters for a re-pinned stub, which is G2c anyway. | adv_g2b_py312.log, adv_g2c_*.log section 4 |
| F4 LOW | chmod-000 verifier → uncaught PermissionError | **CLOSED.** Named ERROR "cannot be read (PermissionError: …)", NOT run, rc 1, no traceback. Residual (note N4): an evidence folder with mode 311 (no read, has x) gives a `os.listdir` traceback with rc 1, which is fail-closed. Mode 000 gives a named manifest error. Git cannot carry folder modes. | adv_g2b_py312.log; manual chmod test |
| F5 INFO | islink checked the final component only | **CLOSED.** Every folder component between the repo root and the verifier is checked. A symlinked `evidence/` → ERROR. | adv_g2b_py312.log (`evidence_dir_symlink_to_inrepo_copy`) |
| F6 INFO | TOCTOU between hash and exec | **CLOSED.** The hashed bytes are piped on stdin and exec'd. Swapping the file for a forging stub right after hashing (in-process hook) still FAILs on the tampered tree. | replay_extra.log |

## Claims table (author claims, verified independently)

| # | Claim | Result | Evidence |
|---|---|---|---|
| 1 | Fast-forward cd64939..92c5d77, no force | **CONSISTENT.** cd64939 → bff8bb8 → 92c5d77 is a linear first-parent chain, and cd64939 is an ancestor of the tip. I cannot see the remote reflog, so "no force" is inferred from ancestry. | git log/merge-base |
| 2 | bff8bb8 parents are cd64939 and ad58a46; both are ancestors of the tip | **TRUE.** `bff8bb8 → cd64939 ad58a46`. ad58a46, cd64939 and 14072c3 are all ancestors of 92c5d77. | git log -1 --format=%P |
| 3 | Only REDTEAM.md and artifacts_current.csv conflicted | **TRUE.** My own `git merge --no-commit ad58a46` on cd64939 conflicts on exactly those 2 files. | re-merge |
| 4 | REDTEAM resolution: hunk 1 branch, hunk 2 main, hunk 3 both; main's "counts not hard-coded" heading and GAPs unchanged | **TRUE.** Rebuilding the file from the conflict markers with that policy gives bff8bb8's REDTEAM.md, apart from one added blank separator line. Main's hunk-1 side was only the stale "GAP verifier deleted" row (closed by G2). The hunk-2 branch side was the stale v3 comparator table. | REDTEAM_rebuilt_by_policy.md vs REDTEAM_bff8bb8.md |
| 5 | Nothing else from either side was lost | **TRUE.** `git diff ad58a46 92c5d77` touches only the 5 branch files. For every file the branch changed since merge-base 47a8b31, the tip equals cd64939 (check_manifest.py, test_rt_hashes.py), or is the resolved/regenerated file, or is cd64939 plus the 92c5d77 tests. | changed_files_vs_main.txt |
| 6 | Main did not touch check_manifest.py / test_check_manifest.py / test_rt_hashes.py; the implementation is byte-for-byte cd64939 | **TRUE.** `git diff 47a8b31 ad58a46` on those paths is empty. Blob identity: check_manifest.py `9359bbec` at cd64939 = bff8bb8 = 92c5d77; test_rt_hashes.py `44ef1b76` at all three; test_check_manifest.py `886a7be5` at cd64939 = bff8bb8. | git rev-parse blobs |
| 7 | artifacts_current.csv regenerated; 3406 rows; byte-identical to the generator `--stdout` | **TRUE.** `cmp` is identical, 3407 lines / 3406 data rows. Compared with main, only the 4 changed tool files are re-hashed and test_check_manifest.py is added. | this audit |
| 8 | No pinned historical file edited | **TRUE.** Changed files ∩ artifacts.csv rows / SHA256SUMS = ∅. No diff under `AI Agent Audits/`, `registry/artifacts.csv`, `check_artifact_pins.py`, `.gitignore`, `.github/`. | changed_files_vs_main.txt |
| 9 | 4 new ordinary CI tests, each failing when its rule is disabled; before 92c5d77 nothing in CI caught these rules | **TRUE.** Mutants: M1 empty-manifest rule off → T1, T2 FAIL. M2 `own={key}` → T2 FAIL. M3 listed-file-exists off → T4 FAIL. M4 empty-inputs off → T3 FAIL. M5 coverage errors not counted, or M6 check_coverage not called → all 4 FAIL. The same 6 mutants against the bff8bb8 test file leave CI **green** (149 OK). None of the 4 is an xfail. Each uses a correctly pinned stub printing the exact success line, so only the coverage rule can fail it. | mutation_new_tests.log, mutation_old_tests_bff8bb8.log |
| 10 | Every G2/G2b guard is caught by the tests | **TRUE** for the 14 guards I mutated: dropping `-I`; running the file by path; no dup-key hook; no stray-.py check; no `__pycache__` check; no F5; no F4 try; no problem-line check; no count==1; no success-line check; no hash check; no outside-repo check; no self-symlink check; no missing-verifier check. **Each is caught by the CI self-tests**, and all but the self-symlink check by test_rt_hashes too. | mutation_g2b_guards.log |
| 11 | New CI and red-team controls fail against 14072c3, except the repo-root shadow | **TRUE.** With the tip tests on the 14072c3 wrapper: CI 23 failures + 1 error; test_rt_hashes 14 failures. | ci_tests_vs_14072c3_wrapper.log |
| 12 | CI 153 OK (py3.13/pd3.0.6, pd3.1.0, py3.12); red-team 173 OK, 9 xfail, 0 unexpected; all checkers pass | **TRUE.** See "What was run". | checks_92c5d77.log, ci_py312.log, redteam_py313.log |
| 13 | G2b fake-hashlib replay: unlisted refused; listed and hashed ignored, real verifier FAILs; repo-root fake FAILs; unisolated control forges OK | **TRUE.** Reproduced for hashlib/json/glob/pathlib (plus os/sys listed and hashed). | adv_g2b_py312.log, replay_extra.log, adv_g2c_*.log |
| 14 | Low note: the wrapper runs without `-I`, so PYTHONPATH can hijack it | **TRUE, but understated**: a *committed* `tools/ci/<stdlib>.py` hijacks it as well, with no environment control needed. That is B1. | attackC_checks.log, adv_g2c_*.log section 6 |
| 15 | Low note: unreadable evidence folder → traceback, non-zero exit | **TRUE** (mode 311). Fail-closed. | manual |

## Findings (ranked)

- **B1, BLOCKER (MEDIUM-HIGH): the wrapper itself is shadowable.** Details and the tested fix are under the Verdict above. It is pre-existing on main, but it is the same F1 mechanism. It passes all CI end to end with a tampered published file and no edit to any security file. It is not in the repo docs.
- **N1, NOTE: environment-based hijacks of the wrapper** (PYTHONPATH sitecustomize/hashlib, PYTHONUSERBASE usercustomize/.pth) pass. They need control of the CI environment (a workflow edit), so they are out of scope. The B1 fix closes them as a side effect.
- **N2, NOTE: G2c is an honest residual (owner item).** A re-pinned stub printing the computed success line passes CI. To close it, pin `audit_manifest.json` and `verify_manifest.py` outside the manifest, and make red-team a required check.
- **N3, NOTE: the PROBLEM regex is narrow.** It is case-sensitive and anchored to the verifier's exact wording, so lowercase or variant wording, zero-width/full-width prefixes, or stderr `error: …` pass. This only matters for a re-pinned stub (G2c class), because the genuine verifier's wording is fixed. It is fine as a smoke check. Don't describe it as more than that.
- **N4, NOTE: mode-311 evidence folder → `os.listdir` traceback, rc 1** (fail-closed). Optionally wrap the call in try/except OSError.
- **N5, NOTE: coverage `isfile(join(base, k))`** accepts absolute or `../` keys that resolve to existing files outside `AI Agent Audits/`. That needs a manifest edit, so it falls under G2c. Optionally require keys to resolve under `base`.
- **N6, INFO: running the verifier by hand with plain `python`** after a local import leaves `evidence/__pycache__`, and check_manifest then refuses (fail-closed, documented by the author).
- **N7, INFO:** the merge's REDTEAM.md has one extra blank line between the two fix-note blocks. Harmless.

No code that hands back the desired result was found. Every new CI test drives the real `check_manifest.main` against synthetic temp trees and asserts exact lines. The success line is computed from the manifest (a known and documented limit). The bootstrap runs the hashed bytes, not a substitute.

## What was run (all on 92c5d77 unless noted)

| Check | Result |
|---|---|
| CI self-tests `unittest discover -s tools/ci/tests` | **153 OK** on py3.12.x (CI version), **153 OK** on py3.13.5 + pandas 3.0.6, **153 OK** on `/workspace/venv_req_cmp` (py3.13.5 + pandas 3.1.0) |
| Red-team `unittest discover -s tools/redteam` (py3.13.5, pandas 3.0.6) | **Ran 173, OK (expected failures=9)**, 0 unexpected successes, rc 0, ~189 s |
| hygiene `--base origin/main` / `--pii` / full tree | PASS 0/0 · PASS 0/0 · PASS (0 errors, 3 warnings) |
| check_modes `--strict` | PASS (0 errors, 119 warnings) |
| lint_claims / `--strict` | PASS 0/0/0 · PASS 0/0/0 |
| check_manifest (inputs / `--no-inputs`) | PASS: "checked 145 published files and 24 inputs; 2 post-manifest logs listed but not hashed" + OK / "checked 145 published files; 2 post-manifest logs …" + OK |
| check_artifact_pins | PASS: 2898 rows, **2839 match / 7 known-changed / 52 known-missing** |
| check_current_inventory | PASS; generator `--stdout` byte-identical; **3406 data rows** |
| verify_inventory_current | ALL … GATES PASSED |
| validate_registry_against_tree | rc 0 (3048 tracked at HEAD, 340 not in artifacts.csv) |
| Re-merge of ad58a46 into cd64939 and REDTEAM policy rebuild | conflicts only in REDTEAM.md and artifacts_current.csv; resolution matches the policy |
| Adversarial harnesses | adv_g2b (28 cases × 2 modes), adv_g2c (47 cases, py3.12 and py3.13 identical), replay_extra (6 listed+hashed shadows + F6 swap), end-to-end attack C (B1) with all checkers, B1 fix test |
| Mutation | 7 coverage mutants × (tip tests, bff8bb8 tests); 15 G2b guard mutants × (CI, test_rt_hashes); tip tests vs the 14072c3 wrapper |

Analysis pytest suites (v4.1 held-event, tests_modular) were not run. No file they touch differs from main.

## Evidence

- Report: `/workspace/audit_r001/AUDIT_g1g2_92c5d77.md`
- Logs: `/workspace/audit_r001/g1g2_evidence/`. The main files are `checks_92c5d77.log`, `ci_py312.log`, `redteam_py313.log`, `adv_g2b_py312.log`, `adv_g2c_python3.12.log`, `adv_g2c_python3.13.log`, `replay_extra.log`, `attackC_checks.log`, `mutation_new_tests.log`, `mutation_old_tests_bff8bb8.log`, `mutation_g2b_guards.log`, `ci_tests_vs_14072c3_wrapper.log`, `changed_files_vs_main.txt`, `REDTEAM_rebuilt_by_policy.md` and `REDTEAM_bff8bb8.md`.
- Harnesses: `/workspace/audit_r001/g1g2_adv/`, with `adv_g2b.py`, `adv_g2c.py`, `replay_extra.py`, `mutate_cov.py` and `mutate_g2b.py`. The first two were adapted from the earlier g2b/g2c harnesses.
- Clean clone at the tip: `/workspace/audit_r001/g1g2_92c5d77`. The scratch and re-merge worktrees were removed. Scratch commits were never pushed.
