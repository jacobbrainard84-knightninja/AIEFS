"""H7 (truthfulness hardening): SPEC/README claims about the mutation suite must match the code.

1. Every mutant number M<k> named in SPEC_P1_gate_identities.md, lean/AIEFGateCore/README.md or the docstring of
   lean_mutation_check.py (singly or as a range M<a>-M<b>) exists in MUTANTS + DEF_MUTANTS (no phantom mutant).
2. Every mutant in the code is documented in the SPEC and the README (no undocumented mutant).
3. The LATEST results sentence in the SPEC (the last occurrence of each "k/n statement|definition|total|equivalence
   controls|typo controls" count) states k == n == the size of the corresponding list in the code. A new mutant added
   without a new results sentence fails here.
4. spec_results_line.py writes the results sentence from logs and refuses to call a short, failed or filtered run a
   pass; a dirty-tree gate run is reported as "<sha> plus N uncommitted files".
"""
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
import lean_mutation_check as mc  # noqa: E402
import spec_results_line as srl  # noqa: E402

SPEC = (HERE.parent / "SPEC_P1_gate_identities.md").read_text(encoding="utf-8")
README = (REPO / "lean" / "AIEFGateCore" / "README.md").read_text(encoding="utf-8")
MC_DOC = mc.__doc__ or ""


def _nums(lst):
    return {int(m[0].split("_")[0][1:]) for m in lst}


CODE = _nums(mc.MUTANTS) | _nums(mc.DEF_MUTANTS)


def _named(text):
    single = {int(x) for x in re.findall(r"\bM(\d+)\b", text)}
    ranged = set()
    for a, b in re.findall(r"\bM(\d+)\s*(?:–|-|to)\s*M?(\d+)\b", text):
        assert int(a) <= int(b), f"backwards range M{a}-M{b}"
        ranged |= set(range(int(a), int(b) + 1))
    return single, ranged


def test_code_numbering_is_contiguous():
    assert len(CODE) == len(mc.MUTANTS) + len(mc.DEF_MUTANTS)          # no duplicate numbers
    assert CODE == set(range(1, max(CODE) + 1))


@pytest.mark.parametrize("name,text", [("SPEC", SPEC), ("README", README), ("lean_mutation_check docstring", MC_DOC)])
def test_no_phantom_mutants(name, text):
    single, ranged = _named(text)
    assert not (single | ranged) - CODE, f"{name} names mutants not in the code: {sorted((single | ranged) - CODE)}"


@pytest.mark.parametrize("name,text", [("SPEC", SPEC), ("README", README)])
def test_no_undocumented_mutants(name, text):
    single, ranged = _named(text)
    assert not CODE - (single | ranged), f"{name} never mentions {sorted(CODE - (single | ranged))}"


LATEST = {
    "statement": (r"(\d+)/(\d+) statement", len(mc.MUTANTS)),
    "definition": (r"(\d+)/(\d+) definition", len(mc.DEF_MUTANTS)),
    "total": (r"(\d+)/(\d+) total", len(mc.MUTANTS) + len(mc.DEF_MUTANTS)),
    "equivalence": (r"(\d+)/(\d+) equivalence controls not killed", len(mc.EQUIV_CONTROLS)),
    "typo": (r"(\d+)/(\d+) typo controls", len(mc.TYPO_CONTROLS)),
}


@pytest.mark.parametrize("key", list(LATEST))
def test_latest_spec_results_match_code(key):
    pat, n = LATEST[key]
    hits = re.findall(pat, SPEC.replace("**", ""))
    assert hits, key
    k, m = map(int, hits[-1])
    assert k == m == n, f"latest SPEC {key} result {k}/{m}, code has {n}"


MUT_LOG = """CONTROL unmutated EmaRadialRef.lean: rc=0 errors=0 -> PASS
statement mutants rejected: 84/84; flagged with a name-reference/parse error line: 1
definition mutants killed: 61/61
mutants rejected in total: 145/145
equivalence controls not killed: 21/21
typo controls flagged invalid: 4/4
RESULT: PASS
"""
GATE = """check_lean_gate.sh  project=AIEFGateCore  utc=20261120T164743Z
git HEAD: ea96f55c8ef9d27cd34af4472c239b58f002dca0  dirty_files: 0
PASS step 5: Build completed successfully (2342 jobs); warnings=0
PASS step 7: AUDITED 979 project declarations; allowed: propext Classical.choice Quot.sound
RESULT: PASS (logs in somewhere)
"""


def test_results_line_exact():
    line = srl.results_line(srl.parse_mutation_log(MUT_LOG), srl.parse_gate_summary(GATE), 381)
    assert line == (
        "Gate PASS at `ea96f55`, 0 warnings, **979 declarations**, standard axioms only. Full unfiltered mutation run: "
        "**84/84 statement** mutants rejected (1 flagged with a name-reference/parse error line), **61/61 definition** "
        "mutants killed, **145/145 total**, 21/21 equivalence controls not killed, 4/4 typo controls flagged invalid, "
        "RESULT PASS. pytest 381 passed.")


def test_dirty_gate_is_disclosed():
    g = srl.parse_gate_summary(GATE.replace("dirty_files: 0", "dirty_files: 2"))
    assert "`ea96f55` plus 2 uncommitted files" in srl.results_line(srl.parse_mutation_log(MUT_LOG), g)


@pytest.mark.parametrize("old,new,why", [
    ("definition mutants killed: 61/61", "definition mutants killed: 60/61", "definition 60/61"),
    ("RESULT: PASS", "RESULT: FAIL", "mutation RESULT FAIL"),
    ("equivalence controls not killed: 21/21", "equivalence controls not killed: 20/21", "equivalence 20/21"),
])
def test_short_or_failed_run_is_not_a_pass(old, new, why):
    log = MUT_LOG.replace(old, new)
    if "60/61" in new:
        log = log.replace("145/145", "144/145")
    line = srl.results_line(srl.parse_mutation_log(log))
    assert line.startswith("NOT A PASS") and why in line


def test_filtered_run_and_gate_warnings_are_not_a_pass():
    assert "filtered" in srl.results_line(srl.parse_mutation_log("AIEF_MUT_ONLY=M14\n" + MUT_LOG))
    g = srl.parse_gate_summary(GATE.replace("warnings=0", "warnings=3"))
    assert srl.results_line(srl.parse_mutation_log(MUT_LOG), g).startswith("NOT A PASS: gate warnings=3")


@pytest.mark.parametrize("bad", [
    MUT_LOG.replace("mutants rejected in total: 145/145", "mutants rejected in total: 146/146"),   # sum mismatch
    MUT_LOG.replace("typo controls flagged invalid: 4/4\n", ""),                                    # line missing
    MUT_LOG + "RESULT: PASS\n",                                                                   # two results
])
def test_malformed_logs_raise(bad):
    with pytest.raises(srl.LogError):
        srl.parse_mutation_log(bad)


def test_cli_exit_codes(tmp_path):
    ok, bad = tmp_path / "ok.log", tmp_path / "bad.log"
    ok.write_text(MUT_LOG)
    bad.write_text(MUT_LOG.replace("RESULT: PASS", "RESULT: FAIL"))
    assert srl.main(["--mut", str(ok)]) == 0 and srl.main(["--mut", str(bad)]) == 1
