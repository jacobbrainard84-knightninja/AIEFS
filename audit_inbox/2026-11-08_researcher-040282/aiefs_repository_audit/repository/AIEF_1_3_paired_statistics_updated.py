#!/usr/bin/env python3
"""Paired seed-level statistics for two or more AIEF-1.3 cohorts.

The independent unit is one seed/graph realization. Conditions are paired by
seed *within* each cohort. Cohorts are never paired to one another.

Outputs
-------
paired_effects.csv
    Cohort-specific and stratified-pooled paired effects for continuous metrics.
paired_binary_effects.csv
    Paired degeneracy-rate effects with exact McNemar/binomial tests.
paired_seed_deltas.csv
    Auditable per-seed differences, defined as baseline minus control.
paired_cohort_heterogeneity.csv
    Bootstrap comparisons of effect magnitudes between validation cohorts.
analysis_manifest.json
    Input hashes and analysis settings.
paired_report.txt
    A concise text report of selected effects.

Examples
--------
Use the two known 50-seed validation cohorts:
    python AIEF_1_3_paired_statistics.py

Specify cohorts explicitly:
    python AIEF_1_3_paired_statistics.py \
      --cohort validation_A=runs/HASH_A/AIEF_1_3_HASH_A_scalar_summary.csv \
      --cohort validation_B=runs/HASH_B/AIEF_1_3_HASH_B_scalar_summary.csv
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_COHORTS = (
    (
        "validation_A",
        "/home/deck/AI_Programs/SSRH/runs/87dfe5798954/AIEF_1_3_87dfe5798954_scalar_summary.csv",
    ),
    (
        "validation_B",
        "/home/deck/AI_Programs/SSRH/runs/5a338105785a/AIEF_1_3_5a338105785a_scalar_summary.csv",
    ),
)

CONTROLS = ("shuffle_R", "no_delay", "no_mu", "no_gap")

# Phi is intentionally excluded: it is undefined or unstable near D_B == 0.
METRICS = (
    "D_B",
    "Corr_physical",
    "FisherZ_Corr_physical",
    "Corr_driver",
    "FisherZ_Corr_driver",
    "r_mean",
    "S_spectral",
    "G_min_final",
    "G_min_over_time",
    "G_min_pre_over_time",
    "P_mean",
    "P_variance",
    "P_max",
    "P_nonzero_fraction",
    "Cov_physical",
    "Cov_driver",
    "Total_edge_weight",
    "Mean_row_sum",
    "Max_row_sum",
    "Nonzero_edge_fraction",
    "Effective_edges",
    "Weight_gini",
    "Weight_entropy",
    "Pre_gap_violation_fraction",
    "Projection_active_fraction",
    "Projection_norm_mean_active",
    "Projection_norm_max",
)

# Selected effects printed in the concise report. All available metrics are
# still written to paired_effects.csv.
REPORT_METRICS = {
    "shuffle_R": (
        "D_B",
        "P_mean",
        "P_max",
        "P_nonzero_fraction",
        "Cov_physical",
        "Total_edge_weight",
        "Effective_edges",
    ),
    "no_delay": (
        "Corr_physical",
        "FisherZ_Corr_physical",
        "D_B",
        "P_mean",
        "Effective_edges",
        "r_mean",
    ),
    "no_mu": (
        "D_B",
        "P_mean",
        "Total_edge_weight",
        "Mean_row_sum",
        "Effective_edges",
        "Weight_gini",
        "Weight_entropy",
        "Nonzero_edge_fraction",
        "Projection_norm_mean_active",
    ),
    "no_gap": (
        "D_B",
        "P_mean",
        "G_min_over_time",
        "Total_edge_weight",
        "Effective_edges",
        "r_mean",
        "Corr_physical",
    ),
}

# Primary endpoints are control-specific. Metrics not listed here are marked
# secondary/exploratory. Fisher-z is always treated as a sensitivity endpoint.
PRIMARY_METRICS = {
    "shuffle_R": {"D_B", "P_mean", "P_max"},
    "no_delay": {"Corr_physical", "D_B", "P_mean"},
    "no_mu": {
        "D_B",
        "Total_edge_weight",
        "Effective_edges",
        "Weight_gini",
        "Weight_entropy",
    },
    "no_gap": {"G_min_over_time", "D_B", "Total_edge_weight"},
}

# Expected directions refer to delta = baseline - control. They are metadata
# for interpretation only; all reported tests remain two-sided.
EXPECTED_DIRECTIONS = {
    ("shuffle_R", "D_B"): "positive",
    ("shuffle_R", "P_mean"): "positive",
    ("shuffle_R", "P_max"): "positive",
    ("shuffle_R", "P_nonzero_fraction"): "positive",
    ("no_mu", "D_B"): "positive",
    ("no_mu", "Effective_edges"): "negative",
    ("no_mu", "Weight_gini"): "positive",
    ("no_mu", "Weight_entropy"): "negative",
    ("no_gap", "G_min_over_time"): "positive",
    ("no_gap", "D_B"): "negative",
    ("no_gap", "Total_edge_weight"): "negative",
    ("no_gap", "Effective_edges"): "negative",
}

# Relative differences are meaningful only for nonnegative ratio-scale metrics.
RELATIVE_CHANGE_METRICS = {
    "D_B",
    "r_mean",
    "P_mean",
    "P_variance",
    "P_max",
    "P_nonzero_fraction",
    "Total_edge_weight",
    "Mean_row_sum",
    "Max_row_sum",
    "Nonzero_edge_fraction",
    "Effective_edges",
    "Weight_entropy",
    "Pre_gap_violation_fraction",
    "Projection_active_fraction",
    "Projection_norm_mean_active",
    "Projection_norm_max",
}

DEFAULT_BOOTSTRAPS = 20_000
DEFAULT_SIGN_FLIPS = 100_000
DEFAULT_ANALYSIS_SEED = 20260714
DEFAULT_OUTPUT_DIR = "paired_seed_analysis"
CORRELATION_CLIP = 1.0 - 1e-12


def parse_cohort(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("cohort must have the form LABEL=CSV_PATH")
    label, path = value.split("=", 1)
    label = label.strip()
    path = path.strip()
    if not label or not path:
        raise argparse.ArgumentTypeError("cohort label and path must be nonempty")
    return label, path


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rng_for(analysis_seed: int, label: str) -> np.random.Generator:
    digest = hashlib.sha256(f"{analysis_seed}|{label}".encode("utf-8")).digest()
    child_seed = int.from_bytes(digest[:8], "little", signed=False)
    return np.random.default_rng(child_seed)


def to_boolean(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(bool)
    text = series.astype(str).str.strip().str.lower()
    mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
    }
    converted = text.map(mapping)
    if converted.isna().any():
        bad = sorted(text[converted.isna()].unique())
        raise ValueError(f"cannot parse boolean values: {bad}")
    return converted.astype(bool)


def add_derived_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    for column in ("Corr_physical", "Corr_driver"):
        if column not in frame.columns:
            continue
        values = pd.to_numeric(frame[column], errors="coerce").to_numpy(float)
        transformed = np.full(values.shape, np.nan, dtype=float)
        finite = np.isfinite(values)
        transformed[finite] = np.arctanh(
            np.clip(values[finite], -CORRELATION_CLIP, CORRELATION_CLIP)
        )
        frame[f"FisherZ_{column}"] = transformed
    if "P_degenerate" in frame.columns:
        frame["P_degenerate"] = to_boolean(frame["P_degenerate"])
    return frame


def load_cohort(label: str, path: str) -> pd.DataFrame:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"cohort CSV not found: {path}")

    # Seed is read as text so uint64-valued seeds remain exact in pandas.
    frame = pd.read_csv(path, dtype={"seed": str})
    required = {"condition", "seed"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{label}: missing required columns {sorted(missing)}")

    frame["condition"] = frame["condition"].astype(str)
    frame["seed"] = frame["seed"].astype(str)
    frame["cohort"] = label
    frame = add_derived_metrics(frame)

    duplicate = frame.duplicated(["condition", "seed"], keep=False)
    if duplicate.any():
        rows = frame.loc[duplicate, ["condition", "seed"]]
        raise ValueError(f"{label}: duplicate condition/seed rows:\n{rows}")

    if "baseline" not in set(frame["condition"]):
        raise ValueError(f"{label}: baseline condition is absent")

    baseline_seeds = set(frame.loc[frame["condition"] == "baseline", "seed"])
    for control in CONTROLS:
        if control not in set(frame["condition"]):
            raise ValueError(f"{label}: condition {control!r} is absent")
        control_seeds = set(frame.loc[frame["condition"] == control, "seed"])
        if baseline_seeds != control_seeds:
            only_baseline = sorted(baseline_seeds - control_seeds)[:5]
            only_control = sorted(control_seeds - baseline_seeds)[:5]
            raise ValueError(
                f"{label}: seed mismatch for {control}; "
                f"baseline-only={only_baseline}, control-only={only_control}"
            )

    return frame


def pair_condition(frame: pd.DataFrame, control: str) -> pd.DataFrame:
    baseline = frame.loc[frame["condition"] == "baseline"].copy()
    comparison = frame.loc[frame["condition"] == control].copy()

    keep = ["seed"]
    if "seed_index" in frame.columns:
        keep.append("seed_index")
    keep.extend(metric for metric in METRICS if metric in frame.columns)
    if "P_degenerate" in frame.columns:
        keep.append("P_degenerate")

    baseline = baseline[keep]
    comparison = comparison[keep]
    paired = baseline.merge(
        comparison,
        on="seed",
        how="inner",
        suffixes=("_baseline", "_control"),
        validate="one_to_one",
    )

    if "seed_index_baseline" in paired.columns:
        left = pd.to_numeric(paired["seed_index_baseline"], errors="coerce")
        right = pd.to_numeric(paired["seed_index_control"], errors="coerce")
        if not np.array_equal(left.to_numpy(), right.to_numpy()):
            raise ValueError(f"seed_index mismatch in baseline vs {control}")
        paired["seed_index"] = left.astype("Int64")

    return paired


def bootstrap_mean_ci(
    differences: np.ndarray,
    cohort_labels: np.ndarray,
    *,
    repetitions: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Stratified paired bootstrap CI for the mean difference."""
    differences = np.asarray(differences, dtype=float)
    cohort_labels = np.asarray(cohort_labels, dtype=str)
    if len(differences) == 0:
        return np.nan, np.nan
    if repetitions <= 0:
        return np.nan, np.nan

    unique_cohorts = np.unique(cohort_labels)
    bootstrap_means = np.zeros(repetitions, dtype=float)
    total_n = len(differences)

    for cohort in unique_cohorts:
        values = differences[cohort_labels == cohort]
        n = len(values)
        indices = rng.integers(0, n, size=(repetitions, n))
        bootstrap_means += np.mean(values[indices], axis=1) * (n / total_n)

    low, high = np.percentile(bootstrap_means, [2.5, 97.5])
    return float(low), float(high)


def sign_flip_pvalue(
    differences: np.ndarray,
    *,
    repetitions: int,
    rng: np.random.Generator,
    batch_size: int = 5_000,
) -> float:
    """Two-sided symmetry-based sign-flip test for a paired mean difference."""
    differences = np.asarray(differences, dtype=float)
    if len(differences) == 0 or repetitions <= 0:
        return np.nan
    observed = abs(float(np.mean(differences)))
    if np.allclose(differences, 0.0, rtol=0.0, atol=0.0):
        return 1.0

    extreme = 0
    completed = 0
    while completed < repetitions:
        size = min(batch_size, repetitions - completed)
        signs = rng.integers(0, 2, size=(size, len(differences)), dtype=np.int8)
        signs = signs * 2 - 1
        simulated = np.abs(np.mean(signs * differences, axis=1))
        extreme += int(np.count_nonzero(simulated >= observed - 1e-15))
        completed += size

    return float((extreme + 1) / (repetitions + 1))


def exact_mcnemar_pvalue(b: int, c: int) -> float:
    """Exact two-sided McNemar/binomial p-value for discordant pairs."""
    discordant = b + c
    if discordant == 0:
        return 1.0
    tail = sum(math.comb(discordant, k) for k in range(min(b, c) + 1))
    p_value = 2.0 * tail / (2**discordant)
    return float(min(1.0, p_value))


def endpoint_role(control: str, metric: str) -> str:
    if metric.startswith("FisherZ_"):
        return "sensitivity"
    return "primary" if metric in PRIMARY_METRICS.get(control, set()) else "secondary"


def expected_direction(control: str, metric: str) -> str:
    return EXPECTED_DIRECTIONS.get((control, metric), "not_predeclared")


def paired_cohen_dz(mean_difference: float, std_difference: float) -> tuple[float, str]:
    tolerance = 1e-15
    if not np.isfinite(mean_difference) or not np.isfinite(std_difference):
        return np.nan, "nonfinite"
    if std_difference > tolerance:
        return float(mean_difference / std_difference), "ok"
    if abs(mean_difference) <= tolerance:
        return 0.0, "zero_mean_and_sd"
    return np.nan, "zero_sd_nonzero_mean"


def relative_difference(
    metric: str,
    mean_difference: float,
    baseline_mean: float,
) -> tuple[float, str]:
    if metric not in RELATIVE_CHANGE_METRICS:
        return np.nan, "not_applicable"
    if not np.isfinite(mean_difference) or not np.isfinite(baseline_mean):
        return np.nan, "nonfinite"
    if abs(baseline_mean) <= 1e-12:
        return np.nan, "baseline_near_zero"
    return float(mean_difference / abs(baseline_mean)), "ok"


def bootstrap_cohort_difference_ci(
    values_a: np.ndarray,
    values_b: np.ndarray,
    *,
    repetitions: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Bootstrap CI for mean(effect in cohort A) - mean(effect in cohort B)."""
    values_a = np.asarray(values_a, dtype=float)
    values_b = np.asarray(values_b, dtype=float)
    if len(values_a) == 0 or len(values_b) == 0 or repetitions <= 0:
        return np.nan, np.nan
    index_a = rng.integers(0, len(values_a), size=(repetitions, len(values_a)))
    index_b = rng.integers(0, len(values_b), size=(repetitions, len(values_b)))
    boot = np.mean(values_a[index_a], axis=1) - np.mean(values_b[index_b], axis=1)
    low, high = np.percentile(boot, [2.5, 97.5])
    return float(low), float(high)


def continuous_effect_row(
    paired: pd.DataFrame,
    *,
    cohort_scope: str,
    control: str,
    metric: str,
    bootstrap_repetitions: int,
    sign_flip_repetitions: int,
    analysis_seed: int,
) -> tuple[dict[str, object] | None, list[dict[str, object]]]:
    baseline_column = f"{metric}_baseline"
    control_column = f"{metric}_control"
    if baseline_column not in paired.columns or control_column not in paired.columns:
        return None, []

    n_total_pairs = int(len(paired))
    baseline_all = pd.to_numeric(
        paired[baseline_column], errors="coerce"
    ).to_numpy(float)
    control_all = pd.to_numeric(
        paired[control_column], errors="coerce"
    ).to_numpy(float)
    valid = np.isfinite(baseline_all) & np.isfinite(control_all)
    n_valid_pairs = int(np.sum(valid))
    role = endpoint_role(control, metric)
    direction = expected_direction(control, metric)

    empty_row: dict[str, object] = {
        "scope": cohort_scope,
        "control": control,
        "metric": metric,
        "endpoint_role": role,
        "expected_direction_baseline_minus_control": direction,
        "difference_definition": "baseline_minus_control",
        "n_total_pairs": n_total_pairs,
        "n_valid_pairs": n_valid_pairs,
        "valid_pair_fraction": float(n_valid_pairs / n_total_pairs)
        if n_total_pairs
        else np.nan,
        # n_pairs is retained as a backwards-compatible alias.
        "n_pairs": n_valid_pairs,
        "baseline_mean": np.nan,
        "control_mean": np.nan,
        "mean_difference": np.nan,
        "median_difference": np.nan,
        "std_difference": np.nan,
        "paired_cohen_dz": np.nan,
        "paired_cohen_dz_status": "nonfinite",
        "relative_difference": np.nan,
        "relative_difference_status": "nonfinite",
        "ci95_low": np.nan,
        "ci95_high": np.nan,
        "fraction_positive": np.nan,
        "fraction_negative": np.nan,
        "fraction_zero": np.nan,
        "sign_flip_p_two_sided_supporting": np.nan,
    }
    if not np.any(valid):
        return empty_row, []

    baseline = baseline_all[valid]
    comparison = control_all[valid]
    differences = baseline - comparison
    cohorts = paired.loc[valid, "cohort"].astype(str).to_numpy()

    bootstrap_rng = rng_for(
        analysis_seed,
        f"bootstrap|{cohort_scope}|{control}|{metric}",
    )
    sign_rng = rng_for(
        analysis_seed,
        f"sign|{cohort_scope}|{control}|{metric}",
    )
    ci_low, ci_high = bootstrap_mean_ci(
        differences,
        cohorts,
        repetitions=bootstrap_repetitions,
        rng=bootstrap_rng,
    )
    p_value = sign_flip_pvalue(
        differences,
        repetitions=sign_flip_repetitions,
        rng=sign_rng,
    )

    baseline_mean = float(np.mean(baseline))
    control_mean = float(np.mean(comparison))
    mean_difference = float(np.mean(differences))
    std_difference = (
        float(np.std(differences, ddof=1)) if len(differences) > 1 else 0.0
    )
    cohen_dz, cohen_status = paired_cohen_dz(mean_difference, std_difference)
    relative, relative_status = relative_difference(
        metric,
        mean_difference,
        baseline_mean,
    )

    tolerance = 1e-15
    row = {
        **empty_row,
        "baseline_mean": baseline_mean,
        "control_mean": control_mean,
        "mean_difference": mean_difference,
        "median_difference": float(np.median(differences)),
        "std_difference": std_difference,
        "paired_cohen_dz": cohen_dz,
        "paired_cohen_dz_status": cohen_status,
        "relative_difference": relative,
        "relative_difference_status": relative_status,
        "ci95_low": ci_low,
        "ci95_high": ci_high,
        "fraction_positive": float(np.mean(differences > tolerance)),
        "fraction_negative": float(np.mean(differences < -tolerance)),
        "fraction_zero": float(np.mean(np.abs(differences) <= tolerance)),
        "sign_flip_p_two_sided_supporting": p_value,
    }

    per_seed_rows: list[dict[str, object]] = []
    valid_indices = np.flatnonzero(valid)
    for output_index, frame_index in enumerate(valid_indices):
        per_seed_rows.append(
            {
                "cohort": str(paired.iloc[frame_index]["cohort"]),
                "seed": str(paired.iloc[frame_index]["seed"]),
                "seed_index": paired.iloc[frame_index].get("seed_index", pd.NA),
                "control": control,
                "metric": metric,
                "endpoint_role": role,
                "expected_direction_baseline_minus_control": direction,
                "baseline_value": float(baseline[output_index]),
                "control_value": float(comparison[output_index]),
                "difference_baseline_minus_control": float(differences[output_index]),
            }
        )

    return row, per_seed_rows

def binary_effect_row(
    paired: pd.DataFrame,
    *,
    cohort_scope: str,
    control: str,
) -> dict[str, object] | None:
    baseline_column = "P_degenerate_baseline"
    control_column = "P_degenerate_control"
    if baseline_column not in paired.columns or control_column not in paired.columns:
        return None

    baseline = to_boolean(paired[baseline_column]).to_numpy(bool)
    comparison = to_boolean(paired[control_column]).to_numpy(bool)
    baseline_only = int(np.count_nonzero(baseline & ~comparison))
    control_only = int(np.count_nonzero(~baseline & comparison))
    baseline_rate = float(np.mean(baseline))
    control_rate = float(np.mean(comparison))

    if control_rate > baseline_rate:
        direction = "increased_in_control"
    elif control_rate < baseline_rate:
        direction = "decreased_in_control"
    else:
        direction = "no_rate_difference"

    return {
        "scope": cohort_scope,
        "control": control,
        "metric": "P_degenerate",
        "endpoint_role": "primary" if control == "shuffle_R" else "secondary",
        "expected_direction_control_minus_baseline": "positive"
        if control == "shuffle_R"
        else "not_predeclared",
        "difference_definition": "control_rate_minus_baseline_rate",
        "n_total_pairs": int(len(baseline)),
        "n_valid_pairs": int(len(baseline)),
        "valid_pair_fraction": 1.0 if len(baseline) else np.nan,
        "n_pairs": int(len(baseline)),
        "baseline_rate": baseline_rate,
        "control_rate": control_rate,
        "rate_difference": float(control_rate - baseline_rate),
        "discordance_direction": direction,
        "both_nondegenerate": int(np.count_nonzero(~baseline & ~comparison)),
        "baseline_only_degenerate": baseline_only,
        "control_only_degenerate": control_only,
        "both_degenerate": int(np.count_nonzero(baseline & comparison)),
        "mcnemar_exact_p_two_sided": exact_mcnemar_pvalue(
            baseline_only,
            control_only,
        ),
    }

def cohort_heterogeneity_rows(
    cohort_pairs: dict[str, pd.DataFrame],
    *,
    control: str,
    metrics: Iterable[str],
    bootstrap_repetitions: int,
    analysis_seed: int,
) -> list[dict[str, object]]:
    """Compare paired effect magnitudes between independent cohorts."""
    rows: list[dict[str, object]] = []
    for cohort_a, cohort_b in itertools.combinations(sorted(cohort_pairs), 2):
        frame_a = cohort_pairs[cohort_a]
        frame_b = cohort_pairs[cohort_b]
        for metric in metrics:
            baseline_column = f"{metric}_baseline"
            control_column = f"{metric}_control"
            if (
                baseline_column not in frame_a.columns
                or control_column not in frame_a.columns
                or baseline_column not in frame_b.columns
                or control_column not in frame_b.columns
            ):
                continue

            def finite_differences(frame: pd.DataFrame) -> np.ndarray:
                baseline = pd.to_numeric(
                    frame[baseline_column], errors="coerce"
                ).to_numpy(float)
                comparison = pd.to_numeric(
                    frame[control_column], errors="coerce"
                ).to_numpy(float)
                valid = np.isfinite(baseline) & np.isfinite(comparison)
                return baseline[valid] - comparison[valid]

            values_a = finite_differences(frame_a)
            values_b = finite_differences(frame_b)
            mean_a = float(np.mean(values_a)) if len(values_a) else np.nan
            mean_b = float(np.mean(values_b)) if len(values_b) else np.nan
            difference = mean_a - mean_b if len(values_a) and len(values_b) else np.nan
            rng = rng_for(
                analysis_seed,
                f"heterogeneity|{control}|{metric}|{cohort_a}|{cohort_b}",
            )
            ci_low, ci_high = bootstrap_cohort_difference_ci(
                values_a,
                values_b,
                repetitions=bootstrap_repetitions,
                rng=rng,
            )
            if not np.isfinite(mean_a) or not np.isfinite(mean_b):
                same_direction: object = pd.NA
            elif mean_a == 0.0 or mean_b == 0.0:
                same_direction = bool(mean_a == mean_b)
            else:
                same_direction = bool(np.sign(mean_a) == np.sign(mean_b))

            rows.append(
                {
                    "control": control,
                    "metric": metric,
                    "endpoint_role": endpoint_role(control, metric),
                    "cohort_a": cohort_a,
                    "cohort_b": cohort_b,
                    "n_total_a": int(len(frame_a)),
                    "n_total_b": int(len(frame_b)),
                    "n_valid_a": int(len(values_a)),
                    "n_valid_b": int(len(values_b)),
                    "valid_fraction_a": float(len(values_a) / len(frame_a))
                    if len(frame_a)
                    else np.nan,
                    "valid_fraction_b": float(len(values_b) / len(frame_b))
                    if len(frame_b)
                    else np.nan,
                    "mean_difference_a": mean_a,
                    "mean_difference_b": mean_b,
                    "cohort_difference_a_minus_b": difference,
                    "ci95_low": ci_low,
                    "ci95_high": ci_high,
                    "same_effect_direction": same_direction,
                    "ci_contains_zero": bool(ci_low <= 0.0 <= ci_high)
                    if np.isfinite(ci_low) and np.isfinite(ci_high)
                    else pd.NA,
                }
            )
    return rows


def format_number(value: object, digits: int = 6) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not np.isfinite(number):
        return "nan"
    return f"{number:.{digits}f}"


def make_report(
    effects: pd.DataFrame,
    binary_effects: pd.DataFrame,
    heterogeneity: pd.DataFrame,
    cohort_labels: list[str],
) -> str:
    lines = [
        "AIEF-1.3 paired seed-level analysis",
        "====================================",
        "",
        "Continuous differences are baseline minus control.",
        "Bootstrap confidence intervals and raw effect magnitudes are primary.",
        "Sign-flip p-values are supporting symmetry-based tests, not design-based randomization tests.",
        "Pooled confidence intervals use a stratified paired bootstrap.",
        "Correlation comparisons are non-estimable when either member is degenerate.",
        "",
        f"Cohorts: {', '.join(cohort_labels)}",
        "",
    ]

    for control in CONTROLS:
        lines.append(control)
        lines.append("-" * len(control))
        selected = effects.loc[
            (effects["scope"] == "pooled")
            & (effects["control"] == control)
            & (effects["metric"].isin(REPORT_METRICS[control]))
        ]
        for metric in REPORT_METRICS[control]:
            row_set = selected.loc[selected["metric"] == metric]
            if row_set.empty:
                continue
            row = row_set.iloc[0]
            lines.append(
                f"  {metric} [{row['endpoint_role']}]: "
                f"valid={int(row['n_valid_pairs'])}/{int(row['n_total_pairs'])}, "
                f"base={format_number(row['baseline_mean'])}, "
                f"control={format_number(row['control_mean'])}, "
                f"delta={format_number(row['mean_difference'])}, "
                f"95% CI=[{format_number(row['ci95_low'])}, "
                f"{format_number(row['ci95_high'])}], "
                f"dz={format_number(row['paired_cohen_dz'], 3)}, "
                f"relative={format_number(row['relative_difference'], 3)}, "
                f"positive={format_number(row['fraction_positive'], 3)}, "
                f"p_sign(supporting)="
                f"{format_number(row['sign_flip_p_two_sided_supporting'], 6)}"
            )

        binary_set = binary_effects.loc[
            (binary_effects["scope"] == "pooled")
            & (binary_effects["control"] == control)
        ]
        if not binary_set.empty:
            row = binary_set.iloc[0]
            lines.append(
                "  P_degenerate "
                f"[{row['endpoint_role']}]: "
                f"base={format_number(row['baseline_rate'], 3)}, "
                f"control={format_number(row['control_rate'], 3)}, "
                f"delta(control-base)={format_number(row['rate_difference'], 3)}, "
                f"direction={row['discordance_direction']}, "
                f"p_McNemar={format_number(row['mcnemar_exact_p_two_sided'], 6)}"
            )

        if not heterogeneity.empty:
            hset = heterogeneity.loc[
                (heterogeneity["control"] == control)
                & (heterogeneity["metric"].isin(PRIMARY_METRICS.get(control, set())))
            ]
            for _, row in hset.iterrows():
                lines.append(
                    f"  cohort check {row['metric']}: "
                    f"{row['cohort_a']}={format_number(row['mean_difference_a'])}, "
                    f"{row['cohort_b']}={format_number(row['mean_difference_b'])}, "
                    f"A-B={format_number(row['cohort_difference_a_minus_b'])}, "
                    f"95% CI=[{format_number(row['ci95_low'])}, "
                    f"{format_number(row['ci95_high'])}], "
                    f"same_direction={row['same_effect_direction']}"
                )
        lines.append("")

    lines.extend(
        [
            "Interpretation notes",
            "--------------------",
            "* Raw differences and bootstrap CIs are the headline results.",
            "* Paired Cohen dz is undefined when the paired SD is zero but the mean is nonzero.",
            "* Relative differences are emitted only for eligible nonnegative ratio-scale metrics.",
            "* Do not compare baseline and shuffle_R using Fisher-z if shuffle_R is degenerate.",
            "* Treat no_gap correlation as conditional on the finite paired subset.",
            "* Phi is intentionally excluded because it is unstable near zero density.",
            "* Cohort compatibility uses a bootstrap difference of cohort mean effects; with two cohorts it is diagnostic, not a random-effects meta-analysis.",
            "",
        ]
    )
    return "\n".join(lines)

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cohort",
        action="append",
        type=parse_cohort,
        default=None,
        metavar="LABEL=CSV_PATH",
        help="cohort label and scalar-summary CSV; repeat for multiple cohorts",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"analysis output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=DEFAULT_BOOTSTRAPS,
        help=f"paired bootstrap repetitions (default: {DEFAULT_BOOTSTRAPS})",
    )
    parser.add_argument(
        "--sign-flips",
        type=int,
        default=DEFAULT_SIGN_FLIPS,
        help=f"Monte Carlo sign-flip repetitions (default: {DEFAULT_SIGN_FLIPS})",
    )
    parser.add_argument(
        "--analysis-seed",
        type=int,
        default=DEFAULT_ANALYSIS_SEED,
        help=f"analysis RNG seed (default: {DEFAULT_ANALYSIS_SEED})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    cohort_specs = args.cohort if args.cohort is not None else list(DEFAULT_COHORTS)
    labels = [label for label, _ in cohort_specs]
    if len(set(labels)) != len(labels):
        raise ValueError("cohort labels must be unique")
    if args.bootstrap < 0 or args.sign_flips < 0:
        raise ValueError("bootstrap and sign-flips must be nonnegative")

    os.makedirs(args.output_dir, exist_ok=True)

    cohorts: dict[str, pd.DataFrame] = {}
    input_manifest: list[dict[str, str]] = []
    for label, path in cohort_specs:
        frame = load_cohort(label, path)
        cohorts[label] = frame
        input_manifest.append(
            {
                "label": label,
                "path": str(Path(path).resolve()),
                "sha256": file_sha256(path),
                "rows": str(len(frame)),
            }
        )
        baseline_count = int(np.sum(frame["condition"] == "baseline"))
        print(f"Loaded {label}: {baseline_count} paired seeds from {path}")

    paired_by_control: dict[str, dict[str, pd.DataFrame]] = {}
    for control in CONTROLS:
        paired_by_control[control] = {}
        for label, frame in cohorts.items():
            paired = pair_condition(frame, control)
            paired["cohort"] = label
            paired_by_control[control][label] = paired

    effect_rows: list[dict[str, object]] = []
    binary_rows: list[dict[str, object]] = []
    per_seed_rows: list[dict[str, object]] = []
    heterogeneity_rows: list[dict[str, object]] = []

    for control in CONTROLS:
        cohort_pairs = paired_by_control[control]

        # Cohort-specific effects.
        for label, paired in cohort_pairs.items():
            for metric in METRICS:
                row, delta_rows = continuous_effect_row(
                    paired,
                    cohort_scope=label,
                    control=control,
                    metric=metric,
                    bootstrap_repetitions=args.bootstrap,
                    sign_flip_repetitions=args.sign_flips,
                    analysis_seed=args.analysis_seed,
                )
                if row is not None:
                    effect_rows.append(row)
                per_seed_rows.extend(delta_rows)

            binary = binary_effect_row(
                paired,
                cohort_scope=label,
                control=control,
            )
            if binary is not None:
                binary_rows.append(binary)

        # Stratified-pooled effects across cohorts.
        pooled = pd.concat(list(cohort_pairs.values()), ignore_index=True)
        for metric in METRICS:
            row, _ = continuous_effect_row(
                pooled,
                cohort_scope="pooled",
                control=control,
                metric=metric,
                bootstrap_repetitions=args.bootstrap,
                sign_flip_repetitions=args.sign_flips,
                analysis_seed=args.analysis_seed,
            )
            if row is not None:
                effect_rows.append(row)

        binary = binary_effect_row(
            pooled,
            cohort_scope="pooled",
            control=control,
        )
        if binary is not None:
            binary_rows.append(binary)

        heterogeneity_rows.extend(
            cohort_heterogeneity_rows(
                cohort_pairs,
                control=control,
                metrics=METRICS,
                bootstrap_repetitions=args.bootstrap,
                analysis_seed=args.analysis_seed,
            )
        )

    effects = pd.DataFrame(effect_rows)
    binary_effects = pd.DataFrame(binary_rows)
    per_seed = pd.DataFrame(per_seed_rows)
    heterogeneity = pd.DataFrame(heterogeneity_rows)

    effects_path = os.path.join(args.output_dir, "paired_effects.csv")
    binary_path = os.path.join(args.output_dir, "paired_binary_effects.csv")
    deltas_path = os.path.join(args.output_dir, "paired_seed_deltas.csv")
    heterogeneity_path = os.path.join(
        args.output_dir,
        "paired_cohort_heterogeneity.csv",
    )
    report_path = os.path.join(args.output_dir, "paired_report.txt")
    manifest_path = os.path.join(args.output_dir, "analysis_manifest.json")

    effects.to_csv(effects_path, index=False)
    binary_effects.to_csv(binary_path, index=False)
    per_seed.to_csv(deltas_path, index=False)
    heterogeneity.to_csv(heterogeneity_path, index=False)

    report = make_report(effects, binary_effects, heterogeneity, labels)
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report)
    print("\n" + report)

    manifest = {
        "analysis": "AIEF-1.3 paired seed-level statistics",
        "difference_definition": "baseline_minus_control",
        "cohorts": input_manifest,
        "controls": list(CONTROLS),
        "metrics": list(METRICS),
        "primary_metrics_by_control": {
            control: sorted(metrics)
            for control, metrics in PRIMARY_METRICS.items()
        },
        "expected_directions_baseline_minus_control": {
            f"{control}|{metric}": direction
            for (control, metric), direction in EXPECTED_DIRECTIONS.items()
        },
        "relative_change_metrics": sorted(RELATIVE_CHANGE_METRICS),
        "bootstrap_repetitions": args.bootstrap,
        "sign_flip_repetitions": args.sign_flips,
        "analysis_seed": args.analysis_seed,
        "correlation_clip": CORRELATION_CLIP,
        "notes": [
            "Pooled bootstrap is stratified by cohort.",
            "Seeds are paired only within cohort.",
            "Raw paired differences and bootstrap CIs are primary.",
            "Sign-flip tests are supporting symmetry-based tests, not design-based randomization tests.",
            "Cohort heterogeneity is a bootstrap difference of cohort mean paired effects.",
            "Phi is excluded because it is unstable near zero density.",
            "Shuffle correlation comparisons may be non-estimable due to degeneracy.",
        ],
    }
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(f"Saved analysis to {args.output_dir}")
    print(f"  {os.path.basename(effects_path)}")
    print(f"  {os.path.basename(binary_path)}")
    print(f"  {os.path.basename(deltas_path)}")
    print(f"  {os.path.basename(heterogeneity_path)}")
    print(f"  {os.path.basename(report_path)}")
    print(f"  {os.path.basename(manifest_path)}")


if __name__ == "__main__":
    main()
