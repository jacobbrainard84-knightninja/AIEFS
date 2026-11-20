#!/usr/bin/env python3
"""H7 (truthfulness hardening): write the SPEC "Results" sentence from the run logs instead of by hand.

Usage:
  python3 research/lean_gate/spec_results_line.py --mut MUTATION_LOG [--gate GATE_SUMMARY] [--pytest N]

MUTATION_LOG is the stdout of a full unfiltered `lean_mutation_check.py` run; GATE_SUMMARY is the summary.txt that
`check_lean_gate.sh` writes under .check_logs/<utc>/. The script only reads the summary lines and refuses to print a
PASS sentence when any count is short (k < n), RESULT is not PASS, the run was filtered (AIEF_MUT_ONLY), or the gate
was run with warnings; it states those facts instead. A gate run on a dirty tree is reported as
`<sha> plus N uncommitted files`, never as the bare sha. It never runs Lean or the mutation check itself.
"""
import argparse
import re
import sys

MUT_PATTERNS = {
    "statement": r"^statement mutants rejected: (\d+)/(\d+)(?:; flagged with a name-reference/parse error line: (\d+))?",
    "definition": r"^definition mutants killed: (\d+)/(\d+)",
    "total": r"^mutants rejected in total: (\d+)/(\d+)",
    "equivalence": r"^equivalence controls not killed: (\d+)/(\d+)",
    "typo": r"^typo controls flagged invalid: (\d+)/(\d+)",
}


class LogError(ValueError):
    pass


def parse_mutation_log(text):
    out = {}
    for key, pat in MUT_PATTERNS.items():
        hits = re.findall(pat, text, re.M)
        if len(hits) != 1:
            raise LogError(f"expected exactly one '{key}' summary line, found {len(hits)}")
        h = hits[0]
        out[key] = (int(h[0]), int(h[1]))
        if key == "statement":
            out["name_ref_notes"] = int(h[2]) if h[2] else 0
    res = re.findall(r"^RESULT: (\w+)", text, re.M)
    if len(res) != 1:
        raise LogError(f"expected exactly one RESULT line, found {len(res)}")
    out["result"] = res[0]
    out["filtered"] = "AIEF_MUT_ONLY" in text
    s, d, t = out["statement"], out["definition"], out["total"]
    if s[1] + d[1] != t[1] or s[0] + d[0] != t[0]:
        raise LogError(f"statement {s} + definition {d} != total {t}")
    return out


def parse_gate_summary(text):
    head = re.search(r"^git HEAD: ([0-9a-f]{40})\s+dirty_files: (\d+)", text, re.M)
    decls = re.search(r"AUDITED (\d+) project declarations", text)
    warn = re.search(r"warnings=(\d+)", text)
    res = re.search(r"^RESULT: (\w+)", text, re.M)
    if not (head and decls and warn and res):
        raise LogError("gate summary is missing the git HEAD, declaration count, warnings or RESULT line")
    return {"head": head.group(1), "dirty": int(head.group(2)), "decls": int(decls.group(1)),
            "warnings": int(warn.group(1)), "result": res.group(1)}


def problems(mut, gate=None):
    p = []
    for key in ("statement", "definition", "total", "equivalence", "typo"):
        k, n = mut[key]
        if k != n:
            p.append(f"{key} {k}/{n}")
    if mut["result"] != "PASS":
        p.append(f"mutation RESULT {mut['result']}")
    if mut["filtered"]:
        p.append("filtered run (AIEF_MUT_ONLY)")
    if gate is not None:
        if gate["result"] != "PASS":
            p.append(f"gate RESULT {gate['result']}")
        if gate["warnings"]:
            p.append(f"gate warnings={gate['warnings']}")
    return p


def results_line(mut, gate=None, pytest_passed=None):
    bad = problems(mut, gate)
    if bad:
        return "NOT A PASS: " + "; ".join(bad) + "."
    s, d, t, e, y = (mut[k] for k in ("statement", "definition", "total", "equivalence", "typo"))
    parts = []
    if gate is not None:
        where = f"`{gate['head'][:7]}`" + (f" plus {gate['dirty']} uncommitted files" if gate["dirty"] else "")
        parts.append(f"Gate PASS at {where}, 0 warnings, **{gate['decls']} declarations**, "
                     "standard axioms only.")
    note = (f" ({mut['name_ref_notes']} flagged with a name-reference/parse error line)"
            if mut["name_ref_notes"] else "")
    parts.append(f"Full unfiltered mutation run: **{s[0]}/{s[1]} statement** mutants rejected{note}, "
                 f"**{d[0]}/{d[1]} definition** mutants killed, **{t[0]}/{t[1]} total**, {e[0]}/{e[1]} equivalence "
                 f"controls not killed, {y[0]}/{y[1]} typo controls flagged invalid, RESULT PASS.")
    if pytest_passed is not None:
        parts.append(f"pytest {pytest_passed} passed.")
    return " ".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mut", required=True)
    ap.add_argument("--gate")
    ap.add_argument("--pytest", type=int)
    a = ap.parse_args(argv)
    with open(a.mut, encoding="utf-8") as f:
        mut = parse_mutation_log(f.read())
    gate = None
    if a.gate:
        with open(a.gate, encoding="utf-8") as f:
            gate = parse_gate_summary(f.read())
    line = results_line(mut, gate, a.pytest)
    print(line)
    return 1 if line.startswith("NOT A PASS") else 0


if __name__ == "__main__":
    sys.exit(main())
