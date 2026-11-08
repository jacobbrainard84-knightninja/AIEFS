# tools/sync — safe upload / download helpers

Plain bash scripts. They need only git (2.30 or newer) and coreutils. Run them from anywhere inside the repository. File names with spaces (e.g. `AI Agent Audits/...`) are handled.

| Script | What it does |
|---|---|
| `download_new.sh` | Pulls down what is new on GitHub without losing local work |
| `upload_new.sh` | Uploads only files that are new or changed locally |
| `untrack_artifacts.sh` | One-time cleanup: stops tracking build/cache/editor files that `.gitignore` already excludes |

If a script is not executable after download (files committed through the GitHub web/API may lose the executable bit), either make it executable once:

```
chmod +x tools/sync/*.sh tools/sync/tests/*.sh
```

or run it through bash, e.g. `bash tools/sync/upload_new.sh --dry-run`.

Always try `--dry-run` first. It shows what would happen and changes nothing.

## download_new.sh

```
tools/sync/download_new.sh --dry-run     # preview incoming commits and files
tools/sync/download_new.sh               # do it
```

- **Clean working tree:** it fast-forwards.
- **Uncommitted local changes:**
  1. It first copies them to `.git/download_new_backup/<timestamp>/`.
  2. It stashes them, fast-forwards, then re-applies them.
  3. If re-applying conflicts, it stops (exit 2) and tells you what to do. Your changes stay in `git stash list` and in the backup folder.
- **Local commits that are not on GitHub (diverged):** it stops and explains. Use `--rebase` to replay your commits on top of GitHub's.
- **A file deleted on GitHub that you still have:** by default your copy is KEPT on disk as an untracked file. Use `--apply-deletions` to let git remove it.
- **An incoming file would overwrite an untracked or ignored local file:** it stops and lists the files.
- **Afterwards:** it prints new, changed and deleted files, plus a summary.

## upload_new.sh

```
tools/sync/upload_new.sh --dry-run       # preview what would be uploaded / skipped
tools/sync/upload_new.sh                 # asks y/N, then commits and pushes
tools/sync/upload_new.sh -m "message" --yes
```

- It first runs `git fetch`. It checks incoming paths against local untracked or ignored files (e.g. a local `*.log`), including descendants of a tracked directory replaced by a file or symlink. On a collision it lists the files and stops before integration (fetch metadata has already changed). Normal directory-to-directory updates are allowed. `--yes` does not skip this check. Move or rename those files and rerun.
- It then integrates GitHub's changes with `git pull --rebase --autostash`. On a conflict it stops with instructions. The collision check is inspect-only: an upstream change between the guard fetch and the pull's second fetch remains a race; this is not universal overwrite protection.
- It uploads only new or changed files that `.gitignore` allows. It never uses `git add -f`.
- These are skipped, with the reason printed:
  - files over 95 MB (`--max-size-mb N` or `UPLOAD_MAX_MB=N` changes this)
  - names that look private: `.env*`, `*.key`, `*.pem`, `id_rsa*`, `credentials*`, `*token*`, `*.kdbx`, …
  - text files whose contents match private-key or API-token patterns (a heuristic, not a universal secret scan; `git grep -I` skips binary/NUL-prefixed blobs)
  - nested git repositories
- Files you deleted locally are only listed. They are deleted on GitHub only with `--include-deletions`.
- It refuses to run when files are already staged, for example leftovers from an earlier `git add -f`. To unstage them (this does not change the files): `git restore --staged :/`.
- It refuses to push local commits that contain oversized, secret-looking or force-added ignored files. It checks every local commit that is not on GitHub, not just the latest one:
  - the name of every file added or changed in any of those commits, including paths introduced only by a merge (diffs against each parent, deduplicated)
  - the size and contents (private key / API token patterns) of every file version GitHub does not already have, including files that a later commit deleted
  - force-added ignored files, at the latest commit

  Unpublished path/object enumeration and committed-blob content checks fail closed if they cannot complete. Content checks use the same text heuristic and binary skip described above; commit messages/metadata and external submodule histories are not scanned.

  For a branch that does not exist on GitHub yet, everything not already on another GitHub branch is checked (on an empty repository that is the whole history). To fix a refusal, undo those commits but keep the files with `git reset --mixed <safe-base>`, then rerun. Use `origin/<branch>` only if that ref exists and is the intended safe base; for a new branch select an existing reviewed base commit/ref instead.
- The commit message is `Upload via upload_new.sh <UTC time> (N file(s))`, or your own text via `-m`.
- It never force-pushes. If the push is rejected, just run it again.

## untrack_artifacts.sh (one-time cleanup)

```
tools/sync/untrack_artifacts.sh --dry-run
tools/sync/untrack_artifacts.sh
```

- **Untracks:** files that are tracked but ignored and are clearly artifacts: `.lake/`, `__pycache__/`, `*.pyc`, `*.olean`, office lock files `.~lock.*#`, editor swap and backup files. It also adds the missing `.gitignore` lines.
- **How:** everything happens in one commit using `git rm --cached`. Files stay on your disk and history is not rewritten.
- **Leaves alone:** other tracked-but-ignored files (logs, data, PDFs). They are only listed, so you can decide about them.
- **Confirms twice:** it asks y/N before committing and again before pushing.

## Notes

- **When another machine pulls the cleanup commit:** a plain `git pull` deletes the untracked artifact files from that machine's disk. Lean/Lake rebuilds `.lake/`; Python rebuilds `__pycache__/`. If such a file was rebuilt or changed locally, a plain pull refuses. `download_new.sh` avoids both problems because it keeps local copies.
- **Upload scope:** files ignored by `.gitignore` (e.g. `*.log`) are never uploaded. Audit logs under `AI Agent Audits/` are deliberately un-ignored (`!AI Agent Audits/**/logs/` and `!AI Agent Audits/**/*.log` in `.gitignore`), so they are uploaded. To publish another ignored file deliberately, add a similar negation line.
- **Tests:** `tests/run_tests.sh [path/to/git]` builds a throwaway bare "GitHub" repository and two clones under a temporary directory. It never contacts GitHub.
