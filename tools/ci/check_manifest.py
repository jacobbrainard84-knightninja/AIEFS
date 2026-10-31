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

Exit status: 0 = all verifiers passed or none present, 1 = a verifier failed, 2 = usage error.
"""
import argparse
import os
import subprocess
import sys

VERIFIERS = [
    # (path, args that accept the "inputs" mode)
    ("AI Agent Audits/evidence/verify_manifest.py", ["--inputs"]),
]


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
    if ran == 0 and os.environ.get("GITHUB_ACTIONS") == "true":
        print("::notice::no manifest verifier found; manifest check skipped")
    print(f"== result: {ran} verifier(s) run, {failed} failed -> {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
