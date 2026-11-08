# Audit: fix/check-manifest-g1g2 @ 14072c3 (G2b, Auditor Seat 002), parent f8eb5e8

Auditor: Grok Bot, for Researcher 001. Date: 2026-10-31, about 12:55 EDT. This audit was read-only. All work happened in throwaway local worktrees, nothing was pushed, and no one was contacted.

## Verdict: **FIXES REQUIRED**

The pre-run checks work as claimed. The wrapper refuses symlinks, directories and FIFOs, anything outside the repo, a hash mismatch, a missing entry, and an unreadable manifest, and it says plainly that the verifier was NOT run. The CI and red-team counts all reproduce. Two problems stop this from being clean:

1. **Shadow-module bypass (F1, HIGH).** The wrapper authenticates the bytes of `verify_manifest.py`, but not the code Python actually executes. If someone adds an untracked-by-manifest `AI Agent Audits/evidence/hashlib.py` (or `json.py`, `glob.py`, `pathlib.py`), it shadows the stdlib, because the script directory is `sys.path[0]`. That module can print the computed summary line plus `OK` and exit 0. The genuine, hash-matching verifier never gets to check anything, and published files can be tampered with freely. **Every CI check passes** in this case (end-to-end evidence below), and **no re-pin or pinned-file edit is needed**. The one-line fix `[sys.executable, "-I", rel]` closes it. I tested it: the real tree still passes, all 4 shadow variants fail, and test_check_manifest still reports OK.
2. **The trust chain the docs claim does not exist (F2, MEDIUM).** `check_manifest.py:26-27`, `tools/redteam/REDTEAM.md:196` and `tools/redteam/test_rt_hashes.py:250` all say `audit_manifest.json` is "itself pinned in registry/artifacts.csv". It is not. `registry/artifacts.csv` has 0 rows for anything under `AI Agent Audits/`. That means the re-pinned-stub residual is cheaper than documented. It needs no artifacts.csv or EXPECTED_* edit, and in CI it is caught by nothing.

## Claims table

| # | Claim | Result | Evidence |
|---|---|---|---|
| 1 | Refuses symlinks (including one to the real verifier), files outside the repo, and directories; requires a regular file | **TRUE** (final component only; see F5). FIFO refused too. A hardlink to an outside file is accepted, by design: realpath is inside the repo and git can't carry hardlinks. | adv_g2b.log |
| 2 | The sha256 must match `files_sha256['evidence/verify_manifest.py']`; a missing entry or unreadable manifest is an error; output says NOT run | **TRUE**. Also refused: an uppercase hex value and a non-object entry. **Exception:** an unreadable verifier (chmod 000) raises an uncaught `PermissionError` traceback at `check_manifest.py:84`. It still fails closed (rc 1) but without the NOT-run message (F4). | adv_g2b.log |
| 3 | After exit 0 the output must contain the exact summary line computed from the manifest, and the last non-empty line must be `OK` | **TRUE as implemented, but weak.** The line is derived purely from manifest counts (`success_line`, `check_manifest.py:91-96`), so any stub can compute it (or hardcode it). See F3. | adv_g2b.log |
| 4 | CI tests went from 5 to 19 exact-line tests; 16 fail on f8eb5e8 | **TRUE**: 16/19 fail on the old wrapper. The 3 that pass on old: bad_repo usage error, failing verifier, missing verifier. | evidence/ci_cm_oldwrapper.log |
| 5 | All 7 red-team controls fail on f8eb5e8 | **TRUE** | evidence/rt_hashes_oldwrapper.log |
| 6 | CI 122 OK; red-team 84 (73 pass / 11 xfail); all checkers rc 0 | **TRUE** on py3.12 and py3.13. Red-team: 84 = 73 ok + 11 xfail, 0 unexpected; git status clean afterwards (`__pycache__` removed). | evidence/ci_py312.log, ci_py313.log, redteam.log, checks_14072c3.log, validate_registry.log |
| 7 | No pinned files touched; verifier unchanged | **TRUE**. Changed: `registry/artifacts_current.csv` (4 rows re-hashed for the changed tool files), `tools/ci/check_manifest.py`, `tools/ci/tests/test_check_manifest.py`, `tools/redteam/REDTEAM.md`, `tools/redteam/test_rt_hashes.py`. The intersection with artifacts.csv rows, SHA256SUMS, `artifacts.csv`, `check_artifact_pins.py` and `.gitignore` is empty. `AI Agent Audits/` is byte-identical to main. | evidence/changed_files.txt |

## Residual: re-pinned stub, tested end to end as a full attacker (Attack A)

I worked in a scratch worktree with a local commit that was never pushed. The steps:

- Replace `verify_manifest.py` with a 6-line stub that reads `audit_manifest.json` and prints the computed summary (`--inputs`-aware) and then `OK`.
- Re-pin its sha256 and bytes in `audit_manifest.json`.
- Append `TAMPERED` to the published `AI Agent Audits/AIEFS_audit.md`.
- Regenerate `registry/artifacts_current.csv`.
- **`registry/artifacts.csv` did not need updating**, because it pins nothing under `AI Agent Audits/`.

**Which check still fails: none in CI.** These all PASS:

- hygiene (± `--pii`)
- check_modes `--strict`
- lint_claims (± `--strict`)
- **check_manifest**
- check_artifact_pins
- check_current_inventory
- verify_inventory_current
- validate_registry_against_tree
- CI unittests (122 OK)

Only the red-team `test_rt_hashes` catches it (7 failures). Those tests compare against the real verifier's source text, and red-team is not part of CI. Evidence: `evidence/attackA_checks.log`, `evidence/attackA_rt_hashes.log`.

Suppose the attacker had to touch artifacts.csv (it would be needed only if the manifest really were pinned there). They would then also edit `EXPECTED_CSV_SHA256`/`EXPECTED_ROWS` in `check_artifact_pins.py`. That is 2 constants: still trivial, just more visible in the diff.

**How hard is it to forge?** Trivial: about 6 lines. **Is the summary line derivable purely from the manifest?** Yes. It is `len(files_sha256)`, `len(inputs_sha256)` when in inputs mode, and `len(set(post_manifest_logs))`. It does not depend on any file actually being hashed. Against a re-pinned stub, the exact-line check adds nothing. It only stops a lazy stub (empty, comment-only, `sys.exit(0)`), which is what the 7 new controls cover.

## Shadow-module bypass, end to end (Attack B, F1)

I worked in a scratch worktree with a local commit that was never pushed. The steps:

- Add `AI Agent Audits/evidence/hashlib.py`, which prints the computed summary and `OK`, then calls `sys.exit(0)`.
- Tamper `AIEFS_audit.md`.
- `git add` the changes, regenerate the inventory, and commit.
- The verifier and the manifest are **untouched**.

Result: **all CI checks pass**, including check_manifest, because the genuine verifier's hash matches. Running the same tree with `python3 -I verify_manifest.py --inputs` gives `SIZE AIEFS_audit.md: 23097 != 23088`, `UNLISTED evidence/hashlib.py`, `FAILED: 2 problem(s)`. CI uses Python 3.12 (`.github/workflows/repo-checks.yml:35,49,66`), so `-I` (which implies `-P`) is available. Evidence: `evidence/attackB_checks.log`, `evidence/adv_g2b.log` (shadow_* cases), `evidence/adv_g2b_with_dash_I.log` (fix applied).

This is strictly worse than the re-pin residual. The diff contains no change to the verifier or the manifest, only a new `.py` file in an evidence directory.

## Own negative controls (scratch worktree, `adv/adv_g2b.py`; full table in `evidence/adv_g2b.log`)

"Re-pinned" means the stub hash was written into the manifest, so these probe the output check only.

| Control | Result | Comment |
|---|---|---|
| Hardlink to an outside file with genuine bytes | PASS | Acceptable: the content is genuine. Git can't carry hardlinks, so CI can't reach this. |
| Hardlink, then the outside file edited | FAIL (hash) | Correct |
| TOCTOU (conceptual) | — | The hash is read at `check_manifest.py:84-85` and the file is exec'd by path at `:152-155`; a concurrent writer could swap it in between. No attacker code runs before check_manifest in the CI job, so this is low risk. The proper fix is to read the bytes once and run them via `-I -c`/stdin, or from a private temp copy. F6. |
| `OK ` / `OK\t` (trailing whitespace) | FAIL | Strict; fine |
| `OK\r\n` (CRLF) | PASS | Intended (`rstrip("\r")`, `:165`) |
| `OK` followed by blank/whitespace lines | PASS | Fine |
| Summary line twice, then OK | PASS | Minor laxity (F3) |
| Summary, then `SHA256 …` / `FAILED: 1 problem(s)`, then `OK` | **PASS** | Problem lines in the output aren't rejected (F3) |
| Summary + OK on stderr only | FAIL | Correct (stdout only) |
| Crash after printing OK | FAIL (rc 1) | Correct (`:160`) |
| OK, then exit 3 | FAIL | Correct |
| Duplicate `files_sha256` key, genuine hash first and stub hash last | PASS | `json.load` keeps the last value, so a reviewer skimming the diff sees the genuine hash. It is a re-pin variant (F3/F2). |
| Duplicate key, bad hash last, genuine verifier | FAIL | Consistent last-wins |
| Verifier chmod 000 | FAIL via traceback | F4 |
| Verifier is a FIFO / directory | FAIL ("not a regular file") | Correct |
| Manifest is bad JSON / missing entry / entry is a string / sha is uppercase | FAIL with NOT-run message | Correct |
| `evidence/` is a symlink to an in-repo copy | FAIL | Fails closed |
| Shadow `hashlib.py` / `json.py` / `glob.py` / `pathlib.py` | **PASS** | **F1**. With `-I`, all FAIL and the control passes. |

## Findings (ranked)

- **F1 HIGH — shadow-module bypass of the authenticated verifier.** `tools/ci/check_manifest.py:152` runs `[sys.executable, rel]` without `-I`. The verifier's imports (`verify_manifest.py:5`) resolve to files in `AI Agent Audits/evidence/` before the stdlib. **Fix:**
  - Use `cmd = [sys.executable, "-I", rel] + …`. I verified it: the real tree still passes, the shadows fail, and test_check_manifest is OK.
  - Add a CI test (with a red-team mirror) that drops a `hashlib.py` next to the verifier and expects FAIL.
  - Optionally, refuse any `*.py` under the evidence directory other than the verifier itself.
- **F2 MEDIUM — the pin chain claimed in the docs does not exist.** `check_manifest.py:26-27`, `tools/redteam/REDTEAM.md:196` and `tools/redteam/test_rt_hashes.py:250` claim `audit_manifest.json` is pinned in `registry/artifacts.csv`. There are 0 such rows. **Fix:** either correct the text, or anchor the trust outside the attacker-editable manifest by putting `EXPECTED_VERIFIER_SHA256` and `EXPECTED_MANIFEST_SHA256` constants in `check_manifest.py` (or artifacts.csv rows plus the existing EXPECTED_CSV_SHA256). Either way, an in-repo pin only makes a re-pin *visible in the diff*. The real control is review (CODEOWNERS/branch protection on `AI Agent Audits/evidence/**` and `tools/ci/**`), or a base-diff check that fails when those paths change. Document that residual honestly.
- **F3 LOW — the output check is forgeable and lax.** `check_manifest.py:91-96,164-171`: the summary line is a pure function of the manifest, so it gives no assurance against a re-pinned stub. Separately, it accepts duplicate summaries and problem/`FAILED` lines before the final `OK`. **Fix:** require the non-empty stdout lines to be exactly `[want, "OK"]`. Stop describing the line check as protection against re-pinned stubs. It is a smoke test against lazy stubs only.
- **F4 LOW — unreadable verifier gives a traceback.** `check_manifest.py:84-85` has no `try`, so a `PermissionError`/`OSError` escapes. It still exits 1, but without the "was NOT run" message. This doesn't contradict the claim for the cases that were tested. **Fix:** wrap the read in `try/except OSError` and add a test.
- **F5 INFO — `islink` checks the final component only** (`:76`). An intermediate directory symlink is accepted, provided realpath stays inside the repo (`:73-75`). That fails closed in practice. Noted for accuracy of the "refuses symlinks" wording.
- **F6 INFO — TOCTOU between hash and exec** (`:84-85` vs `:152-155`). Low risk in CI. To fix, execute the exact bytes that were hashed.

## What was run

- CI unittests on py3.12 and py3.13: 122 OK.
- `tools/ci/tests/test_check_manifest.py` against the old wrapper: 16/19 fail.
- Red-team: 84 (73 + 11 xfail), git status clean afterwards. `test_rt_hashes` against the old wrapper: all 7 G2b controls fail.
- All checkers rc 0: hygiene ± `--pii`, check_modes `--strict`, lint_claims ± `--strict`, check_manifest (both modes), check_artifact_pins, check_current_inventory, verify_inventory_current, `audits/engineering/validate_registry_against_tree.py`.
- Attacks A and B.
- 28 own cases, including the control, × 2 modes, plus a re-run with `-I`.
- Evidence directory: `/workspace/audit_r001/g2b/evidence/`. Harness: `/workspace/audit_r001/g2b/adv/adv_g2b.py`.
- Scratch worktrees were removed afterwards. Their local scratch commits were never pushed.
