# Wrap-invariant near-unit EMA condition

**Status:** locally kernel-checked candidate; not deposited, independently reviewed or pushed. Base main: `7865ab19282ceae49df9aa70b396d60ada38d3c2`. The new source imports the prior `EmaNearUnit.lean` candidate, SHA-256 `292d1e7a98cf7ff963ac23873839686562a9cb453140d5f21b2d176589a895ec`, and Mathlib's angle module. No project-owned imports, CI, mutation scripts or prior files were edited.

**Date / UNEXPLAINED:** the session date is stated as 2026-09-11 Atlantic/Reykjavik. The container command `TZ=America/Denver date '+%F %T %Z'` instead reported `2026-11-22 17:10:53 MST`, matching DIRECTION-8's November chronology. These observations conflict. This local draft is not a deposit; its dated MST filing name remains unresolved. Older folders have been left unchanged.

## Ran: proof

For main's zero-start `PhaseCoherence.coherenceTrace`, let Δₖ be the engine-convention input phase for an edge. `near_unit_circular_spread` replaces the previous unwrapped condition `|Δₖ| ≤ β` with the periodic condition

`cos Δₖ ≥ cos β` for every `k < N`.

With `0 ≤ α ≤ 1` and `α^N + 1 − cos β ≤ ε`, Lean proves `‖C_N(i,j)‖ ≥ 1 − ε`. `arcBound_periodic` separately proves the condition is unchanged if any Δ is replaced by Δ + m·2π, for integer m. The condition constrains phasors relative to the **fixed positive real-axis reference**; this is not a theorem about an arbitrary moving center or an assertion that the actual trajectory satisfies it.

## Exact cross-wrap witness — ran Lean

For β = π/60 (3°), choose Δ = 2π − π/60. Lean proves on `Real.Angle` that Δ equals −π/60, proves the new cosine condition, and proves `¬(|Δ| ≤ β)`. Thus the previous sufficient condition rejects this near-aligned, across-the-wrap representative while the new one accepts it. This is an exact example, not a float experiment or claim about a reachable engine trajectory.

## Ran: one targeted mutation

Replaced the definition `arcBound phi beta := cos beta ≤ cos phi` with `arcBound phi beta := |phi| ≤ beta` in a scratch copy of the new file and ran Lean on that copy. The command exited 1: notably `cross_wrap_good` became an unsolved goal `|2π − π/60| ≤ π/60`; periodicity and corollary proofs also failed. The mutation is therefore killed by the proof suite, including the explicit witness. `mutant.log.txt` contains failed-elaboration `sorryAx` reports, which are expected for failed proofs and do **not** describe the final source.

## Verification

Lean 4.33.1: `lake build AIEFGateCore.EmaWrapInvariant` passed **2,220 jobs without warnings**. Five new `#print axioms` reports contain only `propext`, `Classical.choice`, `Quot.sound`. The first build failed on an angle coercion simplification; this was corrected before the final build. No `sorry`, `admit`, new axiom, `native_decide`, `implemented_by` or `unsafe` in the new source. `SHA256SUMS.txt` pins the source and both `.log.txt` files.

Reproduce with the stated base and the prior candidate source:

```sh
cp EmaNearUnit.lean EmaWrapInvariant.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.EmaWrapInvariant
# For the mutant, make a scratch copy with the one replacement described above:
lake env lean AIEFGateCore/EmaWrapMutant.lean  # expected nonzero
```

Main's coherence formalization and the prior near-unit theorem are used, but Python/list/float correspondence is not proved. No bound on derivative approximation, locking, stability or project mutation-suite result is claimed. The DIRECTION-8 inherited rederivations remain open.
