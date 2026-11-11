# MERGE_CHECK — independent audit of Researcher 001's AIEFS merge-prep

- Checked: `/workspace/AIEFS_merge_prep`. HEAD is **`103cef5`** on `merge-prep/arena-reconciled`, read-only. Its HEAD, branch and clean status were confirmed unchanged at the end of this check.
  - The brief named HEAD `96f1144` with 13 commits. `96f1144` is not an object in the repo.
  - The actual history is: arena `7edbab2`, then merge `ce8cced`, then 12 merge-prep commits (`4b09647` … `103cef5`). That is 14 commits after `main` (`853498f`).
- Work copy: `/workspace/merge_check/tree`, a clone. Scripts are in `scripts/` and logs in `logs/`.
- Nothing was pushed and GitHub was not touched.
- The private-literal file was used only as a local scan input. Only counts are reported here.

## Overall verdict: **READY AFTER 8 REQUIRED FIXES** (plus 9 minor fixes)

The registry is solid and well sourced:
- Every "(line N)" citation in `claims.csv` resolves to the right line (`logs/check_citations.log`, 0 bad).
- The relocation_map statuses are correct.
- REPRODUCING §3–§5 reproduce exactly.
- There are no deletions, no changes to `AI Agent Audits/`, `lean/` or the licence files, and no secrets.

The blockers:
- 4 hash pins are broken by inline edits. As a result, `verify_manifest --inputs` FAILS, and several audit line citations have shifted.
- A few ledger statements are mis-stated.
- Two files are referenced but do not exist.
- The Lean section of REPRODUCING is stale.
- The privacy scrub list has gaps.

### Required fixes
1. **Undo the inline edits to audit inputs (Q6).**
   - Revert the edits to `AI_AGENT_HANDOFF_PROMPT.md` and `aief_1_4_augmented_spectrum/augmented_spectrum_report.txt`. Preferably also revert `AIEF_1_4_FORWARD_PLAN.md` and `AIEF_HISTORIC_UNFOLDING.md`.
   - Move the dated caveats into a sidecar errata file, e.g. `ERRATA_2026-10-28.md`, and the claims ledger.
   - This restores `verify_manifest --inputs`, `artifacts.csv` ART-0012/0101/0103/0343, and `zip_vs_tree_comparison.csv` IDENTICAL_TO_WORKTREE.
   - It also fixes the shifted `AIEFS_audit.md` citations: HANDOFF :152, :327 and :495 are currently off by 2 lines.
2. **AUD-KAPPA-TW**: rewrite the statement (see the table below).
3. **AUD-RATELAW**: add condition (e) and ker A_J, give the true conditional closed form, and state both bound sets plus the unexplained ~2e-8 residual.
4. **EMP-AIEF14-02**:
   - Drop "mediates".
   - Change evidence_scope from "Controlled experimental result" to "Controlled exploratory analysis with fixed recorded design".
   - State in the statement that P_mean_late is negative.
5. **AUD-SLOWPOLE**: change artifact_status `Superseded` to `Quarantined`, or explain the mismatch with audited_status. Remove the reference to the nonexistent `MERGE_PREP_REPORT.md`.
6. **Dangling references**:
   - `MERGE_PREP_REPORT.md` does not exist. It is cited in README.md:82, in claims AUD-SLOWPOLE, and in `build_claims_reconciliation.py:144`. Add the file or remove the references.
   - `registry/reconciliation/lineage_reconciliation.csv` should be `registry/lineage_reconciliation.csv`. Fix it in CURRENT_STATUS.md:8, README.md:18 and registry/README.md:61.
7. **REPRODUCING.md**:
   - §7 says toolchain `v4.29.0-rc8` and 3 modules. The actual toolchain is `leanprover/lean4:v4.33.1`, with 6 modules plus `AIEFProofs.lean` and `check_lean.sh` (lean_r4 logs).
   - §2's arena text ("2,760 tracked files … 12 Lean lock hashes") is stale.
   - The "144 conditional DID rows" figure is not produced by any v4 output CSV. Remove it or point to its source.
8. **PRIVACY_SCRUB_LIST.md**: add the missing items (Q7) and fix the INVENTORY line citations, which are off by about 2 lines throughout.

### Minor fixes
1. AUD-REPRO-B2A95: give the observed maximum difference, 6.7e-16, not just the 1e-12 tolerance.
2. AUD-FROZEN-TOPO: add "0 nonbinary P_future, 0 label differences".
3. CF02: replace "projected output" with "gated (node-strength-normalised) output".
4. AUD-LABEL: evidence_scope "Implementation identity" should be a labelling or policy scope.
5. LEAN-CF-01: understated. Add a row, or extend this one, for the round-4 Lean package (v4.33.1, 115 declarations, only standard axioms).
6. Add ledger rows for held-out label identity (resp2 #6) and for the cycle-kernel multiplier replacing the "Jacobian" (kernel dimension n(n−3)/2).
7. Remove the personal device name from IMPL-MODULAR-01. Its audit_source text "test-count mismatch only" really refers to resp2 §7 item 2: "output not saved" (line 146).
8. README says 248 files are not inventoried; the validator finds 249.
9. requirements.txt:
   - It does not mention that the archived b2a95 reproduction ran on numpy 2.5.4 / pandas 3.0.6 (`compare_b2a95dfbfbe3.log:1`).
   - ENVIRONMENT.md lists pytest 9.1.1. The difference is disclosed, but say "9.2.0 verified, 9.1.1 audit".

## Q1 — claims.csv (65 rows) vs the audit records

All cited file:line references resolve (`scripts/check_citations.py`). Discrepancies:

| claim | current text (abridged) | problem | correct status / wording | evidence |
|---|---|---|---|---|
| AUD-KAPPA-TW | "κ(T_w) = 2η/c − 1/T_w (0.069182 at T_w=17.503) matches the discrete rate within 5.3e-6 over 292 slow components" | **Mis-stated.** The 292 components span k=2–5 ({2:1, 3:88, 4:24, 5:179}). The formula is per k (kη/c − 1/T_w; discrete λ_k form). 0.069182 is the k=2 value, which applies only to the single exceptional K3. | Supported (conditional). "κ_k(T_w) = kη/c − 1/T_w per component (k = 2…5); matches the discrete λ_k within 5.3e-6 over 292 components / 200 replays; within 4.5e-4 of the continuous form". Also note the tighter resp3 bounds. | `evidence/results/kappa_tw_summary.json`; resp3 §2.2 (lines 41–63) |
| AUD-RATELAW | "Exact one-step law λ=(1−γdt)s_J … closed form κ = kη/c − 1/T_w is conditional (R=1, row sum c)" | **Overstated.** It omits condition (e), equal controlling scales, and h ∈ ker A_J. The real closed form is λ_k = (1−γdt)c/(c+dt(kη−γc)+ε); kη/c − 1/T_w is only its limit. It gives no bounds. | Supported (conditional theorem). Add the conditions and the bounds: 264 two-sided λ 2.07e-8 / κ 2.07e-6; 110 K3 one-sided rays λ 1.7e-7 / κ 1.7e-5; 32 poorly resolved (ρ=2) 4.8e-6 / 4.8e-4; the ~2e-8 gap is unexplained (ε contributes only 1.6e-12). | resp3 lines 22–23, 41–63 |
| EMP-AIEF14-02 | "delayed phase/EMA history **mediates** post-ablation topological recovery"; evidence_scope "Controlled experimental result" | **Overstated.** The language is causal, and the scope contradicts artifact_status Exploratory. | Exploratory: "controlled exploratory analysis with fixed recorded design". Weighted_similarity_late +0.064 [0.041, 0.089] (31/40); P_mean_late −0.018 [−0.027, −0.009]; Retention CI spans 0. | resp2 #3 (line 17), #7 (line 21); `evidence/results/matched_phase_check.json` |
| AUD-SLOWPOLE | artifact_status `Superseded`; note: "Reusing scripts listed in MERGE_PREP_REPORT.md §5" | **Internally inconsistent**, and cites a missing file. | Quarantined (see Q4). | resp3 line 29, line 94 (§2.5), lines 105, 112 |
| AUD-REPRO-B2A95 | "float fields within 1e-12" | **Understated.** 1e-12 is the tolerance; the observed maximum is 6.7e-16. | Supported: "max abs diff 6.7e-16 (tolerance 1e-12), at 6b49a7b". | `evidence/reproductions/b2a95dfbfbe3_REPRODUCTION.md` lines 7, 63 |
| AUD-FROZEN-TOPO | "0 of 29,040 edges change threshold status (P_future also tested)" | Minor understatement. | Add "0 nonbinary P_future, 0 label differences". | resp3 #4 (line 25); `frozen_topology_check.json` |
| CF02 | "strictly interior in the **projected** output" | Uses projection language the audit retired (the row's own note says so). | Supported: "gated output". | resp2 #1 (line 15); resp3 #5 (line 26) |
| AUD-LABEL | evidence_scope "Implementation identity" | Wrong scope vocabulary. | Supported (labelling rule). | resp2 #7 (line 21) |
| LEAN-CF-01 | 2×3 kernel only | **Understated / incomplete.** The round-4 Lean package (v4.33.1, 6 modules, standard axioms) has no row. | Keep the row; add LEAN-R4 (Supported, formalized). | `evidence/logs/lean_r4/summary.txt` |
| IMPL-MODULAR-01 | caveat names a personal device; audit_source "test-count mismatch only" | PII (P5); slight mis-cite. | See Q2. | resp2 line 146 |
| AUD-CORR-0995 | statement wording | Accurate but incomplete. | See Q5. | salvage line 96, §3.1 lines 108–117; resp1 lines 15, 42 |
| (missing) | — | No row for held-out label identity, or for the cycle-kernel multiplier replacing the "Jacobian". | Add both as Supported (audit-derived). | resp2 #6, §2.3 |

The other 53 rows were checked and agree with the audit records:
- EMP-AIEF13-01/02 and EMP-AIEF14-01
- CF06
- S01–S18
- REJ-* (5 rows)
- AUD-TOPO-OMEGA, AUD-GATE, AUD-SCOPE-1.4, AUD-DELAY, AUD-K3, AUD-TIES, AUD-REPRO13, AUD-NOVELTY
- the 13 decision rows and 7 SSRH rows, as recorded; verdicts are in Q2

## Q2 — the 20 decision rows

| row | recommended verdict | reason |
|---|---|---|
| CF01, CF03, CF04, CF07, CF08, CF09 | Supported (conditional linear algebra, single exceptional seed; not independently re-derived by audit) | These are algebraic or structural statements consistent with the audit's gate/K3 analysis, but no audit re-derived them line by line. |
| CF05 | Finite numerical observation, single seed (not re-checked); do not label Frozen | The winner map (7,2,7) is a single-replay fact that LEAN-CF-01 depends on. |
| CF10 | Finite numerical observation, single seed (not re-checked) | Same reasoning; it is a numerical observation, not a frozen result. |
| CF11, CF12 | Conjecture / Exploratory (keep) | No proof or test in the repo. |
| CAVEAT-MS-8.4 | Accept as arena's own caveat (Exploratory / Caveat, not audited) | It narrows an earlier claim, and nothing in the audits contradicts it. |
| EMP-AIEF14-03 | Controlled exploratory (DID not tested by audit); not Frozen | Same exploratory-label rule as EMP-AIEF14-02 (resp2 #3, #7). |
| IMPL-MODULAR-01 | Supported – implementation identity, not re-tested by the audit; scrub the device name | Tests pass (41/1 re-run here), but the 344-array identity was not re-run. The device name is PII P5. |
| SSRH-ORIG-01 … 07 | Retired / Unsupported – no data, script or analysis in repo; do not cite | The audits never adjudicated them, and the repo holds nothing that could support them. |

## Q3 — matched-phase status

**Exploratory (the audit's verdict). Arena's "Frozen / Controlled" is wrong.**
- resp2 #3 (line 17): "It stays exploratory."
- resp2 #7 (line 21): label it "controlled exploratory analysis with fixed recorded design".
- The audit's own re-run (`matched_phase_check.json`) shows P_mean_late is *negative* and the Retention CI spans 0. "Mediates" is therefore not supported.
- The ledger's artifact_status is already correct. Only the statement and evidence_scope need fixing (Required fix 4).

## Q4 — "unique slow pole"

**Quarantined is correct; `Superseded` in artifact_status is not.** The 18-coordinate map is not a closed state: `restore_state` omits θ (resp3 §2.5, line 94). So the original claim is not merely replaced by a later result; it was invalidly derived.

Most accurate label: **"Quarantined — invalid derivation (18-coordinate map is not a closed state); do not cite. Audit proposal on the closed 966-dim state (one replay, finite-difference, not a proof) gives NO: 10 gap rates."** The source of the "proposal" wording is resp3 line 105.

## Q5 — 0.995 caveat wording

The current wording's numbers and quotes are accurate:
- uniform 0.711 / 0.712 and clustered 0.588 / 0.634 (salvage lines 114–117)
- the verdict quotes (resp1 line 42, salvage line 96)

But:
- "holds … only" is loose.
- It omits the scope of the random draws (20 + 20 at N=12).
- It omits that past R beats Δω-only at the repo ω but is worse on clustered ω.
- It omits that the correlations are point-biserial.

Proposed replacement, for the sidecar errata and the AUD-CORR-0995 statement:

> **Caveat on Corr_physical ≈ 0.995 (2026-10-28; number unchanged).** The value is specific to the repository's hand-picked natural frequencies. In the audit's replays with random frequencies (N = 12; 20 uniform U(1,2) draws and 20 clustered draws), Corr_physical falls to about 0.71 (uniform) and 0.59–0.63 (clustered). Because P_future is binary, these are point-biserial correlations. The audit's verdict is "not a tautology, but dominated by persistence", valid on the chosen ω only. At the repository ω, past R beats a Δω-only predictor on held-out seeds (AUC 0.999995 vs 0.972). On clustered ω it does worse (AUC 0.457 vs 0.652). Sources: AIEFS_salvage.md §3 row 2 (line 96) and §3.1 (lines 108–117); AIEFS_audit_response.md ledger #2 (line 15) and §3 item 3 (line 42); AIEFS_audit_response_2.md #6; ledger row AUD-CORR-0995.

## Q6 — hash pins

There are 4 broken pins in `registry/artifacts.csv`. All four files were edited by merge-prep after the merge:

| file | artifacts.csv row | old hash also recorded in |
|---|---|---|
| `AIEF_1_4_FORWARD_PLAN.md` | ART-0012 | `recovered_from_workspace_019ff402/zip_only_files/AIEF_1_4_lineage_freeze_manifest.json`; `zip_vs_tree_comparison.csv` (IDENTICAL_TO_WORKTREE is now false) |
| `AIEF_HISTORIC_UNFOLDING.md` | ART-0101 | same as above |
| `AI_AGENT_HANDOFF_PROMPT.md` | ART-0103 | **`AI Agent Audits/evidence/audit_manifest.json` inputs_sha256 (line 23)**; `PROVENANCE.json:126` |
| `aief_1_4_augmented_spectrum/augmented_spectrum_report.txt` | ART-0343 | **`audit_manifest.json` line 36** |

The other 5 changed rows in artifacts.csv are main's own legitimate changes.

- `verify_manifest.py`: the published check is OK. **`--inputs` FAILS** on 2 inputs, HANDOFF and the spectrum report (`logs/verify_manifest_inputs_merged.log`). It passes on main (`logs/verify_manifest_inputs_main.log`).
- The HANDOFF insert, 2 lines after line 117, also shifts the `AIEFS_audit.md` citations:
  - HANDOFF:152 is now at 154 (cited at audit.md lines 67 and 113).
  - :327 is now at 329 (cited at line 121).
  - :495 is now at 497 (cited at line 111).
  - The range :112-146 (line 54) is slightly affected.
- **Recommendation: a sidecar errata file, not a re-pin.**
  - Re-pinning `audit_manifest.json` would edit the audit folder and break its own record of what the audit actually read.
  - Revert all 4 files to their pinned bytes. Put the caveats in `ERRATA_2026-10-28.md`, which is referenced from README/CURRENT_STATUS and the claims rows.
  - If the owner wants the notes inline in FORWARD_PLAN/HISTORIC (not audit inputs), re-pin only ART-0012/0101 with a dated note. Leave the historical zip-comparison records as they are.

## Q7 — PRIVACY_SCRUB_LIST vs license_inventory and review_6b49a7b hygiene_scan

Verified correct:
- P1 pages
- P5 locations: device-name lines match exactly
- P6 `artifacts.py:315` and `runner.py:244`
- P4 arena-merged files and lines: matches my diff scan, 11 files and 42 occurrences
- 292 home-path occurrences in tracked text
- §4: 119 of 128 main commits carry the personal Gmail
- M1 and M2 members exist

**Missing** (present in the sources, absent from the list):
1. `Project Origins/Origin Document 02.pdf`: personal context (occupation, background, device type), ~7 hits at text lines ~10046–10152. Source: hygiene_scan `personal_context` and REVIEW.md line 90.
2. Device type in `Origin Document 01.pdf` (10 hits) and `Origin Document 02.pdf` (20 hits). These belong in P5.
3. The device-default terminal prompt and home path, 40 times in `Origin Document 02.pdf` (~7928–13243). These belong in P4.
4. `Origin Document.pdf`: 1 email at text line ~4266, from the author block of the pasted MMS article. This belongs in P3.
5. Third-party material missing from §2:
   - the pasted MMS foreshock article at the end of `Origin Document.pdf`
   - the YouTube transcript in `Origin Document 02.pdf` (~10238–10580)
   - Source: REVIEW.md §Hygiene.
6. ORCID iDs in `SSRH 001 stuff.pdf` p.647:4–5 (INVENTORY line 74). P3 does not mention ORCIDs.
7. The street address in `grok ice 4009942.pdf` p.34:34 and p.35:1 (INVENTORY line 89) is covered only implicitly. Name it.
8. The PII inside the deleted `Papers/` PDFs, still in git history: author emails and ORCIDs (INVENTORY lines 56–63). C6 covers these files as copyright only. Cross-reference them in §1.
9. P4 calls every username "generic". In 40 of the 42 occurrences, the username matches an entry on the owner's private-literal list (#2). Only the 2 occurrences in `aief_1_3_disjoint_100seed_analysis_manifest.json` are the generic sandbox user. Reword P4.

**Mis-cited INVENTORY lines** (the list's number, then the actual line):

| what | list says | actual line(s) |
|---|---|---|
| SSRH 000244 PII | 67–71 | 65–69 |
| SSH history PII | 72–75 | 70–73 |
| SSRH 001 PII | 77–84 | 74–84 |
| grok ice PII | 88–91 | 85–89 |
| other home paths | 93–110 | 91–108 |
| IP note (P2) | 114 | 112 |
| C2 | 35 / 151 | 33 / 145–150 |
| C3 | 34 / 145 | 32 / 143–144 |
| C4 | 30 / 142 | 31 / 139–142 |
| C5 | 29, 36, 38 | 34, 36, 30 |
| C7 | 121–131 | 123–130 |
| C7 suggested header | 159–166 | 158–163 |

**Extra** (in the list but in neither source; checked and valid):
- P5 and P6 additions (`runner.py:244` `platform.node()`)
- P7
- M1/M2
- the arena-merged P4 files
- §4's commit counts (updated from INVENTORY's 94/102)
- C7 adds `ControllerFiberQuotient.lean` and `CompleteGraphIncidence.lean`. Confirmed: all four Lean files contain "All rights reserved".

## Mechanical results

| check | result | log |
|---|---|---|
| validate_registry (`--base e47bad1 --edited-since ce8cced`, no `--write`) | artifacts 2699 same / 9 changed / 52 missing (main deletions) / 138 zip members; relocation 214 same / 3 count-changed / 4 missing; 249 not inventoried (README says 248) | `logs/validate_registry.log` |
| verify_inventory (REPRODUCING §2) | FAILS at [1/5], as documented | `logs/verify_inventory.log` |
| verify_manifest (published) | OK | `logs/verify_manifest_published.log` |
| verify_manifest `--inputs` | **FAILED**: 2 inputs (HANDOFF, spectrum report); OK on main | `logs/verify_manifest_inputs_*.log` |
| pii_scan without the private list | CLEAN, exit 0 | `logs/pii_scan_nopriv.log` |
| pii_scan with the private list | CLEAN, exit 0, 0 private-literal hits in `AI Agent Audits/` | `logs/pii_scan_priv.log` |
| Diff scan, all files changed vs main (`scripts/diff_scan.py`) | 0 deletions; 0 emails except `.invalid`; 0 secrets/tokens; home paths 42 in 11 files (40 match private literal #2, 2 are the generic sandbox user); private literal #1 (owner email): 0; IPv4: 2 regex hits in the raw `Results.pdf` stream, 0 in extracted text (false positive) | `logs/diff_scan.log` |
| Large / binary files | `registry/artifacts.csv` 1.27 MB (text); binaries `results_embedded.bin` and `.docx` (30 KB each, identical size), `uploads/Results.pdf` 76 KB; nothing ≥ 50 MB | same |
| CRLF | the `registry/*.csv` tables (inherited from arena's writer) and the arena audit CSVs (`python_path_dependencies.csv`, `zip_vs_tree_comparison.csv`, `runs_cohort_reconciliation.csv`) plus 2 zip-only CSVs. These are arena-generated, not merge-prep edits. Consider adding `.gitattributes`. | same |
| Audit folder, `lean/`, LICENSE / LICENSE-docs / NOTICE / LICENSING.md | **No changes vs main** (0 diff lines). Lean sources: `AIEF_LEAN_SOURCE_SHA256SUMS.txt` all 8 OK; toolchain v4.33.1 | — |
| Round-4 files overwritten | None in the audit folder. The 4 root files in Q6 were edited. | `logs/artifact_sha_changed.txt` |
| requirements.txt vs ENVIRONMENT.md and round-4 logs | numpy 2.5.1, scipy 1.18.1, pandas 3.1.0 and matplotlib 3.11.2 match ENVIRONMENT.md. pytest is 9.2.0 vs 9.1.1 (disclosed). The round-4 logs record only Lean versions. The b2a95 log used numpy 2.5.4 / pandas 3.0.6. The pins install cleanly. | `logs/pip_install.log` |
| REPRODUCING §3 pytest | **41 passed, 1 skipped** (11 s) | `logs/repro_s3_pytest.log` |
| REPRODUCING §4 paired statistics | **Match**: 100/100; shuffle_R +0.305909 [0.298939, 0.313030] dz 8.434; no_mu +0.271061 dz 4.900; no_delay −0.027424 dz −0.756 | `logs/repro_s4_paired.log` |
| REPRODUCING §5 Twindow v4 | **Match**: identity `6e6dea18…282355`; 15/15 output hashes match the revalidated manifest; 24 / 72 / 12 / 9,600 row counts match. "144 conditional DID rows" is not found in any output CSV. | `logs/repro_s5_*.log` |
| REPRODUCING §6 and §7 | Not run (timebox). §7's text is stale (v4.29.0-rc8, 3 modules). | — |
| relocation_map vs tree | 221 rows; independent recount agrees with `tree_check_2026_10_28` in all rows. Not present: `.~lock` file, `Papers`, `__pycache__`, `.lake`. Counts changed: `Project Histories` 11→15, `Project Origins` 9→12, Lean dir 3→6. | `logs/relocation_check.log` |
| Dangling references | `MERGE_PREP_REPORT.md` (missing); `registry/reconciliation/lineage_reconciliation.csv` (wrong path) | — |
