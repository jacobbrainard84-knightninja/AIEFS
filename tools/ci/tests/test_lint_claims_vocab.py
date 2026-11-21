"""Status-vocabulary parsing tests for tools/ci/lint_claims.py (stdlib unittest).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v

H3 (2026-11-20), lint_claims L247 `or -> and`: when the line after the '## Status vocabulary' heading is not a
fence, parse_readme_vocab must return [] (lint then falls back / errors); the mutant instead walks on and takes
the NEXT fenced block in the README as the status vocabulary. These tests pin the exact return values.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import lint_claims  # noqa: E402

H = lint_claims.VOCAB_HEADING


class ReadmeVocabTests(unittest.TestCase):
    def test_control_fenced_block_right_after_heading(self):
        text = f"# R\n\n{H}\n\n```\nFrozen\nSupported\n```\n"
        self.assertEqual(lint_claims.parse_readme_vocab(text), ["Frozen", "Supported"])

    def test_prose_after_heading_is_not_a_vocabulary(self):
        """Kills L247: a later, unrelated fenced block must NOT become the status vocabulary."""
        text = (f"# R\n\n{H}\n\nThe statuses are listed elsewhere.\n\n## Other section\n\n"
                "```\nAnything\nGoes\n```\n")
        self.assertEqual(lint_claims.parse_readme_vocab(text), [])

    def test_heading_at_end_of_file(self):
        """Control for the `k >= len(lines)` side of the same condition."""
        self.assertEqual(lint_claims.parse_readme_vocab(f"# R\n\n{H}\n\n\n"), [])


if __name__ == "__main__":
    unittest.main()
