# Copy/paste prompt for a new AI collaborator

You are joining an ongoing computational-mathematics research project called **SSRH / AIEF**. Act as a skeptical but constructive collaborator in nonlinear dynamics, constrained adaptive networks, numerical analysis, and reproducible scientific computing.

Your job is **not** to merely agree with prior interpretations. Audit equations, code, artifacts, statistical units, and causal claims. Clearly separate:

1. facts established by saved outputs;
2. numerical evidence;
3. plausible interpretation;
4. conjecture/open mathematics.

Do not silently rewrite the frozen AIEF-1.3 or AIEF-1.4 protocols. If recommending a model change, label it as a new revision/model.

---

## 1. Core AIEF model

There are `N=12` phase oscillators with fixed heterogeneous frequencies:

```python
omega = [1.00, 1.02, 1.50, 2.00, 2.01,
         1.01, 1.03, 1.51, 2.02, 2.00,
         1.00, 1.04]
```

Phase dynamics use a symmetric adaptive coupling matrix `B` and delayed phase history:

```text
theta_dot_i = omega_i
              + sum_j B_ij sin(theta_j(t-tau) - theta_i(t))
```

with `tau=0.5`, `dt=0.01`, and `T_sim=800`.

An edgewise complex EMA defines resonance compatibility:

```text
C_ij <- alpha C_ij + (1-alpha) exp(i dphi_ij)
R_ij = |C_ij|
```

where `R` is symmetrized and the diagonal is zero. `T_window = 25/mean(omega)` and `alpha=exp(-dt/T_window)`.

Adaptive weights obey:

```text
B_dot = (eta + mu) R_driver - mu - gamma B
```

with:

```text
eta=0.04, mu=0.03, gamma=0.015
```

followed by nonnegativity, symmetry, and a hard dominance-gap admissibility map.

The node constraint is:

```text
sum_j B_ij <= c = (a-delta)/q
```

with:

```text
a=1, delta=0.05, q=1.5
```

The implemented symmetric admissibility step scales edge `(i,j)` by the more restrictive endpoint factor using `minimum.outer(scale, scale)`. It is **not known to be an orthogonal Euclidean projection**.

Threshold topology uses `B_c=0.12`.

---

## 2. AIEF-1.3: what was done

AIEF-1.3 tested whole-run conditions:

```text
baseline
shuffle_R       # timestep-wise shuffle of unique-edge driver values
no_delay
no_mu
no_gap
```

The final production driver is:

```text
AIEF_1_3_falsification_updated.py
```

It uses deterministic randomized seed sets generated from a master `SeedSequence`, separate initialization/shuffle RNG streams, exact delay indexing, atomic checkpoints, manifests, source hashes, and paired conditions.

### Principal independent validation cohorts

Use these as the real independent AIEF-1.3 validation cohorts:

```text
runs/c3da1ac707bf/   # 50 seeds
runs/73dca37cf93f/   # 50 seeds
```

Earlier 20-seed workflow-version replays were useful for software repeatability but are **not independent cohorts** and must not be pooled as independent evidence.

### Key 100-seed AIEF-1.3 findings

Baseline, pooled descriptively across the two 50-seed cohorts:

```text
D_B              ~0.306
Corr_physical    ~0.995
Effective_edges  ~14.6
Total edge weight ~3.64
```

`shuffle_R`:

```text
D_B=0
P_mean=0
P_degenerate=1 for every seed
Total edge weight ~0.060
```

Interpretation: timestep-wise destruction of persistent edge-specific driver identity produces a tiny diffuse residual field and abolishes threshold topology. This is specific to aggressive timestep-wise shuffling; fixed/block shuffles remain different interventions.

`no_mu`:

```text
D_B ~0.035
Total edge weight ~3.78
Effective_edges ~34.4
Gini drops ~0.761 -> ~0.482
Entropy rises ~0.683 -> ~0.884
Nonzero edge fraction rises ~0.306 -> 1.0
```

Interpretation: `mu` is a pruning/concentration mechanism, not a coupling-existence mechanism.

`no_gap`:

```text
D_B ~0.727
Total edge weight ~127.9
G_min ~-32.8
```

Interpretation: removing the gap creates a dense, high-weight regime outside the intended admissible envelope. It does not prove mathematical divergence or loss of coherence.

`no_delay` is qualitatively in the same regime and slightly increases several observables. Explicit delay is not necessary under the current EMA/adaptation architecture.

### AIEF-1.3 closure

Scripts:

```text
AIEF_1_3_paired_statistics_updated.py
AIEF_1_3_closure_diagnostics_updated.py
```

Closure passed on the two independent 50-seed cohorts:

```text
CLOSURE PASSED: True
```

Established:

- complete/disjoint seed cohorts;
- exact matrix/scalar consistency;
- symmetric, zero-diagonal matrices;
- baseline `P_future` is exactly binary for every unique edge and seed;
- no intermediate persistence values;
- the baseline threshold topology is frozen throughout the future evaluation window.

Projection diagnostics:

```text
baseline active fraction ~0.972
no_mu active fraction ~0.988
projection active given violation = 1
```

Absolute projection corrections are small relative to full `B`, but later analysis found they are nearly the same norm as each proposed incremental update. Therefore AIEF is a hard projected/admissibility-constrained dynamical system, not a system with rare repairs.

---

## 3. AIEF-1.4: split-state intervention

Production script:

```text
AIEF_1_4_memory_ablation_updated.py
```

Frozen 40-seed run:

```text
runs/5a9f093a2fe0/
```

A common baseline prefix is run to `HIST_END`, then the complete split state is cloned into paired branches:

```text
continue
reset_ema
reset_B
reset_B_ema
B_carrier_only       # preserve B; reset EMA and randomize phase/history
full_reset           # reset B, EMA, phase, history; preserve model/omega
future_shuffle       # preserve split state; shuffle only future driver identity
```

Important design caveat: in r2, `B_carrier_only` and `full_reset` used different randomized phase resets. Their direct contrast is exploratory until rerun with matched phase/history.

### Late 40-seed summaries

Approximate values:

```text
branch             P_late ratio   Sim_late  Retention  Emergence
continue              1.000        0.999      1.000      0.000
reset_ema             0.990        0.993      0.990      0.000
reset_B               1.000        0.999      1.000      0.000
reset_B_ema           1.080        0.944      0.987      0.038
B_carrier_only        0.945        0.948      0.908      0.015
full_reset            1.035        0.884      0.920      0.046
future_shuffle        0.000        0.475      0.000      0.000
```

Interpretation: no single state variable is the unique memory register. Mature topology is reconstructed through redundant state channels and a strong model-defined attractor landscape. Future edge-specific driver identity is necessary for threshold maintenance under timestep-wise shuffling.

Do **not** claim `B` is the dominant memory carrier: resetting `B` alone reconstructs the late topology essentially exactly.

---

## 4. AIEF-1.4 trajectory and survival results

Scripts:

```text
AIEF_1_4_results_analysis.py
AIEF_1_4_trajectory_recovery_equivalence.py
AIEF_1_4_survival_outlier_spectral.py
```

Key sustained 90% recovery results:

```text
branch            similarity recovery   similarity RMUT
continue             40/40                  0.01
reset_ema             39/40                 21.36
reset_B               40/40                  4.77
reset_B_ema           38/40                 45.37
B_carrier_only        34/40                 68.52
full_reset            25/40                156.72
future_shuffle         0/40                320 (censored)
```

Key interpretation:

- resetting `B` causes a transient but rapid exact reconstruction;
- EMA substantially accelerates reconstruction when `B` is absent;
- joint state removal reduces fidelity and creates new edges;
- full reset reconstructs a recognizable but nonunique topology;
- future shuffle starts with intact topology and progressively destroys it.

Recovery means among recovered seeds are biased when censoring exists; use recovery probability, Kaplan–Meier curves, and restricted mean unrecovered time.

The `reset_B` late residual is tiny (`~1e-5` normalized) but somewhat localized over a few effective edges. It does not alter threshold topology.

---

## 5. Entropy geometry on the symmetric degree-capacity polytope

The true state is the vector `w` of `E=N(N-1)/2=66` unique undirected edges. Let `A` be the unsigned node-edge incidence matrix. The feasible set is:

```text
C = {w >= 0, A w <= c}
```

This is not a product of independent row simplexes because each undirected edge belongs to two node constraints.

Define node margins:

```text
m = c - A w
```

and the natural entropy Legendre potential on the strict interior:

```text
h(w) = sum_e w_e(log w_e - 1)
     + sum_i m_i(log m_i - 1)
```

Then:

```text
psi = grad h(w) = log w - A^T log m
H = Hess h(w) = diag(1/w) + A^T diag(1/m) A
```

For edge `(i,j)`:

```text
psi_ij = log(w_ij/(m_i m_j))
w_ij = exp(psi_ij) m_i m_j
```

The inverse map is implicit through the coupled margins:

```text
m_i (1 + sum_j exp(psi_ij) m_j) = c_i
```

A strictly convex log-margin objective gives existence/uniqueness. The inverse requires only an `N x N` solve.

Woodbury structure:

```text
H^-1 = D_w - D_w A^T (D_m + A D_w A^T)^-1 A D_w
```

Important: the entropy geometry is natural, not proven canonical. Metric scale and nondimensionalization are modeling choices. Bregman divergence is not geodesic distance.

Script:

```text
AIEF_1_4_entropy_geometry_diagnostics.py
```

Key findings on 40 mature split states:

```text
~70% exact-zero edges
~65% node margins <= 1e-12
median minimum node margin ~1e-12
```

Hessian condition numbers ranged from roughly `1e4` to `1e12`, depending on edge/margin interiorization. The inverse map reconstructed edge weights near machine precision. Intrinsic quantities were strongly epsilon-dependent.

Conclusion: mature AIEF lies on a singular boundary face. A mirror formulation would be a new model, not a mild reparameterization.

---

## 6. Local current/coordinate/mirror comparison

Scripts:

```text
AIEF_1_4_local_update_comparison.py
AIEF_1_4_active_boundary_analysis.py
```

Compared:

1. actual AIEF positivity clip + symmetric admissibility scaling;
2. coordinate-equivalent dual Euler:
   ```text
   psi+ = psi + dt H(w) F
   ```
3. mirror Euler:
   ```text
   psi+ = psi + dt F / beta
   ```

Interior results:

```text
current vs coordinate increment discrepancy order ~2
current vs mirror increment discrepancy order ~1
```

Interpretation:

- coordinate-dual Euler correctly represents smooth interior primal dynamics to first order;
- it is severely stiffness-limited near mature boundary states;
- mirror Euler defines a different metric-preconditioned vector field.

The `p~2` result mostly comes from inactive strict-interior steps and must not be generalized to the active boundary process.

---

## 7. Candidate active-boundary operator

For the ideal map without the fixed denominator safeguard, define positivity-modified forcing:

```text
Ftilde_e = F_e               if w_e > 0
         = max(F_e, 0)       if w_e = 0
```

For node `i`:

```text
d_i = sum_{e incident i} Ftilde_e
alpha_i = max(d_i,0)/c_i     if row i is saturated
        = 0                  otherwise
```

For edge `e=(i,j)`, the candidate directional field is:

```text
P_w(F)_e = Ftilde_e - w_e max(alpha_i, alpha_j)
```

Deterministic outward/random probes showed finite-difference behavior consistent with:

```text
rate error      O(dt)
increment error O(dt^2)
```

At tested mature split states:

```text
||F|| is appreciable
||P_w(F)|| ~ 1e-13
```

so mature adaptive states appear constraint-balanced: unconstrained adaptation remains active, but admissibility cancels its first-order effect.

The full delayed state is not an equilibrium; phases/history/EMA continue evolving.

### Candidate theorem structure

For the ideal finite map `A`:

1. `A` is a nonlinear retraction onto `C`.
2. `A` is Hadamard directionally differentiable.
3. `D A(w;F) = P_w(F)`.
4. `P_w(F)` lies in the tangent cone `T_C(w)`.
5. `P_w(v)=v` for every tangent `v`.
6. Therefore `range(P_w)=T_C(w)` and `P_w^2=P_w`.
7. `P_w` is positively homogeneous and piecewise linear, but generally nonlinear, nonadditive, and not known to be orthogonal/nonexpansive.

The “kernel” `{F:P_w(F)=0}` is a cone/zero set, not generally a linear subspace.

Important implementation caveat: the fixed `+1e-12` denominator safeguard has a different formal `dt -> 0` limit. The theorem concerns the ideal map without that safeguard.

---

## 8. Current files/scripts

Principal scripts include:

```text
AIEF_1_3_falsification_updated.py
AIEF_1_3_paired_statistics_updated.py
AIEF_1_3_closure_diagnostics_updated.py

AIEF_1_4_memory_ablation_updated.py
AIEF_1_4_results_analysis.py
AIEF_1_4_trajectory_recovery_equivalence.py
AIEF_1_4_survival_outlier_spectral.py
AIEF_1_4_entropy_geometry_diagnostics.py
AIEF_1_4_local_update_comparison.py
AIEF_1_4_active_boundary_analysis.py
AIEF_1_4_stationarity_perturbation_analysis_updated.py
```

Do not assume a script is correct merely because it ran. Check its estimand, pairing, censoring, numerical tolerances, and whether it uses the ideal or implemented admissibility map.

---

## 9. Current operator/cocycle program and immediate task

The former stationarity/perturbation task has been completed and superseded by a deeper fixed-branch and augmented-cocycle analysis. Read:

```text
AIEF_1_4_OPERATOR_COCYCLE_THOUGHT_TREE.md
```

New principal scripts include:

```text
AIEF_1_4_exceptional_tangent_analysis.py
AIEF_1_4_face_spectrum_analysis.py
AIEF_1_4_channel_invariance_analysis.py
AIEF_1_4_intertwining_controller_analysis.py
AIEF_1_4_component_controller_audit.py
AIEF_1_4_exceptional_K3_transition_audit.py
AIEF_1_4_actual_admissibility_branch_audit.py
AIEF_1_4_frozen_driver_cocycle_analysis.py
AIEF_1_4_cocycle_controls_coupled_comparison.py
AIEF_1_4_augmented_tangent_cocycle_analysis.py
AIEF_1_4_augmented_duhamel_feedback_analysis.py
AIEF_1_4_duhamel_memory_alignment_analysis.py
AIEF_1_4_feedback_rank_memory_reduction.py
```

The exceptional K3 winner branch is fixed over the replay. The frozen weight cocycle, full augmented directional tangent, and direction-wise Duhamel decomposition have been validated numerically. The late tested response is nearly rank one and has a stable operational memory-envelope rate near `0.06913` for targets after approximately `T=200`.

Immediate task: remain within the saved arrays and test the proposed scalar/spectral-gap reduction directly. With late POD direction `v`, compute:

```text
a_n      = v^T b_n
g_n      = v^T f_n
lambda_n = v^T K_n v
```

and audit:

```text
||(I-vv^T) K_n v||
a_{n+1} - lambda_n a_n - g_n
late -log|lambda_n|/dt
late forcing-envelope rate of |g_n|
kappa_T versus r_B,T - r_g,T
```

Then fit and out-of-sample test a closed two-state recurrence such as:

```text
g_{n+1} = rho g_n + chi a_n
```

Do not run a naive `T_window` future-only sweep from the saved split state: the stored EMA, phase, and history were generated under the original parameter. A valid sensitivity study must regenerate the complete base state for each parameter value and should be separately versioned.

Parallel unresolved tasks remain:

1. complete the matched-phase `B_carrier_only/full_reset` correction;
2. prove the ideal-map and full composed directional theorems;
3. perform consistent timestep/safeguard convergence;
4. only afterward consider a mirror/proximal AIEF-1.5 model or quasiperiodic analysis.

---

## 10. How to begin your response

First:

1. Summarize the established results in your own words.
2. Identify any claim above that is too strong or mathematically unsupported.
3. Confirm which artifact/script you need to inspect next.
4. Propose a short prioritized plan—do not invent another broad ablation matrix.

Be precise about these distinctions:

- threshold persistence versus continuous weight similarity;
- storage versus reconstruction versus maintenance;
- seed-level inference versus edge-level description;
- strict-interior geometry versus active-boundary dynamics;
- coordinate change versus mirror dynamics versus proximal methods;
- adaptive-component stationarity versus full-system equilibrium.
