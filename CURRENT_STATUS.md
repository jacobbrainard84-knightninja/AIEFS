# Current Scientific & Engineering Status (`CURRENT_STATUS.md`)

**Last Verified:** 2026-10-23 (`Milestone 1` complete; `verify_inventory.py` passing on all `2,898` inventoried objects)

> **Reconciliation note (2026-10-28, local merge-prep into `main`, Researcher 001; pending auditor review).**
> - This page was written on 2026-10-23, before audit rounds 2–4 (`AI Agent Audits/`). The authoritative per-claim
>   verdicts are now in `registry/claims.csv` (columns `prior_status`, `audited_status`, `audited_qualifier`, `audit_source`,
>   `reconciliation_note`) and, for the 1.4 lineage, in `registry/lineage_reconciliation.csv`.
>   Where they disagree with this page, they take precedence.
> - `verify_inventory.py` **no longer passes** on the merged tree. It stops at check [1/5] because `main` deleted 52
>   inventoried files (`lean/AIEFProofs/.lake/` 30, `__pycache__/` 17, `Papers/` 4, one editor lock file). Per-row
>   status is in the `tree_check_2026_10_28` column of `registry/artifacts.csv`.
> - "Classified" below means every file got a label. It does **not** mean every file was audit-verified.
> - The AIEF-1.4 operator/tangent/cocycle/controller rows below are a **single-seed case study** (one exceptional seed,
>   1 of 40). Only the split-state memory ablation is a 40-seed cohort result (`AUD-SCOPE-1.4`).
> - Corrections to hash-pinned documents are kept in `ERRATA_2026-10-28.md`; the pinned files are unchanged.
>   Status categories (past origin hypotheses / current tested results / future untested ideas) are in §3 below.
>   Where we've been / where we are / where we're going is in §4 below. This file is the single status file.

---

## 1. Two-Axis Inventory Summary (`registry/artifacts.csv`)

Every tracked file (`2,760` working-tree files) and every member inside the three `.zip` archives (`138` archive members) carries **both** an `artifact_status` and an `evidence_scope`:

| `artifact_status` | Worktree Files (`2,760`) | Zip Members (`138`) | Combined (`2,898`) | Meaning |
|---|---:|---:|---:|---|
| **`Frozen`** | `803` | `0` | **`803`** | Immutable baseline datasets, disjoint production cohorts, and SHA-256 authority-locked sources |
| **`Supported`** | `466` | `24` | **`490`** | Active, audited code, Lean 4 formal proofs, full-state cocycle analyses, and unpacked `.zip` lineage records |
| **`Exploratory`** | `157` | `0` | **`157`** | Non-authoritative pilot runs (`ebfec9a5c419`), historical origin scans, and draft manuscript with scope caveats |
| **`Superseded`** | `1,308` | `114` | **`1,422`** | Deterministic 20-seed reruns, older code versions (`v1`/`v2`), duplicate `.zip`s, `01` copies, and build caches |
| **`Rejected`** | `15` | `0` | **`15`** | Scientifically falsified compressed-spectrum scripts, K3 subgraph overcount, and pseudoreplicated `N=40` pool |
| **`Incomplete`** | `11` | `0` | **`11`** | Aborted partial execution outputs (`aief_1_4_matched_phase_memory_ablation/`, `runs/a937d5e96efb/`) |
| **`Unreviewed`** | `0` | `0` | **`0`** | **100% of files explicitly classified** (2026-10-28: classified ≠ audit-verified; see note above) |

---

## 2. Study-by-Study Status & Authoritative Artifacts (`registry/studies.csv`)

| Study / Component | `artifact_status` | `evidence_scope` | Authoritative Code & Evidence Paths | Critical Pitfalls to Avoid |
|---|---|---|---|---|
| **AIEF-1.3 Causal Ablations ($N=100$)** | `Frozen` (audit: *Supported, qualified*; `shuffle_R` outcome forced by construction; fixed design, not preregistered; EMP-AIEF13-01/02) | `Controlled experimental result` | `AIEF_1_3_paired_statistics_updated.py` + `runs/c3da1ac707bf` + `runs/73dca37cf93f` | **Do NOT use `paired_seed_analysis/` (`Rejected`)** or pass default CLI flags without explicit cohort paths (root defaults point to duplicate 20-seed runs). |
| **AIEF-1.4 Split-State Memory Ablation** | `Frozen` (audit: *Supported, reworded*: phase+history+EMA suffice; B predictive, not causal; EMP-AIEF14-01) | `Controlled experimental result` | `AIEF_1_4_memory_ablation_updated.py` + `runs/5a9f093a2fe0/` | Root `AIEF_1_4_memory_ablation_updated.py` (`34d37908...`) is SHA-256 locked by `manifest.json`; **do NOT overwrite** with whitespace-modified `.zip` copy. |
| **AIEF-1.4 Matched-Phase Ablation** | ~~`Frozen`~~ → **`Exploratory`** (2026-10-28, per audit resp2 #3/#7: controlled exploratory analysis with fixed recorded design; "mediates" wording withdrawn; P_mean_late is negative, −0.018 [−0.027, −0.009]; EMP-AIEF14-02) | `Finite numerical observation` in the ledger (the vocabulary has no exploratory-design value) | `AIEF_1_4_matched_phase_memory_ablation.py` + **`test_output/`** (`6.2 MB`, 40 seeds) | **Name inversion trap:** `test_output/` is the completed 40-seed study; `aief_1_4_matched_phase_memory_ablation/` (`2.9 KB`) is an aborted 3-file partial run (`Incomplete`). |
| **AIEF-1.4 $T_{\text{window}}$ Sensitivity (`200` cond.)** | Run outputs `Frozen`; claim EMP-AIEF14-03 **`Exploratory`** (controlled exploratory analysis with fixed recorded design; DID estimand not tested by the audits). κ_k(T_w) = kη/c − 1/T_w per component is audit-verified (AUD-KAPPA-TW) | `Finite numerical observation` (claim) | `runs/b57562a8ee77/` + `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4.py` | **Do NOT confuse with `Older files/b57562a8ee77/`** (`--baseline-only` pre-run) or `runs_pivot_study/ebfec9a5c419/` (`120`-cond. non-authoritative pilot). |
| **Full-State Tangent & History Cocycle** | `Supported` (single-seed case study) | `Finite numerical observation` | `aief_1_4_full_state_tangent_operator.py`, `aief_1_4_history_cocycle_test.py`, `aief_1_4_branch_tangent_comparison.py`, `aief_1_4_jacobian_step_convergence/` | **Keep strictly separate from `Rejected` compressed-operator scripts** (`aief_1_4_operator_compression.py` etc.). |
| **Multiplier-Controller Fiber & Intertwining** | `Supported` (single-seed case study; "projection" wording rejected — the gate is not a projection, AUD-GATE; strict K3 have one-sided rays, AUD-K3) | `Conditional theorem` / `Finite numerical observation` | `aief_1_4_intertwining_controller 02/` (`40/40`), `aief_1_4_feedback_rank_memory_reduction/`, `aief_1_4_k3_fiber_audit/` (`26` isolated $K_3$ components) | Unnumbered `aief_1_4_intertwining_controller/` is pre-fix (`38/40`, `Superseded`); `01` is a duplicate of `02`. |
| **Lean 4 Controller Kernel Proof** | `Supported` (audit-verified; trivial linear algebra, LEAN-CF-01). Round-4 package: Lean `v4.33.1`, 6 modules, 115 declarations, standard axioms only (LEAN-R4) | `Formalized theorem` | `lean/AIEFProofs/` (`AIEFProofs.lean`, 6 modules, `check_lean.sh`; `0` `sorry`) | Proves algebraic identity $\ker C_{\{2,7\}} = \operatorname{span}\{(1,-1,-1)\}$ only; winner persistence along trajectories is empirical (`CF05`) / open (`CF12`). |
| **Operator Theory Draft Manuscript** | `Exploratory` | `Conditional theorem` | `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md` | **Caveat `CAVEAT-MS-8.4`:** Corollary 8.4 ambient left orthogonality $V^\top D\mathcal{A}_\varepsilon(x_G) = s_k V^\top$ holds at $x_G = x_{\text{common}}\mathbf{1}$, **not** across general fiber perturbations $x_0\mathbf{1}+h$. |
| **Modular Platform `v1_analysis_v4`** | `Supported` implementation identity, not re-tested by the audit (IMPL-MODULAR-01; tests re-run 2026-10-28: default 40 passed, 2 skipped; 41 passed, 1 skipped with AIEF_RUN_SLOW_TESTS=1 and the repo root on PYTHONPATH) | `Implementation identity` | `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/` | Supersedes `workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f/`. Same-host equivalence vs monolithic code is exact (`0.000e+00`). |
| **Retired Spectral Compression & K3 Subgraph Scan** | `Rejected` | `Finite numerical observation` | `aief_1_4_operator_compression.py` (`24,323.8%` leakage), `aief_1_4_slow_subspace_projection.py` (`7.5e35`), `aief_1_4_observable_jacobian.py`, `aief_1_4_coupling_lock_audit.py`, `aief_1_4_k3_structure_scan.py` (`856` subgraphs) | Preserved byte-for-byte unmodified as negative methodological evidence; never cite as positive support. |
| **"EMA pole is the unique slow pole" (`aief_1_4_augmented_spectrum/`)** | `Quarantined` (2026-10-28; AUD-SLOWPOLE; ledger `artifact_status` `Rejected`, as the vocabulary has no `Quarantined`) | `Finite numerical observation` | `aief_1_4_augmented_spectrum/augmented_spectrum_report.txt` (file unchanged; caveat in `ERRATA_2026-10-28.md` E2) | Quarantined — invalid derivation; do not cite. Audit proposal on the 966-dim state (one replay, finite-difference, not a proof) gives NO: 10 gap rates. |
| **Pre-AIEF SSRH origin hypotheses (`Project Origins/`)** | **Speculative / untested origin hypothesis** (owner decision 2026-10-28; SSRH-ORIG-01..07; ledger `Incomplete`) | `Conjecture` | `Project Origins/` PDFs (AI-chat text only; no script or data in the repo) | Not cited as results until a testable form is stated and a test is run. Not retired: nothing was tested and failed. |

---

## 3. Status categories

Claims fall into three time-ordered categories. The full definitions are in `registry/README.md` ("Status categories").

| Category | Ledger rows | Rule |
|---|---|---|
| **Past origin hypotheses** | `SSRH-ORIG-01..07` (audited_status *Speculative / untested origin hypothesis*) | Kept as history and possible future directions. Not cited as results. Promotable to Exploratory or Supported once a testable form is stated and a test is run. |
| **Current tested results** | `EMP-*`, `CF*`, `IMPL-*`, `LEAN-*`, `AUD-*` | Cited only at the scope in `audited_status` / `audited_qualifier` / `scope_boundary_and_caveat`. |
| **Future untested ideas** | Conjectures such as `CF11`, `CF12`, `AUD-NOVELTY` | Stated as conjectures or open questions; not cited as results. |

Retired (`S01–S18`, `Superseded`), `Rejected` and Quarantined (`AUD-SLOWPOLE`) are reserved for claims that were tested and failed, or were withdrawn.

## 4. Where we've been / where we are / where we're going

**Where we've been.**
- Pre-AIEF Solar System Resonance Hypothesis (SSRH) ideas. These are the origin hypotheses, `SSRH-ORIG-01..07`, and are untested.
- AIEF-1.3 multi-seed cohort studies.
- AIEF-1.4 operator/tangent/cocycle/controller work. This is a single-seed case study, plus the 40-seed split-state memory ablation.
- Milestone 1 inventory (2026-10-23).
- Audit rounds 1–4 (`AI Agent Audits/`).
- Retired and rejected claims are kept in `registry/claims.csv` (`S01–S18`, `REJ-*`, `AUD-SLOWPOLE`).
- The SSRH origin numbers appear only in AI-chat text in `Project Origins/`. No script or data in the repo computes
  them (see the reconciliation note on the `SSRH-ORIG-*` rows). They are valued as where the project came from and are not retired.

**Where we are (2026-10-28).**
- The local branch `merge-prep/arena-reconciled` reconciles the arena Milestone 1 work with `main` and the audits.
- It is **not pushed**. It waits for review by the owner, Auditor Seat 002 and outside reviewers.
- The claim ledger has 75 rows (7 post-push review rows added on local branch `work/post-push-1`, not pushed). Corrections to pinned files are in `ERRATA_2026-10-28.md`.
- Details, checks and open items are in `MERGE_PREP_REPORT.md`. Working rules are in `OPERATING_MANUAL.md`.

**Where we are: tested model results.** Each item cites its ledger row in `registry/claims.csv`. Cite only at that row's scope.
- **Model.** 12 delayed Kuramoto oscillators, an exponentially averaged coherence `R`, Hebbian edge weights `B`
  and a capacity gate (`README.md`).
  - The gate is min-endpoint: `s_i = min(1, c/(q_i+ε))`, `B'_ij = x_ij·min(s_i, s_j)`, with
    `c = (A−δ)/Q = 0.6333` (A = 1, Q = 1.5, δ = 0.05). Sources: `AI Agent Audits/AIEFS_audit_response_2.md`
    line 29 and `AI Agent Audits/AIEFS_salvage.md` line 38.
  - It is node-strength normalisation, not a projection (AUD-GATE).
- **Rate law: exact only under conditions (AUD-RATELAW, AUD-KAPPA-TW).**
  - The one-step multiplier `λ = (1 − γ·dt)·s_J` on the unsigned-incidence controller kernel (row-sum-preserving edge kernel) is exact only under conditions
    (a)–(e), including (e) equal controlling scales.
  - The closed form `κ_k = kη/c − 1/T_w` needs further ideal hypotheses.
  - It was checked on 374 resolved components (264 two-sided, 110 all-tied K3) from 40 fixed seeds × 5 T_w.
    These are not independent replications.
  - A ~2e-8 gap is unexplained until a step-size sweep is run. A within-step response of R to a B perturbation is ruled out, because Engine v1
    computes R before it updates B (`ERRATA_2026-10-28.md` E5). The maximum residual comes from one component with a tiny
    finite-difference step (δ in [1e-9, 1e-8)); the 263 well-resolved components agree within 2.1e-10. Finite-difference/rounding
    error is the most likely cause; finite-time departure and unequal controlling scales are less likely.
- **Old 18-coordinate spectrum and "unique slow pole": quarantined.** The 18-coordinate map is not a closed state.
  Cite neither the original YES nor the audit's NO proposal (AUD-SLOWPOLE; `ERRATA_2026-10-28.md` E2).
  - The audit's 966-coordinate closed-state calculation is evidence against the claimed spectral gap. It is not a
    branch-independent full-system spectrum, and it stays a proposal. Its limits are:
    - central differences at nonsmooth points (clipping, gate, endpoint minima, ties) give a generalized response
      matrix, not a Jacobian;
    - the eigenvalues of the 500-step finite-time map are not Floquet or equilibrium multipliers, so singular
      values are more defensible;
    - the neutral phase-shift modes of the independently rotating components have not been quotiented out;
    - the block participation weights depend on the coordinates chosen;
    - only h = 1e-7 was used.
- **Tie formulas need equal edge weights (AUD-TIES).** For an all-tied K_n with equal edge weights, nonadditivity is
  `1/√(2k(k−1))` and the odd defect is `√(2/(k+1))`. For n ≥ 4, equal row sums do not imply equal edges. An unequal-edge
  K4 breaks both formulas (0.2003 vs 0.2887; 0.7254 vs 0.7071). The figures depend on which pair of adjacent edges is perturbed
  (other pairs give 0.2627 / 0.7254 and 0.3046 / 0.7140), and the unequal-edge state is not a fixed point. So it refutes
  universality, but it is not a fixed-point counterexample.
- **Corr_physical ≈ 0.995 holds only for the hand-picked frequencies.** It is ~0.71 for uniform random ω and
  0.59–0.63 for clustered ω (AUD-CORR-0995; errata E1). Replication means: uniform 0.745/0.747 (medians ~0.98), clustered
  0.553/0.531 (defined in 37/39 of 60 runs) (AUD-CORR-0995-SCOPE). Response 1 overstates "past R adds over Δω-only" for
  uniform no_delay: it holds on log loss only (AUC 0.850 vs 0.883; AUD-RESP1-UNIFORM, errata E8).
  The ~0.995 lines in the pinned `AIEF_HISTORIC_UNFOLDING.md` / `AI_AGENT_HANDOFF_PROMPT.md` are scoped by AUD-CORR-0995-SCOPE (errata E9; the inline side branch is not merged).
- **Analysis v4 held events at exact-duration boundaries: blocker.** v4's end check can reject an event held exactly the required
  duration (floating-point rounding; 32 of 605 starts on v4's saved grid in a synthetic test). Only grid-multiple holds are affected,
  i.e. the fixed_physical_17p5 held rows; the T_window-nominal holds are not. Separately, v4's "recovery" events include retention.
  Cite the fixed_physical_17p5 held numbers only with this caveat (AUD-V4-HELDEVENT, AUD-V4-RECOVERY-WORDING). A v4.1 candidate exists and is unaudited.
- **Modular platform: not oracle-certified by the repo tests.** The oracle-equivalence test is skipped by default, and the slow
  engine test runs only with `AIEF_RUN_SLOW_TESTS=1` and the repo root on `PYTHONPATH` (default: 40 passed, 2 skipped; AUD-MODULAR-ORACLE).
- **Matched-phase ablation: exploratory.**
  - Weighted_similarity_late is +0.064 [0.041, 0.089] (31/40).
  - P_mean_late is negative, and the Retention CI spans 0.
  - No mediation claim (EMP-AIEF14-02).
- **Split-state memory ablation (40 paired seeds): supported, audit-qualified wording.** B is not a unique memory
  bottleneck. Resetting B at the split time rebuilds mature topology almost identically from the delayed
  oscillator/EMA state (EMP-AIEF14-01).
- **Scope of the AIEF-1.4 operator work.** It is a single-seed case study, 1 of 40 seeds (AUD-SCOPE-1.4).
- **Lean.**
  - `lean/AIEFProofs` uses toolchain v4.33.1.
  - The audit found 115 declarations that use only `propext`, `Classical.choice` and `Quot.sound`, with
    0 `sorry`/`admit` (LEAN-R4). After the `Smoke.lean`/`Basic.lean` header and import changes (E7), it was re-run:
    cached build by Auditor Seat 002 at 886daf6: 7/7 PASS, 115 declarations, 3 allowed axioms, 0 warnings, 1,591 build jobs.
  - The proofs are linear-algebra and incidence facts, not dynamics (LEAN-CF-01).

**Where we're going.**
1. Review of the set-up branch by the owner, GPT and Arena AI. After that, the owner decides whether to push and merge.
2. Automated PR checks from Auditor Seat 002 are now in this branch (`OPERATING_MANUAL.md` §7). They have not run on GitHub yet, because nothing is pushed.
3. Owner-only items:
   - the history rewrite for PII;
   - `verify_inventory.py` fixes;
   - inventorying the untracked files;
   - whether generated datasets get a separate data licence (CC BY 4.0 or CC0) instead of Apache-2.0.

   The Lean "All rights reserved … Released under Apache 2.0" headers are the standard Mathlib form, not a licence conflict.
4. Research directions. These stay labelled as untested until they are tested:

| Open question | Ledger | What would test it |
|---|---|---|
| Testable forms of the SSRH origin ideas | `SSRH-ORIG-01..07` | One falsifiable statement per row, with a dataset and a threshold stated in advance. Each row's `reconciliation_note` says what would test it. |
| Do the coupled phase/EMA dynamics force both K3 proposal differences to zero? | `CF11` | A proof, or long-horizon runs on many seeds. There is currently no proof or test in the repo. |
| Do the exceptional support, clipping and winner branch persist for all time? | `CF12` | A proof of persistence, or a counterexample trajectory. |
| Do the single-seed AIEF-1.4 results hold on other seeds? | `AUD-SCOPE-1.4` | Re-run the operator/cocycle/controller pipeline on more of the 40 seeds. |
| What explains the ~2e-8 rate-law gap? | `AUD-RATELAW` | Run a δ sweep on the component with the maximum residual (δ in [1e-9, 1e-8)). Finite-difference/rounding error is the most likely cause (the well-resolved components agree within 2.1e-10); finite-time departure, unequal controlling scales and storage rounding are less likely. The gap stays unexplained until the sweep is run. Finite ε accounts for only ~1.6e-12, and a within-step R response is ruled out (E5). |
| Is there a valid slow-pole statement on the closed state? | `AUD-SLOWPOLE` | An analysis on the closed 966-dim state with more than one replay, using one of the methods in the next five rows. |
| Is the 966-dim response a derivative? | `AUD-SLOWPOLE` | One-sided, branch-aware directional maps with the support, gate and controller branch held fixed, instead of a central difference across nonsmooth points. |
| Finite-time growth on the 966-dim state | `AUD-SLOWPOLE` | Singular values of the 500-step map instead of eigenvalues, unless the base state is shown to be fixed or periodic with the matching period. |
| Slowest mode once symmetries are removed | `AUD-SLOWPOLE` | Quotient out the neutral phase-shift mode of each independently rotating component, then recompute. |
| Mode content by block | `AUD-SLOWPOLE` | Report participation weights under at least two coordinate scalings, or a scale-invariant measure. |
| Stability of rates against perturbation size | `AUD-SLOWPOLE` | Repeat at several h values (for example 1e-9 to 1e-5) and report only the modes and rates that stay stable. |
| Does the T_window DID / horizon-confounding claim hold? | `EMP-AIEF14-03` | An audit test of the DID estimand itself. The audits checked only κ(T_w). |
| Do Corr_physical and the topology predictor carry over to random frequencies? | `AUD-CORR-0995`, `AUD-TOPO-OMEGA` | Random and clustered ω cohorts with held-out seeds. The audit's numbers already suggest they do not. |
| Are the results novel? | `AUD-NOVELTY` | A literature review. This is an open owner decision. |
| Is the timestep accurate? | `AUD-TIMESTEP` | A separately versioned dt sweep (for example dt, dt/2, dt/4) reporting topology agreement and trajectory differences. Open item. |
| Under which conditions is B a "conditional scaffold"? | `AUD-B-SCAFFOLD` | State the conditions as a testable claim, then an ablation that varies B with phase/history/EMA fixed. Open item. |
| Are the v4 held-event outputs affected by the end-check bug? | `AUD-V4-HELDEVENT` | Audit the v4.1 candidate, then compare its held rows with the saved v4 outputs. |

**Proposed formal-math steps (proposals, not results; from the Arena AI review):**
- (a) **Done on research branch `research/lean-kn` (2026-10-29; local, not audited).** `dim ker A_{K_n} = C(n,2) − n` is
  proved for all n ≥ 3 for the repository's `inc` (n = 3…6 were proved in `CompleteGraphIncidence.lean`), together with
  full row rank, `m = C(n,2)`, the repository's `rinv` as a right inverse for every n ≥ 3, and `dim ker = 54` for n = 12.
  New Lake project `lean/AIEFProofsKn/` (imports the pinned `lean/AIEFProofs` unchanged); its `check_lean_kn.sh` passes 7/7.
  Connected + non-bipartite (characteristic ≠ 2) is sufficient, not necessary; Mathlib's `Sym2`-indexed `incMatrix` has zero
  diagonal/non-edge columns, so the Mathlib-side version is edge-restricted (`LEAN-KN-01`, `ERRATA_2026-10-28.md` E11).
- (b) Prove the finite one-sided K3 gate identity. At an all-tied K3, for small t > 0 under explicit positivity and gate
  assumptions, `A(x + t·v_c) − A(x) = t·λ_2·v_c`, and the negative direction is not governed by the same scalar. This would
  be tested by a Lean proof, with no calculus, of both the identity and the inequality.
- (c) Prove scalar action on complete-clique controller kernels under explicit branch assumptions (gate on, clipping
  inactive, no controller switch, `A h = 0`, common scale s). This would be tested by a Lean proof of
  `A(x + (1−γΔt)t·h) − A(x) = (1−γΔt)·s·t·h`.
