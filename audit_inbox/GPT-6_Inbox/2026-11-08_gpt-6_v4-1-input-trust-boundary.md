# AIEFS Analysis v4.1 — Input Trust-Boundary Review

- **Agent / model:** GPT-6
- **Date:** 2026-11-08 (Europe/Tirane, UTC+01:00)
- **Repository / branch reviewed:** `main` @ `eb3933c196ee19e80e1621ae80d89ca72e6d9485`
- **Scope:** Static review of Analysis v4.1 candidate input discovery and validation, the committed S01 run manifest and repository inventory anchor, synthetic tests, and CI coverage. Focus: whether an input cohort is authenticated independently before it is analysed.
- **Status:** **UNVERIFIED INPUT** — an outside-review lead for independent triage, not a confirmed defect or a project verdict.

## Executive summary

The v4.1 candidate has a material input-provenance gap: its run validator checks data-file hashes against values in the same supplied manifest, but does not independently authenticate that manifest or bind the supplied run to the committed S01 authority. It also accepts a baseline certificate after checking only its `status` and `n_seeds` fields, once the certificate's file hash matches the supplied manifest.

This is a **static control-flow finding**, not a reproduced false-acceptance test. I did not construct a forged cohort or execute `validate_run`; I do not claim that the committed `runs/b57562a8ee77` data are false, tampered, or invalid.

There is an important existing safeguard: the v4.1 module identifies itself as an unaudited candidate, warns not to run on real trajectories, and its CLI refuses by default unless `--allow-unaudited-candidate` is provided. The candidate must remain non-authoritative until the input-authentication gap is closed and tested.

## P1 — Input hashes are self-consistent, but not independently anchored

### Evidence

1. In `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py` (blob SHA `df78b01607e6792afe9afc09fcc9b0cb83585ec6`):
   - `_require_hash` reads the expected digest from `manifest["output_hashes"]` and compares the supplied file with that digest (`main:283–291`).
   - `validate_run` accepts the supplied manifest when it declares `freezeable: true`, `completion.status: completed`, and `baseline_equivalence.status: passed`; it then checks the scalar CSV, branch NPZ, condition-status CSV, and baseline-certificate file against the digests in that same manifest (`main:293–319`).
   - The certificate itself is accepted when `status == "passed"` and `n_seeds == 40` (`main:320–325`). The validator does not check the certificate's frozen-source hashes, frozen artifact hashes, 40/40 per-seed result set, or authority identity against an independently trusted expected value.
   - The remaining design checks verify expected row/condition coverage, finite outcomes, ranges, and `T_window` arithmetic; they are useful schema checks, but do not authenticate the origin of the numerical values (`main:327–420`).
   - The CLI accepts a caller-supplied `run_dir`; `run_analysis` passes that directory directly through `discover_inputs` to `validate_run` (`main:1488–1499`, `1619–1659`). The acknowledgement flag is a safeguard, not an authority check.

2. There is an independent repository anchor available for the actual S01 run:
   - `registry/artifacts_current.csv:2474` (blob SHA `31be448f5343ce434587e5eaf3d7a397cd3af961`) records the committed `runs/b57562a8ee77/manifest.json` as artifact `ART-2217` with SHA-256 `7d1b86ab39eed397e2d281faf729ee5c3ac515efc00b2789c2e0013dce0d1e78`.
   - The committed manifest itself (blob SHA `7ae179db4eda4f6eef8a503567adf8324d94e336`) records the baseline gate's frozen input/source hashes and its 40/40 pass record (`runs/b57562a8ee77/manifest.json:1–45)); it also records the expected hashes for the baseline certificate, branch NPZ, condition-status CSV, and scalar CSV (`runs/b57562a8ee77/manifest.json:119–127`).
   - The v4.1 `validate_run` code does not compare the supplied manifest's bytes with the independently recorded `ART-2217` digest, nor does it compare its claimed run identity or baseline lineage with the committed S01 authority.

### Why this matters

A manifest and its output files can be internally consistent without being genuine production outputs. On the inspected code path, someone preparing a different input directory can provide matching files and a newly authored manifest whose own hash declarations agree with those files, while asserting the required completion and baseline status fields. The validator then has no external provenance comparison at which to distinguish that directory from the committed S01 cohort.

This establishes a **structural acceptance risk**. It does not yet establish that a particular fabricated directory actually passes every check: that requires a negative-control execution, which was not performed in this review.

### Recommended independent test

Run this only in an isolated temporary directory, not in the repository worktree and not from `audit_inbox/salvage/`.

- **Negative control:** construct a fabricated 40-seed × 5-rho × 4-branch cohort with 800 structurally valid scalar rows, 200 successful condition rows, appropriately shaped NPZ arrays, a certificate containing only asserted `status: passed` and `n_seeds: 40`, and a manifest whose local `output_hashes` match every supplied file. Give it the expected high-level schema and run the production `validate_run` entry point. Under an S01-only authority policy, it must be rejected because it is not bound to the independently pinned S01 manifest and baseline lineage.
- **Certificate-only mutation:** alter a certificate in a temporary copy, recompute its local manifest digest, and confirm the independent authority check still rejects it.
- **Positive control:** the genuine committed S01 inputs should pass the same independent authority check.
- Preserve the complete command, exit status, generated test fixture description, and observed validation result. Do not treat a hand-constructed unit test of a helper as a substitute for invoking the production validator.

### Recommended fix boundary

For the S01-only v4.1 candidate, require the exact trusted manifest hash (currently recorded by `ART-2217`) before trusting any of its child `output_hashes`; then verify the complete expected input set and baseline certificate against the trusted manifest and frozen authority values. If v4.1 is meant to analyse future runs as well, define a separate authenticated-run profile whose trust anchor is issued by the run/authority workflow—not a manifest that authenticates itself.

Add positive and negative tests for `validate_run` and make the negative controls part of CI. Keep the candidate flag and unaudited warning until a separate audit and a real S01 v4.1 run are complete.

## Positive observations and scope limits

- The held-event logic change is narrowly scoped: the new end check subtracts a tolerance of (10^{-6}) times the smallest positive saved-grid spacing, and the code separates retention and recovery classifications. The inspected logic is consistent with the intended saved-grid event definitions; this is not a proof of all scientific or numerical properties.
- `tests/test_v4_1_held_event.py` (blob SHA `4dc1aa1df6de39398a9e98f2fbf7c853957d9987`) is explicitly synthetic-only (`main:1–7`). It exercises exact-duration acceptance, one-step-short rejection, non-grid durations, retention/recovery cases, and synthetic-cohort row counts (`main:38–176`).
- `.github/workflows/repo-checks.yml` (blob SHA `f8c96af3de08be9acb0c627a673bb998dab99dd0`) explicitly runs this synthetic v4.1 test file in CI (`main:183–190`). That is good coverage for the held-event correction, but it does not test input provenance or production S01 validation.
- The former metadata wording mismatch about the tolerance appears corrected in the current candidate source and is not repeated here as an active finding.
- No source code, registry, frozen file, production data, simulation, or `main` branch content was changed. No tests, workflow jobs, forged-input fixture, real S01 v4.1 run, or independent artifact verification were executed during this review.

## Suggested triage disposition

Please independently reproduce or refute P1 with the negative and positive controls above. Until then, retain it as an unverified input-authentication risk. Do not certify v4.1, cite its outputs, register them, or use the candidate to replace the v3/v4 analysis on the strength of its synthetic held-event tests alone.
