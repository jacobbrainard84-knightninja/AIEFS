"""Collect the deterministic facts the chronicler reasons over.

The output is a JSON-serialisable snapshot. Nothing here guesses: every field comes
from git objects, the documents themselves, or an explicit (optional)
``git ls-remote``. If a fact cannot be obtained, it is ``None`` and the rule that
needs it stays quiet instead of inventing an answer.
"""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

from . import docs as doclib
from . import util

DEFAULT_REF = "origin/main"

#: Files that are hash-pinned. ``scope`` decides how a mismatch is treated:
#:   frozen           -> the file must never change (critica on any drift)
#:   audited_inputs   -> drift is allowed only if the errata file records it
DEFAULT_PIN_SOURCES = [
    {
        "path": "AI Agent Audits/evidence/audit_manifest.json",
        "scope": "audited_inputs",
        "verify_at_key": "audited_commit",
    },
    {"path": "twindow_frozen_authority_hashes.txt", "scope": "frozen"},
    {
        "path": "lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt",
        "scope": "frozen",
        "relative_to": "lean/AIEFProofs",
    },
]


# --------------------------------------------------------------------------
# Manifest
# --------------------------------------------------------------------------

def manifest_path() -> Path:
    return Path(__file__).resolve().parent / "docs_manifest.json"


def load_manifest(path: Path | None = None) -> dict:
    path = path or manifest_path()
    data = util.read_json(path)
    if not isinstance(data, dict):
        raise util.GitError(f"cannot read manifest at {path}")
    data.setdefault("ref", DEFAULT_REF)
    data.setdefault("docs", [])
    return data


def doc_ref_candidates(doc: dict, default_ref: str) -> list[str]:
    if doc.get("refs"):
        return list(doc["refs"])
    if doc.get("ref"):
        return [doc["ref"]]
    return [default_ref]


# --------------------------------------------------------------------------
# Git inventory
# --------------------------------------------------------------------------

def list_tree(ref: str) -> dict[str, dict]:
    """``{path: {mode, type, blob, size}}`` for every tracked object at ``ref``."""
    out = util.git_out(["ls-tree", "-r", "-l", ref])
    entries: dict[str, dict] = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        try:
            meta, path = line.split("\t", 1)
        except ValueError:
            continue
        parts = meta.split()
        if len(parts) < 4:
            continue
        mode, kind, blob, size = parts[0], parts[1], parts[2], parts[3]
        try:
            size_int = int(size)
        except ValueError:
            size_int = None
        entries[path] = {"mode": mode, "type": kind, "blob": blob, "size": size_int}
    return entries


def ref_commit_info(ref: str) -> dict:
    try:
        raw = util.git_out(["log", "-1", "--format=%H%x1f%cI%x1f%s", ref])
    except util.GitError:
        return {"sha": None, "date": None, "subject": None}
    sha, date, subject = (raw.split("\x1f") + ["", "", ""])[:3]
    return {"sha": sha or None, "date": util.iso(util.parse_git_date(date)), "subject": subject or None}


def path_commit_info(ref: str, path: str) -> dict:
    try:
        raw = util.git_out(["log", "-1", "--format=%H%x1f%cI%x1f%s", ref, "--", path])
    except util.GitError:
        return {"sha": None, "date": None, "subject": None}
    if not raw:
        return {"sha": None, "date": None, "subject": None}
    sha, date, subject = (raw.split("\x1f") + ["", "", ""])[:3]
    return {"sha": sha or None, "date": util.iso(util.parse_git_date(date)), "subject": subject or None}


def remote_heads(remote: str = "origin", *, allow_network: bool = True) -> dict:
    """Live branch tips. Degrades to ``ok=False`` rather than failing the run."""
    if util.offline() or not allow_network:
        return {"remote": remote, "ok": False, "error": "offline requested", "heads": {}}
    try:
        proc = util.run_git(["ls-remote", "--heads", remote], timeout=25, check=False)
    except util.GitError as exc:
        return {"remote": remote, "ok": False, "error": str(exc), "heads": {}}
    if proc.returncode != 0:
        stderr = proc.stderr if isinstance(proc.stderr, str) else proc.stderr.decode("utf-8", "replace")
        return {"remote": remote, "ok": False, "error": stderr.strip() or f"exit {proc.returncode}", "heads": {}}
    heads: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "\trefs/heads/" not in line:
            continue
        sha, refname = line.split("\t", 1)
        heads[refname.strip().removeprefix("refs/heads/")] = sha.strip()
    return {"remote": remote, "ok": bool(heads), "error": None, "heads": heads}


def local_head() -> dict:
    branch = sha = None
    try:
        branch = util.git_out(["rev-parse", "--abbrev-ref", "HEAD"])
    except util.GitError:
        pass
    try:
        sha = util.git_out(["rev-parse", "HEAD"])
    except util.GitError:
        pass
    dirty = False
    if sha:
        proc = util.run_git(["status", "--porcelain"], check=False)
        dirty = bool(proc.stdout.strip()) if isinstance(proc.stdout, str) else bool(proc.stdout)
    return {"branch": branch, "sha": sha, "dirty": dirty}


def history_depth() -> dict:
    """Shallow clones cannot verify sha citations; say so instead of guessing."""
    shallow = util.git_ok(["rev-parse", "--is-shallow-repository"]) and (
        util.git_out(["rev-parse", "--is-shallow-repository"]).strip() == "true"
    )
    try:
        count = int(util.git_out(["rev-list", "--count", "HEAD"]))
    except (util.GitError, ValueError):
        count = 0
    return {"shallow": bool(shallow), "commits": count, "reliable": (not shallow) and count >= 50}


# --------------------------------------------------------------------------
# Pin discovery
# --------------------------------------------------------------------------

def _match_tracked(raw_path: str, tracked: set[str], base_dir: str | None = None) -> str | None:
    cleaned = raw_path.strip().lstrip("*").strip()
    if base_dir:
        joined = f"{base_dir.rstrip('/')}/{cleaned}"
        if joined in tracked:
            return joined
    if cleaned in tracked:
        return cleaned
    parts = [p for p in cleaned.split("/") if p]
    for start in range(len(parts)):
        candidate = "/".join(parts[start:])
        if candidate in tracked:
            return candidate
    return None


def _skip_pin_path(path: str) -> bool:
    """Aggregate, glob and prose entries are not files."""
    return (
        not path
        or "*" in path
        or "(" in path
        or path.endswith("/")
        or re.search(r"\b(aggregate|sha256 over|sorted)\b", path, re.I) is not None
    )


def _pins_from_json(text: str, source: dict, tracked: set[str]) -> tuple[list[dict], str | None]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [], None
    verify_at = None
    key = source.get("verify_at_key")
    if key and isinstance(data.get(key), str):
        candidate = data[key].strip()
        if len(candidate) >= 7:
            verify_at = candidate
    pins: list[dict] = []
    for map_key in ("inputs_sha256", "sha256", "files_sha256"):
        mapping = data.get(map_key)
        if not isinstance(mapping, dict):
            continue
        for path, digest in mapping.items():
            if not isinstance(digest, str) or len(digest) != 64 or _skip_pin_path(path):
                continue
            resolved = _match_tracked(path, tracked, source.get("relative_to"))
            pins.append({
                "path": resolved or path,
                "sha256": digest.lower(),
                "source": source["path"],
                "scope": source.get("scope", "audited_inputs"),
                "note": map_key,
                "resolved": bool(resolved),
            })
    return pins, verify_at


def _pins_from_sums(text: str, source: dict, tracked: set[str]) -> list[dict]:
    pins: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+)$", line)
        if not match:
            continue
        digest, raw_path = match.group(1).lower(), match.group(2)
        if _skip_pin_path(raw_path):
            continue
        resolved = _match_tracked(raw_path, tracked, source.get("relative_to"))
        pins.append({
            "path": resolved or raw_path,
            "sha256": digest,
            "source": source["path"],
            "scope": source.get("scope", "frozen"),
            "note": "relative_to " + str(source.get("relative_to")) if source.get("relative_to") else "sha256sum",
            "resolved": bool(resolved),
        })
    return pins


def collect_pins(ref: str, tracked: dict[str, dict], sources: list) -> list[dict]:
    tracked_set = set(tracked)
    pins: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for raw_source in sources:
        source = {"path": raw_source, "scope": "audited_inputs"} if isinstance(raw_source, str) else dict(raw_source)
        text = util.blob_text(ref, source["path"])
        if text is None:
            continue
        if source["path"].endswith(".json"):
            found, verify_at = _pins_from_json(text, source, tracked_set)
        else:
            found, verify_at = _pins_from_sums(text, source, tracked_set), None

        verify_ref = ref
        verify_scope = "current-ref"
        if verify_at and util.commit_exists(verify_at):
            verify_ref = verify_at
            verify_scope = "pin-commit"
        elif verify_at:
            verify_scope = "pin-commit-unavailable"

        for pin in found:
            key = (pin["path"], pin["sha256"])
            if key in seen:
                continue
            seen.add(key)
            pin["verify_ref"] = verify_ref
            pin["verify_scope"] = verify_scope
            pin["declared_commit"] = verify_at
            pins.append(pin)
    return pins


def verify_pins(pins: list[dict], default_ref: str) -> list[dict]:
    """Attach ``actual_sha256`` / ``match``, hashing each pin at its own verify ref."""
    cache: dict[tuple[str, str], bytes | None] = {}
    enriched: list[dict] = []
    for pin in pins:
        ref = pin.get("verify_ref") or default_ref
        key = (ref, pin["path"])
        if key not in cache:
            cache[key] = util.blob_bytes(ref, pin["path"]) if pin.get("resolved", True) else None
        data = cache[key]
        actual = util.sha256_bytes(data) if data is not None else None
        item = dict(pin)
        item["actual_sha256"] = actual
        item["present"] = data is not None
        item["match"] = (actual == pin["sha256"]) if actual is not None else False
        enriched.append(item)
    return enriched


# --------------------------------------------------------------------------
# Documents
# --------------------------------------------------------------------------

def describe_document(
    doc: dict,
    *,
    default_ref: str,
    resolved_refs: dict[str, str],
    files_by_ref: dict[str, dict[str, dict]],
    now,
) -> dict:
    path = doc["path"]
    candidates = [resolved_refs[c] for c in doc_ref_candidates(doc, default_ref) if c in resolved_refs]
    ref = None
    for candidate in candidates:
        if path in files_by_ref.get(candidate, {}):
            ref = candidate
            break
    if ref is None:
        ref = candidates[0] if candidates else default_ref

    tracked = files_by_ref.get(ref, {})
    text = util.blob_text(ref, path) if path in tracked else None

    record: dict = {
        "path": path,
        "ref": ref,
        "ref_candidates": candidates,
        "class": doc.get("class", "status"),
        "role": doc.get("role", ""),
        "owner": doc.get("owner", "owner"),
        "editable": bool(doc.get("editable", True)),
        "required": bool(doc.get("required", True)),
        "required_sections": doc.get("required_sections", []),
        "max_age_days": doc.get("max_age_days"),
        "watch": doc.get("watch", []),
        "check_counts": bool(doc.get("check_counts", False)),
        "present": text is not None,
        "blob": tracked.get(path, {}).get("blob"),
        "commit": path_commit_info(ref, path) if text is not None else {"sha": None, "date": None, "subject": None},
        "declared_date": None,
        "declared_date_line": None,
        "age_days": None,
        "headings": [],
        "cited_shas": [],
        "cited_paths": [],
        "stated_counts": [],
        "branch_rows": [],
        "text_sha256": None,
        "line_count": 0,
    }
    if text is None:
        return record

    analysed = doclib.analyse_document(path, text)
    record.update({k: v for k, v in analysed.items() if k != "path"})
    declared_date = analysed.get("declared_date")
    record["age_days"] = util.age_days(util.parse_date(declared_date) if declared_date else None, now)

    newest = None
    for watched in doc.get("watch", []):
        info = path_commit_info(ref, watched)
        when = util.parse_git_date(info.get("date") or "")
        if when and (newest is None or when > newest[1]):
            newest = (watched, when, info.get("sha"))
    record["watch_newest"] = (
        {"path": newest[0], "date": util.iso(newest[1]), "sha": newest[2]} if newest else None
    )
    return record


# --------------------------------------------------------------------------
# Snapshot
# --------------------------------------------------------------------------

def parse_status_vocabulary(text: str, *, require_heading: bool = True) -> list[str]:
    """Extract the fenced status list from ``## Status vocabulary``.

    ``tools/ci/lint_claims.py`` parses this same block, so it is a machine contract.
    """
    if not text:
        return []
    lines = text.splitlines()
    start = 0
    if require_heading:
        start = -1
        for index, line in enumerate(lines):
            if re.match(r"^#{1,6}\s*Status vocabulary\s*$", line.strip(), re.I):
                start = index
                break
        if start < 0:
            return []
    values: list[str] = []
    inside = False
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("```"):
            if inside:
                break
            inside = True
            continue
        if inside and stripped and not stripped.startswith("#"):
            values.append(stripped)
    return values


def parse_claims_statuses(text: str) -> dict:
    """Distinct ``artifact_status`` / ``audited_status`` values used by the ledger."""
    if not text:
        return {"artifact_status": [], "audited_status": [], "rows": 0}
    try:
        reader = csv.DictReader(io.StringIO(text))
        artifact: dict[str, int] = {}
        audited: dict[str, int] = {}
        rows = 0
        for row in reader:
            rows += 1
            for column, bucket in (("artifact_status", artifact), ("audited_status", audited)):
                value = (row.get(column) or "").strip()
                if value:
                    bucket[value] = bucket.get(value, 0) + 1
        return {
            "artifact_status": [{"value": k, "count": v} for k, v in sorted(artifact.items())],
            "audited_status": [{"value": k, "count": v} for k, v in sorted(audited.items())],
            "rows": rows,
        }
    except csv.Error:
        return {"artifact_status": [], "audited_status": [], "rows": 0}


def collect(
    *,
    ref: str | None = None,
    allow_network: bool = True,
    manifest: dict | None = None,
    remote: str = "origin",
) -> dict:
    manifest = manifest or load_manifest()
    ref = util.resolve_ref(ref or manifest.get("ref") or DEFAULT_REF)
    now = util.utcnow()

    resolved_refs: dict[str, str] = {}
    for doc in manifest.get("docs", []):
        for raw in doc_ref_candidates(doc, ref):
            if raw in resolved_refs:
                continue
            try:
                resolved_refs[raw] = util.resolve_ref(raw)
            except util.GitError:
                continue
    resolved_refs.setdefault(ref, ref)

    files_by_ref: dict[str, dict[str, dict]] = {}
    for needed in sorted(set(resolved_refs.values())):
        files_by_ref[needed] = list_tree(needed)

    primary_files = files_by_ref[ref]
    by_ext: dict[str, int] = {}
    total_bytes = 0
    for path, entry in primary_files.items():
        suffix = Path(path).suffix.lower() or "(none)"
        by_ext[suffix] = by_ext.get(suffix, 0) + 1
        total_bytes += entry.get("size") or 0

    pin_sources = manifest.get("pin_sources", DEFAULT_PIN_SOURCES)
    pins = verify_pins(collect_pins(ref, primary_files, pin_sources), ref)

    documents = [
        describe_document(
            doc,
            default_ref=ref,
            resolved_refs=resolved_refs,
            files_by_ref=files_by_ref,
            now=now,
        )
        for doc in manifest.get("docs", [])
    ]

    universe: set[str] = set()
    for table in files_by_ref.values():
        universe.update(table)

    pinned_present = {pin["path"] for pin in pins if pin.get("present")}
    for document in documents:
        document["pinned_by"] = sorted({pin["source"] for pin in pins if pin["path"] == document["path"]})
        document["is_pinned"] = document["path"] in pinned_present

    # The status vocabulary in registry/README.md is parsed by tools/ci/lint_claims.py.
    # Editing that fenced block is therefore a contract change, not prose.
    vocabulary = parse_status_vocabulary(util.blob_text(ref, "registry/README.md") or "")
    claims_statuses = parse_claims_statuses(util.blob_text(ref, "registry/claims.csv") or "")

    errata_path = manifest.get("errata_path", "ERRATA_2026-10-28.md")
    errata_text = util.blob_text(ref, errata_path) or ""

    return {
        "schema": 1,
        "generated_at": util.iso(now),
        # Redacted on purpose: local home paths are a P4 privacy item in this repo.
        "repo_root": "<repo>",
        "ref": ref,
        "refs": sorted(files_by_ref),
        "ref_commit": ref_commit_info(ref),
        "local_head": local_head(),
        "history": history_depth(),
        "remote": remote_heads(remote, allow_network=allow_network),
        "counts": {
            "tracked_files": len(primary_files),
            "tracked_bytes": total_bytes,
            "by_extension": dict(sorted(by_ext.items(), key=lambda kv: (-kv[1], kv[0]))[:20]),
        },
        "pins": pins,
        "pin_summary": {
            "total": len(pins),
            "present": sum(1 for p in pins if p.get("present")),
            "matching": sum(1 for p in pins if p.get("match")),
            "mismatched": [p["path"] for p in pins if p.get("present") and not p.get("match")],
            "missing": [p["path"] for p in pins if not p.get("present")],
        },
        "vocabulary": {
            "source": "registry/README.md",
            "values": vocabulary,
            "lint_source": "tools/ci/claim_statuses.txt",
            "lint_fallback_values": parse_status_vocabulary(
                util.blob_text(ref, "tools/ci/claim_statuses.txt") or "", require_heading=False
            ),
            "claims_values": claims_statuses,
        },
        "errata_path": errata_path,
        "errata_covered": sorted(
            {pin["path"] for pin in pins if pin["path"] and pin["path"] in errata_text}
        ),
        "universe": sorted(universe),
        "documents": documents,
        "manifest": {
            "path": str(manifest_path()),
            "stale_after_days": manifest.get("stale_after_days", 14),
            "status_sources": manifest.get("status_sources", []),
        },
    }
