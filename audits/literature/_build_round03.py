#!/usr/bin/env python3
"""Build Round 3: append 5 sources, resolve the 3 remaining leads, open 1.

Idempotent, same convention as _build_round02.py.
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
        "source_id": "LIT-0029",
        "title": "Numerical Methods for Delay Differential Equations",
        "authors": "Bellen, A.; Zennaro, M.",
        "year": "2003",
        "venue": "Numerical Mathematics and Scientific Computation, Oxford University Press",
        "venue_type": "book",
        "identifiers": "DOI:10.1093/acprof:oso/9780198506546.001.0001;ISBN:0198506546",
        "canonical_url": "https://doi.org/10.1093/acprof:oso/9780198506546.001.0001",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L3",
        "bears_on_ids": "AIEF_1_4_SPLIT_STATE_ABLATION;S03;AIEF_1_4_TANGENT_AND_COCOYCLE".replace("COCOYCLE", "COCYCLE"),
        "stance": "METHOD",
        "excerpt": (
            "Oxford University Press, 2003, series Numerical Mathematics and Scientific "
            "Computation, ISBN 0198506546. Publisher description: '...provides an introduction to "
            "the Cauchy problem for delay differential equations. It is aimed at mathematicians, "
            "physicists, engineers and other scientists interested in this area of numerical "
            "methods.'"
        ),
        "notes": (
            "The canonical reference for DDE numerics, and the source of the caveat that matters "
            "most for AIEF_1_4_SPLIT_STATE_ABLATION. In a DDE the state is the history segment "
            "(LIT-0010), and a well-posed DDE needs an explicit history function on the initial "
            "interval. Two consequences for the split-state design. (1) An ablation applied at the "
            "split time does not merely reset a component; it injects a first-order discontinuity "
            "into the history, and the method-of-steps error analysis is organised around how such "
            "discontinuities propagate and smooth. (2) Comparing post-split trajectories across "
            "arms therefore compares two different discontinuity structures unless the split is "
            "handled identically in both. The registry currently records the split operation but "
            "not this propagation effect. Round 4/5 action item: state the discontinuity order "
            "induced by the split and confirm it is identical across arms."
        ),
    },
    {
        "source_id": "LIT-0030",
        "title": (
            "Synchronization in oscillator networks with delayed coupling: A stability criterion"
        ),
        "authors": "Earl, M. G.; Strogatz, S. H.",
        "year": "2003",
        "venue": "Physical Review E",
        "venue_type": "journal",
        "identifiers": "DOI:10.1103/PhysRevE.67.036204",
        "canonical_url": "https://doi.org/10.1103/PhysRevE.67.036204",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L1;L3",
        "bears_on_ids": "REJ-LOCK-03;AIEF_1_4_TWINDOW_SENSITIVITY",
        "stance": "SUPPORTS",
        "excerpt": (
            "Physical Review E 67, 036204 (2003). Cited consistently across the delay-coupled "
            "oscillator literature as establishing the stability criterion for phase-locked states "
            "in ring networks of identical phase oscillators with delayed coupling: locking "
            "conditions are transcendental in the delay and must be solved for the collective "
            "frequency, not checked as an algebraic sum. (Bibliographic record plus the cited "
            "characterisation; the abstract itself was not opened - see notes.)"
        ),
        "notes": (
            "HONESTY NOTE: this record is VERIFIED_METADATA for the bibliographic fields, but the "
            "description of the content is taken from how the delay-coupled-oscillator literature "
            "consistently cites it (verified across four independent citing works in the same "
            "search), not from the paper's own abstract. A Round 4 task is to open the abstract "
            "and tighten this.\n\n"
            "Why it matters: it gives REJ-LOCK-03 a published alternative. The rejected claim was "
            "that mature oscillator frequencies satisfy the bare algebraic zero-sum "
            "omega_i + G_i = 0. For delay-coupled networks the correct object is the phase-locked "
            "condition: frequency and phase offsets satisfy implicit equations in the delay, so "
            "an algebraic sum is the wrong functional form regardless of numerics. Combined with "
            "LIT-0018 and LIT-0028 this turns a bare negative numerical result into a structural "
            "statement."
        ),
    },
    {
        "source_id": "LIT-0031",
        "title": (
            "From Kuramoto to Crawford: exploring the onset of synchronization in populations of "
            "coupled oscillators"
        ),
        "authors": "Strogatz, S. H.",
        "year": "2000",
        "venue": "Physica D: Nonlinear Phenomena",
        "venue_type": "journal",
        "identifiers": "DOI:10.1016/S0167-2789(00)00094-4",
        "canonical_url": "https://doi.org/10.1016/S0167-2789(00)00094-4",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L1",
        "bears_on_ids": "AIEF_1_0_TO_1_2_FOUNDATIONAL;AIEF_1_3_DISJOINT_100SEED",
        "stance": "CONTEXT",
        "excerpt": (
            "Physica D: Nonlinear Phenomena 143(1-4):1-20, 2000; "
            "DOI:10.1016/S0167-2789(00)00094-4. The standard review of the Kuramoto programme: "
            "the mean-field order parameter R, the critical coupling, and the open problems "
            "surrounding the infinite-N limit and finite-N fluctuations."
        ),
        "notes": (
            "Resolves LEAD-0004. Context only: it does not adjudicate any AIEF claim and is not "
            "offered as support for one. Its value is that it defines the vocabulary (order "
            "parameter, critical coupling, phase-locked versus incoherent) that the AIEF-1.0-1.2 "
            "adaptive-network material uses without citing. Useful when the Era-1 provenance gap "
            "(see ROUND_03 F16) is repaired: whichever code produced those results was working in "
            "this framework and should say so."
        ),
    },
    {
        "source_id": "LIT-0032",
        "title": "Wild Bootstrap Inference for Wildly Different Cluster Sizes",
        "authors": "MacKinnon, J. G.; Webb, M. D.",
        "year": "2017",
        "venue": "Journal of Applied Econometrics",
        "venue_type": "journal",
        "identifiers": "DOI:10.1002/jae.2508",
        "canonical_url": "https://doi.org/10.1002/jae.2508",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L2",
        "bears_on_ids": "EMP-AIEF13-01;EMP-AIEF13-02",
        "stance": "CAUTION",
        "excerpt": (
            "Journal of Applied Econometrics 32(2):233-254, March 2017. 'The cluster robust "
            "variance estimator (CRVE) relies on the number of clusters being sufficiently large. "
            "Monte Carlo evidence suggests that the \"rule of 42\" is not true for unbalanced "
            "clusters. Rejection frequencies are higher for datasets with 50 clusters proportional "
            "to US state populations than with 50 balanced clusters. Using critical values based on "
            "the wild cluster bootstrap performs much better. However, this procedure fails when a "
            "small number of clusters is treated.'"
        ),
        "notes": (
            "Resolves LEAD-0005 (the Queen's working paper 1314 became this journal article). "
            "Confirms and sharpens Round 2's F14 without changing it. The failure modes named here "
            "are unbalanced cluster sizes and few TREATED clusters. Neither applies to the AIEF "
            "design: seeds are exchangeable and every seed is treated in every arm, so the treated "
            "fraction is 1 by construction and cluster sizes are equal. Conclusion stands: no "
            "remedial work on EMP-AIEF13-01's interval. The one transferable caution is that if a "
            "future design ever ablates a SUBSET of seeds, this paper says the interval "
            "construction must change at that moment."
        ),
    },
    {
        "source_id": "LIT-0033",
        "title": "Reachability for Nonsmooth Systems with Lexicographic Jacobians",
        "authors": "Ji, C.; Zhang, H.; Mitra, S.",
        "year": "2025",
        "venue": (
            "Tools and Algorithms for the Construction and Analysis of Systems (TACAS 2025), "
            "LNCS, pp. 364-384"
        ),
        "venue_type": "conference",
        "identifiers": "DOI:10.1007/978-3-031-90653-4_18",
        "canonical_url": "https://doi.org/10.1007/978-3-031-90653-4_18",
        "retrieval_method": "fetch_page",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L7",
        "bears_on_ids": "CF01;CF02;CF03;CF05",
        "stance": "SUPPORTS",
        "excerpt": (
            "TACAS 2025, pp. 364-384, open access, first online 1 May 2025. 'Reachability analysis "
            "for dynamical systems typically relies on the system's Jacobian to bound sensitivity "
            "of solutions. This method fails for nonsmooth dynamical systems as the Jacobian "
            "becomes undefined at the points where the vector field is non-differentiable... We "
            "propose an alternative approach based on lexicographic differentiation... Our "
            "algorithm computes linear bounds on sets of lexicographic Jacobians, which give bounds "
            "on trajectory sensitivities. This avoids hybridization, eliminates mode transition "
            "computations, and yields more accurate reachsets. On nonsmooth models, our method "
            "improves accuracy on average by 50%, compared to hybrid algorithms.'"
        ),
        "notes": (
            "Resolves LEAD-0006, and is the applied demonstration Round 2 wanted. It is the same "
            "structural situation as the CF block: a nonsmooth map, a Jacobian that does not exist "
            "at the non-differentiable points, and the choice between hybridizing into smooth "
            "modes or using the lexicographic derivative. The authors do the latter and report a "
            "50% accuracy gain over hybridization. Two implications for AIEF. (1) CF03's approach "
            "is current best practice in a verified-systems venue, not a local convention. (2) The "
            "'hybridize into modes' alternative is precisely the branch bookkeeping that the AIEF "
            "audit performs when it tracks winner signatures, and this paper is evidence that the "
            "bookkeeping is avoidable rather than necessary. Worth citing if the CF block is ever "
            "rewritten."
        ),
    },
]

LEAD_RESOLUTIONS = {
    "LEAD-0004": ("RESOLVED", "LIT-0031"),
    "LEAD-0005": ("RESOLVED", "LIT-0032"),
    "LEAD-0006": ("RESOLVED", "LIT-0033"),
}

NEW_LEADS = [
    {
        "lead_id": "LEAD-0007",
        "title_hint": (
            "Recent trends in the numerical solution of retarded functional differential equations"
        ),
        "identifier_hint": "Acta Numerica 18:1-110 (2009), Bellen, Guglielmi, Maset, Zennaro",
        "url": "(no URL captured)",
        "why_not_citable": (
            "Seen only as reference [2] inside the Springer encyclopedia entry on delay "
            "differential equations, while verifying LIT-0029. Not opened."
        ),
        "next_action": (
            "Open the Acta Numerica record; it is the modern survey of DDE numerics and would "
            "supersede LIT-0029 as the citation of record for method-of-steps details."
        ),
        "status": "OPEN",
        "resolved_as": "",
    },
]


def main() -> None:
    SNAP.mkdir(parents=True, exist_ok=True)

    with (ROOT / "SOURCES.csv").open(encoding="utf-8", newline="") as fh:
        all_rows_in = list(csv.DictReader(fh))
    existing = [r for r in all_rows_in if r["round_added"] != "3"]
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
        row["round_added"] = "3"
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
