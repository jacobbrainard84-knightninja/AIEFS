# Literature Review — Round 2: The Nonsmooth Spine, Causal Identification, and the Cocycle Question

**Round:** 2 · **Date:** 2026-10-30 · **Sources added:** 12 (total 28) · **Leads:** 3 resolved, 3 opened
**Registry:** [`SOURCES.csv`](SOURCES.csv) · **Leads:** [`LEADS.csv`](LEADS.csv) · **Round 1:** [`ROUND_01_FINDINGS.md`](ROUND_01_FINDINGS.md)

---

## 0. Bottom line

Round 2 closed the two gaps Round 1 named as its own failures, and opened one it did not anticipate.

The `CF01`–`CF12` block — the controller-fiber mechanism, twelve claims, no literature whatsoever
after Round 1 — now has a complete methodological chain: piecewise-smooth dynamical systems
[LIT-0020], lexicographic differentiation [LIT-0021], and a computable automatic-differentiation
route to it [LIT-0022]. The result is not merely that the CF block is *defensible*. It is that
`CF03`'s handling of winner ties, which the audit presents as care taken at a singularity, turns
out to be **the unique canonical derivative**, and the tool that computes it is standard.

Domain `L4` (cocycles, Lyapunov spectrum) was the largest hole in the Round 1 map and is now
filled [LIT-0019]. It arrives with a problem attached: a cocycle is an identity, not a name, and
the repository has not demonstrated the identity.

Two findings are `SUPPORTS` and one is a clean negative result requiring no action. One is the
most important `CAUTION` the inbox has produced so far.

---

## 1. Method

Unchanged from Round 1. Every row came from an in-session retrieval on 2026-10-30 and carries a
SHA-256-hashed snapshot. Levels: `VERIFIED_FULL` 7 (up from 4), `VERIFIED_METADATA` 21. No paywalled
full text was opened; no numbered theorem is attributed to a source that was not read.

Two process changes this round, both recorded rather than silent:

- `_build_round02.py` is **idempotent** — it drops and rebuilds its own rows, so a rerun reproduces
  the same 28 sources rather than appending duplicates. Had it been a blind append, the CF
  remapping in §2 would have created phantom duplicates.
- `LEADS.csv` gained `status` and `resolved_as` columns so a resolved lead is visibly retired.
  Gate `6/7` now enforces that `RESOLVED` points at a real source and that `OPEN` carries no pointer.

---

## 2. Findings

### F9 — The `CF` block now has a complete chain, and it upgrades `CF03` from "careful" to "canonical"

**[INFERRED]** This is the substantive result of the round.

The admissibility map is $A_\varepsilon(x) = M(Ax)\,x$, with endpoint winners selected by
$\min(\text{scale}_i, \text{scale}_j)$. Three facts now hold together:

1. Such a map is piecewise-smooth, and piecewise-smooth systems form a field with its own
   vocabulary precisely because *"distinctive phenomena unique to discontinuous systems... fall
   outside the usual methodology for smooth dynamical systems"* [LIT-0020].
2. At a winner tie the branchwise Jacobian does not exist. But for a piecewise-differentiable
   function, once a basis is fixed the **lexicographic derivative is unique**, and *"the system of
   lexicographic derivatives along a fixed basis correctly represents the corresponding nonsmooth
   function (Newton-Leibnitz formula)"* [LIT-0021].
3. That derivative is computable: *"piecewise differentiable functions are lexicographically smooth
   in the sense of Nesterov, and... lexicographic derivatives of these functions comprise a
   particular subset of both the B-subdifferential and the Clarke Jacobian"* [LIT-0022], with
   differentiation rules for `min`, `max`, `mid` and `abs` — and `min` is exactly the primitive the
   winner map is built from.

So `CF03` — *"the admissibility map is exactly affine on multiplier-controller fibers, including
active endpoint ties"* — is not an ad hoc tie-handling convention. It is a statement that the map
is piecewise-affine, and the one-sided derivative the audit computes is the lexicographic
derivative, which exists and is unique. **`CF03` can be restated in those terms and thereby become
stronger.**

Note the direction of the hierarchy: Nesterov explicitly argues the lexicographic subdifferential
gives *"a more rigorous selection of a candidate optimal solution than the subdifferential of
Clarke"* [LIT-0021]. Round 1 reached for Clarke as the correct object at ties [LIT-0009]. That was
right, but lexicographic is the sharper instrument and it is the one the audit was already
effectively using.

On the spectral side, [LIT-0017] is the map the rejected programme never had. It sorts DMD into
three families — linear-regression, Galerkin, and structure-preserving — and treats the relation
between DMD eigenvalues and Koopman spectral properties as the central question rather than a
formality. The rejected 8D compression was a single linear-regression variant with no convergence
argument and no residual check; the review enumerates what else was on the table in 2023. This does
not reopen `REJ-SPEC-01` — it explains why the rejection was inevitable given the method chosen, and
what a future attempt would have to pick up.

This also disposes of the last hope for `REJ-SPEC-02`. Khan & Barton state the finite-difference
objection structurally: finite differencing is unsuitable for nonsmooth functions because it
*"'steps' over nonsmooth points"* [LIT-0022]. A smaller $\varepsilon$ does not approach the
derivative; it lands at a different branch. The rejection was correct and is now grounded in the
literature rather than in an observation about tolerances.

### F10 — A "cocycle" is an identity, and the repository has not shown it holds — **open item**

**[SUSPICION]** This is a new problem, and I could not resolve it in this round.

`AIEF_1_4_TANGENT_AND_COCYCLE` is titled around an *exact history-cocycle*. Arnold's definition
[LIT-0019] requires, for a cocycle $\Phi$ over a measure-preserving shift $\theta$:

$$\Phi(t+s,\ \omega) \;=\; \Phi(t,\ \theta_s\omega)\,\Phi(s,\ \omega).$$

That is a composition law. It is what makes the multiplicative ergodic theorem applicable and what
licenses the word "cocycle" as opposed to "propagator" or "linearization".

**Round 2 did not verify that the AIEF history operator satisfies it.** Round 1 and Round 2 both
mapped `AIEF_1_4_TANGENT_AND_COCYCLE` to sources about DDE state spaces [LIT-0010] and cocycle
theory [LIT-0019] without checking the identity itself. Two possibilities, and they have different
consequences:

- If the operator composes correctly over the history shift, the claim is well-founded and should
  carry an explicit statement of the law, because that is the whole content of the word.
- If it does not, the construction is a **linearization along a trajectory**, which is a perfectly
  good object, but naming it a cocycle is an overclaim that would not survive a specialist reader.

**Proposed Round 3 action (cheap, testable):** write a single check that composes the tangent map
over two successive legs and compares it to the map over the concatenated leg, at one frozen seed
from `runs/5a9f093a2fe0`. Either result is publishable; only the unexamined case is not.

### F11 — Phase reduction provably discards delay information

**[VERIFIED]** [LIT-0028] is explicit: *"the delays are often absorbed in the reduced description as
a phase shift. The reduced system is a set of ODEs that loses some information about the full delay
differential equation (DDE) system. We adopt a less restrictive approach..."*

This cuts two ways and both are useful.

- **As a constraint:** any AIEF claim that describes a delay effect through a phase variable
  inherits that loss and must say so. This is the sharpest available boundary on what the
  `T_window`/matched-phase programme may assert about *mechanism*.
- **As a defence:** the AIEF-1.4 platform keeps the delay explicit in the state rather than
  collapsing it to a phase shift. That is exactly the "less restrictive approach" the paper
  recommends, and the repository should say so instead of leaving it as an unstated design choice.

Worth noting the adjacency: [LIT-0028] and [LIT-0016] share three authors (Ruschel, Nicks,
Coombes), and [LIT-0018] is their 2020 precursor. Three papers across six years on adaptive delay
and network coherence. The priority-risk note from Round 1 (F7) is not a single preprint — it is a
programme.

### F12 — Schreiber supplies the formal reason the matched-phase design exists

**[VERIFIED]** `EMP-AIEF14-02` claims that delayed phase/EMA history mediates post-ablation recovery
*"independently of instantaneous phase mismatch"*, and the design separates the two by matching
split-time phase across conditions.

Schreiber's diagnosis of the naive alternative is the same problem in another field: *"The standard
time delayed mutual information fails to distinguish information that is actually exchanged from
shared information due to common history and input signals"* [LIT-0025].

That is the confound. If two conditions share a history, a statistic computed over that history
cannot separate transmission from common inheritance. Schreiber's remedy is conditioning; AIEF's
remedy is an intervention that holds the confound fixed. Different instruments, same logic — and
the AIEF version is the stronger one, because it removes the confound by construction rather than by
estimation.

**Consequence:** `EMP-AIEF14-02` currently justifies matching empirically. It can now justify it
structurally, and that is a one-sentence upgrade to the claim's `scope_boundary_and_caveat`.

### F13 — The AIEF-1.3 result is an intervention, not a Granger test — and the claim should say so

**[INFERRED]** Granger defines causality as incremental predictability conditional on history, and
already warns that apparent causality *"often arises due to slowness in recording information or
because a sufficiently wide class of possible causal variables has not been used"* [LIT-0023].
Sugihara et al. then showed that the framework is limited for coupled nonlinear systems, extending
to *"nonseparable weakly connected dynamic systems (cases not covered by the current Granger
causality paradigm)"* [LIT-0024].

Together these pin the two poles, and the AIEF-1.3 design is not at either. It does not infer
causality from observables; it **intervenes on the mechanism** and measures the downstream
structural effect. That is a stronger identification strategy than either pole, and the registry
currently leaves the word "causal" undefined while using it.

**Recommendation:** add one clause to `EMP-AIEF13-01` and `EMP-AIEF13-02` stating that the effect is
identified by intervention (shuffle_R / no_mu), not by predictability, and that this is why the
Granger-vs-CCM debate does not apply. Cheap, and it pre-empts a reviewer objection.

### F14 — Bootstrap: **no action required**. A clean negative result

**[VERIFIED]** Webb demonstrates that standard bootstrap procedures *"perform poorly with fewer than
eleven clusters"*, and that with few clusters *"the wild cluster bootstrap results in p-values that
are not point identified"*, with a 6-point weight distribution as the remedy [LIT-0027]. The wild
cluster bootstrap itself originates with Cameron, Gelbach & Miller [LIT-0026].

Both AIEF cohorts exceed the threshold: **N = 100** (disjoint, `runs/c3da1ac707bf` +
`runs/73dca37cf93f`) and **N = 40** (the rejected cohort). Neither needs the 6-point distribution.

Round 1 flagged, as a `SUSPICION`, that `EMP-AIEF13-01`'s interval might need replacing. **It does
not.** The 95 % interval stands as reported. This is worth stating plainly: a literature review
that only ever finds things to fix is not calibrating, and this round found that the existing choice
was correct.

The Round 1 caveat about *which* bootstrap variant the script uses remains open as a code-reading
task, but it no longer matters for the claim's validity.

### F15 — Leads resolved, and one Round 1 record corrected

All three Round 1 leads are promoted:

| Lead | Resolution | Correction |
|---|---|---|
| `LEAD-0001` | **[LIT-0017]** — Colbrook, *The Multiverse of Dynamic Mode Decomposition Algorithms*, arXiv:2312.00137 | Round 1 guessed a group; it is **a single author** |
| `LEAD-0002` | **[LIT-0018]** — Park & Lefebvre, *J. Math. Neurosci.* 10:16 | Author list captured |
| `LEAD-0003` | **[LIT-0019]** — Arnold, *Random Dynamical Systems*, Springer 1998 | Course notes retired entirely |

`LEAD-0002` also yielded a point not in the Round 1 record: the Park–Lefebvre model *"corresponds to
an $N + N^2$-dimensional functional differential equation with state-dependent delays"* [LIT-0018].
The state dimension grows with the edge set. That is the concrete dimension count behind
`EMP-AIEF14-01` — it is the same argument as Hale & Verduyn Lunel [LIT-0010], now with an explicit
number, and it makes "no single edge matrix is a privileged memory bottleneck" a structural
expectation rather than a finding.

Three new leads opened: `LEAD-0004` (Strogatz 2000, seen only as a reference in [LIT-0018]),
`LEAD-0005` (MacKinnon & Webb on wild bootstrap intervals), `LEAD-0006` (*Reachability for
Nonsmooth Systems with Lexicographic Jacobians*, which would be the applied demonstration that the
`CF03` approach is standard practice).

---

## 3. Coverage

| Measure | After Round 1 | After Round 2 | Δ |
|---|---|---|---|
| Sources | 16 | **28** | +12 |
| Claims with a source | 19 / 43 | **22 / 43** | +3 |
| Studies with a source | 9 / 14 | **11 / 14** | +2 |
| Domains covered | 7 / 8 | **8 / 8** | +1 |
| `CONTRADICTS` rows | 0 | 0 | 0 |

Stance mix: 6 `SUPPORTS` / 10 `METHOD` / 8 `CAUTION` / 4 `CONTEXT`.

**Honest note on the claim count.** Twelve new sources moved claim coverage by only three. That is
not a failure; it is a measurement. The `CF` block is one mechanism, and three good sources
saturate it — adding twelve more papers about nonsmooth analysis would not move the number and would
be padding. The remaining unmapped claims split cleanly:

| Group | Count | Status |
|---|---|---|
| `CF04`, `CF07`, `CF09`–`CF12` | 6 | **Correctly unmapped.** These are linear-algebra factorization, spectral invariance, asymptotic convergence and open conjectures — none is a nonsmooth problem, so the L7 chain is irrelevant to them |
| `S01`–`S18` (retired) | 13 | **Deliberately unmapped.** They are retired and the registry already records each replacement. Mapping literature to retired claims is theatre — the retirement is the finding |
| `EMP-AIEF14-03`, `REJ-LOCK-03` | 2 | Genuine gaps → Round 3* |

\* `REJ-LOCK-03` (bare zero-sum frequency locking rejected) is now tractable: **Park & Lefebvre**
give implicit equations for the global frequency $\Omega$ and stability eigenvalues $\lambda$ of
phase-locked states in exactly this class of network [LIT-0018], and **Jolly et al.** extend the
treatment to multiple and state-dependent delays [LIT-0028]. The lock claim can be restated against
a published solvability condition rather than numerically.

Unmapped studies are down to three: `HISTORICAL_PROJECT_ORIGINS`, `AIEF_1_4_PIVOT_PILOT`,
`AIEF_1_4_PROPOSAL_EQUALIZATION`.

---

## 4. Proposed registry amendments — **for owner approval, not applied**

| Claim | Proposed change | Basis |
|---|---|---|
| `CF03` | Restate the winner-tie handling as computing the **lexicographic derivative**, which is unique once a basis is fixed, and which is a subset of both the B-subdifferential and the Clarke Jacobian | [LIT-0021], [LIT-0022] |
| `CF01`, `CF02`, `CF05` | Add the piecewise-smooth framing; name the active-set/winner-map class explicitly | [LIT-0020] |
| `REJ-SPEC-02` | Record the structural reason finite differencing cannot be rescued: it steps over nonsmooth points, so shrinking ε changes branch rather than converging | [LIT-0022], [LIT-0021] |
| `EMP-AIEF13-01`, `EMP-AIEF13-02` | State that identification is **by intervention**, not predictability, and that the Granger/CCM debate therefore does not apply; record that bootstrap is adequate at N ≥ 40 | [LIT-0023], [LIT-0024], [LIT-0026], [LIT-0027] |
| `EMP-AIEF14-02` | Justify matched-phase **structurally** (conditioning out shared history) not only empirically | [LIT-0025] |
| `EMP-AIEF14-01` | Add the dimension argument: the state is $N + N^2$-dimensional in the adaptive-delay formulation, so no single edge block is privileged | [LIT-0018], [LIT-0010] |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | **Do not amend yet.** Add the cocycle identity as an explicit open verification item | [LIT-0019] |
| `REJ-LOCK-03` | Restate against the published implicit solvability condition for phase-locked frequency | [LIT-0018], [LIT-0028] |
| `AIEF_1_4_TWINDOW_SENSITIVITY` | Record that phase reduction loses delay information, and that the platform deliberately avoids it | [LIT-0028] |

---

## 5. What Round 2 did not do

- Did not test the cocycle composition law (F10). **This is the round's main carry-over.**
- Did not read Cameron, Gelbach & Miller [LIT-0026] directly; its content is second-hand via
  [LIT-0002], and the record says so in its `notes` rather than concealing it.
- Did not read `AIEF_1_3_paired_statistics_updated.py` to confirm the bootstrap variant. The
  validity question is now answered (F14); only the description remains unverified.
- Did not open the three new leads.
- Did not look at Lean/Mathlib literature (Round 4), persistent homology (Round 5), or
  nonsmooth-dynamics *applied* work beyond the reachability lead.

---

## 6. Round 3 intent

1. **Cocycle verification** (F10) — compose the tangent map over two legs and test the identity.
   Highest value, lowest cost.
2. `REJ-LOCK-03` restoration against the phase-locked solvability conditions in [LIT-0018]/[LIT-0028].
3. `EMP-AIEF14-03` — the $\rho$-sweep claim has no external anchor yet.
4. Close `LEAD-0004`/`0005`/`0006`.
5. DDE numerics: method of steps, discontinuity propagation, and the correct treatment of history at
   a split event — which bears directly on `AIEF_1_4_SPLIT_STATE_ABLATION`.
