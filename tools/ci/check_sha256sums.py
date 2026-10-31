#!/usr/bin/env python3
"""Verify every SHA256SUMS file in the repository (fail-closed).

Plain Python 3 standard library. Run from the repository root:

    python3 tools/ci/check_sha256sums.py              # whole tree
    python3 tools/ci/check_sha256sums.py --repo PATH

A SHA256SUMS file is any file named SHA256SUMS or matching *SHA256SUMS*.txt (directories .git,
.lake, __pycache__ and node_modules are skipped). Each line is "<64 hex>  <path>" (sha256sum
format, "*path" binary marker and "./" prefix allowed; blank lines and "#" comments ignored);
the path is relative to the directory of the SHA256SUMS file and must stay inside the repo.

Every entry must exist and match. The only exceptions are the entries in ALLOWED_MISSING below,
each with a reason; such an entry is accepted only while the file is MISSING. If an allow-listed
file appears (matching or not) or the entry disappears, that is an error too, so the list cannot
go stale silently. Finding no SHA256SUMS file at all, a malformed line, or an unreadable SUMS file
is an error. All failures are reported, not just the first.

Exit status: 0 = all entries verified, 1 = any failure, 2 = usage error.
"""
import argparse
import hashlib
import os
import re
import sys

SKIP_DIRS = {".git", ".lake", "__pycache__", "node_modules"}
NAME_RE = re.compile(r"^(SHA256SUMS|.*SHA256SUMS.*\.txt)$")
LINE_RE = re.compile(r"^([0-9a-fA-F]{64}) [ *](.+)$")

# (SHA256SUMS path relative to repo, entry path as written) -> reason. Accepted only while MISSING.
ALLOWED_MISSING = {
    ("audits/reproductions/b2a95dfbfbe3/SHA256SUMS", "compare_b2a95dfbfbe3_v3.log"):
        "v3 comparison log was never committed (Auditor Seat 002 finding M1). Branch "
        "fix/comparator-v4-gates (Auditor Seat 002) regenerates the log and fixes this SUMS file; "
        "remove this entry when that branch lands on main (the check then errors until you do).",
}


def find_sums(repo):
    out = []
    for d, dirs, files in os.walk(repo, followlinks=True):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            if NAME_RE.match(f):
                out.append(os.path.relpath(os.path.join(d, f), repo).replace(os.sep, "/"))
    return sorted(out)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check(repo):
    errors, notices, seen_allowed = [], [], set()
    sums = find_sums(repo)
    if not sums:
        errors.append("no SHA256SUMS file found in the repository (expected at least one)")
    n_ok = 0
    for srel in sums:
        sdir = os.path.dirname(os.path.join(repo, srel))
        try:
            with open(os.path.join(repo, srel), encoding="utf-8") as f:
                lines = f.read().splitlines()
        except Exception as ex:
            errors.append(f"{srel}: cannot read: {ex}")
            continue
        n_entries = 0
        for i, line in enumerate(lines, 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = LINE_RE.match(line)
            if not m:
                errors.append(f"{srel}:{i}: malformed line (expected '<64 hex>  <path>'): {line[:120]!r}")
                continue
            n_entries += 1
            want, entry = m.group(1).lower(), m.group(2)
            target = os.path.normpath(os.path.join(sdir, entry))
            if os.path.isabs(entry) or os.path.relpath(target, repo).startswith(".."):
                errors.append(f"{srel}:{i}: path escapes the repository: {entry}")
                continue
            key = (srel, entry)
            allowed = ALLOWED_MISSING.get(key)
            if allowed is not None:
                seen_allowed.add(key)
            if not os.path.isfile(target):
                if allowed is not None:
                    notices.append(f"{srel}:{i}: {entry} is missing (allow-listed: {allowed})")
                else:
                    errors.append(f"{srel}:{i}: MISSING {entry}")
                continue
            got = sha256(target)
            if got != want:
                errors.append(f"{srel}:{i}: MISMATCH {entry}: listed {want}, actual {got}")
            elif allowed is not None:
                errors.append(f"{srel}:{i}: {entry} is allow-listed as missing but now exists and "
                              f"matches; remove it from ALLOWED_MISSING in tools/ci/check_sha256sums.py")
            else:
                n_ok += 1
        if n_entries == 0:
            errors.append(f"{srel}: contains no checksum entries")
    for key in sorted(set(ALLOWED_MISSING) - seen_allowed):
        errors.append(f"stale allow-list entry: {key[0]} no longer lists {key[1]}; remove it from "
                      f"ALLOWED_MISSING in tools/ci/check_sha256sums.py")
    return sums, n_ok, errors, notices


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo)
    if not os.path.isdir(repo):
        print(f"ERROR   --repo {a.repo} is not a directory"); return 2
    print(f"== check_sha256sums: {repo}")
    sums, n_ok, errors, notices = check(repo)
    gha = os.environ.get("GITHUB_ACTIONS") == "true"
    for s in sums:
        print(f"SUMS    {s}")
    for n in notices:
        print(f"NOTICE  {n}")
        if gha:
            print(f"::notice::{n}")
    for e in errors:
        print(f"ERROR   {e}")
        if gha:
            print(f"::error::{e}")
    print(f"== result: {len(sums)} SHA256SUMS file(s), {n_ok} entr{'y' if n_ok == 1 else 'ies'} verified, "
          f"{len(notices)} allow-listed, {len(errors)} error(s) -> {'FAIL' if errors else 'PASS'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
