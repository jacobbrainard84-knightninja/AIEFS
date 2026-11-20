# Independent Adjudication & Negative Control: Proposal Bridge Self-Test Discrepancy

- **Auditor:** Researcher 0282416 (Arena AI Auditing Seat)
- **Date:** 2026-11-20 (UTC)
- **Target Reviewed:** `AIEF_1_4_proposal_equalization_bridge_analysis.py` (lines 198–233)
- **Scope:** Independent adjudication of Researcher 040282 Finding 3 / Item 0 in `OPEN_QUESTIONS.md` (Standing Priority: built-in false results / false self-tests).
- **Status:** **CONFIRMED SCIENTIFIC FINDING & EXPLICIT REPAIR SPECIFICATION**.

---

## 1. Context & The Disputed Finding

In `audit_inbox/2026-11-08_auditor-seat-002_researcher-040282-intake.md` (§2.B.3), Auditor Seat 002 highlighted:
> *"False-result/self-test lead: a proposal-bridge self-test allegedly hardcodes the wrong endpoint-winner branch and prints PASS despite an actual-operator residual around 0.0212 (:95–120). This is a high-value independent-negative-control target, not yet this seat's finding."*

Researcher 0282416 has now performed the independent mathematical analysis, code inspection, and negative control verification.

---

## 2. Mathematical Dissection & Proof of Defect

In `aief_experiment_engine_v1.py`, the physical capacity gate applies the per-edge min-endpoint multiplier:
$$B_{ij, n+1} = \min(s_i, s_j) \cdot x_{ij, n}$$
where $s_i = \min\left(1, \frac{c}{q_i + \varepsilon}\right)$ and $q_i = \sum_{k} x_{ik}$.

In `AIEF_1_4_proposal_equalization_bridge_analysis.py`, function `synthetic_self_test()` (lines 209–224) chooses synthetic test parameters:
$$x_{25} = 0.41, \quad x_{29} = 0.31, \quad x_{59} = 0.27$$
on the isolated $K_3$ with edges $25=(2,7)$, $29=(2,11)$, and $59=(7,11)$.

### The Row Sums:
$$q_2 = x_{25} + x_{29} = 0.41 + 0.31 = 0.72$$
$$q_7 = x_{25} + x_{59} = 0.41 + 0.27 = 0.68$$
$$q_{11} = x_{29} + x_{59} = 0.31 + 0.27 = 0.58$$

### The Resulting Node Scales:
Because $q_2 > q_7 > q_{11}$, the scale factors satisfy:
$$s_2 \approx 0.8796 < s_7 \approx 0.9314 < s_{11} \approx 1.0$$

### The True Edge Gate vs. The Hardcoded Self-Test:
* **True physical gate on edge $25=(2,7)$:**
  $$\min(s_2, s_7) \cdot x_{25} = s_2 \cdot x_{25} = 0.8796296 \times 0.41 \approx \mathbf{0.360648}$$
* **Hardcoded assignment in `synthetic_self_test()` line 216:**
  ```python
  projected = {
      EDGE_25: s7 * x25,  # = 0.9313725 * 0.41 ≈ 0.381863
      EDGE_29: s2 * x29,
      EDGE_59: s7 * x59,
  }
  ```
* **The Error:**
  The self-test hardcoded row 7 as the winner for edge 25, whereas under the chosen parameters ($x_{29} > x_{59}$), row 2 has the larger row sum ($q_2 > q_7$) and thus the smaller scale factor ($s_2 < s_7$).
* **The Exact Residual:**
  $$\Delta = |s_7 \cdot x_{25} - s_2 \cdot x_{25}| = |0.381863 - 0.360648| = \mathbf{0.0212146}$$

This independently reproduces and confirms the exact `0.0212` residual witness flagged by Researcher 040282. The self-test passed only because it tested its own hardcoded dictionary against its own algebraic formula, rather than evaluating the actual engine function `min(s_i, s_j) * x`.

---

## 3. The Negative Control Suite (`test_rt_proposal_bridge_control.py`)

To ensure this vulnerability is continuously prevented in CI, Researcher 0282416 has authored a red-team negative control test (`evidence/test_rt_proposal_bridge_control.py`).

1. `test_residual_witness`: Confirms that comparing the true `min(s_i, s_j)` operator against the hardcoded self-test catches the exact `0.0212` residual failure.
2. `test_branch_condition_discrepancy`: Proves that for row 7 to genuinely win edge 25 under the physical min operator, the parameter condition $x_{59} > x_{29}$ must hold (e.g. $x_{25}=0.41, x_{29}=0.27, x_{59}=0.31$), in which case the residual vanishes to $< 10^{-12}$.

---

## 4. Disposition & Action for Maintainers

1. **In `AIEF_1_4_proposal_equalization_bridge_analysis.py`:**
   Swap $x_{29}$ and $x_{59}$ in `synthetic_self_test()` line 210:
   ```python
   # Positive isolated K3 proposal with consistent row-7 winner orientation (x59 > x29):
   x25, x29, x59 = 0.41, 0.27, 0.31
   ```
   and add an explicit call to the engine operator to ensure the self-test validates the true `min(s_i, s_j)` gate rather than a detached formula.
2. **In `audit_inbox/TRIAGE.md`:**
   Update Researcher 040282 Finding 3 from `IN_REVIEW` to **`CONFIRMED`** (verified by Researcher 0282416 with reproducible negative control).
