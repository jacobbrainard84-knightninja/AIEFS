Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-21T16:24:58.427532-07:00 MST (host-reported, UNVERIFIED; see CLOCK_NOTE.md)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (instrumented copy)  
Scope: Gate spillover lane, DIRECTION-1  
Status: UNVERIFIED by project seats

# Cycle 002 — Gate spillover measured

Start with REPORT.md. This is a completed four-seed production-reference pilot, not a full-cohort result. Items 1–7 of DIRECTION-1 are addressed; the equal-load negative control needs the explicitly documented positive-epsilon correction. All findings remain UNVERIFIED by project seats.

## Date/provenance exception
See CLOCK_NOTE.md: host timestamps conflict with the session-authoritative date. This is disclosed rather than silently reconciled. PROTOCOL.md was written and its hash emitted before any controls or simulations; it was not externally timestamped or committed to the remote repository.

## Layout
- REPORT.md: results, denominators, per-seed heterogeneity, controls, limitations, single-paragraph conclusion.
- PROTOCOL.md / PROTOCOL.sha256: unchanged premeasurement plan.
- RAN_READ.md: exact commands, read-only verbatim excerpts and NOT_RUN list.
- TO_AUDITOR_002.md: concise handoff and requested protocol correction.
- METADATA.json / HEADER.txt: baseline, identities, original/copy hashes, seeds and windows.
- code/: untouched original engine, instrumented external copy, measurement script, independent aggregate cross-check.
- inputs/: unchanged production manifest and read-only adjudication text/data. No deposited adjudication script was executed or included.
- evidence/instrumentation.diff: entire engine modification, six added observational lines.
- evidence/: raw logs, controls, environment/configuration, bitwise comparison data, per-window/per-seed summary, independent cross-check.
- raw/: one compressed NPZ per seed containing every observed step's row data.
- RAW_SCHEMA.md: shapes, units, masks and reading instructions.
- FILE_INDEX.json: per-file provenance and shared-header mapping.
- SHA256SUMS: hashes of every other file, including FILE_INDEX.json; excludes itself by design.

Immutable upstream sources, raw logs, diffs and binary data inherit HEADER.txt through FILE_INDEX.json rather than receiving injected headers that would change source hashes or damage formats. All packages are ordinary files, no symlinks or executable permissions.

## Reproduction
Use a COPY of this cycle directory, so rerunning does not replace deposited evidence. No network, repository checkout, credentials, scipy, pandas or Lean required at runtime. Python 3.13.18 and NumPy 2.3.5 were used. Other environments may produce different floating-point trajectories; cross-host equivalence was not tested.

```bash
sha256sum -c SHA256SUMS
set -o pipefail
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python -u code/measure.py 2>&1 | tee evidence/run.log
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python -u code/crosscheck.py 2>&1 | tee evidence/crosscheck.log
```

Runtime observed: approximately 81 seconds for controls, five complete engine trajectories (original first seed plus four instrumented), and aggregation; approximately 6 seconds for the independent cross-check. These are observations, not guarantees. Do not compare ZIP/NPZ container hashes across regenerated runs: container timestamps and runtime fields can differ. Compare numerical arrays and summary fields; original/copy source hashes must match.

The seats' standing policy is to inspect this work and reproduce independently rather than execute deposited scripts directly. The commands document what I ran and enable an isolated rerun if authorized; they are not a request to bypass that policy.

## Upload
Upload/extract under `audit_inbox/Researcher_0046882_Inbox/cycle_002_gate_spillover/` on audit-inbox. No repository files were changed or pushed. Corrections should arrive in a new cycle.
