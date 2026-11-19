# Revised exact-real phase reference: orbit and directional derivative

**Status:** one locally Lean-checked candidate file on main only; unreviewed and not an engine-correspondence theorem. This revises the existing fixed-weight reference rather than adding an adaptive or stability layer.

## Revision

`orbit_invariant` now proves that the synchronized unwrapped history `theta−k·dt·Ω` advances by one step under the reference map, for N≥1 and 0≤k≤d, provided

`Ω = omega + (N−1)·max(0,b)·sin(−d·dt·Ω)`.

It does not prove this frequency equation has a solution or that the adaptive Python state follows the reference map. The earlier arbitrary-direction `HasDerivAt` head/shift results remain. The source-line comments now identify `aief_experiment_engine_v1.py`, the full main SHA and line ranges.

**Sign clarification for review:** with this file's definition `orbitPath(k)=theta−k·dt·Ω`, the correct one-step result is `orbitPath(k)+dt·Ω`, not minus. For k=1, the shifted entry is the old current angle theta; `theta−dt·Ω+dt·Ω=theta`. The minus sign suggested in the review would give `theta−2dt·Ω` in general. The Lean theorem uses the plus sign.

The file adds direct N=2 probes for a delayed **self** perturbation (zero phase-head derivative) and unequal adjacent history perturbations (the k=1 derivative is 3, not the previous k=1 value 7). It replaces the former clipping filler with the explicit comparison: the clipped derivative is 0 while the unclipped block expression evaluates to −1. All are exact Lean declarations, not a mutation-suite run. `MUTATION_PROPOSALS.md` updates the proposed detectors.

## Scope and verification

The reference uses a prescribed clipped scalar weight and unwrapped real phases. It does **not** model the engine's adaptive EMA/weight step, capacity branch, modulo or floating-point semantics. The proof does not establish theta/history consistency for Python, an actual engine orbit, full Fréchet differentiability, or stability. The positive-proposal derivative formula retains the explicit hypotheses in the source; the orbit theorem uses the clipped scalar and does not require positivity. Full details of the frozen-weight limitation remain in the prior reference note.

At main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`, Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`, the final targeted build passed **2,138 jobs without warnings**. Ten in-file axiom reports contain only `propext`, `Classical.choice`, `Quot.sound`. The first revision build failed when an unrestricted rewrite also changed Ω inside a sine; the final proof avoids that rewrite. No `sorry` or new axiom is present. No full gate, mutation suite, network-off independent build, project integration, push or claim promotion.

```sh
# From the directory containing EngineStepRef.lean; REPO is the cited checkout.
cp EngineStepRef.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.EngineStepRef
```

`LOG_HASHES.txt` pins the source and final log. Inbox head rechecked at `d2f62c9f4f3dc039cb5f88af1ea6f59c5bda3837`. No project root imports, inventory, repository hash files or mutation scripts were edited. Held cycles remain held.
