"""Red-team negative controls: the claims lint (tools/ci/lint_claims.py) and the hygiene scan
(tools/ci/hygiene_scan.py). Known-false inputs are built in temp folders only.
Tests marked GAP are expected failures: the checker accepts the false input today."""
import csv
import io
import os
import shutil
import subprocess
import unittest
import zipfile

from rtcommon import PY, REPO, TempDirMixin, gap, run

LINT = os.path.join(REPO, "tools/ci/lint_claims.py")
SCAN = os.path.join(REPO, "tools/ci/hygiene_scan.py")


class ClaimsLint(TempDirMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.root = os.path.join(self.tmp, "repo")
        for rel in ("registry/README.md", "registry/claims.csv", "tools/ci/claim_statuses.txt"):
            os.makedirs(os.path.dirname(os.path.join(self.root, rel)), exist_ok=True)
            shutil.copy(os.path.join(REPO, rel), os.path.join(self.root, rel))
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
        self.assertRejected(*self.lint(), "audited_status 'Proved' is not in the status vocabulary")

    def test_status_with_trailing_space(self):
        self.rows[0]["artifact_status"] = self.rows[0]["artifact_status"] + " "
        self.write()
        self.assertRejected(*self.lint(), "is not in the status vocabulary (has leading/trailing spaces)")

    def test_status_wrong_case(self):
        bad = self.rows[0]["audited_status"].upper()
        self.rows[0]["audited_status"] = bad
        self.write()
        self.assertRejected(*self.lint(), f"audited_status '{bad}' is not in the status vocabulary")

    def test_duplicate_claim_id(self):
        self.rows.append(dict(self.rows[0]))
        self.write()
        self.assertRejected(*self.lint(), f"duplicate claim_id {self.rows[0]['claim_id']}")

    def test_empty_claim_id(self):
        self.rows[0]["claim_id"] = ""
        self.write()
        self.assertRejected(*self.lint(), ": empty claim_id")

    @gap("lint_claims.py: a row citing an artifact that does not exist passes")
    def test_GAP_row_citing_nonexistent_artifact(self):
        self.rows.append(self.fake_row(supporting_artifacts="runs/000000000000;results/no_such_file.npz"))
        self.write()
        self.assertRejected(*self.lint())

    @gap("lint_claims.py: a false claim marked Supported with a formal-proof scope passes")
    def test_GAP_false_claim_marked_proved(self):
        self.rows.append(self.fake_row(
            statement="The settle threshold is R* = 0.40, proved in Lean.",   # false: R* = 0.4543
            artifact_status="Supported", audited_status="Supported",
            evidence_scope="Formal proof", supporting_artifacts="lean/AIEFProofs/README.md"))
        self.write()
        self.assertRejected(*self.lint())

    def test_claims_file_missing(self):
        """Was GAP G5 (NOTICE and exit 0). Fixed on fix/lint-claims-fail-closed."""
        os.unlink(os.path.join(self.root, "registry/claims.csv"))
        rc, out = self.lint()
        self.assertRejected(rc, out, "claims registry missing", "-> FAIL")
        self.assertEqual(rc, 1, out)

    def test_vocabulary_missing_fails_without_strict(self):
        """Was GAP G6 (warning, value checks skipped, exit 0 as CI runs it). Fixed on fix/lint-claims-fail-closed."""
        p = os.path.join(self.root, "registry/README.md")
        with open(p) as f:
            txt = f.read()
        with open(p, "w") as f:
            f.write(txt.replace("## Status vocabulary", "## Status words"))
        self.rows[0]["audited_status"] = "Proved"          # would be an error with a vocabulary
        self.write()
        rc, out = self.lint()
        self.assertRejected(rc, out, "no status vocabulary found", "NOT checked", "-> FAIL")
        self.assertEqual(rc, 1, out)

    def test_vocabulary_missing_is_caught_with_strict(self):
        p = os.path.join(self.root, "registry/README.md")
        with open(p) as f:
            txt = f.read()
        with open(p, "w") as f:
            f.write(txt.replace("## Status vocabulary", "## Status words"))
        self.assertRejected(*self.lint("--strict"), "no status vocabulary found")


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
