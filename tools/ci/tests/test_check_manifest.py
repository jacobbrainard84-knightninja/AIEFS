"""Self-tests for tools/ci/check_manifest.py (stdlib unittest; synthetic fixtures in temp folders).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v

Assertions are on exact output lines (each expected line must be a whole line of the output) and on the
exact final '== result: ...' line, not on substrings.
"""
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_manifest  # noqa: E402

VERIFIER = "AI Agent Audits/evidence/verify_manifest.py"
MANIFEST = "AI Agent Audits/evidence/audit_manifest.json"
KEY = "evidence/verify_manifest.py"
# A stand-in verifier that prints the same summary the real one prints for the fixture manifest
# (2 published files: REPORT.md + itself; 1 input) and a final OK.
GOOD = ('import sys\n'
        'print("checked 2 published files" + (" and 1 inputs" if "--inputs" in sys.argv else ""))\n'
        'print("OK")\n')
PASS = "== result: 1 verifier(s) run, 0 failed -> PASS"
FAIL_RUN = "== result: 1 verifier(s) run, 1 failed -> FAIL"
FAIL_NOT_RUN = "== result: 0 verifier(s) run, 1 failed -> FAIL"
NOT_RUN = f"ERROR   {VERIFIER} was NOT run, so the manifest hashes were NOT checked"


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check_manifest.main(argv)
    return rc, buf.getvalue()


def sha(b):
    return hashlib.sha256(b).hexdigest()


class CheckManifestTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.root = self.d.name
        self.old_gha = os.environ.pop("GITHUB_ACTIONS", None)

    def tearDown(self):
        if self.old_gha is not None:
            os.environ["GITHUB_ACTIONS"] = self.old_gha
        self.d.cleanup()

    def assertLines(self, out, *lines):
        got = out.splitlines()
        for ln in lines:
            self.assertIn(ln, got, out)

    def verifier(self, body, pinned=None):
        """Write the verifier `body` and a minimal non-empty manifest (G1) that pins `pinned` (default: body)."""
        p = os.path.join(self.root, VERIFIER)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(body)
        with open(os.path.join(self.root, "AI Agent Audits", "REPORT.md"), "w") as f:
            f.write("report\n")
        pin = (body if pinned is None else pinned).encode()
        m = {"files_sha256": {"REPORT.md": {"bytes": 7, "sha256": sha(b"report\n")},
                              KEY: {"bytes": len(pin), "sha256": sha(pin)}},
             "inputs_sha256": {"x.py": "0"}}
        with open(os.path.join(self.root, MANIFEST), "w") as f:
            json.dump(m, f)
        return p

    def check(self, *extra):
        return run(["--repo", self.root, *extra])

    def test_missing_verifier_fails_closed(self):
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} not found; manifest verifier missing (deleted or moved?), "
                              "so the manifest hashes were NOT checked", FAIL_NOT_RUN)

    def test_passing_verifier_passes(self):
        self.verifier(GOOD)
        rc, out = self.check()
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines()[-3:], ["checked 2 published files and 1 inputs", "OK", PASS])

    def test_failing_verifier_fails(self):
        self.verifier("import sys\nprint('checked 2 published files and 1 inputs')\nprint('OK')\nsys.exit(3)\n")
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} exited 3", FAIL_RUN)

    def test_no_inputs_flag_drops_inputs_arg(self):
        self.verifier(GOOD.replace('import sys\n', 'import sys\nif "--inputs" in sys.argv: sys.exit(4)\n'))
        rc, out = self.check("--no-inputs")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines()[-3:], ["checked 2 published files", "OK", PASS])
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} exited 4", FAIL_RUN)

    def test_bad_repo_is_usage_error(self):
        rc, out = run(["--repo", os.path.join(self.root, "nope")])
        self.assertEqual(rc, 2)
        self.assertEqual(out.splitlines(), [f"ERROR   --repo {os.path.join(self.root, 'nope')} is not a directory"])

    # --- G2b: the verifier itself is authenticated before it is run, and its success line is required ----------
    def _hash_mismatch(self, body):
        self.verifier(body, pinned=GOOD)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER}: sha256 {sha(body.encode())} does not match "
                              f"{MANIFEST} files_sha256['{KEY}'] {sha(GOOD.encode())}; refusing to run an unverified verifier",
                         NOT_RUN, FAIL_NOT_RUN)
        self.assertNotIn("$ ", out)                       # the stub was never executed

    def test_zero_byte_verifier_fails(self):
        self._hash_mismatch("")

    def test_comment_only_verifier_fails(self):
        self._hash_mismatch("# verify_manifest.py\n")

    def test_exit0_stub_verifier_fails(self):
        self._hash_mismatch("import sys\nsys.exit(0)\n")

    def test_verifier_without_manifest_entry_fails(self):
        self.verifier(GOOD)
        mp = os.path.join(self.root, MANIFEST)
        with open(mp) as f:
            m = json.load(f)
        del m["files_sha256"][KEY]
        with open(mp, "w") as f:
            json.dump(m, f)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER}: {MANIFEST} has no files_sha256 entry '{KEY}' with a sha256, "
                              "so the verifier cannot be authenticated", NOT_RUN, FAIL_NOT_RUN)

    def test_unreadable_manifest_fails_before_running(self):
        self.verifier(GOOD)
        with open(os.path.join(self.root, MANIFEST), "w") as f:
            f.write("[]")
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {MANIFEST}: files_sha256 is missing or not an object", NOT_RUN, FAIL_NOT_RUN)

    def test_symlink_outside_repo_fails(self):
        p = self.verifier(GOOD)
        outside = tempfile.TemporaryDirectory(); self.addCleanup(outside.cleanup)
        stub = os.path.join(outside.name, "stub.py")
        with open(stub, "w") as f:
            f.write(GOOD)                               # same bytes, so only the location is wrong
        os.unlink(p); os.symlink(stub, p)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} resolves outside the repository (to {os.path.realpath(stub)}); "
                              "refusing to run it", NOT_RUN, FAIL_NOT_RUN)

    def test_symlink_inside_repo_fails(self):
        p = self.verifier(GOOD)
        real = os.path.join(self.root, "tools", "verify_copy.py")
        os.makedirs(os.path.dirname(real))
        os.replace(p, real); os.symlink(real, p)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} is a symlink (to tools/verify_copy.py); "
                              "the verifier must be a regular file at its listed path", NOT_RUN, FAIL_NOT_RUN)

    def test_dangling_symlink_fails(self):
        p = self.verifier(GOOD)
        os.unlink(p); os.symlink(os.path.join(self.root, "gone.py"), p)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} is a symlink (to gone.py); "
                              "the verifier must be a regular file at its listed path", NOT_RUN, FAIL_NOT_RUN)

    def test_directory_in_place_of_verifier_fails(self):
        p = self.verifier(GOOD)
        os.unlink(p); os.mkdir(p)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} is not a regular file; refusing to run it", NOT_RUN, FAIL_NOT_RUN)

    def _no_success_line(self, body, mode=()):
        self.verifier(body)                                # correctly pinned, so it IS run
        rc, out = self.check(*mode)
        self.assertEqual(rc, 1, out)
        want = "checked 2 published files" + ("" if mode else " and 1 inputs")
        self.assertLines(out, f"ERROR   {VERIFIER} exited 0 but did not print its success line '{want}' followed by 'OK'; "
                              "the manifest hashes are NOT confirmed", FAIL_RUN)

    def test_pinned_verifier_silent_exit0_fails(self):
        self._no_success_line("import sys\nsys.exit(0)\n")

    def test_pinned_verifier_printing_failed_exit0_fails(self):
        self._no_success_line("print('checked 2 published files and 1 inputs')\nprint('FAILED: 1 problem(s)')\n")

    def test_pinned_verifier_wrong_count_fails(self):
        self._no_success_line("print('checked 1 published files and 1 inputs')\nprint('OK')\n")

    def test_pinned_verifier_inputs_line_in_no_inputs_mode_fails(self):
        self._no_success_line("print('checked 2 published files and 1 inputs')\nprint('OK')\n", ("--no-inputs",))

    def test_github_annotation(self):
        self.verifier("", pinned=GOOD)
        os.environ["GITHUB_ACTIONS"] = "true"
        try:
            rc, out = self.check()
        finally:
            del os.environ["GITHUB_ACTIONS"]
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"::error file={VERIFIER}::{VERIFIER}: sha256 {sha(b'')} does not match "
                              f"{MANIFEST} files_sha256['{KEY}'] {sha(GOOD.encode())}; refusing to run an unverified verifier")


if __name__ == "__main__":
    unittest.main()
