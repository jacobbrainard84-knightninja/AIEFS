#!/usr/bin/env python3
"""Self-tests for tools/ci/lint_claims.py and tools/ci/hygiene_scan.py (stdlib unittest).

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v
All fixtures are synthetic and built in temporary folders; fake credentials are assembled at
run time so this file contains no credential-like literal.
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import hygiene_scan  # noqa: E402
import lint_claims  # noqa: E402

SPEC = "Speculative / untested origin hypothesis"
README = """# Registry

## Status vocabulary

```text
Supported
Incomplete
Rejected
Quarantined
Retired / Superseded
{spec}
```

Prose after the block.
"""
# lint_claims' scope check needs this table in registry/README.md; readme=False fixtures get only this table.
SCOPE_TABLE = """
### Axis 2 — `evidence_scope`

| Value | Definition |
|---|---|
| `Implementation identity` | x |
| `Finite numerical observation` | x |
| `Controlled experimental result` | x |
| `Conditional theorem` | x |
| `Formalized theorem` | x |
| `Conjecture` | x |
"""
README += SCOPE_TABLE
# evidence_scope and supporting_artifacts are required by lint_claims' artifact checks; repo() appends ROW_TAIL.
HEADER = "claim_id,statement,artifact_status,audited_status,audited_qualifier,evidence_scope,supporting_artifacts\n"
ROW_TAIL = ",Conditional theorem,registry/README.md\n"


def run(fn, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(argv)
    return rc, buf.getvalue()


def write(root, rel, text, mode="w"):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, mode) as f:
        f.write(text)
    return p


class LintClaimsTests(unittest.TestCase):
    """Each test asserts whole output lines (exact text), not substrings, and the exact result line."""

    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.root = self.d.name
        # Synthetic repos cite none of the live KNOWN_MISSING_ARTIFACTS entries; empty the list so the
        # stale-entry check (which always runs) does not flag them. The real list is tested in tools/redteam.
        p = mock.patch.object(lint_claims, "KNOWN_MISSING_ARTIFACTS", {}); p.start(); self.addCleanup(p.stop)

    def tearDown(self):
        self.d.cleanup()

    def repo(self, rows, spec=SPEC, readme=True, header=None):
        """readme=False writes a README with only SCOPE_TABLE (no status vocabulary, so the fallback is read).
        Rows give the first 5 fields; ROW_TAIL fills evidence_scope and supporting_artifacts. With a custom
        header, rows are written as given and must hold every field."""
        write(self.root, "registry/README.md", README.format(spec=spec) if readme else SCOPE_TABLE)
        body = "".join(rows) if header else "".join(r.rstrip("\n") + ROW_TAIL for r in rows)
        write(self.root, "registry/claims.csv", (header or HEADER) + body)

    def lint(self, *extra):
        return run(lint_claims.main, ["--repo", self.root, *extra])

    def assertLines(self, out, *lines):
        got = out.splitlines()
        for ln in lines:
            self.assertIn(ln, got, out)

    def assertResult(self, out, errors, warnings=0, notices=0, verdict=None):
        verdict = verdict or ("FAIL" if errors else "PASS")
        self.assertEqual(out.splitlines()[-1], f"== result: {errors} error(s), {warnings} warning(s), "
                                               f"{notices} notice(s) -> {verdict}", out)

    def test_parse_block(self):
        v = lint_claims.parse_readme_vocab(README.format(spec=SPEC))
        self.assertEqual(v, ["Supported", "Incomplete", "Rejected", "Quarantined", "Retired / Superseded", SPEC])

    def test_speculative_accepted_when_listed(self):
        self.repo([f'SSRH-ORIG-01,x,Incomplete,{SPEC},free text (not linted)\n'])
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertLines(out, "registry/claims.csv: 7 columns; linting artifact_status, audited_status",
                         "checked 1 claim rows; 0 status violation(s)")
        self.assertResult(out, 0)

    def test_speculative_rejected_when_not_listed(self):
        self.repo([f'SSRH-ORIG-01,x,Incomplete,{SPEC},\n'], spec="Exploratory")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"WARNING vocabulary has no '{SPEC}' status; untested origin ideas need it",
                         f"ERROR   registry/claims.csv:2: SSRH-ORIG-01: audited_status '{SPEC}' is not in the status vocabulary")
        self.assertResult(out, 1, 1)

    def test_strict_turns_warning_into_failure(self):
        """The only difference between the two runs is --strict: a warning-only input passes without it and
        fails with it (exit 1, verdict FAIL, same counts)."""
        self.repo(['SSRH-ORIG-02,x,Incomplete,Retired / Superseded,\n'])
        warning = ("WARNING registry/claims.csv:2: SSRH-ORIG-02: audited_status 'Retired / Superseded' uses Retired; "
                   f"untested origin hypotheses should be '{SPEC}', never Retired "
                   "(Retired/Rejected/Quarantined are for tested-and-failed or withdrawn claims)")
        rc, out = self.lint()
        self.assertEqual(rc, 0, out); self.assertLines(out, warning); self.assertResult(out, 0, 1)
        rc, out = self.lint("--strict")
        self.assertEqual(rc, 1, out); self.assertLines(out, warning); self.assertResult(out, 0, 1, verdict="FAIL")

    def test_unknown_and_qualified_status_fail(self):
        self.repo(['A-1,x,Supported,Supported (single seed),\n', 'A-2,x,Bogus,Supported,\n'])
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out,
                         "ERROR   registry/claims.csv:2: A-1: audited_status 'Supported (single seed)' is not in the status vocabulary",
                         "ERROR   registry/claims.csv:3: A-2: artifact_status 'Bogus' is not in the status vocabulary",
                         "checked 2 claim rows; 2 status violation(s)")
        self.assertResult(out, 2)

    def test_duplicate_id(self):
        self.repo(['A-1,x,Supported,Supported,\n', 'A-1,y,Supported,Supported,\n'])
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   registry/claims.csv:3: duplicate claim_id A-1 (first at line 2)")
        self.assertResult(out, 1)

    def test_missing_claims_fails(self):
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, f"ERROR   registry/claims.csv not found in {self.root}; claims registry missing, nothing was linted")
        self.assertResult(out, 1)

    def test_no_vocabulary_fails_without_strict(self):
        self.repo(['A-1,x,Anything,Anything,\n'], readme=False)
        write(self.root, "tools/ci/claim_statuses.txt", "# PLACEHOLDER\n# no values\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   no status vocabulary found (no '## Status vocabulary' fenced block in registry/README.md "
                              "and no values in tools/ci/claim_statuses.txt); status values were NOT checked")
        self.assertResult(out, 1, 0, 2)

    def test_filled_fallback_used(self):
        self.repo(['A-1,x,Supported,Bogus,\n'], readme=False)
        write(self.root, "tools/ci/claim_statuses.txt", f"# list\nSupported\n{SPEC}\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "vocabulary: 2 statuses from " + os.path.join(self.root, "tools/ci/claim_statuses.txt"),
                         "ERROR   registry/claims.csv:2: A-1: audited_status 'Bogus' is not in the status vocabulary")
        self.assertResult(out, 1, 0, 1)

    # --- G5b / G6b / G6c / G6d and unreadable input: errors, never a silent pass ----------------
    def test_status_column_renamed_fails(self):
        self.repo(['A-1,x,Supported,Proved,' + ROW_TAIL], header=HEADER.replace("audited_status", "audited_status_v2"))
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   registry/claims.csv:1: status column 'audited_status' missing from the header; "
                              "its values were NOT checked",
                         "registry/claims.csv: 7 columns; linting artifact_status")
        self.assertResult(out, 1)

    def test_duplicate_header_column_fails(self):
        self.repo(['A-1,x,Supported,Proved,' + ROW_TAIL.rstrip("\n") + ',Supported\n'],
                  header=HEADER.rstrip("\n") + ",audited_status\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   registry/claims.csv:1: duplicate column 'audited_status' in the header (columns 4, 8)")
        self.assertResult(out, 1)

    def test_header_only_fails(self):
        self.repo([])
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   registry/claims.csv: no data rows (header only); nothing was linted")
        self.assertResult(out, 1)

    def test_two_vocabulary_headings_fail(self):
        self.repo(['A-1,x,Supported,Proved,\n'])
        p = os.path.join(self.root, "registry/README.md")
        with open(p) as f:
            txt = f.read()
        write(self.root, "registry/README.md", "## Status vocabulary\n\n```text\nProved\n```\n\n" + txt)
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   registry/README.md: 2 '## Status vocabulary' headings (lines 1, 9); exactly one is "
                              "allowed, status values were NOT checked")
        self.assertResult(out, 1)

    def test_bom_fails(self):
        for rel in ("registry/claims.csv", "registry/README.md"):
            with self.subTest(rel=rel):
                self.repo(['A-1,x,Supported,Supported,\n'])
                p = os.path.join(self.root, rel)
                with open(p, "rb") as f:
                    data = f.read()
                write(self.root, rel, b"\xef\xbb\xbf" + data, "wb")
                rc, out = self.lint()
                self.assertEqual(rc, 1, out)
                self.assertLines(out, f"ERROR   {rel}: starts with a UTF-8 byte-order mark (BOM); save it as UTF-8 without a BOM")
                self.assertNotIn("Traceback", out)
                self.assertResult(out, 1)

    def test_non_utf8_fails(self):
        self.repo([])   # README; claims.csv is overwritten below with a Latin-1 byte
        write(self.root, "registry/claims.csv", (HEADER + "A-1,x,Supported,Supported,caf\xe9\n").encode("latin-1"), "wb")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        off = len(HEADER) + len("A-1,x,Supported,Supported,caf")
        self.assertLines(out, f"ERROR   registry/claims.csv:2: not valid UTF-8 (byte 0xe9 at offset {off})")
        self.assertResult(out, 1)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root can read chmod 000 files")
    def test_unreadable_fails(self):
        self.repo(['A-1,x,Supported,Supported,\n'])
        p = os.path.join(self.root, "registry/claims.csv")
        os.chmod(p, 0)
        try:
            rc, out = self.lint()
        finally:
            os.chmod(p, 0o644)
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   registry/claims.csv: cannot be read (PermissionError: Permission denied)")
        self.assertResult(out, 1)


    # --- Researcher 001 audit of 588d5ee: F1, F2, F3, F6, F7 ----------------------------------------
    def test_unterminated_quote_at_eof_fails(self):
        """F1: an unclosed quote in the last field of the last row swallowed an appended 'Proved' row into one field
        (csv strict=False) and the lint passed, also with --strict. Now one ERROR line, exit 1, no traceback."""
        self.repo(['A-1,x,Supported,Supported,"unclosed\n', 'A-2,x,Supported,Proved,\n'])
        for extra in ((), ("--strict",)):
            with self.subTest(args=extra):
                rc, out = self.lint(*extra)
                self.assertEqual(rc, 1, out)
                self.assertLines(out, "ERROR   registry/claims.csv:2: not parseable as CSV (unexpected end of data)")
                self.assertEqual([ln for ln in out.splitlines() if ln.startswith("ERROR")],
                                 ["ERROR   registry/claims.csv:2: not parseable as CSV (unexpected end of data)"], out)
                self.assertNotIn("Traceback", out)
                self.assertResult(out, 1)

    def test_text_after_closing_quote_fails(self):
        """Parse-error path mid-file: strict=False silently turned '"Supp"orted' into 'Supported'."""
        self.repo(['A-1,x,"Supp"orted,Supported,\n', 'A-2,x,Supported,Supported,\n'])
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   registry/claims.csv:2: not parseable as CSV (',' expected after '\"')")
        self.assertNotIn("Traceback", out)
        self.assertResult(out, 1)

    def test_header_name_with_whitespace_fails(self):
        """F2: an extra 'audited_status ' column (trailing space) holding Proved was never checked, and was not
        caught as a duplicate (exact-name comparison only)."""
        self.repo(['A-1,x,Supported,Supported,' + ROW_TAIL.rstrip("\n") + ',Proved\n'],
                  header=HEADER.rstrip("\n") + ",audited_status \n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   registry/claims.csv:1: column 8 name 'audited_status ' has leading/trailing whitespace",
                         "ERROR   registry/claims.csv:1: duplicate column in the header (columns 4, 8: 'audited_status', "
                         "'audited_status ' differ only in case or surrounding whitespace)",
                         "registry/claims.csv: 8 columns; linting artifact_status")
        self.assertResult(out, 2)

    def test_header_name_case_duplicate_fails(self):
        """F2: 'Audited_Status' next to 'audited_status' is a duplicate after casefold()."""
        self.repo(['A-1,x,Supported,Supported,' + ROW_TAIL.rstrip("\n") + ',Proved\n'],
                  header=HEADER.rstrip("\n") + ",Audited_Status\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   registry/claims.csv:1: duplicate column in the header (columns 4, 8: 'audited_status', "
                              "'Audited_Status' differ only in case or surrounding whitespace)")
        self.assertResult(out, 1)

    def test_nul_byte_fails(self):
        """F6: csv accepts NUL on Python >= 3.11, so a NUL byte in claims.csv passed."""
        self.repo(['A-1,x,Supported,Supported,a\x00b\n'])
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        off = len(HEADER) + len("A-1,x,Supported,Supported,a")
        self.assertLines(out, f"ERROR   registry/claims.csv:2: contains a NUL byte (offset {off}); not a text file")
        self.assertResult(out, 1)

    def test_empty_columns_option_fails(self):
        """F7: --columns "" checked nothing and passed."""
        self.repo(['A-1,x,Supported,Proved,\n'])
        for arg in ("", " , "):
            with self.subTest(columns=arg):
                rc, out = self.lint("--columns", arg)
                self.assertEqual(rc, 1, out)
                self.assertLines(out, "ERROR   --columns names no status column; status values were NOT checked")
                self.assertResult(out, 1)

    def _fallback_repo(self, data):
        """claims.csv with a bad value, a README with no status vocabulary (only SCOPE_TABLE, so the fallback is
        read), fallback bytes as given."""
        self.repo(['A-1,x,Supported,Bogus,\n'], readme=False)
        write(self.root, "tools/ci/claim_statuses.txt", data, "wb")
        return os.path.join(self.root, "tools/ci/claim_statuses.txt")

    def test_fallback_bom_fails(self):
        self._fallback_repo(b"\xef\xbb\xbfSupported\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   tools/ci/claim_statuses.txt: starts with a UTF-8 byte-order mark (BOM); "
                              "save it as UTF-8 without a BOM")
        self.assertNotIn("Traceback", out)
        self.assertResult(out, 1, 0, 1)

    def test_fallback_non_utf8_fails(self):
        self._fallback_repo(b"# list\nSupported\ncaf\xe9\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertLines(out, "ERROR   tools/ci/claim_statuses.txt:3: not valid UTF-8 (byte 0xe9 at offset 20)")
        self.assertNotIn("Traceback", out)
        self.assertResult(out, 1, 0, 1)

    def test_readme_non_utf8_fails(self):
        self.repo(['A-1,x,Supported,Supported,\n'])
        p = os.path.join(self.root, "registry/README.md")
        with open(p, "rb") as f:
            data = f.read()
        write(self.root, "registry/README.md", data + b"caf\xe9\n", "wb")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        line = data.count(b"\n") + 1
        self.assertLines(out, f"ERROR   registry/README.md:{line}: not valid UTF-8 (byte 0xe9 at offset {len(data) + 3})")
        self.assertNotIn("Traceback", out)
        self.assertResult(out, 1)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root can read chmod 000 files")
    def test_readme_and_fallback_unreadable_fail(self):
        cases = (("registry/README.md", lambda: self.repo(['A-1,x,Supported,Supported,\n']), 0),
                 ("tools/ci/claim_statuses.txt", lambda: self._fallback_repo(b"Supported\n"), 1))
        for rel, build, notices in cases:
            with self.subTest(rel=rel):
                build()
                p = os.path.join(self.root, rel)
                os.chmod(p, 0)
                try:
                    rc, out = self.lint()
                finally:
                    os.chmod(p, 0o644)
                self.assertEqual(rc, 1, out)
                self.assertLines(out, f"ERROR   {rel}: cannot be read (PermissionError: Permission denied)")
                self.assertNotIn("Traceback", out)
                self.assertResult(out, 1, 0, notices)


class HygieneScanTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.root = self.d.name
        g = ["git", "-C", self.root]
        subprocess.run(g + ["init", "-q"], check=True)
        subprocess.run(g + ["config", "user.email", "ci@example.com"], check=True)
        subprocess.run(g + ["config", "user.name", "ci"], check=True)
        write(self.root, "README.md", "hello\n")
        write(self.root, "tools/ci/hygiene_allow.txt", "runs/\n")
        subprocess.run(g + ["add", "-A"], check=True)
        subprocess.run(g + ["commit", "-qm", "base"], check=True)
        self.g = g

    def tearDown(self):
        self.d.cleanup()

    def commit(self):
        subprocess.run(self.g + ["add", "-A", "-f"], check=True)
        subprocess.run(self.g + ["commit", "-qm", "change"], check=True)

    def test_clean(self):
        rc, out = run(hygiene_scan.main, ["--repo", self.root])
        self.assertEqual(rc, 0, out)

    def test_secret_pattern_value_not_printed(self):
        fake = "gh" + "p_" + "A1b2C3d4" * 5
        write(self.root, "notes.txt", f"token here {fake}\n")
        self.commit()
        rc, out = run(hygiene_scan.main, ["--repo", self.root])
        self.assertEqual(rc, 1); self.assertIn("SECRET_PATTERN notes.txt:1", out); self.assertNotIn(fake, out)

    def test_secret_file_names(self):
        write(self.root, ".env", "X=1\n"); write(self.root, "a/server.pem", "x\n")
        write(self.root, ".env.example", "X=\n")
        self.commit()
        rc, out = run(hygiene_scan.main, ["--repo", self.root])
        self.assertEqual(rc, 1); self.assertIn("SECRET_FILE .env ", out); self.assertIn("a/server.pem", out)
        self.assertNotIn(".env.example", out)

    def test_large_file(self):
        write(self.root, "big.txt", "x" * (2 * 1024 * 1024))
        self.commit()
        rc, out = run(hygiene_scan.main, ["--repo", self.root, "--max-mb", "1"])
        self.assertEqual(rc, 1); self.assertIn("LARGE_FILE big.txt", out)

    def test_new_binary_outside_allowed(self):
        base = subprocess.run(self.g + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        write(self.root, "runs/ok.npz", b"\x00\x01", "wb"); write(self.root, "stray.npz", b"\x00\x01", "wb")
        self.commit()
        rc, out = run(hygiene_scan.main, ["--repo", self.root, "--base", base])
        self.assertEqual(rc, 1, out); self.assertIn("NEW_BINARY stray.npz", out); self.assertNotIn("runs/ok.npz", out)

    def test_pii_and_private_list_locations_only(self):
        mail = "someone" + "@" + "realdomain.org"
        write(self.root, "doc.md", f"contact {mail}\nprivate WORDXYZ here\n")
        plist = os.path.join(self.root, "..", os.path.basename(self.root) + "_private.txt")
        write("/", os.path.abspath(plist).lstrip("/"), "wordxyz\n")
        self.commit()
        rc, out = run(hygiene_scan.main, ["--repo", self.root, "--pii", "--private-patterns", plist])
        os.remove(plist)
        self.assertEqual(rc, 0, out)
        self.assertIn("PII_EMAIL doc.md:1", out); self.assertIn("PRIVATE_LITERAL doc.md:2", out)
        self.assertNotIn(mail, out); self.assertNotIn("WORDXYZ", out); self.assertNotIn("wordxyz", out)

    def _emails(self, line):
        return [m for m in hygiene_scan.EMAIL_PATTERN.finditer(line) if not hygiene_scan.email_is_benign(line, m)]

    def test_email_skips_python_matmul(self):
        at = "@"
        for line in (f"y = M{at}np.array([1, 2])", f"z = (A{at}numpy.linalg.inv(B))",
                     f"w = U{at}torch.ones(3)", f"v = foo(x){at}np.eye(3)", f"q = P{at}jnp.diag(d)"):
            self.assertEqual(self._emails(line), [], line)

    def test_email_skips_reserved_domains(self):
        at = "@"
        for dom in ("example.invalid", "mail.example", "box.test", "example.com", "sub.example.org",
                    "example.net", "dev.localhost", "host.tld"):
            line = f'author "user{at}{dom}"'
            self.assertEqual(self._emails(line), [], dom)

    def test_email_real_shape_still_flagged(self):
        at = "@"
        real = "jane.q.doe" + at + "mailprovider" + ".com"   # synthetic, built at run time
        for line in (f"contact {real}", f"({real})", f"<{real}>", f"np: {real}",
                     "x " + "a" + at + "numpyfans.org", "x " + "a" + at + "example-corp.com",
                     "x " + "b" + at + "testing.io"):
            self.assertEqual(len(self._emails(line)), 1, line)
        write(self.root, "mix.py", f"y = M{at}np.array([1])\nz = 'u{at}example.invalid'\nwho = '{real}'\n")
        self.commit()
        rc, out = run(hygiene_scan.main, ["--repo", self.root, "--pii"])
        self.assertEqual(rc, 0, out)
        self.assertIn("PII_EMAIL mix.py:3", out); self.assertNotIn("mix.py:1", out); self.assertNotIn("mix.py:2", out)
        self.assertNotIn(real, out)


if __name__ == "__main__":
    unittest.main()
