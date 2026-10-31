#!/usr/bin/env python3
"""Verify the literature inbox. Stdlib only. Exit 0 = every gate passed.

Gates
-----
[1/8] SOURCES.csv schema     exact header, no duplicates, IDs match LIT-\\d{4},
                             IDs dense and ordered, required fields non-empty.
[2/8] Controlled vocabulary  verification_level / stance / venue_type /
                             relevance_domains all in the documented sets.
[3/8] Snapshot integrity     every source has snapshots/<id>.json whose SHA-256
                             equals the snapshot_sha256 recorded in SOURCES.csv,
                             and whose embedded bibliographic record agrees with
                             the CSV row (title/authors/year).
[4/8] Registry linkage       every token in bears_on_ids resolves to a real
                             claim in registry/claims.csv or a study in
                             registry/studies.csv. A citation may not be attached
                             to a nonexistent claim.
[5/8] Findings coverage      every [LIT-xxxx] token in ROUND_*_FINDINGS.md
                             exists in SOURCES.csv; every source with
                             round_added=N is cited at least once in
                             ROUND_0N_FINDINGS.md (no orphan bibliography).
[6/8] Leads quarantine       no LEAD-xxxx is cited as if it were a source, and
                             every lead has a next_action.
[7/8] State consistency      ROUND_STATE.json parses, next_round == completed+1,
                             and its per-round source counts match SOURCES.csv.
[8/8] Adjudication           ADJUDICATION.csv covers exactly the claims that
                             carry at least one source, cites only sources that
                             map back to that claim, uses closed vocabularies,
                             and agrees with registry/claims.csv on status.

Usage
-----
    python audits/literature/verify_literature.py
    python audits/literature/verify_literature.py --quiet
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent

ADJ_COLS = [
    "claim_id", "study_id", "registry_status", "claim_class", "literature_role",
    "sources", "n_sources", "verdict", "mapping_health", "verdict_basis",
    "producing_code", "required_change", "severity",
]

EXPECTED_COLS = [
    "source_id",
    "round_added",
    "title",
    "authors",
    "year",
    "venue",
    "venue_type",
    "identifiers",
    "canonical_url",
    "retrieved_date",
    "retrieval_method",
    "verification_level",
    "snapshot_file",
    "snapshot_sha256",
    "relevance_domains",
    "bears_on_ids",
    "stance",
    "notes",
]

VERIFICATION_LEVELS = {"VERIFIED_FULL", "VERIFIED_METADATA"}
RETRIEVAL_METHODS = {"fetch_page", "web_search"}
STANCES = {"SUPPORTS", "CONTRADICTS", "CAUTION", "METHOD", "CONTEXT"}
VENUE_TYPES = {"journal", "conference", "book", "preprint", "standard", "dataset", "thesis"}
DOMAINS = {"L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"}

failures: list[str] = []
warnings: list[str] = []


def fail(gate: str, msg: str) -> None:
    failures.append(f"[{gate}] {msg}")


def warn(gate: str, msg: str) -> None:
    warnings.append(f"[{gate}] {msg}")


def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def load_registry_ids() -> set[str]:
    ids: set[str] = set()
    claims = REPO / "registry" / "claims.csv"
    studies = REPO / "registry" / "studies.csv"
    if claims.exists():
        with claims.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                if row.get("claim_id"):
                    ids.add(row["claim_id"].strip())
    if studies.exists():
        with studies.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                if row.get("study_id"):
                    ids.add(row["study_id"].strip())
    return ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    # ---------------------------------------------------------------- [1/8]
    gate = "1/8 schema"
    src_path = HERE / "SOURCES.csv"
    if not src_path.exists():
        fail(gate, "SOURCES.csv missing")
        return report(args)

    with src_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        rows = list(reader)

    if header != EXPECTED_COLS:
        fail(gate, f"header mismatch\n  expected {EXPECTED_COLS}\n  found    {header}")

    seen: set[str] = set()
    for i, row in enumerate(rows, start=2):
        sid = row.get("source_id", "")
        if not re.fullmatch(r"LIT-\d{4}", sid):
            fail(gate, f"line {i}: bad source_id {sid!r}")
        if sid in seen:
            fail(gate, f"line {i}: duplicate source_id {sid}")
        seen.add(sid)

    expected_ids = [f"LIT-{n:04d}" for n in range(1, len(rows) + 1)]
    if [r["source_id"] for r in rows] != expected_ids:
        fail(gate, (
            "source_id set is not dense/ordered from LIT-0001; "
            f"found {rows[0]['source_id']}..{rows[-1]['source_id']} ({len(rows)} rows). "
            "IDs are append-only and must never be renumbered or reused."
        ))

    required = ["title", "authors", "year", "venue", "venue_type", "canonical_url",
                "retrieved_date", "retrieval_method", "verification_level",
                "snapshot_file", "snapshot_sha256", "relevance_domains",
                "bears_on_ids", "stance", "notes"]
    for row in rows:
        for key in required:
            if not str(row.get(key, "")).strip():
                fail(gate, f"{row.get('source_id')}: empty required field {key!r}")

    # ---------------------------------------------------------------- [2/8]
    gate = "2/8 vocabulary"
    for row in rows:
        sid = row["source_id"]
        if row["verification_level"] not in VERIFICATION_LEVELS:
            fail(gate, f"{sid}: verification_level {row['verification_level']!r} not citable")
        if row["retrieval_method"] not in RETRIEVAL_METHODS:
            fail(gate, f"{sid}: retrieval_method {row['retrieval_method']!r} unknown")
        if row["stance"] not in STANCES:
            fail(gate, f"{sid}: stance {row['stance']!r} not in {sorted(STANCES)}")
        if row["venue_type"] not in VENUE_TYPES:
            fail(gate, f"{sid}: venue_type {row['venue_type']!r} not in {sorted(VENUE_TYPES)}")
        for d in filter(None, (x.strip() for x in row["relevance_domains"].split(";"))):
            if d not in DOMAINS:
                fail(gate, f"{sid}: relevance domain {d!r} not in {sorted(DOMAINS)}")
        if not row["canonical_url"].startswith("https://"):
            fail(gate, f"{sid}: canonical_url must be https")

    # ---------------------------------------------------------------- [3/8]
    gate = "3/8 snapshots"
    for row in rows:
        sid = row["source_id"]
        rel = row["snapshot_file"]
        path = HERE / rel
        if not path.exists():
            fail(gate, f"{sid}: snapshot {rel} missing")
            continue
        actual = sha256_file(path)
        if actual != row["snapshot_sha256"]:
            fail(gate, f"{sid}: snapshot sha256 mismatch\n  csv  {row['snapshot_sha256']}\n  file {actual}")
        try:
            snap = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(gate, f"{sid}: snapshot is not valid JSON ({exc})")
            continue
        bib = snap.get("bibliographic_record", {})
        for field in ("title", "authors", "year"):
            if bib.get(field, "").strip() != row[field].strip():
                fail(gate, f"{sid}: snapshot {field} disagrees with CSV")
        if not snap.get("verbatim_excerpt", "").strip():
            fail(gate, f"{sid}: snapshot carries no verbatim excerpt")

    # ---------------------------------------------------------------- [4/8]
    gate = "4/8 registry linkage"
    claims_path = REPO / "registry" / "claims.csv"
    studies_path = REPO / "registry" / "studies.csv"
    for p in (claims_path, studies_path):
        if not p.exists():
            # Hard failure, not a warning: a silent skip would let the strongest
            # structural gate be bypassed simply by running from the wrong directory.
            fail(gate, f"{p} not found — cannot check bears_on_ids. "
                       "Gate 4 must never degrade to a no-op.")
    registry_ids = load_registry_ids()
    if not registry_ids:
        fail(gate, "registry yielded no claim/study IDs; linkage would be vacuous")
    if registry_ids:  # already failed above if empty; avoid a useless 45-line cascade
        for row in rows:
            for token in filter(None, (t.strip() for t in row["bears_on_ids"].split(";"))):
                if token not in registry_ids:
                    fail(gate, f"{row['source_id']}: bears_on {token!r} is not in the claim/study registry")

    # ---------------------------------------------------------------- [5/8]
    gate = "5/8 findings coverage"
    cited: dict[str, set[str]] = {}
    for md in sorted(HERE.glob("ROUND_*_FINDINGS.md")):
        text = md.read_text(encoding="utf-8")
        toks = set(re.findall(r"\[(LIT-\d{4})\]", text))
        cited[md.name] = toks
        for t in sorted(toks):
            if t not in seen:
                fail(gate, f"{md.name}: cites {t} which is not in SOURCES.csv")
        match = re.search(r"ROUND_(\d+)_FINDINGS", md.name)
        if not match:
            continue
        rnd = str(int(match.group(1)))
        expected = {r["source_id"] for r in rows if r["round_added"] == rnd}
        missing = expected - toks
        if missing:
            fail(gate, f"{md.name}: sources added in round {rnd} never cited: {sorted(missing)}")
        extra = {t for t in toks if t in seen} - expected
        if extra:
            warn(gate, f"{md.name}: cites sources from other rounds: {sorted(extra)}")

    if not cited:
        warn(gate, "no ROUND_*_FINDINGS.md present")

    # ---------------------------------------------------------------- [6/8]
    gate = "6/8 leads"
    leads_path = HERE / "LEADS.csv"
    lead_ids: set[str] = set()
    if leads_path.exists():
        with leads_path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                lid = (row.get("lead_id") or "").strip()
                if not re.fullmatch(r"LEAD-\d{4}", lid):
                    fail(gate, f"bad lead_id {lid!r}")
                if not (row.get("next_action") or "").strip():
                    fail(gate, f"{lid}: empty next_action")
                status = (row.get("status") or "").strip()
                if status not in {"OPEN", "RESOLVED"}:
                    fail(gate, f"{lid}: status {status!r} not in {{OPEN, RESOLVED}}")
                resolved = (row.get("resolved_as") or "").strip()
                if status == "RESOLVED":
                    if not resolved:
                        fail(gate, f"{lid}: RESOLVED but no resolved_as pointer")
                    elif resolved not in seen:
                        fail(gate, f"{lid}: resolved_as {resolved!r} is not a source in SOURCES.csv")
                elif resolved:
                    fail(gate, f"{lid}: OPEN lead must not carry resolved_as {resolved!r}")
                lead_ids.add(lid)
    all_text = "\n".join(p.read_text(encoding="utf-8") for p in HERE.glob("*.md"))
    for lid in lead_ids:
        if re.search(rf"\[{lid}\]", all_text):
            fail(gate, f"{lid} is cited as a source but lives in LEADS.csv (not citable)")
    for lid in lead_ids:
        if lid not in all_text:
            warn(gate, f"{lid} never mentioned in any findings file")

    # ---------------------------------------------------------------- [7/8]
    gate = "7/8 state"
    state_path = HERE / "ROUND_STATE.json"
    if not state_path.exists():
        fail(gate, "ROUND_STATE.json missing")
    else:
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(gate, f"ROUND_STATE.json invalid ({exc})")
            state = {}
        if state:
            done = state.get("last_round_completed")
            nxt = state.get("next_round")
            if not isinstance(done, int) or not isinstance(nxt, int):
                fail(gate, "last_round_completed and next_round must be integers")
            elif nxt != done + 1:
                fail(gate, f"next_round {nxt} != last_round_completed {done} + 1")
            per_round: dict[str, int] = {}
            for row in rows:
                per_round[row["round_added"]] = per_round.get(row["round_added"], 0) + 1
            declared = state.get("sources_per_round", {})
            for rnd, cnt in per_round.items():
                if str(rnd) in declared and declared[str(rnd)] != cnt:
                    fail(gate, f"round {rnd}: state says {declared[str(rnd)]} sources, CSV has {cnt}")
            for rnd in declared:
                if rnd not in per_round:
                    fail(gate, f"state declares round {rnd} but CSV has no such sources")
            total = state.get("total_sources")
            if isinstance(total, int) and total != len(rows):
                fail(gate, f"state total_sources {total} != CSV rows {len(rows)}")

    # ---------------------------------------------------------------- [8/8]
    gate = "8/8 adjudication"
    adj_path = HERE / "ADJUDICATION.csv"
    if not (claims_path.exists() and studies_path.exists()):
        # Same fail-closed rule as gate 4: without the registry the coverage
        # comparison is meaningless, and a silent skip would hide that.
        fail(gate, "registry missing — adjudication coverage cannot be checked")
    elif not adj_path.exists():
        fail(gate, "ADJUDICATION.csv missing; the round-5 deliverable is absent")
    else:
        ADJ_VERDICTS = {
            "SUPPORTED", "SUPPORTED_WITH_SCOPE", "BOUNDED", "CONTEXT_ONLY",
            "VALIDATED_RETIREMENT", "VALIDATED_REJECTION",
        }
        ADJ_MAPPING = {"COMPLETE", "INCOMPLETE", "WRONG"}
        ADJ_SEVERITY = {"NONE", "LOW", "MEDIUM", "HIGH"}
        ADJ_CLASS = {"EMPIRICAL", "FORMAL", "IMPLEMENTATION", "REJECTION", "RETIRED"}
        ADJ_ROLE = {
            "DESIGN", "INFERENCE", "INTERPRETATION", "FORMALIZATION",
            "METHOD_VALIDITY", "SCOPE_ONLY",
        }
        ADJ_CODE = {"PRESENT", "RELOCATED", "UNRESOLVED", "NOT_APPLICABLE"}

        with adj_path.open(encoding="utf-8", newline="") as fh:
            adj_rows = list(csv.DictReader(fh))
        adj_header = list(adj_rows[0].keys()) if adj_rows else []
        if adj_header and adj_header != ADJ_COLS:
            fail(gate, f"ADJUDICATION.csv header mismatch: {adj_header}")

        # Every claim carrying at least one source must be adjudicated, and
        # nothing else may appear. Both directions: a table that quietly drops a
        # claim is worse than no table at all.
        claim_ids: set[str] = set()
        if claims_path.exists():
            with claims_path.open(encoding="utf-8", newline="") as fh:
                claim_ids = {c["claim_id"].strip() for c in csv.DictReader(fh) if c.get("claim_id")}
        claim_sources: dict[str, set[str]] = {}      # claim -> sources citing it
        source_claims: dict[str, set[str]] = {}      # source -> claims it cites
        for row in rows:
            for token in filter(None, (t.strip() for t in row["bears_on_ids"].split(";"))):
                if token in claim_ids:
                    claim_sources.setdefault(token, set()).add(row["source_id"])
                    source_claims.setdefault(row["source_id"], set()).add(token)
        all_source_ids = {row["source_id"] for row in rows}
        covered = [r.get("claim_id", "") for r in adj_rows]
        if len(covered) != len(set(covered)):
            fail(gate, "duplicate claim_id in ADJUDICATION.csv")
        missing = set(claim_sources) - set(covered)
        if missing:
            fail(gate, f"claims with sources but no adjudication: {sorted(missing)}")
        extra = set(covered) - set(claim_sources)
        if extra:
            fail(gate, f"adjudicated claims that carry no source mapping: {sorted(extra)}")

        reg_status: dict[str, str] = {}
        if claims_path.exists():
            with claims_path.open(encoding="utf-8", newline="") as fh:
                reg_status = {
                    c["claim_id"]: c["artifact_status"]
                    for c in csv.DictReader(fh)
                    if c.get("claim_id")
                }

        for r in adj_rows:
            cid = r.get("claim_id", "?")
            for field, allowed in (
                ("verdict", ADJ_VERDICTS),
                ("mapping_health", ADJ_MAPPING),
                ("severity", ADJ_SEVERITY),
                ("claim_class", ADJ_CLASS),
                ("literature_role", ADJ_ROLE),
                ("producing_code", ADJ_CODE),
            ):
                if r.get(field) not in allowed:
                    fail(gate, f"{cid}: {field} {r.get(field)!r} not in vocabulary")
            for field in ("verdict_basis", "required_change"):
                if not (r.get(field) or "").strip():
                    fail(gate, f"{cid}: empty {field}")
            if r.get("mapping_health") in {"INCOMPLETE", "WRONG"} and \
                    (r.get("required_change") or "").strip().lower() in {"", "none"}:
                fail(gate, f"{cid}: mapping_health={r.get('mapping_health')} "
                           f"but required_change is 'none'")

            cited = [s.strip() for s in (r.get("sources") or "").split(";") if s.strip()]
            if (r.get("n_sources") or "").strip() != str(len(cited)):
                fail(gate, f"{cid}: n_sources {r.get('n_sources')!r} != {len(cited)} cited")
            for sid in cited:
                if sid not in all_source_ids:
                    fail(gate, f"{cid}: cites {sid} which is not in SOURCES.csv")
                elif cid not in source_claims.get(sid, set()):
                    fail(gate, f"{cid}: cites {sid}, but {sid} does not list {cid} in bears_on_ids")
            for sid in sorted(claim_sources.get(cid, set())):
                if sid not in cited:
                    fail(gate, f"{cid}: omits mapped source {sid}")

            if cid in reg_status and r.get("registry_status") != reg_status[cid]:
                fail(gate, f"{cid}: registry_status {r.get('registry_status')!r} "
                           f"!= registry {reg_status[cid]!r}")

    return report(args)


def report(args) -> int:
    if failures:
        print("LITERATURE INBOX: FAIL")
        for f in failures:
            print("  " + f)
        if warnings:
            print("WARNINGS")
            for w in warnings:
                print("  " + w)
        return 1
    if not args.quiet:
        print("LITERATURE INBOX: PASS (8/8 gates)")
        for w in warnings:
            print("  warning: " + w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
