# Old-files drift audit: `Older files/` vs current counterparts (origin/main 395ea53)

Read-only. No branch was made and nothing was pushed. Written 2026-10-31 at about 12:05 EDT.
Full unified diffs for every pair are in `/workspace/review_r026/oldfiles/*.diff`. The extracted constant,
default and assert changes are in `oldfiles/consts_report.txt`, made by `oldfiles/consts.py`, an AST
extractor for UPPER_CASE module constants, argparse defaults, function defaults and asserts.

## Scope and method
- **Folder.** The only old-files folder on origin/main is **`Older files/`** (152 files: 31 `.py`, plus 3 data
  folders). I also checked these names, and none of them holds old code copies: archive, legacy, deprecated,
  backup, superseded, `_old`, `.bak`, `history/`, `Project Histories/` and `Project Origins/`. The last two hold
  only docs, PDFs and zips.
- **Pairing.** Each old `.py` was paired with the root file of the same stem, with numeric suffixes such as
  `_01`, `_07` and `_1` removed. Every old file has a current counterpart.
- **Flag criteria.** A change was flagged if it touched a constant, threshold, tolerance, seed, assert, verdict
  condition or pass/fail check. Each flagged change was then judged on direction (toward or away from the
  expected answer) and on whether it is documented.
- **Documentation.** origin/main has 185 commits, but `git log` on `Older files/` and on every flagged current
  file shows only the import commit `add81e6 "Add SSRH project"`, so no per-change commit messages exist. I checked documentation against these sources:
  - `ERRATA_2026-10-28.md`
  - `CURRENT_STATUS.md`
  - `registry/claims.csv`
  - `AI Agent Audits/**`
  - the reproduction notes

## Summary table

| # | Old → current | What changed | Direction | Documented? | Benign? |
|---|---|---|---|---|---|
| **F1** | `Older files/aief_1_4_augmented_spectrum.py` and `…_02.py` → `aief_1_4_augmented_spectrum.py` | Gap lower bound `r_ema` → `r_ema*1.01`. "Near-EMA" band ±10% → ±1%. SUPPORTED condition `n_near_ema == 1` → `>= 1`. Wording changed to "unique slow pole". | **Toward expected answer.** Under `_02`'s rule the committed spectrum is REVISED (5 rates in the gap `(r_ema, mu)`); under the current rule it is SUPPORTED. *(Corrected 2026-10-31: an earlier version of this file said PARTIAL.)* | The *claim* is quarantined (ERRATA E2, `AUD-SLOWPOLE`, `CURRENT_STATUS.md:52`), but for a different reason (the 18-coordinate map is not a closed state). The **verdict-rule loosening itself is not documented anywhere.** | **No** (methodology). Its impact is contained because the claim is already quarantined. |
| F2 | `Older files/aief_1_4_slow_subspace_projection.py` → current | Verdict metric changed from mean variance fraction > 0.95/0.80 to mean abs correlation > 0.95/0.80. Composition verdict changed from "> 0.5 dominates" to h, B < 1e-12 or 1e-6 "machine zero". | Swapped metric after low variance fractions were seen (the new SUPPORTED text explains them away). **The actual output is still "Weak" (0.7394) and "non-negligible"**, so the result did not move. | Not documented. | Benign in effect, but a post-hoc metric switch. |
| F3 | `Older files/aief_1_4_multiseed_geometry_01.py` → `aief_1_4_multiseed_geometry.py` | Slow modes changed from a fixed ±1% band around r_EMA to an adaptive "largest-gap cluster" (`identify_slow_cluster`, `min_cluster=3`, contracting modes only). | Adaptive: a slow cluster is found by construction. | Not documented. | Mostly benign. No geometry output is committed (only `k3_structure_scan.csv`), and no claim cites it. **Latent bug:** `cluster_rates = sorted_rates[:max_gap_idx]` indexes the *unfiltered* array, so negative-rate (unstable) modes enter `rate_low`/`rate_high`. |
| F4 | `Older files/AIEF_1_4_matched_phase_memory_ablation{,_01,_07}.py` → current | Anchor and initial-match checks changed from `any(...)` to `all(...)` with expected counts (2 and 3). Trajectory keys changed from `allclose(rtol=atol=1e-14)` to NaN-aware exact equality. ZERO_TOL check is now against a hard-coded 1e-12. | **Stricter (away from passing).** | Comments in the code ("FIX: Require ALL …"). | Benign. One residual fail-open: `anchor_pass = … if seed_anchors else True` passes a seed that has *no* anchor rows. |
| F5 | `Older files/AIEF_1_4_feedback_rank_memory_reduction.py` → current | New `DEFAULT_LATE_TARGET_MIN = 100.0` and late-window (R² ≥ 0.95) kappa/POD summaries were added next to the existing "all" summaries. | Additive. A post-hoc late window could flatter stationarity. | Not documented. | Benign. The "all" scope is still reported. |
| F6 | `Older files/AIEF_1_4_augmented_duhamel_feedback_analysis{,_01}.py` → current | Norm guards `ZERO_TOL` (1e-12) → `np.finfo(float).tiny`. Cosine is clipped to [-1, 1]. New degeneracy guard: alignment is reported only if σ1/σ2 > 1 + 1e-8. | Mixed: the guard is more conservative, and the tiny-norm threshold admits near-zero vectors. | Not documented. | Benign (numerical hygiene). |
| F7 | `Older files/AIEF_1_4_face_spectrum_analysis.py` and `Older files/aief_1_4_face_spectrum/` → current | Adds `same_full_spectrum` and multiplicity checks, plus an R² ≥ 0.95 reliability count. The new outputs show `same_full_spectrum=False`, where the old report only showed `same_rate_1e10=True`. | **Away (more honest).** | — | Benign. |
| F8 | `Older files/AIEF_1_4_memory_ablation_updated.py` → current | 58 changed lines: 56 comment or blank lines, plus `R_physical, _, _ =` → `R_physical, *_ =`. | Neutral. | **Yes**: `b2a95dfbfbe3_REPRODUCTION.md` §Source difference. I confirm its count independently. | Benign. |
| F9 | Data folders | `Older files/87dfe5798954/` is byte-identical to `runs/87dfe5798954/` (103/103). In `Older files/b57562a8ee77/` only `manifest.json` differs: baseline-only → completed 200-condition run, and `"baseline_certified": true` was dropped. | Progression. | — | Benign. |
| — | Every other pair is formatting, logging or additive only, with 0 constant or verdict changes: `…tangent_cocycle` (optional ablations, defaults preserved), `duhamel_memory_alignment` (identical), `freeze_controller_fiber_theorem`, `phase_source_locking`, `resonant_tracking_angular`, `coupling_lock_audit`, `slow_bundle_geometry_01` (adds a report-only frac_C verdict), `two_channel_alignment_v4/v5/v5_01`, `multiseed_geometry_02…11` (seed-key parsing and error handling). | | | | Benign. |

## F1 in detail (top finding)

Old path: `Older files/aief_1_4_augmented_spectrum_02.py`. The earlier version is
`Older files/aief_1_4_augmented_spectrum.py`, which had no near-EMA check at all: `if n_in_gap == 0` →
"alpha IS the unique slow pole", with `gap_lower = r_ema`.
Current path: `aief_1_4_augmented_spectrum.py`. Its output is `aief_1_4_augmented_spectrum/augmented_spectrum_report.txt`.

```diff
-    gap_lower = r_ema
+    gap_lower = r_ema * 1.01      # 1% above EMA to exclude numerical noise
-    # Also find eigenvalues near r_EMA (within 10%)
-    near_ema = (sorted_rates > r_ema * 0.9) & (sorted_rates < r_ema * 1.1) & relevant
+    # Eigenvalues near r_EMA (within 1% — the EMA cluster)
+    near_ema = (sorted_rates > r_ema * 0.99) & (sorted_rates < r_ema * 1.01) & relevant
-    if n_in_gap == 0 and n_near_ema == 1:
+    if n_in_gap == 0 and n_near_ema >= 1:
         lines.append("  VERDICT: SUPPORTED.")
-        lines.append("  No eigenvalues in the gap and exactly one near r_EMA.")
-        lines.append("  The EMA pole alpha IS the unique slow pole.")
+        lines.append("  Gap lower bound set at r_EMA * 1.01 to account for")
+        lines.append("  ~1% finite-difference precision.")
+        lines.append("  The EMA pole alpha IS the unique slow pole of the")
+        lines.append("  true augmented dynamics on this replay.")
```

**Effect on the committed result.** The report lists these slow rates: 0.055106, then 7 rates between 0.057129 and
0.057170 (marked "EMA"), then 31.71. The phase reference is 0.689918 and r_EMA is 0.057133.
- **Under `_02`'s rule:** 5 of the "EMA" rates (0.057133538 to 0.057170314) are just above r_EMA, so they lie in
  `_02`'s gap `(r_ema, mu)`. The verdict is **REVISED** (5 in gap). Even without them, the ±10% band holds 8
  eigenvalues (including 0.055106), so `n_near_ema == 1` fails and the verdict would be PARTIAL.
  *(Corrected 2026-10-31: this said PARTIAL before; recomputed by `audits/old_files_drift/recheck_slowpole_rule.py` on branch `fix/errata-old-files-drift`.)*
- **Under the current rule:** the ±1% band holds 7 eigenvalues and the rule is `>= 1`, so the verdict is
  **SUPPORTED**, and the text says "unique slow pole" even though 7 near-degenerate poles are in the cluster.
- **What the verdict ignores.** A mode *slower* than EMA (0.055106) sits outside both bands and is never
  examined. Five unstable modes (|λ| up to 4.4e4, negative rate) pass the `relevant` filter but cannot fall in
  the gap.
- **Stale label.** The report still prints "Eigenvalues near r_EMA (within 10%): 7", although the band is now ±1%.

**Is it documented?** The verdict is quarantined:
- ERRATA E2
- `AUD-SLOWPOLE`
- `CURRENT_STATUS.md:52, :104`
- `AI Agent Audits/evidence/proposals/augmented_spectrum_citations.md`, which even lists the `Older files` copies at :13

The 966-dim audit proposal gives NO, with 10 rates in the gap. But none of these mention that the verdict rule
itself was loosened between versions, from "exactly one near-EMA pole" to "at least one". **Suggested follow-up
(not done):** add one sentence to E2, or a new erratum at the next free number after E14, recording that the v2
rule turned a REVISED into a SUPPORTED (done as ERRATA E15 on `fix/errata-old-files-drift`). Fix the stale "(within 10%)" label only via a non-pinned path. Note that
`aief_1_4_augmented_spectrum.py` and its report are hash-pinned in `AI Agent Audits/evidence/audit_manifest.json`
(lines 32 and 36), so they must not be edited in place.

## F2 in detail
Old path: `Older files/aief_1_4_slow_subspace_projection.py`. Current path: `aief_1_4_slow_subspace_projection.py`.

```diff
-    mean_cap = float(np.mean(var_df["frac_variance_slow"]))
-    if mean_cap > 0.95:   "All measured observables are dominated by the slow subspace."
-    elif mean_cap > 0.80: ...
+    mean_corr = float(np.mean(np.abs(var_df["correlation"])))
+    if mean_corr > 0.95:  "...The low variance fractions indicate that amplitude is generated outside the slow subspace..."
-    if mC > 0.5:  "EMA/coherence variables dominate the slow subspace."
+    if mh < 1e-12 and mB < 1e-12: "structurally confined to C"   elif < 1e-6: "Effectively C-dominated"
```

- **Committed output:** mean |corr| = 0.7394, which gives "Weak temporal alignment", and "h_old and/or B have
  non-negligible slow components". The result did *not* move toward the hypothesis. The old `mC > 0.5` rule
  would actually have said "EMA/coherence dominate".
- **Side observation:** the `var(slow)/var(full)` column holds values up to 7.5e35, which a variance fraction
  cannot reach. This is a likely projection or normalisation bug, out of scope here.

## F3 and F4 diffs
These are in `oldfiles/aief_1_4_multiseed_geometry_01.py__vs__aief_1_4_multiseed_geometry.py.diff` and
`oldfiles/AIEF_1_4_matched_phase_memory_ablation_01.py__vs__AIEF_1_4_matched_phase_memory_ablation.py.diff`.
Key F4 lines:
```diff
-        row["anchor_pass"] = any(r.get("seed") == seed_str and r.get("pass", True) for r in anchor_validation_rows) if anchor_validation_rows else True
+        row["anchor_pass"] = (not verify_anchors or (len(seed_anchors) == 3 and all(r.get("pass", True) for r in seed_anchors))) if seed_anchors else True
-            exact_equal = np.allclose(frozen_arr, new_arr, rtol=1e-14, atol=1e-14)   # TOLERANCE_KEYS trajectories
+        exact_equal = exact_array_equal_with_nan(frozen_arr, new_arr)
```

## Adjacent (outside `Older files/`, noted only)
- **Root-level `*_updated.py` pairs.** In `AIEF_1_3_closure_diagnostics.py` → `_updated.py`, `BINARY_ATOL` went
  from 1e-15 to `DEFAULT_BINARY_ATOL` 1e-12, which is looser. But the updated script also reports
  `exact_binary` (tol 0.0) next to `tolerant_binary`, so it is benign overall.
- **The root stub.** `AIEF_1_4_memory_ablation_updated_07.py` (eta 0.1, mu 0.01, gamma 0.5, B_c 1.0, ω 0…1.1)
  differs from the real driver (0.04 / 0.03 / 0.015 / 0.12). It is already documented as a fake stand-in in
  `Project Histories/README.md` and `b2a95dfbfbe3_REPRODUCTION.md`.
