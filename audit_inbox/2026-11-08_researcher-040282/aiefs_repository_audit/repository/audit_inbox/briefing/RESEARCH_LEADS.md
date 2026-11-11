# Research leads (literature only)

Status: **proposed, checked by Auditor Seat 002, verdict AGREE WITH CHANGES (2026-10-31).** The corrections below are applied. The ledger row is **PENDING** on `research/freezing`.

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

## RES-FREEZE-01 novelty: proposed rescope (PENDING ledger row RES-FREEZE-NOVELTY)

- **Proposed label:** `Known variant (partial overlap; consistency hit) — narrow residual plausibly new, search non-exhaustive`.
- **Overlap (known):** "phase-locking ⇒ relax-to-target Hebbian couplings converge", and so, given a strict margin, an eventually constant thresholded edge set. Cho–Dong–Ha 2023 publish this for an inertial continuous-time model and *prove* the locking that AIEFS assumes (O1).
- **Counts only as a consistency hit.** It is not validation of the gate, delay, EMA or N.
- **Residual, plausibly new (narrow, elementary):** it rests on
  - **Lemma 1**, a gate-independent bracket on the gate factor;
  - **Thms 2–3**, strict-margin OFF / ON / gated-OFF certificates. The main one is the capacity-gated-OFF case: a locked clique of size ≥ 7 is pushed below threshold. No precedent for this was found.
  - All of this is conditional on coherence bands holding on [T,∞).
- **Not what carries the novelty:** discrete time (discrete and Euler Kuramoto theory with fixed couplings exists) and the explicit N (a textbook iteration count; paper-level only; Lean has ∃N).
- **Search was non-exhaustive:** arXiv, Crossref and web on 2026-10-31; no Scholar and no full text.
