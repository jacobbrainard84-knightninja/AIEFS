from __future__ import annotations

from aief_modular.artifacts import execution_paths, make_execution_id


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
