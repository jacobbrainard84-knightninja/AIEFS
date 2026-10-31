"""Self-tests for tools/ci/check_manifest.py (stdlib unittest; synthetic fixtures in temp folders).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v
"""
import contextlib
import io
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_manifest  # noqa: E402

VERIFIER = "AI Agent Audits/evidence/verify_manifest.py"


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check_manifest.main(argv)
    return rc, buf.getvalue()


class CheckManifestTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.root = self.d.name

    def tearDown(self):
        self.d.cleanup()

    def verifier(self, body):
        p = os.path.join(self.root, VERIFIER)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(body)
        # Minimal non-empty manifest so the G1 coverage rule (fix/manifest-nonempty) is satisfied.
        rep = os.path.join(self.root, "AI Agent Audits", "REPORT.md")
        with open(rep, "w") as f:
            f.write("report\n")
        with open(os.path.join(os.path.dirname(p), "audit_manifest.json"), "w") as f:
            f.write('{"files_sha256": {"REPORT.md": {}}, "inputs_sha256": {"x.py": "0"}}')

    def test_missing_verifier_fails_closed(self):
        rc, out = run(["--repo", self.root])
        self.assertEqual(rc, 1, out)
        self.assertIn("manifest verifier missing", out)
        self.assertIn("-> FAIL", out)

    def test_passing_verifier_passes(self):
        self.verifier("import sys\nsys.exit(0)\n")
        rc, out = run(["--repo", self.root])
        self.assertEqual(rc, 0, out); self.assertIn("1 verifier(s) run, 0 failed -> PASS", out)

    def test_failing_verifier_fails(self):
        self.verifier("import sys\nsys.exit(3)\n")
        rc, out = run(["--repo", self.root])
        self.assertEqual(rc, 1, out); self.assertIn("exited 3", out)

    def test_no_inputs_flag_drops_inputs_arg(self):
        self.verifier("import sys\nsys.exit(0 if '--inputs' not in sys.argv else 4)\n")
        self.assertEqual(run(["--repo", self.root, "--no-inputs"])[0], 0)
        self.assertEqual(run(["--repo", self.root])[0], 1)

    def test_bad_repo_is_usage_error(self):
        self.assertEqual(run(["--repo", os.path.join(self.root, "nope")])[0], 2)


if __name__ == "__main__":
    unittest.main()
