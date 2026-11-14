# AIEF-1.4 multiplier-controller fiber theorem package

**Status:** frozen proof-oriented supplement  
**Date:** 2026-07-27  
**Production evidence authority:** frozen AIEF-1.4 run `5a9f093a2fe0` and its historical manifests  
**Exceptional replay:** seed `4619122171158768524`  

## 1. Scope and epistemic separation

This supplement formalizes the common geometry behind the audited complete-component fibers and the exceptional K3 selected block. It separates:

1. exact polyhedral geometry;
2. exact finite-step implementation identities;
3. facts supplied by the frozen replay audits;
4. conditional fixed-branch operator conclusions;
5. finite-horizon numerical evidence;
6. open infinite-time dynamical claims.

No new trajectory, seed cohort, or parameter variant is generated here. The exceptional seed is one seed/graph realization. Saved times, perturbation directions, and component edges are not independent experimental replicates.

---

# Part I. Polyhedral and implementation geometry

## 2. Capacity polytope

Let

\[
\mathcal C=\{w\in\mathbb R^m:w\ge0,\ Aw\le c\},
\]

where \(A\) is the unsigned node-edge incidence matrix and \(c_i>0\). For \(w\in\mathcal C\), define

\[
S_w=\{e:w_e>0\},
\qquad
I_{\rm face}=\{i:(Aw)_i=c_i\}.
\]

### Proposition 2.1 — polyhedral tangent-cone lineality

\[
\boxed{
\operatorname{lin}T_{\mathcal C}(w)
=
\{h:h_{S_w^c}=0,\ A_{I_{\rm face},S_w}h_{S_w}=0\}.
}
\]

### Proof

At a zero edge, tangent feasibility gives \(h_e\ge0\). Requiring both \(h\) and \(-h\) to be tangent gives \(h_e=0\). At an active capacity row, tangent feasibility gives \((Ah)_i\le0\); applying it to \(-h\) gives \((Ah)_i=0\). Inactive inequalities impose no lineality equality. ∎

This is exact feasible-set geometry. It is independent of the implemented safeguard.

---

## 3. Safeguarded output interiority

Let \(x\ge0\) be the post-positivity proposal and \(q=Ax\). If the production global gate is on, define

\[
s_i=\min\left(1,\frac{c_i}{q_i+\varepsilon}\right),
\qquad
m_{ij}=\min(s_i,s_j).
\]

If the global gate is off, the effective edge multipliers are instead \(m_{ij}=1\), exactly as in the implementation. Let

\[
y=\mathcal A_\varepsilon(x),
\qquad
y_{ij}=x_{ij}m_{ij}.
\]

### Proposition 3.1 — clipped rows are interior in the projected output

If row \(i\) is clipped while constructing \(y\), then

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

For each incident edge \((i,j)\),

\[
x_{ij}\min(s_i,s_j)\le x_{ij}s_i.
\]

Sum over incident edges. The final inequality is strict because \(c_i>0\) and \(\varepsilon>0\). ∎

The conclusion concerns the projected output \(y\). It does not determine whether the input weight state lay on a capacity face.

---

## 4. Multiplier-controller fibers

Let

\[
S_x=\{e:x_e>0\}
\]

be the positive proposal support. For each \(e=(i,j)\in S_x\), define

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
C_J=A_{J,S_x},
\]

and

\[
\boxed{
L_J=\{h:h_{S_x^c}=0,\ C_Jh_{S_x}=0\}.
}
\]

The set \(J\) contains multiplier-determining proposal rows. It need not equal the exact active-face set. A clipped endpoint that remains a strict loser on every selected edge need not enter \(J\).

### Proposition 4.1 — exact fiber-affine identity

Fix \(x\) and \(h\in L_J\). Suppose \(t\) is sufficiently small that:

1. positive proposal support persists;
2. the global-gate state persists;
3. every strict winner-loser inequality persists;
4. every identity edge remains strictly unscaled.

Then

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

The result includes active endpoint ties.

### Proof

For every controller row \(j\in J\), \((Ah)_j=0\), so its proposal row sum and scale are unchanged. At a strict winner edge, the losing scale may vary or cross its own clipping threshold, but it remains irrelevant while the winner inequality persists. At a tie, both endpoint scales remain fixed. A strict identity edge retains multiplier one. Therefore every edge multiplier is constant, and the exact factorization \(\mathcal A_\varepsilon(x)=M(Ax)x\) gives the result. ∎

### Corollary 4.2 — frozen-driver fiber action

Freeze the resonance driver and remain on a fixed positivity branch. For \(h\in L_J\),

\[
\boxed{
Kh=(1-\gamma dt)M(Ax)h.
}
\]

This maps \(L_J\) into the ambient edge space. It is an endomorphism of \(L_J\) only under the additional preservation condition

\[
M(Ax)L_J\subseteq L_J.
\]

---

## 5. Invariance and reduced coordinates

### Proposition 5.1 — kernel preservation and intertwining

Let \(C\) be any matrix, \(L=\ker C\), and \(D\) a linear multiplier. Then

\[
\boxed{
DL\subseteq L
\iff
\ker C\subseteq\ker(CD)
\iff
\exists\,\Gamma:\ CD=\Gamma C.
}
\]

No rank hypothesis is needed for existence. If \(C\) has full row rank, \(\Gamma\) is unique.

### Proof

The first equivalence is immediate. Under kernel preservation, \(CDx\) depends only on \(Cx\), defining a linear map on \(\operatorname{im}C\); extend it to the codomain to obtain \(\Gamma\). The converse follows from \(CD=\Gamma C\). Full row rank makes \(C\) surjective and the factor unique. ∎

### Corollary 5.2 — right reduction

If \(DL\subseteq L\) and the columns of \(V\) form a basis of \(L\), then there is a unique \(\Lambda\) such that

\[
DV=V\Lambda.
\]

Right invariance alone does not produce a dynamically closed left basis.

### Proposition 5.3 — fixed common dual

Suppose, for every step \(n\),

\[
K_nV=V\Lambda_n,
\qquad
U^TK_n=\Lambda_nU^T,
\qquad
U^TV=I.
\]

If

\[
b_{n+1}=K_nb_n+f_n,
\qquad a_n=U^Tb_n,
\]

then

\[
\boxed{
a_{n+1}=\Lambda_na_n+U^Tf_n.}
\]

### Proposition 5.4 — moving dual bundle

If instead

\[
K_nV_n=V_{n+1}\Lambda_n,
\qquad
U_{n+1}^TK_n=\Lambda_nU_n^T,
\qquad
U_n^TV_n=I,
\]

then, for \(a_n=U_n^Tb_n\),

\[
\boxed{
a_{n+1}=\Lambda_na_n+U_{n+1}^Tf_n.}
\]

Pointwise left eigenvectors alone do not imply this moving-bundle relation.

---

# Part II. Ordinary tied cliques and the exceptional strict K3

## 6. Tied rate-uniform complete components

On an audited complete component, let \(C_G\) be its unsigned incidence matrix and

\[
L_G=\ker C_G.
\]

All component proposal row sums and node scales are equal. Active endpoint labels can tie and change under bookkeeping conventions, but if \(h\in L_G\), every component row sum is fixed. Proposition 4.1 therefore applies at the tie and gives

\[
Kh=(1-\gamma dt)s_kh.
\]

Thus \(L_G\) is exactly invariant and the restriction is scalar. For \(G=K_s\), \(s\ge3\),

\[
\dim L_G=\binom{s}{2}-s=\frac{s(s-3)}2.
\]

This recovers dimensions \(2,5,9\) for \(K_4,K_5,K_6\). Winner-label stability is not required for this fiber restriction.

---

## 7. Exceptional K3 controller carrier

Use edge order

\[
(25,29,59)=((2,7),(2,11),(7,11)).
\]

### Saved replay fact 7.1

The frozen branch audit reports the effective winners

\[
(25,29,59)\mapsto(7,2,7)
\]

throughout 32,001 saved states, with no effective positive-edge winner change. This is a saved finite-replay fact, not an infinite-time theorem.

### Proposition 7.2 — exact controller kernel conditional on the audited winner map

The selected multiplier-controller rows are

\[
J=\{2,7\},
\]

and

\[
\boxed{
C_J=
\begin{pmatrix}
1&1&0\\
1&0&1
\end{pmatrix}.
}
\]

Hence

\[
\boxed{
\ker C_J
=
\operatorname{span}\{(1,-1,-1)^T\}.
}
\]

The analytic right carrier

\[
v=\frac1{\sqrt3}(1,-1,-1)^T
\]

belongs to the multiplier-controller fiber exactly.

### Proof

Node 2 is incident to edges 25 and 29, and node 7 is incident to edges 25 and 59, giving the two displayed rows. Solving

\[
h_{25}+h_{29}=0,
\qquad
h_{25}+h_{59}=0
\]

gives \(h=a(1,-1,-1)^T\). ∎

Node 11 eventually changes clipping label in the saved replay but never becomes a selected controller. Its label change does not alter the selected multiplier formula while the strict winner inequalities persist.

---

## 8. Exact selected block and right closure

Let

\[
c_0=1-\gamma dt,
\]

and

\[
\beta_{25}=\frac{x_{25}s_7}{q_7+\varepsilon},
\qquad
\beta_{29}=\frac{x_{29}s_2}{q_2+\varepsilon},
\qquad
\beta_{59}=\frac{x_{59}s_7}{q_7+\varepsilon}.
\]

The selected frozen-driver block is

\[
K=c_0
\begin{pmatrix}
s_7-\beta_{25}&0&-\beta_{25}\\
-\beta_{29}&s_2-\beta_{29}&0\\
-\beta_{59}&0&s_7-\beta_{59}
\end{pmatrix}.
\]

### Proposition 8.1 — right closure

\[
\boxed{
Kv=\lambda v
\iff
s_2=s_7,
\qquad
\lambda=c_0s_7.
}
\]

### Proof

Direct multiplication gives

\[
Kv
=
\frac{c_0}{\sqrt3}(s_7,-s_2,-s_7)^T.
\]

This is proportional to \(v\) exactly when \(s_2=s_7\), in which case the multiplier is \(c_0s_7\). ∎

Thus the carrier is exact, while its invariance is conditional on controller-scale equality.

---

## 9. Pointwise and fixed left covectors

Assume \(s_2=s_7\), \(\beta_{59}>0\), and define

\[
r=\frac{\beta_{25}}{\beta_{59}},
\qquad
u(r)=\frac{\sqrt3}{1+r}(1,0,-r)^T.
\]

### Proposition 9.1 — exact pointwise left covector

\[
\boxed{
u(r)^Tv=1}
\]

and

\[
\boxed{
u(r)^TK=\lambda u(r)^T.}
\]

The fixed parameter-free covector

\[
u_*=rac{\sqrt3}{2}(1,0,-1)^T
\]

is recovered exactly when

\[
\beta_{25}=\beta_{59}.
\]

### Proof

Write \(u(r)=a(1,0,-r)^T\), where \(a=\sqrt3/(1+r)\). The normalization is

\[
u(r)^Tv=\frac{a(1+r)}{\sqrt3}=1.
\]

In the left product with the selected block, the correction terms cancel because \(r\beta_{59}=\beta_{25}\). The remaining terms give \(u(r)^TK=c_0s_7u(r)^T\). Finally, \(u(r)=u_*\) exactly when \(r=1\). ∎

A pointwise \(u(r_n)\) is not automatically a fixed common cocycle dual or a moving adjoint bundle.

---

## 10. Proposal equalization and fixed-pair closure

Assume:

1. equal capacities;
2. isolated positive proposal support of the K3;
3. rows 2 and 7 are clipped;
4. the winner map is \((7,2,7)\);
5. the three proposal coordinates are positive.

Then

\[
q_2=x_{25}+x_{29},
\qquad
q_7=x_{25}+x_{59}.
\]

### Proposition 10.1 — exact defect identities

\[
\boxed{
s_2-s_7
=c\frac{x_{59}-x_{29}}
{(q_2+\varepsilon)(q_7+\varepsilon)}.}
\]

Also,

\[
\boxed{
\beta_{25}-\beta_{59}
=
\frac{s_7}{q_7+\varepsilon}(x_{25}-x_{59}).}
\]

### Proof

Isolation gives

\[
q_2=x_{25}+x_{29},
\qquad
q_7=x_{25}+x_{59}.
\]

Since both controller rows are clipped and capacities are equal,

\[
s_2-s_7
=c\left(\frac1{q_2+\varepsilon}-\frac1{q_7+\varepsilon}\right),
\]

which is the first identity. The two correction coefficients \(\beta_{25}\) and \(\beta_{59}\) share the factor \(s_7/(q_7+\varepsilon)\), giving the second. ∎

Consequently, for the algebraic continuation of the selected branch matrix,

\[
\boxed{
\begin{aligned}
x_{29}=x_{59}
&\iff \text{right closure of }v,\\
x_{25}=x_{59}
&\iff \text{left closure of the fixed }u_*.
\end{aligned}}
\]

The strict winner inequalities themselves are equivalent to

\[
x_{59}-x_{29}>0,
\qquad
x_{25}-x_{59}>0.
\]

Therefore exact proposal equality is the boundary of the strict branch, not a point in its interior. A sequence that retains the strict winner signs while both differences tend to zero has selected one-sided branch matrices converging to the fixed analytic family associated with \((u_*,v)\).

At exact equality all three node scales tie. The full tied-controller incidence matrix is

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

Thus the limiting statement is not the existence of a nonzero two-sided controller fiber or a unique classical Jacobian at the triple tie. It is convergence of one-sided selected branch matrices. This is also distinct from the mere existence of an instantaneous left covector.

---

# Part III. Evidence status and open theorem

## 11. Strongest established statement

The exact and replay-established conclusions are:

1. the saved winner map is fixed over the finite record;
2. conditional on that map, \(v\in\ker C_{\{2,7\}}\) exactly;
3. the fiber-affine implementation identity is exact locally;
4. right closure is exactly equivalent to \(s_2=s_7\);
5. closure of the fixed analytic left covector is exactly equivalent to \(\beta_{25}=\beta_{59}\);
6. on the saved finite horizon, the selected frozen-driver block moves increasingly close to the fixed analytic family.

At \(t=319.99\), the recorded residuals are approximately:

\[
\text{right residual}=2.57\times10^{-14},
\]

\[
\text{fixed-left residual}=8.55\times10^{-9},
\]

\[
\text{distance to fixed biorthogonal family}=6.98\times10^{-9}.
\]

These are finite-horizon replay facts, not asymptotic limits.

---

## 12. Structural and dynamical chains

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

The replay-specific dynamical interpretation is

\[
\boxed{
\text{phase/EMA feedback}
\longrightarrow
\text{proposal-difference decay}
\longrightarrow
\text{operator-defect decay}
\longrightarrow
\text{approach to fixed analytic pair closure}.}
\]

Only the first chain is theorem-level. The second is finite-horizon mechanism evidence.

---

## 13. Remaining theorem

### Conditional branch theorem

Assume that after some step:

1. the K3 remains isolated in positive proposal support;
2. rows 2 and 7 remain clipped;
3. the winner map remains \((7,2,7)\);
4. required positivity and strict branch margins persist.

Derive from the coupled delayed phase/EMA evolution that

\[
x_{59,n}-x_{29,n}\to0,
\qquad
x_{25,n}-x_{59,n}\to0.
\]

This would imply asymptotic fixed-pair closure on the persistent branch.

### Strong trajectory theorem

Starting from the frozen exceptional split state, prove jointly:

1. persistence of the support, clipping, and winner hypotheses;
2. convergence of both proposal differences.

The saved replay proves neither assertion beyond its finite horizon. The upstream obstacle is to derive the observed EMA-rate phase-balance and radial envelopes from the coupled phase, delayed-history, EMA, and weight dynamics.

---

## 14. Reproducibility and nonclaims

Principal implementation/evidence sources are:

```text
AIEF_1_4_actual_admissibility_branch_audit.py
AIEF_1_4_frozen_driver_cocycle_analysis.py
AIEF_1_4_nested_operator_family_audit.py
AIEF_1_4_biorthogonal_triangular_closure.py
AIEF_1_4_existing_clique_invariant_subspaces.py
AIEF_1_4_defect_recurrence_analytic_mode.py
AIEF_1_4_defect_causal_ema_trace.py
AIEF_1_4_radial_observable_subsystem_analysis.py
AIEF_1_4_resonant_tracking_angular_analysis.py
AIEF_1_4_phase_balance_source_dynamics.py
```

Historical execution hashes remain authoritative in the corresponding saved `analysis_manifest.json` files. Current workspace source hashes do not replace those historical hashes.

This package does not establish:

- infinite-time branch persistence;
- asymptotic proposal equalization;
- generality across other seeds or winner maps;
- full augmented-state invariant-manifold geometry;
- a global directional-differentiability theorem at all safeguarded strata.
