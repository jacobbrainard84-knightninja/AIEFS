# Independent Audit Census of False, Tautological, and Redundant Self-Tests Across AIEFS Analysis Scripts (Revision 2)

**Auditor / Researcher ID:** Researcher 0282416  
**Auditor Seat Mandate:** Auditor Seat 002 Lead Direction (dated 2026-11-20, 5:15 PM MST)  
**Target Repository:** `jacobbrainard84-knightninja/AIEFS`  
**Target Base Commits Audited:** `main` @ `0a6a2f62ea9af147cac60a7be30d85d6b37fe52a` and `7ec6011d5161e7dd105b6db841ed91b6196e88d4` (verified identical across all in-scope analysis scripts)  
**Census Scope:** All analysis and driver Python scripts at repo root and under `AIEF_Experiments/` (excluding `Older files/` and `Historical files/`). Total audited scripts: 114 Python files.

---

## 1. Executive Summary & Audit Mandate Reconciliation

Per lead direction from **Auditor Seat 002** (DIRECTION-2), this audit census has been completely rebuilt directly from the grounded source code on `main`, strictly eliminating extrapolated memory rows and grounding every single entry on verifiable line numbers, function signatures, verbatim code quotes, execution/reading classification, and rigorous negative control analysis.

In addition, as instructed by Seat 002, static integrity items previously assigned to GPT-6 and Researcher 026 were absorbed:
1. **Registry Path Integrity (`registry/studies.csv`)**: Exhaustive resolution scan of all `canonical_entrypoints` and `canonical_evidence_paths` tokens against tracked repository trees, with exact git commit provenance tracing via `git log --all --follow`.
2. **Study Entrypoint Importability**: Verification of whether each resolved canonical entrypoint imports cleanly from a clean checkout under standard documented invocation.

---

## 2. Methodology, Taxonomy, & Rebuilt Census Breakdown

Across the 114 in-scope files, all self-test entry points were systematically extracted and audited:
- `aief_1_4_two_channel_alignment_v4.py:293` (`run_self_test()`)
- `aief_1_4_two_channel_alignment_v5.py:409` (`run_self_test()`)
- `AIEF_1_4_proposal_equalization_bridge_analysis.py:198` (`synthetic_self_test()`)
- `AIEF_1_4_proposal_equalization_bridge_analysis_v1_1.py:237` (`synthetic_self_test()`)
- `AIEF_1_4_matched_phase_memory_ablation.py:2310` (`run_self_test()`, Tests 1–16)
- `AIEF_1_4_Twindow_sensitivity.py:574` (`validate_engine_contract()`)
- `aief_experiment_engine_v1.py:1755-2670` (`exact_array_equal_with_nan` and `run_baseline_equivalence()`)
- `AIEF_1_4_Twindow_sensitivity_analysis_v3.py:1360` (`validate_run()`)

### Taxonomy Definitions
- **`SELF_COPY`**: The test synthesizes or defines an intermediate variable immediately prior to assertion using the exact formula being tested, bypassing runtime operators and state. A bug in the production operator cannot fail this test.
- **`PARTIAL_REDUNDANT`**: An isolated helper test on random or synthetic data that verifies internal Python consistency or duplicate code across script versions, rather than physical trajectory state.
- **`KNOWN_DEFECT`**: Historically pinned defect in pinned legacy code where a false mathematical claim passes due to hardcoded fixtures or flawed operator logic (e.g. ERRATA E19).
- **`REAL_OPERATOR`**: Directly exercises genuine runtime simulation operators, intervention engines, or strict zero-tolerance (`rtol=0.0, atol=0.0`) bit-for-bit trajectory regression checks.

### Rebuilt Census Statistics (49 Total Verified Checks)
- **`REAL_OPERATOR`**: 33 checks (67.3%)
- **`SELF_COPY`**: 7 checks (14.3%)
- **`PARTIAL_REDUNDANT`**: 6 checks (12.2%)
- **`KNOWN_DEFECT`**: 3 checks (6.1%)

---

## 3. Top 5 Ranked Findings (Grounded Line-by-Line)

### Finding 1: Pure Tautology in Proposition 3.1 Proposal Identity Check
- **File**: `aief_1_4_two_channel_alignment_v5.py:459-467`
- **Class**: `SELF_COPY` | **Claim ID**: `EMP-AIEF14-01`, `PROP-EQUALIZATION`
- **Verbatim Code Quote**:
  ```python
  c0_test = 0.999
  a_R_test = 0.01
  b_test = np.array([0.5, 0.3, 0.1])
  r_test = np.array([0.02, 0.01, 0.005])
  d_test = c0_test * b_test + a_R_test * r_test
  prop_check = test_proposal_identity(d_test, c0_test, b_test, a_R_test, r_test)
  assert prop_check["identity_passes"]
  ```
- **Operator Bypass**: `test_proposal_identity` computes `errors = np.abs(d - (c0 * b + a_R * r))`. Because `d_test` is created directly as `c0_test * b_test + a_R_test * r_test`, this evaluates $X - X = 0$. The check does not invoke `augmented.base_intermediates` or test simulation arrays.
- **Verification Execution**: **Ran**. Running `python3 aief_1_4_two_channel_alignment_v5.py --self-test` prints `[PASS] Exact proposal identity d_n = c0 * b_n + a_R * r_n`.
- **Negative Control**: Mutating production proposal logic in `augmented.base_intermediates` leaves this self-test reporting `[PASS]`. Mutating line 464 to `d_test = c0_test * b_test + a_R_test * r_test + 0.5` causes `prop_check["identity_passes"]` to evaluate `False` with max error 0.5, proving that the self-test is sensitive only to its own local definition and completely blind to the engine.

### Finding 2: Pure Tautology in Proposition 5.1 Recurrence Check
- **File**: `aief_1_4_two_channel_alignment_v5.py:469-478`
- **Class**: `SELF_COPY` | **Claim ID**: `EMP-AIEF14-01`, `PROP-EQUALIZATION`
- **Verbatim Code Quote**:
  ```python
  lambda_test = np.array([0.998, 0.5, 0.998])
  r_next_test = np.array([0.015, 0.008, 0.003])
  d_next_test = lambda_test * d_test + a_R_test * r_next_test
  rec_check = test_proposal_recurrence(
      d_next_test, lambda_test, d_test, a_R_test, r_next_test
  )
  assert rec_check["identity_passes"]
  ```
- **Operator Bypass**: `d_next_test` is computed from the exact linear recurrence formula being tested. No physical state or simulation data is exercised.
- **Verification Execution**: **Ran**. Output: `[PASS] Exact proposal recurrence identity`.

### Finding 3: Tautological Projected Weight Check (Proposition 4.1)
- **File**: `aief_1_4_two_channel_alignment_v5.py:480-485`
- **Class**: `SELF_COPY` | **Claim ID**: `EMP-AIEF14-01`, `PROP-EQUALIZATION`
- **Verbatim Code Quote**:
  ```python
  s7_test = np.array([0.9, 0.9, 0.9])
  b_next_test = s7_test * d_test
  pw_check = test_projected_weight_identity_fixed_left(b_next_test, s7_test, d_test)
  assert pw_check["identity_passes"]
  ```
- **Operator Bypass**: Multiplies `d_test` by `s7_test` one line prior to calling `test_projected_weight_identity_fixed_left`, which checks `np.abs(b_next - s_7 * d_L) < tol`.
- **Verification Execution**: **Ran**. Output: `[PASS] Exact projected weight identity (fixed-left)`.

### Finding 4: Trivial Hardcoded Modulo Phase Separation Check
- **Files**: `aief_1_4_two_channel_alignment_v4.py:330-338` & `v5.py:448-457`
- **Class**: `SELF_COPY` | **Claim ID**: `EMP-AIEF14-01`
- **Verbatim Code Quote**:
  ```python
  Z_a_next = np.exp(1j * 0.1) * Z_a
  Z_b_next = np.exp(1j * 0.05) * Z_b
  inc_a = np.angle(Z_a_next * np.conj(Z_a))
  inc_b = np.angle(Z_b_next * np.conj(Z_b))
  act_sep_inc = np.angle(np.exp(1j * (inc_a - inc_b)))
  pred_sep_inc = 0.05
  phase_sep_check = test_phase_balance_identity(np.array([act_sep_inc]), np.array([pred_sep_inc]))
  assert phase_sep_check["identity_passes"]
  ```
- **Operator Bypass**: Validates that `0.1 - 0.05 == 0.05` under complex exponentiation. Does not test Kuramoto phase coupling or real dynamics.
- **Verification Execution**: **Ran**. Output: `[PASS] Phase separation temporal increment identity`.

### Finding 5: Triangle Edge Dummy Array Index Check
- **Files**: `aief_1_4_two_channel_alignment_v4.py:298-305` & `v5.py:414-421`
- **Class**: `SELF_COPY` | **Claim ID**: `EMP-AIEF14-01`
- **Verbatim Code Quote**:
  ```python
  edge_i = np.zeros(60, dtype=int)
  edge_j = np.zeros(60, dtype=int)
  edge_i[25], edge_j[25] = 2, 7
  edge_i[29], edge_j[29] = 2, 11
  edge_i[59], edge_j[59] = 7, 11
  validate_edge_indexing((edge_i, edge_j))
  ```
- **Operator Bypass**: Constructs zero vectors of length 60 and only populates the three triangle edges inspected by `validate_edge_indexing`, ignoring all other 57 edges and graph topology.
- **Verification Execution**: **Ran**. Output: `[PASS] Tuple-of-arrays edge index validation`.

---

## 4. Execution vs. Reading Inventory

In accordance with Seat 002 direction, every census check is explicitly categorized as either **Ran** (executed directly in the environment with verified command and stdout) or **Read** (audited via static code inspection and tracing):

### A. Executed Self-Test Suites (**Ran**)
1. `aief_1_4_two_channel_alignment_v5.py --self-test`
   - Command: `python3 aief_1_4_two_channel_alignment_v5.py --self-test`
   - Output: 8/8 checks passed (`Tuple-of-arrays`, `e = T1 + T2`, `radial recurrence`, `phase separation`, `Prop 3.1`, `Prop 5.1`, `Prop 4.1`, `sign changes`).
2. `aief_1_4_two_channel_alignment_v4.py --self-test`
   - Command: `python3 aief_1_4_two_channel_alignment_v4.py --self-test`
   - Output: 5/5 checks passed (`Tuple-of-arrays`, `e = T1 + T2`, `radial recurrence`, `phase separation`, `sign changes`).
3. `AIEF_1_4_matched_phase_memory_ablation.py --self-test`
   - Command: `python3 AIEF_1_4_matched_phase_memory_ablation.py --self-test`
   - Output: Tests 1–16 all reported `PASS` (line 2310 onward); final status `Self-test: ALL PASSED`.
4. `AIEF_1_4_proposal_equalization_bridge_analysis.py --self-test`
   - Command: `python3 AIEF_1_4_proposal_equalization_bridge_analysis.py --self-test`
   - Output: `Synthetic proposal-equalization bridge checks: PASS` (reproduces E19 pinned defect).
5. `AIEF_1_4_proposal_equalization_bridge_analysis_v1_1.py --self-test`
   - Command: `python3 AIEF_1_4_proposal_equalization_bridge_analysis_v1_1.py --self-test`
   - Output: `Synthetic proposal-equalization bridge checks: PASS` (reproduces negative control rejection of `BAD=(0.41, 0.31, 0.27)` and acceptance of `GOOD=(0.41, 0.27, 0.31)`).

### B. Static Audit Tracing (**Read**)
1. `AIEF_1_4_Twindow_sensitivity.py:574-632` (`validate_engine_contract`): Audited driver/engine constant dictionary comparisons.
2. `aief_experiment_engine_v1.py:1755-2670` (`run_baseline_equivalence` and `exact_array_equal_with_nan`): Audited 12 structural preflight, schema key validation, exact parameter matching, and bit-for-bit array/scalar checks.
3. `AIEF_1_4_Twindow_sensitivity_analysis_v3.py:1360-1430` (`validate_run`): Audited Stage 1 baseline certificate check and dataset completeness.

---

## 5. Inherited Static-Integrity Items

### 5.1. Registry Path Integrity (`registry/studies.csv`)
Tokens from `canonical_entrypoints` and `canonical_evidence_paths` were audited against the tracked working tree. Unresolved tokens were traced across git history (`git log --all --follow`):

| Study ID | Field | Token | Resolution Status | Last Git Commit / Provenance |
| :--- | :--- | :--- | :--- | :--- |
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `canonical_entrypoints` | `AIEF_1_0_*.py` | Unresolved Glob | `UNEXPLAINED` (never committed in git history) |
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `canonical_entrypoints` | `AIEF_1_1_*.py` | Unresolved Glob | `UNEXPLAINED` (never committed in git history) |
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `canonical_entrypoints` | `AIEF_1_2_*.py` | Unresolved Glob | `UNEXPLAINED` (never committed in git history) |
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `canonical_evidence_paths` | `Papers/` | Missing Directory | `17f2cf719451fc8a5bec89126a082c6e09c63b3a` (Sat Oct 24 2026: removed 3rd-party paper) |
| `AIEF_1_3_EARLY_20SEED_RERUNS` | `canonical_evidence_paths` | `runs/87dfe5798954` | Missing Directory | `UNEXPLAINED` (external data run; never committed to git) |
| `AIEF_1_3_DISJOINT_100SEED` | `canonical_entrypoints` | `AIEF_1_3_sensitivity_audit_updated.py` | Missing File | `UNEXPLAINED` (referenced in commit `57aa8ea48d5f` audit notes, never added) |
| `AIEF_1_3_DISJOINT_100SEED` | `canonical_entrypoints` | `AIEF_1_3_persistence_mechanism_test_updated.py` | Missing File | `UNEXPLAINED` (never committed in git history) |
| `AIEF_1_3_DISJOINT_100SEED` | `canonical_evidence_paths` | `runs/c3da1ac707bf` | Missing Directory | `UNEXPLAINED` (external data run; never committed to git) |
| `AIEF_1_3_DISJOINT_100SEED` | `canonical_evidence_paths` | `runs/73dca37cf93f` | Missing Directory | `UNEXPLAINED` (external data run; never committed to git) |
| `AIEF_1_3_DISJOINT_100SEED` | `canonical_evidence_paths` | `audits/scientific/revalidated_summaries/` | Missing Directory | `UNEXPLAINED` (external audit folder; never committed) |
| `AIEF_1_4_SPLIT_STATE_ABLATION` | `canonical_evidence_paths` | `runs/5a9f093a2fe0` | Missing Directory | `UNEXPLAINED` (external data run; never committed to git) |
| `AIEF_1_4_SPLIT_STATE_ABLATION` | `canonical_evidence_paths` | `aief_1_4_frozen_history_reproduction/` | Missing Directory | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_SPLIT_STATE_ABLATION` | `canonical_evidence_paths` | `aief_1_4_trajectory_recovery_equivalence/` | Missing Directory | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_MATCHED_PHASE_ABLATION` | `canonical_entrypoints` | `AIEF_1_4_driver_mechanism.py` | Missing File | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_MATCHED_PHASE_ABLATION` | `canonical_evidence_paths` | `aief_1_4_driver_mechanism/` | Missing Directory | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_TWINDOW_SENSITIVITY` | `canonical_evidence_paths` | `runs/b57562a8ee77` | Missing Directory | `UNEXPLAINED` (external data run; never committed to git) |
| `AIEF_1_4_TWINDOW_SENSITIVITY` | `canonical_evidence_paths` | `audits/scientific/revalidated_summaries/` | Missing Directory | `UNEXPLAINED` (external audit folder; never committed) |
| `AIEF_1_4_PIVOT_PILOT` | `canonical_evidence_paths` | `runs_pivot_study/ebfec9a5c419` | Missing Directory | `UNEXPLAINED` (external data run; never committed) |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | `canonical_entrypoints` | `aief_1_4_full_state_tangent_operator.py` | Missing File | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | `canonical_entrypoints` | `aief_1_4_history_cocycle_test.py` | Missing File | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | `canonical_entrypoints` | `aief_1_4_branch_tangent_comparison.py` | Missing File | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | `canonical_evidence_paths` | `aief_1_4_jacobian_step_convergence/` | Missing Directory | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | `canonical_evidence_paths` | `aief_1_4_*_report.txt` | Unresolved Glob | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_CONTROLLER_FIBER` | `canonical_entrypoints` | `aief_1_4_intertwining_controller.py` | Missing File | `UNEXPLAINED` (referenced in commit `57aa8ea48d5f`, never committed) |
| `AIEF_1_4_CONTROLLER_FIBER` | `canonical_entrypoints` | `aief_1_4_fiber_coordinate_controller.py` | Missing File | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_CONTROLLER_FIBER` | `canonical_evidence_paths` | `aief_1_4_k3_fiber_audit/` | Missing Directory | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_CONTROLLER_FIBER` | `canonical_evidence_paths` | `aief_1_4_full_seed_fiber_audit/` | Missing Directory | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_PROPOSAL_EQUALIZATION` | `canonical_evidence_paths` | `aief_1_4_boundary_stress_audit/` | Missing Directory | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_PROPOSAL_EQUALIZATION` | `canonical_evidence_paths` | `aief_1_4_proposal_margin_audit/` | Missing Directory | `UNEXPLAINED` (never committed) |
| `AIEF_1_4_PROPOSAL_EQUALIZATION` | `canonical_evidence_paths` | `aief_1_4_selection_margin_control/` | Missing Directory | `UNEXPLAINED` (never committed) |

*Note on Unpacked Archive Artifacts:* `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/` tokens (such as `AIEF_modular_driver_v1.py` and `AIEF_1_4_Twindow_sensitivity_analysis_v4.py`) exist inside the checked-in archive `AIEF_Experiments/aief_modular_platform_v1_analysis_v4.zip`. In the active git tree on `main`, they resolve once the zip archive is extracted.

### 5.2. Study Entrypoint Importability
Every resolved Python entrypoint was subjected to a clean-checkout import test (`python3 -c "import ..."` with repo root on `PYTHONPATH`):

| Resolved Canonical Entrypoint | Import Status | Diagnostic Notes |
| :--- | :--- | :--- |
| `gap_phase_scan_v9.py` | **SUCCESS** | Clean import |
| `AIEF_1_3_paired_statistics.py` | **SUCCESS** | Clean import |
| `AIEF_1_3_paired_statistics_updated.py` | **SUCCESS** | Clean import |
| `AIEF_1_3_closure_diagnostics_updated.py` | **SUCCESS** | Clean import |
| `AIEF_1_4_memory_ablation_updated.py` | **SUCCESS** | Clean import |
| `AIEF_1_4_trajectory_recovery_equivalence.py` | **SUCCESS** | Clean import |
| `AIEF_1_4_matched_phase_memory_ablation.py` | **SUCCESS** | Clean import |
| `AIEF_1_4_Twindow_sensitivity.py` | **SUCCESS** | Clean import |
| `AIEF_1_4_Twindow_sensitivity_analysis_v3.py` | **SUCCESS** | Clean import |
| `run_twindow_pivot_study.py` | **SUCCESS** | Clean import |
| `AIEF_1_4_frozen_driver_cocycle_analysis.py` | **SUCCESS** | Clean import |
| `aief_1_4_operator_compression.py` | **SUCCESS** | Clean import |
| `aief_1_4_slow_subspace_projection.py` | **SUCCESS** | Clean import |
| `aief_1_4_observable_jacobian.py` | **SUCCESS** | Clean import |
| `aief_1_4_coupling_lock_audit.py` | **SUCCESS** | Clean import |
| `aief_1_4_k3_structure_scan.py` | **SUCCESS** | Clean import |
| `AIEF_1_4_actual_admissibility_branch_audit.py` | **SUCCESS** | Clean import |
| `AIEF_1_4_component_controller_audit.py` | **SUCCESS** | Clean import |
| `AIEF_1_4_proposal_equalization_bridge_analysis.py` | **SUCCESS** | Clean import |
| `AIEF_1_4_nested_operator_family_audit.py` | **SUCCESS** | Clean import |
| `AIEF_modular_driver_v1.py` (extracted platform) | **SUCCESS** | Clean import |
| `AIEF_1_4_Twindow_sensitivity_analysis_v4.py` (extracted platform) | **SUCCESS** | Clean import |
| `AI Agent Audits/evidence/verify_manifest.py` | **SUCCESS** | Clean import |

---

## 6. Audit Limitations & Scope Demarcation

1. In accordance with Seat 002 direction, `Older files/` and `Historical files/` directories remain strictly excluded from the active census.
2. Pinned historical files (`AIEF_1_4_proposal_equalization_bridge_analysis.py`) are retained as historical witnesses without modification.
3. All file paths and line ranges match the authoritative checkout on `main`.
