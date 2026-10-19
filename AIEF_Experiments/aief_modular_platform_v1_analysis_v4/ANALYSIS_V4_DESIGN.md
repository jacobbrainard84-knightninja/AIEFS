# AIEF-1.4 T-window Analysis v4

## Status

Analysis v4 is a **separately versioned reanalysis** of the existing S01 raw trajectories. It does not replace Analysis v3 and does not constitute an independent experiment.

- Analysis v3 remains the prespecified legacy-compatible analysis.
- Analysis v4 corrects and clarifies recovery and inferential semantics that can be addressed from the saved trajectories.
- Engine v2 is still required for t=0/t=320 observations, step-resolution crossings, all-step order-parameter means, and endpoint-complete AUC.

## Command

```bash
python AIEF_1_4_Twindow_sensitivity_analysis_v4.py \
  runs/b57562a8ee77 \
  --bootstrap-seed 20260814 \
  --n-bootstrap 2000
```

Default output:

```text
<run_dir>/analysis/v4/<analysis_execution_id>/
```

Every execution gets a new immutable directory. There is no overwrite mode.

## Recovery data model

Analysis v4 separates concepts that Analysis v3 combined under `horizon_system`.

### Target definitions

Density has one horizon-independent target:

```text
density_90pct_continue_final
```

Similarity has two target definitions:

```text
similarity_90pct_continue_late_fixed_physical
similarity_90pct_continue_late_normalized_EMA
```

### Observation support

All recovery searches and AUCs use the actual saved support:

```text
0.01, 0.51, ..., 319.51
```

They are not described as complete `[0,320]` observations.

### Undefined cosine

Raw similarity remains unchanged and may contain NaN for an undefined zero-vector cosine. A derived recovery representation converts NaN to zero and uses that same representation consistently for:

- first crossing;
- sustained-through-last-saved-observation;
- held recovery;
- recovery AUC.

The number of imputed samples is recorded.

### Event types

```text
first_crossing
sustained_through_last_saved_observation
held
```

Event times are saved-grid times and are interval-censored at diagnostic resolution. Event interval bounds are included.

### Held recovery

The timestamp condition is:

```python
times[j] - times[i] >= duration
```

Two hold-duration systems are reported:

```text
fixed_physical_17p5
one_current_Twindow_nominal
```

The nominal and effective discretized T-window values and their rounding difference are recorded separately.

### AUC

AUC is stored once per metric and condition, not duplicated under target systems:

```text
one-sided deficit versus same-condition continue
over saved support [0.01,319.51]
```

## Recovery estimand hierarchy

### Full-cohort outcomes

All 40 seeds contribute to:

- restricted event time;
- restricted event time divided by nominal T-window;
- event-observed indicator;
- AUC deficit;
- interactions/DIDs of those quantities.

Unobserved event times are restricted to the final saved time, 319.51.

### Conditional secondary outcomes

Raw event-time interactions require all four cells to be observed:

```text
rho branch
rho continue
baseline branch
baseline continue
```

These are explicitly labelled four-cell complete-case outcomes. Summaries include:

- complete-case n;
- included fraction of 40 seeds;
- SHA-256 of the included ordered seed set.

## Bootstrap design

The same seed-index draw matrix is reused across all groups and outcomes.

- Pointwise intervals: percentile-bootstrap 95% intervals.
- Primary fixed-physical regime and branch-DID families: simultaneous max-t 95% bands.
- Secondary normalized-EMA regime and branch-DID families: separately identified simultaneous max-t bands.
- Cross-T topology: simultaneous max-t family.
- Recovery intervals: pointwise, with complete-case support reported explicitly.

The bootstrap seed, iteration count, and draw-matrix SHA-256 are recorded.

## Transactional output

Analysis writes every file into a staging directory, reopens all CSVs, validates headers and row counts, rechecks hashes, writes the analysis manifest last, fsyncs, and atomically promotes the complete directory.

A failed attempt is retained under:

```text
analysis/v4/failed_<analysis_execution_id>/
```

A prior completed analysis is never deleted or replaced.

## Main outputs

```text
twindow_paired_regime_contrasts_v4.csv
twindow_branch_interactions_v4.csv
twindow_cross_condition_topology_v4.csv
twindow_recovery_events_by_seed_v4.csv
twindow_recovery_auc_by_seed_v4.csv
twindow_recovery_event_interactions_v4.csv
twindow_recovery_auc_interactions_v4.csv
twindow_regime_summary_v4.csv
twindow_branch_DID_summary_v4.csv
twindow_topology_summary_v4.csv
twindow_recovery_event_summary_v4.csv
twindow_recovery_auc_summary_v4.csv
twindow_recovery_event_interaction_summary_v4.csv
twindow_recovery_auc_interaction_summary_v4.csv
twindow_sensitivity_report_v4.txt
analysis_manifest.json
```

## Expected raw-row counts

```text
ordinary regime contrasts:     960 combined fixed + normalized rows
ordinary branch DIDs:         2880 combined fixed + normalized rows
cross-T topology:              160 rows
recovery events:              9600 rows
recovery AUC:                 1600 rows
recovery event interactions:  5760 rows
recovery AUC interactions:     960 rows
```

## Remaining limitations

Analysis v4 cannot infer information that was never saved:

- intervention-time t=0 trajectory values;
- terminal t=320 trajectory values;
- exact step-level crossing times;
- exact continuous-time crossing times;
- endpoint-complete AUC;
- all-step order-parameter averages.

These limitations must not be hidden by interpolation or silent endpoint assumptions.
