#!/usr/bin/env python3
"""H3: hand-rolled, REPORT-ONLY Python mutation tester for the repo's checker scripts.

Truthfulness hardening plan (2026-11-20), item H3 + AGREED REVISION: stdlib only (ast), no mutmut, report only.
It is NOT a CI gate and is not wired into any workflow. research/engine_guards and the SHA-locked engine are out
of scope, and the tool never edits the working tree: every mutant is written into a scratch `git clone` of the
repository (default under /tmp) and that clone is reset (git checkout + git clean) after each mutant.
Clone-location guard (F1, 2026-11-20 audit): --repo and the clone path (<work>/clone) are realpath-resolved FIRST and
the run is refused (exit 2) when they are equal or either lies inside the other. An existing <work>/clone is deleted
only if it carries the marker file .git/H3_MUTATION_CLONE that this tool writes into every clone it creates;
anything else is refused (exit 2), never removed.

    unshare -rn python3 research/hardening/py_mutation_check.py --out /path/report.json   # all default targets
    python3 research/hardening/py_mutation_check.py --target tools/ci/check_modes.py --max-per-file 10

Operators (AST sites, replaced in the source text by position so formatting and comments elsewhere survive):
  CMP   == <-> !=, < <-> <=, > <-> >=, in <-> not in, is <-> is not
  BOOL  and <-> or            NOT   `not x` -> `x`
  CONST 0 <-> 1, n -> n + 1 (other ints), True <-> False
  RET   return True/False flipped, return 0/1 flipped (exit codes)
  DEL   `raise ...`, `<errors-like>.append(...)`, `sys.exit(...)` replaced by `pass`
  LOOP  continue <-> break
Sites inside f-strings are skipped. Mutants that do not compile are reported as `error` and excluded from the
kill rate. Per file at most --max-per-file mutants (default 40) are kept, sampled with random.Random(--seed)
when there are more (deterministic for a given source).

Kill signals per target, run in order inside the clone (first that fires wins):
  tests  the checker's own test files (found by grepping test dirs for the module name) must still pass;
  good   the checker run against the clean clone must still exit 0;
  bad    the checker run against a known-bad fixture applied to the clone must still exit non-zero.
Each signal is first checked on the UNMUTATED file (baseline); a signal whose baseline is wrong is dropped and
reported. Outcome per mutant: killed (by which signal), survived, timeout, error. A survivor is a candidate test
gap; deciding whether it is equivalent or a real gap is done by reading the code (see the report).
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PY = sys.executable

DEFAULT_TARGETS = [
    "tools/ci/check_artifact_pins.py", "tools/ci/check_current_inventory.py", "tools/ci/check_manifest.py",
    "tools/ci/check_modes.py", "tools/ci/check_pinned_restatement.py", "tools/ci/check_sha256sums.py",
    "tools/ci/check_study_paths.py", "tools/ci/hygiene_scan.py", "tools/ci/lint_claims.py",
    "audits/engineering/verify_inventory_current.py", "research/lean_gate/spec_results_line.py",
]
# CI_TEST_DIRS is exactly what .github/workflows/repo-checks.yml runs (2026-11-20): `unittest discover -s tools/ci/tests`
# and `pytest research/lean_gate/tests` (tests/ and tests_modular/ are engine/platform suites, not checker tests).
# The other dirs (incl. tools/redteam) are NOT run by CI; --ci-tests-only restricts the tests signal to CI_TEST_DIRS.
CI_TEST_DIRS = ["tools/ci/tests", "research/lean_gate/tests"]
TEST_DIRS = CI_TEST_DIRS + ["research/hardening/tests", "audits/engineering/tests", "tools/redteam"]
OUT_OF_SCOPE = ("research/engine_guards/", "aief_experiment_engine_v1.py", "Pinned/", "lean/AIEFProofs", "AIEFFreezeCore")

ERRORISH = re.compile(r"err|problem|fail|bad|issue|viol|missing|mismatch|stale|finding|unexpected|wrong", re.I)
CMP_FLIP = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE,
            ast.GtE: ast.Gt, ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Is: ast.IsNot, ast.IsNot: ast.Is}


@dataclasses.dataclass
class Mutant:
    mid: str
    op: str
    lineno: int
    desc: str
    source: str


def _offsets(src_bytes: bytes):
    starts, pos = [0], 0
    for line in src_bytes.splitlines(keepends=True):
        pos += len(line)
        starts.append(pos)
    return starts


def _replace(src: str, node: ast.AST, text: str) -> str:
    b = src.encode("utf-8")
    st = _offsets(b)
    s = st[node.lineno - 1] + node.col_offset
    e = st[node.end_lineno - 1] + node.end_col_offset
    return (b[:s] + text.encode("utf-8") + b[e:]).decode("utf-8")


def _paren(node: ast.AST) -> str:
    return "(" + ast.unparse(node) + ")"


def enumerate_mutants(src: str) -> list[Mutant]:
    """All mutants of a module source, deterministic order, duplicates (same resulting source) removed."""
    tree = ast.parse(src)
    in_fstring = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.JoinedStr):
            in_fstring.update(id(x) for x in ast.walk(n))
    docstrings = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body:
            f = n.body[0]
            if isinstance(f, ast.Expr) and isinstance(f.value, ast.Constant) and isinstance(f.value.value, str):
                docstrings.add(id(f.value))
    sites: list[tuple[int, int, str, str, str]] = []  # (line, col, op, desc, new_source)

    def add(node, op, desc, text):
        sites.append((node.lineno, node.col_offset, op, desc, _replace(src, node, text)))

    for n in ast.walk(tree):
        if id(n) in in_fstring or id(n) in docstrings or not hasattr(n, "lineno"):
            continue
        if isinstance(n, ast.Compare):
            for i, o in enumerate(n.ops):
                if type(o) in CMP_FLIP:
                    m = ast.Compare(left=n.left, ops=list(n.ops), comparators=n.comparators)
                    m.ops[i] = CMP_FLIP[type(o)]()
                    add(n, "CMP", f"{type(o).__name__} -> {CMP_FLIP[type(o)].__name__}", _paren(m))
        elif isinstance(n, ast.BoolOp):
            new = ast.Or() if isinstance(n.op, ast.And) else ast.And()
            add(n, "BOOL", f"{type(n.op).__name__} -> {type(new).__name__}", _paren(ast.BoolOp(op=new, values=n.values)))
        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not):
            add(n, "NOT", "drop not", _paren(n.operand))
        elif isinstance(n, ast.Constant):
            v = n.value
            if isinstance(v, bool):
                add(n, "CONST", f"{v} -> {not v}", repr(not v))
            elif isinstance(v, int):
                nv = {0: 1, 1: 0}.get(v, v + 1)
                add(n, "CONST", f"{v} -> {nv}", repr(nv))
        elif isinstance(n, ast.Return) and isinstance(n.value, ast.Constant) and type(n.value.value) in (bool, int) \
                and n.value.value in (0, 1):
            v = n.value.value
            nv = (not v) if isinstance(v, bool) else 1 - v
            add(n, "RET", f"return {v!r} -> return {nv!r}", f"return {nv!r}")
        elif isinstance(n, ast.Raise):
            add(n, "DEL", "delete raise", "pass")
        elif isinstance(n, ast.Expr) and isinstance(n.value, ast.Call):
            f = n.value.func
            if isinstance(f, ast.Attribute) and f.attr == "append" and ERRORISH.search(ast.unparse(f.value)):
                add(n, "DEL", f"delete {ast.unparse(f.value)}.append(...)", "pass")
            elif isinstance(f, ast.Attribute) and f.attr == "exit" and ast.unparse(f.value) == "sys":
                add(n, "DEL", "delete sys.exit(...)", "pass")
        elif isinstance(n, ast.Continue):
            add(n, "LOOP", "continue -> break", "break")
        elif isinstance(n, ast.Break):
            add(n, "LOOP", "break -> continue", "continue")
    sites.sort(key=lambda s: (s[0], s[1], s[2], s[3]))
    out, seen = [], {src}
    for line, col, op, desc, new in sites:
        if new in seen:
            continue
        seen.add(new)
        out.append(Mutant(mid=f"L{line}c{col}-{op}", op=op, lineno=line, desc=desc, source=new))
    # make ids unique
    cnt: dict[str, int] = {}
    for m in out:
        cnt[m.mid] = cnt.get(m.mid, 0) + 1
        if cnt[m.mid] > 1:
            m.mid += f"-{cnt[m.mid]}"
    return out


def sample(mutants: list[Mutant], cap: int, seed: int) -> list[Mutant]:
    if len(mutants) <= cap:
        return mutants
    idx = sorted(random.Random(seed).sample(range(len(mutants)), cap))
    return [mutants[i] for i in idx]


# ---------------------------------------------------------------------------------------------- signals

@dataclasses.dataclass
class Signal:
    name: str
    cmd: list[str]
    expect_zero: bool          # True: must exit 0 (tests, good); False: must exit non-zero (bad)
    fixture: object = None     # callable(root) applied before the command (bad runs)


def run_cmd(cmd, cwd, timeout, env):
    t = time.time()
    try:
        r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
        return r.returncode, time.time() - t, (r.stdout + r.stderr)[-2000:]
    except subprocess.TimeoutExpired:
        return None, time.time() - t, "TIMEOUT"


def find_tests(root: Path, rel: str, dirs=None) -> list[str]:
    stem = Path(rel).stem
    pat = re.compile(r"\b" + re.escape(stem) + r"\b")
    hits = []
    for d in dirs or TEST_DIRS:
        p = root / d
        if p.is_dir():
            for f in sorted(p.glob("test_*.py")):
                if pat.search(f.read_text(encoding="utf-8", errors="replace")):
                    hits.append(str(f.relative_to(root)))
    return hits


# Known-bad fixtures. Each mutates the scratch clone only; the clone is reset afterwards.
def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def fx_tamper_same_sha(root: Path):
    """Append a line to the first same_sha snapshot file (breaks snapshot pins and the current inventory)."""
    import csv
    with open(root / "registry/artifacts_current.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["container"] == "worktree" and r["snapshot_sha_state"] == "same_sha" and r["path"].endswith(".md"):
                with open(root / r["path"], "a", encoding="utf-8") as g:
                    g.write("\nH3 bad fixture\n")
                return
    raise RuntimeError("no same_sha .md file")


def fx_tamper_sync_script(root: Path):
    with open(root / "tools/sync/download_new.sh", "a", encoding="utf-8") as g:
        g.write("\n# H3 bad fixture\n")


def fx_tamper_restated(root: Path):
    d = root / "lean/AIEFGateCore/AIEFGateCore/Pinned"
    f = sorted(d.glob("*.lean"))[0]
    with open(f, "a", encoding="utf-8") as g:
        g.write("\n-- H3 bad fixture\n")


def fx_tamper_report(root: Path):
    with open(root / "AI Agent Audits/REPORT.md", "a", encoding="utf-8") as g:
        g.write("\nH3 bad fixture\n")


def fx_exec_bit_dropped(root: Path):
    f = "tools/sync/download_new.sh"  # on check_modes.KNOWN_EXECUTABLES
    os.chmod(root / f, 0o644)
    _git(root, "update-index", "--chmod=-x", f)


def fx_bad_status(root: Path):
    p = root / "registry/claims.csv"
    s = p.read_text(encoding="utf-8")
    p.write_text(s.replace(",Frozen,", ",Bogusstatus,", 1), encoding="utf-8")


def fx_secret_file(root: Path):
    (root / "h3_fixture.key").write_text("not a key\n", encoding="utf-8")
    _git(root, "add", "-f", "h3_fixture.key")  # *.key is gitignored; force it into the index


def fx_missing_study_path(root: Path):
    """Remove one registered study path from the tree (git rm), if the checker resolves study paths."""
    import csv
    with open(root / "registry/studies.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for v in r.values():
            for tok in re.split(r"[;,\s]+", v or ""):
                if tok and (root / tok).is_file() and tok.endswith(".py"):
                    _git(root, "rm", "-q", tok)
                    return
    raise RuntimeError("no study path file found")


def good_bad(rel: str) -> tuple[list[str], list[tuple[str, object]]]:
    """(good-run argv, [(fixture name, fixture)]) per target."""
    c = [PY, rel]
    table = {
        "tools/ci/check_artifact_pins.py": (c, [("tamper_same_sha", fx_tamper_same_sha)]),
        "tools/ci/check_current_inventory.py": (c, [("tamper_same_sha", fx_tamper_same_sha)]),
        "tools/ci/check_manifest.py": (c, [("tamper_report", fx_tamper_report)]),
        "tools/ci/check_modes.py": (c + ["--strict"], [("exec_bit_dropped", fx_exec_bit_dropped)]),
        "tools/ci/check_pinned_restatement.py": (c, [("tamper_restated", fx_tamper_restated)]),
        "tools/ci/check_sha256sums.py": (c, [("tamper_sync_script", fx_tamper_sync_script)]),
        "tools/ci/check_study_paths.py": (c, [("missing_study_path", fx_missing_study_path)]),
        "tools/ci/hygiene_scan.py": (c, [("secret_file", fx_secret_file)]),
        "tools/ci/lint_claims.py": (c, [("bad_status", fx_bad_status)]),
        "audits/engineering/verify_inventory_current.py": (c, [("tamper_same_sha", fx_tamper_same_sha)]),
    }
    return table.get(rel, (c, []))


# ---------------------------------------------------------------------------------------------- driver

CLONE_MARKER = "H3_MUTATION_CLONE"   # written into <clone>/.git/ (git clean never touches .git)


class Refused(Exception):
    """A clone location that could touch the source tree or a directory this tool did not create."""


def _inside(child: str, parent: str) -> bool:
    return child != parent and os.path.commonpath([child, parent]) == parent


def prepare_clone(repo: str, work: str) -> Path:
    """Resolve paths, refuse unsafe layouts, remove only a previous clone of OURS, then clone repo -> <work>/clone."""
    repo_r = os.path.realpath(repo)
    root_r = os.path.realpath(os.path.join(work, "clone"))
    if root_r == repo_r:
        raise Refused(f"clone path {root_r} is the source repository")
    if _inside(root_r, repo_r):
        raise Refused(f"clone path {root_r} is inside the source repository {repo_r}")
    if _inside(repo_r, root_r):
        raise Refused(f"source repository {repo_r} is inside the clone path {root_r}")
    root = Path(root_r)
    if os.path.lexists(root_r):
        if os.path.islink(os.path.join(work, "clone")) or not root.is_dir() \
                or not (root / ".git" / CLONE_MARKER).is_file():
            raise Refused(f"{root_r} exists and is not a clone made by this tool (no .git/{CLONE_MARKER}); "
                          f"not deleting it")
        shutil.rmtree(root_r)
    os.makedirs(os.path.dirname(root_r), exist_ok=True)
    subprocess.run(["git", "clone", "-q", "--local", repo_r, root_r], check=True)
    (root / ".git" / CLONE_MARKER).write_text("created by research/hardening/py_mutation_check.py\n", encoding="utf-8")
    return root


def pytest_available(py: str = None) -> bool:
    return subprocess.run([py or PY, "-c", "import pytest"], capture_output=True).returncode == 0


def reset_clone(root: Path):
    subprocess.run(["git", "-C", str(root), "checkout", "-q", "-f", "--", "."], check=True)
    subprocess.run(["git", "-C", str(root), "reset", "-q"], check=True)
    subprocess.run(["git", "-C", str(root), "checkout", "-q", "-f", "--", "."], check=True)
    subprocess.run(["git", "-C", str(root), "clean", "-fdxq"], check=True)


# Targets whose good/bad runs hash every tracked file through registry/artifacts_current.csv. Writing a mutant
# into the clone changes the checker's own bytes, so the inventory would flag the mutated file itself and every
# mutant would be "killed" for a reason unrelated to its logic (found in the first 2026-11-20 run: 35/40 vacuous
# kills of verify_inventory_current.py). For these the inventory is regenerated after writing each mutant, i.e.
# the mutant is judged as if it had been committed together with a fresh inventory.
REFRESH_INVENTORY = {"tools/ci/check_current_inventory.py", "audits/engineering/verify_inventory_current.py"}
INVENTORY_BUILDER = "registry/reconciliation/build_current_inventory.py"


def refresh_inventory(root: Path, env):
    subprocess.run([PY, INVENTORY_BUILDER], cwd=root, env=env, check=True, capture_output=True)


def evaluate(root: Path, rel: str, signals: list[Signal], timeout: float, env, reset, apply=None
             ) -> tuple[str, str, str]:
    """Run signals in order on the file currently in root. Returns (outcome, signal, tail).
    apply() re-applies the mutant (and any inventory refresh) after a fixture's reset."""
    for s in signals:
        if s.fixture is not None:
            s.fixture(root)
        rc, _, tail = run_cmd(s.cmd, root, timeout, env)
        if s.fixture is not None:
            reset()
            if apply is not None:
                apply()
        if rc is None:
            return "timeout", s.name, tail
        ok = (rc == 0) if s.expect_zero else (rc != 0)
        if not ok:
            return "killed", s.name, tail
    return "survived", "", ""


def run_target(root: Path, rel: str, signals: list[Signal], cap: int, seed: int, timeout: float, env,
               reset, log=print, only_ids=None) -> dict:
    path = root / rel
    original = path.read_bytes()
    refresh = rel in REFRESH_INVENTORY and (root / INVENTORY_BUILDER).is_file()
    res = {"target": rel, "signals": [], "dropped_signals": [], "mutants": []}
    # baseline: every signal must give its expected result on the unmutated file
    kept = []
    for s in signals:
        if s.fixture is not None:
            try:
                s.fixture(root)
            except Exception as e:  # fixture not applicable
                reset()
                res["dropped_signals"].append({"signal": s.name, "why": f"fixture error: {e}"})
                continue
        rc, dt, tail = run_cmd(s.cmd, root, timeout, env)
        if s.fixture is not None:
            reset()
        ok = rc is not None and ((rc == 0) if s.expect_zero else (rc != 0))
        if ok:
            kept.append(s)
            res["signals"].append({"signal": s.name, "baseline_rc": rc, "seconds": round(dt, 1)})
        else:
            res["dropped_signals"].append({"signal": s.name, "why": f"baseline rc={rc}", "tail": tail[-400:]})
            print(f"WARNING: {rel}: signal '{s.name}' DROPPED (baseline rc={rc}); its kills are not counted",
                  file=sys.stderr)
    src = original.decode("utf-8")
    allm = enumerate_mutants(src)
    chosen = sample(allm, cap, seed)
    if only_ids is not None:  # rescore mode: re-run just these mutant ids (e.g. a previous run's survivors)
        chosen = [m for m in chosen if m.mid in only_ids]
    res["n_sites"] = len(allm)
    log(f"{rel}: {len(allm)} mutants, running {len(chosen)}; signals {[s.name for s in kept]}")
    try:
        for m in chosen:
            try:
                compile(m.source, rel, "exec")
            except SyntaxError as e:
                out = ("error", "", f"SyntaxError {e}")
            else:
                def apply(m=m):
                    path.write_text(m.source, encoding="utf-8")
                    if refresh:
                        refresh_inventory(root, env)
                apply()
                out = evaluate(root, rel, kept, timeout, env, reset, apply) if kept else ("error", "", "no signals")
                path.write_bytes(original)
                reset()
            line = src.splitlines()[m.lineno - 1].strip()
            res["mutants"].append({"id": m.mid, "op": m.op, "line": m.lineno, "desc": m.desc, "code": line[:160],
                                   "outcome": out[0], "killed_by": out[1]})
            log(f"  {m.mid:22s} {m.desc:34s} {out[0]:8s} {out[1]}")
    finally:
        path.write_bytes(original)
        reset()
    k = sum(x["outcome"] == "killed" for x in res["mutants"])
    sv = sum(x["outcome"] == "survived" for x in res["mutants"])
    res["killed"], res["survived"] = k, sv
    res["timeout"] = sum(x["outcome"] == "timeout" for x in res["mutants"])
    res["error"] = sum(x["outcome"] == "error" for x in res["mutants"])
    # One denominator (N2): a timeout is DETECTED (the mutant hangs a signal); errors (non-compiling) are excluded.
    # detected_rate = (killed + timeout) / (killed + timeout + survived).
    det = k + res["timeout"]
    res["detected"] = det
    res["kill_rate"] = round(det / (det + sv), 3) if det + sv else None
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(REPO), help="source repository to clone (never modified)")
    ap.add_argument("--work", default=None, help="scratch dir for the clone (default: a new temp dir)")
    ap.add_argument("--target", action="append", help="repo-relative file (repeatable); default: the checkers")
    ap.add_argument("--max-per-file", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20261120)
    ap.add_argument("--timeout", type=float, default=300.0, help="seconds per signal run")
    ap.add_argument("--out", default=None, help="write the JSON report here")
    ap.add_argument("--ci-tests-only", action="store_true", help="use only test dirs that CI runs (no tools/redteam)")
    ap.add_argument("--rescore", default=None, help="previous JSON report: re-run only its survivors")
    ap.add_argument("--tests-only", action="store_true",
                    help="only the tests signal (for --rescore: good/bad runs are deterministic and already ran)")
    a = ap.parse_args(argv)
    targets = a.target or DEFAULT_TARGETS
    for t in targets:
        if any(x in t for x in OUT_OF_SCOPE):
            print(f"refusing out-of-scope target {t}", file=sys.stderr)
            return 2
    if not pytest_available():
        print(f"ERROR: {PY} cannot import pytest; the tests signal would be silently dropped. "
              f"Run with an interpreter that has pytest.", file=sys.stderr)
        return 2
    work = Path(a.work or tempfile.mkdtemp(prefix="h3_mut_"))
    try:
        root = prepare_clone(a.repo, str(work))
    except Refused as e:
        print(f"ERROR: refusing: {e}", file=sys.stderr)
        return 2
    gcfg = work / "gitconfig"
    gcfg.write_text("[user]\n\tname = H3 mutation clone\n\temail = h3@localhost.invalid\n", encoding="utf-8")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_CONFIG_GLOBAL=str(gcfg), GITHUB_ACTIONS="")
    env.pop("AIEF_MUT_ONLY", None)
    reset = lambda: reset_clone(root)  # noqa: E731
    report = {"repo_head": subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                                          text=True).stdout.strip(),
              "seed": a.seed, "max_per_file": a.max_per_file, "timeout": a.timeout, "ci_tests_only": a.ci_tests_only,
              "argv": list(sys.argv[1:] if argv is None else argv), "python": PY, "targets": []}
    prev = None
    if a.rescore:
        prev = {t["target"]: {m["id"] for m in t.get("mutants", []) if m["outcome"] == "survived"}
                for t in json.loads(Path(a.rescore).read_text(encoding="utf-8"))["targets"]}
        targets = [t for t in targets if prev.get(t)]
    for rel in targets:
        if not (root / rel).is_file():
            report["targets"].append({"target": rel, "skipped": "not in tree"})
            print(f"{rel}: not in tree, skipped")
            continue
        tests = find_tests(root, rel, CI_TEST_DIRS if a.ci_tests_only else TEST_DIRS)
        sigs = []
        if tests:
            sigs.append(Signal("tests", [PY, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *tests], True))
        good, bads = good_bad(rel)
        if not a.tests_only:
            sigs.append(Signal("good", good, True))
            for name, fx in bads:
                sigs.append(Signal("bad:" + name, good, False, fx))
        r = run_target(root, rel, sigs, a.max_per_file, a.seed, a.timeout, env, reset,
                       only_ids=None if prev is None else prev[rel])
        r["tests"] = tests
        report["targets"].append(r)
        if a.out:
            Path(a.out).write_text(json.dumps(report, indent=1), encoding="utf-8")
    tot = {k: sum(t.get(k, 0) for t in report["targets"]) for k in ("killed", "survived", "timeout", "error")}
    det = tot["killed"] + tot["timeout"]
    tot["detected_rate"] = round(det / (det + tot["survived"]), 3) if det + tot["survived"] else None
    report["totals"] = tot
    if a.out:
        Path(a.out).write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("TOTALS", tot)
    return 0  # report-only: never fails on survivors


if __name__ == "__main__":
    sys.exit(main())
