# AIEFS_EMAFiniteSum — C012 recursive/finite-sum equivalence

**Status:** prepared for owner deposit; not deposited, independently reviewed, or promoted. Base main `7865ab19282ceae49df9aa70b396d60ada38d3c2`. Audit-inbox checked at `de347c6222b3acff9216870381e7889c3860dc54`; DIRECTION-10 was the latest direction in the lead folder. This file depends on the earlier candidate `CausalEMATracking.lean`, which is not on main. An unchanged copy is included solely as a build dependency, SHA-256 `21493f2821130734c1fe900454be57769ec38991506b755290f53f111f1ec958`. No project file or prior deposit was edited.

**GMT:** session date 2026-09-11. UNEXPLAINED: container clock read `2026-11-23 19:54:16 GMT`, conflicting with that date.

## Ran: finite-sum equivalence

For the previous recursive definition `budget₀ = E`, `budgetₙ₊₁ = α budgetₙ + driftₙ`, Lean proves for **every real α and E** and arbitrary real-valued drift:

`budgetₙ = αⁿ E + ∑ₖ₌₀ⁿ⁻¹ α⁽ⁿ⁻¹⁻ᵏ⁾ driftₖ`.

The index is chronological: at n updates, the freshest drift has weight 1 and the oldest has weight αⁿ⁻¹. The identity needs no α nonnegativity, upper bound, or division. The file then applies the earlier `delayed_tracking_bound` and rewrites its recursive budget to prove the explicit finite-sum C012 form against main's wrapped delayed-input model, with the existing hypothesis `α ≥ 0`. The original finite-time bound was already in the earlier candidate; this wave proves the previously unformalized equivalence and makes the explicit form available. It does not establish phase locking, decay of drift or Python refinement.

## Ran: probe and mutation

An exact definition-level probe has α=2, E=0, n=3, and only the oldest drift equal to 1: the budget is 4. Another Lean theorem proves this chronological sum is unequal to the reversed-power sum `∑ αᵏ driftₖ` (4 versus 1). α=2 is an **abstract algebraic test**, not an engine-valid EMA parameter.

One targeted statement mutant replaced the exponent `n−1−k` with `k` in `budget_eq_finite_sum`, retaining the rest of the file. Lean exited 1 at the invalid induction and at the resulting downstream rewrite. A renamed **unmutated** copy, checked separately with the same `lake env lean`, exited 0. The mutant is a changed theorem statement, not a modified engine or project mutation suite. `sorryAx` appears in the failed mutant's diagnostics because elaboration failed; it is absent from the final candidate's axiom reports.

## Verification

Lean 4.33.1: `lake build AIEFGateCore.EMAFiniteSum` passed **2,220 jobs without warnings**. Four new `#print axioms` reports list only `propext`, `Classical.choice`, `Quot.sound`. No `sorry`, `admit`, new axiom, `native_decide`, `implemented_by` or `unsafe` occurs in the new source. The build, mutant, and control outputs are included as `.log.txt` files. `SHA256SUMS.txt` pins the included dependency, new source, note and logs.

Reproduce after preparing the stated base checkout and its dependencies:

```sh
cp CausalEMATracking.lean EMAFiniteSum.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.EMAFiniteSum
# In scratch copies, respectively change the equivalence exponent as described
# above and leave a renamed copy unmodified:
lake env lean AIEFGateCore/EMAFiniteMutant.lean   # expected exit 1
lake env lean AIEFGateCore/EMAFiniteControl.lean  # expected exit 0
```

No full gate, numerical engine experiment, or independent review was performed. The previously completed product-gate engine mutant is in the separate `AIEFS_GateMutation` wave.
