# AIEF-1.4 operator/cocycle thought tree

## Purpose

This document records the current mechanistic and mathematical interpretation of the frozen AIEF-1.4 exceptional seed after the component, actual-branch, frozen-cocycle, augmented-tangent, Duhamel, memory, and rank-reduction analyses.

Always distinguish:

1. exact consequences of the implemented code;
2. facts established numerically on the frozen replay;
3. strongly supported mechanisms;
4. open theorems/generalizations.

The inferential unit remains one seed/graph realization. Direction and amplitude probes are conditional diagnostics, not independent seed replicates.

---

## 1. Exact implemented admissibility structure

For a nonnegative proposal edge vector `x`, let

\[
q=Ax.
\]

The safeguarded admissibility stage factorizes as

\[
\mathcal A_\varepsilon(x)=M(Ax)x,
\]

where `M(q)` is diagonal and its edge multiplier is

\[
m_{ij}(q)=\min(s_i(q),s_j(q)).
\]

When the global gate is on,

\[
s_i(q)=\min\left(1,\frac{c_i}{q_i+\varepsilon}\right),
\qquad \varepsilon=10^{-12}.
\]

On a strict winner stratum, if node `k(e)` wins edge `e`,

\[
D\mathcal A_\varepsilon(x)_{ef}
=
s_{k(e)}\delta_{ef}
-
\frac{x_e s_{k(e)}}{q_{k(e)}+\varepsilon}A_{k(e)f}.
\]

The proposal space is polyhedrally stratified by positivity, gate, clipping, and winner inequalities; the map is smooth rational on each strict open stratum.

On a nonnegative row-sum fiber `Ax=q`, the map is exactly affine-linear:

\[
\mathcal A_\varepsilon(y)-\mathcal A_\varepsilon(x)
=
M(q)(y-x),
\qquad Ax=Ay=q.
\]

At winner ties the ambient classical Fréchet derivative generally fails, but directional derivatives exist. On fully constrained face-lineality directions `Ah=0`, scales remain exactly fixed, so the ambient tie nonsmoothness disappears on the fiber.

---

## 2. Ordinary mature component mechanism

The component audit directly found complete support components in the frozen cohort.

For 39/40 ordinary split states:

- every positive-support node is saturated;
- support components are rate-uniform;
- locked-edge, edge-balance, and degree-rate checks pass;
- explicit component intertwiners reproduce the tangent operator;
- component spectra reproduce the full tangent spectra.

Observed support components include `K2`, `K3`, `K4`, `K5`, and `K6`.

For a fully saturated locked connected component with uniform capacity `c`, edge stationarity and controller balance imply:

\[
\alpha_i=\alpha_j \quad\text{on connected support},
\]

\[
w=\frac{c}{k},
\qquad
r=\gamma+\alpha=\frac{k\eta}{c}.
\]

With

\[
\frac{\eta}{c}=\frac6{95},
\]

the observed channels are degree-generated:

\[
k=2,3,4,5
\quad\Longrightarrow\quad
r=\frac{12,18,24,30}{95}.
\]

For complete `K_s`, the signless-incidence face-lineality nullity is

\[
q_s=\binom{s}{2}-s=\frac{s(s-3)}2.
\]

Thus `K2` and fully saturated `K3` are spectrally silent, while `K4`, `K5`, `K6` contribute multiplicities `2`, `5`, `9`.

---

## 3. Exceptional K3 topology and classifier history

Exceptional seed:

```text
4619122171158768524
```

The fixed positive-support triangle is

```text
nodes: [2, 7, 11]
edges: [25=(2,7), 29=(2,11), 59=(7,11)]
```

The tolerance classifier at `1e-9` changes at step `12405`, but this is not an executed winner-branch switch.

Proposal violation begins at:

```text
node 2: step 0
node 7: step 0
node 11: step 11381
```

The actual K3 winner map is constant throughout the 32,001-state replay:

\[
(2,7)\mapsto7,
\qquad
(2,11)\mapsto2,
\qquad
(7,11)\mapsto7.
\]

Node 11 becomes scale-clipped but never wins a positive K3 edge. The `1e-9` classifier event changes no executed edge formula.

Therefore the exceptional implemented map is not a switched K3 system over the replay. It follows one fixed symbolic winner branch with continuously changing coefficients and approaches a late tie stratum.

---

## 4. Frozen-driver weight cocycle

With the replayed `R_n` treated as exogenous,

\[
K_n^{(B)}=(1-\gamma dt)D\mathcal A_\varepsilon(x_n).
\]

The matrix sequence is fixed-form but non-autonomous.

Established numerically:

- exact base replay;
- winner-signature changes: `0`;
- strong branchwise-Jacobian/nonlinear frozen agreement;
- all tested centered perturbations preserve the branch;
- maximum tested branch ratio `chi < 0.161`.

Finite-time controls:

```text
actual peak amplification:       1.27097 at t=0.1
K0-constant peak:                1.27095 at t=0.1
late-K constant peak:            1.20899 at t=0.1
diagonal-scale-only peak:        1 at t=0
```

The early transient is already encoded in the initial non-normal branch Jacobian. Coefficient drift is unnecessary for that peak. Removing the node-mediated low-rank term removes amplification and severe anisotropy.

Stable compound-cocycle exponents for the actual frozen sequence are approximately:

\[
(-0.1233,-66.8,-2717.7).
\]

The third mode is dominated by the implemented safeguard scale:

\[
e^{-2717.7dt}\approx\varepsilon/c.
\]

It remains a real mode of the implemented discrete algorithm, but it is not an intended finite channel of an `epsilon -> 0` continuum model.

---

## 5. Augmented directional tangent

The validated augmented tangent state is

\[
X_n=(\theta_n,B_n,C_n,\mathcal H_n).
\]

The tangent includes:

- current phase and delayed-history derivatives in `dphi`;
- complex EMA memory and fresh phase forcing;
- `R=|C|` differentiation and symmetrization;
- `dF=(eta+mu)dR-gamma dB`;
- positivity and safeguarded admissibility directional derivatives;
- projected phase coupling;
- exact history shift.

Both `+h` and `-h` directional tangents are propagated; centered predictions use their odd part.

Production results:

```text
final base replay error:                 0
custom-step vs implemented-step error:   0
overall median K3 augmented error:       ~5e-4
overall median phase error:              ~1.6e-6
overall median R error:                  ~1.8e-4
maximum nonadditive tie interaction:     ~3e-16
```

The augmented tangent reduces the previous slow-direction frozen/coupled error from order `4e-1` to order `1e-4`--`1e-3` while all tested nonlinear branches remain preserved.

This establishes the augmented tangent numerically for this seed, branch, two directions, amplitudes, and resolved finite horizons. It is not yet a universal full-map differentiability theorem.

---

## 6. Exact direction-wise Duhamel decomposition

Partition the validated tangent into K3 weight component `b_n` and remaining augmented variables. Define

\[
f_n=b_{n+1}-K_nb_n.
\]

Then

\[
h_{n+1}=K_nh_n,
\qquad h_0=b_0,
\]

\[
r_{n+1}=K_nr_n+f_n,
\qquad r_0=0,
\]

and

\[
b_n=h_n+r_n.
\]

Production reconstruction errors are approximately `1e-15`. Residual forcing matches the directly differentiated projected `dR` pathway at approximately `1e-13`.

The forcing is endogenous to the closed augmented system; it is called forcing only in the weight-block representation.

Exact crossover times:

```text
direction 0: t*=0.38
direction 1: t*=72.86
```

where `||r_n|| >= ||h_n||`.

Median instantaneous forcing/weight-output ratios are only order `1e-3`, but forcing is repeatedly regenerated and directionally selective.

Median immediate alignment with the principal one-step output singular direction:

```text
direction 0: ~0.772
direction 1: ~0.988
```

---

## 7. Duhamel temporal organization and feedback pathways

At the final horizon, forcing contributions from early bins are tiny and anti-aligned with the final feedback; late-bin contributions are aligned.

Almost all final feedback comes from the last `60--70` time units. This is continual recent regeneration plus forgetting, not accumulation over the entire 320-unit history.

Counterfactual tangent ablations for the long-lived direction show:

- removing `R -> B` feedback collapses the late response;
- removing fresh phase forcing has the same late effect because `dC_0=0`;
- removing EMA memory also collapses the late response;
- removing the current-phase term leaves a small late response with opposite sign;
- removing delayed-history input leaves the same sign but a late norm about `11%` larger.

These are recursive counterfactuals, not additive causal fractions.

---

## 8. Rank-one late reduction

The reduction analysis directly measures a nearly fixed late line.

Late POD results for total and feedback tangents:

```text
weighted first-mode fraction: ~1
unit-vector first-mode fraction: ~0.999999
```

Late scalar transverse fractions:

```text
direction 0 median: ~1.48e-3
direction 1 median: ~1.02e-8
```

The leading direction rotates negligibly in the late regime.

Raw instantaneous forcing has late unit-vector first-mode fraction about `0.93`, so raw forcing is directionally broader. After propagation, forcing contributions have unit first-mode fractions above `0.99996` for direction 0 and essentially `1` for direction 1.

Therefore the low-dimensional response is produced by anisotropic filtering through the weight cocycle, not by perfectly collinear raw forcing.

---

## 9. Late operational memory law

Target-time reconstruction fits are transient before about `T=150` and stabilize late.

For `T >= 200`, both directions converge toward

\[
\kappa\approx0.06913,
\qquad
\tau_{\mathrm{eff}}\approx14.46.
\]

At targets `250--320`, fits have `R^2` approximately `1`, with horizons:

```text
50% error: ~10.02
10% error: ~33.3
1% error:  ~66.6
```

The claim is that the late operational reconstruction-error envelope is exponential. The full raw curve has local nonmonotonicity from vector cancellation.

Base EMA rate:

\[
1/T_{\mathrm{window}}\approx0.0571333.
\]

A striking numerical closure is

\[
0.126255-0.0571333\approx0.0691217,
\]

matching the observed late memory rate to about `1e-6`.

This motivates, but does not prove, the spectral-gap hypothesis

\[
\kappa\stackrel{?}{=}r_{\mathrm{weight}}-r_{\mathrm{aug/forcing}}.
\]

---

## 10. Immediate next task: direct scalar recurrence test

Remain within the saved arrays. Let `v` be the measured late POD direction and define

\[
a_n=v^Tb_n,
\qquad
g_n=v^Tf_n,
\qquad
\lambda_n=v^TK_nv.
\]

Test

\[
a_{n+1}=\lambda_na_n+g_n+\epsilon_n,
\qquad
\epsilon_n=v^TK_ne_n,
\]

with

\[
e_n=b_n-a_nv.
\]

Required diagnostics:

1. line-invariance defect
   \[
   \|(I-vv^T)K_nv\|;
   \]
2. scalar recurrence residual;
3. late projected weight rate
   \[
   -\log|\lambda_n|/dt;
   \]
4. projected forcing envelope rate from `|g_n|`;
5. target-wise comparison
   \[
   \kappa_T\stackrel{?}{\approx}r_{B,T}-r_{g,T};
   \]
6. fit and out-of-sample test of a closed two-state recurrence, for example
   \[
   g_{n+1}=\rho g_n+\chi a_n.
   \]

Only after this direct test should a consistently regenerated `T_window` sensitivity study be considered.

---

## 11. Confidence levels

### Exact implementation mathematics

- admissibility factorization;
- branchwise Jacobian on strict strata;
- exact fiber linearity;
- directional tie formula;
- augmented tangent update equations;
- direction-wise Duhamel identity once block linearity/additivity holds.

### Established numerically on this replay/tested subspace

- fixed K3 winner branch;
- frozen cocycle validation;
- early non-normal transient and low-rank mechanism;
- augmented tangent validation;
- exact Duhamel reconstruction and direct-driver match;
- exact crossover times;
- late rank-one reduction;
- stable late operational memory-envelope rate.

### Strongly supported mechanisms

- anisotropic weight propagation filters feedback into a fixed slow line;
- delayed phase/EMA feedback continually regenerates the late weight perturbation;
- EMA memory, fresh phase forcing, and `R -> B` transfer are necessary for the tested late response;
- the memory rate is a spectral gap between frozen weight contraction and EMA-dominated augmented decay.

### Open

- direct pointwise scalar recurrence verification;
- closed two-state reduction;
- formal augmented Hadamard differentiability theorem;
- joint `dt`, slack, and safeguard limit;
- generality beyond this seed, branch, and two directions;
- consistent parameter sensitivity after full state regeneration.
