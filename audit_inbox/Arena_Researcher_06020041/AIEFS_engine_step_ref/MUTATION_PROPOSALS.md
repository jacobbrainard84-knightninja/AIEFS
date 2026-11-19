# Proposed mutation controls — not executed

Local labels are not project mutation numbers. Each should be applied independently in the project-owned harness with direct evaluation probes where appropriate. A compiler failure of the existing proof alone is not evidence that an equivalent definition is semantically wrong.

| Label | Kind | Proposed mutation | Intended detector |
|---|---|---|---|
| P-S1 | Statement | Remove `0<b` from `head_derivative_block` while retaining its unclipped b coefficient. | `clipping_probe` has b=−1, derivative 0; the proposed unclipped block predicts −1. |
| P-D1 | Definition | Replace the sine argument `x d j−x 0 i` with `x 0 i−x d j`. | `two_node_probe` pins the actual reference derivative at +1/2; the mutant yields −1/2. Ensure the probe evaluates the mutant definition directly. |
| P-D2 | Definition | Replace clipping `max 0 b` with b. | `clipping_probe` should fail semantically: the derivative changes from 0 to −1. |
| P-D3 | Definition | Include the self-node in the coupling sum. | Add a direct N=2 probe whose only nonzero direction is the delayed self-node; baseline derivative is 0, mutant is 1/2. The current `two_node_probe` alone does **not** kill this mutation. |
| P-D4 | Definition | In `phaseStep` use `x k i` instead of `x (k−1) i` for k>0. | `history_derivative` and a new direct probe with unequal adjacent history directions should distinguish the shift. An unchanged proof failing to compile alone is not a semantic test. |
| P-E1 | Equivalence | Replace `sin(a−b)` with `−sin(b−a)` throughout the reference coupling. | Equivalent by oddness of sine; it should survive direct semantic probes and an adapted proof. Proof-script breakage alone must not be counted as a kill. |

No mutant or equivalence control has been implemented or run in this package.
