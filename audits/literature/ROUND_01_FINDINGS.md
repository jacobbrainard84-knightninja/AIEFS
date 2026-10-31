# Literature Review — Round 1: Foundations and the Four Falsified Claims

**Round:** 1 · **Date:** 2026-10-30 · **Sources added:** 16 · **Leads opened:** 3
**Registry:** [`SOURCES.csv`](SOURCES.csv) · **Leads:** [`LEADS.csv`](LEADS.csv) · **Verifier:** `verify_literature.py`

---

## 0. Bottom line

The repository argues entirely from first principles. **Verified:** of the 18 tracked Markdown
files, **not one contains a DOI, an arXiv identifier, or an ISBN** (`grep -rlE 'doi\.org|arxiv\.org|arXiv:[0-9]{4}|ISBN'` over
`git ls-files '*.md'` returns empty), and no file contains a `## References` section. Round 1 is
therefore not an enrichment of an existing bibliography — it is **the first external bibliography
this project has ever had**.

That reframes the job. The useful question is not "what should we cite?" but:

> For each claim the project already asserts, does the literature **support**, **contradict**, or
> **merely contextualise** it — and does that change the claim's status?

Applying that to the four claims the project already formally rejected (`REJ-SPEC-01`,
`REJ-SPEC-02`, `REJ-K3-04`, `REJ-COHORT-05`) plus the two live caveats (`CAVEAT-MS-8.4`, `CF08`)
produces a clean result: **all six are independently corroborated, and in four cases the
literature supplies the formal object the project was reaching for but did not name.**

---

## 1. Method, and what the verification levels mean

Every record in `SOURCES.csv` was produced by an actual retrieval on 2026-10-30 and carries a
SHA-256-hashed snapshot in `snapshots/`. Two levels are citable:

| Level | Meaning | Count |
|---|---|---|
| `VERIFIED_FULL` | Canonical landing page opened and read; abstract quoted from that page | 4 |
| `VERIFIED_METADATA` | Complete bibliographic record confirmed from a search-index rendering of the canonical page | 12 |
| `SEARCH_SNIPPET_ONLY` | **Not citable.** Lives in `LEADS.csv` only | 3 leads |

Two honest limits, stated up front:

- **No paywalled full text was opened.** Where a source is credited with a theorem, what has been
  read is its abstract or its cited statement — not the numbered theorem in a PDF. Statements below
  are phrased to match that ceiling.
- **No forward-citation analysis.** The field map is search-driven and therefore recall-limited. A
  genuine gap is possible and is recorded as a gap, not as an absence in the literature.

Claims in this document are tagged **[VERIFIED]** (ran it / read it), **[INFERRED]** (follows from
what was read), or **[SUSPICION]** (flagged, not established). This follows the convention already
used in `AI Agent Audits/`.

---

## 2. Findings

### F1 — The four rejections are correct, and three of them were rejected for the right *reason*

**[VERIFIED]** Each of the four falsified claims maps onto a distinct, named failure mode in the
literature. This matters because a rejection that is merely empirical ("we tried it, the numbers
were bad") is weaker than a rejection that names the structural reason it *had* to be bad.

| Rejected claim | Named failure mode | Source |
|---|---|---|
| `REJ-SPEC-01` 8D POD compression "faithfully captures" dynamics | Truncating to a subspace that is not invariant; spurious/aliased spectrum | [LIT-0003], [LIT-0005], [LIT-0006] |
| `REJ-SPEC-02` ε = 1e-8 Jacobian resolves spectrum at 4.44e-14 ties | Difference step ≫ the feature being resolved; non-differentiability at ties | [LIT-0014], [LIT-0009] |
| `REJ-K3-04` 856 K3 instances "dominate" | Raw motif count without a degree-matched null ensemble | [LIT-0015] |
| `REJ-COHORT-05` N=40 "independent" paired seeds | Pseudoreplication: non-independent units analysed as independent | [LIT-0001], [LIT-0002] |

The strongest single upgrade is `REJ-SPEC-01`. Haller & Ponsioen define the object the compression
implicitly assumed and never established — a spectral submanifold: *"the unique, smoothest,
nonlinear continuations of spectral subspaces of the linearized, unforced limit"*, on which *"the
dynamics... will serve as a mathematically exact reduced-order model"* [LIT-0003]. Kaiser, Kutz &
Brunton name the symptom that a finite projection produces instead: *"sometimes the
finite-dimensional approximation is not closed and spurious eigenfunctions may appear"* [LIT-0005].
Herwig et al. supply the acceptance test that was missing — a residual criterion — and warn that
*"spectral features can arise even when the corresponding eigenfunctions lie outside the chosen
space"* [LIT-0006].

Two separate summaries in the repository already quantify the failure (24,323.8 % off-subspace
leakage; `var(slow)/var(full) = 7.5e35`). Those numbers are now interpretable as *the size of the
projection defect*, which is the quantity the literature says must be controlled or carried as an
explicit error term.

### F2 — `REJ-SPEC-02` and `CAVEAT-MS-8.4` are **two different defects that were being treated as one**

**[INFERRED]** This is the most consequential finding of the round for the live claim set.

The ε = 1e-8 finite-difference Jacobian problem and the Draft Corollary 8.4 left-covector problem
are often discussed together because both concern the exceptional $K_3$ spectrum near ties. They
have different causes and different fixes:

1. **Numerical**: ε = 1e-8 is roughly five to six orders of magnitude larger than the 4.44e-14 tie
   margin it is meant to resolve. Goldberg's tutorial fixes the scale: this is the rounding-error
   regime, and the reported spectrum is dominated by the difference step rather than the dynamics
   [LIT-0014]. **Fix:** branch-preserving analytic derivatives, not smaller ε.
2. **Structural**: at a winner tie the map $A_\varepsilon(x) = M(Ax)\,x$ with min-selected endpoint
   winners is piecewise-smooth but not differentiable. There is no Jacobian to compute; the correct
   object is a generalized gradient or a directional derivative [LIT-0009]. **Fix:** report
   one-sided derivatives at ties (which the audit's `CF03` already does — *"the admissibility map is
   exactly affine on multiplier-controller fibers, including active endpoint ties"* — this is the
   right move and should be stated in Clarke's terms).

Separately, `CF08` / `CAVEAT-MS-8.4` is a **non-normality** problem: when the finite-step operator
is non-normal, left and right eigenvectors are not orthogonal, so a "pointwise left covector" is a
property of one eigenvector normalization rather than an invariant of the operator [LIT-0008]. The
concrete defect already derived in `audits/scientific/` — the residual
$V^\top D\mathcal{A}_\varepsilon(x_G) - s_k V^\top = -\frac{s_k}{q^+ + \varepsilon}(C_G \operatorname{diag}(x_G) V)^\top C_G \neq 0$
away from edge-uniform $x_G$ — is exactly the non-orthogonality term Trefethen–Embree describe.

**[SUSPICION]** The reason the draft Corollary held was that it was checked, or reasoned about, only
at edge-uniform $x_G \propto \mathbf 1$, where the offending term vanishes by symmetry. If so, the
correction is a one-line scope statement rather than a retraction. Round 2 should test this
directly by evaluating the residual at a deliberately non-uniform mature state.

### F3 — `REJ-K3-04` needs a null model, and the 26-vs-856 discrepancy is the whole story

**[VERIFIED]** Milo et al. define a network motif as a pattern occurring *"at numbers that are
significantly higher than those in randomized networks"* [LIT-0015]. A raw instance count is not a
motif claim at all.

The audit already found **26 isolated $K_3$ components**, against **856 raw $K_3$ instances**
reported by the rejected scan. Those two numbers are consistent under a null model in which most
$K_3$s overlap heavily inside a few dense components. **The project reached the correct conclusion
but has not yet stated it in the vocabulary the field uses.** A restatement as a z-score against a
degree-preserving configuration-model ensemble would convert `REJ-K3-04` from "we counted again and
got a different number" into a properly normalised negative result. This is the cheapest available
upgrade to an existing registry entry and is proposed as a Round 5 target.

### F4 — `LEAN-CF-01` is a correct specialization of a classical theorem (which is the right status)

**[INFERRED]** `LEAN-CF-01` formalizes $\ker C_{\{2,7\}} = \operatorname{span}\{(1,-1,-1)\}$ for the
2×3 controller incidence matrix. Godsil & Royle give the general statement: for a graph with $n$
vertices and $c$ components, $\operatorname{rank}(D) = n - c$ over $\mathbb{R}$, hence nullity
$= |E| - (n-c)$ in edge coordinates [LIT-0011].

The 2-vertex, 3-edge multigraph with $c = 1$ gives $\operatorname{rank} = 1$ and nullity $2$ in edge
coordinates, and the one-dimensional kernel in the node/controller formulation is the corresponding
statement. So `LEAN-CF-01` is **a machine-checked instance of a standard theorem**, not new
mathematics. Its registry status — `Formalized theorem`, with the Lean package showing no `sorry` —
is therefore exactly right, and it should **not** be promoted in narrative. The value of the Lean
work is that a load-bearing kernel used in `CF06` is now machine-verified; that value is real and
does not require novelty.

Practical consequence: if the project ever wants the Lean result to carry weight beyond the
specific $C_{\{2,7\}}$, the statement to formalize is the rank–incidence theorem itself, in a form
Mathlib can consume. Proposed as a Round 4 target.

### F5 — The cross-host 4.405e-13 drift is expected behaviour, and `IMPL-MODULAR-01`'s scope boundary is already correct

**[VERIFIED]** The audit records `max_abs_diff = 0.000e+00` on discrete $P_*$ topology arrays and
`4.405e-13` on continuous 80,000-step DDE arrays across hosts, and `0.000e+00` everywhere on the
same host.

This is precisely what reproducible-summation work predicts. Bit-reproducibility is not a property
of "the same code": it requires controlled summation order, and is achieved only by construction —
pre-rounding to a common exponent boundary and a fixed-width accumulator [LIT-0012], [LIT-0013] —
or it is lost to differences in libm transcendental rounding and compiler reassociation [LIT-0014].

`IMPL-MODULAR-01` already scopes itself to *"an identical host/libm environment"*, which is the
correct boundary. The literature makes that boundary **citable rather than merely cautious**, and
it settles the Stage 7 CI design question: a 0-ULP gate is correct for discrete $P_*$ arrays and
unattainable in principle for continuous DDE arrays. Stage 7 therefore needs a **two-tier tolerance
gate**, and the second tier must be justified by a stated bound, not chosen to make the build pass.

### F6 — `REJ-COHORT-05` is textbook, and it is the project's strongest independent vindication

**[VERIFIED]** Hurlbert's 1984 paper is the canonical statement: of 176 experimental studies,
pseudoreplication *"occurred in 27% of them, or 48% of all such studies that applied inferential
statistics"* [LIT-0001]. The project independently detected the same defect, rejected the cohort,
and rebuilt on disjoint seed sets.

Cameron & Miller supply the correct inferential frame for what replaced it — errors *"independent
across clusters but correlated within clusters"*, with the warning that *"default standard errors
can greatly overstate estimator precision"* [LIT-0002].

**Actionable open item [SUSPICION]:** `EMP-AIEF13-01` reports a 95 % bootstrap CI on a paired
contrast. If that interval is a naive percentile bootstrap over seeds, it is adequate at N = 100 but
is not the preferred construction in this literature; the wild cluster bootstrap is. Round 2 should
read `AIEF_1_3_paired_statistics_updated.py` and either confirm the variant used or add a
sensitivity line. **This does not impugn the effect size** (`D_B = +0.305909`, `dz = 8.434`) — an
effect that large is not bootstrap-dependent. It concerns only the width of the reported interval.

### F7 — Two 2026 preprints are close neighbours to live AIEF-1.4 programmes, and neither is cited anywhere in the repository

**[VERIFIED]** Both were opened and read in full this round.

- **Abbasciano, Buza & Haller (2026), arXiv:2605.22299** [LIT-0004] — SSM theory extended to delay
  differential equations, giving *"purely data-driven, SSM-reduced, delay-free ODE models"* that
  *"require no information about the form of the underlying DDE, or about the number and magnitude
  of the delays it contains"*, and which *"remain predictive even for chaotic dynamics"*.
- **Ruschel, Hristov, Meijer, Coombes & Nicks (2026), arXiv:2605.23520** [LIT-0016] — *"a framework
  for collective frequency selection and attractor formation by means of delay plasticity"*, where
  adaptive axonal delays produce *"frequency selection and explosive network relaxation
  oscillations"*.

Two consequences, and they point in opposite directions.

1. **Priority risk.** A mechanism close to `EMP-AIEF14-02` — adaptive delayed history mediating
   network-level recovery/selection — is under active independent investigation. The repository
   should state its novelty boundary explicitly and early: its contribution is **the ablation design
   and the topological-recovery metric**, not the existence of delay-driven frequency selection.
   `AIEF_1_4_TWINDOW_SENSITIVITY` and `AIEF_1_4_MATCHED_PHASE_ABLATION` are experiments; they are
   not claims of a new mechanism.
2. **A free upgrade.** `REJ-SPEC-01` is currently a negative result with nothing behind it.
   [LIT-0004] is a published, citable, delay-aware reduction for exactly this class of system. A
   future spectral programme no longer has to invent a baseline — it has a target to reproduce or
   beat, which is a materially stronger position than "we tried POD and it failed".

### F8 — The delay system's state space is the history, which retroactively explains `EMP-AIEF14-01`

**[INFERRED]** Hale & Verduyn Lunel formalize the point: for a delay equation the state at time $t$
is the history segment $x_t \in C([-r,0],\mathbb{R}^n)$, defined by
$x_t(\theta) = x(t+\theta)$ [LIT-0010].

Under that definition, `EMP-AIEF14-01` — *"Adaptive edge matrix $B$ is not a unique memory
bottleneck: resetting $B$ at the split time reconstructs mature network topology almost identically"*
— is **expected, not surprising**. Removing one component of a state that is itself the history
leaves the history intact. The claim is correct, and the literature supplies the reason it could
not have come out otherwise. Worth stating in `claims.csv`, because "we found $B$ is redundant"
reads as an empirical curiosity while "the state space contains the history, so no component is
privileged" reads as a structural fact.

---

## 3. Coverage table

Stance vocabulary: `SUPPORTS` (corroborates a repo claim), `CONTRADICTS` (would falsify one),
`CAUTION` (bounds what a claim may assert), `METHOD` (supplies technique or frame),
`CONTEXT` (situates without adjudicating).

| ID | Source | Year | Stance | Bears on | Level |
|---|---|---|---|---|---|
| [LIT-0001] | Hurlbert, *Pseudoreplication…*, Ecol. Monogr. 54(2):187–211 | 1984 | SUPPORTS | `REJ-COHORT-05`, `AIEF_1_3_DISJOINT_100SEED` | METADATA |
| [LIT-0002] | Cameron & Miller, *A Practitioner's Guide to Cluster-Robust Inference*, JHR 50(2):317–372 | 2015 | METHOD | `EMP-AIEF13-01`, `EMP-AIEF13-02` | METADATA |
| [LIT-0003] | Haller & Ponsioen, *Nonlinear normal modes and spectral submanifolds*, Nonlinear Dyn. 86:1493–1534 | 2016 | SUPPORTS | `REJ-SPEC-01`, `S09` | METADATA |
| [LIT-0004] | Abbasciano, Buza & Haller, *Data-Driven Reduced Modeling of Delayed Dynamical Systems via SSMs*, arXiv:2605.22299 | 2026 | METHOD | `REJ-SPEC-01`, `AIEF_1_4_TANGENT_AND_COCYCLE` | **FULL** |
| [LIT-0005] | Kaiser, Kutz & Brunton, *Data-driven discovery of Koopman eigenfunctions for control*, MLST | 2021 | CAUTION | `REJ-SPEC-01`, `S09`, `S16` | METADATA |
| [LIT-0006] | Herwig, Colbrook, Junge, Koltai & Slipantschuk, *Avoiding spectral pollution…*, arXiv:2507.16915 | 2025 | SUPPORTS | `REJ-SPEC-01`, `S09` | **FULL** |
| [LIT-0007] | Mohr, Fonoberova & Mezić, *Koopman Reduced Order Modeling with Confidence Bounds*, arXiv:2209.13127 | 2022 | METHOD | `REJ-SPEC-01`, `S09` | **FULL** |
| [LIT-0008] | Trefethen & Embree, *Spectra and Pseudospectra*, Princeton UP | 2005 | CAUTION | `CAVEAT-MS-8.4`, `CF08`, `REJ-SPEC-02` | METADATA |
| [LIT-0009] | Clarke, *Optimization and Nonsmooth Analysis*, Wiley 1983 / SIAM 1990 | 1983 | METHOD | `REJ-SPEC-02`, `CF03`, `S04` | METADATA |
| [LIT-0010] | Hale & Verduyn Lunel, *Introduction to Functional Differential Equations*, Springer AMS 99 | 1993 | SUPPORTS | `AIEF_1_4_TANGENT_AND_COCYCLE`, `S11` | METADATA |
| [LIT-0011] | Godsil & Royle, *Algebraic Graph Theory*, GTM 207 | 2001 | SUPPORTS | `LEAN-CF-01`, `CF06` | METADATA |
| [LIT-0012] | Demmel & Nguyen, *Parallel Reproducible Summation*, IEEE TC 64(7):2060–2070 | 2015 | CAUTION | `IMPL-MODULAR-01`, `PLATFORM_V1_V4` | METADATA |
| [LIT-0013] | Ahrens, Demmel & Nguyen, *Algorithms for Efficient Reproducible Floating Point Summation*, ACM TOMS | 2020 | METHOD | `IMPL-MODULAR-01` | METADATA |
| [LIT-0014] | Goldberg, *What every computer scientist should know about floating-point arithmetic*, ACM CSUR 23(1):5–48 | 1991 | CAUTION | `IMPL-MODULAR-01`, `REJ-SPEC-02` | METADATA |
| [LIT-0015] | Milo et al., *Network Motifs*, Science 298(5594):824–827 | 2002 | CAUTION | `REJ-K3-04`, `S07` | METADATA |
| [LIT-0016] | Ruschel, Hristov, Meijer, Coombes & Nicks, *Network Attractors driven by Time-Delay Plasticity*, arXiv:2605.23520 | 2026 | CONTEXT | `EMP-AIEF14-01`, `EMP-AIEF14-02` | **FULL** |

**Coverage (computed, not estimated):** **19 of the 43 claims** and **9 of the 14 studies** now
carry at least one external source. Stance balance is 5 `SUPPORTS` / 5 `METHOD` / 5 `CAUTION` /
1 `CONTEXT`.

The **five unmapped studies** are `HISTORICAL_PROJECT_ORIGINS`, `AIEF_1_0_TO_1_2_FOUNDATIONAL`,
`AIEF_1_4_PIVOT_PILOT`, `AIEF_1_4_CONTROLLER_FIBER` and `AIEF_1_4_PROPOSAL_EQUALIZATION`. The
`CF01`–`CF12` block is mapped only at `CF03`, `CF06` and `CF08`. That remainder is the Round 2–5
backlog, not an oversight — and it is the reason Round 2's first target is nonsmooth/active-set
analysis, which is the literature the whole `CF` block depends on.

---

## 4. Proposed registry amendments — **for owner approval, not applied**

Nothing in `registry/` was modified in this round. The following are proposals; each names the
claim and the change.

| Claim | Proposed change | Basis |
|---|---|---|
| `REJ-SPEC-01` | Add a `literature_basis` note naming the invariance requirement and the spectral-pollution failure mode; cite the delay-aware SSM alternative as the constructive replacement | [LIT-0003], [LIT-0005], [LIT-0006], [LIT-0004] |
| `REJ-SPEC-02` | Split the caveat into the **numerical** defect (ε ≫ tie margin) and the **structural** defect (non-differentiability at ties). Record that `CF03`'s one-sided handling is the correct remedy | [LIT-0014], [LIT-0009] |
| `CAVEAT-MS-8.4` | Restate as a non-normality/eigenvector-basis statement rather than an isolated algebra slip | [LIT-0008] |
| `REJ-K3-04` | Restate as a normalized negative result against a degree-preserving null ensemble | [LIT-0015] |
| `EMP-AIEF14-01` | Add the structural reason: the state space is the history, so no single component is privileged | [LIT-0010] |
| `LEAN-CF-01` | Note that this is a verified instance of the rank–incidence theorem, and keep status `Formalized theorem` (do **not** promote) | [LIT-0011] |
| `IMPL-MODULAR-01` | Record that the scope boundary is a known property of floating-point summation, and that Stage 7 CI requires a two-tier tolerance gate | [LIT-0012], [LIT-0013], [LIT-0014] |

---

## 5. Leads opened (not citable)

- **`LEAD-0001`** — *The Multiverse of Dynamic Mode Decomposition Algorithms*, arXiv:2312.00137.
  On target (DMD spectral pollution); author list unconfirmed.
- **`LEAD-0002`** — *Synchronization and resilience in the Kuramoto white matter network model with
  adaptive state-dependent delays*, DOI 10.1186/s13408-020-00091-y. Author list not captured.
- **`LEAD-0003`** — Oseledec MET course notes (Kelliher, UC Riverside). A teaching source; the
  primary citation for the cocycle formalism should be Arnold (1998), which was **not verified**
  this round and is therefore not cited.

`LEAD-0003` is worth a note: the repository's tangent/cocycle programme names a "history cocycle",
and the correct primary reference is almost certainly Arnold's *Random Dynamical Systems*. Round 1
declined to add it because it could not be verified. Recorded as a gap rather than papered over.

---

## 6. What Round 1 did not do

- Did not open any paywalled full text. No numbered theorem was read in the original.
- Did not run forward-citation / citation-graph analysis, so the map is recall-limited.
- Did not verify which bootstrap variant `AIEF_1_3_paired_statistics_updated.py` uses (F6).
- Did not test the F2 suspicion at a non-uniform $x_G$ (deferred to Round 2).
- Did not look at nonsmooth-dynamics or causality-in-dynamical-systems literature at all. Both are
  large and both are directly load-bearing; they are the Round 2 spine.
