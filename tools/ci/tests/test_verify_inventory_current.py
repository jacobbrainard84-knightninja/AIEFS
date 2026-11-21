"""Self-tests for audits/engineering/verify_inventory_current.py gates [3/5] and [4/5] (stdlib unittest).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v

H3 (2026-11-20): the script had no test file; [3/5] (controlled vocabularies over registry/{artifacts,claims,
studies,relocation_map}.csv and Unreviewed = 0) has no other CI backstop, and [4/5] could verify zero Lean digests
and still print PASS (mutants L93 drop `not`, L97 `== -> !=`, L94/L98 `continue -> break`). These tests import the
module, point its REPO at a synthetic temp tree (never the real repository, never lean/AIEFProofs of the repo),
stub run_tool (gates [1/5] and [2/5] run the sub-checkers, which CI also runs as their own steps), and run
main(["--skip-authority"]). They assert the exit code AND the exact gate message, including the exact count of
verified Lean digests.
"""
import contextlib
import csv
import hashlib
import importlib.util
import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parents[2] / "audits" / "engineering" / "verify_inventory_current.py"
_spec = importlib.util.spec_from_file_location("verify_inventory_current_under_test", SCRIPT)
vic = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vic)

TABLES = ("artifacts.csv", "claims.csv", "studies.csv", "relocation_map.csv")
LEDGER = "AIEF_LEAN_PROJECT_LOCK_HASHES.txt"
GOOD = {"artifact_status": "Frozen", "evidence_scope": "Formalized theorem"}


class VerifyInventoryCurrentTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="vic_"))
        self.addCleanup(shutil.rmtree, self.root, True)
        for t in TABLES:
            self.write_table(t, [dict(GOOD, path=f"x/{t}.1"), dict(GOOD, path=f"x/{t}.2")])
        self.lean = self.root / "lean" / "AIEFProofs"
        self.lean.mkdir(parents=True)
        self.files = {"lean-toolchain": b"leanprover/lean4:v4.0.0\n", "lakefile.toml": b'name = "x"\n'}
        for name, data in self.files.items():
            (self.lean / name).write_bytes(data)
        for p in (mock.patch.object(vic, "REPO", self.root), mock.patch.object(vic, "run_tool", lambda rel: 0)):
            p.start()
            self.addCleanup(p.stop)

    def write_table(self, name, rows):
        d = self.root / "registry"
        d.mkdir(exist_ok=True)
        with open(d / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["path", "artifact_status", "evidence_scope"])
            w.writeheader()
            w.writerows(rows)

    def entry(self, name):
        return f"{hashlib.sha256(self.files[name]).hexdigest()}  ./{name}"

    def write_ledger(self, lines):
        (self.lean / LEDGER).write_text("\n".join(lines) + "\n", encoding="utf-8")

    def run_main(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = vic.main(["--skip-authority"])
        return rc, out.getvalue(), err.getvalue()

    def standard_ledger(self):
        # the self-entry sits between two real entries (kills L98 `continue -> break`); no blank line here, so
        # L93 drop-`not` verifies nothing instead of crashing on a blank line.
        self.write_ledger([self.entry("lean-toolchain"), f"{'0' * 64}  ./{LEDGER}", self.entry("lakefile.toml")])

    # ---- control
    def test_control_clean_tree_passes_with_exact_digest_count(self):
        self.standard_ledger()
        rc, out, err = self.run_main()
        self.assertEqual(rc, 0, out + err)
        self.assertIn("  PASS: vocabularies conform (Unreviewed = 0).", out.splitlines())
        self.assertIn("  PASS: 2 Lean source/config digests verified.", out.splitlines())

    # ---- [3/5] vocabularies, every table, status and scope separately (kills L81 and L78 `or -> and`)
    def test_bad_status_fails_in_every_table(self):
        self.standard_ledger()
        for t in TABLES:
            with self.subTest(table=t):
                self.write_table(t, [dict(GOOD, path="x/1"), dict(GOOD, path="x/2", artifact_status="Bogus")])
                rc, out, err = self.run_main()
                self.assertEqual(rc, 1, out + err)
                self.assertIn(f"FAIL: {t}:3 status='Bogus' scope='Formalized theorem'", err)
                self.assertNotIn("PASS: vocabularies conform", out)
                self.write_table(t, [dict(GOOD, path="x/1"), dict(GOOD, path="x/2")])

    def test_bad_scope_fails_in_every_table(self):
        self.standard_ledger()
        for t in TABLES:
            with self.subTest(table=t):
                self.write_table(t, [dict(GOOD, path="x/1", evidence_scope="Proved")])
                rc, out, err = self.run_main()
                self.assertEqual(rc, 1, out + err)
                self.assertIn(f"FAIL: {t}:2 status='Frozen' scope='Proved'", err)
                self.write_table(t, [dict(GOOD, path="x/1")])

    # ---- [3/5] Unreviewed = 0 (kills L86 `return 1 -> 0` and L83 `== -> !=`)
    def test_unreviewed_artifact_fails(self):
        self.standard_ledger()
        self.write_table("artifacts.csv", [dict(GOOD, path="x/1"),
                                           dict(GOOD, path="x/2", artifact_status="Unreviewed")])
        rc, out, err = self.run_main()
        self.assertEqual(rc, 1, out + err)
        self.assertIn("FAIL: 1 artifacts still Unreviewed", err)
        self.assertNotIn("PASS: vocabularies conform", out)

    # ---- [4/5] Lean lock ledger
    def test_lean_digest_mismatch_fails(self):
        """Kills L101 `return 1 -> 0` and L99 `!= -> ==`."""
        self.standard_ledger()
        (self.lean / "lakefile.toml").write_bytes(b'name = "tampered"\n')
        rc, out, err = self.run_main()
        self.assertEqual(rc, 1, out + err)
        self.assertIn(f"FAIL: Lean lock hash mismatch on {self.lean / 'lakefile.toml'}", err)

    def test_blank_line_does_not_end_the_ledger(self):
        """Kills L94 `continue -> break`: an entry after a blank line is still verified (exact count)."""
        self.write_ledger([self.entry("lean-toolchain"), "", self.entry("lakefile.toml"), f"{'0' * 64}  ./{LEDGER}"])
        rc, out, err = self.run_main()
        self.assertEqual(rc, 0, out + err)
        self.assertIn("  PASS: 2 Lean source/config digests verified.", out.splitlines())

    def test_zero_digests_verified_is_not_a_silent_pass(self):
        """The L93/L97 class: the exact count must equal the ledger's non-self entries, never 0."""
        self.standard_ledger()
        rc, out, err = self.run_main()
        line = [ln for ln in out.splitlines() if "Lean source/config digests verified" in ln]
        self.assertEqual(len(line), 1, out)
        n = int(line[0].split()[1])
        self.assertGreater(n, 0, out)
        self.assertEqual(n, 2, out)


if __name__ == "__main__":
    unittest.main()
