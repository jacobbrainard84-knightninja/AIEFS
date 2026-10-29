#!/usr/bin/env python3
"""Close-out diagnostics for the two AIEF-1.3 validation cohorts.

This script answers two pre-AIEF-1.4 questions:
1. Are baseline P_future values exactly binary (0 or 1)?
2. How frequently and how strongly does the gap projection intervene?

It writes auditable CSV tables plus a concise text report.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_COHORTS = (
    (
        "validation_A",
        "runs/c3da1ac707bf/AIEF_1_3_c3da1ac707bf_scalar_summary.csv",
        "runs/c3da1ac707bf/AIEF_1_3_c3da1ac707bf_edge_diagnostics.npz",
    ),
    (
        "validation_B",
        "runs/73dca37cf93f/AIEF_1_3_73dca37cf93f_scalar_summary.csv",
        "runs/73dca37cf93f/AIEF_1_3_73dca37cf93f_edge_diagnostics.npz",
    ),
)

PROJECTION_COLUMNS = (
    "Pre_gap_violation_fraction",
    "Projection_active_fraction",
    "Projection_norm_mean_active",
    "Projection_norm_max",
    "G_min_pre_over_time",
    "G_min_over_time",
)

DEFAULT_OUTPUT_DIR = "aief_1_3_closure_diagnostics"
BINARY_ATOL = 1e-15


def parse_cohort(value: str) -> tuple[str, str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            "cohort must be LABEL=SCALAR_CSV,EDGE_NPZ"
        )
    label, paths = value.split("=", 1)
    parts = paths.split(",", 1)
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(
            "cohort must include scalar CSV and edge NPZ separated by a comma"
        )
    label = label.strip()
    scalar_path = parts[0].strip()
    edge_path = parts[1].strip()
    if not label or not scalar_path or not edge_path:
        raise argparse.ArgumentTypeError("cohort fields must be nonempty")
    return label, scalar_path, edge_path


def parse_npz_key(key: str) -> tuple[str, str, str]:
    condition, remainder = key.split("_seed_", 1)
    seed, metric = remainder.split("_", 1)
    return condition, seed, metric


def load_baseline_persistence(
    label: str,
    edge_path: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if not os.path.isfile(edge_path):
        raise FileNotFoundError(edge_path)

    seed_rows: list[dict[str, object]] = []
    value_rows: list[dict[str, object]] = []

    with np.load(edge_path, allow_pickle=False) as data:
        matching = []
        for key in data.files:
            if "_seed_" not in key:
                continue
            condition, seed, metric = parse_npz_key(key)
            if condition == "baseline" and metric == "P_future":
                matching.append((seed, key))

        if not matching:
            raise RuntimeError(f"{label}: no baseline P_future matrices found")

        for seed, key in sorted(matching, key=lambda item: int(item[0])):
            matrix = np.asarray(data[key], dtype=float)
            if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
                raise ValueError(f"{key}: expected a square matrix")
            if not np.all(np.isfinite(matrix)):
                raise ValueError(f"{key}: contains nonfinite values")

            edges = np.triu_indices(matrix.shape[0], k=1)
            values = matrix[edges]
            is_zero = np.isclose(values, 0.0, rtol=0.0, atol=BINARY_ATOL)
            is_one = np.isclose(values, 1.0, rtol=0.0, atol=BINARY_ATOL)
            intermediate = ~(is_zero | is_one)
            unique, counts = np.unique(values, return_counts=True)

            seed_rows.append(
                {
                    "cohort": label,
                    "seed": seed,
                    "n_edges": int(len(values)),
                    "n_zero": int(np.sum(is_zero)),
                    "n_one": int(np.sum(is_one)),
                    "n_intermediate": int(np.sum(intermediate)),
                    "binary_fraction": float(np.mean(is_zero | is_one)),
                    "P_min": float(np.min(values)),
                    "P_max": float(np.max(values)),
                    "P_mean": float(np.mean(values)),
                    "P_variance": float(np.var(values)),
                    "n_unique": int(len(unique)),
                    "exactly_binary": bool(np.all(is_zero | is_one)),
                }
            )

            for value, count in zip(unique, counts):
                value_rows.append(
                    {
                        "cohort": label,
                        "seed": seed,
                        "P_value": float(value),
                        "P_value_repr": format(float(value), ".17g"),
                        "count": int(count),
                    }
                )

    return seed_rows, value_rows


def load_projection_data(label: str, scalar_path: str) -> pd.DataFrame:
    if not os.path.isfile(scalar_path):
        raise FileNotFoundError(scalar_path)
    frame = pd.read_csv(scalar_path, dtype={"seed": str})
    required = {"condition", "seed", *PROJECTION_COLUMNS}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{label}: scalar CSV missing {sorted(missing)}")
    frame["cohort"] = label
    return frame


def projection_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (cohort, condition), group in frame.groupby(["cohort", "condition"]):
        for metric in PROJECTION_COLUMNS:
            values = pd.to_numeric(group[metric], errors="coerce").to_numpy(float)
            values = values[np.isfinite(values)]
            rows.append(
                {
                    "cohort": cohort,
                    "condition": condition,
                    "metric": metric,
                    "n_valid": int(len(values)),
                    "mean": float(np.mean(values)) if len(values) else np.nan,
                    "std": float(np.std(values)) if len(values) else np.nan,
                    "median": float(np.median(values)) if len(values) else np.nan,
                    "minimum": float(np.min(values)) if len(values) else np.nan,
                    "maximum": float(np.max(values)) if len(values) else np.nan,
                }
            )

    # Add pooled descriptive summaries while preserving cohort-specific rows.
    for condition, group in frame.groupby("condition"):
        for metric in PROJECTION_COLUMNS:
            values = pd.to_numeric(group[metric], errors="coerce").to_numpy(float)
            values = values[np.isfinite(values)]
            rows.append(
                {
                    "cohort": "pooled",
                    "condition": condition,
                    "metric": metric,
                    "n_valid": int(len(values)),
                    "mean": float(np.mean(values)) if len(values) else np.nan,
                    "std": float(np.std(values)) if len(values) else np.nan,
                    "median": float(np.median(values)) if len(values) else np.nan,
                    "minimum": float(np.min(values)) if len(values) else np.nan,
                    "maximum": float(np.max(values)) if len(values) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def make_report(
    persistence_by_seed: pd.DataFrame,
    projection: pd.DataFrame,
) -> str:
    lines = [
        "AIEF-1.3 close-out diagnostics",
        "================================",
        "",
        "Baseline future persistence",
        "---------------------------",
    ]

    for cohort, group in persistence_by_seed.groupby("cohort"):
        lines.append(
            f"{cohort}: seeds={len(group)}, edges={int(group['n_edges'].sum())}, "
            f"intermediate={int(group['n_intermediate'].sum())}, "
            f"all_seeds_binary={bool(group['exactly_binary'].all())}, "
            f"mean(P_mean)={group['P_mean'].mean():.9f}"
        )

    lines.extend(["", "Projection diagnostics (pooled)", "-------------------------------"])
    selected = projection.loc[
        (projection["cohort"] == "pooled")
        & (
            projection["metric"].isin(
                [
                    "Pre_gap_violation_fraction",
                    "Projection_active_fraction",
                    "Projection_norm_mean_active",
                    "Projection_norm_max",
                ]
            )
        )
    ]
    for condition in ("baseline", "no_delay", "no_mu", "shuffle_R", "no_gap"):
        lines.append(condition)
        block = selected.loc[selected["condition"] == condition]
        for _, row in block.iterrows():
            lines.append(
                f"  {row['metric']}: mean={row['mean']:.9g}, "
                f"std={row['std']:.9g}, max={row['maximum']:.9g}, "
                f"n={int(row['n_valid'])}"
            )

    lines.extend(
        [
            "",
            "Interpretation",
            "--------------",
            "* n_intermediate == 0 confirms that P_future is exactly binary at the saved numerical precision.",
            "* Projection_active_fraction measures frequency; Projection_norm_* measures intervention magnitude.",
            "* A frequent projection with a small norm is a continuously active but gentle constraint.",
            "* Do not interpret summed projection norms as physical work without a separately defined quantity.",
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
        metavar="LABEL=SCALAR_CSV,EDGE_NPZ",
        help="repeat for multiple cohorts",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    specs = args.cohort if args.cohort is not None else list(DEFAULT_COHORTS)
    labels = [spec[0] for spec in specs]
    if len(set(labels)) != len(labels):
        raise ValueError("cohort labels must be unique")

    os.makedirs(args.output_dir, exist_ok=True)

    persistence_rows: list[dict[str, object]] = []
    unique_rows: list[dict[str, object]] = []
    projection_frames: list[pd.DataFrame] = []

    for label, scalar_path, edge_path in specs:
        print(f"Loading {label}")
        seed_rows, value_rows = load_baseline_persistence(label, edge_path)
        persistence_rows.extend(seed_rows)
        unique_rows.extend(value_rows)
        projection_frames.append(load_projection_data(label, scalar_path))

    persistence = pd.DataFrame(persistence_rows)
    unique_values = pd.DataFrame(unique_rows)
    projection_raw = pd.concat(projection_frames, ignore_index=True)
    projection = projection_summary(projection_raw)

    # Aggregate exact-value counts across seeds without rounding the stored value.
    unique_aggregate = (
        unique_values.groupby(["cohort", "P_value_repr"], as_index=False)["count"]
        .sum()
        .sort_values(["cohort", "P_value_repr"])
    )

    persistence_path = os.path.join(
        args.output_dir,
        "baseline_persistence_by_seed.csv",
    )
    unique_path = os.path.join(
        args.output_dir,
        "baseline_persistence_unique_values.csv",
    )
    projection_path = os.path.join(
        args.output_dir,
        "projection_diagnostics_summary.csv",
    )
    report_path = os.path.join(args.output_dir, "closure_report.txt")

    persistence.to_csv(persistence_path, index=False)
    unique_aggregate.to_csv(unique_path, index=False)
    projection.to_csv(projection_path, index=False)

    report = make_report(persistence, projection)
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report)
    print("\n" + report)
    print(f"Saved diagnostics to {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
