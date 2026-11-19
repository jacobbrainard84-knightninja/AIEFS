# Proposed mutation controls — not executed

Local labels, not official project numbers. Apply mutants independently in the project harness; a proof-script failure alone does not establish a semantic kill. Probe declarations are in the candidate file.

| Label | Kind | Mutation | Intended detector |
|---|---|---|---|
| P-S1 | Statement | Remove b>0 from the block theorem without changing its b coefficient. | `clipping_probe`: at b=−1 the clipped derivative is 0 and the unclipped block expression is −1. |
| P-S2 | Statement | Change the orbit shift from `+dt·Ω` to `−dt·Ω`. | At k=1, old current theta must appear; a direct test with dt=Ω=1 refutes the changed statement. The general `orbit_invariant` establishes the correct sign; add the concrete probe to the project harness. |
| P-D1 | Definition | Reverse the sine argument. | `two_node_probe` predicts +1/2; the mutant yields −1/2. Add an independent direct evaluation to avoid relying solely on its proof dependency. |
| P-D2 | Definition | Replace clipping `max 0 b` by b. | `clipping_probe` should fail semantically, since the derivative becomes −1. |
| P-D3 | Definition | Include the self-node in the coupling sum. | `self_coupling_probe` is a direct proof from the definition: the delayed-self direction gives 0, versus 1/2 for the mutant. |
| P-D4 | Definition | Use `x k i` rather than `x (k−1) i` for k>0. | `adjacent_history_probe` is proved directly from the shift definition and distinguishes derivative 3 from 7. |
| P-E1 | Equivalence | Replace `sin(a−b)` by `−sin(b−a)`. | Equivalent by oddness. It should survive direct semantic probes and a suitably adapted proof; proof-script failure is not a semantic kill. |

No mutant or equivalence control has been wired or run.
