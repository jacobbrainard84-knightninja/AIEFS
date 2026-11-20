"""Negative control for research/hardening/py_mutation_check.py (H3): on a tiny fixture module, a weak test
must let a boundary mutant SURVIVE and a strong test must KILL every mutant; the fixture file must be restored."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import py_mutation_check as pmc  # noqa: E402

MOD = "def is_positive(x):\n    return x > 0\n"
WEAK = "from mod_under_test import is_positive\n\ndef test_weak():\n    assert is_positive(5)\n"
STRONG = ("from mod_under_test import is_positive\n\ndef test_strong():\n"
          "    assert is_positive(1) and is_positive(5)\n    assert not is_positive(0) and not is_positive(-1)\n")


def _setup(tmp_path, test_src):
    (tmp_path / "mod_under_test.py").write_text(MOD)
    (tmp_path / "test_fixture.py").write_text(test_src)
    sig = pmc.Signal("tests", [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_fixture.py"], True)
    env = dict(__import__("os").environ, PYTHONDONTWRITEBYTECODE="1")
    return pmc.run_target(tmp_path, "mod_under_test.py", [sig], 40, 1, 60, env, lambda: None, log=lambda *a: None)


def test_weak_test_leaves_boundary_survivor(tmp_path):
    r = _setup(tmp_path, WEAK)
    by = {m["desc"]: m["outcome"] for m in r["mutants"]}
    assert by["Gt -> GtE"] == "survived"          # 5 >= 0 still true: the weak test cannot see the boundary
    assert by["0 -> 1"] == "survived"             # 5 > 1 still true
    assert r["survived"] >= 2 and r["kill_rate"] < 1
    assert (tmp_path / "mod_under_test.py").read_text() == MOD


def test_strong_test_kills_every_mutant(tmp_path):
    r = _setup(tmp_path, STRONG)
    assert r["mutants"] and all(m["outcome"] == "killed" for m in r["mutants"]), r["mutants"]
    assert r["kill_rate"] == 1.0
    assert (tmp_path / "mod_under_test.py").read_text() == MOD


def test_operator_coverage_and_determinism():
    src = ("import sys\nerrors = []\n"
           "def f(a, b):\n    if a == b and not a:\n        errors.append(1)\n        raise ValueError\n"
           "    for _ in range(2):\n        if a < b or a is None:\n            continue\n        break\n"
           "    if errors:\n        sys.exit(1)\n    return True\n")
    ms = pmc.enumerate_mutants(src)
    assert {m.op for m in ms} == {"CMP", "BOOL", "NOT", "CONST", "RET", "DEL", "LOOP"}
    for m in ms:
        compile(m.source, "x", "exec")
    assert [m.source for m in pmc.enumerate_mutants(src)] == [m.source for m in ms]
    assert [m.mid for m in pmc.sample(ms, 5, 7)] == [m.mid for m in pmc.sample(ms, 5, 7)]


def test_refuses_out_of_scope_targets():
    assert pmc.main(["--target", "aief_experiment_engine_v1.py"]) == 2
    assert pmc.main(["--target", "research/engine_guards/x.py"]) == 2
