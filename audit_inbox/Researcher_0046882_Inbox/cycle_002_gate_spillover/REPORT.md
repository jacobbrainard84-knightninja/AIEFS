Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-21T16:24:58.427532-07:00 MST (host-reported, UNVERIFIED; see CLOCK_NOTE.md)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (instrumented copy)  
Scope: Gate spillover lane, DIRECTION-1  
Status: UNVERIFIED by project seats

# Cycle 002 report

## 1. Scope and predeclaration

Four seeds, selected **before measurements** as the first four of the 40-seed frozen manifest, each with the complete 48,000-step prefix and 32,000-step `continue` future: **320,000 measured updates**. A separate original-engine run of seed 1 provides the instrumentation check. Model parameters, full seven-branch RNG namespace and production API remain unchanged; only `continue` is executed after the split.

K=4 was a predeclared bounded pilot for runtime and raw-archive size. It is not an outcome-selected sample, a full-cohort estimate, or a replication of registry claims. The actual runtime turned out modest; I did not enlarge K after seeing outcomes. Protocol SHA256: `80eb74fbcafa36f87fb219bb7f503061cf9d1f8ce9eb4937d488813893c90984`.

## 2. Gate activation and row populations

`pre_violation` and `projection_active` agreed on every measured step. This observation is not an identity assumed by the measurement.

| Window | Gated / measured steps | Fraction |
|---|---:|---:|
| all | 311,064 / 320,000 | 97.207500% |
| burn | 55,064 / 64,000 | 86.037500% |
| history | 128,000 / 128,000 | 100.000000% |
| future | 128,000 / 128,000 | 100.000000% |
| future_immediate | 7,000 / 7,000 | 100.000000% |
| future_recovery | 28,000 / 28,000 | 100.000000% |
| future_late | 93,000 / 93,000 | 100.000000% |

The earlier report of 100% activation is compatible with these history/future windows, but not with the full trajectory including burn-in in this pilot. No claim about that earlier unverified note is re-adjudicated here.

Across gated steps, binding rows per step: min 1, median 11, p95 12, max 12. Bystander rows per step: min 0, median 1, p95 3, max 11. Zero-load bystander row-steps excluded from fractional-loss division: **236,383**. They remain present in the raw data and row counts.

## 3. Primary event frequencies

Thresholds are the predeclared strict `> 1e-9`, applied only on gated steps. Binding means `scale < 1`; it is not replaced by `row_sum_pre > capacity`. Bystander loss excludes zero-load rows.

| Effect | Events / eligible row-steps | Row-step frequency | Gated steps with ≥1 event | Gated-step frequency |
|---|---:|---:|---:|---:|
| Binding depth d | 684,126 / 3,324,857 | 20.576103% | 185,656 / 311,064 | 59.684181% |
| Positive-load bystander loss l | 140,568 / 171,528 | 81.950469% | 79,530 / 311,064 | 25.567086% |

These denominators answer different questions. Neither row-steps nor repeated steps are independent experimental replicates; no confidence intervals or population-level inference are supplied.

## 4. Magnitudes — dimensionless fractions, not percentages

Values below are over **all eligible row-steps**, including non-events. Raw observations allow the threshold to be changed without a rerun.

| Metric | Median | p95 | Maximum |
|---|---:|---:|---:|
| spillover | 1.5782112459e-12 | 1.37974739839e-05 | 0.002989876971 |
| bystander_loss | 0.000815372856256 | 0.00290300652328 | 0.00299090389062 |

For scale: maximum binding depth is **0.298988% of capacity**; maximum bystander loss is **0.299090% of that row’s pre-gate weight**. These percentages have different denominators.

Event-only distributions:

| Metric | Median | p95 | Maximum |
|---|---:|---:|---:|
| spillover | 7.12826838083e-07 | 0.00028723171428 | 0.002989876971 |
| bystander_loss | 0.00103661152042 | 0.0029272326233 | 0.00299090389062 |

## 5. Future-window concentration: do not conceal it in a pooled average

All four seeds have gate activation on every future update. However, all above-threshold future events occur in seed **4619122171158768524**.

| Seed | Future binding events / eligible | Future bystander events / eligible |
|---|---:|---:|
| 11242426753702356865 | 0 / 352,000 | 0 / 0 |
| 4619122171158768524 | 33,837 / 372,619 | 11,381 / 11,381 |
| 16329425431442249417 | 0 / 352,000 | 0 / 0 |
| 10431384713483787270 | 0 / 352,000 | 0 / 0 |

Zero eligible bystanders means the fractional-loss rate is **undefined**, not 0%. The three seeds with no eligible future bystander rows have one zero-load bystander on each future step. In the event-bearing seed, at least one binding event occurs on each of its 32,000 future steps. Pooled future binding-event frequency is 2.368511% of eligible row-steps; bystander loss is 100% of its 11,381 eligible row-steps, but those occur on only 8.891406% of all pooled future steps.

**UNEXPLAINED:** why this future-window behavior concentrates in this one seed. This cycle does not make a topology, locking, memory, stability, or cumulative causal-impact claim. First four manifest seeds cannot settle full-cohort prevalence.

## 6. Necessary correction to the requested negative control

Equal row sums imply equal scales, so there is no *extra neighbor-induced* reduction. But for a binding common row load q and positive epsilon, exact arithmetic gives:

`r_post = c*q/(q+epsilon)` and `d = epsilon/(q+epsilon) > 0`.

Consequently, the requested “equal row sums ⇒ d=0 exactly” is false at the production positive epsilon. This was identified and recorded in PROTOCOL.md **before** execution, not used to reclassify outcomes.

Controls actually run:

- Equal-load K4, edge weights 2/5, cap 19/30, epsilon=0: d=0 exactly on all rows.
- Same graph, epsilon=1/10^12: d=1/1200000000001 exactly (positive, below 1e-9); extra-neighbor deficit is zero exactly.
- Feasible equal-load graph: guard off, unchanged rows, no eligible event.
- W1 reproduced with independent Fraction arithmetic: post rows 19/30, 47/90, 14/45; bystander losses 7/54 and 1/9.
- W2 reproduced: post rows 19/30, 209/420, 209/420; binding depths 0, 57/266, 57/266.
- Wrong per-row-only scaling is rejected against both W1 and W2.
- Strict threshold equality, next representable value above threshold, zero denominator and NaN/±infinity rejection controls passed.

The epsilon-zero W1/W2 witnesses reproduce the adjudication’s exact setting; they are not advertised as exact representations of float64 production.

For measured binding rows, the predeclared decomposition is `d = b + e`, where `b=(c-scale*q)/c` and `e=(scale*q-r_post)/c`. Own-scale deficit b ranged about 1.57418e-12–1.57891e-12. Extra-neighbor loss e had p95 1.37974724e-5 and max 0.002989876969. Small negative e values (minimum -5.25895e-16) were retained rather than clamped; interpretation beyond their arithmetic scale is not needed for event counts. Maximum decomposition residual was 4.33681e-19. This supports keeping the assigned metric and threshold while separating the regularizer from endpoint competition.

## 7. Instrumentation and independent validation

- Original repository engine hash remained `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`; git working tree remained clean.
- Instrumented copy hash: `a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830`. It lives outside the repository.
- Six added lines call an observer with copied arrays. No gate, state, RNG or return expression was changed.
- First seed: all **101** saved returned-output/state/RNG leaves matched original bytes, shapes and dtypes, including matching NaN representations where returned diagnostics contain them.
- SHA256 of the stream of **every post-step full state/history and advance return** matched across all 80,000 updates: `c6ec8b7edd19415445e0fb49269140a90a690022312bb0b5a496573b0cf7e04f`.
- Both compared output sets are deposited; the full state stream itself is represented by its digest rather than a second enormous trajectory archive.
- A separate scalar-loop crosscheck, not importing the measurement script, reproduced pooled counts, extrema and quantiles from raw row data; it also recomputed every gated endpoint scale with zero mismatches. Quantile interpolation is allowed only a 2e-15 relative last-rounding tolerance in this secondary check; event counts and instrumentation comparisons use no tolerance.
- The independent saved-output byte comparator rejected a one-bit corruption in final B.

These checks establish noninterference and measurement consistency in this environment, not certification against frozen NPZ artifacts or equivalence across hosts. RAN_READ.md lists exact commands and omissions.

## 8. Conclusion (one paragraph)

**Frequent and small per step in this predeclared four-seed reference pilot:** the gate fired on 97.2075% of all updates; binding-depth events occurred on 59.6842% of gated steps and positive-load bystander events on 25.5671%, with observed maxima below 0.30% in their respective normalization units. Those pooled figures hide a strong window/seed dependence: after the split, all above-threshold events were confined to one of the four seeds despite 100% gate activation in all four. The existence and measured size of these effects are documented here; their full-cohort prevalence, the cause of the one-seed concentration, and any cumulative or topology-selection impact remain **UNEXPLAINED**. This cycle changes no gate, threshold, rate-law claim, or freezing claim.
