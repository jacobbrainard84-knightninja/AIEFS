"""Red-team negative controls: the claims lint (tools/ci/lint_claims.py) and the hygiene scan
(tools/ci/hygiene_scan.py). Known-false inputs are built in temp folders only.
Tests marked GAP are expected failures: the checker accepts the false input today.

Claims-lint tests assert the exact ERROR line(s) and the exact final '== result: ...' line, exit code 1 and no
traceback. The --strict test uses a warning-only input, so it passes without --strict and fails with it.
G5b/G6b/G6c/G6d (Researcher 001 audit of 37b9026) and BOM / non-UTF-8 / unreadable claims.csv are normal
negative controls: each was accepted (or crashed) at 37b9026 and is rejected after the fix. Likewise F1 (unterminated
quote swallowing an appended row), F2 (header name with trailing space), F6 (NUL byte) and F7 (--columns "") from the
audit of 588d5ee; F5 (indented vocabulary heading) is a GAP."""
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

    def assertLintFails(self, rc, out, *lines, errors=1):
        """Exit 1, no traceback, each given line present as a WHOLE output line, and the exact result line."""
        self.assertRejected(rc, out)
        self.assertEqual(rc, 1, out)
        self.assertNotIn("Traceback", out)
        got = out.splitlines()
        for ln in lines:
            self.assertIn(ln, got, out[-3000:])
        self.assertEqual(got[-1], f"== result: {errors} error(s), 0 warning(s), 0 notice(s) -> FAIL", out[-3000:])

    def edit_text(self, rel, fn, binary=False):
        p = os.path.join(self.root, rel)
        with open(p, "rb" if binary else "r", **({} if binary else {"newline": ""})) as f:
            data = f.read()
        with open(p, "wb" if binary else "w", **({} if binary else {"newline": ""})) as f:
            f.write(fn(data))

    def test_00_control_copy_passes(self):
        rc, out = self.lint()
        self.assertEqual(rc, 0, out[-2000:])
        self.assertEqual(out.splitlines()[-1], "== result: 0 error(s), 0 warning(s), 0 notice(s) -> PASS")

    def test_status_outside_vocabulary(self):
        self.rows[0]["audited_status"] = "Proved"
        self.write()
        cid = self.rows[0]["claim_id"]
        self.assertLintFails(*self.lint(), f"ERROR   registry/claims.csv:2: {cid}: audited_status 'Proved' is not in the status vocabulary")

    def test_status_with_trailing_space(self):
        val = self.rows[0]["artifact_status"] + " "
        self.rows[0]["artifact_status"] = val
        self.write()
        cid = self.rows[0]["claim_id"]
        self.assertLintFails(*self.lint(), f"ERROR   registry/claims.csv:2: {cid}: artifact_status '{val}' is not in the "
                                           "status vocabulary (has leading/trailing spaces)")

    def test_status_wrong_case(self):
        bad = self.rows[0]["audited_status"].upper()
        self.rows[0]["audited_status"] = bad
        self.write()
        cid = self.rows[0]["claim_id"]
        self.assertLintFails(*self.lint(), f"ERROR   registry/claims.csv:2: {cid}: audited_status '{bad}' is not in the status vocabulary")

    def test_duplicate_claim_id(self):
        self.rows.append(dict(self.rows[0]))
        self.write()
        cid = self.rows[0]["claim_id"]
        self.assertLintFails(*self.lint(), f"ERROR   registry/claims.csv:{len(self.rows) + 1}: duplicate claim_id {cid} (first at line 2)")

    def test_empty_claim_id(self):
        self.rows[0]["claim_id"] = ""
        self.write()
        self.assertLintFails(*self.lint(), "ERROR   registry/claims.csv:2: empty claim_id")

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
        self.assertLintFails(*self.lint(), f"ERROR   registry/claims.csv not found in {self.root}; claims registry "
                                           "missing, nothing was linted")

    VOCAB_MISSING = ("ERROR   no status vocabulary found (no '## Status vocabulary' fenced block in registry/README.md and "
                     "no values in tools/ci/claim_statuses.txt); status values were NOT checked")

    def test_vocabulary_missing_fails_without_strict(self):
        """Was GAP G6 (warning, value checks skipped, exit 0 as CI runs it). Fixed on fix/lint-claims-fail-closed."""
        self.edit_text("registry/README.md", lambda t: t.replace("## Status vocabulary", "## Status words"))
        self.rows[0]["audited_status"] = "Proved"          # would be an error with a vocabulary
        self.write()
        rc, out = self.lint()
        self.assertRejected(rc, out)
        self.assertEqual(rc, 1, out)
        self.assertIn(self.VOCAB_MISSING, out.splitlines())
        self.assertEqual(out.splitlines()[-1], "== result: 1 error(s), 0 warning(s), 2 notice(s) -> FAIL")

    def test_strict_fails_a_warning_only_input(self):
        """--strict must change the verdict: an input whose only finding is a WARNING (an untested SSRH-ORIG origin
        hypothesis labelled with a valid but 'failed-only' status) passes without --strict and fails with it."""
        i = next(k for k, r in enumerate(self.rows) if r["claim_id"].startswith("SSRH-ORIG-"))
        self.rows[i]["audited_status"] = "Retired / Superseded"        # in the vocabulary, so not an ERROR
        self.write()
        rc, out = self.lint()
        self.assertEqual(rc, 0, out[-2000:])
        self.assertEqual(out.splitlines()[-1], "== result: 0 error(s), 1 warning(s), 0 notice(s) -> PASS")
        rc, out = self.lint("--strict")
        self.assertRejected(rc, out, f"{self.rows[i]['claim_id']}: audited_status 'Retired / Superseded' uses Retired")
        self.assertEqual(out.splitlines()[-1], "== result: 0 error(s), 1 warning(s), 0 notice(s) -> FAIL")

    # --- Researcher 001 audit of 37b9026: G5b, G6b, G6c, G6d (were accepted, exit 0) ----------------
    def test_status_column_renamed(self):
        """G6b (high): audited_status renamed -> NOTICE '(column not present)' and PASS, even with --strict."""
        self.cols = [c if c != "audited_status" else "audited_status_v2" for c in self.cols]
        for r in self.rows:
            r["audited_status_v2"] = r.pop("audited_status")
        self.rows[0]["audited_status_v2"] = "Proved"
        self.write()
        msg = "ERROR   registry/claims.csv:1: status column 'audited_status' missing from the header; its values were NOT checked"
        for extra in ((), ("--strict",)):
            with self.subTest(args=extra):
                self.assertLintFails(*self.lint(*extra), msg)

    def test_duplicate_status_column(self):
        """G6c: a second audited_status column shadowed a bad value in the first copy (DictReader keeps the last)."""
        k = self.cols.index("audited_status")
        def edit(t):
            rows = list(csv.reader(io.StringIO(t)))
            rows[0].append("audited_status")
            for r in rows[1:]:
                r.append(r[k])
            rows[1][k] = "Proved"
            b = io.StringIO(); csv.writer(b, lineterminator="\n").writerows(rows); return b.getvalue()
        self.edit_text("registry/claims.csv", edit)
        self.assertLintFails(*self.lint(), f"ERROR   registry/claims.csv:1: duplicate column 'audited_status' in the header "
                                           f"(columns {k + 1}, {len(self.cols) + 1})")

    def test_header_only_claims_csv(self):
        """G5b: a header with 0 data rows printed 'checked 0 claim rows' and passed."""
        self.write(rows=[])
        self.assertLintFails(*self.lint(), "ERROR   registry/claims.csv: no data rows (header only); nothing was linted")

    def test_earlier_duplicate_vocabulary_block(self):
        """G6d: an EARLIER '## Status vocabulary' block adding 'Proved' silently won (first block was used)."""
        self.edit_text("registry/README.md", lambda t: "## Status vocabulary\n\n```text\nProved\n```\n\n" + t)
        self.rows[0]["audited_status"] = "Proved"
        self.write()
        rc, out = self.lint()
        with open(os.path.join(self.root, "registry/README.md")) as f:
            n = [k + 1 for k, ln in enumerate(f.read().splitlines()) if ln.strip() == "## Status vocabulary"]
        self.assertEqual(len(n), 2)
        self.assertLintFails(rc, out, f"ERROR   registry/README.md: 2 '## Status vocabulary' headings (lines {n[0]}, {n[1]}); "
                                      "exactly one is allowed, status values were NOT checked")

    # --- unreadable input: one-line ERROR, exit 1, no traceback (BOM was a misleading "no 'claim_id' column") ------
    def test_claims_csv_with_bom(self):
        self.edit_text("registry/claims.csv", lambda b: b"\xef\xbb\xbf" + b, binary=True)
        self.assertLintFails(*self.lint(), "ERROR   registry/claims.csv: starts with a UTF-8 byte-order mark (BOM); "
                                           "save it as UTF-8 without a BOM")

    def test_claims_csv_not_utf8(self):
        self.edit_text("registry/claims.csv", lambda b: b + b"RT-FAKE-02,x,caf\xe9\n", binary=True)
        with open(os.path.join(self.root, "registry/claims.csv"), "rb") as f:
            data = f.read()
        off = data.index(b"\xe9"); line = data[:off].count(b"\n") + 1
        self.assertLintFails(*self.lint(), f"ERROR   registry/claims.csv:{line}: not valid UTF-8 "
                                           f"(byte 0xe9 at offset {off})")

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root can read chmod 000 files")
    def test_claims_csv_unreadable(self):
        p = os.path.join(self.root, "registry/claims.csv")
        os.chmod(p, 0)
        try:
            rc, out = self.lint()
        finally:
            os.chmod(p, 0o644)
        self.assertLintFails(rc, out, "ERROR   registry/claims.csv: cannot be read (PermissionError: Permission denied)")

    # --- Researcher 001 audit of 588d5ee: F1, F2, F5, F6, F7 ---------------------------------------
    def test_unterminated_quote_swallows_appended_row(self):
        """F1: an unclosed quote opening the LAST field of the last row swallowed an appended 'Proved' row into
        that field (csv strict=False) and the lint passed, also with --strict."""
        p = os.path.join(self.root, "registry/claims.csv")
        with open(p, newline="") as f:
            data = f.read().rstrip("\n")
        self.assertTrue(data.endswith(","))                     # fixture: last field of the last row is empty
        r = csv.reader(io.StringIO(data + "\n", newline=""), strict=True)
        starts = [1]
        for _ in r:
            starts.append(r.line_num + 1)
        last_start = starts[-2]                                  # first physical line of the last record
        fake = dict.fromkeys(self.cols, "")                      # no quotes or commas: nothing to close the quote
        fake.update(claim_id="RT-FAKE-01", statement="R* = 0.40 proved in Lean", artifact_status="Proved",
                    audited_status="Proved")
        with open(p, "w", newline="") as f:
            f.write(data + '"\n' + ",".join(fake[c] for c in self.cols) + "\n")
        for extra in ((), ("--strict",)):
            with self.subTest(args=extra):
                self.assertLintFails(*self.lint(*extra), f"ERROR   registry/claims.csv:{last_start}: not parseable as CSV "
                                                         "(unexpected end of data)")

    def test_status_column_name_with_trailing_space(self):
        """F2: an extra 'audited_status ' column (trailing space) holding Proved was not a duplicate (exact names
        only) and was never checked."""
        k = self.cols.index("audited_status")
        def edit(t):
            rows = list(csv.reader(io.StringIO(t)))
            rows[0].append("audited_status ")
            for r in rows[1:]:
                r.append(r[k])
            rows[1][-1] = "Proved"
            b = io.StringIO(); csv.writer(b, lineterminator="\n").writerows(rows); return b.getvalue()
        self.edit_text("registry/claims.csv", edit)
        n = len(self.cols) + 1
        self.assertLintFails(*self.lint(),
                             f"ERROR   registry/claims.csv:1: column {n} name 'audited_status ' has leading/trailing whitespace",
                             f"ERROR   registry/claims.csv:1: duplicate column in the header (columns {k + 1}, {n}: "
                             "'audited_status', 'audited_status ' differ only in case or surrounding whitespace)", errors=2)

    def test_claims_csv_nul_byte(self):
        """F6: csv accepts NUL bytes on Python >= 3.11, so a NUL in claims.csv passed."""
        self.edit_text("registry/claims.csv", lambda b: b.replace(b"\n", b"\x00\n", 1), binary=True)
        with open(os.path.join(self.root, "registry/claims.csv"), "rb") as f:
            off = f.read().index(b"\x00")
        self.assertLintFails(*self.lint(), f"ERROR   registry/claims.csv:1: contains a NUL byte (offset {off}); not a text file")

    def test_empty_columns_option(self):
        """F7: --columns "" linted no column and passed."""
        self.rows[0]["audited_status"] = "Proved"
        self.write()
        self.assertLintFails(*self.lint("--columns", ""),
                             "ERROR   --columns names no status column; status values were NOT checked")

    @gap("lint_claims.py: an indented '    ## Status vocabulary' (a Markdown code line, not a heading) is used as the vocabulary")
    def test_GAP_indented_vocabulary_heading(self):
        """F5 (low): the heading match is ln.strip() == '## Status vocabulary', so a 4-space-indented line, which
        Markdown renders as code, still selects the block. Here it is the only one and adds 'Proved'."""
        self.edit_text("registry/README.md", lambda t: t.replace("## Status vocabulary\n", "    ## Status vocabulary\n", 1)
                       .replace("```text\n", "```text\nProved\n", 1))
        self.rows[0]["audited_status"] = "Proved"
        self.write()
        self.assertRejected(*self.lint())


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
