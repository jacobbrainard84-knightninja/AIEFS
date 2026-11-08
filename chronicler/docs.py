"""Parse maintained documents into machine-checkable facts.

Every function here is pure: text in, plain data out. That keeps the rules in
``checks.py`` testable without touching git.
"""

from __future__ import annotations

import re

from . import util

# --------------------------------------------------------------------------
# Patterns
# --------------------------------------------------------------------------

#: A self-declared freshness stamp, e.g. "**Last Verified:** 2026-10-23".
DATE_PATTERNS = [
    re.compile(r"last\s+(?:verified|updated|reviewed|synced)\**\s*[:\-]?\s*\**\s*(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r"last\s+(?:verified|updated|reviewed|synced)[^\n]{0,40}?(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r"status\s+of\s+this\s+\w+[^\n]{0,30}?\((\d{4}-\d{2}-\d{2})\)", re.I),
    re.compile(r"\bas\s+of\s+(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r"retrieved[^\n]{0,80}?(\d{4}-\d{2}-\d{2})", re.I),
]

#: Dates in a header block, used as a fallback signal.
BARE_DATE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)

#: This repo marks key sections with a bold lead-in ("**Authority order.**") rather
#: than a markdown heading, so treat those as headings too.
BOLD_HEADING = re.compile(r"^[\s>*-]*\*\*([^*\n]{2,80}?)[.:]?\*\*", re.M)

BACKTICK = re.compile(r"`([^`\n]{2,160})`")

SHA_TOKEN = re.compile(r"(?<![0-9a-fA-F])([0-9a-f]{7,12})(?![0-9a-fA-F])")

SHA_CONTEXT = ("sha", "commit", "tip", "branch", "merge", "head", " pr ", "@", "revision")

#: Tokens on these lines are run ids or cohort labels, not commit shas.
RUN_CONTEXT = ("runs/", "run ", "seed", "cohort", "replay", "production run")

PATH_EXTENSIONS = (
    ".md", ".py", ".csv", ".json", ".txt", ".yml", ".yaml", ".sh", ".lean",
    ".npz", ".zip", ".pdf", ".toml", ".cfg", ".ini", ".odt", ".gz", ".b64",
)

#: Shell commands inside backticks are not paths.
COMMAND_PREFIX = re.compile(
    r"^(python3?|pytest|git|gh|bash|sh|cd|lean|lake|pip3?|npm|npx|node|make|"
    r"curl|wget|sed|awk|grep|tar|zip|unzip|chmod|uv|poetry|docker)\b"
)

MATH_CHARS = set("()=*^|{}<>\\√≈≤≥∈−+×→←⇒∝")

#: Hidden / generated directories that legitimately never appear in the tree.
GENERATED_SEGMENTS = (".lake", "__pycache__", ".git", "node_modules", ".venv", ".pytest_cache")

PLACEHOLDER_STEMS = {
    "FILE", "PATH", "NAME", "TODO", "YOUR_FILE", "EXAMPLE", "PLACEHOLDER",
    "OUTPUT", "INPUT", "SCRIPT", "TEMPLATE", "X",
}

#: "| `main` | `395ea53` | ..." or "**main** at `395ea53`".
BRANCH_ROW = re.compile(r"`([A-Za-z0-9._/\-]+)`[^|\n]{0,50}\|\s*`([0-9a-f]{7,40})`")

COUNT_PATTERNS = [
    ("tracked_files", re.compile(r"(\d[\d,]{2,})\s+(?:tracked\s+)?(?:working-tree\s+)?files\b", re.I)),
    ("inventoried_objects", re.compile(r"(\d[\d,]{2,})\s+inventoried\s+objects", re.I)),
    ("zip_members", re.compile(r"(\d[\d,]{2,})\s+(?:archive\s+)?zip\s+members", re.I)),
    ("claims", re.compile(r"(\d[\d,]{2,})\s+claims\b", re.I)),
]


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------

def _lines(text: str):
    return text.splitlines()


def extract_headings(text: str) -> list[str]:
    found = [m.group(2).strip() for m in HEADING.finditer(text)]
    found.extend(m.group(1).strip() for m in BOLD_HEADING.finditer(text))
    return found


def extract_declared_date(text: str, header_lines: int = 45) -> tuple[str | None, int | None]:
    """Return the document's own freshness date and the line it was found on."""
    lines = _lines(text)
    header = lines[:header_lines]
    for pattern in DATE_PATTERNS:
        for index, line in enumerate(header, start=1):
            match = pattern.search(line)
            if match:
                return match.group(1), index
    # Fallback: any date in the header block.
    for index, line in enumerate(header, start=1):
        match = BARE_DATE.search(line)
        if match:
            return match.group(1), index
    return None, None


def classify_token(raw: str) -> tuple[str, str] | None:
    """Classify a backticked token as ``("relative"|"bare", cleaned_path)``.

    Precision matters more than recall: a rule that cries wolf gets ignored. Inline
    code that is a command, a formula, a branch name or a bare ratio is rejected
    rather than guessed at.
    """
    token = raw.strip().strip("\"'")
    if not token or len(token) > 140:
        return None
    if "://" in token:
        return None
    if COMMAND_PREFIX.match(token):
        return None
    if any(ch in MATH_CHARS for ch in token):
        return None
    if re.search(r"\s--?\w", token):  # a "--flag" inside a command
        return None
    if token.startswith(("-", "$", "~", "/", "%", "#", "!")):
        return None
    if "..." in token:
        return None
    token = token.rstrip(".,;:")
    token = re.sub(r":\d+(?:-\d+)?$", "", token)  # "claims.csv:71-74"
    had_slash = token.endswith("/")
    token = token.rstrip("/")
    if not token:
        return None
    if any(seg in GENERATED_SEGMENTS for seg in token.split("/")):
        return None
    if re.fullmatch(r"\.\w+", token):  # ".zip" alone is an extension, not a path
        return None
    stem = token.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    if stem in PLACEHOLDER_STEMS and token.count("/") == 0:
        return None

    has_ext = token.lower().endswith(PATH_EXTENSIONS)
    if has_ext and "/" in token:
        return ("relative", token)
    if has_ext:
        return ("bare", token)
    if token.count("/") >= 2:
        return ("relative", token)  # a directory reference
    if had_slash and "/" not in token:
        return ("relative", token)  # "test_output/"
    if token.count("/") == 1 and had_slash:
        return ("relative", token)
    # A single slash without an extension is a branch, a ratio or an org/repo slug.
    return None


def extract_paths(text: str) -> list[dict]:
    found: list[dict] = []
    seen: set[tuple[str, int]] = set()
    all_lines = _lines(text)
    for index, line in enumerate(all_lines, start=1):
        # Markdown hard-wraps sentences, so "main deleted 52 files (Papers/ 4 ...)" can put the
        # verb on the previous line. Keep that line as context: without it, a correct sentence
        # about a deletion is reported as a dead pointer.
        previous = all_lines[index - 2] if index >= 2 else ""
        for match in BACKTICK.finditer(line):
            classified = classify_token(match.group(1))
            if classified is None:
                continue
            kind, token = classified
            key = (token, index)
            if key in seen:
                continue
            seen.add(key)
            found.append({
                "token": token, "line": index, "kind": kind,
                "text": util.truncate(line, 200),
                "context": util.truncate(previous + " " + line, 400),
            })
    return found


def extract_cited_shas(text: str) -> list[dict]:
    """Commit-like tokens, excluding run ids, cohort labels and hashes in paths."""
    path_tokens = [item["token"] for item in extract_paths(text)]
    found: list[dict] = []
    seen: set[tuple[str, int]] = set()
    for index, line in enumerate(_lines(text), start=1):
        lowered = line.lower()
        if any(marker in lowered for marker in RUN_CONTEXT):
            continue
        backticked = {m.group(1).strip() for m in BACKTICK.finditer(line)}
        contextual = any(hint in f" {lowered} " for hint in SHA_CONTEXT)
        if not (contextual or backticked):
            continue
        for match in SHA_TOKEN.finditer(line):
            token = match.group(1)
            if any(token in candidate for candidate in path_tokens):
                continue  # part of a run id such as runs/5a9f093a2fe0/
            if token not in backticked and not any(ch.isdigit() for ch in token):
                continue  # plain English words made of a-f (e.g. "defaced")
            key = (token, index)
            if key in seen:
                continue
            seen.add(key)
            found.append({"token": token, "line": index})
    return found


def extract_branch_rows(text: str) -> list[dict]:
    rows: list[dict] = []
    for index, line in enumerate(_lines(text), start=1):
        for match in BRANCH_ROW.finditer(line):
            branch, token = match.group(1), match.group(2)
            if "/" not in branch and not re.match(r"^[a-z][a-z0-9._\-]*$", branch):
                continue
            if len(token) < 7 or len(token) > 40:
                continue
            rows.append({"branch": branch, "token": token, "line": index})
    return rows


def extract_stated_counts(text: str) -> list[dict]:
    counts: list[dict] = []
    seen: set[tuple[str, int]] = set()
    for index, line in enumerate(_lines(text), start=1):
        for kind, pattern in COUNT_PATTERNS:
            for match in pattern.finditer(line):
                raw = match.group(1).replace(",", "")
                if not raw.isdigit():
                    continue
                key = (kind, index)
                if key in seen:
                    continue
                seen.add(key)
                counts.append({"kind": kind, "value": int(raw), "line": index, "raw": match.group(0)})
    return counts


def analyse_document(path: str, text: str) -> dict:
    """All text-level facts the rules need, for one document."""
    declared, declared_line = extract_declared_date(text)
    return {
        "path": path,
        "line_count": len(text.splitlines()),
        "char_count": len(text),
        "headings": extract_headings(text),
        "declared_date": declared,
        "declared_date_line": declared_line,
        "cited_shas": extract_cited_shas(text),
        "cited_paths": extract_paths(text),
        "stated_counts": extract_stated_counts(text),
        "branch_rows": extract_branch_rows(text),
        "text_sha256": util.sha256_text(text),
    }


def normalise_heading(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
