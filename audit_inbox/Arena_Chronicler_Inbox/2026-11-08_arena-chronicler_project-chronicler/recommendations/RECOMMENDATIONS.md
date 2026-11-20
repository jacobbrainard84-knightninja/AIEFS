# Recommendations, in priority order

All evidence is at `origin/main` @ `eb3933c` unless stated. Nothing here has been applied.
Severity is the chronicler's, not an audit verdict.

| # | Severity | Document | What to do | Owner | Route |
|---|---|---|---|---|---|
| R1 | high | `audit_inbox/briefing/STATE.md` | Replace the branch table; fix the Lean/CI paragraph | Researcher 001 | direct edit, then restamp |
| R2 | high | `CURRENT_STATUS.md` | Re-verify §2/§4, fix 3 dead paths, relabel the freeze rows, then restamp | owner / Researcher 001 | side branch + PR |
| R3 | medium | `audit_inbox/briefing/NORTH_STAR.md` | Three lines still say PR #3 is pending and `AIEFFreezeCore` is absent from `main` | Researcher 001 | direct edit |
| R4 | medium | `docs/architecture/EPISTEMIC_GOVERNANCE_AND_LAYOUT.md` | Two counts in the layout block are stale (43 claims → 80; 14 studies → 15) | owner | side branch + PR |
| R5 | medium | `README.md` | Its 2026-10-28 status banner predates 9 merges; re-read its scoped claims, then restamp | owner | side branch + PR |
| R6 | low | `AIEF_MODULAR_DRIVER_CODING_AGENT_PROMPT.md` | `FAILED_manifest.json` (line 743) is a run output, not a repo file — say so inline | owner | side branch + PR |
| R7 | process | this deposit | Decide where the maintenance loop lives and merge `chronicler/` into `main` | owner | merge |
| R8 | process | CI | Optional non-blocking `check --fail-on high` job per PR | owner | `.github/workflows/` |
| R9 | follow-up | toolkit | Add a rule for "document asserts a CI fact that the workflow contradicts" | owner | `chronicler/checks.py` |

---

## R1 — Refresh `audit_inbox/briefing/STATE.md` (highest value)

**Finding:** `DOC-BRANCH-DRIFT` + `DOC-BRANCH-GONE`, medium.

The table at lines 13–25 is 8 days and **9 merged PRs** out of date. Every "**Not merged**" verdict on
PRs #3, #4 and #5 is wrong: those merged on 2026-11-01, 2026-11-06 and 2026-11-06. Line 66 says
`AIEFFreezeCore` is `required: false` and not on `main`; `lean.yml:49` has it `required: true`, and the
directory is on `main`.

Concrete replacement text: `state_md_proposed_table.md`.

Why it matters more than the others: this file is what outside review agents read first. Right now it
tells them that four audited work packages are still awaiting the owner, which invites duplicate work.

## R2 — `CURRENT_STATUS.md` needs re-verification, not a date bump

**Finding:** `DOC-STALE-VS-SOURCE` + `DOC-PATH-MISSING`, high.

Stamped 2026-10-23; `registry/claims.csv` changed 2026-11-08. It also cites `Papers/` and four
scripts/directories that are not in the tree, and describes the freezing theorem as living on a
research branch (merged 2026-11-06, `2e55eb5`).

Do not restamp without §A–§D of `current_status_checklist.md`. A date-only edit is the failure mode
this whole deposit exists to prevent.

## R3 — `NORTH_STAR.md` carries the same stale fact

Lines 66, 76 and 81. One-line each. Its living checklist can now cite `2e55eb5` instead of
"PENDING, PR #3".

## R4 — Stale counts in the architecture document

`docs/architecture/EPISTEMIC_GOVERNANCE_AND_LAYOUT.md` contains a layout block with counts:

| Line | Says | Actual at `eb3933c` |
|---|---|---|
| 27 | `studies.csv` — "14 research studies" | **15** data rows |
| 28 | `claims.csv` — "43 claims" | **80** data rows |
| 26 | `artifacts.csv` — "2,898 SHA-256 entries" | 2,898 ✅ (this one is right) |

Counts in the frozen-inventory sentence (line 9, "2,760 files … `e47bad1`") are correctly scoped to
the base commit and should stay as they are. Only the two unlabelled counts are wrong.

## R5 — `README.md` status banner

Line 8: "Status of this README (2026-10-28)". The banner is not false by itself — it is dated, which is
the honest form — but the scoped claim list below it has not been re-read against the ledger in 11
days, during which PRs #3–#5 and #7–#12 landed. Re-read §"What the audits support", then decide
whether the banner date moves.

## R6 — A bare filename that is really a run output

`AIEF_MODULAR_DRIVER_CODING_AGENT_PROMPT.md:743` names `FAILED_manifest.json`. No tracked file has that
name; it is described in context as a failure marker a run would write. Worth one clause — "written
into the run directory on failure" — so a future reader does not go looking for it in the repo.
`docs/architecture/…:13` has the same issue with `provenance.json` (that one is planned by Stage 5).
Both are `low`; no action is required to keep the docs correct.

## R7 — Where the maintenance loop lives

`PROJECT_CHRONICLER_AGENT.md` and `chronicler/` are on `arena/eae4f5a6-aiefs`. This deposit is under
`audit_inbox/` on the same branch. Two structural decisions:

1. **Carry this folder to `audit-inbox`** (the branch these deposits belong on), or merge the branch.
   The session branch is fixed, so I cannot push to `audit-inbox` myself.
2. **Merge `chronicler/` into `main`** when convenient, so the agent does not depend on a side branch.
   It is stdlib-only, adds no runtime dependency, and its own tests run under `unittest`.

Recommendation: merge the toolkit to `main` as a `tools/`-adjacent package, keep the *loop state* on a
side branch or out of the repo if you prefer not to see it churn on every cycle. The charter works
either way; only the state paths change.

## R8 — Optional CI visibility

`python -m chronicler check --fail-on high` exits `1` on today's tree (2 high findings), so it is **not**
safe to make it a required check yet. A non-blocking job that prints the findings per PR would make
document drift visible when it happens instead of 11 days later. Add `--fail-on none` initially; raise
it to `high` once R1–R3 are done and the queue is empty.

## R9 — A rule worth writing, and one limit to accept

The sharpest drift found here — `STATE.md:66` claiming `required: false` for a project the workflow
marks `required: true` — is **not** caught by any current rule. It is a semantic contradiction between
a document and a workflow file. Two options:

- a narrow rule: parse the `{ project: …, required: … }` matrix from
  `.github/workflows/lean.yml`, and flag documents that assert a project's presence or `required` flag
  with a different value (high precision, ~40 lines);
- or accept that this class is caught by the periodic deep sweep, and make sure sweeps actually run.

I recommend the narrow rule plus sweeps. The rule is cheap and this exact fact has now been wrong in
three documents at once, which suggests it will regress.

---

## What I recommend **not** doing

- Do not restamp `CURRENT_STATUS.md` as the first step. It is the single most tempting edit and the
  least useful one.
- Do not "refresh" any hash pin. All 29 match; there is nothing to refresh.
- Do not merge the `audit-inbox` tree into `main`. The briefing and this deposit are navigation and
  evidence, not repository content; `audit_inbox/salvage/` in particular must never be merged.
- Do not treat R1–R6 as a single PR. They have different owners and different review routes; one
  finding per commit is what keeps the review readable.
