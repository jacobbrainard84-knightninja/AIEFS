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

**Actually executed.** Seven critical files were extracted byte-for-byte; twelve public dependency modules were freshly fetched/verified. The extracted suite returned0 normally and under `-O`. All six scientific result groups match the original runs. This is submitter-local self-reproduction, not independent-seat confirmation.

```json
{
  "actually_executed": true,
  "returncodes": [
    0,
    0
  ],
  "tested_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "critical_files": [
    "ESTIMAND_CONTRACT.json",
    "audit_v41.py",
    "extract_from_report.py",
    "fetch_public_dependencies.py",
    "load_upstream.py",
    "reference_contract.py",
    "source_modules.json"
  ],
  "critical_file_count": 7,
  "all_extracted_files_match_supplied_sources": true,
  "fresh_public_modules_fetched_and_verified": 12,
  "all_six_scientific_result_groups_match_all_four_runs": true,
  "normal_elapsed_seconds": 18.338563283999974,
  "optimized_elapsed_seconds": 18.478244070000073,
  "original_normal_elapsed_seconds": 18.289061058000016,
  "original_optimized_elapsed_seconds": 17.981578323000008,
  "commands": [
    "python -B standalone/extracted/audit_v41.py --source standalone/upstream --output standalone/checks",
    "python -O -B standalone/extracted/audit_v41.py --source standalone/upstream --output standalone/optimized_checks"
  ],
  "results": [
    "cycle_006/standalone/checks/cycle_results.json",
    "cycle_006/standalone/optimized_checks/cycle_results.json"
  ],
  "log": "cycle_006/standalone/reproduction.log",
  "scope": "Submitter-local exact-note reproduction with public dependencies, not independent review, real trajectories, universal floating correctness, full pipeline acceptance or project freeze"
}
```


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

### audit_v41.py

<!-- BEGIN_CRITICAL_FILE: audit_v41.py -->
```python
"""Bounded outside-source/synthetic review of the current v4.1 candidate.

No real trajectories, run_analysis, production simulation or source edits.
All acceptance checks are explicit exceptions, including under python -O.
Our independently written finite tests are not a project freeze decision or
an independently reviewed theorem about this audit harness.
"""
from __future__ import annotations
import argparse
import contextlib
from fractions import Fraction
import io
import itertools
import json
import math
from pathlib import Path
import sys
import tempfile
import time
from unittest import mock

import numpy as np
import pandas as pd

import load_upstream
import reference_contract as ref

MEAN_ATOL = 5e-13
AUC_ATOL = 5e-12
BASE_WINDOW = 17.502917152858814
RHOS = (.5, .75, 1.0, 1.5, 2.0)
BRANCHES = ('continue', 'reset_ema', 'reset_B', 'future_shuffle')
TARGETS = {'density_90pct_continue_final',
           'similarity_90pct_continue_late_fixed_physical',
           'similarity_90pct_continue_late_normalized_EMA'}


class AuditMismatch(RuntimeError):
    pass


def require(condition, message):
    if not bool(condition):
        raise AuditMismatch(message)


def finite_or_nan_equal(left, right, allowance=MEAN_ATOL):
    left, right = float(left), float(right)
    return ((math.isnan(left) and math.isnan(right)) or
            (math.isfinite(left) and math.isfinite(right) and abs(left - right) <= allowance))


def safe(value):
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return safe(value.tolist())
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(float(value)) else None
    return value


def dump(path, value):
    path.write_text(json.dumps(safe(value), indent=2, allow_nan=False) + '\n')


def actual_indices(module, times, condition, duration):
    original_t = np.array(times, dtype=float, copy=True)
    original_c = np.array(condition, dtype=bool, copy=True)
    result = {}
    functions = {
        'held': module._held_index, 'held_retention': module._held_retention_index,
        'held_recovery': module._held_recovery_index,
        'classification': module.classify_held_event,
    }
    for name, function in functions.items():
        ts, cs = original_t.copy(), original_c.copy()
        result[name] = function(ts, cs, duration)
        require(np.array_equal(ts, original_t) and np.array_equal(cs, original_c),
                'Candidate modified supplied input during ' + name)
    result['first'] = module._first_index(original_c.copy())
    result['sustained'] = module._sustained_index(original_c.copy())
    return result


def compare_case(module, times, condition, duration, name, require_robust=True):
    # Compute immutable reference snapshots BEFORE invoking candidate functions.
    immutable_t = tuple(float(value) for value in times)
    immutable_c = tuple(bool(value) for value in condition)
    robust, expected, weak, strong = ref.robust_expectation(immutable_t, immutable_c, duration)
    require(robust or not require_robust, 'Unexpected gray-zone case: ' + name)
    observed = actual_indices(module, immutable_t, immutable_c, duration)
    for key in ('first', 'sustained'):
        require(observed[key] == expected[key], name + ': mismatch ' + key)
    for key in ('held', 'held_retention', 'held_recovery', 'classification'):
        if robust:
            require(observed[key] == expected[key],
                    f'{name}: {key}: observed={observed[key]}, expected={expected[key]}')
        else:
            require(observed[key] in (weak[key], strong[key]), name + ': outside preregistered gray bracket')
    h = observed['held'] is not None
    r = observed['held_retention'] is not None
    v = observed['held_recovery'] is not None
    require(h == (r or v), name + ': held union identity failed')
    require(observed['classification'] == ('retention' if r else 'recovery' if v else 'none'),
            name + ': retention precedence failed')
    return robust, observed


def exhaustive_small(module):
    count = 0
    for origin in (.01, 100.01):
        times = np.asarray([origin + .5 * index for index in range(9)])
        for pattern in itertools.product((False, True), repeat=9):
            for duration in (.5, 1.0, 1.25):
                compare_case(module, times, pattern, duration, 'small_' + str(count))
                count += 1
    return {'Boolean_patterns_per_origin': 512, 'origins': 2, 'durations': 3,
            'robust_cases': count, 'mismatches': 0, 'gray_not_counted': 0}


def block(length, start, steps):
    result = np.zeros(length, dtype=bool)
    result[start:start + steps + 1] = True
    return result


def saved_grid_checks(module, output):
    times = np.array(module.EXPECTED_SAMPLE_TIMES, copy=True)
    require(times.shape == (640,) and np.all(np.diff(times) > 0), 'Unexpected saved grid')
    nominal = np.asarray([float(Fraction(1, 100) + Fraction(index, 2)) for index in range(640)])
    require(np.max(np.abs(times - nominal)) <= 1e-12, 'Saved grid differs from stated nominal geometry')
    details, count = [], 0
    for duration in (17.5, 35.0):
        steps = ref.minimum_half_grid_steps(duration)
        starts = range(len(times) - steps)
        for start in starts:
            for delta in (0, -1):
                compare_case(module, times, block(len(times), start, steps + delta), duration,
                             f'saved_D{duration}_start{start}_delta{delta}')
                count += 1
        details.append({'duration': duration, 'all_valid_starts': len(starts),
                        'exact_block_and_one_step_short_cases': 2 * len(starts)})
    nominal_cases = 0
    for rho in RHOS:
        duration = BASE_WINDOW * rho
        steps = ref.minimum_half_grid_steps(duration)
        last = len(times) - steps - 1
        starts = sorted({0, 1, 32, 100, last // 2, last})
        for start in starts:
            for delta in (0, -1):
                compare_case(module, times, block(len(times), start, steps + delta), duration,
                             f'nominal_rho{rho}_start{start}_delta{delta}')
                nominal_cases += 1
        details.append({'rho': rho, 'duration': duration, 'minimum_half_grid_steps': steps,
                        'selected_starts': starts, 'last_eligible_onset': float(times[last])})
    for duration in (17.5, BASE_WINDOW, 35.0):
        for name, condition in [('all_false', np.zeros(640, bool)), ('all_true', np.ones(640, bool)),
                                ('last_only', block(640, 639, 0)), ('late_tail', block(640, 620, 19))]:
            compare_case(module, times, condition, duration, name + str(duration))
    for function in (module._held_index, module._held_retention_index, module._held_recovery_index):
        for invalid in (0.0, -1.0, float('nan'), float('inf')):
            try:
                function(times.copy(), np.ones(640, bool), invalid)
            except ValueError:
                pass
            else:
                raise AuditMismatch('Invalid duration was accepted')
    dump(output / 'saved_grid_cases.json', details)
    return {'translated_robust_cases': count, 'nominal_selected_robust_cases': nominal_cases,
            'other_robust_cases': 12, 'invalid_duration_rejections': 12,
            'maximum_nominal_timestamp_difference': float(np.max(np.abs(times - nominal))),
            'details': details}


def policy_boundary_checks(module, output):
    times = np.array(module.EXPECTED_SAMPLE_TIMES, copy=True)
    tau = float(ref.exact_tolerance(times))
    groups, records = [], []
    for factor in (-2.0, -.5, 0.0, .5, 1.0, 2.0):
        duration = 17.5 + factor * tau
        robust_count = gray_count = accepted = 0
        for start in range(605):
            robust, result = compare_case(module, times, block(640, start, 35), duration,
                                          f'policy_factor{factor}_start{start}', require_robust=False)
            robust_count += int(robust)
            gray_count += int(not robust)
            accepted += int(result['held'] is not None)
            records.append({'factor': factor, 'duration': duration, 'start': start,
                            'robust_conformance_case': robust, 'held_index': result['held']})
        groups.append({'factor': factor, 'duration': duration, 'robust_cases': robust_count,
                       'gray_cases_not_counted_as_conformance': gray_count, 'accepted_blocks': accepted})
    tiny = 1e-7
    robust, result = compare_case(module, times, block(640, 639, 0), tiny, 'tiny_policy_duration')
    require(result['held'] == 639, 'Tiny-duration policy extension changed')
    pd.DataFrame(records).to_csv(output / 'policy_boundary_cases.csv', index=False)
    return {'policy_tau': tau, 'gray_boundary_band': float(ref.BAND), 'groups': groups,
            'tiny_duration_stress': {'duration': tiny, 'single_sample_held': result['held'],
                                     'interpretation': 'tolerant policy, not literal positive-duration support'},
            'gray_cases_are_not_conformance_passes': True}


def row_arguments(index, duration=17.5):
    return dict(seed='synthetic', rho=1.0, t_window=BASE_WINDOW, branch='reset_ema',
                metric='density', target_definition='density_90pct_continue_final', target_value=.45,
                event_type='held', hold_system='fixed_physical_17p5', hold_duration=duration,
                event_index=index, imputed_count=0, held_classification='recovery')


def mutation_controls(module, output):
    small = np.array([.01 + .5 * index for index in range(9)])
    always = np.ones(9, bool)
    later = np.array([False, False, True, True, True, True, True, False, False])
    both = np.array([True, True, True, False, True, True, True, True, True])
    short = np.array([True, False, False, False, False, False, False, False, False])
    saved = np.array(module.EXPECTED_SAMPLE_TIMES, copy=True)
    original_from = module._held_from
    original_recovery = module._held_recovery_index
    def no_tolerance(ts, ends, index, duration, tol):
        return original_from(ts, ends, index, duration, 0.0)
    def doubled(ts, ends, index, duration, tol):
        return original_from(ts, ends, index, 2.0 * duration, tol)
    def no_later_after_retention(ts, condition, duration):
        return None if module._held_retention_index(ts, condition, duration) is not None else original_recovery(ts, condition, duration)
    def initial_only(ts, condition, duration):
        return 0 if len(condition) and condition[0] else None
    def wrong_precedence(ts, condition, duration):
        return ('recovery' if module._held_recovery_index(ts, condition, duration) is not None
                else 'retention' if module._held_retention_index(ts, condition, duration) is not None else 'none')
    cases = [
        ('zero_tolerance', '_held_from', no_tolerance, saved, block(640, 32, 35), 17.5),
        ('double_duration', '_held_from', doubled, small, block(9, 0, 2), 1.0),
        ('any_is_retention_only', '_held_index', module._held_retention_index, small, later, 1.0),
        ('recovery_includes_initial_retention', '_held_recovery_index', module._held_index, small, always, 1.0),
        ('recovery_is_exclusive_or_suppressed_after_retention', '_held_recovery_index', no_later_after_retention, small, both, 1.0),
        ('retention_is_initial_true_only', '_held_retention_index', initial_only, small, short, 1.0),
        ('recovery_precedence', 'classify_held_event', wrong_precedence, small, both, 1.0),
    ]
    results = []
    for name, attribute, mutant, times, condition, duration in cases:
        compare_case(module, times, condition, duration, 'unmodified_positive_' + name)
        try:
            with mock.patch.object(module, attribute, mutant):
                compare_case(module, times, condition, duration, name)
        except AuditMismatch as error:
            results.append({'mutant': name, 'detected': True, 'reason': str(error)})
        else:
            raise AuditMismatch('Harness missed mutant: ' + name)
    original_row = module._event_row
    onset = 40
    confirmation = ref.confirmation_index(saved, onset, 17.5)
    def onset_as_confirmation(**kwargs):
        changed = dict(kwargs)
        changed['event_index'] = confirmation
        return original_row(**changed)
    try:
        with mock.patch.object(module, '_event_row', onset_as_confirmation):
            row = module._event_row(**row_arguments(onset))
            require(row['event_time'] == float(saved[onset]), 'held onset mislabeled as confirmation')
    except AuditMismatch as error:
        results.append({'mutant': 'onset_is_confirmation', 'detected': True, 'reason': str(error)})
    else:
        raise AuditMismatch('Harness missed onset/confirmation mutant')
    require(len(results) == 8, 'Unexpected distinct mutant count')
    dump(output / 'mutation_results.json', results)
    return results


def make_cohort(module, directory):
    times = np.array(module.EXPECTED_SAMPLE_TIMES, copy=True)
    archetypes = ref.archetype_masks()
    names = ['always'] * 10 + ['later'] * 6 + ['both'] * 14 + ['never'] * 10
    seeds = tuple(f's{index:02d}' for index in range(40))
    membership = dict(zip(seeds, names, strict=True))
    conditions, arrays, scalar = {}, {}, []
    for seed in seeds:
        for rho in RHOS:
            for branch in BRANCHES:
                mask = np.array([True] * 640 if branch == 'continue' else archetypes[membership[seed]], bool)
                if branch == 'reset_B' and rho != 1.0:
                    mask = np.r_[np.zeros(10, bool), mask[:-10]]
                conditions[(seed, rho, branch)] = tuple(bool(value) for value in mask)
                values = np.full(640, .5) if branch == 'continue' else np.where(mask, .6, .1)
                for field, data in [('sample_times', times), ('density_trajectory', values), ('similarity_trajectory', values)]:
                    arrays[module._npz_key(branch, seed, rho, field)] = data
                scalar.append({'seed': seed, 'rho': rho, 'branch': branch, 'T_window': BASE_WINDOW * rho,
                               'D_B_final': .5, 'Weighted_similarity_late_fixed_physical': .5,
                               'Weighted_similarity_late_normalized_EMA': .5})
    npz = directory / 'synthetic_branches.npz'
    np.savez_compressed(npz, **arrays)
    inputs = module.RunInputs(directory, directory / 'unused.csv', npz, directory / 'unused.manifest',
                              directory / 'unused.status', directory / 'unused.certificate')
    run = module.ValidatedRun(inputs, pd.DataFrame(scalar), {}, seeds, RHOS, BRANCHES, .12, 25.0, {})
    return run, conditions, membership


def synthetic_pipeline(module, output):
    times = np.array(module.EXPECTED_SAMPLE_TIMES, copy=True)
    with tempfile.TemporaryDirectory(prefix='r040282_synthetic_') as temporary:
        run, conditions, membership = make_cohort(module, Path(temporary))
        events, auc = module.compute_recovery(run)
    require(len(events) == 19200 and len(auc) == 1600, 'Synthetic compute row counts changed')
    keys = ['seed', 'rho', 'branch', 'metric', 'target_definition', 'event_type', 'hold_duration_system']
    require(not events.duplicated(keys).any(), 'Duplicate synthetic event key')
    require(set(events['target_definition']) == TARGETS, 'Target definition set changed')
    expected_rows, cached = {}, {}
    for row in events.itertuples(index=False):
        condition = conditions[(row.seed, row.rho, row.branch)]
        duration = 17.5 if row.hold_duration_system == 'fixed_physical_17p5' else BASE_WINDOW * row.rho
        cache_key = (condition, duration)
        if cache_key not in cached:
            cached[cache_key] = ref.reference(times, condition, duration)
        expected = cached[cache_key]
        require(float(row.target_value) == .45, 'Synthetic target not continue-based .45')
        if row.event_type == 'first_crossing':
            index, label = expected['first'], 'not_applicable'
        elif row.event_type == 'sustained_through_last_saved_observation':
            index, label = expected['sustained'], 'not_applicable'
        else:
            require(row.event_type in ('held', 'held_retention', 'held_recovery'), 'Unexpected event type')
            index, label = expected[row.event_type], expected['classification']
        observed = index is not None
        event_time = float(times[index]) if observed else float('nan')
        restricted = event_time if observed else float(times[-1])
        require(bool(row.event_observed) == observed and row.held_classification == label,
                'Synthetic observed/classification mismatch')
        require(finite_or_nan_equal(row.event_time, event_time, 0.0), 'Synthetic event onset mismatch')
        require(float(row.restricted_time) == restricted, 'Synthetic restricted cap mismatch')
        require(finite_or_nan_equal(row.event_time_over_Twindow, event_time / (BASE_WINDOW * row.rho)), 'Normalized event time mismatch')
        require(finite_or_nan_equal(row.restricted_time_over_Twindow, restricted / (BASE_WINDOW * row.rho)), 'Normalized restricted time mismatch')
        lower = 0.0 if observed and index == 0 else float(times[index - 1]) if observed else float('nan')
        require(finite_or_nan_equal(row.event_interval_lower, lower, 0.0)
                and finite_or_nan_equal(row.event_interval_upper, event_time, 0.0), 'Saved bracket metadata mismatch')
        require(row.event_time_semantics == 'first_qualifying_saved_sample_detection', 'E17 wording not present')
        key = tuple(getattr(row, item) for item in keys)
        expected_rows[key] = {'observed': observed, 'event_time': event_time, 'restricted': restricted,
                              'event_norm': event_time / (BASE_WINDOW * row.rho),
                              'restricted_norm': restricted / (BASE_WINDOW * row.rho)}
    auc_error = 0.0
    for row in auc.itertuples(index=False):
        mask = conditions[(row.seed, row.rho, row.branch)]
        deficits = [0.0 if row.branch == 'continue' or value else .5 - .1 for value in mask]
        expected_auc = math.fsum((times[index + 1] - times[index]) *
                                 (deficits[index] + deficits[index + 1]) / 2.0 for index in range(639))
        error = abs(float(row.auc_deficit) - expected_auc)
        auc_error = max(auc_error, error)
        require(error <= AUC_ATOL, 'Independent loop AUC mismatch')
    interactions = module.recovery_event_interactions(events)
    require(len(interactions) == 11520, 'Interaction row count changed')
    complete_count = nonzero_full = nonzero_complete = 0
    for row in interactions.itertuples(index=False):
        suffix = (row.metric, row.target_definition, row.event_type, row.hold_duration_system)
        cells = [expected_rows[(row.seed, row.rho, row.branch, *suffix)],
                 expected_rows[(row.seed, row.rho, 'continue', *suffix)],
                 expected_rows[(row.seed, 1.0, row.branch, *suffix)],
                 expected_rows[(row.seed, 1.0, 'continue', *suffix)]]
        complete = all(cell['observed'] for cell in cells)
        def did(field):
            values = [float(cell[field]) for cell in cells]
            return (values[0] - values[1]) - (values[2] - values[3])
        targets = {'restricted_time_DID': did('restricted'),
                   'restricted_time_over_Twindow_DID': did('restricted_norm'),
                   'event_observed_DID': did('observed'),
                   'conditional_event_time_DID': did('event_time') if complete else float('nan'),
                   'conditional_event_time_over_Twindow_DID': did('event_norm') if complete else float('nan')}
        require(bool(row.four_cell_complete_case) == complete, 'Four-cell eligibility mismatch')
        for field, target in targets.items():
            require(finite_or_nan_equal(getattr(row, field), target), 'Independent DID mismatch: ' + field)
        complete_count += int(complete)
        nonzero_full += int(abs(targets['restricted_time_DID']) > MEAN_ATOL)
        nonzero_complete += int(complete and abs(targets['conditional_event_time_DID']) > MEAN_ATOL)
    require(nonzero_full > 0 and nonzero_complete > 0, 'Vacuous all-zero DID fixture')
    chosen = events[(events['rho'] == 1.0) & (events['branch'] == 'reset_ema') &
                    (events['metric'] == 'density') & (events['hold_duration_system'] == 'fixed_physical_17p5')]
    draws = module.bootstrap_draws(run.seeds, 512, 2026090406)
    summary = module.pointwise_summary(chosen, group_columns=('event_type',), value_column='event_observed',
                                       seeds=run.seeds, draws=draws)
    rates = {str(row.event_type): float(row.mean) for row in summary.itertuples(index=False)}
    for key, expected in [('held', .75), ('held_retention', .6), ('held_recovery', .5)]:
        require(finite_or_nan_equal(rates[key], expected), 'Archetype cohort rate mismatch')
    require(all(int(value) == 40 for value in summary['n']), 'Recovery rates not full-cohort')
    classified = chosen[chosen['event_type'] == 'held'].set_index('seed')['held_classification']
    classification_counts = classified.value_counts().to_dict()
    require(classification_counts == {'retention': 24, 'none': 10, 'recovery': 6}, 'Classification partition changed')
    cohort = {'archetype_counts': {'always': 10, 'later': 6, 'both': 14, 'never': 10},
              'event_rates': rates, 'overlap_rate': .35,
              'exclusive_classification_counts': classification_counts,
              'recovery_fraction_among_ever_dropped': 20 / 30,
              'recovery_fraction_among_initially_below': 6 / 16,
              'reported_recovery_fraction_all_seeds': rates['held_recovery'],
              'post_treatment_selection_warning': 'Alternative conditional denominators are descriptive, not an automatic causal repair'}
    semantics = []
    masks = ref.archetype_masks()
    for name, mask in masks.items():
        expected = ref.reference(times, mask, 17.5)
        onset = expected['held_recovery']
        drop = expected['first_drop']
        confirm = ref.confirmation_index(times, onset, 17.5)
        semantics.append({'archetype': name, 'retention': expected['held_retention'],
                          'recovery_onset_index': onset, 'first_false_index': drop,
                          'source_event_time': float(times[onset]) if onset is not None else None,
                          'confirmation_time': float(times[confirm]) if confirm is not None else None,
                          'time_after_first_false': float(times[onset] - times[drop]) if onset is not None else None,
                          'restricted_recovery_score': float(times[onset]) if onset is not None else float(times[-1])})
    late = block(640, 620, 19)
    late_index = module._held_index(times, late, 17.5)
    require(late_index is None, 'Late unconfirmable run incorrectly counted')
    late_row = module._event_row(**row_arguments(late_index))
    require(late_row['restricted_time'] == float(times[-1]), 'Operational cap changed')
    events.to_csv(output / 'synthetic_events.csv', index=False)
    auc.to_csv(output / 'synthetic_auc.csv', index=False)
    interactions.to_csv(output / 'synthetic_event_interactions.csv', index=False)
    summary.to_csv(output / 'synthetic_cohort_summary.csv', index=False)
    dump(output / 'semantic_witnesses.json', {'cohort': cohort, 'time_roles': semantics,
                                              'late_tail': {'start': float(times[620]),
                                                            'fully_confirmed_event': False,
                                                            'restricted_time': late_row['restricted_time']}})
    return {'event_rows_checked': len(events), 'AUC_rows_checked': len(auc),
            'DID_rows_checked': len(interactions), 'complete_case_DID_rows': complete_count,
            'nonzero_full_cohort_DID_rows': nonzero_full, 'nonzero_complete_raw_DID_rows': nonzero_complete,
            'maximum_AUC_difference': auc_error, 'cohort': cohort, 'time_roles': semantics,
            'scope': 'Actual compute_recovery/interactions/selected pointwise summaries on synthetic scaffold; not validate_run/run_analysis or physical trajectory feasibility'}


def bootstrap_diagnostics(module, output):
    seeds = tuple(f's{index:02d}' for index in range(40))
    draws = module.bootstrap_draws(seeds, 512, 2026090406)
    arrays = {'zero': np.zeros(40), 'one': np.ones(40),
              'one_finite': np.array([7.0 if index == 3 else np.nan for index in range(40)]),
              'none_finite': np.full(40, np.nan)}
    frame = pd.DataFrame([{'group': group, 'seed': seed, 'value': value}
                          for group, values in arrays.items() for seed, value in zip(seeds, values, strict=True)])
    result = module.pointwise_summary(frame, group_columns=('group',), value_column='value', seeds=seeds, draws=draws)
    records = []
    for row in result.itertuples(index=False):
        values = arrays[row.group]
        means = []
        for indices in draws:
            finite = [float(values[int(index)]) for index in indices if math.isfinite(float(values[int(index)]))]
            if finite:
                means.append(math.fsum(finite) / len(finite))
        expected_n = sum(math.isfinite(float(value)) for value in values)
        require(int(row.n) == expected_n, 'Pointwise effective n mismatch')
        expected_bounds = (0.0, 0.0) if row.group == 'zero' else (1.0, 1.0) if row.group == 'one' else (7.0, 7.0) if row.group == 'one_finite' else (float('nan'), float('nan'))
        require(finite_or_nan_equal(row.pointwise_ci_lower, expected_bounds[0], 0.0)
                and finite_or_nan_equal(row.pointwise_ci_upper, expected_bounds[1], 0.0), 'Bootstrap diagnostic mechanism changed')
        records.append({'group': row.group, 'finite_n': row.n,
                        'mean': row.mean, 'lower': row.pointwise_ci_lower, 'upper': row.pointwise_ci_upper,
                        'valid_bootstrap_replicates_calculated_independently': len(means),
                        'empty_bootstrap_replicates_calculated_independently': len(draws) - len(means),
                        'source_interval_type': row.interval_type})
    result.to_csv(output / 'bootstrap_pointwise_summary.csv', index=False)
    dump(output / 'bootstrap_diagnostics.json', records)
    return {'iterations': 512, 'seed': 2026090406, 'groups': records,
            'same_joint_draws_across_groups': True,
            'inference_limit': 'Empirical fixed-cohort resampling diagnostic, not boundary-valid population CI; sparse finite groups also have unreported empty draws',
            'iid_Bernoulli_example_p_point01_n40_probability_all_zero': float(Fraction(99, 100) ** 40)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('checks'))
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    print('Verifying/loading reviewed candidate', flush=True)
    module = load_upstream.load(args.source)
    stages = [('exhaustive_small', lambda: exhaustive_small(module)),
              ('saved_grid', lambda: saved_grid_checks(module, output)),
              ('policy_boundaries', lambda: policy_boundary_checks(module, output)),
              ('mutations', lambda: mutation_controls(module, output)),
              ('synthetic_pipeline', lambda: synthetic_pipeline(module, output)),
              ('bootstrap', lambda: bootstrap_diagnostics(module, output))]
    results = {}
    for name, function in stages:
        print('START ' + name, flush=True)
        stage_start = time.perf_counter()
        try:
            results[name] = function()
        except Exception as error:
            dump(output / 'failure.json', {'stage': name, 'error_type': type(error).__name__, 'message': str(error)})
            raise
        print('DONE ' + name + ' seconds=' + str(time.perf_counter() - stage_start), flush=True)
    errors = io.StringIO()
    with mock.patch.object(module, 'run_analysis', side_effect=RuntimeError('must not enter real pipeline')):
        with contextlib.redirect_stderr(errors):
            status = module.main(['/nonexistent', '--bootstrap-seed', '1'])
    require(status == 2 and 'UNAUDITED CANDIDATE' in errors.getvalue(), 'Candidate opt-in guard failed')
    manifest = load_upstream.verify_sources(args.source)
    results.update({'tested_main': manifest['commit'], 'upstream_modules_unchanged': len(manifest['modules']),
                    'all_preregistered_robust_checks_passed': True, 'optimized_python': not __debug__,
                    'candidate_cli_default_refuses_real_pipeline': True,
                    'python': sys.version, 'packages': {'numpy': np.__version__, 'pandas': pd.__version__},
                    'no_real_trajectories_or_new_lean': True, 'elapsed_seconds': time.perf_counter() - start,
                    'review_disposition': 'QUALIFIED_SOURCE_AND_SYNTHETIC_CONFORMANCE;NOT_PROJECT_FREEZE_OR_POPULATION_INFERENCE_APPROVAL'})
    dump(output / 'cycle_results.json', results)
    print(json.dumps(safe(results), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: audit_v41.py -->

### reference_contract.py

<!-- BEGIN_CRITICAL_FILE: reference_contract.py -->
```python
"""Independent forward-run, exact-rational reference for the stated saved-grid policy.
No import of candidate code, reverse run-end algorithm, or searchsorted.
This is a finite executable specification, not a universal float64 theorem.
"""
from fractions import Fraction
from functools import lru_cache
import math

BAND = Fraction(1, 10_000_000_000)  # preregistered 1e-10 gray boundary band
TOLERANCE_FRACTION = Fraction(1, 1_000_000)


def as_fraction(value):
    return Fraction.from_float(float(value))


def forward_runs(condition):
    values = tuple(bool(value) for value in condition)
    runs = []
    index = 0
    while index < len(values):
        if not values[index]:
            index += 1
            continue
        start = index
        while index + 1 < len(values) and values[index + 1]:
            index += 1
        runs.append((start, index))
        index += 1
    return values, runs


@lru_cache(maxsize=32)
def grid_data(values):
    # Cache only immutable input geometry, never candidate outputs/answers.
    ts = tuple(as_fraction(value) for value in values)
    steps = [right - left for left, right in zip(ts, ts[1:]) if right > left]
    tau = TOLERANCE_FRACTION * min(steps) if steps else Fraction(0)
    return ts, tau


def exact_tolerance(times):
    return grid_data(tuple(float(value) for value in times))[1]


def reference(times, condition, duration, adjustment=Fraction(0)):
    values, runs = forward_runs(condition)
    ts, tau = grid_data(tuple(float(value) for value in times))
    if len(ts) != len(values):
        raise ValueError('Reference requires matching input lengths')
    required = as_fraction(duration) + adjustment - tau
    qualifies = [(start, end) for start, end in runs if ts[end] - ts[start] >= required]
    first_drop = next((index for index, value in enumerate(values) if not value), None)
    held = qualifies[0][0] if qualifies else None
    retention = 0 if qualifies and qualifies[0][0] == 0 else None
    recovery = next((start for start, _ in qualifies if first_drop is not None and start > first_drop), None)
    label = 'retention' if retention is not None else 'recovery' if recovery is not None else 'none'
    return {'held': held, 'held_retention': retention, 'held_recovery': recovery,
            'classification': label,
            'first': next((index for index, value in enumerate(values) if value), None),
            'sustained': runs[-1][0] if runs and runs[-1][1] == len(values) - 1 else None,
            'first_drop': first_drop, 'qualifying_runs': qualifies}


def robust_expectation(times, condition, duration):
    lower = reference(times, condition, duration, -BAND)
    upper = reference(times, condition, duration, BAND)
    keys = ('held', 'held_retention', 'held_recovery', 'classification')
    robust = all(lower[key] == upper[key] for key in keys)
    return robust, reference(times, condition, duration), lower, upper


def confirmation_index(times, start, duration):
    if start is None:
        return None
    ts = tuple(as_fraction(value) for value in times)
    threshold = as_fraction(duration) - exact_tolerance(times)
    return next((index for index in range(start, len(ts)) if ts[index] - ts[start] >= threshold), None)


def minimum_half_grid_steps(duration):
    required = as_fraction(duration) - TOLERANCE_FRACTION * Fraction(1, 2)
    return max(0, math.ceil(2 * required))


def archetype_masks(length=640):
    if length < 220:
        raise ValueError('The preregistered archetypes need at least220 samples')
    always = [True] * length
    later = [False] * length
    later[40:120] = [True] * 80
    both = [False] * length
    both[:80] = [True] * 80
    both[120:220] = [True] * 100
    never = [False] * length
    return {'always': always, 'later': later, 'both': both, 'never': never}
```
<!-- END_CRITICAL_FILE: reference_contract.py -->

### load_upstream.py

<!-- BEGIN_CRITICAL_FILE: load_upstream.py -->
```python
"""Load only the reviewed candidate with its verified public dependencies.
Owned-report tooling, not a sandbox for arbitrary submitted code.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def manifest():
    return json.loads((HERE / 'source_modules.json').read_text())


def verify_sources(source):
    data = manifest()
    source = Path(source).resolve()
    for record in data['modules']:
        content = (source / record['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if blob != record['blob'] or len(content) != record['bytes']:
            raise RuntimeError('Acquired source changed: ' + record['path'])
    return data


def load(source):
    source = Path(source).resolve()
    data = verify_sources(source)
    platform = source / data['platform']
    sys.path.insert(0, str(platform))
    sys.path.insert(1, str(source))
    name = 'r040282_reviewed_v41'
    specification = importlib.util.spec_from_file_location(name, source / data['candidate'])
    if specification is None or specification.loader is None:
        raise ImportError('Unable to load reviewed candidate')
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module  # dataclass registration must precede execution
    try:
        specification.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module
```
<!-- END_CRITICAL_FILE: load_upstream.py -->

### ESTIMAND_CONTRACT.json

<!-- BEGIN_CRITICAL_FILE: ESTIMAND_CONTRACT.json -->
```json
{
  "status": "PROPOSED_REVIEW_AID_NOT_REGISTERED_OR_FROZEN",
  "reviewed_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "observation_grid": {
    "nominal_first_time": 0.01,
    "nominal_spacing": 0.5,
    "samples": 640,
    "last_saved_time": 319.51,
    "not_observed": ["unsaved step-level excursions", "t=0", "t=320"]
  },
  "hold_policy": {
    "scope": "contiguous true SAVED observations, not continuous path certification",
    "tolerance": "1e-6 times minimum positive saved-grid spacing",
    "strict_duration_and_tolerant_duration_are_different": true,
    "review_gray_band": "1e-10 around the exact rational tolerance boundary; gray cases not conformance passes"
  },
  "events": {
    "held": "first saved onset of any fully observed qualifying true run",
    "held_retention": "initial true run qualifies; not a claim of retention forever",
    "held_recovery": "first qualifying true run after the first False saved observation, including False at index0",
    "held_classification": "exclusive trajectory label; retention takes precedence over recovery",
    "event_flags_can_overlap": true,
    "identity": "P(held)=P(held_retention)+P(held_recovery)-P(both)",
    "classified_recovery": "held_recovery AND NOT held_retention"
  },
  "time_roles": {
    "event_time_for_held_rows": "retrospective run-onset timestamp relative to the branch origin",
    "not_event_time": ["online confirmation timestamp", "elapsed time since first drop", "first physical crossing time"],
    "confirmation": "first later saved sample satisfying the hold-span policy; requires future observations",
    "adjacent_interval_fields": "sampling metadata only; not an identified first-physical-crossing interval without assumptions",
    "first_saved_retention": "index0 means true at first saved time0.01; behavior before that is not reconstructed"
  },
  "population_and_cap": {
    "reported_event_rate_denominator": "all40 supplied seeds, including never-dropped seeds",
    "alternative_ever_dropped_denominator": "descriptive alternative only; post-treatment selection is not a default causal repair",
    "nonobserved_restricted_time": 319.51,
    "meaning": "finite-support capped confirmation-qualified-onset score",
    "not_meaning": "ordinary physical-onset censoring at319.51",
    "last_eligible_onset": "last saved onset whose duration can finish by the support end; depends on duration/rho",
    "comparison_warning": "an always-retained reference can have NO recovery event and receive the cap; a lower recovery score is not automatically better overall resilience"
  },
  "inference": {
    "interval_scope": "pointwise empirical joint-seed resampling diagnostic",
    "boundary_intervals_not_population_confidence_certificates": true,
    "conditional_time_summary": "finite observed event times only",
    "conditional_raw_DID": "same seed has all four cell events; not merely each branch has some events",
    "requested_diagnostics": ["finite_n", "bootstrap_valid_replicates", "bootstrap_empty_replicates", "empirical_zero_variance", "insufficient_n_or_no_event_flag"],
    "no_new_metric_or_interval_replacement_authorized": true
  },
  "limits": [
    "no real S01 trajectory reanalysis",
    "no run_analysis artifact/provenance or atomic-output acceptance audit",
    "no universal float64 conformance theorem",
    "no Lean compilation or coupled dynamics result",
    "outside source/synthetic review is not project freeze or registry approval"
  ]
}
```
<!-- END_CRITICAL_FILE: ESTIMAND_CONTRACT.json -->

### source_modules.json

<!-- BEGIN_CRITICAL_FILE: source_modules.json -->
```json
{
  "repo": "jacobbrainard84-knightninja/AIEFS",
  "commit": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "candidate": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py",
  "platform": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4",
  "modules": [
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py",
      "blob": "df78b01607e6792afe9afc09fcc9b0cb83585ec6",
      "bytes": 70127
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/__init__.py",
      "blob": "2693906361d9b8a958dcca3809a1e48f3ba3d37b",
      "bytes": 429
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/artifacts.py",
      "blob": "1755fd1c91c78306efe185614a5ec25ccb2812f0",
      "bytes": 12582
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/authority.py",
      "blob": "23f50b547e5035cd8638ccf00525e18ffeab188f",
      "bytes": 9065
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/branches.py",
      "blob": "28e364284afbf799ee2d474bb5791a6efab3f56c",
      "bytes": 3477
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/collectors.py",
      "blob": "06ea96da686224bdbbf0790792e83a58f73b2abe",
      "bytes": 9992
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/factors.py",
      "blob": "a9c16999baf18b0ada513bc29b62ccb0da0c7ebf",
      "bytes": 12545
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/registry.py",
      "blob": "2b50e409c851bf02b87ecdd3b1fe56fec2c66169",
      "bytes": 3180
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/runner.py",
      "blob": "9e3eb431444f3f32b3b3e616014332939bf0ea59",
      "bytes": 32813
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/spec.py",
      "blob": "6ce7361d85e14946a0b854bb9078bcb58f75e9dc",
      "bytes": 19734
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/studies/__init__.py",
      "blob": "2b1fcdde0aa007b747e60cf0bdd234ab8e186840",
      "bytes": 58
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/validation.py",
      "blob": "9afffc1c0e3d1f8e0ad726e33d3b059e9337a1da",
      "bytes": 11178
    }
  ]
}
```
<!-- END_CRITICAL_FILE: source_modules.json -->

### fetch_public_dependencies.py

<!-- BEGIN_CRITICAL_FILE: fetch_public_dependencies.py -->
```python
"""Download only the reviewed public Python dependency set; execute no code.

No commit author/contact/signature API metadata is requested or persisted.
Existing mismatched files cause an error rather than silent replacement.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('upstream'))
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).resolve().parent / 'source_modules.json').read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    def acquire(record):
        name = record['path']
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or relative.suffix != '.py':
            raise ValueError('Unexpected public module path')
        target = args.output / relative
        if target.exists():
            content = target.read_bytes()
        else:
            url = ('https://raw.githubusercontent.com/' + manifest['repo'] + '/' +
                   manifest['commit'] + '/' + quote(name, safe='/'))
            request = urllib.request.Request(url, headers={'User-Agent': 'Researcher-040282-read-only'})
            with urllib.request.urlopen(request, timeout=60) as response:
                content = response.read()
        blob = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if blob != record['blob'] or len(content) != record['bytes']:
            raise RuntimeError('Dependency differs from reviewed source: ' + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return name
    with ThreadPoolExecutor(max_workers=4) as pool:
        names = list(pool.map(acquire, manifest['modules']))
    print(json.dumps({'tested_main': manifest['commit'], 'public_modules_fetched_and_verified': len(names),
                      'code_executed_by_fetcher': False,
                      'metadata_policy': 'no author/committer/contact/signature payloads'}, indent=2))


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: fetch_public_dependencies.py -->

### extract_from_report.py

<!-- BEGIN_CRITICAL_FILE: extract_from_report.py -->
```python
"""Extract seven named text files from the owned006 standalone audit.
Does not import/run code, fetch dependencies, or sandbox arbitrary submissions.
"""
import argparse
import json
from pathlib import Path
import re

NAMES = {'audit_v41.py', 'reference_contract.py', 'load_upstream.py',
         'ESTIMAND_CONTRACT.json', 'source_modules.json',
         'fetch_public_dependencies.py', 'extract_from_report.py'}
PATTERN = re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                     r'<!-- END_CRITICAL_FILE: \1 -->', re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    pairs = PATTERN.findall(args.report.read_text())
    if len(pairs) != len(NAMES) or {name for name, _ in pairs} != NAMES:
        raise ValueError('Missing/duplicate/unexpected critical-file blocks')
    args.output.mkdir(parents=True, exist_ok=True)
    for name, content in pairs:
        if Path(name).name != name:
            raise ValueError('Unexpected extraction path')
        text = content + '\n'
        target = args.output / name
        if target.exists() and target.read_text() != text:
            raise ValueError('Existing different extracted file: ' + name)
        target.write_text(text)
    print(json.dumps({'critical_files_extracted': len(pairs), 'code_executed': False}, indent=2))


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: extract_from_report.py -->


## Appendix B — actual normal-run result record

```json
{
  "exhaustive_small": {
    "Boolean_patterns_per_origin": 512,
    "origins": 2,
    "durations": 3,
    "robust_cases": 3072,
    "mismatches": 0,
    "gray_not_counted": 0
  },
  "saved_grid": {
    "translated_robust_cases": 2350,
    "nominal_selected_robust_cases": 60,
    "other_robust_cases": 12,
    "invalid_duration_rejections": 12,
    "maximum_nominal_timestamp_difference": 2.842170943040401e-14,
    "details": [
      {
        "duration": 17.5,
        "all_valid_starts": 605,
        "exact_block_and_one_step_short_cases": 1210
      },
      {
        "duration": 35.0,
        "all_valid_starts": 570,
        "exact_block_and_one_step_short_cases": 1140
      },
      {
        "rho": 0.5,
        "duration": 8.751458576429407,
        "minimum_half_grid_steps": 18,
        "selected_starts": [
          0,
          1,
          32,
          100,
          310,
          621
        ],
        "last_eligible_onset": 310.51
      },
      {
        "rho": 0.75,
        "duration": 13.12718786464411,
        "minimum_half_grid_steps": 27,
        "selected_starts": [
          0,
          1,
          32,
          100,
          306,
          612
        ],
        "last_eligible_onset": 306.01
      },
      {
        "rho": 1.0,
        "duration": 17.502917152858814,
        "minimum_half_grid_steps": 36,
        "selected_starts": [
          0,
          1,
          32,
          100,
          301,
          603
        ],
        "last_eligible_onset": 301.51
      },
      {
        "rho": 1.5,
        "duration": 26.25437572928822,
        "minimum_half_grid_steps": 53,
        "selected_starts": [
          0,
          1,
          32,
          100,
          293,
          586
        ],
        "last_eligible_onset": 293.01
      },
      {
        "rho": 2.0,
        "duration": 35.00583430571763,
        "minimum_half_grid_steps": 71,
        "selected_starts": [
          0,
          1,
          32,
          100,
          284,
          568
        ],
        "last_eligible_onset": 284.01
      }
    ]
  },
  "policy_boundaries": {
    "policy_tau": 4.999999999999716e-07,
    "gray_boundary_band": 1e-10,
    "groups": [
      {
        "factor": -2.0,
        "duration": 17.499999,
        "robust_cases": 605,
        "gray_cases_not_counted_as_conformance": 0,
        "accepted_blocks": 605
      },
      {
        "factor": -0.5,
        "duration": 17.49999975,
        "robust_cases": 605,
        "gray_cases_not_counted_as_conformance": 0,
        "accepted_blocks": 605
      },
      {
        "factor": 0.0,
        "duration": 17.5,
        "robust_cases": 605,
        "gray_cases_not_counted_as_conformance": 0,
        "accepted_blocks": 605
      },
      {
        "factor": 0.5,
        "duration": 17.50000025,
        "robust_cases": 605,
        "gray_cases_not_counted_as_conformance": 0,
        "accepted_blocks": 605
      },
      {
        "factor": 1.0,
        "duration": 17.5000005,
        "robust_cases": 0,
        "gray_cases_not_counted_as_conformance": 605,
        "accepted_blocks": 553
      },
      {
        "factor": 2.0,
        "duration": 17.500001,
        "robust_cases": 605,
        "gray_cases_not_counted_as_conformance": 0,
        "accepted_blocks": 0
      }
    ],
    "tiny_duration_stress": {
      "duration": 1e-07,
      "single_sample_held": 639,
      "interpretation": "tolerant policy, not literal positive-duration support"
    },
    "gray_cases_are_not_conformance_passes": true
  },
  "mutations": [
    {
      "mutant": "zero_tolerance",
      "detected": true,
      "reason": "zero_tolerance: held: observed=None, expected=32"
    },
    {
      "mutant": "double_duration",
      "detected": true,
      "reason": "double_duration: held: observed=None, expected=0"
    },
    {
      "mutant": "any_is_retention_only",
      "detected": true,
      "reason": "any_is_retention_only: held: observed=None, expected=2"
    },
    {
      "mutant": "recovery_includes_initial_retention",
      "detected": true,
      "reason": "recovery_includes_initial_retention: held_recovery: observed=0, expected=None"
    },
    {
      "mutant": "recovery_is_exclusive_or_suppressed_after_retention",
      "detected": true,
      "reason": "recovery_is_exclusive_or_suppressed_after_retention: held_recovery: observed=None, expected=4"
    },
    {
      "mutant": "retention_is_initial_true_only",
      "detected": true,
      "reason": "retention_is_initial_true_only: held_retention: observed=0, expected=None"
    },
    {
      "mutant": "recovery_precedence",
      "detected": true,
      "reason": "recovery_precedence: classification: observed=recovery, expected=retention"
    },
    {
      "mutant": "onset_is_confirmation",
      "detected": true,
      "reason": "held onset mislabeled as confirmation"
    }
  ],
  "synthetic_pipeline": {
    "event_rows_checked": 19200,
    "AUC_rows_checked": 1600,
    "DID_rows_checked": 11520,
    "complete_case_DID_rows": 4752,
    "nonzero_full_cohort_DID_rows": 2496,
    "nonzero_complete_raw_DID_rows": 1200,
    "maximum_AUC_difference": 2.842170943040401e-14,
    "cohort": {
      "archetype_counts": {
        "always": 10,
        "later": 6,
        "both": 14,
        "never": 10
      },
      "event_rates": {
        "held": 0.75,
        "held_recovery": 0.5,
        "held_retention": 0.6
      },
      "overlap_rate": 0.35,
      "exclusive_classification_counts": {
        "retention": 24,
        "none": 10,
        "recovery": 6
      },
      "recovery_fraction_among_ever_dropped": 0.6666666666666666,
      "recovery_fraction_among_initially_below": 0.375,
      "reported_recovery_fraction_all_seeds": 0.5,
      "post_treatment_selection_warning": "Alternative conditional denominators are descriptive, not an automatic causal repair"
    },
    "time_roles": [
      {
        "archetype": "always",
        "retention": 0,
        "recovery_onset_index": null,
        "first_false_index": null,
        "source_event_time": null,
        "confirmation_time": null,
        "time_after_first_false": null,
        "restricted_recovery_score": 319.51
      },
      {
        "archetype": "later",
        "retention": null,
        "recovery_onset_index": 40,
        "first_false_index": 0,
        "source_event_time": 20.01,
        "confirmation_time": 37.51,
        "time_after_first_false": 20.0,
        "restricted_recovery_score": 20.01
      },
      {
        "archetype": "both",
        "retention": 0,
        "recovery_onset_index": 120,
        "first_false_index": 80,
        "source_event_time": 60.01,
        "confirmation_time": 77.51,
        "time_after_first_false": 20.0,
        "restricted_recovery_score": 60.01
      },
      {
        "archetype": "never",
        "retention": null,
        "recovery_onset_index": null,
        "first_false_index": 0,
        "source_event_time": null,
        "confirmation_time": null,
        "time_after_first_false": null,
        "restricted_recovery_score": 319.51
      }
    ],
    "scope": "Actual compute_recovery/interactions/selected pointwise summaries on synthetic scaffold; not validate_run/run_analysis or physical trajectory feasibility"
  },
  "bootstrap": {
    "iterations": 512,
    "seed": 2026090406,
    "groups": [
      {
        "group": "none_finite",
        "finite_n": 0,
        "mean": null,
        "lower": null,
        "upper": null,
        "valid_bootstrap_replicates_calculated_independently": 0,
        "empty_bootstrap_replicates_calculated_independently": 512,
        "source_interval_type": "joint-seed-resampling_pointwise_percentile_95pct"
      },
      {
        "group": "one",
        "finite_n": 40,
        "mean": 1.0,
        "lower": 1.0,
        "upper": 1.0,
        "valid_bootstrap_replicates_calculated_independently": 512,
        "empty_bootstrap_replicates_calculated_independently": 0,
        "source_interval_type": "joint-seed-resampling_pointwise_percentile_95pct"
      },
      {
        "group": "one_finite",
        "finite_n": 1,
        "mean": 7.0,
        "lower": 7.0,
        "upper": 7.0,
        "valid_bootstrap_replicates_calculated_independently": 337,
        "empty_bootstrap_replicates_calculated_independently": 175,
        "source_interval_type": "joint-seed-resampling_pointwise_percentile_95pct"
      },
      {
        "group": "zero",
        "finite_n": 40,
        "mean": 0.0,
        "lower": 0.0,
        "upper": 0.0,
        "valid_bootstrap_replicates_calculated_independently": 512,
        "empty_bootstrap_replicates_calculated_independently": 0,
        "source_interval_type": "joint-seed-resampling_pointwise_percentile_95pct"
      }
    ],
    "same_joint_draws_across_groups": true,
    "inference_limit": "Empirical fixed-cohort resampling diagnostic, not boundary-valid population CI; sparse finite groups also have unreported empty draws",
    "iid_Bernoulli_example_p_point01_n40_probability_all_zero": 0.6689717585696805
  },
  "tested_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "upstream_modules_unchanged": 12,
  "all_preregistered_robust_checks_passed": true,
  "optimized_python": false,
  "candidate_cli_default_refuses_real_pipeline": true,
  "python": "3.13.16 (main, Oct  6 2026, 04:38:44) [GCC 14.2.0]",
  "packages": {
    "numpy": "2.3.5",
    "pandas": "2.2.3"
  },
  "no_real_trajectories_or_new_lean": true,
  "elapsed_seconds": 18.289061058000016,
  "review_disposition": "QUALIFIED_SOURCE_AND_SYNTHETIC_CONFORMANCE;NOT_PROJECT_FREEZE_OR_POPULATION_INFERENCE_APPROVAL"
}
```


## Appendix C — preregistration and scoped review decision

### PLAN.md

```text
# Cycle 006 preregistration — bounded v4.1 source/synthetic review

Researcher040282. Session preparation stamp2026-09-04, Atlantic/Reykjavik.
Prior owner/seat correspondence carries2026-11-08 handoff labels; those are not
reconstructed execution dates. Do not infer dates from compiler builds or logs.

## Source and nonduplication

Current main acquired read-only: eb3933c196ee19e80e1621ae80d89ca72e6d9485.
Inbox: b466ab6cdd564ce3f7848e7701b378c5f0cc475f. No new targeted005 feedback found
in the selected navigation. Main17 and inbox37 files acquired before this plan;
local import dependencies will be verified before any candidate execution.

Target: AIEF_Experiments/aief_modular_platform_v1_analysis_v4/
AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py. It remains an unaudited synthetic-
only candidate. E17 already corrects saved-grid detection/interval-censoring and
min-positive-saved-spacing tolerance wording. Do NOT rediscover frozen-v4 misses,
re-report corrected strings, or infer actual saved-run impact. Existing candidate
tests were read but are not our independent oracle. No real trajectory files,
--allow-unaudited-candidate, run_analysis or production simulation will be used.

Prior own A-F2/A-F3 already state boundary bootstrap and shorter onset follow-up
limitations. Here verify/explain their precise persistence in the CURRENT
candidate; do not rename them new defects. No code patch or altered estimand is
promised if candidate behavior matches its declared operational contract.

## Operational reference, before tests

Saved grid: intended t_i=1/100+i/2, i=0..639; actual supplied timestamps separately
checked against the acquired candidate's declared array. On a Boolean condition,
find maximal contiguous true runs by a forward scan, independent of candidate
_run_end and searchsorted. A run start s qualifies if its endpoint span is at
least D minus tau, with tau=1e-6 times the minimum positive saved-grid spacing.
Compute reference spans/thresholds with Fraction, not candidate float additions.

Run-onset outputs:
H = earliest qualifying run start, or None;
R =0 iff the initial true run qualifies;
V = earliest qualifying true run start after the first False sample (including
False at index0), or None;
class = retention if R, else recovery if V, else none.

For a sorted grid, later starts in one true run cannot have more remaining span
than its start. Hence H exists iff R exists OR V exists. R and V can both exist:
classification is exclusive by retention precedence, but event flags are not a
partition. Explain/probe rather than silently redefine V or its denominator.

Floating policy versus exact duration must remain separate. The declared tau
intentionally accepts some spans shorter than D by at most approximately tau;
this is not a new bug by itself. For nominal-grid/binary rounding comparisons use
a preregistered1e-10 boundary band: if exact reference outputs at D−1e-10 and
D+1e-10 agree, candidate indices/labels must match EXACTLY (no relaxed index
allowance). If they differ, label the case gray/undetermined and do NOT count it
as conformance. All ordinary/exact-duration cases lie far inside tau's margin.
Record a separate near-tau-boundary sweep; do not demand arbitrary universal
translation invariance within floating gray zones or quietly change the rule.

## Fixed finite checks

1. Exhaust all512 Boolean patterns of length9, durations0.5,1.0,1.25, at origins
   0.01 and100.01 on half-unit grids. Compare H/R/V/class, any/sustained helpers,
   source input preservation, and logical union/precedence identities.
2. On the actual640-point saved grid, test EVERY valid translated start at
   D=17.5 and35.0: exact-minimum-length true blocks and one-step-short blocks.
   Also test representative nominal holds17.502917152858814*rho at
   rho=(.5,.75,1,1.5,2), using starts0,1,32,100,middle,last (deduplicate as needed),
   minimum qualifying blocks and one-step-short blocks. Include all-false,
   all-true, final-sample-only, initial retention, later recovery and tail-only
   fixtures with insufficient confirmation support.
3. Separate policy stress sweep: durations17.5+f*tau for f=(-2,-.5,0,.5,1,2),
   all605 candidate starts of a17.5 block. Record robust versus gray outcomes,
   not a universal floating-point guarantee. Include a tiny positive duration
   below tau as a documented policy-extension stress case, not a normal caller.
4. Exercise actual compute_recovery on a fully synthetic40-seed ×5-rho ×4-branch
   scaffold, generated in a temporary directory. Continue reference stays at.5;
   target=.45; reset_ema uses four archetypes:10 always true,6 initially false
   then held,14 initially held then later dropped/recovered,10 never held.
   Held runs last comfortably beyond all specified holds. Source should produce
   19200 event rows/1600 AUC rows; verify selected rows versus independent masks,
   source interactions11520 rows, full-cohort/complete-case fields and summaries.
   To avoid a vacuous all-zero DID check, shift reset_B masks by10 saved samples
   at nonbaseline rho, leaving reset_ema's planned cohort unchanged. Require a
   nonzero full-cohort and a nonzero complete-case raw DID positive control.
   This calls compute helpers on synthetic Run objects, NOT full validate_run,
   artifact/provenance checks, production feasibility or all run_analysis stages.
5. For that fixed cohort, expected rates R=.6,V=.5,H=.75,overlap=.35;
   classification-recovery=.15. V among ever-dropped seeds is20/30, NOT the
   full-cohort.5. Source rec_time is branch-relative retrospective onset, NOT
   time since first drop; confirmation time is later by the hold/grid rule.
   Capture onset, first drop, confirmation and branch-relative/after-loss times.
6. Actual pointwise_summary with512 joint seed draws, seed2026090406: all-zero,
   all-one, one-finite and all-missing groups. Record degenerate intervals,
   effective n and independently calculated empty/valid bootstrap counts.
   These are fixed-cohort resampling diagnostics, not population-valid boundary
   CIs; no coverage claim or real S01 group count is being established here.

## Numeric comparison allowances (also before execution)

Index/label/Boolean agreement is exact. Timestamp fields use the declared saved
array exactly. Normalized ratios/means/DID allow absolute5e-13,relative0;
independent loop-trapezoid AUC allows absolute5e-12,relative0 for640 terms.
These are not tolerances for event indices or a way to promote gray cases.
Keep mismatches/logs rather than enlarge these allowances after seeing results.

## Strongest wrong-model controls

The harness must detect at least one witness for each admitted wrong model:
zero tolerance/addition miss; double-sized hold requirement; retention-only
substituted for any held; recovery incorrectly includes initial retention;
recovery incorrectly discards later recovery after an initially held run;
retention defined as initial True alone; classification gives recovery precedence;
onset mislabeled as confirmation; recovery flags treated as an exclusive class.
Use small predetermined witnesses and actual-source in-process substitutions,
restored after each. Do not accept a dependency/import failure as a detected
mathematical/semantic mutant. Snapshots/oracle inputs precede candidate calls;
never let a mutable call move the expected answer with the observed input.

No assertion-based acceptance decisions that disappear under python -O. Run the
owned suite normally and optimized. Confirm acquired source files unchanged.
No Lean installation/compilation is planned for this software/estimand audit.
No claim that all640-bit paths, all floating schedules, or every analysis stage
have been proved correct. A limited qualified synthetic review is an acceptable
outcome; do not force a new defect or silently freeze/promote the candidate.

## Handoff acceptance

Produce a numbered standalone report with full critical source/oracle code and
essential results inline; extract/run it with verified public dependencies.
Provide a proposed machine-readable ESTIMAND_CONTRACT as review aid, not a
registered new scientific estimand or changed production output. Keep original
labels/review scope separate:94 prior Lean compilation/footprint confirmations
are not review of these new controls. Main/frozen v4/candidate sources untouched.

Update root state/queue/ledger from observed outcomes only; current main named
exactly. Metadata minimal from acquisition, including no author/contact/signed
payloads. Unpack/index all cited logs in the outgoing bundle. No remote push,
PR, direct inbox/salvage merge, registry edit, bot contact or automatic upload.

## Post-execution administrative notice (not part of scientific preregistration)

Original normal/optimized tests have completed. ADMINISTRATIVE_PROVENANCE.md was
added after those runs to distinguish the supplied preparation label from prior
owner handoff labels and unknown historical chronology. Scientific protocol,
allowances, gray-band policy and seed are unchanged. The pre-notice plan text is
preserved in PLAN_PREREGISTERED_BEFORE_ADMIN_NOTICE.md. This notice is not
represented as predating execution.
```

### review_decision.json

```json
{
  "reviewed_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "disposition": "QUALIFIED_SOURCE_AND_SYNTHETIC_CONFORMANCE",
  "positive_scope": [
    "held/retention/recovery/classification and first/sustained helpers on stated finite cases",
    "actual synthetic compute_recovery event rows, AUC and event DID values",
    "specified full-cohort pointwise rates and boundary bootstrap mechanisms",
    "opt-in guard and unchanged12 public modules"
  ],
  "not_approved": [
    "project freeze or artifact/claim registry promotion",
    "real S01 output changes or zero-impact claims",
    "population-valid boundary confidence intervals",
    "full validate_run/run_analysis/provenance/atomic bundle audit",
    "all floating schedules or translation invariance at tolerance boundaries",
    "metric-channel swaps or distinct target-channel behavior: synthetic masks/targets are deliberately shared",
    "physical trajectory feasibility, step-level crossings, full dynamics or Lean theorem"
  ],
  "known_work_acknowledged": [
    "frozen-v4 exact-boundary miss already known; frozen-v4 module not executed for this audit",
    "E17 saved-grid/tolerance wording corrections already present on main",
    "A-F2/A-F3 bootstrap/onset-observability limitations previously reported; current review makes candidate contract precise, not new novelty claims"
  ],
  "scope_of_gray_cases": {
    "policy_boundary_gray": 605,
    "accepted_in_this_environment": 553,
    "rejected_in_this_environment": 52,
    "counted_as_conformance_passes": 0,
    "boundary_band": 1e-10
  },
  "next_owner_seat_choices": [
    "agree that event_time means retrospective qualifying-run onset, not confirmation or time since first drop",
    "acknowledge overlapping event flags versus exclusive classification and fixed40 denominator",
    "choose whether finite-support capped scores are the intended comparisons; changing the cap/denominator is an estimand change",
    "require explicit empirical/bootstrap diagnostic limitations or separately chosen population inference before citing confidence claims",
    "independently review this harness/counterexamples and any real-data execution before freeze"
  ],
  "normal_and_optimized_scientific_results_agree": true,
  "no_source_patch_or_remote_submission": true,
  "peer_review_of_this_harness_received": false
}
```

### ADMINISTRATIVE_PROVENANCE.md

```text
# 006 administrative provenance clarification

This notice was written **after** the original normal and optimized synthetic
executions, before report publication. It did not precede those executions.

The current session supplies2026-09-04 in Atlantic/Reykjavik as its preparation
label. Prior owner/seat correspondence supplies2026-11-08 handoff labels, which
are retained as correspondence/folder labels. Runtime clock, compiler build
strings, folder dates and durations do not independently establish historical
execution chronology. No claim is made to reconstruct004's execution date.

Scientific006 preregistration—including the oracle/domain, comparison allowances,
1e-10 gray band, nonzero-DID fixture and seed2026090406—was fixed before the first
candidate execution. This clarification does NOT alter/backdate that protocol,
change any source/seed, promote gray cases, or imply a rerun of historical science.
The original delivered004/005 reports, archives and protected snapshots remain
unchanged. Their narrower closure/review scopes remain in force. Current006
navigation/state is finalized only from observed results, separately from those
historical files; source/header labels are not audited as scientific findings.

For owner upload, use a newly dated audit-inbox folder and the owner's actual
upload date. A preparation label is not a receipt, real-run timestamp or remote
submission. No remote upload is performed by the agent.
```

