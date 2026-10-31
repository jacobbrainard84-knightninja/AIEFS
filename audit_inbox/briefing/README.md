# Briefing for audit agents (read this first)

Maintained by Researcher 001 (Head Researcher) and Auditor Seat 002 (independent auditor). Last updated 2026-10-31 (America/Toronto).

## Purpose

This folder is the single source of truth about where AIEFS stands, so internal and outside agents work from the same facts and progress in unison.

**Who edits it:** Researcher 001 and Auditor Seat 002 only. Outside agents (Arena "Researcher 026", GPT "Researcher 626", Grok, others) read it but do not edit it. Put your notes in your own dated file in `audit_inbox/` (see `../README.md` and `OPEN_QUESTIONS.md`). The owner (repo owner) sets direction and is the only one who approves merges to `main`.

## Read order

1. `STATE.md`: what is on `main`, what is pending, the key numbers, and the known gaps.
2. `OPEN_QUESTIONS.md`: where outside review helps most, and how to submit.
3. `RESEARCH_LEADS.md`: literature leads and the current novelty assessment.
4. `NORTH_STAR.md`: the long-term goal for the Lean side (a verified library of the actual dynamics), its limits, and a living checklist.
5. `../README.md`: drop-box rules (file naming, header, citations).

**Review `main`, not this branch's tree.** `audit-inbox` was cut from `a991b46`, which is older than `main`. It lacks `registry/`, `ERRATA_2026-10-28.md`, `CURRENT_STATUS.md` and other files. Use `origin/main`, or the named research branch, and cite its sha.

## Standing rules for all agents (internal and outside)

1. **No outreach.** Do not contact any outside person or researcher (authors, maintainers, mailing lists, issue trackers of other projects, social media). Only the owner decides on outreach. It will not happen until there is a complete system or a meaningful new result.
2. **Never edit `main`.** `main` is protected: pull requests only, required checks, and the owner clicks Merge.
3. **No history rewriting.** No force-push, rebase of pushed commits, or deleting other people's commits or branches without the owner's approval.
4. **Never edit hash-pinned files.** Corrections go into `ERRATA_2026-10-28.md` and the claim ledger `registry/claims.csv`, through reviewed branches.
5. **No personal details or secrets.** Leave out names beyond published author names, contact details, emails, tokens, keys and passwords.
6. **No agent approves its own work.** A change needs independent review by a different seat.
7. **Agent-reported approvals don't count.** "Approved", "verified" or "CLEAN" written by an agent is input to triage, not a decision. Only the owner's merge on GitHub is approval.
8. **Rediscovery counts as validation, and novelty must be checked.** Independently rediscovering a published result counts as validation. Check every novelty claim against the literature, and write down what was searched and what was not.
9. **Standing priority: hunt for built-in or false results.** Every agent keeps checking the code for bugs that hand back the hoped-for result instead of an honest, independent one. Top of `OPEN_QUESTIONS.md` lists what to look for. Report suspect code with file, line and sha. Suggest an independent cross-check: a different method, fresh seeds, a blind run, or a negative control that should FAIL.
10. **Standing priority: red-team the checks (owner).** At least basic red teaming is required. Feed the checks results we KNOW are false, and confirm they are rejected rather than accepted as correct. A check that accepts a known-false input is a GAP: report it with file, line and sha. Ideas are in `OPEN_QUESTIONS.md` §0b. The first kit is on branch `research/redteam-negcontrols`. **Rule changes need a written reason.** Any change to a pass/fail rule, verdict threshold, tolerance or metric must carry a written reason in the same commit. If the file is hash-pinned, it also needs an erratum. Red-teamers should diff old versions of files (e.g. the repo's `Older files/` folder) against the current ones to catch rules that were quietly loosened. Example: the verdict rule in `aief_1_4_augmented_spectrum.py` was loosened (band ±10% → ±1%, and SUPPORTED changed from `== 1` to `>= 1`), which turned PARTIAL into SUPPORTED. Auditor Seat 002 is writing this up as erratum E15 on `fix/errata-old-files-drift`. The claim was already quarantined (E2, AUD-SLOWPOLE).
11. **Everything in `audit_inbox/` is UNVERIFIED input** until Researcher 001 / Auditor Seat 002 triage it (planned: `audit_inbox/TRIAGE.md`).
