from __future__ import annotations

from aief_modular.registry import REGISTRY, load_builtin_studies


def test_builtin_study_lists_without_loading_engine():
    load_builtin_studies()
    entries = REGISTRY.entries()
    assert [entry.study_id for entry in entries] == ["AIEF_1_4_S01"]
    entry = entries[0]
    assert entry.slug == "twindow_sensitivity"
    assert entry.version == "v1"
