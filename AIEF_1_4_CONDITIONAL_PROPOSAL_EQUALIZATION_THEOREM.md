# AIEF-1.4 conditional proposal-equalization theorem

**Status:** proof-oriented next-step note  
**Date:** 2026-07-27  
**Scope:** exceptional K3 on a persistent isolated multiplier-controller branch  

## 1. Purpose

The controller-fiber theorem identified the two proposal differences that control closure of the fixed analytic K3 pair:

\[
d_n^{\mathrm L}=x_{25,n}-x_{59,n},
\qquad
d_n^{\mathrm R}=x_{59,n}-x_{29,n}.
\]

This note proves that, on the persistent isolated branch, proposal equalization follows from decay of the corresponding resonance differences. It then gives a sufficient EMA-level condition—vanishing directed alignment residuals—for resonance equalization.

The note does **not** prove that the delayed phase dynamics generate those alignment limits, and it does not prove infinite-time branch persistence.

---

# Part I. Persistent-branch assumptions and exact recurrences

## 2. Branch assumptions

For all \(n\ge n_0\), assume:

1. the positive proposal component is exactly the K3 with edges
   \[
   25=(2,7),\qquad29=(2,11),\qquad59=(7,11);
   \]
2. proposal coordinates \(x_{25,n},x_{29,n},x_{59,n}\) are positive;
3. rows 2 and 7 are clipped;
4. capacities are equal to \(c>0\);
5. the effective winner map is
   \[
   25\mapsto7,\qquad29\mapsto2,\qquad59\mapsto7;
   \]
6. the production parameters and update order remain unchanged.

Define

\[
c_0=1-\gamma dt,
\qquad
a_R=dt(\eta+\mu).
\]

The production values satisfy \(0<c_0<1\) and \(a_R>0\).

At step \(n\), let \(R_{e,n}\) denote the symmetrized resonance driver computed from the newly updated EMA and used to form the proposal \(x_{e,n}\).

### Proposition 2.1 — strict-branch cone and tie boundary

On the isolated equal-capacity clipped K3,

\[
q_{7,n}-q_{2,n}=x_{59,n}-x_{29,n}=d_n^{\mathrm R},
\]

\[
q_{2,n}-q_{11,n}=x_{25,n}-x_{59,n}=d_n^{\mathrm L}.
\]

Because the clipped scale is strictly decreasing in the proposal row sum, the strict winner map

\[
25\mapsto7,
\qquad29\mapsto2,
\qquad59\mapsto7
\]

is equivalent to

\[
\boxed{d_n^{\mathrm L}>0,\qquad d_n^{\mathrm R}>0.}
\]

Thus proposal equalization approaches the corner of this open branch cone. It cannot remain an interior strict-winner point at the exact equality limit.

At

\[
x_{25}=x_{29}=x_{59},
\]

all three node scales tie. The tie-safe multiplier-controller set contains all three K3 rows, whose incidence matrix is

\[
C_{K_3}
=
\begin{pmatrix}
1&1&0\\
1&0&1\\
0&1&1
\end{pmatrix},
\qquad
\det C_{K_3}=-2,
\]

so

\[
\ker C_{K_3}=\{0\}.
\]

Consequently, the nonzero carrier \(v\) belongs to the partial-controller fiber at every strict finite branch state, while the exact tied limiting map has no nonzero two-sided K3 controller fiber. Any closure conclusion below concerns convergence of the selected one-sided branch matrices, not a unique classical derivative at the tied endpoint.

### Proof

The row-sum identities follow from isolation. Equal capacities make scale order the reverse of row-sum order. The third winner inequality is implied by

\[
q_7-q_{11}=(q_7-q_2)+(q_2-q_{11})=d_n^{\mathrm R}+d_n^{\mathrm L}>0.
\]

The determinant calculation gives the tied-fiber assertion. ∎

---

## 3. Difference coordinates

Define weight differences

\[
b_n^{\mathrm L}=B_{25,n}-B_{59,n},
\qquad
b_n^{\mathrm R}=B_{59,n}-B_{29,n},
\]

resonance differences

\[
r_n^{\mathrm L}=R_{25,n}-R_{59,n},
\qquad
r_n^{\mathrm R}=R_{59,n}-R_{29,n},
\]

and proposal differences

\[
d_n^{\mathrm L}=x_{25,n}-x_{59,n},
\qquad
d_n^{\mathrm R}=x_{59,n}-x_{29,n}.
\]

Because all selected proposal coordinates remain positive, the positivity map is the identity on these coordinates.

### Proposition 3.1 — exact proposal identities

For every \(n\ge n_0\),

\[
\boxed{
d_n^{\mathrm L}=c_0b_n^{\mathrm L}+a_Rr_n^{\mathrm L}}
\]

and

\[
\boxed{
d_n^{\mathrm R}=c_0b_n^{\mathrm R}+a_Rr_n^{\mathrm R}.}
\]

### Proof

On a positive proposal edge,

\[
x_{e,n}
=c_0B_{e,n}+a_RR_{e,n}-dt\,\mu.
\]

The edge-independent \(-dt\,\mu\) term cancels in each difference. ∎

---

## 4. Exact projected-weight difference identities

The isolated proposal row sums are

\[
q_{2,n}=x_{25,n}+x_{29,n},
\qquad
q_{7,n}=x_{25,n}+x_{59,n}.
\]

The controller scales are

\[
s_{2,n}=\frac{c}{q_{2,n}+\varepsilon},
\qquad
s_{7,n}=\frac{c}{q_{7,n}+\varepsilon}.
\]

### Proposition 4.1 — fixed-left channel projection

\[
\boxed{
b_{n+1}^{\mathrm L}=s_{7,n}d_n^{\mathrm L}.}
\]

### Proof

Edges 25 and 59 share the same strict controller row 7, so

\[
B_{25,n+1}=s_{7,n}x_{25,n},
\qquad
B_{59,n+1}=s_{7,n}x_{59,n}.
\]

Subtract. ∎

### Proposition 4.2 — right-mode channel projection

Define

\[
\sigma_n^{\mathrm R}
=
\frac{c(x_{25,n}+\varepsilon)}
{(q_{7,n}+\varepsilon)(q_{2,n}+\varepsilon)}.
\]

Then

\[
\boxed{
b_{n+1}^{\mathrm R}=\sigma_n^{\mathrm R}d_n^{\mathrm R}.}
\]

### Proof

Using the winner map,

\[
B_{59,n+1}=\frac{cx_{59,n}}{x_{25,n}+x_{59,n}+\varepsilon},
\]

\[
B_{29,n+1}=\frac{cx_{29,n}}{x_{25,n}+x_{29,n}+\varepsilon}.
\]

Set \(a_n=x_{25,n}+\varepsilon\). Then

\[
\frac{x_{59,n}}{a_n+x_{59,n}}
-
\frac{x_{29,n}}{a_n+x_{29,n}}
=
\frac{a_n(x_{59,n}-x_{29,n})}
{(a_n+x_{59,n})(a_n+x_{29,n})}.
\]

Multiply by \(c\). ∎

### Corollary 4.3 — uniform contraction bounds

Let

\[
\sigma_n^{\mathrm L}=s_{7,n}.
\]

Then

\[
0<\sigma_n^{\mathrm L}<1,
\qquad
0<\sigma_n^{\mathrm R}<1.
\]

Indeed,

\[
\sigma_n^{\mathrm R}
=s_{7,n}
\frac{x_{25,n}+\varepsilon}{q_{2,n}+\varepsilon}
<1.
\]

Consequently

\[
0<\lambda_n^j< c_0<1,
\qquad
\lambda_n^j=c_0\sigma_n^j,
\qquad j\in\{\mathrm L,\mathrm R\}.
\]

---

## 5. Exact forced proposal recurrences

### Proposition 5.1 — stable scalar recurrences

For \(j\in\{\mathrm L,\mathrm R\}\),

\[
\boxed{
d_{n+1}^j=\lambda_n^j d_n^j+a_Rr_{n+1}^j.}
\]

### Proof

Apply Proposition 3.1 at step \(n+1\), then substitute the corresponding projected-weight identity from Proposition 4.1 or 4.2. ∎

This is an exact implementation-level downstream closure. The delayed phase and EMA variables enter only through the forcing \(r_{n+1}^j\).

---

# Part II. Stable-filter consequences

## 6. Variable-multiplier stability lemma

### Lemma 6.1

Suppose

\[
y_{n+1}=\lambda_ny_n+f_{n+1},
\qquad
|\lambda_n|\le\rho<1.
\]

Then

\[
\boxed{
|y_n|
\le
\rho^{n-n_0}|y_{n_0}|
+
\sum_{k=n_0+1}^{n}\rho^{n-k}|f_k|.
}
\]

If \(f_n\to0\), then \(y_n\to0\).

### Proof

Iterate the recurrence and bound each product of multipliers by the corresponding power of \(\rho\). For convergence, split the convolution into a finite early part, which decays geometrically, and a late part on which \(|f_k|\) is uniformly small. ∎

### Theorem 6.2 — resonance equalization implies proposal equalization

Under the persistent-branch assumptions, if

\[
r_n^{\mathrm L}\to0,
\qquad
r_n^{\mathrm R}\to0,
\]

then

\[
\boxed{
d_n^{\mathrm L}\to0,
\qquad
d_n^{\mathrm R}\to0.}
\]

Equivalently,

\[
\boxed{
x_{25,n}-x_{59,n}\to0,
\qquad
x_{59,n}-x_{29,n}\to0.}
\]

Hence the selected one-sided frozen-driver branch matrices approach the fixed analytic family associated with \((u_*,v)\). This does not assert a nonzero two-sided fiber or unique classical derivative at the exact triple tie.

### Proof

Apply Lemma 6.1 to Proposition 5.1 with \(f_{n+1}=a_Rr_{n+1}^j\) and the uniform bound \(|\lambda_n^j|\le c_0<1\). ∎

### Remark 6.3

This theorem does not infer resonance equalization from rate matching. It proves only the exact stable transfer

\[
\Delta R\to\Delta x\to\text{operator closure}
\]

on the stated branch.

---

## 7. Rate transfer

If \(|\lambda_n^j|\le\bar\lambda_j<1\) eventually and

\[
r_n^j=O(\zeta^n),
\qquad 0<\zeta<1,
\]

then the convolution bound gives

\[
d_n^j=
\begin{cases}
O(\max(\bar\lambda_j,\zeta)^n),&\bar\lambda_j\ne\zeta,\\
O(n\zeta^n),&\bar\lambda_j=\zeta.
\end{cases}
\]

Thus an EMA-rate proposal mode follows if the resonance forcing has multiplier \(\alpha\) and the branch contraction is uniformly faster than \(\alpha\). This rate ordering is replay evidence and is not assumed in Theorem 6.2.

---

# Part III. EMA radial condition sufficient for resonance equalization

## 8. Directed squared-magnitude recurrence

Consider any directed comparison of two edges \(a,b\). Let

\[
C_{a,n+1}=\alpha C_{a,n}+(1-\alpha)z_{a,n},
\]

\[
C_{b,n+1}=\alpha C_{b,n}+(1-\alpha)z_{b,n},
\]

with \(|z_{a,n}|=|z_{b,n}|=1\). Define

\[
\Delta M_n=|C_{a,n}|^2-|C_{b,n}|^2,
\]

\[
\Delta A_n
=\Re(\overline{C_{a,n}}z_{a,n})
-
\Re(\overline{C_{b,n}}z_{b,n}),
\]

and the alignment residual

\[
e_n=2\Delta A_n-\Delta M_n.
\]

### Proposition 8.1 — exact radial forced recurrence

\[
\boxed{
\Delta M_{n+1}
=\alpha\Delta M_n
+\alpha(1-\alpha)e_n.
}
\]

### Proof

The unit-modulus source terms cancel in the edge difference, giving

\[
\Delta M_{n+1}
=\alpha^2\Delta M_n
+2\alpha(1-\alpha)\Delta A_n.
\]

Substitute \(2\Delta A_n=\Delta M_n+e_n\). ∎

### Corollary 8.2 — alignment convergence implies directed magnitude convergence

If \(e_n\to0\), then \(\Delta M_n\to0\). If additionally

\[
|C_{a,n}|+|C_{b,n}|\ge m_*>0
\]

eventually, then

\[
|C_{a,n}|-|C_{b,n}|
=
\frac{\Delta M_n}{|C_{a,n}|+|C_{b,n}|}
\to0.
\]

### Proof

Apply Lemma 6.1 to Proposition 8.1 with multiplier \(\alpha<1\). Then use the exact difference-of-squares quotient. ∎

---

## 9. Symmetrized resonance

Under the production indexing, step \(n\) first forms

\[
C_{n+1}=\alpha C_n+(1-\alpha)z_n
\]

and then uses

\[
R_{e,n}
=\frac12\left(|C_{ij,n+1}|+|C_{ji,n+1}|\right)
\]

for the proposal at the same step. Thus convergence of the directed magnitude differences at index \(n+1\) gives convergence of the resonance forcing \(r_n^j\).

For each proposal channel \(j\in\{\mathrm L,\mathrm R\}\), compare its two undirected edges in both directed orientations. Let

\[
e_{n,\rightarrow}^j,
\qquad
e_{n,\leftarrow}^j
\]

be the corresponding alignment residuals.

### Proposition 9.1 — directed radial conditions imply resonance equalization

Suppose for both channels and both orientations:

1. \(e_{n,\rightarrow}^j\to0\) and \(e_{n,\leftarrow}^j\to0\);
2. the two directed magnitude denominators are eventually bounded below by a positive constant.

Then

\[
\boxed{
r_n^{\mathrm L}\to0,
\qquad
r_n^{\mathrm R}\to0.}
\]

### Proof

Corollary 8.2 gives convergence of each directed magnitude difference to zero. Their symmetrized averages are exactly \(r_n^{\mathrm L}\) and \(r_n^{\mathrm R}\). ∎

---

## 10. Conditional proposal-equalization theorem

### Theorem 10.1

Under the persistent-branch assumptions of Section 2, suppose the directed alignment residuals for both edge pairs

\[
(25,59),
\qquad
(59,29)
\]

vanish in both orientations, and suppose the corresponding directed magnitude denominators remain bounded away from zero. Then

\[
\boxed{
x_{25,n}-x_{59,n}\to0,
\qquad
x_{59,n}-x_{29,n}\to0.}
\]

Therefore the selected one-sided frozen-driver K3 branch matrices approach the fixed analytic family associated with \((u_*,v)\). The exact tied map remains directionally nonsmooth and has zero full K3 controller-fiber lineality.

### Proof

Proposition 9.1 yields resonance equalization. Theorem 6.2 then yields proposal equalization. The fixed-pair conclusion follows from the exact controller-fiber closure identities. ∎

---

# Part IV. What remains open

## 11. Reduced proof frontier

The downstream implication is now proved conditionally:

\[
\boxed{
\text{directed alignment-residual decay}
\Longrightarrow
\text{resonance equalization}
\Longrightarrow
\text{proposal equalization}
\Longrightarrow
\text{fixed-pair operator closure}.}
\]

The remaining tasks are:

1. audit the previously unanalyzed right-mode pair \((59,29)\) on the saved replay;
2. derive alignment-residual decay from the delayed phase/history/EMA dynamics rather than treating it as an observed input;
3. prove that \(d_n^{\mathrm L},d_n^{\mathrm R}>0\) for every finite future step while both tend to zero, or retain this one-sided branch approach as an explicit hypothesis;
4. distinguish finite-horizon EMA-rate fits from infinite-time bounds;
5. formulate the limiting object as a one-sided branch-matrix limit rather than a classical Jacobian on the triple-tie stratum.

The stronger trajectory theorem must prove the one-sided branch-cone invariance, the alignment limits, and convergence to the tie boundary from the frozen split state. Existing replay evidence is not such a proof.
