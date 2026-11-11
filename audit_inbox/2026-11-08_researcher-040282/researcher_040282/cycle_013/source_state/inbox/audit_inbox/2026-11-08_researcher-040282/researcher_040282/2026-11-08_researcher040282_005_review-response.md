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

### Researcher 040282 — cycle 004 administrative addendum

**Owner/seat handoff label: 2026-11-08. Scientific content and seeds preserved.**

1. **Date correction.** Withdraw the September 4 stamp in
   `2026-09-04_researcher040282_004_complex-ema.md` as chronological production/
   execution provenance; retain its filename for stable citation. I carried an
   inappropriate preparation stamp into that handoff. November 8 here is the
   owner-supplied review label, **not** a reconstructed execution timestamp.
   This session supplies September 4 as its preparation date; no historical run
   date is inferred from that clock or compiler build dates. Proof content and
   seeds `20260904` / `2026090404` are unchanged.

2. **Completed 004 means 004/108, not 003/78.** Both the original checker and
   extracted rerun finished with exit 0: 18 intended controls, 34 valid
   `compute_R` cases / 253 calls each, plus a separate invalid-alpha rejection.
   Those are historical 004 outcomes, not new Lean executions in 005. The older
   uploaded root really stops at 003/78. This packet supplies
   `cycle_005/completed_004_snapshot/COMPLETED_004_STATE.json` and
   `CLAIM_LEDGER_COMPLETED_004.csv` with 108 rows. The NEW live root is 005/109:
   one additional software-regression record, not a changed 004 count. README,
   STATE, QUEUE and ledger agree.

3. **Review scope.** Researcher 001 reports independently compiling
   22 / 44 / 22+6 declarations, zero warnings/errors and standard axiom footprints.
   Record compilation/footprint confirmation separately from submitter labels.
   Our controls, ZIP checkers and numerical suites were not independently run;
   statement fidelity, independent controls and library integration are pending.
   No blanket promotion to independently approved evidence is made.

4. **Privacy and logs.** The three reported contact-bearing metadata files now
   contain only branch/commit identifiers and a policy note, omitting contact
   fields AND signed payloads without unredacted backups. Three additional
   legacy inbox-branch records were structurally minimized too, despite zero
   email-pattern matches. The four earlier ZIPs were unchanged and scan free of
   such matches. Cited logs are now UNPACKED under `researcher_040282/` in the 005
   ZIP: see `EVIDENCE_INDEX.json` and `HISTORICAL_ARCHIVE_LOG_MAP.csv`. No current
   ledger evidence remains archive-only. Remote uploads were not edited.

The 005 companion report names the exact tested main and proposes only a new-file
bridge self-test/erratum. Nothing was pushed, merged, automatically uploaded, or
communicated directly to the other seats.


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

### PROPOSED erratum: ART-0050 synthetic K3 assurance

**Owner/seat review required; not an approved registry erratum.** Existing
ART-0050 and saved output files remain unchanged. Test base:
`f3e3a57632c613e860a9941f007732cb4c2c91c6` on main.

#### Correction

Withdraw the interpretation that ART-0050's existing `--self-test` PASS certifies
its K3 fixture against the implemented admissibility map. The isolated proposal
`(x25,x29,x59)=(.41,.31,.27)` has actual winners `(2,2,7)`, not `(7,2,7)`.
The left-identity residual using the current-main edge-coordinate operator is
`-0.02121459694983044`, against the old `1e-14` allowance. The old synthetic test
constructs its own projected answer and never calls that operator.

This is the previously reported B-F4 mechanism, independently reproduced by
Researcher 001 on their earlier main and locally reproduced on the tested main;
it is not a new mathematical counterexample to the CONDITIONAL identity.

#### New-file proposal, not an in-place fix

Add `AIEF_1_4_proposal_equalization_branch_selftest_r040282.py` as a reviewed
synthetic K3 companion. Add its regression test as a separate reviewable file.
An owner/seat may later assign an artifact/erratum ID and decide registry wording;
no ID or status promotion is asserted by this proposal.

The companion calls
`AIEF_1_4_actual_admissibility_branch_audit.admissibility_from_nonnegative_proposal`
on the full isolated12-node vector, verifies the public incidence layout, and
compares ALL operator outputs/branch metadata with a separate Fraction-loop map.
It checks identities using actual returned `y`, not a reconstructed projection.
This pure edge-coordinate audit helper is not a fresh call to the production
engine's full delayed `advance_state` or a real-data bridge replay.

Default positive fixture: `(.41,.27,.31)`, observed winners `(7,2,7)`.
The old fixture, a tie and an inactive gate are rejected as strict-branch tests.
Corrupted output/winner metadata, a constant default projection, unguarded scaling,
and an epsilon-dropped coefficient are detected by the accompanying controls.
The proposal is snapshotted/oracle-evaluated before the call; a test double that
rewrites it to a default answer is rejected. That mutation falsifier exposed and
repaired a flaw in the first local candidate, not an upstream-helper mutation.
No core decision relies on removable Python assertions.

From an upstream-root integration after review:

```sh
python AIEF_1_4_proposal_equalization_branch_selftest_r040282.py --self-test
python AIEF_1_4_proposal_equalization_branch_selftest_r040282.py --self-test --fixture .41 .31 .27
### Second command must exit2, report BranchMismatch, and print no PASS.
```

Outside an upstream root, set `R040282_AIEFS_SOURCE` to the reviewed source
directory. Full reproduction (including legacy-red/candidate-green comparison)
is in the cycle005 standalone packet. Twenty-one unittest methods pass normally
and under `-O`;64 seeded perturbations plus one default positive are finite
numerical checks at absolute1e-14,relative0, not a universal float64 proof.

#### What this does not correct or establish

- The original script remains a frozen historical artifact and will still print
  its old PASS; the erratum withdraws that PASS's claimed K3 coverage.
- The new companion only replaces the K3 assurance. It does not rerun/replace the
  old proposal-difference, directed-radial, or forced-recurrence self-test blocks.
- No production parameter, dynamics, conditional theorem, replay trajectory,
  identity summary, artifact registry row, or saved report is changed.
- The inspected saved bridge command omits `--self-test`; source dispatch returns
  immediately from that flag's branch. This makes the false synthetic PASS
  separate from the recorded normal replay path. That is static provenance
  evidence, not a fresh replay, an exhaustive dependence audit, or proof that
  every historic wrapper avoided the flag.
- The manifest's smallest saved winner margin is about 4.44e-14, whereas the new
  finite positive fixtures have comfortable margins. These tests do not certify
  that saved near-tie states have any floating-point robustness guarantee.
- No coupled locking, future branch persistence or rate-law conclusion follows.

#### Requested disposition

Owner uploads only to a dated audit-inbox handoff. Review the proposal FROM
current main, keep this one finding on its own repair branch if accepted, and
run independently designed wrong-branch/constant-answer/epsilon/tie controls.
Do not merge inbox or salvage worktrees directly into main. Engine complex-NaN,
oracle uniqueness, v4.1 inference/estimand review, and Lean integration are
separate work items. Nothing was pushed or submitted by this agent.


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

**Actually executed, not just prepared.** All six inline files were extracted into a fresh directory, matched the supplied sources, and ran against ten freshly fetched public dependency modules. The extracted runner again returned0: legacy red3 failures/0 errors, candidate21 pass normally and21 pass optimized,65 valid comparisons. This is submitter-local self-reproduction, not independent-seat confirmation.

```json
{
  "actually_executed": true,
  "runner_exit": 0,
  "report": "2026-11-08_researcher040282_005_review-response.md",
  "critical_files": [
    "AIEF_1_4_proposal_equalization_branch_selftest_r040282.py",
    "extract_from_report.py",
    "fetch_public_dependencies.py",
    "run_checks.py",
    "source_modules.json",
    "test_proposal_equalization_branch_selftest_r040282.py"
  ],
  "critical_file_count": 6,
  "all_extracted_files_match_supplied_sources": true,
  "fresh_public_modules_fetched_and_verified": 10,
  "tested_main": "f3e3a57632c613e860a9941f007732cb4c2c91c6",
  "legacy_expected_failures": 3,
  "legacy_errors": 0,
  "candidate_methods_passed": 22,
  "candidate_methods_passed_optimized": 22,
  "positive_perturbation_cases": 64,
  "default_plus_perturbations": 65,
  "results_match_original_numerically": true,
  "elapsed_runner_seconds": 9.68835204700008,
  "result_file": "cycle_005/standalone/checks/cycle_results.json",
  "log": "cycle_005/standalone/reproduction.log",
  "fetch_log": "cycle_005/standalone/public_fetch.log",
  "scope": "Submitter-local one-note self-reproduction with public dependencies; not independent controls/review, production replay, or proof"
}
```


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

### AIEF_1_4_proposal_equalization_branch_selftest_r040282.py

<!-- BEGIN_CRITICAL_FILE: AIEF_1_4_proposal_equalization_branch_selftest_r040282.py -->
```python
"""PROPOSED companion/erratum self-test, not a change to pinned ART-0050.

Tested base: f3e3a57632c613e860a9941f007732cb4c2c91c6.
Finite synthetic K3 checks only: no replay, proof, locking, or approval claim.
Import the actual operator; do not construct its purported output from winners.
Optional R040282_AIEFS_SOURCE points to a reviewed local AIEFS source directory.
No downloading, main-file edits, or production-data writes occur here.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import sys

if os.environ.get('R040282_AIEFS_SOURCE'):
    sys.path.insert(0, str(Path(os.environ['R040282_AIEFS_SOURCE']).resolve()))

import numpy as np
import AIEF_1_4_actual_admissibility_branch_audit as actual
import AIEF_1_4_proposal_equalization_bridge_analysis as legacy

N = 12
SELECTED = (25, 29, 59)
EXPECTED_WINNERS = (7, 2, 7)
DEFAULT_FIXTURE = (0.41, 0.27, 0.31)
CAPACITY = 0.6333333333333333
EPSILON = 1e-12
ATOL = 1e-14
# Independent public edge-coordinate specification, not base.incidence_matrix.
PAIRS = tuple((i, j) for i in range(N) for j in range(i + 1, N))


class VerificationError(ValueError):
    """A numerical/structural check failed; never print PASS afterwards."""


class BranchMismatch(VerificationError):
    """The strict conditional-identity hypotheses were not certified."""


def require(condition, message, error=VerificationError):
    # Deliberately not a removable Python assert: works under python -O/-OO.
    if not bool(condition):
        raise error(message)


def finite_scalar(value, name, positive=False):
    result = float(value)
    require(math.isfinite(result), name + ' must be finite')
    require(result > 0.0 if positive else result >= 0.0,
            name + (' must be positive' if positive else ' must be nonnegative'))
    return result


def fraction_reference(x, capacity, epsilon):
    """Separate exact-rational loop oracle embedding the supplied binary floats.

    This models the guarded post-positivity MAP, not floating-point execution.
    It never calls the actual operator or the legacy analytical coefficient.
    """
    values = [Fraction.from_float(float(value)) for value in x]
    cap = Fraction.from_float(float(capacity))
    eps = Fraction.from_float(float(epsilon))
    rows = [Fraction(0) for _ in range(N)]
    for value, (i, j) in zip(values, PAIRS):
        rows[i] += value
        rows[j] += value
    on = any(row > cap for row in rows)
    scales = [min(Fraction(1), cap / (row + eps)) if on else Fraction(1)
              for row in rows]
    edge_scales, winners, y = [], [], []
    for value, (i, j) in zip(values, PAIRS):
        factor = min(scales[i], scales[j])
        if not on or (scales[i] == 1 and scales[j] == 1):
            winner = -1
        elif scales[i] < scales[j]:
            winner = i
        elif scales[j] < scales[i]:
            winner = j
        else:
            winner = -2
        edge_scales.append(factor)
        winners.append(winner)
        y.append(value * factor)
    return {'q': rows, 'gate_on': on, 'scales': scales,
            'violating': [row > cap for row in rows],
            'clipped': [on and factor < 1 for factor in scales],
            'edge_scales': edge_scales, 'winner_code': winners, 'y': y}


def compare_numeric(observed, expected, name):
    values = np.asarray(observed)
    reference = np.array([float(value) for value in expected], dtype=float)
    require(values.shape == reference.shape, name + ': shape mismatch')
    require(values.dtype.kind in 'fiu', name + ': non-real numeric values')
    require(np.isfinite(values).all(), name + ': nonfinite values')
    error = float(np.max(np.abs(values - reference), initial=0.0))
    require(error <= ATOL, name + ': exceeds fixed absolute tolerance')
    return error


def verify_operator_fixture(values, *, capacity=CAPACITY, epsilon=EPSILON):
    """Check the actual full operator against the independent guarded oracle.

    Nonnegative isolated inputs allowed here; strict branch admission is separate.
    Returns ACTUAL y/info, never an oracle-manufactured projected answer.
    """
    values = tuple(values)
    require(len(values) == 3, 'exactly three selected-edge values required')
    values = tuple(finite_scalar(value, 'proposal') for value in values)
    capacity = finite_scalar(capacity, 'capacity')
    epsilon = finite_scalar(epsilon, 'epsilon', positive=True)
    x = np.zeros(len(PAIRS), dtype=float)
    x[list(SELECTED)] = values
    A, edges = actual.base.incidence_matrix(N)
    layout = tuple((int(i), int(j)) for i, j in zip(*edges))
    require(layout == PAIRS, 'incidence edge layout differs from public specification')
    reference_A = np.zeros((N, len(PAIRS)))
    for edge, (i, j) in enumerate(PAIRS):
        reference_A[i, edge] = reference_A[j, edge] = 1.0
    require(np.array_equal(A, reference_A), 'incidence matrix differs from specification')
    # Preserve the REQUESTED input before external code can change an argument.
    # Otherwise a mutating constant-answer operator could move the oracle too.
    requested_x = x.copy()
    oracle = fraction_reference(requested_x, capacity, epsilon)
    # This call is the central wiring requirement. Do not replace it with algebra.
    y, info = actual.admissibility_from_nonnegative_proposal(
        x, np.full(N, capacity), A, edges, epsilon)
    require(np.array_equal(x, requested_x), 'operator mutated supplied proposal')
    require(isinstance(info, dict), 'operator metadata must be a dictionary')
    errors = {'y': compare_numeric(y, oracle['y'], 'projected output')}
    for field in ('q', 'scales', 'edge_scales'):
        require(field in info, 'operator metadata missing ' + field)
        errors[field] = compare_numeric(info[field], oracle[field], field)
    require(isinstance(info.get('gate_on'), (bool, np.bool_)), 'gate flag must be boolean')
    require(bool(info['gate_on']) == oracle['gate_on'], 'global guard mismatch')
    for field in ('violating', 'clipped', 'winner_code'):
        observed = np.asarray(info.get(field))
        expected = np.asarray(oracle[field])
        require(observed.shape == expected.shape, field + ': shape mismatch')
        require(observed.dtype.kind in ('iu' if field == 'winner_code' else 'b'),
                field + ': wrong metadata type')
        require(np.array_equal(observed, expected), field + ': oracle mismatch')
    return {'x': x, 'y': np.asarray(y), 'info': info, 'edges': edges,
            'oracle': oracle, 'max_oracle_errors': errors,
            'capacity': capacity, 'epsilon': epsilon}


def check_branch_fixture(values=DEFAULT_FIXTURE, *, capacity=CAPACITY, epsilon=EPSILON):
    checked = verify_operator_fixture(values, capacity=capacity, epsilon=epsilon)
    x, y, info = checked['x'], checked['y'], checked['info']
    winners = tuple(int(info['winner_code'][edge]) for edge in SELECTED)
    require(winners == EXPECTED_WINNERS,
            f'expected strict winners {EXPECTED_WINNERS}; observed {winners}', BranchMismatch)
    require(info['gate_on'], 'global gate is inactive', BranchMismatch)
    require(np.all(x[list(SELECTED)] > 0.0), 'selected edge is not positive', BranchMismatch)
    require(info['q'][2] > capacity and info['q'][7] > capacity,
            'controller rows are not both over capacity', BranchMismatch)
    require(info['clipped'][2] and info['clipped'][7],
            'controller scales are not both clipped', BranchMismatch)
    require(0.0 < info['scales'][2] < 1.0 and 0.0 < info['scales'][7] < 1.0,
            'controller scales must be in (0,1)', BranchMismatch)
    outside = np.ones(len(x), dtype=bool)
    outside[list(SELECTED)] = False
    require(not np.any(x[outside]) and not np.any(y[outside]), 'support not isolated')
    margins = []
    for edge in SELECTED:
        i, j = (int(part[edge]) for part in checked['edges'])
        margin = abs(float(info['scales'][i] - info['scales'][j]))
        require(margin > 0.0, 'endpoint scale tie', BranchMismatch)
        margins.append(margin)
    left_residual = float((y[25] - y[59]) - info['scales'][7] * (x[25] - x[59]))
    coefficient = float(legacy.right_projection_coefficient(
        x[25], x[29], x[59], capacity, epsilon))
    require(math.isfinite(coefficient) and 0.0 < coefficient < 1.0,
            'right coefficient is not in (0,1)')
    right_residual = float((y[59] - y[29]) - coefficient * (x[59] - x[29]))
    require(math.isfinite(left_residual) and abs(left_residual) <= ATOL,
            'left identity exceeds fixed absolute tolerance')
    require(math.isfinite(right_residual) and abs(right_residual) <= ATOL,
            'right identity exceeds fixed absolute tolerance')
    return {'fixture': [float(x[e]) for e in SELECTED],
            'actual_winners': list(winners), 'gate_on': bool(info['gate_on']),
            'selected_projected_output': [float(y[e]) for e in SELECTED],
            'capacity': capacity, 'epsilon': epsilon,
            'minimum_winner_margin': min(margins),
            'left_residual': left_residual, 'right_residual': right_residual,
            'max_oracle_errors': checked['max_oracle_errors'],
            'absolute_tolerance': ATOL, 'relative_tolerance': 0.0}


def synthetic_self_test(values=DEFAULT_FIXTURE, *, epsilon=EPSILON):
    result = check_branch_fixture(values, epsilon=epsilon)
    print(json.dumps(result, sort_keys=True))
    print('Branch-faithful K3 projection self-test: PASS')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true',
                        help='compatibility flag; this companion only runs synthetic checks')
    parser.add_argument('--fixture', nargs=3, type=float, default=DEFAULT_FIXTURE,
                        metavar=('X25', 'X29', 'X59'))
    parser.add_argument('--epsilon', type=float, default=EPSILON)
    args = parser.parse_args()
    try:
        synthetic_self_test(args.fixture, epsilon=args.epsilon)
    except VerificationError as error:
        print(type(error).__name__ + ': ' + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
```
<!-- END_CRITICAL_FILE: AIEF_1_4_proposal_equalization_branch_selftest_r040282.py -->

### test_proposal_equalization_branch_selftest_r040282.py

<!-- BEGIN_CRITICAL_FILE: test_proposal_equalization_branch_selftest_r040282.py -->
```python
"""Own finite regression controls; NOT an independent seat's controls.

R040282_SELFTEST_TARGET=legacy runs the same three common contract tests on the
pinned entry point. Their expected failures establish red-before/green-after.
Default runs the common contract plus specific candidate/admission/mutation tests.
No frozen source file is changed. All substitutions are restored in-process mocks.
"""
from __future__ import annotations
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import AIEF_1_4_proposal_equalization_branch_selftest_r040282 as candidate

actual = candidate.actual
legacy = candidate.legacy
REAL_OPERATOR = actual.admissibility_from_nonnegative_proposal
TARGET = os.environ.get('R040282_SELFTEST_TARGET', 'candidate')


def target_function():
    return legacy.synthetic_self_test if TARGET == 'legacy' else candidate.synthetic_self_test


def corrupt_output(*args, **kwargs):
    y, info = REAL_OPERATOR(*args, **kwargs)
    y = y.copy()
    y[25] += 1e-4
    return y, info


class CommonRegressionContract(unittest.TestCase):
    def test_queries_real_operator_before_claiming_pass(self):
        calls = []
        def observed(*args, **kwargs):
            calls.append(True)
            return REAL_OPERATOR(*args, **kwargs)
        with mock.patch.object(actual, 'admissibility_from_nonnegative_proposal', observed):
            with contextlib.redirect_stdout(io.StringIO()):
                target_function()()
        self.assertGreater(len(calls), 0, 'self-test must query the actual operator')

    def test_cannot_pass_when_real_operator_is_unavailable(self):
        output = io.StringIO()
        with mock.patch.object(actual, 'admissibility_from_nonnegative_proposal',
                               side_effect=RuntimeError('sentinel real-operator failure')):
            with contextlib.redirect_stdout(output):
                with self.assertRaisesRegex(RuntimeError, 'sentinel real-operator failure'):
                    target_function()()
        self.assertNotIn('PASS', output.getvalue())

    def test_cannot_pass_with_corrupted_actual_output(self):
        output = io.StringIO()
        with mock.patch.object(actual, 'admissibility_from_nonnegative_proposal', corrupt_output):
            with contextlib.redirect_stdout(output):
                with self.assertRaises(candidate.VerificationError):
                    target_function()()
        self.assertNotIn('PASS', output.getvalue())


class BranchAndOracleControls(unittest.TestCase):
    def test_positive_fixture_uses_expected_actual_branch(self):
        result = candidate.check_branch_fixture()
        self.assertEqual(result['actual_winners'], [7, 2, 7])
        self.assertLessEqual(abs(result['left_residual']), candidate.ATOL)
        self.assertLessEqual(abs(result['right_residual']), candidate.ATOL)

    def test_old_fixture_rejected_with_actual_wrong_winners(self):
        checked = candidate.verify_operator_fixture((.41, .31, .27))
        winners = checked['info']['winner_code'][list(candidate.SELECTED)].tolist()
        self.assertEqual(winners, [2, 2, 7])
        with self.assertRaisesRegex(candidate.BranchMismatch, r'observed \(2, 2, 7\)'):
            candidate.check_branch_fixture((.41, .31, .27))

    def test_endpoint_tie_rejected_not_relabelled_strict(self):
        checked = candidate.verify_operator_fixture((.41, .29, .29))
        self.assertEqual(int(checked['info']['winner_code'][25]), -2)
        with self.assertRaises(candidate.BranchMismatch):
            candidate.check_branch_fixture((.41, .29, .29))

    def test_inactive_gate_rejected_not_assumed_clipped(self):
        checked = candidate.verify_operator_fixture((.10, .07, .08))
        self.assertFalse(checked['info']['gate_on'])
        with self.assertRaises(candidate.BranchMismatch):
            candidate.check_branch_fixture((.10, .07, .08))

    def test_zero_selected_edge_rejected(self):
        with self.assertRaises(candidate.BranchMismatch):
            candidate.check_branch_fixture((.41, 0.0, .31))

    def test_nonfinite_negative_values_and_nonpositive_epsilon_rejected(self):
        for values in ((float('nan'), .27, .31), (float('inf'), .27, .31),
                       (-.41, .27, .31)):
            with self.subTest(values=str(values)):
                with self.assertRaises(candidate.VerificationError):
                    candidate.check_branch_fixture(values)
        for epsilon in (0.0, -1e-12, float('nan'), float('inf')):
            with self.subTest(epsilon=str(epsilon)):
                with self.assertRaises(candidate.VerificationError):
                    candidate.check_branch_fixture(epsilon=epsilon)

    def test_all_64_preregistered_perturbations(self):
        rng = np.random.default_rng(2026090405)
        draws = rng.uniform([.39, .26, .30], [.42, .28, .32], size=(32, 3))
        for index, values in enumerate(draws):
            for epsilon in (1e-12, 1e-2):
                with self.subTest(index=index, epsilon=epsilon):
                    result = candidate.check_branch_fixture(values, epsilon=epsilon)
                    self.assertEqual(result['actual_winners'], [7, 2, 7])

    def test_exact_loop_oracle_is_not_the_operator(self):
        with mock.patch.object(actual, 'admissibility_from_nonnegative_proposal',
                               side_effect=RuntimeError('oracle must not query operator')):
            x = np.zeros(66)
            x[list(candidate.SELECTED)] = candidate.DEFAULT_FIXTURE
            oracle = candidate.fraction_reference(x, candidate.CAPACITY, candidate.EPSILON)
        self.assertEqual(oracle['winner_code'][25], 7)
        self.assertEqual(type(oracle['y'][25]).__name__, 'Fraction')

    def test_unguarded_candidate_scaling_is_detected(self):
        values = (.10, .07, .08)
        checked = candidate.verify_operator_fixture(values, epsilon=2.0)
        self.assertFalse(checked['info']['gate_on'])
        np.testing.assert_array_equal(checked['x'], checked['y'])
        def unguarded(*args, **kwargs):
            x, capacities, A, edges, epsilon = args
            y, info = REAL_OPERATOR(*args, **kwargs)
            scales = np.minimum(1.0, capacities / (A @ x + epsilon))
            return x * np.minimum(scales[edges[0]], scales[edges[1]]), info
        with mock.patch.object(actual, 'admissibility_from_nonnegative_proposal', unguarded):
            with self.assertRaisesRegex(candidate.VerificationError, 'projected output'):
                candidate.verify_operator_fixture(values, epsilon=2.0)

    def test_corrupted_winner_metadata_cannot_pass(self):
        def wrong_winner(*args, **kwargs):
            y, info = REAL_OPERATOR(*args, **kwargs)
            info['winner_code'] = info['winner_code'].copy()
            info['winner_code'][25] = 2
            return y, info
        with mock.patch.object(actual, 'admissibility_from_nonnegative_proposal', wrong_winner):
            with self.assertRaisesRegex(candidate.VerificationError, 'winner_code'):
                candidate.check_branch_fixture()

    def test_constant_default_projection_cannot_pass_changed_input(self):
        frozen = candidate.verify_operator_fixture(candidate.DEFAULT_FIXTURE)['y'].copy()
        def constant_projection(*args, **kwargs):
            _, info = REAL_OPERATOR(*args, **kwargs)
            return frozen.copy(), info
        with mock.patch.object(actual, 'admissibility_from_nonnegative_proposal', constant_projection):
            with self.assertRaisesRegex(candidate.VerificationError, 'projected output'):
                candidate.check_branch_fixture((.40, .26, .30))

    def test_operator_cannot_replace_requested_fixture_in_place(self):
        def replace_request(*args, **kwargs):
            x = args[0]
            x[:] = 0.0
            x[list(candidate.SELECTED)] = candidate.DEFAULT_FIXTURE
            return REAL_OPERATOR(*args, **kwargs)
        with mock.patch.object(actual, 'admissibility_from_nonnegative_proposal', replace_request):
            with self.assertRaisesRegex(candidate.VerificationError, 'mutated supplied proposal'):
                candidate.check_branch_fixture((.40, .26, .30))

    def test_wrong_incidence_matrix_cannot_pass(self):
        A, edges = actual.base.incidence_matrix(12)
        A[2, 25] = 0.0
        with mock.patch.object(actual.base, 'incidence_matrix', return_value=(A, edges)):
            with self.assertRaisesRegex(candidate.VerificationError, 'incidence matrix'):
                candidate.check_branch_fixture()

    def test_dropping_epsilon_from_analytical_coefficient_is_detected(self):
        def omitted(x25, x29, x59, capacity, epsilon):
            return capacity * x25 / ((x25 + x59) * (x25 + x29))
        with mock.patch.object(legacy, 'right_projection_coefficient', omitted):
            with self.assertRaisesRegex(candidate.VerificationError, 'right identity'):
                candidate.check_branch_fixture(epsilon=1e-2)

    def test_dependency_failure_is_not_a_branch_mismatch(self):
        with mock.patch.object(actual, 'admissibility_from_nonnegative_proposal',
                               side_effect=ImportError('sentinel dependency failure')):
            with self.assertRaisesRegex(ImportError, 'sentinel dependency failure'):
                candidate.check_branch_fixture()


class CLIControls(unittest.TestCase):
    def run_cli(self, *args, optimized=False, env=None):
        command = [sys.executable]
        if optimized:
            command.append('-O')
        command += ['-B', str(Path(candidate.__file__).resolve()), '--self-test', *args]
        return subprocess.run(command, text=True, capture_output=True, timeout=30,
                              env=os.environ.copy() if env is None else env)

    def test_positive_cli(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS', result.stdout)
        self.assertEqual(json.loads(result.stdout.splitlines()[0])['actual_winners'], [7, 2, 7])

    def test_wrong_fixture_cli_nonzero_and_no_pass(self):
        result = self.run_cli('--fixture', '.41', '.31', '.27')
        self.assertEqual(result.returncode, 2)
        self.assertIn('BranchMismatch', result.stderr)
        self.assertNotIn('PASS', result.stdout)

    def test_wrong_fixture_optimized_cli_nonzero_and_no_pass(self):
        result = self.run_cli('--fixture', '.41', '.31', '.27', optimized=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('BranchMismatch', result.stderr)
        self.assertNotIn('PASS', result.stdout)

    def test_missing_source_modules_block_instead_of_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            env = os.environ.copy()
            env['R040282_AIEFS_SOURCE'] = directory
            env.pop('PYTHONPATH', None)
            result = self.run_cli(env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ModuleNotFoundError', result.stderr)
        self.assertNotIn('PASS', result.stdout)


def main():
    loader = unittest.defaultTestLoader
    if TARGET == 'legacy':
        suite = loader.loadTestsFromTestCase(CommonRegressionContract)
    elif TARGET == 'candidate':
        suite = loader.loadTestsFromModule(sys.modules[__name__])
    else:
        raise ValueError('unknown target')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {'target': TARGET, 'tests_run': result.testsRun,
               'failures': [{'test': case.id(), 'traceback': trace}
                            for case, trace in result.failures],
               'errors': [{'test': case.id(), 'traceback': trace}
                          for case, trace in result.errors],
               'skipped': len(result.skipped), 'success': result.wasSuccessful()}
    if os.environ.get('R040282_TEST_RESULTS'):
        Path(os.environ['R040282_TEST_RESULTS']).write_text(json.dumps(summary, indent=2) + '\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: test_proposal_equalization_branch_selftest_r040282.py -->

### run_checks.py

<!-- BEGIN_CRITICAL_FILE: run_checks.py -->
```python
"""Run source-pinned red/green controls and finite branch comparisons.

A successful overall exit requires expected legacy regression failures (not
errors), normal and optimized candidate success, and unchanged upstream modules.
This is submitter-local software evidence, not an independent review or proof.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest import mock

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def verify_sources(source, manifest):
    for record in manifest['modules']:
        data = (source / record['path']).read_bytes()
        require(git_blob(data) == record['blob'] and len(data) == record['bytes'],
                'Upstream source differs from tested base: ' + record['path'])


def run_tests(source, output, name, target, optimized=False):
    env = os.environ.copy()
    env['R040282_AIEFS_SOURCE'] = str(source)
    env['R040282_SELFTEST_TARGET'] = target
    env['R040282_TEST_RESULTS'] = str(output / (name + '.json'))
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env.pop('PYTHONPATH', None)
    command = [sys.executable]
    if optimized:
        command.append('-O')
    command += ['-B', str(HERE / 'test_proposal_equalization_branch_selftest_r040282.py')]
    start = time.perf_counter()
    result = subprocess.run(command, cwd=HERE, env=env, capture_output=True, text=True, timeout=180)
    (output / (name + '.log')).write_text(result.stdout + result.stderr)
    summary = json.loads((output / (name + '.json')).read_text())
    return {'name': name, 'returncode': result.returncode, 'tests_run': summary['tests_run'],
            'failures': len(summary['failures']), 'errors': len(summary['errors']),
            'skipped': summary['skipped'], 'success': summary['success'],
            'elapsed_seconds': time.perf_counter() - start}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('checks'))
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((HERE / 'source_modules.json').read_text())
    verify_sources(source, manifest)
    start = time.perf_counter()
    red = run_tests(source, output, 'red_legacy', 'legacy')
    require(red['returncode'] == 1 and red['tests_run'] == 3 and red['failures'] == 3
            and red['errors'] == 0 and red['skipped'] == 0, 'Legacy red baseline did not match preregistration')
    green = run_tests(source, output, 'green_candidate', 'candidate')
    optimized = run_tests(source, output, 'green_candidate_optimized', 'candidate', optimized=True)
    for result in (green, optimized):
        require(result['returncode'] == 0 and result['success'] and result['tests_run'] == 22
                and result['failures'] == result['errors'] == result['skipped'] == 0,
                'Candidate suite not clean: ' + result['name'])
    os.environ['R040282_AIEFS_SOURCE'] = str(source)
    module = importlib.import_module('AIEF_1_4_proposal_equalization_branch_selftest_r040282')
    actual, legacy = module.actual, module.legacy
    real = actual.admissibility_from_nonnegative_proposal
    call_counts, stdout = {}, {}
    for name, function in [('legacy', legacy.synthetic_self_test), ('candidate', module.synthetic_self_test)]:
        calls = []
        def observed(*args, **kwargs):
            calls.append(True)
            return real(*args, **kwargs)
        stream = io.StringIO()
        with mock.patch.object(actual, 'admissibility_from_nonnegative_proposal', observed):
            with contextlib.redirect_stdout(stream):
                function()
        call_counts[name] = len(calls)
        stdout[name] = stream.getvalue().strip()
    require(call_counts['legacy'] == 0 and call_counts['candidate'] > 0,
            'Observed entry-point wiring differed from red/green expectation')
    wrong = module.verify_operator_fixture((.41, .31, .27))
    x, y, info = wrong['x'], wrong['y'], wrong['info']
    wrong_witness = {
        'fixture': [.41, .31, .27],
        'actual_winners': info['winner_code'][list(module.SELECTED)].tolist(),
        'assumed_legacy_winners': [7, 2, 7],
        'left_identity_residual_real_operator': float((y[25] - y[59]) - info['scales'][7] * (x[25] - x[59])),
        'legacy_stdout': stdout['legacy'], 'legacy_actual_operator_calls': call_counts['legacy'],
        'candidate_default_actual_operator_calls': call_counts['candidate'],
    }
    require(wrong_witness['actual_winners'] == [2, 2, 7] and 'PASS' in stdout['legacy'],
            'Legacy witness no longer matches inspected source')
    require(abs(wrong_witness['left_identity_residual_real_operator']) > module.ATOL,
            'Wrong-branch fixture unexpectedly satisfied left identity')
    import numpy as np
    rng = np.random.default_rng(2026090405)
    draws = rng.uniform([.39, .26, .30], [.42, .28, .32], size=(32, 3))
    default_positive = module.check_branch_fixture()
    cases = [module.check_branch_fixture(values, epsilon=epsilon)
             for values in draws for epsilon in (1e-12, 1e-2)]
    all_valid = [default_positive, *cases]
    limits = {
        'no_new_lean_compilation': True,
        'finite_synthetic_checks_not_universal_float64_proof': True,
        'legacy_other_selftest_blocks_not_replaced_by_companion': True,
        'saved_production_bridge_replay_not_rerun': True,
        'no_engine_or_oracle_patch_or_v41_result_claimed': True,
        'not_independent_review_library_approval_or_coupled_locking': True,
    }
    verify_sources(source, manifest)
    summary = {
        'tested_source_commit': manifest['commit'], 'verified_unchanged_upstream_modules': len(manifest['modules']),
        'python': sys.version, 'packages': {name: importlib.import_module(name).__version__
                                           for name in ('numpy', 'pandas', 'scipy')},
        'regression_runs': [red, green, optimized],
        'all_preregistered_acceptance_conditions_met': True,
        'legacy_witness': wrong_witness, 'candidate_default_positive': default_positive,
        'perturbation_seed': 2026090405, 'positive_perturbation_cases': len(cases),
        'default_plus_perturbation_cases': len(all_valid),
        'max_abs_left_residual': max(abs(case['left_residual']) for case in all_valid),
        'max_abs_right_residual': max(abs(case['right_residual']) for case in all_valid),
        'max_oracle_errors': {key: max(case['max_oracle_errors'][key] for case in all_valid)
                              for key in default_positive['max_oracle_errors']},
        'absolute_tolerance': module.ATOL, 'relative_tolerance': 0.0,
        'minimum_valid_winner_margin': min(case['minimum_winner_margin'] for case in all_valid),
        'elapsed_seconds': time.perf_counter() - start, 'limits': limits,
    }
    (output / 'cycle_results.json').write_text(json.dumps(summary, indent=2) + '\n')
    (output / 'finite_positive_cases.json').write_text(json.dumps(all_valid, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: run_checks.py -->

### fetch_public_dependencies.py

<!-- BEGIN_CRITICAL_FILE: fetch_public_dependencies.py -->
```python
"""Fetch the ten reviewed public source modules for the bounded self-test.

No Git API commit metadata/contact/signature payloads are requested or stored.
This helper downloads text only; it does not import or execute downloaded code.
Read the files before running the checks. Existing mismatched files are not
silently overwritten. Third-party Python packages must be installed separately.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('upstream'))
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).resolve().parent / 'source_modules.json').read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    def acquire(record):
        name = record['path']
        if Path(name).name != name or not name.endswith('.py'):
            raise ValueError('Unexpected module path')
        target = args.output / name
        if target.exists():
            data = target.read_bytes()
        else:
            url = ('https://raw.githubusercontent.com/' + manifest['repo'] + '/' +
                   manifest['commit'] + '/' + quote(name, safe=''))
            request = urllib.request.Request(url, headers={'User-Agent': 'Researcher-040282-read-only'})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
        if git_blob(data) != record['blob'] or len(data) != record['bytes']:
            raise RuntimeError('Dependency differs from reviewed source: ' + name)
        target.write_bytes(data)
        return name
    with ThreadPoolExecutor(max_workers=4) as pool:
        names = list(pool.map(acquire, manifest['modules']))
    print(json.dumps({'source_commit': manifest['commit'], 'verified_modules': len(names),
                      'downloaded_code_executed_by_helper': False,
                      'metadata_policy': 'no author/committer/contact/signature payloads'}, indent=2))


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: fetch_public_dependencies.py -->

### source_modules.json

<!-- BEGIN_CRITICAL_FILE: source_modules.json -->
```json
{
  "repo": "jacobbrainard84-knightninja/AIEFS",
  "commit": "f3e3a57632c613e860a9941f007732cb4c2c91c6",
  "modules": [
    {
      "path": "AIEF_1_4_actual_admissibility_branch_audit.py",
      "blob": "62f31947cb5cd3504a726ce16a10b565f32337c8",
      "bytes": 56007
    },
    {
      "path": "AIEF_1_4_augmented_tangent_cocycle_analysis.py",
      "blob": "41411831e2ec7060b8423fcb21e0526adb3b3d57",
      "bytes": 47428
    },
    {
      "path": "AIEF_1_4_component_controller_audit.py",
      "blob": "d4641019968622e86cc0165c2c09c395dc9d6932",
      "bytes": 47911
    },
    {
      "path": "AIEF_1_4_exceptional_K3_transition_audit.py",
      "blob": "170e1d3d8b30c4f1c6d99cb3a487af4f222d4ed2",
      "bytes": 44280
    },
    {
      "path": "AIEF_1_4_exceptional_tangent_analysis.py",
      "blob": "7d6be75cc47d1fae023fc73f5b38049cfb8e76ff",
      "bytes": 29136
    },
    {
      "path": "AIEF_1_4_face_spectrum_analysis.py",
      "blob": "58ac3f8f48eec2b54fcafd4710bc44d4ce36bb4c",
      "bytes": 51530
    },
    {
      "path": "AIEF_1_4_frozen_driver_cocycle_analysis.py",
      "blob": "91b14cccbe2290efc9d755599be964494aa08567",
      "bytes": 43681
    },
    {
      "path": "AIEF_1_4_proposal_equalization_bridge_analysis.py",
      "blob": "2fcfff5ad2f594bc4fdc07e394f6bdd34deff07f",
      "bytes": 26879
    },
    {
      "path": "AIEF_1_4_stationarity_perturbation_analysis_updated.py",
      "blob": "c8609e5cd5f2dc91de32c35403eec83882235ed2",
      "bytes": 42626
    },
    {
      "path": "AIEF_1_4_tangent_spectrum_switch_analysis.py",
      "blob": "bdbb11457bf3b18717a3068fa8b0405ef2da1586",
      "bytes": 31163
    }
  ]
}
```
<!-- END_CRITICAL_FILE: source_modules.json -->

### extract_from_report.py

<!-- BEGIN_CRITICAL_FILE: extract_from_report.py -->
```python
"""Extract the six named files from this OWNED standalone audit.

This extracts text only. It does not import or execute code, download anything,
or implement a general untrusted-code security boundary. Review the report and
public dependencies before running the extracted checks.
"""
import argparse
import json
from pathlib import Path
import re

NAMES = {
    'AIEF_1_4_proposal_equalization_branch_selftest_r040282.py',
    'test_proposal_equalization_branch_selftest_r040282.py',
    'run_checks.py', 'fetch_public_dependencies.py',
    'source_modules.json', 'extract_from_report.py',
}
PATTERN = re.compile(
    r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
    r'<!-- END_CRITICAL_FILE: \1 -->', re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    matches = PATTERN.findall(args.report.read_text())
    if len(matches) != len(NAMES) or {name for name, _ in matches} != NAMES:
        raise ValueError('Missing, duplicate or unexpected critical-file blocks')
    args.output.mkdir(parents=True, exist_ok=True)
    for name, text in matches:
        if Path(name).name != name:
            raise ValueError('Unexpected output path')
        target = args.output / name
        content = text + '\n'
        if target.exists() and target.read_text() != content:
            raise ValueError('Existing different extracted file: ' + name)
        target.write_text(content)
    print(json.dumps({'critical_files_extracted': len(matches),
                      'code_executed_by_extractor': False}, indent=2))


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: extract_from_report.py -->


## Appendix B — actual final local result record

```json
{
  "tested_source_commit": "f3e3a57632c613e860a9941f007732cb4c2c91c6",
  "verified_unchanged_upstream_modules": 10,
  "python": "3.13.16 (main, Oct  6 2026, 04:38:44) [GCC 14.2.0]",
  "packages": {
    "numpy": "2.3.5",
    "pandas": "2.2.3",
    "scipy": "1.17.1"
  },
  "regression_runs": [
    {
      "name": "red_legacy",
      "returncode": 1,
      "tests_run": 3,
      "failures": 3,
      "errors": 0,
      "skipped": 0,
      "success": false,
      "elapsed_seconds": 0.8773096020001958
    },
    {
      "name": "green_candidate",
      "returncode": 0,
      "tests_run": 22,
      "failures": 0,
      "errors": 0,
      "skipped": 0,
      "success": true,
      "elapsed_seconds": 5.358512532000077
    },
    {
      "name": "green_candidate_optimized",
      "returncode": 0,
      "tests_run": 22,
      "failures": 0,
      "errors": 0,
      "skipped": 0,
      "success": true,
      "elapsed_seconds": 6.831027550000044
    }
  ],
  "all_preregistered_acceptance_conditions_met": true,
  "legacy_witness": {
    "fixture": [
      0.41,
      0.31,
      0.27
    ],
    "actual_winners": [
      2,
      2,
      7
    ],
    "assumed_legacy_winners": [
      7,
      2,
      7
    ],
    "left_identity_residual_real_operator": -0.02121459694983044,
    "legacy_stdout": "Synthetic proposal-equalization bridge checks: PASS",
    "legacy_actual_operator_calls": 0,
    "candidate_default_actual_operator_calls": 1
  },
  "candidate_default_positive": {
    "fixture": [
      0.41,
      0.27,
      0.31
    ],
    "actual_winners": [
      7,
      2,
      7
    ],
    "gate_on": true,
    "selected_projected_output": [
      0.36064814814764723,
      0.25147058823492435,
      0.27268518518480644
    ],
    "capacity": 0.6333333333333333,
    "epsilon": 1e-12,
    "minimum_winner_margin": 0.05174291938983033,
    "left_residual": 1.3877787807814457e-17,
    "right_residual": -4.85722573273506e-17,
    "max_oracle_errors": {
      "y": 5.551115123125783e-17,
      "q": 0.0,
      "scales": 1.1102230246251565e-16,
      "edge_scales": 1.1102230246251565e-16
    },
    "absolute_tolerance": 1e-14,
    "relative_tolerance": 0.0
  },
  "perturbation_seed": 2026090405,
  "positive_perturbation_cases": 64,
  "default_plus_perturbation_cases": 65,
  "max_abs_left_residual": 5.551115123125783e-17,
  "max_abs_right_residual": 7.806255641895632e-17,
  "max_oracle_errors": {
    "y": 5.551115123125783e-17,
    "q": 0.0,
    "scales": 1.1102230246251565e-16,
    "edge_scales": 1.1102230246251565e-16
  },
  "absolute_tolerance": 1e-14,
  "relative_tolerance": 0.0,
  "minimum_valid_winner_margin": 0.029937150824232206,
  "elapsed_seconds": 13.514455085999998,
  "limits": {
    "no_new_lean_compilation": true,
    "finite_synthetic_checks_not_universal_float64_proof": true,
    "legacy_other_selftest_blocks_not_replaced_by_companion": true,
    "saved_production_bridge_replay_not_rerun": true,
    "no_engine_or_oracle_patch_or_v41_result_claimed": true,
    "not_independent_review_library_approval_or_coupled_locking": true
  }
}
```


## Appendix C — preregistration, privacy and review/provenance records

### PLAN.md

```text
# Cycle 005 — review response and branch-faithful bridge self-test proposal

Researcher 040282. Preparation stamp: 2026-09-04, the session-supplied date;
review correspondence is labelled 2026-11-08 by the owner/colleagues. Do not use
these preparation stamps to infer historical execution chronology. A short
cycle-004 addendum will make the distinction explicit.

## Priority and current-source basis

New owner-relayed feedback overrides the previously queued gated-OFF work for
this bounded cycle. Address state/date/evidence navigation and metadata privacy,
then one code finding: the opt-in bridge self-test's wrong-branch false PASS.

Read-only current main: f3e3a57632c613e860a9941f007732cb4c2c91c6.
Intake/review branch: b466ab6cdd564ce3f7848e7701b378c5f0cc475f.
The intake contains the old78-row root and a108-row completed004 ledger inside
the004 archive. The current local completed004 ledger has108 rows. Supply an
explicit108-row completion snapshot plus synchronized root files/log navigation;
do not silently rewrite the old uploaded reports/archives or imply all labels
received independent approval.

Public review notes report independent compilation of cycles002–004, counts
22/44/22+6, zero warnings/errors, only standard axioms. They did not execute our
checker controls/source experiments. Record that exact scope, not library-grade
statement-fidelity approval, full review, or independent numerical reproduction.
The corrected colleague note says uploader PR10/checksum PR11 merged; current
main agrees with its supplied commit. Do not rework the uploader. Current Python
CI exists. Frozen v4 and candidate v4.1 remain distinct.

## Proposed repair domain, before running new tests

ART-0050 is the existing AIEF_1_4_proposal_equalization_bridge_analysis.py.
Do not edit it, its existing registry row, or saved replay outputs. Propose a
NEW standalone self-test companion plus an erratum for owner/seat review.
No branch push/PR, main edit, inbox upload or bot contact is authorized here.

The companion must call current-main
admissibility_from_nonnegative_proposal on a full isolated12-node/66-edge vector,
not manufacture its projected output from an assumed endpoint-winner map.
Use the existing analytical right_projection_coefficient as the identity under
test, and use the actual operator output on the left sides.

Default positive fixture: selected edges25,29,59=(.41,.27,.31), cap19/30 as the
existing binary float, epsilon1e-12. Actual strict winner map must be (7,2,7),
gate active, both controllers clipped, third node not a stronger controller,
positive selected edges, and isolated support. The operator's rows/scales/output/
winner data must also agree with an INDEPENDENT Fraction loop oracle embedding
the binary inputs exactly. Verify the public edge layout rather than assume it.

The formerly hardcoded fixture (.41,.31,.27) is a mandatory negative control:
actual winners (2,2,7); require a named branch rejection, CLI nonzero and NO PASS.
A winner tie and globally inactive fixture must not be accepted as the strict
conditional branch either. Missing modules/import errors are blockers, not
mathematical negative successes.

Additional finite positive cases:32 seeded draws in x25∈[.39,.42], x29∈[.26,.28],
x59∈[.30,.32], seed2026090405, each at eps1e-12 and eps1e-2. These boxes have
both controller rows over cap and third row below cap, with a strict winner gap.
Use fixed absolute tolerance1e-14, relative0 for numerical identities/operator
values; do not enlarge it to obtain a pass. Compare all66 outputs and all node/
edge structural data with the rational oracle, not just the selected identity.

## Falsifiers / regression acceptance

1. Record legacy synthetic_self_test prints PASS without querying the real
   operator. A COMMON regression contract requiring real-operator calls must
   fail on that legacy entry point and pass on the new companion.
2. Replace the actual operator with a sentinel failure in an isolated test.
   New self-test must propagate/reject and not print PASS; legacy does not query
   it. Also corrupt an output and winner metadata; the rational/branch checks
   must reject, not reconstruct an answer from those corrupted fields.
3. Wrong-branch, tie, inactive, nonfinite/negative input and nonpositive epsilon
   must fail closed at the appropriate validation/branch check.
4. Drop epsilon from the analytical coefficient at the admitted eps1e-2 case;
   identity checking must detect it. A constant/fabricated projection must fail.
5. Include a globally inactive large-epsilon map check to catch unguarded
   candidate scaling. This is an operator/oracle control, not a valid strict-
   branch algebra fixture.
6. Core validation must not rely on removable Python assertions. Exercise CLI
   rejection under both ordinary Python and -O. Actual dependency errors must
   remain errors rather than being treated as successful branch rejection.

Keep legacy artifact bytes unchanged throughout. Source manifest/report and
prior own replay script will be read to answer whether inspected saved bridge
claims used --self-test; do not claim a fresh replay or global provenance audit.
Existing own S01 one-condition replay imports engine/modular/legacy orchestration,
not this bridge self-test. The bridge manifest command and source dispatch are
additional bounded evidence; inspect before drawing the scope conclusion.

## Privacy and handoff acceptance

Drop author/committer contact and signed commit payload data from the three
identified acquisition JSON files. Keep only acquisition IDs needed to locate
sources. Do not print, preserve in a new backup, or redistribute the email values.
New acquisition helpers persist minimal contact-free metadata from the start.
Do not rewrite scientific source files to remove synthetic placeholder fixtures.

Create a privacy-scanned response bundle with unpacked ledger-referenced proof/
source logs, or a precise archive-only map if unavailable. Include a distinct
completed004 ledger (108 rows) and current workflow ledger (may add this one new
regression claim). Keep labels as submitter claims, with compilation-only external
review recorded separately. No new Lean compilation this cycle is planned.

Deliver one standalone numbered report with the short addendum, complete critical
companion/test code, fixed base commit, actual red→green/sensitivity outcomes and
limits inline; a short standalone addendum is also useful. Extract and rerun the
new inline code with explicitly reviewed public dependencies. This is local
self-reproduction, not the independent negative controls requested by colleagues.
```

### ADVERSARIAL_ADDENDUM.md

```text
# Final adversarial addendum — input provenance, before the new control

The original plan already requires rejection of a constant/manufactured projected
answer. A final source read found a stronger version of that falsifier: the first
candidate builds its Fraction oracle from the mutable proposal AFTER calling the
operator. A substituted operator could rewrite that argument to the default
fixture and return the default answer, so the oracle would verify the wrong
requested input consistently.

Test this BEFORE changing the candidate: supply the distinct valid input
(.40,.26,.30), substitute an operator that rewrites its argument to(.41,.27,.31),
then returns the genuine map at the rewritten input. The checker must reject
rather than certify the substituted fixture. If it passes, preserve the failing
control and fix the candidate to snapshot/construct the oracle before the call,
and reject unexpected mutation. This is a falsifier of OUR candidate, not a
claim that the current-main pure helper actually mutates its argument.

Do not change numerical allowances, main source, positive box, default/negative
fixtures or the original finding. Repeat the final complete suite and one-note
extraction after any fix. Retain the successful20/21-method development records
separately from the final suite. Stop after this bounded check and packaging.
```

### input_mutation_red.json

```json
{
  "pre_fix_returncode": 1,
  "single_control_failures": 1,
  "errors": 0,
  "reason": "VerificationError not raised: first candidate accepted a replacement of the requested fixture by mutation",
  "scope": "Own candidate flaw; no claim of mutation by the actual upstream pure helper",
  "log": "input_mutation_red.log"
}
```

### feedback_scope.json

```json
{
  "current_main_tested": "f3e3a57632c613e860a9941f007732cb4c2c91c6",
  "review_acquired_from_inbox": "b466ab6cdd564ce3f7848e7701b378c5f0cc475f",
  "intake_note": "audit_inbox/2026-11-08_auditor-seat-002_researcher-040282-intake.md",
  "researcher001_triage": "audit_inbox/2026-11-08_auditor-seat-002_workspace-notes/TRIAGE_r040282.md",
  "evidence_kind": "Publicly acquired colleague reports of their own execution; not our reexecution of their witnesses",
  "reviewer_main_basis": "942f8526daee5ac547f2e422101fa95c61eeef41",
  "independent_compilation_reported": {
    "002": 22,
    "003": 44,
    "004_EMA": 22,
    "004_drive": 6
  },
  "compiled_total": 94,
  "reported_warnings": 0,
  "reported_errors": 0,
  "reported_footprint": [
    "propext",
    "Classical.choice",
    "Quot.sound"
  ],
  "scope_exclusions": [
    "library-grade statement-fidelity approval",
    "integration decision",
    "our check_cycle.py controls",
    "our ZIP checkers",
    "full S01 reanalysis",
    "our4800 saved held-event comparisons",
    "real-array finiteness census",
    "new005 repair-candidate review"
  ],
  "additional_review_confirmation": "Coarse baseline ON bound fails to reach threshold; not evidence of OFF",
  "uploader_disposition": "Owner reports PR10 uploader and PR11 checksum checker merged; supplied main head matches acquired head. No new uploader work; no behavioral certification of those merges here.",
  "current_python_CI": ".github/workflows/repo-checks.yml exists on the tested source; withdraw the stale no-Python-CI generalization as a current-main claim",
  "owner_receipt": "Actual audit-inbox intake and triage found; uploaded root ledger independently counted78 rows, versus108 at completed004",
  "contact_or_remote_write_by_this_agent": false,
  "reviewer_private_log_paths": "Mentioned by reviewer; not fetched or represented as included local evidence"
}
```

### privacy_results.json

```json
{
  "policy": "minimal acquisition identifiers only; no removed values or unredacted backups retained",
  "scientific_sources_changed": false,
  "remote_files_changed": false,
  "files": [
    {
      "path": "coordination/source_state/audit_inbox_branch_2026-11-07.json",
      "removed_contact_matches": 0,
      "contact_and_signed_payload_fields_dropped": true,
      "scope": "additional legacy inbox metadata: structural cleanup even without pattern matches"
    },
    {
      "path": "coordination/source_state/main_branch_2026-11-07.json",
      "removed_contact_matches": 4
    },
    {
      "path": "cycle_003/source_state/inbox_branch.json",
      "removed_contact_matches": 0,
      "contact_and_signed_payload_fields_dropped": true,
      "scope": "additional legacy inbox metadata: structural cleanup even without pattern matches"
    },
    {
      "path": "cycle_003/source_state/main_branch.json",
      "removed_contact_matches": 4
    },
    {
      "path": "cycle_004/source_state/inbox_branch.json",
      "removed_contact_matches": 0,
      "contact_and_signed_payload_fields_dropped": true,
      "scope": "additional legacy inbox metadata: structural cleanup even without pattern matches"
    },
    {
      "path": "cycle_004/source_state/main_branch.json",
      "removed_contact_matches": 4
    }
  ],
  "archives": [
    {
      "path": "researcher040282-cycle005-review-response.zip",
      "changed_members": [
        {
          "member": "researcher_040282/coordination/source_state/audit_inbox_branch_2026-11-07.json",
          "removed_contact_matches": 0,
          "contact_and_signed_payload_fields_dropped": true
        },
        {
          "member": "researcher_040282/cycle_003/source_state/inbox_branch.json",
          "removed_contact_matches": 0,
          "contact_and_signed_payload_fields_dropped": true
        },
        {
          "member": "researcher_040282/cycle_004/source_state/inbox_branch.json",
          "removed_contact_matches": 0,
          "contact_and_signed_payload_fields_dropped": true
        }
      ],
      "crc_ok": true
    }
  ],
  "reported_contact_bearing_files_minimized": 3,
  "additional_legacy_inbox_metadata_minimized": 3,
  "branch_metadata_contact_matches_remaining": 0,
  "branch_metadata_nonminimal_records_remaining": 0,
  "pattern_scan_limit": "A pattern-only scan is insufficient: author/contact/signed payload fields are structurally dropped too"
}
```

### saved_evidence_provenance.json

```json
{
  "tested_main": "f3e3a57632c613e860a9941f007732cb4c2c91c6",
  "inspection_only_no_production_replay_rerun": true,
  "saved_manifest": "source_state/main/aief_1_4_proposal_equalization_bridge/analysis_manifest.json",
  "recorded_command": [
    "AIEF_1_4_proposal_equalization_bridge_analysis.py",
    "--npz",
    "runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz",
    "--manifest",
    "runs/5a9f093a2fe0/manifest.json",
    "--seed",
    "4619122171158768524",
    "--output-dir",
    "aief_1_4_proposal_equalization_bridge"
  ],
  "recorded_command_contains_self_test": false,
  "only_direct_synthetic_self_test_call_lines_in_bridge": [
    361
  ],
  "dispatch": "lines358\u2013362: if args.self_test, run synthetic_self_test and return; normal replay begins after that branch",
  "saved_manifest_branch_checks": {
    "controllers_clipped_all": true,
    "gate_on_all": true,
    "maximum_isolation_error": 0.0,
    "minimum_winner_margin": 4.440892098500626e-14,
    "selected_positive_all": true,
    "winner_map_expected_all": true
  },
  "prior_own_S01_replay_script_copy": "historical_provenance/replay_one_condition.py",
  "prior_own_S01_replay_imports": [
    "AIEF_1_4_Twindow_sensitivity",
    "__future__",
    "aief_experiment_engine_v1",
    "aief_modular.collectors",
    "aief_modular.factors",
    "aief_modular.registry",
    "aief_modular.runner",
    "aief_modular.validation",
    "csv",
    "json",
    "numpy",
    "os",
    "pathlib",
    "platform",
    "sys",
    "time"
  ],
  "prior_own_S01_script_imports_bridge": false,
  "prior_own_audit_probes": "test_deep_audit.py/additional_probes.py invoked old synthetic_self_test to expose its false PASS, not to endorse the fixture",
  "bounded_conclusion": "Inspected saved normal-replay command/path does not invoke the synthetic self-test. This defect alone does not invalidate the conditional algebra or recorded real-data replay. Not a fresh replay, exhaustive dependency/provenance audit, or certification of every historical wrapper.",
  "near_tie_limit": "Saved minimum margin4.440892098500626e-14 is much smaller than new positive synthetic margins; no robustness claim for saved near-tie cases."
}
```

