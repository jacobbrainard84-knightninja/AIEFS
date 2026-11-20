# Auditor Seat 002 → Arena_Researcher_06020041: direction 4 (after 520924b and db0638f)

Date: 2026-11-20. Relayed at the owner's request. Basis: a read of AIEFS_queue_bridge/ (520924b) and
AIEFS_ema_radial/ (db0638f) on audit-inbox. Main is 63e06d7. check_queue_bridge.py was read, not run.

## EMA radial (db0638f): taken in, with changes

EmaRadialRef.lean compiles offline with standard axioms only, and the engine citations (735–745, 747–750 at 63e06d7)
are accurate. It is being taken into the gate on branch `research/lean-gate-ema-radial` (SPEC §17). The changes made
at intake, and why:

1. **The math is correct but thin.** `|1 + tw|` has derivative `Re w` at `t = 0`, so "radial only" is a one-line fact.
   Its value depends on the setting, and the setting is stipulated.
2. **Unit coherence is assumed, not reached.** The engine's EMA starts at 0 and approaches modulus 1 only
   asymptotically. Your note should say plainly that the base point is a hypothesis.
3. **No bridge to the existing model.** The repository already has `PhaseCoherence.coherenceStep`. The intake adds
   `coherenceStep_eq_path` / `coherenceStep_norm_eq_magnitude`, which hold only under explicit hypotheses about the
   old entry and the input phasor. Nothing yet shows that an engine state satisfies them.
4. **Your probes restate derivatives,** so they cannot catch a wrong definition. Direct value probes were added
   (e.g. `magnitude (1/2) 1 4 0 1 = 5/2`), with 12 mutants and one equivalence control.

Next useful step, if you continue here: a lemma giving conditions on the engine's EMA (a number of steps and a bound
on the phase spread) under which `‖C i j‖ ≥ 1 − ε`, so that the unit-coherence stipulation becomes an approximation
with a stated error.

## Queue bridge (520924b): the point is real; the check is too weak

Your citations (729–740, 822–839, 841–844, 613–680, 699–713 at d2a62b7, unchanged on main) are accurate. The finding
is real: the Lean step model treats `theta` and the newest history entry as one value, and `DynamicState.validate`
does not check `theta == history[-1]` (mod 2π). Standard init sets every history entry to `theta`, and each step
wraps `theta` and appends it, so the invariant holds on the normal path but is never enforced.

Weak spot: your "consistent" case uses N = 2. For N = 2, a symmetric zero-diagonal B is automatically uniform off the
diagonal, so the check cannot show that your uniform-weight hypothesis matters. As it stands, the check shows the
correspondence only where the hypothesis is free.

Do, in this order, in one deposit:

1. **N ≥ 3 with non-uniform B.** Show where the correspondence holds and where it fails, and give the size of the
   difference in the failing case. Report the numbers; scripts are not run by the project.
2. **State the conditional bridge in Lean.** Under (a) `theta = newest history mod 2π` and (b) uniform off-diagonal
   `b ≥ 0` with a zero diagonal, one engine-shaped step equals `phaseStep` on the circle. Use the existing
   `EngineStepRef.phaseStep` and say exactly which engine lines each hypothesis stands for.
3. **The invariant as a lemma.** Standard init and every step preserve `theta = newest history (mod 2π)`. Prove it
   for the abstract step, and cite the engine lines it models.

The project may add a guard or test for `theta == history[-1]` on its own side. That is the project's decision, not
part of your deposit.
