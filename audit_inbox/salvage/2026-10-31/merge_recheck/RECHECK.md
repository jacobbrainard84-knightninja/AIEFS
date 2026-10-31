# Independent re-check of `merge-prep/arena-reconciled` — final target 9053b77

Re-checked by an independent auditor seat on 2026-10-28, read-only. The scratch clone is `/workspace/merge_recheck/repo`. `/workspace/AIEFS_merge_prep` was not modified, nothing was pushed, and GitHub was only read: `main` was fetched, and is 853498f.
The verdict is for **HEAD 9053b77**. The base checks were run at 11de659. They were then folded forward through 2be5c64, e861124, 21f4f35 and 9053b77, and re-run where those commits changed anything.
Privacy items are given as file, line and type only. This report contains no tokens and no PII values.
Scripts are in `scripts/` and logs are in `logs/`. The final-HEAD logs are in `logs/ci_9053b77/`.

## 1. Verdict

**Ready to propose to the owner for merge. No required fix is outstanding.** All 8 required findings from MERGE_CHECK are fixed. Of the 9 minor findings, 8 are fixed and 1 is partial (a disclosed workaround). The Lean build passes, and only the 3 allowed axioms are used. All repo CI checks pass at 9053b77.
What is left is a set of owner decisions (§8) and a few optional small items (§7).

## 2. Researcher 001's claims (verified)

| Claim | Result | Evidence |
|---|---|---|
| Branch is based on current `main` 853498f | Confirmed. 853498f is an ancestor. The branch has 15 commits after the 103cef5 base (11 up to 11de659, then 2be5c64, e861124, 21f4f35, 9053b77). | `git merge-base` |
| Pinned files are sha256-identical to 853498f | Confirmed for HANDOFF (ART-0103), the spectrum report (ART-0343), FORWARD_PLAN (ART-0012) and the HISTORIC copy (ART-0101). They are identical in `main`, the tree and HEAD, and match the `artifacts.csv` pins. | `logs/artifact_sha_diff*` |
| Nothing on `main` was modified or deleted | Confirmed. Compared with `main`, files are only added (78 at 11de659, plus the CI files). There is no diff in `AI Agent Audits/`, `lean/` or the licence files, and `audit_manifest.json` was not re-pinned. | `logs/name_status.txt`, `logs/merged_vs_main.diff` |
| `verify_manifest.py` OK | Confirmed at 9053b77. The published check gives 145 OK, and `--inputs` gives 145+24 OK. `--inputs` must be run from the repo root; from the evidence folder it exits 2. | `logs/ci_9053b77/verify_manifest*.log` |
| Registry is consistent | Confirmed. `claims.csv` has 68 rows, 13 columns and unique IDs. There are 0 vocabulary violations across artifacts, claims, studies and relocation_map. `validate_registry --write` gives 2703 same / 5 changed (all edits made on `main`) / 52 deleted on main; relocation is 214/3/4. `--write` produced **no diff** to the committed CSVs. | `logs/ci_9053b77/vocab_check.log`, `validate_registry_write.log` |
| The 9 CI files are byte-identical to `/workspace/autonomy_setup/out/` | **Confirmed at 9053b77, 9 of 9 MATCH.** These include `hygiene_scan.py` 42ce59dd… and `test_ci_tools.py` ddf9b7b9… At 21f4f35 those two files matched the original out/ versions (d295ad8d…, dcc3271e…), as expected. | `logs/ci_files_identity_9053b77.log` |
| `lean.yml` unchanged vs `main` | Confirmed: empty diff. | — |
| 9053b77 touches only the 2 CI files | Confirmed: +56/−4 lines, `hygiene_scan.py` and `tests/test_ci_tools.py` only. Since 11de659 there are no `.lean`, lakefile, manifest or toolchain changes, so **Lean was not rebuilt again**. | `git diff --stat` |
| `CURRENT_STATUS.md` §4 is accurate | Accurate. Every claim ID cited exists, and the numbers match the audit sources (c=0.6333, rate-law values, SCOPE 1 of 40, …). It has 0 private-literal matches and 0 occurrences of the GitHub username. | `logs/ci_9053b77/private_literals_new_files.log` |

`verify_inventory.py` still stops at step [1/5]: it is called without its root argument, so `sys.argv[1]` raises IndexError. This was already the case and is not caused by this branch.

## 3. MERGE_CHECK findings

### Required (8)

| # | Finding | Status | Evidence |
|---|---|---|---|
| 1 | Pinned files had been edited | **Fixed** | All 4 pins match 853498f (§2) |
| 2 | AUD-KAPPA-TW wording | **Fixed** | Per-k form; by_k = {2:1, 3:88, 4:24, 5:179}, which matches the JSON |
| 3 | AUD-RATELAW wording | **Fixed** | Conditions (a)–(e), ker A_J, closed form, bounds 264/110/32, and the unexplained ~2e-8 gap are all stated as in resp3 |
| 4 | EMP-AIEF14-02 "mediates" | **Fixed** | "Mediates" is dropped and the P_mean_late sign is negative. It is now Exploratory / Finite numerical observation, with the qualifier "controlled exploratory…" |
| 5 | AUD-SLOWPOLE | **Fixed** | Audited Quarantined, artifact Rejected, and no reference to the missing report |
| 6 | Dangling references | **Fixed** | No `reconciliation/lineage_reconciliation` path remains, and every `MERGE_PREP_REPORT.md` reference resolves |
| 7 | REPRODUCING.md Lean section | **Fixed** | v4.33.1, 6 modules plus the root, check_lean in 7 steps, 115 declarations. The "144 conditional DID" figure is removed. Nit: the header says "see the note there for whether it was re-run", but §7 has no such note |
| 8 | PRIVACY_SCRUB_LIST corrections | **Fixed** | P4 now reads 40 personal / 2 generic, with files and lines matching my scan. All nine Q7 items are added (P8, P9, C8, C9, ORCID, street address, terminal prompt, device type, MMS email). I spot-checked the INVENTORY line citations and all are correct; the MMS email is at text line 4309, p.133, as stated. The list has 0 email-like strings and 0 private literals |

### Minor (9)

| # | Finding | Status |
|---|---|---|
| 1 | B2A95 6.7e-16 | Fixed |
| 2 | FROZEN-TOPO | Fixed |
| 3 | CF02 "gated" | Fixed |
| 4 | AUD-LABEL scope | **Partial**. The scope is "Finite numerical observation", disclosed as a workaround because the vocabulary has no value for labelling. Acceptable |
| 5 | LEAN-R4 row | Fixed |
| 6 | AUD-HELDOUT-LABEL and AUD-CYCLE-KERNEL rows | Fixed |
| 7 | Device name in claims | Fixed. Now "a second Linux host"; audit_source is resp2 line 146 |
| 8 | Not-inventoried count | Fixed as of the time it was written: README says 252. **At 9053b77 the true count is 261** (the 9 new CI files are not inventoried), so it is now slightly stale. Optional update |
| 9 | requirements.txt | Fixed. Exact pins with provenance; it states the version differences (pytest 9.1.1 vs 9.2.0, and the B2A95 log's numpy/pandas) |

## 4. Label judgments

- **AUD-SLOWPOLE, Rejected + Quarantined.** Consistent: Rejected is defined as "methodologically invalid".
- **EMP-AIEF14-02/03, Finite numerical observation.** Conservative and acceptable. However, the Axis-2 definition of "Controlled experimental result" explicitly names the matched-phase and T_window studies, so either value can be defended. Owner choice; not a blocker. The clean fix would be a new scope value.
- **AUD-LABEL.** Acceptable as a disclosed workaround (see minor #4).
- **SSRH-ORIG-01…07 (currently Incomplete / Speculative… / Conjecture). Recommendation: set `artifact_status` to `Exploratory`, not to 'Speculative / untested origin hypothesis'.**
  - Incomplete means an "aborted/partial execution artifact", which these rows are not.
  - Axis-1 Exploratory explicitly covers "historical origin scan", and the earlier study row was Exploratory/Conjecture.
  - 'Speculative…' is not in `verify_inventory.py`'s 7-value VALID_STATUS. Using it in `artifact_status` would fail check [3/5], even though `lint_claims.py` would pass.
  - Keep `audited_status` = 'Speculative / untested origin hypothesis' and evidence_scope = Conjecture. This keeps to the owner rule: the rows are not retired, and each row already says what would test it.
- **Vocabulary gap to note.** `lint_claims.py` / `claim_statuses.txt` accept all 14 statuses in `artifact_status`, but `verify_inventory.py` accepts only 7. `evidence_scope` is not linted by CI. Suggest that lint_claims check `artifact_status` against the 7 values and also lint `evidence_scope`.
- The top note in registry/README says Quarantined is something "the vocabulary lacks". That is stale: Quarantined is missing only from the artifact_status axis.

## 5. Lean (built at 11de659; no Lean inputs changed through 9053b77)

`check_lean.sh` passed all 7 steps:
1. Toolchain v4.33.1.
2. Mathlib pin 0df444a… OK.
3. 8 source hashes OK.
4. Imports OK.
5. `lake exe cache get`: 8690 files already decompressed, about 66 s.
6. Clean build: 8713 jobs, **0 errors**, 12 lint warnings (doc-string style in Smoke.lean).
7. sorry/admit/axiom markers: 0 in 7 files.

The axiom audit covered **115 project declarations**. I parsed its output independently: 115 AXIOMS entries and 67 `#print axioms` lines. The union of axioms is exactly **{propext, Classical.choice, Quot.sound}**, so there are no disallowed axioms. Logs: `logs/lean/`, `logs/lean_check_lean.out`.

## 6. CI tools at 9053b77 (Python 3.13.5)

| Check | Result |
|---|---|
| `lint_claims.py` | 68 rows, 0 violations, PASS |
| `check_manifest.py` | 1 verifier, 145+24 OK, PASS |
| `unittest` / `pytest tools/ci/tests` | **18 tests OK** (15 at 21f4f35, plus 3 new), 18 passed |
| `hygiene_scan.py --base 853498f --pii` | 0 errors, 0 warnings, PASS |
| `hygiene_scan.py` (full) | 0 errors, 3 BIG_FILE warnings (3 trajectory CSVs of 51–64 MiB), PASS; 21.7 s |
| `hygiene_scan.py --pii` (full, default 10 MiB limit) | 0 errors, 3 BIG_FILE warnings, **0 PII warnings**. The 5 false positives seen at 21f4f35 (matmul `@` and reserved domains) are now suppressed. 28.2 s. 30 text files over 10 MiB were only size-checked |
| **`hygiene_scan.py --pii --max-scan-mb 1000` (full, covers all files)** | **0 PII hits, 0 errors, 3 BIG_FILE warnings, PASS; 168.2 s** (the largest tracked file is 63.5 MiB, and no "size-checked only" note was printed) |

**Recommendation on the CI limit:**
- The PR/push job runs `--pii` only with `--base`, so it scans changed files. Raise `--max-scan-mb` there to about 100, so that a large text file added in a PR is content-scanned. This costs little because only changed files are read.
- Do not add a full-tree `--pii` job to every push, because it takes about 3 minutes. If one is wanted, run it on a schedule or by manual dispatch with `--max-scan-mb 100`.

**Small hardening note on the new email filter (warn-only, not a blocker).** I tested it with synthetic addresses:
- It skips addresses whose domain starts with `np.`, `sp.`, `la.`, `sm.` and similar (for example a `…@la.gov` or `…@sm.<university>.edu` form).
- It also skips any address that is immediately followed by `(` or `[`.

Suggestion: require **both** conditions (a matmul-module prefix **and** a following `(` or `[`, or a known numpy function name) before treating a match as a matmul.

## 7. Privacy, at 9053b77 vs `main` (file, line, type only)

The home-path and IPv4 findings below are unchanged since 11de659. The new files (the CI files, CURRENT_STATUS, OPERATING_MANUAL, PRIVACY_SCRUB_LIST, docs/REVIEWING) have 0 private-literal matches.

| File | Lines | Type | Pinned? | Audit input? | Recommendation |
|---|---|---|---|---|---|
| audits/engineering/PATH_AND_LOCK_DEPENDENCY_AUDIT.md | 32, 34, 35 | home path, personal username | No | No | Leave while on hold; scrub with a placeholder if the hold is lifted |
| audits/engineering/python_path_dependencies.csv | 3, 4, 7, 8, 140 (13 hits) | home path, personal | No | No | Same |
| audits/github_reconciliation/GITHUB_TREE_AND_ZIP_RECONCILIATION.md | 49–52 | home path, personal | No | No | Same |
| audits/github_reconciliation/zip_vs_tree_comparison.csv | 70, 71, 73, 74 | home path, personal | No (the CSV itself is not pinned) | No | Same |
| registry/artifacts.csv | 2830, 2831, 2833, 2834 (notes column) | home path, personal | No | No | Same. Scrubbing the notes column does not break any pin |
| …/diffs_vs_root/AIEF_1_3_closure_diagnostics.py.diff | 7, 8, 14, 15 | home path, personal | No | No (derived from the pinned zip) | Leave; or annotate/regenerate if the hold is lifted |
| …/diffs_vs_root/AIEF_1_3_closure_diagnostics_updated.py.diff | 7, 8, 14, 15 | home path, personal | No | No | Same |
| …/diffs_vs_root/AIEF_1_3_paired_statistics.py.diff | 7, 12 | home path, personal | No | No | Same |
| …/diffs_vs_root/AIEF_1_3_paired_statistics_updated.py.diff | 7, 12 | home path, personal | No | No | Same |
| audits/scientific/revalidated_summaries/aief_1_3_disjoint_100seed_analysis_manifest.json | 8, 14 | home path, **generic sandbox user** | No | No | Leave |
| zip_only_files/uploads/Results.pdf | raw lines 579, 582 | IPv4-like pattern | **Yes** (PROVENANCE.json, zip_vs_tree_comparison.csv, artifacts.csv) | — | **False positive.** It is the PDF Producer version string, with 0 hits in the extracted text. Leave it; scrubbing would break the pins |

In total there are 42 home paths in 10 files plus 1 manifest (40 personal, 2 generic), and 2 IPv4 hits that are false positives. There are no emails, phone numbers or other private literals. None of these hits are inside AI-bot conversation material. All of them are already listed in PRIVACY_SCRUB_LIST P4.
`main` already has about 290–380 home-path occurrences, and git history keeps every one of them. Real removal needs the owner's history-rewrite decision, so errata are not needed for these.

Optional small items:
- The REPRODUCING header nit (§3 required #7).
- The not-inventoried count, now 261.
- The EMP-AIEF14-01 paraphrase in CURRENT_STATUS §4 ("rebuilds almost identically") could use the audit wording from resp2 #4.
- CURRENT_STATUS:46 cites 3 scripts that do not exist. This text was already there (arena) and was not introduced by this branch.
- §4 says Lean was "not re-run in this session". This re-check has now re-run it, and it passes.

## 8. Owner decisions remaining

1. The privacy scrub and git history rewrite (on hold). This covers the 40 personal home paths above, and P1/P2/C1/C6 and the Gmail commit metadata in PRIVACY_SCRUB_LIST.
2. The "All rights reserved" headers in Apache-2.0 Lean files (C7).
3. The SSRH `artifact_status`: Exploratory recommended (§4).
4. Whether to add an evidence_scope value for exploratory designs and for labelling, and whether to have CI lint `artifact_status` (7 values) and `evidence_scope`.
5. Fixing the `verify_inventory.py` [1/5] argv call, and whether to inventory the 261 untracked-in-registry files (including the 9 CI files).
6. The `--max-scan-mb` setting for CI (§6), and the email-filter hardening.
7. AUD-NOVELTY handling (unchanged).
8. Re-authoring the "Researcher 001 (local)" commits before any push, and the push/merge itself.

---

## 9. Follow-up re-check at HEAD 886daf6 (2026-10-28, evening, America/Toronto)

Scope: commits bdef1e6, e152397, d43d757 and 886daf6 on top of 9053b77, with 12 files changed. I worked read-only in the scratch clone `/workspace/merge_recheck/repo`. The tree was clean before and after every check, and every temporary write was reverted. Nothing was pushed, and the original folder was not touched. Logs are in `logs/lean886/`, `logs/ci_886daf6/`, `logs/d43d757_math.log` and `logs/ratelaw_gap_vs_delta.log`.

### 9.1 Lean (`check_lean.sh` with the Mathlib cache, clean project build, about 62 s)
- **RESULT: PASS. All 7 steps passed.** The run was at git HEAD 886daf6 with 0 dirty files.
- **Declarations and axioms:** 115 project declarations were audited. The union of axioms, which I parsed myself from the axiom log, is exactly {propext, Classical.choice, Quot.sound}. `7_axioms_summary.txt` is byte-identical to the earlier 11de659 run.
- **Warnings:** 0 now, down from 12. All 12 earlier warnings were in `Smoke.lean` and none remain.
- **Build jobs:** 1,591, down from 8,713. `Smoke.lean` no longer imports all of Mathlib.
- **Marker scan:** 7 files, 0 hits.
- **Source diff:** `Smoke.lean` and `Basic.lean` changed only in their header, SPDX line, module docstring and imports. The proofs are unchanged.
- **`sha256sum -c AIEF_LEAN_SOURCE_SHA256SUMS.txt`:** 8 of 8 OK.
- **audit_manifest pins:** `verify_manifest.py` passes, both published and with `--inputs`. Its Lean inputs (`AIEFProofs.lean`, `ControllerFiber.lean`, `lean-toolchain`, `lake-manifest.json`) all match.
- **Header wording (closing C7):** all 6 module files and the recovery copies carry the standard Mathlib header ("Copyright (c) … All rights reserved. Released under Apache 2.0 license as described in the file LICENSE."). This is not a licence conflict, so closing C7 is reasonable. The two new headers use the same copyright line as the existing ones and contain 0 private literals.

### 9.2 Engine claim behind the rate-law gap (e152397): **verified, and the wording is accurate**
I checked the order of operations in `aief_experiment_engine_v1.py`. This is the pinned copy (`ca4593fd…`), which is also the one the audit scripts import.
- `compute_R` reads only θ, the delayed history and the coherence EMA (:721–752; EMA at :743–745). It never reads B.
- R is computed at :779, before the B proposal (:790–797), the gate projection (:803–813) and `state.B =` (:823).
- B is used only afterwards, in the θ coupling (:830–839).

So a one-step, B-only perturbation (`step_B`, kappa_cycle_kernel.py:52–57) cannot change R within that step. Ruling out "R depends on B within a step" is therefore correct.

AUD-RATELAW still says the ~2e-8 gap is unexplained and lists the remaining candidates. It is not overstated.

**Optional (non-blocking) suggestions:**
1. My own split of the census residuals points to finite-difference rounding:
   - The 2.04e-8 maximum comes from a single component whose step δ lies in [1e-9, 1e-8).
   - The other 263 well-resolved components (δ ≥ 1e-6) agree to ≤ 2.1e-10, with a median of 6.3e-13.
   - Error × δ is roughly constant (median ~6e-18), which fits rounding that scales as 1/δ.
   
   A one-line note, plus a δ sweep to confirm it, would help. It should not be stated as a claim until that sweep is run.
2. Two of the listed candidates are weaker than the text implies:
   - Response 3 already says the gap is "the same against the state formula as against the closed form", which argues against "finite-time departure".
   - The spread of s on J is 8.5e-10, which is far too small to produce a 2e-8 gap ("unequal controlling scales").
   
   The researcher could rank these as unlikely.

### 9.3 d43d757 (renaming the cycle kernel)
- **Dimension claim: correct.** For the unsigned incidence matrix of a connected graph, the rank is n (non-bipartite) or n−1 (bipartite). So the kernel dimension is m−n or m−n+1. Every K_n with n ≥ 3 is non-bipartite, so dim K = m−n = n(n−3)/2. I checked K3=0, K4=2, K5=5 and K6=9 numerically. Bipartite checks gave C4=1 and K2,3=2, which equal m−n+1.
  - The oriented incidence kernel (the true cycle space) has dimension m−n+1. The K4 comparison "2 vs 3" is correct.
  - The documents state the condition ("non-bipartite K_n"). That is redundant for K_n with n ≥ 3, but correct.
  - Scope: the claim applies to an all-tied complete graph. For a proper controller set J, dim = m − rank(A_J). The docs do not claim more than this.
- **K4 counterexample (AUD-TIES): valid.** I reproduced nonadditivity 0.2003 against the ideal 0.2887, and an odd-cycle defect of 0.7254 against the ideal 0.7071, for h1 = (0,1) and h2 = (0,2). Two minor caveats, both optional to add:
  - The figures depend on which pair of adjacent edges is chosen. Other pairs give 0.2627 / 0.7254 and 0.3046 / 0.7140.
  - The unequal state is not a fixed point of the ideal R = 1 gate (its maximum one-step change is 2e-4).
  
  This means it is a valid counterexample to universality, but not a fixed-point counterexample. The sentence "for K3, equal row sums force equal edges" is correct.
- **966-dimension limits (AUD-SLOWPOLE): accurate.** All 5 stated limits match `full_state_spectrum.json`: B-block 0.4993689, h = 1e-7, T = 500, 10 gap rates, dimension 966.
- **Dangling references: none.** "Cycle kernel" remains only in the pinned audit files, the claim ID, the script and file names (which are kept on purpose), and the docstring at `CompleteGraphIncidence.lean:141`. E6 covers all of these.

### 9.4 CI and registry
- **CI checks:**
  - `lint_claims`: PASS, with 0/0/0.
  - `check_manifest`: PASS.
  - Unit tests: 18/18 OK.
  - Hygiene, full tree with `--pii`: PASS in 28 s. The only output is the same 3 BIG_FILE warnings as before.
  - Hygiene `--base 853498f --pii`: PASS.
- **Other checks:**
  - `verify_manifest`, published and `--inputs`: both OK.
  - `check_citations`: 0 blank or out-of-range cited lines. It needs the repo root as an argument.
  - Vocabulary check: 0 violations.
  - `build_claims_reconciliation.py` regenerates `claims.csv` byte-identically, so it is idempotent.
- **Stale-hash rows:** `validate_registry_against_tree.py` now reports 2,701 same SHA and 7 changed SHA, up from 5 changed. The two new changed rows are ART-0744 (Basic.lean) and ART-0746 (Smoke.lean).
  - Keeping the e47bad1 hashes in the `sha256` column is acceptable. The column is a snapshot, and E7 says so.
  - **However, the committed `tree_check_2026_10_28` flag on those two rows still reads PRESENT_SAME_SHA.** That is now false: `--write` flips both rows to PRESENT_CHANGED_SHA (the change was tested and reverted).
  - `MERGE_PREP_REPORT.md:136` still says "2703 same SHA, 5 changed SHA".
  
  This is small, but the registry should not state a check result that the tree contradicts.

### 9.5 Privacy (9053b77..886daf6)
- `hygiene_scan.py --base 9053b77 --pii`: 12 files scanned, 0 errors, 0 warnings, PASS.
- Private-literal matches, counted file by file across the 12 changed files: 0 in every file.

### 9.6 Verdict for 886daf6
**Ready to push as the review branch once two small documentation and registry fixes are made.** None of them changes code, maths or proofs.

Required:
1. **Registry flags:** run `validate_registry_against_tree.py --write` so ART-0744 and ART-0746 read PRESENT_CHANGED_SHA. Then update the count to "2,701 same / 7 changed" in `MERGE_PREP_REPORT.md:136`, and anywhere else the 2,703/5 figures appear. E7 could add one line saying the flag now reflects the edit.
2. **Lean compile status:** E7 (ERRATA:124, "not compiled"), REPRODUCING §7 (line 106, "has not been compiled yet … Auditor Seat 002 is to re-run"), and the 12-warnings line should record this run instead. The new result is: 886daf6, cached Mathlib, PASS 7/7, 115 declarations, only the 3 allowed axioms, 0 warnings, 1,591 jobs.
   - Optional precision: the earlier Seat 002 run was at 11de659, and the Lean sources were identical through 9053b77.

Optional: `MERGE_PREP_REPORT.md:140` records Researcher 001's own uncached run (`SKIP_CACHE=1`) as "Incomplete". That is accurate history, but a pointer to the passing cached run would help.

Also optional: the rate-law notes in 9.2 and the K4 caveats in 9.3.
