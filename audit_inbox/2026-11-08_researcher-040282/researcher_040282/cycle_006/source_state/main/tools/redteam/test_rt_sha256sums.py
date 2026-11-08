"""Red-team negative controls: tools/ci/check_sha256sums.py (every tracked checksum list).

Each test breaks a pinned file (or a checksum list itself) in a symlink mirror of the repo and
asserts the checker REJECTS it with a specific message.
Run:  python3 -m unittest discover -s tools/redteam -v   (from the repository root)

Safety: the mirror's directories are symlinks into the real checkout, so a test must never
open() a mirror path for writing directly. Every write goes through tamper() or put() below,
which first materialize the directory and unlink the symlink. setUpClass/tearDownClass compare
`git status --porcelain --ignored` of the real checkout and fail if any test changed it.

The checker is run through a small driver that sets module globals instead of using CLI flags:
GIT_ROOT (take the tracked-file list from the real checkout, since the mirror is not a git
repo) and, for the allow-list tests, a synthetic ALLOWED_MISSING entry (added to the live ones)
or a replacement EXCLUDED, so no test depends on the live allow-list entries.
"""
import json
import os
import subprocess
import unittest

from rtcommon import PY, REPO, TempDirMixin, farm, materialize, remove, run, sha256, tamper

CHK_DIR = os.path.join(REPO, "tools", "ci")
SYNC = "tools/sync"                                     # tools/sync/SHA256SUMS
SYNC_SUMS = f"{SYNC}/SHA256SUMS"
LEAN_SUMS = "lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt"
LOCK_HASHES = "lean/AIEFProofs/AIEF_LEAN_PROJECT_LOCK_HASHES.txt"
GHOST = "ghost_artifact.log"                            # synthetic allow-listed entry

DRIVER = r"""
import json, sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import check_sha256sums as c
o = json.loads(sys.argv[2])
c.GIT_ROOT = o["git_root"]
if "allowed" in o:
    c.ALLOWED_MISSING = {**c.ALLOWED_MISSING, **{(s, e): r for s, e, r in o["allowed"]}}
if "excluded" in o:
    c.EXCLUDED = o["excluded"]
sys.exit(c.main(sys.argv[3:]))
"""


def put(root, rel, data):
    """Create or replace root/rel with `data` without ever writing through a symlink."""
    p = materialize(root, rel)
    if os.path.lexists(p):
        os.unlink(p)
    with open(p, "wb") as f:
        f.write(data)
    return p


def tree_state():
    out = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--ignored", "-z"],
                         capture_output=True, check=True).stdout.decode("utf-8", "replace")
    return sorted(x for x in out.split("\0") if x and "__pycache__" not in x)


class Sha256Sums(TempDirMixin, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._tree_before = tree_state()

    @classmethod
    def tearDownClass(cls):
        after = tree_state()
        if after != cls._tree_before:
            raise AssertionError(f"red-team tests changed the real checkout: before={cls._tree_before} after={after}")

    def setUp(self):
        super().setUp()
        self.root = farm(os.path.join(self.tmp, "repo"))

    def chk(self, root=None, **over):
        over["git_root"] = REPO
        return run([PY, "-c", DRIVER, CHK_DIR, json.dumps(over), "--repo", root or self.root])

    def add_sync_entry(self, name, digest):
        tamper(self.root, SYNC_SUMS, lambda d: d + f"{digest}  {name}\n".encode())

    # --- controls -------------------------------------------------------------------------
    def test_00_control_untampered_mirror_passes(self):
        rc, out = self.chk()
        self.assertEqual(rc, 0, out[-2000:])
        self.assertIn(LOCK_HASHES, out)                         # included explicitly

    def test_01_control_synthetic_allow_listed_missing_entry_passes(self):
        self.add_sync_entry(GHOST, "0" * 64)
        rc, out = self.chk(allowed=[[SYNC_SUMS, GHOST, "synthetic test entry"]])
        self.assertEqual(rc, 0, out[-2000:])
        self.assertIn(f"{GHOST} is missing (allow-listed: synthetic test entry)", out)

    # --- tampering ------------------------------------------------------------------------
    def test_listed_file_one_byte_changed(self):
        tamper(self.root, f"{SYNC}/download_new.sh", lambda d: d + b"\n# injected\n")
        self.assertRejected(*self.chk(), "tools/sync/SHA256SUMS:", "MISMATCH download_new.sh")

    def test_lean_source_edited(self):
        tamper(self.root, "lean/AIEFProofs/AIEFProofs.lean", lambda d: d + b"\n-- injected\n")
        self.assertRejected(*self.chk(), LEAN_SUMS, "MISMATCH AIEFProofs.lean")

    def test_lean_lock_file_edited(self):
        tamper(self.root, "lean/AIEFProofs/lake-manifest.json", lambda d: d + b"\n")
        self.assertRejected(*self.chk(), LOCK_HASHES, "MISMATCH lake-manifest.json")

    def test_listed_file_deleted(self):
        remove(self.root, f"{SYNC}/upload_new.sh")
        self.assertRejected(*self.chk(), "MISSING upload_new.sh")

    def test_tracked_sums_file_deleted(self):
        remove(self.root, SYNC_SUMS)
        self.assertRejected(*self.chk(), f"{SYNC_SUMS}: cannot read")

    def test_malformed_line(self):
        tamper(self.root, SYNC_SUMS, lambda d: d + b"not-a-hash  evil.sh\n")
        self.assertRejected(*self.chk(), "malformed line")

    def test_path_escaping_repo(self):
        self.add_sync_entry("../../../../etc/passwd", "0" * 64)
        self.assertRejected(*self.chk(), "path escapes the repository: ../../../../etc/passwd")

    def test_in_repo_symlink_pointing_outside(self):
        outside = os.path.join(self.tmp, "outside.txt")
        with open(outside, "wb") as f:
            f.write(b"not part of the repo\n")
        link = materialize(self.root, f"{SYNC}/evil_link.txt")
        os.symlink(outside, link)
        self.add_sync_entry("evil_link.txt", sha256(outside))   # hash matches, so only the escape check can catch it
        self.assertRejected(*self.chk(), "path escapes the repository via a symlink: evil_link.txt")

    # --- allow-list (synthetic entry, independent of the live ALLOWED_MISSING) ---------------
    def test_allow_listed_file_reappears_with_wrong_content(self):
        self.add_sync_entry(GHOST, "0" * 64)
        put(self.root, f"{SYNC}/{GHOST}", b"forged log\n")
        self.assertRejected(*self.chk(allowed=[[SYNC_SUMS, GHOST, "synthetic"]]), f"MISMATCH {GHOST}")

    def test_allow_listed_file_reappears_matching(self):
        p = put(self.root, f"{SYNC}/{GHOST}", b"restored log\n")
        self.add_sync_entry(GHOST, sha256(p))
        self.assertRejected(*self.chk(allowed=[[SYNC_SUMS, GHOST, "synthetic"]]),
                            f"{GHOST} is allow-listed as missing but now exists and matches")

    def test_allow_listed_entry_not_in_sums_is_stale(self):
        self.assertRejected(*self.chk(allowed=[[SYNC_SUMS, GHOST, "synthetic"]]),
                            f"stale allow-list entry: {SYNC_SUMS} no longer lists {GHOST}")

    # --- discovery ------------------------------------------------------------------------
    def test_unclassified_hash_list_is_an_error(self):
        # With an empty EXCLUDED list, the tracked historical hash lists must be reported.
        self.assertRejected(*self.chk(excluded={}), "twindow_source_hashes_before.txt: looks like a hash list but is not classified")

    def test_stale_exclusion_is_an_error(self):
        self.assertRejected(*self.chk(excluded={"no/such_hashes.txt": "synthetic"}),
                            "stale EXCLUDED entry: no/such_hashes.txt")

    def test_no_sums_files_at_all(self):
        empty = os.path.join(self.tmp, "empty")
        os.makedirs(empty)
        with open(os.path.join(empty, "README.md"), "w") as f:
            f.write("x\n")
        subprocess.run(["git", "init", "-q", empty], check=True)
        subprocess.run(["git", "-C", empty, "add", "README.md"], check=True)
        rc, out = run([PY, "-c", DRIVER, CHK_DIR, json.dumps({"git_root": None, "excluded": {}}), "--repo", empty])
        self.assertRejected(rc, out, "no SHA256SUMS file found")

    def test_not_a_git_checkout(self):
        rc, out = run([PY, os.path.join(CHK_DIR, "check_sha256sums.py"), "--repo", self.root])
        self.assertRejected(rc, out, "is not a git work tree")


if __name__ == "__main__":
    unittest.main()
