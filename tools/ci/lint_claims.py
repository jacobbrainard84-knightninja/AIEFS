#!/usr/bin/env python3
"""Lint the claims registry (registry/claims.csv) against the allowed status vocabulary.

Plain Python 3 standard library. Run from the repository root:

    python3 tools/ci/lint_claims.py              # lint ./registry/claims.csv
    python3 tools/ci/lint_claims.py --repo PATH  # lint another checkout
    python3 tools/ci/lint_claims.py --strict     # treat warnings as errors

Where the allowed values come from (single source of truth)
-----------------------------------------------------------
The vocabulary is NOT hard-coded here. It is read from registry/README.md. The expected format:

    ## Status vocabulary            <- a heading line that is exactly this text
                                    <- (blank lines allowed)
    ```text                         <- the first fenced block after the heading
    Supported                       <- one exact status per line, no comments
    Speculative / untested origin hypothesis
    ```

Every value in the checked columns (default: artifact_status and audited_status) must equal one
of these strings exactly (case-sensitive). audited_qualifier and other free-text columns are not
linted. evidence_scope is a separate axis, not a status: it must equal one of the values in the
'### Axis 2 ... `evidence_scope`' table of registry/README.md exactly (see the artifact rules below).

If registry/README.md has no such block, the fallback file tools/ci/claim_statuses.txt is used
(one status per line, '#' comment lines allowed). That file ships as a PLACEHOLDER with no values;
if neither source gives a vocabulary, that is an ERROR (exit 1, also without --strict): the value
checks cannot run, and a renamed heading must not turn the lint into a silent pass (red-team G6).

If registry/claims.csv does not exist, that is an ERROR (exit 1): there is nothing to lint, and a
deleted registry must not pass (red-team G5).

Also ERRORs, never a silent pass (red-team G5b, G6b, G6c, G6d):
  - claims.csv has a header but no data rows (G5b);
  - a checked status column (default artifact_status, audited_status) is missing from the header,
    e.g. renamed: its values could not be checked (G6b; this was a NOTICE, and passed even with --strict);
  - a column the artifact rules read (statement, evidence_scope, supporting_artifacts) is missing from
    the header: those checks could not run (same message style as G6b, one ERROR per column);
  - the header repeats a column name: csv.DictReader keeps only the last copy, so an earlier copy
    would never be checked (G6c). Names are compared after strip() + casefold(), so 'audited_status '
    or 'Audited_Status' next to 'audited_status' is a duplicate too;
  - a header name has leading or trailing whitespace (e.g. 'audited_status '): it would not match the
    checked column name, so its values would never be checked;
  - claims.csv is not parseable as CSV. The reader runs with strict=True, so e.g. an unterminated
    quoted field at the end of the file ('unexpected end of data') is an error; with strict=False it
    silently swallowed every following line, including appended rows, into one field;
  - --columns names no column (e.g. --columns ""): nothing would be checked;
  - registry/README.md has more than one '## Status vocabulary' heading: which block is the
    vocabulary would be ambiguous (G6d; the first block used to win silently);
  - claims.csv, registry/README.md or the fallback file starts with a UTF-8 byte-order mark (BOM),
    is not valid UTF-8, contains a NUL byte, or cannot be read: a one-line ERROR, not a traceback.

Extra rule (warning): rows whose claim_id starts with SSRH-ORIG- are untested origin hypotheses.
They must never be labelled Retired (Retired / Rejected / Quarantined are reserved for claims
that were tested and failed, or were withdrawn). Such a label produces a warning.

Artifact rules (errors, added for red-team G3/G4, see tools/redteam/REDTEAM.md):
- Every ';'-separated entry of supporting_artifacts that looks like a path (contains '/' or its first
  word has a file extension) must resolve to a file or folder in the tree. Trailing words, ':LINE'
  and '§section' suffixes are allowed ("AI Agent Audits/x.md §2.1", "x.pdf p.3:20"), but only if
  the trailing words outside parentheses are not themselves path-like (no '/', no file extension):
  "lean/AIEFProofs missing.lean" is an error even though lean/AIEFProofs exists. Plain prose entries ("direct matrix multiplication") are not checked.
  Known gaps are listed, with a reason, in KNOWN_MISSING_ARTIFACTS; an entry there that is no longer
  cited, or whose file now exists, is an error (stale allow-list).
- evidence_scope must be exactly one of the values in the '### Axis 2' table of registry/README.md
  (6 values today); if that table cannot be found, that is an error.
- The columns these checks read (statement, evidence_scope, supporting_artifacts) must be in the
  claims.csv header (see the ERROR list above).
- A row that claims a formal / Lean proof (evidence_scope exactly 'Formalized theorem', or a statement
  such as "proved in Lean", "Machine-checked in Lean 4", "Lean 4 verifies") must cite at least one
  existing .lean file. A registry row is not enough: registry/artifacts.csv marks non-proof files
  (README.md, CI YAML) under lean/ as 'Formalized theorem' too. Limitation: only the existence of the
  .lean file is checked, not that it contains the claimed theorem (red-team GAP, see REDTEAM.md).

Exit status: 0 = OK (warnings allowed unless --strict), 1 = errors, 2 = usage error.
"""
import argparse
import csv
import io
import os
import re
import sys

SPECULATIVE_LABEL = "Speculative / untested origin hypothesis"
ORIGIN_PREFIX = "SSRH-ORIG-"
FAILED_ONLY_WORDS = ("Retired", "Rejected", "Quarantined")
CURRENT_STATUS_COLUMNS = ("artifact_status", "audited_status")  # prior_status is history: not checked
IN_GHA = os.environ.get("GITHUB_ACTIONS") == "true"

# (claim_id, cited path) -> reason. Reviewed known-missing citations; anything else missing is an error.
KNOWN_MISSING_ARTIFACTS = {
    ("AUD-REPRO-B2A95", "audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v3.log"):
        "listed in that folder's SHA256SUMS but never committed (Auditor Seat 002 finding M1); "
        "restore the log or reword the row",
}
_EXT = re.compile(r"^\S+\.[A-Za-z0-9]{1,8}$")
_SUFFIX = re.compile(r"(:\d+(-\d+)?|\s*\u00a7.*)$")
_PATHLIKE = re.compile(r"/|^[^\s/]+\.[A-Za-z][A-Za-z0-9]{0,7}$")   # trailing word that names a file/path
FORMAL_SCOPE_VALUE = "Formalized theorem"
# claims.csv columns the artifact / scope / formal-proof checks read -> what is not checked without them
ARTIFACT_CHECK_COLUMNS = {
    "statement": "its Lean-proof wording was",
    "evidence_scope": "evidence_scope values and formal-scope rows were",
    "supporting_artifacts": "cited artifacts and KNOWN_MISSING_ARTIFACTS entries were",
}


def missing_column(rep, claims_rel, kind, col, what):
    """One ERROR line for a column a check needs (G6b style): a deleted or renamed column is never a silent pass."""
    rep.error(f"{claims_rel}:1: {kind} column '{col}' missing from the header; {what} NOT checked", claims_rel, 1)
SCOPE_HEADING = re.compile(r"^###\s.*`evidence_scope`")
LEAN_PROOF_TEXT = re.compile(
    r"\b(proved|proven|proof|verified|formali[sz]ed|machine[- ]checked|checked)\b[^.;]{0,40}\bLean\b"
    r"|\bLean\b(\s*4)?[^.;]{0,20}\b(proof|proved|proven|formali[sz]ation|verif(y|ies|ied)|checks|checked)\b",
    re.I)


def resolve_artifact(repo, entry):
    """Return the repo-relative path an entry cites if it exists, '' if it is prose, None if missing."""
    if "/" not in entry and not _EXT.match(entry.split()[0]):
        return ""
    words = entry.split()
    for k in range(len(words), 0, -1):
        cand = _SUFFIX.sub("", " ".join(words[:k])).strip()
        full = os.path.abspath(os.path.join(repo, cand))
        if cand and not os.path.isabs(cand) and full.startswith(os.path.abspath(repo) + os.sep) \
                and os.path.exists(full):
            # The rest must be a locator or prose, not another (missing) path. Parenthesised prose
            # ("(proposal/scale/winner audit)") is ignored.
            rest = re.sub(r"\([^)]*\)?", " ", " ".join(words[k:]))
            if any(_PATHLIKE.search(w.strip(",;:")) for w in rest.split()):
                return None
            return cand
    return None


def parse_scope_vocab(text):
    """Return the evidence_scope values from the '### Axis 2 ... `evidence_scope`' table, or []."""
    lines = text.splitlines()
    try:
        i = next(k for k, ln in enumerate(lines) if SCOPE_HEADING.match(ln.strip()))
    except StopIteration:
        return []
    vals = []
    for ln in lines[i + 1:]:
        s = ln.strip()
        if s.startswith("#"):
            break
        m = re.match(r"^\|\s*`([^`]+)`\s*\|", s)
        if m:
            vals.append(m.group(1))
    return vals


def check_artifacts(repo, row, cid, rep, where, line, scopes, known_seen):
    cited = []
    for entry in [e.strip() for e in (row.get("supporting_artifacts") or "").split(";") if e.strip()]:
        got = resolve_artifact(repo, entry)
        reason = KNOWN_MISSING_ARTIFACTS.get((cid, entry))
        if reason is not None:
            known_seen[(cid, entry)] = got is None
        if got is None:
            if reason:
                rep.notice(f"{where}: {cid}: cited artifact '{entry}' is missing (known: {reason})")
            else:
                rep.error(f"{where}: {cid}: cited artifact does not exist: '{entry}'", where, line)
        elif got:
            cited.append(got)
    scope = row.get("evidence_scope") or ""
    if scopes is not None and "evidence_scope" in row and scope not in scopes:
        hint = " (has leading/trailing spaces)" if scope.strip() in scopes else ""
        rep.error(f"{where}: {cid}: evidence_scope '{scope}' is not one of the {len(scopes)} values in "
                  f"registry/README.md (Axis 2){hint}", where, line)
    if "supporting_artifacts" not in row:
        return   # the missing column is already one header ERROR; do not repeat it per formal row
    if scope == FORMAL_SCOPE_VALUE or LEAN_PROOF_TEXT.search(row.get("statement") or ""):
        if not any(c.endswith(".lean") and os.path.isfile(os.path.join(repo, c)) for c in cited):
            rep.error(f"{where}: {cid}: claims a formal/Lean proof (evidence_scope "
                      f"'{row.get('evidence_scope', '')}') but cites no existing .lean file", where, line)



class Report:
    def __init__(self):
        self.errors, self.warnings, self.notices = [], [], []

    def _gha(self, kind, msg, path=None, line=None):
        if IN_GHA:
            loc = ""
            if path:
                loc = f" file={path}" + (f",line={line}" if line else "")
            print(f"::{kind}{loc}::{msg}")

    def error(self, msg, path=None, line=None):
        self.errors.append(msg); print(f"ERROR   {msg}"); self._gha("error", msg, path, line)

    def warn(self, msg, path=None, line=None):
        self.warnings.append(msg); print(f"WARNING {msg}"); self._gha("warning", msg, path, line)

    def notice(self, msg):
        self.notices.append(msg); print(f"NOTICE  {msg}"); self._gha("notice", msg)


# ---------------------------------------------------------------- reading files
def read_text(path, rel, rep):
    """Return the file's text, or None after a one-line ERROR (unreadable, BOM, NUL byte, not UTF-8)."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        rep.error(f"{rel}: cannot be read ({type(e).__name__}: {e.strerror or e})", rel)
        return None
    if data.startswith(b"\xef\xbb\xbf"):
        rep.error(f"{rel}: starts with a UTF-8 byte-order mark (BOM); save it as UTF-8 without a BOM", rel, 1)
        return None
    if b"\x00" in data:   # csv accepts NUL on Python >= 3.11; a text registry never contains one
        off = data.index(b"\x00"); line = data[:off].count(b"\n") + 1
        rep.error(f"{rel}:{line}: contains a NUL byte (offset {off}); not a text file", rel, line)
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as e:
        line = data[:e.start].count(b"\n") + 1
        rep.error(f"{rel}:{line}: not valid UTF-8 (byte 0x{data[e.start]:02x} at offset {e.start})", rel, line)
        return None


# ---------------------------------------------------------------- vocabulary sources
VOCAB_HEADING = "## Status vocabulary"


def vocab_heading_lines(text):
    """1-based line numbers of every exact vocabulary heading."""
    return [k + 1 for k, ln in enumerate(text.splitlines()) if ln.strip() == VOCAB_HEADING]


def parse_readme_vocab(text):
    """Return the list of statuses in the first fenced block after the exact heading, or []."""
    lines = text.splitlines()
    try:
        i = next(k for k, ln in enumerate(lines) if ln.strip() == VOCAB_HEADING)
    except StopIteration:
        return []
    k = i + 1
    while k < len(lines) and not lines[k].strip():
        k += 1
    if k >= len(lines) or not lines[k].strip().startswith("```"):
        return []
    vals = []
    for ln in lines[k + 1:]:
        if ln.strip().startswith("```"):
            return [v for v in vals if v]
        vals.append(ln.strip())
    return []  # unterminated fence


def parse_fallback_vocab(text):
    """Fallback: one status per line; lines starting with '#' are comments.
    Returns (values, is_placeholder)."""
    placeholder = "PLACEHOLDER" in text
    vals = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    return vals, placeholder


def load_vocab(readme_path, fallback_path, rep, readme_rel=None, fallback_rel=None):
    """Return the vocabulary list; [] if none was found; None after an ERROR (unreadable or ambiguous)."""
    readme_rel, fallback_rel = readme_rel or readme_path, fallback_rel or fallback_path
    if os.path.isfile(readme_path):
        text = read_text(readme_path, readme_rel, rep)
        if text is None:
            return None
        heads = vocab_heading_lines(text)
        if len(heads) > 1:
            rep.error(f"{readme_rel}: {len(heads)} '{VOCAB_HEADING}' headings (lines {', '.join(map(str, heads))}); "
                      f"exactly one is allowed, status values were NOT checked", readme_rel, heads[1])
            return None
        v = parse_readme_vocab(text)
        if v:
            print(f"vocabulary: {len(v)} statuses from '{VOCAB_HEADING}' block in {readme_path}")
            return v
        rep.notice(f"{readme_path} has no '{VOCAB_HEADING}' fenced block; trying fallback")
    else:
        rep.notice(f"{readme_path} not found; trying fallback")
    if os.path.isfile(fallback_path):
        text = read_text(fallback_path, fallback_rel, rep)
        if text is None:
            return None
        v, placeholder = parse_fallback_vocab(text)
        if v:
            if placeholder:
                rep.warn(f"{fallback_path} is still marked PLACEHOLDER; its values were used anyway")
            print(f"vocabulary: {len(v)} statuses from {fallback_path}")
            return v
        rep.notice(f"{fallback_path} defines no values" + (" (PLACEHOLDER)" if placeholder else ""))
    return []


def lint(repo, claims_rel, readme_rel, fallback_rel, columns, rep):
    if not columns:   # e.g. --columns "": nothing would be checked, which must not be a silent pass
        rep.error("--columns names no status column; status values were NOT checked")
        return
    claims = os.path.join(repo, claims_rel)
    if not os.path.isfile(claims):
        rep.error(f"{claims_rel} not found in {repo}; claims registry missing, nothing was linted", claims_rel)
        return
    vocab = load_vocab(os.path.join(repo, readme_rel), os.path.join(repo, fallback_rel), rep, readme_rel, fallback_rel)
    allowed = set(vocab or [])
    if vocab is None:
        vocab = []          # the ERROR is already reported
    elif not vocab:
        rep.error(f"no status vocabulary found (no '{VOCAB_HEADING}' fenced block in {readme_rel} and no values "
                  f"in {fallback_rel}); status values were NOT checked", readme_rel)
    elif SPECULATIVE_LABEL in allowed:
        print(f"vocabulary: '{SPECULATIVE_LABEL}' is allowed")
    else:
        rep.warn(f"vocabulary has no '{SPECULATIVE_LABEL}' status; untested origin ideas need it")

    text = read_text(claims, claims_rel, rep)
    if text is None:
        return
    # strict=True: malformed quoting (e.g. an unterminated quoted field at EOF) raises csv.Error instead of
    # silently swallowing the rest of the file into one field (Researcher 001 audit of 588d5ee, F1).
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    done = [0]   # physical lines consumed by complete records; the failing record starts on the next line
    try:
        _lint_rows(reader, claims_rel, columns, vocab, allowed, rep, done, repo, readme_rel)
    except csv.Error as e:
        line = done[0] + 1
        rep.error(f"{claims_rel}:{line}: not parseable as CSV ({e})", claims_rel, line)


def _lint_rows(reader, claims_rel, columns, vocab, allowed, rep, done, repo, readme_rel):
    header = reader.fieldnames or []
    done[0] = reader.line_num
    if "claim_id" not in header:
        rep.error(f"{claims_rel}: no 'claim_id' column", claims_rel, 1)
        return
    for k, h in enumerate(header):   # 'audited_status ' would not match 'audited_status' and go unchecked
        if h != h.strip():
            rep.error(f"{claims_rel}:1: column {k + 1} name '{h}' has leading/trailing whitespace", claims_rel, 1)
    def norm(c):
        return c.strip().casefold()
    keys = [norm(h) for h in header]
    dups = sorted({key for key in keys if keys.count(key) > 1})
    for key in dups:   # G6c: DictReader keeps only the last copy, so the others would never be checked
        ks = [k for k, h in enumerate(keys) if h == key]
        names = [header[k] for k in ks]
        where = ", ".join(str(k + 1) for k in ks)
        if len(set(names)) == 1:
            rep.error(f"{claims_rel}:1: duplicate column '{names[0]}' in the header (columns {where})", claims_rel, 1)
        else:
            rep.error(f"{claims_rel}:1: duplicate column in the header (columns {where}: "
                      f"{', '.join(repr(n) for n in names)} differ only in case or surrounding whitespace)",
                      claims_rel, 1)
    checked = [c for c in columns if c in header and norm(c) not in dups]
    for c in columns:
        if c not in header:   # G6b: a renamed status column must not turn the lint into a silent pass
            missing_column(rep, claims_rel, "status", c, "its values were")
    for c, what in ARTIFACT_CHECK_COLUMNS.items():
        if c not in header:   # same for the columns the artifact / scope / formal-proof checks read
            missing_column(rep, claims_rel, "required", c, what)
    scopes = None
    if "evidence_scope" in header:
        readme = os.path.join(repo, readme_rel)
        text, unreadable = "", False
        if os.path.isfile(readme):
            try:   # a BOM / NUL / UTF-8 problem in the README is already one ERROR from load_vocab
                with open(readme, encoding="utf-8", errors="replace") as rf:
                    text = rf.read()
            except OSError:
                unreadable = True   # already one 'cannot be read' ERROR from load_vocab
        scopes = parse_scope_vocab(text) or None
        if scopes is None and not unreadable:
            rep.error(f"{readme_rel}: no '### Axis 2 ... `evidence_scope`' table found; evidence_scope cannot "
                      f"be checked", readme_rel)
        elif scopes:
            print(f"evidence_scope: {len(scopes)} values from {readme_rel}")
    print(f"{claims_rel}: {len(header)} columns; linting {', '.join(checked) or '(none)'}")
    seen, n, bad, known_seen = {}, 0, 0, {}
    for row in reader:
        n += 1
        line = reader.line_num
        done[0] = line
        if None in row:
            rep.error(f"{claims_rel}:{line}: row has more fields than the header", claims_rel, line)
        cid = (row.get("claim_id") or "").strip()
        if not cid:
            rep.error(f"{claims_rel}:{line}: empty claim_id", claims_rel, line)
        elif cid in seen:
            rep.error(f"{claims_rel}:{line}: duplicate claim_id {cid} (first at line {seen[cid]})", claims_rel, line)
        else:
            seen[cid] = line
        if vocab:
            for col in checked:
                val = row.get(col) or ""
                if val not in allowed:
                    bad += 1
                    hint = " (has leading/trailing spaces)" if val.strip() in allowed else ""
                    rep.error(f"{claims_rel}:{line}: {cid}: {col} '{val}' is not in the status vocabulary{hint}",
                              claims_rel, line)
        check_artifacts(repo, row, cid or "(empty claim_id)", rep, claims_rel, line, scopes, known_seen)
        if cid.startswith(ORIGIN_PREFIX):
            for col in CURRENT_STATUS_COLUMNS:
                val = row.get(col) or ""
                hit = [w for w in FAILED_ONLY_WORDS if w.lower() in val.lower()]
                if hit:
                    rep.warn(f"{claims_rel}:{line}: {cid}: {col} '{val.strip()}' uses {'/'.join(hit)}; "
                             f"untested origin hypotheses should be '{SPECULATIVE_LABEL}', never Retired "
                             f"(Retired/Rejected/Quarantined are for tested-and-failed or withdrawn claims)",
                             claims_rel, line)
    print(f"checked {n} claim rows; {bad} status violation(s)")
    if n == 0:   # G5b: a header-only registry must not pass
        rep.error(f"{claims_rel}: no data rows (header only); nothing was linted", claims_rel, 1)
    if n == 0 or "supporting_artifacts" not in header:
        return   # already one 'no data rows' / 'required column' ERROR; no follow-on stale-entry errors
    for key in sorted(KNOWN_MISSING_ARTIFACTS):
        if key not in known_seen:
            rep.error(f"stale KNOWN_MISSING_ARTIFACTS entry: {key[0]} no longer cites '{key[1]}'; "
                      f"remove it from tools/ci/lint_claims.py")
        elif not known_seen[key]:
            rep.error(f"{key[0]}: '{key[1]}' is listed in KNOWN_MISSING_ARTIFACTS but now exists; "
                      f"remove it from tools/ci/lint_claims.py")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".", help="repository root (default: current directory)")
    ap.add_argument("--claims", default="registry/claims.csv")
    ap.add_argument("--readme", default="registry/README.md")
    ap.add_argument("--fallback", default="tools/ci/claim_statuses.txt")
    ap.add_argument("--columns", default="artifact_status,audited_status",
                    help="comma-separated status columns to lint (default: artifact_status,audited_status)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.repo):
        print(f"ERROR   --repo {a.repo} is not a directory"); return 2
    print(f"== lint_claims: {os.path.abspath(a.repo)}")
    rep = Report()
    lint(a.repo, a.claims, a.readme, a.fallback, [c.strip() for c in a.columns.split(',') if c.strip()], rep)
    failed = bool(rep.errors) or (a.strict and bool(rep.warnings))
    print(f"== result: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s), "
          f"{len(rep.notices)} notice(s) -> {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
