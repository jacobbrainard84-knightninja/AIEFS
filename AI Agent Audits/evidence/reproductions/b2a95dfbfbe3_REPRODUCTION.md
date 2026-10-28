# Reproduction record: run `b2a95dfbfbe3` reproduces official run `runs/5a9f093a2fe0`

Date: 2026-10-28. Checked against repository commit `6b49a7b`. Type: reproduction check (RAN).

## Summary

The zip `workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2.zip` in the `Project Histories` folder contains an independent re-run of the AIEF-1.4 memory-ablation production run, stored at `runs/frozen_production_20260806/b2a95dfbfbe3/` inside the zip. It reproduces the official run `runs/5a9f093a2fe0` on **all 40 seeds**. The largest absolute difference in any float value is **6.7e-16** (6.661338147750939e-16), which is floating-point rounding.

- Model, protocol, randomization and output schema in the two `manifest.json` files are identical.
- 40 of 40 seed files are present in both runs. 15,160 fields were compared (the per-seed `config_hash` label is excluded, see below). 1,255 fields differ, all by rounding only (max 6.7e-16). NaN patterns are identical. No seed file is byte-identical, because each one stores its own `config_hash`.
- Scalar summary CSV: 280 × 46 in both runs, with identical columns. The largest numeric difference is 6.7e-16 (in `Weight_gini`). The non-numeric columns are identical.
- Branch diagnostics: 3,320 fields in both runs, none missing. The largest difference is 5.6e-16.
- The only manifest keys that differ are `config_hash`, `environment` and `source_sha256`, which is expected. The config hash includes the source hash, so the run IDs differ.

## Zip

| | |
|---|---|
| Folder | `Project Histories` |
| File | `workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2.zip` |
| Size | 19,703,485 bytes |
| sha256 | `281bf33be105cb6219af7aecb9f8ae547459856c1548fdf646f5caee9f8d17ad` |
| Run inside zip | `runs/frozen_production_20260806/b2a95dfbfbe3/` (43 files: manifest, scalar summary CSV, branch diagnostics, 40 seed files) |

## Environments (numpy and python versions, from each run's `manifest.json`)

| Run | numpy | python |
|---|---|---|
| Re-run `b2a95dfbfbe3` (in zip) | 2.3.5 | 3.13.14 |
| Official `runs/5a9f093a2fe0` | 2.5.1 | 3.13.5 |
| This comparison | 2.5.4 (pandas 3.0.6) | 3.13.5 |

Platform strings are left out on purpose: the official run's platform string identifies the owner's device.

## Source difference

The two runs used different tracked copies of the driver:

| Run | `source_sha256` | Tracked file with that hash |
|---|---|---|
| Re-run `b2a95dfbfbe3` | `a94acae3f6b7cc2baef62c53eaaa07acac346ce073e18d8f566e22bef7d03549` | `AIEF_1_4_memory_ablation_updated.py` (repo root) |
| Official `5a9f093a2fe0` | `34d37908479f766c4036b35975b334935a5b5fb60c0c437d7649db8d14473257` | `Older files/AIEF_1_4_memory_ablation_updated.py` |

The line diff between the two files has 58 changed lines. 56 of them are comments or blank lines. The other 2 are one equivalent rewrite: `R_physical, _, _ = advance_state(` became `R_physical, *_ = advance_state(`. `advance_state` always returns exactly three values (`return R_physical, R_driver, info`), so the two forms behave the same. **Correction to the 6b49a7b review:** the review said "comments and whitespace only". The accurate wording is "comments and blank lines, plus one behaviour-preserving tuple-unpacking rewrite". The difference has no effect on any output, as the numbers above confirm.

## Warning: a fake stand-in in the same zip

The zip also contains files that have the same paths as real repository files but are **not** the official run or driver:

- `runs/5a9f093a2fe0/manifest.json` (plus a small `…_scalar_summary.csv` and `…_branch_diagnostics.npz` next to it). Its model block (N = 12, dt = 0.01, T_window = 1.0, eta = 0.1, …) has the wrong parameters and does not match the official run. The compare script reports `zip_stub_model_matches_official: false`.
- `AIEF_1_4_memory_ablation_updated.py` at the zip root (15,460 bytes, sha256 prefix `d556e8460cfe`). It is an exact copy of the stub `AIEF_1_4_memory_ablation_updated_07.py`, not the real driver.

**Never unzip this archive at the repository root.** It would overwrite the real `runs/5a9f093a2fe0/` files and the real driver with these stand-ins. The compare script reads the zip in memory and extracts nothing.

## Rerun

From the repository root (needs numpy and pandas):

```
python "AI Agent Audits/evidence/reproductions/compare_b2a95dfbfbe3.py"
```

The script exits 0 and prints `"verdict": "REPRODUCED"` when every float field agrees to 1e-12, every non-float field matches exactly (apart from the `config_hash` label), and all 40 seeds are present. Otherwise it exits 1. The full output from the run on 2026-10-28 is in `compare_b2a95dfbfbe3.log` in this folder.

## Files in this folder

- `b2a95dfbfbe3_REPRODUCTION.md`: this note
- `compare_b2a95dfbfbe3.py`: the exact compare script that was run
- `compare_b2a95dfbfbe3.log`: its output (command line, JSON summary, exit code)
