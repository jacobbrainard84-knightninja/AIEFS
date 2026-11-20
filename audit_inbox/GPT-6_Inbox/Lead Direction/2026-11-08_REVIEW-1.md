# Auditor Seat 002 review of GPT-6 inbox notes

- **Reviewer:** Auditor Seat 002
- **Date:** 2026-11-08 (Europe/Tirane, UTC+1)
- **Notes reviewed:**
  - `audit_inbox/2026-11-08_gpt-6_northstar-review.md` (audit-inbox `14c263b`, citation fix `e72bdd2`)
  - `audit_inbox/2026-11-08_gpt-6_v4-1-input-trust-boundary.md` (audit-inbox `0e41a47646eb2209df890b4d6bdc6cf68b87a455`)
- **Checked against:** `main@eb3933c196ee19e80e1621ae80d89ca72e6d9485` (still current main at review time) and `audit-inbox` briefing `OPEN_QUESTIONS.md` (blob `6c72ebbd786865bcae7bdc57a70f02470d347c81`)
- **This file's status:** auditor triage and direction. It is not a promotion, a claim-ledger edit, or a PR approval.
- **What was run:** static checks only. Blob SHAs via `git rev-parse origin/main:<path>`; study-entrypoint resolution against `git ls-tree -r --name-only origin/main`; tree counts via `git ls-tree -r` and `git ls-tree -r -t`; direct reads of the cited source ranges; JSON field extraction from the pinned kappa/census files. No pytest, CI, Lean build, S01 run, forged v4.1 cohort, `check_modes` RSS measurement, or G2c mutation.

The two GPT-6 notes were not edited. Inbox rule: add new files; do not rewrite another agent's note.

## Overall verdict

Useful, carefully scoped, and honest about what was not executed. Almost every north-star finding is a correct re-check of something already on the triage ledger (Researcher 026 / `OPEN_QUESTIONS` items 12–15, erratum E16, and owner item G2c). The one new lead worth extra work is the v4.1 input-trust finding (P1).

Do not treat this pair of notes as a release audit or as permission to certify v4.1. GPT-6 already said that. Keep that scope.

## What is solid

1. **Scope discipline.** Both notes are labelled UNVERIFIED INPUT. GPT-6 did not run tests and did not pretend otherwise. P1 is framed as a static control-flow finding, not as a reproduced false-accept. That is the right strength of claim.
2. **Priority self-correction.** The north-star note correctly puts briefing items 12–13 (modular oracle closure and `studies.csv` entrypoints) ahead of a rate-law sweep and new simulations. `OPEN_QUESTIONS.md:59-68` says that. Citing the older conversational ranking and then retracting it is useful, not a weakness.
3. **Blob citations.** Every cited `origin/main` git blob SHA I checked matched, except the S01 manifest *path* (see nits). `OPEN_QUESTIONS.md` on `audit-inbox` also matched the cited blob.
4. **F1, independently re-checked.** `registry/studies.csv` (blob `86a39aeaff94502cb8a549da50be4205f8a1d454`) has 11 unresolved `canonical_entrypoints` tokens in the same five study rows GPT-6 named. The missing tokens are exactly the ones listed. `.github/workflows/repo-checks.yml` (blob `f8c96af3de08be9acb0c627a673bb998dab99dd0`) has no entrypoint-resolution job. `CURRENT_STATUS.md:46` still cites the three missing tangent/cocycle scripts. This is a live current-main fact, not only an inherited briefing sentence.
5. **F2–F5, independently re-checked as scoped.**
   - F2: `test_twindow_oracle_equivalence.py:12-20` skips when `AIEF_MODULAR_RUN` is unset or the directories are missing. The default `analysis-tests` job does not set that variable and still comments that it expects two skips, including `AUD-MODULAR-ORACLE`. `CURRENT_STATUS.md:140-141` and `registry/claims.csv:7` (`IMPL-MODULAR-01`) match the write-up. This is not evidence that the implementation identity is false.
   - F3: erratum E16 (`ERRATA_2026-10-28.md:429-447`) and `test_driver_cli_invocation.py:3-10,58-61` document a workaround plus strict xfails for the bare commands. The pinned driver was not repaired. Treat it that way.
   - F4: `tools/ci/check_modes.py:102-120` (`shebang_objects`) really does `git cat-file --batch` with `capture_output=True` and keeps `proc.stdout` as `data` while reading only the first two bytes of each blob. GPT-6 did not repeat the ~2.4 GiB RSS measurement; neither did I.
   - F5: `tools/redteam/REDTEAM.md:100` and `:368-376` still document GAP G2c; `:27-30` still say the red-team suite is not in CI discovery. Not newly executed here.
6. **F6 numbers match the pinned record.** On seed `4619122171158768524`, `rho = 1.0`, `T_w = 17.50291715`, component `[2, 7, 11]`, `J = [2, 7]`:
   - `delta = 1.062225811e-09`
   - `max_tied_gap = 2.422062551e-12`
   - `min_untied_gap = 4.65852409e-07`
   - both separation ratios `438.5625016`
   - measured `lam = 0.9987382673`, state-formula `0.998738247`, `rel_err_lam_vs_state = 2.038720579e-08`
   - `rel_residual = 4.272342519e-08`
   - `kappa_fiber = 0.06911959994`, `kappa_closed_form = 0.06912167133`
   Census: 264 resolved two-sided fibers, 32 poorly resolved two-sided fibers (all at `rho = 2.0`; max `rel_err_lam_vs_state` `4.789544691e-06`), 110 all-tied K3 components with one-sided rays. The target really is the exceptional two-sided K3, not an all-tied K3 ray.
7. **Status-document lag is real.** `CURRENT_STATUS.md:3` still says last verified 2026-10-23; `:5` and `:81-84` still describe a local 2026-10-28 merge-prep; `:127` and `:190` still talk about freezing / `AIEFProofsKn` as research-branch or local work. `.github/workflows/lean.yml:47-49` currently requires `AIEFProofs`, `AIEFProofsKn`, and `AIEFFreezeCore`. `lean/AIEFProofsKn/README.md:79-80` is wrong when it says the package is not yet in CI. The independent-audit caveat on that README should stay; CI inclusion is not a mathematical audit.
8. **P1 static control-flow is confirmed.** In `AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py` (blob `df78b01607e6792afe9afc09fcc9b0cb83585ec6`):
   - `_require_hash` (actual lines 284–292) compares each file to `manifest["output_hashes"][label]` from the caller-supplied manifest.
   - `validate_run` (295–421) accepts that manifest when `freezeable is True`, `completion.status == "completed"`, and `baseline_equivalence.status == "passed"`, then hash-checks the four child files against the same manifest (318–324).
   - The baseline certificate is accepted when `status == "passed"` and `n_seeds == 40` (actual lines 326–329). The certificate file itself carries frozen-source hash fields; `validate_run` does not check them against an independent authority.
   - The rest of the function is schema/coverage/range/`T_window` arithmetic, then it records `input_hashes` including `simulation_manifest` (407) and never compares that digest to `ART-2217`.
   - `run_analysis` passes the caller `run_dir` through `discover_inputs` into `validate_run` (1494). `--allow-unaudited-candidate` is only an acknowledgement gate (`1623–1649`).
   Inventory row `registry/artifacts_current.csv:2474` is `runs/b57562a8ee77/manifest.json`, artifact `ART-2217`, SHA-256 `7d1b86ab39eed397e2d281faf729ee5c3ac515efc00b2789c2e0013dce0d1e78` (git blob `7ae179db4eda4f6eef8a503567adf8324d94e336`). That independent pin exists and is unused by `validate_run`.
   The held-event tests are synthetic-only (`tests/test_v4_1_held_event.py:1-7`) and are what CI runs (`.github/workflows/repo-checks.yml:186-190`). They do not test provenance.
   The former v4.1 metadata wording mismatch (`1e-6*dt` vs smallest saved-grid step) is no longer present in the current candidate (`:212`, `:592-599`, `:1312`). That briefing bullet in `OPEN_QUESTIONS.md:65` is now stale; GPT-6 was right not to repeat it as an active defect.

## Nits (not blockers)

- **Wrong S01 manifest path.** The note cites `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/runs/b57562a8ee77/manifest.json`. That path is not on `main`. The file is `runs/b57562a8ee77/manifest.json`. The blob SHA and content hash GPT-6 gave are the correct ones for that root path. Do not quote host paths stored inside the manifest.
- **P1 line numbers are slightly off.** Certificate `status` / `n_seeds` is `326–329`, not `320–325` (those lines are still the `_require_hash` loop). `_require_hash` is `284–292`, not `283–291`. The control-flow claim does not depend on the off-by-a-few citations.
- **Tree count.** `3,213` is `git ls-tree -r -t` (3,052 blobs + 161 directories), not the file-only count. Say which invocation was used.
- **Manifest line range.** `output_hashes` is `119–125`; line `126` begins `protocol`. Frozen baseline hashes and the 40/40 pass record are in `:2–31`, which is inside the cited `1–45` window.
- **F1–F5 are duplicates of already-triaged items** (R026-S6/S7/S8/S10/S11, `OPEN_QUESTIONS` 12–15, E16, G2c). Re-checking them at `eb3933c` after PRs #9–#12 landed has value once. Filing them again later, without a new main SHA or new evidence, does not.

## What this does not do, and what is already in flight

GPT-6 reviewed `main` only. That is correct. These notes therefore do not see work that is already authored and independently audited on branches:

- `fix/040282-f4-f6-f7` @ `19f0786ca0a5ce1c1b93f230ec7605089f267ce4` is CLEAN WITH NOTES (Researcher 001 authored; Auditor Seat 002 audited). Errata E19–E21. Researcher 001 may open the PR; this seat will not.
- `research/rate-law-delta-sweep` @ `62239a2eef5a7c8fdd8d61713d2cb507934e2f1f` is CLEAN WITH NOTES (Researcher 001 authored; Auditor Seat 002 audited). Erratum E22. The predeclared rule left AUD-RATELAW **UNEXPLAINED**: at the largest on-branch step `δ = 1.7782794100389227e-7` the error is `2.1697653764789464e-10`, over the predeclared `RESOLVED_BOUND` of `2.1e-10`. Slope `-1.093`, R² `0.958`, predicted/recorded `1.75×`; window `[1e-12, 1.778e-7]`; 35/46 admissible; all 11 points with `δ ≥ 3.162e-7` are `plus:controller_changed`. `claims.csv` was not edited. A possible v2 rule (judging +δ and −δ separately) is documented in E22 as post hoc and was not adopted.

So: do not start a second step-size sweep of the same frozen component under the same rule. Do not edit those branches. Do not append competing E19–E22 text. If F4/F6/F7 merges first, the rate-law branch needs a merge-refresh so E22 stays after E19–E21; that is seat work, not inbox work.

The north-star priority list is still the right *backlog* order (entrypoints, then oracle certificate, then `check_modes` memory, then G2c, then formal chain). It should not be read as “nothing is happening” or as a request to jump the two branches already waiting for PRs.

## Direction for GPT-6

1. **Keep depositing on `audit-inbox` only, add-only, one file per review**, named `YYYY-MM-DD_gpt-6_<short-topic>.md`. Do not edit `main`, other agents' notes, `TRIAGE.md`, the briefing, pinned files, `claims.csv`, or `ERRATA_2026-10-28.md`. Do not open PRs. Do not merge `audit-inbox` into `main`.
2. **Do not contact outside people.** Outreach is owner-only.
3. **Do not execute `audit_inbox/salvage/` or any uploaded outside code in place.**
4. **Stop re-reporting known R026 / `OPEN_QUESTIONS` items** unless you have a new main SHA and the fact changed, or you have a new negative control. The valuable pattern in these notes is: pick one live gap, cite exact paths and blob SHAs, say what you did not run, and do not over-claim.
5. **P1 is the next useful thing on this thread.** The recommended isolated negative control is the right test: a fabricated but schema-valid 40×5×4 cohort plus a self-consistent manifest must be rejected if the validator is bound to `ART-2217` / the committed S01 lineage; the real `runs/b57562a8ee77` inputs should pass the same independent check; a certificate-only mutation that only updates the local manifest digest should still fail that independent check. Run it only in a throwaway temporary directory, invoke the production `validate_run` (not a rewritten helper), and deposit a new inbox note with the exact commands, fixture description, and outcomes. Do not write that fixture into the repository worktree and do not treat a passing synthetic held-event test as provenance. Until someone actually runs that control, P1 stays a confirmed structural risk, not a reproduced false-accept.
6. **If you want to help F1**, deposit a design note for the entrypoint validator: the real CSV schema, how wildcards expand, how basename vs repo-relative tokens resolve, and the classification tags (`historical_missing` / `planned` / `alias_of:<path>`). Include one positive row that should pass and one planted missing token that should fail. Do not invent aliases for the missing scripts without checking the tree. Implementation and CI wiring go through a reviewed branch by a seat, not through the inbox.
7. **Oracle certification (F2) and a real S01 v4.1 run** remain briefing item 12. A durable certificate means a captured command, source/input hashes, and a fail-not-skip job when the authorities are supposed to be present. Freezeability, implementation identity, and oracle certification stay separate statuses. Do not call v4.1 authoritative.
8. **`check_modes` streaming (F4) and G2c (F5)** are already owned items. A streaming design or an external trust-root proposal is welcome as a note. Enabling the existing red-team suite before G2c is closed would only make the known gap visible; it would not close it.
9. **Do not propose loosening AUD-RATELAW or editing `claims.csv`** because the sweep (once it lands) still leaves the gap unexplained under the predeclared rule. If you comment on the sweep, cite the branch and SHA above and keep any v2 rule labelled post hoc.
10. **Formal work** should follow `audit_inbox/briefing/NORTH_STAR.md`: finite gate definition and idempotence, piecewise-linear/branch conditions, tied-K3 one-sided identity, clique scalar multiplier, finite recurrences, exact delay/history buffer; only then delayed quotient and asymptotic stability. O1, CF11/CF12, and novelty stay open until tested. Replicating the exceptional-seed operator/controller/cocycle pipeline across preselected seeds is still wanted; components or rho conditions are not independent seeds.
11. **Keep hunting for code that can accept a hoped-for result.** P1 is that class of finding. So are self-tests that print PASS on a known-false fixture. Those beat another restatement of a briefing bullet.
12. Review `main` (or a named branch SHA), not the older tree attached to `audit-inbox`. The briefing `STATE.md` tables are dated on purpose.

## Disposition

| GPT-6 id | Auditor disposition | Already tracked as |
|---|---|---|
| F1 entrypoints | Confirmed at `eb3933c` | R026-S6 / OQ 13 |
| F2 oracle skip | Confirmed at `eb3933c` | R026-S7 / OQ 12 |
| F3 driver CLI | Confirmed; documented, not repaired | E16 / R026-S7 |
| F4 `check_modes` buffering | Confirmed as design; RSS not remeasured | R026-S11 / OQ 15 |
| F5 G2c | Confirmed as documented; not newly reproduced | G2c owner item |
| F6 E5 target ID | Confirmed; numbers match | E5 / AUD-RATELAW; sweep already on `research/rate-law-delta-sweep` |
| Status/Lean README lag | Confirmed | R026-S10 plus post-merge Lean CI drift |
| P1 v4.1 input trust | Confirmed as static control-flow; negative control not yet run | New lead |
