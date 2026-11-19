# Proposed complete-graph phase-block mode bounds — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Reviewed:** main `c9863e1c391a9f39cc8cef680a2fa349378b6cfe` and inbox `2e63035c1c973ff07e8124e3ca9b8e198b4e5171`; depends on unmerged Cycle 15 `DelayModeMain.lean` and main `DelayRoots.lean`.
- **Scope:** exact-complex linear complete-graph phase-history block and conditional pointwise eigenmodes. Unverified research input, not a project claim.

`CompleteGraphPhase.lean` defines a node-indexed step with head `(1−(N−1)h)x₀(i)+h(∑ⱼx_d(j)−x_d(i))` and the usual delayed history shift. It proves the total-minus-self identity, reduction to Cycle 15's scalar shift for delayed zero-sum and delayed node-constant slices, and the corresponding nonzero pointwise eigenmode bounds for N≥2, h>0, (N−1)h<1. Zero-sum modes are strictly inside the unit disk; constant-slice modes are in the closed disk with only z=1 on its boundary. It does not prove a complete decomposition, neutral-root simplicity, Matrix spectrum, nonlinear stability, or correspondence to the actual engine Jacobian. No production, projected-branch or heterogeneous-frequency claim.

Evidence: sparse cited main plus the Cycle 15 and 16 modules, Lean 4.33.1, mathlib `0df444a360eaa60ab8c11dca51a86af692955474`. `lake build AIEFGateCore.CompleteGraphPhase` passed 2213 jobs, no warnings, after fixing an earlier sign error. Six new theorem axiom reports show standard axioms only. An exact two-node value probe distinguishes the specified no-self term from retaining the diagonal. Workspace evidence: `AIEFS_cycle16/CompleteGraphPhase.lean`, `CheckCompleteGraphPhase.lean`, `build_final.log`, `check.log`, `SHA256SUMS.txt`, and `ONE_PAGE_NOTE.md`. This is not a mutation-suite pass; full gate, repo wiring, independent review, push and claim promotion remain outstanding. Suggested next step: independently review and connect the block to an explicit closed-loop model's derivative.
