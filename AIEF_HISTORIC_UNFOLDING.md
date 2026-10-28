# AIEF historic unfolding

## From falsification experiments to operator geometry, augmented cocycles, and asymptotic reduction

**Updated:** 2026-07-26  
**Frozen principal runs:** AIEF-1.3 independent 100-seed validation and AIEF-1.4 40-seed split-state run

---

## Purpose of this document

This document records how the AIEF research program changed over time: which questions were asked, which implementation problems were discovered, which empirical claims survived falsification, which interpretations were retired, and how the central mathematical object shifted from network statistics to the finite-step admissibility operator and its augmented tangent dynamics.

It is a historical and scientific record, not a paper draft. Statements are classified implicitly according to four levels:

1. **Exact implementation fact** — follows from the code or an algebraic derivation of the implemented map.
2. **Replay-established numerical fact** — measured on saved artifacts with exact replay or audited tolerances.
3. **Mechanistic interpretation** — explains several established facts but remains conditional on the audited replay/model regime.
4. **Open theorem or generalization** — not established beyond the tested seed, branch, directions, or parameter set.

The seed/graph realization is the inferential unit. Edges, perturbation directions, amplitudes, and repeated workflow-version runs are not independent experiments.

---

# I. The model and the original scientific question

AIEF couples delayed phase oscillators to a symmetric adaptive edge-weight field.

For `N=12` oscillators,

\[
\dot\theta_i
=
\omega_i
+
\sum_j B_{ij}
\sin\bigl(\theta_j(t-\tau)-\theta_i(t)\bigr),
\]

with fixed delay

\[
\tau=0.5.
\]

A complex exponential moving average stores edge-specific phase compatibility:

\[
C_{ij}^{n+1}
=
\alpha C_{ij}^n
+
(1-\alpha)e^{i\Delta\phi_{ij}^n},
\]

\[
R_{ij}=|C_{ij}|.
\]

The adaptive field is

\[
F_{ij}
=
(\eta+\mu)R_{ij}
-
\mu
-
\gamma B_{ij},
\]

with

```text
eta=0.04
mu=0.03
gamma=0.015
```

and a hard node-capacity constraint

\[
\sum_jB_{ij}\le c,
\qquad
c=\frac{a-\delta}{q}
=0.633333\ldots.
\]

The implemented symmetric admissibility update first forms an Euler proposal, applies nonnegativity, and then scales each edge by the more restrictive endpoint factor:

```python
projected *= np.minimum.outer(scale, scale)
```

This was initially treated mainly as a constraint-enforcement step. It later became the central mathematical object of the project.

The original broad questions were:

- Does persistent phase compatibility create stable sparse topology?
- Which terms are necessary for topology formation and maintenance?
- Where is structural memory stored?
- Is the mature state an equilibrium, a slow attractor, or an actively constrained state?

---

# II. AIEF-1.3 — turning exploratory code into a falsification experiment

## 1. The first major transition: implementation repair

The earliest AIEF-1.3 work was dominated by code and estimand correction. Important problems included:

- HTML/Markdown corruption in pasted source;
- incorrect delay indexing caused by the history deque;
- row-wise projection that destroyed symmetry;
- a `no_delay` branch that retained a nonzero delay correction inside the resonance calculation;
- a purported shuffle intervention that did not truly destroy temporal edge identity;
- inconsistent treatment of diagonal/self-links;
- correlations computed on duplicated matrix entries rather than unique undirected edges;
- floating-time loop drift;
- a miscomputed gap diagnostic;
- undefined correlations silently replaced by zero;
- overlapping historical and future windows.

These were not cosmetic changes. Several altered the implemented model or the estimand.

The corrected production driver became:

```text
AIEF_1_3_falsification_updated.py
```

It added:

- paired randomized seeds generated through `SeedSequence`;
- separate RNG streams for initialization and shuffle interventions;
- exact delay indexing and constant prehistory;
- a symmetry-preserving capacity map;
- integer-step simulation;
- atomic checkpoints;
- validated resume;
- source/configuration hashes;
- full manifests;
- concentration, degeneracy, and projection diagnostics.

This was the first methodological turning point: AIEF became a reproducible falsification program rather than an exploratory simulation.

## 2. Independent validation cohorts

Two independent 50-seed cohorts were produced:

```text
runs/c3da1ac707bf/
runs/73dca37cf93f/
```

Earlier 20-seed reruns used identical seeds under revised workflows. They were useful software-reproducibility checks but were not independent scientific evidence.

## 3. AIEF-1.3 intervention results

### Baseline

Across the 100 independent seeds, the mature baseline had approximately:

```text
D_B               ~0.306
Corr_physical     ~0.995
Effective_edges   ~14.6
Total edge weight ~3.64
```

Scope note (audit correction 2026-10-23): Corr_physical ~0.995 holds only for the repo's hand-picked frequencies (omega). With random frequencies it drops to about 0.71 (uniform) and 0.59-0.63 (clustered). It is not tautological, but it mostly measures persistence. See `AI Agent Audits/AIEFS_salvage.md` (section 3.1, row 2) and `AI Agent Audits/AIEFS_audit_response.md` (point 2). Do not cite 0.995 as a general result.

Threshold topology became completely frozen during the future evaluation window. Closure analysis later established that every baseline persistence value was exactly binary.

### `shuffle_R`

Timestep-wise destruction of persistent edge-specific resonance identity gave:

```text
D_B=0
P_mean=0
P_degenerate=1 for every seed
Total edge weight ~0.060
```

Interpretation: persistent edge identity in the adaptive driver is necessary for threshold topology under this aggressive shuffle. This does not establish that every weaker or blockwise shuffle would have the same effect.

### `no_mu`

Removing the pruning term produced a dense low-concentration field:

```text
D_B ~0.035
Total edge weight ~3.78
Effective_edges ~34.4
nonzero edge fraction -> 1
```

The conclusion was refined from “mu creates coupling” to:

> `mu` is a pruning and concentration mechanism; it is not required for the existence of coupling.

### `no_gap`

Removing the dominance-gap envelope yielded:

```text
D_B ~0.727
Total edge weight ~127.9
G_min ~-32.8
```

This established a dense, high-weight regime outside the intended envelope. It did not prove mathematical divergence or loss of phase coherence.

### `no_delay`

The no-delay branch remained in the same qualitative regime and slightly increased several observables. Explicit delay was not necessary for topology under the current EMA/adaptation architecture.

## 4. AIEF-1.3 closure

The scripts

```text
AIEF_1_3_paired_statistics_updated.py
AIEF_1_3_closure_diagnostics_updated.py
```

established:

- disjoint independent cohorts;
- exact matrix/scalar consistency;
- symmetric zero-diagonal state matrices;
- exactly binary future topology persistence;
- projection activity whenever a proposed row violated capacity.

Projection corrections were small relative to the full weight matrix, but later work showed that they were comparable to the proposed incremental update. This foreshadowed a major reinterpretation: the admissibility operation was not a rare repair but an active part of the dynamics.

---

# III. AIEF-1.4 — where is memory stored?

## 1. Split-state intervention design

The AIEF-1.4 production experiment used a common mature prefix and cloned the complete split state into paired branches:

```text
continue
reset_ema
reset_B
reset_B_ema
B_carrier_only
full_reset
future_shuffle
```

Frozen run:

```text
runs/5a9f093a2fe0/
```

A design caveat remains: `B_carrier_only` and `full_reset` used different randomized phase/history resets. Their direct contrast remains exploratory until a matched-phase correction is run.

## 2. Memory-ablation results

Late summaries showed:

```text
continue       -> near-perfect retention
reset_ema      -> near-perfect late recovery
reset_B        -> near-perfect reconstruction
reset_B_ema    -> mostly recovers, with some new edges
B_carrier_only -> substantial but incomplete recovery
full_reset     -> recognizable but nonunique recovery
future_shuffle -> threshold maintenance collapses
```

The central conclusion changed from a search for a unique memory register to:

> Mature topology is redundantly reconstructed through several state channels and a strong model-defined attractor landscape.

In particular, `B` cannot be called the unique or dominant memory carrier: resetting `B` alone reconstructs the mature topology almost exactly.

Future edge-specific resonance identity remained necessary for threshold maintenance.

## 3. Recovery-time and survival analysis

Sustained 90% similarity recovery was:

```text
continue          40/40
reset_ema         39/40
reset_B           40/40
reset_B_ema       38/40
B_carrier_only    34/40
full_reset        25/40
future_shuffle     0/40
```

This introduced survival-style analysis, restricted mean unrecovered time, and caution against reporting means only among recovered seeds.

---

# IV. Entropy geometry — a natural interior geometry meets a singular boundary state

The undirected edge state is

\[
w\in\mathbb R^{66},
\qquad
\mathcal C=\{w\ge0:Aw\le c\}.
\]

A natural entropy potential is

\[
h(w)
=
\sum_ew_e(\log w_e-1)
+
\sum_im_i(\log m_i-1),
\qquad
m=c-Aw.
\]

Its gradient and Hessian are

\[
\psi=\log w-A^T\log m,
\]

\[
H=\operatorname{diag}(1/w)+A^T\operatorname{diag}(1/m)A.
\]

A Woodbury formula reduced inversion to a node-space solve.

The inverse map reconstructed weights near machine precision, but mature states had:

```text
~70% exact-zero edges
~65% node margins <=1e-12
minimum margins near1e-12
```

Conditioning depended strongly on interiorization and ranged roughly from `1e4` to `1e12`.

Conclusion:

> Mature AIEF lies on a singular boundary face. The entropy geometry is natural, but not proven canonical. A mirror formulation would be a new model, not a coordinate rewrite.

This halted an early temptation to treat mirror/proximal AIEF as a mild reformulation.

---

# V. The active-boundary operator

## 1. Candidate ideal directional field

For positive and zero edges, define

\[
\widetilde F_e
=
\begin{cases}
F_e,&w_e>0,\\
\max(F_e,0),&w_e=0.
\end{cases}
\]

For a saturated node,

\[
d_i=\sum_{e\ni i}\widetilde F_e,
\qquad
\alpha_i=\frac{\max(d_i,0)}{c_i},
\]

and otherwise \(\alpha_i=0\).

The candidate field is

\[
\mathcal P_{w,e}(F)
=
\widetilde F_e
-
w_e\max(\alpha_i,\alpha_j).
\]

Finite-difference probes supported first-order rate convergence and second-order increment convergence for the ideal map without the fixed denominator safeguard.

## 2. Constraint-balanced maturity

At mature split states:

\[
\|F\|\text{ remained appreciable},
\qquad
\|\mathcal P_w(F)\|\sim10^{-13}.
\]

Thus the adaptive driver remained active, but admissibility cancelled it to first order.

The mature **adaptive component** was constraint-balanced. The full delayed state was not an equilibrium: phase, history, and EMA states continued evolving.

## 3. Operator audits

Across roughly 1.28 million mature updates, numerical implementation checks found no failures of:

- tangent feasibility;
- idempotence;
- positive homogeneity;
- permutation equivariance.

These were audits of the candidate formula, not a proof that it is the Hadamard directional derivative.

---

# VI. The exceptional seed and the first tangent interpretation

One seed differed sharply:

```text
4619122171158768524
```

For 39/40 seeds, the mature adaptive field was stationary to machine precision with no support or saturation changes.

The exceptional seed showed:

```text
one saturation-classifier change
large continuous B drift
nonzero ideal stationarity ratio before the event
near-stationarity afterward
exact deterministic replay
```

The first interpretation was an active-face switch at approximately `t=124.05`, with tangent dimension changing from `9` to `8`.

Corrected tangent experiments reused one direction across all amplitudes and found typical contraction near

\[
0.315789,
\]

with excellent exponential fits. The exceptional directions were slower and less radially clean.

At this stage, the project still treated the tolerance-defined active set as if it were the branch structure of the implemented finite-step map. That interpretation was later retired.

---

# VII. Fixed-face spectra and channel invariance

## 1. Analytic fixed-stratum Jacobian

On a fixed support/saturation/controller stratum, tangent perturbations satisfy constant node corrections, giving

\[
J_T
=
Q_T^T
\operatorname{diag}\bigl(-\gamma-\rho_e\bigr)
Q_T.
\]

Numerical finite differences matched this matrix to roughly `1e-13`–`1e-11`.

Observed rates included:

\[
0.189474,
\qquad
0.252632,
\qquad
0.315789.
\]

## 2. Intertwining and channel decomposition

For active incidence matrix \(C\) and diagonal edge-rate operator \(D\), the analysis tested

\[
CD\approx LC.
\]

Residuals were near machine precision for all 40 split states. The tangent projector commutator was similarly tiny.

The mathematical implication is:

\[
CD=LC
\Longrightarrow
D(\ker C)\subseteq\ker C.
\]

Since \(D\) is diagonal/self-adjoint,

\[
T
=
\bigoplus_r(T\cap E_r),
\]

and rate multiplicity equals the dimension of each channel intersection.

This was the first complete explanation of the repeated tangent spectra, conditional on exact intertwining.

---

# VIII. Component geometry — the clique structure becomes directly visible

The component audit reconstructed actual positive-support components rather than inferring graph classes from spectra.

For 39 ordinary split states:

- all positive-support nodes were saturated;
- every support component was rate-uniform;
- every component passed locked-edge and edge-balance checks;
- explicit component intertwiners reproduced the tangent spectra;
- support components were complete graphs.

Observed combinations included:

```text
K6 + K2 + K3
K6 + K2 + K4
K5 + K2 + K4
K5 + K3 + K4
K5 + K6
```

For a fully saturated locked component of degree \(k\),

\[
r=\frac{k\eta}{c},
\qquad
w=\frac{c}{k}.
\]

Since

\[
\frac\eta c=\frac6{95},
\]

the channel rates are degree-generated.

For \(K_s\), the signless-incidence lineality dimension is

\[
q_s=\binom s2-s=\frac{s(s-3)}2.
\]

Thus:

```text
K2 -> nullity 0
K3 -> nullity 0
K4 -> nullity 2
K5 -> nullity 5
K6 -> nullity 9
```

The previously “missing” `K2` and `K3` components were spectrally silent because they had zero fully constrained face lineality.

The clique hypothesis had changed status: within the frozen cohort, complete support components were now directly measured.

---

# IX. The exceptional K3

The exceptional support was

```text
K5 + K3[partially classified active] + K4
```

with triangle

```text
nodes [2,7,11]
edges [25=(2,7), 29=(2,11), 59=(7,11)]
```

The tolerance-classified K3 changed from one active row to two, explaining the classifier-based nullity change from `2` to `1` and the global dimension change `9 -> 8`.

Dense K3 analysis confirmed the finite-dimensional one-row and two-row algebra. However, boundary-tolerance sensitivity showed that the event time depended strongly on the classifier tolerance.

This prompted the next major question:

> What object was actually being linearized?

---

# X. The actual finite-step branch replaces the classifier picture

For a node, define

\[
\Pi_i
=
\frac{dt\,d_i}{\operatorname{slack}_i}.
\]

At the exceptional split:

```text
node 2: Pi ~2392
node 7: Pi ~5.3e8
node11: Pi <<1
```

Nodes 2 and 7 were already proposal-violating at the first recorded state, even though the slack classifier called only node 7 active.

Node 11 became proposal-violating later, at approximately `t=113.81`, but still did not win an edge.

The actual scale/winner audit reconstructed the finite update exactly and found the winner map remained fixed for all 32,001 states:

\[
(2,7)\mapsto7,
\qquad
(2,11)\mapsto2,
\qquad
(7,11)\mapsto7.
\]

There were:

```text
0 effective-edge branch changes
```

The event at `124.05` changed only the post hoc classifier. It did not change the implemented edge formulas.

This retired the “exceptional branch switch” interpretation. The trajectory stayed on one fixed symbolic winner branch while its coefficients evolved toward a tie.

---

# XI. Exact finite-step factorization and fiber geometry

For a nonnegative proposal \(x\), with row sums \(q=Ax\), the safeguarded finite map factorizes as

\[
\boxed{
\mathcal A_\varepsilon(x)=M(Ax)x.
}
\]

All nonlinear dependence enters through node row sums; conditional on those row sums, the edge action is diagonal.

For \(x,y\ge0\) with \(Ax=Ay=q\),

\[
\mathcal A_\varepsilon(y)-\mathcal A_\varepsilon(x)
=
M(q)(y-x).
\]

Thus the map is exactly affine-linear on nonnegative row-sum fibers.

On strict winner strata, the Jacobian follows directly from the code. At ties, the ambient map is generally only directionally differentiable. On a fully constrained face-lineality direction \(Ah=0\), scales remain fixed exactly, so ambient tie nonsmoothness disappears on the fiber.

This factorization became the principal exact implementation theorem.

---

# XII. Frozen-driver cocycle — non-normal transient and severe anisotropy

With replayed \(R_n\) treated as exogenous,

\[
K_n^{(B)}
=
(1-\gamma dt)
D\mathcal A_\varepsilon(x_n).
\]

The K3 sequence was fixed-form but time varying.

The from-split propagator showed:

```text
full peak amplification        1.27097 at t=0.1
split-lineality peak           1.20563
long-horizon principal rate   -0.1233
```

A constant `K0` reproduced the initial transient almost exactly. A diagonal-scale-only control did not amplify.

Conclusion:

> The early weight-sector transient is already encoded in the initial non-normal branch Jacobian and requires the node-mediated low-rank correction; coefficient drift is not required for the peak.

Stable compound-cocycle analysis resolved a spectrum with one moderate and two extreme contraction rates. The most negative mode was controlled by the fixed `1e-12` safeguard and is a real feature of the implemented discrete map, though not an intended finite channel of an ideal `epsilon -> 0` limit.

Centered frozen-driver nonlinear trajectories matched the cocycle accurately while preserving the branch.

---

# XIII. Augmented tangent — the correct state space is larger than weights

The full discrete state is

\[
X_n=(\theta_n,B_n,C_n,\mathcal H_n).
\]

The augmented tangent differentiated:

- delayed phase differences;
- complex EMA memory;
- the magnitude map \(R=|C|\);
- adaptive forcing;
- positivity;
- safeguarded admissibility;
- projected phase coupling;
- phase update;
- history shift.

Both \(+h\) and \(-h\) directional tangents were propagated to handle endpoint ties.

The custom base step reproduced the implemented step exactly. Synthetic one-step and multistep tangent tests passed.

On the production replay, median errors were approximately:

```text
K3/full-B tangent ~5e-4
phase tangent      ~1.6e-6
R tangent          ~1.8e-4
```

This reduced the long-lived frozen/coupled discrepancy from order `4e-1` to order `1e-4`–`1e-3`.

Stage B established that phase/history/EMA feedback was necessary for the long-lived response, while the frozen weight cocycle remained the correct weight-to-weight block.

---

# XIV. Duhamel decomposition — homogeneous decay versus regenerated response

For the K3 weight tangent \(b_n\), define

\[
f_n=b_{n+1}-K_nb_n.
\]

Then

\[
h_{n+1}=K_nh_n,
\qquad
r_{n+1}=K_nr_n+f_n,
\]

\[
b_n=h_n+r_n.
\]

Reconstruction errors were near `1e-15`; residual forcing matched the directly differentiated \(R\to B\) contribution near `1e-13`.

Exact feedback crossover times were:

```text
direction 0: 0.38
direction 1: 72.86
```

The fast homogeneous direction disappeared almost immediately. The slow direction retained its original perturbation for roughly 73 time units before regenerated feedback dominated.

Final feedback was generated almost entirely by recent forcing. Early forcing contributions were tiny and anti-aligned with the final response; late forcing contributions were aligned.

Ablations showed:

- removing `R -> B` collapsed the late response;
- fresh phase forcing and EMA memory were both necessary;
- current-phase input selected the late sign/amplitude;
- delayed-history input modestly suppressed the late direction-1 response.

These were recursive tangent counterfactuals, not additive causal percentages.

---

# XV. Rank-one reduction and operational memory

Late total and regenerated K3 tangents became almost one-dimensional.

POD results:

```text
weighted first-mode fraction ~1
unit-vector first-mode fraction ~0.999999 late
```

Late transverse fractions were approximately:

```text
direction 0: 1.5e-3
direction 1: 1e-8 to 1e-6
```

Raw forcing was directionally broader (`unit E1 ~0.93`), while propagated forcing became almost perfectly rank one. Thus the weight cocycle acted as a rank-one directional filter.

Target-time recent-forcing reconstruction fits were transient before roughly `T=150` and stabilized after about `T=200`:

\[
\kappa\approx0.06913,
\qquad
\tau_{\rm eff}\approx14.46.
\]

At late targets:

```text
50% reconstruction error horizon ~10.02
10% horizon                       ~33.3
1% horizon                        ~66.6
```

The operational memory law was late-regime specific, not global.

---

# XVI. Scalar projection, spectral gap, and biorthogonal correction

The empirical late POD direction was

\[
v_{\rm POD}\approx(0.577341,-0.577369,-0.577341).
\]

The analytic K3 lineality direction is

\[
v=\frac1{\sqrt3}(1,-1,-1).
\]

Their angle was about `0.0013 degrees`.

Euclidean projection onto \(v\) or \(v_{\rm POD}\) gave accurate direction-1 rollouts but failed badly for direction 0 because the operator was strongly non-normal.

A numerical left mode repaired the rollout. It converged to

\[
u=\frac{\sqrt3}{2}(1,0,-1),
\qquad
u^Tv=1.
\]

Fixed left covectors from `t=200`, `250`, and `319.99` gave nearly identical results. From `t=250`, parameter-free final errors were roughly:

```text
direction 0: 1.9e-5
direction 1: 2.8e-5
```

The rank-one decision gate passed: the prior failure was a Euclidean-coordinate artifact rather than evidence that a second weight mode was required.

The late triangular reduction became

\[
a_{n+1}=\lambda_na_n+g_n,
\qquad
 g_{n+1}\approx\alpha_{\rm EMA}g_n,
\]

with

\[
a_n=u^Tb_n,
\qquad
g_n=u^Tf_n.
\]

Direct forcing-propagation analysis established, in the late regime,

\[
\kappa
\approx
r_{\rm prop}-r_g
\]

to approximately `1e-6` at the final target. The projected forcing envelope decayed at the EMA rate.

The quantity \(\lambda_B/\alpha_{\rm EMA}\) is a relative-retention factor, not an established closed-loop gain.

---

# XVII. Nested operator families and the analytic defect

The selected K3 block has exact sparsity

\[
K=
\begin{pmatrix}
p&0&q\\
r&s&0\\
t&0&u
\end{pmatrix}.
\]

Four nested families were audited:

\[
\mathcal K_{\rm sym}
\subset
\mathcal K_{LR}
\subset
\mathcal K_R
\subset
\mathcal K_{\rm sparse}.
\]

At `t=100`, distance to the right-invariant family was already about `5.6e-9`, while distances to the biorthogonal and symmetric families were order `1e-3`. Thus the right line was protected by much weaker conditions than full symmetry.

The dominant left-breaking mismatch was identified as

\[
\delta_n=\beta_{25,n}-\beta_{59,n},
\]

entering through

\[
E_*
=
\begin{pmatrix}
-1&0&-1\\
0&0&0\\
0&0&0
\end{pmatrix}.
\]

This matrix satisfies

\[
E_*v=0
\]

but breaks the analytic left relation.

Its projected shapes explain the exact residual constants

\[
\sqrt{\frac32},
\qquad
\frac3{\sqrt8}.
\]

Numerical defect POD directions matched the analytic projected defect shapes at cosine `1-O(1e-12)`, with direct reconstruction errors of only a few parts in `1e6`.

The scalar defect and family-defect matrices obeyed the EMA multiplier pointwise late:

```text
median multiplier error ~2e-9
matrix shape error       ~1e-9 to1e-8
no sign changes
```

This established a replay-specific operator relaxation mode, while causal control by EMA remained unproved.

---

# XVIII. Causal trace — a productive negative result

The implementation chain from resonance magnitude to operator defect closed exactly:

\[
\Delta R
\to
\Delta x
\to
\Delta B
\to
\delta.
\]

All identities reproduced at machine precision, and the downstream scalar quantities shared the EMA multiplier late.

However, the full directed complex differences and phase-source differences remained approximately persistent. Their norms did **not** decay at the EMA rate.

This rejected the simple story:

> The full complex EMA difference becomes source-free and decays homogeneously.

The source-to-memory norm ratio had been misleading because the source was multiplied by \(1-\alpha\). In fact, source and memory differences had comparable norms.

The unresolved mechanism was localized to the observation map

\[
C\mapsto |C|.
\]

The next exact identity is the squared-magnitude equation:

\[
M_{n+1}
=
\alpha^2M_n
+
(1-\alpha)^2
+
2\alpha(1-\alpha)\Re(\overline C_nz_n).
\]

For directed edge differences:

\[
\Delta M_{n+1}
=
\alpha^2\Delta M_n
+
2\alpha(1-\alpha)\Delta A_n.
\]

An effective \(\alpha\)-mode requires

\[
\Delta A_n\approx\frac12\Delta M_n.
\]

This became the immediate observable-level question.

---

# XIX. Major interpretations retired during the program

The following statements were useful hypotheses but are no longer supported in their original form:

1. **`B` is the unique or dominant memory carrier.**  
   Retired because `reset_B` reconstructs mature topology almost exactly.

2. **The projection is an occasional repair.**  
   Retired because capacity correction is active on essentially every mature update and is comparable to the incremental proposal.

3. **The mature full system is at equilibrium.**  
   Retired; only the adaptive weight component is constraint-balanced.

4. **The exceptional seed undergoes an implemented active-face switch at `t=124.05`.**  
   Retired; this was a tolerance-classifier transition. The actual winner branch remains fixed.

5. **The split K3 has an operational bare-`gamma` edge mode at `dt=0.01`.**  
   Retired; node 2 is proposal-violating and controls the edge from the first step.

6. **A Euclidean scalar coordinate should describe both K3 directions.**  
   Retired; a biorthogonal left coordinate is required by non-normality.

7. **The POD Rayleigh rate gives the exact memory gap.**  
   Retired; the correct rate is the decay of the actual propagated forcing channel.

8. **The full complex EMA difference decays homogeneously at the EMA rate.**  
   Retired; the magnitude observable decays while complex differences persist.

9. **A two-state model in `(a,g)` has been identified.**  
   Retired; late collinearity makes unconstrained coefficients unidentifiable. The parameter-free triangular relation is the supported reduction.

10. **A pointed torus is a likely literal geometry.**  
    Not supported. Any full-state geometric study must first quotient phase symmetry and distinguish attractor tangents from stable fibers.

---

# XX. Current mathematical picture

For the audited exceptional replay, the strongest current synthesis is:

1. The finite-step map follows a fixed K3 winner branch.
2. Its selected Jacobian lies exactly in a sparse family.
3. A broad right-invariant structure is reached very early.
4. A dominant explicit defect preserves the right line but breaks the left mode.
5. The defect amplitude and projected family defects follow the EMA multiplier late.
6. A stable analytic biorthogonal pair gives a parameter-free scalar weight recurrence.
7. The augmented phase/history/EMA state continually regenerates the weight perturbation.
8. The weight cocycle filters forcing into a nearly fixed one-dimensional late channel.
9. The final response depends mainly on recent forcing over roughly `60–70` time units.
10. The remaining unresolved mechanism is how persistent complex EMA dynamics produce an EMA-rate magnitude difference through the nonlinear observation map.

This picture is conditional on:

- one frozen seed;
- one fixed winner branch;
- two tested initial directions;
- the implemented `dt=0.01` and `epsilon=1e-12` map;
- finite replay time.

It is not yet a universal AIEF theorem.

---

# XXI. Immediate research frontier

## 1. Squared-magnitude/radial observable audit

For directed edges 25 and 59, test exactly:

\[
\Delta M_{n+1}
=
\alpha^2\Delta M_n
+
2\alpha(1-\alpha)\Delta A_n,
\]

and whether

\[
2\Delta A_n\approx\Delta M_n.
\]

Separate forward and reverse directions before symmetrization. Quantify radial/tangential components and midpoint conditioning.

## 2. Observable subsystem

Combine the exact weight-difference equation

\[
\Delta B_{n+1}
=
s_{7,n}\big[(1-\gamma dt)\Delta B_n
+dt(\eta+\mu)\Delta R_n\big]
\]

with the measured/derived evolution of \(\Delta R\). Determine whether the late system is triangular or genuinely coupled.

## 3. Formal theorem package

Write proofs for:

- factorization and fiber linearity;
- fixed-winner sparse Jacobian;
- nested invariant families;
- analytic left/right pair;
- defect matrix and projection constants;
- conditional scalar and memory lemmas;
- augmented directional derivative away from gate and zero-magnitude singularities.

## 4. Existing-component generality

Use existing `K4`, `K5`, and `K6` states to test invariant **subspaces**, not universal rank-one behavior.

## 5. Regenerated sensitivity studies

Only after the observable mechanism is resolved, regenerate complete trajectories for targeted changes in:

- `T_window`;
- timestep;
- safeguard scaling.

Never reuse a saved split state under inconsistent dynamics parameters.

---

# XXII. Principal files and artifacts

## Production and closure

```text
AIEF_1_3_falsification_updated.py
AIEF_1_3_paired_statistics_updated.py
AIEF_1_3_closure_diagnostics_updated.py
AIEF_1_4_memory_ablation_updated.py
```

## Geometry and active boundary

```text
AIEF_1_4_entropy_geometry_diagnostics.py
AIEF_1_4_local_update_comparison.py
AIEF_1_4_active_boundary_analysis.py
AIEF_1_4_stationarity_perturbation_analysis_updated.py
```

## Tangent spectra and components

```text
AIEF_1_4_exceptional_tangent_analysis.py
AIEF_1_4_face_spectrum_analysis.py
AIEF_1_4_channel_invariance_analysis.py
AIEF_1_4_intertwining_controller_analysis.py
AIEF_1_4_component_controller_audit.py
AIEF_1_4_exceptional_K3_transition_audit.py
```

## Actual branch and cocycles

```text
AIEF_1_4_actual_admissibility_branch_audit.py
AIEF_1_4_frozen_driver_cocycle_analysis.py
AIEF_1_4_cocycle_controls_coupled_comparison.py
AIEF_1_4_augmented_tangent_cocycle_analysis.py
```

## Duhamel, memory, and reduction

```text
AIEF_1_4_augmented_duhamel_feedback_analysis.py
AIEF_1_4_duhamel_memory_alignment_analysis.py
AIEF_1_4_feedback_rank_memory_reduction.py
AIEF_1_4_scalar_spectral_gap_reduction.py
AIEF_1_4_propagation_gap_geometric_control.py
AIEF_1_4_parameter_free_triangular_closure.py
AIEF_1_4_biorthogonal_triangular_closure.py
```

## Operator-family and defect program

```text
AIEF_1_4_nested_operator_family_audit.py
AIEF_1_4_defect_recurrence_analytic_mode.py
AIEF_1_4_defect_causal_ema_trace.py
```

## Administrative sources of truth

```text
AI_AGENT_HANDOFF_PROMPT.md
AIEF_1_4_OPERATOR_COCYCLE_THOUGHT_TREE.md
AIEF_1_4_FORWARD_PLAN.md
AIEF_HISTORIC_UNFOLDING.md
```

---

# Final perspective

The AIEF program began by asking whether adaptive phase compatibility creates sparse persistent topology. It then passed through reproducibility repair, falsification, memory ablation, boundary geometry, tangent spectra, and active-face analysis.

Its current center is different:

> A piecewise-rational finite-step admissibility map creates a fixed-branch, non-normal weight operator whose geometry can be factored, differentiated, decomposed, and reduced. In one exceptional replay, the resulting augmented tangent dynamics collapse onto an analytically identifiable biorthogonal mode, while persistent complex EMA dynamics are filtered through a nonlinear magnitude observable into an EMA-rate operator defect.

The next advance will come not from adding another broad simulation matrix, but from deriving the observable-level mechanism and formalizing the operator hierarchy already exposed by the saved data.

---

# Postscript — closure of the exceptional replay mechanism

After the first historic-unfolding freeze, the exceptional-seed program advanced through several final layers:

1. **Radial observable audit** — both directed squared-magnitude channels independently acquired the EMA multiplier; forward/reverse symmetrization reinforced rather than created the mode.
2. **Phase-source locking audit** — source-memory tracking, tangentialization, mean alignment, and cancellation of alignment components were separated by exact identities.
3. **Resonant tracking audit** — the complex tracking error followed a polynomial-times-exponential law consistent with a size-two Jordan reduction, while the source difference converged to a nonzero complex limit.
4. **Delayed phase-balance audit** — source mean and separation increments acquired the EMA envelope through increasingly precise cancellation among intrinsic-frequency, projected-coupling, and delayed-history terms.
5. **Biorthogonal and nested-family closure** — the analytic right/left pair and explicit defect matrix were connected directly to the fixed-winner Jacobian and its family distances.
6. **Lineage freeze** — the complete analysis chain and superseded claims were frozen into machine-readable registries.

The final replay-specific mechanism is therefore organized as:

```text
delayed phase-balance cancellation
-> source difference approaches a fixed nonzero complex limit
-> resonant EMA tracking
-> persistent tangential complex separation
-> contracting radial magnitude observable
-> resonance and weight difference
-> explicit K3 Jacobian defect
```

The central uncertainty is no longer the exceptional replay mechanism itself. It is the proof and generality of that mechanism across branches, components, regenerated timesteps, safeguards, and parameters.

Additional principal scripts:

```text
AIEF_1_4_radial_observable_subsystem_analysis.py
AIEF_1_4_phase_source_locking_analysis.py
AIEF_1_4_resonant_tracking_angular_analysis.py
AIEF_1_4_phase_balance_source_dynamics.py
AIEF_1_4_parameter_free_triangular_closure.py
AIEF_1_4_biorthogonal_triangular_closure.py
AIEF_1_4_nested_operator_family_audit.py
AIEF_1_4_defect_recurrence_analytic_mode.py
AIEF_1_4_freeze_analysis_lineage.py
```
