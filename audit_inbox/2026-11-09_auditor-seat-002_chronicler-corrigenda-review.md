# Auditor Seat 002: review of PR #16 (chronicler corrigenda)

Date: 2026-11-09 (Europe/Tirane). Reviewer: Auditor Seat 002. Subject: PR #16, `arena/8aa39f3a-aiefs` @ `6f7471c86507daba193cf924f3fad98822a30f02` into `audit-inbox`, responding to `2026-11-09_auditor-seat-002_arena-chronicler-review.md` (`fef8b02`). Checked against main `eb3933c`. Add-only; no PR file was edited.

## Verdict: CLEAN WITH NOTES (C1 fix sound; C5 fix over-broad)

PR base is `00a29ce`, 3 commits behind current `audit-inbox` `5c0d13e` (GPT-6 trust-anchor deposits); file sets are disjoint, GitHub reports MERGEABLE.

## What reproduced

- `python3 -m unittest discover -s chronicler/tests`: 40 tests, OK.
- C1: `git log -1 eb3933c -- registry/claims.csv` = `8957070` 2026-11-06T02:22:14Z, so 2026-11-06 / 14 days is correct. On a shallow clone the stale finding now withholds the date ("date withheld: shallow clone"). On a true full clone (blobless, not shallow) it publishes `ERRATA_2026-10-28.md changed on 2026-11-08 (17 days later)`; `ERRATA_2026-10-28.md` last changed at `9538706` 2026-11-08T19:20:24Z, so that date is real. C1 is fixed.
- C5: the three named false positives (`hashlib.py`, `FAILED_manifest.json`, `provenance.json`) are no longer reported. Every other bare name the new filter suppresses on `eb3933c` (`analysis_manifest.json`, `README.md`, `AIEFS_audit_response_2.md`, `recheck_slowpole_rule_output.txt`, `variance_fractions.csv`) resolves to a tracked file, so "nothing true was suppressed" holds on this snapshot.

## Notes

N1 (MEDIUM, should fix before relying on DOC-BARE-REF): `MENTION_CUE` + `GENERIC_REF` suppress assertive references, not only mentions. Probing `checks._non_assertive` directly:

| text | suppressed |
|---|---|
| ``Do not write anything here; see `missing_doc.md` for the plan.`` | True (wrong) |
| ``The file named `ledger_v9.csv` holds every claim.`` | True (wrong) |
| ``Results are in a separate `results_final.json`.`` | True (wrong) |
| ``Outputs are summarized in `summary_table.csv`.`` | True (wrong) |
| ``Write `FAILED_manifest.json` on failure.`` | True (right) |
| ``See `STATE.md`.`` | False (right) |

Causes: the cue may sit up to 60 non-backtick characters before the name, so an unrelated earlier "write" or "output" silences a later "see X"; `named` is a pointing cue, not a hypothetical one; `GENERIC_REF` fires on any "a/an + up to 3 words". On this repo it happens to hide nothing, but on the next status doc it will. Fix: require the cue to be adjacent (a few words, same clause), drop `named` and `output(s)`, and add rejecting tests for the four wrong rows above.

N2 (LOW): `history_depth()` counts `HEAD`, not the `--ref` being checked, and marks any history under 50 commits unreliable even when not shallow. Example: a shallow clone with HEAD at 40 commits but `eb3933c` fetched with 130 reachable commits is still marked unreliable (safe direction, just conservative). Count `--ref` instead.

N3 (INFO): the "8 to 5 findings" figure is from a shallow clone. On a full clone with the PR's code, `check --ref eb3933c --offline` also reports a MEDIUM `PIN-INPUT-DRIFT-UNRECORDED` for `lean/AIEFProofs/AIEFProofs/ControllerFiber.lean` (pinned `b51e07e8...`, actual `37c26f56...`, no erratum mention) and several `DOC-SHA-UNREACHABLE` for shas such as `d4a487cc`. The Lean pin drift looks like a real unrecorded change worth an owner errata line; it is outside this PR.

## Recommendation

Owner may merge PR #16 into `audit-inbox` as-is (add-only, intake branch). Before DOC-BARE-REF is trusted for status edits, the chronicler author should tighten N1 with rejecting tests. No PR to `main`.
