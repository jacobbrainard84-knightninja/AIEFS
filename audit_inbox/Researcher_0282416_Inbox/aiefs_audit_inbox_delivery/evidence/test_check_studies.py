#!/usr/bin/env python3
"""Unit tests for tools/ci/check_studies.py."""

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_studies import check_studies


class CheckStudiesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.reg = os.path.join(self.root, "registry")
        os.makedirs(self.reg, exist_ok=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_csv(self):
        rc, errs = check_studies(self.root, strict=True)
        self.assertEqual(rc, 2)

    def test_valid_entrypoints(self):
        # Create dummy file
        dummy = os.path.join(self.root, "run.py")
        with open(dummy, "w") as f:
            f.write("# dummy")

        csv_path = os.path.join(self.reg, "studies.csv")
        with open(csv_path, "w") as f:
            f.write("study_id,canonical_entrypoints\n")
            f.write("STUDY_1,run.py;historical_missing:old.py;alias_of:new.py\n")

        rc, errs = check_studies(self.root, strict=True)
        self.assertEqual(rc, 0)
        self.assertEqual(len(errs), 0)

    def test_missing_entrypoint_fails_strict(self):
        csv_path = os.path.join(self.reg, "studies.csv")
        with open(csv_path, "w") as f:
            f.write("study_id,canonical_entrypoints\n")
            f.write("STUDY_FAIL,nonexistent_file.py\n")

        rc, errs = check_studies(self.root, strict=True)
        self.assertEqual(rc, 1)
        self.assertEqual(len(errs), 1)


if __name__ == "__main__":
    unittest.main()
