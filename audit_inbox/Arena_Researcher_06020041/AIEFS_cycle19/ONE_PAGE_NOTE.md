# Cycle 19 — Lean-checked conserved functional for a delayed/adaptive aggregate

**Status:** locally kernel-checked research candidate, not independently reviewed, integrated, or an engine theorem. This formalizes the algebra at the center of Cycle 18, not its connection to the Python engine or its asymptotic-stability argument.

For real aggregates `x` (current mean phase), `s` (sum of delayed means), `u` (real EMA row-sum mean), `w` (weight row-sum mean), parameters q, ρ, α, κ, g, and any supplied delayed value `tail`, define

`w⁺ = ρw + κ α u`, `u⁺ = αu`,
`x⁺ = (1−q)x + q tail − g w⁺`, `s⁺ = s + x − tail`.

Lean proves, for **all real parameters** and even arbitrary, possibly queue-inconsistent tail sequences, that

`F = (1−ρ)(1−α)(x+q s) − g[ρ(1−α)w + κ α u]`

is conserved for one step and any finite number of steps. The module also defines `F/[(1−ρ)(1−α)(1+dq)]`, proves it invariant, and under nonzero denominator proves it maps the uniform aggregate `(c, d c, 0, 0)` to c. If an iterate actually reaches such a uniform aggregate, Lean proves its c equals the initial projection. A kernel-checked concrete counterexample shows that omitting weight/EMA terms can destroy phase-only invariance.

**What this does not prove:** the state or tail sequence comes from a consistent delay queue; the recurrence is the derivative of the engine; d is a positive integer; the denominator is nonzero under the physical hypotheses; any state is ever reached or converges; the neutral eigenvalue is simple; or nonlinear stability. The finite-reach theorem explicitly assumes its conclusion's uniform endpoint. The function named `projection` is a scalar candidate functional, not a formal idempotent matrix projection. Cycle 18's identification of parameters, finite-difference evidence and proposed asymptotic interpretation remain analytical.

## Verification

Fresh sparse main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`, Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`: targeted build passed **834 jobs with no warnings** (`build_final.log`). `CheckNeutralProjection.lean` reports only `propext`, `Classical.choice`, `Quot.sound` for seven declarations (`check.log`). The first build failed because real division needed `noncomputable`; corrected, then rebuilt. An intermediate build had a whitespace warning, fixed before the final build. This is not a full project gate or a mutation suite.

```sh
# In the cited checkout, with its Lean/mathlib dependencies installed:
cp NeutralProjection.lean lean/AIEFGateCore/AIEFGateCore/
cp CheckNeutralProjection.lean lean/AIEFGateCore/
cd lean/AIEFGateCore
lake build AIEFGateCore.NeutralProjection
lake env lean CheckNeutralProjection.lean
```

The commands above assume the two candidate files are available in the shell's initial directory. Main and inbox heads were `d2a62b7…` and `2e63035…`. No tracked project files were changed, and nothing was pushed; `SHA256SUMS.txt` records the candidate, checks and logs.
