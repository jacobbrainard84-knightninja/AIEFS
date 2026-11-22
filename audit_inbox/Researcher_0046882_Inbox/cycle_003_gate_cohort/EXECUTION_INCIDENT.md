Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-22T03:01:39.733080-07:00 (host-reported MST; not authenticated)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (copy)  
Scope: Gate spillover lane, DIRECTION-2; full 40-seed reference cohort  
Status: UNVERIFIED by project seats

# Execution-only recovery; no protocol/estimand amendment

PROTOCOL.md remains byte-identical to its pre-run hash. All 40 seeds, windows, thresholds, epsilon, definitions and descriptor rules remain unchanged.

Attempt1 used `python -u code/run_cohort.py 2>&1 | tee evidence/run.log.txt` with OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, PYTHONDONTWRITEBYTECODE=1. The tool transport returned shell_error around479 seconds. A process check showed the child still alive, so it was not duplicated or restarted blindly. A monitor waited for that existing PID to exit. Its durable failure record reports BrokenPipeError on the per-seed progress print. The log stopped before all durable work was recorded: 26 completed seeds were present in the JSON checkpoints, though the pipe-delivered log did not list all of them.

Preserved records: attempt1.log.txt, attempt1_failure.json, attempt1_environment.json, attempt1_per_seed_summary.json, attempt1_raw_array_hashes.json, attempt1_future_descriptors.json. The first-attempt log is incomplete by construction; it is not presented as a complete trace.

Recovery uses code/resume_cohort.py (derived execution-only variant, not a new scientific protocol). It reruns the exact controls and first original/instrumented seed comparison. It reuses seeds 2–26 only after checking every cached raw array against its durable dtype/shape/hash record and checks recomputed window summaries against the saved values. It runs seeds 27–40 in manifest order with identical settings, in a background process whose output is redirected directly to recovery.log.txt. Pools are rebuilt in a new scratch directory from all 40 checked observations, eliminating append duplication. Final tables contain each seed once.

State/return stream digests for seeds 2–26 were not durably checkpointed by attempt1 and are explicitly labeled unavailable in the recovery trace file; raw-array hashes are retained and checked. The required full noninterference comparison is rerun on seed 1. No missing trace digest is fabricated.

For a fresh reproduction, run code/run_cohort.py once from a terminal/job manager with direct log-file redirection; do not run the recovery script, which requires the original scratch cache. Failure evidence remains in the submitted package even after successful recovery.
