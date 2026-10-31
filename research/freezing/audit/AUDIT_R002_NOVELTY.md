# AUDIT_R002_NOVELTY: copy of the Auditor Seat 002 novelty audit of RES-FREEZE-01

**What this is.** A copy of the read-only novelty audit by **Auditor Seat 002**, dated **2026-10-31** (America/Toronto).
It was committed to the repo on 2026-10-31 so that the `RES-FREEZE-NOVELTY` ledger row and REPORT.md §5 can cite it. The
text below the line is verbatim except for two changes: the auditor's identity line was removed, and the local filesystem
paths of two inputs were replaced by "[local review note]" / "[local note]". Nothing in the findings was changed. The
two local inputs are not in the repo: `FREEZING_PROPOSAL.md` (the Corollary 4 fix proposal) and a people/literature scan.
Personal details from that scan are not reproduced here.

**What it audited.** The novelty of the single row `RES-FREEZE-01` at branch tip `85ba0a6` (before the 4-row split), and
Researcher 001's proposal to rescope it.

**What changed since, on this branch.**

* The split it could not see ("Split not seen", §5) is now committed: `LEAN-FREEZE-CORE`, `RES-FREEZE-GATED`,
  `RES-FREEZE-NUM` and `RES-FREEZE-NOVELTY` in `registry/claims.csv`.
* The Corollary 4 fix it asks for (§1, §5) is in REPORT.md §3. The proof uses the state-free bound
  ℓ_f^0 = (1 − ρ_f^{N1})·x*_f, revised on 2026-10-29 after Researcher 026's external review. That revision has not been
  independently re-audited.
* §4's recommendation is applied in `RES-FREEZE-NOVELTY` and REPORT.md §0/§5. The ledger vocabulary has no value for the
  label or for "Literature assessment (non-exhaustive)", so they sit in the free-text columns. The label is the
  `audited_qualifier`, with `audited_status` `Not established`. The scope sits at the start of
  `scope_boundary_and_caveat`. `artifact_status` / `evidence_scope` keep the nearest checked values, `Incomplete` /
  `Conjecture`. `Frozen`, `Retired`, `Superseded` and `Rejected` are not used.

---

## RES-FREEZE-01 novelty audit (independent, read-only)

Sat Oct 31, 2026, ~11:15 AM EDT. Scope: Researcher 001's proposal to rescope the novelty of RES-FREEZE-01
(`origin/research/freezing` tip `85ba0a6`, fetched today) and the planned RES-FREEZE-NOVELTY row. I pushed nothing, edited nothing in the
repo or ledger, and contacted nobody.
Inputs: `research/freezing/REPORT.md`, `README.md`, `registry/claims.csv` (RES-FREEZE-01 row) and
`lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean` at `85ba0a6`; `FREEZING_PROPOSAL.md` [local review note];
the 2026-10-31 people/literature scan [local note].

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
