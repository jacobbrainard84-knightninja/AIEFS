#!/usr/bin/env python3
"""Regenerate the evidence bundle for this inbox deposit.

Run from the repository root, with the chronicler scripts next to this file:

    python3 audit_inbox/2026-11-08_arena-chronicler_project-chronicler/scripts/make_evidence.py

Writes into ``../evidence/``:
  findings.txt        human-readable rule output (``check -v`` equivalent)
  findings.csv        one row per finding, stable ids, evidence and recommended action
  (raw snapshot is written to the system temp dir, never inside the repo, because it
   contains the full path universe and the checkout path)
  snapshot_summary.json  a curated, privacy-safe summary of that snapshot

A note on privacy: this repository treats home-directory paths as personal data
(PRIVACY_SCRUB_LIST.md P4), so the published summary redacts ``repo_root`` and drops the
full path universe. The raw snapshot is written next to this script and gitignored.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_PARENT = HERE  # contains the chronicler/ package


def _find_repo(start: Path) -> Path:
    """Walk up until we find the checkout, so this works wherever the deposit lands."""
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return start


REPO_ROOT = _find_repo(HERE)

sys.path.insert(0, str(PACKAGE_PARENT))
os.environ.setdefault("CHRONICLER_REPO", str(REPO_ROOT))
os.environ.setdefault("CHRONICLER_OFFLINE", "0")

from chronicler import checks, facts, util  # noqa: E402


def main() -> int:
    ref = sys.argv[1] if len(sys.argv) > 1 else None
    evidence = HERE.parent / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)

    snapshot = facts.collect(ref=ref, allow_network=True)
    findings = checks.run_checks(snapshot)

    # --- human readable -------------------------------------------------
    lines = [
        f"# chronicler check -v",
        f"ref: {snapshot['ref']} @ {(snapshot['ref_commit']['sha'] or '?')[:7]}",
        f"generated: {snapshot['generated_at']}",
        f"history reliable: {snapshot['history']['reliable']} "
        f"(shallow={snapshot['history']['shallow']}, commits={snapshot['history']['commits']})",
        "",
    ]
    if not findings:
        lines.append("no drift detected")
    for finding in findings:
        location = finding.doc + (f":{finding.line}" if finding.line else "")
        lines.append(f"[{finding.severity.upper():<8}] {finding.rule:<26} {location}")
        lines.append(f"           {finding.title}")
        lines.append(f"           {finding.detail}")
        for item in finding.evidence[:8]:
            lines.append(f"           - {item}")
        lines.append(f"           action: {finding.action}")
        lines.append("")
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    lines.append("summary: " + " · ".join(
        f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: checks.SEVERITY_ORDER.get(kv[0], 9))
    ))
    (evidence / "findings.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # --- machine readable ------------------------------------------------
    with (evidence / "findings.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "rule", "severity", "document", "line", "title",
                         "detail", "evidence", "recommended_action"])
        for finding in findings:
            writer.writerow([
                finding.id, finding.rule, finding.severity, finding.doc,
                finding.line or "", finding.title, finding.detail,
                " | ".join(finding.evidence), finding.action,
            ])

    # --- raw snapshot (gitignored) --------------------------------------
    raw_path = Path(tempfile.gettempdir()) / "chronicler_snapshot.json"
    util.write_json(raw_path, snapshot)
    print(f"raw snapshot (outside the repo, contains local paths): {raw_path}")

    # --- published summary ----------------------------------------------
    documents = []
    for doc in snapshot["documents"]:
        documents.append({
            "path": doc["path"],
            "ref": doc["ref"],
            "class": doc["class"],
            "present": doc["present"],
            "required": doc.get("required", True),
            "editable": doc.get("editable", True),
            "is_hash_pinned": doc.get("is_pinned", False),
            "declared_date": doc.get("declared_date"),
            "age_days": doc.get("age_days"),
            "last_commit": {
                "sha7": ((doc.get("commit") or {}).get("sha") or "")[:7],
                "date": (doc.get("commit") or {}).get("date"),
            },
            "watch_newest": doc.get("watch_newest"),
            "counts": {
                "cited_shas": len(doc.get("cited_shas") or []),
                "cited_paths": len(doc.get("cited_paths") or []),
                "branch_rows": len(doc.get("branch_rows") or []),
            },
        })

    vocabulary = snapshot.get("vocabulary") or {}
    summary = {
        "generated_at": snapshot["generated_at"],
        "repo_root": "<repo> (redacted: PRIVACY_SCRUB_LIST.md P4)",
        "ref": snapshot["ref"],
        "ref_commit": snapshot["ref_commit"],
        "history": snapshot["history"],
        "remote": {
            "ok": snapshot["remote"]["ok"],
            "error": snapshot["remote"]["error"],
            "branch_count": len(snapshot["remote"]["heads"]),
            "main": snapshot["remote"]["heads"].get("main"),
        },
        "counts": {
            "tracked_files": snapshot["counts"]["tracked_files"],
            "tracked_bytes": snapshot["counts"]["tracked_bytes"],
            "by_extension_top10": dict(list(snapshot["counts"]["by_extension"].items())[:10]),
        },
        "pins": {
            "total": snapshot["pin_summary"]["total"],
            "present": snapshot["pin_summary"]["present"],
            "matching": snapshot["pin_summary"]["matching"],
            "mismatched": snapshot["pin_summary"]["mismatched"],
            "missing": snapshot["pin_summary"]["missing"],
            "sources": ["AI Agent Audits/evidence/audit_manifest.json",
                        "twindow_frozen_authority_hashes.txt",
                        "lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt"],
        },
        "vocabulary": {
            "values": vocabulary.get("values", []),
            "value_count": len(vocabulary.get("values", [])),
            "claims_rows": (vocabulary.get("claims_values") or {}).get("rows"),
            "artifact_status_used": [
                item["value"] for item in (vocabulary.get("claims_values") or {}).get("artifact_status", [])
            ],
            "audited_status_used": [
                item["value"] for item in (vocabulary.get("claims_values") or {}).get("audited_status", [])
            ],
            "unknown_vs_vocabulary": [],
        },
        "documents": documents,
        "findings_summary": counts,
    }
    allowed = set(summary["vocabulary"]["values"])
    summary["vocabulary"]["unknown_vs_vocabulary"] = sorted(
        {v for v in summary["vocabulary"]["artifact_status_used"] + summary["vocabulary"]["audited_status_used"]
         if v not in allowed}
    )
    util.write_json(evidence / "snapshot_summary.json", summary)

    print(f"wrote evidence to {evidence}")
    print(f"findings: {len(findings)} ({', '.join(f'{k} {v}' for k, v in sorted(counts.items()))})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
