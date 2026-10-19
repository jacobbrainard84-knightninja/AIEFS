"""Atomic artifact I/O, execution paths, hashing, and write locks."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
import os
import platform
import secrets
import socket
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .spec import ExperimentSpec
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


def json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return json_safe(value.item())
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return str(value)


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
    text = json.dumps(json_safe(value), indent=2, sort_keys=True, allow_nan=False) + "\n"
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
    study_directory = f"{spec.study_id}_{spec.study_slug}"
    leaf = root / study_directory / spec.study_version / run_id / mode / execution_id
    prefix = spec.artifact_policy.scalar_filename_prefix
    scalar_name = f"{prefix}_{run_id}_scalar_summary.csv"
    array_name = f"{spec.artifact_policy.array_filename_prefix}_{run_id}_branch_diagnostics.npz"
    return ExecutionPaths(
        leaf=leaf,
        manifest=leaf / "manifest.json",
        failed_manifest=leaf / "FAILED_manifest.json",
        baseline_certificate=leaf / "baseline_equivalence_certificate.json",
        baseline_by_seed=leaf / "baseline_equivalence_by_seed.json",
        condition_status=leaf / "twindow_condition_status.csv",
        scalar_csv=leaf / scalar_name,
        branch_npz=leaf / array_name,
        conditions=leaf / "conditions",
        logs=leaf / "logs",
        analysis=leaf / "analysis",
        failure=leaf / "failure",
        lock_file=leaf / ".execution.lock",
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
