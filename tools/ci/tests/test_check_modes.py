#!/usr/bin/env python3
"""Self-tests for tools/ci/check_modes.py (stdlib unittest, synthetic temp git repos).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_modes  # noqa: E402

NOTES = """# Push notes

1. **File modes.** Something.
2. **Executable bits to restore.** These scripts:
   - `tools/a.sh`
   - `tools/b.py`

   ```
   git update-index --chmod=+x tools/a.sh tools/b.py tools/c.sh
   ```
3. **Other item.** `tools/not_listed.sh`
"""


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check_modes.main(argv)
    return rc, buf.getvalue()


class CheckModesTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.root = self.d.name
        self.g = ["git", "-C", self.root]
        subprocess.run(self.g + ["init", "-q"], check=True)
        files = {
            "PUSH_NOTES.md": NOTES,
            "tools/a.sh": "#!/bin/sh\necho a\n",
            "tools/b.py": "#!/usr/bin/env python3\n",
            "tools/c.sh": "#!/bin/sh\n",
            "tools/not_listed.sh": "#!/bin/sh\n",
            "lib/module.py": "#!/usr/bin/env python3\nX = 1\n",
            "lib/plain.py": "X = 1\n",
            "dir with space/s.sh": "#!/bin/sh\n",
        }
        for rel, text in files.items():
            p = os.path.join(self.root, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(text)
        subprocess.run(self.g + ["add", "-A"], check=True)
        subprocess.run(self.g + ["update-index", "--chmod=-x"] + list(files), check=True)

    def tearDown(self):
        self.d.cleanup()

    def chmod_x(self, *paths):
        subprocess.run(self.g + ["update-index", "--chmod=+x"] + list(paths), check=True)

    def test_parse_push_notes(self):
        self.assertEqual(check_modes.parse_push_notes(NOTES), ["tools/a.sh", "tools/b.py", "tools/c.sh"])

    def test_warns_but_exits_zero(self):
        rc, out = run(["--repo", self.root])
        self.assertEqual(rc, 0, out)
        for p in ("tools/a.sh", "tools/b.py", "tools/c.sh"):
            self.assertIn(f"KNOWN_NOT_EXEC {p}", out)
        self.assertIn("SHEBANG_NOT_EXEC lib/module.py", out)
        self.assertIn("SHEBANG_NOT_EXEC tools/not_listed.sh", out)
        self.assertIn("SHEBANG_NOT_EXEC dir with space/s.sh", out)
        self.assertNotIn("lib/plain.py", out)
        self.assertIn("NOTICE known script not tracked: lean/AIEFProofs/check_lean.sh", out)

    def test_strict_fails_until_fixed(self):
        rc, out = run(["--repo", self.root, "--strict"])
        self.assertEqual(rc, 1)
        # The summary must be consistent with the exit status (audit N2).
        self.assertIn("ERROR KNOWN_NOT_EXEC tools/a.sh", out)
        self.assertRegex(out, r"== result: 3 error\(s\), \d+ warning\(s\) \(--strict: known-list scripts not 100755 count as errors\) -> FAIL")
        self.assertNotIn("== result: 0 error(s)", out)
        self.chmod_x("tools/a.sh", "tools/b.py", "tools/c.sh")
        rc, out = run(["--repo", self.root, "--strict"])
        self.assertEqual(rc, 0, out)
        self.assertNotIn("KNOWN_NOT_EXEC", out)
        self.assertIn("== result: 0 error(s)", out)
        self.assertIn("-> PASS", out)

    def test_default_summary_counts_known_as_warnings(self):
        rc, out = run(["--repo", self.root])
        self.assertEqual(rc, 0)
        self.assertRegex(out, r"== result: 0 error\(s\), \d+ warning\(s\) -> PASS")

    def test_strict_github_annotation_is_error(self):
        with mock.patch.object(check_modes, "IN_GHA", True):
            rc, out = run(["--repo", self.root, "--strict"])
        self.assertEqual(rc, 1)
        self.assertIn("::error file=tools/a.sh,title=KNOWN_NOT_EXEC::", out)

    def test_cat_file_failure_exits_2(self):
        err = subprocess.CalledProcessError(128, ["git", "cat-file"])
        with mock.patch.object(check_modes, "shebang_objects", side_effect=err):
            rc, out = run(["--repo", self.root])
        self.assertEqual(rc, 2)
        self.assertIn("ERROR: cannot read blobs", out)

    def test_github_annotations(self):
        with mock.patch.object(check_modes, "IN_GHA", True):
            rc, out = run(["--repo", self.root])
        self.assertEqual(rc, 0)
        self.assertIn("::warning file=tools/a.sh,title=KNOWN_NOT_EXEC::", out)
        self.assertEqual(out.count("title=SHEBANG_NOT_EXEC"), 1)

    def test_no_annotations_outside_actions(self):
        with mock.patch.object(check_modes, "IN_GHA", False):
            _, out = run(["--repo", self.root])
        self.assertNotIn("::warning", out)

    def test_not_a_repo(self):
        with tempfile.TemporaryDirectory() as empty:
            rc, out = run(["--repo", empty])
        self.assertEqual(rc, 2, out)


if __name__ == "__main__":
    unittest.main()
