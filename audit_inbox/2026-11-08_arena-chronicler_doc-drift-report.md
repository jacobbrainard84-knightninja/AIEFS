# Doc-drift report: the memory documents no longer describe `main`

- **Agent / model:** Arena agent, "Arena Chronicler" seat (documentation-maintenance role, not a research or audit seat)
- **Date:** 2026-11-08, 22:35–23:00 UTC
- **Repo commit / branch reviewed:** `origin/main` @ `eb3933c` (2026-11-08 19:36 UTC, merge of PR #12); live branch tips retrieved the same window; work done on `arena/eae4f5a6-aiefs`
- **Scope:** every instructional and status document on `main`, plus the `audit_inbox/briefing/` set; hash-pin manifests; `registry/claims.csv` against the CI-parsed status vocabulary; the live branch/PR state
- **Status:** **UNVERIFIED INPUT** (per `audit_inbox/README.md`). Nothing here is a finding until Researcher 001 / Auditor Seat 002 triage it. I changed no claim, no status and no pinned byte.

---

## 1. Summary

This note is two things.

1. **A maintenance agent, with tooling**, whose only job is to keep the repository's memory, instruction and introduction documents true — and to be driven by the single word **continue**.
2. **The evidence from its first run**, which shows that several documents describe a project state that is now wrong.

The drift is not cosmetic. Three documents still describe the freezing theorem as living only on a research branch. It was merged into `main` on **2026-11-06** (PR #3, merge `2e55eb5`). One of them, `CURRENT_STATUS.md` — which declares itself *the single status file* — carries a **2026-10-23** stamp and cites three scripts and one directory that no longer exist in the tree.

Nothing in this deposit touches `main`. Every recommendation is for the document's owner to land.

---

## 2. What was built

| Artifact | Where | What it is |
|---|---|---|
| Agent charter + workstation | `PROJECT_CHRONICLER_AGENT.md` (repo root, not in this folder) | The copy/paste agent: role, authority order, the **continue contract**, editing routes, grounding rules, failure modes |
| Drift toolkit | `chronicler/` (repo root, and a runnable copy in `2026-11-08_arena-chronicler_project-chronicler/scripts/`) | `collect` → `check` → `tick`; 21 rules with stable ids; 31 unit tests |
| Found-by-the-tool evidence | `2026-11-08_arena-chronicler_project-chronicler/evidence/` | `findings.csv`, `findings.txt`, `snapshot_summary.json`, this run's commands and test log |
| Per-document update proposals | `2026-11-08_arena-chronicler_project-chronicler/recommendations/` | Prioritised list, a proposed replacement branch table for `STATE.md`, and a re-verification checklist for `CURRENT_STATUS.md` |
| Handoff | `2026-11-08_arena-chronicler_project-chronicler/HANDOFF.md` | How another agent runs it, resumes the loop, or takes over a recommendation |

Why tooling and not just an agent: an agent asked to "keep the docs up to date" invents a plausible state and writes confident prose about it. The rules here read git objects and the documents' own bytes. Where a rule cannot know, it stays silent — a shallow clone suppresses citation checks, no network suppresses branch-tip checks, planned files are not reported as missing. The design goal is that the agent can trust the tool.

---

## 3. Findings that the owner can act on now

All line numbers are against `origin/main` @ `eb3933c`.

### 3.1 Documents are stale against merged work (highest value)

| Document | Line | Says | Reality |
|---|---|---|---|
| `audit_inbox/briefing/STATE.md` | 13 | `` `main` \| `395ea53` `` | `main` is `eb3933c`; nine PRs (#3,#4,#5,#7-#12) have merged since |
| `audit_inbox/briefing/STATE.md` | 15–23 | PR #3/#4/#5 and four fix branches are "**Not merged**" / "awaiting the owner" | PRs #3,#4,#5,#7,#8,#9,#10,#11,#12 all **MERGED** on GitHub. Four quoted tips have moved; six branches the table lists no longer exist on origin (three deleted after merge) |
| `audit_inbox/briefing/STATE.md` | 66 | "`AIEFFreezeCore` … `required: false`, and that project is not on `main` yet" | `lean/AIEFFreezeCore` is on `main`, and `.github/workflows/lean.yml:49` lists it `required: true` |
| `audit_inbox/briefing/NORTH_STAR.md` | 66, 76, 81 | "AIEFFreezeCore is listed but not on `main` yet"; row 3 and the infrastructure row "PENDING, PR #3" | same, plus `registry/claims.csv` on `main` contains `LEAN-FREEZE-CORE`, `RES-FREEZE-GATED`, `RES-FREEZE-NUM`, `RES-FREEZE-NOVELTY` |
| `CURRENT_STATUS.md` | 127 | "conditional theorem (research branch `research/freezing`, 2026-10-29; not a repo audit round)" | `research/freezing/` is on `main` (21 files); the theorem merged 2026-11-06 |
| `CURRENT_STATUS.md` | 135 | "`LEAN-FREEZE-CORE` (Supported, Lean core, **branch only**)" | no longer branch-only |
| `CURRENT_STATUS.md` | 3 | "**Last Verified:** 2026-10-23" | `registry/claims.csv` last changed 2026-11-08, 17 days later |

Verification is recorded in `evidence/branch_and_pr_state.md`: live tips from `git ls-remote`, the PR table from the GitHub API, and the `main`-tree checks that prove the merge (`ls-tree` for `lean/AIEFFreezeCore` and `research/freezing/`, and the four ledger rows).

`CURRENT_STATUS.md` is now **verified end to end rather than restamped**, and the change is delivered as an
applicable patch: `2026-11-08_arena-chronicler_project-chronicler/recommendations/current_status_edits.patch`
(13 hunks, `git apply --check` clean against `eb3933c:CURRENT_STATUS.md`), with the full text in
`CURRENT_STATUS.proposed.md` and the verification record — the checks that came back clean, and the two
claims in my earlier notes that the evidence did not support — in
`recommendations/current_status_checklist.md` §G.

### 3.2 Dead pointers in a status document

`CURRENT_STATUS.md` cites paths that are absent from `main`:

- line 46: `` `aief_1_4_full_state_tangent_operator.py` ``, `` `aief_1_4_history_cocycle_test.py` ``,
  `` `aief_1_4_branch_tangent_comparison.py` ``, `` `aief_1_4_jacobian_step_convergence/` ``;
- line 47: `` `aief_1_4_k3_fiber_audit/` ``.

None of the five exists anywhere in `origin/main`'s 3,052 tracked files, and none appears in
`registry/artifacts.csv`, so they are not sitting inside one of the archived zips either. The ledger rows for
that work (`CF05`, `CF10`) name only "historical … manifest", so the row's evidence is not reachable from the
repository at all — a stronger finding than a renamed file.

This is the same defect Researcher 026 raised as `R026-S6` / `OPEN_QUESTIONS.md` item 13 (entrypoint integrity). It is still live on `main`.

**Correction (checked 2026-11-08):** an earlier draft of this section also listed line 11's `` `Papers/` ``.
That was wrong. Lines 10–11 say `main` *deleted* those files and then enumerate them; citing a deleted path
while saying it was deleted is not a dead pointer. The chronicler now skips path references on lines that
declare an absence (`ABSENCE_CONTEXT` in `checks.py`, with a test), and a regression test pins that the
filter does not swallow a filename that merely contains the word `missing`.

### 3.3 A CI contract worth guarding

`registry/README.md`'s `## Status vocabulary` fenced block is parsed by `tools/ci/lint_claims.py`. Editing it is a contract change, not prose. I checked it: **14 vocabulary values, 80 ledger rows, 0 unknown values** — consistent today. The tool now watches it (`VOCAB-*` rules), because a future doc edit that "tidies" that block would break CI and the ledger silently.

### 3.4 Pins are intact

29/29 hash-pinned files match, including the three pinned sources (`AI Agent Audits/evidence/audit_manifest.json`, `twindow_frozen_authority_hashes.txt`, the Lean source sums). `AI_AGENT_HANDOFF_PROMPT.md` is itself pinned, so it cannot be corrected in place — the tool flags it as advisory so an agent does not try.

---

## 4. Recommendation

1. **Researcher 001 owns the briefing.** Apply `recommendations/state_md_proposed_table.md` to `audit_inbox/briefing/STATE.md` and refresh `NORTH_STAR.md` lines 66/76/81. I did not edit them: your own rule is that their owner edits them.
2. **`CURRENT_STATUS.md`: the verification is done — apply the patch.** It is no longer a checklist. `recommendations/current_status_edits.patch` applies cleanly to `eb3933c` and changes 13 places: the stamp, three ledger-label/path corrections in §2, the missing freezing row, and §4's description of a branch that no longer exists. `current_status_checklist.md` §G says what was checked and came back clean, so you can reject any hunk without losing the audit trail. Bumping the stamp alone is still the one thing the agent charter calls fatal.
3. **Decide the maintenance loop's home.** The charter and toolkit are on `arena/eae4f5a6-aiefs`, `chronicler/` is not on `main`, and my session branch is fixed — so I cannot push to `audit-inbox` myself. The owner needs to carry this folder over, or merge the branch.
4. **Optional:** run `python -m chronicler check --fail-on high` as a non-blocking CI job so document drift is visible per PR instead of discovered weeks later.

---

## 5. What I did not do, and what the rules cannot see

- I did not modify, re-pin or "fix" any `main` document, claim row, errata entry or pinned file.
- I did not run the simulation or Lean suites; this is a documentation-and-metadata job.
- **Rules are pattern-based.** They catch stale dates, moved tips, dead paths, vocabulary drift and pin changes. They cannot catch a sentence that is grammatical, recently dated and simply no longer true — §3.1's `required: false` claim is exactly that. That class needs the periodic *deep sweep* the charter reserves for when the queue is empty.
- The clone used for the first run is **shallow** (5 commits), so citation checks against old shas were suppressed rather than guessed. A full-history clone will enable `DOC-SHA-UNREACHABLE`.

---

## 6. Reproduction

From a full clone, at the repo root:

```bash
git fetch origin
python3 -m chronicler status                            # document table, pins, queue
python3 -m chronicler check -v                           # all rules with evidence
python3 -m chronicler tick                               # writes chronicler/loop/NEXT.md
python3 -m unittest discover -s chronicler/tests -v      # 31 tests
```

Without the toolkit, regenerate this deposit's evidence from the runnable copy:

```bash
python3 audit_inbox/2026-11-08_arena-chronicler_project-chronicler/scripts/make_evidence.py
python3 -m unittest discover -s audit_inbox/2026-11-08_arena-chronicler_project-chronicler/scripts/chronicler/tests -v
```

---

## 7. Deposit contents

```text
audit_inbox/2026-11-08_arena-chronicler_doc-drift-report.md      <- this note
audit_inbox/2026-11-08_arena-chronicler_project-chronicler/
  README.md                    folder index and how to run the toolkit
  HANDOFF.md                   how to resume, or take over a recommendation
  scripts/chronicler/          runnable copy of the toolkit (stdlib only, 3.9+)
  scripts/make_evidence.py     regenerates everything in evidence/
  evidence/EVIDENCE.md         what was run, when, with what result
  evidence/findings.csv        8 findings, stable ids, evidence, recommended action
  evidence/findings.txt        same, human-readable
  evidence/snapshot_summary.json   refs, counts, pins, vocabulary, per-document table
  evidence/doc_inventory.md    every instructional document read, and what it constrains
  evidence/branch_and_pr_state.md  live tips, PR state, and the main-tree proofs
  evidence/tests.log           unittest output (31 passed)
  evidence/commands.log        exact commands and exit codes
  recommendations/RECOMMENDATIONS.md
  recommendations/state_md_proposed_table.md
  recommendations/current_status_checklist.md
```

No personal data is reproduced anywhere in this deposit: findings cite paths, lines and public commit shas only, and the snapshot redacts the local checkout path (`PRIVACY_SCRUB_LIST.md` P4).
