"""Self-tests for tools/ci/check_pinned_restatement.py (Lean P3 bridge; stdlib unittest).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v

The real checkout must PASS. Negative controls on a temporary copy of the relevant files: a one-character
change to the restated `vCtrl` (a deliberately wrong bridge object), a whitespace-only change, an extra renamed
line, a changed pinned source (with its sums list updated to match), an extra unchecked file under Pinned/, a
missing restated file, and a shadowing tools/ci/hashlib.py must each give the documented result.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_pinned_restatement as cpr  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CHECKER = os.path.abspath(cpr.__file__)
VCTRL_OK = "def vCtrl : Fin 3 → ℚ\n  | 0 => 1\n  | 1 => -1\n  | 2 => -1\n"
VCTRL_BAD = "def vCtrl : Fin 3 → ℚ\n  | 0 => 1\n  | 1 => -1\n  | 2 => 1\n"


def rd(p, mode="r"):
    with open(p, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        return f.read()


def wr(p, data, mode="w"):
    with open(p, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        f.write(data)


def run(repo, checker=CHECKER):
    r = subprocess.run([sys.executable, checker, "--repo", repo], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class RealRepo(unittest.TestCase):
    def test_real_checkout_passes(self):
        rc, out = run(REPO)
        self.assertEqual(rc, 0, out)
        self.assertIn(f"== result: {len(cpr.PAIRS)} pinned module(s), 0 error(s) -> PASS", out)

    def test_pins_match_pinned_sums_list(self):
        sums = cpr.read_sums(os.path.join(REPO, cpr.PINNED_SUMS))
        for rel, _, expected in cpr.PAIRS:
            self.assertEqual(sums[rel], expected)


class NegativeControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for d in (cpr.PINNED_DIR + "/AIEFProofs", cpr.RESTATED_DIR, "tools/ci"):
            os.makedirs(os.path.join(self.tmp, d), exist_ok=True)
        shutil.copy(os.path.join(REPO, cpr.PINNED_SUMS), os.path.join(self.tmp, cpr.PINNED_SUMS))
        for rel, name, _ in cpr.PAIRS:
            shutil.copy(os.path.join(REPO, cpr.PINNED_DIR, rel), os.path.join(self.tmp, cpr.PINNED_DIR, rel))
            shutil.copy(os.path.join(REPO, cpr.RESTATED_DIR, name), os.path.join(self.tmp, cpr.RESTATED_DIR, name))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def edit(self, rel, old, new):
        p = os.path.join(self.tmp, rel)
        s = rd(p)
        self.assertEqual(s.count(old), 1, (rel, old))
        wr(p, s.replace(old, new))

    def assertFails(self, needle):
        rc, out = run(self.tmp)
        self.assertEqual(rc, 1, out)
        self.assertIn("error(s) -> FAIL", out)
        self.assertIn(needle, out)

    def test_copy_passes(self):
        rc, out = run(self.tmp)
        self.assertEqual(rc, 0, out)

    def test_wrong_kernel_vector_in_restatement_fails(self):
        self.edit(cpr.RESTATED_DIR + "/ControllerFiber.lean", VCTRL_OK, VCTRL_BAD)
        self.assertFails("ControllerFiber.lean: differs from substituted")

    def test_whitespace_only_change_fails(self):
        self.edit(cpr.RESTATED_DIR + "/CompleteGraphIncidence.lean", "def vRay (c : Fin 3)",
                  "def vRay  (c : Fin 3)")
        self.assertFails("CompleteGraphIncidence.lean: differs from substituted")

    def test_trailing_newline_change_fails(self):
        p = os.path.join(self.tmp, cpr.RESTATED_DIR, "ControllerFiberQuotient.lean")
        wr(p, b"\n", "ab")
        self.assertFails("ControllerFiberQuotient.lean: differs from substituted")

    def test_unlisted_line_rename_fails(self):
        self.edit(cpr.RESTATED_DIR + "/ControllerFiber.lean", "namespace ControllerFiber\n",
                  "namespace ControllerFiberX\n")
        self.edit(cpr.RESTATED_DIR + "/ControllerFiber.lean", "end ControllerFiber\n", "end ControllerFiberX\n")
        self.assertFails("ControllerFiber.lean: differs from substituted")

    def test_changed_pinned_source_fails_even_with_updated_sums(self):
        rel = cpr.PINNED_DIR + "/AIEFProofs/ControllerFiber.lean"
        self.edit(rel, VCTRL_OK, VCTRL_BAD)
        self.edit(cpr.RESTATED_DIR + "/ControllerFiber.lean", VCTRL_OK, VCTRL_BAD)
        new = cpr.sha(rd(os.path.join(self.tmp, rel), "rb"))
        self.edit(cpr.PINNED_SUMS, "b51e07e83ac173decfbe276afd48a4871caf34edd20aad643a8897addec63411", new)
        self.assertFails("!= hard-coded pin")

    def test_extra_file_under_pinned_fails(self):
        wr(os.path.join(self.tmp, cpr.RESTATED_DIR, "Extra.lean"), "-- unchecked\n")
        self.assertFails("files not covered by this checker: ['Extra.lean']")

    def test_missing_restated_file_fails(self):
        os.remove(os.path.join(self.tmp, cpr.RESTATED_DIR, "ControllerFiberProjector.lean"))
        self.assertFails("ControllerFiberProjector.lean: cannot read restated file")

    def test_shadow_hashlib_is_not_imported(self):
        # A sibling hashlib.py that would make every digest look right must not be used (python -I).
        ci = os.path.join(self.tmp, "tools", "ci")
        shutil.copy(CHECKER, os.path.join(ci, "check_pinned_restatement.py"))
        wr(os.path.join(ci, "hashlib.py"),
           "class _H:\n    def __init__(self, b): pass\n    def hexdigest(self): return 'f' * 64\n"
           "def sha256(b=b''): return _H(b)\n")
        rc, out = run(self.tmp, os.path.join(ci, "check_pinned_restatement.py"))
        self.assertEqual(rc, 0, out)
        self.assertNotIn("ffffffffffff", out)


if __name__ == "__main__":
    unittest.main()
