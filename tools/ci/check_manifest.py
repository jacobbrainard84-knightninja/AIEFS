#!/usr/bin/env python3
"""Run the repository's own manifest hash verification, if that tooling exists.

Plain Python 3 standard library. Run from the repository root:

    python3 tools/ci/check_manifest.py              # published files + hashed repo inputs
    python3 tools/ci/check_manifest.py --no-inputs  # published files only
    python3 tools/ci/check_manifest.py --repo PATH

It looks for these verifiers (repo-relative) and runs each one that exists, from the repo root:
    AI Agent Audits/evidence/verify_manifest.py   (checks audit_manifest.json: size + sha256 of every
                                                   published audit file, and with --inputs the hashed
                                                   repository inputs such as runs/ and the 1.3/1.4 scripts)
If none exists, it prints a notice and exits 0 (not a failure). This wrapper adds no hashes of its own.

Coverage rule (added for red-team G1): the verifier only checks what its manifest lists, so a
"PASSED" manifest that lists nothing would verify OK. For every verifier that is run, this wrapper
also reads the sibling audit_manifest.json and fails if it cannot be read, if files_sha256 lists no
file other than the verifier and the manifest themselves, if a listed file does not exist, or (in
inputs mode) if inputs_sha256 is empty.

Exit status: 0 = all verifiers passed or none present, 1 = a verifier failed, 2 = usage error.
"""
import argparse
import json
import os
import subprocess
import sys

VERIFIERS = [
    # (path, args that accept the "inputs" mode)
    ("AI Agent Audits/evidence/verify_manifest.py", ["--inputs"]),
]


def check_coverage(repo, rel, inputs_mode):
    """Return a list of coverage errors for the manifest next to verifier `rel` (red-team G1)."""
    evid = os.path.dirname(os.path.join(repo, rel))
    base = os.path.dirname(evid)                      # manifest keys are relative to this folder
    mpath = os.path.join(evid, "audit_manifest.json")
    mrel = os.path.relpath(mpath, repo)
    try:
        with open(mpath, encoding="utf-8") as f:
            m = json.load(f)
    except Exception as ex:
        return [f"{mrel}: cannot read manifest: {ex}"]
    files = m.get("files_sha256") if isinstance(m, dict) else None
    if not isinstance(files, dict):
        return [f"{mrel}: files_sha256 is missing or not an object"]
    own = {os.path.relpath(os.path.join(repo, rel), base).replace(os.sep, "/"),
           os.path.relpath(mpath, base).replace(os.sep, "/")}
    errs = []
    if not [k for k in files if k not in own]:
        errs.append(f"{mrel}: manifest lists no data files beyond the verifier itself "
                    f"({len(files)} entr{'y' if len(files) == 1 else 'ies'} in files_sha256); refusing to PASS an empty manifest")
    for k in sorted(files):
        if not os.path.isfile(os.path.join(base, k)):
            errs.append(f"{mrel}: listed file does not exist: {k}")
    if inputs_mode and not m.get("inputs_sha256"):
        errs.append(f"{mrel}: inputs_sha256 is empty, so the --inputs check would verify nothing")
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--no-inputs", action="store_true", help="skip the hashed-input check")
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo)
    if not os.path.isdir(repo):
        print(f"ERROR   --repo {a.repo} is not a directory"); return 2
    print(f"== check_manifest: {repo}")
    ran, failed = 0, 0
    for rel, extra in VERIFIERS:
        if not os.path.isfile(os.path.join(repo, rel)):
            print(f"NOTICE  {rel} not found; skipped")
            continue
        cmd = [sys.executable, rel] + ([] if a.no_inputs else extra)
        print("$ " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
        sys.stdout.flush()
        rc = subprocess.run(cmd, cwd=repo).returncode
        ran += 1
        if rc != 0:
            failed += 1
            print(f"ERROR   {rel} exited {rc}")
            if os.environ.get("GITHUB_ACTIONS") == "true":
                print(f"::error file={rel}::manifest verification failed (exit {rc})")
        cov = check_coverage(repo, rel, not a.no_inputs)
        for e in cov:
            print(f"ERROR   {e}")
            if os.environ.get("GITHUB_ACTIONS") == "true":
                print(f"::error file={rel}::{e}")
        if cov and rc == 0:
            failed += 1
    if ran == 0 and os.environ.get("GITHUB_ACTIONS") == "true":
        print("::notice::no manifest verifier found; manifest check skipped")
    print(f"== result: {ran} verifier(s) run, {failed} failed -> {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
