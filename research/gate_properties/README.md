# H10: gate property checks vs an exact Fraction oracle

Plan item H10 (audit-inbox `PLAN_2026-11-25_scan_leads.md`) as changed by Auditor Seat 002's review
(`REVIEW_2026-11-26_auditor_scan_leads.md`, `b15c5e5`): **stdlib + numpy only (no Hypothesis)**, an oracle that models
the engine's **global `pre_violation` trigger**, and a **fixed ε-band witness**. Author Researcher 001; auditor
Auditor Seat 002 (opens the PR). Mutant block M500 ff., equivalence control E500 (Researcher 001 numbering: M400 H8,
M500 H10, M600 H12, M700 H17).

## What already exists (so this does not duplicate it)
- Lean: `GateMap.lean`, `Capacity.lean` (guarded capacity, row sums ≤ cap, idempotence on the exact real map).
- `research/lean_gate/lean_gate_crosscheck_v1.py` and the gate-form adjudication's W1–W5 Fraction witnesses
  (audit-inbox `Project_Seats/2026-11-20_auditor-seat-002_gate-form-adjudication/`).

## What H10 adds
1. A Fraction oracle of the **control flow** (trigger, then s_i = min(1, cap/(rowsum_i + ε)), per-edge min, zero
   diagonal), applied to the exact values of the float64 inputs.
2. The float side is the engine's own projection block (`# Check gap constraint` … `raise RuntimeError`),
   **extracted at run time from the SHA-locked engine** (sha256 checked; never imported, never edited) and compiled
   into a function. Mutants are textual edits of that in-memory copy.
3. 150 seeded matrices (N = 12; sparse/dense; row sums around the cap; exact endpoint-scale ties every 10th case)
   plus the **ε-band witness**: one edge of 0.6333333333333333, so every row sum is ≤ cap and g_min_pre =
   0.050000000000000044 ≥ δ (no projection), while cap/(rowsum + ε) < 1. Only this witness separates the engine from
   an "always project" mutant.
4. Properties P0–P7: no post-check error; trigger and values equal the oracle (rtol 1e-12); symmetric, nonnegative,
   zero diagonal; rows ≤ cap; float and exact idempotence; exact binding rows strictly below the cap.
5. A **spillover observation** (not a pass/fail rule): how often non-binding rows lose weight when projection fires,
   and how far binding rows end below the cap. Real-run impact stays **UNEXPLAINED**.

## Predeclared outcomes (committed before the first run; `PREDECLARED` in `gate_h10.py`)
| ID | Mutant | Predeclared |
|---|---|---|
| M500 | always project (`if True`) | KILLED (ε-band witness) |
| M501 | one-endpoint factor `scale[:, None]` | KILLED |
| M502 | `np.maximum.outer` | KILLED |
| M503 | cap × 1.01 | KILLED |
| M504 | `scale_epsilon` dropped | SURVIVES (≈1e-12 relative effect, below the float tolerance: a disclosed limit) |
| M505 | diagonal not re-zeroed | SURVIVES (equivalent: input diagonal already zero) |
| M506 | trigger `<=` | SURVIVES (float-equivalent at production a, q, δ: no float64 row sum gives g_min_pre == δ) |
| E500 | `np.minimum.outer(scale, scale).T` (equivalent) | NOT KILLED |

A mismatch with this table fails the run. Survivors are reported, never deleted.

Run: `python research/gate_properties/gate_h10.py` (also run by `research/lean_gate/tests/test_gate_properties_h10.py`).

## Results (commit 2, run 2026-11-26 MST on `main` `daa977a` + this branch)
- Unmutated engine block: all properties PASS on 150 seeded cases + the ε-band witness.
- M500–M503 KILLED, as predeclared. M505, M506 SURVIVE and E500 NOT KILLED, as predeclared.
- **Deviation: M504 (ε dropped) was predeclared SURVIVES but is KILLED.** My prediction was wrong: with ε = 0 a
  binding row lands on the cap in float, often 1 ulp above, so re-applying the gate re-triggers (P5) and the values
  leave the ε > 0 oracle by more than rtol 1e-12 (P2). `PREDECLARED` is unchanged from commit 1; the deviation is
  recorded in `OBSERVED_DEVIATIONS` with its reason.
- The witness is the only thing that kills M500 **on a single application** (P2). Without it M500 still fails P5:
  an always-projected binding row ends inside the ε band, so projecting again shrinks it. So the review's "only the
  witness separates them" holds for P2 but not for P5. (Found when the witness negative control first ran; the test
  `test_witness_is_what_kills_always_project_on_values` now asserts exactly this.)
- **Spillover observation (synthetic matrices, not real runs):** projection fired in 89/150 cases; 457 of the 574
  non-binding rows in those cases lost weight; a binding row ended up to 0.352 below the cap. How often this happens in
  production runs is still **UNEXPLAINED** (unmeasured).
