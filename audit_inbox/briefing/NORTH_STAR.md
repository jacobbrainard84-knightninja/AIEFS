# North star: where the Lean side of AIEFS is ultimately headed

Status: long-term direction, not a schedule. Added 2026-10-31 (America/Toronto) at the owner's request. A rough "6 months" horizon was mentioned, but no date is attached. This file describes the destination. `STATE.md` describes the present.

## Goal

Build a **machine-checked Lean 4 reference library for adaptive oscillator networks**. It should formalize the system's actual dynamics, not only supporting linear-algebra facts:

1. **Delayed Kuramoto evolution.** The discrete-time (Euler) phase update with delay τ.
2. **Coherence / EMA update.** The exponential moving average of pairwise coherence R.
3. **Hebbian weight dynamics.** The relax-to-target coupling law, Ḃ = (η+μ)R − μ − γB in continuous form, with its discrete counterpart.
4. **Capacity gate.** The min-endpoint multiplicative gate and its basic bounds, such as the row-sum sandwich.
5. **Conditional rate-law relations.** The relations between R, B* and the threshold B_c, e.g. the settle-above-threshold condition R > (μ+γB_c)/(η+μ). Each is stated with its exact hypotheses.
6. **Fiber / kernel properties under stated hypotheses.** The controller fiber, projectors and incidence-kernel dimensions, connected explicitly to the dynamics that use them.
7. **Convergence / stability under restricted conditions.** For example: freezing of the thresholded support, and phase-locking under small delay or slow learning. Each result carries explicit, minimal hypotheses.

## Requirements (non-negotiable)

- **No `sorry`**, no `admit`, and no `native_decide` or other trust-extending shortcuts.
- **Standard axioms only.** `#print axioms` must show only `propext`, `Classical.choice` and `Quot.sound`, and CI enforces this for every project.
- **Clear scope boundaries.** Every module states what is formalized, what is only paper-level, and what is open. Conditional results say so in the theorem statement and in the ledger row.
- **Keep the audit discipline.** That means hash pins, the claim ledger (`registry/claims.csv`), errata instead of silent edits, reproducible check scripts, independent review, and red-team checks that must reject known-false input. Verification must stay as careful as the numerical audits.

## What it would add

- **Credibility and reuse.** A verified baseline that others can build on or check against. It extends the niche shown by `kuramoto-lean` (identical oscillators, no delay, EMA or gate; see `RESEARCH_LEADS.md`) toward adaptive, delayed, gated networks.
- **A stronger process signal.** Proofs plus a ledger plus audits show how claims were established, not just what they are.
- **A better basis for talking with formal-methods people.** Concrete, checkable statements are easier to discuss than numerics. Any outreach remains **owner-only** (README rule 1).

## Honest limits

- **It is hard.** The delay, the EMA and the non-smooth gate are exactly what makes the analysis difficult (see `OPEN_QUESTIONS.md` §1, O1).
- **Results will likely be conditional on idealizations.** Expect assumptions such as equal scales, saturated components, fixed branches, or initial conditions in an open semicircle. These conditions must be explicit and must not be hidden in definitions.
- **Novelty is not established.** Check every novelty claim against the literature (README rule 8). Rediscovering a known result still counts as validation.
- **The proofs must remain sound, maintainable and understandable without AI help.** A proof nobody can follow or repair is a liability, even when it compiles.

## Bottom line

What separates an interesting proving ground from a useful library comes down to three things:

- how much of the **actual dynamics** gets formalized;
- how **tightly the hypotheses** are stated;
- whether verification stays **as careful as the numerical audits**.

## Where we are now (checked 2026-10-31 against `origin/main` 395ea53 and `origin/research/freezing` f444401)

The premise that "the Lean part is only a 2×3 kernel identity" is **out of date**.

- **On `main` (`lean/AIEFProofs`):**
  - The controller fiber of the 2×3 matrix `CCtrl`: kernel = span(`vCtrl`), with locked-ratio and smul characterisations (`ControllerFiber.lean`).
  - Orthogonal projectors `PPar` / `PPerp`, with symmetry, idempotence, complementarity and range = kernel (`ControllerFiberProjector.lean`).
  - The fiber quotient TFAE (`ControllerFiberQuotient.lean`).
  - Explicit complete-graph incidence matrices for K3–K6, with right inverses and kernel dimensions. The K3 rows are tied to `CCtrl` (`CompleteGraphIncidence.lean`).
- **On `main` (`lean/AIEFProofsKn`):**
  - **Coefficient field matters.**
    - For K_n, n ≥ 3, the headline theorems are stated **over ℚ**. The unsigned edge-incidence map is surjective, and `finrank_ker_inc_eq_half` / `finrank_ker_edgeIncMatrix_top` give dim ker = |E| − |V| = n(n−3)/2 (`IncMatrixRank.lean:201-230`, `KernelDimFormula.lean:60-62`).
    - The underlying general lemma is proved over any field with 2 ≠ 0 (`[NeZero (2 : K)]`): for a connected non-bipartite graph the incidence map is surjective, so dim ker = |E| − |V| (`IncMatrixRank.lean:147,168,177`).
    - In characteristic 2 the result **fails**. The K_3 incidence map over `ZMod 2` is not surjective, and Lean exhibits this (`CompleteGraphKn.lean:246-252`).
    - Do not quote these results without the field hypothesis.
  - For complete graphs, `finrank_ker_inc_eq_half`: dim ker = n(n−3)/2 for all n ≥ 3. It is checked against K12 (54).
  - Right inverses via the J-matrix, and characteristic-2 / K2 counterexamples showing that the hypotheses are needed.
- **PENDING, PR #3 (`research/freezing` @ f444401, awaiting the owner's merge):**
  - `lean/AIEFFreezeCore`, the scalar core of the conditional freezing theorem: `upper_geom`, `eventually_off` / `eventually_on`, and per-edge `edge_eventually_off` / `edge_eventually_on` for B_{n+1} = λ_n·max(0, (1−h)B_n + h u_n).
  - The conclusions are existential (∃N). The gate λ_n and drive u_n are abstract sequences under band hypotheses.
  - It does not cover phases, delay, the EMA, Lemma 1, Theorem 3 or Corollary 4.
- **CI:** `main`'s `lean.yml` runs AIEFProofs and AIEFProofsKn as required jobs, with forbidden-marker and axiom-audit steps. AIEFFreezeCore is listed but not on `main` yet.

## Living checklist

Status values: **not started** / **partial** / **done**. A status refers to `main` unless it is marked PENDING. Update this table in the same commit that changes the status, citing the sha.

| # | Component | Status | Notes |
|---|---|---|---|
| 1 | Delayed Kuramoto evolution | not started | No phase dynamics in Lean. The `kuramoto-lean` Euler/contraction results are a possible template. |
| 2 | Coherence / EMA update | not started | |
| 3 | Hebbian weight dynamics | partial (PENDING, PR #3) | Only the per-edge scalar recurrence, with abstract gate and drive (`AIEFFreezeCore`). It is not coupled to R. |
| 4 | Capacity gate | not started | Abstracted as λ_n ∈ [0,1]. Lemma 1 (row-sum sandwich) is not formalized. |
| 5 | Conditional rate-law relations | not started | The thresholds (0.454286, 3/7) are paper-level only, and they hold for the **ungated** scalar recurrence only (see STATE.md). |
| 6 | Fiber / kernel properties | partial | The linear-algebra layer is done (controller fiber, projectors, K_n kernel dimension). Its link to the dynamics is not formalized. |
| 7 | Convergence / stability (restricted) | partial (PENDING, PR #3) | Eventual OFF/ON per edge (∃N). There is no phase-locking (O1), no convergence of B and no explicit N. |
| — | Infrastructure: no `sorry`, standard axioms, CI per project | done for AIEFProofs and AIEFProofsKn | AIEFFreezeCore is a required row only on `research/freezing`. |

### Theorem-level dependency chain (suggested by Researcher 026; adopted as the build order)

The coarse rows above hide an order. Each step should be stated and proved, or at least written down exactly, before the next one is used. Halanay/Razumikhin-type delay stability arguments come **last**: they are only meaningful once the finite, exact maps under them are pinned down.

1. **Gate definition and idempotence.** The exact finite capacity gate s_i = min(1, c/(q_i+ε)), with per-edge factor min(s_i, s_j). Prove idempotence of the gated map.
2. **Complete gated map vs. scaling kernel.** Relate the full one-step gated map to the unconditional scaling kernel. Say exactly where it is linear, where it is piecewise linear, and where it is not differentiable (at ties).
3. **Tied-K3 gate identity.** The one-sided gate identity on a tied K_3, linked to `CCtrl`.
4. **Clique scalar gate multiplier.** On a complete, saturated clique the gate acts as a single scalar multiplier.
5. **Finite recurrences.** The finite proposal and radial recurrences built on 4.
6. **Delayed state and buffer indexing.** The exact delayed state: the history buffer, its index arithmetic, and what τ = 0.5 at dt = 0.01 means as a step count.
7. **Delayed quotient recurrence.** The recurrence on the controller-fiber quotient, with the delay included.
8. **Only then** Halanay/Razumikhin-type stability or convergence statements for 7.

### Open modelling choice: exact real arithmetic vs. floating-point implementation

Every formal statement must say which object it is about:

- **(a)** the exact real-arithmetic mathematical recurrence (the paper proofs and `AIEFFreezeCore` today); or
- **(b)** an implementation theorem about the floating-point Python engine (float64, with rounding).

Results about (a) do not transfer to (b) automatically. The freezing report already restricts its explicit N to real arithmetic (`research/freezing/REPORT.md` §3.6). This choice is **open**. The owner and the Lean seats should decide it per component before claiming that any row of the checklist covers "the actual dynamics".
