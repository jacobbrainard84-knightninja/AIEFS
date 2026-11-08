# Instructional corpus read for this task

Read at **2026-11-08**, `origin/main` @ `eb3933c` unless the row says the audit-inbox line.
"Depth" is stated honestly: where I read only part of a file, it says so, so the next agent knows
what still needs reading rather than assuming the whole corpus was absorbed.

Authority order used throughout (`audit_inbox/briefing/README.md`): frozen pins → `main` registry and
errata → research/fix branches → briefing → inbox/salvage.

## Governance and workflow (on `main`)

| Document | Role | Depth | What it constrains |
|---|---|---|---|
| `OPERATING_MANUAL.md` | Read every session; overrides other docs on conflict | full | Roles; side-branch-only workflow; hash-pinned files are never edited (errata instead); ledger changes go through `build_claims_reconciliation.py`; validators to run before handoff; **owner approves every push in the current phase**; privacy (§6); 7 "present" checks (§7); major-change draft definition (§5) |
| `registry/README.md` | Claim-label authority | full | Two orthogonal axes (`artifact_status` × `evidence_scope`); three status categories; the exact `## Status vocabulary` block that `lint_claims.py` parses; which inventory is authoritative for what; regenerate `artifacts_current.csv` in the same commit as any file change |
| `docs/REVIEWING.md` | Reviewer guide | full | The exact local check commands; "if `CURRENT_STATUS.md` changed, every factual line should point to a file in the repo" (directly supports `DOC-PATH-MISSING`); PII reported by type+location only; the major-change draft |
| `docs/architecture/EPISTEMIC_GOVERNANCE_AND_LAYOUT.md` | Architecture / migration plan | substantial | Zero-deletion conservation law; stationary locks; two-axis classification; the Stage 1–7 checklist (Stage 7's `ci.yml` is **planned**, which is why planned paths are excluded from path findings); stale counts at lines 27–28 |
| `.github/PULL_REQUEST_TEMPLATE.md` | Every PR's required form | full | Claims-affected table; evidence and reproduction; checks-run list; Lean axiom box; privacy box; major-change boxes; reviewer sign-off — the shape any chronicler PR must fill |
| `.github/workflows/repo-checks.yml` | CI for repo checks | full | The 8 jobs and their scripts; `--strict` file-mode job; the v4.1 and modular pytest expectations |
| `.github/workflows/lean.yml` | CI for Lean | full | Matrix at lines 47–49: three projects, each `required: true`, including `AIEFFreezeCore` — the fact three docs get wrong |
| `PRIVACY_SCRUB_LIST.md` | Privacy/copyright inventory (locations only) | head (~50 lines) | P1–P9 and C1–C8; P4 = home-directory paths are personal data → my evidence redacts the checkout root; P7 = the GitHub username counts as personal; values are never reproduced |

## Instructional prompts (on `main`)

| Document | Role | Depth | What it constrains |
|---|---|---|---|
| `AI_AGENT_HANDOFF_PROMPT.md` | Briefing for a new scientific collaborator | substantial (§1–2, §8–10) | The model, cohorts and caveats; §8's script list; §9's unresolved tasks; §10's response protocol. **Hash-pinned** → corrections go to errata |
| `AIEF_CODING_AGENT_PROMPT.md` | Implementation-only agent prompt | substantial (§1–4, §11–16) | Scope discipline ("deliver working code, not essays"); the mandatory reading list; §12 inference units (seed/graph, not edge); §13 retired claims that must not be revived; §16 forward priority order |
| `AIEF_MODULAR_DRIVER_CODING_AGENT_PROMPT.md` | Modular-platform driver prompt | excerpt (§10.1–10.3 area, line ~560) | `manifest.json` is execution authority; `analysis/` is written only by the analysis layer; no mutable "latest" authority. **Not fully read** — a follow-up sweep should cover it |
| `README.md` | Front door / introduction | substantial | Start-here pointers; scoped audit claims; the 2026-10-28 status banner; "not a tautology, but dominated by persistence"; the field hypothesis for Lean K_n |
| `CURRENT_STATUS.md` | The single status file | substantial (§1–4 + targeted greps) | Two-axis counts; per-study status and pitfalls; §3 categories; §4 been/are/going; the freeze section at 127–135; the dead pointers at 11 and 46–47 |
| `AIEF_1_4_FORWARD_PLAN.md` | Current plan | not read in full | Referenced by the coding prompt as the priority order. A sweep should read it against §16 of that prompt |
| `AIEF_HISTORIC_UNFOLDING.md` | Long-form history | not read | Low churn; correctness matters, currency does not. Deliberately deprioritised |
| `ERRATA_2026-10-28.md` | Corrections to frozen files | structural read | Append-only, never renumber; E1–E18 exist at `eb3933c` (E16 modular driver, E17 v4 label, E18 `test_01.py`) |
| `MERGE_PREP_REPORT.md` | Historical merge report | head (~60 lines) | "Nothing here has been pushed" — a snapshot of a branch, accurate as history |
| `AI Agent Audits/README.md` | Audit folder index | head (~60 lines) | Which audit document takes precedence (`response_3` > `response_2` > `response_1`); the evidence layout; every script used is included so the process can be audited |
| `LICENSING.md`, `NOTICE` | Licence scope | not read | Third-party papers are not licensed by the project. Relevant only to scrubbing decisions |

## Briefing and inbox rules (on the `audit-inbox` line)

| Document | Role | Depth | What it constrains |
|---|---|---|---|
| `audit_inbox/README.md` | Drop-box rules | full | Push only to `audit-inbox`; add files only inside `audit_inbox/`; one file per review, `YYYY-MM-DD_<agent>_<topic>.md`; header (agent, date+tz, commit, scope); cite paths/lines/shas; no secrets; agent "approvals" don't count; everything here is UNVERIFIED |
| `audit_inbox/TRIAGE.md` | Triage ledger | head + tables | Status vocabulary; add rows, never delete; R026-S*/I* rows are the live record of what was confirmed and what was only read |
| `audit_inbox/briefing/README.md` | Read-first briefing | full | Authority order; the 14 standing rules (no outreach; never edit `main`; no history rewriting; no self-approval; red-team the checks; salvage is never merged or executed) |
| `audit_inbox/briefing/STATE.md` | Navigation snapshot | full | The branch table (stale — see R1); key numbers; the freeze section; the Lean/CI paragraph at line 66 (stale) |
| `audit_inbox/briefing/NORTH_STAR.md` | Lean destination and checklist | full | The 7 components and their statuses; the theorem dependency chain; the exact-real vs floating-point modelling choice; three stale lines (R3) |
| `audit_inbox/briefing/OPEN_QUESTIONS.md` | Where review helps most | full | Standing priority: hunt for code that builds in the hoped-for result; red-team the checks; the 16 open items (including item 13, entrypoint integrity — the same defect as R2's dead paths) |
| `audit_inbox/briefing/RESEARCH_LEADS.md` | Literature leads | head (~60 lines) | Novelty labels and the "do not contact" rule; the RES-FREEZE rescope |
| `audit_inbox/briefing/INTAKE_GUARD_PROPOSAL.md` | Intake enforcement options | full | Two options (guard workflow vs PR-only); both need an owner decision; intake is prose-only today |
| `audit_inbox/salvage/README.md` | Salvage handling | full | Never merge, never execute in place; copy out, pin the hash, only then run; all rows `safe_to_execute=false` |

## Still to read (for the next agent)

- `AIEF_1_4_FORWARD_PLAN.md` and `AIEF_HISTORIC_UNFOLDING.md` in full.
- `AIEF_MODULAR_DRIVER_CODING_AGENT_PROMPT.md` in full (only §10 was read).
- `LICENSING.md`, `NOTICE`, and `Registry` definitions beyond the head of `registry/README.md`.
- `AI Agent Audits/AIEFS_audit_response_3.md` — the authoritative audit ledger, if a claim-level task
  ever comes up. Not needed for a documentation-currency job; explicitly out of scope here.
