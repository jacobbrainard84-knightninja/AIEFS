# Initialized finite-queue / matrix-circle composition

**Status:** locally kernel-checked research candidate, unreviewed and not pushed. Base main checked out at `7ec6011d5161e7dd105b6db841ed91b6196e88d4`. This file imports, rather than copies, both earlier candidate files. Their local SHA-256 values used in the build were `74d44d87e345712b9df9804811fa6586c759e2dcb215eb80a09659a0458fcb62` (`MatrixPhaseBridge.lean`) and `7ee2029583564959cf88b6acf3593aef442f991a1df7bc6667bb29e19ded9aa0` (`ReachableQueue.lean`). The auditor reports reviewing those candidate hashes. No project imports, CI, guards, registry or frozen evidence were edited.

**Date / UNEXPLAINED:** the session date is stated as 2026-09-11 Atlantic/Reykjavik; the container reported `2026-11-22 06:51:08 MST` using `TZ=America/Denver date '+%F %T %Z'`, while DIRECTION-7 is dated November 21 MST. These conflict. The container reading is reported as observed, not asserted as a validated filing date. The local folder is deliberately unfiled pending reconciliation; do not treat it as an inbox deposit or silently change earlier evidence.

## Ran: composition theorem

`abstractState` embeds `ReachableQueue.State` into the earlier matrix state by reversing the finite queue into newest-first order; the unused tail beyond d is zero. `consistent_transfer` proves that finite consistency implies `MatrixPhaseBridge.Consistent`. `finite_abstract_step` proves **exact real equality** between the finite step and the earlier abstract engine step at each retained queue slot `k ≤ d`, including equality of their phase heads. This is more than applying the old bridge to an unrelated state.

`initialized_trajectory_bridge` starts from d+1 copies of theta and proves that, for any fixed real W, every modeled iterate satisfies the old consistency hypothesis and its next finite queue step equals `matrixStep` on `Real.Angle` for every retained slot, with `d > 0`. No separate consistency assumption or matrix-uniformity hypothesis appears in that theorem. The iteration's output is the theta component of `ReachableQueue.step`; `ReachableQueue.iterate` performs the same `shift` as `step` with that output.

The consistency of a single shift is true by construction: theta and the appended entry are the same output. Its value as an engine bridge depends on the source correspondence, not a nontrivial conservation law.

## Read: correspondence, not Python proof

At the base main engine file `aief_experiment_engine_v1.py`, lines 708–711 zero-initialize coherence and initialize history as d+1 copies of theta; the branch reset repeats the phase/history setup at 941–946. Lines 831–839 read `history[0]`, update and wrap theta; lines 841–844 append the new theta and pop the oldest. These lines were read from the base checkout with `git show`; the file's SHA-256 was `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`.

This is a formal composition **between Lean models**, not a refinement proof for Python lists or NumPy floats. W is supplied and fixed, not a proof about engine weight updates, clipping or projection. The Lean phase head uses a scalar omega, whereas Python accepts an omega array; interpretation is restricted to the matching uniform-frequency case. Neither arbitrary external state mutation nor general list validation, closed-loop trajectories, derivatives or stability are established.

## Ran: verification

Lean 4.33.1, main checkout and the two candidate sources at the hashes above: `lake build AIEFGateCore.QueueComposition` passed **2,193 jobs without warnings**. The two new `#print axioms` reports list only `propext`, `Classical.choice`, `Quot.sound`. No `sorry`, new axiom, `native_decide` or `implemented_by` in the new source. The first build failed on a finite-index simplification; it was fixed and rebuilt. The final log uses the upload-safe `build_final.log.txt` name, and `SHA256SUMS.txt` pins it and the source.

Reproduce from a checkout of the stated main and previously deposited candidate sources:

```sh
cp MatrixPhaseBridge.lean ReachableQueue.lean QueueComposition.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.QueueComposition
```

No mutant suite, full gate, independent review, push or promotion. DIRECTION-7's wrap-invariant EMA corollary and exact wrap witness, gate-form witness, and inherited rederivations remain open. Previous missing `.log` uploads were attributed by the auditor to the inbox ignore rule; this new log is named `.log.txt`.
