# Current Scientific & Engineering Status (`CURRENT_STATUS.md`)

**Last Verified:** 2026-10-23 (`Milestone 1` complete; `verify_inventory.py` passing on all `2,898` inventoried objects)

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
| **`Unreviewed`** | `0` | `0` | **`0`** | **100% of files explicitly audited and classified** |

---

## 2. Study-by-Study Status & Authoritative Artifacts (`registry/studies.csv`)

| Study / Component | `artifact_status` | `evidence_scope` | Authoritative Code & Evidence Paths | Critical Pitfalls to Avoid |
|---|---|---|---|---|
| **AIEF-1.3 Causal Ablations ($N=100$)** | `Frozen` | `Controlled experimental result` | `AIEF_1_3_paired_statistics_updated.py` + `runs/c3da1ac707bf` + `runs/73dca37cf93f` | **Do NOT use `paired_seed_analysis/` (`Rejected`)** or pass default CLI flags without explicit cohort paths (root defaults point to duplicate 20-seed runs). |
| **AIEF-1.4 Split-State Memory Ablation** | `Frozen` | `Controlled experimental result` | `AIEF_1_4_memory_ablation_updated.py` + `runs/5a9f093a2fe0/` | Root `AIEF_1_4_memory_ablation_updated.py` (`34d37908...`) is SHA-256 locked by `manifest.json`; **do NOT overwrite** with whitespace-modified `.zip` copy. |
| **AIEF-1.4 Matched-Phase Ablation** | `Frozen` | `Controlled experimental result` | `AIEF_1_4_matched_phase_memory_ablation.py` + **`test_output/`** (`6.2 MB`, 40 seeds) | **Name inversion trap:** `test_output/` is the completed 40-seed study; `aief_1_4_matched_phase_memory_ablation/` (`2.9 KB`) is an aborted 3-file partial run (`Incomplete`). |
| **AIEF-1.4 $T_{\text{window}}$ Sensitivity (`200` cond.)** | `Frozen` / `Supported` | `Controlled experimental result` | `runs/b57562a8ee77/` + `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4.py` | **Do NOT confuse with `Older files/b57562a8ee77/`** (`--baseline-only` pre-run) or `runs_pivot_study/ebfec9a5c419/` (`120`-cond. non-authoritative pilot). |
| **Full-State Tangent & History Cocycle** | `Supported` | `Finite numerical observation` | `aief_1_4_full_state_tangent_operator.py`, `aief_1_4_history_cocycle_test.py`, `aief_1_4_branch_tangent_comparison.py`, `aief_1_4_jacobian_step_convergence/` | **Keep strictly separate from `Rejected` compressed-operator scripts** (`aief_1_4_operator_compression.py` etc.). |
| **Multiplier-Controller Fiber & Intertwining** | `Supported` | `Conditional theorem` / `Finite numerical observation` | `aief_1_4_intertwining_controller 02/` (`40/40`), `aief_1_4_feedback_rank_memory_reduction/`, `aief_1_4_k3_fiber_audit/` (`26` isolated $K_3$ components) | Unnumbered `aief_1_4_intertwining_controller/` is pre-fix (`38/40`, `Superseded`); `01` is a duplicate of `02`. |
| **Lean 4 Controller Kernel Proof** | `Supported` | `Formalized theorem` | `lean/AIEFProofs/AIEFProofs/ControllerFiber.lean` (`0` `sorry`) | Proves algebraic identity $\ker C_{\{2,7\}} = \operatorname{span}\{(1,-1,-1)\}$ only; winner persistence along trajectories is empirical (`CF05`) / open (`CF12`). |
| **Operator Theory Draft Manuscript** | `Exploratory` | `Conditional theorem` | `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md` | **Caveat `CAVEAT-MS-8.4`:** Corollary 8.4 ambient left orthogonality $V^\top D\mathcal{A}_\varepsilon(x_G) = s_k V^\top$ holds at $x_G = x_{\text{common}}\mathbf{1}$, **not** across general fiber perturbations $x_0\mathbf{1}+h$. |
| **Modular Platform `v1_analysis_v4`** | `Supported` | `Implementation identity` | `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/` | Supersedes `workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f/`. Same-host equivalence vs monolithic code is exact (`0.000e+00`). |
| **Retired Spectral Compression & K3 Subgraph Scan** | `Rejected` | `Finite numerical observation` | `aief_1_4_operator_compression.py` (`24,323.8%` leakage), `aief_1_4_slow_subspace_projection.py` (`7.5e35`), `aief_1_4_observable_jacobian.py`, `aief_1_4_coupling_lock_audit.py`, `aief_1_4_k3_structure_scan.py` (`856` subgraphs) | Preserved byte-for-byte unmodified as negative methodological evidence; never cite as positive support. |
