"""Rebuildable, non-authoritative experiment catalog."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .artifacts import atomic_write_csv, atomic_write_json
from .spec import validate_safe_component
from .validation import CatalogError


CATALOG_FIELDS = (
    "study_id",
    "study_slug",
    "study_version",
    "run_id",
    "full_spec_sha256",
    "execution_id",
    "execution_mode",
    "created_utc",
    "status",
    "freezeable",
    "engine_sha256",
    "runner_sha256",
    "seed_count",
    "condition_count",
    "path",
    "malformed_error",
)


def _required_string(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise CatalogError(f"Manifest {key} must be a nonempty string")
    return value


def _required_nonnegative_int(mapping: dict[str, Any], key: str) -> int:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CatalogError(f"Manifest {key} must be a nonnegative integer")
    return value


def _required_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise CatalogError(f"Manifest {label} must be a lowercase SHA-256")
    return value


def _catalog_row(root: Path, manifest_path: Path) -> dict[str, Any]:
    relative_path = manifest_path.parent.relative_to(root)
    relative = relative_path.as_posix()
    try:
        with open(manifest_path, "r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        if not isinstance(manifest, dict):
            raise CatalogError("Manifest root must be an object")

        study_id = _required_string(manifest, "study_id")
        study_slug = _required_string(manifest, "study_slug")
        study_version = _required_string(manifest, "study_version")
        run_id = _required_string(manifest, "run_id")
        execution_id = _required_string(manifest, "execution_id")
        execution_mode = _required_string(manifest, "execution_mode")
        created_utc = _required_string(manifest, "created_utc")
        status = _required_string(manifest, "status")
        for label, value in (
            ("study_id", study_id),
            ("study_slug", study_slug),
            ("study_version", study_version),
            ("execution_id", execution_id),
        ):
            validate_safe_component(value, label)
        if not re.fullmatch(r"[0-9a-f]{16}", run_id):
            raise CatalogError("Manifest run_id must be 16 lowercase hexadecimal characters")
        if execution_mode not in {"baseline", "production"}:
            raise CatalogError(f"Invalid execution_mode: {execution_mode!r}")
        if not re.fullmatch(
            rf"{execution_mode}_[0-9]{{8}}T[0-9]{{6}}Z_[0-9a-f]{{8}}",
            execution_id,
        ):
            raise CatalogError("execution_id does not agree with execution_mode or v1 format")
        validate_safe_component(status, "status")

        freezeable = manifest.get("freezeable")
        if not isinstance(freezeable, bool):
            raise CatalogError("Manifest freezeable field must be boolean")
        source_hashes = manifest.get("source_hashes")
        completion = manifest.get("completion", {})
        study = manifest.get("study")
        if not isinstance(source_hashes, dict):
            raise CatalogError("Manifest source_hashes must be an object")
        if not isinstance(completion, dict):
            raise CatalogError("Manifest completion must be an object when present")
        if not isinstance(study, dict):
            raise CatalogError("Manifest study must be an object")

        full_spec_sha = _required_sha256(manifest.get("spec_sha256"), "spec_sha256")
        engine_sha = _required_sha256(source_hashes.get("engine"), "source_hashes.engine")
        runner_sha = _required_sha256(source_hashes.get("runner"), "source_hashes.runner")
        seed_count = _required_nonnegative_int(study, "n_seeds")
        if "n_conditions_requested" in completion:
            condition_count = _required_nonnegative_int(completion, "n_conditions_requested")
        elif "expected_condition_count" in study:
            condition_count = _required_nonnegative_int(study, "expected_condition_count")
        else:
            raise CatalogError(
                "Manifest must record completion.n_conditions_requested or study.expected_condition_count"
            )

        expected_relative = (
            Path(f"{study_id}_{study_slug}")
            / study_version
            / run_id
            / execution_mode
            / execution_id
        )
        if relative_path != expected_relative:
            raise CatalogError(
                f"Manifest identity/path mismatch: path={relative_path}, expected={expected_relative}"
            )

        row = {
            "study_id": study_id,
            "study_slug": study_slug,
            "study_version": study_version,
            "run_id": run_id,
            "full_spec_sha256": full_spec_sha,
            "execution_id": execution_id,
            "execution_mode": execution_mode,
            "created_utc": created_utc,
            "status": status,
            "freezeable": freezeable,
            "engine_sha256": engine_sha,
            "runner_sha256": runner_sha,
            "seed_count": seed_count,
            "condition_count": condition_count,
            "path": relative,
            "malformed_error": "",
        }
    except Exception as exc:
        row = {key: "" for key in CATALOG_FIELDS}
        row.update(
            {
                "status": "malformed",
                "freezeable": False,
                "path": relative,
                "malformed_error": f"{type(exc).__name__}: {exc}",
            }
        )
    return row


def rebuild_catalog(output_root: str | Path, *, replace: bool = False) -> tuple[Path, Path]:
    root = Path(output_root)
    if not root.exists():
        raise CatalogError(f"Output root does not exist: {root}")
    csv_path = root / "catalog.csv"
    json_path = root / "catalog.json"
    if not replace and (csv_path.exists() or json_path.exists()):
        raise CatalogError(
            "Catalog output already exists; pass --replace-catalog to rebuild it explicitly"
        )

    manifests = sorted(
        path
        for path in root.rglob("manifest.json")
        if path.parent.name != "analysis"
    )
    rows = [_catalog_row(root, path) for path in manifests]
    rows.sort(
        key=lambda row: (
            str(row["study_id"]),
            str(row["study_version"]),
            str(row["run_id"]),
            str(row["execution_id"]),
            str(row["path"]),
        )
    )

    seen: dict[tuple[str, str, str, str], str] = {}
    for row in rows:
        if row["status"] == "malformed":
            continue
        identity = (
            str(row["study_id"]),
            str(row["study_version"]),
            str(row["run_id"]),
            str(row["execution_id"]),
        )
        if identity in seen:
            raise CatalogError(
                f"Duplicate catalog execution identity {identity!r}: "
                f"{seen[identity]} and {row['path']}"
            )
        seen[identity] = str(row["path"])

    atomic_write_csv(csv_path, rows, CATALOG_FIELDS)
    atomic_write_json(
        json_path,
        {
            "catalog_schema": "aief-catalog-v1",
            "authority": "derived_non_authoritative",
            "entries": rows,
            "malformed_count": sum(row["status"] == "malformed" for row in rows),
        },
    )
    return csv_path, json_path
