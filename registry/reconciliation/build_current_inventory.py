#!/usr/bin/env python3
"""Build registry/artifacts_current.csv, the inventory of the CURRENT tree (generated; never hand-edit).

Plain Python 3 standard library plus the `git` command. Run from the repository root:

    python3 registry/reconciliation/build_current_inventory.py            # (re)write the CSV
    python3 registry/reconciliation/build_current_inventory.py --stdout   # print it instead
    python3 tools/ci/check_current_inventory.py                           # CI check: is it current?

Two inventories, two jobs (see registry/README.md, "Which inventory is authoritative for what"):
  registry/artifacts.csv          the e47bad1 snapshot (2,898 rows: 2,760 tracked files + 138 zip
                                  members), with classifications. Frozen (ERRATA E7) and pinned by
                                  tools/ci/check_artifact_pins.py; its name is kept, it is not renamed.
  registry/artifacts_current.csv  this file's output: one row per tracked file of the current tree and
                                  per file member of the tracked .zip archives, with sha256 and size.
                                  It changes with every commit that adds, removes or edits a file, so
                                  regenerate it in the same commit (the CI check fails otherwise).

Rows
  container          "worktree", or "zip:<archive path>" for a member of a tracked .zip
  path               tracked path (git ls-files), or member name inside the archive
  sha256, size_bytes  of the bytes on disk (for a tracked symlink: of the link target string)
  snapshot_artifact_id  the artifacts.csv artifact_id with the same (container, path), else empty
  snapshot_sha_state   same_sha | changed_sha (vs the snapshot's pinned sha256) | not_in_snapshot

Deterministic: rows sorted by (container, path) as UTF-8 bytes, LF line endings, no timestamps,
no file modes (a chmod-only commit does not change this file). registry/artifacts_current.csv is the
only tracked file left out (it cannot contain its own hash); the check reports it if it is missing.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import subprocess
import sys
import zipfile

OUTPUT = "registry/artifacts_current.csv"
SNAPSHOT = "registry/artifacts.csv"
COLUMNS = ("container", "path", "sha256", "size_bytes", "snapshot_artifact_id", "snapshot_sha_state")
SELF_EXCLUDED = (OUTPUT,)


def tracked_files(repo: str) -> list[str]:
    out = subprocess.run(["git", "-c", "core.quotepath=false", "ls-files", "-z"], cwd=repo,
                         check=True, capture_output=True).stdout
    return sorted({p.decode("utf-8") for p in out.split(b"\0") if p})


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: str) -> tuple[str, int]:
    if os.path.islink(path):
        data = os.readlink(path).encode("utf-8")
        return _sha(data), len(data)
    h, n = hashlib.sha256(), 0
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
            n += len(chunk)
    return h.hexdigest(), n


def load_snapshot(repo: str) -> dict[tuple[str, str], tuple[str, str]]:
    p = os.path.join(repo, SNAPSHOT)
    if not os.path.isfile(p):
        return {}
    with open(p, newline="", encoding="utf-8") as f:
        return {(r["container"], r["path"]): (r["artifact_id"], r["sha256"]) for r in csv.DictReader(f)}


class MissingTrackedFile(Exception):
    pass


def build_rows(repo: str) -> list[dict[str, str]]:
    """Inventory rows for the tree at `repo` (tracked files as they are on disk)."""
    snap = load_snapshot(repo)
    rows = []

    def add(container, path, sha, size):
        sid, ssha = snap.get((container, path), ("", ""))
        state = "not_in_snapshot" if not sid else ("same_sha" if ssha == sha else "changed_sha")
        rows.append({"container": container, "path": path, "sha256": sha, "size_bytes": str(size),
                     "snapshot_artifact_id": sid, "snapshot_sha_state": state})

    for rel in tracked_files(repo):
        if rel in SELF_EXCLUDED:
            continue
        fp = os.path.join(repo, rel)
        if not os.path.lexists(fp):
            raise MissingTrackedFile(rel)
        sha, size = file_digest(fp)
        add("worktree", rel, sha, size)
        if rel.lower().endswith(".zip") and not os.path.islink(fp) and zipfile.is_zipfile(fp):
            with zipfile.ZipFile(fp) as zf:
                for zi in zf.infolist():
                    if zi.is_dir():
                        continue
                    data = zf.read(zi.filename)
                    add(f"zip:{rel}", zi.filename, _sha(data), len(data))
    rows.sort(key=lambda r: (r["container"].encode("utf-8"), r["path"].encode("utf-8")))
    return rows


def render(rows: list[dict[str, str]]) -> bytes:
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".", help="repository root (default: current directory)")
    ap.add_argument("--stdout", action="store_true", help="print the CSV instead of writing it")
    a = ap.parse_args(argv)
    try:
        data = render(build_rows(a.repo))
    except MissingTrackedFile as e:
        print(f"error: tracked file missing on disk: {e}", file=sys.stderr)
        return 2
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if a.stdout:
        sys.stdout.buffer.write(data)
    else:
        with open(os.path.join(a.repo, OUTPUT), "wb") as f:
            f.write(data)
        nrows = data.count(b"\n") - 1
        print(f"{OUTPUT}: {nrows} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
