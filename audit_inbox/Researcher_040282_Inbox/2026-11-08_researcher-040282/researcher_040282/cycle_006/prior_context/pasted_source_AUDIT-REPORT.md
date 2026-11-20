# AIEF sensitivity reanalysis — audit of the pasted source

## Verdict

**There is a reproducible recovery-event calculation bug. Fix it before finalizing recovery outputs.** The bootstrap also needs explicit boundary/small-sample handling if its intervals are to support population-level inference. The recovery-time terminology needs tightening, and the artifact-integrity checks have identifiable gaps.

This is not a finding that the actual S01 results are wrong: **the raw run and the imported `aief_modular` implementation were not supplied.** Actual incidence and effect sizes remain unmeasured.

The core paired-contrast arithmetic and shared-seed bootstrap layout passed the controls below. A full synthetic run completed with all expected table cardinalities.

### Evidence boundary

- Audited only the pasted program, saved unchanged as `analysis_under_audit.py`.
- No comparison with other analysis implementations, no engine changes, and no regeneration of actual trajectories.
- Executed the pasted function bodies unchanged. The unavailable `aief_modular` imports were replaced by clearly identified audit-only I/O/error helpers in `audit_support.py`.
- Synthetic fixtures exercise the program's design/schema checks; **they are not engine-generated trajectories, real equivalence certificates, or observations of S01.**
- Environment: Python 3.13.16, NumPy 2.3.5, pandas 2.2.3, pytest 9.0.3.
- Test results: **23 controls/characterizations passed; 6 regression checks were expected failures.** The latter cover five distinct issues because two independently expose the hold bug. They were also rerun with `--runxfail`; each failed for its intended reason, not an unrelated setup exception.

## Findings at a glance

| ID | Priority / category | Finding | Evidence |
|---|---|---|---|
| F1 | High — calculation | Exact-duration true runs can be rejected or a later run selected | Deterministic sweep on the program's declared time grid |
| F2 | High if inferential — method limitation | Event-rate intervals collapse at 0/40 and 40/40; a one-case conditional mean also gets a zero-width interval | Direct function tests and a coverage counterexample |
| F3 | Important — estimand/labeling | Saved-grid detection times are not generally interval-censored first physical crossing times; held-onset observability ends before the last sample | Source inspection and observationally indistinguishable constructed paths |
| F4 | Medium — provenance | Inputs can change after validation; outputs can then describe changed data while recording the earlier input identity | Explicit file-mutation fault injection through the full pipeline |
| F5 | Medium — read-back verification | The staged manifest's serialized identity payload is not checked against its own stored digest | Explicit serialization fault injection |
| F6 | Medium for supported parameter variation — validation | Exact nominal-window equality can reject an ordinary CSV round-trip | Reproduced with `T_star = 17.333` |

Priorities describe what to address, not measured damage to the unavailable raw run. F3 is not a claim that a deliberately defined finite-grid score is numerically invalid.

---

## F1. `_held_index` has an exact-boundary floating-point bug

**Location:** `analysis_under_audit.py:541–558`, especially line 555.

```python
required_end = np.searchsorted(times, times[index] + duration, side="left")
```

The addition can land slightly beyond the saved endpoint that should satisfy the duration. `searchsorted` then requires another observation.

### Minimal witness

```python
times = EXPECTED_SAMPLE_TIMES
condition = np.zeros(len(times), dtype=bool)
condition[32:68] = True

# The declared physical grid has a true block from 16.01 to 33.51.
# Its span is 17.5 units.
_held_index(times, condition, 17.5)  # returns None; intended result is 32
```

The relevant floating-point values are:

```text
times[32]                  16.01
times[67]                  33.51
times[32] + 17.5            33.510000000000005
```

A second witness does not even need an exact-grid interpretation: `times[102] - times[32] == 35.0` is literally true, but a true run over those indices is rejected for a 35.0-unit hold. Thus addition/search and the advertised subtraction criterion can disagree.

### Exhaustive translation sweep

For each duration below, put a single true block of the shortest sufficient saved-grid span at **every** possible starting index. All other samples are false.

| Requested duration | Block span | Starting positions tested | False negatives |
|---:|---:|---:|---:|
| 8.75 | 9.0 | 622 | 0 |
| 13.125 | 13.5 | 613 | 0 |
| 17.5 | 17.5 | 605 | **32** |
| 26.25 | 26.5 | 587 | 0 |
| 35.0 | 35.0 | 570 | **26** |

These are test durations, not an assertion about the missing run's `T_star`.

Adding a second, longer true block at indices 100–150 makes the 17.5-unit example return **50.01 instead of 16.01**. The failure can therefore delay an observed event, not merely change observed to unobserved. It propagates to restricted times, event indicators, and their interactions.

**Repair direction:** exploit the already validated uniform grid: calculate a true run's span from its integer index/tick difference, then compare that span with the requested duration. For this exact grid, `(run_end[index] - index) * 0.5` avoids translation-dependent timestamp rounding. Alternatively, use a documented, tightly calibrated floating-point tolerance with timestamp differences.

**Do not simply switch to an untoleranced `times[j] - times[i] >= duration`:** the first witness subtracts to `17.499999999999996`, so that alone does not solve the nominal-grid boundary problem.

**Unknown:** how many actual trajectories contain affected boundary-length runs, and whether any actual recovery estimates change.

## F2. Percentile bootstrap intervals need boundary and insufficient-data policies

**Locations:** `pointwise_summary`, lines 977–1020; zero-variance treatment in `simultaneous_complete_summary`, lines 1044–1064.

The code correctly computes empirical bootstrap percentiles. The problem is interpreting those percentiles as generally reliable 95% population uncertainty intervals in degenerate samples.

### Recovery rates at the boundary

Direct tests give:

| Events / seeds | Reported pointwise interval |
|---:|---:|
| 0 / 40 | **[0, 0]** |
| 40 / 40 | **[1, 1]** |

For comparison, under an independent identically distributed seed/binomial model, the two-sided exact 95% interval for 0/40 is approximately **[0, 0.0881]**.

This is a substantive coverage issue, not just aesthetics. In a *hypothetical* population with event probability 0.01, all 40 observed indicators are zero with probability `0.99**40 ≈ 0.669`. The reported `[0,0]` interval excludes 0.01 on every such sample. Its overall coverage in that example cannot exceed about 33.1%.

That is a mathematical counterexample to general coverage, **not evidence that S01 has that population probability**.

### Very small complete-case groups

With one finite value equal to 7 and 39 missing values, the function reports:

```text
n = 1
std = NaN
pointwise interval = [7, 7]
```

In the tested 2,000-draw plan, **723 draws contained no complete case** and were discarded. No valid-bootstrap-count field reports that loss. Dropping undefined resamples can be a practical conditional-bootstrap convention, but it does not make one observation sufficient for a meaningful population-mean interval.

### Repair direction

- Use a boundary-aware method for pointwise Bernoulli recovery rates, with its assumptions stated.
- Do **not** apply independent-binomial methods to the four-cell paired DID as though its cells were independent. Choose an appropriate paired-contrast method or flag unsupported/degenerate inference.
- Record `bootstrap_valid_replicates`, `bootstrap_empty_replicates`, and a status such as `insufficient_n` or `empirical_zero_variance`.
- Suppress a confidence-interval claim for `n < 2`; determine a more defensible practical threshold for small conditional groups.
- Distinguish structural zeros, such as continue-versus-itself AUC, from merely observing identical outcomes across 40 sampled seeds.

Increasing the number of bootstrap iterations does **not** fix these boundary/data-support issues. Whether they affect the actual output groups requires the raw run.

## F3. Separate saved-grid outcomes from physical event-time censoring

**Locations:** `analysis_contract:156–181`; `_event_row:576–614`; event summaries at 1073–1151.

### What the program actually estimates

`event_time` is a qualifying **saved sample's timestamp**. Summaries bootstrap those timestamps or their capped versions. `event_interval_lower` and `event_interval_upper` are not used by an interval-censored inference procedure.

That is coherent if the estimand is explicitly the saved-grid detection/run-start score. It is not, without more assumptions, an estimate of the same functional of the underlying step-level physical event times.

### Adjacent samples need not bracket the first physical crossing

Consider saved times and values:

```text
times:  0.01   0.51   1.01
values: 0      0      1
```

Two underlying step-level paths can agree at every saved time:

- Path A first crosses at 0.76.
- Path B crosses at 0.11, falls back below threshold before 0.51, and crosses again at 0.76.

The program reports the adjacent interval `(0.51, 1.01]` for both. That interval excludes Path B's first physical crossing. Without a no-hidden-excursions/path restriction, it is not an identified interval for the *first* physical event.

The saved-grid detection time, by contrast, is exactly known: 1.01.

**Recommended labeling:** use `saved_grid_detection` / `saved_grid_qualifying_run_start`. Treat the neighboring timestamps as sampling metadata, not automatically as valid first-physical-event censoring bounds. If physical interval-censored inference is intended, specify the additional model/assumptions and use the bounds in an appropriate analysis.

This does not require pretending that unsaved observations exist or changing the raw trajectories.

### Held onset has a shorter fully observable horizon

For a 17.5-unit hold ending within support at 319.51, the last saved onset with enough future observations is **302.01**. A true run starting at **310.01** is not confirmable within support.

The program gives that case:

```text
event_observed = False
restricted_time = 319.51
```

This is acceptable as a declared **finite-grid capped score**: “no fully observed qualifying run gets the cap.” It is not ordinary physical-onset right censoring at 319.51. A hold can begin before 319.51 and only become confirmable afterward.

Choose explicitly among:

1. Keep the finite-grid score and describe its tail-observability penalty.
2. Report onset and confirmation time separately, using confirmation-time follow-up where appropriate.
3. Restrict onset comparisons to a declared eligible-onset horizon, potentially a common horizon across different hold durations.

Do not silently change the cap without first choosing the estimand. The one-current-window definition changes both the required hold and the eligible-onset horizon across regimes.

## F4. Provenance is not bound to the bytes actually consumed after validation

**Locations:** initial checking in `validate_run:244–370`; separate later NPZ reads at 487–509 and 631–806; publication at 1211–1354.

`validate_run` records input identities, then topology and recovery reopen the NPZ later. There is no use-time or final input-identity recheck.

### Explicit fault-injection witness

After successful validation, the test changes a topology matrix in the NPZ, without updating the simulation manifest. The full pipeline then:

1. Reads the changed matrix.
2. Produces the changed topology result; checked against an independent calculation.
3. Publishes a completed bundle.
4. Records the **earlier** NPZ identity in its provenance.

This demonstrates a race/integrity boundary. **It does not show that anyone changed the actual run.** If an external read-only snapshot genuinely guarantees input immutability throughout execution, that external guarantee can resolve the threat; a `freezeable` flag alone does not enforce it.

**Repair direction:** parse a verified snapshot or hash and parse the same captured bytes. Share that snapshot across topology and recovery. A final recheck is a useful cooperative-process guard, but is not a complete defense against changes during reading followed by restoration.

## F5. The staged manifest's payload is not verified against its serialized digest

**Location:** lines 1324–1329.

The read-back check compares:

```python
observed_manifest.get("analysis_identity_sha256")
# against a digest of the original in-memory identity_payload
```

It does not recompute the identity from:

```python
observed_manifest["analysis_identity_payload"]
```

An audit writer that changes the serialized payload while retaining the original digest passes the check and gets promoted. The resulting manifest fails its own payload/digest relationship.

This is a **verification-gap fault injection**, not an accusation that the unavailable JSON helper corrupts ordinary writes.

**Repair:** verify the loaded payload against its loaded digest **and** against the expected payload. Validate the other authoritative loaded manifest fields against their expected values too.

Related limitation: CSV read-back deliberately checks headers/cardinality, not values or types. That is a useful structural check, not end-to-end semantic equality of the authoritative tables.

## F6. Exact nominal-window equality is fragile across CSV parsing

**Location:** lines 334–337; scalar loading at 223–230.

With `T_star = 17.333`, an ordinary pandas `to_csv` / default `read_csv` round-trip produces:

```text
rho 0.75: expected 12.999749999999999; parsed 12.99975
rho 1.5:  expected 25.999499999999998; parsed 25.9995
```

The source rejects the first difference as an inconsistent nominal window even when the source values were constructed directly as `rho * T_star`.

**Repair:** use a documented tolerance appropriate for nominal-value validation, or a canonical decimal/tick representation. Round-trip parsing can help where bitwise float preservation is actually the intended contract. Keep a clear distinction between numeric equivalence and detecting a genuinely different window.

This is a parameter-dependent validation defect. It may be irrelevant to a particular fixed run whose window values are exactly representable; the actual manifest was not provided.

---

## Additional policy and operational decisions

### Degenerate recovery references

Zero imputation is implemented consistently for trajectory comparisons and AUC; there is no hidden raw-array mutation in the tested path.

But a zero reference target makes an all-NaN similarity trajectory, imputed to zero, qualify immediately for first, sustained, and held events. If the reference trajectory is likewise imputed to zero, the AUC is zero too.

That follows the explicitly chosen convention. It is **not evidence of physical recovery** from an informative reference. Decide whether to label such cases `degenerate_reference`, count them under a separate convention, or define another scientifically justified outcome. Also verify how the legacy scalar similarity targets were computed: their NaN convention cannot be established from this file alone.

### Empty / below-threshold topology

`cross_t_topology` aborts if any metric is nonfinite. Finite nonzero matrices whose edges are all below `B_c` yield cosine 1 and normalized distance 0 when compared with themselves, but Jaccard NaN because both thresholded sets are empty. The entire analysis then stops.

Failing closed may be intentional. Document nondegeneracy as an input-domain requirement, or define an explicit metric-specific policy and diagnostics. Do not casually replace every undefined metric with zero. Actual incidence is unknown.

### Simultaneous coverage is family-specific

The code calibrates **five separate families**:

| Family | Number of groups |
|---|---:|
| Primary regime | 12 |
| Primary branch DID | 36 |
| Secondary regime | 12 |
| Secondary branch DID | 36 |
| Cross-condition topology | 12 |

Reusing the same draw matrix preserves dependence; it does **not** combine separately calibrated families into one overall 95% simultaneous family. The singular combined-family wording in `analysis_contract` should be made unambiguous. If one joint primary guarantee is intended, calibrate a joint maximum over its full membership.

The implemented statistic uses **fixed original-sample standard errors**, not a fresh SE in each bootstrap replicate. This can be a legitimate fixed-standardization bootstrap method; it is not automatically invalid because it is not a fully studentized bootstrap-t. Record that choice, family sizes, and critical values explicitly.

### Publication failure after rename

A forced parent-directory `fsync` failure after `os.replace(staging, final)` leaves a visible completed bundle while `_write_bundle` raises. The failure handler still assumes a staging directory. Depending on the real helper's parent-creation behavior, it can also attempt to manufacture a separate failed staging artifact.

This does not invalidate atomic rename publication. It means that **published state, return status, and durability confirmation need separate handling**. Define a post-publication failure state and include the published path in diagnostics. This test was deliberate fault injection, not an observed filesystem problem.

### Small provenance/reporting issues

- `elapsed_seconds` starts inside `_write_bundle`, so it measures the writing phase, not total analysis time.
- `main(argv=...)` records `sys.argv` rather than necessarily the supplied `argv`; space-joining also loses shell argument boundaries. Record an argument list if exact invocation provenance matters.
- The report counts conditional-DID groups, but not how many have `n=0`, very small `n`, or valid uncertainty estimates. Add those diagnostics.
- Append-only naming is implemented. Strong filesystem immutability/read-only retention would require an additional external policy.

## What passed / what I am not calling a bug

- Regime contrast signs and four-cell branch-DID signs matched known synthetic values.
- All seven raw/summary table pairs had the intended cardinalities:

| Quantity | Raw rows | Summary rows |
|---|---:|---:|
| Regime | 960 | 24 |
| Branch DID | 2,880 | 72 |
| Topology | 160 | 12 |
| Recovery events | 9,600 | 1,200 |
| Recovery AUC | 1,600 | 80 |
| Recovery event DID | 5,760 | 720 |
| Recovery AUC DID | 960 | 24 |

- The seed-alignment logic was invariant to row shuffling, preserved affine relationships under the shared plan, and rejected duplicate seeds.
- Simultaneous summaries rejected missing cohort members. The fixed-SE maximum statistic matched a separate direct calculation.
- Raw event-time DID was genuinely gated on all four observed events. Capped outcomes remained finite when a cell was unobserved.
- Density events and reference-trajectory AUC were not duplicated under the two similarity-target definitions.
- Continue-versus-itself AUC was exactly zero; a constant unit deficit integrated to **319.5**, the saved-support width, not 320.
- Raw NaNs remained present in the source NPZ after recovery calculation.
- Input changes before initial validation were detected. Missing NPZ fields and invalid trajectory schedules/ranges were rejected.
- Ordinary prepublication write failure was contained without publishing a completed bundle.
- `_sustained_index` implements the explicitly named suffix-through-last-observation definition. A last-sample-only suffix is allowed by that definition; it should not be confused with a positive-duration hold.

## Recommended next sequence

1. **Fix F1 and add exact-boundary translation tests.** Test both rejected events and incorrectly delayed events.
2. **Choose and document the recovery-time estimands** before changing caps or censoring labels.
3. **Add rate-boundary and small-complete-case inference policies**, plus diagnostic counts. Preserve pairing for DID inference.
4. **Bind analysis to verified input snapshots** and correct staged-manifest payload verification.
5. **Make numeric validation tolerant/canonical where appropriate** and declare degenerate-reference/topology policies.
6. **Run the actual input bundle** with the actual imported helpers; compare seed-level outputs before interpreting summary changes.

For real-run sign-off, supply the scalar CSV, diagnostic NPZ, simulation manifest, condition-status table, equivalence certificate, and the two imported module sources. The engine/collector definitions are also needed to verify scalar-target NaN handling, window rounding, and the scientific meaning of the saved quantities.

**No patch to the analysis program was applied in this audit.**

## Reproduction

```bash
python -m pytest -q -rx test_audit.py
python probes.py

# Show the known regressions as ordinary failures:
python -m pytest -q --runxfail --tb=short \
  -k 'fixed_hold_translation or literal_timestamp or zero_events or published_input_digest or nominal_window_check or staged_manifest_payload' \
  test_audit.py
```

`pytest_results.txt`, `unmasked_failures.txt`, and `probe_results.json` preserve the observed test outcomes. Synthetic files are temporary and no real study inputs are included.
