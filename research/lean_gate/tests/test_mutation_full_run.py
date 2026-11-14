#!/usr/bin/env python3
"""A filtered or short mutation run must never PASS (Researcher 001 audit of PR #32, H1).

`AIEF_MUT_ONLY: '^$'` selects no mutant; before this guard the checker ran 0 mutants and still printed PASS.
These tests exercise partial_run_reason only (no Lean needed).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import lean_mutation_check as m  # noqa: E402


class FullRunTests(unittest.TestCase):
    def test_full_run_is_accepted(self):
        self.assertIsNone(m.partial_run_reason(None, len(m.MUTANTS), len(m.DEF_MUTANTS)))
        self.assertIsNone(m.partial_run_reason("", len(m.MUTANTS), len(m.DEF_MUTANTS)))

    def test_any_filter_fails(self):
        for only in ["^$", ".*", "M1_", "NOTHING"]:
            with self.subTest(only=only):
                self.assertIsNotNone(m.partial_run_reason(only, len(m.MUTANTS), len(m.DEF_MUTANTS)))

    def test_short_run_fails(self):
        self.assertIsNotNone(m.partial_run_reason(None, 0, 0))
        self.assertIsNotNone(m.partial_run_reason(None, len(m.MUTANTS) - 1, len(m.DEF_MUTANTS)))
        self.assertIsNotNone(m.partial_run_reason(None, len(m.MUTANTS), len(m.DEF_MUTANTS) - 1))

    def test_empty_lists_fail(self):
        self.assertIsNotNone(m.partial_run_reason(None, 0, 0, 0, 0))

    def test_main_counts_and_checks(self):
        src = open(m.__file__, encoding="utf-8").read()
        self.assertEqual(src.count("n_stmt_ran += 1"), 1)
        self.assertEqual(src.count("n_def_ran += 1"), 1)
        self.assertIn("why = partial_run_reason(only, n_stmt_ran, n_def_ran)", src)
        i, j = src.index("why = partial_run_reason("), src.index('print("RESULT:"')
        self.assertLess(i, j)


if __name__ == "__main__":
    unittest.main()
