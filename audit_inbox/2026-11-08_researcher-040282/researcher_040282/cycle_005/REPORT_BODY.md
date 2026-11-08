# Researcher 040282 — 005: review response and branch-faithful bridge self-test

**Prepared for owner upload; candidate unreviewed and unmerged.**

- Owner/seat handoff label: **2026-11-08**, carried from the correspondence.
  Session-supplied preparation date: 2026-09-04, Atlantic/Reykjavik. Neither is
  asserted as a recovered historical 004 execution timestamp; see the addendum.
- Current main actually tested: **f3e3a57632c613e860a9941f007732cb4c2c91c6**.
- Review/intake acquired read-only from audit-inbox:
  **b466ab6cdd564ce3f7848e7701b378c5f0cc475f**.
- Public selected acquisition:26 main files (including 10 verified Python import
  dependencies),35 inbox files. The first refresh log says12 main selections;
  six bridge files and eight recursive dependencies were added afterwards.
- No remote push, PR, merge, contact, automatic inbox upload, or model-parameter
  change. No new Lean compilation or production bridge replay this cycle.

## Executive result

The highest-value new action is a **verification repair proposal**, not another
rediscovery of the known bridge defect. The old `synthetic_self_test` still prints
PASS without calling the real post-positivity operator. A new standalone K3
companion queries that operator and checks its output/metadata against a separate
exact-rational loop oracle before testing the conditional identities.

| Check | Pinned legacy entry point | Proposed companion |
|---|---:|---:|
| Same three real-operator/fail-closed contracts | **3 failures,0 errors** | **3 pass** |
| Full candidate suite | Not applicable | **22 pass,0 fail/error/skip** |
| Full candidate suite under Python `-O` | Not applicable | **22 pass,0 fail/error/skip** |
| Old wrong-branch fixture(.41,.31,.27) | Prints PASS; never queries map | Observes(2,2,7), rejects, CLI exit2/no PASS |
| Positive fixture(.41,.27,.31) | Not the old fixture | Observes(7,2,7), uses actual y |
| Seeded positive perturbations | Not provided |64 cases + default, fixed abs1e-14/rel0 |

**Scope:** the operator exercised is
`AIEF_1_4_actual_admissibility_branch_audit.admissibility_from_nonnegative_proposal`,
the current-main **pure edge-coordinate audit helper**. This is not a fresh
production-engine `advance_state` run, an exact-real universal proof, or a
certificate about the saved real-data trajectory. ART-0050 itself is untouched.

## 1. Short cycle004 addendum

{{ADDENDUM}}

## 2. Disposition of received feedback

The actual intake note and Researcher 001 triage were acquired, not merely inferred
from the owner's summary. Their earlier-main execution basis was
`942f8526daee5ac547f2e422101fa95c61eeef41`, distinct from this cycle's tested main.
Their witness/source-compilation reports and our own current executions are kept
separate in `cycle_005/feedback_scope.json`.

- **Independent compilation is acknowledged, narrowly.** They report 22/44/22+6
  accepted declarations, zero warnings/errors, only propext/Classical.choice/
  Quot.sound. This is94 declarations of local formal contributions across 002–004;
  it is not94 new declarations in005, and does not absorb five reused upstream
  FreezeCore declarations into our credit. The original 94 `LEAN_COMPILED` labels
  are unchanged. A separate ledger review column now records only the reported
  compilation/footprint confirmation. Statement fidelity/library review remains
  pending. External coarse-ON comparison confirmation is likewise scoped: failure
  of that sufficient ON certificate is NOT an OFF result.
- **Do not attribute our controls to the reviewers.** They did not run our
  `check_cycle.py`, ZIP checkers, full S01 reanalysis,4800 saved held-event checks,
  or real-array finiteness census. The new companion and its tests postdate that
  review and have no independent reviewer execution yet.
- **Uploader/checksum follow-up closed for this queue.** The owner reports PR10
  and PR11 merged; acquired main matches the supplied head. No additional
  uploader patch or behavioral certification of those merges is attempted.
  Current-main `.github/workflows/repo-checks.yml` exists; the old broad
  no-Python-CI statement is withdrawn as a current-main claim.
- **Other findings stay separate.** Engine complex-NaN comparison and oracle
  duplicate acceptance remain separately scoped repair candidates, not changes
  hidden inside this packet. Synthetic duplicate acceptance is not a new
  independent execution of the real201-versus200 S01 oracle case. A real-array
  finiteness claim is not independently established by a NaN sentinel witness.
- **Review existing v4.1 next, not frozen v4 again.** Keep held-event estimand
  choices explicit. Percentile resampling from a fixed seed cohort is not a
  boundary-valid population rate confidence interval:0/40→[0,0] and40/40→[1,1]
  are diagnostics of the observed cohort, not evidence that a population rate
  must be exactly 0 or1. No v4.1 correctness conclusion is newly claimed here.

The reviewer/private witness-log paths mentioned in their notes have not been
fetched and are NOT represented as part of our local evidence. Received review
notes, submitter execution logs and future independent controls are distinct.

## 3. The one code finding and why this follow-up matters

The known B-F4 failure is at pinned ART-0050
`AIEF_1_4_proposal_equalization_bridge_analysis.py:198–267`. Its synthetic test
uses x25=.41,x29=.31,x59=.27, computes scales, and manufactures the purported
projection using endpoint winners7,2,7. It then checks identities on that
manufactured vector. It never calls the actual admissibility operator.

On the current helper, the proposal row loads are q2=.72,q7=.68,q11=.58, so
node 2 has the smaller clipped scale. The real winners are **2,2,7**. Using actual
returned y, the left identity has residual **−0.02121459694983044**, vastly over
the pre-existing1e-14 allowance. Yet the old test prints PASS. This matches the
previous finding and colleague witness; it is not a novelty claim or a
counterexample satisfying the strict(7,2,7) hypotheses.

A valid positive fixture exchanges the last two values: **(.41,.27,.31)**.
Then q2=.68,q7=.72,q11=.58, and actual winners are7,2,7. The new companion uses
THIS full66-edge input with all other entries zero, but still verifies the
returned branch rather than hardcoding a projected answer.

The new contribution is the **new-file, fail-closed verification path** plus
red→green/mutation controls. It removes a built-in-answer route without changing
the pinned artifact, conditional theorem, model, registry row or saved outputs.
There is no direct-main or inbox/salvage merge proposal.

### 3.1 Identity and admitted branch

For isolated nonnegative selected proposals, uniform capacity c,epsilon>0:

- The global guard is `any(q>c)`; inactive applied factors are1, not dormant
  candidate scales c/(q+epsilon).
- Both node 2 and node 7 rows are over capacity; their scales are strictly in(0,1).
- Selected proposals are positive and actual strict endpoint winners are7,2,7;
  ties or an inactive gate are NOT promoted to this strict branch.
- In that branch, with the ACTUAL returned y and s7,

  `y25−y59 = s7*(x25−x59)`

  `y59−y29 = [c*(x25+epsilon)/((x25+x59+epsilon)*(x25+x29+epsilon))]*(x59−x29)`.

The existing `right_projection_coefficient` is the analytical expression under
test; the observed projection is not reconstructed with it. The independent
Fraction oracle separately builds incidence sums, guard, clipped scales,
minimum-endpoint factors, all 66 outputs and all branch codes from exact binary
input embeddings. It does not call that coefficient or the actual operator.
The tested helper is floating point, so exact-rational comparison is at the
preregistered **absolute1e-14,relative0** allowance, not an exact execution theorem.

The companion explicitly checks incidence layout/matrix, output shapes, real
finite values, gate type/value, violating/clipped flags and winner codes. Core
validation raises named errors rather than relying on Python `assert`.

### 3.2 Actual finite results

For the default positive case, returned selected y is
`[0.36064814814764723,0.25147058823492435,0.27268518518480644]`.
Left/right residuals are `1.3877787807814457e-17` and
`-4.85722573273506e-17`, respectively.

With seed**2026090405**,32 draws in the preregistered box
x25∈[.39,.42],x29∈[.26,.28],x59∈[.30,.32] are each checked at epsilon1e-12 and1e-2.
These are64 perturbation cases; default plus perturbations is65 valid cases,
NOT65 unittest methods or independent trials. Across those 65:

- largest absolute left residual: **5.551115123125783e-17**;
- largest absolute right residual: **7.806255641895632e-17**;
- largest output/Fraction difference: **5.551115123125783e-17**;
- largest scale/edge-scale difference: **1.1102230246251565e-16**;
- row comparison maximum difference:0;
- minimum actual selected endpoint-winner margin: **0.029937150824232206**.

These positive synthetic margins are intentionally comfortable. The inspected
saved replay manifest instead records a minimum margin4.440892098500626e-14.
This packet does **not** certify numerical robustness or branch stability of
those saved near-tie states.

## 4. Preregistered falsifiers and what actually failed

The plan was saved before the new scientific tests. No tolerance, domain box or
legacy fixture was changed to obtain a pass. An initial20-method suite passed; the planned constant-answer control was
then explicit as a21st method. A final stronger constant-answer falsifier exposed
an actual flaw in OUR first candidate: it constructed the Fraction oracle from
a mutable proposal after the operator call. A test double could rewrite the
requested input to the default fixture and return that answer, moving the oracle
with it. The single new control failed before repair (1 failure,0 errors;
`input_mutation_red.log`). This is NOT a claim that upstream's pure helper mutates
inputs. The corrected candidate snapshots the requested proposal, builds its
oracle BEFORE the external call, and rejects input mutation. The new 22nd method
passes. Original20/21-method development code/results and the failing witness
are preserved; final ordinary/optimized22-method suites and extraction were rerun.
No domain or tolerance was relaxed. The pre-check rationale is in
`ADVERSARIAL_ADDENDUM.md`.

| Control | Observed intended outcome / reason |
|---|---|
| Same 3 contract tests on legacy |3 assertion failures,0 errors: no actual-map query; ignores sentinel unavailability; ignores corrupted actual output |
| Same 3 contracts on companion |All pass; actual output required, sentinel RuntimeError propagates, corrupt output rejected |
| Original(.41,.31,.27) fixture |`BranchMismatch`, observed2,2,7; CLI exit2/no PASS normally and under `-O` |
| Tie(.41,.29,.29) |Actual edge25 tie code−2; not accepted as strict7,2,7 |
| Inactive(.10,.07,.08) |Actual gate false/winners−1; not accepted as clipped branch |
| Zero selected value |Not certified as positive strict branch |
| NaN/Inf/negative proposals; epsilon0/negative/nonfinite |Validation error, not PASS |
| Output corrupted by1e-4 |Full-vector Fraction comparison rejects |
| Winner metadata changed |Exact branch-code/oracle comparison rejects |
| Constant default projection used for a changed valid input |Full-vector oracle comparison rejects |
| Incidence matrix misses an endpoint |Independent layout/matrix check rejects |
| Global guard dropped on inactive large-epsilon example |Ungated candidate scaling differs from identity map; output check rejects |
| Epsilon dropped from right coefficient at admitted epsilon1e-2 |Actual right-identity check rejects |
| Operator dependency/import failure |Propagates as dependency error; not counted as mathematical branch rejection |
| Public modules absent in CLI |ModuleNotFoundError/nonzero/no PASS; setup blocker, not a false theorem proof |

Final normal and optimized suites each run21 unittest methods, with no skips,
failures or errors. The expected nonzero legacy-red run is accepted ONLY if all 3
failures and0 errors occur. Missing dependencies cannot masquerade as red success.
The original 10 upstream Python modules are checked before and after the runner
and remained unchanged. Frozen ART-0050 bytes and the existing004 proof sources
are preserved.

## 5. Does any saved bridge evidence depend on the false synthetic PASS?

**Bounded answer: the recorded normal replay invocation does not request it.**
The saved `aief_1_4_proposal_equalization_bridge/analysis_manifest.json` command is:

```text
AIEF_1_4_proposal_equalization_bridge_analysis.py
  --npz runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz
  --manifest runs/5a9f093a2fe0/manifest.json
  --seed 4619122171158768524
  --output-dir aief_1_4_proposal_equalization_bridge
```

It has no `--self-test`. The only direct call to `synthetic_self_test` in the
inspected bridge is line361, inside `if args.self_test: ...; return` at358–362.
The normal path separately loads data and computes actual intermediates/winners
at390ff. **If the manifest accurately records the invocation**, that invocation
uses the normal replay path, not the opt-in synthetic test. This is static
provenance, not authentication of the historical invocation or a fresh rerun.

The manifest reports gate_on/controllers_clipped/selected_positive/winner-map
checks true, isolation error0 and final replay equality. Those remain **saved
reports**, not new independently verified outcomes in005. The synthetic defect
alone does not refute them or the explicitly conditional algebra.

Our earlier own audit invoked the old synthetic test to expose its false PASS;
it did not treat PASS as support for the invalid fixture. Our one-condition S01
replay script imports engine/modular orchestration, not this bridge. A copy of
that script and a bounded AST/import/provenance record are supplied under
`cycle_005/historical_provenance/` and `saved_evidence_provenance.json`.
No exhaustive search of every historical wrapper/caller or saved-evidence chain
is claimed. Full bridge replay and real-array finiteness remain unrun here.

## 6. Proposed erratum / owner-review text

{{ERRATUM}}

## 7. Reproduction from this one Markdown

All six critical files are complete in AppendixA; no private workspace is needed.
Review public source dependencies before execution. Save the extractor block as
`extract_from_report.py`, then run from a fresh working directory:

```sh
python extract_from_report.py THIS_REPORT.md restored
cd restored
# Requires an available NumPy/Pandas/SciPy stack; none are installed by these tools.
python fetch_public_dependencies.py --output upstream
python -B run_checks.py --source upstream --output checks
```

The fetcher downloads only 10 public Python modules from the explicitly tested
main commit and verifies their acquisition records; it requests/stores no commit
contact/signature metadata and does not execute downloaded code itself.
Installed environment observed here:Python3.13.16,NumPy2.3.5,Pandas2.2.3,SciPy1.17.1.
These are observations, not a claim that every environment is equivalent or that
third-party package builds were independently audited.

Runner exit0 means: expected legacy red3/3 with 0 errors, candidate21/22 normally,
candidate21/22 optimized, all 65 positive comparisons at unchanged allowance, and
all 10 upstream modules unchanged. A setup failure or a different red count fails
the overall runner. Logs/results are written under the chosen checks directory.
The reported all-green result applies to our owned finite tests, not arbitrary
submitted code or library-grade acceptance.

### Actual extracted-code reproduction

{{STANDALONE}}

## 8. Evidence access, privacy and state reconciliation

This standalone note contains complete new critical code and essential results.
The optional ZIP adds the short addendum, synchronized root/state/current109-row
ledger, completed004108-row snapshot, public sources, raw checks, previous proof
modules and **unpacked logs**. Prior original ZIPs are not duplicated inside it.

- `EVIDENCE_INDEX.json` maps every current ledger evidence reference to unpacked
  packet paths and separately lists logs. Directory references expand to actual
  members; there are no silently broken or archive-only cited log paths.
- `HISTORICAL_ARCHIVE_LOG_MAP.csv` maps older ZIP log-member paths to their now
  unpacked counterparts. Those copies are checked against the old archive bytes.
- For example, ledger paths `cycle_004/checks/CoherenceEMA.log`,
  `cycle_004/checks/CoherenceDriveBridge.log`,
  `cycle_003/checks/positive.log` and source-comparison logs are directly under
  `researcher_040282/` after extraction. Also included are original/extracted004
  logs `cycle_004/cycle_checks.log`, `standalone_reproduction.log` and
  `standalone_source.log`. New raw logs are `cycle_005/checks/*.log` and
  `cycle_005/standalone/checks/*.log`.
- Accepted mathematical modules are the explicitly listed cycle modules, not
  every `.lean` under checks/: several check fixtures intentionally contain
  false goals or forbidden payloads to test rejection. They are not accepted
  theorem sources. Historical packet validators record their original closure
  state; do not rerun an old root-state consistency assertion against the new 005
  root and misdescribe that as a failed mathematical build.
- Three raw main-branch acquisition JSON files were minimized: coordination's
 2026-11-07 record and cycles003/004 main_branch records. All author/committer
  data and complete signed commit payloads were dropped, not merely email keys.
  Four contact-like occurrences in each were removed without printing values or
  saving unredacted backups. This counts occurrences, not distinct people.
  A final structural audit also found three legacy INBOX branch records with
  author/contact/signature keys despite zero email-pattern matches; those were
  minimized too. Thus six historical branch records were cleaned, in addition
  to the two already-minimal005 acquisition records. Pattern matching alone
  is not an adequate contact/signature-field-removal policy.
- The four earlier local ZIPs scanned with zero email-pattern matches and did
  not need rewriting. New fetch/acquisition metadata is minimal from creation.
  A pattern scan is a scoped hygiene check, not a general proof of no personal
  data. No remotely uploaded historical file was edited or removed by us.

Current root has109 unique rows:108 prior claims with their original statements/
evidence labels plus ONE `EXECUTABLE_REGRESSION_CHECK` row for this bounded
software repair. Compilation-only external review is a separate field; the new
repair remains submitter-tested/unreviewed. The 108-row completed004 view remains
available and explicitly separated from the 003/78 intake snapshot and005/109
current workflow. No source/label/canonical-copy debate is a research finding.

## 9. Requested review and next bounded work

**For Researcher 001/AuditorSeat002 via the owner:**

1. Verify that the new K3 companion calls the actual source helper, uses returned
   y on identity left sides, and rejects a wrong branch rather than constructing
   an answer. Independently design constant-answer, wrong-winner, tie, inactive
   guard and epsilon-loss controls; rerunning ours alone is not independent
   adversarial design. Decide any artifact/erratum registration and downstream
   command wording only after review. No automatic registry promotion is asked.
2. Keep the 94-declaration compilation result separate from library-grade review.
   Statement fidelity still needs global guard, epsilon>0,H0, h=gamma*dt,
   positive config.q, drive diagonal−mu/gamma and namespace/integration review.
   Same/fixed INPUT results are not coupled phase locking; infinite-tail drive
   bands remain hypotheses. No main integration is claimed.
3. If accepted, implement this one finding on its own repair branch from THEN-
   current main; do not directly merge an inbox/salvage tree. Engine complex-NaN
   and oracle uniqueness fixes must have their own failing-before/passing-after
   tests on separate branches. This packet contains neither patch.

**Next selected local cycle006:** review the existing v4.1 candidate's held-event
semantics/estimands and boundary interval wording against fresh main, with an
independent small oracle and boundary controls. Do not simply rerun/rediscover
the frozen-v4 failure or promote a fixed-cohort diagnostic to population CI.
If already resolved, choose the next still-open small engine/oracle repair after
refresh rather than duplicate it.

**Lean science remains queued:** exact delay-buffer and phase-step semantics;
sharper local envelope/derived ON bands; gated-OFF and finite-edge aggregation.
No full Python/float64 linkage, future-band derivation, explicit freeze-time,
selected-controller rate law or coupled locking proof is supplied by005.

The bounded cycle ends after packaging and local validation. There is no process
left running and no unattended work between turns.

## Source navigation

Paths below are reproduction/scope metadata, not findings about version labels.

- Main tested source: `https://github.com/jacobbrainard84-knightninja/AIEFS/tree/f3e3a57632c613e860a9941f007732cb4c2c91c6`.
- Bridge: `AIEF_1_4_proposal_equalization_bridge_analysis.py`, coefficient182–195,
  synthetic test198–267, dispatch358–369, actual replay intermediates390–460.
- Operator: `AIEF_1_4_actual_admissibility_branch_audit.py:211–252`;
  incidence specification in stationarity base105–110.
- Saved manifest/report: `aief_1_4_proposal_equalization_bridge/analysis_manifest.json`
  and `proposal_equalization_report.txt`.
- Registry context: `registry/artifacts.csv`, ART-0050; no row changed.
- Received intake: `audit_inbox/2026-11-08_auditor-seat-002_researcher-040282-intake.md`.
- Received R001 triage: `audit_inbox/2026-11-08_auditor-seat-002_workspace-notes/TRIAGE_r040282.md`.
- Current candidate queued for006:
  `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py`.

## Appendix A — complete critical files

{{CRITICAL_FILES}}

## Appendix B — actual final local result record

{{RESULTS}}

## Appendix C — preregistration, privacy and review/provenance records

{{RECORDS}}
