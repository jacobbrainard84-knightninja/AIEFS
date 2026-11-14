# Cycle 3 — phase/delay-dependent coherence theorems (one-page note)

**File:** `lean/AIEFGateCore/AIEFGateCore/PhaseLockCoherence.lean` (new, 147 lines)
**Compile command:** `cd lean/AIEFGateCore && SKIP_CACHE=1 ./check_lean_gate.sh` (7-step gate), or `lake build AIEFGateCore.PhaseLockCoherence` for the single module. Toolchain `leanprover/lean4:v4.33.1`.

## Why this cycle

The 040282 direction note's second rule: *"the next result has to actually use the phases or the delay, for example a condition under which R can only go up."* c016 (`CoherenceMotion`, Cycle 2) was a speed limit that holds for any unit-norm input sequence. This file uses the real phase trace and the delay queue.

## The three theorems

1. **`coherenceInput_constant_after_lock`** — if phase increments `u n i = 0` for all `n ≥ N`, then `coherenceInput d x0 u omega tau (n+1) i j = coherenceInput ... n i j` for all `n ≥ N + d`. Proved from `Phase.delayed_input_step` (ratio of successive input phasors) and `Phase.delayedIncrement` (which reads `u (n - d)`). The delay `d` sets the startup-to-live boundary: the proof needs both `d ≤ n` and `N ≤ n - d`. Replacing `N + d` by `N` makes this proof fail at two arithmetic obligations. This does not prove the stronger statement false.
2. **`coherenceTrace_geometric_of_constant_input`** — if `coherenceInput` is constant `z` from `n0` on, then the EMA error obeys the exact identity: `C_{n0+k} − z = α^k (C_{n0} − z)`. The theorem assumes constant input separately; it has not been formally composed with (1). It implies contraction only when |α| < 1.
3. **`coherenceStep_norm_mono_of_aligned`** — if the EMA state is aligned with the phase/delay-derived input `z` (`C i j = (r : ℂ) * z`), `0 ≤ r ≤ 1`, `0 ≤ α ≤ 1`, `‖z‖ = 1` (from `input_norm`), then `‖C i j‖ ≤ ‖coherenceStep α C … n i j‖`. This concerns a directed magnitude, not the symmetrised reported R.

## Honest scope (in the module docstring)

Exact reals. The locking hypothesis is **assumed, not derived** from the closed-loop dynamics — this is not a phase-locking proof (O1 remains open). No float64, no Lean/Python equivalence, no `B` convergence, no `reported` symmetrisation or zero-diagonal claim, no statement about `C j i` or later steps. `AUD-RATELAW stays UNEXPLAINED`.

## Wiring

`phase_lock_coherence.patch` (5 files): new module; one root import; `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` regenerated (25 → 26 entries); README paragraph and new SPEC §11.9. **No change to the mutation suite**: adding an M60 entry is an owner follow-up (see below). `registry/artifacts_current.csv` is excluded — regenerate with `python3 registry/reconciliation/build_current_inventory.py` in a full clone.

## Verification

See `DELTA_AUDIT.md`. Local: module compiles with 0 warnings; `#print axioms` on all three declarations gives only `propext`, `Classical.choice`, `Quot.sound`; the delay-dropping semantic mutant fails with a real proof failure; full `check_lean_gate.sh` result recorded there.

## Next step

Derive the constant-input hypothesis from an actual closed-loop locking condition rather than assuming it, or extend (3) to `reported` with symmetrisation and the zero diagonal. Both are O1-adjacent and must keep explicit hypotheses. A semantic mutant M60 (drop `+ d`) can be added to `lean_mutation_check.py` with `false_constant_after_lock_no_delay` when the full suite is run by CI.
