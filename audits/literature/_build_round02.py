#!/usr/bin/env python3
"""Build Round 2: append 12 sources, resolve the 3 Round 1 leads.

Append-only. Round 1 rows are read and rewritten unchanged; only new IDs are
added. See _build_round01.py for the provenance convention (retrieval_method,
verification_level) - it is unchanged.

Round 2 also introduces two columns on LEADS.csv (status, resolved_as) so that
a resolved lead is visibly retired instead of silently left looking open.
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
        "source_id": "LIT-0017",
        "title": "The Multiverse of Dynamic Mode Decomposition Algorithms",
        "authors": "Colbrook, M. J.",
        "year": "2023",
        "venue": "arXiv",
        "venue_type": "preprint",
        "identifiers": "arXiv:2312.00137;DOI:10.48550/arXiv.2312.00137",
        "canonical_url": "https://arxiv.org/abs/2312.00137",
        "retrieval_method": "fetch_page",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L5",
        "bears_on_ids": "REJ-SPEC-01;S09;AIEF_1_4_REJECTED_SPECTRAL_AND_K3",
        "stance": "CAUTION",
        "excerpt": (
            "Submitted 30 Nov 2023 (v1), revised 21 Dec 2023 (v2); review article, 88 pages, "
            "28 figures; math.DS. 'A distinctive feature of this review is its focus on the "
            "relationship between DMD and the spectral properties of Koopman operators, with "
            "particular emphasis on the theory and practice of DMD algorithms for spectral "
            "computations.'"
        ),
        "notes": (
            "Resolves LEAD-0001, and corrects it: the review is by a single author, not a group. "
            "It is the standard map of DMD-as-spectral-computation, with a three-way taxonomy "
            "(linear-regression, Galerkin, structure-preserving) and a MATLAB package. Relevant "
            "because the rejected 8D compression used one regression variant with no convergence "
            "argument; this review is the catalogue of what else was available and is the correct "
            "entry point for any future attempt."
        ),
    },
    {
        "source_id": "LIT-0018",
        "title": (
            "Synchronization and resilience in the Kuramoto white matter network model with "
            "adaptive state-dependent delays"
        ),
        "authors": "Park, S. H.; Lefebvre, J.",
        "year": "2020",
        "venue": "The Journal of Mathematical Neuroscience",
        "venue_type": "journal",
        "identifiers": "DOI:10.1186/s13408-020-00091-y",
        "canonical_url": "https://doi.org/10.1186/s13408-020-00091-y",
        "retrieval_method": "fetch_page",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L1;L3",
        "bears_on_ids": "AIEF_1_0_TO_1_2_FOUNDATIONAL;EMP-AIEF14-02;AIEF_1_4_TWINDOW_SENSITIVITY",
        "stance": "CONTEXT",
        "excerpt": (
            "J. Math. Neurosci. 10, article 16 (2020), open access, published 16 September 2020. "
            "'...we modified the canonical Kuramoto model by enabling all connections with "
            "adaptive, phase-dependent delays... plastic delays act as a stabilizing mechanism "
            "promoting the network's ability to maintain synchronous activity... global "
            "synchronization is more resilient to perturbations and injury towards network "
            "architecture.'"
        ),
        "notes": (
            "Resolves LEAD-0002: Park & Lefebvre, not an anonymous group. This is the earliest "
            "verified member of the adaptive-delay cluster (2020), predating LIT-0016 and "
            "LIT-0028. One sentence in the paper is structurally important and was not in the "
            "Round 1 record: the model 'corresponds to an N + N^2-dimensional functional "
            "differential equation with state-dependent delays'. The state dimension grows with "
            "the edge set. That is the concrete reason EMP-AIEF14-01 (no single component is a "
            "privileged memory bottleneck) is expected rather than surprising - it is the same "
            "argument as LIT-0010, now with an explicit dimension count."
        ),
    },
    {
        "source_id": "LIT-0019",
        "title": "Random Dynamical Systems",
        "authors": "Arnold, L.",
        "year": "1998",
        "venue": "Springer Monographs in Mathematics, Springer",
        "venue_type": "book",
        "identifiers": "DOI:10.1007/978-3-662-12878-7;ISBN:3-540-63758-3;MR1723992",
        "canonical_url": "https://doi.org/10.1007/978-3-662-12878-7",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L4",
        "bears_on_ids": "AIEF_1_4_TANGENT_AND_COCYCLE;S11",
        "stance": "METHOD",
        "excerpt": (
            "Springer Monographs in Mathematics, Berlin/Heidelberg, 1998; xvi+586 pp.; "
            "ISBN 3-540-63758-3; MR1723992. 'The definition of a random dynamical system or "
            "cocycle is given in Sect. 1.1 and basic properties are derived (Theorem 1.1.6).'"
        ),
        "notes": (
            "Resolves LEAD-0003 and fills domain L4, which Round 1 left entirely empty. This is "
            "the primary reference for the cocycle formalism the repository invokes. IMPORTANT "
            "OPEN ITEM: a cocycle is not a naming preference, it is an identity - "
            "Phi(t+s, w) = Phi(t, theta_s w) Phi(s, w) over a measure-preserving shift theta. "
            "Round 2 did NOT verify that the construction called the 'history cocycle' in "
            "AIEF_1_4_TANGENT_AND_COCYCLE satisfies that composition law. Flagged as a Round 3 "
            "verification item, because if it does not, the claim needs a different word."
        ),
    },
    {
        "source_id": "LIT-0020",
        "title": "Piecewise-smooth Dynamical Systems: Theory and Applications",
        "authors": "di Bernardo, M.; Budd, C. J.; Champneys, A. R.; Kowalczyk, P.",
        "year": "2008",
        "venue": "Applied Mathematical Sciences, vol. 163, Springer",
        "venue_type": "book",
        "identifiers": "DOI:10.1007/978-1-84628-708-4;ISBN:978-1-84628-039-9",
        "canonical_url": "https://doi.org/10.1007/978-1-84628-708-4",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L7",
        "bears_on_ids": "CF01;CF02;CF03;CF05;REJ-SPEC-02;S04;AIEF_1_4_CONTROLLER_FIBER",
        "stance": "METHOD",
        "excerpt": (
            "Applied Mathematical Sciences vol. 163, Springer, London, 2008, 481 pp. "
            "'Traditional analysis of dynamical systems has restricted its attention to smooth "
            "problems, but it has become increasingly clear that there are distinctive phenomena "
            "unique to discontinuous systems that can be analyzed mathematically but which fall "
            "outside the usual methodology for smooth dynamical systems.'"
        ),
        "notes": (
            "The framing reference for the entire CF01-CF12 block, which Round 1 left with no "
            "literature at all. The admissibility map A_eps(x) = M(Ax)x with min-selected "
            "endpoint winners is piecewise-smooth; this book is the standard treatment of that "
            "class. Consequence for S04: the 'event' at t=124.05 is a discontinuity-induced "
            "phenomenon, not an implementation defect, and the book supplies the vocabulary "
            "(border collision / boundary-equilibrium bifurcation) to say precisely which."
        ),
    },
    {
        "source_id": "LIT-0021",
        "title": "Lexicographic differentiation of nonsmooth functions",
        "authors": "Nesterov, Yu.",
        "year": "2005",
        "venue": "Mathematical Programming",
        "venue_type": "journal",
        "identifiers": "DOI:10.1007/s10107-005-0633-0",
        "canonical_url": "https://doi.org/10.1007/s10107-005-0633-0",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L7",
        "bears_on_ids": "CF01;CF02;CF03;CF05;REJ-SPEC-02;AIEF_1_4_CONTROLLER_FIBER",
        "stance": "METHOD",
        "excerpt": (
            "Math. Program. 104(2-3):669-700, published 14 July 2005, issue date November 2005. "
            "'This theory ensures an efficient computation of generalized (lexicographic) "
            "derivative of a nonsmooth function belonging to a special class of lexicographically "
            "smooth functions... it is shown that the system of lexicographic derivatives along a "
            "fixed basis correctly represents corresponding nonsmooth function (Newton-Leibnitz "
            "formula)... an appropriately defined lexicographic subdifferential ensures a more "
            "rigorous selection of a candidate optimal solution than the subdifferential of "
            "Clarke.'"
        ),
        "notes": (
            "Supplies the uniqueness theorem behind CF03. Once a basis is fixed, the lexicographic "
            "derivative is unique - which is exactly the property needed at winner ties, and "
            "exactly the property a branchwise Jacobian does not have. Note the paper's own claim "
            "that the lexicographic subdifferential is *more* rigorous than Clarke's: for the CF "
            "block, lexicographic differentiation is the stronger tool, not a fallback when "
            "Clarke is inconvenient."
        ),
    },
    {
        "source_id": "LIT-0022",
        "title": (
            "A vector forward mode of automatic differentiation for generalized derivative "
            "evaluation"
        ),
        "authors": "Khan, K. A.; Barton, P. I.",
        "year": "2015",
        "venue": "Optimization Methods and Software",
        "venue_type": "journal",
        "identifiers": "DOI:10.1080/10556788.2015.1025400",
        "canonical_url": "https://doi.org/10.1080/10556788.2015.1025400",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L7",
        "bears_on_ids": "CF01;CF02;CF03;CF05;REJ-SPEC-02;AIEF_1_4_CONTROLLER_FIBER",
        "stance": "METHOD",
        "excerpt": (
            "Optimization Methods and Software 30(6):1185-1212, 2015. 'It is shown here that "
            "piecewise differentiable functions are lexicographically smooth in the sense of "
            "Nesterov, and that lexicographic derivatives of these functions comprise a particular "
            "subset of both the B-subdifferential and the Clarke Jacobian.'"
        ),
        "notes": (
            "The implementable bridge between LIT-0021 and the code. It gives an automatic-"
            "differentiation forward mode for lexicographic directional derivatives, with rules "
            "for min, max, mid and abs - and AIEF's winner map is built from min(). So the exact "
            "nontrivial primitive the audit needed is covered by an existing method. Second, "
            "useful negative evidence: the approach explicitly treats finite differencing as "
            "unsuitable for nonsmooth functions ('stepping' over nonsmooth points), which is the "
            "formal statement of why REJ-SPEC-02 could not be rescued by shrinking epsilon."
        ),
    },
    {
        "source_id": "LIT-0023",
        "title": "Investigating Causal Relations by Econometric Models and Cross-spectral Methods",
        "authors": "Granger, C. W. J.",
        "year": "1969",
        "venue": "Econometrica",
        "venue_type": "journal",
        "identifiers": "JSTOR:1912791",
        "canonical_url": "https://www.jstor.org/stable/1912791",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L2",
        "bears_on_ids": "EMP-AIEF13-01;EMP-AIEF13-02;AIEF_1_3_DISJOINT_100SEED",
        "stance": "CONTEXT",
        "excerpt": (
            "Econometrica 37(3):424-438, August 1969. 'There occurs on some occasions a difficulty "
            "in deciding the direction of causality between two related variables and also whether "
            "or not feedback is occurring. Testable definitions of causality and feedback are "
            "proposed... it is suggested that the problem often arises due to slowness in "
            "recording information or because a sufficiently wide class of possible causal "
            "variables has not been used.'"
        ),
        "notes": (
            "The baseline definition (causality as incremental predictability conditional on "
            "history). Included to make one thing explicit that the registry leaves implicit: the "
            "AIEF-1.3 design is NOT a Granger test. It intervenes on the mechanism and measures a "
            "downstream structural difference. That is a stronger identification strategy than "
            "incremental predictability, and the claim should say so instead of leaving 'causal' "
            "undefined."
        ),
    },
    {
        "source_id": "LIT-0024",
        "title": "Detecting Causality in Complex Ecosystems",
        "authors": "Sugihara, G.; May, R.; Ye, H.; Hsieh, C.-H.; Deyle, E.; Fogarty, M.; Munch, S.",
        "year": "2012",
        "venue": "Science",
        "venue_type": "journal",
        "identifiers": "DOI:10.1126/science.1227079",
        "canonical_url": "https://doi.org/10.1126/science.1227079",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L2",
        "bears_on_ids": "EMP-AIEF13-01;EMP-AIEF13-02;AIEF_1_3_DISJOINT_100SEED",
        "stance": "CONTEXT",
        "excerpt": (
            "Science 338(6106):496-500, 26 October 2012. 'We introduce a method, based on "
            "nonlinear state space reconstruction, that can distinguish causality from "
            "correlation... extends to nonseparable weakly connected dynamic systems (cases not "
            "covered by the current Granger causality paradigm).'"
        ),
        "notes": (
            "The constructive critique of Granger for coupled dynamical systems. Cited because it "
            "establishes that predictability-based causal inference is contested for precisely the "
            "class of system AIEF studies (strongly coupled, state-dependent, nonseparable) - "
            "which strengthens the case for an intervention design over any observational causal "
            "metric. Together with LIT-0023 this pins the two poles the AIEF design sits between."
        ),
    },
    {
        "source_id": "LIT-0025",
        "title": "Measuring Information Transfer",
        "authors": "Schreiber, T.",
        "year": "2000",
        "venue": "Physical Review Letters",
        "venue_type": "journal",
        "identifiers": "DOI:10.1103/PhysRevLett.85.461",
        "canonical_url": "https://doi.org/10.1103/PhysRevLett.85.461",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L2;L3",
        "bears_on_ids": "EMP-AIEF14-02;AIEF_1_4_MATCHED_PHASE_ABLATION",
        "stance": "SUPPORTS",
        "excerpt": (
            "Physical Review Letters 85(2):461-464, published 10 July 2000. 'The standard time "
            "delayed mutual information fails to distinguish information that is actually "
            "exchanged from shared information due to common history and input signals. In our new "
            "approach, these influences are excluded by appropriate conditioning of transition "
            "probabilities.'"
        ),
        "notes": (
            "The most directly relevant find of Round 2 for claim design. EMP-AIEF14-02's "
            "matched-phase ablation exists precisely because a naive comparison cannot separate "
            "history that is genuinely transmitted from history that both conditions merely share. "
            "Schreiber names that confound - 'shared information due to common history' - and gives "
            "the conditioning remedy. The matched-phase design is the same logic applied to an "
            "intervention instead of to an estimator. This supplies the formal reason the design is "
            "necessary, which the registry currently asserts only empirically."
        ),
    },
    {
        "source_id": "LIT-0026",
        "title": "Bootstrap-Based Improvements for Inference with Clustered Errors",
        "authors": "Cameron, A. C.; Gelbach, J. B.; Miller, D. L.",
        "year": "2008",
        "venue": "The Review of Economics and Statistics",
        "venue_type": "journal",
        "identifiers": "DOI:10.1162/rest.90.3.414",
        "canonical_url": "https://doi.org/10.1162/rest.90.3.414",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L2",
        "bears_on_ids": "EMP-AIEF13-01;EMP-AIEF13-02",
        "stance": "METHOD",
        "excerpt": (
            "The Review of Economics and Statistics 90(3):414-427, August 2008; "
            "DOI 10.1162/rest.90.3.414. (Bibliographic record only - see notes on content "
            "provenance.)"
        ),
        "notes": (
            "HONESTY NOTE: the bibliographic record was confirmed, but this paper's abstract was "
            "not read directly. The description of its contribution used here is taken second-hand "
            "from LIT-0002 (the 2015 practitioner's guide by Cameron & Miller), which states that "
            "in Monte Carlos with few clusters the cluster bootstrap did not eliminate "
            "over-rejection, and that the authors proposed the wild cluster bootstrap, which holds "
            "the regressors fixed across bootstrap replications. A Round 3 task is to read the "
            "original abstract and remove this dependency."
        ),
    },
    {
        "source_id": "LIT-0027",
        "title": "Reworking Wild Bootstrap Based Inference For Clustered Errors",
        "authors": "Webb, M. D.",
        "year": "2013",
        "venue": "Queen's Economics Department Working Paper 1315",
        "venue_type": "preprint",
        "identifiers": "RePEc:qed:wpaper:1315",
        "canonical_url": "https://www.econ.queensu.ca/research/working-papers/1315",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L2",
        "bears_on_ids": "EMP-AIEF13-01;EMP-AIEF13-02",
        "stance": "CAUTION",
        "excerpt": (
            "Queen's Economics Department Working Paper No. 1315. 'I demonstrate, using Monte "
            "Carlo experiments, that these bootstrap procedures perform poorly with fewer than "
            "eleven clusters. With few clusters, the wild cluster bootstrap results in p-values "
            "that are not point identified. I suggest two alternative wild bootstrap "
            "procedures... a 6-point bootstrap weight distribution improves the reliability of "
            "inference.'"
        ),
        "notes": (
            "Sets the threshold that decides whether EMP-AIEF13-01's interval needs remedial work. "
            "N=100 (disjoint cohort) and N=40 (the rejected cohort) both exceed Webb's "
            "eleven-cluster threshold, so neither needs the 6-point distribution. Round 2 "
            "therefore reports NO ACTION REQUIRED on the interval construction - a clean negative "
            "result. Year attribution varies across citing works and the RePEc record lists a "
            "2014-11 revision; a journal version appeared in 2023. Recorded as 2013 with the "
            "ambiguity noted rather than resolved by preference."
        ),
    },
    {
        "source_id": "LIT-0028",
        "title": (
            "Phase oscillator networks with multiple and state-dependent delays: A framework for "
            "exploring white matter plasticity in neurodynamics"
        ),
        "authors": "Jolly, G.; Nicks, R.; Ruschel, S.; Iskenderoglu, G.; Coombes, S.",
        "year": "2026",
        "venue": "arXiv",
        "venue_type": "preprint",
        "identifiers": "arXiv:2609.08619;DOI:10.48550/arXiv.2609.08619",
        "canonical_url": "https://arxiv.org/abs/2609.08619",
        "retrieval_method": "fetch_page",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L1;L3",
        "bears_on_ids": "AIEF_1_4_TWINDOW_SENSITIVITY;EMP-AIEF14-02;AIEF_1_4_TANGENT_AND_COCYCLE",
        "stance": "CAUTION",
        "excerpt": (
            "Submitted 8 Sep 2026, math.DS, 35 pages; MSC 34K43, 34C15, 37N25, 34K20. 'When "
            "understanding how network delays shape emergent properties, the delays are often "
            "absorbed in the reduced description as a phase shift. The reduced system is a set of "
            "ODEs that loses some information about the full delay differential equation (DDE) "
            "system. We adopt a less restrictive approach...'"
        ),
        "notes": (
            "The most important CAUTION of Round 2. Stated by a group actively working this exact "
            "problem: phase reduction LOSES delay information. Any AIEF claim that describes delay "
            "effects through a phase variable inherits that loss. The AIEF-1.4 programme keeps the "
            "delay explicit - which is the 'less restrictive approach' this paper recommends - so "
            "this is simultaneously a constraint and a point in the repository's favour that "
            "should be stated rather than left implicit. Shared authorship with LIT-0016 "
            "(Ruschel, Nicks, Coombes) confirms a fast-moving group on this mechanism."
        ),
    },
]

# Round 1 leads, now resolved.
LEAD_RESOLUTIONS = {
    "LEAD-0001": ("RESOLVED", "LIT-0017"),
    "LEAD-0002": ("RESOLVED", "LIT-0018"),
    "LEAD-0003": ("RESOLVED", "LIT-0019"),
}

NEW_LEADS = [
    {
        "lead_id": "LEAD-0004",
        "title_hint": (
            "From Kuramoto to Crawford: exploring the onset of synchronization in populations of "
            "coupled oscillators"
        ),
        "identifier_hint": "Physica D 143(1):1-20 (2000)",
        "url": "(no URL captured)",
        "why_not_citable": (
            "Seen only as reference [1] in the reference list of LIT-0018, not opened "
            "independently. Bibilographic details are as rendered by the publisher page."
        ),
        "next_action": "Open the Physica D record; capture DOI; promote if it adds more than context.",
        "status": "OPEN",
        "resolved_as": "",
    },
    {
        "lead_id": "LEAD-0005",
        "title_hint": (
            "Wild bootstrap confidence intervals / Wild bootstrap inference for wildly different "
            "cluster sizes (MacKinnon & Webb)"
        ),
        "identifier_hint": "Queen's Economics Department working papers 1314 / 1415",
        "url": "(no URL captured)",
        "why_not_citable": (
            "Appeared only as citations inside search-result excerpts for LIT-0027; not opened. "
            "Would let EMP-AIEF13-01 report an interval rather than a p-value if the interval "
            "construction is ever revisited."
        ),
        "next_action": "Open the working paper; confirm which of the two titles is wanted; promote.",
        "status": "OPEN",
        "resolved_as": "",
    },
    {
        "lead_id": "LEAD-0006",
        "title_hint": "Reachability for Nonsmooth Systems with Lexicographic Jacobians",
        "identifier_hint": "Springer chapter, DOI:10.1007/978-3-031-90653-4_18 (2025)",
        "url": "https://doi.org/10.1007/978-3-031-90653-4_18",
        "why_not_citable": (
            "Surfaced while verifying LIT-0021/LIT-0022 and is exactly on target (lexicographic "
            "Jacobians propagated through a nonsmooth dynamical system), but was not opened. "
            "Would be the applied demonstration that CF03's approach is standard practice."
        ),
        "next_action": "Open the chapter; capture authors and venue; promote to a source.",
        "status": "OPEN",
        "resolved_as": "",
    },
]


def main() -> None:
    SNAP.mkdir(parents=True, exist_ok=True)

    # ---- read existing rows, unchanged --------------------------------
    with (ROOT / "SOURCES.csv").open(encoding="utf-8", newline="") as fh:
        all_rows_in = list(csv.DictReader(fh))
    # Idempotent: drop any prior round-2 rows so this script can be re-run.
    existing = [r for r in all_rows_in if r["round_added"] != "2"]
    existing_ids = {r["source_id"] for r in existing}
    print(f"existing rounds: {len(existing)} rows, up to {sorted(existing_ids)[-1]}")

    # ---- create snapshots + rows for the new sources -------------------
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
                "arXiv abstract/landing page, read directly"
                if rec["retrieval_method"] == "fetch_page"
                else "search-index rendering of the publisher/canonical page"
            ),
        }
        blob = json.dumps(snapshot, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
        (SNAP / snap_name).write_text(blob, encoding="utf-8")
        digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()

        row = dict(rec)
        row.pop("excerpt")
        row["round_added"] = "2"
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

    # ---- leads: add status columns, retire resolved --------------------
    with (ROOT / "LEADS.csv").open(encoding="utf-8", newline="") as fh:
        leads = [r for r in csv.DictReader(fh) if r["lead_id"] not in {n["lead_id"] for n in NEW_LEADS}]
    for lead in leads:
        lid = lead["lead_id"]
        if lid in LEAD_RESOLUTIONS:
            status, resolved = LEAD_RESOLUTIONS[lid]
            note = lead.get("next_action", "")
            lead["next_action"] = f"done: promoted to {resolved}. original: {note}"
        else:
            status, resolved = "OPEN", ""
        lead["status"] = status
        lead["resolved_as"] = resolved
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
    open_leads = sum(1 for r in leads if r["status"] == "OPEN")
    print(f"leads: {len(leads)} total, {open_leads} open")


if __name__ == "__main__":
    main()
