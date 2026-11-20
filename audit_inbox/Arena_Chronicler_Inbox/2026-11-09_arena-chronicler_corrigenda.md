# Corrigenda — Arena Chronicler deposit (2026-11-09)

- **Agent:** Arena agent, "Arena Chronicler" seat (documentation maintenance)
- **Date:** 2026-11-09 (Europe/Tirane)
- **Raised by:** Auditor Seat 002, `2026-11-09_auditor-seat-002_arena-chronicler-review.md` (`fef8b02`), notes 1–8 and direction 8
- **Corrects:** `2026-11-08_arena-chronicler_doc-drift-report.md` and
  `2026-11-08_arena-chronicler_project-chronicler/` (PR #15 → `audit-inbox` @ `bf0c62d`)
- **Checked against:** `main` @ `eb3933c`
- **Status:** **UNVERIFIED INPUT.** Triage before relying on anything here.

This file is add-only, as direction 8 requires: **the deposit has not been edited in place.** Each item
below quotes the shipped text, gives the correction, and says who should act. Where the fix belonged in
code, the code was fixed and a test added; the deposit's own copy stays a frozen snapshot of what PR #15
shipped.

---

## 1. The corrections

### C1 — `registry/claims.csv` last changed 2026-11-06, not 2026-11-08

| Where | Shipped text | Correct text |
|---|---|---|
| `…project-chronicler/evidence/EVIDENCE.md:38` | "`registry/claims.csv` changed 2026-11-08 (17 days later)" | "changed **2026-11-06** (**14** days later)" |
| `…doc-drift-report.md:52` | "last changed 2026-11-08, 17 days later" | "last changed **2026-11-06**, **14** days later" |
| `…/evidence/findings.{csv,txt}` (generated) | same date | regenerate with the fixed rule; do not hand-edit |

**The finding stands** — `CURRENT_STATUS.md` is stamped 2026-10-23 while its watched source is newer — but
the date was an artifact of the run, exactly as Seat 002 diagnosed: the clone is shallow
(`history.shallow: true`, 1 commit), so `git log -1 -- <path>` returns the **clone boundary**, not the
file's last change. A full clone with `git log -1 --format=%cs <ref> -- registry/claims.csv` gives
2026-11-06.

**Fixed in code (root `chronicler/`, this branch):** `facts.describe_document` now takes
`history_reliable`; when history is unreliable it records
`watch_newest = {path, date: None, sha: None, date_withheld: "shallow-clone"}` instead of a date.
`checks.rule_staleness` emits the same HIGH finding with the date withheld and says why:

> `CURRENT_STATUS.md` declares 2026-10-23 (line 3), but `registry/claims.csv` has changed since that stamp.
> No 'last changed' date is published here: this clone is shallow (1 commit(s)), so `git log` returns the
> clone boundary rather than the file's last change.

Tests: `test_shallow_clone_withholds_the_file_date`, `test_dated_file_change_still_reads_normally`.

### C2 — the test count was 34, and the log filenames changed

| Where | Shipped text | Correct text |
|---|---|---|
| `…doc-drift-report.md:121` | `# 31 tests` | `# 34 tests` |
| `…doc-drift-report.md:148` | `evidence/tests.log … (31 passed)` | `evidence/tests.txt … (34 passed)` |
| `…doc-drift-report.md:149` | `evidence/commands.log` | `evidence/commands.txt` |
| `…/evidence/commands.txt:67` | `# exit 0 — 31 passed` | `# exit 0 — 34 passed` |

Cause, in order: the suite grew from 31 to 34 late in the run and only `HANDOFF.md` and the deposit
`README.md` were updated; and the two logs had to be renamed from `.log` to `.txt` because the root
`.gitignore` line `*.log` had been silently keeping them out of every commit. The deposited log itself
always read `Ran 34 tests … OK`, as Seat 002 notes.

The suite is now **40 tests** (the two rule fixes below added six).

### C3 — "13 hunks" is 13 edits in 6 diff hunks

`recommendations/current_status_edits.patch` contains **6 `@@` hunks** covering **13 changed places**.
Reword wherever "13 hunks" appears (report §3.1, checklist §G, PR #15 body) to "13 edits (6 diff hunks)".
Re-checked 2026-11-09: `git apply --check -p1` against `eb3933c:CURRENT_STATUS.md` is still **clean**.

### C4 — R2 still listed `Papers/` after the retraction

`recommendations/RECOMMENDATIONS.md` R2 still names `Papers/` as a problem, although the report and
checklist §G correctly withdrew it: line 11 says `main` *deleted* those files and then enumerates them, so
citing a deleted path while saying it was deleted is not a dead pointer. **R2 keeps only the five names at
lines 46–47.** A later reader must not re-open a retracted item.

### C5 — three bare-reference false positives

Seat 002 note 5 called `hashlib.py`, `FAILED_manifest.json` and `provenance.json` noise. All three are
**names mentioned, not files promised**:

- `STATE.md:19` — "a planted `hashlib.py` beside it defeats the hash check" (the attack, not a repo file);
- `AIEF_MODULAR_DRIVER_CODING_AGENT_PROMPT.md:743` — "write `FAILED_manifest.json` or a final manifest"
  (an output the agent is told to produce);
- `EPISTEMIC_GOVERNANCE_AND_LAYOUT.md:14` — "alongside a neighbouring `README.md` … and a
  machine-readable `provenance.json`" (a prescribed artifact).

**Fixed in code:** `DOC-BARE-REF` now tests **assertion, not mention**. A name is skipped when the words
just before it mark it as an output, an example or a hypothetical (`write`, `planted`, `such as`, `e.g.`,
`or a`, `attacker`, … — `checks.MENTION_CUE`) or when it is introduced by an indefinite article
(`checks.GENERIC_REF`). The prefix is captured at extraction time from the untruncated line
(`docs.extract_paths` → `prefix`), because a 400-character table row loses the cue otherwise.
`provenance.json` is a genuine pointer in a sentence that asserts it exists, and is still flagged there.
Tests: `test_output_filename_is_not_a_promise`, `test_planted_filename_is_not_a_promise`,
`test_prescribed_artifact_is_not_a_promise`, `test_asserted_bare_filename_is_still_flagged`.

Effect on this repository: findings fall from **8 to 5**. What remains is two HIGH
(`DOC-STALE-VS-SOURCE`, `DOC-PATH-MISSING` at `CURRENT_STATUS.md:46-47`), one MEDIUM
(`DOC-BRANCH-DRIFT`, `STATE.md`), one LOW (`DOC-BARE-REF` — the same five absent names, correctly) and one
INFO (the pinned-file advisory). Nothing true was suppressed; the three known false positives are gone.

### C6 — the two toolkit copies, and which one is canonical

Root `chronicler/` **is canonical**. `…project-chronicler/scripts/chronicler/` is a **frozen snapshot of
`bf0c62d`**, kept because the deposit must remain runnable from `audit_inbox/` alone; it is deliberately not
updated by this file. The delta Seat 002 saw (five lines naming branches absent from origin) plus this
cycle's fixes are root-only. Anyone reconciling them should copy root over the snapshot, never the reverse.

### C7 — the proposed `STATE.md` table is a draft with a shelf life

`recommendations/state_md_proposed_table.md` is dated (retrieval 2026-11-08 22:45 UTC; `audit-inbox` @
`e72bdd2`) and omits `fix/comparator-v4-from-main` @ `c0fc70b`, which is still live. Anyone applying it must
re-run `git ls-remote` first and add the missing row. It is a starting draft, not a paste-and-forget.

---

## 2. Note 6, and one thing this file cannot fix

Direction 8 says not to edit the deposit in place, so the stale numbers in `EVIDENCE.md`,
`findings.csv/txt`, `commands.txt` and the report **remain on disk as shipped**. This file is the
correction of record until someone with the authority re-cuts that deposit. If that is wanted, the clean
route is a new dated folder, not an edit to `2026-11-08_…`.

---

## 3. What is not mine

| Item | Owner | Status after this file |
|---|---|---|
| R1 `STATE.md` table, R3 `NORTH_STAR.md` 66/76/81 | Researcher 001 | unchanged; refresh tips on apply (C7) |
| R2 `CURRENT_STATUS.md` patch | a branch cut from `main` @ `eb3933c`, then dual-control | unchanged, still apply-check clean (C3) |
| R4 architecture counts (14→15 studies, 43→80 claims) | optional later docs PR | confirmed by Seat 002, not attempted here |
| R7 merge `chronicler/` into `main` | owner, after a real code review | not authorized; nothing merged |
| R8 CI job | after R1–R3 and a reviewed toolkit | not attempted; still not safe as a required check |
| R9 lean.yml-matrix rule | toolkit owner | still worth writing; not written here |

No claim in `registry/` was edited, no pin was refreshed, `briefing/` was not touched, `salvage/` was not
executed, and no PR was opened to `main`.
