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
