"""PUSH_NOTES parsing tests for tools/ci/check_modes.py (stdlib unittest).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v

H3 (2026-11-20): every path in the existing NOTES fixture also appears on the `--chmod=+x` line, so the
backtick branch of parse_push_notes (L86 `"/" in tok`) and the end of the section (L78 `break` at the next
numbered item) were untested: a mutant could drop backtick-only scripts from the exec-bit check, or pull
paths from later items into it. These tests assert the exact parsed list, and the end-to-end KNOWN_NOT_EXEC
result for a backtick-only path in a synthetic git repo.
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_modes  # noqa: E402

NOTES = """# Push notes

1. **File modes.** See `tools/item_one.sh` (not part of the exec-bit item).
2. **Executable bits to restore.** These scripts need their bit restored:
   - `tools/sync/only_in_backticks.sh`
   - `audits/engineering/verify_x.py`
   - bare names such as `lint_claims.py` are prose, not paths
3. **Later item.** Paths below must NOT be picked up (the section ends at "3."):
   - `tools/later_item.sh`
"""


class PushNotesParseTests(unittest.TestCase):
    def test_backtick_paths_exact_and_section_ends_at_next_item(self):
        """Kills L86 (`"/" in tok -> not in`) and L78 (`break -> continue`) by exact equality."""
        self.assertEqual(check_modes.parse_push_notes(NOTES),
                         ["tools/sync/only_in_backticks.sh", "audits/engineering/verify_x.py"])

    def test_backtick_only_path_reaches_the_exec_bit_check(self):
        """End to end: a 100644 script listed only in backticks is reported as KNOWN_NOT_EXEC; --strict fails."""
        with tempfile.TemporaryDirectory() as root:
            files = {"PUSH_NOTES.md": NOTES, "tools/sync/only_in_backticks.sh": "#!/bin/sh\n",
                     "audits/engineering/verify_x.py": "#!/usr/bin/env python3\n",
                     "tools/later_item.sh": "#!/bin/sh\n", "tools/item_one.sh": "#!/bin/sh\n"}
            for rel, text in files.items():
                p = os.path.join(root, rel)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w") as f:
                    f.write(text)
            subprocess.run(["git", "-C", root, "init", "-q"], check=True)
            subprocess.run(["git", "-C", root, "add", "-A"], check=True)
            subprocess.run(["git", "-C", root, "update-index", "--chmod=+x", "audits/engineering/verify_x.py"],
                           check=True)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = check_modes.main(["--repo", root, "--strict"])
            out = buf.getvalue()
            self.assertEqual(rc, 1, out)
            # match the plain report line only: under GITHUB_ACTIONS=true the checker also prints a ::error annotation
            known = [ln for ln in out.splitlines() if ln.startswith("ERROR KNOWN_NOT_EXEC ")]
            self.assertEqual(len(known), 1, out)
            self.assertIn("tools/sync/only_in_backticks.sh", known[0])


if __name__ == "__main__":
    unittest.main()
