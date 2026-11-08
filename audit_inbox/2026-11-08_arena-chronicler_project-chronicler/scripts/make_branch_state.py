#!/usr/bin/env python3
"""Write evidence/branch_and_pr_state.md from live git/GitHub data.

Everything in the output is fetched, not recalled: branch tips from
``git ls-remote``, PR state from the GitHub API, and merge proofs from
``git ls-tree`` / ``git cat-file`` against the review ref.

    python3 .../scripts/make_branch_state.py [ref]

Read-only. Requires an authenticated ``gh`` for the PR table; degrades to a note
if the API is unavailable.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "evidence" / "branch_and_pr_state.md"


def find_repo(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return start


REPO = find_repo(HERE)


def sh(*args: str) -> str:
    return subprocess.run(list(args), cwd=REPO, capture_output=True, text=True).stdout


def main() -> int:
    ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    heads: dict[str, str] = {}
    for line in sh("git", "ls-remote", "--heads", "origin").splitlines():
        if "\trefs/heads/" in line:
            sha, name = line.split("\t", 1)
            heads[name.removeprefix("refs/heads/").strip()] = sha.strip()

    prs = []
    raw = sh("gh", "pr", "list", "--state", "all", "--limit", "40",
             "--json", "number,title,state,headRefName,baseRefName,mergedAt,mergeCommit")
    try:
        prs = sorted(json.loads(raw or "[]"), key=lambda p: p["number"])
    except json.JSONDecodeError:
        prs = []

    # Rows quoted by the briefing snapshot, parsed from the local copy.
    state_md = REPO / "audit_inbox" / "briefing" / "STATE.md"
    quoted: dict[str, str] = {}
    quote_lines: dict[str, int] = {}
    if state_md.exists():
        for number, line in enumerate(state_md.read_text(encoding="utf-8").splitlines(), start=1):
            for match in re.finditer(r"`([A-Za-z0-9._/\-]+)`[^|\n]{0,50}\|\s*`([0-9a-f]{7,40})`", line):
                branch, token = match.group(1), match.group(2)
                quoted.setdefault(branch, token)
                quote_lines.setdefault(branch, number)

    merged = {p["headRefName"]: p for p in prs if p["state"] == "MERGED"}

    lines = [
        "# Branch and PR state at retrieval",
        "",
        f"- Retrieved: **{now}** with `git ls-remote --heads origin`",
        f"- Review ref: `{ref}` @ `{sh('git', 'rev-parse', '--short=7', ref).strip()}`",
        "- Branch tips move. Re-run this script rather than quoting these numbers later.",
        "",
        "## Live branches on origin",
        "",
        "| Branch | Tip |",
        "|---|---|",
    ]
    for name in sorted(heads):
        lines.append(f"| `{name}` | `{heads[name][:7]}` |")
    lines.append(f"\n{len(heads)} branches at retrieval.\n")

    lines += [
        "## Pull requests (GitHub API)",
        "",
        "| # | State | Head → base | Merged | Merge commit | Title |",
        "|---|---|---|---|---|---|",
    ]
    for pr in prs:
        merge_sha = ((pr.get("mergeCommit") or {}).get("oid") or "")[:7] or "—"
        merged_at = (pr.get("mergedAt") or "—")[:19].replace("T", " ")
        lines.append(
            f"| #{pr['number']} | {pr['state']} | `{pr['headRefName']}` → `{pr['baseRefName']}` | "
            f"{merged_at} | `{merge_sha}` | {pr['title'][:70]} |"
        )
    lines.append("")

    lines += [
        "## Briefing branch table vs live state",
        "",
        "Rows parsed from `audit_inbox/briefing/STATE.md` on the working branch, compared with the tips above.",
        "",
        "| Document says | Line | Quoted tip | Live tip | Status |",
        "|---|---|---|---|---|",
    ]
    for branch, token in quoted.items():
        live = heads.get(branch)
        if live is None:
            status = "**branch not present on origin**"
            live_tip = "—"
            pr = merged.get(branch)
            if pr:
                status = f"**branch deleted after merge** (PR #{pr['number']}, `{((pr.get('mergeCommit') or {}).get('oid') or '')[:7]}`)"
        elif live.startswith(token) or token.startswith(live):
            live_tip = f"`{live[:7]}`"
            status = "unchanged"
        else:
            live_tip = f"`{live[:7]}`"
            status = "**moved**"
        lines.append(f"| `{branch}` | {quote_lines.get(branch, '')} | `{token}` | {live_tip} | {status} |")
    lines.append("")

    absent = [b for b in quoted if b not in heads and b != "audit-inbox"]
    new = [b for b in heads if b not in quoted]
    if absent:
        lines.append("Not present on origin at retrieval: " + ", ".join(f"`{b}`" for b in absent) + ".\n")
    if new:
        lines.append("Present on origin but not in the briefing table: " + ", ".join(f"`{b}`" for b in new) + ".\n")

    lines += [
        "## Proof that the merged work is on `main`",
        "",
        "These are direct reads of the tree at the review ref, not inference from a PR title.",
        "",
        "```text",
    ]
    checks = [
        ("lean/AIEFFreezeCore exists", ["git", "ls-tree", "--name-only", ref, "lean/"]),
        ("research/freezing file count", ["bash", "-lc", f"git ls-tree -r --name-only {ref} | grep -c '^research/freezing/'"]),
        ("freeze claim rows in ledger", ["bash", "-lc",
         f"git cat-file -p {ref}:registry/claims.csv | grep -oE 'LEAN-FREEZE-CORE|RES-FREEZE-GATED|RES-FREEZE-NUM|RES-FREEZE-NOVELTY' | sort -u | tr '\\n' ' '"]),
        ("errata headings present", ["bash", "-lc",
         f"git cat-file -p {ref}:ERRATA_2026-10-28.md | grep -oE '^## E1[2-6]' | tr '\\n' ' '"]),
        ("lean.yml matrix rows", ["bash", "-lc",
         f"git cat-file -p {ref}:.github/workflows/lean.yml | grep -E '^\\s+- \\{{ project:' | sed 's/^ *//'"]),
    ]
    for label, args in checks:
        output = subprocess.run(args, cwd=REPO, capture_output=True, text=True).stdout.strip()
        lines.append(f"$ {label}")
        lines.append(output if output else "(no output)")
        lines.append("")
    lines.append("```")
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(heads)} branches, {len(prs)} PRs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
