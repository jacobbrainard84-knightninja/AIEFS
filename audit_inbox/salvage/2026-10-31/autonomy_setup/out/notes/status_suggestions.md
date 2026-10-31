# Suggestions for CURRENT_STATUS.md §4 (not a repo file — offer to the status author)

Prepared by Auditor Seat 002, 2026-10-28, against the merge-prep branch `merge-prep/arena-reconciled`
at `11de659` (local, unpushed). **Suggestions only.** `CURRENT_STATUS.md` is the single status file and
belongs to its author; nothing here was written into the branch. Line numbers refer to that commit;
`claims.csv:N` is the physical line of the row (header = line 1). Items marked **(uncertain)** need a check.

## Gap noticed

§4 "Where we are" (`CURRENT_STATUS.md:79-83`) lists the branch state (ledger size, errata, report), but not
the tested model results themselves. The owner's three-part view asked for them. Suggested bullets below; each
cites a ledger row and a source file.

## Suggested "Where we are — tested model results"

- **Model.** 12 delayed Kuramoto oscillators, an exponentially averaged (EMA) coherence `R`, Hebbian edge
  weights `B`, and a capacity gate (`README.md:3-4`). The gate is min-endpoint:
  `s_i = min(1, c/(q_i+ε))`, `B'_ij = x_ij·min(s_i, s_j)` (`AI Agent Audits/AIEFS_audit_response_2.md:29`),
  with `c = (A−δ)/Q = 0.6333` (A = 1, Q = 1.5, δ = 0.05; `AI Agent Audits/AIEFS_salvage.md:38`;
  `capacity = 0.6333…` in `AIEF_1_4_proposal_equalization_bridge_analysis.py:200`). It is node-strength
  normalisation, not a projection (AUD-GATE, `registry/claims.csv:47`).
- **Rate law — exact only under conditions.** One-step multiplier `λ = (1 − γ·dt)·s_J` on the controller
  cycle kernel, exact only with (a)–(e), including (e) equal controlling scales `s_i = s_J` on J
  ("equal-scale fibers"). Conditional closed form under the further ideal hypotheses R = 1 and row sum c:
  `λ_k = (1 − γdt)·c / (c + dt(kη − γc) + ε)`; `κ_k = kη/c − 1/T_w` is its limit (AUD-RATELAW,
  `registry/claims.csv:50`).
- **374-case bounds split.** Checked on 374 resolved components: 264 two-sided fibers (λ to 2.1e-8 relative,
  κ to 2.1e-6) and 110 all-tied K3s on one-sided rays (λ to 1.7e-7, κ to 1.7e-5). The ~2e-8 gap is
  unexplained. Scope: 40 fixed seeds × 5 T_w, not independent replications (`registry/claims.csv:50`).
- **Old 18-coordinate spectrum / "unique slow pole": invalid, Quarantined.** The 18-coordinate map is not a
  closed state; do not cite either the YES or the audit's NO proposal (AUD-SLOWPOLE, `registry/claims.csv:49`;
  `ERRATA_2026-10-28.md` E2).
- **Corr_physical ≈ 0.995 holds only for the hand-picked frequencies.** ~0.71 (uniform random ω),
  0.59–0.63 (clustered) (AUD-CORR-0995, `registry/claims.csv:45`; `ERRATA_2026-10-28.md` E1).
- **Matched-phase ablation: Exploratory.** Weighted_similarity_late +0.064 [0.041, 0.089] (31/40),
  P_mean_late negative, Retention CI spans 0; no mediation claim (EMP-AIEF14-02, `registry/claims.csv:5`).
- **Split-state memory ablation (40 paired seeds): Supported (audit-qualified, reworded).** B is not a unique
  memory bottleneck: resetting B at the split time rebuilds mature topology almost identically from the delayed
  oscillator/EMA state (EMP-AIEF14-01, `registry/claims.csv:4`; artifact_status Frozen).
- **Scope of AIEF-1.4 operator work:** a single-seed case study (1 of 40) (AUD-SCOPE-1.4, `registry/claims.csv:48`).
- **Lean.** `lean/AIEFProofs`, toolchain `leanprover/lean4:v4.33.1` (`lean/AIEFProofs/lean-toolchain`);
  115 declarations audited, only `propext`, `Classical.choice`, `Quot.sound`; 0 `sorry`/`admit`
  (LEAN-R4, `registry/claims.csv:62`). The proofs are linear-algebra/incidence facts, not dynamics
  (LEAN-CF-01, `registry/claims.csv:8`). CI: `.github/workflows/lean.yml` (axiom-audit allowlist and
  `check_lean.sh` step 7).

## Suggested "Where we've been" addition

- SSRH origin hypotheses `SSRH-ORIG-01..07` (`registry/claims.csv:63-69`): *Speculative / untested origin
  hypothesis*. Valued as where the project came from; the numbers appear only in AI-chat text in
  `Project Origins/` and no script or data computes them (reconciliation note on those rows). Not retired.

## Suggested "Where we're going" — each with what would test it

| Open question | Ledger | What would test it |
|---|---|---|
| Testable forms of the SSRH origin ideas | `SSRH-ORIG-01..07` | Each row's `reconciliation_note` states what would test it, e.g. SSRH-ORIG-01: "testable form not yet stated", then a simulation of gain vs parameters with Lyapunov exponents (`claims.csv:63`; rule in `registry/README.md:60`). First step: write one falsifiable statement per row with a dataset and a pre-stated threshold. **(uncertain: which, if any, are in scope for this repo)** |
| Do coupled phase/EMA dynamics force both K3 proposal differences to zero? | CF11, `claims.csv:20` | A proof, or long-horizon runs on many seeds showing the differences decay (or not). Ledger: "no proof or test in the repo". |
| Do the exceptional support, clipping and winner branch persist for all time? | CF12, `claims.csv:21` | A proof of persistence, or a counterexample trajectory. Same ledger note. |
| Do the single-seed AIEF-1.4 results hold on other seeds? | AUD-SCOPE-1.4, `claims.csv:48` | Re-run the operator/cocycle/controller pipeline on more seeds of the 40 (already listed in `CURRENT_STATUS.md` §4 "Where we're going" item 4; resp1 §6 Limits notes the Duhamel pipeline was not re-run on other seeds). |
| What explains the ~2e-8 rate-law gap? | AUD-RATELAW, `claims.csv:50` | Isolate the term (ledger: finite ε changes λ by only ~1.6e-12; "the gap is not isolated"). |
| Is there a valid slow-pole statement on the closed state? | AUD-SLOWPOLE, `claims.csv:49` | An analysis on the closed 966-dim state with more than one replay and a non-finite-difference method; until then, nothing citable. |
| Does the T_window DID / horizon-confounding claim hold? | EMP-AIEF14-03, `claims.csv:6` | An audit test of the DID estimand itself (the audits only checked κ(T_w)). |
| Does Corr_physical or the topology predictor carry over to random frequencies? | AUD-CORR-0995, AUD-TOPO-OMEGA, `claims.csv:45-46` | Random/clustered ω cohorts with held-out seeds; the audit's numbers already suggest it does not. |
| Are the results novel? | AUD-NOVELTY, `claims.csv:58` | A literature review (ledger: "open owner decision"). |
