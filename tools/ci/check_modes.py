#!/usr/bin/env python3
"""File-mode check: scripts that should be executable are 100755 in the git index.

Plain Python 3 standard library plus the `git` command. Run from the repository root:

    python3 tools/ci/check_modes.py              # report; always exit 0 (warn-only)
    python3 tools/ci/check_modes.py --strict     # exit 1 if any expected script is not 100755
    python3 tools/ci/check_modes.py --repo PATH

What is checked (index modes from `git ls-files -s`, not the working tree)
--------------------------------------------------------------------------
  KNOWN_NOT_EXEC    warn   a script on the known list is not 100755. The known list is
                           KNOWN_EXECUTABLES below plus every path listed under the
                           "Executable bits to restore" item of PUSH_NOTES.md (backtick paths
                           and the arguments of `git update-index --chmod=+x ...`).
  SHEBANG_NOT_EXEC  warn   any other tracked regular file whose content starts with "#!" is
                           not 100755. Many shebang files are imported as modules, so these are
                           listed individually but annotated once, as a summary.

Under GitHub Actions (GITHUB_ACTIONS=true) findings are also printed as ::warning annotations.
The check is warn-only until the owner restores the executable bits (see PUSH_NOTES.md);
switch the CI step to --strict afterwards if desired.

Exit status: 0 = done (always, unless --strict and a known-list script is not 100755),
1 = --strict failure, 2 = usage / git error.
"""
import argparse
import os
import re
import subprocess
import sys

IN_GHA = os.environ.get("GITHUB_ACTIONS") == "true"
KNOWN_EXECUTABLES = (
    "lean/AIEFProofs/check_lean.sh",
    "tools/sync/download_new.sh",
    "tools/sync/tests/run_tests.sh",
    "tools/sync/untrack_artifacts.sh",
    # Added by review r026 (integration/round5): command-line entry points with a #! line. The owner's
    # git push restores their bits (OWNER_STEAMDECK_COMMANDS.md); until then --strict fails on them.
    # Paths not tracked yet (the freezing branch) are reported as NOTICE, not errors.
    "lean/AIEFProofsKn/check_lean_kn.sh",
    "lean/AIEFFreezeCore/check_lean_freeze.sh",
    "research/freezing/lean/check.sh",
    "tools/ci/check_artifact_pins.py",
    "tools/ci/check_current_inventory.py",
    "tools/ci/check_modes.py",
    "tools/ci/lean_presence.sh",
    "audits/engineering/validate_registry_against_tree.py",
    "audits/engineering/verify_inventory_current.py",
    "registry/reconciliation/build_claims_reconciliation.py",
    "registry/reconciliation/build_current_inventory.py",
)
EXEC_MODE = "100755"


def annotate(kind, path, message, level="warning"):
    if IN_GHA:
        safe = path.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        safe = safe.replace(",", "%2C").replace(":", "%3A")
        print(f"::{level} file={safe},title={kind}::{message}")


def parse_push_notes(text):
    """Paths named under the 'Executable bits to restore' item of PUSH_NOTES.md."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.search(r"executable bits?", line, re.I) and re.match(r"\s*\d+\.", line):
            start = i
            break
    if start is None:
        return []
    section = []
    for line in lines[start + 1:]:
        if re.match(r"\d+\.\s", line):  # next top-level numbered item
            break
        section.append(line)
    found = []
    for line in section:
        if "--chmod=+x" in line:
            found.extend(tok for tok in line.split("--chmod=+x", 1)[1].split() if "/" in tok)
        for tok in re.findall(r"`([^`\s]+)`", line):
            # repo-relative paths only; bare names such as `lint_claims.py` are prose
            if "/" in tok and re.search(r"\.(sh|py|bash|pl)$", tok):
                found.append(tok)
    return list(dict.fromkeys(found))


def index_entries(repo):
    out = subprocess.run(["git", "-C", repo, "ls-files", "-s", "-z"], capture_output=True, check=True).stdout
    entries = {}
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, obj, _stage = meta.decode().split()
        entries[path.decode("utf-8", "surrogateescape")] = (mode, obj)
    return entries


def shebang_objects(repo, entries):
    """Return the set of blob ids (regular files only) whose content starts with '#!'."""
    objs = sorted({obj for mode, obj in entries.values() if mode in ("100644", "100755")})
    if not objs:
        return set()
    proc = subprocess.run(["git", "-C", repo, "cat-file", "--batch"], input=("\n".join(objs) + "\n").encode(),
                          capture_output=True, check=True)
    data, result, pos = proc.stdout, set(), 0
    while pos < len(data):
        nl = data.index(b"\n", pos)
        header = data[pos:nl].split()
        pos = nl + 1
        if len(header) < 3 or header[1] == b"missing":
            continue
        size = int(header[2])
        if data[pos:pos + 2] == b"#!":
            result.add(header[0].decode())
        pos += size + 1
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--push-notes", default="PUSH_NOTES.md", help="path relative to --repo")
    ap.add_argument("--strict", action="store_true", help="exit 1 if a known-list script is not 100755")
    args = ap.parse_args(argv)
    try:
        entries = index_entries(args.repo)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"ERROR: cannot read git index in {args.repo}: {exc}")
        return 2

    known = list(KNOWN_EXECUTABLES)
    notes_path = os.path.join(args.repo, args.push_notes)
    if os.path.isfile(notes_path):
        with open(notes_path, encoding="utf-8") as f:
            known += parse_push_notes(f.read())
    known = list(dict.fromkeys(known))

    known_bad, missing = [], []
    for path in known:
        if path not in entries:
            missing.append(path)
        elif entries[path][0] != EXEC_MODE:
            known_bad.append((path, entries[path][0]))
    try:
        shebang_ids = shebang_objects(args.repo, entries)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: cannot read blobs with git cat-file in {args.repo}: {exc}")
        return 2
    shebang_bad = sorted(
        (p, m) for p, (m, o) in entries.items() if m == "100644" and o in shebang_ids and p not in known
    )

    level = "ERROR" if args.strict else "WARNING"
    for path, mode in known_bad:
        print(f"{level} KNOWN_NOT_EXEC {path}: mode {mode}, expected {EXEC_MODE}")
        annotate("KNOWN_NOT_EXEC", path, f"mode {mode}, expected {EXEC_MODE} (see PUSH_NOTES.md)", level.lower())
    for path in missing:
        print(f"NOTICE known script not tracked: {path}")
    for path, mode in shebang_bad:
        print(f"WARNING SHEBANG_NOT_EXEC {path}: mode {mode}, has #! line")
    if shebang_bad:
        annotate("SHEBANG_NOT_EXEC", shebang_bad[0][0],
                 f"{len(shebang_bad)} tracked file(s) with a #! line are not {EXEC_MODE}; see job log")
    print(f"check_modes: {len(known) - len(missing)} known script(s) checked, {len(known_bad)} not executable; "
          f"{len(shebang_bad)} other shebang file(s) not executable "
          f"({'warn-only' if not args.strict else '--strict: known-list scripts are errors, others warn-only'})")
    # --strict promotes KNOWN_NOT_EXEC to errors; SHEBANG_NOT_EXEC stays a warning in both modes.
    errors = len(known_bad) if args.strict else 0
    warnings = len(shebang_bad) + (0 if args.strict else len(known_bad))
    failed = errors > 0
    why = " (--strict: known-list scripts not 100755 count as errors)" if args.strict else ""
    print(f"== result: {errors} error(s), {warnings} warning(s){why} -> {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
