#!/usr/bin/env python3
"""AIEF-1.4 T_window sensitivity reanalysis v4.1 -- CANDIDATE, UNAUDITED.

STATUS: CANDIDATE / UNAUDITED. DO NOT RUN ON REAL TRAJECTORIES.
This file is a proposed successor to Analysis v4
(AIEF_1_4_Twindow_sensitivity_analysis_v4.py, hash-pinned and left
byte-identical). It has only been exercised on synthetic data in
tests/test_v4_1_held_event.py. Its outputs must not be cited, registered, or
compared with v4 bundles until it has been independently audited and
frozen. main() refuses to run without --allow-unaudited-candidate.

Changes from Analysis v4 (and nothing else)
--------------------------------------------
* Held-event end check. v4 used
  ``searchsorted(times, times[index] + duration, side="left")``. On a
  floating-point grid ``times[index] + duration`` can round one ulp above the
  saved sample that is exactly ``duration`` later, so an event held exactly
  the required duration (e.g. 17.5 on the 0.5-spaced saved grid) was
  rejected. v4.1 searches for ``times[index] + duration - tol`` with
  ``tol = HOLD_TOLERANCE_FRACTION * h_min`` (``h_min`` = smallest positive
  spacing of the saved time grid, ``min(diff(times))``, not the simulation dt;
  ``HOLD_TOLERANCE_FRACTION`` = 1e-6, so tol = 0.5e-6 on the 0.5-spaced saved
  grid). The tolerance is NOT dt/2 and the check is NOT done on integer step
  indices; it stays a timestamp comparison as in v4. Justification: the rounding
  error is O(machine-eps * |t|), about 1e-13 here, i.e. ~7 orders of magnitude
  below tol, while tol is 6 orders of magnitude below one grid step, so a run
  one step short is still rejected and nominal durations that are not grid
  multiples (e.g. T_window = 17.5029...) are unaffected unless they lie
  within tol of a grid multiple.
* Held events are split into two estimands in addition to the v4-style
  ``held`` event (kept, with the corrected end check):
  - ``held_retention``: the condition is true from the first saved sample and
    stays true, without any drop, for at least the hold duration.
  - ``held_recovery``: the condition is false at some saved sample (including
    the first) and afterwards re-crosses and is held for the duration; the
    event index is the earliest such re-crossing after the first drop.
  ``held_classification`` (retention / recovery / none) is mutually
  exclusive with retention taking precedence.
  These are the only new estimands. There is no "time to first loss"
  (time of the first drop below target) estimand; that is a possible future
  addition and would need its own versioned, audited change.
* Version labels, output file names (``_v4_1``) and the bundle directory
  (``v4_1``) differ so v4 bundles are never overwritten. Hard-coded row-count
  checks were updated for the two extra event types.

Original v4 description follows.

Analysis v4 is a separately versioned reanalysis of the existing S01 raw run.
It does not regenerate trajectories and does not modify Engine v1, Modular
Runner v1, the legacy collector, or Analysis v3.

Main changes from Analysis v3
-----------------------------
* Recovery target definitions are separated from observation support.
* Recovery events are explicitly saved-grid events on [0.01, 319.51].
* Held recovery uses timestamps: times[j] - times[i] >= duration.
* Both a fixed 17.5-unit hold and one-current-T_window hold are reported.
* Density events and threshold-independent AUCs are not duplicated under two
  horizon labels.
* Undefined zero-vector cosine is retained as NaN in raw input and converted to
  zero in one explicit derived recovery representation used consistently by
  recovery events and AUC.
* Restricted event times and event indicators are full-cohort outcomes.
* Raw event-time interactions are explicitly four-cell complete-case outcomes.
* The same bootstrap seed resamples the same seed indices across all groups.
  Primary regime/DID/topology families also receive simultaneous max-t bands.
* Outputs are written to a staging directory and promoted atomically as one
  immutable analysis bundle.

The analysis cannot reconstruct unsaved t=0/t=320 observations or exact
step-level crossing times. Those require a new engine/collector version.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import platform
import secrets
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

import aief_modular.artifacts as modular_artifacts
import aief_modular.validation as modular_validation
from aief_modular.artifacts import (
    atomic_write_json,
    atomic_write_text,
    file_sha256,
)
from aief_modular.validation import ArtifactIntegrityError


ANALYSIS_ID = "AIEF_1_4_TWINDOW_ANALYSIS_V4_1_CANDIDATE"
ANALYSIS_VERSION = "v4.1-candidate-unaudited"
STUDY_NAME = "AIEF_1_4_Twindow_sensitivity"
EXPECTED_N_SEEDS = 40
EXPECTED_RHO_VALUES = (0.5, 0.75, 1.0, 1.5, 2.0)
EXPECTED_BRANCHES = ("continue", "reset_ema", "reset_B", "future_shuffle")
NON_CONTINUE_BRANCHES = ("reset_ema", "reset_B", "future_shuffle")
EXPECTED_SAMPLE_TIMES = (np.arange(0, 32000, 50, dtype=float) + 1.0) * 0.01
SUPPORT_START = float(EXPECTED_SAMPLE_TIMES[0])
SUPPORT_END = float(EXPECTED_SAMPLE_TIMES[-1])
SAMPLE_SPACING = 0.5
FIXED_HOLD_DURATION = 17.5
# v4.1: tolerance for the held-event end check, as a fraction of grid spacing.
HOLD_TOLERANCE_FRACTION = 1e-6
HELD_EVENT_TYPES = ("held", "held_retention", "held_recovery")

PRIMARY_OUTCOMES = (
    "Weighted_similarity_late_fixed_physical",
    "Retention_contrast_late_fixed_physical",
    "P_mean_late_fixed_physical",
)
SECONDARY_OUTCOMES = (
    "Weighted_similarity_late_normalized_EMA",
    "Retention_contrast_late_normalized_EMA",
    "P_mean_late_normalized_EMA",
)


@dataclass(frozen=True)
class RunInputs:
    run_dir: Path
    scalar_csv: Path
    branch_npz: Path
    manifest: Path
    condition_status: Path
    baseline_certificate: Path


@dataclass(frozen=True)
class ValidatedRun:
    inputs: RunInputs
    scalar: pd.DataFrame
    manifest: dict[str, Any]
    seeds: tuple[str, ...]
    rho_values: tuple[float, ...]
    branches: tuple[str, ...]
    b_c: float
    t_star: float
    input_hashes: dict[str, str]


# ---------------------------------------------------------------------------
# Atomic analysis-bundle utilities
# ---------------------------------------------------------------------------


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(str(path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def save_dataframe_atomic(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    try:
        with open(temporary, "w", encoding="utf-8", newline="") as handle:
            frame.to_csv(handle, index=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def analysis_execution_id() -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"analysis_v4_1_{stamp}_{secrets.token_hex(4)}"


def source_sha256() -> str:
    return file_sha256(Path(__file__))


def seed_set_sha256(seeds: Sequence[str]) -> str:
    text = json.dumps(list(seeds), separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def analysis_contract() -> dict[str, Any]:
    return {
        "raw_trajectory_unchanged": True,
        "observation_support": [SUPPORT_START, SUPPORT_END],
        "sample_spacing": SAMPLE_SPACING,
        "event_time_semantics": "saved_grid_interval_censored",
        "undefined_similarity": "raw_NaN_derived_recovery_zero",
        "held_end_check": "searchsorted_left_on_t_plus_duration_minus_1e-6_dt",
        "held_event_types": list(HELD_EVENT_TYPES),
        "hold_duration_systems": [
            "fixed_physical_17p5",
            "one_current_Twindow_nominal",
        ],
        "AUC_support": "saved_grid_0p01_to_319p51",
        "full_cohort_recovery_estimands": [
            "restricted_time",
            "restricted_time_over_Twindow",
            "event_observed",
            "auc_deficit",
        ],
        "conditional_secondary_estimands": [
            "event_time",
            "event_time_over_Twindow",
            "four_cell_complete_case_event_DID",
        ],
        "primary_interval_family": "fixed_physical_regime_and_branch_DID",
        "secondary_interval_family": "normalized_EMA_regime_and_branch_DID",
    }


def canonical_sha256(value: Mapping[str, Any]) -> str:
    text = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Input discovery and validation
# ---------------------------------------------------------------------------


def _one(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        raise ArtifactIntegrityError(
            f"Expected exactly one {pattern!r} in {directory}, found {[p.name for p in matches]}"
        )
    return matches[0]


def discover_inputs(run_dir: str | Path) -> RunInputs:
    root = Path(run_dir)
    if not root.is_dir():
        raise ArtifactIntegrityError(f"Run directory not found: {root}")
    return RunInputs(
        run_dir=root,
        scalar_csv=_one(root, f"{STUDY_NAME}_*_scalar_summary.csv"),
        branch_npz=_one(root, f"{STUDY_NAME}_*_branch_diagnostics.npz"),
        manifest=root / "manifest.json",
        condition_status=root / "twindow_condition_status.csv",
        baseline_certificate=root / "baseline_equivalence_certificate.json",
    )


def _load_scalar(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"seed": str, "branch": str})
    if "rho" in frame:
        frame["rho"] = pd.to_numeric(frame["rho"], errors="raise")
    for column in frame.columns:
        if column not in {"seed", "branch"}:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def _require_hash(manifest: Mapping[str, Any], label: str, path: Path) -> None:
    expected = manifest.get("output_hashes", {}).get(label)
    if not isinstance(expected, str):
        raise ArtifactIntegrityError(f"Manifest lacks output hash {label!r}")
    observed = file_sha256(path)
    if observed != expected:
        raise ArtifactIntegrityError(
            f"Input hash mismatch for {label}: expected={expected}, observed={observed}"
        )


def validate_run(inputs: RunInputs) -> ValidatedRun:
    for path in (
        inputs.manifest,
        inputs.condition_status,
        inputs.baseline_certificate,
        inputs.scalar_csv,
        inputs.branch_npz,
    ):
        if not path.is_file():
            raise ArtifactIntegrityError(f"Required input missing: {path}")

    with open(inputs.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise ArtifactIntegrityError("Simulation manifest root must be an object")
    if manifest.get("freezeable") is not True:
        raise ArtifactIntegrityError("Simulation run is not explicitly freezeable")
    completion = manifest.get("completion", {})
    if completion.get("status") != "completed":
        raise ArtifactIntegrityError("Simulation run is not completed")
    if manifest.get("baseline_equivalence", {}).get("status") != "passed":
        raise ArtifactIntegrityError("Simulation baseline equivalence is not passed")

    for label, path in (
        ("scalar_csv", inputs.scalar_csv),
        ("branch_npz", inputs.branch_npz),
        ("condition_status_csv", inputs.condition_status),
        ("baseline_certificate", inputs.baseline_certificate),
    ):
        _require_hash(manifest, label, path)

    with open(inputs.baseline_certificate, "r", encoding="utf-8") as handle:
        certificate = json.load(handle)
    if certificate.get("status") != "passed" or certificate.get("n_seeds") != 40:
        raise ArtifactIntegrityError("Baseline certificate is not a passing 40-seed certificate")

    frame = _load_scalar(inputs.scalar_csv)
    required_columns = {
        "seed",
        "seed_index",
        "rho",
        "T_window",
        "branch",
        "D_B_final",
        *PRIMARY_OUTCOMES,
        *SECONDARY_OUTCOMES,
    }
    missing = required_columns - set(frame)
    if missing:
        raise ArtifactIntegrityError(f"Scalar CSV missing fields: {sorted(missing)}")
    if len(frame) != 800:
        raise ArtifactIntegrityError(f"Scalar CSV has {len(frame)} rows, expected 800")
    if frame.duplicated(["seed", "rho", "branch"]).any():
        raise ArtifactIntegrityError("Scalar CSV contains duplicate seed/rho/branch rows")

    randomization = manifest.get("randomization", {})
    study = manifest.get("study", {})
    protocol = manifest.get("protocol", {})
    model = manifest.get("model", {})
    seeds = tuple(str(seed) for seed in randomization.get("paired_seeds", ()))
    rho_values = tuple(float(value) for value in study.get("rho_values", ()))
    branches = tuple(protocol.get("branches", ()))
    if len(seeds) != EXPECTED_N_SEEDS or len(set(seeds)) != EXPECTED_N_SEEDS:
        raise ArtifactIntegrityError("Manifest does not contain 40 unique paired seeds")
    if rho_values != EXPECTED_RHO_VALUES:
        raise ArtifactIntegrityError(f"Unexpected rho levels/order: {rho_values}")
    if branches != EXPECTED_BRANCHES:
        raise ArtifactIntegrityError(f"Unexpected branch set/order: {branches}")

    expected_conditions = {
        (seed, rho, branch)
        for seed in seeds
        for rho in rho_values
        for branch in branches
    }
    observed_conditions = set(zip(frame["seed"], frame["rho"], frame["branch"]))
    if observed_conditions != expected_conditions:
        raise ArtifactIntegrityError("Scalar condition coverage differs from manifest design")

    for outcome in (*PRIMARY_OUTCOMES, *SECONDARY_OUTCOMES, "D_B_final"):
        values = pd.to_numeric(frame[outcome], errors="coerce").to_numpy(float)
        if not np.all(np.isfinite(values)):
            raise ArtifactIntegrityError(f"Scalar outcome {outcome} contains nonfinite values")
    density = frame["D_B_final"].to_numpy(float)
    if np.any((density < 0.0) | (density > 1.0)):
        raise ArtifactIntegrityError("D_B_final is outside [0,1]")

    t_star = float(model.get("T_star", float("nan")))
    if not np.isfinite(t_star) or t_star <= 0.0:
        raise ArtifactIntegrityError("Manifest model.T_star is invalid")
    for rho in rho_values:
        observed = frame.loc[frame["rho"] == rho, "T_window"].unique()
        if len(observed) != 1 or float(observed[0]) != rho * t_star:
            raise ArtifactIntegrityError(f"rho={rho} has inconsistent nominal T_window")

    status = pd.read_csv(inputs.condition_status, dtype={"seed": str})
    if len(status) != 200 or status.duplicated(["seed", "rho"]).any():
        raise ArtifactIntegrityError("Condition-status table does not have 200 unique conditions")
    if set(status["status"]) != {"success"}:
        raise ArtifactIntegrityError("Condition-status table contains non-success conditions")
    observed_status = set(zip(status["seed"], status["rho"].astype(float)))
    expected_status = {(seed, rho) for seed in seeds for rho in rho_values}
    if observed_status != expected_status:
        raise ArtifactIntegrityError("Condition-status coverage differs from design")

    b_c = float(model.get("B_c", float("nan")))
    if not np.isfinite(b_c) or b_c < 0.0:
        raise ArtifactIntegrityError("Manifest model.B_c is invalid")

    input_hashes = {
        "scalar_csv": file_sha256(inputs.scalar_csv),
        "branch_npz": file_sha256(inputs.branch_npz),
        "simulation_manifest": file_sha256(inputs.manifest),
        "condition_status": file_sha256(inputs.condition_status),
        "baseline_certificate": file_sha256(inputs.baseline_certificate),
    }
    return ValidatedRun(
        inputs=inputs,
        scalar=frame,
        manifest=manifest,
        seeds=seeds,
        rho_values=rho_values,
        branches=branches,
        b_c=b_c,
        t_star=t_star,
        input_hashes=input_hashes,
    )


# ---------------------------------------------------------------------------
# Common scientific metrics
# ---------------------------------------------------------------------------


def cosine_edges(left: np.ndarray, right: np.ndarray) -> float:
    if left.shape != (12, 12) or right.shape != (12, 12):
        raise ArtifactIntegrityError("Topology matrix shape must be (12,12)")
    if not np.all(np.isfinite(left)) or not np.all(np.isfinite(right)):
        raise ArtifactIntegrityError("Topology matrix contains nonfinite values")
    edges = np.triu_indices(12, 1)
    x = left[edges]
    y = right[edges]
    denominator = float(np.linalg.norm(x) * np.linalg.norm(y))
    if denominator <= 1e-12:
        return float("nan")
    return float(np.dot(x, y) / denominator)


def jaccard_edges(left: np.ndarray, right: np.ndarray, threshold: float) -> float:
    edges = np.triu_indices(12, 1)
    x = left[edges] > threshold
    y = right[edges] > threshold
    union = np.count_nonzero(x | y)
    return float(np.count_nonzero(x & y) / union) if union else float("nan")


def normalized_distance(left: np.ndarray, baseline: np.ndarray) -> float:
    edges = np.triu_indices(12, 1)
    denominator = float(np.linalg.norm(baseline[edges]))
    if denominator <= 1e-12:
        return float("nan")
    return float(np.linalg.norm(left[edges] - baseline[edges]) / denominator)


def regime_contrasts(frame: pd.DataFrame, outcomes: Sequence[str], system: str) -> pd.DataFrame:
    control = frame.loc[frame["branch"] == "continue", ["seed", "rho", *outcomes]].copy()
    baseline = control.loc[control["rho"] == 1.0, ["seed", *outcomes]].rename(
        columns={outcome: f"{outcome}_baseline" for outcome in outcomes}
    )
    merged = control.merge(baseline, on="seed", validate="many_to_one")
    rows: list[dict[str, Any]] = []
    for row in merged.loc[merged["rho"] != 1.0].itertuples(index=False):
        values = row._asdict()
        for outcome in outcomes:
            current = float(values[outcome])
            reference = float(values[f"{outcome}_baseline"])
            rows.append(
                {
                    "seed": values["seed"],
                    "rho": float(values["rho"]),
                    "target_system": system,
                    "outcome": outcome,
                    "Y_rho_continue": current,
                    "Y_baseline_continue": reference,
                    "paired_regime_contrast": current - reference,
                }
            )
    return pd.DataFrame(rows)


def branch_interactions(frame: pd.DataFrame, outcomes: Sequence[str], system: str) -> pd.DataFrame:
    indexed = frame.set_index(["seed", "rho", "branch"], verify_integrity=True)
    rows: list[dict[str, Any]] = []
    for seed in frame["seed"].unique():
        for rho in EXPECTED_RHO_VALUES:
            if rho == 1.0:
                continue
            for branch in NON_CONTINUE_BRANCHES:
                for outcome in outcomes:
                    y_rho_b = float(indexed.loc[(seed, rho, branch), outcome])
                    y_rho_c = float(indexed.loc[(seed, rho, "continue"), outcome])
                    y_base_b = float(indexed.loc[(seed, 1.0, branch), outcome])
                    y_base_c = float(indexed.loc[(seed, 1.0, "continue"), outcome])
                    effect_rho = y_rho_b - y_rho_c
                    effect_base = y_base_b - y_base_c
                    rows.append(
                        {
                            "seed": seed,
                            "rho": rho,
                            "branch": branch,
                            "target_system": system,
                            "outcome": outcome,
                            "branch_effect_rho": effect_rho,
                            "branch_effect_baseline": effect_base,
                            "difference_in_differences": effect_rho - effect_base,
                        }
                    )
    return pd.DataFrame(rows)


def _npz_key(branch: str, seed: str, rho: float, field: str) -> str:
    return f"{branch}_seed_{seed}_rho_{rho}_{field}"


def load_npz_keys(path: Path, keys: Iterable[str]) -> dict[str, np.ndarray]:
    requested = tuple(dict.fromkeys(keys))
    result: dict[str, np.ndarray] = {}
    try:
        with np.load(path, allow_pickle=False) as archive:
            missing = [key for key in requested if key not in archive]
            if missing:
                raise ArtifactIntegrityError(
                    f"NPZ missing {len(missing)} required entries: {missing[:10]}"
                )
            for key in requested:
                result[key] = archive[key].copy()
    except ArtifactIntegrityError:
        raise
    except Exception as exc:
        raise ArtifactIntegrityError(f"Cannot read NPZ: {exc}") from exc
    return result


def cross_t_topology(run: ValidatedRun) -> pd.DataFrame:
    keys = [
        _npz_key("continue", seed, rho, "B_final")
        for seed in run.seeds
        for rho in run.rho_values
    ]
    arrays = load_npz_keys(run.inputs.branch_npz, keys)
    rows = []
    for seed in run.seeds:
        baseline = np.asarray(arrays[_npz_key("continue", seed, 1.0, "B_final")], float)
        for rho in run.rho_values:
            if rho == 1.0:
                continue
            current = np.asarray(arrays[_npz_key("continue", seed, rho, "B_final")], float)
            metrics = {
                "cross_T_cosine": cosine_edges(current, baseline),
                "cross_T_Jaccard": jaccard_edges(current, baseline, run.b_c),
                "cross_T_normalized_distance": normalized_distance(current, baseline),
            }
            if not all(np.isfinite(value) for value in metrics.values()):
                raise ArtifactIntegrityError(f"Nonfinite topology metric for seed={seed}, rho={rho}")
            rows.append({"seed": seed, "rho": rho, **metrics})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Saved-grid recovery semantics
# ---------------------------------------------------------------------------


def _validate_trajectory(times: np.ndarray, density: np.ndarray, similarity: np.ndarray, label: str) -> None:
    if times.shape != EXPECTED_SAMPLE_TIMES.shape or not np.array_equal(times, EXPECTED_SAMPLE_TIMES):
        raise ArtifactIntegrityError(f"{label} has an unexpected saved-time schedule")
    if density.shape != times.shape or similarity.shape != times.shape:
        raise ArtifactIntegrityError(f"{label} trajectory shapes do not agree")
    if not np.all(np.isfinite(density)) or np.any((density < 0.0) | (density > 1.0)):
        raise ArtifactIntegrityError(f"{label} density is nonfinite or outside [0,1]")
    if np.any(np.isinf(similarity)):
        raise ArtifactIntegrityError(f"{label} similarity contains Infinity")
    finite = similarity[np.isfinite(similarity)]
    if np.any((finite < -1.0 - 1e-12) | (finite > 1.0 + 1e-12)):
        raise ArtifactIntegrityError(f"{label} similarity is outside [-1,1]")


def _first_index(condition: np.ndarray) -> int | None:
    indices = np.flatnonzero(condition)
    return int(indices[0]) if len(indices) else None


def _sustained_index(condition: np.ndarray) -> int | None:
    suffix = np.logical_and.accumulate(condition[::-1])[::-1]
    return _first_index(suffix)


def _hold_tolerance(times: np.ndarray) -> float:
    """v4.1: end-check tolerance = 1e-6 x smallest positive saved-grid step (see module header)."""
    steps = np.diff(np.asarray(times, dtype=float))
    positive = steps[steps > 0.0]
    if len(positive) == 0:
        return 0.0
    return HOLD_TOLERANCE_FRACTION * float(positive.min())


def _run_end(condition: np.ndarray) -> np.ndarray:
    run_end = np.empty(len(condition), dtype=np.int64)
    end = -1
    for index in range(len(condition) - 1, -1, -1):
        if condition[index]:
            if index == len(condition) - 1 or not condition[index + 1]:
                end = index
            run_end[index] = end
        else:
            run_end[index] = index - 1
    return run_end


def _held_from(times: np.ndarray, run_end: np.ndarray, index: int, duration: float, tol: float) -> bool:
    # v4 used times[index] + duration (no tolerance); see module header.
    required_end = int(np.searchsorted(times, times[index] + duration - tol, side="left"))
    return required_end < len(times) and required_end <= run_end[index]


def _held_index(times: np.ndarray, condition: np.ndarray, duration: float) -> int | None:
    """Earliest saved index with a true run spanning at least ``duration``."""
    if not np.isfinite(duration) or duration <= 0.0:
        raise ValueError("Hold duration must be finite and positive")
    tol = _hold_tolerance(times)
    run_end = _run_end(condition)
    for index in np.flatnonzero(condition):
        if _held_from(times, run_end, int(index), duration, tol):
            return int(index)
    return None


def _held_retention_index(times: np.ndarray, condition: np.ndarray, duration: float) -> int | None:
    """0 if the condition holds from the first saved sample, without any drop,
    for at least ``duration``; otherwise None."""
    if not np.isfinite(duration) or duration <= 0.0:
        raise ValueError("Hold duration must be finite and positive")
    if len(condition) == 0 or not condition[0]:
        return None
    tol = _hold_tolerance(times)
    return 0 if _held_from(times, _run_end(condition), 0, duration, tol) else None


def _held_recovery_index(times: np.ndarray, condition: np.ndarray, duration: float) -> int | None:
    """Earliest index after the first drop (first False sample, including
    index 0) at which the condition re-crosses and is held for ``duration``."""
    if not np.isfinite(duration) or duration <= 0.0:
        raise ValueError("Hold duration must be finite and positive")
    dropped = np.flatnonzero(~np.asarray(condition, dtype=bool))
    if len(dropped) == 0:
        return None
    first_drop = int(dropped[0])
    tol = _hold_tolerance(times)
    run_end = _run_end(condition)
    for index in np.flatnonzero(condition):
        if index > first_drop and _held_from(times, run_end, int(index), duration, tol):
            return int(index)
    return None


def classify_held_event(times: np.ndarray, condition: np.ndarray, duration: float) -> str:
    """Mutually exclusive label: 'retention', 'recovery', or 'none'."""
    if _held_retention_index(times, condition, duration) is not None:
        return "retention"
    if _held_recovery_index(times, condition, duration) is not None:
        return "recovery"
    return "none"


def _event_row(
    *,
    seed: str,
    rho: float,
    t_window: float,
    branch: str,
    metric: str,
    target_definition: str,
    target_value: float,
    event_type: str,
    hold_system: str,
    hold_duration: float | None,
    event_index: int | None,
    imputed_count: int,
    held_classification: str = "not_applicable",
) -> dict[str, Any]:
    observed = event_index is not None
    event_time = float(EXPECTED_SAMPLE_TIMES[event_index]) if observed else float("nan")
    restricted = event_time if observed else SUPPORT_END
    lower = (
        0.0
        if observed and event_index == 0
        else float(EXPECTED_SAMPLE_TIMES[event_index - 1])
        if observed
        else float("nan")
    )
    upper = event_time if observed else float("nan")
    window_steps = int(round(t_window / 0.01))
    effective = window_steps * 0.01
    return {
        "seed": seed,
        "rho": rho,
        "T_window_nominal": t_window,
        "window_steps": window_steps,
        "T_window_effective": effective,
        "T_window_rounding_error": effective - t_window,
        "branch": branch,
        "metric": metric,
        "target_definition": target_definition,
        "target_value": target_value,
        "observation_support": "saved_grid_0p01_to_319p51",
        "support_start": SUPPORT_START,
        "support_end": SUPPORT_END,
        "sample_spacing": SAMPLE_SPACING,
        "event_type": event_type,
        "hold_duration_system": hold_system,
        "hold_duration": hold_duration,
        "held_classification": held_classification,
        "event_time_semantics": "first_qualifying_saved_sample_interval_censored",
        "event_time": event_time,
        "event_observed": bool(observed),
        "restricted_time": restricted,
        "event_time_over_Twindow": event_time / t_window if observed else float("nan"),
        "restricted_time_over_Twindow": restricted / t_window,
        "event_interval_lower": lower,
        "event_interval_upper": upper,
        "undefined_samples_imputed_zero": imputed_count,
        "undefined_similarity_convention": (
            "raw_NaN_to_zero_for_all_derived_recovery_metrics"
            if metric == "similarity"
            else "not_applicable"
        ),
    }


def _auc(times: np.ndarray, reference: np.ndarray, target: np.ndarray) -> float:
    deficit = np.maximum(0.0, reference - target)
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(deficit, x=times))
    return float(np.trapz(deficit, x=times))


def compute_recovery(run: ValidatedRun) -> tuple[pd.DataFrame, pd.DataFrame]:
    fields = ("sample_times", "density_trajectory", "similarity_trajectory")
    keys = [
        _npz_key(branch, seed, rho, field)
        for seed in run.seeds
        for rho in run.rho_values
        for branch in run.branches
        for field in fields
    ]
    arrays = load_npz_keys(run.inputs.branch_npz, keys)
    scalar = run.scalar.set_index(["seed", "rho", "branch"], verify_integrity=True)
    event_rows: list[dict[str, Any]] = []
    auc_rows: list[dict[str, Any]] = []

    for seed in run.seeds:
        for rho in run.rho_values:
            t_window = float(scalar.loc[(seed, rho, "continue"), "T_window"])
            density_target = 0.9 * float(scalar.loc[(seed, rho, "continue"), "D_B_final"])
            similarity_targets = (
                (
                    "similarity_90pct_continue_late_fixed_physical",
                    0.9
                    * float(
                        scalar.loc[
                            (seed, rho, "continue"),
                            "Weighted_similarity_late_fixed_physical",
                        ]
                    ),
                ),
                (
                    "similarity_90pct_continue_late_normalized_EMA",
                    0.9
                    * float(
                        scalar.loc[
                            (seed, rho, "continue"),
                            "Weighted_similarity_late_normalized_EMA",
                        ]
                    ),
                ),
            )
            cont_times = np.asarray(
                arrays[_npz_key("continue", seed, rho, "sample_times")], float
            )
            cont_density = np.asarray(
                arrays[_npz_key("continue", seed, rho, "density_trajectory")], float
            )
            cont_similarity_raw = np.asarray(
                arrays[_npz_key("continue", seed, rho, "similarity_trajectory")], float
            )
            _validate_trajectory(
                cont_times, cont_density, cont_similarity_raw, f"continue/{seed}/{rho}"
            )
            cont_similarity = np.nan_to_num(cont_similarity_raw, nan=0.0)

            for branch in run.branches:
                times = np.asarray(arrays[_npz_key(branch, seed, rho, "sample_times")], float)
                density = np.asarray(
                    arrays[_npz_key(branch, seed, rho, "density_trajectory")], float
                )
                similarity_raw = np.asarray(
                    arrays[_npz_key(branch, seed, rho, "similarity_trajectory")], float
                )
                _validate_trajectory(times, density, similarity_raw, f"{branch}/{seed}/{rho}")
                similarity = np.nan_to_num(similarity_raw, nan=0.0)
                undefined_count = int(np.isnan(similarity_raw).sum())

                metric_targets = (
                    (
                        "density",
                        density,
                        (("density_90pct_continue_final", density_target),),
                        0,
                    ),
                    ("similarity", similarity, similarity_targets, undefined_count),
                )
                for metric, values, targets, imputed_count in metric_targets:
                    for target_definition, target_value in targets:
                        if not np.isfinite(target_value):
                            raise ArtifactIntegrityError(
                                f"Nonfinite recovery target {target_definition} for {seed}/{rho}"
                            )
                        condition = values >= target_value
                        first = _first_index(condition)
                        sustained = _sustained_index(condition)
                        event_rows.append(
                            _event_row(
                                seed=seed,
                                rho=rho,
                                t_window=t_window,
                                branch=branch,
                                metric=metric,
                                target_definition=target_definition,
                                target_value=target_value,
                                event_type="first_crossing",
                                hold_system="not_applicable",
                                hold_duration=None,
                                event_index=first,
                                imputed_count=imputed_count,
                            )
                        )
                        event_rows.append(
                            _event_row(
                                seed=seed,
                                rho=rho,
                                t_window=t_window,
                                branch=branch,
                                metric=metric,
                                target_definition=target_definition,
                                target_value=target_value,
                                event_type="sustained_through_last_saved_observation",
                                hold_system="not_applicable",
                                hold_duration=None,
                                event_index=sustained,
                                imputed_count=imputed_count,
                            )
                        )
                        for hold_system, hold_duration in (
                            ("fixed_physical_17p5", FIXED_HOLD_DURATION),
                            ("one_current_Twindow_nominal", t_window),
                        ):
                            classification = classify_held_event(
                                times, condition, hold_duration
                            )
                            for event_type, held in (
                                ("held", _held_index(times, condition, hold_duration)),
                                (
                                    "held_retention",
                                    _held_retention_index(times, condition, hold_duration),
                                ),
                                (
                                    "held_recovery",
                                    _held_recovery_index(times, condition, hold_duration),
                                ),
                            ):
                                event_rows.append(
                                    _event_row(
                                        seed=seed,
                                        rho=rho,
                                        t_window=t_window,
                                        branch=branch,
                                        metric=metric,
                                        target_definition=target_definition,
                                        target_value=target_value,
                                        event_type=event_type,
                                        hold_system=hold_system,
                                        hold_duration=hold_duration,
                                        event_index=held,
                                        imputed_count=imputed_count,
                                        held_classification=classification,
                                    )
                                )

                for metric, reference, target, target_nan, reference_nan in (
                    ("density", cont_density, density, 0, 0),
                    (
                        "similarity",
                        cont_similarity,
                        similarity,
                        undefined_count,
                        int(np.isnan(cont_similarity_raw).sum()),
                    ),
                ):
                    auc_value = _auc(times, reference, target)
                    auc_rows.append(
                        {
                            "seed": seed,
                            "rho": rho,
                            "T_window_nominal": t_window,
                            "branch": branch,
                            "metric": metric,
                            "auc_definition": "one_sided_deficit_vs_same_condition_continue",
                            "observation_support": "saved_grid_0p01_to_319p51",
                            "support_start": SUPPORT_START,
                            "support_end": SUPPORT_END,
                            "support_width": SUPPORT_END - SUPPORT_START,
                            "auc_deficit": auc_value,
                            "auc_deficit_per_support_unit": auc_value
                            / (SUPPORT_END - SUPPORT_START),
                            "target_undefined_samples_imputed_zero": target_nan,
                            "reference_undefined_samples_imputed_zero": reference_nan,
                        }
                    )

    events = pd.DataFrame(event_rows)
    auc = pd.DataFrame(auc_rows)
    if len(events) != 19200:
        raise ArtifactIntegrityError(f"Recovery event row count {len(events)} != 19200")
    if len(auc) != 1600:
        raise ArtifactIntegrityError(f"Recovery AUC row count {len(auc)} != 1600")
    return events, auc


# ---------------------------------------------------------------------------
# Recovery interactions
# ---------------------------------------------------------------------------


def recovery_event_interactions(events: pd.DataFrame) -> pd.DataFrame:
    keys = [
        "seed",
        "rho",
        "branch",
        "metric",
        "target_definition",
        "event_type",
        "hold_duration_system",
    ]
    indexed = events.set_index(keys, verify_integrity=True)
    rows: list[dict[str, Any]] = []
    definitions = events[
        ["metric", "target_definition", "event_type", "hold_duration_system"]
    ].drop_duplicates()
    for seed in sorted(events["seed"].unique()):
        for rho in EXPECTED_RHO_VALUES:
            if rho == 1.0:
                continue
            for branch in NON_CONTINUE_BRANCHES:
                for definition in definitions.itertuples(index=False):
                    suffix = tuple(definition)
                    cells = {
                        "rho_branch": indexed.loc[(seed, rho, branch, *suffix)],
                        "rho_continue": indexed.loc[(seed, rho, "continue", *suffix)],
                        "base_branch": indexed.loc[(seed, 1.0, branch, *suffix)],
                        "base_continue": indexed.loc[(seed, 1.0, "continue", *suffix)],
                    }
                    restricted = {
                        name: float(value["restricted_time"]) for name, value in cells.items()
                    }
                    restricted_norm = {
                        name: float(value["restricted_time_over_Twindow"])
                        for name, value in cells.items()
                    }
                    observed = {
                        name: float(bool(value["event_observed"])) for name, value in cells.items()
                    }
                    complete = all(bool(value["event_observed"]) for value in cells.values())
                    raw = {
                        name: float(value["event_time"]) for name, value in cells.items()
                    }
                    raw_norm = {
                        name: float(value["event_time_over_Twindow"])
                        for name, value in cells.items()
                    }

                    def did(values: Mapping[str, float]) -> float:
                        return (values["rho_branch"] - values["rho_continue"]) - (
                            values["base_branch"] - values["base_continue"]
                        )

                    rows.append(
                        {
                            "seed": seed,
                            "rho": rho,
                            "branch": branch,
                            "metric": definition.metric,
                            "target_definition": definition.target_definition,
                            "event_type": definition.event_type,
                            "hold_duration_system": definition.hold_duration_system,
                            "rho_branch_restricted_time": restricted["rho_branch"],
                            "rho_continue_restricted_time": restricted["rho_continue"],
                            "baseline_branch_restricted_time": restricted["base_branch"],
                            "baseline_continue_restricted_time": restricted["base_continue"],
                            "restricted_branch_effect_rho": (
                                restricted["rho_branch"] - restricted["rho_continue"]
                            ),
                            "restricted_branch_effect_baseline": (
                                restricted["base_branch"] - restricted["base_continue"]
                            ),
                            "restricted_time_DID": did(restricted),
                            "restricted_time_over_Twindow_DID": did(restricted_norm),
                            "rho_branch_event_observed": bool(observed["rho_branch"]),
                            "rho_continue_event_observed": bool(observed["rho_continue"]),
                            "baseline_branch_event_observed": bool(observed["base_branch"]),
                            "baseline_continue_event_observed": bool(observed["base_continue"]),
                            "event_observed_DID": did(observed),
                            "four_cell_complete_case": complete,
                            "rho_branch_event_time": raw["rho_branch"],
                            "rho_continue_event_time": raw["rho_continue"],
                            "baseline_branch_event_time": raw["base_branch"],
                            "baseline_continue_event_time": raw["base_continue"],
                            "conditional_event_time_DID": did(raw) if complete else float("nan"),
                            "conditional_event_time_over_Twindow_DID": (
                                did(raw_norm) if complete else float("nan")
                            ),
                        }
                    )
    result = pd.DataFrame(rows)
    if len(result) != 11520:
        raise ArtifactIntegrityError(f"Recovery event DID row count {len(result)} != 11520")
    return result


def recovery_auc_interactions(auc: pd.DataFrame) -> pd.DataFrame:
    indexed = auc.set_index(["seed", "rho", "branch", "metric"], verify_integrity=True)
    rows = []
    for seed in sorted(auc["seed"].unique()):
        for rho in EXPECTED_RHO_VALUES:
            if rho == 1.0:
                continue
            for branch in NON_CONTINUE_BRANCHES:
                for metric in ("density", "similarity"):
                    values = {
                        "rho_branch": float(indexed.loc[(seed, rho, branch, metric), "auc_deficit"]),
                        "rho_continue": float(
                            indexed.loc[(seed, rho, "continue", metric), "auc_deficit"]
                        ),
                        "base_branch": float(
                            indexed.loc[(seed, 1.0, branch, metric), "auc_deficit"]
                        ),
                        "base_continue": float(
                            indexed.loc[(seed, 1.0, "continue", metric), "auc_deficit"]
                        ),
                    }
                    did = (values["rho_branch"] - values["rho_continue"]) - (
                        values["base_branch"] - values["base_continue"]
                    )
                    rows.append(
                        {
                            "seed": seed,
                            "rho": rho,
                            "branch": branch,
                            "metric": metric,
                            "rho_branch_auc_deficit": values["rho_branch"],
                            "rho_continue_auc_deficit": values["rho_continue"],
                            "baseline_branch_auc_deficit": values["base_branch"],
                            "baseline_continue_auc_deficit": values["base_continue"],
                            "auc_branch_effect_rho": (
                                values["rho_branch"] - values["rho_continue"]
                            ),
                            "auc_branch_effect_baseline": (
                                values["base_branch"] - values["base_continue"]
                            ),
                            "auc_deficit_DID": did,
                        }
                    )
    result = pd.DataFrame(rows)
    if len(result) != 960:
        raise ArtifactIntegrityError(f"Recovery AUC DID row count {len(result)} != 960")
    return result


# ---------------------------------------------------------------------------
# Joint seed bootstrap summaries
# ---------------------------------------------------------------------------


def bootstrap_draws(seeds: Sequence[str], iterations: int, seed: int) -> np.ndarray:
    if iterations <= 0:
        raise ValueError("Bootstrap iterations must be positive")
    rng = np.random.default_rng(seed)
    return rng.integers(0, len(seeds), size=(iterations, len(seeds)))


def _aligned_values(group: pd.DataFrame, value: str, seeds: Sequence[str]) -> np.ndarray:
    if group["seed"].duplicated().any():
        raise ArtifactIntegrityError("Summary group contains duplicate seeds")
    mapping = dict(zip(group["seed"], group[value], strict=True))
    return np.asarray([mapping.get(seed, float("nan")) for seed in seeds], dtype=float)


def pointwise_summary(
    frame: pd.DataFrame,
    *,
    group_columns: Sequence[str],
    value_column: str,
    seeds: Sequence[str],
    draws: np.ndarray,
) -> pd.DataFrame:
    rows = []
    for group_key, group in frame.groupby(list(group_columns), sort=True, dropna=False):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        values = _aligned_values(group, value_column, seeds)
        finite = np.isfinite(values)
        n = int(finite.sum())
        mean = float(np.mean(values[finite])) if n else float("nan")
        std = float(np.std(values[finite], ddof=1)) if n > 1 else float("nan")
        sampled = values[draws]
        counts = np.isfinite(sampled).sum(axis=1)
        means = np.divide(
            np.nansum(sampled, axis=1),
            counts,
            out=np.full(len(draws), np.nan),
            where=counts > 0,
        )
        finite_boot = means[np.isfinite(means)]
        lower = float(np.percentile(finite_boot, 2.5)) if len(finite_boot) else float("nan")
        upper = float(np.percentile(finite_boot, 97.5)) if len(finite_boot) else float("nan")
        included_seeds = [seed for seed, keep in zip(seeds, finite, strict=True) if keep]
        rows.append(
            {
                **dict(zip(group_columns, group_key, strict=True)),
                "estimand": value_column,
                "mean": mean,
                "std": std,
                "n": n,
                "pointwise_ci_lower": lower,
                "pointwise_ci_upper": upper,
                "interval_type": "joint-seed-resampling_pointwise_percentile_95pct",
                "included_seed_set_sha256": seed_set_sha256(included_seeds),
                "included_seed_fraction": n / len(seeds),
            }
        )
    return pd.DataFrame(rows)


def simultaneous_complete_summary(
    frame: pd.DataFrame,
    *,
    group_columns: Sequence[str],
    value_column: str,
    seeds: Sequence[str],
    draws: np.ndarray,
    family_id: str,
) -> pd.DataFrame:
    groups = []
    keys = []
    for key, group in frame.groupby(list(group_columns), sort=True, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        values = _aligned_values(group, value_column, seeds)
        if not np.all(np.isfinite(values)):
            raise ArtifactIntegrityError(f"Simultaneous family {family_id} is not full cohort")
        keys.append(key)
        groups.append(values)
    matrix = np.asarray(groups, dtype=float)
    means = matrix.mean(axis=1)
    std = matrix.std(axis=1, ddof=1)
    standard_error = std / math.sqrt(len(seeds))
    bootstrap_means = matrix[:, draws].mean(axis=2)
    point_lower = np.percentile(bootstrap_means, 2.5, axis=1)
    point_upper = np.percentile(bootstrap_means, 97.5, axis=1)
    denominators = np.where(standard_error > 0.0, standard_error, np.inf)
    max_t = np.max(np.abs((bootstrap_means - means[:, None]) / denominators[:, None]), axis=0)
    critical = float(np.percentile(max_t, 95.0))
    rows = []
    for index, key in enumerate(keys):
        rows.append(
            {
                **dict(zip(group_columns, key, strict=True)),
                "estimand": value_column,
                "mean": float(means[index]),
                "std": float(std[index]),
                "n": len(seeds),
                "pointwise_ci_lower": float(point_lower[index]),
                "pointwise_ci_upper": float(point_upper[index]),
                "simultaneous_ci_lower": float(means[index] - critical * standard_error[index]),
                "simultaneous_ci_upper": float(means[index] + critical * standard_error[index]),
                "simultaneous_family": family_id,
                "simultaneous_method": "joint-seed-bootstrap_max_t_95pct",
                "included_seed_set_sha256": seed_set_sha256(seeds),
            }
        )
    return pd.DataFrame(rows)


def recovery_summaries(
    events: pd.DataFrame,
    auc: pd.DataFrame,
    event_did: pd.DataFrame,
    auc_did: pd.DataFrame,
    seeds: Sequence[str],
    draws: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    event_groups = (
        "rho",
        "branch",
        "metric",
        "target_definition",
        "event_type",
        "hold_duration_system",
    )
    event_parts = [
        pointwise_summary(
            events,
            group_columns=event_groups,
            value_column=field,
            seeds=seeds,
            draws=draws,
        )
        for field in (
            "restricted_time",
            "restricted_time_over_Twindow",
            "event_observed",
            "event_time",
            "event_time_over_Twindow",
        )
    ]
    event_summary = pd.concat(event_parts, ignore_index=True)

    auc_parts = [
        pointwise_summary(
            auc,
            group_columns=("rho", "branch", "metric"),
            value_column=field,
            seeds=seeds,
            draws=draws,
        )
        for field in ("auc_deficit", "auc_deficit_per_support_unit")
    ]
    auc_summary = pd.concat(auc_parts, ignore_index=True)

    interaction_groups = (
        "rho",
        "branch",
        "metric",
        "target_definition",
        "event_type",
        "hold_duration_system",
    )
    interaction_parts = [
        pointwise_summary(
            event_did,
            group_columns=interaction_groups,
            value_column=field,
            seeds=seeds,
            draws=draws,
        )
        for field in (
            "restricted_time_DID",
            "restricted_time_over_Twindow_DID",
            "event_observed_DID",
            "conditional_event_time_DID",
            "conditional_event_time_over_Twindow_DID",
        )
    ]
    interaction_summary = pd.concat(interaction_parts, ignore_index=True)
    auc_interaction_summary = pointwise_summary(
        auc_did,
        group_columns=("rho", "branch", "metric"),
        value_column="auc_deficit_DID",
        seeds=seeds,
        draws=draws,
    )
    return event_summary, auc_summary, interaction_summary, auc_interaction_summary


# ---------------------------------------------------------------------------
# Report and bundle execution
# ---------------------------------------------------------------------------


def build_report(
    run: ValidatedRun,
    regime_summary: pd.DataFrame,
    did_summary: pd.DataFrame,
    topology_summary: pd.DataFrame,
    events: pd.DataFrame,
    event_did_summary: pd.DataFrame,
) -> str:
    complete_case = event_did_summary[
        event_did_summary["estimand"] == "conditional_event_time_DID"
    ]
    lines = [
        "=" * 80,
        "AIEF-1.4 T_window Sensitivity — Analysis v4.1 (CANDIDATE, UNAUDITED)",
        "=" * 80,
        "",
        "STATUS",
        "  Separately versioned reanalysis of the existing S01 raw trajectories.",
        "  No trajectories were regenerated.",
        "",
        "RECOVERY SEMANTICS",
        f"  Saved observation support: [{SUPPORT_START}, {SUPPORT_END}]",
        f"  Saved-grid spacing: {SAMPLE_SPACING}",
        "  Event times: first qualifying saved observation; interval-censored.",
        "  Undefined similarity: raw NaN, derived recovery representation uses zero.",
        "  Hold systems: fixed 17.5 units and one nominal current T_window.",
        "  Held end check: t + duration - 1e-6*dt (v4.1 fix of v4 rounding miss).",
        "  Held event types: held (any), held_retention, held_recovery.",
        "  AUC: one-sided deficit over saved support; not labelled full [0,320].",
        "",
        "INFERENCE",
        "  Seed/graph is the inferential unit.",
        "  One joint seed-resampling plan is reused across all estimands.",
        "  Primary regime, branch-DID, and topology families have max-t simultaneous bands.",
        "  Recovery intervals are pointwise; complete-case raw-event estimates are secondary.",
        "",
        "COUNTS",
        f"  Seeds: {len(run.seeds)}",
        f"  Regime summary groups: {len(regime_summary)}",
        f"  Branch-DID summary groups: {len(did_summary)}",
        f"  Topology summary groups: {len(topology_summary)}",
        f"  Recovery event rows: {len(events)}",
        f"  Conditional recovery-DID groups: {len(complete_case)}",
        "",
        "INTERPRETATION LIMITS",
        "  Exact step-level crossings and t=0/t=320 endpoint values are unavailable.",
        "  Analysis v3 remains the prespecified legacy-compatible analysis.",
        "  Analysis v4.1 is an unaudited candidate, not an independent experiment.",
        "",
        "=" * 80,
    ]
    return "\n".join(lines) + "\n"


def _write_bundle(
    *,
    run: ValidatedRun,
    frames: Mapping[str, pd.DataFrame],
    report: str,
    output_root: Path,
    bootstrap_seed: int,
    n_bootstrap: int,
    draws: np.ndarray,
    command_line: str,
) -> Path:
    execution_id = analysis_execution_id()
    version_root = output_root / "v4_1"
    version_root.mkdir(parents=True, exist_ok=True)
    final = version_root / execution_id
    staging = version_root / f".{execution_id}.tmp"
    failed = version_root / f"failed_{execution_id}"
    if final.exists() or staging.exists() or failed.exists():
        raise ArtifactIntegrityError("Analysis execution path collision")
    staging.mkdir()
    started = time.time()
    try:
        output_paths: dict[str, Path] = {}
        for filename, frame in frames.items():
            path = staging / filename
            save_dataframe_atomic(path, frame)
            output_paths[filename] = path
        report_path = staging / "twindow_sensitivity_report_v4_1.txt"
        atomic_write_text(report_path, report)
        output_paths[report_path.name] = report_path

        # Reopen every authoritative table before bundle promotion. This checks
        # logical readability, exact header order, and row cardinality rather
        # than relying only on successful writes and byte hashes.
        for filename, expected_frame in frames.items():
            observed_frame = pd.read_csv(staging / filename)
            if list(observed_frame.columns) != list(expected_frame.columns):
                raise ArtifactIntegrityError(f"Staged CSV header mismatch: {filename}")
            if len(observed_frame) != len(expected_frame):
                raise ArtifactIntegrityError(
                    f"Staged CSV row count mismatch for {filename}: "
                    f"{len(observed_frame)} != {len(expected_frame)}"
                )
        if report_path.read_text(encoding="utf-8") != report:
            raise ArtifactIntegrityError("Staged analysis report failed read-back validation")

        output_hashes = {
            filename: file_sha256(path) for filename, path in sorted(output_paths.items())
        }
        dependency_hashes = {
            "analysis_source": source_sha256(),
            "aief_modular.artifacts": file_sha256(Path(modular_artifacts.__file__)),
            "aief_modular.validation": file_sha256(Path(modular_validation.__file__)),
        }
        identity_payload = {
            "identity_schema": "aief-analysis-scientific-identity-v1",
            "analysis_id": ANALYSIS_ID,
            "analysis_version": ANALYSIS_VERSION,
            "dependency_hashes": dependency_hashes,
            "input_hashes": run.input_hashes,
            "ordered_seed_set_sha256": seed_set_sha256(run.seeds),
            "bootstrap": {
                "seed": bootstrap_seed,
                "iterations": n_bootstrap,
                "resampling": "same_seed_indices_reused_across_all_groups",
            },
            "analysis_contract": analysis_contract(),
        }
        manifest = {
            "analysis_manifest_schema": "aief-analysis-execution-manifest-v1",
            "analysis_id": ANALYSIS_ID,
            "analysis_version": ANALYSIS_VERSION,
            "analysis_execution_id": execution_id,
            "created_utc": utc_now(),
            "status": "completed",
            "analysis_identity_sha256": canonical_sha256(identity_payload),
            "analysis_identity_payload": identity_payload,
            "dependency_hashes": dependency_hashes,
            "source_sha256": dependency_hashes["analysis_source"],
            "command_line": command_line,
            "input_run": {
                "path_recorded_for_provenance": str(run.inputs.run_dir),
                "input_hashes": run.input_hashes,
                "simulation_run_id": run.manifest.get("run_id"),
                "simulation_spec_sha256": run.manifest.get("spec_sha256"),
            },
            "cohort": {
                "seed_count": len(run.seeds),
                "ordered_seed_set_sha256": seed_set_sha256(run.seeds),
                "rho_values": list(run.rho_values),
                "branches": list(run.branches),
                "inferential_unit": "paired_seed_graph",
            },
            "bootstrap": {
                "seed": bootstrap_seed,
                "iterations": n_bootstrap,
                "draw_matrix_sha256": hashlib.sha256(
                    np.ascontiguousarray(draws, dtype=np.int64).tobytes()
                ).hexdigest(),
                "resampling": "same_seed_indices_reused_across_all_groups",
                "pointwise_method": "percentile_95pct",
                "primary_simultaneous_method": "max_t_95pct",
            },
            "analysis_contract": analysis_contract(),
            "output_hashes": output_hashes,
            "elapsed_seconds": time.time() - started,
            "environment": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "pandas": pd.__version__,
                "platform": platform.platform(),
            },
        }
        manifest_path = staging / "analysis_manifest.json"
        atomic_write_json(manifest_path, manifest)
        with open(manifest_path, "r", encoding="utf-8") as handle:
            observed_manifest = json.load(handle)
        if observed_manifest.get("analysis_identity_sha256") != canonical_sha256(identity_payload):
            raise ArtifactIntegrityError("Staged analysis manifest identity failed read-back")
        for filename, expected_hash in output_hashes.items():
            if file_sha256(staging / filename) != expected_hash:
                raise ArtifactIntegrityError(f"Staged output hash changed before promotion: {filename}")
        _fsync_directory(staging)
        os.replace(staging, final)
        _fsync_directory(version_root)
        return final
    except Exception as exc:
        failure = {
            "analysis_id": ANALYSIS_ID,
            "analysis_execution_id": execution_id,
            "status": "failed",
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
            "created_utc": utc_now(),
        }
        try:
            atomic_write_json(staging / "FAILED_analysis_manifest.json", failure)
            _fsync_directory(staging)
            os.replace(staging, failed)
            _fsync_directory(version_root)
        except Exception:
            pass
        raise


def run_analysis(
    run_dir: str | Path,
    *,
    output_root: str | Path | None,
    bootstrap_seed: int,
    n_bootstrap: int,
    command_line: str,
) -> Path:
    run = validate_run(discover_inputs(run_dir))
    draws = bootstrap_draws(run.seeds, n_bootstrap, bootstrap_seed)

    regime = pd.concat(
        [
            regime_contrasts(run.scalar, PRIMARY_OUTCOMES, "fixed_physical"),
            regime_contrasts(run.scalar, SECONDARY_OUTCOMES, "normalized_EMA"),
        ],
        ignore_index=True,
    )
    branch_did = pd.concat(
        [
            branch_interactions(run.scalar, PRIMARY_OUTCOMES, "fixed_physical"),
            branch_interactions(run.scalar, SECONDARY_OUTCOMES, "normalized_EMA"),
        ],
        ignore_index=True,
    )
    topology = cross_t_topology(run)
    if len(regime) != 960:
        raise ArtifactIntegrityError(f"Regime contrast row count {len(regime)} != 960")
    if len(branch_did) != 2880:
        raise ArtifactIntegrityError(f"Branch DID row count {len(branch_did)} != 2880")
    if len(topology) != 160:
        raise ArtifactIntegrityError(f"Topology row count {len(topology)} != 160")

    events, auc = compute_recovery(run)
    event_did = recovery_event_interactions(events)
    auc_did = recovery_auc_interactions(auc)

    regime_summary = pd.concat(
        [
            simultaneous_complete_summary(
                regime.loc[regime["target_system"] == system],
                group_columns=("rho", "target_system", "outcome"),
                value_column="paired_regime_contrast",
                seeds=run.seeds,
                draws=draws,
                family_id=(
                    "primary_regime_fixed_physical"
                    if system == "fixed_physical"
                    else "secondary_regime_normalized_EMA"
                ),
            )
            for system in ("fixed_physical", "normalized_EMA")
        ],
        ignore_index=True,
    )
    did_summary = pd.concat(
        [
            simultaneous_complete_summary(
                branch_did.loc[branch_did["target_system"] == system],
                group_columns=("rho", "branch", "target_system", "outcome"),
                value_column="difference_in_differences",
                seeds=run.seeds,
                draws=draws,
                family_id=(
                    "primary_branch_DID_fixed_physical"
                    if system == "fixed_physical"
                    else "secondary_branch_DID_normalized_EMA"
                ),
            )
            for system in ("fixed_physical", "normalized_EMA")
        ],
        ignore_index=True,
    )
    topology_long = topology.melt(
        id_vars=("seed", "rho"), var_name="topology_metric", value_name="topology_value"
    )
    topology_summary = simultaneous_complete_summary(
        topology_long,
        group_columns=("rho", "topology_metric"),
        value_column="topology_value",
        seeds=run.seeds,
        draws=draws,
        family_id="cross_T_topology",
    )
    (
        event_summary,
        auc_summary,
        event_did_summary,
        auc_did_summary,
    ) = recovery_summaries(events, auc, event_did, auc_did, run.seeds, draws)
    expected_summary_counts = {
        "regime": (len(regime_summary), 24),
        "branch_DID": (len(did_summary), 72),
        "topology": (len(topology_summary), 12),
        "recovery_event": (len(event_summary), 2400),
        "recovery_AUC": (len(auc_summary), 80),
        "recovery_event_DID": (len(event_did_summary), 1440),
        "recovery_AUC_DID": (len(auc_did_summary), 24),
    }
    for label, (observed, expected) in expected_summary_counts.items():
        if observed != expected:
            raise ArtifactIntegrityError(
                f"{label} summary row count {observed} != {expected}"
            )

    report = build_report(
        run, regime_summary, did_summary, topology_summary, events, event_did_summary
    )
    frames = {
        "twindow_paired_regime_contrasts_v4_1.csv": regime,
        "twindow_branch_interactions_v4_1.csv": branch_did,
        "twindow_cross_condition_topology_v4_1.csv": topology,
        "twindow_recovery_events_by_seed_v4_1.csv": events,
        "twindow_recovery_auc_by_seed_v4_1.csv": auc,
        "twindow_recovery_event_interactions_v4_1.csv": event_did,
        "twindow_recovery_auc_interactions_v4_1.csv": auc_did,
        "twindow_regime_summary_v4_1.csv": regime_summary,
        "twindow_branch_DID_summary_v4_1.csv": did_summary,
        "twindow_topology_summary_v4_1.csv": topology_summary,
        "twindow_recovery_event_summary_v4_1.csv": event_summary,
        "twindow_recovery_auc_summary_v4_1.csv": auc_summary,
        "twindow_recovery_event_interaction_summary_v4_1.csv": event_did_summary,
        "twindow_recovery_auc_interaction_summary_v4_1.csv": auc_did_summary,
    }
    root = Path(output_root) if output_root is not None else Path(run_dir) / "analysis"
    return _write_bundle(
        run=run,
        frames=frames,
        report=report,
        output_root=root,
        bootstrap_seed=bootstrap_seed,
        n_bootstrap=n_bootstrap,
        draws=draws,
        command_line=command_line,
    )


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", help="completed freezeable S01 run directory")
    parser.add_argument(
        "--output-root",
        default=None,
        help="analysis root (default: <run_dir>/analysis)",
    )
    parser.add_argument("--bootstrap-seed", required=True, type=int)
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    parser.add_argument(
        "--allow-unaudited-candidate",
        action="store_true",
        help="required: acknowledge v4.1 is an unaudited candidate",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_arguments(argv)
    if not args.allow_unaudited_candidate:
        print(
            "Analysis v4.1 is an UNAUDITED CANDIDATE; refusing to run without "
            "--allow-unaudited-candidate. Do not run on real trajectories.",
            file=sys.stderr,
        )
        return 2
    if args.n_bootstrap <= 0:
        raise ValueError("--n-bootstrap must be positive")
    final = run_analysis(
        args.run_dir,
        output_root=args.output_root,
        bootstrap_seed=args.bootstrap_seed,
        n_bootstrap=args.n_bootstrap,
        command_line=" ".join(sys.argv),
    )
    print(f"Analysis v4.1 candidate bundle: {final}")
    print(f"Manifest: {final / 'analysis_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
