# Audit: `fix/errata-old-files-drift` @ 6d180dd (ERRATA E15)

Auditor: Researcher 001's auditor seat (independent re-derivation). Date: 2026-10-31, about 12:25 EDT.
Repository: jacobbrainard84-knightninja/AIEFS. I worked in one fresh clone under `/workspace/audit_r001/e15/repo`.
I did not push, open a PR, touch main, or edit any other workspace folder.
Base: `395ea53` (= `origin/main`). `52f5c92` is the cherry-pick of `a614451` (on `origin/research/redteam-negcontrols`). Its `tools/redteam` patch is byte-identical to the original; I compared with `git show` diff. `6d180dd` is the erratum commit (16:13 UTC = 12:13 EDT).

## Verdict: **CLEAN WITH NOTES**

E15 is accurate. I checked every blob hash and every line citation. The recheck script computes its results from the committed data and does not hard-code them. Its committed output matches a fresh run byte for byte. The registry change is exactly one cell, and the registry rebuilds with no diff. No pinned file changed. All suites match the stated numbers.

None of the notes below blocks a merge. N1 to N3 are suggested wording additions. N4 to N6 are pre-existing issues outside this branch.

---

## 1. F1 re-derived independently

Sources:
- `Older files/aief_1_4_augmented_spectrum.py` (v1, blob f7ef1f5d78ae)
- `Older files/aief_1_4_augmented_spectrum_02.py` (v2, blob 930ad02af207)
- `aief_1_4_augmented_spectrum.py` (current, blob 45dffa1e5cfd, sha256 7b54aa88… = `audit_manifest.json:32`)

`diff _02 current` shows only the gap lower bound (L291), the near band (L297), `>= 1` (L344), and the comments and verdict text. So the committed CSV is exactly what v2 would have produced, as E15 says.

My own code reads `augmented_eigenvalues.csv` and `analysis_manifest.json`. It recomputes each rate as `-ln|eval_real + i eval_imag| / dt` from the eigenvalue components, not from the `rate` column. Inputs: r_EMA = 0.05713333333333142 (= −ln α/dt exactly) and mu = 0.689918.

| rule | gap | n_in_gap | near band | n_near | verdict |
|---|---|---|---|---|---|
| v1 | (r, mu) | 5 | – | – | "5 eigenvalue(s) found in the gap" |
| v2 (_02) | (r, mu) | **5** | (0.9r, 1.1r) | **8** | **REVISED** |
| current | (1.01r, mu) | 0 | (0.99r, 1.01r) | 7 | **SUPPORTED** |

- If v2's gap were empty, the near count would still be 8, not 1, so the verdict would be **PARTIAL**. Seat 002's correction is right.
- The 4 rows left out of the CSV are sorted indices 14–17. Indices 0..13 are contiguous, and the CSV's index is the position in the sorted rate array, so each left-out rate is ≥ 31.71 > mu. They cannot change any count.
- The recheck script's results respond to the data (mutation tests on a temporary copy):
  - Moving the 5 gap rates below r_EMA gives v1 "NO", v2 PARTIAL, and rc=1 (it also flags the broken sort).
  - Injecting a rate at 0.3 gives current = REVISED (1) and rc=1 for the mismatch with the CSV flags.
  - A rate that disagrees with |λ| gives rc=1.
  - Flipping a `near_ema` flag gives rc=1.
- A fresh run gives rc=0. Its body is identical to `recheck_slowpole_rule_output.txt` once the header line ("command: …"), the blank line and the "exit code: 0" footer are stripped.

## 2. E15 text, numbering and registry
- Every citation checks out: v1 L281–282, L327, L329; _02 L284, L288–289, L294, L341, L346, L350; current L284, L291–292, L297, L339, L344; report :20, :25, :28, :36–40, :41; `audit_manifest.json` :32 and :36; `CURRENT_STATUS.md` :51, :52 and :104–105; `augmented_spectrum_citations.md` :13 and :22. All 9 short blob hashes match `git hash-object`. The import commit is `add81e6`, dated 2026-10-18 18:08 −0600.
- Numbering: E15 comes after E13. `origin/fix/comparator-v4-gates` @ 1250bbd holds `## E14.` (the comparator v3 gates). E12 is absent on main, which matches the existing E13 merge note (research/freezing).
- Registry: the old and new `claims.csv` differ in exactly one cell, row AUD-SLOWPOLE, column `reconciliation_note`. The cause is the one-sentence edit to the builder.
- Rebuild: I ran `build_claims_reconciliation.py` and then `build_current_inventory.py`. `git status` was clean afterwards and `check_current_inventory` passed.
- `artifacts_current.csv` changes only the rows for the new or edited files, which is expected. Strictly, the change is "one claims.csv cell plus the builder line plus the regenerated inventory", not the claims cell alone. The commit message says this.

## 3. F2 (7.5e35) and F3
**F2 is a real defect, but in the method, not in floating point.** `aief_1_4_slow_subspace_projection.py` L276 projects the **absolute** state vector onto the span of the slow eigenvectors (`Q_slow Q_slowᵀ sv`) rather than a deviation from a reference state. It then injects that unphysical state and recomputes the nonlinear observables.
- The slow modes have h_old ≈ 0, and the projected node strength `q_scale[7]` comes out at 0. The gate `s7 = cap/(q+eps_sc)` therefore saturates at 0.63333/1e-12.
- Evidence: min `slow_s2_minus_s7` = −6.3333e11 = −cap/eps_sc exactly; 914 of 32,000 steps have |slow| > 1e6; the median |slow| is 339, against full values of order 1e-7.
- Dividing var_slow ≈ 1.1e22 by var_full ≈ 1.5e-14 gives 7.5e35.

Does it matter for a claim? No.
- The only claim citing the script is REJ-SPEC-01, which is already Rejected. Its stated reason ("blow-up under non-normal coupling") misattributes the cause, but the status is right.
- E15's wording ("points to a projection or normalisation defect") is accurate.

**F3:**
- E15's sentence ("listed in `augmented_spectrum_citations.md:22` as a user of the quarantined 18-coordinate Jacobian, and no claim rests on its output") matches :22, which is in section B, "scripts that reuse the same 18-coordinate map".
- `claims.csv` does not mention the script.
- `studies.csv:11` and `relocation_map.csv:142` file it as Rejected.
- L167 (rate range taken from the unfiltered `sorted_rates`) is a correct reading of the code.

## 4. AST red-team test robustness
I mutation-tested it on a temporary copy of the pinned script:

| mutation | result |
|---|---|
| unmodified | OK, 1 expected failure |
| expression moved 40 lines down | OK. It finds the expression by AST, not by line number, and still evaluates the real expression |
| gap fixed (`else False`) | FAILED (unexpected success) |
| `= True` | FAILED (2 failures) |
| target renamed / assignment duplicated / variable renamed | FAILED (3 errors; RuntimeError "expected exactly one" or NameError) |
| `len == 3` dropped | FAILED |
| `any` instead of `all` | FAILED (NameError; builtins are restricted) |
| `not verify_anchors` branch inverted | **OK (not caught)** (N3) |

A moved line cannot go unnoticed in practice. A one-byte edit to the script made `check_artifact_pins` fail: `PIN_MISMATCH ART-0041` (sha256 2a0f2c7e… is pinned).

The docstring's statement about the committed run is true: `test_output/frozen_anchor_validation.csv` has 120 rows, 40 seeds × 3 anchors, all passing. `matched_phase_seed_status.csv` shows 40 × success and anchor_pass=True.

## 5. Pins and suites (Python 3.13.5)
- No file the branch changed appears in `registry/artifacts.csv`, `audit_manifest.json` or any `SHA256SUMS`.
- `.gitignore` (ART-0001) is unchanged from 395ea53. Its sha 6a81afd0… equals the `KNOWN_CHANGED` allowlist entry.
- `sha256sum -c`:
  - `AI Agent Audits/lean_recovery`: OK
  - `tools/sync`: OK
  - `audits/reproductions/b2a95dfbfbe3`: one entry fails, pre-existing (N6)
- CI unittests (`tools/ci/tests`): **Ran 103, OK**.
- Red-team (`tools/redteam`): **Ran 78, OK (expected failures=14)**, no skips. The 4 new tests are 3 ok and 1 expected failure.
- Repo checks, all rc 0: lint_claims; hygiene_scan (3 pre-existing BIG_FILE warnings); hygiene_scan with `--base 395ea53 --pii` (0 warnings); check_manifest; check_artifact_pins; check_modes `--strict`; check_current_inventory; verify_inventory_current.
- Not run: the two pytest CI steps (pytest is not installed on the box). The branch does not touch `AIEF_Experiments/`.

## 6. Hunt for false or built-in results in `recheck_slowpole_rule.py`
- There is no try/except, so no error is swallowed. It exits 1 on any problem.
- No verdict is asserted or hard-coded. The constants 0.9, 1.1, 1.01 and 0.99 are copied from the rules; I checked each against the source lines.
- The cross-check against the CSV's own `in_gap`/`near_ema` flags is a real independent comparison, not a self-reference.
- Two minor weaknesses:
  - The rules are copied by hand rather than extracted from the old files, so a copying error would not be caught. I checked them manually.
  - The rate check uses the `abs_eval` column rather than the eigenvalue components. My recomputation from the components gives the same counts.

---

## Notes (non-blocking)
- **N1. Not overstated, but not robust either.** The 5 "gap" rates lie only 3.6e-6, 8.3e-6 (×2), 2.6e-5 and 6.5e-4 above r_EMA, in relative terms. Four of them differ from α by ≤ 1.5e-8 in |λ|, which is at the scale of the 1e-8 finite-difference perturbation. So v2's REVISED is a strict-inequality outcome, not evidence of a separate slow mode. The robust statement is: **no pre-loosening rule gives SUPPORTED** (v2 gives REVISED, or PARTIAL with n_near = 8). Suggest adding one sentence to E15.
- **N2. F2/F3 outputs are classified Supported (pre-existing).** `registry/artifacts.csv` ART-0637–0641 (all F2 outputs, including the 7.5e35 `variance_fractions.csv`) and ART-0535 (`aief_1_4_multiseed_geometry/k3_structure_scan.csv`, a committed 1-byte "\n" placeholder), plus `relocation_map.csv:141` and `:165`, file these outputs as **Supported** under AIEF_1_4_CONTROLLER_FIBER ("Active verified"), while their scripts are Rejected. "No claim rests on its output" is still true at claim level, but E15's "No geometry report is committed" should mention the placeholder and this mismatch. `artifacts.csv` is frozen (E7), so the fix is a documentation note, not an edit.
- **N3. One branch untested.** The AST test has no case for the `verify_anchors=False` branch; inverting it passes. Optional: add a control in which `evaluate(anchors(True, False, True), verify_anchors=False)` is True.
- **N4. Merge conflict.** E14 (comparator-v4) and E15 both append after E13 at line 221, so merging both gives a textual conflict. Keep E14 before E15. E15 has no merge note of the kind E13 has.
- **N5. A GAP test can be skipped and still exit 0 (pre-existing).** `rtcommon.gap` turns a broken GAP fixture into a skip, and a run with only a skip still exits rc 0. Today's run has 0 skips. Anyone reading the results should check the skip count.
- **N6. A SHA256SUMS entry names an uncommitted file (pre-existing on main, 98da939).** `audits/reproductions/b2a95dfbfbe3/SHA256SUMS` lists `compare_b2a95dfbfbe3_v3.log`, which is git-ignored (`*.log`, `.gitignore:23`) and was never committed. E14 on comparator-v4 already records this. It is not caused by this branch.
- Observation, out of scope: the failed partial run `aief_1_4_matched_phase_memory_ablation/` (manifest status FAILED) shows seed 11242426753702356865's `full_reset` anchor **failing**, while the same seed passes in `test_output/`.

Cleanup: I removed the clone, its `__pycache__` and the temporary mutation trees. Logs are kept in `/workspace/audit_r001/e15/` (`ci_unittest.log`, `redteam.log`).
