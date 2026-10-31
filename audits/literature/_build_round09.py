#!/usr/bin/env python3
"""Build Round 9: close the named gap (preregistration) and settle the gate form.

Two separate things, kept separate on purpose:

1. LITERATURE. Two sources on exploratory-vs-confirmatory methodology, which is the
   one gap named in round 8. They let AUD-LABEL be adjudicated.

2. RE-VERIFICATION. LIT-0041 and LIT-0042 were VERIFIED_METADATA. Their abstracts
   have now been read directly. That adds evidence WITHOUT contradicting the recorded
   record, so the snapshot and verification_level stay byte-identical and the new
   reading is appended to `notes`. Rationale in the round's findings.

Notes are a living annotation field; snapshots and identity fields are not. The
script enforces that distinction rather than trusting itself to observe it.
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SNAP = ROOT / "snapshots"
SRC = ROOT / "SOURCES.csv"
RETRIEVED = "2026-10-31"

COLS = [
    "source_id", "round_added", "title", "authors", "year", "venue", "venue_type",
    "identifiers", "canonical_url", "retrieved_date", "retrieval_method",
    "verification_level", "snapshot_file", "snapshot_sha256", "relevance_domains",
    "bears_on_ids", "stance", "notes",
]

IDENTITY_FIELDS = ["source_id", "title", "authors", "year", "venue", "identifiers",
                   "canonical_url", "verification_level", "snapshot_sha256"]

SOURCES = [
    {
        "source_id": "LIT-0044",
        "title": "The preregistration revolution",
        "authors": "Nosek, B. A.; Ebersole, C. R.; DeHaven, A. C.; Mellor, D. T.",
        "year": "2018",
        "venue": "Proceedings of the National Academy of Sciences 115(11), pp. 2600-2606",
        "venue_type": "journal",
        "identifiers": "DOI:10.1073/pnas.1708274114",
        "canonical_url": "https://doi.org/10.1073/pnas.1708274114",
        "retrieval_method": "fetch_page",
        "verification_level": "VERIFIED_FULL",
        "relevance_domains": "L8",
        "bears_on_ids": "AUD-LABEL;AUD-HELDOUT-LABEL",
        "stance": "METHOD",
        "excerpt": (
            "PNAS 115(11):2600-2606, 2018. 'Progress in science relies in part on generating "
            "hypotheses with existing observations and testing hypotheses with new observations. "
            "This distinction between postdiction and prediction is appreciated conceptually but "
            "is not respected in practice. Mistaking generation of postdictions with testing of "
            "predictions reduces the credibility of research findings. ... An effective solution "
            "is to define the research questions and analysis plan before observing the research "
            "outcomes - a process called preregistration. Preregistration distinguishes analyses "
            "and outcomes that result from predictions from those that result from postdictions.'"
        ),
        "notes": (
            "THE SOURCE THAT CLOSES THE GAP NAMED IN ROUND 8. The bibliography had nothing on "
            "exploratory-versus-confirmatory methodology, which is what blocked AUD-LABEL from "
            "being adjudicated at all.\n\n"
            "What it supplies is not a rule but a vocabulary distinction the audit already half-"
            "made: postdiction versus prediction, and the observation that the failure mode is not "
            "dishonesty but hindsight bias - 'the researcher's prediction is vague so that many "
            "possible outcomes can be rationalized after the fact as supporting the prediction'. "
            "That is precisely why 'controlled exploratory analysis with a fixed recorded design' "
            "is a coherent and honest category rather than a hedge, and why it is NOT equivalent "
            "to a confirmatory result.\n\n"
            "The paper's own remedy - define the research questions and analysis plan before "
            "observing outcomes - is the thing the AIEF repository did not do. AUD-LABEL says so "
            "plainly ('nothing in the repo was preregistered'), which is the correct disclosure; "
            "the literature makes clear that the disclosure costs the confirmatory interpretation "
            "and does not cost the exploratory one."
        ),
    },
    {
        "source_id": "LIT-0045",
        "title": "HARKing: Hypothesizing After the Results are Known",
        "authors": "Kerr, N. L.",
        "year": "1998",
        "venue": "Personality and Social Psychology Review 2(3), pp. 196-217",
        "venue_type": "journal",
        "identifiers": "DOI:10.1207/s15327957pspr0203_4",
        "canonical_url": "https://doi.org/10.1207/s15327957pspr0203_4",
        "retrieval_method": "web_search",
        "verification_level": "VERIFIED_METADATA",
        "relevance_domains": "L8",
        "bears_on_ids": "AUD-LABEL",
        "stance": "CAUTION",
        "excerpt": (
            "Personality and Social Psychology Review 2(3):196-217, 1998. Definition as recorded "
            "across independent citing works: presenting a post hoc hypothesis as if it were an a "
            "priori hypothesis. Abstract not read directly."
        ),
        "notes": (
            "The named failure mode that preregistration exists to prevent, and the reason the "
            "distinction matters operationally rather than decoratively. Citing works summarise it "
            "as: 'HARKing becomes problematic when exploratory findings are misleadingly presented "
            "as confirmatory' - which is the exact boundary AUD-LABEL is drawing.\n\n"
            "VERIFIED_METADATA only: the bibliographic record is confirmed consistently across "
            "several independent citing works, but the 1998 abstract was not opened. The content "
            "statement above therefore rests on how the field uses the term, not on the paper's "
            "own text - the same caveat LIT-0030 carried in round 3, and which round 4 had to "
            "correct. Flagged rather than glossed."
        ),
    },
]

# Appended to `notes` only. Never to a snapshot, never to an identity field.
REVERIFY = {
    "LIT-0041": (
        "ROUND 9 RE-VERIFICATION (abstract read directly at journals.aps.org, 2026-10-31; "
        "verification_level deliberately left at VERIFIED_METADATA and the snapshot left "
        "byte-identical): 'We explore both analytically and numerically an ensemble of coupled "
        "phase oscillators governed by a Kuramoto-type system... we have included the effects of "
        "time delay (due to finite signal-propagation speeds) and network plasticity (via dynamic "
        "coupling constants) inspired by the Hebbian learning rule in neuroscience... We "
        "investigate the formation of spatiotemporal patterns in both one- and two-dimensional "
        "oscillator LATTICES WITH PERIODIC BOUNDARY CONDITIONS and comment on the role of "
        "dimensionality.' MATERIAL REFINEMENT: the delay-plus-plasticity combination is prior art "
        "on REGULAR LATTICES, not on irregular adaptive networks. Round 7's claim that this "
        "supplies 'both of the things LIT-0040 lacks' stands, but the topology is regular and "
        "uniform-degree, so it does not close the structural part of the novelty residue."
    ),
    "LIT-0042": (
        "ROUND 9 RE-VERIFICATION (abstract read directly via PubMed 21517574, 2026-10-31; "
        "verification_level deliberately left at VERIFIED_METADATA and the snapshot left "
        "byte-identical): 'we investigate ALL-TO-ALL networks of nonidentical oscillators with "
        "adaptive coupling. The adaptation models spike-timing-dependent plasticity in which the "
        "sum of the weights of all incoming links is CONSERVED.' MATERIAL REFINEMENT: this is a "
        "genuinely conserved multiplicative adaptation - the real thing in Miller-MacKay's sense - "
        "on an all-to-all (uniform in-degree) network. AIEF's gate conserves nothing and runs on a "
        "hypergraph, so the two are further apart than the shared word 'normalisation' suggests."
    ),
}


def main() -> None:
    SNAP.mkdir(parents=True, exist_ok=True)
    with SRC.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    cols = COLS

    # --- snapshot integrity before we touch anything -------------------------
    for r in rows:
        actual = hashlib.sha256((ROOT / r["snapshot_file"]).read_bytes()).hexdigest()
        if actual != r["snapshot_sha256"]:
            raise SystemExit(f"pre-existing snapshot drift on {r['source_id']}")
    before = {r["source_id"]: {k: r[k] for k in IDENTITY_FIELDS} for r in rows}
    print(f"[pre] {len(rows)} snapshots verified, no drift")

    # --- 1. re-verification: notes only -------------------------------------
    by_id = {r["source_id"]: r for r in rows}
    for sid, text in REVERIFY.items():
        if sid not in by_id:
            raise SystemExit(f"re-verification targets unknown source {sid}")
        if "ROUND 9 RE-VERIFICATION" in by_id[sid]["notes"]:
            continue
        by_id[sid]["notes"] = by_id[sid]["notes"].rstrip() + "\n\n" + text
        print(f"  {sid}: re-verification appended to notes")

    # --- 2. new sources ------------------------------------------------------
    existing = [r for r in rows if r["round_added"] != "9"]
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
                "title": rec["title"], "authors": rec["authors"], "year": rec["year"],
                "venue": rec["venue"], "venue_type": rec["venue_type"],
                "identifiers": rec["identifiers"],
            },
            "verbatim_excerpt": rec["excerpt"],
            "excerpt_provenance": (
                "publisher landing page, abstract read directly"
                if rec["verification_level"] == "VERIFIED_FULL"
                else "bibliographic record confirmed across independent citing works; abstract not read"
            ),
        }
        blob = json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"
        (SNAP / snap_name).write_text(blob, encoding="utf-8")
        row = dict(rec)
        row.pop("excerpt")
        row["round_added"] = "9"
        row["retrieved_date"] = RETRIEVED
        row["snapshot_file"] = f"snapshots/{snap_name}"
        row["snapshot_sha256"] = hashlib.sha256(blob.encode("utf-8")).hexdigest()
        new_rows.append(row)
    rows = existing + new_rows

    with SRC.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in cols})
    print(f"added {len(new_rows)} sources -> total {len(rows)}")

    # --- 3. identity fields must be untouched --------------------------------
    after = {r["source_id"]: {k: r[k] for k in IDENTITY_FIELDS} for r in rows if r["source_id"] in before}
    if after != before:
        drift = [s for s in before if before[s] != after.get(s)]
        raise SystemExit(f"identity fields changed: {drift}")
    print("identity fields unchanged for all pre-existing sources")

    for r in rows:
        actual = hashlib.sha256((ROOT / r["snapshot_file"]).read_bytes()).hexdigest()
        if actual != r["snapshot_sha256"]:
            raise SystemExit(f"snapshot drift after write on {r['source_id']}")
    print(f"[post] {len(rows)} snapshots verified, no drift")

    # --- 4. mapping extension for the new claims -----------------------------
    EXTEND = {"LIT-0044": ["AUD-LABEL", "AUD-HELDOUT-LABEL"], "LIT-0045": ["AUD-LABEL"]}
    final = {r["source_id"]: r for r in rows}
    for sid, claims in EXTEND.items():
        if sid not in final:
            raise SystemExit(f"mapping targets unknown source {sid}")
        cur = [t.strip() for t in final[sid]["bears_on_ids"].split(";") if t.strip()]
        merged = sorted(set(cur) | set(claims))
        if merged != sorted(cur):
            final[sid]["bears_on_ids"] = ";".join(merged)
            print(f"  {sid}: bears_on -> {len(merged)} claims")
    with SRC.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in cols})

    aud = {t.strip() for r in rows for t in r["bears_on_ids"].split(";") if t.strip().startswith("AUD-")}
    print(f"AUD-* claims with >=1 source: {len(aud)} of 24")
    print("AUD-* without any source:",
          sorted(c for c in (r["claim_id"] for r in
                             csv.DictReader((ROOT / "baseline" / "claims.csv").open(encoding="utf-8")))
                 if c.startswith("AUD-") and c not in aud))


if __name__ == "__main__":
    main()
