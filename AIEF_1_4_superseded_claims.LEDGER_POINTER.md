# Pointer: `AIEF_1_4_superseded_claims.csv` → `registry/claims.csv`

Added 2026-10-28 by the local merge-prep reconciliation (Researcher 001).

`AIEF_1_4_superseded_claims.csv` (rows S01–S18) is **left byte-for-byte unchanged** because its SHA-256
(`2e841ec6…2727`) is pinned in
`audits/github_reconciliation/recovered_from_workspace_019ff402/zip_only_files/AIEF_1_4_lineage_freeze_manifest.json`.
Editing it would break that pin, so this sidecar file carries the pointer instead.

The single authoritative claim ledger is now `registry/claims.csv`:

- Rows `S01`–`S18` there carry the same IDs, plus `prior_status`, `audited_status`, `audit_source`,
  `reconciliation_note` and `legacy_list_refs`.
- `legacy_list_refs` shows where each item also appeared in the two older prose lists:
  `AIEF_HISTORIC_UNFOLDING.md` §XIX (10 items) and `AIEF_1_4_FORWARD_PLAN.md` §II (13 items).
  All 23 prose items deduplicate into S01–S18. S06, S07, S16, S17 and S18 appear only in this CSV.
- Known conflict: S01's replacement wording ("Memory is redundantly reconstructed") was replaced by the audit's wording
  (`AI Agent Audits/AIEFS_audit_response_2.md` #4). See `registry/claims.csv` rows S01 and EMP-AIEF14-01.
