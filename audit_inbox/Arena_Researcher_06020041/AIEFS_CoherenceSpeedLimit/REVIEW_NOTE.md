# AIEFS_CoherenceSpeedLimit — C016 re-derivation

**Status:** local Lean candidate, prepared for owner deposit; not deposited, independently reviewed, or promoted. Base main `7865ab19282ceae49df9aa70b396d60ada38d3c2`. Import: main `AIEFGateCore.PhaseCoherence` only. No project files, root imports, CI, mutation scripts, guards, registries or prior deposits were edited.

**Time basis:** GMT. The container's `date -u '+%F %T GMT'` reported `2026-11-23 01:42:01 GMT`. The session date is stated as 2026-09-11 Atlantic/Reykjavik (GMT at that date). These conflict; the shell reading is an observation, not a validated calendar date. The ZIP is ready for the owner to file with the date the owner determines.

## Ran: one-step reported coherence motion

Lean proves for the actual main `PhaseCoherence.reported` and `coherenceTrace` definitions: if `0 ≤ α ≤ 1` and every initial directed accumulator entry lies in the closed unit disk, then for any edge and time n,

`|Rₙ₊₁(i,j) − Rₙ(i,j)| ≤ min(1, 2(1−α))`.

This is a per-step **speed limit**, not a locking, convergence, or full-engine dynamics result. It is exact-real mathematics and does not account for NumPy rounding. The trace theorem uses main's unit-disk preservation and reported-range lemmas. There is no new assumption about phase locking or a coherence band.

The proof is independently written, not copied from the retired file or main's already-existing `CoherenceMotion.lean`. It takes a different route from the C016 port: use the reverse triangle inequality on the change of a directed magnitude, factor the complex increment as `(1−α)(z−C)`, bound `‖z−C‖ ≤ 2`, average the two directed bounds, then combine with `R ∈ [0,1]`. The one-step bound itself needs only `α ≤ 1` and current directed values in the unit disk; the trace result also needs `α ≥ 0` to inherit unit-disk preservation. It re-derives the core bound, **not** C016's stronger rise/fall envelopes or numerical 1214-step corollaries. Main already contains the C016 result; this is a corroborating alternative proof, not a novelty or a new project claim.

## Ran: exact probes and targeted mutant

* A direct complex-value probe gives change 1 for α=1/2, old accumulator −1 and input +1, showing that replacing `2(1−α)` by `1−α` is false in general.
* A direct probe unfolds main's actual `reported` and `coherenceStep`: with α=1/2, input phasors +1, and asymmetric initial entries `C₀₁=1`, `C₁₀=0`, the report changes from 1/2 to 3/4. The probe uses the two directed magnitudes, not the bound theorem. It is a constructed model state, not a demonstrated Python trajectory.
* In a scratch copy, the directed-motion **statement** was mutated from `2(1−α)` to `1−α`; `lake env lean AIEFGateCore/CoherenceSpeedMutant.lean` exited 1 at the incompatible bound. This is a targeted statement mutant, not a modified-engine run or the project mutation suite. Its failed elaboration reports `sorryAx`; these reports do not describe the final source.

## Verification

Lean 4.33.1: `lake build AIEFGateCore.CoherenceSpeedLimit` passed **2,219 jobs without warnings**. Five new `#print axioms` reports list only `propext`, `Classical.choice`, `Quot.sound`. No `sorry`, `admit`, new axiom, `native_decide`, `implemented_by` or `unsafe` in the new source. Both actual outputs are included under `.log.txt` names; `SHA256SUMS.txt` pins the source, note, and logs.

Reproduce after preparing the base checkout and dependencies:

```sh
cp CoherenceSpeedLimit.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.CoherenceSpeedLimit
# For the mutant, use a scratch copy with the one statement replacement above:
lake env lean AIEFGateCore/CoherenceSpeedMutant.lean  # expected exit 1
```

No full gate, numerical engine run, project mutation suite or independent review was performed. The separate C012 causal-EMA re-derivation was prepared in the preceding `AIEFS_CausalEMATracking` wave. Neither wave proves Python refinement, phase locking, adaptive-weight stability or transient-amplification bounds.
