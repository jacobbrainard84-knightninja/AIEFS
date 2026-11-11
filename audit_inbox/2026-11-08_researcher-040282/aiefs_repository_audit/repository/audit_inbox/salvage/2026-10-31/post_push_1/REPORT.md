# work/post-push-1: report (local only; nothing pushed, no GitHub access used)

Worktree: `/workspace/AIEFS_merge_prep`. Branch `work/post-push-1`, based on `7fdf9ed` (origin `merge-prep/arena-reconciled`).
HEAD = `f51c6d04347c23b7dab1f4c539ed873523dc58bd`. Commit identity: `Researcher 001 (local)` / `researcher001@localhost.invalid`.

## Commits (oldest first)

| commit | content |
|---|---|
| `1ebe0b4` | (b) Analysis v4.1 candidate (unaudited) + `tests/test_v4_1_held_event.py` |
| `228b95c` | (c1) `tools/ci/check_modes.py` (100755) + `tools/ci/tests/test_check_modes.py` + `file-modes` job in `.github/workflows/repo-checks.yml` |
| `b3c6648` | (c1) `== result` summary line for check_modes; command listed in `docs/REVIEWING.md` |
| `8f4f9d5` | (c2) 7 ledger rows, added through `registry/reconciliation/build_claims_reconciliation.py` (NEW list) + regenerated `registry/claims.csv` |
| `7ae5137` | (c2) `ERRATA_2026-10-28.md` E8 (response-1 uniform overstatement) |
| `f51c6d0` | (c2) `CURRENT_STATUS.md` + `registry/README.md`: 75 rows, new items, open-question table |

## Files

New: `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py`,
`AIEF_Experiments/aief_modular_platform_v1_analysis_v4/tests/test_v4_1_held_event.py`, `tools/ci/check_modes.py`,
`tools/ci/tests/test_check_modes.py`.
Edited (all checked first: none of them is pinned by path or hash in `registry/artifacts.csv` or `AI Agent Audits/evidence/audit_manifest.json`):
`.github/workflows/repo-checks.yml`, `docs/REVIEWING.md`, `registry/reconciliation/build_claims_reconciliation.py`,
`registry/claims.csv`, `ERRATA_2026-10-28.md`, `CURRENT_STATUS.md`, `registry/README.md`.
v4 (`AIEF_1_4_Twindow_sensitivity_analysis_v4.py`, ART-0063) is byte-identical: sha256 `d05a32a4…7084a74`, the same as the pin.
`AIEFS_audit_response.md` is not edited.

## (b) v4.1: tolerance choice and justification

- End check: `searchsorted(times, times[i] + duration - tol, side="left")` with `tol = 1e-6 × min positive diff(times)`
  (`HOLD_TOLERANCE_FRACTION = 1e-6`, `_hold_tolerance`).
- Why this value: the rounding error of `times[i] + duration` is about 1e-13 for these magnitudes, about 7 orders of magnitude
  below tol. tol is 6 orders of magnitude below one grid step, so a hold that is one step short is still rejected (the tests check this).
  Tying tol to the grid step keeps it scale-free. The T_window-nominal holds (17.5029 × rho) are not grid multiples, so they behave as in v4.
- Estimands: `held_retention` (condition true from index 0 for the full window, with no drop), `held_recovery` (the earliest held
  start after the first False sample), and `held` (tolerant generic, same meaning as v4's). `classify_held_event` → retention / recovery / none
  (retention takes precedence), written as the `held_classification` column. Expected row counts change: 19200 events, 11520 DID, 2400/1440 summaries.
- Header: "CANDIDATE, UNAUDITED. DO NOT RUN ON REAL TRAJECTORIES". `main()` returns 2 unless `--allow-unaudited-candidate` is given.
  It was not run on any real trajectory, and nothing was regenerated.

### Did the constructed case reproduce v4's miss? Yes.
The test copies v4's exact expression and asserts a miss on `np.arange(0, 40, dt)` for dt = 0.01, 0.05, 0.1, and on v4's own
`EXPECTED_SAMPLE_TIMES` (spacing 0.5). On the saved grid, 32 of the 605 valid start positions (corrected from 32/604 after audit N1; the last valid start is now included) held exactly 17.5 are missed. The first is
t = 16.01 → 33.51, where v4 effectively requires 18.0. An `np.arange` grid with dt = 0.5 shows no miss, so the bug depends on the grid.

## (c1) check_modes.py
It reads modes from `git ls-files -s`, detects a shebang through `git cat-file --batch`, uses the known list (`check_lean.sh`, `tools/sync/download_new.sh`,
`tools/sync/tests/run_tests.sh`, `tools/sync/untrack_artifacts.sh`) plus the paths in the "Executable bits" item of PUSH_NOTES.md.
Output: `WARNING KNOWN_NOT_EXEC` (one `::warning` annotation per file under GITHUB_ACTIONS) and `SHEBANG_NOT_EXEC` (one summary annotation).
It always exits 0 (`--strict` → 1; a git error → 2). Current tree: 8 known scripts plus 117 other shebang files are not 100755 (125 warnings), PASS.

## (c2) Ledger rows (68 → 75)
`AUD-V4-HELDEVENT`, `AUD-V4-RECOVERY-WORDING`, `AUD-MODULAR-ORACLE`: findings, audited_status *Finite numerical observation* (not audited).
`AUD-TIMESTEP`, `AUD-B-SCAFFOLD`: **open items**, `Incomplete` / `Conjecture` / *Not established*, explicitly not findings against existing claims.
`AUD-CORR-0995-SCOPE`: Supported (audit evidence). It gives first-pass 0.711/0.712 and 0.588/0.634, and replication 0.745/0.747 (medians 0.978/0.987) and
0.553/0.531 (37/39 of 60). It cites `delay_heldout_analysis.json`, `frozen_topology_check.json` and the side-branch scope note.
`AUD-RESP1-UNIFORM`: Supported (the audit's own numbers). Erratum E8: uniform no_delay AUC 0.850 vs 0.883, log loss 0.240 vs 0.396.
The rows are in the build script's NEW list, so a re-run does not drop them. The script writes CRLF; the output was converted back to LF to match
the branch. After that, `lineage_reconciliation.csv` was unchanged and the claims.csv diff is the 7 added lines only.

## Test / check results (logs in `/workspace/post_push_1/logs/`)
- `lint_claims.py`: 75 rows, 0 violations, PASS
- `hygiene_scan.py`: 0 errors, 3 warnings (pre-existing BIG_FILE > 50 MiB), PASS. `--base 7fdf9ed --pii`: 0/0, PASS
- `check_manifest.py`: 1 verifier, 0 failed, PASS
- `check_modes.py`: 0 errors, 125 warnings, PASS (exit 0)
- `unittest discover -s tools/ci/tests`: 24 tests OK; `pytest tools/ci/tests`: 24 passed
- `pytest tests/test_v4_1_held_event.py tests_modular/test_analysis_v4.py`: 19 passed (13 + 6), 2 Pandas4Warning (`verify_integrity`, inherited from v4)

## Not done / concerns
1. The v4.1 summary-table counts (2400/1440) through the full `run_analysis` path were not checked on real data, by design. Only a synthetic
   `compute_recovery` cohort (19200 / 11520) was checked. Whether any saved v4 held row changes is unknown until v4.1 is audited and run.
2. Line endings: the build script emits CRLF and the branch stores LF, so the output was normalized by hand. Whoever re-runs the script must do the same,
   or the script should be changed to write LF.
3. 117 non-known shebang files are not executable, which gives noisy warnings. v4 and v4.1 themselves are 100644 with a shebang.
4. `check_modes.py` is committed as 100755. If the upload path drops modes, PUSH_NOTES.md should list it.
5. The side-branch Corr scope note (`fix/corr-0995-scope`; v2 text is on a local-only branch at `6cb00ea`) edits `AI_AGENT_HANDOFF_PROMPT.md` and
   `AIEF_HISTORIC_UNFOLDING.md`, which are hash-pinned (ART-0103/ART-0101). That conflicts with the "never edit pinned files" rule and needs an owner decision.
6. The commit 487d5a9 is not an ancestor of 7fdf9ed. It was not used.
7. `CURRENT_STATUS.md`: three open-question rows had been stranded after the formal-math bullets, as a table with no header. They were moved back into the table.

---

## Follow-up (2026-10-28 evening, America/Toronto): E9 pointer + CRLF

New commits on top of f51c6d0. Nothing was rewritten and nothing was pushed. HEAD was 180bd03 at the time; see the audit-fix section at the end for the current HEAD and the superseded statements below.

| commit | change |
|---|---|
| 3187ada | ERRATA_2026-10-28.md **E9** and a one-line pointer in CURRENT_STATUS.md |
| 0b96ba8 | build script plus regenerated claims.csv: the AUD-CORR-0995-SCOPE caveat/note now says the inline side branch fix/corr-0995-scope (and v2) is not being merged (option A) and that E9 is the record |
| 7c1e079 | `registry/reconciliation/build_claims_reconciliation.py` writes LF (`lineterminator="\n"`, `newline=""`), with a docstring note |
| 180bd03 | `audits/engineering/validate_registry_against_tree.py --write` also writes LF (it was `"\r\n"`) |

### E9 (part 1)
- E9 cites `AIEF_HISTORIC_UNFOLDING.md:166` and `AI_AGENT_HANDOFF_PROMPT.md:113` (`Corr_physical ~0.995`).
- It says these lines are scoped by AUD-CORR-0995-SCOPE, and quotes verbatim the scope note from /workspace/corr_0995_fix/AUDIT_v2.md section D.
- It explains why the files stay untouched: ART-0101 and ART-0103 in artifacts.csv, plus the HANDOFF prompt's pin in `AI Agent Audits/evidence/audit_manifest.json` inputs_sha256.
- `git diff 7fdf9ed HEAD` is empty for both docs and for `AI Agent Audits/`.

### CRLF inventory (`git ls-files --eol`, work/post-push-1, at 180bd03; superseded, see the end of this report)
- **Counts:**
  - i/lf: 908
  - i/crlf: 18
  - i/-text (binary): 2044
  - i/none: 3 (empty/no-newline JSON)
  - i/mixed: 0
- **All 18 i/crlf files are hash-pinned.** Each has a sha256 in registry/artifacts.csv, and all but one are also pinned in a manifest:
  - `AIEF_1_4_superseded_claims.csv`: AIEF_1_4_lineage_freeze_manifest.json
  - `Older files/87dfe5798954/AIEF_1_3_87dfe5798954_scalar_summary.csv`: paired_seed_analysis/analysis_manifest.json
  - `runs/{0ddf42b3e20a,123b2cadbb0d,2e2843f5e26c,46fb82c784ef,5a338105785a,87dfe5798954,92dd4ddbdba1,9fb83552f0ce,a3dcc58f4939,fccebfc14855}/AIEF_1_3_*_scalar_summary.csv` (10): paired_seed_analysis/analysis_manifest.json
  - `runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv`: several analysis manifests and twindow_frozen_authority_hashes.txt
  - `runs/73dca37cf93f/…` and `runs/c3da1ac707bf/…` scalar summaries (2): aief_1_3_disjoint_100seed_analysis_manifest.json
  - `runs/b57562a8ee77/AIEF_1_4_Twindow_sensitivity_b57562a8ee77_scalar_summary.csv`: twindow_v4_analysis_manifest.json, runs/b57562a8ee77/analysis/analysis_manifest.json, runs/b57562a8ee77/manifest.json
  - `runs_aief14_smoke/ae136b3a165b/AIEF_1_4_ae136b3a165b_scalar_summary.csv`: artifacts.csv only
  - `runs_pivot_study/ebfec9a5c419/AIEF_1_4_Twindow_sensitivity_ebfec9a5c419_scalar_summary.csv`: runs_pivot_study/ebfec9a5c419/manifest.json
- **The 11 CSVs the upload converted to LF.** These are the EOL-only diffs between local `merge-prep/arena-reconciled` and the remote:
  - audits/engineering/python_path_dependencies.csv
  - audits/github_reconciliation/{runs_cohort_reconciliation,zip_vs_tree_comparison}.csv
  - registry/{artifacts,claims,lineage_reconciliation,relocation_map,studies,supersessions}.csv
  - the two pinned files `…/zip_only_files/AIEF_1_4_CONTROLLER_FIBER_CLAIM_REGISTRY.csv` (ART-2835) and `…/zip_only_files/AIEF_1_4_analysis_lineage.csv` (ART-2845, also in AIEF_1_4_lineage_freeze_manifest.json)
- **Which branch keeps the original CRLF bytes (correction to the brief):**
  - It is the local branch **merge-prep/arena-reconciled** that keeps them:
    - CONTROLLER_FIBER_CLAIM_REGISTRY: sha 2fb5517d…, 13 CR lines. This matches ART-2835.
    - analysis_lineage: sha a633819d…, 33 CR lines. This matches ART-2845.
  - **work/post-push-1 is based on the remote 7fdf9ed and inherited the LF versions.** Their shas are 4fd11fc9… and 00df78c8…, so on this branch both files **do not match their pins**.
  - I did not change them. Two options for the owner/auditor:
    - restore them with `git checkout merge-prep/arena-reconciled -- <2 paths>` in a separate commit. This restores the exact pinned bytes and doesn't change content. Pair it with a narrow `.gitattributes` marking those paths `-text`.
    - leave them and record the mismatch.
  - `check_manifest` still passes, because it only verifies audit_manifest.json. It does not check artifacts.csv or the lineage freeze manifest.

### CRLF fix (part 2b)
- **build_claims_reconciliation.py:**
  - Its outputs are registry/claims.csv and registry/lineage_reconciliation.csv. Neither is hash-pinned: their shas are not in any tracked file.
  - Its only pinned file is the input LINEAGE_IN, which it reads and never writes.
  - I switched it to LF and re-ran it with no manual CR stripping. Both outputs are **byte-identical** to the committed files:
    - claims.csv: 7098d0eb…, 75 rows
    - lineage_reconciliation.csv: 745d478b…, 32 rows
    - 0 CR in either; `git status` clean.
- **validate_registry_against_tree.py --write:** had the same `"\r\n"` writer for registry/artifacts.csv and relocation_map.csv. Neither file is hash-pinned, and the script itself is not pinned.
  - I switched it to LF and ran `--write` in a throwaway detached worktree, now removed.
  - artifacts.csv came out byte-identical.
  - relocation_map.csv differed by one line, and only in content. The `aief_modular_platform_v1_analysis_v4` row flag changed from PRESENT_SAME_COUNT to PRESENT_COUNT_CHANGED ("files now 41; registry 39") because of the v4.1 files added in 1ebe0b4.
  - That refresh is **not** committed; it is left for the owner.
- **No .gitattributes added (at 180bd03; superseded: a60b0d9 added one, see below).** core.autocrlf is unset and there is no attributes file, so git doesn't convert anything, and all 18 CRLF files stay as they are. A `-text` list is only needed if someone turns on eol normalization. If one is wanted, it should list only the 18 paths (plus the 2 zip_only files if restored) as `-text`, with no `* text=auto`.

### Checks re-run at 180bd03 (logs: /workspace/post_push_1/logs2/)
- lint_claims: 0/0/0, PASS
- hygiene_scan: 0 errors, 3 warnings (pre-existing BIG_FILE), PASS
- `hygiene_scan --base 7fdf9ed --pii`: 0/0, PASS
- check_manifest: 1 verifier, 0 failed (145 published + 24 inputs OK), PASS
- check_modes: 0 errors, 125 warnings, PASS
- `unittest discover -s tools/ci/tests`: 24 OK
- `pytest tools/ci/tests`: 24 passed
- v4 dir `pytest tests/test_v4_1_held_event.py tests_modular/test_analysis_v4.py`: 19 passed, 2 inherited Pandas4Warnings
- v4 script sha256 is still d05a32a4…

## Audit fixes (Auditor Seat 002 review of a60b0d9): R1-R4 and N1-N6

New commits on top of a60b0d9, local only. Nothing was rewritten and nothing was pushed, and no GitHub access was used. **HEAD is 0493f26** and the worktree is clean. No hash-pinned file was edited: none of the 10 changed paths has a row in registry/artifacts.csv, and none of their a60b0d9 sha256 values appears in any tracked file.

| commit | item | change |
|---|---|---|
| fd08957 | R1 | ERRATA E8: on clustered omega the model is worse on AUC only (0.46-0.47 vs 0.65-0.73); log-loss differences are at most 0.02 (baseline past R 0.304 vs dOmega 0.319; no_delay 0.286 vs 0.279). This matches E9. No number changed. |
| b8a3709 | R2-R4 | Edits are in the NEW list of build_claims_reconciliation.py, and claims.csv was regenerated by re-running it, not hand-edited (75 rows, 0 CR). R2 AUD-CORR-0995-SCOPE: median 0.986 (the JSON has 0.98649). Cites omega_random.log, omega_random.json and AIEFS_salvage.md s3.1. First-pass means are over defined runs only: 15/20 no_delay, 30/40 baseline. R3 AUD-MODULAR-ORACLE: the default run gives 40 passed, 2 skipped. AIEF_RUN_SLOW_TESTS=1 plus the repo root on PYTHONPATH gives 41 passed, 1 skipped (pytest.ini already sets pythonpath = .). Either condition alone still gives 40/2. R4 AUD-V4-HELDEVENT: 32 of 605 starts; the blocker is scoped to the fixed_physical_17p5 held rows, and T_window-nominal holds and non-held estimands are not affected. |
| 0bd4552 | R3/R4 | CURRENT_STATUS.md: the same test counts and conditions, and the same blocker scope. |
| cb2e853 | N1 | test_v4_1_held_event.py: the start range now includes the last valid start, `range(0, len(times) - k)`. It asserts 605 starts, 32 v4 misses, and that the last start ends at the final sample and is held by v4. |
| b4870f2 | N6 | v4.1 docstrings: `tol = HOLD_TOLERANCE_FRACTION * h_min = 1e-6 x the smallest positive saved-grid step` (0.5e-6 on the saved grid). The docstrings state that this is **not** dt/2 and does **not** use integer steps. Estimands are `held` / `held_retention` / `held_recovery`, with `held_classification` = retention / recovery / none. No new estimand was added; "time to first loss" is noted as a possible future addition. |
| f342557 | N2 | check_modes --strict: KNOWN_NOT_EXEC is printed and annotated as an error, and the result line explains why the run fails. A cat-file failure exits 2. There are 3 new or extended tests. |
| 028a9d4 | N4 | `validate_registry_against_tree.py --write` refresh. The only diff is relocation_map.csv row aief_modular_platform_v1_analysis_v4, which is now PRESENT_COUNT_CHANGED (files now 41; registry 39). artifacts.csv is byte-identical. |
| 0493f26 | N3 | PUSH_NOTES item 4 gets a note that the 2 pinned zip_only CSVs were restored to CRLF at a60b0d9 and marked `-text`. |

### Line endings at 0493f26 (current)
- `git ls-files --eol`: i/lf 907, **i/crlf 20**, i/-text 2044, i/none 3, i/mixed 0.
- **All 20 CRLF files are hash-pinned and match their pins.** That is the 18 listed above plus ART-2835 (2fb5517d...) and ART-2845 (a633819d...), restored at a60b0d9.
- `.gitattributes` (from a60b0d9) marks exactly those 2 zip_only paths `-text`. It has no `text=auto` and no other rules.
- Artifact pin sweep (the auditor's check_artifacts.py logic, run read-only against this worktree): 2701 worktree rows SAME / PRESENT_SAME_SHA; 138 zip-member rows SAME; 52 MISSING_DELETED_ON_MAIN. There are 7 CHANGED rows, and every one is already flagged PRESENT_CHANGED_SHA: ART-0001, 0712, 0743, 0744, 0745, 0746, 0748. **No row that claims an unchanged SHA differs.**

### Checks re-run at 0493f26 (logs: /workspace/post_push_1/logs3/)
- lint_claims: 0/0/0, PASS
- hygiene_scan: 0 errors, 3 pre-existing BIG_FILE warnings, PASS
- `hygiene_scan --base 7fdf9ed --pii`: 0/0, PASS
- check_manifest: 1 verifier, 0 failed, PASS. Running verify_manifest.py directly also gives OK.
- check_modes (default): 0 errors, 125 warnings, PASS
- `check_modes --strict`: rc=1, 8 errors, 117 warnings (8 known-list scripts are not 100755). This is the expected strict result and is not enabled in CI.
- validate_registry_against_tree.py (read-only): rc=0, no tree changes.
- `unittest discover -s tools/ci/tests`: 27 OK. `pytest tools/ci/tests`: 27 passed.
- v4 dir `pytest tests/test_v4_1_held_event.py tests_modular/test_analysis_v4.py`: 19 passed, with 2 inherited Pandas4Warnings.
- Modular platform pytest: the default run gives 40 passed, 2 skipped. With AIEF_RUN_SLOW_TESTS=1 and the repo root on PYTHONPATH it gives 41 passed, 1 skipped.
- build_claims_reconciliation.py re-run: outputs are byte-identical and `git status` is clean.
- The v4 script sha256 is still d05a32a4...

## Post-push follow-ups (not implemented)
- **Artifact-pin CI check.** Extend `tools/ci/check_manifest.py`, or add a sibling check, so CI verifies the registry/artifacts.csv sha256 pins for worktree rows and zip-member rows. Today check_manifest only verifies `AI Agent Audits/evidence/audit_manifest.json`. The check should **fail only on pinned rows whose status claims an unchanged SHA** (PRESENT_SAME_SHA, ZIP_MEMBER_PRESENT). Rows already flagged PRESENT_CHANGED_SHA should be reported, not failed. That covers ART-0744 and ART-0746, plus ART-0001, 0712, 0743, 0745 and 0748. MISSING_DELETED_ON_MAIN rows should only be reported. On today's tree such a check would pass (see the sweep above). Not implemented, as requested.
- Possible future estimand for v4.1: "time to first loss". This is noted only; it is not part of the candidate.

