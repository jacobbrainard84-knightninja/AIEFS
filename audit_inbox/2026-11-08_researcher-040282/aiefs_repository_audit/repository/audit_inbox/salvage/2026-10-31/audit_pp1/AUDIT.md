# Independent audit: work/post-push-1 @ a60b0d9

Auditor: independent read-only audit. Written 2026-10-28 ~20:45 EDT (America/Toronto).
Repo: jacobbrainard84-knightninja/AIEFS. Branch `work/post-push-1`, HEAD **a60b0d9**. That is 11 commits on remote
`merge-prep/arena-reconciled` 7fdf9ed and 5 commits on f51c6d0.
All runs were done in my own clone, `/workspace/audit_pp1/repo`. Researcher 001's worktree was not modified.
Nothing was pushed and nothing was written to GitHub. Logs are in `/workspace/audit_pp1/logs/` (logs for a60b0d9 are in `logs/a60/`).
This report contains no tokens and no PII values.

## Verdict: **REQUIRED FIXES** (documentation/ledger only; no code or pin blockers)

- The code, pins, CI and line endings are in order at a60b0d9.
- Four ledger/errata wording or number errors must be fixed before merge. See R1–R4 below.
- `registry/claims.csv` is generated, so fix R2–R4 in the `NEW` list of `registry/reconciliation/build_claims_reconciliation.py` and re-run the script.

### Required fixes
| # | Where | Problem | Evidence | Fix |
|---|---|---|---|---|
| R1 | ERRATA_2026-10-28.md E8, corrected wording (line ~149) | "For clustered ω it does worse" is overstated. It repeats AUDIT_v2 S4d. It now **contradicts E9 in the same file**, which says "no better than chance … log-loss differences of at most 0.02". | delay_heldout_analysis.json point2_heldout, clustered_baseline: past R log loss 0.30402 is *better* than Δω-only 0.31910. The AUCs are 0.457 vs 0.652 (no_delay: 0.473 vs 0.725; log loss 0.28590 vs 0.27878). | Use E9's wording: "For clustered ω it discriminated worse on AUC (0.46–0.47 vs 0.65–0.73), with log-loss differences of at most 0.02." |
| R2 | claims.csv AUD-CORR-0995-SCOPE | The uniform no_delay median is given as **0.987**. | JSON per-run pearson_P_Rpast for uniform_no_delay has median 0.98649, which rounds to **0.986**. The other three medians (0.978, 0.449, 0.379) are correct. | Change 0.987 to 0.986. Recommended: cite `logs/omega_random.log` / `AIEFS_salvage.md` §3.1 as the source of the first-pass 0.711/0.712/0.588/0.634 (they are not in supporting_artifacts), and say that the first-pass clustered means cover only defined runs (15/20, 30/40). |
| R3 | claims.csv AUD-MODULAR-ORACLE | (a) "The default re-run (41 passed, 1 skipped)" is wrong. (b) "the test suite imports only when PYTHONPATH includes both the repository root and the platform directory" is overstated. | Re-run at a60b0d9 (`pytest -q` in the platform dir): **40 passed, 2 skipped**. 41/1 needs AIEF_RUN_SLOW_TESTS=1 plus the repo root on PYTHONPATH. pytest.ini sets `pythonpath = .`, so the suite imports without that. The repo root only enables the slow engine test, which is otherwise skipped silently. | Say "default run: 40 passed, 2 skipped". Reword the PYTHONPATH clause to "the slow engine-comparison test needs AIEF_RUN_SLOW_TESTS=1 and the repo root on PYTHONPATH". |
| R4 | claims.csv AUD-V4-HELDEVENT (+ CURRENT_STATUS / report wording if repeated) | (a) "32 of 604 start positions" has the wrong denominator. (b) "Blocker for citing v4 held-event estimands" is broader than the defect. | The saved grid (spacing 0.5) has **605** valid starts. 604 comes from the test helper `range(0, len-k-1)`, which drops the last valid start. I reproduced 32 misses; the last start is held correctly, so the count stays 32. The defect affects only exact-boundary held rows (fixed_physical_17p5 held events). | Use "32 of 605". Scope the blocker to v4 held-event rows at exact-duration boundaries (fixed_physical_17p5). Optional: extend the test range to include the last start. |

## Checks on the 5 new commits (f51c6d0..a60b0d9)

### E9 (3187ada) — PASS
- The E9 quoted paragraph is **byte-identical** to the `> Scope note (audit correction, revised 2026-10-28): …` paragraph in `/workspace/corr_0995_fix/AUDIT_v2.md` section D: one line, 2167 chars, string equality True.
- The cited lines are correct: `AIEF_HISTORIC_UNFOLDING.md:166` and `AI_AGENT_HANDOFF_PROMPT.md:113` both contain `Corr_physical ~0.995`.
- The pin explanation is correct:
  - ART-0101 = HISTORIC_UNFOLDING (6a011762…)
  - ART-0103 = HANDOFF prompt (5c24dbdf…)
  - The HANDOFF prompt is also in audit_manifest.json `inputs_sha256`.
  - Both files match their pins at HEAD.
  - `git diff 7fdf9ed HEAD` is empty for both files and for `AI Agent Audits/`.
- I spot-checked the section-D numbers against the JSON:
  - repo-ω held-out AUC: 0.99999 vs 0.972 ✓
  - repo-ω delay-off Δω AUC: 1.0 ✓
  - n = 6600 = 100 runs × 66 edges ✓
  - uniform AUC/log loss: 0.84/0.83, 0.85/0.88, 0.26/0.45, 0.24/0.40 ✓
  - clustered Rpast AUC: 0.457/0.473 ✓
  - clustered log-loss differences: 0.015 and 0.007, so ≤ 0.02 ✓
- The CURRENT_STATUS.md pointer line (line 124) is present. CURRENT_STATUS.md and ERRATA are **not** pinned (not in artifacts.csv or audit_manifest).
- E9 itself is sound. Its only problem is that E8 contradicts it (R1).

### AUD-CORR-0995-SCOPE row (0b96ba8) — PASS for the new text; R2 still open
The caveat/note now says that `fix/corr-0995-scope` (and v2) will not be merged and that E9 is the record. The change was made in the build script's `NEW` list, and the CSV was regenerated from it. The 0.987 median is unchanged (R2).

### build_claims_reconciliation.py LF (7c1e079) — PASS
- Re-run in my clone at a60b0d9: exit 0, "claims.csv: 75 rows", "lineage_reconciliation.csv: 32 rows". `git status` is clean, so the output is **byte-identical**.
- Neither output is pinned. The pinned input (ART-2845 lineage CSV) still hashes to a633819d… after the run.

### validate_registry_against_tree.py --write LF (180bd03) — PASS
- `--write` in my clone left artifacts.csv byte-identical.
- relocation_map.csv differs by **one content field** only: the `aief_modular_platform_v1_analysis_v4` row goes from `PRESENT_SAME_COUNT` to `PRESENT_COUNT_CHANGED, files now 41; registry 39`. This is caused by the v4.1 files, not by EOL; the file has 0 CR before and after.
- Neither output is pinned. I reverted the clone afterwards.
- Registry drift is left for the owner (see N4).

### Pinned CSV restore + .gitattributes (a60b0d9) — PASS
| file | 7fdf9ed / f51c6d0 | a60b0d9 | pin |
|---|---|---|---|
| zip_only_files/AIEF_1_4_CONTROLLER_FIBER_CLAIM_REGISTRY.csv | 4fd11fc9… (LF, 0 CR) ✗ | **2fb5517d…** (13 CR) | ART-2835 2fb5517d… ✓; also CONTROLLER_FIBER_FREEZE_MANIFEST.json, PROVENANCE.json ✓ |
| zip_only_files/AIEF_1_4_analysis_lineage.csv | 00df78c8… (LF, 0 CR) ✗ | **a633819d…** (33 CR) | ART-2845 a633819d… ✓; also lineage_freeze_manifest.json, PROVENANCE.json ✓ |

- The content is identical to 7fdf9ed after stripping `\r`, so the restore changes only EOL bytes. The bytes equal the local original 487d5a9.
- `.gitattributes` has 1 comment line plus exactly these 2 paths with `-text`. I ran `git check-attr -a` over all tracked files: only these 2 paths have any attribute set. There is no `* text=auto`.
- Note: at 7fdf9ed and f51c6d0 these two files did **not** match their pins (connector-upload damage, inherited from the remote). a60b0d9 fixes a pre-existing pin break; it does not create one.

## Line endings
- The `git ls-files --eol` inventory at a60b0d9 has **20** i/crlf files and 0 i/mixed. The researcher's "18" is the count at 180bd03; a60b0d9 adds the 2 restored files. The REPORT.md follow-up (still says HEAD 180bd03 and "No .gitattributes added") is out of date, but it is not in the repo.
- **All 20 CRLF files are pinned and match their pins.**
  - 18 are worktree rows in artifacts.csv: ART-0056, 0105, 0762, 0865, 0968, 1071, 1175, 1278, 1321, 1575, 1679, 1782, 1885, 1996, 2221, 2474, 2577, 2583.
  - 2 are zip-member rows whose planned_stage4_target is the tracked file: ART-2835 and ART-2845.
- Changed files (15 vs 7fdf9ed) whose EOL differs from 7fdf9ed:
  - the 2 restored CSVs (LF→CRLF, intended)
  - 5 new files, all LF: .gitattributes, v4.1 script, v4.1 test, check_modes.py, test_check_modes.py
  - All other changed files are LF at both ends.
- **No pinned file was touched by a CRLF→LF hand conversion on this branch.** The only pinned files whose bytes changed are the 2 restorations, and they now match their pins.
- Nuance on "no build script writes CRLF": that is true of the registry build scripts (no `\r\n` literal remains in tracked .py). Several *simulation/freeze* scripts use `csv.DictWriter` with its default `\r\n` terminator, which is where the 20 pinned CRLF files come from (e.g. AIEF_1_3_falsification*.py, AIEF_1_4_Twindow_sensitivity.py, the modular `artifacts.py`, `AIEF_1_4_freeze_analysis_lineage.py`). This is consistent: a re-run would reproduce CRLF that matches the pins. Not a defect.

## Every artifacts.csv pin vs the tree at a60b0d9
I wrote an independent checker, `/workspace/audit_pp1/scripts/check_artifacts.py`. It hashes every worktree row from the git blob and every zip row from the zip member. Results are identical at 7fdf9ed, f51c6d0 and a60b0d9:
- worktree SAME 2701, CHANGED 7, MISSING 52; zip members SAME 138; 2898 rows total.
- The 7 CHANGED are all pre-existing and already flagged `PRESENT_CHANGED_SHA`: ART-0001 `.gitignore`, ART-0712, ART-0743–0746, ART-0748 (lean/AIEFProofs). The 52 MISSING are all already flagged `MISSING_DELETED_ON_MAIN`.
- **No new pin breaks on this branch.**

A second check (`scripts/check_targets.py`) compares each zip row's planned_stage4_target with its pin:
- 7fdf9ed: 4 mismatches.
- a60b0d9: 2 mismatches. These are ART-2869 and ART-2886, whose targets are `diffs_vs_root/*.py.diff`. A diff file is not meant to equal its zip member, and both are unchanged since 487d5a9, so this is expected.
- The 2 that this branch fixed are ART-2835 and ART-2845.

## Earlier scope (carried forward; re-verified at a60b0d9 where applicable)
- **v4 unchanged.** sha256 d05a32a4… equals 7fdf9ed and the ART-0063 / ART-2762 pins.
- **v4.1 diff.** It is minimal and correct:
  - Tolerance is HOLD_TOLERANCE_FRACTION 1e-6 × the minimum grid spacing. It is *not* dt/2 or an integer step index, as the brief stated.
  - Exact holds are accepted on all grids, including the last start.
  - A drop one step short is rejected, and censored events are rejected.
  - For nominal durations it gives 0 disagreements with v4.
  - Estimands `held`, `held_retention` and `held_recovery`, and the priority order of `classify_held_event`, match their docstrings. There is no "time to first loss" estimand (another brief discrepancy).
  - v4.1 sits behind `--allow-unaudited-candidate` and returns exit 2 otherwise.
- **32 misses reproduced** on the saved v4 grid (time stamps 0.01…319.51, 640 samples) without regenerating trajectories. The denominator is 605 (R4).
- **check_modes.** Warn-only, exit 0. 125 warnings = 8 known (4 built-in plus the 4 from PUSH_NOTES) + 117 other shebang files; these are plausible. The new CI job uses the same pinned action SHAs.
- **Ledger.** lint_claims: 75 rows, 0 violations. AUD-TIMESTEP / AUD-B-SCAFFOLD labels (Incomplete/Conjecture/Not established) follow the AUD-NOVELTY precedent, and their citations (FORWARD_PLAN line 360, HANDOFF line 527, resp1 line 19, resp2 line 18) check out. E8 numbers all match the JSON (wording: R1).
- **Pinned/audit inputs.** verify_manifest OK (145). `--inputs` OK (145 + 24). check_manifest PASS.

## CI / tools re-run at a60b0d9 (logs/a60/)
| check | result |
|---|---|
| lint_claims | 75 rows, 0/0/0 PASS |
| hygiene_scan (tree) | 0 errors, 3 BIG_FILE warnings (pre-existing) PASS |
| hygiene_scan --base 7fdf9ed --pii | 15 files, 0/0 PASS |
| check_manifest | 1 verifier, 0 failed PASS |
| verify_manifest / --inputs | OK 145 / OK 145 + 24 |
| check_modes | exit 0, 125 warnings PASS; `--strict` exit 1 "0 error(s) … FAIL" (cosmetic, N2) |
| unittest discover tools/ci/tests | 24 OK |
| pytest tools/ci/tests | 24 passed |
| v4.1 + analysis_v4 tests | 19 passed, 2 inherited Pandas4Warnings |
| platform pytest (default) | 40 passed, 2 skipped |
| validate_registry (read-only) | same flags as at f51c6d0, except +1 tracked file not in artifacts.csv (.gitattributes) |
| check_citations (merge_recheck script) | 0 blank or out-of-range cited lines |
| build scripts re-run | claims.csv / lineage byte-identical; artifacts.csv byte-identical |

## Non-blocking notes
- N1: The v4.1 test `_exact_cases` should include the last valid start (`range(0, len-k)`).
- N2: `check_modes --strict` prints "0 error(s) … FAIL". Say why it fails (warnings are promoted). `shebang_objects` can raise an uncaught CalledProcessError.
- N3: PUSH_NOTES.md item 4 still lists the two pinned zip_only CSVs as differing from local. That is no longer true at a60b0d9; add a one-line note. PUSH_NOTES is not pinned.
- N4: relocation_map.csv is stale for `aief_modular_platform_v1_analysis_v4` (41 files vs registry 39). Refresh it or record it. `.gitattributes` is a new tracked file not in artifacts.csv (harmless).
- N5: Only 2 of the 20 CRLF files are marked `-text`. This is fine while no `text=auto` is used. If normalization is ever enabled, add the other 18.
- N6: Brief discrepancies, for the record: the tolerance is not dt/2 or an integer step, and there is no "time to first loss" estimand.

---

# Delta check: work/post-push-1 @ 0493f26 (8 commits on a60b0d9)

Written 2026-10-28 ~21:05 EDT (America/Toronto). This check was read-only, run in my clone `/workspace/audit_pp1/repo`. Nothing was pushed and Researcher 001's worktree was not touched. Logs are in `/workspace/audit_pp1/logs/d0493/`.

## Delta verdict: **READY.** R1–R4 and N1–N4 and N6 are fixed as described. N5 was not acted on, which is acceptable. No new blockers.

### Required fixes
| # | Commit | Status | Evidence |
|---|---|---|---|
| R1 | fd08957 | **Fixed** | E8 now reads "For clustered ω it discriminated worse on AUC (0.46–0.47 vs 0.65–0.73), with log-loss differences of at most 0.02". This matches E9. The revision note's numbers match the JSON: clustered baseline log loss 0.304 (past R) vs 0.319 (Δω-only); no_delay 0.286 vs 0.279. |
| R2 | b8a3709 | **Fixed** | The uniform no_delay median now reads 0.986 (JSON 0.98649). First-pass sources are added to the statement and to supporting_artifacts (`evidence/logs/omega_random.log`, `results/omega_random.json`, salvage §3.1); both files exist. I recomputed the defined-run counts from omega_random.json: uniform 20/20 and 40/40; clustered 15/20 (mean 0.588) and 30/40 (mean 0.634). All match. |
| R3 | b8a3709, 0bd4552 | **Fixed** | AUD-MODULAR-ORACLE and CURRENT_STATUS now say "default 40 passed, 2 skipped; 41/1 with AIEF_RUN_SLOW_TESTS=1 and the repo root on PYTHONPATH". The IMPL-MODULAR-01 note is updated the same way. I re-ran both: default **40 passed, 2 skipped**; slow **41 passed, 1 skipped**. The PYTHONPATH wording now correctly says that `pytest.ini pythonpath = .` imports the rest of the suite. |
| R4 | b8a3709, 0bd4552, cb2e853 | **Fixed** | The ledger and CURRENT_STATUS say "32 of the 605 valid start positions". The blocker is scoped to the fixed_physical_17p5 held rows, and the T_window-nominal and non-held estimands are explicitly excluded. The test now asserts 605 starts and 32 v4 misses, and that v4 holds the last start correctly. It passes. |

### Non-blocking items
- **N1 (cb2e853): fixed.** `_exact_cases` and `test_v4_1_rejects_one_step_short` now use `range(0, len-k)`, which includes the last start.
- **N2 (f342557): fixed.**
  - `--strict` now prints `8 error(s), 117 warning(s) (--strict: known-list scripts not 100755 count as errors) -> FAIL` with exit 1, and `ERROR KNOWN_NOT_EXEC` ×8.
  - In GitHub Actions the annotation is `::error`. The default mode is unchanged (0 errors, 125 warnings, PASS, exit 0).
  - A `git cat-file` failure now exits 2.
  - 3 new tests; the CI suite went from 24 to 27, all passing.
- **N3 (0493f26): fixed.** PUSH_NOTES item 4 has an update paragraph: the two pinned CSVs are restored at a60b0d9 and marked `-text`, and the other 9 stay LF (unpinned).
- **N4 (028a9d4): fixed.** In relocation_map only the `aief_modular_platform_v1_analysis_v4` row changed (`PRESENT_COUNT_CHANGED, files now 41; registry 39`). Re-running `validate_registry --write` now leaves *both* artifacts.csv and relocation_map.csv byte-identical. `.gitattributes` is still not in artifacts.csv, which is harmless.
- **N5: not acted on.** Only 2 of the 20 CRLF files are marked `-text`. This is acceptable while no `text=auto` is set.
- **N6 (b4870f2): fixed.** The v4.1 header now says tol = 1e-6 × the smallest positive saved-grid step (0.5e-6 on the 0.5 grid). It states that this is not dt/2 and not an integer-step check, and that the only new estimands are held/retention/recovery. "Time to first loss" is noted as a possible future, separately audited change. These are docstring-only changes; the logic is unchanged.

### Regeneration, pins, EOL
- **claims.csv equals a fresh regeneration.** I re-ran `build_claims_reconciliation.py` at 0493f26 (75 rows; lineage 32 rows), and `git status` was clean. Both claims.csv and lineage_reconciliation.csv are byte-identical.
- **verify_manifest:** OK, 145 published files. **`--inputs`:** OK, 145 + 24 inputs. check_manifest: PASS. `AI Agent Audits/` has not changed since 7fdf9ed.
- **artifacts.csv pin check** (all 2898 rows): worktree SAME 2701 / CHANGED 7 / MISSING 52; zip SAME 138.
  - The CHANGED rows are exactly ART-0001, 0712, 0743, 0744, 0745, 0746 and 0748, all flagged `PRESENT_CHANGED_SHA`.
  - The 52 MISSING rows are all `MISSING_DELETED_ON_MAIN`.
  - There are no new breaks. The zip-target check is unchanged (21 match; the 2 expected `.diff` mismatches).
- The v4 script is still at d05a32a4… (its pins).
- **EOL:** 20 i/crlf files and 0 mixed. They are the same 20 paths as at a60b0d9, and all are pinned and match their pins. All 10 files changed in this delta are LF before and after (no CR at a60b0d9 either).

### CI re-run at 0493f26
| check | result |
|---|---|
| lint_claims | 75 rows, 0/0/0 PASS |
| hygiene_scan | 0 errors, 3 BIG_FILE (pre-existing) PASS |
| hygiene_scan --base 7fdf9ed --pii | 17 files, 0/0 PASS |
| check_manifest | PASS |
| check_modes / --strict | exit 0, 125 warnings PASS / exit 1, 8 errors + 117 warnings FAIL (consistent) |
| unittest / pytest tools/ci/tests | 27 OK / 27 passed |
| v4.1 + analysis_v4 tests | 19 passed (2 inherited Pandas4Warnings) |
| platform pytest default / slow | 40 passed, 2 skipped / 41 passed, 1 skipped |
| validate_registry | artifacts flags 2701/7/52/138; relocation_map 213 same, 4 count-changed, 4 missing |
| check_citations | 0 blank or out-of-range cited lines |

### H2 / AIEFS_audit.md:32 "near-circular" (non-blocking)
- `AI Agent Audits/AIEFS_audit.md` line 32 (H2) still opens with "Corr_physical ≈ 0.995 is near-circular. …" and has only a trailing tag, "[Correction 2026-10-23, response #2: done; see the response ledger]". That tag does not say what the corrected verdict is.
- The file is hash-pinned (audit_manifest.json; unchanged since 7fdf9ed), so it must stay as is.
- The ledger already records the supersession. The AUD-CORR-0995 note says "'near-circular' is the round-1 wording (audit.md H2, line 32) that was later corrected to 'not a tautology'", in line with resp1 #2 and §3 item 3.
- None of the ERRATA entries (E1, E8, E9) points at H2 / audit.md:32.
- **Recommendation (non-blocking):** add a one-line pointer, e.g. in E9 or E1: "`AIEFS_audit.md:32` (H2) 'near-circular' is round-1 wording; superseded (resp1 #2): not a tautology, dominated by persistence, and scoped to the repository ω (AUD-CORR-0995, AUD-CORR-0995-SCOPE)." This is not required: the ledger is the authority and already says it. But someone reading the audit file directly currently gets no corrected verdict from the errata.
- Related: the pinned `AIEFS_audit_response.md:42` still says "does worse for clustered ω". E8 already covers this as an erratum, so no further action is needed.
