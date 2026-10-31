# Literature Review — Round 8: The Audit Corpus, Adjudicated

**Round:** 8 · **Date:** 2026-10-31 · **New sources:** 0 · **Adjudications:** 46 total (was 25)
**Registry:** [`ADJUDICATION.csv`](ADJUDICATION.csv) · [`baseline/`](baseline/) · **Prior:** [R1](ROUND_01_FINDINGS.md) · [R2](ROUND_02_FINDINGS.md) · [R3](ROUND_03_FINDINGS.md) · [R4](ROUND_04_FINDINGS.md) · [R5](ROUND_05_FINDINGS.md) · [R6](ROUND_06_FINDINGS.md) · [R7](ROUND_07_FINDINGS.md)

---

## 0. Bottom line

22 of the 24 `AUD-*` claims are now adjudicated. **None is refuted.** Five are `SUPPORTED`
outright, fifteen `SUPPORTED_WITH_SCOPE`, one `CONTEXT_ONLY`, one validated rejection.

Three findings are high-severity, and none of them is about the science being wrong:

1. **`AUD-GATE` is using Miller & MacKay's term for an object their paper defines differently** —
   which matters because their entire result is that the choice of enforcement determines the
   attractor (§2).
2. **`AUD-MODULAR-ORACLE` has a policy consequence the claim does not draw**: a certification test
   skipped by default does not satisfy ACM's "exercisable" criterion (§3).
3. **`AUD-TIMESTEP` is a bigger gap than it reads** — for a DDE, a timestep study is a convergence
   analysis of the solution map, not a truncation-error check (§4).

Round 8 adds **no sources**. Everything here was already in the bibliography; what was missing was
the mapping and the reading.

---

## 1. F44 — The adjudication result

| | n |
|---|---:|
| `SUPPORTED` | 11 |
| `SUPPORTED_WITH_SCOPE` | 20 |
| `CONTEXT_ONLY` | 3 |
| `VALIDATED_RETIREMENT` | 6 |
| `VALIDATED_REJECTION` | 6 |
| `BOUNDED` | **0** |

Of the 22 `AUD-*` rows: 5 `SUPPORTED`, 15 `SUPPORTED_WITH_SCOPE`, 1 `CONTEXT_ONLY`, 1
`VALIDATED_REJECTION`.

Coverage moved without a single new source: **claims with ≥1 source went 25/76 → 46/76**, because
`bears_on_ids` is a living mapping and I had never extended it to the audit claims.

`BOUNDED` stayed unused for the third round running. I keep it in the vocabulary because a verdict set
that has no room for "the claim overreaches" is a verdict set that cannot fail.

| Claim | Status | Verdict | Role | Code | Sev |
|---|---|---|---|---|---|
| `AUD-B-SCAFFOLD` | Incomplete | `SUPPORTED_WITH_SCOPE` | interpretation | `NOT_APPLICABLE` | LOW |
| `AUD-CORR-0995` | Supported | `SUPPORTED_WITH_SCOPE` | interpretation | `PRESENT` | MEDIUM |
| `AUD-CORR-0995-SCOPE` | Supported | `SUPPORTED_WITH_SCOPE` | interpretation | `PRESENT` | MEDIUM |
| `AUD-CYCLE-KERNEL` | Supported | `SUPPORTED` | formalization | `PRESENT` | — |
| `AUD-DELAY` | Supported | `SUPPORTED_WITH_SCOPE` | interpretation | `PRESENT` | LOW |
| `AUD-FROZEN-TOPO` | Supported | `CONTEXT_ONLY` | scope_only | `PRESENT` | — |
| `AUD-GATE` | Supported | `SUPPORTED_WITH_SCOPE` | formalization | `PRESENT` | HIGH |
| `AUD-HELDOUT-LABEL` | Supported | `SUPPORTED_WITH_SCOPE` | inference | `PRESENT` | MEDIUM |
| `AUD-K3` | Supported | `SUPPORTED_WITH_SCOPE` | formalization | `PRESENT` | LOW |
| `AUD-KAPPA-TW` | Supported | `SUPPORTED_WITH_SCOPE` | formalization | `PRESENT` | LOW |
| `AUD-MODULAR-ORACLE` | Supported | `SUPPORTED_WITH_SCOPE` | method_validity | `NOT_APPLICABLE` | HIGH |
| `AUD-NOVELTY` | Incomplete | `SUPPORTED_WITH_SCOPE` | interpretation | `NOT_APPLICABLE` | MEDIUM |
| `AUD-RATELAW` | Supported | `SUPPORTED_WITH_SCOPE` | formalization | `PRESENT` | MEDIUM |
| `AUD-REPRO-B2A95` | Supported | `SUPPORTED_WITH_SCOPE` | method_validity | `PRESENT` | LOW |
| `AUD-REPRO13` | Supported | `SUPPORTED` | method_validity | `PRESENT` | — |
| `AUD-RESP1-UNIFORM` | Supported | `SUPPORTED` | inference | `PRESENT` | LOW |
| `AUD-SCOPE-1.4` | Supported | `SUPPORTED` | inference | `NOT_APPLICABLE` | LOW |
| `AUD-SLOWPOLE` | Rejected | `VALIDATED_REJECTION` | method_validity | `PRESENT` | LOW |
| `AUD-TIES` | Supported | `SUPPORTED_WITH_SCOPE` | formalization | `PRESENT` | LOW |
| `AUD-TIMESTEP` | Incomplete | `SUPPORTED_WITH_SCOPE` | scope_only | `NOT_APPLICABLE` | HIGH |
| `AUD-TOPO-OMEGA` | Supported | `SUPPORTED_WITH_SCOPE` | interpretation | `PRESENT` | MEDIUM |
| `AUD-V4-HELDEVENT` | Supported | `SUPPORTED` | method_validity | `NOT_APPLICABLE` | LOW |

---

## 2. F45 — `AUD-GATE` calls it "multiplicative normalisation"; Miller & MacKay define that term differently

**This is the highest-value finding of the round, and it is a naming defect in a claim whose
mathematics is correct.**

`AUD-GATE` states: *"The capacity gate `s_i = min(1, c/(q_i+eps))` is node-strength multiplicative
normalisation. It is idempotent but it is not a metric, KL or Bregman projection onto the capacity set
(no-go over the stated domain)."*

The no-go half is correct. The first sentence is not.

[LIT-0043] draws its distinction precisely: **multiplicative** enforcement rescales the whole weight
vector by a common factor so a total-strength constraint holds; **subtractive** enforcement takes the
excess off in a way that drives almost every weight to a bound. The paper's entire result is that this
choice *determines which attractor the dynamics select* — multiplicative converges to the principal
eigenvector of the unconstrained operator, subtractive saturates.

The AIEF gate is **neither**. It caps each node independently at its own threshold
`c/(q_i + eps)`, with no common rescaling and no conserved total. It is a per-node saturation, which
is a third thing.

**Why this matters more than a label.** This is the same class of defect as `ERRATA` E6 on "cycle
kernel": a correct computation under a term imported from a different object. E6 was caught because
`dim ker` came out one dimension off from the cycle space. Here the error is invisible in the
arithmetic — `s_i` is well-defined and idempotent either way — and only becomes visible when you ask
what the borrowed term *means*. Borrowed names are a provenance defect, and this inbox exists to
catch provenance defects.

**It also lands on `AUD-RATELAW` and `AUD-KAPPA-TW`.** `AIEFS_salvage.md` asserts that multiplicative
normalisation "is exactly what produces the k·η/c rates". If the gate is not multiplicative in
[LIT-0043]'s sense, that assertion is unsupported *as stated* — the rate law may still be correct, but
it is not explained by Miller & MacKay's mechanism. This is now the sharpest open question in the
literature layer, and it is testable in an afternoon: compare the gate against both enforcement
methods on a small network and see which attractor it produces.

---

## 3. F46 — A skipped certification test is not an exercisable artifact

`AUD-MODULAR-ORACLE` is accurate and understated. The oracle test that would certify the modular
platform is skipped unless `AIEF_MODULAR_RUN` is set and a pre-generated data directory is supplied,
so a default `pytest -q` reports **40 passed / 2 skipped** having never tested oracle equivalence. The
claim already notes that neither run re-tests the 344-array `max_abs_diff = 0` identity of
`IMPL-MODULAR-01`.

[LIT-0038] supplies the consequence the claim does not draw. ACM's *Artifacts Evaluated – Functional*
requires artifacts be *"documented, consistent, complete, **exercisable**, and include appropriate
evidence of verification and validation."* A reviewer following the documented instructions gets a
green suite that skipped the only certification test. That is not exercisable.

So there are two readings and the repository currently takes the more flattering one:
- *the platform is oracle-equivalent, and the test proves it when enabled* (needs the data directory);
- *the platform's oracle equivalence is asserted in a claim, not demonstrated in CI* (true today).

Only the second is currently supportable. The fix is cheap — make the oracle test runnable without a
secret environment, or vendor a minimal certification fixture — and it is the difference between
`IMPL-MODULAR-01` being a certified identity and a recorded one.

---

## 4. F47 — The timestep gap is a convergence analysis, not a truncation check

`AUD-TIMESTEP` is an open item stated plainly: no `dt` / `dt/2` / `dt/4` study exists, so trajectories,
rates and topologies hold for `dt = 0.01` only. It rates itself "not a finding against any existing
claim", which is fair in the sense it means.

The literature says it is a bigger deal than "unverified integration step" sounds. [LIT-0035] states
that numerically solving retarded functional differential equations *"cannot be founded on the mere
adaptation of well-known methods for ordinary ... equations"*, and that convergence analysis for these
equations is organised around the approximation of the **solution map** and the propagation of
discontinuity points. [LIT-0029] gives the method-of-steps error analysis.

For an ODE, halving `dt` and watching a number settle is routine due diligence. For a DDE it is the
**first required step** of validating the integrator, because the object being approximated is a
solution map on a history space, not a trajectory on a vector space. Absence of the study therefore
means the convergence order of the frozen results is *unknown*, not merely unstated.

Consequence worth stating plainly: several claims in this registry are of the form "the rate matches
within 5.3e-6" or "the multiplier matches to 2.1e-8". Those agreements are computed at one `dt`. If
the discretisation is first-order, the agreement is real but the *rate law itself* is a `dt → 0`
statement that has not been tested at any other `dt`. **The two open items that gate publication-grade
claims are `AUD-TIMESTEP` and `AUD-NOVELTY`.**

---

## 5. F48 — What the audit corpus gets right, and why it is the best material in the repository

Three claims are worth holding up as models, not because they are correct but because of how they are
written.

**`AUD-TIES` derives its own counterexample.** It states the nonadditivity and odd-defect formulas for
an all-tied equal-weight `K_n`, then volunteers that they are **not** universal: an unequal-edge `K4`
with equal row sums gives 0.2003 against a predicted 0.2887, the figure depends on which adjacent edge
pair is perturbed, and — carefully — the refuting configuration *is not a fixed point of the ideal
gate*, so it refutes universality without being a fixed-point counterexample. Claims that construct
their own disconfirmation are rare in any literature.

**`AUD-CYCLE-KERNEL` separates a check from a law.** It reports `dim K = m − n = n(n−3)/2` verified on
373/373 all-tied components, *and* separately reports that only 292 of 406 replay components agree
with the slow multiplier to 4.5e-4. Two numbers, two confidences, no blending.

**`AUD-V4-HELDEVENT` is a defect report with a blast radius.** A floating-point boundary bug —
`searchsorted(times, times[index] + duration, side='left')` rejects an event held *exactly* the
required duration when the sum rounds up one ulp — and then it bounds itself: 32 of 605 valid start
positions, only grid-multiple hold durations can be hit, so the `17.5029 × rho` nominal holds and the
non-crossing estimands are unaffected. [LIT-0014] is the textbook citation for exactly this
comparison, and the claim reached it by measurement first.

The pattern across all three: **state the check, state its scope, state what would falsify it.** That
is what most of the claims I rejected in earlier rounds were missing.

---

## 6. F49 — Two claims deliberately left unadjudicated, and a gap in my own coverage

`AUD-LABEL` and `AUD-V4-RECOVERY-WORDING` have **no source** and are not in
[`ADJUDICATION.csv`](ADJUDICATION.csv). That is deliberate, and gate 8 enforces the boundary in both
directions — I could not adjudicate them without inventing a citation.

- **`AUD-LABEL`** is a labelling rule: *"controlled exploratory analyses with a fixed recorded design;
  nothing in the repo was preregistered."* Adjudicating it needs literature on
  confirmatory/exploratory methodology and preregistration. **I have none.** After eight rounds the
  bibliography has a real, specific hole here, and this is the first one I can name precisely rather
  than as "the rest is unadjudicable".
- **`AUD-V4-RECOVERY-WORDING`** is an internal definitional finding: `_first_index` / `_held_index`
  return index 0 when the signal is already above target, so a "recovery" event can be retention. No
  external literature can attest what a local function returns. It is a correct finding that belongs
  to code review, not to a bibliography.

**Named gap for a future round:** one source on exploratory-versus-confirmatory analysis and
preregistration would let `AUD-LABEL` be adjudicated and would also strengthen `AUD-HELDOUT-LABEL`.
That is a better use of a search than anything else left.

---

## 7. Proposed registry amendments — **for owner approval, not applied**

| # | Target | Change | Sev |
|---|---|---|---|
| 1 | `AUD-GATE` | **Rename.** `s_i = min(1, c/(q_i+eps))` is a per-node min-endpoint cap, not multiplicative normalisation in [LIT-0043]'s sense. Keep the no-go verbatim | **HIGH** |
| 2 | `AUD-MODULAR-ORACLE` | Draw the ACM consequence: `IMPL-MODULAR-01`'s 344-array identity is uncertified in CI; a skipped-by-default oracle test fails "exercisable" | **HIGH** |
| 3 | `AUD-TIMESTEP` | Restate as a convergence analysis of the solution map; raise priority to gate publication claims | **HIGH** |
| 4 | `AUD-RATELAW`, `AUD-KAPPA-TW` | Record that the `k·η/c` mechanism claim is unsupported *as stated* pending §2's test | MED |
| 5 | `AUD-TOPO-OMEGA` | Promote "multistable for generic ω" from caveat to statement — it is the best-supported clause | MED |
| 6 | `AUD-HELDOUT-LABEL` | Add: label equivalence makes the AUC table unambiguous, it does not upgrade predictability to causation ([LIT-0024]) | MED |
| 7 | `AUD-KAPPA-TW` | Flag the `k=2` coefficient as `n=1` in the statement, not only in the caveat | LOW |
| 8 | `AUD-TIES` | Promote the equal-edge hypothesis to the statement; the counterexample depends on it | LOW |
| 9 | `AUD-DELAY` | Restate as "delay increases the diversity of sampled outcomes" | LOW |
| 10 | `AUD-B-SCAFFOLD` | Convert to the testable form: `reset_B` cannot separate `B`'s contribution from the history that produced it | LOW |
| 11 | `AUD-LABEL` | Leave open; requires a preregistration-methodology source (§6) | — |

---

## 8. State

| Measure | R5 | R6 | R7 | **R8** |
|---|---|---|---|---|
| Sources | 38 | 39 | 43 | **43** |
| Adjudicated | 24 | 24 | 25 | **46** |
| Claims with ≥1 source | 24/43 | 24/43 | 25/76 | **46/76** |
| `AUD-*` with ≥1 source | 0/24 | 0/24 | 1/24 | **22/24** |
| Open leads | 0 | 4 | 0 | **0** |
| Verifier gates | 8 | 8 | 8 | **8** |

Studies with ≥1 source: **11/15**. The four unmapped are `HISTORICAL_PROJECT_ORIGINS`,
`AIEF_1_4_PIVOT_PILOT`, `AIEF_1_4_PROPOSAL_EQUALIZATION` and `AI_AGENT_AUDITS_2026_10` — the last of
which is a bookkeeping artefact, since its claims are now sourced individually.

## 9. What Round 8 did not do

- Added **no** sources. Verdict mix moved only because the mapping and reading did.
- Touched **only** `bears_on_ids` in `SOURCES.csv`. The builder verifies every snapshot SHA-256 before
  and after and asserts no identity field changed — a mapping extension cannot silently rewrite the
  bibliographic record.
- Did not resolve §2's open question. Renaming a term is a registry edit; testing which enforcement
  method the gate actually implements is a numerical experiment, and it is not a literature task.
- Did not adjudicate `AUD-LABEL` or `AUD-V4-RECOVERY-WORDING`, for the reasons in §6.
- Did not read the 39 audit logs or the 8 origin PDFs.
