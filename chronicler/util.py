"""Shared helpers for the project chronicler.

Standard library only. No network except an optional ``git ls-remote``.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Iterable, Sequence


# --------------------------------------------------------------------------
# Locations
# --------------------------------------------------------------------------

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_REPO = PACKAGE_DIR.parent

#: Environment override, used by the tests and by agents working in a worktree.
ENV_REPO = "CHRONICLER_REPO"
ENV_OFFLINE = "CHRONICLER_OFFLINE"


def repo_root() -> Path:
    """Absolute path of the git checkout the chronicler should inspect."""
    override = os.environ.get(ENV_REPO)
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_REPO


def offline() -> bool:
    value = os.environ.get(ENV_OFFLINE, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


# --------------------------------------------------------------------------
# Git
# --------------------------------------------------------------------------

class GitError(RuntimeError):
    """A git invocation failed when the caller needed it to succeed."""


def run_git(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    timeout: float = 60.0,
    check: bool = False,
    text: bool = True,
) -> subprocess.CompletedProcess:
    """Run ``git`` with a list of arguments. Never uses a shell."""
    cmd = ["git", *args]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd or repo_root()),
            capture_output=True,
            text=text,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:  # pragma: no cover - git is a hard dependency
        raise GitError("git is not installed or not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitError(f"git {' '.join(args)} timed out after {timeout}s") from exc
    if check and proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "replace") if isinstance(proc.stderr, bytes) else proc.stderr
        raise GitError(f"git {' '.join(args)} failed ({proc.returncode}): {err.strip()}")
    return proc


def git_out(args: Sequence[str], **kwargs) -> str:
    """Run git and return stripped stdout, raising on failure."""
    return run_git(args, check=True, **kwargs).stdout.strip()


def git_ok(args: Sequence[str], **kwargs) -> bool:
    """Run git and report only whether it succeeded."""
    try:
        return run_git(args, check=False, **kwargs).returncode == 0
    except GitError:
        return False


def toplevel() -> Path:
    try:
        return Path(git_out(["rev-parse", "--show-toplevel"]))
    except GitError:
        return repo_root()


def resolve_ref(preferred: str) -> str:
    """Return the first of ``preferred``, ``main``, ``origin/main``, ``HEAD`` that exists."""
    candidates = [preferred, f"origin/{preferred.split('/')[-1]}", "main", "origin/main", "HEAD"]
    seen: list[str] = []
    for cand in candidates:
        if cand in seen:
            continue
        seen.append(cand)
        if git_ok(["rev-parse", "--verify", "--quiet", f"{cand}^{{commit}}"]):
            return cand
    raise GitError(f"none of these refs resolve: {seen}")


def commit_exists(sha: str) -> bool:
    return git_ok(["rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}"])


def commit_exists_many(shas: Iterable[str]) -> dict[str, bool]:
    """Check many abbreviated shas in one ``cat-file --batch-check`` call."""
    tokens = sorted({s for s in shas if s})
    if not tokens:
        return {}
    payload = "\n".join(tokens) + "\n"
    try:
        proc = subprocess.run(
            ["git", "cat-file", "--batch-check"],
            cwd=str(repo_root()),
            input=payload.encode(),
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {tok: commit_exists(tok) for tok in tokens}
    result: dict[str, bool] = {}
    lines = proc.stdout.decode("utf-8", "replace").splitlines()
    for tok, line in zip(tokens, lines):
        # "<sha> commit <size>" on success, "<tok> missing" or "ambiguous" otherwise.
        result[tok] = " commit " in f" {line} " or line.endswith(" commit")
    return result


def blob_bytes(ref: str, path: str) -> bytes | None:
    proc = run_git(["cat-file", "blob", f"{ref}:{path}"], check=False, text=False)
    if proc.returncode != 0:
        return None
    out = proc.stdout
    return out if isinstance(out, bytes) else out.encode()


def blob_text(ref: str, path: str) -> str | None:
    data = blob_bytes(ref, path)
    if data is None:
        return None
    return data.decode("utf-8", "replace")


# --------------------------------------------------------------------------
# Time
# --------------------------------------------------------------------------

def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_date(value: str) -> dt.datetime | None:
    """Parse the date forms found in this repo's documents."""
    value = value.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d", "%d %B %Y", "%B %d, %Y"):
        try:
            parsed = dt.datetime.strptime(value, fmt)
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed
    return None


def parse_git_date(value: str) -> dt.datetime | None:
    """Parse ``git log --format=%cI`` style timestamps (strict ISO 8601)."""
    value = value.strip()
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return parse_date(value)
    if parsed is not None and parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def iso(value: dt.datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def age_days(then: dt.datetime | None, now: dt.datetime | None = None) -> float | None:
    if then is None:
        return None
    now = now or utcnow()
    return round((now - then).total_seconds() / 86400.0, 1)


# --------------------------------------------------------------------------
# Small utilities
# --------------------------------------------------------------------------

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_id(*parts: object, length: int = 10) -> str:
    """Deterministic short id, so the same problem keeps the same id across runs."""
    joined = "\u001f".join(str(p) for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:length]


def squish(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, limit: int = 240) -> str:
    text = squish(text)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "\u2026"


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def human_days(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value < 1:
        return "today"
    if value < 2:
        return "1 day"
    return f"{value:.0f} days"
