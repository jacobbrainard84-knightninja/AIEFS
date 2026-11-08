# `CURRENT_STATUS.md` — re-verification checklist

**This is not a "bump the date" task.** The file is stamped 2026-10-23 and `registry/claims.csv` has
changed since. The charter treats a date-only edit as a false claim of freshness — worse than a stale
date, because it hides the staleness.

Owner: the owner / Researcher 001. Reviewer: a seat that is not the author.

Everything below was read at `origin/main` @ `eb3933c` on 2026-11-08. Line numbers are that blob's.

---

## A. Statements that are now false (high confidence, evidence attached)

| Line | Statement | Why it is wrong | Evidence |
|---|---|---|---|
| 127 | "Topology freezing is a conditional theorem (research branch `research/freezing`, 2026-10-29; not a repo audit round)." | The branch merged into `main` on 2026-11-06. It is no longer "a research branch". | PR #3 merged, `2e55eb5`; `research/freezing/` has 21 files at `eb3933c` |
| 133 | Cites `research/freezing/audit/AUDIT_R002_d9c03ef.md` as the audit record | Path now resolves on `main`, so the sentence should say so rather than imply a side branch | same |
| 135 | "`LEAN-FREEZE-CORE` (Supported, Lean core, **branch only**)" | No longer branch-only | `registry/claims.csv` at `eb3933c` contains `LEAN-FREEZE-CORE` |
| 127–135 | Framing "not a repo audit round" | The 4 claim rows are now in the `main` ledger, i.e. it is a repo claim set | `git cat-file -p origin/main:registry/claims.csv \| grep -c FREEZE` → 4 distinct rows |

Suggested shape once checked (do not paste blindly; confirm each clause):

> **Topology freezing is a conditional theorem (on `main` since PR #3, merge `2e55eb5`, 2026-11-06;
> originally `research/freezing`, 2026-10-29).** …

and for the ledger rows: replace "(Supported, Lean core, branch only)" with "(Supported, Lean core)"
plus the merge sha.

## B. Dead pointers (mechanical, safe to fix)

| Line | Pointer | Status at `eb3933c` |
|---|---|---|
| 11 | `Papers/` | **Not a defect — checked 2026-11-08.** Lines 10–11 already say `main` *deleted* these 52 files, so citing `Papers/` there is correct. No edit; recorded so the next pass does not re-flag it. |
| 46 | `aief_1_4_full_state_tangent_operator.py` | not in the tree |
| 46 | `aief_1_4_history_cocycle_test.py` | not in the tree |
| 46 | `aief_1_4_branch_tangent_comparison.py` | not in the tree |
| 47 | `aief_1_4_k3_fiber_audit/` | not in the tree |

This is the unresolved half of **R026-S6** / `OPEN_QUESTIONS.md` item 13. Either point at the real
paths, or mark the artifacts `historical_missing` in the study row — do not delete the sentence.

## C. Counts to restate with a scope

The document's inventory table says 2,760 working-tree files / 2,898 inventoried objects. At
`eb3933c` the tracked-file count is **3,052**. Two acceptable fixes:

1. keep the numbers as the `e47bad1` snapshot and label them `at e47bad1` (they are about the frozen
   inventory, so this is probably correct); or
2. add the current count separately and date it.

Never present a moving count as a fixed fact.

## D. What must be re-checked before the stamp moves

Tick each one, or say in the PR that it was not re-run:

- [ ] §2 study table: every `artifact_status` / `evidence_scope` matches its `registry/claims.csv` row
      at the same sha.
- [ ] §2 pitfalls: every "do NOT confuse X with Y" still names files that exist.
- [ ] §3 status categories agree with `registry/README.md`'s three-category block.
- [ ] §4 been / are / going: "are" includes everything merged since 2026-10-23 (PRs #3–#5, #7–#12).
- [ ] Errata list mentions **E1–E18**, not E1–E13. At `eb3933c`: E14 (comparator v4), E15 (loosened SUPPORTED rule), E16 (modular driver CLI), E17 (v4 "interval-censored" label), E18 (root `test_01.py` removed, ART-2717 unchanged).
- [ ] Lean paragraph matches `.github/workflows/lean.yml`'s three required projects.
- [ ] Any claim labelled `PENDING` still is pending; anything merged is relabelled with its merge sha.

## E. Also update, in the same PR, if the "been / are / going" picture moves

- `README.md:8` — "Status of this README (2026-10-28)". Same test: re-read the scoped claims it makes,
  then restamp. Do not restamp alone.
- `registry/README.md` — its 2026-10-28 reconciliation note is still accurate about the `e47bad1`
  snapshot, so it may not need a change. Check the "Which inventory is authoritative" table against
  `tools/ci/*` first.

## F. Definition of done

- The file's claims are true at a cited sha, not merely newer.
- Every path it names resolves at that sha.
- The stamp date is the date of verification, and the commit message says what was verified and what
  was not.

---

## G. Result of the 2026-11-08 verification pass

**Status: verified, patch prepared, not landed.** `CURRENT_STATUS.md` is not in this branch's tree (the
branch carries the `audit-inbox` line), so the change is delivered as an applicable patch, not as an edit:

- `recommendations/current_status_edits.patch` — 13 hunks, `git apply -p1` clean against
  `eb3933c:CURRENT_STATUS.md` (checked in a scratch copy on 2026-11-08).
- `recommendations/CURRENT_STATUS.proposed.md` — the whole file after the patch.
- `scripts/make_current_status_patch.py` — regenerates both; it asserts each target string occurs exactly
  once and refuses to emit a patch if the source has moved.

### Verified true at `eb3933c`, left byte-identical

| Check | Result |
|---|---|
| §1 six-status totals | exact: Frozen 803 · Supported 490 · Exploratory 157 · Superseded 1422 · Rejected 15 · Incomplete 11 = 2,898 data rows |
| §1 worktree/zip split | exact and derivable: the `container` column gives worktree 2,760 and zip 138; per status 466+24 and 1,308+114 match the document |
| §2 evidence paths not named in §B | all resolve (`runs/c3da1ac707bf`, `runs/73dca37cf93f`, `runs/5a9f093a2fe0`, `runs/b57562a8ee77`, `runs_pivot_study/ebfec9a5c419`, `Older files/b57562a8ee77`, `test_output/`, `aief_1_4_intertwining_controller 02/`, `aief_1_4_feedback_rank_memory_reduction/`, `aief_1_4_matched_phase_memory_ablation/`, `Project Origins/`, `lean/AIEFProofsKn/`, the four `research/freezing/` paths) |
| §2 `cold` and `Frozen` audit wording | consistent with the 80 ledger rows read row by row |
| §3 retired/rejected scoping | consistent with the ledger (`S01–S18`, `REJ-*`, `AUD-SLOWPOLE`) |

### Corrected in the patch

| Hunk | Line | Change |
|---|---|---|
| 1 | 3 | stamp gains a scoped re-check clause that says what was verified and what was not |
| 2 | 44 | the claim that the vocabulary has no exploratory-design label is false (`Controlled exploratory` exists) |
| 3 | 45 | add the ledger's exact `audited_status` for `EMP-AIEF14-03` |
| 4 | 46 | four evidence paths are absent from the tree, and `CF05`/`CF10` carry only "historical … manifest" pointers |
| 5 | 47 | `aief_1_4_k3_fiber_audit/` is absent |
| 6 | 50 | §2 and §4 gave different test counts for one suite; `repo-checks.yml:195` fixes 43 passed, 2 skipped, 2 xfailed |
| 7 | after 48 | §2 had no row for the merged freezing study although §4 describes it and four ledger rows back it |
| 8 | 81–85 | "where we are" described a branch that is gone, a 75-row ledger, and an unpushed leader branch |
| 9 | 127 | freezing is merged (PR #3, `2e55eb5`), not "a research branch" |
| 10 | 134 | "Lean core, branch only" is no longer true |
| 11–12 | 158–159 | the setup-branch review and the "checks have not run on GitHub" statement are both historical |
| 13 | 190 | `research/lean-kn` is merged and audited (`LEAN-KN-01`) |

### Still not verifiable from the repository

- The 1,412 issued (run, T) certificates, the 32-of-605 held-event count and the audit CIs: they need the
  run outputs re-derived. A documentation pass must not restate them as re-verified.
- Whether every CI job is a *required* status check: that is branch protection, not a file. Hunk 12 says so
  in the document instead of asserting it.

### Two claims in this file that the evidence did not support

- §A row 11 (`Papers/`) — see above; the sentence already declares the deletion.
- §A row 127–135, "not a repo audit round" — that clause stays true: the freezing work is not one of the
  numbered audit rounds. Only the branch wording was wrong.
