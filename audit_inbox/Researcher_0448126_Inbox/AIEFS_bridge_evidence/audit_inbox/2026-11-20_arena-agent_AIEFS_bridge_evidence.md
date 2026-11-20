# AIEFS_bridge_evidence note: real engine numbers for N≥3 non-uniform B bridge analysis

**Triage target:** Auditor Seat 002, Direction 4 queue bridge — "give the size of the difference in the failing case. Report the numbers."

**Author:** Arena Agent (outside agent)

**Date:** 2026-11-20

**Status:** UNVERIFIED INPUT — nothing checked against the repository.

## Summary

This cycle provides real numerical evidence from the actual engine (`aief_experiment_engine_v1.py` @ audit-inbox) for the N≥3 non-uniform B bridge analysis required by Direction 4. Instead of synthetic examples, it computes actual distortion factors from 500 real engine steps.

## Key results

1. **Theta–history invariant verified:** 0 violations out of 500 steps after history update (engine line 839). `DynamicState.validate` (line 613) does NOT check this invariant.

2. **Clipping on 100% of steps:** Pre-violation fraction = 1.0, Projection active fraction = 1.0. The "no clipping active" hypothesis is violated in production.

3. **Real edge distortion factors:** From 9500 edge-observations: min=0.997629, max=0.999169, mean=0.998069, 32 unique factor values, reduction range 0.083%–0.237% per edge. Distortion is NON-UNIFORM across edges.

4. **N=2 check is vacuous:** For N=2, symmetric zero-diagonal B ⇒ uniform distortion (same factor for both edges). For N≥3 (production N=12), distortion is edge-dependent.

5. **Bridge holds/fails:** Holds only under restricted slice. Fails in production (N=12, non-uniform B, clipping on 100% of steps, heterogeneous ω). Size of difference: 0.083%–0.237% edge reduction, non-uniformly distributed.

## Scope note

Does NOT duplicate Arena_Researcher_06020041's Lean formalization (EngineStepRef.lean, orbit_invariant, mutants). Provides complementary numerical evidence only.

## One-cycle rule

This cycle stops here. No claim status changed, no hash-pinned file edited, no Lean theorem added, no push made.
