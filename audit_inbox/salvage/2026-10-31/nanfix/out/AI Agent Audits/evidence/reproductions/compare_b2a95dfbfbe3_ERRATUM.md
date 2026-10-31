# Erratum: NaN-mask check missing from the CSV path of `compare_b2a95dfbfbe3.py`

Date: 2026-10-28. Applies to `compare_b2a95dfbfbe3.py` (sha256 `66ee634b…2994f`, pinned in `evidence/audit_manifest.json`). The original script and its log are left unchanged. The fix is a separate file, `compare_b2a95dfbfbe3_v2.py`.

## The gap

The seed-file and branch-diagnostics comparisons go through `cmp_arrays` (line 52). It reports `NaN pattern differs` as a problem before it takes the max abs diff over the non-NaN entries. The scalar-summary CSV path (line 79) only computed

    float((cz[num] - cr[num]).abs().max().max())

pandas `max()` skips NaN. So a cell that is NaN in one run and finite in the other gives a NaN difference, and that difference was silently dropped. The CSV could have passed with mismatched NaN patterns. The reproduction note's sentence "NaN patterns are identical" was therefore only checked for the NPZ files, not for the CSV. The gap matters here because the CSV has 348 NaN cells, spread over 5 of its 44 numeric columns (`Corr_Rpast_Plate`, `Time_to_90pct_continue_final_density`, `Time_to_90pct_continue_late_similarity`, `Time_to_similarity_below_0_9`, `Time_to_similarity_below_0_5`).

## The fix (v2)

`compare_b2a95dfbfbe3_v2.py` is identical to the original apart from the CSV block (see `compare_b2a95dfbfbe3_v1_to_v2.diff`). It:

- converts the numeric columns to float arrays;
- records `csv_nan_mask_mismatches`, the number of cells where exactly one run is NaN;
- adds a `scalar summary CSV: NaN pattern differs in N cells` problem when that count is non-zero, so the verdict becomes NOT REPRODUCED (the same handling as `cmp_arrays`);
- takes `csv_worst_abs_diff` only over cells that are non-NaN in both runs.

## Re-run result

The re-run was on 2026-10-28, from a fresh clone of `main` at `853498f`, with numpy 2.5.4, pandas 3.0.6 and python 3.13.5. The zip sha256 matches the note (`281bf33b…8d17ad`). The full log is `compare_b2a95dfbfbe3_v2.log`.

- `csv_nan_mask_mismatches`: **0**. Both runs have 348 NaN cells in the same positions, and neither has any inf.
- `csv_worst_abs_diff`: 6.661338147750939e-16 (unchanged)
- seed worst 6.66e-16 and branch-diagnostics worst 5.55e-16 (unchanged); `problems: []`; **verdict REPRODUCED**, exit 0.
- The v2 JSON output is identical to the original's apart from the added `csv_nan_mask_mismatches` key.

**The original verdict stands.** The NaN masks match, so the gap did not affect the result. The statement "NaN patterns are identical" now also holds for the CSV.
