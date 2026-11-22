Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-22T03:01:39.733080-07:00 (host-reported MST; not authenticated)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (copy)  
Scope: Gate spillover lane, DIRECTION-2; full 40-seed reference cohort  
Status: UNVERIFIED by project seats

# Cycle003 handoff — request lane-closure review

All 40 manifest seeds completed, with the original four included once and checked against Cycle002. Main result: **future events remain exactly 1/40**, seed4619122171158768524. The other 39 have no d/l event above1e-9. Both effects occurred during burn-in in all 40. Predeclared median/maximum descriptor ranges overlap; no causal explanation is claimed.

Please start with REPORT.md and evidence/per_seed_windows.csv (280 rows), then future_seed_table.csv, no_instrumentation.json, pilot_check.json, validation.json, and raw_array_hashes.json. Full40 and pilot4 pools are separate in pooled_summary.json. Exact controls and b/e split are retained.

## Resource disclosure requested by owner
RESOURCE_LIMITS.md records the ~128MiB/10,000-file best-effort persistence cap, nondurable cache, observed ~2GiB RAM, and an actual long-command transport failure. This cycle uses your permitted raw-hash fallback:240 full observation-array hashes plus per-seed summaries; compact future-step vectors are delivered for all 40. No raw40 archive is promised to survive in cache.

The first foreground job failed at logging with BrokenPipeError, after 26 durable seed records. Failure evidence is retained. Recovery revalidated raw hashes, recomputed summaries, reran first-seed equivalence and finished the remaining 14 in order with direct background logging. Pools were rebuilt rather than appended twice. No scientific rule changed. EXECUTION_INCIDENT.md explains details, including unavailable intermediate state-stream digests for recovered seeds 2–26 (raw hashes are present).

All actual log files use .log.txt. Clock chronology remains owner-upload-commit based, as you directed. Any copied historical filename ending .log appears only inside text, not as a delivered log path.

I submit this as **UNVERIFIED by project seats** and request the independent check and lane-closure decision. I have not started gate redesign, a cumulative-impact study, a Lean bridge, registry replication, a self-test census, or a residual/step-size experiment. A cause/cumulative-impact investigation would require a separately assigned lane; it is not appended here.
