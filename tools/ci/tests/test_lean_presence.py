#!/usr/bin/env python3
"""Tests for tools/ci/lean_presence.sh, the presence gate used by .github/workflows/lean.yml.

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v
Runs the real script (the workflow step only calls it) with bash in a temporary directory.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SCRIPT = os.path.join(REPO, "tools", "ci", "lean_presence.sh")
WORKFLOW = os.path.join(REPO, ".github", "workflows", "lean.yml")
PROJ, CHECK = "lean/AIEFProofsKn", "check_lean_kn.sh"


@unittest.skipUnless(shutil.which("bash"), "bash missing")
class LeanPresenceTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = self.d.name
        self.out = os.path.join(self.root, "gh_output")
        self.summary = os.path.join(self.root, "gh_summary")

    def tearDown(self):
        self.d.cleanup()

    def make(self, *files):
        os.makedirs(os.path.join(self.root, PROJ), exist_ok=True)
        for f in files:
            open(os.path.join(self.root, PROJ, f), "w").close()

    def run_gate(self, required, project=PROJ, check=CHECK):
        env = dict(os.environ, GITHUB_OUTPUT=self.out, GITHUB_STEP_SUMMARY=self.summary)
        r = subprocess.run(["bash", SCRIPT, project, check, required], cwd=self.root, env=env,
                           capture_output=True, text=True)
        output = open(self.out).read() if os.path.exists(self.out) else ""
        return r.returncode, output, r.stdout + r.stderr

    def test_dir_missing_optional_skips(self):
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (0, "present=false\n"))
        self.assertIn("::warning::", msg)
        self.assertIn("SKIPPED", open(self.summary).read())

    def test_dir_with_lakefile_toml_and_script_present(self):
        self.make("lakefile.toml", CHECK)
        for req in ("false", "true"):
            os.path.exists(self.out) and os.remove(self.out)
            rc, output, msg = self.run_gate(req)
            self.assertEqual((rc, output), (0, "present=true\n"), req)
            self.assertNotIn("::", msg)

    def test_lakefile_lean_accepted(self):
        self.make("lakefile.lean", CHECK)
        self.assertEqual(self.run_gate("false")[:2], (0, "present=true\n"))

    def test_dir_with_missing_script_errors(self):
        self.make("lakefile.toml", "check_lean_kn_renamed.sh")
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("::error::", msg); self.assertIn(CHECK, msg)

    def test_dir_with_missing_lakefile_errors(self):
        self.make(CHECK, "lakefile.toml.bak")
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("::error::", msg); self.assertIn("lakefile", msg)

    def test_empty_dir_errors(self):
        self.make()
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("::error::", msg)

    def test_required_dir_missing_errors(self):
        rc, output, msg = self.run_gate("true", project="lean/AIEFProofs", check="check_lean.sh")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("::error::", msg); self.assertNotIn("::warning::", msg)

    def test_without_github_env_prints_to_stdout(self):
        self.make("lakefile.toml", CHECK)
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_OUTPUT", "GITHUB_STEP_SUMMARY")}
        r = subprocess.run(["bash", SCRIPT, PROJ, CHECK, "false"], cwd=self.root, env=env,
                           capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "present=true\n", ""))

    def test_bad_arguments(self):
        self.assertEqual(self.run_gate("maybe")[0], 2)

    def test_workflow_calls_this_script(self):
        wf = open(WORKFLOW, encoding="utf-8").read()
        self.assertEqual(len(re.findall(r"bash tools/ci/lean_presence\.sh ", wf)), 1)
        self.assertNotIn("lakefile.toml\" ] &&", wf)   # no inline copy of the old gate


if __name__ == "__main__":
    unittest.main()
