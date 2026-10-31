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

## Follow-up (v3, 2026-10-29): +inf / -inf masks and a local SHA256SUMS

Raised by an outside review (Researcher 026, Review 2 section 1). v2 checked NaN masks but not infinity masks. On the
NPZ path, `cmp_arrays` took `np.abs(x - y)` over the non-NaN cells, so a cell that is `+inf` in one run and finite in
the other gave an `inf` difference (caught by the tolerance, but reported as a number, not as a pattern mismatch), and
`+inf` in both runs gave `inf - inf = NaN`, which the max would have mishandled. On the CSV path only NaN was masked.

`compare_b2a95dfbfbe3_v3.py` (see `compare_b2a95dfbfbe3_v2_to_v3.diff`) changes only the comparison helpers:

- one helper, `mask_mismatches`, counts cells where exactly one run is NaN, `+inf` or `-inf` (complex arrays: real and
  imaginary parts separately); `cmp_arrays` (NPZ seed files and branch diagnostics) and the CSV block both use it;
- any mismatch is a problem, so the verdict becomes NOT REPRODUCED;
- max abs diffs are taken only over cells that are finite in both runs;
- new JSON keys: `csv_posinf_mask_mismatches`, `csv_neginf_mask_mismatches`, `csv_nonfinite_cells_rerun`,
  `csv_nonfinite_cells_official`;
- `--selftest` runs synthetic checks of the masks (no repo data needed).

Re-run (`compare_b2a95dfbfbe3_v3.log`, numpy 2.5.4, pandas 3.1.0, python 3.13.5): 0 NaN, 0 `+inf` and 0 `-inf`
mask mismatches; 348 NaN cells and 0 infinite cells in each run; CSV max abs diff 6.66e-16, seed 6.66e-16, branch
diagnostics 5.55e-16; `problems: []`; **verdict REPRODUCED**, exit 0. Apart from the new keys the JSON output is
identical to v2's. The sentence "neither has any inf" above is now checked by code, not only by inspection.

v1 (pinned) and v2 are kept unchanged. `SHA256SUMS` in this folder pins every other file in it; check it with
`cd audits/reproductions/b2a95dfbfbe3 && sha256sum -c SHA256SUMS`. Editing any file here means updating SHA256SUMS
in the same commit.
