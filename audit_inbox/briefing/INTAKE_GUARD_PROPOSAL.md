# Proposal: enforce audit-inbox intake rules (owner decision needed)

**Status:** draft by Researcher 001, 2026-10-31 (America/Toronto). **No workflow has been added.** This file only sets out the options. The owner chooses.

**Problem (Researcher 026, TRIAGE R026-I4, confirmed).** Today the intake rules in `audit_inbox/README.md` are prose only. The only workflow on `audit-inbox` is the old `.github/workflows/lean.yml`, which triggers on `lean/**`. Nothing stops an agent with push access from:

- editing the briefing or other agents' notes;
- adding files outside `audit_inbox/`;
- adding executables, symlinks or workflows;
- force-pushing over history.

## Option A: add-only, path-restricted guard workflow on `audit-inbox`

A `push` / `pull_request` workflow on `audit-inbox` that fails when a commit range:

1. changes any path outside `audit_inbox/`;
2. modifies or deletes an existing file. Only additions (`A`) are allowed, except for paths that maintainers own: `audit_inbox/briefing/**`, `audit_inbox/TRIAGE.md`, `audit_inbox/salvage/**/MANIFEST.csv`. Those are allowed only for listed maintainer identities, which a workflow cannot verify strongly (see the cons);
3. adds a symlink (mode `120000`), a submodule (`160000`), an executable (`100755`), or anything under `.github/`;
4. adds a file over a size limit (for example 1 MiB), or with an extension outside `.md .txt .csv .json .patch .diff`;
5. adds a top-level file whose name does not match `YYYY-MM-DD_<agent>_<topic>.md`, or whose header lacks agent, date with time zone, commit reviewed, scope, and "UNVERIFIED";
6. contains conflict markers, or matches secret / PII patterns (reuse `tools/ci/hygiene_scan.py --pii` from `main`).

To make it binding, a branch ruleset on `audit-inbox` must block force-push and deletion, and it must require this check. A plain push cannot be "required" unless pushes go through PRs, so on its own the workflow only **detects** problems after the push.

- **Pros:** low friction for outside agents, who keep pushing directly. Violations are flagged quickly, and history stays append-only if force-push is blocked.
- **Cons:** it is detect-after-the-fact, not prevention. Bad content is already on the branch when the check goes red, and someone must revert it with a normal commit. Telling maintainer from contributor edits by commit identity is weak, since all agents may push as the same account. The workflow file itself sits on the branch, so a contributor could edit it unless the rule against `.github/` changes is enforced by a ruleset rather than by the workflow.

## Option B: PR-only intake (recommended by Researcher 026 as safer)

Contributors push to their own branch (for example `inbox/<agent>/<date>-<topic>`) and open a PR into `audit-inbox`. A ruleset on `audit-inbox` requires PRs, blocks force-push and deletion, and requires the Option A checks (1–6) as status checks. Maintainers (Researcher 001 / Auditor Seat 002, with the owner merging or delegating) own `briefing/` and `TRIAGE.md`.

- **Pros:** real prevention, because nothing lands until the checks pass and someone merges. There is a reviewable record per submission, and briefing and triage edits get the same control.
- **Cons:** more friction. Outside agents need permission to create branches and PRs, and someone must merge each submission, which adds owner or maintainer load. The repo gains more branches; they can be deleted after merge.

## Comparison

| | A: guard workflow, direct push | B: PR-only intake |
|---|---|---|
| Prevents bad content landing | no (detects after the push) | yes |
| Protects briefing / TRIAGE from contributors | weakly (identity-based) | yes (merge gate) |
| Contributor friction | low | medium |
| Owner/maintainer load | revert on failure | merge each PR |
| Needs ruleset change on `audit-inbox` | yes (no force-push or deletion; protect `.github/`) | yes (require PR + checks) |
| Same checks reusable | yes | yes (as required checks) |

## Decisions for the owner

1. A or B (or neither, keeping the prose rules).
2. Whether to add a ruleset on `audit-inbox` that blocks force-push and deletion. This is useful under either option.
3. Whether contributors should be able to modify their **own** earlier note, or only add new dated files.

Once the owner chooses, a seat implements the workflow on a fresh branch and gets an independent review. Nothing is enforced until then.
