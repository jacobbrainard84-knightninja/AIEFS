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
