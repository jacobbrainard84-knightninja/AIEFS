#!/usr/bin/env python3
"""AIEF-1.4 T_window PIVOT seed-level contrasts.

Lightweight analysis for the reduced-rho pivot study only.
Does NOT replace AIEF_1_4_Twindow_sensitivity_analysis_v3.py
(which expects the full 40 x 5 x 4 production grid).

Design
------
Unit of inference: one seed (graph realization).
Conditions are paired within seed.

Estimands
---------
1. Regime contrast (continue branch):
       Delta_rho(Y) = Y(seed, rho, continue) - Y(seed, 1.0, continue)

2. Branch gap at fixed rho:
       G_rho,b(Y) = Y(seed, rho, b) - Y(seed, rho, continue)

3. Branch difference-in-differences:
       I_rho,b(Y) = G_rho,b(Y) - G_1.0,b(Y)

Primary outcomes (fixed-physical late horizon)
---------------------------------------------
  Weighted_similarity_late_fixed_physical
  Retention_contrast_late_fixed_physical
  P_mean_late_fixed_physical

Example
-------
  python3 AIEF_1_4_Twindow_pivot_seed_contrasts.py \\
    --csv runs_pivot_study/ebfec9a5c419/AIEF_1_4_Twindow_sensitivity_ebfec9a5c419_scalar_summary.csv \\
    --output-dir runs_pivot_study/ebfec9a5c419/pivot_seed_contrasts \\
    --bootstrap-seed 20260811
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ANALYSIS_VERSION = "pivot-seed-contrasts-v1"
BASELINE_RHO = 1.0
PRIMARY_OUTCOMES = (
    "Weighted_similarity_late_fixed_physical",
    "Retention_contrast_late_fixed_physical",
    "P_mean_late_fixed_physical",
)
NON_CONTINUE = ("reset_ema", "reset_B", "future_shuffle")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--csv",
        required=True,
        help="pivot scalar summary CSV path",
    )
    p.add_argument(
        "--output-dir",
        default=None,
        help="output directory (default: <csv_dir>/pivot_seed_contrasts)",
    )
    p.add_argument(
        "--bootstrap",
        type=int,
        default=10_000,
        help="bootstrap repetitions for seed-level means (default: 10000)",
    )
    p.add_argument(
        "--bootstrap-seed",
        type=int,
        default=20260811,
        help="RNG seed for bootstrap (default: 20260811)",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="allow writing into a non-empty output directory",
    )
    return p.parse_args()


def load_scalar(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"seed": str, "branch": str})
    df["rho"] = pd.to_numeric(df["rho"], errors="coerce")
    for col in PRIMARY_OUTCOMES:
        if col not in df.columns:
            raise RuntimeError(f"Missing required column: {col}")
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def validate_pivot_frame(df: pd.DataFrame) -> dict[str, Any]:
    seeds = sorted(df["seed"].unique().tolist())
    rhos = sorted(float(r) for r in df["rho"].unique())
    branches = sorted(df["branch"].unique().tolist())

    info = {
        "n_rows": int(len(df)),
        "n_seeds": len(seeds),
        "rho_values": rhos,
        "branches": branches,
    }

    if BASELINE_RHO not in rhos:
        raise RuntimeError(
            f"Baseline rho={BASELINE_RHO} missing from data: {rhos}"
        )
    if "continue" not in branches:
        raise RuntimeError("branch 'continue' missing from data")

    expected_rows = len(seeds) * len(rhos) * len(branches)
    if len(df) != expected_rows:
        # Allow incomplete pivot only with explicit warning later; still require
        # unique (seed, rho, branch) keys.
        dup = df.duplicated(subset=["seed", "rho", "branch"]).sum()
        if dup:
            raise RuntimeError(f"Duplicate (seed, rho, branch) rows: {dup}")

    counts = df.groupby(["seed", "rho", "branch"]).size()
    if (counts != 1).any():
        raise RuntimeError("Non-unique (seed, rho, branch) combinations")

    return info


def bootstrap_mean_ci(
    values: np.ndarray,
    n_boot: int,
    rng: np.random.Generator,
) -> tuple[float, float, float, int]:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    n = int(x.size)
    if n == 0:
        return float("nan"), float("nan"), float("nan"), 0
    mean = float(np.mean(x))
    if n == 1 or n_boot <= 0:
        return mean, mean, mean, n
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = np.mean(x[idx], axis=1)
    lo = float(np.percentile(boots, 2.5))
    hi = float(np.percentile(boots, 97.5))
    return mean, lo, hi, n


def build_lookup(df: pd.DataFrame) -> dict[tuple[str, float, str], dict[str, float]]:
    out: dict[tuple[str, float, str], dict[str, float]] = {}
    for row in df.itertuples(index=False):
        key = (str(row.seed), float(row.rho), str(row.branch))
        out[key] = {name: float(getattr(row, name)) for name in PRIMARY_OUTCOMES}
    return out


def compute_regime_contrasts(
    df: pd.DataFrame,
    lookup: dict[tuple[str, float, str], dict[str, float]],
) -> pd.DataFrame:
    seeds = sorted(df["seed"].unique())
    rhos = sorted(float(r) for r in df["rho"].unique() if float(r) != BASELINE_RHO)
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        base_key = (seed, BASELINE_RHO, "continue")
        if base_key not in lookup:
            continue
        base = lookup[base_key]
        for rho in rhos:
            key = (seed, rho, "continue")
            if key not in lookup:
                continue
            cur = lookup[key]
            for outcome in PRIMARY_OUTCOMES:
                rows.append(
                    {
                        "seed": seed,
                        "rho": rho,
                        "branch": "continue",
                        "outcome": outcome,
                        "value_rho": cur[outcome],
                        "value_baseline": base[outcome],
                        "delta": cur[outcome] - base[outcome],
                    }
                )
    return pd.DataFrame(rows)


def compute_branch_gaps(
    df: pd.DataFrame,
    lookup: dict[tuple[str, float, str], dict[str, float]],
) -> pd.DataFrame:
    seeds = sorted(df["seed"].unique())
    rhos = sorted(float(r) for r in df["rho"].unique())
    branches = [b for b in NON_CONTINUE if b in set(df["branch"])]
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        for rho in rhos:
            cont_key = (seed, rho, "continue")
            if cont_key not in lookup:
                continue
            cont = lookup[cont_key]
            for branch in branches:
                key = (seed, rho, branch)
                if key not in lookup:
                    continue
                cur = lookup[key]
                for outcome in PRIMARY_OUTCOMES:
                    rows.append(
                        {
                            "seed": seed,
                            "rho": rho,
                            "branch": branch,
                            "outcome": outcome,
                            "value_branch": cur[outcome],
                            "value_continue": cont[outcome],
                            "gap": cur[outcome] - cont[outcome],
                        }
                    )
    return pd.DataFrame(rows)


def compute_did(
    gaps: pd.DataFrame,
) -> pd.DataFrame:
    if gaps.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    # Index baseline gaps by (seed, branch, outcome)
    base = gaps[gaps["rho"] == BASELINE_RHO].set_index(
        ["seed", "branch", "outcome"]
    )["gap"]
    alt = gaps[gaps["rho"] != BASELINE_RHO]
    for row in alt.itertuples(index=False):
        key = (row.seed, row.branch, row.outcome)
        if key not in base.index:
            continue
        g0 = float(base.loc[key])
        rows.append(
            {
                "seed": row.seed,
                "rho": float(row.rho),
                "branch": row.branch,
                "outcome": row.outcome,
                "gap_rho": float(row.gap),
                "gap_baseline": g0,
                "did": float(row.gap) - g0,
            }
        )
    return pd.DataFrame(rows)


def summarize(
    frame: pd.DataFrame,
    value_col: str,
    group_cols: list[str],
    n_boot: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for keys, group in frame.groupby(group_cols, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        mean, lo, hi, n = bootstrap_mean_ci(
            group[value_col].to_numpy(dtype=float),
            n_boot=n_boot,
            rng=rng,
        )
        std = float(np.nanstd(group[value_col].to_numpy(dtype=float), ddof=1)) if n > 1 else 0.0
        positive = float(np.mean(group[value_col].to_numpy(dtype=float) > 0)) if n else float("nan")
        rec = {col: val for col, val in zip(group_cols, keys)}
        rec.update(
            {
                "n": n,
                "mean": mean,
                "std": std,
                "ci_low": lo,
                "ci_high": hi,
                "frac_positive": positive,
            }
        )
        rows.append(rec)
    return pd.DataFrame(rows)


def save_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def make_report(
    info: dict[str, Any],
    regime_sum: pd.DataFrame,
    gap_sum: pd.DataFrame,
    did_sum: pd.DataFrame,
) -> str:
    lines = [
        "AIEF-1.4 T_window PIVOT seed-level contrasts",
        "=" * 72,
        f"analysis_version: {ANALYSIS_VERSION}",
        f"n_seeds: {info['n_seeds']}",
        f"rho_values: {info['rho_values']}",
        f"branches: {info['branches']}",
        f"n_rows: {info['n_rows']}",
        "",
        "Interpretation constraints",
        "-" * 72,
        "* Seed is the independent unit; edges are not.",
        "* This is a pivot (reduced rho set), not the full production study.",
        "* Bootstrap CIs are seed-level percentile intervals.",
        "* Do not treat driver Freezeable=True as analysis_v3 readiness.",
        "",
        "Regime contrasts (continue): mean Delta = Y(rho) - Y(1.0)",
        "-" * 72,
    ]
    if regime_sum.empty:
        lines.append("(none)")
    else:
        for row in regime_sum.itertuples(index=False):
            lines.append(
                f"  rho={row.rho:.2f}  {row.outcome}: "
                f"mean={row.mean:.6g}  95% CI=[{row.ci_low:.6g}, {row.ci_high:.6g}]  "
                f"n={row.n}"
            )

    lines.extend(
        [
            "",
            "Branch gaps vs continue: mean G = Y(branch) - Y(continue)",
            "-" * 72,
        ]
    )
    if gap_sum.empty:
        lines.append("(none)")
    else:
        for row in gap_sum.itertuples(index=False):
            lines.append(
                f"  rho={row.rho:.2f}  {row.branch}  {row.outcome}: "
                f"mean={row.mean:.6g}  95% CI=[{row.ci_low:.6g}, {row.ci_high:.6g}]  "
                f"n={row.n}"
            )

    lines.extend(
        [
            "",
            "Branch DID: mean I = G(rho) - G(1.0)",
            "-" * 72,
        ]
    )
    if did_sum.empty:
        lines.append("(none)")
    else:
        for row in did_sum.itertuples(index=False):
            lines.append(
                f"  rho={row.rho:.2f}  {row.branch}  {row.outcome}: "
                f"mean={row.mean:.6g}  95% CI=[{row.ci_low:.6g}, {row.ci_high:.6g}]  "
                f"n={row.n}"
            )

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv).resolve()
    if not csv_path.is_file():
        print(f"MISSING csv: {csv_path}", flush=True)
        return 1

    output_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else csv_path.parent / "pivot_seed_contrasts"
    )
    if output_dir.exists() and any(output_dir.iterdir()) and not args.overwrite:
        print(
            f"Output directory not empty: {output_dir}\n"
            "Pass --overwrite or choose a new --output-dir.",
            flush=True,
        )
        return 1
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading {csv_path}")
    df = load_scalar(csv_path)
    info = validate_pivot_frame(df)
    print(
        f"  seeds={info['n_seeds']}  rho={info['rho_values']}  "
        f"branches={info['branches']}  rows={info['n_rows']}"
    )

    lookup = build_lookup(df)
    regime = compute_regime_contrasts(df, lookup)
    gaps = compute_branch_gaps(df, lookup)
    did = compute_did(gaps)

    rng = np.random.default_rng(args.bootstrap_seed)
    regime_sum = summarize(
        regime, "delta", ["rho", "outcome"], args.bootstrap, rng
    )
    gap_sum = summarize(
        gaps, "gap", ["rho", "branch", "outcome"], args.bootstrap, rng
    )
    did_sum = summarize(
        did, "did", ["rho", "branch", "outcome"], args.bootstrap, rng
    )

    save_csv(output_dir / "pivot_regime_contrasts_by_seed.csv", regime)
    save_csv(output_dir / "pivot_branch_gaps_by_seed.csv", gaps)
    save_csv(output_dir / "pivot_branch_did_by_seed.csv", did)
    save_csv(output_dir / "pivot_regime_summary.csv", regime_sum)
    save_csv(output_dir / "pivot_branch_gap_summary.csv", gap_sum)
    save_csv(output_dir / "pivot_branch_did_summary.csv", did_sum)

    report = make_report(info, regime_sum, gap_sum, did_sum)
    report_path = output_dir / "pivot_seed_contrasts_report.txt"
    report_path.write_text(report + "\n", encoding="utf-8")

    manifest = {
        "analysis": ANALYSIS_VERSION,
        "csv": str(csv_path),
        "output_dir": str(output_dir),
        "bootstrap": args.bootstrap,
        "bootstrap_seed": args.bootstrap_seed,
        "primary_outcomes": list(PRIMARY_OUTCOMES),
        "baseline_rho": BASELINE_RHO,
        "frame": info,
        "created_unix": time.time(),
        "note": (
            "Pivot-only seed-level contrasts. Not analysis_v3. "
            "Not a substitute for the full 5-rho production study."
        ),
    }
    (output_dir / "pivot_analysis_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print()
    print(report)
    print(f"Saved analysis to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
