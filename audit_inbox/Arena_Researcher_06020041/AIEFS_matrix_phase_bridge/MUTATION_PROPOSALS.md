# Mutation proposals — not executed

**Session date:** 2026-09-11, Atlantic/Reykjavik; lead-note date conflicts, so confirm project filing date before upload. **Base:** main `0a6a2f62ea9af147cac60a7be30d85d6b37fe52a`.

Local labels only. A proof-script failure alone is not a semantic kill; the project should implement and run mutations independently.

| Label | Proposed mutation | Expected evidence |
|---|---|---|
| P-S1 | Drop uniform W from `matrix_to_scalar`, keeping the scalar b as the mean. | `nonuniform_counterexample` is an exact Lean inequality at N=3 with mean proved 2; matrix and scalar values are 1 and 2, respectively. |
| P-S2 | Drop theta/newest-history consistency from the circle bridge. | `inconsistent_counterexample` is an exact circle-valued inequality against main's `phaseStep`, for W=0 and k=1. |
| P-D1 | Change the old-history shift `k−1` to `k`. | The unequal-adjacent-history direct example expects π at the shifted slot, while old slot 1 is 0. |
| P-D2 | Replace delayed neighbor input by the current phase input in `matrixHead`. | The direct delayed-angle example evaluates to 1; using the all-zero current phase yields 0. |
| P-E1 | Rewrite the weighted sum as an erased-self sum, assuming W has zero diagonal. | Equivalent on the stated zero-diagonal domain; semantic probes should survive, and a proof may require adaptation. |

None of these mutations has been run or wired. P-E1 is equivalent **under zero diagonal**, not for arbitrary W; use that condition when designing its control.
