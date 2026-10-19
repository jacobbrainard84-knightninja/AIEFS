from __future__ import annotations

import csv
import json

import numpy as np
import pytest

from aief_modular.artifacts import atomic_write_csv, atomic_write_json, atomic_write_npz, load_npz
from aief_modular.validation import ArtifactIntegrityError


def test_atomic_artifact_round_trips(tmp_path):
    json_path = tmp_path / "x.json"
    csv_path = tmp_path / "x.csv"
    npz_path = tmp_path / "x.npz"

    atomic_write_json(json_path, {"b": 2, "a": 1})
    assert json.loads(json_path.read_text()) == {"a": 1, "b": 2}

    atomic_write_csv(csv_path, [{"x": 1, "y": "a"}], ("x", "y"))
    with open(csv_path, newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == [{"x": "1", "y": "a"}]

    value = np.arange(12, dtype=np.float64).reshape(3, 4)
    atomic_write_npz(npz_path, {"value": value, "scalar": 1.25})
    observed = load_npz(npz_path)
    np.testing.assert_array_equal(observed["value"], value)
    assert observed["scalar"] == 1.25
    assert not list(tmp_path.glob("*.tmp*"))


def test_strict_json_rejects_nonfinite_and_unsupported_values(tmp_path):
    with pytest.raises(ArtifactIntegrityError, match="Non-finite"):
        atomic_write_json(tmp_path / "nan.json", {"value": float("nan")})
    with pytest.raises(ArtifactIntegrityError, match="Unsupported"):
        atomic_write_json(tmp_path / "set.json", {"value": {1, 2}})
    with pytest.raises(ArtifactIntegrityError, match="key must be str"):
        atomic_write_json(tmp_path / "key.json", {1: "bad"})


def test_csv_rejects_missing_extra_and_duplicate_schema(tmp_path):
    with pytest.raises(ArtifactIntegrityError, match="missing"):
        atomic_write_csv(tmp_path / "missing.csv", [{"x": 1}], ("x", "y"))
    with pytest.raises(ArtifactIntegrityError, match="extra"):
        atomic_write_csv(tmp_path / "extra.csv", [{"x": 1, "y": 2}], ("x",))
    with pytest.raises(ArtifactIntegrityError, match="unique"):
        atomic_write_csv(tmp_path / "duplicate.csv", [{"x": 1}], ("x", "x"))
