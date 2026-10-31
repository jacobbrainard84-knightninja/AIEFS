#!/usr/bin/env python3
"""Fresh-clone tests for audits/engineering/validate_registry_against_tree.py (stdlib unittest).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v
Each test builds a tiny synthetic git repository (an "origin" plus a fresh `git clone` of it) that
contains a copy of the validator and two small registry CSVs, so no local-only commit such as
ce8cced exists. Needs the `git` command; skipped if it is missing.
"""
import csv
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SCRIPT_REL = "audits/engineering/validate_registry_against_tree.py"
SCRIPT = os.path.join(REPO, SCRIPT_REL)
BASIC = "lean/AIEFProofs/AIEFProofs/Basic.lean"
OTHER = "lean/AIEFProofs/README.md"
GIT_ENV = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
ART_COLS = ["artifact_id", "container", "path", "sha256", "size_bytes"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, *args], check=True, capture_output=True,
                          env=GIT_ENV).stdout.decode().strip()


@unittest.skipUnless(shutil.which("git") and os.path.isfile(SCRIPT), "git or validator missing")
class FreshCloneTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        origin = os.path.join(self.d.name, "origin")
        os.makedirs(origin)
        git(origin, "init", "-q")
        self.put(origin, SCRIPT_REL, open(SCRIPT, "rb").read())
        # base commit: the inventoried state
        files = {"a.txt": b"a\n", BASIC: b"basic v1\n", OTHER: b"readme v1\n", "gone.txt": b"g\n"}
        for rel, data in files.items():
            self.put(origin, rel, data)
        rows = [{"artifact_id": f"ART-{i:04d}", "container": "worktree", "path": rel,
                 "sha256": sha(data), "size_bytes": str(len(data))}
                for i, (rel, data) in enumerate(files.items(), 1)]
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=ART_COLS, lineterminator="\n")
        w.writeheader(); w.writerows(rows)
        self.put(origin, "registry/artifacts.csv", buf.getvalue().encode())
        self.put(origin, "registry/relocation_map.csv",
                 b"current_path,file_count\nlean/,2\nmissing_dir/,1\n")
        git(origin, "add", "-A"); git(origin, "commit", "-q", "-m", "base")
        self.base = git(origin, "rev-parse", "HEAD")
        # later commit: main edits README, merge prep edits Basic.lean, gone.txt deleted
        self.put(origin, BASIC, b"basic v2\n"); self.put(origin, OTHER, b"readme v2\n")
        os.remove(os.path.join(origin, "gone.txt"))
        git(origin, "add", "-A"); git(origin, "commit", "-q", "-m", "edits")
        self.clone = os.path.join(self.d.name, "clone")
        subprocess.run(["git", "clone", "-q", origin, self.clone], check=True, env=GIT_ENV,
                       capture_output=True)

    def tearDown(self):
        self.d.cleanup()

    @staticmethod
    def put(root, rel, data):
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    def run_script(self, *args):
        return subprocess.run([sys.executable, SCRIPT_REL, "--base", self.base, *args],
                              cwd=self.clone, capture_output=True, text=True, env=GIT_ENV)

    def read(self, rel):
        with open(os.path.join(self.clone, rel), "rb") as f:
            return f.read()

    def notes(self):
        rows = csv.DictReader(io.StringIO(self.read("registry/artifacts.csv").decode()))
        return {r["path"]: (r["tree_check_2026_10_28"], r["tree_check_note"]) for r in rows}

    def test_default_runs_on_fresh_clone(self):
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn('"PRESENT_CHANGED_SHA": 2', r.stdout)
        self.assertIn('"MISSING_DELETED_ON_MAIN": 1', r.stdout)

    def test_write_default_notes_lf_and_idempotent(self):
        r = self.run_script("--write")
        self.assertEqual(r.returncode, 0, r.stderr)
        n = self.notes()
        self.assertEqual(n[BASIC], ("PRESENT_CHANGED_SHA",
                                    "edited by merge-prep after the merge (see git log)"))
        self.assertEqual(n[OTHER], ("PRESENT_CHANGED_SHA", "changed on main or in the merge"))
        self.assertEqual(n["a.txt"][0], "PRESENT_SAME_SHA")
        self.assertEqual(n["gone.txt"][0], "MISSING_DELETED_ON_MAIN")
        for rel in ("registry/artifacts.csv", "registry/relocation_map.csv"):
            data = self.read(rel)
            self.assertNotIn(b"\r", data, rel); self.assertTrue(data.endswith(b"\n"))
        first = self.read("registry/artifacts.csv")
        git(self.clone, "commit", "-q", "-am", "flags")
        r = self.run_script("--write")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.read("registry/artifacts.csv"), first)
        self.assertEqual(git(self.clone, "status", "--porcelain"), "")

    def test_missing_edited_since_commit_is_clear_error(self):
        r = self.run_script("--edited-since", "ce8cced")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--edited-since ce8cced: no such commit", r.stderr)
        self.assertIn("omit --edited-since", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_missing_base_commit_is_clear_error(self):
        r = subprocess.run([sys.executable, SCRIPT_REL, "--base", "0" * 40], cwd=self.clone,
                           capture_output=True, text=True, env=GIT_ENV)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--base", r.stderr); self.assertNotIn("Traceback", r.stderr)

    def test_default_base_missing_message_is_accurate(self):
        # default --base (e47bad1) is absent from the synthetic clone: must not say "omit --base"
        r = subprocess.run([sys.executable, SCRIPT_REL], cwd=self.clone, capture_output=True,
                           text=True, env=GIT_ENV)
        self.assertEqual(r.returncode, 2)
        self.assertIn("e47bad1 is the default --base", r.stderr)
        self.assertNotIn("omit --base", r.stderr)
        # passing the default explicitly must not suggest omitting it either
        r = subprocess.run([sys.executable, SCRIPT_REL, "--base", "e47bad1"], cwd=self.clone,
                           capture_output=True, text=True, env=GIT_ENV)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("omit --base", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_shallow_clone_message_suggests_unshallow(self):
        shallow = os.path.join(self.d.name, "shallow")
        subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + os.path.join(self.d.name, "origin"),
                        shallow], check=True, env=GIT_ENV, capture_output=True)
        r = subprocess.run([sys.executable, SCRIPT_REL, "--base", self.base], cwd=shallow,
                           capture_output=True, text=True, env=GIT_ENV)
        self.assertEqual(r.returncode, 2)
        self.assertIn("git fetch --unshallow", r.stderr)
        self.assertIn("omit --base to use the default e47bad1", r.stderr)   # a non-default --base was given
        r = subprocess.run([sys.executable, SCRIPT_REL], cwd=shallow, capture_output=True, text=True,
                           env=GIT_ENV)
        self.assertEqual(r.returncode, 2)
        self.assertIn("git fetch --unshallow", r.stderr)
        self.assertNotIn("omit --base", r.stderr)

    def test_edited_since_override(self):
        r = self.run_script("--edited-since", self.base, "--write")
        self.assertEqual(r.returncode, 0, r.stderr)
        n = self.notes()
        self.assertEqual(n[OTHER][1], "edited by merge-prep after the merge (see git log)")
        self.assertEqual(n[BASIC][1], "edited by merge-prep after the merge (see git log)")


if __name__ == "__main__":
    unittest.main()
