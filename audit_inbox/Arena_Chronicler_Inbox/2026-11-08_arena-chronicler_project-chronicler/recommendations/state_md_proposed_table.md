# Proposed correction: `audit_inbox/briefing/STATE.md`

**Owner of this file: Researcher 001.** This is a proposal, not an edit. I did not modify the briefing.

Evidence: `../evidence/branch_and_pr_state.md` (live tips and PR state, retrieved 2026-11-08 22:45 UTC)
and the `main`-tree reads at the end of that file.

---

## Why

`STATE.md` is a *navigation snapshot*, and its snapshot is from 2026-10-31. Since then:

- `main` moved `395ea53` → `eb3933c`;
- **nine** pull requests merged: #3, #4, #5, #7, #8, #9, #10, #11, #12;
- the branches named in rows 15, 16 and 18 were deleted after those merges;
- two rows (20, 21) name branches that never reached origin under those names — the work landed via
  `fix/lint-claims-combined` (PR #7);
- five branches now exist that the table does not mention.

The document's own rule — "Branch tips move. Re-run `git ls-remote origin` before citing any sha
below." — is doing its job as a warning, but the table is 8 days and 9 merges out of date, and its
"**Not merged**" verdicts are now wrong in a way a reader will not catch.

---

## 1. Replace the branch table

Retrieved 2026-11-08 22:45 UTC with `git ls-remote --heads origin` (14 branches). Suggested rows,
keeping the existing column shape:

```markdown
| What | Tip at retrieval | Status |
|---|---|---|
| `main` | `eb3933c` | Merge of PR #12 (`fix/r026-cleanup`), 2026-11-08 19:36 UTC. PRs #1–#5 and #7–#12 are merged. |
| PR #3 `research/freezing` | `2e55eb5` (merged) | **Merged 2026-11-06.** Claim split, Corollary 4 fix, novelty rescope and `lean/AIEFFreezeCore` are on `main`. Branch deleted. |
| PR #4 `research/redteam-negcontrols` | `37deb7d` (merged) | **Merged 2026-11-01.** `tools/redteam` is on `main`. Branch deleted. |
| PR #5 `fix/errata-old-files-drift` (E15) | `7c7032f` (merged) | **Merged 2026-11-06.** E15 is in `ERRATA_2026-10-28.md` on `main`. Branch deleted. |
| PR #7 `fix/lint-claims-combined` | `58d5543` (merged) | **Merged 2026-11-07.** Also covers the intent of the old `fix/lint-claims-fail-closed` and `-artifacts` rows; those branch names never reached origin. |
| PR #8 `fix/comparator-v4-from-main` (E14) | `ad58a46` (merged) | **Merged 2026-11-07.** E14 is on `main`. |
| PR #9 `fix/check-manifest-g1g2` | `942f852` (merged) | **Merged 2026-11-08.** Branch also exists at `13a01d1`. |
| PR #10 `fix/upload-new-f1f2` | `3a5d0e2` (merged) | **Merged 2026-11-08.** |
| PR #11 `ci/check-sha256sums` | `f3e3a57` (merged) | **Merged 2026-11-08.** Branch also exists at `aababfe`. |
| PR #12 `fix/r026-cleanup` | `eb3933c` (merged) | **Merged 2026-11-08.** Includes erratum E16 and `test_01.py` removal. |
| `audit-inbox` | `e72bdd2` | Drop box, cut from `a991b46`. **Never merge.** |
| `arena/d4a487cc-aiefs` | `2af3859` | Arena working branch. **Never merge its tree.** |
| `fix/040282-f4-f6-f7` | `19f0786` | **Not merged.** |
| `fix/comparator-v4-gates` | `902abe8` | **Not merged**, and superseded in intent by PR #8. Say so. |
| `fix/manifest-nonempty` | `92993eb` | **Not merged**, superseded in intent by PR #9. |
| `research/aiefs-northstar-evaluation` | `003522e` | **Not merged** (PR #13 closed without merge). |
| `research/rate-law-delta-sweep` | `62239a2` | **Not merged.** |
```

Two closed PRs are worth one line each so nobody re-opens them by accident: **#6**
(`fix/corr-0995-scope-main`) and **#13** (`research/aiefs-northstar-evaluation`), both **CLOSED without
merge**.

## 2. Correct the Lean/CI paragraph (line 66)

Current text:

> `main`'s `lean.yml` now runs AIEFProofs and AIEFProofsKn as required. It also lists AIEFFreezeCore
> with `required: false`, and that project is not on `main` yet.

Both clauses are now false. At `eb3933c`:

- `lean/AIEFFreezeCore` **is** on `main` (directory present in `git ls-tree`);
- `.github/workflows/lean.yml:49` lists `{ project: AIEFFreezeCore, script: check_lean_freeze.sh,
  axiom_root: AIEFFreezeCore, required: true }`;
- the workflow's own comment at line 18 says "AIEFFreezeCore is required since main was merged into
  research/freezing".

Suggested replacement:

> `main`'s `lean.yml` runs three Lake projects as required jobs: AIEFProofs, AIEFProofsKn and
> AIEFFreezeCore, each with its own axiom-audit root and forbidden-marker step
> (`.github/workflows/lean.yml:47-49`). `tools/ci/lean_presence.sh` makes a missing project fail
> rather than skip.

## 3. Refresh the header stamp

Line 1 is `# Project state (as of 2026-10-31, America/Toronto)`. After the table and §2 are applied,
restamp with the date you actually verified it, and keep the "snapshot, not live" language — it is
what makes the table honest.

## 4. Also affected: `NORTH_STAR.md`

Same file family, same owner. Three lines carry the same stale fact:

- line 66: "AIEFFreezeCore is listed but not on `main` yet";
- line 76: row `3 | Hebbian weight dynamics | partial (PENDING, PR #3)`;
- line 81: "AIEFFreezeCore is a required row only on `research/freezing`".

The dependency-chain checklist can now say PR #3 is **merged**, and move row 3 from "partial
(PENDING)" to "partial" with `2e55eb5` cited.

---

## How to check this proposal

```bash
git ls-remote --heads origin | sort -k2          # 14 branches; compare the tip column
gh pr list --state all --limit 40 --json number,state,headRefName,mergedAt,mergeCommit
git ls-tree --name-only origin/main lean/         # AIEFFreezeCore is present
git cat-file -p origin/main:.github/workflows/lean.yml | sed -n '45,50p'
git cat-file -p origin/main:registry/claims.csv | grep -oE 'LEAN-FREEZE-CORE|RES-FREEZE-(GATED|NUM|NOVELTY)' | sort -u
```

All five were run; output is in `../evidence/branch_and_pr_state.md`.
