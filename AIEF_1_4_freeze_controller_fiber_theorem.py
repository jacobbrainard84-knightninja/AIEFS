#!/usr/bin/env python3
"""Freeze the AIEF-1.4 multiplier-controller theorem supplement.

This is an additive administrative freeze.  It does not overwrite the earlier
analysis-lineage freeze and does not re-run the frozen production trajectory.
Historical execution hashes in per-analysis manifests remain authoritative for
saved replay evidence.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
FREEZE_DATE = "2026-07-27"
PRODUCTION_RUN_HASH = "5a9f093a2fe0"
EXCEPTIONAL_SEED = "4619122171158768524"
CLAIM_PATH = ROOT / "AIEF_1_4_CONTROLLER_FIBER_CLAIM_REGISTRY.csv"
MANIFEST_PATH = ROOT / "AIEF_1_4_CONTROLLER_FIBER_FREEZE_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_text(path: Path, text: str) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def atomic_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def claim_rows() -> list[dict[str, str]]:
    return [
        {
            "id": "CF01",
            "claim": "The capacity tangent-cone lineality is obtained by zeroing inactive-edge directions and exact active-row sums.",
            "status": "exact theorem",
            "scope": "capacity polytope at a fixed feasible point",
            "hypotheses": "positive support and exact active capacity set are specified",
            "evidence_authority": "polyhedral proof in theorem package",
            "caveat": "This is distinct from finite-safeguard controller geometry.",
        },
        {
            "id": "CF02",
            "claim": "A clipped row is strictly interior in the projected output at finite epsilon.",
            "status": "exact implementation theorem",
            "scope": "safeguarded admissibility output",
            "hypotheses": "epsilon>0, positive capacity, row scale clipped",
            "evidence_authority": "algebraic proof from minimum.outer scaling",
            "caveat": "The statement concerns the output, not necessarily the input weight state.",
        },
        {
            "id": "CF03",
            "claim": "The admissibility map is exactly affine on multiplier-controller fibers, including active endpoint ties.",
            "status": "exact implementation theorem",
            "scope": "local fixed multiplier-controller neighborhood",
            "hypotheses": "proposal support and gate persist; strict winner inequalities and identity-edge margins persist",
            "evidence_authority": "factorization and controller-fiber proof",
            "caveat": "A nonwinning endpoint may change clipping label without changing the selected multiplier.",
        },
        {
            "id": "CF04",
            "claim": "Kernel preservation is equivalent to a row-space intertwining factorization CD=Gamma C.",
            "status": "exact linear-algebra theorem",
            "scope": "finite-dimensional linear maps",
            "hypotheses": "L=ker(C)",
            "evidence_authority": "factorization proof in theorem package",
            "caveat": "Full row rank is needed for uniqueness of Gamma, not existence.",
        },
        {
            "id": "CF05",
            "claim": "The exceptional K3 effective winner map is (7,2,7) throughout 32,001 saved states.",
            "status": "finite replay fact",
            "scope": f"production run {PRODUCTION_RUN_HASH}, exceptional seed {EXCEPTIONAL_SEED}",
            "hypotheses": "saved actual-branch audit",
            "evidence_authority": "historical actual-admissibility branch analysis manifest",
            "caveat": "This does not establish infinite-time branch persistence.",
        },
        {
            "id": "CF06",
            "claim": "Conditional on the audited winner map, the exceptional controller kernel is span(1,-1,-1).",
            "status": "exact algebra conditional on replay fact",
            "scope": "K3 edges (25,29,59)",
            "hypotheses": "controller rows J={2,7}",
            "evidence_authority": "explicit 2x3 incidence calculation",
            "caveat": "This is a multiplier-controller fiber, not necessarily exact face lineality.",
        },
        {
            "id": "CF07",
            "claim": "The fixed right carrier v is invariant if and only if s2=s7.",
            "status": "exact conditional operator identity",
            "scope": "selected frozen-driver K3 block",
            "hypotheses": "fixed winner block and positive selected proposal support",
            "evidence_authority": "direct matrix multiplication",
            "caveat": "The replay realizes this only approximately at finite times.",
        },
        {
            "id": "CF08",
            "claim": "After right closure, u(r) is an exact normalized pointwise left covector.",
            "status": "exact conditional operator identity",
            "scope": "selected frozen-driver K3 block",
            "hypotheses": "s2=s7 and beta59>0",
            "evidence_authority": "direct matrix multiplication",
            "caveat": "Pointwise left eigenvectors do not automatically form a fixed or moving cocycle dual.",
        },
        {
            "id": "CF09",
            "claim": "One-sided proposal equalization makes the selected K3 branch matrices converge to the fixed analytic family.",
            "status": "exact conditional operator identity",
            "scope": "isolated equal-capacity K3 approaching its triple-tie boundary",
            "hypotheses": "rows 2 and 7 clipped; strict winner signs remain positive at finite steps; proposal differences tend to zero",
            "evidence_authority": "exact scale, beta, and branch-cone identities",
            "caveat": "At the exact tie the full K3 controller kernel is zero; this is a one-sided matrix limit, not a unique classical derivative.",
        },
        {
            "id": "CF10",
            "claim": "The selected frozen-driver K3 block becomes very close to the fixed analytic family by the saved final time.",
            "status": "finite replay fact",
            "scope": f"production run {PRODUCTION_RUN_HASH}, exceptional seed {EXCEPTIONAL_SEED}",
            "hypotheses": "saved nested-family and analytic-residual outputs",
            "evidence_authority": "historical per-analysis manifests",
            "caveat": "Small final residuals do not prove asymptotic convergence.",
        },
        {
            "id": "CF11",
            "claim": "Coupled phase/EMA feedback forces both K3 proposal differences to zero asymptotically.",
            "status": "open conjecture",
            "scope": "future exceptional trajectory",
            "hypotheses": "at minimum, persistent isolated support and fixed controller branch",
            "evidence_authority": "finite-horizon mechanism evidence only",
            "caveat": "Neither asymptotic convergence nor continuation beyond the saved horizon is proved.",
        },
        {
            "id": "CF12",
            "claim": "The exceptional support, clipping, and winner branch persist for all future time.",
            "status": "open conjecture",
            "scope": "future exceptional trajectory",
            "hypotheses": "frozen split state under unchanged production dynamics",
            "evidence_authority": "finite saved branch record only",
            "caveat": "A strong trajectory theorem must prove this rather than assume it.",
        },
    ]


def validate_text() -> None:
    package = (ROOT / "AIEF_1_4_CONTROLLER_FIBER_THEOREM_PACKAGE.md").read_text(
        encoding="utf-8"
    )
    manuscript = (ROOT / "AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md").read_text(
        encoding="utf-8"
    )
    required_package = [
        "Proposition 3.1 — clipped rows are interior in the projected output",
        "Proposition 4.1 — exact fiber-affine identity",
        "Proposition 7.2 — exact controller kernel conditional on the audited winner map",
        "Proposition 9.1 — exact pointwise left covector",
        "Conditional branch theorem",
        "Strong trajectory theorem",
    ]
    required_manuscript = [
        "Proposition 2.10 — clipped rows are interior in the projected output",
        "Proposition 2.11 — exact fiber-affine multiplier identity",
        "Proposition 5.2 — exact exceptional controller-row carrier",
        "Proposition 6.4 — exact pointwise left covector",
        "Conditional branch theorem",
        "Strong trajectory theorem",
    ]
    for marker in required_package:
        if marker not in package:
            raise RuntimeError(f"missing theorem-package marker: {marker}")
    for marker in required_manuscript:
        if marker not in manuscript:
            raise RuntimeError(f"missing manuscript marker: {marker}")


def main() -> None:
    validate_text()
    rows = claim_rows()
    fields = [
        "id",
        "claim",
        "status",
        "scope",
        "hypotheses",
        "evidence_authority",
        "caveat",
    ]
    atomic_csv(CLAIM_PATH, rows, fields)

    document_files = [
        "AIEF_1_4_CONTROLLER_FIBER_THEOREM_PACKAGE.md",
        "AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md",
        "AIEF_1_4_OPERATOR_COCYCLE_CLOSURE_THEOREM_NOTE.md",
        "AIEF_1_4_CONTROLLER_FIBER_CLAIM_REGISTRY.csv",
    ]
    source_files = [
        "AIEF_1_4_actual_admissibility_branch_audit.py",
        "AIEF_1_4_frozen_driver_cocycle_analysis.py",
        "AIEF_1_4_nested_operator_family_audit.py",
        "AIEF_1_4_biorthogonal_triangular_closure.py",
        "AIEF_1_4_existing_clique_invariant_subspaces.py",
        "AIEF_1_4_defect_recurrence_analytic_mode.py",
        "AIEF_1_4_defect_causal_ema_trace.py",
        "AIEF_1_4_radial_observable_subsystem_analysis.py",
        "AIEF_1_4_resonant_tracking_angular_analysis.py",
        "AIEF_1_4_phase_balance_source_dynamics.py",
    ]
    parent_manifest = ROOT / "AIEF_1_4_lineage_freeze_manifest.json"
    for filename in document_files + source_files:
        if not (ROOT / filename).is_file():
            raise FileNotFoundError(ROOT / filename)
    if not parent_manifest.is_file():
        raise FileNotFoundError(parent_manifest)

    manifest: dict[str, Any] = {
        "freeze_date": FREEZE_DATE,
        "freeze_kind": "additive theorem-package freeze; no trajectory regeneration",
        "production_run_hash": PRODUCTION_RUN_HASH,
        "exceptional_seed": EXCEPTIONAL_SEED,
        "claim_count": len(rows),
        "claim_status_counts": {},
        "parent_lineage_freeze": {
            "path": parent_manifest.name,
            "sha256": sha256(parent_manifest),
        },
        "generator": {
            "path": Path(__file__).name,
            "sha256": sha256(Path(__file__)),
        },
        "documents": {},
        "current_source_dependencies": {},
        "historical_hash_authority": (
            "Historical execution hashes in saved per-analysis analysis_manifest.json "
            "files remain authoritative. Current source hashes below do not replace them."
        ),
        "evidence_limitation": (
            "The production output directories are not regenerated by this freeze. "
            "Replay claims remain finite-horizon facts inherited from the frozen lineage."
        ),
    }
    for row in rows:
        key = row["status"]
        manifest["claim_status_counts"][key] = (
            manifest["claim_status_counts"].get(key, 0) + 1
        )
    for filename in document_files:
        manifest["documents"][filename] = sha256(ROOT / filename)
    for filename in source_files:
        manifest["current_source_dependencies"][filename] = sha256(ROOT / filename)

    atomic_text(MANIFEST_PATH, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {len(rows)} claims to {CLAIM_PATH.name}")
    print(f"Wrote additive freeze manifest to {MANIFEST_PATH.name}")


if __name__ == "__main__":
    main()
