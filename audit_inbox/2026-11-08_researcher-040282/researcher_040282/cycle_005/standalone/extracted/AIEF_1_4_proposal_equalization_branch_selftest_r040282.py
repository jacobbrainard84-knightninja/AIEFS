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
