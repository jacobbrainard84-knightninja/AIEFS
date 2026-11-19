# Cycle 20 — from complete-graph node histories to the Lean invariant

**Status:** locally kernel-checked research candidate, not independently reviewed or integrated. This cycle closes two specific gaps in Cycle 19: its arbitrary tail is now read from a consistently shifted queue, and its scalar aggregates are derived by summing a stipulated node-indexed complete-graph linear step. It does **not** derive that step from the engine.

## Formal result

For N nodes, natural-number delay d, and real parameters h, ρ, α, κ, g, define histories `x_k(i)`, node quantities `u_i,w_i`, and `q=(N−1)h` (the Lean expression is `((N:ℝ)−1)h`; for N≥1 these agree). The stipulated step is

- `w⁺ᵢ=ρwᵢ+καuᵢ`, `u⁺ᵢ=αuᵢ`;
- `x⁺₀(i)=(1−q)x₀(i)+h[∑ⱼx_d(j)−x_d(i)]−g w⁺ᵢ`;
- `x⁺_k(i)=x_(k−1)(i)` for k≥1.

Lean proves the total neighbour identity and that **summing this node step commutes with the scalar queue step**, without an eigenmode or symmetry assumption on the node perturbations. It proves that a consistent queue's history sum transforms as `S⁺=S+X₀−X_d`. Composing these facts with Cycle 19 yields a conserved quantity for every finite iterate of this node-indexed model. Here X, S, U and W are **sums over nodes** (not means); F is

`F=(1−ρ)(1−α)(X₀+qS)−g[ρ(1−α)W+καU]`.

The proof covers d=0 as well as positive delays and does not require positivity or nonzero-denominator hypotheses, because F is denominator-cleared. The model stores a function on natural indices, but each step and invariant use only 0,…,d; the retained entries are shifted consistently. This is an exact-real linear model, not floating-point execution.

## Evidence and boundaries

On sparse main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`, Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`, the final targeted build passed **963 jobs without warnings** (`build_node_final.log`). Six theorem axiom reports contain only `propext`, `Classical.choice`, `Quot.sound`; the check file additionally compiles exact d=0 and d=2 history-sum examples. First queue build failed on a simplification detail and was corrected. The exploratory first node build used a temporary `sorry`; it was removed before the final build, and no `sorry` or `admit` remains in the delivered sources. The first completed node proof attempt also needed a sum simplification. These are not mutation-suite or full-gate results.

The U and W updates above are **stipulated**. It has not been proved that the Python engine's EMA, symmetric weight update, nonlinear phase map, clipping/projection, or their derivatives induce this node model. Nor does this show convergence, characterize a matrix spectrum, prove neutral-root simplicity, establish nonlinear stability, or treat heterogeneous frequencies or production trajectories. Cycle 18's engine finite differences remain separate numerical evidence, not a Lean bridge.

## Reproduce

```sh
# From the directory containing the three candidate sources and check file,
# set REPO to the cited checkout's root.
cp NeutralProjection.lean QueueNeutral.lean NodeQueueNeutral.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cp CheckNodeQueueNeutral.lean "$REPO/lean/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.NodeQueueNeutral
lake env lean CheckNodeQueueNeutral.lean
```

The inbox head was `2e63035c1c973ff07e8124e3ca9b8e198b4e5171`. No tracked project files were modified, no push or promotion was made. Suggested next step: derive the node aggregate equations from a precisely defined smooth interior closed-loop map, including the symmetrized EMA-to-weight update, before asserting an engine correspondence.
