# Part 6 — Genuine S01 artifact retrieval and positive-control feasibility

**Agent:** GPT-6  
**Date:** 2026-11-09 (Europe/Tirane)  
**Main reviewed:** `eb3933c196ee19e80e1621ae80d89ca72e6d9485`  
**Audit-inbox tip before deposit:** `4fbd00b6e5f975b49bd74885e8c381af9abaf9f7`  
**Scope:** Retrieve the genuine S01 bundle, re-hash accessible inputs, and determine whether the original v4.1 validator can be run without synthetic substitutes.

## Finding

**The genuine S01 positive control could not be completed in this execution environment.** The manifest and two supporting text inputs were retrieved and independently SHA-256 checked against the main-branch inventory. The 27,992,867-byte branch NPZ and 4,348,855-byte baseline certificate could not be retrieved as bytes. The 4,215,297-byte baseline seed-results JSON was also returned with an empty body. No synthetic artifact was substituted.

This is a connector/runtime retrieval limitation, not evidence that the Git objects are absent or corrupt. The main inventory contains entries for all these files, and the connector returned Git blob identifiers for the inaccessible objects.

## Independently verified text inputs

At main commit `eb3933c196ee19e80e1621ae80d89ca72e6d9485`:

- `runs/b57562a8ee77/manifest.json`: Git blob `7ae179db4eda4f6eef8a503567adf8324d94e336`; 11,457 bytes; recomputed SHA-256 `7d1b86ab39eed397e2d281faf729ee5c3ac515efc00b2789c2e0013dce0d1e78`, matching ART-2217 at `registry/artifacts_current.csv:2474`.
- Scalar CSV: Git blob `f64b776ecf80fe1e63e8a64f93987e98ad972485`; 603,831 bytes; recomputed SHA-256 `e9aa74e68b758b21e64b5757607af3c4bf98e88f616757319cb9e4e6d3a8e378`, matching ART-1996 at `registry/artifacts_current.csv:2253`. Parsed 800 rows: 40 seeds, five rho values, four executed branches with 200 rows each.
- Condition-status CSV: Git blob `62ffacd3581d728c1f2f9ad74a8fc3ac2c9f58cb`; 10,272 bytes; recomputed SHA-256 `1f6985026c292c15b5fa5cacacbe92600916ab8d43bdbc8df4f9f0a76baa98e8`, matching ART-2218 at `registry/artifacts_current.csv:2475`. Parsed 200 rows: 40 seeds, five rho values, all statuses success.

The manifest's output-hash block is at lines 119–124 and paired-seed array begins at line 158. Inventory blob: `31be448f5343ce434587e5af3d7a397cd3af961`.

## Unavailable inputs

Inventory `registry/artifacts_current.csv`, blob `31be448f5343ce434587e5af3d7a397cd3af961`:

| Input | Inventory row | Size | Expected SHA-256 |
|---|---:|---:|---|
| Branch diagnostics NPZ | ART-1995, line 2252 | 27,992,867 bytes | `55a419c790d0a46bad2a52488d9de018a539ad3daa3759eee849cebf4df468c2` |
| Baseline seed results JSON | ART-2015, line 2272 | 4,215,297 bytes | `47b1627a20be52ee4cf3ad69feeae3fe8d8e008687912c83c2237dfa8e5363ff` |
| Baseline certificate JSON | ART-2016, line 2273 | 4,348,855 bytes | `08314de365196fa369bfa2b0363352cf04bdfb1a957f3ed86847f5d17b9d620f` |

For the NPZ, ordinary and base64 fetch-file calls returned empty bodies; fetch-blob failed UTF-8 decoding; the text-only API fetch rejected the binary response. The two large JSON files also returned empty bodies, including line-range attempts. Direct curl to raw.githubusercontent.com failed DNS resolution. The successful main Repo checks run `42515853741` had no uploaded workflow artifacts.

## Why original validation is blocked

v4.1 source: `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py`, blob `df78b01607e6792afe9afc09fcc9b0cb83585ec6`. `validate_run()` requires the manifest, condition-status CSV, baseline certificate, scalar CSV and branch NPZ (lines 295–303); checks four child hashes from the supplied manifest (326–329); and parses the certificate, requiring passed status and 40 seeds (331–334). Without the NPZ and certificate bytes, the original function cannot be run against genuine S01. `run_analysis()`, CLI and bundle writing were not run.

This is a retrieval blocker only, not a false-PASS finding. The manifest's `freezeable=true` is not interpreted as `oracle_certified`.

## Preflight helper and next step

The read-only helper hard-pins the manifest and five child SHA-256 values; rejects symlinked inputs; checks cohort coverage and CSV counts; parses both JSON outputs; and reads all NPZ arrays with `allow_pickle=False`. It explicitly does not run the original validator, analysis, CLI or oracle certification. Compilation passed. A missing-bundle negative control exited 1 and listed all six missing files. The helper was not run against genuine S01 because those inputs were not staged locally.

Have the owner or Researcher 001 make the existing full S01 bundle available to the isolated audit/CI environment as a read-only artifact. Do not add binary copies to the inbox. Once staged, run the preflight, independently verify every byte hash, then run original v4.1 `validate_run()` and `run_analysis()` separately while preserving the `--allow-unaudited-candidate` guard. Keep v3 and v4.1 analyses distinct.

**Disposition:** deposited as **UNVERIFIED INPUT for triage**. No main, source, registry, briefing, TRIAGE or existing inbox file was modified.
