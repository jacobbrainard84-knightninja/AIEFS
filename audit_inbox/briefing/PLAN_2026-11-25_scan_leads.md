# DRAFT for Auditor Seat 002 review: implementation plan for the 2026-11-25 scan leads

_Drafted 2026-11-25 10:35 AM MST by Researcher 001, at the owner's request (t232u: "make a plan with the other lead auditor to implement everything we can"). **Planning only.** No code, installs, branches or PRs exist yet. Source: the read-only scan of 2026-11-25 10:08 MST (box file `review_r001/2026-11-25_outside_scan.md`; summary row in `STATE.md`). Nothing here is adopted until Auditor Seat 002 reviews it and the owner agrees._

## Ground rules for every item
- **Usage gate.** Weekly usage was 61.9% at drafting. The soft stop is 50% Mon–Wed unless the owner raises it; the reset is **Fri 2026-11-27 12:02 PM MST**. **No item starts without the owner's go-ahead on usage.** "Cutoff-safe" means the item can stop at any commit and leave nothing half-claimed: no ledger row changes, and no claim wording changes.
- **Never touched:** `Pinned/`, `lean/AIEFProofs*`, `lean/AIEFFreezeCore`, ART-0076, `aief_experiment_engine_v1.py`. Engine work uses a **copy** under the item's own directory, and the item's tests check that the copy's hash is the pinned one.
- **Dual control.** The author pushes a branch; the other seat audits and opens the PR from the exact audited sha; only the owner merges. Merge commits only; no force push.
- **Lean rules.** No `sorry`/`admit`/`native_decide`; `#print axioms` shows only propext, Classical.choice, Quot.sound; outside Lean runs only under `unshare -rn`.
- **Anomalies stay UNEXPLAINED** unless a check actually closes them. A bound that fails to exclude something is reported as "not excluded", not as support.
- Every pass/fail rule gets a written reason in the same commit; any CI rule change is an owner decision.

## Work items

### H8. RESEARCH_LEADS additions (literature only)
- **Goal:** add the scan's verified leads with exact claim-level labels: Carty–Choi–Cicolani–Pignotti arXiv 2406.01703 (Theorem A: small τ, large κ, D_θ(0)<π ⇒ frequency sync; fixed couplings); Jamali arXiv 2611.24268 (divisive homeostatic normalization vs Hebbian; exact conservation and mean-weight relaxation identities; preprint); Anand et al. arXiv 2604.04428 (delay-dependent two-cluster upper bound, perturbative); Ha–Lee–Li–Park SIADS 17 (2018), doi 10.1137/17M1124048 (metadata verified; content unverified). Also record LeanPool `Kuramoto/Hebbian.lean` (contents verified at L30/L35/L209), Mathlib DiscreteGronwall, LeanForControl, LeanCert as tooling leads, plus the rejected list.
- **Deliverable / branch:** a commit on `audit-inbox` (briefing is not on main), file `audit_inbox/briefing/RESEARCH_LEADS.md` only.
- **Author:** Researcher 001. **Auditor:** Auditor Seat 002 re-opens each link and checks each claim against the source. No PR (audit-inbox stays out of main).
- **Red team:** the auditor spot-checks one deliberately mis-stated claim planted in the review copy only (e.g. "Carty proves sync for adaptive couplings"). The review must catch it before the real text is committed.
- **Effort:** low. **Order:** first. **Cutoff-safe:** yes. **Owner decision:** none (leads only, novelty unchanged).

### H9. DiscreteGronwall cross-check of `upper_geom` and n-step bounds (pinned Mathlib, no bump)
- **Goal:** (a) reprove the `AIEFFreezeCore.upper_geom` statement independently via Mathlib `discrete_gronwall_prod_general` / `discrete_gronwall`, in a new module, without editing AIEFFreezeCore. (b) Prove n-step envelopes for the exact-real B recurrence with a time-varying drive, for use in the AUD-TIMESTEP design (modelling choice (a) only).
- **Deliverable / branch:** `research/h9-discrete-gronwall`; new files `lean/AIEFGateCore/AIEFGateCore/DiscreteGronwallBridge.lean`, its README section and SPEC notes in `research/lean_gate/`, plus mutation entries. AIEFGateCore is not pinned; confirm this at branch time.
- **Author:** Auditor Seat 002 (cleaner split, since Researcher 001 wrote the scan). **Auditor:** Researcher 001, who opens the PR.
- **Red team:** mutation entries that weaken a hypothesis (drop `0 ≤ u n₀`, flip `≤`, use c > 1 where the geometric form needs c ≤ 1) must make the build fail. Add a statement-equality check that the new theorem's type is defeq to `upper_geom`'s statement (imported, not copied).
- **Effort:** low–med. **Order:** after H8; independent of H10–H11. **Cutoff-safe:** yes (new module only). **Owner decision:** none, beyond the usage go-ahead.
- **Caveat to state in the module header:** this bounds growth only. It does not give convergence, O1, or an explanation of E22.

### H10. Hypothesis gate property tests vs a Fraction oracle (W1–W5 generalized)
- **Goal:** property tests for the min-endpoint gate on a **copy** of the engine gate lines (L803–813): idempotence; per-edge factor = min(s_i, s_j); row sum ≤ cap (+ε); and the spillover/overshoot cases from the gate-form adjudication. Each is checked against an independent exact `fractions.Fraction` oracle written from the SPEC, not from the engine. W1–W5 become fixed `@example`s.
- **Deliverable / branch:** `research/h10-gate-properties`; new `research/gate_properties/` (oracle, tests, README), engine copy with a hash check, and a `requirements-dev` line if approved.
- **Author:** Researcher 001. **Auditor:** Auditor Seat 002, who opens the PR.
- **Red team:** three planted mutants in the copy must each be caught: one-endpoint factor `s_i`, `max` instead of `min`, cap off by 1%. A swapped expected/actual must also fail. CI uses `derandomize=True` with a fixed `max_examples`, so the gate is not flaky.
- **Spillover measurement:** report how often non-binding rows lose weight on seeded real-run states, as an **observation** (still UNEXPLAINED impact, no claim).
- **Effort:** low. **Order:** after H8; parallel with H9. **Cutoff-safe:** yes.
- **Owner decision:** **new dev dependency Hypothesis (MPL-2.0)**. Fallback if declined: the same properties with a seeded stdlib `random` generator, with no shrinking.

### H11. Arb / python-flint rigorous-bounds check of the E22 residual
- **Goal:** recompute the E22 single-gap-component step with ball arithmetic on an **engine copy** (one step, then the E22 window), to test whether float64 rounding can account for the residual. Outcome rule, predeclared in the branch's first commit: if the Arb enclosure of (exact − float64) is strictly smaller than the residual, report "rounding excluded as sole cause". Otherwise report "not excluded". **AUD-RATELAW stays UNEXPLAINED either way**, unless a separate mechanism is found and audited.
- **Deliverable / branch:** `research/h11-arb-e22`; new `research/arb_e22/` (predeclared rule, script, results JSON, report). No change to ERRATA without the owner.
- **Author:** Auditor Seat 002. **Auditor:** Researcher 001.
- **Red team:** a negative control injects a known 1e-12 perturbation into one copy step; the enclosure must flag it. A precision-starved run (e.g. 20-bit) must widen the balls and return "not excluded", which shows the rule can say no.
- **Effort:** med. **Order:** after H10 (reuses the copy-plus-hash harness). **Cutoff-safe:** yes, if the predeclared rule is committed before any run.
- **Owner decision:** **new dependency python-flint (MIT / LGPL-3.0)**. The fallback is `mpmath` interval mode, which is also a new dependency, or exact `Fraction` for the rational parts only. sin/cos need intervals.

### H12. LeanPool Hebbian contrast note (where the energy argument breaks)
- **Goal:** a paper-level note comparing LeanPool's `hebbian_joint_lyapunov_descent` (weight flow `(K/2)cos(θj−θi) − λW`, energy = weighted Kuramoto potential + (λ/2)‖W‖²) with the AIEFS law Ḃ = (η+μ)R − μ − γB. It should pinpoint each obstruction exactly: R is the modulus of a delayed complex EMA, not cos(Δθ), so it is phase-offset invariant and not a gradient; the delay; the non-smooth min-endpoint gate. It should also state which restricted regime, if any, admits a joint energy (candidate: τ = 0, EMA rate → 1, gate inactive). Optionally add a small Lean lemma showing the obstruction, e.g. the drive is not the partial derivative of any energy.
- **Deliverable / branch:** `research/h12-hebbian-contrast`; `research/hebbian_contrast/NOTE.md`. Citation with attribution only; **no LeanPool code copied**.
- **Author:** Researcher 001. **Auditor:** Auditor Seat 002.
- **Red team:** the note must include one regime where the naive energy argument *seems* to work but fails (a numerical counterexample on the engine copy where the candidate energy increases). If none can be found, say so explicitly; do not claim the obstruction is real without it.
- **Effort:** med. **Order:** after H9. **Cutoff-safe:** yes.
- **Owner decision:** none for citation. Copying or porting Apache-2.0 code would need the owner's decision (→ H15).

### H13. Discrete Halanay inequality in Lean on top of DiscreteGronwall (original contribution)
- **Goal, tightly scoped:** for a nonnegative real sequence with `u (n+1) ≤ a·u n + b·max_{n−d ≤ k ≤ n} u k`, a, b ≥ 0, a + b < 1, prove `u n ≤ (max of initial window)·ρ^(n/(d+1))` (or the cleaner `ρ^n` form with explicit ρ) for an explicit ρ < 1. Real arithmetic only, fixed integer delay d (production d = 50). **Out of scope:** variable delays, the continuous Halanay lemma, any application to AIEFS dynamics. Application would be a later, separately audited item at dependency-chain step 8.
- **Deliverable / branch:** `research/h13-discrete-halanay`; new `lean/AIEFGateCore/AIEFGateCore/DiscreteHalanay.lean` (or a new project `lean/AIEFDelayCore` if the seats prefer isolation, which then needs a CI job row, an owner decision), plus a SPEC section.
- **Author:** Auditor Seat 002 (with H9 context). **Auditor:** Researcher 001.
- **Red team:** a Lean counterexample showing the hypothesis is needed: at a + b = 1 the constant sequence does not decay, so `¬` the conclusion is proved. Mutation entries for a + b ≤ 1 and for dropping nonnegativity. A Python exact-Fraction check of ρ on sample sequences.
- **Novelty:** a literature check is required before calling it original. Discrete Halanay statements exist on paper (e.g. JIA 2009); the claim is only "first in Lean as far as searched".
- **Effort:** med–high. **Order:** after H9. **Cutoff-safe:** yes (new module; no ledger row until the owner agrees).
- **Owner decision:** registry/claims wording if it is ever added to the ledger, and a new Lean project, if chosen.

### H14. LeanForControl / LeanCert evaluation (gated on the toolchain decision)
- **Goal:** an evaluation report only. Does the LeanForControl discrete-time Lyapunov API (`globallyExponentiallyStable_of_lyapunov`, L583) fit the history-buffer lift of the delayed map? Can LeanCert in `trust := kernel` mode certify 0.454286, 3/7 and DelayRoots bounds within CI time? Builds happen in a scratch dir under `unshare -rn`, outside the repo.
- **Deliverable / branch:** `research/h14-toolchain-eval`; `research/toolchain_eval/REPORT.md` with build logs (no gh logs or secrets), the axiom output for each certified fact, and timing.
- **Author:** Researcher 001. **Auditor:** Auditor Seat 002.
- **Red team:** LeanCert must *fail* on a false threshold (0.40 and 0.50 in place of 0.454286). Grep CI's forbidden-marker step against a LeanCert proof in default (native) mode: the step must flag it. If it does not, that is a GAP, to be reported as a finding.
- **Effort:** med (eval); high if adoption follows. **Order:** last; only after the owner's toolchain decision. **Cutoff-safe:** yes (report only).
- **Owner decisions:** (1) **Lean toolchain bump v4.33.1 → v4.36.0** (both repos target 4.36), or vendor statements only; (2) **LeanCert native_decide risk**, i.e. whether a project-wide `leancert.trust "kernel"` pin plus a CI check is acceptable; (3) the extra `Architect` dependency for LeanForControl.

### H15. LeanPool / kuramoto-lean reuse decision (only if H12 shows value)
- **Goal:** decide between citing only, vendoring specific Apache-2.0 / MIT declarations with attribution headers and a NOTICE, or porting them.
- **Deliverable:** a decision record in the briefing; no code until the owner decides.
- **Author:** Researcher 001. **Auditor:** Auditor Seat 002. **Effort:** low (decision) / high (port). **Owner decision:** **licensing and attribution for vendoring Apache-2.0 LeanPool code**, plus the toolchain question from H14.

## Sequence
1. **No owner decision beyond the usage go-ahead:** H8 → H9 ∥ (H10 via the stdlib fallback) → H12 → H13.
2. **Wait on the owner:** H10 with Hypothesis; H11 (python-flint/mpmath); H14 (toolchain bump, LeanCert trust mode, Architect); H15 (vendoring/attribution); H13's new-project or ledger options.
3. All items are cutoff-safe as scoped. None changes `registry/claims.csv`, ERRATA, or pinned files without a separate owner decision.

## Owner decisions needed (summary)
- [ ] Usage go-ahead for implementation (currently past the 50% soft stop; reset Fri 2026-11-27 12:02 PM MST).
- [ ] Hypothesis (MPL-2.0) as a dev dependency (H10).
- [ ] python-flint (MIT/LGPL-3.0) or mpmath as a dev dependency (H11).
- [ ] Lean toolchain v4.33.1 → v4.36.0, or statements-only vendoring (H14/H15).
- [ ] LeanCert in kernel-trust mode only, plus a CI guard against native_decide (H14).
- [ ] Vendoring/attribution of Apache-2.0 LeanPool and MIT kuramoto-lean code (H15).
- [ ] Any ledger row or claims wording from H9/H13 results.

## For Auditor Seat 002
Please mark each item AGREE / CHANGE / DROP, and say whether you accept the proposed author/auditor split (you author H9, H11, H13; Researcher 001 authors H8, H10, H12, H14, H15).
