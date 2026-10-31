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
A listed verifier that is missing is an ERROR, not a skip: the check fails closed, because a deleted or
moved verifier would otherwise turn the CI manifest check into a silent pass (red-team gap G2).
This wrapper adds no hashes of its own.

Coverage rule (added for red-team G1): the verifier only checks what its manifest lists, so a
"PASSED" manifest that lists nothing would verify OK. For every verifier that is run, this wrapper
also reads the sibling audit_manifest.json and fails if it cannot be read, if files_sha256 lists no
file other than the verifier and the manifest themselves, if a listed file does not exist, or (in
inputs mode) if inputs_sha256 is empty.

Verifier integrity (red-team G2b): the verifier is not trusted just because it exits 0. Before it is run,
it must be a regular file at its listed path (a symlink, or anything that resolves outside the repo, is
an ERROR), and its sha256 must equal its own files_sha256 entry in that manifest (audit_manifest.json is
itself hash-pinned in registry/artifacts.csv, see check_artifact_pins.py). After it runs, its output must
contain the exact success line computed from the manifest, e.g.
    checked 145 published files and 24 inputs; 2 post-manifest logs listed but not hashed
and its last line must be exactly "OK". So a 0-byte, comment-only, `sys.exit(0)` or symlinked stub fails.

Exit status: 0 = all verifiers present and passed, 1 = a verifier failed or is missing, 2 = usage error.
"""
import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys

VERIFIERS = [
    # (path, args that accept the "inputs" mode)
    ("AI Agent Audits/evidence/verify_manifest.py", ["--inputs"]),
]


def _paths(repo, rel):
    """(manifest path, manifest repo-relative path, folder the manifest keys are relative to, verifier key)."""
    evid = os.path.dirname(os.path.join(repo, rel))
    base = os.path.dirname(evid)                      # manifest keys are relative to this folder
    mpath = os.path.join(evid, "audit_manifest.json")
    return mpath, os.path.relpath(mpath, repo), base, os.path.relpath(os.path.join(repo, rel), base).replace(os.sep, "/")


def load_manifest(repo, rel):
    """Return (manifest dict, None) or (None, error message) for the manifest next to verifier `rel`."""
    mpath, mrel, _, _ = _paths(repo, rel)
    try:
        with open(mpath, encoding="utf-8") as f:
            m = json.load(f)
    except Exception as ex:
        return None, f"{mrel}: cannot read manifest: {ex}"
    if not isinstance(m, dict) or not isinstance(m.get("files_sha256"), dict):
        return None, f"{mrel}: files_sha256 is missing or not an object"
    return m, None


def check_verifier_file(repo, rel, m):
    """Return a list of integrity errors for verifier `rel` BEFORE it is run (red-team G2b)."""
    full = os.path.join(repo, rel)
    _, mrel, _, key = _paths(repo, rel)
    real, root = os.path.realpath(full), os.path.realpath(repo)
    if os.path.commonpath([real, root]) != root:
        return [f"{rel} resolves outside the repository (to {real}); refusing to run it"]
    if os.path.islink(full):
        return [f"{rel} is a symlink (to {os.path.relpath(real, root)}); the verifier must be a regular file at its listed path"]
    if not stat.S_ISREG(os.stat(full).st_mode):
        return [f"{rel} is not a regular file; refusing to run it"]
    entry = m["files_sha256"].get(key)
    want = entry.get("sha256") if isinstance(entry, dict) else None
    if not isinstance(want, str):
        return [f"{rel}: {mrel} has no files_sha256 entry '{key}' with a sha256, so the verifier cannot be authenticated"]
    with open(full, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if got != want:
        return [f"{rel}: sha256 {got} does not match {mrel} files_sha256['{key}'] {want}; refusing to run an unverified verifier"]
    return []


def success_line(m, inputs_mode):
    """The exact summary line verify_manifest.py prints for manifest `m` (it must be followed by a final 'OK')."""
    n_in = len(m.get("inputs_sha256") or {}) if inputs_mode else 0
    post = set(m.get("post_manifest_logs") or [])
    return (f"checked {len(m['files_sha256'])} published files" + (f" and {n_in} inputs" if n_in else "")
            + (f"; {len(post)} post-manifest logs listed but not hashed" if post else ""))


def check_coverage(repo, rel, inputs_mode):
    """Return a list of coverage errors for the manifest next to verifier `rel` (red-team G1)."""
    mpath, mrel, base, key = _paths(repo, rel)
    m, err = load_manifest(repo, rel)
    if err:
        return [err]
    files = m["files_sha256"]
    own = {key, os.path.relpath(mpath, base).replace(os.sep, "/")}
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
    gha = os.environ.get("GITHUB_ACTIONS") == "true"

    def error(rel, msg, note=None):
        print(f"ERROR   {msg}")
        if gha:
            print(f"::error file={rel}::{note or msg}")

    for rel, extra in VERIFIERS:
        full = os.path.join(repo, rel)
        if not os.path.lexists(full):
            failed += 1
            error(rel, f"{rel} not found; manifest verifier missing (deleted or moved?), "
                       f"so the manifest hashes were NOT checked", "manifest verifier missing; manifest hashes not checked")
            continue
        m, merr = load_manifest(repo, rel)
        pre = [merr] if merr else check_verifier_file(repo, rel, m)
        if pre:
            failed += 1
            for e in pre:
                error(rel, e)
            print(f"ERROR   {rel} was NOT run, so the manifest hashes were NOT checked")
            continue
        inputs_mode = not a.no_inputs
        cmd = [sys.executable, rel] + (extra if inputs_mode else [])
        print("$ " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
        sys.stdout.flush()
        p = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, errors="replace")
        out = p.stdout + p.stderr
        sys.stdout.write(out if not out or out.endswith("\n") else out + "\n")
        rc = p.returncode
        ran += 1
        if rc != 0:
            failed += 1
            error(rel, f"{rel} exited {rc}", f"manifest verification failed (exit {rc})")
        else:
            want = success_line(m, inputs_mode)
            lines = [ln.rstrip("\r") for ln in p.stdout.splitlines()]
            body = [ln for ln in lines if ln.strip()]
            if want not in lines or not body or body[-1] != "OK":
                failed += 1
                error(rel, f"{rel} exited 0 but did not print its success line '{want}' followed by 'OK'; "
                           f"the manifest hashes are NOT confirmed")
                rc = -1                                  # already counted; don't count coverage errors twice
        cov = check_coverage(repo, rel, inputs_mode)
        for e in cov:
            error(rel, e)
        if cov and rc == 0:
            failed += 1
    print(f"== result: {ran} verifier(s) run, {failed} failed -> {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
