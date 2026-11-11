# Workspace salvage 2026-10-31 — UNVERIFIED

**Status: UNVERIFIED salvage.** Nothing here has been re-run, reviewed, or checked for correctness. Treat every file as a lead, not as evidence. Do not cite it in claims, verdicts, or the registry without re-verifying from source.

## Why this exists
The shared work box ran out of disk on 2026-10-31. Before old clones and scratch folders were deleted, small, possibly useful non-git files were copied here, along with uncommitted diffs.

## How it was selected
- Source folders: `/workspace/<folder>` on the shared box. Each top-level directory here is named after its source folder.
- Text types only (.md .txt .py .sh .lean .csv .json .diff .patch .toml .yml), each ≤ 5 MB. No `*.log` files, build outputs, `.lake`, venvs or binaries.
- Files whose git blob hash already exists anywhere in GitHub history were dropped, as were exact duplicates within this salvage.
- Excluded on purpose: PDF text extracts of project-history/origin documents (personal material), extracted agent-workspace zips, gh auth output, private-pattern files, credential files, and the scrub/evidence folders.
- Home-directory paths were rewritten to `/home/<user>`. Two files that contained a private literal were dropped or redacted. `tools/ci/hygiene_scan.py --pii --private-patterns` then showed only 2 PII_PHONE warnings, both in `audit_project_map/freezing_count.txt`. They are false positives: RNG seeds, not phone numbers.

## Unpushed git commits
These were pushed as `salvage/<folder>-<branch>` branches, not copied here: AIEFS_audit_fresh (work-post-push-1, merge-prep-arena-reconciled, fix-corr-0995-scope-v2), autonomy_setup (merge-prep-arena-reconciled, main), audit_r001_branches-wt_merge, AIEFS-local-final, AIEFS-local-cleanup-untrack. Note: these branches carry the same history (and the same pre-existing PII exposure) as main/arena. Any future history scrub must include them.

## Contents

### _uncommitted_diffs/ (5 files, 214 KB)
`git diff HEAD` of dirty worktrees that were deleted (logs, .lake and a 56k-line inventory.json deletion excluded).

- `_uncommitted_diffs/license_inventory_fresh_vs_1a81cb6.patch` (1327 B)
- `_uncommitted_diffs/push_r5_AIEFS_vs_6b49a7b.patch` (7526 B)
- `_uncommitted_diffs/push_r5_stateA_vs_6b49a7b.patch` (3024 B)
- `_uncommitted_diffs/v4_r4b_vs_43ce98f.patch` (107648 B)
- `_uncommitted_diffs/v4_repo_vs_dc0250a.patch` (99582 B)

### audit_pp1/ (9 files, 53 KB)
Audit of a post-push state (AUDIT.md), v4→v4.1 diff, small check scripts and validation JSON.

- `audit_pp1/AUDIT.md` (19972 B)
- `audit_pp1/check_outputs/eol_crlf_head.txt` (2117 B)
- `audit_pp1/check_outputs/validate_base.json` (1115 B)
- `audit_pp1/check_outputs/validate_head.json` (1142 B)
- `audit_pp1/check_outputs/validate_write_a60.json` (1167 B)
- `audit_pp1/new_rows.txt` (8195 B)
- `audit_pp1/scripts/check_artifacts.py` (1261 B)
- `audit_pp1/scripts/check_targets.py` (646 B)
- `audit_pp1/v4_v41.diff` (18328 B)

### audit_project_map/ (31 files, 466 KB)
Project claims map (AUDIT.md, DELTA.md), claims_map.csv reruns, Lean theorem/axiom listings, evidence-level tables. Page snapshots are text dumps of a project page.

- `audit_project_map/AUDIT.md` (17173 B)
- `audit_project_map/DELTA.md` (9291 B)
- `audit_project_map/_lean/AIEFFreezeCore/AuditAxioms.lean` (226 B)
- `audit_project_map/_lean/AIEFProofs/AuditAxioms_AIEFProofs.lean` (3969 B)
- `audit_project_map/_lean/AIEFProofsKn/AuditAxioms.lean` (2765 B)
- `audit_project_map/_lean/axioms_AIEFFreezeCore.txt` (439 B)
- `audit_project_map/_lean/axioms_AIEFProofs.txt` (6942 B)
- `audit_project_map/_lean/axioms_AIEFProofsKn.txt` (4711 B)
- `audit_project_map/_lean/checklog/summary.txt` (1214 B)
- `audit_project_map/_lean/gen_axioms.py` (739 B)
- `audit_project_map/_lean/theorems.txt` (7103 B)
- `audit_project_map/delta/page_v2.txt` (39819 B)
- `audit_project_map/delta/rerun_shas.txt` (916 B)
- `audit_project_map/delta/run2/MAP_NOTES.md` (8521 B)
- `audit_project_map/delta/run2/build_map.py` (50565 B)
- `audit_project_map/delta/run2/claims_map.csv` (46798 B)
- `audit_project_map/delta/run2/inconsistencies.csv` (5026 B)
- `audit_project_map/delta/run2/totals.json` (5251 B)
- `audit_project_map/delta/sweep_v2.txt` (68568 B)
- `audit_project_map/evidence/citations.csv` (2043 B)
- `audit_project_map/evidence/confusion_table.md` (531 B)
- `audit_project_map/evidence/evidence_levels_auditor.csv` (7825 B)
- `audit_project_map/evidence/independent_count.json` (2422 B)
- `audit_project_map/evidence/independent_count_and_confusion.py` (4530 B)
- `audit_project_map/evidence/rerun_diff.txt` (383 B)
- `audit_project_map/freezing_count.txt` (821 B)
- `audit_project_map/page_source_snapshot.txt` (32740 B)
- `audit_project_map/rerun/build_map_copy.py` (32971 B)
- `audit_project_map/rerun/claims_map.csv` (41236 B)
- `audit_project_map/rerun/totals.json` (3191 B)
- `audit_project_map/research_sweep_page_snapshot.txt` (68492 B)

### audit_r001_branches/ (17 files, 31 KB)
Branch audit notes (AUDIT.md), Lean axiom-check summaries for base / freezing core / lean-kn, CI helper scripts.

- `audit_r001_branches/AUDIT.md` (11890 B)
- `audit_r001_branches/lean_audit/AuditKn.lean` (835 B)
- `audit_r001_branches/check_outputs/c_base_check/source_sha256.txt` (920 B)
- `audit_r001_branches/check_outputs/c_base_check/summary.txt` (1205 B)
- `audit_r001_branches/check_outputs/c_fz_check/3_reachable_modules.txt` (41 B)
- `audit_r001_branches/check_outputs/c_fz_check/7_axioms_check.lean` (1276 B)
- `audit_r001_branches/check_outputs/c_fz_check/7_axioms_summary.txt` (382 B)
- `audit_r001_branches/check_outputs/c_fz_check/source_sha256.txt` (429 B)
- `audit_r001_branches/check_outputs/c_fz_check/summary.txt` (717 B)
- `audit_r001_branches/check_outputs/c_lean_kn_check/3_reachable_modules.txt` (108 B)
- `audit_r001_branches/check_outputs/c_lean_kn_check/7_axioms_check.lean` (3896 B)
- `audit_r001_branches/check_outputs/c_lean_kn_check/7_axioms_summary.txt` (4021 B)
- `audit_r001_branches/check_outputs/c_lean_kn_check/source_sha256.txt` (757 B)
- `audit_r001_branches/check_outputs/c_lean_kn_check/summary.txt` (1111 B)
- `audit_r001_branches/scripts/ci_all.sh` (1192 B)
- `audit_r001_branches/scripts/pins.py` (2047 B)
- `audit_r001_branches/scripts/run_ci.sh` (917 B)

### autonomy_setup/ (4 files, 13 KB)
Notes from an autonomy/CI setup pass (README, a PII-email change note, status suggestions).

- `autonomy_setup/out/CHANGES_2026-10-28_pii_email.md` (1926 B)
- `autonomy_setup/out/README_AUTONOMY_SETUP.md` (4441 B)
- `autonomy_setup/out/notes/status_suggestions.md` (6256 B)
- `autonomy_setup/sim/run_ci.sh` (624 B)

### corr_0995_fix/ (2 files, 14 KB)
Audit v2 and patch scoping the Corr_physical 0.995 figure (the branch itself is on GitHub as fix/corr-0995-scope).

- `corr_0995_fix/0001-Docs-scope-the-Corr_physical-0.995-figure-to-the-rep.patch` (1965 B)
- `corr_0995_fix/AUDIT_v2.md` (11936 B)

### lean_fix/ (38 files, 68 KB)
Lean recovery work: 3 patches (dangling import, candidate projector module, check_lean script + CI), negative-test summaries (sorry/axiom/native_decide/macro sorryAx), axiom-check outputs.

- `lean_fix/0001-remove-dangling-ControllerFiberProjector-import.patch` (309 B)
- `lean_fix/0002-OPTIONAL-candidate-ControllerFiberProjector-module.patch` (3992 B)
- `lean_fix/0003-add-check_lean-script-and-root-CI-workflow.patch` (14881 B)
- `lean_fix/LEAN_STATUS.before_recovery.md` (9756 B)
- `lean_fix/candidate/ControllerFiberProjector.candidate.lean` (3629 B)
- `lean_fix/check_outputs/20_fix_a_check/7_axioms_check.lean` (2156 B)
- `lean_fix/check_outputs/20_fix_a_check/summary.txt` (1262 B)
- `lean_fix/check_outputs/21_fix_a_check_rerun/summary.txt` (855 B)
- `lean_fix/check_outputs/22_fix_a_no_committed_build_artifacts/3_reachable_modules.txt` (55 B)
- `lean_fix/check_outputs/22_fix_a_no_committed_build_artifacts/7_axioms_check.lean` (2162 B)
- `lean_fix/check_outputs/22_fix_a_no_committed_build_artifacts/7_axioms_summary.txt` (1533 B)
- `lean_fix/check_outputs/22_fix_a_no_committed_build_artifacts/source_sha256.txt` (602 B)
- `lean_fix/check_outputs/22_fix_a_no_committed_build_artifacts/summary.txt` (873 B)
- `lean_fix/check_outputs/23_fix_a_final_script/summary.txt` (954 B)
- `lean_fix/check_outputs/30_negative_tests/N1_sorry/5_build_diagnostics.txt` (63 B)
- `lean_fix/check_outputs/30_negative_tests/N1_sorry/summary.txt` (881 B)
- `lean_fix/check_outputs/30_negative_tests/N2_axiom/summary.txt` (862 B)
- `lean_fix/check_outputs/30_negative_tests/N3_native_decide/summary.txt` (896 B)
- `lean_fix/check_outputs/30_negative_tests/N4_macro_sorryAx/5_build_diagnostics.txt` (63 B)
- `lean_fix/check_outputs/30_negative_tests/N4_macro_sorryAx/summary.txt` (912 B)
- `lean_fix/check_outputs/30_negative_tests/N5_missing_import/3_reachable_modules.txt` (74 B)
- `lean_fix/check_outputs/30_negative_tests/N5_missing_import/summary.txt` (814 B)
- `lean_fix/check_outputs/30_negative_tests/N6_type_error/5_build_diagnostics.txt` (186 B)
- `lean_fix/check_outputs/30_negative_tests/N6_type_error/summary.txt` (876 B)
- `lean_fix/check_outputs/30_negative_tests/N7_step7_semantic/7_axioms_check_neg.lean` (2188 B)
- `lean_fix/check_outputs/30_negative_tests/R0_restored/summary.txt` (865 B)
- `lean_fix/check_outputs/41_candidate_as_module_check/3_reachable_modules.txt` (91 B)
- `lean_fix/check_outputs/41_candidate_as_module_check/7_axioms_check.lean` (2881 B)
- `lean_fix/check_outputs/41_candidate_as_module_check/7_axioms_summary.txt` (2539 B)
- `lean_fix/check_outputs/41_candidate_as_module_check/source_sha256.txt` (709 B)
- `lean_fix/check_outputs/41_candidate_as_module_check/summary.txt` (993 B)
- `lean_fix/check_outputs/50_final_end_to_end/20261025T012635Z/summary.txt` (1019 B)
- `lean_fix/check_outputs/51_final_end_to_end_NO_CACHE_from_source/20261025T012114Z/summary.txt` (992 B)
- `lean_fix/check_outputs/verify_0b5b108_plus_0003/7_axioms_check.lean` (3542 B)
- `lean_fix/check_outputs/verify_0b5b108_plus_0003/7_axioms_summary.txt` (3629 B)
- `lean_fix/check_outputs/verify_0b5b108_plus_0003/source_sha256.txt` (709 B)
- `lean_fix/check_outputs/verify_0b5b108_plus_0003/summary.txt` (1089 B)
- `lean_fix/scratch/clone_final/lean/AIEFProofs/AIEFProofs.lean` (59 B)

### merge_check/ (8 files, 84 KB)
MERGE_CHECK.md for merge-prep/arena-reconciled plus scan scripts and logs (the 2.8 MB merged_vs_main.diff was dropped; regenerate from salvage branches).

- `merge_check/MERGE_CHECK.md` (21025 B)
- `merge_check/check_outputs/artifact_sha_changed.txt` (1063 B)
- `merge_check/check_outputs/claims_dump.txt` (50110 B)
- `merge_check/check_outputs/hash_pins_old.txt` (3102 B)
- `merge_check/check_outputs/name_status.txt` (6709 B)
- `merge_check/scripts/artifact_sha_diff.py` (464 B)
- `merge_check/scripts/check_citations.py` (1332 B)
- `merge_check/scripts/diff_scan.py` (2107 B)

### merge_recheck/ (10 files, 40 KB)
RECHECK.md, Lean summaries, privacy/vocab/time-hygiene scripts.

- `merge_recheck/RECHECK.md` (22818 B)
- `merge_recheck/check_outputs/ci_886daf6/validate_registry_write.diff` (1004 B)
- `merge_recheck/check_outputs/ci_9053b77/hyg_timing.txt` (165 B)
- `merge_recheck/check_outputs/lean/summary.txt` (1294 B)
- `merge_recheck/check_outputs/lean886/20261028T232944Z/summary.txt` (1333 B)
- `merge_recheck/check_outputs/name_status.txt` (6632 B)
- `merge_recheck/scripts/d43d757_math.py` (2519 B)
- `merge_recheck/scripts/privacy_classify.py` (3357 B)
- `merge_recheck/scripts/time_hygiene.py` (722 B)
- `merge_recheck/scripts/vocab_check.py` (1449 B)

### nanfix/ (3 files, 10 KB)
NaN-fix reproduction: compare_b2a95dfbfbe3 v2 script, v1→v2 diff and ERRATUM note (were untracked).

- `nanfix/out/AI Agent Audits/evidence/reproductions/compare_b2a95dfbfbe3_ERRATUM.md` (2557 B)
- `nanfix/out/AI Agent Audits/evidence/reproductions/compare_b2a95dfbfbe3_v1_to_v2.diff` (1082 B)
- `nanfix/out/AI Agent Audits/evidence/reproductions/compare_b2a95dfbfbe3_v2.py` (6966 B)

### post_push_1/ (1 files, 19 KB)
REPORT.md from a post-push audit.

- `post_push_1/REPORT.md` (19323 B)

### push_pp1/ (1 files, 1 KB)
File list used for a push.

- `push_pp1/list.txt` (538 B)

### push_r5/ (1 files, 6 KB)
compare_b2a95dfbfbe3.py reproduction script.

- `push_r5/repro/compare_b2a95dfbfbe3.py` (6446 B)

### push_review/ (3 files, 22 KB)
Push review plan/text.

- `push_review/all.txt` (6848 B)
- `push_review/plan.json` (9365 B)
- `push_review/text.txt` (6551 B)

### repo_cleanup/ (1 files, 50 KB)
Patch adding tools/sync safe upload/download/cleanup scripts (the 3.1 MB untrack patch was dropped: same change as salvage/AIEFS-local-cleanup-untrack).

- `repo_cleanup/0002-Add-tools-sync-safe-upload-download-cleanup-scripts-.patch` (51319 B)

### review_6b49a7b/ (16 files, 264 KB)
Review of commit 6b49a7b: REVIEW.md, inventory/namematch/compare_runs JSON, numbered scripts. One line of 05_hygiene_scan.py redacted (private literal).

- `review_6b49a7b/REVIEW.md` (15630 B)
- `review_6b49a7b/inventory.json` (71942 B)
- `review_6b49a7b/namematch.json` (62219 B)
- `review_6b49a7b/results/compare_runs.json` (90554 B)
- `review_6b49a7b/results/hygiene_scan.json` (11384 B)
- `review_6b49a7b/results/identity_check.json` (191 B)
- `review_6b49a7b/results/text_overlap.json` (923 B)
- `review_6b49a7b/scratch/run_copy/aief_1_4_two_channel_alignment_v2/two_channel_summary.csv` (846 B)
- `review_6b49a7b/scripts/01_extract.sh` (737 B)
- `review_6b49a7b/scripts/02_inventory.py` (3662 B)
- `review_6b49a7b/scripts/03_namematch.py` (1949 B)
- `review_6b49a7b/scripts/04_compare_runs.py` (4180 B)
- `review_6b49a7b/scripts/05_hygiene_scan.py` (3190 B)
- `review_6b49a7b/scripts/06_identity_check.py` (991 B)
- `review_6b49a7b/scripts/07_run_included_tests.sh` (864 B)
- `review_6b49a7b/scripts/08_text_overlap.py` (1263 B)

### upload_stage/ (2 files, 6 KB)
Upload manifests for freezing / lean-kn branches.

- `upload_stage/freezing.json` (4084 B)
- `upload_stage/lean-kn.json` (1974 B)

### v2/ (1 files, 7 KB)
make_manifest.py (make_v2.py dropped: contained a private literal).

- `v2/make_manifest.py` (7541 B)

### v4/ (11 files, 99 KB)
Lean check summaries, check.sh, and modified-vs-HEAD copies of v4/repo files (audit_response_3, audit_manifest, make_manifest).

- `v4/leanwork/lean/AIEFProofs/check_outputs/20261025T025501Z/source_sha256.txt` (920 B)
- `v4/leanwork/lean/AIEFProofs/check_outputs/20261025T025501Z/summary.txt` (1294 B)
- `v4/push_r4/check.sh` (1231 B)
- `v4/repo/AI Agent Audits/AIEFS_audit_response_3.md` (23842 B)
- `v4/repo/AI Agent Audits/evidence/audit_manifest.json` (40547 B)
- `v4/repo/AI Agent Audits/evidence/check_outputs/lean_r4/summary.txt` (1269 B)
- `v4/repo/AI Agent Audits/evidence/tooling/make_manifest.py` (16159 B)
- `v4/repo/lean/AIEFProofs/AIEFProofs/CompleteGraphIncidence.lean` (7594 B)
- `v4/repo/lean/AIEFProofs/AIEFProofs/ControllerFiberQuotient.lean` (2710 B)
- `v4/repo/lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt` (754 B)
- `v4/repo/lean/AIEFProofs/README.md` (5092 B)
Note: directories named `logs/` or `.check_logs/` in the source folders were renamed to `check_outputs/` here, because the repo `.gitignore` ignores `logs/`. The files themselves are unchanged.
