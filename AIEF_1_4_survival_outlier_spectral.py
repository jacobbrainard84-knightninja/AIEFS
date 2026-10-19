#!/usr/bin/env python3
"""AIEF-1.4 recovery survival, basin-feature, spectral, and residual analysis.

This is the next analysis stage after trajectory/recovery extraction. It uses
only existing r2 artifacts; it does not run new simulations.

Analyses
--------
1. Kaplan-Meier curves for sustained 90% similarity and density recovery.
2. Recovery probability, median recovery, and restricted mean unrecovered time.
3. Paired branch contrasts using per-seed restricted recovery times.
4. Split-state basin-margin features and descriptive recovery associations.
5. Symmetric adjacency/Laplacian spectra at split, late mean, and final state.
6. Localization of the tiny reset_B versus continue residual.

Censoring convention
--------------------
A seed without a sustained-recovery time is right-censored at the end of the
future window. Recovery-time means among recovered seeds are also reported, but
restricted mean unrecovered time and event probability are the primary summary.
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
DEFAULT_TRAJECTORY_METRICS = (
    "aief_1_4_trajectory_recovery/trajectory_metrics_by_seed.csv"
)
DEFAULT_OUTPUT_DIR = "aief_1_4_survival_outlier_spectral"
DEFAULT_BOOTSTRAPS = 20_000
DEFAULT_ANALYSIS_SEED = 20260717
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

RECOVERY_ENDPOINTS = {
    "similarity90": "sustained_similarity_90_rest",
    "density90": "sustained_density_90_rest",
}

RECOVERY_CONTRASTS = (
    ("continue", "reset_B", "primary"),
    ("continue", "reset_ema", "primary"),
    ("reset_B", "reset_B_ema", "primary"),
    ("continue", "future_shuffle", "primary_driver_control"),
    (
        "B_carrier_only",
        "full_reset",
        "exploratory_unmatched_phase_reset",
    ),
)

ASSOCIATION_BRANCHES = (
    "reset_ema",
    "reset_B_ema",
    "B_carrier_only",
    "full_reset",
)

SPLIT_FEATURES = (
    "split_r",
    "split_D_B",
    "split_total_edge_weight",
    "split_effective_edges",
    "split_weight_gini",
    "split_weight_entropy",
    "split_min_distance_to_Bc",
    "split_selected_margin_min",
    "split_unselected_margin_min",
    "split_min_row_slack",
    "split_R_selected_mean",
    "split_R_unselected_mean",
    "split_R_contrast",
    "split_EMA_selected_mean",
    "split_EMA_unselected_mean",
    "split_EMA_contrast",
    "split_adjacency_lambda1",
    "split_adjacency_gap12",
    "split_principal_eigenvector_ipr",
    "split_laplacian_lambda2",
    "split_laplacian_lambda_max",
    "split_laplacian_entropy",
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


def npz_key(branch: str, seed: str, metric: str) -> str:
    return f"{branch}_seed_{seed}_{metric}"


def prefix_key(seed: str, metric: str) -> str:
    return f"prefix_seed_{seed}_{metric}"


def load_inputs(
    scalar_path: str,
    trajectory_path: str,
    manifest_path: str,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    for path in (scalar_path, trajectory_path, manifest_path):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)

    scalar = pd.read_csv(scalar_path, dtype={"seed": str})
    trajectory = pd.read_csv(trajectory_path, dtype={"seed": str})
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    for frame, name in ((scalar, "scalar"), (trajectory, "trajectory")):
        required = {"seed", "branch"}
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"{name} input missing {sorted(missing)}")
        frame["seed"] = frame["seed"].astype(str)
        frame["branch"] = frame["branch"].astype(str)
        if frame.duplicated(["seed", "branch"]).any():
            raise ValueError(f"duplicate seed/branch rows in {name} input")
        branch_set = set(frame["branch"])
        if branch_set != set(BRANCHES):
            raise ValueError(f"branch mismatch in {name} input")

    scalar_seeds = set(scalar.loc[scalar["branch"] == "continue", "seed"])
    trajectory_seeds = set(
        trajectory.loc[trajectory["branch"] == "continue", "seed"]
    )
    if scalar_seeds != trajectory_seeds:
        raise ValueError("scalar and trajectory seed sets differ")
    for branch in BRANCHES:
        if set(scalar.loc[scalar["branch"] == branch, "seed"]) != scalar_seeds:
            raise ValueError(f"scalar seed mismatch for {branch}")
        if set(trajectory.loc[trajectory["branch"] == branch, "seed"]) != scalar_seeds:
            raise ValueError(f"trajectory seed mismatch for {branch}")
    return scalar, trajectory, manifest


def bootstrap_interval(
    values: np.ndarray,
    repetitions: int,
    rng: np.random.Generator,
    confidence: float = 0.95,
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


def km_curve(
    durations: np.ndarray,
    events: np.ndarray,
    tau: float,
) -> tuple[pd.DataFrame, float, float, float]:
    """Return KM unrecovered curve, median recovery, event probability, RMUT."""
    durations = np.asarray(durations, dtype=float)
    events = np.asarray(events, dtype=bool)
    if len(durations) != len(events) or not len(durations):
        raise ValueError("invalid survival arrays")

    durations = np.minimum(durations, tau)
    event_times = np.unique(durations[events])
    survival = 1.0
    previous_time = 0.0
    area = 0.0
    rows = [
        {
            "time": 0.0,
            "unrecovered_probability": 1.0,
            "n_at_risk": int(len(durations)),
            "n_events": 0,
            "n_censored": 0,
        }
    ]
    median_recovery = np.nan

    all_times = np.unique(durations)
    for time_value in all_times:
        area += survival * (float(time_value) - previous_time)
        at_risk = int(np.sum(durations >= time_value))
        event_count = int(np.sum((durations == time_value) & events))
        censored_count = int(np.sum((durations == time_value) & ~events))
        if event_count and at_risk:
            survival *= 1.0 - event_count / at_risk
            if not np.isfinite(median_recovery) and survival <= 0.5:
                median_recovery = float(time_value)
        rows.append(
            {
                "time": float(time_value),
                "unrecovered_probability": float(survival),
                "n_at_risk": at_risk,
                "n_events": event_count,
                "n_censored": censored_count,
            }
        )
        previous_time = float(time_value)

    if previous_time < tau:
        area += survival * (tau - previous_time)
        rows.append(
            {
                "time": float(tau),
                "unrecovered_probability": float(survival),
                "n_at_risk": int(np.sum(durations >= tau)),
                "n_events": 0,
                "n_censored": int(np.sum((durations == tau) & ~events)),
            }
        )

    recovery_probability = float(np.mean(events))
    return pd.DataFrame(rows), median_recovery, recovery_probability, float(area)


def survival_analysis(
    trajectory: pd.DataFrame,
    future_time: float,
    bootstraps: int,
    analysis_seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    curve_rows: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []

    for endpoint, column in RECOVERY_ENDPOINTS.items():
        if column not in trajectory.columns:
            raise ValueError(f"trajectory metrics missing {column}")
        for branch in BRANCHES:
            group = trajectory.loc[trajectory["branch"] == branch].copy()
            observed = pd.to_numeric(group[column], errors="coerce").to_numpy(float)
            events = np.isfinite(observed)
            durations = np.where(events, observed, future_time)
            curve, median, probability, rmut = km_curve(
                durations, events, future_time
            )
            curve.insert(0, "endpoint", endpoint)
            curve.insert(0, "branch_family", BRANCH_FAMILIES[branch])
            curve.insert(0, "branch", branch)
            curve_rows.append(curve)

            probability_samples = events.astype(float)
            restricted_times = np.minimum(durations, future_time)
            prob_ci = bootstrap_interval(
                probability_samples,
                bootstraps,
                rng_for(analysis_seed, f"prob|{branch}|{endpoint}"),
            )
            rmut_ci = bootstrap_interval(
                restricted_times,
                bootstraps,
                rng_for(analysis_seed, f"rmut|{branch}|{endpoint}"),
            )
            recovered_times = durations[events]
            conditional_ci = bootstrap_interval(
                recovered_times,
                bootstraps,
                rng_for(analysis_seed, f"conditional|{branch}|{endpoint}"),
            )
            summary_rows.append(
                {
                    "branch": branch,
                    "branch_family": BRANCH_FAMILIES[branch],
                    "endpoint": endpoint,
                    "n_total": int(len(group)),
                    "n_recovered": int(np.sum(events)),
                    "n_censored": int(np.sum(~events)),
                    "recovery_probability": probability,
                    "recovery_probability_ci95_low": prob_ci[0],
                    "recovery_probability_ci95_high": prob_ci[1],
                    "median_recovery_time_KM": median,
                    "restricted_mean_unrecovered_time": rmut,
                    "rmut_ci95_low": rmut_ci[0],
                    "rmut_ci95_high": rmut_ci[1],
                    "conditional_mean_recovery_time": float(
                        np.mean(recovered_times)
                    )
                    if len(recovered_times)
                    else np.nan,
                    "conditional_recovery_ci95_low": conditional_ci[0],
                    "conditional_recovery_ci95_high": conditional_ci[1],
                    "censor_time": future_time,
                }
            )

            for seed, duration, event in zip(
                group["seed"].astype(str), durations, events
            ):
                seed_rows.append(
                    {
                        "seed": seed,
                        "branch": branch,
                        "branch_family": BRANCH_FAMILIES[branch],
                        "endpoint": endpoint,
                        "duration": float(duration),
                        "event_recovered": bool(event),
                        "right_censored": bool(not event),
                    }
                )

    curves = pd.concat(curve_rows, ignore_index=True)
    return curves, pd.DataFrame(summary_rows), pd.DataFrame(seed_rows)


def paired_recovery_contrasts(
    seed_survival: pd.DataFrame,
    bootstraps: int,
    analysis_seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for endpoint in RECOVERY_ENDPOINTS:
        endpoint_frame = seed_survival.loc[
            seed_survival["endpoint"] == endpoint
        ]
        indexed = {
            branch: endpoint_frame.loc[
                endpoint_frame["branch"] == branch
            ].set_index("seed")
            for branch in BRANCHES
        }
        for left, right, role in RECOVERY_CONTRASTS:
            shared = sorted(set(indexed[left].index) & set(indexed[right].index), key=int)
            left_time = indexed[left].loc[shared, "duration"].to_numpy(float)
            right_time = indexed[right].loc[shared, "duration"].to_numpy(float)
            left_event = indexed[left].loc[shared, "event_recovered"].to_numpy(bool)
            right_event = indexed[right].loc[shared, "event_recovered"].to_numpy(bool)

            # Lower restricted time is faster/better. Difference is left-right.
            time_difference = left_time - right_time
            event_difference = left_event.astype(float) - right_event.astype(float)
            time_ci = bootstrap_interval(
                time_difference,
                bootstraps,
                rng_for(analysis_seed, f"time|{endpoint}|{left}|{right}"),
            )
            event_ci = bootstrap_interval(
                event_difference,
                bootstraps,
                rng_for(analysis_seed, f"event|{endpoint}|{left}|{right}"),
            )
            rows.append(
                {
                    "endpoint": endpoint,
                    "left_branch": left,
                    "right_branch": right,
                    "contrast_role": role,
                    "difference_definition": "left_minus_right",
                    "n_pairs": int(len(shared)),
                    "restricted_time_difference_mean": float(
                        np.mean(time_difference)
                    ),
                    "restricted_time_difference_ci95_low": time_ci[0],
                    "restricted_time_difference_ci95_high": time_ci[1],
                    "recovery_probability_difference": float(
                        np.mean(event_difference)
                    ),
                    "recovery_probability_difference_ci95_low": event_ci[0],
                    "recovery_probability_difference_ci95_high": event_ci[1],
                    "fraction_left_faster": float(np.mean(time_difference < 0.0)),
                    "fraction_equal_restricted_time": float(
                        np.mean(time_difference == 0.0)
                    ),
                }
            )
    return pd.DataFrame(rows)


def effective_number(weights: np.ndarray) -> float:
    weights = np.asarray(weights, dtype=float)
    total = float(np.sum(weights))
    denominator = float(np.sum(weights**2))
    if total <= ZERO_TOL or denominator <= ZERO_TOL:
        return 0.0
    return total**2 / denominator


def gini(weights: np.ndarray) -> float:
    x = np.sort(np.asarray(weights, dtype=float))
    total = float(np.sum(x))
    if total <= ZERO_TOL:
        return 0.0
    n = len(x)
    ranks = np.arange(1, n + 1, dtype=float)
    return float(2.0 * np.dot(ranks, x) / (n * total) - (n + 1.0) / n)


def entropy(weights: np.ndarray) -> float:
    weights = np.asarray(weights, dtype=float)
    total = float(np.sum(weights))
    if total <= ZERO_TOL:
        return 0.0
    p = weights / total
    positive = p > 0.0
    return float(-np.sum(p[positive] * np.log(p[positive])) / np.log(len(p)))


def spectral_metrics(B: np.ndarray) -> dict[str, float]:
    B = np.asarray(B, dtype=float)
    B = 0.5 * (B + B.T)
    eigenvalues, eigenvectors = np.linalg.eigh(B)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    principal = eigenvectors[:, order[0]]
    principal_power = principal**2
    principal_ipr = float(np.sum(principal_power**2))

    row_sum = np.sum(B, axis=1)
    L = np.diag(row_sum) - B
    laplacian = np.clip(np.linalg.eigvalsh(L), 0.0, None)
    laplacian.sort()
    total = float(np.sum(laplacian))
    if total <= ZERO_TOL:
        lap_entropy = 0.0
    else:
        p = laplacian / total
        positive = p > 0.0
        lap_entropy = float(-np.sum(p[positive] * np.log(p[positive])))

    return {
        "adjacency_lambda1": float(eigenvalues[0]),
        "adjacency_lambda2": float(eigenvalues[1]),
        "adjacency_gap12": float(eigenvalues[0] - eigenvalues[1]),
        "principal_eigenvector_ipr": principal_ipr,
        "laplacian_lambda2": float(laplacian[1]),
        "laplacian_lambda_max": float(laplacian[-1]),
        "laplacian_entropy": lap_entropy,
    }


def split_features(
    scalar: pd.DataFrame,
    npz_path: str,
    manifest: dict[str, Any],
) -> pd.DataFrame:
    omega = np.asarray(manifest["model"]["omega"], dtype=float)
    B_c = float(manifest["model"]["B_c"])
    cap = (float(manifest["model"]["a"]) - float(manifest["model"]["delta"])) / float(
        manifest["model"]["q"]
    )
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    rows: list[dict[str, Any]] = []

    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            B = np.asarray(data[prefix_key(seed, "B_at_split")], dtype=float)
            R = np.asarray(data[prefix_key(seed, "R_physical_past")], dtype=float)
            theta = np.asarray(data[prefix_key(seed, "theta_at_split")], dtype=float)
            C = np.asarray(
                data[prefix_key(seed, "coherence_acc_at_split")]
            )
            edges = np.triu_indices(B.shape[0], k=1)
            weights = B[edges]
            selected = weights > B_c
            r_edges = R[edges]
            ema_matrix = 0.5 * (np.abs(C) + np.abs(C).T)
            ema_edges = ema_matrix[edges]
            row_slack = cap - np.sum(B, axis=1)
            selected_margin = weights[selected] - B_c
            unselected_margin = B_c - weights[~selected]
            spec = spectral_metrics(B)

            r_split = float(abs(np.mean(np.exp(1j * theta))))
            selected_r_mean = (
                float(np.mean(r_edges[selected])) if np.any(selected) else np.nan
            )
            unselected_r_mean = (
                float(np.mean(r_edges[~selected])) if np.any(~selected) else np.nan
            )
            selected_ema_mean = (
                float(np.mean(ema_edges[selected])) if np.any(selected) else np.nan
            )
            unselected_ema_mean = (
                float(np.mean(ema_edges[~selected])) if np.any(~selected) else np.nan
            )
            row = {
                "seed": seed,
                "split_r": r_split,
                "split_D_B": float(np.mean(selected)),
                "split_total_edge_weight": float(np.sum(weights)),
                "split_effective_edges": effective_number(weights),
                "split_weight_gini": gini(weights),
                "split_weight_entropy": entropy(weights),
                "split_min_distance_to_Bc": float(np.min(np.abs(weights - B_c))),
                "split_selected_margin_min": float(np.min(selected_margin))
                if len(selected_margin)
                else np.nan,
                "split_unselected_margin_min": float(np.min(unselected_margin))
                if len(unselected_margin)
                else np.nan,
                "split_min_row_slack": float(np.min(row_slack)),
                "split_R_selected_mean": selected_r_mean,
                "split_R_unselected_mean": unselected_r_mean,
                "split_R_contrast": selected_r_mean - unselected_r_mean,
                "split_EMA_selected_mean": selected_ema_mean,
                "split_EMA_unselected_mean": unselected_ema_mean,
                "split_EMA_contrast": selected_ema_mean - unselected_ema_mean,
                **{f"split_{key}": value for key, value in spec.items()},
            }
            rows.append(row)
    return pd.DataFrame(rows)


def spectral_stage_table(
    scalar: pd.DataFrame,
    npz_path: str,
) -> pd.DataFrame:
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    rows: list[dict[str, Any]] = []
    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            split = np.asarray(data[prefix_key(seed, "B_at_split")], dtype=float)
            rows.append(
                {
                    "seed": seed,
                    "branch": "prefix",
                    "stage": "split",
                    **spectral_metrics(split),
                }
            )
            for branch in BRANCHES:
                for matrix_key, stage in (
                    ("B_mean_late", "late_mean"),
                    ("B_final", "final"),
                ):
                    matrix = np.asarray(
                        data[npz_key(branch, seed, matrix_key)], dtype=float
                    )
                    rows.append(
                        {
                            "seed": seed,
                            "branch": branch,
                            "stage": stage,
                            **spectral_metrics(matrix),
                        }
                    )
    return pd.DataFrame(rows)


def rank_correlation(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    if np.sum(valid) < 3:
        return np.nan
    x_rank = pd.Series(x[valid]).rank(method="average").to_numpy(float)
    y_rank = pd.Series(y[valid]).rank(method="average").to_numpy(float)
    if np.std(x_rank) <= ZERO_TOL or np.std(y_rank) <= ZERO_TOL:
        return np.nan
    return float(np.corrcoef(x_rank, y_rank)[0, 1])


def feature_recovery_associations(
    features: pd.DataFrame,
    trajectory: pd.DataFrame,
    future_time: float,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for branch in ASSOCIATION_BRANCHES:
        branch_outcomes = trajectory.loc[
            trajectory["branch"] == branch
        ][
            [
                "seed",
                "sustained_similarity_90_rest",
                "Mean_similarity_deficit_vs_continue",
                "sampled_similarity_mean_late",
            ]
        ]
        merged = features.merge(branch_outcomes, on="seed", how="inner")
        recovered = np.isfinite(
            pd.to_numeric(
                merged["sustained_similarity_90_rest"], errors="coerce"
            ).to_numpy(float)
        )
        restricted_time = np.where(
            recovered,
            pd.to_numeric(
                merged["sustained_similarity_90_rest"], errors="coerce"
            ).to_numpy(float),
            future_time,
        )
        deficit = pd.to_numeric(
            merged["Mean_similarity_deficit_vs_continue"], errors="coerce"
        ).to_numpy(float)
        late_similarity = pd.to_numeric(
            merged["sampled_similarity_mean_late"], errors="coerce"
        ).to_numpy(float)

        for feature in SPLIT_FEATURES:
            x = pd.to_numeric(merged[feature], errors="coerce").to_numpy(float)
            recovered_values = x[recovered & np.isfinite(x)]
            censored_values = x[(~recovered) & np.isfinite(x)]
            rows.append(
                {
                    "branch": branch,
                    "feature": feature,
                    "n_total": int(len(merged)),
                    "n_recovered": int(np.sum(recovered)),
                    "n_censored": int(np.sum(~recovered)),
                    "recovered_feature_mean": float(np.mean(recovered_values))
                    if len(recovered_values)
                    else np.nan,
                    "censored_feature_mean": float(np.mean(censored_values))
                    if len(censored_values)
                    else np.nan,
                    "recovered_minus_censored": (
                        float(np.mean(recovered_values) - np.mean(censored_values))
                        if len(recovered_values) and len(censored_values)
                        else np.nan
                    ),
                    "spearman_with_restricted_recovery_time": rank_correlation(
                        x, restricted_time
                    ),
                    "spearman_with_mean_similarity_deficit": rank_correlation(
                        x, deficit
                    ),
                    "spearman_with_late_similarity": rank_correlation(
                        x, late_similarity
                    ),
                    "note": "descriptive; n=40 is too small for high-dimensional causal modeling",
                }
            )
    return pd.DataFrame(rows)


def residual_localization(
    scalar: pd.DataFrame,
    npz_path: str,
    manifest: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    omega = np.asarray(manifest["model"]["omega"], dtype=float)
    edges = np.triu_indices(len(omega), k=1)
    frequency_gap = np.abs(omega[:, None] - omega[None, :])[edges]
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    rows: list[dict[str, Any]] = []
    residual_vectors = []

    with np.load(npz_path, allow_pickle=False) as data:
        for seed in seeds:
            reference = np.asarray(
                data[npz_key("continue", seed, "B_mean_late")], dtype=float
            )
            reconstructed = np.asarray(
                data[npz_key("reset_B", seed, "B_mean_late")], dtype=float
            )
            residual_matrix = reconstructed - reference
            residual = residual_matrix[edges]
            residual_vectors.append(residual)
            norm = float(np.linalg.norm(residual))
            absolute = np.abs(residual)
            power = residual**2
            power2 = float(np.sum(power**2))
            # Participation ratio is scale invariant. Do not compare power2 to
            # ZERO_TOL: genuine residuals can be far below that absolute scale.
            participation = (
                float(np.sum(power) ** 2 / power2) if power2 > 0.0 else 0.0
            )
            max_index = int(np.argmax(absolute))
            node_burden = np.sum(np.abs(residual_matrix), axis=1)
            rows.append(
                {
                    "seed": seed,
                    "residual_norm": norm,
                    "normalized_residual_norm": norm
                    / max(float(np.linalg.norm(reference[edges])), ZERO_TOL),
                    "max_absolute_edge_residual": float(absolute[max_index]),
                    "largest_edge_fraction_of_norm": float(absolute[max_index])
                    / max(norm, ZERO_TOL),
                    "residual_participation_ratio": participation,
                    "max_node_burden_fraction": float(np.max(node_burden))
                    / max(float(np.sum(node_burden)), ZERO_TOL),
                    "dominant_edge_i": int(edges[0][max_index]),
                    "dominant_edge_j": int(edges[1][max_index]),
                    "dominant_edge_frequency_gap": float(frequency_gap[max_index]),
                    "spearman_abs_residual_vs_frequency_gap": rank_correlation(
                        absolute, frequency_gap
                    ),
                }
            )

    residual_matrix = np.stack(residual_vectors)
    centered = residual_matrix - np.mean(residual_matrix, axis=0, keepdims=True)
    _, singular_values, right_vectors = np.linalg.svd(centered, full_matrices=False)
    variance = singular_values**2
    explained = variance / np.sum(variance) if np.sum(variance) > 0 else variance
    svd_rows = [
        {
            "component": int(index + 1),
            "singular_value": float(value),
            "explained_residual_variance": float(explained[index]),
            "cumulative_explained_variance": float(np.sum(explained[: index + 1])),
        }
        for index, value in enumerate(singular_values)
    ]

    first_mode = right_vectors[0]
    mode_order = np.argsort(np.abs(first_mode))[::-1]
    mode_rows = [
        {
            "rank": int(rank + 1),
            "edge_i": int(edges[0][index]),
            "edge_j": int(edges[1][index]),
            "omega_i": float(omega[edges[0][index]]),
            "omega_j": float(omega[edges[1][index]]),
            "frequency_gap": float(frequency_gap[index]),
            "first_mode_loading": float(first_mode[index]),
            "absolute_loading": float(abs(first_mode[index])),
        }
        for rank, index in enumerate(mode_order)
    ]
    return pd.DataFrame(rows), pd.DataFrame(svd_rows), pd.DataFrame(mode_rows)


def plot_km(curves: pd.DataFrame, output_dir: str) -> list[str]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib unavailable; skipping survival plots")
        return []

    paths = []
    for endpoint in RECOVERY_ENDPOINTS:
        fig, ax = plt.subplots(figsize=(11, 7))
        for branch in BRANCHES:
            block = curves.loc[
                (curves["endpoint"] == endpoint)
                & (curves["branch"] == branch)
            ]
            ax.step(
                block["time"],
                block["unrecovered_probability"],
                where="post",
                label=branch,
                linewidth=2,
            )
        ax.set_xlabel("Time since split")
        ax.set_ylabel("Probability not yet sustainably recovered")
        ax.set_ylim(-0.02, 1.02)
        ax.set_title(f"AIEF-1.4 sustained {endpoint} recovery")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8, ncol=2)
        fig.tight_layout()
        path = os.path.join(output_dir, f"KM_{endpoint}_recovery.png")
        fig.savefig(path, dpi=180)
        plt.close(fig)
        paths.append(path)
    return paths


def make_report(
    survival: pd.DataFrame,
    contrasts: pd.DataFrame,
    residual: pd.DataFrame,
) -> str:
    lines = [
        "AIEF-1.4 survival, basin-feature, spectral, and residual analysis",
        "================================================================",
        "",
        "Recovery-time means are conditional on recovery; recovery probability and restricted mean unrecovered time account for censoring.",
        "B_carrier_only/full_reset remains exploratory because r2 used unmatched phase resets.",
        "",
        "Sustained recovery",
        "------------------",
    ]
    for branch in BRANCHES:
        lines.append(branch)
        for endpoint in RECOVERY_ENDPOINTS:
            row = survival.loc[
                (survival["branch"] == branch)
                & (survival["endpoint"] == endpoint)
            ].iloc[0]
            lines.append(
                f"  {endpoint}: recovered={int(row['n_recovered'])}/{int(row['n_total'])}, "
                f"prob={row['recovery_probability']:.3f}, "
                f"KM_median={row['median_recovery_time_KM']:.6g}, "
                f"RMUT={row['restricted_mean_unrecovered_time']:.6g}, "
                f"conditional_mean={row['conditional_mean_recovery_time']:.6g}"
            )

    lines.extend(["", "Primary recovery contrasts", "--------------------------"])
    for _, row in contrasts.loc[
        contrasts["contrast_role"].isin(["primary", "primary_driver_control"])
    ].iterrows():
        lines.append(
            f"  {row['left_branch']} - {row['right_branch']} / {row['endpoint']}: "
            f"restricted_time_delta={row['restricted_time_difference_mean']:.6g}, "
            f"95% CI=[{row['restricted_time_difference_ci95_low']:.6g}, "
            f"{row['restricted_time_difference_ci95_high']:.6g}], "
            f"recovery_probability_delta={row['recovery_probability_difference']:.3f}"
        )

    lines.extend(["", "reset_B residual localization", "-----------------------------"])
    lines.append(
        f"  normalized residual mean={residual['normalized_residual_norm'].mean():.6g}"
    )
    lines.append(
        f"  participation ratio median={residual['residual_participation_ratio'].median():.6g}"
    )
    lines.append(
        f"  largest-edge fraction median={residual['largest_edge_fraction_of_norm'].median():.6g}"
    )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Censored recovery times must not be treated as ordinary missing values.",
            "* Feature associations are descriptive and high-dimensional relative to n=40.",
            "* B is symmetric; adjacency spectra are real, not non-Hermitian.",
            "* Largest adjacency eigenvalue is bounded by the row-sum constraint and may mainly report cap saturation.",
            "* Split/late/final spectra do not constitute a continuous spectral-recovery trajectory.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scalar", default=DEFAULT_SCALAR)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--trajectory-metrics", default=DEFAULT_TRAJECTORY_METRICS)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--bootstrap", type=int, default=DEFAULT_BOOTSTRAPS)
    parser.add_argument("--analysis-seed", type=int, default=DEFAULT_ANALYSIS_SEED)
    parser.add_argument("--no-plots", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.scalar, args.npz, args.manifest, args.trajectory_metrics):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if args.bootstrap < 0:
        raise ValueError("bootstrap repetitions must be nonnegative")
    os.makedirs(args.output_dir, exist_ok=True)

    scalar, trajectory, manifest = load_inputs(
        args.scalar, args.trajectory_metrics, args.manifest
    )
    future_time = float(manifest["protocol"]["future_steps"]) * float(
        manifest["model"]["dt"]
    )

    km_curves, survival_summary, survival_by_seed = survival_analysis(
        trajectory, future_time, args.bootstrap, args.analysis_seed
    )
    recovery_contrasts = paired_recovery_contrasts(
        survival_by_seed, args.bootstrap, args.analysis_seed
    )
    features = split_features(scalar, args.npz, manifest)
    spectra = spectral_stage_table(scalar, args.npz)
    associations = feature_recovery_associations(features, trajectory, future_time)
    residual, residual_svd, residual_mode = residual_localization(
        scalar, args.npz, manifest
    )

    outputs = {
        "KM_curves.csv": km_curves,
        "recovery_summary.csv": survival_summary,
        "recovery_by_seed.csv": survival_by_seed,
        "paired_recovery_contrasts.csv": recovery_contrasts,
        "split_state_features.csv": features,
        "spectral_metrics_split_late_final.csv": spectra,
        "feature_recovery_associations.csv": associations,
        "resetB_residual_localization_by_seed.csv": residual,
        "resetB_residual_svd.csv": residual_svd,
        "resetB_residual_first_mode_edges.csv": residual_mode,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)

    plot_paths = [] if args.no_plots else plot_km(km_curves, args.output_dir)
    report = make_report(survival_summary, recovery_contrasts, residual)
    report_path = os.path.join(args.output_dir, "survival_outlier_spectral_report.txt")
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report)
    print(report)

    analysis_manifest = {
        "analysis": "AIEF-1.4 survival, basin features, spectra, and residuals",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "source_manifest_path": str(Path(args.manifest).resolve()),
        "source_manifest_sha256": file_sha256(args.manifest),
        "trajectory_metrics_path": str(Path(args.trajectory_metrics).resolve()),
        "trajectory_metrics_sha256": file_sha256(args.trajectory_metrics),
        "future_censor_time": future_time,
        "bootstrap_repetitions": args.bootstrap,
        "analysis_seed": args.analysis_seed,
        "recovery_endpoints": RECOVERY_ENDPOINTS,
        "plots": [str(Path(path).resolve()) for path in plot_paths],
        "warnings": [
            "B_carrier_only/full_reset is exploratory because r2 phase resets were unmatched.",
            "Feature associations are descriptive with n=40.",
            "Spectra are available only at split, late mean, and final state.",
        ],
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
