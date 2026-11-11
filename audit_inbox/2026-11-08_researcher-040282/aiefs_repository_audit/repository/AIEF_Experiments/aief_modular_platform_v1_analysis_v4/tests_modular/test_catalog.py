from __future__ import annotations

import json

import pytest

from aief_modular.catalog import rebuild_catalog
from aief_modular.validation import CatalogError


def test_catalog_rebuild_and_explicit_replace(tmp_path):
    run_id = "0123456789abcdef"
    execution_id = "production_20260814T120000Z_abcdef12"
    leaf = tmp_path / "S_slug" / "v1" / run_id / "production" / execution_id
    leaf.mkdir(parents=True)
    manifest = {
        "study_id": "S",
        "study_slug": "slug",
        "study_version": "v1",
        "run_id": run_id,
        "spec_sha256": "f" * 64,
        "execution_id": execution_id,
        "execution_mode": "production",
        "created_utc": "2026-08-13T00:00:00Z",
        "status": "completed",
        "freezeable": True,
        "source_hashes": {"engine": "a" * 64, "runner": "b" * 64},
        "study": {"n_seeds": 40},
        "completion": {"n_conditions_requested": 200},
    }
    (leaf / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    csv_path, json_path = rebuild_catalog(tmp_path)
    assert csv_path.exists() and json_path.exists()
    catalog = json.loads(json_path.read_text())
    assert catalog["authority"] == "derived_non_authoritative"
    assert catalog["entries"][0]["path"] == leaf.relative_to(tmp_path).as_posix()
    with pytest.raises(CatalogError, match="already exists"):
        rebuild_catalog(tmp_path)
    rebuild_catalog(tmp_path, replace=True)


def test_catalog_marks_parseable_wrong_types_as_malformed(tmp_path):
    run_id = "0123456789abcdef"
    execution_id = "production_20260814T120000Z_abcdef12"
    leaf = tmp_path / "S_slug" / "v1" / run_id / "production" / execution_id
    leaf.mkdir(parents=True)
    manifest = {
        "study_id": "S",
        "study_slug": "slug",
        "study_version": "v1",
        "run_id": run_id,
        "spec_sha256": "f" * 64,
        "execution_id": execution_id,
        "execution_mode": "production",
        "created_utc": "2026-08-14T12:00:00Z",
        "status": "completed",
        "freezeable": "false",
        "source_hashes": {"engine": "a" * 64, "runner": "b" * 64},
        "study": {"n_seeds": 40},
        "completion": {"n_conditions_requested": 200},
    }
    (leaf / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    _csv, json_path = rebuild_catalog(tmp_path)
    catalog = json.loads(json_path.read_text())
    assert catalog["malformed_count"] == 1
    assert catalog["entries"][0]["status"] == "malformed"
    assert "freezeable" in catalog["entries"][0]["malformed_error"]
