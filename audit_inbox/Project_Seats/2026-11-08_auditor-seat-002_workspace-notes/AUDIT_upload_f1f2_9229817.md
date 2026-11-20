# Auditor Seat 002: independent re-audit

## Verdict: CLEAN WITH NOTES

All three blockers from my 7daf35b audit are closed in the independently exercised fixtures, with non-vacuous regression tests. Original F1/F2 protections still work and harmless uploads still succeed. No new blocking defect was found in the claimed blocker scope. This verdict applies only to the exact tip below, not an unreviewed later change, and does not merge or open a PR.

- Completed: 2026-11-08 17:07:27 Europe/Tirane (CET).
- Branch: `fix/upload-new-f1f2`.
- Verified tip: `9229817b451c6176b9bf856354a760f52adba8d0`.
- Verified single parent: `7daf35b41c6abfe3b3f77e7be3f3f0ce7fe78c18`.
- Verified remote main: `942f8526daee5ac547f2e422101fa95c61eeef41`.
- `git rev-list --left-right --count 942f852...HEAD`: `0 2` (0 behind / 2 ahead).
- `gh pr list --repo jacobbrainard84-knightninja/AIEFS --head fix/upload-new-f1f2 --state open --json number,url`: `[]`.
- Worktree: `/tmp/wt_audit_upload_f1f2_9229817`, detached at reviewed SHA; final `git status --porcelain` empty.
- Usage checked during work: 44.8%, below the 50% stop.

## Review scope / facts checked

Read full incremental diff of upload helper, U17–U19 tests, README, and SHA256SUMS; inspected inventory diff and verified its deterministic output. Exactly these five files changed vs parent:

- `tools/sync/upload_new.sh`
- `tools/sync/tests/run_tests.sh`
- `tools/sync/README.md`
- `tools/sync/SHA256SUMS`
- `registry/artifacts_current.csv`

Used my previous independent fixture implementation as the baseline, not the author's note or reported counts. Extracted scripts are byte copies of the reviewed Git files. Re-ran independent fixtures with `new_upload.sh` = 9229817 and `old_upload.sh` = 7daf35b. **In this report's new artifacts, “old” means 7daf35b, not main.** The earlier report retains controls against main.

## Independent reproduction commands

```sh
python3 /workspace/review_r040282/audit_f1f2_9229817/probes.py
python3 /workspace/review_r040282/audit_f1f2_9229817/supplemental.py
```

These auditor-owned scripts create only temporary local bare remotes and dummy repositories. They retain exact fixture commands and full per-case logs. Executed command is `bash new_upload.sh --yes` for F1, and `bash new_upload.sh --yes --max-size-mb 1` for regular F2 fixtures. Explicit dry-run and no-yes controls are described below. Fake token-shaped text is generated at runtime from a prefix plus 36 X characters; no credentials are used.

### Blocker 1: tracked directory replacement

Baseline: `.gitignore` contains `*.log`, `folder/tracked.txt` is tracked. Mine adds ignored `folder/local.log` containing dummy precious text. Other clone removes tracked `folder/` and commits either a regular file `folder` or a symlink `folder -> README`; its push targets only the local bare remote.

- Directory-to-file, `bash new_upload.sh --yes`: **exit 1**, names `folder/local.log`, original content preserved, HEAD and bare remote unchanged.
- Directory-to-symlink, same command: **exit 1**, ignored child preserved, HEAD and remote unchanged.
- Positive directory-to-directory update (`folder/new.txt` incoming): **exit 0**, integration occurs, new child arrives, ignored local child preserved, no remote change.
- Expanded harness separately confirms dry-run exits 0, lists colliding descendants, and preserves them for both replacements.
- Parent-script independent controls: both replacements exit 0 and delete the ignored child; directory update succeeds and preserves it. Thus the new protection is not merely refusing all directory updates.

The new guard checks a real local directory at an incoming blob/symlink path, lists its ordinary untracked and ignored descendants, and feeds those into the existing pre-integration collision refusal. `--yes` does not bypass it. Normal tree updates are not classified as replacement blobs. Guard still runs after fetch, before pull.

Evidence: `new_tracked_directory.log`, `new_tracked_dir_symlink.log`, `new_tracked_dir_update.log`, plus corresponding `old_*` logs in the artifact directory.

### Blocker 2: merge-only blocked name

Fixture: diverging side/main commits, `git merge --no-commit --no-ff side`, add harmless dummy `credentials.json` only in the merge resolution, commit merge, then delete that path in another commit and change README.

`bash new_upload.sh --yes --max-size-mb 1`: **exit 1**, explicitly identifies `credentials.json` as a credentials-file name in an intermediate commit. HEAD and bare remote unchanged. No merge history published.

Parent-script independent control: **exit 0**, merge history pushed to dummy remote.

The name enumeration now uses `git log -m`, covering diffs against each merge parent; names are deduplicated before policy testing. It also captures path enumeration into a checked temp file instead of trusting an unchecked process substitution.

Evidence: `new_merge_name.log`, `old_merge_name.log`.

### Blocker 3: producer errors / fail-closed checks

Fixture: an unpublished `notes.txt` commit containing only generated dummy-token-shaped text. Isolated PATH shims delegate every ordinary invocation to real Git; each fault mode fails exactly one operation with status 7. The script being reviewed is unmodified.

1. `git cat-file --batch-check=*` fails: **exit 1**, `could not list/check unpublished objects`, HEAD/remote unchanged.
2. `git rev-list --objects ...` fails while the consumer may succeed: **exit 1**, same enumeration failure message, HEAD/remote unchanged. Confirms pipefail catches the first producer too.
3. `git cat-file blob ...` fails: **exit 1**, `could not check the contents`, HEAD/remote unchanged. Existing individual-blob fail-closed behavior retained.
4. Supplemental merge-aware `git -c ... log -m ...` failure: **exit 1**, path enumeration failure, HEAD/remote unchanged.
5. Empty-list positive: new `feature` branch initially points to fetched origin history; verified `git rev-list --objects HEAD --not --remotes=origin` output is genuinely empty. Add uncommitted harmless `fresh.txt`; run helper. **Exit 0**, helper commits/publishes `feature:fresh.txt` to local bare remote. Not an injected empty list that conceals content.

The object pipeline now completes into a temp file under shell `pipefail`, and its status is checked before parsing. Cleanup trap is in place. Individual blob content checking remains checked. No arbitrary history cutoff introduced.

Evidence: `new_batch_failure.log`, `new_revlist_failure.log`, `new_unreadable_blob.log`, `new_path_enum_failure.log`, `new_empty_list.log`, source in `probes.py` / `supplemental.py`.

## Original protection and extra-case reconfirmation

| Independent fixture / command | Observed at 9229817 |
|---|---|
| Ignored incoming same-path file, `--yes` | exit 1, local content/HEAD/remote preserved |
| Same fixture, no `--yes` (`--message dummy`) | exit 1 before confirmation, preserved |
| Same fixture, `--dry-run` | exit 0, names collision, preserved |
| Nonignored untracked same-path file | exit 1 at guard, preserved |
| Ignored dangling symlink collision | exit 1, link preserved |
| Ignored local file blocking incoming parent directory | exit 1, preserved |
| Committed dummy-token content (`notes.txt`) | exit 1, token-pattern reason; HEAD/remote unchanged |
| Same dummy content uncommitted | exit 0, explicitly skips it; nothing committed/pushed |
| 2 MiB blob committed then deleted; 1 MiB limit | exit 1, history size refusal; HEAD/remote unchanged |
| Same 2 MiB blob at HEAD; 1 MiB limit | exit 1; HEAD/remote unchanged |
| Ordinary harmless new file | exit 0, local commit and dummy-remote update succeed |
| Brand-new branch with dummy-token blob only in deleted history | exit 1; no branch push |
| Committed symlink with dummy-token-shaped target | exit 1, blob pattern detected |
| NUL-prefixed binary with dummy-token bytes | exit 0, pushed: unchanged accepted binary-skip limitation |

Original named protections also continue working on the parent tip; regressions specific to this increment are isolated by the controls below.

## Harness: observed counts, not author's assertions

```sh
cd /tmp/wt_audit_upload_f1f2_9229817
bash tools/sync/tests/run_tests.sh
# RESULT: 189 passed, 0 failed; exit 0

# Exact new harness with only upload_new.sh replaced by parent's script,
# in a throwaway copy outside any worktree:
bash /workspace/review_r040282/audit_f1f2_9229817/control_previous/tests/run_tests.sh
# RESULT: 167 passed, 22 failed; exit 1
```

All 22 parent-control failures are in U17/U18/U19: directory file/symlink replacements (10 assertions), merge-only blocked name (4), batch and rev-list producer failures (8). Individual-blob error and empty-list success controls still pass on parent. Tests are demonstrably non-vacuous; counts are assertions, not 22 separate flaws. Previous F1/F2 mutation tests are recorded in the prior audit; no tracked branch files were mutated for this re-audit.

Logs: `harness.log`, `harness_previous.log`.

## Hashes / inventory / docs

```sh
cd /tmp/wt_audit_upload_f1f2_9229817/tools/sync
sha256sum -c SHA256SUMS
# 8/8 OK, including all three updated payload files
python3 ../../tools/ci/check_current_inventory.py --repo /tmp/wt_audit_upload_f1f2_9229817
# 0 errors -> PASS
```

Inventory diff changes only hashes/lengths of the four changed non-inventory files. The deterministic checker regenerated expected data in memory and matched the committed CSV; no suspicious discrepancy. This confirms generated output, not a claim about the author's editing method. Logs: `hashes.log`, `inventory.log`.

README now accurately describes merge-aware path checking, checked enumeration, directory replacement scope, fetch metadata changes, text-only secret heuristics, the second-fetch race, and safe-base reset advice for new branches. It no longer presents these as universal secret/overwrite protection.

## Notes retained (not blockers)

- Inspect-only TOCTOU: remote may change between the guard's fetch and pull's second fetch. Not newly fixed or newly exercised here; now explicit in README.
- Content matching is a text heuristic; `git grep -I` intentionally skips binary/NUL-prefixed data. Independently reconfirmed. Not a general secret detector.
- Previously documented scope limitations remain: ignore enforcement is latest-tree only; metadata/external submodule histories are not scanned; new uncommitted symlink handling predates this committed-history fix. These are not assertions of universal coverage.

No additional serious defect found in the three blocker fixes under review. This is **CLEAN WITH NOTES**, not CLEAN, because accepted limitations remain.

## Artifacts / hygiene

- Main re-audit artifacts: `/workspace/review_r040282/audit_f1f2_9229817/` (full diff, scripts, JSON results, logs, prior-tip control copy).
- Independent dummy fixture roots: `/tmp/independent_f1f2_k88rp7xy` and `/tmp/independent_f1f2_ra68435w`.
- Worktree untouched and clean at exact reviewed tip.
- No PR opened; no GitHub push, commit, comment, or review. Dummy commits/local filesystem pushes only.
- No real credentials or personal details copied; no Researcher 040282 uploaded code executed. No unrelated fixes started.
