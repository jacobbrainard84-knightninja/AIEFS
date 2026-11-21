Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-21T16:24:58.427532-07:00 MST (host-reported, UNVERIFIED; see CLOCK_NOTE.md)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (instrumented copy)  
Scope: Gate spillover lane, DIRECTION-1  
Status: UNVERIFIED by project seats

# Raw data and summary schema

Each raw/seed_<uint64>.npz contains:
- row_sum_pre: float64 [80000,12], actual pre-gate row sums.
- scale: float64 [80000,12], actual engine scale when gated; all ones by convention when ungated.
- r_post: float64 [80000,12], sum of the copied actual B_projected.
- pre_violation: bool [80000], engine guard value.
- projection_active: bool [80000], unchanged engine norm-threshold decision.
- capacity: scalar float64, engine config.capacity.
- metadata_json: Unicode JSON shared provenance.

Index k identifies the transition starting at k*0.01; prefix indices 0..47999, reference future indices 48000..79999. Row i is oscillator index i. Only pre_violation=True rows enter d/l statistics. Zero-load bystanders are not divided by zero. Exact float64 values, including subthreshold and tiny signed values, are retained. NPZ loads with allow_pickle=False; there are no object arrays.

Derived values:
```python
with np.load(path, allow_pickle=False) as z:
    g = z['pre_violation']
    q, s, r = z['row_sum_pre'][g], z['scale'][g], z['r_post'][g]
    c = float(z['capacity'])
    binding = s < 1
    eligible_bystander = (s == 1) & (q > 0)
    d = (c - r[binding]) / c
    loss = (q[eligible_bystander] - r[eligible_bystander]) / q[eligible_bystander]
    binding_counts_per_gated_step = binding.sum(axis=1)
    bystander_counts_per_gated_step = (s == 1).sum(axis=1)
```

summary.json includes all seven predeclared windows, per-seed and pooled. `all_eligible` includes non-events; `event_only` uses the strict >1e-9 rule. Null values indicate empty denominators/populations. Histogram/ECDF alternatives can be recomputed from the exact raw arrays; no binning discards the distribution.

NPZ original_outputs / instrumented_outputs contain every flattened returned prefix/future value, full split/final state/history and final RNG state for the first seed. Huge integer RNG fields are stored as decimal strings to avoid object arrays; arrays retain dtype/shape/bytes. Consult no_instrumentation.json for the stream digest and exact equality status.
