#!/usr/bin/env python3
"""Self-tests for tools/ci/check_artifact_pins.py (stdlib unittest).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v
All fixtures are synthetic and built in temporary folders, with small test allowlists passed to
main(); one test also checks the real allowlist is consistent with itself.
"""
import contextlib
import csv
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_artifact_pins as cap  # noqa: E402

COLS = ["artifact_id", "container", "path", "sha256", "size_bytes", "tree_check_2026_10_28"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ArtifactPinTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.root = self.d.name
        self.rows = []

    def tearDown(self):
        self.d.cleanup()

    def put(self, rel, data):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    def row(self, aid, path, pinned, container="worktree", flag="PRESENT_SAME_SHA"):
        self.rows.append({"artifact_id": aid, "container": container, "path": path,
                          "sha256": pinned, "size_bytes": "0", "tree_check_2026_10_28": flag})

    def write_csv(self, cols=COLS):
        p = os.path.join(self.root, cap.ARTIFACTS)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
            w.writeheader(); w.writerows(self.rows)

    def run_check(self, changed=None, missing=None, argv=None, gha=False,
                  expected_sha=None, expected_rows=None, write=True):
        if write:
            self.write_csv()
        buf = io.StringIO()
        env = {"GITHUB_ACTIONS": "true"} if gha else {}
        with mock.patch.dict(os.environ, env), mock.patch.object(cap, "IN_GHA", gha), \
                contextlib.redirect_stdout(buf):
            extra = ["--no-git"] if argv is None else argv
            rc = cap.main(["--repo", self.root] + extra,
                          known_changed=changed or {}, known_missing=missing or {},
                          expected_sha=expected_sha, expected_rows=expected_rows)
        return rc, buf.getvalue()

    def test_all_match_passes(self):
        self.put("a.txt", b"a\n"); self.row("ART-1", "a.txt", sha(b"a\n"))
        rc, out = self.run_check()
        self.assertEqual(rc, 0, out); self.assertIn("1 match", out); self.assertIn("PASS", out)

    def test_new_mismatch_fails(self):
        self.put("a.txt", b"edited\n"); self.row("ART-1", "a.txt", sha(b"a\n"))
        rc, out = self.run_check()
        self.assertEqual(rc, 1); self.assertIn("PIN_MISMATCH ART-1", out)

    def test_new_missing_fails(self):
        self.row("ART-1", "gone.txt", sha(b"a\n"))
        rc, out = self.run_check()
        self.assertEqual(rc, 1); self.assertIn("PIN_MISSING ART-1", out)

    def test_flag_alone_does_not_allow(self):
        # Flagging a row in the CSV is not enough; only the hard-coded allowlist counts.
        self.put("a.txt", b"edited\n")
        self.row("ART-1", "a.txt", sha(b"a\n"), flag="PRESENT_CHANGED_SHA")
        self.row("ART-2", "gone.txt", sha(b"b\n"), flag="MISSING_DELETED_ON_MAIN")
        rc, out = self.run_check()
        self.assertEqual(rc, 1)
        self.assertIn("PIN_MISMATCH ART-1", out); self.assertIn("PIN_MISSING ART-2", out)

    def test_known_changed_exact_sha_passes(self):
        self.put("a.txt", b"edited\n")
        self.row("ART-1", "a.txt", sha(b"a\n"), flag="PRESENT_CHANGED_SHA")
        rc, out = self.run_check(changed={"ART-1": ("a.txt", sha(b"edited\n"))})
        self.assertEqual(rc, 0, out); self.assertIn("1 known-changed", out)

    def test_known_changed_edited_again_fails(self):
        self.put("a.txt", b"edited twice\n")
        self.row("ART-1", "a.txt", sha(b"a\n"), flag="PRESENT_CHANGED_SHA")
        rc, out = self.run_check(changed={"ART-1": ("a.txt", sha(b"edited\n"))})
        self.assertEqual(rc, 1); self.assertIn("KNOWN_CHANGED allows only", out)

    def test_known_changed_restored_is_stale_notice(self):
        self.put("a.txt", b"a\n")
        self.row("ART-1", "a.txt", sha(b"a\n"), flag="PRESENT_CHANGED_SHA")
        rc, out = self.run_check(changed={"ART-1": ("a.txt", sha(b"edited\n"))})
        self.assertEqual(rc, 0, out); self.assertIn("STALE_ALLOWLIST ART-1", out)

    def test_known_changed_missing_fails(self):
        self.row("ART-1", "a.txt", sha(b"a\n"), flag="PRESENT_CHANGED_SHA")
        rc, out = self.run_check(changed={"ART-1": ("a.txt", sha(b"edited\n"))})
        self.assertEqual(rc, 1); self.assertIn("PIN_MISSING ART-1", out)

    def test_known_missing_passes(self):
        self.row("ART-2", "gone.txt", sha(b"b\n"), flag="MISSING_DELETED_ON_MAIN")
        rc, out = self.run_check(missing={"ART-2": "gone.txt"})
        self.assertEqual(rc, 0, out); self.assertIn("1 known-missing", out)

    def test_known_missing_back_with_wrong_bytes_fails(self):
        self.put("gone.txt", b"other\n")
        self.row("ART-2", "gone.txt", sha(b"b\n"), flag="MISSING_DELETED_ON_MAIN")
        rc, out = self.run_check(missing={"ART-2": "gone.txt"})
        self.assertEqual(rc, 1); self.assertIn("PIN_MISMATCH ART-2", out)

    def test_allowlist_path_drift_fails(self):
        self.put("b.txt", b"edited\n")
        self.row("ART-1", "b.txt", sha(b"a\n"))
        rc, out = self.run_check(changed={"ART-1": ("a.txt", sha(b"edited\n"))})
        self.assertEqual(rc, 1); self.assertIn("ALLOWLIST_DRIFT ART-1", out)
        self.assertIn("PIN_MISMATCH ART-1", out)

    def test_allowlisted_id_removed_from_csv_fails(self):
        self.put("a.txt", b"a\n"); self.row("ART-1", "a.txt", sha(b"a\n"))
        rc, out = self.run_check(missing={"ART-9": "gone.txt"})
        self.assertEqual(rc, 1); self.assertIn("ALLOWLIST_DRIFT ART-9", out)

    def test_duplicate_id_and_bad_sha(self):
        self.put("a.txt", b"a\n")
        self.row("ART-1", "a.txt", sha(b"a\n")); self.row("ART-1", "a.txt", sha(b"a\n"))
        self.row("ART-3", "a.txt", "not-a-hash")
        self.row("ART-4", "a.txt", sha(b"a\n"), container="tar:x.tar")
        rc, out = self.run_check()
        self.assertEqual(rc, 1)
        self.assertEqual(out.count("BAD_ROW"), 3, out)

    def test_zip_members(self):
        zp = os.path.join(self.root, "arch.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr("in/ok.txt", b"ok\n"); z.writestr("in/bad.txt", b"changed\n")
        c = "zip:arch.zip"
        self.row("ART-1", "in/ok.txt", sha(b"ok\n"), container=c, flag="ZIP_MEMBER_PRESENT")
        self.row("ART-2", "in/bad.txt", sha(b"orig\n"), container=c, flag="ZIP_MEMBER_PRESENT")
        self.row("ART-3", "in/none.txt", sha(b"x\n"), container=c, flag="ZIP_MEMBER_PRESENT")
        self.row("ART-4", "m.txt", sha(b"x\n"), container="zip:nope.zip")
        rc, out = self.run_check()
        self.assertEqual(rc, 1)
        self.assertIn("PIN_MISMATCH ART-2 arch.zip!in/bad.txt", out)
        self.assertIn("PIN_MISSING ART-3", out); self.assertIn("PIN_MISSING ART-4", out)
        self.assertIn("1 match", out)

    def test_broken_zip_is_error(self):
        self.put("arch.zip", b"not a zip")
        self.row("ART-1", "m.txt", sha(b"x\n"), container="zip:arch.zip")
        rc, out = self.run_check()
        self.assertEqual(rc, 1); self.assertIn("cannot open archive", out)

    def test_flag_disagrees_is_notice_only(self):
        self.put("a.txt", b"a\n")
        self.row("ART-1", "a.txt", sha(b"a\n"), flag="PRESENT_CHANGED_SHA")
        rc, out = self.run_check()
        self.assertEqual(rc, 0, out); self.assertIn("FLAG_DISAGREES ART-1", out)

    def test_missing_csv_is_notice_without_git(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cap.main(["--repo", self.root, "--no-git"])
        self.assertEqual(rc, 0); self.assertIn("skipped", buf.getvalue())

    # R1: the registry itself is pinned (sha256 + row count), so it cannot be used to launder pins.
    def pinned_fixture(self):
        self.put("a.txt", b"a\n"); self.put("b.txt", b"b\n")
        self.row("ART-1", "a.txt", sha(b"a\n")); self.row("ART-2", "b.txt", sha(b"b\n"))
        self.write_csv()
        with open(os.path.join(self.root, cap.ARTIFACTS), "rb") as f:
            return sha(f.read()), len(self.rows)

    def test_registry_pinned_passes_unchanged(self):
        csv_sha, n = self.pinned_fixture()
        rc, out = self.run_check(expected_sha=csv_sha, expected_rows=n, write=False)
        self.assertEqual(rc, 0, out)

    def test_repin_row_fails(self):
        # Edit a pinned file and re-pin its row to the new bytes (audit T10).
        csv_sha, n = self.pinned_fixture()
        self.put("a.txt", b"tampered\n"); self.rows[0]["sha256"] = sha(b"tampered\n")
        rc, out = self.run_check(expected_sha=csv_sha, expected_rows=n)
        self.assertEqual(rc, 1, out)
        self.assertIn("REGISTRY_CHANGED", out); self.assertIn("sha256", out)
        self.assertIn("update EXPECTED_CSV_SHA256 and EXPECTED_ROWS", out)
        self.assertNotIn("PIN_MISMATCH", out)   # the row itself now "matches": only the CSV pin catches it

    def test_delete_row_fails(self):
        # Delete a row, then edit its file (audit T11).
        csv_sha, n = self.pinned_fixture()
        del self.rows[0]; self.put("a.txt", b"tampered\n")
        rc, out = self.run_check(expected_sha=csv_sha, expected_rows=n)
        self.assertEqual(rc, 1, out)
        self.assertIn(f"has {n - 1} row(s), expected {n}", out)
        self.assertEqual(out.count("REGISTRY_CHANGED"), 2, out)   # sha256 and row count

    def test_row_count_alone_fails(self):
        _, n = self.pinned_fixture()
        del self.rows[1]
        rc, out = self.run_check(expected_rows=n)
        self.assertEqual(rc, 1, out); self.assertIn("expected 2", out)

    def test_registry_changed_annotation(self):
        csv_sha, n = self.pinned_fixture()
        self.rows[0]["size_bytes"] = "1"
        rc, out = self.run_check(expected_sha=csv_sha, expected_rows=n, gha=True)
        self.assertEqual(rc, 1)
        self.assertIn("::error file=registry/artifacts.csv::REGISTRY_CHANGED", out)

    @unittest.skipUnless(shutil.which("git"), "git not installed")
    def test_delete_csv_fails_in_git_mode(self):
        # `git rm registry/artifacts.csv` (audit T12): an error in git mode, not a notice.
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        subprocess.run(["git", "init", "-q", self.root], check=True, env=env)
        self.put("a.txt", b"a\n")
        subprocess.run(["git", "-C", self.root, "add", "a.txt"], check=True, env=env)
        buf = io.StringIO()
        with mock.patch.object(cap, "IN_GHA", True), contextlib.redirect_stdout(buf):
            rc = cap.main(["--repo", self.root])
        out = buf.getvalue()
        self.assertEqual(rc, 1, out); self.assertIn("REGISTRY_MISSING", out)
        self.assertIn("::error file=registry/artifacts.csv::REGISTRY_MISSING", out)
        # An untracked CSV on disk does not count either.
        self.row("ART-1", "a.txt", sha(b"a\n")); self.write_csv()
        with contextlib.redirect_stdout(io.StringIO()) as buf2:
            rc = cap.main(["--repo", self.root], known_changed={}, known_missing={},
                          expected_sha=None, expected_rows=None)
        self.assertEqual(rc, 1, buf2.getvalue()); self.assertIn("REGISTRY_MISSING", buf2.getvalue())

    def test_shipped_registry_constants_match_repo(self):
        # The shipped constants describe this repository's registry/artifacts.csv.
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), cap.ARTIFACTS)
        if not os.path.isfile(path):
            self.skipTest("registry/artifacts.csv not present")
        with open(path, "rb") as f:
            data = f.read()
        self.assertEqual(sha(data), cap.EXPECTED_CSV_SHA256)
        with open(path, encoding="utf-8", newline="") as f:
            self.assertEqual(sum(1 for _ in csv.DictReader(f)), cap.EXPECTED_ROWS)

    def test_missing_column_is_usage_error(self):
        self.row("ART-1", "a.txt", sha(b"a\n"))
        self.write_csv(cols=["artifact_id", "container", "path"])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cap.main(["--repo", self.root, "--no-git"], known_changed={}, known_missing={})
        self.assertEqual(rc, 2); self.assertIn("sha256", buf.getvalue())

    def test_not_a_directory(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cap.main(["--repo", os.path.join(self.root, "nope")])
        self.assertEqual(rc, 2)

    def test_github_annotations(self):
        self.put("a.txt", b"edited\n"); self.row("ART-1", "a.txt", sha(b"a\n"))
        rc, out = self.run_check(gha=True)
        self.assertEqual(rc, 1)
        self.assertIn("::error file=registry/artifacts.csv::PIN_MISMATCH ART-1", out)

    def test_no_annotations_outside_actions(self):
        self.put("a.txt", b"edited\n"); self.row("ART-1", "a.txt", sha(b"a\n"))
        rc, out = self.run_check()
        self.assertNotIn("::error", out)

    @unittest.skipUnless(shutil.which("git"), "git not installed")
    def test_untracked_file_counts_as_missing_in_git_repo(self):
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        subprocess.run(["git", "init", "-q", self.root], check=True, env=env)
        self.put("tracked.txt", b"t\n"); self.put("untracked.txt", b"u\n")
        self.row("ART-1", "tracked.txt", sha(b"t\n"))
        self.row("ART-2", "untracked.txt", sha(b"u\n"))
        self.write_csv()
        subprocess.run(["git", "-C", self.root, "add", "tracked.txt", cap.ARTIFACTS],
                       check=True, env=env)
        rc, out = self.run_check(argv=[])
        self.assertEqual(rc, 1, out); self.assertIn("git-tracked only", out)
        self.assertIn("PIN_MISSING ART-2", out); self.assertNotIn("ART-1 ", out)
        rc, out = self.run_check(argv=["--no-git"])
        self.assertEqual(rc, 0, out)

    def test_real_allowlist_shape(self):
        # The shipped allowlist: exactly the 7 rows flagged PRESENT_CHANGED_SHA when it was added,
        # each with a full sha256, and no ID listed as both changed and missing.
        self.assertEqual(sorted(cap.KNOWN_CHANGED), ["ART-0001", "ART-0712", "ART-0743",
                                                     "ART-0744", "ART-0745", "ART-0746",
                                                     "ART-0748"])
        for path, digest in cap.KNOWN_CHANGED.values():
            self.assertTrue(cap.SHA_RE.match(digest), path)
        self.assertEqual(len(cap.KNOWN_MISSING), 52)
        self.assertFalse(set(cap.KNOWN_CHANGED) & set(cap.KNOWN_MISSING))


if __name__ == "__main__":
    unittest.main()
