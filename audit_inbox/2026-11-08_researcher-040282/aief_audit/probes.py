"""Deterministic numerical witnesses; no actual S01 observations are used."""
from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

from audit_support import load_analysis


def collect():
    m = load_analysis()
    t = m.EXPECTED_SAMPLE_TIMES
    holds = []
    for duration in (8.75, 13.125, 17.5, 26.25, 35.):
        intervals = int(np.ceil(duration / .5))
        misses = []
        for start in range(len(t) - intervals):
            end = start + intervals
            c = np.zeros(len(t), bool)
            c[start:end+1] = True
            got = m._held_index(t, c, duration)
            if got != start:
                misses.append({
                    'start_index': start, 'end_index': end,
                    'start_time': float(t[start]), 'end_time': float(t[end]),
                    'addition_used_for_search': float(t[start] + duration),
                    'timestamp_subtraction': float(t[end] - t[start]),
                    'returned_index': got,
                })
        holds.append({
            'duration': duration, 'true_block_span': .5 * intervals,
            'eligible_start_positions_tested': len(t) - intervals,
            'false_negative_count': len(misses), 'first_examples': misses[:3],
        })
    c = np.zeros(len(t), bool)
    c[32:68] = True
    c[100:151] = True
    later = m._held_index(t, c, 17.5)

    seeds = tuple(str(i) for i in range(40))
    draws = m.bootstrap_draws(seeds, 2000, 41)
    rate_results = []
    for constant in (0., 1.):
        f = pd.DataFrame({'seed': seeds, 'group': 'one', 'value': constant})
        row = m.pointwise_summary(f, group_columns=('group',), value_column='value',
                                  seeds=seeds, draws=draws).iloc[0]
        rate_results.append({
            'events': int(constant * 40), 'n': 40,
            'bootstrap_ci': [row.pointwise_ci_lower, row.pointwise_ci_upper],
        })
    cc = pd.DataFrame({'seed': seeds, 'group': 'one', 'value': [7.] + [np.nan] * 39})
    row = m.pointwise_summary(cc, group_columns=('group',), value_column='value',
                              seeds=seeds, draws=draws).iloc[0]
    no_case_draws = int(np.sum(np.isfinite(cc.value.to_numpy()[draws]).sum(axis=1) == 0))

    tstar = 17.333
    before = [rho * tstar for rho in m.EXPECTED_RHO_VALUES]
    after = pd.read_csv(StringIO(pd.DataFrame({'T_window': before}).to_csv(index=False))).T_window
    roundtrip_mismatches = [{
        'rho': rho, 'expected_float_repr': repr(x), 'parsed_float_repr': repr(float(y)),
    } for rho, x, y in zip(m.EXPECTED_RHO_VALUES, before, after) if x != y]

    small = np.ones((12, 12)) * .1
    np.fill_diagonal(small, 0)
    return {
        'evidence_scope': 'SYNTHETIC/deterministic function probes; no raw S01 run and no real aief_modular package',
        'hold_grid_sweep': holds,
        'delayed_held_event': {
            'expected_index': 32, 'expected_time': float(t[32]),
            'actual_index': later, 'actual_time': float(t[later]),
        },
        'event_rate_intervals': rate_results,
        'exact_binomial_95pct_interval_0_of_40': [0., 1. - .025**(1/40)],
        'coverage_counterexample': {
            'hypothetical_population_event_probability': .01,
            'probability_all_40_events_zero': .99**40,
            'maximum_coverage_given_zero_width_at_all_zero': 1 - .99**40,
        },
        'one_complete_case': {
            'n': int(row.n), 'mean': row['mean'],
            'bootstrap_ci': [row.pointwise_ci_lower, row.pointwise_ci_upper],
            'bootstrap_draws_without_any_complete_case': no_case_draws,
            'bootstrap_iterations': len(draws),
            'theoretical_zero_case_draw_probability': (39/40)**40,
        },
        'nominal_window_csv_roundtrip': {'test_T_star': tstar, 'mismatches': roundtrip_mismatches},
        'all_below_threshold_but_nonzero_topologies': {
            'cosine': m.cosine_edges(small, small),
            'normalized_distance': m.normalized_distance(small, small),
            'Jaccard_is_NaN': bool(np.isnan(m.jaccard_edges(small, small, .2))),
        },
        'physical_crossing_nonidentifiability': {
            'saved_times': [.01, .51, 1.01], 'saved_values_both_paths': [0., 0., 1.],
            'same_reported_adjacent_interval': [.51, 1.01],
            'possible_step_level_first_crossings': [.11, .76],
            'interpretation': 'The interval does not identify the first physical crossing without path restrictions; the saved-grid detection time is exactly 1.01.',
        },
        'hold_onset_observability': {
            'duration': 17.5, 'last_fully_confirmable_saved_onset': 302.01,
            'example_true_run_starts': 310.01, 'support_end': m.SUPPORT_END,
            'code_records_event_observed': False, 'code_records_restricted_time': m.SUPPORT_END,
            'interpretation': 'Coherent as a finite-grid capped score, not as usual physical-onset censoring at support_end.',
        },
    }


if __name__ == '__main__':
    result = collect()
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    Path(__file__).with_name('probe_results.json').write_text(text)
    print(text)
