# Merge-prep local history

The `merge-prep/arena-reconciled` branch on GitHub was uploaded file by file
through a GitHub upload tool, starting from `main` at `853498f`. Its content
matches the local merge-prep commit `487d5a9`, except that three binary files
were not uploaded (see
`audits/github_reconciliation/recovered_from_workspace_019ff402/zip_only_files/BINARIES_NOT_UPLOADED.md`)
and three notes were added: this one, that one, and `PUSH_NOTES.md`
(known limitations of this upload, including file modes).

Because of the file-by-file upload, the local commits below are **not** part of
GitHub's history for this branch. The GitHub commits are named
`merge-prep (n/N): <scope>` instead. The local commits were authored by the AI
agent Researcher 001, plus one commit (`7edbab2`) by the repository owner.

Local commits from `origin/main` (`853498f`) to `487d5a9`, oldest first
(`short hash | author | subject`):

```
7edbab2 | jacobbrainard84-knightninja | Milestone 1 (Stages 1-3): complete SHA-256 inventory, zip/run reconciliation, scientific & AST path lock audits, and status docs
ce8cced | Researcher 001 (local) | Merge origin/arena/d4a487cc-aiefs (7edbab2) into merge-prep: unreconciled, as-is; reconciliation follows in later commits
4b09647 | Researcher 001 (local) | registry: reconcile claims and 1.4 lineage against audit rounds 1-4
751ec2f | Researcher 001 (local) | docs: point the three retired-claim lists at the registry/claims.csv ledger
6dc568c | Researcher 001 (local) | registry: AUD-SLOWPOLE caveat says the 966-dim NO verdict is an audit proposal
070e28a | Researcher 001 (local) | docs: dated caveats for Corr_physical ~0.995 and the retired 'unique slow pole' verdict
9da686c | Researcher 001 (local) | docs: audit-scoped README, verified requirements.txt, corrected REPRODUCING commands
fd781c6 | Researcher 001 (local) | registry/README: licence files exist on main since 115e99e; flag Lean 'All rights reserved' headers instead
d50c958 | Researcher 001 (local) | tools: add validate_registry_against_tree.py (per-row tree check that tolerates main's deletions)
4dcb90f | Researcher 001 (local) | registry: add tree_check_2026_10_28 flags to artifacts.csv and relocation_map.csv
122808e | Researcher 001 (local) | docs: dated audit reconciliation notes in CURRENT_STATUS.md and registry/README.md
2e9523d | Researcher 001 (local) | registry/README: correct changed-SHA breakdown and not-inventoried count
e657013 | Researcher 001 (local) | docs: PRIVACY_SCRUB_LIST.md (locations only, values redacted; nothing scrubbed)
103cef5 | Researcher 001 (local) | docs: correct PNAS stamp line positions in scrub list
d56b0ae | Researcher 001 (local) | docs: restore 4 hash-pinned files to pinned bytes; move dated caveats to ERRATA_2026-10-28.md
c79c2d1 | Researcher 001 (local) | registry: apply MERGE_CHECK claim fixes (kappa per-k, rate-law conditions/bounds, slow-pole quarantine, matched-phase rewording), minor ledger rows, verdicts, owner SSRH status
1da7b53 | Researcher 001 (local) | docs: per-k rate law, quarantine/exploratory wording, status categories, lineage path fix, REPRODUCING §2/§5/§7, requirements note
30e31a6 | Researcher 001 (local) | privacy list: add Origin Documents items, MMS article, YouTube transcript, ORCIDs, grok-ice street address, Papers/ history PII; GitHub username personal; fix INVENTORY line citations (locations and types only)
7920d2b | Researcher 001 (local) | errata: match registry/README section title for status categories
ac792c2 | Researcher 001 (local) | add MERGE_PREP_REPORT.md: honest summary of merge prep, fixes, deviations, checks, open owner items
4356d95 | Researcher 001 (local) | registry/README: exact allowed status values list for automated checks; CURRENT_STATUS: where we've been / are / going
252720d | Researcher 001 (local) | add OPERATING_MANUAL.md: goal, roles, label rules, workflow, staged approvals (major-change draft), privacy, pending automated checks
0118e41 | Researcher 001 (local) | registry: refresh tree_check flags after the pin revert (5 changed SHA, 252 not inventoried); update counts in README, registry/README, report
0d10d14 | Researcher 001 (local) | registry: audited_status holds exactly one Status-vocabulary label; free-text detail moved to new audited_qualifier column (build script, regenerated claims.csv)
11de659 | Researcher 001 (local) | docs: '## Status vocabulary' block in registry/README (exact list for CI lint); point manual, status, report and README at it and at audited_qualifier
2be5c64 | Researcher 001 (local) | privacy: describe local committer email by type only in scrub list
e861124 | Researcher 001 (local) | ci: add PR template, repo-checks workflow, claims lint, hygiene scan, manifest check, CI tests, reviewer guide
21f4f35 | Researcher 001 (local) | docs: OPERATING_MANUAL §7 links the integrated CI files (allowlist is an owner-confirm draft); CURRENT_STATUS §4 adds tested model results and open questions (checked against the ledger)
9053b77 | Researcher 001 (local) | ci: hygiene scan skips Python @ operator and reserved-domain emails (authored by Auditor Seat 002, integrated unchanged)
bdef1e6 | Researcher 001 (local) | docs: REPRODUCING §7 records the Lean re-run; not-inventoried count 252 -> 261 after the CI files
e152397 | Researcher 001 (local) | errata E5: rate-law gap candidate 'within-step R dependence on B' ruled out by Engine v1 update order (file:line evidence); AUD-RATELAW notes updated
d43d757 | Researcher 001 (local) | docs+ledger: unsigned-incidence controller kernel naming (errata E6), 966-dim proposal limits (AUD-SLOWPOLE), equal-edge hypothesis + K4 counterexample (AUD-TIES), formal-math proposals and data-licence decision in CURRENT_STATUS §4, Lean header wording is the standard Mathlib form (not a conflict)
886daf6 | Researcher 001 (local) | lean: Smoke.lean narrow imports (Mathlib.Data.Real.Basic + Mathlib.Tactic.Ring) and standard header; Basic.lean header; source SHA256SUMS updated; errata E7 (not compiled here; AIEFProofs.lean left unchanged because it is audit-manifest pinned)
487d5a9 | Researcher 001 (local) | registry+docs: refresh tree_check flags (2,701 same / 7 changed; ART-0744, ART-0746 now PRESENT_CHANGED_SHA); record Auditor Seat 002 cached Lean build at 886daf6 (7/7 PASS, 115 decls, 3 axioms, 0 warnings, 1,591 jobs; earlier run was at 11de659); rate-law residual split (E5, AUD-RATELAW); K4 counterexample caveats (AUD-TIES)
```
