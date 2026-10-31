# AIEF-1.4 Split-State Memory-Carrier Ablation Plan

## Research question

After topology has formed, which state carries the information that determines future topology?

Candidate carriers:

1. Adaptive topology `B`
2. EMA state `coherence_acc`
3. Current phase state and delayed phase history
4. Continuing edge-specific resonance input
5. Static oscillator frequencies `omega`

## Stage 0 — close AIEF-1.3

Run:

```bash
python AIEF_1_3_closure_diagnostics.py
```

Confirm:

- exact unique baseline `P_future` values;
- count of intermediate persistence values;
- `Projection_active_fraction`;
- `Projection_norm_mean_active`;
- `Projection_norm_max`;
- `Pre_gap_violation_fraction`.

Do not combine the duplicate 20-seed workflow-version runs as independent cohorts. Use the two independent 50-seed cohorts as the principal validation result.

## Stage 1 — common prefix

For each paired seed, simulate one baseline prefix from `t=0` through `HIST_END`.

At the split, clone all state needed for exact continuation:

- `theta`
- `B`
- `coherence_acc`
- every array in the delay `history` deque
- historical resonance sums/counts
- the split-selected edge mask
- deterministic branch RNG seeds

Use a state container with a deep clone operation. Every NumPy array and every deque element must be copied.

## Stage 2 — future branches

| Branch | Split intervention | Question |
|---|---|---|
| `continue` | Preserve all state | Reference |
| `reset_ema` | Set `coherence_acc` to zero | Is stored estimator state needed? |
| `reset_B` | Set `B` to zero | Can retained EMA/phase state reconstruct topology? |
| `reset_B_ema` | Reset both `B` and EMA | Can phase state/history reconstruct topology? |
| `B_only` | Preserve `B`; reset EMA; randomize phases and refill delay history | Is inherited topology sufficient without dynamical resonance memory? |
| `full_reset` | Reset `B`, EMA, phases, and delay history; preserve `omega` | Can static frequency structure reselect the same topology? |
| `future_shuffle` | Preserve all split state; shuffle only the future driver each step | Is continuing edge-specific input required for maintenance? |

Do **not** use `ALPHA = 0` as an instantaneous-resonance control. Under the current definition, that produces `abs(exp(1j*dphi)) == 1` for every edge.

### Exact interventions

```python
# reset_ema
state.coherence_acc.fill(0.0)

# reset_B
state.B.fill(0.0)

# phase/history reset
state.theta = branch_rng.random(N) * 2.0 * np.pi
state.history = deque(
    (state.theta.copy() for _ in range(DELAY_STEPS + 1)),
    maxlen=DELAY_STEPS + 1,
)
```

After any `B` intervention, enforce symmetry and a zero diagonal.

For `future_shuffle`, compute physical resonance normally, then shuffle only unique undirected driver values and mirror them, exactly as in AIEF-1.3.

## Stage 3 — evaluation horizons

A reset causes a transient. Report three horizons relative to `T_WINDOW`:

1. Immediate: `0` to `1*T_WINDOW`
2. Recovery: `1*T_WINDOW` to `5*T_WINDOW`
3. Late: after `5*T_WINDOW` through the end

Primary outcomes should use the late window. Immediate and recovery outcomes are secondary.

## Primary outcome

Weighted topology similarity to the split state:

```python
def cosine_similarity_edges(B_reference, B_current, edges, eps=1e-12):
    x = B_reference[edges]
    y = B_current[edges]
    denominator = np.linalg.norm(x) * np.linalg.norm(y)
    if denominator <= eps:
        return np.nan
    return float(np.dot(x, y) / denominator)
```

Store final similarity and mean late-window similarity.

## Secondary outcomes

- Jaccard similarity of threshold-selected edges
- retention among edges selected at the split
- emergence among edges unselected at the split
- retention contrast: selected persistence minus unselected persistence
- `D_B` and `P_mean` by horizon
- total edge weight
- effective edge count
- Gini and entropy
- coherence
- gap minima
- projection frequency and norms
- time to first threshold edge after a `B` reset
- time to recover 50% and 90% of reference density

Store sampled density and topology-similarity trajectories so recovery times can be calculated after all branches finish.

## Decision logic

### `B` dominant

- `reset_B` has a large negative effect;
- `reset_ema` has a small effect;
- `B_only` remains similar to `continue`.

### EMA dominant

- `reset_ema` has a large effect;
- `reset_B` reconstructs topology;
- `reset_B_ema` performs worse than `reset_B`.

### Distributed memory

- both single resets matter;
- the double reset has a larger-than-additive effect.

For outcome `Y`, use the factorial interaction:

```text
I = Y_continue - Y_reset_ema - Y_reset_B + Y_reset_B_ema
```

### Static-frequency re-selection

If `full_reset` reconstructs a topology similar to `B_at_split`, the topology is being reselected from persistent `omega` structure rather than retained solely as dynamic memory.

### Continuing input required

If `future_shuffle` starts with intact topology but loses late similarity, future edge-specific resonance is required for maintenance.

## Statistical protocol

Use one fixed, preregistered master seed, for example:

```text
MASTER_SEED = 20260714
N_SEEDS = 40
```

Do not use `random` after viewing outcomes.

All branches are paired within seed. For each primary outcome:

```text
delta(seed) = continue(seed) - intervention(seed)
```

Report:

- mean and median paired difference;
- paired bootstrap 95% CI over seeds;
- paired SD and Cohen `d_z`;
- fraction of seeds in the predicted direction;
- supporting two-sided sign-flip result.

Primary comparisons:

1. `continue` vs `reset_B`
2. `continue` vs `reset_ema`
3. `reset_B` vs `reset_B_ema`
4. `continue` vs `future_shuffle`
5. `B_only` vs `full_reset`

Use Holm correction only if all five are treated as confirmatory hypothesis tests. Keep raw differences and bootstrap intervals as headline results.

## Implementation architecture

Recommended functions/classes:

```text
DynamicState.clone()
simulate_prefix(seed)
apply_intervention(state, branch, rng)
simulate_future(state, branch, rng)
calculate_branch_metrics(...)
run_seed_branches(seed)
```

Generate branch RNG streams deterministically from each paired seed. Branch RNG use must not alter the common prefix.

Checkpoint one file per seed containing the split state and all completed branch results. This permits branch-level resume without recomputing the prefix.

## Execution order

1. Run the AIEF-1.3 closure diagnostic.
2. Freeze this AIEF-1.4 protocol and endpoint list.
3. Implement common-prefix branching.
4. Run two smoke-test seeds.
5. Verify branch cloning by confirming `continue` exactly reproduces a normal baseline continuation.
6. Verify deterministic checkpoint resume.
7. Run 40 paired seeds.
8. Analyze before performing `DT`, `B_C`, or positive `T_WINDOW` sensitivity sweeps.
