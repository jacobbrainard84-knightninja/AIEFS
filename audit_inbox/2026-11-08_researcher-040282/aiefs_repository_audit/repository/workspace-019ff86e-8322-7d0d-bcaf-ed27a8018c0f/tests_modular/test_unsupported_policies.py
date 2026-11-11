from __future__ import annotations

import dataclasses

import pytest

from aief_modular.factors import validate_factor_compatibility
from aief_modular.runner import execute
from aief_modular.validation import UnsupportedPolicyError


def test_unknown_factor_resolver_fails(small_spec):
    axis = dataclasses.replace(small_spec.model_axes[0], resolver_id="engine_v1.arbitrary_noise")
    with pytest.raises(UnsupportedPolicyError, match="not implemented"):
        validate_factor_compatibility(axis)


def test_resume_fails_before_execution():
    with pytest.raises(UnsupportedPolicyError, match="Resume is not implemented"):
        execute(
            None,  # not reached
            mode="production",
            frozen_manifest="x",
            frozen_npz="y",
            frozen_scalar="z",
            output_root="out",
            resume=True,
        )
