# AIEFS_CausalEMATracking — C012 re-derivation

**Status:** local research candidate, prepared for owner deposit; not deposited, independently reviewed, or promoted. Base main `7865ab19282ceae49df9aa70b396d60ada38d3c2`. Import: main `AIEFGateCore.PhaseCoherence` only. No project file, mutation script, root import, guard, CI, registry, or existing deposit was edited.

**Time basis:** GMT, as requested. The environment's `date -u '+%F %T GMT'` reported `2026-11-23 00:34:18 GMT`. The session date is stated as 2026-09-11 in Atlantic/Reykjavik (also GMT at that date). These conflict; the shell reading is recorded as an observation, not silently asserted to be the validated calendar date. No dated inbox filename is included; owner may choose the filing date when depositing.

## Ran: C012-style causal tracking

For a directed entry of main's `PhaseCoherence.coherenceTrace`, let `zₙ = coherenceInput … n`, `Cₙ = coherenceTrace … n`, and `eₙ = Cₙ − zₙ`. Lean proves the exact identity

`eₙ₊₁ = α eₙ − (zₙ₊₁ − zₙ)`.

The freshest input motion has coefficient **1**, not `1−α`. Lean then proves a delayed-phase tracking bound for every finite n and every `α ≥ 0`:

`‖eₙ‖ ≤ budgetₙ`, where `budget₀ = ‖e₀‖` and
`budgetₙ₊₁ = α budgetₙ + |uₙ(i) − delayedIncrement(d,u,n,j)|`.

The delayed increment is main's `Phase.delayedIncrement`: zero for `n < d`, then `u_(n−d)(j)`. This uses main's circular chord bound, not Euclidean differences between wrapped representatives. The recursive budget expresses chronological weights, with the newest drift unscaled; this file does not separately formalize the equivalent finite-sum expression. The argument allows α=0 and α=1 without division. Engine configuration permits `0 < α ≤ 1`, so α=0 is an abstract endpoint, not a valid engine parameter.

A direct exact Lean value probe takes α=1, old C=old z=1 and new z=−1: the new error norm is 2 even though `1−α=0`. The probe checks the EMA expression directly; it is an abstract unit-input example, not an engine trajectory test.

## Difference from inherited work — read and re-derived

The retired researcher's C012 report was read for its theorem and causal indexing. This is a newly written proof against main's `coherenceTrace`, `coherenceInput`, and `Phase.delayed_input_chord_bound`: it uses a recursive budget rather than the original finite-sum definition, and does not copy or import the retired file. Main's phase transport/chord theorem is a dependency, not re-proved here. C016's reported-coherence one-step bound was **not** re-derived in this cycle and remains open for the lane.

## Ran: verification and mutant

Lean 4.33.1: `lake build AIEFGateCore.CausalEMATracking` passed **2,219 jobs without warnings**. Four `#print axioms` reports list only `propext`, `Classical.choice`, and `Quot.sound`. No `sorry`, `admit`, new axiom, `native_decide`, `implemented_by` or `unsafe` appears in the candidate source.

One targeted **statement mutant** was tested in a scratch copy: multiply the input-motion term in `tracking_identity` by `1−α`. `lake env lean AIEFGateCore/CausalEMAMutant.lean` exited 1; the identity and downstream calculation failed. This is not a modified-engine run or the project mutation suite. The failed elaboration naturally reports `sorryAx`; those reports are not from the final candidate. Both outputs are included under `.log.txt` names, with SHA-256 pins.

Reproduce after preparing the base checkout and dependencies:

```sh
cp CausalEMATracking.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.CausalEMATracking
# Scratch mutant: change the identity's drift term as described above.
lake env lean AIEFGateCore/CausalEMAMutant.lean  # expected exit 1
```

No full gate, numerical engine experiment, or independent verification was run. This is a finite exact-real model bound, not proof of Python/float correspondence, closed-loop phase locking, decay of input drift, or convergence of coherence.
