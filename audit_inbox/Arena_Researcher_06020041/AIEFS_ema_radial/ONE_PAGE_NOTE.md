# Directed EMA magnitude: a Lean-checked directional step

**Status:** locally kernel-checked research candidate, not independently reviewed or integrated. Main has advanced to `63e06d76bafa6d8e3627d31fbbbf5cb4499ae49d`; both `CommonRootSimple.lean` and `EngineStepRef.lean` are present there. This is a new, independent one-file candidate, not a resubmission of the held cycles.

## Result

At a unit normalized coherence, suppose the old directed EMA and instantaneous input follow the prescribed paths

`old(t)=1+t(u+i v)`, `input(t)=cos(t δ)+i sin(t δ)`,
`new(t)=α old(t)+(1−α) input(t)`.

For arbitrary real α,u,v,δ, Lean proves using `HasDerivAt` at t=0:

- the real component has derivative `αu` and the imaginary component has derivative `αv+(1−α)δ`;
- the **magnitude** has derivative `αu`, independent of the angular direction δ and imaginary EMA direction v;
- the average of two such directed magnitudes has derivative `α(u₁+u₂)/2`.

It also proves that the square-root expression equals the complex norm of the defined real/imaginary pair. Concrete exact probes check a radial derivative 1/2, zero angular-only derivative, and asymmetric averaged derivative 3/4. These are directional one-variable results, not a Fréchet theorem. The base magnitude is 1, so the square root is differentiated away from its singular point. The output is a statement about the **prescribed normalized path**, not yet about all engine states.

## Connection and gaps

The definitions mirror the EMA-before-magnitude and directed-magnitude averaging at `aief_experiment_engine_v1.py` lines 735–750 on the cited main. The intended interpretation is to divide both the old accumulator and instantaneous input by a common unit orbit phasor. However, the file does **not** prove its real-component path is identical to main's `PhaseCoherence.coherenceStep` or Python's complex update, nor does it derive δ from current/delayed phase histories. Diagonal masking, weight update, clipping, gate branches, modulo, floating-point behavior, full network derivatives and stability remain outside the theorem. No conclusion about generic trajectories or production behavior follows.

## Verification

Lean 4.33.1, mathlib `0df444a360eaa60ab8c11dca51a86af692955474`, cited main checkout: final targeted build passed **2,139 jobs without warnings**. Ten axiom reports contain only `propext`, `Classical.choice`, `Quot.sound`. The first attempt failed on proof simplification; fixes were rebuilt. No `sorry` or new axiom remains. The exact probes are not a mutation-suite run; proposed mutants and an equivalence control are in `MUTATION_PROPOSALS.md`.

```sh
# From the directory containing EmaRadialRef.lean; REPO is the cited checkout.
cp EmaRadialRef.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.EmaRadialRef
```

Only Mathlib modules are directly imported. `LOG_HASHES.txt` pins the candidate and final log. Inbox head was `520924b89c94af0a57f8e56b858a185ca52422d1`. No full gate, mutation suite, independent review, project wiring, push or promotion. Recommended next review: verify the normalization and then prove its relation to the existing main `PhaseCoherence` definitions before composing with the phase reference.
