#!/usr/bin/env python3
"""Seed-level analysis for the AIEF-1.4 memory-carrier ablation.

This script analyzes the frozen 40-seed r2 production result. It treats one
seed as the independent unit and distinguishes preregistered primary contrasts
from secondary and exploratory contrasts.

Outputs include:
* paired branch effects with bootstrap CIs and supporting sign-flip tests;
* per-seed B x EMA interactions;
* immediate/recovery/late summaries and reconstruction times;
* normalized edge-weight Frobenius distances;
* density/similarity trajectory envelopes across seeds;
* projection diagnostics;
* optional trajectory plots.

The B_carrier_only versus full_reset contrast is explicitly labeled
exploratory because those r2 branches used different randomized phase resets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_SCALAR_PATH = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_scalar_summary.csv"
)
DEFAULT_NPZ_PATH = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_OUTPUT_DIR = "aief_1_4_results_analysis"
DEFAULT_BOOTSTRAPS = 20_000
DEFAULT_SIGN_FLIPS = 100_000
DEFAULT_ANALYSIS_SEED = 20260715
ZERO_TOL = 1e-12

BRANCHES = (
    "continue",
    "reset_ema",
    "reset_B",
    "reset_B_ema",
    "B_carrier_only",
    "full_reset",
    "future_shuffle",
)

BRANCH_FAMILIES = {
    "continue": "reference",
    "reset_ema": "memory_ablation",
    "reset_B": "memory_ablation",
    "reset_B_ema": "memory_ablation",
    "B_carrier_only": "memory_ablation",
    "full_reset": "memory_ablation",
    "future_shuffle": "future_driver_control",
}

PRIMARY_OUTCOMES = (
    "Weighted_similarity_late",
    "Retention_contrast_late",
    "P_mean_late",
)

# left minus right throughout the analysis.
CONTRASTS = (
    ("continue", "reset_B", "primary"),
    ("continue", "reset_ema", "primary"),
    ("reset_B", "reset_B_ema", "primary"),
    ("continue", "future_shuffle", "primary_driver_control"),
    (
        "B_carrier_only",
        "full_reset",
        "exploratory_unmatched_phase_reset",
    ),
    ("continue", "reset_B_ema", "secondary"),
    ("continue", "B_carrier_only", "secondary"),
    ("continue", "full_reset", "secondary"),
    ("reset_B_ema", "full_reset", "secondary_phase_history"),
)

OUTCOMES = (
    "Weighted_similarity_late",
    "Retention_contrast_late",
    "P_mean_late",
    "D_B_final",
    "P_mean_full",
    "P_mean_immediate",
    "P_mean_recovery",
    "Weighted_similarity_final",
    "Jaccard_final",
    "Retention_selected_late",
    "Emergence_unselected_late",
    "Total_edge_weight",
    "Effective_edges",
    "Weight_gini",
    "Weight_entropy",
    "r_mean_future",
    "r_mean_late",
    "Projection_active_fraction",
    "Projection_norm_mean_active",
    "Projection_relative_state_mean_active",
    "Projection_relative_update_mean_active",
    "Time_to_50pct_continue_final_density",
    "Time_to_90pct_continue_final_density",
    "Time_to_50pct_continue_late_similarity",
    "Time_to_90pct_continue_late_similarity",
    "Minimum_similarity",
    "Time_to_similarity_below_0_9",
    "Time_to_similarity_below_0_5",
)

INTERACTION_OUTCOMES = (
    "Weighted_similarity_late",
    "Retention_contrast_late",
    "P_mean_late",
    "P_mean_immediate",
    "P_mean_recovery",
    "D_B_final",
)

PROJECTION_METRICS = (
    "Pre_gap_violation_fraction",
    "Projection_active_fraction",
    "Projection_active_given_violation",
    "Projection_norm_mean_active",
    "Projection_norm_max",
    "Projection_relative_state_mean_active",
    "Projection_relative_state_max",
    "Projection_relative_update_mean_active",
    "Projection_relative_update_max",
    "G_min_pre_future",
    "G_min_future",
)

FROBENIUS_COMPARISONS = (
    ("B_final", "continue_final"),
    ("B_mean_late", "continue_late_mean"),
    ("B_final", "split"),
    ("B_mean_late", "split"),
)


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rng_for(seed: int, label: str) -> np.random.Generator:
    digest = hashlib.sha256(f"{seed}|{label}".encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "little"))


def load_scalar(path: str) -> pd.DataFrame:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    frame = pd.read_csv(path, dtype={"seed": str})
    required = {"seed", "seed_index", "branch", *PRIMARY_OUTCOMES}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"scalar CSV missing columns: {sorted(missing)}")
    frame["seed"] = frame["seed"].astype(str)
    frame["branch"] = frame["branch"].astype(str)
    duplicate = frame.duplicated(["seed", "branch"], keep=False)
    if duplicate.any():
        raise ValueError("duplicate seed/branch rows in scalar CSV")

    branch_set = set(frame["branch"])
    if branch_set != set(BRANCHES):
        raise ValueError(
            f"branch set mismatch: missing={set(BRANCHES)-branch_set}, "
            f"extra={branch_set-set(BRANCHES)}"
        )
    reference_seeds = set(frame.loc[frame["branch"] == "continue", "seed"])
    for branch in BRANCHES:
        seeds = set(frame.loc[frame["branch"] == branch, "seed"])
        if seeds != reference_seeds:
            raise ValueError(f"seed-set mismatch for branch {branch}")
    return frame


def bootstrap_mean_ci(
    values: np.ndarray,
    repetitions: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if not len(values) or repetitions <= 0:
        return np.nan, np.nan
    indices = rng.integers(0, len(values), size=(repetitions, len(values)))
    samples = np.mean(values[indices], axis=1)
    low, high = np.percentile(samples, [2.5, 97.5])
    return float(low), float(high)


def sign_flip_pvalue(
    values: np.ndarray,
    repetitions: int,
    rng: np.random.Generator,
    batch_size: int = 5_000,
) -> float:
    values = np.asarray(values, dtype=float)
    if not len(values) or repetitions <= 0:
        return np.nan
    if np.allclose(values, 0.0, rtol=0.0, atol=0.0):
        return 1.0
    observed = abs(float(np.mean(values)))
    extreme = 0
    completed = 0
    while completed < repetitions:
        size = min(batch_size, repetitions - completed)
        signs = rng.integers(0, 2, size=(size, len(values)), dtype=np.int8)
        signs = signs * 2 - 1
        simulated = np.abs(np.mean(signs * values, axis=1))
        extreme += int(np.count_nonzero(simulated >= observed - 1e-15))
        completed += size
    return float((extreme + 1) / (repetitions + 1))


def paired_dz(mean: float, std: float) -> float:
    if not np.isfinite(mean) or not np.isfinite(std):
        return np.nan
    if std <= 1e-15:
        return 0.0 if abs(mean) <= 1e-15 else np.nan
    return float(mean / std)


def summarize_paired_values(
    values: np.ndarray,
    *,
    label: str,
    bootstraps: int,
    sign_flips: int,
    analysis_seed: int,
) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return {
            "n_valid": 0,
            "mean": np.nan,
            "median": np.nan,
            "std": np.nan,
            "ci95_low": np.nan,
            "ci95_high": np.nan,
            "paired_cohen_dz": np.nan,
            "fraction_positive": np.nan,
            "fraction_negative": np.nan,
            "sign_flip_p_supporting": np.nan,
        }
    mean = float(np.mean(values))
    std = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    ci_low, ci_high = bootstrap_mean_ci(
        values,
        bootstraps,
        rng_for(analysis_seed, f"bootstrap|{label}"),
    )
    return {
        "n_valid": int(len(values)),
        "mean": mean,
        "median": float(np.median(values)),
        "std": std,
        "ci95_low": ci_low,
        "ci95_high": ci_high,
        "paired_cohen_dz": paired_dz(mean, std),
        "fraction_positive": float(np.mean(values > 1e-15)),
        "fraction_negative": float(np.mean(values < -1e-15)),
        "sign_flip_p_supporting": sign_flip_pvalue(
            values,
            sign_flips,
            rng_for(analysis_seed, f"sign|{label}"),
        ),
    }


def paired_contrast_tables(
    frame: pd.DataFrame,
    *,
    bootstraps: int,
    sign_flips: int,
    analysis_seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []

    indexed = {
        branch: frame.loc[frame["branch"] == branch].set_index("seed")
        for branch in BRANCHES
    }

    for left, right, role in CONTRASTS:
        shared = sorted(set(indexed[left].index) & set(indexed[right].index), key=int)
        for outcome in OUTCOMES:
            if outcome not in frame.columns:
                continue
            left_values = pd.to_numeric(
                indexed[left].loc[shared, outcome], errors="coerce"
            ).to_numpy(float)
            right_values = pd.to_numeric(
                indexed[right].loc[shared, outcome], errors="coerce"
            ).to_numpy(float)
            valid = np.isfinite(left_values) & np.isfinite(right_values)
            differences = left_values[valid] - right_values[valid]
            stats = summarize_paired_values(
                differences,
                label=f"contrast|{left}|{right}|{outcome}",
                bootstraps=bootstraps,
                sign_flips=sign_flips,
                analysis_seed=analysis_seed,
            )
            summary_rows.append(
                {
                    "left_branch": left,
                    "right_branch": right,
                    "difference_definition": "left_minus_right",
                    "contrast_role": role,
                    "outcome": outcome,
                    "outcome_role": "primary"
                    if outcome in PRIMARY_OUTCOMES
                    else "secondary",
                    "n_total": int(len(shared)),
                    "left_mean": float(np.mean(left_values[valid]))
                    if np.any(valid)
                    else np.nan,
                    "right_mean": float(np.mean(right_values[valid]))
                    if np.any(valid)
                    else np.nan,
                    **stats,
                }
            )

            valid_seeds = np.asarray(shared, dtype=object)[valid]
            for seed, left_value, right_value, difference in zip(
                valid_seeds,
                left_values[valid],
                right_values[valid],
                differences,
            ):
                seed_rows.append(
                    {
                        "seed": seed,
                        "left_branch": left,
                        "right_branch": right,
                        "contrast_role": role,
                        "outcome": outcome,
                        "left_value": float(left_value),
                        "right_value": float(right_value),
                        "difference_left_minus_right": float(difference),
                    }
                )

    return pd.DataFrame(summary_rows), pd.DataFrame(seed_rows)


def interaction_tables(
    frame: pd.DataFrame,
    *,
    bootstraps: int,
    sign_flips: int,
    analysis_seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pivot = frame.pivot(index="seed", columns="branch")
    summary_rows: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []

    for outcome in INTERACTION_OUTCOMES:
        if outcome not in frame.columns:
            continue
        continue_values = pd.to_numeric(
            pivot[outcome]["continue"], errors="coerce"
        ).to_numpy(float)
        reset_ema = pd.to_numeric(
            pivot[outcome]["reset_ema"], errors="coerce"
        ).to_numpy(float)
        reset_B = pd.to_numeric(
            pivot[outcome]["reset_B"], errors="coerce"
        ).to_numpy(float)
        reset_both = pd.to_numeric(
            pivot[outcome]["reset_B_ema"], errors="coerce"
        ).to_numpy(float)
        interaction = continue_values - reset_ema - reset_B + reset_both
        valid = np.isfinite(interaction)
        values = interaction[valid]
        stats = summarize_paired_values(
            values,
            label=f"interaction|{outcome}",
            bootstraps=bootstraps,
            sign_flips=sign_flips,
            analysis_seed=analysis_seed,
        )
        summary_rows.append(
            {
                "interaction": "continue-reset_ema-reset_B+reset_B_ema",
                "outcome": outcome,
                "outcome_role": "primary"
                if outcome in PRIMARY_OUTCOMES
                else "secondary",
                "n_total": int(len(interaction)),
                **stats,
            }
        )
        valid_seeds = pivot.index.to_numpy()[valid]
        for seed, value in zip(valid_seeds, values):
            seed_rows.append(
                {
                    "seed": str(seed),
                    "outcome": outcome,
                    "interaction_value": float(value),
                }
            )
    return pd.DataFrame(summary_rows), pd.DataFrame(seed_rows)


def npz_key(branch: str, seed: str, metric: str) -> str:
    return f"{branch}_seed_{seed}_{metric}"


def prefix_key(seed: str, metric: str) -> str:
    return f"prefix_seed_{seed}_{metric}"


def normalized_distance(x: np.ndarray, reference: np.ndarray) -> float:
    x_edges = np.asarray(x, dtype=float)[np.triu_indices(x.shape[0], k=1)]
    ref_edges = np.asarray(reference, dtype=float)[
        np.triu_indices(reference.shape[0], k=1)
    ]
    denominator = max(float(np.linalg.norm(ref_edges)), ZERO_TOL)
    return float(np.linalg.norm(x_edges - ref_edges) / denominator)


def frobenius_tables(
    scalar: pd.DataFrame,
    npz_path: str,
    *,
    bootstraps: int,
    sign_flips: int,
    analysis_seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    per_seed_rows: list[dict[str, Any]] = []
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )

    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            B_split = np.asarray(data[prefix_key(seed, "B_at_split")], dtype=float)
            continue_final = np.asarray(
                data[npz_key("continue", seed, "B_final")], dtype=float
            )
            continue_late = np.asarray(
                data[npz_key("continue", seed, "B_mean_late")], dtype=float
            )

            for branch in BRANCHES:
                branch_final = np.asarray(
                    data[npz_key(branch, seed, "B_final")], dtype=float
                )
                branch_late = np.asarray(
                    data[npz_key(branch, seed, "B_mean_late")], dtype=float
                )
                comparisons = {
                    "final_vs_continue_final": normalized_distance(
                        branch_final, continue_final
                    ),
                    "late_mean_vs_continue_late_mean": normalized_distance(
                        branch_late, continue_late
                    ),
                    "final_vs_split": normalized_distance(branch_final, B_split),
                    "late_mean_vs_split": normalized_distance(branch_late, B_split),
                }
                for metric, value in comparisons.items():
                    per_seed_rows.append(
                        {
                            "seed": seed,
                            "branch": branch,
                            "branch_family": BRANCH_FAMILIES[branch],
                            "metric": metric,
                            "normalized_edge_frobenius_distance": value,
                        }
                    )

    per_seed = pd.DataFrame(per_seed_rows)
    summary_rows: list[dict[str, Any]] = []
    for (branch, metric), group in per_seed.groupby(["branch", "metric"]):
        values = group["normalized_edge_frobenius_distance"].to_numpy(float)
        stats = summarize_paired_values(
            values,
            label=f"frobenius|{branch}|{metric}",
            bootstraps=bootstraps,
            sign_flips=sign_flips,
            analysis_seed=analysis_seed,
        )
        summary_rows.append(
            {
                "branch": branch,
                "branch_family": BRANCH_FAMILIES[branch],
                "metric": metric,
                **stats,
            }
        )
    return pd.DataFrame(summary_rows), per_seed


def trajectory_tables(
    scalar: pd.DataFrame,
    npz_path: str,
) -> pd.DataFrame:
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    rows: list[dict[str, Any]] = []

    with np.load(npz_path, allow_pickle=False) as data:
        for branch in BRANCHES:
            times_reference: np.ndarray | None = None
            metric_arrays: dict[str, list[np.ndarray]] = {
                "density": [],
                "similarity": [],
            }
            for seed in seeds:
                times = np.asarray(
                    data[npz_key(branch, seed, "sample_times")], dtype=float
                )
                density = np.asarray(
                    data[npz_key(branch, seed, "density_trajectory")], dtype=float
                )
                similarity = np.asarray(
                    data[npz_key(branch, seed, "similarity_trajectory")], dtype=float
                )
                if times_reference is None:
                    times_reference = times
                elif not np.array_equal(times_reference, times):
                    raise ValueError(f"trajectory times differ for {branch}, seed={seed}")
                metric_arrays["density"].append(density)
                metric_arrays["similarity"].append(similarity)

            assert times_reference is not None
            for metric, arrays in metric_arrays.items():
                matrix = np.stack(arrays)
                for index, time_value in enumerate(times_reference):
                    values = matrix[:, index]
                    values = values[np.isfinite(values)]
                    rows.append(
                        {
                            "branch": branch,
                            "branch_family": BRANCH_FAMILIES[branch],
                            "metric": metric,
                            "time_since_split": float(time_value),
                            "n_valid": int(len(values)),
                            "mean": float(np.mean(values)) if len(values) else np.nan,
                            "median": float(np.median(values)) if len(values) else np.nan,
                            "std": float(np.std(values)) if len(values) else np.nan,
                            "seed_q025": float(np.quantile(values, 0.025))
                            if len(values)
                            else np.nan,
                            "seed_q975": float(np.quantile(values, 0.975))
                            if len(values)
                            else np.nan,
                        }
                    )
    return pd.DataFrame(rows)


def projection_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for branch in BRANCHES:
        group = frame.loc[frame["branch"] == branch]
        for metric in PROJECTION_METRICS:
            if metric not in frame.columns:
                continue
            values = pd.to_numeric(group[metric], errors="coerce").to_numpy(float)
            finite = values[np.isfinite(values)]
            rows.append(
                {
                    "branch": branch,
                    "branch_family": BRANCH_FAMILIES[branch],
                    "metric": metric,
                    "n_total": int(len(values)),
                    "n_valid": int(len(finite)),
                    "mean": float(np.mean(finite)) if len(finite) else np.nan,
                    "std": float(np.std(finite)) if len(finite) else np.nan,
                    "median": float(np.median(finite)) if len(finite) else np.nan,
                    "minimum": float(np.min(finite)) if len(finite) else np.nan,
                    "maximum": float(np.max(finite)) if len(finite) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def plot_trajectories(trajectory: pd.DataFrame, output_dir: str) -> list[str]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is unavailable; skipping plots")
        return []

    paths: list[str] = []
    for metric, ylabel in (
        ("density", "Threshold density"),
        ("similarity", "Weighted topology cosine similarity"),
    ):
        fig, ax = plt.subplots(figsize=(11, 7))
        for branch in BRANCHES:
            block = trajectory.loc[
                (trajectory["branch"] == branch)
                & (trajectory["metric"] == metric)
            ]
            ax.plot(
                block["time_since_split"],
                block["mean"],
                label=branch,
                linewidth=2,
            )
            ax.fill_between(
                block["time_since_split"],
                block["seed_q025"],
                block["seed_q975"],
                alpha=0.10,
            )
        ax.set_xlabel("Time since split")
        ax.set_ylabel(ylabel)
        ax.set_title(f"AIEF-1.4 {metric} trajectories across seeds")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8, ncol=2)
        fig.tight_layout()
        path = os.path.join(output_dir, f"{metric}_trajectories.png")
        fig.savefig(path, dpi=180)
        plt.close(fig)
        paths.append(path)
    return paths


def format_number(value: Any, digits: int = 6) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return "nan" if not np.isfinite(number) else f"{number:.{digits}f}"


def make_report(
    effects: pd.DataFrame,
    interactions: pd.DataFrame,
    frobenius: pd.DataFrame,
    projection: pd.DataFrame,
    seed_count: int,
) -> str:
    lines = [
        "AIEF-1.4 seed-level results analysis",
        "====================================",
        "",
        f"Seeds: {seed_count}",
        "Differences are left branch minus right branch.",
        "Bootstrap CIs are primary; sign-flip p-values are supporting.",
        "B_carrier_only vs full_reset is exploratory because r2 used unmatched phase resets.",
        "",
        "Primary contrasts",
        "-----------------",
    ]

    selected = effects.loc[
        effects["contrast_role"].isin(["primary", "primary_driver_control"])
        & effects["outcome"].isin(PRIMARY_OUTCOMES)
    ]
    for _, row in selected.iterrows():
        lines.append(
            f"  {row['left_branch']} - {row['right_branch']} / {row['outcome']}: "
            f"n={int(row['n_valid'])}, delta={format_number(row['mean'])}, "
            f"95% CI=[{format_number(row['ci95_low'])}, "
            f"{format_number(row['ci95_high'])}], "
            f"dz={format_number(row['paired_cohen_dz'], 3)}, "
            f"positive={format_number(row['fraction_positive'], 3)}, "
            f"p_sign={format_number(row['sign_flip_p_supporting'], 6)}"
        )

    lines.extend(["", "B x EMA interactions", "--------------------"])
    for _, row in interactions.loc[
        interactions["outcome"].isin(PRIMARY_OUTCOMES)
    ].iterrows():
        lines.append(
            f"  {row['outcome']}: delta={format_number(row['mean'])}, "
            f"95% CI=[{format_number(row['ci95_low'])}, "
            f"{format_number(row['ci95_high'])}], "
            f"dz={format_number(row['paired_cohen_dz'], 3)}"
        )

    lines.extend(["", "Exploratory matched-state warning", "---------------------------------"])
    exploratory = effects.loc[
        (effects["left_branch"] == "B_carrier_only")
        & (effects["right_branch"] == "full_reset")
        & effects["outcome"].isin(PRIMARY_OUTCOMES)
    ]
    for _, row in exploratory.iterrows():
        lines.append(
            f"  {row['outcome']}: delta={format_number(row['mean'])}, "
            f"95% CI=[{format_number(row['ci95_low'])}, "
            f"{format_number(row['ci95_high'])}] (unmatched phase reset)"
        )

    lines.extend(["", "Magnitude-sensitive distances", "-----------------------------"])
    selected_frob = frobenius.loc[
        frobenius["metric"] == "late_mean_vs_continue_late_mean"
    ]
    for _, row in selected_frob.iterrows():
        lines.append(
            f"  {row['branch']}: normalized distance="
            f"{format_number(row['mean'])}, "
            f"95% CI=[{format_number(row['ci95_low'])}, "
            f"{format_number(row['ci95_high'])}]"
        )

    lines.extend(["", "Projection-relative-to-update", "-----------------------------"])
    selected_projection = projection.loc[
        projection["metric"] == "Projection_relative_update_mean_active"
    ]
    for _, row in selected_projection.iterrows():
        lines.append(
            f"  {row['branch']}: mean={format_number(row['mean'])}, "
            f"median={format_number(row['median'])}, "
            f"max={format_number(row['maximum'])}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Late reconstruction is not equivalent to immediate memory retention.",
            "* Future shuffle is a driver-identity intervention, not a memory-state ablation.",
            "* Similarity quantifies orientation; normalized Frobenius distance also captures magnitude.",
            "* Full reset preserves the model, node identities, frequencies, and adaptation law.",
            "* The r2 B_carrier_only/full_reset comparison must remain exploratory until phase resets are matched.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scalar", default=DEFAULT_SCALAR_PATH)
    parser.add_argument("--npz", default=DEFAULT_NPZ_PATH)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--bootstrap", type=int, default=DEFAULT_BOOTSTRAPS)
    parser.add_argument("--sign-flips", type=int, default=DEFAULT_SIGN_FLIPS)
    parser.add_argument("--analysis-seed", type=int, default=DEFAULT_ANALYSIS_SEED)
    parser.add_argument("--no-plots", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if not os.path.isfile(args.npz):
        raise FileNotFoundError(args.npz)
    if args.bootstrap < 0 or args.sign_flips < 0:
        raise ValueError("bootstrap/sign-flip repetitions must be nonnegative")
    os.makedirs(args.output_dir, exist_ok=True)

    scalar = load_scalar(args.scalar)
    seed_count = int(np.sum(scalar["branch"] == "continue"))
    print(f"Loaded {seed_count} paired seeds")

    effects, per_seed_effects = paired_contrast_tables(
        scalar,
        bootstraps=args.bootstrap,
        sign_flips=args.sign_flips,
        analysis_seed=args.analysis_seed,
    )
    interactions, per_seed_interactions = interaction_tables(
        scalar,
        bootstraps=args.bootstrap,
        sign_flips=args.sign_flips,
        analysis_seed=args.analysis_seed,
    )
    frobenius, per_seed_frobenius = frobenius_tables(
        scalar,
        args.npz,
        bootstraps=args.bootstrap,
        sign_flips=args.sign_flips,
        analysis_seed=args.analysis_seed,
    )
    trajectory = trajectory_tables(scalar, args.npz)
    projection = projection_summary(scalar)

    outputs = {
        "paired_branch_effects.csv": effects,
        "paired_branch_effects_by_seed.csv": per_seed_effects,
        "B_EMA_interactions.csv": interactions,
        "B_EMA_interactions_by_seed.csv": per_seed_interactions,
        "frobenius_distance_summary.csv": frobenius,
        "frobenius_distances_by_seed.csv": per_seed_frobenius,
        "trajectory_summary.csv": trajectory,
        "projection_summary.csv": projection,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)

    plot_paths = [] if args.no_plots else plot_trajectories(
        trajectory, args.output_dir
    )
    report = make_report(effects, interactions, frobenius, projection, seed_count)
    report_path = os.path.join(args.output_dir, "AIEF_1_4_analysis_report.txt")
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report)
    print("\n" + report)

    manifest = {
        "analysis": "AIEF-1.4 seed-level memory-ablation results",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "seed_count": seed_count,
        "branches": list(BRANCHES),
        "branch_families": BRANCH_FAMILIES,
        "primary_outcomes": list(PRIMARY_OUTCOMES),
        "contrasts": [list(item) for item in CONTRASTS],
        "interaction": "continue-reset_ema-reset_B+reset_B_ema",
        "bootstrap_repetitions": args.bootstrap,
        "sign_flip_repetitions": args.sign_flips,
        "analysis_seed": args.analysis_seed,
        "trajectory_intervals": "empirical seed quantiles, not confidence intervals",
        "plots": [str(Path(path).resolve()) for path in plot_paths],
        "warnings": [
            "B_carrier_only and full_reset used unmatched randomized phase resets in r2.",
            "Sign-flip p-values are supporting symmetry-based tests.",
            "Late reconstruction is not equivalent to immediate memory retention.",
        ],
    }
    with open(
        os.path.join(args.output_dir, "analysis_manifest.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(f"Saved analysis to {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
