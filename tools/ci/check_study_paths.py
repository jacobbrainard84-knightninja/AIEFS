#!/usr/bin/env python3
"""Study-registry path check: every path a registry row names must exist in the tree, or be baselined.

Plain Python 3 standard library plus the `git` command. Run from the repository root:

    python3 tools/ci/check_study_paths.py
    python3 tools/ci/check_study_paths.py --repo PATH [--baseline FILE]
    python3 tools/ci/check_study_paths.py --print-baseline      # JSON of the current unresolved tokens (review aid)

What is checked (CHECKED_FIELDS; the row id is the value of the id column):

    registry/studies.csv        canonical_entrypoints, canonical_evidence_paths     id: study_id
    registry/supersessions.csv  authoritative_target                                id: superseded_target

`supersessions.csv:superseded_target` is NOT checked: a superseded thing is allowed to be gone (it is the
retired one); the authoritative target is the claim that something exists. `rationale` and the other
columns are prose and are not read.

Tokenizer (TOKENIZER; applied identically to every checked field, nothing is dropped silently):

  1. The field is split at every `;`, then each piece at every ` + ` (space, plus, space).
  2. Each piece is stripped of leading/trailing whitespace and of a leading `./`. Whitespace INSIDE a
     piece is kept (`aief_1_4_intertwining_controller 02/` is one real directory name).
     Empty pieces (a trailing `;`) are counted and listed as EMPTY, not checked.
  3. A piece matching an ALLOWED_NON_PATH pattern is not a path: it is listed as NONPATH and not
     resolved. The only allowed pattern today is a URL (`scheme://...`). Anything else, including prose
     such as `9 sibling 20-seed reruns`, is treated as a path and must resolve or be baselined.
  4. Paths are repository-root-relative and case-sensitive (no `..` or absolute paths: those never
     resolve). Commas are NOT separators.

Resolution (against `git ls-files`, i.e. the tracked tree; untracked or ignored files do not count):

  * a token resolves if it is a tracked file or a tracked directory (a prefix of a tracked path); a token
    ending in `/` must be a directory;
  * a token containing `*` or `?` is a glob, matched segment by segment at the repository root: `*` and
    `?` never match `/`, there is no `**`, `[` is literal. A glob resolves if some tracked file or
    directory matches all its segments. So `aief_1_4_*_report.txt` matches root-level files only.

Baseline (tools/ci/study_paths_baseline.json): the known-unresolved tokens, each with file, row_id, field,
token and a reason. Replacing or restoring a missing path is an owner/provenance decision, so the checker
never rewrites registry CSVs; it only stops the debt from growing silently. Findings (ERROR, exit 1):

  UNRESOLVED        a token does not resolve and is not baselined
  STALE_BASELINE    a baselined token now resolves: delete its baseline entry
  BASELINE_GONE     a baseline entry's file, row, field or token no longer exists (row_id / field / token
                    in the registry): delete or update the entry
  BASELINE_BAD      the baseline is unreadable, malformed, has a duplicate entry, an empty reason, or names
                    a file / field that is not checked
  REGISTRY_BAD      a checked CSV is missing or untracked, lacks a checked column, or has duplicate row ids

Exit status: 0 = pass, 1 = at least one ERROR, 2 = usage / read error.

Checker isolation (same class as check_sha256sums.py S-B1): run as a script, this file first re-executes
itself as `python -I -B`, so a committed tools/ci/csv.py (or re.py, json.py ...) cannot run inside it.
"""
import sys as _sys
if __name__ == "__main__" and not _sys.flags.isolated:
    import os as _os
    _os.execv(_sys.executable, [_sys.executable, "-I", "-B", _os.path.abspath(__file__)] + _sys.argv[1:])
import argparse
import csv
import json
import os
import re
import subprocess
import sys

IN_GHA = os.environ.get("GITHUB_ACTIONS") == "true"
DEFAULT_BASELINE = os.path.join("tools", "ci", "study_paths_baseline.json")
BASELINE_REASON = "unresolved at 871417d; replacement is an owner/provenance decision"

# (csv file, id column, checked fields)
CHECKED_FIELDS = (
    ("registry/studies.csv", "study_id", ("canonical_entrypoints", "canonical_evidence_paths")),
    ("registry/supersessions.csv", "superseded_target", ("authoritative_target",)),
)
SEPARATOR_RE = re.compile(r";| \+ ")
TOKENIZER = "split at ';' and ' + ', strip whitespace and a leading './', keep inner whitespace, commas are not separators"
# Pieces that are not paths. Each must be named here; everything else is a path.
ALLOWED_NON_PATH = (
    ("URL", re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://\S+$")),
)
MAX_LISTED = 40


# ---- tokenizer -----------------------------------------------------------------------------------------

def tokenize(value):
    """Return [(kind, token)] for a field value; kind is PATH, EMPTY or the name of an ALLOWED_NON_PATH."""
    out = []
    for piece in SEPARATOR_RE.split(value):
        tok = piece.strip()
        while tok.startswith("./"):
            tok = tok[2:].lstrip()
        if not tok:
            out.append(("EMPTY", ""))
            continue
        for name, rx in ALLOWED_NON_PATH:
            if rx.match(tok):
                out.append((name, tok))
                break
        else:
            out.append(("PATH", tok))
    return out


# ---- resolution ----------------------------------------------------------------------------------------

class Tree:
    """The tracked tree: files and every directory prefix."""

    def __init__(self, files):
        self.files = set(files)
        self.dirs = set()
        for f in self.files:
            parts = f.split("/")
            for i in range(1, len(parts)):
                self.dirs.add("/".join(parts[:i]))
        self._split_dirs = [d.split("/") for d in self.dirs]
        self._split = [f.split("/") for f in self.files] + self._split_dirs

    @staticmethod
    def _seg_regex(seg):
        return re.compile("".join("[^/]*" if c == "*" else "[^/]" if c == "?" else re.escape(c) for c in seg) + r"\Z")

    def resolves(self, token):
        dir_only = token.endswith("/")
        t = token[:-1] if dir_only else token
        if not t:
            return False
        if "*" in t or "?" in t:
            rxs = [self._seg_regex(s) for s in t.split("/")]
            cands = self._split_dirs if dir_only else self._split
            return any(len(p) == len(rxs) and all(r.match(s) for r, s in zip(rxs, p)) for p in cands)
        return t in self.dirs if dir_only else (t in self.files or t in self.dirs)


def tracked_files(repo):
    r = subprocess.run(["git", "ls-files", "-z"], cwd=repo, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git ls-files failed: " + r.stderr.decode("utf-8", "replace").strip())
    return [p for p in r.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


# ---- registry ------------------------------------------------------------------------------------------

def read_registry(repo, tree):
    """Return (tokens, notes, errors). tokens: {(file,row_id,field,token): kind-less}, in file order."""
    tokens, nonpath, empties, errors, rows_seen = [], [], [], [], {}
    for rel, id_col, fields in CHECKED_FIELDS:
        path = os.path.join(repo, rel)
        if rel not in tree.files or not os.path.isfile(path):
            errors.append(("REGISTRY_BAD", f"{rel} is absent or not tracked"))
            continue
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames or []
            missing = [c for c in (id_col,) + tuple(fields) if c not in header]
            if missing:
                errors.append(("REGISTRY_BAD", f"{rel}: missing column(s) {missing}"))
                continue
            seen_ids = {}
            for line_no, row in enumerate(reader, start=2):
                rid = (row[id_col] or "").strip()
                if not rid:
                    errors.append(("REGISTRY_BAD", f"{rel}:{line_no}: empty {id_col}"))
                    continue
                if rid in seen_ids:
                    errors.append(("REGISTRY_BAD", f"{rel}:{line_no}: duplicate {id_col} {rid!r} "
                                                   f"(first at line {seen_ids[rid]})"))
                    continue
                seen_ids[rid] = line_no
                rows_seen[(rel, rid)] = line_no
                for field in fields:
                    for kind, tok in tokenize(row[field] or ""):
                        if kind == "PATH":
                            tokens.append((rel, rid, field, tok, line_no))
                        elif kind == "EMPTY":
                            empties.append((rel, rid, field, line_no))
                        else:
                            nonpath.append((rel, rid, field, tok, kind, line_no))
    return tokens, nonpath, empties, errors, rows_seen


def load_baseline(path):
    """Return (entries, errors); entries: list of (file,row_id,field,token,reason)."""
    if not os.path.isfile(path):
        return [], [("BASELINE_BAD", f"{path} is missing")]
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        return [], [("BASELINE_BAD", f"{path}: unreadable: {e}")]
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        return [], [("BASELINE_BAD", f"{path}: expected an object with an 'entries' list")]
    errors, entries, seen = [], [], set()
    checked = {(rel, field) for rel, _, fields in CHECKED_FIELDS for field in fields}
    for n, e in enumerate(data["entries"], start=1):
        if not isinstance(e, dict) or set(e) != {"file", "row_id", "field", "token", "reason"} \
                or not all(isinstance(v, str) for v in e.values()):
            errors.append(("BASELINE_BAD", f"entry {n}: must be an object with exactly the string keys "
                                           f"file,row_id,field,token,reason"))
            continue
        key = (e["file"], e["row_id"], e["field"], e["token"])
        if not e["token"].strip() or not e["row_id"].strip():
            errors.append(("BASELINE_BAD", f"entry {n}: empty token or row_id"))
        elif not e["reason"].strip():
            errors.append(("BASELINE_BAD", f"entry {n} {key}: empty reason"))
        elif (e["file"], e["field"]) not in checked:
            errors.append(("BASELINE_BAD", f"entry {n}: {e['file']}:{e['field']} is not a checked field"))
        elif key in seen:
            errors.append(("BASELINE_BAD", f"entry {n}: duplicate entry {key}"))
        else:
            seen.add(key)
            entries.append(key + (e["reason"],))
    return entries, errors


# ---- check ---------------------------------------------------------------------------------------------

def check(repo, baseline_path):
    """Return (findings, report) where findings = [(code, message)] and report is a dict of counts/lists."""
    tree = Tree(tracked_files(repo))
    tokens, nonpath, empties, findings, rows_seen = read_registry(repo, tree)
    entries, bad = load_baseline(baseline_path)
    findings += bad
    base = {e[:4]: e[4] for e in entries}
    present = {(t[0], t[1], t[2], t[3]) for t in tokens}
    stats = {}
    unresolved_keys = set()
    for rel, rid, field, tok, line_no in tokens:
        key = (rel, rid, field, tok)
        s = stats.setdefault((rel, field), {"tokens": 0, "unresolved": 0, "rows": set(), "baselined": 0})
        s["tokens"] += 1
        if tree.resolves(tok):
            if key in base:
                findings.append(("STALE_BASELINE", f"{rel}:{line_no} {rid} {field}: {tok!r} now resolves; "
                                                   f"remove its entry from the baseline"))
            continue
        s["unresolved"] += 1
        s["rows"].add(rid)
        unresolved_keys.add(key)
        if key in base:
            s["baselined"] += 1
        else:
            findings.append(("UNRESOLVED", f"{rel}:{line_no} {rid} {field}: {tok!r} is not in the tracked tree "
                                           f"(restore it, correct the registry, or, as an owner/provenance "
                                           f"decision, baseline it)"))
    for key in sorted(set(base) - present):
        rel, rid, field, tok = key
        if (rel, rid) not in rows_seen:
            why = "row no longer exists"
        else:
            why = "token no longer in that field"
        findings.append(("BASELINE_GONE", f"{rel} {rid} {field}: baselined {tok!r}: {why}; remove the entry"))
    report = {"stats": stats, "nonpath": nonpath, "empties": empties, "unresolved": unresolved_keys,
              "n_baseline": len(entries), "n_tracked": len(tree.files)}
    return findings, report


def print_baseline(repo):
    tree = Tree(tracked_files(repo))
    tokens, _, _, errors, _ = read_registry(repo, tree)
    ents = [{"file": rel, "row_id": rid, "field": field, "token": tok, "reason": BASELINE_REASON}
            for rel, rid, field, tok, _ in tokens if not tree.resolves(tok)]
    print(json.dumps({"entries": ents}, indent=2, ensure_ascii=False))
    return 1 if errors else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--baseline", default=None, help=f"baseline JSON (default: {DEFAULT_BASELINE} in the repo)")
    ap.add_argument("--print-baseline", action="store_true")
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo)
    if not os.path.isdir(repo):
        print(f"ERROR   --repo {a.repo} is not a directory")
        return 2
    baseline = a.baseline or os.path.join(repo, DEFAULT_BASELINE)
    try:
        if a.print_baseline:
            return print_baseline(repo)
        print(f"== check_study_paths: {repo}")
        findings, rep = check(repo, baseline)
    except (OSError, RuntimeError, UnicodeDecodeError, csv.Error) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"tokenizer: {TOKENIZER}; allowed non-path patterns: {', '.join(n for n, _ in ALLOWED_NON_PATH)}")
    for (rel, field), s in sorted(rep["stats"].items()):
        print(f"FIELD   {rel}:{field}: {s['tokens']} token(s), {s['tokens'] - s['unresolved']} resolve, "
              f"{s['unresolved']} unresolved in {len(s['rows'])} row(s), {s['baselined']} baselined")
    for rel, rid, field, tok, kind, line_no in rep["nonpath"]:
        print(f"NONPATH {rel}:{line_no} {rid} {field}: {tok!r} ({kind}, not resolved)")
    for rel, rid, field, line_no in rep["empties"]:
        print(f"EMPTY   {rel}:{line_no} {rid} {field}: empty piece (ignored)")
    by_code = {}
    for code, msg in findings:
        by_code.setdefault(code, []).append(msg)
    for code, msgs in by_code.items():
        for m in msgs[:MAX_LISTED]:
            print(f"ERROR {code} {m}")
            if IN_GHA:
                print(f"::error::{code} {m}")
        if len(msgs) > MAX_LISTED:
            print(f"ERROR {code} ... and {len(msgs) - MAX_LISTED} more")
    print(f"== result: {len(rep['unresolved'])} unresolved token(s), {rep['n_baseline']} baseline entr"
          f"{'y' if rep['n_baseline'] == 1 else 'ies'}, {len(findings)} error(s) -> {'FAIL' if findings else 'PASS'}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
