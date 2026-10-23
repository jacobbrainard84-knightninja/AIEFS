# Chronological History of the AIEFS Research Program

**Cross-Referenced Primary Sources:** `AIEF_HISTORIC_UNFOLDING.md`, `AIEF_1_4_superseded_claims.csv`, `Project Origins/*.pdf`, `Papers/*.pdf`, `Project Histories/Project Lead History 01.pdf`–`10.pdf` (`10,723` pages total), and frozen run manifests in `runs/`.

---

## Overview: How the Scientific Question Evolved

AIEFS began as an exploratory dynamical-systems hypothesis asking whether coupled oscillators with transmission delays could spontaneously form and retain resonant coupling topologies. Across four distinct eras of falsification, statistical hardening, operator-theoretic analysis, and formal verification, the project repeatedly **retired appealing over-interpretations when confronted with counterfactual experiments and exact numerical audits**, progressively narrowing its focus onto reproducible multi-seed causal effects and sharply scoped piecewise-linear admissibility geometry.

---

## Era 0 — Pre-AIEF Origins: Delay-Coupled Resonance & Gap/Phase Scans

- **Primary Artifacts:** `Project Origins/Solar System Resonance Hypothesis Delay‑Coupled Dynamics draft 01–04.pdf`, `gap_phase_scan_v9.py` (`Exploratory` / `Conjecture`).
- **Central Question:** Can delayed phase coupling and incidence constraints select persistent low-integer or structured coupling patterns without hand-coded target graphs?
- **Outcome & Transition:** Exploratory toy hypergraph and phase-gap scans motivated formalizing an explicit, seeded discrete-time simulation protocol with capacity-projected adaptive weights (`AIEF 1.0`).

---

## Era 1 — AIEF 1.0 to 1.3: Adaptive Persistence, Pseudoreplication Audit & Disjoint $N=100$ Validation

- **Primary Artifacts:** `AIEF_1_0_*.py`, `AIEF_1_1_*.py`, `AIEF_1_2_*.py`, `runs/c3da1ac707bf`, `runs/73dca37cf93f`, `AIEF_1_3_paired_statistics_updated.py`, `aief_1_3_closure_diagnostics/` (`Project Lead History 01.pdf`, pp. 535–555).
- **What Happened:**
  1. **Early 20-Seed Reproducibility Runs (`runs/87dfe5798954` + 9 sibling dirs):** Ten production executions with `master_seed=20260602` (`seeds 42..19042`) produced bit-identical outputs (`CSV sha256 = d71bb071...`), confirming deterministic execution on the host platform.
  2. **Catching Pseudoreplication (`paired_seed_analysis/` -> `Rejected`):** Root `paired_seed_analysis/` pooled two of those 20-seed runs as if they were 40 distinct seeds (`valid=40/40`, `seed_overlap = 20`). Self-audit caught this defect (`Project Lead History 01.pdf, p. 545`), leading to `AIEF_1_3_paired_statistics_updated.py` with mandatory seed-disjointness gates.
  3. **Freeze-Grade Disjoint $50 + 50 = 100$-Seed Cohorts (`runs/c3da1ac707bf` + `runs/73dca37cf93f` -> `Frozen`):**
     - `shuffle_R` degrades persistent topology strongly: $\bar{\Delta} D_B = +0.305909$, 95% CI $[0.298939, 0.313030]$, $d_z = 8.434$.
     - Removing adaptive feedback (`no_mu`) degrades persistence ($\bar{\Delta} D_B = +0.271061$, $d_z = 4.900$), whereas removing constant transmission delay alone (`no_delay`) shifts $D_B$ slightly negatively ($\bar{\Delta} D_B = -0.027424$, $d_z = -0.756$).

---

## Era 2 — AIEF 1.4 Split-State Ablation, Spectral Falsification & Matched-Phase Counterfactuals

- **Primary Artifacts:** `runs/5a9f093a2fe0`, `AIEF_1_4_memory_ablation_updated.py`, `test_output/`, `aief_1_4_full_state_tangent_operator.py`, `AIEF_1_4_superseded_claims.csv` (`Project Lead History 02.pdf`–`07.pdf`).
- **Major Scientific Turning Points:**
  1. **Falsification of Single-Carrier `B` Memory (`S01`, `runs/5a9f093a2fe0`):** Splitting 40 mature trajectories into 7 counterfactual branches revealed that resetting the adaptive weight matrix (`reset_B`) **still recovers the pre-split mature topology nearly identically** because the delayed oscillator phase/EMA history re-imprints the same proposal rankings onto the admissibility map!
  2. **Matched-Phase Ablation (`test_output/` -> `Frozen`):** Controlling directly for instantaneous split-time phase alignment across 40 seeds confirmed that historical delayed phase/EMA trajectories mediate topological recovery (`EMP-AIEF14-02`). *(Note: CLI default output directory wrote this complete bundle to `test_output/`, while root `aief_1_4_matched_phase_memory_ablation/` retained an aborted 3-file partial attempt.)*
  3. **Separation Within the Spectral Program (`Supported` Full-State Cocycle vs. `Rejected` 8D Compression & K3 Scan):**
     - **Survived (`Supported`):** Full-state finite-step tangent operators and time-ordered non-autonomous history cocycles (`aief_1_4_full_state_tangent_operator.py`, `aief_1_4_history_cocycle_test.py`) accurately track perturbation dynamics.
     - **Falsified & Retired (`Rejected`):** Autonomous 8D POD slow-subspace projections suffered **`24,323.8%` off-subspace leakage** (`aief_1_4_operator_compression.py`) and variance blow-up **`7.5e35`** (`aief_1_4_slow_subspace_projection.py`); coarse finite-difference observable Jacobians (`eps=1e-8`) crossed true active-tie margins (`4.44e-14`); and `aief_1_4_k3_structure_scan.py` overcounted `856` triangle subgraphs rather than the **`26` true isolated $K_3$ connected components** across the 40 seeds.

---

## Era 3 — Multiplier-Controller Fiber Geometry, Proposal Equalization & Lean 4 Proof

- **Primary Artifacts:** `lean/AIEFProofs/AIEFProofs/ControllerFiber.lean`, `AIEF_1_4_CONDITIONAL_PROPOSAL_EQUALIZATION_THEOREM.md`, `aief_1_4_intertwining_controller 02/`, `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md` (`Project Lead History 08.pdf`–`10.pdf`).
- **Outcomes & Sharp Scope Boundaries:**
  1. **Piecewise-Affine Controller Fiber Algebra (`CF01`–`CF08`):** On strict row-scale winner neighborhoods, the safeguarded admissibility map is locally affine along multiplier-controller kernels; for the exceptional $K_3$ with winners $(7,2,7)$, $\ker C_{\{2,7\}} = \operatorname{span}\{(1,-1,-1)\}$—**formally verified in Lean 4 (`ControllerFiber.lean`, 0 `sorry`)**.
  2. **Post-Fix Intertwining Verification (`aief_1_4_intertwining_controller 02/`):** Fixing floating-point tie classification brought empirical multiplicity matching from `38/40` seeds (in unnumbered `aief_1_4_intertwining_controller/`) to **`40/40` seeds**.
  3. **Critical Scope Guardrails:**
     - **Draft Manuscript Corollary 8.4 Caveat (`CAVEAT-MS-8.4`):** Ambient left orthogonality $V^\top D\mathcal{A}_\varepsilon(x_G) = s_k V^\top$ holds at edge-uniform points $x_G = x_{\text{common}}\mathbf{1}$, **not** across general fiber perturbations $x_0\mathbf{1}+h$.
     - **Open Conjectures (`CF11`, `CF12`):** Finite-horizon replay shows small late proposal differences, and `CF09` proves the conditional one-sided matrix limit, but infinite-time autonomous convergence of proposal differences remains **open**.

---

## Era 4 — Dual-Horizon $T_{\text{window}}$ Oracle, Modular Platform v1 / Analysis v4 & Conservative Governance

- **Primary Artifacts:** `aief_experiment_engine_v1.py`, `AIEF_1_4_Twindow_sensitivity.py`, `runs/b57562a8ee77/`, `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/`, `registry/*`, `audits/*`.
- **Outcomes:**
  1. **Dual-Horizon $T_{\text{window}}$ Oracle (`runs/b57562a8ee77`, 200 conditions) + `Analysis v4`:** Resolved timescale confounding by contrasting fixed physical evaluation windows against normalized EMA horizons via paired bootstrap DID.
  2. **SHA-256 Authority Lock & Modular Driver (`aief_modular`):** Cryptographically pinned frozen baseline `5a9f093a2fe0` and root legacy sources (`verify_authority_lock`), verified bitwise `0.000e+00` same-host equivalence across all `344` arrays, and established the non-destructive registry and governance layer in **Milestone 1**.
