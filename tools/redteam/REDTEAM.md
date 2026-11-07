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

About 70 s total (the comparator file is about 35 s; the Lean file is about 20 s
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
| **GAP** PASSED manifest listing only the verifier, no data | verify_manifest | **GAP**: verifies OK; nothing requires the manifest to cover any data |
| wrapper propagates verifier failure | tools/ci/check_manifest.py | PASS |
| **GAP** verifier deleted | check_manifest.py (line 79: `if not os.path.isfile(...)` → `NOTICE ... not found; skipped`) | **GAP**: prints NOTICE and exits 0 (not fixed in this commit; Researcher 001 also reports G2b: a stub verifier passes) |

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

Target: `audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v3.py`
(hash-pinned, run unmodified) on a temp copy of `runs/5a9f093a2fe0`.

| Test | Result |
|---|---|
| control: untampered copy | PASS (REPRODUCED) |
| CSV cell +1e-9 | PASS (NOT REPRODUCED) |
| CSV cell +1e-11 (just over TOL 1e-12) | PASS |
| CSV NaN / +inf / -inf | PASS (3 tests) |
| branch diagnostics +inf | PASS |
| seed NaN | PASS |
| seed value +1e-6 | PASS |
| seed bytes truncated | PASS (fail-closed crash, rc≠0, no REPRODUCED) |
| seed deleted | PASS (fail-closed crash, rc≠0, no REPRODUCED) |
| extra fabricated seed file | PASS |
| seed integer field changed | PASS |
| two numeric columns swapped | PASS |
| manifest model eta changed | PASS |
| --selftest still passes | PASS |
| **GAP** branch labels swapped in CSV text column | **GAP**: `out["csv_nonnumeric_equal"]` is computed but is not part of the `ok = (...)` verdict expression (v3) |
| **GAP** manifest "schema" field changed | **GAP**: schema is not part of the verdict |

### Settle threshold and swapped expected/actual: `test_rt_threshold_swap.py`

No existing checker recomputes the settle threshold R*, so this file adds an
independent check. It reads the `FROZEN_*` constants via `ast`, simulates the
engine's B update, and confirms R* ≈ 0.4543.

| Test | Result |
|---|---|
| control: true R* accepted | PASS |
| fabricated R* = 0.40 rejected | PASS |
| fabricated R* = 0.50 rejected | PASS |
| comparator `cmp_arrays`: inf vs finite, both orders | PASS |
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
expression is evaluated on hand-built anchor rows. The header count above does not include these
5 tests (4 PASS including 2 controls, 1 GAP); it was left as is to avoid merge conflicts with
parallel branches.

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

- **G3 + G4, fixed** (`check_artifacts` / `resolve_artifact` in `tools/ci/lint_claims.py`). Every path-like
  `supporting_artifacts` entry must exist in the tree (trailing words, `:LINE` and `§section` are
  allowed; prose entries are skipped). A row that claims a formal/Lean proof (`evidence_scope`
  `Formalized theorem`, see Round 2, or a statement like "proved in Lean")
  must cite at least one existing `.lean` file. A registry row is not accepted as proof because
  `registry/artifacts.csv` marks `lean/AIEFProofs/README.md` and the CI YAML there as
  `Formalized theorem` too. Known missing citations are listed with a reason in
  `KNOWN_MISSING_ARTIFACTS` (one entry today: AUD-REPRO-B2A95 cites
  `compare_b2a95dfbfbe3_v3.log`, which was never committed; Auditor Seat 002 finding M1).
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
