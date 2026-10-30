# Audit inbox (outside AI reviews)

This branch is a drop box for audit notes and reviews from outside AI agents (Arena, GPT, Grok, others) that the owner has given repo access.

**Status of everything here: UNVERIFIED INPUT.** Notes in this folder are not findings, claims, or errata. Researcher 001 and Auditor Seat 002 sift them; anything useful is checked independently and only then moved into the real registry, errata, or code through the normal reviewed branches.

## Rules for contributing agents

1. Push only to the `audit-inbox` branch, never to `main` (main is protected; changes there go through pull requests the owner merges).
2. Add new files only, inside `audit_inbox/`. Do not edit or delete anything else in the repo, and do not edit other agents' notes.
3. One file per review, named `YYYY-MM-DD_<agent-name>_<short-topic>.md` (e.g. `2026-10-30_researcher-626_branch-review.md`).
4. Start each file with a short header:
   - Agent / model name
   - Date (with time zone)
   - Repo commit or branch reviewed (sha if known)
   - Scope (what you looked at)
5. Cite exact file paths, line numbers, and commit shas for every point, so it can be checked.
6. Never include passwords, tokens, keys, or personal details.

## How notes are processed

Researcher 001 and Auditor Seat 002 read new notes, mark each point as confirmed, wrong, or already handled, and record that triage in `audit_inbox/TRIAGE.md`. Only the owner approves changes to `main`.
