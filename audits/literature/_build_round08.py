#!/usr/bin/env python3
"""Build Round 8: extend the source -> claim mapping for the AUD-* claims.

This touches `bears_on_ids` and nothing else. That column is the living mapping
between a source and the claims it bears on; the frozen bibliographic record is
the snapshot JSON plus the CSV's identity fields. The builder asserts, before and
after, that every snapshot SHA-256 recorded in SOURCES.csv still matches the file
on disk and that no identity field changed. If a snapshot hash ever moves, this
script has done something it was not supposed to do and must fail.
"""

from __future__ import annotations

import csv
import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SNAP = ROOT / "snapshots"
SRC = ROOT / "SOURCES.csv"

# Claims are added to a source's bears_on_ids -- never removed.
EXTEND: dict[str, list[str]] = {
    # ---- adaptive / delay network cluster (L1) ----
    "LIT-0010": ["AUD-FROZEN-TOPO", "AUD-B-SCAFFOLD"],
    "LIT-0011": ["AUD-K3", "AUD-CYCLE-KERNEL"],
    "LIT-0018": ["AUD-B-SCAFFOLD"],
    "LIT-0028": ["AUD-DELAY"],
    "LIT-0035": ["AUD-DELAY", "AUD-TIMESTEP"],
    "LIT-0039": ["AUD-TOPO-OMEGA", "AUD-DELAY", "AUD-SCOPE-1.4"],
    "LIT-0040": ["AUD-CORR-0995", "AUD-TOPO-OMEGA", "AUD-CORR-0995-SCOPE"],
    # ---- normalisation / rate-law (L1 + L7) ----
    "LIT-0043": ["AUD-GATE", "AUD-RATELAW", "AUD-KAPPA-TW"],
    # ---- nonsmooth analysis (L7) ----
    "LIT-0006": ["AUD-SLOWPOLE"],
    "LIT-0008": ["AUD-SLOWPOLE"],
    "LIT-0009": ["AUD-SLOWPOLE", "AUD-TIES"],
    "LIT-0020": ["AUD-K3", "AUD-RATELAW", "AUD-CYCLE-KERNEL"],
    "LIT-0021": ["AUD-TIES"],
    "LIT-0022": ["AUD-SLOWPOLE", "AUD-TIES"],
    "LIT-0033": ["AUD-TIES"],
    # ---- reproducibility (L8) ----
    "LIT-0012": ["AUD-REPRO13", "AUD-REPRO-B2A95"],
    "LIT-0013": ["AUD-REPRO-B2A95"],
    "LIT-0014": ["AUD-V4-HELDEVENT", "AUD-REPRO13", "AUD-REPRO-B2A95",
                 "AUD-RATELAW", "AUD-TIMESTEP"],
    "LIT-0038": ["AUD-MODULAR-ORACLE", "AUD-REPRO13", "AUD-REPRO-B2A95"],
    # ---- causal inference (L2) ----
    "LIT-0002": ["AUD-SCOPE-1.4", "AUD-HELDOUT-LABEL"],
    "LIT-0023": ["AUD-HELDOUT-LABEL", "AUD-RESP1-UNIFORM"],
    "LIT-0024": ["AUD-HELDOUT-LABEL", "AUD-RESP1-UNIFORM"],
    # ---- DDE numerics (L3) ----
    "LIT-0029": ["AUD-TIMESTEP", "AUD-RATELAW"],
}

IDENTITY_FIELDS = ["source_id", "title", "authors", "year", "venue", "identifiers",
                   "canonical_url", "verification_level", "snapshot_sha256"]


def audit_snapshots(rows: list[dict], label: str) -> None:
    bad = []
    for r in rows:
        f = ROOT / r["snapshot_file"]
        if not f.exists():
            bad.append(f"{r['source_id']}: snapshot missing")
            continue
        actual = hashlib.sha256(f.read_bytes()).hexdigest()
        if actual != r["snapshot_sha256"]:
            bad.append(f"{r['source_id']}: snapshot sha256 drift")
    if bad:
        raise SystemExit(f"[{label}] snapshot integrity FAILED:\n  " + "\n  ".join(bad))
    print(f"[{label}] {len(rows)} snapshots verified, no drift")


def main() -> None:
    with SRC.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        cols = list(reader.fieldnames or [])
        rows = list(reader)

    audit_snapshots(rows, "pre")
    before = {r["source_id"]: {k: r[k] for k in IDENTITY_FIELDS} for r in rows}

    by_id = {r["source_id"]: r for r in rows}
    changed = 0
    for sid, new_claims in EXTEND.items():
        if sid not in by_id:
            raise SystemExit(f"unknown source {sid}")
        cur = [t.strip() for t in by_id[sid]["bears_on_ids"].split(";") if t.strip()]
        add = [c for c in new_claims if c not in cur]
        if not add:
            continue
        merged = sorted(set(cur) | set(add))
        by_id[sid]["bears_on_ids"] = ";".join(merged)
        changed += 1
        print(f"  {sid}: +{len(add)} -> {len(merged)} claims")

    with SRC.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in cols})

    # The identity fields must be untouched by a mapping extension.
    after = {r["source_id"]: {k: r[k] for k in IDENTITY_FIELDS} for r in rows}
    if before != after:
        drift = [s for s in before if before[s] != after[s]]
        raise SystemExit(f"identity fields changed for {drift}")
    print(f"extended {changed} sources; identity fields unchanged")

    audit_snapshots(rows, "post")

    claims = {r["claim_id"] for r in
              csv.DictReader((ROOT / "baseline" / "claims.csv").open(encoding="utf-8"))}
    tokens = {t.strip() for r in rows for t in r["bears_on_ids"].split(";") if t.strip()}
    aud = {c for c in tokens if c.startswith("AUD-")}
    print(f"claims reachable from sources: {len(tokens & claims)} / {len(claims)}")
    print(f"AUD-* claims now with >=1 source: {len(aud)} of 24")
    print("AUD-* without any source:", sorted(
        c for c in claims if c.startswith("AUD-") and c not in tokens))


if __name__ == "__main__":
    main()
