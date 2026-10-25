# AIEFS audit: response 3 (round-4 adjudication ledger)

Status: **current** (2026-10-25). This ledger answers the round-4 collaborator reviews of the published tree at `dc0250a`. It is authoritative over `AIEFS_audit_response_2.md`, `AIEFS_audit_response.md`, `AIEFS_salvage.md` and `AIEFS_audit.md`. Where those files disagree with this one, this file wins. The affected passages carry dated inline notes of the form "[Correction 2026-10-25, response-3 #N: …]".
Audited repository: github.com/jacobbrainard84-knightninja/AIEFS. Simulation inputs are unchanged from rounds 1–3 (code and data at `e47bad1`; input hashes in `evidence/audit_manifest.json`).
Round-4 status: everything here was prepared locally on top of `dc0250a`. It is **not** committed or pushed yet; publication needs the owner's approval.
Tags: **[RAN]** executed for this response; **[READ]** read in the repo or our own files; **[DERIVED]** algebra written out here and checked numerically where stated; **[INFERRED]** reasoning, not a run.

---

## 0. Already resolved before this round (no further change)

| Reviewer point | Resolved in | Evidence |
|---|---|---|
| Lean build fails (missing `ControllerFiberProjector`) | `0b5b108` (module added; statements unchanged), checked by `1f9afc9` (`check_lean.sh` + root workflow) | GitHub Actions run #31, id 40153641197, success at `dc0250a`: https://github.com/jacobbrainard84-knightninja/AIEFS/actions/runs/40153641197 |
| Nested template workflows under `lean/AIEFProofs/.github/` never run | `1f9afc9` added the active workflow at the repository root `.github/workflows/lean.yml`. The nested copies were left untouched, as the owner asked | https://github.com/jacobbrainard84-knightninja/AIEFS/commit/1f9afc9 |
| Tracked editor lock file, `.lake` build outputs, `__pycache__/*.pyc` | Cleanup commits `e8bcb0b` (1/48, the lock file) … `dc0250a` (48/48): 17 `.pyc` files and 30 `.lake` files are no longer tracked; `.gitignore` updated in `0f5ef7a` | https://github.com/jacobbrainard84-knightninja/AIEFS/compare/00b17d6...dc0250a |

## 1. Ledger (round 4)

| # | Point | Verdict | What changed | Evidence |
|---|---|---|---|---|
| 1 | "374 well-resolved components" mixes two different objects | **Concede.** 374 = **264** resolved components with a two-sided nonzero controller fiber + **110** resolved all-tied K3s, which have no fiber (ker A_K3 = 0) and are checked through one-sided rays. The single "λ to 2.1e-8, κ to 2.1e-6 on 374" bound holds only for the 264. For the 110 K3s, the bound is λ to 1.7e-7 relative and κ to 1.7e-5 absolute (on 294 resolved slow node rays). The strongest claim is reworded (§3). | New script; claim (iv) reworded in response_2, salvage and response | [RAN] `scripts/rate_law_census_r4.py` → `results/rate_law_census_r4.json` (`census`, `two_sided_resolved_errors`, `K3_one_sided_resolved_errors`) |
| 2 | Rate law stated too strongly | **Concede.** The exact one-step statement is λ = (1−γdt)·s_J, for h ∈ ker A_J with equal controlling scales s_J (§2.2 lists the conditions). The closed form λ_k = (1−γdt)c/(c+dt(kη−γc)+ε) is conditional: it adds the ideal hypotheses R = 1 and row sum c at the controlling nodes. The finite-ε fixed point is now solved and reported: it moves λ by 1.6e-12 relative, so ε does not explain the observed ~2e-8 deviations. | §2.2; wording in §3 | [RAN] `results/rate_law_census_r4.json` (`finite_eps_fixed_point`) |
| 3 | K3 described in spectral/eigenmode language; tie ratios underived | **Concede the language; the ratios are now derived.** An all-tied K3 has **zero lineality but nontrivial one-sided controller-selection rays +v_c with the degree-two slow multiplier λ_2**. It has no eigenmode or two-sided slow direction. Both tie patterns are now derived (§2.3), for all-tied K_n with **equal edge weights**: nonadditivity 1/√(2k(k−1)) and odd defect √(2/(k+1)). They were checked on synthetic K3–K8 to ≤ 4.4e-10. A K4 with unequal edges breaks them (0.2003 vs 0.2887; 0.7254 vs 0.7071). | §2.3–2.4 | [DERIVED] + [RAN] `results/rate_law_census_r4.json` (`tie_patterns_synthetic`, `tie_patterns_observed_vs_derived`) |
| 4 | `frozen_topology_check` should also test P_future | **Concede (added); the result is unchanged.** New fields `nonbinary_P_future_count` and `P_future_label_differs_from_split_status`, per group and in total. Totals: 29040 edges; 0 change status; 0 have non-binary P_future; 0 have a P_future label that differs from the split status. P_future is accumulated at **every** future step (stride 1, `P_sum += B > B_C`), so a binary P_future means each edge keeps its threshold status at every step of the future window, not just at the endpoints. Continuous weights can still move. | modified script; the result now carries `P_future_definition` and `interpretation` | [RAN] `scripts/frozen_topology_check.py` → `results/frozen_topology_check.json` |
| 5 | Bregman no-go: domain unstated | **Concede (stated now).** The no-go applies to every Legendre generator φ whose open domain of differentiability contains **both** the exterior witness x and its output A_ε(x). In edge coordinates (ℝ^66, upper triangle) both lie in the open positive orthant (all entries of x equal 1.5c/11 ≈ 0.0864; min output entry 0.05758). So the no-go covers negative entropy/KL, every quadratic (positive-definite metric) generator, and any other φ differentiable on a neighbourhood of both points. It says nothing about generators whose domain excludes either point. | §2.1 | [INFERRED] standard optimality argument; numbers [RAN] `logs/mathcheck.log` |
| 6 | Stale publication wording | **Concede.** Round 3 was published at `60e6029` (22 commits, `7d752fd`…`60e6029`, parent `c9907a6`). The Lean projector came next, in `0b5b108`. Tooling, lean_recovery and cleanup followed in 56 commits, `0f5ef7a`…`dc0250a`. The "Nothing was pushed / local" sentences in response_2 (line 4 and §5) and in README (line 22) now carry dated corrections. | inline notes | [READ] `git log` (§5) |
| 7 | PII scan scope overstated | **Concede.** `tooling/pii_scan.py` scans **only** `AI Agent Audits/`. Its CLEAN result says nothing about the rest of the repository. Repo-wide privacy and copyright (audit H3/H4) remain **unresolved, an owner decision**. | README Tooling and this ledger | [RAN] `tooling/logs/pii_scan.log` |
| 8 | The 18-coordinate "unique slow pole" spectrum is still cited | **Concede: quarantined.** (a) New corrected script `evidence/proposals/aief_1_4_full_state_spectrum.py` (the repo original is not edited). On the closed 966-dimensional state, its verdict is **NO**: the EMA pole is not the unique slow pole (§2.5). (b) Citation list with file:line: `evidence/proposals/augmented_spectrum_citations.md`. Nothing listed there was edited (owner decision, §6). | new proposal + citation list | [RAN] `evidence/proposals/results/full_state_spectrum.{json,log}` |
| 9 | Regenerate and verify | **Done.** Full `run_all.sh` rerun (19 steps, `UPDATE=1`). The only differences from the committed results were the two expected files (§4). Then a second full run without `UPDATE` (fresh outputs in a temp dir, compared byte-for-byte against the committed results): ALL OK. After that, the manifest was regenerated and checked with `verify_manifest.py`, and the PII scan was run with and without the private-literal list. | §4 | [RAN] `logs/run_all_update_r4.log`, `logs/run_all_verify.log`, `tooling/logs/verify_manifest.log`, `tooling/logs/pii_scan.log` |
| L1–L6 | Lean (Part B) | **Done locally** (§5): Smoke imported from the root; `STRICT_ORPHANS=1` in CI; source SHA256SUMS enforced by `check_lean.sh`; README rewritten; workflow header fixed; new conditional theorems with no `sorry` | §5 | [RAN] `evidence/logs/lean_r4/` |

## 2. Derivations and new results

### 2.1 Gate no-go, with the domain stated (point 5)
Gate: s_i = min(1, c/(q_i+ε)), A_ε(x)_ij = x_ij·min(s_i, s_j), q_i = Σ_j x_ij. Let C = {B ≥ 0 symmetric, row sums ≤ c} (closed, convex). Witness: x_ij = t = 1.5c/11 for all i ≠ j, so q = 1.5c = 0.95 > c and x ∉ C. Output row sum: c·q/(q+ε) = c − cε/(q+ε) = c − 6.67e-13 < c, and every output entry is t·c/(q+ε) > 0. So A_ε(x) ∈ int C and A_ε(x) ≠ x.
Claim: let φ be Legendre (strictly convex, differentiable on the open set int dom φ) with x, A_ε(x) ∈ int dom φ. Then A_ε(x) is not the φ-Bregman projection P(x) = argmin_{z∈C} D_φ(z, x).
Proof: if P(x) = A_ε(x) ∈ int C ∩ int dom φ, first-order optimality gives ∇φ(P(x)) − ∇φ(x) ∈ −N_C(P(x)) = {0}. ∇φ is injective on int dom φ, so P(x) = x ∈ C, a contradiction. [INFERRED: standard]
Domain: both points are in (0,∞)^66, so the claim covers KL/negative entropy, every positive-definite quadratic, and any φ differentiable near both. Generators whose domain excludes x or A_ε(x) are not covered. The ε = 0 question stays open, as in response_2 §6.

### 2.2 Rate law: exact statement, conditional closed form, finite-ε fixed point (point 2)
One engine step on a component: x = B + dt((η+μ)R − μ − γB), then the gate. Fix the controlling set J (nodes whose scale is the minimum on some edge), and take h ∈ K = ker A_J with ‖h‖ = 1 and δ small.
**Exact one-step statement [DERIVED].** Assume:
- (a) the gate is on;
- (b) the clamp x ≥ 0 is inactive on the component;
- (c) R does not respond to the B-perturbation within the step;
- (d) δ is smaller than the untied gaps, so no controller changes;
- (e) the controlling scales are equal, s_i = s_J for all i ∈ J.

Then δx = (1−γdt)δh, δq_i = 0 for i ∈ J (h ∈ ker A_J), so s is unchanged on J and δB' = (1−γdt)s_J·δh. Hence λ = (1−γdt)·s_J. ε enters only through s_J = c/(q_J+ε). If (e) fails, the response is (1−γdt)·diag(s_ctrl(e))·h, which is not a multiple of h in general.
**Ideal hypotheses → closed form (conditional).** If additionally R = 1 on the component's edges and each controlling row of B sums to c, then x_e = (1−γdt)B_e + ηdt, q_J = (1−γdt)c + kηdt, and λ_k = (1−γdt)c/(c + dt(kη − γc) + ε). Both hypotheses are exact only in the limit; the replay states satisfy them approximately.
**Finite-ε fixed point [DERIVED + RAN].** For the ideal clique with all k row edges equal, the fixed-point row sum S solves S = c·q/(q+ε), q = aS + b, a = 1−γdt, b = kηdt, i.e. aS² + (b + ε − ac)S − bc = 0. Then λ_fp = ac/(q* + ε).

| k | c − S | λ_fp | λ_k (closed form) | relative change |
|---|---|---|---|---|
| 2 | 9.99e-13 | 0.99873824664 | 0.99873824663 | 1.575e-12 |
| 3 | 9.98e-13 | 0.99810856322 | 0.99810856322 | 1.573e-12 |
| 4 | 9.98e-13 | 0.99747967330 | 0.99747967330 | 1.571e-12 |
| 5 | 9.97e-13 | 0.99685157539 | 0.99685157539 | 1.569e-12 |

κ changes by about 1.6e-10.
**Observed (264 resolved two-sided fibers, 40 fixed seeds × 5 T_w):** the fiber multiplier agrees with (1−γdt)·mean(s_J) to 2.04e-8 relative and with λ_k to 2.07e-8. The rate agrees to 1.64e-5 relative and κ to 2.07e-6 absolute. The max s spread on J is 8.5e-10 and the max relative residual 4.3e-8. On the 32 poorly resolved components (all ρ=2): λ to 4.8e-6, κ to 4.8e-4, rate to 3.8e-3.
The ~2e-8 gap is about 10⁴ times larger than the ε correction, so it is **not** an ε effect. It is the same against the state formula as against the closed form, so it is not a departure from the ideal hypotheses either. I have **not** isolated its source. Unverified candidates are finite-difference error at the per-component δ and a within-step dependence of R on B, which would violate (c).

### 2.3 Tie patterns, derived (point 3) [DERIVED + RAN]
Setting: an all-tied K_n (k = n−1) in the gate. Every node has the same q and the same scale s < 1, every edge has weight x_e = q/k (**equal edge weights**), λ = (1−γdt)s, and D(v) is the one-sided difference quotient of the step in direction v (taken with respect to B, which contributes the factor 1−γdt). ds_i/dq_i = −s/(q+ε), and x_e·s/(q+ε) = (s/k)·q/(q+ε). The factor q/(q+ε) = 1 − O(1e-12) is dropped below.
- **D(h₁), h₁ = e_(i,j) raised:** q_i and q_j rise, so s_i and s_j fall by sδ/q. Edge (i,j): λ − λ/k. Each of the other 2(k−1) edges at i or j has its minimum lowered, giving −λ/k. Hence D(h₁) = λe₁ − (λ/k)·1_{edges at i or j}, and ‖D(h₁)‖ = (λ/k)√((k−1)(k+1)).
- **D(−h₁):** s_i and s_j rise. Only edge (i,j) has both endpoints raised, so only its minimum moves: D(−h₁) = −(λ − λ/k)e₁. Then D(h₁) + D(−h₁) = −(λ/k)·1_{2(k−1) edges at i or j other than e₁}, with norm (λ/k)√(2(k−1)).
  **Odd defect** = √(2(k−1))/√((k−1)(k+1)) = **√(2/(k+1))**.
- **Nonadditivity, h₂ = e_(i,l), adjacent at i:** D(h₁+h₂) − D(h₁) − D(h₂) is zero except at the edge (j,l). There, D(h₁+h₂) gives −λ/k (both s_j and s_l fall by one unit), while D(h₁) + D(h₂) gives −2λ/k. So the difference has norm λ/k.
  D(h₁) + D(h₂) has the following entries:

  | edges | count | entry |
  |---|---|---|
  | e₁, e₂ | 2 | λ − 2λ/k |
  | other edges at i | k−2 | −2λ/k |
  | (j,l) | 1 | −2λ/k |
  | other edges at j | k−2 | −λ/k |
  | other edges at l | k−2 | −λ/k |

  The squared norm is (λ/k)²·2k(k−1). **Nonadditivity** = **1/√(2k(k−1))**.

Synthetic check: an exact copy of the gate step on ideal equal-weight all-tied K3…K8 matches both formulas to ≤ 4.4e-10. A K4 with equal row sums but edge weights in the ratio 0.3 : 0.2 : 0.1 gives nonadditivity 0.2003 (formula 0.2887) and odd defect 0.7254 (formula 0.7071), so **equal edge weights are required**.
Replay data (373 resolved all-tied components) agree with the formulas to a maximum relative deviation of 1.5e-5 to 5.8e-5 per type. For K3, equal row sums force equal edge weights. For n ≥ 4 they do not, so the replay states must be close to equal-weight. I have not decomposed the deviations further.

### 2.4 K3: zero lineality, one-sided controller-selection rays (point 3)
For K3, A_K3 is the 3×3 unsigned incidence of a triangle, which is invertible, so ker A_K3 = 0. There is no two-sided direction that preserves the controllers, and no eigenmode. Let v_c be −1 on the two edges at node c and +1 on the opposite edge.
- **+v_c [DERIVED]:** q_c falls and the other two row sums are unchanged. So s_c rises, node c stops controlling, and the minima on its edges stay at the unchanged neighbour scale. Hence D(+v_c) = λ·v_c exactly, with the degree-two multiplier λ_2 (k = 2).
- **−v_c [DERIVED]:** q_c rises by 2δ and s_c falls by 2sδ/q. Each edge at c changes by s − x_e·2s/q = 0 (x_e = q/2). The opposite edge changes by −s. So D(−v_c) = λ·e_opp, ⟨D(−v_c), −v_c⟩/‖v_c‖² = λ/3, and −v_c is not slow.
- **Observed [RAN]:** in 110/110 resolved all-tied K3s, a +v_c ray is slow. There are 294 resolved slow node rays: λ vs λ_2 to 1.7e-7 relative, residual ≤ 2.4e-7. The bound over all +rays, including the ρ=2 nodes that miss the slowness threshold, is 1.8e-5. −v_c is slow in 0/110, and its λ/λ_2 lies in [0.33333, 0.33337] (prediction 1/3).
- **Lean** (§5, `CompleteGraphIncidence.lean`): ker of the K3 incidence = ⊥; row sums of the incidence applied to v_c are −2 at c and 0 elsewhere (+2 at c for −v_c); v_c ∉ ker. These are the linear-algebra facts only. The gate statements above are not formalized.
Replacement wording: "An all-tied K3 has zero lineality (ker A_K3 = 0) but nontrivial one-sided controller-selection rays +v_c with the degree-two slow multiplier λ_2. It has no two-sided slow mode." This replaces the round-3 phrases "slow direction", "the response is linear", "spectrally silent" (retracted earlier) and any eigenmode wording for K3.

### 2.5 18-coordinate spectrum: quarantine (point 8) [RAN]
The repo's `aief_1_4_augmented_spectrum.py` differentiates an 18-coordinate map that is not a closed state (response_2 §2.5: `restore_state` omits theta, and the result depends on column order). Its verdict, "The EMA pole alpha IS the unique slow pole …", is **quarantined**: do not cite it. The corrected replacement is a new file, `evidence/proposals/aief_1_4_full_state_spectrum.py`; the original is untouched.
It works on the closed 966-dimensional state: history 612 + B upper triangle 66 + Re/Im C 288. It uses run 5a9f093a2fe0, seed 4619122171158768524, 32000 replay steps and a central difference with h = 1e-7. Checks: rotation symmetry exact to 2.2e-16; theta equals the last history entry.
- **One step, central:** 3 neutral modes and the 288-mode EMA cluster at rate 0.057133. **10 rates lie in the gap:**
  - 0.189328 ×2 (B-dominated, K4 cluster; λ_3)
  - 0.252355 ×5 (B-dominated, K5 cluster; λ_4)
  - 0.650378, 0.662045 and 0.668921 (history/phase-dominated)
- **T = 500 finite-time:** 13 rates in the gap.
- No 0.126 mode appears. This is consistent with §2.4: the K3 has no two-sided mode, and a central difference averages the +v_c ray (λ) with the −v_c ray (λ/3).
- The one-sided matrices J± differ by up to 0.49937, all in the B block. They are mixed-branch objects and are not presented as Jacobians.

Verdict: "EMA pole is the unique slow pole of the full closed state: **NO**." This is one replay, a finite-difference result and not a proof. Its status is a proposal; it is not a repo result.

## 3. Wording replacements (authoritative; supersede response_2 §3)
- **Strongest claim (iv):** "On complete, saturated, phase-locked components, the one-step multiplier on the controller cycle kernel K = ker A_J is λ = (1−γdt)s_J, when the controlling scales are equal (conditions in response_3 §2.2). Under the ideal hypotheses R = 1 and row sum c at the controlling nodes, this equals λ_k = (1−γdt)c/(c+dt(kη−γc)+ε) (the repo's Prop 8.3 form); the finite-ε fixed point changes it by 1.6e-12 relative. It was checked on 374 resolved components: (a) 264 with a two-sided nonzero fiber (λ to 2.1e-8 relative, κ_k = −log λ_k/dt − 1/T_w to 2.1e-6 absolute); and (b) 110 all-tied K3s, which have zero lineality but nontrivial one-sided controller-selection rays +v_c with the degree-two slow multiplier (λ to 1.7e-7, κ to 1.7e-5 on 294 resolved rays). Data: 40 fixed seeds × 5 T_w; not independent replications."
- **Tie patterns:** "For all-tied K_n with equal edge weights, the one-sided gate derivative has nonadditivity 1/√(2k(k−1)) and odd defect √(2/(k+1)) (derived; response_3 §2.3). The replay values agree to ≤ 5.8e-5 relative."
- **Frozen topology:** "0/29040 edges change threshold status between split and end, and 0/29040 have non-binary P_future. Since P_future averages the threshold indicator over every future step, every tested edge keeps its status throughout the future window (finite horizon). Continuous weights may still move."
- **Gate:** add to response_2's gate sentence: "…for every Legendre generator differentiable on a neighbourhood of both x and A_ε(x) (both lie in the open positive orthant of edge space)."
- **Spectrum:** "The 18-coordinate 'unique slow pole' result is quarantined. On the closed 966-dimensional state of the same replay, the EMA pole is not the unique slow pole (10 rates in the gap; proposal, finite-difference)."
- **PII:** "The personal-data scan covers `AI Agent Audits/` only. Repo-wide privacy and copyright are unresolved, pending the owner's decision."

## 4. Regeneration and verification (point 9) [RAN]
- `run_all.sh` now has 19 steps; `rate_law_census_r4` was added after `analyze_kappa_cycle_kernel`. A full run with `UPDATE=1` found exactly two expected differences against the `dc0250a` results: `frozen_topology_check.json` DIFFERS (new fields only) and `rate_law_census_r4.json` NEW. Every other result was byte-identical (`logs/run_all_update_r4.log`). A second full run without `UPDATE` then reported ALL OK (`logs/run_all_verify.log`).
- The dated inline corrections in `AIEFS_audit_response_2.md` (18), `README.md` (4), `AIEFS_salvage.md` (2) and `AIEFS_audit_response.md` (2) were applied by `evidence/tooling/round4/corrections_r4.py`. It was run once; each anchor must match exactly once, and it refuses to run a second time.
- The manifest was regenerated (`tooling/make_manifest.py`) to include the new script, result, proposals and this ledger. `verify_manifest.py` returned OK, exit 0 (`tooling/logs/verify_manifest.log`).
- PII scan of `AI Agent Audits/`: CLEAN (FOUND 0) without the private list and CLEAN with it (`tooling/logs/pii_scan.log`). On the first rebased tree (main `43ce98f`) both runs reported FOUND 2, both packaging-size findings from `licensing_inventory/inventory.json` (1,460,241 bytes, over the 1 MB per-file limit; folder total about 5.86 MB, over 5 MB). With the owner's approval (2026-10-25), that file was replaced by `licensing_inventory/inventory.json.gz.b64` (226,940 bytes): the same JSON, gzip-compressed (level 9, mtime 0) and base64-encoded in 76-character lines. This form is lossless: decoding gives back the exact bytes of the old file (sha256 `8deaa885…b731d68a`). A text form was chosen because the GitHub connector writes text only, and because the scanner flags `.gz` as binary. Its limits were not changed. `licensing_inventory/scripts/make_report.py` reads and writes the encoded form, and `INVENTORY.md` says how to decode it (`base64 -d inventory.json.gz.b64 | gunzip`). The private literals are never written to any log.

## 5. Lean (Part B) [RAN]
Local clone, first run at `dc0250a` plus the changes, then rerun after rebasing onto main `43ce98f` (LICENSE files, executable bits, the new copyright/SPDX headers on `ControllerFiber.lean` and `ControllerFiberProjector.lean`). Logs of the rebased run (paths redacted) are in `evidence/logs/lean_r4/`.
- **Rebase onto the new headers:** this round does not edit `ControllerFiber.lean` or `ControllerFiberProjector.lean`; their bytes are taken unchanged from `43ce98f` (sha256 `b51e07e8…ec63411` and `8199407d…b2d27ec`, matching that commit's message). The two new modules carry the same header form (holder "Jacob Brainard and AIEF contributors", Apache 2.0, plus an `-- SPDX-License-Identifier: Apache-2.0` line). `AIEF_LEAN_SOURCE_SHA256SUMS.txt` was regenerated after the rebase.
- **Smoke:** `AIEFProofs/Smoke.lean` builds, so it is now imported from `AIEFProofs.lean`. Its content is unchanged. The workflow runs `STRICT_ORPHANS=1`, and orphans = 0.
- **Source hashes:** `lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt` covers 8 files (all `.lean` files and `check_lean.sh`). `check_lean.sh` step 2 fails, exit 2, if the file is missing, if `sha256sum -c --strict` mismatches, or if a `.lean` file is unlisted. Negative tests of all three cases failed as intended. Update command (run in `lean/AIEFProofs/`): `sha256sum AIEFProofs.lean $(find AIEFProofs -name '*.lean' | sort) check_lean.sh > AIEF_LEAN_SOURCE_SHA256SUMS.txt`.
- **Build:** all 7 steps PASS, 8713 jobs, toolchain v4.33.1, Mathlib `0df444a360eaa60ab8c11dca51a86af692955474`. There are 12 warnings, all from the header linter on `Smoke.lean` (6 commands × "Copyright too short" / module doc-string), triggered by `weak.linter.mathlibStandardSet`. Fixing them requires editing Smoke.lean (owner decision). The new modules have 0 warnings. 0 `sorry`/`admit`/`axiom` markers in 7 scanned files.
- **Axioms:** 115 declarations audited, 0 disallowed. Allowed: `propext`, `Classical.choice`, `Quot.sound`.
- **New theorems:**
  - `ControllerFiberQuotient.lean`: CCtrl x = CCtrl y ⇔ x − y ∈ span vCtrl ⇔ PPerp x = PPerp y ⇔ PPar(x−y) = x−y (TFAE)
  - `CompleteGraphIncidence.lean`:
    - for n = 3..6, dim ker of the K_n unsigned incidence = C(n,2) − n (through an explicit right inverse)
    - K3: ker = ⊥; the row sums of the incidence applied to ±v_c; v_c ∉ ker; the K3 incidence rows equal CCtrl; v_2 = vCtrl
- **README** rewritten: theorem list, what is NOT proved, build steps, pins, allowed axioms, open problems; the template PR/Pages text removed. The workflow header now names the active root location.
- **Executable bit:** resolved on main in `1a81cb6` (`check_lean.sh` and the `tools/sync` scripts are mode 100755). This round keeps mode 100755; the README now says so.

## 6. Owner decisions (listed, not acted on)
1. ~~LICENSE: file headers claim Apache 2.0, but there is no LICENSE file.~~ **Resolved on main (2026-10-25):** `LICENSE` (Apache-2.0), `LICENSE-docs` (CC BY 4.0), `LICENSING.md`, `NOTICE` in `115e99e`; Lean headers in `43ce98f`; licensing inventory in `fb2e570`.
2. Root README.
3. Root environment lock (Python).
4. Scratch and duplicate trees (`Older files/`, etc.).
5. Large generated artifacts in the repo.
6. Renaming `test_output/`.
7. PII/copyright repo-wide (audit H3/H4). Partly acted on by the owner: 4 third-party PDFs under `Papers/` were removed (`d12b08c`, `15feb9b`, `aae9e75`, `17f2cf7`) and `AI Agent Audits/licensing_inventory/` lists the remaining third-party and personal files. Whatever is left there is still the owner's decision.
8. Editing the repo's source scripts, reports and manuscripts that cite the 18-coordinate result (`evidence/proposals/augmented_spectrum_citations.md`).
9. `Smoke.lean` header-linter warnings (needs an edit to Smoke.lean or to the lakefile linter option).
10. ~~Applying the executable-bit command in §5.~~ **Resolved on main in `1a81cb6`.**
11. ~~`licensing_inventory/inventory.json` exceeds the packaging limits~~ **Resolved (owner-approved 2026-10-25):** replaced by the lossless `inventory.json.gz.b64` (§4).

## 7. Limits
- Single parameter set; N = 12; 40 fixed S01 seeds. The full-state spectrum uses one replay.
- §2.2–2.4 are one-step algebra under stated conditions plus finite-difference checks. Only the linear-algebra parts are formalized in Lean.
- The source of the ~2e-8 rate-law residual is not identified (§2.2).
- The provenance gaps of response_2 §7 still apply, except gap 7 (Lean build not rerun), which is closed by CI run 40153641197 and the round-4 local run.
