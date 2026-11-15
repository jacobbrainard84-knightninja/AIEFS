#!/usr/bin/env python3
"""Self-tests for tools/ci/check_study_paths.py (stdlib unittest, synthetic temp git repos).

Covers the tokenizer, path / directory / glob resolution, the baseline rules (new unresolved token, stale
baseline entry, vanished row / field / token, malformed baseline) and the CLI exit codes, plus a mutation
check: the checker source is mutated in memory (always resolve, skip the baseline comparison, drop the
stale check, a wrong tokenizer, ...) and every mutant must make at least one scenario fail.
These tests use fixtures only; the real registry is checked by the `study-paths` job of repo-checks.yml.

Run from the repository root:  python3 -m unittest discover -s tools/ci/tests -v
"""
import contextlib
import csv
import io
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CI = os.path.dirname(HERE)
sys.path.insert(0, CI)
import check_study_paths as csp  # noqa: E402

SCRIPT = os.path.join(CI, "check_study_paths.py")
STUDY_COLS = ["study_id", "title", "era", "artifact_status", "evidence_scope", "canonical_entrypoints",
              "canonical_evidence_paths", "sample_design", "stage4_target_dir", "summary"]
SUP_COLS = ["superseded_target", "authoritative_target", "category", "rationale"]
REASON = csp.BASELINE_REASON


def study(sid, entry="", evidence=""):
    return {"study_id": sid, "canonical_entrypoints": entry, "canonical_evidence_paths": evidence}


def sup(old, new):
    return {"superseded_target": old, "authoritative_target": new, "category": "x", "rationale": "r"}


def bl(file, row, field, token, reason=REASON):
    return {"file": file, "row_id": row, "field": field, "token": token, "reason": reason}


S, U = "registry/studies.csv", "registry/supersessions.csv"
EP, EV, AU = "canonical_entrypoints", "canonical_evidence_paths", "authoritative_target"


def make_repo(root, studies=(), sups=(), files=("a.py", "d/x.txt", "dir with space/y.txt", "runs/r1/f.csv"),
              baseline=(), untracked=(), study_cols=None):
    def w(rel, data):
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p) or root, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(data)
    subprocess.run(["git", "-C", root, "init", "-q"], check=True)
    for rel in files:
        w(rel, "x\n")
    for rel in untracked:
        w(rel, "x\n")
    for rel, cols, rows in ((S, study_cols or STUDY_COLS, studies), (U, SUP_COLS, sups)):
        buf = io.StringIO()
        wr = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        wr.writeheader()
        for r in rows:
            wr.writerow(r)
        w(rel, buf.getvalue())
    w("tools/ci/study_paths_baseline.json", json.dumps({"entries": list(baseline)}))
    tracked = list(files) + [S, U]
    subprocess.run(["git", "-C", root, "add", "--"] + tracked, check=True)
    return os.path.join(root, "tools", "ci", "study_paths_baseline.json")


def run(mod, root, extra=()):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = mod.main(["--repo", root] + list(extra))
    return rc, buf.getvalue()


class Base(unittest.TestCase):
    mod = csp

    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = self.d.name

    def tearDown(self):
        self.d.cleanup()

    def go(self, **kw):
        make_repo(self.root, **kw)
        return run(self.mod, self.root)

    def codes(self, out):
        return {ln.split()[1] for ln in out.splitlines() if ln.startswith("ERROR ")}


class OutcomeTests(Base):
    def test_clean_passes(self):
        rc, out = self.go(studies=[study("A", "a.py;d/x.txt", "runs/r1/;d")], sups=[sup("old.py", "a.py")])
        self.assertEqual(rc, 0, out)
        self.assertIn("0 error(s) -> PASS", out)
        self.assertIn("0 unresolved token(s)", out)

    def test_new_unresolved_token_fails(self):
        rc, out = self.go(studies=[study("A", "a.py;missing.py")])
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.codes(out), {"UNRESOLVED"})
        self.assertIn("'missing.py'", out)

    def test_new_unresolved_in_supersessions_fails(self):
        rc, out = self.go(sups=[sup("old.py", "gone.py")])
        self.assertEqual((rc, self.codes(out)), (1, {"UNRESOLVED"}), out)

    def test_superseded_target_is_not_checked(self):
        rc, out = self.go(sups=[sup("long gone.py", "a.py")])
        self.assertEqual(rc, 0, out)

    def test_baselined_unresolved_passes(self):
        rc, out = self.go(studies=[study("A", "a.py;missing.py")], baseline=[bl(S, "A", EP, "missing.py")])
        self.assertEqual(rc, 0, out)
        self.assertIn("1 unresolved token(s), 1 baseline entry", out)
        self.assertIn("1 unresolved in 1 row(s), 1 baselined", out)

    def test_baseline_is_exact_to_row_field_and_token(self):
        # same token baselined for another row / another field does not cover this one
        for entry in (bl(S, "B", EP, "m.py"), bl(S, "A", EV, "m.py"), bl(S, "A", EP, "n.py")):
            with self.subTest(entry=entry):
                with tempfile.TemporaryDirectory() as d:
                    make_repo(d, studies=[study("A", "m.py"), study("B", "a.py")], baseline=[entry, bl(S, "B", EP, "a.py")])
                    rc, out = run(csp, d)
                    self.assertEqual(rc, 1, out)
                    self.assertIn("UNRESOLVED", self.codes(out))

    def test_stale_baseline_entry_fails(self):
        rc, out = self.go(studies=[study("A", "a.py")], baseline=[bl(S, "A", EP, "a.py")])
        self.assertEqual((rc, self.codes(out)), (1, {"STALE_BASELINE"}), out)
        self.assertIn("now resolves", out)

    def test_baselined_token_that_becomes_tracked_fails(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, studies=[study("A", "later.py")], baseline=[bl(S, "A", EP, "later.py")], untracked=["later.py"])
            rc, out = run(csp, d)
            self.assertEqual(rc, 0, "present on disk but untracked must still be unresolved:\n" + out)
            subprocess.run(["git", "-C", d, "add", "later.py"], check=True)
            rc, out = run(csp, d)
            self.assertEqual((rc, self.codes(out)), (1, {"STALE_BASELINE"}), out)

    def test_removed_row_fails(self):
        rc, out = self.go(studies=[study("A", "a.py")], baseline=[bl(S, "GONE", EP, "m.py")])
        self.assertEqual((rc, self.codes(out)), (1, {"BASELINE_GONE"}), out)
        self.assertIn("row no longer exists", out)

    def test_removed_token_fails(self):
        rc, out = self.go(studies=[study("A", "a.py")], baseline=[bl(S, "A", EP, "m.py")])
        self.assertEqual((rc, self.codes(out)), (1, {"BASELINE_GONE"}), out)
        self.assertIn("token no longer in that field", out)

    def test_removed_registry_file_fails(self):
        make_repo(self.root, studies=[study("A", "a.py")])
        subprocess.run(["git", "-C", self.root, "rm", "-q", "-f", U], check=True)
        rc, out = run(csp, self.root)
        self.assertEqual((rc, self.codes(out)), (1, {"REGISTRY_BAD"}), out)

    def test_removed_column_fails(self):
        cols = [c for c in STUDY_COLS if c != EV]
        rc, out = self.go(studies=[study("A", "a.py")], study_cols=cols)
        self.assertEqual((rc, self.codes(out)), (1, {"REGISTRY_BAD"}), out)
        self.assertIn(EV, out)

    def test_duplicate_row_id_fails(self):
        rc, out = self.go(studies=[study("A", "a.py"), study("A", "d/x.txt")])
        self.assertEqual((rc, self.codes(out)), (1, {"REGISTRY_BAD"}), out)

    def test_baseline_problems_fail(self):
        good = bl(S, "A", EP, "m.py")
        cases = {
            "duplicate": [good, dict(good)],
            "empty reason": [bl(S, "A", EP, "m.py", reason="  ")],
            "unchecked field": [bl(S, "A", "title", "m.py")],
            "unchecked file": [bl("registry/claims.csv", "A", EP, "m.py")],
            "extra key": [dict(good, extra="x")],
            "non-string": [dict(good, token=3)],
        }
        for name, entries in cases.items():
            with self.subTest(name):
                with tempfile.TemporaryDirectory() as d:
                    make_repo(d, studies=[study("A", "m.py")], baseline=entries)
                    rc, out = run(csp, d)
                    self.assertEqual(rc, 1, out)
                    self.assertIn("BASELINE_BAD", self.codes(out))

    def test_missing_and_invalid_baseline_fail(self):
        path = make_repo(self.root, studies=[study("A", "a.py")])
        with open(path, "w") as f:
            f.write("{not json")
        rc, out = run(csp, self.root)
        self.assertEqual((rc, "BASELINE_BAD" in self.codes(out)), (1, True), out)
        os.remove(path)
        rc, out = run(csp, self.root)
        self.assertEqual((rc, "BASELINE_BAD" in self.codes(out)), (1, True), out)

    def test_not_a_directory_is_usage_error(self):
        rc, _ = run(csp, os.path.join(self.root, "nope"))
        self.assertEqual(rc, 2)

    def test_print_baseline_lists_only_unresolved(self):
        make_repo(self.root, studies=[study("A", "a.py;m.py")], sups=[sup("o", "n.py")])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = csp.main(["--repo", self.root, "--print-baseline"])
        got = [(e["file"], e["row_id"], e["field"], e["token"], e["reason"]) for e in json.loads(buf.getvalue())["entries"]]
        self.assertEqual((rc, got), (0, [(S, "A", EP, "m.py", REASON), (U, "o", AU, "n.py", REASON)]))


class TokenizerTests(unittest.TestCase):
    def test_semicolon_whitespace_and_empty_pieces(self):
        self.assertEqual(csp.tokenize(" a.py ; b/ ;;c.py; "),
                         [("PATH", "a.py"), ("PATH", "b/"), ("EMPTY", ""), ("PATH", "c.py"), ("EMPTY", "")])

    def test_inner_space_is_kept(self):
        self.assertEqual(csp.tokenize("aief_1_4_intertwining_controller 02/;AI Agent Audits/"),
                         [("PATH", "aief_1_4_intertwining_controller 02/"), ("PATH", "AI Agent Audits/")])

    def test_comma_is_not_a_separator(self):
        self.assertEqual(csp.tokenize("a.py,b.py"), [("PATH", "a.py,b.py")])

    def test_plus_needs_surrounding_spaces(self):
        self.assertEqual(csp.tokenize("runs/a + runs/b"), [("PATH", "runs/a"), ("PATH", "runs/b")])
        self.assertEqual(csp.tokenize("a+b.py"), [("PATH", "a+b.py")])

    def test_leading_dot_slash_is_stripped(self):
        self.assertEqual(csp.tokenize("./a.py"), [("PATH", "a.py")])

    def test_url_is_listed_as_non_path_and_prose_is_not(self):
        self.assertEqual(csp.tokenize("https://example.org/x?y=1;9 sibling 20-seed reruns"),
                         [("URL", "https://example.org/x?y=1"), ("PATH", "9 sibling 20-seed reruns")])

    def test_url_is_reported_not_resolved_not_silently_dropped(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, studies=[study("A", "a.py;https://example.org/p;prose text (x)")],
                      baseline=[bl(S, "A", EP, "prose text (x)")])
            rc, out = run(csp, d)
            self.assertEqual(rc, 0, out)
            self.assertIn("NONPATH", out)
            self.assertIn("'https://example.org/p' (URL, not resolved)", out)
            self.assertIn("2 token(s), 1 resolve, 1 unresolved", out)   # a.py and the prose; the URL is not counted

    def test_empty_piece_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, studies=[study("A", "a.py;")])
            rc, out = run(csp, d)
            self.assertEqual(rc, 0, out)
            self.assertIn("EMPTY", out)


class ResolutionTests(unittest.TestCase):
    tree = csp.Tree(["a.py", "d/x.txt", "d/sub/z.txt", "dir with space/y.txt", "reports/r_report.txt",
                     "aief_1_4_q/q_report.txt", "Case.py"])

    def test_files_dirs_and_trailing_slash(self):
        for tok in ("a.py", "d", "d/", "d/sub", "d/sub/z.txt", "dir with space/", "dir with space/y.txt"):
            self.assertTrue(self.tree.resolves(tok), tok)

    def test_non_members(self):
        for tok in ("b.py", "d/y.txt", "dir with", "a.py/", "d/x.txt/", "case.py", "../a.py", "/a.py", "d//x.txt", ""):
            self.assertFalse(self.tree.resolves(tok), tok)

    def test_glob_is_root_relative_and_segment_wise(self):
        self.assertTrue(self.tree.resolves("*.py"))
        self.assertTrue(self.tree.resolves("a.p?"))
        self.assertTrue(self.tree.resolves("d/*.txt"))
        self.assertTrue(self.tree.resolves("d/*"))            # a directory counts
        self.assertTrue(self.tree.resolves("*/x.txt"))
        self.assertFalse(self.tree.resolves("*_report.txt"))              # only nested files match: not at the root
        self.assertFalse(self.tree.resolves("aief_1_4_*_report.txt"))     # the real registry case
        self.assertFalse(self.tree.resolves("d/*.py"))
        self.assertFalse(self.tree.resolves("*.csv"))
        self.assertTrue(self.tree.resolves("aief_1_4_*/q_report.txt"))

    def test_bracket_is_literal(self):
        self.assertFalse(self.tree.resolves("[a].py"))
        self.assertTrue(csp.Tree(["[a].py"]).resolves("[a].py"))


class CliTests(Base):
    def cli(self, *args):
        r = subprocess.run([sys.executable, SCRIPT, "--repo", self.root] + list(args), capture_output=True, text=True)
        return r.returncode, r.stdout

    def test_exit_codes_through_the_script(self):
        make_repo(self.root, studies=[study("A", "a.py;m.py")], baseline=[bl(S, "A", EP, "m.py")])
        self.assertEqual(self.cli()[0], 0)
        make_repo_fail = os.path.join(self.root, "tools", "ci", "study_paths_baseline.json")
        with open(make_repo_fail, "w") as f:
            json.dump({"entries": []}, f)
        rc, out = self.cli()
        self.assertEqual(rc, 1, out)
        self.assertIn("-> FAIL", out)

    def test_script_runs_isolated_from_a_shadowing_module(self):
        make_repo(self.root, studies=[study("A", "a.py")])
        shadow = os.path.join(self.root, "csv.py")
        with open(shadow, "w") as f:
            f.write("raise SystemExit(0)\n")
        r = subprocess.run([sys.executable, SCRIPT, "--repo", self.root], cwd=self.root, capture_output=True, text=True,
                           env=dict(os.environ, PYTHONPATH=self.root))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("-> PASS", r.stdout)


class ShippedBaselineTests(unittest.TestCase):
    def test_shipped_baseline_is_well_formed(self):
        entries, errors = csp.load_baseline(os.path.join(CI, "study_paths_baseline.json"))
        self.assertEqual(errors, [])
        self.assertTrue(entries)
        for e in entries:
            self.assertTrue(e[4].startswith("unresolved at 871417d"), e)

    def test_script_is_executable_with_shebang(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK))
        with open(SCRIPT, encoding="utf-8") as f:
            self.assertEqual(f.readline().strip(), "#!/usr/bin/env python3")


# ---- mutation check ------------------------------------------------------------------------------------

def scenarios(mod):
    """Run a fixed set of fixtures through `mod` (a loaded copy of the checker); name -> bool."""
    res = {}

    def case(name, expect_rc, expect_code=None, expect_text=None, **kw):
        with tempfile.TemporaryDirectory() as d:
            try:
                make_repo(d, **kw)
                rc, out = run(mod, d)
            except BaseException:   # a mutant that crashes is a failed scenario
                res[name] = False
                return
        codes = {ln.split()[1] for ln in out.splitlines() if ln.startswith("ERROR ")}
        ok = rc == expect_rc
        if expect_code is not None:
            ok = ok and expect_code in codes
        if expect_rc == 0:
            ok = ok and not codes
        if expect_text is not None:
            ok = ok and expect_text in out
        res[name] = ok

    case("clean", 0, studies=[study("A", "a.py;d/x.txt", "runs/r1/;d")])
    case("new_unresolved", 1, "UNRESOLVED", studies=[study("A", "a.py;zzz.py")])
    case("baselined", 0, studies=[study("A", "zzz.py")], baseline=[bl(S, "A", EP, "zzz.py")])
    case("stale", 1, "STALE_BASELINE", studies=[study("A", "a.py")], baseline=[bl(S, "A", EP, "a.py")])
    case("row_gone", 1, "BASELINE_GONE", studies=[study("A", "a.py")], baseline=[bl(S, "Z", EP, "m.py")])
    case("token_gone", 1, "BASELINE_GONE", studies=[study("A", "a.py")], baseline=[bl(S, "A", EP, "m.py")])
    case("semicolon_split", 1, "UNRESOLVED", studies=[study("A", "a.py;nothere.py")])
    case("space_token_checked", 1, "UNRESOLVED", studies=[study("A", "no such dir/")])
    case("space_dir_resolves", 0, studies=[study("A", "dir with space/")])
    case("prose_not_skipped", 1, "UNRESOLVED", studies=[study("A", "just some words")])
    case("glob_root_only", 1, "UNRESOLVED", studies=[study("A", "*_nothing.txt")], files=("a.py", "n/q_nothing.txt"))
    case("glob_match", 0, studies=[study("A", "*.py")])
    case("dir_prefix", 0, studies=[study("A", "d;runs/")])
    case("file_with_trailing_slash", 1, "UNRESOLVED", studies=[study("A", "a.py/")])
    case("duplicate_id", 1, "REGISTRY_BAD", studies=[study("A", "a.py"), study("A", "a.py")])
    case("bad_reason", 1, "BASELINE_BAD", studies=[study("A", "zzz.py")], baseline=[bl(S, "A", EP, "zzz.py", reason="")])
    case("duplicate_baseline", 1, "BASELINE_BAD", studies=[study("A", "zzz.py")],
         baseline=[bl(S, "A", EP, "zzz.py")] * 2)
    case("url_listed", 0, expect_text="NONPATH", studies=[study("A", "a.py;https://example.org/x")])
    case("untracked_unresolved", 1, "UNRESOLVED", studies=[study("A", "onlyondisk.py")], untracked=["onlyondisk.py"])
    case("supersession_authoritative", 1, "UNRESOLVED", sups=[sup("o.py", "nothere.py")])
    return res


def load_mutant(src, old, new):
    assert src.count(old) == 1, (old, src.count(old))
    mod = types.ModuleType("check_study_paths_mutant")
    mod.__file__ = SCRIPT
    exec(compile(src.replace(old, new), SCRIPT, "exec"), mod.__dict__)
    return mod


MUTANTS = [
    ("always_resolved", "        return t in self.dirs if dir_only else (t in self.files or t in self.dirs)\n", "        return True\n"),
    ("never_resolved", "        return t in self.dirs if dir_only else (t in self.files or t in self.dirs)\n", "        return False\n"),
    ("glob_always_resolves", '            return any(len(p) == len(rxs) and all(r.match(s) for r, s in zip(rxs, p)) for p in cands)',
     "            return True"),
    ("dirs_never_resolve", "        return t in self.dirs if dir_only else (t in self.files or t in self.dirs)\n", "        return t in self.files\n"),
    ("everything_baselined", '        if key in base:\n            s["baselined"] += 1\n        else:',
     '        if True:\n            s["baselined"] += 1\n        else:'),
    ("baseline_ignored", "    base = {e[:4]: e[4] for e in entries}\n", "    base = {}\n"),
    ("no_stale_check", '            if key in base:\n                findings.append(("STALE_BASELINE"',
     '            if False:\n                findings.append(("STALE_BASELINE"'),
    ("no_gone_check", "    for key in sorted(set(base) - present):\n", "    for key in []:\n"),
    ("tokenizer_no_semicolon", 'SEPARATOR_RE = re.compile(r";| \\+ ")', 'SEPARATOR_RE = re.compile(r" \\+ ")'),
    ("tokenizer_drops_spaced_tokens", '        if not tok:\n            out.append(("EMPTY", ""))',
     '        if " " in tok:\n            continue\n        if not tok:\n            out.append(("EMPTY", ""))'),
    ("url_pattern_matches_everything", 'r"^[A-Za-z][A-Za-z0-9+.-]*://\\S+$"', 'r"^.*$"'),
    ("glob_matches_any_depth", '            return any(len(p) == len(rxs) and all(r.match(s) for r, s in zip(rxs, p)) for p in cands)',
     '            return any(len(p) >= len(rxs) and all(r.match(s) for r, s in zip(rxs, p[-len(rxs):])) for p in cands)'),
    ("trailing_slash_accepts_files", "        return t in self.dirs if dir_only else (t in self.files or t in self.dirs)\n",
     "        return t in self.files or t in self.dirs\n"),
    ("no_duplicate_id_check", "                if rid in seen_ids:\n", "                if False:\n"),
    ("no_reason_check", '        elif not e["reason"].strip():', "        elif False:"),
    ("no_duplicate_baseline_check", "        elif key in seen:\n", "        elif False:\n"),
    ("exit_code_always_zero", "    return 1 if findings else 0\n\n\nif __name__", "    return 0\n\n\nif __name__"),
    ("untracked_files_count", '    r = subprocess.run(["git", "ls-files", "-z"], cwd=repo, capture_output=True)',
     '    r = subprocess.run(["git", "ls-files", "-z", "--others", "--cached"], cwd=repo, capture_output=True)'),
    ("supersessions_not_checked", '    ("registry/supersessions.csv", "superseded_target", ("authoritative_target",)),\n', ""),
]


class MutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCRIPT, encoding="utf-8") as f:
            cls.src = f.read()

    def test_unmutated_checker_passes_every_scenario(self):
        mod = load_mutant(self.src, "IN_GHA = ", "IN_GHA = ")
        res = scenarios(mod)
        self.assertEqual([k for k, v in res.items() if not v], [], res)
        self.assertGreaterEqual(len(res), 15)

    def test_every_mutant_is_caught_by_at_least_one_scenario(self):
        survivors = []
        for name, old, new in MUTANTS:
            res = scenarios(load_mutant(self.src, old, new))
            if all(res.values()):
                survivors.append(name)
        self.assertEqual(survivors, [], "mutants not detected by any scenario")

    def test_mutants_are_really_different(self):
        for name, old, new in MUTANTS:
            self.assertNotEqual(old, new, name)


if __name__ == "__main__":
    unittest.main()
