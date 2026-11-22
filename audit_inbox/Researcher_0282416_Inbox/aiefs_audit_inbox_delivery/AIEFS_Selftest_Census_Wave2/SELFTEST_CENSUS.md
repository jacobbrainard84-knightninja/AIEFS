# Independent Audit Census of False, Tautological, and Redundant Self-Tests Across AIEFS Analysis Scripts (Revision 3)

**Auditor / Researcher ID:** Researcher 0282416  
**Auditor Seat Mandate:** Auditor Seat 002 Lead Direction (dated 2026-11-21, 10:20 AM MST)  
**Target Repository:** `jacobbrainard84-knightninja/AIEFS`  
**Target Commit:** `main` @ `7ec6011d5161e7dd105b6db841ed91b6196e88d4`  
**Census Scope:** All analysis and driver Python scripts at repo root and under `AIEF_Experiments/` (excluding `Older files/` and `Historical files/`). Total audited scripts: 114 Python files.

---

## 1. Executive Summary & Direction-3 Reconciliation

In strict compliance with **DIRECTION-3** issued by Auditor Seat 002:

1. **Proposal-Equalization Bridge Grounding (Fix 1):**  
   All 6 rows for proposal-equalization bridge analysis have been re-anchored to the verbatim code on `main`:
   - In `AIEF_1_4_proposal_equalization_bridge_analysis.py` (v1.0, pinned historical defect / ERRATA E19), `synthetic_self_test()` at L198 does not call an admissibility function; it constructs `projected = {EDGE_25: s7 * x25, EDGE_29: s2 * x29, EDGE_59: s7 * x59}` (L215–219) and asserts residuals `< 1e-14` on `(projected[EDGE_25] - projected[EDGE_59]) - s7 * d_left` (L225–227) and `sigma_right` (L228–230). The KNOWN_DEFECT is grounded: running `python3 AIEF_1_4_proposal_equalization_bridge_analysis.py --self-test` passes on the known-false fixture `(0.41, 0.31, 0.27)` because line 216 hardcodes `s7` rather than the true admissibility operator winner `s2`, giving a false zero residual.
   - In `AIEF_1_4_proposal_equalization_bridge_analysis_v1_1.py` (v1.1, successor), the negative control at L247–257 catches `ValueError` from `check_synthetic_projection((0.41, 0.31, 0.27))` and asserts `bad["left_residual"] == -0.02121459694983044`, while L258–260 exercises the verified positive fixture `(0.41, 0.27, 0.31)`.
2. **Registry Path Provenance (`registry/studies.csv`) Fixed (Fix 2 & 3):**  
   Corrected the false-negative directory resolution. Active runs (`runs/87dfe5798954`, `runs/c3da1ac707bf`, `runs/73dca37cf93f`, `runs/5a9f093a2fe0`, `runs/b57562a8ee77`, `runs_pivot_study/ebfec9a5c419`, `audits/scientific/revalidated_summaries/`) are tracked on `main`. The total number of unresolved tokens is **exactly 22** (not 30). `Papers/` was tracked until commit `17f2cf719451` and originally added in `add81e6150a1` (2026-10-18).
3. **Verbatim Engine & Analysis Quotes (Fix 4):**  
   Every quoted code snippet in `selftest_census.csv` is now verified verbatim against the source code on `main`. For example, engine L2598–2608 is quoted as `elif np.isclose(engine_scalar, frozen_scalar, rtol=0.0, atol=0.0):` with exact zero tolerance (`rtol=0.0, atol=0.0`).
4. **Execution vs. Reading Grounded (Fix 5):**  
   Explicit breakdown provided for all executed commands (`python3 ... --self-test`) and static code readings. The exact mutation test for Finding 1 was re-executed and documented below.
5. **Census Expansion:**  
   Surveyed remaining candidate self-test entry points across the 114 in-scope files.

---

## 2. Methodology & Rebuilt Census Taxonomy

Across all 114 in-scope files on `main`, 49 individual self-test checks across 8 core verification suites were audited and cataloged in `selftest_census.csv`:

### Taxonomy Breakdown (49 Checks)
- **`REAL_OPERATOR`**: 33 checks (67.3%)
- **`SELF_COPY`**: 7 checks (14.3%)
- **`PARTIAL_REDUNDANT`**: 7 checks (14.3%)
- **`KNOWN_DEFECT`**: 2 checks (4.1%)

---

## 3. Top 5 Ranked Findings & Verifiable Witnesses

### Finding 1: Pure Tautology in Proposition 3.1 Proposal Identity Check
- **File**: `aief_1_4_two_channel_alignment_v5.py:459-467`
- **Class**: `SELF_COPY` | **Claim ID**: `EMP-AIEF14-01`, `PROP-EQUALIZATION`
- **Execution Mode**: **Ran** (`python3 aief_1_4_two_channel_alignment_v5.py --self-test`)
- **Verbatim Code Quote**:
  ```python
  d_test = c0_test * b_test + a_R_test * r_test
  prop_check = test_proposal_identity(d_test, c0_test, b_test, a_R_test, r_test)
  assert prop_check["identity_passes"]
  ```
- **Operator Bypass & Flaw**: `test_proposal_identity` evaluates `errors = np.abs(d - (c0 * b + a_R * r))`. Because `d_test` is created directly as `c0_test * b_test + a_R_test * r_test` one line prior, this evaluates $X - X = 0$ on synthetic arrays without invoking the production proposal generator `augmented.base_intermediates`.
- **Negative Control Run**:
  - Mutating line 464 from:
    ```python
    d_test = c0_test * b_test + a_R_test * r_test
    ```
    to:
    ```python
    d_test = c0_test * b_test + a_R_test * r_test + 0.5
    ```
    Causes `test_proposal_identity` to return `{"max_abs_error": 0.5, "identity_passes": False}`, raising `AssertionError` at line 466.
  - Conversely, modifying production proposal dynamics in the engine leaves this self-test printing `[PASS] Exact proposal identity d_n = c0 * b_n + a_R * r_n`, demonstrating that the test is completely decoupled from runtime engine physics.

### Finding 2: Pure Tautology in Proposition 5.1 Recurrence Check
- **File**: `aief_1_4_two_channel_alignment_v5.py:469-478`
- **Class**: `SELF_COPY` | **Claim ID**: `EMP-AIEF14-01`, `PROP-EQUALIZATION`
- **Execution Mode**: **Ran** (`python3 aief_1_4_two_channel_alignment_v5.py --self-test`)
- **Verbatim Code Quote**:
  ```python
  d_next_test = lambda_test * d_test + a_R_test * r_next_test
  rec_check = test_proposal_recurrence(
      d_next_test, lambda_test, d_test, a_R_test, r_next_test
  )
  assert rec_check["identity_passes"]
  ```
- **Operator Bypass & Flaw**: Evaluates linear recurrence on synthetic arrays generated from the tested formula.

### Finding 3: Tautological Projected Weight Check (Proposition 4.1)
- **File**: `aief_1_4_two_channel_alignment_v5.py:480-485`
- **Class**: `SELF_COPY` | **Claim ID**: `EMP-AIEF14-01`, `PROP-EQUALIZATION`
- **Execution Mode**: **Ran** (`python3 aief_1_4_two_channel_alignment_v5.py --self-test`)
- **Verbatim Code Quote**:
  ```python
  b_next_test = s7_test * d_test
  pw_check = test_projected_weight_identity_fixed_left(b_next_test, s7_test, d_test)
  assert pw_check["identity_passes"]
  ```
- **Operator Bypass & Flaw**: Target array is generated via scalar multiplication `s7_test * d_test` immediately before checking `b_next - s7 * d_test == 0`.

### Finding 4: Trivial Hardcoded Modulo Phase Separation Check
- **Files**: `aief_1_4_two_channel_alignment_v4.py:330-338` & `v5.py:448-457`
- **Class**: `SELF_COPY` | **Claim ID**: `EMP-AIEF14-01`
- **Execution Mode**: **Ran**
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
- **Operator Bypass & Flaw**: Checks $0.1 - 0.05 == 0.05$ on hardcoded rotation angles; decoupled from Kuramoto equations.

### Finding 5: Triangle Edge Dummy Array Index Check
- **Files**: `aief_1_4_two_channel_alignment_v4.py:298-305` & `v5.py:414-421`
- **Class**: `SELF_COPY` | **Claim ID**: `EMP-AIEF14-01`
- **Execution Mode**: **Ran**
- **Verbatim Code Quote**:
  ```python
  edge_i = np.zeros(60, dtype=int)
  edge_j = np.zeros(60, dtype=int)
  edge_i[25], edge_j[25] = 2, 7
  edge_i[29], edge_j[29] = 2, 11
  edge_i[59], edge_j[59] = 7, 11
  validate_edge_indexing((edge_i, edge_j))
  ```
- **Operator Bypass & Flaw**: Populates zero vectors only at inspected indices 25, 29, 59, ignoring the incidence matrix and remaining 57 edges.

---

## 4. Execution vs. Reading Inventory

### A. Executed Self-Test Commands (**Ran**)
1. `python3 aief_1_4_two_channel_alignment_v5.py --self-test`
   - Output: 8/8 checks PASS.
2. `python3 aief_1_4_two_channel_alignment_v4.py --self-test`
   - Output: 5/5 checks PASS.
3. `python3 AIEF_1_4_matched_phase_memory_ablation.py --self-test`
   - Output: Tests 1–16 PASS (lines 2327–2590); `Self-test: ALL PASSED`.
4. `python3 AIEF_1_4_proposal_equalization_bridge_analysis.py --self-test`
   - Output: `Synthetic proposal-equalization bridge checks: PASS` (passes on known-false fixture due to hardcoded L216).
5. `python3 AIEF_1_4_proposal_equalization_bridge_analysis_v1_1.py --self-test`
   - Output: `Synthetic proposal-equalization bridge checks: PASS` (executes negative control catching `ValueError` on bad fixture and passes on good fixture).

### B. Static Audit Readings (**Read**)
1. `AIEF_1_4_Twindow_sensitivity.py:574-632` (`validate_engine_contract`): Driver and engine constant dictionary comparisons.
2. `aief_experiment_engine_v1.py:1755-2670` (`exact_array_equal_with_nan` and `run_baseline_equivalence`): 12 structural preflight, schema validation, zero-tolerance model parameter checks (`rtol=0.0, atol=0.0`), and bit-for-bit array/scalar comparisons.
3. `AIEF_1_4_Twindow_sensitivity_analysis_v3.py:1364-1370` (`validate_run`): Baseline certificate seed status validation.

---

## 5. Inherited Static-Integrity Audit: Registry Path Resolution (`registry/studies.csv`)

### Resolution Tool Script
Deposited text of `/home/user/resolve_studies.py` executed against `main`:
```python
#!/usr/bin/env python3
"""Resolve registry/studies.csv tokens against tracked repository tree."""
import csv
import glob
import os
import subprocess
import sys

def resolve_token(repo_dir, token):
    p = os.path.join(repo_dir, token)
    if os.path.exists(p):
        return True, [token]
    matches = glob.glob(p)
    if matches:
        return True, [os.path.relpath(m, repo_dir) for m in matches]
    return False, []

def main():
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else "/home/user/aiefs_git"
    csv_path = os.path.join(repo_dir, "registry/studies.csv")

    resolved = []
    unresolved = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["study_id"]
            eps = [t.strip() for t in row.get("canonical_entrypoints", "").split(";") if t.strip()]
            evs = [t.strip() for t in row.get("canonical_evidence_paths", "").split(";") if t.strip()]
            for t in eps:
                ok, m = resolve_token(repo_dir, t)
                if ok:
                    resolved.append((sid, "canonical_entrypoints", t, m))
                else:
                    unresolved.append((sid, "canonical_entrypoints", t))
            for t in evs:
                ok, m = resolve_token(repo_dir, t)
                if ok:
                    resolved.append((sid, "canonical_evidence_paths", t, m))
                else:
                    unresolved.append((sid, "canonical_evidence_paths", t))

    print(f"Total resolved tokens: {len(resolved)}")
    print(f"Total unresolved tokens: {len(unresolved)}")
    print("\nUnresolved tokens with git provenance:")
    for sid, field, t in unresolved:
        clean_t = t.rstrip("/").split("*")[0].rstrip("/")
        cmd = ["git", "log", "--all", "-n", "1", "--format=%H %cd %s", "--", clean_t if clean_t else t]
        res = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
        out = res.stdout.strip()
        prov = out if out else "UNEXPLAINED (never committed in git history)"
        print(f"[{sid}] {field} -> {t} | {prov}")

if __name__ == "__main__":
    main()
```
**Execution Command**: `python3 /home/user/resolve_studies.py /home/user/aiefs_git`  
**Output**: `Total resolved tokens: 48`, `Total unresolved tokens: 22`.

### The 22 Unresolved Tokens on Main

| # | Study ID | Field | Token | Git Provenance (`git log --all --follow`) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `canonical_entrypoints` | `AIEF_1_0_*.py` | `UNEXPLAINED` (never committed in git history) |
| 2 | `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `canonical_entrypoints` | `AIEF_1_1_*.py` | `UNEXPLAINED` (never committed in git history) |
| 3 | `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `canonical_entrypoints` | `AIEF_1_2_*.py` | `UNEXPLAINED` (never committed in git history) |
| 4 | `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `canonical_evidence_paths` | `Papers/` | Added `add81e6150a1` (2026-10-18); last modified `17f2cf719451` (2026-10-24) |
| 5 | `AIEF_1_3_DISJOINT_100SEED` | `canonical_entrypoints` | `AIEF_1_3_sensitivity_audit_updated.py` | `UNEXPLAINED` (never committed in git history) |
| 6 | `AIEF_1_3_DISJOINT_100SEED` | `canonical_entrypoints` | `AIEF_1_3_persistence_mechanism_test_updated.py` | `UNEXPLAINED` (never committed in git history) |
| 7 | `AIEF_1_4_SPLIT_STATE_ABLATION` | `canonical_evidence_paths` | `aief_1_4_frozen_history_reproduction/` | `UNEXPLAINED` (never committed in git history) |
| 8 | `AIEF_1_4_SPLIT_STATE_ABLATION` | `canonical_evidence_paths` | `aief_1_4_trajectory_recovery_equivalence/` | `UNEXPLAINED` (never committed in git history) |
| 9 | `AIEF_1_4_MATCHED_PHASE_ABLATION` | `canonical_entrypoints` | `AIEF_1_4_driver_mechanism.py` | `UNEXPLAINED` (never committed in git history) |
| 10 | `AIEF_1_4_MATCHED_PHASE_ABLATION` | `canonical_evidence_paths` | `aief_1_4_driver_mechanism/` | `UNEXPLAINED` (never committed in git history) |
| 11 | `AIEF_1_4_TANGENT_AND_COCYCLE` | `canonical_entrypoints` | `aief_1_4_full_state_tangent_operator.py` | `UNEXPLAINED` (never committed in git history) |
| 12 | `AIEF_1_4_TANGENT_AND_COCYCLE` | `canonical_entrypoints` | `aief_1_4_history_cocycle_test.py` | `UNEXPLAINED` (never committed in git history) |
| 13 | `AIEF_1_4_TANGENT_AND_COCYCLE` | `canonical_entrypoints` | `aief_1_4_branch_tangent_comparison.py` | `UNEXPLAINED` (never committed in git history) |
| 14 | `AIEF_1_4_TANGENT_AND_COCYCLE` | `canonical_evidence_paths` | `aief_1_4_jacobian_step_convergence/` | `UNEXPLAINED` (never committed in git history) |
| 15 | `AIEF_1_4_TANGENT_AND_COCYCLE` | `canonical_evidence_paths` | `aief_1_4_*_report.txt` | `UNEXPLAINED` (pattern targets root, where no report files reside) |
| 16 | `AIEF_1_4_CONTROLLER_FIBER` | `canonical_entrypoints` | `aief_1_4_intertwining_controller.py` | `UNEXPLAINED` (never committed in git history) |
| 17 | `AIEF_1_4_CONTROLLER_FIBER` | `canonical_entrypoints` | `aief_1_4_fiber_coordinate_controller.py` | `UNEXPLAINED` (never committed in git history) |
| 18 | `AIEF_1_4_CONTROLLER_FIBER` | `canonical_evidence_paths` | `aief_1_4_k3_fiber_audit/` | `UNEXPLAINED` (never committed in git history) |
| 19 | `AIEF_1_4_CONTROLLER_FIBER` | `canonical_evidence_paths` | `aief_1_4_full_seed_fiber_audit/` | `UNEXPLAINED` (never committed in git history) |
| 20 | `AIEF_1_4_PROPOSAL_EQUALIZATION` | `canonical_evidence_paths` | `aief_1_4_boundary_stress_audit/` | `UNEXPLAINED` (never committed in git history) |
| 21 | `AIEF_1_4_PROPOSAL_EQUALIZATION` | `canonical_evidence_paths` | `aief_1_4_proposal_margin_audit/` | `UNEXPLAINED` (never committed in git history) |
| 22 | `AIEF_1_4_PROPOSAL_EQUALIZATION` | `canonical_evidence_paths` | `aief_1_4_selection_margin_control/` | `UNEXPLAINED` (never committed in git history) |

---

## 6. Remaining Self-Test Survey (Next Lane Wave)

Surveying the remaining in-scope files for verification routines identified:
1. `AIEF_1_3_closure_diagnostics_updated.py:279` (`def audit_baseline_persistence`)
2. `AIEF_1_3_falsification_updated.py:152` (`def validate_configuration`), `L249` (`def validate_checkpoint`)
3. `AIEF_1_4_Twindow_pivot_seed_contrasts.py:105` (`def validate_pivot_frame`)
4. `AIEF_1_4_component_controller_audit.py:283` (`def audit_state`)
5. `AIEF_1_4_scalar_spectral_gap_reduction.py:170` (`def validate_linear_map`)
6. `AIEF_1_4_stationarity_perturbation_analysis_updated.py:193` (`def audit_directional_operator`)
7. `AIEF_1_4_freeze_controller_fiber_theorem.py:184` (`def validate_text`)
8. `AIEF_1_4_memory_ablation_updated.py:271` (`def validate_configuration`), `L844` (`def validate_seed_result`)

These will form Wave 2 of the census additions.
