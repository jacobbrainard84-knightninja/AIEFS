"""Logical-content comparison against the successful T_window production oracle."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .validation import ArtifactIntegrityError, exact_equal_with_nan, exact_scalar_equal_with_nan


@dataclass(frozen=True)
class OracleComparison:
    status: str
    scalar_rows: int
    npz_entries: int
    condition_rows: int
    errors: tuple[str, ...]


def _read_csv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ArtifactIntegrityError(f"CSV has no header: {path}")
        return tuple(reader.fieldnames), list(reader)


def _is_numeric_text(value: str) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _compare_scalar_csv(candidate: Path, oracle: Path, errors: list[str]) -> int:
    candidate_fields, candidate_rows = _read_csv(candidate)
    oracle_fields, oracle_rows = _read_csv(oracle)
    if candidate_fields != oracle_fields:
        errors.append(
            f"Scalar CSV columns/order differ: candidate={candidate_fields!r}, oracle={oracle_fields!r}"
        )
        return len(candidate_rows)
    if len(candidate_rows) != len(oracle_rows):
        errors.append(
            f"Scalar CSV row count differs: candidate={len(candidate_rows)}, oracle={len(oracle_rows)}"
        )
        return len(candidate_rows)

    text_fields = {"seed_index", "seed", "branch"}
    for index, (left, right) in enumerate(zip(candidate_rows, oracle_rows, strict=True)):
        for field in candidate_fields:
            a = left[field]
            b = right[field]
            if field in text_fields:
                if a != b:
                    errors.append(f"Scalar row {index} field {field}: {a!r} != {b!r}")
            elif not exact_scalar_equal_with_nan(a, b):
                errors.append(f"Scalar row {index} field {field}: {a!r} != {b!r}")
            if len(errors) >= 100:
                return len(candidate_rows)
    return len(candidate_rows)


def _load_npz(path: Path) -> dict[str, np.ndarray]:
    try:
        with np.load(path, allow_pickle=False) as archive:
            return {key: archive[key].copy() for key in archive.files}
    except Exception as exc:
        raise ArtifactIntegrityError(f"Cannot load NPZ {path}: {exc}") from exc


def _compare_npz(candidate: Path, oracle: Path, errors: list[str]) -> int:
    left = _load_npz(candidate)
    right = _load_npz(oracle)
    if set(left) != set(right):
        missing = sorted(set(right) - set(left))
        extra = sorted(set(left) - set(right))
        errors.append(f"NPZ key mismatch: missing={missing[:20]}, extra={extra[:20]}")
    for key in sorted(set(left) & set(right)):
        if not exact_equal_with_nan(left[key], right[key]):
            errors.append(
                f"NPZ value mismatch for {key}: "
                f"candidate(shape={left[key].shape},dtype={left[key].dtype}), "
                f"oracle(shape={right[key].shape},dtype={right[key].dtype})"
            )
            if len(errors) >= 100:
                break
    return len(left)


def _compare_condition_coverage(candidate: Path, oracle: Path, errors: list[str]) -> int:
    left_fields, left_rows = _read_csv(candidate)
    right_fields, right_rows = _read_csv(oracle)
    required = {"seed", "rho", "status"}
    if not required.issubset(left_fields) or not required.issubset(right_fields):
        errors.append("Condition status files lack seed/rho/status columns")
        return len(left_rows)
    left_keys = {(row["seed"], float(row["rho"]), row["status"]) for row in left_rows}
    right_keys = {(row["seed"], float(row["rho"]), row["status"]) for row in right_rows}
    if left_keys != right_keys:
        errors.append(
            f"Condition status coverage differs: missing={sorted(right_keys-left_keys)[:10]}, "
            f"extra={sorted(left_keys-right_keys)[:10]}"
        )
    return len(left_rows)


def _single_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if len(files) != 1:
        raise ArtifactIntegrityError(
            f"Expected exactly one {pattern!r} in {directory}, found {[item.name for item in files]}"
        )
    return files[0]


def compare_twindow_run(candidate_dir: str | Path, oracle_dir: str | Path) -> OracleComparison:
    """Compare decompressed logical contents, never compressed NPZ bytes."""
    candidate = Path(candidate_dir)
    oracle = Path(oracle_dir)
    errors: list[str] = []
    candidate_csv = _single_file(candidate, "AIEF_1_4_Twindow_sensitivity_*_scalar_summary.csv")
    oracle_csv = _single_file(oracle, "AIEF_1_4_Twindow_sensitivity_*_scalar_summary.csv")
    candidate_npz = _single_file(candidate, "AIEF_1_4_Twindow_sensitivity_*_branch_diagnostics.npz")
    oracle_npz = _single_file(oracle, "AIEF_1_4_Twindow_sensitivity_*_branch_diagnostics.npz")
    scalar_rows = _compare_scalar_csv(candidate_csv, oracle_csv, errors)
    npz_entries = _compare_npz(candidate_npz, oracle_npz, errors)
    condition_rows = _compare_condition_coverage(
        candidate / "twindow_condition_status.csv",
        oracle / "twindow_condition_status.csv",
        errors,
    )
    return OracleComparison(
        status="passed" if not errors else "failed",
        scalar_rows=scalar_rows,
        npz_entries=npz_entries,
        condition_rows=condition_rows,
        errors=tuple(errors),
    )
