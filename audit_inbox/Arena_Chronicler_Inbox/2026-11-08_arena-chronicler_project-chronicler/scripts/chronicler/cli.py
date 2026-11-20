"""Command line interface: ``python -m chronicler <command>``.

Commands are deliberately tiny so an agent can chain them without guessing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import checks, facts, loop, util

FAIL_LEVELS = {"none": 99, "low": 3, "medium": 2, "high": 1, "critical": 0}


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ref", default=None, help="git ref to inspect (default from docs_manifest.json)")
    parser.add_argument("--offline", action="store_true", help="skip git ls-remote")


def cmd_collect(args: argparse.Namespace) -> int:
    snapshot = facts.collect(ref=args.ref, allow_network=not args.offline)
    if args.out:
        util.write_json(Path(args.out), snapshot)
    if args.json:
        print(json.dumps(snapshot, indent=2))
    else:
        print(f"ref        {snapshot['ref']} @ {(snapshot['ref_commit']['sha'] or '?')[:7]}")
        print(f"files      {snapshot['counts']['tracked_files']:,} tracked")
        print(f"pins       {snapshot['pin_summary']['matching']}/{snapshot['pin_summary']['total']} matching")
        print(f"remote     {'live' if snapshot['remote']['ok'] else 'unavailable: ' + str(snapshot['remote']['error'])}")
        print(f"documents  {sum(1 for d in snapshot['documents'] if d['present'])}/{len(snapshot['documents'])} present")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    snapshot = facts.collect(ref=args.ref, allow_network=not args.offline)
    findings = checks.run_checks(snapshot)
    if args.json:
        print(json.dumps([f.to_dict() for f in findings], indent=2))
    else:
        if not findings:
            print(f"no drift detected against {snapshot['ref']}")
        for finding in findings:
            location = finding.doc + (f":{finding.line}" if finding.line else "")
            print(f"[{finding.severity.upper():<8}] {finding.rule:<22} {location}")
            print(f"           {finding.title}")
            if args.verbose:
                print(f"           {finding.detail}")
                for ev in finding.evidence[:6]:
                    print(f"           - {ev}")
        counts: dict[str, int] = {}
        for finding in findings:
            counts[finding.severity] = counts.get(finding.severity, 0) + 1
        if findings:
            print()
            print("summary: " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: checks.SEVERITY_ORDER.get(kv[0], 9))))
    threshold = FAIL_LEVELS[args.fail_on]
    worst = min((checks.SEVERITY_ORDER.get(f.severity, 9) for f in findings), default=99)
    return 1 if worst <= threshold else 0


def cmd_status(args: argparse.Namespace) -> int:
    snapshot = facts.collect(ref=args.ref, allow_network=not args.offline)
    findings = checks.run_checks(snapshot)
    state = loop.load_state()
    print(loop.render_status(snapshot, findings, state))
    return 0


def cmd_tick(args: argparse.Namespace) -> int:
    result = loop.tick(ref=args.ref, allow_network=not args.offline, agent=args.agent, quiet=args.quiet)
    if args.json:
        chosen = result["chosen"]
        print(json.dumps({
            "cycle": result["state"]["cycle"],
            "findings": len(result["findings"]),
            "chosen": chosen["id"] if chosen else None,
            "title": chosen["title"] if chosen else None,
            "next_file": str(loop.next_path()),
        }, indent=2))
    return 0


def cmd_queue(args: argparse.Namespace) -> int:
    state = loop.load_state()
    snapshot = util.read_json(loop.snapshot_path(), {}) or {}
    queue = loop.candidates(state, snapshot)
    if not queue:
        print("queue empty")
        return 0
    print(f"{'#':>3}  {'priority':>8}  {'severity':<8}  {'item':<12}  document")
    for index, item in enumerate(queue, start=1):
        print(f"{index:>3}  {loop._score(item, snapshot, util.utcnow()):>8}  {item['severity']:<8}  {item['id']:<12}  {item.get('doc')}")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    try:
        item = loop.close_item(args.item_id, note=args.note or "")
    except KeyError:
        print(f"no such item: {args.item_id}", file=sys.stderr)
        return 2
    print(f"closed {args.item_id}: {item['title']}")
    print("run `python -m chronicler tick` to pick up the next item")
    return 0


def cmd_defer(args: argparse.Namespace) -> int:
    try:
        item = loop.defer_item(args.item_id, reason=args.reason or "", until=args.until)
    except KeyError:
        print(f"no such item: {args.item_id}", file=sys.stderr)
        return 2
    print(f"deferred {args.item_id}: {item['title']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m chronicler",
        description="Keep the AIEFS memory documents true, one cycle at a time.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    collect = sub.add_parser("collect", help="write the deterministic fact snapshot")
    _add_common(collect)
    collect.add_argument("--json", action="store_true", help="print the whole snapshot")
    collect.add_argument("--out", default=None, help="write the snapshot to this path")
    collect.set_defaults(func=cmd_collect)

    check = sub.add_parser("check", help="report drift; exit 1 at or above --fail-on")
    _add_common(check)
    check.add_argument("--json", action="store_true")
    check.add_argument("--verbose", "-v", action="store_true")
    check.add_argument("--fail-on", default="high", choices=sorted(FAIL_LEVELS))
    check.set_defaults(func=cmd_check)

    status = sub.add_parser("status", help="human digest of docs, pins and queue")
    _add_common(status)
    status.set_defaults(func=cmd_status)

    tick = sub.add_parser("tick", help="one full cycle; writes loop/NEXT.md")
    _add_common(tick)
    tick.add_argument("--agent", default="chronicler")
    tick.add_argument("--quiet", action="store_true")
    tick.add_argument("--json", action="store_true")
    tick.set_defaults(func=cmd_tick)

    queue = sub.add_parser("queue", help="list the open work queue")
    queue.set_defaults(func=cmd_queue)

    close = sub.add_parser("close", help="mark an item done")
    close.add_argument("item_id")
    close.add_argument("--note", default="")
    close.set_defaults(func=cmd_close)

    defer = sub.add_parser("defer", help="park an item, optionally until a date")
    defer.add_argument("item_id")
    defer.add_argument("--reason", default="")
    defer.add_argument("--until", default=None, help="YYYY-MM-DD")
    defer.set_defaults(func=cmd_defer)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except util.GitError as exc:
        print(f"chronicler: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
