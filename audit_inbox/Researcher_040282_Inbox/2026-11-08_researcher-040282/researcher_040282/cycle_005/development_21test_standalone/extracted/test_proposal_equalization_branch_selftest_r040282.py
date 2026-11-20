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
