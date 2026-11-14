#!/usr/bin/env python3
"""A filtered or short mutation run must never PASS (Researcher 001 audit of PR #32, H1).

`AIEF_MUT_ONLY: '^$'` selects no mutant; before this guard the checker ran 0 mutants and still printed PASS.
partial_run_reason is tested directly, and main() is run end to end with Lean stubbed out (StubbedMainTests), so the
wiring (counters, the PARTIAL RUN check, the exit code) is exercised, not only its text.
"""
import os
import sys
import contextlib
import io
import unittest
from unittest import mock

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


class StubbedMainTests(unittest.TestCase):
    """main() with every Lean call stubbed so that each check comes out good. Unfiltered it must exit 0; any
    AIEF_MUT_ONLY must make it exit 1 (Researcher 001 note F-A on 6ff39ae)."""

    def run_main(self, only):
        srcs = {f: (m.SRCDIR / f).read_text() for f in
                {x[1] for x in m.MUTANTS} | {x[1] for x in m.DEF_MUTANTS} | {x[1] for x in m.EQUIV_CONTROLS}
                | {x[1] for x in m.TYPO_CONTROLS} | {x[1] for x in m.KNOWN_SURVIVORS}
                | {x[1] for x in m.STATEMENT_CONTROLS} | {m.LEGACY_NAME_ONLY[1]}}
        clean = set(srcs.values())
        lname, lf, lthm, ledits = m.LEGACY_NAME_ONLY
        legacy = m.mutate(srcs[lf], lthm, ledits)
        ctrl = {m.mutate(srcs[f], thm, e) for _, f, thm, e, _, _ in m.STATEMENT_CONTROLS}
        tag = {}
        for lst, t in ((m.DEF_MUTANTS, "KILLED"), (m.EQUIV_CONTROLS, "BUILDS"), (m.TYPO_CONTROLS, "INVALID")):
            for x in lst:
                tag[m.mutate_file(srcs[x[1]], x[2])] = t
        for x in m.KNOWN_SURVIVORS:
            clean.add(m.mutate_file(srcs[x[1]], x[2]))

        def lean(text):
            if text in clean:
                return 0, [], ""
            if text == legacy:
                return 1, ["Mutant.lean:1:1: error: unknown identifier 'h'"], ""
            return 1, ["Mutant.lean:1:1: error: type mismatch"], ""

        def refute(msrc, src, thm, closure, term):
            good = msrc not in ctrl
            return good, "stub", good, []

        env = dict(os.environ)
        env.pop("AIEF_MUT_ONLY", None)
        if only is not None:
            env["AIEF_MUT_ONLY"] = only
        out = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(m, "lean", lean), mock.patch.object(m, "refute", refute), \
                mock.patch.object(m, "failing_decls", lambda msrc, errs: [tag.get(msrc, "?")]), \
                mock.patch.object(m, "def_mutant_status", lambda rc, errs, failing, pins: failing[0]), \
                contextlib.redirect_stdout(out):
            with self.assertRaises(SystemExit) as cm:
                m.main()
        return cm.exception.code, out.getvalue()

    def test_unfiltered_stubbed_run_passes(self):
        code, out = self.run_main(None)
        self.assertEqual(code, 0, out[-2000:])
        self.assertIn("RESULT: PASS", out)
        self.assertNotIn("PARTIAL RUN", out)
        self.assertIn(f"mutants rejected in total: {len(m.MUTANTS) + len(m.DEF_MUTANTS)}/", out)

    # Wiring mutants checked against these tests by the author (each makes a test fail): dropping `ok = False` after
    # PARTIAL RUN, `if why:` -> `if False:`, `only = None`, `ok = True` before RESULT, `sys.exit(0)`. One edit is
    # equivalent under the current rule and survives: moving `n_stmt_ran += 1` above the filter (any AIEF_MUT_ONLY
    # already fails, and without a filter every mutant runs).

    def test_filtered_stubbed_run_fails(self):
        for only in ["^$", "^M1_", ".*", "M37"]:
            with self.subTest(only=only):
                code, out = self.run_main(only)
                self.assertEqual(code, 1)
                self.assertIn("PARTIAL RUN", out)
                self.assertIn("RESULT: FAIL", out)


if __name__ == "__main__":
    unittest.main()
