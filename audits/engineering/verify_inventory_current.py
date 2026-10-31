#!/usr/bin/env python3
"""Current-tree counterpart of audits/engineering/verify_inventory.py (which is left unchanged).

verify_inventory.py is the Milestone 1 gate: it requires that nothing from e47bad1 was modified or
deleted, so it fails at [1/5] on every later tree by design (registry/README.md). This script runs
the same five gates against the CURRENT tree, using the two inventories:

  [1/5] e47bad1 snapshot accountability: tools/ci/check_artifact_pins.py -- every one of the 2,898
        registry/artifacts.csv rows matches the tree or is on its reviewed known-changed /
        known-missing allowlist (replaces "zero files modified", which no longer holds).
  [2/5] current inventory: tools/ci/check_current_inventory.py -- every tracked file (and member of a
        tracked .zip) appears exactly once in registry/artifacts_current.csv with a matching sha256.
  [3/5] controlled vocabularies across registry/{artifacts,claims,studies,relocation_map}.csv and
        Unreviewed = 0 (same rule as verify_inventory.py [3/5]).
  [4/5] Lean lock hashes in lean/AIEFProofs/AIEF_LEAN_PROJECT_LOCK_HASHES.txt (same as [4/5]).
  [5/5] live aief_modular.authority.verify_authority_lock() (same as [5/5]; needs requirements.txt).

    python3 audits/engineering/verify_inventory_current.py [--skip-authority]

Exit status: 0 = all gates passed, 1 = a gate failed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VALID_STATUS = {"Supported", "Frozen", "Exploratory", "Superseded", "Rejected", "Incomplete", "Unreviewed"}
VALID_SCOPE = {"Implementation identity", "Finite numerical observation", "Controlled experimental result",
               "Conditional theorem", "Formalized theorem", "Conjecture"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def run_tool(rel: str) -> int:
    script = REPO / rel
    if not script.is_file():
        print(f"  FAIL: {rel} not found", file=sys.stderr)
        return 1
    r = subprocess.run([sys.executable, str(script), "--repo", str(REPO)], capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if l.strip()][-3:]
    for l in tail:
        print(f"  {l}")
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-4000:] + r.stderr[-2000:])
    return r.returncode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skip-authority", action="store_true", help="skip [5/5] (no numpy/scipy installed)")
    a = ap.parse_args(argv)

    print("[1/5] e47bad1 snapshot accountability (tools/ci/check_artifact_pins.py)...")
    if run_tool("tools/ci/check_artifact_pins.py") != 0:
        print("FAIL: [1/5]", file=sys.stderr)
        return 1

    print("[2/5] Current-tree inventory (tools/ci/check_current_inventory.py)...")
    if run_tool("tools/ci/check_current_inventory.py") != 0:
        print("FAIL: [2/5]", file=sys.stderr)
        return 1

    print("[3/5] Controlled vocabularies across registry CSVs...")
    for table in ("artifacts.csv", "claims.csv", "studies.csv", "relocation_map.csv"):
        rows = list(csv.DictReader((REPO / "registry" / table).open(encoding="utf-8")))
        for idx, r in enumerate(rows, start=2):
            if r["artifact_status"] not in VALID_STATUS or r["evidence_scope"] not in VALID_SCOPE:
                print(f"FAIL: {table}:{idx} status={r['artifact_status']!r} scope={r['evidence_scope']!r}",
                      file=sys.stderr)
                return 1
    arts = list(csv.DictReader((REPO / "registry" / "artifacts.csv").open(encoding="utf-8")))
    unreviewed = [r["path"] for r in arts if r["artifact_status"] == "Unreviewed"]
    if unreviewed:
        print(f"FAIL: {len(unreviewed)} artifacts still Unreviewed", file=sys.stderr)
        return 1
    print("  PASS: vocabularies conform (Unreviewed = 0).")

    print("[4/5] Lean project hash ledger (lean/AIEFProofs/AIEF_LEAN_PROJECT_LOCK_HASHES.txt)...")
    lean_root = REPO / "lean" / "AIEFProofs"
    n = 0
    for line in (lean_root / "AIEF_LEAN_PROJECT_LOCK_HASHES.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.strip().split(None, 1)
        target = lean_root / rel.lstrip("./")
        if target.name == "AIEF_LEAN_PROJECT_LOCK_HASHES.txt":
            continue
        if sha256_file(target) != digest:
            print(f"FAIL: Lean lock hash mismatch on {target}", file=sys.stderr)
            return 1
        n += 1
    print(f"  PASS: {n} Lean source/config digests verified.")

    print("[5/5] Live aief_modular.authority.verify_authority_lock()...")
    if a.skip_authority:
        print("  SKIPPED (--skip-authority)")
    else:
        mod_root = REPO / "AIEF_Experiments" / "aief_modular_platform_v1_analysis_v4"
        sys.path.insert(0, str(REPO))
        sys.path.insert(0, str(mod_root))
        import aief_experiment_engine_v1 as engine  # type: ignore
        from aief_modular.authority import load_authority_lock, verify_authority_lock  # type: ignore
        lock, lock_sha = load_authority_lock(mod_root / "AIEF_1_4_FROZEN_5a9f093a2fe0.authority.lock.json")
        verify_authority_lock(
            lock, authority_root=REPO,
            supplied_artifacts={
                "manifest": REPO / "runs/5a9f093a2fe0/manifest.json",
                "npz": REPO / "runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz",
                "scalar": REPO / "runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv",
            },
            runtime_engine_path=engine.__file__,
        )
        print(f"  PASS: authority lock verified (lock_sha256={lock_sha[:16]}...).")
    print("\nALL CURRENT-TREE INVENTORY, VOCABULARY & AUTHORITY LOCK GATES PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
