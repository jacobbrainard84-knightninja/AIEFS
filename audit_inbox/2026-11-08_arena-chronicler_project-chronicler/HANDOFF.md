# Handoff — how to pick this up

For another agent, or for the owner. Two ways in: **resume the loop**, or **take one recommendation**.

Read first: `../2026-11-08_arena-chronicler_doc-drift-report.md`. This file is the operating manual for
the deposit, not the report.

---

## A. Resume the maintenance loop

The loop is a state machine in git, so it does not depend on any chat history.

```bash
git fetch origin
python3 -m chronicler status        # where the documents stand
python3 -m chronicler tick          # one cycle: facts -> findings -> queue -> NEXT.md
cat chronicler/loop/NEXT.md         # the current work order
```

At the time of writing `loop/NEXT.md` had finished the `CURRENT_STATUS.md` item (`14d13939a8`,
`DOC-STALE-VS-SOURCE`): the file was verified and delivered as an applicable patch,
`recommendations/current_status_edits.patch`. Run `python3 -m chronicler queue` for the live list
rather than trusting a count written here.

After doing the item:

```bash
python3 -m chronicler check --fail-on high
python3 -m chronicler close <item-id> --note "what changed and how it was verified"
python3 -m chronicler tick          # advances to the next item
```

Rules the loop enforces, and that you should not work around:

- **one item per cycle, one finding per commit** — unreviewable diffs are the failure mode;
- an item left `in_progress` is **resumed**, not skipped;
- `close` without a real verification is a false record; `defer` with a reason is fine;
- if a finding reappears after being closed, the item reopens — that is a regression, treat it as one.

## B. Take over one recommendation

`recommendations/RECOMMENDATIONS.md` has R1–R9 with owner and route. Each is independent.

| If you are… | Take |
|---|---|
| Researcher 001 | **R1** (`STATE.md` table + Lean paragraph) and **R3** (`NORTH_STAR.md`, three lines) |
| the owner | **R2** (`CURRENT_STATUS.md`), **R4** (architecture counts), **R5** (`README.md`), **R7** (where the loop lives) |
| a coding agent | **R6** (one clause), **R8** (optional CI job), **R9** (the Lean-matrix rule) |

For each: make the smallest correct edit, cite the evidence file, and do not restamp a document whose
content you did not re-read.

## C. What is safe to touch, and what is not

**Safe**
- The deposit folder itself.
- `CURRENT_STATUS.md`, `README.md`, `docs/**`, the prompt documents — on a side branch, with a PR.
- `audit_inbox/briefing/*` — **only Researcher 001**; I left these untouched on purpose.

**Not safe, ever**
- `registry/claims.csv` by hand (use `registry/reconciliation/build_claims_reconciliation.py`).
- `ERRATA_2026-10-28.md` — append only; never renumber.
- Any hash-pinned file: `AI Agent Audits/evidence/audit_manifest.json` inputs (`AI_AGENT_HANDOFF_PROMPT.md`,
  `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md`, `AIEF_1_3_falsification_updated.py`, `aief_experiment_engine_v1.py`,
  `runs/5a9f093a2fe0/*`, …), `twindow_*hashes*.txt`, and the Lean source sums. A correction goes in
  the errata file; only the owner can authorise a re-pin.
- `lean/AIEFProofs/*` core proofs and `.github/` without the owner.
- Anything under `audit_inbox/salvage/` — never merge, never execute in place.

## D. Current facts you can rely on (and where they came from)

| Fact | Evidence |
|---|---|
| `main` is `eb3933c`, merge of PR #12 | `evidence/branch_and_pr_state.md` |
| 11 PRs merged in total (#1–#5, #7–#12); #6 and #13 closed unmerged | `gh pr list --state all` |
| 29/29 hash pins match | `evidence/snapshot_summary.json` |
| Status vocabulary: 14 values, 80 ledger rows, 0 unknown | `evidence/snapshot_summary.json` |
| 3,052 tracked files at `eb3933c` | `evidence/snapshot_summary.json` |
| `AIEFFreezeCore` is on `main` and `required: true` | `evidence/branch_and_pr_state.md` §Proof |
| 8 findings, 2 high | `evidence/findings.csv` |
| 34 tests pass on the deposited copy | `evidence/tests.txt` |

Everything above decays. Re-run the script rather than quoting it after a week.

## E. Known limits of the toolkit

- Pattern-based rules miss semantic drift. `STATE.md:66` ("`required: false`, not on `main` yet") is
  true-looking, recently stamped prose that no rule can refute. That is what the **deep sweep** is for
  (`tick` selects one when the queue is empty). See R9.
- In a shallow clone, `DOC-SHA-UNREACHABLE` is suppressed. Fetch full history to enable it.
- Without network, branch-tip rules are skipped and the report says so.
- The manifest covers 15 documents. Anything else is unmaintained by definition; adding one is a
  one-line manifest edit.

## F. If you disagree with something here

Good — say so in your own dated file in `audit_inbox/`, cite `path@sha:line`, and mark whether you ran
it or only read it. This deposit is UNVERIFIED input; it is a lead, not a verdict. Do not edit this
folder in place; add a new note that supersedes it.

## G. Attribution and outreach

No outreach was made and none should be. Do not contact any author, maintainer or project named in
`RESEARCH_LEADS.md` or elsewhere; that is the owner's call alone.
