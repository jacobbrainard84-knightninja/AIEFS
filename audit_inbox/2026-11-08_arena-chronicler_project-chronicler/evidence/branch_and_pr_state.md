# Branch and PR state at retrieval

- Retrieved: **2026-11-08 22:46 UTC** with `git ls-remote --heads origin`
- Review ref: `origin/main` @ `eb3933c`
- Branch tips move. Re-run this script rather than quoting these numbers later.

## Live branches on origin

| Branch | Tip |
|---|---|
| `arena/d4a487cc-aiefs` | `2af3859` |
| `audit-inbox` | `e72bdd2` |
| `ci/check-sha256sums` | `aababfe` |
| `fix/040282-f4-f6-f7` | `19f0786` |
| `fix/check-manifest-g1g2` | `13a01d1` |
| `fix/comparator-v4-from-main` | `c0fc70b` |
| `fix/comparator-v4-gates` | `902abe8` |
| `fix/lint-claims-combined` | `382ccdb` |
| `fix/manifest-nonempty` | `92993eb` |
| `fix/r026-cleanup` | `9538706` |
| `fix/upload-new-f1f2` | `9229817` |
| `main` | `eb3933c` |
| `research/aiefs-northstar-evaluation` | `003522e` |
| `research/rate-law-delta-sweep` | `62239a2` |

14 branches at retrieval.

## Pull requests (GitHub API)

| # | State | Head → base | Merged | Merge commit | Title |
|---|---|---|---|---|---|
| #1 | MERGED | `integration/round5` → `main` | 2026-10-31 01:38:00 | `ddc9f46` | Round 5 integration (nanfix-v2 + validator/Lean matrix + lean-kn + R02 |
| #2 | MERGED | `fix/hygiene-allow-data-external` → `main` | 2026-10-31 13:38:19 | `395ea53` | CI: allow third-party datasets under data/external/ in the hygiene sca |
| #3 | MERGED | `research/freezing` → `main` | 2026-11-06 02:38:01 | `2e55eb5` | Freezing theorem: 4-row claim split, Corollary 4 fix, novelty rescope |
| #4 | MERGED | `research/redteam-negcontrols` → `main` | 2026-11-01 07:33:07 | `37deb7d` | Red-team negative-control suite (step 1 of checker fixes) |
| #5 | MERGED | `fix/errata-old-files-drift` → `main` | 2026-11-06 02:20:42 | `7c7032f` | E15: document loosened SUPPORTED rule in aief_1_4_augmented_spectrum ( |
| #6 | CLOSED | `fix/corr-0995-scope-main` → `main` | — | `—` | Docs: scope Corr_physical ~0.995 to hand-picked frequencies |
| #7 | MERGED | `fix/lint-claims-combined` → `main` | 2026-11-07 06:46:56 | `58d5543` | lint_claims: fail-closed CSV checks and artifact resolution |
| #8 | MERGED | `fix/comparator-v4-from-main` → `main` | 2026-11-07 07:42:32 | `ad58a46` | Comparator v4 / ERRATA E14: exact integer comparison and restored repr |
| #9 | MERGED | `fix/check-manifest-g1g2` → `main` | 2026-11-08 13:56:08 | `942f852` | Manifest checker: isolate the verifier and wrapper, and cover G1/G2 ga |
| #10 | MERGED | `fix/upload-new-f1f2` → `main` | 2026-11-08 18:48:41 | `3a5d0e2` | Protect upload_new.sh from overwriting ignored files and pushing unsaf |
| #11 | MERGED | `ci/check-sha256sums` → `main` | 2026-11-08 18:54:31 | `f3e3a57` | Checksum checker: verify every SHA256SUMS file and isolate the checker |
| #12 | MERGED | `fix/r026-cleanup` → `main` | 2026-11-08 19:36:14 | `eb3933c` | R026 cleanup: driver CLI erratum, v4.1 label fixes, and test_01.py rem |
| #13 | CLOSED | `research/aiefs-northstar-evaluation` → `main` | — | `—` | Research: AIEFS north-star evaluation and staged scientific plan |

## Briefing branch table vs live state

Rows parsed from `audit_inbox/briefing/STATE.md` on the working branch, compared with the tips above.

| Document says | Line | Quoted tip | Live tip | Status |
|---|---|---|---|---|
| `main` | 13 | `395ea53` | `eb3933c` | **moved** |
| `fix/hygiene-allow-data-external` | 14 | `c59eabc` | — | **branch deleted after merge** (PR #2, `395ea53`) |
| `research/freezing` | 15 | `f444401` | — | **branch deleted after merge** (PR #3, `2e55eb5`) |
| `research/redteam-negcontrols` | 16 | `a614451` | — | **branch deleted after merge** (PR #4, `37deb7d`) |
| `fix/comparator-v4-gates` | 17 | `f0aadce` | `902abe8` | **moved** |
| `fix/errata-old-files-drift` | 18 | `3645770` | — | **branch deleted after merge** (PR #5, `7c7032f`) |
| `fix/check-manifest-g1g2` | 19 | `14072c3` | `13a01d1` | **moved** |
| `fix/lint-claims-fail-closed` | 20 | `ad1470a` | — | **branch not present on origin** |
| `fix/lint-claims-artifacts` | 21 | `f495d1c` | — | **branch not present on origin** |
| `ci/check-sha256sums` | 23 | `7c3bbba` | `aababfe` | **moved** |
| `arena/d4a487cc-aiefs` | 24 | `2af3859` | `2af3859` | unchanged |

Not present on origin at retrieval: `fix/hygiene-allow-data-external`, `research/freezing`, `research/redteam-negcontrols`, `fix/errata-old-files-drift`, `fix/lint-claims-fail-closed`, `fix/lint-claims-artifacts`.

Present on origin but not in the briefing table: `audit-inbox`, `fix/040282-f4-f6-f7`, `fix/comparator-v4-from-main`, `fix/lint-claims-combined`, `fix/manifest-nonempty`, `fix/r026-cleanup`, `fix/upload-new-f1f2`, `research/aiefs-northstar-evaluation`, `research/rate-law-delta-sweep`.

## Proof that the merged work is on `main`

These are direct reads of the tree at the review ref, not inference from a PR title.

```text
$ lean/AIEFFreezeCore exists
lean/AIEFFreezeCore
lean/AIEFProofs
lean/AIEFProofsKn

$ research/freezing file count
21

$ freeze claim rows in ledger
LEAN-FREEZE-CORE RES-FREEZE-GATED RES-FREEZE-NOVELTY RES-FREEZE-NUM

$ errata headings present
## E12 ## E13 ## E14 ## E15 ## E16

$ lean.yml matrix rows
- { project: AIEFProofs,     script: check_lean.sh,        axiom_root: AIEFProofs,     required: true }
- { project: AIEFProofsKn,   script: check_lean_kn.sh,     axiom_root: AIEFProofsKn,   required: true  }
- { project: AIEFFreezeCore, script: check_lean_freeze.sh, axiom_root: AIEFFreezeCore, required: true  }

```

