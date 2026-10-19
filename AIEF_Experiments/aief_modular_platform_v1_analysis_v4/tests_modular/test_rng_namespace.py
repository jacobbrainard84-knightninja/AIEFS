from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from aief_modular.branches import (
    FROZEN_ENGINE_V1_NAMESPACE,
    branch_rng_child_index,
    make_branch_rngs,
    validate_branch_compatibility,
)
from aief_modular.validation import SpecValidationError


class FakeEngine:
    @staticmethod
    def make_branch_rngs(seed, branch_order):
        root = np.random.SeedSequence(seed)
        _, branch_root = root.spawn(2)
        sequences = branch_root.spawn(len(branch_order))
        return {
            branch: np.random.default_rng(int(sequence.generate_state(1, dtype=np.uint64)[0]))
            for branch, sequence in zip(branch_order, sequences)
        }


def test_future_shuffle_keeps_seventh_child(small_spec):
    assert branch_rng_child_index(small_spec, "future_shuffle") == 6
    actual = make_branch_rngs(FakeEngine, 1234, FROZEN_ENGINE_V1_NAMESPACE)

    root = np.random.SeedSequence(1234)
    _, branch_root = root.spawn(2)
    seventh = branch_root.spawn(7)[6]
    expected = np.random.default_rng(int(seventh.generate_state(1, dtype=np.uint64)[0]))
    np.testing.assert_array_equal(
        actual["future_shuffle"].integers(0, 2**32, size=10, dtype=np.uint64),
        expected.integers(0, 2**32, size=10, dtype=np.uint64),
    )


def test_requires_rng_is_part_of_branch_contract(small_spec):
    wrong = dataclasses.replace(
        small_spec,
        branches=(
            small_spec.branches[0],
            dataclasses.replace(small_spec.branches[1], requires_rng=False),
        ),
    )
    with pytest.raises(SpecValidationError, match="requires_rng"):
        validate_branch_compatibility(wrong)
