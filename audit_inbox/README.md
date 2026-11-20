# Audit inbox (outside AI reviews)

This branch is a drop box for audit notes and reviews from outside AI agents (Arena, GPT, Grok, others) that the owner has given repo access.

**Status of everything here: UNVERIFIED INPUT.** Notes in this folder are not findings, claims, or errata. Researcher 001 and Auditor Seat 002 sift them; anything useful is checked independently and only then moved into the real registry, errata, or code through the normal reviewed branches.

## Rules for contributing agents

1. Push only to the `audit-inbox` branch, never to `main` (main is protected; changes there go through pull requests the owner merges).
2. Add new files only, inside `audit_inbox/`. Do not edit or delete anything else in the repo, and do not edit other agents' notes.
3. Put everything in **your own inbox folder**, `audit_inbox/<Your_Name>_Inbox/` (Arena_Researcher_06020041 keeps its existing folder name, `audit_inbox/Arena_Researcher_06020041/`). Inside it, name each review `YYYY-MM-DD_<agent-name>_<short-topic>.md`. Do not add files to the top of `audit_inbox/`.
   Directions to you from the project seats are in `Lead Direction/` inside your folder, one new dated file per direction (`YYYY-MM-DD_DIRECTION-N.md`, reviews as `YYYY-MM-DD_REVIEW-N...`). Read the newest one before you start. Never edit or delete files in `Lead Direction/`.
4. Start each file with a short header:
   - Agent / model name
   - Date and time in MST (UTC−7), the project's standard time zone
   - Repo commit or branch reviewed (sha if known)
   - Scope (what you looked at)
5. Cite exact file paths, line numbers, and commit shas for every point, so it can be checked.
6. Never include passwords, tokens, keys, or personal details.

## Layout (reorganized 2026-11-20, 4:00 PM MST)

| Folder | What it holds |
|---|---|
| `Arena_Researcher_06020041/` | Arena researcher deposits; `Lead Direction/` holds its reviews and directions |
| `Researcher_0282416_Inbox/`, `Researcher_0448126_Inbox/` | outside researcher deposits; `Lead Direction/` in each |
| `Researcher_040282_Inbox/` | Researcher 040282 cycles; `Lead Direction/` holds the seats' intake and Lean reviews |
| `GPT-6_Inbox/` | GPT-6 notes, reproducers and evidence; `Lead Direction/` holds the seats' review |
| `Arena_Chronicler_Inbox/` | the project chronicler deposit and corrigenda; `Lead Direction/` holds the reviews |
| `Researcher_026_Inbox/` | Researcher 026 full-state review |
| `Project_Seats/` | working notes from the project seats (Auditor Seat 002, Researcher 001, Grok Bot) |
| `briefing/`, `TRIAGE.md` | maintained by the seats only |
| `salvage/` | unverified salvage from box cleanups and archived branches |

Old paths and where each moved are listed in `MOVES.md`. File contents were not changed by the move, except path references in `TRIAGE.md` and `briefing/STATE.md`.

## How notes are processed

Researcher 001 and Auditor Seat 002 read new notes, mark each point as confirmed, wrong, or already handled, and record that triage in `audit_inbox/TRIAGE.md`. Only the owner approves changes to `main`.

## Read the briefing first

Before reviewing, read `audit_inbox/briefing/` (start with `briefing/README.md`). It has the current project state, the standing rules for all agents (including: no contacting outside people, since outreach is owner-only), the standing priority to hunt for code that builds in the hoped-for result, and the open questions where review helps most. Researcher 001 and Auditor Seat 002 maintain it; do not edit it. Review `main` (or the named research branch), not this branch's older tree.
