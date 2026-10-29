# Erratum: NaN-mask check missing from the CSV path of `compare_b2a95dfbfbe3.py`

Date: 2026-10-28 (relocated and re-run 2026-10-29). Applies to
`AI Agent Audits/evidence/reproductions/compare_b2a95dfbfbe3.py` (sha256 `66ee634b…2994f`, pinned in
`AI Agent Audits/evidence/audit_manifest.json` `files_sha256`). The original script, its log
(`compare_b2a95dfbfbe3.log`) and the note `b2a95dfbfbe3_REPRODUCTION.md` are left unchanged. The fix is a
separate file, `compare_b2a95dfbfbe3_v2.py`, in this folder.

Why this folder: `AI Agent Audits/evidence/verify_manifest.py` (run in CI by `tools/ci/check_manifest.py`) fails on
any file under `AI Agent Audits/` that is not listed in `audit_manifest.json` (`UNLISTED`), and the manifest is not
re-pinned. So the v2 files live in `audits/reproductions/b2a95dfbfbe3/`, which no manifest, `registry/artifacts.csv`
row or `SHA256SUMS` file pins.

## The gap

The seed-file and branch-diagnostics comparisons go through `cmp_arrays` (line 52). It reports `NaN pattern differs`
as a problem before it takes the max abs diff over the non-NaN entries. The scalar-summary CSV path (line 79) only computed

    float((cz[num] - cr[num]).abs().max().max())

pandas `max()` skips NaN. So a cell that is NaN in one run and finite in the other gives a NaN difference, and that
difference was silently dropped. The CSV could have passed with mismatched NaN patterns. The reproduction note's sentence
"NaN patterns are identical" was therefore only checked for the NPZ files, not for the CSV. The gap matters here because
the CSV has 348 NaN cells, spread over 5 of its 44 numeric columns (`Corr_Rpast_Plate`,
`Time_to_90pct_continue_final_density`, `Time_to_90pct_continue_late_similarity`, `Time_to_similarity_below_0_9`,
`Time_to_similarity_below_0_5`).

## The fix (v2)

`compare_b2a95dfbfbe3_v2.py` is identical to the original apart from the CSV block and the docstring (run command and
log name updated for this folder, plus a pointer to this erratum); see `compare_b2a95dfbfbe3_v1_to_v2.diff`. It:

- converts the numeric columns to float arrays;
- records `csv_nan_mask_mismatches`, the number of cells where exactly one run is NaN;
- adds a `scalar summary CSV: NaN pattern differs in N cells` problem when that count is non-zero, so the verdict
  becomes NOT REPRODUCED (the same handling as `cmp_arrays`);
- takes `csv_worst_abs_diff` only over cells that are non-NaN in both runs.

The script still reads its inputs by repo-relative path (`Project Histories/workspace-019ff425-…zip`,
`runs/5a9f093a2fe0`, the two `AIEF_1_4_memory_ablation_updated.py` files), so it runs from the repo root as before.

## Re-run result

First run: 2026-10-28, from a fresh clone of `main` at `853498f`, numpy 2.5.4, pandas 3.0.6, python 3.13.5.
Second run (the committed `compare_b2a95dfbfbe3_v2.log`): 2026-10-29, from this folder on branch `audit/nanfix-v2`
(base `9d46d9b`), numpy 2.5.4, pandas 3.1.0, python 3.13.5. The JSON output of the two runs is identical. The zip
sha256 matches the note (`281bf33b…8d17ad`).

- `csv_nan_mask_mismatches`: **0**. Both runs have 348 NaN cells in the same positions, and neither has any inf.
- `csv_worst_abs_diff`: 6.661338147750939e-16 (unchanged)
- seed worst 6.66e-16 and branch-diagnostics worst 5.55e-16 (unchanged); `problems: []`; **verdict REPRODUCED**, exit 0.
- The v2 JSON output is identical to the original's apart from the added `csv_nan_mask_mismatches` key.

**The original verdict stands.** The NaN masks match, so the gap did not affect the result. The statement
"NaN patterns are identical" now also holds for the CSV. Ledger row: `AUD-REPRO-B2A95` in `registry/claims.csv`;
errata entry: `ERRATA_2026-10-28.md` E10.
