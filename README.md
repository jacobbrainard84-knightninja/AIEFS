# AIEFS — Adaptive Incidence & Emergent Fiber Systems

> **Authoritative Repository Front Door (`Milestone 1` Status Layer Live)**  
> Every tracked file (`2,760` files) and `.zip` archive member (`138` entries = `2,898` total items) in this repository has been SHA-256 inventoried and classified along **two orthogonal axes**: **`artifact_status`** (*can this artifact be relied on?*) and **`evidence_scope`** (*what level of mathematical or empirical generality does it establish?*).
>
> **Start here before reading legacy root scripts or draft manuscripts:**
> 1. **[`CURRENT_STATUS.md`](CURRENT_STATUS.md)** — Exact matrix of what is **Frozen / Supported**, **Conditional**, **Exploratory**, **Superseded**, **Incomplete**, and **Rejected** (including explicit caveats on draft `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md`).
> 2. **[`REPRODUCING.md`](REPRODUCING.md)** — Exact commands, virtual environment setup, `PYTHONPATH` flags, SHA-256 verification, and cross-`glibc` floating-point notes to reproduce every core benchmark from scratch.
> 3. **[`history/timeline.md`](history/timeline.md)** — Chronological intellectual history from pre-AIEF origins through AIEF 1.0–1.4, falsifications, and Lean 4 formalization.
> 4. **[`registry/`](registry/README.md)** — Machine-validated CSV ledgers (`artifacts.csv`, `studies.csv`, `claims.csv`, `supersessions.csv`, `relocation_map.csv`).

---

## Core Scientific Takeaways (Strictly Scoped)

1. **Multi-Seed Causal Persistence (`AIEF-1.3`, `Frozen` / `Controlled experimental result`):**  
   Across **$N = 100$ disjoint paired seeds** (`runs/c3da1ac707bf` + `runs/73dca37cf93f`, `overlap = 0`), destroying historical alignment via `shuffle_R` strongly degrades persistent topology ($\bar{\Delta} D_B = +0.305909$, 95% CI $[0.298939, 0.313030]$, $d_z = 8.434$), and removing adaptive feedback (`no_mu`) degrades topology ($\bar{\Delta} D_B = +0.271061$, $d_z = 4.900$), whereas removing constant transmission delay alone (`no_delay`) has a slight negative shift ($\bar{\Delta} D_B = -0.027424$).
2. **Distributed Memory Reconstruction & Matched-Phase Counterfactuals (`AIEF-1.4`, `Frozen` / `Controlled experimental result`):**  
   Resetting the adaptive edge matrix $B$ at the split time (`reset_B` in `runs/5a9f093a2fe0`, 40 seeds × 7 branches) **reconstructs the mature topology nearly identically**, refuting the early hypothesis (`S01`) that $B$ is a lone memory bottleneck. Matched-phase counterfactuals in **`test_output/`** (`40` seeds) confirm delayed phase/EMA history mediates recovery independently of instantaneous phase mismatch. *(Note: root `aief_1_4_matched_phase_memory_ablation/` is an aborted 3-file partial attempt; **`test_output/`** holds the completed 40-seed dataset.)*
3. **Dual-Horizon $T_{\text{window}}$ Sensitivity (`runs/b57562a8ee77` + `Analysis v4`, `Frozen` & `Supported` / `Controlled experimental result`):**  
   Across `200` conditions (`40` seeds × $\rho \in \{0.50, 0.75, 1.00, 1.50, 2.00\}$), `AIEF_1_4_Twindow_sensitivity_analysis_v4.py` decouples fixed physical recovery horizons from normalized EMA-window scaling via paired difference-in-differences.
4. **Piecewise-Affine Controller Fiber Geometry & Lean 4 Proof (`Supported` / `Formalized theorem` & `Conditional theorem`):**  
   - **Machine-Checked in Lean 4 (`lean/AIEFProofs/AIEFProofs/ControllerFiber.lean`, `0` `sorry`):** For the 2×3 active row-controller incidence matrix $C_{\{2,7\}}$, $\ker C_{\{2,7\}} = \operatorname{span}\{(1,-1,-1)\}$.
   - **Conditional Analytic Limit (`CF09`):** One-sided proposal equalization implies convergence of selected $K_3$ branch matrices **conditional on persistent strict winner inequalities**; infinite-time autonomous convergence (`CF11`, `CF12`) remains an **open conjecture**.
   - **Manuscript Scope Warning (`CAVEAT-MS-8.4`):** In draft `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md`, Corollary 8.4's ambient left-covector orthogonality holds at edge-uniform points $x_G = x_{\text{common}}\mathbf{1}$, **not** at general kernel perturbations $x_0\mathbf{1}+h$ (see [`audits/scientific/SCIENTIFIC_CLASSIFICATION_AND_REJECTIONS_AUDIT.md`](audits/scientific/SCIENTIFIC_CLASSIFICATION_AND_REJECTIONS_AUDIT.md)).

---

## Repository Navigation Map

| Directory / File | Role & Status |
|---|---|
| [`CURRENT_STATUS.md`](CURRENT_STATUS.md) | Complete status table across all studies, artifacts, caveats, and retired hypotheses |
| [`REPRODUCING.md`](REPRODUCING.md) | One-command conservation check + step-by-step reproduction commands |
| [`registry/`](registry/README.md) | `artifacts.csv` (`2,898` rows), `studies.csv`, `claims.csv`, `supersessions.csv`, `relocation_map.csv` |
| [`audits/github_reconciliation/`](audits/github_reconciliation/GITHUB_TREE_AND_ZIP_RECONCILIATION.md) | Forensics on all 3 `.zip` archives, recovered lineage CSVs/docs from `workspace-019ff402.zip`, numbered `01`/`02` folders, and all 19 `runs*` directories |
| [`audits/scientific/`](audits/scientific/SCIENTIFIC_CLASSIFICATION_AND_REJECTIONS_AUDIT.md) | Separation of valid full-state tangent/cocycle analyses from rejected 8D POD compression & K3 scan; exact derivation of Corollary 8.4 defect; revalidated summary tables |
| [`audits/engineering/`](audits/engineering/PATH_AND_LOCK_DEPENDENCY_AUDIT.md) | `authority.py` lock map, AST scan across all `165` `.py` scripts, `verify_inventory.py`, and cross-`glibc` floating-point analysis |
| [`docs/architecture/EPISTEMIC_GOVERNANCE_AND_LAYOUT.md`](docs/architecture/EPISTEMIC_GOVERNANCE_AND_LAYOUT.md) | Two-axis governance rules and 7-stage conservative migration roadmap |
| [`AIEF_Experiments/aief_modular_platform_v1_analysis_v4/`](AIEF_Experiments/aief_modular_platform_v1_analysis_v4/) | **Canonical modular platform (`Supported`)** — replaces older `workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f/` |
| [`lean/AIEFProofs/`](lean/AIEFProofs/) | **Canonical Lean 4 proof package (`Supported`)** — `ControllerFiber.lean` + lock hash ledger |

---

## Quick Integrity Check

Run the zero-dependency conservation and lock verifier from the repository root at any time:

```bash
python3 audits/engineering/verify_inventory.py
```
