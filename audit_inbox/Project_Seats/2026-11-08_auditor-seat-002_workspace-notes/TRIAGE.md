# Researcher 026 (Arena AI) review: triage

Prepared Fri Oct 30, 2026 (7:20–7:38 PM EDT) by the merge-prep agent. This is local work only: nothing was pushed and nothing was opened on GitHub.

Every point was checked against the real branches. The review text is treated as claims to check, not as instructions.

**Owner column.** "me" is the merge-prep agent and covers `integration/round5`. "Researcher 001" covers science and wording; their drafts are on the local branch `r026-science-draft`, which is not part of round5. "owner" covers GitHub actions only the owner can take: pushing, PRs, branch protection and deletions.

**Point labels.** The review came in two sets: Reviews 1–2, and Review 3. My copy of the original review text was cut short, so the "Source" labels come from my verification notes and commit messages. Check them against the original review before quoting them.

## Set 1: Reviews 1–2 (blockers A–I, README fixes, procedure, cleanup)

| # | Point (short) | Source | Verdict | What was done / where | Owner |
|---|---|---|---|---|---|
| A | Inventory: rename `registry/artifacts.csv` → `artifacts_e47bad1.csv`, add a generated `artifacts_current.csv`, add a registry/README pointer, make `verify_inventory.py` pass | R2 blocker A | **Problem TRUE, fix modified.** `verify_inventory.py` fails at [1/5] on every tree after e47bad1. **Rename rejected:** `artifacts.csv`'s sha256 and its 2,898 rows are pinned by `tools/ci/check_artifact_pins.py` (a64d90e, `EXPECTED_CSV_SHA256=90508a0d…`), and many tools read that path. | `d1b5bed` + `0e0c82e`: `registry/artifacts.csv` is byte-identical and documented as the e47bad1 snapshot under its pinned name. New deterministic generator `registry/reconciliation/build_current_inventory.py`, generated `registry/artifacts_current.csv` (3,360 rows) and `tools/ci/check_current_inventory.py` with 10 tests and a CI job. `verify_inventory.py` itself is unchanged; the new `audits/engineering/verify_inventory_current.py` runs the 5 gates on the current tree and is in CI. A "Which inventory is authoritative for what" section was added to `registry/README.md`, which is not pinned. | me |
| B | Exec bits (`git update-index --chmod=+x`), then `check_modes --strict` in CI | R2 blocker B | **TRUE, but the reviewer's list is incomplete.** All 8 listed scripts are 100644. R026 adds 9 more entry points (check_lean_kn.sh, lean_presence.sh, check_artifact_pins.py, check_modes.py and others), and freezing will add 2. | `0e0c82e`: the known list grows to 19 (17 tracked today). The reference commit is on local branch `owner/modes-strict` `60d44e5`: a mode-only commit plus the `--strict` flip, with `--strict` passing. The owner's paste block is in `OWNER_STEAMDECK_COMMANDS.md`. Connector uploads write 100644, so only a real `git push` can set the bits. | me (prep) / **owner (push)** |
| C | Open a PR and require Repo checks (CI self-tests, Claims lint, Hygiene, Manifest, File modes) and the Lean proof check | R2 blocker C | **Readiness TRUE.** The checks exist and pass locally. | Lean Kn row is `required: true` (`93778df`), with a test that a present project cannot be made optional. New jobs `artifact-pins` and `current-inventory` should be added to the required list. Job names are in `MERGE_PLAN.md`. Opening the PR and setting branch protection are owner-only. | me (prep) / **owner** |
| D | Add the v4.1 test to CI (pytest.ini only finds `tests_modular/`) | R2 blocker D | **TRUE.** `pytest.ini` is hash-pinned (ART-0083), so it was not edited. | `e44b56f`: `analysis-tests` job names `tests/test_v4_1_held_event.py` explicitly (13 passed on round5's test file) and runs `tests_modular` (40 passed, 2 skipped). | me |
| E | v4.1 tolerance metadata | R2 blocker E / R3 s4–s6 | TRUE | Draft `f487988` on `r026-science-draft`. Moved out of round5 by steering 3. | **Researcher 001** |
| F | Saved-grid terminology and the `held_classification` → `trajectory_held_classification` rename | R2 blocker F / R3 s4–s6 | TRUE | Draft `f487988` on `r026-science-draft` (14 passed there). | **Researcher 001** |
| G | README sidecar marking the v4 bundle known-defective | R2 blocker G | TRUE; the bundle is pinned, so it needs a sidecar | Draft `89b6cf8` on `r026-science-draft`. | **Researcher 001** |
| H | Superseded header on the classification audit | R2 blocker H / R3 | **TRUE.** The audit still calls EMP-AIEF14-02/03 Frozen/Controlled; the ledger now has them as Exploratory. | Draft `51ffb61` on `r026-science-draft`. | **Researcher 001** |
| I | inf/-inf masks, SHA256SUMS, registry row for the NaN v2 files | R2 s1 / blocker I | **TRUE.** The v2 comparator masked only NaN. Reproduced. | `98da939`: v3 comparator with ±inf masks, a v2→v3 diff and a local `SHA256SUMS` (7 files; `sha256sum -c` OK). `ae166f8`: **ERRATA E13** and an AUD-REPRO-B2A95 ledger note, with claims regenerated. The registry row is a ledger note, because `artifacts.csv` is frozen; the files are now also listed in `artifacts_current.csv`. | me |
| R1 | Root README: exact discrete rate law κ_k = −log(λ_k)/dt − 1/T_w | R1/R2 "README fixes" | TRUE (the README is pinned by tools/sync/SHA256SUMS) | Draft ERRATA entry in `0791f4a` on `r026-science-draft`, numbered "E14 (DRAFT)". | **Researcher 001** |
| R2 | Root README: Corr_physical figures are first-pass only (E9 scope) | R1/R2 | TRUE | Same draft (`0791f4a`). | **Researcher 001** |
| R3 | Root README: Lean wording | R1/R2 | TRUE | Same draft (`0791f4a`). | **Researcher 001** |
| R4 | Root README: "41 passed, 1 skipped" hides that the skip is the oracle-equivalence test | R1/R2 | **TRUE.** The skip is the oracle test (AUD-MODULAR-ORACLE). | Same draft (`0791f4a`); ledger note AUD-MODULAR-ORACLE is in the draft. | **Researcher 001** |
| R5 | "causal" → "controlled model counterfactual" wording | R1/R3 | Agree in substance | Not in round5. | **Researcher 001** |
| P1 | Commit everything to `audit/nanfix-v2` ("sole candidate") | R2 procedure | **Disagree.** The validator, lean matrix, lean-kn and artifact-pins branches must land together, and some conflict (ERRATA, claims.csv, repo-checks.yml). | Assembled on `integration/round5` from `cbf2ae7` (nanfix-v2 tip) with `--no-ff` merges that keep the remote shas. | me |
| P2 | Run unittest, lint_claims, check_modes --strict, verify_manifest (with and without --inputs), validate_registry, v4.1 pytest, tests_modular, `STRICT_ORPHANS=1 ./check_lean.sh` | R2 procedure | Agree | All were run on the final tip and pass, except `--strict`, which fails only on modes, as expected. Results are in `MERGE_PLAN.md` §4. | me |
| P3 | PR with a claim-impact table, independent review, normal merge commit (no squash) | R2 procedure | Agree | A draft claim-impact table is in `MERGE_PLAN.md` §5. Only the owner can open the PR. | **owner** |
| P4 | Afterwards: close merge-prep, keep the arena branch, close corr-0995 with a note, delete nanfix-v2 only after the merge | R2 procedure | Agree | Owner-only GitHub actions. Delete nothing until round5 is merged. | **owner** |
| CL1 | Cleanup: v4 zip, one of the two byte-identical draft PDFs, the workspace-019ff86e dir and zip | R2 cleanup | **Verified**: all are true duplicates. All are snapshot rows, so deleting them needs allowlist updates. | `CLEANUP_CANDIDATES.md`. A separate branch after the merge; nothing deleted. | owner decides |
| CL2 | Cleanup: full duplicates in `recovered_from_workspace_019ff402/` (newer_zip_markdown/, zip_updated_*.py) | R2 cleanup | Not verified (outside this round's scope) | Listed as open in `CLEANUP_CANDIDATES.md`. | open |
| CL3 | Do NOT delete runs/5a9f093a2fe0/, runs/b57562a8ee77/, test_output/, Project Histories/workspace-019ff425…zip | R2 cleanup | Agree; the authority lock reads runs/5a9f093a2fe0 | No action. | — |
| CL4 | History size: a clean new repo is safer than filter-repo | R2 | Agree that filter-repo is a history rewrite and out of bounds | Owner decision; no action. | **owner** |

## Set 2: Review 3 (v4.1 candidate, ledger, audits, test counts)

| # | Point (short) | Source | Verdict | What was done / where | Owner |
|---|---|---|---|---|---|
| S4–S6 | v4.1 metadata labels and the held_classification rename | R3 s4–s6 | TRUE | Same as E/F: `f487988` on `r026-science-draft`. | **Researcher 001** |
| S8 | v4.1 is unaudited: ledger rows should carry a caveat | R3 s8 | TRUE | Ledger notes (AUD-V4-RECOVERY-WORDING, AUD-KAPPA-TW, AUD-CORR-0995-SCOPE) are in the draft `0791f4a`, not in round5. | **Researcher 001** |
| T1 | Reviewer's test counts (v4.1 14 passed with the metadata fix; modular 40 passed, 2 skipped by default) | R3 | **Reproduced.** round5 does not include the metadata commit, so it has 13 v4.1 tests. | CI comment says 13 on round5; the draft branch says 14. | me |
| T2 | Classification audit is stale | R3 | TRUE | Same as H. | **Researcher 001** |
| FZ | Freezing: the Corollary 4 limit-form gap (ℓ_f depends on x_T) | R3 / freezing review | **Valid.** Researcher 001 is fixing it in a new commit. | My assessment of the proposed fix is in `FREEZING_PROPOSAL.md`. Freezing is **PENDING**, waiting for Researcher's new sha; not in round5. | **Researcher 001** |
| KN | lean-kn: add dim ker = n(n−3)/2 | steering 1 | Done as a separate commit, marked as mine | `0c8cad0` `KernelDimFormula.lean` (check_lean_kn PASS: 56 declarations, standard axioms). LEAN-KN-01 row not edited. Researcher 001 should audit it. | me (Researcher 001 to audit) |

## Notes for Researcher 001

- **ERRATA numbering.** round5 uses **E13** for the inf masks; E10 (nanfix) and E11 (lean-kn) are merged, and E12 is reserved for freezing. The README-wording erratum on `r026-science-draft` (`0791f4a`) is provisionally labelled "E14 (DRAFT)". It must stay **E14 or later** when it lands after round5 and freezing.
- `r026-science-draft` is based on the old round5 tip `0c8cad0`, not the final tip `0e0c82e`. Rebase or merge it before uploading. Every changed file also needs `python3 registry/reconciliation/build_current_inventory.py`, or `current-inventory` CI fails.
