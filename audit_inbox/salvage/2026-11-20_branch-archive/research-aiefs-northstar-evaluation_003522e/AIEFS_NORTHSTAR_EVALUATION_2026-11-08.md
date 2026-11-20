# AIEFS north-star evaluation and research execution plan
Date: 2026-11-08
Base reviewed: `main` at `eb3933c196ee19e80e1621ae80d89ca72e6d9485`
Status: evaluation proposal; no scientific result is promoted by this document.

## Executive assessment

AIEFS is a constrained, delayed, adaptive oscillator research program. Its highest-value next step is not broader narrative synthesis or another generic CI expansion. It is to close the highest-leverage gaps between (i) the implemented nonsmooth finite-dimensional map, (ii) reproducible trajectory-level observations, and (iii) branch-conditional mathematical statements.

The current evidence base has a strong integrity posture: immutable production cohorts, source hashes, a current-tree inventory, hardened manifest/checksum checks, red-team negatives, and three required Lean projects. But integrity and formal compilation do not establish that a theorem's hypotheses occur on the closed-loop dynamics, nor that a single-seed mechanism generalizes.

### North-star framing

Build a mathematically precise, computationally falsifiable theory of when delayed phase/EMA feedback and a capacity-constrained adaptive coupling map create, preserve, and reconstruct sparse interaction topology—and identify which statements survive changes in seeds, frequency ensembles, time step, and admissibility branch.

A publication-grade north star must separate:
1. **Model facts:** exact update order, domains, constraints, and branch structure.
2. **Conditional mathematics:** statements with explicit hypotheses (support, clipping, gate activity, controller winners/ties, equal scales).
3. **Numerical evidence:** frozen cohorts/replays with declared independent units and precision/error controls.
4. **Empirical generality:** replication across independent seeds and model regimes.
5. **Novelty/physical relevance:** separate literature and external-data programmes; not implied by AIEF simulations.

## Current state established in this review

- Repository: `jacobbrainard84-knightninja/AIEFS`; default branch `main`; current head reviewed: `eb3933c196ee19e80e1621ae80d89ca72e6d9485`.
- PRs #9–#12 have merged. PR #12 landed the driver invocation erratum, v4.1 held-event wording corrections, root invalid-test removal, and inventory regeneration.
- README scopes the AIEF-1.3 `Corr_physical ≈ 0.995` to hand-picked frequencies; random/clustered-`ω` results are materially lower. AIEF-1.3 100-seed ablations are audited with qualifications; `shuffle_R` is forced by construction because shuffled mean R falls below the edge threshold.
- AIEF-1.4 split-state memory ablation is a 40-seed result; it supports reconstruction of topology from phase/history/EMA when B is reset, but does not identify a unique memory carrier. The operator/tangent/cocycle/controller-fiber work remains a single-seed case study (one exceptional seed).
- Rate-law evidence is conditional: the one-step multiplier requires a controller-kernel direction and equal controlling scales; the parameter-only closed form adds ideal hypotheses. The small maximum residual is localized to one tiny finite-difference step and remains explicitly unexplained pending a delta sweep.
- The gate is node-strength multiplicative normalization, not a metric/KL/Bregman projection.
- The old 18-coordinate unique-slow-pole claim is quarantined. The 966-coordinate audit calculation is a proposal, not a branch-independent spectrum or derivative proof.
- The freezing result has a formally checked per-edge existential core, but the closed-loop R-band/phase-locking hypotheses remain open; numerical certificates are nested/dependent windows, not independent replications.
- `lean/AIEFProofsKn` and `lean/AIEFFreezeCore` are now covered by the root Lean CI matrix (the former README claim that AIEFProofsKn is not in CI is stale). This corrects the status narrative without asserting that the dynamical hypotheses are proved.
- `tools/redteam` documents G2c: a re-pinned verifier stub can pass the manifest wrapper because the manifest and verifier are not pinned outside themselves; the red-team suite remains outside CI discovery. This is a real engineering trust gap, independent of the science.

## Highest-priority research programme

### P0 — Resolve the rate-law finite-difference discrepancy

**Question.** Does the ∼2e-8 relative multiplier discrepancy vanish under a controlled perturbation-size sweep, and can a stable limiting response be distinguished from finite-time/branch effects?

**Protocol.**
- Reproduce the exact offending component from the recorded `rate_law_census_r4.json` and `kappa_cycle_kernel.json` lineage; freeze seed, rho, saved base state, engine SHA, controller set J, support, gate status, and all parameters.
- Sweep symmetric perturbation amplitudes logarithmically over at least 1e-12–1e-4, with denser coverage around the historical delta in [1e-9, 1e-8). For each h, run +h and -h separately and repeat using higher-precision arithmetic for the scalar projection where practical.
- Add controls: one well-resolved two-sided fiber from the same run; a synthetic exact affine branch where the expected multiplier is known; and deliberately crossed controller/tie boundaries to verify the branch detector rejects invalid samples.
- Record `||A_J h||`, `||A h||`, winner margins, scale spread, minimum positivity margin, gate activation, clipping activity, leakage, residual, plus absolute and relative multiplier error.
- Fit error versus h and 1/h. Do not pick the best-looking h post hoc. Predeclare an admissibility interval using branch margins; report non-admissible points as branch-crossing, not numerical failures.
- Keep the current audit result and source artifacts immutable. New run output and script receive their own manifest and registry rows.

**Decision rule.** Resolve the claim only if there is a plateau (or a defensible Richardson/roundoff model) over an interval that remains on the same branch, with synthetic and well-resolved controls passing. Otherwise retain “unexplained” and narrow the statement.

**Why P0.** It is a small, directly actionable uncertainty in an otherwise precise conditional law. A resolution improves trust in the mathematical/numerical bridge without requiring a new expensive cohort.

### P1 — Establish the actual branch-conditional dynamical theorem

**Question.** When does the unsigned-incidence controller kernel describe a genuine local invariant response of the implemented min-endpoint gate?

**Work packages.**
1. Formalize the unsigned incidence map with explicit edge indexing, non-bipartite rank assumptions and the distinction from the oriented graph cycle space. Preserve existing nomenclature caveats.
2. Prove the local finite-step identity only under explicit conditions: positive support, proposal clipping inactive, gate active, selected endpoint controllers fixed, equal controlling scales on the relevant edges, and A_J h = 0. Include a theorem that states what breaks when controller ties/switches occur.
3. For all-tied K3, formalize the finite one-sided ray identity and the non-oddness/non-additivity of the directional response. Do not call the one-sided rays eigenmodes or two-sided fibers.
4. Connect the algebra to the engine update order. In particular R is computed before B changes within a step; a B perturbation can affect R only in subsequent steps through phase/history evolution.
5. Build a branch-aware empirical persistence test on the frozen replay: support, edge positivity, winner labels/margins, tie multiplicity, gate activity, clipping flags, and the relevant tangent/fiber residual at every saved state.

**Replication requirement.** The single exceptional seed must remain a discovery case. Extend diagnostics over a declared, preselected subset of the 40-seed AIEF-1.4 cohort, including ordinary and exceptional K3 cases. State the sampling rule before inspecting outcomes. A seed is not a separate component; do not inflate N by pooling components.

**Formal boundary.** Lean can prove conditional finite-dimensional algebra. It cannot prove the trajectory satisfies the branch assumptions unless the trajectory invariance argument is itself formalized from the closed-loop equations.

### P2 — Test closed-loop support freezing hypotheses

**Question.** Can the R-band conditions used by the freezing theorem be derived from phase/EMA dynamics, rather than assumed exogenously?

**Tests.**
- Write R_e(n) as the modulus of the edge complex EMA, preserving the phase-offset invariance.
- Derive exact one-step inequalities for |C_e(n+1)| using |C'|^2 identities, not an unqualified cosine-locking substitution.
- Define a checkable phase-source condition that supplies a uniform R-band margin after some T. Distinguish within-edge phase increment convergence from cross-edge source equality.
- Seek either (a) an invariant/absorbing region giving the R-band, or (b) a minimal counterexample under the actual delayed phase equation.
- Audit the gated-OFF 7-clique certificate separately: its narrow R-spread requirement and assumptions must be measurable and not conflated with general support freezing.

**Stop condition.** If a closed-loop band cannot be proved, publish the freezing theorem as a useful conditional theorem and identify O1 as the unresolved bridge. Do not upgrade finite-window “no violation” into an infinite-time result.

### P3 — Multi-seed generality for the exceptional AIEF-1.4 mechanism

Run a targeted, pre-registered replication of the operator/cocycle/controller pipeline across the 40 paired split-state seeds:
- First classify each seed/component by support size, clique structure, tie pattern, and gate branch without selecting on eventual outcome.
- Run the same branch-aware analysis on all eligible cases; report the fraction meeting hypotheses, not only successful cases.
- Separate two-sided kernel components, all-tied K3 one-sided rays, and components with no stable controller set.
- Use seed-level uncertainty summaries; component-level measurements are nested and must not be treated as independent.
- Report failures and undefined metrics explicitly.

This is the bridge from a compelling exceptional-case calculation to a general statement about the model.

### P4 — Numerical robustness and regime generality

A separate versioned model study (never overwrite AIEF-1.3 / AIEF-1.4 production protocols):
- timestep convergence at dt, dt/2, dt/4 with matched initial conditions and correctly rescaled delay/history indexing;
- frequency ensembles: hand-picked baseline, uniform random, clustered, and controlled perturbations around the hand-picked pattern;
- held-out seeds, with seed-level estimands and predeclared analysis;
- threshold sensitivity around B_c and capacity scaling;
- separate ablation of EMA memory, delay, and instantaneous feedback, ensuring interventions do not mechanically force the outcome via threshold crossing.

Primary outcomes: topology agreement/Jaccard, edge persistence, coherence distribution, row-sum margin, total weight, and seed-level recovery. Treat continuous trajectory differences separately from discrete topology identity.

### P5 — Resolve epistemic/engineering blockers

1. Close G2c by pinning the verifier and manifest outside the self-referential manifest (e.g., a trusted CI constant or separately pinned bootstrap file), then move the G2c attack from expected failure to ordinary CI negative control. Do not merely make the existing suite required without independently anchoring the trust root.
2. Make the red-team suite's safe subset part of CI after runtime and dependency review; retain slow/Lean-dependent controls in a separate job if appropriate.
3. Finish the explicitly listed engine/oracle engineering issues (bridge self-test integration, complex-NaN equality edge cases, duplicate-row validation) only after locating their exact current code paths and writing minimal reproductions.
4. Correct stale documentation where it asserts AIEFProofsKn is not in CI; keep dated errata rather than editing hash-pinned documents.
5. Reconcile the stale `CURRENT_STATUS.md` chronology (it describes an old local/unpushed state) with the now-merged main history. Preserve claim status and caveats; update only unpinned docs through a reviewed PR.
6. Keep privacy, third-party copyright and dataset licensing as explicit owner decisions. Do not rewrite Git history or remove source materials without owner authorization.

## Proposed staged delivery

| Stage | Deliverable | Acceptance |
|---|---|---|
| 1 | Delta-sweep script + synthetic branch tests + immutable result bundle | Reproducible, branch-aware plateau/error analysis; no post-hoc delta selection |
| 2 | Lean branch-conditional gate identities (K_n kernel + K3 rays) | 0 warnings, no extra axioms, all assumptions explicit; CI required |
| 3 | Multi-seed branch persistence census | All eligible cohort seeds represented; failures/undefined included; seed is inference unit |
| 4 | Closed-loop R-band proof or counterexample | Exact derivation or explicit counterexample under engine-consistent dynamics |
| 5 | Versioned dt/frequency regime study | Predeclared design, held-out seeds, no mutation of frozen production runs |
| 6 | Publication package | Claim table maps every sentence to evidence scope; novelty and external physical claims separated |

## Guardrails for subsequent agents

- Never edit frozen run outputs, hash-pinned production scripts, audit evidence or retired/rejected artifacts in place.
- Never reinterpret a failed checker as evidence a claim is false; checker gaps are epistemic gaps.
- No claims of a “universal” rate, unique slow pole, unique memory carrier, generic K3 spectral silence, Bregman projection, or causal mediation unless new evidence specifically establishes them.
- Do not call the unsigned-incidence kernel the graph cycle space.
- Do not treat components, timesteps, nested certificate windows, or repeated rho conditions as independent seeds.
- Preserve negative results and failed hypotheses; they are part of the project's evidence.
- External contributions go through the existing `audit-inbox` protocol as unverified notes and must not be merged into authoritative claims without review.
- Every new numerical result must carry source/input hashes, seed and parameter provenance, output hashes, and a reproducibility command.
