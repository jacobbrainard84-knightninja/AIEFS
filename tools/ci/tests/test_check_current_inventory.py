#!/usr/bin/env python3
"""Self-tests for tools/ci/check_current_inventory.py and
registry/reconciliation/build_current_inventory.py (stdlib unittest, synthetic temp git repos).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v
"""
import contextlib
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
import check_current_inventory as cci  # noqa: E402

GEN_REL = os.path.join("registry", "reconciliation", "build_current_inventory.py")
SNAP = ("artifact_id,container,path,sha256\n"
        "ART-0001,worktree,a.txt,{a}\n"
        "ART-0002,worktree,b.txt,{old}\n")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cci.main(argv)
    return rc, buf.getvalue()


class CurrentInventoryTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.root = self.d.name
        self.g = ["git", "-C", self.root]
        subprocess.run(self.g + ["init", "-q"], check=True)
        os.makedirs(os.path.join(self.root, "registry", "reconciliation"))
        shutil.copy(os.path.join(REPO, GEN_REL), os.path.join(self.root, GEN_REL))
        self.write("a.txt", b"alpha\n")
        self.write("b.txt", b"beta changed\n")
        self.write("c.txt", b"new file\n")
        with zipfile.ZipFile(os.path.join(self.root, "pack.zip"), "w") as z:
            z.writestr("inner/x.txt", b"x\n")
            z.writestr("inner/", b"")
        subprocess.run(self.g + ["add", "pack.zip", GEN_REL], check=True)
        self.write("registry/artifacts.csv", SNAP.format(a=sha(b"alpha\n"), old=sha(b"beta\n")).encode())
        self.gen = cci.load_generator(self.root)
        self.regen()

    def tearDown(self):
        self.d.cleanup()

    def write(self, rel, data):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)
        subprocess.run(self.g + ["add", rel], check=True)

    def regen(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.gen.main(["--repo", self.root]), 0)
        subprocess.run(self.g + ["add", self.gen.OUTPUT], check=True)

    def inventory(self):
        with open(os.path.join(self.root, self.gen.OUTPUT), "rb") as f:
            return f.read()

    def set_inventory(self, data):
        with open(os.path.join(self.root, self.gen.OUTPUT), "wb") as f:
            f.write(data)

    def codes(self):
        return [c for c, _ in cci.check(self.root)]

    def test_fresh_inventory_passes(self):
        rc, out = run(["--repo", self.root])
        self.assertEqual(rc, 0, out)
        self.assertIn("PASS", out)

    def test_every_tracked_file_once_with_sha_and_snapshot_state(self):
        text = self.inventory().decode()
        lines = text.splitlines()
        self.assertEqual(lines[0], ",".join(self.gen.COLUMNS))
        rows = {(l.split(",")[0], l.split(",")[1]): l.split(",") for l in lines[1:]}
        tracked = subprocess.run(self.g + ["ls-files"], capture_output=True, text=True).stdout.split()
        for p in tracked:
            if p == self.gen.OUTPUT:
                self.assertNotIn(("worktree", p), rows)   # self-excluded
            else:
                self.assertIn(("worktree", p), rows)
        self.assertEqual(len(lines) - 1, len(tracked) - 1 + 1)  # + one zip member, dir entry skipped
        self.assertEqual(rows[("worktree", "a.txt")][2], sha(b"alpha\n"))
        self.assertEqual(rows[("worktree", "a.txt")][4:], ["ART-0001", "same_sha"])
        self.assertEqual(rows[("worktree", "b.txt")][4:], ["ART-0002", "changed_sha"])
        self.assertEqual(rows[("worktree", "c.txt")][4:], ["", "not_in_snapshot"])
        self.assertEqual(rows[("zip:pack.zip", "inner/x.txt")][2], sha(b"x\n"))

    def test_deterministic(self):
        first = self.inventory()
        self.regen()
        self.assertEqual(first, self.inventory())
        self.assertNotIn(b"\r", first)

    def test_missing_inventory(self):
        subprocess.run(self.g + ["rm", "-q", "--cached", self.gen.OUTPUT], check=True)
        self.assertEqual(self.codes(), ["INVENTORY_MISSING"])

    def test_new_untracked_row_and_missing_row(self):
        self.write("d.txt", b"later\n")
        self.assertIn("NOT_INVENTORIED", self.codes())
        subprocess.run(self.g + ["rm", "-q", "-f", "c.txt"], check=True)
        codes = self.codes()
        self.assertIn("NOT_IN_TREE", codes)
        self.regen()
        self.assertEqual(self.codes(), [])

    def test_sha_mismatch(self):
        with open(os.path.join(self.root, "a.txt"), "ab") as f:
            f.write(b"edit\n")
        self.assertEqual(self.codes(), ["SHA_MISMATCH"])

    def test_duplicate_row(self):
        data = self.inventory()
        last = data.rstrip(b"\n").split(b"\n")[-1]
        self.set_inventory(data + last + b"\n")
        self.assertEqual(self.codes(), ["DUPLICATE_ROW"])

    def test_snapshot_fields_and_header(self):
        data = self.inventory().replace(b"same_sha", b"changed_sha", 1)
        self.set_inventory(data)
        self.assertEqual(self.codes(), ["SNAPSHOT_FIELDS"])
        self.set_inventory(b"path,sha256\n")
        self.assertEqual(self.codes(), ["BAD_HEADER"])

    def test_not_canonical(self):
        self.set_inventory(self.inventory().replace(b"\n", b"\r\n"))
        self.assertEqual(self.codes(), ["NOT_CANONICAL"])

    def test_cli_failure_exit_code(self):
        with open(os.path.join(self.root, "c.txt"), "ab") as f:
            f.write(b"x")
        rc, out = run(["--repo", self.root])
        self.assertEqual(rc, 1)
        self.assertIn("SHA_MISMATCH", out)
        self.assertIn("build_current_inventory.py", out)


if __name__ == "__main__":
    unittest.main()
