# Delta audit: `fix/errata-old-files-drift` @ 340e5b5 (ERRATA E15 review additions)

Auditor: Researcher 001's auditor seat. Date: 2026-10-31, about 12:35 EDT.
Repo: jacobbrainard84-knightninja/AIEFS. I made a fresh `gh repo clone` under `/workspace/audit_r001/e15b/repo` and removed it afterwards. Logs are kept in `/workspace/audit_r001/e15b/` (`ci.log`, `rt.log`).
I did not push, open a PR, or contact anyone. I edited no other workspace folder.

The target `340e5b5` (author: Auditor Seat 002; committed 16:27:45 UTC = 12:27 EDT) is a fast-forward of `6d180dd` (`git merge-base --is-ancestor` OK). `origin/main` is still `395ea53`.
The delta touches 4 files:
- `ERRATA_2026-10-28.md` (+27/−1)
- `registry/artifacts_current.csv` (3 rows regenerated)
- `tools/redteam/REDTEAM.md`
- `tools/redteam/test_rt_matched_phase_anchor.py` (+4)

## Verdict: **CLEAN WITH NOTES**

I re-derived every number the author claims, and they reproduce. All suites and checkers match the stated results. No pinned or hash-listed file changed. The notes below are wording or merge hygiene, and none blocks a merge.

## Claims

| # | Claim | Status | How I checked |
|---|---|---|---|
| N1 | Rates recomputed from the eigenvalues; relative excess 3.59e-6 to 6.47e-4; four of the five within 1.5e-8 of α; E15 says REVISED is not a separate slow mode and no pre-loosening rule gives SUPPORTED | **Verified** | See §1 |
| N2 | Note in E15 only, `artifacts.csv` untouched; ART-0535 and ART-0637..0641 Supported while ART-0534/0636 Rejected; relocation_map :141/:165 vs :142/:166; `k3_structure_scan.csv` is 1 byte | **Verified** | See §2 |
| F2 | L276 projects the full state; min `slow_s2_minus_s7` = −6.3333e11 = −cap/eps_sc; REJ-SPEC-01's stated reason is wrong but its status is unchanged | **Verified** (one wording nit, W2) | See §3 |
| N3 | New test `test_01_control_verify_anchors_false_skips_anchor_check`; two mutations each make it fail | **Verified**, plus 3 mutations of my own | See §4 |
| N4 | E15 placed after E14, with an E13-style merge note | **Verified**, but the note is incomplete (W3) | See §5 |
| Checks | CI 103 OK; red-team 79 OK (14 xfail); all repo checks rc 0; no pinned file touched | **Verified** | See §6 |
| Side note | In `full_reset` only `similarity_trajectory_exact` fails, "because of an extra blank `similarity_trajectory_max_diff` column" | **Partly**: the first half holds, the causal half does not (W4) | See §7 |

## 1. N1, recomputed
My code reads `aief_1_4_augmented_spectrum/augmented_eigenvalues.csv`, computes |λ| = |eval_real + i·eval_imag| myself, and takes rate = −ln|λ|/dt with dt = 0.01. It uses α = 0.9994288298464774 from `analysis_manifest.json`, so r_EMA = 0.05713333333333142.

| idx | rate | (rate−r)/r | \|λ\|−α | _02 gap | ±10% | ±1% |
|---|---|---|---|---|---|---|
| 5 | 0.055106383 | −3.55e-2 | +2.0e-5 | | ✓ | |
| 6 | 0.057129228 | −7.19e-5 | +4.1e-8 | | ✓ | ✓ |
| 7 | 0.057132387 | −1.66e-5 | +9.5e-9 | | ✓ | ✓ |
| 8 | 0.057133538 | **3.589e-6** | −2.05e-9 | ✓ | ✓ | ✓ |
| 9, 10 | 0.057133809 | **8.333e-6** | −4.76e-9 | ✓ | ✓ | ✓ |
| 11 | 0.057134819 | **2.600e-5** | **−1.485e-8** | ✓ | ✓ | ✓ |
| 12 | 0.057170314 | **6.473e-4** | −3.70e-7 | ✓ | ✓ | ✓ |

- Counts: the _02 gap holds 5 and the ±10% band holds 8, so _02 gives REVISED (PARTIAL if the gap were empty). The current rule gives gap 0 and band 7, so SUPPORTED.
- Four of the five gap rates have |Δ| ≤ 1.485e-8, which E15 rounds to 1.5e-8. The fifth is at 3.7e-7.
- `DEFAULT_PERTURBATION = 1e-8` is at `aief_1_4_augmented_spectrum.py:47`, and the manifest records perturbation 1e-08.
- More support for the noise reading: rates 6 and 7 scatter *below* α by similar amounts (+4.1e-8, +9.5e-9 in |λ|). That means the cluster straddles α on both sides; it is not offset to one side.
- The E15 wording (ERRATA L252–256) matches these numbers. See W1 for one soft phrase.

## 2. N2, checked against the files
- `registry/artifacts.csv` is unchanged in 6d180dd..340e5b5, and also against 395ea53.
- Rows as stated:
  - ART-0534 (`aief_1_4_multiseed_geometry.py`) and ART-0636 (`aief_1_4_slow_subspace_projection.py`) are `AIEF_1_4_REJECTED_SPECTRAL_AND_K3,Rejected`.
  - ART-0535 (`k3_structure_scan.csv`, size 1) and ART-0637..0641 (the five `aief_1_4_slow_subspace_projection/` files) are `AIEF_1_4_CONTROLLER_FIBER,Supported`, with "Active verified AIEF 1.4 script".
- `registry/relocation_map.csv`:
  - :141 (dir `aief_1_4_multiseed_geometry`) and :165 (dir `aief_1_4_slow_subspace_projection`) are Supported.
  - :142 and :166 (the two scripts) are Rejected.
- `k3_structure_scan.csv` is 1 byte. Its sha256 is `01ba4719…546b` = sha256("\n"). It is written by `aief_1_4_multiseed_geometry.py:621`, so calling it that script's output is correct.
- `registry/claims.csv` cites neither output directory. REJ-K3-04 cites the separate `aief_1_4_k3_structure_scan.py`, whose outputs are in a different folder. So "No claim cites these outputs" holds.

## 3. F2 cause, checked
- `aief_1_4_slow_subspace_projection.py:276` reads `sv_slow = Q_slow @ (Q_slow.T @ sv)`, where `sv = extract_fundamental(state)` (L275). That is the full state, with no reference subtracted.
- L279 is `inject_fundamental(state, sv_slow)` and L280 calls `base_intermediates`. E15 says "L279 injects … into the nonlinear observable map", which is accurate with the map at L280.
- `cap = (a−delta)/q` (L185). Run manifest `runs/5a9f093a2fe0/manifest.json` gives a = 1.0, δ = 0.05, q = 1.5, so cap = 0.633333…; eps_sc = 1e-12 (L35). That makes −cap/eps_sc = −6.333333333e11.
- `observable_projections.csv` (32,000 rows):
  - min `slow_s2_minus_s7` = −6.33333332593e11, which is −cap/eps_sc to a relative 1.2e-9 (one step).
  - 914 steps have |slow| > 1e6.
  - median |slow| = 339.47.
- `variance_fractions.csv`: 7.496e35 (var_full 1.478e-14, var_slow 1.108e22) and 1.448e11 are as stated.
- `claims.csv:40` REJ-SPEC-01 reads "blow-up under non-normal coupling", status Rejected, and is unchanged.
- "`q_scale[7]` comes out at about 0" is an inference, not a logged value. It is sound: the minimum implies |q_s[7]| ≈ 1e-21 at that step.

## 4. N3, mutation tests
I ran these on a temp copy of `tools/redteam` plus the pinned script. Each edit was asserted to match exactly once.

| mutation of L1751 | result |
|---|---|
| none | OK, 5 tests (1 xfail) |
| author's #1: drop `not verify_anchors or` | FAIL: test_01 |
| author's #2: `not verify_anchors` → `verify_anchors` (my N3 case; previously not caught) | FAIL: test_01, one_failed, two_of_three |
| mine: `or` → `and` | FAIL: test_00, test_01 |
| mine: `not verify_anchors` → `True` | FAIL: one_failed, two_of_three |
| mine: `== 3` → `>= 2` | FAIL: two_of_three |

N3 is closed. The REDTEAM.md table row and the count "5 tests (4 PASS including 2 controls, 1 GAP)" match the run.

## 5. N4, ordering and merge note
- In the branch, E15 follows E13 directly (L221). The added line at L224 says E15 belongs after E14.
- The merge note at the end (ERRATA L314–317) mirrors E13's note. Its "including its correction section" matches `origin/fix/comparator-v4-gates` @ f0aadce, which has `## E14.` at L221 and its correction block at L237.

## 6. Suites, checkers, pins (Python 3, fresh clone)
- CI: `python -m unittest discover -s tools/ci/tests` gives **Ran 103, OK**.
- Red-team: `discover -s tools/redteam` gives **Ran 79, OK (expected failures=14)**. That is 65 ok plus 14 xfail, with **0 skips**. `git status --porcelain` was empty afterwards.
- All rc 0:
  - `validate_registry_against_tree.py`
  - `hygiene_scan.py --base origin/main` (0 warnings), with `--pii` (0 warnings), and a full scan (3 pre-existing BIG_FILE warnings)
  - `check_artifact_pins` (0 errors)
  - `check_current_inventory`
  - `verify_inventory_current` ("ALL … GATES PASSED")
  - `check_manifest` (1 verifier, 0 failed)
  - `lint_claims` (0/0/0)
  - `check_modes --strict` (0 errors)
- Not run: the two pytest steps. pytest is absent here, and the branch does not touch those paths.
- Pins: no delta file appears in any `SHA256SUMS`, `audit_manifest.json`, `registry/artifacts.csv`, or the pin lists.
  - The only match is a prose mention of `ERRATA…E7` in a comment in `check_artifact_pins.py:16`, which is not a pin.
  - `.gitignore` (ART-0001) sha is `6a81afd0…`, unchanged.
  - `check_lean.sh`, `verify_manifest.py`, all SHA256SUMS files, the Lean source sums, and `artifacts.csv` are unchanged in 6d180dd..340e5b5.
- `sha256sum -c`: `AI Agent Audits/lean_recovery` and `tools/sync` are OK. `audits/reproductions/b2a95dfbfbe3` still has the uncommitted `v3.log` entry (pre-existing N6).
- `artifacts_current.csv`: the 3 changed rows match the actual sha256 and size of the 3 edited files.
- PII: the added lines and the commit message contain no names, emails, home paths, or other personal details. The only identifiers are the seat labels.

## 7. Side note (light look)
`aief_1_4_matched_phase_memory_ablation/frozen_anchor_validation.csv`, seed 11242426753702356865:
- `full_reset` has pass=False, and `similarity_trajectory_exact` is its **only** False check. This half of the claim holds.
- The "because of an extra blank column" half does not hold. See W4.

## Findings / notes (non-blocking)
- **W1 (wording, optional). ERRATA_2026-10-28.md:253.** "within the noise of the 1e-8 finite-difference Jacobian" is slightly stronger than what has been shown: same order of magnitude, with no re-run at another perturbation step. "at the scale of" would be exact. The two-sided scatter in §1 does support the reading. No change required.
- **W2 (wording nit). ERRATA_2026-10-28.md:288.** "full values of order 1e-7" fits the standard deviation (√1.48e-14 ≈ 1.2e-7) and the maximum (5.2e-7). The median |full_s2_minus_s7| is 4.1e-10, though, so "median 339 against full values of order 1e-7" compares a median with a spread. It is harmless.
- **W3 (merge note incomplete). ERRATA_2026-10-28.md:314–317.** `git merge-tree 340e5b5 origin/fix/comparator-v4-gates` (f0aadce) conflicts in **four** files, not only at the end of ERRATA:
  - `registry/artifacts_current.csv` (regenerate it)
  - `tools/redteam/REDTEAM.md` (add/add)
  - `tools/redteam/test_rt_comparator.py` (add/add)

  The cause: each branch cherry-picked the red-team suite separately (52f5c92 here, 0ed36da there), and comparator-v4 then edited those two files. This was already true at 6d180dd. Suggest the PR description or the merge note say:
  - take comparator-v4's `test_rt_comparator.py`
  - merge both REDTEAM.md additions
  - rebuild the inventory
- **W4 (side note's causal claim is wrong).** The `*_max_diff` column is added *because* a key failed (`AIEF_1_4_matched_phase_memory_ablation.py:796–800`); it is not the reason for the failure. Its value is blank (NaN) for full_reset even though the code always assigns it on failure. NaN entries are replaced with 0 before the diff, so a NaN max_diff can only come from inf − inf, meaning matching ±inf entries. So the diagnostic hides the real mismatch, which could be a finite-value difference, a NaN-mask mismatch, or a dtype difference (L349–370). The cause of this anchor failure is still unexplained. This is pre-existing and outside this branch.
- N5 (the GAP skip that exits rc 0) and N6 (the b2a95 SHA256SUMS entry for an uncommitted log) are still open, as before. Both are pre-existing.
