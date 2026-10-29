# Copy/paste prompt for the V4 coding agent — matched-phase AIEF-1.4 correction

You are the coding agent that produced the successful AIEF-1.4 V4 two-channel directed-alignment analysis. You have not participated in subsequent work. Treat this prompt as the complete task specification. Do not infer a different task from newer exploratory files in the workspace.

Your role is implementation and validation, not broad scientific interpretation.

---

## 1. Task

Create a new, separately versioned production-grade script:

```text
AIEF_1_4_matched_phase_memory_ablation.py
```

Its purpose is to correct the unmatched phase/history randomization in the existing comparison:

```text
B_carrier_only  versus  full_reset
```

in the frozen AIEF-1.4 memory-ablation experiment.

The original branches both reset EMA and randomize phase/history, but they used different branch-specific random draws. Therefore their difference combines:

1. preservation versus removal of mature `B`; and
2. different randomized phase/history initial conditions.

The new script must construct **matched phase/history reset blocks** so that, within each block and seed, the two branches differ only in initial `B`.

Do not create another seed cohort. Use the existing 40 paired seeds from the frozen run.

---

## 2. Scientific estimand

For each frozen seed/graph, estimate the effect of preserving mature `B`, conditional on:

- the same randomized phase vector;
- the same randomized history deque;
- the same zeroed complex EMA state;
- the same `omega`;
- the same future dynamics and safeguards.

The primary branch contrast is:

\[
Y(B=B_{\rm split})-Y(B=0)
\]

under an otherwise identical reset state.

This is a controlled counterfactual about the contribution of mature `B`. It is **not** a test that `B` is the unique memory carrier.

---

## 3. Frozen sources and inputs

Inspect before coding:

```text
AIEF_CODING_AGENT_PROMPT.md
AIEF_1_4_memory_ablation_updated.py
AIEF_1_4_trajectory_recovery_equivalence.py
runs/5a9f093a2fe0/manifest.json
runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz
runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv
```

Use the frozen run manifest and per-analysis manifests as hash authorities.

Do **not** modify:

```text
AIEF_1_4_memory_ablation_updated.py
```

Import it as a production dependency, for example:

```python
import AIEF_1_4_memory_ablation_updated as prod
```

Reuse its code-identical functions wherever possible, especially:

```python
prod.apply_intervention
prod.simulate_future
prod.time_to_at_least
prod.time_to_below
```

You may also reuse validated recovery helpers from:

```text
AIEF_1_4_trajectory_recovery_equivalence.py
```

Do not import or rely on later exploratory slow-spectrum, multi-seed bundle, or K3-prevalence scripts. They are unrelated to this task.

---

## 4. Exact matched-reset design

Use **two matched reset blocks per seed**, based on the two original branch-specific reset draws. This preserves direct anchors to both original branches and reduces dependence on one arbitrary reset realization.

The original production branch RNG seeds are reconstructed exactly using the original algorithm:

```python
_, branch_root = np.random.SeedSequence(seed).spawn(2)
branch_sequences = branch_root.spawn(len(branch_order))
branch_rng_seeds = {
    branch: int(sequence.generate_state(1, dtype=np.uint64)[0])
    for branch, sequence in zip(branch_order, branch_sequences)
}
```

Obtain `branch_order` from the frozen manifest and require exact agreement with `prod.BRANCHES`. Abort on disagreement.

### Reset block A — original `B_carrier_only` reset realization

Use:

```python
reset_seed = branch_rng_seeds["B_carrier_only"]
```

Run:

```text
carrier_reset__B_preserved
carrier_reset__B_zero
```

by calling `prod.simulate_future` with separate generators initialized from the **same** `reset_seed`:

```python
prod.simulate_future(
    split_state,
    prefix,
    "B_carrier_only",
    np.random.default_rng(reset_seed),
)

prod.simulate_future(
    split_state,
    prefix,
    "full_reset",
    np.random.default_rng(reset_seed),
)
```

The first result must exactly reproduce the frozen original `B_carrier_only` branch.

### Reset block B — original `full_reset` reset realization

Use:

```python
reset_seed = branch_rng_seeds["full_reset"]
```

Run:

```text
full_reset__B_preserved
full_reset__B_zero
```

using the same two production branch labels with the same reset seed.

The second result (`B_zero`) must exactly reproduce the frozen original `full_reset` branch.

### Continue reference

Also replay or load the frozen `continue` trajectory for each seed. If replayed, require exact equality with the frozen continuation arrays.

### Important nesting rule

The two reset realizations are repeated controlled contexts within one seed. They are **not independent seed replicates**.

---

## 5. Load the frozen split state; do not regenerate incompatible prefixes

Prefer loading the exact split state and prefix arrays from the frozen NPZ rather than rerunning the prefix.

The NPZ keys use:

```text
prefix_seed_<seed>_<metric>
<branch>_seed_<seed>_<metric>
```

Construct a `prod.DynamicState` from:

```text
theta_at_split
B_at_split
coherence_acc_at_split
history_at_split
```

with a deque having the saved maximum length.

Load every key required by `prod.simulate_future` from `prod.PREFIX_KEYS`, including:

```text
B_at_split
R_physical_past
theta_at_split
coherence_acc_at_split
history_at_split
selected_at_split
```

Use copies. Do not mutate the NPZ-backed arrays.

Validate dimensions, symmetry, zero diagonal, deque length, and exact seed identity.

---

## 6. Initial-state matching audit — mandatory

Before running the future simulation, independently construct the two intervention states for each reset block using `prod.apply_intervention` and generators initialized from the same reset seed.

For each seed and reset block, require exact equality of the matched branches for:

```text
theta
history
coherence_acc
```

Require:

```text
coherence_acc == 0 exactly in both branches
B_preserved.B == B_at_split exactly
B_zero.B == 0 exactly
```

The two branches must differ only in `B`.

Also verify:

- `B` symmetry and zero diagonal;
- every history entry equals the reset theta, as defined by the production intervention;
- RNG state after intervention is identical between the two matched generators;
- the original split state remains unchanged after every branch simulation.

Save one row per seed/reset block to:

```text
matched_initial_state_audit.csv
```

Include exact Boolean fields and SHA-256 hashes of the initial arrays.

Any failure is fatal. Do not write a scientific summary from a partially matched run.

---

## 7. Frozen-anchor validation — mandatory

Use the frozen NPZ as the historical output authority.

For every seed, require exact array equality for the anchor branches:

### Carrier-origin block anchor

```text
carrier_reset__B_preserved
```

must reproduce frozen:

```text
B_carrier_only
```

### Full-reset-origin block anchor

```text
full_reset__B_zero
```

must reproduce frozen:

```text
full_reset
```

### Continue anchor

The continue reference must reproduce frozen:

```text
continue
```

Compare all available production matrix/trajectory keys in `prod.BRANCH_MATRIX_KEYS`, not merely final scalar summaries. At minimum compare exactly:

```text
B_final
B_mean_late
P_full
P_late
sample_times
density_trajectory
similarity_trajectory
```

Save:

```text
frozen_anchor_validation.csv
```

with maximum absolute differences and exact-equality flags.

Any anchor failure is fatal. It may indicate source-hash drift, RNG mismatch, branch-order mismatch, or a state-loading bug. Do not weaken the comparison tolerance to force a pass.

---

## 8. Branch IDs and output schema

Use these unambiguous output branch IDs:

```text
carrier_reset__B_preserved
carrier_reset__B_zero
full_reset__B_preserved
full_reset__B_zero
continue
```

Also store separate columns:

```text
reset_source      # carrier_reset, full_reset, or continue
B_status          # preserved, zero, or continue
production_intervention_label  # B_carrier_only, full_reset, continue
reset_seed_uint64
```

Do not collapse the two reset blocks before saving raw results.

---

## 9. Primary outcomes

Save all scalar outcomes returned by `prod.simulate_future`, but designate these as primary:

```text
P_mean_late
Weighted_similarity_late
Weighted_similarity_final
Retention_selected_late
Emergence_unselected_late
D_B_final
Total_edge_weight
Effective_edges
Nonzero_edge_fraction
Minimum_similarity
```

Also compute trajectory recovery outcomes using the existing validated conventions:

```text
time_to_similarity_90
sustained_similarity_90_rest
held_similarity_90_for_1Twindow
AUC_similarity_deficit_vs_continue
Mean_similarity_deficit_vs_continue
time_to_density_90
sustained_density_90_rest
AUC_density_deficit_vs_continue
```

Use the frozen/replayed continue branch as the within-seed recovery reference.

Preserve the existing convention that a cosine similarity `NaN` caused by an exactly zero edge vector is mapped to zero **only for recovery/loss calculations**, while raw similarity outputs remain `NaN`.

First crossing and sustained recovery are distinct estimands. Do not conflate them.

---

## 10. Paired contrasts and inferential unit

For each seed and reset source, compute:

\[
\Delta_{s,r}(Y)
=
Y_{s,r,B\ preserved}-Y_{s,r,B\ zero}.
\]

Save:

```text
matched_phase_paired_contrasts.csv
```

with one row per seed, reset source, and outcome, or an equivalently clear wide schema.

Also compute the predeclared seed-level average contrast:

\[
\bar\Delta_s(Y)
=
\frac12
\left[
\Delta_{s,carrier}(Y)
+
\Delta_{s,full}(Y)
\right].
\]

and reset-realization interaction/sensitivity:

\[
I_s(Y)
=
\Delta_{s,carrier}(Y)-\Delta_{s,full}(Y).
\]

Save:

```text
matched_phase_seed_level_contrasts.csv
```

The seed/graph is the inferential unit. Bootstrap or summarize across 40 seeds only. Do not treat the 80 reset-block contrasts as 80 independent observations.

For continuous outcomes, report:

- paired mean and median contrast;
- standard deviation across seeds;
- deterministic seed-level bootstrap 95% interval for the mean;
- positive/zero/negative seed counts.

For binary sustained-recovery outcomes, report:

- recovery probability for each `B_status`;
- paired discordant counts;
- difference in seed-level recovery probability;
- exact or clearly labeled descriptive paired interval/test if implemented.

Censored recovery times must not be summarized only among recovered seeds. Report recovery probability and an RMUT/AUC-style measure over the fixed horizon.

---

## 11. Required outputs

At minimum create:

```text
matched_phase_scalar_summary.csv
matched_phase_paired_contrasts.csv
matched_phase_seed_level_contrasts.csv
matched_phase_recovery_summary.csv
matched_initial_state_audit.csv
frozen_anchor_validation.csv
matched_phase_branch_diagnostics.npz
matched_phase_report.txt
analysis_manifest.json
```

The NPZ should contain branch matrices and sampled trajectories with keys that include seed and full branch ID.

Write outputs atomically. Support resumable per-seed checkpoints if practical. A failed seed must remain visible in a seed-status table; do not silently drop it.

---

## 12. Manifest requirements

The manifest must record:

- new script path and SHA-256;
- current imported production source path and SHA-256;
- frozen production manifest path and SHA-256;
- frozen NPZ path and SHA-256;
- frozen scalar CSV path and SHA-256;
- command line;
- all 40 seed IDs as strings and integers where needed;
- exact branch order used to reconstruct original RNG seeds;
- branch RNG derivation algorithm;
- matched reset-block design;
- model constants copied from the frozen manifest;
- all output filenames;
- successful/failed seed counts;
- initial-match pass count;
- anchor-validation pass count;
- bootstrap seed and repetitions;
- software versions;
- interpretation constraints.

Historical execution hashes in the frozen run remain authoritative. Current source hashes do not replace them.

---

## 13. Required validation and tests

Before presenting the script, run:

```bash
python -m py_compile AIEF_1_4_matched_phase_memory_ablation.py
python AIEF_1_4_matched_phase_memory_ablation.py --help
python AIEF_1_4_matched_phase_memory_ablation.py --self-test
```

Implement `--self-test` without requiring frozen inputs. It must test at least:

1. same reset seed produces exactly equal theta/history/EMA for both intervention labels;
2. only `B` differs after matched intervention;
3. reset-block contrast construction and seed-level averaging are correct on synthetic rows;
4. binary paired counts are correct;
5. array hashing includes shape, dtype, and contiguous bytes;
6. atomic output helpers work in a temporary directory.

Then run a smoke test on one frozen seed, requiring:

- exact initial matching;
- exact continue anchor;
- exact original `B_carrier_only` anchor;
- exact original `full_reset` anchor;
- no split-state mutation;
- expected output schemas.

Only after the one-seed smoke test passes should the 40-seed run be attempted.

---

## 14. CLI requirements

Provide reproducible defaults for the frozen run and options such as:

```text
--npz
--manifest
--scalar
--output-dir
--max-seeds
--seed-filter
--bootstrap-repetitions
--bootstrap-seed
--resume
--verify-anchors / --no-verify-anchors
--self-test
```

For production defaults, anchor verification must be on. `--no-verify-anchors` may exist only for debugging and must mark outputs non-production/non-freezeable.

Fail clearly when inputs are absent. Do not silently run a synthetic experiment.

---

## 15. Scientific interpretation constraints

The report may state only what the matched experiment estimates.

Allowed wording:

```text
Preserving mature B has [measured] conditional effect under matched randomized phase/history and reset EMA.
```

Forbidden wording:

```text
B is the unique memory carrier.
B stores the attractor by itself.
No other state variable matters.
Matched reset proves universal causality.
```

Keep separate:

- storage;
- reconstruction;
- maintenance;
- threshold topology;
- continuous-weight similarity;
- recovery probability;
- recovery time conditional on recovery.

Repeated workflow runs with the same seeds are not independent evidence.

---

## 16. Do not change the model

Do not change:

```text
N
dt
tau
T_window
alpha
omega
eta
mu
gamma
capacity
B_c
delay indexing
EMA update
positivity map
symmetrization
global gate
minimum.outer scaling
fixed +1e-12 safeguard
future horizon
diagnostic stride
seed list
```

This is a matched intervention correction under the original AIEF-1.4 dynamics, not AIEF-1.5.

---

## 17. Stop conditions

Stop and report rather than continuing if:

- frozen branch order differs from the imported production branch order;
- any required frozen key is missing;
- matched theta/history/EMA equality fails;
- any anchor branch fails exact replay;
- continue replay is not exact;
- a split state is mutated across branches;
- fewer than all requested seeds complete without explicit failure rows;
- current production constants differ from the frozen manifest;
- output schemas differ across seeds.

Do not weaken exact checks merely to obtain a result.

---

## 18. Final response format

Return:

```text
Created
Validation performed
One-seed smoke-test result
Full run command
Inputs
Outputs
Known limitations
```

Keep interpretation brief. Deliver working code, exact commands, and test results.
