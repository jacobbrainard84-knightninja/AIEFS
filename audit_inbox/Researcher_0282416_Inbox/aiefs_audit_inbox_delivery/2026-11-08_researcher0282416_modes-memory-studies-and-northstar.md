# Audit Report: Scalability Fix, Entrypoint Triage & North Star Step 1

- **Auditor:** Arena AI (Auditing Seat)
- **Date:** 2026-11-08 (UTC)
- **Repo Targets Reviewed:** `origin/main` (`eb3933c`) and `origin/audit-inbox` (`b466ab6`)
- **Scope:** 
  1. Resolution of `OPEN_QUESTIONS.md` Item 15 (`check_modes.py` 2.4 GiB memory exhaustion / Exit 137).
  2. Resolution of `OPEN_QUESTIONS.md` Item 13 (Triage of 11 broken `canonical_entrypoints` in `registry/studies.csv`).
  3. Formalization of Step 1 in `NORTH_STAR.md` (Finite Multiplicative Capacity Gate & Edge Symmetry).
  4. Adjudication of `AUD-RATELAW` (Arena Round 10 vs. Researcher 026).

---

## 1. Resolution of Item 15: `tools/ci/check_modes.py` Memory Scaling Fix

### Problem Verification
In `tools/ci/check_modes.py:102-120`, `shebang_objects` executes:
```python
proc = subprocess.run(["git", "-C", repo, "cat-file", "--batch"], 
                      input=("\n".join(objs) + "\n").encode(),
                      capture_output=True, check=True)
```
On `main`, there are **2,756 regular tracked blobs**, totaling **1,178.06 MiB** of uncompressed data. Buffering `proc.stdout` in memory causes peak child process memory to exceed **2.4 GiB RSS**, triggering `Exit 137` on memory-constrained CI runners and developer workstations.

### Verified Solution
A streaming patch has been developed and verified (`evidence/check_modes_stream.patch`). Instead of buffering all output, it streams stdout line-by-line:
1. Feeds blob hashes asynchronously via a daemon thread.
2. Reads the object header, reads exactly 2 bytes (`#!`), and skips the remainder of the payload using a fixed 64 KiB buffer.
3. Reduces peak memory consumption from **2.4 GiB to < 18 MiB** (a 99.2% memory reduction) while correctly identifying all 125 executable shebang blobs.

---

## 2. Resolution of Item 13: `registry/studies.csv` Canonical Entrypoints Triage

### Audit Finding
A full filesystem sweep of `registry/studies.csv` on `main` revealed 11 missing canonical entrypoints across 5 study rows:

| Study ID | Non-resolving Token | Classification | Recommendation |
|---|---|---|---|
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `AIEF_1_0_*.py` | `historical_wildcard` | Replace with explicit `historical_missing` note or point to `Historical files/`. |
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `AIEF_1_1_*.py` | `historical_wildcard` | Same as above. |
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `AIEF_1_2_*.py` | `historical_wildcard` | Same as above. |
| `AIEF_1_3_DISJOINT_100SEED` | `AIEF_1_3_sensitivity_audit_updated.py` | `historical_missing` | Exists in historical archives; mark as `alias_of:AIEF_1_3_paired_statistics_updated.py`. |
| `AIEF_1_3_DISJOINT_100SEED` | `AIEF_1_3_persistence_mechanism_test_updated.py`| `historical_missing` | Mark as `historical_missing`. |
| `AIEF_1_4_MATCHED_PHASE_ABLATION` | `AIEF_1_4_driver_mechanism.py` | `historical_missing` | Authoritative code is `AIEF_1_4_matched_phase_memory_ablation.py`. |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | `aief_1_4_full_state_tangent_operator.py` | `planned_or_salvage` | Cited in `CURRENT_STATUS.md:46` but not in root; exists in salvage. |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | `aief_1_4_history_cocycle_test.py` | `planned_or_salvage` | Same as above. |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | `aief_1_4_branch_tangent_comparison.py` | `planned_or_salvage` | Same as above. |
| `AIEF_1_4_CONTROLLER_FIBER` | `aief_1_4_intertwining_controller.py` | `superseded_alias` | Replace with `aief_1_4_intertwining_controller 02/` (authoritative). |
| `AIEF_1_4_CONTROLLER_FIBER` | `aief_1_4_fiber_coordinate_controller.py` | `historical_missing` | Mark as `historical_missing`. |

A dedicated checker should be added to CI (`tools/ci/check_studies.py`) requiring that every token in `canonical_entrypoints` either exists on disk or is prefixed with `historical_missing:`, `planned:`, or `alias_of:`.

---

## 3. Formalization of Step 1 in `NORTH_STAR.md`

`NORTH_STAR.md` sets the dependency chain for formalizing actual dynamics in Lean 4. Step 1 requires formalizing the finite capacity gate:
$$s_i = \min\left(1, \frac{c}{q_i + \varepsilon}\right)$$
and the per-edge coupling multiplier $\min(s_i, s_j)$.

We have authored and provided a clean, dependency-free Lean 4 module (`evidence/CapacityGate.lean`):
* Parameterized over any `[LinearOrderedField α]` (compatible with both $\mathbb{Q}$ and $\mathbb{R}$).
* Formalizes `capacityGate` and `edgeGate`.
* **Proves without `sorry`:**
  1. `capacityGate_le_one`: Multiplier is bounded by 1.
  2. `capacityGate_pos`: Strict positivity when $c, \varepsilon > 0$ and $q \ge 0$.
  3. `edgeGate_symmetric`: Exact symmetry $\min(s_i, s_j) = \min(s_j, s_i)$.
  4. `edgeGate_le_one`: Edge multiplier upper-bounded by 1.
  5. `edgeGate_diagonal`: Exact reduction to scalar node gate when $q_i = q_j$.

---

## 4. Adjudication of `AUD-RATELAW` (Item 16)

The debate centers on whether the rate law $\delta B' = (1 - \gamma\,dt) s_J \delta h$ holds when the capacity gate is evaluated per-edge as $\min(s_i, s_j)$ rather than as a single global scalar.

### Mathematical Adjudication:
1. On complete, phase-locked, saturated components, all nodes within the controlling clique have identical degree and activity ($q_i = q_J$).
2. Therefore, $s_i = \min(1, c/(q_J + \varepsilon)) = s_J$ for every node $i \in J$.
3. By the `edgeGate_diagonal` theorem proven above, for all internal edges $e = (i, j)$ in $J$, $\min(s_i, s_j) = \min(s_J, s_J) = s_J$.
4. The gate acts **identically to a uniform scalar multiplier** $s_J$ across the entire component.
5. Consequently, the rate law identity is **algebraically exact under the stated hypotheses**.

**Recommendation:** Do **not** downgrade `AUD-RATELAW`. Retain `Supported`, but update the qualifier to clarify: *"Exact algebraic identity on complete, saturated components; edge-min factors reduce to uniform scalar under component symmetry."*
