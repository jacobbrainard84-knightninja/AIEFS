# Finite-step constraint geometry and asymptotic reduction in AIEF

## A proof-oriented manuscript section

### Scope

This section develops exact algebraic properties of the implemented AIEF admissibility map and of one fixed-winner K3 branch. It then states conditional reduction lemmas that organize replay-established asymptotic behavior. Exact propositions are separated from numerical observations and from open generalizations.

The results concern the discrete implemented algorithm unless explicitly labeled “ideal.” The fixed denominator safeguard is denoted by \(\varepsilon>0\). The global ideal-map directional-differentiability theorem remains open.

---

## Abstract

AIEF is an adaptive delayed phase-oscillator network whose symmetric edge weights are constrained by nonnegativity and node-capacity inequalities. The production algorithm applies an Euler proposal followed by positivity and a symmetric endpoint scaling. We show that the post-positivity admissibility stage factorizes as a diagonal edge action depending only on proposal row sums. Consequently it is exactly affine-linear on nonnegative row-sum fibers and smooth rational on open fixed-winner strata. We derive its branchwise Jacobian and directional formula at endpoint ties, distinguish exact polyhedral face lineality from finite-safeguard multiplier-controller fibers, and prove a tie-safe fiber-affine reduction theorem.

For a three-edge component observed on a fixed winner branch, the selected weight Jacobian belongs to an exact sparse matrix family. Its geometric right carrier is the explicit kernel of the audited controller-row incidence matrix. We characterize nested right-invariant, fixed-biorthogonal, and symmetric subfamilies, derive both the pointwise left covector and its fixed parameter-free limit, and identify an explicit defect matrix that preserves the right line while breaking the fixed-left relation. The resulting fixed biorthogonal coordinate obeys an exact scalar recurrence when the stated common-basis hypotheses hold.

We also derive exact directed EMA tracking and squared-magnitude identities. Under a resonant geometric source increment, the EMA tracking error has a Jordan-type polynomial-times-exponential solution. A conditional triangular reduction yields a relative-retention memory rate. Numerical evidence from one frozen replay is summarized separately: it supports a fixed winner branch, an analytic rank-one defect, a biorthogonal late scalar coordinate, resonant EMA tracking, and a radial observable mode. These replay observations motivate but do not establish universal asymptotic theorems.

---

# 1. Model and notation

## 1.1 Undirected edge coordinates

Let \(N\) be the number of nodes and

\[
m=\binom N2
\]

the number of unique undirected edges. Let

\[
w\in\mathbb R^m
\]

be the edge-weight vector and

\[
A\in\{0,1\}^{N\times m}
\]

the unsigned incidence matrix: \(A_{ie}=1\) if node \(i\) is incident to edge \(e\).

The capacity-constrained set is

\[
\mathcal C
=
\{w\in\mathbb R^m:w\ge0,\ Aw\le c\},
\]

where \(c\in\mathbb R_{>0}^N\). In the frozen production model all capacities are equal, but the implementation identities below do not require equal capacities unless stated.

## 1.2 Adaptive proposal

At one discrete step, let

\[
F=(\eta+\mu)R-\mu-\gamma w
\]

be the edge driver. The raw Euler proposal is

\[
z=w+dtF.
\]

Positivity is applied edgewise:

\[
x=z_+.
\]

Let

\[
q=Ax
\]

be the post-positivity proposal row sums.

## 1.3 Global gate and node scales

The production code first checks whether any proposal row violates capacity. If no row violates, no scaling is applied. If at least one row violates, define

\[
s_i(q)
=
\min\left(1,\frac{c_i}{q_i+\varepsilon}\right),
\qquad \varepsilon>0.
\]

For edge \(e=(i,j)\), define

\[
m_e(q)=\min(s_i(q),s_j(q)).
\]

Let

\[
M(q)=\operatorname{diag}(m_e(q)).
\]

The notation \(\mathcal A_\varepsilon\) will denote the post-positivity admissibility stage, not the preceding positivity map.

---

# 2. Exact structure of the implemented admissibility map

## Proposition 2.1 — factorization

For every nonnegative proposal \(x\),

\[
\boxed{
\mathcal A_\varepsilon(x)=M(Ax)x.
}
\]

### Proof

If the global gate is off, the implementation returns \(x\), so the result holds with \(M=I\). If the global gate is on, the symmetric matrix implementation multiplies edge \((i,j)\) by

\[
\min(s_i,s_j)=m_e.
\]

In unique-edge coordinates this is exactly multiplication by the diagonal matrix \(M(q)\), with \(q=Ax\). ∎

## Corollary 2.2 — exact fiber linearity

Let \(x,y\ge0\) satisfy

\[
Ax=Ay=q.
\]

Then

\[
\boxed{
\mathcal A_\varepsilon(y)-\mathcal A_\varepsilon(x)
=M(q)(y-x).
}
\]

### Proof

By Proposition 2.1,

\[
\mathcal A_\varepsilon(y)=M(q)y,
\qquad
\mathcal A_\varepsilon(x)=M(q)x.
\]

Subtract. ∎

### Remark 2.3

The identity is finite, not merely differential. The nonnegative row-sum fiber

\[
\mathcal F_q^+=\{x\ge0:Ax=q\}
\]

is generally an affine polytope, and the restriction of \(\mathcal A_\varepsilon\) to that fiber is the restriction of a linear diagonal map.

---

## 2.1 Proposal-space stratification

The strict formulas used by \(\mathcal A_\varepsilon\) are determined by:

1. the global gate state;
2. the node scale-clipping set;
3. the endpoint winner for every edge.

For clipped nodes \(i,j\),

\[
s_i<s_j
\iff
c_i(q_j+\varepsilon)<c_j(q_i+\varepsilon).
\]

Since \(q=Ax\), this is an affine inequality in \(x\). Together with gate and clipping inequalities, the strict branch regions are relatively open polyhedral cells. On each such cell the map is smooth rational.

## Proposition 2.4 — strict-branch Jacobian

Suppose the global gate is on, the clipping set is locally constant, and edge \(e\) has a unique winning endpoint \(k(e)\). Then

\[
\boxed{
D\mathcal A_\varepsilon(x)_{ef}
=
s_{k(e)}\delta_{ef}
-
\frac{x_es_{k(e)}}{q_{k(e)}+\varepsilon}
A_{k(e)f}.
}
\]

### Proof

On the fixed branch,

\[
y_e=x_es_{k(e)}.
\]

For a clipped winner \(k\),

\[
s_k=\frac{c_k}{q_k+\varepsilon},
\qquad
q_k=\sum_fA_{kf}x_f.
\]

Therefore

\[
\frac{\partial s_k}{\partial x_f}
=-\frac{c_k}{(q_k+\varepsilon)^2}A_{kf}
=-\frac{s_k}{q_k+\varepsilon}A_{kf}.
\]

Apply the product rule. ∎

## Proposition 2.5 — endpoint-tie directional derivative

Suppose \(s_i=s_j\) for edge \(e=(i,j)\), away from the safeguarded global-gate discontinuity. For perturbation \(h\), let \(s_i'[h]\), \(s_j'[h]\) denote the node-scale directional derivatives. Then

\[
m_e'[h]=\min(s_i'[h],s_j'[h]),
\]

and

\[
\boxed{
\mathcal A_\varepsilon'(x;h)_e
=m_eh_e+x_em_e'[h].
}
\]

### Remark 2.6

At an active tie the directional map is positively homogeneous but generally nonadditive. A classical Fréchet derivative need not exist.

## Proposition 2.7 — branch persistence

Let an open strict stratum be described by finitely many affine inequalities

\[
\ell_r(x)=a_r^Tx+b_r>0.
\]

Define, for a chosen norm and its dual,

\[
\rho(x)=\min_r\frac{\ell_r(x)}{\|a_r\|_*}.
\]

If \(\rho(x)>0\), every \(h\) with \(\|h\|<\rho(x)\) remains in the same stratum.

### Proof

For each \(r\),

\[
\ell_r(x+h)
\ge
\ell_r(x)-\|a_r\|_*\|h\|>0.
\]

∎

## Remark 2.8 — global-gate caveat

With fixed \(\varepsilon>0\), scaling is skipped immediately below the global gate but uses \(q+\varepsilon\) immediately above it. Hence the production map has a small discontinuity of order \(\varepsilon/c\) at gate onset. Any global directional theorem must distinguish the implemented safeguarded map from the ideal \(\varepsilon=0\) map.

---

## 2.2 Polyhedral lineality and safeguarded output interiority

Let \(w\in\mathcal C\), let

\[
S_w=\{e:w_e>0\},
\qquad
I_{\rm face}=\{i:(Aw)_i=c_i\}.
\]

## Proposition 2.9 — lineality of the capacity tangent cone

The lineality space of the tangent cone of \(\mathcal C\) at \(w\) is

\[
\boxed{
\operatorname{lin}T_{\mathcal C}(w)
=
\{h:h_{S_w^c}=0,\ A_{I_{\rm face},S_w}h_{S_w}=0\}.
}
\]

### Proof

At a zero edge, tangent feasibility requires \(h_e\ge0\); lineality requires both \(h\) and \(-h\) to be tangent, hence \(h_e=0\). At an active capacity row, tangent feasibility requires \((Ah)_i\le0\); applying the same condition to \(-h\) gives \((Ah)_i=0\). Inactive inequalities impose no first-order equality. ∎

## Proposition 2.10 — clipped rows are interior in the projected output

Let \(y=\mathcal A_\varepsilon(x)\), and suppose row \(i\) is clipped while constructing \(y\). Then

\[
\boxed{
(Ay)_i
\le
s_iq_i
=
\frac{c_iq_i}{q_i+\varepsilon}
<c_i.
}
\]

Equality in the first inequality holds exactly when row \(i\) wins or ties every incident edge with positive proposal.

### Proof

For every incident edge \(e=(i,j)\),

\[
y_e=x_e\min(s_i,s_j)\le x_es_i.
\]

Sum over incident edges. Since \(\varepsilon>0\) and \(c_i>0\), the final inequality is strict. Equality in the sum holds exactly when \(\min(s_i,s_j)=s_i\) on every incident edge with \(x_e>0\). ∎

This conclusion concerns the projected output \(y\). It does not assert that the input weight state was interior before the proposal was formed.

---

## 2.3 Multiplier-controller fibers

Let

\[
S_x=\{e:x_e>0\}
\]

be the positive post-positivity proposal support. For each \(e=(i,j)\in S_x\), define a multiplier-controller set

\[
J_e=
\begin{cases}
\{i\},&s_i<s_j,\\
\{j\},&s_j<s_i,\\
\{i,j\},&s_i=s_j<1,\\
\varnothing,&s_i=s_j=1\text{ with strict unclipped margins}.
\end{cases}
\]

When the global gate is off, every edge is an implementation identity edge and one may take \(J=\varnothing\). When it is on, set

\[
J=\bigcup_{e\in S_x}J_e,
\qquad
C_J=A_{J,S_x}.
\]

In either case define the multiplier-controller fiber direction space

\[
\boxed{
L_J=
\{h:h_{S_x^c}=0,\ C_Jh_{S_x}=0\}.
}
\]

The set \(J\) concerns proposal rows that determine selected edge multipliers. It need not equal the exact active-face set \(I_{\rm face}\). In particular, a clipped endpoint that remains a strict loser on every incident positive-proposal edge does not enter \(J\).

## Proposition 2.11 — exact fiber-affine multiplier identity

Fix \(x\) and \(h\in L_J\). Suppose \(t\) is sufficiently small that positive proposal support and the global-gate state persist, every strict winner-loser inequality persists, and every identity edge remains strictly unscaled. Then

\[
M(A(x+th))=M(Ax)
\]

on \(S_x\), and

\[
\boxed{
\mathcal A_\varepsilon(x+th)
=
\mathcal A_\varepsilon(x)+tM(Ax)h.
}
\]

The identity remains valid on active endpoint ties because both tied controller row sums are fixed.

### Proof

For each controller row \(j\in J\),

\[
(A(x+th))_j=(Ax)_j+t(Ah)_j=(Ax)_j.
\]

Thus every winning or tied controller scale remains fixed. A strict losing endpoint may change clipping status, but its scale remains irrelevant while the strict winner-loser inequality persists. Strict identity edges retain multiplier one. Hence every selected edge multiplier is constant, and Proposition 2.1 gives the finite affine identity. ∎

## Corollary 2.12 — frozen-driver action on the controller fiber

Freeze the resonance driver and remain on a fixed positivity branch. For \(h\in L_J\), the Euler proposal perturbation is

\[
\delta x=(1-\gamma dt)h.
\]

Consequently

\[
\boxed{
Kh=(1-\gamma dt)M(Ax)h.
}
\]

This is an equality of maps from \(L_J\) into the ambient edge space. It becomes an endomorphism of \(L_J\) only if

\[
M(Ax)L_J\subseteq L_J.
\]

## Proposition 2.13 — invariance, intertwining, and right reduction

Let \(C\) be any matrix, \(L=\ker C\), and \(D\) a linear edge multiplier. Then

\[
DL\subseteq L
\iff
\ker C\subseteq\ker(CD)
\iff
\exists\,\Gamma\text{ such that }CD=\Gamma C.
\]

No rank assumption is required for existence of \(\Gamma\). If \(C\) has full row rank, \(\Gamma\) is unique.

If \(DL\subseteq L\) and the columns of \(V\) form a basis of \(L\), there is a unique reduced matrix \(\Lambda\) such that

\[
DV=V\Lambda.
\]

### Proof

The first equivalence is the definition of invariance of \(\ker C\). If \(DL\subseteq L\), then \(CDx\) depends only on \(Cx\): whenever \(Cx=Cy\), one has \(x-y\in\ker C\) and therefore \(CD(x-y)=0\). This defines a linear map on \(\operatorname{im}C\), which extends to a matrix \(\Gamma\) on the codomain. The converse follows immediately from \(CD=\Gamma C\). Invariance also implies that every column of \(DV\) lies in \(\operatorname{im}V\), giving a unique coordinate matrix \(\Lambda\). ∎

## Proposition 2.14 — fixed and moving dual closure

For a fixed pair of bases \(V,U\), suppose for every step \(n\)

\[
K_nV=V\Lambda_n,
\qquad
U^TK_n=\Lambda_nU^T,
\qquad
U^TV=I.
\]

Then the forced recurrence

\[
b_{n+1}=K_nb_n+f_n
\]

closes in \(a_n=U^Tb_n\):

\[
\boxed{
a_{n+1}=\Lambda_na_n+U^Tf_n.}
\]

More generally, moving bases satisfy

\[
K_nV_n=V_{n+1}\Lambda_n,
\qquad
U_{n+1}^TK_n=\Lambda_nU_n^T,
\qquad
U_n^TV_n=I,
\]

and then

\[
\boxed{
a_{n+1}=\Lambda_na_n+U_{n+1}^Tf_n,\qquad a_n=U_n^Tb_n.}
\]

Pointwise left eigenvectors alone do not imply the moving-bundle relation.

### Proof

Left-multiply the forced recurrence by \(U^T\), or by \(U_{n+1}^T\) in the moving case, and apply the stated intertwining relation. ∎

---

# 3. Augmented delayed state and exact phase/EMA identities

## 3.1 Directed phase source

The implemented directed source phase is

\[
\phi_{ij,n}
=
\theta_{i,n}
-h_{j,n}
-
\frac{\omega_i+\omega_j}{2}\tau,
\]

with source

\[
z_{ij,n}=e^{i\phi_{ij,n}}.
\]

The constant correction drops out of the temporal increment.

## Proposition 3.1 — directed phase increment

Let

\[
G_{i,n}
=
\sum_kB_{ik,n+1}
\sin(h_{k,n}-\theta_{i,n})
\]

be the implemented projected coupling. Then, modulo \(2\pi\),

\[
\boxed{
\phi_{ij,n+1}-\phi_{ij,n}
=
dt(\omega_i+G_{i,n})
-
(h_{j,n+1}-h_{j,n}).
}
\]

### Proof

Subtract the phase definitions at consecutive steps and use

\[
\theta_{i,n+1}-\theta_{i,n}
=dt(\omega_i+G_{i,n})
\quad(\bmod 2\pi).
\]

∎

---

## 3.2 Complex EMA tracking

The directed complex EMA is

\[
C_{n+1}
=
\alpha C_n+(1-\alpha)z_n,
\qquad 0<\alpha<1.
\]

Define

\[
e_n=z_n-C_n.
\]

## Proposition 3.2 — tracking-error recurrence

\[
\boxed{
e_{n+1}
=
\alpha e_n+(z_{n+1}-z_n).
}
\]

### Proof

\[
\begin{aligned}
e_{n+1}
&=z_{n+1}-C_{n+1}\\
&=z_{n+1}-\alpha C_n-(1-\alpha)z_n\\
&=\alpha(z_n-C_n)+(z_{n+1}-z_n).
\end{aligned}
\]

∎

For a difference of two directed edges, define

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

# 4. Exact nonlinear observation identities

## 4.1 Squared magnitude

Let

\[
M_n=|C_n|^2,
\qquad
Q_n=\Re(\overline{C_n}z_n).
\]

## Proposition 4.1 — squared-magnitude update

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

### Proof

Expand

\[
|\alpha C_n+(1-\alpha)z_n|^2
\]

and use \(|z_n|=1\). ∎

For directed edge difference \(a-b\),

\[
\boxed{
\Delta M_{n+1}
=
\alpha^2\Delta M_n
+
2\alpha(1-\alpha)\Delta Q_n.
}
\]

## Corollary 4.2 — effective EMA mode

If

\[
2\Delta Q_n
=
\Delta M_n+o(\Delta M_n),
\]

then

\[
\Delta M_{n+1}
=
\alpha\Delta M_n+o(\Delta M_n).
\]

---

## 4.2 Midpoint and alignment decomposition

Let

\[
\bar C=\frac{C_a+C_b}{2},
\quad
\Delta C=C_a-C_b,
\]

\[
\bar z=\frac{z_a+z_b}{2},
\quad
\Delta z=z_a-z_b.
\]

## Proposition 4.3 — midpoint identity

\[
\boxed{
\Delta M
=
2\Re(\overline{\bar C}\,\Delta C).
}
\]

### Proof

Write

\[
C_a=\bar C+\Delta C/2,
\quad
C_b=\bar C-\Delta C/2
\]

and subtract squared magnitudes. ∎

Define

\[
\Delta Q
=
\Re(\overline{C_a}z_a)
-
\Re(\overline{C_b}z_b).
\]

## Proposition 4.4 — alignment decomposition

\[
\boxed{
2\Delta Q-\Delta M=T_1+T_2,
}
\]

where

\[
T_1
=
2\Re[\overline{\bar C}(\Delta z-\Delta C)],
\]

\[
T_2
=
2\Re(\overline{\Delta C}\,\bar z).
\]

### Proof

Expanding the directed alignment difference gives

\[
\Delta Q
=
\Re(\overline{\bar C}\,\Delta z
+
\overline{\Delta C}\,\bar z).
\]

Subtract Proposition 4.3. ∎

---

## 4.3 Exact magnitude and symmetrization

## Proposition 4.5 — directed magnitude difference

If \(|C_a|+|C_b|>0\),

\[
\boxed{
|C_a|-|C_b|
=
\frac{|C_a|^2-|C_b|^2}{|C_a|+|C_b|}.
}
\]

The implemented physical resonance difference is obtained only after directed magnitudes are symmetrized.

---

# 5. Fixed-winner K3 branch

Use edge order

\[
(25,29,59)=((2,7),(2,11),(7,11)).
\]

The audited effective winners are

\[
(25,29,59)\mapsto(7,2,7).
\]

Let

\[
c_0=1-\gamma dt,
\]

and

\[
\beta_{25}=\frac{x_{25}s_7}{q_7+\varepsilon},
\quad
\beta_{29}=\frac{x_{29}s_2}{q_2+\varepsilon},
\quad
\beta_{59}=\frac{x_{59}s_7}{q_7+\varepsilon}.
\]

## Proposition 5.1 — exact selected block

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

This follows by restricting Proposition 2.4 to the three selected edges.

## Proposition 5.2 — exact exceptional controller-row carrier

On the audited winner branch, the multiplier-controller rows are

\[
J=\{2,7\}.
\]

With columns ordered \((25,29,59)\), their restricted unsigned-incidence matrix is

\[
\boxed{
C_J
=
\begin{pmatrix}
1&1&0\\
1&0&1
\end{pmatrix}.
}
\]

It has rank two and

\[
\boxed{
\ker C_J
=
\operatorname{span}\{(1,-1,-1)^T\}.
}
\]

Thus

\[
v=\frac1{\sqrt3}(1,-1,-1)^T
\]

belongs to the exceptional multiplier-controller fiber exactly.

### Proof

Node 2 controls edge 29 and is incident to edges 25 and 29, giving the first row. Node 7 controls edges 25 and 59 and is incident to those edges, giving the second row. Solving

\[
h_{25}+h_{29}=0,
\qquad
h_{25}+h_{59}=0
\]

gives \(h=a(1,-1,-1)^T\). ∎

### Remark 5.3 — node 11 and the retired classifier event

Node 11 eventually becomes scale-clipped in the saved replay but never wins a selected positive K3 edge. It therefore does not enter \(J\). Its clipping-label change leaves the selected multiplier formula unchanged as long as the strict winner inequalities persist. This is an exact branch-formula statement conditioned on the audited winner map, not a claim of infinite-time branch persistence.

---

# 6. Nested invariant families

Define

\[
v=\frac1{\sqrt3}(1,-1,-1),
\qquad
u=\frac{\sqrt3}{2}(1,0,-1),
\qquad
u^Tv=1.
\]

## Proposition 6.1 — right invariance

For the matrix in Proposition 5.1,

\[
\boxed{
Kv=\lambda v
\iff
s_2=s_7,
}
\]

with

\[
\lambda=c_0s_7.
\]

### Proof

Direct multiplication gives

\[
Kv
=
\frac{c_0}{\sqrt3}
(s_7,-s_2,-s_7)^T.
\]

∎

## Proposition 6.2 — left invariance

Assume \(s_2=s_7\). Then

\[
\boxed{
u^TK=\lambda u^T
\iff
\beta_{25}=\beta_{59}.
}
\]

### Proof

Direct multiplication gives

\[
u^TK
=
\frac{\sqrt3}{2}c_0
(s_7-\beta_{25}+\beta_{59},0,-s_7+\beta_{59}-\beta_{25}).
\]

∎

## Corollary 6.3 — realized-support symmetry

Assume the K3 is isolated in positive proposal support, capacities are equal, and nodes 2 and 7 are scale-clipped. Then

\[
s_2=s_7
\iff
x_{29}=x_{59},
\]

and

\[
\beta_{25}=\beta_{59}
\iff
x_{25}=x_{59}.
\]

Hence right and fixed-analytic-left invariance together imply

\[
x_{25}=x_{29}=x_{59},
\]

and therefore equality of all three correction coefficients.

## Proposition 6.4 — exact pointwise left covector

Assume \(s_2=s_7\), \(\beta_{59}>0\), and define

\[
r=\frac{\beta_{25}}{\beta_{59}},
\qquad
u(r)=\frac{\sqrt3}{1+r}(1,0,-r)^T.
\]

Then

\[
\boxed{
u(r)^Tv=1}
\]

and

\[
\boxed{
u(r)^TK=\lambda u(r)^T,\qquad \lambda=c_0s_7.}
\]

The fixed parameter-free covector

\[
u_*=\frac{\sqrt3}{2}(1,0,-1)^T
\]

is recovered exactly when

\[
\beta_{25}=\beta_{59}.
\]

### Proof

Let \(a=\sqrt3/(1+r)\). Direct multiplication of \((a,0,-ar)\) by the block in Proposition 5.1 shows that the two correction terms cancel because \(r\beta_{59}=\beta_{25}\). The normalization follows from

\[
(a,0,-ar)^Tv=\frac{a(1+r)}{\sqrt3}=1.
\]

The equality \(u(r)=u_*\) is equivalent to \(r=1\). ∎

### Remark 6.5 — pointwise duality versus fixed cocycle closure

A pointwise left eigenvector is not by itself a common cocycle dual. If \(r=r_n\) varies with time, the covectors \(u(r_n)\) need not satisfy the moving adjoint-bundle relation in Proposition 2.14. The replay-supported result is stronger and more specific: a single fixed covector \(u_*\) becomes highly accurate late.

## Corollary 6.6 — one-sided approach to fixed analytic pair closure

Assume the K3 is isolated in positive proposal support, capacities are equal, nodes 2 and 7 are clipped, the winner map remains \((7,2,7)\), and the three proposal coordinates are positive. Then

\[
\boxed{
\begin{aligned}
x_{29}=x_{59}
&\iff s_2=s_7
\iff \text{right closure of }v,\\
x_{25}=x_{59}
&\iff \beta_{25}=\beta_{59}
\iff \text{left closure of }u_*.
\end{aligned}
}
\]

The strict winner inequalities are equivalent to

\[
x_{59}-x_{29}>0,
\qquad
x_{25}-x_{59}>0.
\]

Consequently exact proposal equality lies on the triple-tie boundary of the strict branch. If a trajectory retains these one-sided signs while both differences tend to zero, its selected branch matrices converge to the fixed analytic family associated with \((u_*,v)\).

At exact equality all three K3 node scales tie and the full tied-controller incidence matrix has zero kernel:

\[
C_{K_3}
=
\begin{pmatrix}
1&1&0\\
1&0&1\\
0&1&1
\end{pmatrix},
\qquad
\ker C_{K_3}=\{0\}.
\]

Thus fixed-pair closure is a one-sided selected-branch matrix limit, not a nonzero two-sided fiber or unique classical Jacobian at the tied endpoint. It is also not equivalent to the mere existence of an instantaneous left eigenvector.

---

# 7. Explicit defect mode

Let

\[
\delta=\beta_{25}-\beta_{59}.
\]

Under negligible right and secondary symmetry mismatches, the remaining raw defect is

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

It satisfies

\[
E_*v=0,
\]

but

\[
u^TE_*\notin\operatorname{span}(u^T).
\]

Thus the dominant defect preserves the right line but breaks the analytic left relation.

## Proposition 7.1 — projected defect shapes

The orthogonal residual of \(E_*\) from the biorthogonal family is

\[
E_{*,LR}
=
\frac12
\begin{pmatrix}
-1&0&-1\\
0&0&0\\
1&0&1
\end{pmatrix},
\]

with

\[
\|E_{*,LR}\|_F=1.
\]

The orthogonal residual from the symmetric family is

\[
E_{*,\mathrm{sym}}
=
\frac13
\begin{pmatrix}
-2&0&-2\\
1&1&0\\
1&0&1
\end{pmatrix},
\]

with

\[
\|E_{*,\mathrm{sym}}\|_F=\frac2{\sqrt3}.
\]

These constants generate the replay-observed family-distance ratios, subject to the normalizations used by the numerical residuals.

---

# 8. Fully saturated complete components

The one-dimensional exceptional K3 reduction is a partially constrained case. Fully saturated complete components possess multidimensional signless-incidence lineality spaces on which the finite-step frozen-driver map acts as a scalar.

Let \(G=K_s\) be a complete positive-support component with \(s\ge3\) vertices, degree

\[
k=s-1,
\]

and component edge count

\[
m_G=\binom{s}{2}.
\]

Let

\[
C_G\in\{0,1\}^{s\times m_G}
\]

be its unsigned incidence matrix.

## Proposition 8.1 — complete-component lineality dimension

For \(s\ge3\),

\[
\operatorname{rank}C_G=s,
\]

and therefore

\[
\boxed{
\dim\ker C_G
=
\binom{s}{2}-s
=
\frac{s(s-3)}2.
}
\]

### Proof

Suppose \(y^TC_G=0\). For every edge \((i,j)\),

\[
y_i+y_j=0.
\]

Choose three distinct vertices \(i,j,\ell\). Then

\[
y_i=-y_j,
\qquad
y_j=-y_\ell,
\qquad
y_i=-y_\ell.
\]

The first two equalities give \(y_i=y_\ell\), while the third gives \(y_i=-y_\ell\). Hence \(y_i=y_j=y_\ell=0\). Completeness then gives \(y=0\), so the rows are independent. Apply rank-nullity. ∎

### Corollary 8.2

\[
\dim\ker C_{K_4}=2,
\qquad
\dim\ker C_{K_5}=5,
\qquad
\dim\ker C_{K_6}=9.
\]

Fully saturated \(K_2\) and \(K_3\) components have zero signless-incidence lineality and are spectrally silent in this tangent channel.

---

## 8.1 Locked regular component state

Assume:

1. all component vertices have equal capacity \(c\) and are saturated;
2. all component edges are positive;
3. the component is locked with \(R_e=1\);
4. the adaptive weight field is edge-stationary on the constrained component;
5. no additional positive proposal edges are incident to the component vertices.

Then every component edge has common weight

\[
w_e=\frac{c}{k},
\]

and the continuous ideal contraction channel is

\[
\boxed{
r_{k,\mathrm{cont}}=\frac{k\eta}{c}.
}
\]

The raw row-direction sum is

\[
k\eta-\gamma c.
\]

Thus the post-positivity proposal row sum is

\[
q^+
=
c+dt(k\eta-\gamma c).
\]

When the production global gate is on, the common node scale is

\[
\boxed{
s_k
=
\frac{c}
{c+dt(k\eta-\gamma c)+\varepsilon}.
}
\]

---

## Proposition 8.3 — exact frozen-driver scalar action on the lineality space

Let

\[
T_G=\ker C_G.
\]

For every \(h\in T_G\), the frozen-driver one-step tangent satisfies

\[
\boxed{
D\Phi_G[h]
=
\lambda_{k,\varepsilon}h,
}
\]

where

\[
\boxed{
\lambda_{k,\varepsilon}
=
(1-\gamma dt)
\frac{c}
{c+dt(k\eta-\gamma c)+\varepsilon}.
}
\]

### Proof

With the resonance driver frozen,

\[
DF[h]=-\gamma h.
\]

Therefore the Euler proposal perturbation is

\[
\delta x=(1-\gamma dt)h.
\]

Since \(h\in\ker C_G\),

\[
C_G\delta x=0.
\]

Hence every component proposal row sum and every node scale remain fixed exactly. All component endpoints have the common scale \(s_k\), so Corollary 2.2 gives

\[
D\mathcal A_\varepsilon(x)[\delta x]
=s_k\delta x.
\]

Substitute \(\delta x=(1-\gamma dt)h\). ∎

## Corollary 8.4 — self-dual invariant subspace

Let \(V\in\mathbb R^{m_G\times q_G}\) have orthonormal columns spanning \(T_G\), and set \(U=V\). Then

\[
U^TV=I,
\]

\[
D\Phi_GV=V\Lambda_G,
\]

\[
U^TD\Phi_G=\Lambda_GU^T,
\]

with

\[
\boxed{
\Lambda_G
=
\lambda_{k,\varepsilon}I_{q_G}.
}
\]

Thus the complete-component tangent action is multidimensional but isotropic and scalar. Ambient endpoint-winner ties do not affect this fiber restriction.

---

## Proposition 8.5 — finite-step contraction rate

The exact safeguarded finite-step rate is

\[
\boxed{
r_{k,\varepsilon}
=
-\frac1{dt}\log|\lambda_{k,\varepsilon}|
}
\]

or explicitly

\[
\boxed{
r_{k,\varepsilon}
=
\frac1{dt}
\left[
\log\left(
1+dt\left(\frac{k\eta}{c}-\gamma\right)
+\frac{\varepsilon}{c}
\right)
-
\log(1-\gamma dt)
\right].
}
\]

For \(\varepsilon=0\),

\[
r_{k,0}
=
\frac{k\eta}{c}
+
\frac{dt}{2}
\left[
\gamma^2
-
\left(\frac{k\eta}{c}-\gamma\right)^2
\right]
+
O(dt^2).
\]

### Proof

Insert the multiplier from Proposition 8.3 and take \(-dt^{-1}\log\). The expansion follows from the Taylor series for \(\log(1+x)\) and \(-\log(1-x)\). ∎

### Remark 8.6

If \(\varepsilon\) is fixed while \(dt\to0\), the term \(\varepsilon/(c\,dt)\) produces a singular formal contribution. The continuous-rate expansion is meaningful for \(\varepsilon=0\) or for a specified scaling such as \(\varepsilon=o(dt)\).

---

## 8.2 Frozen-cohort evidence

The existing split-state audit found:

\[
\begin{array}{c|c|c|c}
\text{component}&q_G&r_{\rm step}&k\eta/c\\ \hline
K_4&2&0.189322781&0.189473684\\
K_5&5&0.252350807&0.252631579\\
K_6&9&0.315339132&0.315789474
\end{array}
\]

Across all existing complete components, constraint, duality, right-invariance, left-invariance, and reduced-scalarity residuals were at approximately \(10^{-14}\) or smaller. Centered frozen nonlinear one-step checks agreed with the exact fiber action at approximately \(10^{-11}\) median error.

Raw endpoint-winner labels were not always preserved under tiny perturbations of tied scales, especially for \(K_6\), but the fiber formula was preserved in every tested case. This is numerical evidence for the tangent-restricted smoothness described by Corollary 8.4, not evidence of ambient classical differentiability at ties.

---

# 9. Exact scalar and Duhamel reductions

## Proposition 9.1 — biorthogonal scalar recurrence

Suppose

\[
u^TK_n=\lambda_nu^T
\]

and

\[
b_{n+1}=K_nb_n+f_n.
\]

Define

\[
a_n=u^Tb_n,
\qquad
g_n=u^Tf_n.
\]

Then

\[
\boxed{
a_{n+1}=\lambda_na_n+g_n.
}
\]

### Proof

Left-multiply the vector recurrence by \(u^T\). ∎

## Proposition 9.2 — Duhamel decomposition

Define

\[
h_{n+1}=K_nh_n,
\quad h_0=b_0,
\]

\[
r_{n+1}=K_nr_n+f_n,
\quad r_0=0.
\]

Then

\[
\boxed{
b_n=h_n+r_n.
}
\]

### Proof

Induction. ∎

---

# 10. Jordan-resonant tracking

## Proposition 10.1 — exact Jordan-resonant lemma

Let \(E_n,S_n\in\mathbb C\), \(0<|\alpha|<1\), and suppose

\[
E_{n+1}=\alpha E_n+S_n,
\qquad
S_n=B\alpha^{n+1}.
\]

Then

\[
\boxed{
E_n=(E_0+Bn)\alpha^n.
}
\]

Moreover,

\[
\begin{pmatrix}E_{n+1}\\S_{n+1}\end{pmatrix}
=
\begin{pmatrix}\alpha&1\\0&\alpha\end{pmatrix}
\begin{pmatrix}E_n\\S_n\end{pmatrix}.
\]

### Proof

Variation of constants gives

\[
E_n
=
\alpha^nE_0
+
\sum_{k=0}^{n-1}\alpha^{n-1-k}B\alpha^{k+1}
=
(E_0+Bn)\alpha^n.
\]

The matrix relation follows from \(S_{n+1}=\alpha S_n\). ∎

## Corollary 10.2 — source limit

If

\[
S_n=\Delta z_{n+1}-\Delta z_n,
\]

then

\[
\boxed{
\Delta z_\infty
=
\Delta z_n
+
\frac{B\alpha^{n+1}}{1-\alpha}.
}
\]

## Proposition 10.3 — perturbed resonant recurrence

Suppose

\[
S_n=B\alpha^{n+1}+r_n.
\]

Then

\[
\boxed{
E_n
=
(E_0+Bn)\alpha^n
+
\sum_{k=0}^{n-1}\alpha^{n-1-k}r_k.
}
\]

Let

\[
\rho_k=\frac{r_k}{\alpha^{k+1}}.
\]

Then

\[
\frac{E_n}{\alpha^n}
=
E_0+Bn+
\sum_{k=0}^{n-1}\rho_k.
\]

### Asymptotic hierarchy

1. If \(\sum\rho_k\) converges, then
   \[
   E_n=(A+Bn)\alpha^n+o(\alpha^n).
   \]

2. If \(\rho_n\to0\), then
   \[
   E_n=(E_0+Bn+o(n))\alpha^n.
   \]
   The source-limit estimator has error \(o(|\alpha|^n)\).

3. If \(\rho_n=O(1)\), then
   \[
   E_n=(E_0+Bn+O(n))\alpha^n,
   \]
   while the source-limit estimator remains consistent with error \(O(|\alpha|^n)\).

---

# 11. Conditional triangular memory law

Assume

\[
a_{n+1}=\lambda_Ba_n+g_n,
\]

\[
g_{n+1}=\alpha g_n,
\]

with constant late multipliers satisfying \(|\lambda_B|,|\alpha|<1\).

## Proposition 11.1 — relative-retention memory rate

A forcing contribution of age \(k\) has relative multiplier

\[
\left(\frac{\lambda_B}{\alpha}\right)^k.
\]

Therefore

\[
\boxed{
\kappa
=
-\frac1{dt}
\log\left|\frac{\lambda_B}{\alpha}\right|.
}
\]

This is a theorem about the triangular reduction, not a universal AIEF identity.

---

# 12. Numerical evidence from the frozen exceptional replay

This section records numerical evidence rather than theorems.

## 12.1 Fixed branch and exact controller carrier

- Positive K3 support remains fixed.
- Effective winner map remains \((7,2,7)\).
- No effective positive-edge branch change occurs over 32,001 recorded states.
- Conditional on that saved winner fact, the controller matrix is exactly
  \[
  C_{\{2,7\}}=\begin{pmatrix}1&1&0\\1&0&1\end{pmatrix},
  \]
  and its kernel is exactly \(\operatorname{span}\{(1,-1,-1)\}\).
- Node 11 changes clipping label but never becomes a selected edge controller.

## 12.2 Frozen and augmented tangents

- Frozen K3 cocycle reproduces frozen nonlinear perturbations on preserved branches.
- Full augmented directional tangent reproduces coupled perturbations with median K3 error around \(5\times10^{-4}\) over resolved horizons.

## 12.3 Biorthogonal reduction

- Numerical right modes approach \(v=(1,-1,-1)/\sqrt3\).
- Numerical left modes approach \(u_*=\sqrt3(1,0,-1)/2\).
- Fixed left covectors reduce direction-0 final rollout error from about \(0.74\) to about \(1.9\times10^{-5}\) for a rollout starting at \(t=250\).
- At \(t=319.99\), the saved analytic right residual is approximately \(2.57\times10^{-14}\), while the fixed-left residual is approximately \(8.55\times10^{-9}\).
- These are finite-horizon residuals of the selected frozen-driver K3 block, not an infinite-time convergence theorem.

## 12.4 Defect family and recurrence

- Distance to the right-invariant family is already order \(10^{-9}\) at \(t=100\).
- At \(t=319.99\), distance to the fixed biorthogonal family is approximately \(6.98\times10^{-9}\).
- Biorthogonal and symmetric family defects decay monotonically toward order \(10^{-9}\) over the saved horizon.
- Numerical defect POD and analytic projected defect cosine is \(1-O(10^{-12})\).
- Dominant defect multiplier approaches \(\alpha\) pointwise over the saved late window, with median discrepancy order \(10^{-9}\).

## 12.5 Resonant tracking and angular freezing

- \(E_n/\alpha^n\) is complex affine in \(n\) late.
- \(S_n/\alpha^{n+1}\) independently converges to the affine slope.
- Source-limit estimates collapse to relative spreads near \(10^{-13}\).
- Alignment terms satisfy \(T_1/T_2\to-1\).
- Source mean and separation increments acquire the EMA rate.
- Source and memory phase separations freeze while radius differences decay at the EMA rate.

---

# 13. Structural and replay-specific dynamical chains

The exact structural chain is

\[
\boxed{
\text{multiplier-controller fiber}
\longrightarrow
\text{fiber-affine multiplier action}
\longrightarrow
\begin{cases}
\text{right defect }s_2-s_7,\\
\text{fixed-left defect }\beta_{25}-\beta_{59}.
\end{cases}
}
\]

Under the isolated equal-capacity fixed-branch hypotheses,

\[
s_2-s_7
=
c\frac{x_{59}-x_{29}}
{(q_2+\varepsilon)(q_7+\varepsilon)},
\]

and

\[
\beta_{25}-\beta_{59}
=
\frac{s_7}{q_7+\varepsilon}(x_{25}-x_{59}).
\]

Thus the two proposal differences have distinct operator meanings.

The saved numerical evidence supports, but does not prove beyond the finite horizon, the dynamical chain

\[
\boxed{
\begin{aligned}
&\text{delayed phase-balance and EMA feedback}\\
&\Downarrow\\
&\text{proposal-difference decay}\\
&\Downarrow\\
&\text{right- and fixed-left-defect decay}\\
&\Downarrow\\
&\text{approach to fixed analytic pair closure}.
\end{aligned}
}
\]

The detailed replay-specific route includes resonant tracking, persistent tangential complex separation, radial-observable decay, and exact downstream \(\Delta R\to\Delta B\to\Delta x\to K\) identities. Its infinite-time continuation and branch persistence are open.

---

# 14. Limitations and non-results

The analysis does not establish:

- a universal defect matrix across winner branches;
- a universal rank-one reduction across components;
- a full-system Jordan block;
- an invariant manifold or toroidal attractor;
- a loop gain equal to \(\lambda_B/\alpha\);
- a global ideal-map directional theorem for the safeguarded implementation;
- infinite-time persistence of the exceptional support, clipping, and winner branch;
- asymptotic convergence of \(x_{59}-x_{29}\) and \(x_{25}-x_{59}\) to zero;
- timestep or safeguard convergence;
- parameter sensitivity under consistently regenerated states;
- generality beyond the frozen seed and tested directions.

---

# 15. Proof and generalization frontier

## 15.1 Proof-ready results

The following are ready for formal proof from the implemented formulas:

- factorization;
- full row-sum fiber linearity;
- polyhedral tangent-cone lineality;
- safeguarded projected-output interiority;
- multiplier-controller fiber affinity, including active endpoint ties;
- invariance/intertwining factorization;
- fixed and moving dual-closure lemmas;
- strict-branch Jacobian;
- branch persistence;
- exact exceptional controller-row kernel;
- exact pointwise K3 left covector and fixed-pair closure conditions;
- directed phase increment;
- tracking-error recurrence;
- squared-magnitude identity;
- alignment decomposition;
- fixed-winner sparse block;
- nested invariant families;
- analytic left/right pair;
- explicit defect matrices;
- complete-component lineality dimension, scalar fiber action, and finite-step rate;
- biorthogonal scalar recurrence;
- Duhamel decomposition;
- exact Jordan-resonant lemma;
- triangular memory lemma.

## 15.2 Conditional asymptotic results

The following require explicit convergence assumptions:

- convergence to the biorthogonal/symmetric family;
- EMA-rate pointwise defect recurrence beyond the finite replay;
- resonant source asymptotics;
- radial quotient alpha mode;
- convergence of mean and separation phases;
- persistence of the reduced mechanism on neighboring trajectories.

## 15.3 Next theoretical target

There are two nested targets.

**Conditional branch theorem.** Assume that after some step the exceptional K3 remains isolated in positive proposal support, rows 2 and 7 remain clipped, and the winner map remains \((7,2,7)\). Derive from the coupled delayed phase/EMA dynamics that

\[
x_{59,n}-x_{29,n}\to0,
\qquad
x_{25,n}-x_{59,n}\to0.
\]

**Strong trajectory theorem.** Starting from the frozen exceptional split state, prove both persistence of those branch hypotheses and the two limits. Existing artifacts establish neither assertion beyond the finite replay.

The upstream analytic obstacle is to derive the observed EMA-rate phase-balance and radial envelopes from the jointly linearized phase, history, EMA, and weight dynamics rather than assuming them.

---

# 16. Reproducibility anchors

Principal sources:

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

Administrative context:

```text
AIEF_HISTORIC_UNFOLDING.md
AIEF_1_4_OPERATOR_COCYCLE_THOUGHT_TREE.md
AIEF_1_4_FORWARD_PLAN.md
AI_AGENT_HANDOFF_PROMPT.md
```
