# AIEF-1.4 operator/cocycle closure and theorem note

## Exact identities, replay-established asymptotics, and conditional reductions

**Status:** working mathematical consolidation  
**Scope:** frozen AIEF-1.4 run `5a9f093a2fe0`, with detailed mechanism analysis on exceptional seed `4619122171158768524`  
**Updated:** 2026-07-26

---

## 1. Purpose and epistemic structure

The AIEF-1.4 analysis has reached a point where further local diagnostics are less valuable than formal consolidation. This note separates the results into three layers:

1. **Exact implementation identities** — algebraic consequences of the finite-step code.
2. **Replay-established asymptotic laws** — numerical results on one frozen branch and tested perturbation subspace.
3. **Conditional mathematical lemmas** — exact conclusions under explicitly stated asymptotic assumptions.

Nothing in this note promotes one replay into a universal theorem about all AIEF trajectories. The seed/graph realization remains the inferential unit.

---

# Part I. State, proposal, and admissibility map

## 2. Edge coordinates and capacity geometry

Let

\[
w\in\mathbb R^m,
\qquad m=\binom N2,
\]

be the unique undirected edge vector, and let

\[
A\in\{0,1\}^{N\times m}
\]

be the unsigned node-edge incidence matrix. The feasible set is

\[
\mathcal C
=
\{w\ge0:Aw\le c\}.
\]

The current production model has equal capacities

\[
c_i=c=\frac{a-\delta}{q}.
\]

For one Euler step, let

\[
z=w+dtF
\]

be the raw edge proposal and

\[
x=z_+
\]

the post-positivity proposal.

Let

\[
q=Ax
\]

be its proposal row sums.

---

## 3. Implemented safeguarded admissibility map

The production code uses a global gate. If no row violates capacity, scaling is skipped. If at least one row violates, node scales are

\[
s_i(q)
=
\min\left(1,\frac{c_i}{q_i+\varepsilon}\right),
\qquad
\varepsilon=10^{-12},
\]

and edge \(e=(i,j)\) receives multiplier

\[
m_e(q)=\min(s_i(q),s_j(q)).
\]

Define

\[
M(q)=\operatorname{diag}(m_e(q)).
\]

### Proposition 3.1 — exact factorization

On the nonnegative proposal domain,

\[
\boxed{
\mathcal A_\varepsilon(x)=M(Ax)x.
}
\]

This follows directly from `minimum.outer(scale, scale)`.

### Corollary 3.2 — exact fiber linearity

If \(x,y\ge0\) and

\[
Ax=Ay=q,
\]

then

\[
\boxed{
\mathcal A_\varepsilon(y)-\mathcal A_\varepsilon(x)
=
M(q)(y-x).
}
\]

Thus the map is exactly affine-linear on each nonnegative row-sum fiber.

This statement does not require the support of \(x\) and \(y\) to be identical, only nonnegativity and equal row sums.

---

## 4. Proposal-space strata and branch Jacobian

The post-positivity proposal space is stratified by:

- global gate state;
- node clipping inequalities;
- endpoint scale comparisons;
- positivity/support boundaries inherited from the preceding map.

For two clipped nodes,

\[
s_i<s_j
\iff
c_i(q_j+\varepsilon)<c_j(q_i+\varepsilon),
\]

an affine inequality in \(x\). Hence strict branch regions are relatively open polyhedral cells in proposal space. On each strict cell the map is smooth rational.

For edge \(e\) with unique winning endpoint \(k(e)\),

\[
y_e=x_es_{k(e)}.
\]

Since

\[
\frac{\partial s_k}{\partial x_f}
=
-\frac{s_k}{q_k+\varepsilon}A_{kf},
\]

we obtain:

### Proposition 4.1 — strict-branch Jacobian

\[
\boxed{
D\mathcal A_\varepsilon(x)_{ef}
=
s_{k(e)}\delta_{ef}
-
\frac{x_es_{k(e)}}{q_{k(e)}+\varepsilon}A_{k(e)f}.
}
\]

At endpoint ties, the classical Fréchet derivative generally fails. The directional derivative uses the minimum of the endpoint scale derivatives.

### Caveat 4.2 — safeguarded global-gate discontinuity

Because scaling is skipped below the global gate but uses \(q+\varepsilon\) immediately above it, the fixed-\(\varepsilon\) production map has a tiny jump of order \(\varepsilon/c\) at gate onset. Ideal-map directional theorems should concern either \(\varepsilon=0\) or an explicitly specified joint limit.

### Proposition 4.3 — clipped rows are interior in the projected output

For \(y=\mathcal A_\varepsilon(x)\), if row \(i\) is clipped while constructing \(y\), then

\[
\boxed{
(Ay)_i
\le
\frac{c_iq_i}{q_i+\varepsilon}
<c_i.
}
\]

Equality in the first inequality holds only when row \(i\) wins or ties every incident positive-proposal edge. This concerns the output \(y\), not necessarily the input weight state.

### Multiplier-controller fiber

Let \(S_x=\{e:x_e>0\}\). For a strict winner edge include its winner row; for an active endpoint tie include both rows; for a strictly unscaled identity edge include neither. Let \(J\) be the union of these multiplier-determining rows and define

\[
L_J=\{h:h_{S_x^c}=0,\ A_{J,S_x}h_{S_x}=0\}.
\]

If positive support and the global gate persist, strict winner-loser inequalities persist, and identity edges remain strictly unscaled, then for sufficiently small \(t\)

\[
\boxed{
\mathcal A_\varepsilon(x+th)
=
\mathcal A_\varepsilon(x)+tM(Ax)h,
\qquad h\in L_J.
}
\]

This finite fiber-affine identity includes active endpoint ties. A strict losing endpoint may change its own clipping label without changing the selected multiplier. With frozen resonance driver,

\[
h\in L_J
\Longrightarrow
Kh=(1-\gamma dt)M(Ax)h.
\]

The right-hand side need not lie in \(L_J\) unless the multiplier preserves that fiber.

### Proposition 4.4 — preservation and intertwining

For \(L=\ker C\),

\[
DL\subseteq L
\iff
\exists\,\Gamma:\ CD=\Gamma C.
\]

No rank assumption is required for existence; full row rank gives uniqueness. If the inclusion holds and \(V\) spans \(L\), then \(DV=V\Lambda\) for a unique reduced \(\Lambda\). A dynamically closed left coordinate requires the additional left intertwining relation; right invariance alone is insufficient.

The full statement, including fixed and moving dual bundles, is frozen in `AIEF_1_4_CONTROLLER_FIBER_THEOREM_PACKAGE.md`.

---

# Part II. Delayed phase, EMA, and augmented state

## 5. Augmented discrete state

The Markov state of the implemented simulation is

\[
X_n=(\theta_n,B_n,C_n,\mathcal H_n),
\]

where \(\mathcal H_n\) is the finite delay-history deque.

The weight vector alone is not a closed state because the driver depends on phase, delayed history, and complex EMA memory.

---

## 6. Directed phase source

For directed edge \((i,j)\), define

\[
\phi_{ij,n}
=
\theta_{i,n}
-h_{j,n}
-
\frac{\omega_i+\omega_j}{2}\tau,
\]

\[
z_{ij,n}=e^{i\phi_{ij,n}}.
\]

The phase correction is constant in time, so the source-phase increment is

\[
\boxed{
\Delta\phi_{ij,n}
=
dt(\omega_i+G_{i,n})
-
\Delta h_{j,n},
}
\]

where

\[
G_{i,n}
=
\sum_k B_{ik,n+1}
\sin(h_{k,n}-\theta_{i,n}).
\]

This decomposes exactly into intrinsic-frequency, current-coupling, and delayed-history terms.

For the exceptional K3 comparisons, both source mean and source separation increments were reconstructed to machine precision from these terms.

---

## 7. Complex EMA and tracking error

The directed EMA update is

\[
C_{n+1}
=
\alpha C_n
+
(1-\alpha)z_n.
\]

Define tracking error

\[
e_n=z_n-C_n.
\]

### Proposition 7.1 — exact tracking-error recurrence

\[
\boxed{
e_{n+1}
=
\alpha e_n
+
(z_{n+1}-z_n).
}
\]

For a difference between two directed edges, let

\[
E_n=\Delta z_n-\Delta C_n,
\qquad
S_n=\Delta z_{n+1}-\Delta z_n.
\]

Then

\[
\boxed{
E_{n+1}=\alpha E_n+S_n.
}
\]

---

# Part III. Exact magnitude-observable identities

## 8. Squared magnitude

Define

\[
M_n=|C_n|^2,
\qquad
Q_n=\Re(\overline{C_n}z_n).
\]

Since \(|z_n|=1\),

### Proposition 8.1 — exact squared-magnitude update

\[
\boxed{
M_{n+1}
=
\alpha^2M_n
+
(1-\alpha)^2
+
2\alpha(1-\alpha)Q_n.
}
\]

For two directed edges,

\[
\Delta M_n=|C_{a,n}|^2-|C_{b,n}|^2,
\]

\[
\Delta Q_n
=
\Re(\overline{C_{a,n}}z_{a,n})
-
\Re(\overline{C_{b,n}}z_{b,n}),
\]

so

\[
\boxed{
\Delta M_{n+1}
=
\alpha^2\Delta M_n
+
2\alpha(1-\alpha)\Delta Q_n.
}
\]

An effective \(\alpha\)-multiplier is obtained when

\[
2\Delta Q_n=\Delta M_n+o(\Delta M_n).
\]

---

## 9. Exact midpoint geometry

Let

\[
\bar C=\frac12(C_a+C_b),
\qquad
\Delta C=C_a-C_b,
\]

\[
\bar z=\frac12(z_a+z_b),
\qquad
\Delta z=z_a-z_b.
\]

Then

\[
\boxed{
\Delta M
=
2\Re(\overline{\bar C}\,\Delta C).
}
\]

Also

\[
\Delta Q
=
\Re(
\overline{\bar C}\,\Delta z
+
\overline{\Delta C}\,\bar z
).
\]

Therefore

### Proposition 9.1 — exact alignment decomposition

\[
\boxed{
2\Delta Q-\Delta M
=
T_1+T_2,
}
\]

with

\[
T_1
=
2\Re[
\overline{\bar C}(\Delta z-\Delta C)
],
\]

\[
T_2
=
2\Re(
\overline{\Delta C}\,\bar z
).
\]

This identity separates tracking error from tangential/mean-source geometry.

---

## 10. Magnitude and symmetrization

The directed magnitude difference satisfies exactly

\[
\boxed{
|C_a|-|C_b|
=
\frac{|C_a|^2-|C_b|^2}{|C_a|+|C_b|}.
}
\]

The physical resonance matrix is symmetrized after magnitude:

\[
\Delta R
=
\frac12(
\Delta|C|_{\rm forward}
+
\Delta|C|_{\rm reverse}
).
\]

On the audited replay, forward and reverse directed modes reinforce rather than cancel.

---

# Part IV. Exceptional K3 operator algebra

## 11. Fixed winner branch

The exceptional positive K3 has edge order

\[
(25,29,59)
=
((2,7),(2,11),(7,11)),
\]

with fixed winners

\[
(25,29,59)\mapsto(7,2,7).
\]

Let

\[
c_0=1-\gamma dt.
\]

Define

\[
\beta_{25}
=
\frac{x_{25}s_7}{q_7+\varepsilon},
\qquad
\beta_{29}
=
\frac{x_{29}s_2}{q_2+\varepsilon},
\qquad
\beta_{59}
=
\frac{x_{59}s_7}{q_7+\varepsilon}.
\]

Then

### Proposition 11.1 — exact selected K3 block

\[
\boxed{
K
=
c_0
\begin{pmatrix}
s_7-\beta_{25}&0&-\beta_{25}\\
-\beta_{29}&s_2-\beta_{29}&0\\
-\beta_{59}&0&s_7-\beta_{59}
\end{pmatrix}.
}
\]

### Proposition 11.2 — exact multiplier-controller carrier

Conditional on the audited fixed winner map, the selected controller rows are \(J=\{2,7\}\), with

\[
C_J
=
\begin{pmatrix}
1&1&0\\
1&0&1
\end{pmatrix},
\qquad
\boxed{
\ker C_J
=
\operatorname{span}\{(1,-1,-1)^T\}.
}
\]

Thus the analytic right direction \(v=(1,-1,-1)^T/\sqrt3\) is exactly the controller-fiber carrier. Node 11 changes clipping label in the saved replay but never becomes a selected multiplier controller.

---

## 12. Nested invariant families

Let

\[
v=\frac1{\sqrt3}(1,-1,-1),
\qquad
u=\frac{\sqrt3}{2}(1,0,-1).
\]

### Proposition 12.1 — right invariance

\[
Kv=\lambda v
\iff
s_2=s_7,
\]

with

\[
\lambda=c_0s_7.
\]

### Proposition 12.2 — fixed analytic left invariance

Assuming \(s_2=s_7\),

\[
u_*^TK=\lambda u_*^T
\iff
\beta_{25}=\beta_{59},
\qquad
u_*=\frac{\sqrt3}{2}(1,0,-1)^T.
\]

### Proposition 12.3 — exact pointwise left covector

If \(s_2=s_7\) and \(\beta_{59}>0\), define

\[
r=\frac{\beta_{25}}{\beta_{59}},
\qquad
u(r)=\frac{\sqrt3}{1+r}(1,0,-r)^T.
\]

Then

\[
u(r)^Tv=1,
\qquad
u(r)^TK=\lambda u(r)^T.
\]

The fixed covector \(u_*\) is recovered exactly at \(r=1\). A pointwise left eigenvector does not by itself give a fixed common cocycle dual or a moving adjoint bundle.

### Realized-support symmetry

Assume equal capacities, isolated positive proposal support, clipped controller rows 2 and 7, positive proposal coordinates, and persistence of the winner map \((7,2,7)\). Then

\[
s_2=s_7
\iff
x_{29}=x_{59},
\]

and fixed analytic left closure gives

\[
\beta_{25}=\beta_{59}
\iff
x_{25}=x_{59}.
\]

The strict winner signs are \(x_{59}-x_{29}>0\) and \(x_{25}-x_{59}>0\). Exact equality is therefore the triple-tie boundary of the strict branch. If both positive differences tend to zero without a finite crossing, the selected one-sided branch matrices converge to the fixed analytic family associated with \((u_*,v)\).

At the exact tie all three controller rows participate and

\[
C_{K_3}=\begin{pmatrix}1&1&0\\1&0&1\\0&1&1\end{pmatrix},
\qquad
\ker C_{K_3}=\{0\}.
\]

The limiting claim is therefore not a nonzero two-sided controller fiber or a unique classical Jacobian at the tied endpoint, and it is not equivalent to the mere existence of an instantaneous left covector.

---

## 13. Analytic dominant defect

Let

\[
\delta_n=\beta_{25,n}-\beta_{59,n}.
\]

Under negligible right and secondary symmetry mismatches,

\[
K_n
=
K_{{\rm sym},n}
+
c_0\delta_nE_*,
\]

where

\[
\boxed{
E_*
=
\begin{pmatrix}
-1&0&-1\\
0&0&0\\
0&0&0
\end{pmatrix}.
}
\]

The defect satisfies

\[
E_*v=0,
\]

but

\[
u^TE_*\notin\operatorname{span}(u^T).
\]

Its projections into the biorthogonal and symmetric quotient spaces explain the observed family-distance constants.

---

# Part V. Exact reduced dynamics

## 14. Biorthogonal scalar coordinate

If

\[
u^TK_n=\lambda_nu^T,
\]

and

\[
b_{n+1}=K_nb_n+f_n,
\]

then

### Proposition 14.1 — exact scalar recurrence

\[
\boxed{
a_{n+1}=\lambda_na_n+g_n,
}
\]

where

\[
a_n=u^Tb_n,
\qquad
g_n=u^Tf_n.
\]

This recurrence is exact for arbitrary transverse components of \(b_n\). It explains why the left coordinate repairs the Euclidean direction-0 rollout.

---

## 15. Duhamel decomposition

For the weight tangent,

\[
b_{n+1}=K_nb_n+f_n.
\]

Define

\[
h_{n+1}=K_nh_n,
\qquad
r_{n+1}=K_nr_n+f_n,
\]

with \(h_0=b_0\), \(r_0=0\). Then

\[
\boxed{
b_n=h_n+r_n.
}
\]

This is an exact block decomposition once \(K_n\) and \(f_n\) are fixed.

---

## 16. Conditional triangular memory lemma

Assume late constants or asymptotically stationary sequences satisfy

\[
a_{n+1}=\lambda_Ba_n+g_n,
\]

\[
g_{n+1}=\alpha g_n.
\]

Then a forcing contribution of age \(k\) has relative factor

\[
\left(\frac{\lambda_B}{\alpha}\right)^k.
\]

Therefore the memory-envelope rate is

\[
\boxed{
\kappa
=
-\frac1{dt}
\log\left|\frac{\lambda_B}{\alpha}\right|.
}
\]

This is a theorem about the triangular model, not an unconditional AIEF law.

---

# Part VI. Resonant source tracking

## 17. Jordan-resonant tracking lemma

Let \(E_n,S_n\in\mathbb C\) and let \(0<|\alpha|<1\). Suppose

\[
E_{n+1}=\alpha E_n+S_n,
\qquad
S_n=B\alpha^{n+1}
\]

for every \(n\ge0\).

### Proposition 17.1 — exact resonant solution

\[
\boxed{
E_n=(E_0+Bn)\alpha^n.
}
\]

Moreover,

\[
\begin{pmatrix}
E_{n+1}\\S_{n+1}
\end{pmatrix}
=
\begin{pmatrix}
\alpha&1\\0&\alpha
\end{pmatrix}
\begin{pmatrix}
E_n\\S_n
\end{pmatrix}.
\]

If additionally

\[
S_n=\Delta z_{n+1}-\Delta z_n,
\]

then \(\Delta z_n\) converges and

\[
\boxed{
\Delta z_\infty
=
\Delta z_n
+
\frac{B\alpha^{n+1}}{1-\alpha}.
}
\]

### Proposition 17.2 — perturbed resonant solution

Suppose instead

\[
S_n=B\alpha^{n+1}+r_n.
\]

Then variation of constants gives the exact identity

\[
\boxed{
E_n
=
(E_0+Bn)\alpha^n
+
\sum_{k=0}^{n-1}\alpha^{n-1-k}r_k,
}
\]

or equivalently, with

\[
\rho_k=\frac{r_k}{\alpha^{k+1}},
\]

\[
\boxed{
\frac{E_n}{\alpha^n}
=
E_0+Bn+
\sum_{k=0}^{n-1}\rho_k.
}
\]

If \(S_n=\Delta z_{n+1}-\Delta z_n\) and the remainder tail converges, then

\[
\boxed{
\Delta z_\infty-\Delta z_n
=
\frac{B\alpha^{n+1}}{1-\alpha}
+
\sum_{k=n}^{\infty}r_k.
}
\]

The error of the finite-time source estimator is therefore exactly the unobserved remainder tail.

### Asymptotic hierarchy

1. If \(\sum_{k=0}^{\infty}\rho_k\) converges, then for some constant \(A\),
   \[
   E_n=(A+Bn)\alpha^n+o(\alpha^n),
   \]
   and the source-estimator error is \(o(|\alpha|^n)\).

2. If \(\rho_n\to0\), equivalently \(r_n=o(\alpha^{n+1})\), then Cesàro's theorem gives
   \[
   \sum_{k=0}^{n-1}\rho_k=o(n),
   \]
   so
   \[
   E_n=(E_0+Bn+o(n))\alpha^n.
   \]
   Also \(\sum|r_n|<\infty\), and the source-estimator tail is \(o(|\alpha|^n)\).

3. If only \(\rho_n=O(1)\), then
   \[
   E_n=(E_0+Bn+O(n))\alpha^n,
   \]
   while the source-estimator tail is \(O(|\alpha|^n)\) and remains consistent. If the Cesàro mean
   \[
   \frac1n\sum_{k=0}^{n-1}\rho_k\to L
   \]
   exists, then
   \[
   E_n=(E_0+(B+L)n+o(n))\alpha^n.
   \]

Without geometric control of \(r_n\), no general resonant asymptotic conclusion follows.

### AIEF application status

The replay shows finite-horizon convergence of

\[
\frac{S_n}{\alpha^{n+1}}\to B
\]

and affine behavior of

\[
\frac{E_n}{\alpha^n}
\]

over late windows. Conditional on continuation of that asymptotic regime, the trajectory falls in the \(\rho_n\to0\) case. This supports the \(o(n)\) tracking correction and a consistent source-limit estimator, but does not yet establish convergence of \(\sum\rho_n\) or the stronger fixed-intercept form.

---

# Part VII. Replay-established asymptotics

The following are numerical results on the frozen exceptional replay and tested directions, not general theorems.

## 18. Fixed branch and augmented tangent

- The effective K3 winner map has zero changes over 32,001 saved states.
- The tolerance event at `t=124.05` changes no implemented positive-edge formula.
- The frozen-driver K3 cocycle predicts frozen nonlinear perturbations accurately.
- The augmented tangent predicts coupled nonlinear perturbations with median K3 error around `5e-4` over resolved horizons.
- All tested nonlinear perturbations preserve the audited winner branch.

## 19. Non-normal transient

- Full K3 peak amplification is about `1.27097` at `t=0.1`.
- Split-lineality peak amplification is about `1.20563`.
- A constant initial matrix reproduces this peak.
- Diagonal scale alone does not amplify.
- The node-mediated low-rank term creates the transient and severe anisotropy.

## 20. Rank-one and biorthogonal reduction

- Late total and feedback tangent POD first-mode fractions are effectively one.
- The geometric right direction is
  \[
  v=(1,-1,-1)/\sqrt3.
  \]
- The analytic left covector is
  \[
  u=\sqrt3(1,0,-1)/2.
  \]
- Fixed late biorthogonal coordinates reduce direction-0 final rollout error from about `0.74` to about `1.9e-5` for a rollout starting at `t=250`.
- A time-varying adjoint covector gives no material improvement.

## 21. Nested-family and defect mode

- Exact fixed-winner sparsity holds.
- The right-invariant family is reached far earlier than the biorthogonal/symmetric families.
- The analytic projected defect matches numerical defect POD at cosine `1-O(1e-12)`.
- Direct defect reconstruction error is approximately `3e-6` relative.
- Dominant defect and family-defect matrices follow the EMA multiplier pointwise to approximately `1e-9` late.

## 22. Duhamel and memory

- Exact Duhamel crossover times are approximately `0.38` and `72.86` for the two tested directions.
- Feedback forcing is individually small but strongly aligned with persistent output directions.
- Final feedback is reconstructed to 1% using roughly the previous `66.6` time units.
- The late operational memory rate is approximately
  \[
  \kappa\approx0.06913.
  \]
- Direct propagation gives
  \[
  \kappa\approx r_{\rm prop}-r_g
  \]
  to about `1e-6` at the final target.

## 23. Radial observable and complex persistence

- Directed complex EMA differences and source differences persist in norm.
- Directed squared-magnitude differences independently acquire the EMA multiplier.
- Forward and reverse magnitude differences reinforce; symmetrization does not create the mode.
- Radial fractions decrease to order `1e-7`, while tangential components persist.
- Mean source and memory directions align to order `1e-7`.
- Tracking and tangential alignment terms become equal and opposite to order `1e-6` or better.

## 24. Resonant source and phase balance

- Complex source increments follow the EMA-rate envelope.
- \(E_n/\alpha^n\) is complex affine in \(n\) with late `R^2` effectively one.
- \(S_n/\alpha^{n+1}\) matches the affine slope.
- Independent estimates of \(\Delta z_\infty\) collapse to relative spreads near `1e-13` late.
- Source mean and source separation increments both acquire the EMA rate.
- Their net values arise from cancellation of intrinsic-frequency, coupling, and delayed-history terms.
- Source and memory angular separations freeze, while radius differences decay at the EMA rate.

---

# Part VIII. Structural and replay-specific mechanisms

The exact structural chain is

\[
\boxed{
\text{multiplier-controller fiber}
\longrightarrow
\text{fiber-affine action}
\longrightarrow
\begin{cases}
\text{right defect }s_2-s_7,\\
\text{fixed-left defect }\beta_{25}-\beta_{59}.
\end{cases}}
\]

Under the isolated equal-capacity persistent-branch assumptions, these defects are proportional to the distinct proposal differences

\[
x_{59}-x_{29},
\qquad
x_{25}-x_{59},
\]

respectively.

The replay-specific dynamical chain is

\[
\boxed{
\begin{aligned}
&\text{delayed phase-balance and EMA feedback}\\
&\Downarrow\\
&\text{radial and proposal-difference decay}\\
&\Downarrow\\
&\text{right- and fixed-left-defect decay}\\
&\Downarrow\\
&\text{approach to fixed analytic pair closure}.
\end{aligned}}
\]

The detailed route contains resonant tracking, persistent tangential complex separation, \(T_1\approx-T_2\), and exact downstream \(\Delta R\to\Delta B\to\Delta x\to K\) identities. This is finite-horizon evidence on one fixed winner branch, not an infinite-time theorem.

---

# Part IX. Claims explicitly not established

The current evidence does **not** establish:

- a universal scalar reduction for all AIEF components;
- a universal defect matrix across winner branches;
- a full-system Jordan block;
- an invariant manifold or toroidal attractor;
- causal control by EMA solely from rate matching;
- a closed-loop gain equal to \(\lambda_B/\alpha\);
- a valid future-only `T_window` sweep from the saved split state;
- timestep/safeguard convergence of the finite map;
- infinite-time persistence of the exceptional support, clipping, and winner branch;
- asymptotic convergence of \(x_{59}-x_{29}\) and \(x_{25}-x_{59}\) to zero;
- generality beyond the frozen seed and tested directions.

---

# Part X. Theorem and formalization frontier

## 25. Proof-ready implementation results

The following can be formalized directly from the code:

1. admissibility factorization;
2. exact row-sum fiber linearity;
3. polyhedral tangent-cone lineality and safeguarded output interiority;
4. tie-safe multiplier-controller fiber affinity;
5. invariance/intertwining factorization and dual-closure lemmas;
6. branchwise Jacobian;
7. exact exceptional controller-row kernel;
8. fixed-winner K3 sparse form;
9. right-invariant and fixed-biorthogonal family characterizations;
10. exact pointwise left covector and fixed analytic pair conditions;
11. explicit raw and projected defect matrices;
12. squared-magnitude identity;
13. tracking-error recurrence;
14. alignment-residual decomposition;
15. directed phase-increment decomposition.

## 26. Conditional asymptotic lemmas

The following require stated assumptions:

1. defect perturbation bound;
2. pointwise EMA defect recurrence;
3. Jordan-resonant tracking solution;
4. radial quotient alpha-mode;
5. triangular memory-gap law;
6. convergence of the numerical left mode;
7. source mean/separation limit.

## 27. Remaining upstream mathematical question

A conditional branch theorem would assume persistent isolated positive proposal support, clipped controller rows 2 and 7, and the fixed winner map \((7,2,7)\), and then derive

\[
x_{59,n}-x_{29,n}\to0,
\qquad
x_{25,n}-x_{59,n}\to0
\]

from the coupled delayed phase/EMA dynamics. A stronger trajectory theorem would also prove those branch-persistence assumptions from the frozen split state.

The upstream obstacle is to derive why the delayed phase-balance and radial residuals acquire the EMA-rate envelope when phase, history, weight, and EMA perturbations are coupled, rather than treating source stabilization as an observed input.

---

# Part XI. Recommended next actions

1. Freeze the multiplier-controller theorem supplement and updated manuscript hashes.
2. Develop the conditional branch theorem without promoting finite-horizon trends to limits.
3. Complete the matched-phase `B_carrier_only/full_reset` correction.
4. Only then run separately versioned, fully regenerated `T_window`, timestep, and safeguard studies.
5. Defer full-attractor topology and new broad cohorts.

---

# Part XII. Reproducibility anchors

Principal analysis sources:

```text
AIEF_1_4_actual_admissibility_branch_audit.py
AIEF_1_4_frozen_driver_cocycle_analysis.py
AIEF_1_4_augmented_tangent_cocycle_analysis.py
AIEF_1_4_augmented_duhamel_feedback_analysis.py
AIEF_1_4_feedback_rank_memory_reduction.py
AIEF_1_4_scalar_spectral_gap_reduction.py
AIEF_1_4_propagation_gap_geometric_control.py
AIEF_1_4_parameter_free_triangular_closure.py
AIEF_1_4_biorthogonal_triangular_closure.py
AIEF_1_4_nested_operator_family_audit.py
AIEF_1_4_defect_recurrence_analytic_mode.py
AIEF_1_4_defect_causal_ema_trace.py
AIEF_1_4_radial_observable_subsystem_analysis.py
AIEF_1_4_phase_source_locking_analysis.py
AIEF_1_4_resonant_tracking_angular_analysis.py
AIEF_1_4_phase_balance_source_dynamics.py
```

Administrative sources of truth:

```text
AIEF_HISTORIC_UNFOLDING.md
AIEF_1_4_OPERATOR_COCYCLE_THOUGHT_TREE.md
AIEF_1_4_FORWARD_PLAN.md
AI_AGENT_HANDOFF_PROMPT.md
```

---

# Closing statement

The project began with network-level falsification and memory ablation. Its current mathematical center is an implementation-derived operator hierarchy coupled to a replay-validated augmented tangent mechanism.

The strongest current result is not merely that a scalar defect decays at the EMA rate. It is that, on one audited branch, a delayed phase-balance mode generates a persistent complex separation whose radial observable follows an EMA-rate quotient dynamics, which is then transferred exactly into the adaptive weight and operator-defect sectors.

The next progress should come through proof, consolidation, and carefully scoped generalization—not another unconstrained expansion of simulations.
