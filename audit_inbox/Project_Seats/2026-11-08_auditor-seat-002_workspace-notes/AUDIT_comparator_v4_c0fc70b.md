# Independent re-audit: comparator v4 at c0fc70b

**VERDICT: CLEAN WITH NOTES**

Completed: 2026-11-07 08:19 CET (Europe/Tirane).
Repo: https://github.com/jacobbrainard84-knightninja/AIEFS
Tip: **c0fc70bad9c75218526124496cedc07f4504f987**
Parent / previous audited tip: **018b5139d59b850898ce9f39a1e27c3ef4143280**
Main baseline: **58d554395aef3e54ca2e53220c7d17efd9dc36d3**
Detached worktree: `/tmp/aiefs-audit-c0fc70b`.

## Summary and scope

**F1 is fixed.** The exact former NPZ integer-to-float seed bypass now produces NOT REPRODUCED, exit 1 and the required single dtype-mismatch problem in both pandas environments. Nearby independent mutations also reject. No remaining bypass was identified in this review; that is a bounded audit result, not a proof of general checker completeness.

The new implementation handles NPZ integer fields generally by dtype, not by the name `seed`. Same-valued different integer types remain accepted; signed/unsigned wraparound is not mistaken for equality. Existing float tolerances and nonfinite-mask checks are not loosened. New regression tests are ordinary tests and demonstrably fail against the old implementation.

This is a read-only local audit. No repo files or branches were edited, no push/rebase/history rewrite/deletion was performed, and no PR was opened. Reports, logs and audit harnesses live outside the repo. Usage was checked before work: **12.9%**, below the owner's 50% stop threshold. No pytest or multi-hour Lean rebuild was run. This verdict does **not** authorize a PR or merge.

## 1. Remote/history verification

- Fetched origin before auditing. Remote `fix/comparator-v4-from-main` resolved exactly to the requested c0fc70b full hash.
- `git show -s --format='%H %P'` reports exactly one parent, 018b513 full hash. The observed fetch was `018b513..c0fc70b`, an ordinary fast-forward, not a forced update. The previous tip is preserved as the direct parent; no rewrite of that observed chain occurred.
- `git merge-base --is-ancestor 58d5543 c0fc70b` succeeds. `origin/main` remains 58d5543.
- Old `origin/fix/comparator-v4-gates` remains **902abe8b2bdaabf13ee3060dce1e3e7da72ded18**.
- Read-only public GitHub API query for open PRs with this head returned **0**. This verifies no current open PR, not the nonexistence of every possible past closed PR. Snapshot saved as `open_prs_c0fc70b.json`.

## 2. Code review: why F1 is closed

Actual source reviewed: `audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v4.py`, particularly `cmp_arrays` at lines 87-110 and its call sites for every seed/branch-diagnostic field. Diff versus 018b513 was read directly, not inferred from a commit message.

The new logic is:

1. Different shapes reject, as before.
2. If exactly one dtype kind is `i`/`u`, return a named `integer/non-integer dtype mismatch (rerun ..., official ...)` string. This works in either direction, also for boolean, string, object or complex counterparts.
3. If both are integer kinds, `astype(object)` converts the NumPy integer values to exact Python integers before equality. This avoids both mixed integer/float precision loss and signed/unsigned wraparound. Same-valued uint64/int64 or uint8/int64 remain equal.
4. Other incompatible dtype-kind categories return `dtype kind mismatch` rather than silently matching/coercing.
5. Float/complex fields continue through the same mask/difference helper path. TOL = RTOL = **1e-12**, applied conjunctively; existing nonfinite masks and finite-cell differences are unchanged.

No seed-specific allow-list, input identity special case, threshold relaxation, false-data fallback or hidden xfail was added. The change applies to all NPZ integer fields, including `seed_index` and `prefix__selected_at_split`, and also branch-diagnostic arrays passed to the helper.

### Independent original probe and nearby variants

Ran the **unchanged original audit probe** through a harness in both environments. Its historical final assertion expected acceptance, so it now intentionally raises `AssertionError: bypass no longer reproduces`; the harness separately verifies the comparator's actual JSON and exit. This expected harness assertion is not a checker regression or infrastructure failure.

Both versions now report exactly:

```text
exit 1 / NOT REPRODUCED
seed_10431384713483787270.npz:seed: integer/non-integer dtype mismatch (rerun uint64, official float64)
```

That is the **sole problem**, not a generic zip failure. The mutated official-side represented seed is still the different integer 10431384713483788288, versus original 10431384713483787270.

Additional full-comparator official-NPZ mutations in each environment:

| Mutation | Observed outcome |
|---|---|
| seed uint64 -> float32 | exit 1, exact named integer/non-integer dtype problem |
| seed uint64 -> string containing the value | exit 1, named dtype problem |
| seed uint64 -> object containing the value | exit 1, named unreadable-field ValueError; `allow_pickle=False` prevents loading object arrays, no traceback |
| seed_index -> float64 of the same representable integer | exit 1, named dtype problem (even equal numeric value cannot erase integer schema) |
| seed_index -> bool | exit 1, named dtype problem |
| seed_index -> complex128 of the same value | exit 1, named dtype problem |

There are also **42 independent helper assertions per environment**, executing the actual AST-extracted helper definitions: equal mixed integer values including 2**53+1 and 2**63-1 in both directions, signed -1 vs uint64 maximum in both directions, integer/noninteger pairs in both directions, NaN/+inf/-inf mask mismatches in both directions, and float/complex over/within-tolerance controls. All pass.

The complete suite also independently runs the reverse/rerun-zip F1 mutation and the 40-seed same-value integer-retyping control. The reverse test requires its dtype-specific problem **in addition to** the unavoidable rebuilt-zip hash problem; the hash gate alone cannot satisfy it.

## 3. New tests are meaningful, not vacuous

`test_F1_official_npz_seed_float64_plus_1` asserts the original dtype, that the represented integer actually changes, and that NumPy's old mixed equality is fooled. It verifies the full comparator's rejecting verdict, exit 1, no traceback and **exactly one** expected problem.

`test_F1_zip_npz_seed_float64_plus_1` confirms its member-edit hook ran exactly once and requires the opposite-direction dtype mismatch plus the zip-pin problem. It does not merely assert any rejection.

`test_F1_official_npz_integer_fields_other_int_type_still_reproduce` checks the original field dtypes, rewrites both integer fields in every official seed, and demands exit 0 / REPRODUCED / empty problems. This guards against an over-broad fix that rejects all mixed integer widths or signedness.

All three are ordinary tests with no `expectedFailure`/GAP decorator. I pointed those **new test methods** at the unchanged comparator in `/tmp/aiefs-audit-018b513`: in **both environments**, exactly the two negatives fail and the same-value positive control passes. Those deliberately failing old-tip runs are logged separately and checked by the audit harness; they do not indicate failures on c0fc70b.

## 4. Documents, inventory, hashes and preserved history

- E14 gains only an inserted review addition immediately before E15. Sequence comparison of the complete errata file finds **insert-only**, no deletion/replacement. E12, E13, E14 and E15 remain in order, each once; no renumbering.
- The folder ERRATUM preserves the complete old file as a byte prefix and appends the “Audit of `018b513`” explanation. The previous overstatement about exact NPZ comparisons is explicitly corrected, not erased.
- Folder SHA256SUMS changes **only three lines**: folder ERRATUM, v3_to_v4.diff, v4.py. All existing v1/v2/v3 lines and v4.log line are unchanged. Actual folder-local `sha256sum -c SHA256SUMS`: **10/10 OK**.
- The stored v3-to-v4 patch was applied to a disposable copy of v3; it reproduces the actual new v4 **byte-for-byte**. An initial exact rendering comparison with Python difflib did not match the stored renderer's formatting; patch application establishes content correctness.
- Independently ran the current inventory generator with `--stdout`; output is byte-identical to the committed **3405-row** current inventory. Its checker passes. It is not the 3373-row stale 902abe8 inventory.
- Exactly eight files changed from parent: global errata, folder SHA256SUMS, folder ERRATUM, v3_to_v4.diff, v4.py, current inventory, REDTEAM.md, test_rt_comparator.py.
- None of those is a frozen worktree artifact row. No zip/NPZ inputs, registry/artifacts.csv, audit_manifest.json, verify_manifest.py, root .gitignore, check_lean.sh, augmented-spectrum source, ART-0064 driver or ART-0068/0102 documents changed. Integrity checks independently confirm all existing pins, including permitted historical drift.
- The folder-local comparator SHA256SUMS is not itself an immutable frozen-registry/audit-manifest pin; it is a tracked additive comparator manifest covered by the generated inventory, as established in the prior audit.
- Main's REDTEAM “counts are not hard-coded” Results heading remains. New F1 rows are honest; the stale anchor header-count prose is fixed. All remaining GAPs are still listed. G10/G11 remain normal rejecting tests.
- The earlier allow-list removal remains intact: live KNOWN_MISSING_ARTIFACTS is empty, restored v3.log retains E13 hash fcf370da026920417264c90eb2ff00b7e46b5dae4eb912f66b76891abe3552b6, and normal/strict lint both pass without exemptions/notices.

## 5. Independent runs

| Independent check | Actual result |
|---|---|
| pandas 3.1.0 CI self-tests | **120 tests OK**, 1.410 s |
| pandas 3.1.0 full red-team | **153 total: 143 ordinary passes, 10 expected failures, 0 skips, 0 unexpected successes**, 177.587 s |
| pandas 3.0.6 comparator discovery | **62 tests OK**, 0 skips, 148.582 s |
| lint_claims normal and --strict | both PASS; 0 errors/warnings/notices |
| Changed-file hygiene (`--base origin/main --pii`) | PASS, 0 warnings |
| Full-tree hygiene | PASS, 3 existing large-file warnings |
| check_manifest | PASS, 1 verifier run |
| check_artifact_pins | PASS, 2839 match / 7 known-changed / 52 known-missing |
| check_modes --strict | PASS, 0 errors; 119 pre-existing warn-only shebang warnings |
| check_current_inventory + independent generation | PASS, exact 3405-row byte match |
| validate_registry_against_tree | exit 0, report-mode output |
| verify_inventory_current | PASS, inventory/vocabulary/authority-lock/source digests |
| Folder SHA256SUMS | **10/10 OK** |
| Real comparator, pandas 3.0.6 | REPRODUCED, problems []; entire JSON equals committed v4.log JSON |
| Real comparator, pandas 3.1.0 | REPRODUCED, problems []; only csv_worst_rel_diff differs as already documented |
| Original F1 mutation, both environments | NOT REPRODUCED, exit 1, exactly the one required dtype problem |
| Additional whole-comparator dtype neighbors | 6 reject correctly per environment |
| Independent helper probes | 42 passed per environment |
| New tests applied to old 018b513 implementation | Exactly 2 negative tests fail and 1 positive control passes, in both environments (expected mutation-sensitivity result) |

`check_manifest` actually ran one verifier. `validate_registry_against_tree` is report mode; its exit alone is not claimed as independent fail-closed certification. Full modes check has the pre-existing warn-only shebang list; strict applies to its known-script list. Full hygiene warnings are the same three large CSVs.

No pytest-style v4.1/modular analysis suite or full Lean project rebuild was run. Red-team Lean marker and compiled tiny-project axiom-audit checks did run, not skip. No new simulation was run or scientifically certified.

### Still-open expected failures (not introduced or hidden by this fix)

The same 10 remain: indented vocabulary heading; Lean theorem-content not checked; full hygiene binary warning-only; large-text content not scanned; allowed binary/archive content not scanned; audit manifest with no data; missing-verifier wrapper skip; attribute-prefixed axiom marker miss; hidden admitGoal marker miss; seed without anchor rows. The two Lean marker gaps are caught by the compiled axiom audit. F1 and G10/G11 are **not** expected failures.

## 6. Notes, ownership and disposition

**No blocking bot fix remains from this audit.** F1 is closed by the actual code and nonvacuous independent controls. The verdict is CLEAN WITH NOTES because the known broader checker limitations and source-attribution owner item remain; this is not general scientific certification.

**Optional bot-fixable wording note:** the new folder-erratum final paragraph says “unchanged output … on pandas 3.0.6 and 3.1.0” and “v4.log is byte-identical apart from its header line.” More precise wording would distinguish unchanged output *relative to the previous comparator within each environment*, unchanged committed log, and exact committed-log JSON equality only under pandas 3.0.6. Pandas 3.1.0 differs solely in `csv_worst_rel_diff`: 8.469582303444215e-16 rather than 1.1542724065754715e-15. The preceding existing paragraph already documents that difference, so this is not a concealed verdict change or blocker.

**Separate owner erratum:** ART-0043 still incorrectly attributes the official run to the root memory-ablation source. Official manifest source hash is 34d37908479f766c4036b35975b334935a5b5fb60c0c437d7649db8d14473257 (Older files copy, ART-0217), not a94acae3f6b7cc2baef62c53eaaa07acac346ce073e18d8f566e22bef7d03549 (root, ART-0043). Existing E14 discloses this. Do not silently rewrite the pinned historical registry as part of the checker fix. Choosing whether to update valid v3-log citations to v4-log citations is also separate.

This report records an audit outcome only. It opens no PR, authorizes no PR, and authorizes no merge. Final GitHub required checks and the owner's integration process remain separate.

## Evidence

All evidence is under `/workspace/review_r026/`: `ci_c0fc70b.log`, `redteam_c0fc70b.log`, `comparator_pd306_c0fc70b.log`, `check_results_c0fc70b.json`, `check_*_c0fc70b.log`, `generated_inventory_c0fc70b.csv`, `real_pd306_c0fc70b.json`, `real_pd310_c0fc70b.json`, `reaudit_probes_c0fc70b.py`, `probes_pd306_c0fc70b.log`, `probes_pd310_c0fc70b.log`, `original_probe_c0fc70b_3.0.6.log`, `original_probe_c0fc70b_3.1.0.log`, `open_prs_c0fc70b.json`. The unchanged original `probe_npz_seed_dtype.py` remains available.
