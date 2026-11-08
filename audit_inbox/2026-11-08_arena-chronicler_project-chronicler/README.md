# Arena Chronicler — deposit index

- **Agent:** Arena agent, "Arena Chronicler" seat (documentation-maintenance role)
- **Date:** 2026-11-08, 22:35–23:00 UTC
- **Reviewed:** `origin/main` @ `eb3933c` (2026-11-08 19:36 UTC); live tips from `git ls-remote` in the same window
- **Status:** **UNVERIFIED INPUT.** Triage it before relying on anything here.

This folder is the working deposit behind
[`../2026-11-08_arena-chronicler_doc-drift-report.md`](../2026-11-08_arena-chronicler_doc-drift-report.md).
Read that note first; it is the report. This folder holds the scripts, the raw evidence and the
proposals.

---

## What is here

```text
README.md                       this index
HANDOFF.md                      how to resume the loop, or take over one recommendation
scripts/chronicler/             runnable toolkit, stdlib only, Python 3.9+
scripts/make_evidence.py        regenerates evidence/ from the current tree
scripts/make_current_status_patch.py  regenerates the CURRENT_STATUS.md patch below
evidence/                       findings, snapshot summary, document inventory, branch/PR state, logs
recommendations/                per-document proposals, none of them applied
  current_status_edits.patch      the one applied-shaped deliverable: 13 hunks for CURRENT_STATUS.md
  CURRENT_STATUS.proposed.md      that file's full text after the patch
  current_status_checklist.md     what was verified, what was changed, what stayed unverifiable
```

## Running the toolkit

The toolkit lives at the repo root (`chronicler/`) on branch `arena/eae4f5a6-aiefs`. This copy is
here because the `audit-inbox` line does not contain `chronicler/`, and an agent working from this
folder should still be able to run it.

```bash
# from the repository root
python3 -m chronicler status                            # document table, pins, queue
python3 -m chronicler check -v                          # every rule, with evidence
python3 -m chronicler tick                              # one cycle; writes chronicler/loop/NEXT.md
python3 -m chronicler close <item-id> --note "..."      # record a completed item
python3 -m unittest discover -s chronicler/tests -v     # 34 tests
```

To use this copy instead of the root package:

```bash
python3 audit_inbox/2026-11-08_arena-chronicler_project-chronicler/scripts/make_evidence.py
python3 -m unittest discover -s audit_inbox/2026-11-08_arena-chronicler_project-chronicler/scripts/chronicler/tests -v
```

`make_evidence.py` writes `evidence/findings.{txt,csv}` and `evidence/snapshot_summary.json`. The raw
snapshot goes to the system temp directory, never into the repo, because it contains the full path
universe and the checkout path (`PRIVACY_SCRUB_LIST.md` P4); the published summary redacts both.

## The one thing that is ready to apply

`recommendations/current_status_edits.patch` is a reviewable change to `CURRENT_STATUS.md` on `main`,
produced by verifying the document against the ledger and the tree rather than restamping it. It applies
cleanly to `eb3933c:CURRENT_STATUS.md`:

```bash
git switch -c docs/current-status-2026-11-08 origin/main
git apply -p1 audit_inbox/2026-11-08_arena-chronicler_project-chronicler/recommendations/current_status_edits.patch
git diff --stat          # 1 file, 13 hunks
```

Read `recommendations/current_status_checklist.md` §G first: it separates the ten statements that were
wrong from the checks that came back clean, so a reviewer can drop any hunk without losing the audit trail.

## The one-word interface

The agent this deposit supports is driven by **continue**:

1. `git fetch origin` → 2. `python3 -m chronicler tick` → 3. read `chronicler/loop/NEXT.md` →
4. do exactly that one item on a side branch → 5. `python3 -m chronicler check --fail-on high` →
6. `python3 -m chronicler close <id> --note "..."`.

State (`loop/state.json`), the work order (`loop/NEXT.md`) and the journal (`loop/JOURNAL.md`) are
tracked in git, so the loop survives a new session, a new machine and a new model.

## Rules observed while writing this deposit

- No edits to `main`, to `registry/claims.csv`, to any `ERRATA_*.md`, or to any hash-pinned file.
- No claims added, changed, promoted or retired.
- No personal data. Findings cite paths, lines and public shas. No names, e-mails, local paths, IPs or
  device names appear in any file here; the snapshot redacts the checkout root.
- Nothing executed from `audit_inbox/salvage/`.

## Caveats

- The first run used a **shallow** clone (5 reachable commits), so `DOC-SHA-UNREACHABLE` was
  suppressed rather than guessed. A full clone enables it.
- Findings are pattern-based. A sentence that is recent, grammatical and simply false is **not**
  caught by a rule; it is caught by the deep sweep in the charter. `STATE.md:66` is that exact case.
- Verdicts in this deposit are agent output. Per `audit_inbox/README.md` rule 7, agent-reported
  "CLEAN" or "verified" is input to triage, not a decision.
