Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-22T03:01:39.733080-07:00 (host-reported MST; not authenticated)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (copy)  
Scope: Gate spillover lane, DIRECTION-2; full 40-seed reference cohort  
Status: UNVERIFIED by project seats

# Cycle 003 — Full-cohort gate spillover

## Main answer

**Future-window events are rare across seeds and concentrated: exactly 1 of the 40 manifest seeds (2.5%) has any above-threshold binding-depth or bystander-loss event.** It is the same pilot seed, `4619122171158768524`. The other 39 have zero events under the unchanged strict `>1e-9` rule. This is a statement about the fixed production cohort, not an estimate for arbitrary random seeds.

Both effects occur during burn-in in all 40 seeds. Thus “rare” describes future-seed prevalence, not the existence of gate side effects throughout the full trajectory. No causal explanation is supplied.

## 1. Protocol, data and completion

- All 40 seeds in frozen-manifest order; each has48000 prefix updates and32000 reference `continue` updates: **3,200,000 measured updates**.
- The four pilot seeds were rerun and remain members of the 40, not extra samples. Their six raw arrays per seed match Cycle002 byte hashes, and their seven-window summaries and pooled pilot summary match exactly.
- Premeasurement protocol SHA256: `8cb6faa6ecc9f980574226f0e35cef6cb0c85c045e6905fa419dc40f00948bdb`.
- Frozen model, full branch RNG namespace, windows, epsilon convention and thresholds unchanged. No ablations or step-size sweep.
- Foreground logging failed after the first 26 seeds had durable checkpoints. Recovery validated cached arrays, reran first-seed noninterference, completed the remaining 14, and rebuilt pools. EXECUTION_INCIDENT.md preserves the failure and provenance. No partial run is being substituted for the 40-seed table.
- Full40 raw NPZs exceed the persistence budget and are not delivered. The authorized fallback is used: all per-seed/window summaries plus240 raw-array hashes with dtype/shape. Compact future descriptors are delivered for every step of every seed. RESOURCE_LIMITS.md explains regeneration and cache limits.

## 2. Activation and seed prevalence

| Window | Gated steps / total | Gated fraction | Seeds with d event | Seeds with l event |
|---|---:|---:|---:|---:|
| all | 3,111,069 / 3,200,000 | 97.220906% | 40/40 | 40/40 |
| burn | 551,069 / 640,000 | 86.104531% | 40/40 | 40/40 |
| history | 1,280,000 / 1,280,000 | 100.000000% | 40/40 | 4/40 |
| future | 1,280,000 / 1,280,000 | 100.000000% | 1/40 | 1/40 |
| future_immediate | 70,000 / 70,000 | 100.000000% | 1/40 | 1/40 |
| future_recovery | 280,000 / 280,000 | 100.000000% | 1/40 | 1/40 |
| future_late | 930,000 / 930,000 | 100.000000% | 1/40 | 1/40 |

pre_violation and projection_active counts agree in these runs. The gate is active on100% of history/future steps, but not100% of burn-in. Seed prevalence, eligible-row event frequency and gated-step event frequency are different denominators. Repeated rows/steps are not independent replicates.

## 3. Full-cohort effects: entire trajectory

| Metric | Event rows / eligible rows | Row frequency | Gated steps with event | Gated-step frequency |
|---|---:|---:|---:|---:|
| spillover | 6,569,600 / 33,943,754 | 19.354371% | 1,498,936 | 48.180738% |
| bystander_loss | 1,018,380 / 1,353,582 | 75.235930% | 487,871 | 15.681780% |

Raw magnitudes are dimensionless fractions (not percentages):

| Effect / population | Median | p95 | Maximum |
|---|---:|---:|---:|
| spillover / all_eligible | 1.5782112459e-12 | 1.23885885947e-05 | 0.00299398505846 |
| spillover / event_only | 5.60800445906e-07 | 0.000326390033347 | 0.00299398505846 |
| bystander_loss / all_eligible | 0.00095202987462 | 0.00293006936997 | 0.00299400255156 |
| bystander_loss / event_only | 0.00110471548537 | 0.0029501337934 | 0.00299400255156 |

The all-trajectory maximum binding depth is **0.299399% of capacity**, and maximum bystander loss is **0.299400% of its pre-gate row weight**. The denominators differ. There were 2,035,492 zero-load bystander row-steps excluded from l division; they are not falsely counted as eligible no-loss observations.

## 4. Future window: same exceptional seed, not a growing event group

Full future: 1,280,000 updates, all gated. Binding events: **33,837 / 14,484,619 eligible binding row-steps = 0.233606%**. Those events occur on32,000 gated steps (2.5% of pooled future steps), all belonging to the exceptional seed. Positive-load bystander events: **11,381 / 11,381 eligible row-steps**; these occupy0.889141% of pooled future steps and also all belong to that seed. Zero-load bystanders excluded:864,000.

Within seed4619122171158768524, at least one binding event occurs on every one of its 32,000 future steps. Its binding denominator is372619 row-steps; the other 39 have no above-threshold event. For seeds with no positive-load bystanders, the l frequency/max is undefined, not zero.

Future maxima: d=0.0011110282021250353 (**0.111103% of capacity**); l=0.001111145181421048 (**0.111115% of pre-gate row weight**). These are the same future maxima observed in the pilot.

## 5. Predeclared descriptors: observed ranges overlap

All 32,000 per-step future vectors are delivered for every seed: binding-count, min-scale and binding-load spread. The table below compares each seed’s median or maximum, exactly as predeclared. Event group n=1; no-event group n=39.

| Descriptor / per-seed statistic | Event seed | No-event seed range | Strict separation? |
|---|---:|---:|---|
| binding_count/median | 12 | [11, 12] | overlap_or_touch |
| binding_count/max | 12 | [11, 12] | overlap_or_touch |
| min_scale/median | 0.9976293177 | [0.997001125562, 0.9976293177] | overlap_or_touch |
| min_scale/max | 0.9976293177 | [0.997001125562, 0.9976293177] | overlap_or_touch |
| binding_load_spread/median | 0.000804949122139 | [0.000400000000004, 0.0016] | overlap_or_touch |
| binding_load_spread/max | 0.00150492554992 | [0.000400000000005, 0.00160000000001] | overlap_or_touch |
| binding_load_spread_over_capacity/median | 0.00127097229811 | [0.000631578947375, 0.00252631578948] | overlap_or_touch |
| binding_load_spread_over_capacity/max | 0.00237619823672 | [0.000631578947376, 0.00252631578949] | overlap_or_touch |

**None of these predeclared median/maximum range comparisons strictly separates the event seed from the other 39.** Binding-count=12 and relatively high min-scale are not unique to the event seed. A nonzero range of binding loads is also present among no-event seeds. These summaries do not explain the concentration. This does not establish that the complete time-series descriptors contain no information; it only reports the specified comparisons without adding a post-hoc classifier.

**UNEXPLAINED:** why this one seed carries the above-threshold future behavior. No topology, locking, memory, cumulative-impact, or rate-law-residual inference is made.

## 6. Retain the epsilon/neighbor split

For binding rows, b=(capacity-scale*pre)/capacity and e=(scale*pre-post)/capacity, so d=b+e up to rounding. All-trajectory distributions:

| Component | Minimum | Median | p95 | Maximum |
|---|---:|---:|---:|---:|
| own_scale_deficit_binding | 1.57417938334e-12 | 1.57523117357e-12 | 1.5782112459e-12 | 1.57891243939e-12 |
| extra_neighbor_loss_binding | -5.25895116928e-16 | 1.75298372309e-16 | 1.23885870196e-05 | 0.00299398505689 |

The own-scale deficit remains approximately 1.57e-12. Tiny negative neighbor residuals are preserved rather than clipped. Maximum absolute d-b-e residual is4.33681e-19. Per-window/per-seed b/e statistics remain in the JSON and selected columns in the CSV.

## 7. Checks, controls and evidence boundary

- Exact controls rerun: epsilon-zero equal-load K4 d=0; production-epsilon K4 d=1/1200000000001 with e=0; feasible inactive gate; W1 and W2 exact Fraction positives. Wrong row-only scaling is rejected. Strict-threshold, zero-denominator and NaN/infinity controls pass.
- First seed:101 returned/state/RNG leaves match byte-for-byte, and80,000-step full state/return stream digest matches original engine. A one-bit corrupted B fails the same exact comparator.
- Supplemental code/validate_saved.py imports neither common.py nor the cohort driver: it checked all 280 window tables from raw observations, all 240 raw array hashes, all 1,280,000 descriptor steps and pooled count/extrema sums. It is a consistency check, not an independent simulation. Full-cohort pooled quantiles were not independently regenerated by this second checker; the externally reproducible hashes and supplied code support the seats’ independent check.
- Pilot4 summaries, pooled quantiles and raw arrays match Cycle002; full40 includes them once. evidence/pilot_check.json and completion.json record this.
- No raw outcomes from the remaining 36 were selected out. No model, threshold, window or descriptor amendment was made after observing results.

## 8. Complete per-seed future table

All seven windows for all 40 seeds are in evidence/per_seed_windows.csv (280 rows). A companion evidence/future_seed_table.csv supplies all future descriptors. Seed identifiers should be read as strings or exact uint64, never rounded spreadsheet floats.

| # | Seed | Binding events / eligible | Bystander events / eligible | Max d | Max l |
|---:|---|---:|---:|---:|---:|
| 1 | 11242426753702356865 | 0 / 352,000 | 0 / 0 | 2.91240715755e-12 | undefined |
| 2 | 4619122171158768524 | 33,837 / 372,619 | 11,381 / 11,381 | 0.00111102820213 | 0.00111114518142 |
| 3 | 16329425431442249417 | 0 / 352,000 | 0 / 0 | 1.12462670755e-11 | undefined |
| 4 | 10431384713483787270 | 0 / 352,000 | 0 / 0 | 6.46938643007e-12 | undefined |
| 5 | 18127452951968972828 | 0 / 352,000 | 0 / 0 | 4.64260209224e-12 | undefined |
| 6 | 12851640484293199234 | 0 / 352,000 | 0 / 0 | 4.92588426189e-12 | undefined |
| 7 | 4219039243791140697 | 0 / 352,000 | 0 / 0 | 1.40496386455e-11 | undefined |
| 8 | 9082055256280075172 | 0 / 384,000 | 0 / 0 | 5.0049438278e-12 | undefined |
| 9 | 1918007468868772336 | 0 / 384,000 | 0 / 0 | 2.55851480353e-11 | undefined |
| 10 | 17883847597205629106 | 0 / 384,000 | 0 / 0 | 9.63502961626e-11 | undefined |
| 11 | 16627818730624180313 | 0 / 352,000 | 0 / 0 | 3.44250943541e-12 | undefined |
| 12 | 15403081841477312463 | 0 / 352,000 | 0 / 0 | 8.4348317804e-12 | undefined |
| 13 | 4040285944958847150 | 0 / 352,000 | 0 / 0 | 5.30593113306e-12 | undefined |
| 14 | 17521310920850592782 | 0 / 384,000 | 0 / 0 | 7.03647666449e-12 | undefined |
| 15 | 2461295749352584108 | 0 / 352,000 | 0 / 0 | 3.02582520443e-12 | undefined |
| 16 | 9036321132460399255 | 0 / 352,000 | 0 / 0 | 5.09013883674e-12 | undefined |
| 17 | 14040336450255043598 | 0 / 384,000 | 0 / 0 | 2.04678379508e-12 | undefined |
| 18 | 1888415619847841128 | 0 / 352,000 | 0 / 0 | 6.3976893958e-12 | undefined |
| 19 | 172180395821707403 | 0 / 352,000 | 0 / 0 | 8.71390678912e-12 | undefined |
| 20 | 17715532056777442089 | 0 / 352,000 | 0 / 0 | 5.95243153013e-12 | undefined |
| 21 | 3704716633526084363 | 0 / 352,000 | 0 / 0 | 2.40965142576e-12 | undefined |
| 22 | 6942591650975756121 | 0 / 384,000 | 0 / 0 | 6.09565030031e-12 | undefined |
| 23 | 305986450614148690 | 0 / 384,000 | 0 / 0 | 6.02184968557e-12 | undefined |
| 24 | 16952466944611321358 | 0 / 352,000 | 0 / 0 | 5.73348386312e-12 | undefined |
| 25 | 12123519807951751650 | 0 / 352,000 | 0 / 0 | 8.51687141864e-12 | undefined |
| 26 | 15853699719446171583 | 0 / 384,000 | 0 / 0 | 4.63594075409e-12 | undefined |
| 27 | 9189988769602851417 | 0 / 352,000 | 0 / 0 | 1.25047340903e-11 | undefined |
| 28 | 5213047409853278064 | 0 / 352,000 | 0 / 0 | 2.42279880369e-12 | undefined |
| 29 | 4932511216876650745 | 0 / 352,000 | 0 / 0 | 2.26134900279e-12 | undefined |
| 30 | 6108867655028980287 | 0 / 384,000 | 0 / 0 | 9.04136414859e-12 | undefined |
| 31 | 6023008189364820510 | 0 / 352,000 | 0 / 0 | 1.07696308012e-11 | undefined |
| 32 | 1230287949579537403 | 0 / 352,000 | 0 / 0 | 1.23373241448e-10 | undefined |
| 33 | 283404770198602602 | 0 / 352,000 | 0 / 0 | 3.06510956966e-11 | undefined |
| 34 | 3582616062465030267 | 0 / 352,000 | 0 / 0 | 8.10053778441e-12 | undefined |
| 35 | 3258463328937640595 | 0 / 384,000 | 0 / 0 | 6.40364954046e-12 | undefined |
| 36 | 3952397966055989215 | 0 / 384,000 | 0 / 0 | 8.16189221472e-12 | undefined |
| 37 | 17279552413280415429 | 0 / 352,000 | 0 / 0 | 3.88601431735e-12 | undefined |
| 38 | 5415544643585892346 | 0 / 352,000 | 0 / 0 | 7.76974975586e-12 | undefined |
| 39 | 10856823803646276806 | 0 / 384,000 | 0 / 0 | 8.63712610205e-12 | undefined |
| 40 | 14924267685654216746 | 0 / 352,000 | 0 / 0 | 3.36783232881e-12 | undefined |

## Pilot cross-check: pooled side by side

The pilot is the first four members of full40, not a separate sample added to it. All pilot raw array hashes, per-window summaries and pooled quantiles match Cycle002 exactly.

| Group / window | Gated / total | Binding events / eligible | Bystander events / eligible |
|---|---:|---:|---:|
| pilot4 / all | 311,064 / 320,000 | 684,126 / 3,324,857 | 140,568 / 171,528 |
| pilot4 / future | 128,000 / 128,000 | 33,837 / 1,428,619 | 11,381 / 11,381 |
| full40 / all | 3,111,069 / 3,200,000 | 6,569,600 / 33,943,754 | 1,018,380 / 1,353,582 |
| full40 / future | 1,280,000 / 1,280,000 | 33,837 / 14,484,619 | 11,381 / 11,381 |

## 9. Conclusion — one paragraph

**Rare and seed-specific in the production future window: exactly 1/40 seeds has either above-threshold effect, and it is the original pilot seed; all 40 show both effects during burn-in.** Across 3.2 million updates the gate fires 97.220906% of the time, and observed per-step maxima stay below 0.30% in their respective normalization units; future maxima stay below 0.112%. The predeclared descriptor median/maximum ranges overlap between event and no-event seeds, so they do not furnish a simple descriptive separation in this cohort. The concentration’s cause and any cumulative consequences remain **UNEXPLAINED**. The assigned prevalence/magnitude measurement is complete and ready for independent review; only the project seats can mark the lane DONE.
