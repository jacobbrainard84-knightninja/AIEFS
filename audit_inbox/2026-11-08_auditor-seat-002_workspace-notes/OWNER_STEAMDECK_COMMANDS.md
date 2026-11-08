# Owner commands (Steam Deck): restore exec bits and turn on `check_modes --strict`

Prepared Fri Oct 30, 2026 (7:20–7:38 PM EDT). Run this **after** `integration/round5` (tip `0e0c82e`) is on GitHub, whether you pushed it or a connector uploaded it.

## What this does, in plain language

Some files in the repo are scripts you run directly, like `./check_lean.sh`. On Linux a file can only be run directly if its "executable" permission is set, and git stores that permission with the file. The uploads so far went through a web connector, which can only create plain (non-executable) files. So 17 scripts are currently stored as non-executable, and the "File modes" CI check warns about it.

The block below:
1. gets the round5 branch;
2. confirms each of the 17 files really starts with a `#!` line, so it is a script;
3. marks them executable in git (`git update-index --chmod=+x`) and on disk (`chmod +x`, so `git status` stays clean);
4. changes the CI step from warn-only to `--strict`, so the check fails if a script loses its bit in the future. This goes in the same commit, so CI never runs `--strict` against unfixed files;
5. regenerates `registry/artifacts_current.csv`, because the workflow file's content changed and the inventory check would otherwise fail;
6. runs the strict check and the inventory check locally before committing;
7. commits under your own name and does a normal `git push` (no force), so nothing on GitHub is overwritten.

Only a real `git push` can record executable bits, which is why this is your step and not the connector's.

## Paste-safe block

- Change `cd ~/AIEFS` to wherever your clone is. The remote is assumed to be `origin`.
- Everything runs inside `( … )` with `set -e`, so the first error stops the block without closing your terminal.
- Nothing is pushed unless every check passes.

```bash
cd ~/AIEFS && (
set -eu
# 0. Clean start: refuse to run on top of uncommitted work
test -z "$(git status --porcelain)" || { echo "STOP: working tree not clean"; git status --short; exit 1; }

# 1. Get integration/round5 and switch to it (fast-forward only)
git fetch origin integration/round5
git switch integration/round5 2>/dev/null || git switch -c integration/round5 --track origin/integration/round5
git pull --ff-only origin integration/round5
test -f tools/ci/check_current_inventory.py || { echo "STOP: this is not the round5 tip (0e0c82e or later)"; exit 1; }

# 2. The 17 entry-point scripts; each must exist and start with #!
FILES="lean/AIEFProofs/check_lean.sh
tools/sync/download_new.sh
tools/sync/tests/run_tests.sh
tools/sync/untrack_artifacts.sh
audits/engineering/verify_inventory.py
tools/ci/check_manifest.py
tools/ci/hygiene_scan.py
tools/ci/lint_claims.py
lean/AIEFProofsKn/check_lean_kn.sh
tools/ci/check_artifact_pins.py
tools/ci/check_current_inventory.py
tools/ci/check_modes.py
tools/ci/lean_presence.sh
audits/engineering/validate_registry_against_tree.py
audits/engineering/verify_inventory_current.py
registry/reconciliation/build_claims_reconciliation.py
registry/reconciliation/build_current_inventory.py"
for f in $FILES; do
  test -f "$f" || { echo "STOP: missing $f"; exit 1; }
  head -c2 "$f" | grep -q '^#!' || { echo "STOP: no #! line in $f"; exit 1; }
done

# 3. Set the bit in git's index and on disk
for f in $FILES; do git update-index --chmod=+x "$f"; chmod +x "$f"; done
# Freezing scripts: only present after the freezing merge (update-index errors on missing paths)
for f in lean/AIEFFreezeCore/check_lean_freeze.sh research/freezing/lean/check.sh; do
  if [ -f "$f" ]; then head -c2 "$f" | grep -q '^#!' && git update-index --chmod=+x "$f" && chmod +x "$f"; else echo "skip (not in tree yet): $f"; fi
done

# 4. Flip the CI step to --strict (exactly one line should change)
sed -i 's|run: python tools/ci/check_modes.py$|run: python tools/ci/check_modes.py --strict|' .github/workflows/repo-checks.yml
grep -c 'check_modes.py --strict$' .github/workflows/repo-checks.yml | grep -qx 1 || { echo "STOP: --strict flip did not apply exactly once"; exit 1; }

# 5. Regenerate the current inventory (the workflow file's content changed)
python3 registry/reconciliation/build_current_inventory.py
git add .github/workflows/repo-checks.yml registry/artifacts_current.csv

# 6. Local checks; nothing is committed unless these pass
python3 tools/ci/check_modes.py --strict
python3 tools/ci/check_current_inventory.py
python3 tools/ci/check_artifact_pins.py

# 7. Commit under your own git identity, show it, then push normally (no force)
git commit -m "Restore executable bits on entry-point scripts; check_modes --strict in CI"
git show --stat --format='%h %s' HEAD
echo "tree $(git rev-parse HEAD^{tree})  (local reference owner/modes-strict 60d44e5 has tree 18ebbb49cac146ef8db44abd84c49bbf70fc945b)"
git push origin integration/round5
)
```

## What to expect

- The commit changes **19 files**: 17 show up as `mode change 100644 => 100755` with 0 lines changed, plus `repo-checks.yml` (1 line) and `artifacts_current.csv` (1 line, the yml's new hash).
- `check_modes --strict` reports 17 checked and 0 not executable. It still prints some warnings about other `#!` files that are not on the known list. Those are warnings, not errors.
- Before freezing is merged, the tree hash printed in step 7 should equal `18ebbb49…`, the tree of the reference commit `owner/modes-strict` `60d44e5` prepared on the merge-prep box. If it differs, nothing is wrong yet; compare with `git show --stat HEAD`.
- If the push is rejected as non-fast-forward, someone pushed in between. Run `git pull --ff-only` if possible; otherwise stop and ask. **Do not use `--force`.**
- The CI job keeps its display name "File modes (warn-only)", so branch protection doesn't need changing. Rename it later if you like, then update the required-check name.
- **After freezing is merged:** run the block again. The two freezing scripts are then picked up, step 4 finds nothing to flip and stops at the grep check. For that rerun, delete step 4 and keep steps 5–7.
