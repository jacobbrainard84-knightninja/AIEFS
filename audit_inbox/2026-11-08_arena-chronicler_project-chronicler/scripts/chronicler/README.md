# `chronicler` — the drift detector behind `PROJECT_CHRONICLER_AGENT.md`

A deterministic toolkit that answers three questions about this repository:

1. **What is true right now?** (`collect`) — git objects, tracked files, hash pins, document stamps.
2. **Which memory documents have drifted from that truth?** (`check`) — coded rules, stable ids, exact evidence.
3. **What should be done next?** (`tick`) — reconcile into a durable queue, pick one item, write the work order.

It is stdlib-only Python 3.9+. No third-party packages, no API keys, no daemon.

```bash
python -m chronicler status
python -m chronicler check -v
python -m chronicler tick
cat chronicler/loop/NEXT.md
```

---

## Why it exists

An AI agent that "keeps the docs up to date" has one failure mode that ruins it: it invents a
plausible state and writes confident prose about it. This package removes the invention. The agent
reads facts from git and from the documents' own bytes; the rules are code, not vibes; and every
finding carries `path:line` evidence the agent must reproduce before editing.

The second failure mode is thrash: an agent that rewrites six documents a session and produces an
unreviewable diff. Hence the loop: **one item per cycle, one finding per commit.**

---

## Commands

| Command | What it does |
|---|---|
| `collect` | Builds the fact snapshot. `--json` prints it; `--out PATH` writes it. |
| `check` | Runs every rule. `--fail-on {none,low,medium,high,critical}` (default `high`) sets the exit code. `-v` adds evidence. |
| `status` | Human digest: document table, self-declared dates and ages, pins, queue. |
| `tick` | One cycle: snapshot → findings → reconcile queue → select → write `loop/NEXT.md` + journal. |
| `queue` | Open items in priority order. |
| `close ID --note "..."` | Mark done, journal it. |
| `defer ID --reason "..." [--until YYYY-MM-DD]` | Park it, with a reason on the record. |

Common flags: `--ref <git-ref>` (default from `docs_manifest.json`, `origin/main`), `--offline`
(skip `git ls-remote`; branch-tip rules then stay silent instead of guessing).

Exit codes: `0` success, `1` findings at or above `--fail-on`, `2` operational error (bad ref, no git).

---

## Rules

Each rule has a stable id, so the same problem keeps the same id across runs and `close` sticks.

| Rule | Severity | Fires when |
|---|---|---|
| `PIN-HASH-MISMATCH` | critical | A `frozen` pinned file's bytes differ from the recorded hash. |
| `PIN-FILE-MISSING` | high/medium | A pinned file is absent (high for frozen, medium for audit inputs). |
| `PIN-INPUT-DRIFT-UNRECORDED` | medium | An audited input changed and the errata file does not mention it. |
| `PIN-INPUT-DRIFT-DOCUMENTED` | info | Same, but the errata records it. Advisory only. |
| `DOC-MISSING` | high | A `required` document in the manifest is absent at every ref it declares. |
| `DOC-PATH-MISSING` | high | A document cites a repo-relative path that does not exist (doc-relative and suffix resolution supported). |
| `DOC-STALE-VS-SOURCE` | high | A **status** document's own date predates a change in a source it watches. |
| `DOC-AGED` | medium | A document's own date exceeds its freshness budget. |
| `DOC-NO-DATE` | medium | A status/introduction document has no date stamp at all. |
| `DOC-SHA-UNREACHABLE` | medium | A cited commit does not resolve (skipped entirely in shallow clones). |
| `DOC-BRANCH-DRIFT` | medium | A branch table quotes a tip that has moved (needs network). |
| `DOC-BRANCH-GONE` | low | A branch table lists a branch that no longer exists on origin. |
| `DOC-MISSING-SECTION` | medium | A required heading disappeared. |
| `DOC-COUNT-MISMATCH` | low | A `check_counts` document quotes a file count that no longer holds. |
| `DOC-WATCH-MISSING` | medium | A `watch` entry points at a file that does not exist, silently disabling staleness detection. |
| `DOC-BARE-REF` | low | A bare filename with no matching file — probably a runtime output, worth a look. |
| `DOC-AUTHORITY-OVERLAP` | low | Two documents each claim to *be* the single status file / source of truth. |
| `DOC-HASH-PINNED` | info | A maintained document is itself hash-pinned: correct it via errata, never in place. |
| `VOCAB-UNKNOWN-STATUS` | high | A `registry/claims.csv` status value is outside the `## Status vocabulary` block that CI parses. |
| `VOCAB-MISSING` | high | The status vocabulary block is missing or unparsable (the lint would fall back to an empty list). |
| `VOCAB-PARITY` | medium | The lint fallback list is no longer empty and has drifted from the vocabulary block. |

### Deliberate silences

A rule that cannot be evaluated says nothing rather than accusing a document:

* shallow clone or fewer than 50 commits → no citation checks (`history.reliable` is false);
* offline or no remote → no branch-tip rules;
* a pin whose declared commit is not fetched → verified at the current ref, and the finding says so;
* a document that is not `required` and is absent → no finding.

This is the difference between a tool the agent trusts and one it learns to ignore.

---

## `docs_manifest.json`

The registry of documents to maintain. It is data, not code, so adding a document is a one-line change.

```json
{
  "path": "docs/REVIEWING.md",
  "class": "instruction",
  "role": "How an outside reviewer runs the checks.",
  "owner": "owner",
  "editable": true,
  "required": true,
  "max_age_days": 45,
  "required_sections": ["Running the checks"],
  "watch": ["tools/ci/lint_claims.py", "registry/claims.csv"],
  "check_counts": false,
  "ref": "origin/main",
  "refs": ["origin/audit-inbox", "HEAD"]
}
```

* `class` — `introduction` · `instruction` · `status` · `plan` · `history` · `errata`. Drives the
  priority weighting and which staleness rule applies.
* `watch` — files whose change makes this document suspect. Used by `DOC-STALE-VS-SOURCE`.
* `ref` / `refs` — a document may live on another line of work (the briefing lives on the
  audit-inbox line). The first ref that actually contains the file wins.
* `editable` / `owner` — a pinned or another-seat document still gets checked, but the agent must route
  the fix elsewhere. `tick` keeps that distinction in the work order.

Top-level keys: `ref` (default inspection target), `stale_after_days`, `status_sources`,
`errata_path`, `pin_sources`.

### Pin sources

```json
{"path": "AI Agent Audits/evidence/audit_manifest.json",
 "scope": "audited_inputs", "verify_at_key": "audited_commit"}
{"path": "twindow_frozen_authority_hashes.txt", "scope": "frozen"}
{"path": "lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt",
 "scope": "frozen", "relative_to": "lean/AIEFProofs"}
```

* `scope: "frozen"` — bytes must never change. Drift is **critical**.
* `scope: "audited_inputs"` — the hash is the audit-time state. Drift is allowed only if the errata
  file names the file; otherwise **medium**.
* `verify_at_key` — a key in the JSON manifest naming the commit the hashes belong to
  (`audited_commit` here). If that commit is fetchable, pins are verified there; if not, at the current
  ref, and the finding says which.
* `relative_to` — resolve bare filenames against that directory (Lean sums files list `AIEFProofs.lean`,
  not `lean/AIEFProofs/AIEFProofs.lean`).
* Entries that are globs, aggregates or prose (`runs/x/* (aggregate …)`) are skipped: they are not files.

---

## State files

| Path | Tracked | Purpose |
|---|---|---|
| `loop/state.json` | yes | Cycle counter, the durable queue, per-item history, last chosen action. |
| `loop/NEXT.md` | yes | The current work order. Regenerated by every `tick`. |
| `loop/JOURNAL.md` | yes | Append-only record of each cycle and each closed item. |
| `loop/snapshot.json` | ignored | Last full fact snapshot (large, regenerated). |

Keeping `state.json`, `NEXT.md` and `JOURNAL.md` in git is deliberate: the loop survives a new
session, a new machine and a new model. "Where were we?" is a file read, not a guess.

Item lifecycle: `open` → `in_progress` (selected by a cycle) → `done` (closed by the agent) or
`resolved` (the rule stopped firing on its own) or `deferred`. If a finding reappears after being
closed, the item reopens with a note — a regression is a fact worth keeping.

---

## Environment

| Variable | Effect |
|---|---|
| `CHRONICLER_REPO` | Inspect another checkout (used by the tests). |
| `CHRONICLER_LOOP_DIR` | Keep loop state elsewhere (scratch runs, tests). |
| `CHRONICLER_OFFLINE` | Same as `--offline`. |

---

## Tests

```bash
python -m unittest discover -s chronicler/tests -v      # stdlib only
```

The suite covers the token classifier (the part most likely to produce false findings), the date
extractor, reconciliation and regression reopening, id stability, and one end-to-end run against a
temporary git repository.

---

## Design constraints

1. **Deterministic.** Same tree, same snapshot, same findings, same ids. No randomness, no timestamps
   inside findings; only in the snapshot envelope.
2. **Read-only unless told otherwise.** `collect`, `check` and `status` never write. Only `tick`,
   `close` and `defer` mutate loop state, and only inside `loop/`.
3. **Precision over recall.** A false finding teaches the agent to distrust the tool. Ambiguity is
   skipped or demoted to `low`/`info`, never guessed.
4. **Honest degradation.** Missing network, missing history, missing refs are reported as such.
5. **No science.** The tool never edits a claim, a status label or a scope. It points; the agent and
   the owner decide.
