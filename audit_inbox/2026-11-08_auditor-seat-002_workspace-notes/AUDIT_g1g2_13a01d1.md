# Re-audit: fix/check-manifest-g1g2 @ 13a01d1 (B1 fix), Auditor Seat 002

Auditor: Grok Bot, for Researcher 001. Date: 2026-11-07, about 10:00 Europe/Tirane (UTC+1). The re-audit was read-only. I worked in a throwaway clone (`/workspace/audit_r001/g1g2_92c5d77`, checked out at 13a01d1) and in scratch worktrees at 92c5d77 and 13a01d1, which I removed afterwards. Scratch commits were never pushed. I contacted no one and opened no PR. When I finished, origin still had `fix/check-manifest-g1g2` = 13a01d1 and `main` = ad58a46. Previous report: `AUDIT_g1g2_92c5d77.md`.

## Verdict: **CLEAN WITH NOTES**

**B1 is closed for committed files.** The wrapper now re-executes itself as `python -I -B` before any import that a sibling file could shadow. I planted 25 stdlib-named modules in `tools/ci/` (including sitecustomize, usercustomize, site and an encodings package) plus two in the repo root:
- **Every plant FAILs** with `SIZE AIEFS_audit.md` in both modes, on py3.12 and py3.13.
- On unfixed 92c5d77, 10 of them forge PASS.

I found no tracked-file-only bypass. Other results:
- The 3 new CI tests catch the regression. Disabling, removing or moving the re-exec gives 11 failures each, and the clean-tree control still passes.
- All counts reproduce.
- The G1/G2/G2b code is unchanged (additions only).
- No pinned file changed.

The author may open the PR.

Remaining items are notes:
- **N1 (refined).** A sitecustomize on PYTHONPATH, or a usercustomize via PYTHONUSERBASE, still forges PASS. Both run at interpreter start-up, before any script code. Both need control of the CI environment.
- G2c is still an owner item.
- N3–N6 are unchanged.

## Claims table

| # | Claim | Result | Evidence |
|---|---|---|---|
| 1 | Fast-forward 92c5d77..13a01d1; main ad58a46 is still an ancestor | **TRUE / CONSISTENT.** 13a01d1's only parent is 92c5d77. 92c5d77 and ad58a46 are both ancestors. No force is inferred from ancestry, since I cannot see the remote reflog. | git log/merge-base |
| 2 | check_manifest.py: re-exec right after the docstring, plus one docstring paragraph; every guard unchanged | **TRUE.** The diff is +10/−0. Removing the added paragraph and the 4-line block gives the 92c5d77 file again, apart from one blank line. The re-exec runs before `import argparse`. | diff in this audit |
| 3 | 3 new CI tests run a copy of the real wrapper as a script from a temp repo's `tools/ci/` | **TRUE.** `run_wrapper_script` copies `check_manifest.__file__` to `<tmp>/tools/ci/` and runs it with `cwd=<tmp>`, PYTHON* scrubbed and a 120 s timeout. The negatives tamper REPORT.md and expect `SHA256   REPORT.md`, `exited 1`, the FAIL result line, and no PASS line. They are ordinary tests, not xfail. | test diff |
| 4 | Disabling the re-exec gives 11 failures (10 subtests + PYTHONPATH); the control passes | **TRUE.** `if False:` → 11; block removed → 11; **re-exec moved below the stdlib imports → 11**. Each time the clean-tree control still passes and the full CI suite reports exactly 11 failures. A `-B`-only mutant (no `-I`) loops forever (the guard flag never flips). The tests' 120 s timeout would turn that into an error, so it fails closed. The fix was restored after each mutant, confirmed with `cmp`. | mutation_b1.log |
| 5 | REDTEAM.md: two B1 rows above GAP G2c, plus a fix note, not marked GAP; G2c unchanged | **TRUE.** The text is accurate. It does not mention the env-sitecustomize residual (see N1). | diff |
| 6 | test_rt_hashes.py: docstring only | **TRUE.** 3 lines in one docstring. | diff |
| 7 | artifacts_current.csv regenerated; 3406 rows; byte-identical to `--stdout` | **TRUE.** `cmp` is identical and there are 3406 data rows. Only the 4 changed tool files are re-hashed. | this audit |
| 8 | No pinned file changed; no planted module tracked | **TRUE.** Compared with main, only the 5 branch files differ. There is no diff under `AI Agent Audits/`, `registry/artifacts.csv`, `check_artifact_pins.py`, `.gitignore`, `.github/`. The only tracked non-checker files in `tools/ci` are `claim_statuses.txt` and `lean_presence.sh`. | this audit |
| 9 | CI 156 OK ×3; red-team 173 OK / 9 xfail; checkers pass | **TRUE.** See "What was run". | ci_matrix.log, redteam_py313.log, checks_13a01d1.log |
| 10 | Unfixed 92c5d77 forges; 13a01d1 refuses tools/ci hashlib, json, subprocess, argparse, re, os, stat, sitecustomize; PYTHONPATH hashlib fails; clean tree passes | **TRUE.** The table below covers more than the author's list. | b1_replay.log |
| 11 | A sitecustomize on PYTHONPATH still forges (env control, N1 class) | **TRUE.** A usercustomize via PYTHONUSERBASE forges too, for the same start-up reason. | b1_replay.log |

## B1 replay (`g1g2_adv/b1_replay.py`)

Every case tampers `AIEFS_audit.md`. A plant forges the PASS result line and exits 0 the moment it is imported, so any load of the plant into the wrapper process shows up as FORGED-PASS. Each case runs in both modes and was repeated on py3.12 and py3.13 with identical results.

| Case | 92c5d77 (unfixed) | 13a01d1 |
|---|---|---|
| clean tree, no plant | PASS | PASS |
| tampered, no plant / wrapper run with `-I` | FAIL (SIZE) / FAIL (SIZE) | FAIL / FAIL |
| committed `tools/ci/{hashlib,json,subprocess,argparse,re}.py` | **FORGED PASS** | FAIL (SIZE) |
| committed `tools/ci/{warnings,types,functools,enum,contextlib}.py` | **FORGED PASS** | FAIL (SIZE) |
| committed `tools/ci/{os,stat,sitecustomize,usercustomize,site,codecs,io,abc,posixpath,genericpath,_collections_abc,tempfile,linecache,traceback}.py`, `tools/ci/encodings/__init__.py` | FAIL (preloaded or not imported) | FAIL (SIZE) |
| committed repo-root `hashlib.py` / `sitecustomize.py` | FAIL | FAIL |
| env PYTHONPATH `hashlib.py` | **FORGED PASS** | FAIL (SIZE) |
| env PYTHONPATH `sitecustomize.py` | **FORGED PASS** | **FORGED PASS** (N1) |
| env PYTHONUSERBASE `usercustomize.py` | **FORGED PASS** | **FORGED PASS** (N1) |
| env PYTHONSTARTUP | FAIL | FAIL |

End to end on 13a01d1, in a scratch commit: I committed a proxying `tools/ci/hashlib.py` (the B1 attack), tampered `AIEFS_audit.md` and regenerated the inventory.
- **check_manifest FAILs** in both modes, with `SIZE AIEFS_audit.md: 23098 != 23088`.
- All other checkers and CI 156 OK still pass, which is expected because they don't check the manifest.

Evidence: `attackC_on_13a01d1_checks.log`. On 92c5d77 the same attack passed all of CI (previous report).

## Findings

- **No blockers.**
- **N1 (refined), NOTE: environment start-up hooks.** Python imports `sitecustomize` (from PYTHONPATH) and `usercustomize` (from the user site via PYTHONUSERBASE) during interpreter start-up, before line 1 of the script. So no in-script re-exec can stop them.
  - Both need control of the CI environment, which means a workflow or env edit. Someone with that access can also just remove the check.
  - A committed `tools/ci/sitecustomize.py` or `usercustomize.py` is **not** loaded, because the script folder is not on sys.path during start-up processing. I verified this.
  - My previous report said the B1 fix closes the env hijacks "as a side effect". That holds for module shadowing via PYTHONPATH, not for these start-up hooks. I correct it here.
  - Optional: add one sentence to the REDTEAM B1 note or the docstring saying start-up hooks via environment variables are out of scope. Only `python -I` in the workflow would close them, and a workflow editor can undo that. This is not a prerequisite.
- **N2: G2c**, owner item, unchanged: pin audit_manifest.json and verify_manifest.py outside the manifest, and make red-team a required check.
- **N3–N6** are unchanged from the previous report: the narrow problem regex, the folder-mode traceback, coverage keys outside `base`, and the hand-run `__pycache__` refusal.
- **INFO:** if a future edit drops `-I` from the re-exec, the wrapper loops forever instead of failing fast. The CI tests' 120 s timeout and the job timeout make that fail closed. Optional hardening: pass a sentinel env var or check `sys.flags.isolated` after the re-exec to fail fast.

## What was run (13a01d1)

| Check | Result |
|---|---|
| CI self-tests | **156 OK** on py3.12 (CI version; no pandas installed, not needed); **156 OK** on py3.13.5 + pandas 3.0.6; **156 OK** in `venv_req_cmp` (py3.13.5 + pandas 3.1.0) |
| Red-team `discover -s tools/redteam` (py3.13.5) | **Ran 173, OK (expected failures=9)**, 0 unexpected successes, 0 skips, rc 0 |
| hygiene `--base origin/main` / `--pii` / full | PASS 0/0 · PASS 0/0 · PASS (0 errors, 3 warnings) |
| check_modes `--strict` | PASS (0 errors, 119 warnings) |
| lint_claims / `--strict` | PASS 0/0/0 · PASS 0/0/0 |
| check_manifest inputs / `--no-inputs` | PASS: "checked 145 published files and 24 inputs; 2 post-manifest logs listed but not hashed" + OK / "checked 145 published files; 2 post-manifest logs …" + OK |
| check_artifact_pins | PASS: 2898 rows, **2839 match / 7 known-changed / 52 known-missing** |
| check_current_inventory, verify_inventory_current, validate_registry_against_tree | all rc 0; generator `--stdout` byte-identical; **3406 rows** |
| B1 replay | 33 cases × 2 modes × 2 Pythons × 2 commits |
| B1 end-to-end attack on 13a01d1 | check_manifest FAIL (SIZE) |
| Mutation | 3 re-exec mutants + control (11/11/11 failures, control OK) + a `-B`-only loop check |

## Evidence

- Report: `/workspace/audit_r001/AUDIT_g1g2_13a01d1.md`
- Logs: `/workspace/audit_r001/b1_evidence/`, with `b1_replay.log`, `mutation_b1.log`, `attackC_on_13a01d1_checks.log`, `checks_13a01d1.log`, `ci_matrix.log` and `redteam_py313.log`.
- Harnesses: `/workspace/audit_r001/g1g2_adv/`, with `b1_replay.py` and `mutate_b1.py`. The earlier harnesses are there too.
- Clean clone: `/workspace/audit_r001/g1g2_92c5d77`, now at 13a01d1. Scratch worktrees were removed. Scratch commits were never pushed.
