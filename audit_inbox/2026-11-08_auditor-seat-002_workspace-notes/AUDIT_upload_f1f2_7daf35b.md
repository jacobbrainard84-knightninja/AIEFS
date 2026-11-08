# Auditor Seat 002: independent upload-helper review

## Verdict: FIXES REQUIRED

The ordinary F1/F2 witnesses are fixed, and the new harness is non-vacuous. However, an incoming directory-to-file replacement still deletes ignored local data, merge-only intermediate secret-named paths bypass the history name check, and failure of blob enumeration is not fail-closed. Do not open the PR at this tip.

- Review completed: 2026-11-08 16:59:33 Europe/Tirane (CET)
- Remote branch verified: `fix/upload-new-f1f2` = `7daf35b41c6abfe3b3f77e7be3f3f0ce7fe78c18`.
- Exactly one parent: `942f8526daee5ac547f2e422101fa95c61eeef41`, also independently verified as remote main.
- `git rev-list --left-right --count 942f852...HEAD`: `0 1` (0 behind / 1 ahead).
- `gh pr list --repo jacobbrainard84-knightninja/AIEFS --head fix/upload-new-f1f2 --state open --json number,url`: `[]`.
- Dedicated detached worktree: `/tmp/wt_audit_upload_f1f2`. Final `git status --porcelain`: empty.
- Weekly usage observed during review: 39.9%, below the 50% stop.

## Scope / reviewed files

The only changed files are exactly those reported:
1. `tools/sync/upload_new.sh` (full diff and full file)
2. `tools/sync/tests/run_tests.sh` (full added U12–U16 diff, setup, and executed entire harness)
3. `tools/sync/README.md`
4. `tools/sync/SHA256SUMS`
5. `registry/artifacts_current.csv`

Also compared `download_new.sh:74–104`, read the earlier independent baseline `/workspace/review_r040282/REPRO_r001_items.md`, and ran the current-tree inventory checker. The author's local fix note was not used as a verdict. No Researcher 040282 uploaded code was executed. No project tracked files were modified; mutations were outside the checkout. No GitHub push, PR, review, comment, or other remote write was made. Dummy fixture commits/pushes went only to temporary local bare remotes.

## Blocking finding 1: F1 still loses ignored data inside a tracked directory

Location: `upload_new.sh:89–101` (`in_head` treats any object type, including a tree, as tracked; incoming path check does not enumerate ignored descendants).

Independent fixture:
```sh
# Baseline in both clones: .gitignore contains *.log; folder/tracked.txt is tracked.
# Local mine:
printf 'LOCAL PRECIOUS' > folder/local.log
# Other clone:
git rm -r folder
printf upstream > folder
git add -A && git commit -m 'dummy directory-to-file replacement'
git push origin main  # LOCAL bare remote only
# Local mine:
bash /workspace/review_r040282/audit_f1f2/new_upload.sh --yes
```
Observed: exit **0**, no collision warning, fast-forward, `folder` becomes an upstream regular file and `folder/local.log` is gone. HEAD advances; no stash or recovery copy is made by the uploader. This is directly within the F1 ignored-local-file preservation goal, not just a cosmetic message issue. Old script has the same loss.

Evidence: `audit_f1f2/new_tracked_directory.log`; fixture `/tmp/independent_f1f2_94ukhw8o/new_tracked_directory/`. Require a regression covering ignored descendants of tracked directories replaced by incoming files/symlinks, and refuse before integration with local contents intact.

## Blocking finding 2: merge-only intermediate secret-named paths bypass F2

Location: `upload_new.sh:212–216`: `git log --name-only` omits merge diffs by default. Content scanning cannot substitute for path-name policy when text itself is harmless.

Independent fixture, from baseline main:
```sh
git switch -c side
printf side > side.txt; git add -A; git commit -m dummy
git switch main
printf main > main.txt; git add -A; git commit -m dummy
git merge --no-commit --no-ff side
printf 'dummy harmless text' > credentials.json
git add -A; git commit -m 'dummy merge with extra path'
git rm credentials.json
printf changed > README; git add -A; git commit -m 'dummy remove path'
bash /workspace/review_r040282/audit_f1f2/new_upload.sh --yes --max-size-mb 1
```
Observed: exit **0**, pushed to local bare remote. `main~1:credentials.json` exists on that remote. The path is first introduced in the two-parent merge and absent at HEAD, so both tip checking and the default log name traversal miss it. The blob's harmless dummy content passes the content regex. This violates the specific claim to name-check every added/changed path in every unpublished commit.

Evidence: `audit_f1f2/new_merge_name.log`, `audit_f1f2/merge_evidence.log`; fixture `/tmp/independent_f1f2_94ukhw8o/new_merge_name/`. Require merge-aware history path checks plus a test where a blocked-name path is introduced only by a merge and subsequently deleted.

## Blocking finding 3: object-enumeration failure allows upload

Location: `upload_new.sh:218–226`: producer pipeline is a process substitution; its failure is not checked. The earlier `git rev-list --quiet` only preflights commit traversal, not batch object metadata production.

Fault injection used an isolated PATH shim, not modified repository code. It delegated every command to real Git except:
```sh
if [ "$1" = cat-file ] && [[ "$2" == --batch-check=* ]]; then exit 7; fi
```
Fixture: unpublished committed `notes.txt` with the runtime-generated dummy token-shaped string. Run `PATH=<shim>:$PATH bash new_upload.sh --yes`.

Observed: exit **0**, local bare remote advances and receives the token-shaped dummy file. No content check occurs because the enumeration loop sees no records. This is a robustness/fail-closed gap, not a claim that ordinary Git normally fails this way. The claimed unreadable-content contract must cover failures obtaining the blob list as well as materializing individual blobs. Require checked enumeration completion/status and a regression that forces its producer to fail.

Positive fault control: a shim failing only `git cat-file blob ...` exits **1**, says `could not check the contents`, and leaves HEAD and remote unchanged. Thus the individual-blob error branch works, but the surrounding enumeration is not fail-closed.

Evidence: `audit_f1f2/new_batch_failure.log`, `audit_f1f2/new_unreadable_blob.log`; fixture `/tmp/independent_f1f2_94ukhw8o/new_committed_token/`. The exact shims and commands are retained in `probes.py`.

## Independent named witnesses and extra cases

Reproduction entry point (all dummy data, no network push):
```sh
python3 /workspace/review_r040282/audit_f1f2/probes.py
```
The script creates a separate local bare remote and two disposable clones per case and executes extracted new/old upload scripts. Its source, per-case stdout/stderr, and `results.json` are retained. `--yes` is the command suffix except where stated; F2 tests use `--yes --max-size-mb 1`. Token text is assembled at runtime from a prefix and 36 X characters, never a real credential.

| Fixture / command | New tip observed | Main old script control |
|---|---|---|
| Ignored `collision.log`, upstream force-added same path; `--dry-run` | rc 0, collision listed, real-run-stop message, local content + HEAD + remote unchanged | rc 0, no collision warning, no overwrite in dry-run |
| Same ignored path, no `--yes` (`--message dummy`) | rc 1 at guard, content/HEAD/remote unchanged | rc 0, silently overwrites before prompt |
| Same ignored path, `--yes` | rc 1, content/HEAD/remote unchanged | local data already lost in preceding no-yes control; rc 0 on rerun |
| Nonignored untracked `collision.txt` | rc 1 at guard, original content/HEAD/remote unchanged | rc 1 from Git's own later integration check, preserved |
| Ignored dangling symlink `collision.log -> absent-dummy` | rc 1, symlink/HEAD/remote unchanged | rc 0, replaces symlink |
| Ignored local file `block.log` blocks incoming `block.log/child.txt` | rc 1, content/HEAD/remote unchanged | rc 0, replaces local blocker |
| Ignored child of tracked directory, incoming directory-to-file replacement | **rc 0, ignored child deleted** | same loss |
| Committed `notes.txt` with dummy token-shaped text | rc 1, key/token message, HEAD/remote unchanged | rc 0, pushed |
| Same text uncommitted | rc 0, explicitly skipped, no commit/push/remote change | same skip behavior |
| 2 MiB `big.dat` committed then deleted, README changed; limit 1 MiB | rc 1, HEAD/remote unchanged | rc 0, pushed history |
| Same 2 MiB blob still at HEAD; limit 1 MiB | rc 1, HEAD/remote unchanged | rc 1 |
| Ordinary new `harmless.txt` | rc 0, commit created and local bare remote updated | rc 0, same success |
| New `feature` branch, dummy-token `notes.txt` committed then deleted | rc 1, history token detected, no branch published | rc 0 but no push: old unrelated no-tip-difference behavior; see note below |
| Committed symlink with dummy token-shaped target | rc 1, blob content detected, HEAD/remote unchanged | rc 0, pushed |
| Individual blob materialization failure via PATH shim | rc 1, explicit fail-closed message, HEAD/remote unchanged | not needed |
| Batch metadata enumeration failure via PATH shim | **rc 0, dummy-token commit pushed** | not needed |
| NUL-prefixed binary blob with dummy-token bytes | rc 0, pushed (existing binary skip policy) | same skip policy |
| Merge-only `credentials.json`, harmless content, later deleted | **rc 0, blocked-name history pushed** | rc 0, pushed |

The new branch witness's remote-main unchanged field is not sufficient on its own to establish branch absence; the new script exits before push and the independent U16 harness also explicitly verifies that `feature` is not created. In the old script, an add/delete-only new branch has no UNPUSHED tip paths and prints nothing to upload; its lack of U16 rejection is real but this particular fixture does not prove a successful old-script push. The independent ordinary F2a and F2b controls do prove successful old-script pushes. The new harness's U16 token-message assertion is what fails against the old script.

For every ordinary new-script refusal above, the dedicated local target content/link was preserved (F1), HEAD was unchanged, and the bare remote was unchanged. The F1 guard itself writes no worktree/index content; fetch updates metadata, so 'nothing changed' should not be read as literally no Git metadata changes.

## Harness and mutation / non-vacuity results

Observed by running, not copied from the author's note:
```sh
cd /tmp/wt_audit_upload_f1f2
bash tools/sync/tests/run_tests.sh
```
- Unmodified tip: **142 passed / 0 failed**, exit 0.
- Same new harness with main's old `upload_new.sh` in a throwaway copy: **125 passed / 17 failed**, exit 1.
- Remove only new F1 guard in a throwaway copy: **135 passed / 7 failed**, exit 1.
- Remove only new F2 history/blob scan in a throwaway copy: **132 passed / 10 failed**, exit 1.

The non-vacuity controls genuinely detect removed protection. Some failures cascade because the harness reuses a sandbox; counts are assertions, not independent bug counts. No branch files were mutated. Logs: `audit_f1f2_harness.log`, `audit_f1f2/harness_{old,no_f1,no_f2}.log`. These existing tests do not cover the three blocking counterexamples above.

## Guard placement / comparator

- New guard is after `git fetch --prune` and before `git pull --rebase --autostash`, only if target branch is behind. `--yes` is not consulted by it; a real collision calls `die` and no pull happens on that path. Verified with/without `--yes`.
- Common core is equivalent to `download_new.sh:74–104`: changed incoming paths which exist locally and are not in HEAD are collisions, including ignored files and dangling symlinks. Added parent-component loop is **stronger** than downloader: it handles a local file/symlink blocking an incoming directory.
- Both use existence of any `HEAD:path` object instead of distinguishing blobs from trees, leaving the blocking directory-to-file descendant loss.
- Dry-run continues reporting after listing collisions but does not integrate; ordinary fixture exits 0 as claimed. A separate safety error can still produce nonzero in more complex dry-runs.

## Object scope, residual notes, README

- `rev-list --objects HEAD --not --remotes=origin` is a reasonable boundary for blobs not already reachable from fetched origin branches. It deliberately does not re-audit content already reachable on another remote branch. Different configured remote names are passed through consistently. It can conservatively overscan stale/unrelated local history, cost time and produce refusals; no arbitrary history-size cutoff is used. The blocking problem here is unchecked producer status, not this ordinary reachability boundary.
- Committed symlinks are blobs and were checked successfully. Empty blobs are traversed and ordinarily return clean. Gitlinks/submodules are not recursively scanned as external repositories; working-tree nested repositories are skipped. The symlink fast path for *new uncommitted* symlinks predates this patch and bypasses working-tree name/content checks before the script creates its own commit (scan is before that commit); not introduced by this F2 unpublished-commit fix.
- Binary blobs are intentionally skipped by `git grep -I` both before/after this patch. A NUL-prefixed fake-token blob pushes successfully. This is an existing limitation, but README should describe the content check as a heuristic for text, not a universal secret guarantee.
- Ignore enforcement is still latest-tree only, accurately called out by README. Committed messages/author metadata and external submodule histories are not secret-scanned; no real sensitive content was sought or copied.
- README's ordinary overwrite and intermediate content/size examples match passing tests, but its universal overwrite protection and every-commit path-name claim are false for the blocking cases. Its reset advice is not valid for a brand-new branch when `origin/<branch>` does not exist: choose an existing safe base instead. Minor process/docs note aside from the blockers.
- An upstream update between guard fetch and `git pull`'s second fetch is a remaining TOCTOU surface by inspection; not independently exercised here, and not needed for this verdict.

## Hashes / inventory

```sh
cd /tmp/wt_audit_upload_f1f2/tools/sync
sha256sum -c SHA256SUMS
# 8 of 8 OK, including upload_new.sh, README.md, tests/run_tests.sh
cd /tmp/wt_audit_upload_f1f2
python3 tools/ci/check_current_inventory.py
# 0 errors -> PASS
```

Inventory diff changes only the four rows corresponding to the changed non-inventory files (hash and byte count). Deterministic checker regenerates expected content in memory and found an exact match. This proves correct generated output, not how the author physically produced it; no suspicious hand-edited discrepancy found. `audit_f1f2/inventory.log` contains the observed result.

## Audit artifacts and hygiene

- Full reviewed diff: `/workspace/review_r040282/audit_f1f2.diff`.
- Independent probe source/results/logs: `/workspace/review_r040282/audit_f1f2/`.
- Local bare fixtures: `/tmp/independent_f1f2_94ukhw8o` (retained, only dummy data).
- Worktree remains detached at reviewed SHA and clean. No tracked project changes, no network pushes, no PR. No own-code approval given. Findings should go to Researcher 001 for correction and a new independent review before any PR.
