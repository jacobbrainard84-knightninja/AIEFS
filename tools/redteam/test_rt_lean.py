"""Red-team negative controls: the Lean gate lean/AIEFProofs/check_lean.sh, steps 6 (forbidden
markers) and 7 (axiom audit).

The script itself needs the full Mathlib build, so these tests run the script's OWN embedded
checker code, extracted verbatim from check_lean.sh at test time (nothing is copied into this file):
  * step 6: the Python marker scanner, run on a temp library folder;
  * step 7: the `#aief_axiom_audit` Lean elaborator and the `#print axioms` summary parser, run
    against a tiny core-only temp Lake project named AIEFProofs (no Mathlib), built with the
    repo's lean-toolchain. The audit file adds `import Lean` (in the real project Mathlib brings
    it in). Skipped if `lake` is not installed.
GAP tests are expected failures (the layer accepts the false input)."""
import os
import re
import shutil
import subprocess
import unittest

from rtcommon import PY, REPO, TempDirMixin, gap, run

SCRIPT = os.path.join(REPO, "lean/AIEFProofs/check_lean.sh")
TOOLCHAIN = os.path.join(REPO, "lean/AIEFProofs/lean-toolchain")
ELAN_BIN = os.path.expanduser("~/.elan/bin")
LAKE = shutil.which("lake") or (os.path.join(ELAN_BIN, "lake") if os.path.exists(os.path.join(ELAN_BIN, "lake")) else None)


def heredocs():
    with open(SCRIPT) as f:
        src = f.read()
    blocks = re.findall(r"<<'(PY|LEAN)'[^\n]*\n(.*?)\n\1\n", src, re.S)
    py = [b for tag, b in blocks if tag == "PY"]
    lean = [b for tag, b in blocks if tag == "LEAN"]
    markers = next(b for b in py if "sorryAx" in b and "strip(" in b)
    summary = next(b for b in py if "depends on axioms" in b)
    elab = next(b for b in lean if "#aief_axiom_audit" in b)
    return markers, summary, elab


MARKERS, SUMMARY, ELAB = heredocs()

CLEAN = "theorem rt_ok : 1 + 1 = 2 := rfl\n"
CASES = {
    "sorry": "theorem rt_bad : 1 = 2 := by sorry\n",
    "admit": "theorem rt_bad : 1 = 2 := by admit\n",
    "user_axiom": "axiom rt_ax : 1 = 2\ntheorem rt_bad : 1 = 2 := rt_ax\n",
    "native_decide": "theorem rt_bad : 10 < 20 := by native_decide\n",
}
# A tactic that closes any goal via the elaborator's admitGoal (inserts sorryAx) without ever
# spelling a forbidden word.
HIDDEN_SORRY = ("import Lean\nopen Lean Elab Tactic in\n"
                "elab \"trust_me\" : tactic => do\n"
                "  let g ← getMainGoal\n"
                "  Lean.Elab.admitGoal g\n"
                "theorem rt_bad : 1 = 2 := by trust_me\n")
ATTR_AXIOM = "@[simp] axiom rt_ax : 1 = 2\ntheorem rt_bad : 1 = 2 := rt_ax\n"


class MarkerScan(TempDirMixin, unittest.TestCase):
    """Step 6 of check_lean.sh."""

    def scan(self, body):
        lib = os.path.join(self.tmp, "AIEFProofs")
        os.makedirs(lib, exist_ok=True)
        with open(lib + ".lean", "w") as f:
            f.write("import AIEFProofs.Bad\n")
        with open(os.path.join(lib, "Bad.lean"), "w") as f:
            f.write(body)
        return self._run(lib)

    def _run(self, lib):
        p = subprocess.run([PY, "-", lib], input=MARKERS, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def test_00_control_clean_file_passes(self):
        rc, out = self.scan(CLEAN + "-- a comment that says sorry is fine\n/- admit in a block comment -/\n")
        self.assertEqual(rc, 0, out)

    def test_sorry(self):
        self.assertRejected(*self.scan(CASES["sorry"]), "HIT")

    def test_admit(self):
        self.assertRejected(*self.scan(CASES["admit"]), "HIT")

    def test_user_axiom(self):
        self.assertRejected(*self.scan(CASES["user_axiom"]), "HIT")

    def test_native_decide(self):
        self.assertRejected(*self.scan(CASES["native_decide"]), "HIT")

    @gap("check_lean.sh step 6: a sorry inserted by a custom tactic (Lean.Elab.admitGoal) has no marker word (step 7 catches it)")
    def test_GAP_hidden_sorry_via_admitGoal(self):
        self.assertRejected(*self.scan(HIDDEN_SORRY))

    @gap("check_lean.sh step 6: `@[simp] axiom` is missed by the line-start axiom regex (step 7 catches it)")
    def test_GAP_axiom_with_attribute_prefix(self):
        self.assertRejected(*self.scan(ATTR_AXIOM))


@unittest.skipUnless(LAKE, "lake not installed")
class AxiomAudit(TempDirMixin, unittest.TestCase):
    """Step 7 of check_lean.sh, on a tiny core-only project (one build per test)."""

    def audit(self, body):
        proj = os.path.join(self.tmp, "proj")
        os.makedirs(os.path.join(proj, "AIEFProofs"))
        shutil.copy(TOOLCHAIN, os.path.join(proj, "lean-toolchain"))
        with open(os.path.join(proj, "lakefile.toml"), "w") as f:
            f.write('name = "AIEFProofs"\ndefaultTargets = ["AIEFProofs"]\n\n[[lean_lib]]\nname = "AIEFProofs"\n')
        with open(os.path.join(proj, "AIEFProofs.lean"), "w") as f:
            f.write("import AIEFProofs.Bad\n")
        with open(os.path.join(proj, "AIEFProofs", "Bad.lean"), "w") as f:
            f.write(body)
        env = {"PATH": ELAN_BIN + os.pathsep + os.environ.get("PATH", "")}
        rc, out = run([LAKE, "build"], cwd=proj, env=env, timeout=900)
        self.assertEqual(rc, 0, "fixture build failed:\n" + out[-2000:])
        names = re.findall(r"^\s*theorem\s+(\S+)", body, re.M)
        ax = os.path.join(proj, "audit.lean")
        with open(ax, "w") as f:
            f.write("import AIEFProofs.Bad\nimport Lean\n" + ELAB + "\n" + "".join(f"#print axioms {n}\n" for n in names))
        rc, log = run([LAKE, "env", "lean", ax], cwd=proj, env=env, timeout=900)
        if rc == 0:      # elaborator passed; the script then also runs the #print axioms parser
            logf = os.path.join(proj, "7.log")
            with open(logf, "w") as f:
                f.write(log)
            p = subprocess.run([PY, "-", logf], input=SUMMARY, capture_output=True, text=True)
            rc, log = p.returncode, log + p.stdout + p.stderr
        return rc, log

    def test_00_control_clean_project_passes(self):
        rc, out = self.audit(CLEAN)
        self.assertEqual(rc, 0, out[-2000:])
        self.assertIn("AUDITED", out)

    def test_sorry(self):
        self.assertRejected(*self.audit(CASES["sorry"]), "DISALLOWED")

    def test_user_axiom(self):
        self.assertRejected(*self.audit(CASES["user_axiom"]), "DISALLOWED")

    def test_hidden_sorry_via_admitGoal(self):
        self.assertRejected(*self.audit(HIDDEN_SORRY), "DISALLOWED")

    def test_axiom_with_attribute_prefix(self):
        self.assertRejected(*self.audit(ATTR_AXIOM), "DISALLOWED")

    def test_native_decide(self):
        self.assertRejected(*self.audit(CASES["native_decide"]), "DISALLOWED")


if __name__ == "__main__":
    unittest.main()
