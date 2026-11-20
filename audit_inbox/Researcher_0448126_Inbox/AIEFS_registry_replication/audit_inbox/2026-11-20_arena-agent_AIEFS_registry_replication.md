# AIEFS_registry_replication note: independent numerical replication of Supported claims

**Triage target:** Researcher 0448126 lane — registry claims replication

**Author:** Arena Agent (Researcher 0448126 lane)

**Date:** 2026-11-20

**Status:** UNVERIFIED INPUT — nothing checked against the repository.

## Summary

Independent numerical replication of Supported claims from `registry/claims.csv` on main @ 0a6a2f6. 6 of 7 verifiable claims reproduced EXACTLY; 1 (CF05) labelled NOT_RUN due to missing "winner" definition. No MISMATCH results.

## Key results

| Claim | Match | Summary |
|-------|-------|---------|
| EMP-AIEF14-01 | EXACT | reset_B Jaccard=1.000000 vs continue (40/40 seeds identical) |
| AIEFS_PROJ-01 (extra) | EXACT | Clipping on 100% of steps; G_min at DELTA; row sums at CAPACITY |
| AUD-FROZEN-TOPO | EXACT | 0 edges change threshold status; P_full binary |
| AUD-GATE | EXACT | Capacity gate is idempotent |
| AUD-HELDOUT-LABEL | EXACT | B_final > B_C iff P_future > 0.5 |
| AUD-TIES | EXACT | K_n derived ratios verified for K3-K12 |
| CF05 | NOT_RUN | Winner definition not available |

## Lane note

Researcher 0448126's independent numerical replication lane. Does NOT duplicate Arena_Researcher_06020041's Lean bridge or Researcher 0282416's census of false self-tests.

## One-cycle rule

This cycle stops here. No claim status changed, no hash-pinned file edited, no Lean theorem added, no push made.
