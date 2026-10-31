"""Red-team negative controls: tools/ci/check_sha256sums.py (every SHA256SUMS file in the tree).

Each test breaks a SHA256SUMS-pinned file (or the SUMS file itself) in a symlink mirror of the
repo and asserts the checker REJECTS it with a specific message.
Run:  python3 -m unittest discover -s tools/redteam -v   (from the repository root)
"""
import os
import unittest

from rtcommon import PY, REPO, TempDirMixin, farm, remove, run, tamper

CHK = os.path.join(REPO, "tools/ci/check_sha256sums.py")
SYNC = "tools/sync"                                     # tools/sync/SHA256SUMS
LEAN_SUMS = "lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt"
B2A = "audits/reproductions/b2a95dfbfbe3"
V3 = "compare_b2a95dfbfbe3_v3.log"                      # allow-listed missing entry (finding M1)


class Sha256Sums(TempDirMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.root = farm(os.path.join(self.tmp, "repo"))

    def chk(self, root=None):
        return run([PY, CHK, "--repo", root or self.root])

    def test_00_control_untampered_mirror_passes(self):
        rc, out = self.chk()
        self.assertEqual(rc, 0, out[-2000:])
        self.assertIn("allow-listed", out)

    def test_listed_file_one_byte_changed(self):
        tamper(self.root, f"{SYNC}/download_new.sh", lambda d: d + b"\n# injected\n")
        self.assertRejected(*self.chk(), "tools/sync/SHA256SUMS:", "MISMATCH download_new.sh")

    def test_lean_source_edited(self):
        tamper(self.root, "lean/AIEFProofs/AIEFProofs.lean", lambda d: d + b"\n-- injected\n")
        self.assertRejected(*self.chk(), LEAN_SUMS, "MISMATCH AIEFProofs.lean")

    def test_listed_file_deleted(self):
        remove(self.root, f"{SYNC}/upload_new.sh")
        self.assertRejected(*self.chk(), "MISSING upload_new.sh")

    def test_malformed_line(self):
        tamper(self.root, f"{SYNC}/SHA256SUMS", lambda d: d + b"not-a-hash  evil.sh\n")
        self.assertRejected(*self.chk(), "malformed line")

    def test_path_escaping_repo(self):
        tamper(self.root, f"{SYNC}/SHA256SUMS", lambda d: d + ("0" * 64 + "  ../../../../etc/passwd\n").encode())
        self.assertRejected(*self.chk(), "path escapes the repository")

    def test_allow_listed_file_reappears_with_wrong_content(self):
        tamper(self.root, f"{B2A}/compare_b2a95dfbfbe3_v2.log", lambda d: d)   # materialize the folder
        with open(os.path.join(self.root, B2A, V3), "w") as f:
            f.write("forged v3 log\n")
        self.assertRejected(*self.chk(), f"MISMATCH {V3}")

    def test_allow_listed_entry_removed_from_sums_is_stale(self):
        tamper(self.root, f"{B2A}/SHA256SUMS",
               lambda d: b"".join(l for l in d.splitlines(True) if V3.encode() not in l))
        self.assertRejected(*self.chk(), "stale allow-list entry")

    def test_no_sums_files_at_all(self):
        empty = os.path.join(self.tmp, "empty")
        os.makedirs(empty)
        self.assertRejected(*self.chk(empty), "no SHA256SUMS file found")


if __name__ == "__main__":
    unittest.main()
