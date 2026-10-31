#!/usr/bin/env python3
"""Current-tree inventory check: registry/artifacts_current.csv matches the tree exactly.

Plain Python 3 standard library plus the `git` command. Run from the repository root:

    python3 tools/ci/check_current_inventory.py
    python3 tools/ci/check_current_inventory.py --repo PATH

Regenerates the inventory in memory with registry/reconciliation/build_current_inventory.py and
compares it with the committed registry/artifacts_current.csv:

  ERROR  INVENTORY_MISSING    registry/artifacts_current.csv is absent or not tracked
  ERROR  BAD_HEADER           the CSV header is not the generator's COLUMNS
  ERROR  DUPLICATE_ROW        a (container, path) appears more than once
  ERROR  NOT_INVENTORIED      a tracked file (or zip member) has no row
  ERROR  NOT_IN_TREE          a row names a file (or member) that is not tracked / not in the archive
  ERROR  SHA_MISMATCH         a row's sha256 or size_bytes differs from the bytes in the tree
  ERROR  SNAPSHOT_FIELDS      snapshot_artifact_id / snapshot_sha_state differ from registry/artifacts.csv
  ERROR  NOT_CANONICAL        same rows, but the file is not byte-identical to the generator output
                              (order, quoting or line endings)

So every tracked file except the inventory itself appears exactly once with a matching sha256.
Fix every finding the same way: run `python3 registry/reconciliation/build_current_inventory.py`
and commit the result. registry/artifacts.csv (the e47bad1 snapshot) is checked separately by
tools/ci/check_artifact_pins.py and is never rewritten.

Exit status: 0 = pass, 1 = at least one ERROR, 2 = usage / read error.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import os
import subprocess
import sys

IN_GHA = os.environ.get("GITHUB_ACTIONS") == "true"
HERE = os.path.dirname(os.path.abspath(__file__))
GEN_REL = os.path.join("registry", "reconciliation", "build_current_inventory.py")
FIX = "run: python3 registry/reconciliation/build_current_inventory.py, then commit registry/artifacts_current.csv"
MAX_LISTED = 20


def load_generator(repo: str):
    path = os.path.join(repo, GEN_REL)
    if not os.path.isfile(path):
        path = os.path.join(os.path.dirname(os.path.dirname(HERE)), GEN_REL)
    spec = importlib.util.spec_from_file_location("build_current_inventory", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def is_tracked(repo: str, rel: str) -> bool:
    r = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=repo, capture_output=True)
    return r.returncode == 0


def check(repo: str) -> list[tuple[str, str]]:
    gen = load_generator(repo)
    findings: list[tuple[str, str]] = []
    out = os.path.join(repo, gen.OUTPUT)
    if not os.path.isfile(out) or not is_tracked(repo, gen.OUTPUT):
        return [("INVENTORY_MISSING", f"{gen.OUTPUT} is absent or not tracked; {FIX}")]
    expected_rows = gen.build_rows(repo)
    expected_bytes = gen.render(expected_rows)
    with open(out, "rb") as f:
        actual_bytes = f.read()
    if actual_bytes == expected_bytes:
        return []
    reader = csv.DictReader(io.StringIO(actual_bytes.decode("utf-8", errors="replace"), newline=""))
    if tuple(reader.fieldnames or ()) != tuple(gen.COLUMNS):
        return [("BAD_HEADER", f"header {reader.fieldnames!r} != {list(gen.COLUMNS)!r}; {FIX}")]
    actual: dict[tuple[str, str], dict[str, str]] = {}
    for r in reader:
        key = (r["container"], r["path"])
        if key in actual:
            findings.append(("DUPLICATE_ROW", f"{key[0]} {key[1]}"))
        actual[key] = r
    expected = {(r["container"], r["path"]): r for r in expected_rows}
    for key in sorted(set(expected) - set(actual)):
        findings.append(("NOT_INVENTORIED", f"{key[0]} {key[1]}"))
    for key in sorted(set(actual) - set(expected)):
        findings.append(("NOT_IN_TREE", f"{key[0]} {key[1]}"))
    for key in sorted(set(actual) & set(expected)):
        a, e = actual[key], expected[key]
        if (a["sha256"], a["size_bytes"]) != (e["sha256"], e["size_bytes"]):
            findings.append(("SHA_MISMATCH", f"{key[0]} {key[1]}: listed {a['sha256'][:12]}/{a['size_bytes']}, "
                                             f"tree {e['sha256'][:12]}/{e['size_bytes']}"))
        elif (a["snapshot_artifact_id"], a["snapshot_sha_state"]) != (e["snapshot_artifact_id"], e["snapshot_sha_state"]):
            findings.append(("SNAPSHOT_FIELDS", f"{key[0]} {key[1]}"))
    if not findings:
        findings.append(("NOT_CANONICAL", f"rows match but bytes differ from the generator output; {FIX}"))
    return findings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    a = ap.parse_args(argv)
    print(f"== check_current_inventory: {os.path.abspath(a.repo)}")
    try:
        findings = check(a.repo)
    except Exception as e:  # read / git errors
        print(f"error: {e}", file=sys.stderr)
        return 2
    by_code: dict[str, list[str]] = {}
    for code, msg in findings:
        by_code.setdefault(code, []).append(msg)
    for code, msgs in by_code.items():
        for m in msgs[:MAX_LISTED]:
            print(f"ERROR {code} {m}")
            if IN_GHA:
                print(f"::error::{code} {m}")
        if len(msgs) > MAX_LISTED:
            print(f"ERROR {code} ... and {len(msgs) - MAX_LISTED} more")
    if findings:
        print(f"fix: {FIX}")
    print(f"== result: {len(findings)} error(s) -> {'FAIL' if findings else 'PASS'}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
