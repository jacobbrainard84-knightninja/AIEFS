# Literature Review — Round 7: All Four Titles Were Wrong, and the Baseline Moves

**Round:** 7 · **Date:** 2026-10-31 · **New sources:** 4 (total **43**) · **Leads:** 4 resolved, **0 open**
**Registry:** [`SOURCES.csv`](SOURCES.csv) · [`ADJUDICATION.csv`](ADJUDICATION.csv) · [`baseline/`](baseline/) · **Prior:** [R1](ROUND_01_FINDINGS.md) · [R2](ROUND_02_FINDINGS.md) · [R3](ROUND_03_FINDINGS.md) · [R4](ROUND_04_FINDINGS.md) · [R5](ROUND_05_FINDINGS.md) · [R6](ROUND_06_FINDINGS.md)

---

## 0. Bottom line

Two things happened. The four prior-art leads were verified — and **every single title I wrote in
Round 6 was wrong.** Separately, the inbox was re-baselined off a 43-claim registry onto the
76-claim registry of record, which immediately caught two stale statuses that gate 8 had been
silently passing.

That title result is the round's most useful finding, because it is pure evidence for a rule the
inbox already had and I had been half-following.

---

## 1. F39 — Four leads, four wrong titles

Round 6 recorded four prior-art citations taken from the repository's own audit documents. I wrote a
`title_hint` for each from how the repository *described* the paper. Verification against publisher
records:

| Lead | Title I recorded in Round 6 | Actual title | Verdict |
|---|---|---|---|
| `LEAD-0008` | "Self-organization in networks of phase oscillators with Hebbian coupling" | **"Plasticity and learning in a network of coupled phase oscillators"** | wrong |
| `LEAD-0009` | "Delay-induced patterns / delay plus plasticity in adaptive oscillator networks" | **"Synchronization in phase-coupled Kuramoto oscillator networks with axonal delay and synaptic plasticity"** | wrong |
| `LEAD-0010` | "Conserved-coupling normalisation in adaptive networks" | **"Adaptive oscillator networks with conserved overall coupling: sequential firing and near-synchronized states"** | wrong |
| `LEAD-0011` | "Adding up the parts: multiplicative vs subtractive normalisation constraints in Hebbian learning" | **"The Role of Constraints in Hebbian Learning"** | **invented** |

`LEAD-0011` is the one to sit with. "Adding up the parts" is not a paraphrase and not a corruption of
anything in the repository — I manufactured a plausible-sounding subtitle and wrote it down as if it
were a citation. It survived a full round in the lead queue looking like a bibliographic record.

All four are now promoted with verified titles: [LIT-0040], [LIT-0041], [LIT-0042], [LIT-0043]. The
lead rows retain the wrong title in `title_hint` alongside the correction, so the error is auditable
rather than tidied away.

**The rule this vindicates:** a citation found inside a document is a prompt to go and find the
record, never a record. Round 4 already paid for this lesson with [LIT-0030]; Round 6 came within one
step of paying for it again with five citations at once.

---

## 2. F40 — What the prior-art cluster actually says about novelty

**[VERIFIED]** With all five sources in hand, the novelty picture is sharper — and narrower — than
either the repository or my earlier rounds had it.

**The residue is smaller than "minus delay and cap."** `AIEFS_salvage.md` characterises [LIT-0040]
as *"essentially AIEF minus delay and cap."* But [LIT-0041] is Kuramoto oscillators with **axonal
delay and synaptic plasticity** — it supplies both of the things [LIT-0040] was said to lack. So the
residue is not "AIEF minus delay and cap"; it is **AIEF minus delay, minus plasticity, minus
normalisation**, plus two specific mechanisms:

1. an **EMA of the delay-compensated phasor** as the adaptation driver;
2. a **min-endpoint hard capacity cap**.

That is a much smaller claim than the repository makes, and a much more defensible one, because it is
specific enough to be checked.

**[VERIFIED] [LIT-0043] is the sharpest source of the four, and it is not about novelty at all.** Its
result is that the *choice* of constraint changes the attractor: multiplicative enforcement converges
to the principal eigenvector of the unconstrained operator, while subtractive enforcement drives
almost every weight to a bound. That is a direct statement that the **form** of a normalisation is
load-bearing, which is exactly the territory `CF01`–`CF03` and `AUD-GATE` occupy.

`AIEFS_salvage.md` asserts multiplicative normalisation *"is exactly what produces the k·η/c rates."*
I have **not** verified that the AIEF capacity gate is multiplicative in Miller–MacKay's sense — the
gate is `s_i = min(1, c/(q_i + ε))`, a min-endpoint cap, which is arguably *neither* multiplicative
nor subtractive as those terms are defined there. [LIT-0043] therefore cuts both ways: it offers the
classical licence for the rate law if the mapping holds, and it makes the mapping a question nobody
has asked. Recorded as an open question, not a result.

---

## 3. F41 — Re-baseline: the adjudication now runs against 76 claims, not 43

The registry situation, restated because it governs every number in this inbox:

| File | `origin/main` | arena base branch | `integration/round5` |
|---|---|---|---|
| `registry/claims.csv` | **absent** | 43 | **76** |
| `registry/studies.csv` | absent | 14 | **15** |

The inbox protocol forbids editing `registry/`. So the registry of record is **pinned, not merged**:
[`baseline/`](baseline/) holds byte-exact copies of `claims.csv` (76 rows) and `studies.csv` (15 rows)
from `origin/integration/round5` @ `893e0b6`, with [`BASELINE.json`](baseline/BASELINE.json) recording
the source commit, sha256 of each file, row counts and the reason.

**Three consequences, all deliberate:**

1. **Gate 4** resolves `bears_on_ids` against the union of the local registry and the pinned baseline,
   failing closed only if neither is usable.
2. **Gate 8** takes claim IDs and `registry_status` from the **baseline**, because that is the registry
   of record.
3. **A new tamper check**: gate 4 now recomputes the sha256 of each pinned file and fails if it no
   longer matches `BASELINE.json`. The baseline is a snapshot; a snapshot that can be edited silently
   is not a snapshot.

### 3.1 The re-baseline immediately caught what gate 8 had been passing

The moment gate 8 switched source, it failed:

```
[8/8 adjudication] CF05: registry_status 'Frozen' != registry 'Supported'
[8/8 adjudication] EMP-AIEF14-02: registry_status 'Frozen' != registry 'Exploratory'
```

Two of the 25 adjudications had been carrying a status that changed upstream. They now read correctly
from the baseline. This is the first time in this project that a verifier failure was caused purely
by *improving the reference standard* rather than by a new error — which is the right reason to fail.

---

## 4. F42 — `AUD-NOVELTY` adjudicated: one half closed, one half unclosable

This was Round 5's "highest-value task left". It is now the 25th adjudication.

**Verdict: `SUPPORTED_WITH_SCOPE`** — and the split matters.

- **Half two — "the ingredients are prior art" — is closed.** Five verified sources, one per
  ingredient: [LIT-0040] plasticity, [LIT-0041] delay-plus-plasticity, [LIT-0042] conserved coupling,
  [LIT-0043] the constraint-choice result, [LIT-0039] the field review.
- **Half one — "novelty is not established either way" — cannot be closed by literature.** A search
  can never prove a negative, and the repository's own audit already said the search was not
  exhaustive.

**Proposed change (not applied):** split the row. The prior-art half moves from `Incomplete` to
`Supported` with the five sources attached. The novelty half stays `Incomplete` but should be
restated narrowly — *"no prior art was found for the specific combination"* — because "novelty is not
established either way" now **understates** what the literature says. The ingredients' prior-art
status *is* established.

---

## 5. F43 — The Physics Reports record is confirmed; the snapshot is deliberately not amended

[LIT-0039] was recorded in Round 6 from the arXiv record, with the journal version cited only
second-hand from the repository. It is now independently confirmed:

**Berner, Gross, Kuehn, Kurths & Yanchuk, "Adaptive dynamical networks", *Physics Reports* 1031
(10 August 2023), pp. 1–59, DOI `10.1016/j.physrep.2023.08.001`** — consistent across the publisher
listing, the institutional repositories (UCC, PIK) and independent citing works.

**The `LIT-0039` row is not amended.** Rewriting it would change its snapshot hash and silently
invalidate the tamper-evidence chain for a cosmetic improvement. The CSV continues to carry the arXiv
identifier as primary and this section is the record that the journal DOI is verified. A future round
may add the journal version as a separate source if a distinct row is wanted.

---

## 6. State

| Measure | R1 | R2 | R3 | R4 | R5 | R6 | **R7** |
|---|---|---|---|---|---|---|---|
| Sources | 16 | 28 | 33 | 38 | 38 | 39 | **43** |
| Open leads | 3 | 3 | 1 | 0 | 0 | 4 | **0** |
| Claims adjudicated | 0 | 0 | 0 | 0 | 24 | 24 | **25** |
| Adjudication baseline | 43 | 43 | 43 | 43 | 43 | 43 | **76** |
| Claims with ≥1 source | 19/43 | 22/43 | 24/43 | 24/43 | 24/43 | 24/43 | **25/76** |
| Studies with ≥1 source | 9/14 | 11/14 | 11/14 | 11/14 | 11/14 | 11/14 | **11/15** |
| Verifier gates | 7 | 7 | 7 | 7 | 8 | 8 | **8** |

Verdict mix across 25: 6 `SUPPORTED`, 6 `SUPPORTED_WITH_SCOPE`, 2 `CONTEXT_ONLY`, 6
`VALIDATED_RETIREMENT`, 5 `VALIDATED_REJECTION`, **0 `BOUNDED`**. Mapping health: 22 `COMPLETE`,
2 `INCOMPLETE`, 1 `WRONG`.

**Relative to the old figure, coverage reads worse (24/43 → 25/76) because the denominator became
honest.** That is the correct direction of travel and it is the same principle as the lead queue
filling in Round 6.

### Remaining unmapped studies (4 of 15)

`HISTORICAL_PROJECT_ORIGINS`, `AIEF_1_4_PIVOT_PILOT`, `AIEF_1_4_PROPOSAL_EQUALIZATION`,
`AI_AGENT_AUDITS_2026_10` — the last of which matters, because it owns 24 audit claims and the
`SSRH-ORIG-*` origin hypotheses.

---

## 7. What Round 7 did not do

- Did not edit `registry/`. The baseline is a pinned copy, and gate 4 now enforces that it stays byte-exact.
- Did not amend the `LIT-0039` snapshot despite having a better record (§5).
- Did not read the [LIT-0041] or [LIT-0042] abstracts — both remain `VERIFIED_METADATA`, and their notes
  stop at what the titles assert.
- Did not adjudicate the 24 `AUD-*` claims beyond `AUD-NOVELTY`, nor the 7 `SSRH-ORIG-*` claims.
- Did not verify that the AIEF capacity gate is multiplicative in the [LIT-0043] sense (§2).
