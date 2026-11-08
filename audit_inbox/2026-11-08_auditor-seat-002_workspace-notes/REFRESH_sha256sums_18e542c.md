# SHA256SUMS branch refresh — implementation handoff, not a CLEAN verdict

- Completed: 2026-11-08 15:51:48 Europe/Tirane.
- Repository: https://github.com/jacobbrainard84-knightninja/AIEFS
- Branch: `ci/check-sha256sums`
- Old tip: `7c3bbba9ba93cc7fe067d9a0a6d2b7882c12ed50`
- New pushed tip: `18e542c846bb683ad722c1ea15b809dd07c32feb`
- Merge commit: `52f2eac422469eb17d518609bfb278709ffd6445`
- Merge parents (in order): `7c3bbba9ba93cc7fe067d9a0a6d2b7882c12ed50`, `942f8526daee5ac547f2e422101fa95c61eeef41`.
- Follow-up `18e542c846bb683ad722c1ea15b809dd07c32feb` has sole parent `52f2eac422469eb17d518609bfb278709ffd6445`.
- Dedicated worktree: `/tmp/wt_sha256sums_refresh` (detached HEAD because the original local branch is already checked out elsewhere; no other worktree modified).

## Resolution

Only `registry/artifacts_current.csv` and `tools/redteam/REDTEAM.md` conflicted.
- Inventory was regenerated with `python3 registry/reconciliation/build_current_inventory.py`, never hand-merged.
- REDTEAM retained main's G1/G2/G2b/B1/G2c material and branch SHA256SUMS table/fix notes; removed the obsolete branch assertion that deleting the verifier is an open GAP, superseded by main's fixed case.
- repo-checks.yml merged without conflict. Verified exact equality with main after removing only the added sha256sums job and its header mention. The separate Lean workflow is byte-identical to main, including all three required matrix projects. Manifest implementation is byte-identical to main.
- SHA256SUMS checker and tests initially preserved byte-for-byte from old branch.

## Post-merge follow-up

Initial CI: 156 tests, all passed. Initial red-team: 190 tests, 179 passed, 2 failures, 9 expected failures.
Both unexpected failures were SHA256SUMS positive controls: main had restored `compare_b2a95dfbfbe3_v3.log` at its matching checksum (ERRATA E14), making the branch's missing-file allow-list entry stale. Removed that obsolete entry as the branch itself instructed; no checksum lists edited and no tests weakened. Added a refresh note and regenerated inventory in the separate follow-up commit.

## Final tests

- `python3 -m unittest discover -s tools/ci/tests`: 156 passed, 0 failed (exit 0).
- `python3 -m unittest discover -s tools/redteam -v`: 190 total, 181 passed, 9 expected failures, 0 unexpected failures (exit 0).
- `python3 tools/ci/check_sha256sums.py`: 7 lists, 61 verified entries, 0 allow-listed, 0 errors (PASS).
- `python3 tools/ci/check_current_inventory.py`: PASS (also verified after commit/push).
- Inventory: 3409 data rows (header excluded).
- `git diff --check origin/main`: passed; final status empty.
- Logs: `/workspace/review_r026/sha256sums_refresh_ci_final.log`, `/workspace/review_r026/sha256sums_refresh_redteam_final.log`. Initial logs without `_final` preserve the pre-follow-up failures.

## Scope and delivery

Final delta against main is exactly these six files:
- `.github/workflows/repo-checks.yml`
- `audits/reproductions/.gitignore`
- `registry/artifacts_current.csv`
- `tools/ci/check_sha256sums.py`
- `tools/redteam/REDTEAM.md`
- `tools/redteam/test_rt_sha256sums.py`

No pinned files, briefing, or Researcher 040282 content changed relative to main. No r026-cleanup or 040282 fixes started. No force-push, rebase, squash, branch deletion, PR, or push to main. Remote main remains `942f8526daee5ac547f2e422101fa95c61eeef41`. Fetched refs immediately before push and confirmed origin branch remained the old tip, so no pull was needed. Fast-forward push used explicit `HEAD:refs/heads/ci/check-sha256sums` and remote read-back confirms the new tip.

## Limits / independent review

This is NOT a CLEAN self-verdict; hand the pushed tip to Researcher 001. Nine existing expected-failure gaps remain in the red-team suite. Lean builds and the full GitHub Actions matrix were not run here; the requested stdlib self-tests and red-team suite were run. CI self-tests emitted existing unclosed-file ResourceWarnings but passed. A merge-index whitespace check reported whitespace inherited from main in reproduction diff/freezing report files; these files were not modified to paper over it. Final delta whitespace check against main passes. No known workflow job was dropped.
