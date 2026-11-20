# RES-FREEZE-01 novelty audit (independent, read-only)

Sat Oct 31, 2026, ~11:15 AM EDT. Auditor: Grok Bot (executor). Scope: Researcher 001's proposal to rescope the novelty of RES-FREEZE-01
(`origin/research/freezing` tip `85ba0a6`, fetched today) and the planned RES-FREEZE-NOVELTY row. I pushed nothing, edited nothing in the
repo or ledger, and contacted nobody.
Inputs: `research/freezing/REPORT.md`, `README.md`, `registry/claims.csv` (RES-FREEZE-01 row) and
`lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean` at `85ba0a6`; `/workspace/review_r026/FREEZING_PROPOSAL.md`;
`/workspace/research/people/kuramoto_people_2026-10-31.md`.

## Verdict: AGREE WITH CHANGES

The direction is right. RES-FREEZE-01's novelty should be narrowed, and Cho–Dong–Ha 2023 is real prior art that the 2026-10-28 search missed.
The proposal has four problems:

1. It overstates Ha–Noh–Park 2016. As a pre-emption of coupling convergence or freezing, it is unverified.
2. "Known variant" fits the mechanism, not the gated result.
3. "Discrete-time" and "explicit N" are not what carries the novelty. Discrete-time Kuramoto theory exists, and the explicit N is paper-level and depends on tail data.
4. The residual statement leaves out the condition on R, which is load-bearing.

## 1. What RES-FREEZE-01 actually claims (at 85ba0a6)

**Model.** This is the discrete-time AIEF engine map (`aief_experiment_engine_v1.py`, REPORT §1). N=12 oscillators, dt=0.01, delay D=50 steps (τ=0.5).
Each step:

- **Complex EMA coherence:** z_ij ← α z_ij + (1−α) exp(i(θ_i^n − θ_j^{n−D} − (ω_i+ω_j)τ/2)), and R_ij = (|z_ij|+|z_ji|)/2.
  R is a modulus, so R → 1 for any frequency-locked pair, whatever its phase offset.
- **Pre-gate weight:** Ũ = sym(max(0, B + dt((η+μ)R − μ − γB))). This is a clipped forward-Euler step of the relax-to-target law
  Ḃ = (η+μ)R − μ − γB. Per edge: B⁺ = λ_e · max(0, (1−h)B + h u_e), with h = γdt and u_e = ((η+μ)R_e − μ)/γ.
- **Min-endpoint multiplicative capacity gate:** when some row sum s_i > c = (a−δ)/q, set λ_i = min(1, c/(s_i+ε)) and
  B⁺_ij = Ũ_ij · min(λ_i, λ_j).
- **Delayed Kuramoto phase step** using B⁺.

**What "freezing" means.** The status set {e : B_e > B_c}, with B_c = 0.12, is constant for all n ≥ T+N. This is finite-step constancy of a
thresholded support. It is not convergence of B, and B itself need not converge.

**Claim.** The claim is conditional. If from step T on, every edge's R_e stays in a band satisfying one of three strict certificates, the support is
frozen from T+N on. The certificates are:

- OFF: U⁺ < B_c.
- ON: x* > B_c, using the Lemma 1 lower bracket.
- Gated-OFF (Thm 3): for large locked cliques, using the capacity squeeze.

**Proof status and caveats.**

- Paper proofs: Lemma 1, Thms 2–3 and Cor 4.
- Lean covers only the scalar or per-edge OFF/ON core, with an existential N (`upper_geom`, `eventually_off/on`, `edge_eventually_off/on`).
- The explicit N is real-arithmetic and paper-level, and it depends on R over [T,∞) (O4).
- Without some hypothesis on R the claim is false (§3.4).
- Closed-loop locking (O1) is **open**. The theorem assumes it.
- Cor 4 still needs the state-free ℓ fix from FREEZING_PROPOSAL.md.

**The old novelty wording** (REPORT §0/§5, ledger caveat) is: "plausibly new as a model-specific certificate theorem but mathematically elementary;
search not exhaustive". Note that §5 *did* find Ha–Noh–Park 2016, Ha et al. SIADS 2018 and Bronski et al. Chaos 2017. The people-scan's line
"missed the Ha school" is therefore overstated. What it missed is Cho–Dong–Ha 2023, plus CMS 2024 and Wang–Dong 2025.

## 2. Citation verification

V = confirmed today against Crossref (api.crossref.org/works/<doi>) and/or arXiv/zbMATH. Content checks are separate from metadata checks.

| Ref | DOI | Metadata | Content claim as used |
|---|---|---|---|
| Cho, Dong, Ha, "Interplay of inertia and adaptive couplings in the emergent dynamics of Kuramoto ensemble", J. Differential Equations 360 (2023) 523–571 | [10.1016/j.jde.2023.03.047](https://doi.org/10.1016/j.jde.2023.03.047) | **V** (first author Hangjun Cho per ScienceDirect/MaRDI; Semantic Scholar's "Han-Hyun Cho" looks like a misattribution) | **V via abstract + zbMATH review:** second-order (inertial) Kuramoto, κ̇_ij = μΓ(θ_j−θ_i) − γκ_ij, Γ = cos (Hebbian) or \|sin\| (anti-Hebbian); continuous time; frameworks giving "complete synchronisation of phases and convergence of the coupling strengths". Full text not read (closed); the "(FA)" framework and "K∞" notation in the people-scan are **unverified** by me |
| Ha, Noh, Park, "Synchronization of Kuramoto Oscillators with Adaptive Couplings", SIAM J. Appl. Dyn. Syst. 15(1) (2016) 162–194 | [10.1137/15M101484X](https://doi.org/10.1137/15M101484X) | **V** | **Abstract only (V):** adaptive laws preserving the sum of incoming couplings; "frameworks that guarantee the emergence of synchronization". Secondary (Bronski et al., [arXiv:1611.09941](https://arxiv.org/abs/1611.09941)): their Model A is γ̇_ij = μcos(θ_i−θ_j) − αγ_ij; results summarised there are exponential phase sync (identical, arc < π/2) and a phase-diameter bound ~1/(min coupling) (nonidentical). **No coupling-convergence or edge-set result is verified**; SIAM page 403, no arXiv version found |
| Ha, Li, Xue, "Formation of phase-locked states in a population of locally interacting Kuramoto oscillators", JDE 255(10) (2013) 3053–3070 | [10.1016/j.jde.2013.07.013](https://doi.org/10.1016/j.jde.2013.07.013) | **V** | **V** (ScienceDirect open-archive intro): gradient flow + Łojasiewicz; bounded fluctuation ⇔ frequency sync; exponential if D0 < π/2 (under the stated K condition). Fixed couplings |
| Ha, Ryoo, "Asymptotic Phase-Locking Dynamics and Critical Coupling Strength for the Kuramoto Model", Commun. Math. Phys. 377(2) (2020) 811–857 | [10.1007/s00220-020-03786-1](https://doi.org/10.1007/s00220-020-03786-1) | **V** | content not re-checked |
| Correction to Ha–Ryoo, CMP 403(3) (2023) 1627 | [10.1007/s00220-023-04820-8](https://doi.org/10.1007/s00220-023-04820-8) | **V: exists**; Crossref `update-to` → the 2020 DOI (Nov 2023 issue) | content of correction not read |
| Dong, Ha, Kim, "Emergent Behaviors of the Kuramoto Model with a Time Delay on a General Digraph", SIAM J. Appl. Dyn. Syst. 19(1) (2020) 304–328 | [10.1137/19M1249096](https://doi.org/10.1137/19M1249096) | **V** (venue SIADS) | **V via zbMATH review:** delayed Kuramoto **and its Euler discretisation**, fixed coupling; complete sync for small delay, large κ |
| Cho, Ha, Kang, "Emergent Behaviors of a Kuramoto Ensemble Under Fading Memory", J. Nonlinear Sci. 35(1), Paper 9 (2025) | [10.1007/s00332-024-10099-3](https://doi.org/10.1007/s00332-024-10099-3) | **V** | abstract **unverified** (publisher elides it); "nearest analogue to EMA" is an inference from the title |
| Niyogi, English, "Learning-rate-dependent clustering and self-development in a network of coupled phase oscillators", Phys. Rev. E 80, 066213 (2009) | [10.1103/PhysRevE.80.066213](https://doi.org/10.1103/PhysRevE.80.066213), [arXiv:0908.4220](https://arxiv.org/abs/0908.4220) | **V** | **V (arXiv abstract):** critical learning rate; two anti-phase clusters above it, one below; numerical/physics, no theorem |
| Cassie, kuramoto-lean | [github.com/velvetmonkey/kuramoto-lean](https://github.com/velvetmonkey/kuramoto-lean) | **V: exists, MIT** (LICENSE "Copyright (c) 2026 Ben Cassie"); Lean v4.31.0-rc1; 51 commits; head 32b9c36 (2026-08-25 09:25 EDT); no `.github` (no CI) | **Partly V.** `discreteFlow_bounded_skew` (Discrete.lean:193) and `discreteFlow_tendsto_zero` (DiscreteConvergence.lean:325): present. `barbalat_of_nonneg_lipschitz`: present but **`private`** (Frontier.lean:205). **LaSalle is not in kuramoto-lean** (paper.md:346 says the proof avoids LaSalle). It lives in separate MIT repos [lasalle-lean](https://github.com/velvetmonkey/lasalle-lean) and [barbalat-lean](https://github.com/velvetmonkey/barbalat-lean). `#print axioms`: 6 occurrences (5 `#guard_msgs in`, 1 bare, on floor_coupling_convergence_to_synchrony), not per-theorem. grep finds no `sorry`/`admit`/`axiom`. **Not built by me** |

None of these citations is fabricated or has wrong metadata. The unverified items are content claims only: Ha–Noh–Park's exact
results, Cho–Dong–Ha's framework details, and Cho–Ha–Kang's abstract.

## 3. Comparing the two pre-emption papers with RES-FREEZE-01

| | RES-FREEZE-01 | Cho–Dong–Ha 2023 | Ha–Noh–Park 2016 |
|---|---|---|---|
| Time | discrete (forward-Euler-type map, h=γdt) | continuous ODE | continuous ODE |
| Phase model | first-order, delayed (D=50 steps), heterogeneous ω | second-order (inertia), no delay | first-order, no delay |
| Coupling law | clipped relax-to-target, drive (η+μ)R−μ, R = modulus of a complex EMA (phase-offset-invariant) | κ̇ = μΓ(Δθ) − γκ, Γ = cos or \|sin\| (instantaneous phase difference) | Model A ≈ μcos − αγ (secondary source), plus sum-preserving laws |
| Normalisation | min-endpoint multiplicative row-sum gate, switching on and off | none (verified level) | incoming-sum conservation (abstract) |
| Proves locking? | **No.** Assumed (O1 open) | **Yes**, under frameworks | Yes (sync frameworks) |
| Proves couplings converge? | No (B need not converge) | **Yes** (zbMATH) | **Not verified** |
| Thresholded edge set fixed in finite steps? | **Yes, conditional**, explicit N (paper) | Not stated. It follows only qualitatively (∃T) from convergence plus a strict margin | Not stated |

**Assessment**

- **Same law?** No, but the same type. Both are damped relax-to-target Hebbian laws (Ḃ = drive − decay·B). AIEFS's drive is an affine function of
  an EMA coherence modulus, not cos(Δθ). AIEFS also adds clipping and a gate.
- **Overlap.** In both, "phases settle ⇒ drive settles ⇒ couplings settle". That step is an elementary linear-ODE or affine-contraction fact. Cho–Dong–Ha
  publish it, together with a locking theorem, for an inertial continuous-time model. Given a strict margin, an eventually-constant thresholded
  support follows at once from their coupling convergence. So for the **mechanism**, "known variant" is fair.
- **Where "known variant" is too strong.** It is too strong for the **whole** of RES-FREEZE-01. Nothing found covers three things:
  - (i) Lemma 1, the gate-switching-independent bracket 1/g_e ≤ λ_e ≤ min(1, c/s_i, c/s_j);
  - (ii) Thm 3, a capacity-forced OFF state for large locked cliques ("too many friends"). Here the gate drives an edge *below* threshold even though its pair is fully locked. This has no analogue in ungated laws;
  - (iii) the clipping to exact 0 and exact decoupling.
- **Ha–Noh–Park.** It is related prior art for the law (Model A) and for normalised adaptive coupling (it sits next to the gate and Miller–MacKay).
  It should **not** be listed as pre-empting coupling convergence or freezing until its full text is read.
- **Validation hit?** Acceptable only as a *consistency* hit. Published rigorous continuous-time results agree that couplings settle when phases
  lock. It does not independently validate any AIEFS-specific element (gate, delay, EMA, explicit N).
- **Residual statement as proposed** ("discrete-time finite-step freezing of the strong-edge set under the gate with explicit N"): partly inaccurate.
  - *Discrete time is not novel by itself.* There is rigorous discrete-time and Euler Kuramoto theory with fixed coupling:
    - Ha, Kim, Kim, Zhang, J. Math. Phys. 60, 051508 (2019), [10.1063/1.5051788](https://doi.org/10.1063/1.5051788);
    - Zhang–Zhu, [arXiv:1909.03358](https://arxiv.org/abs/1909.03358);
    - Shim, KRM 13 (2020) 979–1005, [10.3934/krm.2020034](https://doi.org/10.3934/krm.2020034);
    - Dong–Ha–Kim SIADS 2020 (Euler scheme with delay);
    - Zhang–Xiao, DCDS-B 29 (2024) 2399–2418, [10.3934/dcdsb.2023183](https://doi.org/10.3934/dcdsb.2023183) (delayed discrete);
    - Ha–Lee–Yoon, JDE 415 (2025) 91–147, [10.1016/j.jde.2024.09.021](https://doi.org/10.1016/j.jde.2024.09.021);
    - Wu, PRE 113, 014210 (2026), [10.1103/fb46-ffzq](https://doi.org/10.1103/fb46-ffzq);
    - Cassie's Lean Euler contraction.

    In arXiv/Crossref/web queries today I found **no** discrete-time *adaptive-coupling* Kuramoto theorem. That search was not exhaustive (no Scholar, no full text).
  - *Explicit N is not a strong carrier.* An iteration count for a scalar affine contraction is textbook. In AIEFS it is paper-level only (Lean has
    ∃N), holds in real arithmetic only, and is computed from R on [T,∞), so it is not a priori (O4).
  - *Omission.* The statement must say it is conditional on coherence bands (locking/drift with margin). That is exactly the part Cho–Dong–Ha
    *prove* for their model and AIEFS does not.

## 4. Recommended RES-FREEZE-NOVELTY row

**Label** (artifact_status / audited_qualifier):
`Known variant (partial overlap; consistency hit) — narrow residual plausibly new, search non-exhaustive`.

- Do **not** use Retired, Superseded or Rejected for this row. Per the owner rule, tested-and-overlapping is not "Retired".
- Do **not** use `Frozen` either. That word is already an artifact_status in claims.csv, meaning frozen experiment artefacts (EMP-AIEF13-01/02, EMP-AIEF14-01), and would be ambiguous here.
- Suggested evidence_scope: `Literature assessment (non-exhaustive)`.

**Statement (suggested exact wording):**

> Novelty assessment for the RES-FREEZE rows. Overlap (known variant): the mechanism "phase-locking ⇒ relax-to-target Hebbian couplings
> converge", and hence, given a strict margin, an eventually constant thresholded edge set, is a known variant of continuous-time results for
> damped Hebbian Kuramoto couplings κ̇_ij = μΓ(θ_j−θ_i) − γκ_ij (Cho–Dong–Ha, J. Differential Equations 360 (2023) 523–571, with inertia;
> they also prove the locking that AIEFS assumes). Ha–Noh–Park, SIAM J. Appl. Dyn. Syst. 15 (2016) 162–194, is related prior art for the law
> and for normalised adaptive couplings. Its verified abstract gives synchronization frameworks, not coupling convergence or edge-set freezing.
> Residual, plausibly new (narrow, mathematically elementary): for the discrete-time, clipped AIEF weight map with the min-endpoint
> multiplicative capacity gate, (i) a bracket on the gate factor that holds whether or not the gate is active (Lemma 1), and (ii) strict-margin
> OFF, ON and gated-OFF certificates (Thms 2–3). Together they give finite-step constancy of the strong-edge set {B_e > B_c}, *conditional on
> coherence bands holding on [T,∞)*, with an explicit step bound N. That bound is a paper proof in real arithmetic, depends on the tail R data,
> and appears in Lean only as ∃N for the per-edge OFF/ON core. The gated-OFF case (capacity forces a locked clique of ≥ 7 below threshold) has no
> precedent found. Discrete time alone is not new: discrete and Euler Kuramoto synchronization with fixed couplings is established (e.g. Ha–Kim–Kim–Zhang,
> J. Math. Phys. 2019; Dong–Ha–Kim, SIADS 2020). No discrete-time adaptive-coupling freezing result was found (arXiv/Crossref/web, 2026-10-31;
> no full-text or Scholar search).

**Scope boundary:** this row is novelty only. It does not change the mathematical status of LEAN-FREEZE-CORE, RES-FREEZE-GATED or RES-FREEZE-NUM.
Add Cho–Dong–Ha 2023 (and CMS 2024, Wang–Dong JDE 2025, both unread here) to the REPORT §5 search log.

## 5. Other concerns

- **People-scan corrections.**
  - "That novelty search missed the Ha school" is inaccurate. REPORT §5 cites Ha–Noh–Park 2016, SIADS 2018 and Bronski 2017. It missed Cho–Dong–Ha.
  - "Ha–Noh–Park … phase-locking ⇒ couplings converge" is unverified.
  - kuramoto-lean has no LaSalle lemma, and its Barbalat lemma is `private`. Reuse means copying or porting it, or using the separate repos.
- **Model mismatch to flag in the write-up.** The R used by AIEFS is phase-offset-invariant. An anti-phase locked pair has R → 1 (drive up), whereas under cos(Δθ) it gets a negative drive.
  So the published K∞ = α cos(Δθ∞) picture (Niyogi–English, Bronski) does not transfer literally.
- **Corollary 4 fix.** The fix in FREEZING_PROPOSAL.md must land before any row cites Cor 4.
- **Split not seen.** The split has not been pushed (tip still 85ba0a6), so I could not check the actual rows.

---

# Addendum A: spot-check of FRONTIER_MAP.md top spots 1–2 (Sat Oct 31, 2026, ~11:46 AM EDT)

Same rules as above: read-only, nobody contacted, ledger untouched.
Inputs: `/workspace/research/frontier/FRONTIER_MAP.md` §4 and `frontier_table.csv` (F3, F4).
The map rates spot 1 "Moderate-low risk" and spot 2 "Low-moderate". Here, "risk" means the risk that the result is not new.

## A1. Spot 1: Lean capacity-gate OFF theorem for a locked k-clique (c/(k−1) < B_c), framed as a "non-projection constraint"

**Rating verdict: TOO OPTIMISTIC.** I would rate it **Moderate**. The concept is classical, and the same kind of cap already exists on Hebbian
Kuramoto, with Lean definitions. What remains new is narrow and elementary.

### Citations

| Ref | Metadata | Claim in map | Finding |
|---|---|---|---|
| Martens & Bick, "Multiple timescale dynamics of network adaptation with constraints", Chaos 35(10) 103141 (2025) | **V**: Crossref [10.1063/5.0289706](https://doi.org/10.1063/5.0289706); [arXiv:2507.06359](https://arxiv.org/abs/2507.06359) (v2, 17 Sep 2025, read in full) | "§V future work: alternative constraint types, including curved constraint manifolds" | **The quote is accurate; the map's use of it is overstated.** Verbatim from the arXiv v2 conclusion: *"Potential generalizations include (i) nonpairwise interactions, such as those found in higher-order networks; (ii) alternative constraint types, including curved constrait [sic] manifolds (with appropriate care near singularities); (iii) weighted subgraph constraints, or replacing the baseline b with a weighted graph; (iv) heterogeneous nodal dynamics…"*. Their constraints are **linear equality** subspaces (subgraph constraints; constant row-sum/"degree" constraint, eq. (12)), enforced by projection or fast relaxation. They do **not** mention inequality caps, multiplicative scaling, thresholds, or anything resembling the clique theorem. The AIEFS cap set {W ≥ 0, row sums ≤ c} is a **linear polytope**, not a curved manifold. Only the gating *map* is nonlinear. "M&B list it as future work" should become "M&B list alternative constraint types generically as future work". Their paper does not cite Miller–MacKay (grep). I read the arXiv version, not the version of record; the wording there is unverified |
| Miller & MacKay, "The Role of Constraints in Hebbian Learning", Neural Computation 6(1) 100–126 (1994) | **V**: Crossref [10.1162/neco.1994.6.1.100](https://doi.org/10.1162/neco.1994.6.1.100); author PDF [Caltech](https://authors.library.caltech.edu/13800/1/MILnc94.pdf) read | "share formula goes back to Miller & MacKay 1994" | **Supported, with a correction.** The abstract says: *"A common method of avoiding these outcomes is to use a constraint that conserves or limits the total synaptic strength over a cell… Two methods of enforcing a constraint are distinguished, multiplicative and subtractive."* It also discusses constraints "both over output cells and over input cells". So multiplicative enforcement of a *limit* on per-cell total strength, on both sides, is explicitly prior art. Multiplicative normalization itself is older: von der Malsburg, Kybernetik 14 (1973) 85–100, [10.1007/BF00288907](https://doi.org/10.1007/BF00288907) (V). The map should write "goes back at least to von der Malsburg 1973; analysed by Miller & MacKay 1994" |

### Prior art for multiplicative capacity or budget gates on adaptive oscillator networks

| Prior work | What it has | Gap to AIEFS |
|---|---|---|
| **Ito & Kaneko, Neural Networks 13 (2000) 275–281**, [10.1016/S0893-6080(99)00107-0](https://doi.org/10.1016/S0893-6080(99)00107-0), [arXiv:cond-mat/9911416](https://arxiv.org/abs/cond-mat/9911416) (eqs. read) | **Discrete-time phase maps** x_{n+1}^i = x^i + Ω + (k/2π) sin 2πx^i + (c/2π)Σ_j ε^{ij} sin 2πx^j + I^i. A Hebbian multiplicative update ε̃ ← [1+δcos2π(x^j−x^i)]ε is followed by **per-node multiplicative normalization** ε^{ij} = ε̃^{ij}/Σ_j ε̃^{ij}, described as "competition for the connections converging on a single unit" | Equality normalization (always on, not a cap), row-only and asymmetric, not min-endpoint, no threshold or freezing theorem. Numerical only |
| **Ito & Kaneko, PRL 88, 028701 (2002)** (Crossref issued 2001-12-27), [10.1103/PhysRevLett.88.028701](https://doi.org/10.1103/PhysRevLett.88.028701), [arXiv:cond-mat/0108408](https://arxiv.org/abs/cond-mat/0108408) | Same normalization, explicitly motivated as a **limited connection resource** ("there is a limitation on this resource… competition among connections"), with logistic-map units. Discrete time | As above; numerical |
| **Cassie, flywheel-universe** (Zenodo [10.5281/zenodo.20469680](https://doi.org/10.5281/zenodo.20469680), DataCite **V**: "Budgeted Hebbian Kuramoto Dynamics for Max-Cut under Amplitude Heterogeneity…", Ben Cassie, 2026, CC-BY-4.0; [repo](https://github.com/velvetmonkey/flywheel-universe), local clone read) | Hebbian Kuramoto with a symmetric non-negative W and an **inequality** per-node budget. Lean `Defs.lean:43–50` has `(∀ i j, 0 ≤ W i j) ∧ … (∀ i, ∑ j, W i j ≤ B)`. The budget is enforced by exact symmetric-Frobenius **projection** inside an alternating phase/weight step, with a **scheduled** freeze. The Zenodo abstract claims a "Lyapunov-descent and KKT-stationarity theorem for the continuous-time joint phase/weight flow, with the algebraic core formalised in Lean 4". The `sorry` hits in LyapunovDescent.lean are in comments only ("closed sorry-free"). **Not built by me** | Projection, not multiplicative min-endpoint. Freeze is scheduled, not emergent. No threshold, OFF or clique theorem. **This means an inequality row-sum cap on Hebbian Kuramoto, with Lean definitions, is not new** |
| Miller–MacKay 1994; von der Malsburg 1973; synaptic-scaling literature (e.g. [Frontiers review 10.3389/fncom.2015.00089](https://doi.org/10.3389/fncom.2015.00089), not Crossref-checked) | Multiplicative conservation or limitation of per-cell total weight | Not oscillators; the clique share c/(k−1) is immediate from uniform multiplicative scaling |

I found **no** prior min-endpoint multiplicative scaling (B_ij · min(λ_i, λ_j) with λ = min(1, c/s)), no prior "over-cap-only" gate on adaptive Kuramoto, and
no published "locked clique of size k > 1 + c/B_c is forced OFF" theorem. Sources searched: Crossref, arXiv API, web, GitHub. The search was not exhaustive.

### Lean, Coq and Isabelle formalizations of adaptive Kuramoto

These were found with `gh search code/repos`, which hit a rate limit partway through.

- **velvetmonkey/kuramoto-lean**, `Hebbian.lean`: joint Lyapunov descent identity.
- **velvetmonkey/flywheel-universe** `lean/RequestProject`: budgeted Hebbian definitions, Lyapunov/KKT.
- **LeanPool/lean-pool** `LeanPool/Kuramoto/Hebbian.lean`: the file names match kuramoto-lean, so it is probably a mirror (unverified). Copies of it also appear in `competemath/*`.
- **taejun-song/kuramoto-lean**: classical Kuramoto stability; no Hebbian hit.
- **prove2me/formalpedia**: non-uniform Kuramoto definitions and theorems; no adaptive hit seen.
- **No Coq (.v) or Isabelle (.thy) Kuramoto formalization found.** The `.v` hits are Verilog FPGA files.

"First Lean proof about adaptive Kuramoto" is therefore **not** available as a claim. "First Lean proof of a capacity-gate threshold or clique OFF theorem" is plausible (not found).

### Recommended spot-1 wording

> Risk: **Moderate**. Multiplicative per-node limits on total Hebbian weight are classical (von der Malsburg 1973; Miller & MacKay 1994: "conserves or limits the total synaptic strength"). A multiplicatively normalized Hebbian phase-map network exists in discrete time (Ito & Kaneko 2000/2002, numerical). An inequality row-sum budget on Hebbian Kuramoto with Lean definitions exists (Cassie, flywheel-universe, by projection). Martens & Bick 2025 list "alternative constraint types" only generically, and their framework uses linear equality constraints. Plausibly new (not found): the min-endpoint over-cap multiplicative gate, the gate bracket (Lemma 1), and the threshold consequence that a locked k-clique with c/(k−1) < B_c is certified OFF, machine-checked. This is mathematically elementary.

## A2. Spot 2: discrete-time adaptive freeze plus timestep sweep ("discrete papers found keep links fixed")

**Rating verdict: ROUGHLY FAIR, slightly optimistic.** I would rate it **Low-moderate → Moderate**. The rigorous-theorem gap held up
under a harder search, but the supporting sentence needs a qualifier.

- **What held up.** I found no *theorem* about discrete-time or Euler-discretized **adaptive-coupling** Kuramoto, or co-evolving phase-network
  synchronization or freezing. Searches covered:
  - Crossref: "discrete-time adaptive Kuramoto Hebbian…", "time-discrete Kuramoto model adaptive couplings", "coupled map lattice adaptive coupling Hebbian";
  - arXiv API: Kuramoto ∧ discrete ∧ adaptive/Hebbian/plastic; "adaptive coupling" ∧ Euler ∧ Kuramoto, which returned 0; Berner discrete adaptive, which returned no relevant hit;
  - web searches.

  The rigorous discrete Kuramoto papers all use fixed coupling:
  - Ha–Kim–Kim–Zhang JMP 2019;
  - Zhang–Zhu, **CMS 18 (2020) 535–570**, [10.4310/cms.2020.v18.n2.a11](https://doi.org/10.4310/cms.2020.v18.n2.a11). This is the journal version of arXiv:1909.03358 and is new information;
  - Shim 2020;
  - Dong–Ha–Kim 2020;
  - Zhang–Xiao 2024;
  - Ha–Lee–Yoon 2025;
  - Wu 2026.

  The adaptive Ha-school papers are all continuous-time:
  - HNP 2016;
  - Ha–Lee–Li–Park SIADS 17 (2018) 1560–1588, [10.1137/17M1124048](https://doi.org/10.1137/17M1124048);
  - Cho–Dong–Ha 2023/2024;
  - Wang–Dong 2025, by title.
- **What needs qualifying.**
  - (a) "Discrete papers keep links fixed" is false as a statement about the literature. **Ito & Kaneko 2000** (see A1) is a discrete-time phase-map network with Hebbian coupling plus normalization, and Ito–Kaneko 2002 / Ito–Ohira PRE 64 066205 (2001) ([10.1103/PhysRevE.64.066205](https://doi.org/10.1103/PhysRevE.64.066205), metadata only) are discrete-time adaptive map networks. They are numerical, not theorems. Plüss & Gleiser, Nonlinear Sci. 9 (2026) 100215 ([10.1016/j.nls.2026.100215](https://doi.org/10.1016/j.nls.2026.100215), metadata only, abstract unread) continues that line.
  - (b) The control literature has discrete-time **adaptive-gain** synchronization theorems for networks, e.g. [10.22436/jnsa.010.11.01](https://doi.org/10.22436/jnsa.010.11.01) (search snippet only, not Crossref-checked). These are adaptive control gains, not Hebbian edge weights, but they are relevant to the "discrete adaptive" framing.
  - (c) An explicit step count for an affine contraction is textbook, and a dt sweep is a numerical robustness study, not a novelty carrier.

**Recommended spot-2 wording:**

> Risk: **Low-moderate to moderate**. No rigorous theorem was found for discrete-time adaptive-coupling Kuramoto. Rigorous discrete Kuramoto results use fixed coupling, and rigorous adaptive results are continuous-time. Discrete-time adaptive phase-map networks exist numerically (Ito & Kaneko 2000/2002), and discrete-time adaptive-gain synchronization theorems exist in control. The contribution would be a conditional, elementary finite-step certificate for this specific clipped and gated map. The dt sweep is supporting evidence, not novelty. Search non-exhaustive (no Scholar or full text).

## A3. Map items flagged unverified: what I could resolve

| Item | Result |
|---|---|
| Wang & Dong, JDE 441 (2025) 113475 | **Partly resolved.** Title, authors and DOI are **V** (Crossref; SSRN preprint [10.2139/ssrn.5225287](https://doi.org/10.2139/ssrn.5225287) also V). Elsevier API: pii S0022-0396(25)00502-9, cover date 5 Oct 2025, not open access. **Abstract and theorems still unverified** (ScienceDirect blocked; web search returned no abstract) |
| Ha–Noh–Park 2016 theorem statements | **Not resolved.** Only the abstract (V) and secondary accounts: Bronski 2017 and the CMS 2024 abstract, which says HNP needed a quarter arc (homogeneous) and an a-priori phase-diameter bound (heterogeneous anti-Hebbian). Coupling convergence remains unverified |
| Cho–Dong–Ha 2023: anti-Hebbian couplings decay to 0 | **Not resolved from a primary source.** ScienceDirect returned 400 or a shell page; the Elsevier API has no abstract. A web-search synthesis asserted it, but I could not see the source text. It *follows mathematically* if all Δθ → 0 under κ̇ = μ\|sinΔθ\| − γκ, but whether the paper states it is **unverified** |
| OpenAlex-only DOIs | **Resolved.** Throm, "Continuum limit for interacting systems on adaptive networks", EJAM 37 (2024 online) 706–720, [10.1017/s0956792524000354](https://doi.org/10.1017/s0956792524000354) (V). Dutta, Kundu, Khanra, Hens, "Transition to synchronization in the adaptive Sakaguchi-Kuramoto model with higher-order interactions", PRE 110, 064317 (2024), [10.1103/PhysRevE.110.064317](https://doi.org/10.1103/PhysRevE.110.064317) (V). Also found: Cestnik & Martens, "Continuum limit of the adaptive Kuramoto model", Chaos 35, 013109 (2025), [10.1063/5.0226759](https://doi.org/10.1063/5.0226759) (V, metadata). The DOI for Nagahama et al. Chaos 2025 is still unresolved |

## A4. Other notes

- Map §2.2 and the table describe M&B's future work as "curved constraint manifolds". The quote is correct, but the AIEFS gate is not a curved-manifold constraint. Please do not present it as answering M&B's future work.
- flywheel-universe should be described as having "inequality row-sum budget (projection) with Lean definitions and KKT/Lyapunov core". Calling it only "exact projection" undersells it as prior art for spot 1.
- The GitHub code search hit a rate limit (HTTP 403) partway through, so the formalization search is incomplete.
