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
        "runs/c3da1ac707bf/AIEF_1_3_c3da1ac707bf_scalar_summary.csv",
    ),
    (
        "validation_B",
        "runs/73dca37cf93f/AIEF_1_3_73dca37cf93f_scalar_summary.csv",
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
    """Two-sided Monte Carlo paired sign-flip test for a mean difference."""
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

    baseline = pd.to_numeric(paired[baseline_column], errors="coerce").to_numpy(float)
    comparison = pd.to_numeric(paired[control_column], errors="coerce").to_numpy(float)
    valid = np.isfinite(baseline) & np.isfinite(comparison)
    if not np.any(valid):
        return {
            "scope": cohort_scope,
            "control": control,
            "metric": metric,
            "difference_definition": "baseline_minus_control",
            "n_pairs": 0,
            "baseline_mean": np.nan,
            "control_mean": np.nan,
            "mean_difference": np.nan,
            "median_difference": np.nan,
            "std_difference": np.nan,
            "ci95_low": np.nan,
            "ci95_high": np.nan,
            "fraction_positive": np.nan,
            "fraction_negative": np.nan,
            "fraction_zero": np.nan,
            "sign_flip_p_two_sided": np.nan,
        }, []

    baseline = baseline[valid]
    comparison = comparison[valid]
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

    tolerance = 1e-15
    row: dict[str, object] = {
        "scope": cohort_scope,
        "control": control,
        "metric": metric,
        "difference_definition": "baseline_minus_control",
        "n_pairs": int(len(differences)),
        "baseline_mean": float(np.mean(baseline)),
        "control_mean": float(np.mean(comparison)),
        "mean_difference": float(np.mean(differences)),
        "median_difference": float(np.median(differences)),
        "std_difference": float(np.std(differences, ddof=1))
        if len(differences) > 1
        else 0.0,
        "ci95_low": ci_low,
        "ci95_high": ci_high,
        "fraction_positive": float(np.mean(differences > tolerance)),
        "fraction_negative": float(np.mean(differences < -tolerance)),
        "fraction_zero": float(np.mean(np.abs(differences) <= tolerance)),
        "sign_flip_p_two_sided": p_value,
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

    return {
        "scope": cohort_scope,
        "control": control,
        "metric": "P_degenerate",
        "difference_definition": "control_rate_minus_baseline_rate",
        "n_pairs": int(len(baseline)),
        "baseline_rate": float(np.mean(baseline)),
        "control_rate": float(np.mean(comparison)),
        "rate_difference": float(np.mean(comparison) - np.mean(baseline)),
        "both_nondegenerate": int(np.count_nonzero(~baseline & ~comparison)),
        "baseline_only_degenerate": baseline_only,
        "control_only_degenerate": control_only,
        "both_degenerate": int(np.count_nonzero(baseline & comparison)),
        "mcnemar_exact_p_two_sided": exact_mcnemar_pvalue(
            baseline_only,
            control_only,
        ),
    }


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
    cohort_labels: list[str],
) -> str:
    lines = [
        "AIEF-1.3 paired seed-level analysis",
        "====================================",
        "",
        "Continuous differences are baseline minus control.",
        "Pooled confidence intervals use a stratified paired bootstrap.",
        "Sign-flip p-values are two-sided Monte Carlo tests.",
        "Correlation comparisons are non-estimable when either member is degenerate.",
        "",
        f"Cohorts: {', '.join(cohort_labels)}",
        "",
    ]

    for control in CONTROLS:
        lines.append(f"{control}")
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
                f"  {metric}: n={int(row['n_pairs'])}, "
                f"base={format_number(row['baseline_mean'])}, "
                f"control={format_number(row['control_mean'])}, "
                f"delta={format_number(row['mean_difference'])}, "
                f"95% CI=[{format_number(row['ci95_low'])}, "
                f"{format_number(row['ci95_high'])}], "
                f"positive={format_number(row['fraction_positive'], 3)}, "
                f"p_sign={format_number(row['sign_flip_p_two_sided'], 6)}"
            )

        binary_set = binary_effects.loc[
            (binary_effects["scope"] == "pooled")
            & (binary_effects["control"] == control)
        ]
        if not binary_set.empty:
            row = binary_set.iloc[0]
            lines.append(
                "  P_degenerate: "
                f"base={format_number(row['baseline_rate'], 3)}, "
                f"control={format_number(row['control_rate'], 3)}, "
                f"delta(control-base)={format_number(row['rate_difference'], 3)}, "
                f"p_McNemar={format_number(row['mcnemar_exact_p_two_sided'], 6)}"
            )
        lines.append("")

    lines.extend(
        [
            "Interpretation notes",
            "--------------------",
            "* Do not compare baseline and shuffle_R using Fisher-z if shuffle_R is degenerate.",
            "* Treat no_gap correlation as conditional on the finite paired subset.",
            "* Phi is intentionally excluded because it is unstable near zero density.",
            "* Cohort-specific rows should be checked before relying on the pooled estimate.",
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

    effects = pd.DataFrame(effect_rows)
    binary_effects = pd.DataFrame(binary_rows)
    per_seed = pd.DataFrame(per_seed_rows)

    effects_path = os.path.join(args.output_dir, "paired_effects.csv")
    binary_path = os.path.join(args.output_dir, "paired_binary_effects.csv")
    deltas_path = os.path.join(args.output_dir, "paired_seed_deltas.csv")
    report_path = os.path.join(args.output_dir, "paired_report.txt")
    manifest_path = os.path.join(args.output_dir, "analysis_manifest.json")

    effects.to_csv(effects_path, index=False)
    binary_effects.to_csv(binary_path, index=False)
    per_seed.to_csv(deltas_path, index=False)

    report = make_report(effects, binary_effects, labels)
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report)
    print("\n" + report)

    manifest = {
        "analysis": "AIEF-1.3 paired seed-level statistics",
        "difference_definition": "baseline_minus_control",
        "cohorts": input_manifest,
        "controls": list(CONTROLS),
        "metrics": list(METRICS),
        "bootstrap_repetitions": args.bootstrap,
        "sign_flip_repetitions": args.sign_flips,
        "analysis_seed": args.analysis_seed,
        "correlation_clip": CORRELATION_CLIP,
        "notes": [
            "Pooled bootstrap is stratified by cohort.",
            "Seeds are paired only within cohort.",
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
    print(f"  {os.path.basename(report_path)}")
    print(f"  {os.path.basename(manifest_path)}")


if __name__ == "__main__":
    main()
