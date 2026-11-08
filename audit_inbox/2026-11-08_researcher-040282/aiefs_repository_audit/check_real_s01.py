"""Execute actual checked-in analysis against actual checked-in raw S01 inputs.

No engine trajectories are regenerated here. Audit outputs go outside the
repository snapshot. An independent grid-span oracle characterizes the held
classification bug's actual incidence without modifying the analysis source.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO = Path(os.environ.get('AIEFS_AUDIT_REPO', ROOT / 'repository')).resolve()
PKG = REPO / 'AIEF_Experiments/aief_modular_platform_v1_analysis_v4'
sys.path[:0] = [str(PKG), str(REPO)]
import AIEF_1_4_Twindow_sensitivity_analysis_v4 as a


def held_oracle(condition, duration):
    padded = np.r_[False, condition, False].astype(np.int8)
    changes = np.diff(padded)
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1) - 1
    for start, end in zip(starts, ends, strict=True):
        if .5 * int(end - start) >= duration:
            return int(start)
    return None


def main():
    raw = REPO / 'runs/b57562a8ee77'
    run = a.validate_run(a.discover_inputs(raw))
    final = a.run_analysis(raw, output_root=ROOT / 'evidence/real_s01_analysis',
                           bootstrap_seed=20260814, n_bootstrap=2000,
                           command_line='Arena read-only branch audit; actual S01 reanalysis')
    events = pd.read_csv(final / 'twindow_recovery_events_by_seed_v4.csv', dtype={'seed': str})
    event_summary = pd.read_csv(final / 'twindow_recovery_event_summary_v4.csv')
    did_summary = pd.read_csv(final / 'twindow_recovery_event_interaction_summary_v4.csv')
    held = events.loc[events.event_type == 'held']
    mismatches = []
    with np.load(run.inputs.branch_npz, allow_pickle=False) as archive:
        for row in held.itertuples(index=False):
            field = 'density_trajectory' if row.metric == 'density' else 'similarity_trajectory'
            values = np.asarray(archive[a._npz_key(row.branch,row.seed,row.rho,field)],float)
            if row.metric == 'similarity':
                values = np.nan_to_num(values,nan=0.)
            # Use original full-precision target, not round-trip CSV target.
            scalar = run.scalar.loc[(run.scalar.seed == row.seed) & (run.scalar.rho == row.rho) & (run.scalar.branch == 'continue')].iloc[0]
            if row.metric == 'density':
                threshold = .9 * scalar.D_B_final
            elif row.target_definition.endswith('fixed_physical'):
                threshold = .9 * scalar.Weighted_similarity_late_fixed_physical
            else:
                threshold = .9 * scalar.Weighted_similarity_late_normalized_EMA
            t_window = float(scalar.T_window)
            duration = 17.5 if row.hold_duration_system == 'fixed_physical_17p5' else t_window
            condition = values >= threshold
            got = a._held_index(a.EXPECTED_SAMPLE_TIMES,condition,duration)
            expected = held_oracle(condition,duration)
            if got != expected:
                mismatches.append({'seed':row.seed,'rho':row.rho,'branch':row.branch,
                                   'target_definition':row.target_definition,
                                   'hold_duration_system':row.hold_duration_system,
                                   'actual_index':got,'oracle_index':expected})
    rates = event_summary.loc[event_summary.estimand == 'event_observed']
    conditional = did_summary.loc[did_summary.estimand == 'conditional_event_time_DID']
    summary = {
        'evidence_class':'actual checked-in S01 data; actual repository modules; no dependency stand-ins',
        'analysis_output_path':str(final.relative_to(ROOT)),
        'input_validation':'passed',
        'raw_trajectory_regeneration':False,
        'n_seeds':len(run.seeds),'scalar_rows':len(run.scalar),
        'event_rows':len(events),'held_rows_checked':len(held),
        'held_grid_oracle_mismatches':mismatches,
        'event_rate_groups':len(rates),
        'zero_event_groups':int((rates['mean'] == 0).sum()),
        'all_event_groups':int((rates['mean'] == 1).sum()),
        'zero_width_event_rate_intervals':int((rates.pointwise_ci_lower == rates.pointwise_ci_upper).sum()),
        'conditional_event_DID_groups':len(conditional),
        'conditional_event_DID_sample_counts':{str(int(k)):int(v) for k,v in conditional.n.value_counts().sort_index().items()},
        'zero_reference_event_rows':int((events.target_value == 0).sum()),
        'undefined_similarity_affected_event_rows':int((events.undefined_samples_imputed_zero > 0).sum()),
    }
    (ROOT / 'evidence/real_s01_execution.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
