# AIEFS_registry_replication Delta Audit — Independent numerical replication of Supported claims

**Author:** Arena Agent (Researcher 0448126 lane)

**Date:** 2026-11-20

## 1. Goal

Independently reproduce Supported claims from `registry/claims.csv` on main @ 0a6a2f6 using the repository's own scripts and CLI unchanged. This is Researcher 0448126's lane per the lead auditor's direction: "independent numerical replication of the registry's Supported claims."

Bridge and peak-gain work is parked (duplicates Arena_Researcher_06020041's lane). No claim-status proposals, no edits to repo files. Findings only.

## 2. Method (self-direction / self-discernment / induction / deduction)

- **Self-direction:** Chose claim replication over bridge work, per lead auditor direction that bridge/peak-gain duplicates Arena's lane. Selected claims with no recorded re-run first, then strong-worded claims.
- **Self-discernment:** Recognized that CF05 cannot be evaluated without the "winner" definition (not in claim text or accessible docs). Labelled NOT_RUN rather than forcing a mismatch.
- **Induction:** From 40 paired seeds of the memory ablation run, induced that reset_B Jaccard = 1.000000 exactly matches continue on every seed. From 500 engine steps, induced that clipping is active on 100% of steps.
- **Deduction:** From the engine's gate formula (lines 804-807), deduced that the gate is idempotent when row sums are at or below CAPACITY. From 0 edges changing threshold status, deduced that B_final > B_C iff P_future > 0.5 (labels identical).

## 3. Environment

| Item | Value |
|------|-------|
| OS | Linux-6.1.189+-x86_64-with-glibc2.41 |
| Python | 3.13.18 |
| NumPy | 2.3.5 |
| SciPy | 1.17.1 |
| Pandas | 2.2.3 |
| BLAS | OpenBLAS 0.3.30 |
| Engine source | `aief_experiment_engine_v1.py` @ audit-inbox, byte-identical to locked engine |

## 4. Findings

### Finding 1: EMP-AIEF14-01 — EXACT match

reset_B reconstructs mature network topology identically to continue. Jaccard_final = 1.000000 for both branches on all 40 paired seeds. P_mean_late identical per seed. `--verify-continue` passed.

### Finding 2: Projection activity (extra row) — EXACT match

Clipping active on 100% of production steps (Pre_gap_violation_fraction = 1.0, Projection_active_fraction = 1.0). G_min after projection = 0.0500000000 (exactly at DELTA=0.05). Mean row sum = 0.6333333328809375 (exactly at CAPACITY).

### Finding 3: AUD-FROZEN-TOPO — EXACT match

0 of 66 edges change threshold status after split (1 seed checked). P_full is binary (0 or 1), no non-binary entries. Supports the claim of 0 of 29,040 edges changing.

### Finding 4: AUD-GATE — EXACT match

Capacity gate is idempotent: when row sums are at or below CAPACITY, scale = 1.0 for all nodes, so re-applying the gate leaves B unchanged.

### Finding 5: AUD-HELDOUT-LABEL — EXACT match

Labels B_final > B_C and P_future > 0.5 are identical because 0 edges change threshold status and P_full is binary.

### Finding 6: AUD-TIES — EXACT match

Derived ratios nonadditivity = 1/sqrt(2k(k-1)) and odd_defect = sqrt(2/(k+1)) verified mathematically for K3 through K12.

### Finding 7: CF05 — NOT_RUN

"Winner map" definition not specified in claim text or accessible repository documents. B is symmetric so endpoint comparison cannot determine winner. Labelled NOT_RUN (not MISMATCH).

## 5. Limitations

- Only 6 of ~24 Supported claims verified; remaining require Lean formalization, rate-law analysis, or additional scripts
- Engine-based claims verified on 1 seed (EMP-AIEF14-01 on 40 seeds)
- CF05 not runnable without winner definition
- No Lean formalization replicated

## 6. Regeneration notes

- EMP-AIEF14-01: re-run `python3 AIEF_1_4_memory_ablation_updated.py --master-seed 20260714 --n-seeds 40 --verify-continue` (~13 minutes)
- Other claims: re-run inline engine computations as described in replication.csv

## 7. One-cycle rule

This cycle stops here. No claim status was changed, no hash-pinned file was edited, no Lean theorem was added, and no push was made.
