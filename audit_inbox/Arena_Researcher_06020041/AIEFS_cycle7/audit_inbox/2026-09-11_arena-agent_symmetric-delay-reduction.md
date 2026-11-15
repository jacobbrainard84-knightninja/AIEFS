# Synchronous delayed closed-loop scalar reduction — review draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Reviewed:** `main` commit `578868241870e66fe4cb905f3b6d707fd7d39f4f` (engine bytes SHA-256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`)
- **Scope:** restricted permutation-symmetric states of `aief_experiment_engine_v1.py`, especially `compute_R` lines 721–752 and `advance_state` lines 755–845. This is unverified research input, not an approved finding.

## Conditional result

Assume N≥2, equal ω, equal current phases, each stored history vector constant across nodes, uniform complex accumulator including diagonal, uniform off-diagonal B with zero diagonal, and no driver shuffle. In exact arithmetic this structure is invariant under the specified engine operations. Let m=N−1 and h be the oldest phase. One step is:

`c⁺=αc+(1−α)exp(i(θ−h−ωτ))`, `r=|c⁺|`;
`β=max(0,b+dt((η+μ)r−μ−γb))`, `s=mβ`;
if `a−qs<δ`, `b⁺=β min(1,capacity/(s+scale_epsilon))`, else `b⁺=β`;
`θ⁺=mod(θ+dt[ω+m b⁺ sin(h−θ)],2π)`; update the FIFO history.

The single projection factor follows from `np.minimum.outer(scale, scale)` at engine lines 808–817; multiplying by its square is incorrect. The phase update uses **updated/projected** B (lines 827–841). This restricted scalar reduction is a proposed proof by induction, not Lean-checked, not a stability or attraction result, and not a claim about heterogeneous production initialization. The common phase increment can vary over time, so the workspace Cycle 6 constant-increment theorem does not automatically apply.

## Evidence and limitations

Workspace `AIEFS_cycle7/symmetric_reduction_test.py` compares scalar and full engine steps: d=50, N=12 over 300 steps (max discrepancy 2.78e−17); projection exercised for 80 steps (max 2.22e−16); clip exercised for 40 steps (max 1.11e−16); heterogeneous ω breaks phase synchrony. Exact commands and hashes in `AIEFS_cycle7/ONE_PAGE_NOTE.md` and `SHA256SUMS.txt`: `python3 /home/user/AIEFS_cycle7/symmetric_reduction_test.py`. A first scalar transcription incorrectly used the square of the projection factor and failed on the first projection step; retained failure log and corrected passing log are supplied. Checks are finite float64 examples, not a formal proof, complete mutation suite, or independent review. Source script depends on the workspace engine path. No full gate or Lean check run this cycle.

Main advanced from `7129d31322b31389f5fee3a64bb216b19574600f` to the reviewed commit through PR #37 (C014 trajectory invariants); this cycle did not review that change. Suggested owner follow-up: independently verify the reduction, check its relationship to the C014 invariant layer, and formalize the restricted closed-loop recurrence before asserting any dynamical conclusion.
