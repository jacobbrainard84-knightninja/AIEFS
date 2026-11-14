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
Since the audit of PR #32 (H1-H3) the step's key list (name, if, env, run; a duplicate `run:` is visible) and its whole
env block are pinned, `AIEF_MUT_ONLY` may not appear anywhere in lean.yml, and the step must sit in the job whose matrix
has the required AIEFGateCore row; since the delta audit of 6ff39ae that job must be `lean` itself, with no job-level
`if:`, `continue-on-error` or `needs:` (a skipped job reports as passed for the required lean checks). lean_mutation_check.py also FAILS any filtered or short run on its own
(partial_run_reason, tested in research/lean_gate/tests/test_mutation_full_run.py).

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


EXPECTED_STEP_KEYS = ["name", "if", "env", "run"]
GATE_ROW = re.compile(r"\{\s*project:\s*AIEFGateCore\s*,[^}]*required:\s*true\s*\}")


def step_keys(block):
    """Top-level keys of the step, in order (duplicates kept, so a second `run:` is visible)."""
    if block is None:
        return None
    lines = block.splitlines()
    indent = len(lines[0]) - len(lines[0].lstrip()) + 2
    keys = [lines[0].strip()[2:].split(":", 1)[0]]
    for l in lines[1:]:
        if l.strip() and not l.strip().startswith("#") and len(l) - len(l.lstrip()) == indent:
            keys.append(l.strip().split(":", 1)[0])
    return keys


def env_block_lines(block):
    """Non-blank lines of the step's `env:` mapping (comments included)."""
    lines = (block or "").splitlines()
    ks = [k for k, l in enumerate(lines) if l.strip() == "env:"]
    if len(ks) != 1:
        return None
    ind = len(lines[ks[0]]) - len(lines[ks[0]].lstrip())
    out = []
    for l in lines[ks[0] + 1:]:
        if l.strip() and len(l) - len(l.lstrip()) <= ind:
            break
        if l.strip():
            out.append(l.strip())
    return out


def job_text_of_step(text):
    """Text of the `jobs:` entry that contains the mutation step, or None."""
    lines = text.splitlines()
    starts = [k for k, l in enumerate(lines) if l.strip().startswith(STEP_NAME)]
    if len(starts) != 1 or "jobs:" not in [l.rstrip() for l in lines]:
        return None
    j0 = [l.rstrip() for l in lines].index("jobs:")
    heads = [k for k in range(j0 + 1, len(lines))
             if re.match(r"^  [A-Za-z0-9_-]+:\s*(#.*)?$", lines[k])]
    before = [k for k in heads if k < starts[0]]
    if not before:
        return None
    a = before[-1]
    after = [k for k in heads if k > a]
    b = after[0] if after else len(lines)
    return "\n".join(lines[a:b])


def job_keys(job):
    """Top-level keys of a job (indent 4), in order."""
    # N1 (R001 on bd4211d): normalise `if :`, `'if':` and `"if":` to `if`.
    return [l.strip().split(":", 1)[0].strip().strip("'\"") for l in (job or "").splitlines()[1:]
            if l.strip() and not l.strip().startswith("#") and len(l) - len(l.lstrip()) == 4]


FORBIDDEN_JOB_KEYS = {"if", "continue-on-error", "needs", "<<"}  # `<<` merge key could inject any of them


def step_is_valid(text):
    b = step_block(text)
    job = job_text_of_step(text)
    # H2b (R001 on 6ff39ae): the step must be in the `lean` job itself, and that job may not be skippable or soft.
    if job is None or job.splitlines()[0].strip() != "lean:" or FORBIDDEN_JOB_KEYS & set(job_keys(job)):
        return False
    return (b is not None and run_script(b) == EXPECTED_RUN
            and project_env_lines(b) == [EXPECTED_PROJECT_ENV]
            and env_block_lines(b) == [EXPECTED_PROJECT_ENV]
            and step_keys(b) == EXPECTED_STEP_KEYS
            and "AIEF_MUT_ONLY" not in text
            and job is not None and GATE_ROW.search(job) is not None)


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
            # Researcher 001 audit of #32, H1-H3
            "mut_only_in_step_env": self.text.replace(
                "          " + EXPECTED_PROJECT_ENV, "          " + EXPECTED_PROJECT_ENV + "\n          AIEF_MUT_ONLY: '^$'", 1),
            "mut_only_in_job_env": self.text.replace(
                "    env:\n", "    env:\n      AIEF_MUT_ONLY: '^$'\n", 1),
            "step_moved_to_job_without_gate_row": self.text.replace(
                "      " + STEP_NAME, "  other:\n    runs-on: ubuntu-latest\n    steps:\n      " + STEP_NAME, 1),
            "duplicate_run_key": self.text.replace(
                "        if: steps.present.outputs.present == 'true'\n        env:\n          " + EXPECTED_PROJECT_ENV,
                "        if: steps.present.outputs.present == 'true'\n        run: echo skipped\n        env:\n          "
                + EXPECTED_PROJECT_ENV, 1),
            # Researcher 001 delta audit of 6ff39ae, H2b and the job-level skip
            "lean_job_if_false": self.text.replace("\n  lean:\n", "\n  lean:\n    if: false\n", 1),
            "lean_job_if_space_colon": self.text.replace("\n  lean:\n", "\n  lean:\n    if : false\n", 1),
            "lean_job_if_single_quoted": self.text.replace("\n  lean:\n", "\n  lean:\n    'if': false\n", 1),
            "lean_job_if_double_quoted": self.text.replace("\n  lean:\n", "\n  lean:\n    \"if\": false\n", 1),
            "lean_job_coe_quoted": self.text.replace("\n  lean:\n", "\n  lean:\n    'continue-on-error': true\n", 1),
            "lean_job_needs_quoted": self.text.replace("\n  lean:\n", "\n  lean:\n    'needs': [x]\n", 1),
            "lean_job_merge_key": self.text.replace("\n  lean:\n", "\n  lean:\n    <<: *skip\n", 1),
            "lean_job_continue_on_error": self.text.replace("\n  lean:\n", "\n  lean:\n    continue-on-error: true\n", 1),
            "step_moved_to_never_running_job_with_spaced_gate_row": self.text.replace(
                "      " + STEP_NAME,
                "  later:\n    needs: [lean]\n    if: failure()\n    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n"
                "        include:\n          - {  project: AIEFGateCore, script: x, axiom_root: x, required: true }\n"
                "    steps:\n      " + STEP_NAME, 1),
        }
        for name, t in edits.items():
            with self.subTest(edit=name):
                self.assertNotEqual(t, self.text, name + " edit did not apply")
                self.assertFalse(step_is_valid(t), name + " was not rejected")


if __name__ == "__main__":
    unittest.main()
