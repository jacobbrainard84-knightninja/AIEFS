"""Rebuildable, non-authoritative experiment catalog."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .artifacts import atomic_write_csv, atomic_write_json
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


def _catalog_row(root: Path, manifest_path: Path) -> dict[str, Any]:
    relative = manifest_path.parent.relative_to(root).as_posix()
    try:
        with open(manifest_path, "r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        source_hashes = manifest.get("source_hashes", {})
        completion = manifest.get("completion", {})
        row = {
            "study_id": manifest["study_id"],
            "study_slug": manifest["study_slug"],
            "study_version": manifest["study_version"],
            "run_id": manifest["run_id"],
            "full_spec_sha256": manifest["spec_sha256"],
            "execution_id": manifest["execution_id"],
            "execution_mode": manifest["execution_mode"],
            "created_utc": manifest["created_utc"],
            "status": manifest.get("status", completion.get("status", "unknown")),
            "freezeable": bool(manifest.get("freezeable", False)),
            "engine_sha256": source_hashes.get("engine", "MISSING"),
            "runner_sha256": source_hashes.get("runner", "MISSING"),
            "seed_count": int(manifest.get("study", {}).get("n_seeds", 0)),
            "condition_count": int(completion.get("n_conditions_requested", 0)),
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
