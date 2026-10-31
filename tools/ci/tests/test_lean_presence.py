#!/usr/bin/env python3
"""Tests for tools/ci/lean_presence.sh, the presence gate used by .github/workflows/lean.yml.

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v
Runs the real script (the workflow step only calls it) with bash in a temporary directory.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SCRIPT = os.path.join(REPO, "tools", "ci", "lean_presence.sh")
WORKFLOW = os.path.join(REPO, ".github", "workflows", "lean.yml")
PROJ, CHECK = "lean/AIEFProofsKn", "check_lean_kn.sh"


@unittest.skipUnless(shutil.which("bash"), "bash missing")
class LeanPresenceTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = self.d.name
        self.out = os.path.join(self.root, "gh_output")
        self.summary = os.path.join(self.root, "gh_summary")

    def tearDown(self):
        self.d.cleanup()

    def make(self, *files, empty=()):
        os.makedirs(os.path.join(self.root, PROJ), exist_ok=True)
        for f in files:
            with open(os.path.join(self.root, PROJ, f), "w") as fh:
                fh.write("" if f in empty else "x\n")

    def run_gate(self, required, project=PROJ, check=CHECK):
        env = dict(os.environ, GITHUB_OUTPUT=self.out, GITHUB_STEP_SUMMARY=self.summary)
        r = subprocess.run(["bash", SCRIPT, project, check, required], cwd=self.root, env=env,
                           capture_output=True, text=True)
        output = open(self.out).read() if os.path.exists(self.out) else ""
        return r.returncode, output, r.stdout + r.stderr

    def test_dir_missing_optional_skips(self):
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (0, "present=false\n"))
        self.assertIn("::warning::", msg)
        self.assertIn("SKIPPED", open(self.summary).read())

    def test_dir_with_lakefile_toml_and_script_present(self):
        self.make("lakefile.toml", CHECK)
        for req in ("false", "true"):
            os.path.exists(self.out) and os.remove(self.out)
            rc, output, msg = self.run_gate(req)
            self.assertEqual((rc, output), (0, "present=true\n"), req)
            self.assertNotIn("::", msg)

    def test_lakefile_lean_accepted(self):
        self.make("lakefile.lean", CHECK)
        self.assertEqual(self.run_gate("false")[:2], (0, "present=true\n"))

    def test_dir_with_missing_script_errors(self):
        self.make("lakefile.toml", "check_lean_kn_renamed.sh")
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("::error::", msg); self.assertIn(CHECK, msg)

    def test_dir_with_missing_lakefile_errors(self):
        self.make(CHECK, "lakefile.toml.bak")
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("::error::", msg); self.assertIn("lakefile", msg)

    def test_empty_dir_errors(self):
        self.make()
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("::error::", msg)

    def test_required_dir_missing_errors(self):
        rc, output, msg = self.run_gate("true", project="lean/AIEFProofs", check="check_lean.sh")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("::error::", msg); self.assertNotIn("::warning::", msg)

    # (a) only "nothing there" is a skip; anything else at the path must be a real directory
    def test_broken_symlink_at_project_path_errors(self):
        os.makedirs(os.path.join(self.root, "lean"))
        os.symlink("does-not-exist", os.path.join(self.root, PROJ))
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("::error::", msg); self.assertNotIn("::warning::", msg)

    def test_plain_file_at_project_path_errors(self):
        os.makedirs(os.path.join(self.root, "lean"))
        open(os.path.join(self.root, PROJ), "w").close()
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("not a plain directory", msg)

    def test_symlink_to_directory_errors(self):
        os.makedirs(os.path.join(self.root, "lean", "Other"))
        for f in ("lakefile.toml", CHECK):
            with open(os.path.join(self.root, "lean", "Other", f), "w") as fh:
                fh.write("x\n")
        os.symlink("Other", os.path.join(self.root, PROJ))
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("not a plain directory", msg)

    # (b) empty files do not count
    def test_zero_byte_script_errors(self):
        self.make("lakefile.toml", CHECK, empty=(CHECK,))
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("0 bytes", msg)

    def test_empty_lakefile_errors(self):
        self.make("lakefile.toml", CHECK, empty=("lakefile.toml",))
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("non-empty lakefile.toml", msg)

    def test_empty_second_lakefile_errors(self):
        # lake prefers lakefile.lean, so an empty one next to a good lakefile.toml must not pass
        self.make("lakefile.toml", "lakefile.lean", CHECK, empty=("lakefile.lean",))
        rc, output, msg = self.run_gate("false")
        self.assertEqual((rc, output), (1, ""))
        self.assertIn("non-empty lakefile.lean", msg)

    def test_script_is_a_directory_errors(self):
        self.make("lakefile.toml")
        os.makedirs(os.path.join(self.root, PROJ, CHECK))
        self.assertEqual(self.run_gate("false")[:2], (1, ""))

    def test_without_github_env_prints_to_stdout(self):
        self.make("lakefile.toml", CHECK)
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_OUTPUT", "GITHUB_STEP_SUMMARY")}
        r = subprocess.run(["bash", SCRIPT, PROJ, CHECK, "false"], cwd=self.root, env=env,
                           capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "present=true\n", ""))

    def test_bad_arguments(self):
        self.assertEqual(self.run_gate("maybe")[0], 2)

    def test_script_emits_only_present_true_false(self):
        self.assertEqual(emitted_values(), {"true", "false"})


GATE_RUN = 'run: bash tools/ci/lean_presence.sh "$PROJECT_DIR" "$SCRIPT" "$REQUIRED"'
GATE_IF = "steps.present.outputs.present == 'true'"


def emitted_values():
    with open(SCRIPT, encoding="utf-8") as f:
        return set(re.findall(r'emit "present=(\w+)"', f.read()))


def steps_of(text):
    """Split the single job's `steps:` list into step blocks (text), stdlib only."""
    lines = text.split("\n")
    i = next(n for n, l in enumerate(lines) if l.strip() == "steps:")
    blocks, cur = [], None
    for l in lines[i + 1:]:
        if l.startswith("      - "):
            cur = [l]; blocks.append(cur)
        elif cur is not None and (l.startswith("        ") or not l.strip()):
            cur.append(l)
        elif l.strip().startswith("#"):
            continue
        elif l.strip():
            break
    return ["\n".join(b) for b in blocks]


def workflow_problems(text, repo_root=None):
    # repo_root: also require required: true on every row whose lean/<project> directory exists there.
    """Ways lean.yml could bypass the presence gate; [] means none found."""
    problems = []
    if re.search(r"(?m)^\s*continue-on-error\s*:", text):
        problems.append("continue-on-error is used")
    steps = steps_of(text)
    gates = [b for b in steps if re.search(r"(?m)^\s+id:\s*present\s*$", b)]
    if len(gates) != 1:
        return problems + [f"expected exactly one step with id: present, found {len(gates)}"]
    gate = gates[0]
    run_lines = [l.strip() for l in gate.split("\n") if re.match(r"\s*-?\s*run\s*:", l)]
    if run_lines != [GATE_RUN]:
        problems.append(f"gate run line is {run_lines!r}, expected exactly {GATE_RUN!r}")
    if re.search(r"(?m)^\s+(if|shell|working-directory)\s*:", gate):
        problems.append("gate step has if:/shell:/working-directory:")
    env_ok = all(re.search(rf"(?m)^\s+{k}:\s*\$\{{\{{ matrix\.{v} \}}\}}\s*$", gate)
                 for k, v in (("REQUIRED", "required"), ("SCRIPT", "script")))
    if not env_ok:
        problems.append("gate env must map REQUIRED/SCRIPT from matrix.required/matrix.script")
    values = emitted_values()
    for m in re.finditer(r"steps\.(\w+)\.outputs\.(\w+)\s*==\s*'([^']*)'", text):
        if m.group(1, 2) != ("present", "present") or m.group(3) not in values or m.group(3) != "true":
            problems.append(f"condition {m.group(0)!r} does not test an emitted value")
    if re.search(r"steps\.(?!present\.outputs\.present\s*==\s*'true')", text):
        problems.append("a steps.* expression other than the gate test is used")
    after = steps[steps.index(gate) + 1:]
    for b in after:
        ifs = re.findall(r"(?m)^\s+if:\s*(.+?)\s*$", b)
        if len(ifs) != 1 or ifs[0] not in (GATE_IF, "always() && " + GATE_IF):
            problems.append(f"step after the gate is not gated exactly on the gate output: {b.split(chr(10))[0].strip()}")
    if not re.search(r"(?m)^\s+- \{ project: AIEFProofs,.*required: true\s*\}", text):
        problems.append("the base AIEFProofs row must be required: true")
    for proj, req in matrix_rows(text):
        if req != "true" and repo_root is not None and os.path.lexists(os.path.join(repo_root, "lean", proj)):
            problems.append(f"lean/{proj} is on this branch, so its row must be required: true")
    return problems


def matrix_rows(text):
    """(project, required) for every `- { project: X, ..., required: Y }` matrix row."""
    return re.findall(r"(?m)^\s+- \{ project: (\w+),.*required: (\w+)\s*\}", text)


class WorkflowGuardTests(unittest.TestCase):
    def setUp(self):
        with open(WORKFLOW, encoding="utf-8") as f:
            self.wf = f.read()

    def test_real_workflow_has_no_bypass(self):
        self.assertEqual(workflow_problems(self.wf, REPO), [])

    def test_paths_filters_include_the_gate_script(self):
        self.assertEqual(self.wf.count('- "tools/ci/lean_presence.sh"'), 1)   # push (pull_request has no filter)
        self.assertNotIn('pull_request:\n    paths:', self.wf)                 # Lean is a required check on every PR

    def mutated(self, old, new):
        self.assertEqual(self.wf.count(old), 1, old)
        return workflow_problems(self.wf.replace(old, new))

    def test_detects_or_echo_on_gate_line(self):
        self.assertTrue(self.mutated(GATE_RUN, GATE_RUN + " || echo present=false >> \"$GITHUB_OUTPUT\""))

    def test_detects_multiline_gate(self):
        self.assertTrue(self.mutated(GATE_RUN, "run: |\n          " + GATE_RUN[5:] + "\n          true"))

    def test_detects_continue_on_error_on_gate(self):
        self.assertTrue(self.mutated("        id: present\n", "        id: present\n        continue-on-error: true\n"))

    def test_detects_continue_on_error_at_job_level(self):
        self.assertTrue(self.mutated("    timeout-minutes: 60\n", "    timeout-minutes: 60\n    continue-on-error: true\n"))

    def test_detects_condition_on_value_never_emitted(self):
        wf = self.wf.replace(GATE_IF, "steps.present.outputs.present == 'yes'")
        self.assertTrue(workflow_problems(wf))

    def test_detects_condition_on_other_output_name(self):
        wf = self.wf.replace(GATE_IF, "steps.present.outputs.found == 'true'", 1)
        self.assertTrue(workflow_problems(wf))

    def test_detects_ungated_check_removed_if(self):
        old = "        if: steps.present.outputs.present == 'true'\n        working-directory"
        self.assertTrue(self.mutated(old, "        working-directory"))

    def test_detects_base_row_made_optional(self):
        self.assertTrue(self.mutated("axiom_root: AIEFProofs,     required: true",
                                     "axiom_root: AIEFProofs,     required: false"))

    def test_matrix_has_the_three_projects(self):
        self.assertEqual([p for p, _ in matrix_rows(self.wf)], ["AIEFProofs", "AIEFProofsKn", "AIEFFreezeCore"])

    def test_detects_present_project_made_optional(self):
        # A research project whose directory exists (here: a temp repo with lean/AIEFProofsKn) must be
        # required: true; an absent one may stay required: false (the row is skipped with a warning).
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "lean", "AIEFProofsKn"))
            kn_true = re.sub(r"(project: AIEFProofsKn,.*required: )\w+", r"\1true", self.wf)
            kn_false = re.sub(r"(project: AIEFProofsKn,.*required: )\w+", r"\1false", self.wf)
            fz_false = re.sub(r"(project: AIEFFreezeCore,.*required: )\w+", r"\1false", kn_true)
            self.assertEqual(workflow_problems(fz_false, root), [])
            self.assertTrue(workflow_problems(kn_false, root))
            os.makedirs(os.path.join(root, "lean", "AIEFFreezeCore"))
            self.assertTrue(workflow_problems(fz_false, root))


if __name__ == "__main__":
    unittest.main()
