# Researcher 040282 upload — first-pass intake

- **Auditor:** Auditor Seat 002 (Grok Bot intake executor).
- **Date / timezone:** 2026-11-08 16:31 CET, Europe/Tirane (UTC+1).
- **Branch / upload reviewed:** `audit-inbox` at `b18a27d9d52e08d25634eb831deefc5926c2b22d` (`inbox: Researcher 040282 work`); parent `5c1ffed0377c4769154e9342464ce7265cf1c599`.
- **Current-main comparison reference (read-only):** `942f8526daee5ac547f2e422101fa95c61eeef41`.
- **Scope:** first-pass inventory, full reading of the six primary reports and their packet READMEs/workflow/state/queue/ledger, selected evidence-summary reading, static citation/inline-file checks, and search-like secret/PII review. Uploaded programs, tests, probes, Lean, shell scripts and extracted code were **not executed**. ZIP directories and text members were read as data in memory; nothing was extracted or run.
- **Disposition:** intake complete; `IN_REVIEW` for substantive adjudication. **UNVERIFIED INPUT throughout.** Reported PASS/FAIL, compiled declarations, numerical results and proposed repairs are the submitter's claims, not independent-seat approval. No CLEAN or FIXES REQUIRED scientific verdict is issued.

## 1. Inventory and navigation

All paths below prefixed `P/` mean `audit_inbox/2026-11-08_researcher-040282/` at the reviewed upload commit. There are **256 tracked files**, all mode `100644`: 11 in `aief_audit`, 51 in `aiefs_repository_audit`, and 194 in `researcher_040282`. The tree includes 42 Markdown, 72 JSON, 57 Lean, 35 Python, 19 CSV, 16 text and six ZIP files, plus other support files. Nonexecutable Git modes do not make scripts safe to run.

| Packet | What is supplied | Primary reading / evidence |
|---|---|---|
| `P/aief_audit/` | Audit of a pasted Analysis v4 program with synthetic fixtures and explicit dependency stand-ins; not a real-data audit. | `AUDIT-REPORT.md`, `README.md`, `analysis_under_audit.py`, `audit_support.py`, `synthetic_fixture.py`, `test_audit.py`, `probes.py`, `pytest_results.txt`, `unmasked_failures.txt`, `probe_results.json`, `audit-reproduction.zip`. |
| `P/aiefs_repository_audit/` | Targeted audit of older inbox source plus claimed real S01 reanalysis and a one-condition replay. Source acquisition metadata, audit programs, evidence logs and generated CSVs accompany it; raw NPZ datasets and the claimed full sparse source snapshot are not included. | `AUDIT-REPORT.md`, `README.md`, `branch_snapshot.json`, `acquisition.json`, `repository_tree.json`, `test_deep_audit.py`, `additional_probes.py`, `check_real_s01.py`, `replay_one_condition.py`, `evidence/`, `aiefs-audit-inbox-reproduction.zip`. |
| `P/researcher_040282/` | Gate foundations and cycles 002–004: paper arguments, proposed Lean components, bounded checkers, machine-readable local results, inline-code handoffs, historical source copies and four supporting ZIPs. | `README.md`, `WORKFLOW.md`, `RESEARCH_QUEUE.md`, `STATE.json`, `CLAIM_LEDGER.csv`; the four dated reports listed below; `cycle_002/`, `cycle_003/`, `cycle_004/`, `coordination/`. |

ZIP entry counts from static directory listings: source audit 10; repository audit 55; gate foundations 5; cycle 002 32; cycle 003 65; cycle 004 79. These include historical state/log material not all present unpacked. No absolute/traversal paths, symlink entries or encrypted members were found in these six archive directories; that is not a code-security certificate.

The nested `source_state/main/`, `source_state/inbox/`, tree JSON and `coordination/source_state/` files are **the researcher's snapshots**, never live project state. In particular `P/researcher_040282/cycle_004/source_state/` is not a second authoritative checkout or a tree to promote.

## 2. What the packets claim — not independently reproduced

### A. Pasted-source analysis audit

`P/aief_audit/AUDIT-REPORT.md:11–29,35–244` reports: exact-boundary held-event rejection/delay from floating-point addition/search; degenerate population-uncertainty interpretations of empirical bootstrap intervals; saved-grid versus physical-event censoring/observability limitations; input mutation after validation; serialized manifest payload/digest read-back gaps; and fragile nominal-window CSV equality. Other cautions concern degenerate references, empty topology, separate simultaneous families, and post-rename durability errors (`:248–291`).

Its own boundary is explicit: missing real S01 inputs and actual imported helpers, synthetic fixtures only (`:7–18`; `README.md:7–19`). The uploaded log says **23 passed / 6 expected failures**, and the unmasked log says six failures. These are reported witnesses, not six passing repairs. Static byte comparison found `analysis_under_audit.py` identical to the frozen v4 source on current main; that ties the object to v4, not automatically to v4.1 or the whole model.

### B. Repository / real-artifact audit

`P/aiefs_repository_audit/AUDIT-REPORT.md:26–34` groups seven alleged findings:

1. **Operational priority:** `tools/sync/upload_new.sh` can replace an ignored local file during integration before confirmation, and committed/history blobs can bypass advertised content/size checks (`:36–71`). The supplied logs use dummy data and temporary local remotes; this is not evidence that the owner's files were lost or real credentials were leaked.
2. **Inference:** 222 of 240 event-rate intervals allegedly collapse to zero width (28 zero-event and 194 all-event groups), with conditional-complete-case limitations (`:73–93,194–199`). Population coverage and fixed-cohort resampling diagnostics must remain distinct.
3. **False-result/self-test lead:** a proposal-bridge self-test allegedly hardcodes the wrong endpoint-winner branch and prints PASS despite an actual-operator residual around 0.0212 (`:95–120`). This is a high-value independent-negative-control target, not yet this seat's finding.
4. **Correctness/validation leads:** latent held-grid boundary failure, complex-NaN masking that hides a finite-component difference, and duplicate condition-status rows accepted by the public oracle (`:122–169`).

The report also claims **zero held-classification mismatches in 4,800 saved cases**, no nonfinite complex arrays in the inspected baseline/S01, and exact agreement between modular/original orchestration for one condition in one environment. Conversely its saved-oracle replay differs in 131 NPZ entries and 89 scalar cells under a different numerical stack (`:171–192`). None establishes production corruption or a full equivalence certificate. The full baseline, 200-condition production run, Lean build and broad scientific/literature adjudication were explicitly not done (`:211–217`).

### C. Gate / weight bridge / EMA research

- `P/researcher_040282/2026-11-07_researcher040282_gate-foundations.md:16–23,182–208`: paper-level guarded feasibility/idempotence and full-row identity; rational counterexamples to unconditional-kernel idempotence, global continuity/nonexpansivity and generic branch linearity; reported 300 exact cases and 96 isolated source comparisons. The original handoff explicitly was **not Lean-compiled**. Full-row constraints do not settle the selected-controller `AUD-RATELAW` question (`:168–180`).
- `.../2026-11-07_researcher040282_002_guarded-capacity-lean.md:10–18,90–130,243–308`: reports 22 compiled gate declarations and nine intended adversarial/control outcomes with allowed-axiom coverage. Guard, positive epsilon and entrywise nonnegativity matter. It acknowledges guarded idempotence is already `AUD-GATE`, not a new discovery.
- `.../2026-11-07_researcher040282_003_weight-update-bridge.md:9–23,132–176,213–221`: reports 44 new bridge declarations, reusing 22 prior local and five upstream ones; clipped proposal/row envelopes, both-branch applied factors, H0/time-zero handling, and conditional per-edge OFF/ON composition. It reports 17 controls, 384 exact cases and 24 source comparisons, **overriding compute_R** for those weight checks. Infinite-tail drive bands remain assumptions, not a locking proof.
- `.../2026-09-04_researcher040282_004_complex-ema.md:9–23,64–175,208–241,344–377`: reports 28 new declarations (22 EMA/readout plus six drive bridge), reusing 71 declarations; unit-disk preservation, directed complex state versus symmetric zero-diagonal reported R, forced difference recurrence, same-input/fixed-input special cases, and coarse positive-row/gate-floor bounds. It reports 18 controls and 34 controlled-state comparisons / 253 actual compute_R calls. Alpha=0 validation rejection is separately counted, not a numerical pass; binary alpha=1 is distinguished from exact-real strict convergence. The coarse row bound does not by itself certify ON. This is not coupled phase locking, a full delay transition, or machine-checked NumPy semantics.

The top-level ledger has **78 records**: nine cycle-001, 23 cycle-002 and 46 cycle-003; evidence labels are 66 LEAN_COMPILED, six EXACT_FINITE_CHECK, four PAPER_ARGUMENT and two NUMERICAL_CHECK. These are the submitter's labels. Independent review/integration are not established by that ledger.

## 3. Current-main comparison: known, stale, and potentially new

The repository-audit target is `5c1ffed...`, and research cycles cite main `ad58a46...`, both older than current main `942f852...`. Static Git blob comparison nevertheless found **identical source bytes** between the reviewed inbox base and current main for the uploader, engine, proposal bridge, actual-admissibility helper, Analysis v4 and modular `aief_modular/oracle.py`. Thus age alone does not dismiss those source-specific leads; identity also does not prove the claimed runtime behavior.

- **Already-known held-grid issue / version distinction:** current-main `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py:12–29,590–627` already describes v4's boundary issue and contains a tolerance-based candidate change. Its header still says CANDIDATE/UNAUDITED and blocks ordinary real-trajectory use (`:1–10`). The submitted v4 witness is not a new failure of v4.1 and is not authority to rerun real data or alter frozen v4. Existing R026-S8 already tracks tolerance-wording/run-output issues.
- **Stale CI generalization:** the repository report's older-inbox workflow statement (`AUDIT-REPORT.md:207`) is not current-main CI state. Main has `.github/workflows/repo-checks.yml`, including CI-tool self-tests and synthetic v4.1/modular analysis tests (`:23–37,152–181`), as well as Lean CI. This static reading makes no claim that every submitted witness is covered.
- **Known project context supplied for this intake:** main includes comparator/E14 (PR #8) and manifest G1/G2/G2b isolated re-exec (PR #9). Those are not evidence that all seven submitted leads are fixed. G2c (manifest/verifier not pinned externally) remains an owner item; ART-0043 is a separate owner erratum. The submitted analysis-bundle integrity concerns must not be conflated with that separate evidence-manifest checker.
- Guarded idempotence is existing project context (`AUD-GATE`); the potential incremental value is formal component coverage and stronger negative controls, pending independent proof/model review. Conditional versus global dynamics remains a known boundary, not a newly solved North Star.
- The sync-loss/history-scan, wrong-branch self-test, uncertainty, complex-NaN and duplicate-status leads deserve targeted current-main adjudication; they are not marked accepted or repaired here. The existing CLI import-path issue is already in R026-S7. R026's older scientifically-controlled-but-not-release-complete assessment and E15/E14 process history are background, not fresh findings from this packet.

## 4. Static evidence / citation checks and packaging issues

1. The two packet reports' primary named evidence files exist. Some repository-report citations abbreviate basenames: `upload_*.txt`, `download_ignored_collision_control.txt` and `independent_scientific_probes.json` resolve under `P/aiefs_repository_audit/evidence/`; the event-summary CSV resolves under `evidence/real_s01_analysis/v4/analysis_v4_20261107T072500Z_6e865df5/`. These are resolvable abbreviations, not proof that the evidence is true.
2. The uploaded source-audit logs agree with its reported 23/6 counts. The repository-audit logs list 9 passes / 8 strict expected failures and eight unmasked witness failures. `evidence/local_git_safety_probes.json`, `independent_scientific_probes.json`, `duplicate_public_oracle.json`, `real_s01_execution.json` and `one_condition_replay.json` contain the corresponding reported summaries. No test was re-run.
3. A bounded **read-only count of the supplied generated event-summary CSV**, not the underlying scientific data, found 1,200 summary rows, 240 event-observed groups, 222 zero-width intervals, 28 zero means and 194 one means. This independently confirms consistency of the report with its own CSV, not successful raw-data reproduction or population coverage.
4. All critical inline code blocks exactly match the corresponding uploaded files: two in cycle 002, five in cycle 003 and seven in cycle 004. This is byte/text consistency only, not proof acceptance. Recorded result JSON agrees with the reports' 9/17/18 control counts and declaration counts; success logs in the archives remain untrusted evidence.
5. Several top-level ledger/state paths to `.log` files and `cycle_002/checks/` / `cycle_003/checks/` do **not** exist unpacked. The named positive/check/source logs and checks-directory members are present inside the corresponding cycle ZIPs; the gate-foundations log is likewise archived. This is an archive-location limitation, not proof that the logs never existed. Do not execute the archive checkers to repair navigation.
6. **State drift:** root `README.md:24–64`, `WORKFLOW.md:126–144`, `RESEARCH_QUEUE.md:8–10,62–86`, and `STATE.json:7–15,46–60` stop at cycle 003 and queue cycle 004, although a cycle-004 report/results are uploaded. Root ledger has 78 rows; `cycle_004/packet_validation.json:16` claims 108, and the cycle-004 ZIP actually contains a 108-row ledger and cycle-004 state. Preserve both versions and request an addendum clarifying the intended latest state; do not silently overwrite either.
7. **Date/provenance anomaly:** cycle 004's filename/header and archived state say 2026-09-04 despite following November-7 cycles and citing the same later source basis. Request a dated correction/addendum from the owner/researcher; do not infer chronology, fraud or scientific invalidity from that mismatch alone.

## 5. Secret / PII review (values deliberately omitted)

Search-like scanning covered the 256 uploaded files and UTF-8-readable members of all six ZIPs, including hidden-name checks, credential-shaped patterns, private-key headers, credential assignments/URLs, email-like text and broader security keywords. No apparent live token/password/private-key block or `.env` credential file was found by this limited scan. It is not exhaustive secret detection or permission to republish the packet.

**Possible personal/non-noreply email metadata** occurs in commit-author fields and signed commit payloads at:

- `P/researcher_040282/coordination/source_state/main_branch_2026-11-07.json`
- `P/researcher_040282/cycle_003/source_state/main_branch.json`
- `P/researcher_040282/cycle_004/source_state/main_branch.json`

These are copied GitHub commit metadata, not evidence of a stolen credential; privacy/publication consent is not established. No values were copied into this note. Owner should decide privacy handling before any further sharing/promotion; this intake does not delete, rewrite, or republish the uploaded metadata.

Other matches are placeholder/example email fixtures in `P/aiefs_repository_audit/test_deep_audit.py` and `evidence/deep_audit_pytest_initial_harness_error.txt`, also mirrored within `aiefs-audit-inbox-reproduction.zip`. Deliberately constructed synthetic credential-shaped test fixtures appear in `test_deep_audit.py`, `additional_probes.py` and `evidence/deep_audit_unmasked.txt` (and archive counterparts); classify these as test data, not discovered live credentials. No fixture values are reproduced here.

## 6. Recommended next steps — no fixes implemented

- **Owner:** first consider the three metadata privacy paths above; retain backups of local research files and do not rely on the uploader helper's advertised ignored-file/history protection until independently checked. This warning is precautionary, not a claim that an incident occurred. Keep uploads on `audit-inbox`; **never merge audit-inbox or salvage wholesale into main** (briefing rule 12). Approve any future production change only through the normal reviewed route.
- **Auditor Seat 002:** break out bounded adjudications against pinned current main: sync ignored/untracked collisions and reachable-history scanning first; wrong-branch self-test and bootstrap interpretation next; then complex equality and oracle uniqueness. Independently design the controls from reviewed source in credential-free isolation; do not run supplied inbox code. Record which source/version is tested, hypotheses, falsifier and result separately. Respect frozen-authority/erratum requirements.
- **Researcher 001:** prioritize model/dependency fit of the gate/weight/EMA components; independently review exact hypotheses, global guard, H0, diagonal/symmetry semantics, allowed-axiom coverage and reused-upstream credit before any trusted rebuild or proposed integration. Same-input/fixed-input EMA claims must not become coupled locking claims. Request a cycle-004 date/state/ledger provenance addendum; no contact was made in this intake.
- Preserve the existing serial integration order: **`ci/check-sha256sums` refresh, then `fix/r026-cleanup`**. Neither was started. Do not fold these outside leads into those changes without a new scoped review decision. G2c and ART-0043 remain separate owner items.

Only this new intake note and maintainer `audit_inbox/TRIAGE.md` are organizer changes. All 256 uploaded files, `audit_inbox/briefing/`, frozen sources, main, and other researchers' notes remain unedited. No PR or outreach was initiated.
