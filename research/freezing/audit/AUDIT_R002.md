# AUDIT_R002: copy of the Auditor Seat 002 audit of the freezing research (§2 only)

**What this is.** A copy of the freezing section (§2) of the read-only audit by **Auditor Seat 002**, dated
**2026-10-28** (America/Toronto). Copied into the repo on 2026-10-29 so that the audit the ledger rows cite is
committed. The other sections of that audit (§1, a separate Lean incidence-rank project; §3, a repo wording scan
about K12) are not about freezing and are omitted. The text below is verbatim except that local filesystem paths
and the auditor's identity line were removed; nothing in the findings was changed.

**What it audited.**

* The freezing research note (REPORT.md, `freeze_check.py`, FreezeCore.lean) as an **uncommitted scratch
  directory**, before it entered the repo. Its R1-R3 required fixes were applied before the research was committed
  as `research/freezing/` in commit `2672698` (see REPORT.md §9). Line references such as "L12" or "L201" refer to
  that pre-fix scratch REPORT.md, not to the committed file.
* Repo revisions read: branch `work/post-push-1` at `0493f26` (`0493f26c2670…`; a local commit, not an ancestor
  of this branch) and `origin/main` at `853498f` (`853498f2861f…`). The engine
  `aief_experiment_engine_v1.py` (sha256 `ca4593fd…`) is identical on both.
* The `scripts/`, `logs/` and `lean_kn/AuditCheck/` files it cites are the auditor's own working files. They are
  **not in the repo**.

**Not covered.** This audit predates the 2026-10-29 revision of Corollary 4 (REPORT.md §3, §9 "Ext-026"). Its
verdict that Cor 4 is correct refers to the *old* proof, which an external review (Researcher 026, Arena AI) later
found to have a gap. The revised Corollary 4 has **not** been independently re-audited.

---

## 2. freezing — conditional finite-time support-freezing (REPORT.md, FreezeCore.lean)

**Verdict: SOUND WITH WORDING FIXES.** The mathematics (Lemma 1, Thms 2–3, Cor 4) is correct in real arithmetic, and
the re-implementation is the engine. Three required fixes concern float transfer, the stated Thm 3 coverage, and
counts.

### 2(i) λ bracketing (Lemma 1), derived independently from the engine

Engine source: `aief_experiment_engine_v1.py::advance_state` (:755–845), identical on main and the branch, sha
ca4593fd…. The step it performs:

  Ũ = sym(max(0, B + dt((η+μ)R − μ − γB))), with the diagonal set to 0.

  If min_i(a − q·s_i) < δ, where s_i = Σ_j Ũ_ij:
  λ_i = min(1, c/(s_i+ε)) and B⁺ = Ũ ∘ min.outer(λ, λ); otherwise B⁺ = Ũ.

Per edge, B + dt(…) = (1−h)B + h·u with h = γ·dt and u = ((η+μ)R − μ)/γ. This is exact algebra; numerically the two
forms differ by ≤ 1.1e-16. Symmetrisation is a bitwise no-op because B and R are symmetric.

My derivation:

(a) Row sums after the gate.
* Gate active: Σ_j Ũ_ij·min(λ_i,λ_j) ≤ λ_i·s_i = c·s_i/(s_i+ε) < c whenever λ_i < 1. When λ_i = 1 we have
  s_i ≤ c − ε.
* Gate inactive: a − q·s_i ≥ δ ⇔ s_i ≤ c.

(b) Pre-gate row-sum bound. max(0, (1−h)B + hu) ≤ (1−h)B + h·u⁺ because B ≥ 0. Summing and using (a) for the incoming
B gives s_i ≤ (1−h)c + h·S_i, where S_i = Σ_j u_ij⁺ **at the same step**. The report's "s^{n+1} vs S(n)" indexing
refers to the step that produces B(n+1), so it is consistent but easy to misread.

(c) Bracket on the gate factor.
* Lower bound: λ_i ≥ min(1, c/(s_i+ε)) ≥ min(1, c/((1−h)c + hS_i + ε)) in both branches.
* Upper bound: λ_i ≤ min(1, c/s_i) in both branches.

So the bracket is gate-state independent, as claimed. The edge factor is the min over endpoints, which gives
1/g_e ≤ λ_e ≤ min(1, c/s_i, c/s_j).

Empirical check on the **engine's own trajectory**, not the re-implementation (`scripts/engine_lemma1.py`,
`logs/engine_lemma1_80000.{log,json}`). Setup: 3 seeds × 80,000 steps; the gate is active on ~77.8k of the 80k
steps. Results:
* Row-sum excess max(Σ_j B⁺ − c) = −9.97e-13. Row sums sit at c − ε·c/(c+ε).
* Lemma 1(b) slack ≥ +9.97e-13.
* λ lower-bound slack and upper-bound slack: min 0.0 (attained at λ = 1). There were no negative values.
* Per-edge form mismatch ≤ 1.1e-16.

Thms 2/3 recurrences: I checked the N formulas:
* N_off: ceil gives (1−h)^N(x_T − U⁺) ≤ B_c − U⁺.
* N_on: floor + 1 gives a strict inequality.
* Gated-OFF: valid for k ≥ N1 because the ON lower bound is monotone in k.

The FreezeCore ON fixed point κhL/(1−κ(1−h)) with κ = 1/g equals the report's x* = hL/(g − 1 + h), algebraically.

### 2(ii) Engine gate test `a − q·s < δ` vs the paper's `s > c` (ties, near-boundary)

* The float constants give c = 0.6333333333333333, which is 2.8e-17 below the exact rational (a−δ)/q.
  fl(a − q·c) − δ = +4.2e-17, so at s = c the gate does not fire.
* I scanned every float within ±40 ulp of c, plus 200,000 random s within 1e-14 relative of c. In all cases the float
  test agrees exactly with s > (a−δ)/q (exact rational) (`logs/gate_ties.log`). Over the 3 × 80k engine steps there
  were 0 steps where the float gate and the exact test disagreed, and 0 steps with any row sum within 1e-12 of c.
* Consequence: the test choice does not matter. Inside (c−ε, c] the factor is in [c/(c+ε), 1], so either branch
  satisfies the bracket in (c). The report's "can disagree by about 1 ulp" is conservative.
* **What does matter (not in the report): rounding in the B update itself.** Each step adds ~1 ulp(B) ≈ 1e-17 of
  rounding. Dividing by h, that shifts the float fixed point by ~1e-13 relative to the real-arithmetic one.

  Adversarial check (`scripts/adversarial.py off_tight`): single edge, B driven to c, then R held so that
  U⁺ = B_c − 1.0e-13.
  * The implemented certificate issues OFF with N = 195,086 (T = 20,000).
  * The float engine map's last status change came 492 steps **after** the predicted freeze (215,578 vs 215,086).
  * The float B settles at B_c − 5.4e-14, not at U⁺.

  This is a **violation of the implemented certificate on float64**. The real-arithmetic theorem is unaffected.

  Controls: at margins 1e-3, 1e-6 and 1e-10 there are no violations, and the bound is tight to within a few steps.
  At margin 0 (U⁺ = B_c + 2e-16) the certificate correctly issues ON.

### 2(iii) Overstatements

| Report wording | Finding | Class |
|---|---|---|
| L201 "requires … relative spread of about 1e-3 or less"; L189 / §7 "Locked group too large (7 or more) … pushes all their weights below the threshold" | For k = 7 the Thm 3 certificate needs an R spread of ≲ 2e-4 (`adv_clique7`). With i.i.d. R ∈ [1−w, 1] on a 7-clique, it is issued at w ≤ 2e-4 and **not** at w ≥ 3e-4, even though the group stays OFF (B ≈ c/6 = 0.10556, margin 0.0144). Analytic limit at R ≈ 1: U/u_min − 1 < ~4.6e-4, i.e. an R spread of ~2.6e-4. κ uses the lower drive and f_u the upper drive, which nearly cancel. "Covers groups ≥ 7" is true of the limit (c/(k−1) < B_c) but not of the certificate unless the band is very tight; k = 12 is the only tested gated case (stress run). | **Required wording fix** |
| L12 "0 violations over ~1,450 certified (run, T) pairs" | The run_log sum is **1,412**: 140+139+140+141+131+140+123+146+123+3×63. "Certified" means hypotheses evaluated on the finite window [T, 80000), which is stated only under "Honest limits". | **Required wording fix** (number; qualify "certified" in the headline) |
| §4 table "reset B := B_init at step 48000" | The code sets B := 0 (`simulate`, `reset_B_at`; the code comment also says B := 0). | **Required wording fix** |
| §3.6 "Lemma 1 survives with c(1+O(1e-16)) … negligible" | True for the gate, but it omits update rounding, which matters at margins ≲ 1e-13 (2(ii)). The repo runs' margins (≥ 6.7e-3) are safe. | **Required**: add the update-rounding caveat and a numeric margin guard (e.g. require margins ≥ 1e-9) in `certificate`, or state that N is for the real map only |
| L100 / L242 "reproduces the repo engine exactly" | Confirmed and extended: max\|ΔB\| = 0.0 over 80,000 steps for 3 seeds (the report showed 3,000 steps, 1 seed). Same expressions, order, history handling (the engine pops only when len > D+1, but the initial length is D+1, so this is equivalent) and RNG (SeedSequence(seed).spawn(2)[0] = `make_prefix_rng`). The variants are **not** engine modes: no-delay, random ω (α from T_* = 25/mean ω, while the engine uses the config `T_window`), reset, and exogenous R. | Non-blocking (say "exact on the default engine path") |
| "PROVEN" labels | These are paper proofs. Lean covers only the scalar/per-edge core; Lemma 1 and Thm 3 are not in Lean (the report says so in L14 and §6). | Non-blocking |
| "explicit N" | Explicit on paper and in code. The Lean statements are existential ∃N (the report says so in §6). The N depend on sup/inf of R over the infinite future, so they are not observable at T. | Non-blocking |
| Novelty L15 / L317 | Hedged ("plausible but narrow", "not new mathematics"). I did not re-run the literature search. | Non-blocking |

### Re-implementation = engine
I diffed the logic line by line (summarised in the 2(iii) table) and checked it bit-for-bit
(`logs/engine_lemma1_*.json`: crosscheck_maxabs = 0.0 for every seed).

### Numerics spot-check (`logs/adv_*.log`)
* **Re-runs** reproduce run_log.txt exactly:
  * seed 1 repo ω: first certified T 9500, last change 8695, 140 T, 0 violations.
  * reset@48000: T 48000, predicted 48938, observed 48308.
  * no-delay: T 9500, last change 8457.
* **Near-margin ON, 6-clique** (`adv_clique6_on`):
  * R spread 0.03 gives fp − B_c = +2.7e-4. The ON certificate is issued (N = 0) and holds; min B after T = 0.12645.
  * At spread ≥ 0.035, fp < B_c and the certificate stays silent although the edges remain ON. This is conservative,
    with no false ON.
* **Near-margin gated-OFF, 7-clique**: see the 2(iii) table; there are no false certificates.
* **Float-margin OFF**: one violation at a 1e-13 margin; see 2(ii).

### FreezeCore.lean (checked as in §1)
* No forbidden tokens.
* Built in my copy (`lean_kn/AuditCheck/FreezeCore.lean`, `import Mathlib`): success, 8707 jobs.
* `#print axioms` on upper_geom, eventually_off, eventually_on, edge_eventually_off and edge_eventually_on gives
  [propext, Classical.choice, Quot.sound] for each (`logs/freezecore_lean.log`).
* The statements match the report's per-edge OFF/ON claims:
  * OFF: λ ∈ [0, 1], u ≤ U, 0 ≤ U < B_c, B0 ≥ 0 ⇒ ∃N ∀n ≥ N, B n < B_c.
  * ON: κ ≤ λ, 0 < κ ≤ 1, L ≤ u, 0 ≤ L, B_c < κhL/(1−κ(1−h)) ⇒ ∃N ∀n ≥ N, B_c < B n. This equals the report's x*
    form.
  * Both conclusions are strict, which is slightly stronger than the report's ≤ for OFF.
  * Not formalised: the gate (Lemma 1), Thm 3, explicit N, and the link from λ to the engine gate.
* Non-blocking: 5+ mathlib-style whitespace lint warnings (`(n+1)`). `check.sh` points at the research lean_kn
  `.lake`; I built against my copy instead.

Required fixes (§2)
1. Thm 3 / §7 wording: state the band actually needed (k = 7: R spread ≲ 2e-4). "≥ 7 locked groups" holds in the
   limit and needs a tight band for the certificate.
2. Float transfer: add the update-rounding caveat. The theorem is for real arithmetic. Either guard margins in
   `certificate` (≥ ~1e-9) or state that the N bound is for the real map; a 1e-13 margin gives a float violation.
3. Counts/wording: 1,412 rather than ~1,450; reset B := 0 rather than B_init; qualify "certified" as finite-window in
   the headline.
