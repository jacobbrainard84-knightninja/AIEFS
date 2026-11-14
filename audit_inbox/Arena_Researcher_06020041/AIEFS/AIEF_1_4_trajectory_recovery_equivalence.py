#!/usr/bin/env python3
"""Trajectory, sustained-recovery, and equivalence analysis for AIEF-1.4 r2.

The script uses the frozen 40-seed production artifacts. It analyzes how each
branch reaches its late state rather than only where it finishes.

Important convention
--------------------
Cosine similarity is undefined when a branch has an exactly zero edge-weight
vector. For recovery/loss calculations only, such NaN samples are mapped to
zero similarity and the number of imputed samples is reported. Raw stored
trajectories are never modified.

Outputs
-------
trajectory_metrics_by_seed.csv
trajectory_metrics_summary.csv
equivalence_tests.csv
trajectory_envelopes.csv
trajectory_recovery_report.txt
analysis_manifest.json
optional PNG figures
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_SCALAR = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_scalar_summary.csv"
)
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_trajectory_recovery"
DEFAULT_BOOTSTRAPS = 20_000
DEFAULT_ANALYSIS_SEED = 20260716

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

# Exploratory practical-equivalence margins. These were chosen after viewing
# r2 outcomes and must not be described as preregistered confirmatory margins.
EQUIVALENCE_SPECS = (
    ("continue", "reset_B", "Weighted_similarity_late", 0.01),
    ("continue", "reset_B", "Retention_contrast_late", 1.0 / 66.0),
    ("continue", "reset_B", "P_mean_late", 1.0 / 66.0),
    ("continue", "reset_ema", "Weighted_similarity_late", 0.01),
    ("continue", "reset_ema", "Retention_contrast_late", 1.0 / 66.0),
    ("continue", "reset_ema", "P_mean_late", 1.0 / 66.0),
)

ZERO_TOL = 1e-12


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rng_for(seed: int, label: str) -> np.random.Generator:
    digest = hashlib.sha256(f"{seed}|{label}".encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "little"))


def npz_key(branch: str, seed: str, metric: str) -> str:
    return f"{branch}_seed_{seed}_{metric}"


def load_inputs(
    scalar_path: str,
    manifest_path: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not os.path.isfile(scalar_path):
        raise FileNotFoundError(scalar_path)
    if not os.path.isfile(manifest_path):
        raise FileNotFoundError(manifest_path)

    scalar = pd.read_csv(scalar_path, dtype={"seed": str})
    required = {
        "seed",
        "branch",
        "D_B_final",
        "P_mean_late",
        "Weighted_similarity_late",
        "Retention_contrast_late",
    }
    missing = required - set(scalar.columns)
    if missing:
        raise ValueError(f"scalar CSV missing {sorted(missing)}")
    scalar["seed"] = scalar["seed"].astype(str)
    scalar["branch"] = scalar["branch"].astype(str)
    if scalar.duplicated(["seed", "branch"]).any():
        raise ValueError("duplicate seed/branch rows")

    branch_set = set(scalar["branch"])
    if branch_set != set(BRANCHES):
        raise ValueError(
            f"branch mismatch: missing={set(BRANCHES)-branch_set}, "
            f"extra={branch_set-set(BRANCHES)}"
        )
    reference_seeds = set(scalar.loc[scalar["branch"] == "continue", "seed"])
    for branch in BRANCHES:
        branch_seeds = set(scalar.loc[scalar["branch"] == branch, "seed"])
        if branch_seeds != reference_seeds:
            raise ValueError(f"seed-set mismatch for {branch}")

    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    return scalar, manifest


def bootstrap_mean_interval(
    values: np.ndarray,
    repetitions: int,
    rng: np.random.Generator,
    confidence: float,
) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values) or repetitions <= 0:
        return np.nan, np.nan
    indices = rng.integers(0, len(values), size=(repetitions, len(values)))
    samples = np.mean(values[indices], axis=1)
    alpha = (1.0 - confidence) / 2.0
    low, high = np.quantile(samples, [alpha, 1.0 - alpha])
    return float(low), float(high)


def time_to_at_least(
    times: np.ndarray,
    values: np.ndarray,
    threshold: float,
) -> float:
    indices = np.flatnonzero(np.isfinite(values) & (values >= threshold))
    return float(times[indices[0]]) if len(indices) else np.nan


def first_time_sustained_for_rest(
    times: np.ndarray,
    values: np.ndarray,
    threshold: float,
) -> float:
    condition = np.isfinite(values) & (values >= threshold)
    if not len(condition):
        return np.nan
    suffix_all = np.logical_and.accumulate(condition[::-1])[::-1]
    indices = np.flatnonzero(suffix_all)
    return float(times[indices[0]]) if len(indices) else np.nan


def first_time_held_for_duration(
    times: np.ndarray,
    values: np.ndarray,
    threshold: float,
    duration: float,
) -> float:
    if len(times) < 2:
        return np.nan
    step = float(np.median(np.diff(times)))
    required = max(1, int(math.ceil(duration / step)))
    condition = np.isfinite(values) & (values >= threshold)
    if required > len(condition):
        return np.nan
    # Convolution is safe here because trajectories are short (~640 samples).
    run_counts = np.convolve(condition.astype(int), np.ones(required, dtype=int), "valid")
    indices = np.flatnonzero(run_counts == required)
    return float(times[indices[0]]) if len(indices) else np.nan


def integrate(times: np.ndarray, values: np.ndarray) -> float:
    if len(times) < 2:
        return np.nan
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(values, times))
    return float(np.trapz(values, times))


def normalized_edge_distance(x: np.ndarray, reference: np.ndarray) -> float:
    edges = np.triu_indices(x.shape[0], k=1)
    x_edges = np.asarray(x, dtype=float)[edges]
    reference_edges = np.asarray(reference, dtype=float)[edges]
    denominator = max(float(np.linalg.norm(reference_edges)), ZERO_TOL)
    return float(np.linalg.norm(x_edges - reference_edges) / denominator)


def horizon_masks(
    times: np.ndarray,
    window_time: float,
    recovery_end_time: float,
) -> dict[str, np.ndarray]:
    return {
        "immediate": times <= window_time + 1e-12,
        "recovery": (times > window_time) & (times <= recovery_end_time + 1e-12),
        "late": times > recovery_end_time,
        "full": np.ones(len(times), dtype=bool),
    }


def summarize_seed_trajectory(
    *,
    seed: str,
    branch: str,
    times: np.ndarray,
    density: np.ndarray,
    similarity_raw: np.ndarray,
    continue_density: np.ndarray,
    continue_similarity: np.ndarray,
    reference_final_density: float,
    reference_late_similarity: float,
    window_time: float,
    recovery_end_time: float,
) -> dict[str, Any]:
    if not (
        len(times)
        == len(density)
        == len(similarity_raw)
        == len(continue_density)
        == len(continue_similarity)
    ):
        raise ValueError(f"trajectory length mismatch for {branch}, seed={seed}")

    # Zero-vector cosine is undefined. For recovery/loss only, treat it as no
    # retained topology and report how often this convention was invoked.
    similarity_nan_count = int(np.sum(~np.isfinite(similarity_raw)))
    similarity = np.nan_to_num(similarity_raw, nan=0.0)
    continue_similarity_filled = np.nan_to_num(continue_similarity, nan=0.0)

    similarity_target_50 = 0.5 * reference_late_similarity
    similarity_target_90 = 0.9 * reference_late_similarity
    density_target_50 = 0.5 * reference_final_density
    density_target_90 = 0.9 * reference_final_density

    duration = float(times[-1] - times[0]) if len(times) > 1 else np.nan
    similarity_deficit = np.maximum(0.0, continue_similarity_filled - similarity)
    density_deficit = np.maximum(0.0, continue_density - density)
    density_excess = np.maximum(0.0, density - continue_density)

    row: dict[str, Any] = {
        "seed": seed,
        "branch": branch,
        "branch_family": BRANCH_FAMILIES[branch],
        "similarity_nan_samples_imputed_zero": similarity_nan_count,
        "minimum_similarity": float(np.min(similarity)),
        "minimum_density": float(np.min(density)),
        "time_to_similarity_50": time_to_at_least(
            times, similarity, similarity_target_50
        ),
        "time_to_similarity_90": time_to_at_least(
            times, similarity, similarity_target_90
        ),
        "time_to_density_50": time_to_at_least(
            times, density, density_target_50
        ),
        "time_to_density_90": time_to_at_least(
            times, density, density_target_90
        ),
        "sustained_similarity_50_rest": first_time_sustained_for_rest(
            times, similarity, similarity_target_50
        ),
        "sustained_similarity_90_rest": first_time_sustained_for_rest(
            times, similarity, similarity_target_90
        ),
        "sustained_density_50_rest": first_time_sustained_for_rest(
            times, density, density_target_50
        ),
        "sustained_density_90_rest": first_time_sustained_for_rest(
            times, density, density_target_90
        ),
        "held_similarity_90_for_1Twindow": first_time_held_for_duration(
            times, similarity, similarity_target_90, window_time
        ),
        "held_density_90_for_1Twindow": first_time_held_for_duration(
            times, density, density_target_90, window_time
        ),
        "AUC_similarity_deficit_vs_continue": integrate(times, similarity_deficit),
        "AUC_density_deficit_vs_continue": integrate(times, density_deficit),
        "AUC_density_excess_vs_continue": integrate(times, density_excess),
        "Mean_similarity_deficit_vs_continue": (
            integrate(times, similarity_deficit) / duration
            if np.isfinite(duration) and duration > 0
            else np.nan
        ),
        "Mean_density_deficit_vs_continue": (
            integrate(times, density_deficit) / duration
            if np.isfinite(duration) and duration > 0
            else np.nan
        ),
    }

    masks = horizon_masks(times, window_time, recovery_end_time)
    for horizon, mask in masks.items():
        row[f"sampled_similarity_mean_{horizon}"] = (
            float(np.mean(similarity[mask])) if np.any(mask) else np.nan
        )
        row[f"sampled_density_mean_{horizon}"] = (
            float(np.mean(density[mask])) if np.any(mask) else np.nan
        )
    return row


def trajectory_analysis(
    scalar: pd.DataFrame,
    npz_path: str,
    manifest: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dt = float(manifest["model"]["dt"])
    window_time = float(manifest["protocol"]["window_steps"]) * dt
    recovery_end_time = float(manifest["protocol"]["recovery_end"]) * dt
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    scalar_index = scalar.set_index(["seed", "branch"])
    seed_rows: list[dict[str, Any]] = []
    envelope_rows: list[dict[str, Any]] = []

    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            continue_times = np.asarray(
                data[npz_key("continue", seed, "sample_times")], dtype=float
            )
            continue_density = np.asarray(
                data[npz_key("continue", seed, "density_trajectory")], dtype=float
            )
            continue_similarity = np.asarray(
                data[npz_key("continue", seed, "similarity_trajectory")], dtype=float
            )
            reference_final_density = float(
                scalar_index.loc[(seed, "continue"), "D_B_final"]
            )
            reference_late_similarity = float(
                scalar_index.loc[(seed, "continue"), "Weighted_similarity_late"]
            )

            for branch in BRANCHES:
                times = np.asarray(
                    data[npz_key(branch, seed, "sample_times")], dtype=float
                )
                density = np.asarray(
                    data[npz_key(branch, seed, "density_trajectory")], dtype=float
                )
                similarity = np.asarray(
                    data[npz_key(branch, seed, "similarity_trajectory")], dtype=float
                )
                if not np.array_equal(times, continue_times):
                    raise ValueError(f"time grid mismatch for {branch}, seed={seed}")
                seed_rows.append(
                    summarize_seed_trajectory(
                        seed=seed,
                        branch=branch,
                        times=times,
                        density=density,
                        similarity_raw=similarity,
                        continue_density=continue_density,
                        continue_similarity=continue_similarity,
                        reference_final_density=reference_final_density,
                        reference_late_similarity=reference_late_similarity,
                        window_time=window_time,
                        recovery_end_time=recovery_end_time,
                    )
                )

        # Across-seed trajectory envelopes.
        for branch in BRANCHES:
            times_reference: np.ndarray | None = None
            stored: dict[str, list[np.ndarray]] = {"density": [], "similarity": []}
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
                    raise ValueError(f"time mismatch for {branch}")
                stored["density"].append(density)
                stored["similarity"].append(
                    np.nan_to_num(similarity, nan=0.0)
                )

            assert times_reference is not None
            for metric, arrays in stored.items():
                matrix = np.stack(arrays)
                for index, time_value in enumerate(times_reference):
                    values = matrix[:, index]
                    envelope_rows.append(
                        {
                            "branch": branch,
                            "branch_family": BRANCH_FAMILIES[branch],
                            "metric": metric,
                            "time_since_split": float(time_value),
                            "mean": float(np.mean(values)),
                            "median": float(np.median(values)),
                            "std": float(np.std(values)),
                            "seed_q025": float(np.quantile(values, 0.025)),
                            "seed_q975": float(np.quantile(values, 0.975)),
                        }
                    )

    return pd.DataFrame(seed_rows), pd.DataFrame(envelope_rows)


def summarize_metrics(
    seed_metrics: pd.DataFrame,
    bootstraps: int,
    analysis_seed: int,
) -> pd.DataFrame:
    identifier_columns = {"seed", "branch", "branch_family"}
    metrics = [
        column
        for column in seed_metrics.columns
        if column not in identifier_columns
    ]
    rows: list[dict[str, Any]] = []
    for branch in BRANCHES:
        group = seed_metrics.loc[seed_metrics["branch"] == branch]
        for metric in metrics:
            raw = pd.to_numeric(group[metric], errors="coerce").to_numpy(float)
            finite = raw[np.isfinite(raw)]
            ci_low, ci_high = bootstrap_mean_interval(
                finite,
                bootstraps,
                rng_for(analysis_seed, f"summary|{branch}|{metric}"),
                confidence=0.95,
            )
            rows.append(
                {
                    "branch": branch,
                    "branch_family": BRANCH_FAMILIES[branch],
                    "metric": metric,
                    "n_total": int(len(raw)),
                    "n_valid": int(len(finite)),
                    "mean": float(np.mean(finite)) if len(finite) else np.nan,
                    "std": float(np.std(finite)) if len(finite) else np.nan,
                    "median": float(np.median(finite)) if len(finite) else np.nan,
                    "minimum": float(np.min(finite)) if len(finite) else np.nan,
                    "maximum": float(np.max(finite)) if len(finite) else np.nan,
                    "ci95_low": ci_low,
                    "ci95_high": ci_high,
                }
            )
    return pd.DataFrame(rows)


def equivalence_analysis(
    scalar: pd.DataFrame,
    npz_path: str,
    bootstraps: int,
    analysis_seed: int,
) -> pd.DataFrame:
    indexed = {
        branch: scalar.loc[scalar["branch"] == branch].set_index("seed")
        for branch in BRANCHES
    }
    rows: list[dict[str, Any]] = []

    for left, right, outcome, margin in EQUIVALENCE_SPECS:
        shared = sorted(set(indexed[left].index) & set(indexed[right].index), key=int)
        left_values = pd.to_numeric(
            indexed[left].loc[shared, outcome], errors="coerce"
        ).to_numpy(float)
        right_values = pd.to_numeric(
            indexed[right].loc[shared, outcome], errors="coerce"
        ).to_numpy(float)
        valid = np.isfinite(left_values) & np.isfinite(right_values)
        differences = left_values[valid] - right_values[valid]
        ci90 = bootstrap_mean_interval(
            differences,
            bootstraps,
            rng_for(analysis_seed, f"equiv90|{left}|{right}|{outcome}"),
            confidence=0.90,
        )
        ci95 = bootstrap_mean_interval(
            differences,
            bootstraps,
            rng_for(analysis_seed, f"equiv95|{left}|{right}|{outcome}"),
            confidence=0.95,
        )
        rows.append(
            {
                "left_branch": left,
                "right_branch": right,
                "outcome": outcome,
                "difference_definition": "left_minus_right",
                "exploratory_margin": margin,
                "n_valid": int(len(differences)),
                "mean_difference": float(np.mean(differences)),
                "ci90_low": ci90[0],
                "ci90_high": ci90[1],
                "ci95_low": ci95[0],
                "ci95_high": ci95[1],
                "equivalent_by_90pct_CI": bool(
                    ci90[0] > -margin and ci90[1] < margin
                ),
                "equivalent_by_95pct_CI_conservative": bool(
                    ci95[0] > -margin and ci95[1] < margin
                ),
                "fraction_seed_differences_within_margin": float(
                    np.mean(np.abs(differences) < margin)
                ),
                "note": "exploratory post-outcome margin",
            }
        )

    # Magnitude-sensitive one-sided equivalence using late mean B distance.
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    with np.load(npz_path, allow_pickle=False) as data:
        for branch in ("reset_B", "reset_ema"):
            distances = []
            for seed in seeds:
                reference = np.asarray(
                    data[npz_key("continue", seed, "B_mean_late")], dtype=float
                )
                current = np.asarray(
                    data[npz_key(branch, seed, "B_mean_late")], dtype=float
                )
                distances.append(normalized_edge_distance(current, reference))
            values = np.asarray(distances, dtype=float)
            ci90 = bootstrap_mean_interval(
                values,
                bootstraps,
                rng_for(analysis_seed, f"frob_equiv90|{branch}"),
                confidence=0.90,
            )
            ci95 = bootstrap_mean_interval(
                values,
                bootstraps,
                rng_for(analysis_seed, f"frob_equiv95|{branch}"),
                confidence=0.95,
            )
            margin = 0.01
            rows.append(
                {
                    "left_branch": branch,
                    "right_branch": "continue",
                    "outcome": "normalized_late_mean_frobenius_distance",
                    "difference_definition": "nonnegative_distance",
                    "exploratory_margin": margin,
                    "n_valid": int(len(values)),
                    "mean_difference": float(np.mean(values)),
                    "ci90_low": ci90[0],
                    "ci90_high": ci90[1],
                    "ci95_low": ci95[0],
                    "ci95_high": ci95[1],
                    "equivalent_by_90pct_CI": bool(ci90[1] < margin),
                    "equivalent_by_95pct_CI_conservative": bool(
                        ci95[1] < margin
                    ),
                    "fraction_seed_differences_within_margin": float(
                        np.mean(values < margin)
                    ),
                    "note": "exploratory one-sided distance margin",
                }
            )
    return pd.DataFrame(rows)


def plot_envelopes(
    envelopes: pd.DataFrame,
    output_dir: str,
    window_time: float,
    recovery_end_time: float,
) -> list[str]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib unavailable; skipping plots")
        return []

    paths: list[str] = []
    for metric, ylabel in (
        ("similarity", "Weighted topology similarity"),
        ("density", "Threshold density"),
    ):
        fig, ax = plt.subplots(figsize=(12, 7))
        for branch in BRANCHES:
            block = envelopes.loc[
                (envelopes["branch"] == branch)
                & (envelopes["metric"] == metric)
            ]
            ax.plot(
                block["time_since_split"], block["mean"], label=branch, linewidth=2
            )
            ax.fill_between(
                block["time_since_split"],
                block["seed_q025"],
                block["seed_q975"],
                alpha=0.10,
            )
        ax.axvline(window_time, color="black", linestyle="--", alpha=0.5)
        ax.axvline(recovery_end_time, color="black", linestyle=":", alpha=0.6)
        ax.set_xlabel("Time since split")
        ax.set_ylabel(ylabel)
        ax.set_title(f"AIEF-1.4 {metric}: immediate, recovery, and late dynamics")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8, ncol=2)
        fig.tight_layout()
        path = os.path.join(output_dir, f"{metric}_recovery_envelope.png")
        fig.savefig(path, dpi=180)
        plt.close(fig)
        paths.append(path)
    return paths


def make_report(
    seed_metrics: pd.DataFrame,
    summary: pd.DataFrame,
    equivalence: pd.DataFrame,
) -> str:
    lines = [
        "AIEF-1.4 trajectory, sustained-recovery, and equivalence analysis",
        "=================================================================",
        "",
        "Similarity NaNs caused by an exactly zero edge-weight vector are mapped to zero only for recovery/loss calculations.",
        "Equivalence margins are exploratory and post-outcome; they are not preregistered confirmatory bounds.",
        "",
        "Key branch dynamics",
        "-------------------",
    ]

    selected_metrics = (
        "minimum_similarity",
        "sustained_similarity_90_rest",
        "sustained_density_90_rest",
        "Mean_similarity_deficit_vs_continue",
        "Mean_density_deficit_vs_continue",
        "sampled_similarity_mean_immediate",
        "sampled_similarity_mean_recovery",
        "sampled_similarity_mean_late",
    )
    for branch in BRANCHES:
        lines.append(branch)
        block = summary.loc[
            (summary["branch"] == branch)
            & (summary["metric"].isin(selected_metrics))
        ]
        for metric in selected_metrics:
            row_set = block.loc[block["metric"] == metric]
            if row_set.empty:
                continue
            row = row_set.iloc[0]
            lines.append(
                f"  {metric}: mean={row['mean']:.6g}, "
                f"median={row['median']:.6g}, "
                f"95% CI=[{row['ci95_low']:.6g}, {row['ci95_high']:.6g}], "
                f"valid={int(row['n_valid'])}/{int(row['n_total'])}"
            )

    lines.extend(["", "Exploratory equivalence", "-----------------------"])
    for _, row in equivalence.iterrows():
        lines.append(
            f"  {row['left_branch']} vs {row['right_branch']} / {row['outcome']}: "
            f"mean={row['mean_difference']:.6g}, margin={row['exploratory_margin']:.6g}, "
            f"90% CI=[{row['ci90_low']:.6g}, {row['ci90_high']:.6g}], "
            f"equivalent90={row['equivalent_by_90pct_CI']}, "
            f"within_margin={row['fraction_seed_differences_within_margin']:.3f}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* First crossing and sustained recovery are different estimands.",
            "* Late convergence does not imply that an intervention caused no transient loss.",
            "* Density recovery does not imply recovery of edge identity.",
            "* B_carrier_only/full_reset remains exploratory because r2 used unmatched phase resets.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scalar", default=DEFAULT_SCALAR)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--bootstrap", type=int, default=DEFAULT_BOOTSTRAPS)
    parser.add_argument("--analysis-seed", type=int, default=DEFAULT_ANALYSIS_SEED)
    parser.add_argument("--no-plots", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if not os.path.isfile(args.npz):
        raise FileNotFoundError(args.npz)
    if args.bootstrap < 0:
        raise ValueError("bootstrap repetitions must be nonnegative")
    os.makedirs(args.output_dir, exist_ok=True)

    scalar, manifest = load_inputs(args.scalar, args.manifest)
    window_time = float(manifest["protocol"]["window_steps"]) * float(
        manifest["model"]["dt"]
    )
    recovery_end_time = float(manifest["protocol"]["recovery_end"]) * float(
        manifest["model"]["dt"]
    )

    seed_metrics, envelopes = trajectory_analysis(scalar, args.npz, manifest)
    summary = summarize_metrics(seed_metrics, args.bootstrap, args.analysis_seed)
    equivalence = equivalence_analysis(
        scalar, args.npz, args.bootstrap, args.analysis_seed
    )

    seed_metrics.to_csv(
        os.path.join(args.output_dir, "trajectory_metrics_by_seed.csv"), index=False
    )
    summary.to_csv(
        os.path.join(args.output_dir, "trajectory_metrics_summary.csv"), index=False
    )
    equivalence.to_csv(
        os.path.join(args.output_dir, "equivalence_tests.csv"), index=False
    )
    envelopes.to_csv(
        os.path.join(args.output_dir, "trajectory_envelopes.csv"), index=False
    )

    plot_paths = [] if args.no_plots else plot_envelopes(
        envelopes, args.output_dir, window_time, recovery_end_time
    )
    report = make_report(seed_metrics, summary, equivalence)
    report_path = os.path.join(args.output_dir, "trajectory_recovery_report.txt")
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report)
    print(report)

    analysis_manifest = {
        "analysis": "AIEF-1.4 trajectory, sustained-recovery, and equivalence",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "source_manifest_path": str(Path(args.manifest).resolve()),
        "source_manifest_sha256": file_sha256(args.manifest),
        "bootstrap_repetitions": args.bootstrap,
        "analysis_seed": args.analysis_seed,
        "window_time": window_time,
        "recovery_end_time": recovery_end_time,
        "equivalence_specs": [list(spec) for spec in EQUIVALENCE_SPECS],
        "equivalence_note": "exploratory post-outcome margins",
        "zero_similarity_convention": "NaN cosine from zero vector mapped to 0 for recovery/loss calculations only",
        "trajectory_bands": "empirical 2.5% and 97.5% seed quantiles",
        "plots": [str(Path(path).resolve()) for path in plot_paths],
    }
    with open(
        os.path.join(args.output_dir, "analysis_manifest.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(analysis_manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(f"Saved analysis to {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
