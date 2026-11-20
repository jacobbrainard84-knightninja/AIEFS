# Cleanup candidates (verified only, nothing deleted)

Verified Fri Oct 30, 2026 (7:20–7:38 PM EDT) on `integration/round5` `0e0c82e`. Hashes are sha256 over file bytes; zip members were read with Python `zipfile`.

| # | Candidate | Verification | Pinned? | Verdict |
|---|---|---|---|---|
| 1 | `Project Origins/Solar System Resonance Hypothesis Delay‑Coupled Dynamics draft 02.pdf` vs `… draft.pdf` (U+2011 hyphen in the name) | Both are sha256 `8f22db1bc59674f8783184d232d1cf2b8e6bac48dc7f0a857d506861dd84e383`, 290,652 bytes: **byte-identical**. | Both are snapshot rows: ART-0274 (draft 02) and ART-0275 (draft). | True duplicate. Keep `draft.pdf` and remove `draft 02.pdf`. The `.odt` siblings were not compared (out of scope). |
| 2 | `AIEF_Experiments/aief_modular_platform_v1_analysis_v4.zip` (85,074 bytes, sha256 `42b1e4f2…`) vs the extracted folder | All 39 file members match the folder byte for byte (39 same, 0 diff, 0 missing). The folder has 41 tracked files; the 2 extra were added after the zip. | Zip is ART-0061; its member rows are also in the snapshot. | True duplicate; the folder is a superset. |
| 3 | `workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f/` (29 tracked files) and `workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f.zip` (ART-2731, sha256 `78b7eca3…`) | All 29 zip members match the folder byte for byte. `CURRENT_STATUS.md:50` says the v4 platform supersedes this workspace. | Zip is ART-2731 and the folder files are rows too (e.g. ART-2732). | Zip and folder are duplicates of each other. The whole scratch workspace is superseded, so remove both together. |

The snapshot and the two zip archives hold 68 zip-member rows for items 2–3.

## What deleting them would require (separate branch after round5 merges; owner's call)

- `registry/artifacts.csv` stays byte-identical. The snapshot keeps listing the files, so `tools/ci/check_artifact_pins.py` would report them as missing. Add their ART ids, and for the zips the member rows, to its known-missing allowlist in the same commit.
- Regenerate `registry/artifacts_current.csv`.
- Text references that would go stale. None of these is a code dependency, so record the deletion in ERRATA or the ledger rather than editing pinned files.
  - **v4 zip:** named in `audits/engineering/verify_inventory.py` (ZIP_ARCHIVES, the pinned snapshot checker), `registry/relocation_map.csv`, `registry/supersessions.csv`, `PRIVACY_SCRUB_LIST.md` and audit reports.
  - **workspace-019ff86e:** 11 files, including `CURRENT_STATUS.md`, `python_path_dependencies.csv`, the licensing report script (text mention only), the v4 `PROJECT_INTEGRATION_MAP.md` and `verify_inventory.py`.
  - **PDF:** only the cmp command in `AI Agent Audits/evidence/tooling/adhoc_commands.md`, which is pinned in the audit manifest. Leave it unedited.
- **Not verified this round:** the `recovered_from_workspace_019ff402/` duplicates (newer_zip_markdown/, zip_updated_*.py).
- **Do not delete:** `runs/5a9f093a2fe0/` (read by the authority lock), `runs/b57562a8ee77/`, `test_output/`, `Project Histories/workspace-019ff425…zip`.
- Deleting files from the tip does not make the history smaller. Shrinking history means a history rewrite, which is the owner's decision.
