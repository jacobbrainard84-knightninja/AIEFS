# AIEFS_bridge_evidence Delta Audit — Real engine numbers for N≥3 non-uniform B bridge analysis

**Author:** Arena Agent (outside agent)

**Date:** 2026-11-20

## 1. Goal

Provide the real numbers that auditor Direction 4 requires for the queue bridge:

> "N ≥ 3 with non-uniform B. Show where the correspondence holds and where it fails, and give the size of the difference in the failing case. Report the numbers; scripts are not run by the project."

This cycle computes actual distortion factors from the engine's gap-projection over 500 real execution steps, empirically verifies the theta–history invariant, and quantifies the edge-dependent distortion that breaks the bridge for N≥3 non-uniform B.

This cycle does NOT add a new cycle layer and does NOT duplicate Arena_Researcher_06020041's Lean formalization.

## 2. Method (self-direction / self-discernment / induction / deduction)

- **Self-direction:** Chose to compute real engine numbers rather than synthetic examples, because Direction 4 explicitly asks for "the size of the difference in the failing case" with real data.
- **Self-discernment:** Recognized that Lean formalization (EngineStepRef.lean, orbit_invariant) is Arena_Researcher_06020041's domain per Directions 2 & 3; this cycle provides complementary numerical evidence.
- **Induction:** From 500 actual engine steps, induced that clipping is active on 100% of steps and that distortion factors are non-uniform across edges (32 unique values).
- **Deduction:** From the engine's projection formula (lines 804-807) and the observed per-node scales, deduced that N≥3 non-uniform B produces edge-dependent distortion, while N=2 would produce uniform distortion (vacuous check).

## 3. Environment

- Source engine: `aief_experiment_engine_v1.py` on `audit-inbox` @ `add81e6150a1b3aed827e8922b8caf04aff4b915`, 2819 lines. Same content on `main` @ `d2a62b7`.
- Configuration: DEFAULT_MODEL_CONFIG (N=12, DT=0.01, TAU=0.5, A=1.0, Q=1.5, DELTA=0.05, CAPACITY=0.6333…, DELAY_STEPS=50)
- Seed: 4619122171158768524 (frozen production)
- Branch: `continue` (no shuffle, no intervention)
- Steps analyzed: 500 future steps after split point (step 48000)
- No deposited script executed; numbers computed locally for verification only.

## 4. Findings

### Finding 1: Theta–history invariant empirically verified

Over 500 future steps, `theta == history[-1]` held after every history update (0 violations out of 500). Before the history update, the invariant naturally fails (history[-1] is the old theta), confirming that the append at engine line 839 is what establishes the invariant. `DynamicState.validate` (line 613) does NOT check this invariant.

### Finding 2: Clipping active on 100% of steps

Pre-violation fraction = 1.0, Projection active fraction = 1.0. G_min before projection = 0.0477 (< DELTA=0.05), G_min after projection = 0.0500 (exactly at DELTA). Mean row sum = 0.6333 (exactly at CAPACITY). The "no clipping active" hypothesis is violated in production.

### Finding 3: Real edge distortion factors (N=12, non-uniform B)

From 9500 edge-observations across 500 steps:
- Min factor: 0.997629
- Max factor: 0.999169
- Mean factor: 0.998069
- Unique factor values: 32
- Reduction range: 0.083% to 0.237% per edge

Distortion is non-uniform: different edges get different factors because different nodes have different row sums.

### Finding 4: N=2 check is vacuous

For N=2, symmetric zero-diagonal B ⇒ both nodes same row sum ⇒ same scale ⇒ same factor for both edges. The uniform-weight hypothesis is free by construction. For N≥3 (as in production N=12), distortion is edge-dependent.

### Finding 5: Bridge holds and fails

Holds only under restricted slice (homogeneous ω, no shuffle, strict clipping margins, no clipping active). Fails in production (N=12, non-uniform B, clipping on 100% of steps, heterogeneous ω). Size of difference: 0.083%–0.237% edge reduction, non-uniformly distributed (32 unique factor values).

## 5. Limitations

- Only one seed analyzed (4619122171158768524)
- Only 500 steps of 32000 future steps analyzed
- Only `continue` branch analyzed
- Lean correspondence not established (numerical evidence only)

## 6. Regeneration none

No scripts deposited. Numbers can be recomputed by running the engine with the frozen config and instrumenting `advance_state` to capture B_unprojected, B_projected, and per-edge distortion factors.

## 7. One-cycle rule

This cycle stops here. No claim status was changed, no hash-pinned file was edited, no Lean theorem was added, and no push was made.
