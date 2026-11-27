# Research leads (literature only)

_Re-checked 2026-11-20 4:10 PM MST: still current; no new literature round has been triaged since. Novelty remains not established. Arena's ten literature rounds of 2026-10-31 sit on `arena/d4a487cc-aiefs` (owner hold) and have not been reconciled claim by claim._

Status: **proposed, checked by Auditor Seat 002, verdict AGREE WITH CHANGES (2026-10-31).** The corrections below are applied. The ledger row **RES-FREEZE-NOVELTY** is on `main` (PR #3); novelty status remains Not established / non-exhaustive search.

Sources (box-side, not in the repo):
- a literature scan by Researcher 001 (2026-10-31);
- Auditor Seat 002's novelty audit of RES-FREEZE-01 (2026-10-31, against `research/freezing` `85ba0a6`).

Labels:
- **V**: metadata confirmed against Crossref or arXiv.
- **unverified**: a content claim that has not been confirmed.

Leads only. Do not cite any of these as validating AIEFS unless the specific match has been checked.

**Do not contact any of these people; outreach is owner-only.**

## Papers and code

| Ref | Link | Checked | Maps to |
|---|---|---|---|
| Cho, Dong & Ha, "Interplay of inertia and adaptive couplings in the emergent dynamics of Kuramoto ensemble", J. Differential Equations 360 (2023) 523–571 | https://doi.org/10.1016/j.jde.2023.03.047 | V (abstract plus zbMATH review). Inertial, continuous-time, κ̇ = μΓ(Δθ) − γκ with Γ = cos or \|sin\|. It proves phase sync **and** coupling convergence. The "(FA)" framework and K∞ details are unverified (full text not read). | **Real prior art** for RES-FREEZE-01's mechanism. The 2026-10-28 novelty search missed it. |
| Ha, Noh & Park, "Synchronization of Kuramoto oscillators with adaptive couplings", SIADS 15(1) (2016) 162–194 | https://doi.org/10.1137/15M101484X | V (abstract only). Laws that preserve the sum of incoming couplings; sync frameworks. | **Related only.** Coupling convergence is **not confirmed**, so it does not pre-empt freezing. Relevant to the capacity gate and normalisation (AUD-RATELAW). Already cited in REPORT §5. |
| Ha, Li & Xue, JDE 255 (2013) 3053–3070 | https://doi.org/10.1016/j.jde.2013.07.013 | V | Gradient flow plus Łojasiewicz, with fixed couplings. A route for **O1**. |
| Ha & Ryoo, Commun. Math. Phys. 377 (2020) 811–857, and its Correction, CMP 403 (2023) 1627 | https://doi.org/10.1007/s00220-020-03786-1 · https://doi.org/10.1007/s00220-023-04820-8 | V (metadata). Content of both not re-checked. | Locking with heterogeneous ω, for **O1**. Cite the Correction too. |
| Dong, Ha & Kim, SIADS 19(1) (2020) 304–328 | https://doi.org/10.1137/19M1249096 | V (zbMATH). Delayed Kuramoto and its Euler discretisation, fixed coupling. | Delay τ = 0.5 (AUD-DELAY); discrete-time precedent. |
| Cho, Ha & Kang, J. Nonlinear Sci. 35 (2025) paper 9 | https://doi.org/10.1007/s00332-024-10099-3 | V (metadata). Abstract unverified. | Possibly analogous to the EMA (fading memory). This is inferred from the title only. |
| Cho, Dong & Ha, CMS 22 (2024) 2041–2057; Wang & Dong, JDE 441 (2025) 113475 | https://doi.org/10.4310/CMS.240918042900 · https://doi.org/10.1016/j.jde.2025.113475 | Unread | Further adaptive-coupling prior art to add to the REPORT §5 search log. |
| Niyogi & English, PRE 80, 066213 (2009) | https://doi.org/10.1103/PhysRevE.80.066213 · arXiv:0908.4220 | V (arXiv abstract) | A critical learning rate and anti-phase clusters, numerical. Closest physics precedent for U-THRESH / U-MULTISTAB. |
| Timms & English, PRE 89, 032906 (2014) | https://doi.org/10.1103/PhysRevE.89.032906 · arXiv:1307.8398 | full text skimmed in the scan; not re-checked by Auditor Seat 002 | Delay plus Hebbian adiabatic coupling. Already cited in AUD-DELAY and EMP-AIEF13-02, so phrase AIEFS delay results as a "variant of" this. |
| kuramoto-lean (MIT, Lean v4.31.0-rc1) | https://github.com/velvetmonkey/kuramoto-lean | Source read, not built; no CI | Identical oscillators (ω = 0), no delay, EMA or gate, so it does not pre-empt AIEFS Lean. The Euler step-bound / contraction theorems are a template for the dt study. Barbalat is **`private`** there (Frontier.lean:205). **LaSalle is not in it**; it is in the separate repo `lasalle-lean` (barbalat-lean is also separate). `#print axioms` is used only 6 times, not per theorem. AIEFS uses Lean v4.33.1, so reuse needs porting and attribution. |
| flywheel-universe (Zenodo, not peer-reviewed) | https://doi.org/10.5281/zenodo.20469680 | DOI resolves; paper contents not read | "Budgeted Hebbian Kuramoto plus freeze", with a scheduled freeze and exact projection. Mention it as related work for the gate/freeze design. |

## Model mismatch to keep in mind

The AIEFS R is the modulus of a complex EMA, so it is **phase-offset invariant**: an anti-phase locked pair has R → 1. Published limit formulas of the form K∞ = α cos(Δθ∞) (Niyogi–English, Bronski et al.) therefore **do not carry over literally**.

## RES-FREEZE-01 novelty: rescoped ledger row RES-FREEZE-NOVELTY (on `main`)

- **Proposed label:** `Known variant (partial overlap; consistency hit) — narrow residual plausibly new, search non-exhaustive`.
- **Overlap (known):** "phase-locking ⇒ relax-to-target Hebbian couplings converge", and so, given a strict margin, an eventually constant thresholded edge set. Cho–Dong–Ha 2023 publish this for an inertial continuous-time model and *prove* the locking that AIEFS assumes (O1).
- **Counts only as a consistency hit.** It is not validation of the gate, delay, EMA or N.
- **Residual, plausibly new (narrow, elementary):** it rests on
  - **Lemma 1**, a gate-independent bracket on the gate factor;
  - **Thms 2–3**, strict-margin OFF / ON / gated-OFF certificates. The main one is the capacity-gated-OFF case: a locked clique of size ≥ 7 is pushed below threshold. No precedent for this was found.
  - All of this is conditional on coherence bands holding on [T,∞).
- **Not what carries the novelty:** discrete time (discrete and Euler Kuramoto theory with fixed couplings exists) and the explicit N (a textbook iteration count; paper-level only; Lean has ∃N).
- **Search was non-exhaustive:** arXiv, Crossref and web on 2026-10-31; no Scholar and no full text.

## H8 additions and verification levels (Researcher 001, 2026-11-26 ~2:10 PM MST)

_Plan item H8 (`PLAN_2026-11-25_scan_leads.md`), as changed by Auditor Seat 002's review (`REVIEW_2026-11-26_auditor_scan_leads.md`, audit-inbox `b15c5e5`; the review wins). Sources: Researcher 001's box scans of 2026-11-25 (first pass 10:08 AM MST, second pass 11:05 AM MST). Leads only: nothing here validates AIEFS, and novelty stays "not established". **No outreach.**_

Verification levels: **full text read** / **abstract** / **third-party review (zbMATH/MaRDI)** / **metadata only** / **source read (code)** / **UNVERIFIED**. A level says how far *we* checked, not how good the paper is.

### Levels for the entries above (unchanged content, tags only)
| Entry | Level |
|---|---|
| Cho, Dong & Ha, JDE 360 (2023) | abstract + third-party review (zbMATH); "(FA)" framework and K∞ details UNVERIFIED |
| Ha, Noh & Park, SIADS 15 (2016) | abstract |
| Ha, Li & Xue, JDE 255 (2013) | metadata only (route for O1 is our inference) |
| Ha & Ryoo, CMP 377 (2020) + Correction CMP 403 (2023) | metadata only |
| Dong, Ha & Kim, SIADS 19 (2020) | third-party review (zbMATH) |
| Cho, Ha & Kang, JNS 35 (2025) "Fading Memory" | **UNVERIFIED** (closed access; publisher elides the abstract). **No EMA analogy may be claimed.** |
| Cho, Dong & Ha, CMS 22 (2024) | metadata only |
| Niyogi & English, PRE 80 (2009) | abstract |
| Timms & English, PRE 89 (2014) | full text skimmed by Researcher 001 (not re-checked by Auditor Seat 002) |
| kuramoto-lean | source read (code), not built |
| flywheel-universe | metadata only (DOI resolves) |

### New entries
| Ref | Link | Level | What it says (as far as checked) | Maps to |
|---|---|---|---|---|
| Wang & Dong, "Emergent dynamics of the Kuramoto model with adaptive coupling on undirected networks", JDE 441 (2025) 113475 | https://doi.org/10.1016/j.jde.2025.113475 · review: https://portal.mardi4nfdi.de/wiki/Emergent_dynamics_of_the_Kuramoto_model_with_adaptive_coupling_on_undirected_networks | **third-party review (zbMATH/MaRDI); full text not read** | Model θ̇_i = ω_i + Σ a_ij κ_ij sin(θ_j − θ_i), κ̇_ij = μΓ(θ_i − θ_j) − γκ_ij, Γ = cos (Hebbian) or \|sin\| (anti-Hebbian). Per the review: Hebbian, homogeneous connected symmetric network ⇒ exponential phase sync from a quarter circle (up to π under extra assumptions); anti-Hebbian ⇒ at least algebraic sync below π with explicit coupling bounds; heterogeneous: two sufficient topology conditions for locking from a quarter circle. **Coupling convergence is not stated in the review.** | Closest published continuous analogue of the AIEFS relax-to-target-with-decay law (no EMA, delay or gate). Prior art for RES-FREEZE's "known variant" overlap and for O1 (it proves locking AIEFS assumes). |
| Carty, Choi, Cicolani & Pignotti, "Asymptotic synchronization of Kuramoto oscillators with time delay and non-universal interaction" | https://arxiv.org/abs/2406.01703 | **full text read** (Lemma 2.3, eq. (2.1), Thm 4.1) | Fixed couplings, digraph, delay τ_ij. Small τ + large κ + D_θ(0) < π ⇒ frequency sync (exponential all-to-all). R_ω := max\|Ω_i\| + κ; Lemma 2.3 needs d_∞ + R_ω τ < π/2 and a κ lower bound containing (N−1)·c with c = (Σ_{j=1}^{N−1} η^j P(2N, j) + 1)·ξ/sin ξ, η > 2. | **Not applicable at AIEFS τ = 0.5, N = 12.** By our arithmetic (re-checked by Auditor Seat 002), c ≳ 2^11·P(24,11) ≈ 2.04e17 and (N−1)c ≳ 2.24e18, a lower bound under η > 2; with τ = 0.5 the condition R_ω τ < π/2 also forces κ + max\|Ω\| < π while κ must be huge. Qualitative template for O1 only; cite with this caveat. (Lemma 2.3 reading is Researcher 001's; the auditor did not re-read the paper.) |
| Ha, Lee, Li & Park, "Emergent dynamics of Kuramoto oscillators with adaptive couplings: conservation law and fast learning", SIADS 17(2) (2018) 1560–1588 | https://doi.org/10.1137/17M1124048 | **abstract** | Two laws: Picallo–Riecke (sufficient sync frameworks) and Ha–Noh–Park "Model A" in a slow–fast setting where **couplings are fast and phases slow**; Tikhonov limit, classification of locked states, complete-sync frameworks. The conservation law preserves the sum of incoming couplings. | Related work / AUD-GATE wording only. **Opposite time-scale regime to AIEFS** (AIEFS couplings are slow), and the conservation law is not a cap. |
| Jamali, "Amplifying or Redistributing Coupling: Synchronization in Sparse Adaptive Oscillator Networks" (preprint, Nov 2026) | https://arxiv.org/abs/2611.24268 | **full text read** (model and exact-identity sections) | τu̇_ij = 1 + a cos(θ_j − θ_i) − u_ij; compares static, Hebbian (w = u) and divisive homeostatic normalization w_ij = k0·u_ij/Σ_l C_il u_il. Exact: normalization conserves incoming effective coupling; mean raw weight relaxes toward 1 + a·C_E(t). Numerical: the normalized network needs stronger coupling for a given synchrony (finite windows). | Related work for AUD-GATE: an always-on per-node divisive rule, which the AIEFS min(1, c/q) per-edge min-endpoint cap is *not*. Single-author preprint, not peer-reviewed; no delay or freezing. |
| Anand, Fialkowski, Chandrasekar & Suresh, "Delay-Controlled Heterogeneous Nucleation in Adaptive Dynamical Networks" (preprint 2026) | https://arxiv.org/abs/2604.04428 | **full text read** (model and bound sections) | k̇_ij = −ε(k_ij + sin(φ_i(t) − φ_j(t−τ) + β)); perturbative collective-coordinate upper bound, as a function of τ, for existence of two-cluster states; distributed delays too. | Outside cross-check for any AIEFS two-cluster / τ-dependence observation (U-MULTISTAB). Heuristic, not a theorem; different drive. |
| Berner, Gross, Kuehn, Kurths & Yanchuk, "Adaptive Dynamical Networks" (review, 2023) | https://arxiv.org/abs/2304.05652 | **abstract** + model equations seen | Model class κ̇_ij = −ε(κ_ij + h(φ_i − φ_j)) (relax-to-target with decay). | Related-work anchor; AIEFS is a variant of this class (EMA-modulus drive, gate, delay). |
| Berner, Schöll & Yanchuk, "Multi-clusters in networks of adaptively coupled phase oscillators", SIADS 18 (2019) | https://arxiv.org/abs/1809.00573 | **abstract** + §4.2 skimmed | Explicit multi-cluster solutions; stability conditions, several computed numerically. | Cross-check source for U-MULTISTAB. |
| Alanazi, Mueller & Townley, SIADS 24(1) (2025) 68–93 | https://doi.org/10.1137/23M1590639 | **abstract** | Teacher–learner tracking; weights converge only if training phases are unclustered. | **Off-model** (no self-organised Hebbian law). Listed so nobody re-checks it. |

### Tooling leads (code; source read, not built)
| Lead | Link | Level | Status |
|---|---|---|---|
| Mathlib `Analysis/ODE/DiscreteGronwall.lean` | https://github.com/leanprover-community/mathlib4/blob/master/Mathlib/Analysis/ODE/DiscreteGronwall.lean | source read; present at our pin `0df444a` | Used by plan H9(b) (product form only; `discrete_gronwall` is the growth form). |
| Mathlib `Topology/MetricSpace/Contracting.lean`, `Trigonometric/Angle.lean` (`coe_toIcoMod`), `Order/ToIntervalMod.lean` | (Mathlib, pinned) | source read; present at our pin | H16 (auditor) and H17 (`research/h17-wrapphase-toicomod`). |
| LeanPool `Kuramoto/Hebbian.lean` (Apache-2.0) | https://github.com/LeanPool/lean-pool/blob/main/LeanPool/Kuramoto/Hebbian.lean | source read (L30/L35/L209) | H12 contrast note; **cite only, no vendoring** (H15 deferred). Lean v4.36. |
| LeanForControl (Apache-2.0) | https://github.com/AnandGokhale/LeanForControl | source read | H14 deferred (v4.36, `Architect` dependency). |
| LeanCert (Apache-2.0) | https://github.com/alerad/leancert | README/docs read | H14 deferred: no current target (0.454286 = 159/350, 3/7 rational). Default mode uses `native_decide`; axiom audit, not grep, is the control. |
| LeanBlueprint | https://github.com/PatrickMassot/leanblueprint | README read | H19 deferred (owner call). |

### Rejected (do not re-check)
polyrith (Sage server shut down, per Mathlib source); LeanDojo/LeanCopilot (AI proof search, no added trust); Duper (poor fit for real inequalities); lasalle-lean / lyapunov-odes-lean (v4.28, superseded by Mathlib `Dynamics/Flow`, `OmegaLimit` and LeanForControl); Gkogkas–Kuehn continuum limits, CMS 21 (2023) (N → ∞ only); mutmut/cosmic-ray on the engine (SHA-locked; the bespoke H3 mutation tester exists); rate-model synaptic-scaling papers (AMS Notices 2024, bioRxiv 2025.04.10.648137: seen in search snippets only, UNVERIFIED, not phase oscillators).

### H8 corrections after audit (Researcher 001, 2026-11-27 MST; add-only; Auditor Seat 002 CLEAN WITH NOTES on `0d40452`)
_Each line below corrects or supersedes text above, which is left in place. Where they disagree, this subsection wins._

1. **Time (supersedes "~2:10 PM MST" in the H8 header above, and "~2:15 PM MST" in the H8 line in STATE.md):** H8 was
   committed at 2026-11-26 1:48 PM MST (20:48 UTC), commit `0d40452`.
2. **Path (corrects the tooling row "`Order/ToIntervalMod.lean`"):** the file is `Mathlib/Algebra/Order/ToIntervalMod.lean`.
   Checked with `git ls-files` in the pinned Mathlib checkout at `0df444a360eaa60ab8c11dca51a86af692955474`. That is
   the only ToIntervalMod file there, and `Mathlib/Order/ToIntervalMod.lean` does not exist. The other rows check out at
   the same pin:
   - `Mathlib/Analysis/ODE/DiscreteGronwall.lean` and `Mathlib/Topology/MetricSpace/Contracting.lean` exist.
   - `coe_toIcoMod` is at `Mathlib/Analysis/SpecialFunctions/Trigonometric/Angle.lean` L417.
3. **Tooling header (corrects "### Tooling leads (code; source read, not built)"):** that is true only of the Mathlib,
   LeanPool and LeanForControl rows. **LeanCert** is **README/docs read** and **LeanBlueprint** is **README read**,
   with no source read, as their per-row tags say. The per-row Level column is authoritative.
4. **Superseded, old Cho–Ha–Kang row** ("Possibly analogous to the EMA (fading memory). This is inferred from the title
   only…"): **SUPERSEDED.** No EMA analogy is claimed; see item 6.
5. **Superseded, old combined row** "Cho, Dong & Ha, CMS 22 (2024); Wang & Dong, JDE 441 (2025) … | Unread":
   **SUPERSEDED.** The levels are now Cho–Dong–Ha CMS 22 = **metadata only** and Wang–Dong = **third-party review
   (zbMATH/MaRDI); full text not read** (the H8 tables above).
6. **Cho, Ha & Kang, JNS 35 (2025), "Emergent Behaviors of a Kuramoto Ensemble Under Fading Memory"**
   (https://doi.org/10.1007/s00332-024-10099-3):
   - The earlier tag reason "publisher elides the abstract" **is wrong as of 2026-11-27**. The Springer page now serves
     the abstract.
   - **New level: abstract** (read 2026-11-27).
   - What the abstract says: the Kuramoto model with a memory effect, posed as Volterra-type integro-differential
     equations on the circle. The memory enters through nonlocal temporal interactions in the **phase** dynamics. The
     paper gives well-posedness, a framework for a bounded phase diameter, and complete frequency sync (by bootstrap and
     by an energy functional). For identical frequencies it gives complete phase sync.
   - **The no-EMA-analogy conclusion still holds.** In this paper the memory weights past interactions in the phase law,
     with fixed coupling. The AIEFS EMA is a complex average of the delayed phase difference. Its modulus R drives the
     **weight** law. The abstract gives no adaptive coupling and no kernel form, so no EMA analogy is claimed.
7. **Ha, Lee, Li & Park, SIADS 17 (2018)** (corrects "The conservation law preserves the sum of incoming couplings"
   in its row):
   - **The 2018 abstract** (Crossref, re-read 2026-11-27) **does not say what is conserved.** It mentions a
     conservation law only in the title.
   - The "preserves the sum of all incoming pairwise coupling strengths" property is in the **Ha–Noh–Park 2016
     abstract** (SIADS 15, https://doi.org/10.1137/15M101484X, re-read 2026-11-27), which introduced Model A.
   - Whether the 2018 conservation law is that same property is **UNVERIFIED** (full text not read). The row's level
     stays **abstract**; that sentence is now attributed to the 2016 abstract, not to the 2018 one.
