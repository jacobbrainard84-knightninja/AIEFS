# Red-team negative controls

This folder is a negative-control suite for the repo's own checkers. Each test
builds a **known-false input** in a temporary copy and asserts that the checker
**rejects** it. A checker that is good at saying "PASS" has only been proven
useful once we've seen it say "FAIL" on something we broke on purpose.

- **PASS** = the checker correctly rejected the false input (normal `ok` test).
- **GAP** = the checker *accepted* the false input. These tests are kept as
  `unittest.expectedFailure` (via `rtcommon.gap`) and named `test_GAP_*`.
  **The checkers are deliberately not fixed here**; each GAP is a finding for
  the Head Researcher / owner to decide on. When a checker is fixed, its GAP
  test starts "unexpectedly succeeding" and should be turned into a normal test.

## How to run

```
python3 -m unittest discover -s tools/redteam -v      # from repo root
# or
cd tools/redteam && python3 -m unittest discover -v
```

About 100 s total (the comparator file is about 60 s; the Lean file is about 20 s
and needs `lake` from elan on PATH or in `~/.elan/bin`. Without it the Lean
axiom-audit tests are skipped). Needs numpy and pandas.

This suite is **not** in CI discovery (`tools/ci/tests`) on purpose: it is
slow, it needs Lean, and its expected failures document open gaps rather than
regressions. The existing CI tests are unaffected
(`python3 -m unittest discover -s tools/ci/tests`).

## Fixture safety

No real file is ever modified:

- `farm()` mirrors the repo into a temp dir using symlinks (skipping `.git` and
  `__pycache__`); `tamper()` *unlinks* the symlink and writes a new file, so the
  original is only ever read. `materialize()` turns symlinked parent dirs into
  real dirs before tampering below them.
- `copy_real()` makes real copies where a checker resolves paths itself.
- Hash-pinned scripts (comparator, verifier, check_lean.sh) are run or read
  **unmodified**; the Lean tests extract the heredocs embedded in
  `lean/AIEFProofs/check_lean.sh` at test time and run them against a tiny
  core-only lake project, because the full script needs a Mathlib build.
- A GAP only counts as confirmed if the failure is exactly "checker ACCEPTED a
  known-false input". Any other exception turns into a skip labelled
  "GAP fixture broken", so a broken fixture can't pass itself off as a finding.
- Fake secrets in the hygiene tests are assembled at runtime so the source
  file itself contains no secret-shaped strings.

Side note found while building this: a stray local
`__pycache__/aief_experiment_engine_v1.cpython-313.pyc` (git-ignored) makes
`check_artifact_pins.py --no-git` fail, because that path is a KNOWN_MISSING
row. The farm skips `__pycache__` for this reason.

## Results

Counts are not hard-coded here; run the suite (`-v`) for the current number of tests, PASSes
and expected failures (GAPs). Tables describe the checkers in the same commit as this file.

### Hash pins and manifests: `test_rt_hashes.py`

| Test | Checker | Result |
|---|---|---|
| control: untampered mirror | check_artifact_pins.py --no-git | PASS (accepted) |
| one byte changed in pinned file | check_artifact_pins | PASS (PIN_MISMATCH) |
| pinned file deleted | check_artifact_pins | PASS (PIN_MISSING) |
| file tampered and its pin rewritten to match | check_artifact_pins | PASS (REGISTRY_CHANGED) |
| registry row cites nonexistent artifact | check_artifact_pins | PASS (REGISTRY_CHANGED) |
| control: untampered audit copy | AI Agent Audits verify_manifest.py | PASS (accepted) |
| published file one byte changed | verify_manifest | PASS |
| manifest hash tampered | verify_manifest | PASS |
| unlisted PASSED.txt added | verify_manifest | PASS (UNLISTED) |
| corrupted seed in hashed run (--inputs) | verify_manifest | PASS (INPUT) |
| hashed input script edited (FROZEN_ETA) | verify_manifest | PASS (INPUT) |
| PASSED manifest listing only the verifier, no data (was GAP G1) | check_manifest.py coverage rule | PASS ("manifest lists no data files beyond the verifier itself") |
| PASSED manifest with empty inputs_sha256, inputs mode | check_manifest.py coverage rule | PASS ("inputs_sha256 is empty") |
| control: manifest listing the verifier + one data file | check_manifest.py --no-inputs | PASS (accepted) |
| wrapper propagates verifier failure | tools/ci/check_manifest.py | PASS |
| verifier deleted (was GAP G2; fixed on `fix/check-manifest-missing-verifier`) | check_manifest.py (`if not os.path.lexists(...)` in `main`) | PASS (ERROR "manifest verifier missing", exit 1) |
| control: real audit copy (verifier pinned, success line printed) | check_manifest.py | PASS (accepted) |
| 0-byte verifier (G2b) | check_manifest.py `check_verifier_file` | PASS (ERROR "sha256 ... does not match ... files_sha256['evidence/verify_manifest.py']", not run, exit 1) |
| comment-only verifier (G2b) | check_manifest.py `check_verifier_file` | PASS (same sha256 ERROR, not run) |
| real verifier edited to always `sys.exit(0)` (hash mismatch, G2b) | check_manifest.py `check_verifier_file` | PASS (same sha256 ERROR, not run) |
| verifier is a symlink to an outside exit-0 stub (G2b) | check_manifest.py `check_verifier_file` | PASS (ERROR "resolves outside the repository", not run) |
| verifier is a symlink to the genuine verifier outside the repo (G2b) | check_manifest.py `check_verifier_file` | PASS (same ERROR: location, not just bytes, is checked) |
| exit-0 stub with its manifest pin rewritten to match (G2b) | check_manifest.py `success_line` | PASS (ERROR "exited 0 but did not print its success line '...' followed by 'OK'") |
| stub printing "FAILED", exit 0, pin rewritten (G2b) | check_manifest.py `success_line` | PASS (same success-line ERROR) |
| unlisted fake hashlib.py / json.py / glob.py / pathlib.py beside the real verifier, published file tampered (G2b F1) | check_manifest.py `check_verifier_file` | PASS (ERROR ".py file beside the verifier that ... does not list", not run) |
| same fakes listed and hashed in the manifest (G2b F1) | check_manifest.py (`python -I -B`) | PASS (real verifier runs, reports SIZE, "exited 1") |
| same fakes in the repo root, the verifier's cwd (G2b F1 guard for the `-c` launch; also passes on 14072c3) | check_manifest.py (`-I`) | PASS (real verifier runs, "exited 1") |
| `__pycache__` folder beside the verifier (G2b F1) | check_manifest.py `check_verifier_file` | PASS (ERROR "bytecode cache folder beside the verifier", not run) |
| re-pinned stub printing a SHA256 problem line, then the success line + OK (G2b F3) | check_manifest.py output check | PASS (ERROR "printed a problem line") |
| re-pinned stub printing the success line twice (G2b F3) | check_manifest.py output check | PASS (ERROR "printed '...' 2 times (expected exactly once)") |
| verifier chmod 000 (G2b F4) | check_manifest.py `check_verifier_file` | PASS (ERROR "cannot be read (PermissionError: ...)", not run, no traceback) |
| duplicate files_sha256 key for the verifier, stub hash last (G2b) | check_manifest.py `load_manifest` | PASS (ERROR "duplicate key ... in a JSON object", not run) |
| evidence/ folder is a symlink inside the repo (G2b F5) | check_manifest.py `check_verifier_file` | PASS (ERROR "is a symlink (a folder on the verifier's path)", not run) |
| fake hashlib.py / json.py / subprocess.py / argparse.py / re.py beside the WRAPPER (`tools/ci/`), printing a forged PASS result, published file tampered (B1) | check_manifest.py self re-exec (`python -I -B`) | PASS (real verifier runs, reports the tampered file, "exited 1", FAIL; CI self-test `test_shadow_module_beside_wrapper_cannot_hijack_it`, both modes) |
| fake hashlib.py on PYTHONPATH of the wrapper (B1 / N1) | check_manifest.py self re-exec (`-I`) | PASS (same FAIL; CI self-test `test_shadow_module_on_pythonpath_cannot_hijack_wrapper`) |
| **GAP G2c** stub with its re-pinned hash in the manifest, printing the computed success line + OK, published file tampered | check_manifest.py | **GAP**: accepted; audit_manifest.json is not pinned outside itself |

### SHA256SUMS files: `test_rt_sha256sums.py`

| Test | Checker | Result |
|---|---|---|
| control: untampered mirror (lists AIEF_LEAN_PROJECT_LOCK_HASHES.txt) | tools/ci/check_sha256sums.py | PASS (accepted) |
| control: synthetic allow-listed missing entry (test-injected, independent of the live list) | check_sha256sums | PASS (accepted, NOTICE) |
| tools/sync script one byte changed | check_sha256sums | PASS (MISMATCH) |
| Lean source edited (AIEF_LEAN_SOURCE_SHA256SUMS.txt) | check_sha256sums | PASS (MISMATCH) |
| Lean lock file edited (AIEF_LEAN_PROJECT_LOCK_HASHES.txt) | check_sha256sums | PASS (MISMATCH) |
| listed file deleted | check_sha256sums | PASS (MISSING) |
| tracked SUMS file deleted | check_sha256sums | PASS (cannot read) |
| malformed SUMS line | check_sha256sums | PASS (malformed line) |
| SUMS entry `../` outside the repo | check_sha256sums | PASS (path escapes) |
| in-repo symlink pointing outside the repo | check_sha256sums | PASS (escapes via a symlink) |
| allow-listed file reappears with wrong content | check_sha256sums | PASS (MISMATCH) |
| allow-listed file reappears with matching content | check_sha256sums | PASS (stale allow-list entry) |
| allow-listed entry not in its SUMS file | check_sha256sums | PASS (stale allow-list entry) |
| unclassified hash list (`*hashes*.txt` neither checked nor excluded) | check_sha256sums | PASS (error) |
| stale exclusion entry | check_sha256sums | PASS (error) |
| no SHA256SUMS file at all (fresh git repo) | check_sha256sums | PASS (fail-closed) |
| not a git checkout | check_sha256sums | PASS (fail-closed) |
| fake hashlib.py beside the CHECKER (`tools/ci/`) proxying the real module and reporting the listed digest for a tampered listed file (S-B1) | check_sha256sums.py self re-exec (`python -I -B`) | PASS (MISMATCH, FAIL; CI self-test `test_digest_proxy_hashlib_beside_checker_cannot_hide_mismatch`) |
| fake hashlib.py / argparse.py / re.py / subprocess.py beside the checker printing a forged PASS result, listed file tampered (S-B1) | check_sha256sums.py self re-exec (`-I -B`) | PASS (MISMATCH, FAIL; CI self-test `test_forging_shadow_modules_beside_checker_cannot_hijack_it`) |
| fake hashlib.py on PYTHONPATH of the checker (S-B1 / N1) | check_sha256sums.py self re-exec (`-I`) | PASS (same FAIL; CI self-test `test_shadow_hashlib_on_pythonpath_cannot_hijack_it`) |

The main refresh restored the v3 comparison log (ERRATA E14). Its checksum now matches, so
the obsolete live missing-file exception was removed. The allow-list behavior remains tested
with synthetic entries. Current discovery verifies 7 checksum lists and 61 entries.

### Claims lint and hygiene: `test_rt_claims_hygiene.py`

Lint tests assert the exact ERROR line(s), the exact `== result: ...` line, exit 1 and no traceback
(the earlier "exact messages" wording overstated substring checks).

| Test | Checker | Result |
|---|---|---|
| control: copy passes | lint_claims.py | PASS (accepted) |
| status "Proved" (outside vocabulary) | lint_claims | PASS |
| status with trailing space | lint_claims | PASS |
| status wrong case | lint_claims | PASS |
| duplicate claim_id | lint_claims | PASS |
| empty claim_id | lint_claims | PASS |
| --strict changes the verdict: warning-only input (SSRH-ORIG row labelled `Retired / Superseded`) | lint_claims | PASS (exit 0 / PASS without --strict, exit 1 / FAIL with it) |
| vocabulary missing, --strict | lint_claims | PASS |
| row cites nonexistent artifacts (was GAP G3) | lint_claims | PASS (`cited artifact does not exist`) |
| false claim "R* = 0.40, proved in Lean" as Supported/Formal proof (was GAP G4) | lint_claims | PASS (`claims a formal/Lean proof ... but cites no existing .lean file`) |
| "proved in Lean" statement with an experimental scope | lint_claims | PASS |
| control: Formalized theorem row citing a real .lean file | lint_claims | PASS (accepted) |
| "Machine-checked in Lean 4 without sorry" statement, Conditional theorem scope | lint_claims | PASS (`claims a formal/Lean proof`) |
| "Lean 4 verifies ..." statement | lint_claims | PASS (`claims a formal/Lean proof`) |
| evidence_scope "Machine-checked theorem" (outside the 6 values) | lint_claims | PASS (`is not one of the 6 values`) |
| evidence_scope "Informal argument" (no substring match on "formal") | lint_claims | PASS (vocabulary error, no proof-claim error) |
| evidence_scope table removed from registry/README.md | lint_claims | PASS (`no '### Axis 2 ... evidence_scope' table found`) |
| `lean/AIEFProofs missing_file.lean` (missing path after an existing folder) | lint_claims | PASS (`cited artifact does not exist`) |
| `registry/claims.csv nonexistent/file.md` | lint_claims | PASS (`cited artifact does not exist`) |
| control: `§section`, `:LINE` and parenthesised prose after a real path | lint_claims | PASS (accepted) |
| control: synthetic KNOWN_MISSING_ARTIFACTS entry, file missing | lint_claims | PASS (accepted, NOTICE) |
| KNOWN_MISSING_ARTIFACTS entry whose file now exists | lint_claims | PASS (`but now exists`) |
| KNOWN_MISSING_ARTIFACTS entry no longer cited | lint_claims | PASS (`stale KNOWN_MISSING_ARTIFACTS entry`) |
| `evidence_scope` column deleted from claims.csv | lint_claims | PASS (one ERROR "required column 'evidence_scope' missing from the header", exit 1) |
| `supporting_artifacts` column deleted | lint_claims | PASS (one ERROR "required column 'supporting_artifacts' missing from the header", exit 1) |
| `statement` column deleted | lint_claims | PASS (one ERROR "required column 'statement' missing from the header", exit 1) |
| **GAP** Formalized theorem row citing an existing .lean file that lacks the claimed theorem | lint_claims | **GAP**: only the file's existence is checked (content is out of scope) |
| claims.csv missing (was GAP G5; fixed: `lint()` in tools/ci/lint_claims.py errors when the file is absent) | lint_claims | PASS (ERROR "claims registry missing", exit 1) |
| vocabulary heading removed (was GAP G6; fixed: `lint()` errors when `load_vocab` finds no values) | lint_claims (non-strict, as CI runs it) | PASS (ERROR "no status vocabulary found", exit 1) |
| status column renamed, value "Proved" (G6b, high; was NOTICE + PASS even with --strict) | lint_claims, with and without --strict | PASS (ERROR "status column 'audited_status' missing from the header", exit 1) |
| duplicate `audited_status` column, "Proved" in the first copy (G6c; was shadowed) | lint_claims | PASS (ERROR "duplicate column 'audited_status' in the header", exit 1) |
| header-only claims.csv (G5b; was "checked 0 claim rows", PASS) | lint_claims | PASS (ERROR "no data rows (header only)", exit 1) |
| earlier duplicate `## Status vocabulary` block adding "Proved" (G6d; first block won) | lint_claims | PASS (ERROR "2 '## Status vocabulary' headings", exit 1) |
| claims.csv starts with a UTF-8 BOM (was misleading "no 'claim_id' column") | lint_claims | PASS (ERROR "starts with a UTF-8 byte-order mark (BOM)", exit 1) |
| claims.csv contains a non-UTF-8 byte (was a traceback) | lint_claims | PASS (ERROR "not valid UTF-8 (byte 0xe9 at offset N)", exit 1) |
| claims.csv unreadable, chmod 000 (was a traceback; skipped as root) | lint_claims | PASS (ERROR "cannot be read (PermissionError: ...)", exit 1) |
| unclosed quote opening the last field swallows an appended "Proved" row (F1; was PASS, also with --strict) | lint_claims, with and without --strict | PASS (ERROR "not parseable as CSV (unexpected end of data)", exit 1) |
| extra `audited_status ` column (trailing space) holding "Proved" (F2; was not a duplicate, never checked) | lint_claims | PASS (ERROR "has leading/trailing whitespace" and "duplicate column ... differ only in case or surrounding whitespace", exit 1) |
| NUL byte in claims.csv (F6; csv accepts NUL on Python >= 3.11, was PASS) | lint_claims | PASS (ERROR "contains a NUL byte (offset N)", exit 1) |
| `--columns ""`, value "Proved" (F7; nothing was checked, PASS) | lint_claims | PASS (ERROR "--columns names no status column", exit 1) |
| **GAP** only vocabulary heading indented 4 spaces (Markdown code, not a heading), block adds "Proved" (F5, low) | lint_claims | **GAP**: `ln.strip()` match still selects the block |
| control: clean change | hygiene_scan.py | PASS (accepted) |
| .env file | hygiene_scan | PASS |
| id_rsa file name | hygiene_scan | PASS |
| private-key block in text | hygiene_scan | PASS |
| GitHub token in .py | hygiene_scan | PASS |
| AWS key, full scan | hygiene_scan | PASS |
| new .npz outside allowed folders | hygiene_scan | PASS (NEW_BINARY) |
| NUL-byte file named .txt | hygiene_scan | PASS (NEW_BINARY) |
| **GAP** binary outside allowed folders, full scan | hygiene_scan | **GAP**: WARNING only, exit 0 (diff mode catches it) |
| **GAP** token inside STORED zip under runs/ | hygiene_scan | **GAP**: binaries in allowed folders are not content-scanned |
| **GAP** token in a text file over 10 MiB | hygiene_scan | **GAP**: large files are not content-scanned |

### Reproduction comparator: `test_rt_comparator.py`

Target: `audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v4.py`
(run unmodified; listed in that folder's `SHA256SUMS`) on a temp copy of `runs/5a9f093a2fe0`.
Every rejection must be a real verdict: NOT REPRODUCED, exit 1, no traceback, and the specific
reason in `problems`. Zip-side tests write a rebuilt, reduced zip into a real temp `Project Histories` folder. A
rebuilt zip never matches the pinned zip sha256, so each such test also asserts its own reason.

Fix #1 (`fix/comparator-v4-gates`, 2026-10-31) closed the two comparator GAPs (G10, G11). Those tests
are now normal tests. In the "v3" column, *accepted* means v3 said REPRODUCED and *crash* means v3
died with a traceback instead of giving a verdict.

| Test | Result (v4) | v3 |
|---|---|---|
| control: untampered copy | PASS (REPRODUCED, `problems: []`) | same |
| CSV float cell (`D_B_final`, row 1) +1e-9 | PASS (abs diff > TOL) | PASS |
| CSV float cell +1e-11 (just over TOL 1e-12) | PASS (abs diff > TOL) | PASS |
| control: CSV float cell +1e-13 (inside TOL and RTOL) | PASS (REPRODUCED, `problems: []`) | same |
| CSV cell 0 -> 1e-14 | PASS (relative diff > RTOL) | **accepted** |
| CSV NaN / +inf / -inf | PASS (3 tests) | PASS |
| branch diagnostics +inf | PASS | PASS |
| seed NaN | PASS | PASS |
| seed value +1e-6 | PASS | PASS |
| seed bytes truncated | PASS ("unreadable in official run") | crash |
| seed deleted | PASS ("seed files missing in official run") | crash |
| extra fabricated seed file | PASS | PASS |
| seed integer field changed | PASS | PASS |
| seed `config_hash` label rewritten | PASS | **accepted** |
| two numeric columns swapped | PASS | PASS |
| branch labels swapped in CSV text column (was G10) | PASS ("non-numeric columns differ: branch") | **accepted** |
| `branch_family` relabelled | PASS | **accepted** |
| manifest model eta changed | PASS | PASS |
| manifest "schema" field changed (was G11) | PASS ("schema differs") | **accepted** |
| manifest other key changed (`workflow_version`) | PASS ("unexpected differing keys") | **accepted** |
| manifest extra key added | PASS | **accepted** |
| official manifest `source_sha256` rewritten | PASS | **accepted** |
| official manifest `config_hash` rewritten | PASS | **accepted** |
| rerun source file gets an extra code line | PASS ("code line(s) differ") | **accepted** |
| official scalar-summary CSV deleted | PASS | crash |
| official branch diagnostics deleted | PASS | crash |
| *Review r001 of `1250bbd` (G-A to G-E). "1250bbd" column: v4 before these gates* | | *1250bbd* |
| zip rebuilt with the same members (control for the zip pin) | PASS (only problem: "is not EXPECTED_ZIP_SHA256") | **accepted** |
| zip seeds replaced by official seeds relabelled to the rerun id (G-B) | PASS (zip sha; "SUSPICIOUS: 40 seed file(s) identical") | **accepted** (diff 0) |
| zip CSV replaced by the official CSV (G-B) | PASS ("SUSPICIOUS: scalar summary CSV") | **accepted** |
| zip branch diagnostics replaced by official (G-B) | PASS ("SUSPICIOUS: branch diagnostics") | **accepted** |
| zip manifest missing / empty (G-D) | PASS ("rerun manifest.json missing or unreadable"; 2 tests) | crash |
| zip CSV missing / empty (G-D) | PASS ("rerun file missing or unreadable"; 2 tests) | crash |
| zip branch diagnostics missing (G-D) | PASS ("missing in rerun run") | crash |
| zip seed member empty | PASS ("unreadable in rerun run") | PASS |
| zip stub manifest missing (G-D) | PASS ("zip stub … missing or unreadable") | crash |
| text "abc" in a numeric CSV cell, official / zip side (G-D) | PASS ("non-numeric text in numeric cells"; 2 tests) | crash |
| official manifest gets `"notes": null` (G-A) | PASS ("present in only one manifest ['notes']") | **accepted** |
| seed `config_hash` removed on both sides (G-C) | PASS ("config_hash label missing" in both runs) | **accepted** |
| manifest `model` removed from both manifests (G-E) | PASS ("model missing in rerun/official manifest") | **accepted** |
| *Review r001 of `f0aadce` (O1 and remaining tracebacks). "f0aadce" column: v4 before these fixes* | | *f0aadce* |
| official CSV row 1 `seed` +1 / +1000, `seed_index` +1 (O1) | PASS ("integer columns differ (exact)"; 3 tests) | **accepted** |
| official CSV `seed` written as a float string (O1) | PASS ("integer column seed has 1 non-integer cell(s)") | **accepted** |
| zip CSV row 1 `seed` +1 (O1) | PASS ("integer columns differ (exact)") | **accepted** |
| official / zip manifest is `null` or `[]` | PASS ("is not a JSON object"; 4 tests) | crash |
| official manifest `"environment": null` | PASS ("environment is not a JSON object") | crash |
| zip stub manifest is `[1]` | PASS ("zip stub … is not a JSON object") | crash |
| zip seed member with corrupted bytes (bad CRC) | PASS ("unreadable in rerun run (BadZipFile)") | crash |
| official / rerun source file missing | PASS ("source file … missing or unreadable"; 2 tests) | crash |
| *Audit of `018b513` (F1, NPZ integer vs float dtype). "018b513" column: v4 before this fix* | | *018b513* |
| official seed file: `seed` uint64 -> float64(seed + 1), a different integer (+1018) | PASS ("integer/non-integer dtype mismatch (rerun uint64, official float64)", the only problem) | **accepted** |
| zip seed file: `seed` -> float64(seed + 1) (opposite direction) | PASS ("... (rerun float64, official uint64)") | **accepted** apart from the zip pin |
| control: `seed_index` int64 -> uint64 and `prefix__selected_at_split` uint8 -> int64, same values, every official seed file | PASS (REPRODUCED, `problems: []`) | same |
| --selftest still passes | PASS ("selftest OK") | n/a |

Before review r001 of `f0aadce`, the two tolerance tests (and the NaN/inf, text-cell, column-swap and 0 -> 1e-14 tests)
tampered the uint64 `seed` column instead of a float column. The tolerance tests then passed only by accident on
pandas 3.0.6 and failed on pandas 3.1.0. They now tamper float columns, and integer columns have their own tests.

Not gated, on purpose: `zip_stub_model_matches_official`. It is false on the genuine data, because the zip's stub
manifest is documented as wrong in `b2a95dfbfbe3_REPRODUCTION.md` (line 50: N = 12, dt = 0.01, T_window = 1.0,
eta = 0.1). Only its presence and readability are gated. See the v4 section of the folder's ERRATUM.

### Settle threshold and swapped expected/actual: `test_rt_threshold_swap.py`

No existing checker recomputes the settle threshold R*, so this file adds an
independent check. It reads the `FROZEN_*` constants via `ast`, simulates the
engine's B update, and confirms R* ≈ 0.4543.

| Test | Result |
|---|---|
| control: true R* accepted | PASS |
| fabricated R* = 0.40 rejected | PASS |
| fabricated R* = 0.50 rejected | PASS |
| comparator `cmp_arrays` (still v3's helper): inf vs finite, both orders | PASS |
| NaN vs finite, both orders | PASS |
| over tolerance, both orders | PASS |
| shape mismatch, both orders | PASS |

(A false R* written into `registry/claims.csv` is still not recomputed by any repo
checker. The lint does reject it (`check_artifacts` in tools/ci/lint_claims.py) when the row claims a
Lean/formal proof without citing an existing `.lean` file.)

### Matched-phase anchor flag: `test_rt_matched_phase_anchor.py`

Added on branch `fix/errata-old-files-drift` (finding F4 of the old-files drift review). The
`row["anchor_pass"]` expression is read with `ast` from the hash-pinned script
`AIEF_1_4_matched_phase_memory_ablation.py` (line 1751). The script is not imported or run, and the
expression is evaluated on hand-built anchor rows. There are 5 tests (4 PASS including 2 controls,
1 GAP); the Results heading does not hard-code counts.

| Test | Result |
|---|---|
| control: 3 passing anchors accepted | PASS (accepted) |
| control: `verify_anchors=False` with a failed anchor | PASS (anchor_pass=True; catches a dropped or inverted `not verify_anchors`) |
| one of 3 anchors failed | PASS (anchor_pass=False) |
| only 2 of 3 anchors present | PASS (anchor_pass=False) |
| **GAP** seed with no anchor rows, `verify_anchors=True` | **GAP**: `... if seed_anchors else True` reports anchor_pass=True |

This does not affect the committed run: `test_output/` has 40 seeds, all `success`, each with 3 passing
anchors (120 rows in `frozen_anchor_validation.csv`). The flag would be wrong only for a seed that
fails before its anchor validation. Such a seed's `status` column already says `failed: ...`.

### Lean: `test_rt_lean.py`

The step-6 marker scan and the step-7 `#aief_axiom_audit` elab plus summary
parser are extracted from `lean/AIEFProofs/check_lean.sh`.

| Test | Layer | Result |
|---|---|---|
| control: clean file (comment/string false positives) | marker scan | PASS (accepted) |
| sorry / admit / user axiom / native_decide | marker scan | PASS (4 tests) |
| **GAP** hidden sorry via custom tactic calling `Lean.Elab.admitGoal` | marker scan | **GAP**: no marker word in source |
| **GAP** `@[simp] axiom` | marker scan | **GAP**: regex only matches `axiom` at line start |
| control: clean project | axiom audit | PASS (accepted) |
| sorry / user axiom / hidden admitGoal / `@[simp] axiom` / native_decide | axiom audit | PASS (5 tests, all DISALLOWED) |

The two marker-scan GAPs are **closed by the axiom audit** (step 7), which
works on the compiled environment. They only matter if step 7 is skipped or
broken.

## Fix notes

- **G1, branch `fix/manifest-nonempty`** (`tools/ci/check_manifest.py`). The verifier
  `AI Agent Audits/evidence/verify_manifest.py` is hash-pinned in its own `audit_manifest.json`,
  so the rule lives in the CI wrapper: for each verifier it runs, it also reads the sibling
  `audit_manifest.json` and fails if it is unreadable, if `files_sha256` lists nothing besides the
  verifier and the manifest, if a listed file is missing, or (inputs mode) if `inputs_sha256` is
  empty. The real audit manifest (145 files, 24 inputs) still passes; no other manifest in the repo
  is checked by `verify_manifest.py`.

- **G2, branch `fix/check-manifest-missing-verifier`** (`tools/ci/check_manifest.py`, combined here on
  `fix/check-manifest-g1g2`). A listed verifier that is missing is now an ERROR (exit 1), not a NOTICE
  and exit 0. The old `ran == 0` notice is dropped. The CI self-test stub verifier now also writes a
  minimal non-empty manifest, so the G1 coverage rule is satisfied.

- **G2b, branch `fix/check-manifest-g1g2`** (`tools/ci/check_manifest.py`; Researcher 001 audit of
  a428c32). Exit 0 from whatever file sits at the verifier path is no longer enough. Before running it,
  `check_verifier_file` requires a regular file at the listed path (a symlink, a directory, or anything
  resolving outside the repo is refused) whose sha256 equals its own `files_sha256` entry in
  `audit_manifest.json`. After it runs, `success_line` computes the exact summary the real verifier prints for that manifest
  (`checked N published files[ and K inputs][; P post-manifest logs listed but not hashed]`), which must
  appear as a whole line, and the last non-empty line must be exactly `OK`. The real tree still passes
  (145 files, 24 inputs). CI self-tests (`tools/ci/tests/test_check_manifest.py`) and the red-team
  `ManifestWrapper` tests assert exact output lines and the exact `== result:` line, not substrings.
  There was no G2b `@gap` test to flip; the new negative controls were added as normal tests, and each
  fails against the pre-fix check_manifest.py (f8eb5e8).

- **G2b follow-up, branch `fix/check-manifest-g1g2`** (Researcher 001 audit of 14072c3).
  - F1: the verifier ran as `python <path>`, so a hashlib.py / json.py / glob.py / pathlib.py beside it
    shadowed the standard library and could print the success line + OK over a tampered tree. It now runs
    as `python -I -B` (no script folder, cwd or PYTHON* variables on sys.path, no bytecode written), and
    an unlisted `*.py` file or a `__pycache__` folder beside it is an ERROR before anything runs.
  - F6: it runs from the exact bytes that were hashed (sent on stdin to a small `-c` bootstrap that
    execs them with `__file__` set to the verifier's path, so `Path(__file__).resolve().parent` still
    finds the manifest and the output is unchanged). Swapping the file after the hash has no effect.
  - F5: a symlink in any folder between the repo root and the verifier is an ERROR.
  - F4: an unreadable verifier is a named ERROR ("cannot be read"), not a traceback.
  - Duplicate JSON keys in audit_manifest.json are an ERROR (json's last-wins let a second verifier
    entry with a stub hash win).
  - F3: the last two non-empty lines must be the success line then `OK`, each printed exactly once,
    and no line on stdout or stderr may look like a problem report (MISSING / SIZE / SHA256 / UNLISTED /
    INPUT / FAILED, or "problem(s)").
  - F2 (correction): an earlier version of this note said audit_manifest.json is pinned in
    `registry/artifacts.csv`. It is not: that file has no `AI Agent Audits/` rows, and nothing in CI pins
    the manifest outside itself. So the residual, a stub whose new hash is written into the manifest and
    which prints the computed success line + OK, is **not caught in CI**. The success line is computed
    from the manifest, so it only stops lazy stubs. Only this red-team suite flags it (GAP G2c,
    `test_GAP_repinned_stub_printing_success_line_passes`), and this suite does not run in CI.
    **Owner item:** pin audit_manifest.json and verify_manifest.py outside the manifest, somewhere CI
    checks (for example expected sha256 values in check_manifest.py or rows in registry/artifacts.csv),
    and make this red-team suite a required CI check.
  - Each new CI self-test and red-team control fails against 14072c3, except the repo-root shadow
    control. That one guards the new `-c` launch, which puts cwd on sys.path unless `-I` is set, and it
    fails if `-I` is removed.

- **B1, branch `fix/check-manifest-g1g2`** (Researcher 001 audit of 92c5d77; `tools/ci/check_manifest.py`).
  The verifier was isolated, but the wrapper was not: CI runs `python tools/ci/check_manifest.py` without `-I`,
  so `tools/ci/` (the script folder) was `sys.path[0]` for the wrapper itself. A committed
  `tools/ci/hashlib.py` (or `json.py`, `subprocess.py`, `argparse.py`, `re.py`) that printed the PASS
  result line and otherwise proxied the real module, plus a tampered `AIEFS_audit.md` and a regenerated
  inventory, passed every CI check. The verifier, the manifest and check_manifest.py stayed untouched. PYTHONPATH
  worked the same way. This was the F1 mechanism one level up, and it existed on main too. It is **not** an
  accepted residual. Fix: before any shadowable import, check_manifest.py re-executes itself as
  `python -I -B <its own path>` when run as a script and not already isolated (`sys` is built in and `os` is
  loaded at interpreter start-up, so neither can be shadowed). Every invocation is then isolated, in CI and
  locally, with no workflow edit. CI self-tests run a copy of the real wrapper as a script from a temp repo's
  `tools/ci/` with each planted module (both modes) and with a PYTHONPATH shadow, and expect FAIL. A control
  expects the clean tree to PASS in both modes. With the re-exec disabled, those tests fail (11 failures).

- **G3 + G4, fixed** (`check_artifacts` / `resolve_artifact` in `tools/ci/lint_claims.py`). Every path-like
  `supporting_artifacts` entry must exist in the tree (trailing words, `:LINE` and `§section` are
  allowed; prose entries are skipped). A row that claims a formal/Lean proof (`evidence_scope`
  `Formalized theorem`, see Round 2, or a statement like "proved in Lean")
  must cite at least one existing `.lean` file. A registry row is not accepted as proof because
  `registry/artifacts.csv` marks `lean/AIEFProofs/README.md` and the CI YAML there as
  `Formalized theorem` too. Known missing citations are listed with a reason in
  `KNOWN_MISSING_ARTIFACTS` (empty today: its one entry, AUD-REPRO-B2A95 citing
  `compare_b2a95dfbfbe3_v3.log` (Auditor Seat 002 finding M1), was removed when ERRATA E14 restored that
  log at its E13 `SHA256SUMS` hash).
  The claims-lint fixture now mirrors the tree with symlinks so cited artifacts resolve.

- **Round 2 (Auditor Seat 002 follow-ups), fixed in the same functions.** `evidence_scope` must equal one of the
  values in the `### Axis 2 ... evidence_scope` table of `registry/README.md` (6 today; a missing
  table is an error), and only `Formalized theorem` counts as a formal scope (no more substring
  match, so "Informal ..." is not a proof claim). The proof wording also covers "Machine-checked in
  Lean 4" and "Lean 4 verifies". After the longest existing path prefix, the remaining words outside
  parentheses must not be path-like (no `/`, no file extension). KNOWN_MISSING_ARTIFACTS entries
  that are no longer cited, or whose file now exists, are errors. The allow-list tests inject a
  synthetic entry through a small driver, so they do not depend on the live entry. New GAP: the
  `.lean` file's content is not checked. `ClaimsLint` fails in `tearDownClass` if any test changed
  `git status` of the real checkout.
  Deleting or renaming a column these checks read (`statement`, `evidence_scope`,
  `supporting_artifacts`) is one `registry/claims.csv:1: required column '...' missing from the header;
  ... NOT checked` ERROR (`missing_column()`, the same helper and wording as the G6b status-column error) (exit 1, also without --strict), so it cannot switch the checks off (same class
  as G6b). The CI self-test fixtures carry both columns and an Axis 2 table, and empty
  KNOWN_MISSING_ARTIFACTS for their synthetic repos, so these checks always run there too.

- **New check, branch `ci/check-sha256sums`** (`tools/ci/check_sha256sums.py`, job `sha256sums`
  in `.github/workflows/repo-checks.yml`). Verifies every `SHA256SUMS` / `*SHA256SUMS*.txt` file
  (historical: 5 lists, 49 entries when first written; 7 lists, 61 entries since the main refresh, see
  the SHA256SUMS table above). Fail-closed. At first the only accepted failure was an allow-listed missing
  `audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v3.log` (Auditor Seat 002 finding M1); that
  exception was retired in the main refresh (18e542c) after ERRATA E14 restored the log at its listed
  hash, so `ALLOWED_MISSING` is empty today. The allow-list mechanism (an entry becomes an error if the
  file reappears or the line is removed) stays, tested with synthetic entries. `audits/reproductions/.gitignore`
  re-includes `*.log` there (the root `.gitignore` is pinned as ART-0001 by `check_artifact_pins.py`).

- **Round 2 (Auditor Seat 002 follow-ups), branch `ci/check-sha256sums`.** Files are found with
  `git ls-files` (tracked files only; the run fails if the path is not the top of a git checkout).
  Checked: the `SHA256SUMS` name pattern plus `lean/AIEFProofs/AIEF_LEAN_PROJECT_LOCK_HASHES.txt`
  (historical: 6 files, 51 entries at that round; 7 lists, 61 entries today). Excluded with a reason, printed as SKIP:
  `AI Agent Audits/evidence/logs/lean_r4/source_sha256.txt` (historical lean_r4 log; ERRATA E7) and
  the two `twindow_*hashes*.txt` records (absolute `/home/deck` paths). Any other tracked
  `*sha256*/*sums*/*hashes*` list that is neither checked nor excluded is an error, as is a stale
  exclusion. Each listed path must stay inside the repo both lexically and after `realpath`, so an
  in-repo symlink pointing outside is rejected. The red-team tests inject a synthetic allow-list
  entry instead of relying on the live b2a95 entry, never write into the real checkout (every write
  goes through materialize + unlink), and fail in `tearDownClass` if `git status` of the real
  checkout changed. The inventory now includes the 3 rows that were missing.

- **S-B1, branch `ci/check-sha256sums`** (Researcher 001 audit of 18e542c; `tools/ci/check_sha256sums.py`).
  Same class as B1 above, not the accepted start-up-hook residual N1. CI runs
  `python tools/ci/check_sha256sums.py` without `-I`, and the checker imported `hashlib` / `argparse` / `re` /
  `subprocess` before any isolation, so `tools/ci/` was `sys.path[0]`. A committed `tools/ci/hashlib.py` that
  proxied the real module and returned the listed digest for a tampered `tools/sync/download_new.sh` made the
  real tree print `7 SHA256SUMS file(s), 61 entries verified, 0 allow-listed, 0 error(s) -> PASS`, exit 0
  (reproduced independently by Auditor Seat 002 on Python 3.12.16 and 3.13.5; the same plant FAILs with
  MISMATCH under `python -I -B`). A sibling module that just prints the PASS line and exits 0 worked too.
  Fix: the same self re-exec as check_manifest.py, placed before every other import: run as a script and not
  already isolated, the checker re-executes itself as `python -I -B <its own path>`. CI self-tests
  (`tools/ci/tests/test_check_sha256sums.py`) run a copy of the real checker as a script from a synthetic
  git repo's `tools/ci/` with a tampered listed file and expect MISMATCH + FAIL for the digest-proxy hashlib,
  for forging hashlib/argparse/re/subprocess plants and for a PYTHONPATH hashlib; controls expect the clean
  tree to PASS both as a plain script and under `-I -B`, and the tampered tree to FAIL with no plant. With the
  re-exec disabled, the shadow tests fail (6 failures; 7 with the block removed, counting the structural test).
