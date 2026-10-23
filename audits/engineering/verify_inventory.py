#!/usr/bin/env python3
"""AIEFS Milestone 1 Conservation, SHA-256 Inventory, Vocabulary & Authority Lock Verifier.

Verifies:
1. Zero existing files from base commit e47bad150792425eb8e962ff636c69289eedd8b1 were
   modified (M), deleted (D), renamed (R), or type-changed (T).
2. Every single tracked file from base commit e47bad15... (2,760 files) and every single
   archive member inside all 3 .zip files (138 entries = 2,898 total entries) is accounted
   for in registry/artifacts.csv with matching byte size and SHA-256 digest.
3. Zero artifacts remain in 'Unreviewed' status, and every row across registry/{artifacts,
   claims,studies,relocation_map}.csv strictly adheres to the two-axis controlled vocabularies
   (Artifact Status x Evidence Scope).
4. Live execution of aief_modular.authority.verify_authority_lock() succeeds against the
   untouched repository root (all 7 SHA-256 locks verified).
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

BASE_COMMIT = "e47bad150792425eb8e962ff636c69289eedd8b1"

VALID_STATUS = {
    "Supported",
    "Frozen",
    "Exploratory",
    "Superseded",
    "Rejected",
    "Incomplete",
    "Unreviewed",
}
VALID_SCOPE = {
    "Implementation identity",
    "Finite numerical observation",
    "Controlled experimental result",
    "Conditional theorem",
    "Formalized theorem",
    "Conjecture",
}

ZIP_ARCHIVES = (
    "AIEF_Experiments/aief_modular_platform_v1_analysis_v4.zip",
    "workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f.zip",
    "workspace-019ff402-3611-7903-99ce-0679e00cb830.zip",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    print(f"[1/5] Checking non-destructive Git conservation against {BASE_COMMIT[:12]}...")
    diff_raw = subprocess.check_output(
        ["git", "-c", "core.quotepath=false", "diff", "--name-status", BASE_COMMIT],
        cwd=repo_root,
        text=True,
    ).splitlines()
    non_additions = [line for line in diff_raw if not line.startswith("A\t")]
    if non_additions:
        print("FAIL: Existing tracked files were modified/moved/deleted:", file=sys.stderr)
        for line in non_additions[:25]:
            print(f"  {line}", file=sys.stderr)
        return 1
    print(f"  PASS: 0 existing files modified/deleted/renamed ({len(diff_raw)} tracked additions so far).")

    print("[2/5] Verifying SHA-256 digests & byte counts across all 2,760 base worktree files + 138 zip entries...")
    base_tracked = (
        subprocess.check_output(
            ["git", "-c", "core.quotepath=false", "ls-tree", "-r", "-z", "--name-only", BASE_COMMIT],
            cwd=repo_root,
            text=True,
        )
        .rstrip("\0")
        .split("\0")
    )
    artifacts_path = repo_root / "registry" / "artifacts.csv"
    rows = list(csv.DictReader(artifacts_path.open("r", encoding="utf-8")))
    wt_rows = {r["path"]: r for r in rows if r["container"] == "worktree"}
    zip_rows = {(r["container"], r["path"]): r for r in rows if r["container"].startswith("zip:")}

    if set(wt_rows.keys()) != set(base_tracked):
        missing = set(base_tracked) - set(wt_rows.keys())
        extra = set(wt_rows.keys()) - set(base_tracked)
        print(f"FAIL: Worktree set mismatch: missing={len(missing)}, extra={len(extra)}", file=sys.stderr)
        return 1

    for rel in base_tracked:
        fp = repo_root / rel
        expected_sha = wt_rows[rel]["sha256"]
        actual_sha = sha256_file(fp)
        actual_size = fp.stat().st_size
        if actual_sha != expected_sha or int(wt_rows[rel]["size_bytes"]) != actual_size:
            print(f"FAIL: Digest/size mismatch for {rel}", file=sys.stderr)
            return 1

    zip_checked = 0
    for zrel in ZIP_ARCHIVES:
        with zipfile.ZipFile(repo_root / zrel, "r") as zf:
            for zi in zf.infolist():
                if zi.is_dir():
                    continue
                key = (f"zip:{zrel}", zi.filename)
                if key not in zip_rows:
                    print(f"FAIL: Missing zip member {key}", file=sys.stderr)
                    return 1
                actual_sha = hashlib.sha256(zf.read(zi.filename)).hexdigest()
                if actual_sha != zip_rows[key]["sha256"]:
                    print(f"FAIL: Zip digest mismatch for {key}", file=sys.stderr)
                    return 1
                zip_checked += 1
    print(f"  PASS: Verified {len(base_tracked)} worktree files + {zip_checked} zip members ({len(rows)} total rows).")

    print("[3/5] Validating controlled vocabularies across all registry CSVs...")
    for table_name in ("artifacts.csv", "claims.csv", "studies.csv", "relocation_map.csv"):
        trows = list(csv.DictReader((repo_root / "registry" / table_name).open("r", encoding="utf-8")))
        for idx, r in enumerate(trows, start=2):
            if r["artifact_status"] not in VALID_STATUS:
                print(f"FAIL: {table_name}:{idx} invalid artifact_status={r['artifact_status']!r}", file=sys.stderr)
                return 1
            if r["evidence_scope"] not in VALID_SCOPE:
                print(f"FAIL: {table_name}:{idx} invalid evidence_scope={r['evidence_scope']!r}", file=sys.stderr)
                return 1
    unreviewed = [r["path"] for r in rows if r["artifact_status"] == "Unreviewed"]
    if unreviewed:
        print(f"FAIL: {len(unreviewed)} artifacts still marked Unreviewed", file=sys.stderr)
        return 1
    print("  PASS: All registry tables strictly conform to controlled vocabularies (Unreviewed = 0).")

    print("[4/5] Verifying Lean 4 project hash ledger (AIEF_LEAN_PROJECT_LOCK_HASHES.txt)...")
    lean_root = repo_root / "lean" / "AIEFProofs"
    lean_ledger = lean_root / "AIEF_LEAN_PROJECT_LOCK_HASHES.txt"
    lean_verified = 0
    for line in lean_ledger.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel_target = line.split(None, 1)
        target_file = lean_root / rel_target.lstrip("./")
        if target_file.name == "AIEF_LEAN_PROJECT_LOCK_HASHES.txt":
            # Self-hash cannot match non-trivial fixed point; verify file exists
            continue
        actual = sha256_file(target_file)
        if actual != digest:
            print(f"FAIL: Lean lock hash mismatch on {target_file}: {actual} != {digest}", file=sys.stderr)
            return 1
        lean_verified += 1
    print(f"  PASS: Verified {lean_verified} Lean 4 source/config SHA-256 digests.")

    print("[5/5] Executing live aief_modular.authority.verify_authority_lock()...")
    mod_root = repo_root / "AIEF_Experiments" / "aief_modular_platform_v1_analysis_v4"
    sys.path.insert(0, str(repo_root))
    sys.path.insert(0, str(mod_root))
    import aief_experiment_engine_v1 as engine  # type: ignore
    from aief_modular.authority import load_authority_lock, verify_authority_lock  # type: ignore

    lock, lock_sha = load_authority_lock(mod_root / "AIEF_1_4_FROZEN_5a9f093a2fe0.authority.lock.json")
    verify_authority_lock(
        lock,
        authority_root=repo_root,
        supplied_artifacts={
            "manifest": repo_root / "runs/5a9f093a2fe0/manifest.json",
            "npz": repo_root / "runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz",
            "scalar": repo_root / "runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv",
        },
        runtime_engine_path=engine.__file__,
    )
    print(f"  PASS: Authority lock verified (lock_sha256={lock_sha[:16]}...).")
    print("\nALL MILESTONE 1 CONSERVATION, VOCABULARY & AUTHORITY LOCK GATES PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
