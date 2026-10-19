from __future__ import annotations

import json

from aief_modular.artifacts import atomic_write_json, execution_paths, make_execution_id
from aief_modular.runner import _initial_manifest
from aief_modular.spec import scientific_run_sha256, spec_sha256


def test_execution_modes_have_distinct_leaf_paths(tmp_path, small_spec):
    baseline_id = make_execution_id("baseline")
    production_id = make_execution_id("production")
    assert baseline_id != production_id
    baseline = execution_paths(tmp_path, small_spec, "0123456789abcdef", "baseline", baseline_id)
    production = execution_paths(tmp_path, small_spec, "0123456789abcdef", "production", production_id)
    assert baseline.leaf != production.leaf
    assert "/baseline/" in baseline.leaf.as_posix()
    assert "/production/" in production.leaf.as_posix()
    assert baseline.scalar_csv.parent == baseline.leaf


def test_initial_manifest_is_strict_json_serializable(tmp_path, small_spec):
    source_hashes = {
        "engine": "a" * 64,
        "runner": "b" * 64,
        "study": "c" * 64,
    }
    scientific_hash = scientific_run_sha256(small_spec, source_hashes)
    execution_id = "production_20260814T120000Z_abcdef12"
    paths = execution_paths(
        tmp_path, small_spec, scientific_hash[:16], "production", execution_id
    )
    manifest = _initial_manifest(
        spec=small_spec,
        spec_hash=spec_sha256(small_spec),
        scientific_hash=scientific_hash,
        run_id=scientific_hash[:16],
        execution_id=execution_id,
        execution_mode="production",
        source_hashes=source_hashes,
        paths=paths,
    )
    paths.leaf.mkdir(parents=True)
    atomic_write_json(paths.manifest, manifest)
    observed = json.loads(paths.manifest.read_text())
    assert observed["artifact_authority"]["lock_scope"] == "execution_id_not_run_id"
    assert observed["analysis_contract"] == {}
