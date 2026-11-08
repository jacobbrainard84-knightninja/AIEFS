# Independent audit: comparator v4 / E14 at 018b513

**VERDICT: FIXES REQUIRED**

Audit completed: 2026-11-07 08:03 CET (Europe/Tirane).
Repository: https://github.com/jacobbrainard84-knightninja/AIEFS
Branch: `fix/comparator-v4-from-main`
Audited tip: `018b5139d59b850898ce9f39a1e27c3ef4143280`
Baseline: `58d554395aef3e54ca2e53220c7d17efd9dc36d3`.

## Decision

Do **not** open a ready-to-merge PR yet. The two specifically unreviewed integration changes are sound, but an independent known-false NPZ seed mutation still returns **REPRODUCED, exit 0, problems []**. Fix this bot-fixable comparator hole and add a normal rejecting regression test before a new audit. This finding does not establish that the genuine committed data are false; it establishes that the comparator can falsely certify altered inputs.

No repository files or branches were edited, pushed, rebased, deleted or submitted as a PR. Review was local, in detached worktree `/tmp/aiefs-audit-018b513`; reports/probes are outside the repo. The original clone was clean. Weekly usage was checked before work: 8.1%, below the owner's 50% stop threshold.

## F1 — BLOCKER: NPZ integer seed comparison still loses precision across dtypes

**Location:** `audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v4.py:81-88`, called at `:226`.

The CSV O1 fix is real, but `cmp_arrays` still branches only on the rerun array's dtype. If that dtype is integer, it uses `np.array_equal(x, y)` without guarding the official array's dtype. NumPy mixed uint64/float64 equality coerces away low integer bits. This is an O1-like precision bypass in the **NPZ** path, separate from the now-correct CSV path.

Independent reproduction (both default pandas 3.0.6 and `/workspace/venv_pd310` pandas 3.1.0):

1. Create the suite's isolated official-run copy; leave the zip, manifests, sources, CSV, names and other NPZ fields unchanged.
2. In `seed_10431384713483787270.npz`, replace only `seed` with `np.array(int(original_seed) + 1, dtype=np.float64)`.
3. Original: uint64 **10431384713483787270**.
4. Tampered represented value: float64, whose integer value is **10431384713483788288**, a different integer (+1018).
5. `np.array_equal(original_uint64, tampered_float64)` nevertheless returns True.
6. The unmodified full comparator returns **REPRODUCED / exit 0 / problems []**.

This is not a harmless serialization rewrite: the represented seed value changed. Existing `test_seed_integer_field_changed` preserves integer dtype, so it misses this case. CSV exact-int checks cannot detect the independently altered NPZ seed.

Reproducer (safe: temp files only):

```bash
python3 /workspace/review_r026/probe_npz_seed_dtype.py /tmp/aiefs-audit-018b513
/workspace/venv_pd310/bin/python /workspace/review_r026/probe_npz_seed_dtype.py /tmp/aiefs-audit-018b513
```

Evidence: `npz_seed_dtype_pd306.log`, `npz_seed_dtype_pd310.log` alongside this report. The probe asserts that this bypass currently reproduces; it is audit evidence, **not** a production passing-negative test.

Required outcome: integer/seed NPZ comparisons must not silently promote to lossy floating-point equality. Reject an inappropriate dtype or compare integer semantics without precision loss, cover the differing/mixed integer types too, and add normal red-team tests asserting exit 1, NOT REPRODUCED, and an integer/dtype-specific problem for this mutation. Retain the real-data positive control and genuine floating tolerances. Update E14/folder erratum and generated inventories/checksums for the reviewed fix as appropriate; do not modify historical pinned inputs.

## Specifically requested integration reviews

### Merge dbd5759: PASS

- Actual parents: `74936b3` and `58d5543`. The current main is an ancestor of the audit tip (`git merge-base --is-ancestor` succeeds).
- `tools/redteam/REDTEAM.md:56-59` retains main's **Results / Counts are not hard-coded** fix. The lint hardening table and matched-phase section survive.
- Its comparator table now correctly targets v4. G10 (branch labels) and G11 (schema) are normal rejecting tests, not expected failures; both passed independently. Other existing GAP rows are retained, not hidden.
- Inventory at merge `dbd5759`: **3405 data rows**, exact match to the unchanged generator's result for that commit's tracked files and bytes. I independently generated tip rows, substituted the pre-tip versions of files changed by 018b513, and compared rendered bytes with `git show dbd5759:registry/artifacts_current.csv`: identical.
- Tip inventory: **3405 data rows**, byte-for-byte identical to `build_current_inventory.py --stdout` and passes its independent checker.
- Old `902abe8` inventory: **3373 data rows**, different bytes/hash. Thus neither current inventory is the stale copied inventory. Byte identity establishes valid regeneration, not proof of which command the author personally ran.
- Minor inherited prose inconsistency: REDTEAM.md:238-240 still says an old “header count above” excludes the five anchor tests, although the Results header no longer hard-codes counts. Cosmetic, bot-fixable follow-up; no findings are concealed.

### Allow-list removal 018b513: PASS, strictly stronger

- Diff to main changes only the one live `KNOWN_MISSING_ARTIFACTS` entry into comments; there are now **zero live exemptions**. The resolver/check logic is otherwise identical to main.
- Restored v3.log exists and hashes to **fcf370da026920417264c90eb2ff00b7e46b5dae4eb912f66b76891abe3552b6**, exactly the pre-existing E13 checksum line. That line did not change.
- Normal and strict lint pass, both with 0 errors, warnings or notices.
- Independent negative test removed **only a temporary mirror's v3.log**: lint exited 1 with `AUD-REPRO-B2A95: cited artifact does not exist`. Evidence: `missing_v3_negative.log`.
- `tools/ci/lint_claims.py` is not a historical hash-pinned file in the frozen artifacts registry or audit manifest. Its current-tree generated inventory row was updated. No pin bypass is involved.

## History, port completeness and pinned files

- Fetched origin first. Remote audit branch was exactly `018b5139d59b850898ce9f39a1e27c3ef4143280`; old `origin/fix/comparator-v4-gates` still exactly **902abe8b2bdaabf13ee3060dce1e3e7da72ded18**.
- `74936b3` has parent `2e55eb5`; old 902abe8 is not its ancestor. Merge-base of old tip and main is `395ea535d939c594c51c85169859f09f65f360b5`. This is a file port, not a wholesale old-branch merge.
- All comparator-folder files and `tools/redteam/test_rt_comparator.py` match old 902abe8 byte-for-byte. CSV raw-text Python-int comparisons, D_B_final tolerance tests, named malformed-input problems, zip pin and SUSPICIOUS copy gates were all ported.
- E14 occurs **once**, between E13 and E15; headings E12/E13/E14/E15 are in numeric order. E14 is additive to main and does not renumber or delete earlier text.
- E14's add81e6/c4434cb citations exist: their diffs add the root memory-ablation source and the official manifest respectively. The existing clone is shallow; I verified those actual commit diffs, not an unrestricted historical ancestry claim.
- No changed file is a worktree row in frozen `registry/artifacts.csv`; no historical audit-manifest input/published file was modified. The registry and audit manifest themselves, verify_manifest.py, root .gitignore, check_lean.sh files, augmented spectrum source, ART-0064 driver and ART-0068/0102 docs are unchanged against main.
- The one changed `audits/reproductions/b2a95dfbfbe3/SHA256SUMS` is **not itself pinned by that frozen registry or audit manifest**. It is an additive comparator-folder manifest, tracked in the generated current inventory. Its intentional delta updates the appended folder erratum's hash and adds v4.py/v4.log/v3_to_v4.diff. Existing v1/v2/v3 checksum lines remain unchanged. Folder-local `sha256sum -c SHA256SUMS`: **10/10 OK**.
- Author identity is the reported local Researcher 001 identity; no personal/auditor identity substitution was observed. This is not a claim to have externally proven the absence of every historical rewrite.

## Integrity and numerical review

The fixed CSV seed/seed_index path compares raw integer strings via Python ints, not float64; missing/asymmetric cells and float-text seeds reject. Tolerance tests demonstrably perturb **D_B_final**, including a within-tolerance positive control. TOL remains 1e-12 and RTOL 1e-12 is conjunctive (a tightening). NaN/+inf/-inf masks are checked separately from finite numeric differences. Changed schema, source hash, source-code difference, labels, manifest key sets, missing seeds and parameters have real rejecting controls.

Zip pin is the documented **281bf33be105cb6219af7aecb9f8ae547459856c1548fdf646f5caee9f8d17ad** and matches the real archive. Rebuilt-zip control fails on the pin alone. G-B seed, CSV and branch-diagnostics copy tests independently require their SUSPICIOUS reason, so a generic zip-pin failure cannot make those tests pass vacuously. Stub-model equality is explicitly informational because the documented stub is wrong; presence/readability remain gated. Tests of malformed manifests, bad CRC, unreadable members and missing source files produce named rejection verdicts.

There is no newly loosened tolerance, cherry-picked seed subset or always-pass manifest in this port: all 40 expected seed names must match and are compared. However, SUSPICIOUS exact-copy detection is an artifact-specific anti-copy heuristic, **not** proof that independent simulations were actually performed. This comparator is not a general engine certification, and this audit ran no new simulations. F1 is precisely why green repository tests alone do not establish checker correctness.

## Independent execution results

Commands below used pandas 3.1.0 venv unless noted. **No pytest** was run.

| Check | Result |
|---|---|
| `python -m unittest discover -s tools/ci/tests -v` | 120 tests, OK (1.225 s; pre-existing ResourceWarnings) |
| `python -m unittest discover -s tools/redteam -v` | 150 total: 140 ordinary passes, 10 expected failures, 0 skips, 0 unexpected successes (167.984 s) |
| `lint_claims.py`, `lint_claims.py --strict` | both PASS, 0 errors/warnings/notices |
| hygiene changed files (`--base origin/main --pii`) | PASS, 0 warnings |
| hygiene full tree | PASS, 3 existing large-CSV warnings |
| `check_manifest.py` | PASS, 1 verifier run |
| `check_artifact_pins.py` | PASS: 2839 match / 7 known-changed / 52 known-missing |
| `check_modes.py --strict` | PASS, 0 errors, 119 existing warn-only shebang files (strict covers the known script list) |
| `check_current_inventory.py` + generator comparison | PASS, exact 3405-row inventory |
| `validate_registry_against_tree.py` | exit 0, report mode; not an independent fail-closed certification claim |
| `verify_inventory_current.py` | PASS, including lock/vocabulary/Lean source digest checks |
| Folder-local SHA256SUMS | 10/10 OK |
| Real comparator, pandas 3.0.6 | REPRODUCED, problems []; JSON identical to committed v4.log body |
| Real comparator, pandas 3.1.0 | REPRODUCED, problems []; worst relative diff 8.469582303444215e-16 rather than 1.1542724065754715e-15 |
| Independent missing-v3.log control | correctly rejected |
| Independent NPZ mixed-dtype altered-seed control, both pandas versions | **incorrectly accepted (F1)** |

The committed log includes its command header and `exit 0` footer; the exact-match statement above concerns its entire JSON object, not those wrapper lines. The scalar CSV accounts for the small pandas-version difference; verdict and tolerances are unchanged.

Full Lean projects and pytest-style analysis suites (claimed 13 and 40/2) were **not independently rerun**, per no-pytest/fast-local scope. Red-team Lean marker/axiom-audit tests did run successfully. No multi-hour jobs or infrastructure retry loop. Two root-directory checksum invocations used the wrong working directory and reported no root SHA256SUMS; the actual folder-local invocation then verified 10/10. These were audit-command path errors, not repository checksum failures.

### The 10 remaining expected failures (all honestly documented)

1. Claims lint: indented/code-block vocabulary heading accepted (F5).
2. Claims lint: an existing Lean file need not contain the claimed theorem.
3. Hygiene: full-tree binary outside permitted locations is warning-only.
4. Hygiene: token in text larger than 10 MiB is not content-scanned.
5. Hygiene: token inside a binary/archive in an allowed location is not content-scanned.
6. Audit verifier: a PASSED manifest containing no data can pass.
7. Manifest wrapper: missing verifier is skipped, not failed.
8. Lean marker scan: attribute-prefixed axiom missed (compiled axiom audit catches it).
9. Lean marker scan: hidden admitGoal tactic missed (compiled axiom audit catches it).
10. Matched-phase: a seed with no anchor rows reports anchor_pass=True.

G10/G11 are not on this list: both are promoted to ordinary normal negative tests and passed. The newly found F1 is not covered by these existing expected failures and must be fixed rather than hidden as another xfail.

## Owner items versus bot work

**Bot-fixable before proceeding:** F1, its real rejecting negative tests, updated explanatory erratum/checksums/inventory, final fresh-tip re-audit. Cosmetic REDTEAM count prose can be cleaned opportunistically.

**Separate owner/scientific-governance items, not prerequisites to this checker correction:** ART-0043 mis-attribution remains. Official manifest source is **34d37908479f766c4036b35975b334935a5b5fb60c0c437d7649db8d14473257**, which hashes the Older files source (ART-0217), not the root source **a94acae3f6b7cc2baef62c53eaaa07acac346ce073e18d8f566e22bef7d03549** registered as ART-0043. E14 honestly discloses this; a separate erratum/owner decision is appropriate rather than editing the pinned historical registry here. Choosing whether to repoint the claims/reconciliation citation from valid restored v3.log to v4.log is also separate.

**PR recommendation:** not appropriate as merge-ready at this tip; return F1 to Researcher 001, fix locally on the working branch through the normal workflow, then audit the new final commit and run GitHub checks before owner merge. This report neither opens nor authorizes any remote write.

## Evidence files

All in `/workspace/review_r026/`: `ci_018b513.log`, `redteam_018b513.log`, `check_results_018b513.json`, individual `check_*_018b513.log`, `generated_inventory_018b513.csv`, `real_pd306.json`, `real_pd310.json`, `missing_v3_negative.log`, `probe_npz_seed_dtype.py`, `npz_seed_dtype_pd306.log`, `npz_seed_dtype_pd310.log`.
