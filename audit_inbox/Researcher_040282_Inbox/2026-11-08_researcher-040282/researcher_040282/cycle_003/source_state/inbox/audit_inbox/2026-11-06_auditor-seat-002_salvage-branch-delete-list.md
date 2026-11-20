# Salvage remote branch delete/keep list (verified)

- Agent: Auditor Seat 002
- Date: 2026-11-06 11:30 Europe/Tirane
- Repo: jacobbrainard84-knightninja/AIEFS
- Commits reviewed: origin/main `2e55eb5`, origin/audit-inbox `f278d11`
- Scope: live remote branches after PRs #3/#4/#5 merged; unique content check of all `salvage/*` tips vs `main` and vs objects reachable from `audit-inbox`

**Status: UNVERIFIED INPUT for outside readers.** Owner approval required before any delete. Nothing was deleted in this pass.

## Live remote branches (2026-11-06)

| Branch | Tip | Recommendation |
|---|---|---|
| `main` | `2e55eb5` | KEEP |
| `audit-inbox` | `f278d11` | KEEP (long-term salvage home) |
| `arena/d4a487cc-aiefs` | `2af3859` | KEEP (owner hold; claim-by-claim reconcile; never merge tree) |
| `fix/check-manifest-g1g2` | `cd64939` | KEEP (unfinished audited work; still ahead of main) |
| `fix/comparator-v4-gates` | `902abe8` | KEEP |
| `fix/lint-claims-combined` | `84622dc` | KEEP |
| `fix/manifest-nonempty` | `92993eb` | KEEP (related checker work; not ancestor of g1g2) |
| `fix/r026-cleanup` | `c0e05ee` | KEEP |
| `ci/check-sha256sums` | `7c3bbba` | KEEP |
| `fix/corr-0995-scope` | `b77ce5f` | DELETE candidate (see note) |
| all 8 `salvage/*` | (table below) | DELETE candidates |

Open PRs: none. PR #6 (`fix/corr-0995-scope-main`) was closed without merge on 2026-11-06: `AI_AGENT_HANDOFF_PROMPT.md` and `AIEF_HISTORIC_UNFOLDING.md` are hash-pinned (ART-0101 / ART-0103 / audit_manifest inputs). Corr_physical scope already lives in `ERRATA_2026-10-28.md` E1 and `registry/claims.csv` AUD-CORR-0995.

## Salvage branches: unique tip paths vs main

Method: `git ls-tree -r` tip minus main; for each leftover path, check whether the blob is reachable from `origin/audit-inbox` (`git rev-list --objects`).

| Branch | Tip | Ahead of main | Paths not on main | Blob already reachable from audit-inbox? | Notes |
|---|---|---|---|---|---|
| `salvage/AIEFS-local-cleanup-untrack` | `dfb176e` | 47 | 4 under `Papers/` | yes | Third-party PDFs; open-source decision keeps them off main. `tools/sync/*` already on main. |
| `salvage/AIEFS-local-final` | `417d9e8` | 49 | same 4 `Papers/` | yes | Same Papers blobs. |
| `salvage/AIEFS_audit_fresh-fix-corr-0995-scope-v2` | `6cb00ea` | 3 | 0 | n/a | Docs-only tip; superseded by ERRATA E1 / AUD-CORR-0995. Copy also under `audit_inbox/salvage/2026-10-31/corr_0995_fix/`. |
| `salvage/AIEFS_audit_fresh-merge-prep-arena-reconciled` | `487d5a9` | 39 | 3 zip_only recovered files | yes | Blobs already in audit-inbox object graph. |
| `salvage/AIEFS_audit_fresh-work-post-push-1` | `0493f26` | 19 | 0 | n/a | Covered by `audit_inbox/salvage/2026-10-31/post_push_1/` etc. |
| `salvage/audit_r001_branches-wt_merge` | `955f82f` | 6 | 0 | n/a | Covered by `audit_inbox/salvage/2026-10-31/audit_r001_branches/`. |
| `salvage/autonomy_setup-main` | `cdbdffa` | 2 | 0 | n/a | Covered by `audit_inbox/salvage/2026-10-31/autonomy_setup/`. |
| `salvage/autonomy_setup-merge-prep-arena-reconciled` | `9071a33` | 32 | 3 zip_only recovered files | yes | Same zip_only blobs as merge-prep salvage. |

No novel science, proof, or tool was found on a salvage tip that is absent from both `main` and the `audit_inbox/salvage/2026-10-31/` archive (plus the Paper PDFs intentionally kept off main).

## Proposed deletes (need owner OK)

1. `salvage/AIEFS-local-cleanup-untrack`
2. `salvage/AIEFS-local-final`
3. `salvage/AIEFS_audit_fresh-fix-corr-0995-scope-v2`
4. `salvage/AIEFS_audit_fresh-merge-prep-arena-reconciled`
5. `salvage/AIEFS_audit_fresh-work-post-push-1`
6. `salvage/audit_r001_branches-wt_merge`
7. `salvage/autonomy_setup-main`
8. `salvage/autonomy_setup-merge-prep-arena-reconciled`
9. Optional: `fix/corr-0995-scope` (obsolete after correct ERRATA/claims placement; do not edit the pinned docs)

## Keep (active / unfinished)

- `main`, `audit-inbox`, `arena/d4a487cc-aiefs`
- Checker/fix branches still ahead of main: `fix/check-manifest-g1g2`, `fix/comparator-v4-gates`, `fix/lint-claims-combined`, `fix/manifest-nonempty`, `fix/r026-cleanup`, `ci/check-sha256sums`

## Not done here

- No branch deleted.
- No push to `main`.
- briefing/STATE.md is still dated 2026-10-31 (PRs #3/#4/#5 now merged); left for a separate maintainer refresh.
