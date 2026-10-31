#!/usr/bin/env python3
"""Build Round 4: append 5 sources, resolve LEAD-0007.

Round 4 makes NO edits to any existing snapshot. LIT-0030's content description
was found to be narrower than Round 3 implied; per protocol the snapshot is
immutable, so the correction is recorded in ROUND_04_FINDINGS.md (F24) rather
than by rewriting the row. That is deliberate.
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SNAP = ROOT / "snapshots"
RETRIEVED = "2026-10-30"

COLS = [
    "source_id", "round_added", "title", "authors", "year", "venue", "venue_type",
    "identifiers", "canonical_url", "retrieved_date", "retrieval_method",
    "verification_level", "snapshot_file", "snapshot_sha256", "relevance_domains",
    "bears_on_ids", "stance", "notes",
]

SOURCES = [
    {
        "source_id": "LIT-0034",
        "title": "The Lean 4 Theorem Prover and Programming Language",
        "authors": "de Moura, L.; Ullrich, S.",
        "year": "2021",
        "venue": (
            "Automated Deduction - CADE 28 (CADE 2021), Lecture Notes in Computer Science "
            "vol. 12699, Springer, pp. 625-635"
        ),
        "venue_type": "conference",
        "identifiers": "DOI:10.1007/978-3-030-79876-5_37;ISBN:978-3-030-79876-5",
        "canonical_url": "https://doi.org/10.1007/978-3-030-79876-5_37",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L6",
        "bears_on_ids": "LEAN-CF-01;AIEF_1_4_LEAN_CONTROLLER_FIBER",
        "stance": "METHOD",
        "excerpt": (
            "CADE 28, LNCS 12699, pp. 625-635, open access, first online 5 July 2021. "
            "'Lean 4 is also an efficient functional programming language based on a novel "
            "programming paradigm called functional but in-place. Efficient code generation is "
            "crucial for Lean users because many write custom proof automation procedures in Lean "
            "itself.'"
        ),
        "notes": (
            "The system reference for the toolchain the project's Lean CI actually uses. Included "
            "because the repository pins a Lean toolchain and runs lean-action in CI but cites no "
            "Lean reference at all, so a reader cannot tell which Lean the proofs target. This is "
            "the citation that answers 'Lean 4, per CADE 2021'. It does not bear on the "
            "mathematical content of LEAN-CF-01; it anchors the platform."
        ),
    },
    {
        "source_id": "LIT-0035",
        "title": (
            "Recent trends in the numerical solution of retarded functional differential equations"
        ),
        "authors": "Bellen, A.; Maset, S.; Zennaro, M.; Guglielmi, N.",
        "year": "2009",
        "venue": "Acta Numerica",
        "venue_type": "journal",
        "identifiers": "DOI:10.1017/S0962492906390010",
        "canonical_url": "https://doi.org/10.1017/S0962492906390010",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L3",
        "bears_on_ids": "AIEF_1_4_SPLIT_STATE_ABLATION;S03",
        "stance": "CAUTION",
        "excerpt": (
            "Acta Numerica 18:1-110, May 2009. 'Retarded functional differential equations (RFDEs) "
            "form a wide class of evolution equations which share the property that, at any point, "
            "the rate of the solution depends on... values attained by the solution itself in the "
            "past. Thus the initial problem for RFDEs is an infinite-dimensional problem... "
            "numerically solving initial problems for RFDEs is a difficult task that cannot be "
            "founded on the mere adaptation of well-known methods for ordinary, partial or "
            "integro-differential equations... some critical situations have been recently "
            "investigated in connection to specific classes of equations, such as the accurate "
            "location of discontinuity points...'"
        ),
        "notes": (
            "Resolves LEAD-0007, and corrects my own assumption: the author order is Bellen, "
            "Maset, Zennaro, Guglielmi - not the order I recorded in the lead.\n\n"
            "This supersedes LIT-0029 as the citation of record for DDE numerics. Two things it "
            "adds. (1) 'Accurate location of discontinuity points' is named as a critical issue in "
            "its own right, which independently confirms Round 3's F19: the split-state ablation "
            "injects a discontinuity into the history and must locate it. (2) The explicit claim "
            "that DDE integration 'cannot be founded on the mere adaptation of well-known methods' "
            "means a scheme validated for the ODE subsystems is not automatically valid for the "
            "delayed system - relevant if the AIEF platform's Euler step is justified by its ODE "
            "behaviour alone. It also states it does NOT treat stability, deferring to LIT-0029."
        ),
    },
    {
        "source_id": "LIT-0036",
        "title": "The Lean Mathematical Library",
        "authors": "The mathlib Community",
        "year": "2020",
        "venue": (
            "Proceedings of the 9th ACM SIGPLAN International Conference on Certified Programs "
            "and Proofs (CPP 2020), ACM"
        ),
        "venue_type": "conference",
        "identifiers": "DOI:10.1145/3372885.3373824",
        "canonical_url": "https://doi.org/10.1145/3372885.3373824",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L6",
        "bears_on_ids": "LEAN-CF-01;AIEF_1_4_LEAN_CONTROLLER_FIBER",
        "stance": "METHOD",
        "excerpt": (
            "CPP 2020, ACM. 'This paper describes mathlib, a community-driven effort to build a "
            "unified library of mathematics formalized in the Lean proof assistant. Among proof "
            "assistant libraries, it is distinguished by its dependently typed foundations, focus "
            "on classical mathematics, extensive hierarchy of structures, use of large- and "
            "small-scale automation, and distributed organization.'"
        ),
        "notes": (
            "The library the project builds against, cited once so the dependency is visible. "
            "Bears on the Round 1 F4 proposal (generalize LEAN-CF-01 to the rank-incidence "
            "theorem): mathlib's stated design goal is to serve as a basis for research-level "
            "mathematics with an extensive hierarchy of structures, which is precisely the "
            "infrastructure a general rank result needs and a one-off kernel computation does not. "
            "Note this is the Lean 3 era paper; the Lean 4 port was in progress at publication "
            "(see LIT-0034). Cite it for the library's scope, not its current module layout."
        ),
    },
    {
        "source_id": "LIT-0037",
        "title": "Engel's Theorem in Mathlib",
        "authors": "Nash, O.",
        "year": "2023",
        "venue": "Journal of Automated Reasoning",
        "venue_type": "journal",
        "identifiers": "DOI:10.1007/s10817-023-09668-0",
        "canonical_url": "https://doi.org/10.1007/s10817-023-09668-0",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L6",
        "bears_on_ids": "LEAN-CF-01;AIEF_1_4_LEAN_CONTROLLER_FIBER",
        "stance": "METHOD",
        "excerpt": (
            "Journal of Automated Reasoning 67, Article 18 (2023), open access, published 13 May "
            "2023. 'Using nilpotency as the theme, we outline a computer formalisation of Engel's "
            "theorem and an application to root space theory. We emphasise that all arguments work "
            "with coefficients in any commutative ring. ... Mathlib's version of Engel's theorem "
            "unifies the various versions of this result appearing in the informal literature, "
            "while demanding weaker hypotheses and providing a stronger result.'"
        ),
        "notes": (
            "The model paper for what Round 1 F4 proposed, and the strongest single result of "
            "Round 4. Engel's theorem is the closest structural analogue to the project's Lean "
            "situation: a classical linear-algebra result whose informal literature has several "
            "variants, formalized once at full generality so that all variants follow.\n\n"
            "The transferable lesson is stated by the author directly - a good formalization "
            "demands weaker hypotheses and provides a stronger result than the textbook version. "
            "LEAN-CF-01 does the opposite: it fixes C_{2,7} and computes one kernel, so it "
            "demonstrates the kernel but inherits none of the generality. Nash's paper shows the "
            "target state: state the rank-incidence theorem over an arbitrary commutative ring "
            "with no connectivity assumption beyond what is needed, and let the K3 case drop out "
            "as a corollary. Cite this whenever the Lean work is described, as the standard to "
            "which it should be held."
        ),
    },
    {
        "source_id": "LIT-0038",
        "title": "Artifact Review and Badging - Current (Version 1.1)",
        "authors": "Association for Computing Machinery",
        "year": "2020",
        "venue": "ACM Publications Policies",
        "venue_type": "standard",
        "identifiers": "URL:https://www.acm.org/publications/policies/artifact-review-and-badging-current",
        "canonical_url": "https://www.acm.org/publications/policies/artifact-review-and-badging-current",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L8",
        "bears_on_ids": "IMPL-MODULAR-01;PLATFORM_V1_V4",
        "stance": "METHOD",
        "excerpt": (
            "Version 1.1, 24 August 2020. 'An experimental result is not fully established unless "
            "it can be independently reproduced. ... In each case, exact replication or "
            "reproduction of results is not required, or even expected. Instead, the results must "
            "be in agreement to within a tolerance deemed acceptable for experiments of the given "
            "type. In particular, differences in the results should not change the main claims "
            "made in the paper.'"
        ),
        "notes": (
            "Settles the Stage 7 CI design question that has been open since Round 1 F5, and adds "
            "a requirement the repository does not currently meet.\n\n"
            "(1) The two-tier tolerance gate is sanctioned by the standard, not a concession: "
            "'within a tolerance deemed acceptable' and 'exact... not required, or even expected'. "
            "A 0-ULP gate on everything would be stricter than the field's own definition of "
            "reproduced.\n\n"
            "(2) The 'Artifacts Available' badge requires artifacts 'placed on a publicly "
            "accessible, archival repository with a DOI / persistent identifier', and community "
            "practice (USENIX-family, per the SIGIR implementation guidance) rejects a bare GitHub "
            "or personal URL as archival. The AIEF repository is a GitHub repository with no DOI "
            "and no release tag. So even at its best this artifact set would not qualify for "
            "Artifacts Available as published - a concrete, cheap gap (a Zenodo DOI per frozen "
            "run directory would close it).\n\n"
            "(3) Terminology trap worth recording: ACM swapped 'reproduced' and 'replicated' "
            "between v1.0 and v1.1 (May 2020). Any older paper citing these badges may use the "
            "inverted sense; check the badge era."
        ),
    },
]

LEAD_RESOLUTIONS = {
    "LEAD-0007": ("RESOLVED", "LIT-0035"),
}

NEW_LEADS: list[dict] = []


def main() -> None:
    SNAP.mkdir(parents=True, exist_ok=True)

    with (ROOT / "SOURCES.csv").open(encoding="utf-8", newline="") as fh:
        all_rows_in = list(csv.DictReader(fh))
    existing = [r for r in all_rows_in if r["round_added"] != "4"]
    existing_ids = {r["source_id"] for r in existing}
    print(f"existing rounds: {len(existing)} rows, up to {sorted(existing_ids)[-1]}")

    new_rows = []
    for rec in SOURCES:
        assert rec["source_id"] not in existing_ids, f"ID collision on {rec['source_id']}"
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
            "excerpt_provenance": (
                "canonical landing page, read directly"
                if rec["retrieval_method"] == "fetch_page"
                else "search-index rendering of the publisher/canonical page"
            ),
        }
        blob = json.dumps(snapshot, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
        (SNAP / snap_name).write_text(blob, encoding="utf-8")
        digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()

        row = dict(rec)
        row.pop("excerpt")
        row["round_added"] = "4"
        row["retrieved_date"] = RETRIEVED
        row["snapshot_file"] = f"snapshots/{snap_name}"
        row["snapshot_sha256"] = digest
        new_rows.append(row)

    all_rows = existing + new_rows
    with (ROOT / "SOURCES.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in all_rows:
            w.writerow({k: r[k] for k in COLS})
    print(f"appended {len(new_rows)} sources -> total {len(all_rows)}")

    with (ROOT / "LEADS.csv").open(encoding="utf-8", newline="") as fh:
        leads = [
            r for r in csv.DictReader(fh)
            if r["lead_id"] not in {n["lead_id"] for n in NEW_LEADS}
        ]
    for lead in leads:
        lid = lead["lead_id"]
        if lid in LEAD_RESOLUTIONS:
            status, resolved = LEAD_RESOLUTIONS[lid]
            note = lead.get("next_action", "")
            if not note.startswith("done:"):
                lead["next_action"] = f"done: promoted to {resolved}. original: {note}"
            lead["status"], lead["resolved_as"] = status, resolved
    leads.extend(NEW_LEADS)

    lead_cols = [
        "lead_id", "status", "resolved_as", "title_hint", "identifier_hint", "url",
        "why_not_citable", "next_action",
    ]
    with (ROOT / "LEADS.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=lead_cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in leads:
            w.writerow(r)
    print(f"leads: {len(leads)} total, {sum(1 for r in leads if r['status']=='OPEN')} open")


if __name__ == "__main__":
    main()
