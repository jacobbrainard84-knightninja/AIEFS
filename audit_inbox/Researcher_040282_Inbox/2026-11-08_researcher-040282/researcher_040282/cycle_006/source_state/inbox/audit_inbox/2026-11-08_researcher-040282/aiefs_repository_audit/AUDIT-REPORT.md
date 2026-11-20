# AIEFS: deep audit of `audit-inbox`

**Date:** 7 November 2026  
**Scope:** the source and selected real artifacts on the user-requested `audit-inbox` branch. GitHub was accessed read-only. No changes were committed or pushed to the target repository; no patch or PR was submitted.

## Executive assessment

**The numerical workflow has meaningful safeguards, but its green tests are not enough to establish upload safety, calibrated statistical uncertainty, or complete scientific certification.**

I confirmed seven findings, using eight failing regression witnesses. The most consequential operational findings are silent loss of an ignored local file during upload and incomplete inspection of committed material being pushed. The clearest issue affecting the actual S01 reanalysis is boundary-degenerate event-rate uncertainty: **222 of 240 event-rate intervals have zero width**.

The scientific assessment is not uniformly negative:

- The actual saved S01 inputs validated successfully, and their complete reanalysis ran successfully with 2,000 bootstrap replicates.
- An independent saved-grid oracle agreed with **all 4,800 actual held-event classifications**. A floating-point boundary defect exists, but I found **no classification impact on this saved dataset**.
- For one complete condition, the modular and original orchestration produced **exactly equal logical numerical outputs in the same audit environment**.
- Conditional projection identities passed when tested on a proposal that actually satisfies their branch assumptions. A separate repository self-test uses an invalid branch fixture and nevertheless prints `PASS`.
- The inspected Lean sources explicitly distinguish their algebraic projectors from the implemented capacity map. I found no basis for treating those files as a proof of global closed-loop convergence, and their own comments do not claim that.

These results do **not** establish that the saved trajectories are wrong, that the entire model is false, or that a global dynamics theorem has been proved.

## Findings at a glance

Priority: **P1** = address before relying on the helper for ordinary work; **P2** = address before relying on the affected inferential/certification claim; **P3** = validation hardening.

| ID | Priority | Finding | Demonstrated impact |
|---|---|---|---|
| F1 | P1 | Upload integration can overwrite an ignored local file without preserving it | Reproduced with dummy files and a local bare remote; exit 0, original content replaced, no stash |
| F2 | P1 | Upload checks do not inspect all committed content/history being pushed | Synthetic credential-shaped content and a deleted historical 2 MiB blob both reached a local remote |
| F3 | P2 | Percentile event-rate intervals collapse at sample boundaries | Actual S01: 28 zero-event and 194 all-event groups; 222 zero-width intervals |
| F4 | P2 | Proposal-bridge self-test constructs the wrong projection for its own fixture | Prints `PASS`; real operator violates the asserted left identity by about 0.0212146 |
| F5 | P2 | Held-event search has a floating-point grid-boundary error | Deterministic counterexample; zero mismatches among the 4,800 saved S01 held cases |
| F6 | P3 | Engine's complex-NaN equality can hide a changed finite component | Comparator returns true for `nan+1j` versus `nan+99j`; no affected complex arrays found in supplied datasets |
| F7 | P3 | Oracle comparison accepts duplicate condition-status records | Public comparator returns `passed` for 201 candidate rows versus 200 reference rows |

## F1 — Upload can silently replace an ignored local file

**Source:** [`tools/sync/upload_new.sh:80–105`](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/5c1ffed0377c4769154e9342464ce7265cf1c599/tools/sync/upload_new.sh#L80-L105), especially the `git pull --rebase --autostash` integration.

The uploader integrates upstream changes before classifying files and before asking for upload confirmation. It does not perform the ignored/untracked collision checks present in the download helper. Git's autostash does not, by default, preserve ignored local files.

**Reproduction:**

1. Start with `*.log` ignored and an untracked local `experiment.log` containing dummy local observations.
2. A second clone force-adds a different `experiment.log` and pushes it to a **temporary local bare remote**.
3. Run the actual uploader with `--yes` in the first clone.

**Observed:** exit **0**; local content changes from `IRREPLACEABLE LOCAL OBSERVATIONS` to `UPSTREAM CONTENT`; `git stash list` is empty. The actual download helper, tested against the same collision setup, exits **1** and preserves the local content.

This demonstrates a data-preservation gap, not an incident involving the user's files. It can occur during integration even if there is ultimately nothing to upload. The destructive step precedes the normal confirmation prompt.

**Recommendation:** share the downloader's pre-integration collision protection with the uploader, including ignored files and relevant file/directory collisions. Stop before integration or make a verified backup; do not rely on autostash for this protection.

**Evidence:** `evidence/local_git_safety_probes.json`, `upload_ignored_collision.txt`, `download_ignored_collision_control.txt`; regression `test_uploader_preserves_ignored_file_when_upstream_now_tracks_it`.

## F2 — Already-committed material bypasses advertised content/history checks

**Source:** [`tools/sync/upload_new.sh:131–176`](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/5c1ffed0377c4769154e9342464ce7265cf1c599/tools/sync/upload_new.sh#L131-L176).

The working-tree path calls `has_secret_content`. The unpublished-commit path does not. It examines only net added/modified filenames from `git diff BASE HEAD`, sizes at `HEAD`, name patterns, and ignore state. This is not the set of all blobs reachable through commits sent by a push.

Two independent witnesses succeeded:

- **Committed content:** an innocently named text file containing a deliberately invalid, synthetic GitHub-token-shaped string was committed locally. The uploader exited **0** and pushed it. The same shape in an **uncommitted** file was correctly blocked, demonstrating that the regex/control was active.
- **Intermediate history:** commit a 2 MiB file, then remove it in a second commit while making a small allowed README change. With `--max-size-mb 1`, the uploader exited **0**. The local remote contained the **2,097,152-byte historical blob**, despite the **1,048,576-byte** limit. Removing a blob from the tip does not remove it from pushed history.

All pushes in these experiments were to temporary local filesystem remotes. No real credential was used or disclosed.

**Recommendation:** inspect committed blobs and path history reachable through the proposed push, not just the current worktree or base-to-tip diff. Apply the advertised content and size policies to that material. A conservative alternative is to refuse unpublished commits until they have been explicitly reviewed. A regex scanner still cannot promise detection of every possible secret; the immediate defect is that even the existing scanner is bypassed.

**Evidence:** `evidence/local_git_safety_probes.json`, `upload_committed_content.txt`, `upload_historical_blob.txt`; two corresponding strict expected-failure tests.

## F3 — Boundary-degenerate event-rate confidence intervals

**Source:** [`AIEF_1_4_Twindow_sensitivity_analysis_v4.py:977–1020`](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/5c1ffed0377c4769154e9342464ce7265cf1c599/AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4.py#L977-L1020).

`pointwise_summary` constructs a percentile interval from empirical seed-resampling means and labels it a 95% interval. If every observed event indicator is zero, every bootstrap mean is zero and the interval is `[0,0]`. The analogous all-one interval is `[1,1]`.

**Actual-data result:** the complete real S01 reanalysis produced **240 event-rate groups**:

- **28** had mean 0;
- **194** had mean 1;
- **222**, or **92.5%**, had zero-width pointwise intervals.

These are faithful empirical bootstrap outputs. They are **not reliable 95% confidence statements about a seed-population event probability at the boundary**.

A coverage counterexample makes the distinction precise. Under independent Bernoulli seeds with true probability `p = 0.01` and `n = 40`, an all-zero sample occurs with probability `0.99^40 = 0.6689718`. On that event, `[0,0]` excludes the truth. Consequently this procedure's coverage is at most **33.10%** in that example, not 95%. For comparison, the two-sided exact binomial 95% interval at 0/40 has upper endpoint approximately **0.08810**, under those assumptions. This example does not assert that the actual unknown probability is 0.01.

If the intended target is only the fixed, fully observed 40-seed cohort, describe the interval as an empirical resampling diagnostic rather than population uncertainty. If generalization across random seeds is intended, the boundary behavior needs a suitable rate-interval method and the contrast/family procedure needs its own calibration.

**Recommendation:** specify the inferential population and assumptions. Use boundary-aware marginal intervals where a Bernoulli-seed interpretation is appropriate; separately validate any paired or simultaneous contrast procedure. Do not infer joint family coverage merely from marginal fixes.

**Evidence:** actual generated `twindow_recovery_event_summary_v4.csv`; `evidence/real_s01_execution.json`; analytic values in `independent_scientific_probes.json`; regression `test_rate_interval_does_not_assert_zero_population_uncertainty`.

## F4 — A passing scientific self-test uses the wrong admissibility branch

**Source:** [`AIEF_1_4_proposal_equalization_bridge_analysis.py:198–232`](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/5c1ffed0377c4769154e9342464ce7265cf1c599/AIEF_1_4_proposal_equalization_bridge_analysis.py#L198-L232). Independent comparison uses the repository's actual pure operator, [`AIEF_1_4_actual_admissibility_branch_audit.py:211–252`](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/5c1ffed0377c4769154e9342464ce7265cf1c599/AIEF_1_4_actual_admissibility_branch_audit.py#L211-L252).

The fixture sets `(x25,x29,x59) = (0.41,0.31,0.27)` and manually builds projected edges using endpoint winners `(7,2,7)`.

But, using the source's node numbering, the proposal row sums are:

| Node | Proposal row sum | Clipped scale |
|---|---:|---:|
| 2 | 0.72 | 0.8796296296 |
| 7 | 0.68 | 0.9313725490 |
| 11 | 0.58 | 1 |

The actual min-endpoint rule therefore selects **`(2,2,7)`**, not `(7,2,7)`. In particular:

- manually constructed projected edge 25: **0.3818627451**;
- actual projected edge 25: **0.3606481481**.

The self-test prints `Synthetic proposal-equalization bridge checks: PASS`. Applied to the real operator, its asserted left identity has residual **−0.02121459695**, far above its `1e-14` tolerance.

**Scope:** this disproves the self-test's claim to exercise the intended projection on its chosen fixture. It does **not** disprove the conditional algebra, the other identities in that self-test, or the saved replay's branch validity. A positive control with `(0.41,0.27,0.31)` produces the intended winners and satisfies both tested projection identities.

**Recommendation:** evaluate the implemented operator, assert the branch conditions explicitly, and include an out-of-branch negative control. Merely changing a manually constructed answer would leave the test's independence weak.

**Evidence:** `evidence/independent_scientific_probes.json`; `test_bridge_selftest_fixture_matches_the_implemented_gate` and its valid-branch positive control.

## F5 — Held-event detection is not translation-stable on its declared grid

**Source:** [`AIEF_1_4_Twindow_sensitivity_analysis_v4.py:541–558`](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/5c1ffed0377c4769154e9342464ce7265cf1c599/AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4.py#L541-L558).

The search forms `times[index] + duration` and calls `searchsorted`. On the declared half-unit saved grid, a true block at indices **32 through 67 inclusive** spans **35 intervals × 0.5 = 17.5**. `_held_index(..., duration=17.5)` nevertheless returns `None`, because floating-point addition places the requested endpoint just beyond the saved endpoint. Adding one more true sample makes the control pass.

**Important actual-data limit:** I independently classified **all 4,800 held-event cases** in the saved S01 reanalysis using contiguous integer grid spans. There were **zero mismatches**. This is a confirmed latent correctness defect, not observed corruption of those saved classifications.

**Recommendation:** define endpoint semantics on validated grid ticks with an explicit rounding/tolerance policy. Add tests at many translated starting indices, including nominal durations that do and do not land on the grid. Subtraction alone is not a general numerical-policy fix.

**Evidence:** `test_saved_grid_hold_exact_boundary_translation`; actual-data check `check_real_s01.py` and `evidence/real_s01_execution.json`.

## F6 — Complex NaN masking can report false exact equivalence

**Source:** [`aief_experiment_engine_v1.py:1755–1768`](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/5c1ffed0377c4769154e9342464ce7265cf1c599/aief_experiment_engine_v1.py#L1755-L1768). The helper is used by baseline comparisons, including the prefix-array comparison near line 2430.

For complex numbers, `np.isnan(z)` is true if either component is NaN. The engine masks out the entire complex value whenever this occurs. Thus arrays containing **`complex(nan,1)`** and **`complex(nan,99)`** compare equal, despite their different finite imaginary components.

The modular comparator already handles this correctly by comparing real and imaginary parts separately, and it rejects the same witness.

**Actual-data limit:** all **40** complex arrays in the supplied frozen baseline and all **200** complex arrays in supplied S01 were finite. I did not observe a false saved baseline certificate. The full numerical baseline gate was not rerun.

**Recommendation:** use componentwise complex comparison when missingness is legitimate; where complex engine state must be finite, reject nonfinite state before equality testing. Preserve legitimate missing-value behavior for other diagnostics rather than banning all NaNs indiscriminately.

**Evidence:** paired engine/modular comparator tests; `evidence/independent_scientific_probes.json` records the real-data finiteness check.

## F7 — Duplicate condition-status rows pass the public oracle comparison

**Source:** [`aief_modular/oracle.py:97–111`](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/5c1ffed0377c4769154e9342464ce7265cf1c599/AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/oracle.py#L97-L111).

Condition records are reduced to sets of `(seed,rho,status)`, which erase duplicate multiplicity. The returned row count is reported but not checked against the reference count.

I exercised the **public** `compare_twindow_run` on the actual S01 scalar CSV and NPZ, unchanged, with exactly one duplicate status row appended to a temporary candidate:

```text
oracle condition rows:    200
candidate condition rows: 201
comparison status:       passed
scalar rows compared:    800
NPZ entries compared:    68,800
errors:                  []
```

This is a known-false artifact-validation control, **not** a regenerated production candidate or evidence of numerical equivalence of the modular platform. Its narrow conclusion is that duplicate condition records are not rejected.

**Recommendation:** check row counts and unique condition keys explicitly, then compare the required status for each expected condition. Keep logical-content comparison independent of incidental row ordering where ordering is not part of the contract.

**Evidence:** `probe_duplicate_oracle.py`, `evidence/duplicate_public_oracle.json`, and duplicate/changed-coverage unit controls.

## What actually ran

| Check | Result and boundary |
|---|---|
| Existing modular pytest suite | **40 passed, 2 skipped**; orchestration/unit tests are not full numerical certification |
| Repository's opt-in numerical smoke | **1 passed** separately with `AIEF_RUN_SLOW_TESTS=1` |
| Existing sync shell suite | **108 checks passed, 0 failed**; documented `chmod` setup applied only to a temporary copy |
| Added independent audit suite | **9 passed, 8 strict expected failures**; the eight witnesses fail when unmasked |
| Real frozen-authority input/source lock verification | Passed against the actual downloaded inputs and source files; not a numerical baseline rerun |
| Actual S01 validation | Passed: **40 seeds, 800 scalar rows**; all five nominal-window equality checks passed |
| Complete actual S01 reanalysis | Succeeded with bootstrap seed **20260814**, **2,000** replicates; no dependency stand-ins |
| Actual held-event cross-check | **4,800 checked, 0 mismatches**; 9,600 total event rows |
| Same-environment modular/original one-condition replay | **344 logical NPZ entries and four scalar rows matched exactly** |
| Exact comparison of that replay with saved S01 | Did **not** match exactly: **131 NPZ entries and 89 scalar cells differed**; largest recorded finite array/entry difference about **4.41×10⁻¹³** |
| Public oracle known-false duplicate control | Incorrectly returned `passed`, confirming F7 |
| Lean build | **Not run**; Lean/lake unavailable |

### Numerical replay: do not confuse environment drift with orchestration failure

The saved S01 manifest records Python **3.13.5**, NumPy **2.5.1**, and a different Linux environment. The audit used Python **3.13.16**, NumPy **2.3.5**. Even the EMA coefficient differed by **1.11×10⁻¹⁶** from its saved value.

The modular and original drivers agreed exactly when both ran in the current environment. That is bounded positive evidence for their orchestration equivalence. The saved output did not reproduce bit-for-bit here, so I do **not** certify saved-run exact numerical reproducibility or attribute the observed tiny differences to an orchestration bug. A matched numerical stack and the full gate are needed to resolve exact reproduction.

### Additional actual-data interpretation limits

- Conditional event-time DID produced **144 groups**, including **24 with no qualifying complete cases**. Remaining sample-count distribution: `n=11: 2`, `12: 2`, `37: 2`, `39: 38`, `40: 76`. These are selected conditional summaries, not automatically unconditional recovery effects.
- No actual event row had a zero reference target, and no actual event row was affected by undefined-similarity-to-zero imputation.
- Events are detected on saved samples. A held event is confirmed retrospectively on that grid; it is not proof of continuous-time threshold persistence between samples.
- The earlier synthetic nominal-window equality problem was **not reproduced on actual S01**. I have not promoted it into a finding about this dataset.

## Scientific and formal assessment

Positive independent controls included exact rational complete-graph incidence nullities for `n=3…8`, a row-sum-fiber identity checked through the actual admissibility helper, and a non-fiber perturbation that the same check correctly rejected. These are targeted algebraic controls, not a Lean compilation or a global dynamics proof.

The inspected [`ControllerFiberProjector.lean:16–39`](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/5c1ffed0377c4769154e9342464ce7265cf1c599/lean/AIEFProofs/AIEFProofs/ControllerFiberProjector.lean#L16-L39) explicitly says its rational Euclidean projector is **not** the implemented admissibility/capacity projection, and that the required dynamical invariance is not established there. The theorem-freeze source also separates conditional identities, finite replay observations, and open persistence/asymptotic claims. I do not count those explicit qualifications as defects.

The root workflow on this target runs the Lean project on Lean/workflow-path changes. It does not provide an automatic test gate for changes to the Python engine, statistical analysis, or sync scripts. The passing local suites therefore matter, but neither their existence nor Lean-related CI implies coverage of the Python findings above.

I read the inbox triage ledger before finalizing this report. The documented CLI import-path problem was reproduced: invoking `describe` from the package directory without a repository-root import path exits 2. It is already recorded in triage and is a setup/usability issue, not an additional scientific finding here. Likewise, the sync README documents executable-permission setup; tracked nonexecutable helper modes are **not** reported as a defect.

## Limitations and reproducibility

This was a deep **targeted** audit, not a claim that every experiment or every tracked artifact was executed. The verified sparse HTTP snapshot contains **937 files / 63,222,149 bytes** of selected source, configuration, small artifacts, and the required real baseline/S01 files. It is not a git clone. Final verification found **zero content or mode differences** against the fetched tree for these files.

Not performed: the full 40-seed numerical baseline regeneration, the full 200-condition modular production run and its real regenerated-candidate oracle certification, the complete repository-wide scientific negative-control collection, the full bridge replay, a Lean build, or independent literature/novelty adjudication. No claims about uninspected large datasets or another branch follow from this report. Paste-attributable formatting issues were excluded.

Reproductions and raw results are in the accompanying package. The source reference used throughout is the requested branch snapshot at `5c1ffed0377c4769154e9342464ce7265cf1c599`.

**Suggested repair order:** protect local files and scan pushed history first; fix the invalid scientific self-test and uncertainty interpretation next; then harden grid arithmetic, complex equality, and oracle uniqueness. Re-run the negative controls after any proposed changes. No patch has been applied.
