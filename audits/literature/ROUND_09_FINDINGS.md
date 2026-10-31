# Literature Review — Round 9: The Gate Settled From Code, and the Gap Closed

**Round:** 9 · **Date:** 2026-10-31 · **New sources:** 2 (total **45**) · **Adjudications:** 47 (23/24 `AUD-*`)
**Registry:** [`SOURCES.csv`](SOURCES.csv) · [`ADJUDICATION.csv`](ADJUDICATION.csv) · [`baseline/`](baseline/) · **Prior:** [R1](ROUND_01_FINDINGS.md) · [R2](ROUND_02_FINDINGS.md) · [R3](ROUND_03_FINDINGS.md) · [R4](ROUND_04_FINDINGS.md) · [R5](ROUND_05_FINDINGS.md) · [R6](ROUND_06_FINDINGS.md) · [R7](ROUND_07_FINDINGS.md) · [R8](ROUND_08_FINDINGS.md)

---

## 0. Bottom line

Three things, and one of them reverses how I framed the novelty question in Round 7.

1. **The gate question from Round 8 is settled — from the code, not from argument** (§1). The gate is
   neither of Miller & MacKay's enforcement methods, and their convergence theorem provably does not
   apply to it.
2. **The last named literature gap is closed** (§3). `AUD-LABEL` is adjudicated.
3. **The prior-art cluster shares a structural precondition that AIEF violates** (§4). That turns the
   novelty residue from "embarrassingly small" into "structurally distinct", which is the opposite of
   where Round 7 left it.

---

## 1. F50 — The gate, settled: per-edge, not global, so the theorem does not apply

Round 8 said `AUD-GATE`'s phrase "multiplicative normalisation" was probably wrong. It is now settled
by reading the implementation rather than by inference.

`AIEF_1_3_falsification_updated.py:446-447`:

```python
scale = np.minimum(1.0, cap / (row_sum_pre + ZERO_TOL))
B *= np.minimum.outer(scale, scale)
```

Each **edge** is multiplied by the **minimum of two node-specific factors**. Compare [LIT-0043]'s two
methods:

| | factor applied | preserves direction of **B**? | Miller & MacKay's result |
|---|---|---|---|
| multiplicative | one **global** factor for all weights | **yes** | converges to the principal eigenvector |
| subtractive | subtract a constant | no | drives nearly all weights to a bound |
| **AIEF gate** | **per-edge** `min(scale_i, scale_j)` | **no** | **not established by that paper** |

The direction of **B** changes, because different edges get different factors. Miller & MacKay's
theorem is a statement *about* the global-rescale case; it cannot be transferred to a per-edge map.
**The theorem does not apply.**

The label is therefore **half defensible and misleading in the half that matters**: weights *are*
multiplied (so "multiplicative" is true in the trivial sense of "not additive"), and the scale *is*
derived from node strength — but "multiplicative" in [LIT-0043] names a specific property (a single
common factor) whose consequence is the principal-eigenvector convergence. Using the word for a map
that lacks that property is the same class of error as `ERRATA` E6's "cycle kernel": correct
arithmetic under a name belonging to a different object.

**Consequence for two other claims.** `AIEFS_salvage.md` asserts that multiplicative normalisation
"is exactly what produces the k·η/c rates". Under this reading that is **unsupported as stated**. The
rate law itself is verified to 2.1e-8 and is not in doubt — what is unsupported is the *derivation*
narrative. `AUD-RATELAW` and `AUD-KAPPA-TW` are both annotated accordingly: correct results, no cited
mechanism.

**And it is testable in an afternoon**, which is why I put it first in the roadmap: run
global-multiplicative, subtractive, and this per-edge cap on one small network with identical
parameters and compare which attractor each selects. If the per-edge cap lands somewhere neither of
the other two does, the three-way distinction is demonstrated rather than asserted. That is a
numerical experiment and belongs outside this inbox.

---

## 2. F51 — What the gate *is*, positively

Worth stating, because "not Miller–MacKay" is a negative characterisation and the claim deserves a
positive one.

The map enforces `row_sum_i ≤ cap` for every node by scaling each edge by the smaller of its two
endpoint factors. It is:

- **idempotent** on the feasible set (all scales are 1 when no row violates), which the claim already
  asserts and which the code confirms;
- a **feasibility restoration**, not a projection in any metric — matching the claim's own no-go;
- **not conservative**: no total is preserved, unlike [LIT-0042], where "the sum of the weights of all
  incoming links is conserved";
- **edge-symmetric**: `min(scale_i, scale_j)` keeps **B** symmetric, which a per-node scaling would
  not.

That last property is probably the reason for the `min` form, and it is a real design choice worth
recording. "Per-edge symmetric capped admissibility scaling" describes the object; the current name
describes a different one.

---

## 3. F52 — The named gap is closed: `AUD-LABEL` adjudicated

Round 8 named one precise hole: no source on exploratory-versus-confirmatory methodology, which is
what made `AUD-LABEL` unadjudicable. Closed with two sources.

**[LIT-0044] Nosek, Ebersole, DeHaven & Mellor (2018), *The preregistration revolution*, PNAS
115(11):2600–2606** — `VERIFIED_FULL`, abstract read directly. The distinction it draws is
*postdiction* versus *prediction*, and the point that matters for this repository is *why* the two
get confused:

> "Mistaking generation of postdictions with testing of predictions reduces the credibility of
> research findings. However, ordinary biases in human reasoning, such as hindsight bias, make it
> hard to avoid this mistake. ... A common case is when the researcher's prediction is vague so that
> many possible outcomes can be rationalized after the fact as supporting the prediction."

That is the mechanism by which "we found X" quietly becomes "we predicted X". It is not dishonesty;
it is hindsight bias operating on a vague prior. Which is exactly why "controlled exploratory
analysis with a fixed recorded design" is a **coherent and honest category** — and why it is not
equivalent to a confirmatory result.

**[LIT-0045] Kerr (1998), *HARKing: Hypothesizing After the Results are Known*, PSPR 2(3):196–217** —
`VERIFIED_METADATA`, the named failure mode the label is avoiding.

**Verdict: `SUPPORTED`.** The claim does the *opposite* of HARKing — it discloses the absence of
preregistration — and the literature says that disclosure costs the confirmatory interpretation while
leaving the exploratory one intact. The repository made the right trade, explicitly, in writing.

**The consequence the claim should state:** no result in this repository may be described as
confirmatory, and "fixed recorded design" does not substitute for preregistration, because a design
recorded before analysis is still recorded after the data-generating choices were made.

---

## 4. F53 — The prior-art cluster shares a precondition AIEF violates

This reverses Round 7's framing, and the reversal comes from reading two abstracts I had not read.

| Source | Topology in the model |
|---|---|
| [LIT-0041] Timms & English | **1D and 2D lattices with periodic boundary conditions** |
| [LIT-0042] Picallo & Riecke | **all-to-all** networks |
| [LIT-0030] Earl & Strogatz | any network **in which each oscillator receives from *k* others, *k* uniform** |
| [LIT-0040] Seliger et al. | generalised Kuramoto with slowly varying coupling; topology not restricted in the abstract |
| [LIT-0043] Miller & MacKay | neural population model, not a spatial network |
| [LIT-0039] Berner et al. | the review of the whole class |

**Three of the four specific dynamical models are regular**: lattices, all-to-all, and uniform
in-degree. The AIEF network is an adaptive hypergraph with time-varying degree, per-node capacity
caps, and a `shuffle_R` intervention that destroys alignment structure without preserving degree
sequence.

So Round 7's conclusion — that [LIT-0041] "supplies both of the things [LIT-0040] was said to lack",
shrinking the residue to two mechanisms — **was reading the titles, not the models.** The
delay-plus-plasticity combination is prior art *on regular topologies*. It is not prior art on an
irregular adaptive network with per-node caps.

**The residue is therefore structural, not mechanistic**, and that is a better position than a
two-item list. AIEF's defensible claim is not "delay + plasticity + cap" (all prior art) but:

> an adaptive Kuramoto network whose coupling is a **capacity-capped, degree-irregular hypergraph**
> driven by an EMA of the delay-compensated phasor, evaluated by **interventional ablation** rather
> than by predictability.

The last clause is the strongest, and it is the one the literature supports most directly: [LIT-0025]
gives the formal reason the matched-phase design is necessary, and `EMP-AIEF13-01`'s design is an
intervention, not an observational causal metric.

**Stated with its limit:** I have read abstracts, not full texts. A specific-model search inside
[LIT-0039]'s 120 pages could well find an irregular adaptive network example that narrows this again.
This is a better-founded claim than Round 7's, not a final one.

---

## 5. F54 — The re-verification policy, and why it differs from Round 4

Reading the [LIT-0041] and [LIT-0042] abstracts adds evidence. It does not contradict anything
recorded. So:

- the **snapshot stays byte-identical** and `verification_level` stays `VERIFIED_METADATA`;
- the new reading is appended to the source's **`notes`** field, with the excerpt quoted verbatim.

Round 4 did the opposite-looking thing — it refused to rewrite [LIT-0030]'s snapshot and put the
correction in prose. Both decisions follow one rule: **the frozen record is never rewritten; new
evidence goes where new evidence goes.** Round 4's change was a *correction to an attribution*, which
would have made the record disagree with itself. Here the record was never wrong — it said "abstract
not read", which was true, and now the abstract has been read.

The builder enforces this rather than trusting it: it verifies all 45 snapshot SHA-256s before and
after, and asserts that no identity field changed for any pre-existing source. Only `notes` and
`bears_on_ids` are writable, and `bears_on_ids` only grows.

The cost is visible: `verification_level` now *understates* two sources. I would rather have an
auditable trail than a tidier field, and the notes carry the truth.

---

## 6. Proposed registry amendments — **for owner approval, not applied**

| # | Target | Change | Sev |
|---|---|---|---|
| 1 | `AUD-GATE` | Rename to "per-edge symmetric capped admissibility scaling". State that the factor is per-edge so **B**'s direction is not preserved and [LIT-0043]'s convergence theorem is inapplicable. Keep the no-go verbatim | **HIGH** |
| 2 | `AUD-RATELAW`, `AUD-KAPPA-TW` | Record that the `k·η/c` derivation has **no cited mechanism**; the result stands, the explanation does not ([LIT-0043] does not license it) | **HIGH** |
| 3 | `AUD-LABEL` | Attach [LIT-0044]/[LIT-0045] and state the consequence: nothing here is confirmatory, and "fixed recorded design" ≠ preregistration | MED |
| 4 | `AUD-NOVELTY` | Restate the residue as **structural** (§4) rather than a three-ingredient subtraction. This is a *narrowing*, not a broadening | MED |
| 5 | `AUD-DELAY` | Note that the delay literature it is compared against is largely lattice/all-to-all, so a delay effect on a hypergraph is not directly comparable | LOW |
| 6 | `AUD-V4-RECOVERY-WORDING` | Leave unsourced — it is a statement about what a local function returns, and no bibliography can attest it | — |

---

## 7. State

| Measure | R6 | R7 | R8 | **R9** |
|---|---|---|---|---|
| Sources | 39 | 43 | 43 | **45** |
| Adjudicated | 24 | 25 | 46 | **47** |
| Claims with ≥1 source | 24/43 | 25/76 | 46/76 | **47/76** |
| `AUD-*` with ≥1 source | 0/24 | 1/24 | 22/24 | **23/24** |
| `AUD-*` adjudicated | 0/24 | 1/24 | 22/24 | **23/24** |
| Verifier gates | 8 | 8 | 8 | **8** |

`AUD-V4-RECOVERY-WORDING` is the single `AUD-*` claim without a source and without an adjudication,
and that is correct.

## 8. What Round 9 did not do

- Did not touch a snapshot or a `verification_level`, deliberately (§5).
- Did not run the three-way gate experiment. Naming is a registry edit; demonstrating the three
  attractor classes is a numerical study, and it belongs outside this inbox.
- Did not read [LIT-0045]'s abstract — it stays `VERIFIED_METADATA` with that stated in its notes.
- Did not open [LIT-0039]'s 120 pages to test §4's claim.
- Did not adjudicate the 7 `SSRH-ORIG-*` claims; that remains an owner scope decision.
