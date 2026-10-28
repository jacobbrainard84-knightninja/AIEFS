# Project Histories

This folder holds the project's history: the project lead's conversation records (`Project Lead History 01.pdf` … `10.pdf`), `SSRH 000244 Stuff.odt`, and three zip files. Each zip is a raw copy of an AI agent's working folder ("workspace") from July to August 2026.

## Read this before opening a zip

**Never unzip these files at the top level of the repository.** Always unzip into a separate scratch folder outside the repository, for example:

```
mkdir -p ~/scratch/019ff425 && unzip "Project Histories/workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2.zip" -d ~/scratch/019ff425
```

The zips are records of the agents' work, not finished results. Some files inside have the **same names as real repository files but different contents**. If you unzip at the top level, they can silently overwrite the real files.

### Known fake stand-ins in `workspace-019ff425-…zip`

| File inside the zip | Why it is not the real thing |
|---|---|
| `runs/5a9f093a2fe0/manifest.json` (and the small CSV and npz next to it) | A stand-in with the **wrong parameters** (N = 12, dt = 0.01, T_window = 1.0, eta = 0.1, mu = 0.01, gamma = 0.5, capacity = 100, B_c = 1.0). The real official run is the repository's own `runs/5a9f093a2fe0/`. |
| `AIEF_1_4_memory_ablation_updated.py` | An **exact copy of the stub** `AIEF_1_4_memory_ablation_updated_07.py`, not the real driver. Its docstring wrongly claims to be the production module for run 5a9f093a2fe0. |

## The zips

| Zip | Size | sha256 | What it is |
|---|---|---|---|
| `workspace-019fb8fc-d3d9-784a-82a5-03d4ec3f136c.zip` | 11.7 MB, 40 files | `037d984e3389ca2d497cf7f3caa9128cfa4379ad8c5672bd1597ccdfaffb311f` | The workspace behind Origin Document 01: alignment and phase-cancellation scripts, the two-channel alignment versions v2 to v5, tests and output folders. **The output folders come from made-up (synthetic) data with the wrong parameters, so they are not evidence**, even where they say "PASSED" or "VERIFIED". The tests pass, but they only check algebra and plumbing. |
| `workspace-019fc7dc-79cb-7fdd-bdd1-95786b152434.zip` | 0.3 MB, 15 files | `2e38e50bb137d81ab5e7c4f56a7639be6a18c0ebe6a412e1e10c06ea7f204bf3` | Scripts behind Origin Document 02. 14 of the 15 are exact copies of scripts already in the repository. The only new one is `aief_1_4_matched_phase_memory.py`, an early version of `AIEF_1_4_matched_phase_memory_ablation.py`. |
| `workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2.zip` | 19.7 MB, 166 files | `281bf33be105cb6219af7aecb9f8ae547459856c1548fdf646f5caee9f8d17ad` | The modular "experiment engine" workspace (6 to 10 August 2026). **Useful:** `runs/frozen_production_20260806/b2a95dfbfbe3/` is an independent re-run of the official 40-seed experiment, and it matches `runs/5a9f093a2fe0` on all 40 seeds to within rounding (see `AI Agent Audits/evidence/reproductions/b2a95dfbfbe3_REPRODUCTION.md`). Also included: a baseline-equivalence test (`baseline_test_20260809/runs/4355cf6d515a/`, 40/40 seeds passed). **Not evidence:** `final_output/` (a 2-seed partial test run) and about 70 "FINAL", "COMPLETE" and "PRODUCTION READY" notes, which are agent progress notes rather than results. **Contains the fake stand-ins listed above.** |

The sizes and sha256 values above were checked on 2026-10-28, against repository commit `6b49a7b`.
