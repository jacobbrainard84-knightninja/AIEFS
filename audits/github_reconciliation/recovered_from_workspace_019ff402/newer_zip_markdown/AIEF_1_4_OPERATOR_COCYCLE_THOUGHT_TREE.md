# AIEF-1.4 operator/cocycle thought tree

## Purpose

This document records the current mechanistic and mathematical interpretation of the frozen AIEF-1.4 exceptional seed after the component, actual-branch, frozen-cocycle, augmented-tangent, Duhamel, biorthogonal, nested-operator, radial-observable, resonant-tracking, and delayed phase-balance analyses.

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

## 10. Scalar, geometric, and biorthogonal reduction

The direct scalar recurrence test was completed. A Euclidean POD coordinate described the long-lived direction but failed for the cancellation-sensitive direction 0. The analytic K3 right direction is

\[
v=\frac1{\sqrt3}(1,-1,-1).
\]

The late numerical left modes converge to

\[
u=\frac{\sqrt3}{2}(1,0,-1),
\qquad u^Tv=1.
\]

Using the biorthogonal amplitude

\[
a_n=u^Tb_n
\]

reduces direction-0 late rollout error from order `0.74` to order `1e-5`. Fixed left covectors from `t=200`, `250`, `319.99`, and the late average perform essentially identically; a time-dependent adjoint bundle gives no material improvement.

The late parameter-free triangular reduction is

\[
a_{n+1}=\lambda_na_n+g_n,
\qquad
g_{n+1}\approx\alpha_{\rm EMA}g_n,
\]

where

\[
g_n=u^Tf_n.
\]

Direct forcing propagation, not the POD Rayleigh quotient, supplies the relevant weight-channel rate. The late operational memory relation

\[
\kappa\approx r_{\rm prop}-r_g
\]

closes to approximately `1e-6` at the final target.

---

## 11. Nested K3 operator families and analytic defect

The fixed winner branch gives the exact sparse selected block

\[
K=c_0
\begin{pmatrix}
s_7-\beta_{25}&0&-\beta_{25}\\
-\beta_{29}&s_2-\beta_{29}&0\\
-\beta_{59}&0&s_7-\beta_{59}
\end{pmatrix}.
\]

The nested families are

\[
\mathcal K_{\rm sym}
\subset
\mathcal K_{LR}
\subset
\mathcal K_R
\subset
\mathcal K_{\rm sparse}.
\]

Right invariance requires

\[
s_2=s_7.
\]

Given right invariance, analytic left invariance requires

\[
\beta_{25}=\beta_{59}.
\]

The dominant left-breaking mismatch

\[
\delta_n=\beta_{25,n}-\beta_{59,n}
\]

enters through

\[
E_*=
\begin{pmatrix}
-1&0&-1\\
0&0&0\\
0&0&0
\end{pmatrix},
\qquad E_*v=0.
\]

Projected analytic defects match numerical defect POD directions at cosine `1-O(1e-12)`. Direct reconstruction errors are only a few parts in `1e6`. The defect amplitude and family-defect matrices obey the EMA multiplier pointwise late with errors of order `1e-9`; defect shape changes are order `1e-9`--`1e-8`.

The right-invariant family is reached far earlier than the biorthogonal/symmetric families. The right line is structurally protected before the dual geometry and full coefficient symmetry emerge.

---

## 12. Radial observable and persistent complex state

The downstream identities

\[
\Delta R\to\Delta x\to\Delta B\to\delta\to K
\]

close at machine precision. However, the full directed complex EMA differences do not decay at the EMA rate. Their norms and the phase-source-difference norms remain approximately persistent.

For a directed EMA state,

\[
M_n=|C_n|^2,
\qquad
Q_n=\Re(\overline{C_n}z_n),
\]

and

\[
M_{n+1}
=\alpha^2M_n+(1-\alpha)^2+2\alpha(1-\alpha)Q_n.
\]

Directed edge differences satisfy

\[
\Delta M_{n+1}
=\alpha^2\Delta M_n+2\alpha(1-\alpha)\Delta Q_n.
\]

Both forward and reverse directed magnitude channels independently acquire the EMA multiplier; they reinforce under symmetrization. The observed alignment law

\[
2\Delta Q\approx\Delta M
\]

explains the effective alpha mode.

The persistent complex difference becomes almost entirely tangential to the complex midpoint, while its radius difference decays at the EMA rate. Thus the operator defect is a contracting radial observable of a persistent complex state, not decay of the full complex difference.

---

## 13. Source-memory locking, cancellation, and resonant tracking

Define

\[
E_n=\Delta z_n-\Delta C_n,
\qquad
S_n=\Delta z_{n+1}-\Delta z_n.
\]

The exact tracking recurrence is

\[
E_{n+1}=\alpha E_n+S_n.
\]

Late replay data support

\[
S_n\sim B\alpha^{n+1},
\qquad
E_n\sim(A+Bn)\alpha^n.
\]

The pair is therefore described asymptotically by a size-two Jordan block with repeated multiplier \(\alpha\). Complex fits of \(E_n/\alpha^n\) are affine with late `R^2` effectively one, while \(S_n/\alpha^{n+1}\) independently converges to the affine slope. Source-limit estimates collapse to relative spreads near `1e-13`.

For midpoint variables

\[
\bar C=(C_a+C_b)/2,
\qquad
\bar z=(z_a+z_b)/2,
\]

and differences \(\Delta C,\Delta z\), the exact alignment decomposition is

\[
2\Delta Q-\Delta M
=
T_1+T_2,
\]

\[
T_1=2\Re[\overline{\bar C}(\Delta z-\Delta C)],
\qquad
T_2=2\Re(\overline{\Delta C}\bar z).
\]

The replay gives

\[
T_1/T_2\to-1.
\]

The small alignment residual is produced by cancellation of comparable tracking and tangential/mean-alignment terms. Forward/reverse magnitude channels themselves do not cancel.

---

## 14. Delayed phase-balance source dynamics

For directed edge \((i,j)\),

\[
\phi_{ij,n}
=\theta_{i,n}-h_{j,n}
-\frac{\omega_i+\omega_j}{2}\tau,
\qquad
z_{ij,n}=e^{i\phi_{ij,n}}.
\]

The exact increment is

\[
\Delta\phi_{ij,n}
=dt(\omega_i+G_{i,n})-\Delta h_{j,n}.
\]

For both forward and reverse K3 comparisons, source mean, source separation, and full complex-source increments converge to the EMA-rate envelope. Their small net values arise from increasingly precise cancellation of intrinsic-frequency, projected-coupling, and delayed-history terms.

The mean and separation phases converge to fixed late limits; memory and source angular separations lock, while radius differences decay at the EMA rate.

The remaining upstream theorem problem is to derive this delayed phase-balance convergence from the coupled nonlinear equations rather than treat it as replay input.

---

## 15. Corrected Jordan-resonant hierarchy

For

\[
S_n=B\alpha^{n+1}+r_n,
\qquad
E_{n+1}=\alpha E_n+S_n,
\]

variation of constants gives

\[
E_n=(E_0+Bn)\alpha^n
+\sum_{k=0}^{n-1}\alpha^{n-1-k}r_k.
\]

Let

\[
\rho_k=r_k/\alpha^{k+1}.
\]

- If \(\sum\rho_k\) converges, then
  \[
  E_n=(A+Bn)\alpha^n+o(\alpha^n).
  \]
- If \(\rho_n\to0\), then
  \[
  E_n=(E_0+Bn+o(n))\alpha^n,
  \]
  and the source-limit estimator tail is \(o(|\alpha|^n)\).
- If only \(\rho_n=O(1)\), then the tracking correction is \(O(n\alpha^n)\), while the source estimator remains consistent with error \(O(|\alpha|^n)\).

The replay provides finite-horizon evidence for \(\rho_n\to0\), not proof of infinite-horizon summability.

---

## 16. Current replay-specific causal chain

\[
\boxed{
\begin{aligned}
&\text{delayed phase-balance cancellation}\\
&\Downarrow\\
&\Delta z_n=\Delta z_\infty+O(\alpha^n)\\
&\Downarrow\\
&E_n=(A+Bn)\alpha^n\\
&\Downarrow\\
&\text{persistent tangential complex separation}\\
&\Downarrow\\
&T_1\approx-T_2\\
&\Downarrow\\
&\Delta M_{n+1}\approx\alpha\Delta M_n\\
&\Downarrow\\
&\Delta R\to\Delta B\to\Delta x\to\delta\to K.
\end{aligned}}
\]

This chain is established numerically on one replay and fixed winner branch. Its universal extension is open.

---

## 17. Confidence levels

### Exact implementation mathematics

- admissibility factorization and row-sum fiber linearity;
- strict-branch Jacobian and endpoint-tie directional formula;
- fixed-winner K3 sparse block;
- nested family characterizations;
- analytic left/right pair and explicit defect matrices;
- phase increment, EMA tracking, squared-magnitude, magnitude reconstruction, and alignment identities;
- Duhamel and exact Jordan-resonant algebraic lemmas.

### Established numerically on this replay/tested subspace

- fixed K3 winner branch;
- frozen and augmented tangent validation;
- exact Duhamel reconstruction;
- biorthogonal parameter-free scalar rollout;
- nested-family hierarchy and rank-one analytic defect;
- pointwise EMA defect recurrence;
- directed radial alpha modes;
- source-memory locking and alignment cancellation;
- resonant complex tracking;
- angular/radius freezing;
- delayed phase-balance cancellation.

### Strong replay-specific mechanisms

- anisotropic propagation filters forcing into a biorthogonal slow channel;
- the dominant defect preserves the right line and breaks the left relation;
- persistent complex source/memory separation is filtered into a contracting radial observable;
- the radial observable transfers its EMA multiplier into weights and the operator defect.

### Open

- formal augmented Hadamard directional-differentiability theorem;
- derivation of delayed phase-balance convergence from the nonlinear coupled equations;
- invariant-subspace generality for existing K4/K5/K6 components;
- matched-phase memory-ablation correction;
- joint timestep/slack/safeguard limit;
- consistently regenerated parameter sensitivity;
- generality beyond this seed, branch, and two directions.

---

## 18. Immediate program

1. Formalize the proof-oriented operator/observable manuscript.
2. Freeze the full analysis lineage and superseded-claim register.
3. Test geometric/dual invariant subspaces on existing K4/K5/K6 components.
4. Complete the matched-phase memory-ablation correction.
5. Only afterward run separately versioned, fully regenerated EMA and timestep/safeguard studies.
6. Defer broad cohorts and full-attractor topology.
