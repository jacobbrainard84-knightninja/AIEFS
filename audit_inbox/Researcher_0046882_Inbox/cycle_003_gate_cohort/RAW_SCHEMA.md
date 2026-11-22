Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-22T03:01:39.733080-07:00 (host-reported MST; not authenticated)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (copy)  
Scope: Gate spillover lane, DIRECTION-2; full 40-seed reference cohort  
Status: UNVERIFIED by project seats

# Raw data retention and descriptor schema

## Full gate observations (regenerate; hashes delivered)
Each temporary raw seed_<seed>.npz has six numeric arrays:
- row_sum_pre: float64 [80000,12].
- r_post: float64 [80000,12], sum of actual copied B_projected.
- scale: float64 [80000,12], actual scales on gated steps; ones by convention otherwise.
- pre_violation: bool [80000].
- projection_active: bool [80000].
- capacity: scalar float64.

All240 arrays are inventoried in evidence/raw_array_hashes.json: exact dtype.str (including byte order), shape, nbytes and SHA256 of contiguous C-order raw bytes. Hashes are NOT of the NPZ container, whose timestamps/compression may vary. Full raw NPZs are deliberately not in this ZIP, because the persisted workspace cannot hold them all. They can be regenerated with the included source and inputs; cache is not durable storage.

## Delivered compact future descriptors
For each of all 40 seeds, descriptors/future_<seed>.npz:
- binding_count: uint8 [32000].
- min_scale: float64 [32000], minimum across all 12 endpoint scales.
- binding_load_spread: float64 [32000], max-minus-min pre-load among binding rows; one binding row gives0, none givesNaN explicitly as undefined.
- pre_violation: bool [32000].
- metadata_json: Unicode JSON shared provenance.

These refer to global transitions48000..79999, starting at k*dt with dt=.01. They permit direct review of temporal variation without storing the full matrices. They do NOT permit re-thresholding all omitted d/l observations without regeneration.

## Tables
per_seed_windows.csv contains40x7=280 rows. Read seed as a string/uint64, never an Excel floating-point number. Blank numeric cells represent missing/undefined quantities, not zeros. Full precision is retained in JSON.
future_descriptors.json contains per-seed distributions (min,median,p95,max,mean), binding-count histograms0..12, normalized spread, and descriptor-array hashes. future_seed_table.csv combines per-seed future events and descriptors. associations.json gives the predeclared event/no-event group ranges of per-seed descriptor medians and maxima, with strict-separation tests; these are descriptive only.

Original/instrumented outputs NPZs contain101 flattened output/state/RNG leaves for the first seed; compare dtype, shape and bytes. Arrays use allow_pickle=False; huge RNG integer fields are decimal strings, not lossy floats or object arrays.
