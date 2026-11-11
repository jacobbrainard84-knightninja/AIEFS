from __future__ import annotations

import pytest

from aief_modular.registry import StudyRegistry


def test_duplicate_id_is_fatal(small_spec):
    registry = StudyRegistry()
    builder = lambda: small_spec
    registry.register("X", builder, slug="one", version="v1", title="One")
    with pytest.raises(RuntimeError, match="Duplicate study ID"):
        registry.register("X", builder, slug="two", version="v1", title="Two")


def test_duplicate_slug_is_fatal(small_spec):
    registry = StudyRegistry()
    builder = lambda: small_spec
    registry.register("X", builder, slug="one", version="v1", title="One")
    with pytest.raises(RuntimeError, match="Duplicate study slug"):
        registry.register("Y", builder, slug="one", version="v1", title="Two")


def test_listing_is_deterministic(small_spec):
    registry = StudyRegistry()
    registry.register("Z", lambda: small_spec, slug="z", version="v1", title="Z")
    registry.register("A", lambda: small_spec, slug="a", version="v1", title="A")
    assert registry.ids() == ("A", "Z")
