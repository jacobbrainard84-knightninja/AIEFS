"""Entry-level self-tests for tools/ci/check_sha256sums.py (stdlib unittest; synthetic temp git repos).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v

H3 (2026-11-20) found that a deleted listed file (L178 MISSING), a missing entry turned into a notice (L175
`is not -> is`), an emptied list (L189) and a blank/comment line that truncates a list (L154 `continue -> break`)
were noticed only by tools/redteam, which CI does not run. These tests call check() on a synthetic repo with the
module's repo-specific tables (EXTRA_INCLUDE, EXCLUDED, ALLOWED_MISSING) patched to known values, and assert the
exact error/notice lists, so each of those mutants fails an assertion here.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_sha256sums  # noqa: E402

SUMS = "data/SHA256SUMS"


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Sha256sumsEntryTests(unittest.TestCase):
    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="cs_ent_"))
        self.addCleanup(shutil.rmtree, self.root, True)
        for name, attr in (("EXTRA_INCLUDE", {}), ("EXCLUDED", {}), ("ALLOWED_MISSING", {})):
            p = mock.patch.object(check_sha256sums, name, attr)
            p.start()
            self.addCleanup(p.stop)
        self.files = {"data/a.bin": b"alpha\n", "data/b.bin": b"beta\n"}
        for rel, data in self.files.items():
            self.write(rel, data)
        subprocess.run(["git", "init", "-q", self.root], check=True)

    def write(self, rel, data):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    def write_sums(self, lines):
        self.write(SUMS, ("\n".join(lines) + "\n").encode())
        subprocess.run(["git", "-C", self.root, "add", "-A"], check=True)

    def entry(self, name):
        return f"{sha(self.files['data/' + name])}  {name}"

    def check(self):
        sums, n_ok, errors, notices = check_sha256sums.check(self.root)
        return sums, n_ok, errors, notices

    def test_control_clean_list_verifies_every_entry(self):
        self.write_sums([self.entry("a.bin"), self.entry("b.bin")])
        self.assertEqual(self.check(), ([SUMS], 2, [], []))

    def test_deleted_listed_file_is_an_error(self):
        """Kills L178 (delete the MISSING error) and L175 (`is not -> is`: missing entry downgraded to a notice)."""
        self.write_sums([self.entry("a.bin"), self.entry("b.bin")])
        os.unlink(os.path.join(self.root, "data/b.bin"))
        sums, n_ok, errors, notices = self.check()
        self.assertEqual(errors, [f"{SUMS}:2: MISSING b.bin"])
        self.assertEqual(notices, [])
        self.assertEqual(n_ok, 1)

    def test_allow_listed_missing_file_is_a_notice_only(self):
        """Control for the allow-list branch (the other side of L175)."""
        self.write_sums([self.entry("a.bin"), self.entry("b.bin")])
        os.unlink(os.path.join(self.root, "data/b.bin"))
        with mock.patch.object(check_sha256sums, "ALLOWED_MISSING", {(SUMS, "b.bin"): "test reason"}):
            sums, n_ok, errors, notices = self.check()
        self.assertEqual(errors, [])
        self.assertEqual(notices, [f"{SUMS}:2: b.bin is missing (allow-listed: test reason)"])

    def test_emptied_list_fails(self):
        """Kills L189: a list with only comments/blank lines must be an error, not a vacuous PASS."""
        self.write_sums(["# all entries removed", ""])
        sums, n_ok, errors, notices = self.check()
        self.assertEqual((n_ok, errors), (0, [f"{SUMS}: contains no checksum entries"]))

    def test_blank_and_comment_lines_do_not_truncate_the_list(self):
        """Kills L154 (`continue -> break`): entries after a blank or comment line are still verified."""
        self.write_sums([self.entry("a.bin"), "", "# section", self.entry("b.bin")])
        self.assertEqual(self.check(), ([SUMS], 2, [], []))
        self.write("data/b.bin", b"tampered\n")
        sums, n_ok, errors, notices = self.check()
        self.assertEqual(len(errors), 1, errors)
        self.assertTrue(errors[0].startswith(f"{SUMS}:4: MISMATCH b.bin"), errors)


if __name__ == "__main__":
    unittest.main()
