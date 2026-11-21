# Reachable finite queue consistency — unfiled audit draft

**Status:** locally kernel-checked research candidate, unreviewed; not deposited or pushed. Base main checked out at `d7b9fac600686477babf229ede70a19f1c2dfa13`. Import: main `AIEFGateCore.EngineStepRef` and Mathlib's angle module. No project-owned files changed.

**Date / UNEXPLAINED:** the session's stated date is 2026-09-11 in Atlantic/Reykjavik, whereas the container command `TZ=America/Denver date '+%F %T %Z'` reported `2026-11-20 18:39:17 MST`; the relayed DIRECTION-6 is dated 2026-11-20 MST. These sources conflict. The reported shell reading is an observation, not a validated filing date. Do not submit this draft under a dated inbox filename until the owner resolves the discrepancy. Earlier local audit drafts contain the same 2026-09-11 session date; their filing dates also require reconciliation. No historical deposit was changed.

## Ran: finite model and proofs

`State n d` stores a finite `Fin (d+1)` queue, oldest first. `reverseIndex` maps newest-first lag k to oldest-first index d−k. `shift` drops the oldest and appends an arbitrary output, and sets theta to that output. Lean proves:

* `view_shift`: every nonzero newest-first lag after shifting equals the preceding lag before shifting. This proves the index reversal/shift relationship for all retained lags, not merely a definition-level check.
* `shift_consistent`: the new state is consistent modulo 2π even if the input is not. `reachable_consistent` proves the invariant by induction for every iteration from a consistent initial state, for any state-dependent output function. `step_reachable_consistent` specializes this to the fixed-W engine-shaped head and exact-real wrap.
* `bad_breaks_reference`: an exact circle inequality for a finite inconsistent state, with stored phases π and current theta zero, at lag one versus main's `EngineStepRef.phaseStep`.

The single-step theorem applies to any output, so queue consistency does not depend on weight uniformity or on the phase calculation. The induction is over the explicitly defined Lean transition; it does not assert Python executions have been formalized.

## Ran: verification

Lean 4.33.1 and the base checkout's mathlib: final targeted build succeeded, **2,191 jobs**, no warnings. Five `#print axioms` reports list only `propext`, `Classical.choice`, and `Quot.sound`. No `sorry` or newly declared axiom in the source. An earlier build failed in `view_shift`; that error was fixed before the final build. A second build passed with a line-length warning, which was fixed before the final build. No mutants or full gate were run.

Reproduce after preparing the base checkout and its dependencies:

```sh
cp ReachableQueue.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.ReachableQueue
```

`SHA256SUMS.txt` records source and final build-log hashes. The build log is output from the actual build, not independent verification.

## Read / limits / follow-up

The auditor reports independently reading and matching Python's oldest-first append/pop implementation and independently checking the previous matrix candidate. This cycle did not independently run Python, and the present file does **not** prove a refinement relation to Python lists or floats, nor a Lean composition theorem with the previous `MatrixPhaseBridge.matrix_circle_bridge`; those remain open. In particular, this is not a proof of the full engine, adaptive weights, derivatives, stability, or transient bounds. State theta and the appended entry are exactly equal by the defined update, a deliberately modeled behavior rather than an independently verified Python invariant.

DIRECTION-6 items 2–4 (near-unit EMA bound, independent rederivations of the two inherited lemmas, and gate-form counterexample) were not attempted in this cycle. No independent review, mutation run, push, or claim promotion.
