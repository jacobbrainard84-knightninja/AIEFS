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

## Results (115 tests: 104 PASS incl. 12 controls, 11 GAP)

Run on base `395ea53` (main), plus fix #1 (comparator v4, branch `fix/comparator-v4-gates`, including the
review r001 additions: 16 comparator tests, and the review r001 of `f0aadce` additions: 15 more). The comparator and
threshold files pass on pandas 3.0.6 and on pandas 3.1.0 (the `requirements.txt` pin).
The original run (74 tests: 61 PASS, 13 GAP) predates fix #1.

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
| **GAP** PASSED manifest listing only the verifier, no data | verify_manifest | **GAP**: verifies OK; nothing requires the manifest to cover any data |
| wrapper propagates verifier failure | tools/ci/check_manifest.py | PASS |
| **GAP** verifier deleted | check_manifest.py (line 41) | **GAP**: prints NOTICE and exits 0 |

### Claims lint and hygiene: `test_rt_claims_hygiene.py`

| Test | Checker | Result |
|---|---|---|
| control: copy passes | lint_claims.py | PASS (accepted) |
| status "Proved" (outside vocabulary) | lint_claims | PASS |
| status with trailing space | lint_claims | PASS |
| status wrong case | lint_claims | PASS |
| duplicate claim_id | lint_claims | PASS |
| empty claim_id | lint_claims | PASS |
| vocabulary missing, --strict | lint_claims | PASS |
| **GAP** row cites nonexistent artifacts | lint_claims | **GAP**: artifact column never resolved |
| **GAP** false claim "R* = 0.40, proved in Lean" as Supported/Formal proof | lint_claims | **GAP**: content is not checked against anything |
| **GAP** claims.csv missing | lint_claims | **GAP**: exit 0 |
| **GAP** vocabulary heading removed | lint_claims (non-strict, as CI runs it) | **GAP**: checks skipped, exit 0 |
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

(A false R* written into `registry/claims.csv` is *not* caught by any repo
checker; that is the lint GAP above.)

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
