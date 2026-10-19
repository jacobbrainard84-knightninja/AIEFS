from __future__ import annotations

import dataclasses

import pytest

from aief_modular.spec import (
    FrozenDict,
    canonical_json,
    scientific_run_sha256,
    spec_sha256,
)


def test_canonical_serialization_is_deterministic(small_spec):
    first = canonical_json(small_spec)
    second = canonical_json(small_spec)
    assert first == second
    assert spec_sha256(small_spec) == spec_sha256(small_spec)
    assert "NaN" not in first
    assert "Infinity" not in first


def test_scientific_identity_does_not_depend_on_output_path(small_spec):
    hashes = {"engine": "a" * 64, "runner": "b" * 64, "study": "c" * 64}
    identity_a = scientific_run_sha256(small_spec, hashes)
    identity_b = scientific_run_sha256(small_spec, dict(reversed(list(hashes.items()))))
    assert identity_a == identity_b
    # No output root is accepted by the identity function at all.
    assert "/tmp" not in canonical_json(small_spec)


def test_frozen_mapping_rejects_key_coercion_and_sets():
    with pytest.raises(TypeError, match="key must be str"):
        FrozenDict({1: "a"})
    with pytest.raises(TypeError, match="Sets are not permitted"):
        FrozenDict({"bad": {1, 2}})


def test_spec_rejects_unsafe_path_components(small_spec):
    with pytest.raises(ValueError, match="Unsafe study_version"):
        dataclasses.replace(small_spec, study_version="../v1")
