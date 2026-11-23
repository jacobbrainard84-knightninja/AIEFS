# AIEFS_TransientBridge — fixed-weight reference, stable mode with transient growth

**Status:** prepared for owner deposit; not deposited, independently reviewed, or promoted. Base main `7865ab19282ceae49df9aa70b396d60ada38d3c2`; audit-inbox checked at `dc9f6c0d80c33fffe1233ee694bc0bf4960da459`. The folder label uses `date -u +%F`; the container reported `2026-11-23 21:52:48 GMT`. Only main's `AIEFGateCore.EngineStepRef` is imported; there are no unmerged candidate dependencies. No project source, root import, CI, or prior deposit was edited.

## Ran: exact Lean results

For N=3, d=1, dt=1/4, common positive off-diagonal weight b=1, Ω=ω=0, and synchronized phase 1, `reference_mode_link` proves **both** head and retained-history directional derivatives of main's `phaseStep` on the spatial mode `(1,−1,0)`. For arbitrary current/delayed amplitudes `(x,y)` the resulting pair is

`A(x,y) = (x/2 − y/4, x)`, with `A = [[1/2,−1/4],[1,0]]`.

This uses main's `phase_step_head` (itself from `head_derivative_block`) and `history_derivative`; it is not merely an unrelated matrix example. `spatial_energy` proves the six node/queue coordinates of this mode have squared norm `2(x²+y²)`.

* Starting at `(1,0)`, Lean proves squared mode-coordinate norm goes from 1 to 5/4, corresponding to six-coordinate squared norm 2 to 5/2. The norm gain is √5/2 ≈ 1.118.
* `eigenmode_stable` proves any eigenvalue of the complexified two-coordinate update has modulus 1/2. It derives the characteristic equation from the eigenvector equations and proves every root has that modulus. This is for this transverse mode, not the full system; the common-phase mode is neutral.
* `one_step_bound` and `all_steps_bound` prove, for **every** input in this spatial mode and every k≥0, `‖Aᵏp‖² ≤ (81/64)‖p‖²`; thus norm amplification is at most 9/8 (12.5%). This is a rigorous upper bound, not the exact operator-norm supremum.
* `two_step_bound` proves `‖A²p‖² ≤ (1/2)‖p‖²`; `after_first_bound` gives `‖Aᵏp‖² ≤ (81/128)‖p‖²` for all k≥2. Thus only step 1 can exceed the **initial** norm. This does not say every subsequent step decreases monotonically.

The result is a deliberately small transient partly caused by stacking the copied history coordinate; it is not a finding about generic engine behavior. The all-step bounds concern powers of the derived linear mode map. No theorem identifies them with derivatives of nonlinear multi-step Python trajectories.

## Read versus ran; correction on later rises

Read main engine L790–813 (weight update/clip/gate), L830–839 (phase), L841–844 (queue). The fixed-weight/inactive-projection correspondence is source reading, not a proof of Python or float64 behavior. Adaptive-weight derivatives, projected ties, full Fréchet differentiability, arbitrary modes and nonlinear stability are not established.

Ran an independent NumPy matrix-power norm check for k=1,…,8; it gave approximately `1.12384, 0.56192, 0.125, 0.14048, 0.07024, 0.015625, 0.01756, 0.00878`. The overall peak is at step 1 in this check, but the sequence can rise again: for example the norm at k=4 exceeds that at k=3. An exact rational check on p=(1,0) gives energy 1/64 at k=3 and 5/256 at k=4. Both are below the initial energy. This qualifies the auditor's wording that it “never rises again”: it can rise relative to the immediately previous step, although Lean bounds it below its initial level after step 1.

## Ran: required mutants

Two changed-definition scratch copies were checked with `lake env lean`:

1. Queue mutant replaces the second component `p.1` by `0`: exit 1; `reference_mode_link` and the 5/4 witness fail.
2. Step-size mutant changes `stepSize` from `1/4` to `1/2`: exit 1; the unchanged 5/4 witness fails (its new value is 1).

These are targeted Lean definition mutants, not engine mutations or the full project mutation suite. Failed-elaboration `sorryAx` reports in mutant logs are expected and are not final-source axioms.

## Verification

Lean 4.33.1: `lake build AIEFGateCore.TransientBridge` passed **2,149 jobs without warnings**. Nine new axiom reports list only `propext`, `Classical.choice`, `Quot.sound`. No `sorry`, `admit`, new axiom, `native_decide`, `implemented_by` or `unsafe` in the final source. Earlier builds failed on `Fin` simplification and noncomputability declarations; these were fixed before the final build. Logs are `.log.txt`; `SHA256SUMS.txt` pins the source, note and logs.

```sh
cp TransientBridge.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.TransientBridge
# Scratch copies with the exact replacements above:
lake env lean AIEFGateCore/TransientQueueMutant.lean  # expected exit 1
lake env lean AIEFGateCore/TransientDtMutant.lean     # expected exit 1
```

No full gate, project mutation suite, numerical engine run, independent review, push or promotion was performed.
