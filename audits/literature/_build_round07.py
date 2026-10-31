#!/usr/bin/env python3
"""Build Round 7: verify the four prior-art leads and re-baseline.

Every one of the four lead titles I wrote in Round 6 was WRONG. They were
paraphrases of how the repository described the papers, not bibliographic
records. Verification against the publisher records corrected all four, which
is the entire argument for the leads-not-sources rule.
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
        "source_id": "LIT-0040",
        "title": "Plasticity and learning in a network of coupled phase oscillators",
        "authors": "Seliger, P.; Young, S. C.; Tsimring, L. S.",
        "year": "2002",
        "venue": "Physical Review E 65, 041906",
        "venue_type": "journal",
        "identifiers": "DOI:10.1103/PhysRevE.65.041906",
        "canonical_url": "https://doi.org/10.1103/PhysRevE.65.041906",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L1",
        "bears_on_ids": "EMP-AIEF13-02;AUD-NOVELTY",
        "stance": "CAUTION",
        "excerpt": (
            "Phys. Rev. E 65, 041906, published 26 March 2002. 'A generalized Kuramoto model of "
            "coupled phase oscillators with a slow varying coupling matrix is studied. The "
            "dynamics of the coupling coefficients is driven by the phase difference of pairs of "
            "oscillators in such a way that the coupling strengthens for synchronized oscillators "
            "and weakens for nonsynchronized pairs. The system possesses a family of stable "
            "solutions corresponding to synchronized clusters of different sizes. A particular "
            "cluster can be formed by applying external driving at a given frequency to a group "
            "of oscillators. Once established, the synchronized state is robust against noise and "
            "small variations in natural frequencies.'"
        ),
        "notes": (
            "TITLE CORRECTION: my round-6 lead called this 'Self-organization in networks of phase "
            "oscillators with Hebbian coupling'. That is not the title. The real one is above; the "
            "paraphrase came from the repository's description, not a bibliographic record. This is "
            "precisely why a citation found inside an audit document is a lead and not a source.\n\n"
            "THE CLOSEST PRIOR ART IN THE RECORD. `AIEFS_salvage.md` says of this paper: "
            "'essentially AIEF minus delay and cap.' The abstract bears that out - a Kuramoto model "
            "with a slowly varying coupling matrix driven by phase differences, strengthening "
            "synchronised pairs and weakening others, with a family of stable cluster solutions "
            "selectable by external driving and robust to noise and frequency variation.\n\n"
            "Stance is CAUTION rather than SUPPORTS because its function here is to constrain the "
            "novelty claim, not to support an AIEF result. What it does NOT contain is the delay "
            "and the capacity cap, which is exactly the residue the project's novelty claim rests "
            "on - and 'minus delay and cap' is a narrow residue to defend."
        ),
    },
    {
        "source_id": "LIT-0041",
        "title": (
            "Synchronization in phase-coupled Kuramoto oscillator networks with axonal delay and "
            "synaptic plasticity"
        ),
        "authors": "Timms, L.; English, L. Q.",
        "year": "2014",
        "venue": "Physical Review E 89, 032906",
        "venue_type": "journal",
        "identifiers": "DOI:10.1103/PhysRevE.89.032906",
        "canonical_url": "https://doi.org/10.1103/PhysRevE.89.032906",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L1",
        "bears_on_ids": "EMP-AIEF13-02;AUD-NOVELTY",
        "stance": "CAUTION",
        "excerpt": (
            "Phys. Rev. E 89, 032906 (2014). Bibliographic record confirmed against multiple "
            "independent citing works, which give the title, authors, volume, article number and "
            "DOI consistently. Abstract not read directly."
        ),
        "notes": (
            "TITLE CORRECTION: round 6 called this 'Delay-induced patterns / delay plus plasticity "
            "in adaptive oscillator networks'. The real title is above.\n\n"
            "This is the delay-plus-plasticity ingredient: Kuramoto oscillators with axonal "
            "transmission delay and synaptic plasticity together. It is the closest prior art for "
            "the COMBINATION of the two mechanisms, which is the part of the residue that "
            "LIT-0040 leaves open. That makes the residual novelty claim narrow indeed.\n\n"
            "VERIFIED_METADATA only: the bibliographic record was confirmed across several "
            "independent citing works, but the abstract was not read, so no content claim beyond "
            "the title's own scope is made here. Opening the abstract is a round-8 task."
        ),
    },
    {
        "source_id": "LIT-0042",
        "title": (
            "Adaptive oscillator networks with conserved overall coupling: sequential firing and "
            "near-synchronized states"
        ),
        "authors": "Picallo, C. B.; Riecke, H.",
        "year": "2011",
        "venue": "Physical Review E 83, 036206",
        "venue_type": "journal",
        "identifiers": "DOI:10.1103/PhysRevE.83.036206;PMID:21517574",
        "canonical_url": "https://doi.org/10.1103/PhysRevE.83.036206",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L1",
        "bears_on_ids": "AUD-NOVELTY",
        "stance": "CAUTION",
        "excerpt": (
            "Phys. Rev. E 83, 036206, epub 18 March 2011. PubMed record: 'Adaptive oscillator "
            "networks with conserved overall coupling: sequential firing and near-synchronized "
            "states', Clara B. Picallo and Hermann Riecke, Instituto de Fisica de Cantabria "
            "(IFCA), CSIC-UC, Santander, Spain. PMID 21517574. Abstract not read directly."
        ),
        "notes": (
            "TITLE CORRECTION: round 6 called this 'Conserved-coupling normalisation in adaptive "
            "networks'. Real title above.\n\n"
            "The conserved-overall-coupling ingredient. Confirmed only via the PubMed record and "
            "the author's own publication list; the abstract was not read, so the note stops at "
            "what the title asserts. A citing SIAM paper describes this as 'the adaptive law "
            "introduced by Picallo and Riecke', which suggests it is a reference model for the "
            "class rather than a one-off.\n\n"
            "Bears on AUD-NOVELTY only. It was tempting to map it to CF01-CF03 because both "
            "involve a normalisation, but the capacity gate is a min-endpoint cap, not a "
            "conserved-sum constraint, and mapping it would have overstated the connection."
        ),
    },
    {
        "source_id": "LIT-0043",
        "title": "The Role of Constraints in Hebbian Learning",
        "authors": "Miller, K. D.; MacKay, D. J. C.",
        "year": "1994",
        "venue": "Neural Computation 6(1), pp. 100-126",
        "venue_type": "journal",
        "identifiers": "DOI:10.1162/neco.1994.6.1.100",
        "canonical_url": "https://doi.org/10.1162/neco.1994.6.1.100",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L1",
        "bears_on_ids": "AUD-NOVELTY",
        "stance": "METHOD",
        "excerpt": (
            "Neural Computation 6(1):100-126, 1994. 'Models of unsupervised, correlation-based "
            "(Hebbian) synaptic plasticity are typically unstable... A common method of avoiding "
            "these outcomes is to use a constraint that conserves or limits the total synaptic "
            "strength over a cell. We study the dynamic effects of such constraints. Two methods "
            "of enforcing a constraint are distinguished, multiplicative and subtractive. ... "
            "multiplicative enforcement of a constraint results in dynamics that converge to the "
            "principal eigenvector of the operator determining unconstrained synaptic development. "
            "Subtractive enforcement, in contrast, leads to a final state in which almost all "
            "synaptic strengths reach either the maximum or minimum allowed value.'"
        ),
        "notes": (
            "TITLE CORRECTION: round 6 called this 'Adding up the parts: multiplicative vs "
            "subtractive normalisation constraints in Hebbian learning'. I invented that title. "
            "The real one is 'The Role of Constraints in Hebbian Learning', and the fact that I "
            "manufactured a plausible-sounding subtitle is the strongest possible argument for "
            "never recording a citation without fetching its record.\n\n"
            "The most consequential of the four for the project's own reasoning. The result is "
            "that the CHOICE of constraint is not cosmetic - multiplicative enforcement converges "
            "to the principal eigenvector while subtractive enforcement saturates nearly all "
            "weights at the bounds. That is a direct statement about why the capacity gate's FORM "
            "matters, which is the territory CF01-CF03 and AUD-GATE occupy. `AIEFS_salvage.md` "
            "claims multiplicative normalisation 'is exactly what produces the k*eta/c rates'; "
            "this paper is the classical result that would license that claim, and I have not "
            "verified that the AIEF gate is multiplicative in Miller-MacKay's sense - the gate is "
            "a min-endpoint cap, which may be neither.\n\n"
            "Page range: MacKay's own BibTeX gives 98-124 while publisher records and citing "
            "works give 100-126. The DOI encodes the page-100 start. Recorded as 100-126 with the "
            "discrepancy noted rather than silently picked."
        ),
    },
]

LEAD_RESOLUTIONS = {
    "LEAD-0008": "LIT-0040",
    "LEAD-0009": "LIT-0041",
    "LEAD-0010": "LIT-0042",
    "LEAD-0011": "LIT-0043",
}

# What the leads originally claimed, kept so the correction is auditable.
RETIRED_LEAD_TITLES = {
    "LEAD-0008": "Self-organization in networks of phase oscillators with Hebbian coupling",
    "LEAD-0009": "Delay-induced patterns / delay plus plasticity in adaptive oscillator networks",
    "LEAD-0010": "Conserved-coupling normalisation in adaptive networks",
    "LEAD-0011": "Adding up the parts: multiplicative vs subtractive normalisation constraints in Hebbian learning",
}


def main() -> None:
    SNAP.mkdir(parents=True, exist_ok=True)

    with (ROOT / "SOURCES.csv").open(encoding="utf-8", newline="") as fh:
        all_rows = list(csv.DictReader(fh))
    existing = [r for r in all_rows if r["round_added"] != "7"]
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
            "excerpt_provenance": (
                "publisher landing page / author abstract page, read directly"
                if rec["verification_level"] == "VERIFIED_FULL"
                else "publisher or index record confirmed across independent citing works; abstract not read"
            ),
        }
        blob = json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"
        (SNAP / snap_name).write_text(blob, encoding="utf-8")
        row = dict(rec)
        row.pop("excerpt")
        row["round_added"] = "7"
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
    print(f"added {len(new_rows)} sources -> total {len(rows)}")

    leads_path = ROOT / "LEADS.csv"
    with leads_path.open(encoding="utf-8", newline="") as fh:
        leads = list(csv.DictReader(fh))
    for lead in leads:
        lid = lead["lead_id"]
        if lid in LEAD_RESOLUTIONS:
            src = LEAD_RESOLUTIONS[lid]
            original = RETIRED_LEAD_TITLES[lid]
            lead["status"] = "RESOLVED"
            lead["resolved_as"] = src
            note = lead.get("next_action", "")
            if not note.startswith("done:"):
                lead["next_action"] = f"done: promoted to {src}. original: {note}"
            if f"WRONG TITLE {original!r}" not in lead["title_hint"]:
                lead["title_hint"] = f"{lead['title_hint']} [WRONG TITLE {original!r} -> see {src}]"
    cols = ["lead_id", "status", "resolved_as", "title_hint", "identifier_hint",
            "url", "why_not_citable", "next_action"]
    with leads_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in leads:
            w.writerow({k: r[k] for k in cols})
    print(f"leads: {len(leads)} total, {sum(1 for r in leads if r['status']=='OPEN')} open")


if __name__ == "__main__":
    main()
