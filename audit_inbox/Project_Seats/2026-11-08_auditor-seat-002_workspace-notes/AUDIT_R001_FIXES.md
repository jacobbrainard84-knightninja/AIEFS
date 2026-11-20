# Auditor Seat 002 — audit of Researcher 001's red-team fix branches

Date: 2026-10-31 (EDT). Read-only on remote: nothing pushed, no PRs or comments. All work was done in one temporary worktree (`wt_audit3`), which has since been removed. Lean was not built.
Base: `main` 395ea53. Red-team kit: `research/redteam-negcontrols` a614451. Baseline on a614451: CI self-tests 103 OK, red-team 74 tests / 13 GAP (xfail) / 0 unexpected successes.

## Common checks (all branches)
- **Ancestry.** Every fix branch has merge-base 395ea53. The a614451 cherry-picks (54d5ff7, 33d34ca, bec5b69, 47a8b31, 0ed36da) each have parent 395ea53, and each tree is identical to a614451 (0-line diff).
- **Hash-pinned files** (audit_manifest.json, registry/artifacts.csv, lean_recovery/SHA256SUMS, AIEF_LEAN_SOURCE_SHA256SUMS.txt, tools/sync/SHA256SUMS and everything they pin: verify_manifest.py, root .gitignore ART-0001, check_lean.sh): **no branch touches any of them.**
- **Main's real tree** passes every changed checker on every branch.

## (A) fix/lint-claims-artifacts @ 8583ea4 (G3 + G4): MERGE-READY, with follow-ups
- Scope: 4 files. Inventory regenerates with no diff. CI tests 103 OK. Red-team 76 tests / 11 xfail: exactly G3 (`row_citing_nonexistent_artifact`) and G4 (`false_claim_marked_proved`) flipped, 0 unexpected. The converted tests assert specific messages ("cited artifact does not exist", "claims a formal/Lean proof ... cites no existing .lean file").
- **Is the .lean requirement correct?** Yes for the current data. Main has 3 formal-scoped rows (LEAN-CF-01, LEAN-R4, LEAN-KN-01); all cite real .lean files and pass. Not accepting a registry row as proof is the right call.
- **Allow-list:** minimal. `KNOWN_MISSING_ARTIFACTS` (lint_claims.py:60) is keyed exactly by (AUD-REPRO-B2A95, v3.log). Citing the same path under another claim_id is rejected.
- Adversarial rows that wrongly **PASS** (follow-ups, not blockers):
  1. lint_claims.py:68 `LEAN_PROOF_TEXT` misses "Machine-checked in Lean 4 without sorry". That is the exact wording of LEAN-CF-01 and LEAN-KN-01, and "Lean 4 verifies …" is missed too. A false row with that wording, under a non-formal scope such as `Conditional theorem`, passes with no .lean file.
  2. lint_claims.py:67 `FORMAL_SCOPE` and :98: a `Machine-checked theorem` scope passes, because `evidence_scope` is not checked against the closed 6-value vocabulary in registry/README.md:64-73. Fix: lint evidence_scope against that vocabulary.
  3. lint_claims.py:77-81: the prefix-shortening loop fails open. `lean/AIEFProofs missing_file.lean` and `registry/claims.csv nonexistent/file.md` pass, because a shorter existing prefix is accepted. Only accept the trailing remainder if it is not path-like.
  4. lint_claims.py:99 only checks that the .lean file exists, not its content. A row citing `lean/AIEFProofs/AIEFProofs/Basic.lean` (which has no such theorem) passes. Document this limit, or require `file.lean:theorem_name` and grep for the name.
  5. Allow-list entries never go stale. Once 1250bbd restores v3.log, the entry at :60 silently stops matching. Add an "allow-listed but now exists → error" check, mirroring C's check_sha256sums.py:100-102.
  6. Hypothetical false positive: `FORMAL_SCOPE` is an unanchored substring match, so "Informal argument" and "Clean replication" would match. Anchor it to the vocabulary values instead.
- Correctly rejected: `../` paths outside the repo, absolute paths, upper/lower-case scope, "formalised in Lean", a case-different path, a `.lake` path, comma-joined entries.

## (B) fix/manifest-nonempty @ b166c03 (G1): OK, but combine with fix/check-manifest-missing-verifier (a428c32)
- Inventory has no diff. CI tests 103 OK. Red-team 76 / 12 xfail: only G1 flipped, 0 unexpected. Real tree: 145 files and 24 inputs, PASS (also with `--no-inputs`).
- Weaknesses (minor):
  - check_manifest.py:36-61 `check_coverage`: one trivial data file is enough to satisfy coverage.
  - Absolute keys in `files_sha256` could point outside the repo (low risk).
  - In the self-test `test_passed_manifest_with_empty_inputs`, rc≠0 also comes from the verifier exiting 2 in the fake repo. The needle is still asserted, so this is acceptable.
  - check_manifest.py:75-77 still has the G2 NOTICE skip, which a428c32 fixes.
- **Overlap with a428c32 (G2):** both rewrite the docstring and the main loop of tools/ci/check_manifest.py. Both also add tests to tools/redteam/test_rt_hashes.py and REDTEAM.md.
- **Combination plan:** use `/workspace/review_r026/check_manifest_G1G2_combined.py`. It is a428c32's file plus b166c03's `json` import, the Coverage-rule docstring paragraph, `check_coverage()`, and the coverage block placed after the verifier-failed annotation. The `ran == 0` notice (b166c03:95-96) is dropped, because a428c32 makes "no verifier" an error. Also apply `/workspace/review_r026/check_manifest_G1G2_testfix.patch` (17 lines) to tools/ci/tests/test_check_manifest.py: the stub `verifier()` fixture must also write `AI Agent Audits/REPORT.md` and an `audit_manifest.json` with one data file and one input. Without it, a428c32's `test_passing_verifier_passes` and `test_no_inputs_flag_drops_inputs_arg` fail with "cannot read manifest".
- Verified result of the combination: inventory has no diff, CI tests 108 OK, real tree PASS, red-team 76 / 11 xfail, only G1 and G2 flipped, 0 unexpected.
- Simplest route: whichever of B and a428c32 merges second takes the combined file and the testfix. They could also be squashed into one PR.

## (C) ci/check-sha256sums @ 6b9abe8: NEEDS FIXES BEFORE MERGE
- **BLOCKER 1: stale inventory.** The committed `registry/artifacts_current.csv` lacks `audits/reproductions/.gitignore`, `tools/ci/check_sha256sums.py` and `tools/redteam/test_rt_sha256sums.py`, so check_current_inventory.py reports NOT_INVENTORIED. The required check "Current-tree inventory" would FAIL. Fix: regenerate and commit (+3 rows).
- **BLOCKER 2 (appears after 1250bbd lands): a red-team test writes into the real checkout.** tools/redteam/test_rt_sha256sums.py:53-57 (`test_allow_listed_file_reappears_with_wrong_content`) opens `root/B2A/v3.log` with `open(..., "w")` after only materializing the folder. Once v3.log exists in the repo, that path is a symlink into the real tree. The test then overwrote the real `compare_b2a95dfbfbe3_v3.log` with "forged v3 log\n" (seen in the simulation and restored with git checkout). Fix: `tamper(self.root, f"{B2A}/{V3}", lambda d: b"forged v3 log\n")`, or unlink before writing. The suite should never `open(...,"w")` a mirror path directly.
- Otherwise: CI tests 103 OK. Red-team 83 / 13 xfail, no GAP change, 0 unexpected. The 9 new tests assert specific messages. Real tree: 5 SUMS files, 48 entries verified, 1 allow-listed, PASS.
- **Discovery** (check_sha256sums.py:29 `NAME_RE`, :43 `os.walk(followlinks=True)`). It finds all 5 real `SHA256SUMS*` files. It does not find:
  - `lean/AIEFProofs/AIEF_LEAN_PROJECT_LOCK_HASHES.txt` (3 entries, all OK). Recommend including it.
  - `AI Agent Audits/evidence/logs/lean_r4/source_sha256.txt` (paths relative to lean/AIEFProofs; Basic.lean and Smoke.lean now FAIL because they are historical, per ERRATA E7). Excluding it is right, but the exclusion should be explicit and documented.
  - `twindow_*hashes*.txt` (absolute /home/deck paths, historical).
  - Lowercase `sha256sums.txt`, `*.sha256` and `*_HASHES.txt`. There are no such files today.
- **Path traversal** (:83-86): `../` and absolute entries are rejected. But the check uses normpath/relpath, not realpath, so an in-repo symlink pointing outside the repo verifies as OK. Use `os.path.realpath` and require it under the repo.
- `followlinks=True` (:43): a symlink loop caused 43 repeated discoveries. Better: discover with `git ls-files`, which also avoids walking untracked files (it does today).
- **Ruleset:** the new job "SHA256SUMS files" (repo-checks.yml job `sha256sums`) is NOT among the 11 required checks of ruleset "Protect main" (id 26247678). The owner must add it after merge, or it is advisory only.
- **1250bbd simulation:** merged 6b9abe8 with 1250bbd. The allow-list error fires as designed: "ERROR … compare_b2a95dfbfbe3_v3.log is allow-listed as missing but now exists and matches; remove it from ALLOWED_MISSING" (:100-102), FAIL. After clearing `ALLOWED_MISSING` (:33-38): check_sha256sums PASS (5 files, 52 entries). But two red-team tests then fail because they hard-code the live entry: the control at :28-31 (`assertIn("allow-listed")`) and `test_allow_listed_entry_removed_from_sums_is_stale` at :59-62. Recommendation: test the allow-list logic with an injected synthetic entry instead of the real M1 entry. The patch I used is `/workspace/review_r026/post_1250bbd_allowlist_cleanup.patch` (it also clears A's KNOWN_MISSING entry).
- Verdict: fix both blockers (inventory, write-through). Should-fix: realpath, git ls-files, explicit include/exclude list. Owner: add the required check.

## (D) audit-inbox @ 113d9e9 vs 93a2364: OK
- Only `audit_inbox/briefing/README.md` (+1/-1) and `audit_inbox/briefing/STATE.md` (+3/-4) changed. No PII: no emails, phones, tokens or home paths. Names are role names only.
- README: §0 → §0b is correct; OPEN_QUESTIONS.md has "### 0b. Red teaming".
- STATE: the `fix/comparator-v4-gates` (1250bbd) row is accurate; 1250bbd's ERRATA really does add E14. The wording "owner OK reported by Auditor Seat 002" is accurate (owner's OK in Auditor Seat 002's chat, 2026-10-31 ~10:50 EDT).
- Nit: "New entries start at E14 … Otherwise renumber nothing" plus "whichever lands second renumbers" is consistent but wordy.

## Merge order (simulated locally from 395ea53)
- **Proposal tested:** PR `research/redteam-negcontrols` (a614451) first, then each fix branch merges main in.
- **Key finding:** because each branch carries a *cherry-pick* of a614451 (merge-base 395ea53), merging any fix branch with a614451 hits add/add conflicts in tools/redteam/* (REDTEAM.md, plus the edited test file) and registry/artifacts_current.csv. This happens even for a single branch.
- **Fix:** each fix branch first merges `a614451` itself with `-X ours`. That is safe because a614451 equals the branch's own base copy of the kit. Then it regenerates the inventory. Every resulting tree was byte-identical to the branch tip, except 6b9abe8, which gains its 3 missing inventory rows. Rebasing onto a614451 (which drops the empty cherry-pick) also works.
- After that, sequential merges onto main (a614451 → A → B → C → a428c32 → 1250bbd):
  | step | conflicts | resolution | result |
  |---|---|---|---|
  | A 8583ea4 | none | – | – |
  | B b166c03 | artifacts_current.csv, REDTEAM.md (Results header count + Fix notes) | regenerate; header by hand; notes = both | CI 103 OK, RT 78 / 10 xfail, 0 unexpected |
  | C 6b9abe8 | artifacts_current.csv, REDTEAM.md (header + notes) | same | CI 103 OK, RT 87 / 10 xfail; all checkers PASS |
  | a428c32 | artifacts_current.csv, check_manifest.py (2 hunks) | combined file + testfix | CI 108 OK, RT 87 / 9 xfail |
  | 1250bbd | artifacts_current.csv, REDTEAM.md header | regenerate / ours | check_sha256sums **FAIL** (allow-list) until cleanup patch, then all PASS |
- **Final simulated main:** inventory has no diff. CI tests 108 OK. Red-team 96 tests, 7 xfail, 0 unexpected. Remaining GAPs: claims_file_missing, vocabulary_missing_skips_checks, full_scan_binary_outside_is_warning_only, token_in_text_file_over_10_mib, token_inside_binary_in_allowed_folder, axiom_with_attribute_prefix, hidden_sorry_via_admitGoal. check_manifest, lint_claims, check_sha256sums, check_current_inventory, check_artifact_pins, hygiene_scan and check_modes all PASS.
- Every step conflicts on artifacts_current.csv (it is generated, so always regenerate, never hand-merge) and on the REDTEAM.md "Results (N tests …)" header. Suggestion: drop the hard-coded count from that header, or have it generated. After the merges, REDTEAM.md also has stale line refs, e.g. "check_manifest.py (line 41)" is now line 79.
- **Recommended order:** a614451 → A → (B + a428c32 combined) → C (with its fixes) → 1250bbd plus the allow-list cleanup in the same PR. Alternatively, land 1250bbd before C, so C never ships an allow-list entry and the write-through test never exists.
