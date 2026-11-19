# Exact-real phase reference: directional derivative

**Status:** locally Lean-checked partial bridge, unreviewed and not an engine-correspondence theorem. This is one new Lean file, with no dependencies on the held Cycle 16–20 files. It proves more than basis-direction checks—every real perturbation direction is allowed—but it is a coordinatewise `HasDerivAt` result, not a full `HasFDerivAt` theorem.

## Defined and proved

`EngineStepRef.lean` defines a real-valued phase/history reference step with an externally prescribed uniform scalar weight proposal b, clipped as `max 0 b`, and no active capacity projection. The sine coupling excludes self-edges. Angles are unwrapped reals; history index 0 is newest. Source comments cite engine lines 789–797, 830–839, and 841–844 for the operations being mirrored. The model **freezes the weight proposal**; it does not define the complex EMA or adaptive weight update.

At a synchronized affine history `theta−k dt Ω+t v_k(i)`, Lean proves for every direction v and node i that if `1≤N` and `b>0`, the derivative at t=0 of the reference head is

`(1−(N−1)h)v₀(i)+h[(∑ⱼv_d(j))−v_d(i)]`, where `h=dt b cos(d dt Ω)`.

It also proves that each positive-index history coordinate has derivative `v_(k−1)(i)`. Thus the proposed block is checked **for this fixed-weight reference**, including arbitrary directions. The theorem is deliberately stronger than the physical parameter assumptions in some respects: it does not require d≥1, dt>0, τ=d·dt, the rotating-orbit equation, strict capacity slack, or that Ω defines an actual orbit. Those conditions remain necessary when identifying the reference with the intended engine setting; they are not silently asserted by this Lean result.

The file includes two exact probes: N=2, d=1, Ω=0, dt=1, b=1/2 has derivative 1/2 for an other-node delayed perturbation; a negative scalar proposal is clipped to zero and has derivative 0 in the same direction, whereas an unclipped coefficient would be −1. The clipping probe is for this simplified scalar-proposal model, **not** a proof of the behavior of the full adaptive engine under an active clip. `MUTATION_PROPOSALS.md` proposes but does not execute mutants and an equivalence control.

## Explicit correspondence gaps

For the intended engine bridge one must still prove: (1) theta equals the newest history entry and Python's oldest-first queue matches the reference indexing; (2) local circle charts match the modulo operation, including cut handling; (3) homogeneous ω, no shuffle, a prepared rotating orbit and `τ=d dt`; (4) all off-diagonal proposed weights are positive and the strict capacity test leaves projection inactive; (5) the actual complex EMA and adaptive weight derivatives, restricted to u=w=0, do not contribute a first-order phase term; and (6) fixed-b reference equality to that actual restricted derivative. In particular u=w=0 as a **linearized** restriction does not mean the nonlinear adaptive engine keeps its weights literally frozen along finite perturbations. No active gate, nonlinear stability, heterogeneous frequencies or IEEE-floating-point derivative is covered.

## Verification and reproduction

On main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`, Lean 4.33.1, mathlib `0df444a360eaa60ab8c11dca51a86af692955474`, the final targeted build passed **2,138 jobs without warnings**. The seven in-file axiom reports show only `propext`, `Classical.choice`, `Quot.sound`; both examples compile. No `sorry` or new axiom was used. Earlier failed builds record a bad import and proof elaboration corrections; no full project gate or mutation suite was run.

```sh
# From the directory containing EngineStepRef.lean; REPO is the cited checkout.
cp EngineStepRef.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.EngineStepRef
```

`build_final.log` and the file hash are pinned in `LOG_HASHES.txt`. Only Mathlib modules are imported directly; no unmerged project module or held cycle is imported. Inbox head was `bd725622dac5309fe8e67cce819059b599f3a246`. No tracked project files, root imports, inventory, pinned repository hash lists or mutation scripts were edited; no independent review, push or claim promotion.
