# GitHub Working Tree, `.zip` Archive, Sibling Directory & Run Cohort Reconciliation

**Milestone 1 — Stage 1 & Stage 2 Forensic Reconciliation Report**  
**Base Commit Audited:** `e47bad150792425eb8e962ff636c69289eedd8b1` (`main` -> `arena/d4a487cc-aiefs`)  
**Total Audited Objects:** `2,760` tracked files (`1,218.4 MB`) + `138` member files across `3` `.zip` archives = `2,898` hash-verified entries (`360` duplicate SHA-256 groups)

---

## Executive Summary

Before moving or reorganizing any file in `jacobbrainard84-knightninja/AIEFS`, every tracked file, archive snapshot, numbered sibling output folder, and hex-named simulation directory was hashed (`SHA-256`) and cross-checked against run manifests and primary development logs (`Project Histories/Project Lead History 01.pdf`–`10.pdf`).

Five critical discoveries govern safe reorganization in Stage 4:

1. **Two `.zip` archives are 100% SHA-256 duplicates of unpacked folders (`Superseded`), whereas `workspace-019ff402-3611-7903-99ce-0679e00cb830.zip` contains 15 files missing from the working tree AND expanded revisions of 4 core Markdown synthesis documents (`Supported`).** Overwriting root files blindly from `workspace-019ff402.zip` would have **corrupted** `AIEF_1_4_memory_ablation_updated.py`, whose **root** digest (`34d37908...`) matches frozen `runs/5a9f093a2fe0/manifest.json` (`source_sha256`), whereas the `.zip` copy has trailing blank-line formatting edits (`4b792e88...`).
2. **All 15 `.zip`-only lineage/claim/report files and all 4 expanded Markdown revisions from `workspace-019ff402.zip` have been non-destructively unpacked under `audits/github_reconciliation/recovered_from_workspace_019ff402/`**, accompanied by exact unified `.diff` patches against root files (`diffs_vs_root/*.diff`) and SHA-256 provenance (`PROVENANCE.json`).
3. **`test_output/` (`6.2 MB`, 10 files) is the completed 40-seed `matched_phase_ablation` study output**, whereas root `aief_1_4_matched_phase_memory_ablation/` (`2.9 KB`, 3 files) is an aborted early partial attempt (`Incomplete`).
4. **Across the 19 `runs*` / `Older files` directories**, 10 directories (`runs/87dfe5798954` + 9 sibling dirs) are **bit-identical deterministic reruns** of the same 20 seeds (`CSV sha256 = d71bb071...`). Root `paired_seed_analysis/` erroneously pooled two of those identical 20-seed runs (`valid=40/40`, overlap `= 20`, `Rejected`), and was replaced by the true disjoint $50+50 = 100$-seed production cohorts **`runs/c3da1ac707bf` + `runs/73dca37cf93f`** (`overlap = 0`, `Frozen`).
5. **`Older files/b57562a8ee77/` is NOT a copy of `runs/b57562a8ee77/`**: `Older files/b57562a8ee77/` was an earlier `--baseline-only` pre-grid verification certificate run, whereas `runs/b57562a8ee77/` is the complete 200-condition (`40 seeds x 5 rho`) frozen $T_{\text{window}}$ sensitivity oracle.

---

## 1. Three `.zip` Archives vs. Working Tree (`zip_vs_tree_comparison.csv`)

| Archive Path | Entries | Identical to Tree | Zip-Only | Divergent | Classification & Findings |
|---|---:|---:|---:|---:|---|
| `workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f.zip` | `29` | `29` (`100%`) | `0` | `0` | **`Superseded` duplicate.** Every byte matches unpacked `workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f/`, which is the older pre-authority-lock modular v1 scaffold missing `authority.py`, `AIEF_1_4_Twindow_sensitivity_analysis_v4.py`, `ANALYSIS_V4_DESIGN.md`, and `PROJECT_INTEGRATION_MAP.md`. |
| `AIEF_Experiments/aief_modular_platform_v1_analysis_v4.zip` | `39` | `39` (`100%`) | `0` | `0` | **`Superseded` archive duplicate.** Every byte matches unpacked `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/` (`Supported` canonical modular platform). |
| `workspace-019ff402-3611-7903-99ce-0679e00cb830.zip` | `70` | `45` | `15` | `10` | **`Frozen` lineage snapshot.** Holds 15 unique lineage/registry/report files + 10 files that diverge from root in two opposite directions (detailed below). |

### Detailed Audit of the 15 `ZIP_ONLY` Files Recovered from `workspace-019ff402.zip`

All 15 files were extracted verbatim into `audits/github_reconciliation/recovered_from_workspace_019ff402/zip_only_files/`:

- **Lineage & Claim Registries (Critical Provenance Recovery):**
  - `AIEF_1_4_CONTROLLER_FIBER_CLAIM_REGISTRY.csv` — Authoritative 12-row formal scope ledger (`CF01`–`CF12`) explicitly distinguishing exact polyhedral/implementation theorems (`CF01`–`CF04`), finite replay facts (`CF05`, `CF10`), conditional operator identities (`CF06`–`CF09`), and open conjectures (`CF11`, `CF12`), including the exact caveat on `CF08` (*"Pointwise left eigenvectors do not automatically form a fixed or moving cocycle dual"*).
  - `AIEF_1_4_CONTROLLER_FIBER_FREEZE_MANIFEST.json` — SHA-256 freeze manifest for the controller-fiber claim package.
  - `AIEF_1_4_analysis_lineage.csv`, `AIEF_1_4_freeze_analysis_lineage.py`, `AIEF_1_4_lineage_freeze_manifest.json` — Script-to-output lineage registry across AIEF 1.4 analyses.
- **Historical Planning & Prompt Notes:**
  - `AIEF_1_4_memory_ablation_plan.md`, `AIEF_1_4_operator_cocycle_closure_note.md`, `AIEF_MATCHED_PHASE_CODING_AGENT_PROMPT.md`, `AIEF_1_4_stationarity_perturbation_analysis.py`.
- **Saved Text Reports (`uploads/`):**
  - `uploads/channel_invariance_report.txt`, `uploads/exceptional_tangent_report.txt`, `uploads/face_spectrum_report.txt`, `uploads/trajectory_recovery_report.txt`, plus duplicate copies of `uploads/Results.pdf`, `results_embedded.docx`, and `results_embedded.bin`.

### Detailed Audit of the 10 `DIVERGENT` Files in `workspace-019ff402.zip`

| File Name | Root SHA-256 (Prefix) | Zip SHA-256 (Prefix) | Authoritative Version & Exact Reason |
|---|---|---|---|
| `AIEF_1_4_memory_ablation_updated.py` | `34d37908764a` | `4b792e88c2cf` | **ROOT IS FROZEN AUTHORITY.** `runs/5a9f093a2fe0/manifest.json` records `"source_sha256": "34d37908764a..."`. Zip version only changed whitespace/blank lines; overwriting root would break manifest verification! |
| `AIEF_1_3_paired_statistics_updated.py` | `3ad52f59...` | `7810e0ef...` | **ZIP HAS CLEANER CLI DEFAULTS.** Root defaults hardcoded `/home/deck/AI_Programs/SSRH/runs/87dfe5798954` + `5a338105785a`; zip updated defaults to relative `runs/c3da1ac707bf` + `runs/73dca37cf93f`. Identical mathematical logic when cohort paths are passed via CLI. |
| `AIEF_1_3_paired_statistics.py` | `c8f21401...` | `8892c630...` | Same `/home/deck/...` -> relative `runs/...` default path update (`Superseded` by `*_updated.py`). |
| `AIEF_1_3_closure_diagnostics_updated.py` | `412b8e20...` | `f1a90433...` | Same `/home/deck/...` -> relative `runs/c3da1ac707bf` + `runs/73dca37cf93f` default path update. |
| `AIEF_1_3_closure_diagnostics.py` | `9e8c3312...` | `2049e772...` | Same `/home/deck/...` -> relative path update (`Superseded`). |
| `AIEF_1_4_trajectory_recovery_equivalence.py` | `1e4471b2...` | `6f092c11...` | Minor internal helper rename; root matches tracked `aief_1_4_trajectory_recovery_equivalence/` output. |
| `AIEF_1_4_OPERATOR_COCYCLE_THOUGHT_TREE.md` | `468 lines` | `733 lines` | **ZIP HAS EXPANDED REVISION (+265 lines)** adding later controller-fiber & proposal-equalization closure sections; saved to `newer_zip_markdown/`. |
| `AI_AGENT_HANDOFF_PROMPT.md` | `548 lines` | `600 lines` | **ZIP HAS EXPANDED REVISION (+52 lines)** adding claim-scope guardrails; saved to `newer_zip_markdown/`. |
| `AIEF_1_4_CONDITIONAL_PROPOSAL_EQUALIZATION_THEOREM.md` | `596 lines` | `650 lines` | **ZIP HAS EXPANDED REVISION (+54 lines)** tightening boundary/tie remarks; saved to `newer_zip_markdown/`. |
| `AIEF_1_4_PROPOSAL_EQUALIZATION_BRIDGE_INTERPRETATION.md` | `302 lines` | `354 lines` | **ZIP HAS EXPANDED REVISION (+52 lines)** clarifying non-asymptotic replay scope; saved to `newer_zip_markdown/`. |

---

## 2. Numbered Sibling Output Directories (`01` / `02` Disambiguation)

| Sibling Group | Directory Variant | Files | Finding & Canonical Choice |
|---|---|---:|---|
| **Intertwining Controller** | `aief_1_4_intertwining_controller/` | `6` | **`Superseded` pre-fix output:** reports `Multiplicity matches: 38/40` due to strict floating-point edge-tie tolerance bug prior to safeguard fix. |
| | `aief_1_4_intertwining_controller 01/` | `6` | **`Superseded` exact duplicate:** byte-for-byte SHA-256 identical to `02`. |
| | **`aief_1_4_intertwining_controller 02/`** | **`6`** | **`Supported` canonical output:** post-fix verification matching `40/40` seeds (`100%`). |
| **Feedback Rank Reduction** | `aief_1_4_feedback_rank_memory_reduction 01/` | `8` | **`Superseded` earlier snapshot** missing 3 diagnostic CSV/figure files. |
| | **`aief_1_4_feedback_rank_memory_reduction/`** | **`11`** | **`Supported` canonical complete output bundle.** |
| **Fiber Coordinate Controller** | **`aief_1_4_fiber_coordinate_controller/`** | **`7`** | **`Supported` canonical output bundle.** |
| | `aief_1_4_fiber_coordinate_controller 01/` | `7` | **`Superseded` duplicate numbered copy.** |
| **K3 Fiber Controller** | **`aief_1_4_k3_fiber_controller/`** | **`7`** | **`Supported` canonical output bundle** across the 26 isolated $K_3$ seed-components. |
| | `aief_1_4_k3_fiber_controller 01/` | `7` | **`Superseded` duplicate numbered copy.** |

---

## 3. Matched-Phase Study Directory Inversion (`test_output/` vs `aief_1_4_matched_phase_memory_ablation/`)

A critical trap for naive directory cleanup:
- **`test_output/` (`Frozen`, `10` files, `6,247,891` bytes):** Despite its generic scratch-sounding name, `test_output/` holds the **complete, authoritative 40-seed `AIEF_1_4_matched_phase_memory_ablation.py` study dataset** (`matched_phase_branch_diagnostics.npz`, `matched_phase_paired_contrasts.csv`, `matched_phase_recovery_summary.csv`, `matched_phase_scalar_summary.csv`, `matched_phase_report.txt`, `analysis_manifest.json`) because the CLI script defaulted `--output-dir` to `test_output`!
- **`aief_1_4_matched_phase_memory_ablation/` (`Incomplete`, `3` files, `2,914` bytes):** Contains only an aborted early partial run before `--output-dir` produced the full 40-seed run in `test_output/`.

---

## 4. Complete Reconciliation of All 19 `runs*` & `Older files/` Directories (`runs_cohort_reconciliation.csv`)

| Directory | Master Seed | Seeds | CSV Rows | Primary CSV SHA-256 (`[:12]`) | Status | Forensic Role |
|---|---:|---:|---:|---|---|---|
| **`runs/5a9f093a2fe0`** | `20260714` | `40` | `280` | `f4bcdd140379` | **`Frozen`** | **AIEF-1.4 split-state memory ablation baseline authority** (`authority.py` locked). |
| **`runs/b57562a8ee77`** | `20260714` | `40` | `800` | `94c9d3e1...` | **`Frozen`** | **AIEF-1.4 200-condition $T_{\text{window}}$ sensitivity oracle** (`40 seeds x 5 rho x 4 branches`). |
| **`runs/c3da1ac707bf`** | `20260701` | `50` | `200` | `21f7b9a4...` | **`Frozen`** | **AIEF-1.3 Production Cohort A** (`50` unique seeds; `0` overlap with Cohort B). |
| **`runs/73dca37cf93f`** | `20260702` | `50` | `200` | `8c44e01b...` | **`Frozen`** | **AIEF-1.3 Production Cohort B** (`50` unique seeds; `A + B = 100` disjoint paired seeds). |
| `Older files/b57562a8ee77` | `20260714` | `40` | `0` | *(none)* | `Superseded` | Pre-grid `--baseline-only` certificate run (`Project Lead History 09, p. 254`). |
| `runs_pivot_study/ebfec9a5c419` | `20260714` | `40` | `480` | *(pilot)* | `Exploratory` | Reduced 120-condition pilot explicitly tagged `"freezeable": false` in `PIVOT_STUDY_LABEL.json`. |
| `runs_aief14_smoke/ae136b3a165b` | `20260714` | `2` | `14` | *(smoke)* | `Exploratory` | 2-seed smoke verification run. |
| `runs/a937d5e96efb` | — | — | `0` | *(none)* | `Incomplete` | Aborted partial/lock directory with no completed outputs. |
| `runs/87dfe5798954` + 9 `runs/*` dirs + `Older files/87dfe5798954` (`11` dirs total) | `20260602` | `20` | `80` | `d71bb071...` | `Superseded` | **11 bit-identical copies/reruns** of the early 20-seed cohort (`seeds 42..19042`). Pooling two of these produced the pseudoreplicated `paired_seed_analysis/` (`valid=40/40`, `Rejected`). |
