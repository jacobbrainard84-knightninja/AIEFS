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
import json
import os
import shutil
import subprocess
import unittest
import zipfile

from rtcommon import PY, REPO, TempDirMixin, farm, gap, materialize, run

LINT = os.path.join(REPO, "tools/ci/lint_claims.py")


def _known_missing_count():
    """Number of live KNOWN_MISSING_ARTIFACTS entries. On the real copy each one is cited and missing (the lint
    errors otherwise), so each adds exactly one NOTICE to every run that reaches its row."""
    import sys
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sys.path.insert(0, os.path.dirname(LINT))
    try:
        import lint_claims
        return len(lint_claims.KNOWN_MISSING_ARTIFACTS)
    finally:
        sys.path.pop(0)
        sys.dont_write_bytecode = old


KNOWN_NOTICES = _known_missing_count()
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

    def assertLintFails(self, rc, out, *lines, errors=1, notices=KNOWN_NOTICES):
        """Exit 1, no traceback, each given line present as a WHOLE output line, and the exact result line.
        notices: the live KNOWN_MISSING_ARTIFACTS NOTICEs, printed when the lint reaches their rows."""
        self.assertRejected(rc, out)
        self.assertEqual(rc, 1, out)
        self.assertNotIn("Traceback", out)
        got = out.splitlines()
        for ln in lines:
            self.assertIn(ln, got, out[-3000:])
        self.assertEqual(got[-1], f"== result: {errors} error(s), 0 warning(s), {notices} notice(s) -> FAIL", out[-3000:])

    def assertLintFailsBeforeRows(self, rc, out, *lines, errors=1):
        """assertLintFails for inputs rejected before any data row is linted (so no KNOWN_MISSING NOTICE)."""
        self.assertLintFails(rc, out, *lines, errors=errors, notices=0)

    def edit_text(self, rel, fn, binary=False):
        p = os.path.join(self.root, rel)
        with open(p, "rb" if binary else "r", **({} if binary else {"newline": ""})) as f:
            data = f.read()
        with open(p, "wb" if binary else "w", **({} if binary else {"newline": ""})) as f:
            f.write(fn(data))

    def test_00_control_copy_passes(self):
        rc, out = self.lint()
        self.assertEqual(rc, 0, out[-2000:])
        self.assertEqual(out.splitlines()[-1], f"== result: 0 error(s), 0 warning(s), {KNOWN_NOTICES} notice(s) -> PASS")

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

    # Formerly GAP G3 (fixed: check_artifacts / resolve_artifact).
    def test_row_citing_nonexistent_artifact(self):
        self.rows.append(self.fake_row(supporting_artifacts="runs/000000000000;results/no_such_file.npz"))
        self.write()
        self.assertRejected(*self.lint(), "RT-FAKE-01: cited artifact does not exist: 'runs/000000000000'",
                            "RT-FAKE-01: cited artifact does not exist: 'results/no_such_file.npz'")

    # Formerly GAP G4 (fixed: check_artifacts, formal-proof rule). README.md exists and is even registered as
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

    # Round-2 follow-ups from Auditor Seat 002's audit of the G3/G4 fix.
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
                         [ln for ln in out.splitlines() if ln.startswith(f"ERROR   registry/claims.csv:1: required column '{col}'")],
                         out[-2000:])   # exactly the one header ERROR, no follow-on errors
        return rc, out

    def test_evidence_scope_column_deleted(self):
        rc, out = self.drop_column("evidence_scope")
        self.assertRejected(rc, out, "ERROR   registry/claims.csv:1: required column 'evidence_scope' missing from the header; "
                                     "evidence_scope values and formal-scope rows were NOT checked")
        self.assertEqual(rc, 1, out[-2000:])

    def test_supporting_artifacts_column_deleted(self):
        rc, out = self.drop_column("supporting_artifacts")
        self.assertRejected(rc, out, "ERROR   registry/claims.csv:1: required column 'supporting_artifacts' missing from "
                                     "the header; cited artifacts and KNOWN_MISSING_ARTIFACTS entries were NOT checked")
        self.assertEqual(rc, 1, out[-2000:])

    def test_statement_column_deleted(self):
        rc, out = self.drop_column("statement")
        self.assertRejected(rc, out, "ERROR   registry/claims.csv:1: required column 'statement' missing from the header; "
                                     "its Lean-proof wording was NOT checked")
        self.assertEqual(rc, 1, out[-2000:])

    def test_claims_file_missing(self):
        """Was GAP G5 (NOTICE and exit 0). Fixed: lint() errors when claims.csv is absent."""
        os.unlink(os.path.join(self.root, "registry/claims.csv"))
        self.assertLintFailsBeforeRows(*self.lint(), f"ERROR   registry/claims.csv not found in {self.root}; claims registry "
                                           "missing, nothing was linted")

    VOCAB_MISSING = ("ERROR   no status vocabulary found (no '## Status vocabulary' fenced block in registry/README.md and "
                     "no values in tools/ci/claim_statuses.txt); status values were NOT checked")

    def test_vocabulary_missing_fails_without_strict(self):
        """Was GAP G6 (warning, value checks skipped, exit 0 as CI runs it). Fixed: lint() errors when load_vocab finds no values."""
        self.edit_text("registry/README.md", lambda t: t.replace("## Status vocabulary", "## Status words"))
        self.rows[0]["audited_status"] = "Proved"          # would be an error with a vocabulary
        self.write()
        rc, out = self.lint()
        self.assertRejected(rc, out)
        self.assertEqual(rc, 1, out)
        self.assertIn(self.VOCAB_MISSING, out.splitlines())
        self.assertEqual(out.splitlines()[-1], f"== result: 1 error(s), 0 warning(s), {2 + KNOWN_NOTICES} notice(s) -> FAIL")

    def test_vocabulary_missing_is_caught_with_strict(self):
        p = os.path.join(self.root, "registry/README.md")
        with open(p) as f:
            txt = f.read()
        with open(p, "w") as f:
            f.write(txt.replace("## Status vocabulary", "## Status words"))
        self.assertRejected(*self.lint("--strict"))

    def test_strict_fails_a_warning_only_input(self):
        """--strict must change the verdict: an input whose only finding is a WARNING (an untested SSRH-ORIG origin
        hypothesis labelled with a valid but 'failed-only' status) passes without --strict and fails with it."""
        i = next(k for k, r in enumerate(self.rows) if r["claim_id"].startswith("SSRH-ORIG-"))
        self.rows[i]["audited_status"] = "Retired / Superseded"        # in the vocabulary, so not an ERROR
        self.write()
        rc, out = self.lint()
        self.assertEqual(rc, 0, out[-2000:])
        self.assertEqual(out.splitlines()[-1], f"== result: 0 error(s), 1 warning(s), {KNOWN_NOTICES} notice(s) -> PASS")
        rc, out = self.lint("--strict")
        self.assertRejected(rc, out, f"{self.rows[i]['claim_id']}: audited_status 'Retired / Superseded' uses Retired")
        self.assertEqual(out.splitlines()[-1], f"== result: 0 error(s), 1 warning(s), {KNOWN_NOTICES} notice(s) -> FAIL")

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
        self.assertLintFailsBeforeRows(*self.lint(), "ERROR   registry/claims.csv: no data rows (header only); nothing was linted")

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
        self.assertLintFailsBeforeRows(*self.lint(), "ERROR   registry/claims.csv: starts with a UTF-8 byte-order mark (BOM); "
                                           "save it as UTF-8 without a BOM")

    def test_claims_csv_not_utf8(self):
        self.edit_text("registry/claims.csv", lambda b: b + b"RT-FAKE-02,x,caf\xe9\n", binary=True)
        with open(os.path.join(self.root, "registry/claims.csv"), "rb") as f:
            data = f.read()
        off = data.index(b"\xe9"); line = data[:off].count(b"\n") + 1
        self.assertLintFailsBeforeRows(*self.lint(), f"ERROR   registry/claims.csv:{line}: not valid UTF-8 "
                                           f"(byte 0xe9 at offset {off})")

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root can read chmod 000 files")
    def test_claims_csv_unreadable(self):
        p = os.path.join(self.root, "registry/claims.csv")
        os.chmod(p, 0)
        try:
            rc, out = self.lint()
        finally:
            os.chmod(p, 0o644)
        self.assertLintFailsBeforeRows(rc, out, "ERROR   registry/claims.csv: cannot be read (PermissionError: Permission denied)")

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
        self.assertLintFailsBeforeRows(*self.lint(), f"ERROR   registry/claims.csv:1: contains a NUL byte (offset {off}); not a text file")

    def test_empty_columns_option(self):
        """F7: --columns "" linted no column and passed."""
        self.rows[0]["audited_status"] = "Proved"
        self.write()
        self.assertLintFailsBeforeRows(*self.lint("--columns", ""),
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
