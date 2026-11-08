"""The self-directed loop: reconcile findings, choose the next action, remember.

The loop exists so that ``continue`` is a well-defined instruction. State lives in
``chronicler/loop/state.json``; the work order for the current cycle is written to
``chronicler/loop/NEXT.md`` and every cycle is appended to ``JOURNAL.md``.
"""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

from . import checks, facts, util

STATE_SCHEMA = 1

SEVERITY_POINTS = {"critical": 100.0, "high": 80.0, "medium": 55.0, "low": 30.0, "info": 5.0}

ACTIVE_STATUSES = {"open", "in_progress"}

#: Concrete, rule-specific instructions. Generic advice is what makes agents stall.
RULE_PLAYBOOK: dict[str, dict] = {
    "PIN-HASH-MISMATCH": {
        "steps": [
            "Stop editing immediately. This is a frozen-authority breach, not a doc bug.",
            "Confirm which commit changed the file: `git log --oneline -- <path>`.",
            "Report to the owner with the expected/actual hashes before doing anything else.",
            "If the owner approves, add a dated entry to the errata file and update the claim ledger row that depends on it.",
        ],
        "forbidden": "Do not edit the pinned file. Do not 'refresh' the pin to match the new content.",
    },
    "DOC-STALE-VS-SOURCE": {
        "steps": [
            "Read the watched source at the cited commit — not from memory, not from an older doc.",
            "List every sentence in the doc that depends on the changed source.",
            "Rewrite only those sentences; keep all unrelated text byte-identical so the diff stays reviewable.",
            "Update the freshness stamp in the same commit as the text change.",
        ],
        "forbidden": "Do not bump the date without changing content. A date-only commit is a false claim of freshness.",
    },
    "DOC-BRANCH-DRIFT": {
        "steps": [
            "Run `git ls-remote origin` and record the retrieval timestamp.",
            "Rewrite the tip column from live output, keeping the doc's 'snapshot, not live' warning.",
            "Note any branch that exists locally but not on origin, and vice versa.",
        ],
        "forbidden": "Do not drop the 'branch tips move' caveat. It is what makes the table honest.",
    },
    "DOC-PATH-MISSING": {
        "steps": [
            "For each dead path, search the real tree: `git ls-tree -r --name-only <ref> | grep -i <fragment>`.",
            "Repair the pointer to the real path, or mark the artifact as absent in plain words.",
            "If the path moved, check `registry/relocation_map.csv` for an authorised mapping.",
        ],
        "forbidden": "Do not delete the sentence to make the check pass. That hides a missing artifact.",
    },
    "DOC-SHA-UNREACHABLE": {
        "steps": [
            "Try `git fetch origin` then re-resolve the sha.",
            "If it still does not resolve, check whether the work was ever merged into `main`.",
            "Correct the citation, or add the 'not merged / pending' label the doc is missing.",
        ],
        "forbidden": "Do not substitute a different sha without re-reading what that commit actually contains.",
    },
    "DOC-AGED": {
        "steps": [
            "Re-read the whole document against the current registry and tree.",
            "Confirm what is still true, correct what is not, and restamp the date.",
            "If nothing changed, say so explicitly in the commit message ('re-verified, no change') and restamp.",
        ],
        "forbidden": "Do not restamp without re-reading. This rule is about verification, not ceremony.",
    },
    "DOC-MISSING-SECTION": {
        "steps": [
            "Check the doc's git history to see whether the section was removed deliberately.",
            "Restore the section if removal was accidental, or update docs_manifest.json with a written reason.",
        ],
        "forbidden": "Do not silently change the manifest to make a check pass without recording why.",
    },
    "DOC-COUNT-MISMATCH": {
        "steps": [
            "Recount from the commit the sentence refers to, or from the current ref if it claims 'current'.",
            "Either update the number and date it, or qualify it as 'as of <commit/date>'.",
        ],
        "forbidden": "Do not present a moving count as a fixed fact without a scope.",
    },
    "DOC-WATCH-MISSING": {
        "steps": [
            "Find the real source of truth the doc should track.",
            "Update the `watch` list in docs_manifest.json, or drop it with a reason.",
        ],
        "forbidden": "Do not leave a broken watch entry: it silently disables staleness detection.",
    },
    "DOC-NO-DATE": {
        "steps": [
            "Add a dated stamp under the title: `**Last Verified:** YYYY-MM-DD`.",
            "Set it to the date you actually verified the content, not today's date by default.",
        ],
        "forbidden": "Do not add a date to a document you have not read.",
    },
    "DOC-MISSING": {
        "steps": [
            "Restore the file from the last commit that had it, or confirm it was deleted on purpose.",
            "If deleted on purpose, remove it from docs_manifest.json with a reason.",
        ],
        "forbidden": "Do not recreate a doc from memory. Restore the real bytes.",
    },
    "DOC-BRANCH-GONE": {
        "steps": [
            "Confirm deletion with `git ls-remote origin` and `gh api repos/{owner}/{repo}/branches`.",
            "Mark deleted branches as deleted, with the date, as STATE.md already does.",
        ],
        "forbidden": "Do not assume a missing branch was merged.",
    },
    "VOCAB-UNKNOWN-STATUS": {
        "steps": [
            "Open registry/README.md and read the '## Status vocabulary' block as it stands.",
            "List the offending ledger rows and their current values.",
            "If the ledger is wrong, fix it through registry/reconciliation/build_claims_reconciliation.py.",
            "If a new label is genuinely needed, stop: label changes are a major change and need the owner.",
        ],
        "forbidden": "Do not quietly add a value to the vocabulary block to make the lint pass.",
    },
    "VOCAB-MISSING": {
        "steps": [
            "Restore the fenced block from the previous commit, byte for byte.",
            "Run `python3 tools/ci/lint_claims.py` and confirm it parses the block.",
        ],
        "forbidden": "Do not retype the vocabulary from memory; the ordering and exact strings matter.",
    },
    "DOC-AUTHORITY-OVERLAP": {
        "steps": [
            "Decide which document is authoritative for this job and make the other explicitly subordinate.",
            "Add one sentence to the subordinate doc naming the authority it defers to.",
        ],
        "forbidden": "Do not create a third 'single source of truth'.",
    },
    "DOC-HASH-PINNED": {
        "steps": [
            "Treat this as advisory: the file cannot be edited in place.",
            "Record the intended correction in the errata file instead.",
        ],
        "forbidden": "Do not 'just fix' a pinned document, however small the typo.",
    },
    "SWEEP": {
        "steps": [
            "Read the document end to end, out loud if needed.",
            "Check every number, path and claim against the registry and the tree at the current ref.",
            "Fix drift, restamp, and note in the journal what you verified.",
        ],
        "forbidden": "Do not rewrite for style. This sweep is for correctness and currency.",
    },
}

DEFAULT_PLAYBOOK = {
    "steps": [
        "Read the evidence in this file.",
        "Reproduce the finding yourself before changing anything.",
        "Make the smallest correct edit, on a side branch.",
        "Re-run `python -m chronicler check` and confirm the finding is gone.",
    ],
    "forbidden": "Do not make unrelated changes. One finding, one focused commit.",
}


# --------------------------------------------------------------------------
# Paths and state
# --------------------------------------------------------------------------

def loop_dir() -> Path:
    """Override with CHRONICLER_LOOP_DIR (used by tests and scratch runs)."""
    override = os.environ.get("CHRONICLER_LOOP_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parent / "loop"


def state_path() -> Path:
    return loop_dir() / "state.json"


def journal_path() -> Path:
    return loop_dir() / "JOURNAL.md"


def next_path() -> Path:
    return loop_dir() / "NEXT.md"


def snapshot_path() -> Path:
    return loop_dir() / "snapshot.json"


def empty_state() -> dict:
    return {
        "schema": STATE_SCHEMA,
        "cycle": 0,
        "created_at": util.iso(util.utcnow()),
        "last_tick": None,
        "last_ref": None,
        "last_snapshot": None,
        "items": [],
        "history": [],
    }


def load_state() -> dict:
    state = util.read_json(state_path(), None)
    if not isinstance(state, dict):
        return empty_state()
    state.setdefault("items", [])
    state.setdefault("history", [])
    state.setdefault("cycle", 0)
    return state


def save_state(state: dict) -> None:
    util.write_json(state_path(), state)


# --------------------------------------------------------------------------
# Reconciliation
# --------------------------------------------------------------------------

def reconcile(state: dict, findings: list[checks.Finding], *, cycle: int, now: str) -> dict:
    """Merge this cycle's findings into the durable queue.

    * new finding -> new open item
    * still firing -> refresh evidence, keep its history
    * no longer firing -> resolve (or reopen a previously 'done' item as a regression)
    """
    by_id = {item["id"]: item for item in state["items"]}
    fresh = {f.id: f for f in findings}
    stats = {"new": 0, "refreshed": 0, "resolved": 0, "reopened": 0}

    # A finding's id is derived from its content, so the id changes when the finding changes
    # shape: correcting one bad reference out of three replaces the item instead of updating it,
    # and the replacement forgets that the item was deferred. There is at most one finding per
    # (rule, document), so fall back to that pair and keep the item's identity and status.
    by_rule_doc: dict[tuple[str, str], dict] = {}
    for candidate in state["items"]:
        if candidate.get("status") in {"done", "resolved"}:
            continue
        by_rule_doc.setdefault((candidate.get("rule"), candidate.get("doc")), candidate)

    seen: set[str] = set()
    for fid, finding in fresh.items():
        item = by_id.get(fid)
        if item is None:
            item = by_rule_doc.get((finding.rule, finding.doc))
        if item is None:
            state["items"].append({
                "id": fid,
                "finding_key": finding.key,
                "rule": finding.rule,
                "severity": finding.severity,
                "title": finding.title,
                "doc": finding.doc,
                "detail": finding.detail,
                "evidence": finding.evidence,
                "action": finding.action,
                "status": "open",
                "first_seen": now,
                "last_seen": now,
                "cycle_seen": cycle,
                "cycle_closed": None,
                "note": "",
            })
            stats["new"] += 1
            continue

        seen.add(item["id"])
        item.update({
            "finding_key": finding.key,
            "severity": finding.severity,
            "title": finding.title,
            "detail": finding.detail,
            "evidence": finding.evidence,
            "action": finding.action,
            "last_seen": now,
        })
        if item["status"] in {"done", "resolved"}:
            item["status"] = "open"
            item["cycle_closed"] = None
            item["note"] = (item.get("note") or "") + " | reopened: finding reappeared"
            stats["reopened"] += 1
        else:
            stats["refreshed"] += 1

    for item in state["items"]:
        if item["status"] in ACTIVE_STATUSES and item["id"] not in fresh and item["id"] not in seen:
            item["status"] = "resolved"
            item["cycle_closed"] = cycle
            item["resolved_at"] = now
            stats["resolved"] += 1

    return stats


# --------------------------------------------------------------------------
# Selection
# --------------------------------------------------------------------------

def _class_weight(snapshot: dict, doc_path: str) -> float:
    for doc in snapshot.get("documents", []):
        if doc["path"] == doc_path:
            return checks.CLASS_WEIGHT.get(doc.get("class", "status"), 0.5)
    return 0.5


def _score(item: dict, snapshot: dict, now_dt: dt.datetime) -> float:
    base = SEVERITY_POINTS.get(item.get("severity", "low"), 30.0)
    weight = _class_weight(snapshot, item.get("doc", ""))
    bonus = checks.RULE_BONUS.get(item.get("rule"), 0.0)
    age_bonus = 0.0
    seen = util.parse_git_date(item.get("first_seen") or "")
    if seen:
        age_bonus = min((now_dt - seen).total_seconds() / 86400.0, 30.0) * 0.5
    return round(base * (0.6 + 0.8 * weight) + bonus + age_bonus, 2)


def explain_priority(item: dict, snapshot: dict, now_dt: dt.datetime | None = None) -> str:
    """Plain-language account of why this item is first. Determinism needs a reason."""
    now_dt = now_dt or util.utcnow()
    severity = item.get("severity", "low")
    base = SEVERITY_POINTS.get(severity, 30.0)
    weight = _class_weight(snapshot, item.get("doc", ""))
    bonus = checks.RULE_BONUS.get(item.get("rule"), 0.0)
    doc_class = next(
        (d.get("class", "status") for d in snapshot.get("documents", []) if d["path"] == item.get("doc")),
        "status",
    )
    parts = [f"severity {severity} ({base:.0f})", f"{doc_class} weight {weight:.1f}"]
    if bonus:
        parts.append(f"content-drift bonus +{bonus:.0f}")
    parts.append(f"total {_score(item, snapshot, now_dt):.1f}")
    return ", ".join(parts)


def _eligible(item: dict, now_dt: dt.datetime) -> bool:
    """Open items are eligible; deferred items come back when their date passes."""
    status = item.get("status")
    if status in {"open", "in_progress"}:
        # in_progress stays eligible on purpose: an unfinished cycle must be resumed,
        # not silently skipped in favour of the next finding.
        return True
    if status == "deferred":
        raw = item.get("defer_until")
        if not raw:
            # A deferral with no date is a hand-off, not a delay: the item waits on another
            # seat or another branch. Re-selecting it immediately would spin the loop
            # forever on work this agent cannot do.
            return False
        until = util.parse_date(raw)
        return until is None or until <= now_dt
    return False


def candidates(state: dict, snapshot: dict, *, now_dt: dt.datetime | None = None) -> list[dict]:
    now_dt = now_dt or util.utcnow()
    pool = [
        item for item in state["items"]
        if _eligible(item, now_dt)
        and item.get("severity") != "info"
    ]
    return sorted(pool, key=lambda i: (-_score(i, snapshot, now_dt), i.get("first_seen") or "", i["id"]))


def ensure_sweep(state: dict, snapshot: dict, *, cycle: int, now: str) -> dict | None:
    """When nothing is broken, audit the least-recently-touched maintained doc."""
    if candidates(state, snapshot):
        return None
    open_sweeps = [i for i in state["items"] if i.get("rule") == "SWEEP" and i.get("status") == "open"]
    if open_sweeps:
        return open_sweeps[0]

    docs = [d for d in snapshot.get("documents", []) if d.get("present") and d.get("editable")]
    if not docs:
        return None
    docs.sort(key=lambda d: (d.get("commit", {}).get("date") or "", d["path"]))
    target = docs[0]
    item_id = util.stable_id("SWEEP", target["path"])
    if any(i["id"] == item_id and i.get("status") == "done" for i in state["items"]):
        # Rotate: a completed sweep should not immediately re-queue the same doc.
        docs = [d for d in docs if d["path"] != target["path"]]
        if not docs:
            return None
        target = docs[0]
        item_id = util.stable_id("SWEEP", target["path"])

    item = {
        "id": item_id,
        "rule": "SWEEP",
        "severity": "low",
        "title": f"Deep sweep: {target['path']}",
        "doc": target["path"],
        "detail": (
            f"No drift is currently detected, so {target['path']} is the least recently edited "
            "maintained document. Verify its content end to end against the current tree."
        ),
        "evidence": [
            f"{target['path']} last changed {(target.get('commit') or {}).get('date', 'unknown')} "
            f"@ {((target.get('commit') or {}).get('sha') or '?')[:7]}",
            f"declared stamp: {target.get('declared_date') or 'none'}",
        ],
        "action": "Read it fully, check every number and path, fix drift, restamp.",
        "status": "open",
        "first_seen": now,
        "last_seen": now,
        "cycle_seen": cycle,
        "cycle_closed": None,
        "note": "",
    }
    state["items"].append(item)
    return item


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def _badge(severity: str) -> str:
    return {"critical": "CRITICAL", "high": "high", "medium": "medium", "low": "low", "info": "advisory"}.get(
        severity, severity
    )


def render_next(state: dict, snapshot: dict, chosen: dict | None) -> str:
    now = util.iso(util.utcnow())
    ref_commit = snapshot.get("ref_commit", {})
    lines: list[str] = []
    lines.append(f"# CONTINUE — cycle {state['cycle']}")
    lines.append("")
    lines.append(
        f"Generated {now} · ref `{snapshot['ref']}` @ `{(ref_commit.get('sha') or '?')[:7]}` "
        f"({ref_commit.get('date', 'unknown')})"
    )
    if not snapshot.get("remote", {}).get("ok"):
        lines.append("")
        lines.append(f"> Remote tips unavailable (`{snapshot.get('remote', {}).get('error')}`); branch-tip rules were skipped.")
    lines.append("")

    if chosen is None:
        lines.append("## Nothing to do")
        lines.append("")
        lines.append("The queue is empty and no sweep target was available. Stop and report: the maintained docs match the tree.")
        return "\n".join(lines) + "\n"

    play = RULE_PLAYBOOK.get(chosen.get("rule"), DEFAULT_PLAYBOOK)
    lines.append("## Do this now")
    lines.append("")
    lines.append(f"**{chosen['title']}**")
    lines.append("")
    lines.append(f"- item: `{chosen['id']}`")
    lines.append(f"- rule: `{chosen['rule']}` · severity: **{_badge(chosen.get('severity', 'low'))}**")
    lines.append(f"- document: `{chosen.get('doc') or '(none)'}`")
    lines.append(f"- priority: {explain_priority(chosen, snapshot)}")
    lines.append("")
    lines.append(chosen.get("detail", ""))
    lines.append("")
    if chosen.get("evidence"):
        lines.append("### Evidence")
        lines.append("")
        for ev in chosen["evidence"]:
            lines.append(f"- {ev}")
        lines.append("")
    lines.append("### Steps")
    lines.append("")
    for index, step in enumerate(play["steps"], start=1):
        lines.append(f"{index}. {step}")
    lines.append("")
    lines.append("### Boundaries")
    lines.append("")
    lines.append(f"- {play.get('forbidden', 'Do not make unrelated changes.')}")
    lines.append("- Work on a side branch. Never commit to `main`. Ask the owner before any push.")
    lines.append("- Never edit a hash-pinned file; route corrections through the errata file.")
    lines.append("")
    lines.append("### Verify")
    lines.append("")
    lines.append("```")
    lines.append("python -m chronicler check --fail-on high")
    lines.append("```")
    lines.append("")
    lines.append("### Done when")
    lines.append("")
    lines.append(f"- The `{chosen['rule']}` finding for `{chosen.get('doc')}` no longer appears.")
    lines.append("- The document still reads naturally; you did not just delete the offending sentence.")
    lines.append("")
    lines.append("### Record it")
    lines.append("")
    lines.append("```")
    lines.append(f'python -m chronicler close {chosen["id"]} --note "what you changed, and how you verified it"')
    lines.append("```")
    lines.append("")

    queue = candidates(state, snapshot)
    rest = [i for i in queue if i["id"] != chosen["id"]]
    if rest:
        lines.append("## Queue after this item")
        lines.append("")
        lines.append("| # | severity | item | document | rule |")
        lines.append("|---|---|---|---|---|")
        for index, item in enumerate(rest[:15], start=1):
            lines.append(
                f"| {index} | {_badge(item.get('severity', 'low'))} | `{item['id']}` | "
                f"`{item.get('doc') or '-'}` | {item.get('rule')} |"
            )
        if len(rest) > 15:
            lines.append(f"| … | | {len(rest) - 15} more | | |")
        lines.append("")
    info_items = [i for i in state["items"] if i.get("status") == "open" and i.get("severity") == "info"]
    if info_items:
        lines.append("## Advisory (does not block)")
        lines.append("")
        for item in info_items[:6]:
            lines.append(f"- {item['title']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_status(snapshot: dict, findings: list[checks.Finding], state: dict) -> str:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    queue = candidates(state, snapshot)
    ref_commit = snapshot.get("ref_commit", {})

    lines = [
        f"ref: {snapshot['ref']} @ {(ref_commit.get('sha') or '?')[:7]} ({ref_commit.get('date')})",
        f"tracked files: {snapshot['counts']['tracked_files']:,} · pins: "
        f"{snapshot['pin_summary']['matching']}/{snapshot['pin_summary']['total']} matching",
        f"remote: {'live' if snapshot.get('remote', {}).get('ok') else 'unavailable'} · "
        f"cycle {state.get('cycle', 0)}",
        "",
        "documents:",
    ]
    for doc in snapshot.get("documents", []):
        state_txt = "present" if doc.get("present") else "MISSING"
        stamp = doc.get("declared_date") or "no date"
        age = util.human_days(doc.get("age_days"))
        pin = " [pinned]" if doc.get("is_pinned") else ""
        lines.append(f"  {doc['class']:<13} {doc['path']:<52} {state_txt:<8} {stamp:<12} ({age}){pin}")
    lines.append("")
    if counts:
        lines.append("findings: " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: checks.SEVERITY_ORDER.get(kv[0], 9))))
    else:
        lines.append("findings: none")
    lines.append(f"open queue: {len(queue)}")
    if queue:
        top = queue[0]
        lines.append(f"next: {top['id']} · {top['severity']} · {top['title']}")
    else:
        lines.append("next: nothing queued; run `tick` to start a deep sweep")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Tick
# --------------------------------------------------------------------------

def append_journal(entry: str) -> None:
    path = journal_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "# Chronicler journal\n\nAppend-only record of what each cycle found and chose.\n",
            encoding="utf-8",
        )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def tick(
    *,
    ref: str | None = None,
    allow_network: bool = True,
    agent: str = "chronicler",
    quiet: bool = False,
) -> dict:
    """One full cycle: collect, check, reconcile, select, remember."""
    manifest = facts.load_manifest()
    snapshot = facts.collect(ref=ref, allow_network=allow_network, manifest=manifest)
    findings = checks.run_checks(snapshot)

    state = load_state()
    state["cycle"] = int(state.get("cycle", 0)) + 1
    now_dt = util.utcnow()
    now = util.iso(now_dt)
    stats = reconcile(state, findings, cycle=state["cycle"], now=now)
    chosen = ensure_sweep(state, snapshot, cycle=state["cycle"], now=now)

    queue = candidates(state, snapshot, now_dt=now_dt)
    if queue:
        chosen = queue[0]
        for item in state["items"]:
            if item["id"] == chosen["id"] and item.get("status") == "open":
                item["status"] = "in_progress"

    state["last_tick"] = now
    state["last_ref"] = snapshot["ref"]
    state["last_snapshot"] = now
    state["agent"] = agent
    state["history"].append({
        "cycle": state["cycle"],
        "at": now,
        "ref": snapshot["ref"],
        "ref_sha": snapshot.get("ref_commit", {}).get("sha"),
        "findings": len(findings),
        "by_severity": _severity_counts(findings),
        "new": stats["new"],
        "resolved": stats["resolved"],
        "reopened": stats["reopened"],
        "chosen": chosen["id"] if chosen else None,
    })
    state["history"] = state["history"][-200:]

    util.write_json(snapshot_path(), snapshot)
    util.write_json(state_path(), state)
    next_path().write_text(render_next(state, snapshot, chosen), encoding="utf-8")

    sev = _severity_counts(findings)
    append_journal(
        f"\n## Cycle {state['cycle']} — {now}\n\n"
        f"- ref `{snapshot['ref']}` @ `{(snapshot.get('ref_commit', {}).get('sha') or '?')[:7]}`\n"
        f"- findings: {len(findings)} ({', '.join(f'{k} {v}' for k, v in sorted(sev.items())) or 'none'})\n"
        f"- new {stats['new']} · resolved {stats['resolved']} · reopened {stats['reopened']}\n"
        f"- next: {chosen['title'] if chosen else 'nothing'}\n"
    )

    if not quiet:
        print(render_next(state, snapshot, chosen))
    return {"snapshot": snapshot, "findings": findings, "state": state, "chosen": chosen}


def _severity_counts(findings: list[checks.Finding]) -> dict:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return counts


# --------------------------------------------------------------------------
# Manual transitions
# --------------------------------------------------------------------------

def find_item(state: dict, item_id: str) -> dict | None:
    for item in state["items"]:
        if item["id"] == item_id:
            return item
    return None


def close_item(item_id: str, note: str = "") -> dict:
    state = load_state()
    item = find_item(state, item_id)
    if item is None:
        raise KeyError(item_id)
    item["status"] = "done"
    item["cycle_closed"] = state.get("cycle", 0)
    item["closed_at"] = util.iso(util.utcnow())
    item["note"] = note or item.get("note", "")
    save_state(state)
    append_journal(
        f"\n### Closed `{item_id}` — {item['closed_at']}\n\n"
        f"- {item['title']}\n- note: {note or '(none)'}\n"
    )
    return item


def defer_item(item_id: str, reason: str = "", until: str | None = None) -> dict:
    state = load_state()
    item = find_item(state, item_id)
    if item is None:
        raise KeyError(item_id)
    item["status"] = "deferred"
    item["defer_reason"] = reason
    item["defer_until"] = until
    save_state(state)
    return item
