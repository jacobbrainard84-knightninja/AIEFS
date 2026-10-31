#!/usr/bin/env python3
"""Build Round 6: the repository's own prior art, which this inbox omitted.

Round 6 adds ONE source and opens FOUR leads, all of them things the repository
already cites. This is not a search round; it is a provenance repair round. The
finding is that five directly relevant prior-art references were sitting in
`AI Agent Audits/AIEFS_audit_response.md` (point 12) and `AIEFS_salvage.md` the
whole time, and the 38-source bibliography contains none of them.
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SNAP = ROOT / "snapshots"
RETRIEVED = "2026-10-31"

COLS = [
    "source_id", "round_added", "title", "authors", "year", "venue", "venue_type",
    "identifiers", "canonical_url", "retrieved_date", "retrieval_method",
    "verification_level", "snapshot_file", "snapshot_sha256", "relevance_domains",
    "bears_on_ids", "stance", "notes",
]

SOURCES = [
    {
        "source_id": "LIT-0039",
        "title": "Adaptive Dynamical Networks",
        "authors": "Berner, R.; Gross, T.; Kuehn, C.; Kurths, J.; Yanchuk, S.",
        "year": "2023",
        "venue": (
            "arXiv:2304.05652v1 [nlin.AO], submitted 12 April 2023; later published in "
            "Physics Reports 1031 (2023)"
        ),
        "venue_type": "preprint",
        "identifiers": "arXiv:2304.05652;DOI:10.48550/arXiv.2304.05652",
        "canonical_url": "https://arxiv.org/abs/2304.05652",
        "retrieval_method": "fetch_page",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L1",
        "bears_on_ids": "EMP-AIEF14-02;EMP-AIEF13-02;AUD-NOVELTY",
        "stance": "CONTEXT",
        "excerpt": (
            "arXiv:2304.05652 (nlin.AO), submitted 12 Apr 2023, 120 pages. "
            "'It is a fundamental challenge to understand how the function of a network is "
            "related to its structural organization. Adaptive dynamical networks represent a "
            "broad class of systems that can change their connectivity over time depending on "
            "their dynamical state. The most important feature of such systems is that their "
            "function depends on their structure and vice versa.'"
        ),
        "notes": (
            "THE REPOSITORY ALREADY HOLDS THIS PAPER AND THIS INBOX DID NOT.\n\n"
            "It is committed as `Papers/2804.05652v1.pdf` (3.5 MB, 120 pages) under an "
            "impossible arXiv identifier - arXiv month codes run 01-12, so '2804' cannot exist. "
            "`AI Agent Audits/licensing_inventory/INVENTORY.md` already records the correct ID and "
            "even says 'Filename typo: 2804 for 2304'. The audit's L7 flags it too. Nothing loads "
            "the file and no Markdown references it, so a grep for 'arXiv:' across the working "
            "tree returns nothing - which is exactly why five rounds missed it.\n\n"
            "Why it matters more than any source added in rounds 2-5: this is the field-defining "
            "review of the exact class of system AIEF is (adaptive networks whose connectivity "
            "evolves with their state), covering neuronal synaptic plasticity among its "
            "applications. `AUD-NOVELTY` in the integration registry says novelty is 'not "
            "established either way; the ingredients are prior art', with the caveat 'first-pass "
            "literature search only'. This is the survey that settles the framing half of that "
            "question, and the repository's own audit response (point 12) already cites it as "
            "Phys. Rep. 1031 (2023).\n\n"
            "VERIFIED_FULL: the arXiv abstract page was fetched and read directly. The Physics "
            "Reports journal version (vol. 1031) is cited by the repository but its DOI was NOT "
            "independently confirmed here, so the citable identifier is the arXiv one."
        ),
    },
]

NEW_LEADS = [
    {
        "lead_id": "LEAD-0008",
        "title_hint": "Self-organization in networks of phase oscillators with Hebbian coupling",
        "identifier_hint": "Phys. Rev. E 65, 041906 (2002); authors Seliger, Young & Tsimring",
        "url": "",
        "why_not_citable": (
            "Cited by the repository's own audit response (AIEFS_audit_response.md point 12) and "
            "by AIEFS_salvage.md as the closest prior art - 'essentially AIEF minus delay and cap'. "
            "The citation was read inside the repository, not verified against the publisher "
            "record. Not citable until the DOI and author list are confirmed."
        ),
        "next_action": "Verify PRE 65:041906 against the APS record; if confirmed, this is the single most important prior-art source for AUD-NOVELTY and EMP-AIEF13-02.",
    },
    {
        "lead_id": "LEAD-0009",
        "title_hint": "Delay-induced patterns / delay plus plasticity in adaptive oscillator networks",
        "identifier_hint": "Phys. Rev. E 89, 032906 (2014); authors Timms & English",
        "url": "",
        "why_not_citable": (
            "Repository-sourced citation (AIEFS_audit_response.md point 12) for the delay-plus-"
            "plasticity ingredient. Not independently verified."
        ),
        "next_action": "Verify against the APS record; check whether it covers state-dependent (not just constant) delay.",
    },
    {
        "lead_id": "LEAD-0010",
        "title_hint": "Conserved-coupling normalisation in adaptive networks",
        "identifier_hint": "Phys. Rev. E 83, 036206 (2011); authors Picallo & Riecke",
        "url": "",
        "why_not_citable": (
            "Repository-sourced citation (AIEFS_audit_response.md point 12) for the normalisation "
            "ingredient. Not independently verified. Directly relevant to CF01/CF02/CF03 and to "
            "AUD-GATE's claim that the capacity gate is a node-strength multiplicative normalisation."
        ),
        "next_action": "Verify against the APS record; compare its normalisation with the capacity gate s_i = min(1, c/(q_i+eps)).",
    },
    {
        "lead_id": "LEAD-0011",
        "title_hint": "Adding up the parts: multiplicative vs subtractive normalisation constraints in Hebbian learning",
        "identifier_hint": "Neural Computation 6:100 (1994); authors Miller & MacKay",
        "url": "",
        "why_not_citable": (
            "Repository-sourced citation (AIEFS_audit_response.md point 12, and AIEFS_salvage.md "
            "which says multiplicative normalisation 'is exactly what produces the k*eta/c rates'). "
            "Not independently verified. Bears directly on AUD-KAPPA-TW and AUD-RATELAW."
        ),
        "next_action": "Verify the Neural Computation record; if confirmed it anchors the closed-form rate law to a classical result rather than a local derivation.",
    },
]


def main() -> None:
    SNAP.mkdir(parents=True, exist_ok=True)

    with (ROOT / "SOURCES.csv").open(encoding="utf-8", newline="") as fh:
        all_rows = list(csv.DictReader(fh))
    existing = [r for r in all_rows if r["round_added"] != "6"]
    ids = {r["source_id"] for r in existing}

    new_rows = []
    for rec in SOURCES:
        assert rec["source_id"] not in ids, rec["source_id"]
        snap_name = f"{rec['source_id']}.json"
        snapshot = {
            "source_id": rec["source_id"],
            "retrieved": RETRIEVED,
            "retrieval_method": rec["retrieval_method"],
            "canonical_url": rec["canonical_url"],
            "verification_level": rec["verification_level"],
            "bibliographic_record": {
                "title": rec["title"],
                "authors": rec["authors"],
                "year": rec["year"],
                "venue": rec["venue"],
                "venue_type": rec["venue_type"],
                "identifiers": rec["identifiers"],
            },
            "verbatim_excerpt": rec["excerpt"],
            "excerpt_provenance": "arXiv abstract page, read directly",
        }
        blob = json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"
        (SNAP / snap_name).write_text(blob, encoding="utf-8")
        row = dict(rec)
        row.pop("excerpt")
        row["round_added"] = "6"
        row["retrieved_date"] = RETRIEVED
        row["snapshot_file"] = f"snapshots/{snap_name}"
        row["snapshot_sha256"] = hashlib.sha256(blob.encode("utf-8")).hexdigest()
        new_rows.append(row)

    rows = existing + new_rows
    with (ROOT / "SOURCES.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in COLS})
    print(f"added {len(new_rows)} source(s) -> total {len(rows)}")

    with (ROOT / "LEADS.csv").open(encoding="utf-8", newline="") as fh:
        leads = [r for r in csv.DictReader(fh) if r["lead_id"] not in {n["lead_id"] for n in NEW_LEADS}]
    for lead in NEW_LEADS:
        lead.setdefault("status", "OPEN")
        lead.setdefault("resolved_as", "")
        leads.append({k: lead.get(k, "") for k in ["lead_id", "status", "resolved_as",
                                                   "title_hint", "identifier_hint", "url",
                                                   "why_not_citable", "next_action"]})
    cols = ["lead_id", "status", "resolved_as", "title_hint", "identifier_hint",
            "url", "why_not_citable", "next_action"]
    with (ROOT / "LEADS.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in leads:
            w.writerow({k: r[k] for k in cols})
    print(f"leads: {len(leads)} total, {sum(1 for r in leads if r['status']=='OPEN')} open")


if __name__ == "__main__":
    main()
