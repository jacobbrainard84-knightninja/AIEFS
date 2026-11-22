Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-22T03:01:39.733080-07:00 (host-reported MST; not authenticated)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (copy)  
Scope: Gate spillover lane, DIRECTION-2; full 40-seed reference cohort  
Status: UNVERIFIED by project seats

# AIEFS Gate Cohort — Cycle003

Researcher0046882, DIRECTION-2. All 40 frozen-manifest seeds, 3.2million reference updates. UNVERIFIED by project seats.

## Start here
1. TO_AUDITOR_002.md — handoff and resource disclosure.
2. REPORT.md — results, complete40-seed future table, limitations, one-paragraph answer.
3. evidence/per_seed_windows.csv — all 280 seed/window rows; future_seed_table.csv — descriptor table.
4. PROTOCOL.md / PROTOCOL.sha256 — unchanged premeasurement plan.
5. RESOURCE_LIMITS.md / EXECUTION_INCIDENT.md — storage limits, interrupted first attempt and explicit recovery.

## Package contents
- code/engine_original.py: hash-pinned baseline bytes; external copy, not a repository edit.
- code/engine_instrumented.py + evidence/instrumentation.diff: same six-line copied-array hook as accepted Cycle002.
- code/common.py: measurement helpers derived from Cycle002, no simulator main.
- code/run_cohort.py: fresh full40 reproduction driver.
- code/resume_cohort.py: actual execution-only recovery driver; requires first-attempt cache and is NOT the fresh reproduction entrypoint.
- code/validate_saved.py: independent consistency checker (no simulation).
- inputs/: unchanged frozen production manifest, pilot reference hashes and summary.
- evidence/: controls, both-attempt logs/failure/checkpoints, exact equivalence artifacts, completed tables, raw-array hashes and validation.
- descriptors/: all 40 compact future-step NPZs; raw full-row matrices omitted under authorized size fallback.
- HEADER.txt / METADATA.json / FILE_INDEX.json: provenance and shared per-file metadata.
- SHA256SUMS: every delivered file except its own self-entry.

The status/date/baseline header applies through FILE_INDEX.json to immutable upstream sources, CSVs, logs and binary arrays without altering those formats. The owner's upload commit dates the deposit. Host clocks are not authenticated; the session/host discrepancy is preserved in METADATA.json.

## Reproduce in a new copy of the package
Do not overwrite the submitted evidence. Python3.13.18 and NumPy2.3.5 were used. No other Python dependencies, network, credentials, repository clone or Lean installation needed. Seats should inspect/rederive independently under their normal intake policy, not bypass it by blindly executing these scripts.

```bash
sha256sum -c SHA256SUMS
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python -u code/run_cohort.py > evidence/fresh_run.log.txt 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python -u code/validate_saved.py > evidence/fresh_validation.log.txt 2>&1
```

Use a terminal or long-running job manager, not a short-lived streamed tool call with tee. In Arena, use start_process and blocking waits. Default scratch parent is ~/.cache/r0046882; `--scratch /your/scratch` selects another parent. Several GiB of temporary disk and roughly 2 GiB available RAM are recommended. Check completion.json says COMPLETE_40 before using the result. Failed runs retain FAILURE.json; investigate rather than silently reuse stale completion files. Fresh reproduction from this package is intended in a new copy; the driver overwrites result files.

For fresh-run validation, the validator follows completion.json's scratch_path. Check raw-array bytes against hashes in the ORIGINAL submitted package, not merely newly generated hashes. Likewise compare numerical summary fields with the submitted reference. NPZ container hashes and elapsed timestamps are not expected to reproduce byte-for-byte; exact array hashes are. Cross-host differences must be reported, not hidden by loosening tolerances.

## Upload and closure
Extract under audit_inbox/Researcher_0046882_Inbox/cycle_003_gate_cohort/. All logs end .log.txt. No protected repository file was edited; the owner handles upload. Corrections go into a new cycle. Completion of the measurement does not itself authorize a DONE label or new lane.
