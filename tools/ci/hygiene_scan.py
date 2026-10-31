#!/usr/bin/env python3
"""Repository hygiene scan: large files, likely secrets, and new binaries outside allowed folders.

Plain Python 3 standard library (uses the `git` command if the target is a git checkout).
Run from the repository root:

    python3 tools/ci/hygiene_scan.py                     # scan every tracked file
    python3 tools/ci/hygiene_scan.py --base origin/main  # scan only files changed since a ref
    python3 tools/ci/hygiene_scan.py --repo PATH --untracked   # also scan untracked files

Checks
------
  LARGE_FILE      error   file larger than --max-mb (default 95 MiB; GitHub rejects files > 100 MiB)
  BIG_FILE        warn    file larger than --warn-mb (default 50 MiB; GitHub warns above this)
  SECRET_FILE     error   file name that usually holds secrets: .env / .env.* (not .env.example),
                          *.pem, *.key, *.p12, *.pfx, *.keystore, *.jks, id_rsa / id_dsa / id_ecdsa /
                          id_ed25519, .netrc, .pgpass, credentials.json, service-account*.json
  SECRET_PATTERN  error   text that looks like a credential: private-key blocks, AWS access key IDs,
                          GitHub / Slack / OpenAI / Anthropic / Google / Hugging Face / Stripe /
                          xAI tokens, JWTs
  SECRET_ASSIGN   warn    an api key / token / password name assigned a long quoted literal
                          (noisy; review by hand)
  NEW_BINARY      error   (with --base) a binary file ADDED outside the folders in hygiene_allow.txt
  BINARY_OUTSIDE  warn    (full scan) an existing binary outside the allowed folders
  PII_EMAIL/PHONE warn    (with --pii) e-mail address or phone-number-like text; skips Python
                          matmul like A@np.array(...), and reserved domains (.example, .invalid,
                          .test, .localhost, example.com/net/org, localhost, .tld placeholder)

Matched values are NEVER printed: every finding shows only its type and path:line. The scanner
embeds no private literal strings. A private list can be supplied at run time with
--private-patterns FILE (one literal per line, kept OUTSIDE the repo); its matches are reported
as PRIVATE_LITERAL (warn) with location only, and the file's contents are never printed.

Exit status: 0 = no errors (warnings allowed unless --strict), 1 = errors, 2 = usage error.
"""
import argparse
import fnmatch
import os
import re
import subprocess
import sys

MiB = 1024 * 1024
IN_GHA = os.environ.get("GITHUB_ACTIONS") == "true"

BINARY_EXT = {
    ".npz", ".npy", ".pkl", ".pickle", ".h5", ".hdf5", ".pt", ".pth", ".onnx", ".safetensors", ".bin",
    ".pdf", ".zip", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".tar", ".rar", ".whl", ".jar",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".ico",
    ".odt", ".ods", ".odp", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".mp3", ".mp4", ".wav", ".mov", ".avi", ".mkv", ".so", ".dll", ".dylib", ".exe", ".o", ".a",
    ".olean", ".ilean", ".sqlite", ".db",
}
SECRET_NAMES = ["*.pem", "*.key", "*.p12", "*.pfx", "*.keystore", "*.jks", "id_rsa", "id_dsa",
                "id_ecdsa", "id_ed25519", ".netrc", ".pgpass", "credentials.json", "service-account*.json"]
SECRET_NAME_OK = {".env.example", ".env.sample", ".env.template"}

# Patterns are assembled from pieces so this file never matches itself.
_BEGIN = "-----" + "BEGIN"
SECRET_PATTERNS = [
    ("private key block", re.compile(_BEGIN + r" (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY")),
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("Slack webhook", re.compile(r"hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+")),
    ("OpenAI/Anthropic-style key", re.compile(r"\bsk-(?:proj-|ant-|live-)?[A-Za-z0-9_-]{32,}")),
    ("Stripe live key", re.compile(r"\b[rs]k_live_[A-Za-z0-9]{20,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Hugging Face token", re.compile(r"\bhf_[A-Za-z0-9]{30,}\b")),
    ("xAI key", re.compile(r"\bxai-[A-Za-z0-9]{40,}")),
    ("JSON web token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
]
ASSIGN_PATTERN = re.compile(
    r"(?i)\b(?:api[_-]?key|secret(?:[_-]?key)?|access[_-]?token|auth[_-]?token|password|passwd)\b"
    r"\s*[:=]\s*['\"][^'\"\s]{12,}['\"]")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
EMAIL_OK = re.compile(r"(?i)@(?:users\.noreply\.github\.com|noreply\.github\.com)$|^(?:noreply|no-reply|git)@")
# Reserved / non-delegated names that can never be a real person's mailbox:
# RFC 2606 / RFC 6761 (.example, .invalid, .test, .localhost, example.com/.net/.org, localhost),
# plus the ".tld" placeholder (not a delegated top-level domain).
RESERVED_EMAIL_DOMAIN = re.compile(
    r"(?i)(?:^|\.)(?:example\.(?:com|net|org)|localhost)$|\.(?:example|invalid|test|localhost|tld)$")
# Python matrix-multiply: `A@np.array(...)`. The regex sees "A@np.array", but the "domain" starts
# with an array-library module, or the match runs straight into a call/index. A mail address never
# does either.
MATMUL_MODULE = re.compile(r"(?i)^(?:np|numpy|jnp|jax\.numpy|torch|scipy|sp|la|linalg|sympy|sm)\.")


def email_is_benign(line, m):
    """True if an EMAIL_PATTERN match is not a real address (operator use, reserved or noreply domain)."""
    addr = m.group(0)
    domain = addr.split("@", 1)[1]
    if EMAIL_OK.search(addr) or RESERVED_EMAIL_DOMAIN.search(domain):
        return True
    if MATMUL_MODULE.match(domain):
        return True
    nxt = line[m.end():m.end() + 1]
    return nxt in ("(", "[")
PHONE_PATTERN = re.compile(r"(?<![\w.])(?:\+\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?![\w.])")


class Report:
    def __init__(self):
        self.errors = 0; self.warnings = 0; self.lines = []

    def add(self, level, kind, path, line=None, detail=""):
        loc = f"{path}:{line}" if line else path
        msg = f"{kind} {loc}" + (f" ({detail})" if detail else "")
        print(f"{'ERROR  ' if level == 'error' else 'WARNING'} {msg}")
        if IN_GHA:
            ln = f",line={line}" if line else ""
            print(f"::{'error' if level == 'error' else 'warning'} file={path}{ln}::{kind}" + (f" ({detail})" if detail else ""))
        if level == "error":
            self.errors += 1
        else:
            self.warnings += 1


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.decode(errors='replace').strip()}")
    return [p for p in r.stdout.decode("utf-8", errors="surrogateescape").split("\0") if p]


def is_git(repo):
    return subprocess.run(["git", "-C", repo, "rev-parse", "--is-inside-work-tree"],
                          capture_output=True).returncode == 0


def walk_files(repo):
    skip = {".git", ".lake", "__pycache__", ".venv", "venv", "node_modules"}
    out = []
    for d, dirs, files in os.walk(repo):
        dirs[:] = [x for x in dirs if x not in skip]
        for f in files:
            out.append(os.path.relpath(os.path.join(d, f), repo).replace(os.sep, "/"))
    return out


def load_allow(path):
    pats = []
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if ln and not ln.startswith("#"):
                    pats.append(ln)
    return pats


def allowed(rel, pats):
    for p in pats:
        if p.endswith("/") and rel.startswith(p):
            return True
        if fnmatch.fnmatchcase(rel, p):
            return True
    return False


def looks_binary(full, rel):
    if os.path.splitext(rel)[1].lower() in BINARY_EXT:
        return True
    try:
        with open(full, "rb") as f:
            return b"\0" in f.read(8192)
    except OSError:
        return False


def scan_text(full, rel, rep, args, private):
    try:
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f, 1):
                for name, pat in SECRET_PATTERNS:
                    if pat.search(line):
                        rep.add("error", "SECRET_PATTERN", rel, n, name + "; value not shown")
                if ASSIGN_PATTERN.search(line):
                    rep.add("warn", "SECRET_ASSIGN", rel, n, "credential-like assignment; value not shown")
                if args.pii:
                    for m in EMAIL_PATTERN.finditer(line):
                        if not email_is_benign(line, m):
                            rep.add("warn", "PII_EMAIL", rel, n, "e-mail address; value not shown")
                            break
                    if PHONE_PATTERN.search(line):
                        rep.add("warn", "PII_PHONE", rel, n, "phone-number-like text; value not shown")
                if private:
                    low = line.lower()
                    if any(p in low for p in private):
                        rep.add("warn", "PRIVATE_LITERAL", rel, n, "matches the private list; value not shown")
    except OSError as e:
        rep.add("warn", "UNREADABLE", rel, None, type(e).__name__)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".", help="repository root (default: current directory)")
    ap.add_argument("--base", help="git ref to diff against; only changed files are scanned and ADDED "
                                   "binaries outside allowed folders are errors")
    ap.add_argument("--untracked", action="store_true", help="also scan untracked, non-ignored files")
    ap.add_argument("--allow-file", default=None,
                    help="allowed-binary-folders list (default: <repo>/tools/ci/hygiene_allow.txt, "
                         "else the copy next to this script)")
    ap.add_argument("--max-mb", type=float, default=95.0)
    ap.add_argument("--warn-mb", type=float, default=50.0)
    ap.add_argument("--max-scan-mb", type=float, default=10.0,
                    help="text files larger than this are size-checked but not content-scanned (default 10)")
    ap.add_argument("--pii", action="store_true", help="also warn on e-mail / phone-like text (type+location only)")
    ap.add_argument("--private-patterns", help="file of private literals (one per line, kept outside the repo); "
                                               "matches are reported by location only")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = ap.parse_args(argv)

    repo = os.path.abspath(a.repo)
    if not os.path.isdir(repo):
        print(f"ERROR   --repo {a.repo} is not a directory"); return 2
    allow_file = a.allow_file
    if allow_file is None:
        cand = os.path.join(repo, "tools/ci/hygiene_allow.txt")
        allow_file = cand if os.path.isfile(cand) else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                      "hygiene_allow.txt")
    pats = load_allow(allow_file)
    private = []
    if a.private_patterns:
        with open(a.private_patterns, encoding="utf-8", errors="replace") as f:
            private = [ln.strip().lower() for ln in f if ln.strip() and not ln.startswith("#")]

    print(f"== hygiene_scan: {repo}")
    print(f"allowed binary folders: {len(pats)} pattern(s) from {allow_file if pats else '(none found)'}")
    if private:
        print(f"private list: {len(private)} literal(s) loaded (contents not shown)")
    rep = Report()
    added = set()
    try:
        if a.base:
            if not is_git(repo):
                print("ERROR   --base needs a git checkout"); return 2
            files = git(repo, "diff", "--name-only", "--no-renames", "--diff-filter=AMT", "-z", a.base)
            added = set(git(repo, "diff", "--name-only", "--no-renames", "--diff-filter=A", "-z", a.base))
            mode = f"changed since {a.base}"
        elif is_git(repo):
            files = git(repo, "ls-files", "-z")
            mode = "all tracked files"
        else:
            files = walk_files(repo)
            mode = "all files (not a git checkout)"
        if a.untracked and is_git(repo):
            extra = git(repo, "ls-files", "--others", "--exclude-standard", "-z")
            files += extra
            added |= set(extra) if a.base else set()
            mode += " + untracked"
    except RuntimeError as e:
        print(f"ERROR   {e}"); return 2
    print(f"scope: {mode}: {len(files)} file(s)")

    skipped_big_text = 0
    for rel in sorted(set(files)):
        full = os.path.join(repo, rel)
        if not os.path.isfile(full) or os.path.islink(full):
            continue
        size = os.path.getsize(full)
        base = os.path.basename(rel)
        if size > a.max_mb * MiB:
            rep.add("error", "LARGE_FILE", rel, None, f"{size / MiB:.1f} MiB > {a.max_mb:g} MiB")
        elif size > a.warn_mb * MiB:
            rep.add("warn", "BIG_FILE", rel, None, f"{size / MiB:.1f} MiB > {a.warn_mb:g} MiB")
        if (base == ".env" or base.startswith(".env.")) and base not in SECRET_NAME_OK:
            rep.add("error", "SECRET_FILE", rel, None, "environment file")
        elif any(fnmatch.fnmatch(base.lower(), p) for p in SECRET_NAMES):
            rep.add("error", "SECRET_FILE", rel, None, "key/credential file name")
        if looks_binary(full, rel):
            if not allowed(rel, pats):
                if a.base and rel in added:
                    rep.add("error", "NEW_BINARY", rel, None, "binary added outside allowed folders")
                elif not a.base:
                    rep.add("warn", "BINARY_OUTSIDE", rel, None, "existing binary outside allowed folders")
            continue
        if size > a.max_scan_mb * MiB:
            skipped_big_text += 1
            continue
        scan_text(full, rel, rep, a, private)

    if skipped_big_text:
        print(f"note: {skipped_big_text} text file(s) over {a.max_scan_mb:g} MiB were size-checked only "
              f"(raise --max-scan-mb to content-scan them)")
    failed = rep.errors > 0 or (a.strict and rep.warnings > 0)
    print(f"== result: {rep.errors} error(s), {rep.warnings} warning(s) -> {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
