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

Verifier integrity (red-team G2b; Researcher 001 audit of 14072c3). The verifier is not trusted just
because it exits 0. Before it is run:
  - it must be a regular file at its listed path; a symlink (the file itself or any folder between the
    repo root and it), or anything that resolves outside the repo, is an ERROR;
  - it must be readable, and its sha256 must equal its own files_sha256 entry in audit_manifest.json
    (a manifest with a duplicate JSON key is an ERROR, so a second, last-wins entry cannot hide);
  - its folder must not contain a *.py file that the manifest does not list, or a __pycache__ folder
    (a planted hashlib.py / json.py / glob.py / pathlib.py would shadow the standard library).
It is then run in isolated mode (python -I -B: no script folder, current folder or PYTHON* variables
on sys.path), from the exact bytes that were hashed (passed on stdin and exec'd with __file__ set to its
real path, so it still finds its manifest), so neither a shadow module nor a swap of the file between
the hash and the run changes what executes. After it runs, its last two non-empty stdout lines must be
exactly the success line computed from the manifest, e.g.
    checked 145 published files and 24 inputs; 2 post-manifest logs listed but not hashed
followed by "OK", each printed exactly once, and no output line may look like a problem report
(MISSING / SIZE / SHA256 / UNLISTED / INPUT / FAILED ..., or "problem(s)").

What this does NOT catch (residual, documented honestly): audit_manifest.json is NOT pinned anywhere
outside itself. registry/artifacts.csv has no rows under 'AI Agent Audits/', and check_artifact_pins.py
does not cover it. So a stub verifier whose new sha256 is written into the manifest, and which prints
the computed success line and OK, passes every CI check; the success line is a pure function of the
manifest and only stops lazy stubs (0-byte, comment-only, sys.exit(0)). Today only the red-team suite
(tools/redteam/test_rt_hashes.py, which compares against the real verifier's source) catches that, and
the red-team suite does not run in CI. The real defence is an owner item: pin audit_manifest.json and
verify_manifest.py outside the manifest, somewhere CI checks (e.g. expected-sha256 constants here or
rows in registry/artifacts.csv), and make the red-team suite a required CI check.

Exit status: 0 = all verifiers present and passed, 1 = a verifier failed or is missing, 2 = usage error.

Wrapper isolation (Researcher 001 audit of 92c5d77, B1): run as a script, this file first re-executes itself
as `python -I -B`, before importing anything a sibling file could shadow. Without that, tools/ci/ (the script
folder), the current folder and PYTHONPATH are on sys.path, so a committed tools/ci/hashlib.py (or json.py,
subprocess.py, argparse.py, re.py ...) would run inside this wrapper and could print a PASS result over a
tampered tree. sys is built in and os is already loaded at interpreter start-up, so neither can be shadowed.
"""
import sys as _sys
if __name__ == "__main__" and not _sys.flags.isolated:
    import os as _os
    _os.execv(_sys.executable, [_sys.executable, "-I", "-B", _os.path.abspath(__file__)] + _sys.argv[1:])
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys

VERIFIERS = [
    # (path, args that accept the "inputs" mode)
    ("AI Agent Audits/evidence/verify_manifest.py", ["--inputs"]),
]

# Runs the verifier from the exact bytes on stdin (the ones that were hashed), as if it were the script at
# argv[1]: __file__ is that path, so it locates its manifest exactly as `python <path>` would.
BOOTSTRAP = ("import sys\n"
             "p = sys.argv[1]; src = sys.stdin.buffer.read(); sys.argv = sys.argv[1:]\n"
             "exec(compile(src, p, 'exec'), {'__name__': '__main__', '__file__': p, '__builtins__': __builtins__})\n")
PROBLEM = re.compile(r"\s*(MISSING|SIZE|SHA256|UNLISTED|INPUT|FAILED)\b|.*\bproblem\(s\)")


def _no_duplicate_keys(pairs):
    seen = set()
    for k, _ in pairs:
        if k in seen:
            raise ValueError(f"duplicate key '{k}' in a JSON object")
        seen.add(k)
    return dict(pairs)


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
            m = json.load(f, object_pairs_hook=_no_duplicate_keys)
    except Exception as ex:
        return None, f"{mrel}: cannot read manifest: {ex}"
    if not isinstance(m, dict) or not isinstance(m.get("files_sha256"), dict):
        return None, f"{mrel}: files_sha256 is missing or not an object"
    return m, None


def check_verifier_file(repo, rel, m):
    """Return (list of integrity errors, verifier bytes) for verifier `rel` BEFORE it is run (red-team G2b).
    The bytes returned are the ones that were hashed; they are what gets executed."""
    full = os.path.join(repo, rel)
    _, mrel, base, key = _paths(repo, rel)
    parts = rel.split("/")
    for i in range(1, len(parts)):                    # F5: a symlinked folder on the way is refused too
        sub = "/".join(parts[:i])
        if os.path.islink(os.path.join(repo, sub)):
            return [f"{sub} is a symlink (a folder on the verifier's path); refusing to run {rel}"], None
    real, root = os.path.realpath(full), os.path.realpath(repo)
    if os.path.commonpath([real, root]) != root:
        return [f"{rel} resolves outside the repository (to {real}); refusing to run it"], None
    if os.path.islink(full):
        return [f"{rel} is a symlink (to {os.path.relpath(real, root)}); the verifier must be a regular file at its listed path"], None
    if not stat.S_ISREG(os.stat(full).st_mode):
        return [f"{rel} is not a regular file; refusing to run it"], None
    entry = m["files_sha256"].get(key)
    want = entry.get("sha256") if isinstance(entry, dict) else None
    if not isinstance(want, str):
        return [f"{rel}: {mrel} has no files_sha256 entry '{key}' with a sha256, so the verifier cannot be authenticated"], None
    try:
        with open(full, "rb") as f:
            data = f.read()
    except OSError as e:                              # F4: a named error, not a traceback
        return [f"{rel}: cannot be read ({type(e).__name__}: {e.strerror or e}), so the verifier cannot be authenticated"], None
    got = hashlib.sha256(data).hexdigest()
    if got != want:
        return [f"{rel}: sha256 {got} does not match {mrel} files_sha256['{key}'] {want}; refusing to run an unverified verifier"], None
    # F1: nothing importable may sit beside the verifier unless the manifest lists (and so hashes) it
    edir = os.path.dirname(rel)
    errs = []
    for name in sorted(os.listdir(os.path.dirname(full))):
        if name == "__pycache__":
            errs.append(f"{edir}/{name}: bytecode cache folder beside the verifier; refusing to run the verifier next to it")
        elif name.endswith(".py") and os.path.relpath(os.path.join(os.path.dirname(full), name), base).replace(os.sep, "/") not in m["files_sha256"]:
            errs.append(f"{edir}/{name}: .py file beside the verifier that {mrel} does not list; refusing to run the verifier next to it")
    return errs, (None if errs else data)


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
        pre, code = ([merr], None) if merr else check_verifier_file(repo, rel, m)
        if pre:
            failed += 1
            for e in pre:
                error(rel, e)
            print(f"ERROR   {rel} was NOT run, so the manifest hashes were NOT checked")
            continue
        inputs_mode = not a.no_inputs
        args = [rel] + (extra if inputs_mode else [])
        shown = [sys.executable, "-I", "-B"] + args
        print("$ " + " ".join(f'"{c}"' if " " in c else c for c in shown) + "   (isolated; runs the hashed bytes)")
        sys.stdout.flush()
        cmd = [sys.executable, "-I", "-B", "-c", BOOTSTRAP] + args
        p = subprocess.run(cmd, cwd=repo, input=code, capture_output=True)
        p.stdout = p.stdout.decode("utf-8", "replace"); p.stderr = p.stderr.decode("utf-8", "replace")
        out = p.stdout + p.stderr
        sys.stdout.write(out if not out or out.endswith("\n") else out + "\n")
        rc = p.returncode
        ran += 1
        if rc != 0:
            failed += 1
            error(rel, f"{rel} exited {rc}", f"manifest verification failed (exit {rc})")
        else:
            want = success_line(m, inputs_mode)
            body = [ln.rstrip("\r") for ln in p.stdout.splitlines() if ln.strip()]
            errs = [ln.rstrip("\r") for ln in p.stderr.splitlines() if ln.strip()]
            bad = None
            if body[-2:] != [want, "OK"]:
                bad = f"did not print its success line '{want}' followed by 'OK'"
            else:
                for x in (want, "OK"):
                    if body.count(x) != 1:
                        bad = f"printed '{x}' {body.count(x)} times (expected exactly once)"; break
                else:
                    prob = next((ln for ln in body + errs if PROBLEM.match(ln)), None)
                    if prob is not None:
                        bad = f"printed a problem line '{prob}'"
            if bad:
                failed += 1
                error(rel, f"{rel} exited 0 but {bad}; the manifest hashes are NOT confirmed")
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
