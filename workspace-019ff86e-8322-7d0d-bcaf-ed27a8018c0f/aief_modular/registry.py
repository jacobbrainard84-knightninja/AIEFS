"""Explicit, deterministic registry for trusted built-in AIEF studies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .spec import ExperimentSpec


StudyBuilder = Callable[[], ExperimentSpec]


@dataclass(frozen=True)
class StudyRegistration:
    study_id: str
    slug: str
    version: str
    title: str
    source_module: str
    builder: StudyBuilder

    def build(self) -> ExperimentSpec:
        spec = self.builder()
        expected = (self.study_id, self.slug, self.version, self.title)
        observed = (spec.study_id, spec.study_slug, spec.study_version, spec.title)
        if observed != expected:
            raise RuntimeError(
                "Registered study metadata differs from built specification: "
                f"registered={expected!r}, built={observed!r}"
            )
        return spec


class StudyRegistry:
    """Registry that rejects duplicate IDs and slugs."""

    def __init__(self) -> None:
        self._by_id: dict[str, StudyRegistration] = {}
        self._slug_to_id: dict[str, str] = {}

    def register(
        self,
        study_id: str,
        builder: StudyBuilder,
        *,
        slug: str,
        version: str,
        title: str,
        source_module: str | None = None,
    ) -> StudyRegistration:
        if study_id in self._by_id:
            raise RuntimeError(f"Duplicate study ID: {study_id}")
        if slug in self._slug_to_id:
            raise RuntimeError(
                f"Duplicate study slug {slug!r}: already registered by {self._slug_to_id[slug]}"
            )
        registration = StudyRegistration(
            study_id=study_id,
            slug=slug,
            version=version,
            title=title,
            source_module=source_module or builder.__module__,
            builder=builder,
        )
        self._by_id[study_id] = registration
        self._slug_to_id[slug] = study_id
        return registration

    def get(self, study_id: str) -> StudyRegistration:
        try:
            return self._by_id[study_id]
        except KeyError as exc:
            available = ", ".join(self.ids()) or "<none>"
            raise KeyError(f"Unknown study {study_id!r}; available: {available}") from exc

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_id))

    def entries(self) -> tuple[StudyRegistration, ...]:
        return tuple(self._by_id[key] for key in self.ids())

    def clear_for_testing(self) -> None:
        self._by_id.clear()
        self._slug_to_id.clear()


REGISTRY = StudyRegistry()


def register_study(
    study_id: str,
    builder: StudyBuilder,
    *,
    slug: str,
    version: str,
    title: str,
    source_module: str | None = None,
) -> StudyRegistration:
    return REGISTRY.register(
        study_id,
        builder,
        slug=slug,
        version=version,
        title=title,
        source_module=source_module,
    )


def load_builtin_studies() -> None:
    """Import only trusted package-owned study modules.

    No path-based dynamic loading is supported.
    """
    from .studies import aief_1_4_s01_twindow as _twindow  # noqa: F401
