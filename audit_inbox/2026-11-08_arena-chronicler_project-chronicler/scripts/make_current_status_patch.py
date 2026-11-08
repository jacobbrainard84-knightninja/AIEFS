#!/usr/bin/env python3
"""Regenerate the proposed `CURRENT_STATUS.md` edit as an applicable patch.

Reads `CURRENT_STATUS.md` from a git ref (default `origin/main`), applies the
reviewed replacements below, and writes:

  recommendations/current_status_edits.patch   unified diff (apply with `git apply`)
  recommendations/CURRENT_STATUS.proposed.md   the full proposed file

Every replacement is asserted to match exactly once, so if the source document
changes under us this script fails loudly instead of producing a stale patch.
Nothing here is applied to the repository: the patch is a proposal.

    python3 scripts/make_current_status_patch.py [ref]
"""
from __future__ import annotations

import difflib
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "recommendations"
DOC = "CURRENT_STATUS.md"
REF = sys.argv[1] if len(sys.argv) > 1 else "origin/main"

# Why this stamp is not simply bumped: the chronicler verified the inventory
# counts, the ledger labels and every evidence path in section 2 at this commit.
# It did not re-derive any scientific statement, and the stamp must say so.
STAMP = (
    "**Last Verified:** 2026-10-23 (`Milestone 1` complete; `verify_inventory.py` passing on all "
    "`2,898` inventoried objects) — **re-checked 2026-11-08** against `main` @ `eb3933c` for section 1 "
    "counts, ledger labels and section 2 evidence paths; scientific statements were not re-derived."
)

FREEZE_ROW = (
    "| **Topology Freezing (`research/freezing`; merged 2026-11-06, PR #3 `2e55eb5`)** | "
    "`Supported` Lean core (`LEAN-FREEZE-CORE`: per-edge ∃N, real arithmetic, `lean/AIEFFreezeCore`), "
    "`Exploratory` conditional paper theorem (`RES-FREEZE-GATED`), `Exploratory` finite numerics "
    "(`RES-FREEZE-NUM`), novelty not established (`RES-FREEZE-NOVELTY`) | "
    "`Formalized theorem` + `Conditional theorem` | "
    "`research/freezing/REPORT.md`, `research/freezing/README.md`, "
    "`research/freezing/audit/AUDIT_R002_d9c03ef.md`, `lean/AIEFFreezeCore/` | "
    "Conditional: one seed, one winner branch, two directions, `dt=0.01`, safeguard `1e-12`, finite "
    "horizon. 1,412 issued (run, T) certificates with no finite-window violation (nested, dependent "
    "windows to step 80000). Do not state it unconditionally. |"
)

WHERE_WE_ARE = """**Where we are (2026-11-08).**
- `main` is the live branch. The branch `merge-prep/arena-reconciled` described here on 2026-10-28 no longer
  exists on the remote, and no pull request in `#1–#13` was opened from it: its reconciled content is on `main`
  (the `registry/` tree is present), so it either landed directly or was subsumed.
- Eleven pull requests have been merged into `main` (`#1–#5`, `#7–#12`); `#6` and `#13` were closed unmerged.
  The most recent is `#12` (`eb3933c`, 2026-11-08).
- The claim ledger has **80** rows; `registry/claims.csv` is authoritative. The 75-row figure above predates the
  post-push review rows and the `RES-FREEZE-01` split into four rows. Corrections to pinned files are in
  `ERRATA_2026-10-28.md` (E1–E18).
- `MERGE_PREP_REPORT.md` describes the pre-merge branch; read its branch state as history, not as current.
  Working rules are in `OPERATING_MANUAL.md`."""

# (old, new) applied in order; each must occur exactly once.
EDITS: list[tuple[str, str]] = [
    # 1. header stamp -------------------------------------------------------
    (
        "**Last Verified:** 2026-10-23 (`Milestone 1` complete; `verify_inventory.py` passing on all "
        "`2,898` inventoried objects)",
        STAMP,
    ),
    # 2. the vocabulary no longer lacks an exploratory-design label ----------
    (
        "`Finite numerical observation` in the ledger (the vocabulary has no exploratory-design value)",
        "`Finite numerical observation` in the ledger (`audited_status` `Exploratory`)",
    ),
    # 3. cite the ledger's exact label for EMP-AIEF14-03 ---------------------
    (
        "claim EMP-AIEF14-03 **`Exploratory`** (controlled exploratory analysis",
        "claim EMP-AIEF14-03 **`Exploratory`** (ledger `audited_status` `Controlled exploratory`; "
        "controlled exploratory analysis",
    ),
    # 4. four evidence paths in this row are absent from the tree -----------
    (
        "`aief_1_4_full_state_tangent_operator.py`, `aief_1_4_history_cocycle_test.py`, "
        "`aief_1_4_branch_tangent_comparison.py`, `aief_1_4_jacobian_step_convergence/`",
        "**Not present on `main` @ `eb3933c`** (checked 2026-11-08): "
        "`aief_1_4_full_state_tangent_operator.py`, `aief_1_4_history_cocycle_test.py`, "
        "`aief_1_4_branch_tangent_comparison.py`, `aief_1_4_jacobian_step_convergence/`; the ledger rows "
        "(`CF05`, `CF10`) carry only \"historical … manifest\" references, so this row's evidence is not "
        "reachable from the repository",
    ),
    # 5. one of three paths in this row is absent ---------------------------
    (
        "`aief_1_4_k3_fiber_audit/` (`26` isolated $K_3$ components)",
        "`aief_1_4_k3_fiber_audit/` (`26` isolated $K_3$ components; **not present on `main` @ `eb3933c`**)",
    ),
    # 6. two different test counts for one suite inside one file ------------
    (
        "tests re-run 2026-10-28: default 40 passed, 2 skipped; 41 passed, 1 skipped with "
        "AIEF_RUN_SLOW_TESTS=1 and the repo root on PYTHONPATH",
        "tests re-run 2026-10-28: default 40 passed, 2 skipped; 41 passed, 1 skipped with "
        "AIEF_RUN_SLOW_TESTS=1 and the repo root on PYTHONPATH; **current** counts, after the R026-S7 "
        "driver CLI test, are default 43 passed, 2 skipped, 2 xfailed (see §4 and `repo-checks.yml`; "
        "AUD-MODULAR-ORACLE)",
    ),
    # 7. the study table has no row for the merged freezing work ------------
    (
        "empirical (`CF05`) / open (`CF12`). |",
        "empirical (`CF05`) / open (`CF12`). |\n" + FREEZE_ROW,
    ),
    # 8. "where we are" describes a branch that is gone ---------------------
    (
        "**Where we are (2026-10-28).**\n"
        "- The local branch `merge-prep/arena-reconciled` reconciles the arena Milestone 1 work with `main` "
        "and the audits.\n"
        "- It is **not pushed**. It waits for review by the owner, Auditor Seat 002 and outside reviewers.\n"
        "- The claim ledger has 75 rows (7 post-push review rows added on local branch `work/post-push-1`, "
        "not pushed). Corrections to pinned files are in `ERRATA_2026-10-28.md`.\n"
        "- Details, checks and open items are in `MERGE_PREP_REPORT.md`. Working rules are in "
        "`OPERATING_MANUAL.md`.",
        WHERE_WE_ARE,
    ),
    # 9. freezing was merged, not a live branch ----------------------------
    (
        "(research branch `research/freezing`, 2026-10-29; not a repo audit round)",
        "(merged 2026-11-06, PR #3 `2e55eb5`; not a repo audit round)",
    ),
    # 10. "branch only" is no longer true ----------------------------------
    (
        "`LEAN-FREEZE-CORE` (Supported, Lean core, branch only)",
        "`LEAN-FREEZE-CORE` (Supported, Lean core)",
    ),
    # 11. the setup-branch review is done ----------------------------------
    (
        "1. Review of the set-up branch by the owner, GPT and Arena AI. After that, the owner decides "
        "whether to push and merge.",
        "1. ~~Review of the set-up branch by the owner, GPT and Arena AI; owner decision whether to push and "
        "merge.~~ **Done:** the reconciled content is on `main` and later work lands by pull request "
        "(#1–#12). No work is queued on an unpushed local branch.",
    ),
    # 12. the PR checks do run on GitHub -----------------------------------
    (
        "2. Automated PR checks from Auditor Seat 002 are now in this branch (`OPERATING_MANUAL.md` §7). "
        "They have not run on GitHub yet, because nothing is pushed.",
        "2. Automated PR checks from Auditor Seat 002 are in `.github/workflows/` (`repo-checks.yml`, "
        "`lean.yml`) and run on pull requests to `main`. **Not checked from this document:** whether every "
        "job is a required status check in branch protection — verify before relying on a green run.",
    ),
    # 13. lean-kn was merged and audited ------------------------------------
    (
        "- (a) **Done on research branch `research/lean-kn` (2026-10-29; local, not audited).**",
        "- (a) **Done on `research/lean-kn` (2026-10-29; merged; audited as `LEAN-KN-01`, `Supported`).**",
    ),
]


def read_source(ref: str) -> str:
    return subprocess.run(
        ["git", "cat-file", "-p", f"{ref}:{DOC}"],
        check=True, capture_output=True, text=True,
    ).stdout


def main() -> int:
    text = read_source(REF)
    for old, new in EDITS:
        n = text.count(old)
        if n != 1:
            print(f"REFUSING: expected exactly 1 match, found {n}:\n  {old[:100]!r}", file=sys.stderr)
            return 2
        text = text.replace(old, new, 1)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "CURRENT_STATUS.proposed.md").write_text(text)

    diff = list(difflib.unified_diff(
        read_source(REF).splitlines(keepends=True),
        text.splitlines(keepends=True),
        fromfile=f"a/{DOC}", tofile=f"b/{DOC}", n=3,
    ))
    (OUT / "current_status_edits.patch").write_text("".join(diff))
    changed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
    print(f"{REF}: {len(EDITS)} edits, {changed} lines removed by the diff "
          f"(+{sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))} added)")
    print(f"wrote {OUT/'current_status_edits.patch'} and {OUT/'CURRENT_STATUS.proposed.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
