#!/usr/bin/env python3
"""Freeze-grade closure diagnostics for the two AIEF-1.3 validation cohorts.

The scientific persistence object is the set of unique undirected off-diagonal
edges. Full-matrix checks are also performed as storage/model invariants.

Checks
------
* Expected conditions and seed coverage in scalar CSV and aggregate NPZ.
* No cross-cohort seed overlap unless explicitly allowed.
* Baseline P_future shape, finiteness, symmetry, diagonal, and binary status.
* Exact and tolerance-based binary checks on unique edges and full matrices.
* Per-seed and pooled exact P_future value tables.
* Matrix-derived persistence metrics versus scalar CSV values.
* Projection/gap validity, frequency, magnitude, and conditional activity.
* Machine-readable closure status.

Default inputs are the two independent 50-seed validation cohorts.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_COHORTS = (
    (
        "validation_A",
        "/home/deck/AI_Programs/SSRH/runs/c3da1ac707bf/AIEF_1_3_c3da1ac707bf_scalar_summary.csv",
        "/home/deck/AI_Programs/SSRH/runs/c3da1ac707bf/AIEF_1_3_c3da1ac707bf_edge_diagnostics.npz",
    ),
    (
        "validation_B",
        "/home/deck/AI_Programs/SSRH/runs/73dca37cf93f/AIEF_1_3_73dca37cf93f_scalar_summary.csv",
        "/home/deck/AI_Programs/SSRH/runs/73dca37cf93f/AIEF_1_3_73dca37cf93f_edge_diagnostics.npz",
    ),
)

EXPECTED_CONDITIONS = (
    "baseline",
    "shuffle_R",
    "no_delay",
    "no_mu",
    "no_gap",
)

PROJECTION_COLUMNS = (
    "Pre_gap_violation_fraction",
    "Projection_active_fraction",
    "Projection_norm_mean_active",
    "Projection_norm_max",
    "G_min_pre_over_time",
    "G_min_over_time",
)

PERSISTENCE_SCALAR_COLUMNS = (
    "P_mean",
    "P_variance",
    "P_max",
    "P_nonzero_fraction",
    "P_degenerate",
)

DEFAULT_EXPECTED_SEEDS = 50
DEFAULT_OUTPUT_DIR = "aief_1_3_closure_diagnostics"
DEFAULT_BINARY_ATOL = 1e-12
DEFAULT_MATRIX_ATOL = 1e-12
DEFAULT_CONSISTENCY_ATOL = 1e-12
EXACT_ZERO_TOL = 0.0

PROJECTION_REPORT_LABELS = {
    "Pre_gap_violation_fraction": "pre-gap violation fraction",
    "Projection_active_fraction": "active projection fraction",
    "Projection_active_given_violation": "projection active given violation",
    "Projection_norm_mean_active": "mean active projection magnitude (Frobenius norm)",
    "Projection_norm_max": "maximum projection magnitude (Frobenius norm)",
    "G_min_pre_over_time": "minimum pre-projection gap",
    "G_min_over_time": "minimum post-projection gap",
}


# ---------------------------------------------------------------------------
# Parsing and scalar helpers
# ---------------------------------------------------------------------------


def parse_cohort(value: str) -> tuple[str, str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            "cohort must be LABEL=SCALAR_CSV,EDGE_NPZ"
        )
    label, remainder = value.split("=", 1)
    paths = remainder.split(",", 1)
    if len(paths) != 2:
        raise argparse.ArgumentTypeError(
            "cohort must include scalar CSV and edge NPZ separated by a comma"
        )
    label = label.strip()
    scalar_path = paths[0].strip()
    edge_path = paths[1].strip()
    if not label or not scalar_path or not edge_path:
        raise argparse.ArgumentTypeError("cohort fields must be nonempty")
    return label, scalar_path, edge_path


def parse_npz_key(key: str) -> tuple[str, str, str]:
    if "_seed_" not in key:
        raise ValueError(f"unexpected NPZ key format: {key}")
    condition, remainder = key.split("_seed_", 1)
    if "_" not in remainder:
        raise ValueError(f"unexpected NPZ key format: {key}")
    seed, metric = remainder.split("_", 1)
    if not condition or not seed or not metric:
        raise ValueError(f"unexpected NPZ key format: {key}")
    return condition, seed, metric


def to_bool(value: Any) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "1"}:
        return True
    if text in {"false", "0"}:
        return False
    raise ValueError(f"cannot parse boolean value {value!r}")


def numeric_or_nan(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return np.nan
    return number


def binary_masks(values: np.ndarray, atol: float) -> dict[str, np.ndarray]:
    values = np.asarray(values, dtype=float)
    exact_zero = values == 0.0
    exact_one = values == 1.0
    tolerant_zero = np.isclose(values, 0.0, rtol=0.0, atol=atol)
    tolerant_one = np.isclose(values, 1.0, rtol=0.0, atol=atol)
    return {
        "exact_zero": exact_zero,
        "exact_one": exact_one,
        "exact_binary": exact_zero | exact_one,
        "tolerant_zero": tolerant_zero,
        "tolerant_one": tolerant_one,
        "tolerant_binary": tolerant_zero | tolerant_one,
    }


def max_binary_distance(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return np.nan
    return float(np.max(np.minimum(np.abs(values), np.abs(values - 1.0))))


# ---------------------------------------------------------------------------
# Cohort loading and coverage
# ---------------------------------------------------------------------------


def load_scalar_cohort(
    label: str,
    scalar_path: str,
    expected_seeds: int,
) -> tuple[pd.DataFrame, list[dict[str, object]], set[str], list[str]]:
    if not os.path.isfile(scalar_path):
        raise FileNotFoundError(scalar_path)

    frame = pd.read_csv(scalar_path, dtype={"seed": str})
    required = {
        "condition",
        "seed",
        *PROJECTION_COLUMNS,
        *PERSISTENCE_SCALAR_COLUMNS,
    }
    missing_columns = required - set(frame.columns)
    if missing_columns:
        raise ValueError(f"{label}: scalar CSV missing {sorted(missing_columns)}")

    frame["condition"] = frame["condition"].astype(str)
    frame["seed"] = frame["seed"].astype(str)
    frame["cohort"] = label

    duplicate = frame.duplicated(["condition", "seed"], keep=False)
    if duplicate.any():
        rows = frame.loc[duplicate, ["condition", "seed"]]
        raise ValueError(f"{label}: duplicate condition/seed rows:\n{rows}")

    conditions = set(frame["condition"])
    missing_conditions = sorted(set(EXPECTED_CONDITIONS) - conditions)
    extra_conditions = sorted(conditions - set(EXPECTED_CONDITIONS))

    baseline_seeds = set(
        frame.loc[frame["condition"] == "baseline", "seed"].astype(str)
    )
    coverage_rows: list[dict[str, object]] = []
    warnings: list[str] = []

    if missing_conditions:
        warnings.append(f"missing conditions: {missing_conditions}")
    if extra_conditions:
        warnings.append(f"unexpected conditions: {extra_conditions}")
    if len(baseline_seeds) != expected_seeds:
        warnings.append(
            f"baseline scalar seed count {len(baseline_seeds)} != {expected_seeds}"
        )

    for condition in EXPECTED_CONDITIONS:
        condition_seeds = set(
            frame.loc[frame["condition"] == condition, "seed"].astype(str)
        )
        coverage_rows.append(
            {
                "cohort": label,
                "condition": condition,
                "scalar_seed_count": int(len(condition_seeds)),
                "expected_seed_count": int(expected_seeds),
                "scalar_count_ok": bool(len(condition_seeds) == expected_seeds),
                "scalar_seed_set_matches_baseline": bool(
                    condition_seeds == baseline_seeds
                ),
                "scalar_missing_vs_baseline": int(
                    len(baseline_seeds - condition_seeds)
                ),
                "scalar_extra_vs_baseline": int(
                    len(condition_seeds - baseline_seeds)
                ),
            }
        )
        if condition_seeds != baseline_seeds:
            warnings.append(f"{condition}: scalar seed set differs from baseline")

    return frame, coverage_rows, baseline_seeds, warnings


def index_persistence_matrices(
    label: str,
    edge_path: str,
) -> dict[str, dict[str, str]]:
    """Return condition -> seed -> key for every P_future matrix."""
    if not os.path.isfile(edge_path):
        raise FileNotFoundError(edge_path)

    indexed: dict[str, dict[str, str]] = {
        condition: {} for condition in EXPECTED_CONDITIONS
    }
    with np.load(edge_path, allow_pickle=False) as data:
        for key in data.files:
            if "_seed_" not in key:
                continue
            condition, seed, metric = parse_npz_key(key)
            if metric != "P_future" or condition not in indexed:
                continue
            if seed in indexed[condition]:
                raise ValueError(
                    f"{label}: duplicate P_future key for {condition}, seed={seed}"
                )
            indexed[condition][seed] = key
    return indexed


# ---------------------------------------------------------------------------
# Persistence matrix auditing
# ---------------------------------------------------------------------------


def audit_baseline_persistence(
    label: str,
    edge_path: str,
    indexed_keys: dict[str, dict[str, str]],
    scalar_frame: pd.DataFrame,
    *,
    binary_atol: float,
    matrix_atol: float,
    consistency_atol: float,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    matrix_rows: list[dict[str, object]] = []
    unique_rows: list[dict[str, object]] = []
    consistency_rows: list[dict[str, object]] = []

    scalar_baseline = scalar_frame.loc[
        scalar_frame["condition"] == "baseline"
    ].set_index("seed")

    with np.load(edge_path, allow_pickle=False) as data:
        for seed, key in sorted(
            indexed_keys["baseline"].items(), key=lambda item: int(item[0])
        ):
            matrix = np.asarray(data[key], dtype=float)
            square = bool(matrix.ndim == 2 and matrix.shape[0] == matrix.shape[1])
            if not square:
                matrix_rows.append(
                    {
                        "cohort": label,
                        "seed": seed,
                        "matrix_square": False,
                        "matrix_finite": False,
                    }
                )
                continue

            finite = bool(np.all(np.isfinite(matrix)))
            n = matrix.shape[0]
            edges = np.triu_indices(n, k=1)
            edge_values = matrix[edges]
            full_values = matrix.ravel()
            diagonal = np.diag(matrix)

            edge_masks = binary_masks(edge_values, binary_atol)
            full_masks = binary_masks(full_values, binary_atol)
            diagonal_masks = binary_masks(diagonal, binary_atol)

            symmetric = bool(
                finite
                and np.allclose(matrix, matrix.T, rtol=0.0, atol=matrix_atol)
            )
            diagonal_exact_zero = bool(np.all(diagonal == 0.0))
            diagonal_tolerant_zero = bool(
                np.all(np.isclose(diagonal, 0.0, rtol=0.0, atol=matrix_atol))
            )

            row = {
                "cohort": label,
                "seed": seed,
                "matrix_size": int(n),
                "n_unique_edges": int(len(edge_values)),
                "matrix_square": square,
                "matrix_finite": finite,
                "matrix_symmetric": symmetric,
                "diagonal_exact_zero": diagonal_exact_zero,
                "diagonal_tolerant_zero": diagonal_tolerant_zero,
                "diagonal_exact_binary": bool(np.all(diagonal_masks["exact_binary"])),
                "unique_edges_exact_binary": bool(
                    np.all(edge_masks["exact_binary"])
                ),
                "unique_edges_tolerant_binary": bool(
                    np.all(edge_masks["tolerant_binary"])
                ),
                "full_matrix_exact_binary": bool(
                    np.all(full_masks["exact_binary"])
                ),
                "full_matrix_tolerant_binary": bool(
                    np.all(full_masks["tolerant_binary"])
                ),
                "n_edge_zero_exact": int(np.sum(edge_masks["exact_zero"])),
                "n_edge_one_exact": int(np.sum(edge_masks["exact_one"])),
                "n_edge_intermediate_exact": int(
                    np.sum(~edge_masks["exact_binary"])
                ),
                "n_edge_intermediate_tolerant": int(
                    np.sum(~edge_masks["tolerant_binary"])
                ),
                "max_unique_edge_distance_to_binary": max_binary_distance(
                    edge_values
                ),
                "P_min": float(np.min(edge_values)),
                "P_max_recomputed": float(np.max(edge_values)),
                "P_mean_recomputed": float(np.mean(edge_values)),
                "P_variance_recomputed": float(np.var(edge_values)),
                "P_nonzero_fraction_recomputed": float(
                    np.mean(edge_values > 0.0)
                ),
                "P_degenerate_recomputed": bool(
                    np.std(edge_values) < consistency_atol
                ),
            }
            matrix_rows.append(row)

            unique, counts = np.unique(edge_values, return_counts=True)
            for value, count in zip(unique, counts):
                unique_rows.append(
                    {
                        "cohort": label,
                        "seed": seed,
                        "P_value": float(value),
                        "P_value_repr": format(float(value), ".17g"),
                        "count": int(count),
                    }
                )

            if seed not in scalar_baseline.index:
                for metric in PERSISTENCE_SCALAR_COLUMNS:
                    consistency_rows.append(
                        {
                            "cohort": label,
                            "seed": seed,
                            "metric": metric,
                            "matrix_value": np.nan,
                            "scalar_value": np.nan,
                            "absolute_difference": np.nan,
                            "matches": False,
                            "status": "scalar_seed_missing",
                        }
                    )
                continue

            scalar_row = scalar_baseline.loc[seed]
            recomputed = {
                "P_mean": row["P_mean_recomputed"],
                "P_variance": row["P_variance_recomputed"],
                "P_max": row["P_max_recomputed"],
                "P_nonzero_fraction": row[
                    "P_nonzero_fraction_recomputed"
                ],
                "P_degenerate": row["P_degenerate_recomputed"],
            }
            for metric, matrix_value in recomputed.items():
                scalar_value = scalar_row[metric]
                if metric == "P_degenerate":
                    try:
                        parsed_scalar = to_bool(scalar_value)
                        matches = bool(parsed_scalar == bool(matrix_value))
                        difference = 0.0 if matches else 1.0
                        status = "ok" if matches else "mismatch"
                    except ValueError:
                        parsed_scalar = np.nan
                        matches = False
                        difference = np.nan
                        status = "invalid_scalar_boolean"
                else:
                    parsed_scalar = numeric_or_nan(scalar_value)
                    matches = bool(
                        np.isfinite(parsed_scalar)
                        and np.isclose(
                            float(matrix_value),
                            parsed_scalar,
                            rtol=0.0,
                            atol=consistency_atol,
                        )
                    )
                    difference = (
                        abs(float(matrix_value) - parsed_scalar)
                        if np.isfinite(parsed_scalar)
                        else np.nan
                    )
                    status = "ok" if matches else "mismatch_or_invalid"

                consistency_rows.append(
                    {
                        "cohort": label,
                        "seed": seed,
                        "metric": metric,
                        "matrix_value": matrix_value,
                        "scalar_value": parsed_scalar,
                        "absolute_difference": difference,
                        "matches": matches,
                        "status": status,
                    }
                )

    return matrix_rows, unique_rows, consistency_rows


# ---------------------------------------------------------------------------
# Projection diagnostics
# ---------------------------------------------------------------------------


def add_projection_conditionals(
    frame: pd.DataFrame,
    tolerance: float,
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    frame = frame.copy()
    pre = pd.to_numeric(
        frame["Pre_gap_violation_fraction"], errors="coerce"
    ).to_numpy(float)
    active = pd.to_numeric(
        frame["Projection_active_fraction"], errors="coerce"
    ).to_numpy(float)

    ratio = np.full(len(frame), np.nan, dtype=float)
    finite = np.isfinite(pre) & np.isfinite(active)
    positive_pre = finite & (pre > tolerance)
    ratio[positive_pre] = active[positive_pre] / pre[positive_pre]
    frame["Projection_active_given_violation"] = ratio

    rows: list[dict[str, object]] = []
    for index, source_row in frame.iterrows():
        pre_value = numeric_or_nan(source_row["Pre_gap_violation_fraction"])
        active_value = numeric_or_nan(source_row["Projection_active_fraction"])
        valid = bool(np.isfinite(pre_value) and np.isfinite(active_value))
        subset_ok = bool(valid and active_value <= pre_value + tolerance)
        rows.append(
            {
                "cohort": source_row["cohort"],
                "condition": source_row["condition"],
                "seed": source_row["seed"],
                "Pre_gap_violation_fraction": pre_value,
                "Projection_active_fraction": active_value,
                "Projection_active_given_violation": frame.loc[
                    index, "Projection_active_given_violation"
                ],
                "fractions_finite": valid,
                "active_not_greater_than_violation": subset_ok,
            }
        )
    return frame, rows


def projection_summary(frame: pd.DataFrame, zero_atol: float) -> pd.DataFrame:
    metrics = (*PROJECTION_COLUMNS, "Projection_active_given_violation")
    rows: list[dict[str, object]] = []

    def add_group(cohort: str, condition: str, group: pd.DataFrame) -> None:
        for metric in metrics:
            raw = pd.to_numeric(group[metric], errors="coerce").to_numpy(float)
            valid = np.isfinite(raw)
            values = raw[valid]
            rows.append(
                {
                    "cohort": cohort,
                    "condition": condition,
                    "metric": metric,
                    "display_label": PROJECTION_REPORT_LABELS.get(metric, metric),
                    "n_total": int(len(raw)),
                    "n_valid": int(np.sum(valid)),
                    "n_invalid": int(np.sum(~valid)),
                    "invalid_fraction": float(np.mean(~valid)) if len(raw) else np.nan,
                    "mean": float(np.mean(values)) if len(values) else np.nan,
                    "std": float(np.std(values)) if len(values) else np.nan,
                    "median": float(np.median(values)) if len(values) else np.nan,
                    "minimum": float(np.min(values)) if len(values) else np.nan,
                    "maximum": float(np.max(values)) if len(values) else np.nan,
                    "fraction_zero": float(
                        np.mean(np.isclose(values, 0.0, rtol=0.0, atol=zero_atol))
                    )
                    if len(values)
                    else np.nan,
                    "fraction_nonzero": float(
                        np.mean(~np.isclose(values, 0.0, rtol=0.0, atol=zero_atol))
                    )
                    if len(values)
                    else np.nan,
                }
            )

    for (cohort, condition), group in frame.groupby(["cohort", "condition"]):
        add_group(str(cohort), str(condition), group)
    for condition, group in frame.groupby("condition"):
        add_group("pooled", str(condition), group)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Closure report/status
# ---------------------------------------------------------------------------


def build_closure_status(
    *,
    coverage: pd.DataFrame,
    matrix_audit: pd.DataFrame,
    consistency: pd.DataFrame,
    projection: pd.DataFrame,
    projection_consistency: pd.DataFrame,
    overlap: pd.DataFrame,
    allow_seed_overlap: bool,
    expected_cohort_count: int,
    actual_cohort_count: int,
) -> dict[str, Any]:
    checks = {
        "expected_cohort_count": bool(actual_cohort_count == expected_cohort_count),
        "seed_coverage_complete": bool(
            coverage["scalar_count_ok"].all()
            and coverage["scalar_seed_set_matches_baseline"].all()
            and coverage["npz_count_ok"].all()
            and coverage["npz_seed_set_matches_scalar"].all()
        ),
        "cohorts_seed_disjoint": bool(
            allow_seed_overlap or (overlap["overlap_count"] == 0).all()
        ),
        "baseline_matrices_square_and_finite": bool(
            matrix_audit["matrix_square"].all()
            and matrix_audit["matrix_finite"].all()
        ),
        "baseline_matrices_symmetric": bool(
            matrix_audit["matrix_symmetric"].all()
        ),
        "baseline_diagonal_exact_zero": bool(
            matrix_audit["diagonal_exact_zero"].all()
        ),
        "baseline_unique_edges_exact_binary": bool(
            matrix_audit["unique_edges_exact_binary"].all()
        ),
        "baseline_unique_edges_tolerant_binary": bool(
            matrix_audit["unique_edges_tolerant_binary"].all()
        ),
        "baseline_full_matrix_exact_binary": bool(
            matrix_audit["full_matrix_exact_binary"].all()
        ),
        "matrix_scalar_consistent": bool(consistency["matches"].all()),
        "projection_metrics_all_finite": bool(
            (projection.loc[
                projection["metric"] != "Projection_active_given_violation",
                "n_invalid",
            ]
            == 0).all()
        ),
        "projection_activity_subset_of_violation": bool(
            projection_consistency[
                "active_not_greater_than_violation"
            ].all()
        ),
    }
    return {
        "closure_passed": bool(all(checks.values())),
        "checks": checks,
        "counts": {
            "cohorts": int(actual_cohort_count),
            "baseline_matrices": int(len(matrix_audit)),
            "matrix_scalar_checks": int(len(consistency)),
            "projection_summary_rows": int(len(projection)),
        },
    }


def make_report(
    status: dict[str, Any],
    coverage: pd.DataFrame,
    matrix_audit: pd.DataFrame,
    projection: pd.DataFrame,
    overlap: pd.DataFrame,
) -> str:
    lines = [
        "AIEF-1.3 freeze-grade closure diagnostics",
        "==========================================",
        "",
        f"CLOSURE PASSED: {status['closure_passed']}",
        "",
        "Closure checks",
        "--------------",
    ]
    for name, value in status["checks"].items():
        lines.append(f"  {name}: {value}")

    lines.extend(["", "Seed and artifact coverage", "--------------------------"])
    for _, row in coverage.iterrows():
        lines.append(
            f"  {row['cohort']} / {row['condition']}: "
            f"scalar={int(row['scalar_seed_count'])}, "
            f"P_future={int(row['npz_P_future_count'])}, "
            f"complete={bool(row['coverage_complete'])}"
        )

    lines.extend(["", "Cross-cohort seed overlap", "-------------------------"])
    for _, row in overlap.iterrows():
        lines.append(
            f"  {row['cohort_a']} vs {row['cohort_b']}: "
            f"overlap={int(row['overlap_count'])}"
        )

    lines.extend(["", "Baseline P_future audit", "-----------------------"])
    for cohort, group in matrix_audit.groupby("cohort"):
        lines.append(
            f"  {cohort}: seeds={len(group)}, "
            f"exact_binary={bool(group['unique_edges_exact_binary'].all())}, "
            f"tolerant_binary={bool(group['unique_edges_tolerant_binary'].all())}, "
            f"intermediate_exact={int(group['n_edge_intermediate_exact'].sum())}, "
            f"full_matrix_binary={bool(group['full_matrix_exact_binary'].all())}, "
            f"symmetric={bool(group['matrix_symmetric'].all())}, "
            f"diagonal_zero={bool(group['diagonal_exact_zero'].all())}"
        )

    lines.extend(["", "Projection/gap diagnostics (pooled)", "-----------------------------------"])
    pooled = projection.loc[projection["cohort"] == "pooled"]
    metric_order = (
        "Pre_gap_violation_fraction",
        "Projection_active_fraction",
        "Projection_active_given_violation",
        "Projection_norm_mean_active",
        "Projection_norm_max",
        "G_min_pre_over_time",
        "G_min_over_time",
    )
    for condition in EXPECTED_CONDITIONS:
        lines.append(f"  {condition}")
        block = pooled.loc[pooled["condition"] == condition]
        for metric in metric_order:
            row_set = block.loc[block["metric"] == metric]
            if row_set.empty:
                lines.append(f"    {metric}: MISSING")
                continue
            row = row_set.iloc[0]
            lines.append(
                f"    {row['display_label']}: mean={row['mean']:.9g}, "
                f"median={row['median']:.9g}, max={row['maximum']:.9g}, "
                f"nonzero_seed_fraction={row['fraction_nonzero']:.6g}, "
                f"valid={int(row['n_valid'])}/{int(row['n_total'])}"
            )

    lines.extend(
        [
            "",
            "Interpretation notes",
            "--------------------",
            "* Unique upper-triangular edges are the scientific topology object.",
            "* Full-matrix, symmetry, and diagonal checks are storage/model invariants.",
            "* Exact binary and binary-within-tolerance are reported separately.",
            "* Projection magnitudes are Frobenius norms of numerical corrections, not physical work.",
            "* Conditional projection activity is active_fraction / violation_fraction when the denominator is nonzero.",
            "",
        ]
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cohort",
        action="append",
        type=parse_cohort,
        default=None,
        metavar="LABEL=SCALAR_CSV,EDGE_NPZ",
        help="repeat for multiple cohorts",
    )
    parser.add_argument(
        "--expected-seeds",
        type=int,
        default=DEFAULT_EXPECTED_SEEDS,
        help=f"expected seeds per condition/cohort (default: {DEFAULT_EXPECTED_SEEDS})",
    )
    parser.add_argument(
        "--expected-cohorts",
        type=int,
        default=2,
        help="expected independent cohort count (default: 2)",
    )
    parser.add_argument(
        "--binary-atol",
        type=float,
        default=DEFAULT_BINARY_ATOL,
        help=f"tolerance for tolerant binary check (default: {DEFAULT_BINARY_ATOL})",
    )
    parser.add_argument(
        "--matrix-atol",
        type=float,
        default=DEFAULT_MATRIX_ATOL,
        help=f"matrix symmetry/diagonal tolerance (default: {DEFAULT_MATRIX_ATOL})",
    )
    parser.add_argument(
        "--consistency-atol",
        type=float,
        default=DEFAULT_CONSISTENCY_ATOL,
        help=f"matrix/scalar consistency tolerance (default: {DEFAULT_CONSISTENCY_ATOL})",
    )
    parser.add_argument(
        "--allow-seed-overlap",
        action="store_true",
        help="allow cohorts with overlapping seeds (not recommended for validation)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit with status 2 if any closure check fails",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if args.expected_seeds <= 0 or args.expected_cohorts <= 0:
        raise ValueError("expected seed/cohort counts must be positive")
    if min(args.binary_atol, args.matrix_atol, args.consistency_atol) < 0:
        raise ValueError("tolerances must be nonnegative")

    specs = args.cohort if args.cohort is not None else list(DEFAULT_COHORTS)
    labels = [spec[0] for spec in specs]
    if len(set(labels)) != len(labels):
        raise ValueError("cohort labels must be unique")

    os.makedirs(args.output_dir, exist_ok=True)

    scalar_frames: list[pd.DataFrame] = []
    coverage_rows: list[dict[str, object]] = []
    matrix_rows: list[dict[str, object]] = []
    unique_rows: list[dict[str, object]] = []
    consistency_rows: list[dict[str, object]] = []
    projection_consistency_rows: list[dict[str, object]] = []
    cohort_seed_sets: dict[str, set[str]] = {}
    warnings: dict[str, list[str]] = {}

    for label, scalar_path, edge_path in specs:
        print(f"Auditing {label}")
        scalar, scalar_coverage, baseline_seeds, cohort_warnings = (
            load_scalar_cohort(label, scalar_path, args.expected_seeds)
        )
        indexed = index_persistence_matrices(label, edge_path)

        for row in scalar_coverage:
            condition = str(row["condition"])
            npz_seeds = set(indexed[condition])
            scalar_seeds = set(
                scalar.loc[scalar["condition"] == condition, "seed"].astype(str)
            )
            row.update(
                {
                    "npz_P_future_count": int(len(npz_seeds)),
                    "npz_count_ok": bool(len(npz_seeds) == args.expected_seeds),
                    "npz_seed_set_matches_scalar": bool(npz_seeds == scalar_seeds),
                    "npz_missing_vs_scalar": int(len(scalar_seeds - npz_seeds)),
                    "npz_extra_vs_scalar": int(len(npz_seeds - scalar_seeds)),
                }
            )
            row["coverage_complete"] = bool(
                row["scalar_count_ok"]
                and row["scalar_seed_set_matches_baseline"]
                and row["npz_count_ok"]
                and row["npz_seed_set_matches_scalar"]
            )
            if not row["coverage_complete"]:
                cohort_warnings.append(f"{condition}: incomplete scalar/NPZ coverage")
            coverage_rows.append(row)

        audited, unique, consistency = audit_baseline_persistence(
            label,
            edge_path,
            indexed,
            scalar,
            binary_atol=args.binary_atol,
            matrix_atol=args.matrix_atol,
            consistency_atol=args.consistency_atol,
        )
        matrix_rows.extend(audited)
        unique_rows.extend(unique)
        consistency_rows.extend(consistency)

        scalar, projection_consistency = add_projection_conditionals(
            scalar,
            tolerance=args.consistency_atol,
        )
        projection_consistency_rows.extend(projection_consistency)
        scalar_frames.append(scalar)
        cohort_seed_sets[label] = baseline_seeds
        warnings[label] = cohort_warnings

    overlap_rows: list[dict[str, object]] = []
    for cohort_a, cohort_b in itertools.combinations(sorted(cohort_seed_sets), 2):
        overlap = cohort_seed_sets[cohort_a] & cohort_seed_sets[cohort_b]
        overlap_rows.append(
            {
                "cohort_a": cohort_a,
                "cohort_b": cohort_b,
                "overlap_count": int(len(overlap)),
                "overlap_seeds": ";".join(sorted(overlap, key=int)),
            }
        )

    coverage = pd.DataFrame(coverage_rows)
    matrix_audit = pd.DataFrame(matrix_rows)
    unique_by_seed = pd.DataFrame(unique_rows)
    consistency = pd.DataFrame(consistency_rows)
    projection_consistency = pd.DataFrame(projection_consistency_rows)
    overlap = pd.DataFrame(overlap_rows)
    projection_raw = pd.concat(scalar_frames, ignore_index=True)
    projection = projection_summary(
        projection_raw,
        zero_atol=args.consistency_atol,
    )

    unique_pooled = (
        unique_by_seed.groupby(["cohort", "P_value_repr"], as_index=False)["count"]
        .sum()
        .sort_values(["cohort", "P_value_repr"])
    )

    status = build_closure_status(
        coverage=coverage,
        matrix_audit=matrix_audit,
        consistency=consistency,
        projection=projection,
        projection_consistency=projection_consistency,
        overlap=overlap,
        allow_seed_overlap=args.allow_seed_overlap,
        expected_cohort_count=args.expected_cohorts,
        actual_cohort_count=len(specs),
    )
    status["warnings"] = warnings
    status["settings"] = {
        "expected_seeds": args.expected_seeds,
        "expected_cohorts": args.expected_cohorts,
        "binary_atol": args.binary_atol,
        "matrix_atol": args.matrix_atol,
        "consistency_atol": args.consistency_atol,
        "allow_seed_overlap": args.allow_seed_overlap,
    }

    outputs = {
        "cohort_seed_coverage.csv": coverage,
        "baseline_persistence_by_seed.csv": matrix_audit,
        "baseline_persistence_unique_values_by_seed.csv": unique_by_seed,
        "baseline_persistence_unique_values_pooled.csv": unique_pooled,
        "matrix_scalar_consistency.csv": consistency,
        "projection_diagnostics_summary.csv": projection,
        "projection_consistency_by_seed.csv": projection_consistency,
        "cohort_seed_overlap.csv": overlap,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)

    report = make_report(status, coverage, matrix_audit, projection, overlap)
    report_path = os.path.join(args.output_dir, "closure_report.txt")
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report)

    status_path = os.path.join(args.output_dir, "closure_status.json")
    with open(status_path, "w", encoding="utf-8") as handle:
        json.dump(status, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("\n" + report)
    print(f"Saved closure artifacts to {Path(args.output_dir).resolve()}")

    if args.strict and not status["closure_passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
