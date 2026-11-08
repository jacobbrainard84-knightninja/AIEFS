# Independent audit: ci/check-sha256sums @ 18e542c

Auditor: Grok Bot, for Researcher 001. Date: 2026-11-08 16:58 Europe/Tirane (UTC+0100). Implementation handoff was treated as unverified input. No contact, PR, push, merge, rebase, commit, or branch edits. The detached audit worktree was not edited; mutation controls ran only in a separate archival copy with its own disposable Git index.

## Verdict: **FIXES REQUIRED — S-B1 (blocker)**

The new job introduces the same stdlib-shadowing false-PASS class that main's manifest wrapper already fixed as B1. CI invokes `python tools/ci/check_sha256sums.py` without isolated mode. The checker immediately imports argparse/hashlib, with no pre-import self-reexec. On Python 3.12.16, a planted `tools/ci/hashlib.py` made a genuinely modified pinned `tools/sync/download_new.sh` report **61 verified, zero errors, PASS, exit 0**. Removing the plant, or launching with `-I -B`, reports the real mismatch and exits 1. This needs only checkout-file control, not PYTHONPATH, workflow editing, or CI-environment control; it is not the accepted startup-hook residual. **Do not mark this tip CLEAN or open a PR on this verdict.** The merge and removal of the stale v3 exception are otherwise consistent with main.

## Scope and ancestry

- Repository: https://github.com/jacobbrainard84-knightninja/AIEFS
- Original checker tip: `7c3bbba9ba93cc7fe067d9a0a6d2b7882c12ed50`.
- Merge: `52f2eac422469eb17d518609bfb278709ffd6445`; independently verified parents, in order: original tip and `942f8526daee5ac547f2e422101fa95c61eeef41`.
- Reviewed tip: `18e542c846bb683ad722c1ea15b809dd07c32feb`, sole parent the merge above.
- Fetched origin before checkout. `origin/main` and merge-base both `942f8526daee5ac547f2e422101fa95c61eeef41`. `git rev-list --left-right --count origin/main...HEAD` = `0 6` (behind 0, ahead 6). Final read-only `ls-remote` confirms main and branch still at these tips.
- Original-work range includes `bec5b698` (red-team kit), `6b9abe8` (initial checker), `7be49d0` (kit merge), and `7c3bbba` (round-two discovery and containment). Final checker/tests were read, and layer diffs saved separately.
- Audit worktree: `/workspace/audit_r001/sha256sums_18e542c`, detached. Throwaway control copy: `/workspace/audit_r001/sha256sums_probe_18e542c`.
- Verified final file list against main (6 files; 465 insertions / 3 deletions): `.github/workflows/repo-checks.yml`, `audits/reproductions/.gitignore`, `registry/artifacts_current.csv`, `tools/ci/check_sha256sums.py`, `tools/redteam/REDTEAM.md`, `tools/redteam/test_rt_sha256sums.py`.

## Findings

| ID | Status | Finding / evidence |
|---|---|---|
| S-B1 | **NEW BLOCKER** | Unisolated CI script imports sibling hashlib.py and false-PASSes a real pinned-file mismatch. `negative_controls.log`, `shadow_hashlib_py312.log`; isolated comparison correctly FAILs. |
| M1 / stale-v3 | **CLOSED** | Main really restores v3 at the pinned digest. Follow-up removes precisely the sole missing-file exception; no other exception was added or removed. Present/matching PASS; deleted v3 FAILs. |
| Merge | VERIFIED | Ancestry, 6-file final delta, preserved main wrapper/workflows, REDTEAM union, and generated inventory match independently. |
| Tests | NOTE | Existing 18 SHA256SUMS tests are unchanged through merge/follow-up and cover ordinary tampering/allow-list cases, but their module driver does not exercise the production CLI's import boundary. No planted-module regression test for this checker exists there. |
| D1 | NOTE | REDTEAM retains historical fix-note text saying “5 today, 49 entries,” then “6 files, 51 entries,” and a live missing-v3 exception, while the new refresh paragraph correctly says 7/61 and removed exception. Label those paragraphs historical or update them to avoid contradictory current-tense claims. |
| N1 | RESIDUAL, NOT REPLAYED | Environment startup hooks (sitecustomize on PYTHONPATH / usercustomize) are the sibling checker's documented accepted boundary; they execute before script-level isolation. This audit does not promote S-B1 into that category. |
| G2c | EXISTING OWNER ITEM | Main's external-manifest-pin / required-red-team owner note is retained verbatim, not closed by this branch. |

## Merge review

`git show --remerge-diff 52f2eac` independently reconstructs content conflicts only in `registry/artifacts_current.csv` and `tools/redteam/REDTEAM.md`; no repo-checks conflict. This verifies the merge result/conflict set, not the author's historical keystrokes.

- **Inventory:** ran `python3 registry/reconciliation/build_current_inventory.py --stdout` into an evidence file, then `cmp` against the tracked inventory: byte-identical, **3409 data rows**. This proves the final inventory equals fresh generation; it cannot prove the author never used a manual editor. Inventory checker independently PASSes.
- **REDTEAM:** diff against main consists only of SHA256SUMS section/notes additions. No main line is removed or softened, including G1/G2/G2b/B1/G2c. Diff against old tip replaces the obsolete “verifier deleted is an open GAP” row with main's fixed cases, preserves the SHA256SUMS table, and relocates its two fix-note paragraphs intact. D1 is documentation staleness, not a dropped security qualification.
- **Workflow:** deleting only the new `sha256sums` job and its header mention yields byte-for-byte main's repo-checks.yml. All other workflow files (including lean.yml) are byte-identical to main. Main's manifest wrapper is also byte-identical.
- **Job behavior:** setup-python requests Python 3.12; job runs `python tools/ci/check_sha256sums.py`, no `-I`. Ordinary mismatch correctly exits 1, but S-B1 bypasses it.
- **Checksum lists:** no SHA256SUMS / *SHA256SUMS*.txt / lock-hash list differs from main at the audited tip. Lists do change from the old branch to the merge because main brought the v4 reproduction entries and freeze-source list; those are inherited unchanged from main, not an unreported branch-side repinning. The follow-up edits no checksum list.
- **Tests:** SHA256SUMS test file is byte-identical at 7c3bbba, 52f2eac, and 18e542c. All CI tests equal main at the tip. No removed positive control or newly skipped SHA case in either layer.

## Follow-up review

`18e542c` modifies exactly three files: checker (+1/-6), REDTEAM (+4), inventory (+2/-2). It replaces the one-key ALLOWED_MISSING dictionary with `{}`, adds the refresh paragraph, and updates just the checker/REDTEAM inventory hashes and sizes. There are no test edits or checksum-list edits.

Independently hashing `git show 942f852:audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v3.log` gives:

`fcf370da026920417264c90eb2ff00b7e46b5dae4eb912f66b76891abe3552b6`

That is exactly the v3 line in main's SHA256SUMS and the digest of the tip's file. Removing its exception is correct: the old code deliberately errors when an allow-listed missing file reappears matching. At the final tip no live missing-file exception remains.

## Isolation / hijack analysis and bounded negative controls

Checker imports at lines 32–37 precede all validation. Workflow line 117 is the unisolated invocation. The separate negative harness uses Python **3.12.16**, matching CI's requested minor. The box has no bare `python` command (initial exact spelling exited 127); replay used the explicit Python 3.12 executable with the same script arguments, cwd, and no isolation. No alias, workflow, or repo modification was needed.

The planted hashlib module proxies `_hashlib.openssl_sha256`, forwarding updates, but substitutes the known original digest only when the actual tampered download_new.sh digest is encountered. Thus the real checker executes, hashes all entries, and prints its own normal PASS; this is not just a fake banner or early process exit. Neither checker nor checksum list was changed. The plant was not committed; whether tracked does not affect Python import resolution. The disposable copy's index contains the original tracked file list.

| Control | Measured result (Python 3.12.16) |
|---|---|
| Unmodified, normal / `-I -B` | PASS / PASS, exit 0; 7 lists, 61 verified |
| Append audit comment to download_new.sh, no plant | FAIL / FAIL isolated; exit 1, MISMATCH, 60 verified |
| Delete download_new.sh | FAIL exit 1, MISSING |
| Delete v3 log | FAIL exit 1, MISSING; no allow-list notice |
| Restore exact v3 bytes | PASS exit 0, 61 verified |
| Same download mismatch + sibling hashlib.py | **FALSE PASS exit 0, 61 verified, zero errors** |
| Same mismatch + same plant + `-I -B` | FAIL exit 1, MISMATCH |
| Append `../../../../etc/passwd` SUMS entry | FAIL exit 1, lexical path escape |
| Matching-hash symlink into similarly prefixed sibling root | FAIL exit 1, symlink escape (prefix boundary holds) |
| Restore original files, remove plants | PASS exit 0, 61 verified |

ALLOWED_MISSING uses exact `(list path, entry text)` tuple lookup, not prefix matching, and is empty at this tip. EXCLUDED has the same three explicit historical-list exclusions at old tip, merge, and follow-up. The synthetic missing/returned/stale allow-list cases remain unchanged in the suite. No extra bypass was established by these bounded containment checks.

**Acceptance requirement for S-B1:** isolate the production entrypoint before any shadowable import (or equivalently protect the workflow launch), and add script-level regression controls proving a sibling module cannot suppress a real mismatch while the unmodified-tree control still PASSes. To match main's protection for both local and CI invocation, protect the script too. Do not rely on ordinary suite PASS counts as evidence of import-boundary security.

## What ran / independent counts

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/ci/tests`: **156 tests, OK, exit 0**, Python 3.13.5; 2.509 seconds. Existing ResourceWarnings emitted.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/redteam -v`: **190 total, 181 ordinary passes, 9 expected failures, 0 unexpected failures/successes, 0 skips, exit 0**, Python 3.13.5; 187.772 seconds.
- `python3 tools/ci/check_sha256sums.py`: **PASS**, 7 lists / 61 verified / 0 allow-listed / 0 errors, exit 0 (Python 3.13.5).
- `python3 -I tools/ci/check_sha256sums.py`: same PASS.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/ci/check_current_inventory.py`: **PASS**, 0 errors, exit 0.
- Inventory generator stdout + cmp: byte-identical; **3409 rows**.
- Independent Python 3.12 negative/positive controls: **12 invocations**, outcomes above; one deliberate false-PASS establishes blocker.
- `git diff --check origin/main...HEAD`: exit 0.

## Honest limits / stop point

A hard blocker was established, so no widening into extra attack classes or fixes. No full Lean matrix, full GitHub Actions matrix, remote CI execution, all-other-job end-to-end bypass, environment-startup-hook replay, broad module-shadow sweep, or separate full-suite run on 7c3bbba/52f2eac. Red-team suite was launched as requested and includes its own Lean negative-control tests; this is not the full Lean matrix. No proof of historical author intent or whether an editor was used. No 040282 packet content was inspected or quoted. No upload-fix branch/worktree was used and upload_new.sh was not edited; the requested existing suite may mutate only its own safe mirrors.

## Evidence

Directory: `/workspace/audit_r001/sha256sums_evidence/`.
- `ancestry.log`, `stat.log`, `remote_final.log`, `final_status.log`.
- `diff_395ea53_7c3bbba.txt`, `diff_7c3bbba_52f2eac.txt`, `diff_942f852_52f2eac.txt`, `diff_52f2eac_18e542c.txt`, `merge_resolution.diff`.
- `ci.log`, `redteam.log`, `checker.log`, `isolated.log`, `inventory.log`, `regenerated.csv`.
- `negative_controls.py`, `negative_controls.log`, `negative_results.json` and per-case logs, particularly `shadow_hashlib_py312.log` versus `shadow_hashlib_py312_isolated.log`.

No external actions taken. No source-repo file edits, branch changes, commits, pushes, PRs, or contacts. Detached audit status recorded at completion; all deliberate tampering confined to the disposable copy and restored before the final positive control.
