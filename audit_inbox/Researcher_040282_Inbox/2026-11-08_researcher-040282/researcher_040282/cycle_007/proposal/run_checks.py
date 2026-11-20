"""Run preregistered007 red/green/-O comparison contracts and eight mutants.

Source/child setup errors are blockers, never successful red evidence. No real
trajectory, frozen-run validation, installation or authority-file edit occurs.
"""
import argparse
from collections import Counter
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import numpy as np

from comparison_contract import Case, ContractMismatch, cases, checked
from load_reviewed import load_target, verify
from test_comparison_contract import make_suite

HERE = Path(__file__).resolve().parent
MODES = ('baseline', 'candidate-engine', 'candidate-leaf', 'modular-extracted')
EXPECTED_RED = {'test_missing_real', 'test_missing_imag', 'test_nan_positions', 'test_reduced_alphabet'}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def store(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def describe(value):
    a = np.asarray(value)
    return {'shape':list(a.shape), 'dtype':str(a.dtype), 'values_repr':repr(a.tolist())}


def census(target):
    selected = [case for case in cases() if case.group == 'reduced_alphabet']
    mismatches = []
    for case in selected:
        left, right = describe(case.left), describe(case.right)
        try:
            checked(target, case)
        except ContractMismatch as error:
            require(error.rule == 'truth_value', 'Unexpected nontruth census violation')
            mismatches.append({'case':case.name, 'expected':error.expected, 'observed':error.observed,
                               'left':left, 'right':right})
    summary = {'ordered_pairs':len(selected), 'mismatches':len(mismatches),
               'false_accepts':sum(not row['expected'] and row['observed'] for row in mismatches),
               'false_rejects':sum(row['expected'] and not row['observed'] for row in mismatches)}
    return summary, mismatches


def mutant_check(source):
    fixed, _ = load_target(source, 'candidate-engine')
    original, _ = load_target(source, 'baseline')
    def real_only(a, b):
        return fixed(np.asarray(a).real, np.asarray(b).real)
    def imag_only(a, b):
        return fixed(np.asarray(a).imag, np.asarray(b).imag)
    def approximate(a, b):
        a, b = np.asarray(a), np.asarray(b)
        return a.shape == b.shape and a.dtype == b.dtype and bool(np.allclose(a, b, rtol=1e-5, atol=1e-8, equal_nan=True))
    def ignore_dtype(a, b):
        return fixed(np.asarray(a, dtype=np.complex128), np.asarray(b, dtype=np.complex128))
    def ignore_shape(a, b):
        return fixed(np.asarray(a).reshape(-1), np.asarray(b).reshape(-1))
    def never_match_nan(a, b):
        return bool(np.array_equal(a, b))
    def mutate_input(a, b):
        a[...] = b
        return fixed(a, b)
    def pair(name, a, b):
        return Case('mutant_witness', name, a, b)
    def z(r, i):
        return np.array([complex(r, i)], dtype=np.complex128)
    mutants = [
        ('whole_complex_missingness', original, pair('missing_real_masks_finite_imag', z(math.nan, 1), z(math.nan, 99)), 'truth_value'),
        ('real_only', real_only, pair('imag_changes', z(1, 1), z(1, 2)), 'truth_value'),
        ('imaginary_only', imag_only, pair('real_changes', z(1, 1), z(2, 1)), 'truth_value'),
        ('approximate_equality', approximate, pair('one_ulp_not_equal', np.array([1.]), np.nextafter(np.array([1.]), np.array([2.]))), 'truth_value'),
        ('ignore_dtype', ignore_dtype, pair('int32_vs_int64', np.array([1], dtype=np.int32), np.array([1], dtype=np.int64)), 'truth_value'),
        ('ignore_shape', ignore_shape, pair('matrix_vs_flat', np.arange(6).reshape(2, 3), np.arange(6)), 'truth_value'),
        ('never_match_nan', never_match_nan, pair('matching_float_nan', np.array([math.nan]), np.array([math.nan])), 'truth_value'),
        ('mutate_requested_input', mutate_input, pair('precall_original_inputs', np.array([1., 2.]), np.array([3., 4.])), 'input_preservation'),
    ]
    records = []
    for label, target, case, intended in mutants:
        before = {'left':describe(case.left), 'right':describe(case.right)}
        try:
            checked(target, case)
        except ContractMismatch as error:
            require(error.rule == intended, 'Wrong rejection reason for mutant ' + label)
            records.append({'mutant':label, 'detected':True, 'reason':error.rule,
                            'expected':error.expected, 'observed':error.observed, 'precall_input':before})
        else:
            raise RuntimeError('Undetected controlled mutant: ' + label)
    require(len(records) ==8, 'Mutant inventory incomplete')
    verify(source)
    return records


def child(args):
    args.output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    if args.child == 'mutants':
        records = mutant_check(args.source)
        value = {'mode':'mutants', 'mutants_detected':len(records), 'setup_errors_credited_as_detections':0,
                 'records':records, 'optimized_python':not __debug__, 'verified_source_files_unchanged':len(verify(args.source)['modules']),
                 'elapsed_seconds':time.perf_counter() - start}
        store(args.output / 'result.json', value)
        print(json.dumps(value, indent=2))
        return 0
    target, boundary = load_target(args.source, args.child)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(make_suite(target))
    print(stream.getvalue(), end='')
    summary, mismatches = census(target)
    store(args.output / 'reduced_alphabet_mismatches.json', mismatches)
    failure_names = [test.id().split('.')[-1] for test, _ in result.failures]
    error_names = [test.id().split('.')[-1] for test, _ in result.errors]
    records = {'mode':args.child, 'optimized_python':not __debug__,
               'tests_run':result.testsRun, 'failures':len(result.failures), 'errors':len(result.errors),
               'skipped':len(result.skipped), 'failure_methods':sorted(failure_names), 'error_methods':sorted(error_names),
               'reduced_alphabet':summary, 'fixture_group_counts':dict(Counter(case.group for case in cases())),
               'source_boundary':boundary,
               'verified_source_files_unchanged':len(verify(args.source)['modules']),
               'elapsed_seconds':time.perf_counter() - start}
    store(args.output / 'result.json', records)
    print(json.dumps(records, indent=2))
    return 0 if result.wasSuccessful() else 1


def parent(args):
    args.output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    manifest = verify(args.source)
    runs = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    environment.pop('PYTHONOPTIMIZE', None)
    modes = MODES + ('mutants',)
    for mode in modes:
        for optimized in (False, True):
            name = mode + ('_optimized' if optimized else '_normal')
            directory = args.output / name
            command = [sys.executable] + (['-O'] if optimized else []) + ['-B', str(Path(__file__).resolve()),
                       '--child', mode, '--source', str(args.source.resolve()), '--output', str(directory.resolve())]
            completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, env=environment, timeout=90)
            (args.output / (name + '.log')).write_text(completed.stdout)
            require((directory / 'result.json').is_file(), 'Child setup/run failed before result: ' + name)
            result = json.loads((directory / 'result.json').read_text())
            require(result['optimized_python'] is optimized and result['verified_source_files_unchanged'] ==2,
                    'Optimization/source-preservation record mismatch')
            if mode == 'mutants':
                require(completed.returncode ==0 and result['mutants_detected'] ==8 and
                        result['setup_errors_credited_as_detections'] ==0, 'Mutant sensitivity incomplete')
            elif mode == 'baseline':
                require(completed.returncode ==1 and result['tests_run'] ==11 and result['failures'] ==4 and
                        set(result['failure_methods']) == EXPECTED_RED and result['errors'] ==0 and result['skipped'] ==0,
                        'Original did not fail exactly the preregistered semantic contracts; stop/reassess')
                require(result['reduced_alphabet'] == {'ordered_pairs':2592, 'mismatches':220, 'false_accepts':220, 'false_rejects':0},
                        'Original finite census differs from preregistration')
            else:
                require(completed.returncode ==0 and result['tests_run'] ==11 and result['failures'] ==0 and
                        result['errors'] ==0 and result['skipped'] ==0 and result['reduced_alphabet']['mismatches'] ==0,
                        'Candidate/crosscheck not conforming')
            result['observed_returncode'] = completed.returncode
            runs.append(result)
            print(name, 'rc=' + str(completed.returncode), 'science checked', flush=True)
    for mode in modes:
        pair = [record for record in runs if record['mode'] ==mode]
        ignored = {'elapsed_seconds', 'optimized_python'}
        require({k:v for k,v in pair[0].items() if k not in ignored} ==
                {k:v for k,v in pair[1].items() if k not in ignored}, 'Normal/-O result mismatch: ' + mode)
    unchanged = len(verify(args.source)['modules'])
    store(args.output / 'target_runs.json', runs)
    science = {'tested_main':manifest['commit'], 'target_contract_tests':11,
               'baseline_tests':{'failures':4, 'errors':0, 'same_under_optimization':True},
               'candidate_engine_tests':{'pass':11, 'same_under_optimization':True},
               'candidate_leaf_tests':{'pass':11, 'same_under_optimization':True},
               'modular_ast_extracted_tests':{'pass':11, 'same_under_optimization':True},
               'reduced_alphabet_ordered_pairs_each_target':2592,
               'baseline_false_accepts':220, 'baseline_false_rejects':0,
               'candidate_engine_leaf_modular_mismatches':[0,0,0],
               'mutants_detected_normal':8, 'mutants_detected_optimized':8,
               'verified_public_source_files_unchanged':unchanged,
               'no_frozen_source_edit_or_authority_certificate':True,
               'no_real_data_or_simulation_or_new_lean':True,
               'all_preregistered_acceptance_conditions_met':True}
    store(args.output / 'science_summary.json', science)
    record = {'science':science, 'python':sys.version, 'numpy':np.__version__,
              'elapsed_seconds':time.perf_counter() - start,
              'source_execution_scope':'Full engine import only; replacement of ONE comparison AST node for memory-only candidate; existing modular helper only AST-extracted. No engine dynamics/certification call.',
              'proposal_status':'LOCAL_NEW_FILE_PROPOSAL;NOT_INSTALLED_OR_AUTHORITY_APPROVED;NO_INDEPENDENT_REVIEW'}
    store(args.output / 'cycle_results.json', record)
    print(json.dumps(record, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--child', choices=MODES + ('mutants',))
    args = parser.parse_args()
    try:
        return child(args) if args.child else parent(args)
    except Exception as error:
        args.output.mkdir(parents=True, exist_ok=True)
        store(args.output / 'failure.json', {'type':type(error).__name__, 'message':str(error),
                                           'counts_as_semantic_rejection':False})
        raise


if __name__ == '__main__':
    raise SystemExit(main())
