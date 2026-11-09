"""Drift rules: the chronicler's definition of "out of date".

Each rule returns :class:`Finding` objects with stable ids, exact evidence and a
suggested action. Rules that cannot be evaluated (for example because the network
is unavailable) stay silent instead of guessing.
"""

from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass, field

from . import util

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

#: Content-truth problems outrank pointer hygiene. A wrong status page misleads a reader;
#: a dead path blocks them. Both matter, but the first is what this agent exists for.
RULE_BONUS = {
    "PIN-HASH-MISMATCH": 40.0,
    "DOC-MISSING": 14.0,
    "DOC-STALE-VS-SOURCE": 12.0,
    "DOC-AGED": 8.0,
    "PIN-INPUT-DRIFT-UNRECORDED": 6.0,
    "DOC-MISSING-SECTION": 4.0,
}

#: Which document classes the owner wants kept freshest.
CLASS_WEIGHT = {"instruction": 1.0, "introduction": 0.9, "status": 0.8, "plan": 0.6, "history": 0.4}

#: A document may describe a file that is planned but not yet created. Flagging those
#: as "missing" is a false positive that teaches the agent to distrust the tool.
ASPIRATIONAL = re.compile(
    r"(-\s*\[\s*\])|(\bnot yet\b)|(\bplanned\b)|(\bproposed\b)|(\bfuture\b)|(\btarget\b)|"
    r"(\bwill (?:be|run|add|wire|create|land)\b)|(\bto be (?:added|created|wired|built)\b)",
    re.I,
)

#: A line that says a path was deleted, removed or is absent is citing the deletion, not
#: asserting the path exists. Flagging those as dead pointers is a false positive.
ABSENCE_CONTEXT = re.compile(
    r"\b(deleted|removed|absent|missing|no longer|not present|does not exist|never merged|dropped)\b",
    re.I,
)

#: A bare filename only promises that a file exists when the sentence points at it as a thing
#: that is there ("see X", "X contains"). Names that follow "write", "planted", "such as" or
#: "or a" are outputs, examples or hypotheticals: `FAILED_manifest.json` is a file the agent is
#: told to produce, and a planted `hashlib.py` is the attack in an audit note, not a repo path.
#: Audit review 2026-11-09 confirmed both as false positives.
MENTION_CUE = re.compile(
    r"\b(write|writes|writing|wrote|create|creates|creating|produce|produces|producing|emit|emits|"
    r"output|outputs|planted|plant|shadow|such as|e\.g\.|for example|for instance|or a|or an|"
    r"hypothetical|attacker|defeats?|named)\b[^`]{0,60}$",
    re.I,
)

AUTHORITY_CLAIM = re.compile(r"single\s+(status\s+file|source\s+of\s+truth)", re.I)
NEGATION = re.compile(r"\b(not|never|isn't|is not)\b", re.I)


@dataclass
class Finding:
    rule: str
    severity: str
    title: str
    doc: str
    detail: str
    action: str
    evidence: list[str] = field(default_factory=list)
    line: int | None = None
    key: str = ""

    @property
    def id(self) -> str:
        return util.stable_id(self.rule, self.doc, self.key or self.title)

    def score(self, class_weight: float = 0.5) -> float:
        base = 100.0 - 10 * SEVERITY_ORDER.get(self.severity, 4)
        return round(base * class_weight + RULE_BONUS.get(self.rule, 0.0), 3)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "rule": self.rule,
            "severity": self.severity,
            "title": self.title,
            "doc": self.doc,
            "line": self.line,
            "detail": self.detail,
            "evidence": list(self.evidence),
            "action": self.action,
        }


# --------------------------------------------------------------------------
# Individual rules
# --------------------------------------------------------------------------

def rule_pins(snapshot: dict) -> list[Finding]:
    out: list[Finding] = []
    covered = set(snapshot.get("errata_covered", []))
    for pin in snapshot.get("pins", []):
        path = pin["path"]
        if not pin.get("resolved", True):
            continue
        scope = pin.get("scope", "audited_inputs")
        scope_note = (
            "verified at the pin's own commit"
            if pin.get("verify_scope") == "pin-commit"
            else f"pin commit not in this clone; verified at {pin.get('verify_ref')}"
        )

        if not pin.get("present"):
            out.append(Finding(
                rule="PIN-FILE-MISSING",
                severity="high" if scope == "frozen" else "medium",
                title=f"Hash-pinned file is absent: {path}",
                doc=pin.get("source", ""),
                detail=f"{path} is listed in {pin['source']} but is not present ({scope_note}).",
                action="Restore the file, or record the removal in the errata file. Never silently drop a pin.",
                evidence=[f"{pin['source']}: {path} -> {pin['sha256'][:12]}..."],
                key=path,
            ))
            continue

        if pin.get("match"):
            continue

        expected, actual = pin["sha256"], pin.get("actual_sha256") or ""
        if scope == "frozen":
            out.append(Finding(
                rule="PIN-HASH-MISMATCH",
                severity="critical",
                title=f"Frozen authority changed: {path}",
                doc=pin.get("source", ""),
                detail=(
                    f"{path} no longer matches its frozen hash. Expected {expected[:16]}..., "
                    f"found at {pin.get('verify_ref')} is {actual[:16]}... ({scope_note})."
                ),
                action=(
                    "Stop. Do not 'fix' the pin. Confirm with the owner, then record the change as a dated "
                    "erratum; if a claim depends on the bytes, update the claim ledger."
                ),
                evidence=[
                    f"{pin['source']} pins {path} = {expected}",
                    f"actual at {pin.get('verify_ref')} = {actual}",
                ],
                key=path,
            ))
        elif path in covered:
            out.append(Finding(
                rule="PIN-INPUT-DRIFT-DOCUMENTED",
                severity="info",
                title=f"Audited input changed and is covered by errata: {path}",
                doc=pin.get("source", ""),
                detail=(
                    f"{path} differs from its audit-time hash, but the errata file mentions it, so the "
                    f"change is on record ({scope_note})."
                ),
                action="No action needed. Confirm the erratum still describes this exact change if the file moves again.",
                evidence=[f"{path}: pinned {expected[:12]}... actual {actual[:12]}..."],
                key=path,
            ))
        else:
            out.append(Finding(
                rule="PIN-INPUT-DRIFT-UNRECORDED",
                severity="medium",
                title=f"Audited input changed with no erratum: {path}",
                doc=pin.get("source", ""),
                detail=(
                    f"{path} differs from the hash recorded at audit time and the errata file does not "
                    f"mention it ({scope_note}). Expected {expected[:12]}..., actual {actual[:12]}...."
                ),
                action=(
                    "Add a dated erratum entry naming the file and what changed, or restore the audited bytes. "
                    "Do not update the manifest hash yourself."
                ),
                evidence=[
                    f"{pin['source']} records {path} = {expected}",
                    f"actual = {actual}",
                ],
                key=path,
            ))
    return out


def rule_presence(snapshot: dict) -> list[Finding]:
    out: list[Finding] = []
    for doc in snapshot.get("documents", []):
        if not doc.get("present"):
            if not doc.get("required", True):
                continue
            out.append(Finding(
                rule="DOC-MISSING",
                severity="high",
                title=f"Maintained document is missing: {doc['path']}",
                doc=doc["path"],
                detail=f"{doc['path']} is registered in docs_manifest.json but absent at {doc['ref']}.",
                action="Restore it, or remove it from docs_manifest.json with a written reason.",
                evidence=[f"ref {doc['ref']}"],
            ))
            continue
        for watched in doc.get("watch", []):
            if not any(p == watched or p.startswith(watched.rstrip("/") + "/") for p in snapshot.get("universe", [])):
                out.append(Finding(
                    rule="DOC-WATCH-MISSING",
                    severity="medium",
                    title=f"Staleness signal is broken: {doc['path']} watches a missing file",
                    doc=doc["path"],
                    detail=f"{doc['path']} is supposed to track {watched}, which does not exist at {doc['ref']}.",
                    action="Point the watch entry at the real source of truth, or drop it with a reason.",
                    evidence=[f"docs_manifest.json: {doc['path']}.watch includes {watched}"],
                    key=watched,
                ))
    return out


def rule_staleness(snapshot: dict) -> list[Finding]:
    out: list[Finding] = []
    stale_after = snapshot.get("manifest", {}).get("stale_after_days", 14)
    for doc in snapshot.get("documents", []):
        if not doc.get("present"):
            continue
        doc_class = doc.get("class", "status")
        if doc_class not in {"status", "introduction", "instruction", "plan"}:
            continue

        declared = doc.get("declared_date")
        age = doc.get("age_days")
        watch_newest = doc.get("watch_newest")
        newest_dt = util.parse_git_date((watch_newest or {}).get("date") or "")
        declared_dt = util.parse_date(declared) if declared else None

        track_sources = doc_class == "status"

        # A shallow clone cannot date a file: the finding stands, the date does not travel with it.
        if track_sources and declared_dt and (watch_newest or {}).get("date_withheld"):
            tip = snapshot.get("ref_commit") or {}
            tip_dt = util.parse_git_date(tip.get("date") or "")
            if tip_dt and tip_dt > declared_dt:
                depth = (snapshot.get("history") or {}).get("commits")
                out.append(Finding(
                    rule="DOC-STALE-VS-SOURCE",
                    severity="high",
                    title=f"{doc['path']} is older than the sources it describes",
                    doc=doc["path"],
                    detail=(
                        f"{doc['path']} declares {declared} (line {doc.get('declared_date_line')}), but "
                        f"{watch_newest['path']} has changed since that stamp. No 'last changed' date is "
                        f"published here: this clone is shallow ({depth} commit(s)), so `git log` returns "
                        f"the clone boundary rather than the file's last change."
                    ),
                    action=(
                        f"Re-verify {doc['path']} against {watch_newest['path']} at "
                        f"{(tip.get('sha') or '')[:7]}, then update the text and the date stamp in the same "
                        f"edit. Date the file change with a full clone; do not take it from this one."
                    ),
                    evidence=[
                        f"{doc['path']}:{doc.get('declared_date_line')}: declares {declared}",
                        f"{watch_newest['path']}: changed after {declared} (date withheld: shallow clone)",
                        f"ref tip {(tip.get('sha') or '')[:7]} dated {(tip.get('date') or '')[:10]}",
                    ],
                    line=doc.get("declared_date_line"),
                ))
                continue

        if track_sources and declared_dt and newest_dt and newest_dt > declared_dt:
            late = round((newest_dt - declared_dt).total_seconds() / 86400.0, 1)
            out.append(Finding(
                rule="DOC-STALE-VS-SOURCE",
                severity="high",
                title=f"{doc['path']} is older than the sources it describes",
                doc=doc["path"],
                detail=(
                    f"{doc['path']} declares {declared} (line {doc.get('declared_date_line')}), but "
                    f"{watch_newest['path']} changed on {watch_newest['date'][:10]} "
                    f"({util.human_days(late)} later)."
                ),
                action=(
                    f"Re-verify the statements in {doc['path']} against {watch_newest['path']} at "
                    f"{(watch_newest.get('sha') or '')[:7]}, then update the text and the date stamp in the same edit."
                ),
                evidence=[
                    f"{doc['path']}:{doc.get('declared_date_line')}: declares {declared}",
                    f"{watch_newest['path']} last changed {watch_newest['date'][:10]} @ {(watch_newest.get('sha') or '')[:7]}",
                ],
                line=doc.get("declared_date_line"),
            ))
            continue

        if not declared:
            if doc_class in {"status", "introduction"}:
                out.append(Finding(
                    rule="DOC-NO-DATE",
                    severity="medium",
                    title=f"{doc['path']} has no freshness stamp",
                    doc=doc["path"],
                    detail=(
                        f"{doc['path']} is a {doc_class} document with no 'Last Verified' or "
                        "'as of YYYY-MM-DD' stamp, so its age cannot be judged."
                    ),
                    action="Add a dated stamp near the top and keep it in sync with every substantive edit.",
                    evidence=[f"{doc['path']}: no date found in the first 45 lines"],
                ))
            continue

        if age is not None and age > stale_after:
            out.append(Finding(
                rule="DOC-AGED",
                severity="medium",
                title=f"{doc['path']} has not been refreshed in {util.human_days(age)}",
                doc=doc["path"],
                detail=(
                    f"Last stamp {declared} ({util.human_days(age)} ago) exceeds the "
                    f"{stale_after}-day freshness budget for {doc_class} documents."
                ),
                action="Re-read it against current reality, then either confirm it (and restamp) or correct it.",
                evidence=[f"{doc['path']}:{doc.get('declared_date_line')}: {declared}"],
                line=doc.get("declared_date_line"),
            ))
    return out


#: "a machine-readable `provenance.json`" prescribes an artifact; nobody writes "a" before the
#: name of a specific file they are pointing at. Same for "alongside a neighbouring `README.md`".
GENERIC_REF = re.compile(r"\b(?:a|an)\s+(?:[a-z][a-z\-]*\s+){0,3}$", re.I)


def _non_assertive(text: str, token: str, prefix: str | None = None) -> bool:
    """True when the words just before a bare filename mark it as an output or a hypothetical."""
    if prefix:
        window = prefix.rstrip("`")
        return bool(MENTION_CUE.search(window) or GENERIC_REF.search(window))
    index = text.find(token)
    if index < 0:
        return False
    # The token sits inside backticks, so the window ends with the opening one.
    window = text[max(0, index - 70):index].rstrip("`")
    return bool(MENTION_CUE.search(window) or GENERIC_REF.search(window))


def rule_citations(snapshot: dict) -> list[Finding]:
    out: list[Finding] = []
    universe = set(snapshot.get("universe", []))
    history_ok = bool(snapshot.get("history", {}).get("reliable", True))

    for doc in snapshot.get("documents", []):
        if not doc.get("present"):
            continue

        # --- commits the document says exist -----------------------------
        # In a shallow or truncated clone almost nothing resolves, so the check
        # would be pure noise. Say nothing rather than accuse the document.
        cited = doc.get("cited_shas", [])
        if cited and history_ok:
            exists = util.commit_exists_many({c["token"] for c in cited})
            missing = [c for c in cited if not exists.get(c["token"], False)]
            if missing:
                tokens = sorted({m["token"] for m in missing})
                lines = sorted({m["line"] for m in missing})
                out.append(Finding(
                    rule="DOC-SHA-UNREACHABLE",
                    severity="medium",
                    title=f"{doc['path']} cites {len(tokens)} commit(s) not present in this clone",
                    doc=doc["path"],
                    detail=(
                        "Cited short shas that do not resolve: " + ", ".join(tokens[:8])
                        + (" ..." if len(tokens) > 8 else "")
                        + ". Either the citation is wrong, or the commit was never fetched or merged."
                    ),
                    action=(
                        "Fetch the ref that contains it and re-check, then correct the citation. If the work "
                        "was never merged, the document must say so explicitly."
                    ),
                    evidence=[f"{doc['path']}:{line}" for line in lines[:6]],
                    line=lines[0] if lines else None,
                    key=",".join(tokens),
                ))

        # --- repo-relative paths the document says exist -----------------
        relative_missing: list[dict] = []
        bare_missing: list[dict] = []
        for ref in doc.get("cited_paths", []):
            _text = ref.get("context") or ref.get("text", "")
            if ASPIRATIONAL.search(_text):
                continue  # describes a planned artifact, not a current one
            # Strip the token first: a filename like `docs/missing.md` is not a claim of absence.
            if ABSENCE_CONTEXT.search(_text.replace(ref.get("token", ""), " ")):
                continue  # cites a deletion/absence, so the dead path is the point
            kind = ref.get("kind", "relative")
            if kind == "bare":
                if _non_assertive(_text, ref["token"], ref.get("prefix")):
                    continue  # an output, an example or a hypothetical, not a promise of a file
                if not _basename_resolves(ref["token"], universe):
                    bare_missing.append(ref)
                continue
            if not _path_resolves(ref["token"], universe, doc["path"]):
                relative_missing.append(ref)

        if relative_missing:
            tokens = sorted({m["token"] for m in relative_missing})
            out.append(Finding(
                rule="DOC-PATH-MISSING",
                severity="high",
                title=f"{doc['path']} points at {len(tokens)} path(s) that do not exist",
                doc=doc["path"],
                detail="Missing references: " + ", ".join(tokens[:8]) + (" ..." if len(tokens) > 8 else ""),
                action=(
                    "Point the reference at the real path (renamed/moved), or state plainly that the "
                    "artifact is absent. Do not leave a dead pointer in an instruction document."
                ),
                evidence=[f"{doc['path']}:{m['line']}: `{m['token']}`" for m in relative_missing[:6]],
                line=relative_missing[0]["line"],
                key=",".join(tokens),
            ))

        if bare_missing:
            tokens = sorted({m["token"] for m in bare_missing})
            out.append(Finding(
                rule="DOC-BARE-REF",
                severity="low",
                title=f"{doc['path']} names {len(tokens)} bare filename(s) with no matching file",
                doc=doc["path"],
                detail=(
                    "Bare filenames are often run outputs rather than repo files, so this is only a prompt "
                    "to check: " + ", ".join(tokens[:8]) + (" ..." if len(tokens) > 8 else "")
                ),
                action=(
                    "For each name, decide whether it should exist in the repo. If it is a generated output, "
                    "say so inline; if it was moved, give the path."
                ),
                evidence=[f"{doc['path']}:{m['line']}: `{m['token']}`" for m in bare_missing[:6]],
                line=bare_missing[0]["line"],
                key=",".join(tokens),
            ))
    return out


def _path_resolves(token: str, universe: set[str], doc_path: str = "") -> bool:
    """Resolve a cited path against the tree, allowing doc-relative references."""
    if token in universe:
        return True
    candidates = [token]
    if doc_path:
        cursor = posixpath.dirname(doc_path)
        for _ in range(6):
            candidates.append(posixpath.normpath(posixpath.join(cursor, token)))
            if not cursor:
                break
            cursor = posixpath.dirname(cursor)
    for candidate in candidates:
        if candidate in universe:
            return True
        prefix = candidate.rstrip("/") + "/"
        if any(path.startswith(prefix) for path in universe):
            return True
    # A fragment quoted from a subfolder (e.g. "evidence/scripts/x.py") still resolves.
    suffix = "/" + token.lstrip("./")
    if any(path.endswith(suffix) for path in universe):
        return True
    # A single-segment name like "analysis/" is usually a conceptual directory inside a
    # run output, not a repo-relative path. Resolve it if that directory exists anywhere.
    if "/" not in token:
        return any(f"/{token}/" in path or path.startswith(f"{token}/") for path in universe)
    return False


def _basename_resolves(token: str, universe: set[str]) -> bool:
    """A bare filename resolves if any tracked file has that basename."""
    if "/" in token:
        return _path_resolves(token, universe)
    return any(path.rsplit("/", 1)[-1] == token for path in universe)


def rule_branch_drift(snapshot: dict) -> list[Finding]:
    out: list[Finding] = []
    remote = snapshot.get("remote", {})
    if not remote.get("ok"):
        return out
    heads = remote.get("heads", {})
    for doc in snapshot.get("documents", []):
        if not doc.get("present"):
            continue
        rows = doc.get("branch_rows", [])
        drifted: list[str] = []
        gone: list[str] = []
        evidence: list[str] = []
        for row in rows:
            branch, token = row["branch"], row["token"]
            live = heads.get(branch)
            if live is None:
                gone.append(branch)
                continue
            if not (live.startswith(token) or token.startswith(live)):
                drifted.append(f"{branch}: doc {token[:7]} vs live {live[:7]}")
                evidence.append(f"{doc['path']}:{row['line']}: `{branch}` | `{token}` (live {live[:7]})")
        if drifted:
            out.append(Finding(
                rule="DOC-BRANCH-DRIFT",
                severity="medium",
                title=f"{doc['path']} quotes stale branch tips",
                doc=doc["path"],
                detail=(
                    f"{len(drifted)} branch tip(s) moved since this snapshot: "
                    + "; ".join(drifted[:5])
                    + (" ..." if len(drifted) > 5 else "")
                    + (
                        ". Also listed but absent from origin (merged and deleted, or never pushed): "
                        + ", ".join(sorted(set(gone))[:8])
                        if gone else ""
                    )
                ),
                action=(
                    "Refresh the tips from `git ls-remote origin` and restate the retrieval time. "
                    "Branch tables are snapshots, never live state."
                ),
                evidence=evidence[:6],
                key=",".join(sorted(drifted)),
            ))
        elif gone and rows:
            out.append(Finding(
                rule="DOC-BRANCH-GONE",
                severity="low",
                title=f"{doc['path']} lists branches that no longer exist on origin",
                doc=doc["path"],
                detail="Not found on origin: " + ", ".join(sorted(set(gone))[:8]),
                action=(
                    "If they were deleted on purpose, mark them deleted (as STATE.md already does for "
                    "five branches). Otherwise restore or correct the name."
                ),
                evidence=[f"{doc['path']}: branch `{b}`" for b in sorted(set(gone))[:6]],
                key=",".join(sorted(set(gone))),
            ))
    return out


def rule_sections(snapshot: dict) -> list[Finding]:
    out: list[Finding] = []
    from .docs import normalise_heading

    for doc in snapshot.get("documents", []):
        if not doc.get("present"):
            continue
        expected = doc.get("required_sections") or []
        if not expected:
            continue
        present = [normalise_heading(h) for h in doc.get("headings", [])]
        missing = [want for want in expected if not any(normalise_heading(want) in h for h in present)]
        if missing:
            out.append(Finding(
                rule="DOC-MISSING-SECTION",
                severity="medium",
                title=f"{doc['path']} lost a required section",
                doc=doc["path"],
                detail="Missing heading(s): " + ", ".join(sorted(missing)),
                action="Restore the section, or update docs_manifest.json if the structure was changed on purpose.",
                evidence=[f"{doc['path']}: expected heading containing '{m}'" for m in sorted(missing)[:5]],
                key=",".join(sorted(missing)),
            ))
    return out


def rule_counts(snapshot: dict) -> list[Finding]:
    out: list[Finding] = []
    actual = snapshot.get("counts", {}).get("tracked_files")
    if not actual:
        return out
    for doc in snapshot.get("documents", []):
        if not doc.get("present") or not doc.get("check_counts"):
            continue
        for item in doc.get("stated_counts", []):
            if item["kind"] != "tracked_files":
                continue
            stated = item["value"]
            if stated == actual:
                continue
            delta = actual - stated
            if abs(delta) / max(actual, 1) < 0.02:
                severity = "low"
            else:
                severity = "low"
            out.append(Finding(
                rule="DOC-COUNT-MISMATCH",
                severity=severity,
                title=f"{doc['path']} quotes {stated:,} files; {snapshot['ref']} has {actual:,}",
                doc=doc["path"],
                detail=(
                    f"Line {item['line']} states '{item['raw']}'. Actual tracked files at "
                    f"{snapshot['ref']} = {actual:,} ({delta:+,})."
                ),
                action=(
                    "Either restate the count from the commit the sentence is about, or label it "
                    "'as of <date>' so it is not read as current."
                ),
                evidence=[f"{doc['path']}:{item['line']}: {item['raw']}"],
                line=item["line"],
                key=f"{stated}->{actual}",
            ))
    return out


def rule_pinned_docs(snapshot: dict) -> list[Finding]:
    """Informational: a maintained doc that is itself hash-pinned needs the errata route."""
    out: list[Finding] = []
    for doc in snapshot.get("documents", []):
        if doc.get("present") and doc.get("is_pinned"):
            sources = ", ".join(doc.get("pinned_by", [])) or "an audit manifest"
            out.append(Finding(
                rule="DOC-HASH-PINNED",
                severity="info",
                title=f"{doc['path']} is hash-pinned: correct it via errata, not by editing",
                doc=doc["path"],
                detail=f"{doc['path']} appears in {sources}. Editing it breaks the audit pins.",
                action=(
                    "Leave the file byte-identical. Put the correction in the errata file and, if a "
                    "claim moves, in the claim ledger. Only the owner can authorise a re-pin."
                ),
                evidence=[f"{src} pins {doc['path']}" for src in doc.get("pinned_by", [])][:3],
                key="pinned",
            ))
    return out


def rule_vocabulary(snapshot: dict) -> list[Finding]:
    """``registry/README.md``'s status block is parsed by CI, so it is a contract, not prose."""
    vocab = snapshot.get("vocabulary") or {}
    values = vocab.get("values") or []
    claims = vocab.get("claims_values") or {}
    out: list[Finding] = []

    if not values:
        out.append(Finding(
            rule="VOCAB-MISSING",
            severity="high",
            title="The status vocabulary block is missing or unparsable",
            doc="registry/README.md",
            detail=(
                "No fenced list was found under '## Status vocabulary'. tools/ci/lint_claims.py parses "
                "exactly that block and falls back to an intentionally empty placeholder file."
            ),
            action="Restore the fenced block verbatim from the previous commit. Do not retype it from memory.",
            evidence=["registry/README.md: heading '## Status vocabulary' with a ```text fence was not found"],
        ))
        return out

    allowed = set(values)
    for column, label in (("artifact_status", "artifact_status"), ("audited_status", "audited_status")):
        entries = claims.get(column) or []
        unknown = [e for e in entries if e["value"] not in allowed]
        if unknown:
            total = sum(e["count"] for e in unknown)
            out.append(Finding(
                rule="VOCAB-UNKNOWN-STATUS",
                severity="high",
                title=f"{len(unknown)} {label} value(s) are outside the vocabulary",
                doc="registry/claims.csv",
                detail=(
                    "Values used by the ledger but absent from registry/README.md: "
                    + ", ".join(f"'{e['value']}' ({e['count']} rows)" for e in unknown[:6])
                    + f". {total} row(s) affected; the CI claims lint is expected to fail."
                ),
                action=(
                    "Either fix the ledger value through registry/reconciliation/build_claims_reconciliation.py, "
                    "or add the value to the vocabulary block if the owner has approved a new label. "
                    "Label changes are a major change (OPERATING_MANUAL.md §5)."
                ),
                evidence=[f"registry/claims.csv: {label} = '{e['value']}' x{e['count']}" for e in unknown[:6]],
                key=column,
            ))

    fallback = vocab.get("lint_fallback_values") or []
    if fallback and set(fallback) != allowed:
        out.append(Finding(
            rule="VOCAB-PARITY",
            severity="medium",
            title="The lint fallback vocabulary has drifted from registry/README.md",
            doc="tools/ci/claim_statuses.txt",
            detail=(
                "The fallback list is supposed to stay empty. It now holds "
                f"{len(fallback)} value(s); differences: "
                + ", ".join(sorted(set(fallback) ^ allowed)[:6])
            ),
            action="Empty the fallback file again; the block in registry/README.md is the single source.",
            evidence=["tools/ci/claim_statuses.txt: non-empty status list"],
        ))
    return out


def rule_authority_overlap(snapshot: dict) -> list[Finding]:
    """Two documents both claiming to be *the* status file is a real trap."""
    claims: dict[str, list[dict]] = {}
    for doc in snapshot.get("documents", []):
        if not doc.get("present"):
            continue
        text = util.blob_text(doc["ref"], doc["path"]) or ""
        for line_no, line in enumerate(text.splitlines(), start=1):
            if NEGATION.search(line[:60]):
                continue
            match = AUTHORITY_CLAIM.search(line)
            lowered_line = line.lower()
            base = doc["path"].rsplit("/", 1)[-1].lower()
            is_self_claim = any(
                phrase in lowered_line
                for phrase in ("this file", "this page", "this document", base)
            )
            if match and is_self_claim:
                claims.setdefault(match.group(1).lower(), []).append(
                    {"doc": doc["path"], "line": line_no, "text": util.truncate(line, 140)}
                )
    out: list[Finding] = []
    for kind, hits in claims.items():
        docs = sorted({h["doc"] for h in hits})
        if len(docs) < 2:
            continue
        victim = docs[-1]
        out.append(Finding(
            rule="DOC-AUTHORITY-OVERLAP",
            severity="low",
            title=f"More than one document claims to be the single {kind}",
            doc=victim,
            detail=(
                "Claimed by: " + ", ".join(docs) + ". Two 'single' authorities means neither is "
                "trustworthy when they disagree."
            ),
            action=(
                "Name one owner document and make the others explicitly subordinate "
                "(for example 'navigation snapshot, not authority')."
            ),
            evidence=[f"{h['doc']}:{h['line']}: {h['text']}" for h in hits][:6],
            key=kind,
        ))
    return out


ALL_RULES = (
    rule_pins,
    rule_presence,
    rule_staleness,
    rule_citations,
    rule_branch_drift,
    rule_sections,
    rule_counts,
    rule_pinned_docs,
    rule_vocabulary,
    rule_authority_overlap,
)


def run_checks(snapshot: dict) -> list[Finding]:
    findings: list[Finding] = []
    for rule in ALL_RULES:
        findings.extend(rule(snapshot))
    # Deterministic order: severity, then document class weight, then id.
    weights = {
        d["path"]: CLASS_WEIGHT.get(d.get("class", "status"), 0.5)
        for d in snapshot.get("documents", [])
    }
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), -weights.get(f.doc, 0.5), f.rule, f.doc, f.id))
    return findings
