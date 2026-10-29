# Finite-time support freezing in the discrete AIEF model

**Date:** 2026-10-28 (America/Toronto).
**Location:** `research/freezing/` in the AIEFS repo (copied on 2026-10-29 from a scratch directory, without the `preguard/` backups; script paths made repo-relative; see `README.md` here for the scope summary and how to re-run). The original work edited no repo file; the repo engine `aief_experiment_engine_v1.py` (repo root) is imported read-only, for the `--crosscheck` only, with `sys.dont_write_bytecode`.

## 0. Headline

* **True and PROVEN (paper proof, real arithmetic; not in Lean except the per-edge core, §6):** a *conditional* finite-time freezing theorem. Suppose that from some step T on, the coherence R_e(n) of each edge stays in a band that satisfies one of three strict, explicitly computable certificate inequalities (OFF, ON, gated-OFF; Thms 2–3). Then every edge's status `B_e > B_c` is constant for all n ≥ T + N. N is explicit (on paper and in code; paper-level only, the Lean statements are existential ∃N) and holds for the **real-arithmetic** map only (float64: see §3.6). It is explicit in the margin, h = γ·dt, the cap c = (a−δ)/q, the row-sum drive bound S_i and B(T). The proof handles the min-endpoint capacity gate *uniformly*. It never needs to know when the gate switches on or off, including late flips (Lemma 1).
* **False unconditionally** for the B-map viewed on its own. With R given externally (periodic), an edge flips forever (§3.4, numerical counterexample with 10 flips). So any freezing theorem must assume something about R. Equivalently, it must assume something about phase-locking or drift of the closed loop.
* **Open:** whether the *closed-loop* dynamics (phases + delay + EMA + gated weights) always produce R satisfying the hypotheses, i.e. a locking/drift guarantee with margin. Also open: exact ties (gated equilibrium exactly at B_c) and multistability. We prove no closed-loop locking theorem. It remains a hypothesis.
* **Numerics** (5 repo seeds plus no-delay, random-ω, near-identical-ω stress and B-reset variants):
  * Every certificate issued was an upper bound on the last observed status change. There were **0 violations** over **1,412** certified (run, T) pairs, recomputed with the float margin guard (margins ≥ 1e-9, §3.6); the count is unchanged by the guard. Here "certified" means: all 66 edges certified at T, with the hypotheses (R bands) checked only over the **finite window [T, 80000)**, not over [T, ∞).
  * The gated-OFF certificate (Thm 3) for a locked group of ≥ 7 is issued only when the R band on the group is very tight (k = 7: R spread ≲ 2e-4; §3, Thm 3).
  * The certificate is non-trivial (N > 0) in the random-ω, stress and reset runs. In the reset runs it predicted step 48938 against an observed last change at 48308.
* **Lean:** the scalar core and the per-edge OFF/ON statements, including max(0,·) clipping and an arbitrary gate factor λ ∈ [κ,1], are formalised. They compile with no `sorry` against Mathlib (Lean v4.33.1): `lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean` (repo path; separate Lake project, checked by `lean/AIEFFreezeCore/check_lean_freeze.sh`). Those Lean statements are existential (∃N); the explicit N is not in Lean. The gate row-sum lemma and the gated-OFF theorem are not yet formalised, but they look routine (§6).
* **Novelty:** the mathematical core is elementary: comparison with a scalar affine contraction. The search found no prior statement of *finite-time threshold-support freezing with an explicit bound* for adaptive/Hebbian Kuramoto networks under a capacity/normalisation gate. The closest prior work proves asymptotic convergence of weights or binary topologies, not finite-time freezing of a thresholded support. Plausibly new *as a model-specific certificate theorem*, but modest in mathematical depth. Do not oversell it.

## 1. The exact recurrence (code citations)

### 1.1 Engine and constants

Primary engine: `aief_experiment_engine_v1.py` (repo root; sha256 ca4593fd…, the file the line citations below refer to).

Constants (`:63-80`):

| Symbol | Value |
|---|---|
| N | 12 |
| dt | 0.01 |
| τ | 0.5 |
| ω | [1.00, 1.02, 1.50, 2.00, 2.01, 1.01, 1.03, 1.51, 2.02, 2.00, 1.00, 1.04] |
| a | 1 |
| q | 1.5 |
| δ | 0.05 |
| η | 0.04 |
| γ | 0.015 |
| μ | 0.03 |
| B_c | 0.12 |
| B_init_scale | 5e-4 |
| ε (`scale_epsilon`, `:148`) | 1e-12 |
| D = τ/dt | 50 delay steps (`:172`, `:232-235`) |

Derived quantities:

* α = exp(−dt/T_w) (`:162-164`), with T_w = 25/mean(ω) = 17.5029.
* Capacity c = (a−δ)/q = 0.63333 (`:167-169`).

**Initialisation (`:696-711`):**

* θ⁰ ~ U[0,2π).
* B⁰ = sym(5e-4·U[0,1]), diagonal 0.
* z⁰ = 0.
* The history buffer holds D+1 copies of θ⁰.

### 1.2 One step n → n+1 (`advance_state`, `:755-845`)

1. **Coherence** (`compute_R`, `:721-752`):

   z_ij ← α z_ij + (1−α) exp(i(θ_i^n − θ_j^{n−D} − (ω_i+ω_j)τ/2)),

   R_ij = (|z_ij| + |z_ji|)/2, R_ii = 0.

   So R is the modulus of a complex EMA. R ∈ [0,1], and R → 1 for any frequency-locked pair whatever its phase offset.

2. **Pre-gate weights** (`:790-797`):

   Ũ = sym(max(0, B + dt((η+μ)R − μ − γB))), diagonal 0.

3. **Gate** (`:803-814`): s_i = Σ_j Ũ_ij. The gate is active iff min_i(a − q s_i) < δ, i.e. (in real arithmetic) some s_i > c.

   * If active: λ_i = min(1, c/(s_i+ε)) and B⁺_ij = Ũ_ij · min(λ_i, λ_j) (min-endpoint scaling).
   * Otherwise: B⁺ = Ũ.

   A post-check raises if min(a − q·rowsum) < δ − 1e-9 (`:824-828`).

4. **Phases** (`:830-839`), using the *new* B⁺:

   θ ← mod(θ + dt(ω + Σ_j B⁺_ij sin(θ_j^{n−D} − θ_i)), 2π).

   The history is then pushed (`:841-844`).

5. **Status:** edge e = {i,j} is ON iff B_e > B_c.

### 1.3 Other engines and the audit

**AIEF-1.3 engine** (`AIEF_1_3_falsification_updated.py`): same law.

* `compute_R` `:350-363`
* symmetrisation `:421-422`
* B update `:432-435`
* gate `:440-448`
* status accumulator `P_sum += B > B_C` `:472`

**AIEF-1.4 memory-ablation engine** (`AIEF_1_4_memory_ablation_updated.py`): same law.

* `compute_R` `:410-419`
* B update `:443-445`
* outer-min gate `:455`
* θ update `:473`

My re-implementation `freeze_check.py::simulate` (`:26-53`) is **exact on the default engine path**: max|B_mine − B_engine| = **0.0** over 3000 steps, 1 seed (`python3 freeze_check.py --crosscheck`); the independent audit extended this to 0.0 over 80,000 steps for 3 seeds. The variants used in §4 (no delay, random ω with α from T_w = 25/mean ω, the B reset, exogenous R) are **not** engine modes; they are modifications of the re-implementation.

### 1.4 Edge-wise reformulation

Let h = γ·dt = 1.5e-4 and define the drive

u_e(n) := ((η+μ)R_e(n) − μ)/γ ∈ [−2, η/γ = 2.667].

Then **B_e⁺ = λ_e(n) · max(0, (1−h)B_e + h u_e(n))**, with λ_e = min(λ_i, λ_j) ∈ (0,1] and λ ≡ 1 when the gate is inactive.

Useful values:

* B* = 0 at R = μ/(η+μ) = 3/7.
* Ungated ON threshold: R_c = (μ + γB_c)/(η+μ) = 0.454286.

## 2. Fixed points and invariant sets

**Invariant sets.** The following hold unconditionally:

* B ≥ 0 and symmetric.
* Post-gate row sums are ≤ c (Lemma 1), so 0 ≤ B_e ≤ c.
* An edge with B_e = 0 and u_e ≤ 0 stays at exactly 0.

**Constant R (frozen drive).**

* *Ungated:* B_e → u_e⁺ = max(0, u_e).
* *Gated:* a node with drive sum S_i = Σ_j u_ij⁺ > c is scaled. For a locked k-clique (R ≡ 1, u = η/γ), the symmetric gated fixed point solves x = λ((1−h)x + h u), with λ = c/((k−1)((1−h)x + h u)) when active. So x = c/(k−1) − O(ε).

| Locked clique | Neighbours | Gated fixed point c/(k−1) | Status |
|---|---|---|---|
| k = 3 | 2 | 0.317 | ON |
| k = 6 (the repo ω cluster) | 5 | 0.12667 | ON, margin only 0.0067 |
| k = 7 | 6 | 0.10556 | **OFF** |
| k = 12 | 11 | 0.05758 | OFF |

So the gate can switch *off* every edge of a fully locked large clique, a "too many friends" effect. Thm 3 addresses this case, but its certificate is only issued when the R band on the clique is very tight (k = 7: R spread ≲ 2e-4); see the remark after Thm 3. In the limit (c/(k−1) < B_c) all k ≥ 7 are OFF.

* *General gated equilibria* (mixed cliques) give a proportional share x_e ≈ min(u_e, c·u_e/S_i) (a multiplicative-normalisation share; compare Miller–MacKay 1994, §5).

**Finite time is not automatic.** All of these are only *asymptotic* limits. Freezing in finite time needs a strict margin between the limit and B_c. Exact ties (limit = B_c) can give infinitely many crossings in principle. They are non-generic and excluded below.

## 3. Theorems

Notation:

* Each edge e = {i,j} has the scalar sequence x_n = B_e(n).
* For a window [T,∞) let U⁺_e = max(0, sup_{n≥T} u_e(n)), u^min_e = inf_{n≥T} u_e(n), and S_i⁺ = sup_{n≥T} Σ_j u_ij(n)⁺.
* All statements are in real arithmetic; see §3.6 for floating point.

### Lemma 1 (gate sandwich): PROVEN (paper proof; not in Lean), unconditional

For every n ≥ 1 and every node i:

(a) Σ_j B⁺_ij ≤ c, hence B_e ≤ c.

(b) s_i^{n+1} ≤ (1−h)c + h S_i(n), where S_i(n) = Σ_j u_ij(n)⁺.

(c) min(1, c/((1−h)c + hS_i(n) + ε)) ≤ λ_i ≤ min(1, c/s_i). This also holds when the gate is inactive, with λ_i = 1.

Hence the edge factor satisfies 1/g_e ≤ λ_e ≤ min(1, c/s_i, c/s_j), where g_e := max(1, max_{k∈e}((1−h)c + hS_k⁺ + ε)/c).

*Proof.*

(a) If the gate is active: Σ_j Ũ_ij min(λ_i,λ_j) ≤ λ_i s_i = min(1, c/(s_i+ε)) s_i ≤ c. If it is inactive: a − q s_i ≥ δ for all i, i.e. s_i ≤ c, and B⁺ = Ũ. At n = 0, row sums are ≤ 11·5e-4 < c.

(b) max(0, (1−h)B + hu) ≤ (1−h)B + h u⁺ because B ≥ 0. Sum over j and use (a) at the previous step.

(c) The lower bound follows from λ_i = min(1, c/(s_i+ε)) and (b). The upper bound is immediate; in the inactive case s_i ≤ c, so min(1, c/s_i) = 1 = λ_i. ∎

The point of Lemma 1 is that it brackets the gate factor by drive quantities alone, at every step. The proofs below therefore never track *when* the gate is active, and late gate flips are harmless.

### Theorem 2 (OFF and ON certificates): PROVEN (paper proof; the per-edge ∃N form is in Lean, the explicit N is paper-level only), conditional on R on [T,∞)

**(OFF; gate-independent.)** If U⁺_e < B_c, then B_e(n) ≤ B_c for all n ≥ T + N_off, where

N_off = 0 if x_T ≤ B_c, else ⌈ ln((x_T − U⁺)/(B_c − U⁺)) / (−ln(1−h)) ⌉.

If moreover u_e ≤ −m < 0 on [T,∞), then B_e reaches **exactly 0** by step T + ⌈ln((1−h)c/(hm)) / (−ln(1−h))⌉ + 1 at the latest (x_{T+k} ≤ (1−h)^k c, and the clip fires as soon as (1−h)x ≤ hm). It stays at exactly 0, so the edge is exactly decoupled.

*Proof.* x⁺ ≤ 1 · max(0, (1−h)x + h u) ≤ (1−h)x + hU⁺, using x, U⁺ ≥ 0 and λ ≤ 1. Induction gives x_{T+k} − U⁺ ≤ (1−h)^k (x_T − U⁺). Solve (1−h)^k (x_T − U⁺) ≤ B_c − U⁺. For the exact-zero claim: x_{T+k} ≤ (1−h)^k c by the same induction with u ≤ 0, and the clip fires once (1−h)x ≤ hm. ∎

**(ON.)** Suppose u^min_e > 0. Let ρ_e = (1−h)/g_e and x*_e = h u^min_e/(g_e − 1 + h). If x*_e > B_c, then B_e(n) > B_c for all n ≥ T + N_on, where

N_on = 0 if r := (x* − x_T)/(x* − B_c) < 1, else ⌊ln r / ln(1/ρ)⌋ + 1.

*Proof.* By Lemma 1(c), x⁺ ≥ (1/g)((1−h)x + h u^min). The comparison sequence y_{k+1} = ρ y_k + h u^min/g has fixed point x*. Induction gives x_{T+k} ≥ x* − ρ^k (x* − x_T), which is non-decreasing in k, and the last inequality is solved for k. ∎

Interpretation: x* ≈ min(u, c·u/(S⁺ + ε/h)), the worst-case proportional share of the cap.

### Theorem 3 (gated-OFF certificate for large locked cliques): PROVEN (paper proof; not in Lean), conditional on R on [T,∞)

Fix N1 ≥ 0. For each edge f with u^min_f > 0, set ℓ_f := max(0, x*_f − ρ_f^{N1}(x*_f − x_T,f)⁺), and ℓ_f := 0 otherwise.

* By the proof of Thm 2 (ON), B_f(n) ≥ ℓ_f for n ≥ T + N1.
* Let σ_i := Σ_j max(0, (1−h)ℓ_ij + h u^min_ij) and κ_e := min(1, c/σ_i, c/σ_j).
* Let f_u := κ h U⁺/(1 − κ(1−h)).

If κ(1−h) < 1 and f_u < B_c, then B_e(n) ≤ B_c for all n ≥ T + N1 + ⌈ ln((c − f_u)/(B_c − f_u)) / ln(1/(κ(1−h))) ⌉.

*Proof.* For n ≥ T + N1 we have s_i ≥ σ_i, because Ũ is monotone in B and in u. Lemma 1(c) then gives λ_e ≤ κ_e. Hence x⁺ ≤ κ((1−h)x + hU⁺), a contraction with factor κ(1−h) and fixed point f_u. Start from the a-priori bound x ≤ c (Lemma 1(a)) and iterate. ∎

The code (`freeze_check.py::certificate`, `:55-96`) searches N1 ∈ {0, 1e3, 2e3, 4e3, …, 6.4e4} and takes the minimum. It can certify locked k = 7 and k = 12 cliques, but **only under a very tight R band** on the clique, because κ uses the *lower* drive while f_u uses the *upper* drive and the two nearly cancel. For k = 7 the required R spread is **≲ 2e-4**, not ~1e-3: with i.i.d. R ∈ [1−w, 1] on a 7-clique (`clique7_check.py`, T = 20000, 60000 steps) the certificate is issued for w ≤ 2e-4 (N ≈ 950–1370) and **not** for w ≥ 3e-4 (tested 3e-4, 5e-4, 1e-3), even though the group stays OFF (B ≈ c/6 = 0.10556, margin ≈ 0.0144). The audit's analytic limit at R ≈ 1 is U/u_min − 1 ≲ 4.6e-4, i.e. an R spread of ≈ 2.6e-4. So "groups of ≥ 7 are covered" holds for the limit (c/(k−1) < B_c) but for the certificate only when the band is that tight. k = 12 is the only tested gated case from the closed loop (stress run). Outside the tight band the certificate stays silent (conservative; no false certificate was observed).

### Corollary 4 (limit form): PROVEN (paper proof; not in Lean)

Let R̄_e = limsup R_e and R_e = liminf R_e. Suppose every edge satisfies one of the Thm 2/3 inequalities *strictly* when U⁺, u^min and S⁺ are replaced by their limsup/liminf values. Then the support B > B_c is eventually constant.

*Proof.* The inequalities are strict and continuous in (U⁺, u^min, S⁺, ℓ). Tail sups and infs converge to limsup and liminf, so some finite T satisfies them; apply Thms 2–3. ∎

Special cases:

* (i) Every edge's R converges, and no limit lies in the "undecided" band.
* (ii) Frequency-locked clusters (R → 1) with drifting inter-cluster pairs whose limsup R < R_c, which is what is observed. In the repo runs the inter-cluster limsup over the tail is 0.148–0.209, against R_c = 0.4543.
  * Heuristic, not proven: a pair drifting at constant relative frequency Δω has |z| ≈ (1−α)/|1 − α e^{iΔω dt}| ≈ 1/(T_w|Δω|) ≈ 0.11 for Δω = 0.5.

### 3.4 An unconditional theorem is FALSE (for the weight map)

The B-map (with gate) is driven by an exogenous R that alternates between 1 for 20000 steps and 0 for 20000 steps on a triangle. Over 200000 steps edge 0–1 changes status **10 times** (Bmax = 0.3167, B returns to 0). Source: `freeze_check.py:153-160`, logged as `exogenous_periodic_R_counterexample` in `run_log.txt`.

So no theorem of the form "the gated weight dynamics freezes for every input" holds. Freezing must come from the closed loop.

Whether the *closed loop* can produce such persistent recurrent R oscillation (e.g. a cluster that repeatedly locks and unlocks) was **not** shown either way.

### 3.5 What is open (CONJECTURE / OPEN)

* **(O1) Closed-loop locking with margin.** For the repo ω and all initial θ (or almost all), the clusters {ω ≈ 1.0–1.04}, {1.50, 1.51} and {2.00–2.02} phase-lock, R_e → 1 inside clusters, and limsup R_e < R_c across clusters. This is not proven.
  * Classical results do not apply directly: Dörfler–Bullo / Chopra–Spong locking bounds (static weights, no delay); Earl–Strogatz 2003 (delay; identical oscillators; linear stability only); Ha–Noh–Park 2016 / 2018 (adaptive couplings, no delay, no gate, different law).
  * A plausible route is a perturbative argument: the gate floors the intra-cluster weight at ≈ c/(k−1) ≥ 0.1056 once it is ON, and the cluster frequency spreads are ≤ 0.04. But the delay τ = 0.5 and the pre-lock transient (when B ≈ 0) make a global statement hard.
  * Status: **conjecture**, supported by the audit (3300 + 3960 edges, 0 status differences between split and final) and the runs here.
* **(O2) Ties and the undecided band.** Edges whose limit data fall between the ON and OFF certificate thresholds (e.g. a gated share within O(ε, h·spread) of B_c) are not covered. Generically they should not occur, but this is unproven for the closed loop.
* **(O3) Multistability.** Different initial conditions give different frozen supports: 19, 22 or 25 ON edges for the 5 repo seeds. The theorem says nothing about *which* support appears.
* **(O4) A sharper, a-priori N.** Our N is computed from R on [T,∞), which is a *hypothesis*, not something observable at time T. An a-priori freeze time needs an a-priori locking time, which is (O1).

### 3.6 Caveats (floating point and implementation)

* The theorems are in real arithmetic. The implementation tests the gate as `min(a − q s) < δ`, which is not bit-identical to `s > c`. The audit found the float test agrees with the exact rational test s > (a−δ)/q on every float within ±40 ulp of c and on all engine steps, so this choice is harmless; Lemma 1 survives with c replaced by c(1 + O(1e-16)), and the engine's post-check tolerance is 1e-9.
* **Rounding in the B update itself does matter at tiny margins.** Each step adds ~1 ulp(B) ≈ 1e-17 of rounding; divided by h this shifts the float fixed point by ~1e-13 relative to the real-arithmetic one. Audit test (reproduced by `guard_check.py`, `guard_check.json`): a single edge driven to c, then R held so that U⁺ = B_c − 1e-13. The unguarded certificate issues OFF with N = 195,086 (T = 20,000, predicted freeze by 215,086), but the float64 map's last status change is at 215,578, and the float B settles at B_c − 5.4e-14, not at U⁺. That is a violation of the explicit N on float64; the real-arithmetic theorem is unaffected. **Hence the explicit N holds for the real-arithmetic map only.**
* **Fix: margin guard.** `freeze_check.py::certificate` now issues a certificate only if its margin (B_c − U⁺ for OFF, x* − B_c for ON, B_c − f_u for gated-OFF) is ≥ `MARGIN_GUARD` = 1e-9 (`guard=0.0` restores the old behaviour). With the guard, the margin 1e-13 and 1e-10 OFF cases and the margin-0 ON case are not certified (no violation); margins 1e-3 and 1e-6 are certified exactly as before, with N tight (last change = predicted step). The repo runs' margins (≥ 6.7e-3) are far above the guard, and all 1,412 certified (run, T) pairs are unchanged. The guard is an engineering bound (≈ 1e4 × the observed float shift), not a proven float error bound.
* ε = 1e-12 is included in g_e. Its effect on x* is O(ε/h) ≈ 7e-9.
* The ON margin in the repo runs is small: x* ≈ 0.126667 against B_c = 0.12, i.e. 0.0067 ≈ 5.6% of B_c, coming from the 6-cluster share c/5. A cluster of 7 would flip the limit outcome to OFF; Thm 3 certifies that only if the cluster's R spread is ≲ 2e-4.
* The status in the audit's `frozen_topology_check` compares only split vs final status (`frozen_topology_check.py:23-29`). The runs here check *every* step after T + N.

## 4. Numerical check (step 4)

**Script:** `freeze_check.py` (self-contained; exact on the default engine path, cross-checked against the engine; certificate with margin guard 1e-9, §3.6).

**Seeds:** 10431384713483787270, 10856823803646276806, 11242426753702356865, 12123519807951751650, 1230287949579537403 (from `runs/5a9f093a2fe0` file names).

**Run:** 80000 steps. At every T on a 500-step grid, compute the certificates from R on [T, 80000) and B(T). Predicted freeze = T + max_e N_e if *all* 66 edges are certified. A (run, T) pair is called **certified** when all 66 edges are certified with the hypotheses checked over the finite window [T, 80000) only. Check that no edge changes status in (T + N, 80000]. Total: **1,412 certified (run, T) pairs** (140+139+140+141+131+140+123+146+123+3×63), **0 violations**, recomputed after adding the margin guard (identical to the pre-guard run; the `preguard/` backups stayed in the scratch directory and are not in the repo).

**Outputs:** `results.json`, `run_log.txt` (guarded re-run, without `--crosscheck` so the repo engine was not imported again; the 2026-10-29 in-repo re-run with `--crosscheck` gave max|B_mine − B_engine| = 0.0 over 3000 steps and byte-identical `results.json`, see `inrepo_rerun_log.txt`); margins at T = 48000 in `margins.json` (from `margins.py`).

| Run | First certified T | Predicted freeze | Observed last change | ON edges | Certified T's | Violations |
|---|---|---|---|---|---|---|
| repo ω, delay, seed 1 | 9500 | 9500 | 8695 | 19 | 140 | 0 |
| repo ω, delay, seed 2 | 10000 | 10000 | 9166 | 22 | 139 | 0 |
| repo ω, delay, seed 3 | 9500 | 9500 | 7976 | 19 | 140 | 0 |
| repo ω, delay, seed 4 | 9000 | 9000 | 7601 | 19 | 141 | 0 |
| repo ω, delay, seed 5 | 14000 | 14000 | 13654 | 25 | 131 | 0 |
| repo ω, no delay, seed 1 | 9500 | 9500 | 8457 | 22 | 140 | 0 |
| random ω U[1,2] #0, seed 1 (21 goff edges) | 18000 | 19428 | 7944 | 6 | 123 (all N>0) | 0 |
| random ω U[1,2] #1, seed 2 | 6500 | 6500 | 6348 | 18 | 146 | 0 |
| stress ω = 1 + 0.001k (12-clique, all 66 goff) | 18000 | 19178 | 5662 | 0 | 123 (all N>0) | 0 |
| reset B := 0 at step 48000 (EMA kept), seeds 1–3 | 48000 | 48938 | 48308 | 19/22/19 | 63 each | 0 |

* The gate is active in every run: max(1 − λ) ≈ 0.003 in the repo runs and 0.0068 in the stress run.
* Margins at T = 48000 (repo seeds):
  * min ON lower bound x* = 0.1266667, against final ON-edge B = 0.1266667 (= c/5, so the bound is essentially tight).
  * All OFF edges have U⁺ = 0, with max R 0.148–0.209.
  * min ON R ≈ 1 − 1e-10; max S⁺ = 13.33 (= 5 · η/γ).
* **Counterexamples:** none for the theorem. The only "counterexample" is the intended one (§3.4): exogenous R, where the hypotheses fail.
* **Honest limits:**
  * Hypotheses are only checked on the finite window [T, 80000).
  * When all edges are certified at the first certified T, N = 0. That T is only slightly after the observed last change, so in the repo runs the bottleneck is *when R enters its final band*. The reset runs and the gated-OFF runs exercise N > 0. In the reset runs the bound held with slack of about 3× (938 predicted vs 308 observed steps after the reset). In the gated-OFF runs the last change had already happened before the first certified T (7944 and 5662 against T = 18000), so they only test that nothing flips after T + N.

## 5. Novelty search log (step 5), 2026-10-28

**arXiv API** (`https://export.arxiv.org/api/query`; the `http://` endpoint returned HTTP 500). The full log is in `arxiv_search_log.json`, produced by `arxiv_search.py` and `arxiv_search2.py`.

Queries (hits in brackets):

* `all:"adaptive Kuramoto" AND all:"finite time"` [0]
* `abs:adaptive AND abs:Kuramoto AND abs:topology AND abs:frozen` [0]
* `abs:"Hebbian" AND abs:"Kuramoto" AND abs:"normalization"` [0]
* `abs:"Hebbian" AND abs:"oscillators" AND abs:"budget"` [0]
* `abs:"adaptive couplings" AND abs:"Kuramoto" AND abs:"synchronization"` [14]: e.g. 2006.00890 *Stability of cluster formations in adaptive Kuramoto networks*; 2209.10514 *Complex dynamics in adaptive phase oscillator networks*; 1008.0333 *Adaptive Oscillator Networks with Conserved Overall Coupling* (title only checked); 2512.20410 *Metastability induced by non-reciprocal adaptive couplings*.
* `abs:"adaptive network" AND abs:"eventually constant"` [0]
* `abs:"Hebbian" AND abs:"hard bounds" AND abs:"finite time"` [0]
* `abs:"synaptic normalization" AND abs:"Hebbian" AND abs:"convergence"` [0]
* `abs:"Kuramoto" AND abs:"time delay" AND abs:"adaptive coupling"` [0]
* `abs:"ultimate positivity" AND abs:"linear recurrence"` [10]: Ouaknine–Worrell line (1309.1914, 1307.2779, 2305.04870 *Robust Positivity*, 2211.02365 *Robustness for Skolem/Positivity*).
* `abs:"eventual sign" AND abs:"recurrence" AND abs:"perturbation"` [0]
* `abs:"threshold" AND abs:"adaptive network" AND abs:"topology" AND abs:"converge" AND abs:"finite"` [1]: 0811.0980 (SOC in discrete networks; unrelated mechanism).
* `abs:Kuramoto AND abs:"adaptive" AND abs:delay AND abs:plasticity` [0]
* `abs:"phase oscillators" AND abs:"conserved" AND abs:coupling AND abs:adaptive` [1]: 1706.08070
* `abs:Hebbian AND abs:Kuramoto AND abs:"phase-locking"` [2]: 2603.08731, 2410.19156
* `abs:"adaptive coupling" AND abs:Kuramoto AND abs:"phase-locked" AND abs:"sufficient"` [1]: 1008.0333
* `abs:"multiplicative normalization" AND abs:Hebbian` [0]
* `abs:"homeostatic" AND abs:"Kuramoto"` [4] (connectome; unrelated)
* `abs:"network topology" AND abs:"finite time" AND abs:"adaptive" AND abs:synchronization` [1] (unrelated)
* `abs:"coevolution" AND abs:"phase oscillators" AND abs:"pruning"` [0]
* `abs:"Kuramoto" AND abs:"adaptive" AND abs:"capacity"` [1] (unrelated)
* `abs:"discrete-time" AND abs:"adaptive" AND abs:"Kuramoto" AND abs:"Hebbian"` [0]
* `abs:"linear recurrence" AND abs:"bounded" AND abs:"eventually" AND abs:"sign"` [1]: 2609.23839 *Eventual Nonnegativity of a Matrix Is in P*
* `abs:"STDP" AND abs:"hard bounds" AND abs:"bimodal"` [0]

**Web search** (same date):

1. "Ha Noh Park synchronization Kuramoto adaptive couplings Hebbian SIAM 2016": Ha, Noh, Park, *SIADS* 15 (2016) 162-194 (adaptive couplings, preserved incoming-coupling sum, sufficient synchronization frameworks). Also Ha et al., *SIADS* 2018 (doi 10.1137/17M1124048; conservation law, fast learning) and *The stability of fixed points for a Kuramoto model with Hebbian interactions*, Chaos (2017), doi 10.1063/1.4983524. **These give asymptotic synchronization, not finite-time support freezing, and have no delay and no min-endpoint gate.**
2. "Miller MacKay 1994 role of constraints in Hebbian learning": Neural Comput. 6:100–126. Multiplicative constraint → graded weights (principal eigenvector). Subtractive + hard bounds → weights saturate at the bounds. **The closest conceptual antecedent:** our gate is a multiplicative row-sum constraint, and our ON fixed point is the "proportional share". Their results are asymptotic and are not threshold-support freezing statements.
3. "finite time network topology becomes constant adaptive network threshold weights": the hits are *finite-time topology identification* (observer design: Wang et al. 2025, PMC12087917; KTH paper) and the Berner–Gross–Kuehn–Kurths–Yanchuk review *Adaptive dynamical networks* (arXiv 2304.05652, Phys. Rep. 2023). Different problem.
4. "Kuramoto adaptive coupling time delay plasticity": Timms & English, PRE 89, 032906 (2014) (delay + Hebbian; numerical and analytic patterns); Aoki & Aoyagi, PRL 102, 034101 (2009) (co-evolution; two-cluster, coherent and chaotic states). Neither gives finite-time freezing.
5. "edge snapping adaptive network weights converge to binary": DeLellis, di Bernardo, Garofalo, Porfiri, IEEE TCAS-I 57 (2010) (double-well edge dynamics → binary topology *asymptotically*; local stability). Also the *Chaos* 33, 013123 (2023) limited-resources edge snapping (caps the number of active edges). **Closest "topology freezes" result. It is asymptotic and local, not finite-time with an explicit bound.**
6. "Earl Strogatz 2003 delayed coupling stability criterion": PRE 67, 036204 (identical oscillators, uniform delay, linear stability).

**Assessment.**

* The sign-pattern question is trivial here. After the comparison step each edge is a *first-order* scalar affine contraction with bounded forcing, and its eventual sign relative to B_c is decided by the strict margin. The deep Skolem/Positivity literature concerns higher-order recurrences and exact (non-robust) instances, and is not needed. Its *robust* variants (2305.04870, 2211.02365) are the conceptual analogue of our "strict margin" hypothesis.
* No source found states finite-time freezing of a thresholded support, with an explicit bound, for an adaptive oscillator network under a capacity/normalisation gate.
* Novelty is plausible but narrow. The contribution is the gate-robust sandwich (Lemma 1), the two-stage gated-OFF argument (Thm 3) and the explicit N, not new mathematics.
* The search is not exhaustive: there was no full-text search, no Google Scholar, and nothing on neuromorphic/“synaptic pruning finite time” beyond the queries above.

## 6. Lean / Mathlib formalizability (step 6)

The existing repo Lean (`lean/AIEFProofs`: Basic, CompleteGraphIncidence, ControllerFiber, ControllerFiberProjector, ControllerFiberQuotient, Smoke) **does not formalise the gate**. `ControllerFiberProjector.lean:27` says it is "not the implemented AIEF admissibility / capacity projection", and README `:90-108` lists the gate, EMA and persistence as not formalised.

**Done here:** `lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean` (repo path; a separate Lake project that depends on Mathlib only, same toolchain and Mathlib pin as `lean/AIEFProofs`). It compiles with no `sorry` and 0 warnings, and its declarations use only the standard axioms (propext, Classical.choice, Quot.sound). To check it, run `lean/AIEFFreezeCore/check_lean_freeze.sh` (or the wrapper `research/freezing/lean/check.sh`). It contains:

* `upper_geom`: x_{n+1} ≤ ρx_n + β, ρ ∈ [0,1) ⇒ x_n − β/(1−ρ) ≤ ρ^n (x_0 − β/(1−ρ)).
* `eventually_off` / `eventually_on`: strict margin ⇒ ∃N, ∀n ≥ N, x_n < B_c (resp. > B_c).
* `edge_eventually_off`: B_{n+1} = λ_n · max 0 ((1−h)B_n + h u_n), λ_n ∈ [0,1], u_n ≤ U < B_c ⇒ eventually B_n < B_c. This is gate-independent.
* `edge_eventually_on`: the same recurrence with κ ≤ λ_n and L ≤ u_n, κhL/(1−κ(1−h)) > B_c ⇒ eventually B_n > B_c.

Not yet formalised (estimated effort in brackets):

* Lemma 1 for `Fin 12` matrices (row sums under `min`-endpoint scaling, ~100–200 lines; Finset sums).
* Thm 3 composition (routine once Lemma 1 exists).
* The explicit-N versions (replace `exists_pow_lt_of_lt_one` by `Real.log` bounds; straightforward).
* Anything about phases, delay or the EMA (O1). This is not formalisable until it is proven on paper.

A suggested top-level statement is: ∀ trajectory of the exact real-arithmetic step map, if ∃T such that the tail bands of R satisfy the certificate predicate, then ∃N, ∀n ≥ T+N, status(n) = status(T+N).

## 7. Plain-language summary

The edge weights in AIEF behave like leaky buckets: each step they leak a fraction h = 0.00015 and are refilled according to how coherent the two oscillators are. A shared capacity rule (the gate) shrinks a node's buckets whenever its total gets too large.

We proved the following:

* **Persistently incoherent pair:** if, from some time on, a pair stays clearly incoherent, its weight drains below the threshold within a computable number of steps and stays there.
* **Persistently coherent pair:** if it stays clearly coherent and its guaranteed share of the node's capacity is above the threshold, it rises above the threshold and stays there.
* **Locked group too large:** if too many oscillators lock together (7 or more here), the capacity rule pushes all their weights *below* the threshold in the long run. Our finite-time certificate for this case only applies when the group's coherence is extremely steady (for 7 oscillators, fluctuations of about 2e-4 or less); otherwise the group still stays below the threshold in simulation, but we do not certify it.

These arguments work no matter when the capacity rule switches on or off. So "the network topology stops changing after a finite time" is a theorem, *provided* the oscillators settle into a stable pattern of locking and drifting with a clear margin.

What we cannot prove is that the oscillators always do settle like that. Feeding the weight rule an artificial, ever-changing coherence signal makes edges flip forever, so this is a real assumption, not a technicality.

In every simulation we ran (1,412 certified checks over the simulated window), the predicted freeze time was never violated. The explicit freeze time is a statement about exact arithmetic; for margins below about 1e-9 computer rounding can break it, so the checker refuses to certify such cases. The 6-oscillator group in the default setup sits only about 5% above the threshold, so that result is robust but not by a wide margin.

## 8. File index

* `freeze_check.py`: simulator, certificates (Thm 2/3), checks, exogenous counterexample; `--crosscheck` against the repo engine.
* `results.json`, `run_log.txt`: numerical results (re-run with the margin guard; the pre-guard copies were kept in the scratch directory and are not in the repo).
* `guard_check.py`, `guard_check.json`, `guard_check_log.txt`: float-margin OFF/ON test, unguarded vs guarded (audit fix R2).
* `clique7_check.py`, `clique7_check.json`, `clique7_check_log.txt`: 7-clique R-spread test of the Thm 3 certificate (audit fix R1).
* `margins.py`, `margins.json`: margins at T = 48000.
* `arxiv_search.py`, `arxiv_search2.py`, `arxiv_search_log.json`: arXiv query log.
* `lean/check.sh`: wrapper that runs `lean/AIEFFreezeCore/check_lean_freeze.sh`; the Lean formalisation of the scalar and per-edge core is `lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean` (repo paths).
* `inrepo_rerun_log.txt`: 2026-10-29 in-repo re-run (engine cross-check and byte-identical outputs).

## 9. Audit fixes applied (2026-10-28, from the read-only audit of this work, §2; that audit file is not in the repo)

* **R1 (gated-OFF band):** the Thm 3 certificate for a locked group of ≥ 7 needs an R spread ≲ 2e-4 (k = 7), not ~1e-3; at 3e-4 it is not issued although the group stays OFF. Reproduced in `clique7_check.py`. Qualified in §0, §2, the Thm 3 remark, §3.6 and §7: "≥ 7 covered" holds in the limit, and for the certificate only under that tight band.
* **R2 (float rounding):** added `MARGIN_GUARD = 1e-9` to `freeze_check.py::certificate` (OFF, ON and gated-OFF margins). Stated that the explicit N holds for the real-arithmetic map only, with the 1e-13 counterexample (predicted 215,086, last flip 215,578) in §3.6. `guard_check.py`: with the guard, 0 violations (the 1e-13, 1e-10 and margin-0 cases are no longer certified). The main run was re-run with the guard: 1,412 certified pairs, 0 violations, identical results.
* **R3 (counts/wording):** "~1,450" → **1,412** certified (run, T) pairs; "certified" is defined in §0 and §4 as checked over the finite window [T, 80000); reset row corrected to B := 0 (not B_init).
* **Non-blocking:** re-implementation described as "exact on the default engine path" (variants are not engine modes; audit cross-check of 80k steps × 3 seeds cited); proof labels changed to "PROVEN (paper proof)" with the Lean coverage stated; explicit N marked as paper-level only (Lean has ∃N); gate-test caveat updated with the audit's tie scan.
* Not changed: the theorems, proofs, Lean files, novelty assessment and other content.

