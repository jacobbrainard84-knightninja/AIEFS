# Evidence log

Run of **2026-11-08, 22:35–23:00 UTC** against `origin/main` @ `eb3933c`.

## Environment

| Item | Value |
|---|---|
| Python | 3.11.2 |
| git | 2.39.5 |
| Dependencies | none (stdlib only) |
| Clone depth | **shallow**; `history.reliable = false` (5 reachable commits) |
| Network | `git ls-remote origin` reachable; GitHub API reachable via `gh` |
| Working branch | `arena/eae4f5a6-aiefs` (branched from `audit-inbox` @ `e72bdd2`) |

Consequence of the shallow clone: commit-citation checks (`DOC-SHA-UNREACHABLE`) were **suppressed**
by design. Everything else was evaluated.

## Result

| Metric | Value |
|---|---|
| Findings | **8** — high 2, medium 1, low 4, info 1 |
| Documents tracked by the manifest | 15 / 15 present |
| Hash pins verified | **29 / 29 matching**, 0 mismatched, 0 missing |
| Tracked files at `origin/main` | 3,052 |
| Status vocabulary | 14 values parsed from `registry/README.md`; 80 ledger rows; **0 values outside the vocabulary** |
| Tests | **34 passed** (`evidence/tests.txt`) |
| Check exit code | `1` with `--fail-on high` (two high findings), `0` with `--fail-on critical` |

Raw outputs: `findings.txt` (human), `findings.csv` (machine), `snapshot_summary.json` (facts).

## The 8 findings

| # | Severity | Rule | Where | One-line summary |
|---|---|---|---|---|
| 1 | high | `DOC-PATH-MISSING` | `CURRENT_STATUS.md:11,46,47` | Cites `Papers/`, `aief_1_4_full_state_tangent_operator.py`, `aief_1_4_history_cocycle_test.py`, `aief_1_4_branch_tangent_comparison.py`, `aief_1_4_k3_fiber_audit/`; none exist at `eb3933c` |
| 2 | high | `DOC-STALE-VS-SOURCE` | `CURRENT_STATUS.md:3` | Stamped 2026-10-23; `registry/claims.csv` changed 2026-11-08 (17 days later) |
| 3 | medium | `DOC-BRANCH-DRIFT` | `audit_inbox/briefing/STATE.md:13,17,19,23` | 4 tips moved: `main` 395ea53→eb3933c; `fix/comparator-v4-gates` f0aadce→902abe8; `fix/check-manifest-g1g2` 14072c3→13a01d1; `ci/check-sha256sums` 7c3bbba→aababfe. Six branches the table lists are absent from origin; see `branch_and_pr_state.md` |
| 4 | low | `DOC-BARE-REF` | `AIEF_MODULAR_DRIVER_CODING_AGENT_PROMPT.md:743` | `FAILED_manifest.json` — a run output, not a repo file (check only) |
| 5 | low | `DOC-BARE-REF` | `docs/architecture/EPISTEMIC_GOVERNANCE_AND_LAYOUT.md:13` | `provenance.json` — same class |
| 6 | low | `DOC-BARE-REF` | `CURRENT_STATUS.md:46` | three tangent/cocycle scripts named with no matching file (overlaps finding 1) |
| 7 | low | `DOC-BARE-REF` | `audit_inbox/briefing/STATE.md:19` | `hashlib.py` — the planted-file example, not a repo file |
| 8 | info | `DOC-HASH-PINNED` | `AI_AGENT_HANDOFF_PROMPT.md` | pinned by the audit manifest: correct via errata, never in place |

Findings 1–3 and 6 are actionable. 4, 5 and 7 are "check only" by design: bare filenames are usually
runtime outputs, so the tool demotes them rather than accusing the document. Finding 8 is guidance, not
work.

## What this run does NOT establish

- Nothing about whether the claims in those documents are scientifically correct. This is a
  documentation-and-metadata pass; it does not re-run the numerics or the Lean build.
- Nothing about documents outside the 15 registered in `chronicler/docs_manifest.json`. Adding a
  document is a one-line manifest change and should happen when a document starts to matter.
- Nothing about citation validity of old shas (shallow clone).

## Reproducing

```bash
git fetch origin
python3 audit_inbox/2026-11-08_arena-chronicler_project-chronicler/scripts/make_evidence.py
python3 -m unittest discover -s audit_inbox/2026-11-08_arena-chronicler_project-chronicler/scripts/chronicler/tests -v
```

Exit codes and command sequence: `evidence/commands.txt`. Test output: `evidence/tests.txt`.
Both were called `.log` until 2026-11-08, which the root `.gitignore` (`*.log`) silently excluded from
every commit; they are `.txt` now so the deposit actually carries them.
