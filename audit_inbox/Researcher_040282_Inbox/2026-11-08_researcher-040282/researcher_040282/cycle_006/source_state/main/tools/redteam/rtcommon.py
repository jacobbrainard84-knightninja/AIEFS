"""Shared helpers for the red-team negative-control suite (stdlib only).

Every test works in a fresh temporary directory. Real repository files are never opened for
writing: a temp "farm" mirrors the repo with symlinks, and a file is tampered by first REMOVING
its symlink in the farm and then writing a new regular file in its place (see tamper()).
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import functools

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable


def run(cmd, cwd=None, env=None, timeout=600):
    """Run a command; return (returncode, combined stdout+stderr text)."""
    e = dict(os.environ)
    e.pop("GITHUB_ACTIONS", None)
    if env:
        e.update(env)
    p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def farm(dst, skip=(".git", "__pycache__")):
    """Mirror REPO into dst: top-level entries become symlinks (cheap, read-only by construction).
    Ignored local byte-code (__pycache__) is left out: it is not part of the tracked tree."""
    os.makedirs(dst, exist_ok=True)
    for name in os.listdir(REPO):
        if name in skip:
            continue
        os.symlink(os.path.join(REPO, name), os.path.join(dst, name))
    return dst


def materialize(root, rel):
    """Turn every symlinked ancestor of root/rel into a real directory of symlinks, so rel itself
    can be replaced without touching the repo. Returns the absolute path of rel inside root."""
    parts = rel.split("/")
    cur = root
    for part in parts[:-1]:
        nxt = os.path.join(cur, part)
        if os.path.islink(nxt):
            target = os.readlink(nxt)
            os.unlink(nxt)
            os.makedirs(nxt)
            for name in os.listdir(target):
                os.symlink(os.path.join(target, name), os.path.join(nxt, name))
        cur = nxt
    return os.path.join(root, *parts)


def tamper(root, rel, fn):
    """Replace root/rel with fn(original_bytes). The symlink is unlinked first, so the real file
    is only ever read. Returns the absolute path of the new file."""
    p = materialize(root, rel)
    with open(p, "rb") as f:
        data = f.read()
    os.unlink(p)
    with open(p, "wb") as f:
        f.write(fn(data))
    return p


def remove(root, rel):
    p = materialize(root, rel)
    os.unlink(p)


def copy_real(root, rel):
    """Replace the symlink root/rel with a real recursive copy (for tools that resolve their own
    path, or that need several files edited)."""
    p = materialize(root, rel)
    if os.path.islink(p):
        target = os.readlink(p)
        os.unlink(p)
        shutil.copytree(target, p, symlinks=False)
    return p


ACCEPTED = "checker ACCEPTED a known-false input"


def gap(reason):
    """Mark a known GAP: the checker accepts a false input today. The test is an expectedFailure,
    but only the 'checker ACCEPTED' assertion counts; any other exception (a broken fixture)
    is turned into a visible skip so a broken GAP test can never look like a confirmed GAP.
    If the checker starts rejecting the input, unittest reports an UNEXPECTED SUCCESS."""
    def deco(fn):
        @functools.wraps(fn)
        def inner(self, *a, **k):
            try:
                return fn(self, *a, **k)
            except AssertionError as ex:
                if ACCEPTED in str(ex):
                    raise
                raise unittest.SkipTest(f"GAP fixture broken (not a confirmed GAP): {ex}")
            except unittest.SkipTest:
                raise
            except Exception as ex:
                raise unittest.SkipTest(f"GAP fixture broken (not a confirmed GAP): {ex!r}")
        inner.gap_reason = reason
        return unittest.expectedFailure(inner)
    return deco


class TempDirMixin:
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="aiefs_redteam_")
        self.tmp = self._td.name

    def tearDown(self):
        self._td.cleanup()

    def assertRejected(self, rc, out, *needles):
        self.assertNotEqual(rc, 0, ACCEPTED + ":\n" + out[-3000:])
        for n in needles:
            self.assertIn(n, out, out[-3000:])
