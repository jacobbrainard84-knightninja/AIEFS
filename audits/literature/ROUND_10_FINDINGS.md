# Literature Review — Round 10: The Gate Measured

**Round:** 10 · **Date:** 2026-10-31 · **New sources:** 0 · **Adjudications:** 47
**Experiment:** [`audits/experiments/gate_form/`](../experiments/gate_form/REPORT.md)
**Prior:** [R1](ROUND_01_FINDINGS.md) · [R2](ROUND_02_FINDINGS.md) · [R3](ROUND_03_FINDINGS.md) · [R4](ROUND_04_FINDINGS.md) · [R5](ROUND_05_FINDINGS.md) · [R6](ROUND_06_FINDINGS.md) · [R7](ROUND_07_FINDINGS.md) · [R8](ROUND_08_FINDINGS.md) · [R9](ROUND_09_FINDINGS.md)

---

## 0. Why this round exists, and why it is not a literature round

Round 9 concluded from code that the capacity gate is not [LIT-0043]'s multiplicative enforcement, so
Miller & MacKay's convergence theorem cannot apply to it. That was an inference from reading two
lines. It is checkable, so I checked it.

**This round adds no sources.** It closes the loop on one: the question was raised by [LIT-0043], and
the answer is a measurement rather than a citation. Everything here is recorded in the literature
inbox because that is where the question lives, but the work happened in
[`audits/experiments/gate_form/`](../experiments/gate_form/REPORT.md) and that directory is where the
evidence is.

Per the standing rule that scientific work stays separate from organisational work: **no registry row
was edited, no engine file was touched.** `AIEF_1_3_falsification_updated.py` was read only. The
experiment is a new directory containing a script, a JSON result and a report.

---

## 1. F55 — The gate is not multiplicative, and it is now measured rather than argued

Miller & MacKay's argument rests on a single property: their multiplicative rule rescales the whole
weight vector by **one common factor**, so direction is preserved and the dynamics converge to the
principal eigenvector of the unconstrained operator. The AIEF gate applies a **per-edge** factor.

So: apply each rule to 200 random symmetric matrices with a row-sum violation and measure the angle
between `vec(B)` and `vec(B')`. Zero means exactly proportional — i.e. the rule is a rescaling and
their theorem has purchase.

| rule | distinct per-edge factors | `sin θ` median | exactly proportional |
|---|---:|---:|---:|
| global multiplicative | **1** | `3.1e-16` | **200 / 200** |
| AIEF per-edge cap | **11** | `1.0e-01` | **0 / 200** |
| subtractive | 11–27 | `7.2e-01` | **0 / 200** |

All three satisfy the capacity constraint afterwards in every trial, so the comparison is fair — they
differ only in how they restore feasibility.

The global rule's residual of `3e-16` is floating-point zero. The AIEF gate lands about six degrees
away; subtractive about forty-six.

**This settles the question.** `AUD-GATE`'s sentence — "node-strength multiplicative normalisation" —
is false as a statement about [LIT-0043]'s term. The gate multiplies rather than adds, and the factor
does derive from node strength, so the phrase is *half* defensible; but it is not **a** factor, and
single-factor-ness is exactly what the theorem consumes. The error is a borrowed name, the same class
as `ERRATA` E6's "cycle kernel", and it survived nine rounds of reading because the arithmetic is
correct under either name.

Eleven distinct factors for twelve nodes is what the `min` form predicts: the scales are per-node, and
`min(s_i, s_j)` across symmetric edges collapses them to roughly one value per node.

---

## 2. F56 — The rules are distinguishable but not orderable

Swapping **only** the enforcement rule, with seed, ω, delay and every other constant fixed:

| seed | global multiplicative | subtractive | AIEF per-edge cap |
|---|---:|---:|---:|
| 11 | r = 0.602 | r = 0.308 | **r = 0.977** |
| 22 | r = 0.276 | **r = 0.638** | r = 0.541 |
| 33 | r = 0.517 | r = 0.662 | **r = 0.679** |

Final coupling matrices differ by a relative Frobenius gap of **0.60–0.73**, and cluster partitions
match in only **3 of 9** pairwise comparisons. The enforcement geometry reaches the attractor.

**But it does not order them.** Mean `r` is 0.73 / 0.54 / 0.47 for per-edge / subtractive / global, and
the per-edge rule is ranked first in seeds 11 and 33 and second in seed 22 (`[1, 2, 1]`). Three seeds
cannot support an ordering, and **the mean should not be quoted** — it is a summary of a
non-monotone pattern, which is exactly the kind of number this inbox has spent nine rounds criticising
elsewhere.

Writing down the mean and not the ranks would have been the easy version of this round.

---

## 3. F57 — What the measurement licenses, and what it does not

**Licensed:**
- The gate is not [LIT-0043] multiplicative. Measured, 200/200 vs 0/200.
- [LIT-0043]'s convergence theorem does not apply to it.
- `AUD-RATELAW`'s `k·η/c` rate law therefore has **no cited mechanism** — not "a mechanism I have not
  found", but one that is positively excluded by the form of the gate. The result itself is untouched:
  it is verified to `2.1e-8` and was never in question.
- Swapping the enforcement rule changes the selected state in this model.

**Not licensed:**
- That the AIEF engine's attractors differ under the three rules. `T_SIM` was 200 against the engine's
  800, support was all-to-all rather than the repository's hypergraph, and the replica is 12 nodes of
  pure Python. **Part A survives that scoping because it is a property of the map; Part B does not.**
- Any claim that one rule synchronizes better. See §2.

A useful fact fell out unasked: the gate binds on **17,744–17,784 of 20,000 steps** (89%) and the
final maximum row sum equals `cap = 0.633333` exactly under every rule. The constraint is active
almost always, so this is not a corner case — which makes the naming defect more consequential, not
less.

---

## 4. F58 — The three amendments, now evidence-backed

Rounds 8 and 9 proposed these on the strength of reading. Round 10 supplies the measurement.

| # | Target | Change | Evidence |
|---|---|---|---|
| 1 | `AUD-GATE` | Rename to "per-edge symmetric capped admissibility scaling". State that the factor is per-edge, so **B**'s direction is not preserved and [LIT-0043] is inapplicable. Keep the no-go verbatim | 200/200 vs 0/200 (§1) |
| 2 | `AUD-RATELAW`, `AUD-KAPPA-TW` | The `k·η/c` derivation has **no cited mechanism**; the gate's form positively excludes [LIT-0043]'s | 11 factors vs 1 (§1) |
| 3 | `AUD-DELAY` | Note the delay literature it is compared against is largely lattice / all-to-all | §2's scoping |

Amendment 2 is the one with teeth. "Unsupported as stated" was already in the round-9 record; the
difference now is that it is not a gap to be filled by finding the right paper. **No paper will
supply that mechanism, because the mechanism requires a property the gate does not have.** The rate
law needs its own derivation, or its rationale needs restating as empirical regularity rather than as
consequence of normalisation.

---

## 5. State

| Measure | R7 | R8 | R9 | **R10** |
|---|---|---|---|---|
| Sources | 43 | 43 | 45 | **45** |
| Adjudicated | 25 | 46 | 47 | **47** |
| Claims with ≥1 source | 25/76 | 46/76 | 47/76 | **47/76** |
| `AUD-*` adjudicated | 1/24 | 22/24 | 23/24 | **23/24** |
| Open leads | 0 | 0 | 0 | **0** |
| Verifier gates | 8 | 8 | 8 | **8** |

`results.json` is pinned by SHA-256 in `ROUND_STATE.json`, on the same principle as the registry
baseline: a number quoted in a findings document should be checkable against the bytes that produced
it.

---

## 6. What Round 10 did not do

- Added no sources, and did not search. The question was answerable from what was already recorded.
- Did not touch `registry/`, the engine, or any frozen file.
- Did not run the three-way comparison against the real engine — the obvious next step, and an
  engineering task rather than a replica's.
- Did not establish any ordering of synchronization strength, and says so in §2 rather than quoting
  a mean that looks cleaner than the data.
