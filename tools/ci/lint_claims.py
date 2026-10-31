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
linted. evidence_scope is a separate axis, not a status, and is not linted here.

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
  - the header repeats a column name: csv.DictReader keeps only the last copy, so an earlier copy
    would never be checked (G6c);
  - registry/README.md has more than one '## Status vocabulary' heading: which block is the
    vocabulary would be ambiguous (G6d; the first block used to win silently);
  - claims.csv, registry/README.md or the fallback file starts with a UTF-8 byte-order mark (BOM),
    is not valid UTF-8, or cannot be read: a one-line ERROR, not a traceback.

Extra rule (warning): rows whose claim_id starts with SSRH-ORIG- are untested origin hypotheses.
They must never be labelled Retired (Retired / Rejected / Quarantined are reserved for claims
that were tested and failed, or were withdrawn). Such a label produces a warning.

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
    """Return the file's text, or None after a one-line ERROR (unreadable, BOM, not UTF-8)."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        rep.error(f"{rel}: cannot be read ({type(e).__name__}: {e.strerror or e})", rel)
        return None
    if data.startswith(b"\xef\xbb\xbf"):
        rep.error(f"{rel}: starts with a UTF-8 byte-order mark (BOM); save it as UTF-8 without a BOM", rel, 1)
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
    reader = csv.DictReader(io.StringIO(text, newline=""))
    try:
        _lint_rows(reader, claims_rel, columns, vocab, allowed, rep)
    except csv.Error as e:
        rep.error(f"{claims_rel}:{reader.line_num}: not parseable as CSV ({e})", claims_rel, reader.line_num)


def _lint_rows(reader, claims_rel, columns, vocab, allowed, rep):
    header = reader.fieldnames or []
    if "claim_id" not in header:
        rep.error(f"{claims_rel}: no 'claim_id' column", claims_rel, 1)
        return
    dups = sorted({c for c in header if header.count(c) > 1})
    for c in dups:   # G6c: DictReader keeps only the last copy, so the others would never be checked
        where = ", ".join(str(k + 1) for k, h in enumerate(header) if h == c)
        rep.error(f"{claims_rel}:1: duplicate column '{c}' in the header (columns {where})", claims_rel, 1)
    checked = [c for c in columns if c in header and c not in dups]
    for c in columns:
        if c not in header:   # G6b: a renamed status column must not turn the lint into a silent pass
            rep.error(f"{claims_rel}:1: status column '{c}' missing from the header; its values were NOT checked",
                      claims_rel, 1)
    print(f"{claims_rel}: {len(header)} columns; linting {', '.join(checked) or '(none)'}")
    seen, n, bad = {}, 0, 0
    for row in reader:
        n += 1
        line = reader.line_num
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
