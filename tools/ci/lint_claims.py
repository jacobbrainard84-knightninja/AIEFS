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
if neither source gives a vocabulary, the lint warns and skips the value checks.

If registry/claims.csv does not exist, the lint prints a notice and exits 0 (not a failure).

Extra rule (warning): rows whose claim_id starts with SSRH-ORIG- are untested origin hypotheses.
They must never be labelled Retired (Retired / Rejected / Quarantined are reserved for claims
that were tested and failed, or were withdrawn). Such a label produces a warning.

Exit status: 0 = OK (warnings allowed unless --strict), 1 = errors, 2 = usage error.
"""
import argparse
import csv
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


# ---------------------------------------------------------------- vocabulary sources
VOCAB_HEADING = "## Status vocabulary"


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


def load_vocab(readme_path, fallback_path, rep):
    if os.path.isfile(readme_path):
        with open(readme_path, encoding="utf-8") as f:
            v = parse_readme_vocab(f.read())
        if v:
            print(f"vocabulary: {len(v)} statuses from '{VOCAB_HEADING}' block in {readme_path}")
            return v
        rep.notice(f"{readme_path} has no '{VOCAB_HEADING}' fenced block; trying fallback")
    else:
        rep.notice(f"{readme_path} not found; trying fallback")
    if os.path.isfile(fallback_path):
        with open(fallback_path, encoding="utf-8") as f:
            v, placeholder = parse_fallback_vocab(f.read())
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
        rep.notice(f"{claims_rel} not found in {repo}; claims lint skipped (not a failure)")
        return
    vocab = load_vocab(os.path.join(repo, readme_rel), os.path.join(repo, fallback_rel), rep)
    allowed = set(vocab)
    if not vocab:
        rep.warn("no status vocabulary found (registry/README.md or fallback); value checks skipped")
    elif SPECULATIVE_LABEL in allowed:
        print(f"vocabulary: '{SPECULATIVE_LABEL}' is allowed")
    else:
        rep.warn(f"vocabulary has no '{SPECULATIVE_LABEL}' status; untested origin ideas need it")

    with open(claims, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        if "claim_id" not in header:
            rep.error(f"{claims_rel}: no 'claim_id' column", claims_rel, 1)
            return
        checked = [c for c in columns if c in header]
        for c in columns:
            if c not in header:
                rep.notice(f"{claims_rel}: column '{c}' not present; not checked")
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
