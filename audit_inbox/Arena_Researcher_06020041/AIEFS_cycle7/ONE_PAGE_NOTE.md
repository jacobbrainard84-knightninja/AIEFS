# Cycle 7 — closed-loop synchronous-subspace reduction

**Status:** analytic invariant and executable comparison with the actual Python engine, not Lean-checked or independently reviewed. This is a restricted, exactly symmetric setup, not a proof of synchronization from generic initial conditions.

Consider N≥2, identical natural frequencies ω, `shuffle_driver=False`, equal current phases, a history in which each stored vector has equal entries, equal complex accumulator entries c (including diagonal), and equal off-diagonal weights b with zero diagonal. For the engine's standard positive-q configuration, this structure is preserved in exact arithmetic. Let θ be the common current phase, h the oldest common history phase, and m=N−1. A single engine step reduces to:

1. `c⁺ = αc + (1−α) exp(i(θ−h−ωτ))`, `r=|c⁺|`.
2. `β = max(0, b + dt((η+μ)r − μ − γb))`; let `s=mβ`.
3. If `a−q s < δ`, let `λ=min(1, capacity/(s+scale_epsilon))` and set `b⁺=βλ`; otherwise `b⁺=β`.
4. `θ⁺ = mod(θ + dt[ω + m b⁺ sin(h−θ)], 2π)`; append θ⁺ and drop the oldest history entry as the engine does.

**Why invariant:** the delayed phase difference is identical at every entry; all EMA entries remain c⁺. The diagonal of reported R is zero and every off-diagonal equals r. Clipping and symmetrisation preserve a uniform off-diagonal β. All row sums and projection factors are equal, so `np.minimum.outer` multiplies by λ, **not λ²**. All phase coupling sums then equal `m b⁺ sin(h−θ)`, and the history remains synchronous. This is an induction argument over the actual engine update order, not a Lean theorem or a general Python–Lean equivalence proof. The scalar non-autonomous delay system may have time-varying increments, so it does not by itself satisfy Cycle 6's constant-w assumption.

## Evidence

`symmetric_reduction_test.py` compares this independent scalar transcription against `advance_state` at every step, including all phases, weights, complex accumulators, both R matrices, queue slots and projection decision. Results (`test.log`):

- synthetic homogeneous N=12, d=50: 300 steps, max absolute discrepancy 2.78e−17; no projection; phase-increment range ≈1.11649e−4;
- N=4 projection exercise: 80/80 steps projected, max discrepancy 2.22e−16;
- N=4 clipping exercise: 40 steps, max discrepancy 1.11e−16;
- changing one frequency breaks phase synchrony by 0.01 in one step.

These are finite float64 checks, not a proof, a broad parameter sweep, or validation under production's heterogeneous frequencies and random initialization. The initial scalar implementation mistakenly used λ²; the projection test failed immediately (weight error ≈0.15013) before correction. The original failure is retained in `projection_negative_control.log`; the final test uses λ. That failure detects this specific transcription error, not a full mutation campaign.

## Reproduce and provenance

```sh
python3 /home/user/AIEFS_cycle7/symmetric_reduction_test.py
```

Requires NumPy and `/home/user/AIEFS/aief_experiment_engine_v1.py`. The tested engine SHA-256 is `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`, matching GitHub main `578868241870e66fe4cb905f3b6d707fd7d39f4f`. Main advanced since Cycle 6: PR #37 added C014 `TrajectoryInvariants.lean` and associated checks; this cycle did not review or run that work. No Lean build, project gate, CI mutation suite, or independent review was performed this cycle. `SHA256SUMS.txt` pins the script and engine.

The GitHub connector is unsupported in this session, so despite the user's permission no push was possible or attempted. The inbox note is a draft for the owner; no claim promotion, frozen-evidence edit, or repository change was made.
