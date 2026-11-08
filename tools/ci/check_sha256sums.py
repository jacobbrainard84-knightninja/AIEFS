#!/usr/bin/env python3
"""Verify every checksum list (SHA256SUMS file) tracked in the repository (fail-closed).

Plain Python 3 standard library plus git. Run from the repository root:

    python3 tools/ci/check_sha256sums.py              # this checkout
    python3 tools/ci/check_sha256sums.py --repo PATH  # PATH must be the top of a git work tree

Discovery uses `git ls-files` (tracked files only; no tree walk, so untracked files and symlink
loops cannot change the result). A tracked file is a checksum list if
  * its name is SHA256SUMS or matches *SHA256SUMS*.txt, or
  * it is listed in EXTRA_INCLUDE below (with a reason).
Any other tracked file whose name looks like a hash list (contains "sha256", "sums" or "hashes",
any case, with no extension or .txt/.sha256/.sums) must be listed in EXCLUDED with a reason;
an unclassified one is an error, so a new hash list cannot be skipped silently. EXTRA_INCLUDE
and EXCLUDED entries that are no longer tracked are errors too (stale).

Each line of a list is "<64 hex>  <path>" (sha256sum format; "*path" binary marker and "./"
prefix allowed; blank lines and "#" comments ignored). The path is relative to the directory
of the list. It must not be absolute or contain "..", and after resolving symlinks
(os.path.realpath) it must stay inside the repository: an in-repo symlink that points outside
the repository is rejected.

Every entry must exist and match. The only exceptions are the entries in ALLOWED_MISSING below,
each with a reason; such an entry is accepted only while the file is MISSING. If an allow-listed
file appears (matching or not) or the entry disappears from its list, that is an error too, so
the allow-list cannot go stale silently. Finding no checksum list at all, a malformed line, an
empty list or an unreadable list is an error. All failures are reported, not just the first.

Exit status: 0 = all entries verified, 1 = any failure, 2 = usage error.

Checker isolation (Researcher 001 audit of 18e542c, S-B1; same class as check_manifest.py B1): run as a
script, this file first re-executes itself as `python -I -B`, before importing anything a sibling file could
shadow. Without that, tools/ci/ (the script folder), the current folder and PYTHONPATH are on sys.path, so a
committed tools/ci/hashlib.py (or argparse.py, re.py, subprocess.py ...) would run inside this checker and
could report the listed digest for a tampered file, or print a forged PASS. sys is built in and os is already
loaded at interpreter start-up, so neither can be shadowed. Interpreter start-up hooks (sitecustomize /
usercustomize outside the repo) run before any script code and remain the documented residual (N1).
"""
import sys as _sys
if __name__ == "__main__" and not _sys.flags.isolated:
    import os as _os
    _os.execv(_sys.executable, [_sys.executable, "-I", "-B", _os.path.abspath(__file__)] + _sys.argv[1:])
import argparse
import hashlib
import os
import re
import subprocess
import sys

NAME_RE = re.compile(r"^(SHA256SUMS|.*SHA256SUMS.*\.txt)$")
CANDIDATE_RE = re.compile(r"(sha256|sums|hashes)[^/]*$", re.I)
CANDIDATE_EXT = {"", ".txt", ".sha256", ".sums"}
LINE_RE = re.compile(r"^([0-9a-fA-F]{64}) [ *](.+)$")

# Tracked checksum lists whose name does not match NAME_RE but which are verified anyway.
EXTRA_INCLUDE = {
    "lean/AIEFProofs/AIEF_LEAN_PROJECT_LOCK_HASHES.txt":
        "pins lean-toolchain, lake-manifest.json and lakefile.toml of the Lean project "
        "(sha256sum format, paths relative to lean/AIEFProofs)",
}

# Tracked files that look like hash lists but are NOT verified, each with the reason.
EXCLUDED = {
    "AI Agent Audits/evidence/logs/lean_r4/source_sha256.txt":
        "historical log of the lean_r4 audit run, not a live pin: its paths are relative to "
        "lean/AIEFProofs, and Basic.lean/Smoke.lean were changed after that run on purpose "
        "(ERRATA_2026-10-28.md E7), so it no longer matches by design",
    "twindow_frozen_authority_hashes.txt":
        "historical record from the original machine: absolute /home/deck/... paths outside this repo",
    "twindow_source_hashes_before.txt":
        "historical record from the original machine: absolute /home/deck/... paths outside this repo",
}

# (list path relative to repo, entry path as written) -> reason. Accepted only while MISSING.
ALLOWED_MISSING = {}

# Tests only (never set in CI): take the tracked-file list from this git checkout instead of
# --repo, and also treat it as "inside the repository". The red-team suite uses it to run the
# check on a symlink mirror of the repo (tools/redteam/test_rt_sha256sums.py).
GIT_ROOT = None


def tracked_files(git_root):
    """Return the tracked paths of git_root, or raise RuntimeError."""
    top = subprocess.run(["git", "-C", git_root, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    if top.returncode != 0:
        raise RuntimeError(f"{git_root} is not a git work tree: {top.stderr.strip()}")
    if os.path.realpath(top.stdout.strip()) != os.path.realpath(git_root):
        raise RuntimeError(f"{git_root} is not the top of its git work tree ({top.stdout.strip()})")
    p = subprocess.run(["git", "-C", git_root, "ls-files", "-z"], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {p.stderr.decode(errors='replace').strip()}")
    return sorted(x for x in p.stdout.decode("utf-8", "surrogateescape").split("\0") if x)


def classify(tracked):
    """Return (lists to verify, errors)."""
    tset = set(tracked)
    sums, errors = [], []
    for rel in tracked:
        name = rel.rsplit("/", 1)[-1]
        if NAME_RE.match(name) or rel in EXTRA_INCLUDE:
            sums.append(rel)
        elif rel in EXCLUDED:
            continue
        elif CANDIDATE_RE.search(name) and os.path.splitext(name)[1].lower() in CANDIDATE_EXT:
            errors.append(f"{rel}: looks like a hash list but is not classified; add it to "
                          f"EXTRA_INCLUDE (to verify it) or EXCLUDED (with a reason) in tools/ci/check_sha256sums.py")
    for rel in sorted(set(EXTRA_INCLUDE) - tset):
        errors.append(f"stale EXTRA_INCLUDE entry: {rel} is not tracked; remove it")
    for rel in sorted(set(EXCLUDED) - tset):
        errors.append(f"stale EXCLUDED entry: {rel} is not tracked; remove it")
    return sums, errors


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def inside(path, roots):
    real = os.path.realpath(path)
    return any(real == r or real.startswith(r + os.sep) for r in roots)


def check(repo, git_root=None):
    git_root = git_root or repo
    roots = {os.path.realpath(repo), os.path.realpath(git_root)}
    errors, notices, seen_allowed = [], [], set()
    try:
        tracked = tracked_files(git_root)
    except RuntimeError as ex:
        return [], 0, [str(ex)], []
    sums, errors = classify(tracked)
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
            if os.path.isabs(entry) or ".." in entry.replace("\\", "/").split("/") \
                    or os.path.relpath(target, repo).startswith(".."):
                errors.append(f"{srel}:{i}: path escapes the repository: {entry}")
                continue
            if not inside(target, roots):
                errors.append(f"{srel}:{i}: path escapes the repository via a symlink: {entry} "
                              f"-> {os.path.realpath(target)}")
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
    sums, n_ok, errors, notices = check(repo, GIT_ROOT)
    gha = os.environ.get("GITHUB_ACTIONS") == "true"
    for s in sums:
        print(f"SUMS    {s}")
    for rel, why in sorted(EXCLUDED.items()):
        print(f"SKIP    {rel} (excluded: {why})")
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
