#!/usr/bin/env python3
"""Guard for the "Lean-gate mutation check" step in .github/workflows/lean.yml.

The step filters on the matrix row inside its run line (`if [ "$PROJECT" = "AIEFGateCore" ]`), because the step
`if:` must stay exactly the presence gate (see test_lean_presence.py). If the matrix row were renamed, the step would
quietly print "no mutation check for ..." on every row and the red team would stop running with CI still green.
These tests fail instead.

The run script and the PROJECT env line are pinned exactly (comments and blank lines are not ignored), so a
commented-out checker call, moving the call into the else branch, appending `|| true`, or setting PROJECT to a
constant with the matrix expression left in a comment all fail test_run_script_is_exact / test_project_env_is_exact.
test_known_disablings_are_rejected applies each of those edits to the real workflow text and requires rejection.

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


EXPECTED_RUN = [
    'if [ "$PROJECT" = "AIEFGateCore" ]; then',
    "python3 " + CHECKER,
    "else",
    'echo "no mutation check for $PROJECT"',
    "fi",
]
EXPECTED_PROJECT_ENV = "PROJECT: ${{ matrix.project }}"


def run_script(block):
    """Lines of the step's `run: |` script, stripped of indentation; None if absent. Nothing is skipped."""
    if block is None:
        return None
    lines = block.splitlines()
    ks = [k for k, l in enumerate(lines) if l.strip() == "run: |"]
    if len(ks) != 1:
        return None
    key_indent = len(lines[ks[0]]) - len(lines[ks[0]].lstrip())
    out = []
    for l in lines[ks[0] + 1:]:
        if l.strip() and (len(l) - len(l.lstrip())) <= key_indent:
            break
        out.append(l.strip())
    while out and not out[-1]:
        out.pop()
    return out


def project_env_lines(block):
    return [l.strip() for l in (block or "").splitlines() if l.strip().startswith("PROJECT:")]


def step_is_valid(text):
    b = step_block(text)
    return (b is not None and run_script(b) == EXPECTED_RUN
            and project_env_lines(b) == [EXPECTED_PROJECT_ENV])


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


    def test_run_script_is_exact(self):
        self.assertEqual(run_script(self.block), EXPECTED_RUN,
                         "mutation step run script changed; update EXPECTED_RUN only together with the step")

    def test_project_env_is_exact(self):
        self.assertEqual(project_env_lines(self.block), [EXPECTED_PROJECT_ENV])

    def test_known_disablings_are_rejected(self):
        call = "python3 " + CHECKER
        self.assertIn(call, self.text)
        self.assertTrue(step_is_valid(self.text), "real lean.yml must pass the exact-step check")
        edits = {
            "commented_out_call": self.text.replace(call, "# " + call),
            "or_true": self.text.replace(call, call + " || true"),
            "call_in_else_branch": self.text.replace(
                call + "\n", "echo skipped\n", 1).replace(
                'echo "no mutation check for $PROJECT"', call, 1),
            "project_constant_with_comment": self.text.replace(
                EXPECTED_PROJECT_ENV, "PROJECT: AIEFGateCoreX  # ${{ matrix.project }}"),
            "commented_out_filter": self.text.replace(
                'if [ "$PROJECT" = "AIEFGateCore" ]; then', 'if true; then  # [ "$PROJECT" = "AIEFGateCore" ]'),
            "extra_exit_0": self.text.replace(call, "exit 0\n            " + call),
        }
        for name, t in edits.items():
            with self.subTest(edit=name):
                self.assertNotEqual(t, self.text, name + " edit did not apply")
                self.assertFalse(step_is_valid(t), name + " was not rejected")


if __name__ == "__main__":
    unittest.main()
