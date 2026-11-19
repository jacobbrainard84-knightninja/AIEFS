# Mutation proposals — not implemented or run

Local labels only; project maintainers should assign official numbers after M109 / E17 / §15. These proposals are not a mutation-suite result. Apply each in isolation in a scratch copy, run the project's actual mutation harness, and distinguish semantic refutation from a proof-script compilation failure. The named probes are in `CommonRootSimple.lean` unless noted.

| Label | Kind | Proposed mutation | Intended detector / expected outcome |
|---|---|---|---|
| P-S1 | Statement | Remove `0<h` from `root_multiplicity_one` (all real h). | `negative_parameter_double_root` proves multiplicity 2 at d=1,h=−1; a correct general theorem would contradict it. |
| P-S2 | Statement | Replace `h<1` with `h≤1` in `unit_circle_root_unique_and_simple`. | `upper_boundary_other_unit_root` proves −1 is a distinct unit root for d=1,h=1; the weakened statement is false. |
| P-S3 | Statement | Replace the derivative's `1+dh` with `1−dh` in `derivative_at_one`. | `derivative_probe` at d=1,h=1/2 pins the actual value to 3/2, not 1/2. A robust mutant test should evaluate the definition directly rather than rely only on the mutated theorem. |
| P-D1 | Definition | In `commonPoly`, replace the constant `−C h` with `+C h`. | `common_root` and direct evaluation at d=1,h=1/2 should fail: the mutated value at 1 is 1, not 0. |
| P-D2 | Definition | Replace `(1−h)` by `(1+h)` in `commonPoly`. | `common_root` and direct evaluation at d=1,h=1/2 should fail: the mutated value at 1 is −1, not 0. |
| P-D3 | Definition | Replace the leading `X^(d+1)` with `X^(d+2)`. | `derivative_at_one` and `derivative_probe` should fail: at d=1,h=1/2 the mutated derivative is 5/2, not 3/2. |
| P-E1 | Equivalence control | Replace the leading `X^(d+1)` with `X^d * X`, changing no other mathematics. | This is algebraically identical. It should survive semantic probes and a proof adapted to the equivalent representation. A proof-script-only failure must not be counted as a successful semantic kill. |

`h=0` is **not** a counterexample to simplicity or uniqueness of the unit root; do not use it as a supposed kill for positivity. The suite must implement independent evaluations where appropriate and include the baseline plus equivalence control; none of that wiring is supplied here.
