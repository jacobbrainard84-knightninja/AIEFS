# Fix: ci/check-sha256sums S-B1 (checker isolation) — Auditor Seat 002

NOT a CLEAN verdict. Authoring-seat fix for Researcher 001's FIXES REQUIRED on 18e542c; needs independent re-audit.

- Branch: ci/check-sha256sums
- New tip: c47ed8ad408f7431e6dcf37f468073564f6a8e00 (parent 18e542c846bb683ad722c1ea15b809dd07c32feb), fast-forward push, ~17:07 Europe/Tirane 2026-11-08
- main unchanged: 942f8526daee5ac547f2e422101fa95c61eeef41 (branch 7 ahead / 0 behind). No merge needed. No PR.
- Worktree: /tmp/wt_sha256sums_sb1. Evidence: /workspace/review_r026/sb1_evidence/

## 1. Independent reproduction on unfixed 18e542c (own plant: sb1_evidence/plant_hashlib.py)
Tamper: `echo 'echo TAMPERED-SB1-REPRO' >> tools/sync/download_new.sh` (listed 6a811cd5..., actual abeef034...).
Plant: tools/ci/hashlib.py proxying real hashlib, mapping the tampered digest to the listed one.
(First attempt was a no-op because my plant left the real module in sys.modules; fixed the plant, not the target.)

| run | rc | result |
|---|---|---|
| python3.12.16 tools/ci/check_sha256sums.py | 0 | 7 SHA256SUMS file(s), 61 entries verified, 0 allow-listed, 0 error(s) -> PASS |
| python3.12.16 -I -B ... | 1 | MISMATCH download_new.sh ...; 60 verified, 1 error(s) -> FAIL |
| python3.13.5 plain | 0 | ... 61 entries verified ... -> PASS |
| python3.13.5 -I -B | 1 | ... 1 error(s) -> FAIL |
| crude tools/ci/argparse.py printing PASS + os._exit(0), python3 plain | 0 | forged PASS line |
Logs: unfixed_plant_py312*.log, unfixed_plant_py313*.log, unfixed_argparse_forge.log. Plants removed, tamper reverted before the fix.
Verdict: S-B1 CONFIRMED.

## 2. Fix
tools/ci/check_sha256sums.py: check_manifest.py's self re-exec (`import sys as _sys`; if __main__ and not isolated -> os.execv(python -I -B <abspath> argv)) placed right after the docstring, before every other import; docstring paragraph explains S-B1 and the N1 residual.

## 3. Tests (CI suite): tools/ci/tests/test_check_sha256sums.py (7 tests)
Synthetic git repo (TARGET + SUMS, plus dummies for EXTRA_INCLUDE/EXCLUDED so they are not "stale"), copy of the real checker run as a script from <tmp>/tools/ci/ with cwd = repo root, PYTHON*/GITHUB_ACTIONS stripped; exact MISMATCH and final result lines asserted.
- clean tree PASS plain and -I -B; harmless sibling .py still PASS; tampered w/o plant FAIL both modes (controls)
- digest-proxy hashlib beside checker -> FAIL (S-B1 witness)
- forging hashlib/argparse/re/subprocess beside checker -> FAIL
- PYTHONPATH digest-proxy hashlib -> FAIL
- AST: only `import sys as _sys` precedes the isolated execv block

## 4. Mutation
- `if False and ...` on the re-exec: 6 failures (digest proxy, 4 forge subtests, PYTHONPATH); controls + structural pass. mutation_reexec_disabled.log
- block removed: 7 failures (adds structural). mutation_reexec_removed.log
Not committed; file restored from backup before commit.

## 5. Attack replay at the fix (real tree)
Clean: PASS 7/61 rc 0 on py3.12 and 3.13, plain and -I -B. Tampered + digest-proxy plant: FAIL MISMATCH rc 1 (py3.12, 3.13). Forging argparse/re/subprocess/hashlib: FAIL rc 1. PYTHONPATH plant: FAIL rc 1. fixed_*.log

## 6. Docs / inventory
REDTEAM.md: 3 rows in the SHA256SUMS table; S-B1 bullet after the sha256sums Round 2 note; D1: "5 today, 49 entries" / "6 files, 51 entries" marked historical with 7/61 today; the live missing-v3 exception wording now says retired in 18e542c (ALLOWED_MISSING empty). G2c, N1 unchanged.
registry/artifacts_current.csv regenerated (3410 rows; +1 new test, 2 hashes updated).

## 7. Counts at c47ed8a (python 3.13.5)
- unittest tools/ci/tests: 163 run, OK (was 156; +7)
- unittest tools/redteam: 190 run, OK (expected failures=9) -> 181 passed, 9 xfail, 0 unexpected
- check_sha256sums: 7 lists, 61 entries, PASS
- lint_claims, hygiene_scan (3 pre-existing BIG_FILE warnings), check_manifest, check_artifact_pins, check_modes --strict, check_current_inventory, verify_inventory_current: all PASS
Suite PASS counts are not import-boundary evidence; see sections 1, 4, 5.

## Files changed vs 18e542c
tools/ci/check_sha256sums.py (+12), tools/ci/tests/test_check_sha256sums.py (new, 183), tools/redteam/REDTEAM.md (+32/-6), registry/artifacts_current.csv (regenerated). No hash-pinned files touched; no plant committed.
