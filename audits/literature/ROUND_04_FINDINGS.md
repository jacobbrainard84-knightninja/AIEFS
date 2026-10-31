# Literature Review — Round 4: Formalization Standards, Artifact Badging, and Two Corrections to Myself

**Round:** 4 · **Date:** 2026-10-30 · **Sources added:** 5 (total 38) · **Leads:** 1 resolved, **0 open**
**Registry:** [`SOURCES.csv`](SOURCES.csv) · **Prior:** [R1](ROUND_01_FINDINGS.md) · [R2](ROUND_02_FINDINGS.md) · [R3](ROUND_03_FINDINGS.md)

---

## 0. Bottom line

Round 4 closes the lead queue. Seven leads opened across four rounds; seven promoted; none open.

The round also produced **two corrections to my own earlier work**, both recorded here rather
than quietly patched:

- Round 3's use of Earl & Strogatz as support for the lock claim was **too strong** — the criterion
  requires uniform in-degree (F24).
- Round 3's roadmap put the registry repair and the `verify_inventory.py` gate on the *literature*
  worklist. That was a category error, and Round 4 declines the work rather than quietly doing it
  under a heading where it does not belong (F22).

Claim coverage did not move (24/43). That is not a failure of the round — it added depth on claims
already mapped. Saying so plainly matters more than manufacturing a delta.

---

## 1. F22 — Boundary: the registry repair is not a literature task

Round 3's F16 found that 5 of 14 studies name canonical entrypoints that exist nowhere. Round 3's
roadmap then listed "decide demotion vs restoration" and "add gate 6 to `verify_inventory.py`" as
Round 4 literature targets.

**That was wrong and Round 4 declines it.** The inbox protocol is explicit:

> *"Never modify `registry/`. Propose amendments in the findings file (§4 of each round) for owner
> approval. The literature layer observes the registry; it does not write to it."*

Deciding whether `AIEF_1_0_TO_1_2_FOUNDATIONAL` should be demoted from `Frozen`, and editing an
engineering verifier, are repository-governance and engineering actions. They need the same owner
approval as any other registry change, and performing them inside a literature round would launder
a registry edit through a process that promises not to make registry edits.

**Handoff, stated once:** F16's four proposed fixes are in `ROUND_03_FINDINGS.md` §8 and stand. They
belong to the registry/Milestone workstream, not to a literature round. Round 4 has not touched
`registry/`, `audits/engineering/`, or any pre-existing file.

This is worth recording because it is the failure mode of an unbounded "keep going" loop: each round
invents adjacent work for the next one, and the boundary that makes the inbox auditable erodes one
plausible-looking target at a time.

---

## 2. F23 — Lean: three sources form a chain, and Nash's paper is the standard the work should be held to

**[VERIFIED]** The Lean programme now has a complete citation chain, from platform to exemplar:

| Layer | Source | What it anchors |
|---|---|---|
| Toolchain | **de Moura & Ullrich (CADE 2021)** [LIT-0034] | Which Lean, and why: extensible elaborator, tabled typeclass resolution, `functional but in-place` codegen |
| Library | **mathlib Community (CPP 2020)** [LIT-0036] | The library's scope: *"a basis for research level mathematics"*, *"extensive hierarchy of structures"* |
| Exemplar | **Nash, *Engel's Theorem in Mathlib* (JAR 2023)** [LIT-0037] | What a finished formalization paper looks like |

The repository pins a Lean toolchain and runs `lean-action` in CI, but until now cited no Lean
reference at all — a reader could not tell which Lean the proofs target. [LIT-0034] answers that.

**The important one is [LIT-0037].** Nash formalizes Engel's theorem — a classical linear-algebra
result whose informal literature carries several variants — and states the design goal directly:

> *"Mathlib's version of Engel's theorem unifies the various versions of this result appearing in
> the informal literature, while demanding weaker hypotheses and providing a stronger result."*

And on method: *"We emphasise that all arguments work with coefficients in any commutative ring."*

**`LEAN-CF-01` is built the other way round.** It fixes $C_{\{2,7\}}$ over $\mathbb{R}$ and computes
one kernel. That demonstrates the kernel — which is genuinely valuable, since `CF06` leans on it —
but it inherits none of the generality. Nash's paper is the concrete target state: state the
rank–incidence theorem over an arbitrary commutative ring, with no connectivity assumption beyond
what the proof needs, and let the $K_3$ case fall out as a corollary.

This sharpens Round 1's F4 rather than repeating it. F4 said *"if the project ever wants the Lean
result to carry weight beyond $C_{\{2,7\}}$..."*. F23 supplies the standard to measure that against,
and a published example of someone doing it in the same library.

**Recommendation:** cite [LIT-0037] whenever the Lean work is described. It is the honest benchmark,
and it makes the current scope legible as a deliberate choice rather than a limit nobody noticed.

---

## 3. F24 — Correction: Earl & Strogatz is narrower than Round 3 implied

**Round 3's F18 overstated this, and the correction is mine.**

Round 3 characterised [LIT-0030] from four citing works, because the abstract had not been read. The
abstract is now read directly, and it carries a precondition I did not record:

> *"We derive a stability criterion for the synchronous state in networks of identical phase
> oscillators with delayed coupling. The criterion applies to any network (whether regular or
> random, low dimensional or high dimensional, directed or undirected) in which each oscillator
> receives delayed signals from **k others, where k is uniform for all oscillators**."*

The breadth claim is real — regular/random, low/high dimensional, directed/undirected. But the
condition is **uniform in-degree $k$**. AIEF networks are adaptive, hypergraph-structured, and
time-varying in degree by construction; that is the whole point of the adaptive edge matrix $B$.
**The criterion therefore does not apply to the AIEF network class as stated.**

What survives, and what does not:

- **Survives:** the structural point behind `REJ-LOCK-03`. Locking in a delay-coupled network is
  governed by a condition that must be solved for the collective frequency, not checked as an
  algebraic sum. That principle is general.
- **Does not survive:** any suggestion that [LIT-0030] directly supports a claim about *this*
  network. It does not, because the precondition fails.

**Corrected attribution for `REJ-LOCK-03`:** the load-bearing citations are [LIT-0018] (Park &
Lefebvre — implicit equations for $\Omega$ and the stability eigenvalues, no uniform-$k$ restriction)
and [LIT-0028] (Jolly et al. — multiple and state-dependent delays). [LIT-0030] is **context** for
the principle, not support for the claim. Round 3's §8 row for `REJ-LOCK-03` should be read with
this substitution.

**Protocol note:** the LIT-0030 snapshot has *not* been rewritten. The protocol says snapshots are
immutable and that a verification level is not upgraded after the fact. Its `notes` field already
flagged the second-hand provenance, and this section is the correction of record. A future round
citing LIT-0030 should treat F24 as authoritative for its scope.

---

## 4. F25 — ACM badging both sanctions the CI tolerance design and exposes a missing requirement

**[VERIFIED]** Two separate consequences from [LIT-0038].

### 4.1 The two-tier tolerance gate is the standard, not a concession

Open since Round 1's F5. The ACM policy states:

> *"In each case, exact replication or reproduction of results is not required, or even expected.
> Instead, the results must be in agreement to within a tolerance deemed acceptable for experiments
> of the given type. In particular, differences in the results should not change the main claims
> made in the paper."*

So the Stage 7 gate design is settled, and it is settled in the direction Round 1 argued from
floating-point first principles [LIT-0012]–[LIT-0014]: **0-ULP on discrete $P_*$ arrays; a stated,
justified tolerance on continuous 80,000-step DDE arrays.** A uniform 0-ULP gate would be stricter
than the field's own definition of *reproduced*, and would fail for reasons that do not change any
main claim.

The requirement the policy adds is that the tolerance must be **stated and justified**, not chosen
to make the build pass. That is a documentation obligation attached to the CI gate, and it should be
written down before the gate is wired.

### 4.2 The repository would not qualify for *Artifacts Available*

The policy defines artifacts for that badge as *"placed on a publicly accessible, archival
repository with a DOI / persistent identifier"*, and the SIGIR implementation guidance is blunt:
artifacts *"do not need to have been formally evaluated"* for this badge, but a personal or bare
GitHub URL is not archival.

AIEFS is a public GitHub repository with **no DOI, no release, and no tag** (verified in Part 1:
`Releases / tags: 0 / 0`). So the artifact set — which is unusually well-documented for an
independent project, with SHA-256 inventories, frozen authority locks and reproducible run
directories — would still not earn the one badge that only asks for a stable identifier.

**Cheap fix:** mint a DOI (Zenodo or equivalent) per frozen run directory, or one per release tag.
This is hours of work, it is entirely non-scientific, and it converts a large amount of existing
rigor into an auditable, citable artifact. Worth doing before any submission.

### 4.3 A trap worth recording

ACM **swapped** "reproduced" and "replicated" between v1.0 and v1.1 (May 2020). Any older paper
using these terms may mean the inverse. When citing badge terminology from before mid-2020, check
the version. Current sense: *Reproduced* = different team **with** author artifacts; *Replicated* =
different team **without**.

---

## 5. F26 — Acta Numerica independently confirms the split-state discontinuity concern

**[VERIFIED]** [LIT-0035] (which resolves `LEAD-0007`) supersedes [LIT-0029] as the citation of
record for DDE numerics, and it names the issue directly:

> *"some critical situations have been recently investigated in connection to specific classes of
> equations, such as **the accurate location of discontinuity points**..."*

This is Round 3's F19, arrived at independently by the field's own survey: an ablation at a split
time injects a discontinuity into the history, and locating it accurately is named as a critical
issue rather than a detail.

Two further points from the abstract that matter for the platform:

1. *"the initial problem for RFDEs is an infinite-dimensional problem"* — consistent with
   [LIT-0010] and with the $N + N^2$ dimension count in [LIT-0018].
2. *"numerically solving initial problems for RFDEs is a difficult task that cannot be founded on
   the mere adaptation of well-known methods for ordinary, partial or integro-differential
   equations"*. If the AIEF platform's Euler step is justified by its behaviour on the ODE
   subsystems, that justification does not transfer. Worth checking, because the frozen-driver
   cocycle work already shows the audit thinking in ODE-step terms (`1 - gamma dt`).

Also note: this paper explicitly declines to treat stability, deferring to [LIT-0029]. So the two
citations are complementary, not substitutable — use [LIT-0035] for method and discontinuity
behaviour, [LIT-0029] for stability.

---

## 6. F27 — `CF04` does not need a citation, and I checked rather than assumed

Round 2 declared the six unmapped `CF` claims "correctly unmapped". Round 4 tested that claim for
the one I was least sure about: `CF04`, *"kernel preservation is equivalent to a row-space
intertwining factorization $CD = \Gamma C$."*

I searched the intertwining/commutant literature expecting to find a home for it. What came back
was differential-operator intertwining (Darboux transformations), representation-theoretic
intertwiners, and noncommutative-function-theory kernels. None of it is the right frame.

The reason is that `CF04` is the elementary factorization fact: for linear maps, $\ker A \subseteq
\ker B$ if and only if $B$ factors through $A$. That is a first-course linear algebra theorem, not a
research literature. Citing Darboux transformations to it would be precisely the decorative
citation this inbox exists to avoid.

**Conclusion: the Round 2 judgement holds for `CF04`, and I now know why** — not "no source found"
but "this is textbook material with no research literature to point at". The other five `CF` claims
are likewise unmapped for structural reasons: `CF07` is a symmetry/spectral invariance condition,
and `CF09`–`CF12` are asymptotics and open conjectures.

---

## 7. Coverage and state

| Measure | R1 | R2 | R3 | **R4** |
|---|---|---|---|---|
| Sources | 16 | 28 | 33 | **38** |
| Claims with a source | 19/43 | 22/43 | 24/43 | **24/43** |
| Studies with a source | 9/14 | 11/14 | 11/14 | **11/14** |
| Domains | 7/8 | 8/8 | 8/8 | **8/8** |
| Open leads | 3 | 3 | 1 | **0** |

Stance mix this round: 4 `METHOD`, 1 `CAUTION`. All five are `VERIFIED_METADATA`.

**The inbox is now lead-clean.** Every retrieved-but-unconfirmable item from four rounds has been
either promoted with a verified record or explicitly retired.

### Saturation, stated honestly

Claim coverage has been flat at 24/43 for two rounds and will stay there without one of three
things, none of which a search tool can supply:

1. **Paywalled full text.** Several entries are `VERIFIED_METADATA`; reading the actual theorems
   would let content claims be attributed precisely rather than to abstracts.
2. **Forward citation analysis.** The map is recall-limited by construction. A citation-graph pass
   from [LIT-0018]/[LIT-0028] would find the applied delay-plasticity literature that search misses.
3. **New claims.** The unmapped remainder is 12 retired `S` rows (deliberately unmapped), 6 `CF`
   rows that are textbook or conjectural, 1 claim with no appropriate literature (`EMP-AIEF14-03`),
   and 3 studies with no external frame (`HISTORICAL_PROJECT_ORIGINS`, `AIEF_1_4_PIVOT_PILOT`,
   `AIEF_1_4_PROPOSAL_EQUALIZATION`).

Adding more sources now would pad the bibliography without changing any claim's status. Round 5
should therefore change *what it is doing* rather than keep searching: the highest-value remaining
work is not more sources, it is a **claim-by-claim adjudication table** that takes the 24 mapped
claims and states, for each, whether the literature supports, bounds, or contradicts it — which is
the deliverable this whole exercise was for.

---

## 8. Proposed registry amendments — **for owner approval, not applied**

| Target | Proposed change | Basis |
|---|---|---|
| `REJ-LOCK-03` | **Supersedes Round 3 §8.** Cite [LIT-0018] and [LIT-0028] as support; demote [LIT-0030] to context, noting the uniform-$k$ precondition that AIEF networks violate | F24 |
| `LEAN-CF-01` | Record the formalization standard: general rank–incidence theorem over a commutative ring, $K_3$ as corollary. Cite [LIT-0037] as the model and [LIT-0034]/[LIT-0036] as the platform | F23 |
| `AIEF_1_4_SPLIT_STATE_ABLATION` | Strengthen Round 3's note: discontinuity *location* accuracy is a named critical issue in the DDE numerics literature, not only a propagation concern | [LIT-0035] |
| `IMPL-MODULAR-01` | Record that the two-tier tolerance is the ACM standard's own requirement, and that the tolerance must be stated and justified | [LIT-0038] |
| Repository level | Mint DOIs for frozen run directories / releases so artifacts can claim *Artifacts Available* | [LIT-0038] |
| — | **Not a literature amendment:** F16's four registry repairs remain outstanding and belong to the registry workstream (F22) | — |

---

## 9. What Round 4 did not do

- Did not modify `registry/`, `audits/engineering/`, or any pre-existing file. Confirmed by diff.
- Did not rewrite the LIT-0030 snapshot, despite now having better information — protocol, and the
  correction lives in §3.
- Did not add sources merely to move the claim count.
- Did not open paywalled full texts, do forward-citation analysis, or verify any numbered theorem.
