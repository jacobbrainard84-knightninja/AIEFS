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
   0.050000000000000044 ≥ δ (no projection), while cap/(rowsum + ε) < 1. On a single application (P2) only this
   witness separates the engine from an "always project" mutant. Re-applying the gate (P5) catches that mutant
   without the witness (see Results). The tie cases turned out to add no detection power (M508, follow-up).
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
  production runs is still **UNEXPLAINED** (unmeasured). *(Superseded by the follow-up below: mechanism EXPLAINED.)*

## Audit follow-up (Auditor Seat 002 CLEAN WITH NOTES on `f31da4c`; Researcher 001, 2026-11-27 MST)
Every number below was reproduced by Researcher 001 (`h10_followup_checks.py`) and is pinned in the pytest wrapper.
`PREDECLARED` is unchanged.
- **N1, M504 (why it is killed).** The main cause is single-application arithmetic. Dropping ε shifts each scaled
  entry by about ε/rowsum ≈ 1.58e-12 relative (max 1.576e-12). That is **above** rtol 1e-12, so P2 kills M504 on
  84 of 150 cases. **The predeclared arithmetic itself was wrong**: it said "about 1e-12, below the tolerance".
  - Re-gating is secondary. Of the over-cap rows, 62 land exactly on fl(cap), 19 at +1 ulp and 4 at +2 ulp. A row
    1–2 ulp above re-triggers the gate, so P5 fails in 23 cases.
  - The remaining over-cap rows end below fl(cap): 13 at −1 ulp, 1 at −2 ulp, and 395 further below because a
    neighbour's smaller scale pulls them down.
  - The earlier "often 1 ulp above" wording overstated this.
  - The corrected reason is in `M504_REASON_CORRECTED`; the original reason string is left in place.
- **N3, spillover: EXPLAINED.**
  - All 457 below-cap rows that lost weight have an edge to an over-cap row.
  - Every below-cap row with such an edge lost weight.
  - No row lost weight through its own ε-band scale. There are 0 exceptions in either direction.
  - This is the per-edge min-endpoint gate (E27) working as defined. Only how often it happens in real runs is
    **UNMEASURED**.
  - The 0.352 figure is checked: 0.35158304296995124 is the largest exact gap below the cap for an over-cap row. Such
    a row is pulled further down by neighbours with smaller scales.
- **N5:** "What H10 adds" item 3 now agrees with Results.
- **N6:** `test_witness_is_what_kills_always_project_on_values` is labelled a **characterization test**, not a
  predeclared control.
- **N4, follow-up mutants**, predeclared in commit `4c275ca` before the tests existed. They were informed by the
  auditor's red team (X7, R14), so they are not blind predictions.

  | ID | Mutant | Predeclared | Observed |
  |---|---|---|---|
  | M507 | trigger loosened to `g_min_pre < δ − 1e-9` | KILLED (by an above-cap witness, one edge at nextafter(fl(cap), 1)) | **KILLED** (P1, P2), as predeclared |
  | M508 | tie cases removed from the case set (table re-run without them) | NOT DETECTED | **NOT DETECTED**, as predeclared: the tie cases add no detection power |

  - The new witness has edge 0.6333333333333334: exact value > 19/30, and g = 0.04999999999999982, which is < δ but
    ≥ δ − 1e-9.
  - The characterization test `test_above_cap_witness_is_what_kills_m507` shows M507 survives without that witness.
  - With the new witness, M503 now also fails P2. All original outcomes are unchanged.
- **N7, M506 scan:** the "±50 ulps scanned" claim was never committed. It is replaced by a committed scan
  (`m506_ulp_scan`) of ±2,000,000 ulps around fl(cap). No float x gives fl(1 − 1.5x) == 0.05, and the closest g is
  6 ulps from δ. This matches the auditor's scan.
