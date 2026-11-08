"""Self-tests for tools/ci/check_manifest.py (stdlib unittest; synthetic fixtures in temp folders).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v

Assertions are on exact output lines (each expected line must be a whole line of the output) and on the
exact final '== result: ...' line, not on substrings.
"""
import contextlib
import hashlib
import io
import json
import os
import sys
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_manifest  # noqa: E402

VERIFIER = "AI Agent Audits/evidence/verify_manifest.py"
MANIFEST = "AI Agent Audits/evidence/audit_manifest.json"
KEY = "evidence/verify_manifest.py"
# A stand-in verifier that prints the same summary the real one prints for the fixture manifest
# (2 published files: REPORT.md + itself; 1 input) and a final OK.
GOOD = ('import sys\n'
        'print("checked 2 published files" + (" and 1 inputs" if "--inputs" in sys.argv else ""))\n'
        'print("OK")\n')
PASS = "== result: 1 verifier(s) run, 0 failed -> PASS"
FAIL_RUN = "== result: 1 verifier(s) run, 1 failed -> FAIL"
FAIL_NOT_RUN = "== result: 0 verifier(s) run, 1 failed -> FAIL"
NOT_RUN = f"ERROR   {VERIFIER} was NOT run, so the manifest hashes were NOT checked"


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check_manifest.main(argv)
    return rc, buf.getvalue()


def sha(b):
    return hashlib.sha256(b).hexdigest()


class CheckManifestTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.root = self.d.name
        self.old_gha = os.environ.pop("GITHUB_ACTIONS", None)

    def tearDown(self):
        if self.old_gha is not None:
            os.environ["GITHUB_ACTIONS"] = self.old_gha
        self.d.cleanup()

    def assertLines(self, out, *lines):
        got = out.splitlines()
        for ln in lines:
            self.assertIn(ln, got, out)

    def verifier(self, body, pinned=None):
        """Write the verifier `body` and a minimal non-empty manifest (G1) that pins `pinned` (default: body)."""
        p = os.path.join(self.root, VERIFIER)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(body)
        with open(os.path.join(self.root, "AI Agent Audits", "REPORT.md"), "w") as f:
            f.write("report\n")
        pin = (body if pinned is None else pinned).encode()
        m = {"files_sha256": {"REPORT.md": {"bytes": 7, "sha256": sha(b"report\n")},
                              KEY: {"bytes": len(pin), "sha256": sha(pin)}},
             "inputs_sha256": {"x.py": "0"}}
        with open(os.path.join(self.root, MANIFEST), "w") as f:
            json.dump(m, f)
        return p

    def check(self, *extra):
        return run(["--repo", self.root, *extra])

    def test_missing_verifier_fails_closed(self):
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} not found; manifest verifier missing (deleted or moved?), "
                              "so the manifest hashes were NOT checked", FAIL_NOT_RUN)

    def test_passing_verifier_passes(self):
        self.verifier(GOOD)
        rc, out = self.check()
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines()[-3:], ["checked 2 published files and 1 inputs", "OK", PASS])

    def test_failing_verifier_fails(self):
        self.verifier("import sys\nprint('checked 2 published files and 1 inputs')\nprint('OK')\nsys.exit(3)\n")
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} exited 3", FAIL_RUN)

    def test_no_inputs_flag_drops_inputs_arg(self):
        self.verifier(GOOD.replace('import sys\n', 'import sys\nif "--inputs" in sys.argv: sys.exit(4)\n'))
        rc, out = self.check("--no-inputs")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines()[-3:], ["checked 2 published files", "OK", PASS])
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} exited 4", FAIL_RUN)

    def test_bad_repo_is_usage_error(self):
        rc, out = run(["--repo", os.path.join(self.root, "nope")])
        self.assertEqual(rc, 2)
        self.assertEqual(out.splitlines(), [f"ERROR   --repo {os.path.join(self.root, 'nope')} is not a directory"])

    # --- G1: coverage rule (a PASSED manifest must cover data). Each test runs a correctly pinned stub that
    # prints the exact success line + OK for its manifest, so ONLY the coverage rule can make it fail. -------
    def _coverage_fixture(self, files, inputs, success):
        body = f"print({success!r})\nprint('OK')\n"
        p = os.path.join(self.root, VERIFIER)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(body)
        fs = dict(files)
        fs[KEY] = {"bytes": len(body.encode()), "sha256": sha(body.encode())}
        with open(os.path.join(self.root, MANIFEST), "w") as f:
            json.dump({"files_sha256": fs, "inputs_sha256": inputs}, f)

    def test_manifest_listing_only_the_verifier_fails(self):
        self._coverage_fixture({}, {"x.py": "0"}, "checked 1 published files and 1 inputs")
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "checked 1 published files and 1 inputs", "OK",
                         f"ERROR   {MANIFEST}: manifest lists no data files beyond the verifier itself "
                         "(1 entry in files_sha256); refusing to PASS an empty manifest", FAIL_RUN)

    def test_manifest_listing_only_verifier_and_itself_fails(self):
        self._coverage_fixture({"evidence/audit_manifest.json": {"bytes": 0, "sha256": "0" * 64}},
                               {"x.py": "0"}, "checked 2 published files and 1 inputs")
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {MANIFEST}: manifest lists no data files beyond the verifier itself "
                              "(2 entries in files_sha256); refusing to PASS an empty manifest", FAIL_RUN)

    def test_empty_inputs_in_inputs_mode_fails_but_no_inputs_passes(self):
        os.makedirs(os.path.join(self.root, "AI Agent Audits"), exist_ok=True)
        with open(os.path.join(self.root, "AI Agent Audits", "REPORT.md"), "w") as f:
            f.write("report\n")
        self._coverage_fixture({"REPORT.md": {"bytes": 7, "sha256": sha(b"report\n")}}, {},
                               "checked 2 published files")
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {MANIFEST}: inputs_sha256 is empty, so the --inputs check would verify nothing",
                         FAIL_RUN)
        rc, out = self.check("--no-inputs")                 # control: the same tree passes without --inputs
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines()[-3:], ["checked 2 published files", "OK", PASS])

    def test_listed_file_missing_fails(self):
        self._coverage_fixture({"REPORT.md": {"bytes": 7, "sha256": sha(b"report\n")}}, {"x.py": "0"},
                               "checked 2 published files and 1 inputs")
        rc, out = self.check()                              # REPORT.md was never written
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {MANIFEST}: listed file does not exist: REPORT.md", FAIL_RUN)

    # --- G2b: the verifier itself is authenticated before it is run, and its success line is required ----------
    def _hash_mismatch(self, body):
        self.verifier(body, pinned=GOOD)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER}: sha256 {sha(body.encode())} does not match "
                              f"{MANIFEST} files_sha256['{KEY}'] {sha(GOOD.encode())}; refusing to run an unverified verifier",
                         NOT_RUN, FAIL_NOT_RUN)
        self.assertNotIn("$ ", out)                       # the stub was never executed

    def test_zero_byte_verifier_fails(self):
        self._hash_mismatch("")

    def test_comment_only_verifier_fails(self):
        self._hash_mismatch("# verify_manifest.py\n")

    def test_exit0_stub_verifier_fails(self):
        self._hash_mismatch("import sys\nsys.exit(0)\n")

    def test_verifier_without_manifest_entry_fails(self):
        self.verifier(GOOD)
        mp = os.path.join(self.root, MANIFEST)
        with open(mp) as f:
            m = json.load(f)
        del m["files_sha256"][KEY]
        with open(mp, "w") as f:
            json.dump(m, f)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER}: {MANIFEST} has no files_sha256 entry '{KEY}' with a sha256, "
                              "so the verifier cannot be authenticated", NOT_RUN, FAIL_NOT_RUN)

    def test_unreadable_manifest_fails_before_running(self):
        self.verifier(GOOD)
        with open(os.path.join(self.root, MANIFEST), "w") as f:
            f.write("[]")
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {MANIFEST}: files_sha256 is missing or not an object", NOT_RUN, FAIL_NOT_RUN)

    def test_symlink_outside_repo_fails(self):
        p = self.verifier(GOOD)
        outside = tempfile.TemporaryDirectory(); self.addCleanup(outside.cleanup)
        stub = os.path.join(outside.name, "stub.py")
        with open(stub, "w") as f:
            f.write(GOOD)                               # same bytes, so only the location is wrong
        os.unlink(p); os.symlink(stub, p)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} resolves outside the repository (to {os.path.realpath(stub)}); "
                              "refusing to run it", NOT_RUN, FAIL_NOT_RUN)

    def test_symlink_inside_repo_fails(self):
        p = self.verifier(GOOD)
        real = os.path.join(self.root, "tools", "verify_copy.py")
        os.makedirs(os.path.dirname(real))
        os.replace(p, real); os.symlink(real, p)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} is a symlink (to tools/verify_copy.py); "
                              "the verifier must be a regular file at its listed path", NOT_RUN, FAIL_NOT_RUN)

    def test_dangling_symlink_fails(self):
        p = self.verifier(GOOD)
        os.unlink(p); os.symlink(os.path.join(self.root, "gone.py"), p)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} is a symlink (to gone.py); "
                              "the verifier must be a regular file at its listed path", NOT_RUN, FAIL_NOT_RUN)

    def test_directory_in_place_of_verifier_fails(self):
        p = self.verifier(GOOD)
        os.unlink(p); os.mkdir(p)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} is not a regular file; refusing to run it", NOT_RUN, FAIL_NOT_RUN)

    def _no_success_line(self, body, mode=()):
        self.verifier(body)                                # correctly pinned, so it IS run
        rc, out = self.check(*mode)
        self.assertEqual(rc, 1, out)
        want = "checked 2 published files" + ("" if mode else " and 1 inputs")
        self.assertLines(out, f"ERROR   {VERIFIER} exited 0 but did not print its success line '{want}' followed by 'OK'; "
                              "the manifest hashes are NOT confirmed", FAIL_RUN)

    def test_pinned_verifier_silent_exit0_fails(self):
        self._no_success_line("import sys\nsys.exit(0)\n")

    def test_pinned_verifier_printing_failed_exit0_fails(self):
        self._no_success_line("print('checked 2 published files and 1 inputs')\nprint('FAILED: 1 problem(s)')\n")

    def test_pinned_verifier_wrong_count_fails(self):
        self._no_success_line("print('checked 1 published files and 1 inputs')\nprint('OK')\n")

    def test_pinned_verifier_inputs_line_in_no_inputs_mode_fails(self):
        self._no_success_line("print('checked 2 published files and 1 inputs')\nprint('OK')\n", ("--no-inputs",))

    def test_github_annotation(self):
        self.verifier("", pinned=GOOD)
        os.environ["GITHUB_ACTIONS"] = "true"
        try:
            rc, out = self.check()
        finally:
            del os.environ["GITHUB_ACTIONS"]
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"::error file={VERIFIER}::{VERIFIER}: sha256 {sha(b'')} does not match "
                              f"{MANIFEST} files_sha256['{KEY}'] {sha(GOOD.encode())}; refusing to run an unverified verifier")


    # --- Researcher 001 audit of 14072c3: F1 shadow modules, F3 output, F4 unreadable, duplicate keys, F5, F6 ----
    # A small but real verifier: it finds its manifest from its own __file__ (like verify_manifest.py), checks the
    # published files' size + sha256, and imports the same modules (hashlib, json, glob, pathlib).
    REAL = ('import hashlib, json, sys, glob, os\n'
            'from pathlib import Path\n'
            'E = Path(__file__).resolve().parent; P = E.parent\n'
            'M = json.load(open(E / "audit_manifest.json"))\n'
            'bad = []\n'
            'for rel, v in M["files_sha256"].items():\n'
            '    b = open(P / rel, "rb").read()\n'
            '    if len(b) != v["bytes"] or hashlib.sha256(b).hexdigest() != v["sha256"]: bad.append("SHA256   " + rel)\n'
            'n = len(M["inputs_sha256"]) if "--inputs" in sys.argv else 0\n'
            'print(f"checked {len(M[\'files_sha256\'])} published files" + (f" and {n} inputs" if n else ""))\n'
            'for x in bad: print(x)\n'
            'print("OK" if not bad else f"FAILED: {len(bad)} problem(s)")\n'
            'sys.exit(1 if bad else 0)\n')

    def add_listed(self, rel_in_audits, body):
        """Write AI Agent Audits/<rel_in_audits> and list it (correct bytes + sha256) in the manifest."""
        p = os.path.join(self.root, "AI Agent Audits", rel_in_audits)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(body)
        mp = os.path.join(self.root, MANIFEST)
        with open(mp) as f:
            m = json.load(f)
        m["files_sha256"][rel_in_audits] = {"bytes": len(body.encode()), "sha256": sha(body.encode())}
        with open(mp, "w") as f:
            json.dump(m, f)
        return len(m["files_sha256"])

    def tamper_report(self):
        with open(os.path.join(self.root, "AI Agent Audits", "REPORT.md"), "w") as f:
            f.write("REPORT\n")                         # same size, different sha256

    def test_shadow_module_beside_verifier_cannot_hijack_it(self):
        """F1 (HIGH): a hashlib.py / json.py / glob.py / pathlib.py beside the verifier shadowed the stdlib
        (script folder = sys.path[0]); printing the success line + OK at import time made a tampered tree PASS.
        Here the shadow is even listed in the manifest, so only isolated mode (-I) stops it."""
        for mod in ("hashlib", "json", "glob", "pathlib"):
            with self.subTest(module=mod):
                for old in ("hashlib", "json", "glob", "pathlib"):     # previous subtest's shadow
                    q = os.path.join(self.root, "AI Agent Audits/evidence", f"{old}.py")
                    if os.path.exists(q):
                        os.unlink(q)
                self.verifier(self.REAL)
                rc, out = self.check()
                self.assertEqual(rc, 0, out)                       # control: the real verifier passes
                n = self.add_listed(f"evidence/{mod}.py", "")
                want = f"checked {n} published files and 1 inputs"
                self.add_listed(f"evidence/{mod}.py", f"print({want!r})\nprint('OK')\nraise SystemExit(0)\n")
                self.tamper_report()
                rc, out = self.check()
                self.assertEqual(rc, 1, out)
                self.assertLines(out, "SHA256   REPORT.md", "FAILED: 1 problem(s)", f"ERROR   {VERIFIER} exited 1", FAIL_RUN)

    def test_shadow_module_on_pythonpath_or_in_repo_root_cannot_hijack_it(self):
        """F1: the verifier runs with -I, so neither PYTHONPATH (honoured before the fix) nor the current folder
        (the repo root, which a `python -c` launch without -I would put on sys.path) can supply a fake hashlib."""
        shadow = tempfile.mkdtemp(prefix="cm_shadow_")
        self.addCleanup(shutil.rmtree, shadow, True)
        for where in ("PYTHONPATH", "repo root"):
            with self.subTest(where=where):
                self.verifier(self.REAL)
                self.tamper_report()
                d = shadow if where == "PYTHONPATH" else self.root
                with open(os.path.join(d, "hashlib.py"), "w") as f:
                    f.write("print('checked 2 published files and 1 inputs')\nprint('OK')\nraise SystemExit(0)\n")
                old = os.environ.get("PYTHONPATH")
                if where == "PYTHONPATH":
                    os.environ["PYTHONPATH"] = shadow
                try:
                    rc, out = self.check()
                finally:
                    os.unlink(os.path.join(d, "hashlib.py"))
                    if old is None:
                        os.environ.pop("PYTHONPATH", None)
                    else:
                        os.environ["PYTHONPATH"] = old
                self.assertEqual(rc, 1, out)
                self.assertLines(out, "SHA256   REPORT.md", f"ERROR   {VERIFIER} exited 1", FAIL_RUN)

    def test_unlisted_py_beside_verifier_refused(self):
        """F1: an unlisted .py file next to the verifier is refused before anything runs."""
        for mod in ("hashlib", "json", "glob", "pathlib"):
            with self.subTest(module=mod):
                self.verifier(GOOD)
                p = os.path.join(self.root, "AI Agent Audits/evidence", f"{mod}.py")
                with open(p, "w") as f:
                    f.write("print('checked 2 published files and 1 inputs'); print('OK'); raise SystemExit(0)\n")
                rc, out = self.check()
                os.unlink(p)
                self.assertEqual(rc, 1, out)
                self.assertLines(out, f"ERROR   AI Agent Audits/evidence/{mod}.py: .py file beside the verifier that "
                                      f"{MANIFEST} does not list; refusing to run the verifier next to it", NOT_RUN, FAIL_NOT_RUN)
                self.assertNotIn("$ ", out)

    def test_pycache_beside_verifier_refused(self):
        self.verifier(GOOD)
        os.mkdir(os.path.join(self.root, "AI Agent Audits/evidence/__pycache__"))
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   AI Agent Audits/evidence/__pycache__: bytecode cache folder beside the verifier; "
                              "refusing to run the verifier next to it", NOT_RUN, FAIL_NOT_RUN)

    def test_verifier_swapped_after_hash_runs_hashed_bytes(self):
        """F6: the file is replaced between the hash and the run; the bytes that were hashed are what runs."""
        p = self.verifier(self.REAL)
        self.tamper_report()
        real_run = check_manifest.subprocess.run
        def swap_then_run(*a, **k):
            with open(p, "w") as f:
                f.write(GOOD)                               # a stub that always prints the success line + OK
            return real_run(*a, **k)
        check_manifest.subprocess.run = swap_then_run
        try:
            rc, out = self.check()
        finally:
            check_manifest.subprocess.run = real_run
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "SHA256   REPORT.md", f"ERROR   {VERIFIER} exited 1", FAIL_RUN)

    def _bad_output(self, body, msg):
        self.verifier(body)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER} exited 0 but {msg}; the manifest hashes are NOT confirmed", FAIL_RUN)

    def test_success_line_or_ok_twice_fails(self):
        """F3: the success line and OK must each appear exactly once."""
        w = "checked 2 published files and 1 inputs"
        for body, x, n in ((f"print({w!r})\nprint({w!r})\nprint('OK')\n", w, 2),
                           (f"print('OK')\nprint({w!r})\nprint('OK')\n", "OK", 2)):
            with self.subTest(x=x):
                self._bad_output(body, f"printed '{x}' {n} times (expected exactly once)")

    def test_problem_line_in_output_fails(self):
        """F3: a problem-like line anywhere (stdout or stderr) fails, even before a final success line + OK."""
        w = "checked 2 published files and 1 inputs"
        for prob, stream in (("SHA256   REPORT.md", "stdout"), ("MISSING  REPORT.md", "stdout"),
                             ("UNLISTED evidence/x.py", "stdout"), ("INPUT    x.py", "stdout"),
                             ("SIZE     REPORT.md: 8 != 7", "stdout"), ("FAILED: 1 problem(s)", "stdout"),
                             ("note: 1 problem(s) ignored", "stdout"), ("SHA256   REPORT.md", "stderr")):
            with self.subTest(prob=prob, stream=stream):
                self._bad_output(f"import sys\nprint({prob!r}, file=sys.{stream})\nprint({w!r})\nprint('OK')\n",
                                 f"printed a problem line '{prob}'")

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root can read chmod 000 files")
    def test_unreadable_verifier_fails_with_named_error(self):
        """F4: chmod 000 raised a PermissionError traceback."""
        p = self.verifier(GOOD)
        os.chmod(p, 0)
        try:
            rc, out = self.check()
        finally:
            os.chmod(p, 0o644)
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {VERIFIER}: cannot be read (PermissionError: Permission denied), so the verifier "
                              "cannot be authenticated", NOT_RUN, FAIL_NOT_RUN)
        self.assertNotIn("Traceback", out)

    def test_duplicate_manifest_key_fails(self):
        """A second files_sha256 entry for the verifier, holding the stub's hash, used to win (json last-wins)."""
        stub = "print('checked 2 published files and 1 inputs')\nprint('OK')\n"
        self.verifier(stub, pinned=GOOD)                       # first entry: the genuine pin
        mp = os.path.join(self.root, MANIFEST)
        with open(mp) as f:
            txt = f.read()
        dup = json.dumps({KEY: {"bytes": len(stub), "sha256": sha(stub.encode())}})[1:-1]
        with open(mp, "w") as f:
            f.write(txt.replace('}}, "inputs_sha256"', '}, ' + dup + '}, "inputs_sha256"', 1))   # stub hash LAST
        with open(mp) as f:
            self.assertEqual(f.read().count(f'"{KEY}"'), 2)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   {MANIFEST}: cannot read manifest: duplicate key '{KEY}' in a JSON object",
                         NOT_RUN, FAIL_NOT_RUN)

    def test_symlinked_parent_folder_fails(self):
        """F5: only the final path component was checked; a symlinked evidence/ folder was accepted."""
        self.verifier(GOOD)
        ev = os.path.join(self.root, "AI Agent Audits", "evidence")
        os.rename(ev, ev + "_real"); os.symlink("evidence_real", ev)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   AI Agent Audits/evidence is a symlink (a folder on the verifier's path); "
                              f"refusing to run {VERIFIER}", NOT_RUN, FAIL_NOT_RUN)


    # --- Researcher 001 audit of 92c5d77, B1: the WRAPPER itself must not be shadowable -------------------------
    # CI runs `python tools/ci/check_manifest.py` (no -I), so tools/ci/ was sys.path[0] for the wrapper and a
    # committed tools/ci/hashlib.py (json/subprocess/argparse/re ...) ran inside it and could print a PASS result.
    # These tests run a copy of the real wrapper as a script from <temp repo>/tools/ci/, exactly as CI does.
    B1_MODS = ("hashlib", "json", "subprocess", "argparse", "re")
    B1_FORGE = ("import os, sys\n"
                "print('checked 2 published files and 1 inputs'); print('OK')\n"
                "print('== result: 1 verifier(s) run, 0 failed -> PASS'); sys.stdout.flush(); os._exit(0)\n")

    def run_wrapper_script(self, *extra, env_extra=None):
        """Run <root>/tools/ci/check_manifest.py (a copy of the real wrapper) as a script, cwd = repo root."""
        ci = os.path.join(self.root, "tools", "ci")
        os.makedirs(ci, exist_ok=True)
        shutil.copyfile(check_manifest.__file__, os.path.join(ci, "check_manifest.py"))
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON") and k != "GITHUB_ACTIONS"}
        env.update(env_extra or {})
        p = subprocess.run([sys.executable, os.path.join("tools", "ci", "check_manifest.py"), *extra],
                           cwd=self.root, env=env, capture_output=True, text=True, timeout=120)
        return p.returncode, p.stdout + p.stderr

    def test_wrapper_script_clean_tree_passes_both_modes(self):
        """Control for the B1 tests: the real verifier on an untampered tree passes when the wrapper is run as a
        script (so through the isolated re-exec), in inputs mode and with --no-inputs."""
        self.verifier(self.REAL)
        rc, out = self.run_wrapper_script()
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines()[-3:], ["checked 2 published files and 1 inputs", "OK", PASS])
        rc, out = self.run_wrapper_script("--no-inputs")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines()[-3:], ["checked 2 published files", "OK", PASS])

    def test_shadow_module_beside_wrapper_cannot_hijack_it(self):
        """B1: a stdlib-named module beside the wrapper (tools/ci/<mod>.py) that prints a forged PASS at import
        time must not run: the wrapper re-executes itself with -I -B, so the real verifier reports the tampered
        file and the run FAILs, in both modes."""
        self.verifier(self.REAL)
        self.tamper_report()
        ci = os.path.join(self.root, "tools", "ci")
        os.makedirs(ci, exist_ok=True)
        for mod in self.B1_MODS:
            for mode in ((), ("--no-inputs",)):
                with self.subTest(module=mod, mode=mode):
                    plant = os.path.join(ci, f"{mod}.py")
                    with open(plant, "w") as f:
                        f.write(self.B1_FORGE)
                    try:
                        rc, out = self.run_wrapper_script(*mode)
                    finally:
                        os.unlink(plant)
                        shutil.rmtree(os.path.join(ci, "__pycache__"), ignore_errors=True)
                    self.assertEqual(rc, 1, out)
                    self.assertLines(out, "SHA256   REPORT.md", "FAILED: 1 problem(s)", f"ERROR   {VERIFIER} exited 1",
                                     FAIL_RUN)
                    self.assertNotIn(PASS, out.splitlines())

    def test_shadow_module_on_pythonpath_cannot_hijack_wrapper(self):
        """B1 / N1: a hashlib.py on PYTHONPATH is ignored by the wrapper itself (the re-exec uses -I)."""
        self.verifier(self.REAL)
        self.tamper_report()
        shadow = tempfile.mkdtemp(prefix="cm_wrapper_shadow_")
        self.addCleanup(shutil.rmtree, shadow, True)
        with open(os.path.join(shadow, "hashlib.py"), "w") as f:
            f.write(self.B1_FORGE)
        rc, out = self.run_wrapper_script(env_extra={"PYTHONPATH": shadow})
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "SHA256   REPORT.md", f"ERROR   {VERIFIER} exited 1", FAIL_RUN)
        self.assertNotIn(PASS, out.splitlines())


if __name__ == "__main__":
    unittest.main()
