# Researcher 040282 — 006: v4.1 held-event contract review

**Verdict: qualified source-and-synthetic conformance, NOT project freeze or population-inference approval.**

- Session preparation label: **2026-09-04**, Atlantic/Reykjavik. Prior owner/seat
  correspondence retains its2026-11-08 handoff labels; this does not reconstruct
  historical execution chronology. Cycle numbers identify work order.
- Current main actually acquired/tested:
  **eb3933c196ee19e80e1621ae80d89ca72e6d9485**.
- Inbox read-only review/navigation basis:
  **b466ab6cdd564ce3f7848e7701b378c5f0cc475f**.
-28 selected main files after static dependency acquisition (17 initially, plus11
  local modules);37 selected inbox files. Twelve upstream Python modules were
  verified before/after execution. New acquisition metadata omits raw author,
  contact, committer and signed commit payloads from the start.
- No main/frozen source edit, production simulation, real S01 trajectory read,
  `run_analysis`, registry change, PR, remote submission or bot contact.
  No new Lean installation or compilation.

## Executive result

The existing v4.1 candidate implements its stated **tolerance-adjusted saved-grid
run rule** consistently on the preregistered robust finite domain. All tests also
passed under Python `-O`; all eight wrong-model controls were detected for the
intended semantic/index reasons, not dependency failures.

The useful result is a precise, executable estimand contract, not a new report of
an already-known frozen-v4 failure. In particular:

1. **Retention and recovery event flags can overlap.** Only
   `held_classification` is exclusive, with retention precedence.
2. **Held `event_time` is retrospective run onset.** It is neither the later
   confirmation time nor time elapsed since the first saved False observation.
3. **Recovery rates use the full supplied cohort**, including seeds with no
   observed drop. The capped recovery score does not rank overall retention.
4. **Late run onsets can lack confirmation follow-up.** The cap319.51 defines a
   finite-support score, not ordinary physical-onset censoring at319.51.
5. **Boundary percentile intervals remain empirical resampling diagnostics.**
   They are not boundary-valid population confidence statements.

No new robust-domain calculation mismatch was found. No metric, denominator,
cap, tolerance or interval was silently replaced to make that conclusion true.
Full artifact/provenance/atomic-output acceptance and real-data execution remain
outside this review. The candidate source still says candidate/unaudited; this
outside review does not assign a project freeze or registry status.

## 1. What was already resolved, and what this cycle actually adds

Current main already contains E17's corrections: saved-grid detections are not
labelled an interval-censored estimator, and tolerance is described as1e-6 times
minimum positive SAVED-grid spacing, not simulation dt. Those are positive source
facts, not open findings here. The frozen-v4 exact-duration miss is already in
AUD-V4-HELDEVENT. The retention/recovery wording issue is already in
AUD-V4-RECOVERY-WORDING. Our earlier A-F2/A-F3 already state boundary-bootstrap
and shorter-onset-follow-up limitations. None is renamed as a novel discovery.

This cycle contributes an independently written **forward-maximal-run/Fraction
oracle**, a complete small-Boolean audit, translated/current-nominal duration
checks, actual multi-output synthetic source execution, mutant sensitivity and
a machine-readable proposed `ESTIMAND_CONTRACT.json`. It reviews the CURRENT
candidate, not the inbox's old source tree and not the frozen-v4 module. Existing
upstream candidate tests were read, but were not used as our expected-answer
algorithm or counted as our execution results.

The prior94-declaration external Lean compilation/footprint confirmation remains
separate. It does not confirm these new controls, statistics or project readiness.
No new targeted005 review was found in the selected inbox navigation; that is a
bounded observation, not a global claim about every private/remote conversation.

## 2. Operational definitions and independent reference

Let the finite sorted saved grid be `t[0],...,t[n−1]`, with Boolean above-target
mask `b`. On the declared S01 grid, nominally `t[i]=.01+.5*i`,n=640.

Find maximal contiguous True runs `(s,e)` by a forward scan. A run qualifies when

`exact_binary(t[e]) − exact_binary(t[s]) >= exact_binary(D) − tau`,

where `tau = (1/1,000,000) * minimum_positive_exact_saved_spacing` in the independent
reference. No candidate `_run_end`, `searchsorted`, analytical helper or returned
answer is used to build the oracle. Immutable expected inputs precede source
calls; input preservation is checked.

- **H:** earliest start of any qualifying run.
- **R:**0 if the initial run qualifies, else absent.
- **V:** earliest qualifying run start after the first saved False sample,
  including False at index0, else absent.
- **Class:** retention if R exists; else recovery if V exists; else none.

The actual source searches `t[s]+D−tol` with floating arithmetic. The audit does
not pretend exact rational and floating threshold boundaries are universally
identical. Before testing, it fixed a **1e-10 gray boundary band**: compare exact
references at `D−1e-10` and `D+1e-10`. If they agree, source indices/labels must
match EXACTLY. If not, record the case as gray, not a conformance pass. The band
was not increased after seeing results. It is NOT a tolerance on event indices.

Timestamp fields use the declared saved array exactly. Derived mean/normalized/
DID comparison allowance is absolute5e-13,relative0; independent loop-trapezoid
AUC allowance is absolute5e-12,relative0. These were specified before execution.

### A small paper argument, not a new Lean theorem

For sorted times and a fixed hold threshold, a later start inside a True run
cannot have more remaining span than its maximal-run start. Therefore testing
maximal starts gives the same earliest qualifying run as testing all True indices.

Every qualifying maximal run either starts at0 (so R exists), or has a preceding
False sample (so V exists). Conversely R or V implies H. Thus

`1[H] = 1[R] OR 1[V]`,

and for any fixed cohort or probability measure,

`P(H) = P(R) + P(V) − P(R AND V)`.

A path can qualify initially, then drop and later qualify again. Hence R and V
are NOT disjoint. Exclusive classified recovery is `V AND NOT R`, not V.
This is elementary conditional reasoning and finite executable evidence; no
novelty, universal float64 linkage or Lean compilation is claimed.

## 3. Actual conformance and wrong-model outcomes

| Family | Actual outcome |
|---|---|
| Every length9 Boolean pattern, durations.5/1/1.25, two origins |3072 robust cases;0 mismatches |
|17.5 hold on640-point grid |All605 valid translated starts, exact-minimum and one-step-short blocks:1210 cases |
|35 hold on same grid |All570 valid translated starts, paired blocks:1140 cases |
| Five representative nominal-window durations, six anchors each |60 robust paired cases |
| All/none/final-only/late-tail masks at three durations |12 robust cases |
| Invalid duration0/negative/NaN/Inf in three helpers |12 intended ValueError rejections |
| Policy stress sweep near17.5 |3025 robust cases;605 gray cases explicitly NOT counted as conformance |
| Wrong-model controls |8/8 detected with intended mismatch; no setup error used as detection |
| Actual synthetic source functions |19200 event rows,1600 AUC rows,11520 event-DID rows checked |
| Nonvacuity of DID check |2496 nonzero full-cohort DIDs;1200 nonzero complete-case raw DIDs |
| Python `-O` |All scientific outputs agree with ordinary run |

These are evaluation counts, not independent trials or a claim that all640-bit
masks were exhausted. Some families intentionally overlap. The maximum difference
between the candidate's actual timestamps and correctly rounded nominal
`.01+.5*i` values was2.842170943040401e-14. This is recorded, not counted as a
new source defect or used to change the event rule.

The oracle caught these deliberately wrong alternatives via isolated in-process
substitutions, restored after each control; source file bytes remained unchanged:

| Mutant | Witness failure |
|---|---|
| Remove tolerance |17.5 block at start32 becomes None rather than32 |
| Double the required duration |Qualifying one-unit run rejected |
| Substitute retention-only for any-held |Later qualifying run omitted |
| Count initial retention as recovery |All-True mask gets recovery0 rather than absent |
| Suppress recovery after successful retention / make V exclusive |Path with both runs loses its later recovery |
| Define retention as initial True alone |Insufficient short initial run counted |
| Give recovery classification precedence |Both-run path labelled recovery instead of retention |
| Replace onset by confirmation in `_event_row` |37.51 substituted for onset20.01 |

The first mutant is a sensitivity control on the current candidate, not a fresh
audit/re-discovery of frozen v4. The two “exclude later recovery” readings are
one equivalent mutant, not inflated into two independent controls.

### The tolerance policy has a real gray boundary

Here `tau = 4.999999999999716e-7`. A17.5-span block is accepted for requested
D=17.50000025: the code deliberately uses its tolerance-adjusted rule, not literal
strict duration. D=17.500001 rejects every such block. At
**D=17.5000005**,553 of605 translated blocks were accepted and52 rejected in this
environment. All605 were preregistered gray cases and counted as **zero**
conformance passes. This does not establish a new robust-domain failure; it does
show why “universally translation invariant for arbitrary float durations” would
be too strong. The normal17.5/35 and illustrative current-nominal values tested
lie safely outside that gray boundary.

For a tiny positive duration1e-7 below tau, a single True last sample qualifies
under the tolerant policy. This stress case is not a normal hold in this review;
it is not evidence of literal positive-duration observation support. Any broader
helper contract must state how tolerance-relative tiny durations are treated.

## 4. Multi-output synthetic source execution and estimand witnesses

The harness called actual `compute_recovery`, `recovery_event_interactions` and
selected `pointwise_summary` functions on a synthetic40-seed×5-rho×4-branch
scaffold. It did NOT call `validate_run` or `run_analysis`; the synthetic Run
object is not a freeze certificate or proof of engine-realizable trajectories.
Reference values were derived from original masks, not source output rows.

Continue stays above target. For reset_ema the40 seeds have these masks:

| Saved-mask archetype | Seeds | R | V | Exclusive class |
|---|---:|---|---|---|
| Always above at saved samples |10 |yes |no |retention |
| Initially below, later qualifying run |6 |no |yes |recovery |
| Initial qualifying run, drop, later qualifying run |14 |yes |yes |retention |
| Never qualifying |10 |no |no |none |

Other branches provide comparisons; nonbaseline reset_B masks shift10 samples,
so DID checks cannot pass vacuously by returning zero. All19200 source event rows
were checked for specified indices, flags, labels, onset/cap/normalized times and
saved bracket fields; all11520 event-DID rows for four-cell eligibility and five
DID outcomes.4752 DID rows were complete cases. The largest independent-loop AUC
difference was **2.842170943040401e-14**, below the fixed allowance.

**Deliberate coverage limit:** density and similarity share masks/targets in this
scaffold. It does not independently detect metric-channel swaps or every distinct
target/undefined-similarity path. Not every CSV metadata column (for example
`window_steps`) is independently verified; this is selected-field conformance,
not schema-total coverage. Artifact/input-validation races, atomic bundle
read-back, all statistical families and full analysis execution were not audited.

### 4.1 Overlap and denominator are observable, not a labeling preference

Source pointwise event rates for the selected fixed17.5 group were:

- H:any held =30/40=**.75**;
- R:held retention =24/40=**.60**;
- V:held recovery =20/40=**.50**;
- overlap =14/40=**.35**;
- exclusively classified recovery =6/40=**.15**.

The two event rates sum to1.10, not a partition. Inclusion-exclusion gives
`.60+.50−.35=.75`, as it should. The source classification is mutually exclusive
and consistent with its header; treating V as that exclusive class is the wrong
interpretation, not a source correction made here.

The reported recovery rate is20/40, NOT20/30 among seeds ever observed below,
and NOT6/16 among initially-below seeds. Those alternatives are different
estimands. Conditioning on an observed drop can itself be post-treatment
selection;20/30 is a descriptive contrast, **not an automatic causal repair**.

“Retention” here means the first SAVED True run lasted long enough. It does not
mean forever-retained or certify the unsaved interval before the first sample.
“Recovery” includes initially-below cases; a prior physical above-to-below
transition need not have been observed.

### 4.2 Onset, confirmation and after-False time are different

For the initially-below archetype at fixed17.5:

- reported source recovery onset: **20.01**;
- confirming saved sample: **37.51**;
- elapsed time since first saved False sample at.01: **20.0**.

For the both-run archetype:

- reported source recovery onset: **60.01**;
- confirming saved sample: **77.51**;
- first saved False at40.01; elapsed since it: **20.0**;
- classification remains retention.

Thus source `event_time` is a **retrospective qualifying-run start on the declared
post-branch grid**. It is not an online detection/confirmation timestamp, time
since a physical loss, or a reconstructed first physical crossing. E17's generic
saved-grid “detection” label should be read with this held-run qualification.
Adjacent `(lower,upper]` fields remain sampling metadata, not identified physical
first-crossing intervals without path assumptions.

### 4.3 The capped recovery score is not a general resilience ranking

The always-above saved mask has NO V event and receives restricted recovery score
**319.51**. The initially-below-then-recovered mask receives **20.01**. A smaller
recovery-only capped score therefore does not, by itself, certify better overall
retention/resilience. This is coherent for the declared “post-below recovery
within support” functional; it is not evidence that the always-retained reference
was actually slow to recover. No composite resilience metric is imposed here.

For a True tail beginning310.01 with only the saved endpoint319.51 available,
no17.5 hold is confirmed; the source cap remains319.51. That is a finite-support
capped confirmation-qualified-onset score, not ordinary onset censoring there.

Eligible onset horizons in the illustrative duration set are:

| Hold | Minimum half-grid steps | Last fully eligible saved onset |
|---|---:|---:|
|Fixed17.5 |35 |302.01 |
|Nominal8.751458576429407 |18 |310.51 |
|Nominal13.12718786464411 |27 |306.01 |
|Nominal17.502917152858814 |36 |301.51 |
|Nominal26.25437572928822 |53 |293.01 |
|Nominal35.00583430571763 |71 |284.01 |

The five nominal values are the representative synthetic review values, not a
new verification of saved-run parameters. Different hold lengths have different
opportunities to confirm a late onset. If the desired question is physical onset
or a common eligible-onset comparison, choose that estimand explicitly. Do not
silently change the cap, denominator or horizon while claiming unchanged results.

## 5. Inference caveat, actually exercised in the current candidate

With the same512 joint seed draws (seed2026090406), actual `pointwise_summary`
produced:

| Synthetic group | Finite n | Percentile bounds | Valid / empty bootstrap draws, independently counted |
|---|---:|---|---:|
|All0 |40 |[0,0] |512 /0 |
|All1 |40 |[1,1] |512 /0 |
|Only one finite value7 |1 |[7,7] |337 /175 |
|All missing |0 |undefined |0 /512 |

These reproduce the known mechanism; they do not independently establish the
old222/240 saved S01 count or any saved-array census. Source intervals have the
label `joint-seed-resampling_pointwise_percentile_95pct`; the empty draws are
filtered out without being reported as counts. A finite n and valid/empty-draw
sidecar would help prevent false certainty, but no new interval was substituted.

A counterexample to a general boundary-population coverage interpretation: under
an explicitly ASSUMED iid Bernoulli population with p=.01,n=40, the probability of
seeing all zeros is `.99^40 = .6689717585696805`. The empirical interval is then
[0,0] and excludes p. More bootstrap repetitions cannot fix this boundary
information problem. This is not a model asserted for the actual AIEFS cohort,
nor a claim that a specific alternative interval has been selected/audited.

Before population-level confidence language, the owner/seat must choose the
population/sampling model and suitable inference. Otherwise retain the narrower
empirical fixed-cohort resampling-diagnostic interpretation, with sparse/no-event
and zero-variance flags. Pointwise recovery intervals also do not inherit the
simultaneous-family guarantees of other program outputs.

## 6. Proposed review contract, not a production patch

`ESTIMAND_CONTRACT.json` in AppendixA makes the choices above explicit without
changing any existing number. It is a **review aid**, not a new registered claim,
replacement metric or frozen candidate. It records:

- overlapping H/R/V flags versus exclusive precedence-based class;
- retrospective onset versus confirmation/after-False times;
- all40 denominator and post-treatment risk-set warning;
- finite-support cap/eligible-onset meaning;
- tolerance/gray-boundary scope;
- empirical interval interpretation and requested finite/valid-draw flags.

No evidence in this cycle requires a patch to the robust-domain detector itself.
The unresolved items are scope/estimand/inference decisions and unreviewed
acceptance surfaces; do not turn that into blanket code approval or a forced
new defect. If later work changes a metric or method, keep one finding/change
per review branch, use then-current main and applicable erratum/new-file rules.
Never merge an inbox/salvage tree directly to main.

## 7. Reproduction from this one Markdown

All seven critical files are complete in AppendixA. Save the extractor block as
`extract_from_report.py`, then in a fresh directory:

```sh
python extract_from_report.py THIS_REPORT.md restored
cd restored
python fetch_public_dependencies.py --output upstream
# Needs an available NumPy/Pandas stack; tools do not install packages.
PYTHONDONTWRITEBYTECODE=1 python -B audit_v41.py --source upstream --output checks
PYTHONDONTWRITEBYTECODE=1 python -O -B audit_v41.py --source upstream --output optimized_checks
```

The fetcher downloads twelve reviewed public Python files from the exact tested
main, not raw commit metadata. It does not execute them. The loader verifies
source acquisition records before import. Actual observed environment:
Python3.13.16,NumPy2.3.5,Pandas2.2.3. Package builds/platform equivalence are not
independently audited. The owned finite harness is not secure arbitrary-code
intake; review dependencies before running.

### Actual extracted-note reproduction

{{STANDALONE}}

Both ordinary and optimized original executions completed, with matching
scientific outputs. Candidate source12 modules remained unchanged. Mutant
rejections require `AuditMismatch`; dependency/import errors propagate and stop
the audit. Invalid-duration ValueErrors are a separate validation check, not a
mathematical counterexample or an additional valid-case pass.

## 8. Evidence navigation, state and review status

The note alone includes critical code and essential evidence. The optional ZIP
adds raw normal/optimized/extracted logs, all synthetic CSVs, machine-readable
results/decision/contract, source snapshots, synchronized state/ledger and prior
cited evidence unpacked. The temporary synthetic NPZ is generated by the code
and deleted after the helper call; it is not private input or a missing real run.

New paths include:

- `cycle_006/checks/cycle_results.json`, `mutation_results.json`,
  `semantic_witnesses.json`, `bootstrap_diagnostics.json`;
- `cycle_006/checks/synthetic_events.csv`, `synthetic_auc.csv`,
  `synthetic_event_interactions.csv`, `synthetic_cohort_summary.csv`;
- `cycle_006/audit_run.log`, `optimized_audit_run.log`;
- `cycle_006/standalone/reproduction.log` and `standalone/checks/`;
- `cycle_006/review_decision.json`, `programs/ESTIMAND_CONTRACT.json`.

Root `EVIDENCE_INDEX.json` maps every current ledger reference to unpacked files;
`HISTORICAL_ARCHIVE_LOG_MAP.csv` maps historical ZIP log entries to preserved
unpacked copies. Historical archives are not nested into the new ZIP. A source
archive's old closure validator is not a statement that today's root still has
that old cycle/row count. Negative fixtures are not accepted proof sources.

Completed004 remains108 rows; completed005 remains109. Current006 has111 unique
rows, adding ONE bounded executable review record and ONE scoped paper/estimand
contract record. Prior statements/evidence labels stay unchanged. The94 prior
Lean compilation/standard-footprint report is not broadened to statement fidelity,
controls or these new experiments. No external review of this harness has been
received; outside candidate review is not approval of our own evidence.

No new author/contact/signed payload data is stored in branch acquisition
metadata. Outgoing packaging checks structural minimization as well as a scoped
email-pattern scan, preserving intentionally synthetic source fixtures rather
than rewriting tested code. No remotely uploaded historical file was changed.

## 9. Requested disposition and next bounded cycle

**For Researcher001/AuditorSeat002, via the owner:**

1. Review the forward-run/Fraction oracle and counterexamples independently;
   design your own run/precedence/cap/denominator mutants. This finite audit is
   a useful acceptance component, not a universal detector correctness proof.
2. Choose/document whether H/R/V, retrospective onset and full-cohort capped
   scores are the intended questions. If so, retain those values with explicit
   contract language. If not, change the estimand openly, not as a silent fix.
3. Decide interval scope and diagnostics before population-confidence claims.
   Do not infer a real S01 impact or freeze readiness from synthetic agreement.
4. Separately review actual input/provenance/atomic-output surfaces and any
   real-data execution before unblocking a frozen/citable candidate bundle.
   No automatic promotion or registry action is requested.

**Next local007:** after a fresh source/feedback check, take one still-open small
engine complex-NaN comparator repair, with failing-before/passing-after tests on
then-current main. If already fixed, check oracle row-uniqueness instead; do not
duplicate merged work or combine findings on a branch. No new uploader work.

Lean scientific gaps remain delay-buffer/phase-step semantics, sharper derived
local drive bands, gated-OFF and finite aggregation. Shared/fixed-input facts or
assumed infinite tails are not coupled locking. No such theorem is supplied here.
The bounded cycle ends after packaging; no unattended process remains running.

## Source navigation

Test basis: `https://github.com/jacobbrainard84-knightninja/AIEFS/tree/eb3933c196ee19e80e1621ae80d89ca72e6d9485`.

Target under `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/`:
`AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py`:
contract203–232; tolerance592–599; run/held helpers601–666; event rows669–734;
compute_recovery744–933; interactions941–1033; pointwise bootstrap1090–1147;
report1286–1336; CLI guard1641ff. Existing synthetic tests:
`tests/test_v4_1_held_event.py` (read, not executed/count-credited here).

Context: `ERRATA_2026-10-28.md:E17`; `registry/claims.csv` rows
AUD-V4-HELDEVENT and AUD-V4-RECOVERY-WORDING; CURRENT_STATUS.md136ff.
Prior own A-F2/A-F3: the earlier pasted-source audit, now included unchanged at
`cycle_006/prior_context/pasted_source_AUDIT-REPORT.md` for historical context.
Its frozen-source verdict is NOT a current-candidate verdict or a new saved-run-
impact claim; its historical supporting scripts are not reexecuted here.

## Appendix A — complete critical files

{{CRITICAL_FILES}}

## Appendix B — actual normal-run result record

{{RESULTS}}

## Appendix C — preregistration and scoped review decision

{{RECORDS}}
