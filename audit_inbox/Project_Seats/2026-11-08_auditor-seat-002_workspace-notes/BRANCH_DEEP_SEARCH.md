# Deep search of 5 merged branches (2026-10-31, America/Toronto)

origin/main = 395ea53 (PR #2 merge). Fetched with `git fetch --all --prune`. Nothing was pushed or deleted.

| Branch | Tip | Ahead of main | Tip is ancestor of main | PR | Verdict |
|---|---|---|---|---|---|
| audit/nanfix-v2 | cbf2ae7 | 0 | yes | none (came in through PR #1) | safe to delete |
| ci/artifact-pins | a64d90e | 0 | yes | none (came in through PR #1, b49226e) | safe to delete |
| ci/validator-and-lean-matrix | 249ea3f | 0 | yes | none (came in through PR #1, 19e636e) | safe to delete |
| fix/hygiene-allow-data-external | c59eabc | 0 | yes | #2 merged | safe to delete |
| integration/round5 | 893e0b6 | 0 | yes | #1 merged | safe to delete |

## Method
- Unique history: the commits reachable from each branch that are not on main's first-parent chain. That is 54 distinct commits across all five branches: 25 "merge-prep" commits, 4 "post-push-1" commits, the nanfix v2 commits, the CI commits, the lean-kn commits (Researcher 001), the R026 fixes by the "AIEFS merge-prep" agent, and the owner's commits on 10-31.
- For every file version (blob) added or changed in those commits (merge commits compared against their first parent), I checked whether the blob is anywhere in main's tree. For the ones that aren't, I listed lines from the old versions that never appear in main's version of the file.

## Findings
- **Missing from main: 1 path, and it's a move, not a loss.** `AI Agent Audits/evidence/Data from Superconductivity Found in Meteorites/bb24282657_1_1.tar` was deleted in 62c40ca. The same blob (3fbab363) is in main at `data/external/superconductivity_in_meteorites/`. Superseded.
- **Older versions replaced by newer ones on main (23 files):** CURRENT_STATUS.md, ERRATA_2026-10-28.md, OPERATING_MANUAL.md, PUSH_NOTES.md, docs/REVIEWING.md, registry/{README.md, claims.csv, relocation_map.csv, artifacts_current.csv, reconciliation/build_claims_reconciliation.py}, audits/engineering/validate_registry_against_tree.py, compare_b2a95dfbfbe3_ERRATUM.md, lean/AIEFProofsKn/{AIEFProofsKn.lean, README.md, SHA256SUMS}, tools/ci/{check_modes.py, hygiene_allow.txt, lean_presence.sh, tests/test_lean_presence.py}, .github/{PULL_REQUEST_TEMPLATE.md, workflows/lean.yml, workflows/repo-checks.yml}.
  - ERRATA, PUSH_NOTES, ERRATUM.md, AIEFProofsKn.lean, Kn README, check_modes and hygiene_allow: no old line is missing from main.
  - Spot checks: the claims rows AUD-REPRO-B2A95 and IMPL-MODULAR-01 are in main with wording that was updated or extended. Research item (a) in the old CURRENT_STATUS ("generalize dim ker to all n≥3") is marked done in main, and its proofs are in lean/AIEFProofsKn. Main's lean_presence.sh is a stricter rewrite of the old version (it also rejects symlinks and empty files). The old validator defaults (`--base e47bad1`) were replaced on purpose by the fresh-clone-safe default (469f34e).
  - Verdict: superseded or noise. The other blobs are generated inventory CSVs and old CI comments.
- **Nothing found that is new science, a new proof, or a new tool and that is absent from main.** No commit from Researcher 001, "Researcher 026" or the merge-prep agent is lost. Every one stays reachable from main.
- **Not in the repo tree: 2 Researcher 001 audit comments on PRs** (posted from the owner's account):
  - PR #1 (issuecomment-6536420905, 2026-10-30 20:22 America/Toronto): KernelDimFormula 0c8cad0 is **SOUND**. It covers the math, the build, the axioms (only propext, Classical.choice and Quot.sound) and the pins. Main's lean/AIEFProofsKn/README.md:33 still says "pending their audit".
  - PR #2 (issuecomment-6537507570, 2026-10-30 22:00 America/Toronto): **CLEAN WITH NOTES**. It lists follow-ups: a check that every data/external subfolder has a SOURCE.md, the fact that hygiene --strict is blocked by 3 big CSVs, and setting AIEFFreezeCore to required when freezing lands.
  - PR comments survive branch deletion, so this is a convenience copy, not a rescue. It is still useful audit evidence for outside reviewers.
- **Local branches on the box** (not remote; FYI only): local audit/nanfix-v2 7053aa4, ci/artifact-pins df87b65 and ci/validator-and-lean-matrix bb0d321 show 1–2 commits "ahead". These are the pre-upload originals. Each one's tree is identical to the matching remote tip (d248c6f5, 4a0bc6d6, cb24d53b), so nothing is lost there either. /workspace/branches/repo and wt_fix have two of these branches checked out, and the wt worktree has integration/round5 checked out.
- **PII:** commit author metadata on the 2026-10-28/29 commits contains a personal email address. It is not copied into any salvage file. There is no PII in the PR comments.

## Salvage branch (local only, NOT pushed)
- Branch `preserve/merged-branch-salvage`, worktree /workspace/review_r026/wt_salvage. It is based on origin/audit-inbox e4c4048, and the commit is **c27167c**.
- It adds one file, `audit_inbox/2026-10-31_grok-bot_merged-branch-salvage.md`: the header the inbox README requires, a summary of the search, and the two PR audit comments copied word for word with their source URLs.
- I followed the audit-inbox README (new files only, inside `audit_inbox/`, named `YYYY-MM-DD_<agent>_<topic>.md`) rather than a `salvage/<branch>/` folder. No branch had file content worth copying.
- No hash-pinned file was touched.
- To publish it (owner's call): `git -C /workspace/review_r026/wt_salvage push origin preserve/merged-branch-salvage:audit-inbox` (a fast-forward of audit-inbox).
