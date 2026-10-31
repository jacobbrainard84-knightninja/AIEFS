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
HEADER = "claim_id,statement,artifact_status,audited_status,audited_qualifier\n"


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
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.root = self.d.name

    def tearDown(self):
        self.d.cleanup()

    def repo(self, rows, spec=SPEC, readme=True):
        if readme:
            write(self.root, "registry/README.md", README.format(spec=spec))
        write(self.root, "registry/claims.csv", HEADER + "".join(rows))

    def test_parse_block(self):
        v = lint_claims.parse_readme_vocab(README.format(spec=SPEC))
        self.assertEqual(v[0], "Supported"); self.assertIn(SPEC, v); self.assertEqual(len(v), 6)

    def test_speculative_accepted_when_listed(self):
        self.repo([f'SSRH-ORIG-01,x,Incomplete,{SPEC},free text (not linted)\n'])
        rc, out = run(lint_claims.main, ["--repo", self.root])
        self.assertEqual(rc, 0, out); self.assertIn("0 status violation", out)

    def test_speculative_rejected_when_not_listed(self):
        self.repo([f'SSRH-ORIG-01,x,Incomplete,{SPEC},\n'], spec="Exploratory")
        rc, out = run(lint_claims.main, ["--repo", self.root])
        self.assertEqual(rc, 1, out); self.assertIn("no 'Speculative", out)

    def test_ssrh_retired_warns(self):
        self.repo(['SSRH-ORIG-02,x,Incomplete,Retired / Superseded,\n'])
        rc, out = run(lint_claims.main, ["--repo", self.root])
        self.assertEqual(rc, 0, out); self.assertIn("WARNING", out); self.assertIn("never Retired", out)
        rc, _ = run(lint_claims.main, ["--repo", self.root, "--strict"])
        self.assertEqual(rc, 1)

    def test_unknown_and_qualified_status_fail(self):
        self.repo(['A-1,x,Supported,Supported (single seed),\n', 'A-2,x,Bogus,Supported,\n'])
        rc, out = run(lint_claims.main, ["--repo", self.root])
        self.assertEqual(rc, 1); self.assertIn("'Supported (single seed)'", out); self.assertIn("'Bogus'", out)

    def test_duplicate_id(self):
        self.repo(['A-1,x,Supported,Supported,\n', 'A-1,y,Supported,Supported,\n'])
        rc, out = run(lint_claims.main, ["--repo", self.root])
        self.assertEqual(rc, 1); self.assertIn("duplicate claim_id", out)

    def test_missing_claims_is_notice(self):
        rc, out = run(lint_claims.main, ["--repo", self.root])
        self.assertEqual(rc, 0); self.assertIn("NOTICE", out); self.assertIn("skipped", out)

    def test_placeholder_fallback_skips_with_warning(self):
        self.repo(['A-1,x,Anything,Anything,\n'], readme=False)
        write(self.root, "tools/ci/claim_statuses.txt", "# PLACEHOLDER\n# no values\n")
        rc, out = run(lint_claims.main, ["--repo", self.root])
        self.assertEqual(rc, 0, out); self.assertIn("value checks skipped", out)

    def test_filled_fallback_used(self):
        self.repo(['A-1,x,Supported,Bogus,\n'], readme=False)
        write(self.root, "tools/ci/claim_statuses.txt", f"# list\nSupported\n{SPEC}\n")
        rc, out = run(lint_claims.main, ["--repo", self.root])
        self.assertEqual(rc, 1, out); self.assertIn("'Bogus'", out)


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
