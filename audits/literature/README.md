# Literature Inbox — protocol for any bot

An append-only, machine-verifiable literature register for the AIEFS project.

**Purpose.** Keep a continuously growing map from external published work to the specific claims,
studies and artefacts asserted in this repository — such that every citation is checkable by a
third party without trusting the bot that wrote it.

**Status.** Round 1 complete. Next round: see [`ROUND_STATE.json`](ROUND_STATE.json).

---

## 1. The one rule

> **Nothing enters `SOURCES.csv` from memory.**

A bibliographic record either came from a retrieval performed in the current session, or it is a
lead. There is no third option, and there is no "everyone knows this paper" exemption.

This rule exists because the dominant failure mode of a literature bot is a plausible, confidently
formatted, non-existent citation. It is unfalsifiable by reading and therefore poisons everything
downstream. The snapshot mechanism below is what makes the rule enforceable.

---

## 2. Files

| File | Mutability | Contents |
|---|---|---|
| `SOURCES.csv` | **append-only** | Master register. One row per verified source. |
| `LEADS.csv` | append-only | Retrieved-but-**not-citable** items. Carries `status` (`OPEN`/`RESOLVED`) and `resolved_as`, so a promoted lead is visibly retired rather than left looking open. |
| `snapshots/<source_id>.json` | **immutable** | Hashed evidence record: bibliographic fields, verbatim excerpt, retrieval method, provenance of the excerpt. |
| `ROUND_0N_FINDINGS.md` | append-only | Narrative findings for round N, with `[LIT-xxxx]` citations. |
| `ROUND_STATE.json` | mutable | Resume state and forward roadmap. |
| `verify_literature.py` | rarely | The seven gates. Stdlib only. |
| `_build_roundNN.py` | one per round | Generator that produced that round's snapshots and CSV rows. Kept for reproducibility, and **must be idempotent** — it drops and rebuilds only its own round, so a rerun cannot duplicate rows. |

---

## 3. Verification levels

Set at retrieval time. This is a claim about **how much** the retrieval supports, not about the
quality of the paper.

| Level | Retrieval | May be cited for |
|---|---|---|
| `VERIFIED_FULL` | Canonical landing page opened (`fetch_page`). | Bibliographic record **and** the abstract's substantive content. |
| `VERIFIED_METADATA` | Complete record confirmed from a search-index rendering of the canonical page (`web_search`). | Bibliographic record. The *abstract wording* is quoted from the index, not the publisher's render. |
| `SEARCH_SNIPPET_ONLY` | Everything else. | **Nothing.** Goes to `LEADS.csv`. |

Two hard consequences, both learned the hard way in Round 1:

- **No paywalled full text ⇒ no numbered-theorem claims.** If the abstract is the ceiling, phrase
  the citation as "the abstract states X", never "Theorem 3.2 proves X".
- **A 2026 preprint with no venue is still citable** as a preprint. Its *peer-review status* must be
  stated. Do not silently upgrade an arXiv id to a journal citation.

---

## 4. Snapshot integrity — why the hashes matter

Each snapshot is a JSON file whose SHA-256 is recorded in `SOURCES.csv`. This buys three things:

1. **Tamper evidence.** A later bot cannot quietly edit a bibliographic record or an excerpt
   without breaking the hash. `verify_literature.py` catches it.
2. **Link rot resistance.** If the URL dies, the record survives in-repo with its provenance.
3. **Excerpt provenance.** Every snapshot states whether the excerpt came from the page itself or
   from a search-index rendering. A reviewer can therefore tell a primary read from a secondary one.

Snapshots contain a **verbatim excerpt only** — never a full-text copy. Quotation for verification
is fair use; mirroring a publisher's PDF into a repository is not. Keep excerpts to the minimum
needed to justify the claim.

---

## 5. The stance field

The reason this register exists is adjudication, not accumulation. Every source must declare its
relation to the repository's claims:

| Stance | Means | Typical consequence |
|---|---|---|
| `SUPPORTS` | Independent literature reaches the same conclusion. | Strengthens the claim; may allow promotion. |
| `CONTRADICTS` | **Would falsify a repo claim.** | Triggers a registry review. Highest priority. |
| `CAUTION` | Does not dispute the claim but bounds what it may assert. | Scope note added to the claim. |
| `METHOD` | Supplies the technique or formal frame. | Enables a stronger restatement. |
| `CONTEXT` | Situates without adjudicating. | Novelty-boundary discussion. |

A round that adds only `SUPPORTS` and `CONTEXT` rows has not done its job. **The valuable rounds
produce `CONTRADICTS` and `CAUTION` rows**, because those are the only ones that can change a
status in `registry/claims.csv`.

---

## 6. The `bears_on_ids` field

Comma-free, semicolon-separated tokens, each of which **must resolve** to:

- a `claim_id` in `../registry/claims.csv`, or
- a `study_id` in `../registry/studies.csv`.

Gate 4 enforces this. The point is structural: **a citation may not be attached to a claim that
does not exist.** This prevents the classic drift where a bot cites literature against a claim that
was retired three rounds ago. If the claim you want to attach to is not in the registry, either it
isn't a claim, or the registry is missing something — say so explicitly, don't invent an ID.

---

## 7. Running a round — the full procedure

```bash
cd <repo root>

# 0. Recover state
python audits/literature/verify_literature.py        # must PASS before you start
cat audits/literature/ROUND_STATE.json              # next_round + roadmap

# 1. Retrieve. Never write a citation before retrieving the record.
#    fetch_page on the canonical page (arXiv abs / DOI landing) is the gold standard.
#    web_search is acceptable when the result itself carries the full record.

# 2. Record. Add a _build_roundNN.py following the Round 1 template:
#    one dict per source with title, authors, year, venue, identifiers, url,
#    retrieval_method, verification_level, domains, bears_on_ids, stance,
#    excerpt, notes.  Then:  python audits/literature/_build_roundNN.py

# 3. Write ROUND_0N_FINDINGS.md. Cite every new source at least once as [LIT-xxxx].
#    Tag substantive statements [VERIFIED] / [INFERRED] / [SUSPICION].

# 4. Update ROUND_STATE.json (last_round_completed, next_round, total_sources,
#    sources_per_round, open_leads, roadmap for the following round).

# 5. Gate.
python audits/literature/verify_literature.py        # must PASS (8/8)

# 6. Commit. Never amend or renumber an existing row.
```

### Two lessons from Round 2

1. **Make the builder idempotent.** The round-2 builder originally blind-appended, which meant a
   correction to a row would have produced a duplicate. It now filters out its own round before
   rebuilding. Any round that needs a fix after the fact should be re-runnable.
2. **Retire leads explicitly.** A lead that is silently resolved looks identical to one that was
   forgotten. `status` + `resolved_as` make the difference machine-checkable.

### Absolute prohibitions

- **Never renumber, reuse, or delete a `source_id`.** The ID is a permanent handle; findings from
  prior rounds cite it.
- **Never edit a snapshot.** Superseding evidence gets a *new* `source_id` with a note pointing at
  the old one.
- **Never cite a `LEAD-xxxx`.** Promote it first.
- **Never upgrade a verification level after the fact.** If a lead is later verified, it becomes a
  new `LIT-` row carrying the higher level.
- **Never modify `registry/`.** Propose amendments in the findings file (§4 of each round) for owner
  approval. The literature layer observes the registry; it does not write to it.

---

## 8. The seven gates

`verify_literature.py` — stdlib only, no venv, no network. Exit 0 required before commit.

| Gate | Checks |
|---|---|
| `1/7 schema` | Exact header; `LIT-\d{4}`; dense ordered IDs from `LIT-0001`; no empty required fields |
| `2/7 vocabulary` | `verification_level`, `stance`, `venue_type`, `relevance_domains`, `retrieval_method` all in the documented sets; `https://` URLs |
| `3/7 snapshots` | File exists; SHA-256 matches CSV; embedded title/authors/year agree with the row; excerpt non-empty |
| `4/7 registry linkage` | Every `bears_on_ids` token resolves in `registry/claims.csv` or `registry/studies.csv` |
| `5/7 findings coverage` | Every `[LIT-xxxx]` in a findings file exists; every source added in round N is cited in `ROUND_0N_FINDINGS.md` |
| `6/7 leads` | No `LEAD-` cited as a source; every lead has a `next_action` and a `status` in {`OPEN`,`RESOLVED`}; `RESOLVED` must point at a real source, `OPEN` must carry no pointer |
| `7/7 state` | `ROUND_STATE.json` parses; `next_round == last_round_completed + 1`; per-round counts match the CSV |

Gate 5 is what prevents a bibliography from becoming decorative: an uncited source fails the build.

---

## 9. Domain map

| ID | Domain | Bears on |
|---|---|---|
| `L1` | Delay-coupled & adaptive network synchronization | AIEF 1.0–1.3 core, `T_window` |
| `L2` | Causal ablation statistics, pseudoreplication, cluster bootstrap | `EMP-AIEF13-*`, `REJ-COHORT-05` |
| `L3` | DDE state space, history functionals, delay cocycles | `AIEF_1_4_TANGENT_AND_COCYCLE` |
| `L4` | Non-autonomous cocycles, Lyapunov spectrum, inertial manifolds | tangent/cocycle rate claims |
| `L5` | Koopman, spectral submanifolds, DMD limitations | `REJ-SPEC-01`, `S09`, `S16` |
| `L6` | Incidence matrix rank, cycle space, algebraic graph theory | `LEAN-CF-01`, `C1`–`C3` |
| `L7` | Non-normality, pseudospectra, nonsmooth/active-set analysis | `REJ-SPEC-02`, `CAVEAT-MS-8.4`, `CF08` |
| `L8` | Floating-point reproducibility, summation, CI gating | `IMPL-MODULAR-01`, Stage 7 CI |

`L4` is **entirely uncovered** after Round 1 — no source maps to a cocycle/Lyapunov reference
because Arnold (1998) could not be verified in-session. That is the single largest gap in the map
and the first target of Round 2.

---

## 10. Boundary of the claim

This inbox makes a narrow promise: *for each listed source, the record is real, was retrieved, and
is hashed.* It does **not** promise that the field map is complete, that the cited abstracts are a
fair summary of the papers, or that the literature search is unbiased. Recall is search-limited and
stated as a gap. Any bot continuing this work should assume the map has holes and look for them
rather than build on it as authoritative.
