"""Red-team negative controls: the claims lint (tools/ci/lint_claims.py) and the hygiene scan
(tools/ci/hygiene_scan.py). Known-false inputs are built in temp folders only.
Tests marked GAP are expected failures: the checker accepts the false input today."""
import csv
import io
import json
import os
import shutil
import subprocess
import unittest
import zipfile

from rtcommon import PY, REPO, TempDirMixin, farm, gap, materialize, run

LINT = os.path.join(REPO, "tools/ci/lint_claims.py")
SCAN = os.path.join(REPO, "tools/ci/hygiene_scan.py")

# Runs lint_claims.main() with extra (synthetic) KNOWN_MISSING_ARTIFACTS entries added to the live
# ones, so the allow-list tests do not depend on the live entry. No CLI flag weakens the real check.
LINT_DRIVER = r"""
import json, sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import lint_claims as l
l.KNOWN_MISSING_ARTIFACTS = {**l.KNOWN_MISSING_ARTIFACTS, **{(c, e): r for c, e, r in json.loads(sys.argv[2])}}
sys.exit(l.main(sys.argv[3:]))
"""


def tree_state():
    """`git status` of the real checkout (ignored files included, byte-code excluded)."""
    out = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--ignored", "-z"],
                         capture_output=True, check=True).stdout.decode("utf-8", "replace")
    return sorted(x for x in out.split("\0") if x and "__pycache__" not in x)


class ClaimsLint(TempDirMixin, unittest.TestCase):
    # The mirror's directories are symlinks into the real checkout: fail if any test wrote there.
    @classmethod
    def setUpClass(cls):
        cls._tree_before = tree_state()

    @classmethod
    def tearDownClass(cls):
        after = tree_state()
        if after != cls._tree_before:
            raise AssertionError(f"red-team tests changed the real checkout: before={cls._tree_before} after={after}")

    def setUp(self):
        super().setUp()
        # Symlink mirror of the tree (cited artifacts must resolve); the three files the tests edit
        # are replaced by real temp copies, so the repo files are never written.
        self.root = farm(os.path.join(self.tmp, "repo"))
        for rel in ("registry/README.md", "registry/claims.csv", "tools/ci/claim_statuses.txt"):
            p = materialize(self.root, rel)
            os.unlink(p)
            shutil.copy(os.path.join(REPO, rel), p)
        with open(os.path.join(self.root, "registry/claims.csv"), newline="") as f:
            r = csv.DictReader(f)
            self.cols, self.rows = r.fieldnames, list(r)

    def write(self, rows=None):
        with open(os.path.join(self.root, "registry/claims.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=self.cols, lineterminator="\n")
            w.writeheader()
            w.writerows(self.rows if rows is None else rows)

    def lint(self, *extra):
        return run([PY, LINT, "--repo", self.root, *extra])

    def lint_known(self, known):
        return run([PY, "-c", LINT_DRIVER, os.path.dirname(LINT), json.dumps(known), "--repo", self.root])

    def fake_row(self, **kw):
        row = dict(self.rows[0])
        row.update(claim_id="RT-FAKE-01", **kw)
        return row

    def test_00_control_copy_passes(self):
        rc, out = self.lint()
        self.assertEqual(rc, 0, out[-2000:])

    def test_status_outside_vocabulary(self):
        self.rows[0]["audited_status"] = "Proved"
        self.write()
        self.assertRejected(*self.lint())

    def test_status_with_trailing_space(self):
        self.rows[0]["artifact_status"] = self.rows[0]["artifact_status"] + " "
        self.write()
        self.assertRejected(*self.lint())

    def test_status_wrong_case(self):
        self.rows[0]["audited_status"] = self.rows[0]["audited_status"].upper()
        self.write()
        self.assertRejected(*self.lint())

    def test_duplicate_claim_id(self):
        self.rows.append(dict(self.rows[0]))
        self.write()
        self.assertRejected(*self.lint())

    def test_empty_claim_id(self):
        self.rows[0]["claim_id"] = ""
        self.write()
        self.assertRejected(*self.lint())

    # Formerly GAP G3 (fixed on fix/lint-claims-artifacts).
    def test_row_citing_nonexistent_artifact(self):
        self.rows.append(self.fake_row(supporting_artifacts="runs/000000000000;results/no_such_file.npz"))
        self.write()
        self.assertRejected(*self.lint(), "RT-FAKE-01: cited artifact does not exist: 'runs/000000000000'",
                            "RT-FAKE-01: cited artifact does not exist: 'results/no_such_file.npz'")

    # Formerly GAP G4 (fixed on fix/lint-claims-artifacts). README.md exists and is even registered as
    # 'Formalized theorem' in registry/artifacts.csv, but it is not a Lean proof.
    def test_false_claim_marked_proved(self):
        self.rows.append(self.fake_row(
            statement="The settle threshold is R* = 0.40, proved in Lean.",   # false: R* = 0.4543
            artifact_status="Supported", audited_status="Supported",
            evidence_scope="Formal proof", supporting_artifacts="lean/AIEFProofs/README.md"))
        self.write()
        self.assertRejected(*self.lint(), "RT-FAKE-01: claims a formal/Lean proof (evidence_scope 'Formal proof') "
                                          "but cites no existing .lean file")

    def test_proved_in_lean_statement_needs_lean_file(self):
        self.rows.append(self.fake_row(statement="R* = 0.40, proved in Lean."))  # scope stays experimental
        self.write()
        self.assertRejected(*self.lint(), "RT-FAKE-01: claims a formal/Lean proof")

    def test_control_formal_row_citing_real_lean_file_passes(self):
        self.rows.append(self.fake_row(evidence_scope="Formalized theorem",
                                       supporting_artifacts="lean/AIEFProofs/AIEFProofs/ControllerFiber.lean"))
        self.write()
        rc, out = self.lint()
        self.assertEqual(rc, 0, out[-2000:])

    # Round-2 follow-ups from Auditor Seat 002's audit of fix/lint-claims-artifacts.
    def test_machine_checked_wording_needs_lean_file(self):
        self.rows.append(self.fake_row(statement="Machine-checked in Lean 4 without sorry: R* = 0.40.",
                                       evidence_scope="Conditional theorem"))
        self.write()
        self.assertRejected(*self.lint(), "RT-FAKE-01: claims a formal/Lean proof")

    def test_lean4_verifies_wording_needs_lean_file(self):
        self.rows.append(self.fake_row(statement="Lean 4 verifies that R* = 0.40.",
                                       evidence_scope="Conditional theorem"))
        self.write()
        self.assertRejected(*self.lint(), "RT-FAKE-01: claims a formal/Lean proof")

    def test_scope_outside_vocabulary(self):
        self.rows.append(self.fake_row(evidence_scope="Machine-checked theorem"))
        self.write()
        self.assertRejected(*self.lint(), "RT-FAKE-01: evidence_scope 'Machine-checked theorem' is not one of the 6 values")

    def test_informal_scope_is_a_vocabulary_error_not_a_proof_claim(self):
        self.rows.append(self.fake_row(evidence_scope="Informal argument"))
        self.write()
        rc, out = self.lint()
        self.assertRejected(rc, out, "evidence_scope 'Informal argument' is not one of the 6 values")
        self.assertNotIn("claims a formal/Lean proof", out)

    def test_scope_table_missing(self):
        p = os.path.join(self.root, "registry/README.md")     # real temp copy (setUp)
        with open(p) as f:
            txt = f.read()
        with open(p, "w") as f:
            f.write(txt.replace("`evidence_scope` (Epistemic Strength)", "Epistemic Strength"))
        self.assertRejected(*self.lint(), "no '### Axis 2 ... `evidence_scope`' table found")

    def test_missing_path_after_existing_folder(self):
        self.rows.append(self.fake_row(supporting_artifacts="lean/AIEFProofs missing_file.lean"))
        self.write()
        self.assertRejected(*self.lint(), "cited artifact does not exist: 'lean/AIEFProofs missing_file.lean'")

    def test_missing_path_after_existing_file(self):
        self.rows.append(self.fake_row(supporting_artifacts="registry/claims.csv nonexistent/file.md"))
        self.write()
        self.assertRejected(*self.lint(), "cited artifact does not exist: 'registry/claims.csv nonexistent/file.md'")

    def test_control_locator_and_parenthesised_prose_pass(self):
        self.rows.append(self.fake_row(supporting_artifacts="registry/README.md \u00a72 (axis/scope notes);"
                                                            "registry/claims.csv:2-5"))
        self.write()
        rc, out = self.lint()
        self.assertEqual(rc, 0, out[-2000:])

    @gap("lint_claims.py: a formal row citing an existing .lean file that does not contain the claimed theorem passes "
         "(only the file's existence is checked; content is out of scope)")
    def test_GAP_lean_file_content_not_checked(self):
        self.rows.append(self.fake_row(
            statement="Theorem settle_threshold: R* = 0.40 (machine-checked in Lean 4).",
            evidence_scope="Formalized theorem", supporting_artifacts="lean/AIEFProofs/AIEFProofs/Basic.lean"))
        self.write()
        self.assertRejected(*self.lint())

    def test_control_synthetic_known_missing_entry_passes(self):
        self.rows.append(self.fake_row(supporting_artifacts="results/rt_ghost.log"))
        self.write()
        rc, out = self.lint_known([["RT-FAKE-01", "results/rt_ghost.log", "synthetic"]])
        self.assertEqual(rc, 0, out[-2000:])
        self.assertIn("'results/rt_ghost.log' is missing (known: synthetic)", out)

    def test_known_missing_entry_that_now_exists(self):
        self.rows.append(self.fake_row(supporting_artifacts="registry/README.md"))
        self.write()
        self.assertRejected(*self.lint_known([["RT-FAKE-01", "registry/README.md", "synthetic"]]),
                            "RT-FAKE-01: 'registry/README.md' is listed in KNOWN_MISSING_ARTIFACTS but now exists")

    def test_known_missing_entry_no_longer_cited(self):
        self.assertRejected(*self.lint_known([["RT-FAKE-01", "results/rt_ghost.log", "synthetic"]]),
                            "stale KNOWN_MISSING_ARTIFACTS entry: RT-FAKE-01 no longer cites 'results/rt_ghost.log'")

    # A deleted column must not switch the artifact / scope / formal-proof checks off (same class as G6b).
    def drop_column(self, col):
        self.cols = [c for c in self.cols if c != col]
        self.write([{k: v for k, v in r.items() if k != col} for r in self.rows])
        rc, out = self.lint()
        self.assertNotIn("Traceback", out)
        self.assertEqual([ln for ln in out.splitlines() if ln.startswith("ERROR")],
                         [ln for ln in out.splitlines() if ln.startswith(f"ERROR   registry/claims.csv:1: column '{col}'")],
                         out[-2000:])   # exactly the one header ERROR, no follow-on errors
        return rc, out

    def test_evidence_scope_column_deleted(self):
        rc, out = self.drop_column("evidence_scope")
        self.assertRejected(rc, out, "ERROR   registry/claims.csv:1: column 'evidence_scope' missing from the header; "
                                     "evidence_scope values and formal-scope rows were NOT checked")
        self.assertEqual(rc, 1, out[-2000:])

    def test_supporting_artifacts_column_deleted(self):
        rc, out = self.drop_column("supporting_artifacts")
        self.assertRejected(rc, out, "ERROR   registry/claims.csv:1: column 'supporting_artifacts' missing from the "
                                     "header; cited artifacts and KNOWN_MISSING_ARTIFACTS entries were NOT checked")
        self.assertEqual(rc, 1, out[-2000:])

    def test_statement_column_deleted(self):
        rc, out = self.drop_column("statement")
        self.assertRejected(rc, out, "ERROR   registry/claims.csv:1: column 'statement' missing from the header; "
                                     "its Lean-proof wording was NOT checked")
        self.assertEqual(rc, 1, out[-2000:])

    @gap("lint_claims.py: registry/claims.csv deleted -> NOTICE and exit 0")
    def test_GAP_claims_file_missing(self):
        os.unlink(os.path.join(self.root, "registry/claims.csv"))
        self.assertRejected(*self.lint())

    @gap("lint_claims.py: vocabulary block removed -> warning, value checks skipped, exit 0 (CI runs without --strict)")
    def test_GAP_vocabulary_missing_skips_checks(self):
        p = os.path.join(self.root, "registry/README.md")
        with open(p) as f:
            txt = f.read()
        with open(p, "w") as f:
            f.write(txt.replace("## Status vocabulary", "## Status words"))
        self.rows[0]["audited_status"] = "Proved"          # would be an error with a vocabulary
        self.write()
        self.assertRejected(*self.lint())

    def test_vocabulary_missing_is_caught_with_strict(self):
        p = os.path.join(self.root, "registry/README.md")
        with open(p) as f:
            txt = f.read()
        with open(p, "w") as f:
            f.write(txt.replace("## Status vocabulary", "## Status words"))
        self.assertRejected(*self.lint("--strict"))


GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}

# Fake credentials, assembled at run time so this file never matches the scanner itself.
FAKE_GH = "gh" + "p_" + "A1b2C3d4" * 5
FAKE_KEY = "-----" + "BEGIN RSA PRIVATE KEY-----\nMIIBOgIBAAJBAK\n-----" + "END RSA PRIVATE KEY-----\n"
FAKE_AWS = "AK" + "IA" + "ABCDEFGHIJKLMNOP"


@unittest.skipUnless(shutil.which("git"), "git missing")
class HygieneScan(TempDirMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.root = os.path.join(self.tmp, "repo")
        os.makedirs(os.path.join(self.root, "tools/ci"))
        shutil.copy(os.path.join(REPO, "tools/ci/hygiene_allow.txt"), os.path.join(self.root, "tools/ci"))
        self.put("README.md", b"fixture\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "base")

    def git(self, *a):
        subprocess.run(["git", "-C", self.root, *a], check=True, capture_output=True,
                       env=dict(os.environ, **GIT_ENV))

    def put(self, rel, data):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    def commit(self, **files):
        for rel, data in files.items():
            self.put(rel.replace("__", "/"), data)
        self.git("add", "-A")
        self.git("commit", "-qm", "change")

    def scan(self, base=True):
        return run([PY, SCAN, "--repo", self.root] + (["--base", "HEAD~1"] if base else []))

    def test_00_control_clean_change_passes(self):
        self.commit(**{"notes.md": b"plain text\n"})
        rc, out = self.scan()
        self.assertEqual(rc, 0, out)

    def test_env_file(self):
        self.commit(**{".env": b"X=1\n"})
        self.assertRejected(*self.scan(), "SECRET_FILE")

    def test_ssh_private_key_file_name(self):
        self.commit(**{"id_rsa": b"x\n"})
        self.assertRejected(*self.scan(), "SECRET_FILE")

    def test_private_key_block_in_text(self):
        self.commit(**{"docs__key.txt": FAKE_KEY.encode()})
        self.assertRejected(*self.scan(), "SECRET_PATTERN")

    def test_github_token_in_python(self):
        self.commit(**{"tool.py": f'TOKEN = "{FAKE_GH}"\n'.encode()})
        self.assertRejected(*self.scan(), "SECRET_PATTERN")

    def test_aws_key_in_full_scan(self):
        self.commit(**{"cfg.ini": f"id={FAKE_AWS}\n".encode()})
        self.assertRejected(*self.scan(base=False), "SECRET_PATTERN")

    def test_new_binary_outside_allowed_folders(self):
        self.commit(**{"results__fake_results.npz": b"PK\x03\x04fake"})
        self.assertRejected(*self.scan(), "NEW_BINARY")

    def test_binary_disguised_as_txt(self):
        self.commit(**{"results__table.txt": b"abc\x00\x01\x02def"})
        self.assertRejected(*self.scan(), "NEW_BINARY")

    @gap("hygiene_scan.py: full scan (push to main) only WARNS on a binary outside allowed folders")
    def test_GAP_full_scan_binary_outside_is_warning_only(self):
        self.commit(**{"results__fake_results.npz": b"PK\x03\x04fake"})
        self.assertRejected(*self.scan(base=False))

    @gap("hygiene_scan.py: binaries are never content-scanned, so a token inside an allowed-folder zip/npz passes")
    def test_GAP_token_inside_binary_in_allowed_folder(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
            z.writestr("config.txt", f"token={FAKE_GH}\n")
        self.commit(**{"runs__rt0000000000__bundle.zip": buf.getvalue()})
        self.assertRejected(*self.scan())

    @gap("hygiene_scan.py: text files over --max-scan-mb (10 MiB) are not content-scanned")
    def test_GAP_token_in_text_file_over_10_mib(self):
        self.commit(**{"big_log.txt": (b"x" * 1023 + b"\n") * (11 * 1024) + f"t={FAKE_GH}\n".encode()})
        self.assertRejected(*self.scan())


if __name__ == "__main__":
    unittest.main()
