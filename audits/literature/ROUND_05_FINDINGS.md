# Literature Review — Round 5: The Adjudication

**Round:** 5 · **Date:** 2026-10-30 · **New sources:** 0 (total 38) · **Claims adjudicated:** 24 of 43
**Registry:** [`SOURCES.csv`](SOURCES.csv) · [`ADJUDICATION.csv`](ADJUDICATION.csv) · **Prior:** [R1](ROUND_01_FINDINGS.md) · [R2](ROUND_02_FINDINGS.md) · [R3](ROUND_03_FINDINGS.md) · [R4](ROUND_04_FINDINGS.md)

---

## 0. What this round is

Four rounds produced 38 sources and no verdict on anything. This round produces the verdicts and
adds **no sources at all**. That is the point: the bibliography was never the deliverable.

**Headline, stated before the qualifications: not one of the 24 mapped claims is refuted by the
literature.** Six are supported outright, five are supported with a scope condition that must be
written down, two cannot be attested by literature at all (and are not defective for it), and
eleven are retirements or rejections the literature *validates* — four of those rejections are now
over-determined rather than merely correct.

The defects are almost entirely in the **claim-to-source mapping**, not in the science. Three claims
are mis-sourced. Two of those were discovered by reading the mapping rather than the paper — which
is the thing four rounds of searching could not have found.

---

## 1. F28 — The adjudication result

Each row of [`ADJUDICATION.csv`](ADJUDICATION.csv) records five things: what the literature is
being asked to attest, whether it does, whether the **registry mapping** is right, whether the
**producing code exists**, and what change follows. Verdict and mapping health are separate
columns on purpose — a claim can be scientifically correct and wrongly sourced, and collapsing the
two axes would have hidden the single most important finding in this round.

| Verdict | n | Meaning |
|---|---:|---|
| `SUPPORTED` | 6 | Literature substantiates the role it is asked to play |
| `SUPPORTED_WITH_SCOPE` | 5 | Substantiated, but a precondition must be stated |
| `CONTEXT_ONLY` | 2 | No external literature can attest it; sources only frame it |
| `VALIDATED_RETIREMENT` | 6 | Retired claim; literature confirms the retirement |
| `VALIDATED_REJECTION` | 5 | Rejected claim; literature confirms the rejection |
| `BOUNDED` | **0** | Claim exceeds what the literature licenses — *none* |

`BOUNDED` was in the vocabulary and went unused. I did not reach for it to make the table look
discriminating; if a claim had needed it, the scope conditions in the five `SUPPORTED_WITH_SCOPE`
rows are where it would have appeared.

| Mapping health | n |
|---|---:|
| `COMPLETE` | 21 |
| `INCOMPLETE` | 2 |
| `WRONG` | 1 |

| Severity | n | Claims |
|---|---:|---|
| `HIGH` | 1 | `REJ-LOCK-03` |
| `MEDIUM` | 2 | `EMP-AIEF14-01`, `EMP-AIEF14-02` |
| `LOW` | 4 | `EMP-AIEF13-01`, `EMP-AIEF13-02`, `CF08`, `REJ-SPEC-01` |
| `NONE` | 17 | — |

| Claim | Study | Verdict | Mapping | Code | Sev |
|---|---|---|---|---|---|
| `EMP-AIEF13-01` | 1.3 · disjoint-100 | `SUPPORTED_WITH_SCOPE` | COMPLETE | `PRESENT` | LOW |
| `EMP-AIEF13-02` | 1.3 · disjoint-100 | `SUPPORTED_WITH_SCOPE` | **INCOMPLETE** | `RELOCATED` | LOW |
| `REJ-COHORT-05` | 1.3 · early-20 | `VALIDATED_REJECTION` | COMPLETE | `NOT_APPLICABLE` | — |
| `CAVEAT-MS-8.4` | 1.4 · controller-fiber | `SUPPORTED` | COMPLETE | `RELOCATED` | — |
| `CF01` | 1.4 · controller-fiber | `SUPPORTED` | COMPLETE | `PRESENT` | — |
| `CF02` | 1.4 · controller-fiber | `SUPPORTED` | COMPLETE | `PRESENT` | — |
| `CF03` | 1.4 · controller-fiber | `SUPPORTED` | COMPLETE | `PRESENT` | — |
| `CF05` | 1.4 · controller-fiber | `CONTEXT_ONLY` | COMPLETE | `PRESENT` | — |
| `CF06` | 1.4 · controller-fiber | `SUPPORTED_WITH_SCOPE` | COMPLETE | `PRESENT` | — |
| `CF08` | 1.4 · controller-fiber | `SUPPORTED_WITH_SCOPE` | COMPLETE | `RELOCATED` | LOW |
| `LEAN-CF-01` | 1.4 · lean-fiber | `SUPPORTED` | COMPLETE | `PRESENT` | — |
| `EMP-AIEF14-02` | 1.4 · matched-phase | `SUPPORTED_WITH_SCOPE` | COMPLETE | `PRESENT` | MEDIUM |
| `REJ-K3-04` | 1.4 · rejected-spectral | `VALIDATED_REJECTION` | COMPLETE | `NOT_APPLICABLE` | — |
| `REJ-LOCK-03` | 1.4 · rejected-spectral | `VALIDATED_REJECTION` | **WRONG** | `NOT_APPLICABLE` | HIGH |
| `REJ-SPEC-01` | 1.4 · rejected-spectral | `VALIDATED_REJECTION` | COMPLETE | `NOT_APPLICABLE` | LOW |
| `REJ-SPEC-02` | 1.4 · rejected-spectral | `VALIDATED_REJECTION` | COMPLETE | `NOT_APPLICABLE` | — |
| `EMP-AIEF14-01` | 1.4 · split-state | `CONTEXT_ONLY` | **INCOMPLETE** | `PRESENT` | MEDIUM |
| `S03` | 1.4 · synthesis | `VALIDATED_RETIREMENT` | COMPLETE | `NOT_APPLICABLE` | — |
| `S04` | 1.4 · synthesis | `VALIDATED_RETIREMENT` | COMPLETE | `NOT_APPLICABLE` | — |
| `S07` | 1.4 · synthesis | `VALIDATED_RETIREMENT` | COMPLETE | `NOT_APPLICABLE` | — |
| `S09` | 1.4 · synthesis | `VALIDATED_RETIREMENT` | COMPLETE | `NOT_APPLICABLE` | — |
| `S11` | 1.4 · synthesis | `VALIDATED_RETIREMENT` | COMPLETE | `NOT_APPLICABLE` | — |
| `S16` | 1.4 · synthesis | `VALIDATED_RETIREMENT` | COMPLETE | `NOT_APPLICABLE` | — |
| `IMPL-MODULAR-01` | platform v1/v4 | `SUPPORTED` | COMPLETE | `PRESENT` | — |

---

## 2. F29 — The highest-severity item: a rejection supported by a source that does not apply

`REJ-LOCK-03` rejects a bare algebraic zero-sum `ω_i + G_i = 0` as the locking condition. The
rejection is correct. Its **only** attached source is [LIT-0030] — Earl & Strogatz — and Round 4's
F24 established that their criterion requires **uniform in-degree *k***, which adaptive hypergraph
AIEF networks violate by construction.

So the sole citation for this claim does not apply to the system the claim is about. Round 4
corrected the prose; the registry mapping was never fixed. This is exactly what an adjudication
pass catches and a search pass cannot: every retrieval in Round 4 was individually correct, and the
defect only appears when you ask *what is this source doing for this claim*.

**Fix:** [LIT-0018] (implicit equations for the collective frequency, no uniform-*k* restriction)
and [LIT-0028] (multiple and state-dependent delays) carry the claim; [LIT-0030] demotes to context
with its precondition stated.

### 2.1 The two incomplete mappings

**`EMP-AIEF14-01`** ("B is not a unique memory bottleneck") is the most literature-explainable
statement in the entire registry, and it currently has no supporting source — its only mapping is
[LIT-0016], a `CONTEXT`-stance nearest-neighbour paper. The two sources that actually explain it are
bound to *other* claims: [LIT-0010] (in a delay system the state **is** the history segment, so
removing one component leaves the history intact) and [LIT-0018] (the state is an *N + N²*
dimensional functional differential equation, so memory is distributed by construction). Adding
those two moves the claim from `CONTEXT_ONLY` to `SUPPORTED_WITH_SCOPE` with **no scientific edit**.

**`EMP-AIEF13-02`** states that adaptive coupling rather than bare delay drives persistence. Its
inferential frame is fine, but the interpretive half has no adaptive-delay source attached. The
mechanism contrast itself is computed by a surviving script (§3).

### 2.2 The one genuine scope risk

**`EMP-AIEF14-02`** is well-supported — [LIT-0025] gives the formal reason matched-phase design is
*necessary*, not merely careful, by naming the confound ("shared information due to common
history"). But [LIT-0016] shows the underlying mechanism is under active independent investigation,
so **novelty must be claimed for the ablation design and the recovery metric, not for the existence
of delay-driven frequency selection.** That is a live priority risk, not a citation problem.

---

## 3. F30 — The producing-code audit, and why F16 was too blunt

Round 3's F16 reported that 5 of 14 studies name canonical entrypoints that exist nowhere. That is
true. Adjudicating the claims forced me to ask the next question, which F16 did not: **does the
capability exist under another name?**

| Study | Entrypoints | Missing | What actually happened |
|---|---|---:|---|
| `AIEF_1_4_CONTROLLER_FIBER` | 4 | 2 | `AIEF_1_4_component_controller_audit.py` computes explicit intertwiners (`C D = L_component C`); `AIEF_1_4_freeze_controller_fiber_theorem.py` computes the right closure. **Capability present, names stale.** |
| `AIEF_1_3_DISJOINT_100SEED` | 4 | 2 | `AIEF_1_3_paired_statistics_updated.py` carries `CONTROLS = (shuffle_R, no_delay, no_mu, no_gap)` and their arms; `AIEF_1_3_closure_diagnostics_updated.py` computes the persistence matrices. **Capability present, names stale.** |
| `AIEF_1_4_MATCHED_PHASE_ABLATION` | 2 | 1 | Ablation script is present; authoritative output is present in `test_output/` (8 `matched_phase` files). Missing `AIEF_1_4_driver_mechanism.py` is a separate mechanism probe. |
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | 3 | 3 | **Genuine loss.** Zero matching scripts, zero in all three archives. |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | 3 | 3 | Covered in Round 3 (F17): the surviving artifact is narrower than the study title. |

**And there is a defect in the opposite direction, which nobody had looked for:** two claims
(`CAVEAT-MS-8.4`, `CF08`) are produced by `AIEF_1_4_freeze_controller_fiber_theorem.py`, which
**exists in the working tree but is not registered as an entrypoint for its study at all.** F16
asked only whether registered files exist. It never asked whether existing files are registered.

So F16's correct form is **bidirectional referential integrity**, and its severity is lower for
three of the five studies than Round 3 implied. The genuine loss is confined to
`AIEF_1_0_TO_1_2_FOUNDATIONAL` — which, notably, carries **no literature-mapped claims**, so none of
the 24 adjudications rests on missing code.

Producing-code status across the 24: **10 `PRESENT`, 3 `RELOCATED`, 11 `NOT_APPLICABLE`** (rejections
and retirements do not depend on a live producer).

Caveat I will not paper over: these are conclusions from **symbol search**, not from provenance
manifests. I verified that a script *contains* an intertwiner computation; I did not verify that it
produced the specific numbers in `CF08`.

---

## 4. F31 — The bootstrap question is closed, and the answer is not what the recommendation said

Round 1 flagged that the repository's intervals might need the wild cluster bootstrap [LIT-0002]
and never checked which variant the code uses. Now checked:

```
AIEF_1_3_paired_statistics_updated.py:348
    low, high = np.percentile(bootstrap_means, [2.5, 97.5])
```

It is a **stratified paired percentile bootstrap of the mean difference** — not wild cluster, not
BCa. [LIT-0002] prefers wild at 40–100 clusters, and N=100 sits in that band.

**Why this does not change the conclusion, stated precisely rather than reassuringly:**

1. [LIT-0032]'s failure modes are *unbalanced cluster sizes* and *few treated clusters*. Neither
   applies: seeds are exchangeable, cluster sizes are equal, and every seed is treated in every arm
   (treated fraction = 1).
2. The estimand is a **paired within-seed contrast**, which is a different problem from the
   unbalanced cluster-robust setting the wild bootstrap was built for.
3. The effect is `dz = 8.434`. No bootstrap variant moves a 95% CI spanning roughly ±0.007 around
   0.305 across zero.

**Verdict: `SUPPORTED_WITH_SCOPE`, severity `LOW`** — not "no action". The *documentation* action
stands: the claim should state its interval variant, and state that any future arm ablating a
**subset** of seeds changes the interval construction at that moment ([LIT-0032]'s explicit
conditional).

This is the pattern worth keeping: the right answer was not "re-run it" and not "it's fine". It was
"find out, then explain why it doesn't bind here."

---

## 5. F32 — The epistemic limit of this whole exercise

Worth naming once, because it bounds what any literature round can claim.

For the 11 empirical claims, no external source can ever attest the number. `D_B = +0.305909` is
not a fact about the world that a bibliography can corroborate. What the literature can attest is
narrower and — it turns out — more useful:

| Role | Question the literature can answer | Used by |
|---|---|---|
| `INFERENCE` | Is the statistical frame valid for this design? | 1 claim |
| `DESIGN` | Is this control necessary, or merely careful? | 1 |
| `INTERPRETATION` | Is the mechanism claim consistent with the field? | 1 |
| `FORMALIZATION` | Is the theorem correctly stated and properly general? | 8 |
| `METHOD_VALIDITY` | Was this method sound / was rejecting it correct? | 10 |
| `SCOPE_ONLY` | Nothing — the source only frames the question | 3 |

The 8 formalization and 10 method-validity claims are where literature does real work, and they are
where all 5 validated rejections live. **The rejections are the best-supported part of the
repository** — which is the opposite of the usual shape, where rejections are the least documented.

---

## 6. Gate 8: the adjudication is now enforced, not just written

`verify_literature.py` gained an eighth gate. It fails closed (same rule as gate 4 — the vacuity bug
from Round 1), and it checks the things that make the table auditable rather than decorative:

- `ADJUDICATION.csv` covers **exactly** the claims carrying at least one source — both directions,
  because a table that quietly drops a claim is worse than no table;
- every cited source must **map back** to that claim in `bears_on_ids` — the adjudication may not
  introduce a citation the registry does not have;
- every mapped source must **appear** — the adjudication may not silently omit one;
- closed vocabularies for verdict, mapping health, severity, claim class, role, producing-code status;
- `mapping_health ∈ {INCOMPLETE, WRONG}` **requires** a non-`none` `required_change`;
- `registry_status` must agree with `registry/claims.csv`;
- `n_sources` must equal the number of sources actually cited.

**Eight negative tests were run on a throwaway copy and all eight bite:** dropping a claim,
adjudicating an unmapped claim, an invalid verdict, citing a source not mapped to the claim,
`WRONG` with `required_change=none`, a tampered `n_sources`, a tampered `registry_status`, and a
missing `ADJUDICATION.csv`. Verifier now reports **8/8**.

---

## 7. Proposed registry amendments — **for owner approval, not applied**

Ranked by severity. `registry/` is untouched this round.

| # | Target | Change | Sev | Basis |
|---|---|---|---|---|
| 1 | `REJ-LOCK-03` | Replace mapping: `LIT-0018` + `LIT-0028` carry it; `LIT-0030` → context with uniform-*k* precondition noted | **HIGH** | F29 |
| 2 | `EMP-AIEF14-01` | Add `LIT-0010` + `LIT-0018` to `bears_on_ids` (claims it from `CONTEXT_ONLY` → `SUPPORTED_WITH_SCOPE`, no text change) | MED | F29 |
| 3 | `EMP-AIEF14-02` | State novelty boundary: ablation design + recovery metric, **not** the mechanism ([LIT-0016]); note delay kept explicit rather than phase-reduced ([LIT-0028]) | MED | F29 |
| 4 | `AIEF_1_4_CONTROLLER_FIBER` | Register `AIEF_1_4_freeze_controller_fiber_theorem.py`; it produces two of the study's claims and is registered nowhere | MED | F30 |
| 5 | `EMP-AIEF13-01` | Record interval variant (stratified paired percentile) + why wild does not bind + subset-ablation conditional | LOW | F31 |
| 6 | `EMP-AIEF13-02` | Add `LIT-0018`/`LIT-0016` as corroborating context; annotate that the mechanism contrast lives in the paired-statistics script | LOW | F29 |
| 7 | `CF08` | Reword "exact" as explicitly **pointwise** and normalization-dependent; cite `CAVEAT-MS-8.4` for where the global reading fails | LOW | F28 |
| 8 | `REJ-SPEC-01` | Clarify the rejection is of POD truncation as applied, not of spectral reduction generally; `LIT-0004` is the citable alternative | LOW | F28 |
| 9 | `EMP-AIEF13-02`, `CF05` | Housekeeping: state the 32,001-states / 32,000-steps relationship so the two round figures are not read as a discrepancy | — | F28 |
| 10 | Repository | Mint DOIs for frozen run directories to meet ACM *Artifacts Available* ([LIT-0038]) | — | R4 F25 |

**Not amendments, and not literature work:** F16's entrypoint repairs and the `verify_inventory.py`
gate remain outstanding in the registry/engineering workstream (Round 4's F22 declined them
deliberately, and that decision stands).

---

## 8. State

| Measure | R1 | R2 | R3 | R4 | **R5** |
|---|---|---|---|---|---|
| Sources | 16 | 28 | 33 | 38 | **38** |
| Claims with a source | 19/43 | 22/43 | 24/43 | 24/43 | **24/43** |
| Claims **adjudicated** | 0 | 0 | 0 | 0 | **24/24** |
| Open leads | 3 | 3 | 1 | 0 | **0** |
| Verifier gates | 7 | 7 | 7 | 7 | **8** |

The 19 unadjudicated claims are: 12 retired `S` rows (deliberately unmapped — they have replacements
and need no defence), 6 `CF` rows that are textbook material or open conjectures, and
`EMP-AIEF14-03`, for which no defensible external anchor exists.

## 9. What Round 5 did not do

- Added **no** sources. Coverage is unchanged by design.
- Did not modify `registry/`, `audits/engineering/`, or any pre-existing file other than
  `verify_literature.py` (strengthened) and `ROUND_STATE.json`.
- Did not claim to have verified producing code from provenance manifests — the producing-code
  column is symbol-search evidence and is marked as such.
- Did not resolve the two `INCOMPLETE` mappings itself. It proposed them; the registry is not mine
  to edit.
