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


# ---- F1 clone-location guard: every case on throwaway repos under tmp_path, never on the real repository ----
import os  # noqa: E402
import subprocess  # noqa: E402

import pytest  # noqa: E402


def _mkrepo(path):
    path.mkdir(parents=True)
    (path / "f.txt").write_text("source\n")
    g = ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@localhost.invalid"]
    subprocess.run(g + ["init", "-q"], check=True)
    subprocess.run(g + ["add", "f.txt"], check=True)
    subprocess.run(g + ["commit", "-q", "-m", "x"], check=True)
    return path


def test_refuses_clone_equal_to_source_and_keeps_it(tmp_path):
    # the audit's reproduction: --repo <w>/clone --work <w> used to rmtree the source first
    src = _mkrepo(tmp_path / "w" / "clone")
    assert pmc.main(["--repo", str(src), "--work", str(tmp_path / "w"), "--target", "f.txt"]) == 2
    assert (src / "f.txt").read_text() == "source\n" and (src / ".git").is_dir()
    with pytest.raises(pmc.Refused, match="is the source repository"):
        pmc.prepare_clone(str(src), str(tmp_path / "w"))


def test_refuses_equal_via_symlinked_work(tmp_path):
    src = _mkrepo(tmp_path / "real" / "clone")
    os.symlink(tmp_path / "real", tmp_path / "alias")
    with pytest.raises(pmc.Refused, match="is the source repository"):
        pmc.prepare_clone(str(src), str(tmp_path / "alias"))
    assert (src / "f.txt").is_file()


def test_refuses_clone_inside_source(tmp_path):
    src = _mkrepo(tmp_path / "src")
    with pytest.raises(pmc.Refused, match="inside the source repository"):
        pmc.prepare_clone(str(src), str(src / "scratch"))
    assert not (src / "scratch").exists()


def test_refuses_source_inside_clone(tmp_path):
    src = _mkrepo(tmp_path / "w" / "clone" / "inner")
    with pytest.raises(pmc.Refused, match="inside the clone path"):
        pmc.prepare_clone(str(src), str(tmp_path / "w"))
    assert (src / "f.txt").is_file()


def test_refuses_to_delete_unmarked_existing_clone_dir(tmp_path):
    src = _mkrepo(tmp_path / "src")
    other = tmp_path / "w" / "clone"
    other.mkdir(parents=True)
    (other / "keep.txt").write_text("not ours\n")
    with pytest.raises(pmc.Refused, match="not a clone made by this tool"):
        pmc.prepare_clone(str(src), str(tmp_path / "w"))
    assert (other / "keep.txt").read_text() == "not ours\n"


def test_refuses_unmarked_git_repo_and_symlinked_clone(tmp_path):
    src = _mkrepo(tmp_path / "src")
    foreign = _mkrepo(tmp_path / "w" / "clone")          # a git repo, but no marker
    with pytest.raises(pmc.Refused):
        pmc.prepare_clone(str(src), str(tmp_path / "w"))
    assert (foreign / "f.txt").is_file()
    victim = _mkrepo(tmp_path / "victim")
    (victim / ".git" / pmc.CLONE_MARKER).write_text("forged\n")
    (tmp_path / "w2").mkdir()
    os.symlink(victim, tmp_path / "w2" / "clone")       # even a marked target is refused through a symlink
    with pytest.raises(pmc.Refused):
        pmc.prepare_clone(str(src), str(tmp_path / "w2"))
    assert (victim / "f.txt").is_file()


def test_marker_written_and_own_clone_replaced(tmp_path):
    src = _mkrepo(tmp_path / "src")
    root = pmc.prepare_clone(str(src), str(tmp_path / "w"))
    assert (root / ".git" / pmc.CLONE_MARKER).is_file() and (root / "f.txt").is_file()
    (root / "stale.txt").write_text("old run\n")
    root2 = pmc.prepare_clone(str(src), str(tmp_path / "w"))   # marked -> ours -> removed and re-cloned
    assert root2 == root and not (root / "stale.txt").exists()
    assert (root / ".git" / pmc.CLONE_MARKER).is_file()
    assert (src / "f.txt").read_text() == "source\n"


def test_missing_pytest_exits_2(tmp_path, monkeypatch):
    src = _mkrepo(tmp_path / "src")
    monkeypatch.setattr(pmc, "pytest_available", lambda py=None: False)
    assert pmc.main(["--repo", str(src), "--work", str(tmp_path / "w"), "--target", "f.txt"]) == 2
    assert not (tmp_path / "w").exists()


def test_ci_test_dirs_match_workflow():
    wf = (Path(pmc.REPO) / ".github/workflows/repo-checks.yml").read_text(encoding="utf-8")
    for d in pmc.CI_TEST_DIRS:
        assert d in wf
    for d in set(pmc.TEST_DIRS) - set(pmc.CI_TEST_DIRS):
        assert d not in wf, d
