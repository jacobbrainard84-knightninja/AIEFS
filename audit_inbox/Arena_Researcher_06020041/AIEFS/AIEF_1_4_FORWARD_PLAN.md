# AIEF-1.4 forward plan — formalization and scoped generalization

## Updated program status

The exceptional-seed mechanism has now been traced from delayed phase balance through complex EMA tracking, magnitude observation, resonance, weights, and the finite-step operator defect. The immediate task is no longer to add another local diagnostic. It is to formalize the operator/observable theory, freeze the evidence lineage, and test the resulting invariant-subspace framework on existing component classes.

Do not start another broad seed cohort or a naive future-only parameter sweep.

Always separate:

1. exact implementation identities;
2. replay-established numerical laws;
3. replay-specific asymptotic mechanisms;
4. conditional lemmas with explicit assumptions;
5. general claims requiring other seeds, branches, or regenerated states.

---

# I. Completed mechanism chain

## 1. Fixed finite-step branch

For exceptional seed

```text
4619122171158768524
```

and K3 edges

```text
25=(2,7)
29=(2,11)
59=(7,11)
```

the positive support and effective winner map remain fixed:

```text
25 -> node 7
29 -> node 2
59 -> node 7
```

The former `t=124.05` event was a slack-classifier transition, not an implemented winner-branch switch.

## 2. Weight and augmented cocycles

Completed:

- exact post-positivity factorization;
- exact row-sum fiber linearity;
- branchwise finite-step Jacobian;
- frozen-driver K3 cocycle;
- non-normal transient and diagonal-only control;
- augmented directional tangent on `(theta,B,C,history)`;
- centered nonlinear validation with branch preservation.

## 3. Duhamel and reduced dynamics

Completed:

- exact direction-wise Duhamel reconstruction;
- direct differentiated `R -> B` forcing match;
- crossover times `0.38` and `72.86`;
- late recent-forcing memory law;
- propagated-forcing rank analysis;
- parameter-free triangular closure;
- biorthogonal correction of the Euclidean scalar coordinate.

The analytic K3 pair is

\[
v=\frac1{\sqrt3}(1,-1,-1),
\qquad
u=\frac{\sqrt3}{2}(1,0,-1),
\qquad
u^Tv=1.
\]

## 4. Nested operator families and dominant defect

Completed:

- exact fixed-winner sparse family;
- right-invariant family;
- biorthogonal family;
- symmetric subfamily;
- numerical projection distances and decay fits;
- analytic raw defect
  \[
  E_*=\begin{pmatrix}-1&0&-1\\0&0&0\\0&0&0\end{pmatrix};
  \]
- analytic projected defect matrices;
- POD/analytic cosine `1-O(1e-12)`;
- pointwise EMA recurrence of the dominant coefficient and matrix defects.

## 5. Observable-level and phase-source mechanism

Completed:

- exact directed complex EMA recurrence;
- exact squared-magnitude recurrence;
- exact alignment-residual decomposition;
- directed radial/tangential diagnostics;
- forward/reverse reinforcement under symmetrization;
- source-memory tracking analysis;
- resonant `E_n=(A+Bn)alpha^n` test;
- source-limit estimator;
- angular/radius freezing;
- delayed phase-balance decomposition into intrinsic, coupling, and history terms.

The replay-specific chain is now:

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

This is finite-horizon evidence on one branch, not a universal AIEF theorem.

---

# II. Interpretations explicitly retired

Do not reuse these claims without qualification:

1. `B` is the unique or dominant memory carrier.
2. Admissibility is an occasional repair.
3. The full mature delayed system is at equilibrium.
4. The exceptional trajectory undergoes an implemented branch switch at `t=124.05`.
5. The finite-step exceptional K3 has an operational bare-`gamma` edge mode.
6. A Euclidean scalar coordinate should predict both K3 directions.
7. The POD Rayleigh quotient is the relevant memory propagation rate.
8. A shared `(a,g)` two-state model has been identified.
9. The full complex EMA difference decays homogeneously at the EMA rate.
10. Forward/reverse symmetrization creates the resonance mode.
11. The alignment law is cancellation free.
12. `lambda_B/alpha_EMA` is an established loop gain.
13. Weight-tangent rank one implies a one-dimensional full attractor or torus.

---

# III. Immediate priority — formal theorem manuscript

## Action 1: convert the closure note into proof-ready sections

Use:

```text
AIEF_1_4_OPERATOR_COCYCLE_CLOSURE_THEOREM_NOTE.md
```

as the working source.

### Section A — admissibility map

Formalize:

1. safeguarded and ideal map definitions;
2. factorization
   \[
   \mathcal A_\varepsilon(x)=M(Ax)x;
   \]
3. exact fiber linearity;
4. polyhedral proposal strata;
5. strict-branch Jacobian;
6. directional endpoint-tie formula;
7. branch-persistence radius;
8. safeguarded global-gate discontinuity.

### Section B — fixed K3 branch

Formalize:

1. exact selected sparse matrix;
2. right-invariance equivalence;
3. biorthogonal-family equivalence;
4. realized-support symmetry conditions;
5. analytic left/right pair;
6. scalar projection theorem;
7. explicit raw and projected defect matrices;
8. perturbation bounds linking family distance and left residual.

### Section C — delayed phase and EMA

Formalize exact identities:

1. directed source-phase increment;
2. EMA tracking-error recurrence;
3. squared-magnitude recurrence;
4. midpoint/alignment decomposition;
5. exact magnitude reconstruction;
6. exact downstream proposal/weight/operator transfer.

### Section D — conditional asymptotic lemmas

Include explicit assumptions for:

1. pointwise defect recurrence;
2. Jordan-resonant tracking lemma and remainder hierarchy;
3. source-limit estimator;
4. radial-observable alpha mode;
5. triangular memory-gap law;
6. convergence of numerical left modes.

Do not present replay convergence as an unconditional theorem.

**Deliverable:** a proof-oriented manuscript note with proposition numbering, assumptions, and proof status.

---

# IV. Priority 2 — freeze the analysis lineage

Create:

```text
AIEF_1_4_analysis_lineage.csv
AIEF_1_4_operator_cocycle_closure_note.md
```

Each analysis row should contain:

```text
analysis name
source hash
input hashes
output directory
estimand
scope
tolerances/epsilon
principal result
superseded claim
evidence class
```

Evidence classes:

```text
exact code identity
replay fact
controlled counterfactual
conditional mechanism
open generalization
```

Update:

```text
AIEF_HISTORIC_UNFOLDING.md
AIEF_1_4_OPERATOR_COCYCLE_THOUGHT_TREE.md
AI_AGENT_HANDOFF_PROMPT.md
```

with the final radial/source/phase-balance results.

---

# V. Priority 3 — existing-component invariant-subspace controls

Before generating new simulations, use existing ordinary split states.

For `K4`, `K5`, and `K6` components:

1. construct the geometric face-lineality basis `V`;
2. construct a dual basis `U` satisfying
   \[
   U^TV=I;
   \]
3. test
   \[
   KV\approx V\Lambda;
   \]
4. test
   \[
   U^TK\approx\Lambda U^T;
   \]
5. compare Euclidean and biorthogonal conditioning;
6. verify scalar-on-subspace action for rate-uniform components;
7. report component-wise residuals and multiplicities.

Do not expect universal rank one. The correct generalization is an invariant biorthogonal subspace whose dimension equals the signless-incidence lineality dimension.

**Decision gate:** only proceed to new seed cohorts if the mechanism fails to be distinguished using existing component classes.

---

# VI. Priority 4 — matched-phase memory-ablation correction

Complete the outstanding paired correction:

```text
B_carrier_only
full_reset
```

using identical randomized phase/history resets.

This is a closure task for the memory-ablation narrative and should remain separate from the operator theorem program.

---

# VII. Priority 5 — consistently regenerated sensitivity studies

Only after formalization and existing-component checks.

## 1. EMA sensitivity

For a small grid such as

```text
T_window multiplier: 0.75, 1.0, 1.25, 1.5
```

regenerate the entire exceptional trajectory state, including:

- phase prefix;
- delay history;
- complex EMA;
- weights;
- split state.

Do not reuse the original split state under a changed EMA parameter.

First gate on:

```text
support topology
winner branch
component class
augmented tangent validation
```

Treat branch changes as different regimes.

Within a common regime test:

\[
r_{\rm source}\stackrel{?}{=}1/T_{\rm window},
\]

\[
\kappa\stackrel{?}{=}r_{\rm prop}-r_{\rm source}.
\]

## 2. Timestep/safeguard study

Regenerate complete trajectories while varying:

\[
dt,
\qquad
\varepsilon,
\qquad
\varepsilon/dt,
\qquad
\text{slack}/dt.
\]

Separate:

- fixed epsilon;
- epsilon proportional to `dt`;
- ideal epsilon zero where safe.

Primary outputs:

- branch/winner structure;
- safeguard-normal exponent;
- geometric/dual mode residuals;
- augmented slow rate;
- radial observable rate;
- defect multiplier;
- memory gap.

---

# VIII. Priority 6 — broader generality only after existing evidence is exhausted

If needed:

1. select a few existing representative component classes;
2. run validated augmented tangent and invariant-subspace diagnostics;
3. treat each seed as the inferential unit;
4. do not count edges, directions, or amplitudes as independent samples;
5. add a new cohort only for a specific unresolved inferential question.

---

# IX. Full-state geometry remains downstream

Do not infer a torus, slow manifold, or attractor dimension from weight-tangent POD.

A future geometry study must first:

- quotient global phase symmetry;
- encode phases circularly;
- preserve delay-history consistency;
- scale augmented variables explicitly;
- distinguish stable fibers from attractor tangent directions;
- use nearby trajectories for local dimension/curvature;
- only then apply recurrence, frequency-rank, Poincare, or persistent-homology tools.

The defensible downstream hypothesis is a normally attracting, possibly stratified invariant graph over continuing phase/history dynamics—not a literal pointed torus.

---

# X. Immediate execution order

1. Convert the closure theorem note into a proof-oriented manuscript section.
2. Freeze the analysis lineage and update administrative sources of truth.
3. Test biorthogonal invariant subspaces on existing `K4`, `K5`, and `K6` components.
4. Complete the matched-phase memory-ablation correction.
5. Design separately versioned regenerated EMA and timestep/safeguard studies.
6. Defer broad cohorts and full-state topology until these gates are passed.
