"""Self-tests for tools/ci/check_sha256sums.py: checker isolation (stdlib unittest; synthetic temp repos).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v

Researcher 001 audit of 18e542c, S-B1 (same class as check_manifest.py B1). CI runs
`python tools/ci/check_sha256sums.py` without -I, so tools/ci/ (the script folder) was sys.path[0] and a
committed tools/ci/hashlib.py could report the listed digest for a tampered file and turn a real mismatch
into PASS. These tests run a copy of the real checker as a script from <temp repo>/tools/ci/, exactly as CI
does, against a synthetic git repo with one tampered listed file, and assert on the exact final result line.
A green suite count says nothing about the import boundary by itself; the mutation check for these tests is
to delete the re-exec block at the top of check_sha256sums.py and watch the shadow tests fail.
"""
import ast
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_sha256sums  # noqa: E402

CHECKER = os.path.abspath(check_sha256sums.__file__)
TARGET = "tools/sync/download_new.sh"
SUMS = "tools/sync/SHA256SUMS"
ORIGINAL = b"#!/bin/sh\necho synthetic download helper\n"
TAMPERED = ORIGINAL + b"echo tampered\n"
N_LISTS = 1 + len(check_sha256sums.EXTRA_INCLUDE)     # tools/sync/SHA256SUMS + each extra list
PASS = (f"== result: {N_LISTS} SHA256SUMS file(s), {N_LISTS} entries verified, 0 allow-listed, "
        f"0 error(s) -> PASS")
FAIL = (f"== result: {N_LISTS} SHA256SUMS file(s), {N_LISTS - 1} entr{'y' if N_LISTS - 1 == 1 else 'ies'} "
        f"verified, 0 allow-listed, 1 error(s) -> FAIL")


def sha(b):
    return hashlib.sha256(b).hexdigest()


MISMATCH = (f"ERROR   {SUMS}:1: MISMATCH download_new.sh: listed {sha(ORIGINAL)}, "
            f"actual {sha(TAMPERED)}")

# The S-B1 witness: a hashlib.py that proxies the real module and reports the listed digest for the
# tampered bytes, so the checker's own comparison sees a match.
DIGEST_PROXY = f'''import os as _o, sys as _s
_here = _o.path.dirname(_o.path.abspath(__file__))
_me = _s.modules[__name__]
_saved = list(_s.path)
_s.path[:] = [p for p in _s.path if _o.path.abspath(p or ".") != _here]
del _s.modules["hashlib"]
import hashlib as _real
_s.path[:] = _saved
_s.modules["hashlib"] = _me
_MAP = {{"{sha(TAMPERED)}": "{sha(ORIGINAL)}"}}
class _P:
    def __init__(self, h): self._h = h
    def update(self, b): self._h.update(b)
    def hexdigest(self):
        d = self._h.hexdigest()
        return _MAP.get(d, d)
def sha256(*a, **k): return _P(_real.sha256(*a, **k))
def __getattr__(n): return getattr(_real, n)
'''
# A cruder plant for every other imported stdlib name: print a forged PASS at import time and exit 0.
FORGE = ("import os, sys\n"
         f"print({PASS!r}); sys.stdout.flush(); os._exit(0)\n")
SHADOW_MODS = ("hashlib", "argparse", "re", "subprocess")


class CheckSha256sumsIsolationTests(unittest.TestCase):
    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="cs_iso_"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.write(TARGET, ORIGINAL)
        self.write(SUMS, f"{sha(ORIGINAL)}  download_new.sh\n".encode())
        for i, rel in enumerate(sorted(check_sha256sums.EXTRA_INCLUDE)):   # must be tracked, else "stale"
            payload = f"pinned file {i}\n".encode()
            self.write(os.path.join(os.path.dirname(rel), f"pinned_{i}.txt"), payload)
            self.write(rel, f"{sha(payload)}  pinned_{i}.txt\n".encode())
        for rel in check_sha256sums.EXCLUDED:                               # same
            self.write(rel, b"historical record\n")
        self.ci = os.path.join(self.root, "tools", "ci")
        os.makedirs(self.ci, exist_ok=True)
        shutil.copyfile(CHECKER, os.path.join(self.ci, "check_sha256sums.py"))
        subprocess.run(["git", "init", "-q", self.root], check=True)
        subprocess.run(["git", "-C", self.root, "add", "-A"], check=True)

    def write(self, rel, data):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    def plant(self, where, mod, src):
        p = os.path.join(where, f"{mod}.py")
        with open(p, "w") as f:
            f.write(src)
        self.addCleanup(lambda: os.path.exists(p) and os.unlink(p))
        self.addCleanup(shutil.rmtree, os.path.join(where, "__pycache__"), True)
        return p

    def run_checker(self, *pyflags, env_extra=None):
        """Run <root>/tools/ci/check_sha256sums.py as a script with cwd = repo root, as CI does."""
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON") and k != "GITHUB_ACTIONS"}
        env.update(env_extra or {})
        p = subprocess.run([sys.executable, *pyflags, os.path.join("tools", "ci", "check_sha256sums.py")],
                           cwd=self.root, env=env, capture_output=True, text=True, timeout=120)
        return p.returncode, p.stdout + p.stderr

    def assertTamperCaught(self, rc, out):
        lines = out.splitlines()
        self.assertEqual(rc, 1, out)
        self.assertIn(MISMATCH, lines, out)
        self.assertEqual(lines[-1], FAIL, out)
        self.assertNotIn(PASS, lines, out)

    def test_clean_tree_passes_both_modes(self):
        """Control: the untampered synthetic tree PASSes as a plain script (through the re-exec) and under -I -B."""
        for flags in ((), ("-I", "-B")):
            with self.subTest(flags=flags):
                rc, out = self.run_checker(*flags)
                self.assertEqual(rc, 0, out)
                self.assertEqual(out.splitlines()[-1], PASS, out)

    def test_clean_tree_with_harmless_sibling_still_passes(self):
        """Control: an unrelated sibling .py beside the checker does not break a clean run."""
        self.plant(self.ci, "unrelated_helper", "X = 1\n")
        rc, out = self.run_checker()
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines()[-1], PASS, out)

    def test_tampered_file_fails_both_modes(self):
        """Control: with no plant, the tampered listed file is a MISMATCH and the run FAILs."""
        self.write(TARGET, TAMPERED)
        for flags in ((), ("-I", "-B")):
            with self.subTest(flags=flags):
                self.assertTamperCaught(*self.run_checker(*flags))

    def test_digest_proxy_hashlib_beside_checker_cannot_hide_mismatch(self):
        """S-B1 witness: tools/ci/hashlib.py proxying the real module and substituting the listed digest for
        the tampered bytes. Before the fix this printed PASS (61 verified, exit 0) on the real tree."""
        self.write(TARGET, TAMPERED)
        self.plant(self.ci, "hashlib", DIGEST_PROXY)
        self.assertTamperCaught(*self.run_checker())

    def test_forging_shadow_modules_beside_checker_cannot_hijack_it(self):
        """S-B1: no stdlib-named module beside the checker (tools/ci/<mod>.py) runs inside it."""
        self.write(TARGET, TAMPERED)
        for mod in SHADOW_MODS:
            with self.subTest(module=mod):
                p = self.plant(self.ci, mod, FORGE)
                try:
                    self.assertTamperCaught(*self.run_checker())
                finally:
                    os.unlink(p)
                    shutil.rmtree(os.path.join(self.ci, "__pycache__"), ignore_errors=True)

    def test_shadow_hashlib_on_pythonpath_cannot_hijack_it(self):
        """S-B1 / N1: a hashlib.py on PYTHONPATH is ignored (the re-exec uses -I)."""
        self.write(TARGET, TAMPERED)
        shadow = os.path.realpath(tempfile.mkdtemp(prefix="cs_iso_shadow_"))
        self.addCleanup(shutil.rmtree, shadow, True)
        self.plant(shadow, "hashlib", DIGEST_PROXY)
        self.assertTamperCaught(*self.run_checker(env_extra={"PYTHONPATH": shadow}))

    def test_reexec_precedes_every_other_import(self):
        """Structure: the only statement before the isolated re-exec is `import sys as _sys` (built in)."""
        with open(CHECKER, encoding="utf-8") as f:
            body = ast.parse(f.read()).body
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
            body = body[1:]                                                 # module docstring
        self.assertIsInstance(body[0], ast.Import)
        self.assertEqual([(a.name, a.asname) for a in body[0].names], [("sys", "_sys")])
        self.assertIsInstance(body[1], ast.If)
        src = ast.unparse(body[1])
        for needle in ("__name__ == '__main__'", "_sys.flags.isolated", "execv", "'-I'", "'-B'"):
            self.assertIn(needle, src)


if __name__ == "__main__":
    unittest.main()
