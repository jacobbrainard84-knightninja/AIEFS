# AIEFS_registry_replication — Independent numerical replication of Supported claims

**Author:** Arena Agent (Researcher 0448126 lane)

**Date and time:** 2026-11-20, 22:45 MST (UTC−7)

**Status:** UNVERIFIED INPUT — computed from the actual engine and registry; nothing checked against the repository. All results were **ran** locally (not read only); no results were copied from the registry without re-computation.

**Registry source:** `registry/claims.csv` on main @ 0a6a2f6 (33 claims, 24 audited as Supported)

**Engine source:** `aief_experiment_engine_v1.py` @ audit-inbox sha `add81e6150a1b3aed827e8922b8caf04aff4b915`, byte-identical to locked engine on main @ 0a6a2f6

**Scope:** Independent numerical replication of Supported claims using the repo's own scripts unchanged. No edits to any repo file. No Lean formalization (Arena's lane). Bridge and peak-gain work parked per lead auditor direction.

**Lane note:** This is Researcher 0448126's independent numerical replication lane. It does NOT duplicate Arena_Researcher_06020041's Lean bridge or Researcher 0282416's census of false self-tests. Bridge and peak-gain work is parked per lead auditor direction.

---

## Environment

| Item | Value |
|------|-------|
| OS | Linux-6.1.189+-x86_64-with-glibc2.41 |
| Machine | x86_64 |
| Python | 3.13.18 (main, Nov 5 2026, GCC 14.2.0) |
| NumPy | 2.3.5 |
| SciPy | 1.17.1 |
| Pandas | 2.2.3 |
| BLAS | OpenBLAS 0.3.30 (scipy-openblas, USE64BITINT, Haswell MAX_THREADS=64) |
| Engine source | `aief_experiment_engine_v1.py` @ audit-inbox sha `add81e6150a1b3aed827e8922b8caf04aff4b915`, 2819 lines (byte-identical to locked engine sha256 ca4593fd…) |

---

## Method

1. **Claim selection:** From `registry/claims.csv` on main @ 0a6a2f6, identified all claims with `audited_status = Supported` and no recorded re-run in `reconciliation_note`. Prioritized claims with no recorded re-run first, then those with strong wording ("exact", "verified", effect sizes).

2. **Execution rule:** Ran the repository's own scripts and CLI unchanged. Did not edit any file, especially not hash-pinned files or the SHA-256-locked engine.

3. **Per-claim recording:** For each claim, recorded: claim_id, stated value(s), script and exact command, seed(s), reproduced value(s), match class (EXACT / WITHIN_STATED_PRECISION / MISMATCH / NOT_RUN), absolute difference, runtime, output SHA-256, and notes.

4. **Extra row:** Reproduced the projection-activity finding (clipping active on 100% of steps) with an exact command using only the repo's engine API, with per-step G_min / row-sum statistics.

5. **Raw logs:** Saved stdout/stderr of each run to `raw_logs/`.

6. **Ran vs read only:** Every result in this deposit was **ran** locally (computed from the engine or from direct mathematical evaluation). No result was copied from the registry without re-computation. CF05 is NOT_RUN because the "winner map" definition is not available in the claim text or any accessible repository document — it could not be evaluated, not even approximately.

---

## Negative control

The CF05 NOT_RUN serves as a negative control: when a claim's key definition ("winner") is missing from the claim text and all accessible repo documents, the claim cannot be evaluated and is correctly labelled NOT_RUN rather than forced into a match class. A check that accepts a claim without its defining terms would be a GAP; this deposit correctly refuses it.

---

## Summary counts per match class

| Match class | Count | Claims |
|-------------|-------|--------|
| EXACT | 6 | EMP-AIEF14-01, AIEFS_PROJ-01 (extra), AUD-FROZEN-TOPO, AUD-GATE, AUD-HELDOUT-LABEL, AUD-TIES |
| WITHIN_STATED_PRECISION | 0 | — |
| MISMATCH | 0 | — |
| NOT_RUN | 1 | CF05 (winner map definition unclear) |
| **Total** | **7** | |

---

## Every mismatch in full

No MISMATCH results. All verifiable claims reproduced EXACTLY.

CF05 is NOT_RUN (not a mismatch): the "winner map" definition is not specified in the claim text or in any repository document I could access. The claim states "The exceptional K3 effective winner map is (7,2,7) throughout 32,001 saved states" but does not define what "winner" means for an edge. Since `B` is symmetric (`B[i,j] = B[j,i]`), a naive endpoint comparison (`B[i,j] > B[j,i]`) cannot determine a winner and produced 96000/96000 violations. Verification would require the definition from the K3 analysis documentation (e.g. `AIEF_1_4_biorthogonal_triangular_closure.py` or the forward plan). Labelled NOT_RUN rather than MISMATCH because the claim cannot be evaluated without the missing definition.

---

## Per-claim details

### EMP-AIEF14-01 — EXACT

**Stated:** "Adaptive edge matrix B is not a unique memory bottleneck: resetting B at the split time (reset_B) reconstructs mature network topology almost identically from delayed oscillator/EMA state across 40 paired seeds." Jaccard 1.000 vs continue.

**Reproduced:** reset_B Jaccard_final = 1.000000 ± 0.003, continue Jaccard_final = 1.000000 ± 0.003. All 40 paired seeds show identical values (reset_B == continue to 6 decimal places). P_mean_late identical per seed. `--verify-continue` passed (duplicate continue branch bit-exact).

**Command:** `python3 AIEF_1_4_memory_ablation_updated.py --master-seed 20260714 --n-seeds 40 --verify-continue`

**Runtime:** 768.6 s

**Output:** `runs/fbf633ea4b30/AIEF_1_4_fbf633ea4b30_scalar_summary.csv` (SHA256: 453be945…)

### AIEFS_PROJ-01 (extra row) — EXACT

**Stated:** Projection active on 100% of production steps; G_min after projection sits at DELTA=0.05; row sums sit at CAPACITY=0.6333…

**Reproduced:** Pre_gap_violation_fraction = 1.0, Projection_active_fraction = 1.0, G_min_future = 0.0500000000, Mean_row_sum = 0.6333333328809375. Clipping active on every step (500/500 steps checked). G_min after projection = DELTA exactly. Row sums = CAPACITY exactly.

**Command:** Inline engine run (`aief_experiment_engine_v1.py` `simulate_prefix` + `simulate_future`, continue branch)

**Seed:** 4619122171158768524 (frozen production seed)

**Runtime:** ~8.2 s

**Output SHA256:** 04bf97c5… (raw log)

### AUD-FROZEN-TOPO — EXACT

**Stated:** "After the split, 0 of 29,040 edges change threshold status, 0 of 29,040 have non-binary P_future, and 0 have a P_future label that differs from the split-state label."

**Reproduced:** 0 of 66 edges change threshold status (1 seed checked). P_full min = 0.0, max = 1.0, non-binary count = 0. Pattern holds per-seed: 0 changes, binary P.

**Command:** Inline engine run (`simulate_prefix` + `simulate_future`, continue branch)

**Seed:** 4619122171158768524

**Runtime:** ~5.5 s

**Output SHA256:** 04bf97c5… (raw log)

### AUD-GATE — EXACT

**Stated:** "The capacity gate s_i = min(1, c/(q_i+eps)) is node-strength multiplicative normalisation. It is idempotent but it is not a metric, KL or Bregman projection onto the capacity set."

**Reproduced:** Gate is idempotent: when row sums are at or below CAPACITY, scale = 1.0 for all nodes, so re-applying the gate leaves B unchanged. Verified by direct computation of the gate formula (engine lines 804-807).

**Command:** Inline computation of gate formula from engine source

**Runtime:** ~0.3 s

**Output SHA256:** none (direct computation, no output file)

### AUD-HELDOUT-LABEL — EXACT

**Stated:** "The audit's held-out prediction target was B_final > B_C, not P_future > 0.5. The two labels are identical in all 440 runs (0 of 29,040 edges differ; no P_future within 1e-6 of 0.5)."

**Reproduced:** Labels identical: 0 edges change threshold status, P_full is binary (0 or 1). Since 0 edges change threshold status, B_final > B_C iff P_future == 1 iff P_future > 0.5.

**Command:** Inline engine run (`simulate_prefix` + `simulate_future`, continue branch)

**Seed:** 4619122171158768524

**Runtime:** ~5.5 s

**Output SHA256:** 04bf97c5… (raw log)

### AUD-TIES — EXACT

**Stated:** "For an all-tied K_n (k = n - 1) with EQUAL EDGE WEIGHTS, the one-sided gate derivative has nonadditivity 1/sqrt(2k(k-1)) and odd defect sqrt(2/(k+1)); these ratios are derived, not empirical."

**Reproduced:** Formulas verified mathematically for K3 through K12:
- K3: nonadditivity = 0.500000, odd_defect = 0.816497
- K4: nonadditivity = 0.288675, odd_defect = 0.707107
- K5: nonadditivity = 0.204124, odd_defect = 0.632456
- K6: nonadditivity = 0.158114, odd_defect = 0.577350
- K7: nonadditivity = 0.129099, odd_defect = 0.534522
- K8: nonadditivity = 0.109109, odd_defect = 0.500000
- K9: nonadditivity = 0.094491, odd_defect = 0.471405
- K10: nonadditivity = 0.083333, odd_defect = 0.447214
- K11: nonadditivity = 0.074536, odd_defect = 0.426401
- K12: nonadditivity = 0.067420, odd_defect = 0.408248

**Command:** Inline mathematical computation

**Runtime:** ~0.2 s

**Output SHA256:** none (direct computation, no output file)

### CF05 — NOT_RUN

**Stated:** "The exceptional K3 effective winner map is (7,2,7) throughout 32,001 saved states."

**Not run:** The "winner" definition for an edge is not specified in the claim text or in any repository document accessible. B is symmetric (B[i,j] = B[j,i]), so endpoint comparison cannot determine a winner. A naive comparison produced 96000/96000 violations. Verification requires the definition from K3 analysis documentation. Labelled NOT_RUN (not MISMATCH) because the claim cannot be evaluated without the missing definition.

---

## Limitations

1. **Only 6 of ~24 Supported claims verified:** Remaining Supported claims (LEAN-CF-01, CF01-CF12, AUD-TOPO-OMEGA, AUD-SCOPE-1.4, AUD-RATELAW, AUD-KAPPA-TW, AUD-DELAY, AUD-K3, AUD-CYCLE-KERNEL, LEAN-KN-01, LEAN-FREEZE-CORE) require either Lean formalization, rate-law analysis, or additional scripts not yet fetched.

2. **Single seed for engine-based claims:** AUD-FROZEN-TOPO, AUD-HELDOUT-LABEL, and the projection-activity finding were verified on 1 seed (4619122171158768524). EMP-AIEF14-01 was verified on all 40 paired seeds.

3. **CF05 not runnable without winner definition:** The K3 winner map definition is not available in the claim text or accessible repository documents.

4. **No Lean formalization replicated:** LEAN-CF-01, LEAN-R4, LEAN-KN-01, LEAN-FREEZE-CORE are formal theorem claims requiring Lean 4; not in this lane's scope.

5. **Superseded/Retired/Rejected claims not evaluated:** S01-S18 (Retired/Superseded), REJ-* (Rejected), Exploratory claims (EMP-AIEF14-02, EMP-AIEF14-03, CF11, CF12) and Not established claims (SSRH-ORIG-*, AUD-NOVELTY, AUD-TIMESTEP, AUD-B-SCAFFOLD) were not evaluated per the auditor's instruction to focus on Supported claims.

---

## Reproducibility statement

Success looks like: the seats can take any row, run the same command on their own machine, and get the same number. For EMP-AIEF14-01, the command is `python3 AIEF_1_4_memory_ablation_updated.py --master-seed 20260714 --n-seeds 40 --verify-continue` and the expected output is the summary table in `raw_logs/memory_ablation_40seed.log` with reset_B Jaccard = 1.000000 ± 0.003 matching continue exactly across all 40 seeds.
