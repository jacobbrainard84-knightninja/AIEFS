# Conditional near-unit EMA bound — unfiled audit draft

**Status:** locally kernel-checked candidate; not independently reviewed, deposited, or pushed. Base checkout: main `d7b9fac600686477babf229ede70a19f1c2dfa13`. This is a new file importing main's `AIEFGateCore.PhaseCoherence`; project files, CI, root imports and mutation scripts were not edited.

**Date / UNEXPLAINED:** the session date is stated as 2026-09-11 in Atlantic/Reykjavik, while the container command `TZ=America/Denver date '+%F %T %Z'` returned `2026-11-20 20:30:17 MST`, consistent with the relayed direction's November chronology but conflicting with the session date. The command is an observation, not a validated filing date. Keep this draft unfiled until the date is reconciled; do not silently revise prior deposits.

## Result — ran Lean build

For the actual `PhaseCoherence.coherenceTrace` starting from zero, fix a directed edge i,j and N updates. Let `0 ≤ α ≤ 1`. If each of its input phasors for `k < N` has real projection at least `1 − δ`, with `δ ≥ 0`, Lean proves

`‖C_N(i,j)‖ ≥ (1 − α^N)(1 − δ) ≥ 1 − (α^N + δ)`.

Thus the explicitly checked budget `α^N + δ ≤ ε` implies `‖C_N(i,j)‖ ≥ 1 − ε`. The first inequality also holds for an arbitrary real projection lower bound L, without requiring L nonnegative. The proof imports and uses main's definitions, not a separate EMA definition.

The stronger source-convention corollary `near_unit_of_phase_spread` uses main's `input_engine_convention`: if, for every `k < N`,

`|phaseTrace(k,i) − phaseTrace(k−d,j) − ((ω i + ω j)/2) τ| ≤ β ≤ π`,

then one may take `δ = 1 − cos β`. The absolute-angle condition is around the fixed real-axis reference zero, on the displayed real representatives, not a general moving or arbitrary-center circular-arc result. The result is conditional on this bound; it does not establish that the engine's phases satisfy it. For N=0 the input condition is vacuous and the budget prevents an unjustified nontrivial conclusion.

## Concrete arithmetic check — ran Python rational arithmetic

For α = 1/2, N = 4 and δ = 1/16, the startup term is 1/16 and the budget ε = 1/8 yields lower bound 7/8; the sharper product bound is 225/256. This checks arithmetic only, not a concrete phase trajectory or a mutant.

## Verification and limitations

Lean 4.33.1: `lake build AIEFGateCore.EmaNearUnit` passed **2,219 jobs with no warnings**. All four candidate `#print axioms` reports list only `propext`, `Classical.choice`, `Quot.sound`. Source contains no `sorry` or new axiom. The first proof build failed due to a complex-real projection lemma mismatch; it was fixed before the final successful build. `SHA256SUMS.txt` hashes the source and final log.

Reproduction after preparing the base checkout and dependencies:

```sh
cp EmaNearUnit.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.EmaNearUnit
```

The theorem concerns main's exact-real model, not a proof of Python execution or IEEE rounding. Its estimate bounds coherence magnitude, not the error in the earlier unit-coherence derivative; that approximation requires a separate derivative-error result. It does not establish locking, stability or attainment of the phase-spread hypothesis. No mutation suite, full gate or independent review was run. DIRECTION-6's inherited results and gate-form witness remain open; the earlier finite queue candidate still lacks a Lean composition theorem with the previous matrix bridge.
