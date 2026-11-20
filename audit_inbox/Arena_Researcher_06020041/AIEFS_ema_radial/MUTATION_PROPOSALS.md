# Proposed mutation controls — not run

Local proposal labels only. Use independent direct-evaluation/derivative probes in the project harness; proof-script failure alone is not a semantic kill.

| Label | Kind | Mutation | Proposed detector |
|---|---|---|---|
| P-S1 | Statement | Change the magnitude derivative from `αu` to `u`. | `radial_probe` has α=1/2,u=1 and derivative 1/2, not 1; use uniqueness of derivatives and a direct probe of the definition. |
| P-S2 | Statement | Add an angular term `(1−α)δ` to the magnitude derivative. | `angular_probe` has α=1/2,u=0,δ=7 and derivative 0, not 7/2. |
| P-D1 | Definition | Replace the input cosine in `reStep` with sine. | Direct base-value probe at α=1/2 gives 1/2 instead of 1; do not rely only on the original proof failing. |
| P-D2 | Definition | Replace the coefficient `1−α` of the input cosine with `α`. | Direct base-value probe at α=1/4 gives 1/2 instead of 1. |
| P-D3 | Definition | Replace the average in `symMagnitude` by its first directed magnitude. | `asymmetric_probe` gives 3/4 while the one-sided derivative is 1/2; add an independent direct probe in the harness. |
| P-E1 | Equivalence | Reorder `α*(1+t*u)+(1−α)*cos(t*δ)` using commutativity of addition. | Algebraically identical; all semantic probes should pass, with proof adjusted if necessary. |

The candidate probes themselves use the general derivative theorem; the project should add independent direct-evaluation checks where appropriate. None of the mutants has been implemented or run.
