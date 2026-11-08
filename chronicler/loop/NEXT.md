# CONTINUE — cycle 8

Generated 2026-11-08T22:59:15Z · ref `origin/main` @ `eb3933c` (2026-11-08T19:36:13Z)

## Do this now

**audit_inbox/briefing/STATE.md quotes stale branch tips**

- item: `9f3419be08`
- rule: `DOC-BRANCH-DRIFT` · severity: **medium**
- document: `audit_inbox/briefing/STATE.md`
- priority: severity medium (55), status weight 0.8, total 68.2

4 branch tip(s) moved since this snapshot: main: doc 395ea53 vs live eb3933c; fix/comparator-v4-gates: doc f0aadce vs live 902abe8; fix/check-manifest-g1g2: doc 14072c3 vs live 13a01d1; ci/check-sha256sums: doc 7c3bbba vs live aababfe. Also listed but absent from origin (merged and deleted, or never pushed): fix/errata-old-files-drift, fix/hygiene-allow-data-external, fix/lint-claims-artifacts, fix/lint-claims-fail-closed, research/freezing, research/redteam-negcontrols

### Evidence

- audit_inbox/briefing/STATE.md:13: `main` | `395ea53` (live eb3933c)
- audit_inbox/briefing/STATE.md:17: `fix/comparator-v4-gates` | `f0aadce` (live 902abe8)
- audit_inbox/briefing/STATE.md:19: `fix/check-manifest-g1g2` | `14072c3` (live 13a01d1)
- audit_inbox/briefing/STATE.md:23: `ci/check-sha256sums` | `7c3bbba` (live aababfe)

### Steps

1. Run `git ls-remote origin` and record the retrieval timestamp.
2. Rewrite the tip column from live output, keeping the doc's 'snapshot, not live' warning.
3. Note any branch that exists locally but not on origin, and vice versa.

### Boundaries

- Do not drop the 'branch tips move' caveat. It is what makes the table honest.
- Work on a side branch. Never commit to `main`. Ask the owner before any push.
- Never edit a hash-pinned file; route corrections through the errata file.

### Verify

```
python -m chronicler check --fail-on high
```

### Done when

- The `DOC-BRANCH-DRIFT` finding for `audit_inbox/briefing/STATE.md` no longer appears.
- The document still reads naturally; you did not just delete the offending sentence.

### Record it

```
python -m chronicler close 9f3419be08 --note "what you changed, and how you verified it"
```

## Queue after this item

| # | severity | item | document | rule |
|---|---|---|---|---|
| 1 | low | `8b5beac313` | `AIEF_MODULAR_DRIVER_CODING_AGENT_PROMPT.md` | DOC-BARE-REF |
| 2 | low | `c872e0e9f4` | `docs/architecture/EPISTEMIC_GOVERNANCE_AND_LAYOUT.md` | DOC-BARE-REF |
| 3 | low | `b3fcec81d8` | `audit_inbox/briefing/STATE.md` | DOC-BARE-REF |
| 4 | low | `f6d2f07553` | `CURRENT_STATUS.md` | DOC-BARE-REF |

## Advisory (does not block)

- AI_AGENT_HANDOFF_PROMPT.md is hash-pinned: correct it via errata, not by editing

