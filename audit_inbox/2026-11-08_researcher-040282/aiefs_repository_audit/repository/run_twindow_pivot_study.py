#!/usr/bin/env python3
"""AIEF T_window PIVOT study launcher (hardened).

Runs a reduced (pilot) T_window sensitivity study without permanently
editing the three production scripts:

  - aief_experiment_engine_v1.py
  - AIEF_1_4_Twindow_sensitivity.py
  - AIEF_1_4_Twindow_sensitivity_analysis_v3.py

How it works
------------
1. Imports the production driver in-process.
2. Temporarily overrides RHO_VALUES (and optional branch subset) in memory.
3. Invokes the driver main() with CLI args aimed at a separate run root.
4. Detects the hashed experiment directory the driver creates and writes
   PIVOT_STUDY_LABEL.json *inside that directory*.

Critical constraint (driver-enforced)
------------------------------------
Baseline equivalence requires --n-seeds to match the frozen production
seed list exactly (40 seeds for run 5a9f093a2fe0). A 2-seed pivot will
fail baseline and abort before the grid. Default here is therefore
n_seeds=40 with a reduced rho set.

RHO_VALUES must include 1.0 (driver dry-run / baseline requirement).

The driver reads RHO_VALUES and STUDY_BRANCHES inside main() (not as
frozen import-time derived constants for the grid loop), so in-memory
overrides are effective.

Default pivot design
--------------------
  n_seeds = 40
  rho     = (0.75, 1.0, 1.5)
  branches = full study set
  run-root = runs_pivot_study

Examples
--------
  python3 run_twindow_pivot_study.py \\
    --frozen-manifest runs/5a9f093a2fe0/manifest.json \\
    --frozen-npz runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz \\
    --frozen-scalar runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv

  python3 run_twindow_pivot_study.py --dry-run \\
    --frozen-manifest ... --frozen-npz ... --frozen-scalar ...
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


# Default pivot: full seed cohort (baseline-compatible), reduced rho
DEFAULT_RHO = (0.75, 1.0, 1.5)
DEFAULT_N_SEEDS = 40
DEFAULT_RUN_ROOT = "runs_pivot_study"
DEFAULT_MASTER_SEED = 20260714
DEFAULT_BRANCHES = (
    "continue",
    "reset_ema",
    "reset_B",
    "future_shuffle",
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Launch a labeled T_window PIVOT study without editing "
            "production scripts."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="directory containing the three production scripts (default: cwd)",
    )
    p.add_argument(
        "--n-seeds",
        type=int,
        default=DEFAULT_N_SEEDS,
        help=(
            f"number of seeds (default: {DEFAULT_N_SEEDS}). "
            "Must match frozen production seed count for baseline to pass."
        ),
    )
    p.add_argument(
        "--master-seed",
        type=int,
        default=DEFAULT_MASTER_SEED,
        help=f"master seed (default: {DEFAULT_MASTER_SEED})",
    )
    p.add_argument(
        "--rho",
        type=float,
        nargs="+",
        default=list(DEFAULT_RHO),
        help=f"rho values; must include 1.0 (default: {list(DEFAULT_RHO)})",
    )
    p.add_argument(
        "--branches",
        type=str,
        nargs="+",
        default=list(DEFAULT_BRANCHES),
        help="study branches (default: full study set)",
    )
    p.add_argument(
        "--run-root",
        type=str,
        default=DEFAULT_RUN_ROOT,
        help=f"output root distinct from production (default: {DEFAULT_RUN_ROOT})",
    )
    p.add_argument("--frozen-manifest", type=str, required=True)
    p.add_argument("--frozen-npz", type=str, required=True)
    p.add_argument("--frozen-scalar", type=str, required=True)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="validate pivot config via driver --dry-run only",
    )
    p.add_argument(
        "--baseline-only",
        action="store_true",
        help="run baseline certificate only (no rho grid)",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="pass --overwrite through to the driver",
    )
    return p.parse_args()


def write_pivot_label(target_dir: Path, meta: dict) -> Path:
    """Write pivot marker into the actual experiment directory."""
    target_dir.mkdir(parents=True, exist_ok=True)
    label_path = target_dir / "PIVOT_STUDY_LABEL.json"
    payload = {
        "label": "PIVOT_STUDY",
        "not_production": True,
        "freezeable": False,
        "analysis_v3_compatible": False,
        "expected_rho_count": len(meta.get("rho_values", [])),
        "expected_seed_count": meta.get("n_seeds"),
        "expected_branch_count": len(meta.get("branches", [])),
        "expected_rho_values": meta.get("rho_values"),
        "expected_branches": meta.get("branches"),
        "production_RHO_VALUES": meta.get("original_driver_RHO_VALUES"),
        "production_STUDY_BRANCHES": meta.get("original_driver_STUDY_BRANCHES"),
        "note": (
            "This directory was produced by run_twindow_pivot_study.py. "
            "Do not treat outputs as the freezeable full T_window study. "
            "AIEF_1_4_Twindow_sensitivity_analysis_v3.py expects the full "
            "40x5x4 production grid and will fail count checks on pivot data."
        ),
        "created_unix": time.time(),
        "meta": meta,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    label_path.write_text(text, encoding="utf-8")
    return label_path


def discover_experiment_dir(run_root: Path, before: set[Path]) -> Path:
    """Prefer the newly created hashed subdirectory under run_root."""
    after = set(run_root.glob("*"))
    new_dirs = sorted(p for p in (after - before) if p.is_dir())
    if len(new_dirs) == 1:
        return new_dirs[0]
    children = sorted(p for p in run_root.glob("*") if p.is_dir())
    if len(children) == 1:
        return children[0]
    return run_root


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    os.chdir(project_root)
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    engine_path = project_root / "aief_experiment_engine_v1.py"
    driver_path = project_root / "AIEF_1_4_Twindow_sensitivity.py"
    analysis_path = project_root / "AIEF_1_4_Twindow_sensitivity_analysis_v3.py"

    for path in (engine_path, driver_path, analysis_path):
        if not path.is_file():
            print(f"MISSING production script: {path}", file=sys.stderr)
            return 1

    for path in (args.frozen_manifest, args.frozen_npz, args.frozen_scalar):
        if not Path(path).is_file():
            print(f"MISSING frozen artifact: {path}", file=sys.stderr)
            return 1

    rho = tuple(float(r) for r in args.rho)
    branches = tuple(str(b) for b in args.branches)

    if not rho:
        print("ERROR: --rho must be non-empty", file=sys.stderr)
        return 1
    if 1.0 not in rho:
        print(
            "ERROR: RHO_VALUES must include 1.0 "
            "(driver baseline / dry-run requirement).",
            file=sys.stderr,
        )
        return 1
    if "continue" not in branches:
        print(
            "ERROR: study branches must include 'continue' "
            "(required for historical / DID metrics).",
            file=sys.stderr,
        )
        return 1
    if len(rho) != len(set(rho)):
        print("ERROR: --rho contains duplicates", file=sys.stderr)
        return 1
    if len(branches) != len(set(branches)):
        print("ERROR: --branches contains duplicates", file=sys.stderr)
        return 1

    import AIEF_1_4_Twindow_sensitivity as driver

    original_rho = tuple(driver.RHO_VALUES)
    original_branches = tuple(driver.STUDY_BRANCHES)

    invalid_branches = set(branches) - set(original_branches)
    if invalid_branches:
        print(
            "ERROR: unknown branch names (not in production STUDY_BRANCHES): "
            f"{sorted(invalid_branches)}",
            file=sys.stderr,
        )
        print(f"  Allowed: {list(original_branches)}", file=sys.stderr)
        return 1

    if int(args.n_seeds) != 40 and not args.dry_run:
        print(
            "WARNING: frozen production uses 40 paired seeds. "
            f"n_seeds={args.n_seeds} will almost certainly fail mandatory "
            "baseline equivalence and abort before the grid.",
            file=sys.stderr,
        )

    run_root = Path(args.run_root)
    run_root.mkdir(parents=True, exist_ok=True)

    label_meta = {
        "project_root": str(project_root),
        "master_seed": int(args.master_seed),
        "n_seeds": int(args.n_seeds),
        "rho_values": list(rho),
        "branches": list(branches),
        "run_root": str(run_root.resolve()),
        "frozen_manifest": str(Path(args.frozen_manifest).resolve()),
        "frozen_npz": str(Path(args.frozen_npz).resolve()),
        "frozen_scalar": str(Path(args.frozen_scalar).resolve()),
        "original_driver_RHO_VALUES": list(original_rho),
        "original_driver_STUDY_BRANCHES": list(original_branches),
        "mode": (
            "dry-run"
            if args.dry_run
            else "baseline-only"
            if args.baseline_only
            else "pivot-grid"
        ),
    }

    argv = [
        str(driver_path),
        "--master-seed",
        str(args.master_seed),
        "--n-seeds",
        str(args.n_seeds),
        "--run-root",
        str(run_root),
        "--frozen-manifest",
        str(args.frozen_manifest),
        "--frozen-npz",
        str(args.frozen_npz),
        "--frozen-scalar",
        str(args.frozen_scalar),
    ]
    if args.dry_run:
        argv.append("--dry-run")
    if args.baseline_only:
        argv.append("--baseline-only")
    if args.overwrite:
        argv.append("--overwrite")

    print("=" * 72)
    print("AIEF T_window PIVOT study launcher")
    print("=" * 72)
    print(f"  project_root : {project_root}")
    print(f"  n_seeds      : {args.n_seeds}")
    print(f"  master_seed  : {args.master_seed}")
    print(f"  rho          : {rho}")
    print(f"  branches     : {branches}")
    print(f"  run_root     : {run_root.resolve()}")
    print(f"  production scripts left UNCHANGED on disk")
    print("=" * 72)

    old_argv = sys.argv
    before = set(run_root.glob("*"))
    try:
        # Driver reads these inside main(), not as import-time grid constants.
        driver.RHO_VALUES = rho
        driver.STUDY_BRANCHES = branches
        sys.argv = argv
        driver.main()
    finally:
        sys.argv = old_argv
        driver.RHO_VALUES = original_rho
        driver.STUDY_BRANCHES = original_branches

    experiment_dir = discover_experiment_dir(run_root, before)
    label_path = write_pivot_label(
        experiment_dir,
        {
            **label_meta,
            "experiment_dir": str(experiment_dir.resolve()),
        },
    )
    if experiment_dir.resolve() != run_root.resolve():
        write_pivot_label(
            run_root,
            {
                **label_meta,
                "experiment_dir": str(experiment_dir.resolve()),
                "note_location": f"Authoritative label also written to {label_path}",
            },
        )

    print("\nPivot launcher finished.")
    print(f"  Experiment dir : {experiment_dir}")
    print(f"  Marker         : {label_path}")
    print(
        "  Do NOT run analysis_v3 on this output without a separate "
        "pivot analysis config."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
