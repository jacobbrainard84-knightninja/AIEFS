# AIEFS — Salvage assessment (deep dive #2)

> **Status (2026-10-23): REVISED per `AIEFS_audit_response.md`.** The original text is from commit f7246a3. It has been corrected in place after adjudicating a collaborator's 14-point critique.
> - **Round 3 (2026-10-24):** further corrections per `AIEFS_audit_response_2.md` (now the authoritative ledger) are marked **[Correction 2026-10-24, response-2 #N …]** (gate no-go, κ/K3, memory, delay wording).
> - **Markup:** corrections are marked **[Correction 2026-10-23 …]**, and retracted text is ~~struck~~.
> - **Strongest claim:** the revised claim in §5 replaces the original.
> - **Publication edits:** absolute local paths were replaced with neutral descriptions.
> - **Script locations:** first-pass scripts referenced here (`audit/deep/*.py`) are re-packaged in `evidence/scripts/`.

Repo: github.com/jacobbrainard84-knightninja/AIEFS (read-only local clone; `git status` clean; nothing pushed/changed on GitHub).
Companion to `AIEFS_audit.md`. New experiment scripts/logs: originally in a local `audit/deep/` scratch directory; re-packaged in `evidence/`.
Legend: **[RAN]** = I executed it; **[READ]** = read in repo; **[SUSPICION]** = my inference, not verified.

---

## 0. Bottom line

The project is **not gibberish**, ~~and it does not hold a new scientific result.~~ **[Correction 2026-10-23, response #12: this was a judgment, not a finding. The ingredients are prior art, the exact combination was not found in a non-exhaustive search, and novelty is not established either way]** The code implements a well-defined, bit-reproducible model **[RAN: 500/500 bit-exact in first audit]** **[Correction 2026-10-24, response-2 #8: bit-exact on the 7 arrays and 4 headline scalars; only 78/500 on all 38 keys, the rest differ in derived scalars by ≤1.3e-12 relative]**: a delayed Kuramoto network with Hebbian-type (EMA-coherence) plasticity, weight decay and a hard multiplicative node-capacity normalisation. The numerics are honest and unusually careful, and the authors' own manuscripts already hedge most claims. The headline phenomena, though, are either (a) direct algebraic consequences of the chosen parameters, or (b) ~~artifacts of~~ specific to a hand-picked frequency vector (a scope limitation; response #3), or (c) results on a single structure that appears in 1 of 40 seeds. Three examples:
- The emergent network is "edges with |Δω| ≲ 0.12, pruned by a row cap".
- Corr_physical = 0.995 drops to about 0.6–0.7 with random frequencies.
- The κ ≈ 0.069 "memory spectral gap" is, to 0.09%, the parameter arithmetic **κ = 2η/c − 1/T_window**. **[Correction 2026-10-23, response #9: this is a conditional closed form for complete saturated locked components, not an identity. The repo's exact discrete rate (Prop 8.3 + 11.1) gives 0.0691217 vs 0.0691225 observed]**

The heavy vocabulary (cocycle, lineality, controller fiber, biorthogonal closure, Bregman projection, spectral gap) mostly renames standard linear algebra of a piecewise-smooth map. **[Correction 2026-10-23, response #11: most of these terms (cocycle, Duhamel, lineality) are used in their standard sense, so this is a style judgment. "Projection/Bregman" for the gate remains a misnomer. The "spectral gap" is a gap of the conditional augmented operator (#10)]** There is a **small salvageable core**: a short computational note on capacity-constrained Hebbian Kuramoto networks. It would show that (i) the active topology is ~~predicted by~~ informatively but imperfectly predicted by a closed-form frequency-proximity rule plus capacity competition, (ii) the topology is multistable and its "memory" ~~lives in the phase/EMA state, not in the weights~~ is carried redundantly by the phase/EMA state and the weights (#6), **[Correction 2026-10-24, response-2 #4: Phase/history/EMA suffice for finite topology reconstruction with B reset; B is predictive and a conditional continuous-weight scaffold; no unique retained register has been identified]** and (iii) relaxation/memory rates are closed-form, kη/c and kη/c − 1/T_window. That fits a workshop paper or arXiv note benchmarked against Seliger et al. 2002 and Miller & MacKay 1994. It is not a theory programme.

---

## 1. The model in standard notation [READ: AIEF_1_3_falsification_updated.py L49–90, 350–363, 376–392, 432–470; AIEF_1_4 same params, verified]

**State:**
- phases θ ∈ T^N, N = 12;
- symmetric weights B ∈ R^{N×N}_{≥0} with zero diagonal;
- complex EMA C ∈ C^{N×N};
- a history buffer for the delay.

**Parameters:**
- dt = 0.01, T = 800, τ = 0.5 (50 steps);
- η = 0.04, μ = 0.03, γ = 0.015;
- A = 1, Q = 1.5, δ = 0.05, so c = (A−δ)/Q = 0.6333;
- T_w = 25/mean(ω) = 17.503, α = e^{−dt/T_w};
- B_c = 0.12, B_0 ~ 5e-4·U.

**Frequencies:** ω = (1.00, 1.02, 1.50, 2.00, 2.01, 1.01, 1.03, 1.51, 2.02, 2.00, 1.00, 1.04). These are hand-picked tight clusters around 1.0, 1.5 and 2.0. The seed sets only θ_0 and B_0. **There is no noise.**

Per step n:

1. **Delayed Kuramoto (Euler):** θ_i ← θ_i + dt[ω_i + Σ_j B_ij sin(θ_j(t−τ) − θ_i(t))] (mod 2π).
2. **Coherence driver:** z_ij = exp(i[θ_i(t) − θ_j(t−τ) − (ω_i+ω_j)τ/2]) (the delay-phase compensation uses the *natural* frequencies), C ← αC + (1−α)z, R = sym(|C|), diag 0.
3. **Plasticity:** B̃ = max(0, B + dt[(η+μ)R − μ − γB]), symmetrised, diag 0. Equivalently Ḃ = ηR − μ(1−R) − γB: Hebbian growth with a coherence threshold R* = μ/(η+μ) = 0.4286 and decay γ.
4. **Capacity "gate":** if any row sum r_i > c, set s_i = min(1, c/r_i) and B ← B̃ ∘ [min(s_i, s_j)]_ij. This is multiplicative normalisation of node strength, with each edge taking the stricter endpoint.

**Observables:**
- D_B: fraction of the 66 edges with B_final > B_c;
- P_future: time fraction above B_c in the last 40%;
- Corr_physical: corr(P_future, past-window mean R);
- Φ = r̄·D_B*/D_B with D_B* = 0.30;
- Laplacian spectral entropy.

**Ablations:**
- no_mu: μ = 0;
- no_gap: skip step 4;
- no_delay: τ = 0;
- shuffle_R: permute R across edges each step.

**Closed-form facts [RAN: freq_predictor.py, mathcheck.py; first audit]:**
- Uncoupled EMA magnitude: R_pred(Δω) = |(1−α)/(1−αe^{iΔω dt})|. The R* threshold gives Δω ≲ 0.12.
- Without the cap, locked edges go to B* = η/γ = 2.667.
- With the cap, a saturated row holds total c, so at most ⌊c/B_c⌋ = 5 edges per row can exceed B_c.

---

## 2. Literature classification [web search, first pass]

Closest prior art:
- **Seliger, Young & Tsimring 2002**, *PRE* 65, 041906. Kuramoto with Hebbian coupling κ̇ = ε(α cos Δθ − κ). Shows clustering and memory of patterns. This is essentially AIEF minus delay and cap.
- **Aoki & Aoyagi 2009**, *PRL* 102, 034101. Co-evolution of phases and connection strengths; self-organised clusters.
- **Berner, Schöll & Yanchuk 2019–2021**. Multiclusters in adaptive phase-oscillator networks; invariant multicluster manifolds (arXiv 1912.03922).
- Adaptive networks with delays and STDP: PMC10422128, PMC9440105, arXiv 2604.04428 (delay-controlled nucleation).
- **Miller & MacKay 1994**, *Neural Computation* 6:100. Multiplicative vs subtractive normalisation constraints in Hebbian learning. Multiplicative normalisation of a node's total weight acts as an extra weight-proportional decay. That is exactly what produces the kη/c rates below.

**Classification:** a delayed Kuramoto model with thresholded Hebbian (EMA phase-coherence) plasticity, linear decay and multiplicative node-capacity normalisation.

**What's genuinely different, all minor:**
- (a) The plasticity driver is an EMA of the complex delayed phasor with natural-frequency delay compensation, rather than the instantaneous cos Δθ.
- (b) The symmetric min(s_i, s_j) rule.
- (c) A hard cap instead of a soft constraint.

None changes the qualitative phenomenology already in the literature (frequency clusters, adaptive cluster selection, multistability). "Entropy-regularised OT/Bregman" is **not** a correct classification: the gate is not a Bregman/KL projection (§3.4).

---

## 3. Per-claim verdicts

| # | Claim | Verdict | Key evidence |
|---|---|---|---|
| 1 | Emergent sparse network from phase compatibility | **Valid but known/mostly trivial** | Set ≈ {Δω ≲ 0.12} ∩ capacity competition; hand-picked ω makes it exact (no_delay only). **[Correction 2026-10-23, response #1: the active set is not generally a subset of the closed-form set: uniform-ω subset in 9/40 and 11/60 runs]** |
| 2 | Corr_physical ≈ 0.995 | **Valid on the chosen ω only (scope limitation)** **[Correction 2026-10-23, response #3: "artifact" retracted]** | Random ω: 0.71 (uniform), 0.59–0.63 (clustered) |
| 3a | no_mu ablation | **Valid; outcome closed-form explainable** **[Correction 2026-10-23, response #8: "trivial" overstated; these are legitimate necessity tests]** | Without the threshold every edge grows; the cap allows max edge 0.404, so few exceed B_c |
| 3b | no_gap ablation | **Valid but trivial** | Active edges = 2.6654 ± 0.0019 ≈ η/γ = 2.667; total 127.9 ≈ 2.667 × 48 |
| 3c | shuffle ablation | **Valid but trivial** | Shuffled mean R = 0.371 < R* = 0.4286, so D_B = 0 is forced |
| 4 | Gate = projection / Bregman / entropy geometry | **Incoherent / false as stated** | ~~Not idempotent onto the boundary: interior-output witness;~~ **[Correction 2026-10-23, response #5: the gate is idempotent (20000/20000 bitwise) and the witness is only ε-level (6.7e-13); at ε=0 the Euclidean projection differs by 0.037–0.046]** **[Correction 2026-10-24, response-2 #1: this is an exact no-go, not an ε artifact: x∉C, A_ε(x)∈int C (margin 6.67e-13 in exact arithmetic), A_ε(x)≠x, so the map as implemented is not a smooth strictly convex Bregman or positive-definite-metric projection onto C. The 1e-12 scale is a separate numerical statement. The ε=0 comparisons only rule out the Euclidean and KL projections at the sampled points]** KL projection differs by 0.022–0.030 per edge [RAN, first audit]. It is multiplicative normalisation |
| 5a | 1.4 "memory stored in B / split-state memory" | **Valid but modest; ~~the authors' own data says the memory is not in B~~** **[Correction 2026-10-23, response #6: memory is carried redundantly: erasing B alone or EMA alone barely matters, erasing both resets 32/40; B at split predicts the future set with AUC 1.0]** **[Correction 2026-10-24, response-2 #4: Phase/history/EMA suffice for finite topology reconstruction with B reset. B is predictive and acts as a conditional continuous-weight scaffold. No unique retained register has been identified. B_split's AUC 1.0 is expected because 0/29040 edges change threshold status after the split; it is predictive, not causal]** | reset_B reproduces continue exactly (Jaccard 1.000); resets pull towards the ω-default set |
| 5b | Operator/cocycle/controller-fiber theory | **Valid linear algebra, oversold; non-generic** | The (7,2,7) K3 appears in 1/40 seeds (repo's own k3_prevalence_report) **[Correction 2026-10-24, response-2 #2: this concerns the two-sided strict K3; all-tied K3s (110 components, 34 seeds) carry a one-sided slow direction at r_{B,2}]** |
| 5c | κ ≈ 0.069 "spectral gap" | **Valid; conditional closed form** | κ = 2η/c − 1/T_w = 0.069182 vs observed 0.069122 (0.09%); discrete exact 0.0691217. **[Correction 2026-10-23, response #9: verified across 5 T_w for k=3–5 components]** |
| 6 | Lean theorems | **Valid but trivial; broken as committed** | Build fails on a missing import; after removing it, 1235 jobs OK, no sorry. Content is the kernel of a 2×3 matrix |

### 3.1 Emergent network [RAN: omega_random.py, omega_multistab.py]

I replaced the hand-picked ω with 20 U(1,2) draws and 20 clustered draws (2–4 centres + N(0, 0.02)), recomputing T_w and α each time. Every other parameter and line of code was unchanged.

**[Correction 2026-10-23, response #1: replicated with 15+15 new ω sets × 4 seeds: subset 11/60 and 16/60 (uniform baseline/no_delay), 49/60 and 58/60 (clustered)]**

| ω draw / condition | exact match to closed-form set | subset | precision | recall | D_B | Corr_phys | corr(P, R_pred) |
|---|---|---|---|---|---|---|---|
| uniform, no_delay (20) | 1/20 | 5/20 | 0.717 | 0.575 | 0.190 | 0.711 | 0.613 |
| uniform, baseline (40 runs) | 0/40 | 9/40 | 0.600 | 0.508 | 0.201 | 0.712 | 0.508 |
| clustered, no_delay (20) | 3/20 | 17/20 | 0.933 | 0.282 | — | 0.588 | — |
| clustered, baseline (40) | 3/40 | 26/40 | 0.838 | 0.267 | — | 0.634 | — |

Under clustered ω the predictor flags about 34 edges while about 10–11 become active. The row cap of ≤5 edges per row decides which ones win.

**Multistability** (10 uniform ω × 4 seeds + no_delay): the mean pairwise Jaccard between seeds' final topologies is **0.514**. Distinct topologies per ω, out of 4: [4, 2, 3, 4, 2, 4, 1, 4, 4, 4]. Jaccard(baseline, no_delay) = 0.516.

So with generic ω the network is strongly initial-condition dependent: frequency proximity, then a capacity race. The repo's hand-picked ω hides this. **Correction to my first audit:** H1/H2's "closed-form match" holds only for the repo's ω.

### 3.2 Corr_physical

~~0.995 in the repo is a near-tautology~~: P_future and past R are both monotone in Δω for well-separated clusters. **[Correction 2026-10-23, response #2: held-out test: at the repo's ω, past R beats Δω-only (AUC 0.999995 vs 0.972; logloss 0.003 vs 0.124). On uniform ω it is better calibrated (logloss 0.26 vs 0.45). On clustered ω it is worse (AUC 0.46 vs 0.65). B at split gives AUC 1.0. Not a tautology; mostly persistence]** With random ω it is 0.6–0.7. It is still positive and real, but unremarkable.

### 3.3 Ablations

Every ablation outcome has a one-line closed-form explanation (table above). They are useful as sanity checks, but they ~~cannot falsify anything nontrivial: each "failure" is guaranteed by the equation being removed.~~ **[Correction 2026-10-23, response #8: they are valid necessity tests whose outcomes have post-hoc closed-form explanations; no_mu's D_B = 0.035 is dynamical]**

### 3.4 Projection/Bregman framing

The map B̃ ↦ B̃∘min(s_i, s_j) is not a metric or Bregman projection onto {row sums ≤ c}. ~~Its outputs can be strictly interior,~~ Its outputs can be interior only at the ε level (6.7e-13; #5), **[Correction 2026-10-24, response-2 #1: this is an exact no-go, not an ε artifact: x∉C, A_ε(x)∈int C (margin 6.67e-13 in exact arithmetic), A_ε(x)≠x, so the map as implemented is not a smooth strictly convex Bregman or positive-definite-metric projection onto C. The 1e-12 scale is a separate numerical statement. The ε=0 comparisons only rule out the Euclidean and KL projections at the sampled points]** it does not minimise KL to B̃, and it is non-smooth at ties of the min [RAN, first audit, mathcheck.log].

The correct name is node-strength multiplicative normalisation. Miller & MacKay 1994 already analyse its effect: an effective weight-proportional decay.

### 3.5 1.4 operator/memory claims and κ

**Multi-seed check [RAN on archived 40-seed run 5a9f093a2fe0]:** I compared B_final topology with the closed-form set and with the continue branch.

| branch | == closed form | subset | Jaccard(pred) | Jaccard(continue) |
|---|---|---|---|---|
| continue | 11/40 | 37 | 0.881 | 1.000 |
| reset_ema | 11 | 38 | 0.887 | 0.992 |
| reset_B | 11 | 37 | 0.881 | 1.000 |
| reset_B_ema | 32 | 39 | 0.969 | 0.913 |
| B_carrier_only | 8 | 39 | 0.847 | 0.885 |
| full_reset | 20 | 39 | 0.915 | 0.836 |
| future_shuffle | 0 | 40 | 0.000 | 0.000 |

- Erasing B alone changes nothing (1.000). Erasing B and the EMA together moves 32/40 seeds to the ω-default set.
- So the "memory" is a modest path-dependent subgraph selection carried by phase/EMA state.
- The handoff itself says "Do not claim B is the dominant memory carrier".
- Caveat (also in the handoff): B_carrier_only and full_reset use different phase resets.

**κ in closed form (new) [RAN].**

The parts:
- The repo's own reports give the degree rate kη/c for saturated rows with locked edges. Sources: manuscript §8.2 table; exceptional_K3_transition_report "Late maximum |rate−2eta/c| 5.96e-10"; component_controller_report L59.
- The manuscript's Prop 11.1 defines κ = −(1/dt)·log|λ_B/α|.
- α = e^{−dt/T_w}.

Putting them together:

  **κ = 2η/c − 1/T_w = 2·0.04/0.6333 − 1/17.503 = 0.126316 − 0.057133 = 0.069182** (~~discrete version 0.069262~~ **discrete version 0.0691217**, from the repo's Prop 8.3 λ_{2,ε} and Prop 11.1).

The reported κ at t = 320 is **0.069122**: a 0.09% error, smaller than the repo's own "predicted gap" 0.06992 (1.2%). The value at t = 150 (0.0729) is a pre-asymptotic transient.

Mechanism: on an isolated, saturated K3 each node has k = 2 locked edges. The cap rescales by s ≈ 1 − dt(kη − γc)/c each step, so a row-sum-preserving perturbation decays at γ + (kη − γc)/c = kη/c. That is the Miller–MacKay effect.

I checked this by computing ~~γ + Σ_j F_ij/c~~ **Σ_j F_ij/c (label corrected 2026-10-23)** on rows 2, 7 and 11 of the exceptional seed's B_final and R_future: 0.1242, 0.1242 and 0.1221, matching kη/c at R slightly below 1.

~~**κ is therefore a parameter identity, not an emergent spectral quantity.**~~ **κ is therefore a conditional closed form, valid on complete saturated locked components (#9).** Falsifiable prediction: κ(T_w) = 0.12632 − 1/T_w. That gives 0.0263 at T_w = 10, 0.0863 at T_w = 25 and 0.1013 at T_w = 40, and κ < 0 ~~(no relative memory)~~ (old forcing relatively amplified; the weight mode dominates) for T_w < c/(2η) = 7.92. ~~Not run: it needs the frozen-replay pipeline at other T_w (§7).~~ **[Correction 2026-10-23, response #9: run at T_w ∈ {8.75, 13.13, 17.50, 26.25, 35.01}. ~~The K3 slow channel exists only at T_w=17.50 (1/200 replays), so the K3 version cannot be tested.~~ **[Correction 2026-10-24, response-2 #2: the round-2 matrix was a central difference across non-smooth ties, not a Jacobian. The cycle-kernel (fiber) multiplier is computed in `kappa_cycle_kernel.py`: all 110 all-tied K3s have a one-sided slow direction (+v_c) at rate r_{B,2}=0.12626; a two-sided K3 fiber exists in 5 components (1 resolved, the exceptional ρ=1 K3; 4 unresolved ρ=2 near-ties). See AIEFS_audit_response_2.md §2.3–2.4]** For k=3–5 complete components, κ_exact matches the discrete kη/c − 1/T_w to ≤5.3e-6 and frozen r_B matches Prop 8.3 to 3.1e-5 relative. κ>0 throughout, so the sign change is untested]**

**Genericity:** the exceptional (7,2,7) K3 occurs in exactly 1 of 40 seeds. Quote from the repo's k3_prevalence_report: "The (7,2,7) partial-controller K3 is EXCEPTIONAL… No multi-seed bundle exists." The whole Duhamel/cocycle/biorthogonal pipeline (DEFAULT_SEED = 4619122171158768524) is single-trajectory. Its own report says "does not establish universality". **[Correction 2026-10-24, response-2 #2: the two-sided K3 is rare, but the k=2 rate itself appears as a one-sided direction in all 110 all-tied K3s]**

### 3.6 Lean [RAN]

- `lake build` of the committed project **fails**: bad import `AIEFProofs.ControllerFiberProjector`, and the file is absent.
- With that import removed, in a temporary copy: "Build completed successfully (1235 jobs)", with mathlib v4.33.1 and no `sorry`/`axiom`/`admit`.
- Content: Basic.lean is `def hello := "world"`; Smoke.lean has ring examples; ControllerFiber.lean has 19 lemmas establishing ker of a fixed 2×3 rational matrix = span v_ctrl, with v_ctrl ≠ 0. Its own docstring disclaims delay, EMA and admissibility.
- Correct, but it certifies nothing about the dynamics.

---

## 4. Jargon vs substance [grep counts: md / py occurrences]

| Term | Occurrences | What it actually is |
|---|---|---|
| "admissibility operator" / "projection" / "Bregman" / "entropy geometry" | Bregman 1/14; entropy geometry 4/1 | Multiplicative row normalisation; not a projection (§3.4) |
| "cocycle" | 48/224 | Product of per-step Jacobians along one trajectory (tangent propagator). Standard and correctly used; ~~the name adds nothing~~ (style judgment, #11) |
| "Duhamel" (augmented, feedback) | 22/166 | Variation-of-constants split of a linear recurrence into homogeneous and forced parts |
| "lineality space" | 25/14 | Kernel of the saturated-row incidence map: perturbations preserving the saturated row sums |
| "controller", "winner map", "controller fiber" | 66/358; 22/56 | For each edge, which endpoint's s_i attains the min in min(s_i, s_j) |
| "biorthogonal closure / scalar reduction" | 34/47 | Left/right null vectors of a small matrix; projecting onto them |
| "spectral gap" | 2/10 | Difference of two decay rates, 2η/c − 1/T_w; ~~not a spectral gap of any operator~~ the gap between the eigenvalue log-moduli of the conditional triangular augmented operator (#10); value fixed by parameters |
| "resonance" / "resonant EMA tracking" | 32/70 | Repeated root (forcing decays at the EMA rate α, giving an nα^n Jordan term). The SSRH acronym conflates this with physical resonance [SUSPICION re the intent of "SSRH"] |
| "slow bundle" | 0/54 | Span of slow eigenvectors; not a bundle |
| "closure PASSED" | 62/64 | Internal consistency checks, not mathematical closure |
| "falsification experiment" | 10/7 | Ablations whose outcomes are algebraically determined (§3.3) |
| "memory" | 67/405 | Path-dependent subgraph selection (§3.5) and a forcing-age decay rate |
| "theorem" | 64/53 | Mostly exact algebra on frozen saved states; the manuscript (L19) says it "motivate[s] but do[es] not establish universal asymptotic theorems" |

~~Ehresmann, holonomy, fiber bundle and gauge appear nowhere in the repo~~ Ehresmann, holonomy and fiber bundle appear nowhere in the repo (only in the collaborator conversation, per the first audit). **[Correction 2026-10-23, response #11: "gauge" appears once, in a code comment at `gap_phase_scan_v9.py:95`]**

---

## 5. Salvageable core

**Strongest defensible claim (original text, SUPERSEDED by the revised claim below; its "subgraph" and "not the weights" parts were wrong, see #1 and #6):**
> In a delayed Kuramoto network with thresholded EMA-coherence Hebbian plasticity, decay and multiplicative node-capacity normalisation, the persistent weight topology is a capacity-limited subgraph of the closed-form frequency-proximity graph {Δω : R_pred(Δω) > μ/(η+μ)}, with ≤ ⌊c/B_c⌋ strong edges per node. Which subgraph is selected depends on initial phases (multistable for generic ω). The selection is carried by the phase/EMA state, not the weights. Relaxation and memory rates on saturated components are closed form: kη/c and kη/c − 1/T_w.

Every part is backed by runs above; the "generic ω" part rests on 10 + 40 draws at N = 12.

**Revised strongest defensible claim (2026-10-23; replaces the claim above):**
> In a delayed Kuramoto network (N=12) with thresholded EMA-coherence Hebbian plasticity, linear decay and min-endpoint multiplicative node-capacity normalisation:
> - **(i)** The closed-form frequency-proximity rule R_pred(Δω) > μ/(η+μ) is an informative but imperfect predictor of the persistent weight topology. It is exact for the repo's ω without delay; over random ω, precision is 0.59–0.98 and recall 0.18–0.57. Strong edges per node are capped at ⌊c/B_c⌋.
> - ~~**(ii)** For generic ω the selected topology is multistable, and delay increases the number of distinct outcomes.~~ **[Correction 2026-10-24, response-2 #5: in sampled ensembles the delayed condition gave more distinct four-seed final topologies (a sample-diversity statistic, not a basin count)]**
> - ~~**(iii)** Path dependence is carried redundantly by the weights and the phase/EMA state.~~ **[Correction 2026-10-24, response-2 #4: Phase/history/EMA suffice for finite topology reconstruction with B reset. B is predictive and acts as a conditional continuous-weight scaffold. No unique retained register has been identified. B_split's AUC 1.0 is expected because 0/29040 edges change threshold status after the split; it is predictive, not causal]**
> - **(iv)** On complete, saturated, phase-locked components of degree k, the slow weight-relaxation rate equals the closed form −log λ_{k,ε}/dt ≈ kη/c (the repo's Prop 8.3). The relative-retention rate is therefore κ = −log|λ_B/α|/dt ≈ kη/c − 1/T_w, verified to ≤5e-6 across five window lengths and 292 components. **[Correction 2026-10-24, response-2 #2: rechecked with the cycle-kernel multiplier: 374 resolved components, κ to 2.1e-6; 40 fixed seeds]**
>
> All of this is conditional on N=12 and the repo's parameters. The κ sign change at small T_w is a prediction, not a result.


**Minimal paper:** a 6–8 page computational note (or a reproducible-computation workshop paper): "Capacity-constrained Hebbian Kuramoto networks: closed-form topology, multistability, and normalisation-induced memory rates." Baselines are Seliger 2002 and Aoki–Aoyagi 2009; the theory link is Miller & MacKay 1994.

**Plan:**
1. **Cut the vocabulary.** Rewrite the model as in §1, drop the projection/Bregman/cocycle/spectral-gap language, and replace it with standard terms (§4).
2. **Make ω random by default.** Report the predictor's precision/recall and Corr_physical over ≥100 ω draws × ≥10 seeds, at N ∈ {12, 24, 48}. Present the repo's ω only as an illustrative case.
3. **Quantify multistability:** number of distinct attractor topologies vs N, c/B_c and τ, plus basin sizes.
4. **Derive and test the rates.** Prove kη/c for saturated locked components (a half-page) and test κ(T_w) = 2η/c − 1/T_w across T_w ∈ {10, 17.5, 25, 40}, predicting a sign change at T_w = c/2η. **[Correction 2026-10-23, response #9: done for k=3–5 over 5 T_w. The K3 version is not testable; the sign change needs T_w < c/(kη)]**
5. **Baseline comparison.** Same experiments with (a) Seliger cos Δθ plasticity and (b) subtractive normalisation, to show which features need the EMA driver and the min rule (the only novel ingredients).
6. **Delay:** test what τ contributes. Same-seed no_delay vs baseline Jaccard is 0.516, about the same as seed-to-seed (0.514). ~~So switching the delay off perturbs the selected topology about as much as changing initial conditions, and it adds no systematic structure.~~ **[Correction 2026-10-23, response #7: a paired test (15+15 ω × 4 seeds, plus 100 archived repo-ω seeds) ~~shows delay increases multistability.~~ **[Correction 2026-10-24, response-2 #5: in sampled ensembles the delayed condition gave more distinct four-seed final topologies (a sample-diversity statistic, not a basin count).]** Distinct topologies: 16 vs 1 at the repo's ω; more with delay in 7/15 and 5/15 random sets vs 1/15. At the repo's ω it shifts D_B by −0.027 and W by −0.16. Same-seed similarity exceeds cross-seed by +0.068 [0.021, 0.124]. There is no significant scalar shift and no delay-specific topology signature on random ω]** Predictor precision is in fact slightly *higher* without delay (0.717 vs 0.600). [SUSPICION: τ plays no qualitative role because z_ij compensates the delay with natural frequencies; test explicitly.]
7. **Fix and scope Lean.** Add the missing file or remove the import; either formalise the kη/c lemma, or drop Lean from any paper claims.
8. **Retire or relabel the 1.4 cocycle/Duhamel pipeline** as a single-seed case study (1/40 prevalence).

---

## 6. Corrections to the first audit
- H1/H2 (closed-form topology match, Corr ≈ 0.995) hold only for the repo's hand-picked ω (§3.1).
- `AIEF_1_4_scalar_spectral_gap_reduction.py` and its outputs **exist** (listed in the OPERATOR_COCYCLE note's Part XII reproducibility anchors). The first audit said it was missing or future work.

## 7. Not done / limits
- Did not re-run the 1.4 Duhamel/κ pipeline on other seeds: the structure it needs exists in 1/40 seeds. Did not re-run it at other T_w (needs frozen replays; a few hours of compute and engineering). ~~So the κ(T_w) formula is derived and matches one data point, but is untested elsewhere.~~ **[Correction 2026-10-23, response #9: now tested at 5 T_w for k=3–5 components]**
- No fresh 800-run modular-platform candidate sweep, so the modular oracle was not re-tested.
- Random-ω tests are at N = 12 only, with 20 + 20 + 10 ω draws (compute-limited: ~4 GB RAM, Pool(7)).
- The literature search was web-based; I did not exhaustively check for an exact prior use of the min(s_i, s_j) rule [SUSPICION: likely unpublished as such, but minor].

## Artifacts
- `evidence/scripts/omega_random.py`, `evidence/results/omega_random.json`, `evidence/logs/omega_random.log`
- `evidence/scripts/omega_multistab.py`, `evidence/results/omega_multistab.json`, `evidence/logs/omega_multistab.log`
- `evidence/scripts/lean_check.sh`, `evidence/logs/lean_build_original.log`, `evidence/logs/lean_build_patched.log`
- All re-packaged scripts: `evidence/scripts/` (see `evidence/REPRODUCE.md`)
