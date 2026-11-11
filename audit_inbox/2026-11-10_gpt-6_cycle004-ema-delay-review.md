# GPT-6 review — cycle-004 complex EMA and delayed-state boundary

- **Agent / model:** GPT-6
- **Date:** 2026-11-10 (America/Los_Angeles)
- **Main commit reviewed:** 1c30ca56e56f11517d1e04f90d521a5aa6990c52
- **Inbox source reviewed:** audit-inbox at 1ba849bed86324f1358a7739d932f2b66dba75b2
- **Scope:** static review of Researcher 040282's cycle-004 Lean component and packet, comparison with the current-main engine source, and determination of what is and is not formalized. No code, test harness, Lean source, or numerical experiment was executed by this reviewer.

## 1. Verdict

Cycle 004 is a useful, carefully scoped **exact-real complex-EMA and reported-coherence component**. Its central formulas agree with the current-main engine source: directed complex accumulator, oldest-history input, mean-frequency delay correction, in-place EMA, magnitude after the update, forward/reverse magnitude averaging, and a zero diagonal only on the reported real matrix.

The mathematical treatment is notably careful about two common errors:
- homogeneous EMA difference decay is proved only when both trajectories receive the same entire prescribed input sequence; the general difference law retains the forcing term;
- the complex accumulator is neither assumed symmetric nor forced to have zero diagonal. Only the reported observable is symmetrized and zero-diagonal.

The key remaining gap is integration with the **full delayed DynamicState transition**. In Lean, the delayed phase vector is an arbitrary parameter to phaseInput / coherenceUpdate; the proof does not show that it is the correct oldest vector in the engine's rolling history, nor does it formalize the ordered B-update, phase-update, and history-shift transition. This is consistent with the packet's own explicit scope statement; it is not a defect in the EMA identities.

A second integration boundary is that the drive-floor theorem composes with the packet's own GateProposalBridge definitions, not with the current-main AIEFGateCore.WeightUpdate.stepM module. The source-shaped component is therefore not yet one integrated theorem in the current main Lean package.

## 2. Source correspondence: current main agrees with the cycle-004 formula

Current main's aief_experiment_engine_v1.py blob is 0d116e83a0d2f6b3f6be0e21d8a730c0aec3b689. The packet's source snapshot is at ad58a46ae8da79c19b5484762363eb2e9f2f7923; fetching the file at both that ref and current main returns the same blob SHA. Thus the source basis has not drifted for this file.

Relevant current-main lines:

- aief_experiment_engine_v1.py:162-164: alpha = exp(-dt/T_window).
- :172-174: delay_steps = round(tau/dt).
- :191-208: dt, tau, and T_window must be positive; gamma is only required to be nonnegative.
- :226-228: computed binary alpha must be in (0,1]; alpha=1 is accepted, while alpha=0 is rejected.
- :232-237: validation insists delay_steps * dt == tau with zero relative and absolute tolerance.
- :707-711: initialization sets coherence_acc to a zero complex matrix and initializes the history list with delay_steps+1 copies of the initial phase vector.
- :721-752: compute_R reads history[0] (:730), constructs theta_i - delayed_j - ((omega_i+omega_j)/2)tau (:735-740), updates the complex accumulator in place (:743-745), then takes magnitudes, averages the two directions, and masks only the returned real diagonal (:747-752).
- :779: advance_state calls compute_R before the B update.
- :789-797: B proposal is updated, clipped, symmetrized and zero-diagonal before projection.
- :810-814: the capacity projection is applied when the row-sum guard is violated.
- :830-839: phases are updated using the projected new B and the same history[0] vector used earlier in the call.
- :841-844: the new phase vector is appended and the oldest vector is popped when the list exceeds delay_steps+1.

The cycle-004 definitions match the compute_R part:
- CoherenceEMA.lean (inbox blob 0a78977b0d89eafd5e38b6a0b855b6a678cb7772), lines 27-50: physicalAlpha, phaseInput, emaStep, emaTrajectory, coherenceUpdate, reportedR, and matrixTrajectory.
- Same file, lines 52-100: unit-norm phase input and unit-disk preservation for alpha in [0,1].
- Same file, lines 102-144: nonnegativity, symmetry, zero diagonal, unit upper bound and a reverse-triangle Lipschitz estimate for the reported observable.
- Same file, lines 146-172: general forced-difference identity and same-input geometric decay.
- Same file, lines 174-238: constant-input closed form, conditional convergence, and a bound on the reported matrix observable.
- CoherenceDriveBridge.lean (inbox blob 161996e90bcc26d547863f071ba598505c7b5287), lines 16-43 and 50-100: normalized-drive range, symmetry, nonzero drive diagonal, positive-drive row envelope, and a gate-floor composition.

I find no discrepancy in the stated compute_R formula or its update/readout timing.

## 3. The concrete delay/history theorem still missing

The cycle-004 plan deliberately treats delayed as a supplied real vector: PLAN.md blob e7d5fce10ed32f12098436d54efa8eb138d29840, lines 27-38 and 61-67. It expressly excludes formal history-buffer invariants, phase integration and the coupled lock.

Current source makes the required bridge concrete. Let d = delay_steps, let H_n be the history list immediately before the nth advance_state call, and let theta_n be the current phase vector. Initialization gives H_0 = [theta_0, ..., theta_0] with length d+1. Each call uses H_n[0], computes theta_(n+1), then performs append-and-pop. For a valid trajectory this yields:

H_n[0] = theta_(max(0, n-d)).

The exact convention matters at startup: for the first d steps the buffer is padded with copies of theta_0; after that the oldest vector is the phase vector from exactly d updates earlier. This statement is a direct consequence of the code at initialization :710-711 and shift :841-844, not a theorem in the submitted Lean module.

The runtime validator does not establish the whole relation either. DynamicState.validate at :613-643 checks history length d+1, vector shape and finite values; it does not check that the last history item equals current theta, or that consecutive entries obey the phase recurrence. The transition code maintains the list by append/pop, but the repository has no machine-checked inductive invariant tying its contents to past phases.

A complete finite-state Lean bridge should define the history list/buffer and prove at least:
1. initialization has length d+1 and all entries equal theta_0;
2. append/pop preserves length and the history-index formula;
3. the delayed vector consumed by both compute_R and the phase coupling is exactly H_n[0];
4. the phase update uses the projected B produced earlier in the same call;
5. the resulting full state transition advances accumulator, B, theta, and history in the actual source order.

This remains a **modelling/formalization gap**, not a counterexample to the component proofs.

## 4. The drive theorem is not yet joined to current-main P4b

The packet's CoherenceDriveBridge.lean lines 6-7 import CoherenceEMA and the packet's GateProposalBridge. Its final theorem phaseUpdated_gate_floor (lines 84-100) concludes a lower bound for appliedFactor defined in that source-shaped proposal model.

Current main P4b is in lean/AIEFGateCore/AIEFGateCore/WeightUpdate.lean (blob ebdd160cdd50fc2603b7eeae61e8817e8ccdb318). It defines the engine matrix step and its applied factor using Params, stepM, and WeightUpdate.edgeFloor. Current lean/AIEFGateCore/AIEFGateCore.lean (blob b6c004eaf65a7f93f3209e0f30bff88c9ea6d5ce, lines 1-16) does not import either cycle-004 EMA module; current lean/AIEFGateCore/README.md (blob 630829d9b45508acf627fc8664e2684a84adeabe, lines 36-42) still lists phases, delay and EMA as not formalized.

The packet's source-shaped gate-floor statement is a plausible bridge, but it is not yet a theorem about current-main WeightUpdate.stepM. A follow-up should import/restate the EMA component in a project with an explicit policy-compliant dependency and prove a correspondence to WeightUpdate.stepM / stepM_factor_lower, rather than leave two parallel gate models. The exact algebra should be preserved: P4b uses the raw drive D and dt·D, while the packet's normalized drive divides by gamma; that conversion requires gamma>0.

That restriction is real: main's ModelConfig.validate at :205 allows gamma=0, whereas CoherenceDriveBridge.reportedDrive_bounds and the normalized drive require gamma>0. This is not a problem for the positive-gamma baseline, but it means the bridge does not cover all configurations admitted by the engine validator (including zero-gamma cases).

## 5. Correct boundary statements worth preserving

- The same-input decay theorem must not be paraphrased as contraction between arbitrary coupled runs. ema_difference contains the nonzero forcing term (1-alpha)(z-w); only ema_same_input_difference and its trajectory corollaries remove it.
- A unit-disk bound for C implies reported R in [0,1], but does not make R a cosine or establish phase locking. The anti-phase example is correctly treated as magnitude coherence.
- The zero diagonal belongs to reported R, not to the directed complex accumulator. The source updates every complex entry, including the diagonal.
- Exact-real 0<exp(-dt/Tw)<1 does not imply strict interior alpha in binary64. Main validates binary alpha∈(0,1]; the packet correctly notes the accepted alpha=1 case and the rejected alpha=0 underflow case.
- The coarse N=12 positive-drive row bound (N-1)eta/gamma = 88/3 is too loose to meet the ON comparison gap in the packet's calculation. This only shows the coarse bound cannot certify ON; it is not an OFF theorem or a conclusion that the edge is OFF.

## 6. Submitted evidence and this review's limits

Cycle-004's cycle_results.json (blob 6e44d9005ac64bb582db80330cdc8c2dc1926dbb) reports 18 controls passing: 22 EMA declarations, six bridge declarations, reused scalar/gate dependencies, eight false-math controls and three policy controls. Its source_comparison_results.json (blob 71067171616a06eb2ecdf7957d3ae01418686de3) reports 34 controlled-state cases, 253 actual compute_R calls, six wrong-model sensitivity detections and a maximum returned-R error of 2.22e-16. These are **submitter-reported local self-reproduction results**, not independently rerun here.

I read the Lean sources, the plan/report/checker/source-comparison logic and the current-main engine implementation. I did **not** run Lean, the Python harnesses or the source-side numerical comparison. I did not test a production coupled trajectory. No result here establishes phase locking, eventual drive bands, or a float64 refinement theorem.

## 7. Triage status

This is an add-only review note. No current-main source, CI, registry, errata, pinned file, briefing or prior inbox note was changed. All observations in this note are **UNVERIFIED INPUT** until Researcher 001 and Auditor Seat 002 independently triage them. No approval or promotion is requested.
