# Audit of Researcher 001's AIEFS project map (independent recount)

Auditor: Grok Bot (executor). Date: 2026-10-29, finished around 19:45 Toronto (EDT).
Scope: read-only. I made no pushes, used no GitHub write tools, and did not edit Researcher's files or Pages. Everything here is in /workspace/audit_project_map/.
Inputs:
- /workspace/research/project_map/ (build_map.py, claims_map.csv, totals.json, MAP_NOTES.md).
- The Page "AIEFS Project Map — current state". Its live source matches page_source_snapshot.txt exactly.
- The "AIEFS Research Sweep" Page, snapshotted as research_sweep_page_snapshot.txt.
- An anonymous mirror of the GitHub repo (_mirror.git; no remote added), plus Researcher's local branches cc31533 (freezing) and 2fc1110 (lean-kn).

## Verdict: BLOCKING (narrow)

Most of the map holds up:
- The row counts, totals, Lean builds, the freezing 249/1,412 numbers and the owner label rule all check out.
- 93 of 98 evidence levels agree with mine.

The blocking part is the "rediscovered independently" (validation) section. Fix it before the Page is used to claim priority or validation:
1. **The "derived before the literature" yardstick is wrong.** The map compares the first commit (add81e6, 2026-10-18) with the first literature search (2026-10-23). But the first commit was a bulk upload of 866 files that already included a literature review: Berner et al. 2023, Physics Reports, arXiv:2304.05652, filed as `Papers/2804.05652v1.pdf`. The chat histories also discuss literature. The order relative to the specific papers cited still holds. The general claim that the work was done "before any literature" does not.
2. **The 0.995 correlation hit is not a real validation hit.** The registry's own erratum E12 says this association is "the mechanism working as designed". The cited paper, Chauhan 2022, matches loosely, and it fits a different row (AUD-TOPO-OMEGA) better.
3. **The surviving hits are textbook facts:** the kernel dimension of K_n, and n·r^n for Jordan blocks. They are real and specific matches, but weak as validation.

## Key numbers: Researcher vs me

| Item | Researcher | Me | How I got it |
|---|---|---|---|
| Rows / registry / unregistered | 98 / 77 / 21 | 98 / 77 / 21 ✔ | Rerun of build_map.py gives a byte-identical CSV. Independent count: evidence/independent_count.json |
| Registry rows per branch | 77 union | ✔ | 75 rows on merge-prep, nanfix-v2, ci/validator and ci/artifact-pins; 76 on freezing (+RES-FREEZE-01) and on lean-kn (+LEAN-KN-01); 43 on arena; no claims.csv on main or fix/corr-0995-scope. Union 75+2 = 77 |
| Lean-proved | 5 | **4** | AUD-CYCLE-KERNEL is argument-only overall (see b) |
| Argument only | 31 | **34** | |
| Conditional | 33 | 33 ✔ | 16 of them in the registry |
| Withdrawn or corrected | 26 | **25** | AUD-RESP1-UNIFORM is a live, supported correction, not a withdrawal |
| Exact / floating-point / unverified | 5 / 18 / 13 | 3 / 19 / 13 | |
| Validation | 3 distinct hits + 1 partial + 9 unclear | **2 distinct hits (both textbook-level), 1 partial, 10 unclear, 3 more "no"** | See (a) |
| Freezing certified (run, T) pairs | 249 of 1,412 with N>0, 0 violations | ✔ 249 / 1,412 / 0 | evidence/freezing_count.txt, recounted from results.json. Note: 246 of the 249 come from just 2 of the 12 runs |
| Lean declarations | 115 (LEAN-R4), 52 (LEAN-KN-01) | ✔ 115, ✔ 52 | I reran the repo's check_lean.sh: 7/7 PASS, 1,591 jobs, 0 warnings. My `#print axioms` over the Kn project lists 52 declarations |
| Inconsistencies | 15 | 15 rated (9 confirmed, 4 partly right, 1 understated, 1 wrong) + 11 new | See (c) |

totals.json: rerunning build_map.py reproduces every number in it. The exceptions are four hand-added keys that the script does not produce: `lean_note` and `validation_hits.{distinct_results_yes, distinct_results_yes_partial, headline}`. So the "3 hits + 1 partial" headline is a hand edit (evidence/rerun_diff.txt).

## (a) The "derived before the literature" calls and the published matches

Full table: evidence/citations.csv. The papers were checked on the web and are all real.

| Rows | Paper | Derived before that paper? | Match real and specific? | Who added the citation | Researcher | Me |
|---|---|---|---|---|---|---|
| AUD-CYCLE-KERNEL, U-MS-8.1 | van Nuffelen 1976; Grossman–Kulkarni–Schochetman 1994 (rank of the signless incidence matrix) | **Supported** (manuscript:1198 at add81e6; h03:16759). But h03:43270 states the general rank theorem from memory, which is recall, not derivation | Real and specific; textbook fact | Bot (Researcher 001, lean-kn README:111) | yes | **yes, weak** |
| U-MS-10 | Elaydi, *An Introduction to Difference Equations*, 3rd ed., Springer 2005 | **Supported** (manuscript:1534; h03:25869). But h03:26349 calls it "the canonical discrete Jordan block", which is recall | Real and specific; textbook | **Added by the map itself** | yes | **yes, weak** |
| AUD-CORR-0995, -SCOPE | Chauhan et al. 2022 | Supported (HU:166; h01:8169) | **Loose.** Chauhan reports a frequency–degree correlation, which matches AUD-TOPO-OMEGA, not the 0.995 statistic. E12 (ERRATA:188–196) calls it designed-in. The closest prior art is Seliger, Young & Tsimring 2002, which is cited in the review that was in the repo from day one (paper.txt:5308) | Bot (E12) | yes | **no** |
| AUD-RATELAW, AUD-KAPPA-TW, U-MS-8.3 | Miller & MacKay | Supported (HU:543) | Analogy only | Bot (salvage f7246a3, 2026-10-23) | partial | **unclear** |
| U-MULTISTAB | Berner 2023 review, §14.6 (paper.txt:2466) | **Unsupported.** The review was in the repo at the first commit | Specific | Owner-supplied PDF | unclear | **no** |
| AUD-TOPO-OMEGA | Chauhan 2022 | Unknowable from git (bulk uploads) | Closer fit than for 0.995 | — | unclear | **partial** |
| Other 7 "unclear" rows | — | Unknowable | — | — | unclear | unclear (agree) |

Notes:
- Git history cannot date anything inside the 866-file first commit, because the commits are web-UI bulk uploads. Only the chat histories (h01–h10) give an internal order.
- **Every literature citation in the repo was added by a bot.** The only literature the owner supplied is the Berner review PDF.

## (b) Evidence levels re-derived

Definition used for Lean-proved: the project builds, is covered by SHA256SUMS or CI, and has no sorry, admit or axiom. On that test:
- **AIEFProofs, AIEFProofsKn and AIEFFreezeCore all qualify.** All three build (1,591, 1,879 and 1,669 jobs). Each project's source SHA256SUMS file verifies. None contains sorry, admit, axiom, native_decide or unsafe. `#print axioms` on all 114 theorems and lemmas shows only propext, Classical.choice and Quot.sound.
- **Only AIEFProofs is in CI.** AIEFProofsKn and AIEFFreezeCore exist only on branches.

Confusion table (rows = Researcher, columns = me; also in evidence/confusion_table.md, per-row detail in evidence/evidence_levels_auditor.csv):

| Researcher \ Me | Lean | exact | argument | float | unverified | retracted/corrected | total |
|---|---|---|---|---|---|---|---|
| Lean-proved | 4 | 0 | 1 | 0 | 0 | 0 | 5 |
| exact computation | 0 | 3 | 1 | 1 | 0 | 0 | 5 |
| argument only | 0 | 0 | 31 | 0 | 0 | 0 | 31 |
| floating-point | 0 | 0 | 1 | 17 | 0 | 0 | 18 |
| unverified | 0 | 0 | 0 | 0 | 13 | 0 | 13 |
| retracted/corrected | 0 | 0 | 0 | 1 | 0 | 25 | 26 |
| total | 4 | 3 | 34 | 19 | 13 | 25 | 98 |

Disagreements (5):
1. **AUD-CYCLE-KERNEL: Lean → argument.** The claim is mainly that the round-2 matrix is not a Jacobian and that the right object is the multiplier on K. Only the dim K part is in Lean, and the registry's own scope calls it a "Conditional theorem".
2. **U-THRESH: exact → argument.** 3/7 and 0.4543 come from hand algebra. There is no script or proof that computes them exactly.
3. **U-MODEL: exact → floating-point.** "Matches the engine exactly (0.0)" is bitwise float64 agreement over finite runs, not exact arithmetic.
4. **AUD-KAPPA-TW: floating-point → argument.** The claim is a derived formula; the 292-component census only checks it numerically.
5. **AUD-RESP1-UNIFORM: retracted → floating-point.** It is a live, Supported erratum, not a withdrawal.

Agreements with a note:
- **LEAN-KN-01:** Lean-proved, but on a branch only and not in CI.
- **CF06:** the kernel is Lean-proved; applying it to the observed pattern depends on CF05, which rests on one seed.
- **U-MS-8.1:** the dimension part is Lean-proved, but its "spectrally silent" wording has been retired.
- **RES-FREEZE-01:** argument only. Lean covers just the per-edge existential-N core.

## (c) The 15 inconsistencies

Paths are on the research/freezing tree (cc31533) unless a commit is named.

| # | Researcher's item | Rating | Evidence |
|---|---|---|---|
| 1 | CURRENT_STATUS says "75 rows" | **Confirmed** (on freezing and lean-kn, which have 76; correct on nanfix-v2) | CURRENT_STATUS.md:84; also "Last Verified 2026-10-23" at line 3 |
| 2 | study_id collision at claims.csv:70 | **Confirmed** | RES-FREEZE-01 (freezing) and LEAN-KN-01 (lean-kn) are both at line 70, both tagged AI_AGENT_AUDITS_2026_10 although neither came from an audit. They will merge-conflict |
| 3 | RES-FREEZE "explicit N" vs ∃N | **Wrong** (no inconsistency) | Every source says the explicit N is paper-level and Lean has ∃N: claims.csv:70 scope, CURRENT_STATUS.md:128, research/freezing/README.md:20,33, AIEFFreezeCore/README.md:16 |
| 4 | ART-0748 hash stale | **Right but understated: 5 of 9 stale** | registry/artifacts.csv:744–749: ART-0743, 0744, 0745, 0746 and 0748 do not match the files; 0747 and 0749–0751 match. The newer Lean modules, AIEFProofsKn and AIEFFreezeCore are not registered at all |
| 5 | README:75 "no literature review" | **Confirmed** | README.md:75 on freezing and lean-kn. The Lean section (README.md:57) also omits Kn and FreezeCore |
| 6 | 0.4286 vs 0.4543 | **Confirmed, with a nuance** | 3/7 = 0.4286 is where B* = 0; 0.4543 is the threshold for settling above B_c. 0.4286 is used as a persistence threshold at claims.csv:2 (EMP-AIEF13-01 note), build_claims_reconciliation.py:49, AIEFS_audit_response.md:21, Map Page line 22, and **Research Sweep Page line 227** ("freezing follows from R > 0.4286", which is wrong: REPORT.md:213 uses R_c = 0.4543). claims.csv:46 states it symbolically as μ/(η+μ). ERRATA:189 gives ≈0.454. The shuffle result (0.371) holds under either threshold |
| 7 | E1 vs E8 wording | **Confirmed (minor)** | ERRATA:30 still says "on clustered ω it does worse"; ERRATA:150–151 calls that wording an overstatement |
| 8 | "0/29,040" under a 40-seed claim | **Confirmed** | EMP-AIEF14-01 note: the 29,040 figure is from the 440-run audit set, not the 40 seeds |
| 9 | "projected" / "spectrally silent" | **Confirmed** | AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md:1248 still says it. It was retired at README.md:73 and in audit responses 2 and 3, but has no erratum |
| 10 | CF05/CF10 Supported on one seed | **Partly right** | Disclosed in the row ("single seed, not re-checked"), but the status is still Supported |
| 11 | EMP-AIEF13-02 caveat broader than the audit | **Confirmed** (already flagged in the row's own note) | claims.csv EMP-AIEF13-02 scope vs reconciliation note |
| 12 | lean.yml gives a false green | **Confirmed** | .github/workflows/lean.yml triggers on `lean/**` but builds only lean/AIEFProofs. A change to Kn or FreezeCore produces a green run that never built it |
| 13 | Validator default `--edited-since ce8cced` | **Confirmed** | ce8cced is not in any pushed ref (`git cat-file` fails). The default is at validate_registry_against_tree.py:50 on merge-prep, nanfix-v2, freezing and lean-kn; it is fixed only on unmerged ci/validator 249ea3f |
| 14 | SSRH-ORIG-04 r = 0.92 | **Partly right** | The number comes from chat text with no data, and the row itself already says so |
| 15 | AUD-NOVELTY stale | **Partly right** | Its scope still says "first-pass search only". Literature work since then (E12, the sweep, the lean-kn README) is not reflected, and the review PDF existed from day one |

New inconsistencies I found:
- N1. MAP_NOTES.md has no inconsistency list. The 15 items exist only on the Page.
- N2. The four hand-added totals.json keys, including the validation headline, are not produced by build_map.py.
- N3. The yardstick and the U-MULTISTAB call ignore the Berner review that was in the repo at add81e6.
- N4. The Chauhan citation is attached to AUD-CORR-0995 when it fits AUD-TOPO-OMEGA.
- N5. The 26 "withdrawn or corrected" includes the live correction AUD-RESP1-UNIFORM.
- N6. AUD-REPRO-B2A95 has an erratum, E10 (on nanfix-v2 cbf2ae7; ERRATA:169; the claims.csv note cites it). The map shows no errata for it.
- N7. tools/sync/SHA256SUMS covers only the sync scripts and tools/sync/README.md. It covers neither the root README nor any Lean file, so it does not back the Lean claims.
- N8. The Page's definition of Lean-proved leaves out the CI requirement, and two of the three projects are not in CI.
- N9. The SSRH-ORIG rows say "Speculative" in the map CSV and show no label on the Page. The owner rule requires the full "Speculative / untested origin hypothesis". The registry itself is compliant on all 8 branches.
- N10. Of the 249 N>0 pairs, 246 come from two runs (random_omega_U[1,2]#0 and stress_near_identical, 123 each). The non-trivial-N path has effectively been tested in 2 settings plus 3 single reset_B pairs.
- N11. Researcher's figure of 249 is right, but the Page and README never say these come from 2 runs.

## Other checks

- **Owner label rule:** compliant in the registry. SSRH-ORIG-01..07 are "Speculative / untested origin hypothesis" on every branch. S01–S18 are Retired / Superseded and AUD-SLOWPOLE is Rejected; both were tested or withdrawn, so those labels are fine. Only fix: show the full SSRH label on the Page and in the CSV (N9).
- **Gaps:** these are as Researcher states:
  - O1 is open;
  - AUD-TIMESTEP is Incomplete, with no dt study;
  - CF12 is a conjecture with no evidence beyond the replay (I did not re-run CF12);
  - 249 / 1,412 is confirmed.
- **Private data** (by type and location only):
  - No emails, IP addresses, tokens, phone numbers or personal names in Researcher's outputs or either Page. The number patterns found are DOIs.
  - The only internal details are box paths:
    - /workspace/audit_research, /workspace/audit_r001 and /workspace/audit_r001_branches, in MAP_NOTES.md:8, build_map.py:86, claims_map.csv:84 and page_rows.ts:1;
    - /workspace/research/project_map, on the Page at lines 135 and 284;
    - a managed-skill path, in MAP_NOTES.md:41.
  - These are harmless, but should be removed if the Page is shared.

## Prioritized fix list

1. **Rewrite the validation section.**
   - Change AUD-CORR-0995 and -SCOPE from "yes" to "no (designed-in; see E12)".
   - Move the Chauhan match to AUD-TOPO-OMEGA as "partial".
   - Change U-MULTISTAB to "no".
   - Downgrade the 3 Miller & MacKay rows to "unclear".
   - Mark the kernel and n·r^n hits as textbook-level.
   - Remove the hand-edited totals.json headline, or have build_map.py generate it.
2. **Replace the yardstick.** State that the Berner 2023 review was in the repo at add81e6. Date claims against specific papers using the chat histories, and mark everything else as unknowable.
3. **Change the Lean-proved count from 5 to 4** (AUD-CYCLE-KERNEL becomes "argument only; dimension part Lean-proved"). Add "in CI" to the Page's definition and flag LEAN-KN-01 and RES-FREEZE-01's Lean core as branch-only and not in CI.
4. **Split the 26** into withdrawn (25) and live corrections (AUD-RESP1-UNIFORM). Reclassify U-THRESH, U-MODEL and AUD-KAPPA-TW.
5. **Correct the inconsistency list:**
   - drop #3;
   - widen #4 to 5 stale artifact hashes plus the unregistered Lean files;
   - add Research Sweep Page:227 to #6;
   - add N1–N11.
6. **Show the full label** "Speculative / untested origin hypothesis" for SSRH-ORIG-01..07 on the Page and in the CSV.
7. **Repo follow-ups for the owner** (not done; this audit is read-only):
   - CI for AIEFProofsKn and AIEFFreezeCore, or narrow lean.yml's path filter;
   - merge the ci/validator fix;
   - re-hash ART-0743..0748;
   - add an erratum for manuscript:1248;
   - fix CURRENT_STATUS row count;
   - give RES-FREEZE-01 and LEAN-KN-01 their own study_id;
   - update README:75 and AUD-NOVELTY.
8. Remove box paths from the Page before sharing it.

## Evidence files (evidence/)

- independent_count_and_confusion.py, independent_count.json: my independent count and level overrides.
- confusion_table.md, evidence_levels_auditor.csv: the evidence-level comparison.
- rerun_diff.txt: the rerun of build_map.py vs Researcher's files.
- freezing_count.txt: the 249 / 1,412 recount.
- citations.csv: the rediscovery and citation table.
- axioms_AIEFProofs.txt, axioms_AIEFProofsKn.txt, axioms_AIEFFreezeCore.txt: axiom output per project.
- build_*.log, check_lean_AIEFProofs.log: Lean build and check logs.

Also in this folder:
- page_source_snapshot.txt, research_sweep_page_snapshot.txt: the two Page snapshots.
- _pdf/: text of the review and of chat histories h01–h10.
- _mirror.git: the anonymous mirror of the repo.
