# Cycle 16 — complete-graph phase-block mode bounds in Lean

**Status:** author-checked Lean candidate, not independently reviewed or integrated. This extends Cycle 15's scalar delay-map results to a proposed **node-indexed complete-graph phase block**. It does not prove this block is the derivative of the AIEFS engine.

## What is formalized

For N≥2 nodes and delay d, define a complexified linear phase-history step with m=N−1:

- head: `x⁺₀(i) = (1−m h)x₀(i) + h[∑ⱼ x_d(j) − x_d(i)]`;
- history: `x⁺ₖ(i) = xₖ₋₁(i)` for k>0.

Lean proves that total-minus-self equals the complete-graph neighbour sum, then formally reduces the block to Cycle 15's scalar map in two cases:

1. If the delayed slice has zero node sum, every **nonzero pointwise eigenmode** has |z|<1, provided h>0 and mh<1. This includes N=2.
2. If the delayed slice is node-constant, every nonzero pointwise eigenmode has |z|≤1, with only z=1 possible on the unit circle, under the same parameter conditions.

The hypotheses concern the delayed slice; nonzero means some node/history coordinate in 0,…,d is nonzero. The conclusions use pointwise eigenrelations on those coordinates, not a Mathlib `Matrix` spectrum. The file does **not** prove every eigenmode decomposes into these classes, neutral-root simplicity, or nonlinear stability. More importantly, the block is supplied as a definition: the full engine's derivative, EMA/weight coupling, projection branch and its correspondence to this definition are **not formally established**. It is not a result for heterogeneous frequencies or ordinary production runs.

## Evidence

On a fresh sparse main checkout `c9863e1c391a9f39cc8cef680a2fa349378b6cfe`, with Lean 4.33.1, mathlib `0df444a360eaa60ab8c11dca51a86af692955474` and the unmerged Cycle 15 `DelayModeMain.lean`, `lake build AIEFGateCore.CompleteGraphPhase` passed: 2213 jobs, no warnings (`build_final.log`). Six new theorem axiom reports contain only `propext`, `Classical.choice`, `Quot.sound` (`check.log`). The check file also proves a two-node value probe where retaining the self term changes the head from 0 to 1/2; it is not a mutation-suite run. The first build failed because an equality was used with the wrong sign; it was corrected and the final source rebuilt. No full gate, `Matrix`/Jacobian proof, independent review, wiring, push or claim promotion.

```sh
# In the cited main checkout, copy Cycle 15 DelayModeMain.lean and Cycle 16
# CompleteGraphPhase.lean to lean/AIEFGateCore/AIEFGateCore/; copy the check
# file to lean/AIEFGateCore/.
cd lean/AIEFGateCore
lake build AIEFGateCore.CompleteGraphPhase
lake env lean CheckCompleteGraphPhase.lean
```

`SHA256SUMS.txt` pins the new source, check, dependency and final logs. Main and inbox heads were rechecked as `c9863e1…` and `2e63035…`. Old privacy-flagged compare files are excluded. The next high-value step is to connect this proposed block to a **precisely defined closed-loop model and its derivative**, rather than infer stability from these conditional eigenvalue bounds.
