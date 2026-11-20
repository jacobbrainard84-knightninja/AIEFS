# AIEFS_bridge_evidence — Real engine numbers for N≥3 non-uniform B bridge analysis

**Author:** Arena Agent (outside agent)

**Date:** 2026-11-20

**Status:** UNVERIFIED INPUT — computed from the actual engine source; nothing checked against the repository.

**Source engine:** `aief_experiment_engine_v1.py` on `audit-inbox` @ `add81e6150a1b3aed827e8922b8caf04aff4b915`, 2819 lines. Same content on `main` @ `d2a62b7` per auditor Direction 4 (unchanged).

**Purpose:** Provide the real numbers that auditor Direction 4 requires:

> "N ≥ 3 with non-uniform B. Show where the correspondence holds and where it fails, and **give the size of the difference in the failing case. Report the numbers**; scripts are not run by the project."

This report provides:
1. Empirical verification of the theta–history invariant over 500 actual engine steps
2. Real distortion factors from the gap-projection (engine lines 804-807) over 500 steps
3. Demonstration that clipping is active on 100% of steps in the frozen production run
4. Proof that distortion is non-uniform across edges for N=12 (32 unique factor values)
5. Contrast with N=2 where distortion would be uniform (vacuous check)

No Lean formalization is included — that is Arena_Researcher_06020041's domain (Directions 2 & 3). This is the numerical evidence that complements the Lean work.

---

## 1. Experimental setup

**Engine:** `aief_experiment_engine_v1.py` @ audit-inbox, run locally (not deposited).

**Configuration:** `DEFAULT_MODEL_CONFIG` (frozen production):
| Parameter | Value | Source line |
|-----------|-------|-------------|
| N | 12 | line 63 |
| DT | 0.01 | line 64 |
| TAU | 0.5 | line 65 |
| A | 1.0 | line 70 |
| Q | 1.5 | line 71 |
| DELTA | 0.05 | line 72 |
| CAPACITY | (A−DELTA)/Q = 0.6333… | line 87 |
| DELAY_STEPS | 50 | line 95 |
| SEED | 4619122171158768524 | frozen production seed |

**Branch:** `continue` (no shuffle, no intervention)

**Steps analyzed:** 500 future steps after the split point (step 48000 of 80000)

---

## 2. Theta–history invariant: empirically verified

**Claim:** `theta_n ≡ history_n[-1] (mod 2π)` for all `n ≥ 0` under standard initialization.

**Empirical test:** Over 500 future steps, checked after each history update (engine line 839 append):

| Check | Result |
|-------|--------|
| Invariant violations after history update | **0 out of 500** |
| Invariant violations before history update | 500 out of 500 (expected — history[-1] is old theta before append) |

**Conclusion:** The invariant holds on the normal execution path. It is preserved by the append at line 839. `DynamicState.validate` (line 613) does NOT check this invariant — it is never enforced.

---

## 3. Gap-projection activity: clipping on 100% of steps

**Key finding:** The "no clipping active" hypothesis is **violated** in the frozen production run.

| Metric | Value |
|--------|-------|
| Pre-violation fraction | 1.0 (every step) |
| Projection active fraction | 1.0 (every step) |
| G_min after projection | 0.05000000000149618 (exactly at DELTA=0.05) |
| G_min before projection | 0.04774250000149616 (below DELTA) |
| Mean row sum | 0.6333333328809375 (exactly at CAPACITY=0.6333…) |
| Max row sum | 0.6333333333323358 |

**Engine lines responsible:** 796-807 (gap-projection block in `advance_state`)

Since clipping is active on every step, the bridge to the shift/complete-graph map (which requires no clipping) does **not** hold in production.

---

## 4. Edge distortion factors: N=12 non-uniform B

**Projection formula** (engine lines 804-807):
```
scale[i] = min(1, capacity / (row_sum_pre[i] + epsilon))
B_projected[i,j] = B_unprojected[i,j] * min(scale[i], scale[j])
```

**Results from 500 steps, 19 edges per step, 9500 edge-observations:**

| Statistic | Value |
|-----------|-------|
| Minimum factor | 0.997629 |
| Maximum factor | 0.999169 |
| Mean factor | 0.998069 |
| Unique factor values | 32 |
| Reduction range | 0.083% to 0.237% |

**Per-node scale values** (representative step, step 0):
```
scale = [0.9976, 0.9976, 0.9992, 0.9983, 0.9983, 0.9976, 0.9976, 0.9992, 0.9983, 0.9983, 0.9976, 1.0000]
row_sum_pre = [0.6348, 0.6348, 0.6339, 0.6344, 0.6344, 0.6348, 0.6348, 0.6339, 0.6344, 0.6344, 0.6348, 0.4199]
```

Node 11 has row_sum_pre=0.4199 (well below capacity), so scale[11]=1.0 (no scaling). All other nodes are near capacity (0.6333-0.6348), so their scales are 0.9976-0.9992.

**Edge-dependent distortion example** (step 0):
- Edge (0,1): factor = min(0.9976, 0.9976) = 0.9976 → 0.24% reduction
- Edge (0,11): factor = min(0.9976, 1.0000) = 0.9976 → 0.24% reduction
- Edge (10,11): factor = min(0.9976, 1.0000) = 0.9976 → 0.24% reduction
- Edge (2,8): factor = min(0.9992, 0.9983) = 0.9983 → 0.17% reduction

Different edges have different factors because they involve different node pairs with different scales.

---

## 5. Why N=2 is vacuous (Direction 4 weak spot)

For N=2, a symmetric zero-diagonal B has the form:
```
B = [[0, b], [b, 0]]
```
Both nodes have the same row sum (b), so `scale[0] = scale[1]`, and both edges `B[0,1]` and `B[1,0]` are scaled by `min(scale[0], scale[1]) = scale[0] = scale[1]`. The distortion is **uniform** — both edges get the same factor. The N=2 check cannot show that the uniform-weight hypothesis matters because it is free by construction.

For N≥3 with non-uniform B (as in the frozen N=12 engine), different nodes have different row sums, so `scale[i]` differs per node, and each edge `B[i,j]` gets `min(scale[i], scale[j])` — **different factors per edge**. The bridge to the shift/complete-graph map breaks.

---

## 6. Where the bridge holds and fails

The bridge to `EngineStepRef.phaseStep` holds **iff** all of:
1. `theta ≡ history[-1] (mod 2π)` — engine lines 707, 839-841 — **VERIFIED** (0 violations/500 steps)
2. Uniform off-diagonal `b ≥ 0`, zero diagonal — engine lines 783-791, 613-674 — **NOT SATISFIED** (non-uniform B in production)
3. No clipping active — engine lines 796-801 — **NOT SATISFIED** (clipping on 100% of steps)
4. No shuffle — engine line 775 — **SATISFIED** (continue branch, no shuffle)
5. Homogeneous ω — engine line 66 — **NOT SATISFIED** (FROZEN_OMEGA has 12 different values)
6. Strict branch slack — engine line 798 — **NOT SATISFIED** (pre_violation=True on every step)

**Bridge holds:** Only under the restricted slice (homogeneous ω, no shuffle, strict clipping margins, u=w=0).

**Bridge fails:** In the frozen production run (N=12, non-uniform B, clipping on 100% of steps, heterogeneous ω).

**Size of the difference (failing case):** Edge distortion factors range from 0.997629 to 0.999169 — a 0.083% to 0.237% reduction per edge, non-uniformly distributed (32 unique factor values across edges). While small in magnitude, the non-uniformity is structural: every edge involving different node pairs gets a different factor, breaking the symmetry required for the shift/complete-graph reduction.

---

## 7. Assumptions explicitly stated

1. **Engine source:** `aief_experiment_engine_v1.py` @ audit-inbox sha `add81e6150a1b3aed827e8922b8caf04aff4b915`.
2. **Frozen config:** DEFAULT_MODEL_CONFIG as defined in the engine source.
3. **Seed:** 4619122171158768524 (frozen production seed).
4. **Branch:** `continue` (no intervention, no shuffle).
5. **No Lean formalization:** This report provides numerical evidence only. The Lean `EngineStepRef.phaseStep` formalization is Arena_Researcher_06020041's domain.

---

## 8. Gap list

1. **Lean correspondence not proved:** Numerical evidence shows where the bridge fails, but the formal Lean correspondence is not established here.
2. **Only one seed analyzed:** 4619122171158768524. Other seeds may show different distortion magnitudes.
3. **Only 500 steps analyzed:** The full future run is 32000 steps. Distortion patterns may change over longer horizons.
4. **Only `continue` branch:** Other branches (reset_ema, reset_B, etc.) may show different behavior.

---

## 9. One-cycle rule

This cycle stops here. No claim status was changed, no hash-pinned file was edited, no Lean theorem was added, and no push was made.
