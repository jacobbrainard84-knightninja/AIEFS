"""Atomic artifact I/O, execution paths, hashing, and write locks."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
import os
import platform
import re
import secrets
import socket
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .spec import ExperimentSpec, validate_safe_component
from .validation import ArtifactIntegrityError, ExecutionLockError


def file_sha256(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(str(directory), flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _temp_path(destination: Path, suffix: str = ".tmp") -> tuple[int, Path]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=f".{destination.name}.",
        suffix=suffix,
    )
    return descriptor, Path(name)


def _replace_and_sync(temporary: Path, destination: Path) -> None:
    os.replace(temporary, destination)
    _fsync_directory(destination.parent)


def strict_json_value(value: Any) -> Any:
    """Convert supported production values to JSON without silent coercion."""
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ArtifactIntegrityError(
                    f"JSON mapping key must be str, got {type(key).__name__}"
                )
            if key in result:
                raise ArtifactIntegrityError(f"Duplicate JSON mapping key: {key!r}")
            result[key] = strict_json_value(item)
        return result
    if isinstance(value, (tuple, list)):
        return [strict_json_value(item) for item in value]
    if isinstance(value, np.ndarray):
        return strict_json_value(value.tolist())
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return strict_json_value(value.item())
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ArtifactIntegrityError("Non-finite float in strict production JSON")
        return value
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return value
    raise ArtifactIntegrityError(
        f"Unsupported strict JSON value type: {type(value).__module__}.{type(value).__qualname__}"
    )


def diagnostic_json_value(value: Any) -> Any:
    """Best-effort conversion used only for non-authoritative diagnostics."""
    if isinstance(value, Mapping):
        items: list[tuple[str, Any]] = []
        for key, item in value.items():
            key_text = key if isinstance(key, str) else f"<{type(key).__name__}:{key!r}>"
            items.append((key_text, diagnostic_json_value(item)))
        # Retain collision evidence rather than silently overwriting it.
        result: dict[str, Any] = {}
        for key, item in items:
            if key in result:
                key = f"{key}<duplicate>"
            result[key] = item
        return result
    if isinstance(value, (tuple, list, set)):
        return [diagnostic_json_value(item) for item in value]
    if isinstance(value, np.ndarray):
        return diagnostic_json_value(value.tolist())
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return diagnostic_json_value(value.item())
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return value
    return {
        "unsupported_type": f"{type(value).__module__}.{type(value).__qualname__}",
        "diagnostic_repr": repr(value),
    }


def atomic_write_text(path: str | Path, text: str) -> None:
    destination = Path(path)
    descriptor, temporary = _temp_path(destination)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        _replace_and_sync(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path: str | Path, value: Any) -> None:
    """Atomically write authoritative JSON using strict type validation."""
    text = json.dumps(
        strict_json_value(value), indent=2, sort_keys=True, allow_nan=False
    ) + "\n"
    atomic_write_text(path, text)


def atomic_write_diagnostic_json(path: str | Path, value: Any) -> None:
    """Atomically write explicitly non-authoritative failure diagnostics."""
    text = json.dumps(
        diagnostic_json_value(value), indent=2, sort_keys=True, allow_nan=False
    ) + "\n"
    atomic_write_text(path, text)


def atomic_write_csv(
    path: str | Path,
    rows: Sequence[Mapping[str, Any]],
    fieldnames: Sequence[str] | None = None,
) -> None:
    destination = Path(path)
    if fieldnames is None:
        if not rows:
            raise ArtifactIntegrityError("Cannot infer CSV fields from an empty row set")
        fieldnames = tuple(rows[0])
    fieldnames = tuple(fieldnames)
    if not fieldnames or len(fieldnames) != len(set(fieldnames)):
        raise ArtifactIntegrityError("CSV fieldnames must be nonempty and unique")
    if any(not isinstance(field, str) or not field for field in fieldnames):
        raise ArtifactIntegrityError("CSV fieldnames must be nonempty strings")
    expected = set(fieldnames)
    for index, row in enumerate(rows):
        observed = set(row)
        missing = expected - observed
        extra = observed - expected
        if missing or extra:
            raise ArtifactIntegrityError(
                f"CSV row {index} schema mismatch: "
                f"missing={sorted(missing)}, extra={sorted(extra)}"
            )
    descriptor, temporary = _temp_path(destination)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(fieldnames), extrasaction="raise")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        _replace_and_sync(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_npz(path: str | Path, payload: Mapping[str, Any]) -> None:
    destination = Path(path)
    descriptor, temporary = _temp_path(destination, suffix=".tmp.npz")
    try:
        with os.fdopen(descriptor, "wb") as handle:
            np.savez_compressed(handle, **payload)
            handle.flush()
            os.fsync(handle.fileno())
        _replace_and_sync(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_npz(path: str | Path) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    try:
        with np.load(path, allow_pickle=False) as archive:
            if len(archive.files) != len(set(archive.files)):
                raise ArtifactIntegrityError(f"NPZ contains duplicate keys: {path}")
            for key in archive.files:
                value = archive[key]
                payload[key] = value.item() if value.ndim == 0 else value.copy()
    except ArtifactIntegrityError:
        raise
    except Exception as exc:
        raise ArtifactIntegrityError(f"Cannot load NPZ {path}: {exc}") from exc
    return payload


def utc_now_text() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_execution_id(mode: str) -> str:
    if mode not in {"baseline", "production"}:
        raise ValueError(f"Invalid execution mode: {mode}")
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{mode}_{timestamp}_{secrets.token_hex(4)}"


@dataclass(frozen=True)
class ExecutionPaths:
    leaf: Path
    manifest: Path
    failed_manifest: Path
    baseline_certificate: Path
    baseline_by_seed: Path
    condition_status: Path
    scalar_csv: Path
    branch_npz: Path
    conditions: Path
    logs: Path
    analysis: Path
    failure: Path
    lock_file: Path


def execution_paths(
    output_root: str | Path,
    spec: ExperimentSpec,
    run_id: str,
    mode: str,
    execution_id: str,
) -> ExecutionPaths:
    root = Path(output_root)
    validate_safe_component(spec.study_id, "study_id")
    validate_safe_component(spec.study_slug, "study_slug")
    validate_safe_component(spec.study_version, "study_version")
    if not isinstance(run_id, str) or len(run_id) != 16 or any(
        character not in "0123456789abcdef" for character in run_id
    ):
        raise ArtifactIntegrityError("run_id must contain exactly 16 lowercase hexadecimal characters")
    if mode not in {"baseline", "production"}:
        raise ArtifactIntegrityError(f"Unsafe execution mode: {mode!r}")
    validate_safe_component(execution_id, "execution_id")
    if not re.fullmatch(
        rf"{mode}_[0-9]{{8}}T[0-9]{{6}}Z_[0-9a-f]{{8}}",
        execution_id,
    ):
        raise ArtifactIntegrityError(
            f"execution_id {execution_id!r} does not match mode {mode!r} or v1 format"
        )
    policy = spec.artifact_policy
    study_directory = f"{spec.study_id}_{spec.study_slug}"
    leaf = root / study_directory / spec.study_version / run_id / mode / execution_id
    scalar_name = f"{policy.scalar_filename_prefix}_{run_id}_scalar_summary.csv"
    array_name = f"{policy.array_filename_prefix}_{run_id}_branch_diagnostics.npz"
    validate_safe_component(scalar_name, "scalar filename", filename=True)
    validate_safe_component(array_name, "array filename", filename=True)
    return ExecutionPaths(
        leaf=leaf,
        manifest=leaf / policy.manifest_filename,
        failed_manifest=leaf / policy.failed_manifest_filename,
        baseline_certificate=leaf / policy.baseline_certificate_filename,
        baseline_by_seed=leaf / policy.baseline_by_seed_filename,
        condition_status=leaf / policy.condition_status_filename,
        scalar_csv=leaf / scalar_name,
        branch_npz=leaf / array_name,
        conditions=leaf / "conditions",
        logs=leaf / "logs",
        analysis=leaf / "analysis",
        failure=leaf / "failure",
        lock_file=leaf / policy.lock_filename,
    )


def create_execution_directory(paths: ExecutionPaths) -> None:
    if paths.leaf.exists():
        raise ArtifactIntegrityError(
            f"Execution directory already exists and overwrite is unsupported: {paths.leaf}"
        )
    paths.leaf.mkdir(parents=True, exist_ok=False)
    for directory in (paths.conditions, paths.logs, paths.analysis, paths.failure):
        directory.mkdir()
    _fsync_directory(paths.leaf.parent)


class ExecutionLock:
    """Atomic create-only lock.  Existing locks are never stolen."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._held = False

    def acquire(self) -> None:
        record = {
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "started_utc": utc_now_text(),
        }
        try:
            descriptor = os.open(
                self.path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o644,
            )
        except FileExistsError as exc:
            raise ExecutionLockError(
                f"Execution lock already exists: {self.path}. "
                "Stale locks require explicit manual investigation and removal."
            ) from exc
        try:
            payload = (json.dumps(record, sort_keys=True) + "\n").encode("utf-8")
            os.write(descriptor, payload)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        _fsync_directory(self.path.parent)
        self._held = True

    def release(self) -> None:
        if self._held and self.path.exists():
            self.path.unlink()
            _fsync_directory(self.path.parent)
        self._held = False

    def __enter__(self) -> "ExecutionLock":
        self.acquire()
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.release()
