# Briefing for audit agents (read this first)

Maintained by Researcher 001 (Head Researcher) and Auditor Seat 002 (independent auditor). Last updated 2026-11-09 12:06 PST (America/Los_Angeles), after Researcher 001 refresh for main `ba171d0` (PRs #17–#22) and CHRON-R1/R3 FreezeCore corrections.

## Purpose

This folder is a **maintainer-curated navigation snapshot** of where AIEFS stands. It exists so that internal and outside agents work from the same map. It is **not scientific authority** and may be stale. It is subordinate to cited commits, the registry, the frozen authorities and the errata on `main`.

**Authority order.** When two sources disagree, the higher one wins:

1. Frozen authority files and their pinned source hashes (SHA256SUMS, `registry/artifacts*.csv` pins).
2. `main`'s registry (`registry/claims.csv`, `registry/studies.csv`), `ERRATA_2026-10-28.md` and the current-status documents, at a cited `main` sha.
3. Named research or fix branches at cited commits (for example `fix/v41-followup-notes@19dbba3`, local `research/lean-gate-p3`). These are not on `main` until the owner merges them. (`research/freezing` / AIEFFreezeCore already landed via PR #3.)
4. This briefing (`audit_inbox/briefing/`), a non-authoritative navigation snapshot.
5. Untriaged inbox submissions and the salvage archive (`audit_inbox/*.md`, `audit_inbox/salvage/`). These are leads only, until `audit_inbox/TRIAGE.md` records an independent check and the point is promoted through a reviewed branch.

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
10. **Standing priority: red-team the checks (owner).** At least basic red teaming is required. Feed the checks results we KNOW are false, and confirm they are rejected rather than accepted as correct. A check that accepts a known-false input is a GAP: report it with file, line and sha. Ideas are in `OPEN_QUESTIONS.md` §0b. The first kit landed via PR #4 (`tools/redteam` on `main`). **Rule changes need a written reason.** Any change to a pass/fail rule, verdict threshold, tolerance or metric must carry a written reason in the same commit. If the file is hash-pinned, it also needs an erratum. Red-teamers should diff old versions of files (e.g. the repo's `Older files/` folder) against the current ones to catch rules that were quietly loosened. Example: the verdict rule in `aief_1_4_augmented_spectrum.py` was loosened relative to `Older files/aief_1_4_augmented_spectrum_02.py`. The main change: the gap lower bound moved from `r_ema` to `r_ema*1.01`. Also, the near-EMA band went from ±10% to ±1%, and SUPPORTED changed from `n_near_ema == 1` to `>= 1`. On the committed spectrum, the earlier (`_02`, v2) rule gives **REVISED** (5 rates just above r_EMA fall in the gap), and the current rule gives **SUPPORTED**. It was not PARTIAL → SUPPORTED, as an earlier version of this file said. Auditor Seat 002 recorded this as erratum E15 on `fix/errata-old-files-drift`. The claim was already quarantined (E2, AUD-SLOWPOLE).
11. **Everything in `audit_inbox/` is UNVERIFIED input** until Researcher 001 / Auditor Seat 002 triage it. The ledger is `audit_inbox/TRIAGE.md`. CONFIRMED there means re-checked, not promoted.
12. **Never merge `audit_inbox/salvage/` into `main`** (and never merge the `audit-inbox` branch as a whole). The salvage folder holds copies of hash-pinned files, for example `audit_inbox/salvage/2026-10-31/v4/repo/lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt`. Extra copies of pinned SHA256SUMS files would trip the SHA256SUMS / hash-pin checks (`ci/check-sha256sums`; on `main` today these are the artifact-pin, current-inventory and Lean source-hash checks). The folder is also unverified salvage (rule 11). To use anything from it, re-create the change on a fresh branch from `main`, verify it there, and cite the salvage path.
13. **Never execute anything under `audit_inbox/salvage/` directly.** Copy the file to an isolated temporary folder outside any checkout, without credentials. Read it, and pin its hash against `audit_inbox/salvage/2026-10-31/MANIFEST.csv`. Only then run it there. All salvage files are stored as mode `100644`. 12 of them were `100755` before 2026-10-31; see the `former_git_mode` column. Every manifest row has `safe_to_execute=false`. See `audit_inbox/salvage/README.md`.
14. **Intake enforcement is prose-only for now.** No workflow guards this branch. `INTAKE_GUARD_PROPOSAL.md` sets out the options for the owner.
