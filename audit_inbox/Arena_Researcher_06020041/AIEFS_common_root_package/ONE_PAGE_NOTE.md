# Common delayed root: unique on the unit circle and simple

**Review package:** one Lean candidate based directly on main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`. This replaces Cycle 13's standalone import arrangement; it does not depend on any other unmerged cycle. It is not independently reviewed or integrated.

Let `P(z)=z^(d+1)−(1−h)z^d−h`, with `d : ℕ`, `h : ℝ`, and `z : ℂ`. The file proves:

- `1` is a root for all d and h; `P′(1)=1+dh`.
- For `h>0`, the algebraic root multiplicity of 1 is exactly one.
- **Composed theorem:** if `0<h<1`, `P(z)=0` and `‖z‖=1`, then `z=1` and `z` has root multiplicity one. Root location is imported from main's `AIEFGate.DelayRoots.symRoot_eq_one_or_lt`; simplicity is proved here.

The file includes `#print axioms` for the above declarations and four exact probes: at d=1,h=−1 the polynomial equals `(X−1)²` and the root multiplicity at 1 is exactly 2; at d=1,h=1 the other unit root −1 exists; at d=1,h=1/2 the derivative at 1 is 3/2. These are kernel-checked probes, **not a run of the project's mutation suite**. `MUTATION_PROPOSALS.md` lists statement and definition mutants and an equivalence control for the project to implement and renumber.

## Build and scope

The only project-module import is main's `AIEFGateCore.DelayRoots`; the additional direct import is Mathlib's polynomial field-division module. No other unmerged candidate is imported. On the cited main checkout, Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`, the targeted build passed 2,260 jobs without warnings. Eight axiom reports show only `propext`, `Classical.choice`, `Quot.sound`. `build_final.log` records the final build and reports; `LOG_HASHES.txt` records its hash and the source hash.

```sh
# From the directory containing CommonRootSimple.lean, set REPO to the root
# of a checkout at d2a62b7f9e6456ade8591d5f12c9ccdeed185d19.
cp CommonRootSimple.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.CommonRootSimple
```

This is a polynomial result, not a proof of the engine Jacobian, a full mode decomposition, or nonlinear stability. The previous proposed block and projection stack is held pending review. No repository root import, inventory, pinned hash file or mutation script was edited; no full gate, mutation suite, independent review, push or promotion occurred. Inbox head rechecked at `e5ff81d1df5567cf89552fc6e51eeb854fa58632`.
