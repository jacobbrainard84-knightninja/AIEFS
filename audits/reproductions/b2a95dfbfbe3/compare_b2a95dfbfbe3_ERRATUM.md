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

## Follow-up (v4, 2026-10-31): gate the fields v3 computed but ignored

Raised by the red-team negative-control suite (`tools/redteam`, gaps G10 and G11; red-team fix #1, branch
`fix/comparator-v4-gates`). v3 computed several fields but did not let them change the verdict. A rerun whose CSV
`branch` labels were swapped (G10), or whose manifest `schema` was changed (G11), still came out REPRODUCED. A missing or
corrupt official file crashed v3 with a traceback (exit 1, but no verdict). v1 (pinned), v2 and v3 are kept unchanged.

`compare_b2a95dfbfbe3_v4.py` (see `compare_b2a95dfbfbe3_v3_to_v4.diff`) prints everything v3 prints (the v3 keys and
values are identical on the genuine data) and adds these gates. Each failed gate adds a named entry to `problems`:

- the scalar-summary CSV's non-numeric columns (`branch`, `branch_family`) must be equal cell for cell (G10);
- manifest `model`, `protocol`, `randomization` and `schema` must be equal (G11), and only `config_hash`,
  `environment` and `source_sha256` may differ (an added, removed or other changed key is a problem);
- each run's `config_hash` must be its run id (`b2a95dfbfbe3` for the rerun, `5a9f093a2fe0` for the official run), and
  each manifest's `source_sha256` must be the sha256 of the source file that run used;
- the source diff must be exactly the documented one-line rewrite (`R_physical, _, _ =` to `R_physical, *_ =`);
- the seed `config_hash` labels must be exactly (rerun id, official id) in every seed file;
- the seed file names must match one to one; a missing or unreadable file (seed, CSV or branch diagnostics) is a named
  problem and a NOT REPRODUCED verdict, not a crash;
- floats: worst abs diff <= `TOL` = 1e-12 (as before) **and** worst relative diff <= `RTOL` = 1e-12. Relative diff is
  `|x-y| / max(|x|,|y|)` over cells finite in both runs. It applies in addition to the absolute check, so it can only
  tighten. It closes a v3 hole: a CSV cell that is exactly 0 in one run and 1e-14 in the other passed v3's absolute
  check. Conversely, the CSV reaches |x| = 1.8e19, so at that scale the absolute check already demands bit-identical
  values.

Not gated, on purpose: `zip_stub_model_matches_official`. It compares a stub inside the zip
(`runs/5a9f093a2fe0/manifest.json`) that `b2a95dfbfbe3_REPRODUCTION.md` documents as carrying the wrong parameters, not
the rerun, and it is `false` on the genuine data. Gating it would fail the genuine reproduction for a known, documented
reason, so it stays informational.

Re-run (`compare_b2a95dfbfbe3_v4.log`, numpy 2.5.4, pandas 3.0.6, python 3.13.5, at `395ea53` plus the red-team suite):
every gate passes. Differing manifest keys are exactly `config_hash`, `environment`, `source_sha256`, the labels are
`[b2a95dfbfbe3, 5a9f093a2fe0]`, both `source_sha256` values match their files, and the CSV non-numeric columns are equal.
Worst abs diff is 6.66e-16 (CSV), 6.66e-16 (seed) and 5.55e-16 (branch diagnostics). Worst relative diff is 1.15e-15,
8.47e-16 and 6.79e-16. `problems: []`; **verdict REPRODUCED**, exit 0. **The original verdict stands.**

`compare_b2a95dfbfbe3_v3.log` was regenerated on 2026-10-31. Its old SHA256SUMS line (`fcf370da…52b6`) pointed to a file
that was never committed. The repo's `.gitignore` has `*.log`, so a plain `git add` skipped it, while `v2.log` had been
force-added. `sha256sum -c SHA256SUMS` therefore failed on every clone. The regenerated log was made by running v3 unchanged
at the commit stated in its header. Its JSON matches the numbers reported in the v3 section above. Both logs are now
force-added (`git add -f`), and SHA256SUMS is updated in the same commit. Errata entry: `ERRATA_2026-10-28.md` E14.
