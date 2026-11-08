# Merged-branch salvage: review notes that exist only in PR comments

- **Agent / model:** Grok Bot (executor subagent working for the repo owner)
- **Date:** 2026-10-31, America/Toronto (UTC-4)
- **Reviewed:** main `395ea535d939c594c51c85169859f09f65f360b5`; branches `audit/nanfix-v2` (`cbf2ae7`), `ci/artifact-pins` (`a64d90e`), `ci/validator-and-lean-matrix` (`249ea3f`), `fix/hygiene-allow-data-external` (`c59eabc`), `integration/round5` (`893e0b6`); PRs #1 and #2
- **Scope:** Before these five merged branches are deleted, I checked whether anything on them is missing from main.

**Status: UNVERIFIED INPUT** (see `audit_inbox/README.md`). Below are two audit comments, copied word for word. They are the only material I found that is not already in the repository tree.

## Result of the branch search

- All five branch tips are ancestors of main (0 commits ahead). Their 54 commits stay reachable from main after the branches are deleted, so no history is lost.
- Every file version from those commits was compared with the tree at main `395ea53`. Only one path is missing from main: `AI Agent Audits/evidence/Data from Superconductivity Found in Meteorites/bb24282657_1_1.tar`. In `62c40ca` it was moved, byte for byte (blob `3fbab363`), to `data/external/superconductivity_in_meteorites/`.
- The other older versions (CURRENT_STATUS, ERRATA, claims.csv, the reconciliation builder, lean_presence.sh, the workflows, and the tests) were replaced by newer versions on main. I spot-checked AUD-REPRO-B2A95, IMPL-MODULAR-01, research item (a) for K_n, and the lean_presence gate. The newer versions keep the content or say more.
- Not in the tree: the two audit comments by Researcher 001 below, which exist only as GitHub PR comments. Main's `lean/AIEFProofsKn/README.md` line 33 still says `KernelDimFormula` is "pending their audit". That audit was posted in PR #1 (verdict SOUND).

## Item 1: Researcher 001 audit of 0c8cad0 (KernelDimFormula)

Source: https://github.com/jacobbrainard84-knightninja/AIEFS/pull/1#issuecomment-6536420905 (posted 2026-10-30 20:22 America/Toronto)

Follow-up to check: update the "pending their audit" note in `lean/AIEFProofsKn/README.md` line 33, and update the LEAN-KN-01 evidence pointer to cite `finrank_ker_inc_eq_half`. This would go through a normal reviewed branch.

> **Researcher 001 audit of 0c8cad0 (KernelDimFormula, dim ker = n(n-3)/2): SOUND.** Audit comment only, not an approval; merging is the owner's call.
> 
> Checked at round5 head 893e0b6 (the file is unchanged since 0c8cad0; only check_lean_kn.sh's mode changed):
> - **Math:** for n ≥ 3, 2·C(n,2) = n(n−1), so 2(C(n,2) − n) = n(n−1) − 2n = n(n−3), and n(n−3) is even, so the ℕ floor division is exact. The ℕ truncated-subtraction steps are guarded by `3 ≤ n` (n = k+3 substitution). `finrank_ker_inc_eq_half` just rewrites `finrank_ker_inc_eq_choose` with `choose_two_sub_eq`, so it adds no new hypotheses. The n < 3 note in the docstring is accurate.
> - **Build:** compiled independently against a project with identical pins (CompleteGraphKn 56547e74…, IncMatrixRank 1d610de8…, CompleteGraphRightInverse 85f1d119…, lake-manifest 3c274000…): exit 0, no warnings, no `sorry`/`admit`/`axiom`.
> - **Axioms:** `finrank_ker_inc_eq_half` and `choose_two_sub_eq` depend only on [propext, Classical.choice, Quot.sound].
> - **Pins:** `sha256sum -c AIEF_LEAN_KN_SOURCE_SHA256SUMS.txt` at 893e0b6 gives all 9 files OK; no repository pin list touched.
> - **Ledger:** LEAN-KN-01's `= n(n−3)/2` wording is now formally covered (previously only the C(n,2) − n form was proved). The row's evidence pointer can cite `finrank_ker_inc_eq_half` in a later ledger update. Not blocking.
> 
> Authorship is correctly labeled as the merge-prep agent, not Researcher 001, so this is an independent check.

## Item 2: Researcher 001 audit of PR #2 @ c59eabc

Source: https://github.com/jacobbrainard84-knightninja/AIEFS/pull/2#issuecomment-6537507570 (posted 2026-10-30 22:00 America/Toronto)

Open follow-ups from these notes: (1) a check that every `data/external/*` subfolder has a `SOURCE.md`; (2) `hygiene_scan.py --strict` can't be turned on until the 3 large CSVs are handled; (3) set `AIEFFreezeCore` to `required: true` when freezing lands.

> **Researcher 001 audit of PR #2 @ c59eabc: CLEAN WITH NOTES.** Audit comment only, not an approval; merging is the owner's call.
> 
> Checked against main ddc9f46 (2 commits, 4 files, +9/−9):
> - **hygiene_allow.txt:** adds `data/external/`. A full-tree `hygiene_scan.py` on the PR tree gives 0 errors and 3 warnings, all pre-existing >50 MiB CSVs, so it PASSES. NEW_BINARY for the meteorite tar is gone.
> - **lean.yml:** `pull_request:` now has no paths filter (null value, valid; it triggers on every PR). The push filter is unchanged. This is needed so the 3 required `lean (...)` contexts report on every PR. AIEFFreezeCore is still `required: false` and its job reports success with a skip warning while the directory is absent, so requiring that context doesn't block merges. Flip it to true with freezing, as planned.
> - **test_lean_presence.py:** the guard now expects 1 filter entry and asserts no `pull_request` paths filter. `unittest discover tools/ci/tests` runs 103 tests: OK.
> - **artifacts_current.csv:** all 3 changed rows match my sha256 of the PR files (894d98ce…, 64d77b3f…, fc0ecacd…).
> 
> Notes (non-blocking):
> 1. The allow-list covers the whole `data/external/` folder, so any future binary there passes without a SOURCE.md. Consider a small check later that every subfolder of `data/external/` has a SOURCE.md.
> 2. `hygiene_scan.py --strict` would FAIL on the 3 pre-existing big CSVs. That's fine because CI runs it non-strict, but strict mode can't be turned on for this scan until those files are handled.
