#!/usr/bin/env python3
"""Guard for the "Lean-gate mutation check" step in .github/workflows/lean.yml.

The step filters on the matrix row inside its run line (`if [ "$PROJECT" = "AIEFGateCore" ]`), because the step
`if:` must stay exactly the presence gate (see test_lean_presence.py). If the matrix row were renamed, the step would
quietly print "no mutation check for ..." on every row and the red team would stop running with CI still green.
These tests fail instead.

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v
"""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORKFLOW = os.path.join(REPO, ".github", "workflows", "lean.yml")
STEP_NAME = "- name: Lean-gate mutation check"
CHECKER = "research/lean_gate/lean_mutation_check.py"


def step_block(text):
    lines = text.splitlines()
    starts = [k for k, l in enumerate(lines) if l.strip().startswith(STEP_NAME)]
    if len(starts) != 1:
        return None
    k = starts[0]
    indent = len(lines[k]) - len(lines[k].lstrip())
    out = [lines[k]]
    for l in lines[k + 1:]:
        if l.strip() and (len(l) - len(l.lstrip())) <= indent:
            break
        out.append(l)
    return "\n".join(out)


class LeanMutationStepTests(unittest.TestCase):
    def setUp(self):
        with open(WORKFLOW, encoding="utf-8") as fh:
            self.text = fh.read()
        self.block = step_block(self.text)

    def test_exactly_one_mutation_step(self):
        self.assertIsNotNone(self.block, "expected exactly one '%s' step in lean.yml" % STEP_NAME)

    def test_filter_names_a_real_matrix_row(self):
        m = re.search(r'\[ "\$PROJECT" = "([A-Za-z0-9_]+)" \]', self.block or "")
        self.assertIsNotNone(m, "mutation step must filter on $PROJECT in its run line")
        rows = re.findall(r"\{\s*project:\s*([A-Za-z0-9_]+)\s*,", self.text)
        self.assertIn(m.group(1), rows, "mutation step filters on a project that is not a matrix row")
        self.assertTrue(os.path.isdir(os.path.join(REPO, "lean", m.group(1))),
                        "mutation step filters on a project with no lean/<project> directory")

    def test_runs_the_checker_and_project_env_is_matrix(self):
        b = self.block or ""
        self.assertIn("python3 " + CHECKER, b)
        self.assertTrue(os.path.isfile(os.path.join(REPO, CHECKER)), CHECKER + " missing")
        self.assertRegex(b, r"PROJECT:\s*\$\{\{\s*matrix\.project\s*\}\}")

    def test_step_block_parser_rejects_renamed_row(self):
        renamed = self.text.replace('"$PROJECT" = "AIEFGateCore"', '"$PROJECT" = "AIEFGateCoreX"')
        m = re.search(r'\[ "\$PROJECT" = "([A-Za-z0-9_]+)" \]', step_block(renamed) or "")
        rows = re.findall(r"\{\s*project:\s*([A-Za-z0-9_]+)\s*,", renamed)
        self.assertNotIn(m.group(1), rows)


if __name__ == "__main__":
    unittest.main()
