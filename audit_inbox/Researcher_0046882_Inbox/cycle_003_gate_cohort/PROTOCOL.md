Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-22T03:01:39.733080-07:00 (host-reported MST; not authenticated)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (copy)  
Scope: Gate spillover lane, DIRECTION-2; full 40-seed reference cohort  
Status: UNVERIFIED by project seats

# Cycle 003 predeclared protocol

Written and hashed before executing controls or full-cohort simulations. No remote preregistration claim. Cycle002 is untouched. Host clock discrepancy remains as disclosed in cycle002; the owner dates acceptance by the upload commit.

## Population and exact schedule
All 40 randomization.paired_seeds from frozen production manifest runs/5a9f093a2fe0/manifest.json, in its supplied order, without exclusions. Manifest hash bf4d8c4152efafac352c8e1e56759ee7867fdd418cb04a8ee1f2fc87c2315a33. Seed list:

1. 11242426753702356865
2. 4619122171158768524
3. 16329425431442249417
4. 10431384713483787270
5. 18127452951968972828
6. 12851640484293199234
7. 4219039243791140697
8. 9082055256280075172
9. 1918007468868772336
10. 17883847597205629106
11. 16627818730624180313
12. 15403081841477312463
13. 4040285944958847150
14. 17521310920850592782
15. 2461295749352584108
16. 9036321132460399255
17. 14040336450255043598
18. 1888415619847841128
19. 172180395821707403
20. 17715532056777442089
21. 3704716633526084363
22. 6942591650975756121
23. 305986450614148690
24. 16952466944611321358
25. 12123519807951751650
26. 15853699719446171583
27. 9189988769602851417
28. 5213047409853278064
29. 4932511216876650745
30. 6108867655028980287
31. 6023008189364820510
32. 1230287949579537403
33. 283404770198602602
34. 3582616062465030267
35. 3258463328937640595
36. 3952397966055989215
37. 17279552413280415429
38. 5415544643585892346
39. 10856823803646276806
40. 14924267685654216746

Rerun all four pilot seeds; do not append them as additional replicates. Report both full40 and pilot4 pools, and all individual seeds. Baseline/copy hashes in HEADER.txt are mandatory. Frozen parameters, epsilon=1e-12, 48,000-step prefix plus 32,000-step continue future, full seven-branch RNG namespace unchanged. Original simulate_prefix / simulate_future API. No other interventions or parameter changes.

## Unchanged windows and measures
Half-open global transition-index windows: all [0,80000); burn [0,16000); history [16000,48000); future [48000,80000); future_immediate [48000,49750); future_recovery [49750,56750); future_late [56750,80000). Global k starts at physical time k*dt; dt=.01. Overlapping windows are not independent samples.

On pre_violation=True steps: binding scale<1; bystander scale==1, eligible for l only when pre>0. d=(capacity-post)/capacity; l=(pre-post)/pre; events strict >1e-9. Preserve tiny signed values. Nonfinite observations invalidate rather than disappear. projection_active is recorded separately using engine threshold1e-14.

Binding decomposition b=(capacity-scale*pre)/capacity and e=(scale*pre-post)/capacity, with d=b+e up to floating-point arithmetic. Report distributions of both, and the decomposition residual. The epsilon convention is not changed.

Per-seed table for EVERY window: gated/total fraction, binding and bystander event/eligible counts, max d and l; plus gated-step any-event frequencies, zero-load exclusions, min/median/p95/max for eligible and event-only distributions. Empty denominators/statistics=null, not zero. Quantile method='linear'. Full40 and pilot4 pools computed from row observations, never averages of seed quantiles. No confidence intervals or significance tests.

## Predeclared future-window descriptors
For EACH of 32,000 future steps and EACH seed, on the actual proposal:
1. binding_count=sum(scale<1) when gated; 0 when ungated (scale=1 observation convention).
2. min_scale=min of all 12 actual scales (1 when ungated).
3. binding_load_spread=max(row_sum_pre[binding])-min(row_sum_pre[binding]); one binding row=>0; no binding rows=>missing (NaN stored only for this explicitly undefined descriptor, not as a measurement failure). Also report spread/capacity.
Save those compact per-step vectors and summarize min, median, p95, max, mean; for binding_count also the frequency table0..12. Descriptors cover all future steps; separately identify any missing-spread steps. A future event seed has at least one d-event OR l-event. Also classify d and l separately. No post-hoc alternative threshold to manufacture separation.

Report the seed lists and counts in those groups. Compare group ranges of each seed's median and maximum descriptors; label strict separation only if max(groupA)<min(groupB) or the reverse. If descriptors overlap, report overlap. These are descriptive associations, UNEXPLAINED as to cause, not predictors, topology explanations, or fitted models. Any further descriptor is explicitly exploratory and cannot replace these.

## Controls and noninterference
Rerun cycle002 exact controls: epsilon-zero equal-load K4 d=0; positive-epsilon equal-load K4 d=epsilon/(q+epsilon)>0 with exactly zero neighbor deficit; feasible equal-load inactive gate; W1 and W2 exact positive witnesses. Also strict-threshold, zero denominator, nonfinite rejection and wrong-per-row-scaling controls. No external deposited scripts executed.

Before remaining39 seeds, compare original and observed first seed full prefix+continue: same101 returned/state/RNG leaves by dtype/shape/bytes plus stream hashes of every post-step state/history and advance return. Observer enabled. Stop INVALID on any mismatch. Compare pilot rerun raw array hashes to cycle002 frozen references, and descriptive summaries separately. A mismatch is an anomaly; stop and investigate, not alter the threshold. Use the same six-line copied-array hook; no main edit.

## Storage and execution plan
Persistent snapshots approximately128MiB/10,000 files, current saved material about47MiB; full raw40 NPZ cohort estimated >200MiB. Therefore use DIRECTION-2's authorized fallback: deposit per-seed/window summaries AND SHA256 of EACH raw array, including shape/dtype/byte-order; keep raw NPZ only in explicitly temporary excluded cache during execution. Do not claim those raw archives will survive a later session. Supply compact future descriptors, which are much smaller. If even those threaten the cap, package hashes instead and document it; do not drop seeds.

At most one trajectory's observations are accumulated in RAM at once. Pool d/l/b/e vectors in temporary disk files and reduce one metric/window at a time. Reproduction requires regeneration of omitted arrays; hashes verify it. Hash raw contiguous C-order bytes, not NPZ container timestamps. No secret credentials or remote access required during execution.

Run all40 in manifest order; no timing-based changes to cohort. Any crash or limit is reported as incomplete with exact completed seeds, never a successful full cohort. All logs end .log.txt. Preserve this protocol and its hash; amendments after observing data must be explicit. End the lane with a single-paragraph descriptive prevalence/magnitude conclusion; no redesign, cumulative-impact study, locking/freezing claim, Lean bridge or rate-residual analysis.
