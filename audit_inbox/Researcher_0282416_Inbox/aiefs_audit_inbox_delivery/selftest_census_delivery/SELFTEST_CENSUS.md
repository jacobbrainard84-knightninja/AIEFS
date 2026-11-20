# Independent Audit Census of False and Synthetic Self-Tests Across AIEFS Analysis Scripts

**Auditor / Researcher ID:** Researcher 0282416  
**Auditor Seat Direction:** Auditor Seat 002 Lead Direction (dated 2026-11-20)  
**Target Repository:** `jacobbrainard84-knightninja/AIEFS`  
**Target Commit:** `main` @ `0a6a2f62ea9af147cac60a7be30d85d6b37fe52a`  
**Census Scope:** All analysis and driver Python scripts at repo root and under `AIEF_Experiments/` (excluding `Older files/` and `Historical files/`). Total audited scripts: 114 Python files.

---

## 1. Executive Summary & Scope

Per explicit direction from **Auditor Seat 002**, this audit is strictly confined to a comprehensive census of false, tautological, and redundant self-tests across the in-scope analysis scripts on `main`. 

In accordance with Seat 002's mandate:
- No Lean bridge modifications or transient-amplification proofs were conducted.
- No claim status re-evaluations or `TRIAGE.md` modifications were performed.
- No hash-pinned files were altered.
- Pinned defects (such as E19 on `AIEF_1_4_proposal_equalization_bridge_analysis.py`) are acknowledged as historically settled and codified in successor test suites (`test_040282_f4_f6_f7.py`).

A total of **114 in-scope Python files** were surveyed. Across all self-test entry points (`run_self_test()`, `synthetic_self_test()`, `validate_engine_contract()`, and `run_baseline_equivalence()`), **43 distinct self-test verification checks** were audited and cataloged in `selftest_census.csv`.

---

## 2. Methodology & Classification Taxonomy

Each test check was inspected against the underlying production operators and classified into one of four taxonomy classes:

1. **`SELF_COPY`**: The self-test fabricates an intermediate input and immediately compares it against an identical definition or tautology in the verification function, bypassing the production operators and physical simulation state completely. A bug in the production operator cannot cause this check to fail.
2. **`PARTIAL_REDUNDANT`**: The self-test exercises an isolated algebraic helper function with random or synthetic inputs, but verifies internal code consistency rather than evaluating simulated trajectory states, or repeats checks across multiple files.
3. **`KNOWN_DEFECT`**: The self-test is known to pass false mathematical claims due to hardcoded fixtures or flawed operator logic (e.g., ERRATA E19).
4. **`REAL_OPERATOR`**: The self-test directly exercises the genuine runtime simulation engine, production operator, or strict bit-for-bit regression comparator with zero tolerances (`rtol=0, atol=0`).

### Census Distribution Summary
- **Total Audited Verification Checks**: 43
- **`REAL_OPERATOR`**: 29 (67.4%)
- **`SELF_COPY`**: 7 (16.3%)
- **`PARTIAL_REDUNDANT`**: 4 (9.3%)
- **`KNOWN_DEFECT`**: 3 (7.0%)

---

## 3. Top 5 Ranked Findings

### Finding 1: Pure Tautology in Proposition 3.1 Proposal Identity Check
- **File**: `aief_1_4_two_channel_alignment_v5.py:459-467`
- **Class**: `SELF_COPY`
- **Claim ID**: `EMP-AIEF14-01`, `PROP-EQUALIZATION`
- **Mechanism**: The self-test defines:
  ```python
  c0_test = 0.999
  a_R_test = 0.01
  b_test = np.array([0.5, 0.3, 0.1])
  r_test = np.array([0.02, 0.01, 0.005])
  d_test = c0_test * b_test + a_R_test * r_test
  prop_check = test_proposal_identity(d_test, c0_test, b_test, a_R_test, r_test)
  assert prop_check["identity_passes"]
  ```
  Inside `test_proposal_identity`, it computes:
  ```python
  prediction = c0 * b + a_R * r
  errors = np.abs(d - prediction)
  ```
- **Witness & Flaw**: `d_test` is constructed by computing `c0_test * b_test + a_R_test * r_test` one line prior to passing it to `test_proposal_identity`, which recomputes `c0 * b + a_R * r`. This is an identity $X - X = 0$. The check does not invoke the production proposal calculation in `augmented.base_intermediates` or evaluate real trajectory arrays.
- **Negative Control**: Mutating the real proposal generation in `run_production_analysis` leaves this self-test reporting `[PASS] Exact proposal identity d_n = c0 * b_n + a_R * r_n`.

### Finding 2: Pure Tautology in Proposition 5.1 Recurrence Check
- **File**: `aief_1_4_two_channel_alignment_v5.py:469-478`
- **Class**: `SELF_COPY`
- **Claim ID**: `EMP-AIEF14-01`, `PROP-EQUALIZATION`
- **Mechanism**:
  ```python
  lambda_test = np.array([0.998, 0.5, 0.998])
  r_next_test = np.array([0.015, 0.008, 0.003])
  d_next_test = lambda_test * d_test + a_R_test * r_next_test
  rec_check = test_proposal_recurrence(
      d_next_test, lambda_test, d_test, a_R_test, r_next_test
  )
  assert rec_check["identity_passes"]
  ```
- **Witness & Flaw**: `d_next_test` is defined by the exact linear formula tested. Neither `lambda_test`, `d_test`, nor `r_next_test` originate from simulation dynamics.
- **Negative Control**: Altering `lambda_n` computation or memory recurrence in the engine cannot fail this check.

### Finding 3: Tautological Projected Weight Check (Proposition 4.1)
- **File**: `aief_1_4_two_channel_alignment_v5.py:480-485`
- **Class**: `SELF_COPY`
- **Claim ID**: `EMP-AIEF14-01`, `PROP-EQUALIZATION`
- **Mechanism**:
  ```python
  s7_test = np.array([0.9, 0.9, 0.9])
  b_next_test = s7_test * d_test
  pw_check = test_projected_weight_identity_fixed_left(b_next_test, s7_test, d_test)
  assert pw_check["identity_passes"]
  ```
- **Witness & Flaw**: Target `b_next_test` is synthesized by scalar multiplication `s7_test * d_test`. The check verifies only that numpy array multiplication is commutative and invertible under subtraction.
- **Negative Control**: Violations of fixed-left projection during simulation runs cannot be detected by this self-test.

### Finding 4: Trivial Hardcoded Modulo Phase Separation Check
- **Files**: `aief_1_4_two_channel_alignment_v4.py:330-338` & `v5.py:448-457`
- **Class**: `SELF_COPY`
- **Claim ID**: `EMP-AIEF14-01`
- **Mechanism**:
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
- **Witness & Flaw**: Hardcodes the numbers `0.1` and `0.05` to verify `0.1 - 0.05 == 0.05`. It exercises none of the phase dynamics, Kuramoto coupling, or differential equations of the model.

### Finding 5: Triangle Edge Dummy Array Index Check
- **Files**: `aief_1_4_two_channel_alignment_v4.py:298-305` & `v5.py:414-421`
- **Class**: `SELF_COPY`
- **Claim ID**: `EMP-AIEF14-01`
- **Mechanism**:
  ```python
  edge_i = np.zeros(60, dtype=int)
  edge_j = np.zeros(60, dtype=int)
  edge_i[25], edge_j[25] = 2, 7
  edge_i[29], edge_j[29] = 2, 11
  edge_i[59], edge_j[59] = 7, 11
  validate_edge_indexing((edge_i, edge_j))
  ```
- **Witness & Flaw**: Does not build or validate the real incidence matrix or full edge table for the 60-edge network. It creates zero arrays, sets the exact indices inspected by `validate_edge_indexing`, and passes.

---

## 4. Audit Limitations & Scope Demarcation

1. **Exclusions**: Per Seat 002 direction, `Older files/` and `Historical files/` directories were strictly excluded from the active census.
2. **Pinned Historical Files**: Pinned historical defect files (such as `AIEF_1_4_proposal_equalization_bridge_analysis.py`) were cataloged to witness historical defect origins, but not modified. Successor validation was verified against `AIEF_1_4_proposal_equalization_bridge_analysis_v1_1.py` and modular test suites.
3. **Execution Environment**: Audits were conducted via static AST analysis, source code tracing, and sandboxed interpreter evaluation on `main` commit `0a6a2f6`.
