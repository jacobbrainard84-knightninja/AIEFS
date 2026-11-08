# Refresh of fix/check-manifest-g1g2 onto main (merge, no rebase)

**This is NOT an independent CLEAN verdict.** Auditor Seat 002 wrote 14072c3 and cd64939. This refresh is the
author's merge plus self-checks. cd64939 (and 92c5d77 below) still need Researcher 001's independent audit.

Times are Europe/Tirane (UTC+1), 2026-11-07.

| | sha |
|---|---|
| old tip (origin, confirmed unmoved before push) | cd6493984b59c18fa2b73fa14756465dd3f106d8 |
| origin/main (confirmed unmoved before push) | ad58a46ae8da79c19b5484762363eb2e9f2f7923 (PR #8) |
| merge commit (09:13) | bff8bb844e1ef1654c512daca5e2fc247054166c |
| new tip (09:19), pushed | 92c5d77f9986fbab810ff8c11864f32f2c533e38 |

- Push: `cd64939..92c5d77`, fast-forward, no force. Confirmed by fetch afterwards. No PR opened. No branch deleted. No history rewritten.
- `git merge-base --is-ancestor`: ad58a46 is an ancestor of the new tip, and so is cd64939.
- The old merge-base was 47a8b31: main had 40 commits that g1g2 did not, and g1g2 had 8 that main did not (33d34ca red-team kit, b166c03, a428c32, cd179b5, f8eb5e8, 14072c3, cd64939).
- Work was done in the detached worktree /tmp/wt_g1g2_refresh. Author and committer: jacobbrainard84-knightninja.

## Conflicts and resolution
Main did not touch `tools/ci/check_manifest.py`, `tools/ci/tests/test_check_manifest.py` or `tools/redteam/test_rt_hashes.py`.
They merged cleanly and keep the G1/G2/G2b code byte-for-byte as it was on cd64939. Only two files conflicted:

1. `tools/redteam/REDTEAM.md` had 3 hunks:
   - Hash-pins table: kept g1g2. That keeps G1/G2 as fixed PASS rows, all G2b and G2b follow-up negative controls, and GAP G2c. Main's side was only the old "GAP verifier deleted" row, which G2 closes.
   - Comparator section: took main. That is the v4 table with G10/G11 as ordinary tests, the F1 NPZ dtype rows and the zip-pin notes. g1g2 had only the stale v3 table.
   - Fix notes: kept both. g1g2's G1/G2/G2b/G2b follow-up notes come first, then main's G3+G4 and Round 2 notes.
   - Unchanged from main: the "Counts are not hard-coded" Results heading, and every remaining honest GAP (claims lint 2, hygiene 3, Lean marker scan 2, matched-phase anchor 1).
2. `registry/artifacts_current.csv`: neither side was used. Once all other files were settled it was regenerated with `python3 registry/reconciliation/build_current_inventory.py`, in both commits.
   - Final file: 3406 data rows (3407 lines). It is byte-identical (`cmp`) to `build_current_inventory.py --stdout`.
   - An independent re-implementation (git ls-files + sha256/size + zip members) produced the same 3406 (container, path, sha256, size) tuples.
   - `check_current_inventory.py` and `verify_inventory_current.py` both pass.

Only 5 files now differ from main: artifacts_current.csv, check_manifest.py, test_check_manifest.py, REDTEAM.md and test_rt_hashes.py.
No hash-pinned file was edited (audit_manifest.json, artifacts.csv, the SHA256SUMS files, verify_manifest.py, .gitignore, check_lean.sh and the rest).

## Extra author fix (92c5d77): CI tests only; check_manifest.py unchanged
I mutation-tested check_manifest.py by disabling each guard in turn: -I, the hashed-bytes bootstrap, the duplicate-key hook, F5 parent symlinks, self symlink, outside-repo, hash, readable guard, stray .py, __pycache__, success line, count==1, problem-line, missing verifier and the coverage rules.
- Every G2/G2b guard is caught by the CI self-tests, the red-team suite, or both.
- Hole found: the CI self-tests (the only manifest tests that run in CI) did not exercise the G1 coverage rule at all. Disabling the empty-manifest rule, the empty-inputs rule, the listed-file-exists rule or the coverage counting line left CI green. Nothing anywhere caught the listed-file-exists rule.
- Fix: 4 ordinary rejecting CI tests, none xfail. Each uses a correctly pinned stub that prints the exact success line + OK, so only the coverage rule can fail it:
  - verifier-only manifest
  - verifier + manifest-only manifest
  - empty inputs_sha256 (with a --no-inputs control)
  - listed file missing
- Each new test fails against its matching mutant, including an `own = {key}` mutant.

## Independent check results on 92c5d77
| Check | Result |
|---|---|
| CI self-tests `python3 -m unittest discover -s tools/ci/tests` | 153 OK on Py 3.13.5 + pandas 3.0.6; 153 OK in venv_pd310 (pandas 3.1.0); 153 OK on Py 3.12.16 (CI's version) |
| red-team `unittest discover -s tools/redteam` | 173 tests OK, 9 expected failures, 0 unexpected successes, 0 skips (Lean ran) |
| lint_claims / --strict | PASS / PASS (0/0/0) |
| hygiene diff vs origin/main --pii / full tree | PASS (0 warnings) / PASS (3 existing warnings) |
| check_manifest (inputs / --no-inputs) | PASS: "checked 145 published files and 24 inputs; 2 post-manifest logs listed but not hashed", OK |
| check_artifact_pins | PASS: 2898 rows, 2839 match / 7 known-changed / 52 known-missing |
| check_modes --strict | PASS (0 errors, 119 warn-only) |
| check_current_inventory + generator cmp + independent generator | PASS / identical / identical (3406) |
| validate_registry_against_tree | exit 0; 2701 same + 7 changed + 52 missing + 138 zip = 2898 |
| verify_inventory_current | ALL ... GATES PASSED |
Analysis tests (v4.1 held-event, modular) were not run: they need pytest, and no file they touch differs from main.

## G1 / G2 / G2b negative controls
- Red-team expected failures went from main's 10 to 9: G1 and G2 were removed, and G2c (an honest residual) was added.
- G1: `AuditManifest.test_passed_manifest_with_no_data` and `test_passed_manifest_with_empty_inputs` are ordinary tests and reject. The 4 new CI tests reject too.
- G2: `ManifestWrapper.test_verifier_missing_fails` is ordinary and rejects. The CI test `test_missing_verifier_fails_closed` also rejects.
- Manual replay of the original G2b attack on a real checkout, with a published file tampered and a fake hashlib.py printing the success line + OK:
  - fake beside the verifier, unlisted: "ERROR ... .py file beside the verifier ... does not list", NOT run, FAIL.
  - fake listed and hashed in the manifest: -I ignores it, the real verifier reports `SIZE AIEFS_audit.md`, exits 1, FAIL.
  - fake in the repo root (cwd): exits 1, FAIL.
  - control: plain `python verify_manifest.py` with the fake beside it prints the forged OK. So the attack is real, and only isolation stops it.

## Remaining issues / owner items (not fixed here)
1. **OWNER:** audit_manifest.json and verify_manifest.py are not pinned outside the manifest. GAP G2c, a re-pinned stub printing the computed success line, passes CI. Pin them somewhere CI checks, and make the red-team suite a required check.
2. Low/informational: the wrapper itself runs as `python tools/ci/check_manifest.py`, not `-I`. A hashlib.py in tools/ci/, or a hostile PYTHONPATH, hijacks the wrapper process. A replay with PYTHONPATH confirmed it. This needs the same access as editing check_manifest.py, which is unpinned, so it adds no new capability. A hardening option: `python -I tools/ci/check_manifest.py` in repo-checks.yml.
3. Low: an unreadable evidence folder (os.listdir/os.stat) gives a traceback (still exit≠0, fail-closed) rather than a named ERROR. The stray-module check only looks at `*.py` and `__pycache__`, not packages or .so files. -I makes those harmless, and that is tested.
4. Running the verifier with plain `python` (not -B) leaves `evidence/__pycache__` if a local module was imported, and that makes check_manifest refuse to run. This is correct fail-closed behaviour; local users should delete it.

## Handoff
Ready for Researcher 001's independent audit of cd64939 + bff8bb8 (merge resolution) + 92c5d77. Nothing is blocking it.
