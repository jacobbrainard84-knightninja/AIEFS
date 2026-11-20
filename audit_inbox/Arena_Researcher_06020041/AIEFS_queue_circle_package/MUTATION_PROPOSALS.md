# Proposed controls — not executed

Local labels only; project owns official numbering and wiring. A proof compilation failure alone is not a semantic kill. Direct test probes should evaluate the candidate definition independently.

| Label | Mutation | Expected detector |
|---|---|---|
| P-S1 | Remove uniform off-diagonal B from `circle_phase_step`. | The N=3 nonuniform example is numerical evidence of a counterexample; add an exact Lean counterexample with convenient angles before claiming a formal kill. |
| P-S2 | Remove input consistency from `circle_phase_step`. | A constructed state with theta unequal to newest history has a mismatched k=1 shift; add an exact circle-valued witness. The old N=2 engine check is finite numerical evidence only. |
| P-D1 | Set `step` history k>0 to old history k instead of k−1. | Add a direct unequal-adjacent-history value probe; k=1 differs from the reference. |
| P-D2 | Use old theta rather than delayed history in the sine. | Add a direct case with different old and current phases. |
| P-E1 | Write the unwrapped head sum as total-minus-self instead of an erased-neighbor sum under diagonal-zero weights. | Equivalent under the theorem's B hypothesis; semantic controls should pass, with proof adapted if necessary. |

No mutants or equivalence controls have been executed.
