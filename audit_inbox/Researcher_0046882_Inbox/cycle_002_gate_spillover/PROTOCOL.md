Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-21T16:24:58.427532-07:00 MST (host-reported, UNVERIFIED; see CLOCK_NOTE.md)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (instrumented copy)  
Scope: Gate spillover lane, DIRECTION-1  
Status: UNVERIFIED by project seats

# Frozen protocol — cycle 002

Written before any control execution or production simulation in this cycle. Source inspection and hash checks are preparation, not measurements. PROTOCOL.sha256 is emitted before runs. No git commit or external preregistration is claimed.

## Cohort and configuration
Use frozen production manifest `runs/5a9f093a2fe0/manifest.json`, the input authority named by the baseline-equivalence certificate in runs/b57562a8ee77/manifest.json. Full manifest is supplied unchanged. K=4, first four seeds in manifest order (below). This bounded pilot is selected before timing or outcomes, to control runtime and downloadable raw-data size. No extrapolation to all 40 seeds. No extra seeds chosen after inspection.

- 11242426753702356865
- 4619122171158768524
- 16329425431442249417
- 10431384713483787270

Use all ModelConfig fields supplied by the manifest, omega converted to tuple; use the engine's existing default scale_epsilon=1e-12. N=12, dt=.01, tau=.5, T_window=17.502917152858814, T_sim=800, burn=160, split=480, future=320. Keep the full seven-branch RNG namespace in manifest order. Run simulate_prefix and simulate_future for the reference `continue` branch only. No ablations, shuffled drivers, parameter sweep, or claim replication. This answers the production reference trajectory question, not all intervention branches.

## Windows
Global transition indices are zero-based; index k is the update starting at k*dt. Half-open windows: all [0,80000); burn [0,16000); history [16000,48000); future [48000,80000); future immediate [48000,49750); recovery [49750,56750); late [56750,80000). Future subwindows are fixed physical windows, not EMA-normalized windows. Every update is observed, not every diagnostic_stride step. Overlapping summary windows are not independent samples.

## Definitions fixed by direction
Evaluate row events only on pre_violation=True steps, irrespective of projection_active. Record projection_active separately using the unchanged engine threshold 1e-14.
For every step retain row_sum_pre, actual scale (ones convention on ungated steps), r_post=sum(B_projected,axis=1), pre_violation, projection_active.
Binding: scale<1, with d=(capacity-r_post)/capacity. Bystander: scale==1 and row_sum_pre>0, with l=(row_sum_pre-r_post)/row_sum_pre. Zero-load bystanders are counted but excluded from l denominators. Events use strict >1e-9, no change or rounding before classification. Keep negative roundoff values; no clamping. Nonfinite observed measurements invalidate the run rather than being ignored.
Report counts and frequencies over eligible row-steps, and gated-step frequency of at least one event. For d and l give count, minimum, median, p95, max over ALL eligible values, plus event-only statistics. Quantiles: NumPy quantile method='linear'. Empty populations: null statistics and explicit zero denominators. Per-seed, per-window and pooled summaries; pooled row-steps are descriptive, not independent statistical replicates. Supply all raw observations for alternative thresholds.

## Additional diagnostic, predeclared
Separate binding depth into own-scale deficit b=(capacity-scale*row_sum_pre)/capacity and extra neighbor loss e=(scale*row_sum_pre-r_post)/capacity, so d=b+e up to floating-point rounding. Record summary of e and residual d-b-e. This does not replace the assigned d metric. It disambiguates epsilon effects from endpoint competition. No modified gate is simulated.

## Controls and a necessary correction
The requested equal-load control d=0 is false in exact arithmetic for a binding row with epsilon>0: equal load q gives r_post=c*q/(q+epsilon), so d=epsilon/(q+epsilon)>0. Before measurements we declare three complementary controls:
1. Equal-load K4, edge weights 2/5, cap=19/30, epsilon=0: exact d=0 and extra-neighbor-loss=0 (the requested mathematical zero control, explicitly epsilon-zero).
2. Same K4 with epsilon=1/10^12: exact d=epsilon/(6/5+epsilon)>0, below 1e-9; exact extra-neighbor-loss=0. Tests production-regularizer semantics without falsely claiming d=0.
3. Feasible equal-load graph: guard inactive, unchanged weights, no event eligible. Guarded-gate negative control.
Reproduce W1 and W2 independently with fractions, checking source note's exact row sums. Do not execute any deposited adjudication script. W1 exercises bystander loss; W2 binding undershoot. Deliberately wrong row-only scaling must fail the positive-control comparisons. Test strict threshold equality, immediately-above-threshold and nonfinite rejection.

## Instrumentation noninterference: mandatory before remaining seeds
Only an external copy is edited. A six-line observational block after projection_active calls a hook with copied arrays. Original gate arithmetic, state updates, return values, RNG and seed schedule remain unchanged. Supply full original/copy, hashes and unified diff.
Run original and instrumented engines for the first seed's complete prefix+continue future using the same API. Compare every returned array's dtype, shape and raw bytes, scalar float bytes (including matching NaN payloads), complete split state/history, final state/history, RNG state, and SHA256 streams of every post-step state and advance return. No isclose. Observer is enabled for the instrumented comparison run. If any comparison fails, declare INVALID and stop before aggregating or running further seeds. This is instrumentation equivalence, not frozen-artifact certification.

## Execution and stop rules
Controls must pass before production. Record exact commands, Python/NumPy versions, sources and outcomes. On errors, report failure; do not silently skip seeds or shorten windows. If resources prevent completion, report partial/NOT_RUN, not a successful cohort. No confidence intervals, locking claims, freezing claims, or explanation of the AUD-RATELAW residual. Changes after observing results require an explicit amendment; preserve this protocol unchanged.
