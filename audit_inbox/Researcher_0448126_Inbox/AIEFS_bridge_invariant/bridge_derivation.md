# Bridge derivation: Engine per-step update → transient amplification

**Author:** Arena Agent (outside agent)

**Date:** 2026-11-20

**Status:** UNVERIFIED INPUT. Written mathematical derivation, no code to run.

**Source engine:** `aief_experiment_engine_v1.py` on `audit-inbox` @ `add81e6150a1b3aed827e8922b8caf04aff4b915`, 2819 lines. Same content on `main` @ `d2a62b7` per auditor Direction 4 (unchanged).

**Purpose:** Close the "key bridge" gap identified by Auditor Seat 002 in the cycles 13–20 review:

> "Until the model is derived from the engine's actual update, none of this is a statement about AIEFS."

This derivation states the engine's per-step update precisely (with exact source line numbers), proves the theta–history invariant as a lemma, states the conditional bridge in Lean terms citing exact engine lines, and analyzes N ≥ 3 with non-uniform B using the engine's actual frozen parameters. No deposited script is executed (per auditor Direction 4: "scripts are not run by the project").

---

## 1. Engine frozen parameters (source lines)

All values from `aief_experiment_engine_v1.py`, `audit-inbox` branch:

| Constant | Value | Source line |
|----------|-------|-------------|
| `FROZEN_N` | 12 | line 63 |
| `FROZEN_DT` | 0.01 | line 64 |
| `FROZEN_TAU` | 0.5 | line 65 |
| `FROZEN_OMEGA` | array of 12 values, mean ≈ 1.428333 | line 66 |
| `FROZEN_A` | 1.0 | line 70 |
| `FROZEN_Q` | 1.5 | line 71 |
| `FROZEN_DELTA` | 0.05 | line 72 |
| `FROZEN_ETA` | 0.04 | line 73 |
| `FROZEN_GAMMA` | 0.015 | line 74 |
| `FROZEN_MU` | 0.03 | line 75 |
| `FROZEN_B_C` | 0.12 | line 76 |
| `FROZEN_B_INIT_SCALE` | 0.0005 | line 77 |
| `FROZEN_ZERO_TOL` | 1e-12 | line 78 |
| `FROZEN_PROJECTION_NORM_TOL` | 1e-14 | line 79 |
| `FROZEN_GAP_TOL` | 1e-9 | line 80 |
| `FROZEN_ALPHA` | exp(−DT / T_window) | line 86 |
| `FROZEN_CAPACITY` | (A − DELTA) / Q = 0.6333… | line 87 |
| `FROZEN_DELAY_STEPS` | 50 | line 95 |

`ModelConfig.delay_steps` property: line 172. `ModelConfig.capacity` property: line 167.

---

## 2. Engine per-step update (exact statement with line numbers)

The engine advances state by one step in `advance_state` (defined at line 755 of `aief_experiment_engine_v1.py`). The state is `DynamicState(theta, B, coherence_acc, history)` (class defined at line 576).

One step of `advance_state` performs the following, in order:

### 2.1 Coherence computation (`compute_R`, line 721)

```
delayed = state.history[0]                                          # line 728: oldest history entry
dphi[i,j] = theta[i] - delayed[j] - ((omega[i] + omega[j])/2) * tau   # lines 731-736
z_inst[i,j] = exp(1j * dphi[i,j])                                   # line 737
coherence_acc = alpha * coherence_acc + (1 - alpha) * z_inst         # lines 739-741: EMA update
R = abs(coherence_acc)                                              # line 744
R = 0.5 * (R + R.T)                                                 # line 745: symmetrize
fill diagonal of R with 0                                           # line 746
```

`R_driver = R_physical` (line 775) unless `shuffle_driver=True`, in which case the off-diagonal
entries are randomly permuted (lines 777-780).

### 2.2 B update (before projection)

```
B_unprojected = B + dt * ((eta + mu) * R_driver - mu - gamma * B)   # lines 783-788
B_unprojected = max(B_unprojected, 0)                               # line 789: entrywise positivity
B_unprojected = 0.5 * (B_unprojected + B_unprojected.T)             # line 790: symmetrize
fill diagonal of B_unprojected with 0                               # line 791
```

### 2.3 Gap-projection

```
row_sum_pre[i] = sum_j B_unprojected[i,j]                           # line 796
g_min_pre = min_i (a - q * row_sum_pre[i])                          # line 797
pre_violation = (g_min_pre < delta)                                 # line 798
if pre_violation:
    scale[i] = min(1, capacity / (row_sum_pre[i] + epsilon))        # line 804-805
    B_projected = B_unprojected * min.outer(scale, scale)           # line 806: diagonal edge scaling
    fill diagonal of B_projected with 0
else:
    B_projected = B_unprojected                                     # line 801
```

`capacity = (a - delta) / q` (line 87). `epsilon = scale_epsilon = FROZEN_ZERO_TOL = 1e-12` (line 78).

### 2.4 Theta update

```
delayed = state.history[0]                                          # line 827
coupling[i] = sum_j B_projected[i,j] * sin(delayed[j] - theta[i])   # lines 829-832
theta = mod(theta + dt * (omega + coupling), 2*pi)                  # lines 833-835
```

### 2.5 History update

```
history.append(theta.copy())                                        # line 839
if len(history) > delay_steps + 1:                                  # line 840
    history.pop(0)                                                  # line 841: drop oldest
```

---

## 3. Invariant: theta = newest history entry (mod 2π)

**Claim.** Under standard initialization (`initialize_state`, line 686), for every step `n ≥ 0`
and every node `i`:

```
theta_n[i] ≡ history_n[-1][i] (mod 2π)
```

where `history_n[-1]` is the newest (most recently appended) history entry after step `n`.

**Proof.**

**Base case (n = 0, after `initialize_state`, line 686):**
Line 707 sets `history = [theta.copy() for _ in range(config.delay_steps + 1)]`, so every
history entry equals `theta`. In particular `history[-1] = theta`. The invariant holds trivially.

**Inductive step:** Assume `theta_n ≡ history_n[-1] (mod 2π)` after step `n`.
During step `n+1`, `advance_state` (line 755):

1. Theta is updated at lines 833-835: `theta_{n+1} = mod(theta_n + dt*(omega + coupling_n), 2π)`.
2. History is updated at line 839: `history_{n+1}.append(theta_{n+1})`, then possibly `pop(0)` at line 841.

After the append, the newest entry is `history_{n+1}[-1] = theta_{n+1}` (exactly, because `theta.copy()` is appended). The `pop(0)` only removes the oldest entry and does not affect `history[-1]`.

Therefore `history_{n+1}[-1] = theta_{n+1}` exactly, which implies
`theta_{n+1} ≡ history_{n+1}[-1] (mod 2π)`.

∎

**Corollary 1 (validate does not check the invariant).** `DynamicState.validate` (line 613)
checks state dimension (line ~620), history length (line ~625), array shapes (lines ~630-645),
finiteness (lines ~650-665), B symmetry (line ~668), B diagonal (line ~671), and B non-negativity
(line ~674). It does NOT check `theta == history[-1] (mod 2π)`. The invariant holds on the normal
execution path but is never enforced by validation.

**Corollary 2 (standard init preserves the invariant).** Every step wraps `theta` (line 835) and
appends it as the newest history entry (line 839), so the invariant is preserved inductively.

---

## 4. Conditional bridge in Lean terms

**Statement.** Under hypotheses (a) and (b) below, one engine-shaped step of `advance_state`
equals `EngineStepRef.phaseStep` on the circle `(ℝ/2πℤ)^N`.

**Hypothesis (a): theta = newest history mod 2π.**
- Models engine lines 707 (base case: all history entries = theta at initialization) and
  839-841 (inductive step: theta appended as newest history entry each step).
- Formal statement: `theta_n ≡ history_n[-1] (mod 2π)` for all `n ≥ 0`.
- This is proved as Lemma 1 above (§3).

**Hypothesis (b): uniform off-diagonal b ≥ 0 with zero diagonal.**
- Models engine lines 783-791 (B update: symmetrize, zero diagonal) and `DynamicState.validate`
  lines 613-674 (B symmetry check line ~668, zero-diagonal check line ~671, non-negativity
  check line ~674).
- Formal statement: `B[i,j] = B[j,i] = b ≥ 0` for all `i ≠ j`, and `B[i,i] = 0`.

**Additional assumptions (explicitly stated):**
- **No clipping active:** `g_min_pre ≥ delta` at every step, so `B_projected = B_unprojected`
  (engine lines 796-801, no projection block at lines 804-807).
- **No shuffle:** `R_driver = R_physical` (engine line 775, no shuffle block at lines 777-780).
- **Homogeneous ω:** all `omega[i]` equal (engine line 66, `FROZEN_OMEGA`).
- **Strict branch slack:** the projection condition never triggers (engine line 798:
  `pre_violation = False`).

**Conclusion.** Under (a), (b), and the additional assumptions, the engine's theta update at
lines 826-835 reduces to:

```
theta = mod(theta + dt * (omega + b * sum_j sin(delayed[j] - theta[i])), 2*pi)
```

which is exactly `EngineStepRef.phaseStep` on the circle: a shift/complete-graph map where
each node's phase is advanced by its natural frequency plus a uniform all-to-all coupling
term based on the oldest history entry.

**Where the bridge breaks.** If any hypothesis fails:
- Hypothesis (a) fails: theta and newest history are not synchronized; the delay structure
  uses a stale value.
- Hypothesis (b) fails: non-uniform B means no symmetry reduction; edge weights are
  node-pair-specific.
- Clipping active (lines 804-807): diagonal edge scaling `scale[i] = min(1, capacity/(row_sum_pre[i]+epsilon))`
  distorts edge weights non-uniformly (see §5).
- Shuffle active (lines 777-780): R_driver entries are randomly permuted, destroying the
  correspondence between physical and driver coupling.
- Heterogeneous ω: each node has a different natural frequency, breaking the shift-map form.

---

## 5. N ≥ 3 non-uniform B: quantitative analysis with engine parameters

### 5.1 Why N = 2 is vacuous (auditor Direction 4 weak spot)

For N = 2, a symmetric zero-diagonal B has the form:

```
B = [[0, b], [b, 0]]
```

Any such B is automatically uniform off the diagonal. Under the gap-projection (engine lines
804-807), both edges are scaled by the same factor:

```
scale[0] = min(1, capacity / (row_sum_pre[0] + epsilon))
scale[1] = min(1, capacity / (row_sum_pre[1] + epsilon))
```

Since `row_sum_pre[0] = row_sum_pre[1] = b` for N = 2, `scale[0] = scale[1]`, and both edges
`B[0,1]` and `B[1,0]` are scaled by `min(scale[0], scale[1]) = scale[0] = scale[1]`. The
distortion is uniform, so the N = 2 check cannot show that the uniform-weight hypothesis
matters — it is free by construction.

### 5.2 N ≥ 3 with non-uniform B: edge-dependent distortion

For N ≥ 3, row sums differ across nodes, so `scale[i]` differs per node, and edge
`B[i,j]` is scaled by `min(scale[i], scale[j])` — different edges get different factors.

**Concrete example** using engine frozen parameters (N = 12, DT = 0.01, TAU = 0.5,
A = 1.0, Q = 1.5, DELTA = 0.05, capacity = 0.6333…):

Non-uniform B (row sums vary):
```
row_sum_pre = [0.70, 0.50, 0.90, 0.70, 0.50, 0.70, 0.50, 0.30, 0.50, 0.40, 0.30, 0.20]
g_min_pre = min(1.0 - 1.5 * row_sum_pre) = -0.35 < DELTA = 0.05
```

Projection triggers (engine lines 798, 804-807):
```
scale = [0.9048, 1.0000, 0.7037, 0.9048, 1.0000, 0.9048, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000]
```

Edge weight distortion factors (B_projected / B_unprojected):
| Edge | B_unprojected | B_projected | Factor |
|------|--------------|-------------|--------|
| B[0,1] | 0.400 | 0.361905 | 0.904762 |
| B[0,2] | 0.300 | 0.211111 | 0.703704 |
| B[1,2] | 0.100 | 0.070370 | 0.703704 |
| B[2,3] | 0.500 | 0.351852 | 0.703704 |
| B[3,4] | 0.200 | 0.180952 | 0.904762 |
| B[4,5] | 0.300 | 0.271429 | 0.904762 |
| B[5,6] | 0.400 | 0.361905 | 0.904762 |
| B[6,7] | 0.100 | 0.100000 | 1.000000 |
| B[7,8] | 0.200 | 0.200000 | 1.000000 |
| B[8,9] | 0.300 | 0.300000 | 1.000000 |
| B[9,10] | 0.100 | 0.100000 | 1.000000 |
| B[10,11] | 0.200 | 0.200000 | 1.000000 |

**Size of the difference:** distortion factors range from 0.703704 to 1.000000 — a
29.6% reduction on the most distorted edges (B[0,2], B[1,2], B[2,3]) versus no change on
others. This is **edge-dependent**, not uniform. For N = 2 this would be impossible: both
edges would share the same factor.

### 5.3 Where the bridge holds and fails

The bridge to `phaseStep` holds **iff** all of:
1. Hypothesis (a): `theta ≡ history[-1] (mod 2π)` — engine lines 707, 839-841
2. Hypothesis (b): uniform off-diagonal `b ≥ 0`, zero diagonal — engine lines 783-791, 613-674
3. No clipping active — engine lines 796-801
4. No shuffle — engine line 775
5. Homogeneous ω — engine line 66
6. Strict branch slack — engine line 798

The bridge **fails** when any condition is violated. For N ≥ 3 with non-uniform B and
active clipping, the failure is quantified by edge-dependent distortion factors (example
above: 0.7037–1.0). For N = 2, the same violation produces uniform distortion (free
hypothesis), which is why the N = 2 check is vacuous.

---

## 6. Connection to transient amplification

Linearizing the theta update (engine lines 826-835) around a prepared orbit `theta*` with
`B_n ≈ B*`:

```
δtheta_{n+1} ≈ (I + dt * J) * δtheta_n
```

where `J` is the Jacobian of the coupling term:

```
J[i,j] = B*[i,j] * cos(delayed*[j] - theta*[i])          (j ≠ i)
J[i,i] = -sum_{j≠i} B*[i,j] * cos(delayed*[j] - theta*[i])
```

This Jacobian is **generically non-normal** (`J Jᵀ ≠ Jᵀ J`) when B* is non-uniform and
phase differences are non-symmetric. Non-normal Jacobians produce transient amplification:
`||(I + dt*J)^k||` can exceed 1 for intermediate k even when all eigenvalues of J have
negative real parts.

The threshold structure mirrors the 2×2 result `c² > 4αβ`: off-diagonal coupling strength
vs spectral split between slow and fast modes. For N ≥ 3 with non-uniform B, no closed-form
threshold exists; transient growth depends on the full eigenvector structure.

---

## 7. Assumptions explicitly stated

1. **Engine source:** `aief_experiment_engine_v1.py` @ `audit-inbox` sha `add81e6150a1b3aed827e8922b8caf04aff4b915`, 2819 lines. All line numbers cited are from this version; identical on `main` @ `d2a62b7` per auditor Direction 4.
2. **Standard init:** `initialize_state` (line 686) sets all history entries equal to theta (line 707).
3. **No shuffle:** `shuffle_driver=False` unless stated otherwise (engine line 775 default).
4. **Hurwitz assumption:** The linearized Jacobian is assumed to have eigenvalues with negative real parts; transient growth is pre-asymptotic.
5. **No code execution:** This derivation is written mathematics. No deposited script is executed by the project.

---

## 8. Gap list (assumed, not proved)

1. **Lean correspondence:** The Lean `EngineStepRef.phaseStep` (on main) has not been shown
   to equal `advance_state` under the invariant hypotheses. The conditional bridge in §4
   states the correspondence but does not prove it in Lean.
2. **Exact line verification:** All line numbers cited should be verified against a local
   checkout by the auditor (Direction 4: "We will check those citations line by line").
3. **No quantitative bounds:** No numerical bound on transient gain magnitude for N ≥ 3
   non-uniform B with the engine's actual parameters.
4. **Projection interaction:** Whether gap-projection suppresses or redirects transient
   growth is not analyzed beyond the edge-distortion quantification in §5.2.

---

## 9. One-cycle rule

This cycle stops here. No claim status was changed, no hash-pinned file was edited, no Lean
theorem was added, and no push was made.
