"""Independent frozen-authority lock loading and verification."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .artifacts import file_sha256
from .validation import ArtifactIntegrityError


AUTHORITY_SCHEMA = "aief-frozen-authority-lock-v1"
EXPECTED_ARTIFACT_KEYS = ("manifest", "branch_npz", "scalar_csv")
EXPECTED_SOURCE_KEYS = ("engine_v1", "twindow_driver_v1", "twindow_analysis_v3")


@dataclass(frozen=True)
class LockedFile:
    relative_path: str
    sha256: str


@dataclass(frozen=True)
class FrozenAuthorityLock:
    authority_schema: str
    authority_id: str
    seed_count: int
    branch_count: int
    ordered_branch_namespace: tuple[str, ...]
    frozen_artifacts: tuple[tuple[str, LockedFile], ...]
    legacy_sources: tuple[tuple[str, LockedFile], ...]

    def artifact(self, key: str) -> LockedFile:
        return dict(self.frozen_artifacts)[key]

    def source(self, key: str) -> LockedFile:
        return dict(self.legacy_sources)[key]


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ArtifactIntegrityError(f"Authority lock {label} must be a lowercase SHA-256")
    return value


def _relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ArtifactIntegrityError(f"Authority lock {label} path must be a nonempty string")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ArtifactIntegrityError(f"Authority lock {label} path is unsafe: {value!r}")
    return path.as_posix()


def _locked_files(
    value: Any,
    *,
    label: str,
    expected_keys: tuple[str, ...],
) -> tuple[tuple[str, LockedFile], ...]:
    if not isinstance(value, dict) or set(value) != set(expected_keys):
        raise ArtifactIntegrityError(
            f"Authority lock {label} keys {set(value) if isinstance(value, dict) else None!r} "
            f"!= {set(expected_keys)!r}"
        )
    result = []
    for key in expected_keys:
        entry = value[key]
        if not isinstance(entry, dict) or set(entry) != {"relative_path", "sha256"}:
            raise ArtifactIntegrityError(f"Authority lock {label}.{key} has invalid schema")
        result.append(
            (
                key,
                LockedFile(
                    relative_path=_relative_path(entry["relative_path"], f"{label}.{key}"),
                    sha256=_sha256(entry["sha256"], f"{label}.{key}.sha256"),
                ),
            )
        )
    return tuple(result)


def load_authority_lock(path: str | Path) -> tuple[FrozenAuthorityLock, str]:
    lock_path = Path(path)
    if not lock_path.is_file():
        raise ArtifactIntegrityError(f"Authority lock not found: {lock_path}")
    try:
        with open(lock_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:
        raise ArtifactIntegrityError(f"Cannot parse authority lock {lock_path}: {exc}") from exc
    required_root = {
        "authority_schema",
        "authority_id",
        "certification_design",
        "frozen_artifacts",
        "legacy_sources",
        "authentication_note",
    }
    if not isinstance(data, dict) or set(data) != required_root:
        raise ArtifactIntegrityError("Authority lock root schema is invalid")
    if data["authority_schema"] != AUTHORITY_SCHEMA:
        raise ArtifactIntegrityError(
            f"Unsupported authority schema: {data['authority_schema']!r}"
        )
    authority_id = data["authority_id"]
    if not isinstance(authority_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", authority_id):
        raise ArtifactIntegrityError("Authority lock authority_id is invalid")
    design = data["certification_design"]
    expected_design_keys = {"seed_count", "branch_count", "ordered_branch_namespace"}
    if not isinstance(design, dict) or set(design) != expected_design_keys:
        raise ArtifactIntegrityError("Authority lock certification_design schema is invalid")
    seed_count = design["seed_count"]
    branch_count = design["branch_count"]
    namespace = design["ordered_branch_namespace"]
    if isinstance(seed_count, bool) or not isinstance(seed_count, int) or seed_count <= 0:
        raise ArtifactIntegrityError("Authority lock seed_count must be a positive integer")
    if isinstance(branch_count, bool) or not isinstance(branch_count, int) or branch_count <= 0:
        raise ArtifactIntegrityError("Authority lock branch_count must be a positive integer")
    if (
        not isinstance(namespace, list)
        or len(namespace) != branch_count
        or len(set(namespace)) != branch_count
        or not all(isinstance(item, str) and item for item in namespace)
    ):
        raise ArtifactIntegrityError("Authority lock branch namespace is invalid")
    note = data["authentication_note"]
    if not isinstance(note, str) or not note:
        raise ArtifactIntegrityError("Authority lock authentication_note is invalid")

    lock = FrozenAuthorityLock(
        authority_schema=AUTHORITY_SCHEMA,
        authority_id=authority_id,
        seed_count=seed_count,
        branch_count=branch_count,
        ordered_branch_namespace=tuple(namespace),
        frozen_artifacts=_locked_files(
            data["frozen_artifacts"],
            label="frozen_artifacts",
            expected_keys=EXPECTED_ARTIFACT_KEYS,
        ),
        legacy_sources=_locked_files(
            data["legacy_sources"],
            label="legacy_sources",
            expected_keys=EXPECTED_SOURCE_KEYS,
        ),
    )
    return lock, file_sha256(lock_path)


def verify_authority_lock(
    lock: FrozenAuthorityLock,
    *,
    authority_root: str | Path,
    supplied_artifacts: Mapping[str, Path],
    runtime_engine_path: str | Path,
) -> dict[str, Any]:
    """Verify locked artifacts/sources against a project root and supplied inputs."""
    root = Path(authority_root).resolve()
    if not root.is_dir():
        raise ArtifactIntegrityError(f"Authority project root not found: {root}")
    expected_supplied = {"manifest", "npz", "scalar"}
    if set(supplied_artifacts) != expected_supplied:
        raise ArtifactIntegrityError(
            f"Supplied authority keys {set(supplied_artifacts)!r} != {expected_supplied!r}"
        )
    supplied_map = {
        "manifest": Path(supplied_artifacts["manifest"]).resolve(),
        "branch_npz": Path(supplied_artifacts["npz"]).resolve(),
        "scalar_csv": Path(supplied_artifacts["scalar"]).resolve(),
    }

    verified_artifacts: dict[str, dict[str, str]] = {}
    for key, entry in lock.frozen_artifacts:
        expected_path = (root / entry.relative_path).resolve()
        supplied_path = supplied_map[key]
        if supplied_path != expected_path:
            raise ArtifactIntegrityError(
                f"Supplied {key} path {supplied_path} != locked path {expected_path}"
            )
        if not expected_path.is_file():
            raise ArtifactIntegrityError(f"Locked authority artifact missing: {expected_path}")
        observed = file_sha256(expected_path)
        if observed != entry.sha256:
            raise ArtifactIntegrityError(
                f"Locked authority hash mismatch for {key}: expected={entry.sha256}, observed={observed}"
            )
        verified_artifacts[key] = {
            "relative_path": entry.relative_path,
            "sha256": observed,
        }

    runtime_engine = Path(runtime_engine_path).resolve()
    if runtime_engine.suffix == ".pyc" and runtime_engine.with_suffix(".py").is_file():
        runtime_engine = runtime_engine.with_suffix(".py").resolve()
    verified_sources: dict[str, dict[str, str]] = {}
    for key, entry in lock.legacy_sources:
        expected_path = (root / entry.relative_path).resolve()
        if not expected_path.is_file():
            raise ArtifactIntegrityError(f"Locked legacy source missing: {expected_path}")
        observed = file_sha256(expected_path)
        if observed != entry.sha256:
            raise ArtifactIntegrityError(
                f"Locked source hash mismatch for {key}: expected={entry.sha256}, observed={observed}"
            )
        if key == "engine_v1" and runtime_engine != expected_path:
            raise ArtifactIntegrityError(
                f"Imported engine path {runtime_engine} != locked engine path {expected_path}"
            )
        verified_sources[key] = {
            "relative_path": entry.relative_path,
            "sha256": observed,
        }

    return {
        "authority_schema": lock.authority_schema,
        "authority_id": lock.authority_id,
        "seed_count": lock.seed_count,
        "branch_count": lock.branch_count,
        "ordered_branch_namespace": list(lock.ordered_branch_namespace),
        "verified_artifacts": verified_artifacts,
        "verified_sources": verified_sources,
    }
