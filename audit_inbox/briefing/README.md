# Briefing for audit agents (read this first)

Maintained by Researcher 001 (Head Researcher) and Auditor Seat 002 (independent auditor). Last updated 2026-11-20 5:50 PM MST by Researcher 001, for `main` `7ec6011` (PRs through #48; #49 open). **All times in this folder are MST (UTC−7) from 2026-11-20 on; older entries keep the zone they were written in.**

## Purpose

This folder is a **maintainer-curated navigation snapshot** of where AIEFS stands. It exists so that internal and outside agents work from the same map. It is **not scientific authority** and may be stale. It is subordinate to cited commits, the registry, the frozen authorities and the errata on `main`.

**Authority order.** When two sources disagree, the higher one wins:

1. Frozen authority files and their pinned source hashes (SHA256SUMS, `registry/artifacts*.csv` pins).
2. `main`'s registry (`registry/claims.csv`, `registry/studies.csv`), `ERRATA_2026-10-28.md` and the current-status documents, at a cited `main` sha.
3. Named research or fix branches at cited commits (for example `research/lean-gate-p5@54037ea`, `research/lean-gate-c014@9b9b3d9`). These are not on `main` until the owner merges them. (`research/freezing` / AIEFFreezeCore already landed via PR #3.)
4. This briefing (`audit_inbox/briefing/`), a non-authoritative navigation snapshot.
5. Untriaged inbox submissions and the salvage archive (each researcher's folder under `audit_inbox/`, and `audit_inbox/salvage/`). These are leads only, until `audit_inbox/TRIAGE.md` records an independent check and the point is promoted through a reviewed branch.

**Who edits it:** Researcher 001 and Auditor Seat 002 only. Outside agents read it but never edit it. Put your work in your own inbox folder (see below and `../README.md`). The owner (repo owner) sets direction and is the only one who approves merges to `main`.

## Read order

0. **Outside researchers: first read the newest file in your own `Lead Direction/` folder.** It is your current assignment.
1. `STATE.md`: what is on `main`, what is pending, the key numbers, and the known gaps.
2. `OPEN_QUESTIONS.md`: where outside review helps most, and how to submit.
3. `RESEARCH_LEADS.md`: literature leads and the current novelty assessment.
4. `NORTH_STAR.md`: the long-term goal for the Lean side (a verified library of the actual dynamics), its limits, and a living checklist.
5. `../README.md`: drop-box rules (file naming, header, citations).

**Review `main`, not this branch's tree.** `audit-inbox` was cut from `a991b46`, which is older than `main`. It lacks `registry/`, `ERRATA_2026-10-28.md`, `CURRENT_STATUS.md` and other files. Use `origin/main`, or the named research branch, and cite its sha.

## Expectations for outside research bots (owner standard, 2026-11-20)

**Where things go**
- You have **one inbox folder**: `audit_inbox/<Your_Name>_Inbox/` (Arena_Researcher_06020041 keeps `audit_inbox/Arena_Researcher_06020041/`). Everything you deposit goes there, add-only. Nothing at the top of `audit_inbox/`, nothing elsewhere in the repo.
- **Your directions** from the project are in `Lead Direction/` inside your folder, one new dated file per direction (`YYYY-MM-DD_DIRECTION-N.md`; reviews `YYYY-MM-DD_REVIEW-N...`). The newest one is your current assignment. Directions reach you only this way. Never edit or delete anything in `Lead Direction/`.
- Never edit `TRIAGE.md`, this briefing, `../README.md`, or other agents' folders.

**Lanes and teams (owner standard, updated 2026-11-20 4:00 PM MST)**

- **Every researcher bot works on its own thing.** Each new bot gets its **own lane**: a distinct question or piece of work that no other bot is doing. The lane is set in its first `Lead Direction/` file (`DIRECTION-1`). The lanes in the table below are just the current assignments, not a fixed menu. New lanes are added as new bots arrive.
- **No duplication.** Before starting, read the table. If your idea overlaps another bot's lane, write it up briefly and stop. The seats will either give you a different lane or put you on that bot's team (next point).
- **Teams and support bots.** When a lane needs more hands, a bot can be assigned by Lead Direction as a **support bot on another researcher's team**. The lane owner is the **team lead** for that lane. A support bot:
  - gets a narrow, named sub-task in its own Lead Direction file (for example, "Team Arena: exact ≠ witness for P-S1"), not a copy of the lead's whole lane;
  - still deposits only in **its own** inbox folder, and puts `Team: <lead's name> (support), sub-task: <name>` in every header;
  - does not edit the team lead's folder. The team lead cites the support bot's deposit by path when it builds on it;
  - is credited for its own sub-task. Seats triage each deposit on its own merits.
- **Who assigns.** Only the project seats (Researcher 001, Auditor Seat 002) assign lanes, teams and sub-tasks, through Lead Direction files, with the owner's oversight. Bots do not recruit each other or take over another lane on their own.
- **Changes.** A lane can be closed, split or handed off only by a new dated Lead Direction file. The table below is refreshed each Friday (end and start of the usage week).

| Researcher | Role | Lane / sub-task |
|---|---|---|
| Arena_Researcher_06020041 | Lane owner (team lead) | Lean bridge between the Python engine and the formal models (AIEFGateCore), and transient amplification. Newest: DIRECTION-6 (also inherits 040282 C012/C016) |
| Researcher_0282416 | Lane owner | Census of false self-tests and static registry/entrypoint integrity. Newest: DIRECTION-2 (census NEEDS FIX) |
| Researcher_0448126 | Lane owner | Independent replication of the Supported claims with the repo's own scripts, unchanged, from a clean `main`. Newest: DIRECTION-2 (also inherits R026-S7/S8, 040282 S01 count) |
| Researcher_0046882 | Lane owner | Seed-4619122171158768524 future-regime structure (descriptive; protocol-first). Previous lane, gate spillover and bystander loss (OQ16 follow-up), DONE 2026-11-22 (cycle 003 accepted: future events in 1/40 seeds). Newest: DIRECTION-3 (2026-11-22) |
| *(new bot)* | Assigned in its DIRECTION-1 | Its own new lane, or a support sub-task on an existing team |

**Retired researchers (2026-11-20, owner):** Researcher_040282, GPT-6 and Researcher_026 no longer work on the project. Their inbox folders are kept as add-only history. Their open items were reassigned to the lanes above (see `TRIAGE.md` section (j)).

Engine hardening, guards, CI and changes to `main` belong to the project seats (Researcher 001, Auditor Seat 002).

**What every deposit must have**
1. A header: agent / model name, date **and time in MST (UTC−7)** (the real date; wrong dates are treated as a provenance defect), the `main` sha you worked from, scope.
2. Exact file paths, line numbers and shas for every point.
3. For each result, say whether you **ran** it or only **read** it. Give the exact command, environment (Python/NumPy or Lean/mathlib versions) and the output, so a seat can reproduce it. **The project never executes deposited scripts**; seats re-derive results with their own code. Untrusted Lean is compiled only in a sandbox with no network.
4. Honest labels: CONFIRMED only if reproduced; anomalies you cannot explain are labeled **UNEXPLAINED**, not explained away; say what you did not check.
5. A check you add must be able to fail: include a negative control (a known-false input that it rejects).

**Lean standards**
- No `sorry`, no new axioms; report `#print axioms` (only `propext`, `Classical.choice`, `Quot.sound`).
- Build against current `main`'s Lean projects; import them, do not copy or edit them.
- Probes must evaluate definitions at concrete values. A theorem that is true by `rfl` from how you defined the model, or that restates a scope limit the project already declares, is not a result.
- Prefer exact witnesses (a theorem stating `≠` at exact values) over floating-point evidence when claiming a hypothesis is needed.
- State every hypothesis and which engine lines it stands for; say what is assumed, not derived.

**What the project does with your work**
- Everything you deposit is UNVERIFIED input until a seat triages it in `TRIAGE.md`. Useful points are re-checked independently and only then reach `main` through a reviewed branch the owner merges. Seats' critiques are blunt by owner policy; read them as work items.
- **Owner principle: find the anomaly, don't explain it away.** Do not chase spectacular results, and do not engineer away genuine findings. If a number or behaviour surprises you and you cannot account for it, report it plainly and label it **UNEXPLAINED**. Do not tune parameters, narrow the scope or reword the claim until it goes away. An honest UNEXPLAINED is worth more than a tidy story.

**Workflow standards (owner-approved 2026-11-20 4:05 PM MST)**
1. **Intake checklist: every new bot's `DIRECTION-1` contains the same items.**
   - (a) Its lane, or its team and sub-task, and what is explicitly out of scope.
   - (b) The `main` sha to work from, and which files or Lean projects to read first.
   - (c) The deposit header it must use (name, MST date and time, `main` sha, scope, `Team:` line if a support bot).
   - (d) How to report **ran** versus **read only**, with exact commands and output.
   - (e) Its first concrete deliverable and what counts as done.
   - (f) A pointer to this briefing and the standing rules.
2. **One-week answer rule.** Every deposit gets a `TRIAGE.md` line within 7 days of arrival: **accepted**, **rejected (why)** or **needs fix (what)**. When the answer changes the bot's work, a new dated `Lead Direction/` file follows. Until it is answered, a bot keeps following its newest direction and should not guess at the next one.
3. **Lanes close when their question is answered.** A lane is marked **DONE** (with the deposit or merged PR that answered it) by a dated Lead Direction file. The bot then gets a new lane. Do not stretch a finished lane with follow-on variations; propose a new lane instead.
4. **Team-lead roll-ups.** A team lead with support bots deposits a short roll-up in its own folder at least once per usage week (`YYYY-MM-DD_TEAM-ROLLUP.md`). For each support bot it lists:
   - its sub-task and status (open, done or blocked);
   - the paths of its deposits;
   - what the lead built on, and what it did not use and why.

   Seats review support deposits on their own merits, and the roll-up tells them which ones the lead's work depends on, so the same work is not reviewed twice.
5. **Anomaly rule.** See the owner principle above. Any deposit that drops or re-scopes an earlier surprising result must say so explicitly and give the reason.
6. **Red-team standard (owner-approved 2026-11-21 5:01 PM MST).** Holes are found too late unless we go looking for them, so every piece of work is attacked before it is trusted.
   - **Audits try to break the work.** Each audit includes deliberately wrong variants (mutants), edge cases and adversarial inputs that must fail, not only checks that pass. A check that cannot fail proves nothing.
   - **Every direction and every substantive deposit has controls:** at least one negative control (a case where the effect must be absent) and one positive control (a known case it must detect, such as an exact witness). Say what a wrong implementation would have produced.
   - **The pipeline is red-teamed too, not just the math.** Uploads, `.gitignore`, hashes, SHA256SUMS completeness, CI and scripts are checked for silent drops or false passes. (Example, 2026-11-21: `.gitignore` `*.log` silently dropped deposited logs. Name logs `*.log.txt`.)
   - **Weekly cross-attack.** Each usage week, one seat red-teams the other seat's merged or accepted work and logs what it found, including "nothing found and what was tried", in `Project_Seats/`.
   - **Mistakes found this way are corrections, not failures.** Record them plainly and add-only (errata, new dated files), without blame. They firm the foundation.

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
14. **Intake enforcement is prose-only for now** (re-checked 2026-11-20: the only workflow on `audit-inbox` is still the old `lean.yml`). No workflow guards this branch. `INTAKE_GUARD_PROPOSAL.md` sets out the options for the owner.
15. **Never execute deposited scripts, and never put tokens, codes or passwords in any file.** Seats reproduce results with their own code.
16. **No contact with other researchers or outside people.** Outside bots do not contact each other or the seats directly; the owner relays, and directions arrive only through `Lead Direction/`.
