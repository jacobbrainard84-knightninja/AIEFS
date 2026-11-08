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
        require(result['returncode'] == 0 and result['success'] and result['tests_run'] == 21
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
